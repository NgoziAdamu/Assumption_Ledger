from pathlib import Path
import json,csv,hashlib,re,io,copy,sys
sys.dont_write_bytecode=True
from formal_rules import RULES,I,U,Q,D,O,B
R=Path('records');C=R/'042_checks';T=Path('data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01')
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
cat=load(C/'evidence_catalog.json');delivery=load(C/'delivery_sources.json');old={x['task']+'_'+x['table']:x['category'] for x in load(R/'023_decisions.json')}
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
events={t:{int(p.stem):(p,load(p)) for p in (T/t/'agent/.events/sessions').glob('*/events/*.json')} for t in {x['task'] for x in cat}}
def eq(t,n,field,quote,kind):
 p,e=events[t][n];v=e
 for k in field.split('.'):v=v[k]
 assert quote in v,(t,n,field,quote)
 return dict(path=str(p),event=n,field=field,quote=quote,kind=kind)
def fq(path,quote,kind):
 assert quote in Path(path).read_text(),(path,quote)
 return dict(path=str(path),field='text',quote=quote,kind=kind)
def excerpt(con,anchor):
 assert anchor in con,anchor
 k=con.index(anchor)
 if anchor.startswith('- name:'):
  m=re.search(r'\n\s*- name:',con[k+len(anchor):]);end=k+len(anchor)+m.start() if m else len(con)
  return con[k:end].rstrip()
 ends=[z for z in [con.find(' - ',k+len(anchor)),con.find('\n',k+len(anchor)),con.find(' • ',k+len(anchor))] if z>=0]
 end=min(ends) if ends else len(con)
 return con[k:min(end,k+850)].rstrip()
DISC={
 'typed_null':'对原始字段中不存在的合同字段采用类型化 NULL',
 'greenhouse_dedup':'staging 对声明为主键的空值行进行过滤，并按主键分组只保留一条记录以满足唯一性',
 'history_key':'History 源数据没有契约所需的 `history_unique_key` 原始列，因此以实体记录 ID 与 Fivetran 起止时间生成确定性 MD5 键，用于稳定标识历史版本。',
 'sf_invalid':'严重问题按契约删除行或过滤软删除数据；非关键字段中的无效关系键、格式值或数值按契约置空；规范化处理保留可用记录。',
 'session_date':'会话来源原始日期/下载日期字段以字符串形式提供；使用 `TRY_CAST` 转为日期。会话 staging 按契约过滤无效、未来及 2020-01-01 以前日期',
 'phone_intercom':'电话标准化/无效字段置空',
 'klaviyo_ids':'无效关键 ID 和非法邮件记录被排除',
 'person_phone':'电话号码按 E.164-like 格式加前缀 `+`，未推断国家码。'
}
RAW={
 'impl-015':'013显示30张raw列/类型不同，行数均未变。event45为解决同库重复ATTACH的Unique file handle conflict，改用fetchdf/register复制raw；这是agent改动，照常标注。直接源按下面逐表检查；CS表使用gold上游，不将本题全部raw变化归给该表。',
 'impl-016':'raw.person_contact_email_address由7284降至2448，少4836行；已回查85个事件及013/015记录，改动步骤和原因均未找到。不得编造是哪次run导致。当前stg_position直读position没有该变化；三个非staging表采用gold上游，不能把email原始减量直接计入本表CS误差。',
 'impl-017':'013/015的变更发生在scheduled_interview_snowflake，gold raw也有同样变化；本批七张staging的直接源不在变更清单，两个marts用gold上游。benchmark加载导致是015推测，非agent行为的独立证明；按用户指定口径照常标注。',
 'impl-018':'013未发现raw结构/类型/行数变化；这项检查不被扩张为所有格子内容的字节等同。staging用agent留存raw，marts用gold上游。',
 'impl-019':'原始session相关变化在gold raw同样存在；按015结论及本次要求照常标注，staging仍使用agent留存raw。benchmark加载原因仅记为推测；两个marts按CS取gold上游。',
 'impl-020':'原始数据变化在gold raw同样存在，包含本批两张staging直接源。按指定口径用agent留存raw并照常标注，列错位据此核查；benchmark加载原因是015推测，不归为agent自己改raw。',
 'impl-021':'五张raw均有013/015记录的变化，gold raw也包含变化；按指定口径用agent留存raw标五张staging，intermediate用gold上游。ID稀疏是实际可见事实，其形成原因未查证，不能从稀疏反推agent删raw。'
}
OUT=[];AUDIT=[];QUOTES=[];SEARCH=[]
for x in cat:
 oid=x['object_id'];t=x['task'];table=x['table'];con='\n'.join(z['original_text'] for z in x['contract_blocks']);original_sql=Path(x['agent_sql']).read_text();rules=copy.deepcopy(RULES[table]);runs={}
 for s in x['rerun_sources']:
  d=load(s['path'])
  for a in d['runs']:
   if a['label']!='baseline':runs[a['label']]=(s['path'],a)
 oldrun=load(R/f'023_reruns_{oid}.json');baseline=oldrun['runs'][0]['comparison']['levels']
 for prefix in ['supplement','diagnostic']:
  f=C/f'{prefix}_{oid}.json'
  if f.exists():
   d=load(f);assert d['baseline_matches_023']
   for a in d['runs'][1:]:runs[a['label']]=(str(f),a)
 obj=dict(id=oid,task=t,table=table,layer=x['layer'],old_label=old[oid],main='',confidence='高',points=[],raw_review=RAW[t],raw_direct_sources=x['raw_direct_sources'],raw_policy=x['raw_policy'],contract_path=x['contract_path'],contract_sha256=x['contract_sha256'],sql_source=x['agent_sql'],sql_sha256=x['agent_sql_sha256'],package=x['package'],baseline=baseline,clock_control=oldrun['clock_control'],source=oldrun['source'],verification_queries=x['verification_queries'],verification_query_count=x['verification_query_count_including_failures'],combination_only=False,excluded_diagnostics=[],rule_questions=[])
 if table=='stg_salesforce__contact_history':
  obj['verification_query_count']+=2;obj['verification_queries'].append(dict(source='records/042_checks/new_verification_queries.json',array_index=0,label='id与历史版本（同SQL执行2次，保守计2条）'))
 for r in rules:
  name=r['name'];category=r['category'];ce=excerpt(con,r['anchor']);quotes=[fq(x['contract_path'],ce,'contract'),eq(t,1,'message',ce,'contract_presence')];grade=r.get('grade',4)
  disc_reason='event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。'
  disc_quotes=[quotes[1]]
  if 'disclosure' in r:
   dq=eq(t,delivery[t]['finish'][0]['event'],'args.final_thought',DISC[r['disclosure']],'delivery');quotes.append(dq);disc_quotes=[dq]
   disc_reason='最终报告有适用于此类处理的通用说明，未逐表点名本处，记第2档。' if grade==2 else '最终报告使用一一对应功能名称点明本处做法，记第1档；仅覆盖所说的处理。'
   if r['disclosure']=='session_date':disc_reason='“会话 staging”一一对应app_session_daily，点明TRY_CAST及日期过滤，覆盖三个解析过滤点；不推广至其他feed或版本号规则。'
   if r['disclosure']=='person_phone':disc_reason='本题只有person staging输出phone_number，电话号码功能一一对应；该句点明加+而不推断国家码。类别Other不因第1档改名。'
   if r['disclosure']=='history_key':disc_reason='“History”涵盖account/contact/opportunity三张history，未一一对应contact_history；因此只记第2档。该句讲生成键和精确重复，不覆盖仅按实体id删不同版本。'
  if r.get('special')=='invoice_override':
   quotes.extend([eq(t,17,'args.command',"'sales_item_item_id':'sales_item_item_id'",'correct_mapping'),eq(t,21,'args.command',"'sales_item_item_id':'item_id'",'overriding_mapping')]);disc_quotes=quotes[-2:]
   disc_reason='event17已有正确同名映射，event21 special覆盖，未解释差别或点出冲突；这是第4档，不把前后代码变化本身自动算意识到疑问。'
   obj['rule_questions'].append('invoice_line：有正确映射再被special覆盖的直接代码证据，按第6节代码写错。若把special看作有意重解字段，可读成Data；轨迹没有解释该重解。本轮用可见的先正确后覆盖证据，把握中。')
  if r.get('special')=='order_mapping':
   q=eq(t,57,'args.command',"# Correct field source mapping; canonical foreign keys should remain FK columns, not the row's own id.",'correct_intent');quotes.append(q);disc_quotes=[q]
   disc_reason='event57点明正确的外键来源原则，但修复列表漏order；没有点出order仍违背该原则。按v3.2正确想法与代码冲突未被意识到仍第4档；临时脚本注释不是交付物。'
  if r.get('special')=='intercom_mapping':
   q1=eq(t,25,'args.command',"('conversation_contact_history','contact_id::varchar as contact_id, try_cast(conversation_id as bigint) as conversation_id')",'alternative_reading')
   q2=eq(t,35,'args.command','try_cast(conversation_id as varchar) as contact_id,\n    try_cast(contact_id as bigint) as conversation_id','alternative_reading')
   q3=eq(t,22,'content',"('5ed93beb39021efc4ccd4ea5', '156643300000684'",'mapping_sample')
   quotes.extend([q1,q2,q3]);disc_quotes=[q1,q2,q3]
   disc_reason='event22看到了列与样例；event25同名映射、event35互换映射，但未找到比较本关系表两种映射结果或点出本处疑问的文字。不能仅凭前后改代码推定第3档，保守记第4档。finish只点名conversation part错位，不推广到conversation contact关系表。'
  if r.get('special')=='klaviyo_sparse':
   tab=table.removeprefix('stg_klaviyo__');counts={'campaign':(200,2),'flow':(79,1),'metric':(29,1)};total,n=counts[tab]
   q1=eq(t,20,'content',f'{tab} [({total}, {n}'+(', 2' if tab=='campaign' else '')+')]','raw_count')
   q2=eq(t,23,'args.command',"for db in ['klaviyo_start.duckdb','klaviyo.duckdb']:",'alternative_source_probe')
   q3=eq(t,24,'content',f'klaviyo_start.duckdb {tab} ({total}, {n}, {n})','initial_probe_result');quotes.extend([q1,q2,q3])
   r['process_awareness']={'has_sign_of_doubt':True,'basis':'event19/20计数本身不足；随后event23/24比较初始库与留存库、带引号/不带引号ID，实际排查两种读取/来源解释，构成第3档的过程疑问迹象。第二库无schema报错，不声称完成了两库比较；初始库计数已返回。','limits':'未点明丢失百分比，没有证明ID稀疏的成因；event27/29修邮件正则不是ID问题的意识证据。','final_grade_precedence':'有第2档交付通用说明，最终填第2档，不能写成交付物完全未提。','raw_rows':total,'nonnull_ids':n,'null_ids':total-n,'null_percent':round((total-n)*100/total,4)}
   disc_reason+=' 单列的构建行数不是说明丢失约99%；中间进一步排查ID来源/大小写存在疑问迹象，但最终第2档优先。'
  if grade==1 and category==U:category='已说出的选择'
  if grade==1 and category==Q:category='已说出的降级'
  if r.get('mode')=='tolerance':
   source=f'records/023_reruns_{oid}.json';run='baseline';after=copy.deepcopy(baseline);red=None;scale_method='仅同钟L0～L3诊断；只有同一Other原因，无实际单改排名'
  else:
   source,a=runs[name];run=a['label'];after=a['comparison']['levels'];red=[baseline[0]['row_scale']-after[0]['row_scale'],baseline[0]['cell_scale']-after[0]['cell_scale']];scale_method='双侧逐列屏蔽诊断（Other定位，非agent SQL修复）' if r.get('diagnostic') else '指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）'
   if a.get('edits'):
    # 运行时固定字面值可能只出现在clock-controlled SQL；其余原表达式直接引最终交付SQL。
    for e in a['edits']:
     if e['old'] in original_sql:quotes.append(fq(x['agent_sql'],e['old'],'delivered_sql_expression'))
  presence=r.get('presence','是') if category in [D,I] else '不适用';ever='否' if category in [D,I] else '不适用'
  p=dict(name=name,category=category,confidence=r.get('confidence','高'),reason=r['reason'],premise=r.get('premise',''),grade=grade,disclosure=levels[grade-1],disclosure_reason=disc_reason,presence=presence,presence_reason=('event1原始提示含完整相关契约，逐句匹配成功。' if presence=='是' else '只看见相关字段/样例，未找到足以定下本点P的全量唯一性或覆盖核实出现在轨迹；不能用本次查询反填证据在场。' if presence=='否' else '非探索类别不填。'),ever_correct=ever,ever_correct_reason=('按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。' if ever=='否' else '非探索类别不填。'),system_prompt='不适用',baseline_levels=baseline,after_levels=after,reduction=red,run_source=source,run=run,scale_method=scale_method,quotes=quotes,process_awareness=r.get('process_awareness'),evidence_use='复用+新做' if '/042_checks/' in source or table=='stg_salesforce__contact_history' else '复用')
  if table=='workday__employee_overview' and name=='comp_ebe_join':p['confidence']='中'
  obj['points'].append(p)
  AUDIT.append({'对象编号':oid,'错误点名称':name,'grade':grade,'是否说出':levels[grade-1],'category':category,'decision':disc_reason,'evidence':disc_quotes,'sql_path':x['agent_sql'],'sql_comments':x['sql_comment_lines'],'final_event':delivery[t]['finish'][0]['event'],'final_checked':True,'temporary_script_comments_count_as_delivery':False,'process_awareness':p['process_awareness']})
  QUOTES.extend(dict(object_id=oid,name=name,**q) for q in quotes)
  if category in [I,D,B]:
   terms=set([table,name]+re.findall(r'\b[a-z]+_[a-z_]+\b',r['reason']+r['anchor']))
   matches=[]
   for n,(ep,e) in sorted(events[t].items()):
    s=e.get('args',{}).get('command','')+'\n'+e.get('content','')
    ls=[line for line in s.splitlines() if any(term in line for term in terms)]
    if ls:matches.append(dict(event=n,path=str(ep),matching_line_count=len(ls),excerpts=ls[:5]))
   SEARCH.append(dict(object=oid,point=name,terms=sorted(terms),event_count=len(events[t]),events=matches,limit='机械检索便于回查；不是仅凭无命中就证明不存在意识。'))
 if table=='stg_intercom__conversation_contact_history':
  obj['combination_only']=True;obj['combination_source']='records/042_checks/supplement_'+oid+'.json';obj['combination_run']='mapping_combination';obj['combination_after']=load(obj['combination_source'])['runs'][1]['comparison']['levels'];assert all(p['reduction']==[0,0] for p in obj['points'])
  for p in obj['points']:p['role']='并列'
 elif len(obj['points'])==1 and obj['points'][0]['reduction'] is None:obj['points'][0]['role']='主要'
 else:
  best=max(tuple(p['reduction']) for p in obj['points']);assert best>(0,0),oid
  winners=[p for p in obj['points'] if tuple(p['reduction'])==best]
  for p in obj['points']:p['role']=('主要' if len(winners)==1 else '并列') if p in winners else '参与' if tuple(p['reduction'])>(0,0) else '非原因'
 winners=[p for p in obj['points'] if p['role'] in ['主要','并列']];cats=sorted(set(p['category'] for p in winners));obj['main']=cats[0] if len(cats)==1 else '多因并列';obj['ties']='；'.join(p['name']+':'+p['category'] for p in winners) if len(winners)>1 else '';obj['confidence']='中' if any(p['confidence']=='中' for p in winners) else '高'
 if table=='quickbooks__general_ledger':obj['confidence']='中';obj['ranking_note']='两列Other，无法构造改变允许并列顺序的可靠独立SQL修复；同宽逐列屏蔽均减少23907格作为定位。按第7节候选同类无需强造不同类排序，主因Other，把握中。'
 if table=='int_klaviyo__events':obj['confidence']='中';obj['ranking_note']='两列均Other；双侧屏蔽inter_event_minutes减少1行2格，session_seq减少0行1格，定位主因前者。诊断减量非可执行修复的因果收益，类别在同类候选下不受此限制影响，把握中。'
 if table=='greenhouse__application_history':obj['ranking_note']='唯一Other点，以同钟L0～L3差异及契约定位，不虚构修复。'
 used={p['run'] for p in obj['points']}
 for label,(s,a) in runs.items():
  if label not in used:
   reasons={'comp_base_multiplicity':'旧补丁仅按position扩增，没有补齐worker键，不能作为正确意图的修复；以comp_ebe_join替代。','similar_group':'同时改计数及组织来源，已拆成两个042单改；原混合补丁不参与排序。','history_key':'旧补丁使用created_date而不是gold运行时刻；用相同固定时刻history_key_clock替代。','revenue_range':'旧补丁同时变精度与范围，已拆开，不能把精度收益算范围收益。','left_conversation':'改为从part出发LEFT JOIN仍不能覆盖无part的conversation；不是覆盖前提的有效修复，以conversation_coverage代替。','mapping_combination':'单列为组合诊断，非单点。'}
   obj['excluded_diagnostics'].append(dict(label=label,source=s,reason=reasons.get(label,'未作为独立错误点重复计入；见对应逐点证据。')))
 if table=='int_intercom__conversation_part_aggregates':obj['rule_questions'].append('026的020-5提出Intent/Data边界：For each conversation规定输出范围但未规定连接算法。本轮按P“每个对话都有part”的可核实覆盖事实归Data（手册第4节也以此为例），而非从gold的LEFT JOIN逆推Intent；把握中。')
 if table=='stg_salesforce__contact_history':obj['rule_questions'].append('history实体ID去重不是契约唯一性要求；新查版本关系证明P错误。event77只去掉account_history去重，无明确组级疑问文字，不据此把contact_history提高到第3档或曾理解对过。其单改增差，故不算参与因素。')
 OUT.append(obj)
save(C/'formal_working.json',OUT);save(C/'formal_quote_inventory.json',QUOTES);save(C/'formal_process_search.json',SEARCH)
# 既有校准字节不改。每次构建从封存的两个CSV前缀追加39正式表，保证可重复执行。
for kind in ['objects','points']:
 prefix=(C/f'phase1_{kind}_prefix.csv').read_bytes();header=next(csv.reader(io.StringIO(prefix.decode())));buf=io.StringIO(newline='');wr=csv.DictWriter(buf,fieldnames=header,lineterminator='\n')
 for o in OUT:
  if kind=='objects':wr.writerow(dict(zip(header,['DAComp',o['id'],o['layer'],o['main'],o['ties'],'是' if o['combination_only'] else '否',o['confidence'],o['old_label'],o['old_label']])))
  else:
   for p in o['points']:wr.writerow(dict(zip(header,['DAComp',o['id'],p['name'],p['role'],p['category'],p['disclosure'],p['presence'],p['ever_correct'],'不适用',p['evidence_use'],f"records/042_annotations/042_{o['id']}.md；{p['run_source']}#{p['run']}；records/042_checks/quote_checks.json",o['old_label']])))
 (R/f'042_{kind}.csv').write_bytes(prefix+buf.getvalue().encode())
original_audit=[x for x in load(C/'disclosure_audit.json') if x['对象编号'] in load(R/'042_scope.json')['calibration']];assert len(original_audit)==3;save(C/'disclosure_audit.json',original_audit+AUDIT)
for o in OUT:
 lines=[f"# 042 正式标注：{o['id']}",'','## 任务','',f"按冻结v3.2第3～8节逐点重标；层：{o['layer']}。",'','## 结论','',f"主要原因：**{o['main']}**；把握{o['confidence']}；{len(o['points'])}点。只能组合修复：{'是' if o['combination_only'] else '否'}。023旧主要原因`{o['old_label']}`仅存档。",'','## 详细发现','','### 比较口径与原始数据','',o['raw_review'],'',f"直接raw逐表013核对：`{json.dumps(o['raw_direct_sources'],ensure_ascii=False)}`。",'',f"重跑输入：`{o['source']}`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`{json.dumps(o['clock_control'],ensure_ascii=False)}`。",'', '先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。', '',o.get('ranking_note','')]
 for p in o['points']:
  lines.extend(['',f"### {p['name']}",'',f"**{p['category']}**；{p['role']}；把握{p['confidence']}。",'',p['reason']])
  if p['premise']:lines+=['','P：'+p['premise']]
  lines+=['',f"是否说出：第{p['grade']}档——{p['disclosure']}。{p['disclosure_reason']}",'',f"证据在场：{p['presence']}。{p['presence_reason']}",'',f"曾经理解对过：{p['ever_correct']}。{p['ever_correct_reason']} 系统提示是否适用：不适用。",'',f"证据：{p['evidence_use']}；`{p['run_source']}` / `{p['run']}`。{p['scale_method']}。",'','| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |','|---|---:|---:|---:|---:|']
  for b,a in zip(p['baseline_levels'],p['after_levels']):lines.append(f"| {b['level']} | {b['row_scale']} | {a['row_scale']} | {b['cell_scale']} | {a['cell_scale']} |")
  lines+=['',f"L0减少：{p['reduction']}（行、格）。" if p['reduction'] is not None else '同钟基线即上表；不把L2容差清零伪装成SQL单改。']
  if p['role']=='非原因':lines+=['','本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。']
  if p['process_awareness']:lines+=['','026单独过程核对：','```json',json.dumps(p['process_awareness'],ensure_ascii=False,indent=2),'```']
  for q in p['quotes']:
   lines+=['',f"原句（{q['kind']}）：`{q['path']}` / {('event '+str(q['event'])+' / ') if 'event' in q else ''}`{q['field']}`。",'','```text',q['quote'],'```']
 if o['combination_only']:lines+=['','### 组合诊断','',f"两处各单改均减少0行0格；`{o['combination_source']}` / mapping_combination从8066行16132格到L0～L3全0。两点同为Other，单列只能组合修复，不虚报各自收益。"]
 if o['excluded_diagnostics']:lines+=['','### 排除的旧控制/混合补丁','']+[f"- `{a['source']}#{a['label']}`：{a['reason']}" for a in o['excluded_diagnostics']]
 lines+=['','## 证据来源','',f"- 契约：`{o['contract_path']}`；SHA-256 `{o['contract_sha256']}`。",f"- 最终SQL：`{o['sql_source']}`；SHA-256 `{o['sql_sha256']}`。",f"- 023材料包：`{o['package']}`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。",'- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。','- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。',f"- 核实预算（含复用/失败的保守上限）：{o['verification_query_count']}条；诊断不计5条上限。"]
 for q in o['verification_queries']:lines.append(f"- 查询：`{q['source']}` 数组索引{q['array_index']}，{q['label']}。")
 lines+=['','## 不确定或没查到的（含规则问题）','']+(o['rule_questions'] or ['没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。'])+['','## 建议的下一步','','交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。','']
 (R/'042_annotations'/f"042_{o['id']}.md").write_text('\n'.join(lines))
print(json.dumps({'objects':len(OUT),'points':sum(len(o['points']) for o in OUT),'quotes':len(QUOTES),'audit':len(AUDIT)},ensure_ascii=False))
