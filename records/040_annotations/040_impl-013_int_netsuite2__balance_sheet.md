# 040 正式标注：impl-013_int_netsuite2__balance_sheet

## 任务

按冻结v3.2第3～8节逐点重标；层：intermediate。022旧主要原因仅原样存档为 `A`，不作为新类别依据。

## 结论

主要原因：**Unstated Choice**；把握中；共4个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### cta_branch

参与；**Intent Misreading**；把握高。

契约明确每条驱动交易再UNION ALL一条CTA；agent只输出主分支，遗漏规定的行范围。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。

曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 826 | 438 | 18172 | 9636 |
| L1 | 826 | 438 | 18172 | 9636 |
| L2 | 826 | 438 | 18172 | 9636 |
| L3 | 826 | 438 | 18172 | 9636 |



来源：`records/022_reruns_impl-013_int_netsuite2__balance_sheet.json` / `cta_branch`。L0减少388行、8536格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

Union all a second row per included transaction line to represent Cumulative Translation Adjustment (CTA):

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

Union all a second row per included transaction line to represent Cumulative Translation Adjustment (CTA):

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__balance_sheet.sql` / `text`（sql；普通SQL表达式不是披露）

```text

FROM presented

```

### key_null

主要；**Unstated Choice**；把握中。

MD5拼接规则给coalesced account_id，但没有指定NULL替代常量；空串和0产生不同键，按未定选择而非Form。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 826 | 388 | 18172 | 8536 |
| L1 | 826 | 388 | 18172 | 8536 |
| L2 | 826 | 388 | 18172 | 8536 |
| L3 | 826 | 388 | 18172 | 8536 |



来源：`records/022_reruns_impl-013_int_netsuite2__balance_sheet.json` / `key_null`。L0减少438行、9636格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

Create balance_sheet_id by concatenating transaction_line_id, transaction_id, accounting_period_id, account_name, and coalesced account_id using "_" as a delimiter and hashing the result with MD5 to produce a deterministic unique identifier.'

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

Create balance_sheet_id by concatenating transaction_line_id, transaction_id, accounting_period_id, account_name, and coalesced account_id using "_" as a delimiter and hashing the result with MD5 to produce a deterministic unique identifier.'

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__balance_sheet.sql` / `text`（sql；普通SQL表达式不是披露）

```text

coalesce(CASE WHEN is_balancesheet THEN account_id END,'')

```

### account_type_id

非原因；**Form Mismatch**；把握高。

普通balance-sheet账户类型ID应保持accounts.type_name，agent统一lower/空格下划线；这是规定标签的形式差异，不改变账户归属。当前被不同键/缺CTA遮住。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 826 | 826 | 18172 | 18172 |
| L1 | 826 | 826 | 18172 | 18172 |
| L2 | 826 | 826 | 18172 | 18172 |
| L3 | 826 | 826 | 18172 | 18172 |



来源：`records/022_reruns_impl-013_int_netsuite2__balance_sheet.json` / `account_type_id`。L0减少0行、0格。

非原因说明：此实现/形式差异已定位，但单改不减少当前判错规模；不计参与因素。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

Else → account_name/display come from accounts.name; for type_name: map lower(type_name)=''retearnings'' to "Retained Earnings", lower(type_name) in (''cta-e'',''cumultransadj'') to "Cumulative Translation Adjustment", otherwise use accounts.type_name; for account_type_id apply the same mappings to ''retained_earnings'' and ''cumulative_translation_adjustment'', otherwise use accounts.type_name.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

Else → account_name/display come from accounts.name; for type_name: map lower(type_name)=''retearnings'' to "Retained Earnings", lower(type_name) in (''cta-e'',''cumultransadj'') to "Cumulative Translation Adjustment", otherwise use accounts.type_name; for account_type_id apply the same mappings to ''retained_earnings'' and ''cumulative_translation_adjustment'', otherwise use accounts.type_name.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__balance_sheet.sql` / `text`（sql；普通SQL表达式不是披露）

```text

lower(replace(out_type,' ', '_'))

```

### rate_selection

非原因；**Intent Misreading**；把握高。

契约按general_rate_type选交易期或报告期金额；agent用COALESCE优先交易期，偏离给定算法。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。

曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 826 | 826 | 18172 | 18172 |
| L1 | 826 | 826 | 18172 | 18172 |
| L2 | 826 | 826 | 18172 | 18172 |
| L3 | 826 | 826 | 18172 | 18172 |



来源：`records/022_reruns_impl-013_int_netsuite2__balance_sheet.json` / `rate_selection`。L0减少0行、0格。

非原因说明：存在未确立的前提，但不是判错原因

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

Non-balance-sheet: use a negative sign; use transaction accounting period for historical/average rates, otherwise use reporting month.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

Non-balance-sheet: use a negative sign; use transaction accounting period for historical/average rates, otherwise use reporting month.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__balance_sheet.sql` / `text`（sql；普通SQL表达式不是披露）

```text

CASE WHEN NOT is_balancesheet OR is_leftside IS FALSE THEN -coalesce(converted_amount_using_transaction_accounting_period, converted_amount_using_reporting_month) ELSE coalesce(converted_amount_using_transaction_accounting_period, converted_amount_using_reporting_month) END AS converted_amount

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`；行段[[1277, 1362]]；SHA-256 `c152a30bcad4df785d3f0ea461101eb8a4b36e4fa06059739a80e04998c4150f`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__balance_sheet.sql`；SHA-256 `7a8a68abcafcc6c720519326892520dd557807837d6a28b3b7b4794e6d37fe26`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json`；材料包：`records/022_packages/022_impl-013_int_netsuite2__balance_sheet.md`。

- 基线源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共2条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 11；上游可见行数；失败=True。

  - `records/022_queries_retry.json` / index 7；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
