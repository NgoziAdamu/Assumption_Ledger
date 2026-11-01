"""Append the formal 43 decisions while retaining phase-1 calibration rows verbatim as values."""
from pathlib import Path
import json,csv,re,hashlib,copy,collections
from formal_rules import RULES,new_rule,I,D,C,O,B,F,M
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads((R/p).read_text())
def write(p,v):(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
CAT=read('records/037_checks/evidence_catalog.json');DEL=read('records/037_checks/delivery_sources.json');PLAN=read('records/037_checks/new_patch_plan.json')
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
Q={
'lever_defaults':'本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。',
'lever_clean':'转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。唯一键重复仅保留一行。',
'pendo_clean':'Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.',
'pendo_time':'The work includes staging raw-field mapping, timestamp parsing, event-key generation, filtering and nullification; latest-record models; daily aggregates and calendar spines; and mart entities.',
'funnel':'product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;',
'health':'product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;',
'quality':'the data-quality report is summary-only;',
'rfm':'RFM account-level metrics are NULL placeholders;',
'lifecycle':'advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.',
'dashboard':'advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.',
'duplicates':'中间层按契约保留源业务数据的重复记录，不对 source IDs 做全局去重。下游按这些 ID 关联时，若上游相同 ID 对应多行，可能发生行数扩增；此项属于合同指定的重复保留行为。',
'random':'生命周期模拟交易数、活动量和依赖它们的派生指标按契约使用 `random()`，因此跨次执行不保证完全可复现；执行时间字段及基于当前日期的指标同样随运行时间变化。',
'ordering':'契约对来源重复记录以及部分聚合排序并未规定唯一 tie-breaker；按 DuckDB 实际行为保留未指定并列顺序，不额外引入业务假设。',
'country':'country alpha-2 冲突记录通过稳定字段排序保留一条，避免唯一键重复。',
'stage3':'staging 中无法满足必要名称、国家码格式/引用条件的记录被过滤；超出 1–999 的 numeric country code 置为 NULL。',
'daily':'日快照同一时间戳存在并列时按契约接受非确定性选择。',
'ads_time':'源时间戳含时区偏移，使用 DuckDB `try_strptime` 解析更新时间；统计日期转换为 DATE。',
'acquisition':'customer acquisition 的细分/建议规则未提供完整精确规则表，channel strategic recommendation 也未规定完整优先级；已采用保守、透明的 CASE 规则。'}
old={r['题目']+'_'+r['表']:r['主要原因类别'] for r in csv.DictReader((R/'records/019_annotations/019_summary.csv').open())}
cal={'impl-008_int_asana__task_projects','impl-021_int_klaviyo__person_metrics'}
objects=[r for r in csv.DictReader((R/'records/037_objects.csv').open()) if r['对象编号'] in cal]
points=[r for r in csv.DictReader((R/'records/037_points.csv').open()) if r['对象编号'] in cal]
audit=[a for a in read('records/037_checks/disclosure_audit.json') if a['对象编号'] in cal]
snap={'objects':objects,'points':points,'audit':audit};snapfile=R/'records/037_checks/calibration_working_rows_before_phase2.json'
if not snapfile.exists():write(str(snapfile.relative_to(R)),snap)
else:assert snap==read(str(snapfile.relative_to(R)))
assert set(RULES)==set(CAT) and len(CAT)==43
stoch={x['table']:x for x in read('records/019_stochastic_diagnostics.json')}
order={(x['object'],x['label']):x for x in read('records/037_checks/order_diagnostics.json')}
formal=[];allquotes=[]
# Relevant exact contract blocks; full initial event is separately verified, not inferred from cat.
def contract_quote(o,term):
 s=o['event_contract'];pat=re.search(r'(?m)^\s+- name: '+re.escape(term)+r'\s*$',s)
 if pat:
  end=re.search(r'(?m)^\s+- name: ',s[pat.end():]);end=pat.end()+end.start() if end else len(s)
  return s[pat.start():end].strip()
 # Business rules contain semantics beyond the output description, preserve the whole exact paragraph.
 k=s.find('business_logic:')
 if k>=0:
  end=s.find('\n      columns:',k)
  return s[k:end if end>=0 else len(s)].strip()
 at=s.lower().find(term.lower());at=max(0,at);return s[max(0,at-150):min(len(s),at+700)].strip()
for id,o in CAT.items():
 ps=copy.deepcopy(RULES[id]);d=DEL[o['task']];runs={r['label']:(r,o['runs'][0],o['rerun_path']) for r in o['runs']}
 nf=R/f'records/037_checks/rerun_{id}.json'
 if nf.exists():
  nr=read(str(nf.relative_to(R)));nb=next(x for x in nr['runs'] if x['label']=='baseline')
  for r in nr['runs']:
   if r['label']=='baseline':continue
   runs[r['label']]=(r,nb,str(nf.relative_to(R)))
   if r['label'] not in [p['label'] for p in ps]:
    plan=next(x for x in PLAN[id] if x['label']==r['label']);ps.append(new_rule(id,r['label'],plan['why']))
 assert ps,id
 for p in ps:
  label=p['label'];p['object']=id;p['name']=label
  # Category definitions are independent of old U/C/A/D labels.
  if p['grade']==1 and p['category'] in [D,C]:p['category']={D:'已说出的降级',C:'已说出的选择'}[p['category']]
  if label=='stochastic_evaluation':
   x=stoch[o['table']];r={'comparison':x['comparison'],'edits':[]};base={'comparison':x['baseline']};src='records/019_stochastic_diagnostics.json';kind='共同屏蔽契约允许的随机输出，仅诊断'
  elif (id,label) in order:
   x=order[id,label];r={'comparison':x['comparison'],'edits':[]};base={'comparison':x['baseline']};src='records/037_checks/order_diagnostics.json';kind='双侧只改呈现的诊断'
  else:
   r,base,src=runs[label];kind=r.get('kind','单处SQL干预；其他类的gold复现只作诊断')
  p['intervention']={'source':src,'label':label,'kind':kind,'levels':[],'edits':r.get('edits',[])}
  for b,a in zip(base['comparison']['levels'],r['comparison']['levels']):
   p['intervention']['levels'].append(dict(level=b['level'],baseline_rows=b['row_scale'],baseline_cells=b['cell_scale'],after_rows=a['row_scale'],after_cells=a['cell_scale'],row_reduction=b['row_scale']-a['row_scale'],cell_reduction=b['cell_scale']-a['cell_scale']))
  z=p['intervention']['levels'][0];p['reduction']=[z['row_reduction'],z['cell_reduction']]
  cq=contract_quote(o,p['term']);assert cq in o['event_contract']
  ce={'source':o['event_path'],'event':str(o['event'])+'.'+o['field'],'quote':cq}
  p['contract_evidence']=ce;allquotes.append(dict(object=id,point=label,kind='契约/在场',**ce))
  p['evidence_presence']='是' if p['category']==I else '否' if p['category']==M else '不适用'
  p['previously_correct']='否' if p['category'] in [I,M] else '不适用'
  p['data_algorithm_gate']='契约已规定算法/做法，按第5节归Intent。' if p['category']==I else ('已检查deleted_at完整契约：只给TIMESTAMP及空值规则，未指定解析算法。P由agent可见raw核实；未使用gold证伪。' if p['category']==M else '不适用')
  if p['category']==M:p['P']='raw.user中非空deleted_at文本可由直接TRY_CAST(... AS TIMESTAMP)解析。';p['data_refutation']={'source':'records/019_queries.json','task':'impl-002','table':'stg_pendo__user','kind':'核实','n':17,'failed_direct_but_substring_parses':12};p['presence_note']='初始契约只规定目标类型，列清单只能看到VARCHAR；未见agent查询直接转换失败的原始格式。单凭这些不能证伪P，所以证据在场=否。'
  if p['grade'] in [1,2]:
   q=Q[p['quote_key']];assert q in d['report'],(id,p['quote_key']);de=[{'source':d['path'],'event':str(d['event'])+'.args.final_thought','quote':q}]
   why='交付报告明确点到这张表/这类指标及其占位或选择。' if p['grade']==1 else '交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。'
  else:de=[ce];why='契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。'
  p['disclosure_evidence']=de;p['disclosure_reason']=why
  p['sql_evidence']=[]
  for ed in r.get('edits',[]):
   frag=ed['old'];idx=o['sql'].find(frag)
   if idx<0:
    # Frozen clocks are explicit rerun substitutions; point to frozen baseline when original differs.
    bs=(R/o['runs'][0]['sql_path']).read_text();idx=bs.find(frag);path=o['runs'][0]['sql_path']
   else:path=o['sql_path']
   if idx>=0:
    text=o['sql'] if path==o['sql_path'] else bs;start=text[:idx].count('\n')+1;end=start+frag.count('\n');p['sql_evidence'].append(dict(path=path,line_start=start,line_end=end,quote=frag))
  if not p['sql_evidence']:
   s=o['sql'];term=p['term'];idx=s.lower().find(term.lower());idx=max(0,idx);start=s.rfind('\n',0,idx)+1;end=s.find('\n',idx);end=len(s) if end<0 else end
   p['sql_evidence']=[dict(path=o['sql_path'],line_start=s[:start].count('\n')+1,line_end=s[:end].count('\n')+1,quote=s[start:end])]
  for se in p['sql_evidence']:allquotes.append(dict(object=id,point=label,kind='SQL',source=se['path'],event=None,quote=se['quote']))
 # rank isolated changes, row first then cells, without adding overlapping contributions.
 best=max(tuple(p['reduction']) for p in ps);winners=[p for p in ps if tuple(p['reduction'])==best and best>(0,0)]
 if not winners and all(p['category']==O for p in ps):winners=ps # stochastic order can reproduce official answer by chance
 assert winners,(id,best)
 for p in ps:p['role']=('主要' if len(winners)==1 else '并列') if p in winners else '参与' if tuple(p['reduction'])>(0,0) else '非原因'
 cats=sorted({p['category'] for p in winners});main=cats[0] if len(cats)==1 else '多因并列'
 conf='中' if any(p['confidence']=='中' for p in winners) or any(p['reduction'][0]<0 or p['reduction'][1]<0 for p in ps) else '高'
 combined='；'.join(f'{p["name"]}：{p["category"]}' for p in winners) if len(winners)>1 else ''
 objects.append({'benchmark':'DAComp','对象编号':id,'层':o['layer'],'主要原因':main,'并列项':combined,'是否只能组合修复':'否','把握':conf,'旧标签':old[id],'019旧标签':old[id]})
 formal.append(dict(object=id,layer=o['layer'],main=main,confidence=conf,old_019_verbatim=old[id],points=ps))
 md=[f'# {id}（037 正式批次）','',f'主要原因：**{main}**；把握：{conf}。019旧主要原因原样保留：`{old[id]}`，不作为新类别依据。','', '## 范围与材料','',f'- 层：{o["layer"]}；属于已核对的43张正式表。',f'- 契约：初始 event {o["event"]} 的 `{o["field"]}` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。',f'- 最终SQL：`{o["sql_path"]}`。',f'- 最终报告：`{d["path"]}`，finish {d["event"]} / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。',f'- CS及数据来源：`{o["source"]}`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。',f'- 019基线/干预：`{o["rerun_path"]}`；037补充：`records/037_checks/`。','', '## 逐点标注']
 for p in ps:
  label=p['label'];cat=p['category'];grade=p['grade'];src=p['intervention']['source']
  evsources=[src+'#'+label,'records/037_checks/evidence_catalog.json#'+id,'records/037_checks/disclosure_audit.json']
  if o['queries']:evsources.append('records/019_queries.json#'+o['table'])
  if p['category']==M:evsources.append('records/019_queries.json#stg_pendo__user')
  points.append({'benchmark':'DAComp','对象编号':id,'错误点名称':p['name'],'角色':p['role'],'类别':cat,'是否说出（五档）':levels[grade-1],'证据在场':p['evidence_presence'],'曾经理解对过':p['previously_correct'],'系统提示是否适用':'不适用','证据是复用还是新做':'复用019单改/查询；037逐点核契约与交付物'+('；037新做干预/诊断' if src.startswith('records/037') else ''),'证据来源':';'.join(evsources),'019旧标签':old[id]})
  audit.append({'benchmark':'DAComp','对象编号':id,'错误点名称':p['name'],'grade':grade,'是否说出':levels[grade-1],'019旧标签':old[id],'037类别':cat,'reason':p['disclosure_reason'],'evidence':p['disclosure_evidence'],'final_answer_or_report_sha256':d['report_sha256'],'final_answer':None})
  md+=['',f'### {p["name"]}','',f'- 类别：{cat}；角色：{p["role"]}；把握：{p["confidence"]}。',f'- 是否说出：第{grade}档（{levels[grade-1]}）。',f'- 证据在场：{p["evidence_presence"]}；曾经理解对过：{p["previously_correct"]}；系统提示：不适用。','',p['reason'],'','契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：','', '> '+p['contract_evidence']['quote'].replace('\n','\n> ')]
  if cat in [I,M]:md+=['',p['data_algorithm_gate'],'','曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。']
  if cat==M:md+=['','P：'+p['P'],'',p['presence_note'],'','反证：`records/019_queries.json` 中impl-002 / stg_pendo__user的只读raw核实，17行中12行直接解析失败但substring(1,23)成功。查询的是agent当时可见数据。']
  md+=['','SQL原处：']
  for se in p['sql_evidence']:md+=['',f'`{se["path"]}`，第 {se["line_start"]}–{se["line_end"]} 行：','', '```sql',se['quote'],'```']
  md+=['','单改/诊断：`'+src+'#'+label+'`。'+p['intervention']['kind']+'；与其自身固定时间基线比较。','', '| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |','|---|---:|---:|---:|']
  for z in p['intervention']['levels']:md.append(f'| {z["level"]} | {z["baseline_rows"]}/{z["baseline_cells"]} | {z["after_rows"]}/{z["after_cells"]} | {z["row_reduction"]}/{z["cell_reduction"]} |')
  if p['role']=='非原因':md+=['','本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。']
  md+=['','披露/相关信息原句：']
  for ev in p['disclosure_evidence']:md+=['',f'`{ev["source"]}`，event `{ev["event"]}`：','', '> '+ev['quote'].replace('\n','\n> ')]
  md+=['',p['disclosure_reason']]
 md+=['','## 规模、覆盖与不确定','', '主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。','', '未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。','', '如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。','', '复用核实/诊断查询：']
 for q in o['queries']:md+=['',f'`records/019_queries.json` / {q.get("kind","")}：', '```sql',q['sql'],'```','结果：`'+json.dumps(q.get('result'),ensure_ascii=False)+'`']
 if id=='impl-003_customer360__customer':md+=['','规则问题：按id结合的明确步骤与每id一行的grain互相冲突。可读成Intent（强调步骤）或Choice（不能同时满足）。本批采用Choice，置信中；026仅提供冲突事实，019旧标签仍保留U，不改规则。']
 if id=='impl-002_stg_pendo__user':md+=['','规则问题：时间解析也可能读成未规定解析方式的Choice。本点区分的是直接解析可成功这一可核实数据事实；反证来自raw，而非gold选了另一解析器，因此按Data，置信中。']
 if id=='impl-003_customer360__status':md+=['','规则问题：官方留存判错与019重跑恰好通过可以同时成立。这里沿用官方判错对象，重复运行未指定的聚合顺序可能对上；不凭这次0规模取消该表。']
 if id in ['impl-001_lever__hiring_manager_scorecard','impl-002_int_pendo__product_health_metrics','impl-002_int_pendo__conversion_funnel_analysis','impl-002_int_pendo__data_quality_checks']:md+=['','不确定：部分恢复公式的干预在其他默认输入仍错误时不能对齐gold，甚至增加差异；保留非原因而不外推整套模型已修复。恢复条件的文字代表若契约未固定，只用于测量，不能反过来当契约。']
 (R/f'records/037_annotations/037_{id}.md').write_text('\n'.join(line.rstrip() for line in '\n'.join(md).split('\n'))+'\n')
write('records/037_checks/formal_decisions.json',formal);write('records/037_checks/formal_quote_inventory.json',allquotes);write('records/037_checks/disclosure_audit.json',audit)
for name,rows in [('objects',objects),('points',points)]:
 with (R/f'records/036_{name}.csv').open() as f:fields=next(csv.reader(f))
 fields[-1]='019旧标签'
 with (R/f'records/037_{name}.csv').open('w',newline='') as f:w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows(rows)
print(json.dumps({'formal_objects':len(formal),'total_objects':len(objects),'total_points':len(points),'main_distribution':dict(collections.Counter(x['main'] for x in formal))},ensure_ascii=False))
