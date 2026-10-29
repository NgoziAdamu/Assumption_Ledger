# impl-006 | intermediate | int_ad_reporting__account_report | 差异：S1；日期 原记录

## 契约完整原文

S3:1341–1419

```yaml
    - name: int_ad_reporting__account_report
      description: Daily account-level ad metrics aggregated per platform from campaign report
      grain: One row per platform + normalized account_id + date_day
      source_models:
      - intermediate.int_ad_reporting__campaign_report
      business_logic: '- Group campaign-level rows by platform, account_id normalized by replacing NULL with ''0'' and casting to text, and date_day. - Set segmentation fields not used at account level to NULL: ad_network_type, device, interaction_event_types. - Aggregate totals across all campaigns in each group: - Sum impressions, clicks, interactions, cost, conversions, conversions_value, and view_through_conversions; missing values are ignored, and if all values are missing the result is NULL. - For active view sums (impressions, measurable impressions, measurable cost), treat missing row values as 0 before summing; if all inputs are missing the result is 0. - For active view averages (measurability, viewability), treat missing row values as 0 and take the unweighted average across rows. - Derived metrics (computed from the aggregated totals): - Click-through rate (percent) = total clicks / total impressions × 100, rounded to 4 decimals; returns 0 if total impressions is not greater than 0; returns NULL if total clicks is NULL while impressions are positive. - Cost per click = total cost / total clicks, rounded to 2 decimals; returns 0 if total clicks is not greater than 0; returns NULL if total cost is NULL while clicks are positive. - Cost per thousand impressions = total cost / total impressions × 1000, rounded to 2 decimals; returns 0 if total impressions is not greater than 0; returns NULL if total cost is NULL while impressions are positive. - Cost per conversion = total cost / total conversions, rounded to 2 decimals; returns 0 if total conversions is not greater than 0; returns NULL if total cost is NULL while conversions are positive. - Return on ad spend = total conversion value / total cost, rounded to 4 decimals; returns 0 unless both totals are greater than 0. - _dbt_loaded_at is the latest timestamp across grouped rows (MAX); if all inputs are missing, the result is NULL.'
      columns:
      - name: platform
        data_type: VARCHAR
        description: Advertising platform for the aggregated row
      - name: account_id
        data_type: VARCHAR
        description: Account ID with NULL replaced by '0' and cast to text; grouping key
      - name: date_day
        data_type: DATE
        description: Reporting date at day level; grouping key
      - name: ad_network_type
        data_type: INTEGER
        description: Not used in this model; always NULL
      - name: device
        data_type: INTEGER
        description: Not used in this model; always NULL
      - name: impressions
        data_type: HUGEINT
        description: Sum of impressions across campaigns; NULLs ignored; NULL if all inputs are NULL
      - name: clicks
        data_type: HUGEINT
        description: Sum of clicks across campaigns; NULLs ignored; NULL if all inputs are NULL
      - name: interactions
        data_type: HUGEINT
        description: Sum of interactions across campaigns; NULLs ignored; NULL if all inputs are NULL
      - name: cost
        data_type: DECIMAL(38,2)
        description: Sum of cost across campaigns; NULLs ignored; NULL if all inputs are NULL; currency from source
      - name: conversions
        data_type: HUGEINT
        description: Sum of conversions across campaigns; NULLs ignored; NULL if all inputs are NULL
      - name: conversions_value
        data_type: DECIMAL(38,2)
        description: Sum of conversion value across campaigns; NULLs ignored; NULL if all inputs are NULL
      - name: view_through_conversions
        data_type: HUGEINT
        description: Sum of view-through conversions across campaigns; NULLs ignored; NULL if all inputs are NULL
      - name: active_view_impressions
        data_type: HUGEINT
        description: Sum of active view impressions with missing values treated as 0; 0 if all inputs are missing
      - name: active_view_measurable_impressions
        data_type: HUGEINT
        description: Sum of measurable impressions with missing values treated as 0; 0 if all inputs are missing
      - name: active_view_measurable_cost
        data_type: HUGEINT
        description: Sum of measurable cost with missing values treated as 0; 0 if all inputs are missing
      - name: active_view_measurability
        data_type: DOUBLE
        description: Unweighted average of measurability with missing values treated as 0
      - name: active_view_viewability
        data_type: DOUBLE
        description: Unweighted average of viewability with missing values treated as 0
      - name: click_through_rate
        data_type: DOUBLE
        description: 'CTR in percent: (total clicks/total impressions)×100, rounded to 4 decimals; 0 if impressions not > 0; NULL if clicks total is NULL while impressions are positive'
      - name: cost_per_click
        data_type: DOUBLE
        description: 'CPC: total cost/total clicks, rounded to 2 decimals; 0 if clicks not > 0; NULL if cost total is NULL while clicks are positive'
      - name: cost_per_thousand_impressions
        data_type: DOUBLE
        description: 'CPM: total cost/total impressions×1000, rounded to 2 decimals; 0 if impressions not > 0; NULL if cost total is NULL while impressions are positive'
      - name: cost_per_conversion
        data_type: DOUBLE
        description: 'CPA: total cost/total conversions, rounded to 2 decimals; 0 if conversions not > 0; NULL if cost total is NULL while conversions are positive'
      - name: return_on_ad_spend
        data_type: DOUBLE
        description: 'ROAS: total conversion value/total cost, rounded to 4 decimals; 0 unless both totals are greater than 0'
      - name: interaction_event_types
        data_type: INTEGER
        description: Not used in this model; always NULL
      - name: _dbt_loaded_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Latest load timestamp across grouped rows; NULL if all inputs are NULL
```

## agent 最终 SQL

S4

```sql
SELECT
    CAST("platform" AS VARCHAR) AS "platform",
    CAST("account_id" AS VARCHAR) AS "account_id",
    CAST("date_day" AS DATE) AS "date_day",
    CAST("ad_network_type" AS INTEGER) AS "ad_network_type",
    CAST("device" AS INTEGER) AS "device",
    CAST("impressions" AS HUGEINT) AS "impressions",
    CAST("clicks" AS HUGEINT) AS "clicks",
    CAST("interactions" AS HUGEINT) AS "interactions",
    CAST("cost" AS DECIMAL(38,2)) AS "cost",
    CAST("conversions" AS HUGEINT) AS "conversions",
    CAST("conversions_value" AS DECIMAL(38,2)) AS "conversions_value",
    CAST("view_through_conversions" AS HUGEINT) AS "view_through_conversions",
    CAST("active_view_impressions" AS HUGEINT) AS "active_view_impressions",
    CAST("active_view_measurable_impressions" AS HUGEINT) AS "active_view_measurable_impressions",
    CAST("active_view_measurable_cost" AS HUGEINT) AS "active_view_measurable_cost",
    CAST("active_view_measurability" AS DOUBLE) AS "active_view_measurability",
    CAST("active_view_viewability" AS DOUBLE) AS "active_view_viewability",
    CAST("click_through_rate" AS DOUBLE) AS "click_through_rate",
    CAST("cost_per_click" AS DOUBLE) AS "cost_per_click",
    CAST("cost_per_thousand_impressions" AS DOUBLE) AS "cost_per_thousand_impressions",
    CAST("cost_per_conversion" AS DOUBLE) AS "cost_per_conversion",
    CAST("return_on_ad_spend" AS DOUBLE) AS "return_on_ad_spend",
    CAST("interaction_event_types" AS INTEGER) AS "interaction_event_types",
    CAST("_dbt_loaded_at" AS TIMESTAMP WITH TIME ZONE) AS "_dbt_loaded_at"
FROM intermediate.int_ad_reporting__campaign_report
```

## gold SQL（仅供定位差异）

S5

```sql
-- Intermediate Account Report Model
-- Combines account-level data from all advertising platforms
-- Standardizes metrics and adds platform identification
-- Currently using aggregated data from campaign level due to account staging errors

SELECT 
    -- Platform identifier
    platform,
    
    -- Primary Keys
    CAST(COALESCE(account_id, '0') AS VARCHAR) AS account_id,
    date_day,
    
    -- Segmentation attributes (aggregated)
    NULL AS ad_network_type,
    NULL AS device,
    
    -- Performance Metrics (aggregated from campaign level)
    SUM(impressions) AS impressions,
    SUM(clicks) AS clicks,
    SUM(interactions) AS interactions,
    
    -- Cost Metrics
    SUM(cost) AS cost,
    
    -- Conversion Metrics
    SUM(conversions) AS conversions,
    SUM(conversions_value) AS conversions_value,
    SUM(view_through_conversions) AS view_through_conversions,
    
    -- Viewability Metrics (aggregated)
    SUM(COALESCE(active_view_impressions, 0)) AS active_view_impressions,
    SUM(COALESCE(active_view_measurable_impressions, 0)) AS active_view_measurable_impressions,
    SUM(COALESCE(active_view_measurable_cost, 0)) AS active_view_measurable_cost,
    AVG(COALESCE(active_view_measurability, 0)) AS active_view_measurability,
    AVG(COALESCE(active_view_viewability, 0)) AS active_view_viewability,
    
    -- Calculated Metrics
    CASE 
        WHEN SUM(impressions) > 0 THEN ROUND((CAST(SUM(clicks) AS DECIMAL) / CAST(SUM(impressions) AS DECIMAL)) * 100, 4)
        ELSE 0 
    END AS click_through_rate,
    
    CASE 
        WHEN SUM(clicks) > 0 THEN ROUND(SUM(cost) / SUM(clicks), 2)
        ELSE 0 
    END AS cost_per_click,
    
    CASE 
        WHEN SUM(impressions) > 0 THEN ROUND((SUM(cost) / SUM(impressions)) * 1000, 2)
        ELSE 0 
    END AS cost_per_thousand_impressions,
    
    CASE 
        WHEN SUM(conversions) > 0 THEN ROUND(SUM(cost) / SUM(conversions), 2)
        ELSE 0 
    END AS cost_per_conversion,
    
    CASE 
        WHEN SUM(cost) > 0 AND SUM(conversions_value) > 0 THEN ROUND(SUM(conversions_value) / SUM(cost), 4)
        ELSE 0 
    END AS return_on_ad_spend,
    
    -- Additional metadata
    NULL AS interaction_event_types,
    MAX(_dbt_loaded_at) AS _dbt_loaded_at

FROM intermediate.int_ad_reporting__campaign_report
GROUP BY platform, CAST(COALESCE(account_id, '0') AS VARCHAR), date_day
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 12990 | 1430 | 1430 | 1430 | 1430 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| date_day | 0 | 0 | 0 | DATE | DATE |
| ad_network_type | 0 | 0 | 0 | INTEGER | INTEGER |
| device | 0 | 0 | 0 | INTEGER | INTEGER |
| impressions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| clicks | 0 | 0 | 0 | HUGEINT | HUGEINT |
| interactions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| cost | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| conversions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| conversions_value | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| view_through_conversions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| active_view_impressions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| active_view_measurable_impressions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| active_view_measurable_cost | 0 | 0 | 0 | HUGEINT | HUGEINT |
| active_view_measurability | 0 | 0 | 0 | DOUBLE | DOUBLE |
| active_view_viewability | 0 | 0 | 0 | DOUBLE | DOUBLE |
| click_through_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cost_per_click | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cost_per_thousand_impressions | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cost_per_conversion | 0 | 0 | 0 | DOUBLE | DOUBLE |
| return_on_ad_spend | 0 | 0 | 0 | DOUBLE | DOUBLE |
| interaction_event_types | 0 | 0 | 0 | INTEGER | INTEGER |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"account_id":null,"date_day":"2021-01-01","ad_network_type":null,"device":null},{"account_id":null,"date_day":"2021-01-02","ad_network_type":null,"device":null},{"account_id":null,"date_day":"2021-01-03","ad_network_type":null,"device":null},{"account_id":null,"date_day":"2021-01-04","ad_network_type":null,"device":null},{"account_id":null,"date_day":"2021-01-05","ad_network_type":null,"device":null}]</code> | <code>[{"account_id":"0","date_day":"2021-01-01","ad_network_type":null,"device":null},{"account_id":"0","date_day":"2021-01-02","ad_network_type":null,"device":null},{"account_id":"0","date_day":"2021-01-03","ad_network_type":null,"device":null},{"account_id":"0","date_day":"2021-01-04","ad_network_type":null,"device":null},{"account_id":"0","date_day":"2021-01-05","ad_network_type":null,"device":null}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>9列；[{"column":"account_id","table_rows":12990},{"column":"ad_network_type","table_rows":12990},{"column":"device","table_rows":12990}]</code> |
| A3_constant_nonnull_column | <code>4列；[{"column":"platform","value":"amazon_ads"},{"column":"interactions","value":"0"},{"column":"view_through_conversions","value":"0"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["interactions","view_through_conversions"],"nonnull_equal_rows":12990,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["interactions","view_through_conversions"],"nonnull_equal_rows":12990,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B8_shared_single_source | <code>唯一源=intermediate.int_ad_reporting__campaign_report；目标数=4；例=["intermediate.int_ad_reporting__account_report","intermediate.int_ad_reporting__monthly_campaign_country_report","intermediate.int_ad_reporting__monthly_campaign_region_report"]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：99；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort &amp;&amp; cat config/layer_dependencies.yaml</code> | 7365 | true | false |
| 23 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>import yaml,re,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))['modeling_spec']<br># output schema<br><br>def parse_src(s):<br> x=s.split('.')[-1]<br> if x.startswith('int_'): return</code> | 0 | false | false |
| 25 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 8424 | true | false |
| 27 | run | <code>cat &gt; /tmp/fallback.py &lt;&lt;'PY'<br>import yaml,os<br>D=yaml.safe_load(open('docs/data_contract.yaml'))<br># build schemas lookup<br>schemas={m['name']:[x['name'] for x in m['columns']] for layer in ('intermediate_m</code> | 0 | false | false |
| 37 | run | <code>python run.py &gt; /tmp/runlog3 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog3;</code> | 6937 | true | false |
| 47 | run | <code>grep -A12 -B2 'unified_campaign_metrics' /tmp/runlog5 &#124; head -25;</code> | 2253 | true | false |
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__account_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__account_report.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_int_ad_reporting__account_report/020_impl-006_int_ad_reporting__account_report.json`
- S11: `data/005_cs_work/impl-006/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
