from __future__ import annotations

import ast
import os
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


def _parse_maybe_list(value: Any) -> list[Any]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, list):
        return value
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return parsed
    except (ValueError, SyntaxError):
        pass
    return [part.strip() for part in text.split(",") if part.strip()]


def _truth_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    text = str(value).strip().lower()
    if text in {"true", "mostly-true", "half-true"}:
        return "true"
    if text in {"false", "mostly-false", "pants-fire"}:
        return "false"
    return normalize_label(text)


def load_raguard_csvs(claims_path: str, documents_path: str, limit: int | None = None) -> list[dict[str, Any]]:
    claims = pd.read_csv(claims_path)
    documents = pd.read_csv(documents_path)
    docs_by_id: dict[str, dict[str, Any]] = {}
    docs_by_claim: dict[str, list[dict[str, Any]]] = {}
    for _, row in documents.iterrows():
        doc_id = str(row.get("Document ID", "")).strip()
        claim_id = str(row.get("Claim ID", "")).strip()
        doc = {
            "id": doc_id,
            "title": "" if pd.isna(row.get("Title")) else str(row.get("Title")),
            "text": "" if pd.isna(row.get("Full Text")) else str(row.get("Full Text")),
            "label": "" if pd.isna(row.get("Document Label")) else str(row.get("Document Label")),
            "link": "" if pd.isna(row.get("Link")) else str(row.get("Link")),
        }
        if doc_id:
            docs_by_id[doc_id] = doc
        if claim_id:
            docs_by_claim.setdefault(claim_id, []).append(doc)

    records: list[dict[str, Any]] = []
    for idx, row in claims.iterrows():
        claim_id = str(row.get("Claim ID", idx)).strip()
        doc_ids = [str(item).strip() for item in _parse_maybe_list(row.get("Document IDs"))]
        doc_labels = [str(item).strip() for item in _parse_maybe_list(row.get("Document Labels"))]
        context = []
        for pos, doc_id in enumerate(doc_ids):
            doc = dict(docs_by_id.get(doc_id, {"id": doc_id, "text": "", "title": "", "label": "", "link": ""}))
            if pos < len(doc_labels) and doc_labels[pos]:
                doc["claim_document_label"] = doc_labels[pos]
            context.append(doc)
        if not context:
            context = docs_by_claim.get(claim_id, [])
        records.append(
            {
                "id": claim_id,
                "claim": "" if pd.isna(row.get("Claim")) else str(row.get("Claim")),
                "gold": _truth_value(row.get("Verdict")),
                "context": context,
                "source": {
                    "original_verdict": "" if pd.isna(row.get("Original Verdict")) else str(row.get("Original Verdict")),
                    "document_ids": doc_ids,
                    "document_labels": doc_labels,
                },
            }
        )
    return records[:limit] if limit else records


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
    local_candidates = [
        (Path("external_data/raguard/claims.csv"), Path("external_data/raguard/documents.csv")),
        (Path("data/raw/raguard/claims.csv"), Path("data/raw/raguard/documents.csv")),
    ]
    for claims_path, documents_path in local_candidates:
        if claims_path.exists() and documents_path.exists():
            return load_raguard_csvs(str(claims_path), str(documents_path), limit=limit)

    claims_source = os.getenv("RAGUARD_CLAIMS_URL", "https://huggingface.co/datasets/UCSC-IRKM/RAGuard/resolve/main/claims.csv")
    documents_source = os.getenv("RAGUARD_DOCUMENTS_URL", "https://huggingface.co/datasets/UCSC-IRKM/RAGuard/resolve/main/documents.csv")
    try:
        return load_raguard_csvs(claims_source, documents_source, limit=limit)
    except Exception:
        pass

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
