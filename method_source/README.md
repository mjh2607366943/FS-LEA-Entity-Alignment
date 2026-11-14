# FS-LEA historical method-core source candidate

**Historical source-reading supplement. The two method-core Python files are provided under the MIT License, Copyright (c) 2026 Jiahao Miao. Numerical-data licensing is separate; see the root rights and licence scope.**

This is a small historical source supplement to the existing saved-rank verification repository. It contains two real, previously used files, not a new or synthetic implementation. Their original and candidate hashes are in SOURCE_FILES.csv. No data, model weights, embeddings, complete prompts/responses or API records are included.

## Read the method

- [controlled.py](controlled_revision_20261104/scripts/controlled.py): `prepare` samples three training supports with seeds 11/22/33; `banks` builds the source/target profile banks and training mapping declaration; the structured instruction is stored in `STRUCTURED`. `rank_embeddings` performs run-specific joint SVD256, normalization, inner-product retrieval and Hits/MRR reporting for 167 queries × 167 candidates.
- [pipeline.py](controlled_revision_20261104/stage3_20261105/scripts/pipeline.py): `load_encoder`, `encode` and `rank_and_save` are the final stage3 encoder/ranking interfaces. They use a local Jina model snapshot/wrapper that is not bundled.

These files are method-core evidence, **not a standalone final v2.3 executor**. controlled.py also contains earlier v1 CLI/generation/validation functions. Publishing that file does not mean those older entry points generated every formal response. The final generation and cache orchestration was execute_stage3_v23.py, with earlier accepted caches spanning registered parent revisions. That executor and its recovery/reporting dependencies are deliberately omitted from this minimum bundle.

## Data and evaluation boundaries

The original code reads test_links to define fixed source/target members and paired order, perform overlap checks and report gold ranks. Training supports are sampled from train_links; selected overlap causes an assertion failure, not performance-based resampling. The inspected prompt assembly does not add the matched test entity as an alignment demonstration.

The score matrix itself uses embeddings, not pair labels as features. Gold position is taken from the shared pair-row order (column i for query i). Exact ties use descending score then Unicode target-ID order. This is not a general gold-free prediction-only API. Joint SVD on all 334 test-side embeddings is transductive. The candidate pool is the 167 fixed test targets, not all of KG2.

## What is missing / what not to run

Do not execute the historical entry points as an installation test. They expect frozen local layouts and protocol hashes, may write outputs, and generation paths can make paid provider requests when configured. No executable setup or new wrapper was invented here. Two private root strings in controlled.py were replaced by placeholders; all function ASTs are unchanged. pipeline.py is byte-identical. Renaming/redacting source is not proof of runtime reproducibility.

Read DEPENDENCIES.md before any separately authorized reconstruction. The external LEA A instruction is loaded from an excluded local file; it is not reproduced here. Standardized data/profile versions, exact encoder patches, accepted response caches, protocols and frozen-layout artifacts are absent or need permission.

## Reproducibility level

Adding these files improves source inspectability only. Existing saved-rank verification remains **Level 1 PASS**. **Level 2 PARTIAL (internal evidence; not executable from this bundle); Levels 3/4 UNAVAILABLE.** No numerical reproduction, model execution, LLM call or new experiment was performed to prepare this source increment.

## Upstream comparison

LEA was inspected at official commit c511638996d5f5317d6d29e5245025e420672f09. No explicit repository licence was found. A scoped comparison against 25 official Python files and two local historical LEA files found no exact whole-function or identifier-normalized whole-function copies; the original A instruction is an external dependency, not embedded text in these two files. Shared short strings include a generic system role, an API endpoint and configuration names. These observations support source distinction, not a legal guarantee of all ownership or a right to redistribute LEA itself. The author describes these files as self-developed FS-LEA research code. Jiahao Miao confirmed the original-source release and MIT grant; the grant does not include upstream LEA code/templates or excluded resources.
