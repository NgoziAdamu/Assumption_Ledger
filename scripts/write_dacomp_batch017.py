"""Task017 annotations. Decisions are separate from factual uncertainty field."""
from annotate_dacomp_batch017 import *
from write_dacomp_batch016 import results,METHOD
import csv
A={
21:dict(cat='U',confidence='中',factors='无；两种计数替换是同一错误点的替代修法',flags='证据曾出现但被忽略',cost='多条查询',primary=['spine_days_count'],u4='是：仅修spine计数，2行/2格→0，L0整表一致',
 desc='date spine连接同一天多条事件后被放大，count(*)减去去重事件日数把两个本应为0的missing_day_count算成1。',
 reason='已核实：CS上游gold中LRqEsZ与MCX88q各有同日2个事件、活动区间仅1天，gold缺失天数均0，agent均1。agent用连接后的count(*)减count(distinct e.occurred_on)，前者为2而后者为1。只把前项改为count(distinct d.day)，或只把后项改为count(e.occurred_on)，两种独立替代修法都L0匹配；主因是依赖连接不扩行的未核实假设。标注者核实agent实际staging中这两个人也各有同日2事件；不是拿CS gold数据反证agent可见的P。',
 seen='event1完整契约明确multiple events on a day do not change this count；event11→12看raw schema及每表1行样例，event31→32只DESCRIBE本表和event表；event15写出COUNT表达式。全部43事件未找到(person_id,source_relation,day)重复频数核实。最终event41提过事件重复保留/计数，但未核实或处理本表连接的日粒度放大。',
 p='P：按(person_id,source_relation,occurred_on)连接事件后，date spine每一天最多得到一行，因而连接后count(*)仍是天数。017-V3在agent留存staging反证两组各2行；原契约也提醒同日可能多事件。U3按手册“证据曾出现但被忽略”例外处理；U4由单项计数修正L0全匹配满足。',
 rules='也可读为C（没有算对缺失天数）或I（COUNT写错）；本次选U，因为契约给的是指标性质和多事件提醒，没有指定COUNT表达式，错误成立依赖可直接核实的连接基数。没有明确的正确COUNT实现意图，不仅凭想算missing_day_count就归I。新增字段记“已提到”只表示确有重复处理声明，不等于核实过P。'),
22:dict(cat='A',confidence='中',factors='A：窗口分组的id约定，独立修改5043→4818行',flags='无',cost='需要查业务说明',primary=['source_id_projection'],u4='是：投影来源单改5043→1833行，减少63.7%；不是U',
 desc='agent把subscription_id作为输出和latest分组键，gold改取历史行id；输出身份约定和窗口粒度均不同。',
 reason='已核实：raw3500行，id唯一3500个，subscription_id为1667个；两列3495行不同。subscription_id能关联订阅主表3500行，id只能2500行。契约仅写History of subscription status changes及输出字段类型，未指明输出id来源或latest分组表达式。agent的FK选择有数据支持，不能因gold选历史行id就判U。单改输出投影使5043行/13087格降为1833行/1833格；单改窗口分组使4818行/12150格，两处分别归A。删除标记均false，单加过滤不改善。',
 seen='event9→10展示raw.subscription_history中id、subscription_id、status、时间及删除标记列；event11选subscription_id并增加时间/id排序。event19移除未在契约规定的删除过滤；event33解释此类过滤的取舍，但没有讨论本表id来源和latest粒度。未找到两id关联核实。',
 p='数据能够显示两个id并不等价、FK候选关联更完整，但目标契约没有明确定义是订阅实体还是历史行身份，不用gold的选择构造错误P。',
 rules='投影与窗口分组都来自同一未规定身份约定，但在SQL中是两个可单独改动的落点；本次分别量化，不把联合修改效果归给任一项。可把gold的历史id选择读成语义问题；没有明确source_expression或FK约束，保守归A而不扩大O。'),
23:dict(cat='多因并列（A、O）',confidence='高',factors='无；impressions默认值控制无改善',flags='无',cost='需要查业务说明',primary=['url_route','followers_representation'],u4='是：各减少138/276格；url_route首次整表匹配L1，非U',
 desc='两种未指定的Facebook URL路由不同，另有契约BIGINT与gold DOUBLE表示差异，各138格并列。',
 reason='已核实：固定2025-10-17共同日期，双方138行，URL与page_followers各138格不同。契约URL仅要求https://facebook.com/前缀模式，没有规定/page/posts/id路径；agent与gold构造均符合此前缀，归A。page_followers明定BIGINT，agent遵守，gold输出DOUBLE；raw fan_count无小数，L1格式归一后这138格消失，归O。两项单修L0行数均138、格子276→138，按v1并列。URL单改在L1整表匹配；另改impressions为契约默认0不改变结果，不列参与因素。',
 seen='event13→14、15→16读契约；event23→24查全部raw schema及样例（未截断），包括page id/fan_count；event29生成URL简写和BIGINT转换。event55最终报告讨论时间窗造成空表，但没有讨论本次日期控制后的URL路由或page_followers类型差异。',
 p='URL路径选择无法由raw列数值决定；整数粉丝数转换遵守类型要求。不存在满足U条件的错误数据假设。',
 rules='主因比较沿016使用L0规模，故A与表示层O并列；若先在L1归一后再挑主因会只剩A，手册未指明主因层级，本次公开L0–L3而不暗换尺度。时间窗已共同固定，不把原运行时空表再算作本表剩余错误。'),
24:dict(cat='A',confidence='中',factors='无',flags='无',cost='需要查业务说明',primary=['email_pattern'],u4='是：单换正则1行/1格→0，L0匹配；非U',
 desc='email正则的域名接受范围不同：agent把adv12@sub..example.com置NULL，gold保留。',
 reason='已核实：200行仅ID12的email不同。agent模式要求各域名段非空，gold的[a-z0-9.-]+接受连续点；017-V1对同一可见值分别返回false/true。只替换这一处模式便L0匹配。契约写standard pattern (local@domain.tld)，没有给出可执行的完整模式或边界例子；本次把正则边界未指定归A，中把握，不把agent拒绝该值说成未发现异常。',
 seen='event15→16看EMAIL列及前2行fake-email样例，不能据此说看过ID12；event23写正则，event31→32看到生成SQL；event49→50查到189/200 email非NULL。event63只泛述可选邮箱校验失败置NULL，没有点名连续点域名或两种正则边界。',
 p='agent明确使用更窄的匹配集合；没有“所有源email都有效”的依赖。单改能匹配gold不是U证据。',
 rules='可读为O（若standard pattern已唯一排除连续点），也可读为A（没有指定可执行正则）。本次不自行引入额外邮件规范作为契约，选择A。这里不裁定现实邮件地址是否可投递，也不评价gold边界设计。'),
25:dict(cat='C',confidence='中',factors='C：user_phone_number预修复，单改2492→2483行',flags='无',cost='一条查询',primary=['contact_phone_no_repair'],u4='否：所选行数口径最大仅2492→2482行',
 desc='电话格式失败本应置NULL，agent先去符号并补+1再验证，两个电话列保留了gold置空的值。',
 reason='已核实：raw2500行，from/to无值直接满足^\\+1[0-9]{10}$；agent修复后分别2490/2491行可通过。共同运行日期筛选后2492行，user/contact分别2482/2483格不同。契约规定格式不符nullify_field，未规定先重写或推断国家码；agent增加repair阶段，归C。去掉contact修复后行数2492→2482，去掉user修复后→2483，故按行数选择contact主因，user为C参与因素。不把格子下降一半冒充本表所选行数口径的U4。',
 seen='event15→16已展示call_data.from/to不含+的样例；event17写预清洗及补+1表达式；event23→24查询本表user_phone_number分布，看到NULL10条和多个+1号码。event41解释的是outgoing_caller_id另一表的过滤，不是本表call补号码的选择。',
 p='数据格式并非完全未见：轨迹已展示不符合原样模式的源值。主要问题是将明确的nullify失败处理改成先repair，而非漏查是否含+。',
 rules='也可把表描述standardized phone fields理解为允许预清洗而归A；本次优先字段级显式RLIKE规则和nullify_field行为。两个号码列共享同类实现，但单独删除各自repair量化影响；不合并两处人为达到U4。raw.twilio_call_data的命名与实际raw.call_data不同，双方SQL均使用后者，未成为本次差异原因。'),
26:dict(cat='O',confidence='高',factors='无；未评分的conversion占位不参与本次归因',flags='无',cost='一条查询',primary=['date_cast'],u4='是：单改为DATE后L0匹配；原基线只在L3匹配不单独证明U4',
 desc='1500行date_day只差TIMESTAMP午夜与DATE表示；agent遵守契约TIMESTAMP，留存gold是DATE。',
 reason='已核实：raw日期1500行均可解析且全为午夜；agent输出TIMESTAMP，留存gold类型DATE，L0–L2各1500行/1500格，L3已整表匹配。只把投影类型改DATE便L0匹配，属评测类型/表示与契约不一致的O。诊断还确认当前引擎执行gold文件的date_trunc(day,try_cast(... AS TIMESTAMP))表达式类型也是TIMESTAMP，因此不能假定SQL文件和留存gold类型完全一致；本轮date_day_type对照确实无改善。',
 seen='event9→10看到了本表date为VARCHAR及2022-05-10、2022-12-15样例；event13选择TIMESTAMP，event25只把intermediate的date_day改DATE。event37提到缺失conversion字段，但那些字段不在本表官方比较列；没有明确说明本表DATE/TIMESTAMP取舍。',
 p='所有本表源日期都能直接解析并且没有时分秒信息，不成立错误P；也没有依据把未评分的NULL conversion列当本次D主因。',
 rules='本表013仍列待标注，但本次复核发现L3已经完全一致。按用户指定对象完成O标注，原004–016状态和记录不改。留存gold与当前gold SQL的类型差异已记录，不猜测是版本、执行路径还是文件演变造成。'),
27:dict(cat='O',confidence='高',factors='无',flags='无',cost='多条查询',primary=['account_keep_duplicates'],u4='是：单取消account去重209行/4807格→0，L0匹配；非U',
 desc='agent为满足line_item_id唯一性对重复account_code取一行，gold保留一对多连接，额外产生209行。',
 reason='已核实：契约grain及line_item_id tests明确每id恰好1行。CS下agent5000行、gold5209行，209个line_item多出1行；移除account_by_code的QUALIFY就L0匹配，说明差异仅来自该去重。agent并非假定account_code唯一：event27→28已查出重复及5209/5000规模，event29才新增按最低account_id选1行。gold重复输出与契约唯一要求矛盾，归O；agent选择哪组账户属性仍有未规定部分，但本次删除去重的完整对照足以定位判错差异。',
 seen='event27→28分别查输出重复、staging account_code重复及源line_item5000行；event29加入确定性去重；event31→32验证5000个唯一id。event41明确披露选择lowest account_id并会丢弃冲突账户属性。',
 p='P“account_code唯一”已被agent亲自查否并处理，不能归U。说明了选择与代价，也不能按无解释占位/降级归D。',
 rules='契约一方面要求one row per line_item_id，另一方面叙述left join accounts；冲突码如何选未写明。以明确unique/grain要求识别gold的209行额外输出为O；A可描述保留哪组属性的未定约定，但不能把该约定直接改写为本次未通过核实的U。'),
28:dict(cat='不可评估',confidence='高',factors='不适用',flags='无',cost='判断不了',primary=[],u4='不适用：不同原始输入，只有基线诊断，不做U干预判定',
 desc='agent/初始只有youtube_channel_demographics_data的2509行，gold另用channel_demographics_a_1的9450行，原始内容不相交。',
 reason='已核实：015三方库存显示agent与初始同名raw一致，二者没有契约/gold引用的channel_demographics_a_1；gold反而没有agent那张youtube_channel_demographics_data。017诊断按相同7个业务列对齐比较，agent/初始多重集合一致，agent2509行与gold9450行完全不相交。输出基线行规模11959、格子83713。符合2026-10-29用户补充第一种情况，标不可评估；不把输入缺失判C/U，也不用改百分比或年龄映射来掩盖输入差异。',
 seen='event21→22列出实际raw表，仅有youtube_channel_*_data等；event23→24看schema与样例；event25选择可用的demographics表；event33修run.py raw-schema导入；event37→38和45→46查看结果行数。event57最终报告讨论channel_basic/video缺失字段，但未明确解释本表替代源名或与gold输入差异。',
 p='不能用gold的9450行和百分比尺度反证agent所见2509行的P；二者数据源不可比，归因在可评估性步骤停止。',
 rules='2026-10-29用户确认：agent=初始≠gold，诊断后不可评估；gold=初始≠agent则照常标注。此表属于前者。契约表在agent/初始缺失而gold存在也属于来源不一致，不只检查双方同名表。新增不确定性字段仍照常记录轨迹事实，不让“不可评估”替代该字段。'),
29:dict(cat='A',confidence='中',factors='无；删除标记控制不改善',flags='无',cost='需要查业务说明',primary=['date_prefix'],u4='是：单取日期前缀后1行/1格→0，L0匹配；非U',
 desc='一个start_date为2022-12-291163029，agent整串TRY_CAST为空，gold截前10位得到2022-12-29。',
 reason='已核实：51行中仅id1163027不同；原文为2022-12-291163029，end_date为2022-12-29。这不是仅TIMESTAMP/DATE显示差异，而是包含尾部数字的畸形输入。契约仅声明start_date DATE，没有指定截前缀或恢复污染值。agent用安全转换失败置NULL，gold截前10位；数据能发现异常，但不能唯一确定尾部数字应丢弃的恢复规则，因此归A。单改前缀解析即L0匹配；补删除过滤无影响。',
 seen='event17→18查看start_date为VARCHAR的schema，没有查询本表日期样例；event21生成TRY_CAST；event41→42只核对各表列名/类型。event55最终报告明确可选字段转换失败成为NULL、未追加文本规范化，但未点名该异常日期。',
 p='不能把使用TRY_CAST本身当成相信所有源值有效：它明确允许失败返回NULL，最终报告也说明此策略。异常值存在不等于可以从数据独立确定该采取截前缀而不是置NULL。',
 rules='可读为U（未查到格式异常）或A（异常恢复策略未给）。选择A，保持与016的解析策略处理一致；本列无not_null或source_expression要求，且源值含多余数字，不能仅凭gold实现补定规则。已提到档位仅表示全局可选字段失败策略适用于本表，不声称agent读过这一行。'),
30:dict(cat='多因并列（X、O）',confidence='中',factors='C：created_date错误非空过滤（减少175格）；O：amount_without_tax及其home_currency表示（各1035格）、exchange_rate_date和target_date表示（各1035格）、balance表示（5格）',flags='无',cost='多条查询',primary=['account_source','adjustment_amount_representation','credit_balance_adjustment_amount_representation','credit_memo_amount_representation','exchange_rate_representation'],u4='否：所选L0格子口径最大仅1040/9565，所有单项都未达一半，且L0–L2均未整表匹配',
 desc='account_id误取invoice id与四项数值表示差异各1040格并列；另有日期/金额类型差异及错误丢弃5条空日期记录。',
 reason='已核实：同用2025-10-13共同时间后agent1040行、gold1045行，行规模1045、格子9565。account_id来源、adjustment_amount、credit_balance_adjustment_amount、credit_memo_amount和exchange_rate五项单修均减1040格且行数不降，按v1并列。四项数值表示中agent遵守DOUBLE、gold保留VARCHAR，归O；account来源错误可见数据已明确：raw.account_id关联账户1999行、raw.id关联0行。该项具备U前三项证据但单改仅减1040格，不满足U4；轨迹也不足以确认agent原本知道本表FK应保留而只是手误，故此并列原因暂记X。其他类型干预分别减少1035或5格，归O参与因素。契约row_filter明确允许created_date不可解析，agent额外要求非空；恢复OR NULL分支使5条保留，格子减175，记C参与因素。',
 seen='event13→14最初看到打包CSV式列名；event39→40已显示解析后的invoice同时有id与account_id。event44显示通用同名列fallback；event45把多种*_id统一放进pk_alias并映射id，未限定所属表；event71最终报告明确声称Fivetran id映射实体标识。未找到invoice.account_id与账户主表的关联核实，也未找到本表外键保留的明确正确意图陈述。',
 p='P：对invoice记录，raw.id可以作为该发票的account_id并与账户主键关联。017-V1给出raw.account_id匹配1999行而invoice id为0（2004行总数），源列区分可被数据明确核实。未见agent执行此核实。但account_source单改L0仅9565→8525格，L1/L2也未整表匹配或减半，U4失败。X表示这个已定位错误的类别门槛未满足，不是说差异位置不明。',
 rules='U前三项成立、单改有效但与其他最大项并列且不到一半：第4节只放宽“除主因之外”的参与因素，不能借该例外把并列主因硬记U。故记X并列，建议手册明确此边界。也可读为I（pk_alias范围写错），但同名fallback被有意覆盖不足以证明本表正确意图，本次不据变量名推断。所有主因按L0比较；若先归一格式再选会改变权重，公开各档结果但不改手册。固定时间控制从所有运行共同剥离原留存1条日期边界差异，不能把它计入某个字段干预。')}

SUPPLEMENT='2026-10-29用户确认补充：本表依赖原始表若agent留存与初始一致而gold不同，先诊断再标不可评估；若gold与初始一致而agent不同，则正常标注并追踪agent运行中的改动。不能把两种情况混淆。raw差异须限定到本表依赖；CS上游用gold。'

def main():
 dest=REC/'017_annotations';dest.mkdir(exist_ok=True);rows=[];unc=json.loads((REC/'017_uncertainty_audit.json').read_text());audit=json.loads((REC/'017_dependency_raw_audit.json').read_text());diagnostics=json.loads((REC/'017_diagnostics.json').read_text())
 for n,a in A.items():
  task=f'impl-{n:03}';pkg=package(n);b=pkg['differences'];r=json.loads((REC/f'017_reruns_{task}.json').read_text());base=r['runs'][0]['comparison']['levels'][0];queries=json.loads((REC/f'017_queries_{task}.json').read_text());u=unc[task]
  count=len(queries);assert count<=5
  slim=next((REC/'013_packages').glob(f'013_{task}_*.md'));block=pkg['contract_specification']['blocks'][0]
  lines=[f'# {task} / {b["table"]}','','## 1. 错在哪里','',a['desc'],'',a['reason'],'','## 2. 依据','',f'- 起点：[013精简材料包](../013_packages/{slim.name})；不修改既有官方判错状态。',f'- 契约：`{pkg["contract_specification"]["source_path"]}` 第{block["start_line"]}–{block["end_line"]}行。',f'- [完整轨迹](../017_trace_{task}.json)，保留事件原文和原始路径；可回查授权归档`traces/dacomp_deimpl_prev.tar.gz`。',f'- [查询原文及结果](../017_queries_{task}.json)、[重跑完整记录](../017_reruns_{task}.json)、[原始表库存](../015_raw_{task}.json)。','- [新增不确定性字段审计](../017_uncertainty_audit.json)、[本表依赖raw核对](../017_dependency_raw_audit.json)。','- [执行前指纹](../017_input_before.json)、[结束后指纹](../017_input_after.json)。本次前快照完成后才开始标注、查询和重跑。','','### 契约原文','', '```yaml',block['original_text'].rstrip(),'```','','### SQL定位','']
  if n==25:
   lines.insert(lines.index('### 契约原文'), '轨迹导出例外：event16样例中的两处Twilio账户标识因GitHub push protection拦截已脱敏，其他事件内容保留；[脱敏位置与原文校验信息](../017_trace_redactions.json)。data/原始轨迹未改，引用的电话证据不涉及脱敏位置。\n')
  for label,key in [('agent','agent_final_SQL'),('gold（仅用于定位差异）','gold_SQL_仅供定位差异')]:
   p=Path(pkg[key][0]['path']);lines += [f'{label}：`{p}`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。','```sql']+[f'{i:4}: {s}'.rstrip() for i,s in enumerate(p.read_text().splitlines(),1)]+['```','']
  lines+=['### 原始数据可评估性','', '下表复用015的完整表schema/行数/typed行哈希比较，只列本表静态传递依赖及双方SQL直接引用的raw。缺表不当作空表；gold与agent一致但二者不同于初始不自动排除（021/030）。','', '|依赖raw|比较|类型/列序相同|行数相同|typed行哈希相同|差异原因|','|---|---|---|---|---|---|']
  for x in audit[task]['comparisons']:lines.append('|'+x['raw_table']+'|'+x['comparison']+'|'+str(x['ordered_columns_and_types_equal'])+'|'+str(x['row_counts_equal'])+'|'+str(x['sorted_content_hash_equal'])+'|'+','.join(x['difference_reasons'])+'|')
  if n==28:lines+=['','[028输入诊断SQL及结果](../017_ineligible_diagnostic_impl-028.json)：同名表存在性、日期范围、完整表哈希复核、语义列多重集合对比。']
  lines+=['','## 3. agent看过什么','',a['seen'],'','只把归档实际展示的内容视为已看到；磁盘有文件、命令包含表名或截断掉的部分，不等于看到相应数据值。','','### 新增字段：是否意识到或提到相关不确定性','',f'**{u["status"]}**。只记录可见表述/信息，不由该档位推定错误类别。','',u['scope_limit'],'']
  for ev in u['evidence']:
   lines += [f'event **{ev["event"]}**，字段`{ev["field"]}`；原路径`{ev["path"]}`。','```text',ev['quote'],'```','']
  lines+=['归档逐项扫描'+str(u['scanned_event_count'])+'个事件；本批thought/args.thought字段均为空，不能由此推断agent没有内部思考。“已提到”的原句来自final_thought中的最终报告；“看到了但没提”依据可见工具返回，不把SQL代码本身当口头说明。长工具输出仅摘录连续原文，截取范围见JSON；不是说agent只看到了这个摘录。','','## 4. 查询与重跑','',f'核实查询执行 **{count}条**（失败尝试也计入）；核实代价档：**{a["cost"]}**。每张≤5条，均只查agent当时可见数据。诊断可以查gold，不计入此数。','']
  for q in queries:
   lines += [f'### {q["id"]} / {q["kind"]}','',f'数据库：`{q["database"]}`。','```sql',q['sql'],'```','结果原文：','```json',json.dumps({k:v for k,v in q.items() if k not in ['id','kind','sql','database']},ensure_ascii=False,indent=2,default=str),'```','']
  if not queries:lines+=['本表无核实P的查询；不可评估诊断见下面。核实代价“判断不了”指无法在同输入条件下估计正常核实代价，并非未查到输入差异。','']
  for i,q in enumerate([x for x in diagnostics if x['task']==task],1):
   lines += [f'### D{i} / 诊断查询','',f'数据库：`{q["database"]}`。','```sql',q['sql'],'```','```json',json.dumps({k:v for k,v in q.items() if k not in ['task','kind','sql','database']},ensure_ascii=False,indent=2,default=str),'```','']
  if n==28:lines += ['### 不同输入诊断','', '```json',(REC/'017_ineligible_diagnostic_impl-028.json').read_text().rstrip(),'```','']
  lines += ['### 比较口径','',METHOD,'',f'键：`{b["key_columns"]}`；原评分比较列：`{b["comparison_columns"]}`。与键取并集，不自行纳入原评分排除列。','', '全部原数据库以READ_ONLY连接或ATTACH；本次建表和改SQL只在`data/017_work/`。staging用agent留存raw，021/027用gold上游CS。每个试验从相同原SQL独立替换，不累积其他修复。', '', '共同时间控制：`'+json.dumps(r.get('clock_control',[]),ensure_ascii=False)+'`。023/025/028沿原筛查候选日期；030沿010已经验证的兼容2025-10-13日期（不声称唯一执行日）；共同控制先应用到基线及全部干预，不能作为某个局部修复的功劳。','', '|单项|L0行：前→后|L0格：前→后|首次整表匹配|','|---|---|---|---|']
  scales=[]
  for t in r['runs'][1:]:
   c=t['comparison'];x=c['levels'][0];lines.append(f'|{t["label"]}|{base["row_scale"]}→{x["row_scale"]}|{base["cell_scale"]}→{x["cell_scale"]}|{c.get("first_match") or "无"}|');scales.append(f'{t["label"]}:{base["cell_scale"]}→{x["cell_scale"]}')
  lines+=['','### 原留存输出基线','',results(r['retained']),'']
  for t in r['runs']:
   lines += [f'### 重跑 {t["label"]}','',f'SQL：`{t["sql_path"]}`；SHA-256：`{t["sql_sha256"]}`。','']
   if not t['edits']:lines+=['同输入、同时间控制、不增加因果改动的基线。','']
   for e in t['edits']:lines+=['唯一替换位置offset='+str(e['offset'])+'；原文：','```sql',e['old'],'```','新文：','```sql',e['new'],'```','']
   lines += [results(t['comparison']),'']
  lines += ['## 5. 类别、把握和对比','',f'- 主要原因：**{a["cat"]}**（归因判断）。',f'- 主因单项：{", ".join(a["primary"]) or "不适用"}。',f'- 参与因素：{a["factors"]}。',f'- 标记：{a["flags"]}。',f'- 把握：**{a["confidence"]}**。',f'- 重跑是否满足U第4条件：{a["u4"]}。','',a['p'],'','与014相比是否变化：不适用（第三批首次标注）；也未修改016任何结论。','','## 规则问题','',a['rules'],'',SUPPLEMENT,'','新增字段统一口径：记录与实际差异机制相关的明确选择/可疑数据表述；不要求agent预知gold，也不把泛称“完成清洗”算作识别具体边界。021关于重复计数、029关于可选字段失败置NULL为适用范围较广的声明，单独注明并未点名本表异常；可见证据只能支持这一有限范围。该字段不增减U/C/D/I/A/O/X条件。','']
  (dest/f'017_{task}_{b["table"]}.md').write_text('\n'.join(lines))
  mention=next((e for e in u['evidence'] if e['field']=='args.final_thought'),None)
  uncertainty=u['status']+('；event '+str(mention['event'])+'：'+mention['quote'] if mention else '；可见信息事件 '+','.join(str(e['event']) for e in u['evidence']))+'；范围：'+u['scope_limit']
  rows.append(dict(zip(['题目','表','一句话描述','主要原因类别','参与因素','标记','把握','核实查询条数','核实代价档','重跑是否满足 U 的第 4 个条件','格子数口径规模变化','与 014 相比是否变化','agent 是否意识到或提到了与本表差异相关的不确定性'],[task,b['table'],a['desc'],a['cat'],a['factors'],a['flags'],a['confidence'],count,a['cost'],a['u4'],'；'.join(scales) or f'仅基线{base["cell_scale"]}，不可评估','不适用：第三批首次标注',uncertainty])))
 with (dest/'017_summary.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
 save(REC/'017_decisions.json',A);print('Wrote',len(rows),'annotations')
if __name__=='__main__':main()
