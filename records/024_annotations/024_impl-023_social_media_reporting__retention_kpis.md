# impl-023 · social_media_reporting__retention_kpis

用途：**全量**；层：**marts**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**C**；把握：高。

额外过滤NULL page_id，丢掉一个cohort的13个week-offset行；删除这一处过滤L0全匹配。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-023_social_media_reporting__retention_kpis.md](../024_packages/024_impl-023_social_media_reporting__retention_kpis.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。

```text
869:     - name: social_media_reporting__retention_kpis
870:       description: Weekly retention KPIs by platform using posting-activity cohorts over a fixed 13-week window
871:       grain: One row per platform per cohort_week per week_offset
872:       source_models:
873:       - intermediate.social_media_reporting__facebook_posts_reporting
874:       - intermediate.social_media_reporting__instagram_posts_reporting
875:       - intermediate.social_media_reporting__linkedin_posts_reporting
876:       - intermediate.social_media_reporting__twitter_posts_reporting
877:       - intermediate.social_media_reporting__youtube_videos_reporting
878:       business_logic: '- Inputs: - Union page activity from the five source models; only keep rows where created_timestamp is present. - Assign platform as one of: "facebook", "instagram", "linkedin", "twitter", "youtube". - Weekly normalization: - Bucket activity into ISO weeks starting Monday 00:00. - A page is considered active in a week if it posts at least once; multiple posts in the same week do not increase the activity count. - Cohorts: - For each (page_id, platform), set cohort_week to the earliest week with activity. - For each (platform, cohort_week), cohort_pages is the number of unique pages in that cohort. - Observation spine: - Generate week_offset values from 0 to 12 inclusive. - For each cohort, create 13 rows and set target_week to the start of the week that is week_offset weeks after cohort_week; when week_offset = 0, target_week equals cohort_week. - Activity presence: - Build distinct (platform, week, page_id) combinations so each active page-week is counted once. - Retention: - For each spine row, retained_pages is the number of unique pages active on the platform in target_week; this is not limited to members of the cohort. - KPI: - retention_rate = retained_pages divided by cohort_pages when cohort_pages > 0; otherwise 0.0. - No rounding; stored as double precision; values may exceed 1.0 due to the numerator scope. - Output: - Emit platform, cohort_week, week_offset, target_week, cohort_pages, retained_pages, retention_rate. - No explicit ordering is applied.'
879:       columns:
880:       - name: platform
881:         data_type: VARCHAR
882:         description: 'Platform name in lowercase: facebook, instagram, linkedin, twitter, or youtube'
883:         tests:
884:         - not_null
885:       - name: cohort_week
886:         data_type: DATE
887:         description: Start date (Monday) of the first week the page is active for the platform
888:         tests:
889:         - not_null
890:       - name: week_offset
891:         data_type: BIGINT
892:         description: Number of weeks since cohort_week, inclusive 0 to 12
893:         tests:
894:         - not_null
895:         - week_offset BETWEEN 0 AND 12
896:       - name: target_week
897:         data_type: TIMESTAMP
898:         description: Start-of-week timestamp at week_offset weeks after cohort_week; equals cohort_week when offset is 0
899:         tests:
900:         - not_null
901:       - name: cohort_pages
902:         data_type: BIGINT
903:         description: Unique pages in the cohort for each (platform, cohort_week)
904:         tests:
905:         - not_null
906:       - name: retained_pages
907:         data_type: BIGINT
908:         description: Unique pages active on the platform in target_week; one count per page-week; not limited to cohort members
909:         tests:
910:         - not_null
911:       - name: retention_rate
912:         data_type: DOUBLE
913:         description: Ratio of retained_pages to cohort_pages; if cohort_pages is 0 then 0.0; no rounding; may exceed 1.0
914:         tests:
915:         - not_null
916:         - retention_rate >= 0
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/marts/social_media_reporting__retention_kpis.sql`；SHA-256 `7a371897e1ebb2ce230f204682e240d9cb136cdbbffcbae9c3a1b998a0bf5658`。

```text
1: with page_activity as (
2:     select 'facebook'::varchar as platform, page_id, date_trunc('week', created_timestamp)::date as activity_week
3:     from intermediate.social_media_reporting__facebook_posts_reporting where created_timestamp is not null
4:     union all
5:     select 'instagram', page_id, date_trunc('week', created_timestamp)::date
6:     from intermediate.social_media_reporting__instagram_posts_reporting where created_timestamp is not null
7:     union all
8:     select 'linkedin', page_id, date_trunc('week', created_timestamp)::date
9:     from intermediate.social_media_reporting__linkedin_posts_reporting where created_timestamp is not null
10:     union all
11:     select 'twitter', page_id, date_trunc('week', created_timestamp)::date
12:     from intermediate.social_media_reporting__twitter_posts_reporting where created_timestamp is not null
13:     union all
14:     select 'youtube', page_id, date_trunc('week', created_timestamp)::date
15:     from intermediate.social_media_reporting__youtube_videos_reporting where created_timestamp is not null
16: ),
17: active_page_weeks as (
18:     select distinct platform, activity_week, page_id
19:     from page_activity
20:     where page_id is not null
21: ),
22: page_cohorts as (
23:     select platform, page_id, min(activity_week) as cohort_week
24:     from active_page_weeks
25:     group by platform, page_id
26: ),
27: cohort_sizes as (
28:     select platform, cohort_week, count(distinct page_id)::bigint as cohort_pages
29:     from page_cohorts
30:     group by platform, cohort_week
31: ),
32: cohort_spine as (
33:     select c.platform, c.cohort_week, offsets.week_offset::bigint as week_offset,
34:            (c.cohort_week + offsets.week_offset * interval '1 week')::timestamp as target_week,
35:            c.cohort_pages
36:     from cohort_sizes c,
37:          unnest(range(0, 13)) as offsets(week_offset)
38: ),
39: weekly_activity as (
40:     select platform, activity_week, count(distinct page_id)::bigint as retained_pages
41:     from active_page_weeks
42:     group by platform, activity_week
43: )
44: select
45:     s.platform,
46:     s.cohort_week,
47:     s.week_offset,
48:     s.target_week,
49:     s.cohort_pages,
50:     coalesce(a.retained_pages, 0)::bigint as retained_pages,
51:     case when s.cohort_pages > 0 then coalesce(a.retained_pages, 0)::double / s.cohort_pages else 0.0 end as retention_rate
52: from cohort_spine s
53: left join weekly_activity a
54:     on a.platform = s.platform and a.activity_week = cast(s.target_week as date)
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/marts/social_media_reporting__retention_kpis.sql`；SHA-256 `f1ef7b7e7e8df0fc5038be1cecf8d6cebc0c94b14c23753c92306674b96d6e0a`。

```text
1: -- Retention KPIs by platform using posting activity cohorts (marts)
2: -- Layer: marts (may only reference intermediate.*)
3: -- Cohort: first week a page_id posts on a platform
4: -- Retention window: 0..12 weeks after cohort_week
5: -- Constraints: denominator > 0 (cohort_pages), date continuity ensured via week spine per cohort
6: 
7: WITH unified AS (
8:     SELECT page_id, created_timestamp, 'facebook' AS platform
9:     FROM intermediate.social_media_reporting__facebook_posts_reporting
10:     WHERE created_timestamp IS NOT NULL
11: 
12:     UNION ALL
13:     SELECT page_id, created_timestamp, 'instagram' AS platform
14:     FROM intermediate.social_media_reporting__instagram_posts_reporting
15:     WHERE created_timestamp IS NOT NULL
16: 
17:     UNION ALL
18:     SELECT page_id, created_timestamp, 'linkedin' AS platform
19:     FROM intermediate.social_media_reporting__linkedin_posts_reporting
20:     WHERE created_timestamp IS NOT NULL
21: 
22:     UNION ALL
23:     SELECT page_id, created_timestamp, 'twitter' AS platform
24:     FROM intermediate.social_media_reporting__twitter_posts_reporting
25:     WHERE created_timestamp IS NOT NULL
26: 
27:     UNION ALL
28:     SELECT page_id, created_timestamp, 'youtube' AS platform
29:     FROM intermediate.social_media_reporting__youtube_videos_reporting
30:     WHERE created_timestamp IS NOT NULL
31: ),
32: 
33: posts_by_week AS (
34:     SELECT
35:         page_id,
36:         platform,
37:         DATE_TRUNC('week', created_timestamp) AS week,
38:         COUNT(*) AS posts_in_week
39:     FROM unified
40:     GROUP BY page_id, platform, DATE_TRUNC('week', created_timestamp)
41: ),
42: 
43: cohorts AS (
44:     SELECT
45:         page_id,
46:         platform,
47:         MIN(week) AS cohort_week
48:     FROM posts_by_week
49:     GROUP BY page_id, platform
50: ),
51: 
52: cohort_sizes AS (
53:     SELECT platform, cohort_week, COUNT(DISTINCT page_id) AS cohort_pages
54:     FROM cohorts
55:     GROUP BY platform, cohort_week
56: ),
57: 
58: week_span AS (
59:     -- Determine overall min/max weeks for generating spines
60:     SELECT MIN(week) AS min_week, MAX(week) AS max_week FROM posts_by_week
61: ),
62: 
63: span_numbers AS (
64:     -- 0..12 weeks window offsets
65:     SELECT i AS week_offset FROM range(0, 13) AS r(i)
66: ),
67: 
68: cohort_week_spine AS (
69:     -- For each cohort, create target weeks = cohort_week + offset
70:     SELECT
71:         c.platform,
72:         c.cohort_week,
73:         s.week_offset,
74:         c.cohort_week + (s.week_offset || ' weeks')::INTERVAL AS target_week
75:     FROM cohorts c
76:     CROSS JOIN span_numbers s
77: ),
78: 
79: activity AS (
80:     SELECT
81:         p.platform,
82:         p.week AS activity_week,
83:         p.page_id
84:     FROM posts_by_week p
85:     GROUP BY p.platform, p.week, p.page_id
86: ),
87: 
88: retention AS (
89:     SELECT
90:         spine.platform,
91:         spine.cohort_week,
92:         spine.week_offset,
93:         spine.target_week,
94:         COUNT(DISTINCT a.page_id) AS retained_pages
95:     FROM cohort_week_spine spine
96:     LEFT JOIN activity a
97:       ON a.platform = spine.platform
98:      AND a.activity_week = spine.target_week
99:     GROUP BY spine.platform, spine.cohort_week, spine.week_offset, spine.target_week
100: ),
101: 
102: final_retention AS (
103:     SELECT
104:         r.platform,
105:         r.cohort_week,
106:         r.week_offset,
107:         r.target_week,
108:         cs.cohort_pages,
109:         r.retained_pages,
110:         CASE
111:             WHEN cs.cohort_pages > 0 THEN r.retained_pages::DOUBLE / cs.cohort_pages
112:             ELSE 0.0
113:         END AS retention_rate
114:     FROM retention r
115:     LEFT JOIN cohort_sizes cs
116:       ON cs.platform = r.platform AND cs.cohort_week = r.cohort_week
117: )
118: 
119: SELECT *
120: FROM final_retention
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- null_page（C）：**看到了但没提**；事件 19、20、33。
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
## 独立单点重跑

### 024_reruns_impl-023_social_media_reporting__retention_kpis.json
[024_reruns_impl-023_social_media_reporting__retention_kpis.json](../024_reruns_impl-023_social_media_reporting__retention_kpis.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|312|325|13|91|否|
|L1|312|325|13|91|否|
|L2|312|325|13|91|否|
|L3|312|325|13|91|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"platform":13,"cohort_week":13,"week_offset":13,"target_week":13,"cohort_pages":13,"retained_pages":13,"retention_rate":13}`
- L1：`{"platform":13,"cohort_week":13,"week_offset":13,"target_week":13,"cohort_pages":13,"retained_pages":13,"retention_rate":13}`
- L2：`{"platform":13,"cohort_week":13,"week_offset":13,"target_week":13,"cohort_pages":13,"retained_pages":13,"retention_rate":13}`
- L3：`{"platform":13,"cohort_week":13,"week_offset":13,"target_week":13,"cohort_pages":13,"retained_pages":13,"retention_rate":13}`

#### baseline
私有SQL：`data/024_work/impl-023_social_media_reporting__retention_kpis/baseline.sql`；SHA-256 `7a371897e1ebb2ce230f204682e240d9cb136cdbbffcbae9c3a1b998a0bf5658`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|312|325|13|91|否|
|L1|312|325|13|91|否|
|L2|312|325|13|91|否|
|L3|312|325|13|91|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"platform":13,"cohort_week":13,"week_offset":13,"target_week":13,"cohort_pages":13,"retained_pages":13,"retention_rate":13}`
- L1：`{"platform":13,"cohort_week":13,"week_offset":13,"target_week":13,"cohort_pages":13,"retained_pages":13,"retention_rate":13}`
- L2：`{"platform":13,"cohort_week":13,"week_offset":13,"target_week":13,"cohort_pages":13,"retained_pages":13,"retention_rate":13}`
- L3：`{"platform":13,"cohort_week":13,"week_offset":13,"target_week":13,"cohort_pages":13,"retained_pages":13,"retention_rate":13}`

#### cohort_date_type
不计参与因素；类别候选O。契约cohort_week为DATE，gold为TIMESTAMP；此处首个UNION决定活动周类型，其他UNION转型检查。
相对本轮基线：行减少-624，格减少-4368。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第2行、offset 77起替换；其他字节相同。
原表达式：
```sql
date_trunc('week', created_timestamp)::date as activity_week
```

修改后：
```sql
date_trunc('week', created_timestamp) as activity_week
```

私有SQL：`data/024_work/impl-023_social_media_reporting__retention_kpis/cohort_date_type.sql`；SHA-256 `722858f1131af415c4509c37992b5b7e6289fc06f86634ce6d522d10f4670048`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|312|325|637|4459|否|
|L1|312|325|637|4459|否|
|L2|312|325|637|4459|否|
|L3|312|325|637|4459|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"platform":637,"cohort_week":637,"week_offset":637,"target_week":637,"cohort_pages":637,"retained_pages":637,"retention_rate":637}`
- L1：`{"platform":637,"cohort_week":637,"week_offset":637,"target_week":637,"cohort_pages":637,"retained_pages":637,"retention_rate":637}`
- L2：`{"platform":637,"cohort_week":637,"week_offset":637,"target_week":637,"cohort_pages":637,"retained_pages":637,"retention_rate":637}`
- L3：`{"platform":637,"cohort_week":637,"week_offset":637,"target_week":637,"cohort_pages":637,"retained_pages":637,"retention_rate":637}`

#### null_page
主因；类别候选C。契约只过滤缺失created_timestamp；额外删除null page_id。
相对本轮基线：行减少13，格减少91。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第20行、offset 1134起替换；其他字节相同。
原表达式：
```sql
    where page_id is not null
```

修改后：
```sql
    where true
```

私有SQL：`data/024_work/impl-023_social_media_reporting__retention_kpis/null_page.sql`；SHA-256 `a2b024bbc83179f17f6306af9f9656c9c18912b98dd33b6a44f40c3b23a600bd`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|325|325|0|0|是|
|L1|325|325|0|0|是|
|L2|325|325|0|0|是|
|L3|325|325|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 规则问题

无。

