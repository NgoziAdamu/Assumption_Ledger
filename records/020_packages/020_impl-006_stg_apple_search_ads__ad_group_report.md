# impl-006 | staging | stg_apple_search_ads__ad_group_report | 差异：S1；日期 2025-10-12

## 契约完整原文

S3:351–447

```yaml
    - name: "stg_apple_search_ads__ad_group_report"
      description: "Staging table for Apple Search Ads  Ad Group Report"
      columns:
        - name: "platform"
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "UPPER(platform) = 'APPLE_SEARCH_ADS'"
              on_failure: delete_row
        - name: "ad_group_id"
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "ad_group_id IS NOT NULL AND TRIM(ad_group_id) != '' AND LENGTH(ad_group_id) <= 50"
              on_failure: delete_row
            - rule: "REGEXP_LIKE(ad_group_id, '^[A-Za-z0-9_-]+$')"
              on_failure: delete_row
        - name: "date_day"
          data_type: DATE
          constraints: [not_null]
          validation_rules:
            - rule: "date_day IS NOT NULL AND date_day >= '2020-01-01' AND date_day <= CURRENT_DATE"
              on_failure: delete_row
            - rule: "date_day NOT IN ('1970-01-01','1900-01-01','9999-12-31')"
              on_failure: delete_row
        - name: "impressions"
          data_type: INTEGER
        - name: "taps"
          data_type: INTEGER
        - name: "tap_installs"
          data_type: INTEGER
        - name: "conversions"
          data_type: INTEGER
        - name: "new_downloads"
          data_type: INTEGER
        - name: "redownloads"
          data_type: INTEGER
        - name: "tap_new_downloads"
          data_type: INTEGER
        - name: "tap_redownloads"
          data_type: INTEGER
        - name: "spend"
          data_type: DECIMAL(18,2)
          validation_rules:
            - rule: "spend >= 0 AND spend <= 999999999999.99"
              on_failure: nullify_field
            - rule: "spend = ROUND(spend, 2)"
              on_failure: correct
            - rule: "spend IS NOT NULL OR spend = 0"
              on_failure: correct
        - name: "spend_currency"
          data_type: VARCHAR
        - name: "avg_cost_per_tap"
          data_type: DECIMAL(18,2)
        - name: "avg_cpt_currency"
          data_type: VARCHAR
          validation_rules:
            - rule: "avg_cpt_currency IS NULL OR avg_cpt_currency IN ('USD','EUR','GBP','JPY','AUD','CAD')"
              on_failure: nullify_field
            - rule: "LENGTH(avg_cpt_currency) <= 3"
              on_failure: nullify_field
            - rule: "avg_cpt_currency = UPPER(TRIM(avg_cpt_currency))"
              on_failure: correct
        - name: "avg_cost_per_acquisition"
          data_type: DECIMAL(18,2)
        - name: "avg_cpa_currency"
          data_type: VARCHAR
          validation_rules:
            - rule: "avg_cpa_currency IS NULL OR avg_cpa_currency IN ('USD','EUR','GBP','JPY','AUD','CAD')"
              on_failure: nullify_field
            - rule: "LENGTH(avg_cpa_currency) <= 3"
              on_failure: nullify_field
            - rule: "avg_cpa_currency = UPPER(TRIM(avg_cpa_currency))"
              on_failure: correct
        - name: "tap_through_rate"
          data_type: DECIMAL(10,6)
        - name: "conversion_rate"
          data_type: DECIMAL(10,6)
          validation_rules:
            - rule: "conversion_rate BETWEEN 0 AND 1"
              on_failure: nullify_field
        - name: "lat_on_installs"
          data_type: INTEGER
        - name: "lat_off_installs"
          data_type: INTEGER
        - name: "calculated_tap_through_rate"
          data_type: DOUBLE
        - name: "cost_per_tap"
          data_type: DOUBLE
        - name: "cost_per_conversion"
          data_type: DOUBLE
        - name: "_dbt_loaded_at"
          data_type: TIMESTAMP WITH TIME ZONE
          constraints: [not_null]
          validation_rules:
            - rule: "_dbt_loaded_at <= CURRENT_TIMESTAMP"
              on_failure: delete_row
```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT * FROM raw.apple_search_ad_group_report_data
),
cleaned AS (
    SELECT
        'APPLE_SEARCH_ADS' AS platform,
        CAST(TRY_CAST("ad_group_id" AS VARCHAR) AS VARCHAR) AS ad_group_id,
        CAST(TRY_CAST(date AS DATE) AS DATE) AS date_day,
        CAST(TRY_CAST("impressions" AS BIGINT) AS INTEGER) AS impressions,
        TRY_CAST("taps" AS INTEGER) AS taps,
        TRY_CAST("tap_installs" AS INTEGER) AS tap_installs,
        CAST(TRY_CAST("conversions" AS BIGINT) AS INTEGER) AS conversions,
        TRY_CAST("new_downloads" AS INTEGER) AS new_downloads,
        TRY_CAST("redownloads" AS INTEGER) AS redownloads,
        TRY_CAST("tap_new_downloads" AS INTEGER) AS tap_new_downloads,
        TRY_CAST("tap_redownloads" AS INTEGER) AS tap_redownloads,
        CAST(ROUND(TRY_CAST("local_spend_amount" AS DOUBLE), 2) AS DECIMAL(18,2)) AS spend,
        TRY_CAST("local_spend_currency" AS VARCHAR) AS spend_currency,
        TRY_CAST("avg_cpt_amount" AS DECIMAL(18,2)) AS avg_cost_per_tap,
        TRY_CAST("avg_cpt_currency" AS VARCHAR) AS avg_cpt_currency,
        TRY_CAST("avg_cpa_amount" AS DECIMAL(18,2)) AS avg_cost_per_acquisition,
        TRY_CAST("avg_cpa_currency" AS VARCHAR) AS avg_cpa_currency,
        TRY_CAST("tap_through_rate" AS DECIMAL(10,6)) AS tap_through_rate,
        TRY_CAST("conversion_rate" AS DECIMAL(10,6)) AS conversion_rate,
        TRY_CAST("lat_on_installs" AS INTEGER) AS lat_on_installs,
        TRY_CAST("lat_off_installs" AS INTEGER) AS lat_off_installs,
        CAST(NULL::DOUBLE AS DOUBLE) AS calculated_tap_through_rate,
        CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_tap,
        CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_conversion,
        CURRENT_TIMESTAMP AS _dbt_loaded_at
    FROM source_rows
)
SELECT * FROM cleaned
```

## gold SQL（仅供定位差异）

S5

```sql
-- Apple Search Ads Ad Group Report Staging Model
-- Standardizes raw Apple Search Ads ad group-level data for downstream consumption
-- Removes Fivetran-specific logic and converts to DuckDB-compatible SQL
-- Includes data quality validation rules per staging_data_specification.yaml

SELECT
    -- Platform Identifier (Rule 1: Platform name standardization)
    UPPER(TRIM('apple_search_ads')) AS platform,

    -- Primary Keys (with validation rules)
    CAST(
        CASE
            WHEN TRIM(CAST(ad_group_id AS VARCHAR)) = '' OR ad_group_id IS NULL THEN NULL
            WHEN NOT regexp_matches(TRIM(CAST(ad_group_id AS VARCHAR)), '^[A-Za-z0-9_-]+$') THEN NULL
            WHEN LENGTH(TRIM(CAST(ad_group_id AS VARCHAR))) > 50 THEN NULL
            ELSE TRIM(CAST(ad_group_id AS VARCHAR))
        END AS VARCHAR
    ) AS ad_group_id,

    CAST(
        CASE
            WHEN date IS NULL THEN NULL
            WHEN CAST(date AS DATE) < '2020-01-01' OR CAST(date AS DATE) > CURRENT_DATE THEN NULL
            WHEN CAST(date AS DATE) IN ('1970-01-01', '1900-01-01', '9999-12-31') THEN NULL
            ELSE date
        END AS DATE
    ) AS date_day,

    -- Performance Metrics (handle negative values)
    CAST(
        CASE WHEN impressions < 0 THEN 0 ELSE impressions END AS INTEGER
    ) AS impressions,

    CAST(
        CASE WHEN taps < 0 THEN 0 ELSE taps END AS INTEGER
    ) AS taps,

    CAST(
        CASE WHEN tap_installs < 0 THEN 0 ELSE tap_installs END AS INTEGER
    ) AS tap_installs,

    CAST(
        CASE WHEN conversions < 0 THEN 0 ELSE conversions END AS INTEGER
    ) AS conversions,

    CAST(
        CASE WHEN new_downloads < 0 THEN 0 ELSE new_downloads END AS INTEGER
    ) AS new_downloads,

    CAST(
        CASE
            WHEN redownloads = true THEN 1
            WHEN redownloads = false THEN 0
            WHEN CAST(COALESCE(redownloads, 0) AS INTEGER) < 0 THEN 0
            ELSE CAST(redownloads AS INTEGER)
        END AS INTEGER
    ) AS redownloads,

    CAST(
        CASE WHEN tap_new_downloads < 0 THEN 0 ELSE tap_new_downloads END AS INTEGER
    ) AS tap_new_downloads,

    CAST(
        CASE
            WHEN tap_redownloads = true THEN 1
            WHEN tap_redownloads = false THEN 0
            WHEN CAST(COALESCE(tap_redownloads, 0) AS INTEGER) < 0 THEN 0
            ELSE CAST(tap_redownloads AS INTEGER)
        END AS INTEGER
    ) AS tap_redownloads,

    -- Cost Metrics (Rule 5: Cost validation, as per YAML spec for spend)
    CAST(
        ROUND(
            CASE
                WHEN local_spend_amount IS NULL THEN 0.0
                WHEN local_spend_amount < 0 THEN 0.0
                WHEN local_spend_amount > 999999999999.99 THEN 999999999999.99
                ELSE local_spend_amount
            END, 2
        ) AS DECIMAL(18,2)
    ) AS spend,

    CAST(TRIM(CAST(local_spend_currency AS VARCHAR)) AS VARCHAR) AS spend_currency,

    CAST(
        CASE
            WHEN avg_cpt_amount < 0 THEN 0.0
            WHEN avg_cpt_amount IS NULL THEN 0.0
            ELSE ROUND(avg_cpt_amount, 2)
        END AS DECIMAL(18,2)
    ) AS avg_cost_per_tap,

    -- Currency validation (Rule 9: Invalid currency codes)
    CAST(
        CASE
            WHEN TRIM(avg_cpt_currency) IS NULL OR avg_cpt_currency = '' THEN NULL
            WHEN NOT UPPER(TRIM(avg_cpt_currency)) IN ('USD','EUR','GBP','JPY','AUD','CAD') THEN NULL
            WHEN LENGTH(TRIM(avg_cpt_currency)) > 3 THEN NULL
            ELSE UPPER(TRIM(avg_cpt_currency))
        END AS VARCHAR
    ) AS avg_cpt_currency,

    CAST(
        CASE
            WHEN avg_cpa_amount < 0 THEN 0.0
            WHEN avg_cpa_amount IS NULL THEN 0.0
            ELSE ROUND(avg_cpa_amount, 2)
        END AS DECIMAL(18,2)
    ) AS avg_cost_per_acquisition,

    CAST(
        CASE
            WHEN TRIM(avg_cpa_currency) IS NULL OR avg_cpa_currency = '' THEN NULL
            WHEN NOT UPPER(TRIM(avg_cpa_currency)) IN ('USD','EUR','GBP','JPY','AUD','CAD') THEN NULL
            WHEN LENGTH(TRIM(avg_cpa_currency)) > 3 THEN NULL
            ELSE UPPER(TRIM(avg_cpa_currency))
        END AS VARCHAR
    ) AS avg_cpa_currency,

    -- Rate Metrics (Rule 10: Rate validation to ensure bounds 0-1)
    CAST(
        CASE
            WHEN tap_through_rate IS NULL THEN NULL
            WHEN tap_through_rate = true THEN 1.0
            WHEN tap_through_rate = false THEN 0.0
            ELSE ROUND(CAST(tap_through_rate AS DECIMAL), 6)
        END AS DECIMAL(10,6)
    ) AS tap_through_rate,

    CAST(
        CASE
            WHEN conversion_rate IS NULL OR conversion_rate < 0 OR conversion_rate > 1.0 THEN NULL
            ELSE ROUND(conversion_rate, 6)
        END AS DECIMAL(10,6)
    ) AS conversion_rate,

    -- Install Attribution
    CAST(
        CASE
            WHEN lat_on_installs = true THEN 1
            WHEN lat_on_installs = false THEN 0
            WHEN CAST(COALESCE(lat_on_installs, 0) AS INTEGER) < 0 THEN 0
            ELSE CAST(lat_on_installs AS INTEGER)
        END AS INTEGER
    ) AS lat_on_installs,

    CAST(
        CASE
            WHEN lat_off_installs = true THEN 1
            WHEN lat_off_installs = false THEN 0
            WHEN CAST(COALESCE(lat_off_installs, 0) AS INTEGER) < 0 THEN 0
            ELSE CAST(lat_off_installs AS INTEGER)
        END AS INTEGER
    ) AS lat_off_installs,

    -- Calculated Metrics
    CAST(
        CASE
            WHEN impressions IS NULL OR impressions <= 0 THEN 0.0
            WHEN taps IS NULL OR taps < 0 THEN 0.0
            ELSE ROUND((CAST(taps AS DECIMAL) / CAST(impressions AS DECIMAL)) * 100, 4)
        END AS DOUBLE
    ) AS calculated_tap_through_rate,

    CAST(
        CASE
            WHEN taps IS NULL OR taps <= 0 THEN 0.0
            WHEN local_spend_amount IS NULL OR local_spend_amount < 0 THEN 0.0
            ELSE ROUND(
                ROUND(
                    CASE
                        WHEN local_spend_amount IS NULL THEN 0.0
                        WHEN local_spend_amount > 999999999999.99 THEN 999999999999.99
                        ELSE local_spend_amount
                    END, 2
                ) / taps, 2
            )
        END AS DOUBLE
    ) AS cost_per_tap,

    CAST(
        CASE
            WHEN conversions IS NULL OR conversions <= 0 THEN 0.0
            WHEN local_spend_amount IS NULL OR local_spend_amount < 0 THEN 0.0
            ELSE ROUND(
                ROUND(
                    CASE
                        WHEN local_spend_amount IS NULL THEN 0.0
                        WHEN local_spend_amount > 999999999999.99 THEN 999999999999.99
                        ELSE local_spend_amount
                    END, 2
                ) / conversions, 2
            )
        END AS DOUBLE
    ) AS cost_per_conversion,

    -- Data Quality (corrected datatype per YAML spec)
    CAST(CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE) AS _dbt_loaded_at

FROM raw.apple_search_ad_group_report_data

WHERE date IS NOT NULL
    AND ad_group_id IS NOT NULL
    AND UPPER('apple_search_ads') IS NOT NULL
    -- Apply validation rules from YAML configuration
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1500 | 1500 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"ad_group_id":"app01008765466"}</code> |
| K2 | <code>{"ad_group_id":"app01011668907"}</code> |
| K3 | <code>{"ad_group_id":"app01017342399"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| ad_group_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| avg_cost_per_acquisition | 0 | 0 | 0 | DECIMAL(18,2) | DECIMAL(18,2) |
| avg_cost_per_tap | 0 | 0 | 0 | DECIMAL(18,2) | DECIMAL(18,2) |
| avg_cpa_currency | 1500 | 1500 | 1500 | VARCHAR | VARCHAR |
| avg_cpt_currency | 1500 | 1500 | 1500 | VARCHAR | VARCHAR |
| calculated_tap_through_rate | 1500 | 1500 | 1500 | DOUBLE | DOUBLE |
| conversion_rate | 1469 | 1469 | 1469 | DECIMAL(10,6) | DECIMAL(10,6) |
| conversions | 0 | 0 | 0 | INTEGER | INTEGER |
| cost_per_conversion | 1500 | 1500 | 1500 | DOUBLE | DOUBLE |
| cost_per_tap | 1500 | 1500 | 1500 | DOUBLE | DOUBLE |
| date_day | 0 | 0 | 0 | DATE | DATE |
| impressions | 0 | 0 | 0 | INTEGER | INTEGER |
| lat_off_installs | 0 | 0 | 0 | INTEGER | INTEGER |
| lat_on_installs | 0 | 0 | 0 | INTEGER | INTEGER |
| new_downloads | 0 | 0 | 0 | INTEGER | INTEGER |
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| redownloads | 0 | 0 | 0 | INTEGER | INTEGER |
| spend | 0 | 0 | 0 | DECIMAL(18,2) | DECIMAL(18,2) |
| spend_currency | 0 | 0 | 0 | VARCHAR | VARCHAR |
| tap_installs | 0 | 0 | 0 | INTEGER | INTEGER |
| tap_new_downloads | 0 | 0 | 0 | INTEGER | INTEGER |
| tap_redownloads | 0 | 0 | 0 | INTEGER | INTEGER |
| tap_through_rate | 0 | 0 | 0 | DECIMAL(10,6) | DECIMAL(10,6) |
| taps | 0 | 0 | 0 | INTEGER | INTEGER |

avg_cpa_currency 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | mock_avg_cpa_currency_681 | null |
| K2 | mock_avg_cpa_currency_302 | null |
| K3 | mock_avg_cpa_currency_448 | null |

avg_cpt_currency 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | mock_avg_cpt_currency_425 | null |
| K2 | mock_avg_cpt_currency_753 | null |
| K3 | mock_avg_cpt_currency_582 | null |

calculated_tap_through_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 6.6667 |
| K2 | null | 7.9208 |
| K3 | null | 6.5934 |

conversion_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 68.000000 | null |
| K2 | 51.000000 | null |
| K3 | 14.000000 | null |

cost_per_conversion 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 59.3 |
| K2 | null | 7.44 |
| K3 | null | 20.18 |

cost_per_tap 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 37.06 |
| K2 | null | 3.49 |
| K3 | null | 18.16 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>3列；[{"column":"calculated_tap_through_rate","table_rows":1500},{"column":"cost_per_tap","table_rows":1500},{"column":"cost_per_conversion","table_rows":1500}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"platform","value":"APPLE_SEARCH_ADS"},{"column":"_dbt_loaded_at","value":"2026-10-25 01:52:29.21054+08"}]</code> |
| B5_null_literal_output | <code>3输出列；[{"column":"calculated_tap_through_rate","expression":["CAST(CAST(NULL AS DOUBLE) AS DOUBLE)"]},{"column":"cost_per_tap","expression":["CAST(CAST(NULL AS DOUBLE) AS DOUBLE)"]},{"column":"cost_per_conversion","expression":["CAST(CAST(NULL AS DOUBLE) AS DOUBLE)"]}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"platform","expression":["'APPLE_SEARCH_ADS'"]}]</code> |
| C9_agent_runtime_text | <code>S4:30 CURRENT_TIMESTAMP；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:23 CURRENT_DATE；命中数=2</code> |
| C9_contract_runtime_text | <code>S3:372 CURRENT_DATE；命中数=2</code> |

## 轨迹索引（不放输出原文）

本题事件总数：99；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort &amp;&amp; cat config/layer_dependencies.yaml</code> | 7365 | true | false |
| 11 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting_start.duckdb',read_only=True)<br>print(c.execute('show all tables').fetchall()[:100])<br>PY</code> | 52227 | false | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('ad_reporting_start.yaml'))<br>print(type(x), x.keys())<br>print(str(x)[:2500])<br>PY</code> | 7232 | false | false |
| 17 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting_start.duckdb',read_only=True)<br>for r in c.execute("select table_name from information_schema.tables where table_schema='raw' order by 1").fe</code> | 26086 | false | false |
| 19 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml,duckdb,os,re<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))<br>con=duckdb.connect('ad_reporting_start.duckdb',r</code> | 528 | false | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>p='/tmp/gen.py'<br>s=open(p).read();s=s.replace("if suffix.startswith('amazon_ads__'): return source['amazon_ads'+suffix[len('amazon_ads'):]]", "if suffix.startswith('amazon_ads__'): retu</code> | 0 | false | false |
| 37 | run | <code>python run.py &gt; /tmp/runlog3 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog3;</code> | 6937 | true | false |
| 81 | run | <code>find sql -type f &#124; wc -l; grep -R ';' sql --include='*.sql' &#124; head; git status --short 2&gt;/dev/null &#124;&#124; true; python - &lt;&lt;'PY'<br>import yaml,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c[</code> | 999 | true | false |
| 85 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>c=yaml.safe_load(open('docs/data_contract.yaml')); d=duckdb.connect('ad_reporting.duckdb',read_only=True)<br>for layer,key in [('staging','staging_contract'),('intermed</code> | 776 | true | false |

### agent action 的 thought/message 命中原句

event 21 / message

```text
s=s.replace("if suffix.startswith('apple_search_ads__'): return source[suffix.replace('apple_search_ads__','apple_search_ads__',1)]", "if suffix.startswith('apple_search_ads__'): return {'stg_apple_search_ads__ad_group_report':'apple_search_ad_group_report_data','stg_apple_search_ads__ad_report':'apple_search_ad_report_data','stg_apple_search_ads__campaign_report':'apple_search_campaign_report_data'}[name]")
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-006.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_stg_apple_search_ads__ad_group_report/020_impl-006_stg_apple_search_ads__ad_group_report.json`
- S11: `data/011_agent_alignment/impl-006_attempt_01/stg_apple_search_ads__ad_group_report_2025-10-12.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
