# Test-link use in the controlled implementation

This note describes static inspection of `controlled.py::prepare` and `rank_embeddings`, and the saved-source call graph. The module bodies are not distributed here. It does not claim that test links were never read.

## Fixed membership and ordering

`prepare` loads train_links and test_links. The latter defines 167 source entities, 167 target candidates and a shared pair-row order; it checks unique identities. This is the fixed KG1→KG2 closed candidate protocol, not retrieval over every entity in KG2. Joint SVD is fit independently within each run on all 334 test-side embeddings, so test-entity visibility is transductive. Test-link membership/order also determines pilot enumeration and scheduling metadata; the recorded pilot had no evaluation-based selection.

## Support selection and prompts

Three supports are drawn only from train_links using `random.Random(seed).sample(train, 3)` with registered seeds 11/22/33. The selected pairs/source IDs/target IDs are checked against test sets by assertions. In this code, an overlap aborts preparation; there is no test-performance selection or rejection-resampling loop.

Each prompt is assembled from that entity's own name/profile plus the training-derived source/target support banks when applicable. C adds the correct mapping between training supports; D omits that declaration while retaining the same banks. A uses the legacy instruction. In the inspected assembly code, a test source's paired target profile or pair annotation is not inserted into its prompt as a demonstration. Pair-row index is request metadata, not a test-answer statement in the message. This finding concerns assembly logic; it does not certify upstream profile contents, pretraining data or all possible semantic overlap.

## Scoring and gold rank

`rank_embeddings` first computes joint SVD, row normalization and source–target inner products without using correct-pair identities as numerical features. Source and target arrays are in the shared test-link order. It sorts each candidate row by descending score, with exact ties broken by Unicode target-ID order (`np.lexsort((target, -row))`). The correct column for query i is then taken as column i, and its position in that sorted row gives gold_rank. This is an evaluation convention derived from paired ordering, not a rule that puts the correct entity first.

The historical implementation combines similarity computation and gold-rank reporting. It is therefore not a general gold-free prediction-only API. The pipeline checks entity order against test_links before calling this routine. Releasing only the saved pseudonymized ranks reproduces arithmetic metrics, not this retrieval computation.

## Interpretation

The evidence supports training-only support sampling and test-gold use for membership/order, overlap checking and evaluation. The inspected code does not show test pairings injected into training support or used to choose performance-favourable parameters. That is narrower than a universal no-leakage guarantee. It also rules out an inaccurate blanket statement that test labels were never read. No new predictions, ranks or metrics were generated for this source audit.
