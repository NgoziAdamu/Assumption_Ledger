# impl-006 | staging | stg_facebook_ads__ad_report | 差异：S1；日期 2025-10-12

## 契约完整原文

S3:648–698

```yaml
    - name: "stg_facebook_ads__ad_report"
      description: "Staging table for Facebook Ads  Ad Report"
      columns:
        - name: "platform"
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "UPPER(platform) = 'FACEBOOK_ADS'"
              on_failure: delete_row
        - name: "ad_id"
          data_type: VARCHAR
          constraints: [not_null]
        - name: "date_day"
          data_type: DATE
          constraints: [not_null]
          validation_rules:
            - rule: "date_day IS NOT NULL AND date_day >= '2020-01-01' AND date_day <= CURRENT_DATE"
              on_failure: delete_row
            - rule: "date_day NOT IN ('1970-01-01','1900-01-01','9999-12-31')"
              on_failure: delete_row
        - name: "account_id"
          data_type: VARCHAR
        - name: "impressions"
          data_type: INTEGER
          validation_rules:
            - rule: "impressions >= 0"
              on_failure: correct
        - name: "inline_link_clicks"
          data_type: INTEGER
          validation_rules:
            - rule: "inline_link_clicks >= 0"
              on_failure: correct
        - name: "spend"
          data_type: DECIMAL(18,2)
          validation_rules:
            - rule: "spend >= 0 AND spend <= 999999999999.99"
              on_failure: correct
            - rule: "spend = ROUND(spend, 2)"
              on_failure: correct
        - name: "click_through_rate"
          data_type: INTEGER
        - name: "cost_per_click"
          data_type: INTEGER
        - name: "cost_per_thousand_impressions"
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
    SELECT * FROM raw.facebook_ads_basic_ad_data
),
cleaned AS (
    SELECT
        'FACEBOOK_ADS' AS platform,
        CAST(TRY_CAST("ad_id" AS VARCHAR) AS VARCHAR) AS ad_id,
        CAST(TRY_CAST(date AS DATE) AS DATE) AS date_day,
        TRY_CAST("account_id" AS VARCHAR) AS account_id,
        CAST(TRY_CAST("impressions" AS BIGINT) AS INTEGER) AS impressions,
        TRY_CAST("inline_link_clicks" AS INTEGER) AS inline_link_clicks,
        CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend,
        CAST(NULL::INTEGER AS INTEGER) AS click_through_rate,
        CAST(NULL::INTEGER AS INTEGER) AS cost_per_click,
        CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions,
        CURRENT_TIMESTAMP AS _dbt_loaded_at
    FROM source_rows
)
SELECT * FROM cleaned
```

## gold SQL（仅供定位差异）

S5

```sql
-- Facebook Ads Ad Report Staging Model
-- Standardizes raw Facebook Ads ad-level data for downstream consumption
-- Removes Fivetran-specific logic and converts to DuckDB-compatible SQL
-- Includes data quality validation rules per staging_data_specification.yaml

SELECT
    -- Platform Identifier (Rule 1: Platform name standardization)
    UPPER(TRIM('facebook_ads')) AS platform,

    -- Primary Keys (with validation rules)
    CAST(TRIM(CAST(ad_id AS VARCHAR)) AS VARCHAR) AS ad_id,

    CAST(
        CASE
            WHEN date IS NULL THEN NULL
            WHEN CAST(date AS DATE) < '2020-01-01' OR CAST(date AS DATE) > CURRENT_DATE THEN NULL
            WHEN CAST(date AS DATE) IN ('1970-01-01', '1900-01-01', '9999-12-31') THEN NULL
            ELSE date
        END AS DATE
    ) AS date_day,

    -- Hierarchy References
    CAST(TRIM(CAST(account_id AS VARCHAR)) AS VARCHAR) AS account_id,

    -- Performance Metrics (Rule 3: Negative impressions correction)
    CAST(
        CASE
            WHEN impressions < 0 THEN 0
            WHEN impressions IS NULL THEN 0
            ELSE impressions
        END AS INTEGER
    ) AS impressions,

    -- inline_link_clicks needs fixing based on data type issue - default to INTERGER per spec
    CAST(
        CASE
            WHEN CAST(inline_link_clicks AS VARCHAR) = '' OR inline_link_clicks IS NULL THEN 0
            WHEN CAST(inline_link_clicks AS INTEGER) < 0 THEN 0
            ELSE CAST(inline_link_clicks AS INTEGER)
        END AS INTEGER
    ) AS inline_link_clicks,

    -- Cost Metrics (Rule 5: Cost validation)
    CAST(
        ROUND(
            CASE
                WHEN spend IS NULL THEN 0.0
                WHEN spend < 0 THEN 0.0
                WHEN spend > 999999999999.99 THEN 999999999999.99
                ELSE spend
            END, 2
        ) AS DECIMAL(18,2)
    ) AS spend,

    -- Calculated Metrics (Rule 4&10: CTR validation bounds - fixed from 0 to proper calculation)
    CAST(
        CASE
            WHEN impressions IS NULL OR impressions <= 0 THEN 0
            WHEN inline_link_clicks IS NULL OR inline_link_clicks < 0 THEN 0
            ELSE ROUND((CAST(inline_link_clicks AS DECIMAL) / CAST(impressions AS DECIMAL)) * 100, 4)
        END AS INTEGER  -- Spec requirement
    ) AS click_through_rate,

    CAST(
        CASE
            WHEN inline_link_clicks IS NULL OR inline_link_clicks <= 0 THEN 0
            WHEN spend IS NULL OR spend < 0 THEN 0
            ELSE ROUND(
                ROUND(
                    CASE
                        WHEN spend IS NULL THEN 0.0
                        WHEN spend > 999999999999.99 THEN 999999999999.99
                        ELSE spend
                    END, 2
                ) / inline_link_clicks, 2
            )
        END AS INTEGER  -- Spec requirement
    ) AS cost_per_click,

    CAST(
        CASE
            WHEN impressions IS NULL OR impressions <= 0 THEN 0.0
            WHEN spend IS NULL OR spend < 0 THEN 0.0
            ELSE ROUND(
                ROUND(
                    CASE
                        WHEN spend IS NULL THEN 0.0
                        WHEN spend > 999999999999.99 THEN 999999999999.99
                        ELSE spend
                    END, 2
                ) / CAST(impressions AS DECIMAL) * 1000.0, 2
            )
        END AS DOUBLE  -- Fixed data type per spec
    ) AS cost_per_thousand_impressions,

    -- Data Quality (corrected datatype)
    CAST(CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE) AS _dbt_loaded_at

FROM raw.facebook_ads_basic_ad_data

WHERE date IS NOT NULL
    AND ad_id IS NOT NULL
    -- Apply validation as per YAML specification
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1000 | 1000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"ad_id":"1022412906784"}</code> |
| K2 | <code>{"ad_id":"1029119952816"}</code> |
| K3 | <code>{"ad_id":"1041423847830"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| ad_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| click_through_rate | 1000 | 1000 | 1000 | INTEGER | INTEGER |
| cost_per_click | 1000 | 1000 | 1000 | INTEGER | INTEGER |
| cost_per_thousand_impressions | 1000 | 1000 | 1000 | DOUBLE | DOUBLE |
| date_day | 0 | 0 | 0 | DATE | DATE |
| impressions | 0 | 0 | 0 | INTEGER | INTEGER |
| inline_link_clicks | 0 | 0 | 0 | INTEGER | INTEGER |
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| spend | 1000 | 1000 | 1000 | DECIMAL(18,2) | DECIMAL(18,2) |

click_through_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 9 |
| K3 | null | 7 |

cost_per_click 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 9 |
| K2 | null | 4 |
| K3 | null | 5 |

cost_per_thousand_impressions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 21.4 |
| K2 | null | 379.96 |
| K3 | null | 384.08 |

spend 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 9.18 |
| K2 | null | 1287.68 |
| K3 | null | 239.28 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>4列；[{"column":"spend","table_rows":1000},{"column":"click_through_rate","table_rows":1000},{"column":"cost_per_click","table_rows":1000}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"platform","value":"FACEBOOK_ADS"},{"column":"_dbt_loaded_at","value":"2026-10-25 01:52:29.231412+08"}]</code> |
| B5_null_literal_output | <code>4输出列；[{"column":"spend","expression":["CAST(CAST(NULL AS DECIMAL(18, 2)) AS DECIMAL(18, 2))"]},{"column":"click_through_rate","expression":["CAST(CAST(NULL AS INT) AS INT)"]},{"column":"cost_per_click","expression":["CAST(CAST(NULL AS INT) AS INT)"]}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"platform","expression":["'FACEBOOK_ADS'"]}]</code> |
| C9_agent_runtime_text | <code>S4:16 CURRENT_TIMESTAMP；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:16 CURRENT_DATE；命中数=2</code> |
| C9_contract_runtime_text | <code>S3:664 CURRENT_DATE；命中数=2</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；task_instruction_not_agent_report  - Facebook Ads (staging.stg_facebook_ads__ad_report): - Map fields: platform=''facebook_ads''; campaign_id from ad_id; campaign_type=''FACEBOOK_FEED''; daily_budget NULL; currency=''USD''; clicks from inline_link_clicks defaulting to 0; impressions defaulting to 0; cost from spend defaulting to 0; revenue_7d=0; revenue_30d=0; conversions=0; conversion_type=''ENGAGEMENT''.</code> |

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
| 37 | run | <code>python run.py &gt; /tmp/runlog3 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog3;</code> | 6937 | true | false |
| 43 | run | <code>cat &gt; sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql &lt;&lt;'SQL'<br>WITH execution_clock AS (<br>    SELECT CURRENT_TIMESTAMP AS processed_at<br>),<br>amazon_rows AS (<br>    SELECT<br>        'amazon_ads'</code> | 0 | false | false |
| 81 | run | <code>find sql -type f &#124; wc -l; grep -R ';' sql --include='*.sql' &#124; head; git status --short 2&gt;/dev/null &#124;&#124; true; python - &lt;&lt;'PY'<br>import yaml,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c[</code> | 999 | true | false |
| 85 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>c=yaml.safe_load(open('docs/data_contract.yaml')); d=duckdb.connect('ad_reporting.duckdb',read_only=True)<br>for layer,key in [('staging','staging_contract'),('intermed</code> | 776 | true | false |

### agent action 的 thought/message 命中原句

event 43 / message

```text
    FROM staging.stg_facebook_ads__ad_report
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-006.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_report.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_stg_facebook_ads__ad_report/020_impl-006_stg_facebook_ads__ad_report.json`
- S11: `data/011_agent_alignment/impl-006_attempt_01/stg_facebook_ads__ad_report_2025-10-12.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
