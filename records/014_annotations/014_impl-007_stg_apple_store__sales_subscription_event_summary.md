# impl-007 / stg_apple_store__sales_subscription_event_summary

## 1. 错在哪里

subscriber_id选vendor ID而gold选促销ID，700行键全不同；另有568行marketing duration选了另一字段。

已核实：两边700行；subscriber_id_vendor与promotional_offer_id每行不同，契约只有subscriber_id VARCHAR，没有来源说明。单改subscriber来源后键对齐，但568行marketing_opt_in_duration仍不同；单改marketing来源使比较值列匹配，却不改变700+700个键不相交。归因判断：主因为A，数据能证明两种ID不等价，却不能决定subscriber_id应指vendor还是促销ID。source_relation也不同但不参与本次评分，单改无效。

## 2. 依据

- 起点：[013精简包](../013_packages/013_impl-007_staging_stg_apple_store__sales_subscription_event_summary.md)。原013状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`，第462–494行。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_event_summary.sql`；gold SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_event_summary.sql`。精简包完整收录；下列补丁逐字给出定位原文。
- [完整事件记录](../014_trace_impl-007.json)；事件文件在该JSON的path中，可回查traces/dacomp_deimpl_prev.tar.gz。
- [查询原文与结果](../014_queries_impl-007.json)、[全部重跑记录](../014_reruns_impl-007.json)。

### SQL行号定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_event_summary.sql`
```text
2:     CAST(app_apple_id AS VARCHAR) AS source_relation,
10:     CAST(subscriber_id_vendor AS VARCHAR) AS subscriber_id,
13:     CAST(subscription_offer_duration AS VARCHAR) AS marketing_opt_in_duration,
```

gold：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_event_summary.sql`
```text
8:         'apple_store' as source_relation,
15:         cast(marketing_opt_in_duration as varchar) as marketing_opt_in_duration,
16:         cast(promotional_offer_id as varchar) as subscriber_id,
```

## 3. agent看过什么

event 1提供简短契约；event 13→14完整显示raw有marketing_opt_in_duration、subscription_offer_duration、subscriber_id_vendor、promotional_offer_id；event 23明确选了后两种映射中的vendor及offer duration。没有看到业务说明来定义subscriber_id，未找到两种duration等值核实。

已逐题核对event 1 message，包含本表契约完整原文；这不是把磁盘上存在的文档等同于agent已经阅读。schema输出、源数据值、运行日志分别处理。轨迹全量转录未删去截断标记；被截断的未显示部分不作为看到的证据。

## 4. 查询与重跑

核实查询实际执行 **1条**；核实代价：**需要查业务说明**。诊断查询不计入5条限制。重复执行的查询仍计数。

### V1：核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE marketing_opt_in_duration IS DISTINCT FROM subscription_offer_duration) durations_differ,count(*) FILTER(WHERE cast(promotional_offer_id AS VARCHAR) IS DISTINCT FROM subscriber_id_vendor) ids_differ,count(marketing_opt_in_duration) marketing_present FROM raw.sales_subscription_event_summary
```

结果：
```json
{
  "columns": [
    "n",
    "durations_differ",
    "ids_differ",
    "marketing_present"
  ],
  "rows": [
    [
      700,
      568,
      700,
      700
    ]
  ]
}
```

### D1：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE marketing_opt_in_duration IS DISTINCT FROM subscription_offer_duration) durations_differ,count(*) FILTER(WHERE cast(promotional_offer_id AS VARCHAR) IS DISTINCT FROM subscriber_id_vendor) ids_differ,count(marketing_opt_in_duration) marketing_present FROM raw.sales_subscription_event_summary
```

结果：
```json
{
  "columns": [
    "n",
    "durations_differ",
    "ids_differ",
    "marketing_present"
  ],
  "rows": [
    [
      700,
      568,
      700,
      700
    ]
  ]
}
```

### D_raw：诊断查询

数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/app_reporting.duckdb']`

```sql
SELECT * FROM raw.sales_subscription_event_summary
```

结果：
```json
{
  "result": {
    "columns_identical": true,
    "agent_rows": 700,
    "gold_rows": 700,
    "agent_only_rows": 0,
    "gold_only_rows": 0
  },
  "operation": "Python Counter of full typed rows, exact multiset difference"
}
```

### 比较口径

原件均READ_ONLY；只把本节点引用表复制到data/014_work私有DuckDB后执行。staging输入来自agent留存库raw；003/008上游直接复制gold，实现CS。固定原评分的comparison_columns与key_columns；L0为lower/trim/NULL规范化，L1数字及布尔归一，L2数值两位小数，L3再放宽日期时间到日期。键始终固定L0，不在宽松档位重新归一。

无共同键时逐列0表示无可比较行，不表示一致。重复键按值/行多重集合抵消，报告最少不一致对数；同时公开额外行次数。为避免键被漏出整表判断，含键整表匹配用于本次U4；旧007式仅值列整表匹配并列展示。这里没有重定义原官方对错或修改旧状态。

比较列：`['app_id', 'app_name', 'consecutive_paid_periods', 'country', 'date_day', 'event_type', 'marketing_opt_in_duration', 'proceeds_reason', 'quantity', 'standard_subscription_duration', 'subscription_id', 'subscription_name']`；键：`['date_day', 'app_id', 'subscription_id', 'subscriber_id', 'country']`。

### 留存基线（013材料来源）

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|700|700|700|700|0|0/0|700/700|False|False|
|L1|700|700|700|700|0|0/0|700/700|False|False|
|L2|700|700|700|700|0|0/0|700/700|False|False|
|L3|700|700|700|700|0|0/0|700/700|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|app_id|0|0|0|0|
|app_name|0|0|0|0|
|consecutive_paid_periods|0|0|0|0|
|country|0|0|0|0|
|date_day|0|0|0|0|
|event_type|0|0|0|0|
|marketing_opt_in_duration|0|0|0|0|
|proceeds_reason|0|0|0|0|
|quantity|0|0|0|0|
|standard_subscription_duration|0|0|0|0|
|subscription_id|0|0|0|0|
|subscription_name|0|0|0|0|

### 重跑：baseline

不改SQL；建立本轮相同引擎、相同输入的比较基线。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|700|700|700|700|0|0/0|700/700|False|False|
|L1|700|700|700|700|0|0/0|700/700|False|False|
|L2|700|700|700|700|0|0/0|700/700|False|False|
|L3|700|700|700|700|0|0/0|700/700|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|app_id|0|0|0|0|
|app_name|0|0|0|0|
|consecutive_paid_periods|0|0|0|0|
|country|0|0|0|0|
|date_day|0|0|0|0|
|event_type|0|0|0|0|
|marketing_opt_in_duration|0|0|0|0|
|proceeds_reason|0|0|0|0|
|quantity|0|0|0|0|
|standard_subscription_duration|0|0|0|0|
|subscription_id|0|0|0|0|
|subscription_name|0|0|0|0|

### 重跑：subscriber_source

只替换以下原文（其余字节经验证不变）：
```sql
CAST(subscriber_id_vendor AS VARCHAR)
```
替换为：
```sql
CAST(promotional_offer_id AS VARCHAR)
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|700|700|0|0|568|0/0|568/568|False|False|
|L1|700|700|0|0|568|0/0|568/568|False|False|
|L2|700|700|0|0|568|0/0|568/568|False|False|
|L3|700|700|0|0|568|0/0|568/568|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|app_id|0|0|0|0|
|app_name|0|0|0|0|
|consecutive_paid_periods|0|0|0|0|
|country|0|0|0|0|
|date_day|0|0|0|0|
|event_type|0|0|0|0|
|marketing_opt_in_duration|568|568|568|568|
|proceeds_reason|0|0|0|0|
|quantity|0|0|0|0|
|standard_subscription_duration|0|0|0|0|
|subscription_id|0|0|0|0|
|subscription_name|0|0|0|0|

### 重跑：marketing_source

只替换以下原文（其余字节经验证不变）：
```sql
CAST(subscription_offer_duration AS VARCHAR)
```
替换为：
```sql
CAST(marketing_opt_in_duration AS VARCHAR)
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|700|700|700|700|0|0/0|700/700|False|True|
|L1|700|700|700|700|0|0/0|700/700|False|True|
|L2|700|700|700|700|0|0/0|700/700|False|True|
|L3|700|700|700|700|0|0/0|700/700|False|True|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|app_id|0|0|0|0|
|app_name|0|0|0|0|
|consecutive_paid_periods|0|0|0|0|
|country|0|0|0|0|
|date_day|0|0|0|0|
|event_type|0|0|0|0|
|marketing_opt_in_duration|0|0|0|0|
|proceeds_reason|0|0|0|0|
|quantity|0|0|0|0|
|standard_subscription_duration|0|0|0|0|
|subscription_id|0|0|0|0|
|subscription_name|0|0|0|0|

### 重跑：source_relation

只替换以下原文（其余字节经验证不变）：
```sql
CAST(app_apple_id AS VARCHAR) AS source_relation
```
替换为：
```sql
'apple_store' AS source_relation
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|700|700|700|700|0|0/0|700/700|False|False|
|L1|700|700|700|700|0|0/0|700/700|False|False|
|L2|700|700|700|700|0|0/0|700/700|False|False|
|L3|700|700|700|700|0|0/0|700/700|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|app_id|0|0|0|0|
|app_name|0|0|0|0|
|consecutive_paid_periods|0|0|0|0|
|country|0|0|0|0|
|date_day|0|0|0|0|
|event_type|0|0|0|0|
|marketing_opt_in_duration|0|0|0|0|
|proceeds_reason|0|0|0|0|
|quantity|0|0|0|0|
|standard_subscription_duration|0|0|0|0|
|subscription_id|0|0|0|0|
|subscription_name|0|0|0|0|

### gold SQL在同一私有输入上的诊断

这是诊断，不是局部修复，也不用于证明U4。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|700|700|0|0|0|0/0|0/0|True|True|
|L1|700|700|0|0|0|0/0|0/0|True|True|
|L2|700|700|0|0|0|0/0|0/0|True|True|
|L3|700|700|0|0|0|0/0|0/0|True|True|

含键整表首次匹配档位：**L0**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|app_id|0|0|0|0|
|app_name|0|0|0|0|
|consecutive_paid_periods|0|0|0|0|
|country|0|0|0|0|
|date_day|0|0|0|0|
|event_type|0|0|0|0|
|marketing_opt_in_duration|0|0|0|0|
|proceeds_reason|0|0|0|0|
|quantity|0|0|0|0|
|standard_subscription_duration|0|0|0|0|
|subscription_id|0|0|0|0|
|subscription_name|0|0|0|0|

## 5. 类别和把握

- 主要原因：**A**（归因判断）。
- 参与因素：无（固定键口径）；marketing映射差异另列诊断。
- 标记：存在未核实假设，但不是判错原因。
- 把握：**中**。
- 重跑是否满足U第4条件：否（按包含固定键的整表口径）。

候选P：subscription_offer_duration可替代raw.marketing_opt_in_duration。V1显示568行不同；但单独修复在固定键整表差异中没有改善，按第4节加“存在未核实假设，但不是判错原因”。这是本次操作性判据，不宣称该字段映射在语义上正确。

## 规则问题

值比较列不包含subscriber_id。若沿用旧L0整表值多重集合定义，marketing单改即可称完全匹配；若包含固定键则仍全部键错。本次U4用后者，保守不判U，并同时公开前者。该键遮蔽效应使“不是判错原因”标记措辞过强：marketing确实是一个可见的独立差异，建议后续规则明确。

共同问题：手册第1节“不预设类别分布”与末句“希望未核实假设多”存在张力；本次以逐条证据条件为准，不按期望调整分布。U3“没看过任何足以判断P的东西”与“证据曾出现但被忽略仍归U”按后者作为例外解释。
