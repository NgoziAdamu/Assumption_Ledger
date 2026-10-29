# impl-006 | staging | stg_amazon_ads__ad_group_report | 差异：S1；日期 2025-10-12

## 契约完整原文

S3:70–111

```yaml
    - name: "stg_amazon_ads__ad_group_report"
      description: "Staging table for Amazon Ads  Ad Group Report"
      columns:
        - name: "platform"
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "UPPER(platform) IN ('AMAZON_ADS','GOOGLE_ADS','FACEBOOK_ADS','MICROSOFT_ADS','LINKEDIN_ADS','APPLE_SEARCH_ADS','PINTEREST_ADS','REDDIT_ADS','SNAPCHAT_ADS','TIKTOK_ADS','TWITTER_ADS')"
              on_failure: delete_row
        - name: "ad_group_id"
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "ad_group_id IS NOT NULL AND TRIM(ad_group_id) != ''"
              on_failure: delete_row
            - rule: "REGEXP_LIKE(ad_group_id, '^[A-Za-z0-9_-]{1,128}$')"
              on_failure: delete_row
        - name: "date_day"
          data_type: DATE
          validation_rules:
            - rule: "date_day IS NULL OR (date_day >= '2020-01-01' AND date_day <= CURRENT_DATE)"
              on_failure: nullify_field
            - rule: "date_day IS NULL OR date_day NOT IN ('1970-01-01','1900-01-01','9999-12-31')"
              on_failure: nullify_field
        - name: "campaign_bidding_strategy"
          data_type: VARCHAR
        - name: "clicks"
          data_type: INTEGER
        - name: "cost"
          data_type: DECIMAL(18,2)
        - name: "impressions"
          data_type: INTEGER
        - name: "click_through_rate"
          data_type: DOUBLE
        - name: "cost_per_click"
          data_type: DOUBLE
        - name: "_dbt_loaded_at"
          data_type: TIMESTAMP WITH TIME ZONE
          constraints: [not_null]
          validation_rules:
            - rule: "_dbt_loaded_at IS NOT NULL AND _dbt_loaded_at <= CURRENT_TIMESTAMP"
              on_failure: delete_row
```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT * FROM raw.amazon_ads_ad_group_level_report_data
),
cleaned AS (
    SELECT
        'AMAZON_ADS' AS platform,
        CAST(TRY_CAST("ad_group_id" AS VARCHAR) AS VARCHAR) AS ad_group_id,
        CAST(TRY_CAST(date AS DATE) AS DATE) AS date_day,
        TRY_CAST("campaign_bidding_strategy" AS VARCHAR) AS campaign_bidding_strategy,
        CAST(TRY_CAST("clicks" AS BIGINT) AS INTEGER) AS clicks,
        CAST(ROUND(TRY_CAST("cost" AS DOUBLE), 2) AS DECIMAL(18,2)) AS cost,
        CAST(TRY_CAST("impressions" AS BIGINT) AS INTEGER) AS impressions,
        CAST(NULL::DOUBLE AS DOUBLE) AS click_through_rate,
        CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_click,
        CURRENT_TIMESTAMP AS _dbt_loaded_at
    FROM source_rows
)
SELECT * FROM cleaned
```

## gold SQL（仅供定位差异）

S5

```sql
-- Amazon Ads Ad Group Report Staging Model
-- Standardizes raw Amazon Ads ad group-level data for downstream consumption
-- Removes Fivetran-specific logic and converts to DuckDB-compatible SQL
-- Includes data quality validation rules per staging_data_specification.yaml

SELECT
    -- Platform Identifier (Rule 1: Platform name standardization)
    UPPER(TRIM('amazon_ads')) AS platform,

    -- Primary Keys (with data quality validation)
    CAST(
        CASE
            WHEN TRIM(CAST(ad_group_id AS VARCHAR)) = '' OR ad_group_id IS NULL THEN NULL
            WHEN NOT regexp_matches(TRIM(CAST(ad_group_id AS VARCHAR)), '^[A-Za-z0-9_-]{1,128}$') THEN NULL
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

    -- Ad Group Attributes
    CAST(
        CASE
            WHEN LOWER(TRIM(campaign_bidding_strategy)) IN (
                'advanced cpc', 'enhanced cpc', 'manual cpc', 'manual cpm',
                'target impression share bids', 'maximize conversions',
                'maximize conversion value', 'target cpa', 'target roas',
                'viewable cpm', 'target cpm', 'commission', 'percent cpc'
            ) THEN UPPER(TRIM(campaign_bidding_strategy))
            ELSE NULL
        END AS VARCHAR
    ) AS campaign_bidding_strategy,

    -- Performance Metrics (Rule 3: Negative clicks correction)
    CAST(
        CASE
            WHEN clicks < 0 THEN 0
            ELSE clicks
        END AS INTEGER
    ) AS clicks,

    CAST(
        -- Rule 5: Cost decimal rounding
        ROUND(
            CASE
                WHEN cost IS NULL THEN 0.0
                WHEN cost < 0 THEN 0.0
                ELSE cost
            END, 2
        ) AS DECIMAL(18,2)
    ) AS cost,

    CAST(impressions AS INTEGER) AS impressions,

    -- Calculated Metrics (Rule 4: Click-through rate consistency check)
    CAST(
        CASE
            WHEN impressions IS NULL OR impressions < 0 THEN 0.0
            WHEN clicks IS NULL OR clicks < 0 THEN 0.0
            WHEN impressions > 0 THEN ROUND((CAST(clicks AS DECIMAL) / CAST(impressions AS DECIMAL)) * 100, 4)
            ELSE 0.0
        END AS DOUBLE
    ) AS click_through_rate,

    CAST(
        CASE
            WHEN clicks IS NULL OR clicks <= 0 THEN 0.0
            ELSE ROUND(
                -- Rule 5: Cost decimal rounding
                ROUND(
                    CASE
                        WHEN cost IS NULL THEN 0.0
                        WHEN cost < 0 THEN 0.0
                        ELSE cost
                    END, 2
                ) / clicks, 2
            )
        END AS DOUBLE
    ) AS cost_per_click,

    -- Data Quality (with constraint validation)
    CAST(CURRENT_TIMESTAMP AS TIMESTAMP WITH TIME ZONE) AS _dbt_loaded_at

FROM raw.amazon_ads_ad_group_level_report_data

WHERE date IS NOT NULL
    AND ad_group_id IS NOT NULL
    -- Apply Rule 6: Delete rows with NULL platform values (handled by select)
    -- Apply Rule 7: Invalid ad_group_id pattern (handled by casting logic above)
    -- Apply Rule 8: Future date validation (handled by date_day casting logic above)
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 17868 | 17868 | 8 | 1 | 631 | 624 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"ad_group_id":"ama01046148963","date_day":"2021-01-01"}</code> |
| K2 | <code>{"ad_group_id":"ama01046148963","date_day":"2021-01-10"}</code> |
| K3 | <code>{"ad_group_id":"ama01046148963","date_day":"2021-02-07"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| ad_group_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_bidding_strategy | 17852 | 17852 | 17852 | VARCHAR | VARCHAR |
| click_through_rate | 17852 | 17852 | 17852 | DOUBLE | DOUBLE |
| clicks | 0 | 0 | 0 | INTEGER | INTEGER |
| cost | 0 | 0 | 0 | DECIMAL(18,2) | DECIMAL(18,2) |
| cost_per_click | 17852 | 17852 | 17852 | DOUBLE | DOUBLE |
| impressions | 0 | 0 | 0 | INTEGER | INTEGER |
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |

campaign_bidding_strategy 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | AUTO_FOR_SALES | null |
| K2 | LEGACY_FOR_SALES | null |
| K3 | LEGACY_FOR_SALES | null |

click_through_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 4.2188 |
| K2 | null | 4.5333 |
| K3 | null | 6.0046 |

cost_per_click 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 3.11 |
| K2 | null | 4.11 |
| K3 | null | 1.37 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"ad_group_id":"","date_day":"2023-01-01"},{"ad_group_id":"AMA 12345678","date_day":"2023-01-01"},{"ad_group_id":"AMA#12345678","date_day":"2023-01-01"},{"ad_group_id":"AMA123-456/789","date_day":"2023-01-01"},{"ad_group_id":"AMA12345678!@#$","date_day":"2023-01-01"}]</code> | <code>[{"ad_group_id":null,"date_day":"2023-01-01"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>2列；[{"column":"click_through_rate","table_rows":17868},{"column":"cost_per_click","table_rows":17868}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"platform","value":"AMAZON_ADS"},{"column":"_dbt_loaded_at","value":"2026-10-25 01:52:29.149313+08"}]</code> |
| B5_null_literal_output | <code>2输出列；[{"column":"click_through_rate","expression":["CAST(CAST(NULL AS DOUBLE) AS DOUBLE)"]},{"column":"cost_per_click","expression":["CAST(CAST(NULL AS DOUBLE) AS DOUBLE)"]}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"platform","expression":["'AMAZON_ADS'"]}]</code> |
| C9_agent_runtime_text | <code>S4:15 CURRENT_TIMESTAMP；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:22 CURRENT_DATE；命中数=2</code> |
| C9_contract_runtime_text | <code>S3:90 CURRENT_DATE；命中数=2</code> |

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
s=open(p).read();s=s.replace("if suffix.startswith('amazon_ads__'): return source['amazon_ads'+suffix[len('amazon_ads'):]]", "if suffix.startswith('amazon_ads__'): return {'stg_amazon_ads__ad_group_report':'amazon_ads_ad_group_level_report_data','stg_amazon_ads__campaign_report':'amazon_ads_campaign_level_report_data','stg_amazon_ads__keyword_report':'amazon_ads_targeting_keyword_report_data','stg_amazon_ads__product_report':'amazon_ads_advertised_product_report_data','stg_amazon_ads__search_report':'amazon_ads_search_term_ad_keyword_report_data'}[name]")
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-006.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__ad_group_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_amazon_ads__ad_group_report.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_stg_amazon_ads__ad_group_report/020_impl-006_stg_amazon_ads__ad_group_report.json`
- S11: `data/011_agent_alignment/impl-006_attempt_01/stg_amazon_ads__ad_group_report_2025-10-12.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
