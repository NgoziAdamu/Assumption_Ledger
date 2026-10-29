# impl-029 / stg_zendesk__schedule_holiday（v2定稿）

## 1. 差异描述与判定

一个start_date为2022-12-291163029，agent整串TRY_CAST为空，gold截前10位得到2022-12-29。

已核实：51行中仅id1163027不同；原文为2022-12-291163029，end_date为2022-12-29。这不是仅TIMESTAMP/DATE显示差异，而是包含尾部数字的畸形输入。契约仅声明start_date DATE，没有指定截前缀或恢复污染值。agent用安全转换失败置NULL，gold截前10位；数据能发现异常，但不能唯一确定尾部数字应丢弃的恢复规则，因此归A。单改前缀解析即L0匹配；补删除过滤无影响。 A项仅表示差异取决于契约未定的选择，不据gold实现认定agent做错。

主要原因：**A**；把握：**中**。
参与因素：无；删除标记控制不改善。标记：无。

与上一版（017）相比：原因类别及参与因素不变。不确定性由017的“已提到”改按四档逐项记录：date_prefix=只有通用策略说明。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../017_annotations/017_impl-029_stg_zendesk__schedule_holiday.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自017，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-029_staging_stg_zendesk__schedule_holiday.md)；不修改既有官方判错状态。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-029/docs/data_contract.yaml` 第131–146行。
- [完整轨迹](../017_trace_impl-029.json)，保留事件原文和原始路径；可回查授权归档`traces/dacomp_deimpl_prev.tar.gz`。
- [查询原文及结果](../017_queries_impl-029.json)、[重跑完整记录](../017_reruns_impl-029.json)、[原始表库存](../015_raw_impl-029.json)。
- [新增不确定性字段审计](../017_uncertainty_audit.json)、[本表依赖raw核对](../017_dependency_raw_audit.json)。
- [执行前指纹](../017_input_before.json)、[结束后指纹](../017_input_after.json)。本次前快照完成后才开始标注、查询和重跑。

### 契约原文

```yaml
    - name: stg_zendesk__schedule_holiday
      description: "Holiday exceptions per schedule."
      source_table: raw.schedule_holiday_data
      columns:
        - name: schedule_holiday_id
          data_type: BIGINT
          constraints: [not_null]
        - name: schedule_id
          data_type: BIGINT
        - name: name
          data_type: VARCHAR
        - name: start_date
          data_type: DATE
        - name: end_date
          data_type: DATE
```

### SQL定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-029/agent/dacomp-de-impl-029/sql/staging/stg_zendesk__schedule_holiday.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: select
   2:     try_cast("id" as BIGINT) as schedule_holiday_id,
   3:     try_cast("schedule_id" as BIGINT) as schedule_id,
   4:     try_cast("name" as VARCHAR) as name,
   5:     try_cast("start_date" as DATE) as start_date,
   6:     try_cast("end_date" as DATE) as end_date
   7: from raw.schedule_holiday_data
   8: where try_cast("id" as BIGINT) is not null
```

gold（仅用于定位差异）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-029/sql/staging/stg_zendesk__schedule_holiday.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: with base as (
   2:   select id, schedule_id, name, start_date, end_date, _fivetran_deleted from raw.schedule_holiday_data
   3: ), cleaned as (
   4:   select cast(id as BIGINT) as schedule_holiday_id,
   5:          cast(schedule_id as BIGINT) as schedule_id,
   6:          name,
   7:          cast(substr(cast(start_date as varchar), 1, 10) as DATE) as start_date,
   8:          cast(substr(cast(end_date as varchar), 1, 10) as DATE) as end_date
   9:   from base
  10:   where id is not null and coalesce(try_cast(_fivetran_deleted as BOOLEAN), false) = false
  11: )
  12: select *
  13: from cleaned
```

### 原始数据可评估性

下表复用015的完整表schema/行数/typed行哈希比较，只列本表静态传递依赖及双方SQL直接引用的raw。缺表不当作空表；gold与agent一致但二者不同于初始不自动排除（021/030）。

|依赖raw|比较|类型/列序相同|行数相同|typed行哈希相同|差异原因|
|---|---|---|---|---|---|
|raw.schedule_holiday_data|gold_vs_initial|True|True|True||
|raw.schedule_holiday_data|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event17→18查看start_date为VARCHAR的schema，没有查询本表日期样例；event21生成TRY_CAST；event41→42只核对各表列名/类型。event55最终报告明确可选字段转换失败成为NULL、未追加文本规范化，但未点名该异常日期。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|date_prefix|A|只有通用策略说明|55|

### date_prefix：只有通用策略说明

适用于本表可选日期的转换失败策略，未点名畸形start_date或是否截前缀。

事件 **55**，字段`args.final_thought`；[轨迹原文](../017_trace_impl-029.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-029/agent/.events/sessions/68a7ea61-4e9f-46-b468b8adb71510e/events/55.json`。
```text
必填字段空值或转换失败的记录按契约过滤；可选字段转换失败会成为 `NULL`。重复记录、枚举和文本规范化没有超出契约进行更改。
```

已检视57个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：需要查业务说明。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../017_reruns_impl-029.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用017的查询与重跑证据；其中“新增/本次”的执行归属仍为017，018没有重复执行。
核实查询执行 **1条**（失败尝试也计入）；核实代价档：**需要查业务说明**。每张≤5条，均只查agent当时可见数据。诊断可以查gold，不计入此数。

### V1 / 核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-029/agent/dacomp-de-impl-029/zendesk.duckdb`。
```sql
SELECT id,start_date,end_date,try_cast(start_date AS DATE) direct_date,try_cast(substr(start_date,1,10) AS DATE) prefix_date FROM raw.schedule_holiday_data WHERE try_cast(start_date AS DATE) IS DISTINCT FROM try_cast(substr(start_date,1,10) AS DATE)
```
结果原文：
```json
{
  "executed_utc": "2026-10-29T11:33:05.830406+00:00",
  "columns": [
    "id",
    "start_date",
    "end_date",
    "direct_date",
    "prefix_date"
  ],
  "rows": [
    [
      "1163027",
      "2022-12-291163029",
      "2022-12-29",
      null,
      "2022-12-29"
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['schedule_holiday_id']`；原评分比较列：`['end_date', 'schedule_holiday_id', 'start_date']`。与键取并集，不自行纳入原评分排除列。

全部原数据库以READ_ONLY连接或ATTACH；本次建表和改SQL只在`data/017_work/`。staging用agent留存raw，021/027用gold上游CS。每个试验从相同原SQL独立替换，不累积其他修复。

共同时间控制：`[]`。023/025/028沿原筛查候选日期；030沿010已经验证的兼容2025-10-13日期（不声称唯一执行日）；共同控制先应用到基线及全部干预，不能作为某个局部修复的功劳。

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|date_prefix|1→0|1→0|L0|
|deleted_filter|1→1|1→1|无|

### 原留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|51|51|0|0|0/0|1|1|1|False|
|L1|51|51|0|0|0/0|1|1|1|False|
|L2|51|51|0|0|0/0|1|1|1|False|
|L3|51|51|0|0|0/0|1|1|1|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|schedule_holiday_id|0|0|0|0|
|end_date|0|0|0|0|
|start_date|1|1|1|1|

### 重跑 baseline

SQL：`data/017_work/impl-029/baseline.sql`；SHA-256：`b6e47acd1ed169148431bf84716589084927ea57734f0d7a9f0ce9e3f1076972`。

同输入、同时间控制、不增加因果改动的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|51|51|0|0|0/0|1|1|1|False|
|L1|51|51|0|0|0/0|1|1|1|False|
|L2|51|51|0|0|0/0|1|1|1|False|
|L3|51|51|0|0|0/0|1|1|1|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|schedule_holiday_id|0|0|0|0|
|end_date|0|0|0|0|
|start_date|1|1|1|1|

### 重跑 date_prefix

SQL：`data/017_work/impl-029/date_prefix.sql`；SHA-256：`c26794ae1a0209b70da7704f9092594bec3a14bed3167ce301f6e86e7125fa57`。

唯一替换位置offset=159；原文：
```sql
try_cast("start_date" as DATE)
```
新文：
```sql
try_cast(substr(cast("start_date" as VARCHAR),1,10) as DATE)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|51|51|0|0|0/0|0|0|0|True|
|L1|51|51|0|0|0/0|0|0|0|True|
|L2|51|51|0|0|0/0|0|0|0|True|
|L3|51|51|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|schedule_holiday_id|0|0|0|0|
|end_date|0|0|0|0|
|start_date|0|0|0|0|

### 重跑 deleted_filter

SQL：`data/017_work/impl-029/deleted_filter.sql`；SHA-256：`9b72440ec67ead3a9f80612d25c10499984c4a1183e3a20aebb23b7917fec3c1`。

唯一替换位置offset=281；原文：
```sql
where try_cast("id" as BIGINT) is not null
```
新文：
```sql
where try_cast("id" as BIGINT) is not null AND coalesce(try_cast(_fivetran_deleted as BOOLEAN),false)=false
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|51|51|0|0|0/0|1|1|1|False|
|L1|51|51|0|0|0/0|1|1|1|False|
|L2|51|51|0|0|0/0|1|1|1|False|
|L3|51|51|0|0|0/0|1|1|1|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|schedule_holiday_id|0|0|0|0|
|end_date|0|0|0|0|
|start_date|1|1|1|1|

## 5. 逐项类别及U门槛

表级主要原因：**A**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|date_prefix|A|1→0|1→0|L0|

重跑是否满足U第4条件：**是：单取日期前缀后1行/1格→0，L0匹配；非U**。

不能把使用TRY_CAST本身当成相信所有源值有效：它明确允许失败返回NULL，最终报告也说明此策略。异常值存在不等于可以从数据独立确定该采取截前缀而不是置NULL。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。不确定性由017的“已提到”改按四档逐项记录：date_prefix=只有通用策略说明。

与014相比的历史对比沿用原字段：不适用：第三批首次标注。此字段不代替本次与016/017的对比。

## 规则问题

v2明确将“转换失败成为NULL”这种跨表说明归通用策略，原三档已提到据此细分。解析/截前缀仍缺约定，A不变；不能把TRY_CAST主动允许失败说成假设每行可解析。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
