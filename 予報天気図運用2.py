import pygrib
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from scipy.ndimage import gaussian_filter
import os
from datetime import datetime, timedelta
import pytz  

# === 設定 ===
# GRIBファイルの保存ディレクトリ
base_dir = r'D:\GSMdownload'

# 画像保存先フォルダ
output_dir = r'D:\GSMdownload\weathermap'

# ダウンロードしたGRIBファイルのバリアント
variants = ["0012", "0112", "0212", "0312", "0412"]

# JSTのタイムゾーンを取得
jst = pytz.timezone('Asia/Tokyo')

# 現在のJSTの前日を取得
yesterday_jst = datetime.now(jst) - timedelta(days=1)
formatted_date = yesterday_jst.strftime('%Y%m%d')

# カラーバーの絶対的な範囲設定
vmin, vmax = 988, 1028
levels = np.linspace(vmin, vmax, 11)

# === 各ファイルを処理 ===
for variant in variants:
    # JSTに基づいた日付でGRIBファイルのパスを生成
    grib_file = os.path.join(
        base_dir, f'Z__C_RJTD_{formatted_date}120000_GSM_GPV_Rgl_FD{variant}_grib2.bin'
    )

    # GRIBファイルを開き、必要なデータを取得
    grbs = pygrib.open(grib_file)

    # 海面更生気圧 (PRMSL) データ取得
    grb = grbs.select(name='Pressure reduced to MSL')[0]
    data, lats, lons = grb.data()

    # 風成分のデータを取得 (U風とV風)
    grb_u = grbs.select(name='10 metre U wind component')[0]
    grb_v = grbs.select(name='10 metre V wind component')[0]
    u_data = grb_u.values
    v_data = grb_v.values

    # 緯度・経度のインデックス取得
    lat_indices = np.where((lats[:, 0] >= 35) & (lats[:, 0] <= 56))[0][::2]
    lon_indices = np.where((lons[0, :] >= 120) & (lons[0, :] <= 162.5))[0][::2]

    # データの抽出と平滑化
    extracted_data = data[np.ix_(lat_indices, lon_indices)] / 100  # hPaに変換
    extracted_u = u_data[np.ix_(lat_indices, lon_indices)]
    extracted_v = v_data[np.ix_(lat_indices, lon_indices)]
    smoothed_data = gaussian_filter(extracted_data, sigma=1)

    # 地図の設定と描画
    fig, ax = plt.subplots(figsize=(10, 8))
    m = Basemap(projection='mill', llcrnrlat=35, urcrnrlat=56,
                llcrnrlon=120, urcrnrlon=162.5, resolution='l', ax=ax)

    # メッシュグリッドの作成
    lon2d, lat2d = np.meshgrid(lons[0, lon_indices], lats[lat_indices, 0])
    x, y = m(lon2d, lat2d)

    # 等圧線と塗りつぶしの描画
    cs = m.contourf(x, y, smoothed_data, levels=levels, cmap='bwr', alpha=0.7, extend='both')
    contour_lines = m.contour(x, y, smoothed_data, levels=levels, colors='black', linewidths=0.5)

    # 風の矢羽根（quiver）の追加
    skip = (slice(None, None, 2), slice(None, None, 2))  # データを間引いて表示
    q = m.quiver(x[skip], y[skip], extracted_u[skip], extracted_v[skip],
                 scale=450, color='black', pivot='middle', width=0.003)

    # 海岸線と経緯線の描画
    m.drawcoastlines()
    m.drawparallels(np.arange(35, 57, 5), labels=[1, 0, 0, 0], fontsize=10)
    m.drawmeridians(np.arange(120, 163, 5), labels=[0, 0, 0, 1], fontsize=10)

    # カラーバーの追加
    cbar = m.colorbar(cs, location='right', pad='5%')
    cbar.set_label('Pressure (hPa)')

    # タイトル設定
    plt.title(f'Sea Level Pressure and Wind - FD{variant}')

    # 画像の保存
    output_path = os.path.join(output_dir, f'Pressure_Wind_FD{variant}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)  # メモリを解放

    print(f'画像を保存しました: {output_path}')
