# FS-LEA: saved-result verification

FS-LEA studies training-derived entity context for description-based entity retrieval within the LEA framework. This V1 candidate provides numerical verification of the completed DOREMUS controlled experiment. It is not a runnable release of the full method.

## Start here

| Item | Location |
|---|---|
| Two numerical verifiers | [primary checker](numerical_verification/verify_saved_results.py), [independent checker](numerical_verification/numerical_results/verify_rank_metrics.py) |
| All 24 run results | [Supplemental Data S1](numerical_verification/numerical_results/Supplemental_Data_S1.csv) |
| Group means and sample SD | [Supplemental Data S2](numerical_verification/numerical_results/Supplemental_Data_S2.csv) |
| 4,008 saved, pseudonymized ranks | [rank CSV](numerical_verification/numerical_results/controlled_per_query_ranks_pseudonymized.csv) |
| Scientific settings and run identities | [scientific config](numerical_verification/config/scientific_config.json), [run manifest](config/RUN_MANIFEST.json) |
| Real method source status | [seven production modules, currently withheld](docs/METHOD_SOURCE_STATUS.md) |
| Test-link use and evaluation boundaries | [protocol note](docs/TEST_LINKS_USAGE.md) |
| Third-party inputs | [sources and restrictions](docs/THIRD_PARTY_RESOURCES.md) |
| Reproducibility scope | [levels and input/output schema](docs/REPRODUCIBILITY.md) |

## Verify offline

Python 3.10+ and its standard library suffice. No pip installation, network, credentials, GPU, encoder or LLM is needed. From this directory:

```bash
python3 -m venv --without-pip /tmp/fslea-verification-v1
/tmp/fslea-verification-v1/bin/python -I -B numerical_verification/verify_saved_results.py --output /tmp/fslea-verified-metrics.json
/tmp/fslea-verification-v1/bin/python -I -B numerical_verification/numerical_results/verify_rank_metrics.py
```

Choose an unused environment path if that path already exists. Both checkers must report PASS. The first verifies hashes, per-run Hits@1/5/10 and MRR, group means and sample SD (ddof=1). The second independently checks the saved ranks and metrics. They do not regenerate predictions or rerun significance tests.

## Scope

**Level 1 PASS; Level 2 PARTIAL (internal evidence only); Levels 3/4 UNAVAILABLE.** Only Level 1 is executable using this release. The ranks are evaluation derivatives, not training inputs; 4,008 rows are repeated observations of 167 queries, not independent datasets. The experiment has A/B: 3 runs each, C/D: 9 runs each. No result has been selected or changed.

Seven real production source modules were identified and checked locally, but are outside this repository pending author/institution rights confirmation. A static source archive would not itself reproduce the full pipeline. Benchmark files, original entity mappings, profiles, full prompts/responses, embeddings and weights are excluded.

This is a local distribution candidate, not evidence of an established public download channel. No blanket licence has been assigned. See [rights and scope](RIGHTS_AND_SCOPE.md). The numerical sub-bundle retains its original documentation and checksums unchanged; its references to local preparation are historical status notes, not new paper-approval requirements.
