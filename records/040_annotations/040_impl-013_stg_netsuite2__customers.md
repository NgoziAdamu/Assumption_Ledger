# 040 正式标注：impl-013_stg_netsuite2__customers

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。022旧主要原因仅原样存档为 `O`，不作为新类别依据。

## 结论

主要原因：**其他**；把握高；共2个点。不是只能组合修复。

主因由独立单改的L0行规模减少量、再格子减少量决定。

## 详细发现

### 第3～7节判断顺序

本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。

各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。

### email_order

非原因；**Intent Misreading**；把握高。

契约列出的邮箱验证在LOWER(TRIM)之前；最终SQL先trim再验证。旧event15生成器曾按先验证再清理表达该顺序；当前单改无改善，保留非原因。

是否说出：第2档——交付物里只有通用说明。交付物有适用于本类处理的通用说明，没有针对本表本处逐项说明。

证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。

曾经理解对过：是。event15先对email_address验证，再在THEN lower(trim)；仅证明本点先验后清顺序，不声称当时整表正确。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2 | 2 | 2 | 2 |
| L1 | 2 | 2 | 2 | 2 |
| L2 | 2 | 2 | 2 | 2 |
| L3 | 2 | 2 | 2 | 2 |



来源：`records/022_reruns_impl-013_stg_netsuite2__customers.json` / `email_order`。L0减少0行、0格。

非原因说明：存在未确立的前提，但不是判错原因

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

rule: "email_address IS NULL OR email_address RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

rule: "email_address IS NULL OR email_address RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/65.json` / `args.final_thought` / event 65（delivery；普通SQL表达式不是披露）

```text

客户邮箱、电话按合同规定清洗或置空。

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__customers.sql` / `text`（sql；普通SQL表达式不是披露）

```text

regexp_full_match(trim(source_email),

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/15.json` / `args.command` / event 15（previous_correct；普通SQL表达式不是披露）

```text

"""+',\n'.join(cols)+f'\n    FROM raw.{source} r\n), cleaned AS (\n SELECT *,\n  CASE WHEN email_address IS NULL OR regexp_full_match(email_address, \'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}\') THEN lower(trim(email_address)) ELSE NULL END AS cleaned_email,\n  CASE WHEN phone_number IS NULL OR (length(trim(phone_number)) BETWEEN 8 AND 20) THEN regexp_replace(trim(phone_number), \'[^0-9+()-]\', \'\') ELSE NULL END AS cleaned_phone\n FROM source_data\n)\nSELECT * EXCLUDE (email_address, phone_number, cleaned_email, cleaned_phone), cleaned_email AS email_address, cleaned_phone AS phone_number\nFROM cleaned\nWHERE customer_id IS NOT NULL'

```

### loose_email

主要；**其他**；把握高。

契约严格正则排除two@@signs.com、missing@.com；agent遵从，gold弱校验保留。

是否说出：第2档——交付物里只有通用说明。交付物有适用于本类处理的通用说明，没有针对本表本处逐项说明。

证据在场：不适用。非探索类别，不填。

曾经理解对过：不适用。非探索类别，不填。

系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 2 | 0 | 2 | 0 |
| L1 | 2 | 0 | 2 | 0 |
| L2 | 2 | 0 | 2 | 0 |
| L3 | 2 | 0 | 2 | 0 |



来源：`records/022_reruns_impl-013_stg_netsuite2__customers.json` / `loose_email`。L0减少2行、2格。

原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）

```text

rule: "email_address IS NULL OR email_address RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）

```text

rule: "email_address IS NULL OR email_address RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"

```

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/65.json` / `args.final_thought` / event 65（delivery；普通SQL表达式不是披露）

```text

客户邮箱、电话按合同规定清洗或置空。

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__customers.sql` / `text`（sql；普通SQL表达式不是披露）

```text

regexp_full_match(trim(source_email), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}$')

```

## 证据来源

- 完整契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`；行段[[232, 279]]；SHA-256 `c152a30bcad4df785d3f0ea461101eb8a4b36e4fa06059739a80e04998c4150f`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__customers.sql`；SHA-256 `22a86f33b6e9e0bded34f8f495d5374597848679fac15ac5d855b3e3613560e6`。

- 原始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json`；材料包：`records/022_packages/022_impl-013_stg_netsuite2__customers.md`。

- 基线源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`；时钟控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。

- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。

- 复用核实查询连失败共3条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：

  - `records/022_queries.json` / index 33；上游可见行数；失败=True。

  - `records/022_queries.json` / index 34；邮箱检验；失败=False。

  - `records/022_queries_retry.json` / index 23；上游可见行数；失败=False。

## 不确定或没查到的（含规则问题）

无新增规则问题；按冻结v3.2执行。

## 建议的下一步

纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。
