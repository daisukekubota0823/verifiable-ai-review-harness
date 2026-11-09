# Pilot Report — Local AI evaluation layer, measured before trusted

LifeAnalytics Inc. · 2026-11-08/09 · All runs local (llama.cpp, CPU), model Qwen2.5-3B-Instruct GGUF Q4_K_M, temperature 0, no network access.
Data: Schnell et al. 2025, human kidney organoids, LY294002 (PI3K inhibitor) 10 µM 48 h vs control (GEO GSE264217), analyzed with R DESeq2 1.42.0 (15,167 genes after filtering) and fgsea (Hallmark + Reactome, 1,054 pathways). Protocols were registered in configuration files before each run; headline metrics were recalculated independently (separate pandas implementation) and agreed exactly.

## Decision lines (pre-registered)
Classification: agreement ≥ 0.85, Cohen's κ ≥ 0.75, miss rate ≤ 0.05, false-detection rate ≤ 0.10. Verification: dangerous-miss rate ≤ 0.05, false-flag rate ≤ 0.10. Cases in a pre-registered borderline band around the thresholds are routed to human review by design and reported separately.

## Pilot 1 — Classification, English (300 cases)
Sample: 150 positives (35 UP / 115 DOWN), 60 borderline, 90 clear negatives; the model sees only the Ensembl ID and statistics.
- All cases: agreement 0.873, κ 0.792, miss 0.007, false detection 0.247.
- Borderline band: agreement 0.467; errors concentrated in over-calling changes where |log2FC| is large but padj is not significant.
- Auto-judged subset (routing applied, 240 cases, coverage 80%): agreement 0.975, κ 0.959, miss 0.007, false detection 0.056 — all decision lines met.

## Pilot 2 — Verification of draft statements, English (84 items)
Half of the statements carry one controlled error (flipped direction, significance asserted against the values, or numbers taken from a different row). An initial version (v1) contained ambiguous statement semantics (bare direction claims on non-significant rows); a full disagreement audit identified the flaw, the construction was fixed, and v2 was re-run.
- v2: agreement 0.738, κ 0.476, dangerous miss 0.143, false flag 0.381 — below the decision lines.
- Audit: false flags are dominated by "no significant change" statements with large |NES| (the model reads effect size over the significance rule); dangerous misses include flipped signs and threshold violations passed as supported.
- Design consequence: checks reducible to numbers are performed deterministically by the platform; verification and drafting are assigned to the largest local tier (36B class) and gated by the same protocol.

## Pilot 3 — Review drafting over the full record
- Free drafting: 22 numbers in the draft, 0 unsupported; all gene IDs and pathway names from the record.
- Slot-filled drafting (platform fills every value; model writes interpretation only): 0 introduced numbers, IDs or pathway names; 1 self-contradictory interpretive claim, which numeric audits cannot detect.
- Design consequence: interpretations are presented with per-sentence provenance, behind a human approval gate.

## Pilot 4 — Classification, Japanese (identical 300 cases; record and instructions in Japanese)
- All cases: agreement 0.830, κ 0.730, miss 0.007, false detection 0.333.
- Auto-judged subset: agreement 0.950, κ 0.918, miss 0.007, false detection 0.122 — the false-detection line (≤ 0.10) is failed in Japanese only.
- 24 cases flipped from correct (EN) to incorrect (JP); 19 are unchanged results over-called as UP; clear-negative errors rose 5 → 11.

## Pilot 5 — Verification, Japanese (identical 84 items)
Statement labels spot-audited for correctness before use.
- Agreement 0.619, κ 0.238, dangerous miss 0.333 (EN: 0.143), false flag 0.429 (EN: 0.381).
- The language penalty is largest in the verification class and falls on the dangerous side (false statements passed).

## Standing conclusions
1. With pre-registered routing, a 3B local model clears all classification lines in English; the routing rule is load-bearing, not decorative.
2. Verification at the 3B tier is below the lines in both languages; numbers are checked deterministically, and model judgment is confined to classification and provenance-linked interpretation.
3. Record language is a measured variable in AI quality: the same system that passes in English fails a pre-registered line in Japanese, in classification by false detections and in verification by dangerous misses.

## Pilot 6 — tier gradient, verification (English, same 84 statements, Qwen2.5-7B-Instruct Q4_K_M, CPU, temperature 0)
- All items: agreement 90.5%, kappa 0.810, dangerous miss 14.3%, false flag 4.8%.
- Against the 3B run on identical items (agreement 73.8%, kappa 0.476, dangerous miss 14.3%, false flag 38.1%): scale repaired precision (false flags 38.1% -> 4.8%, below the 10% line; agreement and kappa now above their lines) but did not move the dangerous-miss rate at all (14.3% at both sizes, line 5%).
- Consequence for the design: verification is not assigned to a larger tier on the expectation that scale clears its lines; the dangerous side is carried by deterministic checking and the human gate at every tier. The 36B tier in the application is a measurement target under the same protocol, not a promised pass.

## Pilot 7 — tier gradient, verification, Japanese (identical 84 items, 7B)
- All items: agreement 86.9%, kappa 0.738, dangerous miss 21.4%, false flag 4.8%.
- Against the 3B run on identical items (agreement 61.9%, kappa 0.238, dangerous miss 33.3%, false flag 42.9%): scale repaired precision completely (false flags 42.9% -> 4.8%) and reduced the dangerous side (33.3% -> 21.4%) without clearing it — the dangerous-miss line (5%) is failed at both tiers, in both languages.
- The language penalty in verification persists at 7B (dangerous miss JP 21.4% vs EN 14.3%).

## Pilot 8 — tier gradient, classification, English (identical 300 cases, 7B)
- All cases: agreement 93.0%, kappa 0.884, miss 0.0%, false detection 14.0%.
- Auto-judged subset: agreement 99.6%, kappa 0.993, miss 0.0%, false detection 1.1% — every decision line cleared with margin (3B auto: 97.5% / 0.959 / 0.7% / 5.6%).

## Pilot 9 — tier gradient, classification, Japanese (identical 300 cases, 7B)
- All cases: agreement 88.0%, kappa 0.796, miss 14.7%, false detection 9.3%.
- Auto-judged subset: agreement 90.0%, kappa 0.838, miss 14.7%, false detection 2.2% — the miss line (<= 5%) is failed: 22 of 150 changed genes were called NO_CHANGE.
- Against the 3B run on identical cases (auto: agreement 95.0%, kappa 0.918, miss 0.7%, false detection 12.2%): scale repaired the false-detection side (12.2% -> 2.2%) and broke the miss side (0.7% -> 14.7%). The failure mode migrates with scale; Japanese classification clears its lines at NEITHER tier and is therefore not deployed automatically in Japanese under this protocol. Per-language, per-tier gating is not a formality: the same class passes in English at both tiers and fails in Japanese at both tiers, for opposite reasons.

## Updated standing conclusions (supersede the list above where they differ)
1. Classification clears all lines in English at both tiers on the auto-judged subset; routing remains load-bearing for the all-cases numbers.
2. Verification is below the dangerous-miss line at both tiers in both languages; deterministic checking and the human gate carry that side by design, and the 36B tier is a measurement target, not an assumed pass.
3. Record language is a measured variable: Japanese verification is worse on the dangerous side at both tiers, and Japanese classification fails at both tiers with scale-dependent failure modes — the benchmark's per-language, per-tier design is the finding, not a detail.

## Benchmark v1 baselines (3B tier, benchmark_v1 release set, Qwen2.5-3B-Instruct Q4_K_M, CPU, temperature 0)
The release benchmark (600 RNA-seq classification cases: positive 300 / borderline 120 / clear 180; ground truth mechanical from the DESeq2 1.42.0 source, audit PASS) run under the same pre-registered decision lines. Borderline cases are routed to human review by design; "auto-judged" = the remaining 480.

### Benchmark classification, English (600)
- All cases: agreement 92.5%, kappa 0.876, miss 0.3%, false detection 14.7%.
- Auto-judged subset (480): agreement 98.1%, kappa 0.970, miss 0.3%, false detection 4.4% — all decision lines cleared (agreement >= 0.85, kappa >= 0.75, miss <= 0.05, false detection <= 0.10).
- Zero parse failures. Independent recalculation from the raw result file agrees exactly.
- Japanese classification, verification (EN/JP) and the dose-response / microscopy baselines follow as their runs complete.

### Benchmark classification, Japanese (600, identical cases)
- All cases: agreement 92.8%, kappa 0.882, miss 5.0%, false detection 9.3%.
- Auto-judged subset (480): agreement 95.8%, kappa 0.933, miss 5.0%, false detection 2.8% — the miss rate sits exactly on the pre-registered line (<= 0.05; 15 of 300 changed genes called NO_CHANGE), where the English run cleared it at 0.3%. On the larger release set the Japanese failure balance differs from the 300-case pilot (false detections repaired, misses at the boundary): per-language gating at the 3B tier keeps Japanese classification behind the human gate until a tier clears it with margin.
- Zero parse failures. Independent recalculation agrees exactly.

### Benchmark verification, English (120 statements)
- All items: agreement 74.2%, kappa 0.483, dangerous miss 43.3%, false flag 8.3%.
- Consistent with the 84-statement pilot: verification is the class where model judgment is weakest on the dangerous side, which is why the harness carries that side with deterministic checking and the human gate rather than model judgment. Japanese verification and the dose-response / microscopy baselines follow.
