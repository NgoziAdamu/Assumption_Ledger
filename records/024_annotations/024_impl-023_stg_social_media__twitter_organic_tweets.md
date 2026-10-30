# impl-023 · stg_social_media__twitter_organic_tweets

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

契约date为DATE；gold保留带时刻TIMESTAMP，导致129+129行键全不配对。仅放宽日期投影后L0全匹配。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-023_stg_social_media__twitter_organic_tweets.md](../024_packages/024_impl-023_stg_social_media__twitter_organic_tweets.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。

```text
115:     - name: stg_social_media__twitter_organic_tweets
116:       description: "Tweet-level organic performance records enriched with tweet text and user attributes; recent 2-year window."
117:       source_table: raw.organic_tweet_report
118:       notes:
119:         - "Rows restricted to last 2 years via: date >= CURRENT_DATE - INTERVAL '2 years'."
120:         - "Tweet text joined from raw.tweet.full_text; user attributes joined from raw.twitter_user_history."
121:         - "All metrics default to 0 when NULL."
122:         - "engagement_rate guarded against division by zero."
123:       columns:
124:         - name: account_id
125:           data_type: VARCHAR
126:         - name: date
127:           data_type: DATE
128:         - name: organic_tweet_id
129:           data_type: VARCHAR
130:           description: "CAST(o.organic_tweet_id AS VARCHAR)."
131:         - name: placement
132:           data_type: VARCHAR
133:         - name: _fivetran_synced
134:           data_type: TIMESTAMP
135:         - name: app_clicks
136:           data_type: BIGINT
137:         - name: card_engagements
138:           data_type: BIGINT
139:         - name: carousel_swipes
140:           data_type: BIGINT
141:         - name: clicks
142:           data_type: BIGINT
143:         - name: engagements
144:           data_type: BIGINT
145:         - name: follows
146:           data_type: BIGINT
147:         - name: impressions
148:           data_type: BIGINT
149:         - name: likes
150:           data_type: BIGINT
151:         - name: poll_card_vote
152:           data_type: BIGINT
153:         - name: qualified_impressions
154:           data_type: BIGINT
155:         - name: replies
156:           data_type: BIGINT
157:         - name: retweets
158:           data_type: BIGINT
159:         - name: tweets_send
160:           data_type: BIGINT
161:         - name: unfollows
162:           data_type: BIGINT
163:         - name: url_clicks
164:           data_type: BIGINT
165:         - name: video_15_s_views
166:           data_type: BIGINT
167:         - name: video_3_s_100_pct_views
168:           data_type: BIGINT
169:         - name: video_6_s_views
170:           data_type: BIGINT
171:         - name: video_content_starts
172:           data_type: BIGINT
173:         - name: video_cta_clicks
174:           data_type: BIGINT
175:         - name: video_total_views
176:           data_type: BIGINT
177:         - name: video_views_100
178:           data_type: BIGINT
179:         - name: video_views_25
180:           data_type: BIGINT
181:         - name: video_views_50
182:           data_type: BIGINT
183:         - name: video_views_75
184:           data_type: BIGINT
185:         - name: tweet_text
186:           data_type: VARCHAR
187:           description: "From raw.tweet.full_text."
188:         - name: screen_name
189:           data_type: VARCHAR
190:           description: "From raw.twitter_user_history.screen_name."
191:         - name: user_name
192:           data_type: VARCHAR
193:           description: "From raw.twitter_user_history.name."
194:         - name: lang
195:           data_type: VARCHAR
196:           description: "From raw.tweet.lang."
197:         - name: tweet_created_at
198:           data_type: TIMESTAMP
199:           description: "From raw.tweet.created_at."
200:         - name: engagement_rate
201:           data_type: DOUBLE
202:           description: "CASE WHEN impressions > 0 THEN engagements / impressions ELSE 0.0 END."
203: 
204:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__twitter_organic_tweets.sql`；SHA-256 `18e2be7f7ec8e6f19fb76c86984f8e6af58edce69e5e0b5e05c474896349c3fd`。

```text
1: with organic as (
2:     select *
3:     from raw.organic_tweet_report
4:     where cast(date as date) >= current_date - interval '2 years'
5: ),
6: tweets as (
7:     select
8:         try_cast(id as bigint) as tweet_id,
9:         full_test as tweet_text,
10:         lang,
11:         created_at as tweet_created_at
12:     from raw.tweet
13: ),
14: users as (
15:     select *, row_number() over (partition by id order by _fivetran_synced desc nulls last) as row_num
16:     from raw.twitter_user_history
17: )
18: select
19:     o.account_id::varchar as account_id,
20:     cast(o.date as date) as date,
21:     cast(o.organic_tweet_id as varchar) as organic_tweet_id,
22:     o.placement::varchar as placement,
23:     o._fivetran_synced::timestamp as _fivetran_synced,
24:     coalesce(o.app_clicks, 0)::bigint as app_clicks,
25:     coalesce(o.card_engagements, 0)::bigint as card_engagements,
26:     coalesce(o.carousel_swipes, 0)::bigint as carousel_swipes,
27:     coalesce(o.clicks, 0)::bigint as clicks,
28:     coalesce(o.engagements, 0)::bigint as engagements,
29:     coalesce(o.follows, 0)::bigint as follows,
30:     coalesce(o.impressions, 0)::bigint as impressions,
31:     coalesce(o.likes, 0)::bigint as likes,
32:     coalesce(o.poll_card_vote, 0)::bigint as poll_card_vote,
33:     coalesce(o.qualified_impressions, 0)::bigint as qualified_impressions,
34:     coalesce(o.replies, 0)::bigint as replies,
35:     coalesce(o.retweets, 0)::bigint as retweets,
36:     coalesce(o.tweets_send, 0)::bigint as tweets_send,
37:     coalesce(o.unfollows, 0)::bigint as unfollows,
38:     coalesce(o.url_clicks, 0)::bigint as url_clicks,
39:     coalesce(o.video_15_s_views, 0)::bigint as video_15_s_views,
40:     coalesce(o.video_3_s_100_pct_views, 0)::bigint as video_3_s_100_pct_views,
41:     coalesce(o.video_6_s_views, 0)::bigint as video_6_s_views,
42:     coalesce(o.video_content_starts, 0)::bigint as video_content_starts,
43:     coalesce(o.video_cta_clicks, 0)::bigint as video_cta_clicks,
44:     coalesce(o.video_total_views, 0)::bigint as video_total_views,
45:     coalesce(o.video_views_100, 0)::bigint as video_views_100,
46:     coalesce(o.video_views_25, 0)::bigint as video_views_25,
47:     coalesce(o.video_views_50, 0)::bigint as video_views_50,
48:     coalesce(o.video_views_75, 0)::bigint as video_views_75,
49:     t.tweet_text::varchar as tweet_text,
50:     regexp_replace(u.screen_name, '[^A-Za-z0-9_]', '', 'g')::varchar as screen_name,
51:     u.name::varchar as user_name,
52:     t.lang::varchar as lang,
53:     t.tweet_created_at::timestamp as tweet_created_at,
54:     case when coalesce(o.impressions, 0) > 0
55:          then coalesce(o.engagements, 0)::double / o.impressions else 0.0 end as engagement_rate
56: from organic o
57: left join tweets t on try_cast(o.organic_tweet_id as bigint) = t.tweet_id
58: left join users u on u.id = o.account_id and u.row_num = 1
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__twitter_organic_tweets.sql`；SHA-256 `ad74cc709021737f196104322a510af1585812c7b51833956766f469223d27d3`。

```text
1: WITH source_data AS (
2:     SELECT
3:         account_id,
4:         date,
5:         organic_tweet_id,
6:         placement,
7:         _fivetran_synced,
8:         app_clicks,
9:         card_engagements,
10:         carousel_swipes,
11:         clicks,
12:         engagements,
13:         follows,
14:         impressions,
15:         likes,
16:         poll_card_vote,
17:         qualified_impressions,
18:         replies,
19:         retweets,
20:         tweets_send,
21:         unfollows,
22:         url_clicks,
23:         video_15_s_views,
24:         video_3_s_100_pct_views,
25:         video_6_s_views,
26:         video_content_starts,
27:         video_cta_clicks,
28:         video_total_views,
29:         video_views_100,
30:         video_views_25,
31:         video_views_50,
32:         video_views_75
33:     FROM raw.organic_tweet_report
34:     WHERE date >= CURRENT_DATE - INTERVAL '2 years' -- Focus on recent data for analytics
35: ),
36: 
37: -- Join with tweet details
38: tweet_details AS (
39:     SELECT
40:         t.id AS tweet_id,
41:         t.account_id,
42:         t.created_at,
43:         t.full_test AS tweet_text,
44:         t.favorite_count,
45:         t.retweet_count,
46:         t.lang,
47:         t.source,
48:         u.screen_name,
49:         u.name AS user_name
50:     FROM raw.tweet t
51:     LEFT JOIN raw.twitter_user_history u ON t.user_id = u.id
52: )
53: 
54: SELECT
55:     o.account_id,
56:     o.date,
57:     CAST(o.organic_tweet_id AS VARCHAR) AS organic_tweet_id,
58:     o.placement,
59:     o._fivetran_synced,
60:     COALESCE(o.app_clicks, 0) AS app_clicks,
61:     COALESCE(o.card_engagements, 0) AS card_engagements,
62:     COALESCE(o.carousel_swipes, 0) AS carousel_swipes,
63:     COALESCE(o.clicks, 0) AS clicks,
64:     COALESCE(o.engagements, 0) AS engagements,
65:     COALESCE(o.follows, 0) AS follows,
66:     COALESCE(o.impressions, 0) AS impressions,
67:     COALESCE(o.likes, 0) AS likes,
68:     COALESCE(o.poll_card_vote, 0) AS poll_card_vote,
69:     COALESCE(o.qualified_impressions, 0) AS qualified_impressions,
70:     COALESCE(o.replies, 0) AS replies,
71:     COALESCE(o.retweets, 0) AS retweets,
72:     COALESCE(o.tweets_send, 0) AS tweets_send,
73:     COALESCE(o.unfollows, 0) AS unfollows,
74:     COALESCE(o.url_clicks, 0) AS url_clicks,
75:     COALESCE(o.video_15_s_views, 0) AS video_15_s_views,
76:     COALESCE(o.video_3_s_100_pct_views, 0) AS video_3_s_100_pct_views,
77:     COALESCE(o.video_6_s_views, 0) AS video_6_s_views,
78:     COALESCE(o.video_content_starts, 0) AS video_content_starts,
79:     COALESCE(o.video_cta_clicks, 0) AS video_cta_clicks,
80:     COALESCE(o.video_total_views, 0) AS video_total_views,
81:     COALESCE(o.video_views_100, 0) AS video_views_100,
82:     COALESCE(o.video_views_25, 0) AS video_views_25,
83:     COALESCE(o.video_views_50, 0) AS video_views_50,
84:     COALESCE(o.video_views_75, 0) AS video_views_75,
85:     t.tweet_text,
86:     t.screen_name,
87:     t.user_name,
88:     t.lang,
89:     t.created_at AS tweet_created_at,
90:     -- Calculate engagement rate inline
91:     CASE
92:         WHEN COALESCE(o.impressions, 0) > 0
93:         THEN (o.engagements::DOUBLE / o.impressions)
94:         ELSE 0.0
95:     END AS engagement_rate
96: FROM source_data o
97: LEFT JOIN tweet_details t ON o.organic_tweet_id = t.tweet_id AND o.account_id = t.account_id
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- date_projection（O）：**看到了但没提**；事件 15、16、23、24、29。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/15.json`；命令首行：`sed -n '220,520p' docs/data_contract.yaml`。
event 16：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/16.json`；原始观察输出。
event 23：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/23.json`；命令首行：`python - <<'PY'`。
event 24：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/24.json`；原始观察输出。
event 29：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/29.json`；命令首行：`mkdir -p sql/staging sql/intermediate sql/marts && cat > /tmp/write_sql.py <<'PY'`。

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

核实查询 **2** 条；代价档：**多条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：直接raw列名类型
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('organic_tweet_report','tweet','twitter_user_history') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["organic_tweet_report","account_id","VARCHAR"],["organic_tweet_report","date","TIMESTAMP"],["organic_tweet_report","organic_tweet_id","DOUBLE"],["organic_tweet_report","placement","VARCHAR"],["organic_tweet_report","_fivetran_synced","TIMESTAMP"],["organic_tweet_report","app_clicks","BIGINT"],["organic_tweet_report","card_engagements","BIGINT"],["organic_tweet_report","carousel_swipes","BIGINT"],["organic_tweet_report","clicks","BIGINT"],["organic_tweet_report","engagements","BIGINT"],["organic_tweet_report","follows","BIGINT"],["organic_tweet_report","impressions","BIGINT"],["organic_tweet_report","likes","BIGINT"],["organic_tweet_report","poll_card_vote","BIGINT"],["organic_tweet_report","qualified_impressions","BIGINT"],["organic_tweet_report","replies","BIGINT"],["organic_tweet_report","retweets","BIGINT"],["organic_tweet_report","tweets_send","BIGINT"],["organic_tweet_report","unfollows","BIGINT"],["organic_tweet_report","url_clicks","BIGINT"],["organic_tweet_report","video_15_s_views","BIGINT"],["organic_tweet_report","video_3_s_100_pct_views","BIGINT"],["organic_tweet_report","video_6_s_views","BIGINT"],["organic_tweet_report","video_content_starts","BIGINT"],["organic_tweet_report","video_cta_clicks","BIGINT"],["organic_tweet_report","video_total_views","BIGINT"],["organic_tweet_report","video_views_100","BIGINT"],["organic_tweet_report","video_views_25","BIGINT"],["organic_tweet_report","video_views_50","BIGINT"],["organic_tweet_report","video_views_75","BIGINT"],["tweet","id","DOUBLE"],["tweet","_fivetran_synced","TIMESTAMP"],["tweet","account_id","VARCHAR"],["tweet","created_at","TIMESTAMP"],["tweet","full_test","VARCHAR"],["tweet","favorite_count","BIGINT"],["tweet","retweet_count","BIGINT"],["tweet","user_id","VARCHAR"],["tweet","lang","VARCHAR"],["tweet","source","VARCHAR"],["twitter_user_history","id","VARCHAR"],["twitter_user_history","_fivetran_synced","TIMESTAMP"],["twitter_user_history","contributors_enabled","BOOLEAN"],["twitter_user_history","created_at","TIMESTAMP"],["twitter_user_history","default_profile","BOOLEAN"],["twitter_user_history","default_profile_image","BOOLEAN"],["twitter_user_history","description","VARCHAR"],["twitter_user_history","favourites_count","DOUBLE"],["twitter_user_history","followers_count","DOUBLE"],["twitter_user_history","friends_count","DOUBLE"],["twitter_user_history","geo_enabled","BOOLEAN"],["twitter_user_history","is_translation_enabled","BOOLEAN"],["twitter_user_history","is_translator","BOOLEAN"],["twitter_user_history","lang","VARCHAR"],["twitter_user_history","listed_count","DOUBLE"],["twitter_user_history","location","VARCHAR"],["twitter_user_history","name","VARCHAR"],["twitter_user_history","profile_background_image_url","VARCHAR"],["twitter_user_history","profile_background_image_url_https","VARCHAR"],["twitter_user_history","profile_background_tile","BOOLEAN"],["twitter_user_history","profile_banner_url","VARCHAR"],["twitter_user_history","profile_image_url","VARCHAR"],["twitter_user_history","profile_image_url_https","VARCHAR"],["twitter_user_history","profile_use_background_image","BOOLEAN"],["twitter_user_history","protected_user","BOOLEAN"],["twitter_user_history","screen_name","VARCHAR"],["twitter_user_history","statuses_count","DOUBLE"],["twitter_user_history","time_zone","VARCHAR"],["twitter_user_history","url","VARCHAR"],["twitter_user_history","utc_offset","DOUBLE"],["twitter_user_history","verified","BOOLEAN"]]}
```


### 核实：tweet关联/账户与用户ID差异
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT count(*) n,count(t.id) tweet_match,count(*) FILTER(WHERE t.account_id=o.account_id) same_account,count(*) FILTER(WHERE t.user_id=o.account_id) user_equals_account FROM raw.organic_tweet_report o LEFT JOIN raw.tweet t ON try_cast(o.organic_tweet_id AS BIGINT)=try_cast(t.id AS BIGINT)
```


```json
{"columns":["n","tweet_match","same_account","user_equals_account"],"rows":[[2500,0,0,0]]}
```


### 诊断：agent实际类型
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_social_media__twitter_organic_tweets'
```


```json
{"columns":["column_name","data_type"],"rows":[["account_id","VARCHAR"],["date","DATE"],["organic_tweet_id","VARCHAR"],["placement","VARCHAR"],["_fivetran_synced","TIMESTAMP"],["app_clicks","BIGINT"],["card_engagements","BIGINT"],["carousel_swipes","BIGINT"],["clicks","BIGINT"],["engagements","BIGINT"],["follows","BIGINT"],["impressions","BIGINT"],["likes","BIGINT"],["poll_card_vote","BIGINT"],["qualified_impressions","BIGINT"],["replies","BIGINT"],["retweets","BIGINT"],["tweets_send","BIGINT"],["unfollows","BIGINT"],["url_clicks","BIGINT"],["video_15_s_views","BIGINT"],["video_3_s_100_pct_views","BIGINT"],["video_6_s_views","BIGINT"],["video_content_starts","BIGINT"],["video_cta_clicks","BIGINT"],["video_total_views","BIGINT"],["video_views_100","BIGINT"],["video_views_25","BIGINT"],["video_views_50","BIGINT"],["video_views_75","BIGINT"],["tweet_text","VARCHAR"],["screen_name","VARCHAR"],["user_name","VARCHAR"],["lang","VARCHAR"],["tweet_created_at","TIMESTAMP"],["engagement_rate","DOUBLE"]]}
```


### 诊断：agent有限差异样例
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT date,account_id FROM staging.stg_social_media__twitter_organic_tweets LIMIT 3
```


```json
{"columns":["date","account_id"],"rows":[]}
```


### 诊断：gold实际类型
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_social_media__twitter_organic_tweets'
```


```json
{"columns":["column_name","data_type"],"rows":[["account_id","VARCHAR"],["date","TIMESTAMP"],["organic_tweet_id","VARCHAR"],["placement","VARCHAR"],["_fivetran_synced","TIMESTAMP"],["app_clicks","BIGINT"],["card_engagements","BIGINT"],["carousel_swipes","BIGINT"],["clicks","BIGINT"],["engagements","BIGINT"],["follows","BIGINT"],["impressions","BIGINT"],["likes","BIGINT"],["poll_card_vote","BIGINT"],["qualified_impressions","BIGINT"],["replies","BIGINT"],["retweets","BIGINT"],["tweets_send","BIGINT"],["unfollows","BIGINT"],["url_clicks","BIGINT"],["video_15_s_views","BIGINT"],["video_3_s_100_pct_views","BIGINT"],["video_6_s_views","BIGINT"],["video_content_starts","BIGINT"],["video_cta_clicks","BIGINT"],["video_total_views","BIGINT"],["video_views_100","BIGINT"],["video_views_25","BIGINT"],["video_views_50","BIGINT"],["video_views_75","BIGINT"],["tweet_text","VARCHAR"],["screen_name","VARCHAR"],["user_name","VARCHAR"],["lang","VARCHAR"],["tweet_created_at","TIMESTAMP"],["engagement_rate","DOUBLE"]]}
```


### 诊断：gold有限差异样例
[024_diagnostics.json](../024_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT date,account_id FROM staging.stg_social_media__twitter_organic_tweets LIMIT 3
```


```json
{"columns":["date","account_id"],"rows":[["2023-12-23 00:16:32","default_account"],["2023-11-07 13:37:17","default_account"],["2023-11-08 22:58:50","default_account"]]}
```

## 独立单点重跑

### 024_reruns_impl-023_stg_social_media__twitter_organic_tweets.json
[024_reruns_impl-023_stg_social_media__twitter_organic_tweets.json](../024_reruns_impl-023_stg_social_media__twitter_organic_tweets.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-17 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-17'","count":1}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|129|129|258|7740|否|
|L1|129|129|258|7740|否|
|L2|129|129|258|7740|否|
|L3|129|129|258|7740|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L1：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L2：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L3：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`

#### baseline
私有SQL：`data/024_work/impl-023_stg_social_media__twitter_organic_tweets/baseline.sql`；SHA-256 `3c1c8c086c1750a00f87a653d30f43b950a24220e70d1d1d45b62c05347427f7`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|129|129|258|7740|否|
|L1|129|129|258|7740|否|
|L2|129|129|258|7740|否|
|L3|129|129|258|7740|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L1：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L2：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L3：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`

#### tweet_join_account
不计参与因素；类别候选A。契约给来源但未细定连接关系；本项仅检验SQL差异，单改不减少评测规模。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第57行、offset 2640起替换；其他字节相同。
原表达式：
```sql
t.tweet_id
```

修改后：
```sql
t.tweet_id and o.account_id = (select any_value(account_id) from raw.tweet tx where try_cast(tx.id as bigint)=t.tweet_id)
```

私有SQL：`data/024_work/impl-023_stg_social_media__twitter_organic_tweets/tweet_join_account.sql`；SHA-256 `aded0b3642bb82e01b73f16088232b1f57a0aec81d0b4a75b4d30308a6812d35`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|129|129|258|7740|否|
|L1|129|129|258|7740|否|
|L2|129|129|258|7740|否|
|L3|129|129|258|7740|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L1：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L2：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L3：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`

#### user_join_source
不计参与因素；类别候选A。契约给来源但未细定连接关系；本项仅检验SQL差异，单改不减少评测规模。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第58行、offset 2672起替换；其他字节相同。
原表达式：
```sql
u.id = o.account_id
```

修改后：
```sql
u.id = (select any_value(user_id) from raw.tweet tx where try_cast(tx.id as bigint)=t.tweet_id)
```

私有SQL：`data/024_work/impl-023_stg_social_media__twitter_organic_tweets/user_join_source.sql`；SHA-256 `aae38030ce8f9ea0a61b242fca0824da8f6bc621594093319007598d8522e6e3`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|129|129|258|7740|否|
|L1|129|129|258|7740|否|
|L2|129|129|258|7740|否|
|L3|129|129|258|7740|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L1：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L2：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L3：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`

#### user_latest
不计参与因素；类别候选A。契约给来源但未细定连接关系；本项仅检验SQL差异，单改不减少评测规模。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第58行、offset 2691起替换；其他字节相同。
原表达式：
```sql
 and u.row_num = 1
```

修改后：
```sql

```

私有SQL：`data/024_work/impl-023_stg_social_media__twitter_organic_tweets/user_latest.sql`；SHA-256 `5612717e6f4965610cf4c334ff014fb6800f4062de8331317f39bb6cd98466e4`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|129|129|258|7740|否|
|L1|129|129|258|7740|否|
|L2|129|129|258|7740|否|
|L3|129|129|258|7740|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L1：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L2：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L3：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`

#### screen_clean
不计参与因素；类别候选A。契约给来源但未细定连接关系；本项仅检验SQL差异，单改不减少评测规模。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第50行、offset 2221起替换；其他字节相同。
原表达式：
```sql
regexp_replace(u.screen_name, '[^A-Za-z0-9_]', '', 'g')
```

修改后：
```sql
u.screen_name
```

私有SQL：`data/024_work/impl-023_stg_social_media__twitter_organic_tweets/screen_clean.sql`；SHA-256 `4d39a2e3978ec4951c52eeedc41ae727568f74534b20fa26bb94771c3a042ca9`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|129|129|258|7740|否|
|L1|129|129|258|7740|否|
|L2|129|129|258|7740|否|
|L3|129|129|258|7740|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L1：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L2：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L3：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
### 024_supplement_reruns_impl-023_stg_social_media__twitter_organic_tweets.json
[024_supplement_reruns_impl-023_stg_social_media__twitter_organic_tweets.json](../024_supplement_reruns_impl-023_stg_social_media__twitter_organic_tweets.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-17 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-17'","count":1}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|129|129|258|7740|否|
|L1|129|129|258|7740|否|
|L2|129|129|258|7740|否|
|L3|129|129|258|7740|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L1：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L2：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L3：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`

#### baseline
私有SQL：`data/024_supplement_work/impl-023_stg_social_media__twitter_organic_tweets/baseline.sql`；SHA-256 `3c1c8c086c1750a00f87a653d30f43b950a24220e70d1d1d45b62c05347427f7`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|129|129|258|7740|否|
|L1|129|129|258|7740|否|
|L2|129|129|258|7740|否|
|L3|129|129|258|7740|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L1：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L2：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`
- L3：`{"account_id":258,"date":258,"organic_tweet_id":258,"placement":258,"app_clicks":258,"card_engagements":258,"carousel_swipes":258,"clicks":258,"engagement_rate":258,"engagements":258,"follows":258,"impressions":258,"likes":258,"poll_card_vote":258,"qualified_impressions":258,"replies":258,"retweets":258,"tweets_send":258,"unfollows":258,"url_clicks":258,"video_15_s_views":258,"video_3_s_100_pct_views":258,"video_6_s_views":258,"video_content_starts":258,"video_cta_clicks":258,"video_total_views":258,"video_views_100":258,"video_views_25":258,"video_views_50":258,"video_views_75":258}`

#### date_projection
主因；类别候选O。契约date为DATE，gold保留带时刻TIMESTAMP，评测键不做容差。
相对本轮基线：行减少258，格减少7740。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第20行、offset 516起替换；其他字节相同。
原表达式：
```sql
cast(o.date as date) as date
```

修改后：
```sql
o.date as date
```

私有SQL：`data/024_supplement_work/impl-023_stg_social_media__twitter_organic_tweets/date_projection.sql`；SHA-256 `3090e92e69176f320e5fa948bcba12c0f72d7acedab682ddbd0cce78d068952b`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|129|129|0|0|是|
|L1|129|129|0|0|是|
|L2|129|129|0|0|是|
|L3|129|129|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 规则问题

无。

