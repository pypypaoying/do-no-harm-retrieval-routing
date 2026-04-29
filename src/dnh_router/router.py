from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from .features import matrix
from .metrics import evaluate_routes

ROUTES = ["abstain", "no_retrieval", "retrieve"]


@dataclass
class RouterResult:
    thresholds: list[float]
    points: list[dict[str, Any]]
    fold_points: list[dict[str, Any]]


def train_logistic(x: np.ndarray, y: np.ndarray, seed: int = 13) -> LogisticRegression:
    model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=seed,
    )
    model.fit(x, y)
    return model


def predict_routes(model: LogisticRegression, x: np.ndarray, threshold: float) -> list[str]:
    probs = model.predict_proba(x)
    classes = list(model.classes_)
    routes = []
    for row in probs:
        idx = int(np.argmax(row))
        route = str(classes[idx])
        if float(row[idx]) < threshold:
            route = "abstain"
        routes.append(route)
    return routes


def cross_validate_router(
    records: list[dict[str, Any]],
    folds: int = 5,
    thresholds: list[float] | None = None,
    seed: int = 13,
) -> RouterResult:
    thresholds = thresholds or [0.0, 0.25, 0.5, 0.65, 0.75, 0.85, 0.9, 0.95]
    x, y = matrix(records)
    n_splits = min(folds, max(2, len(records)))
    splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    fold_points: list[dict[str, Any]] = []
    for fold, (train_idx, test_idx) in enumerate(splitter.split(x, y)):
        model = train_logistic(x[train_idx], y[train_idx], seed=seed + fold)
        test_records = [records[int(i)] for i in test_idx]
        for threshold in thresholds:
            routes = predict_routes(model, x[test_idx], threshold)
            metrics = evaluate_routes(test_records, routes)
            fold_points.append({"fold": fold, "threshold": threshold, **metrics})

    points = []
    for threshold in thresholds:
        subset = [point for point in fold_points if point["threshold"] == threshold]
        if not subset:
            continue
        points.append(
            {
                "threshold": threshold,
                "coverage_mean": float(np.mean([p["coverage"] for p in subset])),
                "coverage_std": float(np.std([p["coverage"] for p in subset])),
                "selective_accuracy_mean": float(np.mean([p["selective_accuracy"] for p in subset])),
                "selective_accuracy_std": float(np.std([p["selective_accuracy"] for p in subset])),
                "accuracy_mean": float(np.mean([p["accuracy"] for p in subset])),
                "accuracy_std": float(np.std([p["accuracy"] for p in subset])),
            }
        )
    return RouterResult(thresholds=thresholds, points=points, fold_points=fold_points)
