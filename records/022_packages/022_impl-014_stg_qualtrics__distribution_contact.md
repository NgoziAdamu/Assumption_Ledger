# impl-014 | staging | stg_qualtrics__distribution_contact | 差异：S1；日期 原记录

## 契约完整原文

S3:352–383

```yaml
    - name: stg_qualtrics__distribution_contact
      description: "Distribution contact tracking and status"
      source_table: "raw.distribution_contact"
      primary_key: ["distribution_id", "contact_id"]
      columns:
        - name: contact_frequency_rule_id
          data_type: VARCHAR
        - name: contact_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: contact_lookup_id
          data_type: VARCHAR
        - name: distribution_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: opened_at
          data_type: VARCHAR
        - name: response_completed_at
          data_type: VARCHAR
        - name: response_id
          data_type: VARCHAR
        - name: response_started_at
          data_type: VARCHAR
        - name: sent_at
          data_type: VARCHAR
        - name: status
          data_type: VARCHAR
        - name: survey_link
          data_type: VARCHAR
        - name: survey_session_id
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT
        try_cast(src."contact_frequency_rule_id" AS VARCHAR) AS contact_frequency_rule_id,
        try_cast(src."contact_id" AS VARCHAR) AS contact_id,
        try_cast(src."contact_lookup_id" AS VARCHAR) AS contact_lookup_id,
        try_cast(src."distribution_id" AS VARCHAR) AS distribution_id,
        try_cast(src."opened_at" AS VARCHAR) AS opened_at,
        try_cast(src."response_completed_at" AS VARCHAR) AS response_completed_at,
        try_cast(src."response_id" AS VARCHAR) AS response_id,
        try_cast(src."response_started_at" AS VARCHAR) AS response_started_at,
        try_cast(src."sent_at" AS VARCHAR) AS sent_at,
        try_cast(src."status" AS VARCHAR) AS status,
        try_cast(src."survey_link" AS VARCHAR) AS survey_link,
        try_cast(src."survey_session_id" AS VARCHAR) AS survey_session_id
    FROM raw.distribution_contact AS src
),
validated_rows AS (
    SELECT *
    FROM source_rows
    WHERE 1 = 1
      AND distribution_id IS NOT NULL
      AND contact_id IS NOT NULL
),
deduplicated_rows AS (
    SELECT *
    FROM validated_rows
    QUALIFY row_number() OVER (PARTITION BY distribution_id, contact_id ORDER BY distribution_id, contact_id) = 1
)
SELECT *
FROM deduplicated_rows
```

## gold SQL（仅供定位差异）

S5

```sql
-- DuckDB-compatible staging model for distribution_contact table
-- Converted from dbt stg_qualtrics__distribution_contact.sql
-- Implements validation rules and data quality transformations per staging_data_specification.yaml

with validated_distribution_contact_data as (
    select
        trim(contact_frequency_rule_id) as contact_frequency_rule_id,
        trim(contact_id) as contact_id,
        trim(contact_lookup_id) as contact_lookup_id,
        trim(distribution_id) as distribution_id,
        try_cast(opened_at as timestamp) as opened_at,
        try_cast(response_completed_at as timestamp) as response_completed_at,
        trim(response_id) as response_id,
        try_cast(response_started_at as timestamp) as response_started_at,
        try_cast(sent_at as timestamp) as sent_at,
        trim(status) as status,
        trim(survey_link) as survey_link,
        trim(survey_session_id) as survey_session_id
    from raw.distribution_contact
    where distribution_id is not null
      and contact_id is not null  -- Composite primary key validation
)

select
    contact_frequency_rule_id,
    contact_id,
    contact_lookup_id,
    distribution_id,
    opened_at,
    response_completed_at,
    response_id,
    response_started_at,
    sent_at,
    status,
    survey_link,
    survey_session_id
from validated_distribution_contact_data
where distribution_id is not null
  and contact_id is not null
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5996 | 6000 | 0 | 0 | 0 | 4 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"distribution_id":"dis10000282658","contact_id":"hersanid276"}</code> |
| K2 | <code>{"distribution_id":"dis10000611595","contact_id":"hersanid256"}</code> |
| K3 | <code>{"distribution_id":"dis10000835264","contact_id":"cor65566760505"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| contact_frequency_rule_id | 0 | 0 | 4 | VARCHAR | VARCHAR |
| contact_id | 0 | 0 | 4 | VARCHAR | VARCHAR |
| contact_lookup_id | 0 | 0 | 4 | VARCHAR | VARCHAR |
| distribution_id | 0 | 0 | 4 | VARCHAR | VARCHAR |
| response_id | 0 | 0 | 4 | VARCHAR | VARCHAR |
| status | 0 | 0 | 4 | VARCHAR | VARCHAR |
| survey_link | 0 | 0 | 4 | VARCHAR | VARCHAR |
| survey_session_id | 0 | 0 | 4 | VARCHAR | VARCHAR |

contact_frequency_rule_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"CFR_8216780","rows":1}]</code> | <code>[{"value":"CFR_8216780","rows":1},{"value":"CFR_8229273","rows":1}]</code> |
| K2 | <code>[{"value":"CFR_6615193","rows":1}]</code> | <code>[{"value":"CFR_5395672","rows":1},{"value":"CFR_6615193","rows":1}]</code> |
| K3 | <code>[{"value":"CFR_7922723","rows":1}]</code> | <code>[{"value":"CFR_5507789","rows":1},{"value":"CFR_7922723","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

contact_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"hersanid276","rows":1}]</code> | <code>[{"value":"hersanid276","rows":2}]</code> |
| K2 | <code>[{"value":"hersanid256","rows":1}]</code> | <code>[{"value":"hersanid256","rows":2}]</code> |
| K3 | <code>[{"value":"COR65566760505","rows":1}]</code> | <code>[{"value":"COR65566760505","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

contact_lookup_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"CLU_4109703","rows":1}]</code> | <code>[{"value":"CLU_4109703","rows":1},{"value":"CLU_7906002","rows":1}]</code> |
| K2 | <code>[{"value":"CLU_1454801","rows":1}]</code> | <code>[{"value":"CLU_1346566","rows":1},{"value":"CLU_1454801","rows":1}]</code> |
| K3 | <code>[{"value":"CLU_4462335","rows":1}]</code> | <code>[{"value":"CLU_4462335","rows":1},{"value":"CLU_7794858","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

distribution_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"DIS10000282658","rows":1}]</code> | <code>[{"value":"DIS10000282658","rows":2}]</code> |
| K2 | <code>[{"value":"DIS10000611595","rows":1}]</code> | <code>[{"value":"DIS10000611595","rows":2}]</code> |
| K3 | <code>[{"value":"DIS10000835264","rows":1}]</code> | <code>[{"value":"DIS10000835264","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

response_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"SUR10011843753","rows":1}]</code> | <code>[{"value":"SUR10003602244","rows":1},{"value":"SUR10011843753","rows":1}]</code> |
| K2 | <code>[{"value":"SUR10012006116","rows":1}]</code> | <code>[{"value":"SUR10011427005","rows":1},{"value":"SUR10012006116","rows":1}]</code> |
| K3 | <code>[{"value":"SUR10004839720","rows":1}]</code> | <code>[{"value":"SUR10004839720","rows":1},{"value":"SUR10006455066","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

status 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"bounced","rows":1}]</code> | <code>[{"value":"bounced","rows":1},{"value":"sent","rows":1}]</code> |
| K2 | <code>[{"value":"sent","rows":1}]</code> | <code>[{"value":"clicked","rows":1},{"value":"sent","rows":1}]</code> |
| K3 | <code>[{"value":"clicked","rows":1}]</code> | <code>[{"value":"clicked","rows":1},{"value":"opened","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

survey_link 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"https://survey.com/link/4506","rows":1}]</code> | <code>[{"value":"https://survey.com/link/4506","rows":1},{"value":"https://survey.com/link/7776","rows":1}]</code> |
| K2 | <code>[{"value":"https://survey.com/link/9222","rows":1}]</code> | <code>[{"value":"https://survey.com/link/3992","rows":1},{"value":"https://survey.com/link/9222","rows":1}]</code> |
| K3 | <code>[{"value":"https://survey.com/link/7365","rows":1}]</code> | <code>[{"value":"https://survey.com/link/1330","rows":1},{"value":"https://survey.com/link/7365","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

survey_session_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"SES_6907932","rows":1}]</code> | <code>[{"value":"SES_6907932","rows":1},{"value":"SES_6960968","rows":1}]</code> |
| K2 | <code>[{"value":"SES_9997055","rows":1}]</code> | <code>[{"value":"SES_4931386","rows":1},{"value":"SES_9997055","rows":1}]</code> |
| K3 | <code>[{"value":"SES_9954537","rows":1}]</code> | <code>[{"value":"SES_4837447","rows":1},{"value":"SES_9954537","rows":1}]</code> |
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
| 29 | run | <code>cat &gt; sql/marts/qualtrics__contact.sql &lt;&lt;'SQL'<br>WITH distribution_response AS (<br>    SELECT<br>        distribution_contact.contact_id,<br>        distribution.survey_id,<br>        distribution_contact.sent_at,</code> | 0 | false | false |
| 31 | run | <code>cat &gt; /tmp/gen_distribution.py &lt;&lt;'PY'<br>from pathlib import Path<br>statuses='pending success error opened complaint skipped blocked failure unknown softbounce hardbounce surveystarted surveypartiallyfinis</code> | 0 | false | false |
| 37 | run | <code>cat &gt; /tmp/gen_daily.py &lt;&lt;'PY'<br>from pathlib import Path<br>channels={'anonymous':'anonymous','social_media':'social','personal_link':'gl','qr_code':'qr','email':'email','sms':'smsinvite'}<br>resp=[]<br>for out</code> | 0 | false | false |
| 39 | run | <code>python run.py &gt; /tmp/pipeline.log 2&gt;&amp;1; tail -100 /tmp/pipeline.log</code> | 6507 | true | false |
| 49 | run | <code>sed -n '80,145p' sql/marts/qualtrics__daily_breakdown.sql</code> | 3953 | true | false |
| 59 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>fmt="'%Y-%m-%d %H:%M:%S.%f %z'"<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> s=re.sub(r'try_cast\((src\."[^"]+") AS TIMESTAMP\)',rf"</code> | 331 | false | false |
| 65 | run | <code>grep -R 'try_cast\&#124;try_strptime' -n sql/marts/qualtrics__daily_breakdown.sql sql/marts/qualtrics__directory.sql &#124; head -30; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('qualtrics.duckdb',read_only=</code> | 1628 | false | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
    FROM staging.stg_qualtrics__distribution_contact AS distribution_contact
```
event 29 / message

```text
    FROM staging.stg_qualtrics__distribution_contact AS distribution_contact
```
event 31 / message

```text
    FROM staging.stg_qualtrics__distribution_contact
```
event 37 / message

```text
    FROM staging.stg_qualtrics__distribution_contact AS distribution_contact
```
event 37 / message

```text
    FROM staging.stg_qualtrics__distribution_contact
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-014.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__distribution_contact.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__distribution_contact.sql`
- S6: `records/006_contract_impl-014.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/result.md`
- S10: `data/022_packages_work/022_impl-014_stg_qualtrics__distribution_contact/022_impl-014_stg_qualtrics__distribution_contact.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/qualtrics.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions`
