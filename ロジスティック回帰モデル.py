import os
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib  # スケーラーとモデルの保存に使用

# 保存先のパスを指定
output_dir = r'C:\Users\sedko\OneDrive\デスクトップ'
scaler_path = os.path.join(output_dir, 'scaler_logistic.pkl')
model_path = os.path.join(output_dir, 'relativehumidity_wind_logistic_model.pkl')

# CSVファイルを読み込み（ファイルパスは適宜変更）
data = pd.read_csv(r'C:\Users\sedko\OneDrive\デスクトップ\ロジスティック回帰モデル2023.csv')

# 説明変数（RH, EW, NS）と目的変数（MigN）を抽出
X = data[['RH', 'EW', 'NS']].values  # 説明変数
y = data['MigN'].values  # 渡り数（8クラス）

# 説明変数を標準化
scaler = StandardScaler()
X = scaler.fit_transform(X)

# スケーラーの保存
joblib.dump(scaler, scaler_path)

# 7分割クロスバリデーションの設定
kf = KFold(n_splits=7, shuffle=True, random_state=42)

# ロジスティック回帰モデルのインスタンスを作成
model = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=100)

# クロスバリデーションでのスコアを取得
scores = cross_val_score(model, X, y, cv=kf, scoring='accuracy')

print(f'各分割の精度: {scores}')
print(f'平均精度: {scores.mean():.2f} ± {scores.std():.2f}')

# クロスバリデーションの中で予測結果も取得する
y_true_list = []
y_pred_list = []

for train_index, test_index in kf.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    
    # モデルの学習
    model.fit(X_train, y_train)
    
    # 予測確率の取得（ソフトマックス出力）
    y_prob = model.predict_proba(X_test)
    
    # 最も確率の高いクラスを予測
    y_pred = np.argmax(y_prob, axis=1)
    
    # 各分割の予測と実際の値を保存
    y_true_list.extend(y_test)
    y_pred_list.extend(y_pred)

# 全体の分類レポートを表示
print(classification_report(y_true_list, y_pred_list))

# 学習したモデルを保存
joblib.dump(model, model_path)

print("スケーラーとモデルが保存されました。")
