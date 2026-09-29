# SQL Server on Azure Virtual Machines: SQL Server on Linux Azure VM のスクリプトベースデプロイ (Public Preview)

**リリース日**: 2026-09-29

**サービス**: SQL Server on Azure Virtual Machines

**機能**: Script-based deployment for SQL Server on Linux Azure VM

**ステータス**: In preview

[このアップデートのインフォグラフィックを見る](https://takech9203.github.io/azure-news-summary/20260929-sql-server-linux-vm-script-deployment.html)

## 概要

SQL Server on Linux Azure Virtual Machines (VM) の新しいデプロイエクスペリエンスがパブリックプレビューとして発表されました。従来の事前作成済み (precreated) Azure Marketplace イメージに代わり、スクリプトベースの自動プロビジョニングが導入されます。標準の Linux ベースイメージから VM を作成し、SQL Server の構成を指定すると、Azure が VM プロビジョニング中に SQL Server を自動的にインストール・構成し、SQL Server IaaS Agent 拡張機能への登録まで統合ワークフローで実行します。

重要な変更点として、事前作成済みの SQL Server on Linux Azure Marketplace イメージは非推奨 (deprecated) となり、Azure portal、Azure SQL hub、Azure CLI、Azure PowerShell からの新規デプロイでは利用できなくなりました。今後は、サポートされる Linux ベースイメージ (RHEL 9/10、Ubuntu 22.04/24.04/26.04) を起点に、ポータルのガイド付き構成で SQL Server のバージョン・エディション・ライセンスモデルを選択してデプロイします。

デプロイは「Create a virtual machine」ページまたは Azure SQL hub のどちらからでも開始でき、いずれも同じガイド付き SQL Server 構成につながります。

**アップデート前の課題**

- SQL Server のバージョン・エディションと Linux ディストリビューションの組み合わせは、事前作成済み Marketplace イメージとして提供されているものに限られていた
- 新しい Linux バージョンや Azure の新機能を利用するには、対応する新しい Marketplace イメージの提供を待つ必要があった
- SQL Server の構成のカスタマイズ (mssql.conf など) はデプロイ後に手動で行う必要があった

**アップデート後の改善**

- Linux ディストリビューション、SQL Server のバージョン・エディション・機能を自由に選択でき、独自の `mssql.conf` ファイルをアップロードして構成をカスタマイズ可能
- 新しい Linux バージョンや Azure 機能が、Marketplace イメージの更新を待たずに利用可能 (サポート対象の新バージョンは自動的に選択肢に追加)
- すべての VM が SQL Server IaaS Agent 拡張機能に既定で自動登録され、ライセンスの柔軟性・コンプライアンス・ライセンス可視性を確保
- ポータルが OS・SQL Server バージョン・ライセンスの有効な組み合わせのみを表示するガイド付き構成

## アーキテクチャ図

```mermaid
flowchart TD
    subgraph Before["🕰️ Before: Marketplace イメージ方式"]
        U1(["👤 管理者"]) --> M["🛒 事前作成済み SQL Server on Linux<br>Marketplace イメージ (非推奨)"]
        M --> V1["🖥️ SQL Server 入り Linux VM<br>(固定の組み合わせ)"]
        V1 --> C1["🔧 デプロイ後に手動カスタマイズ"]
    end
    subgraph After["✨ After: スクリプトベースデプロイ (Preview)"]
        U2(["👤 管理者"]) --> P["🧭 Azure portal / Azure SQL hub<br>ガイド付き構成"]
        P --> B["🐧 標準 Linux ベースイメージ<br>(RHEL 9/10, Ubuntu 22.04/24.04/26.04)"]
        B --> S["⚙️ Azure が SQL Server を自動<br>インストール・構成 (mssql.conf 対応)"]
        S --> E["🤖 SQL IaaS Agent 拡張機能に自動登録"]
    end
```

従来は事前作成済み Marketplace イメージの固定的な組み合わせからしか選べませんでしたが、新方式では標準 Linux イメージを起点に、プロビジョニング中に SQL Server のインストール・構成・IaaS Agent 拡張機能への登録までが自動化されます。

## サービスアップデートの詳細

### 主要機能

1. **柔軟性とコントロール**
   - Linux ディストリビューション、SQL Server のバージョン・エディション・機能を選択可能
   - 独自の `mssql.conf` ファイルをアップロードして SQL Server 構成をカスタマイズ可能

2. **新バージョンへの迅速なアクセス**
   - 新しい Linux バージョンや Azure の新機能が、新しい Marketplace イメージの提供を待たずに利用可能
   - サポートされる新しいディストリビューションのバージョンは自動的に選択肢に追加

3. **SQL Server IaaS Agent 拡張機能への自動登録**
   - すべての VM が既定で SQL Server IaaS Agent 拡張機能に登録
   - VM リソースとは別に「SQL virtual machine」リソースが作成され、Azure から SQL Server のライセンスタイプを管理可能
   - デプロイ後の登録解除・再登録も可能

4. **ガイド付き構成**
   - Azure portal は、選択した OS・SQL Server バージョン・ライセンスオプションの有効な組み合わせのみを表示

5. **2 つのデプロイ開始ポイント**
   - Azure portal の「Create a virtual machine」ページ: Basics タブで Linux ベースイメージを選択し、Advanced タブで「Install SQL Server」を有効化
   - Azure SQL hub: 「SQL Server on Linux」イメージオファーを選択する SQL ファーストのエクスペリエンス。選択内容が VM 作成ページに事前入力される

### デプロイのステージ

1. サポートされる Linux ベースイメージと VM サイズを選択
2. SQL Server を有効化し、バージョン・エディション・機能・ライセンスモデルを構成
3. Azure が VM 上に SQL Server をインストール・構成
4. Azure が VM を SQL Server IaaS Agent 拡張機能に登録 (Pay-as-you-go または Azure Hybrid Benefit のライセンスタイプ)

## 技術仕様

| 項目 | 詳細 |
|------|------|
| サポートされる Linux ディストリビューション | RHEL 9、RHEL 10、Ubuntu 22.04、Ubuntu 24.04、Ubuntu 26.04 |
| SQL Server バージョン | SQL Server 2025、SQL Server 2022 など (ポータルで選択可能なバージョン) |
| SQL Server エディション | Enterprise、Standard、Developer、Express、Evaluation (選択したバージョンにより利用可能なエディションが変動) |
| ライセンスモデル | Pay-as-you-go (既定) / Azure Hybrid Benefit (License Mobility through Software Assurance 付きライセンスが必要) |
| 構成のカスタマイズ | ポータルでの SQL Server オプション構成、またはカスタム `mssql.conf` ファイルのアップロード |
| IaaS Agent 拡張機能 | デプロイ時に自動登録 (VM リソースとは別の SQL virtual machine リソースを作成) |
| 非サポート | SUSE Linux Enterprise Server (SLES)。SLES で SQL Server を実行する場合は SLES VM を作成して手動インストール |
| 既定でインストールされるツール | SQL Server コマンドラインツールパッケージ (`sqlcmd`、`bcp`。パス: `/opt/mssql-tools/bin/`) |
| 従来の Marketplace イメージ | 非推奨。Azure portal、Azure SQL hub、Azure CLI、Azure PowerShell からの新規デプロイで利用不可 |

## 設定方法

### 前提条件

1. Azure サブスクリプション
2. (Azure Hybrid Benefit を選択する場合) License Mobility through Software Assurance 付きの SQL Server ライセンス
3. (SSH 公開キー認証を使用する場合) RSA 公開キー

### Azure Portal

**方法 1: 「Create a virtual machine」ページから**

1. Azure portal で **Virtual machines** > **Create** を選択
2. **Basics** タブでサブスクリプション、リソースグループ、VM 名、リージョン、可用性オプションを設定
3. **Image** でサポートされる Linux ベースイメージ (RHEL 9/10、Ubuntu 22.04/24.04/26.04 など) を選択し、VM サイズを選択
4. 認証 (SSH 公開キー推奨) と受信ポート (SSH 22。リモート接続には後で 1433 を許可) を構成
5. **Advanced** タブで **Install SQL Server** を選択すると、**SQL Server settings** タブが有効化
6. **SQL Server settings** タブでバージョン、エディション、ライセンスモデル (Pay-as-you-go / Azure Hybrid Benefit)、詳細構成 (`mssql.conf` のアップロード可) を設定
7. **Review + create** で構成を確認し、**Create** を選択

**方法 2: Azure SQL hub から**

1. [Azure SQL hub](https://aka.ms/azuresqlhub) で **SQL Server on Azure Virtual Machines** > **+ Create** を選択
2. **Show options** から、イメージオファー **SQL Server on Linux**、SQL Server バージョン (2025 / 2022 など)、ディストリビューション、エディションを選択
3. 選択内容が事前入力された VM 作成ページに進み、以降は方法 1 と同様に構成

デプロイ後は、Azure portal の **SQL virtual machines** に VM が表示されることで IaaS Agent 拡張機能への登録を確認できます。

## メリット

### ビジネス面

- Marketplace イメージの提供を待たずに新しい Linux バージョン・SQL Server バージョンを採用でき、モダナイゼーションのリードタイムを短縮
- IaaS Agent 拡張機能への自動登録により、ライセンスの柔軟性 (Pay-as-you-go / Azure Hybrid Benefit の管理)、コンプライアンス、ライセンスの可視性を確保

### 技術面

- Linux ディストリビューション、SQL Server バージョン・エディション・機能の組み合わせを自由に選択可能
- `mssql.conf` ファイルのアップロードにより、デプロイ時点で SQL Server 構成をコード化・標準化できる
- ポータルが有効な組み合わせのみを表示するため、構成ミスを防止
- VM プロビジョニングから SQL Server のインストール・構成・拡張機能登録までが単一の統合ワークフローで完結

## デメリット・制約事項

- 本機能は現在プレビューであり、本番環境での利用には注意が必要
- SUSE Linux Enterprise Server (SLES) はポータルデプロイの対象外 (手動インストールが必要)
- 事前作成済み SQL Server on Linux Marketplace イメージは非推奨となり、Azure portal / Azure SQL hub / Azure CLI / Azure PowerShell からの新規デプロイでは利用不可。既存の自動化 (IaC やスクリプト) が Marketplace イメージに依存している場合は見直しが必要

## ユースケース

### ユースケース 1: 最新の Linux ディストリビューションでの SQL Server 2025 検証環境の構築

**シナリオ**: Ubuntu 24.04 上で SQL Server 2025 の新機能を検証したいが、従来は対応する Marketplace イメージの提供を待つ必要があった。

**実装例**:

1. Azure SQL hub で「SQL Server on Linux」を選択し、SQL Server 2025 + Ubuntu 24.04 + Developer エディションを指定
2. VM 作成ページで開発用の VM サイズを選択してデプロイ
3. デプロイ完了後、SSH で接続し `/opt/mssql-tools/bin/` の `sqlcmd` で動作確認

**効果**: Marketplace イメージの提供を待たずに、最新の OS と SQL Server バージョンの組み合わせを即座に検証できる。

### ユースケース 2: 標準化された SQL Server 構成での本番 VM プロビジョニング (プレビュー明け以降)

**シナリオ**: 組織標準の SQL Server 構成 (照合順序、トレースフラグなどの `mssql.conf` 設定) を、デプロイ時点で確実に適用したい。

**実装例**:

1. 組織標準の `mssql.conf` ファイルを用意
2. VM 作成時の SQL Server settings タブの Advanced configuration でこのファイルをアップロード
3. Azure Hybrid Benefit を選択して既存ライセンスを活用し、IaaS Agent 拡張機能経由でライセンスタイプを一元管理

**効果**: デプロイ後の手動構成作業を排除し、構成のばらつきを防止。ライセンス管理も Azure 側で可視化される。

## 料金

このアップデート自体に伴う追加料金の公式情報は確認できませんでした。SQL Server on Azure VM の料金は、VM 料金と SQL Server ライセンス (Pay-as-you-go の場合) で構成されます。Azure Hybrid Benefit を選択すると、License Mobility through Software Assurance 付きの既存 SQL Server ライセンスを持ち込めます。詳細は料金ページを参照してください。

- [SQL Server on Azure VM の料金ページ](https://azure.microsoft.com/pricing/details/virtual-machines/sql-server-enterprise-linux/)

## 関連サービス・機能

- **SQL Server IaaS Agent 拡張機能 (Linux)**: 本デプロイ方式で自動登録される拡張機能。Azure からの SQL Server ライセンスタイプ管理やコンプライアンス・ライセンス可視性を提供
- **Azure SQL hub**: SQL ファーストのデプロイ開始ポイント。SQL Server on Linux のイメージオファー・バージョン・ディストリビューション・エディションを選択して VM 作成に進める
- **Azure Hybrid Benefit**: 既存の SQL Server ライセンス (Software Assurance 付き) を持ち込んでコストを削減するライセンスオプション
- **SQL Server on Windows Azure VM**: Windows 版の SQL Server VM。こちらは引き続き Marketplace イメージベースのデプロイを提供

## 参考リンク

- [インフォグラフィック](https://takech9203.github.io/azure-news-summary/20260929-sql-server-linux-vm-script-deployment.html)
- [公式アップデート情報](https://azure.microsoft.com/updates?id=571810)
- [発表ブログ (Tech Community)](https://techcommunity.microsoft.com/blog/sqlserver/announcing-script-based-deployment-for-sql-server-on-linux-azure-vms-public-prev/4547846)
- [Microsoft Learn: SQL Server on Azure Virtual Machines for Linux の概要](https://learn.microsoft.com/azure/azure-sql/virtual-machines/linux/sql-server-on-linux-vm-what-is-iaas-overview)
- [Microsoft Learn: クイックスタート - Linux SQL Server VM の作成](https://learn.microsoft.com/azure/azure-sql/virtual-machines/linux/sql-vm-create-portal-quickstart)
- [料金ページ](https://azure.microsoft.com/pricing/details/virtual-machines/sql-server-enterprise-linux/)

## まとめ

SQL Server on Linux Azure VM のデプロイが、事前作成済み Marketplace イメージからスクリプトベースの自動プロビジョニングへと刷新されました (パブリックプレビュー)。標準 Linux ベースイメージ (RHEL 9/10、Ubuntu 22.04/24.04/26.04) を起点に、SQL Server のバージョン・エディション・ライセンスの柔軟な選択、`mssql.conf` によるカスタマイズ、SQL IaaS Agent 拡張機能への自動登録が統合ワークフローで実現されます。従来の Marketplace イメージは非推奨となり新規デプロイで利用できないため、SQL Server on Linux VM を利用中・検討中の組織は、既存のデプロイ自動化が Marketplace イメージに依存していないか確認し、新しいデプロイ方式への移行を検証することを推奨します。SLES が対象外である点にも注意が必要です。

---

**タグ**: SQL Server on Azure Virtual Machines, Linux, Compute, Databases, In preview, Deployment, SQL IaaS Agent extension
