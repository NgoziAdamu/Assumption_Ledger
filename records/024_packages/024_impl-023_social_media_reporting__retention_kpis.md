# impl-023 | marts | social_media_reporting__retention_kpis | 差异：S1；日期 原记录

## 契约完整原文

S3:869–916

```yaml
    - name: social_media_reporting__retention_kpis
      description: Weekly retention KPIs by platform using posting-activity cohorts over a fixed 13-week window
      grain: One row per platform per cohort_week per week_offset
      source_models:
      - intermediate.social_media_reporting__facebook_posts_reporting
      - intermediate.social_media_reporting__instagram_posts_reporting
      - intermediate.social_media_reporting__linkedin_posts_reporting
      - intermediate.social_media_reporting__twitter_posts_reporting
      - intermediate.social_media_reporting__youtube_videos_reporting
      business_logic: '- Inputs: - Union page activity from the five source models; only keep rows where created_timestamp is present. - Assign platform as one of: "facebook", "instagram", "linkedin", "twitter", "youtube". - Weekly normalization: - Bucket activity into ISO weeks starting Monday 00:00. - A page is considered active in a week if it posts at least once; multiple posts in the same week do not increase the activity count. - Cohorts: - For each (page_id, platform), set cohort_week to the earliest week with activity. - For each (platform, cohort_week), cohort_pages is the number of unique pages in that cohort. - Observation spine: - Generate week_offset values from 0 to 12 inclusive. - For each cohort, create 13 rows and set target_week to the start of the week that is week_offset weeks after cohort_week; when week_offset = 0, target_week equals cohort_week. - Activity presence: - Build distinct (platform, week, page_id) combinations so each active page-week is counted once. - Retention: - For each spine row, retained_pages is the number of unique pages active on the platform in target_week; this is not limited to members of the cohort. - KPI: - retention_rate = retained_pages divided by cohort_pages when cohort_pages > 0; otherwise 0.0. - No rounding; stored as double precision; values may exceed 1.0 due to the numerator scope. - Output: - Emit platform, cohort_week, week_offset, target_week, cohort_pages, retained_pages, retention_rate. - No explicit ordering is applied.'
      columns:
      - name: platform
        data_type: VARCHAR
        description: 'Platform name in lowercase: facebook, instagram, linkedin, twitter, or youtube'
        tests:
        - not_null
      - name: cohort_week
        data_type: DATE
        description: Start date (Monday) of the first week the page is active for the platform
        tests:
        - not_null
      - name: week_offset
        data_type: BIGINT
        description: Number of weeks since cohort_week, inclusive 0 to 12
        tests:
        - not_null
        - week_offset BETWEEN 0 AND 12
      - name: target_week
        data_type: TIMESTAMP
        description: Start-of-week timestamp at week_offset weeks after cohort_week; equals cohort_week when offset is 0
        tests:
        - not_null
      - name: cohort_pages
        data_type: BIGINT
        description: Unique pages in the cohort for each (platform, cohort_week)
        tests:
        - not_null
      - name: retained_pages
        data_type: BIGINT
        description: Unique pages active on the platform in target_week; one count per page-week; not limited to cohort members
        tests:
        - not_null
      - name: retention_rate
        data_type: DOUBLE
        description: Ratio of retained_pages to cohort_pages; if cohort_pages is 0 then 0.0; no rounding; may exceed 1.0
        tests:
        - not_null
        - retention_rate >= 0
```

## agent 最终 SQL

S4

```sql
with page_activity as (
    select 'facebook'::varchar as platform, page_id, date_trunc('week', created_timestamp)::date as activity_week
    from intermediate.social_media_reporting__facebook_posts_reporting where created_timestamp is not null
    union all
    select 'instagram', page_id, date_trunc('week', created_timestamp)::date
    from intermediate.social_media_reporting__instagram_posts_reporting where created_timestamp is not null
    union all
    select 'linkedin', page_id, date_trunc('week', created_timestamp)::date
    from intermediate.social_media_reporting__linkedin_posts_reporting where created_timestamp is not null
    union all
    select 'twitter', page_id, date_trunc('week', created_timestamp)::date
    from intermediate.social_media_reporting__twitter_posts_reporting where created_timestamp is not null
    union all
    select 'youtube', page_id, date_trunc('week', created_timestamp)::date
    from intermediate.social_media_reporting__youtube_videos_reporting where created_timestamp is not null
),
active_page_weeks as (
    select distinct platform, activity_week, page_id
    from page_activity
    where page_id is not null
),
page_cohorts as (
    select platform, page_id, min(activity_week) as cohort_week
    from active_page_weeks
    group by platform, page_id
),
cohort_sizes as (
    select platform, cohort_week, count(distinct page_id)::bigint as cohort_pages
    from page_cohorts
    group by platform, cohort_week
),
cohort_spine as (
    select c.platform, c.cohort_week, offsets.week_offset::bigint as week_offset,
           (c.cohort_week + offsets.week_offset * interval '1 week')::timestamp as target_week,
           c.cohort_pages
    from cohort_sizes c,
         unnest(range(0, 13)) as offsets(week_offset)
),
weekly_activity as (
    select platform, activity_week, count(distinct page_id)::bigint as retained_pages
    from active_page_weeks
    group by platform, activity_week
)
select
    s.platform,
    s.cohort_week,
    s.week_offset,
    s.target_week,
    s.cohort_pages,
    coalesce(a.retained_pages, 0)::bigint as retained_pages,
    case when s.cohort_pages > 0 then coalesce(a.retained_pages, 0)::double / s.cohort_pages else 0.0 end as retention_rate
from cohort_spine s
left join weekly_activity a
    on a.platform = s.platform and a.activity_week = cast(s.target_week as date)
```

## gold SQL（仅供定位差异）

S5

```sql
-- Retention KPIs by platform using posting activity cohorts (marts)
-- Layer: marts (may only reference intermediate.*)
-- Cohort: first week a page_id posts on a platform
-- Retention window: 0..12 weeks after cohort_week
-- Constraints: denominator > 0 (cohort_pages), date continuity ensured via week spine per cohort

WITH unified AS (
    SELECT page_id, created_timestamp, 'facebook' AS platform
    FROM intermediate.social_media_reporting__facebook_posts_reporting
    WHERE created_timestamp IS NOT NULL

    UNION ALL
    SELECT page_id, created_timestamp, 'instagram' AS platform
    FROM intermediate.social_media_reporting__instagram_posts_reporting
    WHERE created_timestamp IS NOT NULL

    UNION ALL
    SELECT page_id, created_timestamp, 'linkedin' AS platform
    FROM intermediate.social_media_reporting__linkedin_posts_reporting
    WHERE created_timestamp IS NOT NULL

    UNION ALL
    SELECT page_id, created_timestamp, 'twitter' AS platform
    FROM intermediate.social_media_reporting__twitter_posts_reporting
    WHERE created_timestamp IS NOT NULL

    UNION ALL
    SELECT page_id, created_timestamp, 'youtube' AS platform
    FROM intermediate.social_media_reporting__youtube_videos_reporting
    WHERE created_timestamp IS NOT NULL
),

posts_by_week AS (
    SELECT
        page_id,
        platform,
        DATE_TRUNC('week', created_timestamp) AS week,
        COUNT(*) AS posts_in_week
    FROM unified
    GROUP BY page_id, platform, DATE_TRUNC('week', created_timestamp)
),

cohorts AS (
    SELECT
        page_id,
        platform,
        MIN(week) AS cohort_week
    FROM posts_by_week
    GROUP BY page_id, platform
),

cohort_sizes AS (
    SELECT platform, cohort_week, COUNT(DISTINCT page_id) AS cohort_pages
    FROM cohorts
    GROUP BY platform, cohort_week
),

week_span AS (
    -- Determine overall min/max weeks for generating spines
    SELECT MIN(week) AS min_week, MAX(week) AS max_week FROM posts_by_week
),

span_numbers AS (
    -- 0..12 weeks window offsets
    SELECT i AS week_offset FROM range(0, 13) AS r(i)
),

cohort_week_spine AS (
    -- For each cohort, create target weeks = cohort_week + offset
    SELECT
        c.platform,
        c.cohort_week,
        s.week_offset,
        c.cohort_week + (s.week_offset || ' weeks')::INTERVAL AS target_week
    FROM cohorts c
    CROSS JOIN span_numbers s
),

activity AS (
    SELECT
        p.platform,
        p.week AS activity_week,
        p.page_id
    FROM posts_by_week p
    GROUP BY p.platform, p.week, p.page_id
),

retention AS (
    SELECT
        spine.platform,
        spine.cohort_week,
        spine.week_offset,
        spine.target_week,
        COUNT(DISTINCT a.page_id) AS retained_pages
    FROM cohort_week_spine spine
    LEFT JOIN activity a
      ON a.platform = spine.platform
     AND a.activity_week = spine.target_week
    GROUP BY spine.platform, spine.cohort_week, spine.week_offset, spine.target_week
),

final_retention AS (
    SELECT
        r.platform,
        r.cohort_week,
        r.week_offset,
        r.target_week,
        cs.cohort_pages,
        r.retained_pages,
        CASE
            WHEN cs.cohort_pages > 0 THEN r.retained_pages::DOUBLE / cs.cohort_pages
            ELSE 0.0
        END AS retention_rate
    FROM retention r
    LEFT JOIN cohort_sizes cs
      ON cs.platform = r.platform AND cs.cohort_week = r.cohort_week
)

SELECT *
FROM final_retention
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 312 | 325 | 0 | 13 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| cohort_week | 0 | 0 | 0 | DATE | DATE |
| week_offset | 0 | 0 | 0 | BIGINT | BIGINT |
| target_week | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| cohort_pages | 0 | 0 | 0 | BIGINT | BIGINT |
| retained_pages | 0 | 0 | 0 | BIGINT | BIGINT |
| retention_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"platform":"youtube","cohort_week":"2023-10-16","week_offset":"0","target_week":"2023-10-16 00:00:00","cohort_pages":"0","retained_pages":"0","retention_rate":"0.0"},{"platform":"youtube","cohort_week":"2023-10-16","week_offset":"1","target_week":"2023-10-23 00:00:00","cohort_pages":"0","retained_pages":"0","retention_rate":"0.0"},{"platform":"youtube","cohort_week":"2023-10-16","week_offset":"10","target_week":"2023-12-25 00:00:00","cohort_pages":"0","retained_pages":"0","retention_rate":"0.0"},{"platform":"youtube","cohort_week":"2023-10-16","week_offset":"11","target_week":"2024-01-01 00:00:00","cohort_pages":"0","retained_pages":"0","retention_rate":"0.0"},{"platform":"youtube","cohort_week":"2023-10-16","week_offset":"12","target_week":"2024-01-08 00:00:00","cohort_pages":"0","retained_pages":"0","retention_rate":"0.0"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A1_zero_rows | 行数=0 |
| B6_constant_literal_output | <code>1输出列；[{"column":"platform","expression":["CAST('facebook' AS TEXT)"]}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 2094 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9937 | false | false |
| 15 | run | <code>sed -n '220,520p' docs/data_contract.yaml</code> | 16556 | false | false |
| 17 | run | <code>sed -n '520,790p' docs/data_contract.yaml</code> | 19316 | false | false |
| 19 | run | <code>sed -n '790,1010p' docs/data_contract.yaml</code> | 14188 | true | false |
| 31 | run | <code>cat &gt;&gt; /tmp/write_sql.py &lt;&lt;'PY'<br>files['intermediate/social_media_reporting__facebook_posts_reporting.sql'] = '''with source_posts as (<br>    select<br>        cast(page_id as varchar) as page_id,<br>        p</code> | 0 | false | false |
| 33 | run | <code>cat &gt;&gt; /tmp/write_sql.py &lt;&lt;'PY'<br>files['marts/social_media_reporting__rollup_report.sql'] = '''with all_posts as (<br>    select page_id, page_name, post_id, post_message, created_timestamp, platform,<br>   </code> | 917 | true | false |
| 37 | run | <code>grep 'staging\.&#124;intermediate\.&#124;marts\.' /tmp/pipeline.log &#124; tail -35; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting.duckdb',read_only=True)<br>for schema in ['staging','intermedi</code> | 1464 | true | false |
| 41 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting.duckdb',read_only=True)<br>for t in ['stg_social_media__linkedin_posts','social_media_reporting__linkedin_posts_reporting']:<br> print(</code> | 977 | false | false |
| 49 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql').rglob('*.sql'):<br> s=p.read_text()<br> assert not s.rstrip().endswith(';'), p<br> assert 'ref(' not in s.lower(), p<br> print(f'{p}: {len(s.splitline</code> | 1600 | true | false |

### agent action 的 thought/message 命中原句

event 33 / message

```text
files['marts/social_media_reporting__retention_kpis.sql'] = '''with page_activity as (
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-023.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/marts/social_media_reporting__retention_kpis.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/marts/social_media_reporting__retention_kpis.sql`
- S6: `records/006_contract_impl-023.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/result.md`
- S10: `data/024_packages_work/024_impl-023_social_media_reporting__retention_kpis/024_impl-023_social_media_reporting__retention_kpis.json`
- S11: `data/005_cs_work/impl-023_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions`
