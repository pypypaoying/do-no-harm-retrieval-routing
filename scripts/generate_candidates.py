from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dnh_router.io import append_jsonl, read_jsonl, update_manifest
from dnh_router.parse import parse_model_output
from dnh_router.prompts import build_candidate_prompts
from dnh_router.providers import batched, make_provider


def existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {str(record.get("id")) for record in read_jsonl(path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--provider", required=True, choices=["echo", "vllm", "anthropic", "google", "openai_compatible", "kimi", "qwen", "deepseek"])
    parser.add_argument("--model", required=True)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--run-dir", default=None)
    args = parser.parse_args()

    records = read_jsonl(args.input)
    if args.limit:
        records = records[: args.limit]

    output = Path(args.output)
    done = existing_ids(output)
    todo = [record for record in records if str(record.get("id")) not in done]
    provider = make_provider(
        args.provider,
        args.model,
        max_tokens=args.max_new_tokens,
        temperature=args.temperature,
        label="auto" if args.provider == "echo" else "unknown",
    )

    for batch in tqdm(list(batched(todo, args.batch_size)), desc="generate"):
        flat_prompts: list[str] = []
        prompt_keys: list[tuple[int, str]] = []
        for idx, record in enumerate(batch):
            prompts = build_candidate_prompts(record, k=args.k)
            for key, prompt in prompts.items():
                prompt_keys.append((idx, key))
                flat_prompts.append(prompt)
        outputs = provider.generate(flat_prompts)
        enriched = [dict(record) for record in batch]
        for (idx, key), text in zip(prompt_keys, outputs):
            enriched[idx][key] = parse_model_output(text)
        for record in enriched:
            record["model"] = args.model
            record["provider"] = args.provider
            record["k"] = args.k
            append_jsonl(output, record)

    run_dir = args.run_dir or str(output.parents[1] if len(output.parents) > 1 else output.parent)
    update_manifest(run_dir, f"candidates:{args.model}:k{args.k}", {"path": str(output), "records": len(records)})
    print(f"Wrote candidates to {output}")


if __name__ == "__main__":
    main()
