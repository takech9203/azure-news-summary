# Azure News インフォグラフィックテーマ

Azure ニュースレポート専用のインフォグラフィックテーマ。Azure ライトテーマ (#[[file:azure-light.md]]) をベースに、Azure サービスアップデートの情報をシングルカラムレイアウトで視覚的に表現します。

## ベーステーマ

このテーマは Azure ライトテーマを継承します。

**参照**: #[[file:azure-light.md]]

- カラーパレット: Microsoft Azure 公式ブランドカラー (White 背景, Azure Blue アクセントなど)
- フォント: Noto Sans JP
- 基本コンポーネント: カード、ハイライト、フロー図など
- レイアウト: シングルカラム、最大幅 1000px (レスポンシブ対応)

## 適用条件

以下の場合にこのテーマを使用します。

- `reports/` フォルダ内の Azure ニュースレポート (.md) からインフォグラフィックを生成する場合
- ユーザーが「Azure ニュースのインフォグラフィック」「レポートを視覚化」などと言った場合

## ファイル名規則

- **形式**: `{YYYYMMDD}-{slug}.html`
- **slug**: レポートファイル名から日付部分を除いた部分を使用
- **例**: `reports/2026/2026-03-01-app-service-update.md` → `infographic/20260301-app-service-update.html`
- **出力先**: `infographic/` フォルダ

## 情報収集

インフォグラフィック作成時は、レポートの情報だけでなく、Web から関連情報を積極的に収集して内容を充実させる。

### 必須の情報源

1. **Azure News レポート** (`reports/` フォルダ)
   - 基本情報、概要、主要機能、ユースケース

2. **Microsoft Learn ドキュメント**
   - Web 検索で `site:learn.microsoft.com/azure {サービス名}` で詳細情報を検索
   - 公式ドキュメントページを読み込み

3. **Azure Blog**
   - 関連する Blog 記事から追加のユースケースや詳細情報を取得

### 推奨の情報源

4. **GitHub サンプルコード** (直接関連するもののみ)
   - `Azure-Samples`: https://github.com/Azure-Samples
   - `Azure`: https://github.com/Azure
   - Web 検索で `site:github.com/Azure {サービス名}` などで検索

5. **Azure Architecture Center**
   - 関連するアーキテクチャパターンやベストプラクティス

## コンテンツ構成

### 必須セクション (この順序で配置)

1. **タイトルエリア**: サービス名、機能名、リリース日
2. **概要セクション**: 要点 + Before/After 比較
3. **アーキテクチャ図**: フロー図、構成図
4. **主要機能セクション**: 3-5 個の機能カード
5. **ユースケースセクション**: 2-3 個のユースケース
6. **フッター**: 出典 URL

### 推奨セクション (情報がある場合は積極的に追加)

- **統計情報**: 数字で見るアップデート効果
- **サンプルコード**: GitHub へのリンク、コードスニペット
- **リージョン情報**: 利用可能リージョン
- **関連リソース**: Blog、ドキュメントへのリンク
- **料金情報**: コスト比較、料金例
- **制限事項・注意点**: 知っておくべき制約
- **関連サービス**: 組み合わせて使うと効果的なサービス

## Azure News 専用コンポーネント

### Before/After 比較

アップデート前後の変化を視覚的に表現。赤 (Before) と緑 (After) で対比。

```html
<div class="before-after">
    <div class="before">
        <h4>❌ Before</h4>
        <ul>
            <li>課題 1</li>
            <li>課題 2</li>
        </ul>
    </div>
    <div class="after">
        <h4>✅ After</h4>
        <ul>
            <li>改善 1</li>
            <li>改善 2</li>
        </ul>
    </div>
</div>
```

### サービスバッジ

Azure Blue 背景でサービス名を表示。

```html
<span class="service-badge">Azure App Service</span>
```

```css
.service-badge {
    background: var(--azure-blue);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
}
```

### ステータスバッジ

```html
<span class="badge badge-ga">Launched (GA)</span>
<span class="badge badge-preview">In Preview</span>
<span class="badge badge-development">In Development</span>
```

### 機能カード

```html
<div class="feature-card">
    <div class="feature-icon">⚡</div>
    <div class="feature-content">
        <h4>機能名</h4>
        <p>機能の説明</p>
    </div>
</div>
```

```css
.feature-card {
    display: flex;
    gap: 16px;
    background: var(--ms-surface);
    border-left: 4px solid var(--azure-blue);
    padding: 16px;
    margin: 12px 0;
    border-radius: 0 8px 8px 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.feature-icon {
    font-size: 24px;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--ms-blue-100);
    border-radius: 8px;
}
```

### 統計カード

```html
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value">50%</div>
        <div class="stat-label">パフォーマンス向上</div>
    </div>
</div>
```

```css
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
    margin: 20px 0;
}

.stat-card {
    background: linear-gradient(135deg, var(--azure-blue), var(--ms-blue-700));
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}

.stat-value {
    font-size: 32px;
    font-weight: bold;
}

.stat-label {
    font-size: 14px;
    opacity: 0.9;
}
```

## 生成ワークフロー

1. **レポートファイルを読み込む**
2. **Web から関連情報を収集** (ドキュメント、Blog、サンプルコード)
3. **情報を整理・選別**
4. **インフォグラフィックを生成** (Azure ライトテーマベース)
5. **`infographic/{YYYYMMDD}-{slug}.html` に保存**
6. **レポートにリンクを追加** (環境変数 `INFOGRAPHIC_BASE_URL` を使用)

## コードブロックの表示ルール

コードブロックはダーク背景 (`#1E1E1E`) で統一する。

### 必須ルール

- 背景色: `#1E1E1E` を使用
- テキスト色: `#E8E8E8` を使用
- 言語ラベル: `#2D2D2D` 背景 + `#9CDCFE` テキスト
- **`pre` タグのスタイル指定は必ず `pre:not(.mermaid)` を使用する**

### highlight.js テーマ

使用してよいテーマ: `vs2015`, `github-dark`, `atom-one-dark`

```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/vs2015.min.css">
```

## 注意事項

- インフォグラフィックは単一の HTML ファイルで完結させる
- 情報は簡潔に、視覚的に理解しやすく
- 技術的な詳細よりも、ビジネス価値とユースケースを強調
- 収集した情報の出典を明記
- モバイル対応のレスポンシブデザインを維持
