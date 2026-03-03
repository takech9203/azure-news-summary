# Azure News Summary

Microsoft Azure の新機能リリース・発表などのニュースを自動収集し、日本語でサマリーレポートを作成するプロジェクト。

## プロジェクト概要

- **目的**: Azure の最新アップデートを自動収集し、Solutions Architect 向けの詳細レポートを生成
- **出力**: Markdown レポート (`reports/`) + HTML インフォグラフィック (`infographic/`)
- **実行方法**: 手動実行 or GitHub Actions による日次自動実行

## 技術スタック

- Python 3.12
- Claude Agent SDK (Amazon Bedrock)
- GitHub Actions

## データソース

1. **Azure Updates RSS**: `https://www.microsoft.com/releasecommunications/api/v2/azure/rss`
2. **Azure Blog RSS**: `https://azure.microsoft.com/en-us/blog/feed/`
3. **Azure Tech Community RSS**: `https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/Category?category.id=Azure`

## ディレクトリ構造

```
azure-news-summary/
├── .claude/skills/          # スキル定義
│   ├── azure-news-summary/  # レポート生成スキル
│   └── creating-infographic/ # インフォグラフィック生成スキル
├── .github/workflows/       # GitHub Actions
├── reports/                 # 生成されたレポート (年別サブフォルダ)
├── infographic/             # 生成されたインフォグラフィック
├── docs/                    # ドキュメント
└── run.py                   # オーケストレーター
```

## 実行方法

### 手動実行

```bash
# 過去 3 日間のアップデートをレポート
python run.py --days 3

# デバッグモードで実行
python run.py --days 3 --debug
```

### スキル実行

```
/azure-news-summary
```

## 注意事項

- RSS フィードは 1 回だけ取得する (複数回リクエストしない)
- 推測で情報を埋めない。確認できた情報のみ記載する
- 1 アップデート = 1 レポートファイル
