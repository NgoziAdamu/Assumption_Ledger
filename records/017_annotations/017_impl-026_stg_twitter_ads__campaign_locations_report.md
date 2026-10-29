# impl-026 / stg_twitter_ads__campaign_locations_report

## 1. 错在哪里

1500行date_day只差TIMESTAMP午夜与DATE表示；agent遵守契约TIMESTAMP，留存gold是DATE。

已核实：raw日期1500行均可解析且全为午夜；agent输出TIMESTAMP，留存gold类型DATE，L0–L2各1500行/1500格，L3已整表匹配。只把投影类型改DATE便L0匹配，属评测类型/表示与契约不一致的O。诊断还确认当前引擎执行gold文件的date_trunc(day,try_cast(... AS TIMESTAMP))表达式类型也是TIMESTAMP，因此不能假定SQL文件和留存gold类型完全一致；本轮date_day_type对照确实无改善。

## 2. 依据

- 起点：[013精简材料包](../013_packages/013_impl-026_staging_stg_twitter_ads__campaign_locations_report.md)；不修改既有官方判错状态。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml` 第118–154行。
- [完整轨迹](../017_trace_impl-026.json)，保留事件原文和原始路径；可回查授权归档`traces/dacomp_deimpl_prev.tar.gz`。
- [查询原文及结果](../017_queries_impl-026.json)、[重跑完整记录](../017_reruns_impl-026.json)、[原始表库存](../015_raw_impl-026.json)。
- [新增不确定性字段审计](../017_uncertainty_audit.json)、[本表依赖raw核对](../017_dependency_raw_audit.json)。
- [执行前指纹](../017_input_before.json)、[结束后指纹](../017_input_after.json)。本次前快照完成后才开始标注、查询和重跑。

### 契约原文

```yaml
    - name: stg_twitter_ads__campaign_locations_report
      description: "Daily campaign performance by country and placement with spend normalized from micro-units."
      source_table: raw.twitter_campaign_locations_report_data
      columns:
        - name: date_day
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: country
          data_type: VARCHAR
        - name: account_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: campaign_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: placement
          data_type: VARCHAR
        - name: clicks
          data_type: BIGINT
        - name: impressions
          data_type: BIGINT
        - name: spend_micro
          data_type: BIGINT
        - name: spend
          data_type: DOUBLE
          description: "Spend amount rounded to 2 decimal places in SQL."
        - name: url_clicks
          data_type: BIGINT
        - name: conversion_purchases_metric
          data_type: BIGINT
        - name: conversion_custom_metric
          data_type: BIGINT
        - name: conversion_purchases_sale_amount
          data_type: DOUBLE
        - name: conversion_custom_sale_amount
          data_type: DOUBLE
```

### SQL定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__campaign_locations_report.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: select
   2:     try_cast(date as timestamp) as date_day,
   3:     country_region as country,
   4:     account_id,
   5:     campaign_id,
   6:     placement,
   7:     clicks,
   8:     impressions,
   9:     billed_charge_local_micro as spend_micro,
  10:     round(billed_charge_local_micro / 1000000.0, 2) as spend,
  11:     url_clicks,
  12:     cast(null as bigint) as conversion_purchases_metric,
  13:     cast(null as bigint) as conversion_custom_metric,
  14:     cast(null as double) as conversion_purchases_sale_amount,
  15:     cast(null as double) as conversion_custom_sale_amount
  16: from raw.twitter_campaign_locations_report_data
```

gold（仅用于定位差异）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/staging/stg_twitter_ads__campaign_locations_report.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: select
   2:   date_trunc('day', try_cast(date as timestamp)) as date_day,
   3:   coalesce(country_region, country_region) as country,
   4:   account_id,
   5:   campaign_id,
   6:   placement,
   7:   clicks,
   8:   impressions,
   9:   billed_charge_local_micro as spend_micro,
  10:   round(billed_charge_local_micro/1000000.0, 2) as spend,
  11:   url_clicks,
  12:   0::BIGINT as conversion_purchases_metric,
  13:   0::BIGINT as conversion_custom_metric,
  14:   0.0::DOUBLE as conversion_purchases_sale_amount,
  15:   0.0::DOUBLE as conversion_custom_sale_amount
  16: from raw.twitter_campaign_locations_report_data
```

### 原始数据可评估性

下表复用015的完整表schema/行数/typed行哈希比较，只列本表静态传递依赖及双方SQL直接引用的raw。缺表不当作空表；gold与agent一致但二者不同于初始不自动排除（021/030）。

|依赖raw|比较|类型/列序相同|行数相同|typed行哈希相同|差异原因|
|---|---|---|---|---|---|
|raw.twitter_campaign_locations_report_data|gold_vs_initial|True|True|True||
|raw.twitter_campaign_locations_report_data|gold_vs_agent|True|True|True||

## 3. agent看过什么

event9→10看到了本表date为VARCHAR及2022-05-10、2022-12-15样例；event13选择TIMESTAMP，event25只把intermediate的date_day改DATE。event37提到缺失conversion字段，但那些字段不在本表官方比较列；没有明确说明本表DATE/TIMESTAMP取舍。

只把归档实际展示的内容视为已看到；磁盘有文件、命令包含表名或截断掉的部分，不等于看到相应数据值。

### 新增字段：是否意识到或提到相关不确定性

**看到了但没提**。只记录可见表述/信息，不由该档位推定错误类别。

event37说明缺失conversion列和其他模型歧义，但这些列不在本表评分列中；没有明确讨论本表date_day保留TIMESTAMP或改成DATE的选择。

event **10**，字段`content`；原路径`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/10.json`。
```text
twitter_campaign_locations_report_data
[('account_id', 'VARCHAR', 'YES', None, None, None), ('campaign_id', 'VARCHAR', 'YES', None, None, None), ('country_region', 'VARCHAR', 'YES', None, None, None), ('date', 'VARCHAR', 'YES', None, None, None), ('placement', 'VARCHAR', 'YES', None, None, None), ('_fivetran_synced', 'VARCHAR', 'YES', None, None, None), ('app_clicks', 'BIGINT', 'YES', None, None, None), ('billed_charge_local_micro', 'BIGINT', 'YES', None, None, None), ('billed_engagements', 'BIGINT', 'YES', None, None, None), ('card_engagements', 'BIGINT', 'YES', None, None, None), ('carousel_swipes', 'BIGINT', 'YES', None, None, None), ('clicks', 'BIGINT', 'YES', None, None, None), ('engagements', 'BIGINT', 'YES', None, None, None), ('follows', 'BIGINT', 'YES', None, None, None), ('impressions', 'BIGINT', 'YES', None, None, None), ('likes', 'BIGINT', 'YES', None, None, None), ('media_engagements', 'BIGINT', 'YES', None, None, None), ('media_views', 'BIGINT', 'YES', None, None, None), ('poll_card_vote', 'BIGINT', 'YES', None, None, None), ('qualified_impressions', 'BIGINT', 'YES', None, None, None), ('replies', 'BIGINT', 'YES', None, None, None), ('retweets', 'BIGINT', 'YES', None, None, None), ('tweets_send', 'BIGINT', 'YES', None, None, None), ('unfollows', 'BIGINT', 'YES', None, None, None), ('url_clicks', 'BIGINT', 'YES', None, None, None)]
[('18ce9i5owm5rx9g', 'zwucc3', 'JP', '2022-05-10', 'ALL_ON_TWITTER', '2022-07-08 11:18:14.000Z', 143, 43887, 1610, 24, 100, 2012, 1815, 3, 14969, 529, 560, 166, 123, 13599, 249, 18, 7, 13, 964), ('18ce1yuy27fr4a1', '0776x0', 'BR', '2022-12-15', 'ALL_ON_TWITTER', '2021-06-06 12:36:27.000Z', 843, 483119, 1454, 316, 122, 1825, 1568, 96, 11800, 552, 453, 1602, 21, 11620, 224, 173, 7, 1, 87)]

 twitter_campaign_regions_report_data
[('account_id', 'VARCHAR', 'YES', None, None, None), ('campaign_id', 'VARCHAR', 'YES', None, None, None
```

归档逐项扫描39个事件；本批thought/args.thought字段均为空，不能由此推断agent没有内部思考。“已提到”的原句来自final_thought中的最终报告；“看到了但没提”依据可见工具返回，不把SQL代码本身当口头说明。长工具输出仅摘录连续原文，截取范围见JSON；不是说agent只看到了这个摘录。

## 4. 查询与重跑

核实查询执行 **1条**（失败尝试也计入）；核实代价档：**一条查询**。每张≤5条，均只查agent当时可见数据。诊断可以查gold，不计入此数。

### V1 / 核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`。
```sql
SELECT count(*) n,count(*) FILTER(WHERE try_cast(date AS TIMESTAMP) IS NULL) parse_null,count(*) FILTER(WHERE try_cast(date AS TIMESTAMP) IS DISTINCT FROM cast(try_cast(date AS DATE) AS TIMESTAMP)) not_midnight,min(cast(date AS VARCHAR)),max(cast(date AS VARCHAR)) FROM raw.twitter_campaign_locations_report_data
```
结果原文：
```json
{
  "executed_utc": "2026-10-29T11:33:05.766491+00:00",
  "columns": [
    "n",
    "parse_null",
    "not_midnight",
    "min(CAST(date AS VARCHAR))",
    "max(CAST(date AS VARCHAR))"
  ],
  "rows": [
    [
      1500,
      0,
      0,
      "2020-01-01",
      "2023-12-30"
    ]
  ]
}
```

### D1 / 诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/twitter.duckdb`。
```sql
SELECT (SELECT data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_twitter_ads__campaign_locations_report' AND column_name='date_day') AS retained_date_type,typeof(try_cast(date AS TIMESTAMP)) AS cast_type,typeof(date_trunc('day',try_cast(date AS TIMESTAMP))) AS gold_sql_type,count(*) AS row_count FROM raw.twitter_campaign_locations_report_data GROUP BY ALL
```
```json
{
  "columns": [
    "retained_date_type",
    "cast_type",
    "gold_sql_type",
    "row_count"
  ],
  "rows": [
    [
      "DATE",
      "TIMESTAMP",
      "TIMESTAMP",
      1500
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['account_id', 'campaign_id']`；原评分比较列：`['account_id', 'campaign_id', 'clicks', 'country', 'date_day', 'impressions', 'placement', 'spend', 'spend_micro', 'url_clicks']`。与键取并集，不自行纳入原评分排除列。

全部原数据库以READ_ONLY连接或ATTACH；本次建表和改SQL只在`data/017_work/`。staging用agent留存raw，021/027用gold上游CS。每个试验从相同原SQL独立替换，不累积其他修复。

共同时间控制：`[]`。023/025/028沿原筛查候选日期；030沿010已经验证的兼容2025-10-13日期（不声称唯一执行日）；共同控制先应用到基线及全部干预，不能作为某个局部修复的功劳。

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|date_day_type|1500→1500|1500→1500|L3|
|date_cast|1500→0|1500→0|L0|

### 原留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1500|1500|0|0|0/0|1500|1500|1500|False|
|L1|1500|1500|0|0|0/0|1500|1500|1500|False|
|L2|1500|1500|0|0|0/0|1500|1500|1500|False|
|L3|1500|1500|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L3**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|clicks|0|0|0|0|
|country|0|0|0|0|
|date_day|1500|1500|1500|0|
|impressions|0|0|0|0|
|placement|0|0|0|0|
|spend|0|0|0|0|
|spend_micro|0|0|0|0|
|url_clicks|0|0|0|0|

### 重跑 baseline

SQL：`data/017_work/impl-026/baseline.sql`；SHA-256：`29e95b4719b734ababb65592956b90ae3655f0cf378e5f6917f0645e176fe23a`。

同输入、同时间控制、不增加因果改动的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1500|1500|0|0|0/0|1500|1500|1500|False|
|L1|1500|1500|0|0|0/0|1500|1500|1500|False|
|L2|1500|1500|0|0|0/0|1500|1500|1500|False|
|L3|1500|1500|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L3**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|clicks|0|0|0|0|
|country|0|0|0|0|
|date_day|1500|1500|1500|0|
|impressions|0|0|0|0|
|placement|0|0|0|0|
|spend|0|0|0|0|
|spend_micro|0|0|0|0|
|url_clicks|0|0|0|0|

### 重跑 date_day_type

SQL：`data/017_work/impl-026/date_day_type.sql`；SHA-256：`8f8bd057a20da65db202b138428021d1e584cb2a9e198c1bc43af3c41db54702`。

唯一替换位置offset=11；原文：
```sql
try_cast(date as timestamp) as date_day
```
新文：
```sql
date_trunc('day', try_cast(date as timestamp)) as date_day
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1500|1500|0|0|0/0|1500|1500|1500|False|
|L1|1500|1500|0|0|0/0|1500|1500|1500|False|
|L2|1500|1500|0|0|0/0|1500|1500|1500|False|
|L3|1500|1500|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L3**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|clicks|0|0|0|0|
|country|0|0|0|0|
|date_day|1500|1500|1500|0|
|impressions|0|0|0|0|
|placement|0|0|0|0|
|spend|0|0|0|0|
|spend_micro|0|0|0|0|
|url_clicks|0|0|0|0|

### 重跑 date_cast

SQL：`data/017_work/impl-026/date_cast.sql`；SHA-256：`6df3aa4ea7cb8d104cb9c3da881c7ab768c7ba17f204585a9f92fd42a39ba261`。

唯一替换位置offset=11；原文：
```sql
try_cast(date as timestamp) as date_day
```
新文：
```sql
try_cast(date as date) as date_day
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1500|1500|0|0|0/0|0|0|0|True|
|L1|1500|1500|0|0|0/0|0|0|0|True|
|L2|1500|1500|0|0|0/0|0|0|0|True|
|L3|1500|1500|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|clicks|0|0|0|0|
|country|0|0|0|0|
|date_day|0|0|0|0|
|impressions|0|0|0|0|
|placement|0|0|0|0|
|spend|0|0|0|0|
|spend_micro|0|0|0|0|
|url_clicks|0|0|0|0|

## 5. 类别、把握和对比

- 主要原因：**O**（归因判断）。
- 主因单项：date_cast。
- 参与因素：无；未评分的conversion占位不参与本次归因。
- 标记：无。
- 把握：**高**。
- 重跑是否满足U第4条件：是：单改为DATE后L0匹配；原基线只在L3匹配不单独证明U4。

所有本表源日期都能直接解析并且没有时分秒信息，不成立错误P；也没有依据把未评分的NULL conversion列当本次D主因。

与014相比是否变化：不适用（第三批首次标注）；也未修改016任何结论。

## 规则问题

本表013仍列待标注，但本次复核发现L3已经完全一致。按用户指定对象完成O标注，原004–016状态和记录不改。留存gold与当前gold SQL的类型差异已记录，不猜测是版本、执行路径还是文件演变造成。

2026-10-29用户确认补充：本表依赖原始表若agent留存与初始一致而gold不同，先诊断再标不可评估；若gold与初始一致而agent不同，则正常标注并追踪agent运行中的改动。不能把两种情况混淆。raw差异须限定到本表依赖；CS上游用gold。

新增字段统一口径：记录与实际差异机制相关的明确选择/可疑数据表述；不要求agent预知gold，也不把泛称“完成清洗”算作识别具体边界。021关于重复计数、029关于可选字段失败置NULL为适用范围较广的声明，单独注明并未点名本表异常；可见证据只能支持这一有限范围。该字段不增减U/C/D/I/A/O/X条件。
