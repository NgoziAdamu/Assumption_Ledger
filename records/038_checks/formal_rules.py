"""Human-reviewed v3.2 decisions. No mapping from 020 categories is used."""
Q='Quiet Downgrade';U='Unstated Choice';I='Intent Misreading';C='代码写错';O='其他'
RULES={i:[] for i in range(43)}
def add(i,label,cat,reason,grade=2,source='old',**kw):
 RULES[i].append(dict(label=label,base_category=cat,reason=reason,grade=grade,source=source,**kw))
# Same-category fallback omissions: section 7 permits category-level attribution,
# with medium confidence, without pretending a whole-gold replacement is a single edit.
fallback={
0:'要求按platform/account/date聚合，NULL分段字段、SUM/COALESCE及聚合后KPI；实际仅首源逐行投影，没有GROUP BY。不是对某一算法的局部误读，而是以campaign记录替代account报告。026所指event27已核实，不沿用旧C。',
3:'要求合并Google/Amazon/Facebook触点，建立customer_identifier，按客户汇总、分类、归因、留存占位及12个月筛选；34个输出全NULL并逐行读取Google，未建立客户模型。缺口属于同一个结构占位替代行为。',
4:'要求三平台合并、月度地区/渠道聚合、增长和竞争指标、机会分类及6个月过滤；30个输出全NULL并逐行读取Google。不是字段解释分歧。',
5:'要求platform/country/campaign/月粒度聚合、平台地理映射、月度KPI/活动天数及非零筛选；仅投影campaign的少量列，其他NULL，没有月度聚合。',
6:'要求region/campaign/月粒度聚合、country_list、月度KPI、区域份额及筛选；仅投影首源，其他NULL，无区域月度计算。',
7:'要求四平台日粒度汇总、日历特征、移动窗口/趋势/异常/预测和12个月筛选；57个字段全NULL并逐行读取Google。整段gold诊断仍有149行875格残差，不据此把占位解释成唯一可精确修复的单点。',
9:'要求月度战略指标连接客户/地理/平台KPI并汇总、分类与建议；42个字段全NULL逐行读取统一指标源，不是执行仪表板。',
12:'要求平台月度汇总、滚动趋势、预测/风险/建议和6个月筛选；31个字段全NULL逐行读取统一指标源，不是预测分析。'}
for i,reason in fallback.items():
 add(i,'whole_implementation_diagnostic',Q,reason,1 if i in [3,4,7,9,12] else 2,diagnostic=True,confidence='中',name='首源投影/整表NULL替代模型（同类缺口组）')
add(2,'whole_implementation_diagnostic',Q,'契约要求跨五大地区的静态国家清单，但没有给出完整枚举输入。agent自造US单行作为占位交付，不满足跨区域清单；依第5节“要求的输入不存在而造替代品”归降级，不把gold的具体45国当作已给要求。',1,diagnostic=True,confidence='中',name='用自造US单行替代跨地区国家映射')
add(1,'missing_apple_branch',Q,'契约明确Facebook+Apple UNION ALL；fallback仅取Facebook，完全漏掉Apple输入。')
for f in ['clicks','cost','interactions','conversions','conversions_value','view_through_conversions','cost_per_conversion','return_on_ad_spend']:
 add(1,f,Q,f'{f}整列NULL；契约规定的源映射/默认0/公式均可用。此处是整列占位，按第3节先判降级。')
add(8,'google_roas_rounding',I,'契约明确Google ROAS为revenue_7d/cost，只对CTR/CPC等列规定舍入；agent在ROAS计算链中额外ROUND(...,4)，改变数值。不是只改展示，也不是数据格式事实。',4)
add(8,'ctr_platform_fallthrough',I,'契约为每个已命名平台规定HIGH/MEDIUM/else LOW，others才用1.0/0.5；SQL把低于本平台阈值的Google/Facebook也落入others分支，6行错分。两处WHEN属于同一个兜底条件点。',4)
for i in [10,11]:
 for f in ['spend','attributed_sales_14_day','attributed_sales_30_day','attributed_conversions_14_day','attributed_conversions_30_day']:
  add(i,f,Q,f'契约已给{f}的total_*透传来源，原始上游有对应列；fallback未正确使用映射而整列NULL。未见代码先明确写对该total_*映射后被覆盖的证据，不能套用staging的代码错误。')
 add(i,'placeholder_filter',I,'契约明确排除platform=placeholder，SQL无该WHERE；新单改无改善，因此只是未落实的前提，不是本次判错原因。',4,source='new')
for f in ['avg_ctr_percent','avg_cpc','avg_cpm','avg_cpa','avg_roas','mart_created_at']:
 add(11,f,Q,f'{f}整列NULL，契约给定monthly_regional_*映射或执行时间来源；属于可提供而未提供。avg_cpm单改格子差异反增，不能据此记参与。')
# Amazon: no-source metrics and available-input calculations are distinguished per column.
add(13,'invalid_id_contract_delete',I,'ad_group_id的正则与delete_row动作均在契约写明；agent未过滤非法ID。采用契约删除实验，拒绝把gold置NULL诊断当作契约修复。',4)
for i in [13,14]:
 add(i,'campaign_bidding_strategy',U,'契约只要求VARCHAR，未规定合法枚举、清理或同义词策略；gold白名单/大写/置空与agent透传不同，不能把gold枚举当作约定。',4)
 for f in ['click_through_rate','cost_per_click']+(['return_on_ad_spend'] if i==14 else []):
  add(i,f,Q,f'{f}整列NULL；raw已有clicks/impressions/cost及（campaign ROAS）sales_30_d候选，可计算。')
for i in [15,16,17]:
 for f in ['attributed_conversions_14_d','attributed_conversions_30_d','attributed_sales_14_d','attributed_sales_30_d']+(['attributed_units_ordered_14_d','attributed_units_ordered_30_d'] if i==16 else [])+(['match_type'] if i==17 else [])+['return_on_ad_spend']:
  add(i,f,U,f'{f}没有相应raw候选（ROAS所需归因收入也不存在）；契约未规定无源时补0还是NULL。对schema逐列核查后归Choice，不因整列NULL一律归降级。')
 for f in ['click_through_rate','cost_per_click']:
  add(i,f,Q,f'{f}虽与无源归因列同表，但raw有clicks/impressions/cost，NULL放弃可算指标，独立归降级。')
for f in ['avg_cpa_currency','avg_cpt_currency']:
 add(18,f,I,f'契约规定{f}须trim/upper后在USD/EUR/GBP/JPY/AUD/CAD中且长度3，否则nullify。038核实1500行均不在允许集，差异是非法值清理，不仅大小写呈现；按契约算法归Intent。',4)
add(18,'conversion_rate',I,'契约明确0–1范围及nullify；未检查范围导致1469格差异。先适用契约算法，不因比例硬约束再记Data。',4)
for f in ['calculated_tap_through_rate','cost_per_conversion','cost_per_tap']:
 add(18,f,Q,f'{f}整列NULL，raw有taps/impressions/conversions/local_spend_amount所需候选。')
for f in ['cost_per_conversion','cost_per_download','cost_per_tap','tap_through_rate']:
 add(19,f,Q,f'{f}整列NULL，raw已有成本、taps、conversions、new_downloads候选；没有缺少输入的依据。')
CODE='event19的special字典同键先写正确候选、后写同键覆盖，导致正确候选消失；这是代码自身可证明的正确意图未实现，归代码写错。020_resume恢复原候选实验复用。'
add(20,'campaign_id_mapping_restore',C,CODE,source='resume')
for f in ['calculated_tap_through_rate','cost_per_conversion','cost_per_tap']:
 add(20,f,Q,f'{f}有raw候选而整列NULL；038分别单改仍3000行63000格，受campaign_id错误掩盖，不记参与因素。',source='new')
for f in ['action_1_d_view','action_7_d_click','action_value','inline_value','is_index_action']:
 add(21,f,Q,f'{f}的raw候选分别为_1_d_view/_7_d_click/value/inline/index；候选存在却整列NULL。字段自身清理要求不能替整列放弃开脱。')
for f in ['click_through_rate','cost_per_click','cost_per_thousand_impressions']:
 add(22,f,Q,f'{f}有clicks/impressions/spend候选而整列NULL。')
add(22,'spend_mapping_restore',C,CODE,source='resume')
BOOL='契约只给数值类型，raw却使用true/false文本。NULL和映射1/0是不同的类型修复政策；布尔值不唯一确定金额/次数，不能只凭gold的1/0证明某个数值前提P。即使直接TRY_CAST大量失败，也不能从“有布尔值”推出“有可唯一恢复的金额/次数”；按第11节记Choice（中），详见规则问题。'
for f in ['conversions_value','view_through_conversions']:
 add(23,f,U,BOOL,confidence='中')
add(24,'ad_group_id',U,'契约没有源列映射。raw.id仅15/715匹配history，base_ad_group原字符串0匹配、提取末段却715/715匹配；不足以唯一确立raw.id。gold选择id只是选择证据，不能定Data。',4,confidence='中')
for f in ['conversions_value','view_through_conversions']:
 add(24,f,U,BOOL+'此表5条复用核实预算已用完，没有新增核实；038单改仅量化被键选择掩盖的差异。',source='new',confidence='中')
add(24,'conversions_decimal',I,'契约要求DECIMAL(10,2)，SQL先BIGINT后DECIMAL使小数转换数被舍去；移除中途整数化是落实数值规格，不是只换输出类型标签。',4,source='new')
add(25,'campaign_id_mapping_restore',C,CODE,source='resume')
add(25,'spend_masked_diagnostic',Q,'spend整列NULL，raw有cost_micros；与被重复键覆盖的campaign_id区分。020_resume只改spend仍无改善，原因是主键错误掩盖。',source='resume')
for f in ['click_through_rate','cost_per_click','cost_per_thousand_impressions']:
 add(26,f,Q,f'{f}整列NULL，raw有clicks/impressions/cost_in_usd可计算。')
add(26,'sends',U,'raw无sends对应列，契约未规定缺源补0或NULL。')
for f in ['comments','follows','likes','shares','video_completions','video_views']:
 add(26,f,U,f'{f}已有同名raw列，SQL确实尝试转换，没有整列直接填NULL；差异来自NULL/不可转文本补0还是保留NULL，契约未定政策。不能以gold补0证明原始缺失实际上为0。',confidence='中')
for f in ['assists','average_position','bounce_rate']:
 add(27,f,U,f'raw没有{f}对应列，契约无缺源默认值政策。')
for f in ['click_through_rate','cost_per_click','cost_per_conversion','cost_per_thousand_impressions','return_on_ad_spend']:
 add(27,f,Q,f'{f}整列NULL，raw有成本/展示/点击/转化/收入候选。')
add(27,'spend_mapping_restore',C,CODE,source='resume')
for f in ['close_ups','outbound_clicks','pin_clicks','saves','video_views']:
 add(28,f,U,f'raw没有{f}对应列，缺源补0与NULL未定；不能借其他列有候选把本列也归降级。')
add(28,'impressions',U,'raw有impression_1/impression_2；契约未规定是否相加、两者是否互斥。选1还是相加不能仅由列名或gold定下。',4,confidence='中')
for f in ['clicks','spend','total_conversions_value','click_through_rate','cost_per_click','cost_per_conversion','cost_per_thousand_impressions']:
 add(28,f,Q,f'{f}整列NULL；raw有clickthrough_1/2、spend微单位、转换价值微单位及展示/转化候选。具体合并策略虽可能需Choice判断，但未做判断就放弃属于降级。')
add(29,'ad_account_id',U,'raw没有账户ID候选；契约未指定unknown或NULL。')
add(29,'spend_mapping_restore',C,CODE,source='resume')
for f in ['cost_per_install','cost_per_swipe','cost_per_thousand_impressions','cost_per_video_view','swipe_up_rate']:
 add(29,f,Q,f'{f}整列NULL，raw有spend/swipes/impressions/video_views/conversion_app_installs等候选，不能视作缺源。')
for f in ['conversion_purchases','quartile_1','quartile_2','quartile_3','screen_time_millis','shares','story_completes','video_views','view_completion']:
 add(29,f,U,f'{f}同名raw列被TRY_CAST处理；差异来自缺失/不可转文本是否补0，契约未定。0不是由原数据唯一恢复的数值，不成立可被证伪的数据前提P。',confidence='中')
add(30,'advertiser_id',U,'raw没有advertiser_id候选；NULL还是unknown未规定。该列参与评测键，补默认值可大幅改变差异规模，但这不证明unknown是唯一正确值。')
add(30,'spend_mapping_restore',C,CODE,source='resume')
for f in ['conversions','calculated_cost_per_click','cost_per_thousand_impressions','cost_per_thousand_reached']:
 add(30,f,Q,f'{f}整列NULL，raw有CONVERSION或SPEND/CLICKS/IMPRESSIONS/REACH候选；单改无改善，键差异掩盖，非参与。')
for f in ['follows','likes','comments','shares','click_through_rate','cost_per_conversion']:
 add(30,f+'_invalid_policy',U,f'{f}已有raw列且执行TRY_CAST，差异是不可转文本或NULL补0政策。038核实CTR和COST_PER_CONVERSION均900个非数值且非布尔文本，其他四列有布尔文本和缺失；无法从这些文本唯一恢复真实数值。',source='new',confidence='中')
add(31,'app_installs_candidate',Q,'raw确有mobile_conversion_installs_order_quantity及相关安装候选，agent不作判断就NULL，归降级。038只恢复该候选改善21格；020补0改善900格只是gold默认值诊断，不用于本点排序。',source='new')
add(31,'app_opens',U,'完整raw列清单没有app_opens/open候选；安装/下载不等于打开，缺源填法未定。')
for f in ['click_through_rate','cost_per_click','cost_per_engagement','cost_per_thousand_impressions','engagement_rate','spend']:
 add(31,f,Q,f'{f}整列NULL；raw有clicks/engagements/impressions/billed_charge_local_micro，候选和计算输入在场。')
for f in ['follows','likes']:
 add(31,f,U,BOOL,confidence='中')
# impl-007: no finish/result.md and no SQL comments. Grade 1/2 prohibited.
add(32,'peer_order_diagnostic',U,'契约规定按date_day的ROWS窗口和LAG，未规定同日tie-break。复用查询证实上游重复键；诊断确认非窗口基础列一致。契约没有明确允许任意并列顺序，不能套第6节Other；差异取决于未定的同日顺序。完整gold SQL也不能消除所有差异。',4,diagnostic=True,confidence='中',name='同日窗口/LAG并列顺序（共享前提）')
add(33,'gold_positional_union_diagnostic',O,'契约要求按字段含义保留downloads/deletions，agent按名UNION正确；gold SELECT *按位置拼接使Apple两列互换。复用定位/条件比较确认其余内容一致，不把错误的gold列序要求强加agent。',4,diagnostic=True)
add(34,'gold_roi_labels_diagnostic',O,'契约明确ROI标签High/Medium/Low/Uncertain；agent使用短标签，gold为High ROI Expected等长标签。按契约时agent正确；020仅替换ROI CASE验证标签差异。',4)
add(34,'clv_presentation',O,'按契约计算的global_avg_clv只剩二进制浮点末位差异，数值容差L2/L3消失；038只将双方输出该列round到10位，其他列比较条件不动，确认是无指定形式的数值呈现差异。',4,source='new',name='global_avg_clv浮点输出呈现')
for f,reason in [('subscription_name','空名称透传或填Unnamed未规定，gold的默认文案不能确立唯一做法。'),('country','country透传或对空/异常文本补US未规定；不能凭gold补US断言真实国家为US。')]:
 add(35,f,U,reason,4)
add(35,'revenue',O,'契约明确BIGINT，agent按该类型输出；gold DECIMAL(15,2)保留小数。换为契约允许的评测条件agent可对上，不归Form或Intent。',4)
for f in ['active_subscriptions','free_trial_subscriptions']:
 add(36,f,U,f'契约只给{f}名称/类型，没有源映射与计数方式；subscribers人数与active_standard_price/free_trial布尔状态解释均需选择，不能由gold唯一决定。失败报告草稿明确指出Apple订阅summary/event字段语义不一致、需源端定义进一步确认，属于同组意识。',3)
for i in [37,38,39,40]:
 add(i,'active_devices_last_30_days',U,'raw有active_device_installs/current_device_installs，契约没有明确active_devices_last_30_days对应哪列或时间窗算法；agent选active、gold选current。未发现任何候选对比或疑问意识，代码选择本身不算第3档。',4)
add(39,'user_uninstalls',O,'契约BIGINT计数；agent保留daily_user_uninstalls次数，gold把非零压为1。依契约读取，保留计数可成立，不能把gold布尔化作为agent应遵循算法。',4)
add(41,'gold_rating_policy_diagnostic',O,'契约明确非法必需评级delete_row；raw有9条越界，agent删除，gold将越界填3保留。按契约agent处理正确。event61修正其他评级规则未比较本处删除与填3，不据此记意识到本差异。',4,diagnostic=True)
add(42,'invalid_rate_policy_diagnostic',O,'契约明确conversion_rate须0–1、越界nullify；agent依规置NULL，gold重算比值补回3行。诊断只改变该非法值政策，确认与契约不一致。',4)
add(42,'valid_rate_formula_choice',U,'另1条合法源rate与acquisitions/visitors重算比值不同；契约未规定重算，保留合法源值和重算是两种选择。与明确越界nullify的3行分开。',4)
