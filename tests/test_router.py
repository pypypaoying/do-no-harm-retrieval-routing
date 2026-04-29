from dnh_router.router import cross_validate_router


def test_router_cv_runs_on_small_records():
    records = []
    for idx in range(18):
        gold = "true" if idx % 2 == 0 else "false"
        records.append(
            {
                "id": str(idx),
                "gold": gold,
                "zero_context": {"label": gold if idx % 3 == 0 else "unknown", "confidence": 0.7},
                "rag": {"label": gold if idx % 3 != 0 else "unknown", "confidence": 0.8},
                "cf_quality": {"label": gold if idx % 2 == 0 else "unknown", "confidence": 0.6},
                "cf_usage": {"label": gold if idx % 2 == 1 else "unknown", "confidence": 0.6},
                "sufficiency": {"sufficient": idx % 2 == 0, "confidence": 0.75},
            }
        )
    result = cross_validate_router(records, folds=2, thresholds=[0.0, 0.5])
    assert len(result.points) == 2
    assert result.fold_points
