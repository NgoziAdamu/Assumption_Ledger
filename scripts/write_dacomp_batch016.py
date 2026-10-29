"""Write independent v1 annotations from recorded evidence; does not modify 004–015."""
from annotate_dacomp_batch016 import *
import csv
from write_dacomp_batch014 import A as OLD
A={n:dict(a) for n,a in OLD.items()}
def setcase(n,**kw):A.setdefault(n,{}).update(kw)
setcase(1,change='否：主要原因、参与因素不变。',primary=['allow_null_created'])
setcase(2,cat='多因并列（C、A）',confidence='高',factors='U：latitude硬约束（单改减少13655格）',flags='无',primary=['key_formula','url_rule'],u4='否：最大单项减少15000/43655格，未达一半',change='是：C改为C/A并列；latitude从O候选改为U参与因素。',
 desc='URL校验遗漏与未规定的hash公式各造成15000格差异，并列主因；另有13655个超界纬度。',
 reason='已核实：基线15000行、43655格。key_formula和url_rule单改均保持15000行，但各减少15000格；latitude_range单改减少13655格。按v1第5节改用格子后C/A并列。契约给出可执行URL正则，agent只trim，按字面执行归C；生成键公式未给出，归A。纬度超出±90违反列本身硬约束，按v1补充归U参与因素。URL的SQL全匹配与现实URL是否有效是不同问题，不评价这些地址在现实中有效与否。',
 p='P（参与因素）：非空latitude均在[-90,90]。014-V1反证13655行；轨迹只有schema，没有范围核实。latitude单改减少13655格但不满足U4的一半门槛，依据v1第4节对参与因素的放宽记U；不是U主因。',
 rules='v1第4节“参与因素不要求一半”与第3节U四条件存在字面冲突：本次将前者作为U参与因素的局部例外，U4仍明确写否。schema展示不等于曾展示越界值，故不使用“证据曾出现但被忽略”。')
setcase(3,change='否：仍O；本次以一致的重复键配对重算行/格子，数值不与014逐列下界混用。',primary=[],u4='否：放宽双侧rank比较属于O诊断，不是单侧修复',
 reason='已核实：CS上下游地址内容多重集合一致，契约明确同priority的顺序unspecified and non-deterministic；两侧窗口均只ORDER BY priority。014_relaxed_impl-003.json的双侧去rank诊断完全一致。016重跑基线6904行/6904格差异，仅rank列。重复键先抵消完全相同行，再对剩余元组固定排序一一配对；014的3192是独立逐列最少值差异，不是这次同一配对的格子数。归O，未把任选并列排序当作数据假设错误。',rules='契约已明确允许任意并列顺序，按v1归O。重复键残余行如何配对手册未规定；本次使用完整元组字典序固定配对，保持行/格子/每列计数内部一致，不声称全局最少格子数。')
setcase(4,factors='无：activity_rule_gold_day单独修复未减少含键规模',primary=['history_key_frozen'],change='是：主要A不变；移除未通过单独规模下降条件的O参与因素。',
 reason='已核实：双方raw一致。agent用hash(_fivetran_start,_fivetran_end)，gold用id与执行时刻拼接；契约未定义history_unique_key算法。正常当前时钟下替换公式仍为6000行/126000格；把该公式固定为gold原时刻后剩1行/1格。固定时刻只用于诊断未规定的key约定。activity_rule_gold_day单独改日期校验时键仍完全不相交，6000行/126000格不变，按v1不能列参与因素。',rules='金标准运行时刻只在history_key_frozen诊断表达式内固定，不能称为agent可见核实或纯粹可部署的U修复。沿用014相同输入结果。键遮蔽下的1行日期差异可记录，但不满足参与因素判据。')
setcase(5,cat='A',confidence='中',factors='无：三项数值类型对照在所选行数口径均不降',primary=['campaign_source'],flags='无',cost='多条查询',change='是：U改A；v1要求agent可见关系能明确决定来源，本次关系核实未满足。',
 desc='campaign来源列选择导致9985行键不同；契约和可见关联数据均未明确应选base还是直接campaign。',
 reason='已核实：014查询两列不同9985/10000，campaign_source单改L2整表匹配。新增016-V1显示两个候选均能关联campaign_history的id（各10000行）；016-V2经base_ad_group关联ad_group_history，10000对中直接campaign符合父表11对、base符合14对。该数据不能给出单一明确来源。v1禁止用gold选择证明映射正确，因此由U改A。L0基线19985行/239672格，改来源后10000行/21395格，L2为0；DECIMAL/DOUBLE对照只降低少量格子，行数不变，不在本表所选行数口径列参与因素。',
 p='不能把“两列不相等”直接升级为“选base这一列错误”的P；前者已反证等价，后者仍缺契约或可见数据的唯一指向。U4数值条件成立并不足以判U。',rules='来源映射按v1第3节新增口径处理。该表行数已能选出主因，参与因素也沿用行数口径；三项精度差异可诊断但不以换格子口径另行纳入。')
setcase(6,cat='多因并列（I、D、A）',confidence='中',factors='无：20处均并列主因',primary=[r for r in ['spend','video_views','video_view_rate','upvotes','downvotes','comments','shares','saves','post_visits','profile_visits','community_joins','conversions','conversion_value','cost_per_video_view','cost_per_conversion','total_engagements','engagement_rate','click_through_rate','cost_per_click','cost_per_thousand_impressions']],change='是：X改为I/D/A多因并列；v1允许代码意图、候选列降级和并列归因。',
 desc='20个指标各造成1200格差异：spend候选被覆盖、四个可映射指标直接填NULL，其余为未规定指标口径。',
 reason='已核实：1200行/24000格，20个单列干预各减少1200格、行数均不变，故20处并列。spend在event19同一映射中先含正确spend候选、后被重复键覆盖掉，归I。video_views/upvotes/downvotes/comments原始表分别有video_started/comment_upvotes/comment_downvotes/viewer_comments，但生成器没有逐字段数据判断就填NULL，按v1归D。video_view_rate、shares、saves、post_visits、profile_visits、community_joins、conversions、conversion_value、cost_per_video_view、cost_per_conversion、total_engagements、engagement_rate及ctr/cpc/ecpm输出共15项，缺直接列、统一汇总/公式或0与NULL约定，归A；这不声称这些值不存在任何可用业务定义。event95明确披露typed NULL，D加“已披露”。',
 p='不将20个不同错误合并成一次U修复。spend有清楚的代码正确意图证据，优先I；D候选列存在的证据来自raw schema和014-V1，不从gold推断。其余指标只有gold实现不能确定业务口径。',rules='v1的D候选列规则用于可直接辨认的四个指标；需定义聚合业务口径的派生指标按A。此边界仍可能有D/A两种读法，保留中把握，逐项而非按占位列总数挑主因。')
setcase(7,primary=['subscriber_source'],flags='无',u4='是（subscriber_source行1400→568，减少59.4%；来源歧义仍归A）',change='是：主要A不变；修正014对U4数值条件的否定，并撤下缺唯一语义依据的未核实假设标记。',
 p='subscriber_id和marketing duration均缺source mapping。字段值不同不足以证明存在可判真假的业务可替代命题；按v1不据gold选择归U。marketing单改不减少含键规模，不能列参与因素。',rules='014对U4曾写否，但subscriber_source单改实际1400→568，已满足至少一半；这里修正计算判定，不把满足数值条件等同U。marketing_source仍被错误键遮蔽；有差异不等于通过独立参与因素条件。')
setcase(8,primary=['project_source'],factors='无：numeric_order与主因同源；section_tie_order单改反而增大差异',change='是：主要U不变；新增并列section顺序单改无改善，移除014的O参与因素。',
 reason='已核实：agent可见数据有44条project_task找不到project。CS基线187行/237格；单换SELECT p.project_id为pt.project_id，剩71行/71格，行数减少62.0%。同一来源选择既丢失缺项目的id又带入VARCHAR排序；数字排序独立对照114行/159格，是同一机制的部分修复，不重复列参与因素。旧014双侧拆分projects_sections诊断79个不同字符串条目多重集合一致；本次单增section_name作为并列排序键却变596行/661格，未减少规模，不列O参与因素。',rules='“项目可能缺失”是数据性质而非指定SELECT表达式，v1 C/U边界支持U；轨迹契约提醒被忽略。O诊断可说明残差来源，但v1参与因素仍要求单改改善，不能以双侧放宽比较替代该要求。')
setcase(9,primary=['country_value_only'],factors='U：lookup数值码非唯一，独立去重使15200→12800行',change='是：主要A不变；lookup从X参与因素改为U参与因素。',
 reason='已核实：raw6400行、lookup250行但数值码246个，4个码各映射两种alpha-2，JOIN多出2400行。country只声明VARCHAR，agent翻成alpha-2而gold保留数值码，主因A。只改输出country表达式保留JOIN，15200→2400行；只去重lookup，15200→12800行，按v1参与因素不要求一半，记U。组合移除翻译表达式及专用JOIN为0，仅用作额外对照，不拿它证明lookup这个P的U4。',
 p='P（参与因素）：lookup.country_code_numeric唯一。014-V2及重复V3反证；轨迹未查重复。unique_lookup单独减少2400行，但不达一半，U4对这个P写否；按第4节参与因素例外记U。',u4='主因单改是（country_value_only 15200→2400）；lookup这个U参与因素否（15200→12800）',rules='U参与因素采用第4节“不要求一半”的例外解释；U4保留逐命题结论。组合remove_country_translation包含两段替换，不替代两项独立对照。')
setcase(10,cat='不可评估',primary=[],change='是：O改为不可评估，按v1和2026-10-29用户补充。',reason='已核实：依赖raw.form_data的agent留存与初始库一致，而gold不同。014完整行多重集合诊断与015三方核对相互印证：agent有1150个FORM_ ID；gold原表1150行、1142个数值ID，输出去重1142行。双方raw原始行不相交，gold SQL在agent输入上也不能重现gold输出。符合补充规则第一种情况，退出类别归因；旧去重/日期重跑仅保留诊断。',rules='2026-10-29用户确认补充规则：agent=初始≠gold，先诊断再不可评估；gold=初始≠agent，照常标注并找轨迹改动。此表属于前者；不把gold中的重复guid拿来反证agent的唯一性。')
setcase(11,cat='A',confidence='中',factors='A：original_estimate优先级；A：remaining_estimate优先级',flags='无',primary=['time_spent_priority'],cost='需要查业务说明',u4='否：最大单改8000/23998格，不达一半',change='不适用：第二批首次标注',desc='三个估算/耗时字段优先使用带下划线列，gold优先同名列，契约未规定优先级。',reason='已核实：8000行、23998格。original/remaining/time_spent两种源值分别7999/7999/8000行不等；分别反转COALESCE后减少7999/7999/8000格。行数均8000，按格子主因为time_spent来源优先级A，另外两项A参与因素。契约只给输出字段和类型，数据不存在足以确定哪组代表业务正式估算的证据。',seen='event1完整契约；event9查结构；event11生成COALESCE(_field,field)。event29/31/37修日期，event45检查键，不是估算来源优先级核实。没有找到业务口径或两组耗时来源可信度比较。',p='两组值不等只能否定等价，不能决定应优先哪列；故A而非U。',rules='同类别的三个错误仍分别干预，不因都属于A便合并。time_spent比其余多减少1格，按v1数字规则选主因，不另设实质差异阈值。')
setcase(12,cat='多因并列（O）',confidence='高',factors='无',flags='无',primary=['first_name_trim_policy','last_name_trim_policy'],cost='一条查询',u4='是（每项6→3行；这不是U）',change='不适用：第二批首次标注',desc='agent按契约排除首尾带空白的姓名，gold只trim后保留；first/last两项各缺3行并列。',reason='已核实：raw6000行且id无重复；first_name和last_name各3行不等于TRIM。契约可执行校验name=TRIM(name)、失败删行，agent照做。两边输出5984与5990行，差6行/36格；分别放宽一项空白校验后3行/18格，去重控制无效。gold保留并修整这些行与字面排除规则不一致，两个O原因并列。',seen='event1含契约；event23落实first/last name字面校验；event43修复NULL条件；event45运行校验。没有把可能的“先trim再校验”推测当契约本意。',p='无U主命题。来源数据是否有空白不是导致错误的未经核实假设：agent已按规则处理。',rules='按v1可执行写法的字面效果，不按“清理后应该保留”解释。两个主因都属O，CSV写多因并列（O），正文保留两个独立原因，未人为拆成不同类别。')
setcase(13,cat='C',confidence='高',factors='无：CLV分母对照未改善',flags='无',primary=['percentile_score'],cost='需要查业务说明',u4='是（percentile_score单改L0整表一致；非U）',change='不适用：第二批首次标注',desc='把契约规定的连续分位阈值评分写成NTILE(5)，造成2行4格差异。',reason='已核实：CS固定2025-10-14共同日期；契约要求按revenue第20/40/60/80百分位阈值分配分数。agent直接ntile(5)，等量桶与数值阈值不等价。单替换评分表达式为quantile_cont阈值后L0整表匹配。另改CLV分母为gold方式不改变2行/4格，不列参与因素。',seen='event1给出完整业务规则；event19生成ntile(5)表达式。未发现正确分位阈值意图的相反代码证据，直接按契约执行遗漏归C，不推断I。',p='规则已经直接规定计算方式，不需把数据分布构造为U命题；无需额外核实查询。',rules='固定日期是所有基线/干预共同的运行条件，不能把这个共同控制当成与局部修改捆绑的第二处原因。')
setcase(14,cat='A',confidence='中',factors='无',flags='无',primary=['gold_timestamp_parser'],cost='需要查业务说明',u4='是（改解析策略后L0整表一致；非U）',change='不适用：第二批首次标注',desc='agent按显式时区格式成功解析12000个created_at，gold用TRY_CAST得到全NULL，契约未规定解析策略。',reason='已核实：两边raw一致；016-V1中creation_date直接TRY_CAST成功0行，显式STRPTIME成功12000行。契约只有created_at TIMESTAMP，未指定源表达式、失败策略或非空。单把agent解析改为gold TRY_CAST即L0匹配，但这不证明agent未核实或数据处理有误。按未规定的解析/保留规则归A，中把握。',seen='event14显示survey_version.creation_date为VARCHAR。event57→58在raw.survey_response.recorded_date上实际测试带时区格式；event59把staging TRY_CAST替成STRPTIME。这是相邻源字段的可见测试，不夸大成已经查询本列全体；本次V1确认本列可完整解析。',p='“格式可以解析本列”在本次核实中成立，不满足U条件2；不能为了匹配gold的NULL构造错误P。',rules='可读为O（gold解析丢值），也可读为A（未指定解析规则）。选择A：此契约允许NULL且没有与gold直接矛盾的表达式，差异确实来自双方处理方式；不扩张O到所有更保守或更宽松的解析。')
setcase(15,cat='A',confidence='中',factors='无：raw类型重建不是本列差异来源',flags='无',primary=['tax_code_null'],cost='需要查业务说明',u4='是（tax_code_null单改L0整表一致；非U）',change='不适用：第二批首次标注',desc='tax_code_id取sales_tax_code_id而gold填NULL；agent另在导入raw时通过pandas改变了全NULL列类型。',reason='已核实：raw.item_data有sales_tax_code_id和purchase_tax_code_id，各2000个非空且全部不等，无统一tax_code_id列。契约未指明选销售税还是采购税、是否留空。只改tax_code_id为NULL即可2000行/2000格→0，归A。015三方结果gold=初始、agent仅parent_item_id类型由VARCHAR变INTEGER。event44报告重复ATTACH句柄冲突；event45为绕开它改成fetchdf/register后CREATE OR REPLACE raw，导致类型重新推断；本次在私有副本复现全NULL parent_item_id导入变INTEGER。原行值无差异的015记录与此一致。继续正常标注，不能列不可评估，也不把这个未参与评分的类型改变当本节点主因。',seen='event1完整契约；event17/21/25生成和修订字段映射；event44→45解释并实施raw导入路径修改。该改动是为修复初始化错误；未找到业务文档解释税码来源。',p='两个税码不相等不能定下目标税码语义；NULL替换能匹配gold不是U证据。',rules='2026-10-29用户确认补充：gold=初始≠agent属于运行留存侧改动，照常标注。此处是schema类型漂移而非删除/伪造原始行；明确区分原始初始库未改、留存库raw重建。')
setcase(16,cat='多因并列（C、O）',confidence='中',factors='C：角色关系聚合（106格）；C：任期平均的连接权重（5格）',flags='无',primary=['annual_zero','management_zero','maturity_labels','size_labels'],cost='需要查业务说明',u4='否：最大单项减少117/696格，不达一半',change='不适用：第二批首次标注',desc='两个比率漏补0、两个枚举标签与gold约定冲突各117格并列；角色关系和任期连接另有贡献。',reason='已核实：CS用gold上游，所有重跑固定gold实际analysis_timestamp。基线117行/696格；annual_zero、management_zero、maturity_labels、size_labels各单独减少117格，行数均不变。契约明确分母0时比率0，agent NULLIF后未补0，两个C；契约明确New/Young/Mature/Legacy及Empty/Micro等短标签，agent遵守而gold输出扩展长标签，两个O。roles_relationship按契约worker/source/role/org关系重建，减少106格；tenure_join_weight补相同关系的行重复权重，减少5格，均C参与因素。health两项阈值控制及risk/fill补0在当前整体比较未减少规模，不列参与因素。raw.email在015中gold/初始7284行、agent2448行，但event65→66末次成功运行仍打印raw和staging各7284行；余下事件只有只读查询和报告写入，未找到2448的改动步骤与原因。按用户规则照常评估；这次CS也隔离了agent上游raw差异。',seen='event1完整给出组织关系、比率默认0和标签；event25/31/33/35/37/51逐步生成marts，event55修列名；event65→66最终执行，event69/71只读检查，event73之后写报告。不能用当前留存库反推轨迹中必然存在某个删除动作。',p='比率补0及连接方式有直接契约规定，归C；枚举标签是契约/gold冲突，归O。raw变化的操作来源无法判定，但不影响本节点CS对照。',rules='2026-10-29用户补充要求gold=初始≠agent正常标注，本表遵守；“一定是agent在轨迹中改了原始数据”在现有证据中尚未找到，明确保留缺口，不虚构原因。标签扩展是字面枚举规则冲突。health残差可能需要多处联动才消失，按独立干预规则不把无改善项硬列参与因素。')
setcase(17,cat='O',confidence='高',factors='无',flags='无',primary=['preserve_duplicate'],cost='一条查询',u4='是（preserve_duplicate单改L0整表一致；非U）',change='不适用：第二批首次标注',desc='agent按复合主键去掉一个重复candidate-tag行，gold保留重复，造成1行2格差异。',reason='已核实：raw中(candidate_id=4420,tag_id=114)出现2次，其余不重复；契约primary_key=[candidate_id,tag_id]。agent ROW_NUMBER去重得到1999行，gold保留2000行。仅取消_row_num=1即L0整表一致。主键声明与gold重复行冲突，归O，不因保留重复能匹配gold反判agent未遵约。',seen='event1给出复合主键；event17生成窗口去重，后续运行成功。无需假定agent看过该重复值才可执行主键约束。',p='无错误的唯一性假设：agent正是显式处理重复，而非依赖无重复。',rules='primary_key按通常完整性约束理解，而非仅描述评分对齐键；若任务只想表达grain而不要求唯一，则O/A边界需另定义。本次按契约字面主键归O。')
setcase(18,cat='多因并列（I）',confidence='中',factors='无：删除标记过滤对照未改善',flags='无',primary=['opportunity_source','product_source'],cost='一条查询',u4='是（每项单改6000→3000格；类别依据为I）',change='不适用：第二批首次标注',desc='通用id映射把opportunity_id和product_2_id都写成本行id，后续修FK时漏掉此表，两项并列。',reason='已核实：3000行/6000格，分别换回raw.opportunity_id和raw.product_2_id后均3000行/3000格。event19的全局mapping将实体主键名均映射id，连带误用于外键；event57代码注释明确“canonical foreign keys should remain FK columns, not the row\'s own id”，实际只修其他五表，遗漏本表。因此存在正确意图与代码未实现的证据，两个I并列。016-V1证实opportunity源列能关联432条而id为0，且is_deleted为true的行0，补过滤无改善。',seen='event19通用生成器；event57明确外键映射原则和修复列表；本表不在列表。schema存在两外键不足以单独证明意图，使用的是event57的明确注释与实际修复行为。',p='有可验证外键关系，但明确正确意图证据使I比U更贴近机制；不把原始opportunity只有部分引用匹配解释为全表外键完整性成立。',rules='正确想法来自后期全局FK修复说明，未逐字点名本表；本次把通用原则应用于同一生成器的漏改，归I，中把握。若只接受逐表意图，可以读为U/A，故明确证据范围。')
setcase(19,cat='A',confidence='中',factors='A：event连接的NULL相等策略（1600→1295行）',flags='无',primary=['summary_null_join'],cost='需要查业务说明',u4='是（summary_null_join单改1600→346行；非U）',change='不适用：第二批首次标注',desc='summary/event两个连接用NULL安全等值，gold用普通等值；summary连接是主要差异。',reason='已核实：CS上游gold，双方1548180行，基线1600行/8855格；只把summary连接的IS NOT DISTINCT FROM改为=后346行/892格，只改event连接后1295行/7538格。契约列出连接键和指标空值补0，但未规定NULL键彼此是否匹配，也没提供可执行等号表达式。此选择不能由NULL存在本身决定，主要A与A参与因素。015显示相关gold/agent raw一致，初始库schema/表示不同，不属于agent=初始≠gold的不可评估情况。',seen='event1包含连接业务说明；event19生成两个NULL安全连接，代码明确选择了NULL匹配策略，不是因为不知道表里可能有NULL才误用普通等号。不存在足以唯一规定NULL业务含义的可见文档。',p='“NULL应互相匹配”是缺业务定义的决策，不是查询NULL计数即可证伪的数据性质命题；不用gold等号作为U真值。',rules='普通“on这些键”是否隐含SQL等号可有C/A两读；因没有直接可执行表达式且NULL键业务含义未说明，选A。重复键格子采用同一残余元组固定配对，8855不是旧材料逐列最少差异下界之和；行数主因选择不受这个配对约定影响。')
setcase(20,cat='O',confidence='中',factors='无：part_type单改行数不降；created_at未参与评分',flags='无',primary=['conversation_direct'],cost='需要查业务说明',u4='否（所选行数口径7524→7476，未达一半）',change='不适用：第二批首次标注',desc='agent从复合id提取BIGINT会话号而gold保留原列时间文本，另补subject到part_type；gold类型与契约冲突。',reason='已核实：契约conversation_id BIGINT，raw同名列全是不可转BIGINT的时间文本，gold直接保留成VARCHAR；agent从id前缀构造BIGINT。conversation_direct单改使7524行/15000格变7476行/7476格；part_type_direct单改仍7524行、7524格。按行数先选conversation_id主因；gold输出违反类型声明，归O，中把握。part_type的NULL用subject填充属于未写明的恢复规则，可读为A差异，但本表已由行数选主因，单改行数不降不列参与因素。created_at虽违背明确source_expression，未在比较列/键中，控制重跑也无影响。015的gold/agent raw一致，初始不同，不是不可评估。',seen='event23查询part_type/type等（输出有截断，不据未展示部分推断）；event31→32完整展示一行错位字段；event33/35尝试从其他列恢复会话号和时间，event37改为id前缀及时间回退。agent已经看过错位值，不说它完全没核实。',p='本次核实raw.conversation_id无一可转BIGINT；这说明原列不满足契约目标类型，而不是证明id前缀的恢复一定对。缺少完整对应业务说明，O仅依据gold直接类型矛盾。',rules='若允许主因用行数、参与因素随时换格子，则part_type可列A参与因素；本次同一表使用同一选定口径，保留为潜在差异而不列参与因素，避免口径切换。O不证明agent所有恢复策略正确。')

COMMON_RULE='2026-10-29用户确认的第3节补充：仅当本表依赖raw满足agent留存=初始、gold不同，且诊断确认影响可评估性时标“不可评估”；gold=初始、agent不同则照常标注，查轨迹改动。不能把两类混为一谈。若gold与agent一致但二者不同于初始（019/020），当前本节点仍可比较；初始差异另记。'
METHOD='L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。'
def results(c):
 ls=['|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|','|---|---:|---:|---:|---:|---|---:|---:|---:|---|']
 for x in c['levels']:
  ls.append(f"|{x['level']}|{x['agent_rows']}|{x['gold_rows']}|{x['agent_only_key_rows']}|{x['gold_only_key_rows']}|{x.get('common_key_agent_excess_rows',0)}/{x.get('common_key_gold_excess_rows',0)}|{x['common_key_different_rows_or_min_pairs']}|{x['row_scale']}|{x['cell_scale']}|{x['whole_match']}|")
 ls += ['',f"整表首次匹配档位：**{c.get('first_match') or 'L0–L3均不匹配'}**。",'','|共同键比较列|L0不同格|L1|L2|L3|','|---|---:|---:|---:|---:|']
 for col in c['levels'][0]['column_mismatches']:
  ls.append('|'+col+'|'+'|'.join(str(x['column_mismatches'].get(col,0)) for x in c['levels'])+'|')
 return '\n'.join(ls)
def raw_status(n,pkg):
 x=json.loads((REC/f'015_raw_impl-{n:03}.json').read_text());raws=set()
 edges=[json.loads(l) for l in (REC/'015_lineage_edges.jsonl').read_text().splitlines() if l]
 target=pkg['differences']['actual_schema']+'.'+pkg['differences']['table'];todo=[target];seen=set()
 while todo:
  t=todo.pop()
  if t in seen:continue
  seen.add(t)
  if t.startswith('raw.'):raws.add(t)
  for e in edges:
   # mart/marts is a naming alias, use the model name to align.
   if e['task']==f'impl-{n:03}' and e['target'].split('.')[-1]==t.split('.')[-1]:todo.append(e['source'])
 sql=Path(pkg['agent_final_SQL'][0]['path']).read_text()
 raws.update(re.findall(r'\braw\.[\w]+',sql))
 rs=[r for r in x['comparisons'] if r['raw_table'] in raws]
 lines=['|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|','|---|---|---|---|---|---|']
 for r in rs:lines.append('|'+r['raw_table']+'|'+r['comparison']+'|'+str(r['ordered_columns_and_types_equal'])+'|'+str(r['row_counts_equal'])+'|'+str(r['sorted_content_hash_equal'])+'|'+','.join(r['difference_reasons'])+'|')
 return '\n'.join(lines),{'transitive_raw_dependencies':sorted(raws),'comparisons':[{k:v for k,v in r.items() if k not in ('gold','agent','initial')} for r in rs]}
def main():
 dest=REC/'016_annotations';dest.mkdir(exist_ok=True);rows=[];raw_audit={}
 for n in range(1,21):
  a=A[n];task=f'impl-{n:03}';pkg=package(n);b=pkg['differences'];r=json.loads((REC/f'016_reruns_{task}.json').read_text());base=r['runs'][0]['comparison']['levels'][0]
  qs=[]
  for prefix in ([14,16] if n<=10 else [16]):
   p=REC/f'{prefix:03}_queries_{task}.json'
   if p.exists():
    for q in json.loads(p.read_text()):qs.append({**q,'evidence_file':str(p.relative_to(ROOT)),'id':f'{prefix:03}-{q["id"]}'})
  count=sum(q['kind']=='核实查询' for q in qs);assert count<=5
  slim=next((REC/'013_packages').glob(f'013_{task}_*.md'));block=pkg['contract_specification']['blocks'][0]
  trace=f'{14 if n<=10 else 16:03}_trace_{task}.json';rawtable,rawmeta=raw_status(n,pkg);raw_audit[task]=rawmeta
  lines=[f'# {task} / {b["table"]}','','## 1. 错在哪里','',a['desc'],'',a['reason'],'','## 2. 依据','',f'- 起点：[013精简材料包](../013_packages/{slim.name})；013官方状态不改。',f'- 契约：`{pkg["contract_specification"]["source_path"]}` 第{block["start_line"]}–{block["end_line"]}行。',f'- [原始轨迹转录](../{trace})：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。',f'- [本轮重跑结果](../016_reruns_{task}.json)；[015三方raw核对](../015_raw_{task}.json)。', '- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。','', '### 契约原文','', '```yaml',block['original_text'].rstrip(),'```','','### SQL行号与原文','']
  for label,key in [('agent','agent_final_SQL'),('gold（仅用于诊断）','gold_SQL_仅供定位差异')]:
   p=Path(pkg[key][0]['path']);sql=p.read_text();lines += [f'{label}：`{p}`','```sql']+[f'{i:4}: {s}' for i,s in enumerate(sql.splitlines(),1)]+['```','']
  lines += ['### 本表原始数据可评估性','', '按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。', '',rawtable,'']
  if n in [10,15,16,19,20]:lines+=['补充诊断与原始事件见[016_raw_diagnostics.json](../016_raw_diagnostics.json)。','']
  lines += ['## 3. agent看过什么','',a['seen'],'','区分event实际展示的契约/数据与磁盘上存在的资料；截断输出中未出现的部分不算agent已经看到。核实查询是标注者新增查询，不冒充agent执行过。','','## 4. 查询与重跑','',f'核实查询合计 **{count}条**（含014复用；本轮新增{sum(q["kind"]=="核实查询" and q["id"].startswith("016-") for q in qs)}条）；核实代价档：**{a["cost"]}**。诊断不计入5条上限。查询失败与重复执行如实保留。','']
  for q in qs:
   lines += [f'### {q["id"]} / {q["kind"]}', '',f'来源：`{q["evidence_file"]}`；数据库：`{q.get("database",q.get("databases","见下列记录"))}`。','','```sql',q['sql'],'```','结果原文：','```json',json.dumps({k:v for k,v in q.items() if k not in ['id','kind','sql','database','databases','evidence_file']},ensure_ascii=False,indent=2,default=str),'```','']
  if not qs:lines+=['无新增数据核实查询；本表依据契约/SQL和只读诊断或重跑判断。','']
  lines+=['### 比较口径','',METHOD,'',f'键：`{b["key_columns"]}`；比较列（与键取并集）：`{b["comparison_columns"]}`。','', '所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。', '',f'复用说明：{r.get("reused_from","本次重新执行；原013留存输出另列")}', '', '共同时间控制：`'+json.dumps(r.get('clock_control',[]),ensure_ascii=False)+'`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。','', '### 单项改善概览','', '|单项|L0行：前→后|L0格：前→后|首次整表匹配|','|---|---|---|---|']
  scales=[]
  for trial in r['runs'][1:]:
   c=trial['comparison'];x=c['levels'][0];lines.append(f'|{trial["label"]}|{base["row_scale"]}→{x["row_scale"]}|{base["cell_scale"]}→{x["cell_scale"]}|{c.get("first_match") or "无"}|');scales.append(f'{trial["label"]}:{base["cell_scale"]}→{x["cell_scale"]}')
  lines+=['','### 留存输出基线','',results(r['retained']),'']
  for trial in r['runs']:
   lines += [f'### 重跑 {trial["label"]}', '',f'SQL：`{trial["sql_path"]}`；SHA-256：`{trial["sql_sha256"]}`。','']
   for ed in trial['edits']:lines += [f'唯一原文位置offset={ed["offset"]}，替换前：','```sql',ed['old'],'```','替换后：','```sql',ed['new'],'```','']
   if not trial['edits']:lines+=['不增加因果修改的基线。','']
   lines += [results(trial['comparison']),'']
  if 'gold_sql_same_input_diagnostic' in r:
   diag=r['gold_sql_same_input_diagnostic'];lines+=['### 复用gold SQL同输入诊断','', '用于诊断，不是单点修复证据。','',results(diag) if 'levels' in diag else json.dumps(diag,ensure_ascii=False),'']
  if n in [3,8]:lines += [f'排序内容诊断复用：[014_relaxed_impl-{n:03}.json](../014_relaxed_impl-{n:03}.json)，查询原文及双侧放宽结果在该记录；不把放宽评测叫作单侧修复。','']
  lines += ['## 5. 类别、把握及与014对比','',f'- 主要原因：**{a["cat"]}**。',f'- 主因对应单项：{", ".join(a["primary"]) or "不适用（评测条件诊断）"}。',f'- 参与因素：{a["factors"]}。',f'- 标记：{a["flags"]}。',f'- 把握：**{a["confidence"]}**。',f'- 重跑是否满足U第4条件：{a["u4"]}。','',a['p'],'',f'与014相比：**{a["change"]}**','', '## 规则问题','',a['rules'],'',COMMON_RULE,'', '共同执行例外：最初指纹快照因外部v0附件已不在原桌面路径而失败；成功的016快照晚于首批私有重跑。已逐文件与015任务前的大小、mtime、SHA-256比较，覆盖原始库的历史指纹无变化；不把晚快照伪称执行前快照。仓库v0与004–015记录保留。','']
  (dest/f'016_{task}_{b["table"]}.md').write_text('\n'.join(lines))
  rows.append(dict(zip(['题目','表','一句话描述','主要原因类别','参与因素','标记','把握','核实查询条数','核实代价档','重跑是否满足 U 的第 4 个条件','格子数口径规模变化','与 014 相比是否变化'],[task,b['table'],a['desc'],a['cat'],a['factors'],a['flags'],a['confidence'],count,a['cost'],a['u4'],'；'.join(scales) or f'基线{base["cell_scale"]}；无单点修复',a['change']])))
 with (dest/'016_summary.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
 save(REC/'016_decisions.json',A);save(REC/'016_dependency_raw_audit.json',raw_audit)
 print('Wrote',len(rows),'annotations',Counter(a['cat'] for a in A.values()))
if __name__=='__main__':main()
