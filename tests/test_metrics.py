from dnh_router.metrics import coverage, evaluate_predictions, selective_accuracy


def test_selective_metrics_ignore_unknown():
    predictions = ["true", "unknown", "false"]
    gold = ["true", "true", "true"]
    assert coverage(predictions) == 2 / 3
    assert selective_accuracy(predictions, gold) == 0.5
    assert evaluate_predictions(predictions, gold)["accuracy"] == 1 / 3
