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
