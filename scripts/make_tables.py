from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dnh_router.io import read_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    metrics = read_json(args.metrics, default={}) or {}
    rows = metrics.get("router", {}).get("points", [])
    lines = [
        r"\begin{tabular}{rrrr}",
        r"\toprule",
        r"Threshold & Coverage & Sel. Acc. & Accuracy \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{row['threshold']:.2f} & {row['coverage_mean']:.3f} & "
            f"{row['selective_accuracy_mean']:.3f} & {row['accuracy_mean']:.3f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
