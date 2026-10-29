# impl-020 / stg_intercom__conversation_part_history（v2定稿）

## 1. 差异描述与判定

agent从复合id提取BIGINT会话号而gold保留原列时间文本，另补subject到part_type；gold类型与契约冲突。

已核实：契约conversation_id BIGINT，raw同名列全是不可转BIGINT的时间文本，gold直接保留成VARCHAR；agent从id前缀构造BIGINT。conversation_direct单改使7524行/15000格变7476行/7476格；part_type_direct单改仍7524行、7524格。按行数先选conversation_id主因；gold输出违反类型声明，归O，中把握。part_type的NULL用subject填充属于未写明的恢复规则，可读为A差异，但本表已由行数选主因，单改行数不降不列参与因素。created_at虽违背明确source_expression，未在比较列/键中，控制重跑也无影响。015的gold/agent raw一致，初始不同，不是不可评估。

主要原因：**O**；把握：**中**。
参与因素：无：part_type单改行数不降；created_at未参与评分。标记：无。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-020_stg_intercom__conversation_part_history.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-020_staging_stg_intercom__conversation_part_history.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml` 第225–250行。
- [原始轨迹转录](../016_trace_impl-020.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-020.json)；[015三方raw核对](../015_raw_impl-020.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_intercom__conversation_part_history
      description: "Conversation part events with typing and activity filtering."
      source_table: raw.conversation_part_history_data
      columns:
        - name: conversation_part_id
          data_type: VARCHAR
          source_expression: "id"
        - name: part_type
          data_type: VARCHAR
        - name: body
          data_type: VARCHAR
        - name: conversation_id
          data_type: BIGINT
        - name: author_id
          data_type: VARCHAR
        - name: author_type
          data_type: VARCHAR
        - name: created_at
          data_type: TIMESTAMP
          source_expression: "try_cast(created_at as timestamp)"
        - name: updated_at
          data_type: TIMESTAMP
      row_filters:
        - rule: "coalesce(try_cast(_fivetran_active as BOOLEAN), true)"
          on_failure: delete_row
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/staging/stg_intercom__conversation_part_history.sql`
```sql
   1: with source_rows as (
   2:     select
   3:         try_cast(id as varchar) as conversation_part_id,
   4:         coalesce(try_cast(part_type as varchar), try_cast(subject as varchar)) as part_type,
   5:         try_cast(body as varchar) as body,
   6:         try_cast(split_part(id, '_', 1) as bigint) as conversation_id,
   7:         try_cast(author_id as varchar) as author_id,
   8:         try_cast(author_type as varchar) as author_type,
   9:         coalesce(try_cast(raw_part_time as timestamp), try_cast(updated_at as timestamp)) as created_at,
  10:         try_cast(updated_at as timestamp) as updated_at,
  11:         coalesce(try_cast(_fivetran_active as boolean), true) as is_active
  12:     from (
  13:         select *, try_cast(conversation_id as timestamp) as raw_part_time
  14:         from raw.conversation_part_history_data
  15:     ) source
  16: )
  17: select conversation_part_id, part_type, body, conversation_id, author_id, author_type, created_at, updated_at
  18: from source_rows
  19: where is_active
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/sql/staging/stg_intercom__conversation_part_history.sql`
```sql
   1: select
   2:   id as conversation_part_id,
   3:   part_type,
   4:   body,
   5:   conversation_id,
   6:   author_id,
   7:   author_type,
   8:   try_cast(created_at as timestamp) as created_at,
   9:   updated_at
  10: from raw.conversation_part_history_data
  11: where coalesce(try_cast(_fivetran_active as BOOLEAN), true)
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.conversation_part_history_data|gold_vs_initial|False|True|False|ordered_columns_or_types_differ,sorted_content_hash_differ|
|raw.conversation_part_history_data|gold_vs_agent|True|True|True||

补充诊断与原始事件见[016_raw_diagnostics.json](../016_raw_diagnostics.json)。

## 3. agent实际看到的信息与不确定性四档

event23查询part_type/type等（输出有截断，不据未展示部分推断）；event31→32完整展示一行错位字段；event33/35尝试从其他列恢复会话号和时间，event37改为id前缀及时间回退。agent已经看过错位值，不说它完全没核实。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|conversation_direct|O|针对本表的具体说明|61|

### conversation_direct：针对本表的具体说明

明确点出conversation part错位、conversation_id的替代来源和原因，针对主因。

事件 **61**，字段`args.final_thought`；[轨迹原文](../016_trace_impl-020.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/61.json`。
```text
原始 conversation part 文件中的实际列数据与源 schema 声明不一致：对话 ID 实际可从 part `id` 的前缀提取，事件时间可从错位的原始 `conversation_id` 字段解析，事件类型可从 `subject` 字段回退获取。
```

已检视63个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：需要查业务说明。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-020.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **1条**（含014复用；本轮新增1条）；核实代价档：**需要查业务说明**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 016-V1 / 核实查询

来源：`records/016_queries_impl-020.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/intercom.duckdb`。

```sql
SELECT count(*) n,count(part_type) part_type_present,count(subject) subject_present,count(*) FILTER(WHERE coalesce(try_cast(_fivetran_active as BOOLEAN),true)) active_rows,count(*) FILTER(WHERE try_cast(conversation_id AS BIGINT) IS NOT NULL) numeric_conversation FROM raw.conversation_part_history_data
```
结果原文：
```json
{
  "columns": [
    "n",
    "part_type_present",
    "subject_present",
    "active_rows",
    "numeric_conversation"
  ],
  "rows": [
    [
      7524,
      48,
      7524,
      7524,
      0
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['conversation_part_id']`；比较列（与键取并集）：`['conversation_part_id', 'part_type', 'body', 'conversation_id', 'author_id', 'author_type']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：本次重新执行；原013留存输出另列

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|part_type_direct|7524→7524|15000→7524|无|
|conversation_direct|7524→7476|15000→7476|无|
|created_contract|7524→7524|15000→15000|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|7524|7524|0|0|0/0|7524|7524|15000|False|
|L1|7524|7524|0|0|0/0|7524|7524|15000|False|
|L2|7524|7524|0|0|0/0|7524|7524|15000|False|
|L3|7524|7524|0|0|0/0|7524|7524|15000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|conversation_part_id|0|0|0|0|
|part_type|7476|7476|7476|7476|
|body|0|0|0|0|
|conversation_id|7524|7524|7524|7524|
|author_id|0|0|0|0|
|author_type|0|0|0|0|

### 重跑 baseline

SQL：`data/016_work/impl-020/baseline.sql`；SHA-256：`67883decbe3a4275bcf27399d260fdbe19958b54eb331c066c6aebf50e348cca`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|7524|7524|0|0|0/0|7524|7524|15000|False|
|L1|7524|7524|0|0|0/0|7524|7524|15000|False|
|L2|7524|7524|0|0|0/0|7524|7524|15000|False|
|L3|7524|7524|0|0|0/0|7524|7524|15000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|conversation_part_id|0|0|0|0|
|part_type|7476|7476|7476|7476|
|body|0|0|0|0|
|conversation_id|7524|7524|7524|7524|
|author_id|0|0|0|0|
|author_type|0|0|0|0|

### 重跑 part_type_direct

SQL：`data/016_work/impl-020/part_type_direct.sql`；SHA-256：`73e17dbc475cbe219c249100339adf9d18bee5de3e39c0a646a52deeb0265d21`。

唯一原文位置offset=98，替换前：
```sql
coalesce(try_cast(part_type as varchar), try_cast(subject as varchar))
```
替换后：
```sql
try_cast(part_type as varchar)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|7524|7524|0|0|0/0|7524|7524|7524|False|
|L1|7524|7524|0|0|0/0|7524|7524|7524|False|
|L2|7524|7524|0|0|0/0|7524|7524|7524|False|
|L3|7524|7524|0|0|0/0|7524|7524|7524|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|conversation_part_id|0|0|0|0|
|part_type|0|0|0|0|
|body|0|0|0|0|
|conversation_id|7524|7524|7524|7524|
|author_id|0|0|0|0|
|author_type|0|0|0|0|

### 重跑 conversation_direct

SQL：`data/016_work/impl-020/conversation_direct.sql`；SHA-256：`4b61844636e013156a82ef8d2a994ee938be5f3c85cf37ed292ddc8e7d21c134`。

唯一原文位置offset=234，替换前：
```sql
try_cast(split_part(id, '_', 1) as bigint)
```
替换后：
```sql
conversation_id
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|7524|7524|0|0|0/0|7476|7476|7476|False|
|L1|7524|7524|0|0|0/0|7476|7476|7476|False|
|L2|7524|7524|0|0|0/0|7476|7476|7476|False|
|L3|7524|7524|0|0|0/0|7476|7476|7476|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|conversation_part_id|0|0|0|0|
|part_type|7476|7476|7476|7476|
|body|0|0|0|0|
|conversation_id|0|0|0|0|
|author_id|0|0|0|0|
|author_type|0|0|0|0|

### 重跑 created_contract

SQL：`data/016_work/impl-020/created_contract.sql`；SHA-256：`39f852ff0e102b44685581551e1a79a1e0751287677daadf44b18ee7a7abedc9`。

唯一原文位置offset=415，替换前：
```sql
coalesce(try_cast(raw_part_time as timestamp), try_cast(updated_at as timestamp))
```
替换后：
```sql
try_cast(created_at as timestamp)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|7524|7524|0|0|0/0|7524|7524|15000|False|
|L1|7524|7524|0|0|0/0|7524|7524|15000|False|
|L2|7524|7524|0|0|0/0|7524|7524|15000|False|
|L3|7524|7524|0|0|0/0|7524|7524|15000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|conversation_part_id|0|0|0|0|
|part_type|7476|7476|7476|7476|
|body|0|0|0|0|
|conversation_id|7524|7524|7524|7524|
|author_id|0|0|0|0|
|author_type|0|0|0|0|

## 5. 逐项类别及U门槛

表级主要原因：**O**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|conversation_direct|O|7524→7476|15000→7476|无|

重跑是否满足U第4条件：**否（所选行数口径7524→7476，未达一半）**。

本次核实raw.conversation_id无一可转BIGINT；这说明原列不满足契约目标类型，而不是证明id前缀的恢复一定对。缺少完整对应业务说明，O仅依据gold直接类型矛盾。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：不适用：第二批首次标注。此字段不代替本次与016/017的对比。

## 规则问题

若允许主因用行数、参与因素随时换格子，则part_type可列A参与因素；本次同一表使用同一选定口径，保留为潜在差异而不列参与因素，避免口径切换。O不证明agent所有恢复策略正确。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
