#!/usr/bin/env python3
"""DOREMUS controlled protocol. prepare/check are offline; API requires explicit execute.

Never import historical request code. Credentials only from DEEPSEEK_API_KEY.
All writable paths must remain in this revision directory.
"""
import argparse, ast, collections, datetime as dt, hashlib, json, os, random, re, sys, time
from pathlib import Path

REV=Path(__file__).resolve().parents[1]
PROJECT=Path('<LEGACY_WORKSPACE>')
DATA=PROJECT/'data/standard/doremus_en'
OLD=Path('<ORIGINAL_LEA>')
PATCHED=PROJECT/'audit/sci_q2_revision_20260716_150534/03_result_provenance_v8_doremus_offline_reencoding/01_model_environment/patched_jina_embeddings_v3'
PARAMS={'model':'deepseek-flash','thinking':{'type':'disabled'},'temperature':0.3,'top_p':1,'max_tokens':1024,'frequency_penalty':0,'presence_penalty':0,'n':1,'stop':None,'stream':False}
SYSTEM='You are an intelligent assistant!'
STRUCTURED='''Task: produce a distinctive entity description for retrieval-based entity alignment.
Use the given profile and your knowledge. Preserve identity and useful attributes,
relations and neighbor information; omit repetitive or generic details.
Return one English paragraph of fewer than 150 words. Do not return candidate
alignments, explanations of the task, or facts copied from the demonstration entities.
If evidence is uncertain, do not invent specific facts.
{support}
ENTITY NAME:
{entity}
ENTITY PROFILE:
{profile}
DESCRIPTION:
'''
SET_SEEDS=[11,22,33]
def jbytes(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n').encode()
def digest(x):return hashlib.sha256(x).hexdigest()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read_json(p):return json.loads(p.read_text())
def writable(p):
    p=p.resolve()
    if not p.is_relative_to(REV):raise ValueError('Output outside revision directory')
    return p
def frozen_write(p,data):
    p=writable(p);p.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(data,str):data=data.encode()
    if p.exists():
        if p.read_bytes()!=data:raise RuntimeError('Frozen artifact differs: '+str(p))
    else:p.write_bytes(data)
def jsonl(p,rows):frozen_write(p,b''.join(jbytes(r) for r in rows))
def load_jsonl(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def pairs(part):
    p=DATA/f'721_5fold/1/{part}_links'
    return [tuple(l.split('\t')) for l in p.read_text().splitlines() if l.strip()]
def normalize_profile(s):
    # Decode only explicit serialization escapes; do not mojibake real Unicode.
    s=re.sub(r'\\u([0-9a-fA-F]{4})',lambda m:chr(int(m[1],16)),s)
    return s.replace('\\r\\n','\n').replace('\\n','\n').replace('\\t',' ').replace('\r\n','\n').replace('\r','\n').strip()
def profiles(side):
    p=DATA/f'output/attr_ngb_seq_{side}.txt';result={}
    for line in p.read_text().splitlines():
        fields=line.split('\t',2)
        if len(fields)!=3:raise ValueError('Profile not 3 columns: '+str(p))
        row_id,entity,raw=fields
        if entity in result:raise ValueError('Duplicate entity in profiles')
        result[entity]={'row_id':row_id,'entity_id':entity,'profile':normalize_profile(raw),'raw_profile_sha256':digest(raw.encode())}
    return result
def original_template():
    p=OLD/'lea_main.py';tree=ast.parse(p.read_text())
    found=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.JoinedStr) and any(isinstance(v,ast.Constant) and isinstance(v.value,str) and '**Input Format**' in v.value for v in node.values):
            assert all(isinstance(v,ast.Constant) or isinstance(v,ast.FormattedValue) and isinstance(v.value,ast.Name) and v.value.id=='entity' for v in node.values)
            found.append(''.join(v.value if isinstance(v,ast.Constant) else '{entity}' for v in node.values))
    if len(found)!=1:raise RuntimeError('Original local normal template not uniquely identified')
    return found[0],{'source':str(p),'sha256':sha(p),'provenance':'local original LEA normal branch; not proof of immutable published upstream commit'}
def banks(selected,p1,p2,seed):
    # Same two banks, same byte order in C and D. Independent shuffled target IDs.
    target_order=list(range(3));random.Random(seed+1000).shuffle(target_order)
    if target_order==list(range(3)):target_order=[1,2,0]
    block='DEMONSTRATION ENTITY INFORMATION (not candidate answers):\nSOURCE BANK:\n'
    for i,(s,t) in enumerate(selected):block+=f'[S{i+1}]\n{p1[s]["profile"]}\n'
    block+='TARGET BANK:\n'
    for i,j in enumerate(target_order):block+=f'[T{i+1}]\n{p2[selected[j][1]]["profile"]}\n'
    mapping=[f'S{i+1}=T{target_order.index(i)+1}' for i in range(3)]
    return block,mapping
def protocol():
    t,src=original_template()
    return {'protocol_id':'doremus_controlled_v1_20261104','dataset_dir':str(DATA),'source_inputs':{str(p):sha(p) for p in [DATA/'output/attr_ngb_seq_1.txt',DATA/'output/attr_ngb_seq_2.txt',DATA/'721_5fold/1/train_links',DATA/'721_5fold/1/test_links']},'api_parameters':PARAMS,'support_selection_seeds':SET_SEEDS,'generation_repeats':[1,2,3],'llm_generation_seed':None,'llm_generation_seed_note':'Not sent. Repeat ID is an independent call, not a provider RNG seed.','system':SYSTEM,'template_A':t,'template_A_source':src,'template_BCD':STRUCTURED,'postprocess':'collapse Unicode whitespace; description only; no entity prefix, raw concat, repair, truncation or selection','validation':'nonempty; no CJK; <150 whitespace words; finish_reason stop; flagged outputs retained, no repair calls','encoder':{'source':str(PATCHED),'task':'text-matching','max_seq_length':8192,'batch_size':32,'device':'cpu','revision':'local file hashes; not claiming upstream revision','mixed_precision':False},'evaluation':{'query':'fold1 test source entities in test_links order','candidates':'fold1 test target entities in test_links order','n_query':167,'n_candidates':167,'svd_fit':'joint all 167 generated source + 167 generated target embeddings, separately within each run','svd_dim':256,'l2_after_svd':True,'direction':'KG1_to_KG2','similarity':'inner product','csls_k':0,'tie_rule':'descending score, then ascending candidate entity ID (Unicode lexicographic)','metrics_scale':'0-100'},'design':{'zero_shot_runs':6,'few_shot_runs':18,'total_runs':24,'entities_per_run':334,'calls_without_retries':8016,'pilot_pairs':'first 5 test_links in fixed order','pilot_calls':80,'pilot_evaluation':False,'pilot_reuse':'same frozen r1 request keys only; never reuse across repeat IDs','schedule_seed':20261104},'provider_endpoint':'https://api.deepseek.com/chat/completions','timeout_seconds':120,'max_http_attempts':1,'notes':'No request retry, fallback or automatic quality repair. All attempts are retained; interrupted in-flight calls are not automatically replayed.'}
def prepare():
    cfg=protocol();train=pairs('train');test=pairs('test');p1,p2=profiles(1),profiles(2)
    cfg['encoder_file_hashes']={str(p):sha(p) for p in sorted(PATCHED.rglob('*')) if p.is_file() and p.suffix not in ['.pyc']}
    for sub in ['1_Pooling/config.json']:
        if (PATCHED/sub).is_file():cfg['encoder_file_hashes'][str(PATCHED/sub)]=sha(PATCHED/sub)
    assert len(test)==len(set(test))==167
    assert len({s for s,t in test})==len({t for s,t in test})==167
    frozen_write(REV/'protocol.json',jbytes(cfg))
    support=[];configs=[('A',None),('B',None)]
    for k,seed in enumerate(SET_SEEDS,1):
        chosen=random.Random(seed).sample(train,3)
        assert not set(chosen)&set(test)
        assert not {s for s,t in chosen}&{s for s,t in test}
        assert not {t for s,t in chosen}&{t for s,t in test}
        support.append({'set_id':f'S{k}','selection_seed':seed,'pairs':chosen,'all_in_train':all(x in train for x in chosen),'test_pair_overlap':0,'test_source_overlap':0,'test_target_overlap':0})
        configs.extend([('C',f'S{k}'),('D',f'S{k}')])
    frozen_write(REV/'dry_run/support_sets.json',jbytes(support))
    allprompts={};runlist=[];diffs=[]
    for group,setid in configs:
        key=group+('_'+setid if setid else '')
        shared='';mapping=[]
        if setid:
            selected=support[int(setid[1:])-1];shared,mapping=banks(selected['pairs'],p1,p2,selected['selection_seed'])
        prompts=[]
        for i,(s,t) in enumerate(test):
            for side,e,ps in [(1,s,p1),(2,t,p2)]:
                if e not in ps:raise ValueError('Missing profile '+e)
                if group=='A':user=cfg['template_A'].format(entity=e)+ps[e]['profile']
                else:
                    evidence=shared
                    if group=='C':evidence+='ALIGNMENT MAPPING:\n'+'; '.join(mapping)+'\n'
                    if group=='D':evidence+='ALIGNMENT MAPPING:\nNot supplied.\n'
                    user=STRUCTURED.format(support=evidence,entity=e,profile=ps[e]['profile'])
                messages=[{'role':'system','content':SYSTEM},{'role':'user','content':user}]
                rec={'prompt_id':f'{key}:KG{side}:{e}','config_id':key,'group':group,'support_set':setid,'support_selection_seed':None if setid is None else selected['selection_seed'],'test_index':i,'kg':side,'entity_id':e,'messages':messages,'messages_sha256':digest(jbytes(messages)),'normalized_profile_sha256':digest(ps[e]['profile'].encode())}
                prompts.append(rec);allprompts[rec['prompt_id']]=rec
        jsonl(REV/f'dry_run/prompts_{key}.jsonl',prompts)
        for repeat in [1,2,3]:
            runlist.append({'run_id':key+f'_r{repeat}','group':group,'support_set':setid,'support_selection_seed':None if setid is None else selected['selection_seed'],'generation_repeat':repeat,'llm_generation_seed':None,'prompt_file':f'dry_run/prompts_{key}.jsonl','expected_entities':334})
    # Assert C and D share everything except mapping content (not profile order).
    for sid in ['S1','S2','S3']:
        c=[v for v in allprompts.values() if v['config_id']=='C_'+sid];d=[v for v in allprompts.values() if v['config_id']=='D_'+sid]
        for x,y in zip(c,d):
            xc=x['messages'][1]['content'];yd=y['messages'][1]['content']
            xc=re.sub(r'ALIGNMENT MAPPING:\n[^\n]*\n','ALIGNMENT MAPPING:\n<MASKED>\n',xc)
            yd=re.sub(r'ALIGNMENT MAPPING:\n[^\n]*\n','ALIGNMENT MAPPING:\n<MASKED>\n',yd)
            assert xc==yd and x['entity_id']==y['entity_id']
        diffs.append({'support_set':sid,'paired_prompts_checked':334,'only_mapping_section_differs':True,'note':'Mapping text adds tokens; this is unavoidable treatment length, not equal token count.'})
    frozen_write(REV/'run_manifest.json',jbytes(runlist))
    schedule=[]
    for run in runlist:
        for p in load_jsonl(REV/run['prompt_file']):
            schedule.append({'request_key':run['run_id']+'::'+p['prompt_id'],'run_id':run['run_id'],'prompt_id':p['prompt_id'],'pilot':run['generation_repeat']==1 and p['test_index']<5})
    random.Random(cfg['design']['schedule_seed']).shuffle(schedule)
    jsonl(REV/'dry_run/schedule.jsonl',schedule)
    frozen_write(REV/'dry_run/prompt_diff_checks.json',jbytes(diffs))
    jsonl(REV/'dry_run/pilot_requests_NOT_SENT.jsonl',[{**item,'payload':{**cfg['api_parameters'],'messages':allprompts[item['prompt_id']]['messages']},'status':'DRY_RUN_NOT_SENT'} for item in schedule if item['pilot']])
    manifest={str(p.relative_to(REV)):sha(p) for p in sorted((REV/'dry_run').glob('*')) if p.is_file() and p.name!='sha256.json'}
    manifest.update({f:sha(REV/f) for f in ['protocol.json','run_manifest.json']})
    frozen_write(REV/'dry_run/sha256.json',jbytes(manifest))
    print(json.dumps({'unique_prompt_instances':len(allprompts),'runs':len(runlist),'planned_calls':len(schedule),'pilot_calls':sum(x['pilot'] for x in schedule),'online_calls':0}))
def check_lock():
    for f,h in read_json(REV/'dry_run/sha256.json').items():
        if sha(REV/f)!=h:raise RuntimeError('Frozen file modified: '+f)
    cfg=read_json(REV/'protocol.json')
    for f,h in cfg['source_inputs'].items():
        if sha(Path(f))!=h:raise RuntimeError('Source input changed: '+f)
    for f,h in cfg.get('encoder_file_hashes',{}).items():
        if sha(Path(f))!=h:raise RuntimeError('Encoder file changed: '+f)
    return cfg
def prompt_lookup():
    return {p['prompt_id']:p for f in sorted((REV/'dry_run').glob('prompts_*.jsonl')) for p in load_jsonl(f)}
def append(p,obj):
    p=writable(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('ab') as f:f.write(jbytes(obj));f.flush();os.fsync(f.fileno())
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def clean_description(s):return ' '.join(s.split())
def validate(content,finish):
    flags=[]
    if not content:flags.append('empty')
    if re.search('[\u3400-\u9fff]',content):flags.append('CJK')
    if len(content.split())>=150:flags.append('word_count_ge150')
    if finish!='stop':flags.append('finish_reason_'+str(finish))
    return flags
def execute(args):
    if not args.execute:raise SystemExit('No network enabled. Use prepare/check for offline dry-run.')
    cfg=check_lock()
    if not args.batch_id or not re.fullmatch('[A-Za-z0-9_-]+',args.batch_id):raise SystemExit('Explicit batch-id required')
    if not os.environ.get('DEEPSEEK_API_KEY'):raise SystemExit('DEEPSEEK_API_KEY environment variable is missing')
    batch=writable(REV/'runs'/args.batch_id);batch.mkdir(parents=True,exist_ok=True)
    lock=batch/'ACTIVE.lock'
    try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:raise SystemExit('Batch locked or interrupted; inspect events before recovery')
    os.close(fd)
    # Record safe environment only; never export credentials or request headers.
    frozen_write(batch/'batch_config.json',jbytes({'protocol_sha256':sha(REV/'protocol.json'),'runner_sha256':sha(Path(__file__)),'python':sys.version,'endpoint':cfg['provider_endpoint'],'source':'frozen plan','created_for_batch':args.batch_id}))
    try:
        completed={r['request_key'] for r in load_jsonl(batch/'responses.jsonl')} if (batch/'responses.jsonl').exists() else set()
        started={r['request_key'] for r in load_jsonl(batch/'requests.jsonl')} if (batch/'requests.jsonl').exists() else set()
        errors={r['request_key'] for r in load_jsonl(batch/'errors.jsonl')} if (batch/'errors.jsonl').exists() else set()
        # Do not silently replay an interrupted request or a failure.
        pending=started-completed-errors
        if pending:raise RuntimeError('Unresolved in-flight request; inspect before any replay')
        prompts=prompt_lookup();sent=0
        import urllib.request,urllib.error
        for item in load_jsonl(REV/'dry_run/schedule.jsonl'):
            if args.scope=='pilot' and not item['pilot']:continue
            if item['request_key'] in started:continue
            if args.max_requests is not None and sent>=args.max_requests:break
            p=prompts[item['prompt_id']];payload={**cfg['api_parameters'],'messages':p['messages']};t0=now()
            append(batch/'requests.jsonl',{**item,'started_at_utc':t0,'payload':payload,'payload_sha256':digest(jbytes(payload))})
            request=urllib.request.Request(cfg['provider_endpoint'],data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Authorization':'Bearer '+os.environ['DEEPSEEK_API_KEY'],'Content-Type':'application/json'},method='POST')
            raw=None;httpstatus=None
            try:
                with urllib.request.urlopen(request,timeout=cfg['timeout_seconds']) as resp:raw=resp.read();httpstatus=resp.status
                data=json.loads(raw);choice=data['choices'][0];content=choice['message'].get('content') or '';finish=choice.get('finish_reason');clean=clean_description(content);flags=validate(clean,finish)
                append(batch/'responses.jsonl',{**item,'started_at_utc':t0,'finished_at_utc':now(),'http_status':httpstatus,'requested_model':payload['model'],'response_model':data.get('model'),'usage':data.get('usage'),'response_id':data.get('id'),'provider_created':data.get('created'),'raw_response':data,'description':clean,'validation_flags':flags,'finish_reason':finish})
            except Exception as exc:
                # Preserve available response body, removing credentials if echoed.
                if isinstance(exc,urllib.error.HTTPError):
                    try:raw=exc.read()
                    except Exception:raw=None
                body=raw.decode('utf-8',errors='replace') if raw is not None else None
                if body is not None:
                    body=body.replace(os.environ['DEEPSEEK_API_KEY'],'[REDACTED]')
                    body=re.sub(r'\bsk-[A-Za-z0-9_-]{16,}|Bearer\s+[A-Za-z0-9._-]{16,}','[REDACTED]',body)
                append(batch/'errors.jsonl',{**item,'started_at_utc':t0,'finished_at_utc':now(),'error_type':type(exc).__name__,'http_status':getattr(exc,'code',httpstatus),'response_body_sanitized':body,'automatic_retry':False})
            started.add(item['request_key']);sent+=1;time.sleep(0.3)
        print(json.dumps({'new_requests':sent,'scope':args.scope,'batch':str(batch),'failures_retained':True}))
    finally:lock.unlink(missing_ok=True)
def response_texts(batch,run):
    cfg=check_lock();runrec=next(r for r in read_json(REV/'run_manifest.json') if r['run_id']==run)
    responses=load_jsonl(batch/'responses.jsonl');rs=[r for r in responses if r['run_id']==run]
    if len(rs)!=334 or len({r['prompt_id'] for r in rs})!=334:raise ValueError('Full 334-entity run required; no evaluation of partial pilot')
    if any(r['validation_flags'] for r in rs):raise ValueError('Flagged responses retained; complete-run metrics blocked pending protocol decision')
    models={r['response_model'] for r in rs}
    if len(models)!=1 or None in models:raise ValueError('Homogeneous saved response model ID required for formal run')
    if len({r['response_model'] for r in responses if r.get('response_model')})>1:raise ValueError('Batch spans backend model IDs; formal comparisons blocked')
    by={r['prompt_id']:r for r in rs};prompts=load_jsonl(REV/runrec['prompt_file']);texts=[];ids=[]
    # Explicit KG1 rows then KG2 rows; never rely on asynchronous response order.
    for side in [1,2]:
        for p in prompts:
            if p['kg']==side:
                texts.append(by[p['prompt_id']]['description']);ids.append({'kg':side,'entity_id':p['entity_id'],'test_index':p['test_index']})
    return cfg,texts,ids,next(iter(models))
def encode(args):
    import numpy as np
    import importlib.metadata
    batch=writable(REV/'runs'/args.batch_id);cfg,texts,ids,modelid=response_texts(batch,args.run_id)
    out=writable(batch/args.run_id);out.mkdir(exist_ok=True)
    if (out/'embedding.npy').exists():raise FileExistsError('Refusing to overwrite embedding')
    os.environ.update({'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_MODULES_CACHE':str(REV/'runtime/hf_modules'),'TOKENIZERS_PARALLELISM':'false'})
    modelpath=Path(cfg['encoder']['source']);sys.path.insert(0,str(modelpath))
    # Lazy import: prepare and request logging do not load the encoder.
    from sentence_transformers import SentenceTransformer
    from tokenizers import Tokenizer
    tokenizer=Tokenizer.from_file(str(modelpath/'tokenizer.json'));tokenizer.no_truncation()
    tokens=[len(tokenizer.encode(t).ids) for t in texts]
    if any(n>8192 for n in tokens):raise ValueError('Encoder truncation would occur; preserve texts and amend protocol first')
    enc=SentenceTransformer(str(modelpath),trust_remote_code=True,device=cfg['encoder']['device'])
    enc.max_seq_length=8192
    emb=enc.encode(texts,task='text-matching',batch_size=32,show_progress_bar=False).astype(np.float32)
    assert emb.shape==(334,1024) and np.isfinite(emb).all()
    np.save(out/'embedding.npy',emb,allow_pickle=False)
    jsonl(out/'encoder_inputs.jsonl',[{**i,'text':t,'encoder_token_count':n} for i,t,n in zip(ids,texts,tokens)])
    frozen_write(out/'entity_order.json',jbytes(ids))
    frozen_write(out/'encoding_config.json',jbytes({'encoder':cfg['encoder'],'response_model':modelid,'model_file_sha256':{str(p.relative_to(modelpath)):sha(p) for p in modelpath.iterdir() if p.is_file()},'embedding_sha256':sha(out/'embedding.npy'),'python':sys.version,'numpy':np.__version__,'dependency_versions':{name:importlib.metadata.version(name) for name in ['sentence-transformers','transformers','torch','numpy','tokenizers']}}))
    print('Encoded full run',args.run_id)
def rank_embeddings(x,source_ids,target_ids):
    import numpy as np
    assert x.shape[0]==334 and len(source_ids)==len(target_ids)==167
    if x.ndim!=2 or x.shape[1]<256 or not np.isfinite(x).all():raise ValueError('Bad embedding')
    u,s,_=np.linalg.svd(x,full_matrices=False);z=u[:,:256]*s[:256];norm=np.linalg.norm(z,axis=1,keepdims=True)
    if (norm==0).any():raise ValueError('Zero norm')
    z=z/norm;sim=z[:167]@z[167:].T;rows=[];target=np.array(target_ids)
    for i,row in enumerate(sim):
        order=np.lexsort((target,-row));rank=int(np.where(order==i)[0][0])+1
        rows.append({'source_entity_id':source_ids[i],'gold_target_id':target_ids[i],'gold_rank':rank,'top1_target_id':target_ids[int(order[0])],'gold_score':float(row[i])})
    r=np.array([t['gold_rank'] for t in rows]);metrics={**{f'Hit@{k}':float((r<=k).mean()*100) for k in [1,5,10]},'MRR':float((1/r).mean()*100)}
    return rows,metrics
def evaluate(args):
    import numpy as np
    batch=writable(REV/'runs'/args.batch_id);cfg,texts,ids,modelid=response_texts(batch,args.run_id);out=batch/args.run_id
    if read_json(out/'entity_order.json')!=ids:raise ValueError('Embedding entity order mismatch')
    ec=read_json(out/'encoding_config.json')
    if sha(out/'embedding.npy')!=ec['embedding_sha256']:raise ValueError('Embedding changed')
    test=pairs('test');assert [x['entity_id'] for x in ids]==[s for s,t in test]+[t for s,t in test]
    rows,metrics=rank_embeddings(np.load(out/'embedding.npy',allow_pickle=False),[s for s,t in test],[t for s,t in test])
    jsonl(out/'per_entity_ranks.jsonl',rows)
    frozen_write(out/'metrics.json',jbytes({'metrics':metrics,'evaluation':cfg['evaluation'],'response_model':modelid,'embedding_sha256':sha(out/'embedding.npy'),'protocol_sha256':sha(REV/'protocol.json'),'encoding_environment':{k:ec[k] for k in ['python','numpy','dependency_versions','encoder']},'evaluation_environment':{'python':sys.version,'numpy':np.__version__}}));print(metrics)
def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
    sub.add_parser('prepare');sub.add_parser('check')
    p=sub.add_parser('generate');p.add_argument('--execute',action='store_true');p.add_argument('--scope',choices=['pilot','full'],default='pilot');p.add_argument('--batch-id');p.add_argument('--max-requests',type=int)
    for command in ['encode','evaluate']:
        p=sub.add_parser(command);p.add_argument('--batch-id',required=True);p.add_argument('--run-id',required=True)
    args=ap.parse_args()
    if args.command=='prepare':prepare()
    elif args.command=='check':check_lock();print('Frozen protocol and inputs verified; no API calls')
    elif args.command=='generate':execute(args)
    elif args.command=='encode':encode(args)
    else:evaluate(args)
if __name__=='__main__':main()
