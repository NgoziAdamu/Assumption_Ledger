# impl-001 / stg_lever__application（v2定稿）

## 1. 差异描述与判定

agent 按契约删除解析后创建时间为空的全部5000行；gold保留这些行，去掉该筛选即完全匹配。

已核实：raw 的5000个 created_at 非空，但 TRY_CAST 后全部为空；agent 输出0行，gold输出5000行。agent SQL 第23行执行 created_at IS NOT NULL，契约明确要求 created_at not_null，gold SQL 明确写“do not drop rows because created_at is empty”。只删除这一项过滤，L0–L3均完全匹配。归因判断：主要是 gold 保留空创建时间与契约非空要求冲突，归 O；不是看到空表就判 D，也不能仅凭解析失败就判 U。

主要原因：**O**；把握：**高**。
参与因素：无。标记：无。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-001_stg_lever__application.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-001_staging_stg_lever__application.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml` 第390–428行。
- [原始轨迹转录](../014_trace_impl-001.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-001.json)；[015三方raw核对](../015_raw_impl-001.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_lever__application
      description: "Cleaned job applications linking candidates to postings with application status and metadata"
      source_table: "raw.application"
      columns:
        - name: application_id
          data_type: VARCHAR(50)
          constraints: [not_null, unique]
        - name: opportunity_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: posting_id
          data_type: VARCHAR(50)
        - name: type
          data_type: VARCHAR(50)
        - name: candidate_id
          data_type: BIGINT
        - name: posting_hiring_manager_user_id
          data_type: VARCHAR(50)
        - name: posting_owner_user_id
          data_type: VARCHAR(50)
        - name: company
          data_type: VARCHAR(255)
        - name: referrer_user_id
          data_type: VARCHAR(50)
        - name: requisition_id
          data_type: VARCHAR(50)
        - name: archived_at
          data_type: TIMESTAMP
          validation_rules:
            - rule: "archived_at IS NULL OR created_at IS NULL OR try_cast(archived_at as timestamp) >= try_cast(created_at as timestamp)"
              on_failure: delete_row
        - name: archived_reason_id
          data_type: VARCHAR(50)
        - name: comments
          data_type: VARCHAR(1000)
        - name: created_at
          data_type: TIMESTAMP
          constraints: [not_null]
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql`
```sql
   1: WITH typed AS (
   2:     SELECT
   3:         try_cast(r."id" AS VARCHAR(50)) AS application_id,
   4:         trim(cast(r."opportunity_id" AS VARCHAR)) AS opportunity_id,
   5:         trim(cast(r."posting_id" AS VARCHAR)) AS posting_id,
   6:         try_cast(r."type" AS VARCHAR(50)) AS type,
   7:         try_cast(r."candidate_id" AS BIGINT) AS candidate_id,
   8:         try_cast(r."posting_hiring_manager_id" AS VARCHAR(50)) AS posting_hiring_manager_user_id,
   9:         try_cast(r."posting_owner_id" AS VARCHAR(50)) AS posting_owner_user_id,
  10:         try_cast(r."company" AS VARCHAR(255)) AS company,
  11:         try_cast(r."referrer_id" AS VARCHAR(50)) AS referrer_user_id,
  12:         trim(cast(r."requisition_for_hire_id" AS VARCHAR)) AS requisition_id,
  13:         try_cast(r."archived_at" AS TIMESTAMP) AS archived_at,
  14:         try_cast(r."archived_reason_id" AS VARCHAR(50)) AS archived_reason_id,
  15:         try_cast(r."comments" AS VARCHAR(1000)) AS comments,
  16:         try_cast(r."created_at" AS TIMESTAMP) AS created_at
  17:     FROM raw.application AS r
  18: ),
  19: valid AS (
  20:     SELECT * FROM typed
  21:     WHERE         application_id IS NOT NULL AND
  22:               opportunity_id IS NOT NULL AND
  23:               created_at IS NOT NULL
  24: ),
  25: ranked AS (
  26:     SELECT *, row_number() OVER (PARTITION BY application_id ORDER BY application_id) AS _row_num
  27:     FROM valid
  28: )
  29: SELECT application_id, opportunity_id, posting_id, type, candidate_id, posting_hiring_manager_user_id, posting_owner_user_id, company, referrer_user_id, requisition_id, archived_at, archived_reason_id, comments, created_at
  30: FROM ranked
  31: WHERE _row_num = 1
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/staging/stg_lever__application.sql`
```sql
   1: -- Standardized cleaning of application information (aligned docs/staging_data_specification.yaml)
   2: 
   3: with cleaned as (
   4:     select
   5:         trim(id) as application_id,
   6:         opportunity_id,
   7:         posting_id,
   8:         type,
   9:         candidate_id,
  10:         posting_hiring_manager_id as posting_hiring_manager_user_id,
  11:         posting_owner_id as posting_owner_user_id,
  12:         trim(company) as company,
  13:         referrer_id as referrer_user_id,
  14:         requisition_for_hire_id as requisition_id,
  15:         try_cast(archived_at as timestamp) as archived_at,
  16:         archived_reason_id,
  17:         comments,
  18:         try_cast(created_at as timestamp) as created_at
  19:     from raw.application
  20: ), filtered as (
  21:     select * from cleaned
  22:     where
  23:         -- Delete a row: the primary key is not empty, the opportunity foreign key is not empty, and the creation time is not empty
  24:         length(application_id) > 0
  25:         and opportunity_id is not null
  26:         -- Relax time filtering: do not drop rows because created_at is empty, only compare when comparable
  27:         and (archived_at is null or created_at is null or archived_at >= created_at)
  28: )
  29: 
  30: select * from filtered
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.application|gold_vs_initial|True|True|True||
|raw.application|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event 1 含完整契约；event 17 用通用生成器把 not_null 转成筛选条件，并把时间统一 TRY_CAST。全69事件未找到 application 创建时间样例或解析成功率查询；event 28 只回显执行日志，不能证明看过源时间值。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|allow_null_created|O|只有通用策略说明|67|

### allow_null_created：只有通用策略说明

说明必需值失败过滤的一般策略，未指出application.created_at全部解析失败。

事件 **67**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-001.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`。
```text
转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。
```

已检视69个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：一条查询。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-001.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **1条**（含014复用；本轮新增0条）；核实代价档：**一条查询**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 014-V1 / 核实查询

来源：`records/014_queries_impl-001.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/lever.duckdb`。

```sql
SELECT count(*) n,count(created_at) raw_created_nonnull,count(try_cast(created_at AS TIMESTAMP)) parsed_created_nonnull,count(*) FILTER(WHERE try_cast(archived_at AS TIMESTAMP)<try_cast(created_at AS TIMESTAMP)) inverted,count(distinct id) ids FROM raw.application
```
结果原文：
```json
{
  "columns": [
    "n",
    "raw_created_nonnull",
    "parsed_created_nonnull",
    "inverted",
    "ids"
  ],
  "rows": [
    [
      5000,
      5000,
      0,
      0,
      5000
    ]
  ]
}
```

### 014-D1 / 诊断查询

来源：`records/014_queries_impl-001.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`。

```sql
SELECT count(*) n,count(created_at) raw_created_nonnull,count(try_cast(created_at AS TIMESTAMP)) parsed_created_nonnull,count(*) FILTER(WHERE try_cast(archived_at AS TIMESTAMP)<try_cast(created_at AS TIMESTAMP)) inverted,count(distinct id) ids FROM raw.application
```
结果原文：
```json
{
  "columns": [
    "n",
    "raw_created_nonnull",
    "parsed_created_nonnull",
    "inverted",
    "ids"
  ],
  "rows": [
    [
      5000,
      5000,
      0,
      0,
      5000
    ]
  ]
}
```

### 014-D_raw / 诊断查询

来源：`records/014_queries_impl-001.json`；数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/lever.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb']`。

```sql
SELECT * FROM raw.application
```
结果原文：
```json
{
  "result": {
    "columns_identical": true,
    "agent_rows": 5000,
    "gold_rows": 5000,
    "agent_only_rows": 0,
    "gold_only_rows": 0
  },
  "operation": "Python Counter of full typed rows, exact multiset difference"
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['application_id']`；比较列（与键取并集）：`['application_id', 'opportunity_id', 'posting_id', 'type', 'candidate_id', 'posting_hiring_manager_user_id', 'posting_owner_user_id', 'company', 'referrer_user_id', 'requisition_id', 'archived_at', 'archived_reason_id', 'comments', 'created_at']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：records/014_reruns_impl-001.json

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|allow_null_created|5000→0|70000→0|L0|
|archive_check|5000→5000|70000→70000|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|0|5000|0|5000|0/0|0|5000|70000|False|
|L1|0|5000|0|5000|0/0|0|5000|70000|False|
|L2|0|5000|0|5000|0/0|0|5000|70000|False|
|L3|0|5000|0|5000|0/0|0|5000|70000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|application_id|0|0|0|0|
|opportunity_id|0|0|0|0|
|posting_id|0|0|0|0|
|type|0|0|0|0|
|candidate_id|0|0|0|0|
|posting_hiring_manager_user_id|0|0|0|0|
|posting_owner_user_id|0|0|0|0|
|company|0|0|0|0|
|referrer_user_id|0|0|0|0|
|requisition_id|0|0|0|0|
|archived_at|0|0|0|0|
|archived_reason_id|0|0|0|0|
|comments|0|0|0|0|
|created_at|0|0|0|0|

### 重跑 baseline

SQL：`data/014_work/impl-001/baseline.sql`；SHA-256：`5ace39feb0cd0f84a617507f230df30324eefd27e14a9c51524ebdc672e88aba`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|0|5000|0|5000|0/0|0|5000|70000|False|
|L1|0|5000|0|5000|0/0|0|5000|70000|False|
|L2|0|5000|0|5000|0/0|0|5000|70000|False|
|L3|0|5000|0|5000|0/0|0|5000|70000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|application_id|0|0|0|0|
|opportunity_id|0|0|0|0|
|posting_id|0|0|0|0|
|type|0|0|0|0|
|candidate_id|0|0|0|0|
|posting_hiring_manager_user_id|0|0|0|0|
|posting_owner_user_id|0|0|0|0|
|company|0|0|0|0|
|referrer_user_id|0|0|0|0|
|requisition_id|0|0|0|0|
|archived_at|0|0|0|0|
|archived_reason_id|0|0|0|0|
|comments|0|0|0|0|
|created_at|0|0|0|0|

### 重跑 allow_null_created

SQL：`data/014_work/impl-001/allow_null_created.sql`；SHA-256：`ed05e6b30452665eb8f9a53ef7cc4fca0d84dfe921705f4cae1a921f205d6c62`。

唯一原文位置offset=1107，替换前：
```sql
opportunity_id IS NOT NULL AND
              created_at IS NOT NULL
```
替换后：
```sql
opportunity_id IS NOT NULL
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|5000|5000|0|0|0/0|0|0|0|True|
|L1|5000|5000|0|0|0/0|0|0|0|True|
|L2|5000|5000|0|0|0/0|0|0|0|True|
|L3|5000|5000|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|application_id|0|0|0|0|
|opportunity_id|0|0|0|0|
|posting_id|0|0|0|0|
|type|0|0|0|0|
|candidate_id|0|0|0|0|
|posting_hiring_manager_user_id|0|0|0|0|
|posting_owner_user_id|0|0|0|0|
|company|0|0|0|0|
|referrer_user_id|0|0|0|0|
|requisition_id|0|0|0|0|
|archived_at|0|0|0|0|
|archived_reason_id|0|0|0|0|
|comments|0|0|0|0|
|created_at|0|0|0|0|

### 重跑 archive_check

SQL：`data/014_work/impl-001/archive_check.sql`；SHA-256：`e5ac7731475336d6e555ebf87438fd2598541095e5297aa70731a81ecf323451`。

唯一原文位置offset=1540，替换前：
```sql
WHERE _row_num = 1
```
替换后：
```sql
WHERE _row_num = 1 AND (archived_at IS NULL OR created_at IS NULL OR archived_at >= created_at)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|0|5000|0|5000|0/0|0|5000|70000|False|
|L1|0|5000|0|5000|0/0|0|5000|70000|False|
|L2|0|5000|0|5000|0/0|0|5000|70000|False|
|L3|0|5000|0|5000|0/0|0|5000|70000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|application_id|0|0|0|0|
|opportunity_id|0|0|0|0|
|posting_id|0|0|0|0|
|type|0|0|0|0|
|candidate_id|0|0|0|0|
|posting_hiring_manager_user_id|0|0|0|0|
|posting_owner_user_id|0|0|0|0|
|company|0|0|0|0|
|referrer_user_id|0|0|0|0|
|requisition_id|0|0|0|0|
|archived_at|0|0|0|0|
|archived_reason_id|0|0|0|0|
|comments|0|0|0|0|
|created_at|0|0|0|0|

### 复用gold SQL同输入诊断

用于诊断，不是单点修复证据。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|5000|5000|0|0|0/0|0|0|0|True|
|L1|5000|5000|0|0|0/0|0|0|0|True|
|L2|5000|5000|0|0|0/0|0|0|0|True|
|L3|5000|5000|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|application_id|0|0|0|0|
|opportunity_id|0|0|0|0|
|posting_id|0|0|0|0|
|type|0|0|0|0|
|candidate_id|0|0|0|0|
|posting_hiring_manager_user_id|0|0|0|0|
|posting_owner_user_id|0|0|0|0|
|company|0|0|0|0|
|referrer_user_id|0|0|0|0|
|requisition_id|0|0|0|0|
|archived_at|0|0|0|0|
|archived_reason_id|0|0|0|0|
|comments|0|0|0|0|
|created_at|0|0|0|0|

## 5. 逐项类别及U门槛

表级主要原因：**O**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|allow_null_created|O|5000→0|70000→0|L0|

重跑是否满足U第4条件：**是（allow_null_created 完全匹配L0；不代表归U）**。

候选 P：raw.created_at 可以直接 TRY_CAST 为 TIMESTAMP。V1反证；但本次导致官方差异的是遵照契约执行非空过滤，删除过滤的干预也不是修复时间解析，故不把这个成功干预作为P的U证据。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：否：主要原因、参与因素不变。。此字段不代替本次与016/017的对比。

## 规则问题

O与U竞争：可以把时间解析失败解释为未核实格式；也可以按契约/gold冲突解释。选择O，因为匹配gold所需的最小改动恰好放宽契约，解析器没有改变。archived_at检查确实漏写，但单独补写差异不变，不列参与因素。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
