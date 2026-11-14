"""Stage 3 frozen offline runtime. Historical inputs are read-only."""
from pathlib import Path
import sys,os,json,shutil,time,importlib.metadata,datetime as dt,unicodedata,re
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent
sys.path.insert(0,str(OLD/'scripts'))
import controlled as base

def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def write(p,obj):
    p=Path(p).resolve()
    if not p.is_relative_to(ROOT):raise ValueError('Output isolation violation')
    p.parent.mkdir(parents=True,exist_ok=True);data=base.jbytes(obj)
    if p.exists() and p.read_bytes()!=data:raise FileExistsError(str(p))
    if not p.exists():p.write_bytes(data)
def lines(p,items):
    p=Path(p);data=b''.join(base.jbytes(x) for x in items)
    if p.exists() and p.read_bytes()!=data:raise FileExistsError(str(p))
    p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():p.write_bytes(data)
def env():
    return {'python':sys.version,'executable':sys.executable,'dependencies':{k:importlib.metadata.version(k) for k in ['numpy','torch','transformers','sentence-transformers','tokenizers']},'device':'cpu','precision':'float32','threads':4,'batch_size':32,'max_seq_length':8192,'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'}
def load_encoder():
    os.environ.update({'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_MODULES_CACHE':str(ROOT/'runtime/hf_modules'),'TOKENIZERS_PARALLELISM':'false'})
    import torch
    torch.set_num_threads(4)
    p=base.PATCHED;sys.path.insert(0,str(p))
    # Preserve all local relative imports; old Transformers' recursive copier misses some.
    cache=ROOT/'runtime/hf_modules/transformers_modules'/p.name;cache.mkdir(parents=True,exist_ok=True)
    for init in [cache/'__init__.py',cache.parent/'__init__.py']:init.touch(exist_ok=True)
    for src in p.glob('*.py'):
        dest=cache/src.name
        if dest.exists() and base.sha(dest)!=base.sha(src):raise ValueError('Local model code cache differs')
        if not dest.exists():shutil.copyfile(src,dest)
    from sentence_transformers import SentenceTransformer
    m=SentenceTransformer(str(p),trust_remote_code=True,device='cpu');m.float();m.eval();m.max_seq_length=8192
    return m
def encode(m,texts):
    import numpy as np,torch
    from tokenizers import Tokenizer
    tok=Tokenizer.from_file(str(base.PATCHED/'tokenizer.json'));tok.no_truncation()
    counts=[len(tok.encode(t).ids) for t in texts]
    if max(counts)>8192:raise ValueError('Encoder truncation would occur')
    start=time.perf_counter()
    with torch.inference_mode():x=m.encode(texts,task='text-matching',batch_size=32,show_progress_bar=False,convert_to_numpy=True).astype(np.float32)
    if x.shape!=(len(texts),1024) or not np.isfinite(x).all():raise ValueError('Invalid embeddings')
    return x,counts,time.perf_counter()-start
def ordered_raw():
    ps={1:base.profiles(1),2:base.profiles(2)};pairs=base.pairs('test');ids=[];texts=[]
    for side in [1,2]:
        for i,pair in enumerate(pairs):
            e=pair[side-1];ids.append({'kg':side,'entity_id':e,'test_index':i});texts.append(ps[side][e]['profile'])
    return texts,ids
def rank_and_save(out,x,texts,ids,timing,scope):
    import numpy as np
    pair=base.pairs('test');expected=[s for s,t in pair]+[t for s,t in pair]
    if [v['entity_id'] for v in ids]!=expected:raise ValueError('Entity order mismatch')
    out.mkdir(parents=True,exist_ok=True)
    if (out/'embedding.npy').exists():raise FileExistsError('No embedding overwrite')
    np.save(out/'embedding.npy',x,allow_pickle=False)
    lines(out/'encoder_inputs.jsonl',[{**i,'text':t} for i,t in zip(ids,texts)]);write(out/'entity_order.json',ids)
    t=time.perf_counter();rows,metrics=base.rank_embeddings(x,[s for s,t in pair],[t for s,t in pair]);timing['svd_retrieval_seconds']=time.perf_counter()-t
    lines(out/'per_entity_ranks.jsonl',rows)
    result={'scope':scope,'metrics':metrics,'n_query':167,'n_candidates':167,'svd_fit_rows':334,'svd_dim':256,'direction':'KG1_to_KG2','csls_k':0,'tie_rule':'score descending, entity-ID ascending','environment':env(),'timing':timing,'embedding_sha256':base.sha(out/'embedding.npy')}
    write(out/'metrics.json',result);return result
def classify(text,finish):
    hard=[];soft=[]
    if not isinstance(text,str) or not text.strip():hard.append('empty_or_nontext')
    if finish!='stop':hard.append('incomplete_finish_reason:'+str(finish))
    if not isinstance(text,str):return hard,soft
    if len(text.split())>150:soft.append('word_count_gt150')
    if len([p for p in re.split(r'\n\s*\n',text.strip()) if p.strip()])!=1 or re.search(r'(?m)^\s*(?:[-*]|\d+\.)\s',text):soft.append('paragraph_format')
    if any(ord(c)>127 and unicodedata.category(c).startswith('L') for c in text):soft.append('non_ASCII_letters_language_proxy')
    return hard,soft
def freeze():
    original=base.read_json(OLD/'protocol.json')
    p={**original,'protocol_id':'doremus_controlled_v2_20261105','parent_protocol':str(OLD/'protocol.json'),'parent_protocol_sha256':base.sha(OLD/'protocol.json'),'created_date':'2026-11-05 Asia/Shanghai','validation':{'soft':['word_count_gt150','paragraph_format','non_ASCII_letters_language_proxy'],'hard':['empty/nontext','finish_reason_not_stop','HTTP/request/schema errors','entity/request identity mismatch'],'soft_policy':'retain original response; collapse whitespace only; do not regenerate/truncate/delete; report group violation rates','language_limit':'non-ASCII letters are a character-level proxy, not an accurate language classifier'},'retry_policy':{'max_backoff_retries':2,'max_attempts_per_logical_request':3,'retryable':'network errors, HTTP429, HTTP5xx only','backoff_seconds':[2,5],'stop_immediately':'HTTP400/401/403/other parameter/auth errors; empty/incomplete/schema/mapping issues; exhausted retries','selection':'first complete valid response; no selection by score'},'budget':{'limit_USD':15.0,'stop_threshold_conservative_USD':14.75,'includes':'all attempts, retries, unknown-charge reservations','rates_max_USD_per_1M':{'input_cache_miss':.3,'input_cache_hit':.006,'output':1.2},'rate_source':'https://api-docs.deepseek.com/quick_start/pricing/','rates_checked':'2026-11-05','ledger_method':'reserve worst-case UTF-8 bytes+4096 input tokens and1024 output tokens before each attempt; settle with peak-rate upper accounting for recorded usage; unresolved usage retains reserve','cost_truth':'derived usage-based conservative USD estimate, not verified account invoice','no_top_up':True,'no_model_change':True},'runtime_environment':env(),'raw_baseline':{'id':'RAW_PROFILE_ONLY_v2','preregistered_before_API':True,'inputs':'same normalized test profiles as prompt query input; no entity-name prefix','encoder_and_eval':'same frozen local Jina/task/SVD256/test167-candidate protocol','output':str(ROOT/'raw-profile-only'),'LLM_calls':0,'external_baseline_substitute':False},'pilot_gate':{'logical_requests':80,'no_pilot_MRR':True,'require':'smoke PASS;80 successful unique logical keys; no unresolved hard issues; saved model/usage/finish; stable returned model; total cost projection under15','auto_continue':True},'HTTP_logical_counts':{'planned_logical':8016,'pilot_is_subset':80,'HTTP_max_if_every_logical_retried_twice':24048,'actual_HTTP':'read attempt ledger, not8016 assumption'},'notes':'v2 supersedes validation/retry rules only; all registered prompts/supports/24 runs retained; no target historical92.19'}
    p['protocol_id']='doremus_controlled_v2.1_20261105'
    p['max_http_attempts']=3
    p['plan_artifact_hashes']={str(OLD/f):base.sha(OLD/f) for f in ['run_manifest.json','dry_run/schedule.jsonl','dry_run/support_sets.json']}
    for f in sorted((OLD/'dry_run').glob('prompts_*.jsonl')):p['plan_artifact_hashes'][str(f)]=base.sha(f)
    write(ROOT/'protocol_v2.json',p)
    write(ROOT/'raw_baseline_registration.json',p['raw_baseline'])
    manifest={str(q):base.sha(q) for q in sorted((ROOT/'scripts').glob('*.py'))}
    manifest[str(OLD/'scripts/controlled.py')]=base.sha(OLD/'scripts/controlled.py')
    manifest[str(ROOT/'protocol_v2.json')]=base.sha(ROOT/'protocol_v2.json')
    write(ROOT/'freeze_manifest.json',manifest)
    print('v2 frozen; no API calls')
def check():
    p=base.read_json(ROOT/'protocol_v2.json')
    for group in ['source_inputs','encoder_file_hashes','plan_artifact_hashes']:
        for f,h in p[group].items():
            if base.sha(Path(f))!=h:raise ValueError('Frozen input differs: '+f)
    for f,h in base.read_json(ROOT/'freeze_manifest.json').items():
        if base.sha(Path(f))!=h:raise ValueError('Frozen implementation differs: '+f)
    if env()!=p['runtime_environment']:raise ValueError('Runtime environment differs')
    return p
def smoke_and_raw():
    import numpy as np
    cfg=check();out=ROOT/'smoke-test';start=time.perf_counter();m=load_encoder();loadtime=time.perf_counter()-start
    short='A string quartet composed for two violins, viola and cello.'
    long=('The chamber composition has distinctive instrumentation, movement order, key and composer information. '*260)
    x,counts,elapsed=encode(m,[short,long]);np.save(out/'short_long_forward.npy',x,allow_pickle=False)
    write(out/'short_long_forward.json',{'counts':counts,'characters':[len(short),len(long)],'shape':list(x.shape),'dtype':str(x.dtype),'environment':env(),'model_load_seconds':loadtime,'forward_seconds':elapsed,'weights_loaded':True})
    manifest=base.PROJECT/'audit/sci_q2_revision_20260716_150534/03_result_provenance_v8_doremus_offline_reencoding/00_inputs/offline_reencoding_input_manifest.csv'
    import csv
    paths={r['role']:Path(r['path']) for r in csv.DictReader(manifest.open(encoding='utf-8-sig'))}
    pair=base.pairs('test');texts=[];ids=[]
    for side in [1,2]:
        rr=[l.split('\t',2) for l in paths[f'llm_kg{side}'].read_text().splitlines() if l.strip()]
        assert [r[1] for r in rr]==[p[side-1] for p in pair]
        for i,r in enumerate(rr):texts.append(base.clean_description(r[-1]));ids.append({'kg':side,'entity_id':r[1],'test_index':i})
    x,tokens,elapsed=encode(m,texts)
    hist=rank_and_save(out/'historical334',x,texts,ids,{'encoding_seconds':elapsed,'model_load_seconds':loadtime},'SMOKE_ONLY_NOT_CONTROLLED_RESULT')
    rawtexts,rawids=ordered_raw();x,counts,elapsed=encode(m,rawtexts)
    raw=rank_and_save(ROOT/'raw-profile-only',x,rawtexts,rawids,{'encoding_seconds':elapsed,'model_load_seconds':loadtime},'PREREGISTERED_RAW_PROFILE_ONLY')
    write(out/'completion.json',{'status':'PASS','historical_rows':334,'historical_metrics':hist['metrics'],'historical_reference_MRR':86.10197344406765,'reference_difference_pp':hist['metrics']['MRR']-86.10197344406765,'reference_difference_policy':'diagnostic only; new env may differ; not tuned to historical score','short_long_forward':True,'raw_baseline_complete':True,'raw_metrics':raw['metrics'],'elapsed_seconds':time.perf_counter()-start,'environment':env(),'API_calls':0})
    print('smoke PASS; raw baseline saved',flush=True)
if __name__=='__main__':
    if sys.argv[1]=='freeze':freeze()
    elif sys.argv[1]=='check':check();print('PASS')
    elif sys.argv[1]=='smoke':smoke_and_raw()
