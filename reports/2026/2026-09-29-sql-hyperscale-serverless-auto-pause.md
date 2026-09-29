# Azure SQL Database: Hyperscale Serverless の自動一時停止・自動再開 (Public Preview)

**リリース日**: 2026-09-29

**サービス**: Azure SQL Database

**機能**: Hyperscale Serverless auto-pause and auto-resume

**ステータス**: In preview

[このアップデートのインフォグラフィックを見る](https://takech9203.github.io/azure-news-summary/20260929-sql-hyperscale-serverless-auto-pause.html)

## 概要

Azure SQL Database Hyperscale サービスレベルの Serverless コンピュートレベルにおいて、自動一時停止 (auto-pause) と自動再開 (auto-resume) がパブリックプレビューとして利用可能になりました。非アクティブな期間が続くとデータベースを自動的に一時停止し、アクティビティが戻ると自動的に再開するように構成できます。

Serverless コンピュートレベルは、ワークロードの需要に応じてコンピュートを自動スケーリングし、秒単位で使用したコンピュート量に対して課金されるモデルです。これまで General Purpose サービスレベルでは自動一時停止・自動再開が利用可能でしたが、今回のアップデートにより Hyperscale サービスレベルでも (プレビューとして) 同じ機能が使えるようになり、Hyperscale の大規模・高速なストレージアーキテクチャと Serverless のコスト最適化を組み合わせられるようになりました。

**アップデート前の課題**

- Hyperscale Serverless では自動一時停止がサポートされておらず、非アクティブな期間でも最小 vCore 分のコンピュート課金が継続していた
- 断続的・予測不能な利用パターンのデータベースで Hyperscale のスケーラビリティを活かしつつコンピュートコストをゼロにする手段がなかった

**アップデート後の改善**

- 非アクティブな期間 (セッション数 0 かつユーザーワークロードの CPU 使用 0) が自動一時停止遅延時間続くと、データベースが自動的に一時停止される
- 一時停止中はコンピュートコストがゼロになり、ストレージコストのみ課金される
- ログイン試行などのアクティビティが発生すると自動的に再開される (再開は通常 1 分程度)

## アーキテクチャ図

```mermaid
flowchart TD
    User([👤 アプリケーション / ユーザー])
    DB[("🗄️ Hyperscale Serverless DB<br/>(稼働中: 秒単位課金)")]
    Check{"⏱️ 非アクティブ判定<br/>セッション数 = 0<br/>ユーザー CPU = 0"}
    Paused[("😴 一時停止状態<br/>コンピュート課金なし<br/>ストレージのみ課金")]
    Login["🔑 ログイン試行 /<br/>管理操作イベント"]
    Retry["🔁 リトライロジック<br/>(エラー 40613 後に再接続)"]

    User -->|クエリ実行| DB
    DB -->|自動一時停止遅延<br/>(最小 60 分) 経過| Check
    Check -->|条件成立| Paused
    Check -->|アクティビティあり| DB
    Login -->|自動再開<br/>(約 1 分)| Paused
    Paused -.->|再開完了| DB
    User --> Retry
    Retry --> Login
```

非アクティブ条件が自動一時停止遅延時間 (Hyperscale では最小 60 分) 継続するとデータベースが一時停止し、コンピュート課金が停止します。ログインなどのアクティビティで自動再開され、初回接続はエラー 40613 を返すためアプリケーション側のリトライロジックが重要です。

## サービスアップデートの詳細

### 主要機能

1. **自動一時停止 (auto-pause)**
   - 自動一時停止遅延時間の間、「セッション数 = 0」かつ「ユーザーリソースプールの CPU = 0」が継続すると自動的に一時停止
   - Hyperscale の自動一時停止遅延は既定 60 分、最小 60 分、最大 10,080 分 (7 日)、1 分単位で設定可能 (General Purpose の最小は 15 分)
   - `-1` を設定することで自動一時停止を無効化可能
   - 一時停止までのレイテンシは条件成立後 1〜10 分程度

2. **自動再開 (auto-resume)**
   - ログイン試行のほか、監査ログの参照、脅威検出設定の変更、データベースコピー、タグの追加・変更、vCore や自動一時停止遅延の変更など、さまざまな操作がトリガーとなる
   - 再開のレイテンシは通常 1 分程度
   - Azure Monitor アクティビティログの「Resume Databases」操作の `Caller` プロパティで再開トリガーを特定可能

3. **一時停止中のコスト削減**
   - 一時停止中はコンピュートコストがゼロとなり、ストレージコストのみ発生

## 技術仕様

| 項目 | 詳細 |
|------|------|
| 対象サービスレベル | Hyperscale (プレビュー)。General Purpose では従来から利用可能 |
| 購入モデル | vCore モデルのみ (DTU モデルは非対応) |
| ハードウェア | Standard シリーズ (Gen5) |
| 自動一時停止遅延 (Hyperscale) | 既定 60 分 / 最小 60 分 / 最大 10,080 分 (7 日) / 1 分単位 / `-1` で無効化 |
| 一時停止の条件 | セッション数 = 0 かつ ユーザーリソースプールの CPU = 0 が遅延時間継続 |
| 再開レイテンシ | 通常約 1 分 |
| 一時停止レイテンシ | 条件成立後 1〜10 分程度 |
| 一時停止中の課金 | コンピュート課金なし、ストレージのみ |
| 課金粒度 (稼働中) | 秒単位 |

## 設定方法

### 前提条件

1. Azure SQL Database Hyperscale サービスレベル、Serverless コンピュートモデル、Standard シリーズ (Gen5) ハードウェアのデータベース
2. geo レプリケーション、長期バックアップ保有 (LTR)、論理サーバーの DNS エイリアスなど、自動一時停止を妨げる機能を使用していないこと

### Azure CLI

```bash
# 新規に Hyperscale Serverless データベースを作成 (自動一時停止遅延 60 分)
az sql db create -g $resourceGroupName \
  -s $serverName \
  -n $databaseName \
  -e Hyperscale \
  --compute-model Serverless \
  -f Gen5 \
  --min-capacity 0.5 \
  -c 2 \
  --auto-pause-delay 60

# 既存の Serverless データベースの自動一時停止遅延を変更
az sql db update -g $resourceGroupName \
  -s $serverName \
  -n $databaseName \
  --auto-pause-delay 1440
```

### PowerShell

```powershell
# 新規に Hyperscale Serverless データベースを作成
$params = @{
    ResourceGroupName = $resourceGroupName
    ServerName = $serverName
    DatabaseName = $databaseName
    Edition = 'Hyperscale'
    ComputeModel = 'Serverless'
    ComputeGeneration = 'Gen5'
    MinVcore = 0.5
    MaxVcore = 2
    AutoPauseDelayInMinutes = 60
}
New-AzSqlDatabase @params
```

### Transact-SQL

```sql
-- T-SQL では既定値 (最小 vCore、自動一時停止遅延) が適用される
CREATE DATABASE testdb
( EDITION = 'Hyperscale', SERVICE_OBJECTIVE = 'HS_S_Gen5_2' );
```

## メリット

### ビジネス面

- 開発・テスト環境や利用が断続的なデータベースで、非アクティブ期間中のコンピュートコストをゼロにでき、TCO を削減できる
- Hyperscale の大規模ストレージ・高速スケーリングを、利用パターンが予測できないワークロードにもコスト効率よく適用できる

### 技術面

- 一時停止・再開が完全に自動化され、手動でのスケール操作やスケジュール化されたスクリプトが不要になる
- 秒単位課金と自動スケーリング (最小/最大 vCore 設定) の組み合わせで、需要変動に自動追従する
- Azure Monitor アクティビティログで再開トリガーを特定でき、意図しない再開の調査が可能

## デメリット・制約事項

- **プレビュー機能**である (General Purpose では GA 済みだが、Hyperscale ではプレビュー)
- 現在のプレビューでは、**named replica は自動一時停止・自動再開と併用できない**
- Hyperscale の最小自動一時停止遅延は **60 分** (General Purpose の 15 分より長い)。自動一時停止遅延を 60 分未満に設定した General Purpose Serverless データベースを Hyperscale にアップグレードすると、アップグレード後に自動一時停止が無効化されるため、手動で再有効化が必要
- 以下の機能を使用している場合、自動一時停止は行われない (自動スケーリングは利用可能):
  - geo レプリケーション (アクティブ geo レプリケーション、フェールオーバーグループ)
  - 長期バックアップ保有 (LTR)
  - 論理サーバーに作成された DNS エイリアス
  - SQL Data Sync の同期データベース (ハブ・メンバーデータベースは一時停止可能)
  - Elastic Jobs のジョブデータベース (ジョブのターゲットとしては一時停止可能)
- 一時停止中のデータベースへの初回接続はエラーコード **40613** を返すため、アプリケーションにリトライロジックが必須
- 開いたままのセッションが存在すると (CPU 使用がなくても) 自動一時停止が行われない。監視ツール等の常時接続に注意
- カスタマーマネージドキー (BYOK) の TDE を使用している場合、キーのローテーションのたびにデータベースが自動再開される

## ユースケース

### ユースケース 1: 開発・テスト環境の Hyperscale データベースのコスト最適化

**シナリオ**: 本番と同じ Hyperscale サービスレベルで開発・テスト環境を運用しているが、夜間・週末はほぼ利用がなく、コンピュートコストが無駄になっている。

**実装例**:

```bash
# 自動一時停止遅延 60 分の Hyperscale Serverless に変換
az sql db update -g rg-dev \
  -s sql-dev-server \
  -n devdb \
  --edition Hyperscale \
  --compute-model Serverless \
  --family Gen5 \
  --min-capacity 0.5 \
  --capacity 4 \
  --auto-pause-delay 60
```

**効果**: 非アクティブ期間中のコンピュート課金がゼロになり、ストレージコストのみで環境を維持できる。

### ユースケース 2: 利用が断続的な大規模データベース

**シナリオ**: データサイズが大きく Hyperscale が必要だが、アクセスが月次バッチや不定期な分析に限られるデータベース。

**効果**: Hyperscale のストレージスケーラビリティを維持しつつ、アクセスがない期間はコンピュートコストを発生させない。再開は通常 1 分程度のため、リトライロジックを備えたバッチ処理であれば運用への影響は限定的。

## 料金

Serverless データベースのコストはコンピュートコストとストレージコストの合計です。

| 状態 | コンピュート課金 |
|------|------|
| 稼働中 (最小〜最大 vCore の範囲内) | 使用した vCore とメモリに基づき秒単位で課金 |
| 稼働中 (使用量が最小構成未満) | 構成した最小 vCore・最小メモリに基づき課金 |
| **一時停止中** | **課金なし (ストレージコストのみ発生)** |

詳細な料金は [Azure SQL Database 料金ページ](https://azure.microsoft.com/pricing/details/azure-sql-database/single/) および [Serverless compute tier billing](https://learn.microsoft.com/azure/azure-sql/database/serverless-tier-billing) を参照してください。

## 利用可能リージョン

リージョン別の提供状況は [Serverless availability by region](https://learn.microsoft.com/azure/azure-sql/database/region-availability#serverless-region-availability) を参照してください。

## 関連サービス・機能

- **Azure SQL Database Hyperscale**: 最大 128 TB のストレージと高速スケーリングを提供するサービスレベル。今回のアップデートの対象
- **Serverless コンピュートレベル (General Purpose)**: 自動一時停止・自動再開が GA 済み。最小自動一時停止遅延は 15 分
- **Azure Monitor アクティビティログ**: 「Resume Databases」操作の `Caller` プロパティで自動再開のトリガーを特定可能
- **Elastic Pool**: 複数データベースの断続的なワークロードを統合する場合の代替アプローチ (プロビジョニング済みコンピュート)

## 参考リンク

- [インフォグラフィック](https://takech9203.github.io/azure-news-summary/20260929-sql-hyperscale-serverless-auto-pause.html)
- [公式アップデート情報](https://azure.microsoft.com/updates?id=571857)
- [Serverless compute tier - Azure SQL Database](https://learn.microsoft.com/azure/azure-sql/database/serverless-tier-overview)
- [Auto-pause and auto-resume in the serverless compute tier](https://learn.microsoft.com/azure/azure-sql/database/serverless-tier-auto-pause-resume)
- [Create and configure a serverless database](https://learn.microsoft.com/azure/azure-sql/database/serverless-tier-create-configure)
- [料金ページ](https://azure.microsoft.com/pricing/details/azure-sql-database/single/)

## まとめ

Hyperscale Serverless の自動一時停止・自動再開のパブリックプレビューにより、Hyperscale のスケーラビリティと Serverless のコスト効率を両立できるようになりました。一時停止中はコンピュート課金がゼロになるため、開発・テスト環境や利用が断続的な大規模データベースのコスト削減に有効です。導入時は、最小自動一時停止遅延が 60 分であること、named replica や geo レプリケーション・LTR との併用制限、エラー 40613 に対するアプリケーションのリトライロジック整備を確認してください。

---

**タグ**: Azure SQL Database, Hyperscale, Serverless, Auto-pause, Auto-resume, Public Preview, Databases, コスト最適化
