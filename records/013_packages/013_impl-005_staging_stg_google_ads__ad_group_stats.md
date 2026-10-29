# impl-005 | staging | stg_google_ads__ad_group_stats | 差异：S1；日期 原记录

## 契约完整原文

S3:442–479

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

## agent 最终 SQL

S4

```sql
WITH base AS (
    SELECT 'google_ads'::VARCHAR AS source_relation, *
    FROM raw.ad_group_stats_data
),
validated AS (
    SELECT source_relation, CAST(customer_id AS VARCHAR(20)) account_id, try_cast(date AS DATE) date_day, CAST(base_ad_group AS VARCHAR(20)) ad_group_id, CAST(campaign_base_campaign AS VARCHAR(20)) campaign_id, case when ad_network_type in ('SEARCH','DISPLAY','MIXED','YOUTUBE') then ad_network_type end ad_network_type, device, clicks, CAST(cost_micros / 1000000.0 AS DECIMAL(15,2)) spend, impressions, CAST(conversions AS DECIMAL(10,2)) conversions, CAST(conversions_value AS DECIMAL(15,2)) conversions_value, view_through_conversions
    FROM base
)
SELECT *
FROM validated
WHERE account_id is not null and date_day is not null and ad_group_id is not null and campaign_id is not null
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select *
    from raw.ad_group_stats_data
),

validated as (
    select
        -- Platform identification per YAML spec (line 683)
        'google_ads' as platform,
        'google_ads' as source_relation,

        -- Core dimensions from YAML spec (lines 684-695)
        CAST(customer_id AS VARCHAR) as account_id,
        CAST(date AS DATE) as date_day,
        CAST(base_ad_group AS VARCHAR) as ad_group_id,
        CAST(campaign_id AS VARCHAR) as campaign_id,
        CAST(ad_network_type AS VARCHAR) as ad_network_type,
        CAST(device AS VARCHAR) as device,

        -- Core metrics from raw data per YAML spec (lines 696-734)
        coalesce(try_cast(active_view_impressions AS BIGINT), 0) as active_view_impressions,
        coalesce(try_cast(active_view_measurable_impressions AS BIGINT), 0) as active_view_measurable_impressions,
        coalesce(try_cast(clicks AS BIGINT), 0) as clicks,
        coalesce(try_cast(impressions AS BIGINT), 0) as impressions,
        coalesce(try_cast(interactions AS BIGINT), 0) as interactions,
        coalesce(try_cast(conversions AS DOUBLE), 0.0) as conversions,
        coalesce(try_cast(conversions_value AS DOUBLE), 0.0) as conversions_value,
        coalesce(try_cast(view_through_conversions AS BIGINT), 0) as view_through_conversions,
        coalesce(try_cast(cost_micros AS BIGINT), 0) as cost_micros,
        coalesce(try_cast(active_view_measurable_cost_micros AS BIGINT), 0) as active_view_measurable_cost_micros,
        interaction_event_types,

        -- Derived metrics from raw data per YAML spec (lines 727-733)
        cost_micros / 1000000.0 as cost,
        active_view_measurable_cost_micros / 1000000.0 as active_view_measurable_cost,

        -- Quality actions per YAML spec - timestamp for tracking (line 757)
        CURRENT_TIMESTAMP as _dbt_loaded_at

    from base

    -- Quality actions per YAML specification (lines 25-36)
    -- Remove rows with severe data quality issues
    WHERE CAST(date AS DATE) <= CURRENT_DATE
      AND CAST(date AS DATE) >= '2020-01-01'
      AND account_id is not null
      AND ad_group_id is not null
      AND campaign_id is not null
      -- Nullify invalid fields when record is still useful
      AND (ad_network_type is null OR ad_network_type IN ('SEARCH', 'DISPLAY', 'MIXED', 'YOUTUBE'))
),

metrics_calculated as (
    select
        platform,
        source_relation,
        account_id,
        date_day,
        ad_group_id,
        campaign_id,
        ad_network_type,
        device,
        active_view_impressions,
        active_view_measurable_impressions,
        clicks,
        impressions,
        interactions,
        conversions,
        conversions_value,
        view_through_conversions,
        cost_micros,
        cost,
        cost as spend,  -- Add spend alias for downstream compatibility
        active_view_measurable_cost_micros,
        active_view_measurable_cost,

        -- Calculate derived fields per YAML spec (lines 735-755)
        CASE
            WHEN active_view_measurable_impressions > 0
            THEN CAST(active_view_impressions AS DOUBLE) / CAST(active_view_measurable_impressions AS DOUBLE)
            ELSE 0.0
        END as active_view_viewability,

        CASE
            WHEN impressions > 0
            THEN CAST(active_view_measurable_impressions AS DOUBLE) / CAST(impressions AS DOUBLE)
            ELSE 0.0
        END as active_view_measurability,

        CASE
            WHEN impressions > 0
            THEN CAST(clicks AS DOUBLE) / CAST(impressions AS DOUBLE)
            ELSE 0.0
        END as click_through_rate,

        CASE
            WHEN clicks > 0
            THEN cost / CAST(clicks AS DOUBLE)
            ELSE 0.0
        END as cost_per_click,

        CASE
            WHEN impressions > 0
            THEN (cost / CAST(impressions AS DOUBLE)) * 1000.0
            ELSE 0.0
        END as cost_per_thousand_impressions,

        CASE
            WHEN conversions > 0
            THEN cost / CAST(conversions AS DOUBLE)
            ELSE 0.0
        END as cost_per_conversion,

        interaction_event_types,
        _dbt_loaded_at

    from validated
)

select
    platform,
    source_relation,
    account_id,
    date_day,
    ad_group_id,
    campaign_id,
    ad_network_type,
    device,
    active_view_impressions,
    active_view_measurable_impressions,
    clicks,
    impressions,
    interactions,
    conversions,
    conversions_value,
    view_through_conversions,
    cost_micros,
    spend,
    active_view_measurable_cost_micros,
    active_view_measurable_cost,
    active_view_viewability,
    active_view_measurability,
    click_through_rate,
    cost_per_click,
    cost_per_thousand_impressions,
    cost_per_conversion,
    interaction_event_types,
    _dbt_loaded_at
from metrics_calculated
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 10000 | 10000 | 9985 | 9985 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"account_id":"acc05079635656","ad_group_id":"93640637684","campaign_id":"cam35518233897"}</code> |
| K2 | <code>{"account_id":"acc09426864345","ad_group_id":"ad_30934736892","campaign_id":"cam79965975493"}</code> |
| K3 | <code>{"account_id":"acc15085741924","ad_group_id":"ad_79904208698","campaign_id":"cam63533158614"}</code> |
| K4 | <code>{"account_id":"acc33675221793","ad_group_id":"ad_14489204611","campaign_id":"cam06058842772"}</code> |
| K5 | <code>{"account_id":"acc94168095905","ad_group_id":"ad_77832428076","campaign_id":"cam56994651770"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| date_day | 0 | 0 | 0 | DATE | DATE |
| ad_group_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| ad_network_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| device | 0 | 0 | 0 | VARCHAR | VARCHAR |
| clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| conversions | 15 | 15 | 15 | DECIMAL(10,2) | DOUBLE |
| conversions_value | 2 | 2 | 2 | DECIMAL(15,2) | DOUBLE |
| view_through_conversions | 0 | 0 | 0 | BIGINT | BIGINT |
| spend | 15 | 15 | 15 | DECIMAL(15,2) | DOUBLE |

conversions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 1.40 | 1.4 |
| K2 | 1.50 | 1.5 |
| K3 | 3.00 | 3.0 |

conversions_value 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | 0.00 | 0.0 |
| K5 | 1758.80 | 1758.8 |

spend 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 80.14 | 80.144075 |
| K2 | 41.54 | 41.537916 |
| K3 | 99.20 | 99.200644 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"account_id":"ACC02369342072","ad_group_id":"00521930902","campaign_id":"CAM77520338340"},{"account_id":"ACC02369342072","ad_group_id":"08033415754","campaign_id":"CAM62780377926"},{"account_id":"ACC02369342072","ad_group_id":"09410789351","campaign_id":"CAM35406698903"},{"account_id":"ACC02369342072","ad_group_id":"18168259322","campaign_id":"CAM12501757507"},{"account_id":"ACC02369342072","ad_group_id":"19339528047","campaign_id":"CAM38089081162"}]</code> | <code>[{"account_id":"ACC02369342072","ad_group_id":"00521930902","campaign_id":"CAM65554097964"},{"account_id":"ACC02369342072","ad_group_id":"08033415754","campaign_id":"CAM84072075752"},{"account_id":"ACC02369342072","ad_group_id":"09410789351","campaign_id":"CAM89918855644"},{"account_id":"ACC02369342072","ad_group_id":"18168259322","campaign_id":"CAM30989386921"},{"account_id":"ACC02369342072","ad_group_id":"19339528047","campaign_id":"CAM06062627998"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"source_relation","value":"google_ads"}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"source_relation","expression":["CAST('google_ads' AS TEXT)"]}]</code> |
| C9_gold_runtime_text | <code>S5:38 CURRENT_TIMESTAMP；命中数=2</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory 'stg_google_ads__ad_group_stats':('ad_group_stats_data', '''source_relation, CAST(customer_id AS VARCHAR(20)) account_id, try_cast(date AS TIMESTAMPTZ)::DATE date_day, CAST(base_ad_group AS VARCHAR(20)) ad_group_id, CAST(campaign_base_campaign AS VARCHAR(20)) campaign_id, case when ad_network_type in ('SEARCH','DISPLAY','MIXED','YOUTUBE') then ad_network_type end ad_network_type, device, clicks, CAST(cost_micros / 1000000.0 AS DECIMAL(15,2)) spend, impressions, CAST(conversions AS DECIMAL(10,2)) conversions, CAST(conversions_value AS DECIMAL(15,2)) conversions_value, view_through_conversions''','''account_id is not null and date_day is not null and ad_group_id is not null and campaign_id is not null'''),</code> |

## 轨迹索引（不放输出原文）

本题事件总数：49；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print -exec wc -l {} \;</code> | 2838 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9858 | false | false |
| 11 | run | cat google_ads_start.yaml | 4209 | false | false |
| 13 | run | <code>find sql -maxdepth 2 -type f -print; sed -n '240,450p' run.py; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('google_ads_start.duckdb',read_only=True)<br>for (t,) in c.execute("select table_name from in</code> | 16568 | false | false |
| 15 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>S=Path('sql/staging')<br># helper CTE SQL table<br>spec={<br>'stg_google_ads__account_history':('account_history_d</code> | 0 | false | false |
| 21 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>M=Path('sql/marts')<br># common basic report templates<br><br>def write(name,sql): (M/f'{name}.sql').write_text(sql)<br>write('google_ads__account_report',"""WI</code> | 0 | false | false |
| 25 | run | <code>sed -i "s/and ad_network_type in ('SEARCH','DISPLAY','MIXED','YOUTUBE') or ad_network_type is null/and (ad_network_type in ('SEARCH','DISPLAY','MIXED','YOUTUBE') or ad_network_type is null)/" sql/stag</code> | 8152 | true | false |
| 31 | run | <code>python run.py &gt; /tmp/run2.log 2&gt;&amp;1; grep -E 'ERROR&#124;Layer complete&#124;rows$' /tmp/run2.log &#124; tail -60</code> | 2499 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb, pathlib<br>c=duckdb.connect('google_ads.duckdb',read_only=True)<br>for schema in ('staging','intermediate','marts'):<br> for (t,) in c.execute(f"select table_name from informatio</code> | 2322 | true | false |

### agent action 的 thought/message 命中原句

event 15 / message

```text
'stg_google_ads__ad_group_stats':('ad_group_stats_data', '''source_relation, CAST(customer_id AS VARCHAR(20)) account_id, try_cast(date AS TIMESTAMPTZ)::DATE date_day, CAST(base_ad_group AS VARCHAR(20)) ad_group_id, CAST(campaign_base_campaign AS VARCHAR(20)) campaign_id, case when ad_network_type in ('SEARCH','DISPLAY','MIXED','YOUTUBE') then ad_network_type end ad_network_type, device, clicks, CAST(cost_micros / 1000000.0 AS DECIMAL(15,2)) spend, impressions, CAST(conversions AS DECIMAL(10,2)) conversions, CAST(conversions_value AS DECIMAL(15,2)) conversions_value, view_through_conversions''','''account_id is not null and date_day is not null and ad_group_id is not null and campaign_id is not null'''),
```
event 21 / message

```text
write('google_ads__ad_group_report',"""WITH s AS (SELECT * FROM staging.stg_google_ads__ad_group_stats), ag AS (SELECT * FROM staging.stg_google_ads__ad_group_history WHERE is_most_recent_record), c AS (SELECT * FROM staging.stg_google_ads__campaign_history WHERE is_most_recent_record), a AS (SELECT * FROM staging.stg_google_ads__account_history WHERE is_most_recent_record)
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-005.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-005/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_group_stats.sql`
- S6: `records/006_contract_impl-005.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/result.md`
- S10: `records/012_packages/012_impl-005_staging_stg_google_ads__ad_group_stats.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/google_ads.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/google_ads.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions`
