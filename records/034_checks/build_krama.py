from replay import *
import csv
D='Data Misconception';I='Intent Misreading';U='Unstated Choice';Q='Quiet Downgrade';X='其他';C='代码写错';F='Form Mismatch'
S={}
def add(id,name,cat,role,why,event,grade='没有迹象',present='不适用',correct='不适用',source='',rule='',confidence='中'):
 S.setdefault(id,[]).append(dict(name=name,cat=cat,role=role,why=why,event=event,grade=grade,present=present,correct=correct,source=source,rule=rule,confidence=confidence))
add('archeology-easy-8','最终参考值与子任务不一致',X,'主要','agent 55，gold 52；子任务4明确55。agent对分号分隔、空串过滤的结果与子任务一致。不能以最终52反推另有三处应合并。',7,'针对本处的具体说明',source='subtask.4.answer',rule='读法一：55是未清洗引用；读法二：最终参考值与子任务冲突。选二：子任务明确给55，未找到唯一支持52的清洗规则。')
add('archeology-hard-1','只平均两个端点',I,'主要','题面average ... from the first and last time且规定样点间线性插值，按整个区间平均的自然读法；step8只平均两端。单改年度格点8347.1887→8477.5473，与gold差230.3411→99.9825；未解释残差。',8,'针对本处的具体说明','是','否','records/032_kramabench_queries/04_archeology_hard_1.stdout.txt;records/034_checks/archeology-hard-1_interval_mean.json',rule='读法一：from first and last指仅两端；读法二：从首至尾整个区间。选二，插值条件支持区间；但gold子任务年龄整数化/插值规则仍未定，不能宣称单改完全解释。',confidence='低')
add('archeology-hard-2','时间方向及年度抽样残差','无法判定','主要','按age升序得到50.25%；032以相同有效列反序49.75%，仍非38.42。子任务使用日历年且包含重复整数年，无法由目前的单改证据确定差异主项；不把反序一项冒充完整解释。',7,source='records/032_kramabench_queries/05_archeology_hard_2.stdout.txt',rule='读法一：按原样点计增加比例；读法二：按年度插值/聚合后计比例。方向可由年龄轴判断，但年度离散规则未规定；暂不强定主因。',confidence='低')
add('archeology-hard-5','参考样本与地域限定冲突',X,'主要','题面In the Maltese dataset；agent筛Region=Malta并取最北样本；gold子任务选row766。032核实row766为Southern Italy、Serra Cicora，而非Malta。存在题面地域/数据集称谓歧义，不据隐藏子任务反判agent应选意大利。',7,'看到了但没提',source='records/032_kramabench_queries/02_archeology_hard_5.stdout.txt',rule='读法一：Maltese指Malta地区；读法二：整本regional数据集俗称Maltese。选一；没有可见说明把Maltese定义为全区域，gold样本地域已核实。',confidence='低')
add('archeology-hard-7','距离度量','已说出的选择','主要','0.1 degrees未指定平面欧氏或球面角距；step3算274、step5球面292、最终选球面。单改阈值使用dist得到274，差18→0。',5,'针对本处的具体说明',source='records/034_checks/archeology-hard-7_euclidean.json',rule='是否代码里明确标明great circle就算具体说明？选是：这里实际并列计算了两个度量并标明名称，不是普通无说明操作。')
add('archeology-hard-9','last sample与highest rank冲突',X,'主要','题面明确last sample，agent step6按anc_idx排序取last；重放-0.210104。隐藏子任务6却问highest numeric rank；单改排序到最高rank得到0.015648。',6,'针对本处的具体说明',source='records/032_kramabench_queries/01_archeology_hard_9.stdout.txt;records/034_checks/archeology-hard-9_highest_rank_diagnostic.json',rule='按最后一条数据或最高rank？选题面最后一条；子任务仅用于诊断，不能作为agent应知要求。',confidence='高')
add('archeology-hard-12','冲突合并和时间边界','已说出的选择','主要','agent明确报告449个起始年范围内冲突及447个全段在范围内的备选；gold409来自隐藏子任务对同演员重叠年份去重。题面没有给重叠合并和演员归并算法。未重建全部409的合并过程，主因把握低。',11,'针对本处的具体说明',source='subtask.3.query;subtask.5.query;subtask.6.answer',rule='读法一：原记录是冲突；读法二：演员同且年份重叠必须并为一个。选Choice，材料不能唯一确定归并与现代国家映射。',confidence='低')
add('astronomy-easy-6','衰减率估计及符号','已说出的选择','主要','agent选负的回归斜率，gold用端点差/天；题面average rate没有指定估计器及decay正方向。step3已输出两种估计，step4注释明确minus least-squares slope。',4,'针对本处的具体说明',source='records/034_checks/astronomy-easy-6_endpoint_diagnostic.json',rule='回归/端点与符号能否合成一处？本条先视为交付的率估计约定；尚未各自单改排序，故低把握而不伪称已验证两者并列。',confidence='低')
add('astronomy-hard-12','自造mock势能场','已说出的降级','主要','npz提供坐标网格和其他场，未提供所要求的势能值；agent没有现成势能场，却定义地表零点的GM(1/R-1/r)替代并提交。step8/13 reasoning具体说明无values file需自行生成。032的g(R+h)诊断也不完全匹配gold，不能把它当规范。',8,'针对本处的具体说明',source='records/032_kramabench_queries/03_astronomy_hard_12.stdout.txt',rule='读法一：题目mock允许自己定义，归Choice；读法二：要求输入场不存在而自造替代，归Downgrade。依v3“要求的输入不存在”选二；若预期要生成场，应修订题面依据而非凭gold反推。',confidence='低')
add('astronomy-hard-8','未指定训练测试及预处理','已说出的选择','主要','题面只要test RMSE，未给70/30、随机种子、有效标记及按小时聚合规则；agent比较seed和chrono，选80/20 seed42。隐藏子任务70/30不能确立agent义务。现有证据不足对每个预处理单独排名。',9,'针对本处的具体说明',source='records/034_checks/astronomy-hard-8_split_candidates.json',rule='拆成多个Choice逐个单改或把建模方案视为一项？暂按方案列一项，低把握；不能从不同RMSE倒推出任一选项错误。',confidence='低')
add('astronomy-hard-9','OMNI列号错位',D,'主要','P：header=None的om[50]是ap-index。文档WORD50=ap-index、WORD51=f10.7，Python列49才是ap；032只改om[50]→om[49]，lag47→24，差23→0。',5,'看到了但没提','是','否','records/032_kramabench_queries/06_astronomy_hard_9.stdout.txt',rule='step6反馈整体截断但50/51两行实际保留；只认实际保留原文，不认被省略部分。',confidence='高')
for id,ev,desc in [('biomedical-easy-2',4,'68.1对68.5；排除Case_excluded=Yes后12行平均68.5'),('biomedical-hard-5',6,'2.4241对2.6563；排除后12行线性尺度中位数2.6563')]:
 add(id,'未落实研究纳入范围',I,'主要',f'题面限定研究中的Serous样本；Case_excluded的含义明确，agent未落实排除标记。{desc}。只见列名不足确定这14行中的具体排除事实。',ev,'看到了但没提','否','否','records/032_kramabench_queries/07_biomedical_serous.stdout.txt',rule='可读作全部附件Serous行或正式研究样本；选后者。Data/Intent边界：标记含义清楚，缺的是落实题目研究范围，因此Intent。证据在场严格要求看到具体排除信息，只有列名填否。')
add('biomedical-easy-9','最终调用背离最后明确选择',C,'主要','step11 reasoning明确选择Gene列及FDR.phos；实际final_answer却交mmc6 sheetA FDR.protein=-0.30146。step10已经计算不同候选。正确想法与交付代码不一致，先排代码写错；题目模态本身仍有歧义。',11,'针对本处的具体说明',source='step.10.feedback',rule='读法一：模态未定的Choice；读法二：最后意图与调用参数冲突。依第3节先排代码写错选二；仍需区分最后意图正确仅对实现一致性，而非靠gold证明模态。',confidence='低')
add('biomedical-hard-8','protein与site粒度',X,'主要','题面明确protein sites，agent返回5个位点而gold仅2个protein。去位点后相同；不能反判输出位点违背题面。',16,'针对本处的具体说明',source='records/034_checks/form_checks.json',rule='sites可被宽泛读为proteins或具体磷酸位点；选择后者自然读法，记参考粒度与题面不一致，而非Form Mismatch。')
forms=['environment-easy-2','environment-easy-5','environment-hard-15','environment-hard-20','environment-hard-7','legal-hard-14','legal-hard-24','legal-hard-29','wildfire-easy-1','wildfire-hard-4']
for id in forms:
 add(id,'答案附带说明或额外字段',X,'主要','输出内容可经仅移除说明/多余字段恢复gold；新做输出级诊断相等，未重算业务数值。题面没有明确要求裸值或禁止解释。',0,'没有迹象',source='records/030_kramabench_tolerance_details.json;records/034_checks/form_checks.json',rule='读法一：问which/how many就隐含只交裸值；读法二：不等于明确格式规定。依v3选二，系统通用Python值要求只另记。',confidence='高')
add('legal-hard-8','bool与字符串比较',X,'主要','题面要求True or False，agent交Python True，gold是字符串True；仅str()即一致。agent已经遵守明确形式，不能将gold的存储类型当作题面规定。',5,'没有迹象',source='records/034_checks/form_checks.json',rule='True要求布尔还是字符串？题面未指定字符串，且系统要求Python值，agent bool合法；归其他。',confidence='高')
add('wildfire-hard-16','未规定的三位小数',X,'主要','要求list of two numbers但没有规定三位小数；agent已交列表，保留完整精度，round(3)后和gold一致。',0,'没有迹象',source='records/030_kramabench_tolerance_details.json;records/034_checks/form_checks.json',rule='题面只要求列表不能推出三位小数；数值显示精度规范化视作呈现，保留原计算。',confidence='高')
add('environment-easy-3','擅限Boston Harbor',I,'主要','题面问beaches且没有Boston Harbor限制；step7已经算全域268，step9改取名单8个海滩得到3。全域诊断复现268。',7,'针对本处的具体说明','是','是','records/034_checks/environment-easy-3_all_beaches.json',confidence='高')
add('environment-hard-16','擅限Boston Harbor',I,'主要','题面marine beaches 2002–2023没有Boston Harbor限制；step5用9个名单，输出0。放开到全部Marine按名称聚合74，差60→14，仍有残差；不能声称已完全复现60。',5,'看到了但没提','是','否','records/034_checks/environment-hard-16_identity_diagnostic.json',rule='海滩身份按名称或community+name？分别74/75且均非60；已核实范围错误能减少差距，但残差不能猜成唯一键问题。',confidence='低')
add('environment-hard-18','只取四城市淡水海滩',I,'并列','题面全部fresh water beaches；额外Community.isin四城市，单改scope仍False。与大小写一起修才True。',3,'针对本处的具体说明','是','否','records/034_checks/environment-hard-18_scope_only.json;records/034_checks/environment-hard-18_combination.json',rule='仅比较有雨量的城市或全州淡水海滩？选题面全州，雨量覆盖不自动缩小水质范围。')
add('environment-hard-18','Violation大小写并非统一',D,'并列','P：全部年份阳性都编码Yes。2021用yes，eq(Yes)得到0；统一lower单改仍False，两处组合后True。',5,'没有迹象','否','否','records/034_checks/environment-hard-18_normalize_only.json;records/034_checks/environment-hard-18_combination.json',rule='原step2输出被截断，不能据全量本地重放推断agent看过2021编码；记录否。')
add('environment-hard-19','True的问法与参考含义',X,'主要','题面different or the same没有明确True对应哪一个；agent算不同并交True，子任务9问是否same并给False。均表达不同年份。signed/absolute和加权虽也不同，当前两种均不同，不能拿它们解释布尔判错。',8,'针对本处的具体说明',source='subtask.4.answer;subtask.8.answer;subtask.9.query',rule='True=不同或True=相同，两种读法均有语法依据；选参考语义未由题面唯一规定，其他。')
add('legal-hard-17','展示比例或精确比例','已说出的选择','主要','step5明确比较3.04%与197015/6471708并选精确比率；题面未指定采用展示舍入比例。改用3.04%得到32542，原32587差45。',5,'针对本处的具体说明',source='records/034_checks/legal-hard-17_printed_share_success.json',rule='distribution指印刷百分比或从计数重算？选两者合理，未规定不用gold倒推。')
add('legal-hard-18','保留2007身份盗窃数量',I,'主要','题面If the 2007 reports were distributed exactly like the 2024 ones；agent用2007已观测identity count259314而非总1070447乘2024类别比率。替换该基数得到91000，126000差35000→0。',5,'看到了但没提','是','否','records/034_checks/legal-hard-18_retry.json',confidence='高')
add('legal-hard-22','all reports分母范围',U,'主要','agent用全部报告6471708，gold用身份盗窃1135291；62982分子一致，改分母0.0097→0.0555。题面all reports既可指全部也可指identity theft子域，不能把隐藏子任务当明文。',4,'没有迹象',source='records/034_checks/legal-hard-22_identity_denominator.json',rule='all reports全局或限定于identity theft？自然全局读法成立，按Choice而不是Intent。')
add('wildfire-easy-9','最终参考与子任务算术不一致',X,'主要','子任务均值0.0128840436减0.0181736257为-0.00528958，舍入-0.0053与agent一致；最终gold却-0.0059。本次原计算复现-0.0053。',5,'没有迹象',source='records/034_checks/wildfire-easy-9_retry.json;subtask.5.answer',confidence='高')
add('wildfire-hard-14','州比例加权口径',U,'主要','agent先按州加总分子分母，gold按县比例等权平均；题面未规定县权重。032县平均0.64688076→0.65，agent0.64，差0.01→0。',4,'没有迹象',source='records/032_kramabench_queries/09_wildfire_hard_14.stdout.txt',rule='汇总比例或县比例均值？两者统计对象不同但题面没定，Choice；不因数值接近就认gold口径必然。')
add('wildfire-hard-17','未限定实际火场监测站',I,'主要','题面weather stations used for fire site monitoring，agent平均全部2965个registry记录，未按fire.station_verified_in_psa筛。以NWS ID匹配759行均值4830.8524，round1=4830.9；3317.37差1513.53→0。',3,'看到了但没提','是','否','records/034_checks/wildfire-hard-17_id_diagnostic.json',rule='是数据对应事实还是要求范围？本项已知只要实际使用站即可，按Intent；哪个ID用于关联用新诊断确认，不据相似名称猜。')
add('wildfire-hard-18','回归设定和响应量','已说出的选择','主要','题面controlling for weather未规定控制集、变换、75% suppression划分与建筑量组合；agent明说log1p、HC3及控制项，给出与gold相反方向。选择机制清楚，尚未逐项复现gold模型，主项排名低把握。',9,'针对本处的具体说明',source='step.6.code;step.6.feedback',rule='建筑威胁量作替代是否Downgrade？agent已具体区分威胁与损失，研究数据含该响应；这里按未定分析模型Choice，若要求必须实际毁损且源不存在应另议。',confidence='低')
for id in ['wildfire-hard-19','wildfire-hard-21']:
 add(id,'参考必需文件缺失','不可评估','主要',('WeatherEvents_Jan2016-Dec2022.csv' if id.endswith('19') else 'ZHVI.csv')+'为子任务明确依赖；递归本地data/kramabench/data未找到。依第3节先排不可评估，不继续把替代量或拒答作为判错原因。',0,'针对本处的具体说明' if id.endswith('19') else '没有迹象',source='records/034_checks/missing_files.json',confidence='高')
add('wildfire-hard-6','误缩短NOAA覆盖起点',D,'主要','P：可比较年度从2002开始；实际monthly_stats从2000开始且NIFC覆盖这两年。032只改between(2002,2024)→(2000,2024)，0.510→0.519，差0.009→0。',4,'针对本处的具体说明','是','否','records/032_kramabench_queries/08_wildfire_hard_6.stdout.txt',rule='agent step4 reasoning已说beginning from year2000，但第8节“曾经理解对过”要求写代码/算结果；仅认该句不能填是，故填否。',confidence='高')
# Conservative object judgments where independent error-point ranking is not established.
for _id in ['archeology-hard-12','astronomy-hard-8','wildfire-hard-18']:
 S[_id][0]['cat']='无法判定'
 S[_id][0]['why']+=' 归因候选是已说出的选择，但还没有足以将多个独立选择逐个定因并排序的单改证据，正式主因留无法判定，不把整套方案捆成已验证错误点。'
 S[_id][0]['rule']+=' 本次正式结论采用无法判定；候选机制不计入已定类别分布。'
S['archeology-hard-2'][0]['source']+=';records/034_checks/climate_diagnostic.json'
S['archeology-hard-2'][0]['why']+=' 新诊断：两种年龄列分别排序、用全部8360行或5993有效点作分母也没有复现38.42。'
_base=S['astronomy-easy-6'][0]
_base.update(name='率估计器',role='并列',why='题面未定端点差或回归。保持负号只改成端点估计，输出[-0.0193,0.002]仍有2个不同元素；两处组合才匹配。',source='records/034_checks/astronomy-easy-6_endpoint_diagnostic.json;records/034_checks/astronomy-easy-6_factorial.json',rule='列表规模按不同元素数：不能因RMSE或数值更接近就计改善。估计器与符号应拆开；二者单改均不减少元素差，组合2→0。',confidence='中')
S['astronomy-easy-6'].append(dict(_base,name='衰减率符号',why='step4明确minus least-squares slope；仅反号成正回归斜率仍两个元素不同。题面decay没有规定正方向，改为端点斜率并采用变化量符号后与gold一致。'))
S['archeology-hard-12'][0]['source']+=';records/034_checks/conflict_diagnostic.json'
S['archeology-hard-12'][0]['why']+=' 新诊断按原Conflict名称合并重叠时段449→446，仍不是409；演员规范化规则未复现。'
S['astronomy-hard-8'][0]['source']+=';records/034_checks/astronomy-hard-8_chrono70_retry.json'
S['astronomy-hard-8'][0]['why']+=' 新诊断70/30时间顺序切分为[6.3294857e-7,5.1632430e-7]，仍非gold两个元素；不能只因数值接近就认已定主因。'
rows=[r for r in csv.DictReader(open(ROOT/'records/029_kramabench_final_scores.csv')) if r['最终状态']!='通过'];objects=[];points=[]
for r in rows:
 id=r['题号']; b=blocks(id); path=f'records/028_kramabench_packages/{id}.md'
 if id=='astronomy-hard-11':
  objects.append({'benchmark':'KramaBench','对象编号':id,'层':'','主要原因':'未交卷','并列项':'','是否只能组合修复':'不适用','把握':'高','旧标签':''}); (ROOT/f'records/034_annotations/kramabench_{id}.md').write_text('# astronomy-hard-11\n\n按029最终状态：未交卷。仅记录，不分析；无错误点。来源：records/029_kramabench_final_scores.csv。\n');continue
 assert id in S,id
 ps=S[id];maincats=list(dict.fromkeys(p['cat'] for p in ps if p['role'] in ['主要','并列']));main=maincats[0] if len(maincats)==1 else '多因并列';combo=id in ['environment-hard-18','astronomy-easy-6']
 objects.append({'benchmark':'KramaBench','对象编号':id,'层':'','主要原因':main,'并列项':'；'.join(p['name']+':'+p['cat'] for p in ps if p['role'] in ['主要','并列']) if len(ps)>1 else '', '是否只能组合修复':'是' if combo else '否','把握':min((p['confidence'] for p in ps),key=lambda x:['低','中','高'].index(x)),'旧标签':''})
 lines=[f'# KramaBench / {id}（v3）','','## 错在哪里',ps[0]['why'],'','## 题面与判错记录',f'来源：[{path}](../028_kramabench_packages/{id}.md)，官方状态按029未通过不改。','```text',b['query'],'```','agent最终答案：','```text',b['final_answer'],'```','参考答案：','```text',b['gold_answer'],'```',f'主要原因：{main}；只能组合修复：{"是" if combo else "否"}。']
 for p in ps:
  ev=p['event']; tags=[f'step.{ev}.reasoning.1',f'step.{ev}.code'] if ev else []
  system='是' if id in forms or id in ['legal-hard-8','wildfire-hard-16','biomedical-hard-8'] else '不适用'
  if id=='wildfire-hard-16':system='否'
  lines += [f'## 错误点：{p["name"]}',f'- 角色：{p["role"]}；类别：**{p["cat"]}**；把握：{p["confidence"]}。',p['why'],f'- 是否说出：{p["grade"]}；证据在场：{p["present"]}；曾经理解对过：{p["correct"]}；系统提示是否适用：{system}。']
  if p['cat'] in [D,I]:
   lines += ['在场判断：题面本身已提供范围/规则的项以query原文为证；数据值与编码项只认实际反馈保留内容。没有把子任务作为agent依据。']
   if id=='astronomy-hard-9':tags += ['step.5.feedback']
   if id=='wildfire-hard-6':tags += ['step.4.feedback']
   if id=='environment-easy-3':tags += ['step.7.feedback']
  for tag in tags:
   if tag in b:lines += [f'轨迹事件 `{tag}` 原文（代码行从本代码块1起计）：','```text',b[tag],'```']
  if ev==0:lines+=['本处依据final_answer原文；无单独解释呈现选择的已确认事件，不用最终格式反推曾经说明过。']
  lines += [f'证据：{path}；{p["source"]}。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。','## 本处规则问题',p['rule'] or '未发现需改变手册定义的额外问题。']
  points.append(dict(zip(['benchmark','对象编号','错误点名称','角色','类别','是否说出（四档）','证据在场','曾经理解对过','系统提示是否适用','证据是复用还是新做','证据来源'],['KramaBench',id,p['name'],p['role'],p['cat'],p['grade'],p['present'],p['correct'],system,'复用+新做' if '034_checks' in p['source'] else '复用',path+';'+p['source']])))
 lines+=['## 重放边界','本次仅执行保存代码的确定性计算，不重新调用agent；源文件路径只作环境迁移。034_checks内记录原代码hash、实际执行代码和修改处。标为diagnostic_suffix的操作是输出/数据诊断，不冒充“其余字节不动”的单处源码重跑。未能全量解释参考值的题已在本页写明残差或低把握；不把诊断成功当官方通过。']
 (ROOT/f'records/034_annotations/kramabench_{id}.md').write_text('\n'.join(lines)+'\n')
(ROOT/'records/034_checks/krama_decisions.json').write_text(json.dumps({'objects':objects,'points':points,'judgments':S},ensure_ascii=False,indent=2))
print(len(objects),len(points))
