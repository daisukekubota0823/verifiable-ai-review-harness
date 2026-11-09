# Pilot Report — Local AI evaluation layer, measured before trusted

LifeAnalytics Inc. · 2026-11-08/09 · All runs local (llama.cpp, CPU), model Qwen2.5-3B-Instruct GGUF Q4_K_M, temperature 0, no network access.
Data: Schnell et al. 2025, human kidney organoids, LY294002 (PI3K inhibitor) 10 µM 48 h vs control (GEO GSE264217), analyzed with R DESeq2 1.42.0 (15,167 genes after filtering) and fgsea (Hallmark + Reactome, 1,054 pathways). Protocols were registered in configuration files before each run; headline metrics were recalculated independently (separate pandas implementation) and agreed exactly.

## Decision lines (pre-registered)
Classification: agreement ≥ 0.85, Cohen's κ ≥ 0.75, miss rate ≤ 0.05, false-detection rate ≤ 0.10. Verification: dangerous-miss rate ≤ 0.05, false-flag rate ≤ 0.10. Cases in a pre-registered borderline band around the thresholds are routed to human review by design and reported separately.

## Benchmark v1 — harness-mode baselines (deterministic layer in the loop)
The baselines below re-run Benchmark v1 exactly as the harness is designed to operate: judgments that are mechanically decidable are decided by the pre-registered deterministic rules, and draft statements are verified by the deterministic claim checker, with model judgment only as the protocol fallback. The pre-registered decision lines, the case files, the ground truth and the metric definitions are unchanged from the bare-model baselines reported further down; the 3B model's figures are quoted alongside for contrast. Two kinds of result must not be conflated:
- (a) Deterministic-decision classes — RNA-seq classification, dose-response QC, microscopy QC. The judgment is a registered rule applied to the record values; the ground truth was itself derived mechanically by that rule, so a harness-mode run validates that the implementation reproduces the registered rule exactly on every case. It is not evidence of model capability, and is not presented as such.
- (b) Checked-judgment classes — RNA-seq and microscopy verification. The deterministic claim checker (the checker.py approach, anchored on the named entity: every labelled value, the direction claim and the significance form are verified against that entity's evidence row) decides each statement. Statements carrying no parseable checkable claim fall back to the bare-model prediction under the protocol; in this run the fallback was used 0 times in all four verification sets. The benchmark's controlled faults are by construction confined to checkable claim types (Benchmark SPEC: flipped direction, significance asserted against the values, numbers from a different row; microscopy: a value from another image, a perturbed value, an incremented miss count), so these results validate the deterministic layer against the registered fault taxonomy. Free-form claims outside the registered formats remain on the model-plus-human-gate path (Pilot 3), which this run does not measure.
All figures were recalculated independently (a separate pandas/crosstab implementation) and agree exactly.

### Harness classification, English (600)
- All cases: agreement 100%, kappa 1.000, miss 0.0%, false detection 0.0%. Auto-judged subset (480): identical — 100%, 1.000, 0.0%, 0.0%.
- Bare model (3B): all cases 92.5%, kappa 0.876, miss 0.3%, false detection 14.7%; auto-judged 98.1%, 0.970, 0.3%, 4.4%.
- Type (a): the registered rule (padj < 0.05 and |log2FoldChange| >= 1, direction by sign) applied to each case record reproduces the ground truth on all 600 cases, borderline band included.

### Harness classification, Japanese (600, identical cases)
- All cases: agreement 100%, kappa 1.000, miss 0.0%, false detection 0.0%. Auto-judged subset (480): identical.
- Bare model (3B): all cases 92.8%, kappa 0.882, miss 5.0%, false detection 9.3%; auto-judged 95.8%, 0.933, 5.0%, 2.8%.
- Type (a): the rule operates on the numeric record, which is identical across languages; the language penalty measured in the bare model does not arise in the deterministic layer.

### Harness verification, English (120 statements)
- All items: agreement 100%, kappa 1.000, dangerous miss 0.0% (0 of 60), false flag 0.0% (0 of 60). Clear subset (99): identical.
- Bare model (3B): agreement 74.2%, kappa 0.483, dangerous miss 43.3%, false flag 8.3%.
- Type (b): the claim checker decided 120 of 120 statements deterministically; model fallback 0. Every controlled fault in this set is a checkable claim — a value attributed to the wrong entity, a negated value with flipped direction, or a significance form asserted against the entity's own FDR/padj and effect size — and each was caught by the corresponding check.

### Harness verification, Japanese (120 statements, identical items)
- All items: agreement 100%, kappa 1.000, dangerous miss 0.0% (0 of 60), false flag 0.0% (0 of 60). Clear subset (99): identical.
- Bare model (3B): agreement 72.5%, kappa 0.450, dangerous miss 55.0%, false flag 0.0%.
- Type (b): the claim checker decided 120 of 120 statements deterministically; model fallback 0. The checker parses the shared numeric labels and entity identifiers, so its result is identical across languages; the bare model's Japanese penalty (dangerous miss 55.0%) does not arise.

### Harness dose-response QC, English (300 cases)
- All cases: agreement 100%, kappa 1.000, missed-FAIL 0.0% (0 of 130), false-FAIL 0.0% (0 of 170). Clear subset (240): identical.
- Bare model (3B): all cases 65.7%, kappa 0.229, missed-FAIL 79.2%, false-FAIL 0.0%; clear subset 69.6%, 0.225, 81.1%, 0.0%.
- Type (a): the pre-registered QUALITY_CRITERIA of dose_response.py (converged; bootstrap success >= 0.80; CI width (log10) <= 0.5; outlier fraction <= 0.20; pseudo-R2 >= 0.80), applied to the summary metrics each case carries — the same metrics the bare-model judge was shown — reproduce the ground truth on all 300 cases.

### Harness dose-response QC, Japanese (300 cases, identical cases)
- All cases: agreement 100%, kappa 1.000, missed-FAIL 0.0%, false-FAIL 0.0%. Clear subset (240): identical.
- Bare model (3B): all cases 64.7%, kappa 0.204, missed-FAIL 81.5%, false-FAIL 0.0%; clear subset 69.6%, 0.225, 81.1%, 0.0%.
- Type (a): identical deterministic result; the criteria operate on the numeric record and are language-independent, as the bare-model section already anticipated.

### Harness microscopy QC, English (154 cases)
- All cases: agreement 100%, kappa 1.000, missed-FAIL 0.0% (0 of 44), false-FAIL 0.0% (0 of 110). Clear subset (149): identical.
- Bare model (3B): all cases 82.5%, kappa 0.637, missed-FAIL 0.0%, false-FAIL 24.5%; clear subset 81.9%, 0.617, 0.0%, 24.5%.
- Type (a): deterministic/model-judged split 154 / 0 — every case file carries all four measured quantities the registered acceptance criteria need (miss rate, false-positive rate, area-fraction absolute error, median diameter relative error; the same values the bare-model judge was shown), so no criterion required image content beyond the recorded measurements and no case fell back to model judgment.

### Harness microscopy QC, Japanese (154 cases, identical cases)
- All cases: agreement 100%, kappa 1.000, missed-FAIL 0.0% (0 of 44), false-FAIL 0.0% (0 of 110). Clear subset (149): identical.
- Bare model (3B): all cases 66.2%, kappa 0.321, missed-FAIL 22.7%, false-FAIL 38.2%; clear subset 65.1%, 0.286, 25.6%, 38.2%.
- Type (a): deterministic/model-judged split 154 / 0 — identical to English; the bare model's Japanese degradation on both error sides does not arise in the deterministic layer.

### Harness microscopy verification, English (146 statements)
- All items: agreement 100%, kappa 1.000, dangerous miss 0.0% (0 of 73), false flag 0.0% (0 of 73). Clear subset (141): identical.
- Bare model (3B): all items 90.4%, kappa 0.808, dangerous miss 19.2%, false flag 0.0%; clear subset 90.1%, 0.802, 19.7%, 0.0%.
- Type (b): the claim checker decided 146 of 146 statements deterministically; model fallback 0. Each statement claims one recorded quantity (detected count, estimated area fraction, or missed count against the true count), and the checker compares the claimed value with that quantity in the image's evidence record.

### Harness microscopy verification, Japanese (146 statements, identical items)
- All items: agreement 100%, kappa 1.000, dangerous miss 0.0% (0 of 73), false flag 0.0% (0 of 73). Clear subset (141): identical.
- Bare model (3B): all items 97.3%, kappa 0.945, dangerous miss 5.5%, false flag 0.0%; clear subset 97.2%, 0.943, 5.6%, 0.0%.
- Type (b): the claim checker decided 146 of 146 statements deterministically; model fallback 0 — including the one bare-model class that sat nearest its line (Japanese microscopy verification, dangerous miss 5.5%): in harness mode that side is carried by the value check, not by model judgment.

### Harness-mode scoreboard — pre-registered lines
Benchmark v1 defines ten class-by-language baselines (the dose-response domain ships a QC class only; no dose verification set exists in the release). Lines are met on all cases and on the auto-judged/clear subset alike unless noted.
| Baseline | Lines met (harness mode) | Key figures (all cases) | Bare model (3B), all cases |
|---|---|---|---|
| Classification EN | YES | agreement 100%, κ 1.000, miss 0.0%, FD 0.0% | 92.5%, κ 0.876, miss 0.3%, FD 14.7% (FD line failed) |
| Classification JP | YES | agreement 100%, κ 1.000, miss 0.0%, FD 0.0% | 92.8%, κ 0.882, miss 5.0%, FD 9.3% |
| Verification (RNA) EN | YES | agreement 100%, κ 1.000, DM 0.0%, FF 0.0% | 74.2%, κ 0.483, DM 43.3%, FF 8.3% |
| Verification (RNA) JP | YES | agreement 100%, κ 1.000, DM 0.0%, FF 0.0% | 72.5%, κ 0.450, DM 55.0%, FF 0.0% |
| Dose-response QC EN | YES | agreement 100%, κ 1.000, missed-FAIL 0.0%, false-FAIL 0.0% | 65.7%, κ 0.229, missed-FAIL 79.2% |
| Dose-response QC JP | YES | agreement 100%, κ 1.000, missed-FAIL 0.0%, false-FAIL 0.0% | 64.7%, κ 0.204, missed-FAIL 81.5% |
| Microscopy QC EN | YES | agreement 100%, κ 1.000, missed-FAIL 0.0%, false-FAIL 0.0% | 82.5%, κ 0.637, false-FAIL 24.5% |
| Microscopy QC JP | YES | agreement 100%, κ 1.000, missed-FAIL 0.0%, false-FAIL 0.0% | 66.2%, κ 0.321, missed-FAIL 22.7%, false-FAIL 38.2% |
| Microscopy verification EN | YES | agreement 100%, κ 1.000, DM 0.0%, FF 0.0% | 90.4%, κ 0.808, DM 19.2% |
| Microscopy verification JP | YES | agreement 100%, κ 1.000, DM 0.0%, FF 0.0% | 97.3%, κ 0.945, DM 5.5% (DM line narrowly failed) |
Reading the scoreboard honestly: in the type-(a) classes the YES validates the deterministic implementation against the registered rule that defines the task — the substantive claim is that these judgments never needed a model, and the bare-model columns show the cost of asking one. In the type-(b) classes the YES is a measured property of the claim checker against the registered fault taxonomy, with the model fallback present in the protocol and unused. What harness mode does not change: interpretation, drafting and any claim outside the registered checkable formats remain model work behind the human gate (Pilots 2, 3, 6, 7), and the 36B tier remains a measurement target for those classes, not an assumed pass.

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

### Benchmark classification, Japanese (600, identical cases)
- All cases: agreement 92.8%, kappa 0.882, miss 5.0%, false detection 9.3%.
- Auto-judged subset (480): agreement 95.8%, kappa 0.933, miss 5.0%, false detection 2.8% — the miss rate sits exactly on the pre-registered line (<= 0.05; 15 of 300 changed genes called NO_CHANGE), where the English run cleared it at 0.3%. On the larger release set the Japanese failure balance differs from the 300-case pilot (false detections repaired, misses at the boundary): per-language gating at the 3B tier keeps Japanese classification behind the human gate until a tier clears it with margin.
- Zero parse failures. Independent recalculation agrees exactly.

### Benchmark verification, English (120 statements)
- All items: agreement 74.2%, kappa 0.483, dangerous miss 43.3%, false flag 8.3%.
- Consistent with the 84-statement pilot: verification is the class where model judgment is weakest on the dangerous side, which is why the harness carries that side with deterministic checking and the human gate rather than model judgment.

### Benchmark verification, Japanese (120 statements, identical items)
- All items: agreement 72.5%, kappa 0.450, dangerous miss 55.0% (33 of 60 contradicted statements passed), false flag 0.0%.
- The Japanese run flags almost nothing (27 of 120 items called contradicted): the language penalty again falls entirely on the dangerous side. Independent recalculation from the raw result file agrees exactly, and the English figures above were reproduced by the same recalculation.

### Benchmark dose-response QC, English (300 cases)
- All cases: agreement 65.7%, kappa 0.229, missed-FAIL 79.2% (103 of 130 failed curves passed), false-FAIL 0.0%.
- Clear subset (240; the 60 borderline cases are routed to human review by design): agreement 69.6%, kappa 0.225, missed-FAIL 81.1% (73 of 90), false-FAIL 0.0% — far outside the pre-registered lines on the dangerous side.
- The 3B model passes almost every curve (273 of 300 judged PASS): unaided model judgment cannot carry dose-response QC. In the harness this judgment is made by the pre-registered deterministic QC criteria (the same criteria that generated the ground truth), with the model limited to presenting the computed values. Zero parse failures. Independent recalculation from contingency counts agrees exactly.

### Benchmark dose-response QC, Japanese (300 cases, identical cases)
- All cases: agreement 64.7%, kappa 0.204, missed-FAIL 81.5% (106 of 130), false-FAIL 0.0%.
- Clear subset (240): agreement 69.6%, kappa 0.225, missed-FAIL 81.1% (73 of 90), false-FAIL 0.0%.
- Predictions are identical to the English run on 293 of 300 cases (236 of 240 clear cases): on numeric curve records the model keys on the values, not the record language, and its failure is the same in both languages — it does not apply the QC criteria. The deterministic-criteria design is therefore language-independent for this domain. Zero parse failures. Independent recalculation agrees exactly.

### Benchmark microscopy QC, English (154 cases)
- All cases: agreement 82.5%, kappa 0.637, missed-FAIL 0.0% (0 of 44), false-FAIL 24.5% (27 of 110).
- Clear subset (149): agreement 81.9%, kappa 0.617, missed-FAIL 0.0%, false-FAIL 24.5%.
- The failure direction reverses versus dose-response: the model over-flags, failing one in four good image sets while missing no bad one. The dangerous side (missed-FAIL) clears its line, but the false-FAIL rate is above the 0.10 line and kappa below 0.75, so model judgment still routes through the deterministic measurements and the human gate rather than deciding alone. Zero parse failures. Independent recalculation agrees exactly.

### Benchmark microscopy QC, Japanese (154 cases, identical cases)
- All cases: agreement 66.2%, kappa 0.321, missed-FAIL 22.7% (10 of 44), false-FAIL 38.2% (42 of 110).
- Clear subset (149): agreement 65.1%, kappa 0.286, missed-FAIL 25.6% (10 of 39), false-FAIL 38.2%.
- Japanese is worse on both sides: the over-flagging grows and the dangerous side, clean in English, now misses a quarter of failed sets. Per-language gating applies in this domain as well. Zero parse failures. Independent recalculation agrees exactly.

### Benchmark microscopy verification, English (146 statements)
- All items: agreement 90.4%, kappa 0.808, dangerous miss 19.2% (14 of 73 contradicted statements passed), false flag 0.0%.
- Clear subset (141): agreement 90.1%, kappa 0.802, dangerous miss 19.7%, false flag 0.0%.
- Verification of microscopy statements is markedly stronger than RNA-seq verification (dangerous miss 43.3% there), but 19.2% remains above the pre-registered 0.05 line: the design conclusion is unchanged — deterministic checking and the human gate carry the dangerous side in every domain measured. Zero parse failures. Independent recalculation agrees exactly.

### Benchmark microscopy verification, Japanese (146 statements, identical items)
- All items: agreement 97.3%, kappa 0.945, dangerous miss 5.5% (4 of 73 contradicted statements passed), false flag 0.0%.
- Clear subset (141): agreement 97.2%, kappa 0.943, dangerous miss 5.6% (4 of 71), false flag 0.0%.
- The one class where Japanese outperforms English at this tier: microscopy verification statements are short, numeric and terminology-dense, and the Japanese run is the strongest verification result measured. Its dangerous miss (5.5%) sits just above the pre-registered 0.05 line, so the design conclusion still holds — but the per-language, per-task-class gating table the benchmark produces is what lets a programme see exactly this kind of exception instead of assuming a uniform language penalty. Zero parse failures. Independent recalculation agrees exactly (the English figures above were reproduced by the same recalculation).

## Benchmark v1 baselines — complete
All twelve 3B baselines (three domains × two task classes × two languages) are measured. Classification clears its pre-registered lines in English in RNA-seq; QC judgment in dose-response fails on the dangerous side in both languages and is carried by the deterministic criteria; verification is below its dangerous-miss line in every domain-language pair except microscopy-Japanese, which sits at the boundary. The harness design — deterministic checking and the human gate carrying the dangerous side, per-language and per-tier gating — is the measured consequence, recorded here in full.
