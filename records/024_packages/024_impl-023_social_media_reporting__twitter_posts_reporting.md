# impl-023 | intermediate | social_media_reporting__twitter_posts_reporting | 差异：S1；日期 原记录

## 契约完整原文

S3:617–676

```yaml
    - name: social_media_reporting__twitter_posts_reporting
      description: Standardizes organic Twitter tweet metrics into one row per tweet and account with summed counts, averaged engagement rate, and canonical URL
      grain: One row per post_id (organic_tweet_id) per page_id (account_id)
      source_models:
      - staging.stg_social_media__twitter_organic_tweets
      business_logic: '- Input: include only records where organic_tweet_id is present. - Grouping: aggregate by organic_tweet_id and account_id to form post-level groups. - created_timestamp: earliest date in the group; null if all dates are missing. - post_message: the lexicographically last non-null tweet_text in the group; if all are missing, result is null; original casing and whitespace are preserved. - page_name: for each row, choose the first non-blank among screen_name, user_name, then account_id as text (blank strings treated as missing); from these per-row candidates, select the lexicographically last value in the group; may be null; original casing and whitespace are preserved. - platform: set to the literal value twitter. - Metrics aggregation: clicks, impressions, likes, retweets, replies, app_clicks, url_clicks, and qualified_impressions are summed per group, ignoring missing values. If a metric has no values in a group, it remains null at this stage. - Renames: shares is the sum of retweets; comments is the sum of replies. - engagement_rate: average of engagement_rate within the group, ignoring missing values; remains null if no values exist. - Final outputs: - page_id is account_id. - post_id is the text form of organic_tweet_id. - clicks, impressions, likes, shares, comments, app_clicks, url_clicks, and qualified_impressions default to 0 when null. - engagement_rate defaults to 0.0 when null. - post_url is built as https://twitter.com/{page_name}/status/{post_id}; if page_name is null, post_url is null; no URL encoding; casing preserved. - calculated_engagement_rate: if impressions (after defaulting) is greater than 0, compute (likes + shares + comments) divided by impressions using the zero-defaulted values; otherwise return 0.0; result is floating point. - Output: one row per (account_id, organic_tweet_id).'
      columns:
      - name: page_id
        data_type: VARCHAR
        description: Twitter account_id for the group; may be null
      - name: page_name
        data_type: VARCHAR
        description: Chosen as the lexicographically last per-row candidate (screen_name, else user_name, else account_id as text); may be null
      - name: post_id
        data_type: VARCHAR
        description: Organic tweet identifier as text; not null
        tests:
        - not_null
      - name: post_message
        data_type: VARCHAR
        description: Lexicographically last non-null tweet_text across the group
      - name: created_timestamp
        data_type: TIMESTAMP
        description: Earliest observed date for the tweet; null if all dates are missing
      - name: platform
        data_type: VARCHAR
        description: Constant value 'twitter'
      - name: clicks
        data_type: HUGEINT
        description: Sum of clicks across the group; missing values ignored; defaults to 0
      - name: impressions
        data_type: HUGEINT
        description: Sum of impressions across the group; missing values ignored; defaults to 0
      - name: likes
        data_type: HUGEINT
        description: Sum of likes across the group; missing values ignored; defaults to 0
      - name: shares
        data_type: HUGEINT
        description: Sum of retweets across the group; missing values ignored; defaults to 0
      - name: comments
        data_type: HUGEINT
        description: Sum of replies across the group; missing values ignored; defaults to 0
      - name: post_url
        data_type: VARCHAR
        description: Built as https://twitter.com/{page_name}/status/{post_id}; null if page_name is null; no URL encoding
      - name: app_clicks
        data_type: HUGEINT
        description: Sum of app_clicks across the group; missing values ignored; defaults to 0
      - name: url_clicks
        data_type: HUGEINT
        description: Sum of url_clicks across the group; missing values ignored; defaults to 0
      - name: qualified_impressions
        data_type: HUGEINT
        description: Sum of qualified_impressions across the group; missing values ignored; defaults to 0
      - name: engagement_rate
        data_type: DOUBLE
        description: Average engagement_rate across the group; defaults to 0.0 if no values
      - name: calculated_engagement_rate
        data_type: DOUBLE
        description: Computed as (likes + shares + comments) divided by impressions using zero-defaulted values; 0.0 when impressions is 0 or missing
```

## agent 最终 SQL

S4

```sql
with valid_tweets as (
    select *
    from staging.stg_social_media__twitter_organic_tweets
    where organic_tweet_id is not null
),
row_candidates as (
    select
        *,
        coalesce(nullif(screen_name, ''), nullif(user_name, ''), account_id::varchar) as page_name_candidate
    from valid_tweets
),
aggregated_tweets as (
    select
        account_id::varchar as page_id,
        max(page_name_candidate) as page_name,
        cast(organic_tweet_id as varchar) as post_id,
        max(tweet_text) as post_message,
        min(tweet_created_at) as created_timestamp,
        sum(clicks) as clicks,
        sum(impressions) as impressions,
        sum(likes) as likes,
        sum(retweets) as shares,
        sum(replies) as comments,
        sum(app_clicks) as app_clicks,
        sum(url_clicks) as url_clicks,
        sum(qualified_impressions) as qualified_impressions,
        avg(engagement_rate) as engagement_rate
    from row_candidates
    group by account_id, organic_tweet_id
),
metric_defaults as (
    select
        *,
        coalesce(clicks, 0)::hugeint as clicks_defaulted,
        coalesce(impressions, 0)::hugeint as impressions_defaulted,
        coalesce(likes, 0)::hugeint as likes_defaulted,
        coalesce(shares, 0)::hugeint as shares_defaulted,
        coalesce(comments, 0)::hugeint as comments_defaulted
    from aggregated_tweets
)
select
    page_id,
    page_name,
    post_id,
    post_message,
    created_timestamp,
    'twitter'::varchar as platform,
    clicks_defaulted as clicks,
    impressions_defaulted as impressions,
    likes_defaulted as likes,
    shares_defaulted as shares,
    comments_defaulted as comments,
    case when page_name is null then null else 'https://twitter.com/' || page_name || '/status/' || post_id end::varchar as post_url,
    coalesce(app_clicks, 0)::hugeint as app_clicks,
    coalesce(url_clicks, 0)::hugeint as url_clicks,
    coalesce(qualified_impressions, 0)::hugeint as qualified_impressions,
    coalesce(engagement_rate, 0.0)::double as engagement_rate,
    case when impressions_defaulted > 0
         then (likes_defaulted + shares_defaulted + comments_defaulted)::double / impressions_defaulted
         else 0.0 end as calculated_engagement_rate
from metric_defaults
```

## gold SQL（仅供定位差异）

S5

```sql
-- Twitter posts reporting intermediate table
-- Standardizes Twitter post data for unified reporting

WITH twitter_posts_source AS (
    SELECT
        organic_tweet_id,
        account_id,
        date,
        tweet_text,
        screen_name,
        user_name,
        lang,
        clicks,
        impressions,
        likes,
        replies,
        retweets,
        app_clicks,
        url_clicks,
        qualified_impressions,
        engagement_rate
    FROM staging.stg_social_media__twitter_organic_tweets
    WHERE organic_tweet_id IS NOT NULL -- Only include posts with IDs
),

-- Aggregate metrics by post
aggregated_metrics AS (
    SELECT
        organic_tweet_id AS post_id,
        account_id,
        MIN(date) AS created_timestamp, -- Use earliest date for post creation
        MAX(tweet_text) AS post_message, -- Get the main tweet text
        MAX(COALESCE(NULLIF(screen_name, ''), NULLIF(user_name, ''), CAST(account_id AS VARCHAR))) AS page_name,
        'twitter' AS platform,
        SUM(clicks) AS clicks,
        SUM(impressions) AS impressions,
        SUM(likes) AS likes,
        SUM(retweets) AS shares,
        SUM(replies) AS comments,
        SUM(app_clicks) AS app_clicks,
        SUM(url_clicks) AS url_clicks,
        SUM(qualified_impressions) AS qualified_impressions,
        AVG(engagement_rate) AS avg_engagement_rate
    FROM twitter_posts_source
    GROUP BY organic_tweet_id, account_id
)

SELECT
    account_id AS page_id,
    page_name,
    CAST(post_id AS VARCHAR) AS post_id,
    post_message,
    created_timestamp,
    platform,
    COALESCE(clicks, 0) AS clicks,
    COALESCE(impressions, 0) AS impressions,
    COALESCE(likes, 0) AS likes,
    COALESCE(shares, 0) AS shares,
    COALESCE(comments, 0) AS comments,
    -- Use screen_name as page name identifier
    CONCAT('https://twitter.com/', page_name, '/status/', post_id) AS post_url,
    -- Include original metrics
    COALESCE(app_clicks, 0) AS app_clicks,
    COALESCE(url_clicks, 0) AS url_clicks,
    COALESCE(qualified_impressions, 0) AS qualified_impressions,
    COALESCE(avg_engagement_rate, 0.0) AS engagement_rate,
    -- Derived metrics
    CASE
        WHEN COALESCE(impressions, 0) > 0
        THEN (COALESCE(likes, 0)::DOUBLE + COALESCE(shares, 0)::DOUBLE + COALESCE(comments, 0)::DOUBLE) / impressions
        ELSE 0.0
    END AS calculated_engagement_rate
FROM aggregated_metrics
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 75 | 75 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"post_id":"1.0957611982341474e+24"}</code> |
| K2 | <code>{"post_id":"1.2582018979009895e+24"}</code> |
| K3 | <code>{"post_id":"1.3140972793474397e+24"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| page_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_timestamp | 75 | 75 | 75 | TIMESTAMP | TIMESTAMP |
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| clicks | 0 | 0 | 0 | HUGEINT | HUGEINT |
| impressions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| likes | 0 | 0 | 0 | HUGEINT | HUGEINT |
| shares | 0 | 0 | 0 | HUGEINT | HUGEINT |
| comments | 0 | 0 | 0 | HUGEINT | HUGEINT |
| app_clicks | 0 | 0 | 0 | HUGEINT | HUGEINT |
| url_clicks | 0 | 0 | 0 | HUGEINT | HUGEINT |
| qualified_impressions | 0 | 0 | 0 | HUGEINT | HUGEINT |
| engagement_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| calculated_engagement_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |

created_timestamp 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 2023-11-03 18:52:25 |
| K2 | null | 2023-10-27 20:22:46 |
| K3 | null | 2023-11-05 17:16:20 |

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
| B6_constant_literal_output | <code>1输出列；[{"column":"platform","expression":["CAST('twitter' AS TEXT)"]}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory     from intermediate.social_media_reporting__twitter_posts_reporting where created_timestamp is not null</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 2094 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9937 | true | false |
| 13 | run | <code>wc -l docs/data_contract.yaml &amp;&amp; sed -n '1,240p' docs/data_contract.yaml</code> | 9685 | false | false |
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
files['intermediate/social_media_reporting__twitter_posts_reporting.sql'] = '''with valid_tweets as (
```
event 33 / message

```text
    from intermediate.social_media_reporting__twitter_posts_reporting
```
event 33 / message

```text
    from intermediate.social_media_reporting__twitter_posts_reporting
```
event 33 / message

```text
    from intermediate.social_media_reporting__twitter_posts_reporting where created_timestamp is not null
```
event 33 / message

```text
    from intermediate.social_media_reporting__twitter_posts_reporting
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-023.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/intermediate/social_media_reporting__twitter_posts_reporting.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/intermediate/social_media_reporting__twitter_posts_reporting.sql`
- S6: `records/006_contract_impl-023.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/result.md`
- S10: `data/024_packages_work/024_impl-023_social_media_reporting__twitter_posts_reporting/024_impl-023_social_media_reporting__twitter_posts_reporting.json`
- S11: `data/005_cs_work/impl-023_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions`
