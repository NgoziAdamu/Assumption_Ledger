# impl-014 | staging | stg_qualtrics__contact_mailing_list_membership | 差异：S1；日期 原记录

## 契约完整原文

S3:288–311

```yaml
    - name: stg_qualtrics__contact_mailing_list_membership
      description: "Contact mailing list membership information"
      source_table: "raw.contact_mailing_list_membership"
      primary_key: ["contact_id", "mailing_list_id"]
      columns:
        - name: contact_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: contact_lookup_id
          data_type: VARCHAR
        - name: directory_id
          data_type: VARCHAR
        - name: mailing_list_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: name
          data_type: VARCHAR
        - name: owner_user_id
          data_type: VARCHAR
        - name: unsubscribed_at
          data_type: TIMESTAMP
        - name: is_unsubscribed
          data_type: BOOLEAN

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT
        try_cast(src."contact_id" AS VARCHAR) AS contact_id,
        try_cast(src."contact_lookup_id" AS VARCHAR) AS contact_lookup_id,
        try_cast(src."directory_id" AS VARCHAR) AS directory_id,
        try_cast(src."mailing_list_id" AS VARCHAR) AS mailing_list_id,
        try_cast(src."name" AS VARCHAR) AS name,
        try_cast(src."owner_id" AS VARCHAR) AS owner_user_id,
        try_strptime(cast(src."unsubscribe_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS unsubscribed_at,
        try_cast(src."unsubscribed" AS BOOLEAN) AS is_unsubscribed
    FROM raw.contact_mailing_list_membership AS src
),
validated_rows AS (
    SELECT *
    FROM source_rows
    WHERE 1 = 1
      AND contact_id IS NOT NULL
      AND mailing_list_id IS NOT NULL
),
deduplicated_rows AS (
    SELECT *
    FROM validated_rows
    QUALIFY row_number() OVER (PARTITION BY contact_id, mailing_list_id ORDER BY contact_id, mailing_list_id) = 1
)
SELECT *
FROM deduplicated_rows
```

## gold SQL（仅供定位差异）

S5

```sql
-- DuckDB-compatible staging model for contact_mailing_list_membership table
-- Converted from dbt stg_qualtrics__contact_mailing_list_membership.sql
-- Implements validation rules and data quality transformations per staging_data_specification.yaml

with validated_contact_mailing_list_data as (
    select
        -- Required field validation
        case
            when contact_id is not null and trim(contact_id) != ''
            then contact_id
            else null
        end as contact_id,
        contact_lookup_id,
        directory_id,
        -- Required field validation
        case
            when mailing_list_id is not null and trim(mailing_list_id) != ''
            then mailing_list_id
            else null
        end as mailing_list_id,
        name,
        owner_id as owner_user_id,
        try_cast(unsubscribe_date as timestamp) as unsubscribed_at,
        cast(unsubscribed as boolean) as is_unsubscribed
    from raw.contact_mailing_list_membership
)

select
    contact_id,
    contact_lookup_id,
    directory_id,
    mailing_list_id,
    name,
    owner_user_id,
    unsubscribed_at,
    is_unsubscribed
from validated_contact_mailing_list_data
where contact_id is not null
  and mailing_list_id is not null  -- Required fields for composite primary key
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 7981 | 8000 | 0 | 0 | 0 | 18 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"contact_id":"cor11126615088","mailing_list_id":"ml_8fdc0931aeb8"}</code> |
| K2 | <code>{"contact_id":"cor93373701095","mailing_list_id":"ml_81531653fcce"}</code> |
| K3 | <code>{"contact_id":"hersanid120","mailing_list_id":"ml_c7f226f9addb"}</code> |
| K4 | <code>{"contact_id":"cor10047883613","mailing_list_id":"ml_82d9384813e9"}</code> |
| K5 | <code>{"contact_id":"cor10123251443","mailing_list_id":"ml_39b0e576a4eb"}</code> |
| K6 | <code>{"contact_id":"cor10151621538","mailing_list_id":"ml_b77cf8e79043"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| contact_id | 0 | 0 | 19 | VARCHAR | VARCHAR |
| contact_lookup_id | 0 | 0 | 19 | VARCHAR | VARCHAR |
| directory_id | 0 | 0 | 19 | VARCHAR | VARCHAR |
| mailing_list_id | 0 | 0 | 19 | VARCHAR | VARCHAR |
| name | 0 | 0 | 19 | VARCHAR | VARCHAR |
| owner_user_id | 0 | 0 | 19 | VARCHAR | VARCHAR |
| unsubscribed_at | 7981 | 7981 | 8000 | TIMESTAMP | TIMESTAMP |
| is_unsubscribed | 0 | 0 | 19 | BOOLEAN | BOOLEAN |

contact_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"COR11126615088","rows":1}]</code> | <code>[{"value":"COR11126615088","rows":2}]</code> |
| K2 | <code>[{"value":"COR93373701095","rows":1}]</code> | <code>[{"value":"COR93373701095","rows":2}]</code> |
| K3 | <code>[{"value":"hersanid120","rows":1}]</code> | <code>[{"value":"hersanid120","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

contact_lookup_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"CLU_7295453","rows":1}]</code> | <code>[{"value":"CLU_2830802","rows":1},{"value":"CLU_7295453","rows":1}]</code> |
| K2 | <code>[{"value":"CLU_2639124","rows":1}]</code> | <code>[{"value":"CLU_2639124","rows":1},{"value":"CLU_9997426","rows":1}]</code> |
| K3 | <code>[{"value":"CLU_6108364","rows":1}]</code> | <code>[{"value":"CLU_6108364","rows":1},{"value":"CLU_6826650","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

directory_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"DIR10000146419","rows":1}]</code> | <code>[{"value":"DIR10000037999","rows":1},{"value":"DIR10000146419","rows":1}]</code> |
| K2 | <code>[{"value":"DIR10000150978","rows":1}]</code> | <code>[{"value":"DIR10000014937","rows":1},{"value":"DIR10000150978","rows":1}]</code> |
| K3 | <code>[{"value":"DIR10000166505","rows":1}]</code> | <code>[{"value":"DIR10000166505","rows":1},{"value":"DIR10000204357","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

mailing_list_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"ML_8fdc0931aeb8","rows":1}]</code> | <code>[{"value":"ML_8fdc0931aeb8","rows":2}]</code> |
| K2 | <code>[{"value":"ML_81531653fcce","rows":1}]</code> | <code>[{"value":"ML_81531653fcce","rows":2}]</code> |
| K3 | <code>[{"value":"ML_c7f226f9addb","rows":1}]</code> | <code>[{"value":"ML_c7f226f9addb","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Membership 614","rows":1}]</code> | <code>[{"value":"Membership 182","rows":1},{"value":"Membership 614","rows":1}]</code> |
| K2 | <code>[{"value":"Membership 880","rows":1}]</code> | <code>[{"value":"Membership 519","rows":1},{"value":"Membership 880","rows":1}]</code> |
| K3 | <code>[{"value":"Membership 308","rows":1}]</code> | <code>[{"value":"Membership 173","rows":1},{"value":"Membership 308","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

owner_user_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"USE10000766815","rows":1}]</code> | <code>[{"value":"USE10000101563","rows":1},{"value":"USE10000766815","rows":1}]</code> |
| K2 | <code>[{"value":"USE10000172126","rows":1}]</code> | <code>[{"value":"USE10000172126","rows":1},{"value":"USE10000539188","rows":1}]</code> |
| K3 | <code>[{"value":"USE10000766347","rows":1}]</code> | <code>[{"value":"USE10000096097","rows":1},{"value":"USE10000766347","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

unsubscribed_at 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | 2025-04-14 05:37:48.914 | null |
| K5 | 2025-04-16 08:48:34.821 | null |
| K6 | 2025-07-22 16:13:43.388 | null |

is_unsubscribed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"true","rows":1}]</code> | <code>[{"value":"false","rows":1},{"value":"true","rows":1}]</code> |
| K2 | <code>[{"value":"false","rows":1}]</code> | <code>[{"value":"false","rows":1},{"value":"true","rows":1}]</code> |
| K3 | <code>[{"value":"true","rows":1}]</code> | <code>[{"value":"true","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

没有 True 痕迹。

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
| 23 | run | <code>cat &gt; sql/intermediate/int_qualtrics__contacts.sql &lt;&lt;'SQL'<br>WITH membership_aggregates AS (<br>    SELECT<br>        directory_id,<br>        contact_id,<br>        string_agg(mailing_list_id, ', ') FILTER (WHERE </code> | 0 | false | false |
| 37 | run | <code>cat &gt; /tmp/gen_daily.py &lt;&lt;'PY'<br>from pathlib import Path<br>channels={'anonymous':'anonymous','social_media':'social','personal_link':'gl','qr_code':'qr','email':'email','sms':'smsinvite'}<br>resp=[]<br>for out</code> | 0 | false | false |
| 39 | run | <code>python run.py &gt; /tmp/pipeline.log 2&gt;&amp;1; tail -100 /tmp/pipeline.log</code> | 6507 | true | false |
| 41 | run | <code>grep -n -E 'ERROR&#124;Binder Error&#124;Catalog Error&#124;Conversion Error' /tmp/pipeline.log &#124; head -40; cat sql/staging/stg_qualtrics__block.sql; cat sql/staging/stg_qualtrics__contact_mailing_list_membership.sq</code> | 3899 | true | false |
| 43 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_qualtrics__block.sql');s=p.read_text().replace('src."is_locked"','src."block_locking"');p.write_text(s)<br>p=Path('sql/staging/stg_qualtri</code> | 451 | false | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
    FROM staging.stg_qualtrics__contact_mailing_list_membership
```
event 37 / message

```text
    FROM staging.stg_qualtrics__contact_mailing_list_membership
```
event 41 / message

```text
Running command: grep -n -E 'ERROR|Binder Error|Catalog Error|Conversion Error' /tmp/pipeline.log | head -40; cat sql/staging/stg_qualtrics__block.sql; cat sql/staging/stg_qualtrics__contact_mailing_list_membership.sql; cat sql/staging/stg_qualtrics__core_contact.sql
```
event 43 / message

```text
p=Path('sql/staging/stg_qualtrics__contact_mailing_list_membership.sql');s=p.read_text().replace('src."owner_user_id"','src."owner_id"');p.write_text(s)
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-014.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__contact_mailing_list_membership.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__contact_mailing_list_membership.sql`
- S6: `records/006_contract_impl-014.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/result.md`
- S10: `data/022_packages_work/022_impl-014_stg_qualtrics__contact_mailing_list_membership/022_impl-014_stg_qualtrics__contact_mailing_list_membership.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/qualtrics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions`
