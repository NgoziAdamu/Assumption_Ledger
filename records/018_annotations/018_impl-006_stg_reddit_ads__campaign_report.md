# impl-006 / stg_reddit_ads__campaign_report（v2定稿）

## 1. 差异描述与判定

20个指标各造成1200格差异：spend候选被覆盖、四个可映射指标直接填NULL，其余为未规定指标口径。

已核实：1200行/24000格，20个单列干预各减少1200格、行数均不变，故20处按v2分别归类后并列。spend在event19同一映射中先含正确spend候选、后被重复键覆盖掉，归I。video_views/upvotes/downvotes/comments原始表分别有video_started/comment_upvotes/comment_downvotes/viewer_comments，但生成器没有逐字段数据判断就填NULL，按v2归D。video_view_rate、shares、saves、post_visits、profile_visits、community_joins、conversions、conversion_value、cost_per_video_view、cost_per_conversion、total_engagements、engagement_rate及ctr/cpc/ecpm输出共15项，缺直接列、统一汇总/公式或0与NULL约定，归A；这不声称这些值不存在任何可用业务定义。event95明确披露typed NULL，D加“已披露”。 018统一固定加载时间补跑，L0–L3行/格子数和各列差异均与旧结果一致。 A项仅表示差异取决于契约未定的选择，不据gold实现认定agent做错。

主要原因：**多因并列（I、D、A）**；把握：**中**。
参与因素：无：20处均并列主因。标记：已披露。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。按v2第7节补做共同固定时间，比较数值不变。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-006_stg_reddit_ads__campaign_report.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

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

## 3. agent实际看到的信息与不确定性四档

event 17→18输出raw列信息；event 19程序读取所有raw schema后生成表达式；event 95报告明确披露缺源字段采用类型化NULL及非完整业务实现。V1证明spend/video_started/comment_upvotes可用。未找到逐指标的明确业务口径说明或正确意图陈述。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|spend|I|只有通用策略说明|97|
|video_views|D|只有通用策略说明|97|
|video_view_rate|A|只有通用策略说明|97|
|upvotes|D|只有通用策略说明|97|
|downvotes|D|只有通用策略说明|97|
|comments|D|只有通用策略说明|97|
|shares|A|只有通用策略说明|97|
|saves|A|只有通用策略说明|97|
|post_visits|A|只有通用策略说明|97|
|profile_visits|A|只有通用策略说明|97|
|community_joins|A|只有通用策略说明|97|
|conversions|A|只有通用策略说明|97|
|conversion_value|A|只有通用策略说明|97|
|cost_per_video_view|A|只有通用策略说明|97|
|cost_per_conversion|A|只有通用策略说明|97|
|total_engagements|A|只有通用策略说明|97|
|engagement_rate|A|只有通用策略说明|97|
|click_through_rate|A|看到了但没提|18|
|cost_per_click|A|看到了但没提|18|
|cost_per_thousand_impressions|A|看到了但没提|18|

### spend：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### video_views：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### video_view_rate：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### upvotes：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### downvotes：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### comments：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### shares：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### saves：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### post_visits：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### profile_visits：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### community_joins：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### conversions：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### conversion_value：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### cost_per_video_view：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### cost_per_conversion：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### total_engagements：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### engagement_rate：只有通用策略说明

仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。

事件 **97**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`。
```text
对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。
```

### click_through_rate：看到了但没提

CTR/CPC/eCPM源列可见；最终报告TRY_CAST/缺列占位说明不解释优先直接指标列还是重算公式，不能覆盖这三项来源选择。

事件 **18**，字段`content`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/18.json`。
```text
, 'comment_upvotes', 'comments_page_views', 'conversion_roas', 'cpc', 'ctr', 'ecpm', 'gallery_item_caption', 'gallery_item_id', 'impressions', 'legacy_click_conversions_attribution_window_day', 'legacy_click_conversions_attribution_window_month', 'legacy_click_conversions_attribution_window_week', 'legacy_view_conversions_attribution_window_day', 'legacy_view_conversions_attribution_window_month', 'legacy_view_conversions_attribution_window_week', 'priority', 'region', 'spend', 'video_fully_viewable_impressions', 'video_plays_expanded', 'video_plays_with_sound', 'video_started', 'video_viewable_impressions', 'video_watched_100_percent', 'video_watched_10_seconds', 'video_watched_25_percent', 'video_watched_3_seconds', 'video_watched_50_percent', 'video_watched_5_seconds', 'video_watched_75_percent', 'video_watched_95_percent', 'viewable_impressions', 'viewer_comments']
snapchat_campaign_hourly_report_data [
```

### cost_per_click：看到了但没提

CTR/CPC/eCPM源列可见；最终报告TRY_CAST/缺列占位说明不解释优先直接指标列还是重算公式，不能覆盖这三项来源选择。

事件 **18**，字段`content`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/18.json`。
```text
nvotes', 'comment_upvotes', 'comments_page_views', 'conversion_roas', 'cpc', 'ctr', 'ecpm', 'gallery_item_caption', 'gallery_item_id', 'impressions', 'legacy_click_conversions_attribution_window_day', 'legacy_click_conversions_attribution_window_month', 'legacy_click_conversions_attribution_window_week', 'legacy_view_conversions_attribution_window_day', 'legacy_view_conversions_attribution_window_month', 'legacy_view_conversions_attribution_window_week', 'priority', 'region', 'spend', 'video_fully_viewable_impressions', 'video_plays_expanded', 'video_plays_with_sound', 'video_started', 'video_viewable_impressions', 'video_watched_100_percent', 'video_watched_10_seconds', 'video_watched_25_percent', 'video_watched_3_seconds', 'video_watched_50_percent', 'video_watched_5_seconds', 'video_watched_75_percent', 'video_watched_95_percent', 'viewable_impressions', 'viewer_comments']
snapchat_campaign_hourly_report
```

### cost_per_thousand_impressions：看到了但没提

CTR/CPC/eCPM源列可见；最终报告TRY_CAST/缺列占位说明不解释优先直接指标列还是重算公式，不能覆盖这三项来源选择。

事件 **18**，字段`content`；[轨迹原文](../014_trace_impl-006.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/18.json`。
```text
ent_upvotes', 'comments_page_views', 'conversion_roas', 'cpc', 'ctr', 'ecpm', 'gallery_item_caption', 'gallery_item_id', 'impressions', 'legacy_click_conversions_attribution_window_day', 'legacy_click_conversions_attribution_window_month', 'legacy_click_conversions_attribution_window_week', 'legacy_view_conversions_attribution_window_day', 'legacy_view_conversions_attribution_window_month', 'legacy_view_conversions_attribution_window_week', 'priority', 'region', 'spend', 'video_fully_viewable_impressions', 'video_plays_expanded', 'video_plays_with_sound', 'video_started', 'video_viewable_impressions', 'video_watched_100_percent', 'video_watched_10_seconds', 'video_watched_25_percent', 'video_watched_3_seconds', 'video_watched_50_percent', 'video_watched_5_seconds', 'video_watched_75_percent', 'video_watched_95_percent', 'viewable_impressions', 'viewer_comments']
snapchat_campaign_hourly_report_data ['campai
```

已检视99个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：一条查询。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../018_reruns_impl-006.json)保存SQL单处替换、基线/干预及L0–L3每列计数。


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


### v2共同时间补跑

原始CURRENT_TIMESTAMP仅用于未评分的_dbt_loaded_at。按v2仍固定所有21次执行为2025-10-25 12:00:00+08；这是任意共同控制，不推断原执行日期。其余单项补丁直接复用014/016，不增加数据核实查询。

原件以READ_ONLY附加，复制raw到data/018_work后执行。比较器沿用016/017；键固定L0并纳入比较列，独有行计格子时包含键。

### 重跑 baseline

SQL：`data/018_work/impl-006/baseline.sql`；SHA-256：`d33867685722d0953ef0c3901db450bdefc32000403c0fdf8c3ca4a0b9202665`。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|24000|False|
|L1|1200|1200|0|0|0/0|1200|1200|24000|False|
|L2|1200|1200|0|0|0/0|1200|1200|24000|False|
|L3|1200|1200|0|0|0/0|1200|1200|24000|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/spend.sql`；SHA-256：`978ed74cef04b3794469ee21efe79fe90354c4183976064942b8905b6c99c52c`。

单处替换offset=476；原文：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend
```
新文：
```sql
CAST(spend AS DECIMAL(18,2)) AS spend
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/video_views.sql`；SHA-256：`87dcf678c238a84ee43111844bd7366572bd82f000d44a90a132f919a33d7f2d`。

单处替换offset=537；原文：
```sql
CAST(NULL::INTEGER AS INTEGER) AS video_views
```
新文：
```sql
CAST(COALESCE(video_started, '0') AS INTEGER) AS video_views
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/video_view_rate.sql`；SHA-256：`c6bbf36b7b00c3f55c622f021aab69689f9ae2dbd48f0751480b785377dd737b`。

单处替换offset=592；原文：
```sql
CAST(NULL::DECIMAL(8,4) AS DECIMAL(8,4)) AS video_view_rate
```
新文：
```sql
CAST(0 AS DECIMAL(8,4)) AS video_view_rate
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/upvotes.sql`；SHA-256：`635d6e3945bdd22a8918c96be0c81b6836295087995217e7ab9114d56638ace7`。

单处替换offset=661；原文：
```sql
CAST(NULL::INTEGER AS INTEGER) AS upvotes
```
新文：
```sql
CAST(COALESCE(comment_upvotes, '0') AS INTEGER) AS upvotes
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/downvotes.sql`；SHA-256：`8f1ef8a0489b3db9eb87ebe9bb4e200a764f1d2826b345b9285b4542e90fe6e3`。

单处替换offset=712；原文：
```sql
CAST(NULL::INTEGER AS INTEGER) AS downvotes
```
新文：
```sql
CAST(COALESCE(comment_downvotes, '0') AS INTEGER) AS downvotes
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/comments.sql`；SHA-256：`83ddbe4be8056067d74b4d3ba24e7e1ca63168a09028262dbf30f1231ab0a6f3`。

单处替换offset=765；原文：
```sql
CAST(NULL::INTEGER AS INTEGER) AS comments
```
新文：
```sql
CAST(COALESCE(viewer_comments, '0') AS INTEGER) AS comments
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/shares.sql`；SHA-256：`d209f07c5e427ee4298f07b87a49efdab1dee113ca47585371267a579aaf7af4`。

单处替换offset=817；原文：
```sql
CAST(NULL::INTEGER AS INTEGER) AS shares
```
新文：
```sql
CAST(0 AS INTEGER) AS shares
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/saves.sql`；SHA-256：`481818c59900ccd134b3bb85eeab81fcdc802a542ae3dc22b5b5a946a1df33cc`。

单处替换offset=867；原文：
```sql
CAST(NULL::INTEGER AS INTEGER) AS saves
```
新文：
```sql
CAST(0 AS INTEGER) AS saves
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/post_visits.sql`；SHA-256：`5911bad851e6bc0cc47a3d7c3629d0bd708292e00e02b37b09b58f0119679989`。

单处替换offset=916；原文：
```sql
CAST(NULL::INTEGER AS INTEGER) AS post_visits
```
新文：
```sql
CAST(0 AS INTEGER) AS post_visits
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/profile_visits.sql`；SHA-256：`b945d21dd1f378ec2238ff138f7a6a8387a8766eb6c148fb992543274ec0edbb`。

单处替换offset=971；原文：
```sql
CAST(NULL::INTEGER AS INTEGER) AS profile_visits
```
新文：
```sql
CAST(0 AS INTEGER) AS profile_visits
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/community_joins.sql`；SHA-256：`5e96dbb47f62b4636b82cb5b97d93bc274f39c6122eddd7df1fcc55509fffcc2`。

单处替换offset=1029；原文：
```sql
CAST(NULL::INTEGER AS INTEGER) AS community_joins
```
新文：
```sql
CAST(0 AS INTEGER) AS community_joins
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/conversions.sql`；SHA-256：`91a1398e704d536d519dbaa8bfe0cafec6bff7188b53b8333a820b58bca157ca`。

单处替换offset=1088；原文：
```sql
CAST(NULL::INTEGER AS INTEGER) AS conversions
```
新文：
```sql
CAST(0 AS INTEGER) AS conversions
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/conversion_value.sql`；SHA-256：`747ff30098b4eeaa101375616589b937ddba236f5fafaad0020b8bf50b3f112c`。

单处替换offset=1143；原文：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS conversion_value
```
新文：
```sql
CAST(0 AS DECIMAL(18,2)) AS conversion_value
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/cost_per_video_view.sql`；SHA-256：`779eb7a5a2433715341fd8ea8aac8cbdd4f171ec790142edc0fb227b3bad1c6e`。

单处替换offset=1394；原文：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_video_view
```
新文：
```sql
CASE WHEN CAST(COALESCE(video_started, '0') AS INTEGER)>0 THEN ROUND(spend/CAST(COALESCE(video_started, '0') AS INTEGER),2) ELSE 0 END AS cost_per_video_view
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/cost_per_conversion.sql`；SHA-256：`85e0923e8264f9c2222dc61a9bacf2a6b1801fefd341e788eb240b33708cd546`。

单处替换offset=1455；原文：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_conversion
```
新文：
```sql
0::DOUBLE AS cost_per_conversion
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/total_engagements.sql`；SHA-256：`a8a7db9e3a1ee1a9e89e4406b1b5f7adedbb82d31f4f1aa944a7c2de5782912e`。

单处替换offset=1516；原文：
```sql
CAST(NULL::INTEGER AS INTEGER) AS total_engagements
```
新文：
```sql
(CAST(COALESCE(comment_upvotes, '0') AS INTEGER)+CAST(COALESCE(comment_downvotes, '0') AS INTEGER)+CAST(COALESCE(viewer_comments, '0') AS INTEGER)) AS total_engagements
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/engagement_rate.sql`；SHA-256：`3c9105cbe81143582f6c57806d45acfef8649432a6ad8ea7bb5c13ed8d063bf1`。

单处替换offset=1577；原文：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS engagement_rate
```
新文：
```sql
CASE WHEN impressions>0 THEN ROUND(CAST((CAST(COALESCE(comment_upvotes, '0') AS INTEGER)+CAST(COALESCE(comment_downvotes, '0') AS INTEGER)+CAST(COALESCE(viewer_comments, '0') AS INTEGER)) AS DECIMAL)/CAST(impressions AS DECIMAL)*100,4) ELSE 0 END AS engagement_rate
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/click_through_rate.sql`；SHA-256：`ea78ef176211b29bfb57903d5f3650db16fb290f27a4bdce0c96e2c0dea728e6`。

单处替换offset=1215；原文：
```sql
TRY_CAST("ctr" AS DOUBLE)
```
新文：
```sql
CASE WHEN impressions>0 THEN ROUND(CAST(clicks AS DECIMAL)/CAST(impressions AS DECIMAL)*100,4) ELSE 0 END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/cost_per_click.sql`；SHA-256：`b3017233469b7a24a027f870b3aafda6a1f5665816d658ce594ac26f4bef8fc5`。

单处替换offset=1272；原文：
```sql
TRY_CAST("cpc" AS DOUBLE)
```
新文：
```sql
CASE WHEN clicks>0 THEN ROUND(spend/clicks,2) ELSE 0 END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

SQL：`data/018_work/impl-006/cost_per_thousand_impressions.sql`；SHA-256：`35b7417834c09b317fe1078f81a1b71ca0373f7ffd2aec05e40bda4e3b9d473a`。

单处替换offset=1325；原文：
```sql
TRY_CAST("ecpm" AS DOUBLE)
```
新文：
```sql
CASE WHEN impressions>0 THEN ROUND(spend/impressions*1000,2) ELSE 0 END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1200|1200|0|0|0/0|1200|1200|22800|False|
|L1|1200|1200|0|0|0/0|1200|1200|22800|False|
|L2|1200|1200|0|0|0/0|1200|1200|22800|False|
|L3|1200|1200|0|0|0/0|1200|1200|22800|False|

整表首次匹配：L0–L3均不匹配。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|campaign_id|0|0|0|0|
|account_id|0|0|0|0|
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

## 5. 逐项类别及U门槛

表级主要原因：**多因并列（I、D、A）**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|spend|I|1200→1200|24000→22800|无|
|video_views|D|1200→1200|24000→22800|无|
|video_view_rate|A|1200→1200|24000→22800|无|
|upvotes|D|1200→1200|24000→22800|无|
|downvotes|D|1200→1200|24000→22800|无|
|comments|D|1200→1200|24000→22800|无|
|shares|A|1200→1200|24000→22800|无|
|saves|A|1200→1200|24000→22800|无|
|post_visits|A|1200→1200|24000→22800|无|
|profile_visits|A|1200→1200|24000→22800|无|
|community_joins|A|1200→1200|24000→22800|无|
|conversions|A|1200→1200|24000→22800|无|
|conversion_value|A|1200→1200|24000→22800|无|
|cost_per_video_view|A|1200→1200|24000→22800|无|
|cost_per_conversion|A|1200→1200|24000→22800|无|
|total_engagements|A|1200→1200|24000→22800|无|
|engagement_rate|A|1200→1200|24000→22800|无|
|click_through_rate|A|1200→1200|24000→22800|无|
|cost_per_click|A|1200→1200|24000→22800|无|
|cost_per_thousand_impressions|A|1200→1200|24000→22800|无|

重跑是否满足U第4条件：**否（每次单列修复仅减少1/20列差异，整行不变）**。

不将20个不同差异点合并成一次U修复。spend有清楚的代码正确意图证据，优先I；D候选列存在的证据来自raw schema和014-V1，不从gold推断。其余指标只有gold实现不能确定业务口径。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。按v2第7节补做共同固定时间，比较数值不变。

与014相比的历史对比沿用原字段：是：X改为I/D/A多因并列；v1允许代码意图、候选列降级和并列归因。。此字段不代替本次与016/017的对比。

## 规则问题

20个单项仍分别归I/D/A，不按同一种NULL外观合并；D候选列与需业务定义的A派生字段边界保持中把握。v2要求共同时间，本轮固定加载时间后全部比较数值不变。缺列填NULL的通用披露只覆盖17个占位项，不延伸为CTR/CPC/eCPM直接字段与重算公式的说明。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
