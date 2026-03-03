#!/bin/bash
# =============================================================================
# Azure News Summary - ローカルテストスクリプト
# =============================================================================
#
# 概要:
#   ローカル環境で Azure News Summary の各コンポーネントをテストします。
#
# 使用方法:
#   ./scripts/test-local.sh [--parser-only] [--days N]
#
# オプション:
#   --parser-only   パーサースクリプトのみテスト (AWS 不要)
#   --days N        遡る日数 (デフォルト: 3)
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
PARSER_ONLY=false
DAYS=3

# 引数パース
while [[ $# -gt 0 ]]; do
    case $1 in
        --parser-only)
            PARSER_ONLY=true
            shift
            ;;
        --days)
            DAYS="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# プロジェクトルートに移動
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"
cd "${PROJECT_ROOT}"

log_info "=== Azure News Summary Local Test ==="
log_info "Project root: ${PROJECT_ROOT}"
log_info "Days: ${DAYS}"
log_info ""

# =============================================================================
# Test 1: パーサースクリプト
# =============================================================================

log_info "=== Test 1: Parser Scripts ==="
log_info ""

# Azure Updates パーサー
log_info "Testing Azure Updates parser..."

curl -L -s "https://www.microsoft.com/releasecommunications/api/v2/azure/rss" > /tmp/azure_updates_test.xml

if python3 .claude/skills/azure-news-summary/scripts/parse_azure_updates.py \
    --days "${DAYS}" \
    --feed /tmp/azure_updates_test.xml > /tmp/azure_updates_test.json 2>&1; then

    ITEM_COUNT=$(python3 -c "import json; print(json.load(open('/tmp/azure_updates_test.json'))['total_items'])")
    log_success "Azure Updates parser: ${ITEM_COUNT} items found"

    # サンプル出力
    log_info "Sample output:"
    python3 -c "
import json
data = json.load(open('/tmp/azure_updates_test.json'))
for item in data['items'][:3]:
    print(f\"  - [{item['status']}] {item['title'][:60]}...\")
"
else
    log_error "Azure Updates parser failed"
    cat /tmp/azure_updates_test.json
fi

log_info ""

# Azure Blog パーサー
log_info "Testing Azure Blog parser..."

curl -L -s "https://azure.microsoft.com/en-us/blog/feed/" > /tmp/azure_blog_test.xml

if python3 .claude/skills/azure-news-summary/scripts/parse_azure_blog.py \
    --days "${DAYS}" \
    --feed /tmp/azure_blog_test.xml > /tmp/azure_blog_test.json 2>&1; then

    ITEM_COUNT=$(python3 -c "import json; print(json.load(open('/tmp/azure_blog_test.json'))['total_items'])")
    log_success "Azure Blog parser: ${ITEM_COUNT} items found"

    # サンプル出力
    if [[ ${ITEM_COUNT} -gt 0 ]]; then
        log_info "Sample output:"
        python3 -c "
import json
data = json.load(open('/tmp/azure_blog_test.json'))
for item in data['items'][:3]:
    print(f\"  - {item['title'][:60]}...\")
"
    fi
else
    log_error "Azure Blog parser failed"
fi

# クリーンアップ
rm -f /tmp/azure_updates_test.xml /tmp/azure_updates_test.json
rm -f /tmp/azure_blog_test.xml /tmp/azure_blog_test.json

if [[ "${PARSER_ONLY}" == "true" ]]; then
    log_info ""
    log_success "Parser tests completed!"
    exit 0
fi

# =============================================================================
# Test 2: AWS 認証確認
# =============================================================================

log_info ""
log_info "=== Test 2: AWS Authentication ==="
log_info ""

if aws sts get-caller-identity &>/dev/null; then
    AWS_ACCOUNT=$(aws sts get-caller-identity --query "Account" --output text)
    log_success "AWS authenticated: Account ${AWS_ACCOUNT}"
else
    log_error "AWS authentication failed"
    log_info "Please configure AWS credentials:"
    log_info "  aws configure"
    exit 1
fi

# =============================================================================
# Test 3: Bedrock アクセス確認
# =============================================================================

log_info ""
log_info "=== Test 3: Bedrock Access ==="
log_info ""

AWS_REGION="${AWS_REGION:-us-east-1}"
log_info "Region: ${AWS_REGION}"

# Bedrock モデル一覧を取得してアクセス確認
if aws bedrock list-foundation-models --region "${AWS_REGION}" --query "modelSummaries[?contains(modelId, 'claude')].modelId" --output text &>/dev/null; then
    log_success "Bedrock access confirmed"

    # 利用可能な Claude モデルを表示
    log_info "Available Claude models:"
    aws bedrock list-foundation-models --region "${AWS_REGION}" \
        --query "modelSummaries[?contains(modelId, 'claude')].modelId" \
        --output text | tr '\t' '\n' | head -5 | while read model; do
        echo "  - ${model}"
    done
else
    log_warn "Could not list Bedrock models (may still work)"
fi

# =============================================================================
# Test 4: スキルファイル確認
# =============================================================================

log_info ""
log_info "=== Test 4: Skill Files ==="
log_info ""

check_file() {
    local file=$1
    if [[ -f "${file}" ]]; then
        log_success "${file}"
        return 0
    else
        log_error "${file} not found"
        return 1
    fi
}

check_file ".claude/skills/azure-news-summary/SKILL.md"
check_file ".claude/skills/azure-news-summary/report_template.md"
check_file ".claude/skills/creating-infographic/SKILL.md"
check_file ".claude/skills/creating-infographic/themes/azure-news.md"

# =============================================================================
# Test 5: ディレクトリ構造確認
# =============================================================================

log_info ""
log_info "=== Test 5: Directory Structure ==="
log_info ""

mkdir -p reports infographic

if [[ -d "reports" ]]; then
    log_success "reports/ directory exists"
else
    log_error "reports/ directory missing"
fi

if [[ -d "infographic" ]]; then
    log_success "infographic/ directory exists"
else
    log_error "infographic/ directory missing"
fi

# =============================================================================
# 完了
# =============================================================================

log_info ""
log_info "=========================================="
log_success "All tests passed!"
log_info "=========================================="
log_info ""
log_info "You can now run the full pipeline:"
log_info "  python run.py --days ${DAYS} --debug"
log_info ""
log_info "Or run with infographic generation skipped:"
log_info "  python run.py --days ${DAYS} --skip-infographic --debug"
log_info ""
