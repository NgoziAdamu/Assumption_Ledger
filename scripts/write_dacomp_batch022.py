from review_dacomp_batch022 import *
import csv,collections,hashlib,datetime,platform
OUT=REC/'022_annotations';OUT.mkdir(exist_ok=True)
fields=next(csv.reader((REC/'018_annotations/018_summary.csv').open()));fields=[f for f in fields if f!='与上一版相比是否变化及原因']
old={(r['题目'],r['表']):r for r in csv.DictReader((REC/'018_annotations/018_summary.csv').open())}
queries=json.loads((REC/'022_queries.json').read_text())+json.loads((REC/'022_queries_retry.json').read_text());decisions=json.loads((REC/'022_decisions.json').read_text());audit=json.loads((REC/'022_trace_audit.json').read_text());diagnostics={x['index']:x for x in json.loads((REC/'022_diagnostics.json').read_text())}
blind=json.loads((REC/'022_calibration_blind_decisions.json').read_text());comparison=[]
for i,r in enumerate(inventory()[38:],38):
 x=blind['decisions'][i-38];d=dict(index=i,**r,main=x['main'],confidence=x['confidence'],uncertainty=x['uncertainty'],quote=x.get('quote',''),events=x['events'],verification_count=x['verification_count'],flags=['校准'],factors=[],selected=['campaign_column'] if i==38 else ['account_duplicates'],metric='行',scores=[],reason=x['reason'],rule_issue=x['rule_issue'])
 if i==38:
  d['reason']='campaign来源选择未被契约和可见关联数据唯一确定，主要原因A；单换源列L2完全一致。盲标把三项数值类型合改当作O参与因素；盲锁后按手册逐项拆开，三项单修行规模均不减，因此最终不列参与因素。保留盲锁原结论，不倒改。'
  d['rule_issue']='三列类型可读为一种统一类型策略或三个独立错误点；按更严格逐列单改执行。合改减15行不能冒充任一单项贡献，最终剔除盲标的O参与因素。'
 d['calibration_status']='先盲标锁定，再读取018；最终修订及原因均显式保留。'
 decisions.append(d)
 o=old[(r['task'],r['table'])];comparison.append({'task':r['task'],'table':r['table'],'018_main':o['主要原因类别'],'022_blind_main':x['main'],'022_final_main':d['main'],'main_consistent':o['主要原因类别']==d['main'],'018_uncertainty':o['不确定性四档'],'022_uncertainty':d['uncertainty'],'uncertainty_consistent':o['不确定性四档'].split('=')[-1]==d['uncertainty'],'018_factors':o['参与因素'],'022_blind_factors':x['factors'],'022_final_factors':[],'blind_factor_difference':i==38,'resolution':d.get('rule_issue'),'018_confidence':o['把握'],'022_confidence':d['confidence']})
(REC/'022_calibration_comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n')

def j(x):return json.dumps(x,ensure_ascii=False,default=str)
def grid(headers,rows):
 def cell(x):return str(x).replace('|','&#124;').replace('\n','<br>')
 return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(cell(v) for v in r)+' |' for r in rows])+'\n'
def scales(c):
 return grid(['L档','agent/gold行','独有A/G','共同键多出A/G','共同键不同配对行','行规模','格子规模','整表匹配'],[[x['level'],f"{x['agent_rows']}/{x['gold_rows']}",f"{x['agent_only_key_rows']}/{x['gold_only_key_rows']}",f"{x['common_key_agent_excess_rows']}/{x['common_key_gold_excess_rows']}",x['common_key_different_rows_or_min_pairs'],x['row_scale'],x['cell_scale'],x['whole_match']] for x in c['levels']])+f"\n整表首次匹配：{c['first_match'] or 'L0–L3均不匹配'}。\n"
def cols(c):
 names=list(c['levels'][0]['column_mismatches']);return grid(['共同键比较列','L0不同格','L1','L2','L3'],[[name]+[x['column_mismatches'][name] for x in c['levels']] for name in names])
rows=[]
for d in decisions:
 i=d['index'];p=pkg(i);b=p['differences'];fn='022_'+d['task']+'_'+d['table'];ev=REC/(fn.replace('022_','022_reruns_',1)+'.json');e=json.loads(ev.read_text());runs=e['runs']
 if i==38:
  sup=json.loads((REC/'022_calibration_supplement_reruns_impl-005_stg_google_ads__ad_group_stats.json').read_text());runs=[x for x in runs if x['label']!='numeric_types']+sup['runs'][1:]
 mainitems=[x for x in d['scores'] if x['label'] in d['selected']];factors='；'.join(x['category']+'：'+x['label'] for x in d['factors']) or '无';ties='；'.join(x['label']+'='+x['category'] for x in mainitems) if len(mainitems)>1 else ''
 count=d['verification_count'];cost='一条查询' if count==1 else '多条查询';base=runs[0]['comparison']['levels'][0]
 ur=[]
 for x in runs[1:]:
  c=x['comparison'];a=c['levels'][0];met=c['first_match'] in ['L0','L1','L2'] or a[d['metric']=='行' and 'row_scale' or 'cell_scale']<=base[d['metric']=='行' and 'row_scale' or 'cell_scale']/2
  if met:ur.append(x['label'])
 utext=('数值门槛达到：'+','.join(ur)+'；非U，未据此改类') if ur else '未达到/不适用；本表没有U归因'
 if i in [0,2]:utext='不适用：契约允许顺序的O诊断'
 changes='；'.join(x['label']+f"：{base['cell_scale']}→{x['comparison']['levels'][0]['cell_scale']}" for x in runs[1:]) or '无局部SQL改动；规范化诊断见逐表记录'
 marker='；'.join(d['flags']) or '无'
 uncertainty_detail=d['uncertainty']+'；事件'+(','.join(map(str,d['events'])) or '无相关证据')
 if d['main']=='多因并列':uncertainty_detail='；'.join(x['label']+'：'+d['uncertainty'] for x in mainitems)
 row=dict(zip(fields,[d['task'],d['table'],d['reason'],d['main'],factors,marker,d['confidence'],count,cost,utext,changes,'不适用：任务022全量/独立校准，不改014记录',uncertainty_detail,ties,d['uncertainty']]))
 rows.append(row)
 text=f"# {d['task']} / {d['table']}（{d['purpose']}；v2）\n\n## 1. 差异与结论\n\n{d['reason']}\n\n主要原因：**{d['main']}**；参与因素：{factors}；把握：{d['confidence']}；标记：{marker}。\n\n依据L0先行后格，本表用于选择主因及参与因素的尺度：**{d['metric']}**。"+'\n\n'
 if mainitems:text+=grid(['主项/并列项','类别','单修行减少','单修格减少'],[[x['label'],x['category'],x['row_reduction'],x['cell_reduction']] for x in mainitems])+'\n'
 if i>=38:text+='校准过程：盲标固定文件 `records/022_calibration_blind_decisions.json`，哈希锁 `records/022_blind_lock.json`；之后才读018。对照见 `records/022_calibration_comparison.json`。\n\n'
 text+='## 2. 来源、契约及SQL位置\n\n'
 text+=f"- 精简材料包：[{d['path']}](../../{d['path']})，只摘原文与机械统计。\n- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`{d['full_json']}`。\n- 比较结果：[{ev.name}](../{ev.name})。\n- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。\n- 手册：`docs/标注手册_v2.md`，未改。\n\n"
 contract=p['contract_specification'];text+=f"契约原件：`{contract['source_path']}`。\n\n"
 for block in contract['blocks']:text+=f"原件第{block['start_line']}–{block['end_line']}行；完整原文见材料包。\n\n"
 if not contract['blocks']:text+='未在完整data_contract中检出本表定义；已搜索依赖配置与utils SQL，配置仅指示依赖。\n\n'
 for k,title in [('agent_final_SQL','agent SQL'),('gold_SQL_仅供定位差异','gold SQL（诊断）')]:
  for source in p[k]:
   text+=f"### {title}\n\n`{source['path']}`；原件第1–{len(source['text'].splitlines())}行。\n\n```sql\n"+'\n'.join(f'{n+1:4}: {l}' for n,l in enumerate(source['text'].splitlines()))+'\n```\n\n'
 text+='## 3. agent看到的材料与不确定性\n\n'
 if i<38:
  a=audit[i];text+=f"已检视该题全部{a['all_events_reviewed']}个原始归档事件（原输出显式截断事件：{a['truncated_observation_events']}），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。\n\n"
  for x in a['events']:text+=f"- event {x['id']} / {x['kind']}：`{x['path']}`。\n"
 else:
  root=ROOT/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{d["task"]}/agent'
  for n in d['events']:
   pp=next(root.glob(f'.events/sessions/*/events/{n}.json'));text+=f'- event {n}：`{pp.relative_to(ROOT)}`。\n'
 text+=f"\n四档：**{d['uncertainty']}**。\n\n"
 if d['main']=='多因并列':text+=grid(['并列项','四档'],[[x['label'],d['uncertainty']] for x in mainitems])+'\n'
 if d['quote']:text+='原句（见上述最终报告事件）：\n\n```text\n'+d['quote']+'\n```\n\n'
 else:text+='未找到针对本表主项选择的说明。“看到了但没提”只表示上述实际输出包含相关schema、样例、代码/运行结果；不把写SQL本身或通用功能清单当作具体说明。“没有迹象”不推断agent内部没有意识到。\n\n'
 if i in [21,22,24]:text+='I的明确意图证据：event15原始生成器包含本表源列字典；event24显示旧源名不存在的报错；event25仅将FROM改为实际源表，未重建SELECT投影。不是仅凭事后gold反推意图。\n\n'
 if i==9:text+='参与因素D的披露见event65：业务规则精确逐条合规率未完整验证；这是参与因素的披露，主项A的四档仍按名称选择填写。\n\n'
 text+='## 4. 核实查询与诊断\n\n'+f"核实查询共**{count}条**（含失败尝试），代价档：**{cost}**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。\n\n"
 qs=[x for x in queries if x['index']==i] if i<38 else [x for x in json.loads((REC/'022_calibration_queries.json').read_text()) if x['task']==d['task']]
 for n,x in enumerate(qs,1):text+=f"### 核实 V{n}：{x['label']}\n\n数据库：`{x['database']}`。\n\n```sql\n{x['sql']}\n```\n\n```json\n{j({k:v for k,v in x.items() if k in ['columns','result','rows','error']})}\n```\n\n"
 if i in diagnostics:
  diag=diagnostics[i];text+='### 诊断（允许gold，不计5条）\n\n`records/022_diagnostics.json` 本表条目：\n\n```json\n'+j(diag)+'\n```\n\n'
 text+='## 5. 单改重跑与L0–L3\n\n'
 text+=f"输入口径：{e['source']}。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`{j(e['clock_control'])}`。所有基线与单改使用相同控制；原件只读ATTACH。\n\n"
 text+=f"键：`{j(b['key_columns'])}`；比较列：`{j(b['comparison_columns'])}`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。\n\n"
 text+='### 原留存输出\n\n'+scales(e['retained'])+'\n'+cols(e['retained'])+'\n'
 for x in runs:
  text+=f"### {x['label']}\n\nSQL：`{x['sql_path']}`；SHA-256：`{x['sql_sha256']}`。\n\n"
  for edit in x['edits']:
   line=p['agent_final_SQL'][0]['text'][:p['agent_final_SQL'][0]['text'].find(edit['old'])].count('\n')+1
   text+=f"替换offset={edit['offset']}，原表达式所在行约{line}（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。\n\n```sql\n-- 旧\n{edit['old']}\n-- 新\n{edit['new']}\n```\n\n"
  text+=scales(x['comparison'])+'\n'+cols(x['comparison'])+'\n'
 text+='### 类别门槛与未计入因素\n\n'+utext+'。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。\n\n'
 for x in d['scores']:
  role='主项' if x['label'] in d['selected'] else '参与因素' if any(z['label']==x['label'] for z in d['factors']) else '单修未满足本表所选尺度的参与门槛'
  text+=f"- {x['label']}：{x['category']}；{role}。{x['reason']}（行减少{x['row_reduction']}，格减少{x['cell_reduction']}）\n"
 if i==38:text+='- 盲标中numeric_types同时改三列的结果保留在原盲锁JSON，仅作组合诊断；逐列单改spend/conversions/conversion_value的行规模均19985，不列O参与因素。\n'
 text+='\n## 规则问题\n\n'+d['rule_issue']+'\n'
 (OUT/(fn+'.md')).write_text(text)
with (OUT/'022_summary.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
full=decisions[:38];stats={'full_count':38,'calibration_count':2,'categories':dict(collections.Counter(d['main'] for d in full)),'uncertainty':dict(collections.Counter(d['uncertainty'] for d in full)),'by_layer':{},'by_task':{},'calibration':comparison,'note':'四档按表计38；两张多因并列的每项也在Markdown单列，项级统计共40。'}
for key in ['layer','task']:
 for value in sorted(set(d[key] for d in full)):
  subset=[d for d in full if d[key]==value];stats['by_'+key][value]={'count':len(subset),'categories':dict(collections.Counter(d['main'] for d in subset)),'uncertainty':dict(collections.Counter(d['uncertainty'] for d in subset))}
(REC/'022_statistics.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
print(j(stats))
