# impl-020 · intercom__company_metrics

用途：**全量**；层：`marts`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**A**；把握：高；主要错误点：contacts_total、contacts_active_7d、contacts_active_30d。

三处 contacts 指标分别选择缺失补0，gold保留NULL；契约没规定缺失默认，三处同类别并列。

参与因素：无。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-020_intercom__company_metrics.md](../023_packages/023_impl-020_intercom__company_metrics.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml`；SHA-256 `b19cdce65b55dd44086f5a7ef864055abfe48bd66f5d6f430785084ab3cd5314`。
契约行 1166–1285：

```
1166:     - name: intercom__company_metrics
1167:       description: "Company-level support and engagement KPIs aggregated across conversations and contacts."
1168:       grain: "One row per company_id"
1169:       source_models: [
1170:         intermediate.int_intercom__latest_conversation,
1171:         intermediate.int_intercom__conversation_part_aggregates,
1172:         intermediate.int_intercom__conversation_part_events,
1173:         intermediate.int_intercom__contact_company_history,
1174:         intermediate.int_intercom__contact_latest,
1175:         intermediate.int_intercom__company_history
1176:       ]
1177:       business_logic: >
1178:         Map conversations to companies via the first contact author and contact-to-company history.
1179:         Compute conversation totals, closed counts, average parts, and average rating for each company.
1180:         Derive conversion-by-channel counts and guarded conversion rates by dividing by the total number of contacts only when the denominator is positive.
1181:         Compute median time metrics per company based on per-conversation minutes and provide date continuity diagnostics using active day coverage within min..max ranges.
1182:         Provide active and retained contact counts based on 7-day and 30-day windows and registration-based retention ratios guarded by denominators.
1183:       columns:
1184:         - name: company_id
1185:           data_type: VARCHAR
1186:           description: "Company identifier."
1187:           tests: [not_null]
1188:         - name: company_name
1189:           data_type: VARCHAR
1190:           description: "Company name."
1191:           tests: []
1192:         - name: website
1193:           data_type: VARCHAR
1194:           description: "Company website."
1195:           tests: []
1196:         - name: industry
1197:           data_type: VARCHAR
1198:           description: "Industry classification."
1199:           tests: []
1200:         - name: plan_id
1201:           data_type: VARCHAR
1202:           description: "Plan identifier."
1203:           tests: []
1204:         - name: plan_name
1205:           data_type: VARCHAR
1206:           description: "Plan name."
1207:           tests: []
1208:         - name: total_conversations
1209:           data_type: BIGINT
1210:           description: "Total number of conversations mapped to the company."
1211:           tests: ["total_conversations >= 0"]
1212:         - name: total_conversations_closed
1213:           data_type: BIGINT
1214:           description: "Number of conversations in a closed state."
1215:           tests: ["total_conversations_closed >= 0"]
1216:         - name: avg_conversation_parts
1217:           data_type: DOUBLE
1218:           description: "Average number of parts per conversation."
1219:           tests: ["avg_conversation_parts >= 0"]
1220:         - name: avg_conversation_rating
1221:           data_type: DOUBLE
1222:           description: "Average conversation rating."
1223:           tests: ["avg_conversation_rating >= 0"]
1224:         - name: contacts_total
1225:           data_type: BIGINT
1226:           description: "Total number of contacts associated with the company."
1227:           tests: ["contacts_total >= 0"]
1228:         - name: conv_rate_overall
1229:           data_type: DOUBLE
1230:           description: "Conversations per contact overall (guarded by positive denominator)."
1231:           tests: ["conv_rate_overall >= 0"]
1232:         - name: conv_rate_email
1233:           data_type: DOUBLE
1234:           description: "Conversations per contact via email channel."
1235:           tests: ["conv_rate_email >= 0"]
1236:         - name: conv_rate_messenger
1237:           data_type: DOUBLE
1238:           description: "Conversations per contact via messenger channel."
1239:           tests: ["conv_rate_messenger >= 0"]
1240:         - name: conv_rate_other
1241:           data_type: DOUBLE
1242:           description: "Conversations per contact via other channels."
1243:           tests: ["conv_rate_other >= 0"]
1244:         - name: contacts_active_7d
1245:           data_type: BIGINT
1246:           description: "Active contacts in the past 7 days."
1247:           tests: ["contacts_active_7d >= 0"]
1248:         - name: contacts_active_30d
1249:           data_type: BIGINT
1250:           description: "Active contacts in the past 30 days."
1251:           tests: ["contacts_active_30d >= 0"]
1252:         - name: registration_retention_7d
1253:           data_type: DOUBLE
1254:           description: "Share of registered contacts retained at 7 days."
1255:           tests: ["registration_retention_7d BETWEEN 0 AND 1"]
1256:         - name: registration_retention_30d
1257:           data_type: DOUBLE
1258:           description: "Share of registered contacts retained at 30 days."
1259:           tests: ["registration_retention_30d BETWEEN 0 AND 1"]
1260:         - name: p50_time_to_first_response_min
1261:           data_type: DOUBLE
1262:           description: "Median minutes to first admin response across the company's conversations."
1263:           tests: ["p50_time_to_first_response_min >= 0"]
1264:         - name: p50_time_to_first_close_min
1265:           data_type: DOUBLE
1266:           description: "Median minutes from first contact reply to first close."
1267:           tests: ["p50_time_to_first_close_min >= 0"]
1268:         - name: p50_time_to_last_close_min
1269:           data_type: DOUBLE
1270:           description: "Median minutes from first contact reply to last close."
1271:           tests: ["p50_time_to_last_close_min >= 0"]
1272:         - name: p50_reopens
1273:           data_type: DOUBLE
1274:           description: "Median number of reopens per conversation."
1275:           tests: ["p50_reopens >= 0"]
1276:         - name: missing_days
1277:           data_type: BIGINT
1278:           description: "Count of missing active days within the min..max range of conversation days."
1279:           tests: ["missing_days >= 0"]
1280:         - name: is_date_continuous
1281:           data_type: BOOLEAN
1282:           description: "True if the company's conversations span continuous days without gaps within the observed range."
1283:           tests: []
1284: 
1285:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/marts/intercom__company_metrics.sql`，SHA-256 `8ac171989fee70519dd2ee0067250239ab50b0012dd313041c4185922e750863`，行 1–72。

```
1: with company_dim_ranked as (
2:     select *, row_number() over(partition by company_id order by coalesce(updated_at,created_at) desc nulls last) as rn
3:     from intermediate.int_intercom__company_history
4: ), company_dim as (
5:     select company_id, company_name, website, industry, plan_id, plan_name from company_dim_ranked where rn=1
6: ), contact_base as (
7:     select distinct rel.company_id, ct.contact_id, ct.signed_up_at, ct.is_active_7d, ct.is_active_30d, ct.retained_7d, ct.retained_30d
8:     from intermediate.int_intercom__contact_company_history rel
9:     join intermediate.int_intercom__contact_latest ct on rel.contact_id=ct.contact_id
10: ), contact_rollup as (
11:     select company_id, count(distinct contact_id)::bigint as contacts_total,
12:            count(distinct contact_id) filter(where is_active_7d)::bigint as contacts_active_7d,
13:            count(distinct contact_id) filter(where is_active_30d)::bigint as contacts_active_30d,
14:            count(distinct contact_id) filter(where signed_up_at is not null) as registered_contacts,
15:            count(distinct contact_id) filter(where signed_up_at is not null and retained_7d) as registered_retained_7d,
16:            count(distinct contact_id) filter(where signed_up_at is not null and retained_30d) as registered_retained_30d
17:     from contact_base group by company_id
18: ), conv_to_company as (
19:     select distinct rel.company_id, c.conversation_id, c.conversation_state, c.conversation_type,
20:            a.count_total_parts, c.conversation_rating, a.count_reopens,
21:            date_trunc('day', c.conversation_created_at)::date as conversation_day
22:     from intermediate.int_intercom__latest_conversation c
23:     join intermediate.int_intercom__conversation_part_events e on c.conversation_id=e.conversation_id
24:     join intermediate.int_intercom__contact_company_history rel on e.first_contact_author_id=rel.contact_id
25:     left join intermediate.int_intercom__conversation_part_aggregates a on c.conversation_id=a.conversation_id
26: ), conversation_rollup as (
27:     select company_id, count(distinct conversation_id)::bigint as total_conversations,
28:            count(distinct conversation_id) filter(where conversation_state='closed')::bigint as total_conversations_closed,
29:            avg(count_total_parts)::double as avg_conversation_parts,
30:            avg(conversation_rating)::double as avg_conversation_rating,
31:            count(distinct conversation_id) filter(where lower(coalesce(conversation_type,''))='email') as email_conversations,
32:            count(distinct conversation_id) filter(where lower(coalesce(conversation_type,''))='messenger') as messenger_conversations,
33:            count(distinct conversation_id) filter(where lower(coalesce(conversation_type,'')) not in ('email','messenger')) as other_conversations,
34:            min(conversation_day) as min_day, max(conversation_day) as max_day,
35:            count(distinct conversation_day) as observed_days,
36:            median(count_reopens)::double as p50_reopens
37:     from conv_to_company group by company_id
38: ), convo_time_metrics as (
39:     select cc.company_id,
40:            median(case when a.first_admin_response_at >= c.conversation_created_at
41:                        then date_diff('second', c.conversation_created_at, a.first_admin_response_at) / 60.0 end)::double as p50_time_to_first_response_min,
42:            median(case when e.first_close_at >= a.first_contact_reply_at
43:                        then date_diff('second', a.first_contact_reply_at, e.first_close_at) / 60.0 end)::double as p50_time_to_first_close_min,
44:            median(case when e.last_close_at >= a.first_contact_reply_at
45:                        then date_diff('second', a.first_contact_reply_at, e.last_close_at) / 60.0 end)::double as p50_time_to_last_close_min
46:     from conv_to_company cc
47:     join intermediate.int_intercom__latest_conversation c on cc.conversation_id=c.conversation_id
48:     left join intermediate.int_intercom__conversation_part_aggregates a on cc.conversation_id=a.conversation_id
49:     left join intermediate.int_intercom__conversation_part_events e on cc.conversation_id=e.conversation_id
50:     group by cc.company_id
51: )
52: select d.company_id, d.company_name, d.website, d.industry, d.plan_id, d.plan_name,
53:        coalesce(cr.total_conversations,0)::bigint as total_conversations,
54:        coalesce(cr.total_conversations_closed,0)::bigint as total_conversations_closed,
55:        cr.avg_conversation_parts, cr.avg_conversation_rating,
56:        coalesce(co.contacts_total,0)::bigint as contacts_total,
57:        case when co.contacts_total>0 then cr.total_conversations::double/co.contacts_total end as conv_rate_overall,
58:        case when co.contacts_total>0 then cr.email_conversations::double/co.contacts_total end as conv_rate_email,
59:        case when co.contacts_total>0 then cr.messenger_conversations::double/co.contacts_total end as conv_rate_messenger,
60:        case when co.contacts_total>0 then cr.other_conversations::double/co.contacts_total end as conv_rate_other,
61:        coalesce(co.contacts_active_7d,0)::bigint as contacts_active_7d,
62:        coalesce(co.contacts_active_30d,0)::bigint as contacts_active_30d,
63:        case when co.registered_contacts>0 then co.registered_retained_7d::double/co.registered_contacts end as registration_retention_7d,
64:        case when co.registered_contacts>0 then co.registered_retained_30d::double/co.registered_contacts end as registration_retention_30d,
65:        tm.p50_time_to_first_response_min, tm.p50_time_to_first_close_min, tm.p50_time_to_last_close_min,
66:        cr.p50_reopens,
67:        case when cr.min_day is not null then greatest(date_diff('day',cr.min_day,cr.max_day)+1-cr.observed_days,0)::bigint else 0::bigint end as missing_days,
68:        case when cr.min_day is not null then date_diff('day',cr.min_day,cr.max_day)+1=cr.observed_days else null end as is_date_continuous
69: from company_dim d
70: left join contact_rollup co on d.company_id=co.company_id
71: left join conversation_rollup cr on d.company_id=cr.company_id
72: left join convo_time_metrics tm on d.company_id=tm.company_id
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/sql/marts/intercom__company_metrics.sql`，SHA-256 `857afe25eeaec9af20571f518ac355a510c48411cfde66e2c4a2f80430f08251`，行 1–146。

```
1: -- intercom__company_metrics
2: -- Purpose: Company-level support performance and engagement metrics
3: -- Layer contract: marts may only read from intermediate
4: with latest_conversation as (
5:   select * from intermediate.int_intercom__latest_conversation
6: ),
7: conversation_part_aggregates as (
8:   select * from intermediate.int_intercom__conversation_part_aggregates
9: ),
10: conversation_part_events as (
11:   select * from intermediate.int_intercom__conversation_part_events
12: ),
13: contact_company_history as (
14:   select * from intermediate.int_intercom__contact_company_history
15: ),
16: contact_latest as (
17:   select * from intermediate.int_intercom__contact_latest
18: ),
19: company_base as (
20:   -- take latest company snapshot per company_id
21:   select company_id, any_value(company_name) as company_name, any_value(website) as website,
22:          any_value(industry) as industry, max(updated_at) as last_company_updated_at,
23:          max(created_at) as company_created_at, any_value(plan_id) as plan_id, any_value(plan_name) as plan_name
24:   from intermediate.int_intercom__company_history
25:   group by 1
26: ),
27: -- map conversations to companies via first_contact_author_id -> contact -> company
28: conv_company as (
29:   select
30:     lc.conversation_id,
31:     lc.conversation_created_at,
32:     lc.conversation_type,
33:     lc.conversation_initiated_type,
34:     cch.company_id
35:   from latest_conversation lc
36:   left join conversation_part_events cpe on cpe.conversation_id = lc.conversation_id
37:   left join contact_company_history cch on cch.contact_id = cpe.first_contact_author_id
38: ),
39: company_contact_stats as (
40:   select
41:     cch.company_id,
42:     count(distinct cl.contact_id) as contacts_total,
43:     count(distinct case when cl.is_active_7d then cl.contact_id end) as contacts_active_7d,
44:     count(distinct case when cl.is_active_30d then cl.contact_id end) as contacts_active_30d,
45:     count(distinct case when cl.retained_7d then cl.contact_id end) as contacts_retained_7d,
46:     count(distinct case when cl.retained_30d then cl.contact_id end) as contacts_retained_30d,
47:     count(distinct case when cl.signed_up_at is not null then cl.contact_id end) as contacts_with_signup
48:   from contact_company_history cch
49:   left join contact_latest cl on cl.contact_id = cch.contact_id
50:   group by 1
51: ),
52: company_conv_stats as (
53:   select
54:     cc.company_id,
55:     sum(case when lc.conversation_state = 'closed' then 1 else 0 end) as total_conversations_closed,
56:     count(*) as total_conversations,
57:     round(avg(coalesce(cpa.count_total_parts, 0)), 2) as avg_conversation_parts,
58:     avg(try_cast(lc.conversation_rating as double)) as avg_conversation_rating,
59:     -- conversion by channel (source_type)
60:     sum(case when lc.conversation_type = 'email' then 1 else 0 end) as conv_email,
61:     sum(case when lc.conversation_type = 'messenger' then 1 else 0 end) as conv_messenger,
62:     sum(case when lc.conversation_type not in ('email','messenger') or lc.conversation_type is null then 1 else 0 end) as conv_other
63:   from conv_company cc
64:   left join latest_conversation lc on lc.conversation_id = cc.conversation_id
65:   left join conversation_part_aggregates cpa on cpa.conversation_id = cc.conversation_id
66:   group by 1
67: ),
68: company_time_medians as (
69:   -- compute per-conversation times and then median by company
70:   select distinct
71:     cc.company_id,
72:     quantile_cont(greatest(0.0, round(date_diff('second', lc.conversation_created_at, cpa.first_admin_response_at) / 60.0, 2)), 0.5)
73:       over (partition by cc.company_id) as p50_time_to_first_response_min,
74:     quantile_cont(greatest(0.0, round(date_diff('second', cpa.first_contact_reply_at, cpe.first_close_at) / 60.0, 2)), 0.5)
75:       over (partition by cc.company_id) as p50_time_to_first_close_min,
76:     quantile_cont(greatest(0.0, round(date_diff('second', cpa.first_contact_reply_at, cpe.last_close_at) / 60.0, 2)), 0.5)
77:       over (partition by cc.company_id) as p50_time_to_last_close_min,
78:     quantile_cont(coalesce(cpa.count_reopens, 0), 0.5) over (partition by cc.company_id) as p50_reopens
79:   from conv_company cc
80:   left join latest_conversation lc on lc.conversation_id = cc.conversation_id
81:   left join conversation_part_aggregates cpa on cpa.conversation_id = cc.conversation_id
82:   left join conversation_part_events cpe on cpe.conversation_id = cc.conversation_id
83: ),
84: company_date_gap_check as (
85:   -- continuity check on conversation days within min..max
86:   select
87:     company_id,
88:     min(date_trunc('day', conversation_created_at)) as min_day,
89:     max(date_trunc('day', conversation_created_at)) as max_day,
90:     count(distinct date_trunc('day', conversation_created_at)) as active_days
91:   from conv_company
92:   group by 1
93: ),
94: company_date_continuity as (
95:   select
96:     g.company_id,
97:     g.min_day,
98:     g.max_day,
99:     case when g.min_day is not null and g.max_day is not null then
100:       datediff('day', g.min_day, g.max_day) + 1
101:     else 0 end as total_days,
102:     g.active_days,
103:     case when g.min_day is not null and g.max_day is not null then (datediff('day', g.min_day, g.max_day) + 1) - g.active_days else 0 end as missing_days,
104:     case when g.min_day is null then true else ((datediff('day', g.min_day, g.max_day) + 1) - g.active_days) = 0 end as is_date_continuous
105:   from company_date_gap_check g
106: ),
107: final as (
108:   select
109:     cb.company_id,
110:     any_value(cb.company_name) as company_name,
111:     any_value(cb.website) as website,
112:     any_value(cb.industry) as industry,
113:     any_value(cb.plan_id) as plan_id,
114:     any_value(cb.plan_name) as plan_name,
115:     max(coalesce(cms.total_conversations,0)) as total_conversations,
116:     max(coalesce(cms.total_conversations_closed,0)) as total_conversations_closed,
117:     max(cms.avg_conversation_parts) as avg_conversation_parts,
118:     max(cms.avg_conversation_rating) as avg_conversation_rating,
119:     -- conversion rates guarded by denominators
120:     max(ccs.contacts_total) as contacts_total,
121:     case when max(ccs.contacts_total) > 0 then max(cms.total_conversations) * 1.0 / max(ccs.contacts_total) else null end as conv_rate_overall,
122:     case when max(ccs.contacts_total) > 0 then max(cms.conv_email) * 1.0 / max(ccs.contacts_total) else null end as conv_rate_email,
123:     case when max(ccs.contacts_total) > 0 then max(cms.conv_messenger) * 1.0 / max(ccs.contacts_total) else null end as conv_rate_messenger,
124:     case when max(ccs.contacts_total) > 0 then max(cms.conv_other) * 1.0 / max(ccs.contacts_total) else null end as conv_rate_other,
125:     -- active users by window
126:     max(ccs.contacts_active_7d) as contacts_active_7d,
127:     max(ccs.contacts_active_30d) as contacts_active_30d,
128:     -- retention ratios (registration-based)
129:     case when max(ccs.contacts_with_signup) > 0 then max(ccs.contacts_retained_7d) * 1.0 / max(ccs.contacts_with_signup) else null end as registration_retention_7d,
130:     case when max(ccs.contacts_with_signup) > 0 then max(ccs.contacts_retained_30d) * 1.0 / max(ccs.contacts_with_signup) else null end as registration_retention_30d,
131:     -- medians
132:     max(ctm.p50_time_to_first_response_min) as p50_time_to_first_response_min,
133:     max(ctm.p50_time_to_first_close_min) as p50_time_to_first_close_min,
134:     max(ctm.p50_time_to_last_close_min) as p50_time_to_last_close_min,
135:     max(ctm.p50_reopens) as p50_reopens,
136:     -- continuity
137:     max(cdc.missing_days) as missing_days,
138:     bool_and(cdc.is_date_continuous) as is_date_continuous
139:   from company_base cb
140:   left join company_conv_stats cms on cms.company_id = cb.company_id
141:   left join company_contact_stats ccs on ccs.company_id = cb.company_id
142:   left join company_time_medians ctm on ctm.company_id = cb.company_id
143:   left join company_date_continuity cdc on cdc.company_id = cb.company_id
144:   group by cb.company_id
145: )
146: select * from final
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 39/40、43/44 看到company metrics 2509行及字段；event 61 未解释缺失contacts聚合补0。清理逻辑清单不作策略证据。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 39：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/39.json`。
- event 40：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/40.json`。
- event 43：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/43.json`。
- event 44：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/44.json`。
- event 61：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/61.json`。
## 查询

核实查询 **0** 条；核实代价档：**需要查业务说明**。诊断查询不计入 5 条上限。

未追加 agent 可见数据核实；判断依据为契约、SQL 和明确标为诊断的查询，不用 gold 结果证明 U。

### 诊断：contact 映射覆盖

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/intercom.duckdb`。

```sql
SELECT count(*) joined_contacts FROM intermediate.int_intercom__contact_company_history r JOIN intermediate.int_intercom__contact_latest c USING(contact_id)
```


```json
{"columns":["joined_contacts"],"rows":[[1327]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-020_intercom__company_metrics.json](../023_reruns_impl-020_intercom__company_metrics.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/intercom.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2509|2509|2509|7527|否|
|L1|2509|2509|2509|7527|否|
|L2|2509|2509|2509|7527|否|
|L3|2509|2509|2509|7527|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"contacts_active_30d":2509,"contacts_active_7d":2509,"contacts_total":2509}`
- L1：`{"contacts_active_30d":2509,"contacts_active_7d":2509,"contacts_total":2509}`
- L2：`{"contacts_active_30d":2509,"contacts_active_7d":2509,"contacts_total":2509}`
- L3：`{"contacts_active_30d":2509,"contacts_active_7d":2509,"contacts_total":2509}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-020_intercom__company_metrics/baseline.sql`；SHA-256 `8ac171989fee70519dd2ee0067250239ab50b0012dd313041c4185922e750863`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2509|2509|2509|7527|否|
|L1|2509|2509|2509|7527|否|
|L2|2509|2509|2509|7527|否|
|L3|2509|2509|2509|7527|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"contacts_active_30d":2509,"contacts_active_7d":2509,"contacts_total":2509}`
- L1：`{"contacts_active_30d":2509,"contacts_active_7d":2509,"contacts_total":2509}`
- L2：`{"contacts_active_30d":2509,"contacts_active_7d":2509,"contacts_total":2509}`
- L3：`{"contacts_active_30d":2509,"contacts_active_7d":2509,"contacts_total":2509}`

#### contacts_total

判定：主因；类别候选 A。契约未指定无匹配 contact 聚合时补0还是 NULL。

相对本轮基线减少行 0、格 2509；按行优先、格次之排序。
共同控制后 SQL 第 56 行起、字符 offset 4415 的唯一连续替换；其余字节不动。
替换前：
```sql
coalesce(co.contacts_total,0)
```

替换后：
```sql
co.contacts_total
```

私有 SQL：`data/023_work/impl-020_intercom__company_metrics/contacts_total.sql`；SHA-256 `e8dd2141b9d237fcd20c980de71026b998b50ff4f8650eb7d24974285d325eba`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2509|2509|2509|5018|否|
|L1|2509|2509|2509|5018|否|
|L2|2509|2509|2509|5018|否|
|L3|2509|2509|2509|5018|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"contacts_active_30d":2509,"contacts_active_7d":2509}`
- L1：`{"contacts_active_30d":2509,"contacts_active_7d":2509}`
- L2：`{"contacts_active_30d":2509,"contacts_active_7d":2509}`
- L3：`{"contacts_active_30d":2509,"contacts_active_7d":2509}`

#### contacts_active_7d

判定：主因；类别候选 A。契约未指定无匹配 contact 聚合时补0还是 NULL。

相对本轮基线减少行 0、格 2509；按行优先、格次之排序。
共同控制后 SQL 第 61 行起、字符 offset 4949 的唯一连续替换；其余字节不动。
替换前：
```sql
coalesce(co.contacts_active_7d,0)
```

替换后：
```sql
co.contacts_active_7d
```

私有 SQL：`data/023_work/impl-020_intercom__company_metrics/contacts_active_7d.sql`；SHA-256 `d6d3b99704d591b26521173504473bbafd640b844643cf00446148fe5b410a56`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2509|2509|2509|5018|否|
|L1|2509|2509|2509|5018|否|
|L2|2509|2509|2509|5018|否|
|L3|2509|2509|2509|5018|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"contacts_active_30d":2509,"contacts_total":2509}`
- L1：`{"contacts_active_30d":2509,"contacts_total":2509}`
- L2：`{"contacts_active_30d":2509,"contacts_total":2509}`
- L3：`{"contacts_active_30d":2509,"contacts_total":2509}`

#### contacts_active_30d

判定：主因；类别候选 A。契约未指定无匹配 contact 聚合时补0还是 NULL。

相对本轮基线减少行 0、格 2509；按行优先、格次之排序。
共同控制后 SQL 第 62 行起、字符 offset 5021 的唯一连续替换；其余字节不动。
替换前：
```sql
coalesce(co.contacts_active_30d,0)
```

替换后：
```sql
co.contacts_active_30d
```

私有 SQL：`data/023_work/impl-020_intercom__company_metrics/contacts_active_30d.sql`；SHA-256 `8964188e298d055435f104aa20b09cf3f6683019d2052031339938bb30cf55e3`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2509|2509|2509|5018|否|
|L1|2509|2509|2509|5018|否|
|L2|2509|2509|2509|5018|否|
|L3|2509|2509|2509|5018|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"contacts_active_7d":2509,"contacts_total":2509}`
- L1：`{"contacts_active_7d":2509,"contacts_total":2509}`
- L2：`{"contacts_active_7d":2509,"contacts_total":2509}`
- L3：`{"contacts_active_7d":2509,"contacts_total":2509}`

## 规则问题

无
