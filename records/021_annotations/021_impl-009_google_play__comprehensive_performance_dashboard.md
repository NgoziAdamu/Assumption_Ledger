# impl-009 / google_play__comprehensive_performance_dashboard（全量）

## 结论

主要原因：**D**；把握：高。综合仪表板只保留user_behavior来源，CS下为空而gold有3568行。

参与因素：无经单修确认的其他参与因素。标记：已披露。

## 差异与归因依据

契约要求overview、user_behavior、revenue多源FULL OUTER JOIN并计算评分。agent只读空的user_behavior，其他指标占位，未做关于可计算性的具体数据判断。整体缺失的多源实现作为D，完整实现诊断L0一致，不称为U局部修复。

层：marts；实际schema：mart；评测键：date_day, package_name。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml:1140–1223`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__comprehensive_performance_dashboard.sql:1–40`，SHA-256 `cd6a49f2020efd454d71e81b434e6c22b8d81854910386fa46e7d02e24153ba4`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/marts/google_play__comprehensive_performance_dashboard.sql:1–272`，SHA-256 `41969d7b74c218a6b7f5dd882aa04c4982959f8ea157febc74d97ab09cfee751`。

- whole_implementation_diagnostic：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_reruns_impl-009_google_play__comprehensive_performance_dashboard.json`。

## agent可见证据与不确定性

**只有通用策略说明**。

event35生成首源fallback；event67披露“多项 marts”的连接/窗口/评分未完整实现，但未具体说明本表丢失其他来源。

最终报告原句（其适用范围按上文判定）：

> 本次交付**未完整实现数据合同中的全部业务逻辑**。留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。`run.py` 成功只能证明 SQL 可执行，不能证明输出满足全部业务定义或可用于生产分析。

> - Earnings 源数据 `transaction_date` 为空而 `transaction_time` 有值；为提供可用日期，暂用 `transaction_time` 日期部分回填。源 SKU 为空时用可用的 product/base-plan 值兜底。

扫描69个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=10。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 38 | 37 | False |
| 42 | 41 | False |
| 44 | 43 | False |
| 54 | 53 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：2；核实代价档：多条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT 'intermediate.int_google_play__user_behavior_metrics' source,count(*) n FROM intermediate.int_google_play__user_behavior_metrics
```

失败：Parser Error: syntax error at or near "source"

LINE 1: ...LECT 'intermediate.int_google_play__user_behavior_metrics' source,count(*) n FROM intermediate.int_google_play__user_b...
                                                                      ^

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/google_play.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT 'intermediate.int_google_play__user_behavior_metrics' source_name,count(*) n FROM intermediate.int_google_play__user_behavior_metrics
```

结果（列顺序["source_name", "n"]）：`[["intermediate.int_google_play__user_behavior_metrics", 0]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：3568行/124880格；选定基线：3568行/124880格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 3568行/124880格；L1 3568行/124880格；L2 3568行/124880格；L3 3568行/124880格 | 均未整表匹配 |
| whole_implementation_diagnostic | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {} |
| whole_implementation_diagnostic | {} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

无。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-009_google_play__comprehensive_performance_dashboard.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-009_google_play__comprehensive_performance_dashboard/021_impl-009_google_play__comprehensive_performance_dashboard.json`。
- 重跑：`records/021_reruns_impl-009_google_play__comprehensive_performance_dashboard.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
