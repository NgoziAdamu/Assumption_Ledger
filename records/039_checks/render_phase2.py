from pathlib import Path
import json,csv,hashlib,re,io,collections
from formal_rules import rules,notes,I,U,D,O,B
R=Path('records');C=R/'039_checks';A=R/'039_annotations'
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
cat=load(C/'evidence_catalog.json');delivery=load(C/'delivery_sources.json');snapshot=load(C/'calibration_working_rows_before_phase2.json');handoff=load(C/'phase1_handoff.json');calids={o['对象编号'] for o in snapshot['objects']};audit=list(snapshot['audit']);quotes=[q for q in load(C/'quote_inventory.json') if q['object'] in calids];orows=[];prows=[];working=[]
old={r['题目']+'_'+r['表']:r['主要原因类别'] for r in csv.DictReader(open(R/'021_annotations/021_summary.csv'))}
for x in load(C/'fact_corrections.json')['025']:old[x['object']]=x['old_label_after_025']
raw={x['object']:x for x in load(C/'raw_integrity_review.json')}
process=[]
for task in ['impl-008','impl-009','impl-010','impl-011']:
 path=Path(next(x for x in cat if x['object'].startswith(task))['event_path']).parent
 evs=[(p,load(p)) for p in sorted(path.glob('*.json'),key=lambda p:int(p.stem))]
 process.append({'task':task,'events_scanned':len(evs),'events':[{'path':str(p),'id':v['id'],'sha256':sha(p),'thought':v.get('args',{}).get('thought','')} for p,v in evs],'review':'初始完整契约、写SQL命令、后续改写和finish已核读；不把仅写打算如何做视为第3档。探索点未发现其单点正确实现后又回退的明确证据；代码自身正确表达另列代码写错。'})
 for id in ([35,39] if task=='impl-009' else []):
  p,v=next((p,v) for p,v in evs if v['id']==id);process[-1].setdefault('generator_evidence',[]).append({'path':str(p),'event':id,'field':'args.command','command':v['args']['command']})
save(C/'process_review.json',process)
for i,o in enumerate(cat):
 key=o['object'];task=key.split('_')[0];sql=Path(o['agent_sql']).read_text();pkg=Path(o['package']).read_text();contract=re.search(r'```yaml\n([\s\S]*?)\n```',pkg)[1];initial=load(o['event_path']);assert contract in initial['args']['content'];finish=delivery[task]['finish'][0];fq=load(finish['path']);assert fq['args']['final_thought']==finish['text']
 # One common exact quote per table, referenced by all points; point SQL and disclosure remain individual.
 cq={'object':key,'point':'__common_contract__','kind':'process','source':o['event_path'],'event':1,'field':'args.content','quote':contract};quotes.append(cq)
 sq={'object':key,'point':'__common_sql__','kind':'sql','source':o['agent_sql'],'field':'text','quote':sql};quotes.append(sq)
 obj={**o,'annotation_status':'complete','points':[],'rules':notes.get(i,[]),'old_label':old[key]}
 text=[f'# {key}（039，v3.2正式表）','','## 任务','','按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。','','## 结论','']
 if key in raw:
  obj.update(main='不可评估',confidence='高',combination_only=False,baseline=None)
  text += ['**不可评估**。原始数据一致性诊断满足“初始库＝agent留存库≠标准答案库”，按第6节停止agent错因归类。没有逐点五档行。','','## 详细发现','','| raw表 | 初始行 | agent行 | gold行 | 初始/agent SHA-256 | gold SHA-256 |','|---|---:|---:|---:|---|---|']
  for z in raw[key]['checks']:
   d=z['diagnostic'];text.append(f"| {z['raw']} | {d['initial']['rows']} | {d['agent']['rows']} | {d['gold']['rows']} | {d['agent']['content_hash']['sha256']} | {d['gold']['content_hash']['sha256']} |")
  text += ['',f"逐表内容hash及依赖路径：`records/039_checks/raw_integrity_review.json`；原诊断：`{raw[key]['source']}`（015序列化口径）。这不是仅凭行数不同推断。",'','025三张间接下游的上游在CS中换成标准答案，不能套用本表不可评估结论。']
 else:
  for r in rules[i]:
   typ=r['source'] or '021_reruns';source=str(C/('025_evidence_'+key+'.json')) if typ=='025' else str(C/('supplement_'+key+'.json')) if typ=='039_supplement' else str(R/(typ+'_'+key+'.json'))
   d=load(source);d=d['record'] if typ=='025' else d;run=next(x for x in d['runs'] if x['label']==r['label']);assert not run.get('error');base=d['runs'][0]['comparison'];scales=lambda cp:{z['level']:{k:z[k] for k in ['row_scale','cell_scale']} for z in cp['levels']};baseline=scales(base)
   if 'baseline' in obj:assert obj['baseline']==baseline,(key,r['label'],obj['baseline'],baseline)
   else:obj['baseline']=baseline
   category=({'Unstated Choice':'已说出的选择','Quiet Downgrade':'已说出的降级'}.get(r['category'],r['category']) if r['grade']==1 else r['category'])
   p={**r,'name':r['label'] if r['label']!='whole_implementation_diagnostic' else '同类缺口组：机械fallback投影','category':category,'rerun':r['label'],'rerun_source':source,'scales':scales(run['comparison']),'edits':run.get('edits',[]),'comparison_sql':run.get('sql'),'clock_control':d.get('clock_control',[]),'source_database':d.get('source'),'evidence_present':'是' if r['category']==I else '不适用','understood_before':'否' if r['category']==I else '不适用','quotes':[]}
   p['reduction']=[baseline['L0'][k]-p['scales']['L0'][k] for k in ['row_scale','cell_scale']]
   if r['grade'] in [1,2]:
    quote=r['delivery_quote'];assert quote and quote in finish['text'],(key,r['label'],quote)
    q={'object':key,'point':p['name'],'kind':'delivery','source':finish['path'],'event':fq['id'],'field':'args.final_thought','quote':quote};p['quotes'].append(q);quotes.append(q)
    p['delivery_review']=('报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。' if r['grade']==1 else '报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。')
   else:p['delivery_review']='完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。'
   # Exact original locus from independent patch (or full delivered SQL when output wrapper recovery).
   oldparts=[x['old'] for x in p['edits'] if 'old' in x and x['old'] in sql]
   q={'object':key,'point':p['name'],'kind':'sql','source':o['agent_sql'],'field':'text','quote':oldparts[0].rstrip() if oldparts else sql};p['quotes'].append(q);quotes.append(q)
   obj['points'].append(p)
  best=max(tuple(p['reduction']) for p in obj['points']);assert best>(0,0),(key,best)
  winners=[p for p in obj['points'] if tuple(p['reduction'])==best];cats={p['category'] for p in winners};obj['main']=next(iter(cats)) if len(cats)==1 else '多因并列';obj['confidence']='中' if any(p['confidence']=='中' for p in obj['points']) else '高';obj['combination_only']=False
  for p in obj['points']:
   p['role']=('主要' if len(winners)==1 else '并列') if p in winners else ('参与' if tuple(p['reduction'])>(0,0) else '非原因')
   if p['role']=='非原因':p['marker']='存在未确立的前提，但不是判错原因' if p['category'] not in [O,B] else '单改未产生行优先口径的净改善，不记参与'
  text += [f"主要原因：**{obj['main']}**；把握：{obj['confidence']}；只能组合修复：否。",f"021旧主要原因（含025更正）原样保留：`{old[key]}`。",'', '## 详细发现','','### 范围、基线与排序','','按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。',f"共同基线：`{json.dumps(obj['baseline'],ensure_ascii=False)}`。",'', '| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |','|---|---|---|---:|---:|---:|']
  for p in obj['points']:text.append(f"| {p['name']} | {p['category']} | {p['role']} | {p['reduction'][0]} | {p['reduction'][1]} | {p['grade']} |")
  text+=['','### 契约原句（所有点共用，逐字回查event1）','','```yaml',contract,'```','','### 逐点结论','']
  for p in obj['points']:
   text += [f"#### {p['name']}",'',f"{p['role']}；**{p['category']}**；把握{p['confidence']}。",'',p['reason'],'',f"是否说出：第{p['grade']}档——{levels[p['grade']-1]}。{p['delivery_review']}",f"证据在场：{p['evidence_present']}；曾经理解对过：{p['understood_before']}；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。",'', '| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |','|---|---:|---:|---:|---:|']
   for l,v in p['scales'].items():
    z=obj['baseline'][l];text.append(f"| {l} | {z['row_scale']} | {v['row_scale']} | {z['cell_scale']} | {v['cell_scale']} |")
   text += ['',f"重跑：`{p['rerun_source']}` / `{p['rerun']}`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。",'']
   if p.get('marker'):text += [f"标记：{p['marker']}。",'']
   for q in p['quotes']:
    text += [f"原句 `{q['source']}` / `{q.get('event','SQL')}.{q['field']}`（{q['kind']}）：",'','```text',q['quote'],'```','']
   if not any(q['kind']=='delivery' for q in p['quotes']):text += [f"否定披露的审计范围：finish event {fq['id']} 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。",'']
   ev=[q for q in p['quotes'] if q['kind']=='delivery'] if p['grade']<=2 else [{'quote_ref':{'object':key,'point':'__common_contract__','kind':'process'},'source':o['event_path'],'event':1,'field':'args.content','kind':'process'}]
   audit.append({'对象编号':key,'错误点名称':p['name'],'category':p['category'],'grade':p['grade'],'是否说出':levels[p['grade']-1],'evidence':ev,'reason':p['delivery_review'],'note':p['reason'],'evidence_present':p['evidence_present'],'understood_before':p['understood_before'],'delivery_checked':{'finish':finish['path'],'event':fq['id'],'sql_comments':0},'contract_quote_ref':{'object':key,'point':'__common_contract__','kind':'process'}})
   prows.append({'benchmark':'DAComp','对象编号':key,'错误点名称':p['name'],'角色':p['role'],'类别':p['category'],'是否说出（五档）':levels[p['grade']-1],'证据在场':p['evidence_present'],'曾经理解对过':p['understood_before'],'系统提示是否适用':'不适用','证据是复用还是新做':'039新做单改；复用021核实' if '/039_checks/supplement_' in p['rerun_source'] else '复用021/025重跑及核实；039新核契约和交付原文','证据来源':';'.join([p['rerun_source'],o['package'],'records/039_checks/disclosure_audit.json',str(A/f'039_{key}.md')]),'021旧标签':old[key]})
 text += ['','## 证据来源','',f"- 契约：`{o['contract_source']}`，行{o['contract_lines']}；材料包 `{o['package']}`。",f"- 交付SQL：`{o['agent_sql']}`；SHA-256 `{o['agent_sql_sha256']}`。",f"- 初始完整提示：`{o['event_path']}`；finish：`{finish['path']}` / event {fq['id']}。",'- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。',f"- 复用核实查询含失败共{o['reused_verification_query_count']}条，新核实0条（总数≤5）。诊断/单改不计作核实查询：",'']
 for q in o['verification_queries']:text += [f"  - `{q['source']}` / index {q['index_in_file']}，失败={q['failed']}。"]
 text += ['','## 不确定或没查到的（含规则问题）','']+['- '+s for s in (obj['rules'] or ['未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。'])]
 if i in [18,19,20]:text+=['- 025明确此表在CS下不受raw版本差异影响；本次上游均用gold，原021“不可评估”不再使用。']
 text += ['','## 建议的下一步','','纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。','']
 (A/f'039_{key}.md').write_text('\n'.join(text));working.append(obj)
 orows.append({'benchmark':'DAComp','对象编号':key,'层':o['layer'],'主要原因':obj['main'],'并列项':'；'.join(p['name']+':'+p['category'] for p in obj['points'] if p['role']=='并列'),'是否只能组合修复':'否','把握':obj['confidence'],'旧标签':old[key],'021旧标签':old[key]})
# Serialize unchanged calibration prefix and append formal rows. Repeated render is idempotent.
for kind,rows in [('objects',orows),('points',prows)]:
 path=R/f'039_{kind}.csv'
 with open(path) as f:fields=next(csv.reader(f))
 s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(snapshot[kind]);prefix=s.getvalue().encode();assert hashlib.sha256(prefix).hexdigest()==handoff['calibration_csv_prefix_sha256'][str(path)]
 s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=fields,lineterminator='\n');w.writerows(rows);path.write_bytes(prefix+s.getvalue().encode())
save(C/'formal_working.json',working);save(C/'disclosure_audit.json',audit);save(C/'quote_inventory.json',quotes)
print('formal objects',len(orows),'points',len(prows),'all audit',len(audit),'quotes',len(quotes));print(collections.Counter(o['main'] for o in working))
