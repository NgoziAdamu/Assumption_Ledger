# impl-006 | staging | stg_google_ads__campaign_report | 差异：S1；日期 原记录

## 契约完整原文

S3:770–796

```yaml
    - name: "stg_google_ads__campaign_report"
      description: "Staging table for Google Ads  Campaign Report"
      columns:
        - name: "source_relation"
          data_type: VARCHAR
        - name: "account_id"
          data_type: VARCHAR(20)
        - name: "date_day"
          data_type: DATE
        - name: "campaign_id"
          data_type: VARCHAR(20)
        - name: "ad_network_type"
          data_type: VARCHAR(20)
        - name: "device"
          data_type: VARCHAR(20)
        - name: "clicks"
          data_type: BIGINT
        - name: "spend"
          data_type: DECIMAL(18,2)
        - name: "impressions"
          data_type: BIGINT
        - name: "conversions"
          data_type: DECIMAL(10,2)
        - name: "conversions_value"
          data_type: DECIMAL(15,2)
        - name: "view_through_conversions"
          data_type: BIGINT
```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT * FROM raw.google_ads_campaign_stats_data
),
cleaned AS (
    SELECT
        'google_ads' AS source_relation,
        TRY_CAST("customer_id" AS VARCHAR(20)) AS account_id,
        CAST(TRY_CAST(date AS DATE) AS DATE) AS date_day,
        CAST(NULL::VARCHAR(20) AS VARCHAR(20)) AS campaign_id,
        TRY_CAST("ad_network_type" AS VARCHAR(20)) AS ad_network_type,
        TRY_CAST("device" AS VARCHAR(20)) AS device,
        CAST(TRY_CAST("clicks" AS BIGINT) AS BIGINT) AS clicks,
        CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend,
        CAST(TRY_CAST("impressions" AS BIGINT) AS BIGINT) AS impressions,
        CAST(TRY_CAST("conversions" AS BIGINT) AS DECIMAL(10,2)) AS conversions,
        TRY_CAST("conversions_value" AS DECIMAL(15,2)) AS conversions_value,
        TRY_CAST("view_through_conversions" AS BIGINT) AS view_through_conversions
    FROM source_rows
)
SELECT * FROM cleaned
```

## gold SQL（仅供定位差异）

S5

```sql
-- stg_google_ads__campaign_stats
-- Cleaned and validated daily campaign performance metrics with computed cost conversions (Updated to match YAML spec)
-- Transform raw Google Ads data into clean staging table per YAML specification
-- DEPRECATED: Use stg_google_ads__campaign_stats.sql instead for pure YAML compliance

SELECT
    -- Source relation for multi-account setups
    'google_ads' AS source_relation,

    -- Account identification - updated to use account_id instead of customer_id
    CAST(customer_id AS VARCHAR(20)) AS account_id,
    CAST(date AS DATE) AS date_day,

    -- Campaign identification - updated to use campaign_id directly
    CAST(id AS VARCHAR(20)) AS campaign_id,

    -- Performance attributes
    CAST(ad_network_type AS VARCHAR(20)) AS ad_network_type,
    CAST(device AS VARCHAR(20)) AS device,

    -- Performance metrics - updated to use spend instead of cost
    CAST(clicks AS BIGINT) AS clicks,
    ROUND(cost_micros / 1000000.0, 2) AS spend,
    CAST(impressions AS BIGINT) AS impressions,

    -- Handle conversions data quality issues
    CASE
        WHEN conversions = true THEN 1.0
        WHEN conversions = false THEN 0.0
        ELSE CAST(conversions AS DECIMAL(10,2))
    END AS conversions,

    -- Handle conversions_value data quality issues
    CASE
        WHEN conversions_value = true THEN 1.0
        WHEN conversions_value = false THEN 0.0
        ELSE CAST(conversions_value AS DECIMAL(15,2))
    END AS conversions_value,

    -- Handle view_through_conversions data quality issues
    CASE
        WHEN view_through_conversions = true THEN 1
        WHEN view_through_conversions = false THEN 0
        ELSE CAST(view_through_conversions AS BIGINT)
    END AS view_through_conversions

FROM raw.google_ads_campaign_stats_data

WHERE date IS NOT NULL
    AND customer_id IS NOT NULL
    AND id IS NOT NULL
    -- Validation rule: date should not be in the future
    AND CAST(date AS DATE) <= CURRENT_DATE
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 26031 | 26031 | 24558 | 25856 | 1412 | 174 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| date_day | 0 | 0 | 0 | DATE | DATE |
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| ad_network_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| device | 0 | 0 | 0 | VARCHAR | VARCHAR |
| clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| spend | 0 | 0 | 0 | DECIMAL(18,2) | DOUBLE |
| impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| conversions | 0 | 0 | 0 | DECIMAL(10,2) | DECIMAL(10,2) |
| conversions_value | 0 | 0 | 0 | DECIMAL(15,2) | DECIMAL(15,2) |
| view_through_conversions | 0 | 0 | 0 | BIGINT | BIGINT |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"account_id":"GOO15831825243","date_day":"2021-01-05","campaign_id":null,"ad_network_type":"YOUTUBE_SEARCH","device":"TABLET"},{"account_id":"GOO15831825243","date_day":"2021-01-07","campaign_id":null,"ad_network_type":"CONTENT","device":"TABLET"},{"account_id":"GOO15831825243","date_day":"2021-01-09","campaign_id":null,"ad_network_type":"SEARCH","device":"MOBILE"},{"account_id":"GOO15831825243","date_day":"2021-01-12","campaign_id":null,"ad_network_type":"CONTENT","device":"DESKTOP"},{"account_id":"GOO15831825243","date_day":"2021-01-12","campaign_id":null,"ad_network_type":"CONTENT","device":"TABLET"}]</code> | <code>[{"account_id":"GOO15831825243","date_day":"2021-01-05","campaign_id":"GOO14877125929","ad_network_type":"YOUTUBE_SEARCH","device":"TABLET"},{"account_id":"GOO15831825243","date_day":"2021-01-05","campaign_id":"GOO77097240371","ad_network_type":"YOUTUBE_SEARCH","device":"TABLET"},{"account_id":"GOO15831825243","date_day":"2021-01-07","campaign_id":"GOO63702652859","ad_network_type":"CONTENT","device":"TABLET"},{"account_id":"GOO15831825243","date_day":"2021-01-09","campaign_id":"GOO31187670443","ad_network_type":"SEARCH","device":"MOBILE"},{"account_id":"GOO15831825243","date_day":"2021-01-12","campaign_id":"GOO42878105509","ad_network_type":"CONTENT","device":"TABLET"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>2列；[{"column":"campaign_id","table_rows":26031},{"column":"spend","table_rows":26031}]</code> |
| A3_constant_nonnull_column | <code>1列；[{"column":"source_relation","value":"google_ads"}]</code> |
| B5_null_literal_output | <code>2输出列；[{"column":"campaign_id","expression":["CAST(CAST(NULL AS TEXT) AS TEXT)"]},{"column":"spend","expression":["CAST(CAST(NULL AS DECIMAL(18, 2)) AS DECIMAL(18, 2))"]}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"source_relation","expression":["'google_ads'"]}]</code> |
| B8_shared_single_source | <code>唯一源=raw.google_ads_campaign_stats_data；目标数=2；例=["staging.stg_google_ads__campaign_report","staging.stg_google_ads__campaign_stats"]</code> |
| C9_gold_runtime_text | <code>S5:53 CURRENT_DATE；命中数=1</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；task_instruction_not_agent_report  - Google Ads (staging.stg_google_ads__campaign_report): - Map fields: platform=''google_ads''; campaign_type from ad_network_type with default ''SEARCH''; daily_budget NULL; currency=''USD''; cost from spend; revenue_7d and revenue_30d both from conversions_value; conversions from conversions; conversion_type=''ONLINE_CONVERSION''.</code> |

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
| 29 | run | <code>python run.py &gt; /tmp/runlog2 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete&#124;ERROR - Failed&#124;Binder Error&#124;Catalog Error' /tmp/runlog2</code> | 1956 | true | false |
| 33 | run | <code>grep -n 'FROM\&#124;JOIN' sql/intermediate/int_ad_reporting__time_series_analytics.sql sql/marts/ad_reporting__predictive_analytics.sql</code> | 466 | true | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> # only raw source casts rather than casts of computed values; make raw conversions tole</code> | 0 | false | false |
| 37 | run | <code>python run.py &gt; /tmp/runlog3 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog3;</code> | 6937 | true | false |
| 43 | run | <code>cat &gt; sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql &lt;&lt;'SQL'<br>WITH execution_clock AS (<br>    SELECT CURRENT_TIMESTAMP AS processed_at<br>),<br>amazon_rows AS (<br>    SELECT<br>        'amazon_ads'</code> | 0 | false | false |
| 81 | run | <code>find sql -type f &#124; wc -l; grep -R ';' sql --include='*.sql' &#124; head; git status --short 2&gt;/dev/null &#124;&#124; true; python - &lt;&lt;'PY'<br>import yaml,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c[</code> | 999 | true | false |
| 85 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>c=yaml.safe_load(open('docs/data_contract.yaml')); d=duckdb.connect('ad_reporting.duckdb',read_only=True)<br>for layer,key in [('staging','staging_contract'),('intermed</code> | 776 | true | false |

### agent action 的 thought/message 命中原句

event 35 / message

```text
 s=re.sub(r'FROM (staging\.stg_google_ads__campaign_report) \([^\)]*\)',r'FROM \1',s)
```
event 43 / message

```text
    FROM staging.stg_google_ads__campaign_report
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-006.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_google_ads__campaign_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_google_ads__campaign_report.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_stg_google_ads__campaign_report/020_impl-006_stg_google_ads__campaign_report.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
