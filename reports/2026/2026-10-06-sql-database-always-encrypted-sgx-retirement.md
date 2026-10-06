# Azure SQL Database: Always Encrypted with Intel SGX Enclaves の廃止

**リリース日**: 2026-10-06

**サービス**: Azure SQL Database

**機能**: Always Encrypted with Intel SGX Enclaves (廃止アナウンス)

**ステータス**: Retirement (廃止日: 2027-10-31)

[このアップデートのインフォグラフィックを見る](https://takech9203.github.io/azure-news-summary/20261006-sql-database-always-encrypted-sgx-retirement.html)

## 概要

Azure SQL Database における Always Encrypted with Intel SGX (Software Guard Extensions) エンクレーブが **2027 年 10 月 31 日に廃止** されることがアナウンスされました。SGX 対応の DC シリーズハードウェアのサポートが段階的に終了することが理由です。

Always Encrypted with secure enclaves は、データベースエンジン内の保護されたメモリ領域 (セキュアエンクレーブ) で暗号化された列に対するインプレース暗号化やリッチな機密クエリ (LIKE、範囲比較、JOIN、GROUP BY、ORDER BY など) を可能にする機密コンピューティング機能です。Azure SQL Database では、DC シリーズハードウェア構成のデータベースが Intel SGX エンクレーブを使用し、それ以外の vCore 構成および DTU 購入モデルのデータベースは VBS (Virtualization-Based Security) エンクレーブを使用できます。

廃止日以降、DC シリーズコンピューティング層に残っているデータベースは、Azure によって自動的にサポート対象の Standard シリーズ (非 DC) コンピューティング層へ移動され、VBS エンクレーブが有効化されます。自動移行に委ねるのではなく、廃止日より前に計画的に移行を完了することが推奨されます。

**アップデート前 (現状)**

- Azure SQL Database では DC シリーズハードウェア上の Intel SGX エンクレーブ (ハードウェアベースの TEE) が利用可能で、Microsoft Azure Attestation による構成証明が必須
- SGX エンクレーブはゲスト OS とホスト OS の両方からの攻撃に対する保護を提供

**アップデート後 (廃止の影響)**

- 2027-10-31 で Intel SGX エンクレーブのサポートが終了。DC シリーズに残るデータベースは Standard シリーズへ自動移動され、VBS エンクレーブが有効化される
- 移行先の VBS エンクレーブはハードウェアに依存しないソフトウェアベースの技術で、構成証明 (attestation) は不要 (Azure SQL Database の VBS エンクレーブは attestation をサポートしない)
- ホスト起点の特権攻撃からの保護が必要な場合は、Azure Confidential VM 上の SQL Server (VBS エンクレーブ + オプションで HGS attestation) が代替オプション

## アーキテクチャ図

```mermaid
flowchart TD
    subgraph Before["🔴 Before: 2027-10-31 まで"]
        APP1(["👤 クライアントアプリ"])
        MAA["🔏 Microsoft Azure Attestation<br/>(構成証明: 必須)"]
        subgraph DC["🖥️ DC シリーズ (SGX 対応ハードウェア)"]
            SGX["🔒 Intel SGX エンクレーブ<br/>(ハードウェアベース TEE)"]
            DB1[("🗄️ Azure SQL Database")]
        end
        APP1 -->|構成証明 + クエリ| MAA
        MAA --> SGX
        SGX --- DB1
    end

    subgraph After["🟢 After: 移行後"]
        APP2(["👤 クライアントアプリ<br/>(ドライバー更新 + 接続文字列変更)"])
        subgraph STD["🖥️ Standard シリーズ (ハードウェア非依存)"]
            VBS["🔒 VBS エンクレーブ<br/>(ハイパーバイザーベース)"]
            DB2[("🗄️ Azure SQL Database")]
        end
        APP2 -->|構成証明なしで接続| VBS
        VBS --- DB2
    end

    Before -.->|移行 (2027-10-31 まで)| After
```

DC シリーズ上の Intel SGX エンクレーブ (構成証明必須) から、Standard シリーズ上の VBS エンクレーブ (構成証明不要) への移行を示しています。移行後もエンクレーブ内でのインプレース暗号化と機密クエリは継続して利用できますが、セキュリティ境界がハードウェアベースからハイパーバイザーベースに変わる点に注意が必要です。

## サービスアップデートの詳細

### 廃止の内容

1. **廃止対象**
   - Azure SQL Database の Always Encrypted with Intel SGX エンクレーブ (DC シリーズハードウェア構成のデータベースで使用)
   - 廃止理由: SGX 対応の DC シリーズハードウェアのサポートの段階的終了

2. **廃止日と自動移行の挙動**
   - **2027 年 10 月 31 日** にサポート終了
   - 廃止日以降、DC シリーズコンピューティング層に残っているデータベースは、Azure により自動的にサポート対象の Standard シリーズ (非 DC) コンピューティング層へ移動され、VBS エンクレーブが有効化される

3. **移行先の選択肢**
   - **Azure SQL Database + VBS エンクレーブ**: Azure SQL Database に留まり、VBS エンクレーブがセキュリティ要件を満たす場合。VBS エンクレーブは attestation をサポートしない
   - **Azure Confidential VM 上の SQL Server + VBS エンクレーブ**: ホストオペレーターのアクセスからゲスト OS を保護するハードウェア強制の境界が必要な場合。HGS (Host Guardian Service) attestation はオプション

### SGX エンクレーブと VBS エンクレーブの比較

| 項目 | Intel SGX エンクレーブ | VBS エンクレーブ |
|------|----------------------|-----------------|
| 技術基盤 | ハードウェアベースの TEE (Intel SGX) | ソフトウェアベース (Windows ハイパーバイザー) |
| ハードウェア要件 | DC シリーズ (SGX 対応ハードウェア) が必要 | 特別なハードウェア不要 |
| 保護範囲 | ゲスト OS とホスト OS の両方からの攻撃に対する保護 | VM 内部からの攻撃に対する保護 (ホスト起点の特権攻撃からは保護しない) |
| 構成証明 (Azure SQL Database) | Microsoft Azure Attestation が必須 | attestation 非サポート (不要) |
| 利用可能な構成 | vCore 購入モデルの DC シリーズのみ | DC シリーズ以外の vCore 構成および DTU 購入モデル |

## 技術仕様

| 項目 | 詳細 |
|------|------|
| 廃止日 | 2027 年 10 月 31 日 |
| 対象サービス | Azure SQL Database (DC シリーズハードウェア構成) |
| 廃止後の自動処理 | DC シリーズのデータベースを Standard シリーズ (非 DC) へ自動移動し、VBS エンクレーブを有効化 |
| 移行先のプロパティ | データベース/エラスティックプールの `preferredEnclaveType` を `VBS` に設定 |
| クライアント側の変更 | VBS エンクレーブ対応ドライバーへの更新、enclave attestation protocol を `None` に変更、Azure Attestation URL の削除 |
| エラスティックプール | プール内の全データベースがプールのエンクレーブ構成を継承 (DC シリーズプールは全データベースが影響を受ける) |

## 設定方法 (移行手順)

### 前提条件

1. 対象の Azure SQL 論理サーバー、データベース、エラスティックプールの表示・変更権限があること
2. 影響を受けるデータベースに接続するアプリケーションを棚卸しし、ドライバー・接続文字列・attestation 設定を更新できるようにしておくこと

### Azure CLI: DC シリーズを使用するデータベースの特定

```bash
# スタンドアロンの DC シリーズデータベースを一覧表示
az sql db list \
    --resource-group $resourceGroupName \
    --server $serverName \
    --query "[?elasticPoolName == null && currentSku.family == 'DC'].{Database:name, ServiceObjective:currentServiceObjectiveName}" \
    --output table

# DC シリーズのエラスティックプールを取得
dcPoolNames=$(az sql elastic-pool list \
    --resource-group $resourceGroupName \
    --server $serverName \
    --query "[?sku.family == 'DC'].name" \
    --output tsv)

# 各 DC シリーズプール内のデータベースを一覧表示
for poolName in $dcPoolNames; do
    az sql elastic-pool list-dbs \
        --resource-group $resourceGroupName \
        --server $serverName \
        --name $poolName \
        --query "[].{PoolName:elasticPoolName, Database:name}" \
        --output table
done
```

### 単一データベースの VBS エンクレーブへの移行手順

1. ワークロードの性能・可用性要件を満たす Standard シリーズ (非 DC) ハードウェア構成を選択する
2. データベースを選択したハードウェア構成へ移動する
3. データベースの VBS エンクレーブを有効化する (`preferredEnclaveType` が `VBS` に設定される)
4. VBS エンクレーブ (attestation なし) に対応したクライアントドライバーの要件を確認し、必要に応じてアプリケーションのドライバーを更新する
5. 各アプリケーション接続の enclave attestation protocol を `None` に変更し、Microsoft Azure Attestation の URL を削除する (キーワードはドライバーにより異なる)
6. 移行後の検証を実施する

### 移行後の検証

1. Always Encrypted を有効にした状態でアプリケーションが接続できることを確認
2. エンクレーブ計算を必要とするクエリを含め、暗号化列を使用する代表的なクエリを実行
3. 暗号化列に対する INSERT / UPDATE / DELETE / インデックス操作が想定どおり動作することを確認
4. 性能をテストし、必要に応じてコンピューティング構成を調整
5. BCDR・フェールオーバー手順をテスト (エンクレーブ対応操作を使う場合、すべてのレプリカがセキュアエンクレーブをサポートしている必要がある)
6. カットオーバー前にエンクレーブ・attestation・クエリのエラーを監視

## メリット

### ビジネス面

- VBS エンクレーブはハードウェア非依存のため、DC シリーズという特定ハードウェアへの依存から解放される
- 構成証明 (Microsoft Azure Attestation) の構成・運用が不要になり、運用がシンプルになる

### 技術面

- 移行後もインプレース暗号化とリッチな機密クエリ (LIKE、範囲比較、JOIN、GROUP BY、ORDER BY など) は継続利用可能
- VBS エンクレーブは DC シリーズ以外の vCore 構成と DTU 購入モデルの両方で利用でき、ハードウェア構成の選択肢が広がる

## デメリット・制約事項

- **セキュリティ保護レベルの変化**: VBS エンクレーブは VM 内部からの攻撃に対する保護を提供するが、ホスト起点の特権システムアカウントによる攻撃からは保護しない。SGX エンクレーブと同等のハードウェア強制の保護が必要な場合は、Azure Confidential VM 上の SQL Server を検討する必要がある
- **構成証明の非対応**: Azure SQL Database の VBS エンクレーブは enclave attestation をサポートしないため、エンクレーブの真正性を外部サービスで検証する防御層がなくなる
- **アプリケーション側の変更が必要**: クライアントドライバーの更新と接続文字列の変更 (attestation protocol を `None` にし、attestation URL を削除) が必要
- **期日までに移行しない場合**: 2027-10-31 以降に Azure による自動移行 (Standard シリーズへの移動 + VBS エンクレーブ有効化) が行われるため、意図しないタイミングでの構成変更が発生し得る
- VBS エンクレーブ対応データベースを復元した場合は、VBS エンクレーブ設定の再構成が必要

## 利用可能リージョン

VBS エンクレーブは、Jio India Central を除くすべての Azure SQL Database リージョンで利用可能です (2026-10 時点の公式ドキュメントによる)。

## 関連サービス・機能

- **Always Encrypted with secure enclaves**: 本廃止の対象機能の基盤。VBS エンクレーブへ移行後も機能自体は継続利用可能
- **Microsoft Azure Attestation**: SGX エンクレーブの構成証明に必須だったサービス。VBS エンクレーブ移行後は不要となり、接続文字列から URL を削除する
- **Azure Confidential VM 上の SQL Server**: ホストからの保護を含むハードウェア強制の境界が必要な場合の代替移行先。データ移行には Azure Data Factory、Smart Bulk Copy、BACPAC などを利用できる
- **Host Guardian Service (HGS)**: SQL Server (Confidential VM 含む) で VBS エンクレーブの attestation を行う場合のオプション

## 参考リンク

- [インフォグラフィック](https://takech9203.github.io/azure-news-summary/20261006-sql-database-always-encrypted-sgx-retirement.html)
- [公式アップデート情報](https://azure.microsoft.com/updates?id=569236)
- [Always Encrypted with secure enclaves (Microsoft Learn)](https://learn.microsoft.com/sql/relational-databases/security/encryption/always-encrypted-enclaves)
- [Always Encrypted with Intel SGX enclaves migration guide (Microsoft Learn)](https://learn.microsoft.com/sql/relational-databases/security/encryption/always-encrypted-enclaves-migration)
- [Enable VBS enclaves (Microsoft Learn)](https://learn.microsoft.com/azure/azure-sql/database/always-encrypted-enclaves-enable)
- [Azure SQL Database 料金ページ](https://azure.microsoft.com/pricing/details/azure-sql-database/single/)

## まとめ

Azure SQL Database の Always Encrypted with Intel SGX エンクレーブは **2027 年 10 月 31 日に廃止** されます。期日を過ぎると DC シリーズ上のデータベースは Standard シリーズへ自動移動され VBS エンクレーブが有効化されるため、意図しない構成変更を避けるには事前の計画的な移行が不可欠です。

Solutions Architect としての推奨アクションは次のとおりです。

1. **棚卸し**: Azure Portal / PowerShell / Azure CLI で DC シリーズを使用するデータベースとエラスティックプールをすべて特定する
2. **移行パスの選定**: VBS エンクレーブがセキュリティ要件を満たすかを評価する。VBS はホスト起点の攻撃からは保護しないため、ハードウェア強制の境界が必要な場合は Azure Confidential VM 上の SQL Server を検討する
3. **移行の実施**: Standard シリーズへの移動、VBS エンクレーブの有効化、クライアントドライバーの更新、接続文字列の変更 (attestation protocol を `None` へ) を行い、移行後検証 (接続・機密クエリ・DML・性能・BCDR) を完了する

廃止日まで約 1 年の猶予がありますが、アプリケーション側の変更とセキュリティ要件の再評価を伴うため、早期に移行計画を開始することを推奨します。

---

**タグ**: Azure SQL Database, Always Encrypted, Intel SGX, VBS Enclaves, Confidential Computing, Retirement, Databases, Security
