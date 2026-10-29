# impl-010 / stg_hubspot__form

## 1. 错在哪里

agent与gold使用不同form_data：前者1150个FORM_ ID，后者1150行/1142个数值ID，全部原始行不相同。

已核实：agent raw与初始库raw的完整行多重集合一致；按同名列对齐后，agent raw与gold raw各1150行完全不相交。agent有1150个FORM_ ID，gold有1142个不同数值ID；gold按guid去重得到1142行。单改agent去重或时间规则都不能弥合输入ID差异；gold SQL在agent私有raw上执行也不能匹配留存gold。归因判断：O，当前比较混入输入差异，不把synthetic风格字段直接说成agent伪造。

## 2. 依据

- 起点：[013精简包](../013_packages/013_impl-010_staging_stg_hubspot__form.md)。原013状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml`，第462–497行。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/staging/stg_hubspot__form.sql`；gold SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/sql/staging/stg_hubspot__form.sql`。精简包完整收录；下列补丁逐字给出定位原文。
- [完整事件记录](../014_trace_impl-010.json)；事件文件在该JSON的path中，可回查traces/dacomp_deimpl_prev.tar.gz。
- [查询原文与结果](../014_queries_impl-010.json)、[全部重跑记录](../014_reruns_impl-010.json)。

### SQL行号定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/staging/stg_hubspot__form.sql`
```text
2:     guid as form_id,
14:     try_strptime(substr(created_at, 1, 19), '%Y-%m-%d %H:%M:%S') as created_timestamp,
15:     try_strptime(substr(updated_at, 1, 19), '%Y-%m-%d %H:%M:%S') as updated_timestamp,
16:     cast(null as timestamptz) as _fivetran_synced
18: where guid is not null
```

gold：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/sql/staging/stg_hubspot__form.sql`
```text
7:         cast(guid as varchar) as form_id,
27:         created_at as created_timestamp_raw,
28:         updated_at as updated_timestamp_raw,
31:         row_number() over (
32:             partition by cast(guid as varchar)
43:             WHEN created_timestamp_raw IS NOT NULL
44:                  AND CAST(created_timestamp_raw AS VARCHAR) ~ '^\d{4}-\d{2}-\d{2}'
45:             THEN CAST(created_timestamp_raw AS TIMESTAMP)
47:         END as created_timestamp,
49:             WHEN updated_timestamp_raw IS NOT NULL
50:                  AND CAST(updated_timestamp_raw AS VARCHAR) ~ '^\d{4}-\d{2}-\d{2}'
51:             THEN CAST(updated_timestamp_raw AS TIMESTAMP)
53:         END as updated_timestamp
55:     where rn = 1
71:     created_timestamp,
72:     updated_timestamp,
73:     current_timestamp::timestamp with time zone as _fivetran_synced
```

## 3. agent看过什么

event 13→14看到form_data schema；event 17按guid编写SQL；event 39复制start raw、event41修复run.py导入连接逻辑。event51查看其他表时间样例，event53批量改时间解析。现有证据未显示agent生成FORM_数据；初始/agent完整行一致是更直接证据。

已逐题核对event 1 message，包含本表契约完整原文；这不是把磁盘上存在的文档等同于agent已经阅读。schema输出、源数据值、运行日志分别处理。轨迹全量转录未删去截断标记；被截断的未显示部分不作为看到的证据。

## 4. 查询与重跑

核实查询实际执行 **1条**；核实代价：**一条查询**。诊断查询不计入5条限制。重复执行的查询仍计数。

### V1：核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/hubspot.duckdb`

```sql
SELECT count(*) n,count(distinct guid) guids,count(*) FILTER(WHERE guid LIKE 'FORM_%') synthetic_style_ids,min(guid) min_guid,max(guid) max_guid,count(distinct portal_id) portals FROM raw.form_data
```

结果：
```json
{
  "columns": [
    "n",
    "guids",
    "synthetic_style_ids",
    "min_guid",
    "max_guid",
    "portals"
  ],
  "rows": [
    [
      1150,
      1150,
      1150,
      "FORM_00000000",
      "FORM_00001149",
      1
    ]
  ]
}
```

### D1：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`

```sql
SELECT count(*) n,count(distinct guid) guids,count(*) FILTER(WHERE guid LIKE 'FORM_%') synthetic_style_ids,min(guid) min_guid,max(guid) max_guid,count(distinct portal_id) portals FROM raw.form_data
```

结果：
```json
{
  "error": "Binder Error: No function matches the given name and argument types '~~(BIGINT, STRING_LITERAL)'. You might need to add explicit type casts.\n\tCandidate functions:\n\t~~(VARCHAR, VARCHAR) -> BOOLEAN\n\n\nLINE 1: ...(*) n,count(distinct guid) guids,count(*) FILTER(WHERE guid LIKE 'FORM_%') synthetic_style_ids,min(guid) min_guid,max...\n                                                                       ^"
}
```

### D_raw：诊断查询

数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/hubspot.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb']`

```sql
SELECT * FROM raw.form_data
```

结果：
```json
{
  "result": {
    "columns_identical": false,
    "agent_columns": [
      "guid",
      "portal_id",
      "name",
      "form_type",
      "method",
      "action",
      "redirect",
      "lead_nurturing_campaign_id",
      "follow_up_id",
      "created_at",
      "updated_at",
      "css_class",
      "notify_recipients",
      "submit_text"
    ],
    "gold_columns": [
      "guid",
      "action",
      "created_at",
      "css_class",
      "follow_up_id",
      "form_type",
      "lead_nurturing_campaign_id",
      "method",
      "name",
      "notify_recipients",
      "portal_id",
      "redirect",
      "submit_text",
      "updated_at"
    ],
    "agent_rows": 1150,
    "gold_rows": 1150
  },
  "operation": "Python Counter of full typed rows, exact multiset difference"
}
```

### D2：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`

```sql
SELECT count(*) n,count(distinct guid) guids,min(cast(guid as varchar)) min_guid,max(cast(guid as varchar)) max_guid FROM raw.form_data
```

结果：
```json
{
  "columns": [
    "n",
    "guids",
    "min_guid",
    "max_guid"
  ],
  "rows": [
    [
      1150,
      1142,
      "10012",
      "99908"
    ]
  ]
}
```

### D_ids：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`

```sql
SELECT count(*) n,count(distinct guid) guids,count(*) FILTER(WHERE CAST(guid AS VARCHAR) LIKE 'FORM_%') form_ids,min(CAST(guid AS VARCHAR)),max(CAST(guid AS VARCHAR)) FROM raw.form_data
```

结果：
```json
{
  "columns": [
    "n",
    "guids",
    "form_ids",
    "min(CAST(guid AS VARCHAR))",
    "max(CAST(guid AS VARCHAR))"
  ],
  "rows": [
    [
      1150,
      1142,
      0,
      "10012",
      "99908"
    ]
  ]
}
```

### D_ids：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`

```sql
SELECT count(*) n,count(distinct guid) guids,count(*) FILTER(WHERE CAST(guid AS VARCHAR) LIKE 'FORM_%') form_ids,min(CAST(guid AS VARCHAR)),max(CAST(guid AS VARCHAR)) FROM raw.form_data
```

结果：
```json
{
  "columns": [
    "n",
    "guids",
    "form_ids",
    "min(CAST(guid AS VARCHAR))",
    "max(CAST(guid AS VARCHAR))"
  ],
  "rows": [
    [
      1150,
      1142,
      0,
      "10012",
      "99908"
    ]
  ]
}
```

### D_input_alignment：诊断查询

数据库：`['/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/hubspot_start.duckdb', '/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/hubspot.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb']`

```sql
SELECT "action","created_at","css_class","follow_up_id","form_type","guid","lead_nurturing_campaign_id","method","name","notify_recipients","portal_id","redirect","submit_text","updated_at" FROM raw.form_data
```

结果：
```json
{
  "schema_query": "DESCRIBE raw.form_data",
  "operation": "sort column names, compare full typed row Counters; data not saved",
  "result": {
    "initial_agent_equal": true,
    "agent_gold_equal": false,
    "agent_only": 1150,
    "gold_only": 1150
  }
}
```

### 比较口径

原件均READ_ONLY；只把本节点引用表复制到data/014_work私有DuckDB后执行。staging输入来自agent留存库raw；003/008上游直接复制gold，实现CS。固定原评分的comparison_columns与key_columns；L0为lower/trim/NULL规范化，L1数字及布尔归一，L2数值两位小数，L3再放宽日期时间到日期。键始终固定L0，不在宽松档位重新归一。

无共同键时逐列0表示无可比较行，不表示一致。重复键按值/行多重集合抵消，报告最少不一致对数；同时公开额外行次数。为避免键被漏出整表判断，含键整表匹配用于本次U4；旧007式仅值列整表匹配并列展示。这里没有重定义原官方对错或修改旧状态。

比较列：`['created_timestamp', 'follow_up_id', 'form_action', 'form_css_class', 'form_id', 'form_method', 'form_name', 'form_redirect', 'form_submit_text', 'form_type', 'lead_nurturing_campaign_id', 'notify_recipients', 'portal_id']`；键：`['form_id']`。

### 留存基线（013材料来源）

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L1|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L2|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L3|1150|1142|1150|1142|0|0/0|1150/1142|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|created_timestamp|0|0|0|0|
|follow_up_id|0|0|0|0|
|form_action|0|0|0|0|
|form_css_class|0|0|0|0|
|form_id|0|0|0|0|
|form_method|0|0|0|0|
|form_name|0|0|0|0|
|form_redirect|0|0|0|0|
|form_submit_text|0|0|0|0|
|form_type|0|0|0|0|
|lead_nurturing_campaign_id|0|0|0|0|
|notify_recipients|0|0|0|0|
|portal_id|0|0|0|0|

### 重跑：baseline

不改SQL；建立本轮相同引擎、相同输入的比较基线。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L1|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L2|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L3|1150|1142|1150|1142|0|0/0|1150/1142|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|created_timestamp|0|0|0|0|
|follow_up_id|0|0|0|0|
|form_action|0|0|0|0|
|form_css_class|0|0|0|0|
|form_id|0|0|0|0|
|form_method|0|0|0|0|
|form_name|0|0|0|0|
|form_redirect|0|0|0|0|
|form_submit_text|0|0|0|0|
|form_type|0|0|0|0|
|lead_nurturing_campaign_id|0|0|0|0|
|notify_recipients|0|0|0|0|
|portal_id|0|0|0|0|

### 重跑：deduplicate

只替换以下原文（其余字节经验证不变）：
```sql
where guid is not null
```
替换为：
```sql
where guid is not null
QUALIFY row_number() over(partition by guid order by updated_at desc nulls last,created_at desc nulls last)=1
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L1|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L2|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L3|1150|1142|1150|1142|0|0/0|1150/1142|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|created_timestamp|0|0|0|0|
|follow_up_id|0|0|0|0|
|form_action|0|0|0|0|
|form_css_class|0|0|0|0|
|form_id|0|0|0|0|
|form_method|0|0|0|0|
|form_name|0|0|0|0|
|form_redirect|0|0|0|0|
|form_submit_text|0|0|0|0|
|form_type|0|0|0|0|
|lead_nurturing_campaign_id|0|0|0|0|
|notify_recipients|0|0|0|0|
|portal_id|0|0|0|0|

### 重跑：created_rule

只替换以下原文（其余字节经验证不变）：
```sql
try_strptime(substr(created_at, 1, 19), '%Y-%m-%d %H:%M:%S')
```
替换为：
```sql
CASE WHEN created_at IS NOT NULL AND CAST(created_at AS VARCHAR) ~ '^\d{4}-\d{2}-\d{2}' THEN CAST(created_at AS TIMESTAMP) ELSE NULL END
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L1|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L2|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L3|1150|1142|1150|1142|0|0/0|1150/1142|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|created_timestamp|0|0|0|0|
|follow_up_id|0|0|0|0|
|form_action|0|0|0|0|
|form_css_class|0|0|0|0|
|form_id|0|0|0|0|
|form_method|0|0|0|0|
|form_name|0|0|0|0|
|form_redirect|0|0|0|0|
|form_submit_text|0|0|0|0|
|form_type|0|0|0|0|
|lead_nurturing_campaign_id|0|0|0|0|
|notify_recipients|0|0|0|0|
|portal_id|0|0|0|0|

### gold SQL在同一私有输入上的诊断

这是诊断，不是局部修复，也不用于证明U4。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L1|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L2|1150|1142|1150|1142|0|0/0|1150/1142|False|False|
|L3|1150|1142|1150|1142|0|0/0|1150/1142|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|created_timestamp|0|0|0|0|
|follow_up_id|0|0|0|0|
|form_action|0|0|0|0|
|form_css_class|0|0|0|0|
|form_id|0|0|0|0|
|form_method|0|0|0|0|
|form_name|0|0|0|0|
|form_redirect|0|0|0|0|
|form_submit_text|0|0|0|0|
|form_type|0|0|0|0|
|lead_nurturing_campaign_id|0|0|0|0|
|notify_recipients|0|0|0|0|
|portal_id|0|0|0|0|

## 5. 类别和把握

- 主要原因：**O**（归因判断）。
- 参与因素：无（输入差异遮蔽局部实现影响）。
- 标记：无。
- 把握：**高**。
- 重跑是否满足U第4条件：否。

无可用U主命题。当前raw.guid实际唯一，不能用gold.raw中的重复guid去反证agent当时看到的数据；这样会违反核实查询边界。

## 规则问题

即使存在未去重/时间解析实现差异，单独重跑都不改善本次判错，不列参与因素。_fivetran_synced全NULL不在比较列与键中，不能据此把本表归D。O说明当前比较条件，不重新改写013官方状态。

共同问题：手册第1节“不预设类别分布”与末句“希望未核实假设多”存在张力；本次以逐条证据条件为准，不按期望调整分布。U3“没看过任何足以判断P的东西”与“证据曾出现但被忽略仍归U”按后者作为例外解释。
