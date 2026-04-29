# Do-No-Harm Retrieval Routing

This repository contains the proposal, experiment scaffold, and paper workspace for
**Do-No-Harm Retrieval Routing: Multi-Signal Risk Control for Misleading Retrievals**.

The project turns a proposal into a reproducible experiment pipeline:

1. Load RAGuard / RC-RAG-style records.
2. Generate zero-context, RAG, and counterfactual answers.
3. Add sufficiency and routing features.
4. Train an auditable router.
5. Export metrics, tables, figures, and paper artifacts from a run manifest.

## Repository Layout

- `proposal.md`, `sections/`: strengthened proposal and section files.
- `src/dnh_router/`: shared Python package for data, prompts, metrics, features, and routing.
- `scripts/`: command-line entrypoints for data download, generation, autorating, training, and reports.
- `configs/`: experiment configuration files and Codex Cloud task prompts.
- `runs/`: generated run artifacts. Kept out of Git except `.gitkeep`.
- `paper/`: paper skeleton and bibliography.
- `tests/`: smoke/unit tests that do not require API keys.

## Local Smoke Test

```powershell
python -m pip install -e .
python scripts/smoke_test.py --run-id local-smoke
python -m pytest
```

The smoke test uses the built-in `echo` provider and does not call external APIs.
For VSCode-based local runs, see `docs/vscode_local_run.md`.

## Codex Cloud Setup

Create a private GitHub repository, connect it at <https://chatgpt.com/codex>,
and create a Codex Cloud environment with network access and these secrets:

- `HF_TOKEN`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`

Use `scripts/setup_cloud.sh` as the environment setup script.
Detailed setup notes are in `docs/codex_cloud_setup.md`.

After the environment exists, submit tasks from the local CLI:

```powershell
codex cloud exec --env <ENV_ID> --branch main "Run Task 1 from configs/codex_cloud_tasks.md"
```

## Full Experiment Order

1. Bootstrap repo and run smoke tests.
2. Download and normalize RAGuard.
3. Generate candidates for Llama/Mistral.
4. Run Gemini sufficiency autorating and Claude sensitivity.
5. Train routers, ablations, and baselines.
6. Generate paper tables/figures and fill the paper.

Do not hand-edit result tables in the paper. Generate them from `runs/<run-id>/manifest.json`.

## Hugging Face Network Fallback

If Codex Cloud returns `httpx.ProxyError: 403 Forbidden` when accessing Hugging Face,
download the two RAGuard CSV files outside Codex Cloud and commit them under
`external_data/raguard/`:

```text
external_data/raguard/claims.csv
external_data/raguard/documents.csv
```

The default command will then read the local mirror automatically:

```bash
python scripts/download_data.py --config configs/raguard.yaml --output data/raguard.jsonl
```

You can also pass local/mirrored paths explicitly:

```bash
python scripts/download_data.py \
  --claims-csv data/raw/raguard/claims.csv \
  --documents-csv data/raw/raguard/documents.csv \
  --output data/raguard.jsonl
```

You can also set:

```bash
export RAGUARD_CLAIMS_URL=<mirror-or-signed-url-to-claims.csv>
export RAGUARD_DOCUMENTS_URL=<mirror-or-signed-url-to-documents.csv>
```
