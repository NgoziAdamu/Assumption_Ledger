# impl-006 | marts | ad_reporting__monthly_campaign_country_report | 差异：S1；日期 原记录

## 契约完整原文

S3:3798–3909

```yaml
    - name: ad_reporting__monthly_campaign_country_report
      description: Monthly campaign performance by country with aggregated metrics; passthrough from intermediate with placeholder platforms removed
      grain: One row per platform, account_id, campaign_id, country_code, report_month
      source_models:
      - intermediate.int_ad_reporting__monthly_campaign_country_report
      business_logic: '- Read from intermediate.int_ad_reporting__monthly_campaign_country_report. - Column mappings (passthrough unless renamed): * month_year → report_month * total_impressions → impressions * total_clicks → clicks * total_interactions → interactions * total_cost → spend * total_conversions → conversions * total_conversions_value → conversions_value * total_view_through_conversions → view_through_conversions * total_attributed_sales_14_d → attributed_sales_14_day * total_attributed_sales_30_d → attributed_sales_30_day * total_attributed_conversions_14_d → attributed_conversions_14_day * total_attributed_conversions_30_d → attributed_conversions_30_day * total_active_view_impressions → active_view_impressions * total_active_view_measurable_impressions → active_view_measurable_impressions * monthly_click_through_rate → avg_ctr_percent * monthly_cost_per_click → avg_cpc * monthly_cost_per_thousand_impressions → avg_cpm * monthly_cost_per_conversion → avg_cpa * monthly_return_on_ad_spend → avg_roas * monthly_amazon_roas_30d → monthly_amazon_roas_30d * _dbt_loaded_at → data_last_updated - Compute mart_created_at using CURRENT_TIMESTAMP at execution time; identical across all rows within a single run. - Exclude rows where platform = ''placeholder''. - No additional aggregation, de-duplication, or transformations; all values and NULLs are passed through from the source. - Output ordering: platform ASC, account_id ASC, campaign_id ASC, report_month DESC, spend DESC.'
      columns:
      - name: platform
        data_type: VARCHAR
        description: Advertising platform identifier.
      - name: country_code
        data_type: VARCHAR
        description: Country code for the campaign’s reported performance.
      - name: report_month
        data_type: DATE
        description: Reporting month derived from month_year.
      - name: year
        data_type: BIGINT
        description: Calendar year of the reporting month.
      - name: month
        data_type: BIGINT
        description: Calendar month number of the reporting month.
      - name: account_id
        data_type: INTEGER
        description: Platform account identifier.
      - name: campaign_id
        data_type: VARCHAR
        description: Campaign identifier within the platform account.
      - name: campaign_name
        data_type: INTEGER
        description: Campaign name identifier as provided by source.
      - name: impressions
        data_type: HUGEINT
        description: Monthly aggregated total impressions.
      - name: clicks
        data_type: HUGEINT
        description: Monthly aggregated total clicks.
      - name: interactions
        data_type: HUGEINT
        description: Monthly aggregated total interactions.
      - name: spend
        data_type: DECIMAL(38,2)
        description: Monthly aggregated total cost.
      - name: conversions
        data_type: HUGEINT
        description: Monthly aggregated total conversions.
      - name: conversions_value
        data_type: DECIMAL(38,2)
        description: Monthly aggregated total conversion value.
      - name: view_through_conversions
        data_type: HUGEINT
        description: Monthly aggregated view-through conversions.
      - name: attributed_sales_14_day
        data_type: DECIMAL(38,2)
        description: Monthly Amazon Ads 14-day attributed sales.
      - name: attributed_sales_30_day
        data_type: DECIMAL(38,2)
        description: Monthly Amazon Ads 30-day attributed sales.
      - name: attributed_conversions_14_day
        data_type: HUGEINT
        description: Monthly Amazon Ads 14-day attributed conversions.
      - name: attributed_conversions_30_day
        data_type: HUGEINT
        description: Monthly Amazon Ads 30-day attributed conversions.
      - name: active_view_impressions
        data_type: HUGEINT
        description: Monthly Google Ads Active View impressions.
      - name: active_view_measurable_impressions
        data_type: HUGEINT
        description: Monthly Google Ads Active View measurable impressions.
      - name: avg_ctr_percent
        data_type: DOUBLE
        description: Monthly click-through rate as provided by source.
      - name: avg_cpc
        data_type: DOUBLE
        description: Monthly average cost per click as provided by source.
      - name: avg_cpm
        data_type: DOUBLE
        description: Monthly cost per thousand impressions as provided by source.
      - name: avg_cpa
        data_type: DOUBLE
        description: Monthly cost per conversion as provided by source.
      - name: avg_roas
        data_type: DOUBLE
        description: Monthly return on ad spend as provided by source.
      - name: monthly_amazon_roas_30d
        data_type: DOUBLE
        description: Monthly Amazon Ads 30-day ROAS as provided by source.
      - name: days_active_in_month
        data_type: BIGINT
        description: Count of days with activity in the reporting month.
      - name: avg_daily_spend
        data_type: DOUBLE
        description: Average daily spend in the reporting month as provided by source.
      - name: avg_daily_impressions
        data_type: DOUBLE
        description: Average daily impressions in the reporting month as provided by source.
      - name: avg_daily_clicks
        data_type: DOUBLE
        description: Average daily clicks in the reporting month as provided by source.
      - name: first_active_date
        data_type: DATE
        description: Earliest activity date within the reporting month.
      - name: last_active_date
        data_type: DATE
        description: Latest activity date within the reporting month.
      - name: data_last_updated
        data_type: TIMESTAMP WITH TIME ZONE
        description: Load timestamp passed through from _dbt_loaded_at.
      - name: mart_created_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Model execution timestamp set at run time.
```

## agent 最终 SQL

S4

```sql
SELECT
    CAST("platform" AS VARCHAR) AS "platform",
    CAST("country_code" AS VARCHAR) AS "country_code",
    CAST("month_year" AS DATE) AS "report_month",
    CAST("year" AS BIGINT) AS "year",
    CAST("month" AS BIGINT) AS "month",
    CAST("account_id" AS INTEGER) AS "account_id",
    CAST("campaign_id" AS VARCHAR) AS "campaign_id",
    CAST("campaign_name" AS INTEGER) AS "campaign_name",
    CAST("total_impressions" AS HUGEINT) AS "impressions",
    CAST("total_clicks" AS HUGEINT) AS "clicks",
    CAST("total_interactions" AS HUGEINT) AS "interactions",
    NULL::DECIMAL(38,2) AS "spend",
    CAST("total_conversions" AS HUGEINT) AS "conversions",
    CAST("total_conversions_value" AS DECIMAL(38,2)) AS "conversions_value",
    CAST("total_view_through_conversions" AS HUGEINT) AS "view_through_conversions",
    NULL::DECIMAL(38,2) AS "attributed_sales_14_day",
    NULL::DECIMAL(38,2) AS "attributed_sales_30_day",
    NULL::HUGEINT AS "attributed_conversions_14_day",
    NULL::HUGEINT AS "attributed_conversions_30_day",
    CAST("total_active_view_impressions" AS HUGEINT) AS "active_view_impressions",
    CAST("total_active_view_measurable_impressions" AS HUGEINT) AS "active_view_measurable_impressions",
    CAST("monthly_click_through_rate" AS DOUBLE) AS "avg_ctr_percent",
    CAST("monthly_cost_per_click" AS DOUBLE) AS "avg_cpc",
    CAST("monthly_cost_per_thousand_impressions" AS DOUBLE) AS "avg_cpm",
    CAST("monthly_cost_per_conversion" AS DOUBLE) AS "avg_cpa",
    CAST("monthly_return_on_ad_spend" AS DOUBLE) AS "avg_roas",
    CAST("monthly_amazon_roas_30d" AS DOUBLE) AS "monthly_amazon_roas_30d",
    CAST("days_active_in_month" AS BIGINT) AS "days_active_in_month",
    CAST("avg_daily_spend" AS DOUBLE) AS "avg_daily_spend",
    CAST("avg_daily_impressions" AS DOUBLE) AS "avg_daily_impressions",
    CAST("avg_daily_clicks" AS DOUBLE) AS "avg_daily_clicks",
    CAST("first_active_date" AS DATE) AS "first_active_date",
    CAST("last_active_date" AS DATE) AS "last_active_date",
    CAST("_dbt_loaded_at" AS TIMESTAMP WITH TIME ZONE) AS "data_last_updated",
    NULL::TIMESTAMP WITH TIME ZONE AS "mart_created_at"
FROM intermediate.int_ad_reporting__monthly_campaign_country_report
```

## gold SQL（仅供定位差异）

S5

```sql
-- Ad Reporting Monthly Campaign Country Report
-- Business-friendly view of monthly campaign performance by country for geographic analysis
-- This table provides aggregated monthly metrics by campaign and country for strategic planning

SELECT 
    -- Primary Keys & Identifiers
    platform,
    country_code,
    month_year AS report_month,
    year,
    month,
    account_id,
    campaign_id,
    campaign_name,
    
    -- Core Performance Metrics (Monthly Aggregated)
    total_impressions AS impressions,
    total_clicks AS clicks,
    total_interactions AS interactions,
    
    -- Financial Metrics (Monthly Aggregated)
    total_cost AS spend,
    
    -- Conversion Metrics (Monthly Aggregated)
    total_conversions AS conversions,
    total_conversions_value AS conversions_value,
    total_view_through_conversions AS view_through_conversions,
    
    -- Platform-Specific Monthly Metrics
    -- Amazon Ads attribution
    total_attributed_sales_14_d AS attributed_sales_14_day,
    total_attributed_sales_30_d AS attributed_sales_30_day,
    total_attributed_conversions_14_d AS attributed_conversions_14_day,
    total_attributed_conversions_30_d AS attributed_conversions_30_day,
    
    -- Google Ads viewability
    total_active_view_impressions AS active_view_impressions,
    total_active_view_measurable_impressions AS active_view_measurable_impressions,
    
    -- Business KPIs (calculated from monthly aggregates)
    monthly_click_through_rate AS avg_ctr_percent,
    monthly_cost_per_click AS avg_cpc,
    monthly_cost_per_thousand_impressions AS avg_cpm,
    monthly_cost_per_conversion AS avg_cpa,
    monthly_return_on_ad_spend AS avg_roas,
    monthly_amazon_roas_30d,
    
    -- Monthly insights
    days_active_in_month,
    avg_daily_spend,
    avg_daily_impressions,
    avg_daily_clicks,
    
    -- Data quality
    first_active_date,
    last_active_date,
    
    -- Data Governance
    _dbt_loaded_at AS data_last_updated,
    CURRENT_TIMESTAMP AS mart_created_at

FROM intermediate.int_ad_reporting__monthly_campaign_country_report

-- Filter out placeholder records
WHERE platform != 'placeholder'

-- Order by platform, account, campaign, month, and spend for optimal query performance
ORDER BY platform, account_id, campaign_id, report_month DESC, spend DESC
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 4236 | 4236 | 0 | 0 | 100 | 100 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"country_code":"us","account_id":"null","campaign_id":"ama01002952115"}</code> |
| K2 | <code>{"country_code":"us","account_id":"null","campaign_id":"ama01048142653"}</code> |
| K3 | <code>{"country_code":"us","account_id":"null","campaign_id":"ama01181409498"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| report_month | 0 | 0 | 0 | DATE | DATE |
| year | 0 | 0 | 0 | BIGINT | BIGINT |
| month | 0 | 0 | 0 | BIGINT | BIGINT |
| account_id | 0 | 0 | 0 | INTEGER | INTEGER |
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_name | 0 | 0 | 0 | INTEGER | INTEGER |
| impressions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| clicks | 0 | 0 | 0 | HUGEINT | HUGEINT |
| interactions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| spend | 4236 | 4236 | 4236 | DECIMAL(38,2) | DECIMAL(38,2) |
| conversions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| conversions_value | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| view_through_conversions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| attributed_sales_14_day | 4236 | 4236 | 4236 | DECIMAL(38,2) | DECIMAL(38,2) |
| attributed_sales_30_day | 4236 | 4236 | 4236 | DECIMAL(38,2) | DECIMAL(38,2) |
| attributed_conversions_14_day | 4236 | 4236 | 4236 | HUGEINT | HUGEINT |
| attributed_conversions_30_day | 4236 | 4236 | 4236 | HUGEINT | HUGEINT |
| active_view_impressions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| active_view_measurable_impressions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| avg_ctr_percent | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_cpc | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_cpm | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_cpa | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_roas | 0 | 0 | 0 | DOUBLE | DOUBLE |
| monthly_amazon_roas_30d | 0 | 0 | 0 | DOUBLE | DOUBLE |
| days_active_in_month | 0 | 0 | 0 | BIGINT | BIGINT |
| avg_daily_spend | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_daily_impressions | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_daily_clicks | 0 | 0 | 0 | DOUBLE | DOUBLE |
| first_active_date | 0 | 0 | 0 | DATE | DATE |
| last_active_date | 0 | 0 | 0 | DATE | DATE |
| data_last_updated | 0 | 0 | 0 | TIMESTAMP WITH TIME ZONE | TIMESTAMP WITH TIME ZONE |

spend 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":46}]</code> | <code>[{"value":"1040.81","rows":1},{"value":"1053.50","rows":1},{"value":"106.42","rows":1},{"value":"1060.95","rows":1},{"value":"1134.90","rows":1}]</code> |
| K2 | <code>[{"value":null,"rows":44}]</code> | <code>[{"value":"1285.87","rows":1},{"value":"133.18","rows":1},{"value":"137.08","rows":1},{"value":"144.63","rows":1},{"value":"1796.96","rows":1}]</code> |
| K3 | <code>[{"value":null,"rows":44}]</code> | <code>[{"value":"103.18","rows":1},{"value":"104.04","rows":1},{"value":"109.39","rows":1},{"value":"110.94","rows":1},{"value":"1187.69","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

attributed_sales_14_day 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":46}]</code> | <code>[{"value":"0.00","rows":6},{"value":"112.42","rows":1},{"value":"112.46","rows":1},{"value":"130.60","rows":1},{"value":"138.12","rows":1}]</code> |
| K2 | <code>[{"value":null,"rows":44}]</code> | <code>[{"value":"0.00","rows":8},{"value":"107.20","rows":1},{"value":"124.29","rows":1},{"value":"124.85","rows":1},{"value":"13.54","rows":1}]</code> |
| K3 | <code>[{"value":null,"rows":44}]</code> | <code>[{"value":"0.00","rows":6},{"value":"106.88","rows":1},{"value":"115.08","rows":1},{"value":"13.26","rows":1},{"value":"13.76","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

attributed_sales_30_day 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":46}]</code> | <code>[{"value":"0.00","rows":6},{"value":"1108.08","rows":1},{"value":"1159.56","rows":1},{"value":"132.10","rows":1},{"value":"132.96","rows":1}]</code> |
| K2 | <code>[{"value":null,"rows":44}]</code> | <code>[{"value":"0.00","rows":8},{"value":"1078.48","rows":1},{"value":"1139.53","rows":1},{"value":"138.97","rows":1},{"value":"15.11","rows":1}]</code> |
| K3 | <code>[{"value":null,"rows":44}]</code> | <code>[{"value":"0.00","rows":6},{"value":"102.34","rows":1},{"value":"103.20","rows":1},{"value":"103.55","rows":1},{"value":"1148.97","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

attributed_conversions_14_day 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":46}]</code> | <code>[{"value":"0","rows":6},{"value":"1","rows":4},{"value":"10","rows":2},{"value":"11","rows":4},{"value":"12","rows":3}]</code> |
| K2 | <code>[{"value":null,"rows":44}]</code> | <code>[{"value":"0","rows":8},{"value":"1","rows":3},{"value":"10","rows":2},{"value":"12","rows":3},{"value":"13","rows":2}]</code> |
| K3 | <code>[{"value":null,"rows":44}]</code> | <code>[{"value":"0","rows":6},{"value":"1","rows":5},{"value":"10","rows":2},{"value":"11","rows":1},{"value":"12","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

attributed_conversions_30_day 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":46}]</code> | <code>[{"value":"0","rows":6},{"value":"1","rows":4},{"value":"10","rows":2},{"value":"11","rows":4},{"value":"12","rows":3}]</code> |
| K2 | <code>[{"value":null,"rows":44}]</code> | <code>[{"value":"0","rows":8},{"value":"1","rows":3},{"value":"10","rows":2},{"value":"12","rows":3},{"value":"13","rows":2}]</code> |
| K3 | <code>[{"value":null,"rows":44}]</code> | <code>[{"value":"0","rows":6},{"value":"1","rows":5},{"value":"10","rows":2},{"value":"11","rows":1},{"value":"12","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

| 约束 | 列 | 违反计数 |
|---|---|---|
| grain | platform,account_id,campaign_id,country_code,report_month | <code>{"distinct_key_groups":100,"duplicate_key_groups":100,"rows_in_duplicate_groups":12990,"excess_duplicate_rows":12890,"null_key_rows":12990,"nonnull_duplicate_key_groups":0,"nonnull_rows_in_duplicate_groups":0,"nonnull_excess_duplicate_rows":0,"null_containing_duplicate_key_groups":100,"rows_in_null_containing_duplicate_groups":12990}</code> |

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>32列；[{"column":"country_code","table_rows":12990},{"column":"report_month","table_rows":12990},{"column":"year","table_rows":12990}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"platform","value":"amazon_ads"},{"column":"data_last_updated","value":"2026-10-25 01:52:29.121387+08"}]</code> |
| B5_null_literal_output | <code>6输出列；[{"column":"spend","expression":["CAST(NULL AS DECIMAL(38, 2))"]},{"column":"attributed_sales_14_day","expression":["CAST(NULL AS DECIMAL(38, 2))"]},{"column":"attributed_sales_30_day","expression":["CAST(NULL AS DECIMAL(38, 2))"]}]</code> |
| C9_gold_runtime_text | <code>S5:60 CURRENT_TIMESTAMP；命中数=1</code> |
| C9_contract_runtime_text | <code>S3:3803 CURRENT_TIMESTAMP；命中数=1</code> |

## 轨迹索引（不放输出原文）

本题事件总数：99；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort &amp;&amp; cat config/layer_dependencies.yaml</code> | 7365 | true | false |
| 25 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 8424 | true | false |
| 37 | run | <code>python run.py &gt; /tmp/runlog3 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog3;</code> | 6937 | true | false |
| 83 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer in ('intermediate_models','marts_models'):<br> for m in c['modeling_spec'][layer]: print(m['name'],len(m['columns']</code> | 1029 | true | false |

### agent action 的 thought/message 命中原句

未找到命中原句。

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-006.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_country_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_country_report.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_ad_reporting__monthly_campaign_country_report/020_impl-006_ad_reporting__monthly_campaign_country_report.json`
- S11: `data/005_cs_work/impl-006/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
