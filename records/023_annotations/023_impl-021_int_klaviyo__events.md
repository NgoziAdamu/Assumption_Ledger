# impl-021 · int_klaviyo__events

用途：**全量**；层：`intermediate`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：直接诊断（无正改善的单点排序）。

相同person/timestamp并列顺序导致lag归属不同；gold还有session_seq=0，与契约从1开始不一致。

参与因素：无。

标记：无。

gold有2组各2条同person同timestamp；除窗口派生列外L0全匹配。O依据包含明确session起点冲突，不能仅以任意排序解释0。

## 材料与比较口径

精简材料包：[023_impl-021_int_klaviyo__events.md](../023_packages/023_impl-021_int_klaviyo__events.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml`；SHA-256 `db04fb84955b6385dd63b72bdf7aae27ac9f612a685f938eabf7051f12cd675f`。
契约行 921–1038：

```
921:     - name: int_klaviyo__events
922:       description: Events enriched with inherited touch attribution, joined dimensions, session features, and non-negative revenue fields
923:       grain: One row per (source_relation, event_id)
924:       source_models:
925:       - staging.stg_klaviyo__event
926:       - staging.stg_klaviyo__campaign
927:       - staging.stg_klaviyo__flow
928:       - staging.stg_klaviyo__person
929:       - staging.stg_klaviyo__metric
930:       business_logic: '- Start from staging.stg_klaviyo__event and derive direct touch fields: touch_id is campaign_id when present, otherwise flow_id; touch_type is ''campaign'' or ''flow'' accordingly. - For events with event_attribution and no direct touch_id, inherit touch from the attributed child: - Remove "$" characters from event_attribution. - Extract the child event id by first looking for relationships.attributed-event.data.id, else attributed_event_id. - Remove surrounding quotes and treat empty values as NULL. - Join back to the events set on source_relation and the extracted child event_id to obtain the child''s touch_id and touch_type. - Set last_touch_id and session_touch_type to the child''s values when found; otherwise use the event’s direct touch_id and touch_type. - Derive occurred_on by truncating occurred_at to the calendar day (date type). - For each person, prev_event_at is the timestamp of the immediately prior event ordered by occurred_at; when none exists it is NULL; ties on identical timestamps follow engine-defined order. - Session features: - inter_event_minutes is the rounded difference in minutes between prev_event_at and occurred_at; NULL when prev_event_at is NULL. - session_seq is a running count per person that starts at 1 and increases by 1 when prev_event_at is NULL or the gap between events exceeds 30 minutes. - Join dimensions with LEFT JOINs scoped by source_relation: - Campaign: only when the effective touch type (session_touch_type if present else touch_type) is ''campaign''; match on the resolved touch id (last_touch_id if present else touch_id). - Flow: only when the effective touch type is ''flow''; match on the resolved touch id (last_touch_id if present else touch_id). - Person: join on person_id. - Metric: join on metric_id. - If a key is not applicable or no match is found, the related dimension fields are NULL. - Derived flags and normalized revenue: - is_engagement_event = 1 when type is one of {''active on site'',''viewed product'',''opened email'',''clicked email'',''received email''} ignoring case; else 0. - amount_positive = numeric_value when type is ''placed order'' or ''ordered product'' (case-insensitive) and numeric_value is non-negative; otherwise 0. - amount_negative = numeric_value when type is ''refunded order'' or ''cancelled order'' (case-insensitive) and numeric_value is non-negative; otherwise 0.'
931:       columns:
932:       - name: source_relation
933:         data_type: VARCHAR
934:         description: Source system identifier used to scope joins and grain
935:       - name: event_id
936:         data_type: VARCHAR
937:         description: Event identifier unique within source_relation; one output row per (source_relation, event_id)
938:         tests:
939:         - not_null
940:       - name: person_id
941:         data_type: VARCHAR
942:         description: Person identifier for the event; used for window partitioning and person dimension join
943:       - name: metric_id
944:         data_type: VARCHAR
945:         description: Metric identifier for the event; used to join metric dimension fields
946:       - name: type
947:         data_type: VARCHAR
948:         description: Event type; used to derive flags via case-insensitive matching to specific values
949:       - name: UUID
950:         data_type: VARCHAR
951:         description: Event UUID when provided; may be NULL
952:       - name: variation_id
953:         data_type: VARCHAR
954:         description: Variant or variation identifier when present; may be NULL
955:       - name: numeric_value
956:         data_type: DOUBLE
957:         description: Numeric amount parsed from event properties; used for revenue normalization; may be NULL
958:       - name: event_attribution
959:         data_type: VARCHAR
960:         description: Raw JSON attribution string used to inherit touch from an attributed child; may be NULL
961:       - name: occurred_at
962:         data_type: TIMESTAMP
963:         description: Event timestamp; used for date derivation, window lag, and session segmentation
964:       - name: occurred_on
965:         data_type: DATE
966:         description: Date derived from occurred_at by truncating to the day; NULL only if occurred_at is NULL
967:       - name: touch_id
968:         data_type: VARCHAR
969:         description: 'Direct touch identifier from the event: campaign_id if present else flow_id; NULL if neither exists'
970:       - name: touch_type
971:         data_type: VARCHAR
972:         description: 'Direct touch type: ''campaign'' if campaign_id is present, ''flow'' if flow_id is present; NULL if neither'
973:       - name: last_touch_id
974:         data_type: VARCHAR
975:         description: 'Resolved touch identifier: inherited from the attributed child when available, otherwise the direct touch_id; may be NULL'
976:       - name: session_touch_type
977:         data_type: VARCHAR
978:         description: 'Resolved touch type: inherited from the attributed child when available, otherwise the direct touch_type; ''campaign''/''flow'' or NULL'
979:       - name: prev_event_at
980:         data_type: TIMESTAMP
981:         description: Previous occurred_at for the same person ordered by occurred_at; NULL for the first event; ties follow engine-defined order
982:       - name: last_touch_campaign_id
983:         data_type: VARCHAR
984:         description: Resolved campaign id when the effective touch type is 'campaign' (equals last_touch_id if present else touch_id), otherwise NULL
985:       - name: last_touch_flow_id
986:         data_type: VARCHAR
987:         description: Resolved flow id when the effective touch type is 'flow' (equals last_touch_id if present else touch_id), otherwise NULL
988:       - name: campaign_name
989:         data_type: VARCHAR
990:         description: Campaign name from campaign dimension joined on the resolved campaign id; NULL if not applicable or no match
991:       - name: CAMPAIGN_TYPE
992:         data_type: VARCHAR
993:         description: Campaign type from campaign dimension joined on the resolved campaign id; NULL if not applicable or no match
994:       - name: campaign_subject_line
995:         data_type: VARCHAR
996:         description: Campaign subject line from campaign dimension joined on the resolved campaign id; NULL if not applicable or no match
997:       - name: flow_name
998:         data_type: VARCHAR
999:         description: Flow name from flow dimension joined on the resolved flow id; NULL if not applicable or no match
1000:       - name: person_city
1001:         data_type: VARCHAR
1002:         description: City from person dimension joined on person_id; NULL if no person match
1003:       - name: person_country
1004:         data_type: VARCHAR
1005:         description: Country from person dimension joined on person_id; NULL if no person match
1006:       - name: person_region
1007:         data_type: VARCHAR
1008:         description: Region from person dimension joined on person_id; NULL if no person match
1009:       - name: person_email
1010:         data_type: VARCHAR
1011:         description: Email from person dimension joined on person_id; NULL if no person match
1012:       - name: person_timezone
1013:         data_type: VARCHAR
1014:         description: Timezone from person dimension joined on person_id; NULL if no person match
1015:       - name: integration_id
1016:         data_type: VARCHAR
1017:         description: Integration id from metric dimension joined on metric_id; NULL if no metric match
1018:       - name: integration_name
1019:         data_type: VARCHAR
1020:         description: Integration name from metric dimension joined on metric_id; NULL if no metric match
1021:       - name: integration_category
1022:         data_type: VARCHAR
1023:         description: Integration category from metric dimension joined on metric_id; NULL if no metric match
1024:       - name: inter_event_minutes
1025:         data_type: BIGINT
1026:         description: Rounded difference in minutes between prev_event_at and occurred_at; NULL when prev_event_at is NULL
1027:       - name: session_seq
1028:         data_type: HUGEINT
1029:         description: Running session counter per person ordered by occurred_at; starts at 1 and increments when the gap exceeds 30 minutes; ties follow engine-defined order
1030:       - name: is_engagement_event
1031:         data_type: INTEGER
1032:         description: 'Flag: 1 if type is one of {''active on site'',''viewed product'',''opened email'',''clicked email'',''received email''} ignoring case, else 0'
1033:       - name: amount_positive
1034:         data_type: DOUBLE
1035:         description: 'Non-negative amount for ''placed order'' or ''ordered product'': numeric_value when present and ≥ 0, otherwise 0'
1036:       - name: amount_negative
1037:         data_type: DOUBLE
1038:         description: 'Non-negative amount for ''refunded order'' or ''cancelled order'': numeric_value when present and ≥ 0, otherwise 0'
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/intermediate/int_klaviyo__events.sql`，SHA-256 `e2b24ec5b4a45ac5f486543e23c597a716edd332394b23d947de7b963f17ecdd`，行 1–44。

```
1: with 
2: events_base as (
3:     select e.*, case when campaign_id is not null then campaign_id else flow_id end as direct_touch_id,
4:            case when campaign_id is not null then 'campaign' when flow_id is not null then 'flow' end as direct_touch_type
5:     from staging.stg_klaviyo__event e
6: ), attribution_ids as (
7:     select *, nullif(replace(coalesce(
8:       json_extract_string(replace(event_attribution, '$', ''), '$.relationships.attributed-event.data.id'),
9:       json_extract_string(replace(event_attribution, '$', ''), '$.attributed_event_id')
10:     ), '"', ''), '') as attributed_event_id
11:     from events_base
12: ), resolved as (
13:     select a.*, coalesce(child.direct_touch_id, a.direct_touch_id) as resolved_touch_id,
14:            coalesce(child.direct_touch_type, a.direct_touch_type) as resolved_touch_type
15:     from attribution_ids a
16:     left join events_base child
17:       on a.attributed_event_id = child.event_id and a.source_relation = child.source_relation
18:      and a.direct_touch_id is null and a.event_attribution is not null
19: ), sequenced as (
20:  select *, lag(occurred_at) over(partition by person_id order by occurred_at) prev_event_at
21:  from resolved
22: ), sessions as (
23:  select *, sum(case when prev_event_at is null or epoch(occurred_at) - epoch(prev_event_at) > 1800 then 1 else 0 end)
24:        over(partition by person_id order by occurred_at rows between unbounded preceding and current row) session_seq
25:  from sequenced
26: )
27: select e.source_relation, e.event_id, e.person_id, e.metric_id, e.type, e.uuid as UUID, e.variation_id,
28:  e.numeric_value, e.event_attribution, e.occurred_at, e.occurred_on, e.direct_touch_id as touch_id,
29:  e.direct_touch_type as touch_type, e.resolved_touch_id as last_touch_id, e.resolved_touch_type as session_touch_type,
30:  e.prev_event_at,
31:  case when coalesce(e.resolved_touch_type,e.direct_touch_type)='campaign' then coalesce(e.resolved_touch_id,e.direct_touch_id) end last_touch_campaign_id,
32:  case when coalesce(e.resolved_touch_type,e.direct_touch_type)='flow' then coalesce(e.resolved_touch_id,e.direct_touch_id) end last_touch_flow_id,
33:  c.campaign_name, c.campaign_type as CAMPAIGN_TYPE, c.subject as campaign_subject_line,
34:  f.flow_name, p.city as person_city, p.country as person_country, p.region as person_region,
35:  p.email as person_email, p.timezone as person_timezone, m.integration_id, m.integration_name, m.integration_category,
36:  case when e.prev_event_at is null then null else round(date_diff('microsecond', e.prev_event_at,e.occurred_at) / 60000000.0) end::bigint inter_event_minutes,
37:  e.session_seq, case when lower(e.type) in ('active on site','viewed product','opened email','clicked email','received email') then 1 else 0 end::integer is_engagement_event,
38:  case when lower(e.type) in ('placed order','ordered product') and e.numeric_value>=0 then e.numeric_value else 0 end::double amount_positive,
39:  case when lower(e.type) in ('refunded order','cancelled order') and e.numeric_value>=0 then e.numeric_value else 0 end::double amount_negative
40: from sessions e
41: left join staging.stg_klaviyo__campaign c on c.campaign_id=coalesce(e.resolved_touch_id,e.direct_touch_id) and c.source_relation=e.source_relation and coalesce(e.resolved_touch_type,e.direct_touch_type)='campaign'
42: left join staging.stg_klaviyo__flow f on f.flow_id=coalesce(e.resolved_touch_id,e.direct_touch_id) and f.source_relation=e.source_relation and coalesce(e.resolved_touch_type,e.direct_touch_type)='flow'
43: left join staging.stg_klaviyo__person p on p.person_id=e.person_id and p.source_relation=e.source_relation
44: left join staging.stg_klaviyo__metric m on m.metric_id=e.metric_id and m.source_relation=e.source_relation
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/sql/intermediate/int_klaviyo__events.sql`，SHA-256 `4b8538a7e30e3cef349365894bf5dd6fc21c1706cdb292aab8aa57d214da3bc8`，行 1–150。

```
1: -- Intermediate: Events enriched with attribution, dimensions and session features
2: -- Layer rules: ONLY reference staging.* sources; no same-layer dependencies
3: -- Business logic: window functions, robust JSON parsing, non-negative revenue, derived activity flags
4: 
5: -- Intermediate: Events enriched with attribution, dimensions and session features
6: -- Layer rules: ONLY reference staging.* sources; no same-layer dependencies
7: -- Business logic: window functions, robust JSON parsing, non-negative revenue, derived activity flags
8: 
9: with events as (
10:     select
11:         e.*,
12:         -- direct touch fields
13:         coalesce(e.campaign_id, e.flow_id) as touch_id,
14:         case when e.campaign_id is not null then 'campaign'
15:              when e.flow_id    is not null then 'flow' end as touch_type
16:     from staging.stg_klaviyo__event e
17: ),
18: 
19: children as (
20:     -- events that point to an attributed child (no direct touch_id)
21:     select
22:         *,
23:         replace(event_attribution, '$', '') as cleaned_event_attribution
24:     from events
25:     where event_attribution is not null
26:       and touch_id is null
27: ),
28: 
29: parsed as (
30:     select
31:         *,
32:         coalesce(
33:             json_extract_string(cleaned_event_attribution, '$.relationships.attributed-event.data.id'),
34:             json_extract_string(cleaned_event_attribution, '$.attributed_event_id')
35:         ) as extracted_event_id_raw
36:     from children
37: ),
38: 
39: normalized_children as (
40:     select
41:         *,
42:         nullif(replace(extracted_event_id_raw, '"', ''), '') as extracted_event_id
43:     from parsed
44: ),
45: 
46: extracted_touch as (
47:     select
48:         event_id as extracted_event_id,
49:         touch_id as extracted_touch_id,
50:         touch_type as extracted_touch_type,
51:         type      as extracted_event_type,
52:         source_relation,
53:         person_id,
54:         occurred_at
55:     from events
56: ),
57: 
58: inherited as (
59:     -- inherit touch info from the attributed child event
60:     select
61:         n.source_relation,
62:         n.event_id,
63:         n.person_id,
64:         n.occurred_at,
65:         e.extracted_touch_id,
66:         e.extracted_touch_type,
67:         e.extracted_event_type
68:     from normalized_children n
69:     left join extracted_touch e
70:       on n.extracted_event_id = e.extracted_event_id
71:      and n.source_relation = e.source_relation
72:     where n.extracted_event_id is not null
73: ),
74: 
75: resolved as (
76:     select
77:         ev.source_relation,
78:         ev.event_id,
79:         ev.person_id,
80:         ev.metric_id,
81:         ev.type,
82:         ev.uuid,
83:         ev.variation_id,
84:         ev.numeric_value,
85:         ev.event_attribution,
86:         ev.occurred_at,
87:         cast(date_trunc('day', ev.occurred_at) as date) as occurred_on,
88:         ev.touch_id,
89:         ev.touch_type,
90:         -- session-level inheritance
91:         coalesce(inh.extracted_touch_id, ev.touch_id)   as last_touch_id,
92:         coalesce(inh.extracted_touch_type, ev.touch_type) as session_touch_type
93:     from events ev
94:     left join inherited inh
95:       on ev.event_id = inh.event_id
96:      and ev.source_relation = inh.source_relation
97: ),
98: 
99: -- enrich with dimensions from staging
100: campaign as (select * from staging.stg_klaviyo__campaign),
101: flow     as (select * from staging.stg_klaviyo__flow),
102: person   as (select * from staging.stg_klaviyo__person),
103: metric   as (select * from staging.stg_klaviyo__metric),
104: 
105: -- precompute previous event to avoid nested window fns
106: with_prev as (
107:     select
108:         r.*,
109:         lag(r.occurred_at) over (partition by r.person_id order by r.occurred_at) as prev_event_at
110:     from resolved r
111: ),
112: joined as (
113:     select
114:         wp.*,
115:         case when coalesce(wp.session_touch_type, wp.touch_type) = 'campaign'
116:              then coalesce(wp.last_touch_id, wp.touch_id) end as last_touch_campaign_id,
117:         case when coalesce(wp.session_touch_type, wp.touch_type) = 'flow'
118:              then coalesce(wp.last_touch_id, wp.touch_id) end as last_touch_flow_id,
119:         -- dims
120:         c.campaign_name,
121:         c.campaign_type,
122:         c.subject as campaign_subject_line,
123:         f.flow_name,
124:         p.city    as person_city,
125:         p.country as person_country,
126:         p.region  as person_region,
127:         p.email   as person_email,
128:         p.timezone as person_timezone,
129:         m.integration_id,
130:         m.integration_name,
131:         m.integration_category,
132:         -- session features
133:         round(date_diff('minute', wp.prev_event_at, wp.occurred_at)) as inter_event_minutes,
134:         sum(case when wp.prev_event_at is null
135:                      or date_diff('minute', wp.prev_event_at, wp.occurred_at) > 30
136:                  then 1 else 0 end)
137:             over (partition by wp.person_id order by wp.occurred_at rows unbounded preceding) as session_seq,
138:         -- derived activity flags
139:         case when lower(wp.type) in ('active on site','viewed product','opened email','clicked email','received email') then 1 else 0 end as is_engagement_event,
140:         -- revenue normalization: non-negative only
141:         case when lower(wp.type) in ('placed order','ordered product') and coalesce(wp.numeric_value,0) >= 0 then coalesce(wp.numeric_value,0) else 0 end as amount_positive,
142:         case when lower(wp.type) in ('refunded order','cancelled order') and coalesce(wp.numeric_value,0) >= 0 then coalesce(wp.numeric_value,0) else 0 end as amount_negative
143:     from with_prev wp
144:     left join campaign c on wp.source_relation = c.source_relation and case when coalesce(wp.session_touch_type, wp.touch_type) = 'campaign' then coalesce(wp.last_touch_id, wp.touch_id) end = c.campaign_id
145:     left join flow     f on wp.source_relation = f.source_relation and case when coalesce(wp.session_touch_type, wp.touch_type) = 'flow' then coalesce(wp.last_touch_id, wp.touch_id) end = f.flow_id
146:     left join person   p on wp.source_relation = p.source_relation and wp.person_id              = p.person_id
147:     left join metric   m on wp.source_relation = m.source_relation and wp.metric_id              = m.metric_id
148: )
149: 
150: select * from joined
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 1 契约明确时间并列engine-defined且session从1开始；event 13/33 写session窗口；event 41 未说明并列排序。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 1：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/1.json`。
- event 13：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/13.json`。
- event 33：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/33.json`。
- event 41：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/41.json`。
## 查询

核实查询 **0** 条；核实代价档：**需要查业务说明**。诊断查询不计入 5 条上限。

未追加 agent 可见数据核实；判断依据为契约、SQL 和明确标为诊断的查询，不用 gold 结果证明 U。

### 诊断：tied 窗口诊断

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/klaviyo.duckdb`。

```sql
SELECT person_id,occurred_at,count(*) n FROM staging.stg_klaviyo__event GROUP BY 1,2 ORDER BY 1,2
```


```json
{"columns":["person_id","occurred_at","n"],"rows":[["LRqEsZ","2020-04-05 20:02:43",2],["MCX88q","2020-04-05 20:02:45",2]]}
```


### 诊断：gold session 起点

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/klaviyo.duckdb`。

```sql
SELECT event_id,person_id,occurred_at,prev_event_at,inter_event_minutes,session_seq FROM intermediate.int_klaviyo__events ORDER BY event_id
```


```json
{"columns":["event_id","person_id","occurred_at","prev_event_at","inter_event_minutes","session_seq"],"rows":[["3gBNHPGp","MCX88q","2020-04-05 20:02:45",null,null,1],["3gBNHPJn","LRqEsZ","2020-04-05 20:02:43",null,null,1],["4gBNHPJn","LRqEsZ","2020-04-05 20:02:43","2020-04-05 20:02:43",0,0],["event123","MCX88q","2020-04-05 20:02:45","2020-04-05 20:02:45",0,1]]}
```


### 诊断：除并列窗口列外一致性

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4|4|0|0|是|
|L1|4|4|0|0|是|
|L2|4|4|0|0|是|
|L3|4|4|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 独立单点重跑

### 首轮：[023_reruns_impl-021_int_klaviyo__events.json](../023_reruns_impl-021_int_klaviyo__events.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/klaviyo.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4|4|2|3|否|
|L1|4|4|2|3|否|
|L2|4|4|2|3|否|
|L3|4|4|2|3|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"inter_event_minutes":2,"session_seq":1}`
- L1：`{"inter_event_minutes":2,"session_seq":1}`
- L2：`{"inter_event_minutes":2,"session_seq":1}`
- L3：`{"inter_event_minutes":2,"session_seq":1}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-021_int_klaviyo__events/baseline.sql`；SHA-256 `e2b24ec5b4a45ac5f486543e23c597a716edd332394b23d947de7b963f17ecdd`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4|4|2|3|否|
|L1|4|4|2|3|否|
|L2|4|4|2|3|否|
|L3|4|4|2|3|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"inter_event_minutes":2,"session_seq":1}`
- L1：`{"inter_event_minutes":2,"session_seq":1}`
- L2：`{"inter_event_minutes":2,"session_seq":1}`
- L3：`{"inter_event_minutes":2,"session_seq":1}`

## 规则问题

无
