# impl-023 · social_media_reporting__twitter_posts_reporting

用途：**全量**；层：**intermediate**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**C**；把握：高。

created_timestamp取tweet_created_at而非契约明确的组内min(date)，75行差异单改后L0全匹配。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-023_social_media_reporting__twitter_posts_reporting.md](../024_packages/024_impl-023_social_media_reporting__twitter_posts_reporting.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。

```text
617:     - name: social_media_reporting__twitter_posts_reporting
618:       description: Standardizes organic Twitter tweet metrics into one row per tweet and account with summed counts, averaged engagement rate, and canonical URL
619:       grain: One row per post_id (organic_tweet_id) per page_id (account_id)
620:       source_models:
621:       - staging.stg_social_media__twitter_organic_tweets
622:       business_logic: '- Input: include only records where organic_tweet_id is present. - Grouping: aggregate by organic_tweet_id and account_id to form post-level groups. - created_timestamp: earliest date in the group; null if all dates are missing. - post_message: the lexicographically last non-null tweet_text in the group; if all are missing, result is null; original casing and whitespace are preserved. - page_name: for each row, choose the first non-blank among screen_name, user_name, then account_id as text (blank strings treated as missing); from these per-row candidates, select the lexicographically last value in the group; may be null; original casing and whitespace are preserved. - platform: set to the literal value twitter. - Metrics aggregation: clicks, impressions, likes, retweets, replies, app_clicks, url_clicks, and qualified_impressions are summed per group, ignoring missing values. If a metric has no values in a group, it remains null at this stage. - Renames: shares is the sum of retweets; comments is the sum of replies. - engagement_rate: average of engagement_rate within the group, ignoring missing values; remains null if no values exist. - Final outputs: - page_id is account_id. - post_id is the text form of organic_tweet_id. - clicks, impressions, likes, shares, comments, app_clicks, url_clicks, and qualified_impressions default to 0 when null. - engagement_rate defaults to 0.0 when null. - post_url is built as https://twitter.com/{page_name}/status/{post_id}; if page_name is null, post_url is null; no URL encoding; casing preserved. - calculated_engagement_rate: if impressions (after defaulting) is greater than 0, compute (likes + shares + comments) divided by impressions using the zero-defaulted values; otherwise return 0.0; result is floating point. - Output: one row per (account_id, organic_tweet_id).'
623:       columns:
624:       - name: page_id
625:         data_type: VARCHAR
626:         description: Twitter account_id for the group; may be null
627:       - name: page_name
628:         data_type: VARCHAR
629:         description: Chosen as the lexicographically last per-row candidate (screen_name, else user_name, else account_id as text); may be null
630:       - name: post_id
631:         data_type: VARCHAR
632:         description: Organic tweet identifier as text; not null
633:         tests:
634:         - not_null
635:       - name: post_message
636:         data_type: VARCHAR
637:         description: Lexicographically last non-null tweet_text across the group
638:       - name: created_timestamp
639:         data_type: TIMESTAMP
640:         description: Earliest observed date for the tweet; null if all dates are missing
641:       - name: platform
642:         data_type: VARCHAR
643:         description: Constant value 'twitter'
644:       - name: clicks
645:         data_type: HUGEINT
646:         description: Sum of clicks across the group; missing values ignored; defaults to 0
647:       - name: impressions
648:         data_type: HUGEINT
649:         description: Sum of impressions across the group; missing values ignored; defaults to 0
650:       - name: likes
651:         data_type: HUGEINT
652:         description: Sum of likes across the group; missing values ignored; defaults to 0
653:       - name: shares
654:         data_type: HUGEINT
655:         description: Sum of retweets across the group; missing values ignored; defaults to 0
656:       - name: comments
657:         data_type: HUGEINT
658:         description: Sum of replies across the group; missing values ignored; defaults to 0
659:       - name: post_url
660:         data_type: VARCHAR
661:         description: Built as https://twitter.com/{page_name}/status/{post_id}; null if page_name is null; no URL encoding
662:       - name: app_clicks
663:         data_type: HUGEINT
664:         description: Sum of app_clicks across the group; missing values ignored; defaults to 0
665:       - name: url_clicks
666:         data_type: HUGEINT
667:         description: Sum of url_clicks across the group; missing values ignored; defaults to 0
668:       - name: qualified_impressions
669:         data_type: HUGEINT
670:         description: Sum of qualified_impressions across the group; missing values ignored; defaults to 0
671:       - name: engagement_rate
672:         data_type: DOUBLE
673:         description: Average engagement_rate across the group; defaults to 0.0 if no values
674:       - name: calculated_engagement_rate
675:         data_type: DOUBLE
676:         description: Computed as (likes + shares + comments) divided by impressions using zero-defaulted values; 0.0 when impressions is 0 or missing
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/intermediate/social_media_reporting__twitter_posts_reporting.sql`；SHA-256 `0fa1b22c34f60e578db9e83689c6976c4bb72882ae3b0c948214578c872ccfc4`。

```text
1: with valid_tweets as (
2:     select *
3:     from staging.stg_social_media__twitter_organic_tweets
4:     where organic_tweet_id is not null
5: ),
6: row_candidates as (
7:     select
8:         *,
9:         coalesce(nullif(screen_name, ''), nullif(user_name, ''), account_id::varchar) as page_name_candidate
10:     from valid_tweets
11: ),
12: aggregated_tweets as (
13:     select
14:         account_id::varchar as page_id,
15:         max(page_name_candidate) as page_name,
16:         cast(organic_tweet_id as varchar) as post_id,
17:         max(tweet_text) as post_message,
18:         min(tweet_created_at) as created_timestamp,
19:         sum(clicks) as clicks,
20:         sum(impressions) as impressions,
21:         sum(likes) as likes,
22:         sum(retweets) as shares,
23:         sum(replies) as comments,
24:         sum(app_clicks) as app_clicks,
25:         sum(url_clicks) as url_clicks,
26:         sum(qualified_impressions) as qualified_impressions,
27:         avg(engagement_rate) as engagement_rate
28:     from row_candidates
29:     group by account_id, organic_tweet_id
30: ),
31: metric_defaults as (
32:     select
33:         *,
34:         coalesce(clicks, 0)::hugeint as clicks_defaulted,
35:         coalesce(impressions, 0)::hugeint as impressions_defaulted,
36:         coalesce(likes, 0)::hugeint as likes_defaulted,
37:         coalesce(shares, 0)::hugeint as shares_defaulted,
38:         coalesce(comments, 0)::hugeint as comments_defaulted
39:     from aggregated_tweets
40: )
41: select
42:     page_id,
43:     page_name,
44:     post_id,
45:     post_message,
46:     created_timestamp,
47:     'twitter'::varchar as platform,
48:     clicks_defaulted as clicks,
49:     impressions_defaulted as impressions,
50:     likes_defaulted as likes,
51:     shares_defaulted as shares,
52:     comments_defaulted as comments,
53:     case when page_name is null then null else 'https://twitter.com/' || page_name || '/status/' || post_id end::varchar as post_url,
54:     coalesce(app_clicks, 0)::hugeint as app_clicks,
55:     coalesce(url_clicks, 0)::hugeint as url_clicks,
56:     coalesce(qualified_impressions, 0)::hugeint as qualified_impressions,
57:     coalesce(engagement_rate, 0.0)::double as engagement_rate,
58:     case when impressions_defaulted > 0
59:          then (likes_defaulted + shares_defaulted + comments_defaulted)::double / impressions_defaulted
60:          else 0.0 end as calculated_engagement_rate
61: from metric_defaults
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/intermediate/social_media_reporting__twitter_posts_reporting.sql`；SHA-256 `cf996cc2d7a1a2594e7e5b9d78f1b6850e0770bf8ba9c3ecfc26c62370c63a2c`。

```text
1: -- Twitter posts reporting intermediate table
2: -- Standardizes Twitter post data for unified reporting
3: 
4: WITH twitter_posts_source AS (
5:     SELECT
6:         organic_tweet_id,
7:         account_id,
8:         date,
9:         tweet_text,
10:         screen_name,
11:         user_name,
12:         lang,
13:         clicks,
14:         impressions,
15:         likes,
16:         replies,
17:         retweets,
18:         app_clicks,
19:         url_clicks,
20:         qualified_impressions,
21:         engagement_rate
22:     FROM staging.stg_social_media__twitter_organic_tweets
23:     WHERE organic_tweet_id IS NOT NULL -- Only include posts with IDs
24: ),
25: 
26: -- Aggregate metrics by post
27: aggregated_metrics AS (
28:     SELECT
29:         organic_tweet_id AS post_id,
30:         account_id,
31:         MIN(date) AS created_timestamp, -- Use earliest date for post creation
32:         MAX(tweet_text) AS post_message, -- Get the main tweet text
33:         MAX(COALESCE(NULLIF(screen_name, ''), NULLIF(user_name, ''), CAST(account_id AS VARCHAR))) AS page_name,
34:         'twitter' AS platform,
35:         SUM(clicks) AS clicks,
36:         SUM(impressions) AS impressions,
37:         SUM(likes) AS likes,
38:         SUM(retweets) AS shares,
39:         SUM(replies) AS comments,
40:         SUM(app_clicks) AS app_clicks,
41:         SUM(url_clicks) AS url_clicks,
42:         SUM(qualified_impressions) AS qualified_impressions,
43:         AVG(engagement_rate) AS avg_engagement_rate
44:     FROM twitter_posts_source
45:     GROUP BY organic_tweet_id, account_id
46: )
47: 
48: SELECT
49:     account_id AS page_id,
50:     page_name,
51:     CAST(post_id AS VARCHAR) AS post_id,
52:     post_message,
53:     created_timestamp,
54:     platform,
55:     COALESCE(clicks, 0) AS clicks,
56:     COALESCE(impressions, 0) AS impressions,
57:     COALESCE(likes, 0) AS likes,
58:     COALESCE(shares, 0) AS shares,
59:     COALESCE(comments, 0) AS comments,
60:     -- Use screen_name as page name identifier
61:     CONCAT('https://twitter.com/', page_name, '/status/', post_id) AS post_url,
62:     -- Include original metrics
63:     COALESCE(app_clicks, 0) AS app_clicks,
64:     COALESCE(url_clicks, 0) AS url_clicks,
65:     COALESCE(qualified_impressions, 0) AS qualified_impressions,
66:     COALESCE(avg_engagement_rate, 0.0) AS engagement_rate,
67:     -- Derived metrics
68:     CASE
69:         WHEN COALESCE(impressions, 0) > 0
70:         THEN (COALESCE(likes, 0)::DOUBLE + COALESCE(shares, 0)::DOUBLE + COALESCE(comments, 0)::DOUBLE) / impressions
71:         ELSE 0.0
72:     END AS calculated_engagement_rate
73: FROM aggregated_metrics
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- created_timestamp（C）：**看到了但没提**；事件 17、18、31。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 17：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/17.json`；命令首行：`sed -n '520,790p' docs/data_contract.yaml`。
event 18：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/18.json`；原始观察输出。
event 31：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/31.json`；命令首行：`cat >> /tmp/write_sql.py <<'PY'`。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】
已按配置顺序完成并写入 `sql/staging/`、`sql/intermediate/` 和 `sql/marts/` 下的 16 个 DuckDB SQL 模型。SQL 使用直接的 `schema.table` 上游引用，无 dbt `ref()`，且文件末尾均无分号。

实现覆盖：
- Staging：7 个合同表，包含字段映射、类型转换、数据清洗、无效键/时区行过滤、指标空值处理及平台相关源表连接。
- Intermediate：5 个平台报告模型，包含合同规定的过滤、指标标准化、聚合、内容分类、比率、时间桶及窗口逻辑。
- Marts：4 个模型，包含平台统一 rollup、每日 KPI 日期 spine、周留存 cohort 及月度 CTR/KPI 聚合。

**验证结果**
- `python run.py` 执行成功，第二次复跑也成功。
- Staging：7/7；Intermediate：5/5；Marts：4/4 模型创建成功。
- 文件检查确认无末尾分号及 `ref()` 引用。
- 无 SQL 执行失败，因此没有失败语句或修复项。

**数据质量及残余影响**
运行环境日期为 2026-10-25，而原始 Facebook、Instagram、Twitter、YouTube 数据最大日期约在 2023 年，LinkedIn 关联历史资料也主要在 2021—2023 年。按合同中相对于 `CURRENT_DATE` 的最近 2 年/4 年过滤要求，记录不在窗口内；本次中间层及 marts 因此为空。这是合同时间窗与源数据时效共同导致的结果，不是 SQL 执行错误；补充时间窗内源数据后，重新执行即可纳入。

合同与源结构存在的缺口：LinkedIn staging 契约指定的关联源表缺少可直接匹配的 UGC 历史主键，关联历史中的 `created_time` 无匹配时为空，此类记录随后按中间层的非空时间要求排除。LinkedIn staging 契约也未提供中间层逻辑所需的互动指标/源 engagement rate，因此缺失指标按模型逻辑默认 0。`account_history.id` 在源中为 VARCHAR，但契约要求 BIGINT；不可转换的键按无效主键处理并删除。上述处理不伪造时间或指标，残余影响是相关记录被排除或其互动量无法体现。

过滤遵循 YAML 的时间窗口及关键字段要求；来源重复按合同保留，未额外去重。
```

## 查询

核实查询 **0** 条；代价档：**需要查业务说明**。含失败后重试的每条SQL；诊断查询不计入5条上限。
## 独立单点重跑

### 024_reruns_impl-023_social_media_reporting__twitter_posts_reporting.json
[024_reruns_impl-023_social_media_reporting__twitter_posts_reporting.json](../024_reruns_impl-023_social_media_reporting__twitter_posts_reporting.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|75|75|75|75|否|
|L1|75|75|75|75|否|
|L2|75|75|75|75|否|
|L3|75|75|75|75|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_timestamp":75}`
- L1：`{"created_timestamp":75}`
- L2：`{"created_timestamp":75}`
- L3：`{"created_timestamp":75}`

#### baseline
私有SQL：`data/024_work/impl-023_social_media_reporting__twitter_posts_reporting/baseline.sql`；SHA-256 `0fa1b22c34f60e578db9e83689c6976c4bb72882ae3b0c948214578c872ccfc4`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|75|75|75|75|否|
|L1|75|75|75|75|否|
|L2|75|75|75|75|否|
|L3|75|75|75|75|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"created_timestamp":75}`
- L1：`{"created_timestamp":75}`
- L2：`{"created_timestamp":75}`
- L3：`{"created_timestamp":75}`

#### created_timestamp
主因；类别候选C。契约明确组内earliest date；agent用了推文创建时间。
相对本轮基线：行减少75，格减少75。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第18行、offset 536起替换；其他字节相同。
原表达式：
```sql
min(tweet_created_at)
```

修改后：
```sql
min(date)
```

私有SQL：`data/024_work/impl-023_social_media_reporting__twitter_posts_reporting/created_timestamp.sql`；SHA-256 `8401fd3f779bfa4783b690b852817583e7945f28853042694005bf57decbc24f`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|75|75|0|0|是|
|L1|75|75|0|0|是|
|L2|75|75|0|0|是|
|L3|75|75|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 规则问题

无。

