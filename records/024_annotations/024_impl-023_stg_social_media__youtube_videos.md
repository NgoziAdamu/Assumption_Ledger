# impl-023 · stg_social_media__youtube_videos

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**A**；把握：中。

page_name两种源列选择造成152格，gold与契约FLOOR不一致另外影响estimated_shares 66格及engagement_rate 133格。

参与因素：O：estimated_shares（行减0，格减66）；O：engagement_shares（行减0，格减133）。
标记：无。

## 材料与比较口径

[024_impl-023_stg_social_media__youtube_videos.md](../024_packages/024_impl-023_stg_social_media__youtube_videos.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。

```text
353:     - name: stg_social_media__youtube_videos
354:       description: "YouTube videos staged with standardized fields and basic derived metrics; recent 2-year window."
355:       source_table: raw.youtube_video
356:       notes:
357:         - "Include only videos with view data: statistics_view_count IS NOT NULL."
358:         - "Restrict to last 2 years: snippet_published_at >= CURRENT_DATE - INTERVAL '2 years'."
359:         - "post_url is constructed as https://img.youtube.com/vi/{video_id}/default.jpg."
360:         - "All numeric metrics default to 0 when NULL."
361:         - "impressions and clicks both mirror statistics_view_count per SQL."
362:       columns:
363:         - name: video_id
364:           data_type: VARCHAR
365:           description: "CAST(id AS VARCHAR)."
366:         - name: video_published_at
367:           data_type: TIMESTAMP
368:           description: "snippet_published_at."
369:         - name: video_title
370:           data_type: VARCHAR
371:         - name: video_description
372:           data_type: VARCHAR
373:         - name: channel_id
374:           data_type: VARCHAR
375:         - name: channel_title
376:           data_type: VARCHAR
377:         - name: page_name
378:           data_type: VARCHAR
379:         - name: post_url
380:           data_type: VARCHAR
381:           description: "Thumbnail URL used as post URL: https://img.youtube.com/vi/{video_id}/default.jpg."
382:           validation_rules:
383:             - rule: "post_url RLIKE '^https://img.youtube.com/vi/.+/default.jpg'"
384:               on_failure: correct
385:         - name: privacy_status
386:           data_type: VARCHAR
387:         - name: clicks
388:           data_type: BIGINT
389:         - name: impressions
390:           data_type: BIGINT
391:           description: "COALESCE(statistics_view_count, 0) — estimated as views in SQL."
392:         - name: likes
393:           data_type: BIGINT
394:         - name: comments
395:           data_type: BIGINT
396:         - name: estimated_shares
397:           data_type: BIGINT
398:           description: >
399:             CASE WHEN statistics_like_count > 10 THEN FLOOR(statistics_like_count / 10) ELSE 0 END.
400:         - name: subscribers
401:           data_type: BIGINT
402:           description: "COALESCE(channel_info.channel_subscribers, 0)."
403:         - name: engagement_rate
404:           data_type: DOUBLE
405:           description: "CASE WHEN impressions > 0 THEN (likes + comments + estimated_shares)::DOUBLE / impressions ELSE 0.0 END."
406:         - name: _fivetran_synced
407:           data_type: TIMESTAMP
408:           description: "_fivetran_synced from raw.youtube_video."
409: 
410: 
411: # --------------------------------------------------------------------------- #
412: # PHASE 2: Defines the business logic from staging to analytical models.      #
413: # --------------------------------------------------------------------------- #
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__youtube_videos.sql`；SHA-256 `06a562457bf5a15ce31c67f2d85a92ac94f7930d79d92ee4b95448b84d8c58e9`。

```text
1: with channel_info as (
2:     select channel_id, max(channel_subscribers) as channel_subscribers
3:     from raw.youtube_channel_basic
4:     group by channel_id
5: )
6: select
7:     cast(v.id as varchar) as video_id,
8:     v.snippet_published_at::timestamp as video_published_at,
9:     v.snippet_title::varchar as video_title,
10:     v.snippet_description::varchar as video_description,
11:     v.snippet_channel_id::varchar as channel_id,
12:     v.snippet_channel_title::varchar as channel_title,
13:     coalesce(v.snippet_channel_title, 'Unknown Channel')::varchar as page_name,
14:     ('https://img.youtube.com/vi/' || v.id || '/default.jpg')::varchar as post_url,
15:     v.privacy_status::varchar as privacy_status,
16:     coalesce(v.statistics_view_count, 0)::bigint as clicks,
17:     coalesce(v.statistics_view_count, 0)::bigint as impressions,
18:     coalesce(v.statistics_like_count, 0)::bigint as likes,
19:     coalesce(v.statistics_comment_count, 0)::bigint as comments,
20:     case when v.statistics_like_count > 10 then floor(v.statistics_like_count / 10.0)::bigint else 0 end as estimated_shares,
21:     coalesce(try_cast(ci.channel_subscribers as bigint), 0)::bigint as subscribers,
22:     case when coalesce(v.statistics_view_count, 0) > 0
23:          then (coalesce(v.statistics_like_count, 0) + coalesce(v.statistics_comment_count, 0)
24:                + case when v.statistics_like_count > 10 then floor(v.statistics_like_count / 10.0) else 0 end)::double / v.statistics_view_count
25:          else 0.0 end as engagement_rate,
26:     v._fivetran_synced::timestamp as _fivetran_synced
27: from raw.youtube_video v
28: left join channel_info ci on ci.channel_id = v.snippet_channel_id
29: where v.statistics_view_count is not null
30:   and v.snippet_published_at >= current_date - interval '2 years'
31:   and v.snippet_published_at is not null
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__youtube_videos.sql`；SHA-256 `4a03885ebd96d9949e73052836a9b8150d4268853fb82abb5e93f577aebed587`。

```text
1: -- YouTube videos staging table - Simplified version
2: -- Based on actual table structure
3: 
4: WITH source_videos AS (
5:     SELECT
6:         id,
7:         _fivetran_synced,
8:         snippet_published_at,
9:         snippet_title,
10:         snippet_description,
11:         snippet_channel_id,
12:         snippet_channel_title,
13:         snippet_thumbnails,
14:         statistics_comment_count,
15:         statistics_dislike_count,
16:         statistics_favorite_count,
17:         statistics_like_count,
18:         statistics_view_count,
19:         privacy_status,
20:         status_embeddable
21:     FROM raw.youtube_video
22:     WHERE statistics_view_count IS NOT NULL -- Include videos with view data
23:     AND snippet_published_at >= CURRENT_DATE - INTERVAL '2 years' -- Recent videos only
24: ),
25: 
26: -- Get channel information
27: channel_info AS (
28:     SELECT DISTINCT
29:         channel_id,
30:         channel_display_name,
31:         channel_subscribers
32:     FROM raw.youtube_channel_basic
33: )
34: 
35: SELECT
36:     CAST(v.id AS VARCHAR) AS video_id,
37:     v.snippet_published_at AS video_published_at,
38:     CAST(v.snippet_title AS VARCHAR) AS video_title,
39:     CAST(v.snippet_description AS VARCHAR) AS video_description,
40:     CAST(v.snippet_channel_id AS VARCHAR) AS channel_id,
41:     COALESCE(v.snippet_channel_title, 'Unknown Channel') AS channel_title,
42:     CAST(c.channel_display_name AS VARCHAR) AS page_name,
43:     -- Use thumbnail URL as post URL
44:     CAST('https://img.youtube.com/vi/' || v.id || '/default.jpg' AS VARCHAR) AS post_url,
45:     v.privacy_status,
46:     -- Standardized metrics (clicks = views per original DBT logic)
47:     COALESCE(v.statistics_view_count, 0) AS clicks,
48:     COALESCE(v.statistics_view_count, 0) AS impressions, -- Estimate impressions as views
49:     COALESCE(v.statistics_like_count, 0) AS likes,
50:     COALESCE(v.statistics_comment_count, 0) AS comments,
51:     -- Estimate shares based on likes
52:     CASE
53:         WHEN COALESCE(v.statistics_like_count, 0) > 10
54:         THEN CAST(v.statistics_like_count / 10 AS BIGINT)
55:         ELSE 0
56:     END AS estimated_shares,
57:     -- Account metrics
58:     COALESCE(c.channel_subscribers, 0) AS subscribers,
59:     -- Engagement rate estimation
60:     CASE
61:         WHEN COALESCE(v.statistics_view_count, 0) > 0
62:         THEN (
63:             COALESCE(v.statistics_like_count, 0)::DOUBLE +
64:             COALESCE(v.statistics_comment_count, 0)::DOUBLE +
65:             (CASE WHEN COALESCE(v.statistics_like_count, 0) > 10 THEN v.statistics_like_count / 10 ELSE 0 END)::DOUBLE
66:         ) / v.statistics_view_count
67:         ELSE 0.0
68:     END AS engagement_rate,
69:     -- Additional channel metrics
70:     v._fivetran_synced
71: FROM source_videos v
72: LEFT JOIN channel_info c ON v.snippet_channel_id = c.channel_id
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- page_name（A）：**看到了但没提**；事件 15、16、23、24、29。
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('youtube_channel_basic','youtube_video') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["youtube_channel_basic","_fivetran_id","VARCHAR"],["youtube_channel_basic","date","DATE"],["youtube_channel_basic","_fivetran_synced","TIMESTAMP"],["youtube_channel_basic","annotation_click_through_rate","DOUBLE"],["youtube_channel_basic","annotation_clickable_impressions","DOUBLE"],["youtube_channel_basic","annotation_clicks","DOUBLE"],["youtube_channel_basic","annotation_closable_impressions","DOUBLE"],["youtube_channel_basic","annotation_close_rate","DOUBLE"],["youtube_channel_basic","annotation_closes","DOUBLE"],["youtube_channel_basic","annotation_impressions","DOUBLE"],["youtube_channel_basic","average_view_duration_percentage","DOUBLE"],["youtube_channel_basic","average_view_duration_seconds","DOUBLE"],["youtube_channel_basic","card_click_rate","DOUBLE"],["youtube_channel_basic","card_clicks","DOUBLE"],["youtube_channel_basic","card_impressions","DOUBLE"],["youtube_channel_basic","card_teaser_click_rate","DOUBLE"],["youtube_channel_basic","card_teaser_clicks","DOUBLE"],["youtube_channel_basic","card_teaser_impressions","DOUBLE"],["youtube_channel_basic","channel_id","VARCHAR"],["youtube_channel_basic","comments","DOUBLE"],["youtube_channel_basic","country_code","VARCHAR"],["youtube_channel_basic","dislikes","DOUBLE"],["youtube_channel_basic","likes","DOUBLE"],["youtube_channel_basic","live_or_on_demand","VARCHAR"],["youtube_channel_basic","red_views","DOUBLE"],["youtube_channel_basic","red_watch_time_minutes","DOUBLE"],["youtube_channel_basic","shares","DOUBLE"],["youtube_channel_basic","subscribed_status","VARCHAR"],["youtube_channel_basic","subscribers_gained","DOUBLE"],["youtube_channel_basic","subscribers_lost","DOUBLE"],["youtube_channel_basic","video_id","VARCHAR"],["youtube_channel_basic","videos_added_to_playlists","DOUBLE"],["youtube_channel_basic","videos_removed_from_playlists","DOUBLE"],["youtube_channel_basic","views","DOUBLE"],["youtube_channel_basic","watch_time_minutes","DOUBLE"],["youtube_channel_basic","channel_display_name","VARCHAR"],["youtube_channel_basic","channel_subscribers","DOUBLE"],["youtube_channel_basic","channel_views","DOUBLE"],["youtube_channel_basic","channel_watch_time_minutes","DOUBLE"],["youtube_channel_basic","channel_estimated_partner_revenue","DOUBLE"],["youtube_channel_basic","channel_annotations_ctr","DOUBLE"],["youtube_video","id","VARCHAR"],["youtube_video","_fivetran_synced","TIMESTAMP"],["youtube_video","content_details_caption","BOOLEAN"],["youtube_video","content_details_definition","VARCHAR"],["youtube_video","content_details_dimension","VARCHAR"],["youtube_video","content_details_duration","VARCHAR"],["youtube_video","content_details_has_custom_thumbnail","BOOLEAN"],["youtube_video","content_details_licensed_content","BOOLEAN"],["youtube_video","content_details_projection","VARCHAR"],["youtube_video","content_details_region_restriction","VARCHAR"],["youtube_video","etag","VARCHAR"],["youtube_video","kind","VARCHAR"],["youtube_video","player_embed_height","VARCHAR"],["youtube_video","player_embed_html","VARCHAR"],["youtube_video","player_embed_width","VARCHAR"],["youtube_video","privacy_status","VARCHAR"],["youtube_video","snippet_category_id","BIGINT"],["youtube_video","snippet_channel_id","VARCHAR"],["youtube_video","snippet_channel_title","VARCHAR"],["youtube_video","snippet_default_audio_language","VARCHAR"],["youtube_video","snippet_default_language","VARCHAR"],["youtube_video","snippet_description","VARCHAR"],["youtube_video","snippet_live_broadcast_content","VARCHAR"],["youtube_video","snippet_localized","VARCHAR"],["youtube_video","snippet_published_at","TIMESTAMP"],["youtube_video","snippet_tags","VARCHAR"],["youtube_video","snippet_thumbnails","VARCHAR"],["youtube_video","snippet_title","VARCHAR"],["youtube_video","statistics_comment_count","BIGINT"],["youtube_video","statistics_dislike_count","BIGINT"],["youtube_video","statistics_favorite_count","DOUBLE"],["youtube_video","statistics_like_count","BIGINT"],["youtube_video","statistics_view_count","BIGINT"],["youtube_video","status_embeddable","BOOLEAN"],["youtube_video","status_failure_reason","VARCHAR"],["youtube_video","status_license","VARCHAR"],["youtube_video","status_made_for_kids","BOOLEAN"],["youtube_video","status_public_stats_viewable","BOOLEAN"],["youtube_video","status_publish_at","VARCHAR"],["youtube_video","status_rejection_reason","VARCHAR"],["youtube_video","status_self_declared_made_for_kids","BOOLEAN"],["youtube_video","upload_status","VARCHAR"]]}
```


### 核实：频道多版本与两个标题
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。

```sql
SELECT (SELECT count(*) FROM (SELECT channel_id FROM raw.youtube_channel_basic GROUP BY 1 HAVING count(DISTINCT (channel_display_name,channel_subscribers))>1)) duplicate_channels,(SELECT count(*) FROM raw.youtube_video WHERE snippet_channel_title IS NULL) null_title,(SELECT count(*) FROM raw.youtube_video WHERE statistics_like_count>10 AND statistics_like_count%10<>0) fractional_share
```


```json
{"columns":["duplicate_channels","null_title","fractional_share"],"rows":[[0,0,2246]]}
```

## 独立单点重跑

### 024_reruns_impl-023_stg_social_media__youtube_videos.json
[024_reruns_impl-023_stg_social_media__youtube_videos.json](../024_reruns_impl-023_stg_social_media__youtube_videos.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-17 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-17'","count":1}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|152|152|152|503|否|
|L1|152|152|152|351|否|
|L2|152|152|152|218|否|
|L3|152|152|152|218|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"engagement_rate":133,"estimated_shares":66,"page_name":152,"subscribers":152}`
- L1：`{"engagement_rate":133,"estimated_shares":66,"page_name":152}`
- L2：`{"estimated_shares":66,"page_name":152}`
- L3：`{"estimated_shares":66,"page_name":152}`

#### baseline
私有SQL：`data/024_work/impl-023_stg_social_media__youtube_videos/baseline.sql`；SHA-256 `8b0128a01ba19d3413119c138fa6952272fc9e86d452f8081afabf219df494d0`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|152|152|152|503|否|
|L1|152|152|152|351|否|
|L2|152|152|152|218|否|
|L3|152|152|152|218|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"engagement_rate":133,"estimated_shares":66,"page_name":152,"subscribers":152}`
- L1：`{"engagement_rate":133,"estimated_shares":66,"page_name":152}`
- L2：`{"estimated_shares":66,"page_name":152}`
- L3：`{"estimated_shares":66,"page_name":152}`

#### channel_relation
不计参与因素；类别候选A。契约未定同channel多个资料版本如何选；gold DISTINCT原三列。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第2行、offset 27起替换；其他字节相同。
原表达式：
```sql
select channel_id, max(channel_subscribers) as channel_subscribers
    from raw.youtube_channel_basic
    group by channel_id
```

修改后：
```sql
select distinct channel_id, channel_display_name, channel_subscribers
    from raw.youtube_channel_basic
```

私有SQL：`data/024_work/impl-023_stg_social_media__youtube_videos/channel_relation.sql`；SHA-256 `8171de49b91247f08f0d273bb031bd22d43630e0a82a44c4ae756ae62896d9aa`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|152|152|152|503|否|
|L1|152|152|152|351|否|
|L2|152|152|152|218|否|
|L3|152|152|152|218|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"engagement_rate":133,"estimated_shares":66,"page_name":152,"subscribers":152}`
- L1：`{"engagement_rate":133,"estimated_shares":66,"page_name":152}`
- L2：`{"estimated_shares":66,"page_name":152}`
- L3：`{"estimated_shares":66,"page_name":152}`

#### channel_title
不计参与因素；类别候选A。契约未明确channel_title缺失时填Unknown。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第12行、offset 417起替换；其他字节相同。
原表达式：
```sql
v.snippet_channel_title::varchar as channel_title
```

修改后：
```sql
coalesce(v.snippet_channel_title, 'Unknown Channel')::varchar as channel_title
```

私有SQL：`data/024_work/impl-023_stg_social_media__youtube_videos/channel_title.sql`；SHA-256 `c0a9f0a203a937817c0ad2ea420b998703b7246263deee45cd59527459e30b06`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|152|152|152|503|否|
|L1|152|152|152|351|否|
|L2|152|152|152|218|否|
|L3|152|152|152|218|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"engagement_rate":133,"estimated_shares":66,"page_name":152,"subscribers":152}`
- L1：`{"engagement_rate":133,"estimated_shares":66,"page_name":152}`
- L2：`{"estimated_shares":66,"page_name":152}`
- L3：`{"estimated_shares":66,"page_name":152}`

#### page_name
主因；类别候选A。page_name没有明确源列映射，gold取channel_display_name。
相对本轮基线：行减少0，格减少152。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第13行、offset 472起替换；其他字节相同。
原表达式：
```sql
coalesce(v.snippet_channel_title, 'Unknown Channel')::varchar as page_name
```

修改后：
```sql
(select max(channel_display_name) from raw.youtube_channel_basic cb where cb.channel_id=v.snippet_channel_id)::varchar as page_name
```

私有SQL：`data/024_work/impl-023_stg_social_media__youtube_videos/page_name.sql`；SHA-256 `45a9ff93d646973b801cc4d0bc98bd590477bf68159399b9f3a680ac93ebc0d1`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|152|152|152|351|否|
|L1|152|152|133|199|否|
|L2|152|152|66|66|否|
|L3|152|152|66|66|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"engagement_rate":133,"estimated_shares":66,"subscribers":152}`
- L1：`{"engagement_rate":133,"estimated_shares":66}`
- L2：`{"estimated_shares":66}`
- L3：`{"estimated_shares":66}`

#### estimated_shares
参与因素；类别候选O。契约明确FLOOR，gold用CAST四舍五入。
相对本轮基线：行减少0，格减少66。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第20行、offset 978起替换；其他字节相同。
原表达式：
```sql
floor(v.statistics_like_count / 10.0)::bigint
```

修改后：
```sql
cast(v.statistics_like_count / 10.0 as bigint)
```

私有SQL：`data/024_work/impl-023_stg_social_media__youtube_videos/estimated_shares.sql`；SHA-256 `2b2c241e2613f4620f443236cf95c30b5a5cb3b30bc3b6fb1644bee0aa6ee611`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|152|152|152|437|否|
|L1|152|152|152|285|否|
|L2|152|152|152|152|否|
|L3|152|152|152|152|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"engagement_rate":133,"page_name":152,"subscribers":152}`
- L1：`{"engagement_rate":133,"page_name":152}`
- L2：`{"page_name":152}`
- L3：`{"page_name":152}`

#### engagement_shares
参与因素；类别候选O。契约engagement使用estimated_shares，gold此处未FLOOR。
相对本轮基线：行减少0，格减少133。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第24行、offset 1350起替换；其他字节相同。
原表达式：
```sql
floor(v.statistics_like_count / 10.0) else 0 end
```

修改后：
```sql
v.statistics_like_count / 10.0 else 0 end
```

私有SQL：`data/024_work/impl-023_stg_social_media__youtube_videos/engagement_shares.sql`；SHA-256 `d52a7e679aeb255ff907c5cd18eeff757e5a707caca44354d11dce939769c411`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|152|152|152|370|否|
|L1|152|152|152|218|否|
|L2|152|152|152|218|否|
|L3|152|152|152|218|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"estimated_shares":66,"page_name":152,"subscribers":152}`
- L1：`{"estimated_shares":66,"page_name":152}`
- L2：`{"estimated_shares":66,"page_name":152}`
- L3：`{"estimated_shares":66,"page_name":152}`
## 规则问题

无。

