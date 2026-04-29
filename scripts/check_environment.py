from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def status(name: str, ok: bool, detail: str = "") -> None:
    mark = "OK" if ok else "MISSING"
    suffix = f" - {detail}" if detail else ""
    print(f"[{mark}] {name}{suffix}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))

    try:
        from dotenv import load_dotenv

        load_dotenv(root / ".env", override=False)
        status(".env loader", True, "python-dotenv available")
    except Exception as exc:
        status(".env loader", False, str(exc))

    print("\nPython")
    print(sys.version)
    print(f"cwd={Path.cwd()}")

    print("\nRequired local files")
    for rel in [
        "external_data/raguard/claims.csv",
        "external_data/raguard/documents.csv",
        "configs/raguard.yaml",
        "scripts/download_data.py",
    ]:
        path = root / rel
        status(rel, path.exists(), f"{path.stat().st_size} bytes" if path.exists() else "")

    print("\nPython packages")
    for module in ["numpy", "pandas", "sklearn", "yaml", "tqdm", "openai", "dotenv"]:
        status(module, has_module(module))

    print("\nOptional packages")
    for module in ["datasets", "huggingface_hub", "anthropic", "google.genai", "vllm", "torch"]:
        status(module, has_module(module))

    print("\nEnvironment variables")
    for name in [
        "DNH_MAX_CONTEXT_CHARS",
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_BASE_URL",
        "DASHSCOPE_API_KEY",
        "DASHSCOPE_BASE_URL",
        "KIMI_API_KEY",
        "KIMI_BASE_URL",
        "HF_TOKEN",
    ]:
        value = os.getenv(name)
        if "KEY" in name or name.endswith("TOKEN"):
            status(name, bool(value), "<set>" if value else "")
        else:
            status(name, bool(value), value or "")


if __name__ == "__main__":
    main()
