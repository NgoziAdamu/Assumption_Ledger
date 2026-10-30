# impl-023 | staging | stg_social_media__twitter_organic_tweets | 差异：S1；日期 2025-10-17

## 契约完整原文

S3:115–204

```yaml
    - name: stg_social_media__twitter_organic_tweets
      description: "Tweet-level organic performance records enriched with tweet text and user attributes; recent 2-year window."
      source_table: raw.organic_tweet_report
      notes:
        - "Rows restricted to last 2 years via: date >= CURRENT_DATE - INTERVAL '2 years'."
        - "Tweet text joined from raw.tweet.full_text; user attributes joined from raw.twitter_user_history."
        - "All metrics default to 0 when NULL."
        - "engagement_rate guarded against division by zero."
      columns:
        - name: account_id
          data_type: VARCHAR
        - name: date
          data_type: DATE
        - name: organic_tweet_id
          data_type: VARCHAR
          description: "CAST(o.organic_tweet_id AS VARCHAR)."
        - name: placement
          data_type: VARCHAR
        - name: _fivetran_synced
          data_type: TIMESTAMP
        - name: app_clicks
          data_type: BIGINT
        - name: card_engagements
          data_type: BIGINT
        - name: carousel_swipes
          data_type: BIGINT
        - name: clicks
          data_type: BIGINT
        - name: engagements
          data_type: BIGINT
        - name: follows
          data_type: BIGINT
        - name: impressions
          data_type: BIGINT
        - name: likes
          data_type: BIGINT
        - name: poll_card_vote
          data_type: BIGINT
        - name: qualified_impressions
          data_type: BIGINT
        - name: replies
          data_type: BIGINT
        - name: retweets
          data_type: BIGINT
        - name: tweets_send
          data_type: BIGINT
        - name: unfollows
          data_type: BIGINT
        - name: url_clicks
          data_type: BIGINT
        - name: video_15_s_views
          data_type: BIGINT
        - name: video_3_s_100_pct_views
          data_type: BIGINT
        - name: video_6_s_views
          data_type: BIGINT
        - name: video_content_starts
          data_type: BIGINT
        - name: video_cta_clicks
          data_type: BIGINT
        - name: video_total_views
          data_type: BIGINT
        - name: video_views_100
          data_type: BIGINT
        - name: video_views_25
          data_type: BIGINT
        - name: video_views_50
          data_type: BIGINT
        - name: video_views_75
          data_type: BIGINT
        - name: tweet_text
          data_type: VARCHAR
          description: "From raw.tweet.full_text."
        - name: screen_name
          data_type: VARCHAR
          description: "From raw.twitter_user_history.screen_name."
        - name: user_name
          data_type: VARCHAR
          description: "From raw.twitter_user_history.name."
        - name: lang
          data_type: VARCHAR
          description: "From raw.tweet.lang."
        - name: tweet_created_at
          data_type: TIMESTAMP
          description: "From raw.tweet.created_at."
        - name: engagement_rate
          data_type: DOUBLE
          description: "CASE WHEN impressions > 0 THEN engagements / impressions ELSE 0.0 END."


```

## agent 最终 SQL

S4

```sql
with organic as (
    select *
    from raw.organic_tweet_report
    where cast(date as date) >= current_date - interval '2 years'
),
tweets as (
    select
        try_cast(id as bigint) as tweet_id,
        full_test as tweet_text,
        lang,
        created_at as tweet_created_at
    from raw.tweet
),
users as (
    select *, row_number() over (partition by id order by _fivetran_synced desc nulls last) as row_num
    from raw.twitter_user_history
)
select
    o.account_id::varchar as account_id,
    cast(o.date as date) as date,
    cast(o.organic_tweet_id as varchar) as organic_tweet_id,
    o.placement::varchar as placement,
    o._fivetran_synced::timestamp as _fivetran_synced,
    coalesce(o.app_clicks, 0)::bigint as app_clicks,
    coalesce(o.card_engagements, 0)::bigint as card_engagements,
    coalesce(o.carousel_swipes, 0)::bigint as carousel_swipes,
    coalesce(o.clicks, 0)::bigint as clicks,
    coalesce(o.engagements, 0)::bigint as engagements,
    coalesce(o.follows, 0)::bigint as follows,
    coalesce(o.impressions, 0)::bigint as impressions,
    coalesce(o.likes, 0)::bigint as likes,
    coalesce(o.poll_card_vote, 0)::bigint as poll_card_vote,
    coalesce(o.qualified_impressions, 0)::bigint as qualified_impressions,
    coalesce(o.replies, 0)::bigint as replies,
    coalesce(o.retweets, 0)::bigint as retweets,
    coalesce(o.tweets_send, 0)::bigint as tweets_send,
    coalesce(o.unfollows, 0)::bigint as unfollows,
    coalesce(o.url_clicks, 0)::bigint as url_clicks,
    coalesce(o.video_15_s_views, 0)::bigint as video_15_s_views,
    coalesce(o.video_3_s_100_pct_views, 0)::bigint as video_3_s_100_pct_views,
    coalesce(o.video_6_s_views, 0)::bigint as video_6_s_views,
    coalesce(o.video_content_starts, 0)::bigint as video_content_starts,
    coalesce(o.video_cta_clicks, 0)::bigint as video_cta_clicks,
    coalesce(o.video_total_views, 0)::bigint as video_total_views,
    coalesce(o.video_views_100, 0)::bigint as video_views_100,
    coalesce(o.video_views_25, 0)::bigint as video_views_25,
    coalesce(o.video_views_50, 0)::bigint as video_views_50,
    coalesce(o.video_views_75, 0)::bigint as video_views_75,
    t.tweet_text::varchar as tweet_text,
    regexp_replace(u.screen_name, '[^A-Za-z0-9_]', '', 'g')::varchar as screen_name,
    u.name::varchar as user_name,
    t.lang::varchar as lang,
    t.tweet_created_at::timestamp as tweet_created_at,
    case when coalesce(o.impressions, 0) > 0
         then coalesce(o.engagements, 0)::double / o.impressions else 0.0 end as engagement_rate
from organic o
left join tweets t on try_cast(o.organic_tweet_id as bigint) = t.tweet_id
left join users u on u.id = o.account_id and u.row_num = 1
```

## gold SQL（仅供定位差异）

S5

```sql
WITH source_data AS (
    SELECT
        account_id,
        date,
        organic_tweet_id,
        placement,
        _fivetran_synced,
        app_clicks,
        card_engagements,
        carousel_swipes,
        clicks,
        engagements,
        follows,
        impressions,
        likes,
        poll_card_vote,
        qualified_impressions,
        replies,
        retweets,
        tweets_send,
        unfollows,
        url_clicks,
        video_15_s_views,
        video_3_s_100_pct_views,
        video_6_s_views,
        video_content_starts,
        video_cta_clicks,
        video_total_views,
        video_views_100,
        video_views_25,
        video_views_50,
        video_views_75
    FROM raw.organic_tweet_report
    WHERE date >= CURRENT_DATE - INTERVAL '2 years' -- Focus on recent data for analytics
),

-- Join with tweet details
tweet_details AS (
    SELECT
        t.id AS tweet_id,
        t.account_id,
        t.created_at,
        t.full_test AS tweet_text,
        t.favorite_count,
        t.retweet_count,
        t.lang,
        t.source,
        u.screen_name,
        u.name AS user_name
    FROM raw.tweet t
    LEFT JOIN raw.twitter_user_history u ON t.user_id = u.id
)

SELECT
    o.account_id,
    o.date,
    CAST(o.organic_tweet_id AS VARCHAR) AS organic_tweet_id,
    o.placement,
    o._fivetran_synced,
    COALESCE(o.app_clicks, 0) AS app_clicks,
    COALESCE(o.card_engagements, 0) AS card_engagements,
    COALESCE(o.carousel_swipes, 0) AS carousel_swipes,
    COALESCE(o.clicks, 0) AS clicks,
    COALESCE(o.engagements, 0) AS engagements,
    COALESCE(o.follows, 0) AS follows,
    COALESCE(o.impressions, 0) AS impressions,
    COALESCE(o.likes, 0) AS likes,
    COALESCE(o.poll_card_vote, 0) AS poll_card_vote,
    COALESCE(o.qualified_impressions, 0) AS qualified_impressions,
    COALESCE(o.replies, 0) AS replies,
    COALESCE(o.retweets, 0) AS retweets,
    COALESCE(o.tweets_send, 0) AS tweets_send,
    COALESCE(o.unfollows, 0) AS unfollows,
    COALESCE(o.url_clicks, 0) AS url_clicks,
    COALESCE(o.video_15_s_views, 0) AS video_15_s_views,
    COALESCE(o.video_3_s_100_pct_views, 0) AS video_3_s_100_pct_views,
    COALESCE(o.video_6_s_views, 0) AS video_6_s_views,
    COALESCE(o.video_content_starts, 0) AS video_content_starts,
    COALESCE(o.video_cta_clicks, 0) AS video_cta_clicks,
    COALESCE(o.video_total_views, 0) AS video_total_views,
    COALESCE(o.video_views_100, 0) AS video_views_100,
    COALESCE(o.video_views_25, 0) AS video_views_25,
    COALESCE(o.video_views_50, 0) AS video_views_50,
    COALESCE(o.video_views_75, 0) AS video_views_75,
    t.tweet_text,
    t.screen_name,
    t.user_name,
    t.lang,
    t.created_at AS tweet_created_at,
    -- Calculate engagement rate inline
    CASE
        WHEN COALESCE(o.impressions, 0) > 0
        THEN (o.engagements::DOUBLE / o.impressions)
        ELSE 0.0
    END AS engagement_rate
FROM source_data o
LEFT JOIN tweet_details t ON o.organic_tweet_id = t.tweet_id AND o.account_id = t.account_id
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 129 | 129 | 126 | 129 | 3 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| date | 0 | 0 | 0 | DATE | TIMESTAMP |
| placement | 0 | 0 | 0 | VARCHAR | VARCHAR |
| app_clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| card_engagements | 0 | 0 | 0 | BIGINT | BIGINT |
| carousel_swipes | 0 | 0 | 0 | BIGINT | BIGINT |
| clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| engagement_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| engagements | 0 | 0 | 0 | BIGINT | BIGINT |
| follows | 0 | 0 | 0 | BIGINT | BIGINT |
| impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| likes | 0 | 0 | 0 | BIGINT | BIGINT |
| poll_card_vote | 0 | 0 | 0 | BIGINT | BIGINT |
| qualified_impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| replies | 0 | 0 | 0 | BIGINT | BIGINT |
| retweets | 0 | 0 | 0 | BIGINT | BIGINT |
| tweets_send | 0 | 0 | 0 | BIGINT | BIGINT |
| unfollows | 0 | 0 | 0 | BIGINT | BIGINT |
| url_clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| video_15_s_views | 0 | 0 | 0 | BIGINT | BIGINT |
| video_3_s_100_pct_views | 0 | 0 | 0 | BIGINT | BIGINT |
| video_6_s_views | 0 | 0 | 0 | BIGINT | BIGINT |
| video_content_starts | 0 | 0 | 0 | BIGINT | BIGINT |
| video_cta_clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| video_total_views | 0 | 0 | 0 | BIGINT | BIGINT |
| video_views_100 | 0 | 0 | 0 | BIGINT | BIGINT |
| video_views_25 | 0 | 0 | 0 | BIGINT | BIGINT |
| video_views_50 | 0 | 0 | 0 | BIGINT | BIGINT |
| video_views_75 | 0 | 0 | 0 | BIGINT | BIGINT |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"account_id":"default_account","date":"2023-10-18","organic_tweet_id":"1.8777425272579647e+24","placement":"ALL_ON_TWITTER"},{"account_id":"default_account","date":"2023-10-18","organic_tweet_id":"4.7075236278081625e+24","placement":"ALL_ON_TWITTER"},{"account_id":"default_account","date":"2023-10-19","organic_tweet_id":"2.155524360829889e+24","placement":"ALL_ON_TWITTER"},{"account_id":"default_account","date":"2023-10-19","organic_tweet_id":"6.836875408877093e+23","placement":"ALL_ON_TWITTER"},{"account_id":"default_account","date":"2023-10-20","organic_tweet_id":"3.3443839821125597e+24","placement":"ALL_ON_TWITTER"}]</code> | <code>[{"account_id":"default_account","date":"2023-10-18 05:03:19","organic_tweet_id":"4.7075236278081625e+24","placement":"ALL_ON_TWITTER"},{"account_id":"default_account","date":"2023-10-18 16:08:54","organic_tweet_id":"1.8777425272579647e+24","placement":"ALL_ON_TWITTER"},{"account_id":"default_account","date":"2023-10-19 03:12:09","organic_tweet_id":"6.836875408877093e+23","placement":"ALL_ON_TWITTER"},{"account_id":"default_account","date":"2023-10-19 20:19:51","organic_tweet_id":"2.155524360829889e+24","placement":"ALL_ON_TWITTER"},{"account_id":"default_account","date":"2023-10-20 17:34:07","organic_tweet_id":"3.3443839821125597e+24","placement":"ALL_ON_TWITTER"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A1_zero_rows | 行数=0 |
| B7_read_not_specified | <code>["raw.tweet","raw.twitter_user_history"]</code> |
| C9_agent_runtime_text | <code>S4:4 current_date；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:34 CURRENT_DATE；命中数=1</code> |
| C9_contract_runtime_text | <code>S3:119 CURRENT_DATE；命中数=1</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 2094 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9937 | true | false |
| 13 | run | <code>wc -l docs/data_contract.yaml &amp;&amp; sed -n '1,240p' docs/data_contract.yaml</code> | 9685 | true | false |
| 17 | run | <code>sed -n '520,790p' docs/data_contract.yaml</code> | 19316 | true | false |
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
files['staging/stg_social_media__twitter_organic_tweets.sql'] = '''with organic as (
```
event 31 / message

```text
    from staging.stg_social_media__twitter_organic_tweets
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-023.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__twitter_organic_tweets.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__twitter_organic_tweets.sql`
- S6: `records/006_contract_impl-023.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/result.md`
- S10: `data/024_packages_work/024_impl-023_stg_social_media__twitter_organic_tweets/024_impl-023_stg_social_media__twitter_organic_tweets.json`
- S11: `data/011_agent_alignment/impl-023/stg_social_media__twitter_organic_tweets_2025-10-17.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions`
