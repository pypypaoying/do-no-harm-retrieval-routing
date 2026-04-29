from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dnh_router.io import append_jsonl, read_jsonl, update_manifest
from dnh_router.parse import parse_confidence
from dnh_router.prompts import sufficiency_prompt
from dnh_router.providers import batched, make_provider


def parse_sufficiency(text: str) -> dict[str, float | bool | str]:
    sufficient = False
    confidence = parse_confidence(text) or 0.5
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        parsed = json.loads(match.group(0)) if match else {}
    if isinstance(parsed, dict):
        value = parsed.get("sufficient")
        if isinstance(value, bool):
            sufficient = value
        elif isinstance(value, str):
            sufficient = value.strip().lower() in {"true", "yes", "sufficient"}
        confidence = parse_confidence(parsed.get("confidence")) or confidence
    return {"sufficient": sufficient, "confidence": confidence, "raw": text}


def existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {str(record.get("id")) for record in read_jsonl(path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--provider", required=True, choices=["echo", "google"])
    parser.add_argument("--model", default="gemini-3.1-pro")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--run-dir", default=None)
    args = parser.parse_args()

    records = read_jsonl(args.input)
    if args.limit:
        records = records[: args.limit]
    output = Path(args.output)
    done = existing_ids(output)
    todo = [record for record in records if str(record.get("id")) not in done]
    provider = make_provider(args.provider, args.model, label="auto" if args.provider == "echo" else "unknown")

    for batch in tqdm(list(batched(todo, args.batch_size)), desc="autorate"):
        prompts = [sufficiency_prompt(record.get("claim", ""), record.get("context"), args.k) for record in batch]
        outputs = provider.generate(prompts)
        for record, text in zip(batch, outputs):
            enriched = dict(record)
            enriched["sufficiency"] = parse_sufficiency(text)
            enriched["autorater_model"] = args.model
            append_jsonl(output, enriched)

    run_dir = args.run_dir or str(output.parents[1] if len(output.parents) > 1 else output.parent)
    update_manifest(run_dir, f"sufficiency:{args.model}:k{args.k}", {"path": str(output), "records": len(records)})
    print(f"Wrote sufficiency ratings to {output}")


if __name__ == "__main__":
    main()
