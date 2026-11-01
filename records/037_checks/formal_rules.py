"""037 人工逐点判据。缩写仅为本脚本常量，绝不读取019类别来决定新类别。"""
I='Intent Misreading';D='Quiet Downgrade';C='Unstated Choice';O='其他';B='代码写错';F='Form Mismatch';M='Data Misconception'
RULES={}
def table(task,name,points):RULES[task+'_'+name]=points
def p(label,cat,reason,term=None,grade=4,quote=None,confidence='高'):
 return dict(label=label,category=cat,reason=reason,term=term or label,grade=grade,quote_key=quote,confidence=confidence)
# 每条说明来自037重新阅读契约、最终SQL及干预；旧字母类别未用作推导条件。
for name,label in [('int_lever__posting_analytics','referral_rate_pct'),('int_lever__posting_performance','referral_rate')]:table('impl-001',name,[p(label,D,'契约要求申请中referrer非空的比例，交付SQL直接填0，属于未完成该指标的占位。',grade=1,quote='lever_defaults')])
table('impl-001','int_lever__posting_applications',[p('tie_order',O,'契约允许created_at并列时由引擎任取。019双侧admissible诊断均为0；本点是允许的并列先后，不是取错经理。','created_at',confidence='高')])
table('impl-001','lever__candidate_experience_insights',[
 p('contact_join',I,'契约要求连接contact_info，SQL省略；单改没有减少评测差异，列为非原因。','contact_info'),
 p('stage_inner',I,'契约规定stage内连接，agent使用LEFT JOIN；单改没有减少差异。','stage'),
 p('completion_zero',I,'契约明确不加零除保护，agent增加NULLIF，改变计算出的值；不是呈现差异。','zero-division'),
 p('timeline_score',B,'同一SQL已经输出timeline_experience_score=1，overall表达式却把这一项写成3；正确计算意图有代码内证据。','overall_candidate_experience_score'),
 p('recommendations',D,'有契约条件和候选输入，却把所有improvement_recommendations写成空串；本表不在最终报告点名的占位表名单中。','improvement_recommendations'),
 p('gold_join_multiplicity',O,'gold将同键的四份子结果再次连接，出现n^5重数；agent结果与契约每opportunity一行的粒度一致。019该改动是复现gold重数的诊断，不是建议修复agent。','grain:',confidence='中')])
table('impl-001','lever__candidate_quality_insights',[p(label,O,'条件和分类内容一致，仅英文消息写法不同；契约规定消息含义而未写死字符串。019只替换文字即消去该列差异，按第5节归其他。',label,confidence='高') for label in ['key_finding_source','key_finding_overall','primary_recommendation','process_recommendation']])
table('impl-001','lever__departmental_hiring_trends',[p('referral_count',I,'契约数有referrer的distinct application；agent数distinct referrer，漏算同一推荐人关联的多个申请。','referral_rate'),p('cost_tier',D,'未实现成本分类，固定No Data；即使无hire也没有输出契约要求的No Hires。','cost_efficiency_tier',1,'lever_defaults')])
table('impl-001','lever__hiring_manager_scorecard',[p('decision_speed',D,'决策速度整列Unknown占位；019对无hire输入恢复Slow分支仅作局部贡献证据。','decision_speed_category',1,'lever_defaults', '中')])
table('impl-001','lever__opportunity_enhanced',[p('candidate_partition',I,'契约明确按candidate选择最新offer，agent按opportunity分区；改动涉及行对应，不是文字形式。','candidate')])
table('impl-001','stg_lever__offer',[p('status_filter',I,'offer.status无效枚举应置NULL；agent套用requisition的枚举并删整行。','status',2,'lever_clean'),p('status',I,'status非法值的nullify_field规则遗漏；过滤尚未修复时单改该列无净改善。','status',2,'lever_clean')])
for table_name,labels in [('stg_lever__posting',['categories_commitment','categories_level']),('stg_lever__requisition',['compensation_band_currency','compensation_band_interval'])]:table('impl-001',table_name,[p(x,I,'契约已逐字段给出合法枚举及nullify_field；agent未执行，改变保留值而不只是呈现。',x,2,'lever_clean') for x in labels])
table('impl-002','int_pendo__conversion_funnel_analysis',[]) # 源模块用037完整单点探针替代019的feature-only局部探针。
table('impl-002','int_pendo__customer_rfm_analysis',[
 *[p(x,C,'契约给出业务用途/大致类别但没有完整segment到策略、CLV或优先级映射；几种规则均说得通。差异取决于未规定的选择，不把gold映射当要求。',x,confidence='中') for x in ['recommended_strategy','predicted_clv_tier','action_priority']],
 *[p(x,D,'契约要求账户级聚合，SQL整列NULL；最终报告明确说RFM account-level metrics为NULL placeholders，按025更正归第1档。',x,1,'rfm') for x in ['account_total_visitors','account_high_value_ratio','account_top_segment_ratio','account_at_risk_ratio','account_avg_rfm_score']]])
table('impl-002','int_pendo__data_quality_checks',[p('completeness_rows',D,'报告只交summary，遗漏event completeness详情行；019单独插回该行已确认其贡献。其余章节在037继续分别检查。','Data Completeness Details',1,'quality')])
table('impl-002','int_pendo__product_health_metrics',[]) # 037完整score公式替代019只有feature项的局部探针。
table('impl-002','pendo__customer_lifecycle_insights',[
 *[p(x,D,'契约逐项给出派生规则，交付SQL用固定默认标签替代。报告点名lifecycle insights使用defaulted derivations。',x,1,'lifecycle') for x in ['customer_journey_stage','predicted_ltv_tier','engagement_velocity','usage_trend','customer_importance_level','investment_expectation']]])
table('impl-002','pendo__executive_dashboard_metrics',[p('avg_feature_adoption',D,'账户级feature adoption汇总被NULL占位；019按每账户max后求平均的单改可复用。','avg_feature_adoption',1,'dashboard')])
table('impl-002','stg_pendo__event',[p('event_key',C,'契约指定六个MD5来源字段但没有指定拼接分隔符；带分隔符与直接拼接造成键值不同。hash是计算值，不归Form。','event_key',confidence='中'),p('account_id_validation',I,'契约的account_id校验规则被省略；当前hash差异掩盖其整表规模贡献。','account_id',2,'pendo_clean')])
table('impl-002','stg_pendo__page_event',[p('page_event_key',C,'契约只声明代理键及类型，未规定生成字段与拼接公式；差异取决于未规定的键生成选择。','page_event_key',confidence='中')])
table('impl-002','stg_pendo__poll_event',[p('poll_event_key',C,'代理键算法/拼接未规定；不拿gold键算法作为规格。','poll_event_key',confidence='中'),p('url',I,'契约给出可执行的URL正则字面规则；agent只做trim。按第5节以DuckDB实际正则效果为准。','url',2,'pendo_clean')])
table('impl-002','stg_pendo__user',[p('deleted_at_parse',M,'P：raw.user中非空deleted_at文本可由直接TRY_CAST(... AS TIMESTAMP)解析。契约只给目标类型/空值规则，未指定解析算法；019在agent留存raw上核实17行中12行直接转换失败而截取前23字符成功，证伪P。','deleted_at',2,'pendo_time','中'),p('normalized_user_type',I,'契约要求先规范化user_type再枚举校验，agent在原始值上过滤。','user_type',2,'pendo_clean'),p('required_user_id',I,'契约要求必需user_id校验；遗漏该条件但单改未减少本次差异。','user_id',2,'pendo_clean')])
table('impl-002','stg_pendo__visitor_history',[p('last_visit_parse',B,'同一最终SQL对first_visit和last_updated_at已用截取解析，只有last_visit遗漏，存在正确实现意图的代码内证据。','last_visit_at',2,'pendo_time')])
table('impl-003','int_customer360__customer_behavior_analysis',[p('first_touch',O,'契约明确任一输入NULL则输出NULL，agent遵守；gold的LEAST忽略NULL。019改为gold做法用于定位差异。','NULL'),p('last_activity',O,'同上，契约对任一NULL的要求与gold GREATEST忽略NULL不同。','NULL')])
table('impl-003','int_customer360__customer_lifecycle_metrics',[p('frequency_score',I,'契约明确active30/60高分分支，agent只按交易计数分档；缺的是规定的算法，不是数据事实。','frequency_score'),p('stochastic_evaluation',O,'契约允许random()模拟；不同执行产生不同交易数。复用019共同屏蔽随机输出的诊断，不能把随机种子差异归为agent错误。','random',1,'random','中')])
table('impl-003','int_customer360__risk_assessment',[p('probability_type',F,'七项风险和阈值计算一致，输出推断为DECIMAL(2,2)，契约明确DECIMAL(3,2)。019只cast同一CASE值即可消除这部分差异，不改变后续计算值。','intervention_success_probability'),p('primary_risk_factor',C,'规定类别优先级但没有完整触发阈值；这里是数值阈值选择，非纯标签差异。','primary_risk_factor',confidence='中'),p('recommended_intervention',C,'契约给优先顺序/含义但未给所有触发阈值，无法以gold阈值作要求。','recommended_intervention',confidence='中')])
table('impl-003','customer360__conversion_funnel_analysis',[p('presentation_round_revenue',F,'037只对最终revenue_velocity_monthly round(...,2)，L0差异由99356行/449116格变为8744行/358504格。原表达式除以days/30与LTV/days×30代数相同；019称分母/单位错误不成立，按明确两位小数要求归Form。','revenue_velocity_monthly'),p('rounded_consistency',I,'契约要求用于journey_efficiency_index的中间consistency先舍入；agent使用未舍入值。会进入计算链，不是Form；单改未减少当前规模。','journey_efficiency_index'),p('journey_completeness_score',O,'契约任意两个平台应得2；gold遗漏Marketo+Zendesk组合，agent按在场平台数实现符合契约。','journey_completeness_score')])
table('impl-003','customer360__customer',[p('metrics_key_multiplicity',C,'契约一方面声明每customer360_id一行，另一方面明确要求metrics按id与dimensions结合；上游重复id使两者发生冲突。agent直接内联保留dimensions重数，gold重新按id连接扩行。按第11节选择Unstated Choice（两个要求不能同时照字面满足），不沿用019的Data。','customer360_id',2,'duplicates','中')])
table('impl-003','customer360__customer_activity_metrics',[p('cross_platform_consistency',I,'契约规定按在场平台数取平均，agent只相加未除；算法已写明，归Intent。','cross_platform_consistency'),p('primary_engagement_channel',I,'契约要求比较原始engagement，agent比较时间衰减后score，属于规定的指标定义未落实。','primary_engagement_channel'),p('stochastic_evaluation',O,'契约允许random模拟活动量及派生量，单次gold随机输出不是唯一有效值；复用019屏蔽随机列诊断。','random',1,'random','中')])
table('impl-003','customer360__mapping',[p('outer_source',I,'契约明确FULL OUTER JOIN后再UNION unmatched，agent把第一组连接写成LEFT JOIN；此算法已规定，不归Data。','FULL OUTER'),p('source_ids_order',O,'source_ids的JSON数组只有无序集合成员先后差异；契约未规定数组排序。037双侧只规范数组顺序的诊断隔离此点。','source_ids',2,'ordering','中')])
table('impl-003','customer360__phone',[p('phone_tie',O,'相同phone不同extension的row_number并列顺序未被规定；019去掉序号后双方多重集完全一致，且SQL按规定phone排序。','phone',2,'ordering','中')])
table('impl-003','customer360__status',[p('string_order',O,'STRING_AGG DISTINCT成员顺序未规定；019双侧排序后差集0。037采用原官方判错范围，019重跑基线恰好一致不将本表剔除。','source_systems',2,'ordering','中')])
table('impl-003','customer360__updates',[p(x+'_order',O,'STRING_AGG DISTINCT的成员先后未规定；019共同规范两列后多重集完全一致，037分别规范每列以测量各自贡献。',x,2,'ordering','中') for x in ['update_types','updated_by_systems']])
table('impl-003','stg_customer360__country_codes',[p('dedup',O,'契约要求alpha-2唯一，agent稳定去重，gold保留重复；移除去重仅作差异诊断。','country_code_alpha_2',1,'country')])
table('impl-003','stg_customer360__state_territory_codes',[p('distinct_rows',C,'契约未声明整行去重或唯一性，agent保留重复，gold DISTINCT删除；这是材料未定的保留策略。','grain:',2,'ordering','中'),p('membership',I,'契约成员校验为存在性判断，agent使用可能扩行的连接；单改为IN不减少本次差异。','country_code_alpha_2',2,'stage3')])
for n in ['account','contact']:table('impl-004',f'salesforce__{n}_daily_history',[p('tie_order',O,'契约允许同实体同日最新时间并列时任取；019双侧非admissible记录数均0。','arbitrary',1,'daily')])
table('impl-005','int_google_ads__account_performance_metrics',[p('cs_column_collision',O,'CS使用gold上游，其额外cost_per_conversion列被SELECT *带入并遮蔽正确舍入列；agent当时的上游没有该额外列。019诊断排除该列后主要差异消失，属于评测上游条件不同。','cost_per_conversion',confidence='中'),p('ctr_precision',C,'契约未规定中间CTR运算使用FLOAT还是DOUBLE；边界舍入数值不同，不能只视为呈现差异。','click_through_rate',confidence='中')])
table('impl-005','google_ads__customer_acquisition_analysis',[
 p('cohort_avg_cac',I,'契约cohort均值使用已舍入的CAC输入，agent使用未舍入表达式；影响计算链，单改无净改善。','cohort_avg_cac'),p('cohort_avg_ltv',I,'契约cohort均值使用已舍入的LTV输入，agent使用未舍入表达式；单改无净改善。','cohort_avg_ltv'),
 *[p(x,C,'契约未给可直接执行的排序方向/完整计分斜率与上限；higher rank可指名次靠前或百分位数更高。这里保留未规定的选择，不用gold公式反推要求。',x,confidence='中') for x in ['cac_efficiency_percentile','ltv_cac_performance_percentile','acquisition_sophistication_score']],
 *[p(x,C,'细分/建议规则缺少完整阈值和优先级；最终报告针对customer acquisition明确承认此缺口并说明选择CASE规则。',x,1,'acquisition','中') for x in ['strategic_customer_segment','acquisition_recommendation']]])
table('impl-005','google_ads__executive_dashboard',[p('rounded_alias',B,'agent已经写出正确round表达式，但SELECT *中的同名列优先，后列被自动改名，最终仍输出旧列；正确意图有明确代码证据。','round'),p('scale_null',I,'契约规定扩张标志默认false，agent布尔比较留下NULL；修改值的语义而非形式。','scale'),p('trending_null',I,'契约trending_alert的else为false，agent三值逻辑留下NULL；算法已规定。','trending_alert')])
for n in ['account','ad','campaign']:table('impl-005',f'stg_google_ads__{n}_history',[p('timestamp_cast',C,'契约只指定TIMESTAMP目标及有效性检查，没有规定源时区文本解析器。agent用try_strptime保留可解析时间，gold直接TRY_CAST得到NULL；这是未指定的解析选择。','updated_at',1,'ads_time','中')])
table('impl-005','stg_google_ads__ad_group_history',[p('timestamp_type',O,'契约要求TIMESTAMP，agent遵守而gold为TIMESTAMPTZ；诊断cast为gold类型可对齐，不把gold类型当契约。','updated_at',1,'ads_time')])
# 新补充干预逐点归类；分类依据是各自契约/代码，而非019旧标签。
def new_rule(id,label,why):
 cat=D;grade=1;key='lever_defaults' if id.startswith('impl-001') else ('funnel' if 'conversion_funnel' in id else 'health' if 'product_health' in id else 'quality' if 'data_quality' in id else 'dashboard' if 'executive_dashboard_metrics' in id else 'lifecycle')
 if label.startswith('unweighted_'):cat=I;grade=2;key='lever_defaults';why='契约要求每posting简单均值；agent在application扩行后求AVG，形成按申请量加权。知道契约规定的汇总层次即可改正，归Intent。'
 if label=='customer_segment_branches':cat=I;grade=2;key='lifecycle';why='已实现有条件的分类，但漏掉契约明写的四个分支；不是数据性质假设。报告只泛称lifecycle简化，没有点出这几个被漏分支。'
 if label.startswith('avg_30d_'):cat=I;grade=2;key='funnel';why='契约明确相对today的30日下界、cohort按account/app等值连接；agent对全历史做窗口平均，未执行规定算法。'
 if label=='retention_join':cat=I;grade=2;key='health';why='契约规定feature先FULL OUTER JOIN账户retention，再接engagement；agent省略中间账户来源，只f/e连接。连接算法已写明，归Intent。'
 if label=='presentation_round_revenue':return next(x for x in RULES[id] if x['label']==label)
 if label=='trending_null':return next(x for x in RULES[id] if x['label']==label)
 return p(label,cat,why,grade=grade,quote=key,confidence='中' if label in ['development_recommendations','department_strength_referral','primary_improvement_area'] else '高')
