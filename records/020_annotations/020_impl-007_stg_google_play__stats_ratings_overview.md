# impl-007 / stg_google_play__stats_ratings_overview（全量）

## 结论

主要原因：**O**；把握：高。agent按评级delete_row规则删9行，gold改写中值3并保留。

参与因素：无。标记：无。

## 差异与归因依据

契约对两列越界明确delete_row；raw daily_average_rating有9条越界、无NULL，total无越界。agent删除9行符合契约，gold保留并纠正值，诊断重现gold。

层：staging；比较库schema：staging；评测键：date_day, package_name。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml:59–79`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/staging/stg_google_play__stats_ratings_overview.sql:1–10`；SHA-256 `cc6cfd2051fea0cb19b37d077fac9ed7d8a8efec14ccb0d66f23579c32c3c0e3`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/staging/stg_google_play__stats_ratings_overview.sql:1–32`；SHA-256 `ac271e7781fb1f9ddddf09e187628c21166d0a6814e8196ed1348da19a0da3c6`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- gold_rating_policy_diagnostic：替换指定完整实现块（诊断）；old/new完整字节见重跑JSON，私有SQL `data/020_work/impl-007_stg_google_play__stats_ratings_overview/gold_rating_policy_diagnostic.sql`。

## agent可见证据与不确定性

不确定性四档：**只有通用策略说明**。

event67：随后修正了输出列顺序及评级规则：无效的必需平均评级记录删除、契约指定 nullify 的评级/转化率置空或删除。

完整事件扫描数：70；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_google_play__stats_ratings_overview | False |
| 14 | 13 | stats_ratings_overview | False |
| 16 | 15 | stats_ratings_overview | False |
| 18 | 17 | stg_google_play__stats_ratings_overview,stats_ratings_overview | False |
| 20 | 19 | stg_google_play__stats_ratings_overview,stats_ratings_overview | False |
| 26 | 25 | stg_google_play__stats_ratings_overview | False |
| 46 | 45 | stg_google_play__stats_ratings_overview,stats_ratings_overview | False |
| 48 | 47 | stg_google_play__stats_ratings_overview,stats_ratings_overview | False |
| 56 | 55 | stg_google_play__stats_ratings_overview | False |
| 62 | 61 | stats_ratings_overview | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='stats_ratings_overview') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "stats_ratings_overview", "Unnamed: 0", "BIGINT"], ["raw", "stats_ratings_overview", "_file", "VARCHAR"], ["raw", "stats_ratings_overview", "_line", "BIGINT"], ["raw", "stats_ratings_overview", "_modified", "VARCHAR"], ["raw", "stats_ratings_overview", "date", "VARCHAR"], ["raw", "stats_ratings_overview", "package_name", "VARCHAR"], ["raw", "stats_ratings_overview", "daily_average_rating", "DOUBLE"], ["raw", "stats_ratings_overview", "total_average_rating", "DOUBLE"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE daily_average_rating IS NULL) null_daily,count(*) FILTER(WHERE daily_average_rating NOT BETWEEN 1 AND 5) invalid_daily,count(*) FILTER(WHERE total_average_rating NOT BETWEEN 1 AND 5) invalid_total FROM raw.stats_ratings_overview
```

结果：`[[700, 0, 9, 0]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=41 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-007_stg_google_play__stats_ratings_overview/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：9行 / 36格；重跑基线：9行 / 36格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:9行/36格 / L1:9行/36格 / L2:9行/36格 / L3:9行/36格 | 均未整表匹配 |
| gold_rating_policy_diagnostic | L0:0行/0格 / L1:0行/0格 / L2:0行/0格 / L3:0行/0格 | L0 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {} |
| gold_rating_policy_diagnostic | {} |

本表全部重跑证据文件：`records/020_reruns_impl-007_stg_google_play__stats_ratings_overview.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-007_stg_google_play__stats_ratings_overview.md`。
- 重跑：`records/020_reruns_impl-007_stg_google_play__stats_ratings_overview.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
