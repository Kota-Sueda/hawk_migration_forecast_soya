import requests
from datetime import datetime, timedelta
import os
import glob
import pytz

# === 設定 ===
# 外付けHDDの保存先パス 
save_dir = r"D:\GSMdownload"

jst = pytz.timezone('Asia/Tokyo')
today = datetime.now(jst)

base_url = "https://database.rish.kyoto-u.ac.jp/arch/jmadata/data/gpv/original"

# ダウンロード対象の日付を指定（例：昨日のデータ）
target_date = today - timedelta(days=1)

# FD0012, 0112, 0212, 0312, 0412 のファイルを取得
file_variants = ["0012", "0112", "0212", "0312", "0412"]

# === ダウンロード処理 ===
for variant in file_variants:
    # 日付に基づいて URL とファイル名を生成
    date_str = target_date.strftime("%Y/%m/%d")
    filename = f"Z__C_RJTD_{target_date.strftime('%Y%m%d120000')}_GSM_GPV_Rgl_FD{variant}_grib2.bin"
    download_url = f"{base_url}/{date_str}/{filename}"

    # ダウンロード先のファイルパスを生成
    output_file = os.path.join(save_dir, filename)

    # ファイルをダウンロード
    try:
        print(f"ダウンロード中: {download_url}")
        response = requests.get(download_url, stream=True)

        if response.status_code == 200:
            # バイナリモードでファイルを保存
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"ダウンロード完了: {output_file}")
        else:
            print(f"エラー: {response.status_code} - ファイルが見つかりませんでした")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

#=======================================================================================================

jst = pytz.timezone('Asia/Tokyo')

# 現在の日本時間を取得し、3日前から2日前までの範囲で日付を生成
now_jst = datetime.now(jst)
start_date = now_jst - timedelta(days=3)  # 3日前
end_date = now_jst - timedelta(days=2)    # 2日前

# === ダウンロード処理 ===
def download_file2(date):
    """
    指定された日付のデータをダウンロードする関数
    """
    base_url = "https://database.rish.kyoto-u.ac.jp/arch/jmadata/data/gpv/original"

    # URLとファイル名を生成
    date_str = date.strftime("%Y/%m/%d")
    filename = f"Z__C_RJTD_{date.strftime('%Y%m%d120000')}_GSM_GPV_Rgl_FD0012_grib2.bin"
    download_url = f"{base_url}/{date_str}/{filename}"

    # 保存するファイルのパス
    output_file = os.path.join(save_dir, filename)

    # ファイルのダウンロード
    try:
        print(f"ダウンロード中: {download_url}")
        response = requests.get(download_url, stream=True)

        if response.status_code == 200:
            # バイナリモードでファイルを保存
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"ダウンロード完了: {output_file}")
        else:
            print(f"エラー: {response.status_code} - ファイルが見つかりませんでした")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

# === 3日前から2日前までのデータをダウンロード ===
current_date = start_date
while current_date <= end_date:
    download_file2(current_date)
    current_date += timedelta(days=1)


# === 古いファイルの削除処理 ==========================================================================
def delete_old_files(directory, days=2):
    """
    指定されたディレクトリ内の古いファイルを削除する関数。
    """
    now = datetime.now()
    threshold_date = now - timedelta(days=days)  # 削除基準の日付

    # 指定されたディレクトリ内のすべての .bin ファイルを検索
    for file_path in glob.glob(os.path.join(directory, "*.bin")):
        # ファイルの最終更新日時を取得
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

        # 削除基準を超えた古いファイルを削除
        if file_mtime < threshold_date:
            try:
                os.remove(file_path)
                print(f"削除しました: {file_path}")
            except Exception as e:
                print(f"削除エラー: {file_path} - {e}")

# 古いファイルの削除を実行
delete_old_files(save_dir, days=10)
