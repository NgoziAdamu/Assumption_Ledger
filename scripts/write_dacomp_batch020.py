"""Render table-by-table v2 decisions, preserving blind calibration and full evidence links."""
import csv,json,hashlib,datetime,re
from pathlib import Path
from collections import Counter,defaultdict
from plan_dacomp_batch020 import ROOT,REC,rows,pkg
OUT=REC/'020_annotations';OUT.mkdir(exist_ok=True)
T=['针对本表的具体说明','只有通用策略说明','看到了但没提','没有迹象']
GEN6='event 97（args.final_thought）：脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。'
NULL6='event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。'
GEN7='event 67（args.command 中报告原文）：部分原始表的字段名和契约 staging 字段名不一致，按原始 schema 映射（例如 Google Play 的 `daily_*` 指标、Apple 的 `date`/`territory`/`counts`/`event`）。'
# Each entry is a reviewed, table-specific interpretation, not an automatic label inference.
M={
0:('C','缺少契约明确要求的 account_id 归一化和账户日聚合，直接投影 campaign 行。','契约明确 Group campaign-level rows，并规定 NULL account_id→0、SUM/AVG/MAX；agent FROM 后无 GROUP BY。完整聚合替换是缺失聚合这一逻辑块的诊断。',2,GEN6),
1:('D','仅取 Facebook 分支且将可映射指标填 NULL，遗漏 Apple 的 1500 行。','event23 写明 primary source only / fanin unsupported；event27 fallback 用 source_models[0]。存在 Apple 来源但未作数据判断而裁成单源，按 D；缺失分支单修减少1500行，逐列NULL单修各减少1000格。',2,NULL6),
2:('A','国家静态枚举未给完整清单；agent 单行占位与 gold 的45行枚举不同。','契约指向 inline VALUES dataset in SQL，但所读契约没有国家逐行数值清单。event23只写US，event97具体说明缺少完整静态列举值。差异取决于未给定的枚举内容，不能用gold的国家人口/地区值反推必然正确值。',1,'event 97：`int_ad_reporting__country_mapping` 由于契约没有给出完整静态列举值，目前为单行静态占位映射，不能代表全量国家覆盖。'),
3:('D','客户旅程模型以整列 NULL 和单一 Google staging 来源代替客户级计算。','契约要求客户识别、归因、cohort和分群；event27只匹配字段名称，缺失就NULL，没有对客户数据的具体判断。event97披露客户旅程业务逻辑未完整实现。',1,'event 97：当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。'),
4:('D','地理渠道分析全列 NULL，未实现地域、月份聚合及渠道指标。','契约要求按地理渠道粒度汇总与分档；最终SQL仅从Google staging逐行输出NULL。与gold空结果的差异是实际输出了26031条占位行。',1,'event 97：当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。'),
5:('D','月度国家模型的 country_code、month_year及聚合指标全部占位。','event27在可用campaign字段上做投影；没有生成契约要求的平台到国家映射、月份和分组汇总。整段fallback生成机制为本表的错误点。',2,NULL6),
6:('D','月度地区模型的 region、month_year及地区聚合指标全部占位。','契约的region映射、GROUP BY月度粒度和区域统计未实现；event27同一fallback生成块保留campaign原粒度。',2,NULL6),
7:('D','时间序列模型用全列 NULL 单源投影代替四源日汇总和窗口分析。','契约列明四源拼接、按日平台汇总、滚动统计和最后12个月过滤。最终SQL这些计算均无，仅产生26031行NULL。',1,'event 97：当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。'),
8:('C','Google ROAS额外四舍五入是主要差异；CTR平台分支还发生回落串用。','契约只对CTR/CPC/CPM/CPA规定舍入，Google ROAS明确是正值相除；agent ROUND(...,4)造成433行差异。CTR前6个分支正确写了平台阈值，后2个通用阈值又作用于同一平台，作为I参与因素，有代码自身的意图证据。',3,'event43写统一指标SQL，event67修改base平台字段限定；event84/86只核对输出列。完整99事件未找到ROAS舍入选择的说明；相关字段/表达式已出现，不将执行成功等同于披露。'),
9:('D','执行仪表板逐行输出全 NULL，缺失月度战略指标与过滤。','契约要求月度汇总和最近6个月过滤；event27生成结构占位。gold为空，但agent从1474条上游记录产生1474条占位行。',1,'event 97：当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。'),
10:('D','月度国家 mart 未映射 total_cost 和四个 total_attributed 字段，直接填 NULL。','契约已规定对应输出；上游有候选列，event27仅检查不完整别名映射后填NULL。逐列独立修复，所有有效错误点都是D。',2,NULL6),
11:('D','月度地区 mart 多个财务/KPI映射与生成时间均被填 NULL。','上游有 total_cost、total_attributed和monthly_regional_*；event27通用映射未覆盖这些名称，未作业务判断就置空。mart_created_at也未计算。',2,NULL6),
12:('D','预测分析表全列 NULL，未实现平台月份预测逻辑。','契约要求按月动量/预测/建议及时间窗口；event27只保留第一来源并生成NULL投影。',1,'event 97：当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。'),
13:('C','未按契约删除非法 ad_group_id；同时遗漏CTR/CPC，并有策略清洗歧义。','契约明确ID正则失败delete_row。16条非法ID被agent原样保留；单修过滤减少16行，是有效契约修复中最大的行数改善。gold也把这些ID置NULL并保留行，违反delete_row；其置NULL只作诊断，不冒充C修复。campaign_bidding_strategy契约仅VARCHAR，gold额外白名单/大写化，A；CTR/CPC有可用输入却直接NULL，D。',2,NULL6+' '+GEN6),
14:('A','竞价策略保留原值与gold白名单/大小写清洗的未规定选择为主因。','契约campaign_bidding_strategy只有VARCHAR，没有gold所用枚举白名单。逐列修复行数均不变，残余重复键按固定配对算格子，策略改动减少最多；CTR/CPC/ROAS占位为D参与因素。',2,GEN6+' '+NULL6),
15:('多因并列','缺失归因字段的NULL/0选择，与可计算CTR/CPC的NULL占位并列。','raw schema无attributed_*及归因收入字段，契约没规定缺失值默认0还是NULL，此类及依赖缺失收入的ROAS归A；clicks/impressions/cost存在而CTR/CPC直接NULL归D。各单列修复减少710格、行数不变。',2,NULL6),
16:('多因并列','产品归因字段的缺省选择，与可计算CTR/CPC占位并列。','raw无销售、转化、件数字段，gold常数0和agent NULL属于A；已有clicks/impressions/cost却不算CTR/CPC属于D。各单列修复减少700格。',2,NULL6),
17:('多因并列','搜索归因/匹配类型的缺省选择，与CTR/CPC占位并列。','raw没有归因和match_type列，gold的0/UNKNOWN并非契约规定，归A；CTR/CPC输入存在但占位归D。逐列单修均减少710格。',2,NULL6),
18:('多因并列','货币代码验证遗漏与三个计算指标占位并列；转化率校验为次因。','契约直接规定avg_cpt/avg_cpa货币白名单/大写，遗漏归C；三个计算指标填NULL归D。五项各减少1500格并列；conversion_rate未按0–1置NULL为C，减少1469格。',2,NULL6+' '+GEN6),
19:('D','四个tap和cost衍生指标均为NULL占位。','taps、impressions、local_spend_amount、conversions和new_downloads均在源schema中；代码未对可计算性作判断，直接四列NULL。各单修1500格。',2,NULL6),
20:('D','campaign_id有原始id候选却直接填NULL，导致两侧键不重合。','event19的别名候选未覆盖id就返回NULL；raw.apple_search_campaign_report_data有id。单改ID使3000行规模降至1500，其余计算指标等被键差异遮蔽。',2,NULL6),
21:('D','Facebook action的五个有候选源字段的输出全部占位。','_1_d_view、_7_d_click、value、inline、index在原始schema中，event19通用精确字段匹配未作语义判断，最终输出五列NULL；逐列单改均减少700格。',2,NULL6),
22:('D','spend及CTR/CPC/CPM直接置空。','原始spend和inline_link_clicks/impressions均存在；占位不是源数据缺失导致。逐列单改均减少1000格。',2,NULL6),
23:('A','布尔文本转换为数值1/0，还是TRY_CAST失败置NULL，契约未定。','两列仅规定DECIMAL/BIGINT；agent采用明确披露的TRY_CAST，gold把字符串true/false变为数值。不能把gold选择反推为唯一正确的源语义；各减少700格。',2,GEN6),
24:('A','ad_group_id取base_ad_group资源路径还是原始id，契约未定。','原始id与history直接匹配15/715，base_ad_group直接匹配0；但去掉资源路径前缀后base_ad_group与history匹配715/715。因此不能据第一次全串连接结果声称原列错误，也不能用gold的id选择判U。字段映射/表示有歧义，单改id使1430→705行。',2,NULL6),
25:('D','campaign_id候选id存在却置NULL，造成整表键差异。','原始Google campaign stats有id，event19未作语义映射就填NULL；单修id使52062→26031行。spend等被键差异遮蔽的遗漏单列不能减少基线规模，不当参与因素。',2,NULL6),
26:('多因并列','三列可计算指标的占位，与缺失sends的NULL/0选择并列。','raw有计算指标输入而三列NULL，D；raw没有sends，契约没指定默认0，A。其他互动字段非法文本清理为0还是NULL也未规定，A参与因素。',2,NULL6+' '+GEN6),
27:('多因并列','可用spend及指标占位，与不存在字段的默认值选择并列。','raw.spend及各计算分子分母存在，D；assists/bounce_rate/average_position没有源列，gold常数0与agent NULL归A。单列影响均1500格。',2,NULL6),
28:('多因并列','Pinterest可计算指标占位、impressions合并选择和无源字段默认值并列。','impression_1与impression_2如何合并没有契约映射，数据未给唯一业务结论，A；无源outbound/pin/saves/close_ups/video默认0或NULL为A；clicks及金额/率指标有候选输入却NULL归D。',2,NULL6),
29:('多因并列','Snapchat spend/率指标占位，与缺失/异常字段默认值选择并列。','raw.spend和计算输入存在却NULL为D；ad_account_id不存在、gold填unknown而agent NULL为A；mock/boolean/空文本清理为0或NULL也没有契约规则，A。',2,NULL6+' '+GEN6),
30:('A','不存在advertiser_id时，NULL与unknown默认值选择改变了评测键。','schema无advertiser_id，契约未给默认值；单改unknown使1800→900行，为主因A。spend、conversions和计算指标确有占位遗漏，但各自在原始键差异下单修规模完全不变，不列参与因素。',2,NULL6),
31:('多因并列','Twitter可计算金额/率指标占位，与无源app指标默认值并列。','已有billed_charge_local_micro、clicks/impressions/engagements却不计算，D；没有app_installs/app_opens，默认0或NULL属A；likes/follows的布尔文本数值化未规定，为A参与因素。',2,NULL6+' '+GEN6),
32:('A','同一app/platform/date存在重复行，ROWS窗口未规定同日顺序。','契约仅ORDER BY date_day，未指定同日次序。实际297组同日重复，304条超额行；用gold SQL重新执行仍不复现留存gold窗口值，排除全部窗口及派生列后基准行多重集L0完全一致。差异取决于未规定的同日排序；不能为了匹配gold捏造唯一排序规则。',3,'event14可见上游schema，event16看过installs样例；event29生成ROWS窗口，event56核对health列。70事件未找到同日peer排序或唯一性检验的说明。'),
33:('O','agent按名UNION ALL符合契约，gold按位置UNION交换了Apple下载/删除列。','契约明确值原样传递。gold Google upstream第5列deletions、第6列downloads，Apple顺序相反；SELECT * UNION ALL按位置拼接后再按Google列名取值。交换Apple两列的诊断与gold全表EXCEPT ALL残余0；agent无此交换。',3,'event33写显式列名UNION，event56核对输出列名；未找到对两个来源列顺序差异的说明。'),
34:('O','ROI类别文本按契约输出High/Medium/Low/Uncertain，而gold使用另一组长文本。','契约business_logic与列description均明定短标签，agent逐字实现；gold输出High ROI Expected等。只替换文本后L2全匹配，余下CLV差异为浮点聚合末位。',4,'检查全部70事件及result.md搜索路径，没有发现针对ROI标签差异的说明或观察输出；编写正确标签本身不当作不确定性披露。'),
35:('O','revenue按契约BIGINT转换，而gold保留DECIMAL小数，是主要原因。','原始700行revenue无负数，696行有小数；契约明确BIGINT，agent遵守而gold DECIMAL(15,2)。单改gold类型减少67行，超过name/country选择。空subscription_name默认名与非法country默认US契约未写，归A参与因素。',3,'event14看过financial原始schema；没有针对本表revenue的类型选择或缺省名称/国家规则说明。'),
36:('A','订阅数取subscribers计数，还是两个布尔标志转1/0，契约未映射。','契约只列BIGINT字段名。raw同时有subscribers和active_*布尔标志，数据本身无法判定业务口径；不能仅因gold用了布尔标志归U。active_subscriptions单修影响最大，free_trial为同类A参与因素。',2,'event67：Apple 订阅 summary/event 字段有若干原始字段与 staging 字段语义不完全一致，使用可用列映射且转换兼容字段类型。没有点名active_subscriptions和free_trial_subscriptions各自选择。'),
37:('A','active_devices_last_30_days取active_device_installs或current_device_installs，契约未映射。','两个源字段均非负，5995行不同，名字与数值不能确定30日活跃口径；差异取决于未指定的源列选择。单改current列L0完全匹配。',2,GEN7),
38:('A','设备粒度的30日活跃量源列选择未规定。','active与current两列5994行不同，均是合法非负计数；缺少字段字典不能判定哪列承载30日活跃语义。单改current列L0匹配。',2,GEN7),
39:('A','OS粒度活跃量映射为主因，user_uninstalls计数与布尔化另有差异。','active/current列5993行不同且均非负；契约未给映射。daily_user_uninstalls是数值，gold以CASE WHEN非零→1、agent保留数值，契约无布尔化规定；同类A参与因素。',2,GEN7),
40:('A','overview的30日活跃量源列选择未规定。','active/current列5997行不同且均非负；没有源字段业务说明能唯一确定取法。单改current列L0匹配。',2,GEN7),
41:('O','agent按评级delete_row规则删9行，gold改写中值3并保留。','契约对两列越界明确delete_row；raw daily_average_rating有9条越界、无NULL，total无越界。agent删除9行符合契约，gold保留并纠正值，诊断重现gold。',2,'event67：随后修正了输出列顺序及评级规则：无效的必需平均评级记录删除、契约指定 nullify 的评级/转化率置空或删除。'),
42:('O','agent按契约把3条越界原始转化率置NULL，gold重新算比例保留。','raw有3条越界率；gold使用acquisitions/visitors而非nullify，违反明定处理，单项改变减少3行；剩余1条合法值取源率还是重算比例未规定，A参与因素。',2,'event67：随后修正了输出列顺序及评级规则：无效的必需平均评级记录删除、契约指定 nullify 的评级/转化率置空或删除。')}
# Per-experiment categories. Non-isolated gold reimplementations are explicitly diagnostics.
CAT={0:{'whole_implementation_diagnostic':'C'},1:{'missing_apple_branch':'D'},2:{'whole_implementation_diagnostic':'A'},8:{'google_roas_rounding':'C','ctr_platform_fallthrough':'I'},13:{'invalid_id_contract_delete':'C','campaign_bidding_strategy':'A','click_through_rate':'D','cost_per_click':'D'},14:{'campaign_bidding_strategy':'A'},18:{'avg_cpa_currency':'C','avg_cpt_currency':'C','conversion_rate':'C'},23:{'conversions_value':'A','view_through_conversions':'A'},24:{'ad_group_id':'A'},28:{'impressions':'A'},30:{'advertiser_id':'A'},35:{'revenue':'O','subscription_name':'A','country':'A'},36:{'active_subscriptions':'A','free_trial_subscriptions':'A'},39:{'active_devices_last_30_days':'A','user_uninstalls':'A'},42:{'invalid_rate_policy_diagnostic':'O','valid_rate_formula_choice':'A'}}
for i,cs in {15:['attributed_conversions_14_d','attributed_conversions_30_d','attributed_sales_14_d','attributed_sales_30_d','return_on_ad_spend'],16:['attributed_conversions_14_d','attributed_conversions_30_d','attributed_sales_14_d','attributed_sales_30_d','attributed_units_ordered_14_d','attributed_units_ordered_30_d','return_on_ad_spend'],17:['attributed_conversions_14_d','attributed_conversions_30_d','attributed_sales_14_d','attributed_sales_30_d','match_type','return_on_ad_spend'],26:['sends','comments','follows','likes','shares','video_views','video_completions'],27:['assists','average_position','bounce_rate'],28:['outbound_clicks','pin_clicks','saves','close_ups','video_views'],29:['ad_account_id','conversion_purchases','quartile_1','quartile_2','quartile_3','screen_time_millis','shares','story_completes','video_views','view_completion'],31:['app_installs','app_opens','likes','follows']}.items():CAT.setdefault(i,{}).update({c:'A' for c in cs})
RULES={
2:'本表两种读法：已披露单行占位可读作D；契约引用的枚举表未提供可读作A。本次选A，因为缺失的是应输出的具体静态内容，不能从数据恢复gold的45行及数值；单行覆盖不足事实保留。',
13:'本表agent和gold都没有执行delete_row。两种读法：用gold置NULL作为“修复”排序；或只让真正契约修复参加C排序。本次选后者，gold置NULL重跑仅诊断。gold保留非法ID为契约矛盾，不能把置NULL当正确修复。',
24:'全串连接base_ad_group为0匹配，若忽略资源路径格式会误读为U；去前缀后715/715匹配。最终按未规定的ID表示/映射标A，不从gold推定raw.id必然更正确。',
32:'手册O例子要求契约明确允许任意顺序；本契约只规定按date_day且声称来源唯一，没有明确允许同日任意顺序。本次选A（未定义tie-break），不扩大O定义。虽然唯一性假设实际不成立，但不能证明某种独立修复就是唯一应有的窗口结果，因此不强行归U。',
}
for i in [0,3,4,5,6,7,9,12]:RULES[i]='此表缺失的是整段聚合/分析实现，原SQL由同一个fallback生成块代替。两种读法：按每个输出列拆成多个错误点；或按整体降级/缺失聚合这一块记录。本次按后一种记录。完整gold实现替换只作诊断，不声称它是满足U第4条件的局部修复；类别依据契约和轨迹直接证据。无法从整段替换推定各未实现子计算的相对贡献。'
for i in [14,10,11]:RULES[i]=RULES.get(i,'')+' 评测键并不唯一，v2未指定重复键残余行如何配对；沿用已验证脚本：先抵消相同行，再在同键内按整行字典序配对。格子数会包含配对变化，主因排序是此固定口径下的结果；没有把单列边际差异直接当整表格子规模。'

from review_metadata_dacomp020 import apply_review, item_tier, OVERWRITE_INDICES
apply_review(M, CAT, RULES)

def mdtable(head,data):
 def e(s):return str(s).replace('|','\\|').replace('\n','<br>')
 return '\n'.join(['| '+' | '.join(head)+' |','|'+'|'.join(['---']*len(head))+'|']+['| '+' | '.join(e(v) for v in r)+' |' for r in data])+'\n'
def rr(i):
 basepath=REC/f'020_reruns_{rows[i]["task"]}_{rows[i]["table"]}.json'
 result=json.loads(basepath.read_text());result['evidence_files']=[str(basepath.relative_to(ROOT))]
 extra=REC/f'020_resume_reruns_{rows[i]["task"]}_{rows[i]["table"]}.json'
 if extra.exists():
  newer=json.loads(extra.read_text())
  assert result['runs'][0]['comparison']['levels']==newer['runs'][0]['comparison']['levels']
  result['runs'].extend(newer['runs'][1:]);result['evidence_files'].append(str(extra.relative_to(ROOT)))
 return result
def category(i,label):
 if label in CAT.get(i,{}):return CAT[i][label]
 if i in [32,33,34,41]:return {32:'A',33:'O',34:'O',41:'O'}[i]
 if i in [37,38,40]:return 'A'
 return 'D'
def valid(i,label):
 if i in OVERWRITE_INDICES and label in ['spend','campaign_id']:return False
 if i==13 and 'gold_diagnostic' in label:return False
 if i==30 and label!='advertiser_id':return False
 if i==32:return False
 if i==42 and label=='gold_ratio_diagnostic':return False
 return True

def main():
 # Verify blind decision artifact before reading reference annotations.
 lock=json.loads((REC/'020_blind_lock.json').read_text());assert hashlib.sha256((ROOT/lock['file']).read_bytes()).hexdigest()==lock['sha256']
 blind=json.loads((REC/'020_calibration_blind_decisions.json').read_text())['decisions'];queries=json.loads((REC/'020_queries.json').read_text());diags=json.loads((REC/'020_diagnostics.json').read_text())+json.loads((REC/'020_final_diagnostics.json').read_text());audit=json.loads((REC/'020_trace_audit.json').read_text())
 fields=next(csv.reader(next((REC/'018_annotations').glob('*.csv')).open()));fields=[x for x in fields if not x.startswith('与上一版相比')]
 summaries=[];decisions=[]
 for i,r in enumerate(rows):
  d=pkg(i);runs=rr(i);b=runs['runs'][0]['comparison']['levels'][0];base=(b['row_scale'],b['cell_scale']);q=[x for x in queries+diags if x.get('index')==i and x['kind']=='核实'];qcount=len(q)
  if i<43:
   maincat,short,reason,tier,uq=M[i];ranks=[]
   for run in runs['runs'][1:]:
    if 'comparison' not in run or not valid(i,run['label']):continue
    lev=run['comparison']['levels'][0];gain=(base[0]-lev['row_scale'],base[1]-lev['cell_scale']);ranks.append((gain,run['label'],category(i,run['label'])))
   positive=[x for x in ranks if x[0]>(0,0)];best=max([x[0] for x in positive],default=(0,0));leaders=[x for x in positive if x[0]==best];participants=[x for x in positive if x[0]<best]
   tied='；'.join(x[1]+'='+x[2] for x in leaders) if len(leaders)>1 else '不适用'
   factors='；'.join(x[2]+'：'+x[1]+f'（减{x[0][0]}行/{x[0][1]}格）' for x in participants) or '无'
   flags='已披露（D占位部分）' if any(x[2]=='D' for x in leaders+participants) else '无'
   conf='中' if i in [0,2,3,4,5,6,7,9,12,14,24,28,32,36,37,38,39,40] else '高'
   rules=RULES.get(i,'无。');um='不适用：主要原因不是U；完整实现诊断不当作U局部修复。'
   if maincat=='多因并列':maincat='多因并列（'+ '、'.join(sorted(set(x[2] for x in leaders)))+'）'
   item_tiers=[{'label':x[1], 'category':x[2], 'tier':item_tier(i,x[1],tier)} for x in leaders] or [{'label':'主要原因', 'category':maincat, 'tier':tier}]
   uncertainty='；'.join(x['label']+'='+T[x['tier']-1] for x in item_tiers) if maincat.startswith('多因') else T[tier-1]
  else:
   item_tiers=[]
   x=blind[i-43];maincat=x['main']+('（C、A）' if i==43 else '');short=x['reason'];reason=x['reason'];conf=x['confidence'];tier=2;uq=x['evidence'];uncertainty=x['uncertainty'];flags='无';qcount=1;q=[z for z in json.loads((REC/'020_calibration_queries.json').read_text()) if z['task']==r['task']]
   tied='url=C；key=A' if i==43 else '不适用';factors='U：latitude（单修减少13655格，行数不变）' if i==43 else '无：两个电话字段在盲标中作为同一预修复策略，另保留逐列测试。'
   um='latitude不满足独立主因的一半门槛，但满足U前三项和参与因素减少格子数要求。' if i==43 else '不适用：C；整项电话策略改动L0匹配。'
   rules=x['rule_issue']
   uq+=' 原句：'+('event59：The work includes staging raw-field mapping, timestamp parsing, event-key generation, filtering and nullification; latest-record models; daily aggregates and calendar spines; and mart entities.' if i==43 else 'event41：依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。')
   if i==43:rules+=' 不确定性盲标把event59的event-key generation泛述计为通用策略；018只对URL采用通用策略、对key计“看到了但没提”。保留盲标，不在对照后改写；此处通用“工作内容”是否足以算“策略说明”存在边界，018的更窄读法亦有依据。'
   else:rules+=' 盲标按同一电话预修复策略归一项，018按两列独立排序并将user列记参与因素；盲标保留，单列试验显示contact减10行，user减9行。'
  scales=[];percols=[];patchtext=[]
  for run in runs['runs']:
   if 'comparison' not in run:scales.append([run['label'],'错误',run.get('error','')]);continue
   c=run['comparison'];scales.append([run['label'],' / '.join(f"{v['level']}:{v['row_scale']}行/{v['cell_scale']}格" for v in c['levels']),c['first_match'] or '均未整表匹配'])
   percols.append({'label':run['label'],'per_level':[{k:v for k,v in lev.items() if k in ['level','column_mismatches','agent_only_key_rows','gold_only_key_rows','common_key_agent_excess_rows','common_key_gold_excess_rows']} for lev in c['levels']]})
   if run.get('edits'):
    if 'whole_implementation' in run['label'] or run['label'] in ['gold_sql_diagnostic','gold_positional_union_diagnostic','gold_rating_policy_diagnostic']:
     patchtext.append('- '+run['label']+'：替换指定完整实现块（诊断）；old/new完整字节见重跑JSON，私有SQL `'+run['sql_path']+'`。')
    else:
     for edit in run['edits']:
      original=d['agent_final_SQL'][0]['text'];line=original[:edit['offset']].count('\n')+1
      # Clock replacement can change byte offsets, but preserves line counts.
      baseline_path=Path(run['sql_path']).parent/'baseline.sql'
      if baseline_path.exists():line=baseline_path.read_text()[:edit['offset']].count('\n')+1
      patchtext.append('- '+run['label']+'（agent SQL 第'+str(line)+'行起）：\n```sql\n'+edit['old']+'\n```\n→\n```sql\n'+edit['new']+'\n```')
  change='；'.join(f"{z['label']}:{base[1]}→{z['comparison']['levels'][0]['cell_scale']}" for z in runs['runs'][1:] if 'comparison'in z)
  summary={k:'' for k in fields};summary.update({'题目':r['task'],'表':r['table'],'一句话描述':short,'主要原因类别':maincat,'参与因素':factors,'标记':flags,'把握':conf,'核实查询条数':str(qcount),'核实代价档':('需要查业务说明' if i in [2,24,36,37,38,39,40] else '一条查询' if qcount==1 else '多条查询' if qcount>1 else '判断不了'),'重跑是否满足 U 的第 4 个条件':um,'格子数口径规模变化':change,'与 014 相比是否变化':'不适用：020独立全量' if i<43 else '校准：独立盲标；与018对照见020校准记录','agent 是否意识到或提到了与本表差异相关的不确定性':uq,'并列项类别':tied,'不确定性四档':uncertainty})
  summaries.append(summary);decisions.append(dict(index=i,task=r['task'],table=r['table'],layer=r['layer'],purpose=r['purpose'],main=maincat,factors=factors,flags=flags,confidence=conf,tier=tier,main_item_tiers=item_tiers,uncertainty=uncertainty,reason=reason,rules=rules,verification_query_count=qcount))
  text=f"# {r['task']} / {r['table']}（{r['purpose']}）\n\n## 结论\n\n主要原因：**{maincat}**；把握：{conf}。{short}\n\n参与因素：{factors}。标记：{flags}。\n\n## 差异与归因依据\n\n{reason}\n\n层：{r['layer']}；比较库schema：{d['differences']['actual_schema']}；评测键：{', '.join(d['differences']['key_columns'])}。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。\n\n"
  text+='已核实的契约原文位置：\n\n'
  for block in d['contract_specification']['blocks']:text+='- `'+d['contract_specification']['source_path']+f":{block['start_line']}–{block['end_line']}`；完整逐字原文见材料包。\n"
  for label,k in [('agent','agent_final_SQL'),('gold（只作差异定位）','gold_SQL_仅供定位差异')]:
   for source in d[k]:text+=f"- {label} SQL：`{source['path']}:1–{source['end_line']}`；SHA-256 `{source['sha256']}`。\n"
  text+='\n具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：\n\n'+'\n\n'.join(patchtext)+'\n'
  text+='\n## agent可见证据与不确定性\n\n不确定性四档：**'+uncertainty+'**。\n\n'+uq+'\n\n'
  text+='完整事件扫描数：'+str(audit[i]['events_scanned'])+'；可见输出的机械命中及原始截断标记：\n\n'
  text+=mdtable(['event','cause','命中名','显式截断'],[[x['event'],x['cause'],','.join(x['names']),x['explicit_truncation']] for x in audit[i]['visible']])
  text+='\n此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。\n'
  text+='\n## 核实查询与诊断\n\n核实查询条数（含失败尝试）：'+str(qcount)+'；核实代价档：'+summary['核实代价档']+'。全部连接原件read_only=True，查询只用agent当时可见库。\n\n'
  for j,x in enumerate(q):text+=f"### 核实 {j+1}\n\n数据库：`{x.get('database','见查询记录')}`\n\n```sql\n{x['sql']}\n```\n\n"+('失败：'+x['error'] if x.get('error') else '结果：`'+json.dumps(x.get('result'),ensure_ascii=False,default=str)+'`')+'\n\n'
  if not q:text+='无数据核实查询；静态枚举问题需缺失的业务清单，来源搜索范围见归因说明。\n'
  text+='诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index='+str(i)+' 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。\n'
  text+='\n## 固定时间与重跑\n\n私有目录：`data/020_work/'+r['task']+'_'+r['table']+'/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`'+json.dumps(runs['clock_control'],ensure_ascii=False)+'`。\n\n'
  text+='留存结果同口径规模：'+str(runs['retained']['levels'][0]['row_scale'])+'行 / '+str(runs['retained']['levels'][0]['cell_scale'])+'格；重跑基线：'+str(base[0])+'行 / '+str(base[1])+'格。\n\n'
  text+=mdtable(['实验','L0–L3 行数/格子规模','整表首次匹配'],scales)
  text+='\n'+um+'\n\n完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：\n\n'
  text+=mdtable(['实验','L0每列不一致数'],[[z['label'],json.dumps({k:v for k,v in z['comparison']['levels'][0]['column_mismatches'].items() if v},ensure_ascii=False)] for z in runs['runs'] if 'comparison'in z])
  text+='\n本表全部重跑证据文件：'+ '；'.join('`'+v+'`' for v in runs['evidence_files'])+'。续做重跑私有副本在`data/020_resume_work/`。\n'
  text+='\n规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。\n'
  text+='\n## 规则问题\n\n'+rules+'\n\n## 证据路径\n\n'
  text+='- 精简材料包：`'+r['path']+'`。\n- 重跑：`records/020_reruns_'+r['task']+'_'+r['table']+'.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。\n- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。\n- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。\n- 输入快照：`records/020_input_before.json`。\n'
  (OUT/(r['stem']+'.md')).write_text(text)
 with (OUT/'020_summary.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(summaries)
 (REC/'020_decisions.json').write_text(json.dumps(decisions,ensure_ascii=False,indent=2)+'\n')
 def tiers_for_table(x):return sorted(set(z['tier'] for z in x['main_item_tiers']))
 def statistics(ds):
  return {'total':len(ds),'categories':dict(Counter(x['main'] for x in ds)),
          'uncertainty_table_combinations':dict(Counter('；'.join(T[t-1] for t in tiers_for_table(x)) for x in ds)),
          'uncertainty_table_coverage':{T[t-1]:sum(t in tiers_for_table(x) for x in ds) for t in range(1,5)},
          'uncertainty_main_items':dict(Counter(T[z['tier']-1] for x in ds for z in x['main_item_tiers']))}
 stats={'formal_tables':43,'calibration_tables':2,**statistics(decisions[:43]),'by_layer':{layer:statistics([x for x in decisions[:43] if x['layer']==layer]) for layer in ['staging','intermediate','marts']}}
 (REC/'020_statistics.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n');print(json.dumps(stats,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
