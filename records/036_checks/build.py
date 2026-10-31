"""Build task036 from explicitly reviewed disclosure decisions, without changing034."""
import csv,json,re,hashlib,collections
from pathlib import Path
R=Path(__file__).resolve().parents[2];OUT=R/'records/036_checks';ANN=R/'records/036_annotations';ANN.mkdir(exist_ok=True)
def readcsv(n):return list(csv.DictReader((R/f'records/{n}.csv').open()))
def dump(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2))
def blocks(id):return dict(re.findall(r'<!-- original:(.*?) chars:\d+ -->\n```[^\n]*\n(.*?)\n```',(R/f'records/028_kramabench_packages/{id}.md').read_text(),re.S))
G={1:'交付物里针对本处说明了',2:'交付物里只有通用说明',3:'过程中意识到了，交付物里没提',4:'看到了相关信息，但没有意识到的迹象',5:'没有迹象'}
oldmap={'针对本处的具体说明':1,'只有通用策略说明':2,'看到了但没提':4,'没有迹象':5}
oldobjs=readcsv('034_objects');oldpts=readcsv('034_points');delivery=json.loads((OUT/'delivery_sources.json').read_text());audit018=json.loads((R/'records/018_uncertainty_audit.json').read_text());kj=json.loads((R/'records/034_checks/krama_decisions.json').read_text())['judgments'];presence=json.loads((R/'records/034_checks/dacomp_trace_presence.json').read_text())
# Each entry was reviewed against final answer and intermediate evidence; these are not renames of034 grades.
K={
'archeology-easy-8':(3,'step.5.reasoning.1'), 'archeology-hard-1':(3,'step.8.reasoning.1'),
'archeology-hard-12':(1,'final_answer'),'archeology-hard-2':(3,'step.8.reasoning.2'),
'archeology-hard-5':(4,'step.5.feedback'),'archeology-hard-7':(3,'step.4.reasoning.1'),
'archeology-hard-9':(3,'step.3.reasoning.1'),'astronomy-easy-6':(3,'step.4.reasoning.1'),
'astronomy-hard-12':(3,'step.8.reasoning.1'),'astronomy-hard-8':(3,'step.11.reasoning.1'),
'astronomy-hard-9':(4,'step.5.feedback'),'biomedical-easy-2':(4,None),
'biomedical-easy-9':(1,'final_answer'),'biomedical-hard-5':(4,None),'biomedical-hard-8':(3,'step.16.reasoning.3'),
'environment-easy-2':(3,'step.5.reasoning.1'),'environment-easy-3':(3,'step.9.reasoning.1'),
'environment-easy-5':(5,None),'environment-hard-15':(3,'step.6.reasoning.1'),
'environment-hard-16':(3,'step.4.reasoning.1'),'environment-hard-18':(3,'step.3.reasoning.1'),
'environment-hard-19':(3,'step.8.code'),'environment-hard-20':(3,'step.8.reasoning.1'),
'environment-hard-7':(5,None),'legal-hard-14':(5,None),'legal-hard-17':(3,'step.5.reasoning.1'),
'legal-hard-18':(4,'step.6.feedback'),'legal-hard-22':(4,'step.3.feedback'),
'legal-hard-24':(3,'step.7.reasoning.1'),'legal-hard-29':(3,'step.11.reasoning.1'),'legal-hard-8':(5,None),
'wildfire-easy-1':(3,'step.6.reasoning.1'),'wildfire-easy-9':(5,None),'wildfire-hard-14':(4,'step.4.feedback'),
'wildfire-hard-16':(5,None),'wildfire-hard-17':(4,'step.3.feedback'),'wildfire-hard-18':(1,'final_answer'),
'wildfire-hard-19':(1,'final_answer'),'wildfire-hard-21':(3,'step.10.reasoning.1'),
'wildfire-hard-4':(3,'step.5.reasoning.1'),'wildfire-hard-6':(3,'step.4.reasoning.1')}
# Generic final disclosures: quote literal source text, not functionality lists.
DQ={
1:'转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。',
2:'Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.',
3:'契约对来源重复记录以及部分聚合排序并未规定唯一 tie-breaker；按 DuckDB 实际行为保留未指定并列顺序，不额外引入业务假设。',
4:'不合格必填字段、无效日期和过短邮编按规则筛除。',
6:'对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。',
17:'staging 对声明为主键的空值行进行过滤，并按主键分组只保留一条记录以满足唯一性；若重复键的内容不一致，合同没有规定优先版本，因而保留记录选择未定义，重复记录中的非键值可能丢失。',
21:'事件 attribution 解析按契约优先级提取 JSON 子事件 ID，查找限定同一 `source_relation`；事件重复保留且照常计数。',
24:'可选邮箱/名称/手机号字段验证失败时置 NULL，记录仍保留。',
25:'依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。',
29:'必填字段空值或转换失败的记录按契约过滤；可选字段转换失败会成为 `NULL`。',
30:'合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。'}
D1={4:'History 原始表没有契约字段 `created_date` / `history_unique_key`，使用源 `_fivetran_start` 作为变更时间，并以 `_fivetran_start` 与 `_fivetran_end` 计算字符串唯一标识；该映射使快照能够按源可用的版本时间运行。',14:"原始 Qualtrics 时间文本带时区后缀（例如 `+0800`），DuckDB 直接 `try_cast(... AS TIMESTAMP)` 无法解析。日期相关 SQL 改用 `try_strptime(..., '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP`；不可解析日期在日期计算中排除。",20:'原始 conversation part 文件中的实际列数据与源 schema 声明不一致：对话 ID 实际可从 part `id` 的前缀提取，事件时间可从错位的原始 `conversation_id` 字段解析，事件类型可从 `subject` 字段回退获取。',27:'Duplicate account codes exist in source; the invoice enrichment chooses one account deterministically by lowest `account_id` to prevent duplicate output line rows. This can discard alternate account attributes for colliding codes.'}
Dgrades={1:[2],2:[4,2,4],3:[2],4:[1,2],5:[4],6:[2]*17+[4]*3,7:[3,3],8:[4],9:[4,4],10:[4],11:[4]*3,12:[4]*2,13:[4,5],14:[1],15:[4],16:[4]*6,17:[2],18:[3,3],19:[4,4],20:[1,1,1],21:[2],22:[4,4],23:[4,4],24:[2],25:[2,2],26:[4],27:[1],28:[4],29:[2],30:[2]*11}
reasons={
'archeology-easy-8':'中间明确比较含空串56与剔除空串55；这是对计数处理的意识，并不表示agent看过隐藏参考52。最终仅55。',
'archeology-hard-1':'中间明确用两端日期插值取平均；最终仅数值，未解释这个范围口径。',
'archeology-hard-5':'用户要求保留034，四档旧名仅映射为等义五档第4档；不重审类别。',
'biomedical-easy-9':'最终答案本身点名sheet A和FDR.protein，属于具体说明；代码写错类别不随说出档位变化。',
'environment-easy-5':'思考说整洁展示，并未明确考虑多附带数值是否改变答案形式；最终额外数值自身不当成对呈现选择的说明。',
'legal-hard-18':'中间计算、已见2007和2024数量不等于意识到应改基数；对缺失年龄的假设是另一处。',
'legal-hard-22':'看到各类报告数量，正常写分母并不证明意识到all reports的两种范围。',
'wildfire-hard-14':'中间比较0.64/0.42针对AQI阈值，不是本错误点的州/县比例加权；只记相关信息可见。',
'environment-hard-19':'中间代码解释两个年份及布尔值语义，最终只有True，无法看到其判定解释。',
'wildfire-hard-6':'中间明确声称NOAA从2000开始；最终相关覆盖前提没有交代。'}
newcat={'archeology-hard-12':'已说出的选择','astronomy-hard-8':'Unstated Choice','wildfire-hard-18':'已说出的选择'}
Bwhy={
'archeology-hard-12':'按第7节同类候选规则补为已说出的选择（低把握）。起止年边界、原记录/同演员重叠合并、现代国家归属均是题面未定的处理约定；最终明确报告按起始年计449、全段计447和重叠归属。复用034合并诊断449→446；没有声称已逐项解释409。保留034同一候选组，组内具体排序未知。',
'astronomy-hard-8':'按第7节同类候选规则补为Unstated Choice（低把握）。训练比例、随机/时间切分、seed、小时聚合及有效标记处理均属未定处理约定。最终只交两个RMSE，中间step9/11才讨论方案，因此第3档。复用034的21条样本切分比较；本次按数值距离复算，但不将整套70/30方案冒充一个已隔离的单改。',
'wildfire-hard-18':'按第7节同类候选规则补为已说出的选择（低把握）。控制变量集、log1p变换、75% suppression分界、建筑威胁量组合均沿用034的Choice候选解释。最终具体披露这些设定；未知哪个选择贡献最大，不宣称已复现隐藏模型。',
'archeology-hard-2':'补做三项沿原链到step8最终答案的单改。基线50.25（差11.83）；只反转年龄顺序49.75（差11.33）；只改年度插值50.25；只按年合并50.25。方向单改确定减少0.50，但候选年度处理链尚未识别，不能把测试的两种年度方案当成穷尽。新诊断发现隐藏日历7507个值与第一Age_ky列先round再乘1000全部相同；该轴并非湿干指数自带Age_ky.3。隐藏增长标记却有8360个（均值38.421%），和5993个有效湿干观测不等长，缺失行、年份并列排序/填充的作用未能分离。候选仍包含数据时间轴理解错误、未定抽样/缺失处理及参考链不一致，保持无法判定（低）。不是因减少不足一半或仍有残差而拒绝方向项，而是另一异类候选的修复尚不可确定。'}
points=[];audits=[];di=collections.Counter()
for old in oldpts:
 p=dict(old);obj=p['对象编号'];name=p['错误点名称'];bench=p['benchmark'];extra=[];evidence=[]
 if bench=='KramaBench':
  b=blocks(obj);grade,event=K[obj]
  if name=='Violation大小写并非统一':grade,event=4,'step.5.feedback'
  if event and event not in b:
   if grade<=3:raise ValueError((obj,event))
   event=None
  if grade==4 and not event:
   n=next(x['event'] for x in kj[obj] if x['name']==name);event=f'step.{n}.feedback'
  if event and event in b:evidence=[{'source':f'records/028_kramabench_packages/{obj}.md','event':event,'quote':b[event]}]
  reason=reasons.get(obj,'最终答案没有说明该处；第3档依据所引中间事件对做法、前提或呈现的明确表述。' if grade==3 else '最终答案明确具体说明该处。' if grade==1 else '已读最终答案及相关轨迹；只有相关信息，无该错误点的自觉表述。' if grade==4 else '已读最终答案和轨迹；未发现对本错误点的意识或说明，普通表达式/答案值不自动算说明。')
  if name=='Violation大小写并非统一':reason='step5确实看到分年计数和2021为0，属于相关信息，故第4档；原step2被截断，不能声称看到了足以证明yes大小写差异的原值，证据在场仍否。'
  if obj in newcat:p['类别']=newcat[obj]
  if obj=='astronomy-easy-6':
   p['角色']='主要' if name=='率估计器' else '参与';extra=['records/036_checks/astronomy-easy-6_scales.json']
  if obj=='archeology-hard-2':extra=['records/036_checks/rerun_summary.json','records/036_checks/archeology-hard-2_annual_diagnostic.json']
  final=b['final_answer']
 else:
  num=int(obj[5:8]);id=obj[:8];grade=Dgrades[num][di[num]];di[num]+=1;d=delivery[obj];trace=audit018[id]['trace_file'];events=json.loads((R/trace).read_text());evdict={e['id']:e for e in events};final=d['report'] or '\n'.join(e.get('args',{}).get('final_thought','') for e in d['finish'])
  reason='最终报告、全部交付SQL注释和相关中间轨迹已核对。只有普通映射/计算或列信息，不自动认作意识到该错误点。'
  if grade in [1,2]:
   quote=D1[num] if grade==1 else DQ[num]
   if num==30 and name=='account_source':quote='Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。非关键不可解析值转为 NULL。'
   if num==30 and name=='created_date_nullable':quote='Staging 采用安全类型转换、删除标记过滤、更新时间驱动的最新记录标记；账户状态按契约规范化/过滤，invoice 创建日期按契约限制时间范围。'
   assert quote in final,(obj,name,quote)
   found=next((e for e in d['finish'] if quote in e.get('args',{}).get('final_thought','')),None)
   evidence=[{'source':trace if found else d['report_path'],'event':str(found['id'])+'.args.final_thought' if found else 'final result.md','quote':quote}]
   reason='最终交付有针对本处的具体说明。' if grade==1 else '交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。'
  elif grade==3:
   event=65 if num==7 else 57
   quote='Apple 订阅 summary/event 字段有若干原始字段与 staging 字段语义不完全一致，使用可用列映射且转换兼容字段类型。若这类字段用于正式订阅财务决策，应以源端字段定义进一步确认。' if num==7 else "# Correct field source mapping; canonical foreign keys should remain FK columns, not the row's own id."
   assert quote in evdict[event]['args']['command'];evidence=[{'source':trace,'event':str(event)+'.args.command','quote':quote}]
   reason='报告草稿明确意识到本组来源映射的语义不一致；event66/68两次写入失败，未留finish或报告文件，只算过程中意识到。草稿未点名两个字段，组级意识的读法列为规则问题。' if num==7 else '中间代码注释明确识别外键不能取行自身id这一前提；未修到本表两外键，也未在最终报告说明。本组共享前提的意识归第3档，非已正确修复。'
  elif grade==4:
   item=next((x for x in audit018[id]['items'] if x['item']==name),None)
   if item and item.get('evidence'):
    for e in item['evidence']:
     field=e['field'];v=evdict[e['event']]
     for part in field.split('.'):v=v.get(part,'') if isinstance(v,dict) else ''
     assert e['quote'] in v,(obj,name,e['event']);evidence.append({'source':trace,'event':str(e['event'])+'.'+field,'quote':e['quote']})
   else:
    a=next(x for x in presence if x['object']==obj)
    evidence=[{'source':'records/034_checks/dacomp_trace_presence.json','event':str(a['event']),'quote':a['paragraph'],'note':'仅已留存的可见契约片段；不扩张证据在场字段'}]
  if num==13 and name=='clv_denominator':reason='最终未说明此非原因前提；未找到该分母歧义的意识证据，第5档。'
 # Main disclosure convention applies to underlying Choice/Downgrade only.
 base={'已说出的选择':'Unstated Choice','已说出的降级':'Quiet Downgrade'}.get(p['类别'],p['类别'])
 p['类别']=({'Unstated Choice':'已说出的选择','Quiet Downgrade':'已说出的降级'}.get(base,base) if grade==1 else base)
 p.pop('是否说出（四档）');p['是否说出（五档）']=G[grade]
 change='改类别' if p['类别']!=old['类别'] else '只改档位' if grade!=oldmap[old['是否说出（四档）']] else '未改'
 if obj in Bwhy:change='补完无法判定'
 p['相对034']=change
 p['证据是复用还是新做']='复用；036新核交付物/轨迹'+('；新做单改/诊断' if extra else '')
 p['证据来源']+=';records/036_checks/disclosure_audit.json'+(';'+';'.join(extra) if extra else '')
 if bench=='KramaBench' and obj in ['archeology-hard-1','archeology-hard-7','archeology-hard-9','astronomy-easy-6','astronomy-hard-8','environment-easy-3','environment-hard-16','environment-hard-18','legal-hard-17','legal-hard-18','legal-hard-22','wildfire-hard-17','wildfire-easy-9','wildfire-hard-16']:
  p['证据来源']+=';records/036_checks/endpoint_audit.json'
 a={'benchmark':bench,'对象编号':obj,'错误点名称':name,'grade':grade,'是否说出':G[grade],'034档位':old['是否说出（四档）'],'034类别':old['类别'],'036类别':p['类别'],'相对034':change,'reason':reason,'evidence':evidence,'final_answer_or_report_sha256':hashlib.sha256(final.encode()).hexdigest(),'final_answer':final if bench=='KramaBench' else None}
 audits.append(a);points.append(p)
assert len(points)==123 and all(di[n]==len(gs) for n,gs in Dgrades.items())
objects=[]
for old in oldobjs:
 o=dict(old);obj=o['对象编号'];ps=[p for p in points if p['对象编号']==obj]
 if ps:
  mains=[p for p in ps if p['角色'] in ['主要','并列']];cats={p['类别'] for p in mains};o['主要原因']=next(iter(cats)) if len(cats)==1 else '多因并列'
  o['并列项']='；'.join(p['错误点名称']+':'+p['类别'] for p in mains) if len(mains)>1 else ''
 if obj=='astronomy-easy-6':o['是否只能组合修复']='否'
 o['相对034']=next((c for c in ['补完无法判定','改类别','只改档位'] if any(p['相对034']==c for p in ps)),'未改');objects.append(o)
for stem,rows,fields in [('objects',objects,list(oldobjs[0])+['相对034']),('points',points,[c if c!='是否说出（四档）' else '是否说出（五档）' for c in oldpts[0]]+['相对034'])]:
 with (R/f'records/036_{stem}.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
dump('disclosure_audit.json',audits)
for o in objects:
 if o['相对034']=='未改':continue
 obj=o['对象编号'];prefix='kramabench' if o['benchmark']=='KramaBench' else 'dacomp';old=next(x for x in oldobjs if x['对象编号']==obj);filename=f'{prefix}_{obj}.md';original=R/f'records/034_annotations/{filename}';originaltext=original.read_text();why=originaltext.split('## 错在哪里\n',1)[-1].split('\n## ',1)[0].strip() if '## 错在哪里\n' in originaltext else '基础错误点与证据沿用034对应标注。'
 lines=[f'# {o["benchmark"]} / {obj}：v3.1 修订', '',f'相对034：**{o["相对034"]}**。主要原因：{old["主要原因"]} → **{o["主要原因"]}**；只能组合修复：{old["是否只能组合修复"]} → {o["是否只能组合修复"]}；把握：{o["把握"]}。','',f'基础错误机制及原有查询见 [034原标注](../034_annotations/{filename})。本页只修订交付口径及本次指定的单改规则。','', '## 修订依据','',Bwhy.get(obj,'逐点检查最终交付物，把中间步骤的意识和交付说明分开。类别仅按第8节已说出主口径调整；其余基础类别沿用034。')]
 if obj=='astronomy-easy-6':lines+=['','规模按逐元素绝对差合计：基线0.078422；只改估计器0.042544（减少0.035878）；只改符号0.068716（减少0.009706）；两项都改0.000056。原round(...,6)保留，未额外改到gold的四位小数。估计器为主要，符号为参与；两者单改都有收益，不是只能组合修复。见[单改记录](../036_checks/astronomy-easy-6_scales.json)。']
 for p,a in [(p,next(a for a in audits if a['对象编号']==obj and a['错误点名称']==p['错误点名称'])) for p in points if p['对象编号']==obj]:
  lines+=['',f'## {p["错误点名称"]}','',f'- 角色：{p["角色"]}；类别：{a["034类别"]} → **{p["类别"]}**。',f'- 是否说出：{a["034档位"]} → **{p["是否说出（五档）"]}**。',f'- 证据在场：{p["证据在场"]}；曾经理解对过：{p["曾经理解对过"]}；系统提示是否适用：{p["系统提示是否适用"]}（均沿用034）。','',a['reason']]
  for e in a['evidence']:
   lines+=['',f'来源：`{e["source"]}`，事件/位置 `{e["event"]}`。','```text',e['quote'],'```']
  lines+=['',f'证据复用/新增：{p["证据是复用还是新做"]}。来源：{p["证据来源"]}。']
 if obj=='archeology-hard-2':lines+=['','## 新单改的可识别范围','','方向变化在已测三个单改中收益最大；它是已确认的减差因素，但另一候选（隐藏日历/空行链）的具体修复未识别，暂不能排序全部候选。原合并错误点保留，不把年度聚合零收益写成已排除所有年度因素。见 `036_checks/archeology-hard-2_*.json` 与 `annual_diagnostic.py`。']
 (ANN/filename).write_text('\n'.join(line.rstrip() for line in '\n'.join(lines).splitlines())+'\n')
stats={'objects':{b:{'034':dict(collections.Counter(x['主要原因'] for x in oldobjs if x['benchmark']==b)),'036':dict(collections.Counter(x['主要原因'] for x in objects if x['benchmark']==b)),'changes':dict(collections.Counter(x['相对034'] for x in objects if x['benchmark']==b))} for b in ['DAComp','KramaBench']},'grades':{b:dict(collections.Counter(a['grade'] for a in audits if a['benchmark']==b)) for b in ['DAComp','KramaBench']},'grade3_choice_downgrade':{b:dict(collections.Counter(a['036类别'] for a in audits if a['benchmark']==b and a['grade']==3 and a['036类别'] in ['Unstated Choice','Quiet Downgrade'])) for b in ['DAComp','KramaBench']},'changed_annotations':sum(x['相对034']!='未改' for x in objects)}
dump('summary.json',stats);print(json.dumps(stats,ensure_ascii=False,indent=2))
