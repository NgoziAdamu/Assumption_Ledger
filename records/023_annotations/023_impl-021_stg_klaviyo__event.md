# impl-021 · stg_klaviyo__event

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：email_regex。

gold 双反斜杠邮箱正则拒绝2496条普通合法邮箱记录，agent按契约保留。

参与因素：无。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-021_stg_klaviyo__event.md](../023_packages/023_impl-021_stg_klaviyo__event.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml`；SHA-256 `db04fb84955b6385dd63b72bdf7aae27ac9f612a685f938eabf7051f12cd675f`。
契约行 68–117：

```
68:     - name: stg_klaviyo__event
69:       description: "Cleaned event stream with derived numeric_value, normalized price fields, and standardized timestamps. Rows with an invalid property_email (when present) are dropped."
70:       source_table: raw.event
71:       columns:
72:         - name: campaign_id
73:           data_type: VARCHAR
74:         - name: flow_id
75:           data_type: VARCHAR
76:         - name: variation_id
77:           data_type: VARCHAR  # sourced from _variation in SQL
78:         - name: flow_message_id
79:           data_type: VARCHAR
80:         - name: event_id
81:           data_type: VARCHAR
82:         - name: metric_id
83:           data_type: VARCHAR
84:         - name: person_id
85:           data_type: VARCHAR
86:         - name: type
87:           data_type: VARCHAR
88:           validation_rules:
89:             - rule: "type is stored in lowercase for consistency"
90:               on_failure: correct
91:         - name: uuid
92:           data_type: VARCHAR
93:         - name: numeric_value
94:           data_type: DOUBLE
95:           validation_rules:
96:             - rule: "numeric_value derived by stripping non-numeric characters from property_value and casting to double"
97:               on_failure: nullify_field
98:         - name: event_attribution
99:           data_type: VARCHAR
100:         - name: occurred_at
101:           data_type: TIMESTAMP
102:         - name: occurred_on
103:           data_type: DATE
104:         - name: source_relation
105:           data_type: VARCHAR
106:           constraints: [not_null]
107:         - name: property_price
108:           data_type: DOUBLE
109:           validation_rules:
110:             - rule: "property_price is NULL or >= 0"
111:               on_failure: nullify_field
112:         - name: property_compare_at_price
113:           data_type: DOUBLE
114:           validation_rules:
115:             - rule: "property_compare_at_price is NULL or >= 0"
116:               on_failure: nullify_field
117:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/staging/stg_klaviyo__event.sql`，SHA-256 `e55a5b163d45b28faeba2260896a33b05c20f675a93d5ec4192202b1e1563956`，行 1–21。

```
1: with cleaned as (
2:  select *, regexp_replace(coalesce(cast(property_value as varchar), ''), '[^0-9.-]', '', 'g') as numeric_text
3:  from raw.event
4: ), casted as (
5:  select *, try_cast(nullif(numeric_text, '') as double) as parsed_numeric_value
6:  from cleaned
7: )
8: select cast(campaign_id as varchar) campaign_id, cast(flow_id as varchar) flow_id,
9:  cast("_VARIATION" as varchar) variation_id, cast(flow_message_id as varchar) flow_message_id,
10:  cast(id as varchar) event_id, cast(metric_id as varchar) metric_id, cast(person_id as varchar) person_id,
11:  lower(cast(type as varchar)) as type, cast(uuid as varchar) uuid,
12:  parsed_numeric_value as numeric_value,
13:  cast(property_attribution as varchar) as event_attribution,
14:  try_cast(coalesce("DATETIME", "TIMESTAMP") as timestamp) occurred_at,
15:  cast(try_cast(coalesce("DATETIME", "TIMESTAMP") as timestamp) as date) occurred_on,
16:  'klaviyo'::varchar source_relation,
17:  case when try_cast(property_price as double) >= 0 then try_cast(property_price as double) else null end property_price,
18:  case when try_cast(property_compare_at_price as double) >= 0 then try_cast(property_compare_at_price as double) else null end property_compare_at_price
19: from casted
20: where nullif(trim(cast(id as varchar)), '') is not null
21:   and (property_email is null or regexp_full_match(lower(trim(cast(property_email as varchar))), '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}'))
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/sql/staging/stg_klaviyo__event.sql`，SHA-256 `5cfa25a9d4f1822c468a9b707011a9dfe030abaf577d3d2f39eb6afba701fa87`，行 1–47。

```
1: with base as (
2:     select * from raw.event
3: ),
4: validated as (
5:     select
6:         cast(campaign_id as varchar) as campaign_id,
7:         cast(flow_id as varchar) as flow_id,
8:         cast(_variation as varchar) as variation_id,
9:         flow_message_id,
10:         cast(id as varchar) as event_id,
11:         cast(metric_id as varchar) as metric_id,
12:         cast(person_id as varchar) as person_id,
13:         lower(type) as type,
14:         uuid,
15:         -- numeric_value from property_value
16:         try_cast(regexp_replace(cast(property_value as varchar), '[^0-9\.-]', '') as double) as numeric_value,
17:         cast(property_attribution as varchar) as event_attribution,
18:         cast(timestamp as timestamp) as occurred_at,
19:         -- optional source_relation constant
20:         'klaviyo' as source_relation,
21:         -- optional price fields validation
22:         case when try_cast(property_price as double) is not null and try_cast(property_price as double) >= 0 then try_cast(property_price as double) else null end as property_price,
23:         case when try_cast(property_compare_at_price as double) is not null and try_cast(property_compare_at_price as double) >= 0 then try_cast(property_compare_at_price as double) else null end as property_compare_at_price
24:     from base
25:     where property_email is null OR regexp_matches(property_email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
26: ),
27: final as (
28:     select
29:         campaign_id,
30:         flow_id,
31:         variation_id,
32:         flow_message_id,
33:         event_id,
34:         metric_id,
35:         person_id,
36:         type,
37:         uuid,
38:         numeric_value,
39:         event_attribution,
40:         occurred_at,
41:         cast(date_trunc('day', occurred_at) as date) as occurred_on,
42:         source_relation,
43:         property_price,
44:         property_compare_at_price
45:     from validated
46: )
47: select * from final
```

## 轨迹可见性与不确定性

**四档：只有通用策略说明**。

event 11/12 看过raw样例，event 27/28、29 显式排查邮箱regex转义；event 41：「无效关键 ID 和非法邮件记录被排除」。未对本表与gold的转义差异作具体说明。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 11：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/11.json`。
- event 12：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/12.json`。
- event 27：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/27.json`。
- event 28：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/28.json`。
- event 29：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/29.json`。
- event 41：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/41.json`。

event 41 最终报告原文（用于检查说明是否超出工作清单）：

```
【回复用户】

已根据 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 Klaviyo SQL 数据管道，SQL 文件均放置在 `sql/staging/`、`sql/intermediate/`、`sql/marts/`，共 18 个模型文件。SQL 使用 DuckDB 语法、直接以 `schema.table` 引用上游、不含 dbt `ref()`，且文件末尾无分号。

**执行验证**
- `python run.py` 成功完成 staging → intermediate → marts 全部层级转换。
- 构建行数：staging campaign 2、event 2,500、flow 1、metric 1、person 2；intermediate event_attribution 2,500、events 2,500、person_campaign_flow 9、campaign_flow_metrics 7、person_metrics 3、campaigns_enriched 2、flows_enriched 1、persons_enriched 2；marts events 2,500、campaigns 2、flows 1、persons 2、person_campaign_flow 9。
- 检查 campaign/person/event/flow/metric staging 主键字段无空值及重复；event 的 `(source_relation, event_id)` 在 staging、intermediate 与 marts 均无空值及重复。

**数据质量处理与边界说明**
- staging 清洗邮件和 timezone 大小写、空白，标准化电话，安全转换时间/数值；无效关键 ID 和非法邮件记录被排除，超长 person email 置空，负的 price/compare-at-price 置空。
- 事件 attribution 解析按契约优先级提取 JSON 子事件 ID，查找限定同一 `source_relation`；事件重复保留且照常计数。
- 契约未指定 `source_relation` 的字面值，本实现使用固定来源键 `'klaviyo'`。电话号码按 E.164-like 格式加前缀 `+`，未推断国家码。
- 所有 SQL 文件遵循 DuckDB/直接 schema-table 引用规范。`python run.py` 成功，无失败 SQL 语句；目标数据库为 `klaviyo.duckdb`。
```

## 查询

核实查询 **0** 条；核实代价档：**需要查业务说明**。诊断查询不计入 5 条上限。

未追加 agent 可见数据核实；判断依据为契约、SQL 和明确标为诊断的查询，不用 gold 结果证明 U。

### 诊断：email 两种正则

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/klaviyo.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE property_email IS NULL OR regexp_matches(property_email,'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')) ordinary_email,count(*) FILTER(WHERE property_email IS NULL OR regexp_matches(property_email,'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')) gold_email FROM raw.event
```


```json
{"columns":["n","ordinary_email","gold_email"],"rows":[[2500,2500,4]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-021_stg_klaviyo__event.json](../023_reruns_impl-021_stg_klaviyo__event.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|4|2496|34944|否|
|L1|2500|4|2496|34944|否|
|L2|2500|4|2496|34944|否|
|L3|2500|4|2496|34944|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"event_id":2496,"campaign_id":2496,"event_attribution":2496,"flow_id":2496,"FLOW_MESSAGE_ID":2496,"metric_id":2496,"numeric_value":2496,"occurred_on":2496,"person_id":2496,"property_compare_at_price":2496,"property_price":2496,"type":2496,"UUID":2496,"variation_id":2496}`
- L1：`{"event_id":2496,"campaign_id":2496,"event_attribution":2496,"flow_id":2496,"FLOW_MESSAGE_ID":2496,"metric_id":2496,"numeric_value":2496,"occurred_on":2496,"person_id":2496,"property_compare_at_price":2496,"property_price":2496,"type":2496,"UUID":2496,"variation_id":2496}`
- L2：`{"event_id":2496,"campaign_id":2496,"event_attribution":2496,"flow_id":2496,"FLOW_MESSAGE_ID":2496,"metric_id":2496,"numeric_value":2496,"occurred_on":2496,"person_id":2496,"property_compare_at_price":2496,"property_price":2496,"type":2496,"UUID":2496,"variation_id":2496}`
- L3：`{"event_id":2496,"campaign_id":2496,"event_attribution":2496,"flow_id":2496,"FLOW_MESSAGE_ID":2496,"metric_id":2496,"numeric_value":2496,"occurred_on":2496,"person_id":2496,"property_compare_at_price":2496,"property_price":2496,"type":2496,"UUID":2496,"variation_id":2496}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-021_stg_klaviyo__event/baseline.sql`；SHA-256 `e55a5b163d45b28faeba2260896a33b05c20f675a93d5ec4192202b1e1563956`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2500|4|2496|34944|否|
|L1|2500|4|2496|34944|否|
|L2|2500|4|2496|34944|否|
|L3|2500|4|2496|34944|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"event_id":2496,"campaign_id":2496,"event_attribution":2496,"flow_id":2496,"FLOW_MESSAGE_ID":2496,"metric_id":2496,"numeric_value":2496,"occurred_on":2496,"person_id":2496,"property_compare_at_price":2496,"property_price":2496,"type":2496,"UUID":2496,"variation_id":2496}`
- L1：`{"event_id":2496,"campaign_id":2496,"event_attribution":2496,"flow_id":2496,"FLOW_MESSAGE_ID":2496,"metric_id":2496,"numeric_value":2496,"occurred_on":2496,"person_id":2496,"property_compare_at_price":2496,"property_price":2496,"type":2496,"UUID":2496,"variation_id":2496}`
- L2：`{"event_id":2496,"campaign_id":2496,"event_attribution":2496,"flow_id":2496,"FLOW_MESSAGE_ID":2496,"metric_id":2496,"numeric_value":2496,"occurred_on":2496,"person_id":2496,"property_compare_at_price":2496,"property_price":2496,"type":2496,"UUID":2496,"variation_id":2496}`
- L3：`{"event_id":2496,"campaign_id":2496,"event_attribution":2496,"flow_id":2496,"FLOW_MESSAGE_ID":2496,"metric_id":2496,"numeric_value":2496,"occurred_on":2496,"person_id":2496,"property_compare_at_price":2496,"property_price":2496,"type":2496,"UUID":2496,"variation_id":2496}`

#### email_regex

判定：主因；类别候选 O。gold 双反斜杠正则拒绝普通有效邮箱，而契约只要求删除 invalid property_email；需诊断确认。

相对本轮基线减少行 2496、格 34944；按行优先、格次之排序。
共同控制后 SQL 第 21 行起、字符 offset 1249 的唯一连续替换；其余字节不动。
替换前：
```sql
(property_email is null or regexp_full_match(lower(trim(cast(property_email as varchar))), '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}'))
```

替换后：
```sql
(property_email is null or regexp_matches(property_email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'))
```

私有 SQL：`data/023_work/impl-021_stg_klaviyo__event/email_regex.sql`；SHA-256 `060cc208f380b754d67d560559e1f7bfdda9eba6b2e3dc8385c9f692efa3a881`。

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

## 规则问题

无
