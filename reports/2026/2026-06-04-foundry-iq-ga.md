# Microsoft Foundry IQ: Foundry IQ GA & ナレッジソース拡張

**リリース日**: 2026-06-04

**サービス**: Microsoft Foundry IQ

**機能**: Foundry IQ GA & ナレッジソース拡張

**ステータス**: Launched (GA) / In preview (mixed)

[このアップデートのインフォグラフィックを見る](https://takech9203.github.io/azure-news-summary/20260604-foundry-iq-ga.html)

## 概要

Microsoft Build 2026 に合わせて、Microsoft Foundry IQ が一般提供 (GA) に到達した。Foundry IQ は、エンタープライズデータに対してエージェントをグラウンディングするためのマネージド知識レイヤーであり、プロジェクトごとに検索パイプラインを再構築する必要がなくなる。チームは SharePoint、OneLake、Azure Blob などのソースを接続するだけで、Foundry IQ がインデックス作成、チャンキング、エンベディング、クエリ時の回答提供を自動的に処理する。

GA と同時に、Foundry IQ MCP サーバーも GA となり、任意の MCP 対応ホスト (Claude、ChatGPT、LangChain、Microsoft Agent Framework など) から Knowledge Base へのアクセスが標準化された。さらに、パブリックプレビューとして Fabric IQ Ontology (セマンティックレイヤーへのフェデレーテッドクエリ) と Azure SQL Database (ファーストクラスの Knowledge Source) が追加された。

公式ブログによると、Foundry IQ は single-shot RAG と比較してリコールを最大 54% 改善し、回答品質ベンチマークを最大 20% 向上させている。これらのアップデートにより、Foundry IQ を中核としたエージェント型 RAG (Retrieval-Augmented Generation) アーキテクチャの構築が大幅に簡素化され、対応データソースの幅が広がった。

**アップデート前の課題**

- エージェントごとに検索パイプライン (インデックス作成、チャンキング、エンベディング) を個別に構築・管理する必要があった
- Azure AI Search と Foundry サービス間の通信がパブリックエンドポイント経由に限定され、規制産業のセキュリティ要件を満たしにくかった
- エージェントフレームワーク間で知識ベースへのアクセス方法が標準化されておらず、フレームワークごとに個別の統合が必要だった
- Microsoft Fabric のセマンティックレイヤー (Ontology) にエージェントから直接アクセスする手段がなかった
- Azure SQL Database のデータを Knowledge Source として利用するには、カスタムの ETL パイプラインが必要だった

**アップデート後の改善**

- Foundry IQ が GA となり、マネージド Knowledge Base を通じて複数データソースの統合検索が即座に利用可能に
- Foundry IQ MCP サーバー (GA) により、Claude、ChatGPT、LangChain 等の MCP 対応ホストから標準プロトコルで接続可能に
- Fabric IQ Ontology を Remote Knowledge Source として接続し、自然言語からオントロジークエリへの変換が可能に
- Azure SQL Database が First-class Knowledge Source としてインデクサーパイプラインを自動生成
- サーバーレスデベロッパーティア (Preview) により、アイドル時はゼロにスケールし、従量課金でコスト最適化

## アーキテクチャ図

```mermaid
flowchart TD
    subgraph Agents["🤖 エージェント / クライアント"]
        direction LR
        A1["Copilot"]
        A2["Custom Agent"]
        A3["MCP Client\n(Claude, ChatGPT等)"]
    end

    subgraph FoundryIQ["☁️ Foundry IQ - マネージド知識レイヤー (GA)"]
        MCP["MCP Server (GA)\n標準プロトコル"]
        KB["Knowledge Base\nAgentic Retrieval"]
        LLM["LLM クエリプランナー\n(Azure OpenAI)"]
    end

    subgraph Search["🔍 Azure AI Search"]
        AR["マルチクエリパイプライン\n(並列サブクエリ実行)"]
        SR["Semantic Ranker\n(L2 リランキング)"]
    end

    subgraph IndexedSources["📦 Indexed Knowledge Sources"]
        Blob["Azure Blob Storage"]
        SP["SharePoint Online"]
        OL["OneLake"]
        SQL["Azure SQL Database\n⭐ NEW Preview"]
    end

    subgraph RemoteSources["🔗 Remote Knowledge Sources"]
        FO["Fabric IQ Ontology\n⭐ NEW Preview"]
        Web["Microsoft Web IQ"]
    end

    A1 & A2 -->|"Retrieve API"| KB
    A3 -->|"MCP プロトコル"| MCP
    MCP --> KB
    KB --> LLM
    LLM -->|"サブクエリ生成"| AR
    AR --> SR
    SR -->|"ランク付き結果"| KB
    AR -->|"インデックス検索"| IndexedSources
    AR -->|"フェデレーテッドクエリ"| RemoteSources
    KB -->|"グラウンディング回答\n+ 引用情報"| Agents
```

Foundry IQ はエージェントとエンタープライズデータの間に位置するマネージド知識レイヤーである。Knowledge Base が LLM を活用してクエリを分解し、Azure AI Search 上で並列実行する。Indexed Knowledge Source (Blob, SharePoint, OneLake, Azure SQL) はデータをインデックスに取り込み、Remote Knowledge Source (Fabric Ontology, Web IQ) はリアルタイムのフェデレーテッドクエリを実行する。

## サービスアップデートの詳細

### 1. Microsoft Foundry IQ - 一般提供 (GA)

Foundry IQ は Microsoft Foundry ポータル上で提供されるマネージド知識レイヤーである。Azure AI Search の Agentic Retrieval 機能を基盤としており、Knowledge Base と Knowledge Source のオーケストレーションを自動化する。開発者はプロジェクトごとに検索パイプラインを再構築する必要がなくなり、SharePoint、OneLake、Azure Blob、その他のソースを接続するだけで利用可能になる。

**主要機能:**
- **マルチソース統合**: SharePoint、OneLake、Azure Blob Storage など複数のデータソースを単一の Knowledge Base に統合
- **自動パイプライン生成**: データソースの接続設定だけでインデクサー、スキルセット、インデックスを自動生成
- **Agentic Retrieval**: LLM を活用したクエリ分解・並列実行・セマンティック再ランキングによる高精度検索
- **会話コンテキスト対応**: チャット履歴を入力として受け取り、文脈を考慮したサブクエリを生成
- **Foundry IQ MCP サーバー (GA)**: Knowledge Base をリモート Model Context Protocol (MCP) サーバーとして公開。Claude、ChatGPT、LangChain、Microsoft Agent Framework など任意の MCP 対応ホストから接続可能
- **サーバーサイドトークンキャッシュ**: マルチターン会話における冗長なトークン消費を削減

**パフォーマンスベンチマーク (公式ブログより):**
- Single-shot RAG と比較してリコールを最大 **54%** 改善
- 評価データセット全体で回答品質を最大 **20%** 向上
- サーバーサイドトークンキャッシュにより、回答品質を犠牲にせずトークン消費を削減

**GA に含まれる機能:**
- Knowledge Base (Agentic Retrieval)
- 出力・アクティビティログ
- Foundry IQ MCP サーバー
- エンタープライズグレードのネットワーク分離 (ID とポリシーによる強制)
- フル SLA カバレッジとコンプライアンス認定
- 安定 API (2026-04-01 REST API)
- Private Connectivity (Shared Private Link / Network Security Perimeter)
- マネージド ID サポート

**技術的背景:**

Foundry IQ は Azure AI Search の Knowledge Base / Knowledge Source API (2026-04-01 GA REST API) を使用する。エージェントは Knowledge Base に対して Retrieve アクションを呼び出し、以下の 3 部構成の応答を受け取る:
1. グラウンディングデータ (マージされたコンテンツ)
2. ソース参照 (引用情報)
3. 実行詳細 (クエリプランと実行ステップ)

### 2. Fabric IQ Ontology Knowledge Source - パブリックプレビュー

Microsoft Fabric の Ontology を Remote Knowledge Source としてフェデレーテッドクエリが可能になった。Foundry IQ は自然言語の質問をオントロジークエリに変換し、顧客が Fabric 上で既にキュレーションしているセマンティックレイヤーをエージェントが直接クエリできるようにする。

**主要機能:**
- **セマンティックレイヤーへの直接アクセス**: Fabric Ontology で定義されたエンティティ、関係性、ルールをエージェントがクエリ時に参照
- **自然言語からオントロジークエリへの変換**: Foundry IQ がユーザーの質問を解釈し、適切なオントロジークエリを生成
- **Remote Knowledge Source**: データのインデックス化不要。Fabric 側のメタデータ・定義を OneLake 内のライブデータと連携してリアルタイムでクエリ
- **エンティティベースの回答**: ビジネス用語やメトリクスの定義をセマンティックレイヤーから取得し、一貫性のある回答を生成
- **Fabric Data Agent との連携**: Ontology は Fabric の正式なビジネスエンティティ・関係性・ルールのモデル

**API**: `fabricOntology` (2026-05-01-preview REST API)

### 3. Azure SQL Database as Knowledge Source - パブリックプレビュー

Azure SQL Database が Azure AI Search の First-class Knowledge Source として追加された。エンタープライズ開発者やソリューションアーキテクトは、Copilot、RAG、エージェンティック体験の構築において、権威あるテーブルやビューを直接公開できるようになった。

**主要機能:**
- **自動インデクサーパイプライン生成**: Azure SQL のテーブルまたはビューからデータを取得し、チャンキング・インデックス化を自動実行
- **Indexed Knowledge Source**: SQL データが検索インデックスに取り込まれ、Full-text / Vector / Hybrid 検索に対応
- **スキーマ活用**: テーブル・ビューの構造を活かした効率的なデータ抽出
- **権威あるデータソースの公開**: 既存の SQL Database のマスタデータやトランザクションデータをエージェントの知識源として直接活用

**API**: `indexedSql` (2026-05-01-preview REST API)

## 技術仕様

| 項目 | 詳細 |
|------|------|
| GA REST API | 2026-04-01 (Knowledge Base / Knowledge Source の基本機能) |
| Preview REST API | 2026-05-01-preview (Fabric Ontology, Azure SQL 等) |
| Foundry IQ ステータス | 一般提供 (GA) |
| Foundry IQ MCP サーバー | 一般提供 (GA) |
| Private Connectivity | 一般提供 (GA) - Shared Private Link / Network Security Perimeter |
| Fabric IQ Ontology | パブリックプレビュー (Remote Knowledge Source) |
| Azure SQL Knowledge Source | パブリックプレビュー (Indexed Knowledge Source) |
| サーバーレスデベロッパーティア | パブリックプレビュー |
| 暗号化 | TLS 1.2/1.3、AES-256 保存時暗号化 |
| 認証 | Microsoft Entra ID、マネージド ID、API キー |
| リコール改善 | Single-shot RAG 比で最大 54% 向上 |
| 回答品質改善 | ベンチマーク全体で最大 20% 向上 |
| MCP 対応ホスト | Claude, ChatGPT, LangChain, Microsoft Agent Framework 等 |

### サーバーレスデベロッパーティア (Preview)

| 項目 | 制限 |
|------|------|
| コンピュート使用量 | $0.24 CU/時間 |
| インデックスストレージ | 最大 $0.29 GB/月 (リージョン依存) |
| インデックスあたりストレージ | 1 GB/インデックス |
| サービスあたりインデックス数 | 30 インデックス/サービス |
| サブスクリプション/リージョンあたりサービス数 | 5 サービス |

## メリット

### ビジネス面

- **開発期間の短縮**: プロジェクトごとに RAG パイプラインを構築する必要がなくなり、エージェント開発のリードタイムが大幅に短縮
- **データ活用範囲の拡大**: SQL Database、Fabric Ontology など既存のエンタープライズデータ資産をそのままエージェントの知識源として活用可能
- **コンプライアンス対応の容易化**: Private Link による閉域接続が GA したことで、規制産業での導入障壁が低下
- **運用コスト削減**: マネージドサービスとしてのインデクサーパイプライン自動生成により、インフラ管理負荷を削減

### 技術面

- **マルチソース統合検索**: 単一の Knowledge Base に対するクエリで、Blob、SharePoint、SQL、Fabric など異なるソースの情報を横断的に取得
- **LLM によるクエリ最適化**: Agentic Retrieval のクエリ分解・並列実行により、複合的な質問に対する検索精度が向上
- **セマンティックレイヤー活用**: Fabric Ontology 接続により、ビジネスメトリクスの定義やエンティティ関係をエージェントが直接参照可能
- **画像コンテンツの検索可能化**: Content Understanding による画像言語化で、図表やダイアグラムの内容もテキスト検索の対象に

## デメリット・制約事項

- **プレビュー機能の SLA 制限**: Fabric Ontology、Azure SQL、Content Understanding は パブリックプレビューのため、SLA の提供なし。本番ワークロードへの適用は非推奨
- **リージョン制限**: Agentic Retrieval は対応リージョンが限定されている (詳細は[リージョンサポートページ](https://learn.microsoft.com/azure/search/search-region-support)を参照)
- **LLM 依存のコスト**: Agentic Retrieval はクエリプランニングに LLM (Azure OpenAI) を使用するため、検索コストに加え Azure OpenAI のトークンコストが発生
- **Preview API の変更リスク**: 2026-05-01-preview API の仕様は GA までに変更される可能性がある

## ユースケース

### ユースケース 1: 企業内ナレッジエージェント

**シナリオ**: 大企業で社内ドキュメント (SharePoint)、データウェアハウス (Fabric)、業務データベース (Azure SQL) に分散した情報をエージェントが統合的に検索し、従業員の質問に回答する。

**構成**:
- Foundry IQ Knowledge Base に以下の Knowledge Source を登録:
  - SharePoint (Indexed): 社内ドキュメント
  - Fabric Ontology (Remote): ビジネスメトリクスの定義
  - Azure SQL (Indexed): 業務データ
- Private Link で閉域接続を確保

**効果**: 従業員は単一のチャットインターフェースから、分散した全社データへ安全にアクセス可能。Agentic Retrieval のクエリ分解により、「先月の売上が目標を下回った部門の改善提案書を探して」のような複合的な質問にも正確に対応。

### ユースケース 2: 規制産業向けマルチモーダル文書検索

**シナリオ**: 製薬企業で研究レポート (PDF、図表含む) を Azure Blob Storage に格納し、Content Understanding による画像言語化を活用して図表の内容も含めた包括的な検索を実現する。

**構成**:
- Blob Storage Knowledge Source + Content Understanding チャンキング
- 画像言語化により、グラフや構造式の内容をテキストとしてインデックス
- Private Connectivity で GxP 準拠のネットワーク構成

**効果**: 研究者が「Phase III 試験の有効性グラフで 95% 信頼区間が狭い結果」のようなクエリを実行すると、図表の内容を含むドキュメントも検索結果に含まれる。

## 料金

Foundry IQ の料金体系は 2 つのオプションがある。

### 従来型 (プロビジョニング型)

| 課金対象 | 課金方式 | 備考 |
|---------|---------|------|
| Azure AI Search (Agentic Retrieval) | トークンベース (サブクエリ実行 + セマンティックランキング) | 無料枠あり (月次トークン割当)。超過分は従量課金 |
| Azure OpenAI (クエリプランニング) | 入出力トークン従量課金 | 使用モデルに依存 (例: gpt-4o-mini) |

### サーバーレスデベロッパーティア (Preview)

| 項目 | 料金 |
|------|------|
| コンピュート使用量 | $0.24 CU/時間 |
| インデックスストレージ | 最大 $0.29 GB/月 (リージョン依存) |

- クラスター管理不要、キャパシティ予約不要
- アイドル時はゼロにスケール
- CU (Compute Unit): CPU 使用率、メモリ、ストレージ I/O を含むリソース消費量の単位
- 毎分 0.25 CU 刻みで計算
- **課金開始は 2026 年後半を予定** (開始の 30 日以上前に通知)

### コスト見積例 (Microsoft Learn ドキュメントに基づく)

2,000 回の Agentic Retrieval 実行 (平均 3 サブクエリ/回):
- Azure AI Search: 約 $3.30 (リランキング)
- Azure OpenAI 入力: 約 $0.60 (クエリプランニング)
- Azure OpenAI 出力: 約 $0.42
- **合計: 約 $4.32**

詳細な料金は以下を参照:
- [Azure AI Search 料金](https://azure.microsoft.com/pricing/details/search)
- [Azure OpenAI 料金](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/#pricing)

## 利用可能リージョン

Agentic Retrieval (Foundry IQ のバックエンド) は対応リージョンが限定されている。最新のリージョンサポート状況は以下を参照:

- [Azure AI Search リージョンサポート](https://learn.microsoft.com/azure/search/search-region-support)

## 関連サービス・機能

- **Azure AI Search**: Foundry IQ のバックエンドとして Agentic Retrieval エンジンを提供。Knowledge Base / Knowledge Source の管理を担当
- **Microsoft Foundry Agent Service**: Foundry IQ と連携してエージェントにグラウンディングデータを提供。Hosted Agents との組み合わせでエンドツーエンドのエージェントソリューションを構築
- **Microsoft Fabric**: Ontology Knowledge Source により、Fabric のセマンティックレイヤー (エンティティ、関係性、ルール) をエージェントの知識源として活用。OneLake 内のライブデータと連携
- **Azure SQL Database**: First-class Knowledge Source として、既存のリレーショナルデータを Copilot / RAG / エージェンティック体験に直接公開
- **Azure OpenAI**: Agentic Retrieval のクエリプランニングと回答合成に使用される LLM を提供
- **Model Context Protocol (MCP)**: Foundry IQ MCP サーバーにより、任意の MCP 対応ホストからの標準化されたアクセスを実現

## 参考リンク

- [インフォグラフィック](https://takech9203.github.io/azure-news-summary/20260604-foundry-iq-ga.html)
- [公式アップデート: Foundry IQ GA](https://azure.microsoft.com/updates?id=563222)
- [公式アップデート: Fabric IQ Ontology](https://azure.microsoft.com/updates?id=563416)
- [公式アップデート: Azure SQL Knowledge Source](https://azure.microsoft.com/updates?id=563446)
- [Azure Blog: Foundry IQ - Build smarter agents faster with unified knowledge and serverless retrieval](https://devblogs.microsoft.com/foundry/build-smarter-agents-faster-with-foundry-iq/)
- [Microsoft Learn - Agentic Retrieval 概要](https://learn.microsoft.com/azure/search/agentic-retrieval-overview)
- [Microsoft Learn - Knowledge Source 概要](https://learn.microsoft.com/azure/search/agentic-knowledge-source-overview)
- [Foundry IQ ポータル](https://ai.azure.com/nextgen/goto/build/knowledge)
- [Azure AI Search 料金](https://azure.microsoft.com/pricing/details/search)

## まとめ

Microsoft Foundry IQ の GA 到達は、エージェント型 AI アプリケーション開発における大きなマイルストーンである。これまでプロジェクトごとに構築が必要だった RAG パイプラインがマネージドサービスとして提供されることで、開発チームはデータの接続設定に集中でき、インフラの構築・運用から解放される。「一度構築すれば、どこでも再利用」というパターンにより、複数のエージェントが同一の Knowledge Base を共有できる。

MCP サーバーの GA により、Foundry IQ は特定のフレームワークに依存しないオープンな知識レイヤーとなった。Claude、ChatGPT、LangChain など MCP 対応クライアントから標準プロトコルで接続でき、エージェント開発のエコシステムが拡大する。

新たにプレビューで追加された Fabric IQ Ontology と Azure SQL の Knowledge Source は、エージェントがアクセスできるデータの幅を大幅に広げる。特に Fabric Ontology によるセマンティックレイヤーへのアクセスは、ビジネスインテリジェンスと AI エージェントの融合を加速し、自然言語でビジネスメトリクスを問い合わせる体験を実現する。

**推奨アクション:**
1. 既存の RAG パイプラインを Foundry IQ への移行を検討する (特に複数データソースを扱うプロジェクト)
2. MCP サーバー経由の接続を評価し、エージェントフレームワークの選択肢を広げる
3. Fabric Ontology や Azure SQL の Knowledge Source はプレビュー段階のため、開発・検証環境での評価を開始する
4. サーバーレスデベロッパーティアを PoC や小規模プロジェクトで試用し、コスト感を把握する

---

**タグ**: #Microsoft-Foundry #Foundry-IQ #Azure-AI-Search #Agentic-Retrieval #Knowledge-Base #MCP #Fabric-Ontology #Azure-SQL #GA #Build2026
