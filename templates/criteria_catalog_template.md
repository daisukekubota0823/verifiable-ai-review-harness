# Criteria catalog template (v0)
A lab copies this file, fills in its own thresholds in its own language, and registers it
before any measurement run. The harness reads the registered catalog; decision lines are
never edited after a run has started. Borderline cases are routed to a human reviewer by
design and scored separately.

## 1. Result classification (example: differential expression)
- Rule: UP if padj < [0.05] and log2FoldChange >= [1]; DOWN if padj < [0.05] and log2FoldChange <= [-1]; otherwise NO_CHANGE.
- Borderline band: padj in [0.03, 0.08] or |log2FoldChange| in [0.85, 1.15] among NO_CHANGE cases.
- Decision lines: agreement >= [0.85]; Cohen's kappa >= [0.75]; miss rate <= [0.05]; false-detection rate <= [0.10].

## 2. Statement verification
- A statement is CONTRADICTED if any value, direction, or significance claim in it conflicts with the record.
- Decision lines: dangerous-miss rate (contradicted judged supported) <= [0.05]; false-flag rate <= [0.10].
- Numbers, signs and thresholds are checked deterministically by the platform, never by the model.

## 3. Curve-fit quality control (example: dose-response)
- Criteria (all must hold): converged; bootstrap success rate >= [0.80]; CI width (log10) <= [0.5]; outlier fraction <= [0.20]; pseudo-R2 >= [0.80].
- Borderline margins: CI width +-[0.05]; pseudo-R2 +-[0.02]; outlier fraction +-[0.03]; bootstrap success +-[0.05].

## 4. Image quantification acceptance (example: microscopy)
- Criteria (all must hold): miss rate <= [0.05]; false-positive rate <= [0.05]; area-fraction absolute error <= [0.5] points; median diameter relative error <= [0.05].
- Borderline margins: [0.01] / [0.01] / [0.1] points / [0.01].

## Registration record
- Lab: [name]  Domain: [section numbers used]  Language of record: [language]
- Model and version measured: [ ]  Date registered: [ ]  Registered by: [ ]
- Rule: a judgment class is deployed in a language only if it clears every line in that language on the benchmark (or on the lab's own registered cases); the result is recorded here either way.
