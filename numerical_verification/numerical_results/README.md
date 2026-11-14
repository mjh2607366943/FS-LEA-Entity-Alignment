# Frozen FS LEA numerical results for review

This local reviewer-preview material contains all 24 controlled runs and 4,008 per-query gold ranks, with source and gold-target identifiers replaced consistently by opaque Q/T labels. No rank is changed or omitted. The identity mapping remains private and is not bundled. This is a data-format derivative of already completed results, not new generation, encoding, retrieval, training or significance testing.

Run with Python 3.10+ and the standard library only:

    python -I -B verify_rank_metrics.py

The check validates file hashes, 24 runs, 167 unique query/gold-target identities per run, a shared gold mapping, ranks in 1..167, and all four percentage metrics against retained full-precision results. It does not run bootstrap or select favorable outcomes. No environment variable, credential, network connection or third-party package is read. Original file digests permit a separately authorized holder to check source identity.

This bundle does NOT reproduce text generation, encoder inference, SVD or retrieval from benchmark inputs. It does not bind opaque identifiers back to original entities for an external reviewer. Complete implementation, benchmark access, cache and model provenance remain separate unresolved requirements. No public repository, DOI, blanket licence for third-party assets, or journal policy compliance is asserted. Preparation for local author/advisor review is authorized by the user; this file does not certify institutional ownership of legacy source code or publish any asset.
