# impl-023 | staging | stg_social_media__facebook_posts | 差异：S1；日期 2025-10-17

## 契约完整原文

S3:205–255

```yaml
    - name: stg_social_media__facebook_posts
      description: "Published, visible Facebook posts joined to page info, standardized fields for analysis; recent 2-year window."
      source_table: 
        - raw.facebook_pages_post_history
        - raw.facebook_pages_page_data
      columns:
        - name: id
          data_type: VARCHAR
        - name: created_timestamp
          data_type: TIMESTAMP
          description: "From created_time."
        - name: post_id
          data_type: VARCHAR
          description: "CAST(id)."
        - name: post_message
          data_type: VARCHAR
          description: "COALESCE(message, '')."
        - name: page_id
          data_type: VARCHAR
          description: "CAST(page_id)."
        - name: page_name
          data_type: VARCHAR
          validation_rules:
            - rule: "page_name IS NOT NULL AND page_name <> ''"
              on_failure: correct  
          description: "Defaults to 'Unknown Page' when page name is missing."
        - name: page_username
          data_type: VARCHAR
        - name: page_category
          data_type: VARCHAR
        - name: page_followers
          data_type: BIGINT
        - name: shares
          data_type: BIGINT
        - name: impressions
          data_type: BIGINT
          description: "Default 0 in staging."
        - name: status_type
          data_type: VARCHAR
        - name: privacy_value
          data_type: VARCHAR
        - name: is_eligible_for_promotion
          data_type: BOOLEAN
        - name: is_instagram_eligible
          data_type: BOOLEAN
        - name: post_url
          data_type: VARCHAR
          validation_rules:
            - rule: "post_url ~ '^https://facebook\\.com/.+'"
              on_failure: correct

```

## agent 最终 SQL

S4

```sql
with post_metrics as (
    select post_id, max(post_impressions) as impressions
    from raw.facebook_pages_lifetime_post_metrics
    group by post_id
), pages as (
    select *, row_number() over (partition by id order by _fivetran_synced desc nulls last) as row_num
    from raw.facebook_pages_page_data
)
select
    p.id::varchar as id,
    p.created_time::timestamp as created_timestamp,
    p.id::varchar as post_id,
    coalesce(p.message, '')::varchar as post_message,
    cast(p.page_id as varchar) as page_id,
    coalesce(nullif(pg.name, ''), 'Unknown Page')::varchar as page_name,
    pg.username::varchar as page_username,
    pg.category::varchar as page_category,
    coalesce(try_cast(pg.fan_count as bigint), 0)::bigint as page_followers,
    coalesce(p.share_count, 0)::bigint as shares,
    coalesce(pm.impressions, 0)::bigint as impressions,
    p.status_type::varchar as status_type,
    p.privacy_value::varchar as privacy_value,
    p.is_eligible_for_promotion::boolean as is_eligible_for_promotion,
    p.is_instagram_eligible::boolean as is_instagram_eligible,
    ('https://facebook.com/' || p.id)::varchar as post_url
from raw.facebook_pages_post_history p
left join pages pg on p.page_id = pg.id and pg.row_num = 1
left join post_metrics pm on pm.post_id = p.id
where coalesce(p.is_published, false)
  and not coalesce(p.is_hidden, false)
  and p.created_time >= current_date - interval '2 years'
  and p.created_time is not null
```

## gold SQL（仅供定位差异）

S5

```sql
-- Facebook posts staging table - Simplified version based on actual columns
-- Created based on real table structure analysis

WITH source_posts AS (
    SELECT
        id,
        created_time,
        page_id,
        status_type,
        message,
        share_count,
        is_published,
        privacy_value,
        is_hidden,
        is_eligible_for_promotion,
        is_instagram_eligible
    FROM raw.facebook_pages_post_history
    WHERE is_published = TRUE -- Only published posts
    AND is_hidden = FALSE -- Not hidden
    AND created_time >= CURRENT_DATE - INTERVAL '2 years' -- Recent posts only
),

-- Get page information
page_info AS (
    SELECT
        id AS page_id,
        name AS page_name,
        username,
        website,
        category,
        fan_count,
        talking_about_count,
        created_time AS page_created_time
    FROM raw.facebook_pages_page_data
    WHERE (_fivetran_deleted = FALSE OR _fivetran_deleted IS NULL)
        AND name IS NOT NULL -- Ensure page has a name
)

-- Simplified join just to get basic page info
SELECT
    sp.id,
    sp.created_time AS created_timestamp,
    CAST(sp.id AS VARCHAR) AS post_id,
    COALESCE(sp.message, '') AS post_message,
    CAST(sp.page_id AS VARCHAR) AS page_id,
    COALESCE(pi.page_name, 'Unknown Page') AS page_name,
    pi.username AS page_username,
    pi.category AS page_category,
    COALESCE(pi.fan_count, 0) AS page_followers,
    COALESCE(sp.share_count, 0) AS shares,
    0 AS impressions,
    sp.status_type,
    sp.privacy_value,
    sp.is_eligible_for_promotion,
    sp.is_instagram_eligible,
    CONCAT('https://facebook.com/', COALESCE(pi.page_id, sp.page_id), '/posts/', sp.id) AS post_url
FROM source_posts sp
LEFT JOIN page_info pi ON sp.page_id = pi.page_id
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 138 | 138 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"id":"514435155248890_7150369778798122"}</code> |
| K2 | <code>{"id":"514435155248892_2419193699044444"}</code> |
| K3 | <code>{"id":"514435155248895_2895703078598069"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| impressions | 0 | 0 | 0 | BIGINT | INTEGER |
| is_eligible_for_promotion | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_instagram_eligible | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| page_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| page_followers | 138 | 138 | 138 | BIGINT | DOUBLE |
| page_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| page_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| page_username | 0 | 0 | 0 | VARCHAR | VARCHAR |
| post_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| post_message | 0 | 0 | 0 | VARCHAR | VARCHAR |
| post_url | 138 | 138 | 138 | VARCHAR | VARCHAR |
| privacy_value | 0 | 0 | 0 | VARCHAR | VARCHAR |
| shares | 0 | 0 | 0 | BIGINT | BIGINT |
| status_type | 0 | 0 | 0 | VARCHAR | VARCHAR |

page_followers 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 15072 | 15072.0 |
| K2 | 4140 | 4140.0 |
| K3 | 6710 | 6710.0 |

post_url 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | https://facebook.com/514435155248890_7150369778798122 | https://facebook.com/514435155250268/posts/514435155248890_7150369778798122 |
| K2 | https://facebook.com/514435155248892_2419193699044444 | https://facebook.com/514435155251029/posts/514435155248892_2419193699044444 |
| K3 | https://facebook.com/514435155248895_2895703078598069 | https://facebook.com/514435155250947/posts/514435155248895_2895703078598069 |

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
| B7_read_not_specified | <code>["raw.facebook_pages_lifetime_post_metrics"]</code> |
| C9_agent_runtime_text | <code>S4:31 current_date；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:20 CURRENT_DATE；命中数=1</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 2094 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9937 | true | false |
| 11 | run | <code>sed -n '1,220p' social_media_reporting_start.yaml</code> | 6432 | false | false |
| 13 | run | <code>wc -l docs/data_contract.yaml &amp;&amp; sed -n '1,240p' docs/data_contract.yaml</code> | 9685 | true | false |
| 15 | run | <code>sed -n '220,520p' docs/data_contract.yaml</code> | 16556 | true | false |
| 23 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb',read_only=True)<br>for t, in c.execute("select table_name from information_schema.tables where table_schema='raw' orde</code> | 30939 | false | false |
| 29 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/write_sql.py &lt;&lt;'PY'<br>from pathlib import Path<br>files={}<br>files['staging/stg_social_media__account_history.sql'] = '''select<br>    try_cast(id a</code> | 0 | false | false |
| 31 | run | <code>cat &gt;&gt; /tmp/write_sql.py &lt;&lt;'PY'<br>files['intermediate/social_media_reporting__facebook_posts_reporting.sql'] = '''with source_posts as (<br>    select<br>        cast(page_id as varchar) as page_id,<br>        p</code> | 0 | false | false |
| 33 | run | <code>cat &gt;&gt; /tmp/write_sql.py &lt;&lt;'PY'<br>files['marts/social_media_reporting__rollup_report.sql'] = '''with all_posts as (<br>    select page_id, page_name, post_id, post_message, created_timestamp, platform,<br>   </code> | 917 | true | false |
| 37 | run | <code>grep 'staging\.&#124;intermediate\.&#124;marts\.' /tmp/pipeline.log &#124; tail -35; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting.duckdb',read_only=True)<br>for schema in ['staging','intermedi</code> | 1464 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb',read_only=True)<br>for t,col in [('account_history','timezone'),('facebook_pages_post_history','created_time'),('insta</code> | 1457 | false | false |
| 43 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb',read_only=True)<br>for t in ['account_history','organic_tweet_report','youtube_video','instagram_business_media_histor</code> | 4968 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb')<br>print('ids linkedin match',c.execute("select count(*) from raw.linkedin_pages_organization_ugc_post o join raw.lin</code> | 639 | false | false |
| 49 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql').rglob('*.sql'):<br> s=p.read_text()<br> assert not s.rstrip().endswith(';'), p<br> assert 'ref(' not in s.lower(), p<br> print(f'{p}: {len(s.splitline</code> | 1600 | true | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
files['staging/stg_social_media__facebook_posts.sql'] = '''with post_metrics as (
```
event 31 / message

```text
    from staging.stg_social_media__facebook_posts
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-023.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__facebook_posts.sql`
- S6: `records/006_contract_impl-023.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/result.md`
- S10: `records/012_packages/012_impl-023_staging_stg_social_media__facebook_posts.json`
- S11: `data/011_agent_alignment/impl-023/stg_social_media__facebook_posts_2025-10-17.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions`
