from __future__ import annotations

import json
import re
from typing import Any

LABELS = ("true", "false", "unknown")


def normalize_label(value: Any) -> str:
    if value is None:
        return "unknown"
    text = str(value).strip().lower()
    text = text.replace("supported", "true").replace("refuted", "false")
    text = text.replace("yes", "true").replace("no", "false")
    if text in {"1", "t"}:
        return "true"
    if text in {"0", "f"}:
        return "false"
    if text in LABELS:
        return text
    for label in LABELS:
        if re.search(rf"\b{label}\b", text):
            return label
    if "not enough" in text or "cannot determine" in text or "insufficient" in text:
        return "unknown"
    return "unknown"


def parse_confidence(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number / 100.0 if number > 1 else number
    text = str(value)
    matches = re.findall(r"(?<!\d)(?:0?\.\d+|1(?:\.0+)?|\d{1,3})(?!\d)", text)
    if not matches:
        return None
    number = float(matches[-1])
    if number > 1:
        number /= 100.0
    return max(0.0, min(1.0, number))


def parse_model_output(text: str) -> dict[str, Any]:
    stripped = text.strip()
    parsed: dict[str, Any] = {}
    try:
        candidate = json.loads(stripped)
        if isinstance(candidate, dict):
            parsed.update(candidate)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
        if match:
            try:
                candidate = json.loads(match.group(0))
                if isinstance(candidate, dict):
                    parsed.update(candidate)
            except json.JSONDecodeError:
                pass

    label = normalize_label(parsed.get("answer") or parsed.get("label") or stripped)
    confidence = parse_confidence(parsed.get("confidence") or parsed.get("p_correct") or stripped)
    return {"label": label, "confidence": confidence, "raw": text}


def is_correct(prediction: Any, gold: Any) -> bool:
    pred = normalize_label(prediction)
    label = normalize_label(gold)
    return pred != "unknown" and pred == label
