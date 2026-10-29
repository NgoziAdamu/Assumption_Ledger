> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-007 / stg_google_play__stats_store_performance_traffic_source（全量）

## 结论

主要原因：**O**；把握：高。agent按契约把3条越界原始转化率置NULL，gold重新算比例保留。

参与因素：A：valid_rate_formula_choice（减1行/1格）。标记：无。

## 差异与归因依据

raw有3条越界率；gold使用acquisitions/visitors而非nullify，违反明定处理，单项改变减少3行；剩余1条合法值取源率还是重算比例未规定，A参与因素。

层：staging；比较库schema：staging；评测键：date_day, package_name, traffic_source。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml:114–135`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_google_play__stats_store_performance_traffic_source.sql:1–12`；SHA-256 `11b906a0ca4f168dd0d758ed9a20a7e1b78db1d072a377bc5f1d1c48ff71f8de`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_google_play__stats_store_performance_traffic_source.sql:1–26`；SHA-256 `69806baa9d3dc30d3ece14e7618955aba06b74bc007945610f0cd8c951702d78`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- gold_ratio_diagnostic：
```sql
CASE WHEN store_listing_conversion_rate BETWEEN 0 AND 1 THEN store_listing_conversion_rate ELSE NULL END AS store_listing_conversion_rate
```
→
```sql
CAST(CASE WHEN store_listing_visitors > 0 THEN CAST(store_listing_acquisitions AS DECIMAL(18, 3)) / CAST(store_listing_visitors AS DECIMAL(18, 3)) WHEN store_listing_visitors IS NULL THEN NULL ELSE 0.0 END AS DECIMAL(10, 4)) AS store_listing_conversion_rate
```

- invalid_rate_policy_diagnostic：
```sql
CASE WHEN store_listing_conversion_rate BETWEEN 0 AND 1 THEN store_listing_conversion_rate ELSE NULL END AS store_listing_conversion_rate
```
→
```sql
CASE WHEN store_listing_conversion_rate NOT BETWEEN 0 AND 1 THEN CAST(CASE WHEN store_listing_visitors > 0 THEN CAST(store_listing_acquisitions AS DECIMAL(18, 3)) / CAST(store_listing_visitors AS DECIMAL(18, 3)) WHEN store_listing_visitors IS NULL THEN NULL ELSE 0.0 END AS DECIMAL(10, 4)) ELSE store_listing_conversion_rate END AS store_listing_conversion_rate
```

- valid_rate_formula_choice：
```sql
CASE WHEN store_listing_conversion_rate BETWEEN 0 AND 1 THEN store_listing_conversion_rate ELSE NULL END AS store_listing_conversion_rate
```
→
```sql
CASE WHEN store_listing_conversion_rate BETWEEN 0 AND 1 THEN CAST(CASE WHEN store_listing_visitors > 0 THEN CAST(store_listing_acquisitions AS DECIMAL(18, 3)) / CAST(store_listing_visitors AS DECIMAL(18, 3)) WHEN store_listing_visitors IS NULL THEN NULL ELSE 0.0 END AS DECIMAL(10, 4)) ELSE NULL END AS store_listing_conversion_rate
```

## agent可见证据与不确定性

不确定性四档：**只有通用策略说明**。

event67：随后修正了输出列顺序及评级规则：无效的必需平均评级记录删除、契约指定 nullify 的评级/转化率置空或删除。

完整事件扫描数：70；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_google_play__stats_store_performance_traffic_source | False |
| 14 | 13 | stats_store_performance_traffic_source | False |
| 18 | 17 | stg_google_play__stats_store_performance_traffic_source,stats_store_performance_traffic_source | False |
| 20 | 19 | stg_google_play__stats_store_performance_traffic_source,stats_store_performance_traffic_source | False |
| 26 | 25 | stg_google_play__stats_store_performance_traffic_source | False |
| 44 | 43 | stg_google_play__stats_store_performance_traffic_source | False |
| 46 | 45 | stg_google_play__stats_store_performance_traffic_source,stats_store_performance_traffic_source | False |
| 48 | 47 | stg_google_play__stats_store_performance_traffic_source,stats_store_performance_traffic_source | False |
| 56 | 55 | stg_google_play__stats_store_performance_traffic_source | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='stats_store_performance_traffic_source') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "stats_store_performance_traffic_source", "_file", "VARCHAR"], ["raw", "stats_store_performance_traffic_source", "_line", "BIGINT"], ["raw", "stats_store_performance_traffic_source", "_modified", "VARCHAR"], ["raw", "stats_store_performance_traffic_source", "date", "VARCHAR"], ["raw", "stats_store_performance_traffic_source", "package_name", "VARCHAR"], ["raw", "stats_store_performance_traffic_source", "traffic_source", "VARCHAR"], ["raw", "stats_store_performance_traffic_source", "search_term", "VARCHAR"], ["raw", "stats_store_performance_traffic_source", "utm_source", "VARCHAR"], ["raw", "stats_store_performance_traffic_source", "utm_campaign", "VARCHAR"], ["raw", "stats_store_performance_traffic_source", "store_listing_acquisitions", "BIGINT"], ["raw", "stats_store_performance_traffic_source", "store_listing_visitors", "BIGINT"], ["raw", "stats_store_performance_traffic_source", "store_listing_conversion_rate", "DOUBLE"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE store_listing_conversion_rate NOT BETWEEN 0 AND 1) invalid_raw_rate,count(*) FILTER(WHERE store_listing_visitors>0 AND store_listing_acquisitions*1.0/store_listing_visitors>1) invalid_ratio,count(*) FILTER(WHERE store_listing_conversion_rate IS DISTINCT FROM round(store_listing_acquisitions*1.0/nullif(store_listing_visitors,0),4)) different_ratio FROM raw.stats_store_performance_traffic_source
```

结果：`[[700, 3, 0, 4]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=42 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-007_stg_google_play__stats_store_performance_traffic_source/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：4行 / 4格；重跑基线：4行 / 4格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:4行/4格 / L1:4行/4格 / L2:3行/3格 / L3:3行/3格 | 均未整表匹配 |
| gold_ratio_diagnostic | L0:0行/0格 / L1:0行/0格 / L2:0行/0格 / L3:0行/0格 | L0 |
| invalid_rate_policy_diagnostic | L0:1行/1格 / L1:1行/1格 / L2:0行/0格 / L3:0行/0格 | L2 |
| valid_rate_formula_choice | L0:3行/3格 / L1:3行/3格 / L2:3行/3格 / L3:3行/3格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"store_listing_conversion_rate": 4} |
| gold_ratio_diagnostic | {} |
| invalid_rate_policy_diagnostic | {"store_listing_conversion_rate": 1} |
| valid_rate_formula_choice | {"store_listing_conversion_rate": 3} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-007_stg_google_play__stats_store_performance_traffic_source.md`。
- 重跑：`records/020_reruns_impl-007_stg_google_play__stats_store_performance_traffic_source.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
