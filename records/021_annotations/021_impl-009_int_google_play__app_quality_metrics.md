# impl-009 / int_google_play__app_quality_metrics（全量）

## 结论

主要原因：**D**；把握：高。app quality的滚动均值、版本/OS指标和趋势被NULL或常量代替。

参与因素：无经单修确认的其他参与因素。标记：已披露。

## 差异与归因依据

契约明确7日窗口及按版本/OS汇总；agent仅投影crashes_overview，将可计算项NULL占位。两个滚动均值分别单修，另以完整实现诊断遗漏的连接/分类；完整实现仍有3行差异，不能声称L0全匹配。

层：intermediate；实际schema：intermediate；评测键：date_day, package_name。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml:993–1102`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql:1–24`，SHA-256 `9eca93d98d48211f80bcb3e23d5f8610ed393bd7aa263775978bed8c7fee4de7`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/intermediate/int_google_play__app_quality_metrics.sql:1–261`，SHA-256 `554ab7b99208b0fc3a2a014a75396e4369882f31d44afe41f08d17cdda3c1e0d`。

- whole_implementation_diagnostic：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_reruns_impl-009_int_google_play__app_quality_metrics.json`。

- avg_7d_crashes：agent SQL第9行起：
```sql
CAST(NULL AS DOUBLE) AS avg_7d_crashes
```
替换为：
```sql
CAST(round(AVG(crashes) OVER(PARTITION BY package_name ORDER BY date_day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),2) AS DOUBLE) AS avg_7d_crashes
```

- avg_7d_anrs：agent SQL第10行起：
```sql
CAST(NULL AS DOUBLE) AS avg_7d_anrs
```
替换为：
```sql
CAST(round(AVG(anrs) OVER(PARTITION BY package_name ORDER BY date_day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),2) AS DOUBLE) AS avg_7d_anrs
```

## agent可见证据与不确定性

**针对本表的具体说明**。

event67：留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。

最终报告原句（其适用范围按上文判定）：

> 本次交付**未完整实现数据合同中的全部业务逻辑**。留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。`run.py` 成功只能证明 SQL 可执行，不能证明输出满足全部业务定义或可用于生产分析。

> - Earnings 源数据 `transaction_date` 为空而 `transaction_time` 有值；为提供可用日期，暂用 `transaction_time` 日期部分回填。源 SKU 为空时用可用的 product/base-plan 值兜底。

扫描69个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=8。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 20 | 19 | False |
| 24 | 23 | False |
| 38 | 37 | False |
| 42 | 41 | False |
| 44 | 43 | False |
| 54 | 53 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：3；核实代价档：多条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT 'staging.stg_google_play__stats_crashes_overview' source,count(*) n FROM staging.stg_google_play__stats_crashes_overview
```

失败：Parser Error: syntax error at or near "source"

LINE 1: SELECT 'staging.stg_google_play__stats_crashes_overview' source,count(*) n FROM staging.stg_google_play__stats_crash...
                                                                 ^

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT 'staging.stg_google_play__stats_crashes_overview' source_name,count(*) n FROM staging.stg_google_play__stats_crashes_overview
```

结果（列顺序["source_name", "n"]）：`[["staging.stg_google_play__stats_crashes_overview", 2928]]`

### 核实 3

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`；记录：`records/021_final_diagnostics.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE daily_average_rating BETWEEN 1 AND 5) valid_ratings FROM staging.stg_google_play__stats_ratings_overview
```

结果（列顺序["n", "valid_ratings"]）：`[[2928, 2928]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：2928行/10884格；选定基线：2928行/10884格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 2928行/10884格；L1 2928行/10884格；L2 2928行/10884格；L3 2928行/10884格 | 均未整表匹配 |
| whole_implementation_diagnostic | L0 3行/9格；L1 3行/9格；L2 3行/9格；L3 3行/9格 | 均未整表匹配 |
| avg_7d_crashes | L0 2928行/7956格；L1 2928行/7956格；L2 2928行/7956格；L3 2928行/7956格 | 均未整表匹配 |
| avg_7d_anrs | L0 2928行/7956格；L1 2928行/7956格；L2 2928行/7956格；L3 2928行/7956格 | 均未整表匹配 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"active_versions_count": 272, "avg_7d_anrs": 2928, "avg_7d_crashes": 2928, "os_with_most_crashes": 272, "stability_trend": 2852, "supported_os_versions": 272, "version_with_most_crashes": 272, "worst_os_anrs": 272, "worst_os_crashes": 272, "worst_version_anrs": 272, "worst_version_crashes": 272} |
| whole_implementation_diagnostic | {"os_with_most_crashes": 2, "version_with_most_crashes": 1, "worst_os_anrs": 2, "worst_os_crashes": 2, "worst_version_anrs": 1, "worst_version_crashes": 1} |
| avg_7d_crashes | {"active_versions_count": 272, "avg_7d_anrs": 2928, "os_with_most_crashes": 272, "stability_trend": 2852, "supported_os_versions": 272, "version_with_most_crashes": 272, "worst_os_anrs": 272, "worst_os_crashes": 272, "worst_version_anrs": 272, "worst_version_crashes": 272} |
| avg_7d_anrs | {"active_versions_count": 272, "avg_7d_crashes": 2928, "os_with_most_crashes": 272, "stability_trend": 2852, "supported_os_versions": 272, "version_with_most_crashes": 272, "worst_os_anrs": 272, "worst_os_crashes": 272, "worst_version_anrs": 272, "worst_version_crashes": 272} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

无。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-009_int_google_play__app_quality_metrics.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-009_int_google_play__app_quality_metrics/021_impl-009_int_google_play__app_quality_metrics.json`。
- 重跑：`records/021_reruns_impl-009_int_google_play__app_quality_metrics.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_extra_reruns_impl-009_int_google_play__app_quality_metrics.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
