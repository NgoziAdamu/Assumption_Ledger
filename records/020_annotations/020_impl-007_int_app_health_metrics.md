> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-007 / int_app_health_metrics（全量）

## 结论

主要原因：**A**；把握：中。同一app/platform/date存在重复行，ROWS窗口未规定同日顺序。

参与因素：无。标记：无。

## 差异与归因依据

契约仅ORDER BY date_day，未指定同日次序。实际297组同日重复，304条超额行；用gold SQL重新执行仍不复现留存gold窗口值，排除全部窗口及派生列后基准行多重集L0完全一致。差异取决于未规定的同日排序；不能为了匹配gold捏造唯一排序规则。

层：intermediate；比较库schema：intermediate；评测键：date_day。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml:901–1064`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/intermediate/int_app_health_metrics.sql:1–18`；SHA-256 `b3f7f3947c1bec6d479cea78d32e30bf496775370e9446dc4350f840566b9012`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/intermediate/int_app_health_metrics.sql:1–283`；SHA-256 `be637d264ed8b7a5e3adbc802190381b60e0abcd1ec59c79f0156c4a6eaa08be`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- peer_order_diagnostic：
```sql
ORDER BY date_day ROWS BETWEEN 6
```
→
```sql
ORDER BY date_day,installs,uninstalls,crash_count ROWS BETWEEN 6
```

- peer_order_diagnostic：
```sql
ORDER BY date_day ROWS BETWEEN 29
```
→
```sql
ORDER BY date_day,installs,uninstalls,crash_count ROWS BETWEEN 29
```

- gold_sql_diagnostic：替换指定完整实现块（诊断）；old/new完整字节见重跑JSON，私有SQL `data/020_work/impl-007_int_app_health_metrics/gold_sql_diagnostic.sql`。

## agent可见证据与不确定性

不确定性四档：**看到了但没提**。

event14可见上游schema，event16看过installs样例；event29生成ROWS窗口，event56核对health列。70事件未找到同日peer排序或唯一性检验的说明。

完整事件扫描数：70；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | int_app_health_metrics,stg_apple_store__app_crash_daily,stg_apple_store__app_store_download_standard_daily,stg_google_play__stats_crashes_overview,stg_google_play__stats_installs_overview,stg_google_play__stats_ratings_overview | False |
| 18 | 17 | stg_apple_store__app_store_download_standard_daily,stg_google_play__stats_crashes_overview,stg_google_play__stats_installs_overview,stg_google_play__stats_ratings_overview | False |
| 20 | 19 | int_app_health_metrics,stg_apple_store__app_crash_daily,stg_apple_store__app_store_download_standard_daily,stg_google_play__stats_crashes_overview,stg_google_play__stats_installs_overview,stg_google_play__stats_ratings_overview | False |
| 22 | 21 | int_app_health_metrics | False |
| 26 | 25 | stg_apple_store__app_crash_daily,stg_apple_store__app_store_download_standard_daily,stg_google_play__stats_crashes_overview,stg_google_play__stats_installs_overview,stg_google_play__stats_ratings_overview | False |
| 44 | 43 | int_app_health_metrics,stg_apple_store__app_store_download_standard_daily,stg_google_play__stats_crashes_overview,stg_google_play__stats_installs_overview | False |
| 46 | 45 | stg_apple_store__app_crash_daily,stg_apple_store__app_store_download_standard_daily,stg_google_play__stats_crashes_overview,stg_google_play__stats_installs_overview,stg_google_play__stats_ratings_overview | False |
| 48 | 47 | int_app_health_metrics,stg_apple_store__app_crash_daily,stg_apple_store__app_store_download_standard_daily,stg_google_play__stats_crashes_overview,stg_google_play__stats_installs_overview,stg_google_play__stats_ratings_overview | False |
| 56 | 55 | int_app_health_metrics,stg_apple_store__app_crash_daily,stg_apple_store__app_store_download_standard_daily,stg_google_play__stats_crashes_overview,stg_google_play__stats_installs_overview,stg_google_play__stats_ratings_overview | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：3；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='staging' AND table_name='stg_apple_store__app_crash_daily') OR (table_schema='staging' AND table_name='stg_apple_store__app_store_download_standard_daily') OR (table_schema='staging' AND table_name='stg_google_play__stats_crashes_overview') OR (table_schema='staging' AND table_name='stg_google_play__stats_installs_overview') OR (table_schema='staging' AND table_name='stg_google_play__stats_ratings_overview') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["staging", "stg_apple_store__app_crash_daily", "source_relation", "VARCHAR"], ["staging", "stg_apple_store__app_crash_daily", "date_day", "DATE"], ["staging", "stg_apple_store__app_crash_daily", "app_name", "VARCHAR"], ["staging", "stg_apple_store__app_crash_daily", "app_version", "VARCHAR"], ["staging", "stg_apple_store__app_crash_daily", "device", "VARCHAR"], ["staging", "stg_apple_store__app_crash_daily", "platform_version", "VARCHAR"], ["staging", "stg_apple_store__app_crash_daily", "crashes", "BIGINT"], ["staging", "stg_apple_store__app_crash_daily", "unique_devices_with_crashes", "BIGINT"], ["staging", "stg_apple_store__app_store_download_standard_daily", "source_relation", "VARCHAR"], ["staging", "stg_apple_store__app_store_download_standard_daily", "date_day", "DATE"], ["staging", "stg_apple_store__app_store_download_standard_daily", "app_name", "VARCHAR"], ["staging", "stg_apple_store__app_store_download_standard_daily", "country", "VARCHAR"], ["staging", "stg_apple_store__app_store_download_standard_daily", "total_downloads", "BIGINT"], ["staging", "stg_apple_store__app_store_download_standard_daily", "download_type", "VARCHAR"], ["staging", "stg_apple_store__app_store_download_standard_daily", "device", "VARCHAR"], ["staging", "stg_apple_store__app_store_download_standard_daily", "app_version", "VARCHAR"], ["staging", "stg_apple_store__app_store_download_standard_daily", "source_type", "VARCHAR"], ["staging", "stg_apple_store__app_store_download_standard_daily", "platform_version", "VARCHAR"], ["staging", "stg_google_play__stats_crashes_overview", "source_relation", "VARCHAR"], ["staging", "stg_google_play__stats_crashes_overview", "date_day", "DATE"], ["staging", "stg_google_play__stats_crashes_overview", "package_name", "VARCHAR"], ["staging", "stg_google_play__stats_crashes_overview", "crashes", "BIGINT"], ["staging", "stg_google_play__stats_crashes_overview", "anrs", "BIGINT"], ["staging", "stg_google_play__stats_installs_overview", "source_relation", "VARCHAR"], ["staging", "stg_google_play__stats_installs_overview", "date_day", "DATE"], ["staging", "stg_google_play__stats_installs_overview", "package_name", "VARCHAR"], ["staging", "stg_google_play__stats_installs_overview", "active_devices_last_30_days", "BIGINT"], ["staging", "stg_google_play__stats_installs_overview", "device_installs", "BIGINT"], ["staging", "stg_google_play__stats_installs_overview", "device_uninstalls", "BIGINT"], ["staging", "stg_google_play__stats_installs_overview", "device_upgrades", "BIGINT"], ["staging", "stg_google_play__stats_installs_overview", "user_installs", "BIGINT"], ["staging", "stg_google_play__stats_installs_overview", "user_uninstalls", "BIGINT"], ["staging", "stg_google_play__stats_installs_overview", "install_events", "BIGINT"], ["staging", "stg_google_play__stats_installs_overview", "uninstall_events", "BIGINT"], ["staging", "stg_google_play__stats_installs_overview", "update_events", "BIGINT"], ["staging", "stg_google_play__stats_ratings_overview", "source_relation", "VARCHAR"], ["staging", "stg_google_play__stats_ratings_overview", "date_day", "DATE"], ["staging", "stg_google_play__stats_ratings_overview", "package_name", "VARCHAR"], ["staging", "stg_google_play__stats_ratings_overview", "average_rating", "DECIMAL(10,2)"], ["staging", "stg_google_play__stats_ratings_overview", "rolling_total_average_rating", "DECIMAL(10,2)"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT 'staging.stg_apple_store__app_crash_daily' source,count(*) duplicate_groups,sum(n-1) extra_rows FROM (SELECT date_day,app_name,count(*) n FROM staging.stg_apple_store__app_crash_daily GROUP BY ALL HAVING count(*)>1) UNION ALL SELECT 'staging.stg_apple_store__app_store_download_standard_daily' source,count(*) duplicate_groups,sum(n-1) extra_rows FROM (SELECT date_day,app_name,count(*) n FROM staging.stg_apple_store__app_store_download_standard_daily GROUP BY ALL HAVING count(*)>1) UNION ALL SELECT 'staging.stg_google_play__stats_crashes_overview' source,count(*) duplicate_groups,sum(n-1) extra_rows FROM (SELECT date_day,package_name,count(*) n FROM staging.stg_google_play__stats_crashes_overview GROUP BY ALL HAVING count(*)>1) UNION ALL SELECT 'staging.stg_google_play__stats_installs_overview' source,count(*) duplicate_groups,sum(n-1) extra_rows FROM (SELECT date_day,package_name,count(*) n FROM staging.stg_google_play__stats_installs_overview GROUP BY ALL HAVING count(*)>1) UNION ALL SELECT 'staging.stg_google_play__stats_ratings_overview' source,count(*) duplicate_groups,sum(n-1) extra_rows FROM (SELECT date_day,package_name,count(*) n FROM staging.stg_google_play__stats_ratings_overview GROUP BY ALL HAVING count(*)>1)
```

失败：Parser Error: syntax error at or near "source"

LINE 1: SELECT 'staging.stg_apple_store__app_crash_daily' source,count(*) duplicate_groups,sum(n-1) extra_rows FROM...
                                                          ^

### 核实 3

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT 'staging.stg_google_play__stats_crashes_overview' AS source_table,count(*) duplicate_groups,sum(n-1) extra_rows FROM (SELECT date_day,package_name,count(*) n FROM staging.stg_google_play__stats_crashes_overview GROUP BY ALL HAVING count(*)>1) UNION ALL SELECT 'staging.stg_google_play__stats_installs_overview' AS source_table,count(*) duplicate_groups,sum(n-1) extra_rows FROM (SELECT date_day,package_name,count(*) n FROM staging.stg_google_play__stats_installs_overview GROUP BY ALL HAVING count(*)>1) UNION ALL SELECT 'staging.stg_google_play__stats_ratings_overview' AS source_table,count(*) duplicate_groups,sum(n-1) extra_rows FROM (SELECT date_day,package_name,count(*) n FROM staging.stg_google_play__stats_ratings_overview GROUP BY ALL HAVING count(*)>1) UNION ALL SELECT 'staging.stg_apple_store__app_crash_daily' AS source_table,count(*) duplicate_groups,sum(n-1) extra_rows FROM (SELECT date_day,app_name,count(*) n FROM staging.stg_apple_store__app_crash_daily GROUP BY ALL HAVING count(*)>1) UNION ALL SELECT 'staging.stg_apple_store__app_store_download_standard_daily' AS source_table,count(*) duplicate_groups,sum(n-1) extra_rows FROM (SELECT date_day,app_name,count(*) n FROM staging.stg_apple_store__app_store_download_standard_daily GROUP BY ALL HAVING count(*)>1)
```

结果：`[["staging.stg_google_play__stats_crashes_overview", 2, 2], ["staging.stg_google_play__stats_installs_overview", 274, 281], ["staging.stg_google_play__stats_ratings_overview", 8, 8], ["staging.stg_apple_store__app_crash_daily", 6, 6], ["staging.stg_apple_store__app_store_download_standard_daily", 7, 7]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=32 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-007_int_app_health_metrics/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：550行 / 963格；重跑基线：550行 / 963格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:550行/963格 / L1:550行/963格 / L2:490行/897格 / L3:490行/897格 | 均未整表匹配 |
| peer_order_diagnostic | L0:533行/938格 / L1:533行/938格 / L2:467行/867格 / L3:467行/867格 | 均未整表匹配 |
| gold_sql_diagnostic | L0:508行/871格 / L1:508行/871格 / L2:455行/815格 / L3:455行/815格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"crashes_30d_sum": 8, "installs": 28, "installs_30d_sum": 339, "total_activity": 28, "uninstall_rate_7d_avg": 492, "uninstall_rate_percentage": 28, "uninstalls": 28, "volume_tier": 12} |
| peer_order_diagnostic | {"crashes_30d_sum": 12, "installs": 30, "installs_30d_sum": 320, "total_activity": 32, "uninstall_rate_7d_avg": 466, "uninstall_rate_percentage": 32, "uninstalls": 32, "volume_tier": 14} |
| gold_sql_diagnostic | {"crashes_30d_sum": 6, "installs": 20, "installs_30d_sum": 314, "total_activity": 20, "uninstall_rate_7d_avg": 456, "uninstall_rate_percentage": 20, "uninstalls": 20, "volume_tier": 15} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

手册O例子要求契约明确允许任意顺序；本契约只规定按date_day且声称来源唯一，没有明确允许同日任意顺序。本次选A（未定义tie-break），不扩大O定义。虽然唯一性假设实际不成立，但不能证明某种独立修复就是唯一应有的窗口结果，因此不强行归U。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-007_int_app_health_metrics.md`。
- 重跑：`records/020_reruns_impl-007_int_app_health_metrics.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
