from pathlib import Path
import json,csv,hashlib,re,sys,copy
sys.dont_write_bytecode=True
from formal_rules import RULES,I,U,Q,O,F,B
from extra_plans import P
ROOT=Path.cwd();R=ROOT/'records';C=R/'040_checks';T=ROOT/'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01'
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else str(p)
rs=load(R/'022_decisions.json');plans=load(R/'022_patch_plan.json');catalog=load(C/'evidence_catalog.json');delivery=load(C/'delivery_sources.json');diagnostics=load(R/'022_diagnostics.json')
events={t:[(p,load(p)) for p in sorted((T/t/'agent/.events/sessions').glob('*/events/*.json'),key=lambda p:int(p.stem))] for t in ['impl-012','impl-013','impl-014']}
def eq(t,n,field,quote,kind='process'):
 p,e=next((p,e) for p,e in events[t] if e['id']==n);v=e
 for k in field.split('.'):v=v[k]
 assert quote in v,(t,n,field,quote)
 return {'path':rel(p),'event':n,'field':field,'quote':quote,'kind':kind}
def fq(path,quote,kind):
 assert quote in Path(path).read_text(),(path,quote)
 return {'path':rel(path),'field':'text','quote':quote,'kind':kind}
def contract_excerpt(con,anchor):
 if not anchor:return ''
 assert anchor in con,anchor
 k=con.index(anchor)
 if anchor.startswith('- name:'):
  end=con.find('\n      - name:',k+len(anchor));end=con.find('\n        - name:',k+len(anchor)) if end<0 else end
  return con[k:end if end>=0 else len(con)]
 # Exact clause, bounded at next business-logic delimiter or line end.
 ends=[x for x in [con.find(' - ',k+len(anchor)),con.find('\n',k+len(anchor))] if x>=0]
 end=min(ends) if ends else len(con)
 start=max(con.rfind(' - ',0,k)+3,con.rfind('\n',0,k)+1,0)
 start=max(start,k-250)
 return con[start:min(end,k+600)]
# Full-file calendar search: name keys vs references, no assumptions from downstream.
contract_path=Path(catalog[6]['contract_path']);full=contract_path.read_text();hits=[{'line':n,'text':s} for n,s in enumerate(full.splitlines(),1) if 'marketo__calendar_spine' in s]
calendar={'path':str(contract_path),'sha256':sha(contract_path),'line_count':len(full.splitlines()),'searched_patterns':['name: marketo__calendar_spine','marketo__calendar_spine','calendar','spine','max_date','1 week','7 day'],'exact_definition_matches':re.findall(r'^\s*-?\s*name:\s*[\"\x27]?marketo__calendar_spine[\"\x27]?\s*$',full,re.M),'references':hits,'result':'没有工具表定义；仅下游引用。下游明文上界由calendar spine定义，没有规定工具表终点。','config_path':'/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/config/layer_dependencies.yaml'}
assert not calendar['exact_definition_matches'];config=Path(calendar['config_path']).read_text();calendar['config_matches']=[{'line':n,'text':x} for n,x in enumerate(config.splitlines(),1) if 'calendar_spine' in x];save(C/'calendar_contract_search.json',calendar)
rawq=load(R/'022_queries.json')+load(R/'022_queries_retry.json');out=[];audit=[];quotes=[];process=[]
for i,r in enumerate(rs):
 oid=r['task']+'_'+r['table'];t=r['task'];pkg=load(r['full_json']);con=''.join(x['original_text'] for x in pkg['contract_specification']['blocks']);sql=pkg['agent_final_SQL'][0];assert Path(sql['path']).read_text().strip()==sql['text'].strip()
 oldfile=R/f'022_reruns_{oid}.json';oldrun=load(oldfile);baseline=oldrun['runs'][0]['comparison']['levels'];rule=copy.deepcopy(RULES.get(i,{}));excluded=[]
 runs={x['label']:(rel(oldfile),x) for x in oldrun['runs'][1:]}
 if i in [0,2]:
  d=next(x for x in diagnostics if x['index']==i)
  runs['unordered_merges']=('records/022_diagnostics.json',{'label':'unordered_merges','comparison':d['order_canonicalization'],'edits':[],'diagnostic_index':diagnostics.index(d)})
 if i in [21,22,24,25]:
  f=C/f'supplement_{oid}.json';d=load(f)
  for x in d['runs'][1:]:runs[x['label']]=(rel(f),x)
  if i in [21,22,24]:
   for x in d['runs'][1:]:
    col=x['label'].removeprefix('restore_');cat=B
    why='event15已明确写出该列源映射和转换意图；因旧源表名schema lookup失败生成NULL，event25只改FROM没有重生成投影。按代码自身意图证据归代码写错，逐列恢复。'
    if i==24 and col=='parent_id':cat=Q;why='原始entities列清单有parent，生成器没有parent_id→parent映射，最终整列NULL；没有正确映射意图证据，不随其他列一律判代码写错，按有候选列但未判断的降级。'
    if i==24 and col=='entity_name':why+=' 此处恢复agent原定entityid，不使用gold的entitytitle冒充agent意图；当前空主键过滤使该列单改没有贡献。'
    rule[x['label']]=(cat,why,'- name: '+col)
   excluded.append({'label':'placeholder_mapping','reason':'022整组恢复只作组级差异定位；主因排序改用040各列单改。'})
 if i in P:
  f=C/f'supplement_extra_{oid}.json';d=load(f)
  for spec in P[i]:
   run=next(x for x in d['runs'] if x['label']==spec['label']);runs[spec['label']]=(rel(f),run)
   # Column definitions suffice for related info; business logic independently reviewed.
   if spec['label']=='value_percentiles':anchor='value_tier via overall revenue percentile thresholds'
   elif spec['label']=='dependency_percentiles':anchor='dependency_level uses total_vendor_spend compared to percentile thresholds'
   else:
    col=re.search(r'(\w+)\s*$',spec['edits'][0][0]).group(1);anchor='- name: '+col
   rule[spec['label']]=(spec['category'],spec['reason'],anchor)
 if i>=26:
  for label in runs:
   if label=='preserve_duplicates':
    a=runs[label][1]['comparison']['levels'][0]
    if a['row_scale']==baseline[0]['row_scale'] and a['cell_scale']==baseline[0]['cell_scale']:
     excluded.append({'label':label,'reason':'原raw重复键查询为0组/没有本次去重差异；这是正确主键实现的无变化诊断，不虚构错误点。'});continue
    rule[label]=(O,'契约明确primary_key；agent按主键唯一化，gold保留重复行。去掉QUALIFY用于诊断，不表示应违反唯一性。若仅减格仍计参与。','primary_key:')
   elif label.startswith('timestamp_'):
    col=label.removeprefix('timestamp_');rule[label]=(U,'契约规定TIMESTAMP而未指定偏移字符串解析方法；agent格式解析成功、gold直接TRY_CAST为NULL。按材料未定选择处理，不以gold失败作为数据事实。','- name: '+col)
   elif label=='email_validation_order':rule[label]=(O,'契约先LOWER(TRIM)再验证，agent遵从；gold验证未trim的原邮箱，额外排掉5行。只改验证对象后与gold一致证明差异来源。','email = LOWER(TRIM(email))')
 if i==16:excluded.append({'label':'class_group','reason':'最终SQL已有l.class_id且GROUP BY ALL；022补丁重复加入该列，不是遗漏，不标错。'})
 obj={'id':oid,'index_022':i,'layer':r['layer'],'old_label':r['main'],'confidence':'高','contract_path':pkg['contract_specification']['source_path'],'contract_sha256':sha(pkg['contract_specification']['source_path']),'contract_lines':[[b['start_line'],b['end_line']] for b in pkg['contract_specification']['blocks']],'initial_prompt':catalog[i]['initial_prompt'],'contract_present':catalog[i]['complete_contract_present_in_initial_prompt'],'sql_source':sql['path'],'sql_sha256':sha(sql['path']),'package':r['path'],'baseline':baseline,'clock_control':oldrun.get('clock_control',[]),'source':oldrun.get('source'),'verification_queries':catalog[i]['verification_queries'],'verification_query_count':catalog[i]['verification_query_count_including_failures'],'points':[],'excluded_diagnostics':excluded,'rule_questions':[]}
 if i==6:obj['rule_questions'].append('报告“日历延伸至当前日期，并按lead created date起算”可被读成utils终点的具体说明，也可读成逐lead日历的组合说明；没有点名工具表且混合两张表，按用户一一对应要求保守记第2档。契约完整搜索无工具表定义，类别为未规定选择。')
 if i==10:obj['rule_questions'].append('条件求和空集返回NULL还是0：没有非空/默认明文。可将日常“总额”理解为0，但本轮不以gold实现补契约，按Unstated Choice，把握中。')
 if i==14:obj['rule_questions'].append('一客户一行grain与明确两次LEFT JOIN在重复上游下有张力；按可执行连接条款判遗漏Intent，不自行删第二次连接。')
 for label,(cat,reason,anchor) in rule.items():
  source,run=runs[label];single=run['comparison']['levels'];red=[baseline[0]['row_scale']-single[0]['row_scale'],baseline[0]['cell_scale']-single[0]['cell_scale']]
  grade=4;discreason='完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。';pquotes=[];ce=contract_excerpt(con,anchor)
  if ce:pquotes.append(fq(obj['contract_path'],ce,'contract'));pquotes.append(eq(t,1,'message',ce,'presence'))
  finish=delivery[t]['finish'][0];disc=''
  if i==4:grade=1;disc='原始活动表没有独立 `email_send_id`，发送表使用 `id` 映射；其他活动表也按原始活动 ID 输出 `email_send_id`。源数据未提供可确认的跨活动发送键，因此打开、点击、投递等跨事件连接存在来源标识的局限，计数仍按 contract 在各活动自身分组。'
  if i==5:grade=2;disc='依据 staging 契约去除缺少关键 ID/时间/必需属性的行，并对重复主键保留更新时间较新的记录（活动重复时保留较早记录）。这保全了声明的唯一粒度，但剔除记录不会进入后续分析。'
  if i==6:grade=2;disc='日历延伸至当前日期，并按 lead created date 起算。';pquotes.append(fq(obj['contract_path'],'The upper bound of dates is defined only by the calendar spine; no additional end-date filter is applied.','contract_context'))
  if i==9 and label=='accuracy_rules':grade=1;disc='数据质量模型输出总体报告、表统计和引用完整性检查；由于合同缺少可直接复用的完整业务规则细节实现，业务规则精确逐条合规率在该报告中未得到完整验证。将报告用于正式审计时应考虑这一限制。'
  if i==13:grade=2;disc='采用 TRY_CAST 安全解析原始日期/类型；不可解析的值成为 NULL。'
  if i==23:grade=2;disc='客户邮箱、电话按合同规定清洗或置空。'
  if i==25 or label.startswith('timestamp_'):
   grade=2;disc="原始 Qualtrics 时间文本带时区后缀（例如 `+0800`），DuckDB 直接 `try_cast(... AS TIMESTAMP)` 无法解析。日期相关 SQL 改用 `try_strptime(..., '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP`；不可解析日期在日期计算中排除。"
   if label=='cohort_month_gold_type':grade=4;disc=''
   if label=='keep_null_dates':grade=1;disc='无法按已观察到的带时区格式解析的日期仍保留在原文本字段，但不进入 cohort、30 日窗口及按日统计，可能造成日期类指标低估。'
  if i>=26 and label=='preserve_duplicates':grade=2;disc='重复主键记录按主键仅保留一条；合同未指定冲突记录排序规则，因此非主键字段冲突时，具体保留行不保证业务优先级，可能丢失冲突值。'
  if i==37 and label=='email_validation_order':grade=2;disc='缺失/无效关键 ID 及合同要求删除的非法状态、邮箱或必需字段记录予以剔除；非关键无效值置 NULL。'
  if disc:pquotes.append(eq(t,finish['event'],'args.final_thought',disc,'delivery'));discreason=('交付物以表名或一一对应功能点明本处处理。' if grade==1 else '交付物有适用于本类处理的通用说明，没有针对本表本处逐项说明。')
  if i==6:discreason='句子混合工具日历终点与逐lead日历起点，没有点名utils表，按一一对应覆盖要求记通用说明；不使用附带测试脚本。'
  if i==9 and label=='accuracy_rules':discreason='“数据质量模型”一一对应本表，并明确业务规则逐条合规率未完整验证；这覆盖本表accuracy_score的计算缺口，不推广到其他NetSuite指标。'
  if i in [12,15,18] and cat==Q:discreason='finish只有“高阶指标受模拟数据/合同指定占位日期及字段可用性影响”，没有说明本处用常量/透传代替计算；该句并非本类省略计算的披露。event1已有指标定义，记第4档。'
  if grade==1:cat={U:'已说出的选择',Q:'已说出的降级'}.get(cat,cat)
  # Exact code edit evidence (SQL is not disclosure unless a comment).
  for e in run.get('edits',[]):
   old=e['old'];new=e['new'];origold=old
   for cl in oldrun.get('clock_control',[]):
    origold=origold.replace(cl['replacement'],'current_timestamp' if 'timestamp' in cl['pattern'] else 'current_date')
   if old in sql['text']:pquotes.append(fq(sql['path'],old,'sql'))
   elif origold in sql['text']:pquotes.append(fq(sql['path'],origold,'sql'))
  if label=='unordered_merges':
   ex="STRING_AGG(DISTINCT merged_lead_ids, ', ')";assert ex.lower() in sql['text'].lower();k=sql['text'].lower().index(ex.lower());pquotes.append(fq(sql['path'],sql['text'][k:k+len(ex)],'sql'))
  if i in [21,22,24]:
   command=next(e['args']['command'] for p,e in events[t] if e['id']==15);mapping=next(l for l in command.splitlines() if l.startswith("'"+r['table']+"'"));pquotes.append(eq(t,15,'args.command',mapping,'intent'))
   repair=next(e['args']['command'] for p,e in events[t] if e['id']==25);rp=next(l for l in repair.splitlines() if 'sql/staging/'+r['table']+'.sql' in l);pquotes.append(eq(t,25,'args.command',rp,'process'))
   if i==24 and label=='restore_parent_id':
    content=next(e['content'] for p,e in events[t] if e['id']==12);line=next(l for l in content.splitlines() if 'netsuite2_entities_data :' in l);pquotes.append(eq(t,12,'content',line,'related'))
   discreason='event15/25显示生成投影及只修FROM的动作，但没有点出该列仍是NULL的冲突；event1契约/列清单在场。代码修复动作本身不等于意识到这一处，记第4档。'
  prev='否' if cat in [I,'Data Misconception'] else '不适用';prev_reason='逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。' if prev=='否' else '非探索类别，不填。'
  if i==23 and label=='email_order':
   command=next(e['args']['command'] for p,e in events[t] if e['id']==15);line=next(l for l in command.splitlines() if 'CASE WHEN email_address IS NULL OR regexp_full_match' in l);pquotes.append(eq(t,15,'args.command',line,'previous_correct'));prev='是';prev_reason='event15先对email_address验证，再在THEN lower(trim)；仅证明本点先验后清顺序，不声称当时整表正确。'
  pt={'name':label,'category':cat,'confidence':'中' if cat==U or i in [17,24] else '高','reason':reason,'disclosure':grade,'disclosure_reason':discreason,'evidence_present':'是' if cat in [I,'Data Misconception'] else '不适用','presence_reason':'相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。' if cat in [I,'Data Misconception'] else '非探索类别，不填。','previously_correct':prev,'previously_correct_reason':prev_reason,'system_prompt':'不适用','quotes':pquotes,'rerun_source':source,'rerun_label':label,'diagnostic_index':run.get('diagnostic_index'),'baseline':baseline,'single_change':single,'reduction':red,'edits':run.get('edits',[]),'new_evidence':source.startswith('records/040_')}
  obj['points'].append(pt)
 best=max(tuple(x['reduction']) for x in obj['points']);w=[x for x in obj['points'] if tuple(x['reduction'])==best and best>(0,0)];assert w,oid
 cats=set(x['category'] for x in w);obj['main']=next(iter(cats)) if len(cats)==1 else '多因并列';obj['ties']=[{'name':x['name'],'category':x['category']} for x in w] if len(w)>1 else [];obj['combination_only']=False
 for p in obj['points']:
  p['role']=('主要' if len(w)==1 else '并列') if p in w else ('参与' if tuple(p['reduction'])>(0,0) else '非原因')
  if p['role']=='非原因':p['noncause_note']='存在未确立的前提，但不是判错原因' if p['category'] in [I,U,Q,'已说出的选择','已说出的降级','Data Misconception'] else '此实现/形式差异已定位，但单改不减少当前判错规模；不计参与因素。'
  audit.append({'对象编号':oid,'错误点名称':p['name'],'grade':p['disclosure'],'reason':p['disclosure_reason'],'evidence':[q for q in p['quotes'] if q['kind'] in (['delivery'] if p['disclosure'] in [1,2] else ['presence','process','related','intent'])]})
  quotes.extend({'object':oid,'point':p['name'],**q} for q in p['quotes'])
 obj['confidence']='中' if any(p['confidence']=='中' for p in w) else '高'
 out.append(obj)
 # All event IDs that mention the table or decisive column retained as audit; no raw payload copies.
 reviewed=[]
 terms={r['table']}|{x['name'].removeprefix('zero_').removeprefix('restore_') for x in obj['points']}
 for path,event in events[t]:
  command=event.get('args',{}).get('command','');content=event.get('content','');message=event.get('message','')
  if event.get('action')=='finish' or event['id']==1 or any(term in command+content+message for term in terms):reviewed.append({'event':event['id'],'path':rel(path),'sha256':sha(path),'action':event.get('action') or event.get('observation'),'truncated_marker':bool(re.search(r'\btruncated\b',content,re.I))})
 process.append({'object':oid,'events_examined':len(events[t]),'relevant_events':reviewed,'initial_contract_block_exact_match':catalog[i]['complete_contract_present_in_initial_prompt'],'delivered_sql_has_comments':catalog[i]['sql_comment_lines'],'excluded_tests':'impl-012附带测试脚本不算交付物；程序注释也不算交付SQL注释。'})
save(C/'formal_working.json',out);save(C/'formal_disclosure_audit.json',audit);save(C/'formal_quote_inventory.json',quotes);save(C/'process_review.json',process)
print('formal',len(out),'points',sum(len(o['points']) for o in out))
from collections import Counter
print('main',Counter(o['main'] for o in out));print('categories',Counter(p['category'] for o in out for p in o['points']));print('roles',Counter(p['role'] for o in out for p in o['points']))
