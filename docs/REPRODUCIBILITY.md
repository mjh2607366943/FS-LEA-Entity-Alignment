# Reproducibility levels and schemas

| Level | Workflow | Status | What can be checked here |
|---|---|---|---|
| 1 | Saved ranks → metrics | PASS | All 24 runs, 4,008 rows, Hits@1/5/10 and MRR; group means/sample SD |
| 2 | Saved embeddings → SVD/ranks/metrics | PARTIAL | Internal validation exists; embeddings and a self-contained executable retrieval package are not included |
| 3 | Saved descriptions → encoder/ranks/metrics | UNAVAILABLE | Requires permission-cleared descriptions, exact encoder resources and an executable pipeline |
| 4 | Raw profiles → prompts/LLM/encoder/retrieval | UNAVAILABLE | Requires upstream inputs, prompt dependencies, provider access and cleared outputs |

PARTIAL is not a runnable public workflow. A source listing does not establish functional reproduction. Level 1 tests only saved arithmetic results, not generation, semantic accuracy or ranking correctness from embeddings. No new hypothesis tests or confidence intervals are computed.

## Inputs and outputs

The rank CSV columns are `run_id,query_id,gold_target_id,gold_rank`. Q/T identifiers are opaque and consistent across runs; no original-ID reverse mapping is supplied. Gold ranks are integers in 1..167. These already saved evaluation labels are deliberately included for arithmetic verification; no raw test_links are opened.

S1 contains one row per completed run; S2 contains group summaries. Metrics are percentages on a 0–100 scale. A/B have three generation runs each; C/D each have three support selections × three generation runs. Support-selection seeds are not LLM generation seeds. Config records preserve the historical settings; referenced prompt files are not present and are not an executable promise.

The primary verifier outputs a PASS JSON, optionally to a caller-selected path. The independent verifier prints its own report. Both use Python 3.10+ standard library, no additional dependencies (see numerical_verification/requirements-verification.txt). Outputs must be written outside the frozen payload to preserve its exact inventory.
