#!/bin/bash
# =============================================================================
# Azure News Summary - AWS OIDC セットアップスクリプト
# =============================================================================
#
# 概要:
#   GitHub Actions から AWS Bedrock にアクセスするための IAM OIDC プロバイダーと
#   IAM ロールを作成します。既存リソースがある場合はスキップします。
#
# 使用方法:
#   ./scripts/setup-aws-oidc.sh <GITHUB_ORG> <GITHUB_REPO>
#
# 例:
#   ./scripts/setup-aws-oidc.sh my-org azure-news-summary
#
# 環境変数:
#   AWS_PROFILE     使用する AWS プロファイル (オプション)
#   AWS_REGION      AWS リージョン (デフォルト: us-east-1)
#
# =============================================================================

set -euo pipefail

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 使用方法
usage() {
    echo "Usage: $0 <GITHUB_ORG> <GITHUB_REPO>"
    echo ""
    echo "Arguments:"
    echo "  GITHUB_ORG   GitHub organization or username"
    echo "  GITHUB_REPO  GitHub repository name (default: azure-news-summary)"
    echo ""
    echo "Environment variables:"
    echo "  AWS_PROFILE  AWS profile to use (optional)"
    echo "  AWS_REGION   AWS region (default: us-east-1)"
    echo ""
    echo "Example:"
    echo "  $0 my-org azure-news-summary"
    exit 1
}

# 引数チェック
if [[ $# -lt 1 ]]; then
    usage
fi

GITHUB_ORG="$1"
GITHUB_REPO="${2:-azure-news-summary}"
AWS_REGION="${AWS_REGION:-us-east-1}"

# プロジェクト固有のリソース名 (Conflict 回避)
ROLE_NAME="azure-news-summary-github-actions"
POLICY_NAME="azure-news-summary-bedrock-access"
OIDC_PROVIDER_URL="token.actions.githubusercontent.com"

log_info "=== Azure News Summary AWS OIDC Setup ==="
log_info "GitHub: ${GITHUB_ORG}/${GITHUB_REPO}"
log_info "AWS Region: ${AWS_REGION}"
log_info "IAM Role: ${ROLE_NAME}"

# AWS アカウント ID 取得
log_info "Getting AWS account ID..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
log_info "AWS Account ID: ${AWS_ACCOUNT_ID}"

# =============================================================================
# Step 1: OIDC プロバイダーの確認・作成
# =============================================================================

log_info ""
log_info "=== Step 1: OIDC Provider ==="

OIDC_PROVIDER_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/${OIDC_PROVIDER_URL}"

# 既存の OIDC プロバイダーを確認
if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "${OIDC_PROVIDER_ARN}" &>/dev/null; then
    log_warn "OIDC provider already exists: ${OIDC_PROVIDER_ARN}"
    log_info "Skipping OIDC provider creation (using existing)"
else
    log_info "Creating OIDC provider..."

    # GitHub Actions の thumbprint を取得
    # 参考: https://github.blog/changelog/2022-01-13-github-actions-update-on-oidc-based-deployments-to-aws/
    THUMBPRINT="6938fd4d98bab03faadb97b34396831e3780aea1"

    aws iam create-open-id-connect-provider \
        --url "https://${OIDC_PROVIDER_URL}" \
        --client-id-list "sts.amazonaws.com" \
        --thumbprint-list "${THUMBPRINT}"

    log_success "OIDC provider created: ${OIDC_PROVIDER_ARN}"
fi

# =============================================================================
# Step 2: IAM ロールの確認・作成
# =============================================================================

log_info ""
log_info "=== Step 2: IAM Role ==="

ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"

# 信頼ポリシードキュメント
TRUST_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "${OIDC_PROVIDER_ARN}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "${OIDC_PROVIDER_URL}:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "${OIDC_PROVIDER_URL}:sub": "repo:${GITHUB_ORG}/${GITHUB_REPO}:*"
        }
      }
    }
  ]
}
EOF
)

# 既存のロールを確認
if aws iam get-role --role-name "${ROLE_NAME}" &>/dev/null; then
    log_warn "IAM role already exists: ${ROLE_NAME}"
    log_info "Updating trust policy..."

    # 信頼ポリシーを更新
    echo "${TRUST_POLICY}" > /tmp/azure-news-summary-trust-policy.json
    aws iam update-assume-role-policy \
        --role-name "${ROLE_NAME}" \
        --policy-document "file:///tmp/azure-news-summary-trust-policy.json"
    rm -f /tmp/azure-news-summary-trust-policy.json

    log_success "Trust policy updated"
else
    log_info "Creating IAM role: ${ROLE_NAME}..."

    echo "${TRUST_POLICY}" > /tmp/azure-news-summary-trust-policy.json
    aws iam create-role \
        --role-name "${ROLE_NAME}" \
        --assume-role-policy-document "file:///tmp/azure-news-summary-trust-policy.json" \
        --description "IAM role for Azure News Summary GitHub Actions"
    rm -f /tmp/azure-news-summary-trust-policy.json

    log_success "IAM role created: ${ROLE_ARN}"
fi

# =============================================================================
# Step 3: Bedrock アクセスポリシーの作成・アタッチ
# =============================================================================

log_info ""
log_info "=== Step 3: Bedrock Access Policy ==="

# Bedrock アクセスポリシー
BEDROCK_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockInvokeModel",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
      ]
    }
  ]
}
EOF
)

# インラインポリシーを作成・更新
log_info "Attaching Bedrock access policy..."

echo "${BEDROCK_POLICY}" > /tmp/azure-news-summary-bedrock-policy.json
aws iam put-role-policy \
    --role-name "${ROLE_NAME}" \
    --policy-name "${POLICY_NAME}" \
    --policy-document "file:///tmp/azure-news-summary-bedrock-policy.json"
rm -f /tmp/azure-news-summary-bedrock-policy.json

log_success "Bedrock access policy attached"

# =============================================================================
# 完了
# =============================================================================

log_info ""
log_info "=========================================="
log_success "Setup completed successfully!"
log_info "=========================================="
log_info ""
log_info "Next steps:"
log_info ""
log_info "1. Add the following Repository Variables to GitHub:"
log_info "   (Settings > Secrets and variables > Actions > Variables)"
log_info ""
log_info "   AWS_ROLE_ARN: ${ROLE_ARN}"
log_info "   AWS_REGION: ${AWS_REGION}"
log_info "   INFOGRAPHIC_BASE_URL: https://${GITHUB_ORG}.github.io/${GITHUB_REPO}"
log_info ""
log_info "2. Enable GitHub Pages:"
log_info "   (Settings > Pages > Source: GitHub Actions)"
log_info ""
log_info "3. Test the workflow:"
log_info "   (Actions > Azure News Summary > Run workflow)"
log_info ""
