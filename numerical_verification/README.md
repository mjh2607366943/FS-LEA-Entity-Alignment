# FS-LEA numerical review candidate

LOCAL CANDIDATE ONLY. Not publicly deposited or licensed for redistribution. Author/institution release approval and any derivative-data permission remain pending. No repository, DOI or journal acceptance is claimed.

This portable subset reuses existing anonymized rank derivatives and author-written numerical code. It contains all 24 completed DOREMUS runs, with 167 queries per run (4,008 rows). Opaque Q/T labels describe saved evaluation outcomes, not train/inference inputs or 4,008 independent statistical observations.

## Offline verification

Python 3.10+ standard library; no package installation, GPU, encoder, LLM, network, credentials or environment secrets are required.

    python -I -B verify_saved_results.py --output result.json
    python -I -B numerical_results/verify_rank_metrics.py

The first checker verifies file hashes, shared identities, every run's Hits@1/5/10 and MRR, and group means/sample SD. The second is a retained independent checker. Neither generates predictions, changes ranks, performs new significance tests, bootstraps intervals or confirms semantic correctness. Gold-target IDs are opaque evaluation labels already in the saved derivative, not original test_links.

## Reproduction scope

Saved ranks -> four metrics and summary statistics: supported. Saved embeddings -> ranking: NOT supported by this package. Raw graph/profile -> LLM generation -> encoding -> ranking: NOT supported. Real profiles, original entity IDs/mappings, complete prompts/responses, embeddings, upstream code and model weights are not included. config/scientific_config.json records settings; it is not a complete executable generation/retrieval environment. A/B zero-shot and C/D support/generation counts must not be mistaken for independent datasets. The existing structural comparator and historical results remain separate studies.

Author-written pipeline utilities and full source-inspection candidates remain in the separately indexed local archive pending permission/provenance review. The legacy synthetic prompt utility is not represented as the exact production serializer or used to regenerate results here.

## Rights and access

No blanket LICENSE is invented. Numerical derivatives, documentation and author code are intended for a permission-cleared reviewer delivery; this local preparation does not establish institutional ownership or an external access right. Third-party data, profiles, models and implementations must be obtained under their own terms. Authors must approve the exact file list and licence/access scope, arrange an allowed review channel, and test non-owner download plus SHA256 before claiming availability. Do not upload this candidate automatically.
