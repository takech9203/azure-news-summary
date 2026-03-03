# Azure ライトテーマ

Microsoft Azure プレゼンテーション風のライトテーマ。Fluent Design System に基づいた配色とコンポーネントを使用します。

## カラーパレット

```css
:root {
    /* Azure Brand Colors */
    --azure-blue: #0078D4;
    --azure-dark-blue: #003D69;
    --azure-light-blue: #50E6FF;

    /* Microsoft Fluent Colors */
    --ms-blue-900: #004578;
    --ms-blue-800: #005A9E;
    --ms-blue-700: #106EBE;
    --ms-blue-600: #0078D4;
    --ms-blue-500: #2B88D8;
    --ms-blue-400: #71AFE5;
    --ms-blue-300: #C7E0F4;
    --ms-blue-200: #DEECF9;
    --ms-blue-100: #EFF6FC;

    /* Status Colors */
    --ms-green: #107C10;
    --ms-yellow: #FFB900;
    --ms-orange: #FF8C00;
    --ms-red: #D83B01;
    --ms-purple: #8764B8;

    /* Text Colors */
    --ms-text-primary: #323130;
    --ms-text-secondary: #605E5C;
    --ms-text-disabled: #A19F9D;

    /* Surface Colors */
    --ms-surface: #FFFFFF;
    --ms-surface-secondary: #FAF9F8;
    --ms-surface-tertiary: #F3F2F1;
    --ms-border: #EDEBE9;
}
```

## フォント

```css
body {
    font-family: 'Noto Sans JP', 'Segoe UI', 'Meiryo', sans-serif;
    color: var(--ms-text-primary);
    background: var(--ms-surface);
    line-height: 1.6;
}
```

## レイアウト

```css
.container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 24px;
}
```

## 基本コンポーネント

### カード

```css
.card {
    background: var(--ms-surface);
    border: 1px solid var(--ms-border);
    border-radius: 8px;
    padding: 20px;
    margin: 16px 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
```

### バッジ

```css
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 13px;
    font-weight: 500;
    color: #FFFFFF;
}

.badge-ga {
    background: var(--ms-green);
}

.badge-preview {
    background: var(--ms-yellow);
    color: var(--ms-text-primary);
}

.badge-development {
    background: var(--ms-blue-400);
}
```

### ハイライト

```css
.highlight-box {
    background: var(--ms-blue-100);
    border-left: 4px solid var(--azure-blue);
    padding: 16px 20px;
    border-radius: 0 8px 8px 0;
    margin: 16px 0;
}
```

## サービスカテゴリ別カラー

| カテゴリ | カラー | サービス例 |
|----------|--------|-----------|
| Compute | `#0078D4` | VMs, App Service, Functions, AKS |
| Storage | `#00BCF2` | Blob, Files, Disks, Data Lake |
| Database | `#FFB900` | SQL, Cosmos DB, PostgreSQL |
| Networking | `#00A651` | Virtual Network, Load Balancer, CDN |
| AI/ML | `#8764B8` | Azure AI, Machine Learning |
| Security | `#D83B01` | Entra ID, Key Vault, Defender |
| Analytics | `#008575` | Synapse, Data Factory |
| DevOps | `#F58B1F` | Azure DevOps, GitHub |

## Before/After コンポーネント

```css
.before-after {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin: 20px 0;
}

.before {
    background: #FFEBEE;
    border: 2px solid var(--ms-red);
    border-radius: 8px;
    padding: 16px;
}

.after {
    background: #E8F5E9;
    border: 2px solid var(--ms-green);
    border-radius: 8px;
    padding: 16px;
}
```

## コードブロック

```css
.code-block {
    background: #1E1E1E;
    border-radius: 8px;
    overflow: hidden;
    margin: 16px 0;
}

.code-header {
    background: #2D2D2D;
    padding: 8px 16px;
    display: flex;
    justify-content: space-between;
    font-size: 12px;
}

.code-lang {
    color: #9CDCFE;
    font-weight: bold;
}

pre:not(.mermaid) {
    background: #1E1E1E;
    margin: 0;
    padding: 0;
    overflow-x: auto;
}

pre:not(.mermaid) code {
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 14px;
    line-height: 1.6;
    padding: 16px !important;
    color: #E8E8E8;
}
```
