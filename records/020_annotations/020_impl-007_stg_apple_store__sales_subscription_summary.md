> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-007 / stg_apple_store__sales_subscription_summary（全量）

## 结论

主要原因：**A**；把握：中。订阅数取subscribers计数，还是两个布尔标志转1/0，契约未映射。

参与因素：A：free_trial_subscriptions（减0行/347格）。标记：无。

## 差异与归因依据

契约只列BIGINT字段名。raw同时有subscribers和active_*布尔标志，数据本身无法判定业务口径；不能仅因gold用了布尔标志归U。active_subscriptions单修影响最大，free_trial为同类A参与因素。

层：staging；比较库schema：staging；评测键：date_day, app_id, country。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml:211–239`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_summary.sql:1–14`；SHA-256 `a647c045495b503131ba547324340e6aa772c4bd22fed4b9713108bd42a71e79`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_apple_store__sales_subscription_summary.sql:1–23`；SHA-256 `6489173e4e2e3d40d7447972c5350af27931a58edd1e4644dd37b198ac16f857`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- active_subscriptions：
```sql
TRY_CAST(subscribers AS BIGINT) AS active_subscriptions
```
→
```sql
CAST(CASE WHEN active_standard_price_subscriptions THEN 1 ELSE 0 END AS BIGINT) AS active_subscriptions
```

- free_trial_subscriptions：
```sql
CASE WHEN active_free_trial_introductory_offer_subscriptions THEN TRY_CAST(subscribers AS BIGINT) ELSE 0 END AS free_trial_subscriptions
```
→
```sql
CAST(CASE WHEN active_free_trial_introductory_offer_subscriptions THEN 1 ELSE 0 END AS BIGINT) AS free_trial_subscriptions
```

## agent可见证据与不确定性

不确定性四档：**只有通用策略说明**。

event67：Apple 订阅 summary/event 字段有若干原始字段与 staging 字段语义不完全一致，使用可用列映射且转换兼容字段类型。没有点名active_subscriptions和free_trial_subscriptions各自选择。

完整事件扫描数：70；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_apple_store__sales_subscription_summary | False |
| 12 | 11 | sales_subscription_summary | False |
| 14 | 13 | sales_subscription_summary | False |
| 16 | 15 | sales_subscription_summary | False |
| 20 | 19 | stg_apple_store__sales_subscription_summary,sales_subscription_summary | False |
| 26 | 25 | stg_apple_store__sales_subscription_summary | False |
| 36 | 35 | stg_apple_store__sales_subscription_summary | False |
| 38 | 37 | stg_apple_store__sales_subscription_summary,sales_subscription_summary | False |
| 46 | 45 | stg_apple_store__sales_subscription_summary,sales_subscription_summary | False |
| 48 | 47 | stg_apple_store__sales_subscription_summary,sales_subscription_summary | False |
| 56 | 55 | stg_apple_store__sales_subscription_summary | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：需要查业务说明。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='sales_subscription_summary') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "sales_subscription_summary", "vendor_number", "DOUBLE"], ["raw", "sales_subscription_summary", "app_name", "VARCHAR"], ["raw", "sales_subscription_summary", "app_apple_id", "VARCHAR"], ["raw", "sales_subscription_summary", "subscription_name", "VARCHAR"], ["raw", "sales_subscription_summary", "subscription_apple_id", "BIGINT"], ["raw", "sales_subscription_summary", "subscription_group_id", "BIGINT"], ["raw", "sales_subscription_summary", "subscription_duration", "VARCHAR"], ["raw", "sales_subscription_summary", "customer_price", "DOUBLE"], ["raw", "sales_subscription_summary", "customer_currency", "VARCHAR"], ["raw", "sales_subscription_summary", "developer_proceeds", "DOUBLE"], ["raw", "sales_subscription_summary", "proceeds_currency", "VARCHAR"], ["raw", "sales_subscription_summary", "preserved_pricing", "BOOLEAN"], ["raw", "sales_subscription_summary", "proceeds_reason", "VARCHAR"], ["raw", "sales_subscription_summary", "subscription_offer_name", "VARCHAR"], ["raw", "sales_subscription_summary", "promotional_offer_id", "BIGINT"], ["raw", "sales_subscription_summary", "state", "VARCHAR"], ["raw", "sales_subscription_summary", "country", "VARCHAR"], ["raw", "sales_subscription_summary", "device", "VARCHAR"], ["raw", "sales_subscription_summary", "client", "VARCHAR"], ["raw", "sales_subscription_summary", "active_standard_price_subscriptions", "BOOLEAN"], ["raw", "sales_subscription_summary", "active_free_trial_introductory_offer_subscriptions", "BOOLEAN"], ["raw", "sales_subscription_summary", "active_pay_up_front_introductory_offer_subscriptions", "BOOLEAN"], ["raw", "sales_subscription_summary", "active_pay_as_you_go_introductory_offer_subscriptions", "BOOLEAN"], ["raw", "sales_subscription_summary", "free_trial_promotional_offer_subscriptions", "BOOLEAN"], ["raw", "sales_subscription_summary", "pay_up_front_promotional_offer_subscriptions", "BOOLEAN"], ["raw", "sales_subscription_summary", "pay_as_you_go_promotional_offer_subscriptions", "BOOLEAN"], ["raw", "sales_subscription_summary", "marketing_opt_ins", "BOOLEAN"], ["raw", "sales_subscription_summary", "billing_retry", "BOOLEAN"], ["raw", "sales_subscription_summary", "grace_period", "BOOLEAN"], ["raw", "sales_subscription_summary", "free_trial_offer_code_subscriptions", "BOOLEAN"], ["raw", "sales_subscription_summary", "pay_up_front_offer_code_subscriptions", "BOOLEAN"], ["raw", "sales_subscription_summary", "pay_as_you_go_offer_code_subscriptions", "BOOLEAN"], ["raw", "sales_subscription_summary", "subscribers", "DOUBLE"], ["raw", "sales_subscription_summary", "date", "VARCHAR"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE subscribers<0) negative_subscribers,count(*) FILTER(WHERE subscribers<>cast(active_standard_price_subscriptions AS BIGINT)) different_active,count(*) FILTER(WHERE active_free_trial_introductory_offer_subscriptions AND subscribers<>1) different_free FROM raw.sales_subscription_summary
```

结果：`[[700, 0, 700, 347]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=36 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-007_stg_apple_store__sales_subscription_summary/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：700行 / 1047格；重跑基线：700行 / 1047格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:700行/1047格 / L1:700行/1047格 / L2:700行/1047格 / L3:700行/1047格 | 均未整表匹配 |
| active_subscriptions | L0:347行/347格 / L1:347行/347格 / L2:347行/347格 / L3:347行/347格 | 均未整表匹配 |
| free_trial_subscriptions | L0:700行/700格 / L1:700行/700格 / L2:700行/700格 / L3:700行/700格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"active_subscriptions": 700, "free_trial_subscriptions": 347} |
| active_subscriptions | {"free_trial_subscriptions": 347} |
| free_trial_subscriptions | {"active_subscriptions": 700} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-007_stg_apple_store__sales_subscription_summary.md`。
- 重跑：`records/020_reruns_impl-007_stg_apple_store__sales_subscription_summary.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
