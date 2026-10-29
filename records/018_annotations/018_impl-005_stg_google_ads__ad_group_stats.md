# impl-005 / stg_google_ads__ad_group_stats（v2定稿）

## 1. 差异描述与判定

campaign来源列选择导致9985行键不同；契约和可见关联数据均未明确应选base还是直接campaign。

已核实：014查询两列不同9985/10000，campaign_source单改L2整表匹配。新增016-V1显示两个候选均能关联campaign_history的id（各10000行）；016-V2经base_ad_group关联ad_group_history，10000对中直接campaign符合父表11对、base符合14对。该数据不能给出单一明确来源。v1禁止用gold选择证明映射正确，因此由U改A。L0基线19985行/239672格，改来源后10000行/21395格，L2为0；DECIMAL/DOUBLE对照只降低少量格子，行数不变，不在本表所选行数口径列参与因素。 A项仅表示差异取决于契约未定的选择，不据gold实现认定agent做错。

主要原因：**A**；把握：**中**。
参与因素：无：三项数值类型对照在所选行数口径均不降。标记：无。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-005_stg_google_ads__ad_group_stats.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-005_staging_stg_google_ads__ad_group_stats.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-005/docs/data_contract.yaml` 第442–479行。
- [原始轨迹转录](../014_trace_impl-005.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-005.json)；[015三方raw核对](../015_raw_impl-005.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_google_ads__ad_group_stats
      description: "Cleaned and validated ad group performance statistics"
      source_table: "raw.ad_group_stats_data"
      columns:
        - name: source_relation
          data_type: VARCHAR(100)
        - name: account_id
          data_type: VARCHAR(20)
          constraints: [not_null]
        - name: date_day
          data_type: DATE
          constraints: [not_null]
        - name: ad_group_id
          data_type: VARCHAR(20)
          constraints: [not_null]
        - name: campaign_id
          data_type: VARCHAR(20)
          constraints: [not_null]
        - name: ad_network_type
          data_type: VARCHAR(20)
          validation_rules:
            - rule: "ad_network_type IN ('SEARCH', 'DISPLAY', 'MIXED', 'YOUTUBE')"
              on_failure: nullify_field
        - name: device
          data_type: VARCHAR(20)
        - name: clicks
          data_type: BIGINT
        - name: spend
          data_type: DECIMAL(15,2)
        - name: impressions
          data_type: BIGINT
        - name: conversions
          data_type: DECIMAL(10,2)
        - name: conversions_value
          data_type: DECIMAL(15,2)
        - name: view_through_conversions
          data_type: BIGINT
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql`
```sql
   1: WITH base AS (
   2:     SELECT 'google_ads'::VARCHAR AS source_relation, *
   3:     FROM raw.ad_group_stats_data
   4: ),
   5: validated AS (
   6:     SELECT source_relation, CAST(customer_id AS VARCHAR(20)) account_id, try_cast(date AS DATE) date_day, CAST(base_ad_group AS VARCHAR(20)) ad_group_id, CAST(campaign_base_campaign AS VARCHAR(20)) campaign_id, case when ad_network_type in ('SEARCH','DISPLAY','MIXED','YOUTUBE') then ad_network_type end ad_network_type, device, clicks, CAST(cost_micros / 1000000.0 AS DECIMAL(15,2)) spend, impressions, CAST(conversions AS DECIMAL(10,2)) conversions, CAST(conversions_value AS DECIMAL(15,2)) conversions_value, view_through_conversions
   7:     FROM base
   8: )
   9: SELECT *
  10: FROM validated
  11: WHERE account_id is not null and date_day is not null and ad_group_id is not null and campaign_id is not null
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql`
```sql
   1: with base as (
   2:     select *
   3:     from raw.ad_group_stats_data
   4: ),
   5: 
   6: validated as (
   7:     select
   8:         -- Platform identification per YAML spec (line 683)
   9:         'google_ads' as platform,
  10:         'google_ads' as source_relation,
  11: 
  12:         -- Core dimensions from YAML spec (lines 684-695)
  13:         CAST(customer_id AS VARCHAR) as account_id,
  14:         CAST(date AS DATE) as date_day,
  15:         CAST(base_ad_group AS VARCHAR) as ad_group_id,
  16:         CAST(campaign_id AS VARCHAR) as campaign_id,
  17:         CAST(ad_network_type AS VARCHAR) as ad_network_type,
  18:         CAST(device AS VARCHAR) as device,
  19: 
  20:         -- Core metrics from raw data per YAML spec (lines 696-734)
  21:         coalesce(try_cast(active_view_impressions AS BIGINT), 0) as active_view_impressions,
  22:         coalesce(try_cast(active_view_measurable_impressions AS BIGINT), 0) as active_view_measurable_impressions,
  23:         coalesce(try_cast(clicks AS BIGINT), 0) as clicks,
  24:         coalesce(try_cast(impressions AS BIGINT), 0) as impressions,
  25:         coalesce(try_cast(interactions AS BIGINT), 0) as interactions,
  26:         coalesce(try_cast(conversions AS DOUBLE), 0.0) as conversions,
  27:         coalesce(try_cast(conversions_value AS DOUBLE), 0.0) as conversions_value,
  28:         coalesce(try_cast(view_through_conversions AS BIGINT), 0) as view_through_conversions,
  29:         coalesce(try_cast(cost_micros AS BIGINT), 0) as cost_micros,
  30:         coalesce(try_cast(active_view_measurable_cost_micros AS BIGINT), 0) as active_view_measurable_cost_micros,
  31:         interaction_event_types,
  32: 
  33:         -- Derived metrics from raw data per YAML spec (lines 727-733)
  34:         cost_micros / 1000000.0 as cost,
  35:         active_view_measurable_cost_micros / 1000000.0 as active_view_measurable_cost,
  36: 
  37:         -- Quality actions per YAML spec - timestamp for tracking (line 757)
  38:         CURRENT_TIMESTAMP as _dbt_loaded_at
  39: 
  40:     from base
  41: 
  42:     -- Quality actions per YAML specification (lines 25-36)
  43:     -- Remove rows with severe data quality issues
  44:     WHERE CAST(date AS DATE) <= CURRENT_DATE
  45:       AND CAST(date AS DATE) >= '2020-01-01'
  46:       AND account_id is not null
  47:       AND ad_group_id is not null
  48:       AND campaign_id is not null
  49:       -- Nullify invalid fields when record is still useful
  50:       AND (ad_network_type is null OR ad_network_type IN ('SEARCH', 'DISPLAY', 'MIXED', 'YOUTUBE'))
  51: ),
  52: 
  53: metrics_calculated as (
  54:     select
  55:         platform,
  56:         source_relation,
  57:         account_id,
  58:         date_day,
  59:         ad_group_id,
  60:         campaign_id,
  61:         ad_network_type,
  62:         device,
  63:         active_view_impressions,
  64:         active_view_measurable_impressions,
  65:         clicks,
  66:         impressions,
  67:         interactions,
  68:         conversions,
  69:         conversions_value,
  70:         view_through_conversions,
  71:         cost_micros,
  72:         cost,
  73:         cost as spend,  -- Add spend alias for downstream compatibility
  74:         active_view_measurable_cost_micros,
  75:         active_view_measurable_cost,
  76: 
  77:         -- Calculate derived fields per YAML spec (lines 735-755)
  78:         CASE
  79:             WHEN active_view_measurable_impressions > 0
  80:             THEN CAST(active_view_impressions AS DOUBLE) / CAST(active_view_measurable_impressions AS DOUBLE)
  81:             ELSE 0.0
  82:         END as active_view_viewability,
  83: 
  84:         CASE
  85:             WHEN impressions > 0
  86:             THEN CAST(active_view_measurable_impressions AS DOUBLE) / CAST(impressions AS DOUBLE)
  87:             ELSE 0.0
  88:         END as active_view_measurability,
  89: 
  90:         CASE
  91:             WHEN impressions > 0
  92:             THEN CAST(clicks AS DOUBLE) / CAST(impressions AS DOUBLE)
  93:             ELSE 0.0
  94:         END as click_through_rate,
  95: 
  96:         CASE
  97:             WHEN clicks > 0
  98:             THEN cost / CAST(clicks AS DOUBLE)
  99:             ELSE 0.0
 100:         END as cost_per_click,
 101: 
 102:         CASE
 103:             WHEN impressions > 0
 104:             THEN (cost / CAST(impressions AS DOUBLE)) * 1000.0
 105:             ELSE 0.0
 106:         END as cost_per_thousand_impressions,
 107: 
 108:         CASE
 109:             WHEN conversions > 0
 110:             THEN cost / CAST(conversions AS DOUBLE)
 111:             ELSE 0.0
 112:         END as cost_per_conversion,
 113: 
 114:         interaction_event_types,
 115:         _dbt_loaded_at
 116: 
 117:     from validated
 118: )
 119: 
 120: select
 121:     platform,
 122:     source_relation,
 123:     account_id,
 124:     date_day,
 125:     ad_group_id,
 126:     campaign_id,
 127:     ad_network_type,
 128:     device,
 129:     active_view_impressions,
 130:     active_view_measurable_impressions,
 131:     clicks,
 132:     impressions,
 133:     interactions,
 134:     conversions,
 135:     conversions_value,
 136:     view_through_conversions,
 137:     cost_micros,
 138:     spend,
 139:     active_view_measurable_cost_micros,
 140:     active_view_measurable_cost,
 141:     active_view_viewability,
 142:     active_view_measurability,
 143:     click_through_rate,
 144:     cost_per_click,
 145:     cost_per_thousand_impressions,
 146:     cost_per_conversion,
 147:     interaction_event_types,
 148:     _dbt_loaded_at
 149: from metrics_calculated
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.ad_group_stats_data|gold_vs_initial|True|True|True||
|raw.ad_group_stats_data|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event 1含契约；event 13→14查看raw列结构；event 15选定campaign_base_campaign。全部49事件中未找到两列等值性、不同值计数或能决定两列等价的业务说明。列名同时出现只证明知道列存在，不证明核实过等价。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|campaign_source|A|看到了但没提|14|

### campaign_source：看到了但没提

看到了两个campaign来源列；最终报告讨论数值/日期、其他mart规则及source_relation，未说明这两个campaign候选的取舍。

事件 **14**，字段`content`；[轨迹原文](../014_trace_impl-005.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/14.json`。
```text
None, None), ('base_ad_group', 'VARCHAR', 'YES', None, None, None), ('campaign_base_campaign', 'VARCHAR', 'YES', None, None, None), ('campaign_id', 'VARCHAR', 'YES', None, None, None), ('clicks', 'BIGINT', 'YES', None, None, None), ('conversions', 'DOUBLE', 'YES', None, None, None), ('conversions_value', 'DOUBLE', 'YES', None, None, None), ('cost_micros', 'BIGINT', 'YES', None, None, None), ('device', 'VARCHAR', 'YES', None, None, None), ('id', 'BIGINT', 'YES', None, None, None), ('impressions', 'BIGINT', 'YES', None, None, None), ('interaction_event_types', 'VARCHAR', 'YES', None, None, None), ('interactions', 'BIGINT', 'YES', None, None, None), ('view_through_conversions', 'BIGINT', 'YES', None, None, None)]
[('ACC61393167557', '2022-04-23 00:00:00.000 +0800', 199, 0.829, 11046500, 239, 0.377, 'MIXED', 'AD_96523691001', 'CAM94269068771', 'CAM15753005768', 5, 0.4, 52.66, 21330460, 'TABLET', 9860686206, 532
```

已检视49个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **3条**；018新增核实查询 **0条**。核实代价：多条查询。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-005.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **3条**（含014复用；本轮新增2条）；核实代价档：**多条查询**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 014-V1 / 核实查询

来源：`records/014_queries_impl-005.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/google_ads.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE cast(campaign_base_campaign AS VARCHAR) IS DISTINCT FROM cast(campaign_id AS VARCHAR)) different_campaign,count(*) FILTER(WHERE ad_network_type IS NOT NULL AND ad_network_type NOT IN ('SEARCH','DISPLAY','MIXED','YOUTUBE')) invalid_network,count(*) FILTER(WHERE try_cast(date AS DATE)<DATE '2020-01-01' OR try_cast(date AS DATE)>DATE '2026-10-25') outside_date FROM raw.ad_group_stats_data
```
结果原文：
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

### 014-D1 / 诊断查询

来源：`records/014_queries_impl-005.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/google_ads.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE cast(campaign_base_campaign AS VARCHAR) IS DISTINCT FROM cast(campaign_id AS VARCHAR)) different_campaign,count(*) FILTER(WHERE ad_network_type IS NOT NULL AND ad_network_type NOT IN ('SEARCH','DISPLAY','MIXED','YOUTUBE')) invalid_network,count(*) FILTER(WHERE try_cast(date AS DATE)<DATE '2020-01-01' OR try_cast(date AS DATE)>DATE '2026-10-25') outside_date FROM raw.ad_group_stats_data
```
结果原文：
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

### 014-D_raw / 诊断查询

来源：`records/014_queries_impl-005.json`；数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/google_ads.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/google_ads.duckdb']`。

```sql
SELECT * FROM raw.ad_group_stats_data
```
结果原文：
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

### 016-V1 / 核实查询

来源：`records/016_queries_impl-005.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/google_ads.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.campaign_history_data h WHERE h.id=cast(s.campaign_id as varchar))) direct_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.campaign_history_data h WHERE h.id=cast(s.campaign_base_campaign as varchar))) base_matches FROM raw.ad_group_stats_data s
```
结果原文：
```json
{
  "columns": [
    "n",
    "direct_matches",
    "base_matches"
  ],
  "rows": [
    [
      10000,
      10000,
      10000
    ]
  ]
}
```

### 016-V2 / 核实查询

来源：`records/016_queries_impl-005.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/google_ads.duckdb`。

```sql
SELECT count(*) matched_pairs,count(*) FILTER(WHERE cast(h.campaign_id AS VARCHAR)=cast(s.campaign_id AS VARCHAR)) direct_parent_matches,count(*) FILTER(WHERE cast(h.campaign_id AS VARCHAR)=cast(s.campaign_base_campaign AS VARCHAR)) base_parent_matches FROM raw.ad_group_stats_data s JOIN raw.ad_group_history_data h ON cast(s.base_ad_group AS VARCHAR)=cast(h.id AS VARCHAR)
```
结果原文：
```json
{
  "columns": [
    "matched_pairs",
    "direct_parent_matches",
    "base_parent_matches"
  ],
  "rows": [
    [
      10000,
      11,
      14
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['account_id', 'ad_group_id', 'campaign_id']`；比较列（与键取并集）：`['account_id', 'ad_group_id', 'ad_network_type', 'campaign_id', 'clicks', 'conversions', 'conversions_value', 'date_day', 'device', 'impressions', 'spend', 'view_through_conversions']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：records/014_reruns_impl-005.json

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|campaign_source|19985→10000|239672→21395|L2|
|spend_type|19985→19985|239672→239657|无|
|conversions_type|19985→19985|239672→239657|无|
|value_type|19985→19985|239672→239670|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|10000|10000|9985|9985|0/0|15|19985|239672|False|
|L1|10000|10000|9985|9985|0/0|15|19985|239655|False|
|L2|10000|10000|9985|9985|0/0|0|19970|239640|False|
|L3|10000|10000|9985|9985|0/0|0|19970|239640|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
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

### 重跑 baseline

SQL：`data/014_work/impl-005/baseline.sql`；SHA-256：`35b7d35bac34f4628dd8b6db13330fb6947104ba63011b39e922026d5279166d`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|10000|10000|9985|9985|0/0|15|19985|239672|False|
|L1|10000|10000|9985|9985|0/0|15|19985|239655|False|
|L2|10000|10000|9985|9985|0/0|0|19970|239640|False|
|L3|10000|10000|9985|9985|0/0|0|19970|239640|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
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

### 重跑 campaign_source

SQL：`data/014_work/impl-005/campaign_source.sql`；SHA-256：`f8d68d1e18e55a430055880608307417f0a4d5ebb651f214821fcf329737a357`。

唯一原文位置offset=275，替换前：
```sql
CAST(campaign_base_campaign AS VARCHAR(20))
```
替换后：
```sql
CAST(campaign_id AS VARCHAR(20))
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|10000|10000|0|0|0/0|10000|10000|21395|False|
|L1|10000|10000|0|0|0/0|9999|9999|9999|False|
|L2|10000|10000|0|0|0/0|0|0|0|True|
|L3|10000|10000|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L2**。

|共同键比较列|L0不同格|L1|L2|L3|
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

### 重跑 spend_type

SQL：`data/014_work/impl-005/spend_type.sql`；SHA-256：`8792f740df66147bbe1b02d3b6e827003c9be82b5b83849e4b0815764b569038`。

唯一原文位置offset=458，替换前：
```sql
CAST(cost_micros / 1000000.0 AS DECIMAL(15,2))
```
替换后：
```sql
cost_micros / 1000000.0
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|10000|10000|9985|9985|0/0|15|19985|239657|False|
|L1|10000|10000|9985|9985|0/0|0|19970|239640|False|
|L2|10000|10000|9985|9985|0/0|0|19970|239640|False|
|L3|10000|10000|9985|9985|0/0|0|19970|239640|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
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

### 重跑 conversions_type

SQL：`data/014_work/impl-005/conversions_type.sql`；SHA-256：`f8719adb5f5ff475d2d96f09b5404e22db5f6cb8cf574ae9c482a330d65cdea0`。

唯一原文位置offset=525，替换前：
```sql
CAST(conversions AS DECIMAL(10,2))
```
替换后：
```sql
CAST(conversions AS DOUBLE)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|10000|10000|9985|9985|0/0|15|19985|239657|False|
|L1|10000|10000|9985|9985|0/0|15|19985|239655|False|
|L2|10000|10000|9985|9985|0/0|0|19970|239640|False|
|L3|10000|10000|9985|9985|0/0|0|19970|239640|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
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

### 重跑 value_type

SQL：`data/014_work/impl-005/value_type.sql`；SHA-256：`9dfb8a6515b5a5ed671a93117fc6e0d5c08fe779227ccb826b8eafb06e60d6f8`。

唯一原文位置offset=573，替换前：
```sql
CAST(conversions_value AS DECIMAL(15,2))
```
替换后：
```sql
CAST(conversions_value AS DOUBLE)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|10000|10000|9985|9985|0/0|15|19985|239670|False|
|L1|10000|10000|9985|9985|0/0|15|19985|239655|False|
|L2|10000|10000|9985|9985|0/0|0|19970|239640|False|
|L3|10000|10000|9985|9985|0/0|0|19970|239640|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
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

### 复用gold SQL同输入诊断

用于诊断，不是单点修复证据。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|10000|10000|0|0|0/0|0|0|0|True|
|L1|10000|10000|0|0|0/0|0|0|0|True|
|L2|10000|10000|0|0|0/0|0|0|0|True|
|L3|10000|10000|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
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

## 5. 逐项类别及U门槛

表级主要原因：**A**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|campaign_source|A|19985→10000|239672→21395|L2|

重跑是否满足U第4条件：**是（只改campaign来源后L2完全匹配）**。

不能把“两列不相等”直接升级为“选base这一列错误”的P；前者已反证等价，后者仍缺契约或可见数据的唯一指向。U4数值条件成立并不足以判U。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：是：U改A；v1要求agent可见关系能明确决定来源，本次关系核实未满足。。此字段不代替本次与016/017的对比。

## 规则问题

来源映射按v2第3节新增口径处理。该表行数已能选出主因，参与因素也沿用行数口径；三项精度差异可诊断但不以换格子口径另行纳入。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
