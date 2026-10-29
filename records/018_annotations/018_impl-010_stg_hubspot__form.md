# impl-010 / stg_hubspot__form（v2定稿）

## 1. 差异描述与判定

agent与gold使用不同form_data：前者1150个FORM_ ID，后者1150行/1142个数值ID，全部原始行不相同。

已核实：依赖raw.form_data的agent留存与初始库一致，而gold不同。014完整行多重集合诊断与015三方核对相互印证：agent有1150个FORM_ ID；gold原表1150行、1142个数值ID，输出去重1142行。双方raw原始行不相交，gold SQL在agent输入上也不能重现gold输出。符合补充规则第一种情况，退出类别归因；旧去重/日期重跑仅保留诊断。

主要原因：**不可评估**；把握：**高**。
参与因素：无（输入差异遮蔽局部实现影响）。标记：无。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-010_stg_hubspot__form.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-010_staging_stg_hubspot__form.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml` 第462–497行。
- [原始轨迹转录](../014_trace_impl-010.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-010.json)；[015三方raw核对](../015_raw_impl-010.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_hubspot__form
      description: "HubSpot form definitions and submission tracking"
      source_table: raw.form_data
      columns:
        - name: form_id
          data_type: VARCHAR
          constraints: [unique]
        - name: portal_id
          data_type: BIGINT
        - name: form_name
          data_type: VARCHAR
        - name: form_type
          data_type: VARCHAR
        - name: form_method
          data_type: VARCHAR
        - name: form_action
          data_type: VARCHAR
        - name: form_css_class
          data_type: VARCHAR
        - name: form_submit_text
          data_type: VARCHAR
        - name: form_redirect
          data_type: VARCHAR
        - name: lead_nurturing_campaign_id
          data_type: VARCHAR
        - name: follow_up_id
          data_type: VARCHAR
        - name: notify_recipients
          data_type: VARCHAR
        - name: created_timestamp
          data_type: TIMESTAMP
        - name: updated_timestamp
          data_type: TIMESTAMP
        - name: _fivetran_synced
          data_type: TIMESTAMP WITH TIME ZONE
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/staging/stg_hubspot__form.sql`
```sql
   1: select
   2:     guid as form_id,
   3:     portal_id::bigint as portal_id,
   4:     name as form_name,
   5:     form_type,
   6:     method as form_method,
   7:     action as form_action,
   8:     css_class as form_css_class,
   9:     submit_text as form_submit_text,
  10:     redirect as form_redirect,
  11:     lead_nurturing_campaign_id,
  12:     follow_up_id,
  13:     notify_recipients,
  14:     try_strptime(substr(created_at, 1, 19), '%Y-%m-%d %H:%M:%S') as created_timestamp,
  15:     try_strptime(substr(updated_at, 1, 19), '%Y-%m-%d %H:%M:%S') as updated_timestamp,
  16:     cast(null as timestamptz) as _fivetran_synced
  17: from raw.form_data
  18: where guid is not null
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/sql/staging/stg_hubspot__form.sql`
```sql
   1: -- Form staging table
   2: -- Standardizes form data from the raw form table
   3: 
   4: with validated_data as (
   5:     select
   6:         -- Primary identifiers
   7:         cast(guid as varchar) as form_id,
   8:         cast(portal_id as bigint) as portal_id,
   9: 
  10:         -- Form details
  11:         name as form_name,
  12:         form_type as form_type,
  13:         method as form_method,
  14:         action as form_action,
  15:         css_class as form_css_class,
  16:         submit_text as form_submit_text,
  17:         redirect as form_redirect,
  18: 
  19:         -- Campaign information
  20:         cast(lead_nurturing_campaign_id as varchar) as lead_nurturing_campaign_id,
  21:         cast(follow_up_id as varchar) as follow_up_id,
  22: 
  23:         -- Settings
  24:         notify_recipients as notify_recipients,
  25: 
  26:         -- Timestamps
  27:         created_at as created_timestamp_raw,
  28:         updated_at as updated_timestamp_raw,
  29: 
  30:         -- Add row number for deduplication - keep most recent record per form_id
  31:         row_number() over (
  32:             partition by cast(guid as varchar)
  33:             order by updated_at desc nulls last, created_at desc nulls last
  34:         ) as rn
  35: 
  36:     from raw.form_data
  37: ),
  38: 
  39: validated_timestamps as (
  40:     select
  41:         *,
  42:         CASE
  43:             WHEN created_timestamp_raw IS NOT NULL
  44:                  AND CAST(created_timestamp_raw AS VARCHAR) ~ '^\d{4}-\d{2}-\d{2}'
  45:             THEN CAST(created_timestamp_raw AS TIMESTAMP)
  46:             ELSE NULL
  47:         END as created_timestamp,
  48:         CASE
  49:             WHEN updated_timestamp_raw IS NOT NULL
  50:                  AND CAST(updated_timestamp_raw AS VARCHAR) ~ '^\d{4}-\d{2}-\d{2}'
  51:             THEN CAST(updated_timestamp_raw AS TIMESTAMP)
  52:             ELSE NULL
  53:         END as updated_timestamp
  54:     from validated_data
  55:     where rn = 1
  56: )
  57: 
  58: select
  59:     form_id,
  60:     portal_id,
  61:     form_name,
  62:     form_type,
  63:     form_method,
  64:     form_action,
  65:     form_css_class,
  66:     form_submit_text,
  67:     form_redirect,
  68:     lead_nurturing_campaign_id,
  69:     follow_up_id,
  70:     notify_recipients,
  71:     created_timestamp,
  72:     updated_timestamp,
  73:     current_timestamp::timestamp with time zone as _fivetran_synced
  74: from validated_timestamps
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.form_data|gold_vs_initial|False|True|False|ordered_columns_or_types_differ,sorted_content_hash_differ|
|raw.form_data|gold_vs_agent|False|True|False|ordered_columns_or_types_differ,sorted_content_hash_differ|

补充诊断与原始事件见[016_raw_diagnostics.json](../016_raw_diagnostics.json)。

## 3. agent实际看到的信息与不确定性四档

event 13→14看到form_data schema；event 17按guid编写SQL；event 39复制start raw、event41修复run.py导入连接逻辑。event51查看其他表时间样例，event53批量改时间解析。现有证据未显示agent生成FORM_数据；初始/agent完整行一致是更直接证据。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|raw_input_mismatch|不可评估|看到了但没提|14|

### raw_input_mismatch：看到了但没提

可见form_data的schema；没有关于本表原始输入与初始/gold不一致的说明。不可评估仍填写四档，不要求agent能看到gold。

事件 **14**，字段`content`；[轨迹原文](../014_trace_impl-010.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/14.json`。
```text
pe:VARCHAR, task_type:VARCHAR, property_hs_engagement_source:VARCHAR

form_data: guid:VARCHAR, portal_id:INTEGER, name:VARCHAR, form_type:VARCHAR, method:VARCHAR, action:VARCHAR, redirect:VARCHAR, lead_nurturing_campaign_id:VARCHAR, follow_up_id:VARCHAR, created_at:VARCHAR, updated_at:VARCHAR, css_class:VARCHAR, notify_recipients:VARCHAR, submit_text:VARCHAR

merged_deal_data: deal_id:BIGINT, merged_deal_id:BIGINT

owner_data: owner_id:BIGINT, created_at:VARCHAR, portal_id:BIGINT, type:VARCHAR, updated_at:VARCHAR, email:VARCHAR, first_name:VARCHAR, last_name:VARCHAR, active_user_id:BIGINT

owner_team_data: owner_id:VARCHAR, team_id:BIGINT, is_team_primary:VARCHAR

property_data: calculated:VARCHAR, created_at:VARCHAR, description:VARCHAR, field_type:VARCHAR, group_name:VARCHAR, hubspot_defined:VARCHAR, hubspot_object:VARCHAR, label:VARCHAR, name:VARCHAR, show_currency_symbol:VARCHAR, type:VARCHAR, updated_a
```

已检视75个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：一条查询。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-010.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **1条**（含014复用；本轮新增0条）；核实代价档：**一条查询**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 014-V1 / 核实查询

来源：`records/014_queries_impl-010.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/hubspot.duckdb`。

```sql
SELECT count(*) n,count(distinct guid) guids,count(*) FILTER(WHERE guid LIKE 'FORM_%') synthetic_style_ids,min(guid) min_guid,max(guid) max_guid,count(distinct portal_id) portals FROM raw.form_data
```
结果原文：
```json
{
  "columns": [
    "n",
    "guids",
    "synthetic_style_ids",
    "min_guid",
    "max_guid",
    "portals"
  ],
  "rows": [
    [
      1150,
      1150,
      1150,
      "FORM_00000000",
      "FORM_00001149",
      1
    ]
  ]
}
```

### 014-D1 / 诊断查询

来源：`records/014_queries_impl-010.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`。

```sql
SELECT count(*) n,count(distinct guid) guids,count(*) FILTER(WHERE guid LIKE 'FORM_%') synthetic_style_ids,min(guid) min_guid,max(guid) max_guid,count(distinct portal_id) portals FROM raw.form_data
```
结果原文：
```json
{
  "error": "Binder Error: No function matches the given name and argument types '~~(BIGINT, STRING_LITERAL)'. You might need to add explicit type casts.\n\tCandidate functions:\n\t~~(VARCHAR, VARCHAR) -> BOOLEAN\n\n\nLINE 1: ...(*) n,count(distinct guid) guids,count(*) FILTER(WHERE guid LIKE 'FORM_%') synthetic_style_ids,min(guid) min_guid,max...\n                                                                       ^"
}
```

### 014-D_raw / 诊断查询

来源：`records/014_queries_impl-010.json`；数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/hubspot.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb']`。

```sql
SELECT * FROM raw.form_data
```
结果原文：
```json
{
  "result": {
    "columns_identical": false,
    "agent_columns": [
      "guid",
      "portal_id",
      "name",
      "form_type",
      "method",
      "action",
      "redirect",
      "lead_nurturing_campaign_id",
      "follow_up_id",
      "created_at",
      "updated_at",
      "css_class",
      "notify_recipients",
      "submit_text"
    ],
    "gold_columns": [
      "guid",
      "action",
      "created_at",
      "css_class",
      "follow_up_id",
      "form_type",
      "lead_nurturing_campaign_id",
      "method",
      "name",
      "notify_recipients",
      "portal_id",
      "redirect",
      "submit_text",
      "updated_at"
    ],
    "agent_rows": 1150,
    "gold_rows": 1150
  },
  "operation": "Python Counter of full typed rows, exact multiset difference"
}
```

### 014-D2 / 诊断查询

来源：`records/014_queries_impl-010.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`。

```sql
SELECT count(*) n,count(distinct guid) guids,min(cast(guid as varchar)) min_guid,max(cast(guid as varchar)) max_guid FROM raw.form_data
```
结果原文：
```json
{
  "columns": [
    "n",
    "guids",
    "min_guid",
    "max_guid"
  ],
  "rows": [
    [
      1150,
      1142,
      "10012",
      "99908"
    ]
  ]
}
```

### 014-D_ids / 诊断查询

来源：`records/014_queries_impl-010.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`。

```sql
SELECT count(*) n,count(distinct guid) guids,count(*) FILTER(WHERE CAST(guid AS VARCHAR) LIKE 'FORM_%') form_ids,min(CAST(guid AS VARCHAR)),max(CAST(guid AS VARCHAR)) FROM raw.form_data
```
结果原文：
```json
{
  "columns": [
    "n",
    "guids",
    "form_ids",
    "min(CAST(guid AS VARCHAR))",
    "max(CAST(guid AS VARCHAR))"
  ],
  "rows": [
    [
      1150,
      1142,
      0,
      "10012",
      "99908"
    ]
  ]
}
```

### 014-D_ids / 诊断查询

来源：`records/014_queries_impl-010.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`。

```sql
SELECT count(*) n,count(distinct guid) guids,count(*) FILTER(WHERE CAST(guid AS VARCHAR) LIKE 'FORM_%') form_ids,min(CAST(guid AS VARCHAR)),max(CAST(guid AS VARCHAR)) FROM raw.form_data
```
结果原文：
```json
{
  "columns": [
    "n",
    "guids",
    "form_ids",
    "min(CAST(guid AS VARCHAR))",
    "max(CAST(guid AS VARCHAR))"
  ],
  "rows": [
    [
      1150,
      1142,
      0,
      "10012",
      "99908"
    ]
  ]
}
```

### 014-D_input_alignment / 诊断查询

来源：`records/014_queries_impl-010.json`；数据库：`['/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/hubspot_start.duckdb', '/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/hubspot.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb']`。

```sql
SELECT "action","created_at","css_class","follow_up_id","form_type","guid","lead_nurturing_campaign_id","method","name","notify_recipients","portal_id","redirect","submit_text","updated_at" FROM raw.form_data
```
结果原文：
```json
{
  "schema_query": "DESCRIBE raw.form_data",
  "operation": "sort column names, compare full typed row Counters; data not saved",
  "result": {
    "initial_agent_equal": true,
    "agent_gold_equal": false,
    "agent_only": 1150,
    "gold_only": 1150
  }
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['form_id']`；比较列（与键取并集）：`['created_timestamp', 'follow_up_id', 'form_action', 'form_css_class', 'form_id', 'form_method', 'form_name', 'form_redirect', 'form_submit_text', 'form_type', 'lead_nurturing_campaign_id', 'notify_recipients', 'portal_id']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：records/014_reruns_impl-010.json

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|deduplicate|2292→2292|29796→29796|无|
|created_rule|2292→2292|29796→29796|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L1|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L2|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L3|1150|1142|1150|1142|0/0|0|2292|29796|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|created_timestamp|0|0|0|0|
|follow_up_id|0|0|0|0|
|form_action|0|0|0|0|
|form_css_class|0|0|0|0|
|form_id|0|0|0|0|
|form_method|0|0|0|0|
|form_name|0|0|0|0|
|form_redirect|0|0|0|0|
|form_submit_text|0|0|0|0|
|form_type|0|0|0|0|
|lead_nurturing_campaign_id|0|0|0|0|
|notify_recipients|0|0|0|0|
|portal_id|0|0|0|0|

### 重跑 baseline

SQL：`data/014_work/impl-010/baseline.sql`；SHA-256：`e8b8a30f71c9de0ced2fecced62afa535753290ae59556934cc23c4ea9055903`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L1|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L2|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L3|1150|1142|1150|1142|0/0|0|2292|29796|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|created_timestamp|0|0|0|0|
|follow_up_id|0|0|0|0|
|form_action|0|0|0|0|
|form_css_class|0|0|0|0|
|form_id|0|0|0|0|
|form_method|0|0|0|0|
|form_name|0|0|0|0|
|form_redirect|0|0|0|0|
|form_submit_text|0|0|0|0|
|form_type|0|0|0|0|
|lead_nurturing_campaign_id|0|0|0|0|
|notify_recipients|0|0|0|0|
|portal_id|0|0|0|0|

### 重跑 deduplicate

SQL：`data/014_work/impl-010/deduplicate.sql`；SHA-256：`1ce241f2240b0ddbf0a14db616aeac9e5b78372e09f5da6a819b45f83458ed47`。

唯一原文位置offset=573，替换前：
```sql
where guid is not null
```
替换后：
```sql
where guid is not null
QUALIFY row_number() over(partition by guid order by updated_at desc nulls last,created_at desc nulls last)=1
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L1|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L2|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L3|1150|1142|1150|1142|0/0|0|2292|29796|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|created_timestamp|0|0|0|0|
|follow_up_id|0|0|0|0|
|form_action|0|0|0|0|
|form_css_class|0|0|0|0|
|form_id|0|0|0|0|
|form_method|0|0|0|0|
|form_name|0|0|0|0|
|form_redirect|0|0|0|0|
|form_submit_text|0|0|0|0|
|form_type|0|0|0|0|
|lead_nurturing_campaign_id|0|0|0|0|
|notify_recipients|0|0|0|0|
|portal_id|0|0|0|0|

### 重跑 created_rule

SQL：`data/014_work/impl-010/created_rule.sql`；SHA-256：`65f7c9384ad1b1df94850744e924a3278280b8e99931132721df7b0249bbe192`。

唯一原文位置offset=334，替换前：
```sql
try_strptime(substr(created_at, 1, 19), '%Y-%m-%d %H:%M:%S')
```
替换后：
```sql
CASE WHEN created_at IS NOT NULL AND CAST(created_at AS VARCHAR) ~ '^\d{4}-\d{2}-\d{2}' THEN CAST(created_at AS TIMESTAMP) ELSE NULL END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L1|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L2|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L3|1150|1142|1150|1142|0/0|0|2292|29796|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|created_timestamp|0|0|0|0|
|follow_up_id|0|0|0|0|
|form_action|0|0|0|0|
|form_css_class|0|0|0|0|
|form_id|0|0|0|0|
|form_method|0|0|0|0|
|form_name|0|0|0|0|
|form_redirect|0|0|0|0|
|form_submit_text|0|0|0|0|
|form_type|0|0|0|0|
|lead_nurturing_campaign_id|0|0|0|0|
|notify_recipients|0|0|0|0|
|portal_id|0|0|0|0|

### 复用gold SQL同输入诊断

用于诊断，不是单点修复证据。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L1|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L2|1150|1142|1150|1142|0/0|0|2292|29796|False|
|L3|1150|1142|1150|1142|0/0|0|2292|29796|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|created_timestamp|0|0|0|0|
|follow_up_id|0|0|0|0|
|form_action|0|0|0|0|
|form_css_class|0|0|0|0|
|form_id|0|0|0|0|
|form_method|0|0|0|0|
|form_name|0|0|0|0|
|form_redirect|0|0|0|0|
|form_submit_text|0|0|0|0|
|form_type|0|0|0|0|
|lead_nurturing_campaign_id|0|0|0|0|
|notify_recipients|0|0|0|0|
|portal_id|0|0|0|0|

## 5. 逐项类别及U门槛

表级主要原因：**不可评估**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|raw_input_mismatch|不可评估|不适用：见诊断|不适用：见诊断|不作为单侧U修复|

重跑是否满足U第4条件：**不适用：不可评估，旧单改仅作输入差异诊断**。

无可用U主命题。当前raw.guid实际唯一，不能用gold.raw中的重复guid去反证agent当时看到的数据；这样会违反核实查询边界。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：是：O改为不可评估，按v1和2026-10-29用户补充。。此字段不代替本次与016/017的对比。

## 规则问题

v2已将不可评估区分写入第3节。没有正常归因主项时，四档仍针对输入差异/源选择填写，不把不可评估当成第五档。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
