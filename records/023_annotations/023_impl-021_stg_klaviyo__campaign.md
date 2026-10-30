# impl-021 · stg_klaviyo__campaign

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：null_id_filter。

agent按契约ID not_null过滤，gold保留NULL ID；仅放开该过滤后L0全匹配。

参与因素：无。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-021_stg_klaviyo__campaign.md](../023_packages/023_impl-021_stg_klaviyo__campaign.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml`；SHA-256 `db04fb84955b6385dd63b72bdf7aae27ac9f612a685f938eabf7051f12cd675f`。
契约行 24–67：

```
24:     - name: stg_klaviyo__campaign
25:       description: "Cleaned Klaviyo campaign records with standardized sender fields and timestamps."
26:       source_table: raw.campaign
27:       columns:
28:         - name: campaign_id
29:           data_type: VARCHAR
30:           constraints: [not_null]
31:         - name: campaign_type
32:           data_type: VARCHAR
33:         - name: created_at
34:           data_type: TIMESTAMP
35:         - name: email_template_id
36:           data_type: VARCHAR
37:         - name: from_email
38:           data_type: VARCHAR
39:           validation_rules:
40:             - rule: "from_email IS NULL OR LOWER(TRIM(from_email)) RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
41:               on_failure: delete_row
42:             - rule: "from_email IS NULL OR from_email = LOWER(TRIM(from_email))"
43:               on_failure: correct
44:         - name: from_name
45:           data_type: VARCHAR
46:         - name: campaign_name
47:           data_type: VARCHAR
48:         - name: scheduled_to_send_at
49:           data_type: TIMESTAMP
50:         - name: sent_at
51:           data_type: TIMESTAMP
52:         - name: status
53:           data_type: VARCHAR
54:         - name: status_id
55:           data_type: INTEGER
56:         - name: subject
57:           data_type: VARCHAR
58:         - name: updated_at
59:           data_type: TIMESTAMP
60:         - name: is_archived
61:           data_type: BOOLEAN
62:         - name: scheduled_at
63:           data_type: TIMESTAMP
64:         - name: source_relation
65:           data_type: VARCHAR
66:           constraints: [not_null]
67:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/staging/stg_klaviyo__campaign.sql`，SHA-256 `9ad024673d6f13b9dba736fcce8a3f759cdc1ed8966995c251e198494e154ac9`，行 1–20。

```
1: select
2:     cast("ID" as varchar) as campaign_id,
3:     cast("CAMPAIGN_TYPE" as varchar) as campaign_type,
4:     try_cast("CREATED" as timestamp) as created_at,
5:     cast("EMAIL_TEMPLATE_ID" as varchar) as email_template_id,
6:     lower(trim(cast("FROM_EMAIL" as varchar))) as from_email,
7:     cast("FROM_NAME" as varchar) as from_name,
8:     cast("NAME" as varchar) as campaign_name,
9:     try_cast("SEND_TIME" as timestamp) as scheduled_to_send_at,
10:     try_cast("SENT_AT" as timestamp) as sent_at,
11:     cast("STATUS" as varchar) as status,
12:     try_cast("STATUS_ID" as integer) as status_id,
13:     cast("SUBJECT" as varchar) as subject,
14:     try_cast("UPDATED" as timestamp) as updated_at,
15:     try_cast("ARCHIVED" as boolean) as is_archived,
16:     try_cast("SCHEDULED" as timestamp) as scheduled_at,
17:     'klaviyo'::varchar as source_relation
18: from raw.campaign
19: where nullif(trim(cast("ID" as varchar)), '') is not null
20:   and ("FROM_EMAIL" is null or regexp_full_match(lower(trim(cast("FROM_EMAIL" as varchar))), '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}'))
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/sql/staging/stg_klaviyo__campaign.sql`，SHA-256 `555df557b6a76885781c94fd307df0359f2329b2ef8b7d3ae67f3c50cf5ea4fa`，行 1–28。

```
1: with base as (
2:     select * from raw.campaign
3: ),
4: validated as (
5:     select
6:         cast(id as varchar) as campaign_id,
7:         campaign_type,
8:         created as created_at,
9:         email_template_id,
10:         lower(trim(from_email)) as from_email,
11:         from_name,
12:         name as campaign_name,
13:         send_time as scheduled_to_send_at,
14:         sent_at,
15:         status,
16:         status_id,
17:         subject,
18:         updated as updated_at,
19:         archived as is_archived,
20:         scheduled as scheduled_at,
21:         'klaviyo' as source_relation
22:     from base
23:     where base.from_email is null OR regexp_matches(lower(trim(base.from_email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
24: ),
25: final as (
26:     select * from validated
27: )
28: select * from final
```

## 轨迹可见性与不确定性

**四档：只有通用策略说明**。

event 19/20、23/24 显式查看raw ID非空计数；event 41：「无效关键 ID 和非法邮件记录被排除」。这是跨表条件处理策略，非工作清单。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 19：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/19.json`。
- event 20：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/20.json`。
- event 23：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/23.json`。
- event 24：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/24.json`。
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

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：ID 空值

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE id IS NULL) null_id,count(*) FILTER(WHERE trim(id)='') blank_id FROM raw.campaign
```


```json
{"columns":["n","null_id","blank_id"],"rows":[[200,198,0]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-021_stg_klaviyo__campaign.json](../023_reruns_impl-021_stg_klaviyo__campaign.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2|184|182|1638|否|
|L1|2|184|182|1638|否|
|L2|2|184|182|1638|否|
|L3|2|184|182|1638|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"campaign_id":182,"campaign_name":182,"CAMPAIGN_TYPE":182,"EMAIL_TEMPLATE_ID":182,"from_email":182,"FROM_NAME":182,"STATUS":182,"STATUS_ID":182,"SUBJECT":182}`
- L1：`{"campaign_id":182,"campaign_name":182,"CAMPAIGN_TYPE":182,"EMAIL_TEMPLATE_ID":182,"from_email":182,"FROM_NAME":182,"STATUS":182,"STATUS_ID":182,"SUBJECT":182}`
- L2：`{"campaign_id":182,"campaign_name":182,"CAMPAIGN_TYPE":182,"EMAIL_TEMPLATE_ID":182,"from_email":182,"FROM_NAME":182,"STATUS":182,"STATUS_ID":182,"SUBJECT":182}`
- L3：`{"campaign_id":182,"campaign_name":182,"CAMPAIGN_TYPE":182,"EMAIL_TEMPLATE_ID":182,"from_email":182,"FROM_NAME":182,"STATUS":182,"STATUS_ID":182,"SUBJECT":182}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-021_stg_klaviyo__campaign/baseline.sql`；SHA-256 `9ad024673d6f13b9dba736fcce8a3f759cdc1ed8966995c251e198494e154ac9`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2|184|182|1638|否|
|L1|2|184|182|1638|否|
|L2|2|184|182|1638|否|
|L3|2|184|182|1638|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"campaign_id":182,"campaign_name":182,"CAMPAIGN_TYPE":182,"EMAIL_TEMPLATE_ID":182,"from_email":182,"FROM_NAME":182,"STATUS":182,"STATUS_ID":182,"SUBJECT":182}`
- L1：`{"campaign_id":182,"campaign_name":182,"CAMPAIGN_TYPE":182,"EMAIL_TEMPLATE_ID":182,"from_email":182,"FROM_NAME":182,"STATUS":182,"STATUS_ID":182,"SUBJECT":182}`
- L2：`{"campaign_id":182,"campaign_name":182,"CAMPAIGN_TYPE":182,"EMAIL_TEMPLATE_ID":182,"from_email":182,"FROM_NAME":182,"STATUS":182,"STATUS_ID":182,"SUBJECT":182}`
- L3：`{"campaign_id":182,"campaign_name":182,"CAMPAIGN_TYPE":182,"EMAIL_TEMPLATE_ID":182,"from_email":182,"FROM_NAME":182,"STATUS":182,"STATUS_ID":182,"SUBJECT":182}`

#### null_id_filter

判定：主因；类别候选 O。前三表契约明确 ID not_null，gold 保留 NULL；person 没有非空要求，额外删除为未规定取舍。

相对本轮基线减少行 182、格 1638；按行优先、格次之排序。
共同控制后 SQL 第 19 行起、字符 offset 848 的唯一连续替换；其余字节不动。
替换前：
```sql
nullif(trim(cast("ID" as varchar)), '') is not null
```

替换后：
```sql
TRUE
```

私有 SQL：`data/023_work/impl-021_stg_klaviyo__campaign/null_id_filter.sql`；SHA-256 `b7917ff159a438ab9894d6476e709d396ec8ceec99636073a68660a5e4046c9c`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|184|184|0|0|是|
|L1|184|184|0|0|是|
|L2|184|184|0|0|是|
|L3|184|184|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 规则问题

无
