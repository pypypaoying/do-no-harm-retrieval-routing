# Proposal Scoring System

Target use: score the proposal, experiment package, and final paper draft with one stable rubric.

## 100-Point Rubric

| Dimension | Weight | Scoring rule |
|---|---:|---|
| Novelty and differentiation | 20 | Clear gap vs RC-RAG, Sufficient Context, TARG, CF-RAG, Knowledgeable-R1, and RAGRouter-Bench; no local broken citation paths. |
| Importance | 15 | Retrieval-induced harm is motivated with benchmark evidence and practical deployment relevance. |
| Soundness | 25 | Baselines are strong, splits avoid leakage, metrics are matched-coverage, and all claims are reproducible from manifests. |
| Feasibility | 15 | Data, models, API keys, and Cloud steps are specified; smoke tests run without secrets. |
| Sharpness | 15 | Proceed / pivot / refute criteria are numeric and tied to coverage-frontier outcomes. |
| Writing and reproducibility | 10 | Clear short-paper framing, generated tables, complete README, and no hand-filled result claims. |

## Penalties

- -10 if a primary reference or result source is a broken local path.
- -10 if RC-RAG+fallback is not implemented as the primary baseline.
- -8 if TARG-style or comparable adaptive retrieval gate is omitted.
- -8 if thresholds or coverage points are tuned on the test fold.
- -6 if paper tables are manually edited instead of generated from `runs/<run-id>/manifest.json`.
- -5 if API model names or setup steps are ambiguous.

## Current Target

The prior evaluation gave a quality score of 3.67/5. The repository changes aim for the equivalent of at least 82/100:

- remove non-standard scope section;
- repair broken local citation paths;
- add TARG and RAGRouter-Bench competitor positioning;
- add reproducible code, smoke tests, and manifest-driven result generation;
- make Cloud execution prerequisites explicit.
