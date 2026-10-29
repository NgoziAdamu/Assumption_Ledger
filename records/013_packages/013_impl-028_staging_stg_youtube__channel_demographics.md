# impl-028 | staging | stg_youtube__channel_demographics | 差异：S1；日期 2024-01-30

## 契约完整原文

S3:155–205

```yaml
    - name: stg_youtube__channel_demographics
      description: "Cleaned per-video demographics (age, gender, geography). Percentages normalized to [0,1]; identifiers validated; categories enforced."
      source_table: raw.channel_demographics_a_1
      columns:
        - name: date_day
          data_type: DATE
          validation_rules:
            - rule: "date_day IS NOT NULL"
              on_failure: delete_row
        - name: channel_id
          data_type: VARCHAR
          validation_rules:
            - rule: "channel_id IS NULL OR (LENGTH(TRIM(channel_id)) BETWEEN 12 AND 40)"
              on_failure: nullify_field
            - rule: "channel_id = TRIM(channel_id)"
              on_failure: correct
        - name: video_id
          data_type: VARCHAR
          validation_rules:
            - rule: "video_id IS NULL OR (LENGTH(TRIM(video_id)) BETWEEN 8 AND 20)"
              on_failure: nullify_field
            - rule: "video_id = TRIM(video_id)"
              on_failure: correct
        - name: country_code
          data_type: VARCHAR
          validation_rules:
            - rule: "country_code IS NULL OR country_code = UPPER(TRIM(country_code))"
              on_failure: correct
        - name: age_group
          data_type: VARCHAR
          validation_rules:
            - rule: "age_group IN ('13-17','18-24','25-34','35-44','45-54','55-64','65-')"
              on_failure: nullify_field
        - name: gender
          data_type: VARCHAR
          validation_rules:
            - rule: "gender IN ('female','male','user_specified')"
              on_failure: nullify_field
        - name: views_percentage
          data_type: DECIMAL(5,4)
          validation_rules:
            - rule: "views_percentage BETWEEN 0 AND 1"
              on_failure: nullify_field
        - name: _fivetran_synced
          data_type: TIMESTAMP
          validation_rules:
            - rule: "_fivetran_synced IS NULL OR _fivetran_synced <= CURRENT_TIMESTAMP"
              on_failure: nullify_field
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
        country_code,
        case
            when age_group = 'AGE_13_17' then '13-17'
            when age_group = 'AGE_18_24' then '18-24'
            when age_group = 'AGE_25_34' then '25-34'
            when age_group = 'AGE_35_44' then '35-44'
            when age_group = 'AGE_45_54' then '45-54'
            when age_group = 'AGE_55_64' then '55-64'
            when age_group = 'AGE_65_' then '65-'
            else age_group
        end as age_group,
        lower(gender) as gender,
        try_cast(views_percentage as decimal(5, 4)) as views_percentage,
        try_cast(replace("_fivetran_synced", ' UTC', '') as timestamp) as _fivetran_synced,
        'youtube_channel_demographics_data' as source_relation
    from raw.youtube_channel_demographics_data
),
validated_rows as (
    select
        date_day,
        case when channel_id is null or length(trim(channel_id)) between 12 and 40 then trim(channel_id) else null end as channel_id,
        case when video_id is null or length(trim(video_id)) between 8 and 20 then trim(video_id) else null end as video_id,
        case when country_code is null then null else upper(trim(country_code)) end as country_code,
        case when age_group in ('13-17', '18-24', '25-34', '35-44', '45-54', '55-64', '65-') then age_group else null end as age_group,
        case when gender in ('female', 'male', 'user_specified') then gender else null end as gender,
        case when views_percentage between 0 and 1 then views_percentage else null end as views_percentage,
        case when _fivetran_synced is null or _fivetran_synced <= current_timestamp then _fivetran_synced else null end as _fivetran_synced,
        source_relation
    from source_rows
    where date_day is not null
)
select *
from validated_rows
```

## gold SQL（仅供定位差异）

S5

```sql
-- Staging: YouTube channel demographics metrics
-- Source: raw.youtube_channel_demographics_data (information_schema verified)
-- Purpose: Normalize percentages, validate categories and identifiers

with source_data as (
    select * from raw.channel_demographics_a_1
),

renamed as (
    select
        date as date_day,
        channel_id,
        video_id,
        upper(trim(country_code)) as country_code,
        age_group,
        gender,
        views_percentage / 100.0 as views_percentage,
        _fivetran_synced,
        'youtube_source' as source_relation
    from source_data
),

validated as (
    select
        date_day,
        case when channel_id IS NOT NULL AND length(trim(channel_id)) between 12 and 40 then trim(channel_id) else NULL end as channel_id,
        case when video_id IS NULL OR length(trim(video_id)) between 8 and 20 then trim(video_id) else NULL end as video_id,
        country_code,
        case when age_group in ('13-17','18-24','25-34','35-44','45-54','55-64','65-') then age_group else NULL end as age_group,
        case when gender in ('female','male','user_specified') then gender else NULL end as gender,
        case when views_percentage >= 0 and views_percentage <= 1 then views_percentage else NULL end as views_percentage,
        case when _fivetran_synced <= current_timestamp then _fivetran_synced else NULL end as _fivetran_synced,
        source_relation
    from renamed
    where date_day is not null
)

select * from validated
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2509 | 9450 | 2504 | 450 | 3 | 450 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| channel_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| video_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| age_group | 0 | 0 | 0 | VARCHAR | VARCHAR |
| gender | 0 | 0 | 0 | VARCHAR | VARCHAR |
| views_percentage | 0 | 0 | 0 | DECIMAL(5,4) | DOUBLE |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"date_day":"2021-08-13","channel_id":null,"video_id":"THK0DyoSVTs","country_code":"FI"},{"date_day":"2021-08-13","channel_id":null,"video_id":"THK0DyoSVTs","country_code":"GB"},{"date_day":"2021-08-13","channel_id":null,"video_id":"THK0DyoSVTs","country_code":"IL"},{"date_day":"2021-08-13","channel_id":null,"video_id":"THK0DyoSVTs","country_code":"NG"},{"date_day":"2021-08-13","channel_id":null,"video_id":"THK0DyoSVTs","country_code":"NO"}]</code> | <code>[{"date_day":"2024-01-01","channel_id":"UC_example_channel","video_id":"video_001","country_code":"CA"},{"date_day":"2024-01-01","channel_id":"UC_example_channel","video_id":"video_001","country_code":"GB"},{"date_day":"2024-01-01","channel_id":"UC_example_channel","video_id":"video_001","country_code":"US"},{"date_day":"2024-01-01","channel_id":"UC_example_channel","video_id":"video_002","country_code":"CA"},{"date_day":"2024-01-01","channel_id":"UC_example_channel","video_id":"video_002","country_code":"GB"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"source_relation","value":"youtube_channel_demographics_data"}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"source_relation","expression":["'youtube_channel_demographics_data'"]}]</code> |
| B7_specified_not_read | <code>["raw.channel_demographics_a_1"]</code> |
| B7_read_not_specified | <code>["raw.youtube_channel_demographics_data"]</code> |
| C9_agent_runtime_text | <code>S4:32 current_timestamp；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:32 current_timestamp；命中数=1</code> |
| C9_contract_runtime_text | <code>S3:201 CURRENT_TIMESTAMP；命中数=1</code> |

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
| 17 | run | <code>sed -n '520,800p' docs/data_contract.yaml</code> | 16271 | true | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics_start.duckdb',read_only=True)<br>print(c.execute('select * from information_schema.tables').fetchall())<br>print(c.execute('select * from du</code> | 1478 | false | false |
| 23 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics_start.duckdb',read_only=True)<br>for t, in c.execute("select table_name from information_schema.tables where table_schema='raw'").fetchal</code> | 6157 | false | false |
| 25 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; sql/staging/stg_youtube__channel_basic.sql &lt;&lt;'SQL'<br>with source_rows as (<br>    select<br>        try_cast("date" as date) as date_day,<br>        chann</code> | 0 | false | false |
| 27 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_youtube__channel_basic.sql'<br>s=open(p).read().replace('        card_clickable_impressions,\n','        cast(null as bigint) as card_clickable_impressions,\n')<br>open(p,</code> | 0 | false | false |
| 31 | run | <code>cat &gt; sql/marts/youtube__age_demographics_pivot.sql &lt;&lt;'SQL'<br>select<br>    age_pivot.date_day,<br>    age_pivot.video_id,<br>    age_pivot.country_code,<br>    age_pivot."13-17" as "13-17_view_percentage",<br>    age</code> | 7266 | true | false |
| 33 | run | <code>python - &lt;&lt;'PY'<br>p='run.py'; s=open(p).read(); s=s.replace('tables_result = source_conn.execute("SHOW TABLES").fetchall()\n            source_tables = [table[0] for table in tables_result]', 'tables_re</code> | 7173 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics.duckdb',read_only=True)<br>for table in ['staging.stg_youtube__channel_basic','staging.stg_youtube__channel_demographics','staging.stg_yo</code> | 13338 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>p='sql/marts/youtube__video_report.sql'<br>s=open(p).read().replace("""            else sum(average_view_duration_seconds * views) filter (where average_view_duration_seconds is not null)</code> | 1874 | true | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('youtube_analytics.duckdb',read_only=True)<br>qs={<br>'raw/staging counts':"select (select count(*) from raw.youtube_channel_basic_data),(select count(*) from </code> | 712 | true | false |
| 47 | run | <code>cat &gt; /workspace/result.md &lt;&lt;'MD'<br>【回复用户】<br><br>已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB SQL、显式 `schema.table` 上</code> | 149 | false | false |
| 51 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'MD'<br>【回复用户】<br><br>已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB </code> | 82 | false | false |
| 55 | run | <code>cat &gt; result.md &lt;&lt;'MD'<br>【回复用户】<br><br>已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 YouTube Analytics 的 staging、intermediate 与 marts SQL。全部模型采用 DuckDB SQL、显式 `schema.table` 上游引用，没有 dbt </code> | 1993 | true | false |

### agent action 的 thought/message 命中原句

event 25 / message

```text
cat > sql/staging/stg_youtube__channel_demographics.sql <<'SQL'
```
event 27 / message

```text
from staging.stg_youtube__channel_demographics
```
event 27 / message

```text
    from staging.stg_youtube__channel_demographics
```
event 27 / message

```text
    from staging.stg_youtube__channel_demographics
```
event 37 / message

```text
for table in ['staging.stg_youtube__channel_basic','staging.stg_youtube__channel_demographics','staging.stg_youtube__video','intermediate.int_youtube__channel_basic','intermediate.int_youtube__channel_demographics','intermediate.int_youtube__age_pivot','intermediate.int_youtube__gender_pivot','intermediate.int_youtube__video','marts.youtube__video_metadata','marts.youtube__video_report','marts.youtube__demographics_report','marts.youtube__age_demographics_pivot','marts.youtube__gender_demographics_pivot']:
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/sql/staging/stg_youtube__channel_demographics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/sql/staging/stg_youtube__channel_demographics.sql`
- S6: `records/006_contract_impl-028.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/result.md`
- S10: `records/012_packages/012_impl-028_staging_stg_youtube__channel_demographics.json`
- S11: `data/011_agent_alignment/impl-028/stg_youtube__channel_demographics_2024-01-30.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-028/youtube_analytics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-028/agent/.events/sessions`
