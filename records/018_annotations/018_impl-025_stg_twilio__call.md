# impl-025 / stg_twilio__call（v2定稿）

## 1. 差异描述与判定

电话格式失败本应置NULL，agent先去符号并补+1再验证，两个电话列保留了gold置空的值。

已核实：raw2500行，from/to无值直接满足^\+1[0-9]{10}$；agent修复后分别2490/2491行可通过。共同运行日期筛选后2492行，user/contact分别2482/2483格不同。契约规定格式不符nullify_field，未规定先重写或推断国家码；agent增加repair阶段，归C。去掉contact修复后行数2492→2482，去掉user修复后→2483，故按行数选择contact主因，user为C参与因素。不把格子下降一半冒充本表所选行数口径的U4。

主要原因：**C**；把握：**中**。
参与因素：C：user_phone_number预修复，单改2492→2483行。标记：无。

与上一版（017）相比：原因类别及参与因素不变。不确定性由017的“看到了但没提”改按四档逐项记录：contact_phone_no_repair=只有通用策略说明。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../017_annotations/017_impl-025_stg_twilio__call.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自017，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-025_staging_stg_twilio__call.md)；不修改既有官方判错状态。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-025/docs/data_contract.yaml` 第116–191行。
- [完整轨迹](../017_trace_impl-025.json)，保留事件原文和原始路径；可回查授权归档`traces/dacomp_deimpl_prev.tar.gz`。
- [查询原文及结果](../017_queries_impl-025.json)、[重跑完整记录](../017_reruns_impl-025.json)、[原始表库存](../015_raw_impl-025.json)。
- [新增不确定性字段审计](../017_uncertainty_audit.json)、[本表依赖raw核对](../017_dependency_raw_audit.json)。
- [执行前指纹](../017_input_before.json)、[结束后指纹](../017_input_after.json)。本次前快照完成后才开始标注、查询和重跑。

轨迹导出例外：event16样例中的两处Twilio账户标识因GitHub push protection拦截已脱敏，其他事件内容保留；[脱敏位置与原文校验信息](../017_trace_redactions.json)。data/原始轨迹未改，引用的电话证据不涉及脱敏位置。

### 契约原文

```yaml
    - name: stg_twilio__call
      description: "Validated call records with standardized phone fields, temporal integrity, and derived metrics (types per current implementation)."
      source_table: raw.twilio_call_data
      columns:
        - name: account_id
          data_type: VARCHAR
        - name: annotation
          data_type: VARCHAR
        - name: answered_by
          data_type: VARCHAR
        - name: created_at
          data_type: TIMESTAMP
          constraints: [not_null]
          validation_rules:
            - rule: "created_at <= CURRENT_TIMESTAMP"
              on_failure: delete_row
        - name: direction
          data_type: VARCHAR
        - name: call_duration_s
          data_type: INTEGER
          description: "Derived from raw duration in seconds; NULL when missing."
        - name: call_ended_at
          data_type: TIMESTAMP
        - name: call_started_at
          data_type: TIMESTAMP
        - name: call_id
          data_type: VARCHAR
        - name: caller_name
          data_type: VARCHAR
          validation_rules:
            - rule: "caller_name = TRIM(caller_name)"
              on_failure: correct
            - rule: "caller_name RLIKE '^[A-Za-z0-9\\s._-]*$'"
              on_failure: nullify_field
            - rule: "LENGTH(caller_name) <= 50"
              on_failure: nullify_field
        - name: forwarded_from
          data_type: VARCHAR
        - name: group_id
          data_type: VARCHAR
        - name: parent_call_id
          data_type: VARCHAR
        - name: raw_price
          data_type: DOUBLE
          description: "Raw price as floating-point per current implementation."
        - name: price_unit
          data_type: VARCHAR
        - name: user_phone_number
          data_type: VARCHAR
          validation_rules:
            - rule: "user_phone_number RLIKE '^\\+1[0-9]{10}$'"
              on_failure: nullify_field
        - name: contact_phone_number
          data_type: VARCHAR
          validation_rules:
            - rule: "contact_phone_number RLIKE '^\\+1[0-9]{10}$'"
              on_failure: nullify_field
        - name: status
          data_type: VARCHAR
          validation_rules:
            - rule: "status IN ('queued','ringing','in-progress','completed','failed','busy','no-answer','canceled')"
              on_failure: nullify_field
        - name: updated_at
          data_type: TIMESTAMP
          validation_rules:
            - rule: "updated_at IS NULL OR updated_at >= created_at"
              on_failure: delete_row
        - name: price_in_usd
          data_type: DOUBLE
          description: "Normalized USD price computed as floating-point per current implementation."
        - name: start_date
          data_type: DATE
        - name: has_talked
          data_type: BOOLEAN
          description: "True when duration indicates any talk time; otherwise NULL."
```

### SQL定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/sql/staging/stg_twilio__call.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: with source_data as (
   2:     select
   3:         account_id::varchar as account_id,
   4:         try_cast(annotation as varchar) as annotation,
   5:         answered_by::varchar as answered_by,
   6:         try_cast(replace(created_at, ' UTC', '') as timestamp) as created_at,
   7:         direction::varchar as direction,
   8:         try_cast(duration as integer) as call_duration_s,
   9:         try_cast(replace(end_time, ' UTC', '') as timestamp) as call_ended_at,
  10:         try_cast(replace(start_time, ' UTC', '') as timestamp) as call_started_at,
  11:         id::varchar as call_id,
  12:         trim(try_cast(caller_name as varchar)) as caller_name,
  13:         try_cast(forwarded_from as varchar) as forwarded_from,
  14:         try_cast(group_id as varchar) as group_id,
  15:         try_cast(parent_call_id as varchar) as parent_call_id,
  16:         price::double as raw_price,
  17:         price_unit::varchar as price_unit,
  18:         regexp_replace(regexp_replace(try_cast("from" as varchar), '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as user_phone_number_raw,
  19:         regexp_replace(regexp_replace(try_cast("to" as varchar), '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as contact_phone_number_raw,
  20:         status::varchar as status,
  21:         try_cast(replace(updated_at, ' UTC', '') as timestamp) as updated_at
  22:     from raw.call_data
  23: ),
  24: cleaned as (
  25:     select
  26:         account_id, annotation, answered_by, created_at, direction, call_duration_s,
  27:         call_ended_at, call_started_at, call_id,
  28:         case when caller_name is null then null
  29:              when regexp_matches(caller_name, '^[A-Za-z0-9\s._-]*$') and length(caller_name) <= 50 then caller_name
  30:              else null end as caller_name,
  31:         forwarded_from, group_id, parent_call_id, raw_price, price_unit,
  32:         case when regexp_matches(user_phone_number_raw, '^\+1[0-9]{10}$') then user_phone_number_raw else null end as user_phone_number,
  33:         case when regexp_matches(contact_phone_number_raw, '^\+1[0-9]{10}$') then contact_phone_number_raw else null end as contact_phone_number,
  34:         case when status in ('queued','ringing','in-progress','completed','failed','busy','no-answer','canceled') then status else null end as status,
  35:         updated_at,
  36:         raw_price as price_in_usd,
  37:         cast(call_started_at as date) as start_date,
  38:         case when call_duration_s > 0 then true else null end as has_talked
  39:     from source_data
  40: )
  41: select
  42:     account_id, annotation, answered_by, created_at, direction, call_duration_s,
  43:     call_ended_at, call_started_at, call_id, caller_name, forwarded_from, group_id,
  44:     parent_call_id, raw_price, price_unit, user_phone_number, contact_phone_number,
  45:     status, updated_at, price_in_usd, start_date, has_talked
  46: from cleaned
  47: where created_at is not null and created_at <= current_timestamp
  48:   and (updated_at is null or updated_at >= created_at)
```

gold（仅用于定位差异）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-025/sql/staging/stg_twilio__call.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: with base as (
   2:     select *
   3:     from raw.call_data
   4: ),
   5:
   6: fields as (
   7:     select
   8:         account_id,
   9:         annotation,
  10:         answered_by,
  11:         try_cast(created_at as timestamp) as created_at,
  12:         direction,
  13:         duration,
  14:         try_cast(end_time as timestamp) as end_time,
  15:         try_cast(start_time as timestamp) as start_time,
  16:         id,
  17:         caller_name,
  18:         forwarded_from,
  19:         group_id,
  20:         parent_call_id,
  21:         price,
  22:         price_unit,
  23:         "from",
  24:         "to",
  25:         status,
  26:         try_cast(updated_at as timestamp) as updated_at
  27:     from base
  28: ),
  29:
  30: filtered as (
  31:     select *
  32:     from fields
  33:     where
  34:         created_at is not null
  35:         and created_at <= current_timestamp
  36:         and (updated_at is null or created_at <= updated_at)
  37:         and (caller_name is null or (
  38:             trim(cast(caller_name as varchar)) = cast(caller_name as varchar)
  39:             and cast(caller_name as varchar) ~ '^[A-Za-z0-9\s._-]*$'
  40:             and length(cast(caller_name as varchar)) <= 50
  41:         ))
  42: ),
  43:
  44: final as (
  45:     select
  46:         account_id,
  47:         annotation,
  48:         answered_by,
  49:         created_at,
  50:         direction,
  51:         cast(duration as integer) as call_duration_s,
  52:         cast(end_time as timestamp) as call_ended_at,
  53:         cast(start_time as timestamp) as call_started_at,
  54:         cast(id as varchar) as call_id,
  55:         caller_name,
  56:         cast(forwarded_from as varchar) as forwarded_from,
  57:         group_id,
  58:         parent_call_id,
  59:         cast(price as double) as raw_price,
  60:         price_unit,
  61:         case when "from" ~ '^\+1[0-9]{10}$' then "from" else null end as user_phone_number,
  62:         case when "to" ~ '^\+1[0-9]{10}$' then "to" else null end as contact_phone_number,
  63:         case when status in ('queued', 'ringing', 'in-progress', 'completed', 'failed', 'busy', 'no-answer', 'canceled') then status else null end as status,
  64:         updated_at,
  65:         cast(price as double)/100.0 as price_in_usd,
  66:         cast(start_time as date) as start_date,
  67:         case when trim(cast(duration as varchar)) != '' and trim(cast(duration as varchar)) != '0' then true else null end as has_talked
  68:     from filtered
  69: )
  70:
  71: select *
  72: from final
```

### 原始数据可评估性

下表复用015的完整表schema/行数/typed行哈希比较，只列本表静态传递依赖及双方SQL直接引用的raw。缺表不当作空表；gold与agent一致但二者不同于初始不自动排除（021/030）。

|依赖raw|比较|类型/列序相同|行数相同|typed行哈希相同|差异原因|
|---|---|---|---|---|---|
|raw.call_data|gold_vs_initial|True|True|True||
|raw.call_data|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event15→16已展示call_data.from/to不含+的样例；event17写预清洗及补+1表达式；event23→24查询本表user_phone_number分布，看到NULL10条和多个+1号码。event41解释的是outgoing_caller_id另一表的过滤，不是本表call补号码的选择。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|contact_phone_no_repair|C|只有通用策略说明|41|

### contact_phone_no_repair：只有通用策略说明

相关电话失败处理的一般声明；没有说明call.contact_phone_number校验前去符号/补+1。声明与实际代码可有差别，本字段不判断声明正确。另表outgoing_caller_id的具体说明不迁移到本表。

事件 **41**，字段`args.final_thought`；[轨迹原文](../017_trace_impl-025.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/41.json`。
```text
依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。
```

已检视43个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：一条查询。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../017_reruns_impl-025.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用017的查询与重跑证据；其中“新增/本次”的执行归属仍为017，018没有重复执行。
核实查询执行 **1条**（失败尝试也计入）；核实代价档：**一条查询**。每张≤5条，均只查agent当时可见数据。诊断可以查gold，不计入此数。

### V1 / 核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/twilio.duckdb`。
```sql
SELECT count(*) n,count(*) FILTER(WHERE regexp_full_match(cast("from" AS VARCHAR),'^\+1[0-9]{10}$')) from_valid_before,count(*) FILTER(WHERE regexp_full_match(cast("to" AS VARCHAR),'^\+1[0-9]{10}$')) to_valid_before,count(*) FILTER(WHERE regexp_full_match(regexp_replace(regexp_replace(cast("from" AS VARCHAR),'[^0-9]','','g'),'^1?([0-9]{10})$','+1\1'),'^\+1[0-9]{10}$')) from_valid_after,count(*) FILTER(WHERE regexp_full_match(regexp_replace(regexp_replace(cast("to" AS VARCHAR),'[^0-9]','','g'),'^1?([0-9]{10})$','+1\1'),'^\+1[0-9]{10}$')) to_valid_after FROM raw.call_data
```
结果原文：
```json
{
  "executed_utc": "2026-10-29T11:33:05.736017+00:00",
  "columns": [
    "n",
    "from_valid_before",
    "to_valid_before",
    "from_valid_after",
    "to_valid_after"
  ],
  "rows": [
    [
      2500,
      0,
      0,
      2490,
      2491
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['call_id']`；原评分比较列：`['account_id', 'annotation', 'answered_by', 'call_duration_s', 'call_id', 'caller_name', 'contact_phone_number', 'direction', 'forwarded_from', 'group_id', 'has_talked', 'parent_call_id', 'price_unit', 'raw_price', 'start_date', 'status', 'user_phone_number']`。与键取并集，不自行纳入原评分排除列。

全部原数据库以READ_ONLY连接或ATTACH；本次建表和改SQL只在`data/017_work/`。staging用agent留存raw，021/027用gold上游CS。每个试验从相同原SQL独立替换，不累积其他修复。

共同时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+08'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。023/025/028沿原筛查候选日期；030沿010已经验证的兼容2025-10-13日期（不声称唯一执行日）；共同控制先应用到基线及全部干预，不能作为某个局部修复的功劳。

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|user_phone_no_repair|2492→2483|4965→2483|无|
|contact_phone_no_repair|2492→2482|4965→2482|无|

### 原留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|2492|2492|0|0|0/0|2492|2492|4965|False|
|L1|2492|2492|0|0|0/0|2492|2492|4965|False|
|L2|2492|2492|0|0|0/0|2492|2492|4965|False|
|L3|2492|2492|0|0|0/0|2492|2492|4965|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|call_id|0|0|0|0|
|account_id|0|0|0|0|
|annotation|0|0|0|0|
|answered_by|0|0|0|0|
|call_duration_s|0|0|0|0|
|caller_name|0|0|0|0|
|contact_phone_number|2483|2483|2483|2483|
|direction|0|0|0|0|
|forwarded_from|0|0|0|0|
|group_id|0|0|0|0|
|has_talked|0|0|0|0|
|parent_call_id|0|0|0|0|
|price_unit|0|0|0|0|
|raw_price|0|0|0|0|
|start_date|0|0|0|0|
|status|0|0|0|0|
|user_phone_number|2482|2482|2482|2482|

### 重跑 baseline

SQL：`data/017_work/impl-025/baseline.sql`；SHA-256：`fc4cfd2e14504576672f54a9b90cec58ef536d31b93b9ec92f20d19ee85ceb02`。

同输入、同时间控制、不增加因果改动的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|2492|2492|0|0|0/0|2492|2492|4965|False|
|L1|2492|2492|0|0|0/0|2492|2492|4965|False|
|L2|2492|2492|0|0|0/0|2492|2492|4965|False|
|L3|2492|2492|0|0|0/0|2492|2492|4965|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|call_id|0|0|0|0|
|account_id|0|0|0|0|
|annotation|0|0|0|0|
|answered_by|0|0|0|0|
|call_duration_s|0|0|0|0|
|caller_name|0|0|0|0|
|contact_phone_number|2483|2483|2483|2483|
|direction|0|0|0|0|
|forwarded_from|0|0|0|0|
|group_id|0|0|0|0|
|has_talked|0|0|0|0|
|parent_call_id|0|0|0|0|
|price_unit|0|0|0|0|
|raw_price|0|0|0|0|
|start_date|0|0|0|0|
|status|0|0|0|0|
|user_phone_number|2482|2482|2482|2482|

### 重跑 user_phone_no_repair

SQL：`data/017_work/impl-025/user_phone_no_repair.sql`；SHA-256：`0ed82bc0a3e0163580d341212d439b9324d6266d664b2eea1a899d3bc9ddd17e`。

唯一替换位置offset=874；原文：
```sql
regexp_replace(regexp_replace(try_cast("from" as varchar), '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1')
```
新文：
```sql
try_cast("from" as varchar)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|2492|2492|0|0|0/0|2483|2483|2483|False|
|L1|2492|2492|0|0|0/0|2483|2483|2483|False|
|L2|2492|2492|0|0|0/0|2483|2483|2483|False|
|L3|2492|2492|0|0|0/0|2483|2483|2483|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|call_id|0|0|0|0|
|account_id|0|0|0|0|
|annotation|0|0|0|0|
|answered_by|0|0|0|0|
|call_duration_s|0|0|0|0|
|caller_name|0|0|0|0|
|contact_phone_number|2483|2483|2483|2483|
|direction|0|0|0|0|
|forwarded_from|0|0|0|0|
|group_id|0|0|0|0|
|has_talked|0|0|0|0|
|parent_call_id|0|0|0|0|
|price_unit|0|0|0|0|
|raw_price|0|0|0|0|
|start_date|0|0|0|0|
|status|0|0|0|0|
|user_phone_number|0|0|0|0|

### 重跑 contact_phone_no_repair

SQL：`data/017_work/impl-025/contact_phone_no_repair.sql`；SHA-256：`72156dd41c1403472a72f27e08cfcac44d5281378bf99539738d6fc72109a2d0`。

唯一替换位置offset=1014；原文：
```sql
regexp_replace(regexp_replace(try_cast("to" as varchar), '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1')
```
新文：
```sql
try_cast("to" as varchar)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|2492|2492|0|0|0/0|2482|2482|2482|False|
|L1|2492|2492|0|0|0/0|2482|2482|2482|False|
|L2|2492|2492|0|0|0/0|2482|2482|2482|False|
|L3|2492|2492|0|0|0/0|2482|2482|2482|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|call_id|0|0|0|0|
|account_id|0|0|0|0|
|annotation|0|0|0|0|
|answered_by|0|0|0|0|
|call_duration_s|0|0|0|0|
|caller_name|0|0|0|0|
|contact_phone_number|0|0|0|0|
|direction|0|0|0|0|
|forwarded_from|0|0|0|0|
|group_id|0|0|0|0|
|has_talked|0|0|0|0|
|parent_call_id|0|0|0|0|
|price_unit|0|0|0|0|
|raw_price|0|0|0|0|
|start_date|0|0|0|0|
|status|0|0|0|0|
|user_phone_number|2482|2482|2482|2482|

## 5. 逐项类别及U门槛

表级主要原因：**C**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|contact_phone_no_repair|C|2492→2482|4965→2482|无|

重跑是否满足U第4条件：**否：所选行数口径最大仅2492→2482行**。

数据格式并非完全未见：轨迹已展示不符合原样模式的源值。主要问题是将明确的nullify失败处理改成先repair，而非漏查是否含+。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。不确定性由017的“看到了但没提”改按四档逐项记录：contact_phone_no_repair=只有通用策略说明。

与014相比的历史对比沿用原字段：不适用：第三批首次标注。此字段不代替本次与016/017的对比。

## 规则问题

v2新增通用策略档，最终报告一般电话处理声明可放此档，尽管未解释本表预修复且声明不能证明代码遵约。主因C按行数选contact，user为C参与因素；不换格子来达到半数门槛。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
