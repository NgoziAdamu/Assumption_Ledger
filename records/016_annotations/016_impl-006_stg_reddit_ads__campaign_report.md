# impl-006 / stg_reddit_ads__campaign_report

## 1. 错在哪里

20个指标各造成1200格差异：spend候选被覆盖、四个可映射指标直接填NULL，其余为未规定指标口径。

已核实：1200行/24000格，20个单列干预各减少1200格、行数均不变，故20处并列。spend在event19同一映射中先含正确spend候选、后被重复键覆盖掉，归I。video_views/upvotes/downvotes/comments原始表分别有video_started/comment_upvotes/comment_downvotes/viewer_comments，但生成器没有逐字段数据判断就填NULL，按v1归D。video_view_rate、shares、saves、post_visits、profile_visits、community_joins、conversions、conversion_value、cost_per_video_view、cost_per_conversion、total_engagements、engagement_rate及ctr/cpc/ecpm输出共15项，缺直接列、统一汇总/公式或0与NULL约定，归A；这不声称这些值不存在任何可用业务定义。event95明确披露typed NULL，D加“已披露”。

## 2. 依据

- 起点：[013精简材料包](../013_packages/013_impl-006_staging_stg_reddit_ads__campaign_report.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml` 第1092–1148行。
- [原始轨迹转录](../014_trace_impl-006.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-006.json)；[015三方raw核对](../015_raw_impl-006.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: "stg_reddit_ads__campaign_report"
      description: "Staging table for Reddit Ads  Campaign Report"
      columns:
        - name: "platform"
          data_type: VARCHAR
        - name: "campaign_id"
          data_type: VARCHAR
        - name: "date_day"
          data_type: DATE
        - name: "account_id"
          data_type: VARCHAR
        - name: "impressions"
          data_type: INTEGER
        - name: "clicks"
          data_type: INTEGER
        - name: "spend"
          data_type: DECIMAL(18,2)
        - name: "video_views"
          data_type: INTEGER
        - name: "video_view_rate"
          data_type: DECIMAL(8,4)
        - name: "upvotes"
          data_type: INTEGER
        - name: "downvotes"
          data_type: INTEGER
        - name: "comments"
          data_type: INTEGER
        - name: "shares"
          data_type: INTEGER
        - name: "saves"
          data_type: INTEGER
        - name: "post_visits"
          data_type: INTEGER
        - name: "profile_visits"
          data_type: INTEGER
        - name: "community_joins"
          data_type: INTEGER
        - name: "conversions"
          data_type: INTEGER
        - name: "conversion_value"
          data_type: DECIMAL(18,2)
        - name: "click_through_rate"
          data_type: DOUBLE
        - name: "cost_per_click"
          data_type: DOUBLE
        - name: "cost_per_thousand_impressions"
          data_type: DOUBLE
        - name: "cost_per_video_view"
          data_type: DOUBLE
        - name: "cost_per_conversion"
          data_type: DOUBLE
        - name: "total_engagements"
          data_type: INTEGER
        - name: "engagement_rate"
          data_type: DOUBLE
        - name: "_dbt_loaded_at"
          data_type: TIMESTAMP WITH TIME ZONE
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_reddit_ads__campaign_report.sql`
```sql
   1: WITH source_rows AS (
   2:     SELECT * FROM raw.reddit_ads_campaign_report_data
   3: ),
   4: cleaned AS (
   5:     SELECT
   6:         'REDDIT_ADS' AS platform,
   7:         CAST(TRY_CAST("campaign_id" AS VARCHAR) AS VARCHAR) AS campaign_id,
   8:         CAST(TRY_CAST(date AS DATE) AS DATE) AS date_day,
   9:         TRY_CAST("account_id" AS VARCHAR) AS account_id,
  10:         CAST(TRY_CAST("impressions" AS BIGINT) AS INTEGER) AS impressions,
  11:         CAST(TRY_CAST("clicks" AS BIGINT) AS INTEGER) AS clicks,
  12:         CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend,
  13:         CAST(NULL::INTEGER AS INTEGER) AS video_views,
  14:         CAST(NULL::DECIMAL(8,4) AS DECIMAL(8,4)) AS video_view_rate,
  15:         CAST(NULL::INTEGER AS INTEGER) AS upvotes,
  16:         CAST(NULL::INTEGER AS INTEGER) AS downvotes,
  17:         CAST(NULL::INTEGER AS INTEGER) AS comments,
  18:         CAST(NULL::INTEGER AS INTEGER) AS shares,
  19:         CAST(NULL::INTEGER AS INTEGER) AS saves,
  20:         CAST(NULL::INTEGER AS INTEGER) AS post_visits,
  21:         CAST(NULL::INTEGER AS INTEGER) AS profile_visits,
  22:         CAST(NULL::INTEGER AS INTEGER) AS community_joins,
  23:         CAST(NULL::INTEGER AS INTEGER) AS conversions,
  24:         CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS conversion_value,
  25:         TRY_CAST("ctr" AS DOUBLE) AS click_through_rate,
  26:         TRY_CAST("cpc" AS DOUBLE) AS cost_per_click,
  27:         TRY_CAST("ecpm" AS DOUBLE) AS cost_per_thousand_impressions,
  28:         CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_video_view,
  29:         CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_conversion,
  30:         CAST(NULL::INTEGER AS INTEGER) AS total_engagements,
  31:         CAST(NULL::DOUBLE AS DOUBLE) AS engagement_rate,
  32:         CURRENT_TIMESTAMP AS _dbt_loaded_at
  33:     FROM source_rows
  34: )
  35: SELECT * FROM cleaned
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_reddit_ads__campaign_report.sql`
```sql
   1: -- Reddit Ads Campaign Report Staging Model
   2: -- Standardizes raw Reddit Ads campaign-level data for downstream consumption
   3: -- Removes Fivetran-specific logic and converts to DuckDB-compatible SQL
   4: 
   5: SELECT 
   6:     -- Platform Identifier
   7:     'reddit_ads' AS platform,
   8:     
   9:     -- Primary Keys
  10:     CAST(campaign_id AS VARCHAR) AS campaign_id,
  11:     CAST(date AS DATE) AS date_day,
  12:     
  13:     -- Campaign Attributes
  14:     CAST(account_id AS VARCHAR) AS account_id,
  15:     
  16:     -- Performance Metrics
  17:     CAST(impressions AS INTEGER) AS impressions,
  18:     CAST(clicks AS INTEGER) AS clicks,
  19:     CAST(spend AS DECIMAL(18,2)) AS spend,
  20:     
  21:     -- Reddit-specific Metrics (using available columns)
  22:     CAST(COALESCE(video_started, '0') AS INTEGER) AS video_views,
  23:     CAST(0 AS DECIMAL(8,4)) AS video_view_rate,
  24:     CAST(COALESCE(comment_upvotes, '0') AS INTEGER) AS upvotes,
  25:     CAST(COALESCE(comment_downvotes, '0') AS INTEGER) AS downvotes,
  26:     CAST(COALESCE(viewer_comments, '0') AS INTEGER) AS comments,
  27:     CAST(0 AS INTEGER) AS shares,
  28:     CAST(0 AS INTEGER) AS saves,
  29:     CAST(0 AS INTEGER) AS post_visits,
  30:     CAST(0 AS INTEGER) AS profile_visits,
  31:     CAST(0 AS INTEGER) AS community_joins,
  32:     
  33:     -- Conversion Metrics (using available columns)
  34:     CAST(0 AS INTEGER) AS conversions,
  35:     CAST(0 AS DECIMAL(18,2)) AS conversion_value,
  36:     
  37:     -- Calculated Metrics
  38:     CASE 
  39:         WHEN impressions > 0 THEN ROUND((CAST(clicks AS DECIMAL) / CAST(impressions AS DECIMAL)) * 100, 4)
  40:         ELSE 0 
  41:     END AS click_through_rate,
  42:     
  43:     CASE 
  44:         WHEN clicks > 0 THEN ROUND(spend / clicks, 2)
  45:         ELSE 0 
  46:     END AS cost_per_click,
  47:     
  48:     CASE 
  49:         WHEN impressions > 0 THEN ROUND((spend / impressions) * 1000, 2)
  50:         ELSE 0 
  51:     END AS cost_per_thousand_impressions,
  52:     
  53:     CASE 
  54:         WHEN CAST(COALESCE(video_started, '0') AS INTEGER) > 0 THEN ROUND(spend / CAST(COALESCE(video_started, '0') AS INTEGER), 2)
  55:         ELSE 0 
  56:     END AS cost_per_video_view,
  57:     
  58:     CASE 
  59:         WHEN 0 > 0 THEN ROUND(spend / 0, 2)
  60:         ELSE 0 
  61:     END AS cost_per_conversion,
  62:     
  63:     -- Engagement Metrics
  64:     (CAST(COALESCE(comment_upvotes, '0') AS INTEGER) + CAST(COALESCE(comment_downvotes, '0') AS INTEGER) + CAST(COALESCE(viewer_comments, '0') AS INTEGER) + 0) AS total_engagements,
  65:     
  66:     CASE 
  67:         WHEN impressions > 0 THEN ROUND((CAST((CAST(COALESCE(comment_upvotes, '0') AS INTEGER) + CAST(COALESCE(comment_downvotes, '0') AS INTEGER) + CAST(COALESCE(viewer_comments, '0') AS INTEGER) + 0) AS DECIMAL) / CAST(impressions AS DECIMAL)) * 100, 4)
  68:         ELSE 0 
  69:     END AS engagement_rate,
  70:     
  71:     -- Data Quality
  72:     CURRENT_TIMESTAMP AS _dbt_loaded_at
  73: 
  74: FROM raw.reddit_ads_campaign_report_data
  75: 
  76: WHERE date IS NOT NULL
  77:     AND campaign_id IS NOT NULL
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.reddit_ads_campaign_report_data|gold_vs_initial|True|True|True||
|raw.reddit_ads_campaign_report_data|gold_vs_agent|True|True|True||

## 3. agent看过什么

event 17→18输出raw列信息；event 19程序读取所有raw schema后生成表达式；event 95报告明确披露缺源字段采用类型化NULL及非完整业务实现。V1证明spend/video_started/comment_upvotes可用。未找到逐指标的明确业务口径说明或正确意图陈述。

区分event实际展示的契约/数据与磁盘上存在的资料；截断输出中未出现的部分不算agent已经看到。核实查询是标注者新增查询，不冒充agent执行过。

## 4. 查询与重跑

核实查询合计 **1条**（含014复用；本轮新增0条）；核实代价档：**一条查询**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 014-V1 / 核实查询

来源：`records/014_queries_impl-006.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`。

```sql
SELECT count(*) n,count(spend) spend_present,count(video_started) video_present,count(comment_upvotes) upvotes_present,count(*) FILTER(WHERE try_cast(ctr AS DOUBLE) IS DISTINCT FROM round(100.0*clicks/nullif(impressions,0),4)) ctr_different FROM raw.reddit_ads_campaign_report_data
```
结果原文：
```json
{
  "columns": [
    "n",
    "spend_present",
    "video_present",
    "upvotes_present",
    "ctr_different"
  ],
  "rows": [
    [
      1200,
      1200,
      1200,
      1200,
      1200
    ]
  ]
}
```

### 014-D1 / 诊断查询

来源：`records/014_queries_impl-006.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`。

```sql
SELECT count(*) n,count(spend) spend_present,count(video_started) video_present,count(comment_upvotes) upvotes_present,count(*) FILTER(WHERE try_cast(ctr AS DOUBLE) IS DISTINCT FROM round(100.0*clicks/nullif(impressions,0),4)) ctr_different FROM raw.reddit_ads_campaign_report_data
```
结果原文：
```json
{
  "columns": [
    "n",
    "spend_present",
    "video_present",
    "upvotes_present",
    "ctr_different"
  ],
  "rows": [
    [
      1200,
      1200,
      1200,
      1200,
      1200
    ]
  ]
}
```

### 014-D_raw / 诊断查询

来源：`records/014_queries_impl-006.json`；数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb']`。

```sql
SELECT * FROM raw.reddit_ads_campaign_report_data
```
结果原文：
```json
{
  "result": {
    "columns_identical": true,
    "agent_rows": 1200,
    "gold_rows": 1200,
    "agent_only_rows": 0,
    "gold_only_rows": 0
  },
  "operation": "Python Counter of full typed rows, exact multiset difference"
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['campaign_id']`；比较列（与键取并集）：`['account_id', 'campaign_id', 'click_through_rate', 'clicks', 'comments', 'community_joins', 'conversion_value', 'conversions', 'cost_per_click', 'cost_per_conversion', 'cost_per_thousand_impressions', 'cost_per_video_view', 'date_day', 'downvotes', 'engagement_rate', 'impressions', 'platform', 'post_visits', 'profile_visits', 'saves', 'shares', 'spend', 'total_engagements', 'upvotes', 'video_view_rate', 'video_views']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：records/014_reruns_impl-006.json

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|spend|1200→1200|24000→22800|无|
|video_views|1200→1200|24000→22800|无|
|video_view_rate|1200→1200|24000→22800|无|
|upvotes|1200→1200|24000→22800|无|
|downvotes|1200→1200|24000→22800|无|
|comments|1200→1200|24000→22800|无|
|shares|1200→1200|24000→22800|无|
|saves|1200→1200|24000→22800|无|
|post_visits|1200→1200|24000→22800|无|
|profile_visits|1200→1200|24000→22800|无|
|community_joins|1200→1200|24000→22800|无|
|conversions|1200→1200|24000→22800|无|
|conversion_value|1200→1200|24000→22800|无|
|cost_per_video_view|1200→1200|24000→22800|无|
|cost_per_conversion|1200→1200|24000→22800|无|
|total_engagements|1200→1200|24000→22800|无|
|engagement_rate|1200→1200|24000→22800|无|
|click_through_rate|1200→1200|24000→22800|无|
|cost_per_click|1200→1200|24000→22800|无|
|cost_per_thousand_impressions|1200→1200|24000→22800|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|24000|False|
|L1|1200|1200|0|0|0/0|1200|1200|24000|False|
|L2|1200|1200|0|0|0/0|1200|1200|24000|False|
|L3|1200|1200|0|0|0/0|1200|1200|24000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 baseline

SQL：`data/014_work/impl-006/baseline.sql`；SHA-256：`5f29b62488b3998f55c87dc9ebcefa3057672fed9544e110f91ffc29094c7cd2`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|24000|False|
|L1|1200|1200|0|0|0/0|1200|1200|24000|False|
|L2|1200|1200|0|0|0/0|1200|1200|24000|False|
|L3|1200|1200|0|0|0/0|1200|1200|24000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 spend

SQL：`data/014_work/impl-006/spend.sql`；SHA-256：`9060091f2b79e27c22288e2184cd4765c976bfc4b3d619fc042a9160a5954ebd`。

唯一原文位置offset=476，替换前：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend
```
替换后：
```sql
CAST(spend AS DECIMAL(18,2)) AS spend
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|0|0|0|0|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 video_views

SQL：`data/014_work/impl-006/video_views.sql`；SHA-256：`4bf561a8299db23ef72a0bf0893451ef6094071ef233a96e1f1b8a579dd42571`。

唯一原文位置offset=537，替换前：
```sql
CAST(NULL::INTEGER AS INTEGER) AS video_views
```
替换后：
```sql
CAST(COALESCE(video_started, '0') AS INTEGER) AS video_views
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|0|0|0|0|

### 重跑 video_view_rate

SQL：`data/014_work/impl-006/video_view_rate.sql`；SHA-256：`a256ddb8b7fb5f61875aa8c79fd4d266b551fc7ffac769b9850414155c9579ed`。

唯一原文位置offset=592，替换前：
```sql
CAST(NULL::DECIMAL(8,4) AS DECIMAL(8,4)) AS video_view_rate
```
替换后：
```sql
CAST(0 AS DECIMAL(8,4)) AS video_view_rate
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|0|0|0|0|
|video_views|1200|1200|1200|1200|

### 重跑 upvotes

SQL：`data/014_work/impl-006/upvotes.sql`；SHA-256：`062eaf6a806c6489ca2490ae1b58aea30265f64c88939f640376e24787e38e9a`。

唯一原文位置offset=661，替换前：
```sql
CAST(NULL::INTEGER AS INTEGER) AS upvotes
```
替换后：
```sql
CAST(COALESCE(comment_upvotes, '0') AS INTEGER) AS upvotes
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|0|0|0|0|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 downvotes

SQL：`data/014_work/impl-006/downvotes.sql`；SHA-256：`984c647280937f744880522d3a693bb49b9db51b2e1f2faefe64ed37f92584fb`。

唯一原文位置offset=712，替换前：
```sql
CAST(NULL::INTEGER AS INTEGER) AS downvotes
```
替换后：
```sql
CAST(COALESCE(comment_downvotes, '0') AS INTEGER) AS downvotes
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|0|0|0|0|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 comments

SQL：`data/014_work/impl-006/comments.sql`；SHA-256：`68d9b30d703dc56e6f666426b56441762b922bd64b39efba2be49e2ce1fd369e`。

唯一原文位置offset=765，替换前：
```sql
CAST(NULL::INTEGER AS INTEGER) AS comments
```
替换后：
```sql
CAST(COALESCE(viewer_comments, '0') AS INTEGER) AS comments
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|0|0|0|0|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 shares

SQL：`data/014_work/impl-006/shares.sql`；SHA-256：`c0f026d5a56585d740e9fec8ae0351fd0b8828e4e64d0900b48405b0e5cc1af0`。

唯一原文位置offset=817，替换前：
```sql
CAST(NULL::INTEGER AS INTEGER) AS shares
```
替换后：
```sql
CAST(0 AS INTEGER) AS shares
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|0|0|0|0|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 saves

SQL：`data/014_work/impl-006/saves.sql`；SHA-256：`eb4520012e83c97273e3b1a514edf2372f727fd4b7701431a6b6eec8ce30929d`。

唯一原文位置offset=867，替换前：
```sql
CAST(NULL::INTEGER AS INTEGER) AS saves
```
替换后：
```sql
CAST(0 AS INTEGER) AS saves
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|0|0|0|0|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 post_visits

SQL：`data/014_work/impl-006/post_visits.sql`；SHA-256：`7807208353d84f81d1bce96ce72a9b81efb57a9c4ee3d4a492e9b1a8732ca673`。

唯一原文位置offset=916，替换前：
```sql
CAST(NULL::INTEGER AS INTEGER) AS post_visits
```
替换后：
```sql
CAST(0 AS INTEGER) AS post_visits
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|0|0|0|0|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 profile_visits

SQL：`data/014_work/impl-006/profile_visits.sql`；SHA-256：`21bb0563932b9c6c3c717dbc5df8955a1b843c80650a43947ace6e32b749aa3f`。

唯一原文位置offset=971，替换前：
```sql
CAST(NULL::INTEGER AS INTEGER) AS profile_visits
```
替换后：
```sql
CAST(0 AS INTEGER) AS profile_visits
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|0|0|0|0|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 community_joins

SQL：`data/014_work/impl-006/community_joins.sql`；SHA-256：`3434c16e3785e07ee1dd03fe2dd01c41aa08c22491fabb3d6505d29ac0b8e37d`。

唯一原文位置offset=1029，替换前：
```sql
CAST(NULL::INTEGER AS INTEGER) AS community_joins
```
替换后：
```sql
CAST(0 AS INTEGER) AS community_joins
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|0|0|0|0|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 conversions

SQL：`data/014_work/impl-006/conversions.sql`；SHA-256：`a762593f2ebd62ea1257d9b4eae6fc778a9193bc313b5e949b1a0f820ac42725`。

唯一原文位置offset=1088，替换前：
```sql
CAST(NULL::INTEGER AS INTEGER) AS conversions
```
替换后：
```sql
CAST(0 AS INTEGER) AS conversions
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|0|0|0|0|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 conversion_value

SQL：`data/014_work/impl-006/conversion_value.sql`；SHA-256：`e463435f6d8457ac84d65b546edf7db2d2f86847888ae2b500b48e590180dc32`。

唯一原文位置offset=1143，替换前：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS conversion_value
```
替换后：
```sql
CAST(0 AS DECIMAL(18,2)) AS conversion_value
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|0|0|0|0|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 cost_per_video_view

SQL：`data/014_work/impl-006/cost_per_video_view.sql`；SHA-256：`6440f8443122343906bb8321fede35d38e74b401dbe5bd9c2802ef54c52bb70e`。

唯一原文位置offset=1394，替换前：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_video_view
```
替换后：
```sql
CASE WHEN CAST(COALESCE(video_started, '0') AS INTEGER)>0 THEN ROUND(spend/CAST(COALESCE(video_started, '0') AS INTEGER),2) ELSE 0 END AS cost_per_video_view
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|0|0|0|0|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 cost_per_conversion

SQL：`data/014_work/impl-006/cost_per_conversion.sql`；SHA-256：`46a57c45c87523fa6351d5563fbd7181c8e996ad3afd1491d35c26a0307f6ed8`。

唯一原文位置offset=1455，替换前：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_conversion
```
替换后：
```sql
0::DOUBLE AS cost_per_conversion
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|0|0|0|0|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 total_engagements

SQL：`data/014_work/impl-006/total_engagements.sql`；SHA-256：`1d8f7979362de251c7e2240b9274a8c5dcc957ee909da217821be89bc3eee0e9`。

唯一原文位置offset=1516，替换前：
```sql
CAST(NULL::INTEGER AS INTEGER) AS total_engagements
```
替换后：
```sql
(CAST(COALESCE(comment_upvotes, '0') AS INTEGER)+CAST(COALESCE(comment_downvotes, '0') AS INTEGER)+CAST(COALESCE(viewer_comments, '0') AS INTEGER)) AS total_engagements
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|0|0|0|0|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 engagement_rate

SQL：`data/014_work/impl-006/engagement_rate.sql`；SHA-256：`2b646546dd64378c03139a90bbc758976e6008db11e44e6a5c9e03609ffde0f7`。

唯一原文位置offset=1577，替换前：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS engagement_rate
```
替换后：
```sql
CASE WHEN impressions>0 THEN ROUND(CAST((CAST(COALESCE(comment_upvotes, '0') AS INTEGER)+CAST(COALESCE(comment_downvotes, '0') AS INTEGER)+CAST(COALESCE(viewer_comments, '0') AS INTEGER)) AS DECIMAL)/CAST(impressions AS DECIMAL)*100,4) ELSE 0 END AS engagement_rate
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|0|0|0|0|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 click_through_rate

SQL：`data/014_work/impl-006/click_through_rate.sql`；SHA-256：`883d0c34d1ebe1d5a81c4787f21ca584a06f61c8ebb7b076c4601eaeac509019`。

唯一原文位置offset=1215，替换前：
```sql
TRY_CAST("ctr" AS DOUBLE)
```
替换后：
```sql
CASE WHEN impressions>0 THEN ROUND(CAST(clicks AS DECIMAL)/CAST(impressions AS DECIMAL)*100,4) ELSE 0 END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|0|0|0|0|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 cost_per_click

SQL：`data/014_work/impl-006/cost_per_click.sql`；SHA-256：`0e836a094e3511a0d208ac20919cad8e41c7e655bebaac84a5b489459d34ec11`。

唯一原文位置offset=1272，替换前：
```sql
TRY_CAST("cpc" AS DOUBLE)
```
替换后：
```sql
CASE WHEN clicks>0 THEN ROUND(spend/clicks,2) ELSE 0 END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|0|0|0|0|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|1200|1200|1200|1200|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 重跑 cost_per_thousand_impressions

SQL：`data/014_work/impl-006/cost_per_thousand_impressions.sql`；SHA-256：`84f8e474d5b6f7e7ece9a3db2bbb1fd87e4af29bd2a739d12433216516fceae5`。

唯一原文位置offset=1325，替换前：
```sql
TRY_CAST("ecpm" AS DOUBLE)
```
替换后：
```sql
CASE WHEN impressions>0 THEN ROUND(spend/impressions*1000,2) ELSE 0 END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|1200|1200|1200|1200|
|clicks|0|0|0|0|
|comments|1200|1200|1200|1200|
|community_joins|1200|1200|1200|1200|
|conversion_value|1200|1200|1200|1200|
|conversions|1200|1200|1200|1200|
|cost_per_click|1200|1200|1200|1200|
|cost_per_conversion|1200|1200|1200|1200|
|cost_per_thousand_impressions|0|0|0|0|
|cost_per_video_view|1200|1200|1200|1200|
|date_day|0|0|0|0|
|downvotes|1200|1200|1200|1200|
|engagement_rate|1200|1200|1200|1200|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|1200|1200|1200|1200|
|profile_visits|1200|1200|1200|1200|
|saves|1200|1200|1200|1200|
|shares|1200|1200|1200|1200|
|spend|1200|1200|1200|1200|
|total_engagements|1200|1200|1200|1200|
|upvotes|1200|1200|1200|1200|
|video_view_rate|1200|1200|1200|1200|
|video_views|1200|1200|1200|1200|

### 复用gold SQL同输入诊断

用于诊断，不是单点修复证据。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|0|0|0|True|
|L1|1200|1200|0|0|0/0|0|0|0|True|
|L2|1200|1200|0|0|0/0|0|0|0|True|
|L3|1200|1200|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|campaign_id|0|0|0|0|
|click_through_rate|0|0|0|0|
|clicks|0|0|0|0|
|comments|0|0|0|0|
|community_joins|0|0|0|0|
|conversion_value|0|0|0|0|
|conversions|0|0|0|0|
|cost_per_click|0|0|0|0|
|cost_per_conversion|0|0|0|0|
|cost_per_thousand_impressions|0|0|0|0|
|cost_per_video_view|0|0|0|0|
|date_day|0|0|0|0|
|downvotes|0|0|0|0|
|engagement_rate|0|0|0|0|
|impressions|0|0|0|0|
|platform|0|0|0|0|
|post_visits|0|0|0|0|
|profile_visits|0|0|0|0|
|saves|0|0|0|0|
|shares|0|0|0|0|
|spend|0|0|0|0|
|total_engagements|0|0|0|0|
|upvotes|0|0|0|0|
|video_view_rate|0|0|0|0|
|video_views|0|0|0|0|

## 5. 类别、把握及与014对比

- 主要原因：**多因并列（I、D、A）**。
- 主因对应单项：spend, video_views, video_view_rate, upvotes, downvotes, comments, shares, saves, post_visits, profile_visits, community_joins, conversions, conversion_value, cost_per_video_view, cost_per_conversion, total_engagements, engagement_rate, click_through_rate, cost_per_click, cost_per_thousand_impressions。
- 参与因素：无：20处均并列主因。
- 标记：已披露。
- 把握：**中**。
- 重跑是否满足U第4条件：否（每次单列修复仅减少1/20列差异，整行不变）。

不将20个不同错误合并成一次U修复。spend有清楚的代码正确意图证据，优先I；D候选列存在的证据来自raw schema和014-V1，不从gold推断。其余指标只有gold实现不能确定业务口径。

与014相比：**是：X改为I/D/A多因并列；v1允许代码意图、候选列降级和并列归因。**

## 规则问题

v1的D候选列规则用于可直接辨认的四个指标；需定义聚合业务口径的派生指标按A。此边界仍可能有D/A两种读法，保留中把握，逐项而非按占位列总数挑主因。

2026-10-29用户确认的第3节补充：仅当本表依赖raw满足agent留存=初始、gold不同，且诊断确认影响可评估性时标“不可评估”；gold=初始、agent不同则照常标注，查轨迹改动。不能把两类混为一谈。若gold与agent一致但二者不同于初始（019/020），当前本节点仍可比较；初始差异另记。

共同执行例外：最初指纹快照因外部v0附件已不在原桌面路径而失败；成功的016快照晚于首批私有重跑。已逐文件与015任务前的大小、mtime、SHA-256比较，覆盖原始库的历史指纹无变化；不把晚快照伪称执行前快照。仓库v0与004–015记录保留。
