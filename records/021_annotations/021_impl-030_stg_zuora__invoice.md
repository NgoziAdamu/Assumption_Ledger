# impl-030 / stg_zuora__invoice（校准）

## 结论

主要原因：**多因并列（I、O）**；把握：中。按每个输出表达式单修，L0行规模均1045；account_mapping、adjustment_amount、credit_balance_adjustment_amount、credit_memo_amount、exchange_rate各减少1040格并列。前者I：event19生成同名srcname=n的正确映射，event45的全局pk_alias覆盖为id；后四者O：契约要求DOUBLE而gold保留VARCHAR。原始invoice.id与account_id 2004行均不同，account_id匹配账户表1999行，id匹配0行。

参与因素：C：错误排除不可解析/NULL created_date，单修减少175格；O：两列BIGINT、两列DATE及balance的契约类型与gold原样VARCHAR不同。标记：无。

## 差异与归因依据

按每个输出表达式单修，L0行规模均1045；account_mapping、adjustment_amount、credit_balance_adjustment_amount、credit_memo_amount、exchange_rate各减少1040格并列。前者I：event19生成同名srcname=n的正确映射，event45的全局pk_alias覆盖为id；后四者O：契约要求DOUBLE而gold保留VARCHAR。原始invoice.id与account_id 2004行均不同，account_id匹配账户表1999行，id匹配0行。

层：staging；实际schema：staging；评测键：invoice_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml:169–281`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql:1–51`，SHA-256 `f744ee511d6f055c0b9df59ee9e3b9830a0629ac6212cfa3c341b77e49f23767`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql:1–63`，SHA-256 `68a16e3ce59d85071f4597a2d5ed8a9bac6a3b04bcbc3463b52fc6e7e8d5662a`。

- keep_null_dates：agent SQL第4行起：
```sql
try_cast(created_date AS timestamp) IS NOT NULL AND try_cast(created_date AS timestamp) <= TIMESTAMPTZ '2025-10-12 12:00:00+00' AND try_cast(created_date AS timestamp) >= timestamp '2000-01-01 00:00:00'
```
替换为：
```sql
(try_cast(created_date AS timestamp) IS NULL OR (try_cast(created_date AS timestamp) <= TIMESTAMPTZ '2025-10-12 12:00:00+00' AND try_cast(created_date AS timestamp) >= timestamp '2000-01-01 00:00:00'))
```

- account_mapping：agent SQL第7行起：
```sql
try_cast("id" AS VARCHAR) AS account_id
```
替换为：
```sql
try_cast("account_id" AS VARCHAR) AS account_id
```

- adjustment_amount：agent SQL第8行起：
```sql
try_cast("adjustment_amount" AS DOUBLE)
```
替换为：
```sql
"adjustment_amount"
```

- amount_without_tax：agent SQL第11行起：
```sql
try_cast("amount_without_tax" AS BIGINT)
```
替换为：
```sql
"amount_without_tax"
```

- amount_without_tax_home_currency：agent SQL第12行起：
```sql
try_cast("amount_without_tax_home_currency" AS BIGINT)
```
替换为：
```sql
"amount_without_tax_home_currency"
```

- balance：agent SQL第14行起：
```sql
try_cast("balance" AS DOUBLE)
```
替换为：
```sql
"balance"
```

- credit_balance_adjustment_amount：agent SQL第19行起：
```sql
try_cast("credit_balance_adjustment_amount" AS DOUBLE)
```
替换为：
```sql
"credit_balance_adjustment_amount"
```

- credit_memo_amount：agent SQL第20行起：
```sql
try_cast("credit_memo_amount" AS DOUBLE)
```
替换为：
```sql
"credit_memo_amount"
```

- exchange_rate：agent SQL第23行起：
```sql
try_cast("exchange_rate" AS DOUBLE)
```
替换为：
```sql
"exchange_rate"
```

- exchange_rate_date：agent SQL第24行起：
```sql
try_cast("exchange_rate_date" AS DATE)
```
替换为：
```sql
"exchange_rate_date"
```

- target_date：agent SQL第43行起：
```sql
try_cast("target_date" AS DATE)
```
替换为：
```sql
"target_date"
```

## agent可见证据与不确定性

**account_mapping=只有通用策略说明；adjustment_amount=只有通用策略说明；credit_balance_adjustment_amount=只有通用策略说明；credit_memo_amount=只有通用策略说明；exchange_rate=只有通用策略说明**。

event39→40已显示invoice原始account_id；event45批量pk_alias覆盖；event69报告：Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。非关键不可解析值转为 NULL。类型报告涉及多表策略，未具体说明本表四列与gold的类型差异。

最终报告原句（其适用范围按上文判定）：

> - Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。非关键不可解析值转为 NULL。

> - 合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。

事件定位补充：报告写入命令为event69，最终finish为event71，二者内容一致；盲标锁定文件保持原样。

扫描73个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=41。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 10 | 9 | False |
| 14 | 13 | False |
| 16 | 15 | False |
| 18 | 17 | False |
| 24 | 23 | False |
| 28 | 27 | False |
| 32 | 31 | False |
| 40 | 39 | False |
| 44 | 43 | False |
| 52 | 51 | False |
| 54 | 53 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：1；核实代价档：一条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`；记录：`records/021_calibration_queries.json`。

```sql
SELECT count(*) n, count(*) FILTER(WHERE id IS NOT DISTINCT FROM account_id) id_eq_account, count(*) FILTER(WHERE account_id IN (SELECT id FROM raw.zuora_account_data)) account_fk_matches, count(*) FILTER(WHERE id IN (SELECT id FROM raw.zuora_account_data)) id_fk_matches, count(*) FILTER(WHERE try_cast(created_date AS TIMESTAMP) IS NULL) null_or_unparsable_created FROM raw.zuora_invoice_data
```

结果（列顺序["n", "id_eq_account", "account_fk_matches", "id_fk_matches", "null_or_unparsable_created"]）：`[[2004, 0, 1999, 0, 9]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：1046行/9609格；选定基线：1045行/9565格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 2}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 1045行/9565格；L1 1045行/5397格；L2 1045行/5381格；L3 1045行/3311格 | 均未整表匹配 |
| keep_null_dates | L0 1045行/9390格；L1 1045行/5202格；L2 1045行/5186格；L3 1045行/3106格 | 均未整表匹配 |
| account_mapping | L0 1045行/8525格；L1 1041行/4357格；L2 1041行/4341格；L3 1031行/2271格 | 均未整表匹配 |
| adjustment_amount | L0 1045行/8525格；L1 1045行/5397格；L2 1045行/5381格；L3 1045行/3311格 | 均未整表匹配 |
| amount_without_tax | L0 1045行/8530格；L1 1045行/4364格；L2 1045行/4356格；L3 1045行/2286格 | 均未整表匹配 |
| amount_without_tax_home_currency | L0 1045行/8530格；L1 1045行/4364格；L2 1045行/4356格；L3 1045行/2286格 | 均未整表匹配 |
| balance | L0 1045行/9560格；L1 1045行/5397格；L2 1045行/5381格；L3 1045行/3311格 | 均未整表匹配 |
| credit_balance_adjustment_amount | L0 1045行/8525格；L1 1045行/5397格；L2 1045行/5381格；L3 1045行/3311格 | 均未整表匹配 |
| credit_memo_amount | L0 1045行/8525格；L1 1045行/5396格；L2 1045行/5380格；L3 1045行/3310格 | 均未整表匹配 |
| exchange_rate | L0 1045行/8525格；L1 1045行/5397格；L2 1045行/5381格；L3 1045行/3311格 | 均未整表匹配 |
| exchange_rate_date | L0 1045行/8530格；L1 1045行/4362格；L2 1045行/4346格；L3 1045行/3311格 | 均未整表匹配 |
| target_date | L0 1045行/8530格；L1 1045行/4362格；L2 1045行/4346格；L3 1045行/3311格 | 均未整表匹配 |

不适用：独立盲标主因不是U。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"account_id": 1040, "adjustment_amount": 1040, "amount_without_tax": 1035, "amount_without_tax_home_currency": 1035, "balance": 5, "credit_balance_adjustment_amount": 1040, "credit_memo_amount": 1040, "exchange_rate": 1040, "exchange_rate_date": 1035, "target_date": 1035} |
| keep_null_dates | {"account_id": 1045, "adjustment_amount": 1045, "amount_without_tax": 1040, "amount_without_tax_home_currency": 1040, "balance": 5, "credit_balance_adjustment_amount": 1045, "credit_memo_amount": 1045, "exchange_rate": 1045, "exchange_rate_date": 1040, "target_date": 1040} |
| account_mapping | {"adjustment_amount": 1040, "amount_without_tax": 1035, "amount_without_tax_home_currency": 1035, "balance": 5, "credit_balance_adjustment_amount": 1040, "credit_memo_amount": 1040, "exchange_rate": 1040, "exchange_rate_date": 1035, "target_date": 1035} |
| adjustment_amount | {"account_id": 1040, "amount_without_tax": 1035, "amount_without_tax_home_currency": 1035, "balance": 5, "credit_balance_adjustment_amount": 1040, "credit_memo_amount": 1040, "exchange_rate": 1040, "exchange_rate_date": 1035, "target_date": 1035} |
| amount_without_tax | {"account_id": 1040, "adjustment_amount": 1040, "amount_without_tax_home_currency": 1035, "balance": 5, "credit_balance_adjustment_amount": 1040, "credit_memo_amount": 1040, "exchange_rate": 1040, "exchange_rate_date": 1035, "target_date": 1035} |
| amount_without_tax_home_currency | {"account_id": 1040, "adjustment_amount": 1040, "amount_without_tax": 1035, "balance": 5, "credit_balance_adjustment_amount": 1040, "credit_memo_amount": 1040, "exchange_rate": 1040, "exchange_rate_date": 1035, "target_date": 1035} |
| balance | {"account_id": 1040, "adjustment_amount": 1040, "amount_without_tax": 1035, "amount_without_tax_home_currency": 1035, "credit_balance_adjustment_amount": 1040, "credit_memo_amount": 1040, "exchange_rate": 1040, "exchange_rate_date": 1035, "target_date": 1035} |
| credit_balance_adjustment_amount | {"account_id": 1040, "adjustment_amount": 1040, "amount_without_tax": 1035, "amount_without_tax_home_currency": 1035, "balance": 5, "credit_memo_amount": 1040, "exchange_rate": 1040, "exchange_rate_date": 1035, "target_date": 1035} |
| credit_memo_amount | {"account_id": 1040, "adjustment_amount": 1040, "amount_without_tax": 1035, "amount_without_tax_home_currency": 1035, "balance": 5, "credit_balance_adjustment_amount": 1040, "exchange_rate": 1040, "exchange_rate_date": 1035, "target_date": 1035} |
| exchange_rate | {"account_id": 1040, "adjustment_amount": 1040, "amount_without_tax": 1035, "amount_without_tax_home_currency": 1035, "balance": 5, "credit_balance_adjustment_amount": 1040, "credit_memo_amount": 1040, "exchange_rate_date": 1035, "target_date": 1035} |
| exchange_rate_date | {"account_id": 1040, "adjustment_amount": 1040, "amount_without_tax": 1035, "amount_without_tax_home_currency": 1035, "balance": 5, "credit_balance_adjustment_amount": 1040, "credit_memo_amount": 1040, "exchange_rate": 1040, "target_date": 1035} |
| target_date | {"account_id": 1040, "adjustment_amount": 1040, "amount_without_tax": 1035, "amount_without_tax_home_currency": 1035, "balance": 5, "credit_balance_adjustment_amount": 1040, "credit_memo_amount": 1040, "exchange_rate": 1040, "exchange_rate_date": 1035} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

手册未明确同一生成器类型策略影响多个输出列时是否合并为一个错误点。本次以单个输出表达式为干预单位（每列独立重跑）；若把所有按契约类型转换视为一个O原因，可能得到O主因。另I/U界线：选择手册允许的代码先给出正确列、再被覆盖这一I证据，不把所有*_id都当主键的猜测作为主因U。 018对照后发现account_source在018归U，本次盲标归I；保留盲标，不为一致率改写。规模和四档一致。

## 证据路径与复现

- 精简材料包：`records/013_packages/013_impl-030_staging_stg_zuora__invoice.md`。
- 完整机械材料（可由prepare脚本重建）：`records/012_packages/012_impl-030_staging_stg_zuora__invoice.json`。
- 重跑：`records/021_reruns_impl-030_stg_zuora__invoice.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
