"""Task 012: quote contract/type evidence for the 19 L1/L2 format tables."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from complete_dacomp_comparisons import ROOT,RECORDS,PROJECT,PYTHON,save,stamp
from dacomp_annotation_evidence import Evidence
from dacomp_trace_scan import contract_index,column_contract,layer_key
from prepare_dacomp_annotation import indices
from reconcile_dacomp_scope import key,jsonl

PRECISION=re.compile(r'\b(?:round(?:ed|ing)?|precision|scale|format(?:ting|ted)?|cast|decimal\s+places?|digits)\b|(?:decimal|numeric|number)\s*\(\s*\d+\s*,|小数|精度|舍入|格式',re.I)


def worker(number,work):
    states=[r for r in jsonl(RECORDS/'012_statuses.jsonl') if r['status']=='格式差异（待核契约）']
    row=sorted(states,key=lambda r:(r['task'],r['layer'],r['table']))[number]
    identity=key(row['task'],row['layer'],row['table']);source_indices=indices();scan=source_indices[1][identity];basis=row['difference_basis']
    original_tolerance=source_indices[4][identity][0]
    case=json.loads((RECORDS/f"006_contract_{row['task']}.json").read_text())
    contract,mode=contract_index(case['contract']['path'])
    blocks=contract.get((layer_key(row['layer']),scan['logical_contract_table'].lower()),[])
    result={'task':row['task'],'layer':row['layer'],'table':row['table'],'status':'格式差异（待核契约）',
        'whole_match_level_original':basis['whole_match_level'],'difference_basis':basis,
        'original_L0_flags':{k:original_tolerance.get(k) for k in ('baseline_l0_whole_match','l0_exact_row_tuple_match','l0_readonly_official_recheck','keyed_match_level')},
        'contract_path':case['contract']['path'],'contract_parse_mode':mode,'columns':[],
        'sampling_policy':'Fixed historical L0 keys; up to 5 shared-key groups. Raw values are DuckDB CAST AS VARCHAR without trim/case/numeric normalization.',
        'interpretation':'仅摘录类型、契约和机械差异，不判断是否违反契约'}
    with Evidence(basis,work/'evidence') as evidence:
        for column in basis['comparison_columns']:
            zero=evidence.make_histogram(column,0)
            if not(zero['pred_unmatched_value_occurrences'] or zero['gold_unmatched_value_occurrences']):continue
            first=evidence.make_histogram(column,1)
            second=evidence.make_histogram(column,2)
            cleared='L1' if not(first['pred_unmatched_value_occurrences'] or first['gold_unmatched_value_occurrences']) else 'L2' if not(second['pred_unmatched_value_occurrences'] or second['gold_unmatched_value_occurrences']) else None
            old=next(c for c in basis['l0_column_differences'] if c['column']==column)
            for k,v in zero.items():assert v==old[k],(row['table'],column,k,v,old[k])
            _,samples=evidence.value_examples(column,0,5)
            spec=column_contract(blocks,column)
            contexts=[]
            for block in blocks:
                for offset,line in enumerate(block['original_text'].splitlines(keepends=True)):
                    if re.search(r'(?<![A-Za-z0-9_])'+re.escape(column)+r'(?![A-Za-z0-9_])',line,re.I) and PRECISION.search(line):
                        contexts.append({'path':block['path'],'line':block['start_line']+offset,'original_text':line,
                            'association':'同一原文行同时提及列名和 precision/rounding/format/type-conversion 关键词；未判定语句适用范围'})
            result['columns'].append({'column':column,'column_first_cleared_level':cleared,
                'l0_counts':zero,'l1_counts':first,'l2_counts':second,
                'agent_actual_type':evidence.types['p'].get(column),'gold_actual_type':evidence.types['g'].get(column),
                'contract':spec,'contract_has_column_definition':bool(spec['definitions']),
                'contract_has_description':any(bool(d.get('description')) for d in spec['definitions']),
                'column_block_precision_format_mentions':[{'path':d['path'],'start_line':d['start_line'],'end_line':d['end_line'],'original_text':d['original_text']} for d in spec['definitions'] if PRECISION.search(d['original_text'])],
                'table_context_mentions_column_and_precision':contexts,'sample_key_groups':samples})
    result['summary']={'changed_columns':len(result['columns']),
        'column_first_cleared_levels':dict(Counter(c['column_first_cleared_level'] or '未消除' for c in result['columns'])),
        'columns_declared_in_contract':sum(c['contract_has_column_definition'] for c in result['columns']),
        'columns_with_description':sum(c['contract_has_description'] for c in result['columns']),
        'columns_with_column_block_precision_format_text':sum(bool(c['column_block_precision_format_mentions']) for c in result['columns']),
        'columns_with_table_context_precision_mentions':sum(bool(c['table_context_mentions_column_and_precision']) for c in result['columns'])}
    save(work/'result.json',result)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker',type=int);parser.add_argument('--case',type=Path);args=parser.parse_args()
    if args.worker is not None:worker(args.worker,args.case);return
    sys.path.insert(0,str(PROJECT/'src'));from safe_env import scrubbed_env
    states=sorted([r for r in jsonl(RECORDS/'012_statuses.jsonl') if r['status']=='格式差异（待核契约）'],key=lambda r:(r['task'],r['layer'],r['table']))
    assert len(states)==19
    def run(number):
        row=states[number];stem=f"012_format_{row['task']}_{row['layer']}_{row['table']}"
        work=ROOT/'data/012_format_work'/stem;index=1
        while work.exists():work=ROOT/'data/012_format_work'/f'{stem}_{index:02d}';index+=1
        work.mkdir(parents=True);(work/'.tmp').mkdir()
        command=[shutil.which('bwrap'),'--ro-bind','/','/','--tmpfs','/home/katherine','--ro-bind',str(PROJECT),str(PROJECT),
            '--ro-bind',str(ROOT),str(ROOT),'--bind',str(work),str(work),'--bind',str(work/'.tmp'),'/tmp','--unshare-pid',
            '--proc','/proc','--dev','/dev','--unshare-net','--die-with-parent','--chdir',str(work),'--',str(PYTHON),'-B',str(Path(__file__).resolve()),'--worker',str(number),'--case',str(work)]
        environment=scrubbed_env();environment.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'data/005_tools'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
        with (RECORDS/(stem+'.log')).open('w') as log:done=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT,timeout=7200)
        if done.returncode:raise RuntimeError(stem+' failed; inspect log')
        result=json.loads((work/'result.json').read_text());save(RECORDS/(stem+'.json'),result)
        print(row['task'],row['table'],result['summary'],flush=True)
        return result,{'task':row['task'],'table':row['table'],'command':command,'private_directory':str(work)}
    with ThreadPoolExecutor(max_workers=2) as pool:finished=[f.result() for f in as_completed([pool.submit(run,n) for n in range(19)])]
    results=sorted([r[0] for r in finished],key=lambda r:(r['task'],r['layer'],r['table']))
    (RECORDS/'012_format_contracts.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in results))
    save(RECORDS/'012_format_execution.json',[r[1] for r in finished])
    save(RECORDS/'012_format_summary.json',{'created_at':stamp(),'tables':19,'columns':sum(r['summary']['changed_columns'] for r in results),
        'columns_declared_in_contract':sum(r['summary']['columns_declared_in_contract'] for r in results),
        'columns_with_description':sum(r['summary']['columns_with_description'] for r in results),
        'columns_with_column_block_precision_format_text':sum(r['summary']['columns_with_column_block_precision_format_text'] for r in results),
        'columns_with_table_context_precision_mentions':sum(r['summary']['columns_with_table_context_precision_mentions'] for r in results),
        'tables_summary':[{k:r[k] for k in ('task','layer','table','whole_match_level_original','summary')} for r in results]})


if __name__=='__main__':main()
