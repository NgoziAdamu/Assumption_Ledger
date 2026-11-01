from pathlib import Path
import json,hashlib,datetime
R=Path('records'); base=Path('data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01')
def ev(t,n):
 p=next((base/t/'agent/.events/sessions').glob(f'*/events/{n}.json'));return p,json.loads(p.read_text())
def quote(t,n,field,s):
 p,d=ev(t,n);v=d
 for k in field.split('.'):v=v[k]
 assert s in v
 return {'path':str(p),'event':n,'field':field,'quote':s}
def metrics(f,label):
 d=json.loads((R/f).read_text());return next(x['comparison']['levels'] for x in d['runs'] if x['label']==label)
def point(name,cat,role,tier,why,q,f,label):
 return {'name':name,'category':cat,'role':role,'confidence':'高','disclosure':tier,'disclosure_reason':why,'quotes':q,'evidence_present':'不适用','previously_correct':'不适用','system_prompt':'不适用','rerun_source':str(R/f),'rerun_label':label,'baseline':metrics(f,'baseline'),'single_change':metrics(f,label)}
a='impl-005_stg_google_ads__ad_group_stats';b='impl-027_int_xero__invoice_line_items_enriched'
q=quote('impl-005',14,'content',"('campaign_base_campaign', 'VARCHAR', 'YES', None, None, None), ('campaign_id', 'VARCHAR', 'YES', None, None, None)")
p=point('campaign_id源列选择','Unstated Choice','主要原因',4,'交付报告和交付SQL未针对campaign映射说明；event 14看到两列，event 15直接选用base列，未见比较或疑问。',[q],f'022_reruns_{a}.json','campaign_column')
p['reason']='契约仅规定campaign_id的类型和非空，未指定源列。014 V1两列9985/10000不同；016 V1两列均10000/10000匹配campaign history，V2匹配ad-group父键分别11/10000、14/10000，不能定下唯一映射；差异取决于材料没定的选择。不能据gold选列判Data Misconception。'
p['verification_sources']=['records/014_queries_impl-005.json#V1','records/016_queries_impl-005.json#V1','records/016_queries_impl-005.json#V2']
ps=[p]
for name,label,typ in [('spend两位小数','spend','DECIMAL(15,2)'),('conversions类型表示','conversions','DECIMAL(10,2)'),('conversions_value类型表示','conversion_value','DECIMAL(15,2)')]:
 col=name.split('两位')[0].split('类型')[0]
 snippet=f'- name: {col}\n          data_type: {typ}'
 q2=quote('impl-005',1,'message',snippet)
 p=point(name,'其他','参与因素',4,'交付报告未针对本处精度说明；event 1直接提供类型规定，执行代码遵从该规定；不把写出CAST本身视为意识到差异。',[q2],f'022_calibration_supplement_reruns_{a}.json',label)
 p['reason']=f'契约明确要求{typ}，agent遵从；gold采用DOUBLE。spend有舍入数值差异，另两列主要为类型文本表示差异。均属于gold与契约类型不一致，不归Form Mismatch。单改行数不降但格子数减少，计参与因素。'
 ps.append(p)
text='Duplicate account codes exist in source; the invoice enrichment chooses one account deterministically by lowest `account_id` to prevent duplicate output line rows. This can discard alternate account attributes for colliding codes.'
p=point('account_code去重满足line_item_id唯一性','其他','主要原因',1,'finish明确点名invoice enrichment并说明按最低account_id去重及舍弃其他属性的影响。',[quote('impl-027',41,'args.final_thought',text)],f'022_reruns_{b}.json','account_duplicates')
p['reason']='契约明确One row per line_item_id及unique；agent输出5000行满足唯一性，gold5209行多209行。去掉account_by_code的QUALIFY后与gold在L0–L3完全一致，证明差异来源；按第6节属于标准答案与唯一性规格不一致。'
p['contract_quote']='Unique identifier for the invoice line item; exactly one output row per value'
p['verification_sources']=['records/017_queries_impl-027.json#V2']
d={'sealed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manual':'docs/标注手册_v3.2.md','blind_protocol':'封存前未读取034/036这两表内容、018逐表标注及037–039报告；仅提取036中impl-012–014的对象键用于范围排除。保护性hash仅读取字节而不解码展示。','objects':[{'id':a,'layer':'staging','main':'Unstated Choice','confidence':'高','combination_only':False,'points':ps,'verification_query_count':3},{'id':b,'layer':'intermediate','main':'其他','confidence':'高','combination_only':False,'points':[p],'verification_query_count':1}],'rule_questions':[]}
f=R/'040_calibration_blind_sealed.json'
assert not f.exists();f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
h=hashlib.sha256(f.read_bytes()).hexdigest()
(R/'040_checks/calibration_seal.json').write_text(json.dumps({'path':str(f),'sha256':h,'sealed_at_utc':d['sealed_at_utc']},ensure_ascii=False,indent=2)+'\n')
print(h)
