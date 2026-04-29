from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dnh_router.io import read_jsonl, update_manifest, write_json
from dnh_router.metrics import evaluate_routes
from dnh_router.router import cross_validate_router


def merge_sufficiency(candidates: list[dict], sufficiency_path: str | None) -> list[dict]:
    if not sufficiency_path:
        return candidates
    suff_records = {str(record.get("id")): record.get("sufficiency") for record in read_jsonl(sufficiency_path)}
    merged = []
    for record in candidates:
        enriched = dict(record)
        if str(record.get("id")) in suff_records:
            enriched["sufficiency"] = suff_records[str(record.get("id"))]
        merged.append(enriched)
    return merged


def baseline_routes(records: list[dict], name: str) -> list[str]:
    if name == "zero_context":
        return ["no_retrieval"] * len(records)
    if name == "rag":
        return ["retrieve"] * len(records)
    if name == "abstain":
        return ["abstain"] * len(records)
    if name == "rc_rag_fallback":
        routes = []
        for record in records:
            ar = record.get("rag", {})
            acfq = record.get("cf_quality", {})
            acfu = record.get("cf_usage", {})
            keep = ar.get("label") == acfq.get("label") and ar.get("label") == acfu.get("label")
            routes.append("retrieve" if keep else "no_retrieval")
        return routes
    if name == "targ_style_gate":
        routes = []
        for record in records:
            a0 = record.get("zero_context", {})
            ar = record.get("rag", {})
            conf0 = float(a0.get("confidence", 0.5) if isinstance(a0, dict) else 0.5)
            confr = float(ar.get("confidence", 0.5) if isinstance(ar, dict) else 0.5)
            routes.append("retrieve" if confr > conf0 else "no_retrieval")
        return routes
    raise ValueError(f"Unknown baseline {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--sufficiency")
    parser.add_argument("--output", required=True)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--run-dir", default=None)
    args = parser.parse_args()

    records = merge_sufficiency(read_jsonl(args.candidates), args.sufficiency)
    result = cross_validate_router(records, folds=args.folds, seed=args.seed)
    baselines = {
        name: evaluate_routes(records, baseline_routes(records, name))
        for name in ["zero_context", "rag", "abstain", "rc_rag_fallback", "targ_style_gate"]
    }
    payload = {
        "records": len(records),
        "folds": args.folds,
        "router": {"points": result.points, "fold_points": result.fold_points},
        "baselines": baselines,
    }
    write_json(args.output, payload)
    run_dir = args.run_dir or str(Path(args.output).parents[1] if len(Path(args.output).parents) > 1 else Path(args.output).parent)
    update_manifest(run_dir, "router_metrics", {"path": args.output, "records": len(records)})
    print(f"Wrote router metrics to {args.output}")


if __name__ == "__main__":
    main()
