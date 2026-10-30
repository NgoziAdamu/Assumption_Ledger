# impl-028 · int_youtube__video

用途：**全量**；层：**intermediate**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**I**；把握：高。

CS gold staging的5条thumbnail文本均可解析；default/medium/high三处regex各多转义一层，单处修复各减少5格，均I。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-028_int_youtube__video.md](../024_packages/024_impl-028_int_youtube__video.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/docs/data_contract.yaml`。

```text
561:     - name: int_youtube__video
562:       description: Video-level metadata with parsed thumbnail URLs and derived publish timestamp/date; all other fields are pass-through from staging.
563:       grain: One row per input record from staging; duplicates by video_id, if any, are preserved.
564:       source_models:
565:       - staging.stg_youtube__video
566:       business_logic: '- Start with all rows from staging.stg_youtube__video. - Thumbnail URL parsing: - Treat video_thumbnails as a JSON-like string that may contain sections labeled default, medium, and high. - For each section (default/medium/high), locate the first occurrence of that section; within it, if a url field exists, extract the exact string value of url up to the next quote; if the section or url is missing, return NULL. - Do not trim, decode, unescape, or alter case or spacing of the extracted URL. - Published timestamps: - published_at_ts: attempt to parse snippet_published_at as a timestamp; if parsing fails, set to NULL. If the input is a date, the time is 00:00:00. - published_at_date: take the calendar date (day-level) from published_at_ts; if published_at_ts is NULL, this is NULL. - All other columns are carried through exactly from staging with no transformations; NULLs and original formatting are preserved. - No deduplication, aggregation, or ordering is applied; output preserves one row per input record.'
567:       columns:
568:       - name: video_id
569:         data_type: VARCHAR
570:         description: YouTube video identifier from the source.
571:         tests:
572:         - not_null
573:         - unique
574:       - name: channel_id
575:         data_type: VARCHAR
576:         description: Owning YouTube channel identifier from the source.
577:         tests: []
578:       - name: video_title
579:         data_type: VARCHAR
580:         description: Video title passed through unchanged.
581:         tests: []
582:       - name: video_description
583:         data_type: VARCHAR
584:         description: Video description passed through unchanged.
585:         tests: []
586:       - name: video_tags
587:         data_type: VARCHAR
588:         description: Tags string from the source; delimiter, order, and casing preserved; NULLs unchanged.
589:         tests: []
590:       - name: video_category_id
591:         data_type: INTEGER
592:         description: YouTube video category ID from the source.
593:         tests: []
594:       - name: snippet_published_at
595:         data_type: DATE
596:         description: Published date/time value as provided by the source, passed through without change.
597:         tests: []
598:       - name: published_at_ts
599:         data_type: TIMESTAMP
600:         description: Parsed timestamp from snippet_published_at; unparseable values become NULL; dates default to 00:00:00.
601:         tests: []
602:       - name: published_at_date
603:         data_type: DATE
604:         description: Calendar date derived from published_at_ts; NULL if published_at_ts is NULL.
605:         tests: []
606:       - name: default_thumbnail_url
607:         data_type: VARCHAR
608:         description: URL extracted from the 'default' thumbnail section; returns the url value if present, else NULL; no decoding or trimming.
609:         tests: []
610:       - name: medium_thumbnail_url
611:         data_type: VARCHAR
612:         description: URL extracted from the 'medium' thumbnail section; returns the url value if present, else NULL; no decoding or trimming.
613:         tests: []
614:       - name: high_thumbnail_url
615:         data_type: VARCHAR
616:         description: URL extracted from the 'high' thumbnail section; returns the url value if present, else NULL; no decoding or trimming.
617:         tests: []
618:       - name: video_default_language
619:         data_type: VARCHAR
620:         description: Default language code passed through from source.
621:         tests: []
622:       - name: video_default_audio_language
623:         data_type: VARCHAR
624:         description: Default audio language code passed through from source.
625:         tests: []
626:       - name: video_duration
627:         data_type: VARCHAR
628:         description: ISO 8601 duration string passed through without parsing.
629:         tests: []
630:       - name: video_dimension
631:         data_type: VARCHAR
632:         description: Video frame dimension (e.g., 2d/3d) passed through.
633:         tests: []
634:       - name: video_definition
635:         data_type: VARCHAR
636:         description: Video definition category (e.g., sd/hd) passed through.
637:         tests: []
638:       - name: video_caption
639:         data_type: VARCHAR
640:         description: Caption availability flag as string passed through; NULLs preserved.
641:         tests: []
642:       - name: video_licensed_content
643:         data_type: VARCHAR
644:         description: Licensed content flag as string passed through; NULLs preserved.
645:         tests: []
646:       - name: video_projection
647:         data_type: VARCHAR
648:         description: Projection type passed through from source.
649:         tests: []
650:       - name: video_has_custom_thumbnail
651:         data_type: VARCHAR
652:         description: Custom thumbnail flag as string passed through; NULLs preserved.
653:         tests: []
654:       - name: video_upload_status
655:         data_type: VARCHAR
656:         description: Upload status passed through from source.
657:         tests: []
658:       - name: video_privacy_status
659:         data_type: VARCHAR
660:         description: Privacy status passed through from source.
661:         tests: []
662:       - name: video_publish_at
663:         data_type: VARCHAR
664:         description: Scheduled publish timestamp as string passed through without parsing.
665:         tests: []
666:       - name: video_embeddable
667:         data_type: VARCHAR
668:         description: Embeddable flag as string passed through; NULLs preserved.
669:         tests: []
670:       - name: video_public_stats_viewable
671:         data_type: VARCHAR
672:         description: Public statistics viewability flag as string passed through; NULLs preserved.
673:         tests: []
674:       - name: video_statistics_view_count
675:         data_type: BIGINT
676:         description: Total view count from source; no adjustments; NULLs preserved.
677:         tests: []
678:       - name: video_statistics_like_count
679:         data_type: BIGINT
680:         description: Total like count from source; no adjustments; NULLs preserved.
681:         tests: []
682:       - name: video_statistics_dislike_count
683:         data_type: BIGINT
684:         description: Total dislike count from source; no adjustments; NULLs preserved.
685:         tests: []
686:       - name: video_statistics_favorite_count
687:         data_type: BIGINT
688:         description: Total favorite count from source; no adjustments; NULLs preserved.
689:         tests: []
690:       - name: video_statistics_comment_count
691:         data_type: BIGINT
692:         description: Total comment count from source; no adjustments; NULLs preserved.
693:         tests: []
694:       - name: source_relation
695:         data_type: VARCHAR
696:         description: Identifier of the upstream source relation passed through from staging.
697:         tests: []
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/sql/intermediate/int_youtube__video.sql`；SHA-256 `e9e701b5fea0034c77269ebd5deb4a4b5a2b5b1afd357efa12e93aaa5fa7dd05`。

```text
1: with source_rows as (
2:     select *
3:     from staging.stg_youtube__video
4: ),
5: parsed_rows as (
6:     select
7:         video_id,
8:         channel_id,
9:         video_title,
10:         video_description,
11:         video_tags,
12:         video_category_id,
13:         snippet_published_at::date as snippet_published_at,
14:         try_cast(snippet_published_at as timestamp) as published_at_ts,
15:         cast(try_cast(snippet_published_at as timestamp) as date) as published_at_date,
16:         regexp_extract(video_thumbnails, '"default"\\s*:\\s*\\{[^}]*"url"\\s*:\\s*"([^"]*)"', 1) as default_thumbnail_url,
17:         regexp_extract(video_thumbnails, '"medium"\\s*:\\s*\\{[^}]*"url"\\s*:\\s*"([^"]*)"', 1) as medium_thumbnail_url,
18:         regexp_extract(video_thumbnails, '"high"\\s*:\\s*\\{[^}]*"url"\\s*:\\s*"([^"]*)"', 1) as high_thumbnail_url,
19:         video_default_language,
20:         video_default_audio_language,
21:         video_duration,
22:         video_dimension,
23:         video_definition,
24:         cast(video_caption as varchar) as video_caption,
25:         cast(video_licensed_content as varchar) as video_licensed_content,
26:         video_projection,
27:         cast(video_has_custom_thumbnail as varchar) as video_has_custom_thumbnail,
28:         video_upload_status,
29:         video_privacy_status,
30:         cast(video_publish_at as varchar) as video_publish_at,
31:         cast(video_embeddable as varchar) as video_embeddable,
32:         cast(video_public_stats_viewable as varchar) as video_public_stats_viewable,
33:         video_statistics_view_count,
34:         video_statistics_like_count,
35:         video_statistics_dislike_count,
36:         video_statistics_favorite_count,
37:         video_statistics_comment_count,
38:         source_relation
39:     from source_rows
40: )
41: select
42:     video_id,
43:     channel_id,
44:     video_title,
45:     video_description,
46:     video_tags,
47:     video_category_id,
48:     snippet_published_at,
49:     published_at_ts,
50:     published_at_date,
51:     nullif(default_thumbnail_url, '') as default_thumbnail_url,
52:     nullif(medium_thumbnail_url, '') as medium_thumbnail_url,
53:     nullif(high_thumbnail_url, '') as high_thumbnail_url,
54:     video_default_language,
55:     video_default_audio_language,
56:     video_duration,
57:     video_dimension,
58:     video_definition,
59:     video_caption,
60:     video_licensed_content,
61:     video_projection,
62:     video_has_custom_thumbnail,
63:     video_upload_status,
64:     video_privacy_status,
65:     video_publish_at,
66:     video_embeddable,
67:     video_public_stats_viewable,
68:     video_statistics_view_count,
69:     video_statistics_like_count,
70:     video_statistics_dislike_count,
71:     video_statistics_favorite_count,
72:     video_statistics_comment_count,
73:     source_relation
74: from parsed_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/sql/intermediate/int_youtube__video.sql`；SHA-256 `a6ffc5a575dae66047e0494af87d4fe20e6f91d4490af3a291982930d2b5b766`。

```text
1: -- Intermediate: Video metadata normalized + derived attributes
2: -- Input: staging.stg_youtube__video
3: -- Output: one row per video with parsed thumbnails and publish date parts
4: 
5: with src as (
6:     select * from staging.stg_youtube__video
7: ),
8: 
9: thumbs as (
10:     select
11:         *,
12:         -- extract likely default/medium/high thumbnail urls from json-like string when present
13:         split_part(video_thumbnails, '"default":', 2) as default_block,
14:         split_part(video_thumbnails, '"medium":', 2) as medium_block,
15:         split_part(video_thumbnails, '"high":', 2) as high_block
16:     from src
17: ),
18: 
19: parsed as (
20:     select
21:         video_id,
22:         channel_id,
23:         video_title,
24:         video_description,
25:         video_tags,
26:         video_category_id,
27:         snippet_published_at,
28:         try_cast(snippet_published_at as timestamp) as published_at_ts,
29:         cast(date_trunc('day', try_cast(snippet_published_at as timestamp)) as date) as published_at_date,
30:         -- get url between quotes following url":
31:         split_part(split_part(default_block, '"url":"', 2), '"', 1) as default_thumbnail_url,
32:         split_part(split_part(medium_block, '"url":"', 2), '"', 1) as medium_thumbnail_url,
33:         split_part(split_part(high_block, '"url":"', 2), '"', 1) as high_thumbnail_url,
34:         video_default_language,
35:         video_default_audio_language,
36:         video_duration,
37:         video_dimension,
38:         video_definition,
39:         video_caption,
40:         video_licensed_content,
41:         video_projection,
42:         video_has_custom_thumbnail,
43:         video_upload_status,
44:         video_privacy_status,
45:         video_publish_at,
46:         video_embeddable,
47:         video_public_stats_viewable,
48:         video_statistics_view_count,
49:         video_statistics_like_count,
50:         video_statistics_dislike_count,
51:         video_statistics_favorite_count,
52:         video_statistics_comment_count,
53:         source_relation
54:     from thumbs
55: )
56: 
57: select * from parsed
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- default_regex（I）：**针对本表的具体说明**；事件 41、42、55。
原句：

```
视频表 `snippet_thumbnails`、`snippet_tags` 等原始字段类型为 DOUBLE 且样例中为空，不能提供 YAML 描述的 URL/标签字符串；视频 thumbnail URLs 因而为空
```


- medium_regex（I）：**针对本表的具体说明**；事件 41、42、55。
原句：

```
视频表 `snippet_thumbnails`、`snippet_tags` 等原始字段类型为 DOUBLE 且样例中为空，不能提供 YAML 描述的 URL/标签字符串；视频 thumbnail URLs 因而为空
```


- high_regex（I）：**针对本表的具体说明**；事件 41、42、55。
原句：

```
视频表 `snippet_thumbnails`、`snippet_tags` 等原始字段类型为 DOUBLE 且样例中为空，不能提供 YAML 描述的 URL/标签字符串；视频 thumbnail URLs 因而为空
```

event 41：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/41.json`；命令首行：`grep regexp_extract -n sql/intermediate/int_youtube__video.sql && python - <<'PY'`。
event 42：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/42.json`；原始观察输出。
event 55：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/55.json`；命令首行：`cat > result.md <<'MD'`。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB SQL、显式 `schema.table` 上游引用，没有 dbt `ref()`，SQL 文件末尾未添加分号。

## 交付文件

- **Staging:** `stg_youtube__channel_basic.sql`、`stg_youtube__channel_demographics.sql`、`stg_youtube__video.sql`
- **Intermediate:** `int_youtube__channel_basic.sql`、`int_youtube__channel_demographics.sql`、`int_youtube__age_pivot.sql`、`int_youtube__gender_pivot.sql`、`int_youtube__video.sql`
- **Marts:** `youtube__video_metadata.sql`、`youtube__video_report.sql`、`youtube__demographics_report.sql`、`youtube__age_demographics_pivot.sql`、`youtube__gender_demographics_pivot.sql`

## 实现和验证

- Staging 实现字段转换、验证、修正/置空和无效日期/视频记录的行级删除；Intermediate 实现逐行/窗口指标、人口统计透视与视频元数据解析；Marts 实现报表聚合、关联和指定输出字段。
- `python run.py` 成功完成所有模型：3 个 staging、5 个 intermediate、5 个 marts 均执行成功。输出行数依次为 **3,500 / 2,509 / 2,501**；intermediate 为 **3,500 / 2,509 / 2,504 / 1,671 / 2,501**；marts 为 **2,501 / 2,951 / 2,504 / 1,671 / 2,504**。
- 已检查 staging 行数及日期质量、透视占比上下界、非负报表总观看量、报表记录数等；所有执行检查均符合预期。非空 `video_report_id` 唯一。
- 运行时发现 `run.py` 从源数据库读取 `SHOW TABLES`、未限定 `raw` schema，因此对按 `raw` schema 存放的源表得到空表列表。已修正导入逻辑，从 `information_schema.tables` 读取 raw 表并通过 `raw.<table>` 读取，之后全流程通过。

## 合约数据不匹配及残余影响

1. 原始数据的 `channel_basic` 缺少 contract 字段 `channel_title`、`video_title`、`deleted`、`viewers`、`views_percentage`、部分 card/playlist 字段等；`video` 源缺少或类型与 contract 不同的缩略图、标签、语言、区域限制等字段。无法从源端恢复的 staging 字段填为类型正确的 NULL；这部分字段以及相应派生信息不可用，其余记录保留。
2. 数据中有 **2 条** channel_basic 记录的 `video_id` 为空。staging 契约允许该字段为空，且 intermediate 与报表业务逻辑要求保留源记录/分组，因此按要求保留；报表中对应 `video_report_id` 也为空（MD5 输入字符串因 `video_id` 为 NULL 而为空）。因此报表键的 not-null 契约测试对这两行不成立；非空 ID 的键唯一性通过。未自行过滤这些行或伪造替代键，以免改变既定粒度和业务逻辑。
3. 视频表 `snippet_thumbnails`、`snippet_tags` 等原始字段类型为 DOUBLE 且样例中为空，不能提供 YAML 描述的 URL/标签字符串；视频 thumbnail URLs 因而为空，marts 按契约将 NULL 缩略图转换为空字符串。源字段的限制使 URL 解析无实际输入可验证。

上述边界按最小安全假设实施：源 schema 不存在的字段映射成类型化 NULL，不引入虚构信息；重复记录予以保留，未增加契约未要求的去重或排除规则。
```

## 查询

核实查询 **1** 条；代价档：**一条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：agent可见thumbnail非空
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics.duckdb`。

```sql
SELECT count(*) n,count(video_thumbnails) nonnull FROM staging.stg_youtube__video
```


```json
{"columns":["n","nonnull"],"rows":[[2501,0]]}
```


### 诊断：CS gold thumbnail解析输入
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/youtube_analytics.duckdb`。

```sql
SELECT video_id,video_thumbnails FROM staging.stg_youtube__video
```


```json
{"columns":["video_id","video_thumbnails"],"rows":[["video_001","{\"default\":{\"url\":\"https://i.ytimg.com/vi/default/default.jpg\"},\"medium\":{\"url\":\"https://i.ytimg.com/vi/default/mqdefault.jpg\"},\"high\":{\"url\":\"https://i.ytimg.com/vi/hqdefault.jpg\"},\"standard\":{\"url\":\"https://i.ytimg.com/vi/sddefault.jpg\"}}"],["video_002","{\"default\":{\"url\":\"https://i.ytimg.com/vi/default/default.jpg\"},\"medium\":{\"url\":\"https://i.ytimg.com/vi/default/mqdefault.jpg\"},\"high\":{\"url\":\"https://i.ytimg.com/vi/hqdefault.jpg\"},\"standard\":{\"url\":\"https://i.ytimg.com/vi/sddefault.jpg\"}}"],["video_003","{\"default\":{\"url\":\"https://i.ytimg.com/vi/default/default.jpg\"},\"medium\":{\"url\":\"https://i.ytimg.com/vi/default/mqdefault.jpg\"},\"high\":{\"url\":\"https://i.ytimg.com/vi/hqdefault.jpg\"},\"standard\":{\"url\":\"https://i.ytimg.com/vi/sddefault.jpg\"}}"],["video_004","{\"default\":{\"url\":\"https://i.ytimg.com/vi/default/default.jpg\"},\"medium\":{\"url\":\"https://i.ytimg.com/vi/default/mqdefault.jpg\"},\"high\":{\"url\":\"https://i.ytimg.com/vi/hqdefault.jpg\"},\"standard\":{\"url\":\"https://i.ytimg.com/vi/sddefault.jpg\"}}"],["video_005","{\"default\":{\"url\":\"https://i.ytimg.com/vi/default/default.jpg\"},\"medium\":{\"url\":\"https://i.ytimg.com/vi/default/mqdefault.jpg\"},\"high\":{\"url\":\"https://i.ytimg.com/vi/hqdefault.jpg\"},\"standard\":{\"url\":\"https://i.ytimg.com/vi/sddefault.jpg\"}}"]]}
```

## 独立单点重跑

### 024_reruns_impl-028_int_youtube__video.json
[024_reruns_impl-028_int_youtube__video.json](../024_reruns_impl-028_int_youtube__video.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/youtube_analytics.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|15|否|
|L1|5|5|5|15|否|
|L2|5|5|5|15|否|
|L3|5|5|5|15|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L1：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L2：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L3：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`

#### baseline
私有SQL：`data/024_work/impl-028_int_youtube__video/baseline.sql`；SHA-256 `e9e701b5fea0034c77269ebd5deb4a4b5a2b5b1afd357efa12e93aaa5fa7dd05`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|15|否|
|L1|5|5|5|15|否|
|L2|5|5|5|15|否|
|L3|5|5|5|15|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L1：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L2：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L3：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`

#### default_regex
主因；类别候选I。regex显式意图匹配JSON的空白/花括号，但SQL原文双反斜杠匹配了字面反斜杠。
相对本轮基线：行减少0，格减少5。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第16行、offset 463起替换；其他字节相同。
原表达式：
```sql
regexp_extract(video_thumbnails, '"default"\\s*:\\s*\\{[^}]*"url"\\s*:\\s*"([^"]*)"', 1) as default_thumbnail_url
```

修改后：
```sql
regexp_extract(video_thumbnails, '"default"\s*:\s*\{[^}]*"url"\s*:\s*"([^"]*)"', 1) as default_thumbnail_url
```

私有SQL：`data/024_work/impl-028_int_youtube__video/default_regex.sql`；SHA-256 `39d878982d6f869929b5b22ee720921fb2c5476059dd6fdfb2b810ff70e7ec75`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|10|否|
|L1|5|5|5|10|否|
|L2|5|5|5|10|否|
|L3|5|5|5|10|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L1：`{"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L2：`{"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L3：`{"high_thumbnail_url":5,"medium_thumbnail_url":5}`

#### default_missing
不计参与因素；类别候选O。契约缺section/url返回NULL，gold split_part缺失返回空串。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第51行、offset 1904起替换；其他字节相同。
原表达式：
```sql
nullif(default_thumbnail_url, '') as default_thumbnail_url
```

修改后：
```sql
default_thumbnail_url as default_thumbnail_url
```

私有SQL：`data/024_work/impl-028_int_youtube__video/default_missing.sql`；SHA-256 `3d3451570e92504cee3a6c498b0a2865ac9c8e6528595d1f7f1ab3bc13380ea3`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|15|否|
|L1|5|5|5|15|否|
|L2|5|5|5|15|否|
|L3|5|5|5|15|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L1：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L2：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L3：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`

#### medium_regex
主因；类别候选I。regex显式意图匹配JSON的空白/花括号，但SQL原文双反斜杠匹配了字面反斜杠。
相对本轮基线：行减少0，格减少5。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第17行、offset 586起替换；其他字节相同。
原表达式：
```sql
regexp_extract(video_thumbnails, '"medium"\\s*:\\s*\\{[^}]*"url"\\s*:\\s*"([^"]*)"', 1) as medium_thumbnail_url
```

修改后：
```sql
regexp_extract(video_thumbnails, '"medium"\s*:\s*\{[^}]*"url"\s*:\s*"([^"]*)"', 1) as medium_thumbnail_url
```

私有SQL：`data/024_work/impl-028_int_youtube__video/medium_regex.sql`；SHA-256 `236eb7c1842148d69f614ae7baa12d5ce65ba45de4b2ad0469c267d43cafe5b0`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|10|否|
|L1|5|5|5|10|否|
|L2|5|5|5|10|否|
|L3|5|5|5|10|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"default_thumbnail_url":5,"high_thumbnail_url":5}`
- L1：`{"default_thumbnail_url":5,"high_thumbnail_url":5}`
- L2：`{"default_thumbnail_url":5,"high_thumbnail_url":5}`
- L3：`{"default_thumbnail_url":5,"high_thumbnail_url":5}`

#### medium_missing
不计参与因素；类别候选O。契约缺section/url返回NULL，gold split_part缺失返回空串。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第52行、offset 1968起替换；其他字节相同。
原表达式：
```sql
nullif(medium_thumbnail_url, '') as medium_thumbnail_url
```

修改后：
```sql
medium_thumbnail_url as medium_thumbnail_url
```

私有SQL：`data/024_work/impl-028_int_youtube__video/medium_missing.sql`；SHA-256 `1f2a0c351bb83cd6d5fbb004e09bd0e67882152873e427ba646a3a3e2b4c0af7`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|15|否|
|L1|5|5|5|15|否|
|L2|5|5|5|15|否|
|L3|5|5|5|15|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L1：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L2：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L3：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`

#### high_regex
主因；类别候选I。regex显式意图匹配JSON的空白/花括号，但SQL原文双反斜杠匹配了字面反斜杠。
相对本轮基线：行减少0，格减少5。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第18行、offset 707起替换；其他字节相同。
原表达式：
```sql
regexp_extract(video_thumbnails, '"high"\\s*:\\s*\\{[^}]*"url"\\s*:\\s*"([^"]*)"', 1) as high_thumbnail_url
```

修改后：
```sql
regexp_extract(video_thumbnails, '"high"\s*:\s*\{[^}]*"url"\s*:\s*"([^"]*)"', 1) as high_thumbnail_url
```

私有SQL：`data/024_work/impl-028_int_youtube__video/high_regex.sql`；SHA-256 `f730e6cee8a140f22b5c5cca3f82c817f46b37d482856e4b8efab777dfbef788`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|10|否|
|L1|5|5|5|10|否|
|L2|5|5|5|10|否|
|L3|5|5|5|10|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"default_thumbnail_url":5,"medium_thumbnail_url":5}`
- L1：`{"default_thumbnail_url":5,"medium_thumbnail_url":5}`
- L2：`{"default_thumbnail_url":5,"medium_thumbnail_url":5}`
- L3：`{"default_thumbnail_url":5,"medium_thumbnail_url":5}`

#### high_missing
不计参与因素；类别候选O。契约缺section/url返回NULL，gold split_part缺失返回空串。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第53行、offset 2030起替换；其他字节相同。
原表达式：
```sql
nullif(high_thumbnail_url, '') as high_thumbnail_url
```

修改后：
```sql
high_thumbnail_url as high_thumbnail_url
```

私有SQL：`data/024_work/impl-028_int_youtube__video/high_missing.sql`；SHA-256 `69f4270c6357994f5a4edd2a1dcaa20faac532f80289dee527c9e9437ba1602c`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|15|否|
|L1|5|5|5|15|否|
|L2|5|5|5|15|否|
|L3|5|5|5|15|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L1：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L2：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L3：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`

#### published_type
不计参与因素；类别候选C。契约其余列原样透传，agent强制DATE。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第13行、offset 243起替换；其他字节相同。
原表达式：
```sql
snippet_published_at::date as snippet_published_at
```

修改后：
```sql
snippet_published_at as snippet_published_at
```

私有SQL：`data/024_work/impl-028_int_youtube__video/published_type.sql`；SHA-256 `69cbc18439928e2937418010f17bb07fbbf84241a95cdcb26f203bb5fdadeae8`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|5|5|15|否|
|L1|5|5|5|15|否|
|L2|5|5|5|15|否|
|L3|5|5|5|15|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L1：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L2：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
- L3：`{"default_thumbnail_url":5,"high_thumbnail_url":5,"medium_thumbnail_url":5}`
## 规则问题

该说明描述agent自己输入未能验证URL解析；CS改用gold上游后仍须评估本节点代码。不把原输入缺失传播成不可评估。

