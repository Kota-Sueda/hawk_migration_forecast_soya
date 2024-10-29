import pygrib
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
import pytz  

# === 設定 ===
# GRIBファイルの保存ディレクトリ
base_dir = r'D:\GSMdownload'

# 画像保存先フォルダ（CSVファイルもこのフォルダに保存）
output_dir = r'D:\GSMdownload\humidity_wind'

# JSTのタイムゾーンを取得
jst = pytz.timezone('Asia/Tokyo')

# 現在のJSTの前日を取得
yesterday_jst = datetime.now(jst) - timedelta(days=1)
formatted_date = yesterday_jst.strftime('%Y%m%d')

# ダウンロードしたGRIBファイルのバリアント
variants = ["0012", "0112", "0212", "0312", "0412"]

# 取得する緯度・経度
target_lat = 45.5
target_lon = 142.0

# データを保存するリスト
data_list = []

# === 各ファイルを処理 ===
for variant in variants:
    # JSTに基づいた日付でGRIBファイルのパスを生成
    grib_file = os.path.join(
        base_dir, f'Z__C_RJTD_{formatted_date}120000_GSM_GPV_Rgl_FD{variant}_grib2.bin'
    )

    # ファイルが存在するかチェック
    if not os.path.exists(grib_file):
        print(f"ファイルが見つかりません: {grib_file}")
        continue

    # GRIBファイルを開く
    grbs = pygrib.open(grib_file)

    # 必要な変数（相対湿度、東西風、南北風）を取得
    rh = grbs.select(name='Relative humidity')[0]
    uwind = grbs.select(name='U component of wind')[0]  # 東西風
    vwind = grbs.select(name='V component of wind')[0]  # 南北風

    # 指定座標のインデックスを取得
    lat, lon = rh.latlons()
    idx = np.unravel_index(
        np.argmin((lat - target_lat)**2 + (lon - target_lon)**2), lat.shape
    )

    # 各変数から指定点の値を取得
    rh_value = rh.values[idx]
    uwind_value = uwind.values[idx]
    vwind_value = vwind.values[idx]

    # データをリストに保存
    data_list.append([variant, rh_value, uwind_value, vwind_value])

# === 保存するCSVファイル名を指定 ===
csv_filename = f'relativehumidity_wind.csv'
csv_path = os.path.join(output_dir, csv_filename)

# === データをCSVに保存 ===
df = pd.DataFrame(data_list, columns=['Variant', 'RH', 'UWind', 'VWind'])
df.to_csv(csv_path, index=False, encoding='utf-8')

print(f"データが保存されました: {csv_path}")
