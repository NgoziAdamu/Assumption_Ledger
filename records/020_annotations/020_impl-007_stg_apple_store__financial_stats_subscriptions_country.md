# impl-007 / stg_apple_store__financial_stats_subscriptions_country（全量）

## 结论

主要原因：**O**；把握：高。revenue按契约BIGINT转换，而gold保留DECIMAL小数，是主要原因。

参与因素：A：subscription_name（减0行/629格）；A：country（减4行/41格）。标记：无。

## 差异与归因依据

原始700行revenue无负数，696行有小数；契约明确BIGINT，agent遵守而gold DECIMAL(15,2)。诊断性地把agent的revenue表达式改为gold的小数表达式减少67行，超过name/country选择。空subscription_name默认名与非法country默认US契约未写，归A参与因素。

层：staging；比较库schema：staging；评测键：date_day, app_id, country。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml:300–322`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__financial_stats_subscriptions_country.sql:1–11`；SHA-256 `815351f3a2209e26ef7a526994ea600d528b0ce7a9080cd8f30aec660369c4d7`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_apple_store__financial_stats_subscriptions_country.sql:1–69`；SHA-256 `824a714f529637ef825624ebadde3ff19be8d320c638a6f08b467182b93bcd7a`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- subscription_name（agent SQL 第5行起）：
```sql
CAST(subscription_name AS VARCHAR) AS subscription_name
```
→
```sql
CAST(CASE WHEN NOT subscription_name IS NULL AND TRIM(subscription_name) <> '' THEN CAST(subscription_name AS TEXT) WHEN subscription_name IS NULL THEN NULL ELSE 'Unnamed Subscription' END AS TEXT) AS subscription_name
```

- revenue（agent SQL 第4行起）：
```sql
TRY_CAST(revenue AS BIGINT) AS revenue
```
→
```sql
CAST(CASE WHEN revenue >= 0 THEN CAST(revenue AS DECIMAL(15, 2)) WHEN revenue IS NULL THEN NULL ELSE 0.0 END AS DECIMAL(15, 2)) AS revenue
```

- country（agent SQL 第9行起）：
```sql
CAST(country AS VARCHAR) AS country
```
→
```sql
CAST(CASE WHEN NOT country IS NULL AND TRIM(country) <> '' AND LENGTH(country) = 2 THEN CAST(country AS TEXT) WHEN country IS NULL THEN NULL ELSE 'US' END AS TEXT) AS country
```

## agent可见证据与不确定性

不确定性四档：**看到了但没提**。

event14看过financial原始schema；没有针对本表revenue的类型选择或缺省名称/国家规则说明。

完整事件扫描数：70；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_apple_store__financial_stats_subscriptions_country | False |
| 12 | 11 | financial_stats_subscriptions_country | False |
| 14 | 13 | financial_stats_subscriptions_country | False |
| 20 | 19 | stg_apple_store__financial_stats_subscriptions_country,financial_stats_subscriptions_country | False |
| 26 | 25 | stg_apple_store__financial_stats_subscriptions_country | False |
| 46 | 45 | stg_apple_store__financial_stats_subscriptions_country,financial_stats_subscriptions_country | False |
| 48 | 47 | stg_apple_store__financial_stats_subscriptions_country,financial_stats_subscriptions_country | False |
| 56 | 55 | stg_apple_store__financial_stats_subscriptions_country | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='financial_stats_subscriptions_country') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "financial_stats_subscriptions_country", "_file", "VARCHAR"], ["raw", "financial_stats_subscriptions_country", "_line", "BIGINT"], ["raw", "financial_stats_subscriptions_country", "_modified", "VARCHAR"], ["raw", "financial_stats_subscriptions_country", "date", "VARCHAR"], ["raw", "financial_stats_subscriptions_country", "app_name", "VARCHAR"], ["raw", "financial_stats_subscriptions_country", "app_apple_id", "VARCHAR"], ["raw", "financial_stats_subscriptions_country", "country", "VARCHAR"], ["raw", "financial_stats_subscriptions_country", "subscription_name", "VARCHAR"], ["raw", "financial_stats_subscriptions_country", "active_subscriptions", "BIGINT"], ["raw", "financial_stats_subscriptions_country", "active_free_trial_introductory_offer_subscriptions", "BIGINT"], ["raw", "financial_stats_subscriptions_country", "revenue", "DOUBLE"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE revenue<0) negative_revenue,count(*) FILTER(WHERE revenue<>round(revenue)) fractional_revenue,count(*) FILTER(WHERE trim(subscription_name)='') blank_name FROM raw.financial_stats_subscriptions_country
```

结果：`[[700, 0, 696, 632]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=35 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-007_stg_apple_store__financial_stats_subscriptions_country/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：704行 / 1373格；重跑基线：704行 / 1373格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:704行/1373格 / L1:704行/1369格 / L2:704行/1369格 / L3:704行/1369格 | 均未整表匹配 |
| subscription_name | L0:704行/744格 / L1:700行/740格 / L2:700行/740格 / L3:700行/740格 | 均未整表匹配 |
| revenue | L0:637行/677格 / L1:637行/677格 / L2:637行/677格 / L3:637行/677格 | 均未整表匹配 |
| country | L0:700行/1332格 / L1:700行/1328格 / L2:700行/1328格 / L3:700行/1328格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"revenue": 696, "subscription_name": 629} |
| subscription_name | {"revenue": 696} |
| revenue | {"subscription_name": 629} |
| country | {"revenue": 700, "subscription_name": 632} |

本表全部重跑证据文件：`records/020_reruns_impl-007_stg_apple_store__financial_stats_subscriptions_country.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-007_stg_apple_store__financial_stats_subscriptions_country.md`。
- 重跑：`records/020_reruns_impl-007_stg_apple_store__financial_stats_subscriptions_country.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
