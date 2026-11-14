# Real production source: availability status

The source identities below belong to the completed controlled experiment. Their bodies are **not in this upload payload**. They remain in a separate local rights-hold archive; no synthetic example or new replacement implementation is presented as production code.

| Module | Role |
|---|---|
| controlled.py | Support sampling/banks, prompt construction, generation interface/cache processing, SVD/rank arithmetic |
| pipeline.py | Frozen local encoder interface, encoding and rank-saving orchestration |
| execute_stage3.py | Request/cache orchestration |
| execute_stage3_v22.py | Bounded recovery and frozen-state checks |
| execute_stage3_v23.py | Final recovery orchestration, encoding and aggregation |
| network_v23.py | Connectivity diagnostics (not necessary for numerical reproduction) |
| report_stage3_v23.py | Saved-result reporting |

Historical execution evidence consists of frozen source bindings and completion/run artifacts; it is not a dynamic trace of every function. The seven source files were not executed in this preparation. Their layout and excluded resources do not form a standalone runnable method package. The legacy synthetic `prompt_context.py` and `repro_core.py` are not substituted for them.

Exact original and held-copy digests are listed below. Only controlled.py has a documented text transformation: two private path roots replaced by placeholders; the other six archives are byte-identical. Individual/institutional authorship and dependency permissions still need confirmation. Source archiving is not end-to-end reproducibility.

```json
[
  {
    "module": "controlled.py",
    "original_sha256": "ce3474a2f5a905a415c6867bfd13c672a17fea181a2d0fdca6e2b15b64998e73",
    "held_archive_sha256": "e1e9608e79af223ae90f816af0560b4ab95d7642ab8a91fc1099eb26b644dcc2",
    "status": "withheld pending author/institution rights confirmation"
  },
  {
    "module": "pipeline.py",
    "original_sha256": "6c99780effdc44edf1188b9278d24d5bd7ce77922e80f6872cbddf2e78211bd1",
    "held_archive_sha256": "6c99780effdc44edf1188b9278d24d5bd7ce77922e80f6872cbddf2e78211bd1",
    "status": "withheld pending author/institution rights confirmation"
  },
  {
    "module": "execute_stage3.py",
    "original_sha256": "08b038a3f0d42d7d97627321eb6ece8adeb34cbfc9a6f027f5b66b962fecfbb0",
    "held_archive_sha256": "08b038a3f0d42d7d97627321eb6ece8adeb34cbfc9a6f027f5b66b962fecfbb0",
    "status": "withheld pending author/institution rights confirmation"
  },
  {
    "module": "execute_stage3_v22.py",
    "original_sha256": "e4c44a11736d7f93d89197be8b5243fccd28dfe5d5c0ff27136a3105c8de8e3e",
    "held_archive_sha256": "e4c44a11736d7f93d89197be8b5243fccd28dfe5d5c0ff27136a3105c8de8e3e",
    "status": "withheld pending author/institution rights confirmation"
  },
  {
    "module": "execute_stage3_v23.py",
    "original_sha256": "2f57c5df4eca66af19b55fd28e98d3becd10491899f155f912799da356155498",
    "held_archive_sha256": "2f57c5df4eca66af19b55fd28e98d3becd10491899f155f912799da356155498",
    "status": "withheld pending author/institution rights confirmation"
  },
  {
    "module": "network_v23.py",
    "original_sha256": "65b4f3eb1f0f3611a4717704d96fd300b26e94a20bc0a4958a64aca3650a7bc7",
    "held_archive_sha256": "65b4f3eb1f0f3611a4717704d96fd300b26e94a20bc0a4958a64aca3650a7bc7",
    "status": "withheld pending author/institution rights confirmation"
  },
  {
    "module": "report_stage3_v23.py",
    "original_sha256": "a5bafb2110e8e10bff8d9a43927c90fac4ae0967f66da8b9e5b0ffeb490278e1",
    "held_archive_sha256": "a5bafb2110e8e10bff8d9a43927c90fac4ae0967f66da8b9e5b0ffeb490278e1",
    "status": "withheld pending author/institution rights confirmation"
  }
]
```
