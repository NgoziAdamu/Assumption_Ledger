# impl-017 / stg_greenhouse__candidate_tag

## 1. 错在哪里

agent按复合主键去掉一个重复candidate-tag行，gold保留重复，造成1行2格差异。

已核实：raw中(candidate_id=4420,tag_id=114)出现2次，其余不重复；契约primary_key=[candidate_id,tag_id]。agent ROW_NUMBER去重得到1999行，gold保留2000行。仅取消_row_num=1即L0整表一致。主键声明与gold重复行冲突，归O，不因保留重复能匹配gold反判agent未遵约。

## 2. 依据

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

## 3. agent看过什么

event1给出复合主键；event17生成窗口去重，后续运行成功。无需假定agent看过该重复值才可执行主键约束。

区分event实际展示的契约/数据与磁盘上存在的资料；截断输出中未出现的部分不算agent已经看到。核实查询是标注者新增查询，不冒充agent执行过。

## 4. 查询与重跑

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

## 5. 类别、把握及与014对比

- 主要原因：**O**。
- 主因对应单项：preserve_duplicate。
- 参与因素：无。
- 标记：无。
- 把握：**高**。
- 重跑是否满足U第4条件：是（preserve_duplicate单改L0整表一致；非U）。

无错误的唯一性假设：agent正是显式处理重复，而非依赖无重复。

与014相比：**不适用：第二批首次标注**

## 规则问题

primary_key按通常完整性约束理解，而非仅描述评分对齐键；若任务只想表达grain而不要求唯一，则O/A边界需另定义。本次按契约字面主键归O。

2026-10-29用户确认的第3节补充：仅当本表依赖raw满足agent留存=初始、gold不同，且诊断确认影响可评估性时标“不可评估”；gold=初始、agent不同则照常标注，查轨迹改动。不能把两类混为一谈。若gold与agent一致但二者不同于初始（019/020），当前本节点仍可比较；初始差异另记。

共同执行例外：最初指纹快照因外部v0附件已不在原桌面路径而失败；成功的016快照晚于首批私有重跑。已逐文件与015任务前的大小、mtime、SHA-256比较，覆盖原始库的历史指纹无变化；不把晚快照伪称执行前快照。仓库v0与004–015记录保留。
