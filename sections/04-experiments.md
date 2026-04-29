## Experiments

### Experimental Setup

**Primary baseline alignment (CRITICAL).**
- For **RC-RAG**, we adopt the RC-NQ/RC-TQ datasets, the keep/discard framing, and the risk/carefulness/alignment/coverage metrics.
- For **RAGuard**, we adopt the zero-context vs standard RAG vs oracle-retrieval settings and report accuracy; for routing we report accuracy–coverage curves.

**Base models** (≥2):

| Model | Size | Download Link | Notes |
|---|---:|---|---|
| Meta Llama 3 Instruct | 8B | https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct | Matches RAGuard open-source backbone family |
| Mistral Instruct | 7B | https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2 | Matches RAGuard open-source backbone family |
| Claude Opus 4.7 | API | https://www.anthropic.com/claude/opus | Black-box model for sensitivity + RC-RAG-style comparison (re-run baselines) |

**Benchmarks** (≥2):
- **RAGuard**: https://huggingface.co/datasets/UCSC-IRKM/RAGuard
- **RC-RAG benchmark (RC-TQ / RC-NQ)**: https://github.com/ict-bigdatalab/RC-RAG

**Retrieval.**
- For RAGuard “Standard RAG”, retrieve from the provided RAGuard corpus; prefer an open embedding model (e.g., `BAAI/bge-m3`) to avoid external dependencies.
- Evaluate both `k=1` and `k=5` retrieval, consistent with RAGuard’s reported settings.

**Calibration / overfitting controls.**
- RAGuard has 2,648 claims. We will use **stratified 5-fold cross-validation** to train and evaluate the router (logistic regression / shallow tree), reporting mean±std across folds for selective accuracy at fixed coverage points.
- For RC-NQ/RC-TQ, we follow RC-RAG’s test-set evaluation protocol but tune routing thresholds on a held-out subset (or via cross-validation if no dev split is provided).

**Sufficiency autorater.**
- Use a fixed, explicit autorater model: **`gemini-3.1-pro`** as the sufficiency autorater (query+context → sufficient/insufficient), and do not reuse the generator model for sufficiency labels.

**Resource Estimate** (order-of-magnitude):
- RAGuard has 2,648 claims. Per claim we generate {a₀, aᵣ, a_cf-q, a_cf-u} (≈4 forward passes) and compute one sufficiency label (≈1 autorater call).
- If we evaluate **2 open-source generators** (Llama 3 + Mistral): ≈ (4+1)×2×2,648 ≈ **26k generator calls + 5k autorater calls**.
- If we additionally evaluate **Claude Opus 4.7** as a third generator: add ≈ (4×2,648) ≈ **10.6k API calls** on the full RAGuard test set.
- With 5-fold CV, router training is lightweight (logistic regression) and the dominant cost remains answer generation.

### Experimental Coverage

- **Benchmarks**: RAGuard + RC-RAG (RC-TQ/RC-NQ)
- **Base models**: Llama-3-Instruct (8B) + Mistral-7B-Instruct
- **Ablations**: at least one (remove sufficiency; remove stability)

### Benchmarks and Metrics

| Benchmark | Description | Metrics | Split | Download Link | Evaluation Script |
|---|---|---|---|---|---|
| RAGuard | Binary fact-checking with supporting/misleading/irrelevant docs | Accuracy; selective accuracy vs coverage | test | https://huggingface.co/datasets/UCSC-IRKM/RAGuard | Simple constrained-output evaluation (restrict to {true,false,unknown}; compute accuracy vs gold label) |
| RC-TQ / RC-NQ | Factoid QA for RAG risk control | risk/carefulness/alignment/coverage (RC-RAG) | test | https://github.com/ict-bigdatalab/RC-RAG | RC-RAG codebase |

### Main Results

**Published baselines (RAGuard Table 4; Accuracy %):**

| Method | Base Model | Benchmark | Accuracy (paper) | Source | Notes |
|---|---|---|---:|---|---|
| Zero-context | Llama 3 | RAGuard | 62.50 | [RAGuard Table 4](https://huggingface.co/datasets/UCSC-IRKM/RAGuard) | Published (1 run; paper setting) |
| Standard RAG (k=1) | Llama 3 | RAGuard | 59.40 | [RAGuard Table 4](https://huggingface.co/datasets/UCSC-IRKM/RAGuard) | Published (1 run; paper setting) |
| Standard RAG (k=5) | Llama 3 | RAGuard | 61.37 | [RAGuard Table 4](https://huggingface.co/datasets/UCSC-IRKM/RAGuard) | Published (1 run; paper setting) |
| Oracle misleading-only | Llama 3 | RAGuard | 36.81 | [RAGuard Table 4](https://huggingface.co/datasets/UCSC-IRKM/RAGuard) | Published (1 run; paper setting) |
| Zero-context | Mistral | RAGuard | 63.97 | [RAGuard Table 4](https://huggingface.co/datasets/UCSC-IRKM/RAGuard) | Published (1 run; paper setting) |
| Standard RAG (k=1) | Mistral | RAGuard | 59.14 | [RAGuard Table 4](https://huggingface.co/datasets/UCSC-IRKM/RAGuard) | Published (1 run; paper setting) |
| Standard RAG (k=5) | Mistral | RAGuard | 58.91 | [RAGuard Table 4](https://huggingface.co/datasets/UCSC-IRKM/RAGuard) | Published (1 run; paper setting) |
| Oracle misleading-only | Mistral | RAGuard | 28.22 | [RAGuard Table 4](https://huggingface.co/datasets/UCSC-IRKM/RAGuard) | Published (1 run; paper setting) |
| **RC-RAG + zero-context fallback** | Llama 3 | RAGuard | **TBD** | generated run manifest | To be verified |
| **TARG-style confidence gate** | Llama 3 | RAGuard | **TBD** | generated run manifest | Added strong adaptive-retrieval baseline |
| **Ours (multi-signal router)** | Llama 3 | RAGuard | **TBD** | generated run manifest | To be verified |

**Published baselines (RC-RAG Table 3; dense retriever):**

| Method | Base Model | Benchmark | risk↓ | carefulness↑ | alignment↑ | coverage↑ | Source | Notes |
|---|---|---|---:|---:|---:|---:|---|---|
| Priori | ChatGPT | RC-TQ | 16.23 | 57.30 | 79.68 | 75.49 | [RC-RAG Table 3](https://github.com/ict-bigdatalab/RC-RAG) | Published (dense retriever; paper setting) |
| RC-RAG (Ours in paper) | ChatGPT | RC-TQ | 14.94 | 65.37 | 75.38 | 66.55 | [RC-RAG Table 3](https://github.com/ict-bigdatalab/RC-RAG) | Published (dense retriever; paper setting) |
| Priori | ChatGPT | RC-NQ | 34.72 | 55.23 | 70.55 | 65.26 | [RC-RAG Table 3](https://github.com/ict-bigdatalab/RC-RAG) | Published (dense retriever; paper setting) |
| RC-RAG (Ours in paper) | ChatGPT | RC-NQ | 35.22 | 62.86 | 66.23 | 53.24 | [RC-RAG Table 3](https://github.com/ict-bigdatalab/RC-RAG) | Published (dense retriever; paper setting) |
| Priori | Mistral | RC-TQ | 21.95 | 33.87 | 77.14 | 86.38 | [RC-RAG Table 3](https://github.com/ict-bigdatalab/RC-RAG) | Published (dense retriever; paper setting) |
| RC-RAG (Ours in paper) | Mistral | RC-TQ | 19.00 | 52.87 | 72.78 | 71.14 | [RC-RAG Table 3](https://github.com/ict-bigdatalab/RC-RAG) | Published (dense retriever; paper setting) |
| Priori | Mistral | RC-NQ | 42.61 | 28.60 | 61.52 | 82.63 | [RC-RAG Table 3](https://github.com/ict-bigdatalab/RC-RAG) | Published (dense retriever; paper setting) |
| RC-RAG (Ours in paper) | Mistral | RC-NQ | 38.22 | 52.98 | 63.60 | 60.66 | [RC-RAG Table 3](https://github.com/ict-bigdatalab/RC-RAG) | Published (dense retriever; paper setting) |
| **RC-RAG + zero-context fallback** | Mistral | RC-TQ/RC-NQ | **TBD** | **TBD** | **TBD** | **TBD** | generated run manifest | Needs re-run (not in paper) |
| **TARG-style confidence gate** | Mistral | RC-TQ/RC-NQ | **TBD** | **TBD** | **TBD** | **TBD** | generated run manifest | Added strong adaptive-retrieval baseline |
| **Ours (multi-signal router)** | Mistral | RC-TQ/RC-NQ | **TBD** | **TBD** | **TBD** | **TBD** | generated run manifest | To be verified |

Primary reported outcome for the paper is not a single scalar, but **accuracy–coverage curves** on RAGuard and **risk/carefulness vs coverage** curves on RC-RAG.

### Ablation Studies

| Variant | What’s changed | Expected finding |
|---|---|---|
| Ours (full) | stability + sufficiency + confidence/disagreement | Best frontier |
| TARG-style gate | confidence-only retrieval gate | Tests whether a simple adaptive retrieval baseline is already enough |
| w/o sufficiency | remove sufficiency signal | Worse on misleading retrieval regime |
| w/o stability | remove counterfactual stability | More harm on retrieval-conditioned errors |
| w/o no-retrieval channel | only retrieve vs abstain | Loses ability to recover correct zero-context answers |

### Experimental Rigor

- **Seeds**: Run ≥3 seeds for any stochastic decoding/sampling components; use deterministic decoding where possible for label outputs.
- **Matched-coverage evaluation**: Report accuracy at fixed coverage levels to prevent “answer less” confounds.
- **Artifact checks (RAGuard)**: Measure correlation of sufficiency predictions with document length/style; report performance stratified by these covariates.
- **Sanity checks**: Random router baseline; oracle router upper bound; verify that retrieval depth (k=1 vs k=5) reproduces the qualitative trend that larger k increases misleading-retrieval exposure (RAGuard misleading retrieval recall increases from 21.3% to 44.8%).

---
