# Novelty and Competitor Search Log

Date: 2026-04-29

Queries checked:

- "RC-RAG zero-context fallback"
- "RAGuard routing abstain"
- "misleading retrieval do-no-harm router"
- "counterfactual stability context sufficiency RAG routing"
- "RAGRouter-Bench Adaptive RAG Routing"
- "Trustworthy Adaptive Retrieval Generation TARG"

Current interpretation:

- No exact prior work was found that combines RC-RAG-style counterfactual stability with an explicit no-retrieval fallback and sufficiency signal on misleading-retrieval benchmarks.
- TARG is a strong training-free adaptive retrieval baseline and should be discussed as a close routing competitor.
- RAGRouter-Bench is a broader adaptive RAG routing benchmark and should be used to frame generalization risk, even if it is not a primary short-paper experiment.
- CF-RAG and Knowledgeable-R1 address related retrieval-interference failure modes but use heavier counterfactual query/arbitration or model training rather than a lightweight inference-time router.
