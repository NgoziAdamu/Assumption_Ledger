> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-007 / stg_google_play__stats_installs_device（全量）

## 结论

主要原因：**A**；把握：中。设备粒度的30日活跃量源列选择未规定。

参与因素：无。标记：无。

## 差异与归因依据

active与current两列5994行不同，均是合法非负计数；缺少字段字典不能判定哪列承载30日活跃语义。单改current列L0匹配。

层：staging；比较库schema：staging；评测键：date_day, package_name, device。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml:383–413`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_google_play__stats_installs_device.sql:1–15`；SHA-256 `20cbdc8001875d6b6e716c84b0ba4a927f2cd8c16fd20dc6d4dde0635c820a7a`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_google_play__stats_installs_device.sql:1–24`；SHA-256 `d1ca25678901b65a55a5e5f3f2e389abb68365073c145ad1359fe4a7ccd30080`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- active_devices_last_30_days：
```sql
TRY_CAST(active_device_installs AS BIGINT) AS active_devices_last_30_days
```
→
```sql
CAST(current_device_installs AS BIGINT) AS active_devices_last_30_days
```

## agent可见证据与不确定性

不确定性四档：**只有通用策略说明**。

event 67（args.command 中报告原文）：部分原始表的字段名和契约 staging 字段名不一致，按原始 schema 映射（例如 Google Play 的 `daily_*` 指标、Apple 的 `date`/`territory`/`counts`/`event`）。

完整事件扫描数：70；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_google_play__stats_installs_device | False |
| 14 | 13 | stats_installs_device | False |
| 20 | 19 | stg_google_play__stats_installs_device,stats_installs_device | False |
| 26 | 25 | stg_google_play__stats_installs_device | False |
| 46 | 45 | stg_google_play__stats_installs_device,stats_installs_device | False |
| 48 | 47 | stg_google_play__stats_installs_device,stats_installs_device | False |
| 56 | 55 | stg_google_play__stats_installs_device | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：需要查业务说明。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='stats_installs_device') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "stats_installs_device", "_file", "VARCHAR"], ["raw", "stats_installs_device", "_line", "BIGINT"], ["raw", "stats_installs_device", "_modified", "VARCHAR"], ["raw", "stats_installs_device", "date", "VARCHAR"], ["raw", "stats_installs_device", "package_name", "VARCHAR"], ["raw", "stats_installs_device", "device", "VARCHAR"], ["raw", "stats_installs_device", "current_device_installs", "BIGINT"], ["raw", "stats_installs_device", "daily_device_installs", "BIGINT"], ["raw", "stats_installs_device", "daily_device_uninstalls", "BOOLEAN"], ["raw", "stats_installs_device", "daily_device_upgrades", "BOOLEAN"], ["raw", "stats_installs_device", "current_user_installs", "BIGINT"], ["raw", "stats_installs_device", "total_user_installs", "BIGINT"], ["raw", "stats_installs_device", "daily_user_installs", "BIGINT"], ["raw", "stats_installs_device", "daily_user_uninstalls", "BOOLEAN"], ["raw", "stats_installs_device", "active_device_installs", "BIGINT"], ["raw", "stats_installs_device", "install_events", "BIGINT"], ["raw", "stats_installs_device", "update_events", "BIGINT"], ["raw", "stats_installs_device", "uninstall_events", "BIGINT"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT count(*) n, count(*) FILTER(WHERE active_device_installs<>current_device_installs) unequal, min(active_device_installs) min_active, min(current_device_installs) min_current, max(active_device_installs) max_active, max(current_device_installs) max_current FROM raw.stats_installs_device
```

结果：`[[6000, 5994, 48, 37, 6470, 7866]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=38 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-007_stg_google_play__stats_installs_device/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：5994行 / 6082格；重跑基线：5994行 / 6082格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:5994行/6082格 / L1:5994行/6070格 / L2:5994行/6070格 / L3:5994行/6070格 | 均未整表匹配 |
| active_devices_last_30_days | L0:0行/0格 / L1:0行/0格 / L2:0行/0格 / L3:0行/0格 | L0 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"active_devices_last_30_days": 5994, "device_installs": 14, "device_uninstalls": 8, "device_upgrades": 2, "install_events": 14, "uninstall_events": 14, "update_events": 14, "user_installs": 14, "user_uninstalls": 8} |
| active_devices_last_30_days | {} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-007_stg_google_play__stats_installs_device.md`。
- 重跑：`records/020_reruns_impl-007_stg_google_play__stats_installs_device.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
