"""Reviewed decisions; labels come from manual review, numeric ranking from isolated runs."""
import json,glob
from pathlib import Path
R=Path(__file__).resolve().parents[1];REC=R/'records'
inv=json.loads((REC/'023_package_inventory.json').read_text());dec=[]
def add(t,cat,summary,main,unc='看到了但没提',evidence='',confidence='高',rule='无',flags=None,extra=''):
 r=next(x for x in inv if x['table']==t);dec.append(dict(task=r['task'],table=t,layer=r['layer'],purpose=r['purpose'],category=cat,summary=summary,main_labels=main,uncertainty=unc,uncertainty_evidence=evidence,confidence=confidence,rule_question=rule,flags=flags or [],extra=extra))
add('quickbooks__general_ledger','O','差异限于契约明确允许 engine-defined 的并列窗口累计顺序；排除两列累计后含键整表一致。',[],evidence='event 1 契约已说明 window ties；event 33 写出相同排序键的 ROWS 累计窗口；event 73 未说明本表并列顺序。',extra='诊断见023_diagnostics：非累计列 L0 全匹配，存在窗口并列组。未通过追加排序键改变契约。')
add('stg_quickbooks__invoice_line','I','初始映射使用 sales_item_item_id，后来的 special 映射将其覆盖成全空的 item_id。',['item_mapping'],evidence='event 15/16 看过两候选列；event 17 rawmap 先写 sales_item_item_id→sales_item_item_id；event 21 special 覆盖为 item_id，未解释本表选择。',confidence='中',rule='I/U 两种读法：若把 special 映射视为有意选列，可读作 U；本次依手册允许的代码自身证据（正确映射随后被覆盖）选 I。核实所选列0/20000非空、另一列20000/20000且全部匹配 item_data。')
for t,label,summary in [('stg_quickbooks__payment_line','linked_id','存在 invoice_id 候选列，却将 linked_txn_payment_id 整列置 NULL。'),('stg_quickbooks__vendor','vendor_name','存在 display_name 等名称候选列，却将 name 整列置 NULL。')]:
 add(t,'D',summary,[label],'只有通用策略说明','event 15/16 已看到源列清单；event 21 仅按原同名列是否存在走 NULL fallback，未判断候选映射。event 73：「对原始字段中不存在的合同字段采用类型化 NULL」。这是跨表占位策略，非本表映射理由。',flags=['已披露'])
add('int_workday__organization_metrics','C','avg_tenure_days 从仅当前 assignment 的 current_stats 取值，违反契约要求覆盖历史与当前 assignment。',['tenure_all_assignments'],evidence='event 1 契约明确 all assignments；event 25 生成 current_stats 取值；event 55/56 观察当前 assignment 为0。event 83 仅解释当前 headcount，不解释历史任期被排除。')
add('workday__employee_overview','O','主要差异是 gold 的 grade 正则未提取数字，agent 的 compensation_tier 符合契约；另有 compensation 回接重复度 C 因素。',['compensation_regex'],evidence='event 15/16 已查看 job_profile 列清单；event 31 写 compensation_tier 数字提取；event 83 实施清单未讨论该正则或回接重复度。',extra='comp_ebe_join 为有效单处 JOIN 干预；初轮 comp_base_multiplicity 未按 worker 约束复制，扩大错误，已排除归因。按第5节行数优先，O 单改减少51965行，C 单改行数不变但格数显著减少。')
add('workday__position_overview','O','gold 的 grade 正则不提取数字是主因；agent 仅从 active organization metrics 读取组织维度造成额外缺失。',['compensation_regex'],evidence='event 15/16 已查看 job_profile/organization 列；event 51 写岗位模型；event 83 未解释 grade 正则及省略非 active 组织维度。',extra='organization_dimension 为 C 参与因素；organization_id/similar_group 干预未减少规模，不列参与因素。')
add('stg_workday__position','C','先 trim 再按枚举校验，使两条原始值不合法的 employee_type 被保留。',['validation_order'],evidence='event 1 提供枚举原式与 trim 规则；event 19/20 读取 position 样例；event 21 生成 SQL。event 83 的 applied cleaning 工作清单不计通用策略。',rule='先 trim 再校验也可视为规则次序歧义；本次按第3节可执行原式的字面值校验，归 C，未改手册。')
add('greenhouse__application_history','O','最后区间使用运行时刻；共同固定到 gold 的时刻后 L2 全匹配，剩余 L0 为等价时长计算的浮点尾差。',[],evidence='event 1 契约说明最后区间 time-variant；event 23 生成区间 SQL；event 53 未对本表时间选择作说明。',extra='023_history_clock 固定到 gold max(valid_until)；基线本身首次 L2匹配。未把运行时间变化当作单独错误点。')
add('greenhouse__job_enhanced','C','days_since_created 使用 current_timestamp 而契约指定 current_date；另有 prospect 预转 VARCHAR 与 gold 未补零比率的差异。',['days_clock'],evidence='event 1 契约明确 current date 和 prospect 比较原式；event 21/23 生成模型；event 53 的层级实施清单不计通用策略。',extra='prospect_cast 为C参与因素；ratio_zero_vs_null 为O参与因素：契约要求count先默认0，gold直接使用NULL原聚合。')
for r in inv:
 if r['task']=='impl-017' and r['layer']=='staging':add(r['table'],'O','agent 按契约 primary_key/unique 去重，gold 保留重复；移除去重后按评测列和键 L0 全匹配。',['uniqueness'],'只有通用策略说明','event 1 提供主键声明；event 15/16 看过 raw schema/样例；event 17 统一生成去重。event 53：「staging 对声明为主键的空值行进行过滤，并按主键分组只保留一条记录以满足唯一性；若重复键的内容不一致，合同没有规定优先版本」。此为跨表处理策略，非实施清单。')
add('salesforce__daily_activity','C','对 Won 金额全 NULL 的8个日分组也补0，契约只对无 Won 的分组规定0。',['won_amount_null'],evidence='event 1 已给 Won/no-Won 的NULL语义；event 31 生成日活动 SQL；event 99 未说明此聚合边界。')
add('salesforce__team_performance','C','增长率 NULL 经 COALESCE 成0后多给5分，是行数口径最大主因；收入来源另有差异。',['health_growth_null'],evidence='event 1 已给增长率分支；event 33 生成模型；event 99 未讨论 NULL 增长率评分。',confidence='中',rule='team_total_revenue 与 avg_revenue_per_member 的收入源未明确列名，可读作 user_performance.total_won_amount 或 revenue_data.total_revenue_won，本次两处列为 A 因素；top_revenue_performer 明确 total won amount，按 C。',extra='top_win_rate_performer 的2个名称差异是契约允许的并列任意选择，023_team_ties 已确认4个候选均为组内最大0；作为剩余O诊断记录，未有单独减少规模干预，不计参与因素。')
add('stg_salesforce__contact','A','主要为 master_record_id 的 NULL 与空串选择；另13处字段默认选择各自独立构成 A 因素。',['null_empty_master_record_id'],evidence='event 17/18 查看 raw 列和样例；event 55/56 查看本表 SQL；event 99 未解释 NULL→空串选择。通用“无效字段置空”不覆盖这里合法的缺失值默认。')
add('stg_salesforce__contact_history','A','契约未规定评测历史键算法；agent 使用 ID/Fivetran 起止时间的 MD5，gold 使用 ID/运行时间串。',['history_key_clock'],'针对本表的具体说明','event 99：「History 源数据没有契约所需的 history_unique_key 原始列，因此以实体记录 ID 与 Fivetran 起止时间生成确定性 MD5 键，用于稳定标识历史版本」。event 53/69 修复本表映射。',extra='共同固定到 gold created_date 后仅改键表达式，5434→566行；剩余566来自契约contact_id唯一性去重与gold保留重复。去重单改因键未对齐反增规模，不列参与因素。',rule='时间参与评测键且公式未规定：共同时间控制用于对照生成时刻，不把时间差另算原因；历史键公式仍作为一个 A 错误点。')
add('stg_salesforce__lead','A','主因是 master_record_id 的 NULL/空串默认；其他字段默认、日期范围、gold 状态规则与契约不一致形成独立因素。',['null_empty_master_record_id'],evidence='event 17/18 查看raw；event 89/90 检查契约；event 99 未解释 master_record_id 默认。',extra='范围额外清洗不是直接硬约束结论；annual_revenue 主差为小数类型，L2已消失。status_value/status_filter 是gold与契约不一致的O；各处独立记录，不捆绑。')
add('stg_salesforce__opportunity','A','lead_source 与 type 两处可选字段 NULL/空串默认未由契约规定；前者行数减少更多。',['null_empty_lead_source'],evidence='event 17/18 查看raw；event 45/46 查看SQL；event 99 未解释这两个字段缺失默认。')
add('stg_salesforce__order','I','account_id 被写成订单自身 id；轨迹已明确意图应保留 FK 列，但 order 未被该修正覆盖。',['account_mapping'],evidence='event 57 注释：「Correct field source mapping; canonical foreign keys should remain FK columns, not the row\'s own id.」；event 67/68 查看各staging首列；event 99 未说明 order 留有这处错误。',extra='原始数据核实：订单id与account表0匹配，account_id有894匹配；分类依据是轨迹中明确正确意图，因此用I，不用U。')
for t,main in [('stg_salesforce__task','status_filter'),('stg_salesforce__user','email_filter')]:add(t,'O','agent 执行契约显式删除规则，gold 保留违反规则的记录。',[main],'只有通用策略说明','event 1 提供校验表达式；event 17/18 查看raw；event 99：「严重问题按契约删除行或过滤软删除数据；非关键字段中的无效关系键、格式值或数值按契约置空」。这是实际条件处理策略，不取实施清单。',extra='user 长邮箱删除另有单独O因素；email NULL 与regex/length过滤相互遮蔽，单放开not_null不减少规模，不列因素。' if t.endswith('user') else '')
add('apple_store__app_version_report','A','session metrics 的 NULL 连接键使用 null-safe 相等，gold 使用普通等号；契约未说明该边界。',['join_ses'],evidence='event 11/12 看过raw和各source信息；event 15 后续模型生成session join；event 63 未解释NULL键相等策略。“聚合保留NULL”不等于解释join NULL语义。')
add('apple_store__territory_report','A','sessions 的 NULL 键连接是主因，downloads 的 NULL 键连接为另一处 A 因素。',['join_ses'],evidence='event 15 及后续模型命令生成null-safe joins；event 63 未解释NULL键连接选择。',extra='ip/dl/ins/ses 预聚合与契约“不聚合”不符，但各自单改规模均不减少，故不列参与因素；也不误标为U。')
add('stg_apple_store__app_session_daily','O','gold 双反斜杠版本正则拒绝契约允许的三段数字版本；另有日期解析格式范围 A 因素。',['semver_regex'],evidence='event 1 契约给版本正则；event 11/12 读取raw；event 63 会话staging过滤工作清单未解释三段数字正则边界，故不计通用策略。',extra='固定同一时间后基线7行/68格；版本单处改为gold行为降为3行/24格。日期三处过滤各自单改均降1行/2格；不能把它们打包算一个错误点。',rule='同一日期解析重复出现在不同代码位置，按用户本轮口径逐处计；它们存在交互，单点结果相同，分别记录。')
add('int_intercom__conversation_part_aggregates','U','从part聚合驱动并内连接conversation，依赖每个conversation都有part的假设，丢弃无匹配part的对话。',['conversation_coverage'],evidence='event 39/40 已看到 conversation 6703 与 part aggregates 977；event 61 报告同样给出977而未解释覆盖缺口。',flags=['证据曾出现但被忽略'],rule='“For each conversation”可理解为明确规定全量驱动（C），也可理解为实体粒度而未指定连接实现（U）。本次选U：关键依赖是每个conversation存在part，agent可见数据明确反证；单改驱动连接后CS L0全匹配。',extra='P：每个conversation均有part。核实可见库5726个conversation无part；CS上游0匹配，漏6703。U前三条件满足（已见行数反证却忽略）；单点6703→0，满足第4条件。初轮left_conversation仅保留part方向，非正确coverage修正，排除。')
add('intercom__company_metrics','A','三处 contacts 指标分别选择缺失补0，gold保留NULL；契约没规定缺失默认，三处同类别并列。',['contacts_total','contacts_active_7d','contacts_active_30d'],evidence='event 39/40、43/44 看到company metrics 2509行及字段；event 61 未解释缺失contacts聚合补0。清理逻辑清单不作策略证据。')
add('stg_intercom__contact_history','O','agent 按契约显式 E.164 正则保留1079条合法号码，gold双反斜杠正则拒绝这些号码。',['phone_gold_regex'],evidence='event 21/22 读取raw；event 45 修改本表不推断无+前缀的国家码；event 61 的“电话满足E.164”是验证清单，未说明差异涉及的regex转义。')
add('stg_intercom__conversation_contact_history','O','raw两列值域错位；agent按数据关系映射并输出BIGINT conversation_id，gold同名透传为VARCHAR，与契约类型不符。',[],evidence='event 21/22 可见两列与主表值域；event 25 生成交换映射；event 61 只解释conversation part错位，没有说明本映射表选择。',rule='两个评测键均不同，逐处改一列都不减少行/格规模；主因不能按正改善排序，但契约BIGINT与gold VARCHAR矛盾已直接核实，按第3节归O，不因交互改成X，也不打包两处修改。',extra='核实：raw.contact_id全部4033可转BIGINT，raw.conversation_id全部不可转；后者与contact主表4024匹配，同名contact_id为0匹配。gold列类型诊断见023_diagnostics。')
add('int_klaviyo__events','O','相同person/timestamp并列顺序导致lag归属不同；gold还有session_seq=0，与契约从1开始不一致。',[],evidence='event 1 契约明确时间并列engine-defined且session从1开始；event 13/33 写session窗口；event 41 未说明并列排序。',extra='gold有2组各2条同person同timestamp；除窗口派生列外L0全匹配。O依据包含明确session起点冲突，不能仅以任意排序解释0。')
for t in ['stg_klaviyo__campaign','stg_klaviyo__flow','stg_klaviyo__metric']:
 add(t,'O','agent按契约ID not_null过滤，gold保留NULL ID；仅放开该过滤后L0全匹配。',['null_id_filter'],'只有通用策略说明','event 19/20、23/24 显式查看raw ID非空计数；event 41：「无效关键 ID 和非法邮件记录被排除」。这是跨表条件处理策略，非工作清单。')
add('stg_klaviyo__event','O','gold 双反斜杠邮箱正则拒绝2496条普通合法邮箱记录，agent按契约保留。',['email_regex'],'只有通用策略说明','event 11/12 看过raw样例，event 27/28、29 显式排查邮箱regex转义；event 41：「无效关键 ID 和非法邮件记录被排除」。未对本表与gold的转义差异作具体说明。')
add('stg_klaviyo__person','A','person_id没有非空要求，agent额外删除NULL ID行而gold保留；属契约未规定的过滤取舍。',['null_id_filter'],'只有通用策略说明','event 19/20、23/24 已看见person的ID大量为空；event 41：「无效关键 ID 和非法邮件记录被排除」。未专门说明person无not_null却过滤的选择。',extra='单改ID过滤1190行/19040格→1行/1格；剩余phone_number归一化差异只在原来被筛掉的行，未作为可独立改善的参与因素。full_name_null单改无改善，不列因素。')
# Load the locked blind decisions verbatim in substance; do not refit them to 018.
for b in json.loads((REC/'023_calibration_blind_decisions.json').read_text()):
 add(b['table'],b['category'],b['reason'],['country_projection'] if b['task']=='impl-009' else ['email_pattern'],b['uncertainty'],b['uncertainty_evidence'],b['confidence'],b['rule_question'],extra='盲标冻结文件023_calibration_blind_decisions.json；018仅在锁定后读取比较。')
 dec[-1]['blind_factors']=b['factors']
assert len(dec)==41
# Explicit reviewed overrides, leaving original experimental plans as execution history.
patchmeta={}
for filename in ['023_patch_plan.json','023_supplement_patch_plan.json']:
 for p in json.loads((REC/filename).read_text()):
  for x in p['patches']:patchmeta[p['table'],x['label']]=x
patchmeta['stg_quickbooks__invoice_line','item_mapping']['category']='I'
patchmeta['stg_salesforce__order','account_mapping']['category']='I'
excluded={'comp_base_multiplicity','left_conversation'}
for d in dec:
 runs=[]
 for filename in sorted(REC.glob('023_*reruns_'+d['task']+'_'+d['table']+'.json')):
  x=json.loads(filename.read_text());baseline=x['runs'][0]['comparison']['levels'][0]
  for r in x['runs'][1:]:
   if 'comparison' not in r:continue
   v=r['comparison']['levels'][0];dr=baseline['row_scale']-v['row_scale'];dc=baseline['cell_scale']-v['cell_scale']
   m=patchmeta.get((d['table'],r['label']),{})
   runs.append(dict(label=r['label'],record=str(filename.relative_to(R)),category=m.get('category','A' if r['label'] in ['country_projection','email_pattern'] else 'U'),reason=m.get('reason','见盲标记录'),row_reduction=dr,cell_reduction=dc,excluded=r['label'] in excluded))
 d['interventions']=runs
 d['factors']=[x for x in runs if not x['excluded'] and x['label'] not in d['main_labels'] and (x['row_reduction']>0 or x['row_reduction']==0 and x['cell_reduction']>0)]
 d['main_ranking']=[x for x in runs if x['label'] in d['main_labels']]
 # All ties with same category resolve directly to that category per manual §5.
 if d['main_ranking']:
  best=max((x['row_reduction'],x['cell_reduction']) for x in runs if not x['excluded'])
  assert all((x['row_reduction'],x['cell_reduction'])==best for x in d['main_ranking']),(d['table'],best,d['main_ranking'])
(REC/'023_decisions.json').write_text(json.dumps(dec,ensure_ascii=False,indent=2)+'\n')
print('decisions',len(dec))
