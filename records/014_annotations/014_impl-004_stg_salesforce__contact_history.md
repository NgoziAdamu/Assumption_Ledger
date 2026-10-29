# impl-004 / stg_salesforce__contact_history

## 1. 错在哪里

history_unique_key生成约定未写明，hash与id加时间导致全部键不相交；另有1行日期边界差异。

已核实：两边raw完整行多重集合一致，均3000行。agent history_unique_key是hash(_fivetran_start,_fivetran_end)，gold是id与运行时间拼接。契约只声明VARCHAR，未定义算法。只换成gold公式但使用当前时钟仍无共同键；把该表达式中的时间固定为gold实际时刻2025-10-24 15:03:11.630125+08后，只剩1行last_activity_date差异。单独按gold日界补日期规则可消去这1行值差异，但key仍不一致。归因判断：主要A，运行日期的残余为O。

## 2. 依据

- 起点：[013精简包](../013_packages/013_impl-004_staging_stg_salesforce__contact_history.md)。原013状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-004/docs/data_contract.yaml`，第432–490行。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/sql/staging/stg_salesforce__contact_history.sql`；gold SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/sql/staging/stg_salesforce__contact_history.sql`。精简包完整收录；下列补丁逐字给出定位原文。
- [完整事件记录](../014_trace_impl-004.json)；事件文件在该JSON的path中，可回查traces/dacomp_deimpl_prev.tar.gz。
- [查询原文与结果](../014_queries_impl-004.json)、[全部重跑记录](../014_reruns_impl-004.json)。

### SQL行号定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/sql/staging/stg_salesforce__contact_history.sql`
```text
10:         CAST("last_activity_date" AS DATE) AS last_activity_date,
24:         CAST(hash("_fivetran_start", "_fivetran_end") AS VARCHAR) AS history_unique_key
```

gold：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/sql/staging/stg_salesforce__contact_history.sql`
```text
11:         current_timestamp as created_date,
21:         -- Apply validation rule for last_activity_date
23:             when last_activity_date is not null and last_activity_date > current_date then null
24:             when last_activity_date is not null and last_activity_date < '2020-01-01' then null
25:             else last_activity_date
26:         end as last_activity_date,
54:         concat(id, '_', current_timestamp::varchar) as history_unique_key
68:     cast(last_activity_date as date) as last_activity_date,
83:     cast(history_unique_key as varchar) as history_unique_key
93:         last_activity_date,
108:         history_unique_key
```

## 3. agent看过什么

event 1提供契约；event 15→16读取raw schema；event 17/25/29生成与修复hash表达式。未看到规定history_unique_key算法的业务文档。按contact_id对齐的只读诊断定位到last_activity_date 1行，而不是把无共同键时列计数0误作值一致。

已逐题核对event 1 message，包含本表契约完整原文；这不是把磁盘上存在的文档等同于agent已经阅读。schema输出、源数据值、运行日志分别处理。轨迹全量转录未删去截断标记；被截断的未显示部分不作为看到的证据。

## 4. 查询与重跑

核实查询实际执行 **1条**；核实代价：**需要查业务说明**。诊断查询不计入5条限制。重复执行的查询仍计数。

### V1：核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/salesforce.duckdb`

```sql
SELECT count(*) n,count(distinct id) ids,count(*) FILTER(WHERE last_activity_date < DATE '2020-01-01') old_activity,count(*) FILTER(WHERE last_activity_date > DATE '2026-10-25') future_activity,count(*) FILTER(WHERE mobile_phone <> '' AND length(regexp_replace(mobile_phone,'[^0-9]',''))<10) short_mobile,count(*) FILTER(WHERE mailing_postal_code <> '' AND length(trim(mailing_postal_code))<3) short_postal FROM raw.contact_history
```

结果：
```json
{
  "columns": [
    "n",
    "ids",
    "old_activity",
    "future_activity",
    "short_mobile",
    "short_postal"
  ],
  "rows": [
    [
      3000,
      2369,
      0,
      0,
      0,
      0
    ]
  ]
}
```

### D1：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`

```sql
SELECT count(*) n,count(distinct id) ids,count(*) FILTER(WHERE last_activity_date < DATE '2020-01-01') old_activity,count(*) FILTER(WHERE last_activity_date > DATE '2026-10-25') future_activity,count(*) FILTER(WHERE mobile_phone <> '' AND length(regexp_replace(mobile_phone,'[^0-9]',''))<10) short_mobile,count(*) FILTER(WHERE mailing_postal_code <> '' AND length(trim(mailing_postal_code))<3) short_postal FROM raw.contact_history
```

结果：
```json
{
  "columns": [
    "n",
    "ids",
    "old_activity",
    "future_activity",
    "short_mobile",
    "short_postal"
  ],
  "rows": [
    [
      3000,
      2369,
      0,
      0,
      0,
      0
    ]
  ]
}
```

### D_raw：诊断查询

数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/salesforce.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb']`

```sql
SELECT * FROM raw.contact_history
```

结果：
```json
{
  "result": {
    "columns_identical": true,
    "agent_rows": 3000,
    "gold_rows": 3000,
    "agent_only_rows": 0,
    "gold_only_rows": 0
  },
  "operation": "Python Counter of full typed rows, exact multiset difference"
}
```

### D_clock：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`

```sql
SELECT min(created_date),max(created_date),min(history_unique_key),max(history_unique_key) FROM staging.stg_salesforce__contact_history
```

结果：
```json
{
  "columns": [
    "min(created_date)",
    "max(created_date)",
    "min(history_unique_key)",
    "max(history_unique_key)"
  ],
  "rows": [
    [
      "2025-10-24 15:03:11.630125",
      "2025-10-24 15:03:11.630125",
      "00302EQ38cvTeOD_2025-10-24 15:03:11.630125+08",
      "003zzyPo1cN6qDC_2025-10-24 15:03:11.630125+08"
    ]
  ]
}
```

### D_activity：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`

```sql
SELECT contact_id,last_activity_date FROM staging.stg_salesforce__contact_history WHERE last_activity_date IS NULL
```

结果：
```json
{
  "columns": [
    "contact_id",
    "last_activity_date"
  ],
  "rows": [
    [
      "003jpvUgLoY7fm4",
      null
    ]
  ]
}
```

### D_clock：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`

```sql
SELECT min(created_date),max(created_date),min(history_unique_key),max(history_unique_key) FROM staging.stg_salesforce__contact_history
```

结果：
```json
{
  "columns": [
    "min(created_date)",
    "max(created_date)",
    "min(history_unique_key)",
    "max(history_unique_key)"
  ],
  "rows": [
    [
      "2025-10-24 15:03:11.630125",
      "2025-10-24 15:03:11.630125",
      "00302EQ38cvTeOD_2025-10-24 15:03:11.630125+08",
      "003zzyPo1cN6qDC_2025-10-24 15:03:11.630125+08"
    ]
  ]
}
```

### D_activity：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`

```sql
SELECT contact_id,last_activity_date FROM staging.stg_salesforce__contact_history WHERE last_activity_date IS NULL
```

结果：
```json
{
  "columns": [
    "contact_id",
    "last_activity_date"
  ],
  "rows": [
    [
      "003jpvUgLoY7fm4",
      null
    ]
  ]
}
```

### 比较口径

原件均READ_ONLY；只把本节点引用表复制到data/014_work私有DuckDB后执行。staging输入来自agent留存库raw；003/008上游直接复制gold，实现CS。固定原评分的comparison_columns与key_columns；L0为lower/trim/NULL规范化，L1数字及布尔归一，L2数值两位小数，L3再放宽日期时间到日期。键始终固定L0，不在宽松档位重新归一。

无共同键时逐列0表示无可比较行，不表示一致。重复键按值/行多重集合抵消，报告最少不一致对数；同时公开额外行次数。为避免键被漏出整表判断，含键整表匹配用于本次U4；旧007式仅值列整表匹配并列展示。这里没有重定义原官方对错或修改旧状态。

比较列：`['account_id', 'contact_description', 'contact_name', 'email', 'first_name', 'is_deleted', 'last_activity_date', 'last_modified_date', 'last_name', 'lead_source', 'mailing_city', 'mailing_country', 'mailing_postal_code', 'mailing_state', 'mailing_street', 'mobile_phone', 'owner_id', 'phone', 'title']`；键：`['contact_id', 'account_id', 'mailing_postal_code', 'owner_id', 'history_unique_key']`。

### 留存基线（013材料来源）

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L1|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L2|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L3|3000|3000|3000|3000|0|0/0|3000/3000|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

### 重跑：baseline

不改SQL；建立本轮相同引擎、相同输入的比较基线。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L1|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L2|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L3|3000|3000|3000|3000|0|0/0|3000/3000|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

### 重跑：history_key

只替换以下原文（其余字节经验证不变）：
```sql
CAST(hash("_fivetran_start", "_fivetran_end") AS VARCHAR)
```
替换为：
```sql
concat(id, '_', current_timestamp::varchar)
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L1|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L2|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L3|3000|3000|3000|3000|0|0/0|3000/3000|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

### 重跑：activity_rule

只替换以下原文（其余字节经验证不变）：
```sql
CAST("last_activity_date" AS DATE) AS last_activity_date
```
替换为：
```sql
CASE WHEN last_activity_date > CURRENT_DATE OR last_activity_date < DATE '2020-01-01' THEN NULL ELSE CAST(last_activity_date AS DATE) END AS last_activity_date
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L1|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L2|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L3|3000|3000|3000|3000|0|0/0|3000/3000|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

### 重跑：history_key_frozen

只替换以下原文（其余字节经验证不变）：
```sql
CAST(hash("_fivetran_start", "_fivetran_end") AS VARCHAR)
```
替换为：
```sql
concat(id, '_', '2025-10-24 15:03:11.630125+08')
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|3000|3000|0|0|1|0/0|1/1|False|False|
|L1|3000|3000|0|0|1|0/0|1/1|False|False|
|L2|3000|3000|0|0|1|0/0|1/1|False|False|
|L3|3000|3000|0|0|1|0/0|1/1|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|1|1|1|1|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

### 重跑：activity_rule_gold_day

只替换以下原文（其余字节经验证不变）：
```sql
CAST("last_activity_date" AS DATE) AS last_activity_date
```
替换为：
```sql
CASE WHEN last_activity_date > DATE '2025-10-24' OR last_activity_date < DATE '2020-01-01' THEN NULL ELSE CAST(last_activity_date AS DATE) END AS last_activity_date
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|3000|3000|3000|3000|0|0/0|3000/3000|False|True|
|L1|3000|3000|3000|3000|0|0/0|3000/3000|False|True|
|L2|3000|3000|3000|3000|0|0/0|3000/3000|False|True|
|L3|3000|3000|3000|3000|0|0/0|3000/3000|False|True|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

### gold SQL在同一私有输入上的诊断

这是诊断，不是局部修复，也不用于证明U4。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L1|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L2|3000|3000|3000|3000|0|0/0|3000/3000|False|False|
|L3|3000|3000|3000|3000|0|0/0|3000/3000|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

## 5. 类别和把握

- 主要原因：**A**（归因判断）。
- 参与因素：O（残余1行运行日期边界）。
- 标记：无。
- 把握：**中**。
- 重跑是否满足U第4条件：是（固定gold时刻的key干预减少超过一半；仅诊断，不支持U）。

hash方案与concat方案是未规定的标识约定；没有可以仅凭agent可见数据证明错误的数据命题P。

## 规则问题

U4的数值条件能被一个A类方案变更满足，不能据此反推U。固定gold时刻属于诊断性对齐、使用gold信息，不能冒充agent当时可做的核实。契约日期校验虽遗漏，但按2026当前日补写不改善差异；按gold日界才改善，因此不单独计为C参与因素。

共同问题：手册第1节“不预设类别分布”与末句“希望未核实假设多”存在张力；本次以逐条证据条件为准，不按期望调整分布。U3“没看过任何足以判断P的东西”与“证据曾出现但被忽略仍归U”按后者作为例外解释。
