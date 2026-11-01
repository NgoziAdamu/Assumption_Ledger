# 040 正式标注：impl-013_int_netsuite2__financial_ratios

## 任务

按冻结v3.2第3～8节逐点重标；层：intermediate。022旧主要原因仅原样存档为 `C`，不作为新类别依据。

## 结论

主要原因：**Unstated Choice**；把握中；共5个点。不是只能组合修复。

并列项：zero_total_current_liabilities（Unstated Choice）；zero_accounts_receivable（Unstated Choice）

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### zero_total_current_assets

参与；**Unstated Choice**；把握中。

完整本表契约仅规定按类别求和，没有always populated、not_null或空类别补0的条款。SUM FILTER的NULL和CASE ELSE 0的零值是材料未定的空集处理选择；不沿用022的“契约明确SUM CASE ELSE 0”表述。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 13 | 13 | 49 | 39 |
| L1 | 13 | 13 | 49 | 39 |
| L2 | 13 | 13 | 49 | 39 |
| L3 | 13 | 13 | 49 | 39 |



来源：`records/022_reruns_impl-013_int_netsuite2__financial_ratios.json` / `zero_total_current_assets`。L0减少0行、10格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: total_current_assets
        data_type: DOUBLE
        description: Sum of period_balance for account types Bank, AcctRec, UnbilledRec, OthCurrAsset in the latest global period (signed as stored)

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: total_current_assets
        data_type: DOUBLE
        description: Sum of period_balance for account types Bank, AcctRec, UnbilledRec, OthCurrAsset in the latest global period (signed as stored)

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__financial_ratios.sql` / `text`（sql；普通SQL表达式不是披露）

```text

sum(period_balance) FILTER(WHERE account_type_name IN ('Bank','AcctRec','UnbilledRec','OthCurrAsset')) total_current_assets

```

### zero_total_current_liabilities

并列；**Unstated Choice**；把握中。

完整本表契约仅规定按类别求和，没有always populated、not_null或空类别补0的条款。SUM FILTER的NULL和CASE ELSE 0的零值是材料未定的空集处理选择；不沿用022的“契约明确SUM CASE ELSE 0”表述。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 13 | 13 | 49 | 36 |
| L1 | 13 | 13 | 49 | 36 |
| L2 | 13 | 13 | 49 | 36 |
| L3 | 13 | 13 | 49 | 36 |



来源：`records/022_reruns_impl-013_int_netsuite2__financial_ratios.json` / `zero_total_current_liabilities`。L0减少0行、13格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: total_current_liabilities
        data_type: DOUBLE
        description: Sum of absolute period_balance for account types AcctPay, CredCard, OthCurrLiab in the latest global period (non-negative)

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: total_current_liabilities
        data_type: DOUBLE
        description: Sum of absolute period_balance for account types AcctPay, CredCard, OthCurrLiab in the latest global period (non-negative)

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__financial_ratios.sql` / `text`（sql；普通SQL表达式不是披露）

```text

sum(abs(period_balance)) FILTER(WHERE account_type_name IN ('AcctPay','CredCard','OthCurrLiab')) total_current_liabilities

```

### zero_cash_and_equivalents

参与；**Unstated Choice**；把握中。

完整本表契约仅规定按类别求和，没有always populated、not_null或空类别补0的条款。SUM FILTER的NULL和CASE ELSE 0的零值是材料未定的空集处理选择；不沿用022的“契约明确SUM CASE ELSE 0”表述。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 13 | 13 | 49 | 39 |
| L1 | 13 | 13 | 49 | 39 |
| L2 | 13 | 13 | 49 | 39 |
| L3 | 13 | 13 | 49 | 39 |



来源：`records/022_reruns_impl-013_int_netsuite2__financial_ratios.json` / `zero_cash_and_equivalents`。L0减少0行、10格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: cash_and_equivalents
        data_type: DOUBLE
        description: Sum of period_balance for account type Bank in the latest global period

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: cash_and_equivalents
        data_type: DOUBLE
        description: Sum of period_balance for account type Bank in the latest global period

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__financial_ratios.sql` / `text`（sql；普通SQL表达式不是披露）

```text

sum(period_balance) FILTER(WHERE account_type_name='Bank') cash_and_equivalents

```

### zero_accounts_receivable

并列；**Unstated Choice**；把握中。

完整本表契约仅规定按类别求和，没有always populated、not_null或空类别补0的条款。SUM FILTER的NULL和CASE ELSE 0的零值是材料未定的空集处理选择；不沿用022的“契约明确SUM CASE ELSE 0”表述。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 13 | 13 | 49 | 36 |
| L1 | 13 | 13 | 49 | 36 |
| L2 | 13 | 13 | 49 | 36 |
| L3 | 13 | 13 | 49 | 36 |



来源：`records/022_reruns_impl-013_int_netsuite2__financial_ratios.json` / `zero_accounts_receivable`。L0减少0行、13格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: accounts_receivable
        data_type: DOUBLE
        description: Sum of period_balance for account types AcctRec and UnbilledRec in the latest global period

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: accounts_receivable
        data_type: DOUBLE
        description: Sum of period_balance for account types AcctRec and UnbilledRec in the latest global period

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__financial_ratios.sql` / `text`（sql；普通SQL表达式不是披露）

```text

sum(period_balance) FILTER(WHERE account_type_name IN ('AcctRec','UnbilledRec')) accounts_receivable

```

### zero_total_equity

参与；**Unstated Choice**；把握中。

完整本表契约仅规定按类别求和，没有always populated、not_null或空类别补0的条款。SUM FILTER的NULL和CASE ELSE 0的零值是材料未定的空集处理选择；不沿用022的“契约明确SUM CASE ELSE 0”表述。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 13 | 13 | 49 | 46 |
| L1 | 13 | 13 | 49 | 46 |
| L2 | 13 | 13 | 49 | 46 |
| L3 | 13 | 13 | 49 | 46 |



来源：`records/022_reruns_impl-013_int_netsuite2__financial_ratios.json` / `zero_total_equity`。L0减少0行、3格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

- name: total_equity
        data_type: DOUBLE
        description: Sum of period_balance for account types Equity, Retained Earnings, Net Income in the latest global period

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

- name: total_equity
        data_type: DOUBLE
        description: Sum of period_balance for account types Equity, Retained Earnings, Net Income in the latest global period

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__financial_ratios.sql` / `text`（sql；普通SQL表达式不是披露）

```text

sum(period_balance) FILTER(WHERE account_type_name IN ('Equity','Retained Earnings','Net Income')) total_equity

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`；行段[[1101, 1189]]；SHA-256 `c152a30bcad4df785d3f0ea461101eb8a4b36e4fa06059739a80e04998c4150f`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__financial_ratios.sql`；SHA-256 `909cf149b5ecde228a64fbe4f0855afe0d30a1de35a3a78b2ff95f0b49c17af2`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json`；材料包：`records/022_packages/022_impl-013_int_netsuite2__financial_ratios.md`。

- 基线源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 2}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共2条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 14；上游可见行数；失败=True。

  - `records/022_queries_retry.json` / index 10；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

- 条件求和空集返回NULL还是0：没有非空/默认明文。可将日常“总额”理解为0，但本轮不以gold实现补契约，按Unstated Choice，把握中。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
