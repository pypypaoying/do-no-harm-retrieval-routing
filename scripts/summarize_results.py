from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dnh_router.reporting import markdown_table, summarize_run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()

    summary = summarize_run(args.run_dir)
    rows = []
    for item in summary["metrics"]:
        metrics = item["metrics"]
        rows.append({"file": Path(item["file"]).name, "records": metrics.get("records", ""), "folds": metrics.get("folds", "")})
    table = markdown_table(rows, ["file", "records", "folds"]) if rows else "No metrics found."
    path = Path(args.run_dir) / "summary.md"
    path.write_text(f"# Run Summary\n\n{table}\n", encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
