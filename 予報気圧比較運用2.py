import pygrib
import numpy as np
import xarray as xr
import netCDF4
import h5netcdf
from numpy import dot
from numpy.linalg import norm
import os
from datetime import datetime, timedelta
import csv
import pandas as pd

# === GRIBファイルからデータを取得する関数 ===
def extract_grib_data(grib_file):
    """GRIBファイルから気圧データを抽出する関数"""
    try:
        grbs = pygrib.open(grib_file)
        grb = grbs.select(name='Pressure reduced to MSL')[0]
        data, lats, lons = grb.data()

        # 緯度・経度の範囲に対応するインデックスを抽出（2.5度刻み）
        lat_indices = np.where((lats[:, 0] >= 35) & (lats[:, 0] <= 56))[0][::5]
        lon_indices = np.where((lons[0, :] >= 120) & (lons[0, :] <= 162.5))[0][::5]

        # データを抽出し、フラットな配列に変換
        extracted_data = data[np.ix_(lat_indices, lon_indices)]
        return extracted_data.flatten()
    except Exception as e:
        print(f"エラー: {e}")
        return None

# === ncファイルからデータを取得する関数 ===
def extract_nc_data(nc_file, node_index):
    """NetCDFファイルから特定ノードのデータを取得する関数"""
    try:
        ds = xr.open_dataset(nc_file)
        var_name = 'PRMSL_msl'
        data = ds[var_name]

        # 緯度データを飛ばして取得
        extracted_data = data.isel(lat=slice(1, None, 2))
        pressure_data = extracted_data.isel(n=node_index)

        return pressure_data.values.flatten()
    except Exception as e:
        print(f"エラー: {e}")
        return None

# === コサイン類似度を計算する関数 ===
def cosine_similarity(map1, map2):
    """2つの配列間のコサイン類似度を計算"""
    return dot(map1, map2) / (norm(map1) * norm(map2))

# === NetCDFファイルの設定 ===
nc_file = r'C:\Users\sedko\output\n20ed-7.nc'

# === 現在の日本時間を取得し、必要な日付を生成 ===
jst = datetime.utcnow() + timedelta(hours=9)
twodays = (jst - timedelta(days=2)).strftime('%Y%m%d')
threedays = (jst - timedelta(days=3)).strftime('%Y%m%d')

# GRIBファイルの保存先ディレクトリ
base_dir = r'D:\GSMdownload'

# GRIBファイルのパスを生成
grib_file_2days = os.path.join(base_dir, f'Z__C_RJTD_{twodays}120000_GSM_GPV_Rgl_FD0012_grib2.bin')
grib_file_3days = os.path.join(base_dir, f'Z__C_RJTD_{threedays}120000_GSM_GPV_Rgl_FD0012_grib2.bin')

# GRIBデータを取得
data_2days = extract_grib_data(grib_file_2days)
data_3days = extract_grib_data(grib_file_3days)

# 最も類似するノードを保存するリスト
most_similar_nodes = []

# === コサイン類似度の計算とノードの追跡 ===
for i in [3, 2]:  # 3日前→2日前の順で処理
    data_idays = data_3days if i == 3 else data_2days
    max_similarity = float('-inf')
    most_similar_node = -1

    # ノードごとにコサイン類似度を計算
    for node_index in range(20):  # n=0から19まで
        nc_data = extract_nc_data(nc_file, node_index)
        distance = cosine_similarity(data_idays, nc_data)
        print(f"ノード {node_index} のコサイン類似度: {distance}")

        if distance > max_similarity:
            max_similarity = distance
            most_similar_node = node_index

    print(f"\n[{i}日前] 最も類似するノード: {most_similar_node}, 類似度: {max_similarity}")
    most_similar_nodes.append(most_similar_node)

# === 前日のGRIBファイルに対する処理 ===
yesterday = (jst - timedelta(days=1)).strftime('%Y%m%d')
variants = ["0012", "0112", "0212", "0312", "0412"]

for variant in variants:
    grib_file = os.path.join(base_dir, f'Z__C_RJTD_{yesterday}120000_GSM_GPV_Rgl_FD{variant}_grib2.bin')
    grib_data = extract_grib_data(grib_file)

    max_similarity = float('-inf')
    most_similar_node = -1

    # ノードごとにコサイン類似度を計算
    for node_index in range(20):  # n=0から19まで
        nc_data = extract_nc_data(nc_file, node_index)
        distance = cosine_similarity(grib_data, nc_data)
        print(f"ノード {node_index} のコサイン類似度: {distance}")

        if distance > max_similarity:
            max_similarity = distance
            most_similar_node = node_index

    print(f"\n[{variant}] 最も類似するノード: {most_similar_node}, 類似度: {max_similarity}")
    most_similar_nodes.append(most_similar_node)

# === 最終結果の表示 ===
print("\n=== 7回の最も類似するノードの結果 ===")
print(most_similar_nodes)

# === リストをCSVファイルに保存 ===
output_csv_dir = r"D:\GSMdownload\similarity_list"
csv_path = os.path.join(output_csv_dir, "similar_nodes.csv")

# リストをCSVファイルに保存
with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(most_similar_nodes)

print(f"\n最も類似するノードの結果を {csv_path} に保存しました。")