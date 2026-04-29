from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .io import write_jsonl
from .parse import normalize_label

CLAIM_KEYS = ("claim", "query", "question", "statement", "text")
LABEL_KEYS = ("label", "gold", "answer", "target", "veracity")
CONTEXT_KEYS = ("context", "documents", "docs", "ctxs", "passages", "evidence", "retrieved_docs")
ID_KEYS = ("id", "claim_id", "qid", "example_id")


def _pick(record: dict[str, Any], keys: tuple[str, ...]) -> Any:
    lower = {str(key).lower(): key for key in record.keys()}
    for key in keys:
        if key in lower and record[lower[key]] not in (None, ""):
            return record[lower[key]]
    return None


def _flatten_context(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, list):
        out = []
        for item in value:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or item.get("document") or str(item)
                out.append({"text": str(text), **{k: v for k, v in item.items() if k != "text"}})
            else:
                out.append({"text": str(item)})
        return out
    if isinstance(value, dict):
        text = value.get("text") or value.get("content") or value.get("document") or str(value)
        return [{"text": str(text), **{k: v for k, v in value.items() if k != "text"}}]
    return [{"text": str(value)}]


def normalize_record(record: dict[str, Any], idx: int) -> dict[str, Any]:
    claim = _pick(record, CLAIM_KEYS)
    label = _pick(record, LABEL_KEYS)
    context = _pick(record, CONTEXT_KEYS)
    sample_id = _pick(record, ID_KEYS) or idx
    return {
        "id": str(sample_id),
        "claim": "" if claim is None else str(claim),
        "gold": normalize_label(label),
        "context": _flatten_context(context),
        "source": record,
    }


def _records_from_dataframe(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [normalize_record(row.dropna().to_dict(), idx) for idx, (_, row) in enumerate(df.iterrows())]


def load_local_tables(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    files = [path] if path.is_file() else list(path.rglob("*"))
    records: list[dict[str, Any]] = []
    for file in files:
        suffix = file.suffix.lower()
        if suffix == ".csv":
            records.extend(_records_from_dataframe(pd.read_csv(file)))
        elif suffix in {".json", ".jsonl"}:
            df = pd.read_json(file, lines=suffix == ".jsonl")
            records.extend(_records_from_dataframe(df))
        elif suffix == ".parquet":
            records.extend(_records_from_dataframe(pd.read_parquet(file)))
    return records


def load_raguard(source: str = "UCSC-IRKM/RAGuard", split: str | None = "test", limit: int | None = None) -> list[dict[str, Any]]:
    try:
        from datasets import load_dataset

        ds = load_dataset(source, split=split)
        records = [normalize_record(dict(row), idx) for idx, row in enumerate(ds)]
    except Exception:
        from huggingface_hub import hf_hub_download, list_repo_files

        records = []
        for file_name in list_repo_files(source, repo_type="dataset"):
            if not file_name.lower().endswith((".csv", ".json", ".jsonl", ".parquet")):
                continue
            local = hf_hub_download(source, file_name, repo_type="dataset")
            records.extend(load_local_tables(local))
    return records[:limit] if limit else records


def write_dataset(records: list[dict[str, Any]], output: str | Path) -> None:
    write_jsonl(output, records)
