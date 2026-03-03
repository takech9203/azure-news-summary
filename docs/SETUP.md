# Azure News Summary セットアップガイド

このドキュメントでは、Azure News Summary を GitHub Actions で自動実行するための設定手順を説明します。

## クイックスタート

セットアップスクリプトを使用して、AWS リソースを自動作成できます。

```bash
# 1. 前提条件を確認
./scripts/check-prerequisites.sh

# 2. AWS OIDC と IAM ロールをセットアップ
./scripts/setup-aws-oidc.sh YOUR_GITHUB_ORG azure-news-summary

# 3. ローカルテストを実行
./scripts/test-local.sh --days 3
```

詳細な手順は以下を参照してください。

## 前提条件

- GitHub リポジトリ
- AWS アカウント (Amazon Bedrock アクセス用)
- AWS CLI がインストール・設定済み
- Python 3.12+

前提条件を確認するには:

```bash
./scripts/check-prerequisites.sh
```

## セットアップ手順

### 方法 1: スクリプトを使用 (推奨)

```bash
# AWS OIDC プロバイダーと IAM ロールを作成
./scripts/setup-aws-oidc.sh YOUR_GITHUB_ORG azure-news-summary
```

スクリプトは以下を行います。

- OIDC プロバイダーが存在しない場合のみ作成 (既存環境と Conflict しない)
- IAM ロールを作成・更新
- Bedrock アクセスポリシーをアタッチ

### 方法 2: 手動セットアップ

#### 1. AWS IAM OIDC プロバイダーの設定

GitHub Actions から AWS リソースにアクセスするために、OIDC プロバイダーを設定します。

```bash
# OIDC プロバイダーの作成
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### 2. IAM ロールの作成

GitHub Actions が使用する IAM ロールを作成します。

**信頼ポリシー (trust-policy.json)**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG/azure-news-summary:*"
        }
      }
    }
  ]
}
```

**権限ポリシー (bedrock-policy.json)**:

Claude Agent SDK は cross-region inference profile を使用するため、foundation-model と inference-profile の両方へのアクセスを許可する必要があります。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockInvokeFoundationModel",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
      ]
    },
    {
      "Sid": "BedrockInvokeInferenceProfile",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*:YOUR_ACCOUNT_ID:inference-profile/*",
        "arn:aws:bedrock:*:*:inference-profile/*"
      ]
    }
  ]
}
```

```bash
# ロールの作成
aws iam create-role \
  --role-name azure-news-summary-github-actions \
  --assume-role-policy-document file://trust-policy.json

# ポリシーのアタッチ
aws iam put-role-policy \
  --role-name azure-news-summary-github-actions \
  --policy-name bedrock-access \
  --policy-document file://bedrock-policy.json
```

### 3. GitHub リポジトリの設定

#### Repository Variables

以下の Variables を設定します (Settings > Secrets and variables > Actions > Variables)。

| 変数名 | 値 | 説明 |
|--------|-----|------|
| `AWS_ROLE_ARN` | `arn:aws:iam::YOUR_ACCOUNT_ID:role/azure-news-summary-github-actions` | IAM ロール ARN |
| `AWS_REGION` | `us-east-1` | AWS リージョン |
| `INFOGRAPHIC_BASE_URL` | `https://YOUR_ORG.github.io/azure-news-summary` | GitHub Pages URL |

#### GitHub Pages の有効化

1. Settings > Pages に移動
2. Source: "GitHub Actions" を選択
3. Save

### 4. 動作確認

#### 手動実行

1. Actions タブに移動
2. "Azure News Summary" ワークフローを選択
3. "Run workflow" をクリック
4. パラメータを設定して実行

#### ローカル実行

```bash
# 依存関係のインストール
pip install -r requirements.txt

# AWS 認証情報の設定
export AWS_PROFILE=your-profile

# 実行
python run.py --days 3 --debug
```

## トラブルシューティング

### AWS 認証エラー

```
Error: Could not load credentials from any providers
```

**解決策**:
- IAM ロールの信頼ポリシーを確認
- リポジトリ名が正しいか確認
- OIDC プロバイダーが正しく設定されているか確認

### Bedrock アクセスエラー

```
Error: User: arn:aws:sts::... is not authorized to perform: bedrock:InvokeModel
```

**解決策**:
- IAM ロールに Bedrock 権限があるか確認
- リージョンで Claude モデルが利用可能か確認

### レート制限エラー

```
Error: ThrottlingException
```

**解決策**:
- しばらく待ってから再実行
- フォールバックモデル (Sonnet) が自動的に使用される

## スクリプト一覧

| スクリプト | 説明 |
|-----------|------|
| `scripts/check-prerequisites.sh` | 前提条件 (Python, AWS CLI, 認証情報) を確認 |
| `scripts/setup-aws-oidc.sh` | AWS OIDC プロバイダーと IAM ロールを作成 |
| `scripts/test-local.sh` | ローカル環境でパーサーと AWS アクセスをテスト |
| `scripts/cleanup-aws.sh` | 作成した AWS リソースを削除 |

### テストスクリプトの使い方

```bash
# パーサーのみテスト (AWS 不要)
./scripts/test-local.sh --parser-only

# フルテスト
./scripts/test-local.sh --days 3
```

### クリーンアップ

```bash
# IAM ロールを削除 (OIDC プロバイダーは残す)
./scripts/cleanup-aws.sh

# OIDC プロバイダーも含めて削除 (注意: 他のプロジェクトに影響する可能性あり)
./scripts/cleanup-aws.sh --include-oidc
```

## 参考リンク

- [GitHub Actions OIDC with AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk)
