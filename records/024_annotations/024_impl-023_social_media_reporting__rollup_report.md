# impl-023 · social_media_reporting__rollup_report

用途：**全量**；层：**marts**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**O**；把握：高。

只有两种rank在impressions并列块内重新分配；去掉rank后L0全匹配，每个并列块rank多重集也完全一致。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-023_social_media_reporting__rollup_report.md](../024_packages/024_impl-023_social_media_reporting__rollup_report.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。

```text
745:     - name: social_media_reporting__rollup_report
746:       description: Unified cross-platform post/video rollup with standardized metrics, platform-specific quality score, rankings, and recent-window filtering
747:       grain: One row per platform + page_id + post_id
748:       source_models:
749:       - intermediate.social_media_reporting__facebook_posts_reporting
750:       - intermediate.social_media_reporting__instagram_posts_reporting
751:       - intermediate.social_media_reporting__linkedin_posts_reporting
752:       - intermediate.social_media_reporting__twitter_posts_reporting
753:       - intermediate.social_media_reporting__youtube_videos_reporting
754:       business_logic: '- Union all five platform models with a platform label: facebook, instagram, linkedin, twitter, youtube; select page_id, page_name, post_id, post_message, created_timestamp, clicks, impressions, likes, shares, comments, post_url. For YouTube, the upstream shares value maps to the unified shares position. - Filter out rows with NULL created_timestamp. - Apply recent data windows relative to the current date: - LinkedIn: keep the last 4 years. - All other platforms: keep the last 2 years. - Standardize content fields: - post_message: default NULL to empty string "". - post_url: default NULL to empty string "". - Standardize metric fields (clicks, impressions, likes, shares, comments): default NULL to 0; no aggregation or deduplication is performed. - Compute engagement_rate: - If impressions > 0: (clicks + likes + shares + comments) / impressions. - Otherwise: 0.0. - No rounding or capping; always non-null and may exceed 1.0. - Compute content_quality_score by platform: - facebook: 75 if impressions > 0, else 50. - instagram: 90 if impressions > 0, else 50. - twitter: 80 if impressions > 0, else 50. - youtube: 95 if clicks > 0, else 50. - linkedin: 70 if impressions > 0, else 50. - Rankings (computed after the above filtering): - daily_platform_rank: within each platform and calendar day of created_timestamp, assign a 1-based rank by sorting impressions descending; ties get arbitrary order. - platform_lifetime_rank: within each platform across the filtered dataset, assign a 1-based rank by sorting impressions descending; ties get arbitrary order. - Final result ordering for display: created_timestamp descending, then engagement_rate descending.'
755:       columns:
756:       - name: page_id
757:         data_type: VARCHAR
758:         description: Source page/account identifier within a platform
759:         tests:
760:         - not_null
761:       - name: page_name
762:         data_type: VARCHAR
763:         description: Source page/account display name; may be null
764:       - name: post_id
765:         data_type: VARCHAR
766:         description: Source post/media identifier within platform and page
767:         tests:
768:         - not_null
769:       - name: created_timestamp
770:         data_type: TIMESTAMP
771:         description: Post/media publish timestamp; rows with NULL are excluded
772:         tests:
773:         - not_null
774:       - name: platform
775:         data_type: VARCHAR
776:         description: 'Platform label: facebook, instagram, linkedin, twitter, youtube'
777:         tests:
778:         - not_null
779:       - name: post_message
780:         data_type: VARCHAR
781:         description: Post/media text; NULL defaults to empty string; casing and whitespace preserved
782:       - name: post_url
783:         data_type: VARCHAR
784:         description: Canonical post/media URL; NULL defaults to empty string; casing and whitespace preserved
785:       - name: clicks
786:         data_type: HUGEINT
787:         description: Total clicks; NULL defaults to 0; used in engagement_rate and YouTube quality rule
788:       - name: impressions
789:         data_type: HUGEINT
790:         description: Total impressions; NULL defaults to 0; denominator for engagement_rate and several quality rules
791:       - name: likes
792:         data_type: HUGEINT
793:         description: Total likes; NULL defaults to 0; included in engagement_rate numerator
794:       - name: shares
795:         data_type: HUGEINT
796:         description: Total shares; NULL defaults to 0; included in engagement_rate numerator; for YouTube, upstream shares are used
797:       - name: comments
798:         data_type: HUGEINT
799:         description: Total comments; NULL defaults to 0; included in engagement_rate numerator
800:       - name: engagement_rate
801:         data_type: DOUBLE
802:         description: If impressions > 0, (clicks + likes + shares + comments) / impressions; else 0.0; not rounded or capped; never null
803:       - name: content_quality_score
804:         data_type: INTEGER
805:         description: 'Platform rule-based score: FB 75 if impressions > 0; IG 90 if impressions > 0; TW 80 if impressions > 0; YT 95 if clicks > 0; LI 70 if impressions > 0; otherwise 50'
806:       - name: daily_platform_rank
807:         data_type: BIGINT
808:         description: 1-based rank within each platform and calendar day by impressions descending; ties receive arbitrary order
809:       - name: platform_lifetime_rank
810:         data_type: BIGINT
811:         description: 1-based rank within each platform across the filtered dataset by impressions descending; ties receive arbitrary order
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/marts/social_media_reporting__rollup_report.sql`；SHA-256 `3331cb9ab49a8556109b392d6179b0eadcb88c7b90003eefba502a0c8fd75cc3`。

```text
1: with all_posts as (
2:     select page_id, page_name, post_id, post_message, created_timestamp, platform,
3:            clicks, impressions, likes, shares, comments, post_url
4:     from intermediate.social_media_reporting__facebook_posts_reporting
5:     union all
6:     select page_id, page_name, post_id, post_message, created_timestamp, platform,
7:            clicks, impressions, likes, shares, comments, post_url
8:     from intermediate.social_media_reporting__instagram_posts_reporting
9:     union all
10:     select page_id, page_name, post_id, post_message, created_timestamp, platform,
11:            clicks, impressions, likes, shares, comments, post_url
12:     from intermediate.social_media_reporting__linkedin_posts_reporting
13:     union all
14:     select page_id, page_name, post_id, post_message, created_timestamp, platform,
15:            clicks, impressions, likes, shares, comments, post_url
16:     from intermediate.social_media_reporting__twitter_posts_reporting
17:     union all
18:     select page_id, page_name, post_id, post_message, created_timestamp, platform,
19:            clicks, impressions, likes, shares, comments, post_url
20:     from intermediate.social_media_reporting__youtube_videos_reporting
21: ),
22: recent_posts as (
23:     select
24:         page_id, page_name, post_id, coalesce(post_message, '')::varchar as post_message,
25:         created_timestamp, platform,
26:         coalesce(clicks, 0)::hugeint as clicks,
27:         coalesce(impressions, 0)::hugeint as impressions,
28:         coalesce(likes, 0)::hugeint as likes,
29:         coalesce(shares, 0)::hugeint as shares,
30:         coalesce(comments, 0)::hugeint as comments,
31:         coalesce(post_url, '')::varchar as post_url
32:     from all_posts
33:     where created_timestamp is not null
34:       and ((platform = 'linkedin' and created_timestamp >= current_date - interval '4 years')
35:         or (platform <> 'linkedin' and created_timestamp >= current_date - interval '2 years'))
36: ),
37: scored_posts as (
38:     select *,
39:         case when impressions > 0 then (clicks + likes + shares + comments)::double / impressions else 0.0 end as engagement_rate,
40:         case platform
41:             when 'facebook' then case when impressions > 0 then 75 else 50 end
42:             when 'instagram' then case when impressions > 0 then 90 else 50 end
43:             when 'twitter' then case when impressions > 0 then 80 else 50 end
44:             when 'youtube' then case when clicks > 0 then 95 else 50 end
45:             when 'linkedin' then case when impressions > 0 then 70 else 50 end
46:             else 50 end::integer as content_quality_score
47:     from recent_posts
48: ),
49: ranked_posts as (
50:     select *,
51:         row_number() over (partition by platform, cast(created_timestamp as date) order by impressions desc) as daily_platform_rank,
52:         row_number() over (partition by platform order by impressions desc) as platform_lifetime_rank
53:     from scored_posts
54: )
55: select
56:     page_id, page_name, post_id, created_timestamp, platform, post_message, post_url,
57:     clicks, impressions, likes, shares, comments, engagement_rate, content_quality_score,
58:     daily_platform_rank, platform_lifetime_rank
59: from ranked_posts
60: order by created_timestamp desc, engagement_rate desc
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/marts/social_media_reporting__rollup_report.sql`；SHA-256 `7f7dda8e6294ddcbb31e012dffaf83ad3b5977c1f7544322dbc039c8fa440c24`。

```text
1: -- Social media unified rollup report
2: -- Combines all platform data into a single unified reporting table
3: 
4: WITH unified_data AS (
5:     -- Facebook data
6:     SELECT
7:         page_id,
8:         page_name,
9:         post_id,
10:         post_message,
11:         created_timestamp,
12:         'facebook' AS platform,
13:         clicks,
14:         impressions,
15:         likes,
16:         shares,
17:         comments,
18:         post_url
19:     FROM intermediate.social_media_reporting__facebook_posts_reporting
20: 
21:     UNION ALL
22: 
23:     -- Instagram data
24:     SELECT
25:         page_id,
26:         page_name,
27:         post_id,
28:         post_message,
29:         created_timestamp,
30:         'instagram' AS platform,
31:         clicks,
32:         impressions,
33:         likes,
34:         shares,
35:         comments,
36:         post_url
37:     FROM intermediate.social_media_reporting__instagram_posts_reporting
38: 
39:     UNION ALL
40: 
41:     -- LinkedIn data
42:     SELECT
43:         page_id,
44:         page_name,
45:         post_id,
46:         post_message,
47:         created_timestamp,
48:         'linkedin' AS platform,
49:         clicks,
50:         impressions,
51:         likes,
52:         shares,
53:         comments,
54:         post_url
55:     FROM intermediate.social_media_reporting__linkedin_posts_reporting
56: 
57:     UNION ALL
58: 
59:     -- Twitter data
60:     SELECT
61:         page_id,
62:         page_name,
63:         post_id,
64:         post_message,
65:         created_timestamp,
66:         'twitter' AS platform,
67:         clicks,
68:         impressions,
69:         likes,
70:         shares,
71:         comments,
72:         post_url
73:     FROM intermediate.social_media_reporting__twitter_posts_reporting
74: 
75:     UNION ALL
76: 
77:     -- YouTube data
78:     SELECT
79:         page_id,
80:         page_name,
81:         post_id,
82:         post_message,
83:         created_timestamp,
84:         'youtube' AS platform,
85:         clicks,
86:         impressions,
87:         likes,
88:         shares AS estimated_shares,
89:         comments,
90:         post_url
91:     FROM intermediate.social_media_reporting__youtube_videos_reporting
92: )
93: 
94: -- Final unified rollup
95: SELECT
96:     -- Primary identifiers
97:     page_id,
98:     page_name,
99:     post_id,
100:     created_timestamp,
101:     platform,
102: 
103:     -- Unified content metrics
104:     COALESCE(post_message, '') AS post_message,
105:     COALESCE(post_url, '') AS post_url,
106: 
107:     -- Standardized engagement metrics
108:     COALESCE(clicks, 0) AS clicks,
109:     COALESCE(impressions, 0) AS impressions,
110:     COALESCE(likes, 0) AS likes,
111:     COALESCE(shares, 0) AS shares,
112:     COALESCE(comments, 0) AS comments,
113: 
114:     -- Engagement metrics
115:     CASE
116:         WHEN COALESCE(impressions, 0) > 0
117:         THEN (COALESCE(clicks, 0)::DOUBLE + COALESCE(likes, 0)::DOUBLE + COALESCE(shares, 0)::DOUBLE + COALESCE(comments, 0)::DOUBLE) / impressions
118:         ELSE 0.0
119:     END AS engagement_rate,
120: 
121:     -- Platform-based quality score
122:     CASE
123:         WHEN platform = 'facebook' AND COALESCE(impressions, 0) > 0 THEN 75
124:         WHEN platform = 'instagram' AND COALESCE(impressions, 0) > 0 THEN 90
125:         WHEN platform = 'twitter' AND COALESCE(impressions, 0) > 0 THEN 80
126:         WHEN platform = 'youtube' AND COALESCE(clicks, 0) > 0 THEN 95
127:         WHEN platform = 'linkedin' AND COALESCE(impressions, 0) > 0 THEN 70
128:         ELSE 50
129:     END AS content_quality_score,
130: 
131:     -- Per-platform rankings
132:     ROW_NUMBER() OVER (PARTITION BY platform, DATE_TRUNC('day', created_timestamp) ORDER BY impressions DESC) AS daily_platform_rank,
133:     ROW_NUMBER() OVER (PARTITION BY platform ORDER BY impressions DESC) AS platform_lifetime_rank
134: 
135: FROM unified_data
136: WHERE (
137:     platform <> 'linkedin' AND created_timestamp >= CURRENT_DATE - INTERVAL '2 years'
138: ) OR (
139:     platform = 'linkedin' AND created_timestamp >= CURRENT_DATE - INTERVAL '4 years'
140: ) -- Recent data windows by platform
141: AND created_timestamp IS NOT NULL
142: ORDER BY created_timestamp DESC, engagement_rate DESC
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- 本表主要差异（O）：**看到了但没提**；事件 19、20、33。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 19：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/19.json`；命令首行：`sed -n '790,1010p' docs/data_contract.yaml`。
event 20：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/20.json`；原始观察输出。
event 33：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/33.json`；命令首行：`cat >> /tmp/write_sql.py <<'PY'`。

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

### 诊断：排除并列顺序派生列后的整表诊断
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`。

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
      and ((platform = 'linkedin' and created_timestamp >= DATE '2025-10-13' - interval '4 years')
        or (platform <> 'linkedin' and created_timestamp >= DATE '2025-10-13' - interval '2 years'))
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

|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|584|584|0|0|是|
|L1|584|584|0|0|是|
|L2|584|584|0|0|是|
|L3|584|584|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
excluded：`["daily_platform_rank","platform_lifetime_rank"]`
tie_permutations：`[{"sql":"SELECT count(*) FROM ((SELECT platform,date_trunc('day',created_timestamp),impressions,list(daily_platform_rank ORDER BY daily_platform_rank) ranks FROM pred GROUP BY ALL EXCEPT ALL SELECT platform,date_trunc('day',created_timestamp),impressions,list(daily_platform_rank ORDER BY daily_platform_rank) ranks FROM src.marts.social_media_reporting__rollup_report GROUP BY ALL) UNION ALL (SELECT platform,date_trunc('day',created_timestamp),impressions,list(daily_platform_rank ORDER BY daily_platform_rank) ranks FROM src.marts.social_media_reporting__rollup_report GROUP BY ALL EXCEPT ALL SELECT platform,date_trunc('day',created_timestamp),impressions,list(daily_platform_rank ORDER BY daily_platform_rank) ranks FROM pred GROUP BY ALL))","difference_groups":0},{"sql":"SELECT count(*) FROM ((SELECT platform,impressions,list(platform_lifetime_rank ORDER BY platform_lifetime_rank) ranks FROM pred GROUP BY ALL EXCEPT ALL SELECT platform,impressions,list(platform_lifetime_rank ORDER BY platform_lifetime_rank) ranks FROM src.marts.social_media_reporting__rollup_report GROUP BY ALL) UNION ALL (SELECT platform,impressions,list(platform_lifetime_rank ORDER BY platform_lifetime_rank) ranks FROM src.marts.social_media_reporting__rollup_report GROUP BY ALL EXCEPT ALL SELECT platform,impressions,list(platform_lifetime_rank ORDER BY platform_lifetime_rank) ranks FROM pred GROUP BY ALL))","difference_groups":0}]`
## 独立单点重跑

### 024_reruns_impl-023_social_media_reporting__rollup_report.json
[024_reruns_impl-023_social_media_reporting__rollup_report.json](../024_reruns_impl-023_social_media_reporting__rollup_report.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":2}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|0|584|584|7592|否|
|L1|0|584|584|7592|否|
|L2|0|584|584|7592|否|
|L3|0|584|584|7592|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"page_id":584,"post_id":584,"clicks":584,"comments":584,"content_quality_score":584,"created_timestamp":584,"daily_platform_rank":584,"engagement_rate":584,"impressions":584,"likes":584,"platform":584,"platform_lifetime_rank":584,"shares":584}`
- L1：`{"page_id":584,"post_id":584,"clicks":584,"comments":584,"content_quality_score":584,"created_timestamp":584,"daily_platform_rank":584,"engagement_rate":584,"impressions":584,"likes":584,"platform":584,"platform_lifetime_rank":584,"shares":584}`
- L2：`{"page_id":584,"post_id":584,"clicks":584,"comments":584,"content_quality_score":584,"created_timestamp":584,"daily_platform_rank":584,"engagement_rate":584,"impressions":584,"likes":584,"platform":584,"platform_lifetime_rank":584,"shares":584}`
- L3：`{"page_id":584,"post_id":584,"clicks":584,"comments":584,"content_quality_score":584,"created_timestamp":584,"daily_platform_rank":584,"engagement_rate":584,"impressions":584,"likes":584,"platform":584,"platform_lifetime_rank":584,"shares":584}`

#### baseline
私有SQL：`data/024_work/impl-023_social_media_reporting__rollup_report/baseline.sql`；SHA-256 `793977fde454f871a2f7a0244e9029524cdb2d3cb1bc7a1fe38e00b5fb011714`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|584|584|260|307|否|
|L1|584|584|260|307|否|
|L2|584|584|260|307|否|
|L3|584|584|260|307|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"daily_platform_rank":47,"platform_lifetime_rank":260}`
- L1：`{"daily_platform_rank":47,"platform_lifetime_rank":260}`
- L2：`{"daily_platform_rank":47,"platform_lifetime_rank":260}`
- L3：`{"daily_platform_rank":47,"platform_lifetime_rank":260}`
## 规则问题

无。

