from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dnh_router.io import write_jsonl


def run(command: list[str]) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="local-smoke")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    run_dir = root / "runs" / args.run_id
    data_path = run_dir / "data" / "synthetic.jsonl"
    candidates = run_dir / "candidates" / "echo.jsonl"
    sufficiency = run_dir / "autorate" / "echo.jsonl"
    metrics = run_dir / "metrics" / "router.json"
    tables = run_dir / "tables" / "router.tex"

    records = [
        {"id": str(i), "claim": f"Synthetic claim {i}", "gold": "true" if i % 2 == 0 else "false", "context": [{"text": f"Evidence {i}"}]}
        for i in range(12)
    ]
    write_jsonl(data_path, records)

    py = sys.executable
    run([py, str(root / "scripts" / "generate_candidates.py"), "--input", str(data_path), "--output", str(candidates), "--provider", "echo", "--model", "echo", "--limit", "12"])
    run([py, str(root / "scripts" / "autorate_sufficiency.py"), "--input", str(candidates), "--output", str(sufficiency), "--provider", "echo", "--model", "echo", "--limit", "12"])
    run([py, str(root / "scripts" / "train_router.py"), "--candidates", str(candidates), "--sufficiency", str(sufficiency), "--output", str(metrics), "--folds", "2"])
    run([py, str(root / "scripts" / "make_tables.py"), "--metrics", str(metrics), "--output", str(tables)])
    run([py, str(root / "scripts" / "summarize_results.py"), "--run-dir", str(run_dir)])
    print(f"Smoke test complete: {run_dir}")


if __name__ == "__main__":
    main()
