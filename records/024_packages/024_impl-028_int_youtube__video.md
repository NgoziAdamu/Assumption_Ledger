# impl-028 | intermediate | int_youtube__video | 差异：S1；日期 原记录

## 契约完整原文

S3:561–697

```yaml
    - name: int_youtube__video
      description: Video-level metadata with parsed thumbnail URLs and derived publish timestamp/date; all other fields are pass-through from staging.
      grain: One row per input record from staging; duplicates by video_id, if any, are preserved.
      source_models:
      - staging.stg_youtube__video
      business_logic: '- Start with all rows from staging.stg_youtube__video. - Thumbnail URL parsing: - Treat video_thumbnails as a JSON-like string that may contain sections labeled default, medium, and high. - For each section (default/medium/high), locate the first occurrence of that section; within it, if a url field exists, extract the exact string value of url up to the next quote; if the section or url is missing, return NULL. - Do not trim, decode, unescape, or alter case or spacing of the extracted URL. - Published timestamps: - published_at_ts: attempt to parse snippet_published_at as a timestamp; if parsing fails, set to NULL. If the input is a date, the time is 00:00:00. - published_at_date: take the calendar date (day-level) from published_at_ts; if published_at_ts is NULL, this is NULL. - All other columns are carried through exactly from staging with no transformations; NULLs and original formatting are preserved. - No deduplication, aggregation, or ordering is applied; output preserves one row per input record.'
      columns:
      - name: video_id
        data_type: VARCHAR
        description: YouTube video identifier from the source.
        tests:
        - not_null
        - unique
      - name: channel_id
        data_type: VARCHAR
        description: Owning YouTube channel identifier from the source.
        tests: []
      - name: video_title
        data_type: VARCHAR
        description: Video title passed through unchanged.
        tests: []
      - name: video_description
        data_type: VARCHAR
        description: Video description passed through unchanged.
        tests: []
      - name: video_tags
        data_type: VARCHAR
        description: Tags string from the source; delimiter, order, and casing preserved; NULLs unchanged.
        tests: []
      - name: video_category_id
        data_type: INTEGER
        description: YouTube video category ID from the source.
        tests: []
      - name: snippet_published_at
        data_type: DATE
        description: Published date/time value as provided by the source, passed through without change.
        tests: []
      - name: published_at_ts
        data_type: TIMESTAMP
        description: Parsed timestamp from snippet_published_at; unparseable values become NULL; dates default to 00:00:00.
        tests: []
      - name: published_at_date
        data_type: DATE
        description: Calendar date derived from published_at_ts; NULL if published_at_ts is NULL.
        tests: []
      - name: default_thumbnail_url
        data_type: VARCHAR
        description: URL extracted from the 'default' thumbnail section; returns the url value if present, else NULL; no decoding or trimming.
        tests: []
      - name: medium_thumbnail_url
        data_type: VARCHAR
        description: URL extracted from the 'medium' thumbnail section; returns the url value if present, else NULL; no decoding or trimming.
        tests: []
      - name: high_thumbnail_url
        data_type: VARCHAR
        description: URL extracted from the 'high' thumbnail section; returns the url value if present, else NULL; no decoding or trimming.
        tests: []
      - name: video_default_language
        data_type: VARCHAR
        description: Default language code passed through from source.
        tests: []
      - name: video_default_audio_language
        data_type: VARCHAR
        description: Default audio language code passed through from source.
        tests: []
      - name: video_duration
        data_type: VARCHAR
        description: ISO 8601 duration string passed through without parsing.
        tests: []
      - name: video_dimension
        data_type: VARCHAR
        description: Video frame dimension (e.g., 2d/3d) passed through.
        tests: []
      - name: video_definition
        data_type: VARCHAR
        description: Video definition category (e.g., sd/hd) passed through.
        tests: []
      - name: video_caption
        data_type: VARCHAR
        description: Caption availability flag as string passed through; NULLs preserved.
        tests: []
      - name: video_licensed_content
        data_type: VARCHAR
        description: Licensed content flag as string passed through; NULLs preserved.
        tests: []
      - name: video_projection
        data_type: VARCHAR
        description: Projection type passed through from source.
        tests: []
      - name: video_has_custom_thumbnail
        data_type: VARCHAR
        description: Custom thumbnail flag as string passed through; NULLs preserved.
        tests: []
      - name: video_upload_status
        data_type: VARCHAR
        description: Upload status passed through from source.
        tests: []
      - name: video_privacy_status
        data_type: VARCHAR
        description: Privacy status passed through from source.
        tests: []
      - name: video_publish_at
        data_type: VARCHAR
        description: Scheduled publish timestamp as string passed through without parsing.
        tests: []
      - name: video_embeddable
        data_type: VARCHAR
        description: Embeddable flag as string passed through; NULLs preserved.
        tests: []
      - name: video_public_stats_viewable
        data_type: VARCHAR
        description: Public statistics viewability flag as string passed through; NULLs preserved.
        tests: []
      - name: video_statistics_view_count
        data_type: BIGINT
        description: Total view count from source; no adjustments; NULLs preserved.
        tests: []
      - name: video_statistics_like_count
        data_type: BIGINT
        description: Total like count from source; no adjustments; NULLs preserved.
        tests: []
      - name: video_statistics_dislike_count
        data_type: BIGINT
        description: Total dislike count from source; no adjustments; NULLs preserved.
        tests: []
      - name: video_statistics_favorite_count
        data_type: BIGINT
        description: Total favorite count from source; no adjustments; NULLs preserved.
        tests: []
      - name: video_statistics_comment_count
        data_type: BIGINT
        description: Total comment count from source; no adjustments; NULLs preserved.
        tests: []
      - name: source_relation
        data_type: VARCHAR
        description: Identifier of the upstream source relation passed through from staging.
        tests: []
```

## agent 最终 SQL

S4

```sql
with source_rows as (
    select *
    from staging.stg_youtube__video
),
parsed_rows as (
    select
        video_id,
        channel_id,
        video_title,
        video_description,
        video_tags,
        video_category_id,
        snippet_published_at::date as snippet_published_at,
        try_cast(snippet_published_at as timestamp) as published_at_ts,
        cast(try_cast(snippet_published_at as timestamp) as date) as published_at_date,
        regexp_extract(video_thumbnails, '"default"\\s*:\\s*\\{[^}]*"url"\\s*:\\s*"([^"]*)"', 1) as default_thumbnail_url,
        regexp_extract(video_thumbnails, '"medium"\\s*:\\s*\\{[^}]*"url"\\s*:\\s*"([^"]*)"', 1) as medium_thumbnail_url,
        regexp_extract(video_thumbnails, '"high"\\s*:\\s*\\{[^}]*"url"\\s*:\\s*"([^"]*)"', 1) as high_thumbnail_url,
        video_default_language,
        video_default_audio_language,
        video_duration,
        video_dimension,
        video_definition,
        cast(video_caption as varchar) as video_caption,
        cast(video_licensed_content as varchar) as video_licensed_content,
        video_projection,
        cast(video_has_custom_thumbnail as varchar) as video_has_custom_thumbnail,
        video_upload_status,
        video_privacy_status,
        cast(video_publish_at as varchar) as video_publish_at,
        cast(video_embeddable as varchar) as video_embeddable,
        cast(video_public_stats_viewable as varchar) as video_public_stats_viewable,
        video_statistics_view_count,
        video_statistics_like_count,
        video_statistics_dislike_count,
        video_statistics_favorite_count,
        video_statistics_comment_count,
        source_relation
    from source_rows
)
select
    video_id,
    channel_id,
    video_title,
    video_description,
    video_tags,
    video_category_id,
    snippet_published_at,
    published_at_ts,
    published_at_date,
    nullif(default_thumbnail_url, '') as default_thumbnail_url,
    nullif(medium_thumbnail_url, '') as medium_thumbnail_url,
    nullif(high_thumbnail_url, '') as high_thumbnail_url,
    video_default_language,
    video_default_audio_language,
    video_duration,
    video_dimension,
    video_definition,
    video_caption,
    video_licensed_content,
    video_projection,
    video_has_custom_thumbnail,
    video_upload_status,
    video_privacy_status,
    video_publish_at,
    video_embeddable,
    video_public_stats_viewable,
    video_statistics_view_count,
    video_statistics_like_count,
    video_statistics_dislike_count,
    video_statistics_favorite_count,
    video_statistics_comment_count,
    source_relation
from parsed_rows
```

## gold SQL（仅供定位差异）

S5

```sql
-- Intermediate: Video metadata normalized + derived attributes
-- Input: staging.stg_youtube__video
-- Output: one row per video with parsed thumbnails and publish date parts

with src as (
    select * from staging.stg_youtube__video
),

thumbs as (
    select
        *,
        -- extract likely default/medium/high thumbnail urls from json-like string when present
        split_part(video_thumbnails, '"default":', 2) as default_block,
        split_part(video_thumbnails, '"medium":', 2) as medium_block,
        split_part(video_thumbnails, '"high":', 2) as high_block
    from src
),

parsed as (
    select
        video_id,
        channel_id,
        video_title,
        video_description,
        video_tags,
        video_category_id,
        snippet_published_at,
        try_cast(snippet_published_at as timestamp) as published_at_ts,
        cast(date_trunc('day', try_cast(snippet_published_at as timestamp)) as date) as published_at_date,
        -- get url between quotes following url":
        split_part(split_part(default_block, '"url":"', 2), '"', 1) as default_thumbnail_url,
        split_part(split_part(medium_block, '"url":"', 2), '"', 1) as medium_thumbnail_url,
        split_part(split_part(high_block, '"url":"', 2), '"', 1) as high_thumbnail_url,
        video_default_language,
        video_default_audio_language,
        video_duration,
        video_dimension,
        video_definition,
        video_caption,
        video_licensed_content,
        video_projection,
        video_has_custom_thumbnail,
        video_upload_status,
        video_privacy_status,
        video_publish_at,
        video_embeddable,
        video_public_stats_viewable,
        video_statistics_view_count,
        video_statistics_like_count,
        video_statistics_dislike_count,
        video_statistics_favorite_count,
        video_statistics_comment_count,
        source_relation
    from thumbs
)

select * from parsed
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5 | 5 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"video_id":"video_001"}</code> |
| K2 | <code>{"video_id":"video_002"}</code> |
| K3 | <code>{"video_id":"video_003"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| video_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| channel_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_tags | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_category_id | 0 | 0 | 0 | INTEGER | INTEGER |
| default_thumbnail_url | 5 | 5 | 5 | VARCHAR | VARCHAR |
| medium_thumbnail_url | 5 | 5 | 5 | VARCHAR | VARCHAR |
| high_thumbnail_url | 5 | 5 | 5 | VARCHAR | VARCHAR |
| video_default_language | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_default_audio_language | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_duration | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_dimension | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_definition | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_projection | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_upload_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_privacy_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_statistics_view_count | 0 | 0 | 0 | BIGINT | BIGINT |
| video_statistics_like_count | 0 | 0 | 0 | BIGINT | BIGINT |
| video_statistics_dislike_count | 0 | 0 | 0 | BIGINT | BIGINT |
| video_statistics_favorite_count | 0 | 0 | 0 | BIGINT | BIGINT |
| video_statistics_comment_count | 0 | 0 | 0 | BIGINT | BIGINT |

default_thumbnail_url 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | https://i.ytimg.com/vi/default/default.jpg |
| K2 | null | https://i.ytimg.com/vi/default/default.jpg |
| K3 | null | https://i.ytimg.com/vi/default/default.jpg |

medium_thumbnail_url 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | https://i.ytimg.com/vi/default/mqdefault.jpg |
| K2 | null | https://i.ytimg.com/vi/default/mqdefault.jpg |
| K3 | null | https://i.ytimg.com/vi/default/mqdefault.jpg |

high_thumbnail_url 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | https://i.ytimg.com/vi/hqdefault.jpg |
| K2 | null | https://i.ytimg.com/vi/hqdefault.jpg |
| K3 | null | https://i.ytimg.com/vi/hqdefault.jpg |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>7列；[{"column":"video_tags","table_rows":2501},{"column":"default_thumbnail_url","table_rows":2501},{"column":"medium_thumbnail_url","table_rows":2501}]</code> |
| A3_constant_nonnull_column | <code>6列；[{"column":"channel_id","value":"UC2vW_-qeIhF1ESszzuH2pyw"},{"column":"video_projection","value":"rectangular"},{"column":"video_upload_status","value":"processed"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["snippet_published_at","published_at_date"],"nonnull_equal_rows":2501,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["video_embeddable","video_public_stats_viewable"],"nonnull_equal_rows":2501,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["snippet_published_at","published_at_date"],"nonnull_equal_rows":2501,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["video_embeddable","video_public_stats_viewable"],"nonnull_equal_rows":2501,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=10；task_instruction_not_agent_report         description: Video title from int_youtube__video; NULL if no match</code> |

## 轨迹索引（不放输出原文）

本题事件总数：59；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 9 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,260p' run.py</code> | 10808 | true | false |
| 11 | run | <code>wc -l docs/data_contract.yaml &amp;&amp; sed -n '1,250p' docs/data_contract.yaml</code> | 10324 | false | false |
| 17 | run | <code>sed -n '520,800p' docs/data_contract.yaml</code> | 16271 | true | false |
| 25 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; sql/staging/stg_youtube__channel_basic.sql &lt;&lt;'SQL'<br>with source_rows as (<br>    select<br>        try_cast("date" as date) as date_day,<br>        chann</code> | 0 | false | false |
| 29 | run | <code>cat &gt; sql/intermediate/int_youtube__video.sql &lt;&lt;'SQL'<br>with source_rows as (<br>    select *<br>    from staging.stg_youtube__video<br>),<br>parsed_rows as (<br>    select<br>        video_id,<br>        channel_id,<br>      </code> | 0 | false | false |
| 31 | run | <code>cat &gt; sql/marts/youtube__age_demographics_pivot.sql &lt;&lt;'SQL'<br>select<br>    age_pivot.date_day,<br>    age_pivot.video_id,<br>    age_pivot.country_code,<br>    age_pivot."13-17" as "13-17_view_percentage",<br>    age</code> | 7266 | true | false |
| 33 | run | <code>python - &lt;&lt;'PY'<br>p='run.py'; s=open(p).read(); s=s.replace('tables_result = source_conn.execute("SHOW TABLES").fetchall()\n            source_tables = [table[0] for table in tables_result]', 'tables_re</code> | 7173 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics.duckdb',read_only=True)<br>for table in ['staging.stg_youtube__channel_basic','staging.stg_youtube__channel_demographics','staging.stg_yo</code> | 13338 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>p='sql/marts/youtube__video_report.sql'<br>s=open(p).read().replace("""            else sum(average_view_duration_seconds * views) filter (where average_view_duration_seconds is not null)</code> | 1874 | true | false |
| 41 | run | <code>grep regexp_extract -n sql/intermediate/int_youtube__video.sql &amp;&amp; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics.duckdb',read_only=True)<br>print(c.execute('''select date_day,video_id,</code> | 393 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics.duckdb',read_only=True)<br>qs={<br>'raw/staging counts':"select (select count(*) from raw.youtube_channel_basic_data),(select count(*) from </code> | 712 | true | false |
| 47 | run | <code>cat &gt; /workspace/result.md &lt;&lt;'MD'<br>【回复用户】<br><br>已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB SQL、显式 `schema.table` 上</code> | 149 | false | false |
| 51 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'MD'<br>【回复用户】<br><br>已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB </code> | 82 | false | false |
| 55 | run | <code>cat &gt; result.md &lt;&lt;'MD'<br>【回复用户】<br><br>已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB SQL、显式 `schema.table` 上游引用，没有 dbt </code> | 1993 | true | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
Running command: cat > sql/intermediate/int_youtube__video.sql <<'SQL'
```
event 29 / message

```text
from intermediate.int_youtube__video
```
event 29 / message

```text
    from intermediate.int_youtube__video
```
event 31 / message

```text
left join intermediate.int_youtube__video as video_lookup
```
event 31 / message

```text
left join intermediate.int_youtube__video as video_lookup
```
event 31 / message

```text
left join intermediate.int_youtube__video as video_lookup
```
event 37 / message

```text
for table in ['staging.stg_youtube__channel_basic','staging.stg_youtube__channel_demographics','staging.stg_youtube__video','intermediate.int_youtube__channel_basic','intermediate.int_youtube__channel_demographics','intermediate.int_youtube__age_pivot','intermediate.int_youtube__gender_pivot','intermediate.int_youtube__video','marts.youtube__video_metadata','marts.youtube__video_report','marts.youtube__demographics_report','marts.youtube__age_demographics_pivot','marts.youtube__gender_demographics_pivot']:
```
event 41 / message

```text
Running command: grep regexp_extract -n sql/intermediate/int_youtube__video.sql && python - <<'PY'
```
event 47 / message

```text
- **Intermediate:** `int_youtube__channel_basic.sql`、`int_youtube__channel_demographics.sql`、`int_youtube__age_pivot.sql`、`int_youtube__gender_pivot.sql`、`int_youtube__video.sql`
```
event 51 / message

```text
- **Intermediate:** `int_youtube__channel_basic.sql`、`int_youtube__channel_demographics.sql`、`int_youtube__age_pivot.sql`、`int_youtube__gender_pivot.sql`、`int_youtube__video.sql`
```
event 55 / message

```text
- **Intermediate:** `int_youtube__channel_basic.sql`、`int_youtube__channel_demographics.sql`、`int_youtube__age_pivot.sql`、`int_youtube__gender_pivot.sql`、`int_youtube__video.sql`
```

## result.md 本表名原句

S9:8

```text
- **Intermediate:** `int_youtube__channel_basic.sql`、`int_youtube__channel_demographics.sql`、`int_youtube__age_pivot.sql`、`int_youtube__gender_pivot.sql`、`int_youtube__video.sql`
```

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-028.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/sql/intermediate/int_youtube__video.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/sql/intermediate/int_youtube__video.sql`
- S6: `records/006_contract_impl-028.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/result.md`
- S10: `data/024_packages_work/024_impl-028_int_youtube__video/024_impl-028_int_youtube__video.json`
- S11: `data/005_cs_work/impl-028_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/youtube_analytics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions`
