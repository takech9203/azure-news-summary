---
name: azure-news-summary
description: Microsoft Azure の Release Notes と Blog の情報を取得し、日本語で詳細な解説レポートを作成するスキル。ユーザーが「Azure 新機能」「Azure アップデート」「Azure ニュース」「最新の Azure 情報」などと言った場合に使用する。特定の Azure サービスの最新情報や、期間を指定したアップデートの調査にも対応。
---

# Azure News Reporter Skill <!-- omit in toc -->

## 目次

- [目次](#目次)
- [情報ソース](#情報ソース)
- [ワークフロー](#ワークフロー)
  - [0. 現在時刻の確認](#0-現在時刻の確認)
  - [1. Azure Updates から最新情報を取得](#1-azure-updates-から最新情報を取得)
  - [2. 期間フィルタリング (デフォルト: 過去 3 日間)](#2-期間フィルタリング-デフォルト-過去-3-日間)
  - [3. 除外フィルタリング](#3-除外フィルタリング)
  - [4. 重複チェック](#4-重複チェック)
  - [5. アップデートごとの情報収集とレポート作成](#5-アップデートごとの情報収集とレポート作成)
    - [5.1. Azure Updates ページの詳細](#51-azure-updates-ページの詳細)
    - [5.2. Microsoft Learn ドキュメント検索](#52-microsoft-learn-ドキュメント検索)
    - [5.3. 料金情報の取得](#53-料金情報の取得)
    - [5.4. Before/After コンテキストの収集](#54-beforeafter-コンテキストの収集)
    - [5.5. 関連サービス・機能の調査](#55-関連サービス機能の調査)
    - [5.6. 情報収集の優先順位](#56-情報収集の優先順位)
    - [5.7. レポート作成](#57-レポート作成)
    - [5.8. アーキテクチャ図の作成](#58-アーキテクチャ図の作成)
  - [6. Azure Blog リンクの取得 (可能な場合)](#6-azure-blog-リンクの取得-可能な場合)
- [出力形式](#出力形式)
- [実行例](#実行例)
- [除外サービス](#除外サービス)
- [除外アップデートタイプ](#除外アップデートタイプ)
- [注意事項](#注意事項)

Microsoft Azure の Updates と Blog から最新情報を取得し、構造化されたレポートを作成する。

## 情報ソース

1. **Azure Updates**: https://azure.microsoft.com/updates/
   - 公式発表、新機能、サービスアップデートの RSS フィード
   - RSS Feed: https://www.microsoft.com/releasecommunications/api/v2/azure/rss
   - RSS 2.0 形式
   - タイトルにステータスプレフィックス: `[Launched]`, `[In preview]`, `[In development]`

2. **Azure Blog**: https://azure.microsoft.com/blog/
   - Updates と関連する詳細記事
   - RSS Feed: https://azure.microsoft.com/en-us/blog/feed/
   - RSS 2.0 形式

3. **Microsoft Learn**:
   - WebFetch でドキュメント検索
   - 詳細情報の補完、技術仕様、設定手順、制限事項の確認に活用

4. **cloud-cost MCP サーバー** (利用可能な場合):
   - Azure インスタンスタイプ、リージョンの料金データ
   - コンピュート、ストレージ、Egress、Kubernetes の料金比較

## ワークフロー

### 0. 現在時刻の確認

**重要**: 作業を開始する前に、必ず現在時刻を確認する。

```bash
date "+%Y-%m-%d %H:%M:%S %Z"
```

これにより、ユーザーが指定した期間 (例: 「2026 年 3 月」「過去 1 週間」) が現在の日付から見て適切かどうかを判断できる。

### 1. Azure Updates から最新情報を取得

**重要**: RSS フィードは **1 回だけ** 取得する。複数回リクエストしない。

**取得方法**: Bash ツールで curl と外部スクリプトを使用する

```bash
# RSS フィードを取得して一時ファイルに保存
curl -L -s "https://www.microsoft.com/releasecommunications/api/v2/azure/rss" > /tmp/azure_updates.xml

# パーサースクリプトで JSON に変換 (過去 7 日間)
python3 .claude/skills/azure-news-summary/scripts/parse_azure_updates.py --days 7 --feed /tmp/azure_updates.xml
```

**パーサースクリプトのオプション:**
- `--days DAYS`: 取得する期間 (デフォルト: 7)
- `--feed PATH`: RSS フィードファイルのパス (デフォルト: /tmp/azure_updates.xml)

**期間指定の例:**
```bash
# 過去 14 日間のアイテムを取得
python3 .claude/skills/azure-news-summary/scripts/parse_azure_updates.py --days 14
```

**Azure Updates RSS の特徴:**
- RSS 2.0 形式 (GCP の Atom とは異なる)
- `<item>`: 各アナウンスメント
- `<title>`: タイトル (ステータスプレフィックス付き: `[Launched]`, `[In preview]`, `[In development]`)
- `<description>`: 説明
- `<pubDate>`: 公開日時 (RFC 2822 形式: "Mon, 01 Mar 2026 00:00:00 GMT")
- `<link>`: 詳細ページ URL
- `<category>`: カテゴリ (複数可: Compute, Storage, Networking など)
- `<a10:updated>`: 更新日時 (ISO 8601 形式)

### 2. 期間フィルタリング (デフォルト: 過去 3 日間)

RSS フィードをパースする際に、指定期間内のアイテムを抽出:
- デフォルト: 過去 3 日間 (`--days 3`) - 毎日実行を想定
- ユーザー指定: 「過去 1 週間」→ `--days 7`、「過去 2 週間」→ `--days 14` など
- パーサースクリプトの `--days` オプションで期間を変更

### 3. 除外フィルタリング

取得したアイテムから、除外対象を除いたアップデートについてレポートを作成する。
除外対象は「除外サービス」および「除外アップデートタイプ」セクションを参照。

**重要: 除外ルールに該当しない限り、すべてのアップデートを対象とする。**

マイナーなアップデートであっても、Solutions Architect として知っておくべき情報であれば含める。判断に迷った場合は対象とする。除外して後から「知らなかった」となるリスクより、網羅的にカバーする方が価値がある。

**ステータス別の優先度:**
- `Launched` (GA): 高 - 詳細レポート作成
- `In preview`: 中 - 標準レポート作成
- `In development`: 低 - 簡易レポートまたはスキップ

### 4. 重複チェック

レポート作成前にプロジェクトルートの `reports/{YYYY}/` ディレクトリを確認:

```
# 既存レポートのファイル名を確認 (年別フォルダ)
# 例: Glob(pattern="reports/2026/*.md")
Glob(pattern="reports/{publishedの年}/*.md")
```

ファイル名形式: `{YYYY}-{MM}-{DD}-{slug}.md`
- 同じ日付・同じ slug のレポートが存在する場合はスキップ

**slug の生成ルール:**
- アップデートの対象サービス名と機能名から生成する
- サービス名と機能名を小文字のケバブケースに変換する
- 例: "Azure App Service - Node.js 22 Support" → `app-service-nodejs-22`
- 例: "Azure Kubernetes Service - TPU Support" → `aks-tpu-support`
- 例: "Azure SQL Database - Hyperscale Tier" → `sql-database-hyperscale`
- slug は英語で生成し、日本語は含めない
- 長すぎる場合は主要なキーワードに絞る (最大 60 文字程度)

### 5. アップデートごとの情報収集とレポート作成

**重要: アップデートごとに「情報収集 → レポート作成」を繰り返す。**

全アップデートの情報を一括で収集してからレポートを書くのではなく、1 つのアップデートについて情報を集め、レポートを書き、次のアップデートに移る。これによりコンテキストの肥大化を防ぎ、各レポートの品質を維持する。

**Subagent モード (CI/CD 実行時)**

`run.py` から実行される場合、オーケストレーターがステップ 1〜4 (RSS 取得、フィルタリング、重複チェック) を実行し、個別レポート作成を `report-generator` subagent に委譲する。subagent は Task ツール経由で並列実行される。

#### 5.1. Azure Updates ページの詳細

WebFetch で詳細ページを取得する。

```
WebFetch(url="https://azure.microsoft.com/updates/...", prompt="アップデートの詳細情報を抽出")
```

#### 5.2. Microsoft Learn ドキュメント検索

WebFetch で Microsoft Learn のドキュメントを検索・取得する。

**検索対象:**
- サービスの概要ドキュメント (機能の詳細、技術仕様)
- 設定・構成ガイド (前提条件、手順)
- 制限事項・クォータ (制約、上限値)
- ベストプラクティス

**検索例:**
```
WebFetch(url="https://learn.microsoft.com/azure/app-service/", prompt="App Service の概要と機能")
WebFetch(url="https://learn.microsoft.com/azure/aks/", prompt="AKS の設定手順と制限事項")
```

#### 5.3. 料金情報の取得

サービスの料金情報を取得する。

**方法 1: cloud-cost MCP サーバー (利用可能な場合)**

```
# Azure インスタンスの料金比較
compare_compute(provider="azure", vcpus=4, memory_gb=16)

# ストレージ料金の比較
compare_storage(provider="azure", storage_type="object", size_gb=1000)

# Kubernetes (AKS) の料金
compare_kubernetes()
```

**方法 2: WebFetch で料金ページを取得**

```
WebFetch(url="https://azure.microsoft.com/pricing/details/app-service/", prompt="料金体系の概要")
```

**レポートへの反映:**
- 料金体系の概要を記載
- 代表的な使用量での月額料金を表形式で記載
- 無料枠がある場合は明記
- 料金ページの URL を参考リンクに含める

#### 5.4. Before/After コンテキストの収集

アップデート前の課題とアップデート後の改善を明確にするため、以下の情報を収集する。

**収集方法:**
- Azure Updates の記述から「以前は〇〇だった」「新たに〇〇が可能になった」を抽出
- Microsoft Learn で既存機能のドキュメントを検索し、従来の制限事項を確認
- GA の場合: Preview 時点からの変更点を確認

**記載のポイント:**
- 具体的な課題を記述 (「手動で〇〇する必要があった」「〇〇に対応していなかった」)
- 改善内容を対応させて記述 (「〇〇が自動化された」「〇〇に対応した」)
- 推測ではなく、ドキュメントや Updates から確認できた情報のみ記載

#### 5.5. 関連サービス・機能の調査

アップデートに関連する Azure サービスや機能を調査する。

**調査方法:**
```
WebFetch(url="https://learn.microsoft.com/azure/...", prompt="関連サービスと連携機能")
```

**記載のポイント:**
- 直接連携するサービス (例: Azure Monitor、Log Analytics)
- 代替・補完するサービス
- 組み合わせて使うことが多いサービス

#### 5.6. 情報収集の優先順位

すべての情報が取得できるとは限らない。以下の優先順位で情報を収集し、取得できた情報でレポートを作成する。

1. **必須**: Azure Updates の詳細 (5.1)、概要、主要機能
2. **重要**: Microsoft Learn ドキュメント (5.2)、Before/After (5.4)
3. **推奨**: 料金情報 (5.3)、関連サービス (5.5)
4. **任意**: 設定手順の詳細、ユースケースの実装例

**テンプレートセクションの扱い:**
- 情報が取得できなかったセクションは、無理に埋めずに削除する
- 推測で埋めない。確認できた情報のみ記載する
- 「料金」「利用可能リージョン」は公式情報が確認できない場合、料金ページ・ドキュメントへのリンクのみ記載する

#### 5.7. レポート作成

情報収集が完了したら、そのアップデートのレポートを作成する。

`.claude/skills/azure-news-summary/report_template.md` のテンプレートを使用する。

**重要: 1 アップデート = 1 レポートファイル**

RSS フィードから取得した各アイテムについて、サービスや機能ごとに個別のレポートファイルを作成する。1 つのレポートに複数のアップデートをまとめない。

**例**: 3 月 1 日に App Service、AKS、SQL Database のアップデートがあった場合:
- `reports/2026/2026-03-01-app-service-nodejs-22.md`
- `reports/2026/2026-03-01-aks-tpu-support.md`
- `reports/2026/2026-03-01-sql-database-hyperscale.md`

**ただし、同一サービスの関連する小さなアップデートはまとめてよい。**

**インフォグラフィック URL の決定:**

レポート内のインフォグラフィックリンク URL は、環境変数 `INFOGRAPHIC_BASE_URL` から取得する。

```bash
echo "$INFOGRAPHIC_BASE_URL"
```

テンプレート内の `{INFOGRAPHIC_URL}` プレースホルダーは、`{INFOGRAPHIC_BASE_URL}/{YYYYMMDD}-{slug}.html` の形式で置換する。

**出力先**: `reports/{YYYY}/{YYYY}-{MM}-{DD}-{slug}.md` (プロジェクトルートからの相対パス)

#### 5.8. アーキテクチャ図の作成

**原則として必ず含める。** アップデート内容に応じて適切な図の種類を選択し、Mermaid でアーキテクチャ図やシーケンス図を作成する。

**配置場所**: レポートテンプレートの「## アーキテクチャ図」セクション (概要セクションの直後)

**削除してよいケース (これ以外は必ず図を含める):**
- UI のみの変更
- ドキュメント更新のみ
- 単純なパラメータ追加など、図で表現する意味がない場合

**アップデートタイプ → 推奨する図の種類:**

| アップデートタイプ | 推奨する図 | 例 |
|-------------------|-----------|-----|
| 新サービス・新機能 | `flowchart TD` | サービス構成、コンポーネント関係 |
| サービス連携・インテグレーション | `flowchart LR` | データフロー、サービス間連携 |
| API の追加・変更 | `sequenceDiagram` | API 呼び出しフロー、処理シーケンス |
| 機能改善・GA 昇格 | `flowchart TD` (Before/After) | 改善前後の比較 |
| セキュリティ・ネットワーク | `flowchart TD` | セキュリティ境界、ネットワーク構成 |
| データ処理・パイプライン | `flowchart LR` | データの流れ、処理ステップ |

**Mermaid 図の作成ルール:**
- 適切な絵文字を使用してコンポーネントの種類を視覚的に示す
- シンプルで見やすい図を心がける (ノード数は 10 個以内を目安)
- 図には簡潔な説明を 1-2 文添える
- Mermaid のシェイプセマンティクスを守る (ユーザーは stadium、DB は cylinder、判断は diamond など)

### 6. Azure Blog リンクの取得 (可能な場合)

アップデートに関連する Azure Blog 記事がある場合、参考リンクに含める。

**取得方法**: RSS フィード

```bash
# Azure Blog RSS フィードを取得
curl -L -s "https://azure.microsoft.com/en-us/blog/feed/" > /tmp/azure_blog.xml

# パーサースクリプトで JSON に変換 (過去 7 日間)
python3 .claude/skills/azure-news-summary/scripts/parse_azure_blog.py --days 7 --feed /tmp/azure_blog.xml
```

- published が近い記事を手動で確認
- Blog 記事が見つからない場合は省略可

## 出力形式

- 言語: 日本語
- フォーマット: Markdown
- 出力先: `reports/{YYYY}/` (プロジェクトルートからの相対パス)
- ファイル名: `{YYYY}-{MM}-{DD}-{slug}.md`
- **1 アップデート (またはサービス内の関連アップデート群) = 1 ファイル**

## 実行例

### 例 1: デフォルト実行 (過去 1 週間のアップデート)

ユーザー: 「Azure の最新ニュースをレポートして」

1. Azure Updates RSS フィード取得 (curl、1 回のみ)
2. 過去 7 日間のアイテムを抽出
3. 除外対象を除外
4. 既存レポートと重複チェック → 対象アップデートリスト確定
5. アップデートごとにループ:
   - 情報収集 (Updates 詳細、Microsoft Learn、料金情報)
   - レポート作成 + アーキテクチャ図
   - 次のアップデートへ
6. Blog リンクの補完 (必要に応じて)

### 例 2: 期間指定

ユーザー: 「過去 2 週間の Azure アップデートをまとめて」

1. Azure Updates RSS フィード取得 (curl、1 回のみ)
2. 過去 14 日間のアイテムを抽出 (`--days 14`)
3. 以降同様

### 例 3: サービス指定

ユーザー: 「Azure Kubernetes Service の最新アップデートを教えて」

1. Azure Updates RSS フィード取得 (curl、1 回のみ)
2. category に "Kubernetes" や "AKS" を含むアイテムを抽出
3. 以降同様

## 除外サービス

現時点では除外サービスは設定されていません。必要に応じて追加してください。

## 除外アップデートタイプ

以下のタイプのアップデートはレポート対象外とする:

- ドキュメント更新のみのアップデート
- 軽微な UI 変更のみのアップデート
- `[In development]` ステータスのアップデート (進捗報告のみで実質的な変更がない場合)

## 注意事項

- **RSS フィードは 1 回だけ取得する。複数回リクエストしない。**
- **RSS フィードの取得には Bash ツールで curl を使用する (WebFetch ツールは RSS には使用しない)**
- 取得できたアイテムで処理を続ける (全アイテムが取得できなくても問題なし)
- 最新情報を優先 (pubDate を確認)
- 公式ドキュメントを情報源として明記
- 推測は避け、確認できた情報のみ記載
- 重複レポートは作成しない (ファイル名で判定)
