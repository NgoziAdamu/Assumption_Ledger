"""Task 013: preserve the supplied human review and fingerprint all read-only inputs."""

from collections import Counter
import csv
import json
import os
from pathlib import Path

from compare_dacomp_staging import fingerprint
from complete_dacomp_comparisons import ROOT,RECORDS,PROJECT,save,stamp
from prepare_dacomp_annotation import EXPORT
from reconcile_dacomp_scope import jsonl

REVIEW={
 'A':{'original_basis':'agent 输出类型符合契约声明，gold 类型与契约声明不同（9 张）',
      'tables':{'impl-005':['stg_google_ads__account_stats','stg_google_ads__campaign_stats','stg_google_ads__keyword_stats'],
       'impl-022':['stg_recharge__address','stg_recharge__charge_line_item','stg_recharge__order_line_item'],
       'impl-026':['stg_twitter_ads__campaign_history'],'impl-027':['stg_xero__journal_line'],'impl-030':['stg_zuora__refund_invoice_payment']}},
 'B':{'original_basis':'差异仅为浮点运算末位误差，契约未要求舍入或要求不舍入（8 张）',
      'tables':{'impl-002':['pendo__product_adoption_analytics'],'impl-005':['int_google_ads__keyword_performance_segmentation'],
       'impl-010':['int_hubspot__deal_performance_metrics'],'impl-014':['qualtrics__survey_analytics'],
       'impl-017':['greenhouse__recruitment_performance','greenhouse__talent_pipeline_simplified'],
       'impl-027':['xero__balance_sheet_report'],'impl-028':['int_youtube__age_pivot']}},
 'C':{'original_basis':'其他（2 张）','tables':{'impl-013':['int_netsuite2__acctxperiod_exchange_rate_map'],'impl-028':['youtube__age_demographics_pivot']}}
}
SPECIFIC={
 ('impl-005','int_google_ads__keyword_performance_segmentation'):'其中 ctr 列 1 行 4.7226 / 4.7225，契约要求保留 4 位小数，经用户复核按格式差异处理',
 ('impl-013','int_netsuite2__acctxperiod_exchange_rate_map'):'契约声明 DOUBLE，agent 为 DOUBLE 1.0，gold 为 BOOLEAN true',
 ('impl-028','youtube__age_demographics_pivot'):'行元组完全一致，官方 L0 判为不一致'
}
SKIP_DIRS={'.git','.venv','venv','__pycache__','.agent-python','node_modules','external','event_cache'}


def code_files(root):
    result=[]
    for directory,dirs,files in os.walk(root):
        dirs[:]=[d for d in dirs if d not in SKIP_DIRS and not d.startswith('.venv')]
        result.extend(Path(directory)/name for name in files if Path(name).suffix in ('.py','.sh','.sql'))
    return sorted(result)


def cases():
    initial={r['task'].removeprefix('dacomp-de-'):r for r in json.loads((RECORDS/'003_dacomp_source_access.json').read_text())['tasks']}
    output=[]
    for n in range(1,31):
        task=f'impl-{n:03d}';case=json.loads((RECORDS/f'006_contract_{task}.json').read_text());agent=Path(case['agent_database'])
        source=next(r['path'] for r in initial[task]['database_checks'] if r['kind']=='initial')
        output.append({'task':task,'initial_database':source,'agent_database':str(agent),'agent_directory':str(agent.parent),
            'initial_directory':initial[task]['initial_repository'],
            'trace_directory':str(EXPORT/'runs/20261025_de_official_batch_01'/task/'agent')})
    return output


def main():
    previous=jsonl(RECORDS/'012_statuses.jsonl');format_rows=[r for r in previous if r['status']=='格式差异（待核契约）']
    wanted={(task,table):(group,entry['original_basis']) for group,entry in REVIEW.items() for task,tables in entry['tables'].items() for table in tables}
    actual={(r['task'],r['table']) for r in format_rows}
    correspondence={'expected':19,'actual_012':len(actual),'missing_from_user_list':[list(k) for k in sorted(actual-set(wanted))],
        'not_in_012_format_list':[list(k) for k in sorted(set(wanted)-actual)],'matches':actual==set(wanted),
        'group_counts':dict(Counter(g for g,text in wanted.values()))}
    save(RECORDS/'013_review_correspondence.json',correspondence)
    save(RECORDS/'013_review_basis.json',{'review_date':'2026-10-29','source':'用户和 Claude 的复核结果，由本任务用户消息提供；Codex 仅逐字记录，不自行归类',
        'groups':REVIEW,'specific_original_basis':[{'task':t,'table':name,'original_basis':text} for (t,name),text in SPECIFIC.items()]})
    states=[]
    for old in previous:
        row={**old,'status_012':old['status'],'status_basis_012':old['status_basis'],'status_source_012':old['status_source'],'status_source':'records/013_statuses.jsonl','human_review':None}
        if old['status']=='格式差异（待核契约）' and correspondence['matches']:
            group,basis=wanted[(old['task'],old['table'])]
            row['status']='格式差异';row['human_review']={'review_date':'2026-10-29','reviewer_source':'用户和 Claude（用户提供的复核结果）',
                'group':group,'group_basis_original':basis,'specific_basis_original':SPECIFIC.get((old['task'],old['table'])),
                'independent_Codex_classification':False,'source_record':'records/013_review_basis.json'}
            row['status_basis']='用户和 Claude 复核（2026-10-29）：'+basis
            if row['human_review']['specific_basis_original']:row['status_basis']+='；'+row['human_review']['specific_basis_original']
        row['status_changed_from_012']=row['status']!=old['status'];row['prior_records_modified']=False;states.append(row)
    (RECORDS/'013_statuses.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in states))
    flat=[{k:r[k] for k in ('task','layer','table','status_012','status','status_changed_from_012')}|{
        'review_date':r['human_review']['review_date'] if r['human_review'] else None,
        'review_group':r['human_review']['group'] if r['human_review'] else None,
        'review_basis_original':r['human_review']['group_basis_original'] if r['human_review'] else None,
        'review_specific_original':r['human_review']['specific_basis_original'] if r['human_review'] else None,
        'review_source':'用户和 Claude（用户消息）' if r['human_review'] else None} for r in states]
    with (RECORDS/'013_statuses.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(flat[0]),lineterminator='\n');writer.writeheader();writer.writerows(flat)
    save(RECORDS/'013_status_summary.json',{'statuses':dict(Counter(r['status'] for r in states)),'rows':len(states),
        'changed':sum(r['status_changed_from_012'] for r in states),'review_groups':correspondence['group_counts'],
        'list_correspondence':correspondence,'old_records_modified':False})
    before=RECORDS/'013_input_before.json'
    if not before.exists():
        files={Path(p) for p in json.loads((RECORDS/'012_input_before.json').read_text())['files']}
        for n in range(4,13):
            files.update(p for p in RECORDS.rglob(f'{n:03d}_*') if p.is_file());files.update((ROOT/'notes').glob(f'{n:03d}_*'))
        inputs=cases();inventory=[]
        for case in inputs:
            files.update(Path(case[k]) for k in ('initial_database','agent_database'))
            agent=Path(case['agent_database']);dependency=agent.with_name(agent.stem+'_start.duckdb')
            if dependency.exists():files.add(dependency)
            scripts=code_files(Path(case['agent_directory']));files.update(scripts)
            initial_runner=Path(case['initial_directory'])/'run.py'
            if initial_runner.exists():files.add(initial_runner)
            inventory.append({**case,'final_script_files':[str(p) for p in scripts]})
        save(RECORDS/'013_cases.json',inventory)
        print('Fingerprinting',len(files),'inputs',flush=True)
        save(before,{'started_at':stamp(),'files':{str(p):fingerprint(p) for p in sorted(files)}})
    print('Review correspondence',correspondence,'new states',dict(Counter(r['status'] for r in states)),flush=True)


if __name__=='__main__':main()
