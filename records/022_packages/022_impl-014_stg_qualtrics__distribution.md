# impl-014 | staging | stg_qualtrics__distribution | 差异：S1；日期 原记录

## 契约完整原文

S3:384–436

```yaml
    - name: stg_qualtrics__distribution
      description: "Survey distribution configuration and metadata"
      source_table: "raw.distribution"
      primary_key: ["distribution_id"]
      columns:
        - name: distribution_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: created_at
          data_type: TIMESTAMP
        - name: header_from_email
          data_type: VARCHAR
        - name: header_from_name
          data_type: VARCHAR
        - name: header_reply_to_email
          data_type: VARCHAR
        - name: header_subject
          data_type: VARCHAR
        - name: message_library_id
          data_type: BIGINT
        - name: message_id
          data_type: BIGINT
        - name: message_text
          data_type: VARCHAR
        - name: last_modified_at
          data_type: TIMESTAMP
        - name: organization_id
          data_type: BIGINT
        - name: owner_user_id
          data_type: VARCHAR
        - name: parent_distribution_id
          data_type: VARCHAR
        - name: recipient_contact_id
          data_type: VARCHAR
        - name: recipient_library_id
          data_type: BIGINT
        - name: recipient_mailing_list_id
          data_type: VARCHAR
        - name: recipient_sample_id
          data_type: BIGINT
        - name: request_status
          data_type: VARCHAR
        - name: request_type
          data_type: VARCHAR
        - name: send_at
          data_type: TIMESTAMP
        - name: survey_link_expires_at
          data_type: TIMESTAMP
        - name: survey_link_type
          data_type: VARCHAR
        - name: survey_id
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT
        try_cast(src."id" AS VARCHAR) AS distribution_id,
        try_strptime(cast(src."created_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS created_at,
        try_cast(src."header_from_email" AS VARCHAR) AS header_from_email,
        try_cast(src."header_from_name" AS VARCHAR) AS header_from_name,
        try_cast(src."header_reply_to_email" AS VARCHAR) AS header_reply_to_email,
        try_cast(src."header_subject" AS VARCHAR) AS header_subject,
        try_cast(src."message_library_id" AS BIGINT) AS message_library_id,
        try_cast(src."message_message_id" AS BIGINT) AS message_id,
        try_cast(src."message_message_text" AS VARCHAR) AS message_text,
        try_strptime(cast(src."modified_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS last_modified_at,
        try_cast(src."organization_id" AS BIGINT) AS organization_id,
        try_cast(src."owner_id" AS VARCHAR) AS owner_user_id,
        try_cast(src."parent_distribution_id" AS VARCHAR) AS parent_distribution_id,
        try_cast(src."recipient_contact_id" AS VARCHAR) AS recipient_contact_id,
        try_cast(src."recipient_library_id" AS BIGINT) AS recipient_library_id,
        try_cast(src."recipient_mailing_list_id" AS VARCHAR) AS recipient_mailing_list_id,
        try_cast(src."recipient_sample_id" AS BIGINT) AS recipient_sample_id,
        try_cast(src."request_status" AS VARCHAR) AS request_status,
        try_cast(src."request_type" AS VARCHAR) AS request_type,
        try_strptime(cast(src."send_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS send_at,
        try_strptime(cast(src."survey_link_expiration_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS survey_link_expires_at,
        try_cast(src."survey_link_link_type" AS VARCHAR) AS survey_link_type,
        try_cast(src."survey_link_survey_id" AS VARCHAR) AS survey_id
    FROM raw.distribution AS src
),
validated_rows AS (
    SELECT *
    FROM source_rows
    WHERE 1 = 1
      AND distribution_id IS NOT NULL
),
deduplicated_rows AS (
    SELECT *
    FROM validated_rows
    QUALIFY row_number() OVER (PARTITION BY distribution_id ORDER BY distribution_id) = 1
)
SELECT *
FROM deduplicated_rows
```

## gold SQL（仅供定位差异）

S5

```sql
-- DuckDB-compatible staging model for distribution table
-- Converted from dbt stg_qualtrics__distribution.sql
-- Implements validation rules and data quality transformations per staging_data_specification.yaml

with validated_distribution_data as (
    select
        id as distribution_id,
        try_cast(created_date as timestamp) as created_at,
        lower(trim(header_from_email)) as header_from_email,
        trim(header_from_name) as header_from_name,
        lower(trim(header_reply_to_email)) as header_reply_to_email,
        trim(header_subject) as header_subject,
        cast(message_library_id as bigint) as message_library_id,
        cast(message_message_id as bigint) as message_id,
        cast(message_message_text as varchar) as message_text,
        try_cast(modified_date as timestamp) as last_modified_at,
        cast(organization_id as bigint) as organization_id,
        trim(owner_id) as owner_user_id,
        trim(parent_distribution_id) as parent_distribution_id,
        trim(recipient_contact_id) as recipient_contact_id,
        cast(recipient_library_id as bigint) as recipient_library_id,
        trim(recipient_mailing_list_id) as recipient_mailing_list_id,
        cast(recipient_sample_id as bigint) as recipient_sample_id,
        trim(request_status) as request_status,
        trim(request_type) as request_type,
        try_cast(send_date as timestamp) as send_at,
        try_cast(survey_link_expiration_date as timestamp) as survey_link_expires_at,
        trim(survey_link_link_type) as survey_link_type,
        trim(survey_link_survey_id) as survey_id
    from raw.distribution
    where id is not null  -- Basic primary key validation
)

select
    distribution_id,
    created_at,
    header_from_email,
    header_from_name,
    header_reply_to_email,
    header_subject,
    message_library_id,
    message_id,
    message_text,
    last_modified_at,
    organization_id,
    owner_user_id,
    parent_distribution_id,
    recipient_contact_id,
    recipient_library_id,
    recipient_mailing_list_id,
    recipient_sample_id,
    request_status,
    request_type,
    send_at,
    survey_link_expires_at,
    survey_link_type,
    survey_id
from validated_distribution_data
where distribution_id is not null
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 3000 | 3000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"distribution_id":"dis10000000636"}</code> |
| K2 | <code>{"distribution_id":"dis10000001617"}</code> |
| K3 | <code>{"distribution_id":"dis10000002481"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| distribution_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_at | 3000 | 3000 | 3000 | TIMESTAMP | TIMESTAMP |
| header_from_email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| header_from_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| header_reply_to_email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| header_subject | 0 | 0 | 0 | VARCHAR | VARCHAR |
| message_library_id | 0 | 0 | 0 | BIGINT | BIGINT |
| message_id | 0 | 0 | 0 | BIGINT | BIGINT |
| message_text | 0 | 0 | 0 | VARCHAR | VARCHAR |
| last_modified_at | 3000 | 3000 | 3000 | TIMESTAMP | TIMESTAMP |
| organization_id | 0 | 0 | 0 | BIGINT | BIGINT |
| owner_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| parent_distribution_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| recipient_contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| recipient_library_id | 0 | 0 | 0 | BIGINT | BIGINT |
| recipient_mailing_list_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| recipient_sample_id | 0 | 0 | 0 | BIGINT | BIGINT |
| request_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| request_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| send_at | 3000 | 3000 | 3000 | TIMESTAMP | TIMESTAMP |
| survey_link_expires_at | 3000 | 3000 | 3000 | TIMESTAMP | TIMESTAMP |
| survey_link_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| survey_id | 0 | 0 | 0 | VARCHAR | VARCHAR |

created_at 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2025-06-05 18:02:57.668 | null |
| K2 | 2025-05-06 14:59:01.108 | null |
| K3 | 2025-03-13 08:44:26.651 | null |

last_modified_at 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2025-07-11 13:49:22.353 | null |
| K2 | 2025-09-01 06:30:52.075 | null |
| K3 | 2025-09-01 12:57:30.221 | null |

send_at 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2025-08-22 06:31:12.891 | null |
| K2 | 2025-08-14 18:25:12.144 | null |
| K3 | 2025-08-17 10:49:22.455 | null |

survey_link_expires_at 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2025-11-30 07:31:00.272 | null |
| K2 | 2026-01-29 01:42:39.095 | null |
| K3 | 2025-12-07 23:34:50.572 | null |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"organization_id","value":"2104505001950"}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：81；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort; cat config/layer_dependencies.yaml</code> | 2649 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9208 | false | false |
| 11 | run | <code>sed -n '1,180p' qualtrics_start.yaml</code> | 4629 | false | false |
| 13 | run | <code>find sql -maxdepth 3 -type f -printf '%p %s bytes\n'; sed -n '180,420p' qualtrics_start.yaml; sed -n '180,380p' run.py; wc -l docs/data_contract.yaml</code> | 11247 | false | false |
| 19 | run | <code>cat &gt; /tmp/gen_stg.py &lt;&lt;'PY'<br>import yaml, pathlib<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>colmaps={<br>'user':{'user_id':'id','account_created_at':'account_creation_date','account_expires_at':'</code> | 0 | false | false |
| 29 | run | <code>cat &gt; sql/marts/qualtrics__contact.sql &lt;&lt;'SQL'<br>WITH distribution_response AS (<br>    SELECT<br>        distribution_contact.contact_id,<br>        distribution.survey_id,<br>        distribution_contact.sent_at,</code> | 0 | false | false |
| 31 | run | <code>cat &gt; /tmp/gen_distribution.py &lt;&lt;'PY'<br>from pathlib import Path<br>statuses='pending success error opened complaint skipped blocked failure unknown softbounce hardbounce surveystarted surveypartiallyfinis</code> | 0 | false | false |
| 39 | run | <code>python run.py &gt; /tmp/pipeline.log 2&gt;&amp;1; tail -100 /tmp/pipeline.log</code> | 6507 | true | false |
| 59 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>fmt="'%Y-%m-%d %H:%M:%S.%f %z'"<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> s=re.sub(r'try_cast\((src\."[^"]+") AS TIMESTAMP\)',rf"</code> | 331 | false | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
    INNER JOIN staging.stg_qualtrics__distribution AS distribution
```
event 29 / message

```text
    LEFT JOIN staging.stg_qualtrics__distribution AS distribution
```
event 31 / message

```text
FROM staging.stg_qualtrics__distribution AS distribution
```
event 31 / message

```text
LEFT JOIN staging.stg_qualtrics__distribution AS parent
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-014.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__distribution.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__distribution.sql`
- S6: `records/006_contract_impl-014.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/result.md`
- S10: `data/022_packages_work/022_impl-014_stg_qualtrics__distribution/022_impl-014_stg_qualtrics__distribution.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/qualtrics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions`
