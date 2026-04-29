# Proposal Evaluation Report

**Proposal**: Do-No-Harm Retrieval Routing: Multi-Signal Risk Control for Misleading Retrievals  
**Evaluation Date**: 2026-04-29  
**Re-evaluation mode**: First evaluation (no prior report exists).

---

## Strategic Context

**Topic alignment**: The proposal targets CIKM 2026 / EMNLP 2026 in NLP/LLM direction — well-aligned with the user's request for NLP/LLM research targeting these venues. RAG robustness and routing is a mainstream topic at both venues.

**Constraint compliance**:
- **Fully automated**: Yes. Evaluation uses existing benchmark labels (RAGuard, RC-NQ/RC-TQ) with constrained output formats ({true, false, unknown}). No human annotation required. ✅
- **Budget**: 32×H200 141GB. The proposal estimates ~13k model calls per base model with short outputs. Comfortably within budget. ✅
- **No search-engine APIs**: Proposal explicitly avoids this. ✅

**Importance gate (brief)**:
- **Who benefits**: RAG deployment teams, enterprise search/assistant builders, fact-checking pipeline operators.
- **Bottleneck**: Yes — retrieval harm (retrieval making answers worse) is documented across multiple 2025–2026 benchmarks (RAGuard, RGB, URAG). Current solutions either (a) are training-heavy (Self-RAG, Knowledgeable-r1) or (b) don't explicitly compare against a no-retrieval fallback (RC-RAG).
- **Already solved by frontier models?** No. RAGuard (NeurIPS 2025) shows even Claude 3.5 and GPT-4o suffer significant accuracy drops under misleading retrieval. The problem persists in 2026.

---

## Pre-Scoring Reality Check

### 1. Clarity Test
**Core idea in one sentence**: "A lightweight router that combines counterfactual stability, context sufficiency, and retrieval-vs-no-retrieval disagreement signals to decide — per query — whether to trust RAG, fall back to parametric-only answering, or abstain, measured against a strong trivial baseline (RC-RAG + zero-context fallback)."

This is clear and communicable. ✅

### 2. Mechanism Test
**Why it should work**: The mechanism rests on three complementary failure-mode detectors: (1) RC-RAG stability catches cases where the RAG answer is fragile under prompt perturbation, (2) sufficiency catches cases where the retrieved context lacks the information needed, and (3) disagreement between a₀ and aᵣ catches cases where retrieval is actively flipping a correct parametric answer. Each signal covers a different blind spot of the others. A logistic regression over these features can learn which failure mode is present and route accordingly.

I understand the mechanism. It is plausible but not guaranteed — the key risk is that RC-RAG+fallback already captures most of the gain, and the additional signals add noise more than signal. The proposal acknowledges this uncertainty. ✅

### 3. Surprise Test
The most surprising element is the **strong trivial baseline design** (RC-RAG + zero-context fallback). This is not something RC-RAG's original paper tested, and the proposal is honest that this baseline may already be hard to beat. This "baseline discipline" framing is refreshingly self-aware and adds genuine information value — even a negative result (trivial baseline is sufficient) would be decision-changing.

Moderate surprise. The combination of signals is somewhat predictable (feature engineering over known signals), but the framing and baseline discipline elevate it.

### 4. Smell Test
- The proposal uses **7–8B open-source models** (Llama 3 8B, Mistral 7B) as generators. These are the same models used in RAGuard. However, RC-RAG was evaluated with ChatGPT and Mistral — the proposal notes RC-RAG+fallback numbers are TBD and need re-running. This model mismatch between RC-RAG's published setting (ChatGPT) and the proposal's target (Llama 3 / Mistral) could complicate interpretation.
- The sufficiency autorater uses "Gemini-family or FLAMe-style" model — this is somewhat vague. The specific model choice matters for cost and quality.
- RAGuard is a **political fact-checking** dataset, which is a specific domain. Generalization to other retrieval-harm settings is uncertain.
- The router is trained on a calibration split — with RAGuard having 2,648 claims, the calibration split size may be small for learning a reliable router. Risk of overfitting.

### 5. Accessibility Check
See "Readability suggestions" under Warnings / Limitations below.

---

## Scores (1–5)

**Proposal Type**: `method`

**Core Metrics**:
- Insight Depth (Novelty): 3/5 (confidence: medium)
- Importance: 4/5 (confidence: high)
- Significance: 3/5 (confidence: medium)
- Sharpness: 4/5 (confidence: high)
- Decisiveness (Scope discipline): 4/5 (confidence: high)
- Soundness: 3/5 (confidence: medium)
- Feasibility: 4/5 (confidence: high)

**Advisory descriptors** (not in quality score; may gate finalization):
- Elegance (Complexity-to-Payoff): 4/5
- Ethical Risks (Risk Level + Mitigation): 2/5 (higher = higher risk; political fact-checking data has some sensitivity but manageable)

**Revision Priorities**:
1. **Address model-mismatch with RC-RAG's primary evaluation setting (Soundness)**: RC-RAG's published results use ChatGPT on RC-NQ/RC-TQ. The proposal plans to evaluate on Llama 3 / Mistral only. Either (a) include at least one API model (e.g., GPT-4o-mini or Claude) to match RC-RAG's evaluation setting, or (b) explicitly justify why open-source-only evaluation is sufficient and commit to re-running all RC-RAG baselines on Llama/Mistral under identical conditions.
2. **Discuss 2025–2026 close competitors in Related Work (Novelty/Soundness)**: CF-RAG (ICLR 2026) and Knowledgeable-r1 (ICLR 2026) are highly relevant recent works that address similar failure modes (counterfactual reasoning for RAG, parametric vs. contextual knowledge routing). The proposal must cite and differentiate from these.
3. **Specify calibration split size and overfitting controls (Soundness)**: With 2,648 RAGuard claims, the train/calibration/test split needs explicit specification. A logistic regression router trained on a small calibration set risks overfitting; discuss cross-validation or leave-one-out strategies.
4. **Remove "Scope and Constraints" section or integrate into standard structure (Format)**: The proposal has a non-standard "Scope and Constraints" header before Introduction. This should be integrated into the standard template.

---

## Overall Summary

**Recommendation: Revise**

**Strengths**:
- The proposal identifies a real, documented 2026 pain point (retrieval harm) with strong empirical evidence from RAGuard and RC-RAG benchmarks.
- Excellent baseline discipline: defining RC-RAG + zero-context fallback as the strong trivial baseline is the right move and raises the bar for the proposed method.
- Clear, concrete decision rule with proceed/pivot/refute conditions.
- Well-scoped for available compute; feasible on 32×H200.
- The three-way routing (retrieve / no-retrieve / abstain) is a natural and practical design.

**Biggest weaknesses**:
1. **Missing discussion of close 2025–2026 competitors**: CF-RAG (ICLR 2026) uses counterfactual reasoning for RAG robustness and achieves dramatic improvements. Knowledgeable-r1 (ICLR 2026) trains models to balance parametric vs contextual knowledge. These are close enough that reviewers will ask "how does this compare?" The proposal must differentiate.
2. **Model mismatch with RC-RAG's evaluation**: RC-RAG publishes results with ChatGPT; the proposal only uses 7–8B open-source models. This makes the RC-RAG comparison potentially unfair or meaningless unless baselines are re-run.
3. **Novelty is moderate**: The core method is feature engineering (combining known signals into a logistic regression router). The insight that these signals are complementary is reasonable but not deeply novel. The value is more in the experimental framing than the method itself.

**Single highest-leverage improvement**: Add CF-RAG and Knowledgeable-r1 to Related Work with explicit differentiation, and resolve the RC-RAG model-mismatch issue.

**Low-confidence flags**: Novelty confidence is medium (need to verify no other work has combined these exact signals); Significance confidence is medium (depends on whether the trivial baseline is already near-optimal).

---

## Insight Depth (Novelty)

**What the proposal claims**: The novelty is in (1) combining counterfactual stability (RC-RAG), context sufficiency (Sufficient Context), and disagreement/confidence signals into a multi-signal router, (2) targeting the "retrieval-harms" failure mode with an explicit no-retrieval channel, and (3) using RC-RAG+fallback as the strong baseline.

**Judgment (3/5 — clearly differentiated but moderate novelty)**:

The proposal is differentiated from its cited prior work:
- RC-RAG doesn't include a no-retrieval fallback or sufficiency signal.
- Sufficient Context doesn't use counterfactual stability or target misleading retrieval.
- RAGuard is a benchmark, not a method.
- Self-RAG / SR-RAG require training, not inference-time features.

However, the core method is **combining existing signals via logistic regression** — this is engineering-level composition rather than a new mechanism. The proposal does articulate *why* the combination should work (each signal covers a different failure mode), which elevates it above pure A+B. But a skeptical reviewer could argue this is "combine three known features into a classifier."

**Deep Research Log (novelty kill search)**:

| Query | Key findings |
|-------|-------------|
| "RC-RAG zero-context fallback" 2025 2026 | No published work combining RC-RAG with explicit zero-context fallback found. |
| "RAGuard routing abstain" 2025 2026 | RAGuard paper proposes no routing baseline; no follow-up work adding routing to RAGuard found. |
| "counterfactual stability" "context sufficiency" RAG routing 2025 2026 | No exact combination found. Sufficient Context (ICLR 2025) combines sufficiency + confidence but not counterfactual stability. |
| CF-RAG ICLR 2026 | CF-RAG uses counterfactual *queries* (not prompts) for causal reasoning in RAG. Different mechanism: generates counterfactual queries + parallel arbitration. Does not use sufficiency signal or no-retrieval fallback. Relevant competitor but substantially different approach. |
| Knowledgeable-r1 ICLR 2026 | RL-based training to balance parametric vs contextual knowledge. Training-heavy (not inference-time). Different approach but addresses similar failure mode (when to trust retrieval). |
| "multi-signal router" RAG retrieval harm 2025 2026 | No exact match. Pre-Route (ICLR 2026) routes between RAG and long-context (different setting). SR-RAG routes between retrieval and verbalized knowledge (training-based). |

**Verdict**: Differentiated — no prior work combines these exact three signals for inference-time routing with a no-retrieval fallback. However, the combination is somewhat predictable and the mechanism is feature engineering rather than a fundamentally new approach.

**Closest 3–5 works**:
1. **RC-RAG** (Chen et al., 2024): Counterfactual prompting for keep/discard — the proposal extends this with no-retrieval channel + sufficiency + disagreement.
2. **Sufficient Context** (Joren et al., ICLR 2025): Autorater + confidence for selective generation — the proposal adds stability and explicit routing.
3. **CF-RAG** (ICLR 2026): Counterfactual query generation + parallel arbitration — different mechanism, training-free but computationally heavier.
4. **Knowledgeable-r1** (ICLR 2026): RL training for parametric vs contextual knowledge — training-heavy, different approach.
5. **SR-RAG** (Wu et al., 2025): Self-routing via training — training-based, not targeted at misleading retrieval.

**Actionable fixes**:
1. Cite and differentiate from CF-RAG and Knowledgeable-r1.
2. Emphasize the practical advantage: training-free, lightweight, auditable (logistic regression/decision tree), which contrasts with training-heavy alternatives.

---

## Importance

**What the proposal claims**: Retrieval can harm LLM accuracy, as demonstrated by RAGuard (accuracy drops from 62.5% to 59.4% with retrieval, and to 36.8% with misleading-only docs). This matters for enterprise RAG deployments.

**Judgment (4/5 — real and current pain point, confidence: high)**:

Evidence strongly supports this is a real 2026 bottleneck:
- RAGuard (NeurIPS 2025) shows even frontier models (GPT-4o, Claude 3.5) suffer significant accuracy drops under misleading retrieval.
- URAG (2026) confirms retrieval doesn't uniformly improve reliability and can amplify overconfident errors.
- Multiple industry analyses (DEV Community, Medium 2026) identify retrieval quality as the primary failure mode in production RAG.
- Knowledgeable-r1's 2026 results show LLMs have a "context dominance" problem where they over-rely on retrieved content even when it's misleading.

**Who would switch**: RAG deployment teams at enterprises would immediately benefit from a lightweight, auditable routing layer that can be placed in front of any existing RAG pipeline without retraining.

**Strongest counterargument**: Frontier models may already handle misleading retrieval better (GPT-4o is most robust per RAGuard), and training-based approaches like Knowledgeable-r1 may eventually make inference-time routing unnecessary.

**Why rejected**: Even if frontier models improve, most deployments use smaller open-source models where the problem is severe. Training-based approaches require fine-tuning per model, while an inference-time router is model-agnostic and immediately deployable. The problem remains acute in 2026.

**What would drop this to 3**: Strong evidence that the RC-RAG+fallback trivial baseline already eliminates >90% of retrieval harm on RAGuard, making the router unnecessary.

---

## Significance

**What the proposal claims**: The result (positive or negative) would inform deployment policies for LLM assistants in noisy-information settings.

**Judgment (3/5 — result matters in a narrow but real regime, confidence: medium)**:

A positive result would provide a practical routing recipe for RAG deployments. However:
- The primary benchmark (RAGuard) is political fact-checking — a specific domain. Transfer to other retrieval-harm settings (medical, legal, general QA) is unproven.
- If the trivial baseline (RC-RAG+fallback) proves near-optimal, the significance reduces to "practitioners should just use the fallback" — still useful but less novel.
- A negative result (refute) is also informative: "RC-RAG+fallback is sufficient; don't bother with multi-signal routing." This has decision value.

The result matters in the narrow regime of misleading-retrieval settings but may not generalize broadly. The dual-benchmark design (RAGuard + RC-NQ/RC-TQ) helps but both are still QA/fact-checking tasks.

---

## Sharpness

**What the proposal claims**: The outcome separates three next actions: proceed (multi-signal router is better), pivot (specialize to misleading regimes only), or refute (trivial baseline is sufficient).

**Judgment (4/5 — sharp information gain, confidence: high)**:

The decision rule is well-specified:
- **Proceed**: Improvement at ≥2 coverage points, outside std range, for both models, with non-inferiority on RC-NQ/RC-TQ.
- **Pivot**: Helps on RAGuard but fails non-inferiority on RC-NQ/RC-TQ → specialized router.
- **Refute**: Trivial baseline matches or exceeds across coverage levels → abandon multi-signal approach.

Each outcome leads to a different concrete action. The accuracy–coverage curve framing adds nuance beyond a single scalar comparison. The matched-coverage evaluation prevents "answer less" confounds.

**Strongest counterargument**: The "outside std range" criterion may be too lenient given that RAGuard is a single dataset with potential domain-specific artifacts. Results could be driven by RAGuard-specific features (political content, Reddit corpus style) rather than general routing ability.

**Why rejected**: The proposal includes artifact checks (correlation with document length/style) and a second benchmark (RC-NQ/RC-TQ) which partially addresses this. The sharpness of the experimental design is strong even if generalizability is uncertain (that's a Soundness issue, not Sharpness).

**What would drop to 3**: If the decision rule thresholds were vague (e.g., "significant improvement") rather than the concrete ±1% absolute bounds specified.

---

## Decisiveness (Scope discipline)

**What the proposal claims**: A single core experiment (multi-signal router vs. RC-RAG+fallback across two benchmarks × two models) with ablations.

**Judgment (4/5 — decisive and immediately implementable, confidence: high)**:

- **One-sentence thesis**: ✅ (multi-signal router improves accuracy–coverage frontier over RC-RAG+fallback)
- **First experiment**: ✅ (generate 4 answers per query, compute features, train logistic regression, evaluate accuracy–coverage curves)
- **Stop rule**: ✅ (concrete proceed/pivot/refute conditions)
- **Benchmarks specified**: ✅ (RAGuard, RC-NQ/RC-TQ with download links)
- **Models specified**: ✅ (Llama 3 8B, Mistral 7B)
- **Resource estimate**: ✅ (~13k model calls per model, feasible on available hardware)

The Verification module can derive a concrete experiment plan from this proposal with minimal ambiguity.

**Strongest counterargument**: The calibration split details are missing — how large is the train split for the router? With 2,648 claims, a 60/20/20 split gives only ~530 claims for calibration, which is small for feature-based learning.

**Why rejected**: This is a valid concern but addressable with cross-validation; it doesn't prevent deriving a first experiment. It's a Soundness refinement, not a Decisiveness blocker.

**What would drop to 3**: If the proposal didn't specify which benchmarks, models, or metrics to use.

---

## Soundness

**What the proposal claims**: The experimental design is rigorous with ≥3 seeds, matched-coverage evaluation, artifact checks, sanity checks (random/oracle routers), and primary baseline alignment with both RC-RAG and RAGuard settings.

**Judgment (3/5 — broadly reasonable but important gaps remain, confidence: medium)**:

**Strengths**:
- Primary baseline alignment is excellent: adopts RC-RAG's metrics and RAGuard's settings.
- Matched-coverage evaluation is the right methodology for selective prediction.
- Artifact checks (correlation with document features) address a real confound.
- Sanity checks (random/oracle router) provide bounds.

**Gaps/Risks**:
1. **Model mismatch with RC-RAG**: RC-RAG published with ChatGPT; the proposal uses Llama 3 / Mistral. RC-RAG+fallback numbers are TBD — all baselines need re-running. This is noted but introduces risk that the re-run numbers may not match published behavior.
2. **Missing close competitors**: CF-RAG (ICLR 2026) and Knowledgeable-r1 (ICLR 2026) are not discussed. A reviewer would expect comparison or at least differentiation.
3. **Calibration split size**: With 2,648 RAGuard claims, the router training data may be small. No cross-validation or regularization strategy discussed.
4. **Sufficiency autorater specification**: "Gemini-family or FLAMe-style" is vague. The choice matters for quality and cost; need a specific model commitment.
5. **Single-domain risk on RAGuard**: Political fact-checking from Reddit is a specific domain. Document style, length distributions, and claim structures may not represent general retrieval-harm scenarios.

**Actionable fixes**:
1. Include at least one API model matching RC-RAG's setting, OR explicitly commit to re-running all RC-RAG baselines on Llama/Mistral and justify the substitution.
2. Cite CF-RAG and Knowledgeable-r1; explain why they are not direct baselines (training-heavy / different mechanism) but acknowledge them as competitive context.
3. Specify calibration protocol (e.g., 5-fold cross-validation for router training).
4. Commit to a specific sufficiency autorater model.

---

## Feasibility

**What the proposal claims**: ~13k model calls per base model (short classification outputs), feasible on 32×H200.

**Judgment (4/5 — operationally concrete and well within budget, confidence: high)**:

- **Benchmarks**: RAGuard is public (HuggingFace). RC-RAG code/data is public (GitHub). ✅
- **Models**: Llama 3 8B and Mistral 7B are downloadable. ✅
- **Compute**: 4 forward passes + 1 autorater call per claim, ~13k calls per model. With 7–8B models and short outputs, this is trivially feasible on 32×H200. Even with ≥3 seeds, total compute is modest.
- **Baseline rerun cost**: RC-RAG baselines need re-running on new models (RC-RAG+fallback is not in the original paper). This is additional cost but still modest given short output lengths.
- **Autorater cost**: If using Gemini API, this adds API cost but is manageable.

**Hard blockers**: None identified.

**Strongest counterargument**: If the proposal added an API frontier model (recommended for Soundness), API costs would increase but remain manageable.

**What would drop to 3**: If a key benchmark were private or the autorater model were unavailable.

---

## Elegance (Complexity-to-Payoff)

The design is deliberately lightweight: a logistic regression / shallow decision tree over a small feature vector. This is a strength — the complexity is low, the method is auditable, and the features are interpretable. The complexity-to-payoff ratio is favorable. **4/5**.

---

## Ethical Risks (Risk Level + Mitigation)

The proposal uses political fact-checking data (RAGuard) sourced from Reddit and PolitiFact. This involves politically sensitive content but the task is automated evaluation, not content generation or deployment. No human subjects, no adversarial content generation. Risk is manageable. **2/5** (low-moderate risk, adequate mitigation by using existing public benchmarks).

---

## Warnings / Limitations

### Recency risk
The proposal cites RC-RAG (2024), Sufficient Context (2025), and RAGuard (2025) as its primary building blocks. However, it **does not cite or discuss** two highly relevant 2026 works:
- **CF-RAG** (ICLR 2026): Counterfactual reasoning for RAG, addressing the same "correlation trap" / misleading retrieval problem.
- **Knowledgeable-r1** (ICLR 2026): RL-based training for parametric vs. contextual knowledge balance.

Both appeared at ICLR 2026 (presented April 2026) and are directly relevant. This is a **recency gap** that should be addressed before finalization.

### Format / template compliance
- The proposal has a "Scope and Constraints" section at the top that is not part of the standard template. This should be integrated into the Introduction or removed.
- The Related Work section has 20 papers (meeting the minimum) but the section structure is well-organized with taxonomy table and comparison table. ✅

### Readability suggestions
- **RAGuard**: First mention should include a brief description (e.g., "a political fact-checking benchmark where each claim is paired with documents labeled as supporting, misleading, or irrelevant"). ✅ (proposal does this)
- **RC-RAG**: The acronym expansion ("Controlling Risk of RAG") should appear at first mention. Partially done — the Introduction mentions it but the acronym isn't fully expanded inline.
- **a₀, aᵣ, a_cf-q, a_cf-u**: These notation symbols are introduced clearly. ✅
- **"Accuracy–coverage frontier"**: This concept should be briefly explained for readers unfamiliar with selective prediction. A one-sentence gloss would help.
- **"Counterfactual prompts"**: The proposal should briefly explain what these are (prompts that challenge the quality or usage of retrieval) on first use. ✅ (done in the proposal)
- **"FLAMe-style"**: This reference is vague — specify what FLAMe is or drop the reference.

### Portfolio note (mode collapse check)
The other proposal in the portfolio ("Correlation-Trap Citation Stress Test") also involves RAG robustness but focuses on citation faithfulness, not retrieval routing. The techniques are different (NLI stress testing vs. multi-signal routing). **No mode collapse detected** — topics and techniques are complementary rather than redundant.

---

## Blind Spots

1. **Shared context bias**: Both the proposal author and I have access to the same RAGuard/RC-RAG/Sufficient Context papers in the local KB. I may be overweighting these papers' importance and underweighting alternative framings from outside this citation cluster.

2. **Queries I wish I could run**: I would like to search for "retrieval routing logistic regression feature combination" to check if the specific feature-engineering approach has been tried in unpublished work or industry blog posts that don't appear in academic search. I would also want to check if RAGuard has been used as a routing benchmark in any follow-up work beyond the original paper.

3. **Assumptions that could be wrong**:
   - I'm assuming the RC-RAG codebase is functional and reproducible for re-running baselines. If it's poorly maintained, feasibility drops.
   - I'm assuming the sufficiency autorater is reliable enough to be a useful signal. If it's noisy, the router may not benefit from it.
   - I'm assuming RAGuard's 2,648 claims are sufficient for training + evaluating a router. This may be marginal.

4. **Areas of lowest confidence**:
   - Whether the trivial baseline (RC-RAG+fallback) is already near-optimal — this is the key uncertainty and determines whether the positive result is achievable.
   - Whether the feature-based router generalizes beyond RAGuard's political fact-checking domain.
   - Whether CF-RAG (ICLR 2026) subsumes the proposal's contribution in the eyes of reviewers, even though the mechanism is different.
