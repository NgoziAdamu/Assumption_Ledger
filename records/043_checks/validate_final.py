"""043最终52表验证：只读既有证据、原始文本及Git状态；仅写043检查结果。"""
from pathlib import Path
from collections import Counter
import csv, hashlib, json, subprocess
R=Path('records');K=R/'043_checks'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with Path(p).open() as f:return list(csv.DictReader(f))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
checks=[]
def check(n,ok,d=None):checks.append({'name':n,'passed':bool(ok),'detail':d})
scope=load(R/'043_scope.json');formal=load(K/'formal_working.json');cal=load(K/'calibration_working.json')
objects=rows(R/'043_objects.csv');points=rows(R/'043_points.csv');allids={o['对象编号'] for o in objects}
pilot={r['对象编号'] for r in rows(R/'036_objects.csv')}
expected={r['task']+'_'+r['table'] for r in rows(R/'013_statuses.csv') if r['status']=='待标注' and 'impl-022'<=r['task']<='impl-030' and r['task']+'_'+r['table'] not in pilot}
calids={'impl-006_stg_reddit_ads__campaign_report','impl-016_workday__organization_overview'}
check('正式范围精确匹配50张',len(expected)==50 and expected=={o['object_id'] for o in formal}=={o['object_id'] for o in scope['formal']})
check('正式题目计数符合9/4/2/10/4/3/18',Counter(o['task'] for o in formal)=={'impl-023':9,'impl-024':4,'impl-025':2,'impl-026':10,'impl-027':4,'impl-028':3,'impl-030':18})
check('50+2对象无重复且全部在CSV',len(objects)==52 and len(allids)==52 and allids==expected|calids and set(scope['calibration'])==calids)
keys={(p['对象编号'],p['错误点名称']) for p in points};formalkeys={(o['object_id'],p['point']) for o in formal for p in o['points']}
check('217点键唯一且正式182点逐一匹配',len(points)==217 and len(keys)==217 and len(formalkeys)==182 and formalkeys=={k for k in keys if k[0]in expected})
uneval={o['object_id'] for o in formal if o['main']=='不可评估'}
check('不可评估仅028两个staging且无错误点',uneval=={'impl-028_stg_youtube__channel_basic','impl-028_stg_youtube__video'} and all(not o['points'] for o in formal if o['object_id']in uneval))
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
categories={'Data Misconception','Intent Misreading','Unstated Choice','Quiet Downgrade','Form Mismatch','已说出的选择','已说出的降级','其他','代码写错','无法判定'}
check('类别与五档取值合法',all(p['类别']in categories and p['是否说出（五档）']in levels for p in points))
check('已说出类别与第1档一致',all((p['类别']not in ['已说出的选择','已说出的降级'] or p['是否说出（五档）']==levels[0]) and (p['是否说出（五档）']!=levels[0] or p['类别']not in ['Unstated Choice','Quiet Downgrade']) for p in points))
check('探索字段合法',all((p['证据在场']in ['是','否'] and p['曾经理解对过']in ['是','否']) if p['类别']in ['Data Misconception','Intent Misreading'] else (p['证据在场']=='不适用' and p['曾经理解对过']=='不适用') for p in points))
check('全部系统提示字段不适用',all(p['系统提示是否适用']=='不适用' for p in points))
old={o['task']+'_'+o['table']:o['category'] for o in load(R/'024_decisions.json')}
check('024旧主要原因逐行原样保留',all(p['024旧标签']==old[p['对象编号']] for p in points+objects))
for typ in ['objects','points']:
    with (R/f'042_{typ}.csv').open() as f:h42=next(csv.reader(f))
    with (R/f'043_{typ}.csv').open() as f:h43=next(csv.reader(f))
    check(typ+'表头与042相同且末列024旧标签',h43[:-1]==h42[:-1] and h43[-1]=='024旧标签')
    check(typ+'校准CSV前缀逐字节未变',(R/f'043_{typ}.csv').read_bytes().startswith((K/f'phase1_{typ}_prefix.csv').read_bytes()))
check('五个校准封存/比较/定稿文件hash未变',all(sha(p)==h for p,h in load(K/'phase1_handoff.json')['calibration_file_hashes'].items()))
check('原封存hash一致',sha(R/'043_calibration_blind_sealed.json')==load(K/'calibration_seal_hash.json')['sha256'])
check('52份逐表说明完整且无额外表',{p.name for p in (R/'043_annotations').glob('*.md')}=={f'043_{oid}.md' for oid in allids})

# 数字独立回查024源记录；未运行任何SQL。
def scale(x):return [{k:l[k] for k in ['level','row_scale','cell_scale']} for l in x['levels']]
source_cache={}
def src(p):
    if p not in source_cache:source_cache[p]=load(p)
    return source_cache[p]
numeric=[];ranking=[];source_modes=[]
for o in formal:
    for p in o['points']:
        if p['after'] is not None:
            rr=src(p['source']);b=next(x for x in rr['runs'] if x['label']=='baseline');a=next(x for x in rr['runs'] if x['label']==p['run_label'])
            reduction=[p['baseline'][0][k]-p['after'][0][k] for k in ['row_scale','cell_scale']]
            numeric.append(scale(b['comparison'])==p['baseline'] and scale(a['comparison'])==p['after'] and a['edits']==p['edits'] and p['reduction']==reduction and rr.get('clock_control',[])==p['clock_control'])
            source_modes.append(('agent' in rr['source']) if o['layer']=='staging' else ('dacomp-de-gold'in rr['source']))
        else:
            d=src(p['source'])[p['group_diagnostic']['index']]
            numeric.append(scale(d['comparison'])==p['group_diagnostic']['levels'] and p['point'] in d['excluded'])
    if o['main']=='不可评估':continue
    if any(p['reduction']is None for p in o['points']):
        ranking.append(o['main']=='其他' and o['confidence']in ['中','低'] and all(p['category']=='其他' and p['role']=='同类候选' for p in o['points']))
        continue
    improved=[p for p in o['points'] if tuple(p['reduction'])>(0,0)]
    if o['combination_only']:
        c=o['combination'];source_combo=src(c['source'])[c['index']]
        b=o['points'][0]['baseline'][0];a=c['levels'][0]
        ranking.append(not improved and tuple([b['row_scale']-a['row_scale'],b['cell_scale']-a['cell_scale']])>(0,0) and scale(source_combo['comparison'])==c['levels'] and all((p['role']=='组合项')==(p['point']in c['labels']) for p in o['points']))
    else:
        best=max(tuple(p['reduction']) for p in improved);winners=[p for p in improved if tuple(p['reduction'])==best]
        cats={p['category'] for p in winners};m=next(iter(cats)) if len(cats)==1 else '多因并列'
        ranking.append(o['main']==m and set(o['main_points'])=={p['point'] for p in winners} and all(p['role']==(('主要' if len(winners)==1 else '并列') if p in winners else ('参与' if p in improved else '非原因')) for p in o['points']))
check('正式182点的单改/成组L0-L3数值和编辑逐条回查',len(numeric)==182 and all(numeric))
check('按行优先再格排序且组合/同类例外正确',len(ranking)==48 and all(ranking))
check('正式复用重跑staging用agent库其他层用CS gold',all(source_modes))
csvpoints={(p['对象编号'],p['错误点名称']):p for p in points};csvobjects={o['对象编号']:o for o in objects}
check('正式CSV与工作件分类角色五档及主因一致',all(csvobjects[o['object_id']]['主要原因']==o['main'] and csvobjects[o['object_id']]['是否只能组合修复']==('是' if o['combination_only'] else '否') and all(csvpoints[(o['object_id'],p['point'])]['类别']==p['category'] and csvpoints[(o['object_id'],p['point'])]['角色']==p['role'] and csvpoints[(o['object_id'],p['point'])]['是否说出（五档）']==levels[p['disclosure']-1] for p in o['points']) for o in formal))
data=[p for o in formal for p in o['points'] if p['category']=='Data Misconception']
check('22个Data逐点有P与agent可见核实反证及曾经正确事件',len(data)==22 and all(p.get('P') and p['verification']['mapping_query']['result']['chosen_matches']==0 and p['verification']['mapping_query']['result']['named_matches']>0 and p['previously_correct']=='是' and {19,45}<={q['event'] for q in p['decision_citations']} for p in data))

# 逐表查询预算及引用索引准确性。
query_ok=[]
for o in formal:
    for q in o['verification_queries']:
        original=src(q['source'])[q['index']]
        query_ok.append(original=={k:v for k,v in q.items() if k not in ['source','index']} and q['kind']=='核实' and q['task']==o['task'] and q['table']==o['table'])
check('正式复用核实查询与原记录逐字一致',all(query_ok),{'query_references':len(query_ok)})
check('全部52表核实预算不超过5',all(len(o['verification_queries'])<=5 for o in formal) and all(q['total']<=5 for q in cal['query_budget'].values()),{'formal_max':max(len(o['verification_queries']) for o in formal),'calibration':cal['query_budget']})
new=load(K/'calibration_queries.json')
check('新查询仅阶段一1条只读；阶段二无新增',len(new)==1 and all(q['read_only'] for q in new),'执行纪律记录：阶段二未调用数据库连接；本检查不声称对阶段一数据库做过读前hash。')

# 全部引句回到对应事件字段；非仅对照整理件。
def quotes(x):
    if isinstance(x,dict):
        if {'source','event','field','quote'}<=x.keys():yield x
        else:
            for v in x.values():yield from quotes(v)
    elif isinstance(x,list):
        for v in x:yield from quotes(v)
audit=[];tracecache={}
quotefiles=[R/'043_calibration_blind_sealed.json',K/'calibration_working.json',K/'disclosure_audit.json',K/'026_review_preparation.json',K/'026_review_final.json',K/'shared_root_decisions.json',K/'formal_working.json',K/'formal_quote_inventory.json',K/'raw_integrity_review.json']
for f in quotefiles:
    for q in quotes(load(f)):
        if q['source']not in tracecache:tracecache[q['source']]={e['id']:e for pair in load(q['source'])['history'] for e in pair if 'id'in e}
        s=tracecache[q['source']][q['event']]
        for k in q['field'].split('.'):s=s[k]
        audit.append({'record':str(f),**q,'matched':bool(q['quote']) and q['quote']in s})
check('全部引句逐一回查原文成功',bool(audit) and all(a['matched'] for a in audit),{'references':len(audit),'unique_quotes':len({(a['source'],a['event'],a['field'],a['quote']) for a in audit})})
save(K/'quote_checks.json',audit)
disclosure=load(K/'disclosure_audit.json')['points']
check('披露审计覆盖217点且档位匹配',len(disclosure)==217 and {(p['object_id'],p['point']) for p in disclosure}==keys and all(levels[p['disclosure']-1]==csvpoints[(p['object_id'],p['point'])]['是否说出（五档）'] for p in disclosure))
check('正式第1/2档只引用最终报告',all(all(q['field']=='args.final_thought' for q in p['citations']) for p in disclosure if p['object_id']in expected and p['disclosure']in [1,2]))
check('217点交付SQL原文hash一致且无注释',all(sha(p['delivered_sql'])==p['delivered_sql_sha256'] and not p['delivered_sql_has_comments'] and '--'not in Path(p['delivered_sql']).read_text() and '/*'not in Path(p['delivered_sql']).read_text() for p in disclosure))
materials=load(K/'formal_material_audit.json')
check('50张契约块和SQL原文hash重新核对',len(materials)==50 and all(sha(m['contract_path'])==m['contract_sha256'] and sha(m['agent_sql'])==m['agent_sql_sha256'] and all(b['original_text']in Path(m['contract_path']).read_text() and b['original_text']in tracecache[f"data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{m['object_id'][:8]}/agent/output.jsonl"][1]['args']['content'] for b in m['contract_blocks']) for m in materials))

shared=load(K/'shared_root_decisions.json')
for label,key in [('共同生成动作','generation_families'),('具体根源决定','decisions')]:
    members=[(o['object_id'],p['point']) for g in shared[key] for o in g['affected'] for p in o['points']]
    check(label+'完整覆盖182点且计数时不重叠',set(members)==formalkeys and len(members)==182)
check('共同生成动作覆盖全部50表含不可评估', {o['object_id'] for g in shared['generation_families'] for o in g['affected']}==expected)
root45=next(r for r in shared['decisions'] if r['id']=='impl-030-event45-pk_alias')
check('event45范围14表43点',root45['table_count']==14 and root45['point_count']==43)
check('18张Zuora逐表说明明确raw版本',all('正常' in o['raw_note'] and 'event' in o['raw_note'] and o['raw_note']in (R/'043_annotations'/f"043_{o['object_id']}.md").read_text() for o in formal if o['task']=='impl-030'))
raw=load(K/'raw_integrity_review.json')['zuora_timeline']
check('Zuora导入程序两份原版hash一致',sha(raw['initial_run_py'])==sha(raw['agent_run_py'])==raw['sha256_both'])

protected={**load(K/'input_hashes_before.json')['sha256'],**load(K/'input_hashes_supplement.json')['sha256']}
changed=[p for p,h in protected.items() if not Path(p).exists() or sha(p)!=h]
check('018～040和042记录及v3.1/v3.2手册hash未变',not changed,{'checked':len(protected),'changed':changed})
idx=subprocess.check_output(['git','ls-files','-s','notes/041*','records/041*'],text=True)
check('041索引不变且工作区未改（不读正文）',idx==load(K/'input_hashes_before.json')['041_git_index_only'] and subprocess.run(['git','diff','--quiet','HEAD','--','notes/041*','records/041*']).returncode==0)
tracked=[p for p in subprocess.check_output(['git','diff','--name-only','-z','HEAD'],text=True).split('\0') if p];untracked=[p for p in subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],text=True).split('\0') if p]
check('工作区变更仅043报告和记录',all(p.startswith(('records/043','notes/043')) for p in tracked+untracked),tracked+untracked)
report=Path('notes/043_2026-11-03_DAComp重标第六批.md').read_text()
check('报告已更新完整且逐张列出50表', '任务043已完成' in report and '## 不确定或没查到的（含规则问题）' in report and all(o['object_id']in report for o in formal))
diff=subprocess.run(['git','diff','HEAD','--check'],text=True,capture_output=True)
check('git diff HEAD --check通过',diff.returncode==0,diff.stdout+diff.stderr)
out={'status':'passed' if all(c['passed'] for c in checks) else 'failed','task_complete':all(c['passed'] for c in checks),'formal_expected':50,'formal_completed':50,'calibration_completed':2,'object_count':52,'point_count':len(points),'formal_point_count':182,'checks':checks,'limitations':['初始hash清单漏720个子文件；读取后补hash，并先通过Git差异检查，不声称补快照在首次读取之前。','唯一新查询在阶段一且read_only=True，未做数据库读前hash；阶段二完全复用证据。','两个同类候选表只有成组顺序诊断，没有虚构逐列独立收益。']}
save(K/'validation.json',out)
print(out['status'],sum(c['passed'] for c in checks),'/',len(checks),'quotes',len(audit))
assert all(c['passed'] for c in checks),[c for c in checks if not c['passed']]
