import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
import pytz
import joblib
from tensorflow.keras.models import load_model

# === 設定 ===
# 出力CSVの保存先フォルダ
output_dir = r'D:\GSMdownload\humidity_wind'

# モデルとスケーラーのパス
model_path = r'C:\Users\sedko\OneDrive\デスクトップ\relativehumidity_wind_logistic_model.pkl'
scaler_path = r'C:\Users\sedko\OneDrive\デスクトップ\scaler_logistic.pkl'

# === 入力データ（2-6行目）をCSVから取得 ===
input_csv = r'D:\GSMdownload\humidity_wind\relativehumidity_wind.csv'
input_df = pd.read_csv(input_csv)

# 2-6行目のデータを取得（RH, UWind, VWindの3列）
input_data = input_df.iloc[0:5][['RH', 'UWind', 'VWind']].values 

# === 学習済みモデルとスケーラーのロード ===
model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# === モデルへの入力と予測 ===
softmax_results = []

for i, row in enumerate(input_data):
    # 入力データの整形とスケーリング
    input_data_scaled = scaler.transform([row])

    # モデルで予測し、ソフトマックス出力（各クラスの確率）を取得
    y_prob = model.predict_proba(input_data_scaled)  # 各クラスの確率を取得

    # y_probは2D配列なので、1次元配列を取得
    softmax_output = y_prob[0]

    # ソフトマックス出力をリストに保存
    softmax_results.append([f'Variant_{i+1}'] + softmax_output.tolist())

# === 予測結果をCSVに保存 ===
# カラム名を作成（Variant + 各クラスの出力名）
columns = ['Variant'] + [f'Class_{i}' for i in range(softmax_output.shape[0])]

# データフレームに変換
df = pd.DataFrame(softmax_results, columns=columns)

# CSVファイルの保存先と名前を指定
csv_filename = f'logistic_results.csv'
csv_path = os.path.join(output_dir, csv_filename)

# CSVに保存
df.to_csv(csv_path, index=False, encoding='utf-8')

print(f"予測結果が保存されました: {csv_path}")
