# impl-006 | intermediate | int_ad_reporting__ad_report | 差异：S1；日期 原记录

## 契约完整原文

S3:1517–1623

```yaml
    - name: int_ad_reporting__ad_report
      description: Unified ad-level report standardizing Facebook Ads and Apple Search Ads by appending source rows
      grain: One row per (platform, ad_id, date_day) source record; duplicates preserved
      source_models:
      - staging.stg_facebook_ads__ad_report
      - staging.stg_apple_search_ads__ad_report
      business_logic: '- Build a standardized ad report by stacking rows from the two source models; no aggregation, filtering, or reordering; original row multiplicity is preserved. - Facebook Ads mapping: - account_id from source; campaign_id NULL; ad_group_id NULL; ad_network_type NULL; device NULL. - impressions from source; clicks from inline_link_clicks; interactions set to 0. - cost from spend. - conversions set to 0; conversions_value set to 0.0; view_through_conversions set to 0. - active_view_* fields NULL. - attributed_* fields NULL. - installs NULL; taps NULL. - click_through_rate from source; cost_per_click from source; cost_per_thousand_impressions from source; cost_per_conversion set to 0.0; return_on_ad_spend set to 0.0. - interaction_event_types NULL; _dbt_loaded_at passed through. - Apple Search Ads mapping: - account_id NULL; campaign_id from source; ad_group_id from source; ad_network_type NULL; device NULL. - impressions converted to integer; clicks from taps converted to integer; interactions set to 0. - cost from spend. - conversions from source; conversions_value set to 0.0; view_through_conversions set to 0. - active_view_* fields NULL. - attributed_* fields NULL. - installs from new_downloads converted to integer; taps converted to integer. - click_through_rate from tap_through_rate; cost_per_click from cost_per_tap; cost_per_thousand_impressions set to 0.0; cost_per_conversion from source; return_on_ad_spend set to 0.0. - interaction_event_types NULL; _dbt_loaded_at passed through. - Numeric constants: 0 is used for integer columns; 0.0 is used for decimal/double columns. Conversions to integer are performed where noted; no other rounding is applied. NULLs are set exactly as indicated.'
      columns:
      - name: platform
        data_type: VARCHAR
        description: Platform identifier passed through from each source row
      - name: ad_id
        data_type: VARCHAR
        description: Ad identifier from source; pairs with platform and date_day to define row grain
      - name: date_day
        data_type: DATE
        description: Report date (day) from source; no transformation
      - name: account_id
        data_type: VARCHAR
        description: 'Facebook: account_id; Apple: NULL'
      - name: campaign_id
        data_type: VARCHAR
        description: 'Facebook: NULL; Apple: campaign_id'
      - name: ad_group_id
        data_type: VARCHAR
        description: 'Facebook: NULL; Apple: ad_group_id'
      - name: ad_network_type
        data_type: INTEGER
        description: NULL for all sources
      - name: device
        data_type: INTEGER
        description: NULL for all sources
      - name: impressions
        data_type: INTEGER
        description: 'Facebook: impressions; Apple: impressions converted to integer'
      - name: clicks
        data_type: INTEGER
        description: 'Facebook: inline_link_clicks; Apple: taps converted to integer'
      - name: interactions
        data_type: INTEGER
        description: Constant 0 in both branches
      - name: cost
        data_type: DECIMAL(18,2)
        description: Spend from source; typed as DECIMAL(18,2)
      - name: conversions
        data_type: INTEGER
        description: 'Facebook: 0; Apple: conversions'
      - name: conversions_value
        data_type: DECIMAL(2,1)
        description: Constant 0.0 in both branches
      - name: view_through_conversions
        data_type: INTEGER
        description: Constant 0 in both branches
      - name: active_view_impressions
        data_type: INTEGER
        description: NULL for all sources
      - name: active_view_measurable_impressions
        data_type: INTEGER
        description: NULL for all sources
      - name: active_view_measurable_cost
        data_type: INTEGER
        description: NULL for all sources
      - name: active_view_measurability
        data_type: INTEGER
        description: NULL for all sources
      - name: active_view_viewability
        data_type: INTEGER
        description: NULL for all sources
      - name: attributed_sales_14_d
        data_type: INTEGER
        description: NULL for all sources
      - name: attributed_sales_30_d
        data_type: INTEGER
        description: NULL for all sources
      - name: attributed_conversions_14_d
        data_type: INTEGER
        description: NULL for all sources
      - name: attributed_conversions_30_d
        data_type: INTEGER
        description: NULL for all sources
      - name: installs
        data_type: INTEGER
        description: 'Facebook: NULL; Apple: new_downloads converted to integer'
      - name: taps
        data_type: INTEGER
        description: 'Facebook: NULL; Apple: taps converted to integer'
      - name: click_through_rate
        data_type: DOUBLE
        description: 'Facebook: click_through_rate; Apple: tap_through_rate'
      - name: cost_per_click
        data_type: DOUBLE
        description: 'Facebook: cost_per_click; Apple: cost_per_tap'
      - name: cost_per_thousand_impressions
        data_type: DOUBLE
        description: 'Facebook: cost_per_thousand_impressions; Apple: 0.0'
      - name: cost_per_conversion
        data_type: DOUBLE
        description: 'Facebook: 0.0; Apple: cost_per_conversion'
      - name: return_on_ad_spend
        data_type: DECIMAL(2,1)
        description: Constant 0.0 in both branches
      - name: interaction_event_types
        data_type: INTEGER
        description: NULL for all sources
      - name: _dbt_loaded_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Load timestamp passed through from sources for data freshness auditing
```

## agent 最终 SQL

S4

```sql
SELECT
    CAST("platform" AS VARCHAR) AS "platform",
    CAST("ad_id" AS VARCHAR) AS "ad_id",
    CAST("date_day" AS DATE) AS "date_day",
    CAST("account_id" AS VARCHAR) AS "account_id",
    NULL::VARCHAR AS "campaign_id",
    NULL::VARCHAR AS "ad_group_id",
    NULL::INTEGER AS "ad_network_type",
    NULL::INTEGER AS "device",
    CAST("impressions" AS INTEGER) AS "impressions",
    NULL::INTEGER AS "clicks",
    NULL::INTEGER AS "interactions",
    NULL::DECIMAL(18,2) AS "cost",
    NULL::INTEGER AS "conversions",
    NULL::DECIMAL(2,1) AS "conversions_value",
    NULL::INTEGER AS "view_through_conversions",
    NULL::INTEGER AS "active_view_impressions",
    NULL::INTEGER AS "active_view_measurable_impressions",
    NULL::INTEGER AS "active_view_measurable_cost",
    NULL::INTEGER AS "active_view_measurability",
    NULL::INTEGER AS "active_view_viewability",
    NULL::INTEGER AS "attributed_sales_14_d",
    NULL::INTEGER AS "attributed_sales_30_d",
    NULL::INTEGER AS "attributed_conversions_14_d",
    NULL::INTEGER AS "attributed_conversions_30_d",
    NULL::INTEGER AS "installs",
    NULL::INTEGER AS "taps",
    CAST("click_through_rate" AS DOUBLE) AS "click_through_rate",
    CAST("cost_per_click" AS DOUBLE) AS "cost_per_click",
    CAST("cost_per_thousand_impressions" AS DOUBLE) AS "cost_per_thousand_impressions",
    NULL::DOUBLE AS "cost_per_conversion",
    NULL::DECIMAL(2,1) AS "return_on_ad_spend",
    NULL::INTEGER AS "interaction_event_types",
    CAST("_dbt_loaded_at" AS TIMESTAMP WITH TIME ZONE) AS "_dbt_loaded_at"
FROM staging.stg_facebook_ads__ad_report
```

## gold SQL（仅供定位差异）

S5

```sql
-- Intermediate Ad Report Model
-- Combines ad-level data from all advertising platforms
-- Standardizes metrics and adds platform identification

-- Facebook Ads Ad Report
SELECT 
    -- Platform identifier
    platform,
    
    -- Primary Keys
    ad_id,
    date_day,
    
    -- Hierarchy References
    account_id,
    NULL AS campaign_id,
    NULL AS ad_group_id,
    
    -- Segmentation attributes
    NULL AS ad_network_type,
    NULL AS device,
    
    -- Performance Metrics
    impressions,
    inline_link_clicks AS clicks,
    0 AS interactions,
    
    -- Cost Metrics
    spend AS cost,
    
    -- Conversion Metrics
    0 AS conversions,
    0.0 AS conversions_value,
    0 AS view_through_conversions,
    
    -- Viewability Metrics
    NULL AS active_view_impressions,
    NULL AS active_view_measurable_impressions,
    NULL AS active_view_measurable_cost,
    NULL AS active_view_measurability,
    NULL AS active_view_viewability,
    
    -- Amazon Ads specific metrics
    NULL AS attributed_sales_14_d,
    NULL AS attributed_sales_30_d,
    NULL AS attributed_conversions_14_d,
    NULL AS attributed_conversions_30_d,
    
    -- Apple Search Ads specific metrics
    NULL AS installs,
    NULL AS taps,
    
    -- Calculated Metrics
    click_through_rate,
    cost_per_click,
    cost_per_thousand_impressions,
    0.0 AS cost_per_conversion,
    0.0 AS return_on_ad_spend,
    
    -- Additional metadata
    NULL AS interaction_event_types,
    
    -- Data Quality
    _dbt_loaded_at

FROM staging.stg_facebook_ads__ad_report

UNION ALL

-- Apple Search Ads Ad Report
SELECT 
    -- Platform identifier
    platform,
    
    -- Primary Keys
    ad_id,
    date_day,
    
    -- Hierarchy References
    NULL AS account_id,
    campaign_id,
    ad_group_id,
    
    -- Segmentation attributes
    NULL AS ad_network_type,
    NULL AS device,
    
    -- Performance Metrics
    CAST(impressions AS INTEGER) AS impressions,
    CAST(taps AS INTEGER) AS clicks,
    0 AS interactions,
    
    -- Cost Metrics
    spend AS cost,
    
    -- Conversion Metrics
    conversions,
    0.0 AS conversions_value,
    0 AS view_through_conversions,
    
    -- Viewability Metrics
    NULL AS active_view_impressions,
    NULL AS active_view_measurable_impressions,
    NULL AS active_view_measurable_cost,
    NULL AS active_view_measurability,
    NULL AS active_view_viewability,
    
    -- Amazon Ads specific metrics
    NULL AS attributed_sales_14_d,
    NULL AS attributed_sales_30_d,
    NULL AS attributed_conversions_14_d,
    NULL AS attributed_conversions_30_d,
    
    -- Apple Search Ads specific metrics
    CAST(new_downloads AS INTEGER) AS installs,
    CAST(taps AS INTEGER) AS taps,
    
    -- Calculated Metrics
    tap_through_rate AS click_through_rate,
    cost_per_tap AS cost_per_click,
    0.0 AS cost_per_thousand_impressions,
    cost_per_conversion,
    0.0 AS return_on_ad_spend,
    
    -- Additional metadata
    NULL AS interaction_event_types,
    
    -- Data Quality
    _dbt_loaded_at

FROM staging.stg_apple_search_ads__ad_report
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1000 | 2500 | 0 | 1500 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"ad_id":"1022412906784"}</code> |
| K2 | <code>{"ad_id":"1029119952816"}</code> |
| K3 | <code>{"ad_id":"1041423847830"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| ad_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| date_day | 0 | 0 | 0 | DATE | DATE |
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| ad_group_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| ad_network_type | 0 | 0 | 0 | INTEGER | INTEGER |
| device | 0 | 0 | 0 | INTEGER | INTEGER |
| impressions | 0 | 0 | 0 | INTEGER | INTEGER |
| clicks | 1000 | 1000 | 1000 | INTEGER | INTEGER |
| interactions | 1000 | 1000 | 1000 | INTEGER | INTEGER |
| cost | 1000 | 1000 | 1000 | DECIMAL(18,2) | DECIMAL(18,2) |
| conversions | 1000 | 1000 | 1000 | INTEGER | INTEGER |
| conversions_value | 1000 | 1000 | 1000 | DECIMAL(2,1) | DECIMAL(2,1) |
| view_through_conversions | 1000 | 1000 | 1000 | INTEGER | INTEGER |
| active_view_impressions | 0 | 0 | 0 | INTEGER | INTEGER |
| active_view_measurable_impressions | 0 | 0 | 0 | INTEGER | INTEGER |
| active_view_measurable_cost | 0 | 0 | 0 | INTEGER | INTEGER |
| active_view_measurability | 0 | 0 | 0 | INTEGER | INTEGER |
| active_view_viewability | 0 | 0 | 0 | INTEGER | INTEGER |
| attributed_sales_14_d | 0 | 0 | 0 | INTEGER | INTEGER |
| attributed_sales_30_d | 0 | 0 | 0 | INTEGER | INTEGER |
| attributed_conversions_14_d | 0 | 0 | 0 | INTEGER | INTEGER |
| attributed_conversions_30_d | 0 | 0 | 0 | INTEGER | INTEGER |
| installs | 0 | 0 | 0 | INTEGER | INTEGER |
| taps | 0 | 0 | 0 | INTEGER | INTEGER |
| click_through_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cost_per_click | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cost_per_thousand_impressions | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cost_per_conversion | 1000 | 1000 | 1000 | DOUBLE | DOUBLE |
| return_on_ad_spend | 1000 | 1000 | 1000 | DECIMAL(2,1) | DECIMAL(2,1) |
| interaction_event_types | 0 | 0 | 0 | INTEGER | INTEGER |

clicks 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 1 |
| K2 | null | 302 |
| K3 | null | 45 |

interactions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

cost 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 9.18 |
| K2 | null | 1287.68 |
| K3 | null | 239.28 |

conversions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

conversions_value 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0.0 |
| K2 | null | 0.0 |
| K3 | null | 0.0 |

view_through_conversions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

cost_per_conversion 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0.0 |
| K2 | null | 0.0 |
| K3 | null | 0.0 |

return_on_ad_spend 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0.0 |
| K2 | null | 0.0 |
| K3 | null | 0.0 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"ad_id":"APP01001454873"},{"ad_id":"APP01016986174"},{"ad_id":"APP01021182670"},{"ad_id":"APP01029752669"},{"ad_id":"APP01032305048"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>27列；[{"column":"campaign_id","table_rows":1000},{"column":"ad_group_id","table_rows":1000},{"column":"ad_network_type","table_rows":1000}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"platform","value":"FACEBOOK_ADS"},{"column":"_dbt_loaded_at","value":"2026-10-25 01:52:29.231412+08"}]</code> |
| B5_null_literal_output | <code>24输出列；[{"column":"campaign_id","expression":["CAST(NULL AS TEXT)"]},{"column":"ad_group_id","expression":["CAST(NULL AS TEXT)"]},{"column":"ad_network_type","expression":["CAST(NULL AS INT)"]}]</code> |
| B7_specified_not_read | <code>["staging.stg_apple_search_ads__ad_report"]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：99；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort &amp;&amp; cat config/layer_dependencies.yaml</code> | 7365 | true | false |
| 23 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>import yaml,re,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))['modeling_spec']<br># output schema<br><br>def parse_src(s):<br> x=s.split('.')[-1]<br> if x.startswith('int_'): return</code> | 0 | false | false |
| 25 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 8424 | true | false |
| 37 | run | <code>python run.py &gt; /tmp/runlog3 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog3;</code> | 6937 | true | false |
| 43 | run | <code>cat &gt; sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql &lt;&lt;'SQL'<br>WITH execution_clock AS (<br>    SELECT CURRENT_TIMESTAMP AS processed_at<br>),<br>amazon_rows AS (<br>    SELECT<br>        'amazon_ads'</code> | 0 | false | false |
| 81 | run | <code>find sql -type f &#124; wc -l; grep -R ';' sql --include='*.sql' &#124; head; git status --short 2&gt;/dev/null &#124;&#124; true; python - &lt;&lt;'PY'<br>import yaml,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c[</code> | 999 | false | false |
| 83 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer in ('intermediate_models','marts_models'):<br> for m in c['modeling_spec'][layer]: print(m['name'],len(m['columns']</code> | 1029 | true | false |
| 85 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>c=yaml.safe_load(open('docs/data_contract.yaml')); d=duckdb.connect('ad_reporting.duckdb',read_only=True)<br>for layer,key in [('staging','staging_contract'),('intermed</code> | 776 | false | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
 if name=='int_ad_reporting__ad_report':
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-006.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_int_ad_reporting__ad_report/020_impl-006_int_ad_reporting__ad_report.json`
- S11: `data/005_cs_work/impl-006/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
