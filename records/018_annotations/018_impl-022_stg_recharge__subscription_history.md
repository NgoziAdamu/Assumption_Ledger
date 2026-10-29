# impl-022 / stg_recharge__subscription_history（v2定稿）

## 1. 差异描述与判定

agent把subscription_id作为输出和latest分组键，gold改取历史行id；输出身份约定和窗口粒度均不同。

已核实：raw3500行，id唯一3500个，subscription_id为1667个；两列3495行不同。subscription_id能关联订阅主表3500行，id只能2500行。契约仅写History of subscription status changes及输出字段类型，未指明输出id来源或latest分组表达式。agent的FK选择有数据支持，不能因gold选历史行id就判U。单改输出投影使5043行/13087格降为1833行/1833格；单改窗口分组使4818行/12150格，两处分别归A。删除标记均false，单加过滤不改善。 A项仅表示差异取决于契约未定的选择，不据gold实现认定agent做错。

主要原因：**A**；把握：**中**。
参与因素：A：窗口分组的id约定，独立修改5043→4818行。标记：无。

与上一版（017）相比：原因类别及参与因素不变。不确定性由017的“看到了但没提”改按四档逐项记录：source_id_projection=看到了但没提。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../017_annotations/017_impl-022_stg_recharge__subscription_history.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自017，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-022_staging_stg_recharge__subscription_history.md)；不修改既有官方判错状态。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-022/docs/data_contract.yaml` 第436–454行。
- [完整轨迹](../017_trace_impl-022.json)，保留事件原文和原始路径；可回查授权归档`traces/dacomp_deimpl_prev.tar.gz`。
- [查询原文及结果](../017_queries_impl-022.json)、[重跑完整记录](../017_reruns_impl-022.json)、[原始表库存](../015_raw_impl-022.json)。
- [新增不确定性字段审计](../017_uncertainty_audit.json)、[本表依赖raw核对](../017_dependency_raw_audit.json)。
- [执行前指纹](../017_input_before.json)、[结束后指纹](../017_input_after.json)。本次前快照完成后才开始标注、查询和重跑。

### 契约原文

```yaml
    - name: stg_recharge__subscription_history
      description: "History of subscription status changes with most recent flag."
      source_table: raw.subscription_history
      columns:
        - name: subscription_id
          data_type: BIGINT
        - name: subscription_created_at
          data_type: TIMESTAMP
        - name: subscription_updated_at
          data_type: TIMESTAMP
        - name: subscription_status
          data_type: VARCHAR
        - name: is_most_recent_record
          data_type: BOOLEAN


# --------------------------------------------------------------------------- #
# PHASE 2: Defines the business logic from staging tables to analytical models. #
# --------------------------------------------------------------------------- #
```

### SQL定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-022/agent/dacomp-de-impl-022/sql/staging/stg_recharge__subscription_history.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: select
   2:     subscription_id as subscription_id,
   3:     try_cast(created_at as timestamp) as subscription_created_at,
   4:     try_cast(updated_at as timestamp) as subscription_updated_at,
   5:     status as subscription_status,
   6:     row_number() over (partition by subscription_id order by try_cast(updated_at as timestamp) desc nulls last, try_cast(created_at as timestamp) desc nulls last, id desc) = 1 as is_most_recent_record
   7: from raw.subscription_history
```

gold（仅用于定位差异）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-022/sql/staging/stg_recharge__subscription_history.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: with base as (
   2:     select *
   3:     from raw.subscription_history
   4: ),
   5: filtered as (
   6:     select *
   7:     from base
   8:     where not coalesce(cast(_fivetran_deleted as boolean), false)
   9: ),
  10: final as (
  11:     select
  12:         coalesce(cast(id as bigint), cast(subscription_id as bigint)) as subscription_id,
  13:         cast(created_at as timestamp) as subscription_created_at,
  14:         cast(updated_at as timestamp) as subscription_updated_at,
  15:         status as subscription_status
  16:     from filtered
  17: )
  18: select
  19:     *,
  20:     row_number() over (
  21:         partition by subscription_id
  22:         order by subscription_updated_at desc nulls last
  23:     ) = 1 as is_most_recent_record
  24: from final
```

### 原始数据可评估性

下表复用015的完整表schema/行数/typed行哈希比较，只列本表静态传递依赖及双方SQL直接引用的raw。缺表不当作空表；gold与agent一致但二者不同于初始不自动排除（021/030）。

|依赖raw|比较|类型/列序相同|行数相同|typed行哈希相同|差异原因|
|---|---|---|---|---|---|
|raw.subscription_history|gold_vs_initial|True|True|True||
|raw.subscription_history|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event9→10展示raw.subscription_history中id、subscription_id、status、时间及删除标记列；event11选subscription_id并增加时间/id排序。event19移除未在契约规定的删除过滤；event33解释此类过滤的取舍，但没有讨论本表id来源和latest粒度。未找到两id关联核实。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|source_id_projection|A|看到了但没提|10|

### source_id_projection：看到了但没提

本表id和subscription_id可见；关于其他subscription缺列及删除过滤的报告不解释本表历史行身份选择。

事件 **10**，字段`content`；[轨迹原文](../017_trace_impl-022.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-022/agent/.events/sessions/f3ea262f-0060-45-e44535a6cc133cd/events/10.json`。
```text
_at: VARCHAR
  _fivetran_deleted: BOOLEAN
  _fivetran_synced: VARCHAR
subscription_history:
  id: BIGINT
  subscription_id: BIGINT
  status: VARCHAR
  created_at: VARCHAR
  updated_at: VARCHAR
  _fivetran_deleted: BOOLEAN
  _fivetran_synced: VARCHAR
[('address',), ('address_discounts',), ('address_shipping_line',), ('charge',), ('charge_discount',), ('charge_line_item',), ('charge_order_attribute',), ('charge_shipping_line',), ('charge_tax_line',), ('checkout',), ('customer',), ('discount',), ('one_time_product',), ('order_bool_int',), ('order_line_item',), ('orders',), ('subscription',), ('subscription_history',)]

 address [('id', 'BIGINT', 'YES', None, None, None), ('customer_id', 'BIGINT', 'YES', None, None, None), ('subscription_id', 'DOUBLE', 'YES', None, None, None), ('first_name', 'VARCHAR', 'YES', None, None, None), ('last_name', 'VARCHAR', 'YES', None, None, None), ('company', 'VARCHAR', 'YES', No
```

已检视35个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：需要查业务说明。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../017_reruns_impl-022.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用017的查询与重跑证据；其中“新增/本次”的执行归属仍为017，018没有重复执行。
核实查询执行 **1条**（失败尝试也计入）；核实代价档：**需要查业务说明**。每张≤5条，均只查agent当时可见数据。诊断可以查gold，不计入此数。

### V1 / 核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-022/agent/dacomp-de-impl-022/recharge.duckdb`。
```sql
SELECT count(*) n,count(distinct id) distinct_id,count(distinct subscription_id) distinct_subscription_id,count(*) FILTER(WHERE id IS DISTINCT FROM subscription_id) different_id,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.subscription s WHERE s.id=h.id)) id_matches_subscription,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.subscription s WHERE s.id=h.subscription_id)) fk_matches_subscription,count(*) FILTER(WHERE _fivetran_deleted) deleted FROM raw.subscription_history h
```
结果原文：
```json
{
  "executed_utc": "2026-10-29T11:33:05.662752+00:00",
  "columns": [
    "n",
    "distinct_id",
    "distinct_subscription_id",
    "different_id",
    "id_matches_subscription",
    "fk_matches_subscription",
    "deleted"
  ],
  "rows": [
    [
      3500,
      3500,
      1667,
      3495,
      2500,
      3500,
      0
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['subscription_id']`；原评分比较列：`['is_most_recent_record', 'subscription_id', 'subscription_status']`。与键取并集，不自行纳入原评分排除列。

全部原数据库以READ_ONLY连接或ATTACH；本次建表和改SQL只在`data/017_work/`。staging用agent留存raw，021/027用gold上游CS。每个试验从相同原SQL独立替换，不累积其他修复。

共同时间控制：`[]`。023/025/028沿原筛查候选日期；030沿010已经验证的兼容2025-10-13日期（不声称唯一执行日）；共同控制先应用到基线及全部干预，不能作为某个局部修复的功劳。

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|source_id_projection|5043→1833|13087→1833|无|
|source_id_group|5043→4818|13087→12150|无|
|deleted_filter|5043→5043|13087→13087|无|

### 原留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3500|3500|0|1833|1833/0|1377|5043|13087|False|
|L1|3500|3500|0|1833|1833/0|1377|5043|13087|False|
|L2|3500|3500|0|1833|1833/0|1377|5043|13087|False|
|L3|3500|3500|0|1833|1833/0|1377|5043|13087|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|subscription_id|0|0|0|0|
|is_most_recent_record|857|857|857|857|
|subscription_status|1232|1232|1232|1232|

### 重跑 baseline

SQL：`data/017_work/impl-022/baseline.sql`；SHA-256：`25d715039cde5e0fb28be6f4dc5c77527ed3ee56d7a846e8dde214217fab58ea`。

同输入、同时间控制、不增加因果改动的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3500|3500|0|1833|1833/0|1377|5043|13087|False|
|L1|3500|3500|0|1833|1833/0|1377|5043|13087|False|
|L2|3500|3500|0|1833|1833/0|1377|5043|13087|False|
|L3|3500|3500|0|1833|1833/0|1377|5043|13087|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|subscription_id|0|0|0|0|
|is_most_recent_record|857|857|857|857|
|subscription_status|1232|1232|1232|1232|

### 重跑 source_id_projection

SQL：`data/017_work/impl-022/source_id_projection.sql`；SHA-256：`497f147bd165353b60b7d43d3a932fe6cb7670865624bf06580d9b8f5006f88f`。

唯一替换位置offset=11；原文：
```sql
subscription_id as subscription_id
```
新文：
```sql
coalesce(cast(id as bigint), cast(subscription_id as bigint)) as subscription_id
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3500|3500|0|0|0/0|1833|1833|1833|False|
|L1|3500|3500|0|0|0/0|1833|1833|1833|False|
|L2|3500|3500|0|0|0/0|1833|1833|1833|False|
|L3|3500|3500|0|0|0/0|1833|1833|1833|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|subscription_id|0|0|0|0|
|is_most_recent_record|1833|1833|1833|1833|
|subscription_status|0|0|0|0|

### 重跑 source_id_group

SQL：`data/017_work/impl-022/source_id_group.sql`；SHA-256：`f5f159a56a4def48c150cfd16ae324c62ff1f803b4b9bdf146f2cd5915d0a1f7`。

唯一替换位置offset=237；原文：
```sql
partition by subscription_id
```
新文：
```sql
partition by coalesce(cast(id as bigint), cast(subscription_id as bigint))
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3500|3500|0|1833|1833/0|1152|4818|12150|False|
|L1|3500|3500|0|1833|1833/0|1152|4818|12150|False|
|L2|3500|3500|0|1833|1833/0|1152|4818|12150|False|
|L3|3500|3500|0|1833|1833/0|1152|4818|12150|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|subscription_id|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|subscription_status|1152|1152|1152|1152|

### 重跑 deleted_filter

SQL：`data/017_work/impl-022/deleted_filter.sql`；SHA-256：`0a24be498973be50f1134b6461d21b3326ccd71952e3508f65c903f1cffbcfea`。

唯一替换位置offset=415；原文：
```sql
from raw.subscription_history
```
新文：
```sql
from raw.subscription_history
where not coalesce(_fivetran_deleted,false)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3500|3500|0|1833|1833/0|1377|5043|13087|False|
|L1|3500|3500|0|1833|1833/0|1377|5043|13087|False|
|L2|3500|3500|0|1833|1833/0|1377|5043|13087|False|
|L3|3500|3500|0|1833|1833/0|1377|5043|13087|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|subscription_id|0|0|0|0|
|is_most_recent_record|857|857|857|857|
|subscription_status|1232|1232|1232|1232|

## 5. 逐项类别及U门槛

表级主要原因：**A**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|source_id_projection|A|5043→1833|13087→1833|无|

重跑是否满足U第4条件：**是：投影来源单改5043→1833行，减少63.7%；不是U**。

数据能够显示两个id并不等价、FK候选关联更完整，但目标契约没有明确定义是订阅实体还是历史行身份，不用gold的选择构造错误P。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。不确定性由017的“看到了但没提”改按四档逐项记录：source_id_projection=看到了但没提。

与014相比的历史对比沿用原字段：不适用：第三批首次标注。此字段不代替本次与016/017的对比。

## 规则问题

投影与窗口分组都来自同一未规定身份约定，但在SQL中是两个可单独改动的落点；本次分别量化，不把联合修改效果归给任一项。可把gold的历史id选择读成语义问题；没有明确source_expression或FK约束，保守归A而不扩大O。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
