# Azure Functions: Durable Task Scheduler / Durable Task 関連アップデート (Ignite 2026)

**リリース日**: 2026-11-17

**サービス**: Azure Functions (Durable Task Scheduler / Durable Task)

**機能**: Task Queues (プレビュー)、Durable Task extension for Microsoft Agent Framework (GA)、プライベートエンドポイント (GA)、カスタマーマネージドキー (GA)、ネイティブディザスターリカバリー (プレビュー)、Durable Task SDK for Go (プレビュー)

**ステータス**: Launched (GA) / In preview (機能により異なる)

[このアップデートのインフォグラフィックを見る](https://takech9203.github.io/azure-news-summary/20261117-durable-task-scheduler-updates.html)

## 概要

Microsoft Ignite 2026 に合わせて、Azure Functions の Durable Task Scheduler および Durable Task 関連の 6 つのアップデートが発表されました。Durable Task Scheduler は、オーケストレーションの状態管理とワークディスパッチを担うマネージドバックエンドサービスで、Durable Functions と Durable Task SDK の推奨ストレージプロバイダーです。

GA (一般提供) となったのは、(1) C# / Python 向けの Durable Task extension for Microsoft Agent Framework、(2) プライベートエンドポイント (Dedicated / Consumption 両 SKU 対応)、(3) カスタマーマネージドキーによる保存データ暗号化 (Dedicated SKU) の 3 件です。パブリックプレビューとして、(4) タスクハブ内で名前付きキューを作成しディスパッチレートを制御できる Task Queues、(5) リージョン障害からオーケストレーション状態を復旧できるネイティブディザスターリカバリー (Dedicated SKU)、(6) Go 言語でオーケストレーションを記述できる Durable Task SDK for Go の 3 件が発表されました。

AI エージェントの長時間実行基盤としての信頼性 (Agent Framework 連携)、エンタープライズ要件 (閉域接続・暗号化キー管理・DR)、マルチ言語対応 (Go) と、Durable Task Scheduler を本番ワークロードで採用するための要素が一斉に強化されたアップデート群です。

**アップデート前の課題**

- Microsoft Agent Framework のエージェント / ワークフローは、LLM のレート制限、ネットワークタイムアウト、プロセス再起動などで中断すると、カスタムの復旧ロジックを実装しない限り状態を失うリスクがあった
- 同一タスクハブを共有するワークロード間でスループット要件や下流サービスの制限が異なっても、ディスパッチレートを個別に制御する手段がなかった
- リージョン障害時には、オーケストレーション状態を再構築するためのカスタム復旧エンジニアリングが必要だった
- スケジューラーへの接続はパブリックエンドポイント経由であり、閉域ネットワーク要件を持つ組織には採用の障壁があった (プレビュー段階では GA 要件を満たせなかった)
- ワークフローデータの暗号化キーを顧客自身で管理 (職務分離、ローテーションポリシー、アクセス監査) する手段が GA として提供されていなかった
- Durable Task SDK は Go 言語に対応していなかった

**アップデート後の改善**

- Agent Framework のエージェントセッション永続化とワークフロー進捗のチェックポイント保存が GA となり、障害後もカスタム復旧ロジックなしで自動再開できるようになった
- Task Queues により、タスクハブ内に名前付きキューを作成し、キューごとに共有ディスパッチレート (アクション/秒) を設定できるようになった
- ネイティブ DR (プレビュー) により、アクティブ・パッシブ構成で状態がペアリージョンへレプリケートされ、顧客主導のフェイルオーバーで永続チェックポイントから処理を再開できるようになった
- プライベートエンドポイントが GA となり、Private Link 経由のプライベート IP アドレスで接続し、パブリックネットワークアクセスを無効化できるようになった (コード変更不要)
- カスタマーマネージドキーが GA となり、Azure Key Vault / Managed HSM のキーでワークフローデータを保護できるようになった
- Durable Task SDK for Go (プレビュー) により、Go でオーケストレーション、アクティビティ、Durable Entities を記述できるようになった

## アーキテクチャ図

```mermaid
flowchart TD
    subgraph VNet["🔒 仮想ネットワーク"]
        APP["⚡ Azure Functions /<br>任意のコンピュート<br>(C#, Python, Go 🆕)"]
        AGENT["🤖 Microsoft Agent Framework<br>+ Durable Task extension (GA)"]
        PE["🔌 プライベートエンドポイント (GA)"]
    end
    subgraph Primary["☁️ プライマリリージョン"]
        DTS["🗓️ Durable Task Scheduler"]
        TH[("📦 タスクハブ<br>Task Queues 🆕 (プレビュー)")]
        KV["🔑 Key Vault / Managed HSM<br>カスタマーマネージドキー (GA)"]
    end
    subgraph Secondary["☁️ セカンダリリージョン"]
        DTS2["🗓️ パッシブスケジューラー"]
    end
    APP -->|gRPC| PE
    AGENT -->|状態の永続化| PE
    PE --> DTS
    DTS --> TH
    KV -.->|保存データ暗号化| DTS
    DTS -.->|状態レプリケーション<br>DR (プレビュー)| DTS2
```

アプリケーション (C# / Python / Go) はプライベートエンドポイント経由で Durable Task Scheduler に gRPC 接続し、タスクハブ内の Task Queues でディスパッチレートを制御できます。保存データはカスタマーマネージドキーで暗号化され、DR 構成ではオーケストレーション状態がセカンダリリージョンのパッシブスケジューラーへレプリケートされます。

## サービスアップデートの詳細

### 主要機能

1. **Task Queues (パブリックプレビュー)**
   - タスクハブ内に名前付きキューを作成し、オーケストレーション / アクティビティのワークに対して共有ディスパッチレート (アクション/秒) を設定できる
   - ワークフロー開始時に `DTS_TaskQueue` タグにキュー名を指定してキューを選択する
   - 関数名を変更せずに、ワークロードごとのペース調整や下流サービスの制限 (API レート制限など) に合わせたスループット予算の割り当てが可能
   - 注意: レート制御の対象はワークアイテムの「ディスパッチ」であり、実行の並行性 (コンカレンシー) は制御しない

2. **Durable Task extension for Microsoft Agent Framework (GA)**
   - C# と Python で一般提供開始。エージェント、マルチエージェントオーケストレーション、Agent Framework ワークフローを数分〜数週間にわたり確実に実行できる
   - エージェントセッションの永続化とワークフロー進捗のチェックポイントにより、LLM レート制限、ネットワークタイムアウト、プロセス再起動 / スケールイベント、インフラ障害の後も自動再開 (完了済み処理は保持され、会話コンテキストを失わずに別ワーカーで再開可能)
   - 永続的な会話履歴、決定論的なマルチエージェントオーケストレーション、Human-in-the-loop 待機、外部イベント対応、セッション TTL によるクリーンアップ、信頼性の高いストリーミング、ダッシュボードでの可視化を提供
   - ホスティングは Azure Functions (自動スケール + HTTP エンドポイント自動生成) または自前のコンピュート (コンテナー、Kubernetes など) の 2 モデル

3. **プライベートエンドポイント (GA)**
   - Dedicated / Consumption 両 SKU で一般提供。Azure Private Link 経由で仮想ネットワーク内のプライベート IP アドレスからスケジューラーに接続できる
   - トラフィックはパブリックインターネットを経由せず Microsoft バックボーンに留まる。パブリックネットワークアクセスを無効化し、承認済みプライベートエンドポイントのみを受け付ける構成が可能
   - 既存のエンドポイントと Microsoft Entra 認証モデルをそのまま利用するため、オーケストレーションコードの変更は不要。複数の仮想ネットワークを同一スケジューラーに接続可能
   - Azure portal、Azure CLI、Bicep で設定可能

4. **カスタマーマネージドキー (GA)**
   - Dedicated SKU で一般提供。Azure Key Vault または Azure Managed HSM に保管した顧客管理キーでワークフローデータ (保存時データ) を暗号化できる
   - 職務分離、キーアクセスの一元監査、顧客定義のキーローテーションポリシーといったコンプライアンス要件に対応
   - 構成は ARM REST API、Azure CLI (`az rest` 経由)、Bicep で行う

5. **ネイティブディザスターリカバリー (パブリックプレビュー)**
   - Dedicated SKU 対象。プライマリスケジューラーと別リージョンのパッシブなセカンダリスケジューラーをペアリングするアクティブ・パッシブ構成
   - オーケストレーション状態がペアスケジューラーへレプリケートされ、リージョン障害時に状態を再構築することなく復旧できる
   - フェイルオーバーは顧客主導 (DR ランブック経由で開始) で、処理は永続チェックポイントから再開される
   - 顧客側の責任: セカンダリリージョンへの互換ワーカー / コンピュート / ネットワーク / アプリ依存関係のデプロイ、トラフィックのリダイレクト、フェイルオーバーの開始。フェイルオーバー後、進行中の作業はリプレイまたは再実行される可能性がある

6. **Durable Task SDK for Go (パブリックプレビュー)**
   - Go でオーケストレーション、アクティビティ、Durable Entities を記述可能。実行履歴の管理とワークディスパッチは Durable Task Scheduler が担当
   - リトライ、タイマー、外部イベント、並列処理を利用したワークフローを構築できる
   - ワーカーは顧客自身のコンピュート環境 (コンテナー、Kubernetes、VM など) で実行可能

## 技術仕様

| 項目 | 詳細 |
|------|------|
| 対象サービス | Durable Task Scheduler (Microsoft.DurableTask/schedulers) |
| 接続方式 | gRPC (TLS)、エンドポイント形式: `{scheduler-name}.{region}.durabletask.io` |
| 認証 | Microsoft Entra ID + RBAC (プライベートエンドポイント利用時も変更なし) |
| Task Queues | タスクハブ内の名前付きキュー。`DTS_TaskQueue` タグで選択、共有ディスパッチレート (アクション/秒) を設定 |
| Agent Framework 拡張の対応言語 | C#、Python (GA) |
| Durable Task SDK の対応言語 | .NET、Python、Java、JavaScript に加え Go (プレビュー) が追加 |
| プライベートエンドポイント対応 SKU | Dedicated / Consumption 両対応 (GA) |
| CMK 対応 SKU | Dedicated のみ (GA)。キーは Azure Key Vault / Managed HSM に保管 |
| DR 対応 SKU | Dedicated のみ (プレビュー)。アクティブ・パッシブ、顧客主導フェイルオーバー |
| タスクハブ数上限 | Dedicated: 25 / スケジューラー、Consumption: 5 / スケジューラー |
| ペイロード上限 | オーケストレーター / アクティビティの入出力、外部イベント、エンティティ状態: 各 1 MB |

## 設定方法

### 前提条件

1. Durable Task Scheduler リソース (`Microsoft.DurableTask/schedulers`) が作成済みであること
2. CMK / DR を使う場合: Dedicated SKU のスケジューラーであること (CMK は加えて Azure Key Vault / Managed HSM とキーが必要)
3. プライベートエンドポイントを使う場合: 接続元の仮想ネットワークとサブネット
4. Agent Framework 拡張を使う場合: C# または Python の Microsoft Agent Framework プロジェクト

### Azure CLI

```bash
# Durable Task Scheduler が利用可能なリージョンの一覧を確認
az provider show --namespace Microsoft.DurableTask \
  --query "resourceTypes[?resourceType=='schedulers'].locations | [0]" --out table
```

プライベートエンドポイントは Azure portal / Azure CLI / Bicep で、カスタマーマネージドキーは ARM REST API / `az rest` / Bicep で構成します。各機能の具体的な手順は参考リンクのドキュメント (aka.ms 短縮リンク) を参照してください。

## メリット

### ビジネス面

- エンタープライズのセキュリティ / コンプライアンス要件 (閉域接続、顧客管理キー、監査、DR) を満たせるようになり、規制業界でも Durable Task Scheduler を採用しやすくなった
- AI エージェントワークロードの信頼性基盤が GA となり、本番環境での長時間実行エージェントの運用リスクを低減できる
- リージョン障害時の復旧手順が製品機能として提供され、カスタム復旧エンジニアリングのコストを削減できる

### 技術面

- Task Queues により、下流サービスのレート制限に合わせたワークロードごとのスループット制御がコード変更 (関数名変更) なしで可能
- 障害復旧 (リトライ、チェックポイント、状態レプリケーション) をアプリケーションコードから分離できる
- Go 対応により、既存の Go ベースのマイクロサービス / プラットフォームチームも Durable Task エコシステムに参加できる
- プライベートエンドポイントは既存の認証モデルを維持するため、移行時のコード変更が不要

## デメリット・制約事項

- Task Queues のレート制御はワークアイテムのディスパッチが対象であり、実行の並行性は制御しない
- カスタマーマネージドキーとネイティブ DR は Dedicated SKU 限定 (Consumption SKU では利用不可)
- CMK の構成は Azure CLI のネイティブコマンドではなく `az rest` (ARM REST API) を使う必要がある
- DR はプレビューであり、フェイルオーバーは自動ではなく顧客主導。セカンダリリージョンのコンピュート / ネットワークの準備とトラフィック切り替えは顧客の責任。フェイルオーバー後に進行中の作業がリプレイ / 再実行される可能性がある
- Task Queues、DR、Go SDK はパブリックプレビューであり、GA 日程は未定。本番利用時の SLA は GA 版と異なる可能性がある

## ユースケース

### ユースケース 1: 下流 API のレート制限に合わせたワークロード分離

**シナリオ**: 複数チームが同一タスクハブを共有しており、一方のワークロードは外部 SaaS API (例: 100 リクエスト/秒制限) を呼び出すため、他方の大量バッチ処理に巻き込まれてレート制限超過が発生している。

**実装**: タスクハブ内に「external-api」「batch」の名前付きキューを作成し、external-api キューにディスパッチレートを設定。ワークフロー開始時に `DTS_TaskQueue` タグでキューを指定する。

**効果**: 関数名の変更なしにワークロードごとのスループット予算を割り当てられ、下流サービスの制限超過を防止できる。

### ユースケース 2: 長時間実行のマルチエージェントオーケストレーション

**シナリオ**: 承認ワークフローを含むカスタマーサポートエージェントが、人間の応答を数日間待機する必要がある。従来はプロセス再起動で会話コンテキストが失われるリスクがあった。

**実装**: Durable Task extension for Microsoft Agent Framework (C# / Python) を導入し、Azure Functions または自前のコンテナー基盤でホストする。Human-in-the-loop 待機と外部イベントで承認を処理する。

**効果**: エージェントセッションが永続化され、スケールイベントやインフラ障害後も会話コンテキストを保持したまま別ワーカーで自動再開できる。

### ユースケース 3: 規制業界のミッションクリティカルワークフロー

**シナリオ**: 金融機関の決済オーケストレーションで、閉域接続・顧客管理キーによる暗号化・リージョン障害からの復旧手順が監査要件となっている。

**実装**: Dedicated SKU スケジューラーにプライベートエンドポイントと CMK (Key Vault / Managed HSM) を構成し、ネイティブ DR (プレビュー) でセカンダリリージョンのパッシブスケジューラーとペアリング。DR ランブックにフェイルオーバー手順を組み込む。

**効果**: パブリックインターネット非経由の接続、キーアクセスの一元監査、オーケストレーション状態を失わないリージョン障害復旧を実現できる。

## 料金

Durable Task Scheduler はオーケストレーションをホストするコンピュート (Azure Functions など) とは別に課金されます。

| SKU | 課金モデル | 性能・保持期間 |
|------|------|------|
| Dedicated | Capacity Unit (CU) ごとの月額固定 (リージョン別価格)。最大 3 CU | 1 CU あたり最大 2,000 アクション/秒・50 GB ストレージ。データ保持最大 90 日。高可用性は 3 CU 必要 |
| Consumption | ディスパッチされたアクション数による従量課金 (初期費用・最低コミットなし) | 最大 500 アクション/秒。データ保持最大 30 日 |

「アクション」はスケジューラーがアプリにディスパッチするメッセージ (オーケストレーション開始、アクティビティのスケジュールと結果処理、タイマー完了、外部イベントなど) の単位です。最新の価格は [Azure Functions 料金ページ](https://azure.microsoft.com/pricing/details/functions/) (Durable Task Scheduler の料金情報を含む) を参照してください。

## 利用可能リージョン

Durable Task Scheduler はほとんどの Azure リージョンで利用可能です。最新のリージョン一覧は次のコマンドで確認できます。

```bash
az provider show --namespace Microsoft.DurableTask \
  --query "resourceTypes[?resourceType=='schedulers'].locations | [0]" --out table
```

ネイティブ DR (プレビュー) は、サポート対象の Azure リージョンの Dedicated SKU で利用可能です。

## 関連サービス・機能

- **Azure Functions (Durable Functions)**: Durable Task Scheduler は Durable Functions の推奨ストレージプロバイダー。すべての Functions SKU で利用可能
- **Microsoft Agent Framework**: 今回 GA となった Durable Task 拡張により、エージェント / ワークフローの耐障害実行を実現
- **Azure Private Link**: プライベートエンドポイントの基盤。トラフィックを Microsoft バックボーン内に留める
- **Azure Key Vault / Managed HSM**: カスタマーマネージドキーの保管先
- **Azure Container Apps / AKS / App Service / VM**: Durable Task SDK (Go を含む) のワーカーをホストできるコンピュートプラットフォーム

## 参考リンク

- [インフォグラフィック](https://takech9203.github.io/azure-news-summary/20261117-durable-task-scheduler-updates.html)
- [公式アップデート情報: Task Queues (プレビュー)](https://azure.microsoft.com/updates?id=578989)
- [公式アップデート情報: Durable Task extension for Microsoft Agent Framework (GA)](https://azure.microsoft.com/updates?id=578829)
- [公式アップデート情報: プライベートエンドポイント (GA)](https://azure.microsoft.com/updates?id=578824)
- [公式アップデート情報: カスタマーマネージドキー (GA)](https://azure.microsoft.com/updates?id=578768)
- [公式アップデート情報: ネイティブディザスターリカバリー (プレビュー)](https://azure.microsoft.com/updates?id=578762)
- [公式アップデート情報: Durable Task SDK for Go (プレビュー)](https://azure.microsoft.com/updates?id=578748)
- [Microsoft Learn: Durable Task Scheduler 概要](https://learn.microsoft.com/azure/durable-task/scheduler/durable-task-scheduler)
- [Microsoft Learn: Durable Task Scheduler の課金](https://learn.microsoft.com/azure/durable-task/scheduler/durable-task-scheduler-billing)
- [Microsoft Learn: Durable Task extension for Microsoft Agent Framework](https://learn.microsoft.com/agent-framework/hosting/durable-extension)
- [ドキュメント: Task Queues](https://aka.ms/dts-task-queues)
- [ドキュメント: プライベートエンドポイント](https://aka.ms/dts-pe)
- [ドキュメント: カスタマーマネージドキー](https://aka.ms/dts-cmk)
- [ドキュメント: ディザスターリカバリー](https://aka.ms/dts-dr)
- [ドキュメント: Durable Task SDK for Go](https://aka.ms/durable-task-go)
- [料金ページ (Azure Functions)](https://azure.microsoft.com/pricing/details/functions/)

## まとめ

Ignite 2026 での Durable Task Scheduler 関連アップデートは、「AI エージェントの耐障害実行基盤の GA」「エンタープライズ要件 (閉域接続・CMK・DR) への対応」「Go 対応によるマルチ言語化」という 3 つの軸で、本番ワークロードでの採用障壁を大きく下げる内容です。Microsoft Agent Framework で長時間実行エージェントを構築しているチームは、GA となった Durable Task 拡張の導入を検討する価値があります。また、既に Durable Task Scheduler を利用中の組織は、プライベートエンドポイント (両 SKU) と CMK (Dedicated) でセキュリティ態勢を強化し、ミッションクリティカルなワークフローにはネイティブ DR プレビューの評価を開始することを推奨します。Task Queues と Go SDK はプレビューのため、非本番環境での検証から始めてください。

---

**タグ**: Azure Functions, Durable Task Scheduler, Durable Functions, Microsoft Agent Framework, AI エージェント, プライベートエンドポイント, カスタマーマネージドキー, ディザスターリカバリー, Go, Microsoft Ignite, GA, Public Preview
