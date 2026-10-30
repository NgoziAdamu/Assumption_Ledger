# impl-015 · stg_quickbooks__invoice_line

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**I**；把握：中；主要错误点：item_mapping。

初始映射使用 sales_item_item_id，后来的 special 映射将其覆盖成全空的 item_id。

参与因素：无。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-015_stg_quickbooks__invoice_line.md](../023_packages/023_impl-015_stg_quickbooks__invoice_line.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml`；SHA-256 `c7c31842035fff7336164f7713a735dde48f8f77e19e992d2dae072b0144c51a`。
契约行 352–406：

```
352:     - name: stg_quickbooks__invoice_line
353:       description: "Cleaned invoice line items with product details and amounts"
354:       source_table: "raw.invoice_line_data"
355:       columns:
356:         - name: invoice_id
357:           data_type: VARCHAR
358:           constraints: [not_null]
359:         - name: index
360:           data_type: INTEGER
361:           constraints: [not_null]
362:         - name: bundle_id
363:           data_type: VARCHAR
364:         - name: sales_item_item_id
365:           data_type: VARCHAR
366:         - name: sales_item_quantity
367:           data_type: DECIMAL(28,6)
368:         - name: sales_item_unit_price
369:           data_type: DECIMAL(28,6)
370:         - name: sales_item_account_id
371:           data_type: VARCHAR
372:         - name: sales_item_class_id
373:           data_type: VARCHAR
374:         - name: sales_item_tax_code_id
375:           data_type: VARCHAR
376:         - name: sales_item_discount_amount
377:           data_type: DECIMAL(28,6)
378:         - name: sales_item_discount_rate
379:           data_type: DECIMAL(28,6)
380:         - name: account_id
381:           data_type: VARCHAR
382:         - name: discount_account_id
383:           data_type: VARCHAR
384:         - name: discount_class_id
385:           data_type: VARCHAR
386:         - name: discount_tax_code_id
387:           data_type: VARCHAR
388:         - name: discount_percent
389:           data_type: DECIMAL(28,6)
390:         - name: discount_discount_amount
391:           data_type: DECIMAL(28,6)
392:         - name: group_line_detail_group_item_id
393:           data_type: VARCHAR
394:         - name: group_line_detail_quantity
395:           data_type: DECIMAL(28,6)
396:         - name: amount
397:           data_type: DECIMAL(28,6)
398:         - name: description
399:           data_type: VARCHAR
400:         - name: detail_type
401:           data_type: VARCHAR
402:         - name: source_relation
403:           data_type: VARCHAR
404:       filter_conditions:
405:         - "invoice_id is not null and index is not null"
406:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/sql/staging/stg_quickbooks__invoice_line.sql`，SHA-256 `d3e269add6bdbcea4f1b4755b5c8c067f281312ea7414a4fe6e66bcf30a92bed`，行 1–29。

```
1: WITH typed AS (
2:     SELECT
3:         CAST(r.invoice_id AS VARCHAR) AS "invoice_id",
4:         TRY_CAST(r.index AS INTEGER) AS "index",
5:         CAST(r.bundle_id AS VARCHAR) AS "bundle_id",
6:         CAST(r.item_id AS VARCHAR) AS "sales_item_item_id",
7:         TRY_CAST(r.sales_item_quantity AS DECIMAL(28,6)) AS "sales_item_quantity",
8:         TRY_CAST(r.sales_item_unit_price AS DECIMAL(28,6)) AS "sales_item_unit_price",
9:         CAST(r.sales_item_account_id AS VARCHAR) AS "sales_item_account_id",
10:         CAST(r.sales_item_class_id AS VARCHAR) AS "sales_item_class_id",
11:         CAST(r.sales_item_tax_code_id AS VARCHAR) AS "sales_item_tax_code_id",
12:         TRY_CAST(r.sales_item_discount_amount AS DECIMAL(28,6)) AS "sales_item_discount_amount",
13:         TRY_CAST(r.sales_item_discount_rate AS DECIMAL(28,6)) AS "sales_item_discount_rate",
14:         CAST(r.account_id AS VARCHAR) AS "account_id",
15:         CAST(r.discount_account_id AS VARCHAR) AS "discount_account_id",
16:         CAST(r.discount_class_id AS VARCHAR) AS "discount_class_id",
17:         CAST(r.discount_tax_code_id AS VARCHAR) AS "discount_tax_code_id",
18:         TRY_CAST(r.discount_discount_percent AS DECIMAL(28,6)) AS "discount_percent",
19:         CAST(NULL AS DECIMAL(28,6)) AS "discount_discount_amount",
20:         CAST(NULL AS VARCHAR) AS "group_line_detail_group_item_id",
21:         CAST(NULL AS DECIMAL(28,6)) AS "group_line_detail_quantity",
22:         TRY_CAST(r.amount AS DECIMAL(28,6)) AS "amount",
23:         CAST(r.description AS VARCHAR) AS "description",
24:         CAST(r.detail_type AS VARCHAR) AS "detail_type",
25:         'quickbooks' AS "source_relation"
26:     FROM raw.invoice_line_data AS r
27: )
28: SELECT * FROM typed
29: WHERE (invoice_id IS NOT NULL AND index IS NOT NULL)
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-015/sql/staging/stg_quickbooks__invoice_line.sql`，SHA-256 `13b6e7c6df51db567786aebeb6910ee4764d7b95d1622d47bf2995bb6f669a50`，行 1–105。

```
1: with source as (
2:     select *
3:     from raw.invoice_line_data
4: ),
5: 
6: renamed as (
7:     select
8:         -- IDs
9:         cast(invoice_id as varchar) as invoice_id,
10:         cast(index as integer) as index,
11:         cast(bundle_id as varchar) as bundle_id,
12: 
13:         -- Sales item fields
14:         cast(sales_item_item_id as varchar) as sales_item_item_id,
15:         cast(sales_item_quantity as decimal(28,6)) as sales_item_quantity,
16:         cast(sales_item_unit_price as decimal(28,6)) as sales_item_unit_price,
17:         cast(sales_item_account_id as varchar) as sales_item_account_id,
18:         cast(sales_item_class_id as varchar) as sales_item_class_id,
19:         cast(sales_item_tax_code_id as varchar) as sales_item_tax_code_id,
20:         cast(sales_item_discount_amount as decimal(28,6)) as sales_item_discount_amount,
21:         cast(sales_item_discount_rate as decimal(28,6)) as sales_item_discount_rate,
22: 
23:         -- Account fields
24:         cast(account_id as varchar) as account_id,
25: 
26:         -- Discount fields
27:         cast(discount_account_id as varchar) as discount_account_id,
28:         cast(discount_class_id as varchar) as discount_class_id,
29:         cast(discount_tax_code_id as varchar) as discount_tax_code_id,
30:         cast(discount_discount_percent as decimal(28,6)) as discount_percent,
31:         cast(null as decimal(28,6)) as discount_discount_amount,
32: 
33:         -- Group fields
34:         cast(null as varchar) as group_line_detail_group_item_id,
35:         cast(null as decimal(28,6)) as group_line_detail_quantity,
36: 
37:         -- Line details
38:         cast(amount as decimal(28,6)) as amount,
39:         cast(description as varchar) as description,
40:         cast(detail_type as varchar) as detail_type,
41: 
42:         -- System fields
43:         'main' as source_relation
44: 
45:     from source
46: )
47: 
48: select
49:     case when invoice_id is null then '' else invoice_id end as invoice_id,
50:     index,
51:     bundle_id,
52:     sales_item_item_id,
53:     case
54:         when cast(sales_item_quantity as decimal(28,6)) is not null and (cast(sales_item_quantity as decimal(28,6)) < -999999.99 or cast(sales_item_quantity as decimal(28,6)) > 999999.99)
55:         then null
56:         else cast(sales_item_quantity as decimal(28,6))
57:     end as sales_item_quantity,
58:     case
59:         when cast(sales_item_unit_price as decimal(28,6)) is not null and (cast(sales_item_unit_price as decimal(28,6)) < -999999.99 or cast(sales_item_unit_price as decimal(28,6)) > 999999.99)
60:         then null
61:         else cast(sales_item_unit_price as decimal(28,6))
62:     end as sales_item_unit_price,
63:     sales_item_account_id,
64:     sales_item_class_id,
65:     sales_item_tax_code_id,
66:     case
67:         when cast(sales_item_discount_amount as decimal(28,6)) is not null and (cast(sales_item_discount_amount as decimal(28,6)) < -999999.99 or cast(sales_item_discount_amount as decimal(28,6)) > 999999.99)
68:         then null
69:         else cast(sales_item_discount_amount as decimal(28,6))
70:     end as sales_item_discount_amount,
71:     case
72:         when cast(sales_item_discount_rate as decimal(28,6)) is not null and (cast(sales_item_discount_rate as decimal(28,6)) < -999999.99 or cast(sales_item_discount_rate as decimal(28,6)) > 999999.99)
73:         then null
74:         else cast(sales_item_discount_rate as decimal(28,6))
75:     end as sales_item_discount_rate,
76:     account_id,
77:     discount_account_id,
78:     discount_class_id,
79:     discount_tax_code_id,
80:     case
81:         when cast(discount_percent as decimal(28,6)) is not null and (cast(discount_percent as decimal(28,6)) < -999999.99 or cast(discount_percent as decimal(28,6)) > 999999.99)
82:         then null
83:         else cast(discount_percent as decimal(28,6))
84:     end as discount_percent,
85:     case
86:         when cast(discount_discount_amount as decimal(28,6)) is not null and (cast(discount_discount_amount as decimal(28,6)) < -999999.99 or cast(discount_discount_amount as decimal(28,6)) > 999999.99)
87:         then null
88:         else cast(discount_discount_amount as decimal(28,6))
89:     end as discount_discount_amount,
90:     group_line_detail_group_item_id,
91:     case
92:         when cast(group_line_detail_quantity as decimal(28,6)) is not null and (cast(group_line_detail_quantity as decimal(28,6)) < -999999.99 or cast(group_line_detail_quantity as decimal(28,6)) > 999999.99)
93:         then null
94:         else cast(group_line_detail_quantity as decimal(28,6))
95:     end as group_line_detail_quantity,
96:     case
97:         when cast(amount as decimal(28,6)) is not null and (cast(amount as decimal(28,6)) < -999999.99 or cast(amount as decimal(28,6)) > 999999.99)
98:         then null
99:         else cast(amount as decimal(28,6))
100:     end as amount,
101:     description,
102:     detail_type,
103:     source_relation
104: from renamed
105: where invoice_id is not null and index is not null
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 15/16 看过两候选列；event 17 rawmap 先写 sales_item_item_id→sales_item_item_id；event 21 special 覆盖为 item_id，未解释本表选择。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/15.json`。
- event 16：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/16.json`。
- event 17：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/17.json`。
- event 21：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/21.json`。
## 查询

核实查询 **3** 条；核实代价档：**多条查询**。诊断查询不计入 5 条上限。

计数保守包含最初额外 2 条结构/少量样例查看。该探索未保留完整返回，不作为分类证据；下列聚合查询独立给出判断所需证据。

### 核实：选列有效性

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/quickbooks.duckdb`。

```sql
SELECT count(*) n,count(item_id) item_id_nonnull,count(sales_item_item_id) sales_item_nonnull,count(*) FILTER(WHERE sales_item_item_id IN(SELECT id FROM raw.item_data)) sales_item_matches FROM raw.invoice_line_data
```


```json
{"columns":["n","item_id_nonnull","sales_item_nonnull","sales_item_matches"],"rows":[[20000,0,20000,20000]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-015_stg_quickbooks__invoice_line.json](../023_reruns_impl-015_stg_quickbooks__invoice_line.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/quickbooks.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|20000|20000|40000|760000|否|
|L1|20000|20000|40000|760000|否|
|L2|20000|20000|40000|760000|否|
|L3|20000|20000|40000|760000|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"invoice_id":40000,"bundle_id":40000,"sales_item_item_id":40000,"sales_item_account_id":40000,"sales_item_class_id":40000,"sales_item_tax_code_id":40000,"account_id":40000,"discount_account_id":40000,"discount_class_id":40000,"discount_tax_code_id":40000,"group_line_detail_group_item_id":40000,"amount":40000,"description":40000,"detail_type":40000,"index":40000,"sales_item_discount_amount":40000,"sales_item_discount_rate":40000,"sales_item_quantity":40000,"sales_item_unit_price":40000}`
- L1：`{"invoice_id":40000,"bundle_id":40000,"sales_item_item_id":40000,"sales_item_account_id":40000,"sales_item_class_id":40000,"sales_item_tax_code_id":40000,"account_id":40000,"discount_account_id":40000,"discount_class_id":40000,"discount_tax_code_id":40000,"group_line_detail_group_item_id":40000,"amount":40000,"description":40000,"detail_type":40000,"index":40000,"sales_item_discount_amount":40000,"sales_item_discount_rate":40000,"sales_item_quantity":40000,"sales_item_unit_price":40000}`
- L2：`{"invoice_id":40000,"bundle_id":40000,"sales_item_item_id":40000,"sales_item_account_id":40000,"sales_item_class_id":40000,"sales_item_tax_code_id":40000,"account_id":40000,"discount_account_id":40000,"discount_class_id":40000,"discount_tax_code_id":40000,"group_line_detail_group_item_id":40000,"amount":40000,"description":40000,"detail_type":40000,"index":40000,"sales_item_discount_amount":40000,"sales_item_discount_rate":40000,"sales_item_quantity":40000,"sales_item_unit_price":40000}`
- L3：`{"invoice_id":40000,"bundle_id":40000,"sales_item_item_id":40000,"sales_item_account_id":40000,"sales_item_class_id":40000,"sales_item_tax_code_id":40000,"account_id":40000,"discount_account_id":40000,"discount_class_id":40000,"discount_tax_code_id":40000,"group_line_detail_group_item_id":40000,"amount":40000,"description":40000,"detail_type":40000,"index":40000,"sales_item_discount_amount":40000,"sales_item_discount_rate":40000,"sales_item_quantity":40000,"sales_item_unit_price":40000}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-015_stg_quickbooks__invoice_line/baseline.sql`；SHA-256 `d3e269add6bdbcea4f1b4755b5c8c067f281312ea7414a4fe6e66bcf30a92bed`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|20000|20000|40000|760000|否|
|L1|20000|20000|40000|760000|否|
|L2|20000|20000|40000|760000|否|
|L3|20000|20000|40000|760000|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"invoice_id":40000,"bundle_id":40000,"sales_item_item_id":40000,"sales_item_account_id":40000,"sales_item_class_id":40000,"sales_item_tax_code_id":40000,"account_id":40000,"discount_account_id":40000,"discount_class_id":40000,"discount_tax_code_id":40000,"group_line_detail_group_item_id":40000,"amount":40000,"description":40000,"detail_type":40000,"index":40000,"sales_item_discount_amount":40000,"sales_item_discount_rate":40000,"sales_item_quantity":40000,"sales_item_unit_price":40000}`
- L1：`{"invoice_id":40000,"bundle_id":40000,"sales_item_item_id":40000,"sales_item_account_id":40000,"sales_item_class_id":40000,"sales_item_tax_code_id":40000,"account_id":40000,"discount_account_id":40000,"discount_class_id":40000,"discount_tax_code_id":40000,"group_line_detail_group_item_id":40000,"amount":40000,"description":40000,"detail_type":40000,"index":40000,"sales_item_discount_amount":40000,"sales_item_discount_rate":40000,"sales_item_quantity":40000,"sales_item_unit_price":40000}`
- L2：`{"invoice_id":40000,"bundle_id":40000,"sales_item_item_id":40000,"sales_item_account_id":40000,"sales_item_class_id":40000,"sales_item_tax_code_id":40000,"account_id":40000,"discount_account_id":40000,"discount_class_id":40000,"discount_tax_code_id":40000,"group_line_detail_group_item_id":40000,"amount":40000,"description":40000,"detail_type":40000,"index":40000,"sales_item_discount_amount":40000,"sales_item_discount_rate":40000,"sales_item_quantity":40000,"sales_item_unit_price":40000}`
- L3：`{"invoice_id":40000,"bundle_id":40000,"sales_item_item_id":40000,"sales_item_account_id":40000,"sales_item_class_id":40000,"sales_item_tax_code_id":40000,"account_id":40000,"discount_account_id":40000,"discount_class_id":40000,"discount_tax_code_id":40000,"group_line_detail_group_item_id":40000,"amount":40000,"description":40000,"detail_type":40000,"index":40000,"sales_item_discount_amount":40000,"sales_item_discount_rate":40000,"sales_item_quantity":40000,"sales_item_unit_price":40000}`

#### item_mapping

判定：主因；类别候选 I。item_id 全空，候选 sales_item_item_id 有值；核实其与商品主表关系后判定。

相对本轮基线减少行 40000、格 760000；按行优先、格次之排序。
共同控制后 SQL 第 6 行起、字符 offset 192 的唯一连续替换；其余字节不动。
替换前：
```sql
CAST(r.item_id AS VARCHAR)
```

替换后：
```sql
CAST(r.sales_item_item_id AS VARCHAR)
```

私有 SQL：`data/023_work/impl-015_stg_quickbooks__invoice_line/item_mapping.sql`；SHA-256 `e83aff9716e213e9791094d657d4892d843dbcedc037c42dff9859d5f5a0ddf1`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|20000|20000|0|0|是|
|L1|20000|20000|0|0|是|
|L2|20000|20000|0|0|是|
|L3|20000|20000|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 原始表改动核对

event 39/40、43/44 报告 Unique file handle conflict；event45 改为 fetchdf/register/CREATE TABLE 导入，event46 成功。raw 类型改变但本次相关 invoice/vendor 表内容哈希相同。

初始/gold 一致而 agent 有变化，依第 3 节照常标注，不标不可评估。完整表清单见 [023_raw_trace_review.json](../023_raw_trace_review.json)；输入不变性另由前后指纹验证。

## 规则问题

I/U 两种读法：若把 special 映射视为有意选列，可读作 U；本次依手册允许的代码自身证据（正确映射随后被覆盖）选 I。核实所选列0/20000非空、另一列20000/20000且全部匹配 item_data。
