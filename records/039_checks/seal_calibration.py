import json,hashlib,datetime
from pathlib import Path
R=Path('records'); C=R/'039_checks'
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def event(n,i):
 p=next(Path(f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-{n:03}/agent').glob(f'.events/sessions/*/events/{i}.json'));return p,json.loads(p.read_text())
def q(n,i,field,quote):
 p,d=event(n,i);v=d
 for k in field.split('.'):v=v[k]
 assert quote in v,(n,i,quote)
 return {'source':str(p),'field':field,'event':i,'quote':quote,'kind':'delivery' if field=='args.final_thought' else 'process'}
obj=[]
point={'name':'revenue_score：ntile 替代百分位阈值','category':'Intent Misreading','role':'主要原因','confidence':'高','disclosure':4,'evidence_present':'是','understood_before':'否','reason':'契约明确要求按 80/60/40/20 百分位的值阈值分档；ntile 按行排名分桶，不能等同。不是数据事实待核实。','premise':'ntile(5) 可以实现契约所要求的百分位阈值评分','quotes':[q(13,1,'args.content','revenue_score: 5 for total_revenue at or above the 80th percentile; 4 at or above the 60th; 3 at or above the 40th; 2 at or above the 20th; otherwise 1.'),q(13,19,'args.command','ntile(5) OVER(ORDER BY total_revenue) revenue_score')],'delivery_review':'finish 65 和交付 SQL 无百分位/ntile 具体或通用说明；日期解析和占位高阶指标声明不适用于本处。','rerun':'percentiles'}
obj.append({'id':'impl-013_int_netsuite2__customer_profitability','layer':'intermediate','main':'Intent Misreading','combination_only':False,'confidence':'高','points':[point],'rerun_source':'records/021_reruns_impl-013_int_netsuite2__customer_profitability.json','verification_sources':['records/021_calibration_queries.json#impl-013'],'rules':[]})
pts=[]
pts.append({'name':'account_id 错取 invoice id','category':'Data Misconception','role':'组合修复项','confidence':'高','disclosure':2,'evidence_present':'否','understood_before':'是','reason':'契约没有明确 source_expression；P 被 agent 留存 raw 的外键匹配核实否定。event40 只展示列名，不足以单独证明匹配关系。event34 已出现正确 account_id 映射，45 泛化 pk_alias 后改错。','premise':'invoice 源 id 可充当账户外键 account_id','verification':'021_calibration_queries：2004 行 id=account_id 为0；account_id 匹配账户1999，id 匹配账户0。','quotes':[q(30,71,'args.final_thought','Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。'),q(30,34,'content','try_cast("account_id" AS VARCHAR) AS account_id'),q(30,45,'args.command',"if n in pk_alias: srcname='id'")],'delivery_review':'finish 的源 id 映射声明未限定 invoice 的 account 外键，记通用第2档。','rerun':'account_mapping'})
pts.append({'name':'created_date：排除 NULL/不可解析日期行','category':'Intent Misreading','role':'组合修复项','confidence':'高','disclosure':2,'evidence_present':'是','understood_before':'否','reason':'契约 row_filter 明写 try_cast IS NULL OR 合法区间，agent 加 IS NOT NULL 删除应保留行。','premise':'created_date 不可解析的发票应删行','quotes':[q(30,1,'args.content',"try_cast(created_date as TIMESTAMP) is null OR (try_cast(created_date as TIMESTAMP) <= current_timestamp AND try_cast(created_date as TIMESTAMP) >= timestamp '2000-01-01 00:00:00')"),q(30,71,'args.final_thought','invoice 创建日期按契约限制时间范围。')],'delivery_review':'只说明时间范围过滤，未说 NULL 排除，记第2档。','rerun':'keep_null_dates'})
for col,typ in [('adjustment_amount','DOUBLE'),('amount_without_tax','BIGINT'),('amount_without_tax_home_currency','BIGINT'),('balance','DOUBLE'),('credit_balance_adjustment_amount','DOUBLE'),('credit_memo_amount','DOUBLE'),('exchange_rate','DOUBLE'),('exchange_rate_date','DATE'),('target_date','DATE')]:
 pts.append({'name':col+'：契约类型与 gold 原值不一致','category':'其他','role':'组合修复项','confidence':'高','disclosure':2,'evidence_present':'不适用','understood_before':'不适用','reason':f'契约 data_type={typ}，agent 按规定转换，gold 直接透传源 VARCHAR；不归为 agent 前提错误。金额 BIGINT 的取整和 DATE 去掉时刻也有契约依据。','quotes':[q(30,71,'args.final_thought','严格按 staging 类型输出，在业务比较时对枚举做文本转换。')],'delivery_review':'通用类型声明，非本列的具体解释。','rerun':col})
obj.append({'id':'impl-030_stg_zuora__invoice','layer':'staging','main':'只能组合修复','combination_only':True,'confidence':'高','parallel_categories':['Data Misconception','Intent Misreading','其他'],'points':pts,'rerun_source':'records/021_reruns_impl-030_stg_zuora__invoice.json','verification_sources':['records/021_calibration_queries.json#impl-030','records/017_queries_impl-030.json#V2'],'rules':['L0 行规模：每处单改均为1045，不能因格子减少改称参与因素；组合诊断另存039_checks/calibration_combo.json。']})
for o in obj:
 d=json.loads(Path(o['rerun_source']).read_text());o['baseline']={x['level']:{k:x[k] for k in ['row_scale','cell_scale']} for x in d['runs'][0]['comparison']['levels']}
 for p in o['points']:
  run=next(x for x in d['runs'] if x['label']==p['rerun']);p['scales']={x['level']:{k:x[k] for k in ['row_scale','cell_scale']} for x in run['comparison']['levels']}
 combo=C/'calibration_combo.json'
 if o['combination_only']:o['combination_evidence']=json.loads(combo.read_text())['runs'][-1]['comparison']
sealed={'manual':'docs/标注手册_v3.2.md','sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blind_protocol':'未打开034/036的试点标注内容、018逐表标注或037/038报告；036仅脚本提取对象编号用于排除试点。已用021重跑/查询和013材料包，未用021旧类别。','objects':obj}
p=R/'039_calibration_blind_sealed.json';assert not p.exists();dump(p,sealed);dump(C/'calibration_seal.json',{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sealed_utc':sealed['sealed_utc']});print((C/'calibration_seal.json').read_text())
