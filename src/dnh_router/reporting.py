from __future__ import annotations

from pathlib import Path
from typing import Any

from .io import read_json, write_json


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return "\n".join([header, sep, *body])


def summarize_run(run_dir: str | Path) -> dict[str, Any]:
    run_dir = Path(run_dir)
    manifest = read_json(run_dir / "manifest.json", default={}) or {}
    metrics = []
    for file in (run_dir / "metrics").glob("*.json") if (run_dir / "metrics").exists() else []:
        metrics.append({"file": str(file), "metrics": read_json(file, default={})})
    summary = {"run_dir": str(run_dir), "manifest": manifest, "metrics": metrics}
    write_json(run_dir / "summary.json", summary)
    return summary
