# impl-015 / stg_quickbooks__item

## 1. 错在哪里

tax_code_id取sales_tax_code_id而gold填NULL；agent另在导入raw时通过pandas改变了全NULL列类型。

已核实：raw.item_data有sales_tax_code_id和purchase_tax_code_id，各2000个非空且全部不等，无统一tax_code_id列。契约未指明选销售税还是采购税、是否留空。只改tax_code_id为NULL即可2000行/2000格→0，归A。015三方结果gold=初始、agent仅parent_item_id类型由VARCHAR变INTEGER。event44报告重复ATTACH句柄冲突；event45为绕开它改成fetchdf/register后CREATE OR REPLACE raw，导致类型重新推断；本次在私有副本复现全NULL parent_item_id导入变INTEGER。原行值无差异的015记录与此一致。继续正常标注，不能列不可评估，也不把这个未参与评分的类型改变当本节点主因。

## 2. 依据

- 起点：[013精简材料包](../013_packages/013_impl-015_staging_stg_quickbooks__item.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml` 第407–461行。
- [原始轨迹转录](../016_trace_impl-015.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-015.json)；[015三方raw核对](../015_raw_impl-015.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_quickbooks__item
      description: "Cleaned product and service items with standardized pricing and inventory information"
      source_table: "raw.item_data"
      columns:
        - name: item_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: parent_item_id
          data_type: VARCHAR
        - name: income_account_id
          data_type: VARCHAR
        - name: expense_account_id
          data_type: VARCHAR
        - name: asset_account_id
          data_type: VARCHAR
        - name: tax_code_id
          data_type: VARCHAR
        - name: sales_tax_code_id
          data_type: VARCHAR
        - name: purchase_tax_code_id
          data_type: VARCHAR
        - name: name
          data_type: VARCHAR
          constraints: [not_null]
        - name: description
          data_type: VARCHAR
        - name: fully_qualified_name
          data_type: VARCHAR
        - name: sku
          data_type: VARCHAR
        - name: type
          data_type: VARCHAR
        - name: unit_price
          data_type: DECIMAL(28,6)
        - name: purchase_cost
          data_type: DECIMAL(28,6)
        - name: quantity_on_hand
          data_type: DECIMAL(28,6)
        - name: is_active
          data_type: BOOLEAN
        - name: is_taxable
          data_type: BOOLEAN
        - name: track_quantity_on_hand
          data_type: BOOLEAN
        - name: created_at
          data_type: TIMESTAMP
        - name: updated_at
          data_type: TIMESTAMP
        - name: sync_token
          data_type: VARCHAR
        - name: source_relation
          data_type: VARCHAR
      filter_conditions:
        - "id is not null and name is not null and track_quantity_on_hand is not null"
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/sql/staging/stg_quickbooks__item.sql`
```sql
   1: WITH typed AS (
   2:     SELECT
   3:         CAST(r.id AS VARCHAR) AS "item_id",
   4:         CAST(r.parent_item_id AS VARCHAR) AS "parent_item_id",
   5:         CAST(r.income_account_id AS VARCHAR) AS "income_account_id",
   6:         CAST(r.expense_account_id AS VARCHAR) AS "expense_account_id",
   7:         CAST(r.asset_account_id AS VARCHAR) AS "asset_account_id",
   8:         CAST(r.sales_tax_code_id AS VARCHAR) AS "tax_code_id",
   9:         CAST(r.sales_tax_code_id AS VARCHAR) AS "sales_tax_code_id",
  10:         CAST(r.purchase_tax_code_id AS VARCHAR) AS "purchase_tax_code_id",
  11:         CAST(r.name AS VARCHAR) AS "name",
  12:         CAST(r.description AS VARCHAR) AS "description",
  13:         CAST(r.fully_qualified_name AS VARCHAR) AS "fully_qualified_name",
  14:         CAST(r.stock_keeping_unit AS VARCHAR) AS "sku",
  15:         CAST(r.type AS VARCHAR) AS "type",
  16:         TRY_CAST(r.unit_price AS DECIMAL(28,6)) AS "unit_price",
  17:         TRY_CAST(r.purchase_cost AS DECIMAL(28,6)) AS "purchase_cost",
  18:         TRY_CAST(r.quantity_on_hand AS DECIMAL(28,6)) AS "quantity_on_hand",
  19:         TRY_CAST(r.active AS BOOLEAN) AS "is_active",
  20:         TRY_CAST(r.taxable AS BOOLEAN) AS "is_taxable",
  21:         TRY_CAST(r.track_quantity_on_hand AS BOOLEAN) AS "track_quantity_on_hand",
  22:         TRY_CAST(r.created_at AS TIMESTAMP) AS "created_at",
  23:         TRY_CAST(r.updated_at AS TIMESTAMP) AS "updated_at",
  24:         CAST(r.sync_token AS VARCHAR) AS "sync_token",
  25:         'quickbooks' AS "source_relation"
  26:     FROM raw.item_data AS r
  27: )
  28: SELECT * FROM typed
  29: WHERE (item_id IS NOT NULL AND name IS NOT NULL AND track_quantity_on_hand IS NOT NULL)
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-015/sql/staging/stg_quickbooks__item.sql`
```sql
   1: with source as (
   2:     select *
   3:     from raw.item_data
   4: )
   5: 
   6: select
   7:     cast(id as varchar) as item_id,
   8:     cast(parent_item_id as varchar) as parent_item_id,
   9:     cast(income_account_id as varchar) as income_account_id,
  10:     cast(expense_account_id as varchar) as expense_account_id,
  11:     cast(asset_account_id as varchar) as asset_account_id,
  12:     cast(null as varchar) as tax_code_id,
  13:     cast(sales_tax_code_id as varchar) as sales_tax_code_id,
  14:     cast(purchase_tax_code_id as varchar) as purchase_tax_code_id,
  15:     cast(name as varchar) as name,
  16:     cast(description as varchar) as description,
  17:     cast(fully_qualified_name as varchar) as fully_qualified_name,
  18:     cast(stock_keeping_unit as varchar) as sku,
  19:     cast(type as varchar) as type,
  20:     case
  21:         when cast(unit_price as decimal(28,6)) is not null and (cast(unit_price as decimal(28,6)) < -999999.99 or cast(unit_price as decimal(28,6)) > 999999.99)
  22:         then null
  23:         else cast(unit_price as decimal(28,6))
  24:     end as unit_price,
  25:     case
  26:         when cast(purchase_cost as decimal(28,6)) is not null and (cast(purchase_cost as decimal(28,6)) < -999999.99 or cast(purchase_cost as decimal(28,6)) > 999999.99)
  27:         then null
  28:         else cast(purchase_cost as decimal(28,6))
  29:     end as purchase_cost,
  30:     cast(quantity_on_hand as decimal(28,6)) as quantity_on_hand,
  31:     cast(active as boolean) as is_active,
  32:     cast(taxable as boolean) as is_taxable,
  33:     cast(track_quantity_on_hand as boolean) as track_quantity_on_hand,
  34:     strptime(created_at, '%Y-%m-%d %H:%M:%S.%f %z') as created_at,
  35:     strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f %z') as updated_at,
  36:     cast(sync_token as varchar) as sync_token,
  37:     'main' as source_relation
  38: from source
  39: where id is not null and name is not null and track_quantity_on_hand is not null
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.item_data|gold_vs_initial|True|True|True||
|raw.item_data|gold_vs_agent|False|True|True|ordered_columns_or_types_differ|

补充诊断与原始事件见[016_raw_diagnostics.json](../016_raw_diagnostics.json)。

## 3. agent看过什么

event1完整契约；event17/21/25生成和修订字段映射；event44→45解释并实施raw导入路径修改。该改动是为修复初始化错误；未找到业务文档解释税码来源。

区分event实际展示的契约/数据与磁盘上存在的资料；截断输出中未出现的部分不算agent已经看到。核实查询是标注者新增查询，不冒充agent执行过。

## 4. 查询与重跑

核实查询合计 **1条**（含014复用；本轮新增1条）；核实代价档：**需要查业务说明**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 016-V1 / 核实查询

来源：`records/016_queries_impl-015.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/quickbooks.duckdb`。

```sql
SELECT count(*) n,count(sales_tax_code_id) sales_present,count(purchase_tax_code_id) purchase_present,count(*) FILTER(WHERE cast(sales_tax_code_id as varchar) IS DISTINCT FROM cast(purchase_tax_code_id as varchar)) unequal FROM raw.item_data
```
结果原文：
```json
{
  "columns": [
    "n",
    "sales_present",
    "purchase_present",
    "unequal"
  ],
  "rows": [
    [
      2000,
      2000,
      2000,
      2000
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['item_id']`；比较列（与键取并集）：`['asset_account_id', 'description', 'expense_account_id', 'fully_qualified_name', 'income_account_id', 'is_active', 'is_taxable', 'item_id', 'name', 'parent_item_id', 'purchase_cost', 'purchase_tax_code_id', 'quantity_on_hand', 'sales_tax_code_id', 'sku', 'sync_token', 'tax_code_id', 'track_quantity_on_hand', 'type', 'unit_price']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：本次重新执行；原013留存输出另列

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|tax_code_null|2000→0|2000→0|L0|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|2000|2000|0|0|0/0|2000|2000|2000|False|
|L1|2000|2000|0|0|0/0|2000|2000|2000|False|
|L2|2000|2000|0|0|0/0|2000|2000|2000|False|
|L3|2000|2000|0|0|0/0|2000|2000|2000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|item_id|0|0|0|0|
|asset_account_id|0|0|0|0|
|description|0|0|0|0|
|expense_account_id|0|0|0|0|
|fully_qualified_name|0|0|0|0|
|income_account_id|0|0|0|0|
|is_active|0|0|0|0|
|is_taxable|0|0|0|0|
|name|0|0|0|0|
|parent_item_id|0|0|0|0|
|purchase_cost|0|0|0|0|
|purchase_tax_code_id|0|0|0|0|
|quantity_on_hand|0|0|0|0|
|sales_tax_code_id|0|0|0|0|
|sku|0|0|0|0|
|sync_token|0|0|0|0|
|tax_code_id|2000|2000|2000|2000|
|track_quantity_on_hand|0|0|0|0|
|type|0|0|0|0|
|unit_price|0|0|0|0|

### 重跑 baseline

SQL：`data/016_work/impl-015/baseline.sql`；SHA-256：`c0ada8b03760b3d835713d578a891d863efedc7305a19dd80e4676ba1b56bc84`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|2000|2000|0|0|0/0|2000|2000|2000|False|
|L1|2000|2000|0|0|0/0|2000|2000|2000|False|
|L2|2000|2000|0|0|0/0|2000|2000|2000|False|
|L3|2000|2000|0|0|0/0|2000|2000|2000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|item_id|0|0|0|0|
|asset_account_id|0|0|0|0|
|description|0|0|0|0|
|expense_account_id|0|0|0|0|
|fully_qualified_name|0|0|0|0|
|income_account_id|0|0|0|0|
|is_active|0|0|0|0|
|is_taxable|0|0|0|0|
|name|0|0|0|0|
|parent_item_id|0|0|0|0|
|purchase_cost|0|0|0|0|
|purchase_tax_code_id|0|0|0|0|
|quantity_on_hand|0|0|0|0|
|sales_tax_code_id|0|0|0|0|
|sku|0|0|0|0|
|sync_token|0|0|0|0|
|tax_code_id|2000|2000|2000|2000|
|track_quantity_on_hand|0|0|0|0|
|type|0|0|0|0|
|unit_price|0|0|0|0|

### 重跑 tax_code_null

SQL：`data/016_work/impl-015/tax_code_null.sql`；SHA-256：`f104c75a050aadfa60b66bfc7e61b642379ae55eea4c7e8a0f278d4c845eaf2d`。

唯一原文位置offset=349，替换前：
```sql
CAST(r.sales_tax_code_id AS VARCHAR) AS "tax_code_id"
```
替换后：
```sql
CAST(NULL AS VARCHAR) AS "tax_code_id"
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
|item_id|0|0|0|0|
|asset_account_id|0|0|0|0|
|description|0|0|0|0|
|expense_account_id|0|0|0|0|
|fully_qualified_name|0|0|0|0|
|income_account_id|0|0|0|0|
|is_active|0|0|0|0|
|is_taxable|0|0|0|0|
|name|0|0|0|0|
|parent_item_id|0|0|0|0|
|purchase_cost|0|0|0|0|
|purchase_tax_code_id|0|0|0|0|
|quantity_on_hand|0|0|0|0|
|sales_tax_code_id|0|0|0|0|
|sku|0|0|0|0|
|sync_token|0|0|0|0|
|tax_code_id|0|0|0|0|
|track_quantity_on_hand|0|0|0|0|
|type|0|0|0|0|
|unit_price|0|0|0|0|

## 5. 类别、把握及与014对比

- 主要原因：**A**。
- 主因对应单项：tax_code_null。
- 参与因素：无：raw类型重建不是本列差异来源。
- 标记：无。
- 把握：**中**。
- 重跑是否满足U第4条件：是（tax_code_null单改L0整表一致；非U）。

两个税码不相等不能定下目标税码语义；NULL替换能匹配gold不是U证据。

与014相比：**不适用：第二批首次标注**

## 规则问题

2026-10-29用户确认补充：gold=初始≠agent属于运行留存侧改动，照常标注。此处是schema类型漂移而非删除/伪造原始行；明确区分原始初始库未改、留存库raw重建。

2026-10-29用户确认的第3节补充：仅当本表依赖raw满足agent留存=初始、gold不同，且诊断确认影响可评估性时标“不可评估”；gold=初始、agent不同则照常标注，查轨迹改动。不能把两类混为一谈。若gold与agent一致但二者不同于初始（019/020），当前本节点仍可比较；初始差异另记。

共同执行例外：最初指纹快照因外部v0附件已不在原桌面路径而失败；成功的016快照晚于首批私有重跑。已逐文件与015任务前的大小、mtime、SHA-256比较，覆盖原始库的历史指纹无变化；不把晚快照伪称执行前快照。仓库v0与004–015记录保留。
