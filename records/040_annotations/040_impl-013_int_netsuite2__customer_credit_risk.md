# 040 正式标注：impl-013_int_netsuite2__customer_credit_risk

## 任务

按冻结v3.2第3～8节逐点重标；层：intermediate。022旧主要原因仅原样存档为 `C`，不作为新类别依据。

## 结论

主要原因：**Intent Misreading**；把握高；共3个点。不是只能组合修复。

并列项：zero_total_receivables（Intent Misreading）；zero_total_collections（Intent Misreading）；zero_outstanding_receivables（Intent Misreading）

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### zero_total_receivables

并列；**Intent Misreading**；把握高。

相关列描述always populated并有非空要求；空类别SUM FILTER返回NULL不符合此要求。依据非空明文，不能声称契约直接给了SUM CASE表达式。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。

曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 115 | 115 | 345 | 230 |
| L1 | 115 | 115 | 345 | 230 |
| L2 | 115 | 115 | 345 | 230 |
| L3 | 115 | 115 | 345 | 230 |



来源：`records/022_reruns_impl-013_int_netsuite2__customer_credit_risk.json` / `zero_total_receivables`。L0减少0行、115格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

        description: Sum of absolute converted_amount for Receivable transactions; always populated.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

        description: Sum of absolute converted_amount for Receivable transactions; always populated.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_credit_risk.sql` / `text`（sql；普通SQL表达式不是披露）

```text

sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctRec','Accounts Receivable')) total_receivables

```

### zero_total_collections

并列；**Intent Misreading**；把握高。

Payment类别没有行时SUM FILTER得到NULL；列描述要求always populated。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。

曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 115 | 115 | 345 | 230 |
| L1 | 115 | 115 | 345 | 230 |
| L2 | 115 | 115 | 345 | 230 |
| L3 | 115 | 115 | 345 | 230 |



来源：`records/022_reruns_impl-013_int_netsuite2__customer_credit_risk.json` / `zero_total_collections`。L0减少0行、115格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

        description: Sum of absolute converted_amount for Payment transactions; always populated.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

        description: Sum of absolute converted_amount for Payment transactions; always populated.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_credit_risk.sql` / `text`（sql；普通SQL表达式不是披露）

```text

sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Bank') total_collections

```

### zero_outstanding_receivables

并列；**Intent Misreading**；把握高。

Outstanding类别无行时输出NULL，违反该列always populated的明文。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。

曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 115 | 115 | 345 | 230 |
| L1 | 115 | 115 | 345 | 230 |
| L2 | 115 | 115 | 345 | 230 |
| L3 | 115 | 115 | 345 | 230 |



来源：`records/022_reruns_impl-013_int_netsuite2__customer_credit_risk.json` / `zero_outstanding_receivables`。L0减少0行、115格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

        description: Sum of absolute converted_amount where collection_status is Outstanding; always populated.

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

        description: Sum of absolute converted_amount where collection_status is Outstanding; always populated.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_credit_risk.sql` / `text`（sql；普通SQL表达式不是披露）

```text

sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctRec','Accounts Receivable')) outstanding_receivables

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`；行段[[1868, 2042]]；SHA-256 `c152a30bcad4df785d3f0ea461101eb8a4b36e4fa06059739a80e04998c4150f`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_credit_risk.sql`；SHA-256 `488eab6d2983029f3cfd1ad174adf2c8cec14d974d580bcf60872d9b173ded74`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json`；材料包：`records/022_packages/022_impl-013_int_netsuite2__customer_credit_risk.md`。

- 基线源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 1}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共2条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 12；上游可见行数；失败=True。

  - `records/022_queries_retry.json` / index 8；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

官方comparison_columns仅覆盖已列的14列及键；其他契约评分/风险列未进入本次比较。这里只对官方判错范围及已诊断点归因，不将未比较的契约缺口虚填成差异规模。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
