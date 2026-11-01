from pathlib import Path
import json,re,hashlib
R=Path('records');C=R/'042_checks';B=Path('data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01')
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def event(t,n):
 p=next((B/t/'agent/.events/sessions').glob(f'*/events/{n}.json'));return p,load(p)
quotes=load(C/'quote_inventory.json')
def q(t,n,field,text,kind):
 p,e=event(t,n);v=e
 for k in field.split('.'):v=v[k]
 assert text in v
 r={'object_id':t,'name':'preparation_fact','path':str(p),'event':n,'field':field,'quote':text,'kind':kind};quotes.append(r);return r
qb=q('impl-015',45,'args.command','# Copy through the source connection rather than ATTACHing the same\n                    # file while it is already open; DuckDB rejects duplicate handles.','raw_change_reason')
qbcode=q('impl-015',45,'args.command','rows = source_conn.execute(f"SELECT * FROM raw.{table_name}").fetchdf()','raw_change_implementation')
raw16=load(R/'013_raw_impl-016.json');tab=next(x for x in raw16['tables'] if x['table']=='person_contact_email_address')
root=B/'impl-016/agent/.events/sessions';hits=[];allpaths=[]
pattern=r'person_contact_email_address|email_address|DELETE\s+FROM|TRUNCATE|DROP\s+TABLE|run\.py'
for p in sorted(root.glob('*/events/*.json'),key=lambda p:int(p.stem)):
 e=load(p);allpaths.append({'path':str(p),'sha256':sha(p)})
 if e.get('action')=='run':
  cmd=e['args']['command'];lines=[{'line':i+1,'text':s} for i,s in enumerate(cmd.splitlines()) if re.search(pattern,s,re.I)]
  if lines:hits.append({'event':e['id'],'path':str(p),'matching_lines':lines})
save(C/'workday_raw_change_search.json',{'scope':'impl-016完整85事件，只读检索args.command；另读013 write_steps和015比较。','regex':pattern,'events':allpaths,'hits':hits,'initial_rows':tab['initial']['row_count'],'agent_rows':tab['agent']['row_count'],'loss':4836,'result':'未找到造成raw.person_contact_email_address减少4836行的具体步骤和原因。run.py执行不等于已定位删除动作；不补全。'})
kl=[]
for name,total,valid in [('campaign',200,2),('flow',79,1),('metric',29,1)]:
 count=f'{name} [({total}, {valid}'+(', 2' if name=='campaign' else '')+')]'
 obs=q('impl-021',20,'content',count,'raw_count_observation')
 initial=f'klaviyo_start.duckdb {name} ({total}, {valid}, {valid})'
 probe=q('impl-021',24,'content',initial,'initial_id_probe_observation')
 final=q('impl-021',41,'args.final_thought','无效关键 ID 和非法邮件记录被排除','delivery_general')
 kl.append({'object_id':'impl-021_stg_klaviyo__'+name,'total_raw':total,'nonnull_id':valid,'null_id':total-valid,'null_id_percent':round(100*(total-valid)/total,4),'evidence':[obs,probe,final],'contract':'对应ID列constraints: [not_null]，agent过滤；gold未执行该ID过滤。','provisional_category':'其他（此ID过滤点）；其他点仍需按列核对。','provisional_disclosure':2,'disclosure_reason':'最终报告该句属于ID过滤通用说明，未点明该表因ID缺失损失的数量；仅列构建行数不等于说明99%丢失。','process_review':'event19/20有计数；event21/22区分ID过滤与邮件正则，event23/24检查初始库、ID大小写；event27/29明确修邮件正则。第二阶段须区分ID稀疏问题的意识与邮件正则的意识，不能仅因计数判第3档。最终已有第2档说明时，不以第3档覆盖。','status':'准备性事实核实；未纳入正式CSV或最终分类计数'})
facts={'source':'records/026_Claude全量标注检查台账.md','items':[{'id':'023-1','task':'impl-016','status':'已确认行数差和未找到步骤；正式表需注明CS上游口径','initial_rows':7284,'agent_rows':2448,'loss':4836,'source':'records/013_raw_impl-016.json','search':'records/042_checks/workday_raw_change_search.json'}, {'id':'026-klaviyo-observation','status':'准备核对已完成，逐表正式点与最终五档待阶段二','tables':kl}],'quickbooks_change':{'task':'impl-015','event':45,'reason_evidence':qb,'implementation_evidence':qbcode,'confirmed':'agent改写run.py绕过重复ATTACH的Unique file handle conflict，经fetchdf/register复制raw。013发现30表类型结构变化、行数未变；015显示gold和initial一致。','inference':'类型变化与此复制路线有关，但未逐列重演类型推断，不声称每列因果已验证。'}}
save(C/'fact_corrections.json',facts);save(C/'quote_inventory.json',quotes)
comp=load(R/'042_calibration_comparison.json')
protected_cal={str(p):sha(p) for p in [R/'042_calibration_blind_sealed.json',R/'042_calibration_comparison.json',C/'calibration_working.json',*sorted((R/'042_annotations').glob('*.md'))]}
for k in ['objects','points']:
 p=R/f'042_{k}.csv';(C/f'phase1_{k}_prefix.csv').write_bytes(p.read_bytes())
save(C/'phase1_handoff.json',{'task':'042','phase':'preparation_and_calibration','formal_completed':0,'formal_pending':39,'calibration_completed':2,'calibration_points':3,'continue_in_same_session':True,'protected_calibration_files':protected_cal,'blind_main_agreement':'1/2；解盲修订后2/2不得算盲标一致','sealed_sha256':sha(R/'042_calibration_blind_sealed.json'),'comparison_sha256':sha(R/'042_calibration_comparison.json'),'phase1_csv_prefix':['records/042_checks/phase1_objects_prefix.csv','records/042_checks/phase1_points_prefix.csv'],'evidence_catalog':'records/042_checks/evidence_catalog.json','pending_work':['按scope正式39张逐表读契约/SQL/重跑/诊断与原始轨迹；旧023类别只存档。','逐点重新按v3.2第3～8节判断，先查明文算法再判Data；占位候选列与无源列区分。','每表直读raw已在catalog映射013；间接依赖与impl-015/016改动在说明里按CS/staging口径写清，不泛化不可评估。','026 Klaviyo三表进一步定稿ID过滤点、五档和过程意识；复核其他错误点与行/格排序。','impl-016 raw email删除步骤仍写未找到；CS上游不把原始减少量直接当当前表错误量。','核实查询每张最多5条，复用也计；只有必要时新做，原数据库只读。','按040格式追加39正式对象与逐点CSV、39份说明；每条引用回查原始文件；验证39+2及hash。','更新同一042报告为完整批次；保护本封存/对比/校准定稿；commit并push main。'],'execution_boundary':'本阶段没有打开数据库，没有执行轨迹命令，没有调用agent/子agent、下载数据或读取041正文。'})
print('facts and handoff saved')
