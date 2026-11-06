"""Second batch: invoke immutable 051 code; only output root and $30 task cap differ.

No judges, known-error CSV, gold matching, or model-setting overrides.
Commands: prepare, run, analyze, verify, publish, report.
"""
import argparse
import csv
import io
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
PUB=ROOT/'records/052_formal_run'
OUT=ROOT/'data/052_formal_run_full'
OLD=ROOT/'data/051_formal_run_full'
SUPPLEMENT='cdc85f19fb5dde0f342a106ebd714e1a7aa150b8'
spec=importlib.util.spec_from_file_location('immutable_051',ROOT/'records/051_formal_run.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
# Keep F.PUB and F.PROMPTS unchanged: frozen text and its audit are read from 051.
# All writes in run_batch() target F.OUT. Budget is per new task, excluding 051.
F.OUT=OUT;F.BUDGET=30
original_stop=F.stop
def task_stop(reason,details):
    return original_stop(reason.replace('estimated_cost_exceeds_20_usd','estimated_cost_exceeds_30_usd'),details)
F.stop=task_stop
SOURCE_SHA=F.sha((ROOT/'records/051_formal_run.py').read_bytes())


def source_check():
    assert F.sha((ROOT/'records/051_formal_run.py').read_bytes())==SOURCE_SHA
    assert F.PUB==ROOT/'records/051_formal_run' and F.PROMPTS==ROOT/'records/051_prompts'
    F.freeze_check()
    audit=json.loads((PUB/'frozen_supplement_source_check.json').read_bytes())
    source=(ROOT/audit['path']).read_bytes();assert F.sha(source)==audit['sha256']
    assert subprocess.check_output(['git','show',SUPPLEMENT+':'+audit['path']])==source
    return json.loads((PUB/'supplement_commit.json').read_bytes())


def put(path,value):F.store(path,value)


def derived(path,value):
    """Replace only derived 052 statistics, never requests/returns or old assets."""
    path=Path(path);assert path.is_relative_to(OUT)
    assert 'calls' not in path.relative_to(OUT).parts and 'tasks' not in path.relative_to(OUT).parts
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def derived_csv(path,rows):
    if not rows:return
    path=Path(path);assert path.is_relative_to(OUT)
    text=io.StringIO(newline='');writer=csv.DictWriter(text,fieldnames=list(rows[0]),lineterminator='\n')
    writer.writeheader();writer.writerows(rows);data=text.getvalue().encode()
    if path.exists():assert path.read_bytes()==data,str(path)
    else:path.write_bytes(data)


def prepare():
    OUT.mkdir(parents=True,exist_ok=True);supplement=source_check()
    # Reuse 051's already verified input assets byte-for-byte; never write 051.
    for name in ['compact_blocks.json','excel_compact_validation.json','input_token_counts.csv',
                 'preparation_summary.json','preregistration.json','selection.json']:
        src=OLD/name;dst=OUT/name
        if dst.exists():assert dst.read_bytes()==src.read_bytes(),name
        else:dst.write_bytes(src.read_bytes())
    put(OUT/'start_state.json',json.loads((PUB/'start_state.json').read_bytes()))
    put(OUT/'supplement_commit.json',supplement)
    selection=F.load(OUT/'selection.json');assert len(selection['remaining'])==19 and not set(selection['remaining'])&set(selection['first'])
    old_hashes={str(p.relative_to(ROOT)):F.sha(p.read_bytes()) for p in OLD.rglob('*') if p.is_file()}
    put(OUT/'protected_051_private_hashes.json',old_hashes)
    F.load_prepared()  # Regenerates and compares all 32 blocks / 10921 cell proofs.
    import csv
    checked=0
    for row in csv.DictReader((OUT/'input_token_counts.csv').open()):
        prompt=F.assembled(row['task'],int(row['call']) if row['call'] else None,method2=row['method']=='method2')
        assert F.sha(prompt.encode())==row['after_sha256'];checked+=1
    tasks=[r for r in F.load(OUT/'preparation_summary.json')['all_29_tasks'] if r['task'] in selection['remaining']]
    config={'time':F.now(),'supplement_commit':supplement,'script_051_sha256':SOURCE_SHA,
        'unchanged_execution_source':'records/051_formal_run.py','unchanged_prompts':'records/051_prompts/',
        'runtime_overrides':{'output_root':str(OUT.relative_to(ROOT)),'task_budget_usd':30,'stop_label_only':'20_usd -> 30_usd'},
        'model_parameters':{'model':F.MODEL,'reasoning':{'effort':'medium','summary':'auto'},'max_output_tokens':32000},
        'selected_tasks':selection['remaining'],'task_count':19,'ordinary_calls':sum(t['ordinary_calls'] for t in tasks),
        'planned_calls':sum(t['ordinary_calls']+2 for t in tasks),'byte_identical_preflight_inputs':checked,
        'excel_verification_passed':True,'model_calls_in_preparation':0,'database_queries':0,
        'unseen_rule_cases':[]}
    put(OUT/'runtime_configuration.json',config)
    print(json.dumps({'event':'prepared','tasks':selection['remaining'],'planned_calls':config['planned_calls'],
        'input_hashes_verified':checked,'source_051_unchanged':True},ensure_ascii=False),flush=True)


def run():
    supplement=source_check();config=F.load(OUT/'runtime_configuration.json')
    assert config['script_051_sha256']==SOURCE_SHA
    assert datetime.now(timezone.utc)>datetime.fromisoformat(supplement['time'])
    try:F.run_batch('remaining')
    except F.StopFormal as e:print(json.dumps({'event':'stopped','reason':str(e),'task_estimated_usd':F.total_cost()}),flush=True)


def aggregate(tasks,calls):
    coverage={}
    for kind in ['method1_final','method2']:
        values=[t['finals'][kind]['coverage_proxy'] for t in tasks if t['finals'][kind] and 'coverage_proxy' in t['finals'][kind]]
        d=sum(p['denominator'] for p in values);n=sum(p['numerator'] for p in values);nonempty=sum(p['nonempty_numerator'] for p in values)
        coverage[kind]={'numerator':n,'denominator':d,'ratio':n/d if d else None,'nonempty_numerator':nonempty,'nonempty_ratio':nonempty/d if d else None}
    reviews=[r for t in tasks for r in t['reviews']]
    result={'tasks_planned':len(tasks),'tasks_completed':sum(t['finished'] for t in tasks),'calls':len(calls),
        'ordinary_calls':sum(c['type']=='method1' for c in calls),'final_rank_calls':sum(c['type']=='method1_final' for c in calls),
        'method2_calls':sum(c['type']=='method2' for c in calls),'premises_total':sum(r['premises_count'] for r in reviews),
        'sum_literal_target_counts_across_reviews':sum(r['literal_target_count'] for r in reviews),
        'distinct_task_and_literal_target_pairs':sum(t['distinct_literal_targets_across_reviews'] for t in tasks),
        'zero_reviews':sum(r['zero_items'] for r in reviews),'coverage_proxy':coverage,
        'fewer_entries_total':sum(len(r['fewer']) for r in reviews if isinstance(r['fewer'],list)),
        'final_raw_totals':{kind:sum(t['finals'][kind].get('raw_total',0) for t in tasks if t['finals'][kind]) for kind in ['method1_final','method2']},
        'final_resolved_totals':{kind:sum(t['finals'][kind].get('resolved_total',0) for t in tasks if t['finals'][kind]) for kind in ['method1_final','method2']},
        'krama_aggregate_totals':{kind:sum(t['finals'][kind].get('krama_aggregate_count') or 0 for t in tasks if t['benchmark']=='KramaBench' and t['finals'][kind]) for kind in ['method1_final','method2']},
        **{field:sum(c[field] or 0 for c in calls) for field in ['input_tokens','cached_input_tokens','output_tokens','reasoning_tokens','estimated_usd']},
        'api_success':sum(c['api_success'] for c in calls),'parse_success':sum(c['parse_success'] for c in calls),
        'truncated':sum(bool(c['truncated']) for c in calls),'reasoning_summaries':sum(c['has_reasoning_summary_text'] for c in calls),
        'sum_task_wall_seconds':sum(t['wall_seconds'] or 0 for t in tasks)}
    result['cached_input_fraction']=result['cached_input_tokens']/result['input_tokens'] if result['input_tokens'] else None
    result['unavailable_final_outputs']=[{'task':t['task'],'method':kind} for t in tasks for kind in ['method1_final','method2']
        if not t['finals'][kind] or 'raw_total' not in t['finals'][kind]]
    result['final_totals_basis']='Sum of available outputs only; unavailable outputs are unknown, not zero.'
    result['calls_without_usage']=sum(c['input_tokens'] is None for c in calls)
    known={(t['task'],r['call']) for t in tasks for r in t['reviews']}
    result['unavailable_review_calls']=[{'task':c['task'],'call':c['call'],'tag':c['tag'],'status':c['status']} for c in calls
        if c['type']=='method1' and (c['task'],c['call']) not in known]
    result['ordinary_reviews_with_readable_output']=len(known)
    return result


def quote_summary(quotes):
    result=[]
    for field in ['evidence_of_dependence','alternative','evidence_in_work','source']:
        rows=[q for q in quotes if q['field']==field];checked=[q for q in rows if q['status']=='checked'];parents=defaultdict(list)
        for q in rows:parents[(q['tag'],q['key'],q['item'])].append(q)
        good=[qs for qs in parents.values() if all(q['status']=='checked' for q in qs)]
        result.append({'field':field,'entries_or_quote_spans':len(rows),'checked':len(checked),
            'exact':sum(q['exact'] for q in checked),'whitespace_collapsed':sum(q['whitespace_collapsed'] for q in checked),
            'statuses':dict(Counter(q['status'] for q in rows)),'parent_fields_total':len(parents),
            'parent_fields_with_checkable_quotes':len(good),'parent_fields_all_exact':sum(all(q['exact'] for q in qs) for qs in good),
            'parent_fields_all_whitespace_collapsed':sum(all(q['whitespace_collapsed'] for q in qs) for qs in good)})
    return result


def group_inventory(tasks):
    result={'method1':[],'method2':[],'per_task':[],'normalization_boundary_cases':[],'excluded_KramaBench':[]}
    for task in tasks:
        m=F.A.manifest(task)
        if m['benchmark']!='DAComp':result['excluded_KramaBench'].append(task);continue
        names={s['name'] for s in m['sections']}
        assert all(n==n.lower() and '.' not in n for n in names)
        base=OLD if task in F.load(OUT/'selection.json')['first'] else OUT
        for method,kind in [('method1','method1_final'),('method2','method2')]:
            folder=base/'calls'/f'{task}_{kind}';p=folder/'parse.json'
            parsed=json.loads(p.read_bytes()) if p.exists() else None
            value=parsed.get('parsed') if parsed and parsed.get('success') else None
            entry={'task':task,'method':method,'contract_table_count':len(names),'group_keys':0 if isinstance(value,dict) else None,
                   'parse_success':bool(parsed and parsed.get('success')),'output_is_object':isinstance(value,dict)}
            if isinstance(value,dict):
                for key,body in value.items():
                    normalized=key.rsplit('.',1)[-1].lower()
                    if key.count('.')>1:result['normalization_boundary_cases'].append({'task':task,'method':method,'key':key,'normalized_by_051_rule':normalized,'reason':'More than one period; no semantic interpretation of schema or compound names.'})
                    if normalized in names:continue
                    items=body if method=='method1' else body.get('items') if isinstance(body,dict) else None
                    result[method].append({'task':task,'key':key,'normalized_key':normalized,
                        'item_count':len(items) if isinstance(items,list) else None,
                        'items_type':type(items).__name__,'parse_path':str(p.relative_to(ROOT)),
                        'parse_sha256':F.sha(p.read_bytes()),'confirmation':'Pending Claude; no table coverage assigned.'})
                    entry['group_keys']+=1
            result['per_task'].append(entry)
    result['definition']='DAComp only; output key rsplit(".",1)[-1].lower() not equal to ANY of the task contract table names. Raw lists counted; no group-to-table assignment.'
    result['counts']={method:len(result[method]) for method in ['method1','method2']}
    return result


def analyze():
    source_check();selected=F.load(OUT/'selection.json')['remaining'];original_load=F.load
    # Only change the analysis task selector. The original 051 analysis function
    # and all its quote/count helpers execute unchanged, writing exclusively 052.
    def analysis_load(path):
        p=Path(path)
        if not p.is_absolute():p=ROOT/p
        value=original_load(path)
        if p==OUT/'selection.json':return {**value,'first':selected}
        return value
    ready=all((OUT/name).exists() for name in ['task_statistics.json','call_statistics.json','quote_checks.json','quote_summary.json','format_issues.json'])
    if not ready:
        F.load=analysis_load
        try:F.analyze()
        finally:F.load=original_load
    else:assert len(F.load(OUT/'call_statistics.json'))==len(F.records_all())
    comparison=OUT/'pilot_count_comparison.json'
    if comparison.exists():
        data=F.load(comparison)
        for row in data:
            if '051_reviews' in row:row['current_batch_reviews']=row.pop('051_reviews')
        comparison.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    tasks=F.load(OUT/'task_statistics.json');calls=F.load(OUT/'call_statistics.json')
    for task in tasks:
        known={r['call'] for r in task['reviews']}
        task['unavailable_review_calls']=[{'call':c['call'],'tag':c['tag'],'status':c['status'],'premises_count':None,
            'literal_target_count':None,'fewer':None,'reason_source':'No readable reviewer output; no model reason is invented.'}
            for c in calls if c['task']==task['task'] and c['type']=='method1' and c['call'] not in known]
    derived(OUT/'task_statistics.json',tasks)
    totals=aggregate(tasks,calls)
    # 051 hardcodes the first-batch planned count as 10. Replace only the newly
    # generated 052 summary with the generic aggregate; no old artifact is edited.
    derived(OUT/'aggregate_statistics.json',totals)
    all_tasks=F.load(OLD/'task_statistics.json')+tasks
    by_task={t['task']:t for t in all_tasks};all_tasks=[by_task[t] for t in F.load(OUT/'selection.json')['all']]
    all_calls=sorted(F.load(OLD/'call_statistics.json')+calls,key=lambda c:c['started_at'])
    all_quotes=F.load(OLD/'quote_checks.json')+F.load(OUT/'quote_checks.json')
    all_formats=F.load(OLD/'format_issues.json')+F.load(OUT/'format_issues.json')
    combined=OUT/'combined_29';combined.mkdir(exist_ok=True)
    for name,value in [('task_statistics.json',all_tasks),('call_statistics.json',all_calls),
        ('aggregate_statistics.json',aggregate(all_tasks,all_calls)),('quote_checks.json',all_quotes),
        ('quote_summary.json',quote_summary(all_quotes)),('format_issues.json',all_formats)]:derived(combined/name,value)
    derived_csv(combined/'call_statistics.csv',all_calls)
    groups=group_inventory(F.load(OUT/'selection.json')['all']);put(OUT/'group_key_inventory_29.json',groups)
    for method in ['method1','method2']:
        put(OUT/f'group_keys_{method}_29.json',groups[method])
        derived_csv(OUT/f'group_keys_{method}_29.csv',groups[method])
    derived(OUT/'analysis_provenance.json',{'time':F.now(),'source_code':'records/051_formal_run.py','source_sha256':SOURCE_SHA,
        'batch_19_analysis':'Original 051 analyze(), selected-task accessor adapted in memory; new planned count corrected to 19.',
        'all_29':'Unredacted 051 statistics plus unredacted 052 statistics; same quote helpers. No old files changed.',
        'group_definition':'All contract table names, not just sections used by method2; no group expansion or ranking.',
        'gold_or_047_content_parsed_or_compared':False,'checksum_only_reads_include_047':True,'judges_called':False})
    print(json.dumps({'event':'analyzed_19_and_29','batch19':totals,'all29':aggregate(all_tasks,all_calls),'group_key_counts':groups['counts']},ensure_ascii=False),flush=True)


def verify():
    source_check();F.load_prepared();checks=Counter();state=F.load(OUT/'start_state.json')
    for path,digest in state['tracked_file_sha256'].items():
        assert F.sha((ROOT/path).read_bytes())==digest,path;checks['existing_tracked_files_unchanged']+=1
    for path,digest in F.load(OUT/'protected_051_private_hashes.json').items():
        assert F.sha((ROOT/path).read_bytes())==digest,path;checks['051_private_files_unchanged']+=1
    selected=F.load(OUT/'selection.json')['remaining'];records=F.records_all();by_tag={r['tag']:r for r in records}
    assert all(r['task'] in selected and r['kind'] in ['method1','method1_final','method2'] for r in records)
    first=min((r['started_at'] for r in records),default=None);supp=source_check()
    if first:assert datetime.fromisoformat(first)>datetime.fromisoformat(supp['time'])
    for task in selected:
        folder=OUT/'tasks'/task;ledger=[]
        for call in F.A.manifest(task)['calls']:
            if call['kind']=='final':continue
            record=by_tag.get(f'{task}_method1_{call["call"]}')
            if not record:continue
            assert F.load(folder/f'ledger_before_call_{call["call"]}.json')==ledger
            if record.get('request_path'):
                expected=F.assembled(task,call['call'],ledger=ledger);path=ROOT/record['request_path']
                assert F.load(path)['json']['input'].encode()==expected.encode()
                assert path.with_name('assembled_prompt.txt').read_bytes()==expected.encode()
                assert F.sha(expected.encode())==record['prompt_sha256'];checks['byte_exact_review_inputs']+=1
            if record['parse_success']:
                added,_,fewer=F.ledger_additions(F.parsed_value(record),call['call']);ledger.extend(added)
                assert F.load(folder/f'fewer_call_{call["call"]}.json')['fewer']==fewer
            assert F.load(folder/f'ledger_after_call_{call["call"]}.json')==ledger
        if (folder/'ledger_all.json').exists():assert F.load(folder/'ledger_all.json')==ledger
        for kind in ['method1_final','method2']:
            record=by_tag.get(f'{task}_{kind}')
            if not record or not record.get('request_path'):continue
            expected=F.assembled(task,final_rank=kind=='method1_final',method2=kind=='method2',ledger=ledger if kind=='method1_final' else None)
            assert F.load(ROOT/record['request_path'])['json']['input'].encode()==expected.encode();checks['byte_exact_final_inputs']+=1
    for record in records:
        if not record.get('request_path'):checks['local_assembly_failure']+=1;continue
        request=F.load(ROOT/record['request_path']);body=request['json']
        assert request['url']=='https://api.openai.com/v1/responses'
        assert set(body)=={'model','input','reasoning','max_output_tokens'}
        assert body['model']==F.MODEL and body['reasoning']=={'effort':'medium','summary':'auto'} and body['max_output_tokens']==32000
        checks['unchanged_model_parameters']+=1
        if record['api_success']:
            raw=F.load(ROOT/record['response_path']);assert F.usage_record(raw,'openai')==record['usage']
            text=F.response_text(raw,'openai');assert F.parse_text(text)==F.load(ROOT/record['parse_path'])
            assert (ROOT/record['response_path']).with_name('text.txt').read_bytes().decode()==text
            checks['raw_response_reconciled']+=1
    if (OUT/'group_key_inventory_29.json').exists():
        assert group_inventory(F.load(OUT/'selection.json')['all'])==F.load(OUT/'group_key_inventory_29.json')
        checks['group_inventory_all_29_verified']=1
    keys=F.credentials()
    for p in OUT.rglob('*'):
        if p.is_file():assert not any(key in p.read_bytes() for key in keys),str(p)
    if (PUB/'full_archive_manifest.json').exists():
        for item in json.loads((PUB/'full_archive_manifest.json').read_bytes())['files']:
            assert F.sha((ROOT/item['full_path']).read_bytes())==item['sha256']
            assert F.sha((ROOT/item['public_path']).read_bytes())==item['public_sha256'];checks['full_public_hash_pairs']+=1
        for p in PUB.rglob('*'):
            if p.is_file():assert not F.secret_hits(p.read_bytes()) and not any(k in p.read_bytes() for k in keys),str(p)
    result={'time':F.now(),'passed':True,'checks':dict(checks),'first_new_api_call':first,'supplement_commit':supp,
        'new_task_budget_usd':30,'budget_excludes_051_cost':True,'judges_called':False,
        'gold_or_047_content_parsed_or_compared':False,'checksum_only_reads_include_047':True,
        'statistics_basis':str(OUT.relative_to(ROOT))+' plus read-only data/051_formal_run_full for the combined 29.'}
    p=PUB/'verification.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'event':'verified','checks':dict(checks)}),flush=True)


def publish():
    assert (OUT/'batch_remaining_complete.json').exists() or (OUT/'STOP.json').exists()
    assert (OUT/'combined_29/aggregate_statistics.json').exists()
    keys=F.credentials();mapping={}
    previous=ROOT/'data/050_pilot_full/private_sid_mapping.json'
    if previous.exists():
        rows=json.loads(previous.read_bytes())['mapping']
        for row in rows:mapping[row['original'].encode()]=row['placeholder'].encode()
    for old in [OLD/'private_redaction_mapping.json',OUT/'private_redaction_mapping.json']:
        if old.exists():mapping.update({k.encode():v.encode() for k,v in json.loads(old.read_bytes()).items()})
    found=defaultdict(set);excluded={'private_redaction_mapping.json','report_unredacted.md','publication.log'}
    files=[p for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in excluded]
    for p in files:
        b=p.read_bytes();assert not any(key in b for key in keys),str(p)
        for kind,value in F.secret_hits(b):found[kind].add(value)
    for kind,values in sorted(found.items()):
        used=set(mapping.values());n=1
        for value in sorted(values):
            if value in mapping:continue
            while f'[REDACTED_{kind}_{n}]'.encode() in used:n+=1
            placeholder=f'[REDACTED_{kind}_{n}]'.encode();mapping[value]=placeholder;used.add(placeholder);n+=1
    (OUT/'private_redaction_mapping.json').write_text(json.dumps({k.decode():v.decode() for k,v in mapping.items()},ensure_ascii=False,indent=2)+'\n')
    manifest=[];changed=[]
    for p in files:
        raw=p.read_bytes();public=raw;counts={};target=PUB/p.relative_to(OUT)
        for value,placeholder in mapping.items():
            count=public.count(value)
            if count:counts[placeholder.decode()]=count;public=public.replace(value,placeholder)
        assert not F.secret_hits(public) and not any(k in public for k in keys),str(target)
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert target.read_bytes()==public,str(target)
        else:target.write_bytes(public)
        row={'full_path':str(p.relative_to(ROOT)),'public_path':str(target.relative_to(ROOT)),
            'bytes':len(raw),'sha256':F.sha(raw),'public_sha256':F.sha(public)};manifest.append(row)
        if counts:changed.append({**row,'replacements':counts,'total_replacements':sum(counts.values())})
    for name,value in [('full_archive_manifest.json',{'full_archive':str(OUT.relative_to(ROOT)),'git_ignored':True,'files':manifest,
            'old_051_archive':'data/051_formal_run_full (read-only; existing hashes in records/051_formal_run/full_archive_manifest.json)'}),
        ('redaction_manifest.json',{'classes':{k:len(v) for k,v in found.items()},'unique_values':sum(map(len,found.values())),
            'total_replacements':sum(r['total_replacements'] for r in changed),'affected_files':changed,
            'private_mapping':str((OUT/'private_redaction_mapping.json').relative_to(ROOT)),
            'only_matched_value_bytes_replaced':True,'statistics_basis':'Unredacted 051 and 052; no recomputation after redaction.'})]:
        p=PUB/name
        if p.exists():assert json.loads(p.read_bytes())==value
        else:F.dump(p,value)
    print(json.dumps({'event':'published','files':len(files),'replacements':sum(r['total_replacements'] for r in changed),'affected_files':len(changed)}),flush=True)


def report():
    state=F.load(OUT/'start_state.json');supp=source_check();config=F.load(OUT/'runtime_configuration.json')
    tasks=F.load(OUT/'task_statistics.json');all_tasks=F.load(OUT/'combined_29/task_statistics.json')
    calls=F.load(OUT/'call_statistics.json');totals=F.load(OUT/'aggregate_statistics.json');all_totals=F.load(OUT/'combined_29/aggregate_statistics.json')
    groups=F.load(OUT/'group_key_inventory_29.json');redaction=json.loads((PUB/'redaction_manifest.json').read_bytes())
    verification=json.loads((PUB/'verification.json').read_bytes());archive=json.loads((PUB/'full_archive_manifest.json').read_bytes())
    environment=F.load(OUT/'environment.json')
    delivery=json.loads((PUB/'delivery_commit.json').read_bytes()) if (PUB/'delivery_commit.json').exists() else None
    def j(value):return json.dumps(value,ensure_ascii=False,indent=2)
    def cell(value):return str(value).replace('|','\\|').replace('\r','').replace('\n','<br>')
    def table(headers,rows):return '\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(cell(v) for v in row)+' |\n' for row in rows)+'\n'
    def overview(ts):
        rows=[]
        for t in ts:
            a=t['finals']['method1_final'] or {};b=t['finals']['method2'] or {};pa=a.get('coverage_proxy');pb=b.get('coverage_proxy')
            cov=f'{pa["numerator"]}/{pa["denominator"]}；{pb["numerator"]}/{pb["denominator"]}' if pa and pb else ('不可用' if t['benchmark']=='DAComp' else '不适用')
            kb=f'{a.get("krama_aggregate_count")} / {b.get("krama_aggregate_count")}' if t['benchmark']=='KramaBench' else '不适用'
            rows.append([t['task'],'051' if t['task'] in F.load(OUT/'selection.json')['first'] else '052',t['ordinary_calls_recorded'],
                t['ledger_count'],len(t['zero_reviews']),f'{a.get("raw_total")} / {b.get("raw_total")}',kb,cov,t['cost_usd'],t['wall_seconds']])
        return table(['题号','批次','普通叫起','新增前提','零条叫起','最终各键合计 一/二','Krama 合并 一/二','DA 表名出现 一；二','估算 USD','秒'],rows)
    text=['# 小实验正式跑第二批\n\n## 任务\n\n',
        '用未改动的 `records/051_formal_run.py` 和 `records/051_prompts/` 跑完第一批余下的 19 道，保持 v2、medium、summary=auto、max_output_tokens=32000。先原样存档共有前提补充口径并单独提交；不运行裁判，不解析或比对标准答案及 047 的内容，不报告命中，不判断条数是否足够。047 等已有文件仅按字节计算 SHA256 以保护原文件。\n',
        '## 结论\n\n',
        f'第二批执行完 {totals["tasks_completed"]}/19 道的预定流程，共 {totals["calls"]} 次调用，其中 API 成功 {totals["api_success"]} 次、JSON 解析成功 {totals["parse_success"]} 次、截断 {totals["truncated"]} 次。已返回 usage 的第二批估算合计 ${totals["estimated_usd"]:.8f}；29 道合计 ${all_totals["estimated_usd"]:.8f}。失败尝试无 usage 的部分未知，未加进已知合计；均以账单为准。\n',
        f'第二批 {totals["ordinary_calls"]} 次普通叫起中，{totals["ordinary_reviews_with_readable_output"]} 次有可读输出，共取得 {totals["premises_total"]} 条前提，其中零条 {totals["zero_reviews"]} 次；29 道 {all_totals["ordinary_calls"]} 次普通叫起中，{all_totals["ordinary_reviews_with_readable_output"]} 次有可读输出，共取得 {all_totals["premises_total"]} 条，其中零条 {all_totals["zero_reviews"]} 次。其余回合未知，不归零。\n',
        f'29 道的程序候选组名键：做法一 {groups["counts"]["method1"]} 个、做法二 {groups["counts"]["method2"]} 个，按题和原始键计数，名单待 Claude 确认；没有推断组名覆盖哪些表。\n',
        '**全部统计、token、费用、引用核对来自未脱敏的 `data/051_formal_run_full/` 与 `data/052_formal_run_full/`；公开脱敏后不重算。**\n',
        '## 详细发现\n\n### 事先存档、范围和执行方式\n\n',
        f'- 开工 commit：`{state["start_commit"]}`；开工时间 `{state["started_at"]}`。开工最大编号 051，使用 052；交付前复查无他人占用，未顺延。\n',
        f'- 补充口径单独提交：`{supp["commit"]}`，时间 `{supp["time"]}`。原文逐字核对并在首条新 API 调用前提交、推送。首条新调用时间 `{verification["first_new_api_call"]}`。\n',
        '- 补充口径：`notes/052_2026-11-06_小实验统计口径补充（共有前提）.md`；核对记录：`records/052_formal_run/frozen_supplement_source_check.json`。\n',
        '- 新调度脚本 `records/052_formal_run.py` 导入原 051 函数，在内存中只把运行输出根目录改为 052、任务预算改为用户指定的 $30，并修正预算停止标签。保留 F.PUB/F.PROMPTS 指向 051，只读冻结提示词与审计。API 调用、重试、JSON 解析、字节读入、拼装、账本逻辑均由原函数执行；没有改模型参数或任何 047、049、050、051 文件。\n',
        f'- 原 051 脚本 SHA256：`{config["script_051_sha256"]}`。重新核对 367 份空账本输入字节哈希及 32 个 Excel 预览块、10,921 个格子，全部通过。\n',
        f'- SDK：OpenAI `{environment["openai_sdk"]}`；tiktoken `{environment["tiktoken"]}`，与 051 相同。\n',
        '- 19 道范围（沿用 051 未跑名单及其顺序）：'+', '.join(config['selected_tasks'])+'。\n',
        f'- 预计 {config["planned_calls"]} 次调用。预算只累计本任务，排除 051 的费用；停止条件仍为认证失败、模型名被拒、本任务估算超过 $30。\n',
        '### 统计口径\n\n',
        '- 与 051 一致：普通叫起的 target 按完整字符串区分；全部成功条目按 c<叫起>-<条目> 编 id 并追加账本，不因 updates 删旧项，fewer 单独保存。最终清单按模型键计条目出现次数；同一 id 在多个键下出现仍分别计，另列位置，不作语义去重。\n',
        '- DAComp “agent 写过的表”仍是做法二所用契约节表名的机械近似，模型键去 schema、转小写后完全相同才算出现。空列表键也计出现，同时记录非空比例。这不是组名对表的覆盖判断。\n',
        '- KramaBench 按 051：单键保留；多键合并按 importance 降序、键序、键内序取前 10，同时保留原始各键条数。\n',
        '- 新组名口径仅用于列名单：DAComp 最终返回键按 051 的 `rsplit(".",1)[-1].lower()` 规范化，与该题**全部**契约表名比对；不相等的列为候选组名。20 道 DAComp 共 774 个契约表名均为小写且不带 schema；KramaBench 9 道不适用。没有把组条目分配给表、追加到单表清单或调整排名。\n',
        '- 未取得返回或无法解析的最终清单记为未知，单独列在 unavailable_final_outputs，条数合计只加已有输出；组名无法枚举时 per_task.group_keys 为 null，不当作没有组名。\n',
        '- 表名出现比例的合计沿用 051 代码，只对具有可用 coverage_proxy 的最终对象加总；存在缺失输出时这是可用子集的描述数，完整范围的比例未知，不能把缺失理解为未出现。是否补跑缺失项交用户和 Claude 决定。\n',
        '- 第二批计数/引用检查调用原 051 analyze() 及其助手，只适配分析任务选择；新文件中原函数写死的计划题数 10 改记为 19。29 道合计按第一批完整统计与本批完整统计机械加总。所有原始请求和返回保持不变。\n',
        '### 第二批 19 道合计\n\n',f'```json\n{j(totals)}\n```\n',overview(tasks),
        '### 全部 29 道合计\n\n',f'```json\n{j(all_totals)}\n```\n',overview(all_tasks),
        '第一批逐次 fewer 原文仍见 051 报告；全部 29 道的逐次内容同时在 `records/052_formal_run/combined_29/task_statistics.json` 中。\n',
        '### 第二批每道题的逐次条数、target、fewer 原文和最终清单\n\n']
    for t in tasks:
        text.append(f'#### {t["task"]}\n\n普通叫起计划 {t["ordinary_calls_planned"]} 次、记录 {t["ordinary_calls_recorded"]} 次；账本 {t["ledger_count"]} 条；用时 {t["wall_seconds"]} 秒；估算 ${t["cost_usd"]:.8f}。\n')
        rows=[];known={r['call']:r for r in t['reviews']};manifest=F.A.manifest(t['task'])
        for c in [c for c in calls if c['task']==t['task'] and c['type']=='method1']:
            r=known.get(c['call']);rules=next(x['rules'] for x in manifest['calls'] if x['call']==c['call'])
            rows.append([c['call'],','.join(rules),r['premises_count'] if r else '未知',r['literal_target_count'] if r else '未知',r['zero_items'] if r else '未知'])
        text.append(table(['叫起','规则','条数','不同 target','零条'],rows))
        text.append('每次的 target 计数与 fewer 全部原文（包括零条叫起的理由，原值为空时保留为空）：\n```json\n'+j([{'call':r['call'],'target_counts':r['target_counts'],'fewer':r['fewer'],'zero_items':r['zero_items']} for r in t['reviews']])+'\n```\n')
        if t.get('unavailable_review_calls'):text.append('无可读返回的回合（fewer 未知，不代写模型理由；后续账本按原规则保持不变并继续）：\n```json\n'+j(t['unavailable_review_calls'])+'\n```\n')
        for kind,label in [('method1_final','做法一交卷重排'),('method2','做法二')]:
            final=t['finals'][kind];text.append(f'**{label}**\n\n')
            if not final:text.append('无调用记录。\n');continue
            text.append(table(['返回键','原始条数','id 回查后/实际条数'],[[key,n,final.get('resolved_key_counts',{}).get(key)] for key,n in final['raw_key_counts'].items()]))
            if kind=='method2':
                if 'raw_total' in final:text.append('fewer_reason 原文：\n```json\n'+j(final['fewer_reasons'])+'\n```\n')
                else:text.append('未取得可用的最终对象，fewer_reason 未知。\n')
            if 'coverage_proxy' in final:text.append('表名出现的机械近似统计：\n```json\n'+j(final['coverage_proxy'])+'\n```\n')
            elif t['benchmark']=='KramaBench':text.append(f'KramaBench 按 051 规则合并后为 {final["krama_aggregate_count"]} 条；各键原始合计 {final.get("raw_total")} 条。\n')
            else:text.append('最终对象不可用，表名出现比例未知。\n')
            if final.get('repeated_ledger_id_occurrences'):text.append('同一 id 的重复出现位置（只记录）：\n```json\n'+j(final['repeated_ledger_id_occurrences'])+'\n```\n')
            if final['unknown_ids'] or final['issues']:text.append('技术异常，交 Claude：\n```json\n'+j({'unknown_ids':final['unknown_ids'],'issues':final['issues']})+'\n```\n')
    text+=['### 29 道的全部候选组名键\n\n',
        '以下只列原始键、规范化值和键下条目数，不推断它们覆盖哪些表。只对 DAComp 适用，KramaBench 排除。做法一计交卷返回的 id 条目数，做法二计 items 的长度；无法取得数组时记未知并保留格式问题。\n']
    for method,label in [('method1','做法一'),('method2','做法二')]:
        text.append(f'**{label}**\n\n')
        text.append(table(['题号','原始组名键','规范化值','条目数'],[[g['task'],g['key'],g['normalized_key'],g['item_count']] for g in groups[method]]))
    text+=['枚举状态（含无组名的 DAComp 题）：\n```json\n'+j(groups['per_task'])+'\n```\n',
        '多点号规范化边界原样列出，不作 schema 或覆盖解释：\n```json\n'+j(groups['normalization_boundary_cases'])+'\n```\n',
        '### 每次调用的状态、用量和费用\n\n',
        '费用估算沿用 051：每百万未缓存输入 $2、缓存输入 $0.10、输出 $10；输出含 reasoning，不再重复计费。超过 272,000 输入 token 标价格待核。缓存 token 属于输入、推理 token 属于输出；失败尝试缺少 usage，不称为免费。完整响应含原始 reasoning 条目和摘要。\n']
    text.append(table(['题号/类型/次','API/解析/完成','截断/尝试','输入/缓存','输出/推理','缓存比例','实际/o200k','估算 USD','秒','摘要'],[
        [f'{c["task"]}/{c["type"]}/{c["call"]}',f'{c["api_success"]}/{c["parse_success"]}/{c["completed"]}',f'{c["truncated"]}/{c["attempts"]}',
         f'{c["input_tokens"]}/{c["cached_input_tokens"]}',f'{c["output_tokens"]}/{c["reasoning_tokens"]}',c['cached_input_fraction'],c['actual_input_to_current_o200k_ratio'],c['estimated_usd'],c['wall_seconds'],c['has_reasoning_summary_text']] for c in calls]))
    errors=[{'tag':r['tag'],**a} for r in F.records_all() for a in r['attempts'] if not a['success']]
    text+=[f'本批 {len(calls)} 个调用回合共记录 {sum(c["attempts"] for c in calls)} 次 HTTP 尝试，其中 {len(errors)} 次失败尝试；两次最终无返回的回合在状态表中单独列出。\n',
        '失败尝试原样记录：\n```json\n'+j(errors)+'\n```\n',
        '长输入、价格待核的调用：\n```json\n'+j([c['tag'] for c in calls if c['long_input_price_unverified']])+'\n```\n',
        '### 引用核对和格式检查\n\n',
        '口径与 051 一致：evidence_of_dependence、evidence_in_work 整栏查对应实际完整输入；alternative、source 只查 json.loads 后文字内部的引号片段，JSON 外围引号不算，沿用 ASCII 单/双引号、弯引号、反引号和代码块的机械提取。没有内部引号记“未给出原文”，null 不适用。完全逐字与连续 Unicode 空白压成一个空格两种口径并列，不修复大小写、拼写、省略号；另报该字段全部片段都找到的数量。\n',
        '第二批 19 道：\n```json\n'+j(F.load(OUT/'quote_summary.json'))+'\n```\n',
        '全部 29 道：\n```json\n'+j(F.load(OUT/'combined_29/quote_summary.json'))+'\n```\n',
        '第二批格式异常原样列出：\n```json\n'+j(F.load(OUT/'format_issues.json'))+'\n```\n',
        '逐条引用与原文在 `quote_checks.json`，29 道在 `combined_29/quote_checks.json`。字符串存在与否不作为语义判断。\n',
        '### 完整版、脱敏和文件 SHA256\n\n',
        '`data/052_formal_run_full/` 为本批完整版，git 忽略；公开版 `records/052_formal_run/`。第一批完整数据仍在 `data/051_formal_run_full/`，只读。全部统计以完整版本为准。\n',
        f'本批公开文件替换 {redaction["total_replacements"]} 处，涉及 {len(redaction["affected_files"])} 个文件、{redaction["unique_values"]} 个不同值；同值沿用同一占位符，包括既有 050/051 映射。只替换匹配字符串，原值映射只在 data/。\n',
        '替换清单：\n```json\n'+j(redaction['affected_files'])+'\n```\n',
        '每个完整请求、原始 JSON 返回、HTTP 正文和 SDK 返回的路径、SHA256 在 `records/052_formal_run/full_archive_manifest.json`。第一批仍见 `records/051_formal_run/full_archive_manifest.json`。\n',
        '复核结果：\n```json\n'+j(verification)+'\n```\n',
        '原始轨迹含尾空白、CRLF 和末尾空行，按字节保留；Git 空白检查只针对脚本与报告，归档依据字节/SHA256 检查。\n',
        '## 证据来源\n\n',
        '- 原执行代码及提示词：`records/051_formal_run.py`、`records/051_prompts/`；原输入与拼装：`records/049_small_exp_inputs/`、`records/049_small_exp_assemble.py`。\n',
        '- 本批调度与分析：`records/052_formal_run.py`；配置 `runtime_configuration.json`、审计 `verification.json`、合并统计 `combined_29/`、组名 `group_keys_method1_29.json/.csv` 与 `group_keys_method2_29.json/.csv`。\n',
        '- 准备、调用和分析均用 `/tmp/assumption-ledger-050-venv/bin/python`，tokenizer cache `/tmp/assumption-ledger-048-tiktoken-cache`；SDK 版本见 `environment.json`。\n',
        '```bash\npython records/052_formal_run.py prepare\npython records/052_formal_run.py run\npython records/052_formal_run.py analyze\npython records/052_formal_run.py publish\npython records/052_formal_run.py verify\npython records/052_formal_run.py report\n```\n',
        '## 不确定或没查到的\n\n',
        '- 候选组名名单交 Claude 确认，未推断任何组名覆盖的表，未构建裁判附加清单或改变原排名。多点号字符串的规范化仍按 051 的字面规则，相关原文已列。\n',
        '- 复合 target、别名、同一 id 的跨键重复及字段/格式问题均保留原样，不作语义归并。\n',
        '- 引用的纯字符串检查不能确认语义支持；无内部引号按指定口径记“未给出原文”。费用未核账，失败尝试无 usage 的部分未知。\n',
        '## 建议的下一步\n\n请用户和 Claude 确认候选组名；前提句复核完成后再安排裁判与抽查。本任务止于被测模型调用和机械统计。\n']
    if (OUT/'STOP.json').exists():text.append('停止记录：\n```json\n'+j(F.load(OUT/'STOP.json'))+'\n```\n')
    if delivery:text.append(f'交付产物 commit：`{delivery["commit"]}`，时间 `{delivery["time"]}`；本报告的提交在其后。\n')
    hashes={item['full_path']:item['sha256'] for item in archive['files']};paths=[]
    for r in F.records_all():
        files=[('完整请求',r.get('request_path')),('原始返回 JSON',r.get('response_path'))]
        if r.get('response_path'):
            p=Path(r['response_path']);files.append(('HTTP 正文',str(p.with_name(p.stem+'_body.txt'))))
        for label,path in files:
            if path:paths.append([r['tag'],label,path,hashes[path]])
    at=text.index('## 证据来源\n\n');text.insert(at,'本批完整请求与原始返回的路径和 SHA256：\n'+table(['调用','类型','完整路径','SHA256'],paths))
    full=''.join(text).encode();public=full;replacements={}
    for value,placeholder in F.load(OUT/'private_redaction_mapping.json').items():
        n=public.count(value.encode())
        if n:replacements[placeholder]=n;public=public.replace(value.encode(),placeholder.encode())
    assert not F.secret_hits(public) and not any(k in public for k in F.credentials())
    private=OUT/'report_unredacted.md';private.write_bytes(full)
    # This report belongs to the task begun on 2026-11-06, even if it spans UTC
    # midnight; actual API timestamps and the report generation time are retained.
    target=ROOT/'notes/052_2026-11-06_小实验正式跑第二批.md';target.write_bytes(public)
    meta={'generated_at':F.now(),'full_path':str(private.relative_to(ROOT)),'sha256':F.sha(full),
        'public_path':str(target.relative_to(ROOT)),'public_sha256':F.sha(public),'replacements':replacements,
        'statistics_basis':'Unredacted 051 and 052; publication replaces matched literal values only.'}
    (PUB/'report_archive_manifest.json').write_text(j(meta)+'\n')
    print(json.dumps({'event':'report_written','path':str(target.relative_to(ROOT)),'bytes':len(public)}),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','run','analyze','verify','publish','report'])
    args=p.parse_args();globals()[args.command]()


if __name__=='__main__':main()
