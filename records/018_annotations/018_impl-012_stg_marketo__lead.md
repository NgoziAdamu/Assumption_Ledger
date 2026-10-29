# impl-012 / stg_marketo__lead（v2定稿）

## 1. 差异描述与判定

agent按契约排除首尾带空白的姓名，gold只trim后保留；first/last两项各缺3行并列。

已核实：raw6000行且id无重复；first_name和last_name各3行不等于TRIM。契约可执行校验name=TRIM(name)、失败删行，agent照做。两边输出5984与5990行，差6行/36格；分别放宽一项空白校验后3行/18格，去重控制无效。gold保留并修整这些行与字面排除规则不一致，两个O原因并列。

主要原因：**O**；把握：**高**。
参与因素：无。标记：无。

与上一版（016）相比：原因类别：多因并列（O）→O。v2第5节要求同类并列直接记该类，独立项及数值均保留。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-012_stg_marketo__lead.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-012_staging_stg_marketo__lead.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml` 第36–81行。
- [原始轨迹转录](../016_trace_impl-012.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-012.json)；[015三方raw核对](../015_raw_impl-012.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_marketo__lead
      description: "Cleaned and standardized lead (contact) records from Marketo with basic contact information and timestamps"
      source_table: "raw.marketo_lead"
      grain: "One row per unique lead in Marketo"
      columns:
        - name: lead_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: created_timestamp
          data_type: VARCHAR
          constraints: [not_null]
        - name: updated_timestamp
          data_type: VARCHAR
          constraints: [not_null]
        - name: email
          data_type: VARCHAR
          constraints: [not_null]
          description: "Email address of the lead"
          validation_rules:
            - rule: "email = LOWER(TRIM(email))"
              description: "Normalize email to lowercase and remove whitespace"
              on_failure: delete_row
            - rule: "email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'"
              description: "Email must follow valid email format"
              on_failure: delete_row
        - name: first_name
          data_type: VARCHAR
          description: "First name of the lead"
          validation_rules:
            - rule: "first_name = TRIM(first_name)"
              description: "Remove leading and trailing whitespace"
              on_failure: delete_row
            - rule: "LENGTH(first_name) <= 100"
              description: "First name cannot exceed 100 characters"
              on_failure: delete_row
        - name: last_name
          data_type: VARCHAR
          description: "Last name of the lead"
          validation_rules:
            - rule: "last_name = TRIM(last_name)"
              description: "Remove leading and trailing whitespace"
              on_failure: delete_row
            - rule: "LENGTH(last_name) <= 100"
              description: "Last name cannot exceed 100 characters"
              on_failure: delete_row
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/staging/stg_marketo__lead.sql`
```sql
   1: SELECT
   2:     CAST(id AS VARCHAR) AS lead_id,
   3:     CAST(created_at AS VARCHAR) AS created_timestamp,
   4:     CAST(updated_at AS VARCHAR) AS updated_timestamp,
   5:     LOWER(TRIM(email)) AS email,
   6:     TRIM(first_name) AS first_name,
   7:     TRIM(last_name) AS last_name
   8: FROM raw.marketo_lead
   9: WHERE id IS NOT NULL AND created_at IS NOT NULL AND updated_at IS NOT NULL AND email IS NOT NULL AND LOWER(TRIM(email)) ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' AND (first_name IS NULL OR (first_name = TRIM(first_name) AND LENGTH(first_name) <= 100)) AND (last_name IS NULL OR (last_name = TRIM(last_name) AND LENGTH(last_name) <= 100))
  10: QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC NULLS LAST) = 1
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/sql/staging/stg_marketo__lead.sql`
```sql
   1: -- Staging: Lead data with standardized columns and data quality transformations
   2: -- Transform raw Marketo data into clean staging table with standardized naming, data types, and quality constraints
   3: SELECT
   4:     CAST(id AS VARCHAR) as lead_id,
   5:     CAST(created_at AS VARCHAR) as created_timestamp,
   6:     CAST(updated_at AS VARCHAR) as updated_timestamp,
   7:     CASE
   8:         WHEN LOWER(TRIM(email)) !~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' THEN NULL
   9:         WHEN email IS NULL THEN NULL
  10:         ELSE LOWER(TRIM(email))
  11:     END as email,
  12:     CASE
  13:         WHEN LENGTH(TRIM(first_name)) > 100 THEN NULL
  14:         WHEN first_name IS NULL THEN NULL
  15:         ELSE TRIM(first_name)
  16:     END as first_name,
  17:     CASE
  18:         WHEN LENGTH(TRIM(last_name)) > 100 THEN NULL
  19:         WHEN last_name IS NULL THEN NULL
  20:         ELSE TRIM(last_name)
  21:     END as last_name
  22: FROM raw.marketo_lead
  23: WHERE id IS NOT NULL
  24:     AND created_at IS NOT NULL
  25:     AND updated_at IS NOT NULL
  26:     AND LOWER(TRIM(email)) ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
  27:     AND TRIM(email) IS NOT NULL
  28:     AND LENGTH(TRIM(first_name)) <= 100
  29:     AND LENGTH(TRIM(last_name)) <= 100
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.marketo_lead|gold_vs_initial|True|True|True||
|raw.marketo_lead|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event1含契约；event23落实first/last name字面校验；event43修复NULL条件；event45运行校验。没有把可能的“先trim再校验”推测当契约本意。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|first_name_trim_policy|O|看到了但没提|1|
|last_name_trim_policy|O|看到了但没提|1|

### first_name_trim_policy：看到了但没提

看到了first/last_name的可执行trim相等校验。报告的缺关键ID/时间/必需属性过滤没有说明首尾空白是先trim还是按原值删行；一般“按契约清理”不当作相关策略说明。

事件 **1**，字段`args.content`；[轨迹原文](../016_trace_impl-012.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json`。
```text
st name of the lead"
          validation_rules:
            - rule: "first_name = TRIM(first_name)"
              description: "Remove leading and trailing whitespace"
              on_failure: delete_row
            - rule: "LENGTH(first_name) <= 100"
              description: "First name cannot exceed 100 characters"
              on_failure: delete_row
        - name: last_name
          data_type: VARCHAR
          description: "Last name of the lead"
          validation_rules:
            - rule: "last_name = TRIM(last_name)"
              description: "Remove leading and trailing whitespace"
              on_failure: delete_row
            - rule: "LENGTH(last_name) <= 100"
              description: "Last name cannot exceed 100 characters"
              on_failure: delete_row

    - name: stg_marketo__campaigns
      description: "Cleaned campaign records with standardized attributes and campaign 
```

### last_name_trim_policy：看到了但没提

看到了first/last_name的可执行trim相等校验。报告的缺关键ID/时间/必需属性过滤没有说明首尾空白是先trim还是按原值删行；一般“按契约清理”不当作相关策略说明。

事件 **1**，字段`args.content`；[轨迹原文](../016_trace_impl-012.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json`。
```text
st name of the lead"
          validation_rules:
            - rule: "last_name = TRIM(last_name)"
              description: "Remove leading and trailing whitespace"
              on_failure: delete_row
            - rule: "LENGTH(last_name) <= 100"
              description: "Last name cannot exceed 100 characters"
              on_failure: delete_row

    - name: stg_marketo__campaigns
      description: "Cleaned campaign records with standardized attributes and campaign configuration details"
      source_table: "raw.marketo_campaign"
      grain: "One row per unique campaign in Marketo"
      columns:
        - name: campaign_id
          data_type: VARCHAR
          constraints: [not_null, unique]
          validation_rules:
            - rule: "campaign_id IS NOT NULL"
              on_failure: delete_row
        - name: campaign_name
          data_type: VARCHAR
          constraints: [not_null]
   
```

已检视57个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：一条查询。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-012.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **1条**（含014复用；本轮新增1条）；核实代价档：**一条查询**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 016-V1 / 核实查询

来源：`records/016_queries_impl-012.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE first_name IS DISTINCT FROM trim(first_name)) first_whitespace,count(*) FILTER(WHERE last_name IS DISTINCT FROM trim(last_name)) last_whitespace,count(*)-count(distinct id) duplicate_excess FROM raw.marketo_lead
```
结果原文：
```json
{
  "columns": [
    "n",
    "first_whitespace",
    "last_whitespace",
    "duplicate_excess"
  ],
  "rows": [
    [
      6000,
      3,
      3,
      0
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['lead_id']`；比较列（与键取并集）：`['created_timestamp', 'email', 'first_name', 'last_name', 'lead_id', 'updated_timestamp']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：本次重新执行；原013留存输出另列

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|first_name_trim_policy|6→3|36→18|无|
|last_name_trim_policy|6→3|36→18|无|
|no_dedupe|6→6|36→36|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|5984|5990|0|6|0/0|0|6|36|False|
|L1|5984|5990|0|6|0/0|0|6|36|False|
|L2|5984|5990|0|6|0/0|0|6|36|False|
|L3|5984|5990|0|6|0/0|0|6|36|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|lead_id|0|0|0|0|
|created_timestamp|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|last_name|0|0|0|0|
|updated_timestamp|0|0|0|0|

### 重跑 baseline

SQL：`data/016_work/impl-012/baseline.sql`；SHA-256：`514ec47be037bc14a9b91f1cb31839081629db332666e92b1f107bfe960a92ac`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|5984|5990|0|6|0/0|0|6|36|False|
|L1|5984|5990|0|6|0/0|0|6|36|False|
|L2|5984|5990|0|6|0/0|0|6|36|False|
|L3|5984|5990|0|6|0/0|0|6|36|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|lead_id|0|0|0|0|
|created_timestamp|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|last_name|0|0|0|0|
|updated_timestamp|0|0|0|0|

### 重跑 first_name_trim_policy

SQL：`data/016_work/impl-012/first_name_trim_policy.sql`；SHA-256：`1e8d00a61cdd2e986c76a6da3245efc9e4b763866aabd4ab13ebb552e2e98405`。

唯一原文位置offset=452，替换前：
```sql
(first_name IS NULL OR (first_name = TRIM(first_name) AND LENGTH(first_name) <= 100))
```
替换后：
```sql
LENGTH(TRIM(first_name)) <= 100
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|5987|5990|0|3|0/0|0|3|18|False|
|L1|5987|5990|0|3|0/0|0|3|18|False|
|L2|5987|5990|0|3|0/0|0|3|18|False|
|L3|5987|5990|0|3|0/0|0|3|18|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|lead_id|0|0|0|0|
|created_timestamp|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|last_name|0|0|0|0|
|updated_timestamp|0|0|0|0|

### 重跑 last_name_trim_policy

SQL：`data/016_work/impl-012/last_name_trim_policy.sql`；SHA-256：`d9d94d77bbedb21c15c7be855494b24e168bc864a6d3f751add15f576620839e`。

唯一原文位置offset=542，替换前：
```sql
(last_name IS NULL OR (last_name = TRIM(last_name) AND LENGTH(last_name) <= 100))
```
替换后：
```sql
LENGTH(TRIM(last_name)) <= 100
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|5987|5990|0|3|0/0|0|3|18|False|
|L1|5987|5990|0|3|0/0|0|3|18|False|
|L2|5987|5990|0|3|0/0|0|3|18|False|
|L3|5987|5990|0|3|0/0|0|3|18|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|lead_id|0|0|0|0|
|created_timestamp|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|last_name|0|0|0|0|
|updated_timestamp|0|0|0|0|

### 重跑 no_dedupe

SQL：`data/016_work/impl-012/no_dedupe.sql`；SHA-256：`c4f2bcb599f4766662ce1628dfa4c1a6e707942438bde2b67b9c619110f3d95e`。

唯一原文位置offset=624，替换前：
```sql
QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC NULLS LAST) = 1
```
替换后：
```sql

```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|5984|5990|0|6|0/0|0|6|36|False|
|L1|5984|5990|0|6|0/0|0|6|36|False|
|L2|5984|5990|0|6|0/0|0|6|36|False|
|L3|5984|5990|0|6|0/0|0|6|36|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|lead_id|0|0|0|0|
|created_timestamp|0|0|0|0|
|email|0|0|0|0|
|first_name|0|0|0|0|
|last_name|0|0|0|0|
|updated_timestamp|0|0|0|0|

## 5. 逐项类别及U门槛

表级主要原因：**O**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|first_name_trim_policy|O|6→3|36→18|无|
|last_name_trim_policy|O|6→3|36→18|无|

重跑是否满足U第4条件：**是（每项6→3行；这不是U）**。

无U主命题。来源数据是否有空白不是导致错误的未经核实假设：agent已按规则处理。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别：多因并列（O）→O。v2第5节要求同类并列直接记该类，独立项及数值均保留。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：不适用：第二批首次标注。此字段不代替本次与016/017的对比。

## 规则问题

v2第5节规定所有并列项同类直接记该类，因此表级由多因并列（O）变O；first/last两项仍各列O及独立四档。报告提到必需属性过滤，但没有说明本处原字符串空白与trim处理，保守记看到了但没提。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
