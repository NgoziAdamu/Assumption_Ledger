"""039人工逐点判类；不读取021旧类别。运行数据只提供独立单改规模。"""
I='Intent Misreading';U='Unstated Choice';D='Quiet Downgrade';O='其他';B='代码写错'
rules={};notes={}
def add(i,label,cat,reason,grade=4,source=None,quote=None,confidence='高'):
 rules.setdefault(i,[]).append(dict(label=label,category=cat,reason=reason,grade=grade,source=source,delivery_quote=quote,confidence=confidence))
add(0,'count_joined_tasks',U,'P：total_tasks按关系表中的关联任务计数，包括未匹配task实体的关系。契约写all linked tasks并LEFT JOIN实体，没有规定孤立关系是否仍是任务；026的021-3指出这一歧义。改为有效task计数是另一可行读法，不把gold读法当数据事实。')
add(0,'zero_denominator_policy',B,'原代码已写CASE WHEN total_tasks=0 THEN 0及六个最终COALESCE(...,0)，明确表达零分母补0的正确意图；但is_valid_record和部分标签仍用补0之前的NULL百分比，WHERE提前排除了23个项目。修复将同一零分母政策放回百分比计算层并沿原链重算，属于正确意图未连到校验的代码错误。')
notes[0]=['规则问题：零分母可读为Intent（契约明文补0）；本次选代码写错，因为交付代码自身反复明确补0，错误在计算链应用位置。','count_joined_tasks不是Data Misconception；缺少能裁定孤立关系语义的契约条款。']
add(1,'timestamp_status',I,'P：完成是否及时可把completed_at与due_date都截为DATE。契约在完成状态使用时间戳比较，只有overdue使用日历日。截日会把同日迟交算成及时；按明文算法归Intent。')
add(2,'source_timezone_midnight',U,'P：daily日界使用UTC午夜。契约涉及日期/午夜但未定源+08日界还是UTC日界；两种合理的时间归属改变2行8格，不是大面积解析失败。',source='021_supplement_reruns')
add(3,'time_management',I,'P：time_management_score由完成比例及剩余天数决定。契约明确按schedule_forecast各档映射25/20/15/10/5，其他12；改变算法而非只改标签。')
for l,reason in [('unique_action_types','distinct action_taken计算正确；没有故事匹配时unique_action_types补0，gold保留NULL。契约没有缺组默认值。'),('days_with_activity','distinct calendar dates计算正确；没有故事匹配时days_with_activity补0，gold保留NULL。契约没有缺组默认值。'),('missing_activity_null_policy','没有故事时活动计数、强度及校验使用0而非NULL；契约没有缺组默认政策。修复同一缺失政策沿指标/过滤链重算，不把多个互不相关的字段合并。')]:
 add(4,l,U,'P：'+reason,source='021_supplement_reruns')
add(4,'modification_source',I,'P：latest modification可直接取task.modified_at。契约要求最近故事活动时间；已有候选源，偏差在明文来源限定而非解析。',source='021_supplement_reruns')
for l in ['medium_projects','small_projects']:add(5,l,I,'P：'+l+'按实际任务量分桶。契约本层project_size_category固定medium，分类来源与该规则不符。',source='021_detailed_reruns')
for l in ['developing_performers','avg_tasks_per_member','collaboration_efficiency_score','resource_optimization_score','overall_team_efficiency_score','improvement_recommendations','team_strengths']:add(5,l,D,l+'使用固定0、NULL、空串或不足的评分分量，省略契约要求的统计/分类；CS上游含所需项目和任务事实。候选输入存在而未计算，不能归缺源Choice。',source='021_detailed_reruns')
add(6,'required_project_id',I,'P：只检查原始project_id非空就满足BIGINT not_null。契约约束的是转换后的字段；解析后NULL仍被交出。',2,quote='staging 中对必需键为空或严重无效的记录进行过滤')
add(7,'due_source_choice',U,'P：due_at优先于due_on。契约未写两列优先级；非解析失败或把明确有效值变空。',source='021_supplement_reruns')
for l in ['due_gold_type','start_gold_type']:add(7,l,O,'契约规定TIMESTAMP，agent无时区时间满足类型；gold按TIMESTAMPTZ时刻比较。该点只诊断gold类型/时区呈现不一致，不把gold选择当agent应遵守的规则。',2,'021_supplement_reruns','日期文本使用 `TRY_STRPTIME` 处理源数据中 `+0800` 时区格式，无法解析的可选日期会转为 NULL。')
notes[7]=['原021 due_date/start_date解析替换不改善差异，不另计Data点；分开源列优先级与gold类型。']
q9='留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。'
for l in ['avg_7d_crashes','avg_7d_anrs']:add(8,l,D,l+'直接NULL，省略已有CS crashes/anrs序列上的7日窗口。finish的app quality一一对应本表，且明说窗口未实现及NULL占位。',1,'021_extra_reruns',q9)
for l in ['active_versions_count','supported_os_versions','version_with_most_crashes','os_with_most_crashes','worst_version_crashes','worst_version_anrs','worst_os_crashes','worst_os_anrs','stability_trend']:add(8,l,D,l+'为占位NULL/常量，未使用现有版本、系统及崩溃统计完成计数、最差项选择或趋势。每列独立恢复从CS重算的值；未将整表恢复规模分摊。finish明确点名app quality。',1,'039_supplement',q9)
for i in [9,12,14]:
 for l in ['device_installs','device_uninstalls','device_upgrades','user_installs','user_uninstalls','active_devices_last_30_days','install_events','uninstall_events','update_events']:
  add(i,l,D,l+'为固定0/NULL，实际CS installs/store源有候选指标；机械投影未做契约需要的连接与该指标计算。finish只笼统提多项marts，没有点名本表，故第2档。',2,'021_supplement_reruns' if l not in ['install_events','uninstall_events','update_events'] else '021_reruns',q9)
 for l in ((['crashes','anrs'] if i in [9,14] else [])+['average_rating','rolling_total_average_rating','total_device_installs','total_device_uninstalls','net_device_installs']):
  add(i,l,D,l+'被整列占位，缺少已有ratings/crashes或installs输入的连接、累计/净额计算。039按该列从CS输入恢复，并保持其他输出和agent行范围不变。',2,'039_supplement',q9)
for i,missing in [(10,'用户行为、留存、app quality、finance等多源连接；收入/安装/稳定性指标；综合评分、分类及时间窗口'),(11,'安装、ratings与store多源合并；国家统计；累计/滚动指标与地区补充'),(13,'earnings和subscription事件连接；国家/商品维度、收入转换/汇总、订阅及滚动窗口'),(15,'安装、ratings、崩溃及store来源合并；应用日汇总、累计/滚动指标')]:
 add(i,'whole_implementation_diagnostic',D,'同类缺口组：'+missing+'。event39用同一个fallback循环，取source_models[0]、只投影少数维度，其余常量/NULL；整表没有实现要求的关系。该首源在CS可为空，缺少其他分支仍是本表自己的缺口。只能整体诊断的机械生成模型按第7节同类候选处理，不能称每个字段都已单改。',2,'021_reruns',q9,'中')
 notes[i]=['规则问题：按用户允许的同脚本机械生成例外记一个同类缺口组；只确立类别，不从整表恢复推导各子指标贡献。event39原脚本见轨迹审计。']
qe='Earnings 源数据 `transaction_date` 为空而 `transaction_time` 有值；为提供可用日期，暂用 `transaction_time` 日期部分回填。源 SKU 为空时用可用的 product/base-plan 值兜底。'
add(16,'transaction_date_source_policy',U,'P：缺失必填transaction_date时，用transaction_time日期保留记录。契约未给来源映射或缺失源的补值政策；同名源全空而时间候选可解析，不能判定回填不合理。反事实选择不回填并执行该列必填约束。',1,'039_supplement',qe,'中')
add(16,'sku_source_policy',U,'P：缺失sku_id时可用product/base-plan兜底保留记录。契约未指定替代来源；核实显示sku_id/product_id全空、base_plan_id可用。反事实是不替代并执行该列必填约束。',1,'039_supplement',qe,'中')
add(16,'package_source_policy',U,'P：package_name可以映射base_plan_id。没有同名原始字段，契约未给映射；product_id也是候选但本数据全空，不能仅凭gold选它认定Data。反事实用product_id并执行该列必填约束。finish的SKU说明不能推广到package_name。',4,'039_supplement',confidence='中')
add(16,'contract_other_default',I,'P：非法或缺失transaction_type保持NULL。契约明确COALESCE(transaction_type, Other)，应补Other；单改无改善仍保留非原因，不把旧output_not_null过滤的全匹配当正确算法。',source='021_extra_reruns')
notes[16]=['规则问题：来源政策的“回填并保留/不回填并按必填排除”各含映射与该列过滤两步，按一个逻辑政策比较；三项反事实重叠，不相加贡献。把握中。','旧missing_required_source_policy替换整表，混入其他校验；output_not_null_policy仅因错误的transaction_type NULL删光而对上，均不用于主因排序。039拆开三列政策，保留Other默认的独立零贡献点。']
add(17,'required_fields',I,'P：date_day可以保留NULL。契约date_day/package_name显式not_null，交付SQL无必填过滤。finish点名installs_overview的缺日期不是本张ratings_overview；“基础投影/部分校验”不是对本处缺键政策的说明，故第4档。')
for l in ['deals_won_rank_peer_order','cycle_time_rank_peer_order','win_rate_rank_peer_order']:add(18,l,O,'契约允许ROW_NUMBER并列任意顺序；025诊断并列组与rank多重集相同，差异在同值行被分配的序号。该替换仅用于对齐gold同值次序，不要求agent另加tie-breaker。',source='025')
add(18,'score_arithmetic',O,'相同契约评分公式的浮点乘除结合顺序导致末位差异；宽松层及025诊断确认。不是新业务算法。',source='025')
for l in ['win_rate_percentage','enterprise_win_rate','large_deal_win_rate']:add(18,l,I,'P：'+l+'零分母可留NULL。契约对无对应deals的win rate明确返回0；不是未规定NULL策略。',source='025')
add(19,'rating_labels',O,'agent使用契约Excellent/Good等短标签，gold另附Performance后缀；同分类的文字差异，不改变数值业务计算。',source='025')
add(19,'growth_arithmetic',O,'相同growth公式的浮点结合顺序造成3格末位差异；025宽松诊断可对齐。',source='025')
for l in ['enterprise_revenue','large_revenue','medium_revenue','small_revenue']:add(20,l,U,'P：'+l+'在没有符合条件的won deal时返回NULL而非0。契约给分类范围但未规定空条件求和的默认值；两种聚合写法合理。',source='025')
for l in ['volume_rank_peer_order','efficiency_rank_peer_order','win_rate_rank_projection']:add(20,l,O,'契约允许同值任意排序；025确认peer组的内容和rank集合一致。直接投影已有rank与重新分配同值rank产生差异，不能据gold序号判Intent。',source='025')
add(20,'recent_month_window',I,'P：最近月份窗口是当前月及前2月。契约给出的边界是当前月减3个月，含边界；范围算法已有明文。该数据单改不减少规模。',source='025')
notes[20]=['025使用threads=1的共同基线200行/862格，不能混用旧865格。stddev/stddev_samp别名、未被最终投影使用的rank探针没有独立错误，不重复记点。']
add(24,'unique_engagement',I,'P：engagement_id重复可直接保留。契约明确unique；单改仅落实该约束。用last_modified选择保留项是诊断具体实现，不据此创造契约未写的优先级要求。')
q10='原始 HubSpot 时间字符串按日期时间前 19 位解析，以支持时区偏移和小数秒，同时输出合同指定的无时区 `TIMESTAMP`。空值或无法解析的时间转换为 NULL；必需创建日期无效的行按合同要求排除。'
for l in ['created_timestamp','updated_timestamp']:add(25,l,O,'agent按契约输出TIMESTAMP，前19位能解析有效时间；gold的整串格式限制将这200个值置NULL。不是agent大面积解析失败，契约未要求拒绝带后缀的有效输入。',2,quote=q10)
add(29,'unresolved_open_until',I,'P：未解决issue也以最后历史记录日期作为结束日。契约明确未解决者延续到today；该条件改变日历范围。',source='021_fast_reruns')
add(29,'history_driver',O,'agent以issue主表驱动并LEFT JOIN历史，契约写For each issue、Join issues to date spine；gold反而由字段历史驱动，漏掉没有历史的issue。该对照改成history驱动只用于定位gold行范围，不把agent实际做法说反，也不要求为迎合gold排除无历史issue。',source='021_fast_reruns',confidence='中')
add(30,'remove_many_to_many',I,'P：按issue聚合生命周期之前可额外连接该issue的所有history行。契约明确基于相邻活动变更区间计算次数和平均时长；这个额外多对多放大转移数，做法由规格定下，归Intent而非Data。')
add(31,'derived_parent_name',B,'原SQL已计算正确coalesce(revised_parent_issue_id,parent_issue_id)，却命名parent_issue_id_derived；i.*保留未修正parent_issue_id。正确意图在代码中明确，实际交付列未被替换。finish只说已修复别名问题，不是披露本处仍有别名错误或采用何种默认处理，故不记第2档。')
for l in ['status','sprint','story_points','story_point_estimate']:add(32,l,I,'P：'+l+'在透视后统一COALESCE为is_null。契约要求在透视前把真实NULL变更标为is_null，未变更字段在透视后仍为NULL；agent把未变更也写成is_null，改变明确的状态语义。')
q11='尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。'
add(33,'overall_health_score',D,'overall_health_score固定常量，未把契约分项统计汇总为项目健康分。已有CS项目/issue输入。finish明确点名project health scoring并披露简化评分。',1,'021_extra_reruns',q11)
for l in ['story_points_mapping','velocity_trend','health_score']:add(34,l,D,{'story_points_mapping':'用常量1代替现有字段历史中的story points；没有做候选映射判断。','velocity_trend':'velocity_trend_3d固定NULL，省略契约要求的三快照移动平均。','health_score':'固定健康分，省略实际指标计算。'}[l]+' finish点名sprint performance analytics的趋势/评分简化，对应本处。',1,'021_extra_reruns' if l!='velocity_trend' else '021_detailed_reruns',q11)
add(34,'timestamp_window',I,'P：sprint边界可以截为DATE。契约用时间戳限定承诺/完成窗口，截日会改变同日窗口内外。',source='021_extra_reruns')
add(34,'velocity_null_default',I,'P：没有速度基线可先COALESCE为0再分档。契约CASE明确NULL落ELSE Negative Velocity；不是任意缺失政策或纯标签呈现。',source='021_detailed_reruns')
add(34,'limit_before_snapshots',I,'P：LIMIT可在快照展开后作用于最终结果。契约先限制sprint再展开快照；修复改变行范围，行规模变坏，不记参与。',source='021_detailed_reruns')
notes[34]=['remove_limit探针违反契约允许LIMIT，不是合法单点修复；有限集合任意取样的残差不硬归agent。limit_before_snapshots虽减少44格但行数增加，按用户行优先口径不列参与。']
add(35,'comparative_join_multiplicity',I,'P：每issue输出一行足以满足本表。契约grain及self-join条款明确保留项目内自连接的重复行；漏掉规定关系改变粒度及计算输入，不是只改变呈现的Form。只恢复重复传播，不替代其他占位列。',source='021_fast_reruns')
for l in ['lifecycle_deviation_ratio','lifecycle_outlier_status','deviation_risk_score','collaboration_opportunity_score','efficiency_opportunity_score','total_risk_score','total_opportunity_score','recommended_action','intelligence_score','health_status','strategic_importance','intervention_urgency']:
 add(35,l,D,l+'为NULL/固定值或缺少分项的简化和式，未计算现有issue数据上的项目统计、异常分数及对应分支。039从CS上游按契约重算该输出，其他列保持原始；没有把整表恢复当该列贡献。finish未点名issue intelligence，只笼统承认复杂指标/分支未完整实现。',2,'039_supplement','少数复杂分析并未完整实现合同中的每个指标/分支。')
notes[35]=['021_runtime_diagnostics的同一时钟gold诊断排除total_lifecycle_days和lifecycle_deviation_ratio后全匹配；固定时钟与已物化gold的时间差不再标成agent算法错误。','039单列恢复保留8000行，主因自连接减少的是格子规模而非行规模；因此不能标“只能组合修复”。']
add(36,'type_id_instead_name',O,'agent以issue type名称判断epic/bug符合契约；gold用类型ID与这些单词比，实际ID无一为这些词。021诊断8000条成功匹配类型、4180非默认名称、ID匹配0，证明差异来自gold实现。',source='021_detailed_reruns')
for l in ['unique_issue_types','unique_components','total_external_links','sprint_adoption_rate','complexity_risk_score','scope_risk_score','recommended_intervention','strategic_priority_recommendation']:add(36,l,D,l+'以固定计数/分数/分类替代契约计算；所需issue、components、links及sprint输入在CS可用。finish明确点名project risk assessment详细计算简化，故第1档。',1,'021_extra_reruns',q11)
for l in ['story_points_committed','story_point_estimate_committed','story_points_end','story_point_estimate_end','story_points_completed','story_point_estimate_completed','issues_committed']:add(37,l,D,l+'直接NULL，未用已有字段历史/issue/sprint窗口计算；不是原始列不存在。finish点名sprint performance analytics，不是一一对应的sprint_enhanced；只适用笼统复杂指标未完成，第2档。',2,'021_detailed_reruns','少数复杂分析并未完整实现合同中的每个指标/分支。')
for l in ['engagement_depth_score','total_engagement_score']:add(38,l,O,'契约明确avg_outbound_influence_strength为NULL时depth为NULL，total随之NULL；诊断4524行均无该strength，而gold的LEAST忽略NULL产生非空分数。agent的本列NULL与契约一致。',source='021_detailed_reruns')
add(38,'influence_level',O,'agent的Minimal短标签符合契约；gold加Influence后缀，分类含义相同。',source='021_detailed_reruns')
for l in ['stakeholder_archetype','development_opportunity','strategic_value_score','recommended_engagement_strategy','engagement_risk_status','engagement_quality_score','engagement_impact_score']:add(38,l,D,l+'是固定值，未执行契约的评分/阈值/分类分支；现有活动、用户与issue数据足以计算。finish点名stakeholder dashboard详细业务计算使用默认/简化，适用第1档。',1,'021_detailed_reruns' if l in ['stakeholder_archetype','development_opportunity'] else '021_extra_reruns',q11)
add(38,'total_comments_authored',O,'agent直接按author计评论符合契约；gold在reporter/assignee多表连接后count(*)放大评论。021诊断1633名用户被多计，总超额5921。',source='021_extra_reruns')
add(38,'total_projects_involved',O,'agent对reported或assigned项目取并集去重，符合契约。gold用coalesce(reporter_project,assignee_project)遗漏另一侧，不能把并集改成gold读法归Intent。',source='021_extra_reruns')
add(38,'cross_functional_projects',O,'契约按用户报告或被分配issue涉及的唯一非空项目计数，agent按此计数；gold另连接project实体，只计匹配成功的项目，排除孤立项目ID。不是0/NULL默认政策。',source='021_extra_reruns',confidence='中')
add(38,'engagement_breadth_score',O,'本数据network无满足阈值的边，agent的8×项目数等价契约3×projects+5×cross_functional（同一issue项目并集）。gold分别用coalesce漏项目和匹配实体排除项目，造成分数不同；未另虚构独立Intent点。',source='021_extra_reruns',confidence='中')
add(38,'response_label_only',O,'契约列举Rapid/Timely/Standard/Slow短标签；gold附加Responder。本探针只把现有常量Slow变成Slow Responder，不修复缺失的响应计算。',source='039_supplement')
add(38,'response_calculation_only',D,'response_pattern_type固定Slow，省略按assigned issue解决时长均值分档。用契约短标签恢复计算后，gold长标签使L0–L3仍全不匹配；标记非原因而不遗漏缺口。finish点名stakeholder简化分类。',1,'039_supplement',q11)
notes[38]=['旧response_pattern_type同时补计算和Responder后缀，不能当一个降级点的贡献；039拆开标签、计算和仅诊断组合。','规则问题：breadth和cross_functional按契约“issue所涉及项目”读为不另要求project实体匹配；另一读法是只计有效项目。选前者，与契约对null项目排除的明确限定相容，把握中。','总分、分类恢复探针用于定位输出差异；gold中项目/评论及NULL传播偏差已单列，不能用gold的类别直接证明agent应选择该类别。']
add(39,'user_metrics_driver',I,'P：以所有user为驱动并LEFT JOIN活动即可。契约明确从user metrics驱动并连接用户，agent多出无活动用户；范围由条款决定。',source='021_detailed_reruns')
for l in ['avg_daily_activity_score','avg_weekly_activity_score']:add(39,l,I,l+'对契约未COALESCE的nullable平均值额外补0；这是明文计算链的改动，不能被“团队dashboard简化”泛化为披露此NULL政策。',source='021_detailed_reruns')
for l in ['projects_contributed_to','issue_types_worked_on','days_since_first_issue','leadership_indicator','overall_performance_score']:add(39,l,D,l+'使用固定0/NULL/默认值，省略已有user/issue活动上的统计、时间或评分。finish明确点名team dashboard详细计算简化，适用第1档。',1,'021_detailed_reruns',q11)

notes[29]=['规则问题：契约For each issue与Join issues to date spine按自然读法包括无历史issue；选其他。若把历史存在视为隐含入选条件则可读为Choice，契约未明写该过滤。与未解决issue必须延续today的明确Intent点分开。']
notes[38].append('039补充诊断stakeholder_diagnostic.json：4524用户，gold与原issue项目计数差356、与有效project实体计数差0；并集差2418；breadth差1579；非零网络0。支持本处Other，而非仅按旧标签或单改成功推定。')
