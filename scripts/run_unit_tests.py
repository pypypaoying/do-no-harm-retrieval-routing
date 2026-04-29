from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    failures = []
    count = 0
    for path in sorted((root / "tests").glob("test_*.py")):
        module = load_module(path)
        for name in dir(module):
            if not name.startswith("test_"):
                continue
            count += 1
            try:
                getattr(module, name)()
            except Exception as exc:
                failures.append((f"{path.name}::{name}", exc))
    if failures:
        for name, exc in failures:
            print(f"FAIL {name}: {exc}")
        raise SystemExit(1)
    print(f"Passed {count} unit tests")


if __name__ == "__main__":
    main()
