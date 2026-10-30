# impl-014 | staging | stg_qualtrics__user | 差异：S1；日期 原记录

## 契约完整原文

S3:31–90

```yaml
    - name: stg_qualtrics__user
      description: "Cleaned and standardized Qualtrics user account information including authentication details and organizational affiliations"
      source_table: "raw.user"
      primary_key: ["user_id"]
      columns:
        - name: user_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: email
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "email = LOWER(TRIM(email))"
              on_failure: correct
            - rule: "email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
              on_failure: delete_row
        - name: first_name
          data_type: VARCHAR
        - name: last_name
          data_type: VARCHAR
        - name: account_created_at
          data_type: TIMESTAMP
        - name: account_expires_at
          data_type: TIMESTAMP
          validation_rules:
            - rule: "account_expires_at IS NULL OR account_expires_at > account_created_at"
              on_failure: nullify_field
        - name: account_status
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "account_status IN ('active','inactive','suspended','deleted','pending')"
              on_failure: delete_row
        - name: division_id
          data_type: BIGINT
        - name: language
          data_type: VARCHAR
        - name: last_login_at
          data_type: TIMESTAMP
        - name: organization_id
          data_type: VARCHAR
        - name: password_expires_at
          data_type: TIMESTAMP
        - name: password_last_changed_at
          data_type: TIMESTAMP
        - name: response_count_auditable
          data_type: DOUBLE
        - name: response_count_deleted
          data_type: DOUBLE
        - name: response_count_generated
          data_type: DOUBLE
        - name: time_zone
          data_type: VARCHAR
        - name: is_unsubscribed
          data_type: BOOLEAN
        - name: user_type
          data_type: VARCHAR
        - name: username
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT
        try_cast(src."id" AS VARCHAR) AS user_id,
        lower(trim(try_cast(src."email" AS VARCHAR))) AS email,
        try_cast(src."first_name" AS VARCHAR) AS first_name,
        try_cast(src."last_name" AS VARCHAR) AS last_name,
        try_strptime(cast(src."account_creation_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS account_created_at,
        CASE WHEN try_strptime(cast(src."account_expiration_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP IS NULL OR try_strptime(cast(src."account_expiration_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP > try_strptime(cast(src."account_creation_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP THEN try_strptime(cast(src."account_expiration_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP ELSE NULL END AS account_expires_at,
        try_cast(src."account_status" AS VARCHAR) AS account_status,
        try_cast(src."division_id" AS BIGINT) AS division_id,
        try_cast(src."language" AS VARCHAR) AS language,
        try_strptime(cast(src."last_login_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_login_at,
        try_cast(src."organization_id" AS VARCHAR) AS organization_id,
        try_strptime(cast(src."password_expiration_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS password_expires_at,
        try_strptime(cast(src."password_last_changed_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS password_last_changed_at,
        try_cast(src."response_count_auditable" AS DOUBLE) AS response_count_auditable,
        try_cast(src."response_count_deleted" AS DOUBLE) AS response_count_deleted,
        try_cast(src."response_count_generated" AS DOUBLE) AS response_count_generated,
        try_cast(src."time_zone" AS VARCHAR) AS time_zone,
        try_cast(src."unsubscribed" AS BOOLEAN) AS is_unsubscribed,
        try_cast(src."user_type" AS VARCHAR) AS user_type,
        try_cast(src."username" AS VARCHAR) AS username
    FROM raw.user AS src
),
validated_rows AS (
    SELECT *
    FROM source_rows
    WHERE 1 = 1
      AND user_id IS NOT NULL AND email IS NOT NULL AND regexp_matches(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') AND account_status IS NOT NULL AND account_status IN ('active','inactive','suspended','deleted','pending')
      AND user_id IS NOT NULL
),
deduplicated_rows AS (
    SELECT *
    FROM validated_rows
    QUALIFY row_number() OVER (PARTITION BY user_id ORDER BY user_id) = 1
)
SELECT *
FROM deduplicated_rows
```

## gold SQL（仅供定位差异）

S5

```sql
-- DuckDB-compatible staging model for user table
-- Converted from dbt stg_qualtrics__user.sql
-- Implements validation rules and data quality transformations per staging_data_specification.yaml

with validated_user_data as (
    select
        id as user_id,
        -- Email validation and normalization
        case
            when email is not null and trim(email) != ''
                 and email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
            then lower(trim(email))
            else null
        end as email,
        first_name,
        last_name,
        try_cast(substr(account_creation_date, 1, 23) as timestamp) as account_created_at,
        -- Account expires validation
        case
            when account_expiration_date is not null
                 and try_cast(substr(account_expiration_date, 1, 23) as timestamp) > try_cast(substr(account_creation_date, 1, 23) as timestamp)
            then try_cast(substr(account_expiration_date, 1, 23) as timestamp)
            else null
        end as account_expires_at,
        -- Account status validation
        case
            when account_status in ('active', 'inactive', 'suspended', 'deleted', 'pending')
            then account_status
            else null  -- This will cause the row to be deleted below
        end as account_status,
        division_id,
        language,
        try_cast(substr(last_login_date, 1, 23) as timestamp) as last_login_at,
        organization_id,
        try_cast(substr(password_expiration_date, 1, 23) as timestamp) as password_expires_at,
        try_cast(substr(password_last_changed_date, 1, 23) as timestamp) as password_last_changed_at,
        cast(response_count_auditable as double) as response_count_auditable,
        cast(response_count_deleted as double) as response_count_deleted,
        cast(response_count_generated as double) as response_count_generated,
        time_zone,
        cast(unsubscribed as boolean) as is_unsubscribed,
        user_type,
        username
    from raw.user
    where id is not null  -- Basic primary key validation
)

select
    user_id,
    email,
    first_name,
    last_name,
    account_created_at,
    account_expires_at,
    account_status,
    division_id,
    language,
    last_login_at,
    organization_id,
    password_expires_at,
    password_last_changed_at,
    response_count_auditable,
    response_count_deleted,
    response_count_generated,
    time_zone,
    is_unsubscribed,
    user_type,
    username
from validated_user_data
where user_id is not null
  and email is not null  -- Essential field validation
  and account_status is not null  -- Required field with validation
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1987 | 1982 | 5 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| first_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| last_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| division_id | 0 | 0 | 0 | BIGINT | BIGINT |
| language | 0 | 0 | 0 | VARCHAR | VARCHAR |
| organization_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| response_count_auditable | 0 | 0 | 0 | DOUBLE | DOUBLE |
| response_count_deleted | 0 | 0 | 0 | DOUBLE | DOUBLE |
| response_count_generated | 0 | 0 | 0 | DOUBLE | DOUBLE |
| time_zone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| user_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| username | 0 | 0 | 0 | VARCHAR | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"user_id":"USE10000005855"},{"user_id":"USE10000006315"},{"user_id":"USE10000006704"},{"user_id":"USE10000007688"},{"user_id":"USE10000007960"}]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| D10_keyword_in_any_result_field | <code>命中数=4；assistant_trajectory   if name=='stg_qualtrics__user' and n=='account_expires_at': expr=f'CASE WHEN {expr} IS NULL OR {expr} &gt; try_cast(src."account_creation_date" AS TIMESTAMP) THEN {expr} ELSE NULL END'</code> |

## 轨迹索引（不放输出原文）

本题事件总数：81；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort; cat config/layer_dependencies.yaml</code> | 2649 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9208 | false | false |
| 13 | run | <code>find sql -maxdepth 3 -type f -printf '%p %s bytes\n'; sed -n '180,420p' qualtrics_start.yaml; sed -n '180,380p' run.py; wc -l docs/data_contract.yaml</code> | 11247 | false | false |
| 19 | run | <code>cat &gt; /tmp/gen_stg.py &lt;&lt;'PY'<br>import yaml, pathlib<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>colmaps={<br>'user':{'user_id':'id','account_created_at':'account_creation_date','account_expires_at':'</code> | 0 | false | false |
| 25 | run | <code>cat &gt; sql/intermediate/int_qualtrics__survey.sql &lt;&lt;'SQL'<br>WITH latest_version AS (<br>    SELECT *<br>    FROM staging.stg_qualtrics__survey_version<br>    WHERE is_published IS TRUE<br>),<br>previous_versions AS (<br> </code> | 0 | false | false |
| 27 | run | <code>cat &gt; sql/marts/qualtrics__survey_analytics.sql &lt;&lt;'SQL'<br>WITH quality_summary AS (<br>    SELECT<br>        survey_id,<br>        count(DISTINCT response_id)::BIGINT AS total_assessed_responses,<br>        count(D</code> | 0 | false | false |
| 31 | run | <code>cat &gt; /tmp/gen_distribution.py &lt;&lt;'PY'<br>from pathlib import Path<br>statuses='pending success error opened complaint skipped blocked failure unknown softbounce hardbounce surveystarted surveypartiallyfinis</code> | 0 | false | false |
| 55 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('qualtrics.duckdb',read_only=True)<br>for t,col in [('raw.survey_response','recorded_date'),('raw.survey_response','start_date'),('raw.user','account_creati</code> | 1177 | false | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
  if name=='stg_qualtrics__user' and n=='email': expr=f'lower(trim({expr}))'
```
event 19 / message

```text
  if name=='stg_qualtrics__user' and n=='account_expires_at': expr=f'CASE WHEN {expr} IS NULL OR {expr} > try_cast(src."account_creation_date" AS TIMESTAMP) THEN {expr} ELSE NULL END'
```
event 19 / message

```text
 if name=='stg_qualtrics__user': sql+="      AND user_id IS NOT NULL AND email IS NOT NULL AND regexp_matches(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$') AND account_status IS NOT NULL AND account_status IN ('active','inactive','suspended','deleted','pending')\n"
```
event 25 / message

```text
LEFT JOIN staging.stg_qualtrics__user AS publisher ON latest_version.publisher_user_id = publisher.user_id
```
event 25 / message

```text
LEFT JOIN staging.stg_qualtrics__user AS creator ON survey.creator_user_id = creator.user_id
```
event 25 / message

```text
LEFT JOIN staging.stg_qualtrics__user AS owner ON survey.owner_user_id = owner.user_id
```
event 31 / message

```text
LEFT JOIN staging.stg_qualtrics__user AS owner
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-014.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__user.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__user.sql`
- S6: `records/006_contract_impl-014.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/result.md`
- S10: `data/022_packages_work/022_impl-014_stg_qualtrics__user/022_impl-014_stg_qualtrics__user.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/qualtrics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions`
