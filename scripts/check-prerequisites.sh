#!/bin/bash
# =============================================================================
# Azure News Summary - 前提条件チェックスクリプト
# =============================================================================
#
# 概要:
#   ローカル環境で Azure News Summary を実行するための前提条件を確認します。
#
# 使用方法:
#   ./scripts/check-prerequisites.sh
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
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[NG]${NC} $1"; }

ERRORS=0

log_info "=== Azure News Summary Prerequisites Check ==="
log_info ""

# -----------------------------------------------------------------------------
# Python
# -----------------------------------------------------------------------------

log_info "Checking Python..."
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo "${PYTHON_VERSION}" | cut -d. -f1)
    PYTHON_MINOR=$(echo "${PYTHON_VERSION}" | cut -d. -f2)

    if [[ "${PYTHON_MAJOR}" -ge 3 && "${PYTHON_MINOR}" -ge 12 ]]; then
        log_success "Python ${PYTHON_VERSION} (>= 3.12 required)"
    else
        log_warn "Python ${PYTHON_VERSION} (>= 3.12 recommended, but ${PYTHON_VERSION} may work)"
    fi
else
    log_error "Python 3 not found"
    ERRORS=$((ERRORS + 1))
fi

# -----------------------------------------------------------------------------
# pip
# -----------------------------------------------------------------------------

log_info "Checking pip..."
if command -v pip3 &>/dev/null || python3 -m pip --version &>/dev/null; then
    PIP_VERSION=$(python3 -m pip --version 2>&1 | awk '{print $2}')
    log_success "pip ${PIP_VERSION}"
else
    log_error "pip not found"
    ERRORS=$((ERRORS + 1))
fi

# -----------------------------------------------------------------------------
# AWS CLI
# -----------------------------------------------------------------------------

log_info "Checking AWS CLI..."
if command -v aws &>/dev/null; then
    AWS_VERSION=$(aws --version 2>&1 | awk '{print $1}' | cut -d/ -f2)
    log_success "AWS CLI ${AWS_VERSION}"
else
    log_error "AWS CLI not found"
    log_info "  Install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    ERRORS=$((ERRORS + 1))
fi

# -----------------------------------------------------------------------------
# AWS 認証情報
# -----------------------------------------------------------------------------

log_info "Checking AWS credentials..."
if aws sts get-caller-identity &>/dev/null; then
    AWS_ACCOUNT=$(aws sts get-caller-identity --query "Account" --output text)
    AWS_ARN=$(aws sts get-caller-identity --query "Arn" --output text)
    log_success "AWS Account: ${AWS_ACCOUNT}"
    log_info "  ARN: ${AWS_ARN}"
else
    log_error "AWS credentials not configured or invalid"
    log_info "  Run: aws configure"
    ERRORS=$((ERRORS + 1))
fi

# -----------------------------------------------------------------------------
# curl
# -----------------------------------------------------------------------------

log_info "Checking curl..."
if command -v curl &>/dev/null; then
    CURL_VERSION=$(curl --version 2>&1 | head -1 | awk '{print $2}')
    log_success "curl ${CURL_VERSION}"
else
    log_error "curl not found"
    ERRORS=$((ERRORS + 1))
fi

# -----------------------------------------------------------------------------
# git
# -----------------------------------------------------------------------------

log_info "Checking git..."
if command -v git &>/dev/null; then
    GIT_VERSION=$(git --version 2>&1 | awk '{print $3}')
    log_success "git ${GIT_VERSION}"
else
    log_warn "git not found (optional, but required for CI/CD)"
fi

# -----------------------------------------------------------------------------
# Node.js (MCP サーバー用、オプション)
# -----------------------------------------------------------------------------

log_info "Checking Node.js (optional, for MCP servers)..."
if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    log_success "Node.js ${NODE_VERSION}"
else
    log_warn "Node.js not found (optional, required for cloud-cost MCP server)"
fi

# -----------------------------------------------------------------------------
# Python パッケージ
# -----------------------------------------------------------------------------

log_info ""
log_info "Checking Python packages..."

check_package() {
    local package=$1
    if python3 -c "import ${package}" &>/dev/null; then
        log_success "${package}"
        return 0
    else
        log_warn "${package} not installed"
        return 1
    fi
}

# 必須パッケージ
PACKAGE_ERRORS=0
check_package "boto3" || PACKAGE_ERRORS=$((PACKAGE_ERRORS + 1))

# claude_agent_sdk は特殊なパッケージ名
if python3 -c "from claude_agent_sdk import query" &>/dev/null; then
    log_success "claude-agent-sdk"
else
    log_warn "claude-agent-sdk not installed"
    PACKAGE_ERRORS=$((PACKAGE_ERRORS + 1))
fi

if [[ ${PACKAGE_ERRORS} -gt 0 ]]; then
    log_info ""
    log_info "Install missing packages with:"
    log_info "  pip install -r requirements.txt"
fi

# -----------------------------------------------------------------------------
# RSS フィードへのアクセス確認
# -----------------------------------------------------------------------------

log_info ""
log_info "Checking RSS feed access..."

if curl -sL --connect-timeout 10 "https://www.microsoft.com/releasecommunications/api/v2/azure/rss" -o /dev/null; then
    log_success "Azure Updates RSS feed accessible"
else
    log_error "Cannot access Azure Updates RSS feed"
    ERRORS=$((ERRORS + 1))
fi

# -----------------------------------------------------------------------------
# 結果サマリー
# -----------------------------------------------------------------------------

log_info ""
log_info "=========================================="

if [[ ${ERRORS} -eq 0 ]]; then
    log_success "All prerequisites met!"
    log_info ""
    log_info "You can now run:"
    log_info "  python run.py --days 3 --debug"
    exit 0
else
    log_error "${ERRORS} issue(s) found"
    log_info ""
    log_info "Please fix the issues above before running."
    exit 1
fi
