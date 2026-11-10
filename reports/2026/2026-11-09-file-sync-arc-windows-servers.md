# Azure File Sync: Arc-enabled Windows Server のモダナイズ (ガイド付きポータル体験)

**リリース日**: 2026-11-09

**サービス**: Azure File Sync / Azure Arc-enabled servers

**機能**: Arc-enabled Windows Server への Azure File Sync のガイド付きオンボーディング

**ステータス**: In preview (パブリックプレビュー)

[このアップデートのインフォグラフィックを見る](https://takech9203.github.io/azure-news-summary/20261109-file-sync-arc-windows-servers.html)

## 概要

Azure File Sync は、オンプレミスの Windows ファイルサーバーの使い勝手 (互換性・パフォーマンス・柔軟性) を維持しながら、組織のファイル共有を Azure Files に集約できるハイブリッドサービスです。登録された各 Windows Server は中央の Azure ファイル共有とデータを同期し、クラウド階層化 (Cloud Tiering) により頻繁にアクセスされるファイルのみをローカルにキャッシュできます。

今回のパブリックプレビューでは、Azure Arc-enabled Windows Server を Azure File Sync にオンボードするための**ガイド付き Azure ポータル体験**が提供されました。Arc-enabled サーバーのポータルページに「Azure File Sync (Preview)」メニューが追加され、エージェントのインストール (VM 拡張機能)、Storage Sync Service へのサーバー登録、同期グループ・エンドポイント・クラウド階層化の構成までを、1 つのワークフローで完結できます。

**アップデート前の課題**

- Azure File Sync エージェントのインストール (MSI のダウンロードと実行) とサーバー登録 (`ServerRegistration.exe` でのサインインと登録) を、サーバー上でそれぞれ個別に実施する必要があった
- エージェント導入、サーバー登録、同期設定が別々の画面・ツールに分かれており、オンボーディングの全体像を 1 か所で把握できなかった

**アップデート後の改善**

- Arc-enabled Windows Server のポータルページから「Azure File Sync (Preview)」を選択するだけで、エージェントインストール (Azure File Sync Agent for Windows 拡張機能) → サーバー登録 → 同期構成までをガイドに従って完結できる
- 既存の Windows Server でファイル提供を継続しながら、データの完全なコピーを Azure Files に集約できる
- クラウド階層化により、頻繁に使うファイルはローカルに保持し、使用頻度の低いコンテンツは Azure に階層化してローカルストレージを最適化できる

## アーキテクチャ図

```mermaid
flowchart LR
    subgraph OnPrem["🏢 オンプレミス"]
        Users(["👥 ユーザー / アプリ"])
        ArcServer["🖥️ Arc-enabled Windows Server<br/>(ローカルキャッシュ + クラウド階層化)"]
        Agent["📦 Azure File Sync Agent<br/>(Arc VM 拡張機能)"]
        Users -->|SMB アクセス| ArcServer
        ArcServer --- Agent
    end
    subgraph Azure["☁️ Azure"]
        Portal["🧭 Azure ポータル<br/>ガイド付き体験 (Preview)"]
        Arc["🔗 Azure Arc"]
        SSS["🔄 Storage Sync Service"]
        Files[("📁 Azure Files<br/>(クラウドエンドポイント)")]
        Portal --> Arc
        Arc -->|拡張機能の配布| Agent
        SSS <--> Files
    end
    Agent <-->|同期 (サーバーエンドポイント)| SSS
```

Azure ポータルのガイド付き体験から Azure Arc 経由でエージェント (拡張機能) をインストールし、オンプレミスの Windows Server と Azure Files 間のファイル同期を構成するハイブリッド構成です。

## サービスアップデートの詳細

### 主要機能

1. **ガイド付きオンボーディング体験 (Preview)**
   - Arc-enabled Windows Server のポータルページ (**Windows management** > **Azure File Sync (Preview)**) に、「Install Azure File Sync agent」「Register server」「Configure Azure File Sync」のセクションが表示される
   - エージェントのインストール、Storage Sync Service へのサーバー登録 (新規作成も可能)、同期グループ・エンドポイント・クラウド階層化の構成までを 1 つの画面フローで実施できる

2. **Azure File Sync Agent for Windows 拡張機能によるエージェント管理**
   - Arc の VM 拡張機能としてエージェントを配布でき、インストールディレクトリ、自動更新スケジュール、プロキシ設定を構成可能
   - Azure PowerShell (`New-AzConnectedMachineExtension`) や Azure CLI (`az connectedmachine extension create`) によるデプロイにも対応

3. **ファイルデータの Azure への集約とローカルストレージの最適化**
   - 既存の Windows Server 経由でユーザーへのファイル提供を続けながら、完全なコピーを Azure Files に保持
   - クラウド階層化により、頻繁にアクセスするファイルはローカルにキャッシュし、低頻度のファイルは Azure に階層化。名前空間全体はローカルから参照可能で、階層化されたファイルはアクセス時に透過的に呼び戻される

## 技術仕様

| 項目 | 詳細 |
|------|------|
| 対象サーバー | Azure Arc-enabled **Windows** Server (Linux の Arc-enabled サーバーは非対応) |
| サポート OS | Windows Server 2016 / 2019 / 2022 / 2025 (Azure File Sync エージェントのサポート対象) |
| エージェント要件 | .NET Framework 4.7.2 以降 (Windows Server 2019 以降は既定で搭載) |
| 配布方式 | Arc VM 拡張機能「Azure File Sync Agent for Windows」(Publisher: Microsoft.StorageSync) |
| 拡張機能の設定項目 | エージェント自動更新 (曜日・時刻)、サーバー診断、Microsoft Update 登録、プロキシ設定 |
| サーバー登録 | 1 サーバーにつき 1 つの Storage Sync Service にのみ登録可能 |
| 必要なロール | 登録には Azure File Sync Administrator、Owner、または Contributor ロールが必要 |

## 設定方法

### 前提条件

1. 対象の Windows Server が Azure Arc-enabled servers として Azure に接続済みであること (Connected Machine Agent 導入済み)
2. Storage Sync Service をデプロイ済み、またはガイド内で新規作成すること
3. 登録を行う管理者が、Storage Sync Service に対して Azure File Sync Administrator / Owner / Contributor のいずれかのロールを持つこと
4. .NET Framework 4.7.2 以降 (Windows Server 2016 の場合は事前に確認)

### Azure Portal (ガイド付き体験)

1. Azure ポータルで **Azure Arc** > **Machines** に移動し、対象の Arc-enabled Windows Server を選択する
2. **Windows management** の下にある **Azure File Sync (Preview)** を選択する
3. **Install Azure File Sync agent** で **Install agent** を選択し、「Azure File Sync Agent for Windows」拡張機能のインストール完了を待つ
4. **Register server** で **Register** を選択し、既存の Storage Sync Service にサーバーを登録する (必要に応じて **Create Storage Sync Service** で新規作成)
5. **Configure Azure File Sync** で **Configure** を選択し、同期グループ、クラウドエンドポイント (Azure ファイル共有)、サーバーエンドポイント、クラウド階層化を設定する

### Azure CLI (拡張機能のインストール)

```bash
# Arc-enabled サーバーに Azure File Sync エージェント拡張機能をインストール
az connectedmachine extension create \
  --name AzureFileSyncAgentExtension \
  --machine-name <machine> \
  --resource-group <resource-group> \
  --publisher Microsoft.StorageSync \
  --type AzureFileSyncAgentExtension \
  --settings '{"EnableAgentAutoUpdate":"true","EnableServerDiagnostics":"true","EnrollInMicrosoftUpdate":"true"}'
```

## メリット

### ビジネス面

- オンボーディング手順の簡素化により、ハイブリッドファイルサーバー環境の導入・移行プロジェクトの初期コストと作業時間を削減できる
- ユーザーやアプリケーションは従来どおりローカルファイルサーバーを使い続けられるため、業務影響を最小化しながらデータを Azure に集約できる
- クラウド階層化によりオンプレミスストレージの増設コストを抑制できる

### 技術面

- エージェントの配布・更新を Arc の VM 拡張機能として一元管理できる (自動更新スケジュールやプロキシ設定も拡張機能側で構成可能)
- サーバー上での MSI 手動インストールと `ServerRegistration.exe` による個別登録が不要になり、ポータルから一貫したワークフローで構成できる
- Azure Files 側で Azure Backup によるクラウド側バックアップや、複数拠点間のマルチサイト同期・災害復旧の構成が可能

## デメリット・制約事項

- パブリックプレビュー段階であり、本番環境での利用は推奨されない (プレビューは非本番・テスト用途向け)
- Azure File Sync エージェント拡張機能は Windows のみサポート。Linux の Arc-enabled サーバーは非対応
- サーバーは 1 つの Storage Sync Service にのみ登録できる
- 前提として対象サーバーが Azure Arc に接続済みである必要がある

## ユースケース

### ユースケース 1: オンプレミスファイルサーバーのハイブリッド化とストレージ最適化

**シナリオ**: 既に Azure Arc で管理している拠点のファイルサーバーのディスク容量が逼迫している。ユーザーの利用体験を変えずに、データを Azure Files に集約してローカルストレージを削減したい。

**実装例**: Azure ポータルの Arc-enabled サーバーページから「Azure File Sync (Preview)」を開き、ガイドに従ってエージェントインストール → サーバー登録 → 同期グループとクラウド階層化を構成する。

**効果**: 頻繁に使うファイルのみローカルにキャッシュされ、低頻度ファイルは Azure に階層化される。全データのコピーが Azure Files に保持されるため、クラウド側バックアップ (Azure Backup) や障害時の再プロビジョニングも容易になる。

### ユースケース 2: Windows Server から Azure Files へのシームレスな移行

**シナリオ**: 老朽化した Windows ファイルサーバーのデータを、ユーザーを中断させずにバックグラウンドで Azure Files へ移行したい。

**効果**: Azure File Sync の同期により、ファイル構造・アクセス許可・アクセスパターンを維持したままデータを Azure に移行できる。移行期間中もローカルサーバー経由のアクセスを継続できる。

## 料金

Azure File Sync は**サーバーごとの固定月額料金**で課金されます (具体的な金額はリージョン・通貨により異なるため、料金ページで確認してください)。これに加えて、同期に伴う Azure Files のストレージ料金・トランザクション料金・送信データ転送料金が別途発生します。

| 項目 | 料金 |
|------|------|
| 同期サーバー | サーバーごとの月額固定料金 (料金ページ参照) |
| Azure Files ストレージ | メディア階層 (SSD/HDD) と課金モデル (Provisioned v2 / v1 / Pay-as-you-go) による |
| トランザクション / データ転送 | 同期時のファイル操作・送信データ転送に応じて課金 |

無料枠: Storage Sync Service ごとに同期サーバー 1 台分が無料。

詳細: [Azure Files 料金ページ](https://azure.microsoft.com/pricing/details/storage/files/)

## 関連サービス・機能

- **Azure Arc-enabled servers**: 本機能の前提。オンプレミスや他クラウドのサーバーを Azure リソースとして管理し、VM 拡張機能の配布を可能にする
- **Azure Files**: 同期先となるフルマネージドのクラウドファイル共有。クラウドエンドポイントとして同期グループに参加する
- **クラウド階層化 (Cloud Tiering)**: 頻繁にアクセスされるファイルのみをローカルにキャッシュし、オンプレミスストレージコストを削減する Azure File Sync の機能
- **Azure Backup**: Azure Files のスナップショットを利用したクラウド側の集中バックアップが可能で、オンプレミスのバックアップ基盤を削減できる

## 参考リンク

- [インフォグラフィック](https://takech9203.github.io/azure-news-summary/20261109-file-sync-arc-windows-servers.html)
- [公式アップデート情報](https://azure.microsoft.com/updates?id=579854)
- [Microsoft Learn: Azure File Sync のデプロイ (Arc-enabled サーバーへのインストール)](https://learn.microsoft.com/azure/storage/file-sync/file-sync-deployment-guide?tabs=azure-portal%2Cproactive-portal#install-on-azure-arc-enabled-servers)
- [Microsoft Learn: Azure File Sync とは](https://learn.microsoft.com/azure/storage/file-sync/file-sync-introduction)
- [Microsoft Learn: Azure Arc-enabled servers の概要](https://learn.microsoft.com/azure/azure-arc/servers/overview)
- [料金ページ (Azure Files / Azure File Sync)](https://azure.microsoft.com/pricing/details/storage/files/)

## まとめ

Azure Arc-enabled Windows Server のポータルページから、Azure File Sync のエージェントインストール・サーバー登録・同期構成までを 1 つのガイド付きワークフローで完結できるパブリックプレビュー機能です。既に Azure Arc でサーバー群を管理している組織にとって、ファイルサーバーのハイブリッド化や Azure Files への移行の導入障壁が大きく下がります。Linux 非対応やプレビュー段階である点に留意しつつ、まずは非本番環境の Arc-enabled Windows Server で、ガイド付き体験とクラウド階層化の効果を検証することを推奨します。

---

**タグ**: Azure File Sync, Azure Arc, Azure Files, Windows Server, Hybrid, Storage, Public Preview
