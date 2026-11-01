"""037 第一阶段：只从盲标允许来源构造封存文件；不读取 034/036 标注。"""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[2]
def event(task,n):
 p=next((R/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent/.events').glob(f'sessions/*/events/{n}.json'))
 return str(p.relative_to(R)),json.loads(p.read_text())
def quote(task,n,field,text):
 p,e=event(task,n)
 v=e
 for k in field.split('.'):v=v[k]
 assert text in v,(task,n,text)
 return {'path':p,'event':n,'field':field,'quote':text}
def point(name,cat,role,P,reason,quotes,evidence,sql_lines,rank):
 return {'错误点名称':name,'类别':cat,'角色':role,'把握':'高','P':P,'判据':reason,'是否说出（五档）':'看到了相关信息，但没有意识到的迹象','disclosure_grade':4,'disclosure_evidence':quotes,'证据在场':'是' if cat=='Data Misconception' else '不适用','evidence_presence_explanation':'契约全文随初始 user message（event 1）直接送入，相关原句完整存在；不是被截断的读文件输出。没有另行读取契约的 run 事件。' if cat=='Data Misconception' else '不适用','曾经理解对过':'否' if cat=='Data Misconception' else '不适用','系统提示是否适用':'不适用','SQL行':sql_lines,'evidence':evidence,'规模与角色':rank}
a='impl-008'; k='impl-021'
q1=quote(a,1,'message','retain rows when the project is missing.')
q2=quote(a,1,'message','ordered ascending by project_name; duplicates are kept;')
q3=quote(k,1,'message','multiple events on a day do not change this count;')
objs=[{'对象编号':a+'_int_asana__task_projects','层':'intermediate','主要原因':'Data Misconception','并列项':'','是否只能组合修复':'否','把握':'高','points':[
point('project_id 取右侧 project，缺失项目关系丢失','Data Misconception','主要','每个 project_task.project_id 都能匹配 project，取右侧 ID 不会丢失原关系 ID。','契约明确允许 project 缺失；014 V1 在 agent 留存 staging 中查得 44 个关系/任务匹配不到。SQL 第 2 行选择 p.project_id。单改为 pt.project_id 同时恢复 ID 并恢复源 ID 类型对应的排序；不把这一类型副作用重复计为独立错误点。',[q1],['records/014_queries_impl-008.json#V1','records/016_reruns_impl-008.json#project_source','records/019_reruns_impl-008_int_asana__task_projects.json#project_source'],'2；聚合 8–12','016/019 同次重跑 L0–L3 均为行 187→71、格 237→71，行减少 116。'),
point('projects_sections 同名 project 内的 section 并列顺序','其他','参与','','契约只规定按 project_name 排序，没有规定同名内 section 的次序。037 诊断确认 79 处字符串差异的 project_name 序列及每个名称内完整项 multiset 全相同，属形式未规定。不是 agent 未遵循已规定的排序。',[q2],['records/037_checks/calibration_diagnostic.json','records/013_packages/013_impl-008_intermediate_int_asana__task_projects.md'],'10','留存结果诊断的基线行 195，单独归一化本列后 122，减少 73；格 245→166。与 016 重跑的 187/237 是不同运行，不混用其基线；同次重跑若消除全部剩余 section 差异最多减少 71 行，小于主点 116。')
]}, {'对象编号':k+'_int_klaviyo__person_metrics','层':'intermediate','主要原因':'Data Misconception','并列项':'','是否只能组合修复':'否','把握':'高','points':[
point('事件连接后仍把 count(*) 当作日期数','Data Misconception','主要','date spine LEFT JOIN events 后每个 person/source/day 最多一行，因此 count(*) 等于 spine 天数。','017 V3 在 agent 可见 staging 中查得 LRqEsZ、MCX88q 于同一天各两条事件；连接后行数膨胀，减去 distinct 事件天数会把重复事件当缺失天。无轨迹证据显示 agent 已正确理解连接后行数却仅手误；不能仅凭 distinct 关键字判代码写错。',[q3],['records/017_queries_impl-021.json#V3','records/017_reruns_impl-021.json#missing_count','records/017_reruns_impl-021.json#spine_days_count'],'7–10','017 两个替代单改各自均使 L0–L3 行 2→0、格 2→0；它们修复同一前提，不重复计点。')
]}]
for o in objs:
 task=o['对象编号'][:8];finish=53 if task==a else 41
 path,e=event(task,finish)
 sql=next((R/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent').glob('dacomp-de-impl-*/sql/intermediate/'+o['对象编号'][9:]+'.sql'))
 assert '--' not in sql.read_text() and '/*' not in sql.read_text()
 o['delivery_review']={'finish_event':finish,'path':path,'field':'args.final_thought','final_report_sha256':hashlib.sha256(e['args']['final_thought'].encode()).hexdigest(),'sql_path':str(sql.relative_to(R)),'sql_has_comments':False,'finding':'最终报告及本表 SQL 注释均无针对这处选择或缺口的说明。其他 SQL 注释关键词扫描也未发现本处说明。普通完成声明不计通用说明；impl-021 报告的 attribution 重复事件计数描述不等同于本表 missing_day_count 的披露。'}
 for p in o['points']:
  p['disclosure_reason']='初始契约提供了相关内容；中间 SQL 只写出实际做法，未显示疑问、候选比较或冲突意识，依 v3.2 记第 4 档。'
  p['evidence_presence_quotes']=p['disclosure_evidence'] if p['类别']=='Data Misconception' else []
  p['rule_issue']=''
obj={'task':'037','phase':'calibration_blind_sealed','sealed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manual':'docs/标注手册_v3.2.md','manual_sha256':hashlib.sha256((R/'docs/标注手册_v3.2.md').read_bytes()).hexdigest(),'blind_restriction':'封存前未查看两表在 records/034_*、records/036_*、notes/034、notes/036 或 018 逐表标注中的内容。仅以程序读取 036 CSV 表头及 impl-001～005 排除 ID，不输出校准表行。','objects':objs,'rule_questions':['Asana 右侧 ID 的选择同时导致未匹配 ID 丢失与数值/文本排序差异。按同一 SQL 源列选择记一个点，保留单独改 numeric order 的 016 试验作为副作用证据，不重复计点。','契约不规定同名内顺序：用呈现归一化诊断量化“其他”的影响；没有向 SQL 强加 gold 的任意并列顺序。']}
p=R/'records/037_calibration_blind_sealed.json'
assert not p.exists(),'封存文件禁止覆盖'
p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
h=hashlib.sha256(p.read_bytes()).hexdigest()
(R/'records/037_checks/calibration_seal.json').write_text(json.dumps({'sealed_path':str(p.relative_to(R)),'sha256':h,'sealed_at_utc':obj['sealed_at_utc'],'comparison_read_after_this_seal':True},ensure_ascii=False,indent=2)+'\n')
print('SEALED SHA256',h)
