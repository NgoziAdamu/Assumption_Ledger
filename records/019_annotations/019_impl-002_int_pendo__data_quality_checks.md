# impl-002 / int_pendo__data_quality_checks

## 结论

主要原因：**D**；把握：中；标记：已披露。

summary-only 降级遗漏所有详情；单独恢复 event completeness 行。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**针对本表的具体说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-002_int_pendo__data_quality_checks.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：1/13。本次固定控制下 baseline 行/格规模：13/63。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml`；原文行段 855–888。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__data_quality_checks.sql`，L1–1；SHA-256 `c73548741676e998fb4f7d29a648f30e697f74af489da1c3b52c3791f8292d69`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/intermediate/int_pendo__data_quality_checks.sql`，L1–298；SHA-256 `47ae7bd5373d51722e0dfe9f3a4b2719fb14fa834cfe80f444ad22ae0d03a785`。

completeness_rows：agent SQL L1，替换原片段如下。
```sql
SELECT 'Data Quality Summary'::VARCHAR report_section,NULL::VARCHAR completeness_score,NULL::FLOAT consistency_score,NULL::FLOAT business_logic_score,NULL::FLOAT overall_quality_score,'Poor'::VARCHAR quality_grade,current_timestamp calculated_at
```
替换为：
```sql
SELECT 'Data Quality Summary'::VARCHAR report_section,NULL::VARCHAR completeness_score,NULL::FLOAT consistency_score,NULL::FLOAT business_logic_score,NULL::FLOAT overall_quality_score,'Poor'::VARCHAR quality_grade,current_timestamp calculated_at UNION ALL SELECT 'Data Completeness Details', 'event', count(*)::FLOAT, count(*) FILTER(WHERE visitor_id IS NULL)::FLOAT, count(*) FILTER(WHERE account_id IS NULL)::FLOAT, count(*) FILTER(WHERE occurred_at IS NULL)::VARCHAR, current_timestamp FROM staging.stg_pendo__event
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-002_int_pendo__data_quality_checks.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 13 | 63 | {"business_logic_score": 1, "consistency_score": 1, "overall_quality_score": 1} | L0–L3均不匹配 |
| baseline | L1 | 13 | 63 | {"business_logic_score": 1, "consistency_score": 1, "overall_quality_score": 1} | L0–L3均不匹配 |
| baseline | L2 | 13 | 63 | {"business_logic_score": 1, "consistency_score": 1, "overall_quality_score": 1} | L0–L3均不匹配 |
| baseline | L3 | 13 | 63 | {"business_logic_score": 1, "consistency_score": 1, "overall_quality_score": 1} | L0–L3均不匹配 |
| completeness_rows | L0 | 12 | 58 | {"business_logic_score": 1, "consistency_score": 1, "overall_quality_score": 1} | L0–L3均不匹配 |
| completeness_rows | L1 | 12 | 58 | {"business_logic_score": 1, "consistency_score": 1, "overall_quality_score": 1} | L0–L3均不匹配 |
| completeness_rows | L2 | 12 | 58 | {"business_logic_score": 1, "consistency_score": 1, "overall_quality_score": 1} | L0–L3均不匹配 |
| completeness_rows | L3 | 12 | 58 | {"business_logic_score": 1, "consistency_score": 1, "overall_quality_score": 1} | L0–L3均不匹配 |

- completeness_rows（D，单处 SQL 改动）：行减少 1，格减少 5。summary-only 降级遗漏所有详情；单独恢复 event completeness 行。

## agent 可见证据及不确定性

event 59 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，字段字符偏移 1215。

> Several complex outputs remain simplified relative to the detailed contract: product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations; the data-quality report is summary-only; RFM account-level metrics are NULL placeholders; and advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

错误点粒度存在两种读法：每个占位输出列分别算一处，或将同一遗漏聚合/规则模块视为一个降级错误点。本次以模块为错误点，列出全部可见占位及残余列统计，以局部恢复模块内表达式/来源证明贡献；没有用整份 gold SQL 替换来宣称因果成立。未逐一补齐全部占位列，不能据局部修法宣称已覆盖模块内所有修复。若后续决定按列拆分，需重新比较这些因素的贡献排序。
