# impl-029 / stg_zendesk__schedule_holiday

## 1. 错在哪里

一个start_date为2022-12-291163029，agent整串TRY_CAST为空，gold截前10位得到2022-12-29。

已核实：51行中仅id1163027不同；原文为2022-12-291163029，end_date为2022-12-29。这不是仅TIMESTAMP/DATE显示差异，而是包含尾部数字的畸形输入。契约仅声明start_date DATE，没有指定截前缀或恢复污染值。agent用安全转换失败置NULL，gold截前10位；数据能发现异常，但不能唯一确定尾部数字应丢弃的恢复规则，因此归A。单改前缀解析即L0匹配；补删除过滤无影响。

## 2. 依据

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

## 3. agent看过什么

event17→18查看start_date为VARCHAR的schema，没有查询本表日期样例；event21生成TRY_CAST；event41→42只核对各表列名/类型。event55最终报告明确可选字段转换失败成为NULL、未追加文本规范化，但未点名该异常日期。

只把归档实际展示的内容视为已看到；磁盘有文件、命令包含表名或截断掉的部分，不等于看到相应数据值。

### 新增字段：是否意识到或提到相关不确定性

**已提到**。只记录可见表述/信息，不由该档位推定错误类别。

明确声明适用于本表可选日期列的转换失败→NULL策略；没有点名1163027或其畸形日期，不能据此声称已经看过异常值。

event **55**，字段`args.final_thought`；原路径`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-029/agent/.events/sessions/68a7ea61-4e9f-46-b468b8adb71510e/events/55.json`。
```text
必填字段空值或转换失败的记录按契约过滤；可选字段转换失败会成为 `NULL`。重复记录、枚举和文本规范化没有超出契约进行更改。
```

event **18**，字段`content`；原路径`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-029/agent/.events/sessions/68a7ea61-4e9f-46-b468b8adb71510e/events/18.json`。
```text
schedule_holiday_data:
  id: VARCHAR
  schedule_id: VARCHAR
  _fivetran_deleted: VARCHAR
  _fivetran_synced: VARCHAR
  end_date: VARCHAR
  name: VARCHAR
  start_date: VARCHAR
  column07: VARCHAR
  column08: VARCHAR
  column09: VARCHAR
  column10: VARCHAR
  column11: VARCHAR
  column12: VARCHAR
ticket_chat_data:
  chat_id: VARCHAR
  _fivetran_synced: VARCHAR
  authenticated: VARCHAR
  backend: VARCHAR
  channel: VARCHAR
  conversation_id: VARCHAR
  initiator: VARCHAR
  integration_id: VARCHAR
  tags: VARCHAR
  ticket_id: VARCHAR
  user_id: VARCHAR
  visitor_id: VARCHAR
  webpath: VARCHAR
  column13: VARCHAR
  column14: VARCHAR
  column15: VARCHAR
  column16: VARCHAR
  column17: VARCHAR
  column18: VARCHAR
  column19: VARCHAR
  column20: VARCHAR
  column21: VARCHAR
  column22: VARCHAR
  column23: VARCHAR
  column24: VARCHAR
ticket_chat_event_data:
  chat_id: VARCHAR
  created_at: VARCHAR
  _Company_synced: VARCHAR
  actor_id: VARCHAR
  chat_index: VARCHAR
  external_message_id: VARCHAR
  filename: VARCHAR
  is_history_context: VARCHAR
  message: VARCHAR
  message_id: VARCHAR
  message_source: VARCHAR
  mime_type: VARCHAR
  original_message: VARCHAR
  original_message_type: VARCHAR
  parent_message_id: VARCHAR
  reason: VARCHAR
  size: VARCHAR
  status: VARCHAR
  status_updated_at: VARCHAR
  type: VARCHAR
  url: VARCHAR
ticket_comment_data:
  id: VARCHAR
  _fivetran_synced: VARCHAR
  body: VARCHAR
  created: VARCHAR
  facebook_comment: VARCHAR
  public: VARCHAR
  ticket_id: VARCHAR
  tweet: VARCHAR
  user_id: VARCHAR
  voice_comment: VARCHAR
  column10: VARCHAR
  column11: VARCHAR
  column12: VARCHAR
  column13: VARCHAR
  column14: VARCHAR
  column15: VARCHAR
  column16: VARCHAR
  column17: VARCHAR
  column18: VARCHAR
ticket_data:
  id: VARCHAR
  _fivetran_synced: VARCHAR
  allow_channelback: VARCHAR
  assignee_id: VARCHAR
  brand_id: VARCHAR
  created_at: VARCHAR
  desc
```

归档逐项扫描57个事件；本批thought/args.thought字段均为空，不能由此推断agent没有内部思考。“已提到”的原句来自final_thought中的最终报告；“看到了但没提”依据可见工具返回，不把SQL代码本身当口头说明。长工具输出仅摘录连续原文，截取范围见JSON；不是说agent只看到了这个摘录。

## 4. 查询与重跑

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

## 5. 类别、把握和对比

- 主要原因：**A**（归因判断）。
- 主因单项：date_prefix。
- 参与因素：无；删除标记控制不改善。
- 标记：无。
- 把握：**中**。
- 重跑是否满足U第4条件：是：单取日期前缀后1行/1格→0，L0匹配；非U。

不能把使用TRY_CAST本身当成相信所有源值有效：它明确允许失败返回NULL，最终报告也说明此策略。异常值存在不等于可以从数据独立确定该采取截前缀而不是置NULL。

与014相比是否变化：不适用（第三批首次标注）；也未修改016任何结论。

## 规则问题

可读为U（未查到格式异常）或A（异常恢复策略未给）。选择A，保持与016的解析策略处理一致；本列无not_null或source_expression要求，且源值含多余数字，不能仅凭gold实现补定规则。已提到档位仅表示全局可选字段失败策略适用于本表，不声称agent读过这一行。

2026-10-29用户确认补充：本表依赖原始表若agent留存与初始一致而gold不同，先诊断再标不可评估；若gold与初始一致而agent不同，则正常标注并追踪agent运行中的改动。不能把两种情况混淆。raw差异须限定到本表依赖；CS上游用gold。

新增字段统一口径：记录与实际差异机制相关的明确选择/可疑数据表述；不要求agent预知gold，也不把泛称“完成清洗”算作识别具体边界。021关于重复计数、029关于可选字段失败置NULL为适用范围较广的声明，单独注明并未点名本表异常；可见证据只能支持这一有限范围。该字段不增减U/C/D/I/A/O/X条件。
