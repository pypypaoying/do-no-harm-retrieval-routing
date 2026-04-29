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