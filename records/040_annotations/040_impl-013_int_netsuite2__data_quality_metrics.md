# 040 正式标注：impl-013_int_netsuite2__data_quality_metrics

## 任务

按冻结v3.2第3～8节逐点重标；层：intermediate。022旧主要原因仅原样存档为 `A`，不作为新类别依据。

## 结论

主要原因：**Unstated Choice**；把握中；共3个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### accuracy_rules

参与；**已说出的降级**；把握高。

accuracy_score固定100，未计算契约的4项合规率；恢复该输出并沿原计算链重算总分/等级。finish一一对应数据质量模型说明业务规则合规率未完整验证，记已说出的降级。

是否说出：第1档——交付物里针对本处说明了。“数据质量模型”一一对应本表，并明确业务规则逐条合规率未完整验证；这覆盖本表accuracy_score的计算缺口，不推广到其他NetSuite指标。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 6 | 82 | 78 |
| L1 | 7 | 6 | 82 | 78 |
| L2 | 7 | 6 | 82 | 78 |
| L3 | 7 | 6 | 82 | 78 |



来源：`records/022_reruns_impl-013_int_netsuite2__data_quality_metrics.json` / `accuracy_rules`。L0减少1行、4格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

accuracy_score = average compliance_percentage across business_rule_validations.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

accuracy_score = average compliance_percentage across business_rule_validations.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/65.json` / `args.final_thought` / event 65（delivery；普通SQL表达式不是披露）

```text

数据质量模型输出总体报告、表统计和引用完整性检查；由于合同缺少可直接复用的完整业务规则细节实现，业务规则精确逐条合规率在该报告中未得到完整验证。将报告用于正式审计时应考虑这一限制。

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__data_quality_metrics.sql` / `text`（sql；普通SQL表达式不是披露）

```text

100.0 AS accuracy_score

```

### customer_counts

非原因；**Intent Misreading**；把握高。

Customers Date Range契约明确使用distinct company_name/email计数，agent用了NULL数。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。

曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 7 | 82 | 82 |
| L1 | 7 | 7 | 82 | 82 |
| L2 | 7 | 7 | 82 | 82 |
| L3 | 7 | 7 | 82 | 82 |



来源：`records/022_reruns_impl-013_int_netsuite2__data_quality_metrics.json` / `customer_counts`。L0减少0行、0格。

非原因说明：存在未确立的前提，但不是判错原因

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

Customers: "Date Range: {unique_names} to {unique_emails}" (distinct counts occupying those positions).

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

Customers: "Date Range: {unique_names} to {unique_emails}" (distinct counts occupying those positions).

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__data_quality_metrics.sql` / `text`（sql；普通SQL表达式不是披露）

```text

ELSE 'Date Range: ' || null_dates || ' to ' || null_entities

```

### table_label

主要；**Unstated Choice**；把握中。

table_name未定义字面赋值，简名和全限定名都可读；该名称同时参与MD5，故是键值生成选择，不能只当文字形式。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 2 | 82 | 5 |
| L1 | 7 | 2 | 82 | 5 |
| L2 | 7 | 2 | 82 | 5 |
| L3 | 7 | 2 | 82 | 5 |



来源：`records/022_reruns_impl-013_int_netsuite2__data_quality_metrics.json` / `table_label`。L0减少5行、77格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

metric columns not applicable are null; assessment_timestamp = check_timestamp; quality_assessment_id = MD5 of table_name concatenated with check_timestamp as text.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

metric columns not applicable are null; assessment_timestamp = check_timestamp; quality_assessment_id = MD5 of table_name concatenated with check_timestamp as text.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__data_quality_metrics.sql` / `text`（sql；普通SQL表达式不是披露）

```text

table_name::VARCHAR AS quality_grade

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__data_quality_metrics.sql` / `text`（sql；普通SQL表达式不是披露）

```text

md5(table_name || cast(current_timestamp AS VARCHAR))

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`；行段[[2114, 2167]]；SHA-256 `c152a30bcad4df785d3f0ea461101eb8a4b36e4fa06059739a80e04998c4150f`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__data_quality_metrics.sql`；SHA-256 `74f21eac1db427376a7f18c3e84b6070062c80a1a05576cc7184acefff76d2ee`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json`；材料包：`records/022_packages/022_impl-013_int_netsuite2__data_quality_metrics.md`。

- 基线源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 10:20:49.607+08'", "count": 5}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共2条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 13；上游可见行数；失败=True。

  - `records/022_queries_retry.json` / index 9；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
