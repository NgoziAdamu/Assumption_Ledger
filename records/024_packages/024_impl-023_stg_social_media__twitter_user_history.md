# impl-023 | staging | stg_social_media__twitter_user_history | 差异：S1；日期 原记录

## 契约完整原文

S3:58–114

```yaml
    - name: stg_social_media__twitter_user_history
      description: "Cleaned and standardized Twitter user profile attributes for safe downstream joins and reporting."
      source_table: raw.twitter_user_history
      columns:
        - name: id
          data_type: BIGINT
          constraints: [not_null]
        - name: _fivetran_synced
          data_type: TIMESTAMP
        - name: screen_name
          data_type: VARCHAR
          constraints: [not_null]
          description: >
            Best-effort cleaning to keep only [A-Za-z0-9_]; rows with NULL/blank or harmful characters are removed.
          validation_rules:
            - rule: "screen_name = CASE WHEN screen_name IS NULL OR TRIM(screen_name) = '' THEN NULL ELSE REGEXP_REPLACE(screen_name, '[^A-Za-z0-9_]', '') END"
              on_failure: correct
            - rule: "screen_name IS NOT NULL AND NOT (screen_name RLIKE '[!@#$%^&*()+=<>?}{|,]')"
              on_failure: delete_row
        - name: url
          data_type: VARCHAR
          validation_rules:
            - rule: "url IS NULL OR url RLIKE '^https?://[A-Za-z0-9.-]+\\.[A-Za-z]{2,}(/.*)?'"
              on_failure: nullify_field
            - rule: "url IS NULL OR (url RLIKE '^(https?://)?[A-Za-z0-9.-]+\\.[A-Za-z]{2,}(/.*)?' AND url RLIKE '^https?://')"
              on_failure: correct
        - name: created_at
          data_type: TIMESTAMP
        - name: followers_count
          data_type: BIGINT
        - name: following_count
          data_type: BIGINT
          description: "Renamed from friends_count."
        - name: listed_count
          data_type: BIGINT
        - name: favourites_count
          data_type: BIGINT
        - name: statuses_count
          data_type: BIGINT
        - name: verified
          data_type: BOOLEAN
        - name: protected
          data_type: BOOLEAN
          description: "Derived from protected_user: TRUE if protected_user=TRUE else FALSE."
        - name: default_profile
          data_type: BOOLEAN
        - name: default_profile_image
          data_type: BOOLEAN
        - name: location
          data_type: VARCHAR
        - name: description
          data_type: VARCHAR
        - name: time_zone
          data_type: VARCHAR
        - name: lang
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
with user_cleaned as (
    select
        try_cast(id as bigint) as id,
        _fivetran_synced::timestamp as _fivetran_synced,
        case when screen_name is null or trim(screen_name) = '' then null
             else regexp_replace(screen_name, '[^A-Za-z0-9_]', '', 'g') end as screen_name,
        case
            when url is null then null
            when regexp_matches(url, '^(https?://)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/.*)?')
                then case when regexp_matches(url, '^https?://') then url else 'https://' || url end
            else null
        end as url,
        created_at::timestamp as created_at,
        try_cast(followers_count as bigint) as followers_count,
        try_cast(friends_count as bigint) as following_count,
        try_cast(listed_count as bigint) as listed_count,
        try_cast(favourites_count as bigint) as favourites_count,
        try_cast(statuses_count as bigint) as statuses_count,
        verified::boolean as verified,
        coalesce(protected_user, false)::boolean as protected,
        default_profile::boolean as default_profile,
        default_profile_image::boolean as default_profile_image,
        location::varchar as location,
        description::varchar as description,
        time_zone::varchar as time_zone,
        lang::varchar as lang
    from raw.twitter_user_history
)
select *
from user_cleaned
where id is not null
  and screen_name is not null
  and screen_name <> '' 
```

## gold SQL（仅供定位差异）

S5

```sql
-- Twitter user history staging table
-- Applies data validation and cleaning rules

WITH source_data AS (
    SELECT
        id,
        _fivetran_synced,
        screen_name,
        url,
        created_at,
        followers_count,
        friends_count,
        listed_count,
        favourites_count,
        statuses_count,
        verified,
        CASE WHEN protected_user = TRUE THEN TRUE ELSE FALSE END AS protected,
        default_profile,
        default_profile_image,
        location,
        description,
        time_zone,
        lang
    FROM raw.twitter_user_history
),

cleaned_data AS (
    SELECT
        id,
        _fivetran_synced,
        -- Apply screen_name validation and cleaning
        CASE
            WHEN screen_name IS NULL OR TRIM(screen_name) = '' THEN NULL
            WHEN REGEXP_MATCHES(screen_name, '^[A-Za-z0-9_]{3,15}$') THEN screen_name
            ELSE REGEXP_REPLACE(screen_name, '[^A-Za-z0-9_]', '')
        END AS screen_name,
        -- Apply URL validation and cleaning
        CASE
            WHEN url IS NULL THEN NULL
            WHEN REGEXP_MATCHES(url, '^https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/.*)?') THEN url
            WHEN REGEXP_MATCHES(url, '^(https?://)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/.*)?') THEN 'https://' || REGEXP_REPLACE(url, '^https?://', '')
            ELSE NULL
        END AS url,
        created_at,
        followers_count,
        friends_count AS following_count,
        listed_count,
        favourites_count,
        statuses_count,
        verified,
        protected,
        default_profile,
        default_profile_image,
        location,
        description,
        time_zone,
        lang
    FROM source_data
    WHERE screen_name IS NOT NULL -- Remove invalid entries
    AND NOT REGEXP_MATCHES(screen_name, '[!@#$%^&*()+=<>?}{|,]') -- Remove rows with harmful characters
)

SELECT *
FROM cleaned_data
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1 | 12 | 0 | 3 | 0 | 2 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"id":"100071333"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| screen_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| url | 0 | 0 | 0 | VARCHAR | VARCHAR |
| followers_count | 1 | 1 | 1 | BIGINT | DOUBLE |
| following_count | 1 | 1 | 1 | BIGINT | DOUBLE |
| listed_count | 0 | 0 | 0 | BIGINT | DOUBLE |
| favourites_count | 1 | 1 | 1 | BIGINT | DOUBLE |
| statuses_count | 1 | 1 | 1 | BIGINT | DOUBLE |
| verified | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| protected | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| default_profile | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| default_profile_image | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| location | 0 | 0 | 0 | VARCHAR | VARCHAR |
| description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| time_zone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| lang | 0 | 0 | 0 | VARCHAR | VARCHAR |

followers_count 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 43200 | 43200.0 |

following_count 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 11233 | 11233.0 |

favourites_count 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 312 | 312.0 |

statuses_count 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2108 | 2108.0 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"id":"False"},{"id":"false853637124"},{"id":"True"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>4列；[{"column":"url","table_rows":1},{"column":"listed_count","table_rows":1},{"column":"default_profile_image","table_rows":1}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["verified","protected"],"nonnull_equal_rows":1,"meaning_status":"契约未描述含义差别"}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 2094 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9937 | false | false |
| 13 | run | <code>wc -l docs/data_contract.yaml &amp;&amp; sed -n '1,240p' docs/data_contract.yaml</code> | 9685 | true | false |
| 23 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb',read_only=True)<br>for t, in c.execute("select table_name from information_schema.tables where table_schema='raw' orde</code> | 30939 | false | false |
| 29 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/write_sql.py &lt;&lt;'PY'<br>from pathlib import Path<br>files={}<br>files['staging/stg_social_media__account_history.sql'] = '''select<br>    try_cast(id a</code> | 0 | false | false |
| 33 | run | <code>cat &gt;&gt; /tmp/write_sql.py &lt;&lt;'PY'<br>files['marts/social_media_reporting__rollup_report.sql'] = '''with all_posts as (<br>    select page_id, page_name, post_id, post_message, created_timestamp, platform,<br>   </code> | 917 | true | false |
| 37 | run | <code>grep 'staging\.&#124;intermediate\.&#124;marts\.' /tmp/pipeline.log &#124; tail -35; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting.duckdb',read_only=True)<br>for schema in ['staging','intermedi</code> | 1464 | true | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb')<br>print('ids linkedin match',c.execute("select count(*) from raw.linkedin_pages_organization_ugc_post o join raw.lin</code> | 639 | false | false |
| 49 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql').rglob('*.sql'):<br> s=p.read_text()<br> assert not s.rstrip().endswith(';'), p<br> assert 'ref(' not in s.lower(), p<br> print(f'{p}: {len(s.splitline</code> | 1600 | true | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
files['staging/stg_social_media__twitter_user_history.sql'] = '''with user_cleaned as (
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-023.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__twitter_user_history.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__twitter_user_history.sql`
- S6: `records/006_contract_impl-023.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/result.md`
- S10: `data/024_packages_work/024_impl-023_stg_social_media__twitter_user_history/024_impl-023_stg_social_media__twitter_user_history.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions`
