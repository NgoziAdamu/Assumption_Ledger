# impl-028 | staging | stg_youtube__channel_basic | 差异：S1；日期 2024-01-30

## 契约完整原文

S3:34–154

```yaml
    - name: stg_youtube__channel_basic
      description: "Cleaned daily per-video channel performance metrics (views, engagement, subscribers, annotations). Percentages are normalized to [0,1]."
      source_table: raw.channel_basic_a_2
      columns:
        - name: date_day
          data_type: DATE
          validation_rules:
            - rule: "date_day IS NOT NULL AND date_day <= CURRENT_DATE AND date_day >= '2020-01-01'"
              on_failure: delete_row
        - name: channel_id
          data_type: VARCHAR
          validation_rules:
            - rule: "channel_id IS NULL OR LENGTH(TRIM(channel_id)) = 24"
              on_failure: nullify_field
            - rule: "channel_id = TRIM(channel_id)"
              on_failure: correct
        - name: video_id
          data_type: VARCHAR
          validation_rules:
            - rule: "video_id IS NULL OR LENGTH(TRIM(video_id)) = 11"
              on_failure: nullify_field
            - rule: "video_id = TRIM(video_id)"
              on_failure: correct
        - name: channel_title
          data_type: VARCHAR
        - name: video_title
          data_type: VARCHAR
        - name: deleted
          data_type: BOOLEAN
        - name: _fivetran_synced
          data_type: TIMESTAMP
          validation_rules:
            - rule: "_fivetran_synced IS NULL OR _fivetran_synced <= CURRENT_TIMESTAMP"
              on_failure: nullify_field
        - name: average_view_duration_seconds
          data_type: BIGINT
        - name: average_view_duration_percentage
          data_type: DECIMAL(5,4)
          validation_rules:
            - rule: "average_view_duration_percentage BETWEEN 0 AND 1"
              on_failure: nullify_field
        - name: views
          data_type: BIGINT
          validation_rules:
            - rule: "views BETWEEN 0 AND 1000000000"
              on_failure: nullify_field
        - name: likes
          data_type: BIGINT
          validation_rules:
            - rule: "likes BETWEEN 0 AND 10000000"
              on_failure: nullify_field
        - name: dislikes
          data_type: BIGINT
          validation_rules:
            - rule: "dislikes BETWEEN 0 AND 1000000"
              on_failure: nullify_field
        - name: shares
          data_type: BIGINT
          validation_rules:
            - rule: "shares >= 0"
              on_failure: nullify_field
        - name: subscribers_gained
          data_type: BIGINT
          validation_rules:
            - rule: "subscribers_gained BETWEEN -50000 AND 50000"
              on_failure: nullify_field
        - name: subscribers_lost
          data_type: BIGINT
          validation_rules:
            - rule: "subscribers_lost BETWEEN 0 AND 10000"
              on_failure: nullify_field
        - name: estimated_minutes_watched
          data_type: DECIMAL(18,4)
          validation_rules:
            - rule: "estimated_minutes_watched >= 0"
              on_failure: nullify_field
        - name: estimated_red_minutes_watched
          data_type: DECIMAL(18,4)
          validation_rules:
            - rule: "estimated_red_minutes_watched >= 0"
              on_failure: nullify_field
        - name: annotation_click_through_rate
          data_type: DECIMAL(18,4)
        - name: annotation_close_rate
          data_type: DECIMAL(18,4)
        - name: annotation_impressions
          data_type: BIGINT
        - name: annotation_clickable_impressions
          data_type: BIGINT
        - name: annotation_closable_impressions
          data_type: BIGINT
        - name: annotation_clicks
          data_type: BIGINT
        - name: annotation_closes
          data_type: BIGINT
        - name: viewers
          data_type: BIGINT
        - name: views_percentage
          data_type: DECIMAL(5,4)
          validation_rules:
            - rule: "views_percentage BETWEEN 0 AND 1"
              on_failure: nullify_field
        - name: average_time_in_video
          data_type: DECIMAL(18,4)
        - name: card_click_rate
          data_type: DECIMAL(18,4)
        - name: card_impressions
          data_type: BIGINT
        - name: card_clickable_impressions
          data_type: BIGINT
        - name: card_clicks
          data_type: BIGINT
        - name: playlist_starts
          data_type: BIGINT
        - name: estimated_minutes_watched_from_playlists
          data_type: DECIMAL(18,4)
        - name: average_time_in_playlist
          data_type: DECIMAL(18,4)
        - name: source_relation
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
with source_rows as (
    select
        try_cast("date" as date) as date_day,
        channel_id,
        video_id,
        cast(null as varchar) as channel_title,
        cast(null as varchar) as video_title,
        cast(null as boolean) as deleted,
        try_cast(replace("_fivetran_synced", ' UTC', '') as timestamp) as _fivetran_synced,
        try_cast(average_view_duration_seconds as bigint) as average_view_duration_seconds,
        try_cast(average_view_duration_percentage as decimal(5, 4)) as average_view_duration_percentage,
        views,
        likes,
        dislikes,
        shares,
        subscribers_gained,
        subscribers_lost,
        try_cast(watch_time_minutes as decimal(18, 4)) as estimated_minutes_watched,
        try_cast(red_watch_time_minutes as decimal(18, 4)) as estimated_red_minutes_watched,
        try_cast(annotation_click_through_rate as decimal(18, 4)) as annotation_click_through_rate,
        try_cast(annotation_close_rate as decimal(18, 4)) as annotation_close_rate,
        annotation_impressions,
        annotation_clickable_impressions,
        annotation_closable_impressions,
        annotation_clicks,
        annotation_closes,
        cast(null as bigint) as viewers,
        cast(null as decimal(5, 4)) as views_percentage,
        cast(null as decimal(18, 4)) as average_time_in_video,
        try_cast(card_click_rate as decimal(18, 4)) as card_click_rate,
        card_impressions,
        cast(null as bigint) as card_clickable_impressions,
        card_clicks,
        cast(null as bigint) as playlist_starts,
        cast(null as decimal(18, 4)) as estimated_minutes_watched_from_playlists,
        cast(null as decimal(18, 4)) as average_time_in_playlist,
        'youtube_channel_basic_data' as source_relation
    from raw.youtube_channel_basic_data
),
validated_rows as (
    select
        date_day,
        case when channel_id is null or length(trim(channel_id)) = 24 then trim(channel_id) else null end as channel_id,
        case when video_id is null or length(trim(video_id)) = 11 then trim(video_id) else null end as video_id,
        channel_title,
        video_title,
        deleted,
        case when _fivetran_synced is null or _fivetran_synced <= current_timestamp then _fivetran_synced else null end as _fivetran_synced,
        average_view_duration_seconds,
        case when average_view_duration_percentage between 0 and 1 then average_view_duration_percentage else null end as average_view_duration_percentage,
        case when views between 0 and 1000000000 then views else null end as views,
        case when likes between 0 and 10000000 then likes else null end as likes,
        case when dislikes between 0 and 1000000 then dislikes else null end as dislikes,
        case when shares >= 0 then shares else null end as shares,
        case when subscribers_gained between -50000 and 50000 then subscribers_gained else null end as subscribers_gained,
        case when subscribers_lost between 0 and 10000 then subscribers_lost else null end as subscribers_lost,
        case when estimated_minutes_watched >= 0 then estimated_minutes_watched else null end as estimated_minutes_watched,
        case when estimated_red_minutes_watched >= 0 then estimated_red_minutes_watched else null end as estimated_red_minutes_watched,
        annotation_click_through_rate,
        annotation_close_rate,
        annotation_impressions,
        annotation_clickable_impressions,
        annotation_closable_impressions,
        annotation_clicks,
        annotation_closes,
        viewers,
        case when views_percentage between 0 and 1 then views_percentage else null end as views_percentage,
        average_time_in_video,
        card_click_rate,
        card_impressions,
        cast(null as bigint) as card_clickable_impressions,
        card_clicks,
        playlist_starts,
        estimated_minutes_watched_from_playlists,
        average_time_in_playlist,
        source_relation
    from source_rows
    where date_day is not null
      and date_day <= current_date
      and date_day >= date '2020-01-01'
)
select *
from validated_rows
```

## gold SQL（仅供定位差异）

S5

```sql
with source_data as (
    select * from raw.channel_basic_a_2
),

renamed as (
    select
        date as date_day,
        channel_id,
        video_id,
        channel_title,
        video_title,
        deleted,
        _fivetran_synced,
        average_view_duration_seconds,
        average_view_duration_percentage / 100.0 as average_view_duration_percentage,
        views,
        likes,
        dislikes,
        shares,
        subscribers_gained,
        subscribers_lost,
        estimated_minutes_watched,
        estimated_red_minutes_watched,
        annotation_click_through_rate,
        annotation_close_rate,
        annotation_impressions,
        annotation_clickable_impressions,
        annotation_closable_impressions,
        annotation_clicks,
        annotation_closes,
        viewers,
        views_percentage / 100.0 as views_percentage,
        average_time_in_video,
        card_click_rate,
        card_impressions,
        card_clickable_impressions,
        card_clicks,
        playlist_starts,
        estimated_minutes_watched_from_playlists,
        average_time_in_playlist,
        'youtube_source' as source_relation
    from source_data
),

validated as (
    select
        -- enforce temporal validity of dates
        date_day,
        -- identifiers cleaning/validation
        case when channel_id IS NOT NULL AND length(trim(channel_id)) = 24 then trim(channel_id) else NULL end as channel_id,
        case when video_id IS NULL OR length(trim(video_id)) = 11 then trim(video_id) else NULL end as video_id,
        channel_title,
        video_title,
        deleted,
        case when _fivetran_synced <= current_timestamp then _fivetran_synced else NULL end as _fivetran_synced,
        -- percentage already normalized to [0,1]; enforce bounds
        average_view_duration_seconds,
        case when average_view_duration_percentage >= 0 and average_view_duration_percentage <= 1 then average_view_duration_percentage else NULL end as average_view_duration_percentage,
        -- non-negative metrics and sensible ranges
        case when views >= 0 and views <= 1000000000 then views else NULL end as views,
        case when likes >= 0 and likes <= 10000000 then likes else NULL end as likes,
        case when dislikes >= 0 and dislikes <= 1000000 then dislikes else NULL end as dislikes,
        case when shares >= 0 then shares else NULL end as shares,
        case when subscribers_gained >= -50000 and subscribers_gained <= 50000 then subscribers_gained else NULL end as subscribers_gained,
        case when subscribers_lost >= 0 and subscribers_lost <= 10000 then subscribers_lost else NULL end as subscribers_lost,
        case when estimated_minutes_watched >= 0 then estimated_minutes_watched else NULL end as estimated_minutes_watched,
        case when estimated_red_minutes_watched >= 0 then estimated_red_minutes_watched else NULL end as estimated_red_minutes_watched,
        annotation_click_through_rate,
        annotation_close_rate,
        annotation_impressions,
        annotation_clickable_impressions,
        annotation_closable_impressions,
        annotation_clicks,
        annotation_closes,
        viewers,
        case when views_percentage >= 0 and views_percentage <= 1 then views_percentage else NULL end as views_percentage,
        average_time_in_video,
        card_click_rate,
        card_impressions,
        card_clickable_impressions,
        card_clicks,
        playlist_starts,
        estimated_minutes_watched_from_playlists,
        average_time_in_playlist,
        source_relation
    from renamed
    where date_day is not null
      and date_day >= '2020-01-01' and date_day <= current_date
)

select * from validated
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1340 | 150 | 794 | 30 | 202 | 30 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| channel_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| annotation_click_through_rate | 0 | 0 | 0 | DECIMAL(18,4) | DOUBLE |
| annotation_clickable_impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| annotation_clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| annotation_closable_impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| annotation_close_rate | 0 | 0 | 0 | DECIMAL(18,4) | DOUBLE |
| annotation_closes | 0 | 0 | 0 | BIGINT | BIGINT |
| annotation_impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| average_view_duration_percentage | 0 | 0 | 0 | DECIMAL(5,4) | DOUBLE |
| average_view_duration_seconds | 0 | 0 | 0 | BIGINT | BIGINT |
| card_click_rate | 0 | 0 | 0 | DECIMAL(18,4) | DOUBLE |
| card_clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| card_impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| channel_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| deleted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| dislikes | 0 | 0 | 0 | BIGINT | BIGINT |
| estimated_minutes_watched | 0 | 0 | 0 | DECIMAL(18,4) | BIGINT |
| estimated_red_minutes_watched | 0 | 0 | 0 | DECIMAL(18,4) | BIGINT |
| likes | 0 | 0 | 0 | BIGINT | BIGINT |
| shares | 0 | 0 | 0 | BIGINT | BIGINT |
| subscribers_gained | 0 | 0 | 0 | BIGINT | BIGINT |
| subscribers_lost | 0 | 0 | 0 | BIGINT | BIGINT |
| video_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| views | 0 | 0 | 0 | BIGINT | BIGINT |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"date_day":"2021-07-16","channel_id":"UC2vW_-qeIhF1ESszzuH2pyw","video_id":"3NFy4gf22C4"},{"date_day":"2021-07-16","channel_id":"UC2vW_-qeIhF1ESszzuH2pyw","video_id":"3ZfKSnkCxd8"},{"date_day":"2021-07-16","channel_id":"UC2vW_-qeIhF1ESszzuH2pyw","video_id":"5-s8NfuPf9s"},{"date_day":"2021-07-16","channel_id":"UC2vW_-qeIhF1ESszzuH2pyw","video_id":"_MbXQQKmZRM"},{"date_day":"2021-07-16","channel_id":"UC2vW_-qeIhF1ESszzuH2pyw","video_id":"gJ6r-DocaJ4"}]</code> | <code>[{"date_day":"2024-01-01","channel_id":null,"video_id":null},{"date_day":"2024-01-02","channel_id":null,"video_id":null},{"date_day":"2024-01-03","channel_id":null,"video_id":null},{"date_day":"2024-01-04","channel_id":null,"video_id":null},{"date_day":"2024-01-05","channel_id":null,"video_id":null}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>10列；[{"column":"channel_title","table_rows":3500},{"column":"video_title","table_rows":3500},{"column":"deleted","table_rows":3500}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"channel_id","value":"UC2vW_-qeIhF1ESszzuH2pyw"},{"column":"source_relation","value":"youtube_channel_basic_data"}]</code> |
| B5_null_literal_output | <code>9输出列；[{"column":"channel_title","expression":["CAST(NULL AS TEXT)"]},{"column":"video_title","expression":["CAST(NULL AS TEXT)"]},{"column":"deleted","expression":["CAST(NULL AS BOOLEAN)"]}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"source_relation","expression":["'youtube_channel_basic_data'"]}]</code> |
| B7_specified_not_read | <code>["raw.channel_basic_a_2"]</code> |
| B7_read_not_specified | <code>["raw.youtube_channel_basic_data"]</code> |
| C9_agent_runtime_text | <code>S4:48 current_timestamp；命中数=2</code> |
| C9_gold_runtime_text | <code>S5:55 current_timestamp；命中数=2</code> |
| C9_contract_runtime_text | <code>S3:41 CURRENT_DATE；命中数=2</code> |
| D10_keyword_in_any_result_field | <code>命中数=5；assistant_trajectory select count(*) from staging.stg_youtube__channel_basic where video_id is null [(2,)]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：59；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions/d3a309f4-d4c1-4b-dacf3c82bc8a080/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find . -maxdepth 3 -type f &#124; sort &#124; head -250</code> | 1225 | false | false |
| 9 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,260p' run.py</code> | 10808 | true | false |
| 11 | run | <code>wc -l docs/data_contract.yaml &amp;&amp; sed -n '1,250p' docs/data_contract.yaml</code> | 10324 | true | false |
| 15 | run | <code>cat youtube_analytics_start.yaml &amp;&amp; sed -n '250,520p' docs/data_contract.yaml</code> | 17810 | true | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics_start.duckdb',read_only=True)<br>print(c.execute('select * from information_schema.tables').fetchall())<br>print(c.execute('select * from du</code> | 1478 | false | false |
| 23 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics_start.duckdb',read_only=True)<br>for t, in c.execute("select table_name from information_schema.tables where table_schema='raw'").fetchal</code> | 6157 | false | false |
| 25 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; sql/staging/stg_youtube__channel_basic.sql &lt;&lt;'SQL'<br>with source_rows as (<br>    select<br>        try_cast("date" as date) as date_day,<br>        chann</code> | 0 | false | false |
| 27 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_youtube__channel_basic.sql'<br>s=open(p).read().replace('        card_clickable_impressions,\n','        cast(null as bigint) as card_clickable_impressions,\n')<br>open(p,</code> | 0 | false | false |
| 31 | run | <code>cat &gt; sql/marts/youtube__age_demographics_pivot.sql &lt;&lt;'SQL'<br>select<br>    age_pivot.date_day,<br>    age_pivot.video_id,<br>    age_pivot.country_code,<br>    age_pivot."13-17" as "13-17_view_percentage",<br>    age</code> | 7266 | true | false |
| 33 | run | <code>python - &lt;&lt;'PY'<br>p='run.py'; s=open(p).read(); s=s.replace('tables_result = source_conn.execute("SHOW TABLES").fetchall()\n            source_tables = [table[0] for table in tables_result]', 'tables_re</code> | 7173 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics.duckdb',read_only=True)<br>for table in ['staging.stg_youtube__channel_basic','staging.stg_youtube__channel_demographics','staging.stg_yo</code> | 13338 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>p='sql/marts/youtube__video_report.sql'<br>s=open(p).read().replace("""            else sum(average_view_duration_seconds * views) filter (where average_view_duration_seconds is not null)</code> | 1874 | true | false |
| 43 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics.duckdb',read_only=True)<br>for q in ["select count(*) from marts.youtube__video_report where video_id is null", "select count(*) from sta</code> | 662 | true | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics.duckdb',read_only=True)<br>qs={<br>'raw/staging counts':"select (select count(*) from raw.youtube_channel_basic_data),(select count(*) from </code> | 712 | true | false |
| 47 | run | <code>cat &gt; /workspace/result.md &lt;&lt;'MD'<br>【回复用户】<br><br>已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB SQL、显式 `schema.table` 上</code> | 149 | false | false |
| 51 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'MD'<br>【回复用户】<br><br>已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB </code> | 82 | false | false |
| 55 | run | <code>cat &gt; result.md &lt;&lt;'MD'<br>【回复用户】<br><br>已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB SQL、显式 `schema.table` 上游引用，没有 dbt </code> | 1993 | true | false |

### agent action 的 thought/message 命中原句

event 25 / message

```text
Running command: mkdir -p sql/staging sql/intermediate sql/marts && cat > sql/staging/stg_youtube__channel_basic.sql <<'SQL'
```
event 27 / message

```text
p='sql/staging/stg_youtube__channel_basic.sql'
```
event 27 / message

```text
    from staging.stg_youtube__channel_basic
```
event 37 / message

```text
for table in ['staging.stg_youtube__channel_basic','staging.stg_youtube__channel_demographics','staging.stg_youtube__video','intermediate.int_youtube__channel_basic','intermediate.int_youtube__channel_demographics','intermediate.int_youtube__age_pivot','intermediate.int_youtube__gender_pivot','intermediate.int_youtube__video','marts.youtube__video_metadata','marts.youtube__video_report','marts.youtube__demographics_report','marts.youtube__age_demographics_pivot','marts.youtube__gender_demographics_pivot']:
```
event 39 / message

```text
 'channel_basic row count preserved': "select (select count(*) from raw.youtube_channel_basic_data) >= (select count(*) from staging.stg_youtube__channel_basic)",
```
event 43 / message

```text
for q in ["select count(*) from marts.youtube__video_report where video_id is null", "select count(*) from staging.stg_youtube__channel_basic where video_id is null", "select * from marts.youtube__video_report where video_id is null limit 3", "select count(*) from marts.youtube__video_report where video_report_id is null"]:
```
event 45 / message

```text
'raw/staging counts':"select (select count(*) from raw.youtube_channel_basic_data),(select count(*) from staging.stg_youtube__channel_basic),(select count(*) from raw.youtube_channel_demographics_data),(select count(*) from staging.stg_youtube__channel_demographics),(select count(*) from raw.youtube_video_data),(select count(*) from staging.stg_youtube__video)",
```
event 45 / message

```text
'bad staging dates':"select count(*) from staging.stg_youtube__channel_basic where date_day is null or date_day > current_date or date_day < date '2020-01-01'",
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/sql/staging/stg_youtube__channel_basic.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/sql/staging/stg_youtube__channel_basic.sql`
- S6: `records/006_contract_impl-028.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/result.md`
- S10: `data/024_packages_work/024_impl-028_stg_youtube__channel_basic/024_impl-028_stg_youtube__channel_basic.json`
- S11: `data/011_agent_alignment/impl-028/stg_youtube__channel_basic_2024-01-30.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/youtube_analytics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions`
