# impl-023 · social_media_reporting__youtube_videos_reporting

用途：**全量**；层：**intermediate**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**A**；把握：中。

page_name来自channel_title；gold来自上游page_name，152个名称不同。契约没有把“channel title”唯一绑定至两列之一。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-023_social_media_reporting__youtube_videos_reporting.md](../024_packages/024_impl-023_social_media_reporting__youtube_videos_reporting.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。

```text
677:     - name: social_media_reporting__youtube_videos_reporting
678:       description: Standardizes YouTube videos to a unified post-level schema and derives ratios for the last two years of videos
679:       grain: One row per post_id (video_id)
680:       source_models:
681:       - staging.stg_social_media__youtube_videos
682:       business_logic: '- Source and filter: use staging.stg_social_media__youtube_videos rows where video_id is present and video_published_at is within the last two years. - Mapping: - page_id: channel_id cast to text; nulls remain null. - page_name: channel title; if missing, set to ''Unknown Channel''. - post_id: video_id cast to text (always present due to filter). - created_timestamp: video_published_at (always present due to filter). - platform: constant ''youtube''. - post_message: video_description cast to text; original casing and spacing preserved. - clicks and impressions: both set to the video''s views; views come from the source clicks field; default to 0 when missing. - likes, comments, shares: interactions default to 0 when missing; shares use the source estimated_shares. - post_url: passed through from source; may represent a thumbnail URL; may be null. - privacy_status: passed through. - channel_subscribers and channel_total_videos: default to 0; total_videos is 0 in the current SQL. - calculated_engagement_rate: - Use the provided engagement_rate when it is positive; otherwise, if views > 0, compute (likes + comments + shares) divided by views; else 0.0; no rounding or capping. - Derived ratios: - views_per_subscriber: clicks divided by channel_subscribers when subscribers > 0, else 0.0. - likes_per_view_ratio: likes divided by clicks when clicks > 0, else 0.0. - No aggregation, de-duplication, or ordering; rows mirror the filtered source.'
683:       columns:
684:       - name: page_id
685:         data_type: VARCHAR
686:         description: Channel identifier cast to text; nulls preserved
687:       - name: page_name
688:         data_type: VARCHAR
689:         description: Channel title with fallback to 'Unknown Channel' when missing
690:       - name: post_id
691:         data_type: VARCHAR
692:         description: YouTube video identifier cast to text; non-null due to the source filter on video_id
693:         tests:
694:         - not_null
695:       - name: post_message
696:         data_type: VARCHAR
697:         description: Video description text; original casing and whitespace preserved; may be null
698:       - name: created_timestamp
699:         data_type: TIMESTAMP
700:         description: Video publish timestamp limited to the last two years by the filter; non-null
701:         tests:
702:         - not_null
703:       - name: platform
704:         data_type: VARCHAR
705:         description: Constant platform label 'youtube'
706:       - name: clicks
707:         data_type: BIGINT
708:         description: YouTube views treated as clicks; sourced from the staging clicks field; defaults to 0 when missing
709:       - name: impressions
710:         data_type: BIGINT
711:         description: Proxy equal to clicks (views); defaults to 0 when missing
712:       - name: likes
713:         data_type: BIGINT
714:         description: Total likes default to 0 when missing
715:       - name: shares
716:         data_type: BIGINT
717:         description: Estimated shares from the source estimated_shares; default to 0 when missing
718:       - name: comments
719:         data_type: BIGINT
720:         description: Total comments default to 0 when missing
721:       - name: post_url
722:         data_type: VARCHAR
723:         description: URL passed through from source (may be a thumbnail URL); may be null
724:       - name: calculated_engagement_rate
725:         data_type: DOUBLE
726:         description: 'Engagement rate: use provided value when positive; otherwise (likes + comments + shares) divided by views when views > 0; else 0.0; no rounding'
727:         tests:
728:         - calculated_engagement_rate >= 0
729:       - name: privacy_status
730:         data_type: VARCHAR
731:         description: Video privacy status passed through; may be null
732:       - name: channel_subscribers
733:         data_type: DOUBLE
734:         description: Channel subscribers default to 0 when missing
735:       - name: channel_total_videos
736:         data_type: INTEGER
737:         description: Total videos default to 0; currently always 0 in this model
738:       - name: views_per_subscriber
739:         data_type: DOUBLE
740:         description: Clicks divided by channel_subscribers when subscribers > 0; otherwise 0.0; no rounding
741:       - name: likes_per_view_ratio
742:         data_type: DOUBLE
743:         description: Likes divided by clicks when clicks > 0; otherwise 0.0; no rounding
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/intermediate/social_media_reporting__youtube_videos_reporting.sql`；SHA-256 `1f9c049f0b765b28b64a8041765ff202c5778db7fe9a431229ea529e95955909`。

```text
1: with source_videos as (
2:     select *
3:     from staging.stg_social_media__youtube_videos
4:     where video_id is not null
5:       and video_published_at is not null
6:       and video_published_at >= current_date - interval '2 years'
7: ),
8: video_metrics as (
9:     select
10:         cast(channel_id as varchar) as page_id,
11:         coalesce(channel_title, 'Unknown Channel')::varchar as page_name,
12:         cast(video_id as varchar) as post_id,
13:         video_description::varchar as post_message,
14:         video_published_at as created_timestamp,
15:         coalesce(clicks, 0)::bigint as clicks,
16:         coalesce(impressions, 0)::bigint as impressions,
17:         coalesce(likes, 0)::bigint as likes,
18:         coalesce(estimated_shares, 0)::bigint as shares,
19:         coalesce(comments, 0)::bigint as comments,
20:         post_url,
21:         privacy_status,
22:         coalesce(subscribers, 0)::double as channel_subscribers,
23:         coalesce(engagement_rate, 0.0)::double as source_engagement_rate
24:     from source_videos
25: )
26: select
27:     page_id,
28:     page_name,
29:     post_id,
30:     post_message,
31:     created_timestamp,
32:     'youtube'::varchar as platform,
33:     clicks,
34:     impressions,
35:     likes,
36:     shares,
37:     comments,
38:     post_url,
39:     case when source_engagement_rate > 0 then source_engagement_rate
40:          when clicks > 0 then (likes + comments + shares)::double / clicks else 0.0 end as calculated_engagement_rate,
41:     privacy_status,
42:     channel_subscribers,
43:     0::integer as channel_total_videos,
44:     case when channel_subscribers > 0 then clicks::double / channel_subscribers else 0.0 end as views_per_subscriber,
45:     case when clicks > 0 then likes::double / clicks else 0.0 end as likes_per_view_ratio
46: from video_metrics
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/intermediate/social_media_reporting__youtube_videos_reporting.sql`；SHA-256 `1e1c2eef538f9b806e3ec6f0f02847cac4ea04a90dfb4767d87cadf360175055`。

```text
1: -- YouTube videos reporting intermediate table
2: -- Standardizes YouTube video data for unified reporting
3: 
4: WITH youtube_videos_source AS (
5:     SELECT
6:         video_id,
7:         video_published_at,
8:         video_title,
9:         video_description,
10:         channel_id,
11:         page_name AS channel_title,
12:         post_url,
13:         privacy_status,
14:         clicks AS views,
15:         likes,
16:         comments,
17:         estimated_shares AS shares,
18:         engagement_rate,
19:         0 AS favorites,
20:         subscribers,
21:         0 AS total_videos
22:     FROM staging.stg_social_media__youtube_videos
23:     WHERE video_id IS NOT NULL
24:     AND video_published_at >= CURRENT_DATE - INTERVAL '2 years' -- Recent videos only
25: ),
26: 
27: -- Standardize to common schema (follow original DBT logic where views = clicks)
28: youtube_standardized AS (
29:     SELECT
30:         CAST(channel_id AS VARCHAR) AS page_id,
31:         COALESCE(channel_title, 'Unknown Channel') AS page_name,
32:         CAST(video_id AS VARCHAR) AS post_id,
33:         video_published_at AS created_timestamp,
34:         'youtube' AS platform,
35:         -- Use video description as post message per original logic
36:         CAST(video_description AS VARCHAR) AS post_message,
37:         -- YouTube views count as clicks per original logic
38:         COALESCE(views, 0) AS clicks,
39:         -- YouTube doesn't provide impressions directly, estimate based on views
40:         COALESCE(views, 0) AS impressions,
41:         COALESCE(likes, 0) AS likes,
42:         COALESCE(comments, 0) AS comments,
43:         COALESCE(shares, 0) AS shares,
44:         -- Use thumbnail URL as post_url per original logic
45:         CAST(post_url AS VARCHAR) AS post_url,
46:         -- Use calculated or provided engagement rate
47:         CASE
48:             WHEN COALESCE(engagement_rate, 0.0) > 0 THEN engagement_rate
49:             WHEN COALESCE(views, 0) > 0
50:             THEN (COALESCE(likes, 0)::DOUBLE + COALESCE(comments, 0)::DOUBLE + COALESCE(shares, 0)::DOUBLE) / views
51:             ELSE 0.0
52:         END AS calculated_engagement_rate,
53:         -- Platform-specific data
54:         privacy_status,
55:         -- Account metrics
56:         COALESCE(subscribers, 0) AS channel_subscribers,
57:         COALESCE(total_videos, 0) AS channel_total_videos
58:     FROM youtube_videos_source
59: )
60: 
61: SELECT
62:     page_id,
63:     page_name,
64:     post_id,
65:     post_message,
66:     created_timestamp,
67:     platform,
68:     clicks,
69:     impressions,
70:     likes,
71:     shares,
72:     comments,
73:     post_url,
74:     calculated_engagement_rate,
75:     privacy_status,
76:     channel_subscribers,
77:     channel_total_videos,
78:     -- Derived performance metrics
79:     CASE
80:         WHEN COALESCE(channel_subscribers, 0) > 0
81:         THEN clicks::DOUBLE / channel_subscribers
82:         ELSE 0.0
83:     END AS views_per_subscriber,
84:     CASE
85:         WHEN COALESCE(clicks, 0) > 0
86:         THEN COALESCE(likes, 0)::DOUBLE / clicks
87:         ELSE 0.0
88:     END AS likes_per_view_ratio
89: FROM youtube_standardized
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- page_name（A）：**看到了但没提**；事件 17、18、31。
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

### 024_reruns_impl-023_social_media_reporting__youtube_videos_reporting.json
[024_reruns_impl-023_social_media_reporting__youtube_videos_reporting.json](../024_reruns_impl-023_social_media_reporting__youtube_videos_reporting.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-17 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-17'","count":1}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|152|152|152|152|否|
|L1|152|152|152|152|否|
|L2|152|152|152|152|否|
|L3|152|152|152|152|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"page_name":152}`
- L1：`{"page_name":152}`
- L2：`{"page_name":152}`
- L3：`{"page_name":152}`

#### baseline
私有SQL：`data/024_work/impl-023_social_media_reporting__youtube_videos_reporting/baseline.sql`；SHA-256 `7e6b62fd5bbe4cc03010f8c8a0837a3438b41716aa2320856d2a33eef4157abf`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|152|152|152|152|否|
|L1|152|152|152|152|否|
|L2|152|152|152|152|否|
|L3|152|152|152|152|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"page_name":152}`
- L1：`{"page_name":152}`
- L2：`{"page_name":152}`
- L3：`{"page_name":152}`

#### page_name
主因；类别候选A。契约channel title与上游两个名称列未明确对应；gold用page_name。
相对本轮基线：行减少152，格减少152。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第11行、offset 319起替换；其他字节相同。
原表达式：
```sql
coalesce(channel_title,
```

修改后：
```sql
coalesce(page_name,
```

私有SQL：`data/024_work/impl-023_social_media_reporting__youtube_videos_reporting/page_name.sql`；SHA-256 `a90e16697241379e4ed9b9513c90359d6105e6b5f8c65c2226080c0eae891cb8`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|152|152|0|0|是|
|L1|152|152|0|0|是|
|L2|152|152|0|0|是|
|L3|152|152|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

#### impressions
不计参与因素；类别候选C。契约impressions与clicks均来自views/clicks。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第16行、offset 587起替换；其他字节相同。
原表达式：
```sql
coalesce(impressions, 0)::bigint as impressions
```

修改后：
```sql
coalesce(clicks, 0)::bigint as impressions
```

私有SQL：`data/024_work/impl-023_social_media_reporting__youtube_videos_reporting/impressions.sql`；SHA-256 `ef773e1ac09fe0a82476951bf70b1255c4ec51fdc51b1f758c7f044cd579dfbd`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|152|152|152|152|否|
|L1|152|152|152|152|否|
|L2|152|152|152|152|否|
|L3|152|152|152|152|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"page_name":152}`
- L1：`{"page_name":152}`
- L2：`{"page_name":152}`
- L3：`{"page_name":152}`
## 规则问题

契约“channel title”可理解为上游channel_title（O），或两种名称列未明确映射（A）。选择A；没有只凭gold选列判断U。

