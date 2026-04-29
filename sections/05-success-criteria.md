## Success Criteria

**Hypothesis (directional).** The multi-signal router will improve selective accuracy at the same coverage compared to RC-RAG+fallback on RAGuard, and will not materially worsen risk/carefulness on RC-NQ/RC-TQ.

**Decision Rule (concrete).**
- **Proceed**: On RAGuard, ours improves selective accuracy by a margin outside the std range at ≥2 coverage points (e.g., 70% and 90% coverage) over RC-RAG+fallback for both Llama and Mistral; and on RC-NQ/RC-TQ, risk is **≤ (RC-RAG baseline + 1% absolute)** at matched coverage and carefulness is **≥ (baseline − 1% absolute)**.
- **Pivot**: If ours helps on RAGuard but fails non-inferiority on RC-NQ/RC-TQ, restrict scope to misleading-retrieval regimes and treat as a specialized router; remove abstention and focus on retrieval vs no-retrieval routing.
- **Refute**: If RC-RAG+fallback matches or exceeds ours across coverage levels on RAGuard, abandon the multi-signal router and instead focus on characterizing the failure modes/conditions where fallback is sufficient.

---