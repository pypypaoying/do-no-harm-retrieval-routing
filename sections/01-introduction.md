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
