import os

from dnh_router.parse import normalize_label, parse_confidence, parse_model_output
from dnh_router.prompts import format_context


def test_normalize_label_variants():
    assert normalize_label("Supported") == "true"
    assert normalize_label("refuted") == "false"
    assert normalize_label("not enough information") == "unknown"


def test_parse_model_output_json():
    parsed = parse_model_output('{"answer": "true", "confidence": 0.82}')
    assert parsed["label"] == "true"
    assert parsed["confidence"] == 0.82


def test_parse_confidence_percent():
    assert parse_confidence("confidence: 73%") == 0.73


def test_context_truncation():
    old = os.environ.get("DNH_MAX_CONTEXT_CHARS")
    os.environ["DNH_MAX_CONTEXT_CHARS"] = "10"
    try:
        assert "[TRUNCATED]" in format_context("a" * 20)
    finally:
        if old is None:
            os.environ.pop("DNH_MAX_CONTEXT_CHARS", None)
        else:
            os.environ["DNH_MAX_CONTEXT_CHARS"] = old
