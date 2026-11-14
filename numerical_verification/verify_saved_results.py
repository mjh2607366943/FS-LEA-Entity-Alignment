"""Arithmetic verification of previously saved ranks; no retrieval or hypothesis tests."""
from pathlib import Path
import argparse,csv,json,hashlib,math,statistics,collections
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--output',type=Path);a=p.parse_args();root=a.root.resolve()
for line in (root/'SHA256SUMS.txt').read_text().splitlines():
 digest,name=line.split('  ',1);f=(root/name).resolve();assert f.is_relative_to(root) and f.is_file();assert hashlib.sha256(f.read_bytes()).hexdigest()==digest,name
base=root/'numerical_results'
with (base/'controlled_per_query_ranks_pseudonymized.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
assert len(rows)==4008
runs=collections.defaultdict(list)
for row in rows:runs[row['run_id']].append(row)
with (base/'Supplemental_Data_S1.csv').open(encoding='utf-8-sig',newline='') as f:expected={x['run_id']:x for x in csv.DictReader(f)}
assert len(runs)==len(expected)==24 and set(runs)==set(expected)
results={};mapping=None
for run,rr in sorted(runs.items()):
 assert len(rr)==167
 mp={r['query_id']:r['gold_target_id'] for r in rr};assert len(mp)==len(set(mp.values()))==167
 if mapping is None:mapping=mp
 assert mp==mapping
 ranks=[int(r['gold_rank']) for r in rr];assert all(1<=r<=167 for r in ranks)
 m={'MRR':100*math.fsum(1/r for r in ranks)/167,**{f'Hit@{k}':100*sum(r<=k for r in ranks)/167 for k in [1,5,10]}}
 for key,val in m.items():assert abs(val-float(expected[run][key]))<1e-10,(run,key)
 results[run]=m
with (base/'Supplemental_Data_S2.csv').open(encoding='utf-8-sig',newline='') as f:groups=list(csv.DictReader(f))
for row in groups:
 rr=[m for run,m in results.items() if run.startswith(row['group']+'_')];assert len(rr)==int(row['n_runs'])
 for key in ['MRR','Hit@1','Hit@5','Hit@10']:
  vals=[r[key] for r in rr];assert abs(statistics.mean(vals)-float(row[key+'_mean']))<1e-10;assert abs(statistics.stdev(vals)-float(row[key+'_sd_ddof1']))<1e-10
out={'status':'PASS','runs':24,'saved_rank_rows':4008,'shared_queries':167,'groups':{'A':3,'B':3,'C':9,'D':9},'all_four_run_metrics_and_group_sample_SD_match':True,'raw_gold_read':False,'new_ranking_or_inference':False,'hypothesis_tests_rerun':False,'scope':'saved opaque ranks to arithmetic metrics only'}
text=json.dumps(out,indent=2)
if a.output:a.output.write_text(text+'\n')
print(text)
