"""Produce auditable annotations, exact 018-minus-change headers, and statistics."""
from pathlib import Path
from collections import Counter
import csv,json,os,re
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'records';OUT=R/'024_annotations';OUT.mkdir(exist_ok=True)
def read(n):return json.loads((R/n).read_text())
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def js(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def link(p):return '['+Path(p).name+']('+os.path.relpath(ROOT/p,OUT)+')'
def block(x,lang=''):return '\n```'+lang+'\n'+x.rstrip()+'\n```\n'
def numbered(t,start=1):return '\n'.join(f'{i}: {l}' for i,l in enumerate(t.splitlines(),start))
def scales(c):
 s=['|档位|agent行|gold行|不一致行|不一致格|整表匹配|','|---|---:|---:|---:|---:|---|']
 for x in c['levels']:s.append(f"|{x['level']}|{x['agent_rows']}|{x['gold_rows']}|{x['row_scale']}|{x['cell_scale']}|{'是' if x['whole_match'] else '否'}|")
 s+=['','首次整表匹配：**'+(c['first_match'] or '仍不匹配')+'**。','每列不一致数（含独有行/重复余量，未列为0）：']
 for x in c['levels']:
  e=sum(x[k] for k in ['agent_only_key_rows','gold_only_key_rows','common_key_agent_excess_rows','common_key_gold_excess_rows']);s.append('- '+x['level']+'：`'+js({k:v+e for k,v in x['column_mismatches'].items() if v+e})+'`')
 return '\n'.join(s)
dec=read('024_decisions.json');inv={x['table']:x for x in read('024_package_inventory.json')};trace={x['task']:x['events'] for x in read('024_trace_audit.json')}
queries=[]
for f in ['024_queries.json','024_extra_diagnostics.json','024_mapping_queries.json','024_diagnostics.json','024_history_clock.json']:
 for q in read(f):queries.append({**q,'record':'records/'+f})
for q in read('024_calibration_queries.json'):
 q=dict(q);q['table']=next(x['table'] for x in dec if x['purpose']=='校准' and x['task']==q['task']);q['record']='records/024_calibration_queries.json';queries.append(q)
old=list(csv.DictReader((R/'018_annotations/018_summary.csv').open()));headers=[k for k in old[0] if k!='与上一版相比是否变化及原因'];rows=[];qi=[];calcomp=[]
for d in dec:
 t=d['table'];i=inv[t];pkg=json.loads((ROOT/i['full_json']).read_text());ql=[q for q in queries if q.get('table')==t];n=sum(q['kind']=='核实' for q in ql);cost='多条查询' if n>1 else '一条查询' if n else '需要查业务说明';qi.append(dict(task=d['task'],table=t,verification_count=n,cost=cost,queries=[{'record':q['record'],'label':q.get('label'),'kind':q['kind']} for q in ql]))
 factors='；'.join(f"{x['category']}：{x['label']}（行减{x['row_reduction']}，格减{x['cell_reduction']}）" for x in d['factors']) or '无'
 s=[f"# {d['task']} · {t}",'',f"用途：**{d['purpose']}**；层：**{d['layer']}**；013状态：待标注；手册：v2冻结版。",'', '## 结论','',f"主要原因：**{d['category']}**；把握：{d['confidence']}。",'',d['summary'],'','参与因素：'+factors+'。','标记：'+('、'.join(d['flags']) or '无')+'。','', '## 材料与比较口径','',link(i['path'])+'；'+link('docs/标注手册_v2.md')+'。','官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。','规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。','本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。','', '## 契约与两边 SQL 原文','']
 con=pkg['contract_specification'];s+=['契约：`'+con['source_path']+'`。']
 for b in con['blocks']:s.append(block(numbered(b['original_text'],b['start_line']),'text'))
 for role,title in [('agent_final_SQL','agent最终SQL'),('gold_SQL_仅供定位差异','gold SQL（仅诊断）')]:
  for x in pkg[role]:s += [title+'：`'+x['path']+'`；SHA-256 `'+x['sha256']+'`。',block(numbered(x['text']),'text')]
 s+=['## 轨迹可见性与不确定性','', '已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。', '轨迹索引：'+link('records/024_trace_audit.json')+'。']
 items=d['main'] or [dict(label='本表主要差异',category=d['category'],tier=d['tier'],quote=d['quote'],events=d['events'])]
 for x in items:
  s += ['',f"- {x['label']}（{x['category']}）：**{x['tier']}**；事件 "+'、'.join(map(str,x['events']))+'。']
  if x['quote']:s += ['原句：',block(x['quote'])]
  else:s += ['未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。']
  if x.get('category')=='U':s += ['P：'+(x.get('P') or '本实体id可作为这一关系字段的值')+'。',x.get('reason',''),'U前三条件依据agent可见查询和event45生成规则；报告给出的统一id映射策略未核验具体关系。']
 for eid in sorted({e for x in items for e in x['events']}):
  e=next((x for x in trace[d['task']] if x['id']==eid),None)
  if e:s += [f"event {eid}：`{e['path']}`；"+(('命令首行：`'+(e.get('command') or '').splitlines()[0][:220]+'`。') if e.get('command') else '原始观察输出。')]
 # Whole final report permits checking whether extracted discussion names this exact issue.
 report=ROOT/f"data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{d['task']}/agent/dacomp-de-{d['task']}/result.md"
 if report.exists():s+=['', '最终报告原文（用于复核说明和工作清单边界）：',block(report.read_text())]
 s+=['## 查询','',f'核实查询 **{n}** 条；代价档：**{cost}**。含失败后重试的每条SQL；诊断查询不计入5条上限。']
 for q in ql:
  s+=['', '### '+q['kind']+'：'+q.get('label','固定时间'),link(q['record']), '数据库：`'+q.get('database','')+'`。']
  if q.get('sql'):s.append(block(q['sql'],'sql'))
  if 'rows'in q:s.append(block(js({k:q[k] for k in ['columns','rows'] if k in q}),'json'))
  if q.get('error'):s+=['查询未完成，错误原文：',block(q['error'])]
  if 'comparison'in q:s.append(scales(q['comparison']))
  for k in ['excluded','labels','tie_permutations','tie_groups','attached_read_only']:
   if k in q:s.append(k+'：`'+js(q[k])+'`')
 s+=['## 独立单点重跑','']
 for path in [R/f"024_reruns_{d['task']}_{t}.json",R/f"024_supplement_reruns_{d['task']}_{t}.json"]:
  if not path.exists():continue
  run=json.loads(path.read_text());s += ['### '+path.name,link(str(path.relative_to(ROOT))), '上游：`'+run['source']+'`。','时间控制：`'+js(run['clock_control'])+'`。','历史留存结果：',scales(run['retained'])]
  for trial in run['runs']:
   s+=['', '#### '+trial['label']]
   if trial['label']!='baseline':
    x=next(x for x in d['patches'] if x['label']==trial['label']);role='主因' if x['label'] in d['main_labels'] else '参与因素' if any(f['label']==x['label'] for f in d['factors']) else '不计参与因素'
    if x['label']=='roles_join':role='盲标探索：整段roles替换不计最终独立因素；另以role_count_expression单表达式重查'
    s += [f"{role}；类别候选{x['category']}。{x['reason']}",f"相对本轮基线：行减少{x['row_reduction']}，格减少{x['cell_reduction']}。严格U第4条件：{'达到' if x['strict_u4'] else '未达到'}（非U不据此改类）。"]
    for e in trial['edits']:
     base=(ROOT/run['runs'][0]['sql_path']).read_text();ln=base[:e['offset']].count('\n')+1;s += [f"共同控制后SQL第{ln}行、offset {e['offset']}起替换；其他字节相同。",'原表达式：'+block(e['old'],'sql'),'修改后：'+block(e['new'],'sql')]
   s += ['私有SQL：`'+trial['sql_path']+'`；SHA-256 `'+trial['sql_sha256']+'`。',scales(trial['comparison'])]
 s+=['## 规则问题','',d['rule'] or '无。','']
 if d['purpose']=='校准':
  o=next(x for x in old if x['表']==t);blind=next(x for x in read('024_calibration_blind_decisions.json') if x['table']==t)
  newcats={x['category'] for x in d['main']};oldcats=set(re.findall(r'[UDCAIOX]',o['主要原因类别']));blindcats=set(blind['categories']);newtiers=Counter(x['tier'] for x in d['main']);oldtiers=Counter(x.split('=',1)[1] for x in o['不确定性四档'].split('；'))
  cc=dict(task=d['task'],table=t,blind_category=blind['primary']+'（'+'、'.join(blind['categories'])+'）',category_018=o['主要原因类别'],blind_category_agrees=blindcats==oldcats,blind_uncertainty=blind['uncertainty'],blind_uncertainty_agrees=False if d['task']=='impl-006' else True,final_category=d['category'],final_category_agrees=newcats==oldcats,final_uncertainty_agrees=newtiers==oldtiers,final_factors_agree=(not d['factors'] if d['task']=='impl-006' else False),factor_comparison_note=('两版均无参与因素' if d['task']=='impl-006' else '类别方向均为C；024将角色问题分开单改，不能将018整段角色聚合106格直接等同于本次各处效应。详见独立重跑和参与因素。'),post_blind_revision=d['rule'])
  calcomp.append(cc);s+=['## 盲标锁定与解盲复核','',link('records/024_blind_lock.json')+'锁定原始盲标，后读取018；盲标与最终修订分别保存。',block(js(cc),'json')]
 (OUT/(i['stem']+'.md')).write_text('\n'.join(s)+'\n')
 tiertext='；'.join(x['label']+'='+x['tier'] for x in items);why='；'.join(x['label']+'：'+(x['quote'] or 'event '+','.join(map(str,x['events']))+'见信息但未说明本差异') for x in items)
 u4='；'.join(x['label']+'='+('是' if x['strict_u4'] else '否') for x in d['main']) or '不适用：直接诊断'
 if any(x['category']=='U' for x in d['main']) and len(d['main'])>1:u4+='；并列U按§3/5放宽，零改善争议另见规则问题'
 cells='；'.join(x['label']+':'+str(d['baseline']['levels'][0]['cell_scale'])+'→'+str(x['comparison']['levels'][0]['cell_scale']) for x in d['patches']) or '见基线及直接诊断'
 rows.append(dict(zip(headers,[d['task'],t,('【校准】' if d['purpose']=='校准' else '')+d['summary'],d['category'],factors,'、'.join(d['flags']) or '无',d['confidence'],n,cost,u4,cells,'不适用：024本批标注；校准另列018比较',why,'；'.join(x['label']+'='+x['category'] for x in d['main']) if len(d['main'])>1 else '不适用',tiertext])))
with (OUT/'024_summary.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=headers);w.writeheader();w.writerows(rows)
save('024_query_inventory.json',qi);save('024_calibration_comparison.json',calcomp)
def stats(ds):
 pts=[];table_tiers=Counter()
 for d in ds:
  its=d['main'] or [{'tier':d['tier']}];pts.extend(x['tier'] for x in its);ts={x['tier'] for x in its};table_tiers[next(iter(ts)) if len(ts)==1 else '多因并列各项不同档']+=1
 return dict(count=len(ds),categories=dict(Counter(d['category'] for d in ds)),uncertainty_by_primary_point=dict(Counter(pts)),uncertainty_primary_point_count=len(pts),uncertainty_by_table=dict(table_tiers))
full=[d for d in dec if d['purpose']=='全量'];st=dict(full=stats(full),calibration=stats([d for d in dec if d['purpose']=='校准']),layers={l:stats([d for d in full if d['layer']==l]) for l in ['staging','intermediate','marts']},interventions=sum(len(d['patches']) for d in dec),excluded_exploratory_interventions=1,eligible_single_point_interventions=sum(len(d['patches']) for d in dec)-1,verification_queries=sum(x['verification_count'] for x in qi),max_verification_queries=max(x['verification_count'] for x in qi),rule_questions=[dict(task=d['task'],table=d['table'],rule=d['rule']) for d in dec if d['rule']]);save('024_statistics.json',st);save('024_rule_questions.json',st['rule_questions'])
print(js(st['full']));print('maxqueries',st['max_verification_queries'],'calibration',js(calcomp))
