# impl-018 / stg_salesforce__opportunity_line_item（v2定稿）

## 1. 差异描述与判定

通用id映射把opportunity_id和product_2_id都写成本行id，后续修FK时漏掉此表，两项并列。

已核实：3000行/6000格，分别换回raw.opportunity_id和raw.product_2_id后均3000行/3000格。event19的全局mapping将实体主键名均映射id，连带误用于外键；event57代码注释明确“canonical foreign keys should remain FK columns, not the row's own id”，实际只修其他五表，遗漏本表。因此存在正确意图与代码未实现的证据，两个I并列。016-V1证实opportunity源列能关联432条而id为0，且is_deleted为true的行0，补过滤无改善。

主要原因：**I**；把握：**中**。
参与因素：无：删除标记过滤对照未改善。标记：无。

与上一版（016）相比：原因类别：多因并列（I）→I。v2第5节要求同类并列直接记该类，独立项及数值均保留。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-018_stg_salesforce__opportunity_line_item.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-018_staging_stg_salesforce__opportunity_line_item.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` 第747–786行。
- [原始轨迹转录](../016_trace_impl-018.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-018.json)；[015三方raw核对](../015_raw_impl-018.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_salesforce__opportunity_line_item
      description: "Cleaned opportunity line item records with validated product and pricing information"
      source_table: raw.opportunity_line_item
      columns:
        - name: opportunity_line_item_id
          data_type: VARCHAR
        - name: opportunity_id
          data_type: VARCHAR
        - name: product_2_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
        - name: opportunity_line_item_description
          data_type: VARCHAR
        - name: has_quantity_schedule
          data_type: BOOLEAN
        - name: has_revenue_schedule
          data_type: BOOLEAN
        - name: is_deleted
          data_type: BOOLEAN
          validation_rules:
            - rule: "NOT COALESCE(is_deleted, false)"
              on_failure: delete_row
        - name: last_modified_date
          data_type: TIMESTAMP
        - name: list_price
          data_type: DECIMAL
        - name: pricebook_entry_id
          data_type: VARCHAR
        - name: quantity
          data_type: DECIMAL
        - name: service_date
          data_type: DATE
        - name: sort_order
          data_type: INTEGER
        - name: total_price
          data_type: DECIMAL
        - name: unit_price
          data_type: DECIMAL
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql`
```sql
   1: select
   2:       id as opportunity_line_item_id,
   3:       id as opportunity_id,
   4:       id as product_2_id,
   5:       try_cast(created_date as TIMESTAMP) as created_date,
   6:       description as opportunity_line_item_description,
   7:       has_quantity_schedule as has_quantity_schedule,
   8:       has_revenue_schedule as has_revenue_schedule,
   9:       is_deleted as is_deleted,
  10:       try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
  11:       try_cast(list_price as DECIMAL) as list_price,
  12:       pricebook_entry_id as pricebook_entry_id,
  13:       try_cast(quantity as DECIMAL) as quantity,
  14:       try_cast(service_date as DATE) as service_date,
  15:       try_cast(sort_order as INTEGER) as sort_order,
  16:       try_cast(total_price as DECIMAL) as total_price,
  17:       try_cast(unit_price as DECIMAL) as unit_price
  18: from raw.opportunity_line_item
  19: where id is not null
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql`
```sql
   1: with fields as (
   2:     select *
   3:     from raw.opportunity_line_item
   4: ), 
   5: 
   6: final as (
   7:     select
   8:         cast(id as varchar) as opportunity_line_item_id,
   9:         cast(opportunity_id as varchar) as opportunity_id,
  10:         cast(product_2_id as varchar) as product_2_id,
  11:         cast(created_date as timestamp) as created_date,
  12:         cast(description as varchar) as opportunity_line_item_description,
  13:         cast(coalesce(has_quantity_schedule, false) as boolean) as has_quantity_schedule,
  14:         cast(coalesce(has_revenue_schedule, false) as boolean) as has_revenue_schedule,
  15:         cast(coalesce(is_deleted, false) as boolean) as is_deleted,
  16:         cast(last_modified_date as timestamp) as last_modified_date,
  17:         cast(list_price as decimal) as list_price,
  18:         cast(pricebook_entry_id as varchar) as pricebook_entry_id,
  19:         cast(quantity as decimal) as quantity,
  20:         cast(service_date as date) as service_date,
  21:         cast(sort_order as integer) as sort_order,
  22:         cast(total_price as decimal) as total_price,
  23:         cast(unit_price as decimal) as unit_price
  24:     from fields
  25: )
  26: 
  27: select *
  28: from final
  29: where not coalesce(is_deleted, false)
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.opportunity_line_item|gold_vs_initial|True|True|True||
|raw.opportunity_line_item|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event19通用生成器；event57明确外键映射原则和修复列表；本表不在列表。schema存在两外键不足以单独证明意图，使用的是event57的明确注释与实际修复行为。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|opportunity_source|I|看到了但没提|14|
|product_source|I|看到了但没提|14|

### opportunity_source：看到了但没提

源schema中两个外键可见。event57代码注释表达正确的通用FK意图，用于I归因；它不在思考字段或最终报告中，不自动当作v2第6节的说明。最终报告未讨论本表两外键来源。

事件 **14**，字段`content`；[轨迹原文](../016_trace_impl-018.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/14.json`。
```text
e, _fivetran_active, _fivetran_start, _fivetran_end, _fivetran_synced
opportunity_line_item id, created_by_id, created_date, description, discount, has_quantity_schedule, has_revenue_schedule, has_schedule, is_deleted, last_modified_by_id, last_modified_date, last_referenced_date, last_viewed_date, list_price, name, opportunity_id, pricebook_entry_id, product_2_id, product_code, quantity, service_date, sort_order, system_modstamp, total_price, unit_price
order_data id, account_id, activated_by_id, activated_date, billing_city, billing_country, billing_country_code, billing_geocode_accuracy, billing_latitude, billing_longitude, billing_postal_code, billing_state, billing_state_code, billing_street, company_authorized_by_id, contract_id, created_by_id, created_date, customer_authorized_by_id, description, effective_date, end_date, is_deleted, is_reduction_order, last_modified_by_id, last_modified_date, last_r
```

### product_source：看到了但没提

源schema中两个外键可见。event57代码注释表达正确的通用FK意图，用于I归因；它不在思考字段或最终报告中，不自动当作v2第6节的说明。最终报告未讨论本表两外键来源。

事件 **14**，字段`content`；[轨迹原文](../016_trace_impl-018.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/14.json`。
```text
e, _fivetran_active, _fivetran_start, _fivetran_end, _fivetran_synced
opportunity_line_item id, created_by_id, created_date, description, discount, has_quantity_schedule, has_revenue_schedule, has_schedule, is_deleted, last_modified_by_id, last_modified_date, last_referenced_date, last_viewed_date, list_price, name, opportunity_id, pricebook_entry_id, product_2_id, product_code, quantity, service_date, sort_order, system_modstamp, total_price, unit_price
order_data id, account_id, activated_by_id, activated_date, billing_city, billing_country, billing_country_code, billing_geocode_accuracy, billing_latitude, billing_longitude, billing_postal_code, billing_state, billing_state_code, billing_street, company_authorized_by_id, contract_id, created_by_id, created_date, customer_authorized_by_id, description, effective_date, end_date, is_deleted, is_reduction_order, last_modified_by_id, last_modified_date, last_r
```

已检视101个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：一条查询。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-018.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **1条**（含014复用；本轮新增1条）；核实代价档：**一条查询**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 016-V1 / 核实查询

来源：`records/016_queries_impl-018.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.opportunity o WHERE o.id=i.opportunity_id)) opportunity_source_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.opportunity o WHERE o.id=i.id)) generic_id_matches,count(*) FILTER(WHERE is_deleted) deleted FROM raw.opportunity_line_item i
```
结果原文：
```json
{
  "columns": [
    "n",
    "opportunity_source_matches",
    "generic_id_matches",
    "deleted"
  ],
  "rows": [
    [
      3000,
      432,
      0,
      0
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['opportunity_line_item_id']`；比较列（与键取并集）：`['created_date', 'has_quantity_schedule', 'has_revenue_schedule', 'is_deleted', 'last_modified_date', 'list_price', 'opportunity_id', 'pricebook_entry_id', 'product_2_id', 'quantity', 'service_date', 'sort_order', 'total_price', 'unit_price']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：本次重新执行；原013留存输出另列

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|opportunity_source|3000→3000|6000→3000|无|
|product_source|3000→3000|6000→3000|无|
|deleted_filter|3000→3000|6000→6000|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|0|0|0/0|3000|3000|6000|False|
|L1|3000|3000|0|0|0/0|3000|3000|6000|False|
|L2|3000|3000|0|0|0/0|3000|3000|6000|False|
|L3|3000|3000|0|0|0/0|3000|3000|6000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|opportunity_line_item_id|0|0|0|0|
|created_date|0|0|0|0|
|has_quantity_schedule|0|0|0|0|
|has_revenue_schedule|0|0|0|0|
|is_deleted|0|0|0|0|
|last_modified_date|0|0|0|0|
|list_price|0|0|0|0|
|opportunity_id|3000|3000|3000|3000|
|pricebook_entry_id|0|0|0|0|
|product_2_id|3000|3000|3000|3000|
|quantity|0|0|0|0|
|service_date|0|0|0|0|
|sort_order|0|0|0|0|
|total_price|0|0|0|0|
|unit_price|0|0|0|0|

### 重跑 baseline

SQL：`data/016_work/impl-018/baseline.sql`；SHA-256：`df414b04f8faa46e8fad09eeb3ffe15dbcc9a76d05d5719959d21892c402c16a`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|0|0|0/0|3000|3000|6000|False|
|L1|3000|3000|0|0|0/0|3000|3000|6000|False|
|L2|3000|3000|0|0|0/0|3000|3000|6000|False|
|L3|3000|3000|0|0|0/0|3000|3000|6000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|opportunity_line_item_id|0|0|0|0|
|created_date|0|0|0|0|
|has_quantity_schedule|0|0|0|0|
|has_revenue_schedule|0|0|0|0|
|is_deleted|0|0|0|0|
|last_modified_date|0|0|0|0|
|list_price|0|0|0|0|
|opportunity_id|3000|3000|3000|3000|
|pricebook_entry_id|0|0|0|0|
|product_2_id|3000|3000|3000|3000|
|quantity|0|0|0|0|
|service_date|0|0|0|0|
|sort_order|0|0|0|0|
|total_price|0|0|0|0|
|unit_price|0|0|0|0|

### 重跑 opportunity_source

SQL：`data/016_work/impl-018/opportunity_source.sql`；SHA-256：`e1372f42be9aa7afe44cbaac0f97da6e11de81884edb2cafbef1eedf7b78ebca`。

唯一原文位置offset=51，替换前：
```sql
id as opportunity_id
```
替换后：
```sql
opportunity_id as opportunity_id
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|0|0|0/0|3000|3000|3000|False|
|L1|3000|3000|0|0|0/0|3000|3000|3000|False|
|L2|3000|3000|0|0|0/0|3000|3000|3000|False|
|L3|3000|3000|0|0|0/0|3000|3000|3000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|opportunity_line_item_id|0|0|0|0|
|created_date|0|0|0|0|
|has_quantity_schedule|0|0|0|0|
|has_revenue_schedule|0|0|0|0|
|is_deleted|0|0|0|0|
|last_modified_date|0|0|0|0|
|list_price|0|0|0|0|
|opportunity_id|0|0|0|0|
|pricebook_entry_id|0|0|0|0|
|product_2_id|3000|3000|3000|3000|
|quantity|0|0|0|0|
|service_date|0|0|0|0|
|sort_order|0|0|0|0|
|total_price|0|0|0|0|
|unit_price|0|0|0|0|

### 重跑 product_source

SQL：`data/016_work/impl-018/product_source.sql`；SHA-256：`13e8f3a35237bdb49916cfa06d75c8ae482844849eeae50e80c6e4263f783139`。

唯一原文位置offset=79，替换前：
```sql
id as product_2_id
```
替换后：
```sql
product_2_id as product_2_id
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|0|0|0/0|3000|3000|3000|False|
|L1|3000|3000|0|0|0/0|3000|3000|3000|False|
|L2|3000|3000|0|0|0/0|3000|3000|3000|False|
|L3|3000|3000|0|0|0/0|3000|3000|3000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|opportunity_line_item_id|0|0|0|0|
|created_date|0|0|0|0|
|has_quantity_schedule|0|0|0|0|
|has_revenue_schedule|0|0|0|0|
|is_deleted|0|0|0|0|
|last_modified_date|0|0|0|0|
|list_price|0|0|0|0|
|opportunity_id|3000|3000|3000|3000|
|pricebook_entry_id|0|0|0|0|
|product_2_id|0|0|0|0|
|quantity|0|0|0|0|
|service_date|0|0|0|0|
|sort_order|0|0|0|0|
|total_price|0|0|0|0|
|unit_price|0|0|0|0|

### 重跑 deleted_filter

SQL：`data/016_work/impl-018/deleted_filter.sql`；SHA-256：`03724eb182196a55d0b1b0c46fdc74fdd74bca1c0b69391616f9d5037a42686f`。

唯一原文位置offset=818，替换前：
```sql
where id is not null
```
替换后：
```sql
where id is not null AND NOT COALESCE(is_deleted,false)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|3000|3000|0|0|0/0|3000|3000|6000|False|
|L1|3000|3000|0|0|0/0|3000|3000|6000|False|
|L2|3000|3000|0|0|0/0|3000|3000|6000|False|
|L3|3000|3000|0|0|0/0|3000|3000|6000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|opportunity_line_item_id|0|0|0|0|
|created_date|0|0|0|0|
|has_quantity_schedule|0|0|0|0|
|has_revenue_schedule|0|0|0|0|
|is_deleted|0|0|0|0|
|last_modified_date|0|0|0|0|
|list_price|0|0|0|0|
|opportunity_id|3000|3000|3000|3000|
|pricebook_entry_id|0|0|0|0|
|product_2_id|3000|3000|3000|3000|
|quantity|0|0|0|0|
|service_date|0|0|0|0|
|sort_order|0|0|0|0|
|total_price|0|0|0|0|
|unit_price|0|0|0|0|

## 5. 逐项类别及U门槛

表级主要原因：**I**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|opportunity_source|I|3000→3000|6000→3000|无|
|product_source|I|3000→3000|6000→3000|无|

重跑是否满足U第4条件：**是（每项单改6000→3000格；类别依据为I）**。

有可验证外键关系，但明确正确意图证据使I比U更贴近机制；不把原始opportunity只有部分引用匹配解释为全表外键完整性成立。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别：多因并列（I）→I。v2第5节要求同类并列直接记该类，独立项及数值均保留。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：不适用：第二批首次标注。此字段不代替本次与016/017的对比。

## 规则问题

两个外键原因均I，按v2表级直接I。event57代码注释能支持第3节正确意图，但第6节明确要求思考或最终报告；本次不把代码注释自动转成该字段的口头披露，因此两个外键均记看到了但没提。这是跨字段证据用途区别，不更改I门槛。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
