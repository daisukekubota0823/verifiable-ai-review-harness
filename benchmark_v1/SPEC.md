# Benchmark v1 — RNA-seq domain (specification)
- Cases: 600 classification (positive 300 / borderline 120 / clear-negative 180), 120 verification statements (60 supported / 60 contradicted; controlled faults: flipped direction, significance asserted against the values, numbers from a different row).
- Ground truth: derived mechanically from DESeq2 1.42.0 results on GEO GSE264217 under the registered rule (padj < 0.05 and |log2FC| >= 1, direction by sign). Borderline band: NO_CHANGE cases with padj in [0.03, 0.08] or |log2FC| in [0.85, 1.15]; routed to human review by design, scored separately.
- Languages: every item exists in English and Japanese versions with identical values and ground truth; only the record language differs.
- Scoring: agreement, Cohen's kappa, miss rate, false-detection rate (classification); dangerous-miss and false-flag rates (verification); reported per language, overall and on the auto-judged subset. Decision lines: agreement >= 0.85, kappa >= 0.75, miss <= 0.05, false detection <= 0.10, dangerous miss <= 0.05.
- Seed 20261120, distinct from all pilot samples. Construction code: build_benchmark.py.
