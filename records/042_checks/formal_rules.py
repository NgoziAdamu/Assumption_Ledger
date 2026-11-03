"""042 v3.2逐点人工判断。旧023类别不进入判类；仅供最后一列原样存档。"""
I='Intent Misreading';U='Unstated Choice';Q='Quiet Downgrade';D='Data Misconception';O='其他';B='代码写错'
RULES={}
def add(table,label,cat,reason,anchor,**kw):
 RULES.setdefault(table,[]).append(dict(name=label,category=cat,reason=reason,anchor=anchor,**kw))
for col in ['running_balance','running_converted_balance']:
 add('quickbooks__general_ledger','mask_'+col,O,f'{col} 的同排序键累计次序不同；契约明文允许 engine-defined ties。023诊断排除两列后其余含键完全一致，5475组并列覆盖28106行。042逐列双侧屏蔽诊断每列减少23907格，行不变；这是允许并列的定位，不是建议改agent算法。','Window ties on all ordering keys are engine-defined',diagnostic=True)
add('stg_quickbooks__invoice_line','item_mapping',B,'event17 rawmap明确写 sales_item_item_id→sales_item_item_id，event21 special映射覆盖成item_id，最终SQL取后者。复用核实显示item_id全空，sales_item_item_id有20000值且全部匹配item表。按手册第6节“同一个映射里先写正确列，后被覆盖”的直接代码证据判代码写错；不拿旧标签定类。','- name: sales_item_item_id',confidence='中',special='invoice_override')
add('stg_quickbooks__payment_line','linked_id',Q,'raw.invoice_id有6000个非空关联候选；agent未判断就整列typed NULL。不是源里根本没有对应候选列的Choice，也没有明确说源表不存在的Data前提。','- name: linked_txn_payment_id',grade=2,disclosure='typed_null')
add('stg_quickbooks__vendor','vendor_name',Q,'raw.display_name和company_name均1500非空，有明显名称候选，agent未判断就整列NULL；不属于无对应源列且默认未定。','- name: name',grade=2,disclosure='typed_null')
add('int_workday__organization_metrics','tenure_all_assignments',I,'契约把avg_tenure_days列在all assignments的mobility段；agent从仅当前任职的current_stats取平均。本数据当前任职0不改变历史任职应纳入的明文要求。','Derive mobility from all assignments')
for table in ['workday__employee_overview','workday__position_overview']:
 add(table,'compensation_regex',O,'契约明确从compensation_grade_id提取第一段数字并分档；agent实现该算法。023核实中900个grade都能提取，gold双反斜杠模式匹配0，落Ungraded。单改成Ungraded仅定位gold差异，不把其解析失败当数据事实，也不要求agent违反契约。','- name: compensation_tier')
add('workday__employee_overview','comp_ebe_join',I,'契约要求从employee enhanced派生compensation/benefits，并以worker_id、source_relation、position_id连接；agent只从position profile派生并只按position/source连接，遗漏worker范围。补齐ebe链和worker键减少7919407格，虽行数不降仍是参与因素。','Compensation/benefits (cb):')
add('workday__position_overview','organization_dimension',I,'契约要求连接organization及organization metrics；agent只用后者，active限制导致inactive组织维度缺失。补齐维度连接改善7784格，行不变仍算参与。','Organizational context:')
add('workday__position_overview','similar_count_only',U,'同组织同job的position计数采用distinct position_id或连接后行数，契约没有给COUNT表达式；本数据单独切换计数无收益。与组织来源选择分开，避免沿用同时改两处的旧similar_group。','similar_positions_in_department is the count',confidence='中')
add('workday__position_overview','similar_organization_only',U,'similar_positions按关系表中的organization_id分组，或先解析组织维度再分组；孤儿键是否保留未明确。保持distinct计数，只换组织来源诊断，不把gold选法当唯一规范。','similar_positions_in_department is the count',confidence='中')
add('workday__position_overview','organization_id',U,'最终organization_id保留关系表可用ID，或只认可匹配维度的ID；契约没有说明孤儿关系键应如何投影。单改到gold来源反而增加差异，记非原因，不用该试验推断违反契约。','- name: organization_id',confidence='中')
add('stg_workday__position','validation_order',I,'employee_type规则先检查原值枚举，再TRIM纠正；agent先TRIM再验证，使2个原值非法的记录被救回。规则已有可执行条件，按Intent而非解析Choice或Data。','- name: employee_type')
add('greenhouse__application_history','floating_days',O,'未结束区间用current_timestamp符合契约。023同一固定时刻重跑后仅days_in_stage浮点运算剩40行40格，L2/L3为0；两种等价秒差/微秒差换算的精度与运行时间条件造成差异，不是未定义的业务算法选择。','- name: days_in_stage',mode='tolerance',confidence='中')
add('greenhouse__job_enhanced','days_clock',I,'days_since_created明定当前日期与created_at之间的天数；agent改用CURRENT_TIMESTAMP，改变时间范围，不是仅运行时点差异。','- name: days_since_created')
add('greenhouse__job_enhanced','prospect_cast',I,"契约给出prospect = 'True'可执行比较；agent先转VARCHAR，BOOLEAN转为小写true后不等于True。按引擎字面效果遵从规则，不推测契约本意。",'prospect')
add('greenhouse__job_enhanced','ratio_zero_vs_null',O,'契约对缺失job-level计数补0，agent据此得到0比率；gold保留NULL计数导致93格不同。替换为gold表达式是诊断，不表示agent应违背计数默认。','- name: application_to_interview_rate')
for table in ['eeoc','email_address','hiring_team','job_department','job_office','phone_number','social_media_address']:
 add('stg_greenhouse__'+table,'uniqueness',O,'本表契约明确声明primary_key/unique；agent按对应键只保留一条，gold保留重复记录。去掉唯一化的单改使含键差异清零，证明是规范/参照不一致，不是默认数据唯一的Data或静默降级。','primary_key:',grade=2,disclosure='greenhouse_dedup')
add('salesforce__daily_activity','won_amount_null',I,'契约仅在没有任何Won记录时补0；存在Won行但amount全NULL时SUM应为NULL。agent无条件COALESCE(sum,0)扩大补零范围。','- name: opportunities_won_amount')
add('salesforce__team_performance','health_growth_null',I,'Revenue growth贡献明定>10给20、>0给15、>=-10给10、否则5；agent将NULL growth补0，落10而不是else5，改变健康分。','Revenue growth:')
for label,col in [('revenue_sum','team_total_revenue'),('revenue_avg','avg_revenue_per_member')]:
 add('salesforce__team_performance',label,U,f'{col}可从user_performance的total_won_amount或另算revenue_data的total_revenue_won取得；契约这里用revenue/won revenue描述但未点明取哪个已存在的量。两者均有业务读法，按材料未定选择。','- name: '+col,confidence='中')
add('salesforce__team_performance','revenue_top',I,'top_revenue_performer明确按highest total won amount排名；agent按另一revenue_data聚合量排名。此处有明文，不把相邻sum/avg的歧义推广过来。','top_revenue_performer =')
add('salesforce__team_performance','mask_top_win_rate_performer',O,'契约允许最高win rate的ties arbitrary；023_team_ties显示差异2组各有4个最高0候选，agent与gold均在其中。逐列双侧屏蔽只减少2格，作为Other参与因素，不虚称实际单改SQL。','top_win_rate_performer =',diagnostic=True)
contact_cols=['assistant_name','department','email_bounced_reason','fax','lead_source','master_record_id','other_city','other_country','other_postal_code','other_state','other_street','photo_url','salutation','title']
lead_cols=['email_bounced_reason','fax','geocode_accuracy','industry','master_record_id','photo_url','salutation','title']
for table,cols in [('stg_salesforce__contact',contact_cols),('stg_salesforce__lead',lead_cols),('stg_salesforce__opportunity',['lead_source','type'])]:
 for col in cols:
  add(table,'null_empty_'+col,U,f'{col}没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。','- name: '+col)
add('stg_salesforce__contact_history','history_key_clock',U,'契约只有history_unique_key非空唯一，没有生成算法；agent用实体ID与Fivetran版本边界MD5，gold用ID与运行时刻拼接。固定同一时刻的单改减少4868行82756格；不使用把created_date误当运行时刻的旧history_key试验。','- name: history_unique_key',grade=2,disclosure='history_key')
add('stg_salesforce__contact_history','unique_contact',D,'P：raw.contact_history的id足以唯一标识一条历史版本。契约只约束history_unique_key，未要求contact_id唯一；042对agent raw核实3000行、2434个id、517个id有多个不同Fivetran版本，P不成立。按id QUALIFY删566行。去重单改被不同评测键遮蔽且反而增差，故非原因，不算参与因素。','- name: contact_id',premise='raw.contact_history的id足以唯一标识一条历史版本。',presence='否',confidence='中')
add('stg_salesforce__lead','status_filter',O,'契约非法status要求delete_row；agent删除4条，gold保留。解除过滤仅定位规范/参照不一致。','- name: status',grade=2,disclosure='sf_invalid')
add('stg_salesforce__lead','status_value',O,'契约允许Open - Not Contacted；agent保留该合法枚举，gold变成Open。值不同不是agent误读规范。','- name: status')
add('stg_salesforce__lead','revenue_precision',O,'annual_revenue明定DECIMAL(18,3)，agent符合；goldDECIMAL(18,2)改变1222格。042仅改精度，不混入范围过滤；L1～L3精度差消除。','- name: annual_revenue')
add('stg_salesforce__lead','revenue_range_only',U,'是否把负收入/极大收入业务值置空未写明；收入不天然等同非负计数硬约束。042保持DECIMAL(18,3)只改范围，收益0，不再把旧混合补丁的精度收益归范围处理。','- name: annual_revenue')
add('stg_salesforce__lead','converted_date',U,'契约给DATE类型但未给该列的1900至current_date+1年边界；agent仅转换，gold额外置空边界外日期。日期范围属未规定业务选择。','- name: converted_date')
add('stg_salesforce__order','account_mapping',B,'event57明确说外键应保持FK列而不是行自身id，并修复多表映射；order遗漏，最终仍id as account_id。该明确正确想法与最终代码冲突，按代码写错。核实order.id匹配account为0，原account_id能匹配894行。','- name: account_id',special='order_mapping')
add('stg_salesforce__task','status_filter',O,'契约列举task status合法值并要求非法值delete_row；agent执行，gold保留2条非法值。','- name: status',grade=2,disclosure='sf_invalid')
for label,reason in [('email_filter','邮箱格式非法应delete_row，agent实施而gold保留5条。'),('email_length','邮箱长度上限255并要求delete_row，agent实施而gold保留1条。'),('email_not_null','email要求not_null；此单点被其他邮箱过滤覆盖，解除非空约束不改善，不能算参与。')]:
 add('stg_salesforce__user',label,O,reason,'- name: email',grade=2,disclosure='sf_invalid')
for table,labels in [('apple_store__app_version_report',['cr','inst','ses','app']),('apple_store__territory_report',['ses','ip','dl','ins','app'])]:
 for label in labels:
  add(table,'join_'+label,U,f'{label}来源的连接使用IS NOT DISTINCT FROM，gold用普通等号；契约指定连接键但未规定NULL键相互匹配与否。NULL-safe键是未定选择，不从gold做法推出数据事实。','business_logic:')
for label in ['ip','dl','ins','ses']:
 add('apple_store__territory_report','aggregate_'+label,I,f'契约明确不在此模型聚合、重复组合传播；agent预聚合{label}上游。去掉该处聚合单改无收益，保留为未确立前提但非判错原因，不混入参与统计。','No aggregation or sorting')
add('stg_apple_store__app_session_daily','semver_regex',O,'契约明确用数值三段版本或纯数字的正则判定合法性；agent正常正则可解析，gold多重反斜杠匹配失败。这里有明文算法，归其他；不是把gold失败当作真实格式不可解析。','- name: app_version')
for label in ['date_filter_null','date_filter_upper','date_filter_lower']:
 add('stg_apple_store__app_session_daily',label,U,'契约给日期有效性和上下界，但未指定字符串解析器；TRY_CAST与多格式try_strptime对1条边界源文本结果不同。未证明agent在可确定格式上大面积失败，属材料未定解析选择；三个过滤位置分别单改。','- name: date_day',grade=1,disclosure='session_date')
add('stg_apple_store__app_session_daily','null_version_filter',I,'契约提供NOT regexp_matches原app_version字面的可执行过滤；agentCOALESCE(NULL,空串)后检查，会把原NULL的UNKNOWN变为通过。去掉COALESCE单改无收益，记非原因。','app_version',confidence='中')
add('int_intercom__conversation_part_aggregates','conversation_coverage',D,'P：每个conversation至少有一条可连接的part，所以以part聚合为基表足以覆盖所有对话。契约For each conversation但没有指定LEFT JOIN算法；缺的是覆盖事实。023在agent可见库核实6703对话中5726个无匹配part；CS换gold上游时6703个全部无匹配，导致全表消失。以conversation为基表覆盖修复清零。','For each conversation, compute counts of parts',premise='每个conversation至少有一条可连接的part。',presence='否',confidence='中')
for label in ['contacts_total','contacts_active_7d','contacts_active_30d']:
 add('intercom__company_metrics',label,U,f'{label}在无匹配聚合时agent补0，gold保留NULL；契约没有给该缺失场景的默认值。三点各减少2509格，行数不降，但仍同类并列主因，不是只能组合修复。','- name: '+label)
add('stg_intercom__contact_history','phone_gold_regex',O,'契约给E.164格式，agent去分隔符、保留/补+并验证；1079个有效号码满足明文，gold双反斜杠模式失配成NULL。非任意解析选择。','- name: phone',grade=2,disclosure='phone_intercom')
for label,col in [('contact_column','contact_id'),('conversation_column','conversation_id')]:
 add('stg_intercom__conversation_contact_history',label,O,f'原始字段错位：数值conversation ID在contact_id，contact文本ID在conversation_id；agent交付按含义交换，符合目标列含义及BIGINT要求。gold同名直取导致不符含义/类型。{col}单独改到gold仍全行不匹配，二者组合才清零；不因此要求agent采纳错位。','- name: '+col,grade=4,special='intercom_mapping')
for col in ['inter_event_minutes','session_seq']:
 reason=('契约允许同occurred_at的prev_event任意次序，两个并列事件的分钟间隔分别不同；其余字段诊断一致。' if col=='inter_event_minutes' else '契约明定session_seq从1开始，首事件NULL prev_event时增加；agent实现，gold有session_seq=0。')
 add('int_klaviyo__events','mask_'+col,O,reason+'042双侧逐列屏蔽用于定位Other，不是实际修复SQL。','- name: '+col,diagnostic=True)
for table in ['campaign','flow','metric']:
 add('stg_klaviyo__'+table,'null_id_filter',O,'契约ID列not_null，agent删除NULL ID行，gold未做该过滤。约99%的raw ID缺失是严重事实，但不能因此把符合契约的处理判成误解。逐表记录raw缺失比例及过程意识，过滤解除仅是gold差异诊断。','- name: '+table+'_id',grade=2,disclosure='klaviyo_ids',special='klaviyo_sparse')
add('stg_klaviyo__event','email_regex',O,'契约要求非法property email删除；agent正确匹配普通合法邮箱，gold双反斜杠正则拒绝2496个本可识别合法邮箱。属于明确格式验证与参照实现差异，不是源数据真实全非法。','Rows with an invalid property_email',grade=2,disclosure='klaviyo_ids')
add('stg_klaviyo__person','null_id_filter',U,'person_id没有not_null约束，agent将其他实体通用ID非空过滤扩展到person；按源缺失person是否保留，契约未定。解除后仅剩1格差异，此过滤为主要原因；不把campaign等三表的约束推广到person。','- name: person_id',grade=2,disclosure='klaviyo_ids')
add('stg_klaviyo__person','full_name_null',U,'契约描述first/last拼接、两者都缺失可NULL，未给单边缺失的可执行拼接规则；concat_ws保留单侧姓名与NULL传播拼接是不同读法。单改被ID过滤遮蔽，未减少规模，记非原因。','- name: full_name',confidence='中')
add('stg_klaviyo__person','phone_normalization',O,'契约明确去非数字并加+，agent符合；gold额外去前导0且替换范围不同。单改无收益，是规范参照不同的非原因控制，不算参与。','- name: phone_number',grade=1,disclosure='person_phone')
