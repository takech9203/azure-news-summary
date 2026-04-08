# Azure Database for PostgreSQL: PgBouncer 1.25.1 サポートの一般提供開始

**リリース日**: 2026-04-08

**サービス**: Azure Database for PostgreSQL - Flexible Server

**機能**: PgBouncer 1.25.1 support in Azure Database for PostgreSQL - Flexible Server

**ステータス**: Launched (GA)

[このアップデートのインフォグラフィックを見る](https://takech9203.github.io/azure-news-summary/20260408-postgresql-pgbouncer-1-25-1.html)

## 概要

Azure Database for PostgreSQL - Flexible Server において、組み込みのコネクションプーリング機能である PgBouncer のバージョンが 1.25.1 に更新され、一般提供（GA）が開始された。PgBouncer は、アイドル状態や短命な接続を効率的に管理することで、低オーバーヘッドで数千の接続にスケールすることを可能にする軽量なコネクションプーラーである。

PgBouncer はデータベースサーバーと同一の仮想マシン（VM）上で動作し、非同期 I/O を活用した軽量モデルにより、最大 10,000 接続まで低オーバーヘッドでスケーリングできる。PostgreSQL はプロセスベースのモデルを採用しているため、多数のアイドル接続を維持するとリソースコストが高くなるが、PgBouncer はトランザクション中またはクエリがアクティブなときにのみ PostgreSQL 接続を使用することで、この課題を解決する。

今回のアップデートにより、サポートされている全てのメジャーバージョンの PostgreSQL エンジンにおいて PgBouncer 1.25.1 がデプロイされる。引き続きポート 6432 で動作し、General Purpose および Memory Optimized コンピュートティアで利用可能である。

**アップデート前の課題**

- PostgreSQL のプロセスベースモデルにより、数千の同時接続を維持するとサーバーリソースが圧迫される
- アイドル状態の接続がリソースを消費し続け、アプリケーションのスケーラビリティが制限される
- 短命な接続の頻繁な作成・切断がパフォーマンスオーバーヘッドを生む
- トランザクションプーリングモードでプリペアドステートメントを使用する場合の制約があった

**アップデート後の改善**

- PgBouncer 1.25.1 への更新により、最新のセキュリティパッチと機能改善が適用される
- 組み込み機能として Azure によるマネージドアップデートが提供され、手動メンテナンスが不要
- `max_prepared_statements` パラメータによりトランザクションプーリングモードでのプリペアドステートメントサポートが利用可能
- Microsoft Entra 認証（Azure AD）との統合をサポート

## アーキテクチャ図

```mermaid
flowchart TD
    subgraph Client["クライアントアプリケーション"]
        App1["アプリケーション 1"]
        App2["アプリケーション 2"]
        AppN["アプリケーション N"]
    end

    subgraph Azure["Azure Cloud"]
        subgraph FlexServer["Azure Database for PostgreSQL - Flexible Server"]
            subgraph VM["同一 VM"]
                PgBouncer["PgBouncer 1.25.1<br/>ポート: 6432<br/>コネクションプーリング"]
                PostgreSQL["PostgreSQL エンジン<br/>ポート: 5432"]
            end
        end

        subgraph HA["高可用性構成"]
            Primary["プライマリサーバー<br/>+ PgBouncer"]
            Standby["スタンバイサーバー<br/>(フェイルオーバー時に<br/>PgBouncer 自動再起動)"]
        end

        EntraID["Microsoft Entra ID<br/>(認証)"]
    end

    App1 -->|"ポート 6432"| PgBouncer
    App2 -->|"ポート 6432"| PgBouncer
    AppN -->|"ポート 6432"| PgBouncer
    PgBouncer -->|"プール管理された接続"| PostgreSQL
    Primary -.->|"フェイルオーバー"| Standby
    EntraID -.->|"認証"| PgBouncer
```

PgBouncer はデータベースサーバーと同一 VM 上で動作し、クライアントからの接続をポート 6432 で受け付ける。内部的に PostgreSQL エンジン（ポート 5432）への接続をプーリングし、効率的にリソースを管理する。

## サービスアップデートの詳細

### 主要機能

1. **組み込みコネクションプーリング**
   - データベースサーバーと同一 VM 上で動作し、追加のインフラストラクチャが不要
   - General Purpose および Memory Optimized コンピュートティアでサポート
   - パブリックアクセスおよびプライベートアクセスネットワークの両方で利用可能

2. **3 つのプーリングモード**
   - **トランザクションプーリング**（デフォルト）: トランザクション単位で接続を割り当て、完了後にプールへ返却
   - **セッションプーリング**: クライアント接続の全期間にわたりサーバー接続を割り当て
   - **ステートメントプーリング**: 個々のステートメント単位で接続を管理

3. **プリペアドステートメントサポート**
   - `max_prepared_statements` パラメータを 0 より大きい値に設定することで、トランザクションモードでプロトコルレベルのプリペアドステートメントを有効化
   - libpq の `PQprepare` 関数を使用するプロトコルレベルのコマンドに対応

4. **高可用性対応**
   - ゾーン冗長高可用性（HA）構成において、フェイルオーバー時にスタンバイサーバー上で PgBouncer が自動的に再起動
   - アプリケーション接続文字列の変更は不要

5. **Microsoft Entra 認証サポート**
   - Azure AD（Microsoft Entra ID）による認証をサポート

6. **Elastic Cluster 対応**
   - Elastic Cluster の各ノードで PgBouncer インスタンスが利用可能
   - コーディネーターノードはポート 6432、ワーカーノードはポート 8432 でルーティング

## 技術仕様

| 項目 | 詳細 |
|------|------|
| PgBouncer バージョン | 1.25.1 |
| 動作ポート | 6432 |
| デフォルトプールモード | トランザクションプーリング |
| 最大クライアント接続数（デフォルト） | 5,000 |
| デフォルトプールサイズ | 50（ユーザー/データベースペアごと） |
| クエリ待機タイムアウト | 120 秒 |
| サーバーアイドルタイムアウト | 600 秒 |
| スケーリング上限 | 最大 10,000 接続（低オーバーヘッド） |
| 対応コンピュートティア | General Purpose、Memory Optimized |
| TLS/SSL | `require_secure_transport` が ON の場合に自動適用 |

## 設定方法

### 前提条件

1. Azure Database for PostgreSQL - Flexible Server インスタンスが作成済みであること
2. General Purpose または Memory Optimized コンピュートティアを使用していること

### Azure Portal

1. Azure Portal で対象の PostgreSQL Flexible Server のリソースページを開く
2. 左側メニューから「サーバーパラメーター」を選択
3. 検索ボックスで「PgBouncer」を検索
4. `pgbouncer.enabled` を `true` に変更（サーバー再起動は不要）
5. 必要に応じて以下のパラメータを調整:
   - `pgbouncer.default_pool_size`: プールサイズ（デフォルト: 50）
   - `pgbouncer.max_client_conn`: 最大クライアント接続数（デフォルト: 5000）
   - `pgbouncer.pool_mode`: プーリングモード（デフォルト: transaction）
   - `pgbouncer.max_prepared_statements`: プリペアドステートメントサポート（デフォルト: 0）
6. 「保存」をクリック

### 接続方法

```bash
# PgBouncer 経由で接続（ポート 6432 を使用）
psql "host=myPgServer.postgres.database.azure.com port=6432 dbname=postgres user=myUser password=<password> sslmode=require"
```

### PgBouncer 管理コンソール

```bash
# 1. pgbouncer.stats_users パラメータに既存ユーザーを設定
# 2. pgbouncer データベースに接続
psql "host=myPgServer.postgres.database.azure.com port=6432 dbname=pgbouncer user=myUser password=<password> sslmode=require"

# 利用可能な SHOW コマンド
# SHOW HELP;       -- 利用可能なコマンド一覧
# SHOW POOLS;      -- 各プールの接続状態
# SHOW DATABASES;  -- データベースごとの接続制限
# SHOW STATS;      -- リクエストとトラフィックの統計
```

## メリット

### ビジネス面

- 追加のインフラストラクチャコストが不要（VM やコンテナの別途費用なし）
- Azure マネージドサービスとして自動アップデートが提供され、運用負荷が軽減
- フェイルオーバー時のダウンタイム最小化により、サービスの可用性が向上

### 技術面

- 最大 10,000 接続まで低オーバーヘッドでスケーリング可能
- アイドル接続と短命接続の効率的な管理によるリソース使用量の削減
- サーバー再起動不要で有効化でき、設定変更も動的に反映
- Microsoft Entra 認証との統合によるセキュアな認証
- ゾーン冗長 HA 構成でのシームレスなフェイルオーバー対応

## デメリット・制約事項

- Burstable コンピュートティアではサポートされない（General Purpose または Memory Optimized から Burstable に変更すると PgBouncer 機能が失われる）
- スケール操作、HA フェイルオーバー、再起動時に PgBouncer も再起動されるため、既存の接続を再確立する必要がある
- シングルスレッドアーキテクチャのため、大量の短命接続を生成するアプリケーションではパフォーマンスに影響する可能性がある
- ステートメントプーリングモードではマルチステートメントトランザクションがサポートされない
- 組み込み PgBouncer は単一障害点となる可能性がある（PgBouncer プロセスが停止すると接続プール全体に影響）
- `pgbouncer.client_tls_sslmode` パラメータは非推奨（`require_secure_transport` サーバーパラメータで制御）
- PgBouncer メトリクスの DatabaseName ディメンションは 30 データベースまで（Burstable SKU では 10 データベースまで）

## ユースケース

### ユースケース 1: 高トラフィック Web アプリケーション

**シナリオ**: 多数のユーザーが同時アクセスする Web アプリケーションにおいて、各リクエストが短命なデータベース接続を生成するケース。

**実装例**:

```bash
# PgBouncer を有効化し、トランザクションプーリングモードで設定
# Azure Portal のサーバーパラメーターで以下を設定:
# pgbouncer.enabled = true
# pgbouncer.pool_mode = transaction
# pgbouncer.default_pool_size = 100
# pgbouncer.max_client_conn = 5000

# アプリケーションの接続文字列をポート 6432 に変更
psql "host=myPgServer.postgres.database.azure.com port=6432 dbname=myapp user=myUser password=<password> sslmode=require"
```

**効果**: 数千のクライアント接続を数十のサーバー接続に集約し、PostgreSQL サーバーのリソース消費を大幅に削減。接続の確立・切断に伴うオーバーヘッドも最小化される。

### ユースケース 2: マイクロサービスアーキテクチャ

**シナリオ**: AKS 上で多数のマイクロサービスが同一の PostgreSQL データベースに接続するケース。各サービスのレプリカが個別に接続を確立するため、接続数が爆発的に増加する。

**実装例**:

```bash
# 組み込み PgBouncer を有効化
# pgbouncer.enabled = true
# pgbouncer.pool_mode = transaction
# pgbouncer.max_client_conn = 5000
# pgbouncer.default_pool_size = 50

# 各マイクロサービスの接続文字列でポート 6432 を指定
# 例: DATABASE_URL=postgresql://user:pass@myPgServer.postgres.database.azure.com:6432/mydb?sslmode=require
```

**効果**: 数百のマイクロサービスレプリカからの接続を効率的にプーリングし、PostgreSQL のプロセス数を制限内に収める。追加のインフラストラクチャなしでコネクションプーリングを実現できる。

## 料金

PgBouncer は Azure Database for PostgreSQL - Flexible Server の組み込み機能として提供されるため、追加料金は発生しない。ただし、PgBouncer プロセスがデータベースサーバーと同一 VM 上で動作するため、CPU リソースに若干の影響がある。料金は Azure Database for PostgreSQL - Flexible Server の通常のコンピュートおよびストレージ料金に含まれる。

## 利用可能リージョン

Azure Database for PostgreSQL - Flexible Server が利用可能な全リージョンで PgBouncer 1.25.1 がサポートされる。

## 関連サービス・機能

- **Azure Database for PostgreSQL - Flexible Server**: PgBouncer が組み込まれるマネージド PostgreSQL サービス
- **Microsoft Entra ID**: PgBouncer での認証に使用可能な ID 管理サービス
- **Azure Kubernetes Service (AKS)**: PgBouncer をサイドカーコンテナとしてデプロイする別の構成パターンも利用可能
- **Azure Monitor**: PgBouncer メトリクス（アクティブ接続、アイドル接続、プール接続数など）の監視に対応

## 参考リンク

- [インフォグラフィック](https://takech9203.github.io/azure-news-summary/20260408-postgresql-pgbouncer-1-25-1.html)
- [公式アップデート情報](https://azure.microsoft.com/updates?id=559623)
- [Microsoft Learn - PgBouncer in Azure Database for PostgreSQL](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-pgbouncer)
- [Microsoft Learn - Connection pooling best practices](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-connection-pooling-best-practices)
- [PgBouncer 公式ドキュメント](https://www.pgbouncer.org/config.html)

## まとめ

Azure Database for PostgreSQL - Flexible Server における PgBouncer 1.25.1 の一般提供開始により、組み込みのコネクションプーリング機能が最新バージョンに更新された。PgBouncer は追加コストなしで利用可能なマネージド機能であり、アイドル接続や短命接続が多いトランザクショナルなアプリケーションに特に有効である。General Purpose または Memory Optimized ティアを使用している場合は、Azure Portal のサーバーパラメーターから `pgbouncer.enabled` を `true` に設定するだけで利用を開始できる。既にポート 5432 で直接接続しているアプリケーションは、接続先ポートを 6432 に変更することで PgBouncer のメリットを享受できる。

---

**タグ**: #Azure #PostgreSQL #FlexibleServer #PgBouncer #ConnectionPooling #Database #GA
