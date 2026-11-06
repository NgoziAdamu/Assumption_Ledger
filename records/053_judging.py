"""Frozen step 5: repair, literal list assembly, three judges, preliminary statistics.

API code is imported from immutable 051 (Sol) and 050 (DeepSeek). No semantic
judgement is performed locally. Private artifacts only are used for statistics.
"""
import argparse
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime,timezone,timedelta
import hashlib
import importlib.util
import io
import inspect
import json
from pathlib import Path
import random
import re
import subprocess
import sys
import tarfile

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
PUB=ROOT/'records/053_judging'
OUT=ROOT/'data/053_judging_full'
PREREG='e904c4ca3bb858166376470e109e9d245b50f694'
PROMPTS=ROOT/'records/053_prompts'


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


F=module('immutable051_for053','records/051_formal_run.py')
P=module('immutable050_for053','records/050_pilot_run.py')
F.OUT=OUT;F.BUDGET=5
P.OUT=OUT;P.SECRETS=F.SECRETS
P.dump=F.dump;P.write=F.write;P.scrub=F.scrub;P.load=F.load;P.total_cost=F.total_cost
P.baseline=lambda task,kind,call:None
P.a049=lambda:F.A
original_stop=F.stop
def stop(reason,details=None):
    return original_stop(reason.replace('estimated_cost_exceeds_20_usd','estimated_cost_exceeds_5_usd'),details or {})
F.stop=stop;P.stop=stop
for _keypath in [Path.home()/'.openai_key',Path.home()/'.deepseek_key']:
    if _keypath.exists():
        _secret=_keypath.read_bytes().decode().strip()
        if _secret not in F.SECRETS:F.SECRETS.append(_secret)


def put(path,value):F.store(path,value)
def load(path):return F.load(path)
def now():return F.now()
def sha(data):return F.sha(data)


def freeze_check():
    audit=json.loads((PUB/'frozen_source_check.json').read_bytes())
    for path,meta in audit['files'].items():
        b=(ROOT/path).read_bytes();assert sha(b)==meta['sha256']
        assert subprocess.check_output(['git','show',PREREG+':'+path])==b
    F.freeze_check()
    remote=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip()
    assert subprocess.run(['git','merge-base','--is-ancestor',PREREG,remote]).returncode==0,'Prerequisite commit must be pushed before APIs.'


def prepare():
    OUT.mkdir(parents=True,exist_ok=True);freeze_check()
    put(OUT/'start_state.json',json.loads((PUB/'start_state.json').read_bytes()))
    put(OUT/'preregistration_commit.json',json.loads((PUB/'preregistration_commit.json').read_bytes()))
    for name in ['compact_blocks.json','excel_compact_validation.json','input_token_counts.csv','preparation_summary.json','selection.json']:
        src=ROOT/'data/052_formal_run_full'/name;dst=OUT/name
        if dst.exists():assert dst.read_bytes()==src.read_bytes()
        else:dst.write_bytes(src.read_bytes())
    F.load_prepared()
    protected={}
    for folder in ['050_pilot_full','051_formal_run_full','052_formal_run_full']:
        for p in (ROOT/'data'/folder).rglob('*'):
            if p.is_file():protected[str(p.relative_to(ROOT))]=sha(p.read_bytes())
    put(OUT/'protected_private_hashes.json',protected)
    put(OUT/'configuration.json',{'time':now(),'budget_usd':5,'budget_includes_repairs_and_all_judges':True,
        'sol_source_sha256':sha((ROOT/'records/051_formal_run.py').read_bytes()),
        'judge_source_sha256':sha((ROOT/'records/050_pilot_run.py').read_bytes()),
        'model':F.MODEL,'reasoning':{'effort':'medium','summary':'auto'},'max_output_tokens':32000,
        'judge_model':P.JUDGE,'judge_base_url':'https://api.deepseek.com','judge_parameters':'050 defaults unchanged',
        'old_files_edited':False,'API_calls_in_preparation':0})
    print(json.dumps({'event':'prepared','preregistration':PREREG,'protected_private_files':len(protected)}),flush=True)


def ensure_repair(record):
    if not (record['api_success'] and record['completed'] and record['parse_success'] and not record['truncated']):
        stop('repair_failed',{'tag':record['tag'],'status':record['status'],'parse_success':record['parse_success']})


def repair():
    freeze_check();F.load_prepared()
    for path in [Path.home()/'.openai_key',Path.home()/'.deepseek_key']:
        value=path.read_bytes().decode().strip()
        if value not in F.SECRETS:F.SECRETS.append(value)
    if (OUT/'repairs_complete.json').exists():return
    impl=F.call_api('impl-006','method2',F.assembled('impl-006',method2=True));ensure_repair(impl)
    task='biomedical-easy-2';folder=OUT/'repairs'/task;folder.mkdir(parents=True,exist_ok=True)
    old=ROOT/'data/052_formal_run_full/calls/biomedical-easy-2_method1_1/record.json'
    record=load(old);assert record['api_success'] and record['parse_success']
    value=F.parsed_value(record);ledger,issues,fewer=F.ledger_additions(value,1)
    if issues:stop('repair_seed_schema_failed',{'issues':issues})
    put(folder/'reused_call_1.json',{'source':str(old.relative_to(ROOT)),'record_sha256':sha(old.read_bytes()),'new_API_call':False})
    put(folder/'ledger_after_call_1.json',ledger)
    rerun=[]
    for c in F.A.manifest(task)['calls']:
        if c['kind']!='regular' or c['call']<2:continue
        number=c['call'];put(folder/f'ledger_before_call_{number}.json',ledger)
        try:prompt=F.assembled(task,number,ledger=load(folder/f'ledger_before_call_{number}.json'))
        except Exception as e:stop('repair_input_assembly_failed',{'call':number,'type':type(e).__name__,'message':str(e)})
        record=F.call_api(task,'method1',prompt,call_number=number);ensure_repair(record)
        added,issues,fewer=F.ledger_additions(F.parsed_value(record),number)
        if issues:stop('repair_schema_failed',{'tag':record['tag'],'issues':issues})
        ledger.extend(added);put(folder/f'ledger_after_call_{number}.json',ledger)
        put(folder/f'fewer_call_{number}.json',{'call':number,'fewer':fewer});rerun.append(record['tag'])
    put(folder/'ledger_all.json',ledger)
    final=F.call_api(task,'method1_final',F.assembled(task,final_rank=True,ledger=load(folder/'ledger_all.json')));ensure_repair(final)
    put(OUT/'repairs_complete.json',{'time':now(),'impl006_method2':impl['tag'],'biomedical_reused_call_1':str(old.relative_to(ROOT)),
        'biomedical_rerun_reviews':rerun,'biomedical_final_rank':final['tag'],'biomedical_method2':'Unchanged original 052 method2',
        'old_failure_records_preserved':True,'estimated_task_usd_so_far':F.total_cost()})
    print(json.dumps({'event':'repairs_complete','new_calls':len(rerun)+2,'estimated_usd':F.total_cost()}),flush=True)


def points():
    with (ROOT/'records/047_premise_sentences_draft.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==119 and len({int(r['序号']) for r in rows})==119
    for r in rows:
        r['seq']=int(r['序号']);r['object']=r['对象编号']
        r['task']=r['object'].split('_',1)[0] if r['benchmark']=='DAComp' else r['object']
        r['table']=re.sub(r'^impl-\d{3}_','',r['object'])
    assert len({r['object'] for r in rows})==79 and len({r['task'] for r in rows})==29
    return rows


def base(task):
    first=load(ROOT/'data/051_formal_run_full/selection.json')['first']
    return ROOT/('data/051_formal_run_full' if task in first else 'data/052_formal_run_full')


def final_sources(task,method):
    root=OUT if (task=='impl-006' and method=='method2') or (task=='biomedical-easy-2' and method=='method1') else base(task)
    kind='method1_final' if method=='method1' else 'method2'
    record=load(root/'calls'/f'{task}_{kind}/record.json');value=F.parsed_value(record)
    ledger=load(OUT/'repairs'/task/'ledger_all.json') if task=='biomedical-easy-2' and method=='method1' else load(base(task)/'tasks'/task/'ledger_all.json')
    return record,value,ledger


def normalized(key):
    name=key.strip().rsplit('/',1)[-1]
    if name.endswith('.sql'):name=name[:-4]
    return name.rsplit('.',1)[-1].lower()


def without_importance(item):
    return {k:v for k,v in item.items() if k!='importance'} if isinstance(item,dict) else item


def numbered(items):
    return [{'rank':i,'item':without_importance(item)} for i,item in enumerate(items,1)]


def template(name,values):
    path=PROMPTS/name if name=='judge_match_group.txt' else ROOT/'records/049_prompts'/name
    text=path.read_bytes().decode()
    return re.sub(r'\{(table|premise|truth|items|group_items|agent_text)\}',lambda m:str(values[m[1]]),text)


def agent_text(task):
    # The original extractor singled out impl-025 because 050 had only two
    # tasks. Expand only that benchmark dispatch; all lexical rules are reused.
    source=inspect.getsource(P.extract_agent_text)
    source=source.replace("if task=='impl-025':","if m['benchmark']=='DAComp':",1)
    namespace=dict(P.__dict__)
    exec(compile(source,'<050 extractor with benchmark dispatch for 053>','exec'),namespace)
    return namespace['extract_agent_text'](task)


def assemble():
    freeze_check();assert (OUT/'repairs_complete.json').exists(),'Repairs must succeed before downstream steps.'
    rows=points();objects=list(dict.fromkeys(r['object'] for r in rows));tasks=list(dict.fromkeys(r['task'] for r in rows))
    delivered=defaultdict(list)
    with tarfile.open(ROOT/'traces/dacomp_deimpl_prev.tar.gz','r:gz') as tar:
        for member in tar:
            if not member.isfile() or not member.name.endswith('.sql'):continue
            for task in tasks:
                if not task.startswith('impl-'):continue
                prefix=f'dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent/dacomp-de-{task}/sql/'
                if member.name.startswith(prefix):delivered[task].append({'member':member.name,'name':Path(member.name).name[:-4].lower()})
    put(OUT/'points.json',rows);put(OUT/'delivered_sql_files.json',dict(delivered))
    lists=[];groups=[];issues=[];provenance=[]
    for task in tasks:
        m=F.A.manifest(task);contract={s['name'] for s in m['sections']} if m['benchmark']=='DAComp' else set()
        single_names=contract|{s['name'] for s in delivered[task]}
        targets=[next(r for r in rows if r['object']==obj) for obj in objects if next(r for r in rows if r['object']==obj)['task']==task]
        for method in ['method1','method2']:
            record,value,ledger=final_sources(task,method);by_id={r['id']:r for r in ledger}
            provenance.append({'task':task,'method':method,'final_record_path':str((ROOT/record['parse_path']).with_name('record.json').relative_to(ROOT)),
                'parse_path':record['parse_path'],'parse_sha256':sha((ROOT/record['parse_path']).read_bytes())})
            buckets=defaultdict(list);group_entries=[];group_keys=[];keymap=[];bad=[]
            if not isinstance(value,dict):bad.append({'kind':'final_root_not_object'})
            else:
                for key,body in value.items():
                    entries=body if method=='method1' else body.get('items') if isinstance(body,dict) else None
                    if not isinstance(entries,list):bad.append({'kind':'items_not_list','key':key});continue
                    resolved=[]
                    for pos,entry in enumerate(entries,1):
                        if method=='method1':
                            identity=entry.get('id') if isinstance(entry,dict) else None
                            if not isinstance(identity,str) or identity not in by_id:bad.append({'kind':'unknown_ledger_id','key':key,'position':pos,'id':identity});continue
                            resolved.append(by_id[identity])
                        else:resolved.append(entry)
                    nk=normalized(key);single=nk in single_names
                    keymap.append({'original_key':key,'normalized_key':nk,'single_table':single if m['benchmark']=='DAComp' else None,'raw_count':len(entries),'resolved_count':len(resolved)})
                    if m['benchmark']=='DAComp':
                        if single:buckets[nk].append({'key':key,'items':resolved})
                        else:
                            group_keys.append({'key':key,'normalized_key':nk,'count':len(resolved)})
                            for item in resolved:group_entries.append({'group':key,'item':without_importance(item)})
                    else:buckets[key].append({'key':key,'items':resolved})
            issues.extend({'task':task,'method':method,**b} for b in bad)
            for t in targets:
                if m['benchmark']=='DAComp':
                    selected=buckets.get(t['table'],[]);keys=[b['key'] for b in selected];items=[item for b in selected for item in b['items']][:10]
                    status='unavailable_format' if bad else ('listed' if keys else 'not_listed')
                else:
                    keys=list(value) if isinstance(value,dict) else [];collected=[];invalid=[]
                    for ki,key in enumerate(keys):
                        for ri,item in enumerate(buckets.get(key,[{'items':[]}])[0]['items']):
                            importance=item.get('importance') if isinstance(item,dict) else None
                            if not isinstance(importance,(int,float)) or isinstance(importance,bool):invalid.append({'key':key,'position':ri+1})
                            else:collected.append((-importance,ki,ri,item))
                    if len(keys)==1:items=buckets.get(keys[0],[{'items':[]}])[0]['items']
                    else:items=[r[3] for r in sorted(collected,key=lambda r:r[:3])[:10]]
                    status='unavailable_format' if bad or (len(keys)>1 and invalid) else ('listed' if keys else 'not_listed')
                    if invalid:issues.append({'task':task,'method':method,'kind':'invalid_importance','entries':invalid})
                lists.append({'task':task,'object':t['object'],'table':t['table'],'benchmark':t['benchmark'],'method':method,
                    'status':status,'keys':keys,'count':len(items) if status!='unavailable_format' else None,
                    'items':numbered(items),'raw_items_with_importance':items,'key_mapping':keymap})
            rendered=[]
            for i,entry in enumerate(group_entries,1):
                entry['position']=i
                rendered.append('Group: '+entry['group']+'\n'+json.dumps({'position':i,'item':entry['item']},ensure_ascii=False,indent=2)+'\n')
            groups.append({'task':task,'method':method,'applicable':m['benchmark']=='DAComp','keys':group_keys,'items':group_entries,
                'text':'\n'.join(rendered),'count':len(group_entries),'status':'unavailable_format' if bad else 'available'})
        agent_text(task)
    put(OUT/'main_lists.json',lists);put(OUT/'group_lists.json',groups);put(OUT/'list_issues.json',issues);put(OUT/'list_provenance.json',provenance)
    put(OUT/'assembly_complete.json',{'time':now(),'points':119,'objects':79,'tasks':29,'main_list_records':len(lists),
        'group_key_counts':{method:sum(len(g['keys']) for g in groups if g['method']==method) for method in ['method1','method2']},
        'issues':issues,'normalization':'strip; last / component; remove final literal .sql; last . component; lowercase',
        'delivered_sql_source':'traces/dacomp_deimpl_prev.tar.gz; selected batch; agent/dacomp-de-impl-NNN/sql recursively; filenames only'})
    print(json.dumps({'event':'lists_assembled','main_lists':len(lists),'issues':len(issues),'group_counts':{k:sum(len(g['keys']) for g in groups if g['method']==k) for k in ['method1','method2']}},ensure_ascii=False),flush=True)


def judge():
    freeze_check();assert (OUT/'assembly_complete.json').exists()
    lists={(x['object'],x['method']):x for x in load(OUT/'main_lists.json')}
    groups={(x['task'],x['method']):x for x in load(OUT/'group_lists.json')};results=[]
    def one_point(point):
        values={'table':point['table'],'premise':point['agent默认的前提'],'truth':point['实际要求或数据情况']}
        for method in ['method1','method2']:
            main=lists[(point['object'],method)];group=groups[(point['task'],method)]
            entry={'seq':point['seq'],'point_id':point['point_id'],'task':point['task'],'object':point['object'],'table':point['table'],
                   'method':method,'kind':'judge_match','called':False,'source_status':main['status']}
            if main['status']=='not_listed':entry['result']={'verdict':'no_match','rank':None,'quote':None,'reason':'未列出'};entry['auto_reason']='未列出'
            elif main['status']!='listed':entry['result']=None;entry['technical_status']='unavailable_list_format'
            else:
                prompt=template('judge_match.txt',{**values,'items':json.dumps(main['items'],ensure_ascii=False,indent=2)})
                record=P.call_api(point['task'],'judge_match',prompt,point_id=point['seq'],method=method)
                entry.update(called=True,tag=record['tag'],parse_success=record['parse_success'],result=F.parsed_value(record))
            results.append(entry);put(OUT/'judge_results'/f'{point["seq"]}_{method}_main.json',entry)
            entry={'seq':point['seq'],'point_id':point['point_id'],'task':point['task'],'object':point['object'],'table':point['table'],
                   'method':method,'kind':'judge_match_group','called':False,'source_status':group['status']}
            if not group['applicable']:entry.update(result=None,not_applicable='KramaBench')
            elif not group['keys']:entry.update(result=None,not_applicable='no_group_keys')
            elif group['status']!='available':entry.update(result=None,technical_status='unavailable_group_format')
            else:
                prompt=template('judge_match_group.txt',{**values,'group_items':group['text']})
                record=P.call_api(point['task'],'judge_match_group',prompt,point_id=point['seq'],method=method)
                entry.update(called=True,tag=record['tag'],parse_success=record['parse_success'],result=F.parsed_value(record))
            results.append(entry);put(OUT/'judge_results'/f'{point["seq"]}_{method}_group.json',entry)
        text=load(OUT/point['task']/'agent_text.json')['text']
        prompt=template('judge_stated.txt',{**values,'agent_text':text})
        record=P.call_api(point['task'],'judge_stated',prompt,point_id=point['seq'])
        entry={'seq':point['seq'],'point_id':point['point_id'],'task':point['task'],'object':point['object'],'table':point['table'],
               'method':None,'kind':'judge_stated','called':True,'tag':record['tag'],'parse_success':record['parse_success'],'result':F.parsed_value(record)}
        results.append(entry);put(OUT/'judge_results'/f'{point["seq"]}_stated.json',entry)
        print(json.dumps({'event':'point_judges_complete','seq':point['seq'],'estimated_usd':F.total_cost()}),flush=True)
    # Each worker owns one point and its unique call tags. Individual request,
    # retry and parsing functions remain the immutable 050 implementation.
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(one_point,load(OUT/'points.json')))
    results.sort(key=lambda r:(r['seq'],['judge_match','judge_match_group','judge_stated'].index(r['kind']),r['method'] or ''))
    put(OUT/'all_judge_results.json',results)
    put(OUT/'judging_complete.json',{'time':now(),'known_points':119,'logical_results':len(results),'called':sum(r['called'] for r in results),'estimated_usd':F.total_cost()})


COLLAPSED={87,88,89,90,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107}
METHODS=['method1','method2']


def csv_out(path,rows,fields=None):
    rows=list(rows);fields=fields or list(rows[0])
    buf=io.StringIO(newline='');writer=csv.DictWriter(buf,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    F.write(path,buf.getvalue())


def norm(text):return re.sub(r'\s+',' ',text).strip()


def serialized_list_element(items,index):
    """Return the exact JSON substring supplied for this element in the request."""
    text=json.dumps(items,ensure_ascii=False,indent=2);decoder=json.JSONDecoder();position=1
    for i in range(len(items)):
        while text[position].isspace() or text[position]==',':position+=1
        _,end=decoder.raw_decode(text,position)
        if i==index:return text[position:end]
        position=end
    raise IndexError(index)


def quote_audit(results):
    mains={(r['object'],r['method']):r for r in load(OUT/'main_lists.json')}
    groups={(r['task'],r['method']):r for r in load(OUT/'group_lists.json')};audits=[]
    for entry in results:
        value=entry.get('result');value=value if isinstance(value,dict) else {}
        quote=value.get('quote');selector=None;selected=None;issue=None
        if entry['kind']=='judge_stated':
            selected=load(OUT/entry['task']/'agent_text.json')['text']
        elif entry['kind']=='judge_match':
            selector=value.get('rank');items=mains[(entry['object'],entry['method'])]['items']
            if isinstance(selector,int) and not isinstance(selector,bool) and 1<=selector<=len(items):selected=items[selector-1]
            else:issue='rank_missing_or_out_of_range'
        else:
            selector=value.get('position');items=groups[(entry['task'],entry['method'])]['items']
            if isinstance(selector,int) and not isinstance(selector,bool) and 1<=selector<=len(items):selected=items[selector-1]
            else:issue='position_missing_or_out_of_range'
        applicable=bool(quote) and isinstance(quote,str)
        if selected is None:haystacks=[]
        elif isinstance(selected,str):haystacks=[selected]
        else:
            haystacks=[json.dumps(selected,ensure_ascii=False,indent=2),*(text for _,text in P.string_leaves(selected))]
            if entry['kind']=='judge_match':haystacks.append(serialized_list_element(mains[(entry['object'],entry['method'])]['items'],selector-1))
            if entry['kind']=='judge_match_group':haystacks.append('Group: '+selected['group']+'\n'+json.dumps({'position':selector,'item':selected['item']},ensure_ascii=False,indent=2))
        exact=any(quote in h for h in haystacks) if applicable else None
        whitespace=any(norm(quote) in norm(h) for h in haystacks) if applicable else None
        if value.get('verdict')=='match' and not applicable:issue='match_without_nonempty_quote'
        audits.append({'seq':entry['seq'],'object':entry['object'],'task':entry['task'],'method':entry['method'],'kind':entry['kind'],
            'called':entry['called'],'verdict':value.get('verdict'),'selector':selector,'quote':quote,
            'quote_provided':applicable,'exact':exact,'whitespace_collapsed':whitespace,
            'issue':issue if applicable or value.get('verdict')=='match' else None,
            'basis':'selected item only, serialized JSON or a decoded string field; stated: extracted agent text only'})
    return audits


def percentile(values,q):
    v=sorted(values);index=(len(v)-1)*q;lo=int(index);hi=min(lo+1,len(v)-1)
    return v[lo]+(v[hi]-v[lo])*(index-lo)


def bootstrap_summary(rows,metric,scope,draw_scope='all29'):
    # Missing judge results are not converted into a verdict; report bounds instead.
    selected=[r for r in rows if scope!='exclude_impl030' or r['task']!='impl-030']
    weighted=scope!='unmerged119';tasks=sorted({r['task'] for r in rows})
    if draw_scope=='filtered28':tasks=[t for t in tasks if t!='impl-030']
    denom=defaultdict(float);numer={m:defaultdict(float) for m in METHODS};missing={m:[] for m in METHODS}
    for row in selected:
        w=1/20 if weighted and row['seq'] in COLLAPSED else 1
        denom[row['task']]+=w
        for method in METHODS:
            value=row[method][metric]
            if value is None:missing[method].append(row['seq'])
            else:numer[method][row['task']]+=w*value
    d=sum(denom.values());totals={m:sum(numer[m].values()) for m in METHODS}
    result={'scope':scope,'draw_scope':draw_scope,'points':len(selected),'units':round(d,12),'bootstrap_iterations':10000,
        'seed':1234,'percentile_method':'linear interpolation at (n-1)*q','missing_judge_points':missing}
    if any(missing.values()):
        for m in METHODS:
            missing_weight=sum((1/20 if weighted and r['seq'] in COLLAPSED else 1) for r in selected if r['seq'] in missing[m])
            result[m]={'found_units_known':totals[m],'rate':None,'lower_bound':totals[m]/d,'upper_bound':(totals[m]+missing_weight)/d}
        result['difference']={'rate':None,'CI95':None};return result
    for m in METHODS:result[m]={'found_units':totals[m],'rate':totals[m]/d}
    result['difference']={'rate':(totals['method1']-totals['method2'])/d}
    rng=random.Random(1234);samples={m:[] for m in METHODS};diff=[]
    for _ in range(10000):
        draw=rng.choices(tasks,k=len(tasks));dd=sum(denom[t] for t in draw)
        if not dd:raise ValueError('Empty bootstrap denominator; no implicit exclusion rule allowed')
        rates={m:sum(numer[m][t] for t in draw)/dd for m in METHODS}
        for m in METHODS:samples[m].append(rates[m])
        diff.append(rates['method1']-rates['method2'])
    for m in METHODS:result[m]['CI95']=[percentile(samples[m],.025),percentile(samples[m],.975)]
    result['difference']['CI95']=[percentile(diff,.025),percentile(diff,.975)]
    return result


def call_summary(record):
    return {'tag':record['tag'],'task':record['task'],'kind':record['kind'],'call':record.get('call'),'point_id':record.get('point_id'),
        'method':record.get('method'),'provider':record['provider'],'started_at':record['started_at'],'finished_at':record['finished_at'],
        'api_success':record['api_success'],'completed':record['completed'],'parse_success':record['parse_success'],
        'status':record['status'],'truncated':record['truncated'],'attempts':len(record['attempts']),
        **{k:record['usage'].get(k) for k in ['input_tokens','cached_input_tokens','output_tokens','reasoning_tokens']},
        'cached_input_fraction':record.get('cached_input_fraction'),'prompt_o200k_tokens':record['prompt_o200k_tokens'],
        'actual_input_to_current_o200k_ratio':record.get('actual_input_to_current_o200k_ratio'),
        'estimated_usd':record['cost']['estimated_usd'],'long_input_price_unverified':record['cost']['long_input_price_unverified'],
        'reasoning_summary_present':record['has_reasoning_summary_text'],'billing_uncertainty':record.get('billing_uncertainty')}


def cost_tables():
    rows=[];objects=load(OUT/'main_lists.json')
    for task in sorted({x['task'] for x in objects}):
        folder=base(task);original=[load(p) for p in (folder/'calls').glob(task+'_*/record.json')]
        count=len({x['object'] for x in objects if x['task']==task})
        for method in METHODS:
            old=[r for r in original if (r['kind'] in ['method1','method1_final'] if method=='method1' else r['kind']=='method2')]
            effective=old[:]
            if task=='impl-006' and method=='method2':effective=[load(OUT/'calls/impl-006_method2/record.json')]
            if task=='biomedical-easy-2' and method=='method1':
                effective=[r for r in old if r['kind']=='method1' and r.get('call')==1]
                effective.extend(load(p) for p in (OUT/'calls').glob('biomedical-easy-2_method1*/record.json'))
            new=[load(p) for p in (OUT/'calls').glob(task+'_*/record.json')]
            new=[r for r in new if (r['kind'] in ['method1','method1_final'] if method=='method1' else r['kind']=='method2')]
            effective_cost=sum(r['cost']['estimated_usd'] or 0 for r in effective)
            incurred=sum(r['cost']['estimated_usd'] or 0 for r in old+new)
            rows.append({'task':task,'method':method,'objects':count,'effective_path_usd':effective_cost,
                'effective_path_per_object_usd':effective_cost/count,'all_incurred_usd':incurred,'all_incurred_per_object_usd':incurred/count,
                'effective_call_tags':[r['tag'] for r in effective],'original_path':str(folder.relative_to(ROOT))})
    return rows


def statistics():
    assert (OUT/'judging_complete.json').exists(),'Complete all judges before preliminary statistics'
    results=load(OUT/'all_judge_results.json');audits=quote_audit(results);put(OUT/'quote_audit.json',audits)
    lookup={(r['seq'],r['method'],r['kind']):r for r in results};rows=[];issues=[]
    for point in load(OUT/'points.json'):
        row=dict(point)
        for method in METHODS:
            main=lookup[(point['seq'],method,'judge_match')];group=lookup[(point['seq'],method,'judge_match_group')]
            mv=main.get('result');gv=group.get('result');mv=mv if isinstance(mv,dict) else {};gv=gv if isinstance(gv,dict) else {}
            verdict=mv.get('verdict');rank=mv.get('rank');valid=verdict in ['match','no_match','unsure']
            rank_valid=isinstance(rank,int) and not isinstance(rank,bool) and rank>=1
            if verdict=='match' and not rank_valid:valid=False
            group_valid=gv.get('verdict') in ['match','no_match','unsure'] or bool(group.get('not_applicable'))
            if not valid or not group_valid:issues.append({'seq':point['seq'],'method':method,'main_valid':valid,'group_valid':group_valid})
            found10=(verdict=='match' and rank<=10) if valid else None
            found5=(verdict=='match' and rank<=5) if valid else None
            supplemental=(verdict=='match' or gv.get('verdict')=='match') if valid and group_valid else (True if verdict=='match' or gv.get('verdict')=='match' else None)
            row[method]={'main_verdict':verdict,'rank':rank,'main10':found10,'main5':found5,'group_verdict':gv.get('verdict'),
                'supplemental':supplemental,'auto_not_listed':main.get('auto_reason')=='未列出'}
        rows.append(row)
    put(OUT/'point_outcomes.json',rows);put(OUT/'statistical_issues.json',issues)
    intervals=[]
    for scope in ['merged100','unmerged119','exclude_impl030']:
        for metric in ['main10','main5','supplemental']:
            intervals.append({'metric':metric,**bootstrap_summary(rows,metric,scope)})
            if scope=='exclude_impl030':intervals.append({'metric':metric,**bootstrap_summary(rows,metric,scope,'filtered28')})
    put(OUT/'preliminary_rates.json',intervals)
    splits=[]
    for field in ['类别','做错或漏做','角色','benchmark']:
        for label in sorted({r[field] for r in rows}):
            selected=[r for r in rows if r[field]==label]
            # A merged unit spans two role labels. Do not assign it to either by judgement.
            modes=['unmerged119'] if field=='角色' else ['merged100','unmerged119']
            for mode in modes:
                d=sum(1/20 if mode=='merged100' and r['seq'] in COLLAPSED else 1 for r in selected)
                for method in METHODS:
                    values={metric:(sum((1/20 if mode=='merged100' and r['seq'] in COLLAPSED else 1)*r[method][metric] for r in selected)/d
                         if all(r[method][metric] is not None for r in selected) else None) for metric in ['main10','main5','supplemental']}
                    splits.append({'field':field,'label':label,'scope':mode,'method':method,'points':len(selected),'units':d,**values})
    put(OUT/'preliminary_splits.json',splits)
    role_boundary={'merged_sequences':sorted(COLLAPSED),'roles':dict(Counter(r['角色'] for r in rows if r['seq'] in COLLAPSED)),
        'handling':'Overall 100-unit statistics computed. Role splits reported on 119 points only. Assignment of the merged unit to a role is left to Claude.'}
    put(OUT/'role_split_boundary.json',role_boundary)
    stated=Counter((r['benchmark'],(lookup[(r['seq'],None,'judge_stated')].get('result') or {}).get('verdict','unavailable')) for r in rows)
    stated_rows=[{'benchmark':bench,'verdict':v,'count':stated[(bench,v)]} for bench in sorted({r['benchmark'] for r in rows}) for v in ['stated_as_assumption','stated_as_decision_or_fact','not_stated','unsure','unavailable']]
    put(OUT/'stated_counts.json',stated_rows)
    records=[load(p) for p in sorted((OUT/'calls').glob('*/record.json'))];calls=[call_summary(r) for r in records]
    put(OUT/'call_summary.json',calls);csv_out(OUT/'call_summary.csv',calls)
    costs=cost_tables();put(OUT/'method_costs.json',costs)
    per_object=[{'object':x['object'],'task':x['task'],'table':x['table'],'method':x['method'],'status':x['status'],'count':x['count'],
                 'keys':json.dumps(x['keys'],ensure_ascii=False)} for x in load(OUT/'main_lists.json')]
    csv_out(OUT/'main_list_counts.csv',per_object)
    quote_counts=[]
    for kind in ['judge_match','judge_match_group','judge_stated']:
        selected=[r for r in audits if r['kind']==kind and r['called']]
        quote_counts.append({'kind':kind,'called':len(selected),'quote_provided':sum(r['quote_provided'] for r in selected),
            'exact':sum(r['exact'] is True for r in selected),'whitespace_collapsed':sum(r['whitespace_collapsed'] is True for r in selected),
            'quote_exact_failures':[{'seq':r['seq'],'method':r['method'],'selector':r['selector']} for r in selected if r['exact'] is False],
            'null_or_empty_quote':sum(not r['quote_provided'] for r in selected),'issues':[r for r in selected if r['issue']]})
    aggregate={'preliminary':True,'human_review_performed':False,'basis':'unredacted full archive',
        'logical_results':len(results),'API_calls':len(calls),'judge_calls':sum(c['provider']=='deepseek' for c in calls),
        'new_repairs':sum(c['provider']=='openai' for c in calls),'API_success':sum(c['api_success'] for c in calls),
        'parse_success':sum(c['parse_success'] for c in calls),'truncated':sum(c['truncated'] is True for c in calls),
        'estimated_usd':sum(c['estimated_usd'] or 0 for c in calls),
        'provider_costs':{p:sum(c['estimated_usd'] or 0 for c in calls if c['provider']==p) for p in ['openai','deepseek']},
        'usage':{k:sum(c[k] or 0 for c in calls) for k in ['input_tokens','cached_input_tokens','output_tokens','reasoning_tokens']},
        'unsure':dict(Counter(r['kind'] for r in results if isinstance(r.get('result'),dict) and r['result'].get('verdict')=='unsure')),
        'auto_not_listed':sum(r.get('auto_reason')=='未列出' for r in results),'statistical_issues':issues,
        'mean_main_list_items':{m:sum(x['count'] for x in load(OUT/'main_lists.json') if x['method']==m)/79 for m in METHODS},
        'mean_cost_per_object':{m:{k:sum(x[k] for x in costs if x['method']==m)/79 for k in ['effective_path_usd','all_incurred_usd']} for m in METHODS},
        'quote_counts':quote_counts,'missing_usage_calls':[c['tag'] for c in calls if c['input_tokens'] is None],
        'network_attempts_without_usage':sum(not a['success'] for r in records for a in r['attempts'])}
    put(OUT/'aggregate_statistics.json',aggregate)
    print(json.dumps({'event':'preliminary_statistics_complete','calls':len(calls),'estimated_usd':aggregate['estimated_usd'],'issues':len(issues)}),flush=True)


def blind():
    results=load(OUT/'all_judge_results.json');audits=load(OUT/'quote_audit.json');rng=random.Random(1234)
    audit={(r['seq'],r['method'],r['kind']):r for r in audits};pts={p['seq']:p for p in load(OUT/'points.json')}
    mains={(r['object'],r['method']):r for r in load(OUT/'main_lists.json')};groups={(r['task'],r['method']):r for r in load(OUT/'group_lists.json')}
    selected={};reasons=defaultdict(list)
    def add(r,reason):
        identity=(r['seq'],r['method'],r['kind']);selected[identity]=r;reasons[identity].append(reason)
    candidates=[r for r in results if r['kind']=='judge_match' and r['called']]
    for r in candidates:
        value=r.get('result') or {};a=audit[(r['seq'],r['method'],r['kind'])]
        if value.get('verdict')=='unsure':add(r,'all_unsure')
        if a['exact'] is False or (value.get('verdict')=='match' and not a['quote_provided']):add(r,'quote_not_found_exactly')
    for verdict in ['match','no_match']:
        for method in METHODS:
            pool=[r for r in candidates if r['method']==method and (r.get('result') or {}).get('verdict')==verdict]
            for r in rng.sample(pool,min(10,len(pool))):add(r,f'random_{verdict}_{method}')
    for r in results:
        if r['kind']=='judge_match_group' and (r.get('result') or {}).get('verdict') in ['match','unsure']:add(r,'all_group_match_or_unsure')
    shuffled=list(selected.items());rng.shuffle(shuffled);review=[];answers=[]
    for n,(identity,r) in enumerate(shuffled,1):
        point=pts[r['seq']];bid=f'R{n:04d}'
        text=(json.dumps(mains[(r['object'],r['method'])]['items'],ensure_ascii=False,indent=2) if r['kind']=='judge_match' else groups[(r['task'],r['method'])]['text'])
        review.append({'盲判编号':bid,'对象':r['object'],'表名':r['table'],'前提句':point['agent默认的前提'],
            '实际要求':point['实际要求或数据情况'],'要判的清单原文':text,'对上了没有':'','第几条':''})
        answers.append({'盲判编号':bid,'seq':r['seq'],'point_id':point['point_id'],'method':r['method'],'kind':r['kind'],
            'judge_result':r['result'],'sampling_reasons':reasons[identity],'quote_audit':audit[identity]})
    csv_out(OUT/'blind_review_match.csv',review);put(OUT/'blind_review_match.json',review);put(OUT/'blind_answers_match.json',answers)
    csv_out(OUT/'blind_answers_match.csv',[{**x,'judge_result':json.dumps(x['judge_result'],ensure_ascii=False),'sampling_reasons':json.dumps(x['sampling_reasons']),
        'quote_audit':json.dumps(x['quote_audit'],ensure_ascii=False)} for x in answers])
    stated=[]
    for verdict in ['stated_as_assumption','stated_as_decision_or_fact','not_stated','unsure']:
        pool=[r for r in results if r['kind']=='judge_stated' and (r.get('result') or {}).get('verdict')==verdict]
        stated.extend(rng.sample(pool,min(10,len(pool))))
    rng.shuffle(stated);sr=[];sa=[]
    for n,r in enumerate(stated,1):
        p=pts[r['seq']];bid=f'S{n:04d}';sr.append({'盲判编号':bid,'对象':r['object'],'表名':r['table'],'前提句':p['agent默认的前提'],
            '实际要求':p['实际要求或数据情况'],'agent文字原文':load(OUT/r['task']/'agent_text.json')['text'],'分类':'','位置':'','原话':''})
        sa.append({'盲判编号':bid,'seq':r['seq'],'point_id':r['point_id'],'judge_result':r['result']})
    csv_out(OUT/'blind_review_stated.csv',sr);put(OUT/'blind_review_stated.json',sr);put(OUT/'blind_answers_stated.json',sa)
    csv_out(OUT/'blind_answers_stated.csv',[{**x,'judge_result':json.dumps(x['judge_result'],ensure_ascii=False)} for x in sa])
    put(OUT/'blind_sampling.json',{'seed':1234,'match_rows':len(review),'stated_rows':len(sr),
        'match_by_kind_method_verdict':dict(Counter(f'{r["kind"]}:{r["method"]}:{r["judge_result"]["verdict"]}' for r in answers)),
        'stated_by_verdict':dict(Counter(r['judge_result']['verdict'] for r in sa)),
        'reviewer_files':['blind_review_match.csv','blind_review_stated.csv'],'answer_files':['blind_answers_match.json','blind_answers_stated.json'],
        'blinding_limit':'No method or judge conclusion columns. Required original item schemas may themselves suggest a method; not rewritten.'})
    print(json.dumps({'event':'blind_tables_complete','match_rows':len(review),'stated_rows':len(sr)}),flush=True)


def verify():
    freeze_check();checks=Counter();F.load_prepared()
    for path,digest in load(OUT/'start_state.json')['tracked_file_sha256'].items():
        assert sha((ROOT/path).read_bytes())==digest,path;checks['original_tracked_files_unchanged']+=1
    for path,digest in load(OUT/'protected_private_hashes.json').items():
        assert sha((ROOT/path).read_bytes())==digest,path;checks['original_private_files_unchanged']+=1
    assert not (OUT/'STOP.json').exists(),'Do not publish as complete following a stopping condition'
    pts={p['seq']:p for p in load(OUT/'points.json')};lists={(x['object'],x['method']):x for x in load(OUT/'main_lists.json')}
    groups={(x['task'],x['method']):x for x in load(OUT/'group_lists.json')}
    results=load(OUT/'all_judge_results.json');assert len(results)==595
    assert abs(sum(1/20 if n in COLLAPSED else 1 for n in pts)-100)<1e-10
    records=[load(p) for p in (OUT/'calls').glob('*/record.json')]
    first_api=min(datetime.fromisoformat(r['started_at']) for r in records)
    assert first_api>datetime.fromisoformat(load(OUT/'preregistration_commit.json')['time'])
    for r in records:
        body=load(ROOT/r['request_path'])['json'];provider=r['provider']
        if provider=='openai':
            assert set(body)=={'model','input','reasoning','max_output_tokens'}
            assert body['model']=='gpt-6.1-sol' and body['reasoning']=={'effort':'medium','summary':'auto'} and body['max_output_tokens']==32000
            if r['kind']=='method2':expected=F.assembled(r['task'],method2=True)
            elif r['kind']=='method1_final':expected=F.assembled(r['task'],final_rank=True,ledger=load(OUT/'repairs/biomedical-easy-2/ledger_all.json'))
            else:expected=F.assembled(r['task'],r['call'],ledger=load(OUT/'repairs/biomedical-easy-2'/f'ledger_before_call_{r["call"]}.json'))
            assert body['input'].encode()==expected.encode()
            assert (ROOT/r['request_path']).with_name('assembled_prompt.txt').read_bytes()==expected.encode()
        else:
            assert set(body)=={'model','messages'} and body['model']=='deepseek-flash'
            assert load(ROOT/r['request_path'])['url']=='https://api.deepseek.com/chat/completions'
            assert len(body['messages'])==1 and body['messages'][0]['role']=='user'
            point=pts[r['point_id']];values={'table':point['table'],'premise':point['agent默认的前提'],'truth':point['实际要求或数据情况']}
            if r['kind']=='judge_match':values['items']=json.dumps(lists[(point['object'],r['method'])]['items'],ensure_ascii=False,indent=2)
            elif r['kind']=='judge_match_group':values['group_items']=groups[(r['task'],r['method'])]['text']
            else:values['agent_text']=load(OUT/r['task']/'agent_text.json')['text']
            expected=template(r['kind']+'.txt',values)
            assert body['messages'][0]['content'].encode()==expected.encode()
        assert sha(expected.encode())==r['prompt_sha256'];checks['byte_exact_requests_verified']+=1
        if r['api_success']:
            raw=load(ROOT/r['response_path'])
            assert P.usage_record(raw,provider)==r['usage']
            text=P.response_text(raw,provider)
            assert text==(ROOT/r['response_path']).with_name('text.txt').read_bytes().decode()
            assert P.parse_text(text)==load(ROOT/r['parse_path'])
            assert P.price(r['usage'],provider,r['attempts'][-1]['started_at'])==r['cost']
            checks['raw_response_usage_price_and_parsing_verified']+=1
    seed_record=load(ROOT/load(OUT/'repairs/biomedical-easy-2/reused_call_1.json')['source'])
    ledger,_,_=F.ledger_additions(F.parsed_value(seed_record),1)
    assert ledger==load(OUT/'repairs/biomedical-easy-2/ledger_after_call_1.json')
    for number in range(2,6):
        assert ledger==load(OUT/'repairs/biomedical-easy-2'/f'ledger_before_call_{number}.json')
        record=load(OUT/'calls'/f'biomedical-easy-2_method1_{number}'/'record.json')
        added,_,_=F.ledger_additions(F.parsed_value(record),number);ledger.extend(added)
        assert ledger==load(OUT/'repairs/biomedical-easy-2'/f'ledger_after_call_{number}.json')
    assert ledger==load(OUT/'repairs/biomedical-easy-2/ledger_all.json');checks['repair_ledger_chain_verified']=5
    assert quote_audit(results)==load(OUT/'quote_audit.json');checks['quote_audit_reproduced']=len(results)
    assert all(x['whitespace_collapsed'] is True for x in load(OUT/'quote_audit.json') if x['exact'] is True)
    for file in ['blind_review_match.json','blind_review_stated.json']:
        data=load(OUT/file)
        forbidden={'method','kind','verdict','judge_result','sampling_reasons','quote_audit'}
        for row in data:assert not set(row)&forbidden
        checks['blind_rows_no_answer_or_method_columns']+=len(data)
    credentials=F.credentials()
    for file in OUT.rglob('*'):
        if file.is_file():assert not any(key in file.read_bytes() for key in credentials),str(file);checks['private_files_actual_credentials_absent']+=1
    put(OUT/'verification.json',{'checks':dict(checks),'all_passed':True,
        'old_dirty_044_file':'Preserved the start-of-task bytes; excluded from commits.',
        'statistics_source':'Private unredacted inputs and outputs; exact lexical checks only.'})
    print(json.dumps({'event':'verified','checks':dict(checks)}),flush=True)


def redaction_map():
    mapping={}
    for folder in ['050_pilot_full','051_formal_run_full','052_formal_run_full']:
        path=ROOT/'data'/folder/('private_sid_mapping.json' if folder.startswith('050') else 'private_redaction_mapping.json')
        if not path.exists():continue
        data=load(path);data=data.get('mapping',data)
        if isinstance(data,dict):
            for k,v in data.items():
                if k.startswith('['):mapping[v.encode()]=k.encode()
                else:mapping[k.encode()]=v.encode()
        else:
            for row in data:
                mapping[(row.get('original') or row.get('value')).encode()]=row['placeholder'].encode()
    return mapping


def publish():
    assert load(OUT/'verification.json')['all_passed']
    excluded={'private_redaction_mapping.json','report_unredacted.md'}
    mapping=redaction_map();found=defaultdict(set)
    files=[p for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in excluded]
    for file in files:
        b=file.read_bytes();assert not any(key in b for key in F.credentials()),str(file)
        for kind,value in F.secret_hits(b):found[kind].add(value)
    for kind,values in sorted(found.items()):
        used=set(mapping.values());index=1
        for value in sorted(values):
            if value in mapping:continue
            while f'[REDACTED_{kind}_{index}]'.encode() in used:index+=1
            placeholder=f'[REDACTED_{kind}_{index}]'.encode();mapping[value]=placeholder;used.add(placeholder);index+=1
    put(OUT/'private_redaction_mapping.json',{k.decode():v.decode() for k,v in mapping.items()})
    manifest=[];affected=[]
    for file in files:
        b=file.read_bytes();public=b;counts={}
        for value,placeholder in mapping.items():
            count=public.count(value)
            if count:counts[placeholder.decode()]=count;public=public.replace(value,placeholder)
        assert not F.secret_hits(public) and not any(k in public for k in F.credentials()),str(file)
        target=PUB/file.relative_to(OUT);target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert target.read_bytes()==public,str(target)
        else:target.write_bytes(public)
        entry={'full_path':str(file.relative_to(ROOT)),'public_path':str(target.relative_to(ROOT)),'bytes':len(b),
            'sha256':sha(b),'public_sha256':sha(public)};manifest.append(entry)
        if counts:affected.append({**entry,'replacements':counts,'total_replacements':sum(counts.values())})
    put(PUB/'full_archive_manifest.json',{'full_archive':str(OUT.relative_to(ROOT)),'git_ignored':True,'files':manifest,
        'statistics_basis':'All counts, quotes, tokens and costs are calculated from full files before public redaction.'})
    put(PUB/'redaction_manifest.json',{'classes':{k:len(v) for k,v in found.items()},'unique_values':sum(map(len,found.values())),
        'total_replacements':sum(r['total_replacements'] for r in affected),'affected_files':affected,
        'only_matched_value_bytes_replaced':True,'mapping_private':str((OUT/'private_redaction_mapping.json').relative_to(ROOT))})
    print(json.dumps({'event':'published','files':len(manifest),'redactions':sum(r['total_replacements'] for r in affected),'affected_files':len(affected)}),flush=True)


def md_table(headers,rows):
    def cell(v):return str(v if v is not None else '—').replace('|','\\|').replace('\r','').replace('\n','<br>')
    return '| '+' | '.join(map(cell,headers))+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(cell,r))+' |\n' for r in rows)+'\n'


def pct(x):return '未知' if x is None else f'{100*x:.4f}%'


def interval(x):
    return pct(x.get('rate'))+' ['+', '.join(pct(v) for v in x.get('CI95',[]))+']'


def delta_interval(x):
    if x.get('rate') is None:return '未知'
    return f'{100*x["rate"]:.4f} ['+', '.join(f'{100*v:.4f}' for v in x.get('CI95',[]))+']'


def report():
    agg=load(OUT/'aggregate_statistics.json');rates=load(OUT/'preliminary_rates.json');splits=load(OUT/'preliminary_splits.json')
    stated=load(OUT/'stated_counts.json');lists=load(OUT/'main_lists.json');groups=load(OUT/'group_lists.json')
    calls=load(OUT/'call_summary.json');costs=load(OUT/'method_costs.json');sampling=load(OUT/'blind_sampling.json')
    archive=json.loads((PUB/'full_archive_manifest.json').read_bytes());redaction=json.loads((PUB/'redaction_manifest.json').read_bytes())
    state=load(OUT/'start_state.json');pre=load(OUT/'preregistration_commit.json');repair=load(OUT/'repairs_complete.json')
    delivery=json.loads((PUB/'delivery_commit.json').read_bytes()) if (PUB/'delivery_commit.json').exists() else None
    date=datetime.now(timezone(timedelta(hours=8))).date().isoformat()
    target=ROOT/f'notes/053_{date}_小实验裁判与初步结果.md';lines=['# 小实验第 5 步：裁判与初步结果\n\n','## 任务\n\n',
        '补跑两处网络失败，按冻结规则整理主清单和组名清单，调用三类 DeepSeek 裁判，生成初步统计与人工抽查盲判表。未修改 047、049、050、051、052 的文件，未更改提示词、模型或模型参数。\n\n',
        '## 结论\n\n',
        '**以下均为初步结果，仅使用裁判返回，尚未经过人工抽查。** 所有条数、引用核对、token 和花费统计均基于 `data/053_judging_full/` 中未脱敏的完整版；公开版只做字面脱敏，不重新计算统计。\n\n']
    primary=next(r for r in rates if r['scope']=='merged100' and r['metric']=='main10')
    lines.append(f'两处补跑成功，共新增 6 次被测模型调用。100 单位口径的前 10 命中率：做法一 {interval(primary["method1"])}，做法二 {interval(primary["method2"])}；配对差值（做法一减做法二，单位：百分点）{delta_interval(primary["difference"])}。方括号为按题重抽样的 95% 范围，不据此修改任何裁判结论。\n\n')
    lines.append(f'本任务共 {agg["API_calls"]} 次调用（补跑 {agg["new_repairs"]}，裁判 {agg["judge_calls"]}），成功 {agg["API_success"]}，解析成功 {agg["parse_success"]}，截断 {agg["truncated"]}；已返回 usage 的估算花费 ${agg["estimated_usd"]:.9f}。网络失败尝试的未返回计费用量未知，以账单为准。\n\n')
    lines+=['## 详细发现\n\n','### 事先存档与执行来源\n\n',
        f'- 开工 commit：`{state["start_commit"]}`；开工时间 `{state["started_at"]}`。开工时 notes/、records/ 最大编号 052，本任务使用 053。交付前再次查号最大为 053，无其他任务占用，未顺延；记录见 `git_secret_scan.json`。\n',
        f'- 补充口径二与组名裁判提示词，按用户全文逐字存档，单独提交并推送：`{pre["commit"]}`，时间 `{pre["time"]}`，在首次 API 调用之前。原文 SHA256 核对见 `records/053_judging/frozen_source_check.json`。\n',
        '- 被测模型完全复用 `records/051_formal_run.py` 的调用与拼装函数，v2 提示词、medium、summary auto、max_output_tokens 32000 不变，按字节读取输入。DeepSeek 完全复用 `records/050_pilot_run.py` 的默认请求、重试与解析函数；官方接口 `https://api.deepseek.com`，模型 `deepseek-flash`。OpenAI Python SDK 3.46.0，tiktoken 0.14.0。\n',
        '- 裁判先串行运行，再在调用完成的检查点转为最多 6 个独立出错点并行；已完成调用按原 tag 缓存复用，无在途请求被打断或重复调用。单个请求参数、重试和解析规则不变。见 `judge_execution_scheduler.json` 和两份 judging 日志。\n\n',
        '### 补跑与账本\n\n',
        '- impl-006：仅替换有效结果来源中的做法二；原失败记录仍在 052。\n',
        '- biomedical-easy-2：第 1 次普通叫起复用 052；重跑第 2、3、4、5 次普通叫起及交卷重排。每次以前面所有解析成功的条目累积账本，不因 updates 删除旧条目；做法二仍取 052。复用出处、逐次账本和 fewer 原文保存在 `repairs/biomedical-easy-2/`。\n',
        '- 六次补跑均 completed、解析成功、未截断。后续清单、裁判和统计均采用补跑后的有效路径。`list_provenance.json` 给出全部 58 个最终来源的路径与解析文件 SHA256。\n\n',
        '### 每个对象的主清单\n\n',
        '按给定规范化顺序识别契约表名或交付 SQL 文件名；多个同表键依返回顺序接起来后取前 10 条。KramaBench 单键直接用，多键按 importance、键顺序、键内顺序取前 10 条。importance 只在最终提交裁判前去掉，其他字段保留。158 份清单未出现格式或账本 ID 问题。完整条目见 `main_lists.json`，逐键映射也保留其中。\n\n']
    by_object=defaultdict(dict)
    for x in lists:by_object[x['object']][x['method']]=x
    lines.append(md_table(['对象','做法一条数','做法一采用的原键','做法二条数','做法二采用的原键'],[
        [obj,d['method1']['count'],'；'.join(d['method1']['keys']) or '未列出',d['method2']['count'],'；'.join(d['method2']['keys']) or '未列出'] for obj,d in by_object.items()]))
    lines+=['### 全部组名键\n\n',
        '做法一 49 个、做法二 27 个（以“题号 × 做法 × 原键”计，不跨题去重）。以下只列名称和条数，不判断它们覆盖哪些表；KramaBench 无组名。裁判每条前均带原始 Group 名称。\n\n',
        md_table(['题号','做法','原始组名键','规范化键','条数'],[[g['task'],g['method'],k['key'],k['normalized_key'],k['count']] for g in groups for k in g['keys']]),
        '### 裁判调用、token 与花费\n\n']
    verdicts=Counter((r['kind'],r['method'],(r.get('result') or {}).get('verdict','不适用/不可用')) for r in load(OUT/'all_judge_results.json'))
    lines.append(md_table(['类型','做法','裁判 verdict（原样）','条数'],[[k[0],k[1],k[2],v] for k,v in sorted(verdicts.items(),key=lambda kv:str(kv[0]))]))
    lines.append(f'主清单未列出而按规则直接记 no_match：{agg["auto_not_listed"]} 次；未调用裁判，也未进入抽查候选池。unsure 在初步命中率里记为未找到，各类型 unsure 数见上表。\n\n')
    lines.append(md_table(['来源','调用','成功','解析成功','截断','输入 token','缓存输入','输出 token','推理 token','估算美元'],[
        [provider,len(cs),sum(c['api_success'] for c in cs),sum(c['parse_success'] for c in cs),sum(c['truncated'] is True for c in cs),
         *[sum(c[k] or 0 for c in cs) for k in ['input_tokens','cached_input_tokens','output_tokens','reasoning_tokens']],sum(c['estimated_usd'] or 0 for c in cs)]
        for provider in ['openai','deepseek'] for cs in [[c for c in calls if c['provider']==provider]]]))
    u=agg['usage'];lines.append(f'全部缓存输入比例 {u["cached_input_tokens"]}/{u["input_tokens"]} = {pct(u["cached_input_tokens"]/u["input_tokens"])}。有思考摘要或 reasoning_content 的返回 {sum(c["reasoning_summary_present"] for c in calls)} 次。网络错误等未返回 usage 的尝试 {agg["network_attempts_without_usage"]} 次；其花费未计入已知用量，不称为免费。\n\n')
    lines.append('每次调用的时间、重试次数、token、缓存比例、reasoning token、输入实际/o200k 比值、状态和花费如下；同样的机器可读明细在 `call_summary.csv`。\n\n')
    lines.append(md_table(['调用','成功/解析/完成','截断','开始 UTC','结束 UTC','尝试数','输入/缓存','输出/推理','实际输入/o200k','美元'],[
        [c['tag'],f'{c["api_success"]}/{c["parse_success"]}/{c["completed"]}',c['truncated'],c['started_at'],c['finished_at'],c['attempts'],
         f'{c["input_tokens"]}/{c["cached_input_tokens"]}',f'{c["output_tokens"]}/{c["reasoning_tokens"]}',c['actual_input_to_current_o200k_ratio'],c['estimated_usd']] for c in calls]))
    lines+=['计价沿用用户指定的估算价格：Sol 每百万输入 $2、缓存 $0.10、输出 $10；DeepSeek 每百万未缓存输入 $0.15/$0.30、缓存 $0.003/$0.006、输出 $0.60/$1.20（低峰/高峰），按请求最后一次尝试的 UTC 开始时间判高峰，周一至周五 01–04、06–10。超过 272,000 输入的 Sol 调用保留长输入价格待核标记。\n\n',
        '### 裁判 quote 的字面核对\n\n',
        'judge_match 只在指定 rank 的那一条中查；judge_match_group 只在指定 position 的那一条中查；judge_stated 只在摘取的 agent_text 中查。对 JSON 中的转义，同时查相同条目的序列化文本及解码后字符串字段，不到其他条目或 Known error 中找。null/空 quote 记为未给出，不算逐字失败；match 若缺 quote 则列入必查。\n\n',
        md_table(['类型','实际调用','给出非空 quote','完全逐字找到','合并空白后找到','未给原话'],[[q[k] for k in ['kind','called','quote_provided','exact','whitespace_collapsed','null_or_empty_quote']] for q in agg['quote_counts']]),
        '逐条核对与失败项见 `quote_audit.json`，本报告不替裁判修正 verdict。\n\n',
        '### 初步命中率与配对差值\n\n',
        '119 行中指定的 20 个序号各占 1/20 权重，合计为一个单位，其余各一个单位，总计 100。去掉 impl-030 是去掉该题全部点。bootstrap 按题有放回重抽 10,000 次，random.Random(1234)，两种做法共用同一抽样，使用线性插值的 2.5%、97.5% 分位。unsure 按零分计；不对裁判语义或原话正确性作人工修正。\n\n',
        md_table(['口径','抽题范围','指标','点数/单位数','做法一及 95% 范围','做法二及 95% 范围','差值及 95% 范围（百分点）'],[
            [r['scope'],r['draw_scope'],r['metric'],f'{r["points"]}/{r["units"]}',interval(r['method1']),interval(r['method2']),delta_interval(r['difference'])] for r in rates]),
        'main10 为主要的数；main5 为辅助的数；supplemental 为本表主清单或组名清单任一裁判为 match。上述数字均为初步，不套用事先结论阈值给研究下结论。\n\n',
        '去掉 impl-030 后，抽样题数有两种读法：仍从 29 题抽后排除该题，或先排除后从 28 题抽。两版均列出，点估计相同；主分析的 29 题口径没有此歧义。最终采用哪版留给 Claude。\n\n',
        '### 辅助条数与每张表花费\n\n',
        md_table(['做法','79 个对象的主清单平均条数','有效路径每对象平均美元','全部已发生调用每对象平均美元'],[
            [m,agg['mean_main_list_items'][m],agg['mean_cost_per_object'][m]['effective_path_usd'],agg['mean_cost_per_object'][m]['all_incurred_usd']] for m in METHODS]),
        '每题花费除以该题对象数，逐题如下。有效路径只计最后采用结果所依赖的 Sol 调用；全部已发生另含被补跑替换的旧调用。两者均列出，避免擅自决定应如何归属补跑前的花费。平均数按 79 个对象加权，不把裁判费用算作任何一种被测做法的费用。未返回 usage 的失败尝试费用仍未知。\n\n',
        md_table(['题号','做法','对象数','有效路径美元','有效路径每对象美元','全部发生美元','全部发生每对象美元'],[
            [c[k] for k in ['task','method','objects','effective_path_usd','effective_path_per_object_usd','all_incurred_usd','all_incurred_per_object_usd']] for c in costs]),
        '### 预定拆分：只列数\n\n',
        md_table(['字段','类别','口径','做法','点数','单位数','前 10','前 5','含组名'],[
            [s['field'],s['label'],s['scope'],s['method'],s['points'],s['units'],pct(s['main10']),pct(s['main5']),pct(s['supplemental'])] for s in splits]),
        '角色只列未合并的 119 点拆分：20 点合并单元跨“主要”和“并列”，归到哪个角色尚无规则；没有自行按多数或任一标签归类。整体 100 单位和其他拆分照常计算。角色的机械计数与待定事项见 `role_split_boundary.json`。\n\n',
        '### judge_stated\n\n',
        md_table(['benchmark','返回分类','个数'],[[s['benchmark'],s['verdict'],s['count']] for s in stated]),
        '摘取规则、带步骤/事件位置的每段文字与全部结果保存在各题 `agent_text.json` 和 `all_judge_results.json`。沿用 050 提取器时，impl-018 event 83 和 impl-030 event 19 各有一次 Python tokenize 失败，保留此前已提取的内容及错误，不自行修复轨迹。\n\n',
        '### 人工抽查盲判表\n\n',
        f'- 匹配抽查 {sampling["match_rows"]} 行：`records/053_judging/blind_review_match.csv`（另有 JSON）。包含本表 unsure、原话逐字未找到的必查项、每种做法 match/no_match 各至多 10 个随机项（不足全取），以及组名 match/unsure 全部；重复入选同一调用只占一行。\n',
        f'- stated 抽查 {sampling["stated_rows"]} 行：`records/053_judging/blind_review_stated.csv`，四类各抽至多 10 个，不足全取。\n',
        '- **不给抽查者**：`blind_answers_match.csv/.json`、`blind_answers_stated.csv/.json`。逐行对应的做法、裁判结论和抽样原因在答案对照表。`blind_sampling.json` 说明各类实际数量。\n',
        '- 抽样和乱序使用 random.Random(1234)，抽查表没有做法或裁判结论字段。按要求保留的条目原文，其字段形状可能暗示做法，这是盲判限制；没有擅自改写条目。\n\n',
        md_table(['抽查类型/做法/裁判分类（仅本报告与答案表）','行数'],list(sampling['match_by_kind_method_verdict'].items())),
        md_table(['stated 抽中分类（仅本报告与答案表）','行数'],list(sampling['stated_by_verdict'].items())),
        '### 完整版、脱敏与复核\n\n',
        f'完整版目录 `data/053_judging_full/`，不进 git。共发布 {len(archive["files"])} 份文件，替换 {redaction["total_replacements"]} 处，涉及 {len(redaction["affected_files"])} 份文件，类别 {json.dumps(redaction["classes"],ensure_ascii=False)}；同值在所有新旧文件里沿用同一占位符。只替换命中的字符串字节；原始返回、解析结果、裁判输入和盲判表如有出现也同样替换。逐文件替换次数、路径和 SHA256 见 `redaction_manifest.json`，全部文件的完整版/公开版 SHA256 见 `full_archive_manifest.json`。\n\n',
        '已复核原有受保护文件字节未改、补跑账本链、每份请求的逐字拼装及参数、原始 usage/价格/解析一致、逐条 quote 核对可重现。开工前已修改的 044 报告保留原样，不纳入本任务提交。详情见 `verification.json`。提交与推送前另扫描本任务全部公开文件及每一个待推送 commit 的全部新增/改动 blob，检查实际 key 与强特征疑似密钥。\n\n',
        md_table(['受脱敏影响的公开文件','替换次数','完整版 SHA256','公开版 SHA256'],[[r['public_path'],r['total_replacements'],r['sha256'],r['public_sha256']] for r in redaction['affected_files']]),
        '完整请求、原始返回 JSON、原始 HTTP 正文路径和 SHA256：\n\n']
    hashes={x['full_path']:x['sha256'] for x in archive['files']};hash_rows=[]
    for record in [load(p) for p in sorted((OUT/'calls').glob('*/record.json'))]:
        paths=[('请求',record['request_path'])]
        for response in sorted((ROOT/record['request_path']).parent.glob('attempt_*_response.json')):
            if not re.fullmatch(r'attempt_\d+_response\.json',response.name):continue
            paths.extend([('原始返回 JSON',str(response.relative_to(ROOT))),('原始 HTTP 正文',str(response.with_name(response.stem+'_body.txt').relative_to(ROOT)))])
        for label,path in paths:
            if path in hashes:hash_rows.append([record['tag'],label,path,hashes[path]])
    lines.append(md_table(['调用','文件','完整版路径','SHA256'],hash_rows))
    lines+=['## 证据来源\n\n',
        '- 标准答案冻结来源：`records/047_premise_sentences_draft.csv`，119 行，29 题、79 个对象；没有改写前提或实际要求。\n',
        '- 冻结输入和提示词：`records/049_small_exp_assemble.py`、`records/049_prompts/`、`records/051_formal_run.py`、`records/051_prompts/`；既有调用来自 `data/051_formal_run_full/`、`data/052_formal_run_full/`。\n',
        '- 轨迹：`traces/dacomp_deimpl_prev.tar.gz` 中指定 20261025 批次；`traces/kramabench_luna_baseline.tar.gz`。SQL 文件仅枚举归档成员，未执行 agent 代码，未查询数据库数据。\n',
        '- 新脚本：`records/053_judging.py`；公开产物总目录 `records/053_judging/`，未脱敏目录 `data/053_judging_full/`。\n',
        '- 已执行命令：在 `TIKTOKEN_CACHE_DIR=/tmp/assumption-ledger-048-tiktoken-cache PYTHONDONTWRITEBYTECODE=1` 下，用 `/tmp/assumption-ledger-050-venv/bin/python records/053_judging.py` 依次执行 `prepare`、`repair`、`assemble`、`judge`、`statistics`、`blind`、`verify`、`publish`、`report`；`judge` 检查点后按原 tag 恢复。提交和推送日志另列于 git 历史。\n\n',
        '## 不确定或没查到的\n\n',
        '- 未进行任何人工语义判断或抽查；裁判误差、组名是否覆盖某表仍由裁判原样判断。初步数字不等于人工复核后的正式结果。\n',
        '- 角色跨标签合并单位的归属、排除 impl-030 后 bootstrap 的抽题范围、被替换旧调用的费用归属，均列出供 Claude 决定，未擅自选择研究口径。\n',
        '- 两处轨迹注释 tokenization 失败、条目字段可能暗示做法的盲判限制见上文。\n',
        '- 网络失败尝试没有 usage 的计费、实际账单和长输入价格尚未核实。\n',
        '- 依据是否在做法一当次材料中按补充口径二暂缓，本任务未做。\n\n',
        '## 建议的下一步\n\n',
        '将两份 blind_review 文件单独交给抽查者，避免同时提供报告、答案对照表和其他裁判结果。独立判完后按 051 事先口径核对一致率；由用户和 Claude 决定上述待定口径及后续处理。\n\n']
    if delivery:lines.append(f'交付产物 commit：`{delivery["commit"]}`，时间 `{delivery["time"]}`；本报告及交付引用的提交在其后。事先存档并推送的 commit 为 `{PREREG}`。\n')
    full=''.join(lines).encode();public=full;counts={}
    for value,placeholder in load(OUT/'private_redaction_mapping.json').items():
        n=public.count(value.encode())
        if n:counts[placeholder]=n;public=public.replace(value.encode(),placeholder.encode())
    assert not F.secret_hits(public) and not any(k in public for k in F.credentials())
    private=OUT/'report_unredacted.md';private.write_bytes(full);target.write_bytes(public)
    metadata={'full_path':str(private.relative_to(ROOT)),'sha256':sha(full),'public_path':str(target.relative_to(ROOT)),
        'public_sha256':sha(public),'replacements':counts,'statistics_basis':'unredacted full archive'}
    (PUB/'report_archive_manifest.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'event':'report_written','path':str(target.relative_to(ROOT)),'bytes':len(public)}),flush=True)


def audit(write=True):
    """Scan every new Git blob, including superseded blobs in unpushed commits."""
    commits=subprocess.check_output(['git','rev-list','--reverse','origin/main..HEAD'],text=True).splitlines()
    object_lines=subprocess.check_output(['git','rev-list','--objects','origin/main..HEAD'],text=True).splitlines()
    objects=list(dict.fromkeys(line.split(' ',1)[0] for line in object_lines))
    data=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(objects)+'\n').encode()) if objects else b''
    position=0;blobs=0;scanned_bytes=0;credentials=F.credentials()
    while position<len(data):
        end=data.index(b'\n',position);identity,kind,size=data[position:end].split();size=int(size)
        payload=data[end+1:end+1+size];position=end+1+size+1
        if kind!=b'blob':continue
        assert not F.secret_hits(payload),('unpublished_blob_secret_pattern',identity.decode())
        assert not any(k in payload for k in credentials),('unpublished_blob_credential',identity.decode())
        blobs+=1;scanned_bytes+=size
    paths=[ROOT/p for p in subprocess.check_output(['rg','--files','notes','records'],text=True).splitlines() if re.match(r'^(notes|records)/053(?:_|/)',p)]
    for path in paths:
        payload=path.read_bytes()
        assert not F.secret_hits(payload),str(path)
        assert not any(k in payload for k in credentials),str(path)
    # Scan current index as well; the report commit must preserve these bytes.
    index=subprocess.check_output(['git','ls-files','--stage','-z']).split(b'\0');indexed=0
    for entry in index:
        if not entry:continue
        header,path=entry.split(b'\t',1);path=path.decode()
        if not re.match(r'^(notes|records)/053(?:_|/)',path):continue
        _,identity,stage=header.split();assert stage==b'0'
        payload=subprocess.check_output(['git','cat-file','blob',identity.decode()])
        assert not F.secret_hits(payload) and not any(k in payload for k in credentials),path
        assert payload==(ROOT/path).read_bytes(),('index_worktree_bytes_differ',path);indexed+=1
    if (PUB/'full_archive_manifest.json').exists():
        for row in json.loads((PUB/'full_archive_manifest.json').read_bytes())['files']:
            assert sha((ROOT/row['full_path']).read_bytes())==row['sha256'],row['full_path']
            assert sha((ROOT/row['public_path']).read_bytes())==row['public_sha256'],row['public_path']
    allowed_notes={'053_2026-11-06_小实验统计口径补充二.md', '053_2026-11-07_小实验裁判与初步结果.md'}
    numbered=[p for p in subprocess.check_output(['rg','--files','notes','records'],text=True).splitlines() if re.match(r'^(notes|records)/\d{3}',p)]
    maximum=max(int(re.match(r'^(?:notes|records)/(\d{3})',p)[1]) for p in numbered)
    foreign=[p for p in paths if (p.parent==ROOT/'notes' and p.name not in allowed_notes) or
        (p.is_relative_to(ROOT/'records') and not(p.is_relative_to(PUB) or p.is_relative_to(PROMPTS) or p==ROOT/'records/053_judging.py'))]
    assert not foreign,foreign
    result={'all_passed':True,'pending_commits':commits,'all_new_blobs_in_all_pending_commits':blobs,
        'new_blob_bytes':scanned_bytes,'public_task_files_scanned':len(paths),'index_files_verified':indexed,
        'checks':'actual home-file credentials plus 8 strong secret-pattern classes; never log matching values',
        'delivery_maximum_number':maximum,'task_number':53,'number_conflicts':[],'renumbered':False}
    if write:
        target=PUB/'git_secret_scan.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        assert not F.secret_hits(target.read_bytes()) and not any(k in target.read_bytes() for k in credentials)
    print(json.dumps({'event':'git_and_public_secret_scan','checks':result}),flush=True)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['prepare','repair','assemble','judge','statistics','blind','verify','publish','report','audit'])
    args=parser.parse_args()
    try:globals()[args.command]()
    except (F.StopFormal,P.StopPilot) as e:print(json.dumps({'event':'stopped','reason':str(e),'estimated_usd':F.total_cost()}),flush=True)


if __name__=='__main__':main()
