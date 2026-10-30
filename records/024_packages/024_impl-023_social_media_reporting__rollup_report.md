# impl-023 | marts | social_media_reporting__rollup_report | 差异：S1；日期 原记录

## 契约完整原文

S3:745–811

```yaml
    - name: social_media_reporting__rollup_report
      description: Unified cross-platform post/video rollup with standardized metrics, platform-specific quality score, rankings, and recent-window filtering
      grain: One row per platform + page_id + post_id
      source_models:
      - intermediate.social_media_reporting__facebook_posts_reporting
      - intermediate.social_media_reporting__instagram_posts_reporting
      - intermediate.social_media_reporting__linkedin_posts_reporting
      - intermediate.social_media_reporting__twitter_posts_reporting
      - intermediate.social_media_reporting__youtube_videos_reporting
      business_logic: '- Union all five platform models with a platform label: facebook, instagram, linkedin, twitter, youtube; select page_id, page_name, post_id, post_message, created_timestamp, clicks, impressions, likes, shares, comments, post_url. For YouTube, the upstream shares value maps to the unified shares position. - Filter out rows with NULL created_timestamp. - Apply recent data windows relative to the current date: - LinkedIn: keep the last 4 years. - All other platforms: keep the last 2 years. - Standardize content fields: - post_message: default NULL to empty string "". - post_url: default NULL to empty string "". - Standardize metric fields (clicks, impressions, likes, shares, comments): default NULL to 0; no aggregation or deduplication is performed. - Compute engagement_rate: - If impressions > 0: (clicks + likes + shares + comments) / impressions. - Otherwise: 0.0. - No rounding or capping; always non-null and may exceed 1.0. - Compute content_quality_score by platform: - facebook: 75 if impressions > 0, else 50. - instagram: 90 if impressions > 0, else 50. - twitter: 80 if impressions > 0, else 50. - youtube: 95 if clicks > 0, else 50. - linkedin: 70 if impressions > 0, else 50. - Rankings (computed after the above filtering): - daily_platform_rank: within each platform and calendar day of created_timestamp, assign a 1-based rank by sorting impressions descending; ties get arbitrary order. - platform_lifetime_rank: within each platform across the filtered dataset, assign a 1-based rank by sorting impressions descending; ties get arbitrary order. - Final result ordering for display: created_timestamp descending, then engagement_rate descending.'
      columns:
      - name: page_id
        data_type: VARCHAR
        description: Source page/account identifier within a platform
        tests:
        - not_null
      - name: page_name
        data_type: VARCHAR
        description: Source page/account display name; may be null
      - name: post_id
        data_type: VARCHAR
        description: Source post/media identifier within platform and page
        tests:
        - not_null
      - name: created_timestamp
        data_type: TIMESTAMP
        description: Post/media publish timestamp; rows with NULL are excluded
        tests:
        - not_null
      - name: platform
        data_type: VARCHAR
        description: 'Platform label: facebook, instagram, linkedin, twitter, youtube'
        tests:
        - not_null
      - name: post_message
        data_type: VARCHAR
        description: Post/media text; NULL defaults to empty string; casing and whitespace preserved
      - name: post_url
        data_type: VARCHAR
        description: Canonical post/media URL; NULL defaults to empty string; casing and whitespace preserved
      - name: clicks
        data_type: HUGEINT
        description: Total clicks; NULL defaults to 0; used in engagement_rate and YouTube quality rule
      - name: impressions
        data_type: HUGEINT
        description: Total impressions; NULL defaults to 0; denominator for engagement_rate and several quality rules
      - name: likes
        data_type: HUGEINT
        description: Total likes; NULL defaults to 0; included in engagement_rate numerator
      - name: shares
        data_type: HUGEINT
        description: Total shares; NULL defaults to 0; included in engagement_rate numerator; for YouTube, upstream shares are used
      - name: comments
        data_type: HUGEINT
        description: Total comments; NULL defaults to 0; included in engagement_rate numerator
      - name: engagement_rate
        data_type: DOUBLE
        description: If impressions > 0, (clicks + likes + shares + comments) / impressions; else 0.0; not rounded or capped; never null
      - name: content_quality_score
        data_type: INTEGER
        description: 'Platform rule-based score: FB 75 if impressions > 0; IG 90 if impressions > 0; TW 80 if impressions > 0; YT 95 if clicks > 0; LI 70 if impressions > 0; otherwise 50'
      - name: daily_platform_rank
        data_type: BIGINT
        description: 1-based rank within each platform and calendar day by impressions descending; ties receive arbitrary order
      - name: platform_lifetime_rank
        data_type: BIGINT
        description: 1-based rank within each platform across the filtered dataset by impressions descending; ties receive arbitrary order
```

## agent 最终 SQL

S4

```sql
with all_posts as (
    select page_id, page_name, post_id, post_message, created_timestamp, platform,
           clicks, impressions, likes, shares, comments, post_url
    from intermediate.social_media_reporting__facebook_posts_reporting
    union all
    select page_id, page_name, post_id, post_message, created_timestamp, platform,
           clicks, impressions, likes, shares, comments, post_url
    from intermediate.social_media_reporting__instagram_posts_reporting
    union all
    select page_id, page_name, post_id, post_message, created_timestamp, platform,
           clicks, impressions, likes, shares, comments, post_url
    from intermediate.social_media_reporting__linkedin_posts_reporting
    union all
    select page_id, page_name, post_id, post_message, created_timestamp, platform,
           clicks, impressions, likes, shares, comments, post_url
    from intermediate.social_media_reporting__twitter_posts_reporting
    union all
    select page_id, page_name, post_id, post_message, created_timestamp, platform,
           clicks, impressions, likes, shares, comments, post_url
    from intermediate.social_media_reporting__youtube_videos_reporting
),
recent_posts as (
    select
        page_id, page_name, post_id, coalesce(post_message, '')::varchar as post_message,
        created_timestamp, platform,
        coalesce(clicks, 0)::hugeint as clicks,
        coalesce(impressions, 0)::hugeint as impressions,
        coalesce(likes, 0)::hugeint as likes,
        coalesce(shares, 0)::hugeint as shares,
        coalesce(comments, 0)::hugeint as comments,
        coalesce(post_url, '')::varchar as post_url
    from all_posts
    where created_timestamp is not null
      and ((platform = 'linkedin' and created_timestamp >= current_date - interval '4 years')
        or (platform <> 'linkedin' and created_timestamp >= current_date - interval '2 years'))
),
scored_posts as (
    select *,
        case when impressions > 0 then (clicks + likes + shares + comments)::double / impressions else 0.0 end as engagement_rate,
        case platform
            when 'facebook' then case when impressions > 0 then 75 else 50 end
            when 'instagram' then case when impressions > 0 then 90 else 50 end
            when 'twitter' then case when impressions > 0 then 80 else 50 end
            when 'youtube' then case when clicks > 0 then 95 else 50 end
            when 'linkedin' then case when impressions > 0 then 70 else 50 end
            else 50 end::integer as content_quality_score
    from recent_posts
),
ranked_posts as (
    select *,
        row_number() over (partition by platform, cast(created_timestamp as date) order by impressions desc) as daily_platform_rank,
        row_number() over (partition by platform order by impressions desc) as platform_lifetime_rank
    from scored_posts
)
select
    page_id, page_name, post_id, created_timestamp, platform, post_message, post_url,
    clicks, impressions, likes, shares, comments, engagement_rate, content_quality_score,
    daily_platform_rank, platform_lifetime_rank
from ranked_posts
order by created_timestamp desc, engagement_rate desc
```

## gold SQL（仅供定位差异）

S5

```sql
-- Social media unified rollup report
-- Combines all platform data into a single unified reporting table

WITH unified_data AS (
    -- Facebook data
    SELECT
        page_id,
        page_name,
        post_id,
        post_message,
        created_timestamp,
        'facebook' AS platform,
        clicks,
        impressions,
        likes,
        shares,
        comments,
        post_url
    FROM intermediate.social_media_reporting__facebook_posts_reporting

    UNION ALL

    -- Instagram data
    SELECT
        page_id,
        page_name,
        post_id,
        post_message,
        created_timestamp,
        'instagram' AS platform,
        clicks,
        impressions,
        likes,
        shares,
        comments,
        post_url
    FROM intermediate.social_media_reporting__instagram_posts_reporting

    UNION ALL

    -- LinkedIn data
    SELECT
        page_id,
        page_name,
        post_id,
        post_message,
        created_timestamp,
        'linkedin' AS platform,
        clicks,
        impressions,
        likes,
        shares,
        comments,
        post_url
    FROM intermediate.social_media_reporting__linkedin_posts_reporting

    UNION ALL

    -- Twitter data
    SELECT
        page_id,
        page_name,
        post_id,
        post_message,
        created_timestamp,
        'twitter' AS platform,
        clicks,
        impressions,
        likes,
        shares,
        comments,
        post_url
    FROM intermediate.social_media_reporting__twitter_posts_reporting

    UNION ALL

    -- YouTube data
    SELECT
        page_id,
        page_name,
        post_id,
        post_message,
        created_timestamp,
        'youtube' AS platform,
        clicks,
        impressions,
        likes,
        shares AS estimated_shares,
        comments,
        post_url
    FROM intermediate.social_media_reporting__youtube_videos_reporting
)

-- Final unified rollup
SELECT
    -- Primary identifiers
    page_id,
    page_name,
    post_id,
    created_timestamp,
    platform,

    -- Unified content metrics
    COALESCE(post_message, '') AS post_message,
    COALESCE(post_url, '') AS post_url,

    -- Standardized engagement metrics
    COALESCE(clicks, 0) AS clicks,
    COALESCE(impressions, 0) AS impressions,
    COALESCE(likes, 0) AS likes,
    COALESCE(shares, 0) AS shares,
    COALESCE(comments, 0) AS comments,

    -- Engagement metrics
    CASE
        WHEN COALESCE(impressions, 0) > 0
        THEN (COALESCE(clicks, 0)::DOUBLE + COALESCE(likes, 0)::DOUBLE + COALESCE(shares, 0)::DOUBLE + COALESCE(comments, 0)::DOUBLE) / impressions
        ELSE 0.0
    END AS engagement_rate,

    -- Platform-based quality score
    CASE
        WHEN platform = 'facebook' AND COALESCE(impressions, 0) > 0 THEN 75
        WHEN platform = 'instagram' AND COALESCE(impressions, 0) > 0 THEN 90
        WHEN platform = 'twitter' AND COALESCE(impressions, 0) > 0 THEN 80
        WHEN platform = 'youtube' AND COALESCE(clicks, 0) > 0 THEN 95
        WHEN platform = 'linkedin' AND COALESCE(impressions, 0) > 0 THEN 70
        ELSE 50
    END AS content_quality_score,

    -- Per-platform rankings
    ROW_NUMBER() OVER (PARTITION BY platform, DATE_TRUNC('day', created_timestamp) ORDER BY impressions DESC) AS daily_platform_rank,
    ROW_NUMBER() OVER (PARTITION BY platform ORDER BY impressions DESC) AS platform_lifetime_rank

FROM unified_data
WHERE (
    platform <> 'linkedin' AND created_timestamp >= CURRENT_DATE - INTERVAL '2 years'
) OR (
    platform = 'linkedin' AND created_timestamp >= CURRENT_DATE - INTERVAL '4 years'
) -- Recent data windows by platform
AND created_timestamp IS NOT NULL
ORDER BY created_timestamp DESC, engagement_rate DESC
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 0 | 584 | 0 | 584 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| page_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| post_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| clicks | 0 | 0 | 0 | HUGEINT | HUGEINT |
| impressions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| likes | 0 | 0 | 0 | HUGEINT | HUGEINT |
| shares | 0 | 0 | 0 | HUGEINT | HUGEINT |
| comments | 0 | 0 | 0 | HUGEINT | HUGEINT |
| engagement_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| content_quality_score | 0 | 0 | 0 | INTEGER | INTEGER |
| daily_platform_rank | 0 | 0 | 0 | BIGINT | BIGINT |
| platform_lifetime_rank | 0 | 0 | 0 | BIGINT | BIGINT |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"page_id":"10429","post_id":"urn:li:share:1034655442"},{"page_id":"10429","post_id":"urn:li:share:1034687017"},{"page_id":"10429","post_id":"urn:li:share:1035074525"},{"page_id":"10429","post_id":"urn:li:share:1044049823"},{"page_id":"10429","post_id":"urn:li:share:1044056016"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A1_zero_rows | 行数=0 |
| C9_agent_runtime_text | <code>S4:34 current_date；命中数=2</code> |
| C9_gold_runtime_text | <code>S5:137 CURRENT_DATE；命中数=2</code> |
| C9_contract_runtime_text | <code>S3:754 current date；命中数=1</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 2094 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9937 | false | false |
| 15 | run | <code>sed -n '220,520p' docs/data_contract.yaml</code> | 16556 | false | false |
| 17 | run | <code>sed -n '520,790p' docs/data_contract.yaml</code> | 19316 | true | false |
| 19 | run | <code>sed -n '790,1010p' docs/data_contract.yaml</code> | 14188 | false | false |
| 21 | run | <code>find sql -maxdepth 3 -type f -ls; sed -n '220,420p' run.py</code> | 8672 | true | false |
| 31 | run | <code>cat &gt;&gt; /tmp/write_sql.py &lt;&lt;'PY'<br>files['intermediate/social_media_reporting__facebook_posts_reporting.sql'] = '''with source_posts as (<br>    select<br>        cast(page_id as varchar) as page_id,<br>        p</code> | 0 | false | false |
| 33 | run | <code>cat &gt;&gt; /tmp/write_sql.py &lt;&lt;'PY'<br>files['marts/social_media_reporting__rollup_report.sql'] = '''with all_posts as (<br>    select page_id, page_name, post_id, post_message, created_timestamp, platform,<br>   </code> | 917 | true | false |
| 37 | run | <code>grep 'staging\.&#124;intermediate\.&#124;marts\.' /tmp/pipeline.log &#124; tail -35; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting.duckdb',read_only=True)<br>for schema in ['staging','intermedi</code> | 1464 | true | false |
| 41 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting.duckdb',read_only=True)<br>for t in ['stg_social_media__linkedin_posts','social_media_reporting__linkedin_posts_reporting']:<br> print(</code> | 977 | false | false |
| 49 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql').rglob('*.sql'):<br> s=p.read_text()<br> assert not s.rstrip().endswith(';'), p<br> assert 'ref(' not in s.lower(), p<br> print(f'{p}: {len(s.splitline</code> | 1600 | true | false |

### agent action 的 thought/message 命中原句

event 33 / message

```text
files['marts/social_media_reporting__rollup_report.sql'] = '''with all_posts as (
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-023.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/marts/social_media_reporting__rollup_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/marts/social_media_reporting__rollup_report.sql`
- S6: `records/006_contract_impl-023.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/result.md`
- S10: `data/024_packages_work/024_impl-023_social_media_reporting__rollup_report/024_impl-023_social_media_reporting__rollup_report.json`
- S11: `data/005_cs_work/impl-023_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions`
