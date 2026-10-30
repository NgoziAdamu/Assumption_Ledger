# impl-014 | staging | stg_qualtrics__core_contact | 差异：S1；日期 原记录

## 契约完整原文

S3:525–549

```yaml
    - name: stg_qualtrics__core_contact
      description: "Core contact information"
      source_table: "raw.core_contact"
      primary_key: ["contact_id"]
      columns:
        - name: contact_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: mailing_list_id
          data_type: VARCHAR
        - name: first_name
          data_type: VARCHAR
        - name: last_name
          data_type: VARCHAR
        - name: email
          data_type: VARCHAR
        - name: email_domain
          data_type: VARCHAR
        - name: external_data_reference
          data_type: VARCHAR
        - name: language
          data_type: VARCHAR
        - name: is_unsubscribed
          data_type: BOOLEAN

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT
        try_cast(src."id" AS VARCHAR) AS contact_id,
        try_cast(src."mailing_list_id" AS VARCHAR) AS mailing_list_id,
        try_cast(src."first_name" AS VARCHAR) AS first_name,
        try_cast(src."last_name" AS VARCHAR) AS last_name,
        try_cast(src."email" AS VARCHAR) AS email,
        CASE WHEN src."email" IS NOT NULL THEN lower(split_part(trim(src."email"), '@', 2)) ELSE NULL END AS email_domain,
        try_cast(src."external_data_reference" AS VARCHAR) AS external_data_reference,
        try_cast(src."language" AS VARCHAR) AS language,
        try_cast(src."unsubscribed" AS BOOLEAN) AS is_unsubscribed
    FROM raw.core_contact AS src
),
validated_rows AS (
    SELECT *
    FROM source_rows
    WHERE 1 = 1
      AND contact_id IS NOT NULL
),
deduplicated_rows AS (
    SELECT *
    FROM validated_rows
    QUALIFY row_number() OVER (PARTITION BY contact_id ORDER BY contact_id) = 1
)
SELECT *
FROM deduplicated_rows
```

## gold SQL（仅供定位差异）

S5

```sql
-- DuckDB-compatible staging model for core_contact table
-- Converted from dbt stg_qualtrics__core_contact.sql
-- Implements validation rules and data quality transformations per staging_data_specification.yaml

with validated_core_contact_data as (
    select
        id as contact_id,
        mailing_list_id,
        first_name,
        last_name,
        -- Email validation and normalization
        case
            when email is not null and trim(email) != ''
            then lower(trim(email))
            else null
        end as email,
        case
            when email is not null and trim(email) != ''
                 and email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
            then split_part(email, '@', 2)
            else null
        end as email_domain,
        external_data_reference,
        language,
        cast(unsubscribed as boolean) as is_unsubscribed
    from raw.core_contact
)

select
    contact_id,
    mailing_list_id,
    first_name,
    last_name,
    email,
    email_domain,
    external_data_reference,
    language,
    is_unsubscribed
from validated_core_contact_data
where contact_id is not null  -- Primary key validation
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 4994 | 8000 | 0 | 0 | 0 | 902 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"contact_id":"hersanid10"}</code> |
| K2 | <code>{"contact_id":"hersanid100"}</code> |
| K3 | <code>{"contact_id":"hersanid101"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| contact_id | 0 | 0 | 3006 | VARCHAR | VARCHAR |
| mailing_list_id | 0 | 0 | 3006 | VARCHAR | VARCHAR |
| first_name | 0 | 0 | 3006 | VARCHAR | VARCHAR |
| last_name | 0 | 0 | 3006 | VARCHAR | VARCHAR |
| email | 0 | 0 | 3006 | VARCHAR | VARCHAR |
| external_data_reference | 0 | 0 | 3006 | VARCHAR | VARCHAR |
| language | 0 | 0 | 3006 | VARCHAR | VARCHAR |
| is_unsubscribed | 0 | 0 | 3006 | BOOLEAN | BOOLEAN |

contact_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"hersanid10","rows":1}]</code> | <code>[{"value":"hersanid10","rows":4}]</code> |
| K2 | <code>[{"value":"hersanid100","rows":1}]</code> | <code>[{"value":"hersanid100","rows":6}]</code> |
| K3 | <code>[{"value":"hersanid101","rows":1}]</code> | <code>[{"value":"hersanid101","rows":5}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

mailing_list_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"ML_9e0a7cd635d1","rows":1}]</code> | <code>[{"value":"ML_1c34267fd3d6","rows":1},{"value":"ML_28d990fd730d","rows":1},{"value":"ML_3ab7471baa62","rows":1},{"value":"ML_9e0a7cd635d1","rows":1}]</code> |
| K2 | <code>[{"value":"ML_9693edb4c793","rows":1}]</code> | <code>[{"value":"ML_014735a14f86","rows":1},{"value":"ML_1ebcea3f7668","rows":1},{"value":"ML_4ee30826e323","rows":1},{"value":"ML_9693edb4c793","rows":1},{"value":"ML_a60bf008367b","rows":1}]</code> |
| K3 | <code>[{"value":"ML_11e717b7be5f","rows":1}]</code> | <code>[{"value":"ML_11e717b7be5f","rows":1},{"value":"ML_29c5d9ba7ec4","rows":1},{"value":"ML_61fc3867a55f","rows":1},{"value":"ML_baf3ab95c445","rows":1},{"value":"ML_f91a7e8ad827","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

first_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"David","rows":1}]</code> | <code>[{"value":"David","rows":1},{"value":"Jane","rows":1},{"value":"Matthew","rows":1},{"value":"Steven","rows":1}]</code> |
| K2 | <code>[{"value":"Donna","rows":1}]</code> | <code>[{"value":"Andrew","rows":1},{"value":"Ashley","rows":2},{"value":"Donna","rows":1},{"value":"Emily","rows":1},{"value":"Jessica","rows":1}]</code> |
| K3 | <code>[{"value":"Jessica","rows":1}]</code> | <code>[{"value":"Christopher","rows":1},{"value":"Donald","rows":1},{"value":"Jessica","rows":1},{"value":"Matthew","rows":1},{"value":"Robert","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

last_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Lewis","rows":1}]</code> | <code>[{"value":"Harris","rows":2},{"value":"Lewis","rows":1},{"value":"Smith","rows":1}]</code> |
| K2 | <code>[{"value":"Gonzalez","rows":1}]</code> | <code>[{"value":"Gonzalez","rows":2},{"value":"Johnson","rows":1},{"value":"Lee","rows":1},{"value":"Lopez","rows":1},{"value":"White","rows":1}]</code> |
| K3 | <code>[{"value":"Moore","rows":1}]</code> | <code>[{"value":"Gonzalez","rows":1},{"value":"Martinez","rows":1},{"value":"Moore","rows":1},{"value":"Robinson","rows":1},{"value":"Rodriguez","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

email 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"davidlewis@test.com","rows":1}]</code> | <code>[{"value":"davidlewis@test.com","rows":1},{"value":"janesmith@demo.org","rows":1},{"value":"matthewharris@test.com","rows":1},{"value":"stevenharris@test.com","rows":1}]</code> |
| K2 | <code>[{"value":"donnagonzalez@example.net","rows":1}]</code> | <code>[{"value":"andrewlee@example.org","rows":1},{"value":"ashleygonzalez@example.com","rows":1},{"value":"ashleylopez@demo.org","rows":1},{"value":"donnagonzalez@example.net","rows":1},{"value":"emilywhite@demo.org","rows":1}]</code> |
| K3 | <code>[{"value":"jessicamoore@example.com","rows":1}]</code> | <code>[{"value":"christopherrobinson@demo.org","rows":1},{"value":"donaldgonzalez@test.com","rows":1},{"value":"jessicamoore@example.com","rows":1},{"value":"matthewmartinez@example.net","rows":1},{"value":"robertrodriguez@example.org","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

external_data_reference 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"ref3228","rows":1}]</code> | <code>[{"value":"ref3228","rows":1},{"value":"ref4522","rows":1},{"value":"ref6284","rows":1},{"value":"ref7221","rows":1}]</code> |
| K2 | <code>[{"value":"ref5872","rows":1}]</code> | <code>[{"value":"ref3391","rows":1},{"value":"ref3866","rows":1},{"value":"ref4998","rows":1},{"value":"ref5872","rows":1},{"value":"ref8876","rows":1}]</code> |
| K3 | <code>[{"value":"ref2158","rows":1}]</code> | <code>[{"value":"ref2158","rows":1},{"value":"ref5363","rows":1},{"value":"ref5629","rows":1},{"value":"ref5653","rows":1},{"value":"ref6586","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

language 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"PT","rows":1}]</code> | <code>[{"value":"DE","rows":1},{"value":"ES","rows":1},{"value":"KO","rows":1},{"value":"PT","rows":1}]</code> |
| K2 | <code>[{"value":"IT","rows":1}]</code> | <code>[{"value":"ES","rows":1},{"value":"FR","rows":1},{"value":"IT","rows":2},{"value":"JA","rows":1},{"value":"ZH","rows":1}]</code> |
| K3 | <code>[{"value":"ZH","rows":1}]</code> | <code>[{"value":"ES","rows":1},{"value":"KO","rows":1},{"value":"PT","rows":1},{"value":"ZH","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

is_unsubscribed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"true","rows":1}]</code> | <code>[{"value":"false","rows":1},{"value":"true","rows":3}]</code> |
| K2 | <code>[{"value":"true","rows":1}]</code> | <code>[{"value":"false","rows":2},{"value":"true","rows":4}]</code> |
| K3 | <code>[{"value":"false","rows":1}]</code> | <code>[{"value":"false","rows":3},{"value":"true","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory p=Path('sql/staging/stg_qualtrics__core_contact.sql');s=p.read_text().replace('try_cast(src."email_domain" AS VARCHAR) AS email_domain','CASE WHEN src."email" IS NOT NULL THEN lower(split_part(trim(src."email"), \'@\', 2)) ELSE NULL END AS email_domain');p.write_text(s)</code> |

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
| 39 | run | <code>python run.py &gt; /tmp/pipeline.log 2&gt;&amp;1; tail -100 /tmp/pipeline.log</code> | 6507 | true | false |
| 41 | run | <code>grep -n -E 'ERROR&#124;Binder Error&#124;Catalog Error&#124;Conversion Error' /tmp/pipeline.log &#124; head -40; cat sql/staging/stg_qualtrics__block.sql; cat sql/staging/stg_qualtrics__contact_mailing_list_membership.sq</code> | 3899 | true | false |
| 43 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_qualtrics__block.sql');s=p.read_text().replace('src."is_locked"','src."block_locking"');p.write_text(s)<br>p=Path('sql/staging/stg_qualtri</code> | 451 | false | false |

### agent action 的 thought/message 命中原句

event 41 / message

```text
Running command: grep -n -E 'ERROR|Binder Error|Catalog Error|Conversion Error' /tmp/pipeline.log | head -40; cat sql/staging/stg_qualtrics__block.sql; cat sql/staging/stg_qualtrics__contact_mailing_list_membership.sql; cat sql/staging/stg_qualtrics__core_contact.sql
```
event 43 / message

```text
p=Path('sql/staging/stg_qualtrics__core_contact.sql');s=p.read_text().replace('try_cast(src."email_domain" AS VARCHAR) AS email_domain','CASE WHEN src."email" IS NOT NULL THEN lower(split_part(trim(src."email"), \'@\', 2)) ELSE NULL END AS email_domain');p.write_text(s)
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-014.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__core_contact.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__core_contact.sql`
- S6: `records/006_contract_impl-014.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/result.md`
- S10: `data/022_packages_work/022_impl-014_stg_qualtrics__core_contact/022_impl-014_stg_qualtrics__core_contact.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/qualtrics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions`
