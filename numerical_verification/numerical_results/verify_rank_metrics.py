"""Read-only numerical verification of saved FS LEA results; standard library."""
from pathlib import Path
from collections import defaultdict
import csv,hashlib,json,math
root=Path(__file__).resolve().parent
for name,digest in json.loads((root/'SHA256.json').read_text()).items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest, name
expected=json.loads((root/'expected_metrics.json').read_text())
grouped=defaultdict(list)
with (root/'controlled_per_query_ranks_pseudonymized.csv').open(newline='',encoding='utf-8') as f:
    for row in csv.DictReader(f):grouped[row['run_id']].append(row)
assert len(grouped)==len(expected)==24 and set(grouped)==set(expected)
gold=None
for run_id,rows in grouped.items():
    assert len(rows)==167
    mapping={x['query_id']:x['gold_target_id'] for x in rows}
    assert len(mapping)==len(set(mapping.values()))==167
    if gold is None:gold=mapping
    assert gold==mapping
    ranks=[int(x['gold_rank']) for x in rows]
    assert all(1<=r<=167 for r in ranks)
    observed={f'Hit@{k}':100*sum(r<=k for r in ranks)/167 for k in [1,5,10]}
    observed['MRR']=100*math.fsum(1/r for r in ranks)/167
    for name,value in observed.items():
        assert math.isclose(value,expected[run_id][name],rel_tol=0,abs_tol=1e-10),(run_id,name)
print('PASS: 24 runs, 4008 ranks, shared identities, four metrics, file digests.')
print('No experiment, model execution, significance test or network request performed.')
