# impl-028 · stg_youtube__video

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**不可评估**；把握：高。

逐张确认直接读取agent/initial同一raw表且内容差集为0；gold读取另一组名称、schema和行数均不同的raw表，满足不可评估。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-028_stg_youtube__video.md](../024_packages/024_impl-028_stg_youtube__video.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/docs/data_contract.yaml`。

```text
206:     - name: stg_youtube__video
207:       description: "Standardized video metadata and statistics. Applies categorical validation and numeric range checks; preserves both raw id and normalized video_id."
208:       source_table: raw.video
209:       columns:
210:         - name: _fivetran_synced
211:           data_type: TIMESTAMP
212:           validation_rules:
213:             - rule: "_fivetran_synced IS NULL OR _fivetran_synced <= CURRENT_TIMESTAMP"
214:               on_failure: nullify_field
215:         - name: snippet_published_at
216:           data_type: TIMESTAMP
217:           validation_rules:
218:             - rule: "snippet_published_at IS NULL OR snippet_published_at <= CURRENT_TIMESTAMP"
219:               on_failure: nullify_field
220:         - name: channel_id
221:           data_type: VARCHAR
222:           validation_rules:
223:             - rule: "channel_id IS NOT NULL AND (LENGTH(TRIM(channel_id)) BETWEEN 12 AND 40)"
224:               on_failure: delete_row
225:             - rule: "channel_id = TRIM(channel_id)"
226:               on_failure: correct
227:         - name: video_title
228:           data_type: VARCHAR
229:         - name: video_description
230:           data_type: VARCHAR
231:         - name: video_thumbnails
232:           data_type: VARCHAR
233:         - name: channel_title
234:           data_type: VARCHAR
235:         - name: video_tags
236:           data_type: VARCHAR
237:         - name: video_category_id
238:           data_type: INTEGER
239:           validation_rules:
240:             - rule: "video_category_id BETWEEN 1 AND 44"
241:               on_failure: nullify_field
242:         - name: video_live_broadcast_content
243:           data_type: VARCHAR
244:         - name: video_default_language
245:           data_type: VARCHAR
246:         - name: video_default_audio_language
247:           data_type: VARCHAR
248:         - name: video_duration
249:           data_type: VARCHAR
250:         - name: video_dimension
251:           data_type: VARCHAR
252:         - name: video_definition
253:           data_type: VARCHAR
254:           validation_rules:
255:             - rule: "video_definition IN ('sd','hd','uhd','4k')"
256:               on_failure: nullify_field
257:         - name: video_caption
258:           data_type: BOOLEAN
259:         - name: video_licensed_content
260:           data_type: BOOLEAN
261:         - name: video_region_restriction_allowed
262:           data_type: VARCHAR
263:         - name: video_region_restriction_blocked
264:           data_type: VARCHAR
265:         - name: video_projection
266:           data_type: VARCHAR
267:         - name: video_has_custom_thumbnail
268:           data_type: BOOLEAN
269:         - name: video_upload_status
270:           data_type: VARCHAR
271:         - name: video_failure_reason
272:           data_type: VARCHAR
273:         - name: video_rejection_reason
274:           data_type: VARCHAR
275:         - name: video_privacy_status
276:           data_type: VARCHAR
277:         - name: video_publish_at
278:           data_type: TIMESTAMP
279:         - name: video_license
280:           data_type: VARCHAR
281:         - name: video_embeddable
282:           data_type: BOOLEAN
283:         - name: video_public_stats_viewable
284:           data_type: BOOLEAN
285:         - name: video_statistics_view_count
286:           data_type: BIGINT
287:           validation_rules:
288:             - rule: "video_statistics_view_count BETWEEN 0 AND 10000000000"
289:               on_failure: nullify_field
290:         - name: video_statistics_like_count
291:           data_type: BIGINT
292:           validation_rules:
293:             - rule: "video_statistics_like_count BETWEEN 0 AND 100000000"
294:               on_failure: nullify_field
295:         - name: video_statistics_dislike_count
296:           data_type: BIGINT
297:           validation_rules:
298:             - rule: "video_statistics_dislike_count BETWEEN 0 AND 10000000"
299:               on_failure: nullify_field
300:         - name: video_statistics_favorite_count
301:           data_type: BIGINT
302:           validation_rules:
303:             - rule: "video_statistics_favorite_count BETWEEN 0 AND 10000000"
304:               on_failure: nullify_field
305:         - name: video_statistics_comment_count
306:           data_type: BIGINT
307:           validation_rules:
308:             - rule: "video_statistics_comment_count BETWEEN 0 AND 10000000"
309:               on_failure: nullify_field
310:         - name: video_id
311:           data_type: VARCHAR
312:           validation_rules:
313:             - rule: "video_id IS NULL OR (LENGTH(TRIM(video_id)) BETWEEN 8 AND 20)"
314:               on_failure: nullify_field
315:             - rule: "video_id = TRIM(video_id)"
316:               on_failure: correct
317:         - name: id
318:           data_type: VARCHAR
319:           validation_rules:
320:             - rule: "id IS NOT NULL AND (LENGTH(TRIM(id)) BETWEEN 8 AND 20)"
321:               on_failure: delete_row
322:         - name: source_relation
323:           data_type: VARCHAR
324: 
325: 
326: 
327: # --------------------------------------------------------------------------- #
328: # PHASE 2: Defines the business logic from staging tables to analytical models. #
329: # --------------------------------------------------------------------------- #
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/sql/staging/stg_youtube__video.sql`；SHA-256 `4272565a49abf078505c01e12b1881fc48f8327df851e9693e7403aeb94f7eb2`。

```text
1: with source_rows as (
2:     select
3:         try_cast(replace("_fivetran_synced", ' UTC', '') as timestamp) as _fivetran_synced,
4:         try_cast(snippet_published_at as timestamp) as snippet_published_at,
5:         snippet_channel_id as channel_id,
6:         snippet_title as video_title,
7:         snippet_description as video_description,
8:         cast(snippet_thumbnails as varchar) as video_thumbnails,
9:         snippet_channel_title as channel_title,
10:         cast(snippet_tags as varchar) as video_tags,
11:         try_cast(snippet_category_id as integer) as video_category_id,
12:         snippet_live_broadcast_content as video_live_broadcast_content,
13:         cast(snippet_default_language as varchar) as video_default_language,
14:         cast(snippet_default_audio_language as varchar) as video_default_audio_language,
15:         content_details_duration as video_duration,
16:         content_details_dimension as video_dimension,
17:         content_details_definition as video_definition,
18:         content_details_caption as video_caption,
19:         content_details_licensed_content as video_licensed_content,
20:         cast(null as varchar) as video_region_restriction_allowed,
21:         cast(null as varchar) as video_region_restriction_blocked,
22:         content_details_projection as video_projection,
23:         content_details_has_custom_thumbnail as video_has_custom_thumbnail,
24:         upload_status as video_upload_status,
25:         cast(null as varchar) as video_failure_reason,
26:         cast(null as varchar) as video_rejection_reason,
27:         privacy_status as video_privacy_status,
28:         try_cast(status_publish_at as timestamp) as video_publish_at,
29:         status_license as video_license,
30:         status_embeddable as video_embeddable,
31:         status_public_stats_viewable as video_public_stats_viewable,
32:         statistics_view_count as video_statistics_view_count,
33:         statistics_like_count as video_statistics_like_count,
34:         statistics_dislike_count as video_statistics_dislike_count,
35:         statistics_favorite_count as video_statistics_favorite_count,
36:         statistics_comment_count as video_statistics_comment_count,
37:         id as video_id,
38:         id,
39:         'youtube_video_data' as source_relation
40:     from raw.youtube_video_data
41: ),
42: validated_rows as (
43:     select
44:         case when _fivetran_synced is null or _fivetran_synced <= current_timestamp then _fivetran_synced else null end as _fivetran_synced,
45:         case when snippet_published_at is null or snippet_published_at <= current_timestamp then snippet_published_at else null end as snippet_published_at,
46:         trim(channel_id) as channel_id,
47:         video_title,
48:         video_description,
49:         video_thumbnails,
50:         channel_title,
51:         video_tags,
52:         case when video_category_id between 1 and 44 then video_category_id else null end as video_category_id,
53:         video_live_broadcast_content,
54:         video_default_language,
55:         video_default_audio_language,
56:         video_duration,
57:         video_dimension,
58:         case when video_definition in ('sd', 'hd', 'uhd', '4k') then video_definition else null end as video_definition,
59:         video_caption,
60:         video_licensed_content,
61:         video_region_restriction_allowed,
62:         video_region_restriction_blocked,
63:         video_projection,
64:         video_has_custom_thumbnail,
65:         video_upload_status,
66:         video_failure_reason,
67:         video_rejection_reason,
68:         video_privacy_status,
69:         video_publish_at,
70:         video_license,
71:         video_embeddable,
72:         video_public_stats_viewable,
73:         case when video_statistics_view_count between 0 and 10000000000 then video_statistics_view_count else null end as video_statistics_view_count,
74:         case when video_statistics_like_count between 0 and 100000000 then video_statistics_like_count else null end as video_statistics_like_count,
75:         case when video_statistics_dislike_count between 0 and 10000000 then video_statistics_dislike_count else null end as video_statistics_dislike_count,
76:         case when video_statistics_favorite_count between 0 and 10000000 then video_statistics_favorite_count else null end as video_statistics_favorite_count,
77:         case when video_statistics_comment_count between 0 and 10000000 then video_statistics_comment_count else null end as video_statistics_comment_count,
78:         case when video_id is null or length(trim(video_id)) between 8 and 20 then trim(video_id) else null end as video_id,
79:         id,
80:         source_relation
81:     from source_rows
82:     where channel_id is not null
83:       and length(trim(channel_id)) between 12 and 40
84:       and id is not null
85:       and length(trim(id)) between 8 and 20
86: )
87: select *
88: from validated_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/sql/staging/stg_youtube__video.sql`；SHA-256 `9eb62ebbf482349ab3d2ff82897d0fc034d25a4049db1dbc6c9c9f89ac4f1594`。

```text
1: -- Staging: YouTube video metadata
2: -- Source: raw.youtube_video_data (information_schema verified)
3: -- Purpose: Standardize column names, map to stable types, validate ranges, drop non-existent fields
4: 
5: with source_data as (
6:     select * from raw.video
7: ),
8: 
9: renamed as (
10:     select
11:         _fivetran_synced,
12:         snippet_published_at,
13:         snippet_channel_id as channel_id,
14:         snippet_title as video_title,
15:         snippet_description as video_description,
16:         snippet_thumbnails as video_thumbnails,
17:         snippet_channel_title as channel_title,
18:         snippet_tags as video_tags,
19:         snippet_category_id as video_category_id,
20:         snippet_live_broadcast_content as video_live_broadcast_content,
21:         snippet_default_language as video_default_language,
22:         snippet_default_audio_language as video_default_audio_language,
23:         content_details_duration as video_duration,
24:         content_details_dimension as video_dimension,
25:         content_details_definition as video_definition,
26:         content_details_caption as video_caption,
27:         content_details_licensed_content as video_licensed_content,
28:         content_details_region_restriction_allowed as video_region_restriction_allowed,
29:         content_details_region_restriction_blocked as video_region_restriction_blocked,
30:         content_details_projection as video_projection,
31:         content_details_has_custom_thumbnail as video_has_custom_thumbnail,
32:         status_upload_status as video_upload_status,
33:         status_failure_reason as video_failure_reason,
34:         status_rejection_reason as video_rejection_reason,
35:         status_privacy_status as video_privacy_status,
36:         status_publish_at as video_publish_at,
37:         status_license as video_license,
38:         status_embeddable as video_embeddable,
39:         status_public_stats_viewable as video_public_stats_viewable,
40:         statistics_view_count as video_statistics_view_count,
41:         statistics_like_count as video_statistics_like_count,
42:         statistics_dislike_count as video_statistics_dislike_count,
43:         statistics_favorite_count as video_statistics_favorite_count,
44:         statistics_comment_count as video_statistics_comment_count,
45:         id,
46:         'youtube_source' as source_relation
47:     from source_data
48: ),
49: 
50: validated as (
51:     select
52:         case when _fivetran_synced <= current_timestamp then _fivetran_synced else NULL end as _fivetran_synced,
53:         case when snippet_published_at <= current_timestamp then snippet_published_at else NULL end as snippet_published_at,
54:         case when length(trim(channel_id)) between 12 and 40 then trim(channel_id) else NULL end as channel_id,
55:         video_title,
56:         video_description,
57:         video_thumbnails,
58:         channel_title,
59:         video_tags,
60:         case when try_cast(video_category_id as integer) between 1 and 44 then try_cast(video_category_id as integer) else NULL end as video_category_id,
61:         video_live_broadcast_content,
62:         video_default_language,
63:         video_default_audio_language,
64:         video_duration,
65:         video_dimension,
66:         case when video_definition in ('sd','hd','uhd','4k') then video_definition else NULL end as video_definition,
67:         video_caption,
68:         video_licensed_content,
69:         video_region_restriction_allowed,
70:         video_region_restriction_blocked,
71:         video_projection,
72:         video_has_custom_thumbnail,
73:         video_upload_status,
74:         video_failure_reason,
75:         video_rejection_reason,
76:         video_privacy_status,
77:         video_publish_at,
78:         video_license,
79:         video_embeddable,
80:         video_public_stats_viewable,
81:         case when try_cast(video_statistics_view_count as bigint) >= 0 and try_cast(video_statistics_view_count as bigint) <= 10000000000 then try_cast(video_statistics_view_count as bigint) else NULL end as video_statistics_view_count,
82:         case when try_cast(video_statistics_like_count as bigint) >= 0 and try_cast(video_statistics_like_count as bigint) <= 100000000 then try_cast(video_statistics_like_count as bigint) else NULL end as video_statistics_like_count,
83:         case when try_cast(video_statistics_dislike_count as bigint) >= 0 and try_cast(video_statistics_dislike_count as bigint) <= 10000000 then try_cast(video_statistics_dislike_count as bigint) else NULL end as video_statistics_dislike_count,
84:         case when try_cast(video_statistics_favorite_count as bigint) >= 0 and try_cast(video_statistics_favorite_count as bigint) <= 10000000 then try_cast(video_statistics_favorite_count as bigint) else NULL end as video_statistics_favorite_count,
85:         case when try_cast(video_statistics_comment_count as bigint) >= 0 and try_cast(video_statistics_comment_count as bigint) <= 10000000 then try_cast(video_statistics_comment_count as bigint) else NULL end as video_statistics_comment_count,
86:         case when length(trim(id)) between 8 and 20 then trim(id) else NULL end as video_id,
87:         id,
88:         source_relation
89:     from renamed
90:     where id is not null and length(trim(id)) between 8 and 20
91:       and channel_id is not null and length(trim(channel_id)) between 12 and 40
92: )
93: 
94: select * from validated
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- 本表主要差异（不可评估）：**针对本表的具体说明**；事件 23、24、55。
原句：

```
原始数据的 `channel_basic` 缺少 contract 字段 `channel_title`、`video_title`、`deleted`、`viewers`、`views_percentage`、部分 card/playlist 字段等；`video` 源缺少或类型与 contract 不同的缩略图、标签、语言、区域限制等字段。
```

event 23：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/23.json`；命令首行：`python - <<'PY'`。
event 24：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/24.json`；原始观察输出。
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

### 核实：直接raw列名类型
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics.duckdb`。

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('youtube_video_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["youtube_video_data","id","VARCHAR"],["youtube_video_data","_fivetran_synced","VARCHAR"],["youtube_video_data","content_details_caption","BOOLEAN"],["youtube_video_data","content_details_definition","VARCHAR"],["youtube_video_data","content_details_dimension","VARCHAR"],["youtube_video_data","content_details_duration","VARCHAR"],["youtube_video_data","content_details_has_custom_thumbnail","BOOLEAN"],["youtube_video_data","content_details_licensed_content","BOOLEAN"],["youtube_video_data","content_details_projection","VARCHAR"],["youtube_video_data","content_details_region_restriction","DOUBLE"],["youtube_video_data","etag","VARCHAR"],["youtube_video_data","kind","VARCHAR"],["youtube_video_data","player_embed_height","DOUBLE"],["youtube_video_data","player_embed_html","VARCHAR"],["youtube_video_data","player_embed_width","DOUBLE"],["youtube_video_data","privacy_status","VARCHAR"],["youtube_video_data","snippet_category_id","BIGINT"],["youtube_video_data","snippet_channel_id","VARCHAR"],["youtube_video_data","snippet_channel_title","VARCHAR"],["youtube_video_data","snippet_default_audio_language","DOUBLE"],["youtube_video_data","snippet_default_language","DOUBLE"],["youtube_video_data","snippet_description","VARCHAR"],["youtube_video_data","snippet_live_broadcast_content","VARCHAR"],["youtube_video_data","snippet_localized","VARCHAR"],["youtube_video_data","snippet_published_at","VARCHAR"],["youtube_video_data","snippet_tags","DOUBLE"],["youtube_video_data","snippet_thumbnails","DOUBLE"],["youtube_video_data","snippet_title","VARCHAR"],["youtube_video_data","statistics_comment_count","BIGINT"],["youtube_video_data","statistics_dislike_count","BIGINT"],["youtube_video_data","statistics_favorite_count","BIGINT"],["youtube_video_data","statistics_like_count","BIGINT"],["youtube_video_data","statistics_view_count","BIGINT"],["youtube_video_data","status_embeddable","BOOLEAN"],["youtube_video_data","status_failure_reason","DOUBLE"],["youtube_video_data","status_license","VARCHAR"],["youtube_video_data","status_made_for_kids","BOOLEAN"],["youtube_video_data","status_public_stats_viewable","BOOLEAN"],["youtube_video_data","status_publish_at","DOUBLE"],["youtube_video_data","status_rejection_reason","DOUBLE"],["youtube_video_data","status_self_declared_made_for_kids","BOOLEAN"],["youtube_video_data","upload_status","VARCHAR"]]}
```


### 诊断：initial_database直接原始表规模
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/youtube_analytics_start.duckdb`。

```sql
SELECT 'raw.youtube_video_data' relation,count(*) n FROM raw.youtube_video_data
```


```json
{"columns":["relation","n"],"rows":[["raw.youtube_video_data",2501]]}
```


### 诊断：agent_database直接原始表规模
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics.duckdb`。

```sql
SELECT 'raw.youtube_video_data' relation,count(*) n FROM raw.youtube_video_data
```


```json
{"columns":["relation","n"],"rows":[["raw.youtube_video_data",2501]]}
```


### 诊断：gold实际raw表清单
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/youtube_analytics.duckdb`。

```sql
SELECT table_name FROM information_schema.tables WHERE table_schema='raw' ORDER BY table_name
```


```json
{"columns":["table_name"],"rows":[["channel_basic_a_2"],["channel_demographics_a_1"],["video"]]}
```


### 诊断：initial-agent逐值差集
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/youtube_analytics_start.duckdb`。

```sql
SELECT count(*) FROM ((SELECT * FROM raw.youtube_video_data EXCEPT ALL SELECT * FROM retained.raw.youtube_video_data) UNION ALL (SELECT * FROM retained.raw.youtube_video_data EXCEPT ALL SELECT * FROM raw.youtube_video_data))
```


```json
{"rows":[[0]]}
```

attached_read_only：`"/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics.duckdb"`
## 独立单点重跑

### 024_reruns_impl-028_stg_youtube__video.json
[024_reruns_impl-028_stg_youtube__video.json](../024_reruns_impl-028_stg_youtube__video.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/youtube_analytics.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2024-01-30 00:00:00+00'","count":2},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2024-01-30'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2501|5|2506|50120|否|
|L1|2501|5|2506|50120|否|
|L2|2501|5|2506|50120|否|
|L3|2501|5|2506|50120|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"video_id":2506,"channel_id":2506,"channel_title":2506,"id":2506,"video_category_id":2506,"video_definition":2506,"video_description":2506,"video_dimension":2506,"video_duration":2506,"video_license":2506,"video_live_broadcast_content":2506,"video_privacy_status":2506,"video_projection":2506,"video_statistics_comment_count":2506,"video_statistics_dislike_count":2506,"video_statistics_favorite_count":2506,"video_statistics_like_count":2506,"video_statistics_view_count":2506,"video_title":2506,"video_upload_status":2506}`
- L1：`{"video_id":2506,"channel_id":2506,"channel_title":2506,"id":2506,"video_category_id":2506,"video_definition":2506,"video_description":2506,"video_dimension":2506,"video_duration":2506,"video_license":2506,"video_live_broadcast_content":2506,"video_privacy_status":2506,"video_projection":2506,"video_statistics_comment_count":2506,"video_statistics_dislike_count":2506,"video_statistics_favorite_count":2506,"video_statistics_like_count":2506,"video_statistics_view_count":2506,"video_title":2506,"video_upload_status":2506}`
- L2：`{"video_id":2506,"channel_id":2506,"channel_title":2506,"id":2506,"video_category_id":2506,"video_definition":2506,"video_description":2506,"video_dimension":2506,"video_duration":2506,"video_license":2506,"video_live_broadcast_content":2506,"video_privacy_status":2506,"video_projection":2506,"video_statistics_comment_count":2506,"video_statistics_dislike_count":2506,"video_statistics_favorite_count":2506,"video_statistics_like_count":2506,"video_statistics_view_count":2506,"video_title":2506,"video_upload_status":2506}`
- L3：`{"video_id":2506,"channel_id":2506,"channel_title":2506,"id":2506,"video_category_id":2506,"video_definition":2506,"video_description":2506,"video_dimension":2506,"video_duration":2506,"video_license":2506,"video_live_broadcast_content":2506,"video_privacy_status":2506,"video_projection":2506,"video_statistics_comment_count":2506,"video_statistics_dislike_count":2506,"video_statistics_favorite_count":2506,"video_statistics_like_count":2506,"video_statistics_view_count":2506,"video_title":2506,"video_upload_status":2506}`

#### baseline
私有SQL：`data/024_work/impl-028_stg_youtube__video/baseline.sql`；SHA-256 `722e7bdcae515231e296ff83d939ad333bd7c3ce257ffd8ba172f8ea5120f32e`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2501|5|2506|50120|否|
|L1|2501|5|2506|50120|否|
|L2|2501|5|2506|50120|否|
|L3|2501|5|2506|50120|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"video_id":2506,"channel_id":2506,"channel_title":2506,"id":2506,"video_category_id":2506,"video_definition":2506,"video_description":2506,"video_dimension":2506,"video_duration":2506,"video_license":2506,"video_live_broadcast_content":2506,"video_privacy_status":2506,"video_projection":2506,"video_statistics_comment_count":2506,"video_statistics_dislike_count":2506,"video_statistics_favorite_count":2506,"video_statistics_like_count":2506,"video_statistics_view_count":2506,"video_title":2506,"video_upload_status":2506}`
- L1：`{"video_id":2506,"channel_id":2506,"channel_title":2506,"id":2506,"video_category_id":2506,"video_definition":2506,"video_description":2506,"video_dimension":2506,"video_duration":2506,"video_license":2506,"video_live_broadcast_content":2506,"video_privacy_status":2506,"video_projection":2506,"video_statistics_comment_count":2506,"video_statistics_dislike_count":2506,"video_statistics_favorite_count":2506,"video_statistics_like_count":2506,"video_statistics_view_count":2506,"video_title":2506,"video_upload_status":2506}`
- L2：`{"video_id":2506,"channel_id":2506,"channel_title":2506,"id":2506,"video_category_id":2506,"video_definition":2506,"video_description":2506,"video_dimension":2506,"video_duration":2506,"video_license":2506,"video_live_broadcast_content":2506,"video_privacy_status":2506,"video_projection":2506,"video_statistics_comment_count":2506,"video_statistics_dislike_count":2506,"video_statistics_favorite_count":2506,"video_statistics_like_count":2506,"video_statistics_view_count":2506,"video_title":2506,"video_upload_status":2506}`
- L3：`{"video_id":2506,"channel_id":2506,"channel_title":2506,"id":2506,"video_category_id":2506,"video_definition":2506,"video_description":2506,"video_dimension":2506,"video_duration":2506,"video_license":2506,"video_live_broadcast_content":2506,"video_privacy_status":2506,"video_projection":2506,"video_statistics_comment_count":2506,"video_statistics_dislike_count":2506,"video_statistics_favorite_count":2506,"video_statistics_like_count":2506,"video_statistics_view_count":2506,"video_title":2506,"video_upload_status":2506}`
## 规则问题

无。

