---
name: creating-infographic
description: グラフィックレコーディング風の HTML インフォグラフィックを生成するスキル。手書き風のビジュアル要素、日本語フォント、カラフルな配色を使用して、テキストコンテンツを視覚的に魅力的なインフォグラフィックに変換します。
---

# グラフィックレコーディング風インフォグラフィック変換

## 目的

テキストコンテンツを、超一流デザイナーが作成したような日本語グラフィックレコーディング風 HTML インフォグラフィックに変換します。情報設計とビジュアルデザインの両面で最高水準を目指し、手書き風の図形やアイコンを活用して内容を視覚的に表現します。

## テーマ一覧

ユーザーの要望に応じて、以下のテーマから選択してください。指定がない場合は「デフォルト」テーマを使用します。

| テーマ | ファイル | 説明 | 適用キーワード |
|--------|----------|------|----------------|
| デフォルト | #[[file:themes/default.md]] | グラフィックレコーディング風 | 「グラレコ」「手書き風」「カラフル」「ポップ」または指定なし |
| Azure ライト | #[[file:themes/azure-light.md]] | Azure プレゼンテーション風ライトテーマ | 「Azure」「ライト」「白背景」「ドキュメント」「印刷」 |
| Azure News | #[[file:themes/azure-news.md]] | Azure ニュースレポート専用テーマ | 「Azure ニュース」「レポート」「アップデート」 |

各テーマファイルには、カラーパレット、CSS テンプレート、HTML テンプレート例が含まれています。テーマを適用する際は、該当ファイルを参照してください。

## グラフィックレコーディング表現技法

インフォグラフィック生成時に適用する表現技法です。

- テキストと視覚要素のバランスを重視
- キーワードを囲み線や色で強調
- 簡易的なアイコンや図形で概念を視覚化
- 数値データは簡潔なグラフや図表で表現
- 接続線や矢印で情報間の関係性を明示
- 余白を効果的に活用して視認性を確保

## アーキテクチャ図・シーケンス図の活用

インフォグラフィックには、可能な限りアーキテクチャ図やシーケンス図などのビジュアルを含めること。

### ソースに Mermaid 図がある場合

**必須**: ソース (レポート、記事など) に Mermaid 図 (` ```mermaid ` ブロック) が含まれている場合は、**必ず** Mermaid.js で HTML に埋め込むこと。HTML/CSS で独自に図を再作成してはならない。

### Mermaid の実装方法

**重要**: Mermaid 図の背景は必ず白にすること。`theme: 'dark'` は使用禁止。

```html
<!-- Mermaid.js の読み込み -->
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
    mermaid.initialize({
        startOnLoad: true,
        theme: 'base',
        themeVariables: {
            primaryColor: '#0078D4',
            primaryTextColor: '#323130',
            primaryBorderColor: '#0078D4',
            lineColor: '#0078D4',
            secondaryColor: '#F3F2F1',
            tertiaryColor: '#FAFAFA',
            background: '#FFFFFF',
            mainBkg: '#E6F2FF',
            nodeBorder: '#0078D4',
            clusterBkg: '#E6F2FF',
            clusterBorder: '#0078D4',
            edgeLabelBackground: '#FFFFFF',
            textColor: '#323130'
        }
    });
</script>

<!-- Mermaid 図の定義 -->
<div class="mermaid-container">
    <pre class="mermaid">
    <!-- 図を作成 -->
    </pre>
</div>
```

### Mermaid コンテナのスタイリング

```css
.mermaid-container {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 24px;
    margin: 20px 0;
    border: 2px solid rgba(0, 120, 212, 0.3);
    overflow-x: auto;
}
.mermaid {
    display: flex;
    justify-content: center;
}
```

## コードサンプルの活用

技術的なコンテンツでは、実装例やコードサンプルを含めることを推奨します。

### コードブロックのスタイリング (highlight.js)

```html
<!-- highlight.js の読み込み -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/vs2015.min.css">
<script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11/build/highlight.min.js"></script>
<script>hljs.highlightAll();</script>
```

**重要: `pre` タグと Mermaid 図の競合を防ぐ**

```css
/* ✅ 正しい: Mermaid の pre を除外 */
.code-block,
pre:not(.mermaid) {
    background: #1E1E1E;
}

/* ❌ 間違い: Mermaid 図も黒背景になる */
.code-block,
pre {
    background: #1E1E1E;
}
```

## 全体的な指針

- 読み手が自然に視線を移動できる配置
- 情報の階層と関連性を視覚的に明確化
- 視覚的な記憶に残るデザイン
- フッターに出典情報を明記
- 生成した HTML は単一ファイルで完結すること (Mermaid.js と highlight.js の CDN 読み込みは許可)

## ソースコンテンツの完全性

**重要**: インフォグラフィックは、ソースの内容を視覚的に表現したものである。ソースの情報を省略せず、全ての内容を含めること。

### 必須ルール

1. **ソースの全セクションを含める**: ソースに含まれるセクションは、原則として全てインフォグラフィックに含める
2. **情報を省略しない**: 視覚的なバランスのために情報を削除してはならない
3. **Mermaid 図はそのまま使用**: ソースに Mermaid 図がある場合は、HTML/CSS で再作成せず、Mermaid.js でそのまま埋め込む

## ファイル名規則

- **形式**: `YYYYMMDD-<descriptive-name>.html`
- **例**: `20260301-azure-app-service-update.html`
- 日付は生成日を使用
- ファイル名の説明部分は英語の小文字とハイフンを使用
