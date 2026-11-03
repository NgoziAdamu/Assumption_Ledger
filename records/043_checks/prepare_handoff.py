"""解盲比较、校准定稿和正式批证据目录；不重写封存件、不执行旧脚本。"""
from pathlib import Path
import collections, copy, csv, datetime, hashlib, json, re

R=Path('records'); C=R/'043_checks'; A=R/'043_annotations'; A.mkdir(exist_ok=True)
def load(p): return json.loads(Path(p).read_text())
def save(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
sealed=load(R/'043_calibration_blind_sealed.json')
assert sha(R/'043_calibration_blind_sealed.json')==load(C/'calibration_seal_hash.json')['sha256']
ids={o['object_id'] for o in sealed['objects']}
with (R/'036_objects.csv').open() as f: oldobjects={r['对象编号']:r for r in csv.DictReader(f) if r['对象编号'] in ids}
with (R/'036_points.csv').open() as f: oldpoints={(r['对象编号'],r['错误点名称']):r for r in csv.DictReader(f) if r['对象编号'] in ids}
name_map={'annual_turnover_rate':'annual_zero','management_ratio':'management_zero','organization_maturity_level':'maturity_labels','organization_size_category':'size_labels','assignment_join':'tenure_join_weight'}
comparison=[]; unmapped=[]
for p in sealed['points']:
    name=name_map.get(p['point'],p['point']) if p['object_id'].startswith('impl-016') else p['point']
    prev=oldpoints.get((p['object_id'],name))
    if not prev:
        unmapped.append({'object_id':p['object_id'],'point':p['point'],'category':p['category'],'note':'role_*五点对应036的roles_relationship组；其余五点是本次额外记录的非原因点。'})
        continue
    comparison.append({'object_id':p['object_id'],'point':p['point'],'036_point':name,'blind_category':p['category'],'036_category':prev['类别'],
                       'blind_disclosure':p['disclosure'],'036_disclosure':levels.index(prev['是否说出（五档）'])+1,
                       'category_agrees':p['category']==prev['类别'],'disclosure_agrees':levels[p['disclosure']-1]==prev['是否说出（五档）'],
                       'blind_role':p['role'],'036_role':prev['角色']})
working=copy.deepcopy(sealed)
working['stage']='解盲后校准定稿；独立保留盲标结果'
changes={
 'post_visits':'复核列清单和契约：comments_page_views是评论页面浏览量，是否等同post_visits没有说明，不能仅凭相近名称确立目标含义；gold也未使用该候选而取0。按缺少明确对应列、默认值未规定处理为Unstated Choice。保留有候选即降级的另一读法。',
 'cost_per_video_view':'原始没有单位观看成本列，video_started、完整可见播放、不同观看时长等不是同一计数；契约未定成本分母，不能以gold选video_started证明本处是省略已定义指标。按未定定义/缺失处理归Unstated Choice。',
 'total_engagements':'契约未规定互动事件集合、是否纳入downvotes、是否将评论页访问纳入；原始没有该总量列。盲标把存在分项等同已明确的目标指标，证据不足；改Unstated Choice。',
 'engagement_rate':'互动事件集合和分母均未规定，原始无此比率列；能构造一种公式不足以证明该公式就是要求的量。按未定选择归Unstated Choice。',
}
for p in working['points']:
    if p['object_id'].startswith('impl-006') and p['point'] in changes:
        p['category']='Unstated Choice'; p['post_unblind_change']=changes[p['point']]; p['reason']=changes[p['point']]
    elif p['point'] in ['click_through_rate','cost_per_click','cost_per_thousand_impressions']:
        p['post_unblind_change']='类别不变；第2档与036第4档存在差异。本次保留第2档：finish event97明确说明TRY_CAST不可解析值转NULL，正是本处处理类别；未点名Reddit，不升级第1档。'
save(R/'043_calibration_comparison.json',{
 'unblinded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sealed_sha256':sha(R/'043_calibration_blind_sealed.json'),
 'object_comparisons':[{'object_id':o['object_id'],'blind_main':o['main'],'036_main':oldobjects[o['object_id']]['主要原因'],'main_and_category_set_agree':True} for o in sealed['objects']],
 'point_comparisons':comparison,'not_one_to_one':unmapped,
 'group_comparison':{'036_point':'roles_relationship','blind_points':[p['point'] for p in sealed['points'] if p['point'].startswith('role_')],'category_agrees':True,'disclosure_agrees':True,'note':'036为一个参与组；本次5个单改点，1个参与、4个非原因，不能计成5个独立校准一致。'},
 'blind_statistics':{'object_main_and_category_set':{'agree':2,'total':2},'one_to_one_points':len(comparison),'category_agree':sum(p['category_agrees'] for p in comparison),'disclosure_agree':sum(p['disclosure_agrees'] for p in comparison)},
 'post_unblind_category_changes':changes,'post_unblind_disclosure_disagreements_retained':['click_through_rate','cost_per_click','cost_per_thousand_impressions'],
 'warning':'不能用解盲后类别一致率替换盲标一致率；036不是事实来源，修订理由回到契约及原始列。'})
save(C/'calibration_working.json',working)

old24={r['task']+'_'+r['table']:r['category'] for r in load(R/'024_decisions.json')}
with (R/'042_objects.csv').open() as f: object_header=next(csv.reader(f))
with (R/'042_points.csv').open() as f: point_header=next(csv.reader(f))
object_header[-1]=point_header[-1]='024旧标签'
roles={'主要原因':'并列','并列主要原因':'并列','参与因素':'参与','存在未确立的前提，但不是判错原因':'非原因'}
with (R/'043_objects.csv').open('w') as f:
    w=csv.writer(f,lineterminator='\n'); w.writerow(object_header)
    for o in working['objects']:
        tied=[p for p in working['points'] if p['object_id']==o['object_id'] and p['role'] in ['主要原因','并列主要原因']]
        w.writerow(['DAComp',o['object_id'],o['layer'],o['main'],'；'.join(p['point']+':'+p['category'] for p in tied),'否',o['confidence'],old24[o['object_id']],old24[o['object_id']]])
with (R/'043_points.csv').open('w') as f:
    w=csv.writer(f,lineterminator='\n');w.writerow(point_header)
    for p in working['points']:
        w.writerow(['DAComp',p['object_id'],p['point'],roles[p['role']],p['category'],levels[p['disclosure']-1],p['evidence_present'],p['previously_correct'],'不适用','复用；043核对原始交付物/轨迹'+('；新核实查询' if p['new_evidence'] else ''),';'.join([p['evidence']['source'],'records/043_checks/disclosure_audit.json',*p['evidence_reuse'],*p['new_evidence']]),old24[p['object_id']]])
audit=[]
for o in working['objects']:
    oid=o['object_id']; task=oid.split('_')[0]; table=oid[len(task)+1:]
    sql=Path(f'/home/katherine/dac/runs/20261025_de_official_batch_01/{task}/agent/dacomp-de-{task}/sql/{o["layer"]}/{table}.sql')
    contract=Path(f'/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-{task}/docs/data_contract.yaml')
    assert sql.exists() and contract.exists()
    s=sql.read_text();assert '--' not in s and '/*' not in s
    text=[f'# 043 校准定稿：{oid}','## 任务','按冻结v3.2第3～8节盲标，封存后解盲。此件是解盲后的定稿，封存件不改。','## 结论',f'主要原因：{o["main"]}；并列类别：'+ '、'.join(o['tied_categories'])+'。不是只能组合修复。',o['rationale'],f'024旧主要原因：`{old24[oid]}`，仅存档。','## 详细发现']
    for p in [p for p in working['points'] if p['object_id']==oid]:
        text += [f'### {p["point"]}',f'{p["role"]}；{p["category"]}；把握{p["confidence"]}。',p['reason'],f'是否说出：第{p["disclosure"]}档，{levels[p["disclosure"]-1]}。'+p['disclosure_reason'],f'证据在场：{p["evidence_present"]}；曾经理解对过：{p["previously_correct"]}；系统提示是否适用：不适用。',f'复用 `{p["evidence"]["source"]}` / `{p["evidence"]["label"]}`。', '| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |','|---|---:|---:|---:|---:|']
        for b,a in zip(p['evidence']['baseline'],p['evidence']['after']):text.append(f'| {b["level"]} | {b["row_scale"]} | {a["row_scale"]} | {b["cell_scale"]} | {a["cell_scale"]} |')
        quotes=p['disclosure_citations']+p['decision_citations']
        for q in {json.dumps(q,sort_keys=True):q for q in quotes}.values():
            text += [f'`{q["source"]}` / event {q["event"]} / `{q["field"]}`：','```text\n'+q['quote']+'\n```']
        if p.get('post_unblind_change'):text += ['解盲后复核：'+p['post_unblind_change']]
        audit.append({'object_id':oid,'point':p['point'],'disclosure':p['disclosure'],'reason':p['disclosure_reason'],'citations':p['disclosure_citations'],'excluded_delivery_citations':p.get('excluded_delivery_citations',[]),'delivered_sql':str(sql),'delivered_sql_sha256':sha(sql),'delivered_sql_has_comments':False,'final_event':97 if task=='impl-006' else 83})
    if o.get('clock_note'):text.append(o['clock_note'])
    text += ['## 证据来源',f'- 契约 `{contract}`；SHA-256 `{sha(contract)}`。',f'- 交付SQL `{sql}`；SHA-256 `{sha(sql)}`。','- 013材料包、024核实查询/单改/补充单改、原始output.jsonl；043新增1条Reddit原始指标文本范围核实查询（只读）。','- 封存、对比与结构化定稿：`records/043_calibration_blind_sealed.json`、`records/043_calibration_comparison.json`、`records/043_checks/calibration_working.json`。','## 不确定或没查到的（含规则问题）','Reddit的派生指标NULL与降级边界、mock_*源指标取数与重算的边界保留在封存/比较件中；不能由gold的公式倒推规格。' if task=='impl-006' else '健康分具体阈值未在契约中找到；角色关系按现有逐点单改记录细分，不能把组合改动的106格收益套给一个单点。','## 建议的下一步','同一会话继续50张正式表。校准定稿与盲标一致率分开保存。']
    (A/f'043_{oid}.md').write_text('\n\n'.join(text)+'\n')
save(C/'disclosure_audit.json',{'stage':'phase1_calibration_only','formal_complete':False,'points':audit})

# 正式表证据目录只列出材料路径及数值，不按024旧类别映射新类别。
scope=load(R/'043_scope.json'); catalog=[]; rawtasks=[]
for i in range(22,31):
    a=load(R/f'013_raw_impl-{i:03}.json'); b=load(R/f'015_raw_impl-{i:03}.json')
    rawtasks.append({'task':a['task'],'013_source':f'records/013_raw_impl-{i:03}.json','013_summary':a['summary'],
                     'changes':[{'table':t['table'],'initial_rows':t['initial']['row_count'],'agent_rows':t['agent']['row_count'],'initial_columns':len(t['initial']['columns']),'agent_columns':len(t['agent']['columns'])} for t in a['tables'] if t['different']],
                     '015_source':f'records/015_raw_impl-{i:03}.json','015_counts':dict(collections.Counter(x['comparison'] for x in b['comparisons'] if x['different']))})
for o in scope['formal']:
    oid=o['object_id']; task=o['task']; table=oid[len(task)+1:]
    pkgpath=Path(f'data/024_packages_work/024_{oid}/024_{oid}.json'); pkg=load(pkgpath)
    sql=pkg['agent_final_SQL'][0]['text']; refs=sorted(set(re.findall(r'\b(?:FROM|JOIN)\s+(raw\.[A-Za-z_0-9]+)',sql,re.I)))
    raw=load(R/f'013_raw_{task}.json'); by={t['table']:t for t in raw['tables']}
    rows=[]
    for ref in refs:
        t=by[ref.split('.')[1]]
        rows.append({'source':ref,'initial_rows':t['initial']['row_count'],'agent_rows':t['agent']['row_count'],'initial_columns':len(t['initial']['columns']),'agent_columns':len(t['agent']['columns']),'013_different':t['different']})
    runs=[]
    for f in sorted(R.glob(f'024*reruns_{oid}.json')):
        d=load(f)
        runs.append({'source':str(f),'runs':[{'label':r['label'],'levels':[{k:c[k] for k in ['level','row_scale','cell_scale']} for c in r.get('comparison',{}).get('levels',[])],'error':r.get('error')} for r in d['runs']]})
    catalog.append(dict(**o,package=f'records/024_packages/024_{oid}.md',package_json=str(pkgpath),raw_review_source=f'records/013_raw_{task}.json',raw_direct_sources=rows,rerun_inventory=runs,formal_annotation_done=False))
save(C/'raw_integrity_review.json',{'stage':'preparation','task_reviews':rawtasks,'per_object':[{'object_id':x['object_id'],'layer':x['layer'],'raw_review_source':x['raw_review_source'],'raw_direct_sources':x['raw_direct_sources']} for x in catalog],
 'handling':{'impl-025':'gold与agent raw相同，正常标注；message用agent raw。','impl-029':'无本批正式待标表；gold与agent raw相同，只记录背景。','impl-030':'gold与agent raw相同，正常标注；invoice初始1列、留存54列；需要按轨迹区分event18初始坏结构、event40正常结构，不能一概说agent只见过正常版。','impl-028':'两张staging直读raw与gold不同，待逐表写不可评估依据；int_youtube__video按CS照常。'}})
save(C/'evidence_catalog.json',catalog)
save(C/'phase1_handoff.json',{'stage':'phase1_complete_phase2_pending','formal_expected':50,'calibration_completed':2,'formal_completed':0,'completed':['范围精确核对50张','盲标2张35点封存与hash','036解盲对比及独立校准定稿','9题013/015 raw摘要及50张材料路径','026台账读取及组合修复数值初核'],
 'remaining':['50张正式表逐点按v3.2判类和披露','026相关条目最终处理','同源决定逐表逐点汇总','逐表最多5条核实查询预算与原句审计','最终52张范围验证和报告更新'],
 'resume_instruction':'在本会话继续043，不重新执行编号空缺检查，不重做盲标，不覆盖封存件；保留2张校准CSV前缀及定稿，在正式标注后追加50张。',
 'calibration_file_hashes':{str(p):sha(p) for p in [R/'043_calibration_blind_sealed.json',R/'043_calibration_comparison.json',C/'calibration_working.json',*sorted(A.glob('*.md'))]}})
(C/'phase1_objects_prefix.csv').write_bytes((R/'043_objects.csv').read_bytes())
(C/'phase1_points_prefix.csv').write_bytes((R/'043_points.csv').read_bytes())
print('calibration 2 objects / 35 points; catalog',len(catalog),'raw tasks',len(rawtasks),'blind category/disclosure',sum(x['category_agrees'] for x in comparison),sum(x['disclosure_agrees'] for x in comparison),'/',len(comparison))
