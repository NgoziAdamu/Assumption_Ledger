"""038 盲标封存：只读允许的契约、轨迹、SQL、014/020 数值证据；禁止覆盖封存件。"""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[2]
def write(p,v): (R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def event(task,n):
 p=next((R/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent/.events').glob(f'sessions/*/events/{n}.json'))
 return str(p.relative_to(R)),json.loads(p.read_text())
def quote(task,n,field,text):
 path,e=event(task,n);v=e
 for k in field.split('.'):v=v[k]
 assert text in v,(task,n,text)
 return dict(path=path,event=n,field=field,quote=text)
def point(name,cat,role,reason,qs,run,P='',presence='不适用',presence_reason='不适用'):
 return {'错误点名称':name,'类别':cat,'角色':role,'把握':'高','P':P,'判据':reason,'是否说出（五档）':'看到了相关信息，但没有意识到的迹象','disclosure_grade':4,'disclosure_evidence':qs,'disclosure_reason':'初始契约/列清单有相关信息，交付物未针对本处说明；代码仅实施所选做法，未发现比较候选、指出冲突或疑问的迹象。一般合规/完成陈述不当作披露。','证据在场':presence,'evidence_presence_explanation':presence_reason,'evidence_presence_quotes':qs if presence=='是' else [],'曾经理解对过':'否' if cat in ['Data Misconception','Intent Misreading'] else '不适用','系统提示是否适用':'不适用','run_label':run,'evidence':['records/020_reruns_'+('impl-002_stg_pendo__guide_event' if run in ['latitude','url','key'] else 'impl-025_stg_twilio__call')+'.json#'+run],'rule_issue':''}
a='impl-002';b='impl-025'
lat=quote(a,1,'args.content','- name: latitude\n          data_type: DOUBLE')
url=quote(a,1,'args.content','- rule: "url IS NULL OR url ~ \'^https?://\'"\n              on_failure: nullify_field')
key=quote(a,1,'args.content','description: "Generated surrogate key"')
phone=[]
for col in ['user_phone_number','contact_phone_number']:
 path,e=event(b,1);txt=e['args']['content'];start=txt.index('- name: '+col);end=txt.index('on_failure: nullify_field',start)+len('on_failure: nullify_field');phone.append(quote(b,1,'args.content',txt[start:end]))
objs=[{'对象编号':a+'_stg_pendo__guide_event','层':'staging','主要原因':'多因并列','并列项':'Intent Misreading；Unstated Choice','是否只能组合修复':'否','把握':'高','points':[
 point('latitude 未处理超出正负90度的值','Data Misconception','参与','契约没有规定 latitude 过滤算法；地理纬度硬约束可定，020 agent 留存 raw 核实查询 15000 行中 13655 行超界。P 被数据否定，依第5节硬约束归 Data。',[lat],'latitude','raw.guide_event.latitude 可以直接作为合法纬度使用，非空值均在 [-90,90]。','否','event 1 仅给 latitude 列名及 DOUBLE 类型；event 14/16 仅 schema，无超界统计/样例，不能单凭它们证明本批 raw 值超界。核实查询是标注者事后复用，非 agent 当时看到的输出。'),
 point('url 未执行契约正则置空规则','Intent Misreading','并列','契约明确给出 url ~ 表达式和 nullify_field；按引擎字面语义执行，agent 只 TRIM/NULLIF，遗漏规定做法。不是依据 gold 发明验证算法，也不是仅呈现差异。',[url],'url',presence='是',presence_reason='初始任务 event 1 args.content 完整包含本表的上述规则，未截断。'),
 point('guide_event_key 拼接列与分隔符','Unstated Choice','并列','契约仅写 Generated surrogate key，没定输入列、拼接顺序或分隔符；差异取决于材料没定的选择。键值为计算结果，非 Form Mismatch。',[key],'key')
]}, {'对象编号':b+'_stg_twilio__call','层':'staging','主要原因':'Intent Misreading','并列项':'','是否只能组合修复':'否','把握':'高','points':[
 point('user_phone_number 先修复再校验','Intent Misreading','参与','契约规定非法电话 nullify_field，未授权先去标点、补 +1 把不合法源值修复为合法。020 核实查询 2500 源行零条 from 符合要求；单改只撤掉该列修复。',[phone[0]],'phone_user',presence='是',presence_reason='event 1 初始任务完整给出本列正则和 nullify_field。'),
 point('contact_phone_number 先修复再校验','Intent Misreading','主要','同一契约规则对 contact_phone_number 独立适用；020 核实查询零条 to 符合要求。两列可独立修改，不合成一个点。',[phone[1]],'phone_contact',presence='是',presence_reason='event 1 初始任务完整给出本列正则和 nullify_field。')
]}]
for o in objs:
 id=o['对象编号'];task=id[:8];r=json.loads((R/f'records/020_reruns_{id}.json').read_text());runs={x['label']:x for x in r['runs']};base=runs['baseline']['comparison']['levels']
 o['ranking_basis']='先整表行规模；行规模相同不能区分时比较格子规模。L0–L3 同结论。保留所有原始数值，不以旧类别定新类别。'
 o['baseline']=[{k:l[k] for k in ['level','agent_rows','gold_rows','row_scale','cell_scale']} for l in base]
 for p in o['points']:
  p['rerun']=[{k:l[k] for k in ['level','agent_rows','gold_rows','row_scale','cell_scale']} for l in runs[p['run_label']]['comparison']['levels']]
  p['reduction']=[base[0]['row_scale']-p['rerun'][0]['row_scale'],base[0]['cell_scale']-p['rerun'][0]['cell_scale']]
  p['evidence'].append('records/020_calibration_queries.json')
 finish=59 if task==a else 41;path,e=event(task,finish)
 sql=next((R/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent').glob('dacomp-de-impl-*/sql/staging/'+id[9:]+'.sql'));t=sql.read_text();assert '--' not in t and '/*' not in t
 o['delivery_review']={'finish_event':finish,'path':path,'field':'args.final_thought','final_report':e['args']['final_thought'],'sql_path':str(sql.relative_to(R)),'sql_sha256':hashlib.sha256(sql.read_bytes()).hexdigest(),'sql_has_comments':False,'finding':'已逐字读最终报告和本表 SQL。Pendo caveat 点名复杂下游表，未点名 guide_event；普通 staging 工作清单不表示承认本处选择。Twilio 报告点名 outgoing_caller_id，不能推广至 call；一般合规说明未交代先修复电话。两表各点记第4档。'}
 o['exclusions']='未见代码自身表明正确意图后被错误覆盖；未据 gold 差异推断代码写错。额外未比较字段不纳入官方判错规模。'
obj={'task':'038','phase':'calibration_blind_sealed','sealed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manual':'docs/标注手册_v3.2.md','manual_sha256':hashlib.sha256((R/'docs/标注手册_v3.2.md').read_bytes()).hexdigest(),'blind_restriction':'封存前未阅读校准表在034/036、018逐表标注以及037报告的内容；036_objects只程序筛选impl-006/007排除ID；保护文件仅按字节计算hash。读过037封存脚本/验证脚本，内含的是另外两张校准表，不含本次答案。','objects':objs,'rule_questions':['guide_event 三个单改的行规模都不变，但格子减少可区分。按第7节“比不出时按格子数”以格子排序；若解释为可计算行数时必须坚持行数零减少，则需要组合修复口径。此处将读法保留供解盲检查，不改手册。']}
p=R/'records/038_calibration_blind_sealed.json';assert not p.exists();write(str(p.relative_to(R)),obj)
h=hashlib.sha256(p.read_bytes()).hexdigest();write('records/038_checks/calibration_seal.json',{'sealed_path':str(p.relative_to(R)),'sha256':h,'sealed_at_utc':obj['sealed_at_utc'],'comparison_read_after_this_seal':True});print(h)
