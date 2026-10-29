# impl-007 / stg_apple_store__sales_subscription_event_summary（v2定稿）

## 1. 差异描述与判定

subscriber_id选vendor ID而gold选促销ID，700行键全不同；另有568行marketing duration选了另一字段。

已核实：两边700行；subscriber_id_vendor与promotional_offer_id每行不同，契约只有subscriber_id VARCHAR，没有来源说明。单改subscriber来源后键对齐，但568行marketing_opt_in_duration仍不同；单改marketing来源使比较值列匹配，却不改变700+700个键不相交。归因判断：主因为A，数据能证明两种ID不等价，却不能决定subscriber_id应指vendor还是促销ID。source_relation也不同但不参与本次评分，单改无效。 A项仅表示差异取决于契约未定的选择，不据gold实现认定agent做错。

主要原因：**A**；把握：**中**。
参与因素：无（固定键口径）；marketing映射差异另列诊断。标记：无。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-007_stg_apple_store__sales_subscription_event_summary.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-007_staging_stg_apple_store__sales_subscription_event_summary.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml` 第462–494行。
- [原始轨迹转录](../014_trace_impl-007.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-007.json)；[015三方raw核对](../015_raw_impl-007.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_apple_store__sales_subscription_event_summary
      description: "Subscription event summary from Apple Store Connect"
      source_table: "raw.sales_subscription_event_summary"
      columns:
        - name: source_relation
          data_type: VARCHAR
        - name: date_day
          data_type: DATE
        - name: app_id
          data_type: VARCHAR
        - name: app_name
          data_type: VARCHAR
        - name: subscription_id
          data_type: VARCHAR
        - name: subscription_name
          data_type: VARCHAR
        - name: event_type
          data_type: VARCHAR
        - name: country
          data_type: VARCHAR
        - name: subscriber_id
          data_type: VARCHAR
        - name: standard_subscription_duration
          data_type: VARCHAR
        - name: proceeds_reason
          data_type: VARCHAR
        - name: marketing_opt_in_duration
          data_type: VARCHAR
        - name: consecutive_paid_periods
          data_type: BIGINT
        - name: quantity
          data_type: BIGINT
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_event_summary.sql`
```sql
   1: SELECT
   2:     CAST(app_apple_id AS VARCHAR) AS source_relation,
   3:     TRY_CAST(SUBSTR(CAST(event_date AS VARCHAR), 1, 10) AS DATE) AS date_day,
   4:     CAST(app_apple_id AS VARCHAR) AS app_id,
   5:     CAST(app_name AS VARCHAR) AS app_name,
   6:     subscription_apple_id AS subscription_id,
   7:     CAST(subscription_name AS VARCHAR) AS subscription_name,
   8:     CAST(event AS VARCHAR) AS event_type,
   9:     CAST(country AS VARCHAR) AS country,
  10:     CAST(subscriber_id_vendor AS VARCHAR) AS subscriber_id,
  11:     subscription_duration AS standard_subscription_duration,
  12:     CAST(proceeds_reason AS VARCHAR) AS proceeds_reason,
  13:     CAST(subscription_offer_duration AS VARCHAR) AS marketing_opt_in_duration,
  14:     TRY_CAST(consecutive_paid_periods AS BIGINT) AS consecutive_paid_periods,
  15:     CAST(quantity AS BIGINT) AS quantity
  16: FROM raw.sales_subscription_event_summary
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_event_summary.sql`
```sql
   1: with base as (
   2:     select *
   3:     from raw.sales_subscription_event_summary
   4: ),
   5: 
   6: final as (
   7:     select
   8:         'apple_store' as source_relation,
   9:         cast(event_date as date) as date_day,
  10:         cast(app_name as varchar) as app_name,
  11:         cast(app_apple_id as varchar) as app_id,
  12:         cast(subscription_name as varchar) as subscription_name,
  13:         cast(subscription_apple_id as varchar) as subscription_id,
  14:         cast(subscription_duration as varchar) as standard_subscription_duration,
  15:         cast(marketing_opt_in_duration as varchar) as marketing_opt_in_duration,
  16:         cast(promotional_offer_id as varchar) as subscriber_id,
  17:         cast(event as varchar) as event_type,
  18:         cast(country as varchar) as country,
  19:         cast(quantity as bigint) as quantity,
  20:         cast(proceeds_reason as varchar) as proceeds_reason,
  21:         cast(consecutive_paid_periods as bigint) as consecutive_paid_periods
  22:     from base
  23: )
  24: 
  25: select * from final
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.sales_subscription_event_summary|gold_vs_initial|True|True|True||
|raw.sales_subscription_event_summary|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event 1提供简短契约；event 13→14完整显示raw有marketing_opt_in_duration、subscription_offer_duration、subscriber_id_vendor、promotional_offer_id；event 23明确选了后两种映射中的vendor及offer duration。没有看到业务说明来定义subscriber_id，未找到两种duration等值核实。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|subscriber_source|A|只有通用策略说明|65|

### subscriber_source：只有通用策略说明

最终报告正文的写入尝试；event66返回路径不存在，event67再次尝试也失败，归档没有finish.final_thought。仅证明轨迹里写出了报告文字，不声称报告成功送达。未点明subscriber_id选vendor而非促销ID。

事件 **65**，字段`args.command`；[轨迹原文](../014_trace_impl-007.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/65.json`。
```text
Apple 订阅 summary/event 字段有若干原始字段与 staging 字段语义不完全一致，使用可用列映射且转换兼容字段类型。若这类字段用于正式订阅财务决策，应以源端字段定义进一步确认。
```

已检视70个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **2条**；018新增核实查询 **0条**。核实代价：需要查业务说明。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-007.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **2条**（含014复用；本轮新增1条）；核实代价档：**需要查业务说明**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 014-V1 / 核实查询

来源：`records/014_queries_impl-007.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE marketing_opt_in_duration IS DISTINCT FROM subscription_offer_duration) durations_differ,count(*) FILTER(WHERE cast(promotional_offer_id AS VARCHAR) IS DISTINCT FROM subscriber_id_vendor) ids_differ,count(marketing_opt_in_duration) marketing_present FROM raw.sales_subscription_event_summary
```
结果原文：
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

### 014-D1 / 诊断查询

来源：`records/014_queries_impl-007.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/app_reporting.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE marketing_opt_in_duration IS DISTINCT FROM subscription_offer_duration) durations_differ,count(*) FILTER(WHERE cast(promotional_offer_id AS VARCHAR) IS DISTINCT FROM subscriber_id_vendor) ids_differ,count(marketing_opt_in_duration) marketing_present FROM raw.sales_subscription_event_summary
```
结果原文：
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

### 014-D_raw / 诊断查询

来源：`records/014_queries_impl-007.json`；数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/app_reporting.duckdb']`。

```sql
SELECT * FROM raw.sales_subscription_event_summary
```
结果原文：
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

### 016-V1 / 核实查询

来源：`records/016_queries_impl-007.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE marketing_opt_in_duration IS DISTINCT FROM subscription_offer_duration) different_duration,count(*) FILTER(WHERE marketing_opt_in_duration IS NULL) marketing_null FROM raw.sales_subscription_event_summary
```
结果原文：
```json
{
  "columns": [
    "n",
    "different_duration",
    "marketing_null"
  ],
  "rows": [
    [
      700,
      568,
      0
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['date_day', 'app_id', 'subscription_id', 'subscriber_id', 'country']`；比较列（与键取并集）：`['app_id', 'app_name', 'consecutive_paid_periods', 'country', 'date_day', 'event_type', 'marketing_opt_in_duration', 'proceeds_reason', 'quantity', 'standard_subscription_duration', 'subscription_id', 'subscription_name']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：records/014_reruns_impl-007.json

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|subscriber_source|1400→568|18200→568|无|
|marketing_source|1400→1400|18200→18200|无|
|source_relation|1400→1400|18200→18200|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|700|700|700|700|0/0|0|1400|18200|False|
|L1|700|700|700|700|0/0|0|1400|18200|False|
|L2|700|700|700|700|0/0|0|1400|18200|False|
|L3|700|700|700|700|0/0|0|1400|18200|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
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

### 重跑 baseline

SQL：`data/014_work/impl-007/baseline.sql`；SHA-256：`e9f4dcc3fbf3ef1aba0eac8ae101f344c91fd444c430b3475ec51a0918932233`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|700|700|700|700|0/0|0|1400|18200|False|
|L1|700|700|700|700|0/0|0|1400|18200|False|
|L2|700|700|700|700|0/0|0|1400|18200|False|
|L3|700|700|700|700|0/0|0|1400|18200|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
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

### 重跑 subscriber_source

SQL：`data/014_work/impl-007/subscriber_source.sql`；SHA-256：`20b0b31ee44eefd15d66765bceacc298d2c3a947de1a58ccacdafc3f49d66ddc`。

唯一原文位置offset=421，替换前：
```sql
CAST(subscriber_id_vendor AS VARCHAR)
```
替换后：
```sql
CAST(promotional_offer_id AS VARCHAR)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|700|700|0|0|0/0|568|568|568|False|
|L1|700|700|0|0|0/0|568|568|568|False|
|L2|700|700|0|0|0/0|568|568|568|False|
|L3|700|700|0|0|0/0|568|568|568|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
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

### 重跑 marketing_source

SQL：`data/014_work/impl-007/marketing_source.sql`；SHA-256：`1141589a29c69e9480597e6e907700a3db8876d6562f0bc156a1f17949ebe310`。

唯一原文位置offset=599，替换前：
```sql
CAST(subscription_offer_duration AS VARCHAR)
```
替换后：
```sql
CAST(marketing_opt_in_duration AS VARCHAR)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|700|700|700|700|0/0|0|1400|18200|False|
|L1|700|700|700|700|0/0|0|1400|18200|False|
|L2|700|700|700|700|0/0|0|1400|18200|False|
|L3|700|700|700|700|0/0|0|1400|18200|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
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

### 重跑 source_relation

SQL：`data/014_work/impl-007/source_relation.sql`；SHA-256：`e22e87f28747c0db876037edfc9dff36773ec886eec46e7c60a64aa96739f910`。

唯一原文位置offset=11，替换前：
```sql
CAST(app_apple_id AS VARCHAR) AS source_relation
```
替换后：
```sql
'apple_store' AS source_relation
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|700|700|700|700|0/0|0|1400|18200|False|
|L1|700|700|700|700|0/0|0|1400|18200|False|
|L2|700|700|700|700|0/0|0|1400|18200|False|
|L3|700|700|700|700|0/0|0|1400|18200|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
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

### 复用gold SQL同输入诊断

用于诊断，不是单点修复证据。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|700|700|0|0|0/0|0|0|0|True|
|L1|700|700|0|0|0/0|0|0|0|True|
|L2|700|700|0|0|0/0|0|0|0|True|
|L3|700|700|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
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

## 5. 逐项类别及U门槛

表级主要原因：**A**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|subscriber_source|A|1400→568|18200→568|无|

重跑是否满足U第4条件：**是（subscriber_source行1400→568，减少59.4%；来源歧义仍归A）**。

subscriber_id和marketing duration均缺source mapping。字段值不同不足以证明存在可判真假的业务可替代命题；按v1不据gold选择归U。marketing单改不减少含键规模，不能列参与因素。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：是：主要A不变；修正014对U4数值条件的否定，并撤下缺唯一语义依据的未核实假设标记。。此字段不代替本次与016/017的对比。

## 规则问题

最终报告写入命令中有订阅字段语义不完全一致的一般警示，但未点名subscriber_id；按通用策略记档。写文件失败不消除轨迹中已经写出的文字，但不宣称用户收到最终报告。字段选择缺契约定义，描述为A差异，不说agent做错。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
