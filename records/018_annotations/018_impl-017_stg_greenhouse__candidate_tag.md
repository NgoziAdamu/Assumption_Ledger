# impl-017 / stg_greenhouse__candidate_tag（v2定稿）

## 1. 差异描述与判定

agent按复合主键去掉一个重复candidate-tag行，gold保留重复，造成1行2格差异。

已核实：raw中(candidate_id=4420,tag_id=114)出现2次，其余不重复；契约primary_key=[candidate_id,tag_id]。agent ROW_NUMBER去重得到1999行，gold保留2000行。仅取消_row_num=1即L0整表一致。主键声明与gold重复行冲突，归O，不因保留重复能匹配gold反判agent未遵约。

主要原因：**O**；把握：**高**。
参与因素：无。标记：无。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-017_stg_greenhouse__candidate_tag.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-017_staging_stg_greenhouse__candidate_tag.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml` 第504–515行。
- [原始轨迹转录](../016_trace_impl-017.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-017.json)；[015三方raw核对](../015_raw_impl-017.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_greenhouse__candidate_tag
      description: "Cleaned candidate tag associations"
      source_table: "raw.candidate_tag"
      primary_key: ["candidate_id", "tag_id"]
      columns:
        - name: candidate_id
          data_type: BIGINT
          constraints: [not_null]
        - name: tag_id
          data_type: BIGINT
          constraints: [not_null]
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/staging/stg_greenhouse__candidate_tag.sql`
```sql
   1: WITH source_rows AS (
   2:     SELECT
   3:         TRY_CAST(candidate_id AS BIGINT) AS "candidate_id",
   4:         TRY_CAST(tag_id AS BIGINT) AS "tag_id",
   5:         ROW_NUMBER() OVER (PARTITION BY "candidate_id", "tag_id" ORDER BY "candidate_id", "tag_id") AS _row_num
   6:     FROM raw.candidate_tag
   7: ),
   8: validated_rows AS (
   9:     SELECT *
  10:     FROM source_rows
  11:     WHERE "candidate_id" IS NOT NULL AND "tag_id" IS NOT NULL AND "candidate_id" IS NOT NULL AND "tag_id" IS NOT NULL
  12: )
  13: SELECT "candidate_id", "tag_id"
  14: FROM validated_rows
  15: WHERE _row_num = 1
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/sql/staging/stg_greenhouse__candidate_tag.sql`
```sql
   1: -- Purpose: Standardize candidate_tag data with validation
   2: -- Source: raw.candidate_tag
   3: -- Target: staging.stg_greenhouse__candidate_tag
   4: 
   5: with source as (
   6:     select * from raw.candidate_tag
   7: ),
   8: 
   9: renamed as (
  10:     select
  11:         cast(candidate_id as bigint) as candidate_id,
  12:         cast(tag_id as bigint) as tag_id
  13: 
  14:     from source
  15: ),
  16: 
  17: validated as (
  18:     select
  19:         candidate_id,
  20:         tag_id
  21: 
  22:     from renamed
  23: 
  24:     where
  25:         -- Ensure composite primary key fields are not null
  26:         candidate_id is not null
  27:         and tag_id is not null
  28: )
  29: 
  30: select * from validated
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.candidate_tag|gold_vs_initial|True|True|True||
|raw.candidate_tag|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event1给出复合主键；event17生成窗口去重，后续运行成功。无需假定agent看过该重复值才可执行主键约束。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|preserve_duplicate|O|只有通用策略说明|53|

### preserve_duplicate：只有通用策略说明

主键去重策略及代价明确，未点名candidate_tag这一复合主键或其重复行。

事件 **53**，字段`args.final_thought`；[轨迹原文](../016_trace_impl-017.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/53.json`。
```text
staging 对声明为主键的空值行进行过滤，并按主键分组只保留一条记录以满足唯一性；若重复键的内容不一致，合同没有规定优先版本，因而保留记录选择未定义，重复记录中的非键值可能丢失。
```

已检视55个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：一条查询。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-017.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **1条**（含014复用；本轮新增1条）；核实代价档：**一条查询**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 016-V1 / 核实查询

来源：`records/016_queries_impl-017.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/greenhouse.duckdb`。

```sql
SELECT candidate_id,tag_id,count(*) n FROM raw.candidate_tag GROUP BY 1,2 HAVING count(*)>1
```
结果原文：
```json
{
  "columns": [
    "candidate_id",
    "tag_id",
    "n"
  ],
  "rows": [
    [
      4420,
      114,
      2
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['candidate_id', 'tag_id']`；比较列（与键取并集）：`['candidate_id', 'tag_id']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：本次重新执行；原013留存输出另列

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|preserve_duplicate|1→0|2→0|L0|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1999|2000|0|0|0/1|0|1|2|False|
|L1|1999|2000|0|0|0/1|0|1|2|False|
|L2|1999|2000|0|0|0/1|0|1|2|False|
|L3|1999|2000|0|0|0/1|0|1|2|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|candidate_id|0|0|0|0|
|tag_id|0|0|0|0|

### 重跑 baseline

SQL：`data/016_work/impl-017/baseline.sql`；SHA-256：`c8cc99d5f7e37a7f6e616b4d31ad7eb393fd3f0276a57f3a3f8fa9e62f5523c5`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1999|2000|0|0|0/1|0|1|2|False|
|L1|1999|2000|0|0|0/1|0|1|2|False|
|L2|1999|2000|0|0|0/1|0|1|2|False|
|L3|1999|2000|0|0|0/1|0|1|2|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|candidate_id|0|0|0|0|
|tag_id|0|0|0|0|

### 重跑 preserve_duplicate

SQL：`data/016_work/impl-017/preserve_duplicate.sql`；SHA-256：`7cec8e9bd915c3e12988fcc910389c31af46a9ecf5dd7605a3b3120d31158a01`。

唯一原文位置offset=509，替换前：
```sql
WHERE _row_num = 1
```
替换后：
```sql
WHERE TRUE
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|2000|2000|0|0|0/0|0|0|0|True|
|L1|2000|2000|0|0|0/0|0|0|0|True|
|L2|2000|2000|0|0|0/0|0|0|0|True|
|L3|2000|2000|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|candidate_id|0|0|0|0|
|tag_id|0|0|0|0|

## 5. 逐项类别及U门槛

表级主要原因：**O**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|preserve_duplicate|O|1→0|2→0|L0|

重跑是否满足U第4条件：**是（preserve_duplicate单改L0整表一致；非U）**。

无错误的唯一性假设：agent正是显式处理重复，而非依赖无重复。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：不适用：第二批首次标注。此字段不代替本次与016/017的对比。

## 规则问题

primary_key按通常完整性约束理解，而非仅描述评分对齐键；若任务只想表达grain而不要求唯一，则O/A边界需另定义。本次按契约字面主键归O。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
