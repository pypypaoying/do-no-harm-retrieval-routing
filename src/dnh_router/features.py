from __future__ import annotations

from typing import Any

import numpy as np

from .parse import is_correct, normalize_label

FEATURE_NAMES = [
    "stability_quality",
    "stability_usage",
    "any_counterfactual_change",
    "zero_rag_disagreement",
    "conf_zero",
    "conf_rag",
    "conf_gap_rag_minus_zero",
    "context_sufficient",
    "suff_confidence",
    "targ_margin",
]


def _answer(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if isinstance(value, dict):
        return normalize_label(value.get("label") or value.get("answer"))
    return normalize_label(value)


def _confidence(record: dict[str, Any], key: str) -> float:
    value = record.get(key)
    if isinstance(value, dict) and value.get("confidence") is not None:
        return float(value["confidence"])
    return 0.5


def build_feature_row(record: dict[str, Any]) -> list[float]:
    a0 = _answer(record, "zero_context")
    ar = _answer(record, "rag")
    acfq = _answer(record, "cf_quality")
    acfu = _answer(record, "cf_usage")
    conf0 = _confidence(record, "zero_context")
    confr = _confidence(record, "rag")
    suff = record.get("sufficiency") or {}
    sufficient = bool(suff.get("sufficient", False)) if isinstance(suff, dict) else bool(suff)
    suff_conf = float(suff.get("confidence", 0.5)) if isinstance(suff, dict) else 0.5
    targ_margin = float(record.get("targ_margin", 0.0) or 0.0)
    return [
        float(ar == acfq),
        float(ar == acfu),
        float(ar != acfq or ar != acfu),
        float(a0 != ar),
        conf0,
        confr,
        confr - conf0,
        float(sufficient),
        suff_conf,
        targ_margin,
    ]


def oracle_action(record: dict[str, Any]) -> str:
    gold = record.get("gold")
    if is_correct(_answer(record, "rag"), gold):
        return "retrieve"
    if is_correct(_answer(record, "zero_context"), gold):
        return "no_retrieval"
    return "abstain"


def matrix(records: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    x = np.array([build_feature_row(record) for record in records], dtype=float)
    y = np.array([oracle_action(record) for record in records])
    return x, y
