"""正式表尚未标注；只封存已回查的026相关事实和同源决定候选。"""
from pathlib import Path
import json
R=Path('records'); C=R/'043_checks'
def load(p): return json.loads(Path(p).read_text())
def save(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def quote(task,n,field,text):
    path=f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent/output.jsonl'
    es={e['id']:e for pair in load(path)['history'] for e in pair if 'id' in e}
    s=es[n]
    for k in field.split('.'):s=s[k]
    assert text in s
    return {'source':path,'event':n,'field':field,'quote':text}

combinations=[]
for r in load(R/'024_extra_diagnostics.json'):
    if r.get('label')=='多处组合仅诊断（不用于单点原因排名）' and r['table'] in ['tiktok_ads__ad_report','tiktok_ads__url_report','stg_zuora__invoice_payment']:
        oid=r['task']+'_'+r['table'];d=load(R/f'024_reruns_{oid}.json')
        stats=[{'label':x['label'],'levels':[{k:c[k] for k in ['level','row_scale','cell_scale']} for c in x['comparison']['levels']]} for x in d['runs']]
        combinations.append({'object_id':oid,'single_runs_source':f'records/024_reruns_{oid}.json','single_runs':stats,
                             'combination_source':'records/024_extra_diagnostics.json','combination_labels':r['labels'],
                             'combination_levels':[{k:c[k] for k in ['level','row_scale','cell_scale']} for c in r['comparison']['levels']],
                             'verified_numeric_conclusion':'所有已测单改都不减少行数或格子数；组合减少。invoice_payment组合L0残留6行6格，L1～L3为0，不能写所有口径全对。','category_pending':True})
trace='data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl'
events={e['id']:e for pair in load(trace)['history'] for e in pair if 'id' in e}
refs=[quote('impl-030',19,'args.command',"srcname=n\n            e=f'try_cast(\"{srcname}\" AS {typ})'"),
      quote('impl-030',45,'args.command',"if n in pk_alias: srcname='id'")]
affected=[]
for p in load(R/'024_patch_plan.json'):
    if p['task']!='impl-030':continue
    pts=[x for x in p['patches'] if x['label'].startswith('source_')]
    if not pts:continue
    oid=p['task']+'_'+p['table'];runs=load(R/f'024_reruns_{oid}.json')['runs']
    edits=[]
    for x in pts:
        run=next(r for r in runs if r['label']==x['label'])
        edits.append({'point':x['label'],'edits':run['edits'],'source':f'records/024_reruns_{oid}.json'})
    affected.append({'object_id':oid,'points':edits,'classification_pending':True})
save(C/'shared_root_decisions.json',{'stage':'preparation_candidates_not_final','decisions':[{
 'id':'impl-030-event45-pk_alias','task':'impl-030','event':45,
 'description':'将pk_alias集合中的外键名也一律映射为本表id；event19原先按同名源列生成。',
 'citations':refs,'affected':affected,'affected_table_count':len(affected),'affected_point_count':sum(len(x['points']) for x in affected),
 'scope_note':'026称12张表出现旧U；同一生成决定实际出现在本批14张表的source_*单改中。14是同源候选范围，不是Data类别计数；两者不可混用。分类、证据在场与曾经理解对过仍须正式逐点核实。'}]})
invoice_line=next(l.strip() for l in events[40]['content'].splitlines() if l.strip().startswith('zuora_invoice_data '))
invoice_before="stg_zuora__invoice missing direct ['account_id', 'adjustment_amount'"
schema_refs=[quote('impl-030',18,'content',invoice_before),quote('impl-030',40,'content',invoice_line)]
report=quote('impl-023',53,'args.command','`account_history.id` 在源中为 VARCHAR，但契约要求 BIGINT；不可转换的键按无效主键处理并删除。')
es={e['id']:e for pair in load('data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl')['history'] for e in pair if 'id'in e}
final=next(e for e in es.values() if e.get('action')=='finish')
report_finish=quote('impl-023',final['id'],'args.final_thought',report['quote'])
save(C/'026_review_preparation.json',{'stage':'facts_verified_classification_pending','source':'records/026_Claude全量标注检查台账.md',
 '024-1':combinations,'021-2':{'citations':refs,'handling':'event19正确同名取列、event45修改为id已回查；正式标注不得沿用旧U/I建议替代v3.2判断。'},
 'account_history':{'source':'records/024_queries.json','query_label':'契约键及timezone过滤计数','rows':[[2500,0,1035]],'columns':['n','numeric_id','invalid_timezone'],'delivery_citations':[report,report_finish],'handling':'报告点名说明类型转换及无效键删除；第1档要对应此处理，不能推广到timezone等其他点。'},
 'impl-028':{'source':['records/013_raw_impl-028.json','records/015_raw_impl-028.json'],'handling':'两个staging与gold源不同；中间层按CS，用gold上游。不可评估不混入五档统计。'},
 'invoice_versions':{'source':['records/013_raw_impl-030.json','records/015_raw_impl-030.json'],'initial_columns':1,'agent_retained_columns':54,'citations':schema_refs,'handling':'event18已见缺列，event40已见正常54列清单。实际运行恢复结构的具体步骤/原因本阶段未追溯，不能自行补全。'},
 '024-2':'另报同源决定范围；当前shared_root_decisions为候选清单，正式判类后完善。',
 '024-3':'首轮hash漏掉编号目录下无编号子文件，本轮补720项并用git diff HEAD确认保护文件未改；不冒称补快照发生在首次读取前。'})
print('shared root candidates',len(affected),'tables',sum(len(x['points']) for x in affected),'points; combinations',len(combinations))
