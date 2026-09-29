# Azure SQL Database (MSSQL extension for VS Code): SQL Formatter の一般提供開始

**リリース日**: 2026-09-29

**サービス**: Azure SQL Database / MSSQL extension for Visual Studio Code

**機能**: SQL Formatter

**ステータス**: Launched (GA)

[このアップデートのインフォグラフィックを見る](https://takech9203.github.io/azure-news-summary/20260929-sql-formatter-vscode.html)

## 概要

Visual Studio Code の MSSQL 拡張機能に組み込まれた SQL Formatter が一般提供 (GA) となりました。VS Code 上で T-SQL スクリプトを直接フォーマットできるようになり、一貫性のある読みやすい SQL コードを維持できます。オンデマンドでのフォーマット実行に加え、ファイル保存時の自動フォーマット (format on save) にも対応し、豊富な設定オプションによりチームや個人のコーディングスタイルに合わせたカスタマイズが可能です。

このフォーマット機能は、T-SQL を解析して抽象構文木 (AST) ベースでスクリプトを生成するオープンソースの .NET ライブラリ [ScriptDOM](https://github.com/microsoft/sqlscriptdom) 上に構築されています。MSSQL 拡張機能は Azure SQL Database、Azure SQL Managed Instance、SQL Server on Azure VM、SQL database in Microsoft Fabric、SQL Server をサポートしており、これらのデータベースを対象とした開発ワークフローで利用できます。

**アップデート前の課題**

- VS Code の MSSQL 拡張機能には T-SQL 向けの組み込みフォーマッターがなく、SQL スクリプトの整形にはサードパーティ拡張機能や外部ツールが必要だった
- チーム開発において SQL コードのスタイル (キーワードの大文字/小文字、カンマ位置、改行ルールなど) を統一する仕組みがエディター内になく、コードレビューや保守の負担になっていた

**アップデート後の改善**

- VS Code の標準操作 (Format Document / Format Selection) で T-SQL をエディター内で直接フォーマットできるようになった
- `editor.formatOnSave` により保存時の自動フォーマットが可能になり、常に整形されたコードを維持できる
- キーワードの大文字/小文字、句の整列、カンマ位置、改行、インデントなど多数の `mssql.format.*` 設定でスタイルを細かくカスタマイズできる

## アーキテクチャ図

```mermaid
flowchart LR
    Dev([👤 開発者]) -->|Format Document /<br>Format on Save| VSCode["📝 VS Code +<br>MSSQL 拡張機能"]
    VSCode -->|T-SQL スクリプト| ScriptDOM["⚙️ ScriptDOM<br>(オープンソース .NET ライブラリ)"]
    ScriptDOM -->|パース| AST["🌳 抽象構文木 (AST)"]
    AST -->|"mssql.format.* 設定を適用<br>してスクリプト再生成"| Formatted["✨ 整形済み T-SQL"]
    Formatted --> VSCode
```

SQL Formatter は T-SQL を ScriptDOM で抽象構文木にパースし、ユーザーが設定したフォーマットオプションに基づいてスクリプトを再生成します。テキスト置換ベースではなく構文解析ベースのため、構文的に正確な整形が行われます。

## サービスアップデートの詳細

### 主要機能

1. **オンデマンドフォーマット**
   - ドキュメント全体 (Format Document) または選択範囲のみ (Format Selection) をフォーマット可能
   - 実行方法: 右クリックのコンテキストメニュー、コマンドパレット、キーボードショートカット (Format Document: Windows/Linux は Shift+Alt+F、macOS は Shift+Option+F / Format Selection: Windows/Linux は Ctrl+K, Ctrl+F、macOS は Cmd+K, Cmd+F)

2. **保存時の自動フォーマット (Format on Save)**
   - VS Code 標準の `editor.formatOnSave` 設定を SQL 言語スコープ (`"[sql]"`) に適用することで、保存のたびに自動整形

3. **豊富なカスタマイズオプション (`mssql.format.*`)**
   - 整列 (Alignment)、大文字/小文字 (Casing)、カンマ位置、改行、インデント、複数行リスト化、ステートメント間の空行数、スペーシングなど 50 以上の設定項目
   - 設定 UI (Mssql > Format) または `settings.json` で構成可能

4. **ScriptDOM ベースの構文解析**
   - オープンソースの .NET ライブラリ ScriptDOM により T-SQL をパースし、AST からスクリプトを生成
   - パースできない T-SQL がある場合は通知を表示 (`mssql.format.showParseErrorNotification`、既定で有効)

## 技術仕様

| 項目 | 詳細 |
|------|------|
| 提供形態 | MSSQL extension for Visual Studio Code の組み込み機能 |
| 対象データベース | Azure SQL Database、Azure SQL Managed Instance、SQL Server on Azure VM、SQL database in Microsoft Fabric、SQL Server |
| フォーマットエンジン | ScriptDOM (オープンソース .NET ライブラリ、AST ベース) |
| T-SQL バージョン | `mssql.format.options.sqlVersion` で指定 (既定: `sql170`) |
| エンジンタイプ | `mssql.format.options.sqlEngineType` で指定 (`all` / `standalone` / `sqlAzure`、既定: `all`) |
| 対応 OS (拡張機能) | Windows 10/11 (x64, Arm64)、macOS (Intel, Apple Silicon)、Linux (x64, Arm64) |

### 代表的なフォーマット設定

| 設定 | 既定値 | 説明 |
|------|--------|------|
| `mssql.format.options.keywordCasing` | `uppercase` | キーワードの大文字/小文字スタイル (`uppercase` / `lowercase` / `pascalCase`) |
| `mssql.format.options.identifierCasing` | `preserve` | オブジェクト識別子の大文字/小文字スタイル |
| `mssql.format.options.builtInFunctionCasing` | `preserve` | 組み込み関数名 (`GETDATE`、`COALESCE` など) のスタイル |
| `mssql.format.options.identifierBracketing` | `preserve` | 識別子の角かっこ `[]` を保持/追加/削除 |
| `mssql.format.options.commaPlacement` | `trailing` | カンマを行末 (`trailing`) か行頭 (`leading`) に配置 |
| `mssql.format.options.columnAliasStyle` | `asKeyword` | 列エイリアスを `AS` / 等号 / 元の構文で表記 |
| `mssql.format.options.alignClauseBodies` | `true` | `FROM`、`WHERE`、`GROUP BY` などの句の本体を整列 |
| `mssql.format.options.multilineSelectElementsList` | `true` | `SELECT` の列リストを複数行で整形 |
| `mssql.format.options.newLineBeforeWhereClause` | `true` | `WHERE` 句の前に改行を挿入 |
| `mssql.format.options.preserveComments` | `true` | フォーマット時にコメントを保持 |
| `mssql.format.options.numNewlinesAfterStatement` | `1` | 各ステートメント後の改行数 (0〜5) |

## 設定方法

### 前提条件

1. Visual Studio Code がインストールされていること
2. MSSQL extension for Visual Studio Code (`ms-mssql.mssql`) がインストールされていること (拡張機能ビューで `mssql` を検索してインストール)

### VS Code settings.json での構成

```json
{
  "[sql]": {
    "editor.defaultFormatter": "ms-mssql.mssql",
    "editor.formatOnSave": true
  },
  "mssql.format.options.keywordCasing": "lowercase",
  "mssql.format.options.alignClauseBodies": false,
  "mssql.format.options.numNewlinesAfterStatement": 2
}
```

- 既定のフォーマッターに設定するには、コマンドの **Configure Default Formatter...** から **SQL Server (mssql)** を選択するか、上記のように `editor.defaultFormatter` を指定します
- フォーマットオプションは設定 UI で **Mssql > Format** を検索して構成することもできます

### フォーマットの実行

1. T-SQL ファイルをエディターで開く
2. 右クリック → **Format Document** (全体) または **Format Selection** (選択範囲)、あるいはキーボードショートカット (Shift+Alt+F など) を実行

## メリット

### ビジネス面

- SQL コードのスタイルがチーム全体で統一され、コードレビューの効率と保守性が向上する
- 追加のサードパーティツールを導入せずに、標準の開発環境 (VS Code) 内で SQL の品質を担保できる
- ワークスペース単位の `settings.json` でプロジェクトごとのフォーマット規約を共有・強制できる

### 技術面

- ScriptDOM による AST ベースの整形のため、構文的に正確なフォーマットが得られる
- format on save により整形作業が自動化され、手作業での整形が不要になる
- 50 以上の設定項目で、キーワードの大文字/小文字からカンマ位置・改行ルールまで細かくスタイルを制御できる
- 選択範囲のみのフォーマットに対応し、大きな既存スクリプトへの段階的な適用が可能

## デメリット・制約事項

- フォーマッターが T-SQL を完全にパースできない場合があり、その際は通知が表示される (`mssql.format.showParseErrorNotification` で制御)
- `mssql.format.options.leadingCommaSpaceCount` は `0` または `1` のみ、改行数系の設定は 0〜5 の範囲のみなど、一部オプションには値の範囲制限がある
- format on save は MSSQL 拡張機能固有の設定ではなく VS Code 標準の `editor.formatOnSave` に依存するため、SQL 言語スコープでの設定が必要

## ユースケース

### ユースケース 1: チーム開発での SQL コーディング規約の統一

**シナリオ**: 複数の開発者が Azure SQL Database 向けのストアドプロシージャやマイグレーションスクリプトを共同開発しており、キーワードの大文字/小文字やカンマ位置がバラバラでレビューに時間がかかっている。

**実装例**: リポジトリの `.vscode/settings.json` にフォーマット規約をコミットして共有する。

```json
{
  "[sql]": {
    "editor.defaultFormatter": "ms-mssql.mssql",
    "editor.formatOnSave": true
  },
  "mssql.format.options.keywordCasing": "uppercase",
  "mssql.format.options.commaPlacement": "leading",
  "mssql.format.options.identifierBracketing": "includeBrackets"
}
```

**効果**: 保存のたびに全員のコードが同一スタイルに自動整形され、スタイル指摘のないコードレビューが実現し、差分も本質的な変更のみになる。

### ユースケース 2: 既存のレガシー SQL スクリプトの段階的な整形

**シナリオ**: 長年メンテナンスされてきた大規模な T-SQL スクリプトの可読性が低く、修正のたびに読み解きに時間がかかっている。

**実装例**: 修正対象の範囲を選択し **Format Selection** (Ctrl+K, Ctrl+F) を実行して、触った箇所のみを整形する。全体を一括整形する場合は **Format Document** (Shift+Alt+F) を使用する。

**効果**: 差分を最小限に抑えながら段階的にコードベースの可読性を改善でき、AST ベースの整形により構文を壊すリスクなく整形できる。

## 関連サービス・機能

- **Azure SQL Database / Azure SQL Managed Instance / SQL Server on Azure VM**: MSSQL 拡張機能が接続・開発をサポートする対象データベース。SQL Formatter はこれらに対する開発スクリプトの整形に利用できる
- **SQL database in Microsoft Fabric**: MSSQL 拡張機能のサポート対象。Fabric ワークスペースの参照や SQL データベースのプロビジョニングにも対応
- **GitHub Copilot integration (MSSQL 拡張機能)**: 自然言語チャットやエージェントモードによる AI 支援 SQL 開発。生成されたコードの整形に SQL Formatter を組み合わせられる
- **ScriptDOM**: SQL Formatter の基盤となるオープンソースの T-SQL パーサー/スクリプト生成ライブラリ
- **SQL notebooks / Schema designer / Schema compare (MSSQL 拡張機能)**: 同拡張機能で GA 済みの開発支援機能群。VS Code を中心とした SQL 開発ワークフローを構成する

## 参考リンク

- [インフォグラフィック](https://takech9203.github.io/azure-news-summary/20260929-sql-formatter-vscode.html)
- [公式アップデート情報](https://azure.microsoft.com/updates?id=571872)
- [Format T-SQL in the MSSQL Extension for Visual Studio Code (Microsoft Learn)](https://learn.microsoft.com/sql/tools/visual-studio-code-extensions/mssql/mssql-sql-formatter)
- [MSSQL extension for Visual Studio Code の概要 (Microsoft Learn)](https://learn.microsoft.com/sql/tools/visual-studio-code-extensions/mssql/mssql-extension-visual-studio-code)
- [MSSQL 拡張機能 (Visual Studio Marketplace)](https://marketplace.visualstudio.com/items?itemName=ms-mssql.mssql)
- [ScriptDOM (GitHub)](https://github.com/microsoft/sqlscriptdom)

## まとめ

VS Code の MSSQL 拡張機能に組み込まれた SQL Formatter が GA となり、Azure SQL Database をはじめとする SQL 系データベースの開発において、エディター内で T-SQL の整形が完結するようになりました。ScriptDOM ベースの構文解析による正確なフォーマット、format on save による自動化、50 以上の設定項目によるスタイルのカスタマイズが特長です。VS Code で SQL 開発を行うチームは、ワークスペースの `settings.json` にフォーマット規約を定義して共有することを推奨します。これにより、コーディングスタイルの統一とレビュー効率の向上が期待できます。

---

**タグ**: Azure SQL Database, MSSQL Extension, Visual Studio Code, SQL Formatter, T-SQL, ScriptDOM, Developer Tools, GA
