# impl-023 | intermediate | social_media_reporting__youtube_videos_reporting | 差异：S1；日期 2025-10-17

## 契约完整原文

S3:677–743

```yaml
    - name: social_media_reporting__youtube_videos_reporting
      description: Standardizes YouTube videos to a unified post-level schema and derives ratios for the last two years of videos
      grain: One row per post_id (video_id)
      source_models:
      - staging.stg_social_media__youtube_videos
      business_logic: '- Source and filter: use staging.stg_social_media__youtube_videos rows where video_id is present and video_published_at is within the last two years. - Mapping: - page_id: channel_id cast to text; nulls remain null. - page_name: channel title; if missing, set to ''Unknown Channel''. - post_id: video_id cast to text (always present due to filter). - created_timestamp: video_published_at (always present due to filter). - platform: constant ''youtube''. - post_message: video_description cast to text; original casing and spacing preserved. - clicks and impressions: both set to the video''s views; views come from the source clicks field; default to 0 when missing. - likes, comments, shares: interactions default to 0 when missing; shares use the source estimated_shares. - post_url: passed through from source; may represent a thumbnail URL; may be null. - privacy_status: passed through. - channel_subscribers and channel_total_videos: default to 0; total_videos is 0 in the current SQL. - calculated_engagement_rate: - Use the provided engagement_rate when it is positive; otherwise, if views > 0, compute (likes + comments + shares) divided by views; else 0.0; no rounding or capping. - Derived ratios: - views_per_subscriber: clicks divided by channel_subscribers when subscribers > 0, else 0.0. - likes_per_view_ratio: likes divided by clicks when clicks > 0, else 0.0. - No aggregation, de-duplication, or ordering; rows mirror the filtered source.'
      columns:
      - name: page_id
        data_type: VARCHAR
        description: Channel identifier cast to text; nulls preserved
      - name: page_name
        data_type: VARCHAR
        description: Channel title with fallback to 'Unknown Channel' when missing
      - name: post_id
        data_type: VARCHAR
        description: YouTube video identifier cast to text; non-null due to the source filter on video_id
        tests:
        - not_null
      - name: post_message
        data_type: VARCHAR
        description: Video description text; original casing and whitespace preserved; may be null
      - name: created_timestamp
        data_type: TIMESTAMP
        description: Video publish timestamp limited to the last two years by the filter; non-null
        tests:
        - not_null
      - name: platform
        data_type: VARCHAR
        description: Constant platform label 'youtube'
      - name: clicks
        data_type: BIGINT
        description: YouTube views treated as clicks; sourced from the staging clicks field; defaults to 0 when missing
      - name: impressions
        data_type: BIGINT
        description: Proxy equal to clicks (views); defaults to 0 when missing
      - name: likes
        data_type: BIGINT
        description: Total likes default to 0 when missing
      - name: shares
        data_type: BIGINT
        description: Estimated shares from the source estimated_shares; default to 0 when missing
      - name: comments
        data_type: BIGINT
        description: Total comments default to 0 when missing
      - name: post_url
        data_type: VARCHAR
        description: URL passed through from source (may be a thumbnail URL); may be null
      - name: calculated_engagement_rate
        data_type: DOUBLE
        description: 'Engagement rate: use provided value when positive; otherwise (likes + comments + shares) divided by views when views > 0; else 0.0; no rounding'
        tests:
        - calculated_engagement_rate >= 0
      - name: privacy_status
        data_type: VARCHAR
        description: Video privacy status passed through; may be null
      - name: channel_subscribers
        data_type: DOUBLE
        description: Channel subscribers default to 0 when missing
      - name: channel_total_videos
        data_type: INTEGER
        description: Total videos default to 0; currently always 0 in this model
      - name: views_per_subscriber
        data_type: DOUBLE
        description: Clicks divided by channel_subscribers when subscribers > 0; otherwise 0.0; no rounding
      - name: likes_per_view_ratio
        data_type: DOUBLE
        description: Likes divided by clicks when clicks > 0; otherwise 0.0; no rounding
```

## agent 最终 SQL

S4

```sql
with source_videos as (
    select *
    from staging.stg_social_media__youtube_videos
    where video_id is not null
      and video_published_at is not null
      and video_published_at >= current_date - interval '2 years'
),
video_metrics as (
    select
        cast(channel_id as varchar) as page_id,
        coalesce(channel_title, 'Unknown Channel')::varchar as page_name,
        cast(video_id as varchar) as post_id,
        video_description::varchar as post_message,
        video_published_at as created_timestamp,
        coalesce(clicks, 0)::bigint as clicks,
        coalesce(impressions, 0)::bigint as impressions,
        coalesce(likes, 0)::bigint as likes,
        coalesce(estimated_shares, 0)::bigint as shares,
        coalesce(comments, 0)::bigint as comments,
        post_url,
        privacy_status,
        coalesce(subscribers, 0)::double as channel_subscribers,
        coalesce(engagement_rate, 0.0)::double as source_engagement_rate
    from source_videos
)
select
    page_id,
    page_name,
    post_id,
    post_message,
    created_timestamp,
    'youtube'::varchar as platform,
    clicks,
    impressions,
    likes,
    shares,
    comments,
    post_url,
    case when source_engagement_rate > 0 then source_engagement_rate
         when clicks > 0 then (likes + comments + shares)::double / clicks else 0.0 end as calculated_engagement_rate,
    privacy_status,
    channel_subscribers,
    0::integer as channel_total_videos,
    case when channel_subscribers > 0 then clicks::double / channel_subscribers else 0.0 end as views_per_subscriber,
    case when clicks > 0 then likes::double / clicks else 0.0 end as likes_per_view_ratio
from video_metrics
```

## gold SQL（仅供定位差异）

S5

```sql
-- YouTube videos reporting intermediate table
-- Standardizes YouTube video data for unified reporting

WITH youtube_videos_source AS (
    SELECT
        video_id,
        video_published_at,
        video_title,
        video_description,
        channel_id,
        page_name AS channel_title,
        post_url,
        privacy_status,
        clicks AS views,
        likes,
        comments,
        estimated_shares AS shares,
        engagement_rate,
        0 AS favorites,
        subscribers,
        0 AS total_videos
    FROM staging.stg_social_media__youtube_videos
    WHERE video_id IS NOT NULL
    AND video_published_at >= CURRENT_DATE - INTERVAL '2 years' -- Recent videos only
),

-- Standardize to common schema (follow original DBT logic where views = clicks)
youtube_standardized AS (
    SELECT
        CAST(channel_id AS VARCHAR) AS page_id,
        COALESCE(channel_title, 'Unknown Channel') AS page_name,
        CAST(video_id AS VARCHAR) AS post_id,
        video_published_at AS created_timestamp,
        'youtube' AS platform,
        -- Use video description as post message per original logic
        CAST(video_description AS VARCHAR) AS post_message,
        -- YouTube views count as clicks per original logic
        COALESCE(views, 0) AS clicks,
        -- YouTube doesn't provide impressions directly, estimate based on views
        COALESCE(views, 0) AS impressions,
        COALESCE(likes, 0) AS likes,
        COALESCE(comments, 0) AS comments,
        COALESCE(shares, 0) AS shares,
        -- Use thumbnail URL as post_url per original logic
        CAST(post_url AS VARCHAR) AS post_url,
        -- Use calculated or provided engagement rate
        CASE
            WHEN COALESCE(engagement_rate, 0.0) > 0 THEN engagement_rate
            WHEN COALESCE(views, 0) > 0
            THEN (COALESCE(likes, 0)::DOUBLE + COALESCE(comments, 0)::DOUBLE + COALESCE(shares, 0)::DOUBLE) / views
            ELSE 0.0
        END AS calculated_engagement_rate,
        -- Platform-specific data
        privacy_status,
        -- Account metrics
        COALESCE(subscribers, 0) AS channel_subscribers,
        COALESCE(total_videos, 0) AS channel_total_videos
    FROM youtube_videos_source
)

SELECT
    page_id,
    page_name,
    post_id,
    post_message,
    created_timestamp,
    platform,
    clicks,
    impressions,
    likes,
    shares,
    comments,
    post_url,
    calculated_engagement_rate,
    privacy_status,
    channel_subscribers,
    channel_total_videos,
    -- Derived performance metrics
    CASE
        WHEN COALESCE(channel_subscribers, 0) > 0
        THEN clicks::DOUBLE / channel_subscribers
        ELSE 0.0
    END AS views_per_subscriber,
    CASE
        WHEN COALESCE(clicks, 0) > 0
        THEN COALESCE(likes, 0)::DOUBLE / clicks
        ELSE 0.0
    END AS likes_per_view_ratio
FROM youtube_standardized
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 152 | 152 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"post_id":"-kb60w6ipkw"}</code> |
| K2 | <code>{"post_id":"-oa0mqiurga"}</code> |
| K3 | <code>{"post_id":"-tc7y7mngix"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| post_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| calculated_engagement_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| channel_subscribers | 0 | 0 | 0 | DOUBLE | DOUBLE |
| channel_total_videos | 0 | 0 | 0 | INTEGER | INTEGER |
| clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| comments | 0 | 0 | 0 | BIGINT | BIGINT |
| created_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| likes | 0 | 0 | 0 | BIGINT | BIGINT |
| likes_per_view_ratio | 0 | 0 | 0 | DOUBLE | DOUBLE |
| page_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| page_name | 152 | 152 | 152 | VARCHAR | VARCHAR |
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| post_message | 0 | 0 | 0 | VARCHAR | VARCHAR |
| post_url | 0 | 0 | 0 | VARCHAR | VARCHAR |
| privacy_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| shares | 0 | 0 | 0 | BIGINT | BIGINT |
| views_per_subscriber | 0 | 0 | 0 | DOUBLE | DOUBLE |

page_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Sutxpa integration cjlhtnwp | Unknown Channel |
| K2 | Vzibi nhg API | Unknown Channel |
| K3 | Api vyguhpw database jshwdnm | Unknown Channel |

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
| B6_constant_literal_output | <code>2输出列；[{"column":"platform","expression":["CAST('youtube' AS TEXT)"]},{"column":"channel_total_videos","expression":["CAST(0 AS INT)"]}]</code> |
| C9_agent_runtime_text | <code>S4:6 current_date；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:24 CURRENT_DATE；命中数=1</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory     from intermediate.social_media_reporting__youtube_videos_reporting where created_timestamp is not null</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 2094 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9937 | true | false |
| 15 | run | <code>sed -n '220,520p' docs/data_contract.yaml</code> | 16556 | false | false |
| 17 | run | <code>sed -n '520,790p' docs/data_contract.yaml</code> | 19316 | true | false |
| 19 | run | <code>sed -n '790,1010p' docs/data_contract.yaml</code> | 14188 | true | false |
| 29 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/write_sql.py &lt;&lt;'PY'<br>from pathlib import Path<br>files={}<br>files['staging/stg_social_media__account_history.sql'] = '''select<br>    try_cast(id a</code> | 0 | false | false |
| 31 | run | <code>cat &gt;&gt; /tmp/write_sql.py &lt;&lt;'PY'<br>files['intermediate/social_media_reporting__facebook_posts_reporting.sql'] = '''with source_posts as (<br>    select<br>        cast(page_id as varchar) as page_id,<br>        p</code> | 0 | false | false |
| 33 | run | <code>cat &gt;&gt; /tmp/write_sql.py &lt;&lt;'PY'<br>files['marts/social_media_reporting__rollup_report.sql'] = '''with all_posts as (<br>    select page_id, page_name, post_id, post_message, created_timestamp, platform,<br>   </code> | 917 | true | false |
| 37 | run | <code>grep 'staging\.&#124;intermediate\.&#124;marts\.' /tmp/pipeline.log &#124; tail -35; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting.duckdb',read_only=True)<br>for schema in ['staging','intermedi</code> | 1464 | true | false |
| 49 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql').rglob('*.sql'):<br> s=p.read_text()<br> assert not s.rstrip().endswith(';'), p<br> assert 'ref(' not in s.lower(), p<br> print(f'{p}: {len(s.splitline</code> | 1600 | true | false |

### agent action 的 thought/message 命中原句

event 31 / message

```text
files['intermediate/social_media_reporting__youtube_videos_reporting.sql'] = '''with source_videos as (
```
event 33 / message

```text
    from intermediate.social_media_reporting__youtube_videos_reporting
```
event 33 / message

```text
    from intermediate.social_media_reporting__youtube_videos_reporting
```
event 33 / message

```text
    from intermediate.social_media_reporting__youtube_videos_reporting where created_timestamp is not null
```
event 33 / message

```text
    from intermediate.social_media_reporting__youtube_videos_reporting
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-023.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/intermediate/social_media_reporting__youtube_videos_reporting.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/intermediate/social_media_reporting__youtube_videos_reporting.sql`
- S6: `records/006_contract_impl-023.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/result.md`
- S10: `data/024_packages_work/024_impl-023_social_media_reporting__youtube_videos_reporting/024_impl-023_social_media_reporting__youtube_videos_reporting.json`
- S11: `data/011_agent_alignment/impl-023/social_media_reporting__youtube_videos_reporting_2025-10-17.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions`
