# Codex Cloud Task Prompts

Use these prompts with `codex cloud exec --env <ENV_ID> --branch <branch> "<prompt>"`.

## Task 1: Bootstrap and Smoke Tests

Install dependencies with `scripts/setup_cloud.sh`, run `python scripts/smoke_test.py --run-id cloud-smoke`,
then run `python -m pytest`. Report failures with the exact command output and do not start full generation.

## Task 2: RAGuard Download and 20-Example E2E

Run:

```bash
python scripts/download_data.py --config configs/raguard.yaml --output data/raguard.jsonl
python scripts/generate_candidates.py --input data/raguard.jsonl --output runs/raguard-smoke/candidates/echo.jsonl --provider echo --model echo --limit 20
python scripts/autorate_sufficiency.py --input runs/raguard-smoke/candidates/echo.jsonl --output runs/raguard-smoke/autorate/echo.jsonl --provider echo --limit 20
python scripts/train_router.py --candidates runs/raguard-smoke/candidates/echo.jsonl --sufficiency runs/raguard-smoke/autorate/echo.jsonl --output runs/raguard-smoke/metrics/router.json --folds 2
python scripts/summarize_results.py --run-dir runs/raguard-smoke
```

Verify the manifest exists and the metrics JSON is parseable.

## Task 3: Open-Source Full Generation

Run Llama 3 and Mistral full RAGuard candidate generation for `k=1` and `k=5`.
Use deterministic decoding and JSONL caching. Resume from existing records if interrupted.

## Task 4: API Autorating and Claude Sensitivity

Run Gemini sufficiency autorating for all generated records. Then run Claude Opus sensitivity on full RAGuard.
Use rate-limit retry and JSONL caching. Do not overwrite existing cached generations.

## Task 5: Router Training and Analysis

Run full router evaluation, ablations, TARG-style gate baseline, RC-RAG+fallback baseline,
random baseline, and oracle upper bound. Export JSON metrics, Markdown summary, LaTeX tables, and PDF/PNG figures.

## Task 6: Paper Draft

Fill `paper/main.tex` from generated metrics and tables. Keep unknown experimental results as explicit placeholders only
if the corresponding run failed; otherwise use generated values from the manifest.
