# impl-007 / app_reporting__overview_report（全量）

## 结论

主要原因：**O**；把握：高。agent按名UNION ALL符合契约，gold按位置UNION交换了Apple下载/删除列。

参与因素：无。标记：无。

## 差异与归因依据

契约明确值原样传递。gold Google upstream第5列deletions、第6列downloads，Apple顺序相反；SELECT * UNION ALL按位置拼接后再按Google列名取值。交换Apple两列的诊断与gold全表EXCEPT ALL残余0；agent无此交换。

层：marts；比较库schema：mart；评测键：date_day。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml:2421–2452`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/marts/app_reporting__overview_report.sql:1–1`；SHA-256 `febfc2255732877727c3a088c32ac0cc0b9962452f264b42e6b7661de860cd11`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/marts/app_reporting__overview_report.sql:1–28`；SHA-256 `4bb328b3d7fbdc3b3b9baf633fd574e094cc0f590e2d124148d08e6c21817d9e`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- gold_positional_union_diagnostic：替换指定完整实现块（诊断）；old/new完整字节见重跑JSON，私有SQL `data/020_work/impl-007_app_reporting__overview_report/gold_positional_union_diagnostic.sql`。

## agent可见证据与不确定性

不确定性四档：**看到了但没提**。

event33写显式列名UNION，event56核对输出列名；未找到对两个来源列顺序差异的说明。

完整事件扫描数：70；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | app_reporting__overview_report,int_apple_store__overview,int_google_play__overview | False |
| 20 | 19 | app_reporting__overview_report,int_apple_store__overview,int_google_play__overview | False |
| 22 | 21 | app_reporting__overview_report,int_apple_store__overview,int_google_play__overview | False |
| 44 | 43 | app_reporting__overview_report,int_google_play__overview | False |
| 46 | 45 | int_apple_store__overview,int_google_play__overview | False |
| 48 | 47 | app_reporting__overview_report,int_apple_store__overview,int_google_play__overview | False |
| 56 | 55 | app_reporting__overview_report,int_apple_store__overview,int_google_play__overview | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：1；核实代价档：一条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='intermediate' AND table_name='int_apple_store__overview') OR (table_schema='intermediate' AND table_name='int_google_play__overview') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["intermediate", "int_apple_store__overview", "source_relation", "VARCHAR"], ["intermediate", "int_apple_store__overview", "date_day", "DATE"], ["intermediate", "int_apple_store__overview", "app_platform", "VARCHAR"], ["intermediate", "int_apple_store__overview", "app_name", "VARCHAR"], ["intermediate", "int_apple_store__overview", "downloads", "HUGEINT"], ["intermediate", "int_apple_store__overview", "deletions", "HUGEINT"], ["intermediate", "int_apple_store__overview", "page_views", "HUGEINT"], ["intermediate", "int_apple_store__overview", "crashes", "INTEGER"], ["intermediate", "int_google_play__overview", "source_relation", "VARCHAR"], ["intermediate", "int_google_play__overview", "date_day", "DATE"], ["intermediate", "int_google_play__overview", "app_platform", "VARCHAR"], ["intermediate", "int_google_play__overview", "app_name", "VARCHAR"], ["intermediate", "int_google_play__overview", "deletions", "BIGINT"], ["intermediate", "int_google_play__overview", "downloads", "BIGINT"], ["intermediate", "int_google_play__overview", "page_views", "INTEGER"], ["intermediate", "int_google_play__overview", "crashes", "BIGINT"]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=33 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-007_app_reporting__overview_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：693行 / 1386格；重跑基线：693行 / 1386格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:693行/1386格 / L1:693行/1386格 / L2:693行/1386格 / L3:693行/1386格 | 均未整表匹配 |
| gold_positional_union_diagnostic | L0:0行/0格 / L1:0行/0格 / L2:0行/0格 / L3:0行/0格 | L0 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"deletions": 693, "downloads": 693} |
| gold_positional_union_diagnostic | {} |

本表全部重跑证据文件：`records/020_reruns_impl-007_app_reporting__overview_report.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-007_app_reporting__overview_report.md`。
- 重跑：`records/020_reruns_impl-007_app_reporting__overview_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
