# impl-028 | staging | stg_youtube__video | 差异：S1；日期 2024-01-30

## 契约完整原文

S3:206–329

```yaml
    - name: stg_youtube__video
      description: "Standardized video metadata and statistics. Applies categorical validation and numeric range checks; preserves both raw id and normalized video_id."
      source_table: raw.video
      columns:
        - name: _fivetran_synced
          data_type: TIMESTAMP
          validation_rules:
            - rule: "_fivetran_synced IS NULL OR _fivetran_synced <= CURRENT_TIMESTAMP"
              on_failure: nullify_field
        - name: snippet_published_at
          data_type: TIMESTAMP
          validation_rules:
            - rule: "snippet_published_at IS NULL OR snippet_published_at <= CURRENT_TIMESTAMP"
              on_failure: nullify_field
        - name: channel_id
          data_type: VARCHAR
          validation_rules:
            - rule: "channel_id IS NOT NULL AND (LENGTH(TRIM(channel_id)) BETWEEN 12 AND 40)"
              on_failure: delete_row
            - rule: "channel_id = TRIM(channel_id)"
              on_failure: correct
        - name: video_title
          data_type: VARCHAR
        - name: video_description
          data_type: VARCHAR
        - name: video_thumbnails
          data_type: VARCHAR
        - name: channel_title
          data_type: VARCHAR
        - name: video_tags
          data_type: VARCHAR
        - name: video_category_id
          data_type: INTEGER
          validation_rules:
            - rule: "video_category_id BETWEEN 1 AND 44"
              on_failure: nullify_field
        - name: video_live_broadcast_content
          data_type: VARCHAR
        - name: video_default_language
          data_type: VARCHAR
        - name: video_default_audio_language
          data_type: VARCHAR
        - name: video_duration
          data_type: VARCHAR
        - name: video_dimension
          data_type: VARCHAR
        - name: video_definition
          data_type: VARCHAR
          validation_rules:
            - rule: "video_definition IN ('sd','hd','uhd','4k')"
              on_failure: nullify_field
        - name: video_caption
          data_type: BOOLEAN
        - name: video_licensed_content
          data_type: BOOLEAN
        - name: video_region_restriction_allowed
          data_type: VARCHAR
        - name: video_region_restriction_blocked
          data_type: VARCHAR
        - name: video_projection
          data_type: VARCHAR
        - name: video_has_custom_thumbnail
          data_type: BOOLEAN
        - name: video_upload_status
          data_type: VARCHAR
        - name: video_failure_reason
          data_type: VARCHAR
        - name: video_rejection_reason
          data_type: VARCHAR
        - name: video_privacy_status
          data_type: VARCHAR
        - name: video_publish_at
          data_type: TIMESTAMP
        - name: video_license
          data_type: VARCHAR
        - name: video_embeddable
          data_type: BOOLEAN
        - name: video_public_stats_viewable
          data_type: BOOLEAN
        - name: video_statistics_view_count
          data_type: BIGINT
          validation_rules:
            - rule: "video_statistics_view_count BETWEEN 0 AND 10000000000"
              on_failure: nullify_field
        - name: video_statistics_like_count
          data_type: BIGINT
          validation_rules:
            - rule: "video_statistics_like_count BETWEEN 0 AND 100000000"
              on_failure: nullify_field
        - name: video_statistics_dislike_count
          data_type: BIGINT
          validation_rules:
            - rule: "video_statistics_dislike_count BETWEEN 0 AND 10000000"
              on_failure: nullify_field
        - name: video_statistics_favorite_count
          data_type: BIGINT
          validation_rules:
            - rule: "video_statistics_favorite_count BETWEEN 0 AND 10000000"
              on_failure: nullify_field
        - name: video_statistics_comment_count
          data_type: BIGINT
          validation_rules:
            - rule: "video_statistics_comment_count BETWEEN 0 AND 10000000"
              on_failure: nullify_field
        - name: video_id
          data_type: VARCHAR
          validation_rules:
            - rule: "video_id IS NULL OR (LENGTH(TRIM(video_id)) BETWEEN 8 AND 20)"
              on_failure: nullify_field
            - rule: "video_id = TRIM(video_id)"
              on_failure: correct
        - name: id
          data_type: VARCHAR
          validation_rules:
            - rule: "id IS NOT NULL AND (LENGTH(TRIM(id)) BETWEEN 8 AND 20)"
              on_failure: delete_row
        - name: source_relation
          data_type: VARCHAR



# --------------------------------------------------------------------------- #
# PHASE 2: Defines the business logic from staging tables to analytical models. #
# --------------------------------------------------------------------------- #
```

## agent 最终 SQL

S4

```sql
with source_rows as (
    select
        try_cast(replace("_fivetran_synced", ' UTC', '') as timestamp) as _fivetran_synced,
        try_cast(snippet_published_at as timestamp) as snippet_published_at,
        snippet_channel_id as channel_id,
        snippet_title as video_title,
        snippet_description as video_description,
        cast(snippet_thumbnails as varchar) as video_thumbnails,
        snippet_channel_title as channel_title,
        cast(snippet_tags as varchar) as video_tags,
        try_cast(snippet_category_id as integer) as video_category_id,
        snippet_live_broadcast_content as video_live_broadcast_content,
        cast(snippet_default_language as varchar) as video_default_language,
        cast(snippet_default_audio_language as varchar) as video_default_audio_language,
        content_details_duration as video_duration,
        content_details_dimension as video_dimension,
        content_details_definition as video_definition,
        content_details_caption as video_caption,
        content_details_licensed_content as video_licensed_content,
        cast(null as varchar) as video_region_restriction_allowed,
        cast(null as varchar) as video_region_restriction_blocked,
        content_details_projection as video_projection,
        content_details_has_custom_thumbnail as video_has_custom_thumbnail,
        upload_status as video_upload_status,
        cast(null as varchar) as video_failure_reason,
        cast(null as varchar) as video_rejection_reason,
        privacy_status as video_privacy_status,
        try_cast(status_publish_at as timestamp) as video_publish_at,
        status_license as video_license,
        status_embeddable as video_embeddable,
        status_public_stats_viewable as video_public_stats_viewable,
        statistics_view_count as video_statistics_view_count,
        statistics_like_count as video_statistics_like_count,
        statistics_dislike_count as video_statistics_dislike_count,
        statistics_favorite_count as video_statistics_favorite_count,
        statistics_comment_count as video_statistics_comment_count,
        id as video_id,
        id,
        'youtube_video_data' as source_relation
    from raw.youtube_video_data
),
validated_rows as (
    select
        case when _fivetran_synced is null or _fivetran_synced <= current_timestamp then _fivetran_synced else null end as _fivetran_synced,
        case when snippet_published_at is null or snippet_published_at <= current_timestamp then snippet_published_at else null end as snippet_published_at,
        trim(channel_id) as channel_id,
        video_title,
        video_description,
        video_thumbnails,
        channel_title,
        video_tags,
        case when video_category_id between 1 and 44 then video_category_id else null end as video_category_id,
        video_live_broadcast_content,
        video_default_language,
        video_default_audio_language,
        video_duration,
        video_dimension,
        case when video_definition in ('sd', 'hd', 'uhd', '4k') then video_definition else null end as video_definition,
        video_caption,
        video_licensed_content,
        video_region_restriction_allowed,
        video_region_restriction_blocked,
        video_projection,
        video_has_custom_thumbnail,
        video_upload_status,
        video_failure_reason,
        video_rejection_reason,
        video_privacy_status,
        video_publish_at,
        video_license,
        video_embeddable,
        video_public_stats_viewable,
        case when video_statistics_view_count between 0 and 10000000000 then video_statistics_view_count else null end as video_statistics_view_count,
        case when video_statistics_like_count between 0 and 100000000 then video_statistics_like_count else null end as video_statistics_like_count,
        case when video_statistics_dislike_count between 0 and 10000000 then video_statistics_dislike_count else null end as video_statistics_dislike_count,
        case when video_statistics_favorite_count between 0 and 10000000 then video_statistics_favorite_count else null end as video_statistics_favorite_count,
        case when video_statistics_comment_count between 0 and 10000000 then video_statistics_comment_count else null end as video_statistics_comment_count,
        case when video_id is null or length(trim(video_id)) between 8 and 20 then trim(video_id) else null end as video_id,
        id,
        source_relation
    from source_rows
    where channel_id is not null
      and length(trim(channel_id)) between 12 and 40
      and id is not null
      and length(trim(id)) between 8 and 20
)
select *
from validated_rows
```

## gold SQL（仅供定位差异）

S5

```sql
-- Staging: YouTube video metadata
-- Source: raw.youtube_video_data (information_schema verified)
-- Purpose: Standardize column names, map to stable types, validate ranges, drop non-existent fields

with source_data as (
    select * from raw.video
),

renamed as (
    select
        _fivetran_synced,
        snippet_published_at,
        snippet_channel_id as channel_id,
        snippet_title as video_title,
        snippet_description as video_description,
        snippet_thumbnails as video_thumbnails,
        snippet_channel_title as channel_title,
        snippet_tags as video_tags,
        snippet_category_id as video_category_id,
        snippet_live_broadcast_content as video_live_broadcast_content,
        snippet_default_language as video_default_language,
        snippet_default_audio_language as video_default_audio_language,
        content_details_duration as video_duration,
        content_details_dimension as video_dimension,
        content_details_definition as video_definition,
        content_details_caption as video_caption,
        content_details_licensed_content as video_licensed_content,
        content_details_region_restriction_allowed as video_region_restriction_allowed,
        content_details_region_restriction_blocked as video_region_restriction_blocked,
        content_details_projection as video_projection,
        content_details_has_custom_thumbnail as video_has_custom_thumbnail,
        status_upload_status as video_upload_status,
        status_failure_reason as video_failure_reason,
        status_rejection_reason as video_rejection_reason,
        status_privacy_status as video_privacy_status,
        status_publish_at as video_publish_at,
        status_license as video_license,
        status_embeddable as video_embeddable,
        status_public_stats_viewable as video_public_stats_viewable,
        statistics_view_count as video_statistics_view_count,
        statistics_like_count as video_statistics_like_count,
        statistics_dislike_count as video_statistics_dislike_count,
        statistics_favorite_count as video_statistics_favorite_count,
        statistics_comment_count as video_statistics_comment_count,
        id,
        'youtube_source' as source_relation
    from source_data
),

validated as (
    select
        case when _fivetran_synced <= current_timestamp then _fivetran_synced else NULL end as _fivetran_synced,
        case when snippet_published_at <= current_timestamp then snippet_published_at else NULL end as snippet_published_at,
        case when length(trim(channel_id)) between 12 and 40 then trim(channel_id) else NULL end as channel_id,
        video_title,
        video_description,
        video_thumbnails,
        channel_title,
        video_tags,
        case when try_cast(video_category_id as integer) between 1 and 44 then try_cast(video_category_id as integer) else NULL end as video_category_id,
        video_live_broadcast_content,
        video_default_language,
        video_default_audio_language,
        video_duration,
        video_dimension,
        case when video_definition in ('sd','hd','uhd','4k') then video_definition else NULL end as video_definition,
        video_caption,
        video_licensed_content,
        video_region_restriction_allowed,
        video_region_restriction_blocked,
        video_projection,
        video_has_custom_thumbnail,
        video_upload_status,
        video_failure_reason,
        video_rejection_reason,
        video_privacy_status,
        video_publish_at,
        video_license,
        video_embeddable,
        video_public_stats_viewable,
        case when try_cast(video_statistics_view_count as bigint) >= 0 and try_cast(video_statistics_view_count as bigint) <= 10000000000 then try_cast(video_statistics_view_count as bigint) else NULL end as video_statistics_view_count,
        case when try_cast(video_statistics_like_count as bigint) >= 0 and try_cast(video_statistics_like_count as bigint) <= 100000000 then try_cast(video_statistics_like_count as bigint) else NULL end as video_statistics_like_count,
        case when try_cast(video_statistics_dislike_count as bigint) >= 0 and try_cast(video_statistics_dislike_count as bigint) <= 10000000 then try_cast(video_statistics_dislike_count as bigint) else NULL end as video_statistics_dislike_count,
        case when try_cast(video_statistics_favorite_count as bigint) >= 0 and try_cast(video_statistics_favorite_count as bigint) <= 10000000 then try_cast(video_statistics_favorite_count as bigint) else NULL end as video_statistics_favorite_count,
        case when try_cast(video_statistics_comment_count as bigint) >= 0 and try_cast(video_statistics_comment_count as bigint) <= 10000000 then try_cast(video_statistics_comment_count as bigint) else NULL end as video_statistics_comment_count,
        case when length(trim(id)) between 8 and 20 then trim(id) else NULL end as video_id,
        id,
        source_relation
    from renamed
    where id is not null and length(trim(id)) between 8 and 20
      and channel_id is not null and length(trim(channel_id)) between 12 and 40
)

select * from validated
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2501 | 5 | 2501 | 5 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| channel_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| channel_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_category_id | 0 | 0 | 0 | INTEGER | INTEGER |
| video_definition | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_dimension | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_duration | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_license | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_live_broadcast_content | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_privacy_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_projection | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_statistics_comment_count | 0 | 0 | 0 | BIGINT | BIGINT |
| video_statistics_dislike_count | 0 | 0 | 0 | BIGINT | BIGINT |
| video_statistics_favorite_count | 0 | 0 | 0 | BIGINT | BIGINT |
| video_statistics_like_count | 0 | 0 | 0 | BIGINT | BIGINT |
| video_statistics_view_count | 0 | 0 | 0 | BIGINT | BIGINT |
| video_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_upload_status | 0 | 0 | 0 | VARCHAR | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"video_id":"--dhjPQM9iB"},{"video_id":"-1-onSVHcsW"},{"video_id":"-4jouQo0FD6"},{"video_id":"-4L5ZqXfT_9"},{"video_id":"-4SznW7WPuo"}]</code> | <code>[{"video_id":"video_001"},{"video_id":"video_002"},{"video_id":"video_003"},{"video_id":"video_004"},{"video_id":"video_005"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>9列；[{"column":"video_thumbnails","table_rows":2501},{"column":"video_tags","table_rows":2501},{"column":"video_default_language","table_rows":2501}]</code> |
| A3_constant_nonnull_column | <code>9列；[{"column":"channel_id","value":"UC2vW_-qeIhF1ESszzuH2pyw"},{"column":"channel_title","value":"Fivetran"},{"column":"video_live_broadcast_content","value":"none"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["video_embeddable","video_public_stats_viewable"],"nonnull_equal_rows":2501,"meaning_status":"契约未描述含义差别"},{"columns":["video_id","id"],"nonnull_equal_rows":2501,"meaning_status":"契约未描述含义差别"}]</code> |
| B5_null_literal_output | <code>4输出列；[{"column":"video_region_restriction_allowed","expression":["CAST(NULL AS TEXT)"]},{"column":"video_region_restriction_blocked","expression":["CAST(NULL AS TEXT)"]},{"column":"video_failure_reason","expression":["CAST(NULL AS TEXT)"]}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"source_relation","expression":["'youtube_video_data'"]}]</code> |
| B7_specified_not_read | <code>["raw.video"]</code> |
| B7_read_not_specified | <code>["raw.youtube_video_data"]</code> |
| C9_agent_runtime_text | <code>S4:44 current_timestamp；命中数=2</code> |
| C9_gold_runtime_text | <code>S5:52 current_timestamp；命中数=2</code> |
| C9_contract_runtime_text | <code>S3:213 CURRENT_TIMESTAMP；命中数=2</code> |
| D10_keyword_in_any_result_field | <code>命中数=3；assistant_trajectory  'video IDs non-null': "select count(*) filter (where video_id is null)=0 from staging.stg_youtube__video",</code> |

## 轨迹索引（不放输出原文）

本题事件总数：59；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find . -maxdepth 3 -type f &#124; sort &#124; head -250</code> | 1225 | false | false |
| 9 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,260p' run.py</code> | 10808 | true | false |
| 11 | run | <code>wc -l docs/data_contract.yaml &amp;&amp; sed -n '1,250p' docs/data_contract.yaml</code> | 10324 | true | false |
| 15 | run | <code>cat youtube_analytics_start.yaml &amp;&amp; sed -n '250,520p' docs/data_contract.yaml</code> | 17810 | false | false |
| 17 | run | <code>sed -n '520,800p' docs/data_contract.yaml</code> | 16271 | true | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics_start.duckdb',read_only=True)<br>print(c.execute('select * from information_schema.tables').fetchall())<br>print(c.execute('select * from du</code> | 1478 | false | false |
| 23 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics_start.duckdb',read_only=True)<br>for t, in c.execute("select table_name from information_schema.tables where table_schema='raw'").fetchal</code> | 6157 | false | false |
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

event 25 / message

```text
cat > sql/staging/stg_youtube__video.sql <<'SQL'
```
event 29 / message

```text
    from staging.stg_youtube__video
```
event 37 / message

```text
for table in ['staging.stg_youtube__channel_basic','staging.stg_youtube__channel_demographics','staging.stg_youtube__video','intermediate.int_youtube__channel_basic','intermediate.int_youtube__channel_demographics','intermediate.int_youtube__age_pivot','intermediate.int_youtube__gender_pivot','intermediate.int_youtube__video','marts.youtube__video_metadata','marts.youtube__video_report','marts.youtube__demographics_report','marts.youtube__age_demographics_pivot','marts.youtube__gender_demographics_pivot']:
```
event 39 / message

```text
 'video IDs non-null': "select count(*) filter (where video_id is null)=0 from staging.stg_youtube__video",
```
event 41 / message

```text
print(c.execute('select count(*) from staging.stg_youtube__video where video_thumbnails is not null').fetchone())
```
event 45 / message

```text
'raw/staging counts':"select (select count(*) from raw.youtube_channel_basic_data),(select count(*) from staging.stg_youtube__channel_basic),(select count(*) from raw.youtube_channel_demographics_data),(select count(*) from staging.stg_youtube__channel_demographics),(select count(*) from raw.youtube_video_data),(select count(*) from staging.stg_youtube__video)",
```
event 47 / message

```text
- **Staging:** `stg_youtube__channel_basic.sql`、`stg_youtube__channel_demographics.sql`、`stg_youtube__video.sql`
```
event 51 / message

```text
- **Staging:** `stg_youtube__channel_basic.sql`、`stg_youtube__channel_demographics.sql`、`stg_youtube__video.sql`
```
event 55 / message

```text
- **Staging:** `stg_youtube__channel_basic.sql`、`stg_youtube__channel_demographics.sql`、`stg_youtube__video.sql`
```

## result.md 本表名原句

S9:7

```text
- **Staging:** `stg_youtube__channel_basic.sql`、`stg_youtube__channel_demographics.sql`、`stg_youtube__video.sql`
```

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-028.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/sql/staging/stg_youtube__video.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/sql/staging/stg_youtube__video.sql`
- S6: `records/006_contract_impl-028.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/result.md`
- S10: `data/024_packages_work/024_impl-028_stg_youtube__video/024_impl-028_stg_youtube__video.json`
- S11: `data/011_agent_alignment/impl-028/stg_youtube__video_2024-01-30.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/youtube_analytics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions`
