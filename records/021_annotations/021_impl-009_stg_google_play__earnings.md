# impl-009 / stg_google_play__earnings（全量）

## 结论

主要原因：**A**；把握：中。缺失必填来源时回填日期/SKU/package，或按原列过滤，契约未定。

参与因素：无经单修确认的其他参与因素。标记：无。

## 差异与归因依据

原始transaction_date、product_id、sku_id均8000行为空，base_plan_id与transaction_time可用。agent明确以这些替代原字段；gold采用原列并因not_null输出空表。契约未给源映射/回填政策，差异取决于这一选择。agent另遗漏transaction_type的COALESCE(...,Other)，8000行均NULL；单独补Other仍保留8000个gold不存在的行，不列参与因素。仅加not_null过滤得到0行不代表完整契约修复，因为契约还明确要求Other回填。

层：staging；实际schema：staging；评测键：sku_id, base_plan_id, buyer_postal_code, order_id, offer_id, package_name。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml:30–97`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__earnings.sql:1–25`，SHA-256 `e328a7b890e38f944ae156b02142671495d8f7df2470bbd1d4f738616f1af880`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/staging/stg_google_play__earnings.sql:1–135`，SHA-256 `47d00ead8ddd997455c8a96f88ba4aca23bb14bfc090d0aa28c8e370139436d5`。

- required_fields：agent SQL第25行起：
```sql
FROM raw.earnings
```
替换为：
```sql
FROM raw.earnings WHERE package_name IS NOT NULL AND sku_id IS NOT NULL AND transaction_date IS NOT NULL AND transaction_type IS NOT NULL
```

- package_source：agent SQL第14行起：
```sql
CAST(base_plan_id AS VARCHAR) AS package_name
```
替换为：
```sql
CAST(product_id AS VARCHAR) AS package_name
```

- output_not_null_policy：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_supplement_reruns_impl-009_stg_google_play__earnings.json`。

- missing_required_source_policy：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_supplement_reruns_impl-009_stg_google_play__earnings.json`。

- contract_other_default：agent SQL第23行起：
```sql
CASE WHEN lower(trim(transaction_type)) = 'charge' THEN 'Charge' WHEN lower(trim(transaction_type)) = 'refund' THEN 'Refund' WHEN lower(trim(transaction_type)) = 'other' THEN 'Other' ELSE NULL END
```
替换为：
```sql
COALESCE(CASE WHEN lower(trim(transaction_type)) = 'charge' THEN 'Charge' WHEN lower(trim(transaction_type)) = 'refund' THEN 'Refund' WHEN lower(trim(transaction_type)) = 'other' THEN 'Other' ELSE NULL END,'Other')
```

## agent可见证据与不确定性

**针对本表的具体说明**。

event53替换transaction_date与sku来源；event67：Earnings 源数据 `transaction_date` 为空而 `transaction_time` 有值；为提供可用日期，暂用 `transaction_time` 日期部分回填。源 SKU 为空时用可用的 product/base-plan 值兜底。

最终报告原句（其适用范围按上文判定）：

> 本次交付**未完整实现数据合同中的全部业务逻辑**。留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。`run.py` 成功只能证明 SQL 可执行，不能证明输出满足全部业务定义或可用于生产分析。

> - Earnings 源数据 `transaction_date` 为空而 `transaction_time` 有值；为提供可用日期，暂用 `transaction_time` 日期部分回填。源 SKU 为空时用可用的 product/base-plan 值兜底。

扫描69个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=16。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 12 | 11 | False |
| 14 | 13 | False |
| 20 | 19 | False |
| 22 | 21 | False |
| 28 | 27 | False |
| 30 | 29 | False |
| 38 | 37 | False |
| 42 | 41 | False |
| 44 | 43 | False |
| 46 | 45 | False |
| 48 | 47 | False |
| 54 | 53 | False |
| 56 | 55 | False |
| 58 | 57 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：2；核实代价档：需要查业务说明。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE transaction_date IS NULL) raw_date_null,count(*) FILTER(WHERE product_id IS NULL) product_null,count(*) FILTER(WHERE base_plan_id IS NULL) base_null,count(*) FILTER(WHERE sku_id IS NULL) sku_null,count(*) FILTER(WHERE try_cast(substr(transaction_time,1,10) AS DATE) IS NOT NULL) alternative_date_parseable FROM raw.earnings
```

结果（列顺序["n", "raw_date_null", "product_null", "base_null", "sku_null", "alternative_date_parseable"]）：`[[8000, 8000, 8000, 0, 8000, 8000]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`；记录：`records/021_earnings_diagnostic.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE package_name IS NULL) package_name_null,count(*) FILTER(WHERE sku_id IS NULL) sku_id_null,count(*) FILTER(WHERE transaction_date IS NULL) transaction_date_null,count(*) FILTER(WHERE transaction_type IS NULL) transaction_type_null FROM (SELECT
    try_cast(CASE WHEN try_cast(amount_buyer_currency_ AS DECIMAL(18,3)) BETWEEN -999999.99 AND 999999.99 THEN try_cast(amount_buyer_currency_ AS DECIMAL(18,3)) ELSE NULL END AS DECIMAL(18,3)) AS amount_buyer_currency,
    try_cast(amount_merchant_currency_ AS DECIMAL(18,3)) AS amount_merchant_currency,
    CAST(base_plan_id AS VARCHAR) AS base_plan_id,
    CAST(buyer_country AS VARCHAR) AS buyer_country,
    CAST(CASE WHEN length(upper(trim(buyer_currency))) = 3 THEN upper(trim(buyer_currency)) ELSE NULL END AS VARCHAR) AS buyer_currency,
    try_cast(buyer_postal_code AS DOUBLE) AS buyer_postal_code,
    CAST(buyer_state AS VARCHAR) AS buyer_state,
    try_cast(currency_conversion_rate AS DOUBLE) AS currency_conversion_rate,
    CAST(description AS VARCHAR) AS order_id,
    try_cast(hardware AS DOUBLE) AS buyer_hardware,
    CAST(merchant_currency AS VARCHAR) AS merchant_currency,
    CAST(offer_id AS VARCHAR) AS offer_id,
    CAST(base_plan_id AS VARCHAR) AS package_name,
    CAST(product_title AS VARCHAR) AS product_title,
    try_cast(product_type AS BOOLEAN) AS product_type,
    try_cast(refund_type AS DOUBLE) AS refund_type,
    CAST(coalesce(sku_id, product_id, base_plan_id) AS VARCHAR) AS sku_id,
    try_cast(tax_type AS DOUBLE) AS tax_type,
    try_cast(substr(transaction_time, 1, 10) AS DATE) AS transaction_date,
    try_cast(substr(transaction_time, 1, 19) AS TIMESTAMP) AS transaction_pt_timestamp,
    CAST(regexp_extract(transaction_time, '([+-][0-9]{2}:[0-9]{2})', 1) AS VARCHAR) AS transaction_timezone,
    CAST(CASE WHEN lower(trim(transaction_type)) = 'charge' THEN 'Charge' WHEN lower(trim(transaction_type)) = 'refund' THEN 'Refund' WHEN lower(trim(transaction_type)) = 'other' THEN 'Other' ELSE NULL END AS VARCHAR) AS transaction_type,
    CAST(_modified AS VARCHAR) AS _fivetran_synced
FROM raw.earnings
) projected
```

结果（列顺序["n", "package_name_null", "sku_id_null", "transaction_date_null", "transaction_type_null"]）：`[[8000, 0, 0, 0, 8000]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：8000行/184000格；选定基线：8000行/184000格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 8000行/184000格；L1 8000行/184000格；L2 8000行/184000格；L3 8000行/184000格 | 均未整表匹配 |
| required_fields | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |
| package_source | L0 8000行/184000格；L1 8000行/184000格；L2 8000行/184000格；L3 8000行/184000格 | 均未整表匹配 |
| output_not_null_policy | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |
| missing_required_source_policy | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |
| contract_other_default | L0 8000行/184000格；L1 8000行/184000格；L2 8000行/184000格；L3 8000行/184000格 | 均未整表匹配 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {} |
| required_fields | {} |
| package_source | {} |
| output_not_null_policy | {} |
| missing_required_source_policy | {} |
| contract_other_default | {} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。

本表not_null过滤、原字段选择和Other回填相互作用，不能从“过滤后为空”的统计反推出C主因；见规则问题。


## 规则问题

存在源字段回填与not_null/Other校正的交互。按回填缺失必填来源的A归因：gold使用空原列并过滤、agent使用替代列。完整政策对照是诊断，不是单点U修复。仅过滤输出NULL会得到空表，但还违背transaction_type必须Other回填的规定，不能以此选C主因。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-009_stg_google_play__earnings.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-009_stg_google_play__earnings/021_impl-009_stg_google_play__earnings.json`。
- 重跑：`records/021_reruns_impl-009_stg_google_play__earnings.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_supplement_reruns_impl-009_stg_google_play__earnings.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_extra_reruns_impl-009_stg_google_play__earnings.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
