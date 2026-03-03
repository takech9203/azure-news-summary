# Azure News Summary

Microsoft Azure の新機能リリース・発表などのニュースを自動収集し、日本語でサマリーレポートを作成するツール。

## 概要

Azure Updates RSS フィードから最新のアップデート情報を取得し、Claude Agent SDK を使用して詳細なレポートとインフォグラフィックを自動生成します。

## 特徴

- Azure Updates RSS からの自動情報収集
- Azure Blog との連携
- 日本語での詳細レポート生成
- Mermaid によるアーキテクチャ図
- HTML インフォグラフィックの自動生成
- GitHub Actions による日次自動実行

## データソース

| ソース | URL | 説明 |
|--------|-----|------|
| Azure Updates | https://www.microsoft.com/releasecommunications/api/v2/azure/rss | 公式アップデート情報 |
| Azure Blog | https://azure.microsoft.com/en-us/blog/feed/ | 技術ブログ記事 |

## ディレクトリ構造

```
azure-news-summary/
├── .claude/skills/          # スキル定義
│   ├── azure-news-summary/  # レポート生成スキル
│   └── creating-infographic/ # インフォグラフィック生成スキル
├── .github/workflows/       # GitHub Actions
├── reports/                 # 生成されたレポート (Markdown)
├── infographic/             # 生成されたインフォグラフィック (HTML)
├── docs/                    # ドキュメント
└── run.py                   # オーケストレーター
```

## 使用方法

### 前提条件

- Python 3.12+
- AWS アカウント (Amazon Bedrock アクセス)
- Claude Agent SDK

### インストール

```bash
# リポジトリのクローン
git clone https://github.com/YOUR_ORG/azure-news-summary.git
cd azure-news-summary

# 依存関係のインストール
pip install -r requirements.txt
```

### 実行

```bash
# デフォルト設定で実行 (過去 3 日間)
python run.py

# 期間を指定
python run.py --days 7

# デバッグモードで実行
python run.py --days 3 --debug

# インフォグラフィック生成をスキップ
python run.py --skip-infographic
```

### スキル実行 (Claude Code)

```
/azure-news-summary
```

## 出力形式

### レポート (Markdown)

各アップデートについて以下の情報を含むレポートを生成します。

- 概要と Before/After 比較
- アーキテクチャ図 (Mermaid)
- 主要機能の詳細
- 技術仕様
- 設定方法 (Azure CLI / Azure Portal)
- メリット・デメリット
- ユースケース
- 料金情報
- 関連サービス

### インフォグラフィック (HTML)

レポートを視覚的に表現した HTML ファイルを生成します。

- Azure ブランドカラーを使用
- レスポンシブデザイン
- Mermaid 図の埋め込み
- highlight.js によるコードハイライト

## CI/CD

GitHub Actions により毎日 05:00 JST に自動実行されます。

詳細なセットアップ手順は [docs/SETUP.md](docs/SETUP.md) を参照してください。

## ライセンス

MIT License

## 関連プロジェクト

- [Google Cloud News Summary](https://github.com/YOUR_ORG/google-cloud-news-summary) - 同様の機能を Google Cloud 向けに提供
