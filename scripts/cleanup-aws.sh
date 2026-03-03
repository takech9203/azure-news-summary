#!/bin/bash
# =============================================================================
# Azure News Summary - AWS リソースクリーンアップスクリプト
# =============================================================================
#
# 概要:
#   setup-aws-oidc.sh で作成した AWS リソースを削除します。
#   OIDC プロバイダーは他のプロジェクトでも使用されている可能性があるため、
#   デフォルトでは削除しません。
#
# 使用方法:
#   ./scripts/cleanup-aws.sh [--include-oidc]
#
# オプション:
#   --include-oidc   OIDC プロバイダーも削除 (注意: 他のプロジェクトに影響)
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

# デフォルト設定
INCLUDE_OIDC=false

# 引数パース
while [[ $# -gt 0 ]]; do
    case $1 in
        --include-oidc)
            INCLUDE_OIDC=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# リソース名
ROLE_NAME="azure-news-summary-github-actions"
POLICY_NAME="azure-news-summary-bedrock-access"
OIDC_PROVIDER_URL="token.actions.githubusercontent.com"

log_info "=== Azure News Summary AWS Cleanup ==="
log_info ""

# AWS アカウント ID 取得
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
log_info "AWS Account ID: ${AWS_ACCOUNT_ID}"

# =============================================================================
# IAM ロールの削除
# =============================================================================

log_info ""
log_info "=== Deleting IAM Role ==="

if aws iam get-role --role-name "${ROLE_NAME}" &>/dev/null; then
    # インラインポリシーを削除
    log_info "Deleting inline policy: ${POLICY_NAME}..."
    aws iam delete-role-policy --role-name "${ROLE_NAME}" --policy-name "${POLICY_NAME}" 2>/dev/null || true

    # ロールを削除
    log_info "Deleting role: ${ROLE_NAME}..."
    aws iam delete-role --role-name "${ROLE_NAME}"
    log_success "IAM role deleted: ${ROLE_NAME}"
else
    log_warn "IAM role not found: ${ROLE_NAME}"
fi

# =============================================================================
# OIDC プロバイダーの削除 (オプション)
# =============================================================================

if [[ "${INCLUDE_OIDC}" == "true" ]]; then
    log_info ""
    log_info "=== Deleting OIDC Provider ==="
    log_warn "WARNING: This may affect other projects using the same OIDC provider!"

    OIDC_PROVIDER_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/${OIDC_PROVIDER_URL}"

    if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "${OIDC_PROVIDER_ARN}" &>/dev/null; then
        read -p "Are you sure you want to delete the OIDC provider? (y/N): " confirm
        if [[ "${confirm}" =~ ^[Yy]$ ]]; then
            aws iam delete-open-id-connect-provider --open-id-connect-provider-arn "${OIDC_PROVIDER_ARN}"
            log_success "OIDC provider deleted"
        else
            log_info "OIDC provider deletion skipped"
        fi
    else
        log_warn "OIDC provider not found"
    fi
else
    log_info ""
    log_info "=== OIDC Provider ==="
    log_info "OIDC provider was NOT deleted (may be used by other projects)"
    log_info "To delete it, run: $0 --include-oidc"
fi

# =============================================================================
# 完了
# =============================================================================

log_info ""
log_info "=========================================="
log_success "Cleanup completed!"
log_info "=========================================="
