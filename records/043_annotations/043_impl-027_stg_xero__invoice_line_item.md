# 043：impl-027_stg_xero__invoice_line_item

## 结论

主要原因：**其他**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为2483行/4937格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`O`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/staging/stg_xero__invoice_line_item.sql`；无SQL注释。材料包：`records/024_packages/024_impl-027_stg_xero__invoice_line_item.md`。

staging采用agent留存raw；013直接源对照逐项列出。

已逐张读取 `records/013_raw_impl-027.json`；与gold关系见 `records/015_raw_impl-027.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.xero_invoice_line_item_data`：initial 5000行/14列；agent留存 5000行/14列；013差异=False。

## 同源决定

同源决定：event 19，`/tmp/gen.py`：stages字典及写文件循环生成staging；金额与时间表达式按表分别列出。 目录编号：`027-stages`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 19，invoice_line_item投影按契约对五个数值字段统一CAST到DECIMAL(18,2)。 本表点：discount_rate, line_amount, quantity, tax_amount, unit_amount；编号 `027-line-numeric`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共1条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引26（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

## 点：discount_rate

类别：**其他**；角色：参与；把握：高。

discount_rate契约明确DECIMAL(18,2)，agent照做，gold保留DOUBLE/更多精度。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-027_stg_xero__invoice_line_item.json`，条目 `discount_rate`。

基线：L0=4984行/8620格; L1=4320行/4320格; L2=7行/7格; L3=7行/7格。

单改后：L0=4981行/8196格; L1=4320行/4320格; L2=7行/7格; L3=7行/7格。L0减量（先行后格）：3行/424格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "TRY_CAST(discount_rate AS DECIMAL(18, 2)) AS discount_rate",
    "new": "discount_rate AS discount_rate",
    "offset": 250
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
        - name: discount_entered_as_percent
          data_type: BOOLEAN
        - name: discount_rate
          data_type: DECIMAL(18,2)
        - name: item_code
          data_type: VARCHAR
        - name: line_amount
          data_type: DECIMAL(18,2)
        - name: quantity
          data_type: DECIMAL(18,2)
        - name: tax_amount
          data_type: DECIMAL(18,2)
        - name: tax_type
          data_type: VARCHAR
        - name: unit_amount
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `027-stages`；根源决定单元 `027-line-numeric`。

## 点：line_amount

类别：**其他**；角色：参与；把握：高。

line_amount契约明确DECIMAL(18,2)，agent照做，gold保留DOUBLE/更多精度。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-027_stg_xero__invoice_line_item.json`，条目 `line_amount`。

基线：L0=4984行/8620格; L1=4320行/4320格; L2=7行/7格; L3=7行/7格。

单改后：L0=4982行/7786格; L1=4320行/4320格; L2=7行/7格; L3=7行/7格。L0减量（先行后格）：2行/834格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "TRY_CAST(line_amount AS DECIMAL(18, 2)) AS line_amount",
    "new": "line_amount AS line_amount",
    "offset": 351
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
        - name: item_code
          data_type: VARCHAR
        - name: line_amount
          data_type: DECIMAL(18,2)
        - name: quantity
          data_type: DECIMAL(18,2)
        - name: tax_amount
          data_type: DECIMAL(18,2)
        - name: tax_type
          data_type: VARCHAR
        - name: unit_amount
          data_type: DECIMAL(18,2)
          validation_rules:
            - rule: "If unit_amount is NULL or not a numeric value with up to 2 decimals, delete row"
              on_failure: delete_row
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `027-stages`；根源决定单元 `027-line-numeric`。

## 点：quantity

类别：**其他**；角色：主要；把握：高。

quantity契约明确DECIMAL(18,2)，agent照做，gold保留DOUBLE/更多精度。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-027_stg_xero__invoice_line_item.json`，条目 `quantity`。

基线：L0=4984行/8620格; L1=4320行/4320格; L2=7行/7格; L3=7行/7格。

单改后：L0=2501行/3683格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：2483行/4937格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "TRY_CAST(quantity AS DECIMAL(18, 2)) AS quantity",
    "new": "quantity AS quantity",
    "offset": 411
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
        - name: line_amount
          data_type: DECIMAL(18,2)
        - name: quantity
          data_type: DECIMAL(18,2)
        - name: tax_amount
          data_type: DECIMAL(18,2)
        - name: tax_type
          data_type: VARCHAR
        - name: unit_amount
          data_type: DECIMAL(18,2)
          validation_rules:
            - rule: "If unit_amount is NULL or not a numeric value with up to 2 decimals, delete row"
              on_failure: delete_row
            - rule: "If unit_amount outside [-1000000, 1000000], delete row"
              on_failure: delete_row
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `027-stages`；根源决定单元 `027-line-numeric`。

## 点：tax_amount

类别：**其他**；角色：参与；把握：高。

tax_amount契约明确DECIMAL(18,2)，agent照做，gold保留DOUBLE/更多精度。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-027_stg_xero__invoice_line_item.json`，条目 `tax_amount`。

基线：L0=4984行/8620格; L1=4320行/4320格; L2=7行/7格; L3=7行/7格。

单改后：L0=4980行/7009格; L1=4320行/4320格; L2=7行/7格; L3=7行/7格。L0减量（先行后格）：4行/1611格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "TRY_CAST(tax_amount AS DECIMAL(18, 2)) AS tax_amount",
    "new": "tax_amount AS tax_amount",
    "offset": 465
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
        - name: quantity
          data_type: DECIMAL(18,2)
        - name: tax_amount
          data_type: DECIMAL(18,2)
        - name: tax_type
          data_type: VARCHAR
        - name: unit_amount
          data_type: DECIMAL(18,2)
          validation_rules:
            - rule: "If unit_amount is NULL or not a numeric value with up to 2 decimals, delete row"
              on_failure: delete_row
            - rule: "If unit_amount outside [-1000000, 1000000], delete row"
              on_failure: delete_row
        - name: processed_at
          data_type: TIMESTAMP
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `027-stages`；根源决定单元 `027-line-numeric`。

## 点：unit_amount

类别：**其他**；角色：参与；把握：高。

unit_amount契约明确DECIMAL(18,2)，agent照做，gold保留DOUBLE/更多精度。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-027_stg_xero__invoice_line_item.json`，条目 `unit_amount`。

基线：L0=4984行/8620格; L1=4320行/4320格; L2=7行/7格; L3=7行/7格。

单改后：L0=4983行/7806格; L1=4320行/4320格; L2=7行/7格; L3=7行/7格。L0减量（先行后格）：1行/814格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "TRY_CAST(unit_amount AS DECIMAL(18, 2)) AS unit_amount",
    "new": "unit_amount AS unit_amount",
    "offset": 558
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
        - name: tax_type
          data_type: VARCHAR
        - name: unit_amount
          data_type: DECIMAL(18,2)
          validation_rules:
            - rule: "If unit_amount is NULL or not a numeric value with up to 2 decimals, delete row"
              on_failure: delete_row
            - rule: "If unit_amount outside [-1000000, 1000000], delete row"
              on_failure: delete_row
        - name: processed_at
          data_type: TIMESTAMP
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `027-stages`；根源决定单元 `027-line-numeric`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
