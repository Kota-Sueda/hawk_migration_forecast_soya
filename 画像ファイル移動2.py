import os
import shutil

def copy_png_files(source_folders, destination_folder):
    """
    複数のフォルダから .png ファイルをコピーし、指定のフォルダに保存する。
    """

    copied_files = []  # コピーされたファイルのリスト

    # 各コピー元フォルダを順に処理
    for source_folder in source_folders:
        if not os.path.exists(source_folder):
            print(f"フォルダが見つかりません: {source_folder}")
            continue  # フォルダが存在しない場合、次のフォルダに進む

        # 指定フォルダ内のファイルを走査
        for filename in os.listdir(source_folder):
            if filename.endswith(".png"):
                # コピー元およびコピー先のパスを定義
                source_path = os.path.join(source_folder, filename)
                destination_path = os.path.join(destination_folder, filename)

                try:
                    # ファイルをコピー
                    shutil.copy2(source_path, destination_path)
                    copied_files.append(filename)  # コピー成功時にリストへ追加
                    print(f"Copied: {filename} → {destination_path}")
                except Exception as e:
                    print(f"ファイルのコピーに失敗しました: {filename} - {e}")

    # 結果の出力
    if copied_files:
        print(f"\n{len(copied_files)} 個の PNG ファイルがコピーされました。")
    else:
        print("PNG ファイルが見つかりませんでした。")

# === 使用例 ===
# コピー元のフォルダをリストで指定
source_folders = [
    r"D:\GSMdownload\histogram",  # 1つ目のフォルダ
    r"D:\GSMdownload\weathermap"  # 2つ目のフォルダ
]

# コピー先のローカルフォルダ
destination_folder = r"C:\Users\sedko\OneDrive\デスクトップ\渡り予報サイト\image"

# 関数を呼び出してファイルをコピー
copy_png_files(source_folders, destination_folder)
