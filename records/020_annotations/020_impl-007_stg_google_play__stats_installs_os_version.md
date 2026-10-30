# impl-007 / stg_google_play__stats_installs_os_version（全量）

## 结论

主要原因：**A**；把握：中。OS粒度活跃量映射为主因，user_uninstalls计数与布尔化另有差异。

参与因素：A：user_uninstalls（减6行/5945格）。标记：无。

## 差异与归因依据

active/current列5993行不同且均非负；契约未给映射。daily_user_uninstalls是数值，gold以CASE WHEN非零→1、agent保留数值，契约无布尔化规定；同类A参与因素。

层：staging；比较库schema：staging；评测键：date_day, package_name, os_version。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml:240–270`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_google_play__stats_installs_os_version.sql:1–15`；SHA-256 `5355d32d19d64ded1344913590da92b1b5871d001a6418594fac8679403b9c0b`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_google_play__stats_installs_os_version.sql:1–24`；SHA-256 `7b3d8ce5b1b55464b2c644fda6cbc0ce0c707a7bbc1d5262791c6f76735fad2a`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- active_devices_last_30_days（agent SQL 第6行起）：
```sql
TRY_CAST(active_device_installs AS BIGINT) AS active_devices_last_30_days
```
→
```sql
CAST(current_device_installs AS BIGINT) AS active_devices_last_30_days
```

- user_uninstalls（agent SQL 第11行起）：
```sql
TRY_CAST(daily_user_uninstalls AS BIGINT) AS user_uninstalls
```
→
```sql
CAST(CASE WHEN daily_user_uninstalls THEN 1 ELSE 0 END AS BIGINT) AS user_uninstalls
```

## agent可见证据与不确定性

不确定性四档：**只有通用策略说明**。

event 67（args.command 中报告原文）：部分原始表的字段名和契约 staging 字段名不一致，按原始 schema 映射（例如 Google Play 的 `daily_*` 指标、Apple 的 `date`/`territory`/`counts`/`event`）。

完整事件扫描数：70；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_google_play__stats_installs_os_version | False |
| 14 | 13 | stats_installs_os_version | False |
| 20 | 19 | stg_google_play__stats_installs_os_version,stats_installs_os_version | False |
| 26 | 25 | stg_google_play__stats_installs_os_version | False |
| 46 | 45 | stg_google_play__stats_installs_os_version,stats_installs_os_version | False |
| 48 | 47 | stg_google_play__stats_installs_os_version,stats_installs_os_version | False |
| 56 | 55 | stg_google_play__stats_installs_os_version | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：需要查业务说明。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='stats_installs_os_version') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "stats_installs_os_version", "_file", "VARCHAR"], ["raw", "stats_installs_os_version", "_line", "BIGINT"], ["raw", "stats_installs_os_version", "_modified", "VARCHAR"], ["raw", "stats_installs_os_version", "date", "VARCHAR"], ["raw", "stats_installs_os_version", "package_name", "VARCHAR"], ["raw", "stats_installs_os_version", "android_os_version", "VARCHAR"], ["raw", "stats_installs_os_version", "current_device_installs", "BIGINT"], ["raw", "stats_installs_os_version", "daily_device_installs", "BIGINT"], ["raw", "stats_installs_os_version", "daily_device_uninstalls", "BOOLEAN"], ["raw", "stats_installs_os_version", "daily_device_upgrades", "BOOLEAN"], ["raw", "stats_installs_os_version", "current_user_installs", "BIGINT"], ["raw", "stats_installs_os_version", "total_user_installs", "BOOLEAN"], ["raw", "stats_installs_os_version", "daily_user_installs", "BIGINT"], ["raw", "stats_installs_os_version", "daily_user_uninstalls", "BIGINT"], ["raw", "stats_installs_os_version", "active_device_installs", "BIGINT"], ["raw", "stats_installs_os_version", "install_events", "BIGINT"], ["raw", "stats_installs_os_version", "update_events", "BIGINT"], ["raw", "stats_installs_os_version", "uninstall_events", "BIGINT"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT count(*) n, count(*) FILTER(WHERE active_device_installs<>current_device_installs) unequal, min(active_device_installs) min_active, min(current_device_installs) min_current, max(active_device_installs) max_active, max(current_device_installs) max_current FROM raw.stats_installs_os_version
```

结果：`[[6000, 5993, 51, 42, 6478, 7911]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=39 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-007_stg_google_play__stats_installs_os_version/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：5999行 / 11998格；重跑基线：5999行 / 11998格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:5999行/11998格 / L1:5999行/11998格 / L2:5999行/11998格 / L3:5999行/11998格 | 均未整表匹配 |
| active_devices_last_30_days | L0:5945行/5945格 / L1:5945行/5945格 / L2:5945行/5945格 / L3:5945行/5945格 | 均未整表匹配 |
| user_uninstalls | L0:5993行/6053格 / L1:5993行/6053格 / L2:5993行/6053格 / L3:5993行/6053格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"active_devices_last_30_days": 5993, "device_installs": 10, "device_uninstalls": 4, "device_upgrades": 6, "install_events": 10, "uninstall_events": 10, "update_events": 10, "user_installs": 10, "user_uninstalls": 5945} |
| active_devices_last_30_days | {"user_uninstalls": 5945} |
| user_uninstalls | {"active_devices_last_30_days": 5993, "device_installs": 10, "device_uninstalls": 4, "device_upgrades": 6, "install_events": 10, "uninstall_events": 10, "update_events": 10, "user_installs": 10} |

本表全部重跑证据文件：`records/020_reruns_impl-007_stg_google_play__stats_installs_os_version.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-007_stg_google_play__stats_installs_os_version.md`。
- 重跑：`records/020_reruns_impl-007_stg_google_play__stats_installs_os_version.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
