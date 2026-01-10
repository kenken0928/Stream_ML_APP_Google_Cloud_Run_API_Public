# Google_Cloudrun_ML_API
（Google Cloud Run / CSV 推論 API）

このリポジトリは、Google Cloud Run 上で動作する  
**CSV バッチ推論用 FastAPI アプリケーション** です。

Cloudflare Pages Functions から CSV ファイルを受け取り、  
scikit-learn で学習済みのモデルを用いて推論を行い、  
**推論結果を CSV として返却**します。

---

## 役割（このリポジトリの責務）

- 学習済みモデル（model.joblib）のロード
- CSV 入力の検証
- 推論（predict / predict_proba）
- 推論結果 CSV の生成
- API_TOKEN による簡易認証
- Cloud Run 上でのスケーラブル実行

---

## 全体構成

[Cloudflare Pages Functions]  
↓ CSV + Bearer Token  
[Cloud Run (FastAPI)]  
・モデルロード  
・推論  
・CSV 生成  
↓  
[CSV Response]

---

## 技術スタック

- Python
- FastAPI
- scikit-learn
- pandas
- joblib
- Docker
- Google Cloud Run

---

## ディレクトリ構成
```
/
├─ main.py                    # FastAPI アプリ本体（CSV 推論 API）
├─ model.joblib               # 学習済みモデル
├─ train_df.csv               # モデル学習用データ
├─ test_df.csv                # 予測対象データ（推論入力）
├─ requirements.txt           # Python 依存関係
├─ Dockerfile                 # Cloud Run 用コンテナ定義
├─ README.md                  # リポジトリ説明・API 仕様
└─ notebooks/
   └─ train_model.ipynb       # 学習済みモデル生成用 Notebook（参考・再学習用）

```
---

## API 仕様

### ヘルスチェック

GET /health

Response:
{
  "status": "ok"
}

---

### CSV 推論 API

POST /predict_csv

Headers:
Authorization: Bearer <API_TOKEN>

Body:
- multipart/form-data
- file: CSV ファイル

---

### 入力 CSV の前提

- `id` カラムは必須
- `Target` カラムは存在しない前提
  - 存在した場合は自動で除外
- 特徴量カラムは学習時と同一構成であること

---

### 出力 CSV

- id
- pred（0 / 1）
- proba（予測確率）

---

## 環境変数（Cloud Run）

Cloud Run サービスの「変数とシークレット」に以下を設定：

| Name | 内容 |
|----|----|
| API_TOKEN | Cloudflare 側と共通の Bearer Token |
| MODEL_PATH | model.joblib（通常は不要・デフォルトあり） |

---

## デプロイ方法（概要）

- 本リポジトリを GitHub に push
- Cloud Run で「リポジトリから継続的にデプロイ」を選択
- Dockerfile を使用してビルド
- 公開アクセスを許可
- 発行された Cloud Run URL を Cloudflare 側に設定

---

## 注意事項

- ML 推論は **同期処理** を前提
- concurrency は低め（1〜2）を推奨
- 大量リクエストは Cloudflare 側で制御すること

---

## 補足

- モデル更新時は model.joblib を差し替えて再デプロイ
- 学習処理は本リポジトリの責務外
