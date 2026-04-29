from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dnh_router.parse import parse_model_output
from dnh_router.providers import make_provider


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True, choices=["qwen", "kimi", "deepseek", "openai_compatible", "anthropic", "google", "echo"])
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url-env", default=None)
    parser.add_argument("--api-key-env", default=None)
    args = parser.parse_args()

    if args.base_url_env:
        print(f"{args.base_url_env}={os.getenv(args.base_url_env, '<missing>')}")
    if args.api_key_env:
        print(f"{args.api_key_env}={'<set>' if os.getenv(args.api_key_env) else '<missing>'}")

    provider = make_provider(
        args.provider,
        args.model,
        max_tokens=32,
        temperature=0.0,
        api_key_env=args.api_key_env or "OPENAI_COMPATIBLE_API_KEY",
        base_url_env=args.base_url_env or "OPENAI_COMPATIBLE_BASE_URL",
        label="auto",
    )
    outputs = provider.generate([
        'Return only JSON: {"answer": "true", "confidence": 0.99}'
    ])
    parsed = parse_model_output(outputs[0])
    print("raw_output=", outputs[0])
    print("parsed_label=", parsed["label"])
    print("parsed_confidence=", parsed["confidence"])


if __name__ == "__main__":
    main()
