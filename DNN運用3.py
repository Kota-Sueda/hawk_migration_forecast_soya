from tensorflow.keras.models import load_model
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
import joblib
import matplotlib.pyplot as plt
import matplotlib
import os

# 日本語フォントの設定
matplotlib.rc('font', family='Meiryo')

# === 日本時間を取得（UTC+9） ===
JST = timezone(timedelta(hours=9))
today = datetime.now(JST).date()
reference_date = datetime(2024, 9, 15).date()

# 7日間のリストを生成
date_list = [today + timedelta(days=i) for i in range(-2, 5)]
days_from_reference_list = [(date - reference_date).days for date in date_list]
print(days_from_reference_list)

# === CSVファイルからデータを読み込み ===
file_path = r'D:\GSMdownload\similarity_list\similar_nodes.csv'
df = pd.read_csv(file_path, header=None)

# 1行目のデータをリストに変換
numbers = df.iloc[0].tolist()

# 3つずつ抽出して5つのリストを生成
result = [numbers[i:i + 3] for i in range(5)]
print(result)

# 4要素の新しいリストを作成
selected_numbers = days_from_reference_list[2:7]
new_data = [[selected_numbers[i]] + result[i] for i in range(5)]
print(new_data)

# numpy配列に変換
new_data_np = np.array(new_data)

# === 学習済みモデルとスケーラーのロード ===
model = load_model(r'C:\Users\sedko\Downloads\hawk_migration_forecast_ver5.h5')
scaler = joblib.load(r'C:\Users\sedko\Downloads\hawk_migration_forecast_ver5.pkl')  # 学習時のスケーラーをロード

# データを標準化（スケーリング）
new_data_scaled = scaler.transform(new_data_np)

# モデルで予測を実行
predictions = model.predict(new_data_scaled)



# === 既存のソフトマックス出力（2-6行目）をCSVから取得 ===
existing_softmax_path = r'D:\GSMdownload\humidity_wind\logistic_results.csv'
existing_softmax_df = pd.read_csv(existing_softmax_path)

# 2-6行目のデータを取得（各クラスの確率）
existing_softmax = existing_softmax_df.iloc[0:5, 1:].values  # 各クラスの確率部分
print("既存のソフトマックス出力:")
print(existing_softmax)

print(f"predictions.shape: {predictions.shape}")
print(f"existing_softmax.shape: {existing_softmax.shape}")


# === 既存の出力と新しい出力を要素ごとに乗じる ===
combined_output = predictions + (2 * existing_softmax) # 対応する要素を掛け合わせる
print("乗算された新しいソフトマックス出力:")
print(combined_output)


# === 各行ごとに正規化（ソフトマックス化）する関数 ===
def softmax_normalization(output):
    # 各行の値を合計が1になるように正規化
    row_sums = np.sum(output, axis=1, keepdims=True)  # 行ごとの合計
    normalized_output = output / row_sums  # 各要素を合計で割る
    return normalized_output

# 新しいソフトマックス出力を正規化
normalized_output = softmax_normalization(combined_output)
print("正規化されたソフトマックス出力:")
print(normalized_output)


# === クラスに応じたシンボルを取得する関数 ===
def get_symbol(class_num):
    if class_num in [0, 1]:
        return '✕'
    elif class_num in [2, 3]:
        return '△'
    elif class_num in [4, 5]:
        return '〇'
    elif class_num in [6, 7]:
        return '◎'
    else:
        return ''  # 該当しない場合は空文字

# === グラフ保存先ディレクトリを作成 ===
save_directory = r"D:\GSMdownload\histogram"
os.makedirs(save_directory, exist_ok=True)

# === ヒストグラムを表示・保存 ===
for i, prediction in enumerate(normalized_output):
    plt.figure(figsize=(5, 10))

    # 横向きの棒グラフ（barh）
    bars = plt.barh(
        range(len(prediction)), prediction, tick_label=range(len(prediction)), color='orange'
    )
    plt.gca().invert_yaxis()

    # 各バーに予測値のラベルを追加
    for bar, value in zip(bars, prediction):
        plt.text(
            bar.get_width(),  # x座標（バーの右端）
            bar.get_y() + bar.get_height() / 2,  # y座標（バーの中央）
            f'{value:.2f}',  # ラベルのテキスト（小数点2桁）
            va='center', ha='left',  # ラベルの位置調整
            fontsize=15
        )

    # 最も高い確率を持つクラスと対応するシンボルを取得
    top_class = np.argmax(prediction)
    symbol = get_symbol(top_class)
    node_value = numbers[i + 2]  # i + 2 番目の数を取得

    # グラフ上部に Node 情報を配置
    plt.text(
        0.5, 1.05, f'{symbol}', 
        fontsize=50, ha='center', va='bottom', transform=plt.gca().transAxes
    )

    # タイトルを設定
    plt.title(f'クラス: {top_class}', fontsize=20, fontweight='bold')

    # サブタイトル（シンボル）を少し離して配置
    plt.suptitle(
        f'Node: {node_value}', fontsize=20, y=1.0
    )

    # グラフのレイアウト調整
    plt.subplots_adjust(top=0.85)
    plt.ylabel('クラス', fontsize=15)
    plt.xlabel('確率', fontsize=15)
    plt.tick_params(axis='x', labelsize=12)
    plt.tick_params(axis='y', labelsize=12)
    plt.xlim(0, 1)

    # 保存するファイル名を設定
    save_path = os.path.join(save_directory, f"histogram_{i + 1}.png")
    plt.savefig(save_path, bbox_inches='tight')  # グラフを保存
    print(f"グラフを保存しました: {save_path}")

# グラフを表示
plt.show()


