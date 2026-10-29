# impl-005 / stg_google_ads__ad_group_stats

## 1. 错在哪里

把campaign_base_campaign当作campaign_id，9985行选错键；单改来源列后L2整表一致。

已核实：10000行中9985行两列值不同，原结果只有15行落入共同键。agent把campaign_base_campaign投影为campaign_id；gold取同名campaign_id。只把这一处CAST的来源列换为campaign_id，其余字节不动，L2完全匹配；L0剩余数值类型与精度差异。归因判断：U，P是这两个campaign列可互换。数值声明中agent的DECIMAL符合契约，gold采用DOUBLE，列为O参与因素，不反过来要求agent违反类型声明。

## 2. 依据

- 起点：[013精简包](../013_packages/013_impl-005_staging_stg_google_ads__ad_group_stats.md)。原013状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-005/docs/data_contract.yaml`，第442–479行。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql`；gold SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql`。精简包完整收录；下列补丁逐字给出定位原文。
- [完整事件记录](../014_trace_impl-005.json)；事件文件在该JSON的path中，可回查traces/dacomp_deimpl_prev.tar.gz。
- [查询原文与结果](../014_queries_impl-005.json)、[全部重跑记录](../014_reruns_impl-005.json)。

### SQL行号定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql`
```text
6:     SELECT source_relation, CAST(customer_id AS VARCHAR(20)) account_id, try_cast(date AS DATE) date_day, CAST(base_ad_group AS VARCHAR(20)) ad_group_id, CAST(campaign_base_campaign AS VARCHAR(20)) campaign_id, case when ad_network_type in ('SEARCH','DISPLAY','MIXED','YOUTUBE') then ad_network_type end ad_network_type, device, clicks, CAST(cost_micros / 1000000.0 AS DECIMAL(15,2)) spend, impressions, CAST(conversions AS DECIMAL(10,2)) conversions, CAST(conversions_value AS DECIMAL(15,2)) conversions_value, view_through_conversions
11: WHERE account_id is not null and date_day is not null and ad_group_id is not null and campaign_id is not null
```

gold：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql`
```text
16:         CAST(campaign_id AS VARCHAR) as campaign_id,
26:         coalesce(try_cast(conversions AS DOUBLE), 0.0) as conversions,
27:         coalesce(try_cast(conversions_value AS DOUBLE), 0.0) as conversions_value,
28:         coalesce(try_cast(view_through_conversions AS BIGINT), 0) as view_through_conversions,
48:       AND campaign_id is not null
60:         campaign_id,
68:         conversions,
69:         conversions_value,
70:         view_through_conversions,
73:         cost as spend,  -- Add spend alias for downstream compatibility
109:             WHEN conversions > 0
110:             THEN cost / CAST(conversions AS DOUBLE)
126:     campaign_id,
134:     conversions,
135:     conversions_value,
136:     view_through_conversions,
138:     spend,
```

## 3. agent看过什么

event 1含契约；event 13→14查看raw列结构；event 15选定campaign_base_campaign。全部49事件中未找到两列等值性、不同值计数或能决定两列等价的业务说明。列名同时出现只证明知道列存在，不证明核实过等价。

已逐题核对event 1 message，包含本表契约完整原文；这不是把磁盘上存在的文档等同于agent已经阅读。schema输出、源数据值、运行日志分别处理。轨迹全量转录未删去截断标记；被截断的未显示部分不作为看到的证据。

## 4. 查询与重跑

核实查询实际执行 **1条**；核实代价：**一条查询**。诊断查询不计入5条限制。重复执行的查询仍计数。

### V1：核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/google_ads.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE cast(campaign_base_campaign AS VARCHAR) IS DISTINCT FROM cast(campaign_id AS VARCHAR)) different_campaign,count(*) FILTER(WHERE ad_network_type IS NOT NULL AND ad_network_type NOT IN ('SEARCH','DISPLAY','MIXED','YOUTUBE')) invalid_network,count(*) FILTER(WHERE try_cast(date AS DATE)<DATE '2020-01-01' OR try_cast(date AS DATE)>DATE '2026-10-25') outside_date FROM raw.ad_group_stats_data
```

结果：
```json
{
  "columns": [
    "n",
    "different_campaign",
    "invalid_network",
    "outside_date"
  ],
  "rows": [
    [
      10000,
      9985,
      0,
      0
    ]
  ]
}
```

### D1：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/google_ads.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE cast(campaign_base_campaign AS VARCHAR) IS DISTINCT FROM cast(campaign_id AS VARCHAR)) different_campaign,count(*) FILTER(WHERE ad_network_type IS NOT NULL AND ad_network_type NOT IN ('SEARCH','DISPLAY','MIXED','YOUTUBE')) invalid_network,count(*) FILTER(WHERE try_cast(date AS DATE)<DATE '2020-01-01' OR try_cast(date AS DATE)>DATE '2026-10-25') outside_date FROM raw.ad_group_stats_data
```

结果：
```json
{
  "columns": [
    "n",
    "different_campaign",
    "invalid_network",
    "outside_date"
  ],
  "rows": [
    [
      10000,
      9985,
      0,
      0
    ]
  ]
}
```

### D_raw：诊断查询

数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/google_ads.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/google_ads.duckdb']`

```sql
SELECT * FROM raw.ad_group_stats_data
```

结果：
```json
{
  "result": {
    "columns_identical": true,
    "agent_rows": 10000,
    "gold_rows": 10000,
    "agent_only_rows": 0,
    "gold_only_rows": 0
  },
  "operation": "Python Counter of full typed rows, exact multiset difference"
}
```

### 比较口径

原件均READ_ONLY；只把本节点引用表复制到data/014_work私有DuckDB后执行。staging输入来自agent留存库raw；003/008上游直接复制gold，实现CS。固定原评分的comparison_columns与key_columns；L0为lower/trim/NULL规范化，L1数字及布尔归一，L2数值两位小数，L3再放宽日期时间到日期。键始终固定L0，不在宽松档位重新归一。

无共同键时逐列0表示无可比较行，不表示一致。重复键按值/行多重集合抵消，报告最少不一致对数；同时公开额外行次数。为避免键被漏出整表判断，含键整表匹配用于本次U4；旧007式仅值列整表匹配并列展示。这里没有重定义原官方对错或修改旧状态。

比较列：`['account_id', 'ad_group_id', 'ad_network_type', 'campaign_id', 'clicks', 'conversions', 'conversions_value', 'date_day', 'device', 'impressions', 'spend', 'view_through_conversions']`；键：`['account_id', 'ad_group_id', 'campaign_id']`。

### 留存基线（013材料来源）

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|10000|10000|9985|9985|15|0/0|10000/10000|False|False|
|L1|10000|10000|9985|9985|15|0/0|10000/10000|False|False|
|L2|10000|10000|9985|9985|0|0/0|9985/9985|False|False|
|L3|10000|10000|9985|9985|0|0/0|9985/9985|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|ad_group_id|0|0|0|0|
|ad_network_type|0|0|0|0|
|campaign_id|0|0|0|0|
|clicks|0|0|0|0|
|conversions|15|0|0|0|
|conversions_value|2|0|0|0|
|date_day|0|0|0|0|
|device|0|0|0|0|
|impressions|0|0|0|0|
|spend|15|15|0|0|
|view_through_conversions|0|0|0|0|

### 重跑：baseline

不改SQL；建立本轮相同引擎、相同输入的比较基线。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|10000|10000|9985|9985|15|0/0|10000/10000|False|False|
|L1|10000|10000|9985|9985|15|0/0|10000/10000|False|False|
|L2|10000|10000|9985|9985|0|0/0|9985/9985|False|False|
|L3|10000|10000|9985|9985|0|0/0|9985/9985|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|ad_group_id|0|0|0|0|
|ad_network_type|0|0|0|0|
|campaign_id|0|0|0|0|
|clicks|0|0|0|0|
|conversions|15|0|0|0|
|conversions_value|2|0|0|0|
|date_day|0|0|0|0|
|device|0|0|0|0|
|impressions|0|0|0|0|
|spend|15|15|0|0|
|view_through_conversions|0|0|0|0|

### 重跑：campaign_source

只替换以下原文（其余字节经验证不变）：
```sql
CAST(campaign_base_campaign AS VARCHAR(20))
```
替换为：
```sql
CAST(campaign_id AS VARCHAR(20))
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|10000|10000|0|0|10000|0/0|10000/10000|False|False|
|L1|10000|10000|0|0|9999|0/0|9999/9999|False|False|
|L2|10000|10000|0|0|0|0/0|0/0|True|True|
|L3|10000|10000|0|0|0|0/0|0/0|True|True|

含键整表首次匹配档位：**L2**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|ad_group_id|0|0|0|0|
|ad_network_type|0|0|0|0|
|campaign_id|0|0|0|0|
|clicks|0|0|0|0|
|conversions|10000|0|0|0|
|conversions_value|1395|0|0|0|
|date_day|0|0|0|0|
|device|0|0|0|0|
|impressions|0|0|0|0|
|spend|10000|9999|0|0|
|view_through_conversions|0|0|0|0|

### 重跑：spend_type

只替换以下原文（其余字节经验证不变）：
```sql
CAST(cost_micros / 1000000.0 AS DECIMAL(15,2))
```
替换为：
```sql
cost_micros / 1000000.0
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|10000|10000|9985|9985|15|0/0|10000/10000|False|False|
|L1|10000|10000|9985|9985|0|0/0|9985/9985|False|False|
|L2|10000|10000|9985|9985|0|0/0|9985/9985|False|False|
|L3|10000|10000|9985|9985|0|0/0|9985/9985|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|ad_group_id|0|0|0|0|
|ad_network_type|0|0|0|0|
|campaign_id|0|0|0|0|
|clicks|0|0|0|0|
|conversions|15|0|0|0|
|conversions_value|2|0|0|0|
|date_day|0|0|0|0|
|device|0|0|0|0|
|impressions|0|0|0|0|
|spend|0|0|0|0|
|view_through_conversions|0|0|0|0|

### 重跑：conversions_type

只替换以下原文（其余字节经验证不变）：
```sql
CAST(conversions AS DECIMAL(10,2))
```
替换为：
```sql
CAST(conversions AS DOUBLE)
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|10000|10000|9985|9985|15|0/0|10000/10000|False|False|
|L1|10000|10000|9985|9985|15|0/0|10000/10000|False|False|
|L2|10000|10000|9985|9985|0|0/0|9985/9985|False|False|
|L3|10000|10000|9985|9985|0|0/0|9985/9985|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|ad_group_id|0|0|0|0|
|ad_network_type|0|0|0|0|
|campaign_id|0|0|0|0|
|clicks|0|0|0|0|
|conversions|0|0|0|0|
|conversions_value|2|0|0|0|
|date_day|0|0|0|0|
|device|0|0|0|0|
|impressions|0|0|0|0|
|spend|15|15|0|0|
|view_through_conversions|0|0|0|0|

### 重跑：value_type

只替换以下原文（其余字节经验证不变）：
```sql
CAST(conversions_value AS DECIMAL(15,2))
```
替换为：
```sql
CAST(conversions_value AS DOUBLE)
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|10000|10000|9985|9985|15|0/0|10000/10000|False|False|
|L1|10000|10000|9985|9985|15|0/0|10000/10000|False|False|
|L2|10000|10000|9985|9985|0|0/0|9985/9985|False|False|
|L3|10000|10000|9985|9985|0|0/0|9985/9985|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|ad_group_id|0|0|0|0|
|ad_network_type|0|0|0|0|
|campaign_id|0|0|0|0|
|clicks|0|0|0|0|
|conversions|15|0|0|0|
|conversions_value|0|0|0|0|
|date_day|0|0|0|0|
|device|0|0|0|0|
|impressions|0|0|0|0|
|spend|15|15|0|0|
|view_through_conversions|0|0|0|0|

### gold SQL在同一私有输入上的诊断

这是诊断，不是局部修复，也不用于证明U4。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|10000|10000|0|0|0|0/0|0/0|True|True|
|L1|10000|10000|0|0|0|0/0|0/0|True|True|
|L2|10000|10000|0|0|0|0/0|0/0|True|True|
|L3|10000|10000|0|0|0|0/0|0/0|True|True|

含键整表首次匹配档位：**L0**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|ad_group_id|0|0|0|0|
|ad_network_type|0|0|0|0|
|campaign_id|0|0|0|0|
|clicks|0|0|0|0|
|conversions|0|0|0|0|
|conversions_value|0|0|0|0|
|date_day|0|0|0|0|
|device|0|0|0|0|
|impressions|0|0|0|0|
|spend|0|0|0|0|
|view_through_conversions|0|0|0|0|

## 5. 类别和把握

- 主要原因：**U**（归因判断）。
- 参与因素：O（DECIMAL与DOUBLE精度/表示差异，L2消失）。
- 标记：无。
- 把握：**高**。
- 重跑是否满足U第4条件：是（只改campaign来源后L2完全匹配）。

P：对本表每行，campaign_base_campaign与campaign_id可以作为同一个campaign_id使用。V1直接反证9985行；没有足以证明等价的可见证据；campaign_source单处干预L2匹配，四条件按本次解释满足。

## 规则问题

字段映射也可读为A：契约未给source_column。本次选择U，是因为代码所需的两列可互换可被数据直接否定、且局部修复有效；不把gold实现当作业务正确性的独立证明。若手册要求必须有额外语义文档才可确定哪列正确，此项应降为A/X。参与因素的数值差异在L0可见、L2为零，必须注明比较档位。

共同问题：手册第1节“不预设类别分布”与末句“希望未核实假设多”存在张力；本次以逐条证据条件为准，不按期望调整分布。U3“没看过任何足以判断P的东西”与“证据曾出现但被忽略仍归U”按后者作为例外解释。
