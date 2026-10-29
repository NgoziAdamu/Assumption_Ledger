# impl-006 | staging | stg_microsoft_ads__campaign_report | 差异：S1；日期 2025-10-12

## 契约完整原文

S3:1002–1046

```yaml
    - name: "stg_microsoft_ads__campaign_report"
      description: "Staging table for Microsoft Ads  Campaign Report"
      columns:
        - name: "platform"
          data_type: VARCHAR
        - name: "campaign_id"
          data_type: VARCHAR
        - name: "date_day"
          data_type: DATE
        - name: "account_id"
          data_type: VARCHAR
        - name: "device_os"
          data_type: VARCHAR
        - name: "device_type"
          data_type: VARCHAR
        - name: "network"
          data_type: VARCHAR
        - name: "clicks"
          data_type: INTEGER
        - name: "impressions"
          data_type: INTEGER
        - name: "spend"
          data_type: DECIMAL(18,2)
        - name: "conversions"
          data_type: INTEGER
        - name: "revenue"
          data_type: DECIMAL(18,2)
        - name: "assists"
          data_type: INTEGER
        - name: "bounce_rate"
          data_type: DECIMAL(8,4)
        - name: "average_position"
          data_type: DECIMAL(8,2)
        - name: "click_through_rate"
          data_type: DOUBLE
        - name: "cost_per_click"
          data_type: DOUBLE
        - name: "cost_per_thousand_impressions"
          data_type: DOUBLE
        - name: "cost_per_conversion"
          data_type: DOUBLE
        - name: "return_on_ad_spend"
          data_type: DOUBLE
        - name: "_dbt_loaded_at"
          data_type: TIMESTAMP WITH TIME ZONE
```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT * FROM raw.microsoft_ads_campaign_performance_daily_report_data
),
cleaned AS (
    SELECT
        'MICROSOFT_ADS' AS platform,
        CAST(TRY_CAST("campaign_id" AS VARCHAR) AS VARCHAR) AS campaign_id,
        CAST(TRY_CAST(date AS DATE) AS DATE) AS date_day,
        TRY_CAST("account_id" AS VARCHAR) AS account_id,
        TRY_CAST("device_os" AS VARCHAR) AS device_os,
        TRY_CAST("device_type" AS VARCHAR) AS device_type,
        TRY_CAST("network" AS VARCHAR) AS network,
        CAST(TRY_CAST("clicks" AS BIGINT) AS INTEGER) AS clicks,
        CAST(TRY_CAST("impressions" AS BIGINT) AS INTEGER) AS impressions,
        CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend,
        CAST(TRY_CAST("conversions" AS BIGINT) AS INTEGER) AS conversions,
        TRY_CAST("revenue" AS DECIMAL(18,2)) AS revenue,
        CAST(NULL::INTEGER AS INTEGER) AS assists,
        CAST(NULL::DECIMAL(8,4) AS DECIMAL(8,4)) AS bounce_rate,
        CAST(NULL::DECIMAL(8,2) AS DECIMAL(8,2)) AS average_position,
        CAST(NULL::DOUBLE AS DOUBLE) AS click_through_rate,
        CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_click,
        CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions,
        CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_conversion,
        CAST(NULL::DOUBLE AS DOUBLE) AS return_on_ad_spend,
        CURRENT_TIMESTAMP AS _dbt_loaded_at
    FROM source_rows
)
SELECT * FROM cleaned
```

## gold SQL（仅供定位差异）

S5

```sql
-- Microsoft Ads Campaign Report Staging Model
-- Standardizes raw Microsoft Ads campaign-level data for downstream consumption
-- Removes Fivetran-specific logic and converts to DuckDB-compatible SQL

SELECT 
    -- Platform Identifier
    'microsoft_ads' AS platform,
    
    -- Primary Keys
    CAST(campaign_id AS VARCHAR) AS campaign_id,
    CAST(date AS DATE) AS date_day,
    
    -- Campaign Attributes
    CAST(account_id AS VARCHAR) AS account_id,
    CAST(device_os AS VARCHAR) AS device_os,
    CAST(device_type AS VARCHAR) AS device_type,
    CAST(network AS VARCHAR) AS network,
    
    -- Performance Metrics
    CAST(clicks AS INTEGER) AS clicks,
    CAST(impressions AS INTEGER) AS impressions,
    CAST(spend AS DECIMAL(18,2)) AS spend,
    
    -- Conversion Metrics
    CAST(COALESCE(conversions, '0') AS INTEGER) AS conversions,
    CAST(COALESCE(revenue, '0') AS DECIMAL(18,2)) AS revenue,
    
    -- Microsoft-specific Metrics (using available columns)
    CAST(0 AS INTEGER) AS assists,
    CAST(0 AS DECIMAL(8,4)) AS bounce_rate,
    CAST(0 AS DECIMAL(8,2)) AS average_position,
    
    -- Calculated Metrics
    CASE 
        WHEN impressions > 0 THEN ROUND((CAST(clicks AS DECIMAL) / CAST(impressions AS DECIMAL)) * 100, 4)
        ELSE 0 
    END AS click_through_rate,
    
    CASE 
        WHEN clicks > 0 THEN ROUND(spend / clicks, 2)
        ELSE 0 
    END AS cost_per_click,
    
    CASE 
        WHEN impressions > 0 THEN ROUND((spend / impressions) * 1000, 2)
        ELSE 0 
    END AS cost_per_thousand_impressions,
    
    CASE 
        WHEN conversions > 0 THEN ROUND(spend / conversions, 2)
        ELSE 0 
    END AS cost_per_conversion,
    
    CASE 
        WHEN spend > 0 THEN ROUND(CAST(COALESCE(revenue, '0') AS DECIMAL(18,2)) / spend, 4)
        ELSE 0 
    END AS return_on_ad_spend,
    
    -- Data Quality
    CURRENT_TIMESTAMP AS _dbt_loaded_at

FROM raw.microsoft_ads_campaign_performance_daily_report_data

WHERE date IS NOT NULL
    AND campaign_id IS NOT NULL
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1500 | 1500 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"campaign_id":"ms01000898931"}</code> |
| K2 | <code>{"campaign_id":"ms01007692841"}</code> |
| K3 | <code>{"campaign_id":"ms01036202291"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| assists | 1500 | 1500 | 1500 | INTEGER | INTEGER |
| average_position | 1500 | 1500 | 1500 | DECIMAL(8,2) | DECIMAL(8,2) |
| bounce_rate | 1500 | 1500 | 1500 | DECIMAL(8,4) | DECIMAL(8,4) |
| click_through_rate | 1500 | 1500 | 1500 | DOUBLE | DOUBLE |
| clicks | 0 | 0 | 0 | INTEGER | INTEGER |
| conversions | 0 | 0 | 0 | INTEGER | INTEGER |
| cost_per_click | 1500 | 1500 | 1500 | DOUBLE | DOUBLE |
| cost_per_conversion | 1500 | 1500 | 1500 | DOUBLE | DOUBLE |
| cost_per_thousand_impressions | 1500 | 1500 | 1500 | DOUBLE | DOUBLE |
| date_day | 0 | 0 | 0 | DATE | DATE |
| device_os | 0 | 0 | 0 | VARCHAR | VARCHAR |
| device_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| impressions | 0 | 0 | 0 | INTEGER | INTEGER |
| network | 0 | 0 | 0 | VARCHAR | VARCHAR |
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| return_on_ad_spend | 1500 | 1500 | 1500 | DOUBLE | DOUBLE |
| revenue | 0 | 0 | 0 | DECIMAL(18,2) | DECIMAL(18,2) |
| spend | 1500 | 1500 | 1500 | DECIMAL(18,2) | DECIMAL(18,2) |

assists 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

average_position 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0.00 |
| K2 | null | 0.00 |
| K3 | null | 0.00 |

bounce_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0.0000 |
| K2 | null | 0.0000 |
| K3 | null | 0.0000 |

click_through_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 8.186 |
| K2 | null | 6.7466 |
| K3 | null | 9.0134 |

cost_per_click 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 4.16 |
| K2 | null | 2.07 |
| K3 | null | 3.14 |

cost_per_conversion 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 20.33 |
| K2 | null | 34.95 |
| K3 | null | 69.63 |

cost_per_thousand_impressions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 340.39 |
| K2 | null | 139.73 |
| K3 | null | 282.68 |

return_on_ad_spend 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 1.4325 |
| K2 | null | 17.4656 |
| K3 | null | 6.6917 |

spend 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 731.84 |
| K2 | null | 279.60 |
| K3 | null | 696.25 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>9列；[{"column":"spend","table_rows":1500},{"column":"assists","table_rows":1500},{"column":"bounce_rate","table_rows":1500}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"platform","value":"MICROSOFT_ADS"},{"column":"_dbt_loaded_at","value":"2026-10-25 01:52:29.305205+08"}]</code> |
| B5_null_literal_output | <code>9输出列；[{"column":"spend","expression":["CAST(CAST(NULL AS DECIMAL(18, 2)) AS DECIMAL(18, 2))"]},{"column":"assists","expression":["CAST(CAST(NULL AS INT) AS INT)"]},{"column":"bounce_rate","expression":["CAST(CAST(NULL AS DECIMAL(8, 4)) AS DECIMAL(8, 4))"]}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"platform","expression":["'MICROSOFT_ADS'"]}]</code> |
| C9_agent_runtime_text | <code>S4:26 CURRENT_TIMESTAMP；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:60 CURRENT_TIMESTAMP；命中数=1</code> |

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
| 81 | run | <code>find sql -type f &#124; wc -l; grep -R ';' sql --include='*.sql' &#124; head; git status --short 2&gt;/dev/null &#124;&#124; true; python - &lt;&lt;'PY'<br>import yaml,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c[</code> | 999 | true | false |

### agent action 的 thought/message 命中原句

未找到命中原句。

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-006.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_microsoft_ads__campaign_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_microsoft_ads__campaign_report.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_stg_microsoft_ads__campaign_report/020_impl-006_stg_microsoft_ads__campaign_report.json`
- S11: `data/011_agent_alignment/impl-006_attempt_01/stg_microsoft_ads__campaign_report_2025-10-12.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
