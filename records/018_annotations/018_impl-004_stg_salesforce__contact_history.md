# impl-004 / stg_salesforce__contact_history（v2定稿）

## 1. 差异描述与判定

history_unique_key生成约定未写明，hash与id加时间导致全部键不相交；另有1行日期边界差异。

已核实：双方raw一致。agent用hash(_fivetran_start,_fivetran_end)，gold用id与执行时刻拼接；契约未定义history_unique_key算法。正常当前时钟下替换公式仍为6000行/126000格；把该公式固定为gold原时刻后剩1行/1格。固定时刻只用于诊断未规定的key约定。activity_rule_gold_day单独改日期校验时键仍完全不相交，6000行/126000格不变，按v2不能列参与因素。 A项仅表示差异取决于契约未定的选择，不据gold实现认定agent做错。

主要原因：**A**；把握：**中**。
参与因素：无：activity_rule_gold_day单独修复未减少含键规模。标记：无。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-004_stg_salesforce__contact_history.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-004_staging_stg_salesforce__contact_history.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-004/docs/data_contract.yaml` 第432–490行。
- [原始轨迹转录](../014_trace_impl-004.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-004.json)；[015三方raw核对](../015_raw_impl-004.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_salesforce__contact_history
      description: "Historical tracking of contact changes"
      source_table: "raw.contact_history"
      columns:
        - name: contact_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: account_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
        - name: contact_description
          data_type: VARCHAR
        - name: email
          data_type: VARCHAR
        - name: first_name
          data_type: VARCHAR
        - name: is_deleted
          data_type: BOOLEAN
        - name: last_activity_date
          data_type: DATE
          validation_rules:
            - rule: "last_activity_date = CASE WHEN last_activity_date IS NOT NULL AND last_activity_date > CURRENT_DATE THEN NULL WHEN last_activity_date IS NOT NULL AND last_activity_date < '2020-01-01' THEN NULL ELSE last_activity_date END"
              on_failure: nullify_field
        - name: last_modified_date
          data_type: TIMESTAMP
        - name: last_name
          data_type: VARCHAR
        - name: lead_source
          data_type: VARCHAR
        - name: mailing_city
          data_type: VARCHAR
        - name: mailing_country
          data_type: VARCHAR
        - name: mailing_postal_code
          data_type: VARCHAR
          validation_rules:
            - rule: "mailing_postal_code = CASE WHEN mailing_postal_code = '' THEN NULL WHEN mailing_postal_code IS NOT NULL AND LENGTH(TRIM(mailing_postal_code)) < 3 THEN DELETE_ROW WHEN mailing_postal_code IS NOT NULL AND LENGTH(TRIM(mailing_postal_code)) > 12 THEN NULL ELSE UPPER(TRIM(mailing_postal_code)) END"
              on_failure: correct
        - name: mailing_state
          data_type: VARCHAR
        - name: mailing_street
          data_type: VARCHAR
        - name: mobile_phone
          data_type: VARCHAR
          validation_rules:
            - rule: "mobile_phone = CASE WHEN mobile_phone = '' THEN NULL WHEN mobile_phone IS NOT NULL AND LENGTH(REGEXP_REPLACE(mobile_phone, '[^0-9]', '')) < 10 THEN NULL ELSE REGEXP_REPLACE(mobile_phone, '[^0-9+()-]', '') END"
              on_failure: nullify_field
        - name: contact_name
          data_type: VARCHAR
        - name: owner_id
          data_type: VARCHAR
        - name: phone
          data_type: VARCHAR
        - name: title
          data_type: VARCHAR
        - name: history_unique_key
          data_type: VARCHAR
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/sql/staging/stg_salesforce__contact_history.sql`
```sql
   1: WITH source_rows AS (
   2:     SELECT
   3:         CAST("id" AS VARCHAR) AS contact_id,
   4:         CAST("account_id" AS VARCHAR) AS account_id,
   5:         CAST("_fivetran_start" AS TIMESTAMP) AS created_date,
   6:         CAST("description" AS VARCHAR) AS contact_description,
   7:         CAST("email" AS VARCHAR) AS email,
   8:         CAST("first_name" AS VARCHAR) AS first_name,
   9:         CAST("is_deleted" AS BOOLEAN) AS is_deleted,
  10:         CAST("last_activity_date" AS DATE) AS last_activity_date,
  11:         CAST("last_modified_date" AS TIMESTAMP) AS last_modified_date,
  12:         CAST("last_name" AS VARCHAR) AS last_name,
  13:         CAST("lead_source" AS VARCHAR) AS lead_source,
  14:         CAST("mailing_city" AS VARCHAR) AS mailing_city,
  15:         CAST("mailing_country" AS VARCHAR) AS mailing_country,
  16:         CASE WHEN CAST("mailing_postal_code" AS VARCHAR) = '' THEN NULL WHEN LENGTH(TRIM(CAST("mailing_postal_code" AS VARCHAR))) > 12 THEN NULL ELSE UPPER(TRIM(CAST("mailing_postal_code" AS VARCHAR))) END AS mailing_postal_code,
  17:         CAST("mailing_state" AS VARCHAR) AS mailing_state,
  18:         CAST("mailing_street" AS VARCHAR) AS mailing_street,
  19:         CASE WHEN CAST("mobile_phone" AS VARCHAR) = '' THEN NULL WHEN LENGTH(REGEXP_REPLACE(CAST("mobile_phone" AS VARCHAR), '[^0-9]', '')) < 10 THEN NULL ELSE REGEXP_REPLACE(CAST("mobile_phone" AS VARCHAR), '[^0-9+()-]', '') END AS mobile_phone,
  20:         CAST("name" AS VARCHAR) AS contact_name,
  21:         CAST("owner_id" AS VARCHAR) AS owner_id,
  22:         CAST("phone" AS VARCHAR) AS phone,
  23:         CAST("title" AS VARCHAR) AS title,
  24:         CAST(hash("_fivetran_start", "_fivetran_end") AS VARCHAR) AS history_unique_key
  25:     FROM raw.contact_history
  26: )
  27: SELECT *
  28: FROM source_rows
  29: WHERE contact_id IS NOT NULL AND
  30:         ("mailing_postal_code" IS NULL OR "mailing_postal_code" = '' OR LENGTH(TRIM(CAST("mailing_postal_code" AS VARCHAR))) >= 3)
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/sql/staging/stg_salesforce__contact_history.sql`
```sql
   1: with base as (
   2:     select *
   3:     from raw.contact_history
   4: ),
   5: 
   6: validated as (
   7:     select
   8:         id,
   9:         account_id,
  10:         -- Generate created_date as current timestamp for history tracking since raw table might not have it
  11:         current_timestamp as created_date,
  12:         description,
  13:         email,
  14:         first_name,
  15:         -- Apply validation rule for is_deleted
  16:         case
  17:             when is_deleted is null then false
  18:             when is_deleted not in (true, false) then false
  19:             else is_deleted
  20:         end as is_deleted,
  21:         -- Apply validation rule for last_activity_date
  22:         case
  23:             when last_activity_date is not null and last_activity_date > current_date then null
  24:             when last_activity_date is not null and last_activity_date < '2020-01-01' then null
  25:             else last_activity_date
  26:         end as last_activity_date,
  27:         last_modified_date,
  28:         last_name,
  29:         lead_source,
  30:         mailing_city,
  31:         mailing_country,
  32:         -- Missing column from raw data - set to null
  33:         cast(null as varchar) as mailing_country_code,
  34:         -- Apply validation rule for mailing_postal_code
  35:         case
  36:             when mailing_postal_code = '' then null
  37:             when mailing_postal_code is not null and length(trim(mailing_postal_code)) < 3 then null
  38:             when mailing_postal_code is not null and length(trim(mailing_postal_code)) > 12 then null
  39:             else upper(trim(mailing_postal_code))
  40:         end as mailing_postal_code,
  41:         mailing_state,
  42:         mailing_street,
  43:         -- Apply validation rule for mobile_phone - delete rows with invalid phone numbers
  44:         case
  45:             when mobile_phone = '' then null
  46:             when mobile_phone is not null and length(regexp_replace(mobile_phone, '[^0-9]', '')) < 10 then null
  47:             else regexp_replace(mobile_phone, '[^0-9+()-]', '')
  48:         end as mobile_phone,
  49:         name,
  50:         owner_id,
  51:         phone,
  52:         title,
  53:         -- Generate unique key for history tracking
  54:         concat(id, '_', current_timestamp::varchar) as history_unique_key
  55:     from base
  56:     -- Delete rows with invalid phone numbers according to YAML spec
  57:     where (mobile_phone = '' or mobile_phone is null or length(regexp_replace(mobile_phone, '[^0-9]', '')) >= 10)
  58: )
  59: 
  60: select
  61:     cast(contact_id as varchar) as contact_id,
  62:     cast(account_id as varchar) as account_id,
  63:     cast(created_date as timestamp) as created_date,
  64:     cast(description as varchar) as contact_description,
  65:     cast(email as varchar) as email,
  66:     cast(first_name as varchar) as first_name,
  67:     cast(is_deleted as boolean) as is_deleted,
  68:     cast(last_activity_date as date) as last_activity_date,
  69:     cast(last_modified_date as timestamp) as last_modified_date,
  70:     cast(last_name as varchar) as last_name,
  71:     cast(lead_source as varchar) as lead_source,
  72:     cast(mailing_city as varchar) as mailing_city,
  73:     cast(mailing_country as varchar) as mailing_country,
  74:     cast(mailing_country_code as varchar) as mailing_country_code,
  75:     cast(mailing_postal_code as varchar) as mailing_postal_code,
  76:     cast(mailing_state as varchar) as mailing_state,
  77:     cast(mailing_street as varchar) as mailing_street,
  78:     cast(mobile_phone as varchar) as mobile_phone,
  79:     cast(name as varchar) as contact_name,
  80:     cast(owner_id as varchar) as owner_id,
  81:     cast(phone as varchar) as phone,
  82:     cast(title as varchar) as title,
  83:     cast(history_unique_key as varchar) as history_unique_key
  84: from (
  85:     select
  86:         id as contact_id,
  87:         account_id,
  88:         created_date,
  89:         description,
  90:         email,
  91:         first_name,
  92:         is_deleted,
  93:         last_activity_date,
  94:         last_modified_date,
  95:         last_name,
  96:         lead_source,
  97:         mailing_city,
  98:         mailing_country,
  99:         mailing_country_code,
 100:         mailing_postal_code,
 101:         mailing_state,
 102:         mailing_street,
 103:         mobile_phone,
 104:         name,
 105:         owner_id,
 106:         phone,
 107:         title,
 108:         history_unique_key
 109:     from validated
 110: ) as final_data
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.contact_history|gold_vs_initial|True|True|True||
|raw.contact_history|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event 1提供契约；event 15→16读取raw schema；event 17/25/29生成与修复hash表达式。未看到规定history_unique_key算法的业务文档。按contact_id对齐的只读诊断定位到last_activity_date 1行，而不是把无共同键时列计数0误作值一致。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|history_key_frozen|A|针对本表的具体说明|51|

### history_key_frozen：针对本表的具体说明

明确指出History同一目标字段的缺源、替代来源及原因；虽然覆盖两张History表，已经定位本表这一选择，不要求重复完整模型名。

事件 **51**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-004.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/.events/sessions/024a80d8-934c-43-4e69514191069ca/events/51.json`。
```text
History 原始表没有契约字段 `created_date` / `history_unique_key`，使用源 `_fivetran_start` 作为变更时间，并以 `_fivetran_start` 与 `_fivetran_end` 计算字符串唯一标识；该映射使快照能够按源可用的版本时间运行。
```

已检视53个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：需要查业务说明。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-004.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **1条**（含014复用；本轮新增0条）；核实代价档：**需要查业务说明**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 014-V1 / 核实查询

来源：`records/014_queries_impl-004.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/salesforce.duckdb`。

```sql
SELECT count(*) n,count(distinct id) ids,count(*) FILTER(WHERE last_activity_date < DATE '2020-01-01') old_activity,count(*) FILTER(WHERE last_activity_date > DATE '2026-10-25') future_activity,count(*) FILTER(WHERE mobile_phone <> '' AND length(regexp_replace(mobile_phone,'[^0-9]',''))<10) short_mobile,count(*) FILTER(WHERE mailing_postal_code <> '' AND length(trim(mailing_postal_code))<3) short_postal FROM raw.contact_history
```
结果原文：
```json
{
  "columns": [
    "n",
    "ids",
    "old_activity",
    "future_activity",
    "short_mobile",
    "short_postal"
  ],
  "rows": [
    [
      3000,
      2369,
      0,
      0,
      0,
      0
    ]
  ]
}
```

### 014-D1 / 诊断查询

来源：`records/014_queries_impl-004.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`。

```sql
SELECT count(*) n,count(distinct id) ids,count(*) FILTER(WHERE last_activity_date < DATE '2020-01-01') old_activity,count(*) FILTER(WHERE last_activity_date > DATE '2026-10-25') future_activity,count(*) FILTER(WHERE mobile_phone <> '' AND length(regexp_replace(mobile_phone,'[^0-9]',''))<10) short_mobile,count(*) FILTER(WHERE mailing_postal_code <> '' AND length(trim(mailing_postal_code))<3) short_postal FROM raw.contact_history
```
结果原文：
```json
{
  "columns": [
    "n",
    "ids",
    "old_activity",
    "future_activity",
    "short_mobile",
    "short_postal"
  ],
  "rows": [
    [
      3000,
      2369,
      0,
      0,
      0,
      0
    ]
  ]
}
```

### 014-D_raw / 诊断查询

来源：`records/014_queries_impl-004.json`；数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/salesforce.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb']`。

```sql
SELECT * FROM raw.contact_history
```
结果原文：
```json
{
  "result": {
    "columns_identical": true,
    "agent_rows": 3000,
    "gold_rows": 3000,
    "agent_only_rows": 0,
    "gold_only_rows": 0
  },
  "operation": "Python Counter of full typed rows, exact multiset difference"
}
```

### 014-D_clock / 诊断查询

来源：`records/014_queries_impl-004.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`。

```sql
SELECT min(created_date),max(created_date),min(history_unique_key),max(history_unique_key) FROM staging.stg_salesforce__contact_history
```
结果原文：
```json
{
  "columns": [
    "min(created_date)",
    "max(created_date)",
    "min(history_unique_key)",
    "max(history_unique_key)"
  ],
  "rows": [
    [
      "2025-10-24 15:03:11.630125",
      "2025-10-24 15:03:11.630125",
      "00302EQ38cvTeOD_2025-10-24 15:03:11.630125+08",
      "003zzyPo1cN6qDC_2025-10-24 15:03:11.630125+08"
    ]
  ]
}
```

### 014-D_activity / 诊断查询

来源：`records/014_queries_impl-004.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`。

```sql
SELECT contact_id,last_activity_date FROM staging.stg_salesforce__contact_history WHERE last_activity_date IS NULL
```
结果原文：
```json
{
  "columns": [
    "contact_id",
    "last_activity_date"
  ],
  "rows": [
    [
      "003jpvUgLoY7fm4",
      null
    ]
  ]
}
```

### 014-D_clock / 诊断查询

来源：`records/014_queries_impl-004.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`。

```sql
SELECT min(created_date),max(created_date),min(history_unique_key),max(history_unique_key) FROM staging.stg_salesforce__contact_history
```
结果原文：
```json
{
  "columns": [
    "min(created_date)",
    "max(created_date)",
    "min(history_unique_key)",
    "max(history_unique_key)"
  ],
  "rows": [
    [
      "2025-10-24 15:03:11.630125",
      "2025-10-24 15:03:11.630125",
      "00302EQ38cvTeOD_2025-10-24 15:03:11.630125+08",
      "003zzyPo1cN6qDC_2025-10-24 15:03:11.630125+08"
    ]
  ]
}
```

### 014-D_activity / 诊断查询

来源：`records/014_queries_impl-004.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`。

```sql
SELECT contact_id,last_activity_date FROM staging.stg_salesforce__contact_history WHERE last_activity_date IS NULL
```
结果原文：
```json
{
  "columns": [
    "contact_id",
    "last_activity_date"
  ],
  "rows": [
    [
      "003jpvUgLoY7fm4",
      null
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['contact_id', 'account_id', 'mailing_postal_code', 'owner_id', 'history_unique_key']`；比较列（与键取并集）：`['account_id', 'contact_description', 'contact_name', 'email', 'first_name', 'is_deleted', 'last_activity_date', 'last_modified_date', 'last_name', 'lead_source', 'mailing_city', 'mailing_country', 'mailing_postal_code', 'mailing_state', 'mailing_street', 'mobile_phone', 'owner_id', 'phone', 'title']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：records/014_reruns_impl-004.json

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|history_key|6000→6000|126000→126000|无|
|activity_rule|6000→6000|126000→126000|无|
|history_key_frozen|6000→1|126000→1|无|
|activity_rule_gold_day|6000→6000|126000→126000|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L1|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L2|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L3|3000|3000|3000|3000|0/0|0|6000|126000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

### 重跑 baseline

SQL：`data/014_work/impl-004/baseline.sql`；SHA-256：`6fbac2cdaddd1bdd3dcab9b556649f35b3dc780b74d1f217fd60298d5940727f`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L1|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L2|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L3|3000|3000|3000|3000|0/0|0|6000|126000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

### 重跑 history_key

SQL：`data/014_work/impl-004/history_key.sql`；SHA-256：`2004dd541d052dde38599ea208fd3e3b15b6373c9b018464612fbc82404483a5`。

唯一原文位置offset=1557，替换前：
```sql
CAST(hash("_fivetran_start", "_fivetran_end") AS VARCHAR)
```
替换后：
```sql
concat(id, '_', current_timestamp::varchar)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L1|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L2|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L3|3000|3000|3000|3000|0/0|0|6000|126000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

### 重跑 activity_rule

SQL：`data/014_work/impl-004/activity_rule.sql`；SHA-256：`a57e6bc967a94304fabde488b6c13f2e711846ecc5cf1db0a9f19a9ae87d6d03`。

唯一原文位置offset=413，替换前：
```sql
CAST("last_activity_date" AS DATE) AS last_activity_date
```
替换后：
```sql
CASE WHEN last_activity_date > CURRENT_DATE OR last_activity_date < DATE '2020-01-01' THEN NULL ELSE CAST(last_activity_date AS DATE) END AS last_activity_date
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L1|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L2|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L3|3000|3000|3000|3000|0/0|0|6000|126000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

### 重跑 history_key_frozen

SQL：`data/014_work/impl-004/history_key_frozen.sql`；SHA-256：`0d951fc84ed83b871b0dd17e0ae6b1357b9bb9820c779f394edc69b840653dff`。

唯一原文位置offset=1557，替换前：
```sql
CAST(hash("_fivetran_start", "_fivetran_end") AS VARCHAR)
```
替换后：
```sql
concat(id, '_', '2025-10-24 15:03:11.630125+08')
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|0|0|0/0|1|1|1|False|
|L1|3000|3000|0|0|0/0|1|1|1|False|
|L2|3000|3000|0|0|0/0|1|1|1|False|
|L3|3000|3000|0|0|0/0|1|1|1|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|1|1|1|1|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

### 重跑 activity_rule_gold_day

SQL：`data/014_work/impl-004/activity_rule_gold_day.sql`；SHA-256：`0a2c1cd7fc44c602a450c5c89a9686f60873068d174a6e6d0c04f057faa58aac`。

唯一原文位置offset=413，替换前：
```sql
CAST("last_activity_date" AS DATE) AS last_activity_date
```
替换后：
```sql
CASE WHEN last_activity_date > DATE '2025-10-24' OR last_activity_date < DATE '2020-01-01' THEN NULL ELSE CAST(last_activity_date AS DATE) END AS last_activity_date
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L1|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L2|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L3|3000|3000|3000|3000|0/0|0|6000|126000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

### 复用gold SQL同输入诊断

用于诊断，不是单点修复证据。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L1|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L2|3000|3000|3000|3000|0/0|0|6000|126000|False|
|L3|3000|3000|3000|3000|0/0|0|6000|126000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|contact_description|0|0|0|0|
|contact_name|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|is_deleted|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_modified_date|0|0|0|0|
|last_name|0|0|0|0|
|lead_source|0|0|0|0|
|mailing_city|0|0|0|0|
|mailing_country|0|0|0|0|
|mailing_postal_code|0|0|0|0|
|mailing_state|0|0|0|0|
|mailing_street|0|0|0|0|
|mobile_phone|0|0|0|0|
|owner_id|0|0|0|0|
|phone|0|0|0|0|
|title|0|0|0|0|

## 5. 逐项类别及U门槛

表级主要原因：**A**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|history_key_frozen|A|6000→1|126000→1|无|

重跑是否满足U第4条件：**是（固定gold时刻的key干预减少超过一半；仅诊断，不支持U）**。

hash方案与concat方案是未规定的标识约定；没有可以仅凭agent可见数据证明错误的数据命题P。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：是：主要A不变；移除未通过单独规模下降条件的O参与因素。。此字段不代替本次与016/017的对比。

## 规则问题

旧history_key_frozen与activity_rule_gold_day均使用2025-10-24同一日期；基线本身不引用运行时间。018仅复用这两个固定条件单项，实时history_key/activity_rule仅保留旧诊断，不参与主因选择。固定key原时刻是匹配gold未规定身份约定的诊断，不构造U。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
