from __future__ import annotations

from collections import Counter
from typing import Any

from .parse import is_correct, normalize_label


def accuracy(predictions: list[str], gold: list[str]) -> float:
    if not predictions:
        return 0.0
    return sum(is_correct(pred, label) for pred, label in zip(predictions, gold)) / len(predictions)


def coverage(predictions: list[str]) -> float:
    if not predictions:
        return 0.0
    return sum(normalize_label(pred) != "unknown" for pred in predictions) / len(predictions)


def selective_accuracy(predictions: list[str], gold: list[str]) -> float:
    answered = [(pred, label) for pred, label in zip(predictions, gold) if normalize_label(pred) != "unknown"]
    if not answered:
        return 0.0
    return sum(is_correct(pred, label) for pred, label in answered) / len(answered)


def evaluate_predictions(predictions: list[str], gold: list[str]) -> dict[str, float]:
    return {
        "accuracy": accuracy(predictions, gold),
        "coverage": coverage(predictions),
        "selective_accuracy": selective_accuracy(predictions, gold),
    }


def route_to_prediction(record: dict[str, Any], route: str) -> str:
    if route == "retrieve":
        value = record.get("rag")
    elif route == "no_retrieval":
        value = record.get("zero_context")
    else:
        return "unknown"
    if isinstance(value, dict):
        return normalize_label(value.get("label") or value.get("answer"))
    return normalize_label(value)


def evaluate_routes(records: list[dict[str, Any]], routes: list[str]) -> dict[str, Any]:
    predictions = [route_to_prediction(record, route) for record, route in zip(records, routes)]
    gold = [normalize_label(record.get("gold")) for record in records]
    out: dict[str, Any] = evaluate_predictions(predictions, gold)
    out["route_counts"] = dict(Counter(routes))
    return out


def frontier(records: list[dict[str, Any]], routes_by_threshold: dict[float, list[str]]) -> list[dict[str, Any]]:
    points = []
    for threshold, routes in sorted(routes_by_threshold.items()):
        metrics = evaluate_routes(records, routes)
        points.append({"threshold": threshold, **metrics})
    return points
