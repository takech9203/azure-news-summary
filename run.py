#!/usr/bin/env python3
"""
Azure News Summary 自動化スクリプト

Claude Agent SDK (Amazon Bedrock) を使用して azure-news-summary スキルを実行します。
GitHub Actions で毎日自動実行されることを想定しています。

使用方法:
    python run.py                           # デフォルト設定で実行
    python run.py "カスタムプロンプト"       # カスタムプロンプトで実行
    python run.py --prompt "カスタムプロンプト"  # カスタムプロンプト (明示的フラグ)

環境変数:
    DEBUG=1         デバッグモード (詳細ログ出力)
    VERBOSE=1       詳細モード (タイミング情報出力)
    AWS_REGION      Bedrock の AWS リージョン (デフォルト: us-east-1)
"""

import argparse
import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, query

from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    UserMessage,
    TextBlock,
    ToolUseBlock,
)

# =============================================================================
# 設定
# =============================================================================

# 遡って取得する日数のデフォルト値。
# 日次実行では 3 日、キャッチアップ実行では --days 7 などを指定。
DEFAULT_DAYS = 3

# オーケストレーターに渡すデフォルトのプロンプトテンプレート。
# {days} プレースホルダーは実際の日数に置換される。
DEFAULT_PROMPT_TEMPLATE = (
    "Report Azure news from the past {days} days. "
    "Fetch the RSS feed, filter updates, check for duplicates, "
    "and delegate report creation to subagents."
)

# モデル設定: 品質重視で Opus を使用、スロットリング時は Sonnet にフォールバック。
PRIMARY_MODEL = "global.anthropic.claude-opus-4-6-v1"
FALLBACK_MODEL = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"

# オーケストレーターと report-generator サブエージェントが使用するツール。
# Claude Code 組み込みのファイル操作・Web アクセス用ツール。
COMMON_TOOLS = [
    "Skill",      # .claude/skills/ のスキル定義を呼び出す
    "Read",       # ファイル読み込み
    "Write",      # ファイル書き込み
    "Edit",       # ファイル編集
    "MultiEdit",  # 複数ファイル編集
    "Glob",       # パターンでファイル検索
    "Grep",       # ファイル内容検索
    "Bash",       # シェルコマンド実行
    "WebFetch",   # Web ページ取得
]

# MCP (Model Context Protocol) ツール。
# 料金情報にアクセス。
# .mcp.json で設定が必要。
MCP_TOOLS = [
    "mcp__cloud-cost__get_pricing",
    "mcp__cloud-cost__compare_pricing",
    "mcp__cloud-cost__list_services",
]


# =============================================================================
# ロギング
# =============================================================================


class Logger:
    """デバッグモードと詳細モードに対応したロガー。

    環境変数で出力の詳細度を制御:
    - DEBUG=1: 全メッセージの詳細 (最も詳細)
    - VERBOSE=1: タイミングと操作の詳細
    - どちらもなし: 最小限の出力 (進捗ドットのみ)
    """

    def __init__(self) -> None:
        self.debug = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")
        self.verbose = os.environ.get("VERBOSE", "").lower() in ("1", "true", "yes") or self.debug
        self.start_time = time.time()
        self.last_timestamp = self.start_time

    def elapsed(self) -> str:
        """開始からの経過時間を返す。"""
        return f"{time.time() - self.start_time:.1f}s"

    def delta(self) -> str:
        """前回のタイムスタンプからの経過時間を返し、タイムスタンプを更新する。"""
        now = time.time()
        delta = now - self.last_timestamp
        self.last_timestamp = now
        return f"+{delta:.1f}s"

    def log(self, message: str, *, level: str = "INFO", force: bool = False) -> None:
        """タイムスタンプ付きでメッセージを出力する。"""
        if force or self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}", flush=True)

    def log_debug(self, message: str) -> None:
        """デバッグメッセージを出力 (デバッグモード時のみ)。"""
        if self.debug:
            self.log(message, level="DEBUG")

    def log_verbose(self, message: str) -> None:
        """詳細メッセージを出力 (verbose または debug モード時)。"""
        if self.verbose:
            self.log(message, level="VERBOSE")

    def log_error(self, message: str) -> None:
        """エラーメッセージを出力 (常に表示)。"""
        self.log(message, level="ERROR", force=True)

    def log_warn(self, message: str) -> None:
        """警告メッセージを出力 (常に表示)。"""
        self.log(message, level="WARN", force=True)


# グローバルロガーインスタンス
logger = Logger()


# =============================================================================
# ユーティリティ関数
# =============================================================================


def print_separator(char: str = "=", length: int = 60) -> None:
    """出力の視覚的な区切り線を表示する。"""
    print(char * length)


def get_latest_reports(output_dir: Path, limit: int = 5) -> list[str]:
    """
    最新のレポートファイル一覧を取得する。

    Args:
        output_dir: レポートが格納されているディレクトリ
        limit: 返すレポートの最大数

    Returns:
        レポートファイル名のリスト
    """
    reports = []

    try:
        if not output_dir.exists():
            return reports

        # 年ディレクトリを取得
        year_dirs = [
            d for d in output_dir.iterdir()
            if d.is_dir() and d.name.isdigit()
        ]
        year_dirs.sort(reverse=True)

        # 年ディレクトリから全 Markdown ファイルを取得
        for year_dir in year_dirs:
            for md_file in year_dir.glob("*.md"):
                reports.append({
                    "name": md_file.name,
                    "path": md_file,
                    "mtime": md_file.stat().st_mtime,
                })

        # 更新日時でソート (新しい順)
        reports.sort(key=lambda x: x["mtime"], reverse=True)

        return [r["name"] for r in reports[:limit]]

    except Exception as e:
        print(f"Warning: Could not read report directory: {e}", file=sys.stderr)
        return []


# =============================================================================
# インデックス生成関数
# =============================================================================


def update_reports_index(reports_dir: Path) -> None:
    """
    reports ディレクトリの INDEX.md を更新する。
    """
    if not reports_dir.exists():
        return

    # 全レポートファイルを収集
    all_reports = []
    for year_dir in sorted(reports_dir.iterdir(), reverse=True):
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue
        for md_file in sorted(year_dir.glob("*.md"), reverse=True):
            if md_file.name == "INDEX.md":
                continue
            # ファイル名からタイトルを抽出
            title = md_file.stem.replace("-", " ").title()
            all_reports.append({
                "year": year_dir.name,
                "name": md_file.name,
                "title": title,
                "path": f"{year_dir.name}/{md_file.name}",
            })

    # INDEX.md を生成
    lines = [
        "# Azure News Summary Reports",
        "",
        f"Total: {len(all_reports)} reports",
        "",
    ]

    # 年ごとにグループ化
    current_year = None
    for report in all_reports:
        if report["year"] != current_year:
            current_year = report["year"]
            lines.append(f"## {current_year}")
            lines.append("")
        lines.append(f"- [{report['name']}]({report['path']})")

    lines.append("")

    index_path = reports_dir / "INDEX.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    logger.log_verbose(f"Updated {index_path}")


def update_infographic_index(infographic_dir: Path) -> None:
    """
    infographic ディレクトリの INDEX.md を更新する。
    """
    if not infographic_dir.exists():
        return

    # 全インフォグラフィックファイルを収集
    all_infographics = []
    for html_file in sorted(infographic_dir.glob("*.html"), reverse=True):
        if html_file.name == "index.html":
            continue
        title = html_file.stem.replace("-", " ").title()
        all_infographics.append({
            "name": html_file.name,
            "title": title,
        })

    # INDEX.md を生成
    lines = [
        "# Azure News Infographics",
        "",
        f"Total: {len(all_infographics)} infographics",
        "",
    ]

    for infographic in all_infographics:
        lines.append(f"- [{infographic['name']}]({infographic['name']})")

    lines.append("")

    index_path = infographic_dir / "INDEX.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    logger.log_verbose(f"Updated {index_path}")


# =============================================================================
# Git 操作
# =============================================================================


def git_commit_and_push(message: str) -> bool:
    """
    変更をコミットしてプッシュする。

    Args:
        message: コミットメッセージ

    Returns:
        成功した場合 True
    """
    import subprocess

    try:
        # 変更があるか確認
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        if not result.stdout.strip():
            logger.log_verbose("No changes to commit")
            return True

        # 変更をステージング
        subprocess.run(["git", "add", "reports/", "infographic/"], check=True)

        # コミット
        subprocess.run(
            ["git", "commit", "-m", message],
            check=True,
        )

        # プッシュ
        subprocess.run(["git", "push"], check=True)

        logger.log_verbose(f"Committed and pushed: {message}")
        return True

    except subprocess.CalledProcessError as e:
        logger.log_error(f"Git operation failed: {e}")
        return False


# =============================================================================
# Claude Agent SDK 実行
# =============================================================================


async def run_skill(prompt: str, days: int) -> list[str]:
    """
    azure-news-summary スキルを実行してレポートを生成する。

    Args:
        prompt: オーケストレーターに渡すプロンプト
        days: 遡る日数

    Returns:
        生成されたレポートファイルのパスリスト
    """
    # AWS リージョン設定
    region = os.environ.get("AWS_REGION", "us-east-1")

    # スキルファイルを読み込む
    skill_path = Path(".claude/skills/azure-news-summary/SKILL.md")
    if not skill_path.exists():
        logger.log_error(f"Skill file not found: {skill_path}")
        return []

    skill_content = skill_path.read_text(encoding="utf-8")

    # プロンプトを構築
    full_prompt = f"""
{prompt}

Follow the instructions in the skill definition below.

<skill>
{skill_content}
</skill>

Important:
- Generate reports for updates from the past {days} days
- Check for duplicates before creating reports
- Create one report per update (or group of related updates for the same service)
- Use the report template from .claude/skills/azure-news-summary/report_template.md
"""

    # Bedrock 統合用の環境変数
    bedrock_env = {
        "CLAUDE_CODE_USE_BEDROCK": "1",
        "AWS_REGION": region,
    }

    # レポート生成用サブエージェントのプロンプト
    report_subagent_prompt = (
        "You are an Azure news report generator. "
        "When given an update item and output file path:\n"
        "1. Invoke the Skill tool with skill='azure-news-summary'\n"
        "2. Follow the skill's workflow to create the report\n"
        "3. Save to the specified output path"
    )

    # プロジェクトディレクトリ
    project_dir = Path.cwd()

    # オーケストレーターオプション
    options = ClaudeAgentOptions(
        model=PRIMARY_MODEL,
        fallback_model=FALLBACK_MODEL,
        env=bedrock_env,
        cwd=str(project_dir),
        setting_sources=["project"],
        allowed_tools=COMMON_TOOLS + ["Task"] + MCP_TOOLS,
        agents={
            "report-generator": AgentDefinition(
                description="Generate a report from an update item.",
                prompt=report_subagent_prompt,
                tools=COMMON_TOOLS + MCP_TOOLS,
            ),
        },
    )

    new_reports = []

    try:
        logger.log_verbose(f"Starting skill execution with model: {PRIMARY_MODEL}")

        async for message in query(prompt=full_prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        logger.log_debug(f"Assistant: {block.text[:200]}...")
                    elif isinstance(block, ToolUseBlock):
                        logger.log_debug(f"Tool: {block.name}")
                        # Write ツールでレポートが作成された場合を追跡
                        if block.name == "Write" and "reports/" in str(block.input.get("file_path", "")):
                            file_path = block.input.get("file_path", "")
                            if file_path and file_path.endswith(".md"):
                                new_reports.append(file_path)
                                logger.log_verbose(f"New report created: {file_path}")

            elif isinstance(message, ResultMessage):
                logger.log_verbose("Skill execution completed")

    except Exception as e:
        logger.log_error(f"Skill execution failed: {e}")
        # フォールバックモデルで再試行
        if PRIMARY_MODEL in str(e):
            logger.log_warn(f"Retrying with fallback model: {FALLBACK_MODEL}")
            options.model = FALLBACK_MODEL
            async for message in query(prompt=full_prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, ToolUseBlock):
                            if block.name == "Write" and "reports/" in str(block.input.get("file_path", "")):
                                file_path = block.input.get("file_path", "")
                                if file_path and file_path.endswith(".md"):
                                    new_reports.append(file_path)

    return new_reports


async def generate_infographics(report_paths: list[str]) -> list[str]:
    """
    レポートからインフォグラフィックを生成する。

    Args:
        report_paths: レポートファイルのパスリスト

    Returns:
        生成されたインフォグラフィックファイルのパスリスト
    """
    if not report_paths:
        logger.log_verbose("No reports to generate infographics for")
        return []

    # AWS Bedrock クライアント設定
    region = os.environ.get("AWS_REGION", "us-east-1")

    # Bedrock 統合用の環境変数
    bedrock_env = {
        "CLAUDE_CODE_USE_BEDROCK": "1",
        "AWS_REGION": region,
    }

    # プロジェクトディレクトリ
    project_dir = Path.cwd()

    # インフォグラフィックスキルを読み込む
    skill_path = Path(".claude/skills/creating-infographic/SKILL.md")
    if not skill_path.exists():
        logger.log_error(f"Infographic skill not found: {skill_path}")
        return []

    skill_content = skill_path.read_text(encoding="utf-8")

    new_infographics = []

    # インフォグラフィック生成用サブエージェントのプロンプト
    infographic_subagent_prompt = (
        "You are an infographic generator. "
        "When given a report file path:\n"
        "1. Read the report file\n"
        "2. Generate an HTML infographic using the Azure News theme\n"
        "3. Save to infographic/{YYYYMMDD}-{slug}.html"
    )

    # バッチサイズ (コンテキスト肥大化を防ぐ)
    batch_size = 5

    for i in range(0, len(report_paths), batch_size):
        batch = report_paths[i:i + batch_size]
        logger.log_verbose(f"Processing infographic batch {i // batch_size + 1}: {len(batch)} reports")

        # プロンプトを構築
        reports_list = "\n".join([f"- {path}" for path in batch])
        prompt = f"""
Generate infographics for the following Azure news reports:

{reports_list}

Use the Azure News theme (themes/azure-news.md).

<skill>
{skill_content}
</skill>

For each report:
1. Read the report file
2. Generate an HTML infographic following the theme
3. Save to infographic/{{YYYYMMDD}}-{{slug}}.html
"""

        options = ClaudeAgentOptions(
            model=PRIMARY_MODEL,
            fallback_model=FALLBACK_MODEL,
            env=bedrock_env,
            cwd=str(project_dir),
            setting_sources=["project"],
            allowed_tools=COMMON_TOOLS + ["Task"],
            agents={
                "infographic-generator": AgentDefinition(
                    description="Generate an infographic from a report.",
                    prompt=infographic_subagent_prompt,
                    tools=["Skill", "Read", "Write", "Edit", "Glob", "Bash"],
                ),
            },
        )

        try:
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, ToolUseBlock):
                            if block.name == "Write" and "infographic/" in str(block.input.get("file_path", "")):
                                file_path = block.input.get("file_path", "")
                                if file_path and file_path.endswith(".html"):
                                    new_infographics.append(file_path)
                                    logger.log_verbose(f"New infographic created: {file_path}")

        except Exception as e:
            logger.log_error(f"Infographic generation failed for batch: {e}")
            # フォールバックモデルで再試行
            if PRIMARY_MODEL in str(e):
                logger.log_warn(f"Retrying with fallback model: {FALLBACK_MODEL}")
                options.model = FALLBACK_MODEL
                try:
                    async for message in query(prompt=prompt, options=options):
                        if isinstance(message, AssistantMessage):
                            for block in message.content:
                                if isinstance(block, ToolUseBlock):
                                    if block.name == "Write" and "infographic/" in str(block.input.get("file_path", "")):
                                        file_path = block.input.get("file_path", "")
                                        if file_path and file_path.endswith(".html"):
                                            new_infographics.append(file_path)
                except Exception as e2:
                    logger.log_error(f"Fallback also failed: {e2}")

    return new_infographics


# =============================================================================
# メイン関数
# =============================================================================


async def main_async(args: argparse.Namespace) -> int:
    """
    非同期メイン関数。

    Args:
        args: コマンドライン引数

    Returns:
        終了コード
    """
    print_separator()
    print("Azure News Summary")
    print_separator()

    # プロンプトを構築
    if args.prompt:
        prompt = args.prompt
    else:
        prompt = DEFAULT_PROMPT_TEMPLATE.format(days=args.days)

    logger.log_verbose(f"Days: {args.days}")
    logger.log_verbose(f"Prompt: {prompt[:100]}...")

    # Phase 1: レポート生成
    print("\n[Phase 1] Generating reports...")
    new_reports = await run_skill(prompt, args.days)
    print(f"Generated {len(new_reports)} reports")

    # Phase 2: インフォグラフィック生成
    if new_reports and not args.skip_infographic:
        print("\n[Phase 2] Generating infographics...")
        new_infographics = await generate_infographics(new_reports)
        print(f"Generated {len(new_infographics)} infographics")
    else:
        new_infographics = []

    # インデックス更新
    print("\n[Updating indexes...]")
    reports_dir = Path("reports")
    infographic_dir = Path("infographic")
    update_reports_index(reports_dir)
    update_infographic_index(infographic_dir)

    # Git コミット (CI/CD 環境の場合)
    if os.environ.get("CI") and (new_reports or new_infographics):
        print("\n[Committing changes...]")
        today = datetime.now().strftime("%Y-%m-%d")
        message = f"docs(reports): add reports for {today}"
        git_commit_and_push(message)

    # サマリー出力
    print_separator()
    print("Summary")
    print_separator()
    print(f"New reports: {len(new_reports)}")
    print(f"New infographics: {len(new_infographics)}")

    if new_reports:
        print("\nGenerated reports:")
        for report in new_reports[:10]:
            print(f"  - {report}")
        if len(new_reports) > 10:
            print(f"  ... and {len(new_reports) - 10} more")

    print_separator()

    return 0


def main() -> int:
    """
    メイン関数。

    Returns:
        終了コード
    """
    parser = argparse.ArgumentParser(
        description="Azure News Summary - Generate reports from Azure Updates RSS feed"
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="Custom prompt for the orchestrator",
    )
    parser.add_argument(
        "--prompt", "-p",
        dest="prompt_flag",
        default=None,
        help="Custom prompt (explicit flag)",
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=DEFAULT_DAYS,
        help=f"Number of days to look back (default: {DEFAULT_DAYS})",
    )
    parser.add_argument(
        "--skip-infographic",
        action="store_true",
        help="Skip infographic generation",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    args = parser.parse_args()

    # プロンプトの優先順位: --prompt フラグ > 位置引数
    if args.prompt_flag:
        args.prompt = args.prompt_flag

    # デバッグモード設定
    if args.debug:
        os.environ["DEBUG"] = "1"
        global logger
        logger = Logger()

    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
