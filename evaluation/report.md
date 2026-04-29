# Proposal Evaluation Report

**Proposal**: Do-No-Harm Retrieval Routing: Multi-Signal Risk Control for Misleading Retrievals  
**Evaluation Date**: 2026-04-29  
**Re-evaluation mode: Revision** — Core idea unchanged from prior evaluation (multi-signal router combining counterfactual stability, context sufficiency, and disagreement signals for retrieval routing). Reusing prior deep research findings; focusing on revision quality.

---

## Prior Evaluation Feedback — Resolution Status

The prior evaluation (report_prev.md) recommended **Revise** with four priorities:

| # | Prior Priority | Status | Evidence |
|---|---|---|---|
| 1 | Address model-mismatch with RC-RAG's evaluation setting (Soundness) | **✅ Addressed** | `claude-opus-4-6` added as a third model for "Black-box model for sensitivity + RC-RAG-style comparison (re-run baselines)" (line 181). |
| 2 | Discuss CF-RAG and Knowledgeable-r1 in Related Work (Novelty/Soundness) | **✅ Addressed** | Both are now cited in Related Papers (lines 123–124), added to Taxonomy (lines 136–137), and given detailed differentiation in Closest Prior Work (lines 147–149). |
| 3 | Specify calibration split size and overfitting controls (Soundness) | **✅ Addressed** | Stratified 5-fold cross-validation specified (line 192), with threshold tuning for RC-NQ/RC-TQ (line 193). |
| 4 | Remove or integrate "Scope and Constraints" section (Format) | **❌ Not addressed** | "Scope and Constraints" still present (lines 3–8). Minor format issue; does not affect experimental substance. |

**Summary**: 3 of 4 revision priorities have been addressed. The remaining issue is a minor format violation.

---

## Strategic Context

**Topic alignment**: The proposal targets CIKM 2026 / EMNLP 2026 in NLP/LLM direction — well-aligned with the user's request. RAG robustness and routing is a mainstream topic at both venues.

**Constraint compliance**:
- **Fully automated**: Yes. Evaluation uses existing benchmark labels (RAGuard, RC-NQ/RC-TQ) with constrained output formats ({true, false, unknown}). No human annotation required. ✅
- **Budget**: 32×H200 141GB. Estimated ~26k generator calls + 5k autorater calls for open-source models + optional ~10.6k API calls for Claude. Comfortably within budget. ✅
- **No search-engine APIs**: Explicitly avoids this. ✅

**Importance gate**:
- **Who benefits**: RAG deployment teams, enterprise search/assistant builders, fact-checking pipeline operators.
- **Bottleneck**: Yes — retrieval harm is documented across multiple 2025–2026 benchmarks (RAGuard, URAG). Current solutions either require training (Self-RAG, Knowledgeable-r1) or don't explicitly compare against a no-retrieval fallback (RC-RAG).
- **Already solved by frontier models?** No. RAGuard (NeurIPS 2025) shows even Claude 3.5 and GPT-4o suffer accuracy drops under misleading retrieval. The problem persists in 2026.

---

## Pre-Scoring Reality Check

### 1. Clarity Test
**Core idea in one sentence**: "A lightweight inference-time router that combines counterfactual stability, context sufficiency, and retrieval-vs-no-retrieval disagreement signals to decide per-query whether to trust RAG, fall back to parametric-only answering, or abstain, evaluated against a strong RC-RAG+fallback baseline on accuracy–coverage curves."

Clear and communicable to an ML researcher outside the specific RAG robustness subfield. ✅

### 2. Mechanism Test
**Why it should work**: The mechanism is that three signals cover complementary failure modes: (1) counterfactual stability catches fragile RAG answers that change under prompt perturbation, (2) context sufficiency catches cases where retrieved documents lack decisive information, and (3) disagreement between parametric and retrieval answers catches cases where retrieval actively flips a correct answer. A simple classifier (logistic regression) can learn which combinations indicate "retrieval is likely harmful."

The mechanism is plausible and well-articulated. The key risk is that the trivial baseline (RC-RAG+fallback) already captures most of the routing gain, and the additional signals add noise. The proposal explicitly acknowledges this uncertainty. ✅

### 3. Surprise Test
The most surprising element remains the **strong trivial baseline design** (RC-RAG + zero-context fallback) — a self-aware framing that raises the bar for the proposed method. Most proposals cherry-pick weak baselines; this one designs the strongest simple competitor first. The proposal is also honest about the possibility that its own method may not beat this baseline.

Moderate surprise. The signal combination itself is somewhat predictable, but the baseline discipline and honesty about uncertainty are notable.

### 4. Smell Test
- **"Scope and Constraints" section persists** despite being flagged in the prior evaluation — suggests selective attention to feedback. Minor but slightly concerning for pipeline discipline.
- **"Optionally on a subset for cost control"** (line 201, re: Claude): This hedge partially undermines the model-mismatch fix from revision priority #1. If Claude evaluation is optional, the API-model comparison may not materialize. However, the core comparison (Llama 3 + Mistral on RAGuard) has published baselines, so this is a robustness addition rather than a critical path.
- **RAGuard domain specificity**: Political fact-checking from Reddit/PolitiFact is narrow. RC-NQ/RC-TQ are broader QA tasks but still in the factoid-QA family. No truly out-of-domain test.
- **Router training on 2,648 claims**: Even with 5-fold CV, each fold trains on ~2,118 instances. For a logistic regression with ~6 features, this should be sufficient, but the feature-label relationship may be noisy.

### 5. Accessibility Check
See "Readability suggestions" under Warnings / Limitations.

---

## Scores (1–5)

**Proposal Type**: `method`

**Core Metrics**:
- Insight Depth (Novelty): 3/5 (confidence: medium)
- Importance: 4/5 (confidence: high)
- Significance: 3/5 (confidence: medium)
- Sharpness: 4/5 (confidence: high)
- Decisiveness (Scope discipline): 4/5 (confidence: high)
- Soundness: 4/5 (confidence: medium)
- Feasibility: 4/5 (confidence: high)

**Advisory descriptors** (not in quality score; may gate finalization):
- Elegance (Complexity-to-Payoff): 4/5
- Ethical Risks (Risk Level + Mitigation): 2/5 (low-moderate risk)

**Revision Priorities** (remaining issues):
1. **Integrate or remove the "Scope and Constraints" section** — non-standard format; should be folded into Introduction or a metadata block (Format compliance).
2. **Commit explicitly to running claude-opus-4-6 evaluation** — remove the "optionally on a subset" hedge and commit to running at least a full RAGuard evaluation with this model, even if RC-RAG re-runs are on a subset (Soundness).

---

## Overall Summary

**Recommendation: Finalize**

The proposal has substantively addressed the three major weaknesses identified in the prior evaluation: (1) model mismatch resolved by adding claude-opus-4-6, (2) CF-RAG and Knowledgeable-r1 now cited and differentiated, and (3) calibration controls specified via 5-fold CV. The remaining issue (format: "Scope and Constraints" section) is minor and does not affect the Verification module's ability to derive an experiment.

**Strengths**:
- **Real 2026 pain point** backed by multiple benchmarks (RAGuard, URAG) showing retrieval harm persists across model scales.
- **Excellent baseline discipline**: RC-RAG + zero-context fallback is a genuinely strong trivial baseline that most proposals would not define. This makes any positive result more credible.
- **Clear, concrete decision rule** with proceed/pivot/refute conditions and specific numeric thresholds.
- **Verification-ready**: benchmarks specified with download links, models specified with HuggingFace paths, metrics defined, calibration protocol (5-fold CV) specified, autorater model committed (gemini-3.1-pro).
- **Well-scoped**: comfortably within 32×H200 budget.
- **Good related work coverage**: 21 papers, including two 2026 works (CF-RAG, Knowledgeable-r1) with substantive differentiation.

**Biggest remaining weaknesses**:
1. **Moderate novelty** (3/5): The core method is combining known signals via logistic regression. This is feature engineering rather than a new mechanism. The proposal's value is more in the experimental framing and baseline discipline than in the method itself.
2. **Domain specificity**: RAGuard (political fact-checking) and RC-NQ/RC-TQ (factoid QA) are both in the QA/fact-checking family. Generalization to other retrieval-harm domains (medical, legal, multi-hop reasoning) is unproven.
3. **Claude evaluation hedged**: The "optionally on a subset" framing for claude-opus-4-6 partially undermines the model-mismatch fix.

**Low-confidence flags**: Significance confidence is medium (depends on whether the trivial baseline is already near-optimal). Soundness confidence is medium (depends on Claude commitment and the quality of the re-run RC-RAG baselines).

**Verification-Ready Checklist**:
- ✅ One-sentence thesis: "Multi-signal router improves accuracy–coverage frontier over RC-RAG+fallback."
- ✅ Execution readiness: Benchmarks, models, metrics, baselines, autorater all specified.
- ✅ Decision rule: Concrete proceed/pivot/refute with numeric thresholds.
- ✅ Budget: Comfortably within 32×H200.
- ✅ Recency: 2026 works (CF-RAG, Knowledgeable-r1) cited and differentiated.
- ✅ Anti-mode-collapse: Different topic/technique from the other portfolio proposal (Correlation-Trap Citation Stress Test).

---

## Insight Depth (Novelty)

**What the proposal claims**: Novelty in (1) combining counterfactual stability (RC-RAG), context sufficiency (Sufficient Context), and disagreement/confidence signals into a multi-signal router, (2) targeting the "retrieval-harms" failure mode with an explicit no-retrieval channel, and (3) using RC-RAG+fallback as the strong baseline.

**Judgment (3/5 — clearly differentiated with mechanism hypothesis, but moderate novelty; confidence: medium)**:

The proposal is differentiated from each of its closest works:
- RC-RAG: no no-retrieval fallback or sufficiency signal.
- Sufficient Context: no counterfactual stability; targets insufficiency, not misleading retrieval.
- CF-RAG: uses counterfactual queries (not prompts), higher inference cost, no routing policy vs no-retrieval.
- Knowledgeable-r1: requires RL training; model-specific.
- Self-RAG / SR-RAG: training-intensive; not evaluated on misleading-retrieval harm.

The "A+B" heuristic fires weakly: the proposal combines three known signals (A=stability, B=sufficiency, C=disagreement) into a classifier. However, the proposal articulates a specific mechanism for why each signal covers a different failure mode — this goes beyond "hasn't been tried" and provides a testable structural hypothesis. The strong trivial baseline framing also adds framing-level novelty (forcing the evaluation to test the marginal value of multi-signal routing above simple fallback).

**Deep Research Log**: Prior evaluation conducted novelty/importance research (see report_prev.md Deep Research Log); core claim unchanged, reusing those findings. Key result: no prior work combining RC-RAG-style counterfactual stability with explicit no-retrieval fallback and sufficiency signals on misleading-retrieval benchmarks.

**What would raise to 4**: A genuinely surprising prediction — e.g., "we expect the sufficiency signal to be *negatively* correlated with stability under misleading retrieval because [mechanism]" — rather than the additive-combination hypothesis. Or a new signal that hasn't been previously studied.

---

## Importance

**What the proposal claims**: Retrieval can harm LLM accuracy, as demonstrated by RAGuard (accuracy drops from 62.5% to 59.4% with retrieval for Llama 3) and oracle-misleading collapses accuracy to 36.8%.

**Judgment (4/5 — real and current pain point; confidence: high)**:

Prior evaluation research (reused here) confirms this is a genuine 2026 bottleneck:
- RAGuard (NeurIPS 2025): Even frontier models (GPT-4o, Claude 3.5) suffer significant accuracy drops under misleading retrieval.
- URAG (2026): Confirms retrieval doesn't uniformly improve reliability and can amplify overconfident errors.
- Multiple industry reports identify retrieval quality as the primary failure mode in production RAG.
- Knowledgeable-r1's 2026 results show LLMs have a "context dominance" problem.

**Who would switch**: RAG deployment teams at enterprises running open-source models (Llama, Mistral) — these are the most affected since they lack the robustness of frontier models. A lightweight, model-agnostic routing layer is directly deployable.

**Strongest counterargument considered**: Frontier models may handle misleading retrieval increasingly well, and training-based approaches (Knowledgeable-r1) may eventually make inference-time routing unnecessary.

**Why rejected**: Most deployments use smaller open-source models where the problem is severe. Training-based approaches require per-model fine-tuning, while an inference-time router is model-agnostic and immediately deployable. The problem remains acute in 2026 for practical deployments.

**What would drop to 3**: Strong evidence that RC-RAG+fallback trivial baseline already eliminates >90% of retrieval harm on RAGuard, making the router unnecessary.

---

## Significance

**What the proposal claims**: The result (positive or negative) would inform deployment policies for LLM assistants in noisy-information settings.

**Judgment (3/5 — result matters in a narrow but real regime; confidence: medium)**:

A positive result provides a practical routing recipe for RAG deployments. A negative result (trivial baseline is sufficient) is also decision-changing: "practitioners should just use RC-RAG+fallback; don't bother with multi-signal routing."

Limiting factors:
- Primary benchmark (RAGuard) is political fact-checking — a specific domain. Transfer to medical, legal, or general QA settings is unproven.
- If RC-RAG+fallback proves near-optimal, significance reduces to "use the simple fallback" — still useful but lower impact.
- Both benchmark families (RAGuard, RC-NQ/RC-TQ) are factoid QA/fact-checking. No long-form or multi-hop task.

The dual-benchmark design and addition of Claude as a third model help broaden applicability but don't fully resolve the domain-specificity concern.

---

## Sharpness

**What the proposal claims**: The outcome separates three concrete next actions: proceed (multi-signal router is better), pivot (specialize to misleading regimes only), or refute (trivial baseline is sufficient).

**Judgment (4/5 — sharp information gain; confidence: high)**:

The decision rule is well-specified with numeric thresholds:
- **Proceed**: Improvement at ≥2 coverage points, outside std range, for both Llama and Mistral, plus non-inferiority on RC-NQ/RC-TQ (≤1% risk increase, ≥1% carefulness preserved).
- **Pivot**: Helps on RAGuard but fails non-inferiority → specialized misleading-retrieval router.
- **Refute**: Trivial baseline matches or exceeds across coverage levels → abandon multi-signal approach.

The accuracy–coverage curve framing provides richer discrimination than a single scalar. Matched-coverage evaluation prevents "answer less" confounds. Each outcome leads to a different concrete action.

**Strongest counterargument**: The "outside std range" criterion may be lenient with 5-fold CV variance on a small dataset. Results could be driven by RAGuard-specific artifacts (political content style) rather than general routing ability.

**Why rejected**: The proposal includes artifact checks (correlation with document length/style) and a second benchmark family (RC-NQ/RC-TQ) that partially addresses this. Sharpness evaluates the information-theoretic quality of the experimental design, not generalizability (which is a Soundness concern).

**What would drop to 3**: Vague thresholds (e.g., "significant improvement") rather than the concrete ±1% absolute bounds.

---

## Decisiveness (Scope discipline)

**What the proposal claims**: A single core experiment (multi-signal router vs. RC-RAG+fallback across 2 benchmarks × 2–3 models) with ablations and sanity checks.

**Judgment (4/5 — decisive and immediately implementable; confidence: high)**:

- **One-sentence thesis**: ✅ (multi-signal router improves accuracy–coverage frontier over RC-RAG+fallback)
- **First experiment**: ✅ (generate 4 answers per query, compute features, train logistic regression via 5-fold CV, evaluate accuracy–coverage curves)
- **Stop rule**: ✅ (concrete proceed/pivot/refute conditions with numeric thresholds)
- **Benchmarks**: ✅ (RAGuard + RC-NQ/RC-TQ with download links)
- **Models**: ✅ (Llama 3 8B + Mistral 7B + claude-opus-4-6)
- **Autorater**: ✅ (gemini-3.1-pro, specified)
- **Calibration protocol**: ✅ (stratified 5-fold CV)
- **Resource estimate**: ✅ (~26k generator calls + 5k autorater calls)

The Verification module can derive a concrete experiment plan from this proposal with minimal ambiguity. The revision improved this metric by specifying the calibration protocol and autorater model.

**Strongest counterargument**: The Claude evaluation is hedged ("optionally on a subset for cost control"), introducing ambiguity about whether it will actually be executed.

**Why this doesn't drop the score**: The core comparison (Llama 3 + Mistral on RAGuard and RC-NQ/RC-TQ) is fully specified and not hedged. Claude is supplementary. The verifier can execute the core experiment without this optional component.

**What would drop to 3**: If benchmarks, models, or metrics were unspecified.

---

## Soundness

**What the proposal claims**: Rigorous experimental design with ≥3 seeds, matched-coverage evaluation, artifact checks, sanity checks (random/oracle routers), 5-fold CV, and primary baseline alignment with both RC-RAG and RAGuard settings.

**Judgment (4/5 — strong and convincing with manageable remaining gaps; confidence: medium)**:

**Improvements from revision** (addressing prior evaluation gaps):
1. **Model mismatch partially resolved**: claude-opus-4-6 added for API-model evaluation. RC-RAG's published Mistral results can be directly compared; Llama 3 RC-RAG baselines will be re-run.
2. **Close competitors cited and differentiated**: CF-RAG and Knowledgeable-r1 are now in Related Papers, Taxonomy, and Closest Prior Work with substantive differentiation.
3. **Calibration protocol specified**: 5-fold CV for router training. For 2,648 RAGuard claims, each fold trains on ~2,118 instances — sufficient for logistic regression with ~6 features.
4. **Autorater specified**: gemini-3.1-pro committed as the sufficiency autorater.

**Remaining concerns (none blocking)**:
- **Claude evaluation hedged**: "Optionally on a subset for cost control" — the commitment should be explicit. However, the core open-source model evaluation is fully specified.
- **Baseline re-run risk**: RC-RAG+fallback numbers are TBD. If the re-run baselines behave unexpectedly (e.g., RC-RAG doesn't transfer well to Llama 3), interpretation becomes complex. This is acknowledged.
- **Single QA/fact-checking domain family**: Both benchmarks (RAGuard, RC-NQ/RC-TQ) are factoid QA or fact-checking tasks. This limits the generalizability claim.
- **Sufficiency autorater quality**: gemini-3.1-pro's sufficiency predictions on RAGuard's political content haven't been validated. The proposal's artifact checks (correlation with document features) partially mitigate this.

**Red-team heuristic check**:
- "Just Prompt It" test: The trivial baseline (RC-RAG+fallback) IS essentially a prompt-based approach. The method adds learned feature combination on top. If the trivial baseline is near-optimal, the method fails. But this is the honest experimental design — the proposal tests whether the addition has value. Does not trigger default Significance cap because the comparison is built in.
- "A+B value" test: Combination of three known signals, but with articulated mechanism hypothesis for why they cover different failure modes. Does not trigger default Insight Depth cap.

**Actionable fixes**:
1. Commit explicitly to full RAGuard evaluation with claude-opus-4-6 (remove "optionally on a subset" hedge for at least one benchmark).
2. Discuss what to conclude if RC-RAG+fallback behaves unexpectedly on Llama 3 (e.g., if counterfactual prompts don't work well with Llama 3's instruction-following style).

---

## Feasibility

**What the proposal claims**: ~26k generator calls + 5k autorater calls for open-source models, plus ~10.6k optional API calls for Claude.

**Judgment (4/5 — operationally concrete and within budget; confidence: high)**:

- **Benchmarks**: RAGuard is public on HuggingFace. RC-RAG data/code is public on GitHub. ✅
- **Models**: Llama 3 8B and Mistral 7B are downloadable from HuggingFace. claude-opus-4-6 is API-accessible. ✅
- **Autorater**: gemini-3.1-pro is API-accessible. ✅
- **Compute**: 5 forward passes per claim × 2 models × 2,648 claims ≈ 26k model calls with short classification outputs. With 7–8B models, this is trivially feasible on 32×H200. Even with 5-fold CV, the dominant cost remains answer generation (one-time), not router training. ✅
- **API costs**: Autorater (gemini-3.1-pro) + optional Claude calls. Manageable; Claude can be scoped to one benchmark if cost is a concern. ✅
- **Baseline rerun**: RC-RAG baselines need re-running on Llama 3 (not in original paper). This adds compute but is within budget.

**Hard blockers**: None identified.

**Strongest counterargument**: If the Verification module decides to run full evaluation with Claude across both benchmarks + both retrieval depths (k=1, k=5) + 5 seeds, API costs increase substantially. But the proposal provides a reasonable scoping plan.

**What would drop to 3**: If a key benchmark were private or the autorater model were unavailable.

---

## Elegance (Complexity-to-Payoff)

The design is deliberately lightweight: a logistic regression or shallow decision tree over a small feature vector (~6 features). The method is auditable, interpretable, and adds minimal inference overhead beyond the four candidate answers that are already being generated for comparison. The complexity-to-payoff ratio is favorable. **4/5**.

---

## Ethical Risks (Risk Level + Mitigation)

The proposal uses political fact-checking data (RAGuard) sourced from Reddit and PolitiFact. This involves politically sensitive content, but the task is automated evaluation of routing decisions, not content generation, deployment, or user-facing claims. No human subjects, no adversarial content generation, no model training on sensitive material. Risk is manageable with standard research ethics. **2/5** (low-moderate risk).

---

## Warnings / Limitations

### Format / template compliance
- The proposal has a "Scope and Constraints" section (lines 3–8) that is not part of the standard proposal template. This was flagged in the prior evaluation and **not addressed**. Should be integrated into the Introduction or removed before finalization. This is a minor issue that does not block verification.

### Recency risk
**Resolved from prior evaluation.** The proposal now cites and differentiates from CF-RAG (ICLR 2026) and Knowledgeable-r1 (ICLR 2026), the two most relevant recent works.

### Readability suggestions
- **"RC-RAG"**: The full expansion ("Risk Control for Retrieval-Augmented Generation") should appear at first mention in the Introduction. Currently, the first mention says "RC-RAG (Controlling Risk of Retrieval-augmented Generation)" — this is acceptable but the acronym "RC-RAG" is used before the expansion.
- **"Accuracy–coverage frontier"**: The proposal provides a one-sentence gloss in line 35 — good. ✅
- **"FLAMe-style"**: No longer referenced in the current proposal (removed or replaced with specific gemini-3.1-pro commitment). ✅ Resolved.
- **"Counterfactual prompts"**: Explained on first use. ✅
- **"suff(x,C)"**: The notation is introduced with its definition. ✅
- Minor: The Taxonomy table (line 130) appears to be missing its header row — there's a `|---|---|---|---|---|` line with no header.

### Portfolio note (mode collapse check)
The other proposal in the portfolio ("Correlation-Trap Citation Stress Test") also involves RAG robustness but focuses on citation faithfulness, not retrieval routing. The techniques are different (NLI stress testing vs. multi-signal routing) and the targets are different (citation evaluation gap vs. routing decision quality). **No mode collapse detected** — topics and techniques are complementary.

---

## Blind Spots

1. **Shared context bias**: Both the proposal author and I have access to the same RAGuard/RC-RAG/Sufficient Context papers in the local KB. I may be overweighting these papers' importance and underweighting alternative framings (e.g., conformal prediction-based approaches, ensemble-based routing, or active retrieval strategies) that don't appear in this citation cluster.

2. **Queries I wish I could run**: 
   - "lightweight retrieval routing logistic regression feature combination RAG" — to check if the specific feature-engineering approach has been tried in unpublished work or industry blog posts.
   - "RAGuard follow-up routing 2026" — to check if any RAGuard follow-up work proposes routing specifically.
   - "multi-signal abstention RAG selective prediction 2026" — to check for very recent parallel work.

3. **Assumptions that could be wrong**:
   - I'm assuming the RC-RAG codebase is functional and reproducible. If it requires significant engineering to re-run on Llama 3, feasibility drops.
   - I'm assuming gemini-3.1-pro produces reliable sufficiency labels for political fact-checking content. If the autorater is noisy on this domain, the sufficiency signal may be worthless.
   - I'm assuming 2,648 RAGuard claims provide sufficient statistical power for 5-fold CV router evaluation. The effective test size per fold is ~530 claims; confidence intervals may be wide.
   - I'm assuming the proposal's three feature types are actually complementary (covering different failure modes). They could be highly correlated in practice, making the combination no better than the best single signal.

4. **Areas of lowest confidence**:
   - Whether the trivial baseline (RC-RAG+fallback) is already near-optimal — this determines whether any positive result is achievable. This is the central experimental uncertainty.
   - Whether the feature-based router generalizes beyond the QA/fact-checking task family.
   - Whether the "optionally on a subset" Claude evaluation will actually be executed, or whether it will be quietly dropped.