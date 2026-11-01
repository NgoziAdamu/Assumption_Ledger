"""Unblind after the immutable seal; amendments apply only to working copy."""
from pathlib import Path
import json,csv,copy,hashlib,datetime
R=Path('records');C=R/'039_checks'
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def quote(n,i,field,text):
 p=next(Path(f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-{n:03}/agent').glob(f'.events/sessions/*/events/{i}.json'));v=load(p)
 for k in field.split('.'):v=v[k]
 assert text in v
 return {'source':str(p),'event':i,'field':field,'quote':text,'kind':'process'}
seal=load(C/'calibration_seal.json');assert hashlib.sha256(Path(seal['path']).read_bytes()).hexdigest()==seal['sha256']
blind=load(R/'039_calibration_blind_sealed.json')['objects'];working=copy.deepcopy(blind)
oldobj={x['对象编号']:x for x in csv.DictReader(open(R/'036_objects.csv'))};oldpts={(x['对象编号'],x['错误点名称']):x for x in csv.DictReader(open(R/'036_points.csv'))}
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
pointmap={'percentiles':'percentile_score','account_mapping':'account_source','keep_null_dates':'created_date_nullable'}
rows=[]
for o in blind:
 for p in o['points']:
  name=pointmap.get(p['rerun'],p['rerun']+'_representation');ref=oldpts[o['id'],name]
  role='主要' if p['role']=='主要原因' else p['role']
  rows.append({'object':o['id'],'blind_point':p['name'],'reference_point':name,'blind':{'category':p['category'],'role':role,'disclosure':levels[p['disclosure']-1],'evidence_present':p['evidence_present'],'understood_before':p['understood_before']},'036':ref,'category_equal':p['category']==ref['类别'],'role_equal':role==ref['角色'],'disclosure_equal':levels[p['disclosure']-1]==ref['是否说出（五档）'],'understood_equal':p['understood_before']==ref['曾经理解对过']})
for o in working:
 for p in o['points']:
  p['name']=pointmap.get(p['rerun'],p['rerun']+'_representation')
  p['role']='主要' if p['role']=='主要原因' else p['role']
 if o['id'].startswith('impl-030'):
  o['main']='多因并列';o['combination_only']=False;o['parallel_categories']=['Data Misconception','其他']
  for p in o['points']:
   p['reduction']=[o['baseline']['L0'][k]-p['scales']['L0'][k] for k in ['row_scale','cell_scale']]
   p['role']='并列' if p['reduction']==[0,1040] else '参与'
  o['rules']=['沿用038按(L0行减少,L0格减少)排序：行并列时用格子数；盲标曾严格按行数判只能组合修复。该读法差异单列规则问题，封存件不改。组合诊断全表对齐只说明差异覆盖，不参与单改排序。']
  p=o['points'][0]
  p['quotes']=[q for q in p['quotes'] if q['event']!=34]
  p['quotes'].append(quote(30,19,'args.command',"else:\n            srcname=n\n            e=f'try_cast(\"{srcname}\" AS {typ})'"))
  p['reason']='契约没有account_id source_expression；P被留存raw的外键匹配核实否定。event40只展示列名，不足以单独证明对应关系。曾经理解对过保留“是”：event19的默认同名分支实际生成正确account_id表达式，event45有意泛化pk_alias后改错。盲标event34引句来自account/invoice_payment，不能证明invoice；此处改用event19生成器及invoice契约。代码曾正确不代表最终全局映射只是无意编码失误。'
  p['quotes'].append(quote(30,40,'content',"zuora_invoice_data ['id', '_fivetran_deleted', '_fivetran_synced', 'account_id'"))
 else:
  p=o['points'][0];p['reduction']=[2,4]
  src='records/016_reruns_impl-013.json';d=load(src);run=next(r for r in d['runs'] if r['label']=='clv_month_denominator')
  clv={'name':'clv_denominator','category':'Unstated Choice','role':'非原因','confidence':'中','disclosure':4,'evidence_present':'不适用','understood_before':'不适用','reason':'契约说net_profit per month，未指明用active_months还是customer_lifetime_months作分母；差异取决于未定的选择。单改结果仍2行4格，不是本表判错原因。','premise':'月均利润按有交易的活跃月数计算','quotes':[quote(13,1,'args.content','predicted_clv: if customer_lifetime_months and active_months are both greater than 0, multiply net_profit per month by the larger of 12 months and 1.2 times customer_lifetime_months; otherwise use net_profit.'),quote(13,19,'args.command','net_profit/nullif(active_months,0)*greatest(12,1.2*coalesce(customer_lifetime_months,1)) predicted_clv')],'delivery_review':'finish65未说明本处；初始event1完整提供相关业务说明，故第4档；没有比较两种分母或点出歧义，不能第3档。036第5档与本次原文回查结果不同。','rerun':'clv_month_denominator','rerun_source':src,'scales':{x['level']:{k:x[k] for k in ['row_scale','cell_scale']} for x in run['comparison']['levels']},'reduction':[0,0],'marker':'存在未确立的前提，但不是判错原因','added_after_unblinding':True}
  o['points'].append(clv);o['rules']=['盲标漏掉既有CLV分母非原因候选，解盲后补录。盲标一致率不包含补录结果。']
# Add exact per-column contract and delivered SQL citations for review.
for o in working:
 n=int(o['id'][5:8]);table=o['id'][9:];package=next((R/'013_packages').glob(f'013_impl-{n:03}_*_{table}.md'));s=package.read_text()
 import re
 sources=dict(re.findall(r'- (S\d+): `([^`]+)`',s));contract=re.search(r'```yaml\n([\s\S]*?)\n```',s).group(1);sql=Path(sources['S4']).read_text()
 o['package']=str(package);o['contract_source']=sources['S3'];o['agent_sql']=sources['S4'];o['verification_query_count']=2
 for p in o['points']:
  src=p.get('rerun_source',o['rerun_source']);d=load(src);run=next(r for r in d['runs'] if r['label']==p['rerun']);p['edits']=run['edits']
  for e in run['edits']:
   old=e['old']
   for ce in d['clock_control']:old=old.replace(ce['replacement'],'current_timestamp' if 'timestamp' in ce['pattern'] else 'current_date')
   if old in sql:p['quotes'].append({'source':sources['S4'],'field':'text','quote':old,'kind':'delivered_code'})
  if p['category']=='其他':
   col=p['rerun'];typ=re.search(r'- name: '+col+r'\n\s+data_type: (\w+)',contract).group(1);line=re.search(r'- name: '+col+r'\n\s+data_type: '+typ,contract).group(0)
   p['quotes'].append(quote(n,1,'args.content',line))
comparison={'sealed_sha256':seal['sha256'],'unblinded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reference':['records/036_objects.csv','records/036_points.csv'],'main_comparison':[{'object':o['id'],'blind':o['main'],'036':oldobj[o['id']]['主要原因'],'equal':o['main']==oldobj[o['id']]['主要原因']} for o in blind],'points':rows,'missing_in_blind':[oldpts[blind[0]['id'],'clv_denominator']],'metrics':{'main_agreement':'1/2','point_coverage':'12/13','matched_point_category_agreement':'12/12','matched_point_role_agreement':'1/12','matched_point_disclosure_agreement':'12/12','matched_exploration_understood_agreement':'2/3'},'working_amendments':['invoice按038的行优先、格子次之排序，改为Data与其他并列，其他六点为参与；不修改封存件。','补录CLV分母非原因候选；依据event1相关原文，第4档，与036第5档不同。','account_source曾经理解对过仍为是，与036否不同；撤回不属于invoice的event34引句，改引event19默认同名生成器；保持Data，因event45是主动统一id映射而非偶然覆盖。','两表把握仍高，036为中；报告并列差异，不为了对齐而改。'],'ranking_rule_issue':'手册第7节文字“比不出时按格子”与“规模完全没变不算参与”存在严格行数读法；本次工作结果依用户要求与038相同，采用行数并列时按格子排序。供用户与Claude复核，不改手册。'}
save(R/'039_calibration_comparison.json',comparison);save(C/'calibration_working.json',working)
print(comparison['metrics'])
