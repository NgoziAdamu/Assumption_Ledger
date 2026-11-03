# 043：impl-027_stg_xero__journal

## 结论

主要原因：**其他**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为0行/3500格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`O`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/staging/stg_xero__journal.sql`；无SQL注释。材料包：`records/024_packages/024_impl-027_stg_xero__journal.md`。

staging采用agent留存raw；013直接源对照逐项列出。

已逐张读取 `records/013_raw_impl-027.json`；与gold关系见 `records/015_raw_impl-027.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.xero_journal_data`：initial 3500行/7列；agent留存 3500行/7列；013差异=False。

## 同源决定

同源决定：event 19，`/tmp/gen.py`：stages字典及写文件循环生成staging；金额与时间表达式按表分别列出。 目录编号：`027-stages`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共1条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引27（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 诊断 `agent实际类型`：`records/024_diagnostics.json` 数组索引16（从0开始）。

- 诊断 `agent有限差异样例`：`records/024_diagnostics.json` 数组索引17（从0开始）。

- 诊断 `gold实际类型`：`records/024_diagnostics.json` 数组索引18（从0开始）。

- 诊断 `gold有限差异样例`：`records/024_diagnostics.json` 数组索引19（从0开始）。

- 诊断 `gold SQL同gold输入重跑`：`records/024_diagnostics.json` 数组索引33（从0开始）。

## 点：processed_at

类别：**Unstated Choice**；角色：非原因；把握：中。

raw没有处理时间列，规格只声明TIMESTAMP，NULL或执行时刻未规定。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-027_stg_xero__journal.json`，条目 `processed_at`。

基线：L0=3500行/7002格; L1=3500行/7002格; L2=3500行/7002格; L3=3500行/3502格。

单改后：L0=3500行/7002格; L1=3500行/7002格; L2=3500行/7002格; L3=3500行/3502格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "NULL::TIMESTAMP AS processed_at",
    "new": "TIMESTAMPTZ '2025-10-17 11:30:22.865253+08:00' AS processed_at",
    "offset": 575
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第2档——交付物里只有通用说明**。some entities未点名journal，缺失processed_at填NULL只有通用说明。

event 41 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
Raw data does not provide a processing timestamp for some entities, so `processed_at` is NULL where unavailable.
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
        - name: source_type
          data_type: VARCHAR
        - name: processed_at
          data_type: TIMESTAMP
```


共同生成动作 `027-stages`；根源决定单元 `impl-027_stg_xero__journal:processed_at`。

## 点：created_date_type

类别：**其他**；角色：并列；把握：高。

契约要求TIMESTAMP，agent转换；gold保留含UTC后缀的原文本。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-027_stg_xero__journal.json`，条目 `created_date_type`。

基线：L0=3500行/7002格; L1=3500行/7002格; L2=3500行/7002格; L3=3500行/3502格。

单改后：L0=3500行/3502格; L1=3500行/3502格; L2=3500行/3502格; L3=2行/2格。L0减量（先行后格）：0行/3500格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "TRY_CAST(created_date_utc AS TIMESTAMP) AS created_date_utc",
    "new": "created_date_utc AS created_date_utc",
    "offset": 50
  }
]
```

是否说出：**第2档——交付物里只有通用说明**。源时间字符串转换有明确通用说明，未逐表点名。

event 41 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
Available source timestamp strings are parsed with DuckDB `TRY_CAST`; invalid timestamps become NULL.
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
            - rule: "journal_id is present"
              on_failure: delete_row
        - name: created_date_utc
          data_type: TIMESTAMP
        - name: journal_date
          data_type: TIMESTAMP
        - name: journal_number
          data_type: INT
          validation_rules:
            - rule: "Remove alphabetic and special characters; if result empty or > 9,999,999, set to NULL"
              on_failure: nullify_field
        - name: reference
          data_type: VARCHAR
        - name: source_id
          data_type: VARCHAR
```


共同生成动作 `027-stages`；根源决定单元 `impl-027_stg_xero__journal:created_date_type`。

## 点：journal_date_type

类别：**其他**；角色：并列；把握：高。

契约要求TIMESTAMP，agent转换；gold保留日期字符串。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-027_stg_xero__journal.json`，条目 `journal_date_type`。

基线：L0=3500行/7002格; L1=3500行/7002格; L2=3500行/7002格; L3=3500行/3502格。

单改后：L0=3500行/3502格; L1=3500行/3502格; L2=3500行/3502格; L3=3500行/3502格。L0减量（先行后格）：0行/3500格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "TRY_CAST(journal_date AS TIMESTAMP) AS journal_date",
    "new": "journal_date AS journal_date",
    "offset": 115
  }
]
```

是否说出：**第2档——交付物里只有通用说明**。源时间字符串转换有明确通用说明，未逐表点名。

event 41 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
Available source timestamp strings are parsed with DuckDB `TRY_CAST`; invalid timestamps become NULL.
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
        - name: created_date_utc
          data_type: TIMESTAMP
        - name: journal_date
          data_type: TIMESTAMP
        - name: journal_number
          data_type: INT
          validation_rules:
            - rule: "Remove alphabetic and special characters; if result empty or > 9,999,999, set to NULL"
              on_failure: nullify_field
        - name: reference
          data_type: VARCHAR
        - name: source_id
          data_type: VARCHAR
        - name: source_type
          data_type: VARCHAR
```


共同生成动作 `027-stages`；根源决定单元 `impl-027_stg_xero__journal:journal_date_type`。

## 点：invalid_prefix

类别：**其他**；角色：参与；把握：高。

契约明确移除字母/特殊符号后保留有效数字；agent照做，gold额外将INVALID/BAD前缀置NULL。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_supplement_reruns_impl-027_stg_xero__journal.json`，条目 `invalid_prefix`。

基线：L0=3500行/7002格; L1=3500行/7002格; L2=3500行/7002格; L3=3500行/3502格。

单改后：L0=3500行/7000格; L1=3500行/7000格; L2=3500行/7000格; L3=3500行/3500格。L0减量（先行后格）：0行/2格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "    CASE\n        WHEN TRY_CAST(NULLIF(regexp_replace(coalesce(journal_number, ''), '[^0-9]', '', 'g'), '') AS BIGINT) <= 9999999\n            THEN TRY_CAST(NULLIF(regexp_replace(coalesce(journal_number, ''), '[^0-9]', '', 'g'), '') AS INTEGER)\n        ELSE NULL\n    END",
    "new": "    CASE WHEN journal_number LIKE 'INVALID%' OR journal_number LIKE 'BAD%' THEN NULL ELSE CASE\n        WHEN TRY_CAST(NULLIF(regexp_replace(coalesce(journal_number, ''), '[^0-9]', '', 'g'), '') AS BIGINT) <= 9999999\n            THEN TRY_CAST(NULLIF(regexp_replace(coalesce(journal_number, ''), '[^0-9]', '', 'g'), '') AS INTEGER)\n        ELSE NULL\n    END END",
    "offset": 168
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/output.jsonl`：

```text
        - name: journal_date
          data_type: TIMESTAMP
        - name: journal_number
          data_type: INT
          validation_rules:
            - rule: "Remove alphabetic and special characters; if result empty or > 9,999,999, set to NULL"
              on_failure: nullify_field
        - name: reference
          data_type: VARCHAR
        - name: source_id
          data_type: VARCHAR
        - name: source_type
          data_type: VARCHAR
        - name: processed_at
          data_type: TIMESTAMP
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `027-stages`；根源决定单元 `impl-027_stg_xero__journal:invalid_prefix`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
