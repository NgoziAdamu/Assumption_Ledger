# impl-006 | staging | stg_snapchat_ads__campaign_report | 差异：S1；日期 2025-10-12

## 契约完整原文

S3:1149–1203

```yaml
    - name: "stg_snapchat_ads__campaign_report"
      description: "Staging table for Snapchat Ads  Campaign Report"
      columns:
        - name: "platform"
          data_type: VARCHAR
        - name: "campaign_id"
          data_type: VARCHAR
        - name: "date_day"
          data_type: DATE
        - name: "ad_account_id"
          data_type: VARCHAR
        - name: "impressions"
          data_type: INTEGER
        - name: "swipes"
          data_type: INTEGER
        - name: "spend"
          data_type: DECIMAL(18,2)
        - name: "video_views"
          data_type: INTEGER
        - name: "screen_time_millis"
          data_type: BIGINT
        - name: "quartile_1"
          data_type: INTEGER
        - name: "quartile_2"
          data_type: INTEGER
        - name: "quartile_3"
          data_type: INTEGER
        - name: "view_completion"
          data_type: INTEGER
        - name: "story_opens"
          data_type: INTEGER
        - name: "story_completes"
          data_type: INTEGER
        - name: "shares"
          data_type: INTEGER
        - name: "saves"
          data_type: INTEGER
        - name: "conversion_purchases"
          data_type: INTEGER
        - name: "conversion_purchases_value"
          data_type: DECIMAL(18,2)
        - name: "app_installs"
          data_type: INTEGER
        - name: "swipe_up_rate"
          data_type: DOUBLE
        - name: "cost_per_swipe"
          data_type: DOUBLE
        - name: "cost_per_thousand_impressions"
          data_type: DOUBLE
        - name: "cost_per_video_view"
          data_type: DOUBLE
        - name: "cost_per_install"
          data_type: DOUBLE
        - name: "_dbt_loaded_at"
          data_type: TIMESTAMP WITH TIME ZONE
```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT * FROM raw.snapchat_campaign_hourly_report_data
),
cleaned AS (
    SELECT
        'SNAPCHAT_ADS' AS platform,
        CAST(TRY_CAST("campaign_id" AS VARCHAR) AS VARCHAR) AS campaign_id,
        CAST(TRY_CAST(date AS DATE) AS DATE) AS date_day,
        CAST(NULL::VARCHAR AS VARCHAR) AS ad_account_id,
        CAST(TRY_CAST("impressions" AS BIGINT) AS INTEGER) AS impressions,
        TRY_CAST("swipes" AS INTEGER) AS swipes,
        CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend,
        CAST(TRY_CAST("video_views" AS BIGINT) AS INTEGER) AS video_views,
        TRY_CAST("screen_time_millis" AS BIGINT) AS screen_time_millis,
        TRY_CAST("quartile_1" AS INTEGER) AS quartile_1,
        TRY_CAST("quartile_2" AS INTEGER) AS quartile_2,
        TRY_CAST("quartile_3" AS INTEGER) AS quartile_3,
        TRY_CAST("view_completion" AS INTEGER) AS view_completion,
        TRY_CAST("story_opens" AS INTEGER) AS story_opens,
        TRY_CAST("story_completes" AS INTEGER) AS story_completes,
        TRY_CAST("shares" AS INTEGER) AS shares,
        TRY_CAST("saves" AS INTEGER) AS saves,
        TRY_CAST("conversion_purchases" AS INTEGER) AS conversion_purchases,
        TRY_CAST("conversion_purchases_value" AS DECIMAL(18,2)) AS conversion_purchases_value,
        TRY_CAST("total_installs" AS INTEGER) AS app_installs,
        CAST(NULL::DOUBLE AS DOUBLE) AS swipe_up_rate,
        CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_swipe,
        CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions,
        CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_video_view,
        CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_install,
        CURRENT_TIMESTAMP AS _dbt_loaded_at
    FROM source_rows
)
SELECT * FROM cleaned
```

## gold SQL（仅供定位差异）

S5

```sql
-- Snapchat Ads Campaign Report Staging Model
-- Standardizes raw Snapchat Ads campaign-level data for downstream consumption
-- Removes Fivetran-specific logic and converts to DuckDB-compatible SQL

SELECT 
    -- Platform Identifier
    'snapchat_ads' AS platform,
    
    -- Primary Keys
    CAST(campaign_id AS VARCHAR) AS campaign_id,
    CAST(date AS DATE) AS date_day,
    
    -- Campaign Attributes
    CAST('unknown' AS VARCHAR) AS ad_account_id,
    
    -- Performance Metrics
    CAST(impressions AS INTEGER) AS impressions,
    CAST(swipes AS INTEGER) AS swipes,
    CAST(spend AS DECIMAL(18,2)) AS spend,
    
    -- Snapchat-specific Metrics (using available columns)
    CASE WHEN video_views IS NULL OR TRIM(CAST(video_views AS VARCHAR)) IN ('', 'true', 'false') OR TRIM(CAST(video_views AS VARCHAR)) LIKE 'mock_%' THEN 0 ELSE CAST(video_views AS INTEGER) END AS video_views,
    CASE WHEN screen_time_millis IS NULL OR TRIM(CAST(screen_time_millis AS VARCHAR)) LIKE '%-%-%' OR TRIM(CAST(screen_time_millis AS VARCHAR)) LIKE 'mock_%' THEN 0 ELSE CAST(COALESCE(screen_time_millis, '0') AS BIGINT) END AS screen_time_millis,
    CASE WHEN quartile_1 IS NULL OR TRIM(CAST(quartile_1 AS VARCHAR)) IN ('', 'true', 'false') OR TRIM(CAST(quartile_1 AS VARCHAR)) LIKE 'mock_%' THEN 0 ELSE CAST(quartile_1 AS INTEGER) END AS quartile_1,
    CASE WHEN quartile_2 IS NULL OR TRIM(CAST(quartile_2 AS VARCHAR)) IN ('', 'true', 'false') OR TRIM(CAST(quartile_2 AS VARCHAR)) LIKE 'mock_%' THEN 0 ELSE CAST(quartile_2 AS INTEGER) END AS quartile_2,
    CASE WHEN quartile_3 IS NULL OR TRIM(CAST(quartile_3 AS VARCHAR)) IN ('', 'true', 'false') OR TRIM(CAST(quartile_3 AS VARCHAR)) LIKE 'mock_%' THEN 0 ELSE CAST(quartile_3 AS INTEGER) END AS quartile_3,
    CASE WHEN view_completion IS NULL OR TRIM(CAST(view_completion AS VARCHAR)) IN ('', 'true', 'false') OR TRIM(CAST(view_completion AS VARCHAR)) LIKE 'mock_%' THEN 0 ELSE CAST(view_completion AS INTEGER) END AS view_completion,
    CASE WHEN story_opens IS NULL OR TRIM(CAST(story_opens AS VARCHAR)) IN ('', 'true', 'false') OR TRIM(CAST(story_opens AS VARCHAR)) LIKE 'mock_%' THEN 0 ELSE CAST(story_opens AS INTEGER) END AS story_opens,
    CASE WHEN story_completes IS NULL OR TRIM(CAST(story_completes AS VARCHAR)) IN ('', 'true', 'false') OR TRIM(CAST(story_completes AS VARCHAR)) LIKE 'mock_%' THEN 0 ELSE CAST(story_completes AS INTEGER) END AS story_completes,
    CASE WHEN shares IS NULL OR TRIM(CAST(shares AS VARCHAR)) IN ('', 'true', 'false') OR TRIM(CAST(shares AS VARCHAR)) LIKE 'mock_%' THEN 0 ELSE CAST(shares AS INTEGER) END AS shares,
    CASE WHEN saves IS NULL OR TRIM(CAST(saves AS VARCHAR)) IN ('', 'true', 'false') OR TRIM(CAST(saves AS VARCHAR)) LIKE 'mock_%' THEN 0 ELSE CAST(saves AS INTEGER) END AS saves,
    
    -- Conversion Metrics (using available columns)
    CASE WHEN conversion_purchases IS NULL OR TRIM(CAST(conversion_purchases AS VARCHAR)) IN ('', 'true', 'false') OR TRIM(CAST(conversion_purchases AS VARCHAR)) LIKE 'mock_%' THEN 0 ELSE CAST(conversion_purchases AS INTEGER) END AS conversion_purchases,
    CASE WHEN conversion_purchases_value IS NULL OR TRIM(CAST(conversion_purchases_value AS VARCHAR)) LIKE 'mock_%' THEN 0.0 ELSE CAST(COALESCE(conversion_purchases_value, '0') AS DECIMAL(18,2)) END AS conversion_purchases_value,
    CASE WHEN total_installs IS NULL OR TRIM(CAST(total_installs AS VARCHAR)) IN ('', 'true', 'false') OR TRIM(CAST(total_installs AS VARCHAR)) LIKE 'mock_%' THEN 0 ELSE CAST(total_installs AS INTEGER) END AS app_installs,
    
    -- Calculated Metrics
    CASE 
        WHEN impressions > 0 THEN ROUND((CAST(swipes AS DECIMAL) / CAST(impressions AS DECIMAL)) * 100, 4)
        ELSE 0 
    END AS swipe_up_rate,
    
    CASE 
        WHEN swipes > 0 THEN ROUND(spend / swipes, 2)
        ELSE 0 
    END AS cost_per_swipe,
    
    CASE 
        WHEN impressions > 0 THEN ROUND((spend / impressions) * 1000, 2)
        ELSE 0 
    END AS cost_per_thousand_impressions,
    
    CASE 
        WHEN (CASE WHEN video_views = '' OR video_views = 'true' OR video_views = 'false' OR video_views IS NULL THEN 0 ELSE CAST(video_views AS INTEGER) END) > 0 THEN ROUND(spend / (CASE WHEN video_views = '' OR video_views = 'true' OR video_views = 'false' OR video_views IS NULL THEN 0 ELSE CAST(video_views AS INTEGER) END), 2)
        ELSE 0 
    END AS cost_per_video_view,
    
    CASE 
        WHEN (CASE WHEN total_installs IS NULL OR TRIM(CAST(total_installs AS VARCHAR)) IN ('', 'true', 'false') THEN 0 ELSE CAST(total_installs AS INTEGER) END) > 0 THEN ROUND(spend / (CASE WHEN total_installs IS NULL OR TRIM(CAST(total_installs AS VARCHAR)) IN ('', 'true', 'false') THEN 0 ELSE CAST(total_installs AS INTEGER) END), 2)
        ELSE 0 
    END AS cost_per_install,
    
    -- Data Quality
    CURRENT_TIMESTAMP AS _dbt_loaded_at

FROM raw.snapchat_campaign_hourly_report_data

WHERE date IS NOT NULL
    AND campaign_id IS NOT NULL
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 900 | 900 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"campaign_id":"unk01019164354"}</code> |
| K2 | <code>{"campaign_id":"unk01026640470"}</code> |
| K3 | <code>{"campaign_id":"unk01042090186"}</code> |
| K4 | <code>{"campaign_id":"unk01066455974"}</code> |
| K5 | <code>{"campaign_id":"unk01081252993"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| ad_account_id | 900 | 900 | 900 | VARCHAR | VARCHAR |
| app_installs | 0 | 0 | 0 | INTEGER | INTEGER |
| conversion_purchases | 900 | 900 | 900 | INTEGER | INTEGER |
| conversion_purchases_value | 0 | 0 | 0 | DECIMAL(18,2) | DECIMAL(18,2) |
| cost_per_install | 900 | 900 | 900 | DOUBLE | DOUBLE |
| cost_per_swipe | 900 | 900 | 900 | DOUBLE | DOUBLE |
| cost_per_thousand_impressions | 900 | 900 | 900 | DOUBLE | DOUBLE |
| cost_per_video_view | 900 | 900 | 900 | DOUBLE | DOUBLE |
| date_day | 0 | 0 | 0 | DATE | DATE |
| impressions | 0 | 0 | 0 | INTEGER | INTEGER |
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| quartile_1 | 900 | 900 | 900 | INTEGER | INTEGER |
| quartile_2 | 900 | 900 | 900 | INTEGER | INTEGER |
| quartile_3 | 900 | 900 | 900 | INTEGER | INTEGER |
| saves | 0 | 0 | 0 | INTEGER | INTEGER |
| screen_time_millis | 900 | 900 | 900 | BIGINT | BIGINT |
| shares | 673 | 673 | 673 | INTEGER | INTEGER |
| spend | 900 | 900 | 900 | DECIMAL(18,2) | DECIMAL(18,2) |
| story_completes | 900 | 900 | 900 | INTEGER | INTEGER |
| story_opens | 0 | 0 | 0 | INTEGER | INTEGER |
| swipe_up_rate | 900 | 900 | 900 | DOUBLE | DOUBLE |
| swipes | 0 | 0 | 0 | INTEGER | INTEGER |
| video_views | 685 | 685 | 685 | INTEGER | INTEGER |
| view_completion | 900 | 900 | 900 | INTEGER | INTEGER |

ad_account_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | unknown |
| K2 | null | unknown |
| K3 | null | unknown |

conversion_purchases 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

cost_per_install 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 20.07 |
| K2 | null | 14.96 |
| K3 | null | 16.86 |

cost_per_swipe 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 9.68 |
| K2 | null | 8.05 |
| K3 | null | 44.97 |

cost_per_thousand_impressions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 845.37 |
| K2 | null | 366455.0 |
| K3 | null | 884.04 |

cost_per_video_view 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0.0 |
| K2 | null | 0.0 |
| K3 | null | 0.0 |

quartile_1 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

quartile_2 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

quartile_3 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

screen_time_millis 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

shares 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | null | 0 |
| K4 | null | 0 |
| K5 | null | 0 |

spend 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 541.88 |
| K2 | null | 732.91 |
| K3 | null | 674.52 |

story_completes 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

swipe_up_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 8.7363 |
| K2 | null | 4550.0 |
| K3 | null | 1.9659 |

video_views 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

view_completion 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0 |
| K2 | null | 0 |
| K3 | null | 0 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>14列；[{"column":"ad_account_id","table_rows":900},{"column":"spend","table_rows":900},{"column":"screen_time_millis","table_rows":900}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"platform","value":"SNAPCHAT_ADS"},{"column":"_dbt_loaded_at","value":"2026-10-25 01:52:29.335436+08"}]</code> |
| B5_null_literal_output | <code>7输出列；[{"column":"ad_account_id","expression":["CAST(CAST(NULL AS TEXT) AS TEXT)"]},{"column":"spend","expression":["CAST(CAST(NULL AS DECIMAL(18, 2)) AS DECIMAL(18, 2))"]},{"column":"swipe_up_rate","expression":["CAST(CAST(NULL AS DOUBLE) AS DOUBLE)"]}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"platform","expression":["'SNAPCHAT_ADS'"]}]</code> |
| C9_agent_runtime_text | <code>S4:31 CURRENT_TIMESTAMP；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:65 CURRENT_TIMESTAMP；命中数=1</code> |

## 轨迹索引（不放输出原文）

本题事件总数：99；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort &amp;&amp; cat config/layer_dependencies.yaml</code> | 7365 | true | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('ad_reporting_start.yaml'))<br>print(type(x), x.keys())<br>print(str(x)[:2500])<br>PY</code> | 7232 | false | false |
| 17 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting_start.duckdb',read_only=True)<br>for r in c.execute("select table_name from information_schema.tables where table_schema='raw' order by 1").fe</code> | 26086 | false | false |
| 19 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml,duckdb,os,re<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))<br>con=duckdb.connect('ad_reporting_start.duckdb',r</code> | 528 | false | false |
| 29 | run | <code>python run.py &gt; /tmp/runlog2 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete&#124;ERROR - Failed&#124;Binder Error&#124;Catalog Error' /tmp/runlog2</code> | 1956 | true | false |
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_stg_snapchat_ads__campaign_report/020_impl-006_stg_snapchat_ads__campaign_report.json`
- S11: `data/011_agent_alignment/impl-006_attempt_01/stg_snapchat_ads__campaign_report_2025-10-12.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
