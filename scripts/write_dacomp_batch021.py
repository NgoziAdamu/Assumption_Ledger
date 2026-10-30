"""Render reviewed decisions and independently locked calibration, retaining every trial."""
from review_dacomp_batch021 import *
from decisions_dacomp_batch021 import M,RULES
import csv,hashlib,datetime
from collections import Counter,defaultdict
OUT=REC/'021_annotations';OUT.mkdir(exist_ok=True)
T=['针对本表的具体说明','只有通用策略说明','看到了但没提','没有迹象']
INV=json.loads((REC/'021_package_inventory.json').read_text());AUD=json.loads((REC/'021_trace_audit.json').read_text());RAW=json.loads((REC/'021_raw_diagnosis.json').read_text());NE={x['index']:x for x in RAW['tables'] if x['unevaluable']}
Q=[]
for name in ['021_queries.json','021_supplement_queries.json','021_final_diagnostics.json','021_earnings_diagnostic.json','021_runtime_diagnostics.json']:
 if (REC/name).exists():Q +=[{**x,'record':'records/'+name} for x in json.loads((REC/name).read_text())]
META={}
for name in ['021_patch_plan.json','021_supplement_patch_plan.json','021_detailed_patch_plan.json','021_extra_patch_plan.json','021_stakeholder_patch_plan.json']:
 for x in json.loads((REC/name).read_text()):
  for p in x['patches']:META[(x['index'],p['label'])]=p
for key,cat in [((31,'derived_parent_name'),'I'),((36,'type_id_instead_name'),'O'),((33,'overall_health_score'),'D'),((35,'comparative_join_multiplicity'),'C'),((8,'avg_7d_crashes'),'D'),((8,'avg_7d_anrs'),'D')]:META.setdefault(key,{})['category']=cat
for col in ['total_comments_authored','total_projects_involved','engagement_depth_score','total_engagement_score','influence_level']:META[(38,col)]['category']='O'
META[(38,'cross_functional_projects')]['category']='A';META[(38,'engagement_breadth_score')]['category']='C'
# Candidates that are diagnostics, refuted hypotheses, or combine distinct reasons do not enter ranking.
INVALID={2:{'calendar_day_type'},7:{'due_date','start_date'},16:{'required_fields','output_not_null_policy','package_source','missing_required_source_policy','contract_other_default'},34:{'remove_limit'},38:{'response_pattern_type'}}

def load_runs(i):
 r=rows[i];files=[]
 for prefix in ['021_reruns','021_supplement_reruns','021_detailed_reruns','021_extra_reruns','021_fast_reruns']:
  p=REC/f'{prefix}_{r["task"]}_{r["table"]}.json'
  if p.exists():files.append((p,json.loads(p.read_text())))
 assert files,(i,r)
 canonical=files[-1][1]
 if i==4:canonical=next(d for p,d in files if 'supplement' in p.name)
 bylabel={}
 for p,d in files:
  if i==4 and 'supplement' not in p.name:continue
  for run in d['runs']:
   bylabel[run['label']]={**run,'record':str(p.relative_to(ROOT)),'clock_control':d['clock_control'],'baseline':d['runs'][0].get('comparison')}
 return files,canonical,bylabel

def grid(h,rs):
 def e(x):return str(x).replace('|','\\|').replace('\n','<br>')
 return '\n'.join(['| '+' | '.join(h)+' |','|'+'|'.join(['---']*len(h))+'|']+['| '+' | '.join(e(x) for x in row)+' |' for row in rs])+'\n'

def main():
 lock=json.loads((REC/'021_calibration_blind_lock.json').read_text());assert hashlib.sha256((REC/'021_calibration_blind.json').read_bytes()).hexdigest()==lock['sha256']
 blind=json.loads((REC/'021_calibration_blind.json').read_text())['rows']
 fields=next(csv.reader(next((REC/'018_annotations').glob('*.csv')).open()));fields=[x for x in fields if not x.startswith('与上一版相比')]
 decisions=[];summaries=[]
 for i,r in enumerate(rows):
  d=pkg(i);files,canonical,runs=load_runs(i);base=canonical['runs'][0]['comparison']['levels'][0];bpair=(base['row_scale'],base['cell_scale']);rank=[]
  for label,z in runs.items():
   if label=='baseline' or 'comparison' not in z or label in INVALID.get(i,set()) or label in ['whole_implementation_diagnostic','gold_sql_same_clock']:continue
   cat=META.get((i,label),{}).get('category')
   if not cat:continue
   b=z['baseline']['levels'][0];v=z['comparison']['levels'][0];delta=(b['row_scale']-v['row_scale'],b['cell_scale']-v['cell_scale'])
   if delta>(0,0):rank.append({'label':label,'category':cat,'gain':delta,'record':z['record']})
  best=max((x['gain'] for x in rank),default=(0,0));leaders=[x for x in rank if x['gain']==best];participants=[x for x in rank if x['gain']<best]
  q=[x for x in Q if x.get('index')==i and x['kind']=='核实'];qcount=len(q)
  if i in NE:
   cat='不可评估';short='本表存在gold与initial/agent不同的原始依赖，三侧逐表诊断满足不可评估条件。';reason='逐张沿008依赖边回溯，并重新只读核对初始库、agent留存库与gold的结构、行数、内容哈希。以下原始依赖initial=agent且gold不同；不对其SQL差异归U/D/C/A/I/O/X。保留基线仅为机械诊断。';tier=4;uq='检查本题全部75个事件和event73最终报告，没有关于gold使用另一版raw的迹象；agent无法访问gold。不把一般解析说明当成知道评测输入不一致。';conf='高';rule='不可评估按逐表raw依赖判定，包括后续CS层沿来源链的原始依赖；不把整题一概跳过。';factors='不适用';flags='无';leaders=[];participants=[];tiers=[4];um='不适用：不可评估。'
  elif i<40:
   cat,short,reason,tier,uq=M[i];conf='中' if i in [0,2,4,5,16,24,31,34,35,36,38] else '高';rule=RULES.get(i,'无。');flags='已披露' if i in list(range(8,16))+[33,34,35,36,37,38,39] else '无'
   if i==0:flags='无';um='U仅作为参与因素：20个悬空链接的P被查询否定；只改计数键减少20行/132格，不满足独立主因半数门槛，但满足参与因素要求。'
   else:um='不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。'
   if i==16:leaders=[];participants=[]
   factors='；'.join(f"{x['category']}：{x['label']}（减{x['gain'][0]}行/{x['gain'][1]}格）" for x in participants) or '无经单修确认的其他参与因素'
   if i==35:factors+='；保留其他评分/分类占位事实，未逐项单修，不列为参与因素。'
   tiers=[tier]
   if i==38:tiers=[1,4]
  else:
   z=blind[i-40];cat=z['primary']+('（I、O）' if i==41 else '');short=z['reason'];reason=z['reason'];tier=T.index(z['uncertainty'])+1;tiers=[tier];uq=z['evidence'];conf=z['confidence'];flags='无';rule=z['rule_issue'];factors='；'.join(z['factors']) or '无';um='不适用：独立盲标主因不是U。'
   q=[{**x,'record':'records/021_calibration_queries.json','kind':'核实','result':x['rows'],'database':x['source']} for x in json.loads((REC/'021_calibration_queries.json').read_text()) if x['task']==r['task']];qcount=len(q)+(1 if i==40 else 0)
   if i==40:uq+=' 首次核实查询使用保留字rows作别名，解析失败，改为n后成功；失败计入查询条数。'
   if i==41:rule+=' 018对照后发现account_source在018归U，本次盲标归I；保留盲标，不为一致率改写。规模和四档一致。'
  if i==38:
   uncertainty='；'.join(x['label']+'='+T[0 if x['category']=='D' else 3] for x in leaders)
   itemtiers=[dict(label=x['label'],category=x['category'],tier=1 if x['category']=='D' else 4) for x in leaders]
  else:
   uncertainty=T[tier-1];itemtiers=[dict(label=x['label'],category=x['category'],tier=tier) for x in leaders] or [dict(label='主要原因',category=cat,tier=tier)]
  if i==5:uncertainty='；'.join(x['label']+'='+T[tier-1] for x in leaders)
  if i==41:
   itemtiers=[dict(label=k,category='I' if k=='account_mapping' else 'O',tier=tier) for k in ['account_mapping','adjustment_amount','credit_balance_adjustment_amount','credit_memo_amount','exchange_rate']]
   uncertainty='；'.join(x['label']+'='+T[tier-1] for x in itemtiers)
  tied='；'.join(x['label']+'='+x['category'] for x in leaders) if len(leaders)>1 else '不适用'
  if i==41:tied='account_mapping=I；adjustment_amount=O；credit_balance_adjustment_amount=O；credit_memo_amount=O；exchange_rate=O'
  if i==40:tied='不适用'
  cost='需要查业务说明' if i in [2,4,16,36] else '一条查询' if qcount==1 else '多条查询' if qcount>1 else '判断不了'
  scales=[];percols=[];patch=[]
  for label,z in runs.items():
   if 'comparison' not in z:scales.append([label,'执行失败',z.get('error','')]);continue
   c=z['comparison'];scales.append([label,'；'.join(f"{v['level']} {v['row_scale']}行/{v['cell_scale']}格" for v in c['levels']),c['first_match'] or '均未整表匹配'])
   percols.append([label,json.dumps({k:v for k,v in c['levels'][0]['column_mismatches'].items() if v},ensure_ascii=False)])
   for edit in z.get('edits',[]):
    original=(ROOT/z['sql_path']).parent/'baseline.sql';line=original.read_text()[:edit['offset']].count('\n')+1
    if len(edit['old'])+len(edit['new'])>2500:patch.append(f"- {label}：agent SQL第{line}行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`{z['record']}`。" )
    else:patch.append(f"- {label}：agent SQL第{line}行起：\n```sql\n{edit['old']}\n```\n替换为：\n```sql\n{edit['new']}\n```" )
  changes='；'.join(f"{label}:{z['baseline']['levels'][0]['cell_scale']}→{z['comparison']['levels'][0]['cell_scale']}" for label,z in runs.items() if label!='baseline' and 'comparison' in z)
  summary={k:'' for k in fields};summary.update({'题目':r['task'],'表':r['table'],'一句话描述':('【校准】' if i>=40 else '')+short,'主要原因类别':cat,'参与因素':factors,'标记':flags,'把握':conf,'核实查询条数':str(qcount),'核实代价档':cost,'重跑是否满足 U 的第 4 个条件':um,'格子数口径规模变化':changes or '不适用：仅机械基线','与 014 相比是否变化':'不适用：021全量独立标注' if i<40 else '校准：盲标锁定后对照018；详见021_calibration_comparison.json','agent 是否意识到或提到了与本表差异相关的不确定性':uq,'并列项类别':tied,'不确定性四档':uncertainty});summaries.append(summary)
  decision=dict(index=i,task=r['task'],table=r['table'],layer=r['layer'],purpose=r['purpose'],main=cat,confidence=conf,reason=reason,factors=factors,flags=flags,tiers=tiers,main_item_tiers=itemtiers,uncertainty=uncertainty,rule_issue=rule,verification_query_count=qcount,ranking=sorted(rank,key=lambda x:x['gain'],reverse=True));decisions.append(decision)
  text=f"# {r['task']} / {r['table']}（{r['purpose']}）\n\n## 结论\n\n主要原因：**{cat}**；把握：{conf}。{short}\n\n参与因素：{factors}。标记：{flags}。\n\n## 差异与归因依据\n\n{reason}\n\n层：{r['layer']}；实际schema：{d['differences']['actual_schema']}；评测键：{', '.join(d['differences']['key_columns'])}。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。\n\n"
  for b in d['contract_specification']['blocks']:text+=f"- 契约：`{d['contract_specification']['source_path']}:{b['start_line']}–{b['end_line']}`；逐字原文见精简材料包。\n"
  for label,k in [('agent','agent_final_SQL'),('gold（仅定位/诊断）','gold_SQL_仅供定位差异')]:
   for s in d[k]:text+=f"- {label} SQL：`{s['path']}:1–{s['end_line']}`，SHA-256 `{s['sha256']}`。\n"
  text+='\n'+ '\n\n'.join(patch)+'\n\n## agent可见证据与不确定性\n\n**'+uncertainty+'**。\n\n'+uq+'\n\n'
  if tier in [1,2] or i==38:
   markers={'impl-008':['日期文本使用','staging 中对必需键','合同内部对 story'],'impl-009':['本次交付**未完整','Earnings 源数据'],'impl-010':['原始 HubSpot 时间字符串','未对合同要求保留'],'impl-011':['合同非常广泛'],'impl-030':['Fivetran 源表以','合同中少量 staging']}.get(r['task'],[])
   quotes=[s for s in AUD[i]['report_text'].splitlines() if any(k in s for k in markers)]
   text+='最终报告原句（其适用范围按上文判定）：\n\n'+'\n\n'.join('> '+s for s in quotes)+'\n\n'
  if i in [40,41]:text+='事件定位补充：报告写入命令为event'+('63，最终finish为event65' if i==40 else '69，最终finish为event71')+'，二者内容一致；盲标锁定文件保持原样。\n\n'
  text+=f"扫描{AUD[i]['events_scanned']}个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index={i}。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。\n\n"
  text+=grid(['event','cause','显式截断'],[[x['event'],x['cause'],x['explicit_truncation']] for x in AUD[i]['visible']])
  text+='\n## 原始数据一致性与查询\n\n'
  rawtable=next((x for x in RAW['tables'] if x['index']==i),None)
  if rawtable:
   text+=grid(['raw','依赖链','initial=agent','gold=initial'],[[x['raw'],' → '.join(x['path']),x['initial_eq_agent'],x['gold_eq_initial']] for x in rawtable['checks']])
   text+='三侧每表结构、行数、SHA-256及实际只读查询记录在 `records/021_raw_diagnosis.json`，不是按题目推断。\n'
  else:text+='015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。\n'
  text+=f'\n核实查询条数（含失败尝试）：{qcount}；核实代价档：{cost}。每张不超过5条。\n\n'
  for k,x in enumerate(q):
   text+=f"### 核实 {k+1}\n\n数据库：`{x.get('database','见查询JSON')}`；记录：`{x['record']}`。\n\n```sql\n{x['sql']}\n```\n\n"+('失败：'+x['error'] if x.get('error') else '结果（列顺序'+json.dumps(x.get('columns'),ensure_ascii=False)+'）：`'+json.dumps(x.get('result'),ensure_ascii=False,default=str)+'`')+'\n\n'
  if not q:text+='无独立核实查询；本表三侧raw比较为允许读取gold的诊断，不计核实限额。\n'
  diags=[x for x in Q if x.get('index')==i and x['kind']=='诊断']
  for x in diags:text+='诊断来源：`'+x['record']+'`；SQL：\n```sql\n'+x['sql']+'\n```\n结果：`'+json.dumps(x.get('result',x.get('error')),ensure_ascii=False,default=str)+'`。\n\n'
  text+='\n## 固定时间与重跑\n\n原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。\n\n'
  text+=f"留存结果同口径L0：{canonical['retained']['levels'][0]['row_scale']}行/{canonical['retained']['levels'][0]['cell_scale']}格；选定基线：{bpair[0]}行/{bpair[1]}格。\n\n共同固定时间替换：`{json.dumps(canonical['clock_control'],ensure_ascii=False)}`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。\n\n"
  text+=grid(['实验','L0–L3规模（包含键）','整表首次匹配'],scales)+'\n'+um+'\n\n'
  text+=grid(['实验','L0每列非零不一致数'],percols)
  text+='\nL1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。\n\n'
  text+='先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。\n\n'
  if i==16:text+='本表not_null过滤、原字段选择和Other回填相互作用，不能从“过滤后为空”的统计反推出C主因；见规则问题。\n\n'
  if i==35:text+='恢复关联后行规模可能保持不变：原先的gold单侧重复行变成共同键差异行；格子规模才体现改善。完整gold同固定时刻重跑仍因历史运行时刻不同在两个时间派生列残留差异，去除这两列的含重复次数诊断见021_runtime_diagnostics.json。\n\n'
  text+='\n## 规则问题\n\n'+rule+'\n\n## 证据路径与复现\n\n'
  text+='- 精简材料包：`'+INV[i]['path']+'`。\n- 完整机械材料（可由prepare脚本重建）：`'+INV[i]['full_json']+'`。\n'
  for p,x in files:text+='- 重跑：`'+str(p.relative_to(ROOT))+'`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。\n'
  text+='- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。\n- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。\n- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。\n'
  (OUT/(r['stem']+'.md')).write_text(text)
 with (OUT/'021_summary.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(summaries)
 (REC/'021_decisions.json').write_text(json.dumps(decisions,ensure_ascii=False,indent=2)+'\n')
 def stat(ds):
  return {'total':len(ds),'categories':dict(Counter(x['main'] for x in ds)),'uncertainty_table_combinations':dict(Counter('；'.join(T[t-1] for t in sorted(set(x['tiers']))) for x in ds)),'uncertainty_table_coverage':{T[t-1]:sum(t in x['tiers'] for x in ds) for t in range(1,5)},'uncertainty_main_items':dict(Counter(T[z['tier']-1] for x in ds for z in x['main_item_tiers']))}
 stats={'formal':stat(decisions[:40]),'evaluatable':stat([x for x in decisions[:40] if x['main']!='不可评估']),'calibration':stat(decisions[40:]),'by_layer':{l:stat([x for x in decisions[:40] if x['layer']==l]) for l in sorted(set(x['layer'] for x in decisions[:40]))}}
 (REC/'021_statistics.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n');print(json.dumps(stats['formal'],ensure_ascii=False,indent=2))
if __name__=='__main__':main()
