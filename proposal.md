# Do-No-Harm Retrieval Routing: Multi-Signal Risk Control for Misleading Retrievals

## Introduction

### Context and Motivation

This short-paper proposal targets CIKM 2026 / EMNLP 2026 as a method contribution: an inference-time routing / selective-prediction layer for RAG. All evaluation is fully automated with existing benchmark labels, and the experiment avoids search-engine APIs.

Retrieval-augmented generation (RAG) is widely used to make large language models (LLMs) more factual by conditioning generation on retrieved documents. In practical deployments (enterprise search, assistants, fact-checking, customer support), the retrieval layer is rarely “clean”: retrieved content can be incomplete, topically related but not decisive, or actively misleading.

Recent benchmarks suggest that this is not a corner case. **RAGuard** is a political fact-checking benchmark where each claim is associated with documents labeled as supporting, misleading, or irrelevant. It shows that adding retrieved context can *reduce* accuracy relative to answering without retrieval: e.g., for **Llama 3**, accuracy drops from **62.50** (zero-context) to **59.40** (RAG-1) and **61.37** (RAG-5), and collapses to **36.81** when given only misleading documents (oracle misleading-only) (RAGuard Table 4).

At the same time, abstention / risk control is becoming a standard requirement for high-stakes LLM systems. **RC-RAG (Controlling Risk of Retrieval-augmented Generation)** proposes a counterfactual prompting framework that decides whether to keep or discard a RAG answer based on whether the answer changes under “counterfactual” prompts that challenge retrieval quality or retrieval usage, and evaluates using risk-aware metrics (risk/carefulness/alignment/coverage) on RC-NQ/RC-TQ (Chen et al., 2024).

### The Problem

Despite progress, there is still a gap between (i) *detecting uncertainty under retrieval* and (ii) *making a routing decision that avoids retrieval-induced harm*. In particular:

- Benchmarks like RAGuard reveal a deployment-relevant failure mode: **retrieval can flip a correct no-retrieval answer into an incorrect answer**.
- Existing risk-control methods (e.g., RC-RAG) focus on “keep vs discard” judgments **within a retrieval-conditioned pipeline**. Their “stability” signal compares the initial RAG answer to answers generated under counterfactual prompts, which still operate in a retrieval setting. This leaves open the question: **when should the system ignore retrieval and fall back to a no-retrieval answer (or abstain), rather than trying to stabilize the retrieval-conditioned answer?**

A practitioner-facing decision rule is missing: *when retrieval is likely to reduce correctness, the system should either answer without retrieval or abstain*, while still using retrieval when it helps.

### Key Insight and Hypothesis

**Key insight.** Counterfactual stability is informative, but it is an incomplete control signal for routing because it does not explicitly compare against a no-retrieval counterfactual, and it can be confounded by (a) retrieval-conditioned answers that remain stable under counterfactual prompts while being wrong, and (b) benign answer variation that triggers “discard” even when retrieval is helpful.

**Hypothesis.** A simple router that combines (1) **counterfactual stability features** (RC-RAG), (2) an independent **context-sufficiency signal** (Sufficient Context), and (3) **confidence / disagreement features** between no-retrieval and retrieval answers can improve the **accuracy–coverage frontier** over a strong trivial baseline: **RC-RAG + zero-context fallback**.

Here, the **accuracy–coverage frontier** means: as we vary a routing threshold, we trade off **coverage** (fraction of inputs not abstained) against **selective accuracy** (accuracy on the answered subset); a better frontier achieves higher accuracy at the same coverage.

The outcome is genuinely uncertain because the trivial RC-RAG+fallback may already eliminate most retrieval harm, and sufficiency signals may be dataset-artifact-driven (e.g., correlated with document style/length) rather than reflecting genuine evidence adequacy.

---

## Proposed Approach

### Overview

We propose a lightweight **Do-No-Harm Router** that chooses, for each query:

1) **Answer with retrieval** (standard RAG)
2) **Answer without retrieval** (zero-context)
3) **Abstain** (return “unknown”)

The design goal is not “always be cautious”; it is to **capture retrieval upside on clean queries while avoiding retrieval downside on misleading queries**, quantified via accuracy–coverage curves.

### Method Details

**Candidate answers per query.** For each input query/claim *x* and retrieved context *C*:

- **a₀**: zero-context answer (no retrieval)
- **aᵣ**: standard RAG answer (with retrieval)
- **a_cf-q**, **a_cf-u**: answers under RC-RAG-style counterfactual prompts that challenge (i) retrieval quality and (ii) retrieval usage

For RAGuard, we constrain the generator to output one of {`true`, `false`, `unknown`} to keep evaluation automated and robust.

**Features.** We compute a small feature vector per instance:

- **Stability features (RC-RAG):** whether aᵣ matches a_cf-q and/or a_cf-u (and whether either counterfactual round changes the answer).
- **Disagreement features:** whether a₀ ≠ aᵣ.
- **Confidence features:** self-reported P(correct) (calibration-style prompting) for a₀ and aᵣ; optionally entropy/token-prob proxies for open-source models.
- **Context sufficiency (independent autorater):** a binary label `suff(x,C)` predicting whether the context contains enough information to decide the label, computed by a **separate autorater model** (following Sufficient Context). To reduce circularity, we use a different model family for the autorater than the generator (e.g., Gemini-3.1-Pro as autorater when the generator is Llama/Mistral).

**Routing policy.** We implement the router as a small, auditable model (logistic regression or shallow decision tree) trained on a calibration split to predict whether to:

- trust retrieval (output aᵣ),
- ignore retrieval (output a₀), or
- abstain.

Operationally, we learn two scores:

- `p_retrieve_helpful(x)` vs `p_retrieve_harmful(x)` from the above features

and use a threshold to trade coverage for selective accuracy.

**Strong trivial baseline (“RC-RAG + fallback”).** We define a baseline that uses RC-RAG’s keep/discard judgment on aᵣ:

- If **keep** → output aᵣ
- If **discard** → output a₀ (zero-context fallback)
- Optional: if both a₀ and aᵣ have low confidence → abstain

This baseline is intentionally strong and should eliminate many obvious retrieval-harm cases.

### Key Innovations

1) **Objective alignment to the deployment failure mode:** evaluate routing by **improving the accuracy–coverage frontier relative to RC-RAG+fallback**, rather than only “discarding uncertain retrieval answers”.
2) **Multi-signal correction of RC-RAG failure modes:** add an independent sufficiency signal and disagreement/confidence features to separate “retrieval is unstable but useful” from “retrieval is stable but misleading”.
3) **Decisive baseline discipline:** treat RC-RAG+fallback as the primary comparison, not vanilla RAG.

---
## Related Work

### Field Overview

This proposal sits at the intersection of (i) RAG robustness under noisy or conflicting evidence, (ii) selective prediction / abstention for LLMs, and (iii) retrieval routing (when to retrieve vs answer directly). Recent work has shown that relevance-based retrieval alone is not enough: models can be distracted by irrelevant context or misled by conflicting context. In parallel, risk control methods propose abstention policies, but often focus on uncertainty estimation within a fixed RAG pipeline.

### Related Papers

- **[Worse than Zero-shot? A Fact-Checking Dataset for Evaluating the Robustness of RAG Against Misleading Retrievals (RAGuard)](https://huggingface.co/datasets/UCSC-IRKM/RAGuard)**: Benchmark showing retrieval can reduce accuracy vs no-retrieval and misleading-only contexts can collapse accuracy.
- **[Controlling Risk of Retrieval-augmented Generation: A Counterfactual Prompting Framework (RC-RAG)](https://github.com/ict-bigdatalab/RC-RAG)**: Counterfactual prompting to keep/discard retrieval-conditioned answers with risk/carefulness/coverage trade-offs.
- **[Sufficient Context: A New Lens on Retrieval Augmented Generation Systems](https://openreview.net/forum?id=Jjr2Odj8DJ)**: Defines and autorates context sufficiency; combines sufficiency with confidence for selective generation.
- **[SELF-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://openreview.net/forum?id=hSyW5go0v8)**: Trains models to decide when to retrieve and critique evidence use via reflection tokens.
- **[Self-Routing RAG: Binding Selective Retrieval with Knowledge Verbalization](https://arxiv.org/abs/2504.01018)**: Trains a policy to choose between retrieval and verbalized parametric knowledge, reducing retrieval frequency while improving accuracy.
- **[TRAQ: Trustworthy Retrieval Augmented Question Answering via Conformal Prediction](https://aclanthology.org/2024.naacl-long.227/)**: Uses conformal prediction to produce correctness-guarantee answer sets for RAG under assumptions.
- **[RePlug: Retrieval-Augmented Black-Box Language Models](https://arxiv.org/abs/2301.12652)**: Retrieval-augments black-box LMs without finetuning the generator.
- **[In-Context Retrieval-Augmented Language Models](https://aclanthology.org/2023.tacl-1.75/)**: Studies retrieval-conditioned generation and in-context RAG variants.
- **[Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html)**: Introduces the original RAG framework combining retriever and generator for knowledge-intensive tasks.
- **[REALM: Retrieval-Augmented Language Model Pre-Training](https://proceedings.mlr.press/v119/guu20a.html)**: Retrieval-augmented pretraining with learned retrieval over a large corpus.
- **[Dense Passage Retrieval for Open-Domain Question Answering](https://aclanthology.org/2020.emnlp-main.550/)**: Dense retriever commonly used as a baseline for open-domain QA.
- **[ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction](https://dl.acm.org/doi/10.1145/3397271.3401075)**: Late-interaction dense retrieval for efficient passage search.
- **[FiD: Leveraging Passage Retrieval with Generative Models for Open Domain QA](https://aclanthology.org/2021.acl-long.340/)**: Fusion-in-decoder architecture for aggregating multiple retrieved passages.
- **[ATLAS: Few-shot Learning with Retrieval Augmented Language Models](https://jmlr.org/papers/v24/23-0037.html)**: Retrieval-augmented few-shot learning with a strong open-source baseline.
- **[When Not to Trust Language Models: Investigating Effectiveness of Parametric and Non-Parametric Memories](https://aclanthology.org/2023.acl-long.548/)**: Analyzes when retrieval (non-parametric memory) helps vs hurts relative to parametric memory.
- **[Making Retrieval-Augmented Language Models Robust to Irrelevant Context](https://openreview.net/forum?id=4As7l7T5oV)**: Studies robustness under noisy/irrelevant retrieval and mitigation strategies.
- **[Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback](https://aclanthology.org/2023.emnlp-main.311/)**: Practical prompting methods to obtain better-calibrated confidence scores.
- **[CF-RAG: Counterfactual Reasoning for Retrieval-Augmented Generation](https://openreview.net/forum?id=9U51rOnGko)**: Training-free counterfactual query generation + evidence arbitration to avoid correlation-trap distractors in RAG.
- **[Knowledgeable-R1: Resisting Contextual Interference in RAG via Parametric-Knowledge Reinforcement](https://arxiv.org/abs/2506.05154)**: RL-based training to balance parametric vs contextual knowledge and resist misleading context.
- **[TARG: Trustworthy Adaptive Retrieval Generation](https://openreview.net/forum?id=L8gYtUZfVU)**: Training-free adaptive retrieval method using prediction confidence; a close baseline for deciding when retrieval is needed.
- **[RAGRouter-Bench: A Dataset and Benchmark for Adaptive RAG Routing](https://arxiv.org/abs/2602.00296)**: Broad adaptive-RAG routing benchmark useful for positioning generalization beyond RAGuard.
- **[Language Models (Mostly) Know What They Know](https://arxiv.org/abs/2207.05221)**: Shows self-knowledge signals can be elicited for selective prediction.
- **[Generating with Confidence: Uncertainty Quantification for Black-Box Large Language Models](https://arxiv.org/abs/2305.19187)**: Uncertainty quantification methods for black-box LLM outputs.
- **[Confidence Matters: Revisiting Intrinsic Self-Correction Capabilities of Large Language Models](https://arxiv.org/abs/2402.12563)**: Revisits self-correction and confidence-based strategies relevant to abstention.

### Taxonomy

| Family / cluster | Core idea | Representative papers | Benchmarks / evaluation | Known limitations |
|---|---|---|---|---|
| Misleading / conflicting retrieval benchmarks | Evaluate RAG under real-world contradictory evidence | RAGuard; fact-checking datasets (MultiFC, FEVER-style) | Accuracy under zero-context vs RAG vs oracle misleading | Domain specificity; potential dataset artifacts |
| Risk control / abstention for RAG | Decide keep/discard to reduce incorrect answered cases | RC-RAG; calibration baselines; confidence-based rejection | risk/carefulness/alignment/coverage; selective accuracy–coverage | Can reduce coverage; may miss routing to no-retrieval |
| Context sufficiency & selective generation | Predict whether context contains enough info; combine with confidence | Sufficient Context; FLAMe autoraters | Coverage–accuracy curves; suff/insuff stratification | Autorater cost; potential circularity |
| Selective retrieval / routing | Decide whether to retrieve or answer directly | Self-RAG; SR-RAG; Active RAG | QA accuracy vs retrieval rate | Often training-heavy; not targeted to misleading retrieval harm |
| Adaptive retrieval gating | Use confidence or routers to decide when retrieval is needed | TARG; RAGRouter-Bench | Routing accuracy; downstream QA accuracy | Not primarily designed for misleading-evidence harm or no-retrieval fallback risk control |
| Statistical guarantees | Conformal prediction / sets / abstention | TRAQ | Coverage guarantees under assumptions | Assumptions may not hold under shift |
| Counterfactual arbitration (training-free) | Counterfactual query generation + evidence arbitration for RAG robustness | **[CF-RAG](https://openreview.net/forum?id=9U51rOnGko)** | Multi-hop QA EM; robustness under distractor injection | Higher inference cost; not a routing policy vs no-retrieval |
| Training-based context-interference resistance | RL training to resist misleading context and balance parametric vs contextual knowledge | **[Knowledgeable-R1](https://arxiv.org/abs/2506.05154)** | Robustness under adversarial/conflicting contexts | Requires RL training; model-specific |

### Closest Prior Work

**RC-RAG (Chen et al., 2024).** Uses counterfactual prompts to assess uncertainty of a retrieval-conditioned answer and decide keep/discard. Limitation for this proposal: its control policy is defined within retrieval-conditioned generation; it does not explicitly optimize against a no-retrieval baseline, nor does it evaluate the “retrieval hurts vs no-retrieval” failure mode exposed by RAGuard.

**RAGuard (Zeng et al., 2025).** Introduces a benchmark demonstrating retrieval-induced accuracy drops and provides oracle misleading-only evaluation. Limitation: it is primarily a diagnostic benchmark; it does not propose an explicit routing/control policy or compare to strong risk-control baselines like RC-RAG.

**Sufficient Context (Joren et al., 2025).** Introduces an autorater for context sufficiency and a simple confidence+sufficiency selective generation method. Limitation: it targets insufficiency-driven hallucinations, not retrieval-induced correctness flips due to misleading evidence; and it does not treat RC-RAG-style stability as a baseline.

**CF-RAG (ICLR 2026).** Uses counterfactual query generation and evidence arbitration to improve RAG robustness on multi-hop QA. It is training-free but substantially higher inference cost (multiple counterfactual queries, clustering, arbitration). Our work is different: we do not change retrieval or generate counterfactual queries; we focus on a lightweight **routing/control policy** to decide when to trust retrieval vs fall back to no-retrieval vs abstain, and we evaluate directly on misleading-retrieval harm (RAGuard) with a strong RC-RAG+fallback baseline.

**Knowledgeable-R1 (ICLR 2026).** Uses reinforcement learning to resist contextual interference by explicitly training policies for parametric-only, context-aware, and robust-parametric behaviors. Our approach is complementary: it is inference-time and model-agnostic (no RL finetuning), intended as a deployable wrapper for existing generators; the comparison is whether simple routing can match some of the robustness benefits without training.

**Self-RAG / SR-RAG.** Train policies to retrieve selectively or route between parametric and external knowledge. Limitation: they are training-intensive and are not evaluated on misleading-retrieval-specific settings like RAGuard; they also do not directly address the risk-control metrics and baselines used in RC-RAG.

**TARG and RAGRouter-Bench.** These works strengthen the adaptive retrieval comparison set. TARG is especially important as a training-free confidence-based gate, while RAGRouter-Bench shows that routing is becoming a benchmarked problem in its own right. Our focus differs: we optimize for retrieval-induced harm control under misleading evidence, compare to RC-RAG+fallback, and include an explicit no-retrieval output channel rather than only deciding whether retrieval is needed.

**Novelty Kill Search Summary (2026-04-29).** Searched for combinations of (i) “RC-RAG zero-context fallback”, (ii) “RAGuard routing abstain”, (iii) “misleading retrieval do-no-harm router”, and checked for selective-retrieval work explicitly evaluated on RAGuard. No prior work combining RC-RAG-style counterfactual stability with an explicit no-retrieval fallback objective on misleading-retrieval benchmarks was found. Full query log is in `novelty_search.md`.

### Comparison Table

| Related work | What it does | Key limitation | What we change | Why ours should win |
|---|---|---|---|---|
| RC-RAG | Counterfactual prompts → keep/discard retrieval answer | No explicit optimization vs no-retrieval baseline; stability is within retrieval | Add no-retrieval channel + sufficiency + disagreement/confidence | Better routing when retrieval hurts; improves accuracy–coverage frontier |
| Sufficient Context | Autorate sufficiency; combine with confidence for abstention | Not targeted to misleading retrieval harm; no counterfactual stability baseline | Add stability and explicit routing between retrieval/no-retrieval/abstain | Separates “insufficient” vs “misleading” regimes; reduces harm |
| RAGuard | Benchmark for misleading retrieval robustness | Diagnostic; no strong routing baselines | Treat as primary benchmark; introduce RC-RAG+fallback baseline | Establishes best-known routing baseline and pushes frontier |
| TARG | Training-free confidence-based adaptive retrieval | Decides retrieval need, not misleading-context harm vs no-retrieval fallback | Add harm-specific features and RC-RAG+fallback comparison | Better aligned with retrieval-induced error flips |
| RAGRouter-Bench | Benchmarks adaptive routing across datasets | Broad routing benchmark, not a targeted do-no-harm policy | Use as positioning / optional generalization check | Clarifies scope and prevents overclaiming |
| Self-RAG / SR-RAG | Train retrieval routing policies | Training-heavy; not evaluated for misleading retrieval harm | Training-light router using audited signals | Cheaper to deploy; targeted to harm-avoidance objective |
| TRAQ | Conformal prediction sets for RAG | Assumption-sensitive; not focused on misleading evidence | Use selective prediction framing (accuracy–coverage) for routing | Practical decision rule without strong assumptions |

---

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

## Success Criteria

**Hypothesis (directional).** The multi-signal router will improve selective accuracy at the same coverage compared to RC-RAG+fallback on RAGuard, and will not materially worsen risk/carefulness on RC-NQ/RC-TQ.

**Decision Rule (concrete).**
- **Proceed**: On RAGuard, ours improves selective accuracy by a margin outside the std range at ≥2 coverage points (e.g., 70% and 90% coverage) over RC-RAG+fallback for both Llama and Mistral; and on RC-NQ/RC-TQ, risk is **≤ (RC-RAG baseline + 1% absolute)** at matched coverage and carefulness is **≥ (baseline − 1% absolute)**.
- **Pivot**: If ours helps on RAGuard but fails non-inferiority on RC-NQ/RC-TQ, restrict scope to misleading-retrieval regimes and treat as a specialized router; remove abstention and focus on retrieval vs no-retrieval routing.
- **Refute**: If RC-RAG+fallback matches or exceeds ours across coverage levels on RAGuard, abandon the multi-signal router and instead focus on characterizing the failure modes/conditions where fallback is sufficient.

---
## Impact Statement

If successful, this work provides a simple, auditable routing layer that practitioners can place in front of any RAG pipeline to decide when to trust retrieval, when to ignore it, and when to abstain. It would directly inform deployment policies for LLM assistants in noisy-information settings by reducing cases where retrieval makes answers less reliable than a no-retrieval baseline.

---
## References

- [Worse than Zero-shot? A Fact-Checking Dataset for Evaluating the Robustness of RAG Against Misleading Retrievals](https://huggingface.co/datasets/UCSC-IRKM/RAGuard) - Zeng et al., 2025
- [Controlling Risk of Retrieval-augmented Generation: A Counterfactual Prompting Framework](https://github.com/ict-bigdatalab/RC-RAG) - Chen et al., 2024
- [Sufficient Context: A New Lens on Retrieval Augmented Generation Systems](https://openreview.net/forum?id=Jjr2Odj8DJ) - Joren et al., 2025
- [CF-RAG: Counterfactual Reasoning for Retrieval-Augmented Generation](https://openreview.net/forum?id=9U51rOnGko) - 2026
- [Knowledgeable-R1: Resisting Contextual Interference in RAG via Parametric-Knowledge Reinforcement](https://arxiv.org/abs/2506.05154) - 2026
- [TARG: Trustworthy Adaptive Retrieval Generation](https://openreview.net/forum?id=L8gYtUZfVU) - 2026
- [RAGRouter-Bench: A Dataset and Benchmark for Adaptive RAG Routing](https://arxiv.org/abs/2602.00296) - 2026
- [SELF-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://openreview.net/forum?id=hSyW5go0v8) - Asai et al., 2024
- [Self-Routing RAG: Binding Selective Retrieval with Knowledge Verbalization](https://arxiv.org/abs/2504.01018) - 2025
- [TRAQ: Trustworthy Retrieval Augmented Question Answering via Conformal Prediction](https://aclanthology.org/2024.naacl-long.227/) - Li et al., 2024
- [RePlug: Retrieval-Augmented Black-Box Language Models](https://arxiv.org/abs/2301.12652) - Shi et al., 2023
- [In-Context Retrieval-Augmented Language Models](https://aclanthology.org/2023.tacl-1.75/) - Ram et al., 2023
- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html) - Lewis et al., 2020
- [REALM: Retrieval-Augmented Language Model Pre-Training](https://proceedings.mlr.press/v119/guu20a.html) - Guu et al., 2020
- [Dense Passage Retrieval for Open-Domain Question Answering](https://aclanthology.org/2020.emnlp-main.550/) - Karpukhin et al., 2020
- [ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction](https://dl.acm.org/doi/10.1145/3397271.3401075) - Khattab & Zaharia, 2020
- [FiD: Leveraging Passage Retrieval with Generative Models for Open Domain QA](https://aclanthology.org/2021.acl-long.340/) - Izacard & Grave, 2021
- [ATLAS: Few-shot Learning with Retrieval Augmented Language Models](https://jmlr.org/papers/v24/23-0037.html) - Izacard et al., 2023
- [When Not to Trust Language Models: Investigating Effectiveness of Parametric and Non-Parametric Memories](https://aclanthology.org/2023.acl-long.548/) - Mallen et al., 2023
- [Making Retrieval-Augmented Language Models Robust to Irrelevant Context](https://openreview.net/forum?id=4As7l7T5oV) - Yoran et al., 2024
- [Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback](https://aclanthology.org/2023.emnlp-main.311/) - Tian et al., 2023
- [Language Models (Mostly) Know What They Know](https://arxiv.org/abs/2207.05221) - Kadavath et al., 2022
- [Generating with Confidence: Uncertainty Quantification for Black-Box Large Language Models](https://arxiv.org/abs/2305.19187) - Lin et al., 2023
- [Confidence Matters: Revisiting Intrinsic Self-Correction Capabilities of Large Language Models](https://arxiv.org/abs/2402.12563) - Li et al., 2024

