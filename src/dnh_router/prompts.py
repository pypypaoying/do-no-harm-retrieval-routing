from __future__ import annotations

import os
from typing import Any


SYSTEM_FACT_CHECK = (
    "You are a careful fact-checking assistant. "
    "Return only JSON with keys answer and confidence. "
    "answer must be one of true, false, unknown. "
    "confidence must be a number between 0 and 1."
)


def _max_context_chars() -> int:
    return int(os.getenv("DNH_MAX_CONTEXT_CHARS", "6000"))


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n[TRUNCATED]"


def format_context(context: Any, k: int | None = None) -> str:
    max_chars = _max_context_chars()
    if context is None:
        return ""
    if isinstance(context, str):
        return _truncate(context, max_chars)
    if isinstance(context, list):
        rows = context[:k] if k else context
        parts: list[str] = []
        for idx, item in enumerate(rows, start=1):
            if isinstance(item, dict):
                text = item.get("text") or item.get("content") or item.get("document") or str(item)
            else:
                text = str(item)
            parts.append(f"[{idx}] {text}")
        return _truncate("\n".join(parts), max_chars)
    return _truncate(str(context), max_chars)


def zero_context_prompt(claim: str) -> str:
    return (
        f"{SYSTEM_FACT_CHECK}\n\n"
        "Decide whether the claim is true, false, or unknown using only your parametric knowledge.\n"
        f"Claim: {claim}\n"
    )


def rag_prompt(claim: str, context: Any, k: int | None = None) -> str:
    return (
        f"{SYSTEM_FACT_CHECK}\n\n"
        "Use the retrieved context if it is relevant and decisive. If the context is insufficient, answer unknown.\n"
        f"Claim: {claim}\n\nRetrieved context:\n{format_context(context, k)}\n"
    )


def cf_quality_prompt(claim: str, context: Any, k: int | None = None) -> str:
    return (
        f"{SYSTEM_FACT_CHECK}\n\n"
        "The retrieved context may contain misleading or low-quality evidence. "
        "Re-evaluate the claim cautiously and answer true, false, or unknown.\n"
        f"Claim: {claim}\n\nRetrieved context:\n{format_context(context, k)}\n"
    )


def cf_usage_prompt(claim: str, context: Any, k: int | None = None) -> str:
    return (
        f"{SYSTEM_FACT_CHECK}\n\n"
        "First consider whether the retrieved context should be ignored. "
        "Then return the final answer only as JSON.\n"
        f"Claim: {claim}\n\nRetrieved context:\n{format_context(context, k)}\n"
    )


def sufficiency_prompt(claim: str, context: Any, k: int | None = None) -> str:
    return (
        "You are an evidence sufficiency autorater. Return only JSON with keys sufficient and confidence. "
        "sufficient must be true if the context contains enough information to decide whether the claim is true or false; "
        "otherwise false. confidence must be between 0 and 1.\n\n"
        f"Claim: {claim}\n\nContext:\n{format_context(context, k)}\n"
    )


def build_candidate_prompts(record: dict[str, Any], k: int | None = None) -> dict[str, str]:
    claim = record.get("claim") or record.get("query") or record.get("question") or ""
    context = record.get("context") or record.get("documents") or record.get("ctxs") or ""
    return {
        "zero_context": zero_context_prompt(claim),
        "rag": rag_prompt(claim, context, k),
        "cf_quality": cf_quality_prompt(claim, context, k),
        "cf_usage": cf_usage_prompt(claim, context, k),
    }
