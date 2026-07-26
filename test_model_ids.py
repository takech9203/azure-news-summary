#!/usr/bin/env python3
"""
Claude Fable 5 と Claude Opus 5 のモデル ID をテストするサンプルプログラム

このスクリプトは、Bedrock でのモデル ID の動作を確認します。
"""

import asyncio
import os
import sys

import boto3
from claude_agent_sdk import ClaudeAgentOptions, query


async def test_model(model_id: str, prompt: str) -> bool:
    """指定されたモデル ID で簡単なクエリを実行してテスト"""
    print(f"\n{'=' * 60}")
    print(f"Testing model: {model_id}")
    print(f"{'=' * 60}")

    try:
        options = ClaudeAgentOptions(
            model=model_id,
            env={
                "CLAUDE_CODE_USE_BEDROCK": "1",
                "AWS_REGION": os.environ.get("AWS_REGION", "us-east-1"),
            },
            cwd=str(os.getcwd()),
            setting_sources=[],  # SDK 設定を無効化
            max_turns=1,  # 1 ターンのみ
        )

        print(f"\nPrompt: {prompt}")
        print(f"Model: {model_id}")
        print(f"Region: {os.environ.get('AWS_REGION', 'us-east-1')}")
        print("\nResponse:")
        print("-" * 60)

        response_received = False
        async for message in query(prompt=prompt, options=options):
            # AssistantMessage をチェック
            if hasattr(message, "content"):
                for block in message.content if isinstance(message.content, list) else []:
                    if hasattr(block, "text"):
                        print(block.text)
                        response_received = True

            # ResultMessage をチェック
            if hasattr(message, "subtype"):
                if message.subtype == "success":
                    print(f"\n✅ Success! Model: {model_id}")
                    return True
                elif "error" in message.subtype:
                    print(f"\n❌ Error: {message.subtype}")
                    if hasattr(message, "errors") and message.errors:
                        for error in message.errors:
                            print(f"   {error}")
                    return False

        if not response_received:
            print("\n⚠️  No response received")
            return False

        return True

    except Exception as e:
        print(f"\n❌ Exception: {type(e).__name__}: {str(e)[:200]}")
        return False


async def main():
    """メインテスト関数"""
    print("\n" + "=" * 60)
    print("Claude Agent SDK - Model ID Test")
    print("=" * 60)

    # AWS 認証確認
    try:
        aws_region = os.environ.get("AWS_REGION", "us-east-1")
        print(f"\nAWS Region: {aws_region}")
        sts_client = boto3.client("sts", region_name=aws_region)
        identity = sts_client.get_caller_identity()
        print(f"AWS Account: {identity['Account']}")
        print(f"AWS ARN: {identity['Arn']}")
    except Exception as e:
        print(f"\n❌ AWS authentication failed: {e}")
        sys.exit(1)

    # テスト用の簡単なプロンプト
    test_prompt = "Please respond with 'Hello from Claude!' and nothing else."

    # テスト 1: Claude Fable 5
    print("\n\n" + "=" * 60)
    print("TEST 1: Claude Fable 5 (Primary Model)")
    print("=" * 60)
    fable_result = await test_model("global.anthropic.claude-fable-5", test_prompt)

    # テスト 2: Claude Opus 5
    print("\n\n" + "=" * 60)
    print("TEST 2: Claude Opus 5 (Fallback Model)")
    print("=" * 60)
    opus_result = await test_model("global.anthropic.claude-opus-5", test_prompt)

    # 結果サマリー
    print("\n\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Claude Fable 5: {'✅ PASS' if fable_result else '❌ FAIL'}")
    print(f"Claude Opus 5:  {'✅ PASS' if opus_result else '❌ FAIL'}")

    if fable_result and opus_result:
        print("\n🎉 All tests passed! Both models are working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
