# 042 正式标注：impl-015_stg_quickbooks__invoice_line

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**代码写错**；把握中；1点。只能组合修复：否。023旧主要原因`I`仅存档。

## 详细发现

### 比较口径与原始数据

013显示30张raw列/类型不同，行数均未变。event45为解决同库重复ATTACH的Unique file handle conflict，改用fetchdf/register复制raw；这是agent改动，照常标注。直接源按下面逐表检查；CS表使用gold上游，不将本题全部raw变化归给该表。

直接raw逐表013核对：`[{"table": "invoice_line_data", "found_in_013": true, "different": true, "columns_types_equal": false, "row_counts_equal": true}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/quickbooks.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### item_mapping

**代码写错**；主要；把握中。

event17 rawmap明确写 sales_item_item_id→sales_item_item_id，event21 special映射覆盖成item_id，最终SQL取后者。复用核实显示item_id全空，sales_item_item_id有20000值且全部匹配item表。按手册第6节“同一个映射里先写正确列，后被覆盖”的直接代码证据判代码写错；不拿旧标签定类。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event17已有正确同名映射，event21 special覆盖，未解释差别或点出冲突；这是第4档，不把前后代码变化本身自动算意识到疑问。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-015_stg_quickbooks__invoice_line.json` / `item_mapping`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 40000 | 0 | 760000 | 0 |
| L1 | 40000 | 0 | 760000 | 0 |
| L2 | 40000 | 0 | 760000 | 0 |
| L3 | 40000 | 0 | 760000 | 0 |

L0减少：[40000, 760000]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml` / `text`。

```text
- name: sales_item_item_id
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/1.json` / event 1 / `message`。

```text
- name: sales_item_item_id
          data_type: VARCHAR
```

原句（correct_mapping）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/17.json` / event 17 / `args.command`。

```text
'sales_item_item_id':'sales_item_item_id'
```

原句（overriding_mapping）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/21.json` / event 21 / `args.command`。

```text
'sales_item_item_id':'item_id'
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/sql/staging/stg_quickbooks__invoice_line.sql` / `text`。

```text
CAST(r.item_id AS VARCHAR)
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml`；SHA-256 `c7c31842035fff7336164f7713a735dde48f8f77e19e992d2dae072b0144c51a`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/sql/staging/stg_quickbooks__invoice_line.sql`；SHA-256 `d3e269add6bdbcea4f1b4755b5c8c067f281312ea7414a4fe6e66bcf30a92bed`。
- 023材料包：`records/023_packages/023_impl-015_stg_quickbooks__invoice_line.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引0，选列有效性。

## 不确定或没查到的（含规则问题）

invoice_line：有正确映射再被special覆盖的直接代码证据，按第6节代码写错。若把special看作有意重解字段，可读成Data；轨迹没有解释该重解。本轮用可见的先正确后覆盖证据，把握中。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
