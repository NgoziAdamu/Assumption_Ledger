# impl-023 | staging | stg_social_media__youtube_videos | 差异：S1；日期 2025-10-17

## 契约完整原文

S3:353–413

```yaml
    - name: stg_social_media__youtube_videos
      description: "YouTube videos staged with standardized fields and basic derived metrics; recent 2-year window."
      source_table: raw.youtube_video
      notes:
        - "Include only videos with view data: statistics_view_count IS NOT NULL."
        - "Restrict to last 2 years: snippet_published_at >= CURRENT_DATE - INTERVAL '2 years'."
        - "post_url is constructed as https://img.youtube.com/vi/{video_id}/default.jpg."
        - "All numeric metrics default to 0 when NULL."
        - "impressions and clicks both mirror statistics_view_count per SQL."
      columns:
        - name: video_id
          data_type: VARCHAR
          description: "CAST(id AS VARCHAR)."
        - name: video_published_at
          data_type: TIMESTAMP
          description: "snippet_published_at."
        - name: video_title
          data_type: VARCHAR
        - name: video_description
          data_type: VARCHAR
        - name: channel_id
          data_type: VARCHAR
        - name: channel_title
          data_type: VARCHAR
        - name: page_name
          data_type: VARCHAR
        - name: post_url
          data_type: VARCHAR
          description: "Thumbnail URL used as post URL: https://img.youtube.com/vi/{video_id}/default.jpg."
          validation_rules:
            - rule: "post_url RLIKE '^https://img.youtube.com/vi/.+/default.jpg'"
              on_failure: correct
        - name: privacy_status
          data_type: VARCHAR
        - name: clicks
          data_type: BIGINT
        - name: impressions
          data_type: BIGINT
          description: "COALESCE(statistics_view_count, 0) — estimated as views in SQL."
        - name: likes
          data_type: BIGINT
        - name: comments
          data_type: BIGINT
        - name: estimated_shares
          data_type: BIGINT
          description: >
            CASE WHEN statistics_like_count > 10 THEN FLOOR(statistics_like_count / 10) ELSE 0 END.
        - name: subscribers
          data_type: BIGINT
          description: "COALESCE(channel_info.channel_subscribers, 0)."
        - name: engagement_rate
          data_type: DOUBLE
          description: "CASE WHEN impressions > 0 THEN (likes + comments + estimated_shares)::DOUBLE / impressions ELSE 0.0 END."
        - name: _fivetran_synced
          data_type: TIMESTAMP
          description: "_fivetran_synced from raw.youtube_video."


# --------------------------------------------------------------------------- #
# PHASE 2: Defines the business logic from staging to analytical models.      #
# --------------------------------------------------------------------------- #
```

## agent 最终 SQL

S4

```sql
with channel_info as (
    select channel_id, max(channel_subscribers) as channel_subscribers
    from raw.youtube_channel_basic
    group by channel_id
)
select
    cast(v.id as varchar) as video_id,
    v.snippet_published_at::timestamp as video_published_at,
    v.snippet_title::varchar as video_title,
    v.snippet_description::varchar as video_description,
    v.snippet_channel_id::varchar as channel_id,
    v.snippet_channel_title::varchar as channel_title,
    coalesce(v.snippet_channel_title, 'Unknown Channel')::varchar as page_name,
    ('https://img.youtube.com/vi/' || v.id || '/default.jpg')::varchar as post_url,
    v.privacy_status::varchar as privacy_status,
    coalesce(v.statistics_view_count, 0)::bigint as clicks,
    coalesce(v.statistics_view_count, 0)::bigint as impressions,
    coalesce(v.statistics_like_count, 0)::bigint as likes,
    coalesce(v.statistics_comment_count, 0)::bigint as comments,
    case when v.statistics_like_count > 10 then floor(v.statistics_like_count / 10.0)::bigint else 0 end as estimated_shares,
    coalesce(try_cast(ci.channel_subscribers as bigint), 0)::bigint as subscribers,
    case when coalesce(v.statistics_view_count, 0) > 0
         then (coalesce(v.statistics_like_count, 0) + coalesce(v.statistics_comment_count, 0)
               + case when v.statistics_like_count > 10 then floor(v.statistics_like_count / 10.0) else 0 end)::double / v.statistics_view_count
         else 0.0 end as engagement_rate,
    v._fivetran_synced::timestamp as _fivetran_synced
from raw.youtube_video v
left join channel_info ci on ci.channel_id = v.snippet_channel_id
where v.statistics_view_count is not null
  and v.snippet_published_at >= current_date - interval '2 years'
  and v.snippet_published_at is not null
```

## gold SQL（仅供定位差异）

S5

```sql
-- YouTube videos staging table - Simplified version
-- Based on actual table structure

WITH source_videos AS (
    SELECT
        id,
        _fivetran_synced,
        snippet_published_at,
        snippet_title,
        snippet_description,
        snippet_channel_id,
        snippet_channel_title,
        snippet_thumbnails,
        statistics_comment_count,
        statistics_dislike_count,
        statistics_favorite_count,
        statistics_like_count,
        statistics_view_count,
        privacy_status,
        status_embeddable
    FROM raw.youtube_video
    WHERE statistics_view_count IS NOT NULL -- Include videos with view data
    AND snippet_published_at >= CURRENT_DATE - INTERVAL '2 years' -- Recent videos only
),

-- Get channel information
channel_info AS (
    SELECT DISTINCT
        channel_id,
        channel_display_name,
        channel_subscribers
    FROM raw.youtube_channel_basic
)

SELECT
    CAST(v.id AS VARCHAR) AS video_id,
    v.snippet_published_at AS video_published_at,
    CAST(v.snippet_title AS VARCHAR) AS video_title,
    CAST(v.snippet_description AS VARCHAR) AS video_description,
    CAST(v.snippet_channel_id AS VARCHAR) AS channel_id,
    COALESCE(v.snippet_channel_title, 'Unknown Channel') AS channel_title,
    CAST(c.channel_display_name AS VARCHAR) AS page_name,
    -- Use thumbnail URL as post URL
    CAST('https://img.youtube.com/vi/' || v.id || '/default.jpg' AS VARCHAR) AS post_url,
    v.privacy_status,
    -- Standardized metrics (clicks = views per original DBT logic)
    COALESCE(v.statistics_view_count, 0) AS clicks,
    COALESCE(v.statistics_view_count, 0) AS impressions, -- Estimate impressions as views
    COALESCE(v.statistics_like_count, 0) AS likes,
    COALESCE(v.statistics_comment_count, 0) AS comments,
    -- Estimate shares based on likes
    CASE
        WHEN COALESCE(v.statistics_like_count, 0) > 10
        THEN CAST(v.statistics_like_count / 10 AS BIGINT)
        ELSE 0
    END AS estimated_shares,
    -- Account metrics
    COALESCE(c.channel_subscribers, 0) AS subscribers,
    -- Engagement rate estimation
    CASE
        WHEN COALESCE(v.statistics_view_count, 0) > 0
        THEN (
            COALESCE(v.statistics_like_count, 0)::DOUBLE +
            COALESCE(v.statistics_comment_count, 0)::DOUBLE +
            (CASE WHEN COALESCE(v.statistics_like_count, 0) > 10 THEN v.statistics_like_count / 10 ELSE 0 END)::DOUBLE
        ) / v.statistics_view_count
        ELSE 0.0
    END AS engagement_rate,
    -- Additional channel metrics
    v._fivetran_synced
FROM source_videos v
LEFT JOIN channel_info c ON v.snippet_channel_id = c.channel_id
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 152 | 152 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"video_id":"-kb60w6ipkw","channel_id":"null"}</code> |
| K2 | <code>{"video_id":"-oa0mqiurga","channel_id":"null"}</code> |
| K3 | <code>{"video_id":"-tc7y7mngix","channel_id":"null"}</code> |
| K4 | <code>{"video_id":"05ywsruvh6r","channel_id":"null"}</code> |
| K5 | <code>{"video_id":"0gbagjkltjb","channel_id":"null"}</code> |
| K6 | <code>{"video_id":"0j32ik6aerz","channel_id":"null"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| video_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| channel_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| channel_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| comments | 0 | 0 | 0 | BIGINT | BIGINT |
| engagement_rate | 133 | 133 | 133 | DOUBLE | DOUBLE |
| estimated_shares | 66 | 66 | 66 | BIGINT | BIGINT |
| impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| likes | 0 | 0 | 0 | BIGINT | BIGINT |
| page_name | 152 | 152 | 152 | VARCHAR | VARCHAR |
| post_url | 0 | 0 | 0 | VARCHAR | VARCHAR |
| privacy_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subscribers | 152 | 152 | 152 | BIGINT | DOUBLE |
| video_description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_title | 0 | 0 | 0 | VARCHAR | VARCHAR |

engagement_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.008845469407505727 | 0.00884548071335379 |
| K2 | 0.620256646642479 | 0.6202603640040445 |
| K3 | 0.02269473598472142 | 0.02269477885391358 |

estimated_shares 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | 9157 | 9158 |
| K5 | 7963 | 7964 |
| K6 | 7437 | 7438 |

page_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Sutxpa integration cjlhtnwp | null |
| K2 | Vzibi nhg API | null |
| K3 | Api vyguhpw database jshwdnm | null |

subscribers 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 0.0 |
| K2 | 0 | 0.0 |
| K3 | 0 | 0.0 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A1_zero_rows | 行数=0 |
| B7_read_not_specified | <code>["raw.youtube_channel_basic"]</code> |
| C9_agent_runtime_text | <code>S4:30 current_date；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:23 CURRENT_DATE；命中数=1</code> |
| C9_contract_runtime_text | <code>S3:358 CURRENT_DATE；命中数=1</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 2094 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9937 | true | false |
| 15 | run | <code>sed -n '220,520p' docs/data_contract.yaml</code> | 16556 | true | false |
| 17 | run | <code>sed -n '520,790p' docs/data_contract.yaml</code> | 19316 | true | false |
| 23 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb',read_only=True)<br>for t, in c.execute("select table_name from information_schema.tables where table_schema='raw' orde</code> | 30939 | false | false |
| 29 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/write_sql.py &lt;&lt;'PY'<br>from pathlib import Path<br>files={}<br>files['staging/stg_social_media__account_history.sql'] = '''select<br>    try_cast(id a</code> | 0 | false | false |
| 31 | run | <code>cat &gt;&gt; /tmp/write_sql.py &lt;&lt;'PY'<br>files['intermediate/social_media_reporting__facebook_posts_reporting.sql'] = '''with source_posts as (<br>    select<br>        cast(page_id as varchar) as page_id,<br>        p</code> | 0 | false | false |
| 33 | run | <code>cat &gt;&gt; /tmp/write_sql.py &lt;&lt;'PY'<br>files['marts/social_media_reporting__rollup_report.sql'] = '''with all_posts as (<br>    select page_id, page_name, post_id, post_message, created_timestamp, platform,<br>   </code> | 917 | true | false |
| 37 | run | <code>grep 'staging\.&#124;intermediate\.&#124;marts\.' /tmp/pipeline.log &#124; tail -35; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting.duckdb',read_only=True)<br>for schema in ['staging','intermedi</code> | 1464 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb',read_only=True)<br>for t,col in [('account_history','timezone'),('facebook_pages_post_history','created_time'),('insta</code> | 1457 | false | false |
| 43 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb',read_only=True)<br>for t in ['account_history','organic_tweet_report','youtube_video','instagram_business_media_histor</code> | 4968 | false | false |
| 49 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql').rglob('*.sql'):<br> s=p.read_text()<br> assert not s.rstrip().endswith(';'), p<br> assert 'ref(' not in s.lower(), p<br> print(f'{p}: {len(s.splitline</code> | 1600 | true | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
files['staging/stg_social_media__youtube_videos.sql'] = '''with channel_info as (
```
event 31 / message

```text
    from staging.stg_social_media__youtube_videos
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-023.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__youtube_videos.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__youtube_videos.sql`
- S6: `records/006_contract_impl-023.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/result.md`
- S10: `data/024_packages_work/024_impl-023_stg_social_media__youtube_videos/024_impl-023_stg_social_media__youtube_videos.json`
- S11: `data/011_agent_alignment/impl-023/stg_social_media__youtube_videos_2025-10-17.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions`
