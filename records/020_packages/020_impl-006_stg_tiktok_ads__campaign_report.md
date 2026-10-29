# impl-006 | staging | stg_tiktok_ads__campaign_report | 差异：S1；日期 2025-10-12

## 契约完整原文

S3:1204–1262

```yaml
    - name: "stg_tiktok_ads__campaign_report"
      description: "Staging table for Tiktok Ads  Campaign Report"
      columns:
        - name: "platform"
          data_type: VARCHAR
        - name: "campaign_id"
          data_type: VARCHAR
        - name: "date_day"
          data_type: DATE
        - name: "advertiser_id"
          data_type: VARCHAR
        - name: "impressions"
          data_type: INTEGER
        - name: "clicks"
          data_type: INTEGER
        - name: "spend"
          data_type: DECIMAL(18,2)
        - name: "reach"
          data_type: INTEGER
        - name: "video_play_actions"
          data_type: INTEGER
        - name: "video_watched_2_s"
          data_type: INTEGER
        - name: "video_watched_6_s"
          data_type: INTEGER
        - name: "video_views_p_25"
          data_type: INTEGER
        - name: "video_views_p_50"
          data_type: INTEGER
        - name: "video_views_p_75"
          data_type: INTEGER
        - name: "video_views_p_100"
          data_type: INTEGER
        - name: "profile_visits"
          data_type: INTEGER
        - name: "follows"
          data_type: INTEGER
        - name: "likes"
          data_type: INTEGER
        - name: "comments"
          data_type: INTEGER
        - name: "shares"
          data_type: INTEGER
        - name: "conversions"
          data_type: INTEGER
        - name: "conversion_rate"
          data_type: DECIMAL(8,4)
        - name: "cost_per_conversion"
          data_type: DECIMAL(18,2)
        - name: "click_through_rate"
          data_type: DOUBLE
        - name: "calculated_cost_per_click"
          data_type: DOUBLE
        - name: "cost_per_thousand_impressions"
          data_type: DOUBLE
        - name: "cost_per_thousand_reached"
          data_type: DOUBLE
        - name: "_dbt_loaded_at"
          data_type: TIMESTAMP WITH TIME ZONE
```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT * FROM raw.tiktok_campaign_report_hourly_data
),
cleaned AS (
    SELECT
        'TIKTOK_ADS' AS platform,
        CAST(TRY_CAST("CAMPAIGN_ID" AS VARCHAR) AS VARCHAR) AS campaign_id,
        CAST(TRY_CAST(STAT_TIME_HOUR AS DATE) AS DATE) AS date_day,
        CAST(NULL::VARCHAR AS VARCHAR) AS advertiser_id,
        CAST(TRY_CAST("IMPRESSIONS" AS BIGINT) AS INTEGER) AS impressions,
        CAST(TRY_CAST("CLICKS" AS BIGINT) AS INTEGER) AS clicks,
        CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend,
        TRY_CAST("REACH" AS INTEGER) AS reach,
        TRY_CAST("VIDEO_PLAY_ACTIONS" AS INTEGER) AS video_play_actions,
        TRY_CAST("VIDEO_WATCHED_2_S" AS INTEGER) AS video_watched_2_s,
        TRY_CAST("VIDEO_WATCHED_6_S" AS INTEGER) AS video_watched_6_s,
        TRY_CAST("VIDEO_VIEWS_P_25" AS INTEGER) AS video_views_p_25,
        TRY_CAST("VIDEO_VIEWS_P_50" AS INTEGER) AS video_views_p_50,
        TRY_CAST("VIDEO_VIEWS_P_75" AS INTEGER) AS video_views_p_75,
        TRY_CAST("VIDEO_VIEWS_P_100" AS INTEGER) AS video_views_p_100,
        TRY_CAST("PROFILE_VISITS" AS INTEGER) AS profile_visits,
        TRY_CAST("FOLLOWS" AS INTEGER) AS follows,
        TRY_CAST("LIKES" AS INTEGER) AS likes,
        TRY_CAST("COMMENTS" AS INTEGER) AS comments,
        TRY_CAST("SHARES" AS INTEGER) AS shares,
        CAST(NULL::INTEGER AS INTEGER) AS conversions,
        TRY_CAST("CONVERSION_RATE" AS DECIMAL(8,4)) AS conversion_rate,
        TRY_CAST("COST_PER_CONVERSION" AS DECIMAL(18,2)) AS cost_per_conversion,
        TRY_CAST("CTR" AS DOUBLE) AS click_through_rate,
        CAST(NULL::DOUBLE AS DOUBLE) AS calculated_cost_per_click,
        CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions,
        CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_reached,
        CURRENT_TIMESTAMP AS _dbt_loaded_at
    FROM source_rows
)
SELECT * FROM cleaned
```

## gold SQL（仅供定位差异）

S5

```sql
-- TikTok Ads Campaign Report Staging Model
-- Standardizes raw TikTok Ads campaign-level data for downstream consumption
-- Removes Fivetran-specific logic and converts to DuckDB-compatible SQL

SELECT 
    -- Platform Identifier
    'tiktok_ads' AS platform,
    
    -- Primary Keys
    CAST(CAMPAIGN_ID AS VARCHAR) AS campaign_id,
    CAST(STAT_TIME_HOUR AS DATE) AS date_day,
    
    -- Campaign Attributes
    CAST('unknown' AS VARCHAR) AS advertiser_id,
    
    -- Performance Metrics
    CAST(IMPRESSIONS AS INTEGER) AS impressions,
    CAST(CLICKS AS INTEGER) AS clicks,
    CAST(SPEND AS DECIMAL(18,2)) AS spend,
    CAST(REACH AS INTEGER) AS reach,
    
    -- TikTok-specific Metrics (using available columns)
    CAST(COALESCE(VIDEO_PLAY_ACTIONS, '0') AS INTEGER) AS video_play_actions,
    CAST(COALESCE(VIDEO_WATCHED_2_S, '0') AS INTEGER) AS video_watched_2_s,
    CAST(COALESCE(VIDEO_WATCHED_6_S, '0') AS INTEGER) AS video_watched_6_s,
    CAST(COALESCE(VIDEO_VIEWS_P_25, '0') AS INTEGER) AS video_views_p_25,
    CAST(COALESCE(VIDEO_VIEWS_P_50, '0') AS INTEGER) AS video_views_p_50,
    CAST(COALESCE(VIDEO_VIEWS_P_75, '0') AS INTEGER) AS video_views_p_75,
    CAST(COALESCE(VIDEO_VIEWS_P_100, '0') AS INTEGER) AS video_views_p_100,
    CASE WHEN PROFILE_VISITS IS NULL OR TRIM(CAST(PROFILE_VISITS AS VARCHAR)) IN ('', 'true', 'false') THEN 0 ELSE CAST(PROFILE_VISITS AS INTEGER) END AS profile_visits,
    CASE WHEN FOLLOWS IS NULL OR TRIM(CAST(FOLLOWS AS VARCHAR)) IN ('', 'true', 'false') THEN 0 ELSE CAST(FOLLOWS AS INTEGER) END AS follows,
    CASE WHEN LIKES IS NULL OR TRIM(CAST(LIKES AS VARCHAR)) IN ('', 'true', 'false') THEN 0 ELSE CAST(LIKES AS INTEGER) END AS likes,
    CASE WHEN COMMENTS IS NULL OR TRIM(CAST(COMMENTS AS VARCHAR)) IN ('', 'true', 'false') THEN 0 ELSE CAST(COMMENTS AS INTEGER) END AS comments,
    CASE WHEN SHARES IS NULL OR TRIM(CAST(SHARES AS VARCHAR)) IN ('', 'true', 'false') THEN 0 ELSE CAST(SHARES AS INTEGER) END AS shares,
    
    -- Conversion Metrics (using available columns)
    CASE WHEN CONVERSION IS NULL OR TRIM(CAST(CONVERSION AS VARCHAR)) IN ('', 'true', 'false') OR CONVERSION LIKE 'mock_%' THEN 0 ELSE CAST(CONVERSION AS INTEGER) END AS conversions,
    CASE WHEN CONVERSION_RATE IS NULL OR TRIM(CAST(CONVERSION_RATE AS VARCHAR)) LIKE 'mock_%' THEN 0.0 ELSE CAST(COALESCE(CONVERSION_RATE, '0') AS DECIMAL(8,4)) END AS conversion_rate,
    CASE WHEN COST_PER_CONVERSION IS NULL OR TRIM(CAST(COST_PER_CONVERSION AS VARCHAR)) LIKE 'mock_%' THEN 0.0 ELSE CAST(COALESCE(COST_PER_CONVERSION, '0') AS DECIMAL(18,2)) END AS cost_per_conversion,
    
    -- Calculated Metrics
    CASE 
        WHEN impressions > 0 THEN ROUND((CAST(clicks AS DECIMAL) / CAST(impressions AS DECIMAL)) * 100, 4)
        ELSE 0 
    END AS click_through_rate,
    
    CASE 
        WHEN clicks > 0 THEN ROUND(spend / clicks, 2)
        ELSE 0 
    END AS calculated_cost_per_click,
    
    CASE 
        WHEN impressions > 0 THEN ROUND((spend / impressions) * 1000, 2)
        ELSE 0 
    END AS cost_per_thousand_impressions,
    
    CASE 
        WHEN CAST(REACH AS INTEGER) > 0 THEN ROUND((spend / CAST(REACH AS DECIMAL)) * 1000, 2)
        ELSE 0 
    END AS cost_per_thousand_reached,
    
    -- Data Quality
    CURRENT_TIMESTAMP AS _dbt_loaded_at

FROM raw.tiktok_campaign_report_hourly_data

WHERE STAT_TIME_HOUR IS NOT NULL
    AND CAMPAIGN_ID IS NOT NULL
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 900 | 900 | 900 | 900 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| date_day | 0 | 0 | 0 | DATE | DATE |
| advertiser_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| calculated_cost_per_click | 0 | 0 | 0 | DOUBLE | DOUBLE |
| click_through_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| clicks | 0 | 0 | 0 | INTEGER | INTEGER |
| comments | 0 | 0 | 0 | INTEGER | INTEGER |
| conversion_rate | 0 | 0 | 0 | DECIMAL(8,4) | DECIMAL(8,4) |
| conversions | 0 | 0 | 0 | INTEGER | INTEGER |
| cost_per_conversion | 0 | 0 | 0 | DECIMAL(18,2) | DECIMAL(18,2) |
| cost_per_thousand_impressions | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cost_per_thousand_reached | 0 | 0 | 0 | DOUBLE | DOUBLE |
| follows | 0 | 0 | 0 | INTEGER | INTEGER |
| impressions | 0 | 0 | 0 | INTEGER | INTEGER |
| likes | 0 | 0 | 0 | INTEGER | INTEGER |
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| profile_visits | 0 | 0 | 0 | INTEGER | INTEGER |
| reach | 0 | 0 | 0 | INTEGER | INTEGER |
| shares | 0 | 0 | 0 | INTEGER | INTEGER |
| spend | 0 | 0 | 0 | DECIMAL(18,2) | DECIMAL(18,2) |
| video_play_actions | 0 | 0 | 0 | INTEGER | INTEGER |
| video_views_p_100 | 0 | 0 | 0 | INTEGER | INTEGER |
| video_views_p_25 | 0 | 0 | 0 | INTEGER | INTEGER |
| video_views_p_50 | 0 | 0 | 0 | INTEGER | INTEGER |
| video_views_p_75 | 0 | 0 | 0 | INTEGER | INTEGER |
| video_watched_2_s | 0 | 0 | 0 | INTEGER | INTEGER |
| video_watched_6_s | 0 | 0 | 0 | INTEGER | INTEGER |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"campaign_id":"mock_CAMPAIGN_ID_1","date_day":"2021-12-29","advertiser_id":null},{"campaign_id":"mock_CAMPAIGN_ID_1","date_day":"2024-01-28","advertiser_id":null},{"campaign_id":"mock_CAMPAIGN_ID_10","date_day":"2021-12-05","advertiser_id":null},{"campaign_id":"mock_CAMPAIGN_ID_10","date_day":"2024-09-21","advertiser_id":null},{"campaign_id":"mock_CAMPAIGN_ID_100","date_day":"2023-11-12","advertiser_id":null}]</code> | <code>[{"campaign_id":"mock_CAMPAIGN_ID_1","date_day":"2021-12-29","advertiser_id":"unknown"},{"campaign_id":"mock_CAMPAIGN_ID_1","date_day":"2024-01-28","advertiser_id":"unknown"},{"campaign_id":"mock_CAMPAIGN_ID_10","date_day":"2021-12-05","advertiser_id":"unknown"},{"campaign_id":"mock_CAMPAIGN_ID_10","date_day":"2024-09-21","advertiser_id":"unknown"},{"campaign_id":"mock_CAMPAIGN_ID_100","date_day":"2023-11-12","advertiser_id":"unknown"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>8列；[{"column":"advertiser_id","table_rows":900},{"column":"spend","table_rows":900},{"column":"conversions","table_rows":900}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"platform","value":"TIKTOK_ADS"},{"column":"_dbt_loaded_at","value":"2026-10-25 01:52:29.346304+08"}]</code> |
| B5_null_literal_output | <code>6输出列；[{"column":"advertiser_id","expression":["CAST(CAST(NULL AS TEXT) AS TEXT)"]},{"column":"spend","expression":["CAST(CAST(NULL AS DECIMAL(18, 2)) AS DECIMAL(18, 2))"]},{"column":"conversions","expression":["CAST(CAST(NULL AS INT) AS INT)"]}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"platform","expression":["'TIKTOK_ADS'"]}]</code> |
| C9_agent_runtime_text | <code>S4:33 CURRENT_TIMESTAMP；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:63 CURRENT_TIMESTAMP；命中数=1</code> |

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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_stg_tiktok_ads__campaign_report/020_impl-006_stg_tiktok_ads__campaign_report.json`
- S11: `data/011_agent_alignment/impl-006_attempt_01/stg_tiktok_ads__campaign_report_2025-10-12.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
