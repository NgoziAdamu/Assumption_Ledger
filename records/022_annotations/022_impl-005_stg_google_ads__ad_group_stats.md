# impl-005 / stg_google_ads__ad_group_stats（校准；v2）

## 1. 差异与结论

campaign来源选择未被契约和可见关联数据唯一确定，主要原因A；单换源列L2完全一致。盲标把三项数值类型合改当作O参与因素；盲锁后按手册逐项拆开，三项单修行规模均不减，因此最终不列参与因素。保留盲锁原结论，不倒改。

主要原因：**A**；参与因素：无；把握：高；标记：校准。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

校准过程：盲标固定文件 `records/022_calibration_blind_decisions.json`，哈希锁 `records/022_blind_lock.json`；之后才读018。对照见 `records/022_calibration_comparison.json`。

## 2. 来源、契约及SQL位置

- 精简材料包：[records/013_packages/013_impl-005_staging_stg_google_ads__ad_group_stats.md](../../records/013_packages/013_impl-005_staging_stg_google_ads__ad_group_stats.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`records/012_packages/012_impl-005_staging_stg_google_ads__ad_group_stats.json`。
- 比较结果：[022_reruns_impl-005_stg_google_ads__ad_group_stats.json](../022_reruns_impl-005_stg_google_ads__ad_group_stats.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-005/docs/data_contract.yaml`。

原件第442–479行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql`；原件第1–11行。

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

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql`；原件第1–149行。

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

## 3. agent看到的材料与不确定性

- event 13：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/13.json`。
- event 14：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/14.json`。
- event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/15.json`。
- event 47：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/47.json`。

四档：**看到了但没提**。

未找到针对本表主项选择的说明。“看到了但没提”只表示上述实际输出包含相关schema、样例、代码/运行结果；不把写SQL本身或通用功能清单当作具体说明。“没有迹象”不推断agent内部没有意识到。

## 4. 核实查询与诊断

核实查询共**1条**（含失败尝试），代价档：**一条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：候选列关系核实

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/google_ads.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE campaign_id=campaign_base_campaign) equal_candidates,
 count(*) FILTER(WHERE campaign_id IN(SELECT id FROM raw.campaign_history_data)) direct_in_history,
 count(*) FILTER(WHERE campaign_base_campaign IN(SELECT id FROM raw.campaign_history_data)) base_in_history FROM raw.ad_group_stats_data
```

```json
{"columns": ["n", "equal_candidates", "direct_in_history", "base_in_history"], "rows": [[10000, 15, 10000, 10000]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/google_ads.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["account_id", "ad_group_id", "campaign_id"]`；比较列：`["account_id", "ad_group_id", "ad_network_type", "campaign_id", "clicks", "conversions", "conversions_value", "date_day", "device", "impressions", "spend", "view_through_conversions"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 10000/10000 | 9985/9985 | 0/0 | 15 | 19985 | 239672 | False |
| L1 | 10000/10000 | 9985/9985 | 0/0 | 15 | 19985 | 239655 | False |
| L2 | 10000/10000 | 9985/9985 | 0/0 | 0 | 19970 | 239640 | False |
| L3 | 10000/10000 | 9985/9985 | 0/0 | 0 | 19970 | 239640 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| account_id | 0 | 0 | 0 | 0 |
| ad_group_id | 0 | 0 | 0 | 0 |
| campaign_id | 0 | 0 | 0 | 0 |
| ad_network_type | 0 | 0 | 0 | 0 |
| clicks | 0 | 0 | 0 | 0 |
| conversions | 15 | 0 | 0 | 0 |
| conversions_value | 2 | 0 | 0 | 0 |
| date_day | 0 | 0 | 0 | 0 |
| device | 0 | 0 | 0 | 0 |
| impressions | 0 | 0 | 0 | 0 |
| spend | 15 | 15 | 0 | 0 |
| view_through_conversions | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-005_stg_google_ads__ad_group_stats/baseline.sql`；SHA-256：`35b7d35bac34f4628dd8b6db13330fb6947104ba63011b39e922026d5279166d`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 10000/10000 | 9985/9985 | 0/0 | 15 | 19985 | 239672 | False |
| L1 | 10000/10000 | 9985/9985 | 0/0 | 15 | 19985 | 239655 | False |
| L2 | 10000/10000 | 9985/9985 | 0/0 | 0 | 19970 | 239640 | False |
| L3 | 10000/10000 | 9985/9985 | 0/0 | 0 | 19970 | 239640 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| account_id | 0 | 0 | 0 | 0 |
| ad_group_id | 0 | 0 | 0 | 0 |
| campaign_id | 0 | 0 | 0 | 0 |
| ad_network_type | 0 | 0 | 0 | 0 |
| clicks | 0 | 0 | 0 | 0 |
| conversions | 15 | 0 | 0 | 0 |
| conversions_value | 2 | 0 | 0 | 0 |
| date_day | 0 | 0 | 0 | 0 |
| device | 0 | 0 | 0 | 0 |
| impressions | 0 | 0 | 0 | 0 |
| spend | 15 | 15 | 0 | 0 |
| view_through_conversions | 0 | 0 | 0 | 0 |

### campaign_column

SQL：`data/022_work/impl-005_stg_google_ads__ad_group_stats/campaign_column.sql`；SHA-256：`95e663841e2fe79c74077a8258d74c78354d9e5c79ba21d651b610cfc8e46eef`。

替换offset=275，原表达式所在行约6（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(campaign_base_campaign AS VARCHAR(20))
-- 新
CAST(base.campaign_id AS VARCHAR(20))
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 10000/10000 | 0/0 | 0/0 | 10000 | 10000 | 21395 | False |
| L1 | 10000/10000 | 0/0 | 0/0 | 9999 | 9999 | 9999 | False |
| L2 | 10000/10000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 10000/10000 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L2。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| account_id | 0 | 0 | 0 | 0 |
| ad_group_id | 0 | 0 | 0 | 0 |
| campaign_id | 0 | 0 | 0 | 0 |
| ad_network_type | 0 | 0 | 0 | 0 |
| clicks | 0 | 0 | 0 | 0 |
| conversions | 10000 | 0 | 0 | 0 |
| conversions_value | 1395 | 0 | 0 | 0 |
| date_day | 0 | 0 | 0 | 0 |
| device | 0 | 0 | 0 | 0 |
| impressions | 0 | 0 | 0 | 0 |
| spend | 10000 | 9999 | 0 | 0 |
| view_through_conversions | 0 | 0 | 0 | 0 |

### spend

SQL：`data/022_calibration_supplement/impl-005_stg_google_ads__ad_group_stats/spend.sql`；SHA-256：`8792f740df66147bbe1b02d3b6e827003c9be82b5b83849e4b0815764b569038`。

替换offset=458，原表达式所在行约6（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(cost_micros / 1000000.0 AS DECIMAL(15,2))
-- 新
cost_micros / 1000000.0
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 10000/10000 | 9985/9985 | 0/0 | 15 | 19985 | 239657 | False |
| L1 | 10000/10000 | 9985/9985 | 0/0 | 0 | 19970 | 239640 | False |
| L2 | 10000/10000 | 9985/9985 | 0/0 | 0 | 19970 | 239640 | False |
| L3 | 10000/10000 | 9985/9985 | 0/0 | 0 | 19970 | 239640 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| account_id | 0 | 0 | 0 | 0 |
| ad_group_id | 0 | 0 | 0 | 0 |
| campaign_id | 0 | 0 | 0 | 0 |
| ad_network_type | 0 | 0 | 0 | 0 |
| clicks | 0 | 0 | 0 | 0 |
| conversions | 15 | 0 | 0 | 0 |
| conversions_value | 2 | 0 | 0 | 0 |
| date_day | 0 | 0 | 0 | 0 |
| device | 0 | 0 | 0 | 0 |
| impressions | 0 | 0 | 0 | 0 |
| spend | 0 | 0 | 0 | 0 |
| view_through_conversions | 0 | 0 | 0 | 0 |

### conversions

SQL：`data/022_calibration_supplement/impl-005_stg_google_ads__ad_group_stats/conversions.sql`；SHA-256：`f8719adb5f5ff475d2d96f09b5404e22db5f6cb8cf574ae9c482a330d65cdea0`。

替换offset=525，原表达式所在行约6（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(conversions AS DECIMAL(10,2))
-- 新
CAST(conversions AS DOUBLE)
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 10000/10000 | 9985/9985 | 0/0 | 15 | 19985 | 239657 | False |
| L1 | 10000/10000 | 9985/9985 | 0/0 | 15 | 19985 | 239655 | False |
| L2 | 10000/10000 | 9985/9985 | 0/0 | 0 | 19970 | 239640 | False |
| L3 | 10000/10000 | 9985/9985 | 0/0 | 0 | 19970 | 239640 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| account_id | 0 | 0 | 0 | 0 |
| ad_group_id | 0 | 0 | 0 | 0 |
| campaign_id | 0 | 0 | 0 | 0 |
| ad_network_type | 0 | 0 | 0 | 0 |
| clicks | 0 | 0 | 0 | 0 |
| conversions | 0 | 0 | 0 | 0 |
| conversions_value | 2 | 0 | 0 | 0 |
| date_day | 0 | 0 | 0 | 0 |
| device | 0 | 0 | 0 | 0 |
| impressions | 0 | 0 | 0 | 0 |
| spend | 15 | 15 | 0 | 0 |
| view_through_conversions | 0 | 0 | 0 | 0 |

### conversion_value

SQL：`data/022_calibration_supplement/impl-005_stg_google_ads__ad_group_stats/conversion_value.sql`；SHA-256：`9dfb8a6515b5a5ed671a93117fc6e0d5c08fe779227ccb826b8eafb06e60d6f8`。

替换offset=573，原表达式所在行约6（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(conversions_value AS DECIMAL(15,2))
-- 新
CAST(conversions_value AS DOUBLE)
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 10000/10000 | 9985/9985 | 0/0 | 15 | 19985 | 239670 | False |
| L1 | 10000/10000 | 9985/9985 | 0/0 | 15 | 19985 | 239655 | False |
| L2 | 10000/10000 | 9985/9985 | 0/0 | 0 | 19970 | 239640 | False |
| L3 | 10000/10000 | 9985/9985 | 0/0 | 0 | 19970 | 239640 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| account_id | 0 | 0 | 0 | 0 |
| ad_group_id | 0 | 0 | 0 | 0 |
| campaign_id | 0 | 0 | 0 | 0 |
| ad_network_type | 0 | 0 | 0 | 0 |
| clicks | 0 | 0 | 0 | 0 |
| conversions | 15 | 0 | 0 | 0 |
| conversions_value | 0 | 0 | 0 | 0 |
| date_day | 0 | 0 | 0 | 0 |
| device | 0 | 0 | 0 | 0 |
| impressions | 0 | 0 | 0 | 0 |
| spend | 15 | 15 | 0 | 0 |
| view_through_conversions | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：campaign_column；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- 盲标中numeric_types同时改三列的结果保留在原盲锁JSON，仅作组合诊断；逐列单改spend/conversions/conversion_value的行规模均19985，不列O参与因素。

## 规则问题

三列类型可读为一种统一类型策略或三个独立错误点；按更严格逐列单改执行。合改减15行不能冒充任一单项贡献，最终剔除盲标的O参与因素。
