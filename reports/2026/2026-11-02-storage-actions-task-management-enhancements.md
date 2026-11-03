# Azure Storage Actions: タスク定義の自動反映・実行制御・大文字小文字を区別するマッチングが一般提供開始

**リリース日**: 2026-11-02

**サービス**: Azure Storage Actions

**機能**: タスク定義の自動反映、実行制御 (停止)、大文字小文字を区別するマッチング

**ステータス**: Launched (GA)

[このアップデートのインフォグラフィックを見る](https://takech9203.github.io/azure-news-summary/20261102-storage-actions-task-management-enhancements.html)

## 概要

Azure Storage Actions に、タスク管理を簡素化し、自動化されたデータ操作をより細かく制御するための 3 つの機能強化が一般提供 (GA) されました。Azure Storage Actions は、Azure Blob Storage と Azure Data Lake Storage 上の数百万オブジェクトに対して、コードを書かずにデータ管理タスク (階層移動、保持管理、インデックスタグ操作など) を自動実行できるフルマネージドプラットフォームです。

今回のアップデートでは、(1) ストレージタスク定義を更新すると既存のすべてのタスク割り当て (アサインメント) に変更が自動反映される機能、(2) 実行中のタスク割り当ての実行 (run) を停止できる実行制御機能、(3) 文字列比較で大文字小文字を区別する新しい演算子 (`_cs` サフィックス付き) の 3 点が追加されました。いずれも Preview を経ずに直接 GA としてリリースされています。

**アップデート前の課題**

- タスク定義 (条件・操作) を変更した場合、変更を反映するにはタスク割り当てを個別に更新する必要があり、多数のストレージアカウントにタスクを割り当てている場合に運用負荷が高かった
- 実行中のタスク割り当ての実行を途中で止める手段が提供されておらず、誤った条件で開始された大規模な処理をコントロールしにくかった
- 文字列演算子 (`equals`、`contains`、`startsWith`、`endsWith`、`matches`) は大文字小文字を区別しない動作のみで、大文字小文字が意味を持つ Blob 命名規則に対する厳密なターゲティングができなかった

**アップデート後の改善**

- タスク定義の更新がすべての既存割り当てに自動的に伝播し、スケジュール実行は次回実行時に更新後の定義を使用するため、割り当てを削除・再作成する必要がなくなった
- 単一のタスク割り当て、またはストレージタスクに紐づくすべての割り当てについて、進行中の実行を停止できるようになった (停止リクエストは非同期で処理される)
- `equals_cs`、`contains_cs`、`startsWith_cs`、`endsWith_cs`、`matches_cs` という大文字小文字を区別する演算子が追加され、従来の演算子は従来どおり大文字小文字を区別しない動作を維持

## アーキテクチャ図

```mermaid
flowchart TD
    Admin([👤 管理者]) -->|① 定義を更新| Task["📋 ストレージタスク定義<br>(条件 + 操作)"]
    Admin -->|② 停止リクエスト<br>(非同期処理)| Runs["▶️ 実行中の Run"]
    Task -->|自動反映<br>(次回実行から適用)| A1["🔗 タスク割り当て 1"]
    Task -->|自動反映| A2["🔗 タスク割り当て 2"]
    A1 --> Runs
    subgraph Target["☁️ ターゲットストレージ"]
        B1[("🗄️ Blob Storage")]
        B2[("🗄️ Data Lake Storage")]
    end
    A1 -->|"条件評価<br>(equals_cs / endsWith_cs など)"| B1
    A2 -->|条件評価 + 操作| B2
```

タスク定義の更新は紐づくすべての割り当てに自動反映され、各割り当ての次回実行から適用されます。実行中の run は管理者が非同期の停止リクエストで中断できます。

## サービスアップデートの詳細

### 主要機能

1. **タスク定義更新の自動反映 (Automatic propagation of task definition updates)**
   - ストレージタスクの条件や操作を更新すると、システムが関連するすべてのタスク割り当てに定義を自動的に伝播する
   - 割り当てを削除・再作成する必要がなく、スケジュールされたタスク割り当ては次回実行時に更新後の定義を使用する
   - すでに実行キューに入っている、または実行中の run は更新されず、古い定義のまま実行される

2. **進行中のタスク割り当て実行の停止 (Stop in-progress task assignment runs)**
   - 単一のタスク割り当ての run、またはストレージタスクに紐づくすべての割り当ての run を停止できる
   - 停止リクエストは非同期で処理される
   - Mock run (シミュレーション実行) についても進行中のインスタンスを停止可能 (再実行には新しいタスク割り当ての作成が必要)

3. **大文字小文字を区別する演算子 (Case-sensitive operators)**
   - 文字列演算子 `equals`、`contains`、`startsWith`、`endsWith`、`matches` に、大文字小文字を区別するバージョン (`equals_cs`、`contains_cs`、`startsWith_cs`、`endsWith_cs`、`matches_cs`) が追加
   - 例: `endsWith(Name, '.CSV')` は `report.CSV` と `report.csv` の両方にマッチするが、`endsWith_cs(Name, '.CSV')` は `report.CSV` のみにマッチする
   - 従来の演算子は従来どおり大文字小文字を区別しない動作を維持 (後方互換性あり)

## 技術仕様

| 項目 | 詳細 |
|------|------|
| 対象サービス | Azure Blob Storage、Azure Data Lake Storage |
| 定義更新の反映タイミング | 次回のスケジュール実行から適用 (キュー済み・実行中の run は旧定義で実行) |
| 停止リクエストの処理 | 非同期 |
| 大文字小文字を区別する演算子 | `equals_cs`、`contains_cs`、`startsWith_cs`、`endsWith_cs`、`matches_cs` |
| `_cs` 演算子の制限 | `matches` / `matches_cs` は `Metadata.Value[Name]` と `Tags.Value[Name]` プロパティでは未サポート。`empty` 演算子に `_cs` 版はない |
| 対象外アカウント | 汎用 v1 (GPv1) およびレガシー Blob Storage アカウントはタスク割り当てのターゲットにできない (GPv2 への移行を推奨) |
| Preview 期間 | なし (直接 GA) |

## 設定方法

### 前提条件

1. ストレージタスクのマネージド ID (システム割り当てまたはユーザー割り当て) に、ターゲットストレージアカウントで操作を実行するために必要な Azure ロールを割り当てる
2. ターゲットストレージアカウントのネットワーク設定で「信頼された Azure サービスへのアクセス」を許可する
3. ターゲットは汎用 v2 (GPv2) ストレージアカウントであること

### 条件定義の例 (大文字小文字を区別する演算子)

条件は Azure Portal のビジュアルデザイナーで作成でき、[Code] タブから JSON 式を確認できます。REST、SDK、PowerShell、Azure CLI、Bicep、Terraform、ARM テンプレートでも定義可能です。

```json
{
   "condition": "[[endsWith_cs(Name, '.CSV')]]"
}
```

上記の条件は、大文字の拡張子 `.CSV` を持つ Blob のみを対象とします (`report.csv` は対象外)。

## メリット

### ビジネス面

- 多数のストレージアカウントにまたがる共有タスクの変更管理が簡素化され、運用コストが低減する
- 誤った設定による大規模なデータ操作を途中で停止できるため、意図しない処理のリスクを抑制できる

### 技術面

- タスク割り当ての削除・再作成が不要になり、定義変更のワークフローが単純化される
- 大文字小文字を区別する命名規則を持つデータセットに対して、より厳密な Blob ターゲティングが可能になる
- 既存の演算子の動作は変わらないため、既存のタスク定義への影響なしに導入できる

## デメリット・制約事項

- すでにキューに入っている、または実行中の run には定義更新が反映されず、旧定義で実行される
- 共有タスクの変更は複数ストレージアカウントの処理に影響するため、更新前に参照している割り当てのレビューが必要。操作を追加する変更の場合、タスクのマネージド ID が各ターゲットでその操作に必要な権限を持つか確認が必要
- `matches_cs` は `Metadata.Value[Name]` と `Tags.Value[Name]` プロパティでは使用できない
- 停止した run を再実行するには、run-once / mock run の場合は新しいタスク割り当ての作成が必要

## ユースケース

### ユースケース 1: 共有タスクの保持ポリシー変更を全アカウントへ一括反映

**シナリオ**: 複数のストレージアカウントに同一のストレージタスク (例: 古い Blob のアーカイブ階層への移動) を割り当てている環境で、保持期間の条件を変更したい。

**実装例**: タスク定義の条件 (例: `Creation-Time` のしきい値) を更新するだけで、すべての割り当てに自動反映され、各割り当ての次回スケジュール実行から新しい条件が適用される。

**効果**: 割り当てごとの個別更新や削除・再作成が不要になり、ポリシー変更の適用漏れを防止できる。

### ユースケース 2: 大文字小文字を区別するファイル命名規則への厳密な一致

**シナリオ**: 大文字の拡張子 (`.CSV`) を持つレガシーシステム出力ファイルのみを対象にクリーンアップ処理を行いたい。小文字の `.csv` ファイルは対象外にする必要がある。

**実装例**:

```json
{
   "condition": "[[endsWith_cs(Name, '.CSV')]]"
}
```

**効果**: 従来の大文字小文字を区別しないマッチングでは不可能だった、命名規則に基づく厳密なターゲティングが実現できる。

### ユースケース 3: 誤設定されたタスク実行の緊急停止

**シナリオ**: 条件設定に誤りのあるタスク割り当てが大量のオブジェクトに対して実行を開始してしまった。

**実装例**: 単一のタスク割り当て、またはストレージタスクに紐づくすべての割り当てについて、進行中の run に停止リクエストを発行する (非同期で処理される)。

**効果**: 意図しないデータ操作の範囲を最小限に抑えられる。なお、事前検証には Mock run (データを変更せずに条件評価とレポート生成のみ行う実行) の活用も有効。

## 料金

Azure Storage Actions の料金はタスク割り当ての実行に基づく従量課金で、以下の 3 つのメーターで構成されます (今回の機能追加自体による追加料金の情報はありません)。

| 項目 | 課金単位 |
|------|------|
| タスク実行インスタンス | 実行 1 回ごと |
| オブジェクトのスキャン・条件評価 | スキャンされたオブジェクト 100 万件あたり |
| オブジェクトへの操作 | 操作されたオブジェクト 100 万件あたり |

繰り返し実行するタスク割り当ては、実行インスタンスごとに課金されます。具体的な単価は [Azure Storage Actions の料金ページ](https://azure.microsoft.com/pricing/details/storage-actions/) を参照してください。

## 利用可能リージョン

Azure Storage Actions は以下を含むパブリッククラウドの 48 リージョンで一般提供されています (日本では Japan East / Japan West が利用可能)。

East US、East US 2、West US、West US 2、West US 3、Central US、North Central US、South Central US、West Central US、Canada Central、Canada East、Brazil South、Brazil Southeast、Mexico Central、North Europe、West Europe、UK South、UK West、France Central、Germany North、Germany West Central、Switzerland North、Switzerland West、Norway East、Norway West、Sweden Central、Sweden South、Spain Central、Italy North、Israel Central、UAE Central、UAE North、South Africa North、South Africa West、Japan East、Japan West、Korea Central、Korea South、East Asia、Southeast Asia、Central India、South India、West India、Jio India Central、Jio India West、Australia Central、Australia East、Australia Southeast

## 関連サービス・機能

- **Azure Blob Storage**: Storage Actions のタスクが条件評価・操作を実行する主要なターゲットサービス
- **Azure Data Lake Storage**: 階層型名前空間を持つストレージもターゲットとして対応 (ただし Blob インデックスタグは利用不可)
- **Azure Event Grid**: タスク実行の完了などの Storage Actions イベントを Azure Functions、Logic Apps、独自の HTTP リスナーなどへ配信可能
- **Blob Storage ライフサイクル管理**: 階層移動・削除の自動化という点で補完関係にあり、Storage Actions はより柔軟な条件 (メタデータ、タグ、名前など) と操作を提供

## 参考リンク

- [インフォグラフィック](https://takech9203.github.io/azure-news-summary/20261102-storage-actions-task-management-enhancements.html)
- [公式アップデート情報](https://azure.microsoft.com/updates?id=578628)
- [Azure Storage Actions 概要 (Microsoft Learn)](https://learn.microsoft.com/azure/storage-actions/overview)
- [ストレージタスクの条件 (Microsoft Learn)](https://learn.microsoft.com/azure/storage-actions/storage-tasks/storage-task-conditions)
- [ストレージタスクの割り当て (Microsoft Learn)](https://learn.microsoft.com/azure/storage-actions/storage-tasks/storage-task-assignment)
- [料金ページ](https://azure.microsoft.com/pricing/details/storage-actions/)

## まとめ

今回の GA により、Azure Storage Actions の運用性が大きく向上しました。特にタスク定義更新の自動反映は、多数のストレージアカウントに共有タスクを割り当てる大規模環境での変更管理を大幅に簡素化します。実行中の run の停止機能は誤設定時のセーフティネットとして機能し、大文字小文字を区別する演算子は厳密な命名規則を持つデータセットへの正確なターゲティングを可能にします。

Storage Actions を利用中の Solutions Architect は、(1) 共有タスクの変更が自動反映されるようになったことを踏まえた変更管理プロセスの見直し (変更前の割り当てレビュー、マネージド ID の権限確認)、(2) 誤設定リスク低減のための Mock run と停止機能を組み込んだ運用手順の整備、を推奨します。

---

**タグ**: Azure Storage Actions, Azure Blob Storage, Azure Data Lake Storage, Storage, GA, 自動化, データ管理
