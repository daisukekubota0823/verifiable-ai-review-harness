# Verifiable local AI for experiment records — evaluation harness (prototype)

Protocols, runners and auditors used to measure whether a small, locally-run model may judge an experiment record — before anyone trusts it. Every protocol is registered in a configuration file before the run; every headline metric is recalculated by an independent implementation.

Pilots (see PILOT_REPORT.md for methods, audits and full results):
1. Classification of differential-expression results (English) — 300 blinded cases, pre-registered borderline band routed to human review.
2. Verification of draft statements against the record (English) — 84 statements, half with a controlled error. (v1 contained ambiguous statement semantics; found by disagreement audit, fixed, re-run as v2.)
3. Review drafting over a full record — free drafting vs slot-filled drafting, with a deterministic claim audit.
4. Classification, Japanese — identical cases, record language as the only change.
5. Verification, Japanese — identical items.

Data: public dataset GEO GSE264217 (Schnell et al. 2025), DESeq2 1.42.0 / fgsea reference results.
Model used in the pilots: Qwen2.5-3B-Instruct (GGUF Q4_K_M) via llama.cpp, CPU-local, temperature 0.

Status: research prototype accompanying a Mozilla Foundation Human-Scale AI Incubator application (LifeAnalytics Inc.). License to be set at public release.

## Benchmark v1 (RNA-seq domain) — included in this repository
`benchmark_v1/` contains the first benchmark release: 600 classification cases and 120 verification statements, each in English and Japanese versions with identical values and ground truth, plus the construction code, the specification (SPEC.md) and the scoring scripts. Ground truth is derived mechanically from DESeq2 1.42.0 results on GEO GSE264217 under the registered rule; borderline cases are routed to human review by design and scored separately.

## Measured results behind this project (pilot report summary)
Local model: Qwen2.5-3B-Instruct (GGUF Q4_K_M), llama.cpp, CPU, temperature 0. Data: DESeq2 1.42.0 / fgsea results on GEO GSE264217. Decision lines pre-registered (agreement >= 0.85, kappa >= 0.75, miss <= 0.05, false detection <= 0.10, dangerous miss <= 0.05).

| Pilot | Set | Agreement | kappa | Key rates |
|---|---|---|---|---|
| Classification EN | auto-judged 240/300 | 97.5% | 0.959 | miss 0.7%, false detection 5.6% — all lines cleared |
| Classification JP (identical cases) | auto-judged 240/300 | 95.0% | 0.918 | miss 0.7%, false detection 12.2% — false-detection line failed in Japanese only |
| Verification EN | 84 statements | 73.8% | 0.476 | dangerous miss 14.3%, false flag 38.1% — below lines |
| Verification JP (identical items) | 84 statements | 61.9% | 0.238 | dangerous miss 33.3%, false flag 42.9% — language penalty largest, on the dangerous side |
| Classification EN, 7B tier | auto-judged 240/300 | 99.6% | 0.993 | miss 0.0%, false detection 1.1% — all lines cleared with margin |
| Classification JP, 7B tier | auto-judged 240/300 | 90.0% | 0.838 | miss 14.7%, false detection 2.2% — scale repaired false detections and broke the miss side; Japanese classification clears at neither tier |
| Verification EN, 7B tier | 84 statements | 90.5% | 0.810 | dangerous miss 14.3% (unchanged from 3B), false flag 4.8% — precision repaired, the dangerous side not |
| Verification JP, 7B tier | 84 statements | 86.9% | 0.738 | dangerous miss 21.4% (3B: 33.3%), false flag 4.8% — improved, still four times the line |
| Drafting | full record | — | — | free draft: 22 numbers, 0 unsupported; slot-filled: 0 introduced values; interpretations carry per-sentence provenance behind a human gate |
| Benchmark v1 classification EN (3B) | auto-judged 480/600 | 98.1% | 0.970 | miss 0.3%, false detection 4.4% — all lines cleared on the release benchmark |
| Benchmark v1 classification JP (3B, identical cases) | auto-judged 480/600 | 95.8% | 0.933 | miss 5.0% — exactly on the line (EN: 0.3%); false detection 2.8% |
| Benchmark v1 verification EN (3B) | 120 statements | 74.2% | 0.483 | dangerous miss 43.3%, false flag 8.3% — the dangerous side is carried by deterministic checking and the human gate by design |

Full protocols, raw outputs and the independent recalculation: PILOT_REPORT.md. Benchmark v1 baselines for the remaining languages and domains are added to PILOT_REPORT.md as their runs complete.

## Deterministic checker (runnable)
`checker/checker.py` verifies a draft against a record: every number and every Ensembl identifier in the draft must be present in the record, or it is flagged. Demonstration included: `draft_supported.txt` passes clean against the pilot record; `draft_corrupted.txt` (one invented value, one invented identifier) is flagged on both. Presence checking catches values that appear nowhere in the record; in the deployed harness the same check runs row-scoped, against the values of the entity the sentence describes, because the platform fills values from that row.
