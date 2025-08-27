# Document Intelligence Services Comparison

Azure Document Intelligence と Google Cloud Document AI の性能を比較するためのPythonサンプルコードです。

## 機能

- **表構造解析**: 両サービスの表検出・抽出性能を比較
- **画像テキスト抽出**: OCR性能の比較
- **処理時間測定**: レスポンス時間の比較
- **信頼度スコア**: 各サービスの結果信頼度比較
- **バッチ処理**: 複数ドキュメントの一括比較
- **レポート生成**: JSON・CSVでの結果出力

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
# 環境設定の確認とサンプルファイル作成
python setup_environment.py
```

`.env.example`を`.env`にコピーして、必要な認証情報を設定してください：

```bash
# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_api_key

# Google Cloud Document AI  
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_DOCUMENT_AI_PROCESSOR_ID=your_processor_id
```

### 3. 認証設定

**Azure:**
- Azure ポータルでDocument Intelligenceリソースを作成
- エンドポイントとAPIキーを取得

**Google Cloud:**
- Document AI APIを有効化
- サービスアカウントキーを作成・ダウンロード
- プロセッサーを作成してIDを取得

## 使用方法

### 単一ドキュメントの比較

```python
from performance_comparison import DocumentIntelligenceComparison

# 比較ツールの初期化
comparator = DocumentIntelligenceComparison()

# ドキュメント分析
result = comparator.compare_services(
    document_path="sample_document.pdf",
    azure_model_id="prebuilt-layout",
    google_processor_id="your_processor_id"
)

# レポート生成
comparator.generate_report("comparison_report.json")
comparator.export_to_csv("results.csv")
```

### バッチ処理

```python
# 複数ドキュメントの一括比較
batch_results = comparator.batch_comparison(
    documents_dir="sample_documents/",
    azure_model_id="prebuilt-layout", 
    google_processor_id="your_processor_id"
)
```

### 個別サービスの使用

```python
# Azure単体での使用
from azure_document_intelligence import create_azure_client

azure_client = create_azure_client()
result = azure_client.analyze_document("document.pdf")

# Google単体での使用  
from google_document_ai import create_google_client

google_client = create_google_client()
result = google_client.analyze_document("document.pdf", "processor_id")
```

## 出力形式

### JSON レポート
```json
{
  "summary": {
    "total_documents": 5,
    "successful_comparisons": 4,
    "performance_summary": {
      "azure_avg_time": 2.3,
      "google_avg_time": 1.8,
      "azure_fastest_count": 1,
      "google_fastest_count": 3
    }
  },
  "detailed_results": [...]
}
```

### CSV エクスポート
- 処理時間比較
- テキスト抽出長
- 表検出数
- 信頼度スコア
- など

## テストドキュメント

以下のタイプのドキュメントでテストすることを推奨：

1. **表構造**: 
   - シンプルな3x3テーブル
   - 複雑な結合セル含むテーブル
   - 複数テーブル含む文書

2. **画像テキスト**:
   - スキャンした文書
   - スクリーンショット
   - 手書きテキスト

3. **混合コンテンツ**:
   - 請求書
   - フォーム
   - レポート

## ファイル構成

```
doc-intelligence/
├── azure_document_intelligence.py  # Azure実装
├── google_document_ai.py          # Google実装  
├── performance_comparison.py       # 比較ツール
├── setup_environment.py           # 環境設定
├── requirements.txt               # 依存関係
├── README.md                     # このファイル
├── .env.example                  # 環境変数サンプル
└── sample_documents/             # テスト用ドキュメント
```

## 注意事項

- APIキーは適切に管理してください
- 両サービスともAPIコールに料金が発生する場合があります
- 大きなファイルや大量のファイル処理時は制限に注意してください
- 機密情報を含むドキュメントの使用時は各サービスのプライバシーポリシーを確認してください