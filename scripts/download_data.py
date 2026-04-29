from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dnh_router.config import load_config
from dnh_router.data import load_local_tables, load_raguard, write_dataset
from dnh_router.io import update_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/raguard.yaml")
    parser.add_argument("--source")
    parser.add_argument("--claims-csv")
    parser.add_argument("--documents-csv")
    parser.add_argument("--split")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    config = load_config(args.config) if args.config else {}
    data_cfg = config.get("data", {})
    source = args.source or data_cfg.get("source", "UCSC-IRKM/RAGuard")
    split = args.split or data_cfg.get("split", "test")
    limit = args.limit if args.limit is not None else data_cfg.get("limit")

    if args.claims_csv and args.documents_csv:
        from dnh_router.data import load_raguard_csvs

        records = load_raguard_csvs(args.claims_csv, args.documents_csv, limit=limit)
    elif Path(source).exists():
        records = load_local_tables(source)
        records = records[:limit] if limit else records
    else:
        records = load_raguard(source=source, split=split, limit=limit)

    write_dataset(records, args.output)
    run_dir = Path(config.get("run", {}).get("output_dir", "runs/manual"))
    update_manifest(run_dir, "data", {"output": args.output, "records": len(records), "source": source, "split": split})
    print(f"Wrote {len(records)} records to {args.output}")


if __name__ == "__main__":
    main()
