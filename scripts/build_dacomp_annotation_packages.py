"""Build 30 verbatim task 012 pilot packages, without replaying any agent SQL."""

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from complete_dacomp_comparisons import ROOT, RECORDS, PROJECT, PYTHON, save, stamp
from dacomp_annotation_evidence import Evidence
from dacomp_sql_extract import contract_blocks
from prepare_dacomp_annotation import EXPORT, ARCHIVE, indices
from reconcile_dacomp_scope import key, jsonl
from scan_dacomp_delivery import sentence_units, json_strings


def source_text(path):
    path=Path(path);raw=path.read_bytes();text=raw.decode('utf-8')
    return {'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'start_line':1,
            'end_line':len(text.splitlines()),'text':text}


def gold_sql_paths(scan,case):
    root=Path(case['gold_database']).parent/'sql'
    names={scan['table'],scan['logical_contract_table']}
    return sorted({p for name in names for p in root.rglob(name+'.sql') if any(part in (scan['layer'],'mart' if scan['layer']=='marts' else scan['layer']) for part in p.relative_to(root).parts[:-1])})


def field_location(path,trail):
    text=Path(path).read_bytes().decode('utf-8')
    for actual,value,start,end in json_strings(text):
        if actual==trail:
            return {'file':str(path),'json_path':trail,'file_line':text.count('\n',0,start)+1,
                    'json_string_token_start_offset':start,'decoded_characters':len(value)}
    return {'file':str(path),'json_path':trail,'field_not_found':True}


def trace_steps(task,table,sources):
    root=EXPORT/'runs/20261025_de_official_batch_01'/task/'agent'
    eventfiles=sorted(root.glob('.events/sessions/*/events/*.json'))
    events=[(p,json.loads(p.read_text())) for p in eventfiles]
    bycause=defaultdict(list)
    for p,e in events:
        if 'observation' in e:bycause[e.get('cause')].append((p,e))
    sidecar=list(root.glob('sidecar/*/commands.jsonl'));sequences={}
    for path in sidecar:
        for line in path.read_text().splitlines():
            row=json.loads(line)
            if row.get('agent_command_sequence') is not None:sequences[row['event_id']]=row['agent_command_sequence']
    names=sorted({name for source in sources for name in (source,source.split('.')[-1])},key=lambda x:(-len(x),x))
    def hits(text,terms):
        return [name for name in terms if re.search(r'(?<![A-Za-z0-9_])'+re.escape(name)+r'(?![A-Za-z0-9_])',text,re.I)]
    steps=[]
    for path,e in sorted(events,key=lambda item:item[1].get('id',-1)):
        if e.get('action')!='run':continue
        command=e.get('args',{}).get('command') or ''
        obs=sorted(bycause[e['id']],key=lambda item:item[1].get('id',-1))
        combined='\n'.join([command]+[o.get('content','') for p,o in obs])
        target=hits(combined,[table]);matched=hits(combined,names)
        if not target and not matched:continue
        output=[]
        for op,o in obs:
            content=o.get('content','');metadata=o.get('extras',{}).get('metadata',{})
            explicit={k:v for k,v in metadata.items() if 'truncat' in k.lower() or 'clip' in k.lower()}
            markers=[line for line in content.splitlines() if re.fullmatch(r'\[.*(?:Observation truncated due to length|response clipped|output truncated).*\]',line,re.I)]
            output.append({'event_id':o['id'],'observation':o.get('observation'),'location':field_location(op,['content']),
                'archive_member':'dacomp_deimpl_prev/'+op.relative_to(EXPORT).as_posix(),
                'content':content,'truncation':{'explicit_metadata_flags':explicit,'marker_lines':markers,
                    'status':'原记录显式截断' if markers or any(v is True for v in explicit.values()) else '未见显式截断标记'},
                'exit_code':metadata.get('exit_code')})
        steps.append({'event_id':e['id'],'agent_command_sequence':sequences.get(e['id']),
            'action_location':field_location(path,['args','command']),'archive_member':'dacomp_deimpl_prev/'+path.relative_to(EXPORT).as_posix(),
            'timestamp':e.get('timestamp'),'target_table_name_hits':target,'source_table_name_hits':matched,
            'command':command,'outputs':output,'full_original_characters':len(command)+sum(len(o['content']) for o in output),
            'retention':'full_original'})
    total=sum(s['full_original_characters'] for s in steps);indexed=0
    if total>60000:
        for step in steps:
            if step['target_table_name_hits']:continue
            first=step['command'].splitlines(keepends=True)
            step['first_line_original']=first[0] if first else (step['outputs'][0]['content'].splitlines(keepends=True) or [''])[0] if step['outputs'] else ''
            step.pop('command')
            for output in step['outputs']:output.pop('content')
            step['retention']='index_and_first_line_only';indexed+=1
    return {'archive':str(ARCHIVE),'event_source_root':str(root),'actual_read_sources_from_008_B7':sources,
        'name_match_policy':'Case-insensitive complete identifier-name boundaries; source names include qualified form and bare leaf name. No semantic association inferred.',
        'matched_step_count':len(steps),'full_original_characters_before_budget':total,'budget_triggered':total>60000,
        'source_only_steps_indexed':indexed,'retained_full_original_characters':sum(s['full_original_characters'] for s in steps if s['retention']=='full_original'),
        'full_target_steps_exceed_60000':sum(s['full_original_characters'] for s in steps if s['target_table_name_hits'])>60000,
        'budget_policy':'If total command/output text exceeds 60000 characters, keep every target-table step complete and retain only id/location/first line for source-only steps. Do not rewrite or truncate a kept original step.',
        'steps':steps}


def result_sentences(task,table,keyword_records):
    root=EXPORT/'runs/20261025_de_official_batch_01'/task/'agent'/f'dacomp-de-{task}'
    candidates=sorted(root.rglob('result.md'))
    if not candidates:return {'present':False,'searched_root':str(root),'searched_glob':'**/result.md','sentences':[]}
    assert len(candidates)==1,('Multiple final result.md files; retain sources separately',task,candidates)
    path=candidates[0]
    text=path.read_bytes().decode('utf-8');sentences=[]
    for value,start,end in sentence_units(text):
        if re.search(r'(?<![A-Za-z0-9_])'+re.escape(table)+r'(?![A-Za-z0-9_])',value,re.I):
            sentences.append({'original_text':value,'path':str(path),'start_offset':start,'end_offset':end,
                'start_line':text.count('\n',0,start)+1,'end_line':text.count('\n',0,end)+1,
                'matching_008_D10_excerpt_ids':[r['excerpt_id'] for r in keyword_records if r['task']==task and r['origin']=='result_md_final_report' and r['original_text']==value]})
    return {'present':True,'path':str(path),'archive_member':'dacomp_deimpl_prev/'+path.relative_to(EXPORT).as_posix(),
        'sha256':hashlib.sha256(text.encode()).hexdigest(),'sentences':sentences,
        'policy':'All sentences naming the table; includes sentences without 008 keywords. Existing D10 ids attached where applicable.'}


def fence(text,kind='text'):
    runs=re.findall(r'`+',text);ticks='`'*max(3,1+max(map(len,runs),default=0))
    return ticks+kind+'\n'+text+('' if text.endswith('\n') else '\n')+ticks+'\n'


def render_package(doc):
    """Render every JSON field; raw contract/SQL/commands/outputs remain verbatim."""
    out=['# '+doc['basic_information']['task']+' / '+doc['basic_information']['table']+'\n']
    for label,value in doc.items():
        out.append('\n## '+label+'\n\n')
        if label=='contract_specification':
            out.append(fence(json.dumps({k:v for k,v in value.items() if k!='blocks'},ensure_ascii=False,indent=2),'json'))
            for block in value['blocks']:
                out.append(fence(json.dumps({k:v for k,v in block.items() if k!='original_text'},ensure_ascii=False,indent=2),'json'))
                out.append(fence(block['original_text'],'yaml'))
        elif label in ('agent_final_SQL','gold_SQL_仅供定位差异'):
            for source in value:
                out.append(fence(json.dumps({k:v for k,v in source.items() if k!='text'},ensure_ascii=False,indent=2),'json'))
                out.append(fence(source['text'],'sql'))
            if not value:out.append('未找到；查找位置在 original_files。\n')
        elif label=='trace_excerpts':
            out.append(fence(json.dumps({k:v for k,v in value.items() if k!='steps'},ensure_ascii=False,indent=2),'json'))
            for step in value['steps']:
                out.append('\n### event '+str(step['event_id'])+'\n\n')
                out.append(fence(json.dumps({k:v for k,v in step.items() if k not in ('command','outputs')},ensure_ascii=False,indent=2),'json'))
                if 'command' in step:out.append(fence(step['command'],'bash'))
                for output in step['outputs']:
                    out.append(fence(json.dumps({k:v for k,v in output.items() if k!='content'},ensure_ascii=False,indent=2),'json'))
                    if 'content' in output:out.append(fence(output['content']))
        else:out.append(fence(json.dumps(value,ensure_ascii=False,indent=2),'json'))
    return ''.join(out)


def worker(task,work):
    states={key(r['task'],r['layer'],r['table']):r for r in jsonl(RECORDS/'012_statuses.jsonl')}
    sample=next(r for r in json.loads((RECORDS/'012_sampling.json').read_text())['samples'] if r['task']==task)
    identity=key(task,sample['layer'],sample['table']);state=states[identity];scan=indices()[1][identity];basis=state['difference_basis']
    case=json.loads((RECORDS/f'006_contract_{task}.json').read_text())
    constraint=next(r for r in case['tables'] if key(task,r['layer'],r['table'])==identity)
    contract=contract_blocks(case['contract']['path'],scan['logical_contract_table'])
    for b in contract['blocks']:b.pop('specification',None)
    agent=[source_text(p) for p in scan['inventory_sources']['agent_final_sql_files']]
    gold=[source_text(p) for p in gold_sql_paths(scan,case)]
    difference={**basis,'value_representation':'Unmodified DuckDB CAST AS VARCHAR; SQL NULL is JSON null. Keys use the unchanged historical L0 normalization.',
        'new_queries_only_read_existing_results':True}
    with Evidence(basis,work/'evidence') as evidence:
        difference['one_side_key_examples']=evidence.exclusive_examples(10)
        difference['column_details']=[]
        for col in basis['l0_column_differences']:
            name=col['column'];samples=[];counts=None
            if col['mismatch_rows_or_minimum_pairs'] or col['pred_unmatched_value_occurrences'] or col['gold_unmatched_value_occurrences']:
                counts,samples=evidence.value_examples(name,0,5)
                for k,v in counts.items():assert col[k]==v,(task,basis['table'],name,k,v,col[k])
            difference['column_details'].append({'column':name,'l0_counts_verbatim':col,
                'l3_counts_verbatim':next((c for c in basis['l3_column_differences'] or [] if c['column']==name),None),
                'sample_level':'L0','sample_key_groups':samples,'sample_counts_recheck':counts,
                'agent_actual_type':evidence.types['p'].get(name),'gold_actual_type':evidence.types['g'].get(name)})
    trace=trace_steps(task,state['table'],scan['source_comparison']['agent_direct_read_sources'])
    sentences=result_sentences(task,state['table'],jsonl(RECORDS/'008_keyword_excerpts.jsonl'))
    original_paths=sorted({case['contract']['path'],basis['prediction_database'],basis['gold_database'],
        *scan['inventory_sources']['agent_final_sql_files'],*[s['path'] for s in gold],
        *[s['action_location']['file'] for s in trace['steps']],*[o['location']['file'] for s in trace['steps'] for o in s['outputs']],
        *([sentences['path']] if sentences['present'] else [])})
    doc={'basic_information':{'task':task,'layer':state['layer'],'table':state['table'],'status':state['status'],
            'difference_source':{k:basis[k] for k in ('kind','record','detail_record','candidate_date','selection_reason')},
            'status_record':'records/012_statuses.jsonl','package_scope':'仅原文和机械统计；未概括轨迹、未推测原因'},
        'contract_specification':contract,'agent_final_SQL':agent,'gold_SQL_仅供定位差异':gold,
        'differences':difference,'agent_constraints_006':{'source_record':f'records/006_contract_{task}.json',
            'declarations':constraint['declarations'],'agent':constraint['agent']},
        'all_markers_and_evidence_008':{'source_record':'records/008_table_scan.jsonl','verbatim_record':scan},
        'trace_excerpts':trace,'result_md_table_sentences':sentences,
        'original_files':{'paths':original_paths,'archive':str(ARCHIVE),
            'gold_SQL_search_root':str(Path(case['gold_database']).parent/'sql'),
            'gold_SQL_search_names':[state['table'],scan['logical_contract_table']],
            'source_fingerprints':'records/012_input_before.json'}}
    stem=sample['package_stem'];save(work/(stem+'.json'),doc)
    md=render_package(doc);(work/(stem+'.md')).write_text(md)
    save(work/'summary.json',{'task':task,'layer':state['layer'],'table':state['table'],'stem':stem,
        'markdown_characters':len(md),'json_characters':len((work/(stem+'.json')).read_text()),
        'trace_original_characters':trace['full_original_characters_before_budget'],
        'trace_kept_full_characters':trace['retained_full_original_characters'],'trace_step_count':trace['matched_step_count'],
        'source_only_steps_indexed':trace['source_only_steps_indexed'],'full_target_steps_exceed_60000':trace['full_target_steps_exceed_60000'],
        'contract_blocks':len(contract['blocks']),'agent_SQL_files':len(agent),'gold_SQL_files':len(gold),
        'result_md_present':sentences['present']})


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker');parser.add_argument('--case',type=Path);args=parser.parse_args()
    if args.worker:worker(args.worker,args.case);return
    sys.path.insert(0,str(PROJECT/'src'));from safe_env import scrubbed_env
    samples=json.loads((RECORDS/'012_sampling.json').read_text())['samples'];destination=RECORDS/'012_packages';destination.mkdir(exist_ok=True)
    def run(sample):
        stem=sample['package_stem'];task=sample['task'];work=ROOT/'data/012_packages_work'/task;index=1
        while work.exists():work=ROOT/'data/012_packages_work'/f'{task}_{index:02d}';index+=1
        work.mkdir(parents=True);(work/'.tmp').mkdir()
        command=[shutil.which('bwrap'),'--ro-bind','/','/','--tmpfs','/home/katherine','--ro-bind',str(PROJECT),str(PROJECT),
            '--ro-bind',str(ROOT),str(ROOT),'--bind',str(work),str(work),'--bind',str(work/'.tmp'),'/tmp',
            '--unshare-pid','--proc','/proc','--dev','/dev','--unshare-net','--die-with-parent','--chdir',str(work),'--',
            str(PYTHON),'-B',str(Path(__file__).resolve()),'--worker',task,'--case',str(work)]
        environment=scrubbed_env();environment.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'data/005_tools'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        with (RECORDS/f'012_package_execution_{task}.log').open('w') as log:done=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT,timeout=7200)
        if done.returncode:raise RuntimeError(task+' package failed; inspect execution log')
        for suffix in ('.json','.md'):shutil.copyfile(work/(stem+suffix),destination/(stem+suffix))
        summary=json.loads((work/'summary.json').read_text());summary.update(command=command,private_directory=str(work))
        print(task,'package complete',summary['markdown_characters'],'characters',flush=True);return summary
    with ThreadPoolExecutor(max_workers=2) as pool:results=[f.result() for f in as_completed([pool.submit(run,s) for s in samples])]
    save(RECORDS/'012_package_inventory.json',sorted(results,key=lambda r:r['task']))


if __name__=='__main__':main()
