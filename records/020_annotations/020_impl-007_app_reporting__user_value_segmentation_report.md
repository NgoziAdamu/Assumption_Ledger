# impl-007 / app_reporting__user_value_segmentation_report（全量）

## 结论

主要原因：**O**；把握：高。ROI类别文本按契约输出High/Medium/Low/Uncertain，而gold使用另一组长文本。

参与因素：无。标记：无。

## 差异与归因依据

契约business_logic与列description均明定短标签，agent逐字实现；gold输出High ROI Expected等。只替换文本后L2全匹配，余下CLV差异为浮点聚合末位。

层：marts；比较库schema：mart；评测键：customer_segment。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml:1827–1910`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/marts/app_reporting__user_value_segmentation_report.sql:1–10`；SHA-256 `25375aeaf95d37177cfc5f6d71844b111a444a3d4c406b4b7baa7dae66ee1aa4`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/marts/app_reporting__user_value_segmentation_report.sql:1–248`；SHA-256 `e1f189c698ae9c8b4c6b8f80dc676143649e164588af8e5041c75880443d1a31`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- gold_roi_labels_diagnostic（agent SQL 第7行起）：
```sql
CASE WHEN global_avg_clv>500 THEN 'High' WHEN global_avg_clv>200 THEN 'Medium' WHEN global_avg_clv>50 THEN 'Low' ELSE 'Uncertain' END roi_expectation
```
→
```sql
CASE WHEN global_avg_clv>500 THEN 'High ROI Expected' WHEN global_avg_clv>200 THEN 'Medium ROI Expected' WHEN global_avg_clv>50 THEN 'Low ROI Expected' ELSE 'ROI Uncertain' END roi_expectation
```

## agent可见证据与不确定性

不确定性四档：**没有迹象**。

检查全部70事件及result.md搜索路径，没有发现针对ROI标签差异的说明或观察输出；编写正确标签本身不当作不确定性披露。

完整事件扫描数：70；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | app_reporting__user_value_segmentation_report,int_user_rfm_analysis | False |
| 20 | 19 | app_reporting__user_value_segmentation_report,int_user_rfm_analysis | False |
| 22 | 21 | app_reporting__user_value_segmentation_report,int_user_rfm_analysis | False |
| 44 | 43 | app_reporting__user_value_segmentation_report,int_user_rfm_analysis | False |
| 48 | 47 | app_reporting__user_value_segmentation_report,int_user_rfm_analysis | False |
| 56 | 55 | app_reporting__user_value_segmentation_report,int_user_rfm_analysis | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：1；核实代价档：一条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/app_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='intermediate' AND table_name='int_user_rfm_analysis') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["intermediate", "int_user_rfm_analysis", "app_id", "VARCHAR"], ["intermediate", "int_user_rfm_analysis", "buyer_country", "VARCHAR"], ["intermediate", "int_user_rfm_analysis", "buyer_currency", "VARCHAR"], ["intermediate", "int_user_rfm_analysis", "recency_days", "BIGINT"], ["intermediate", "int_user_rfm_analysis", "frequency_count", "BIGINT"], ["intermediate", "int_user_rfm_analysis", "monetary_value", "DECIMAL(38,2)"], ["intermediate", "int_user_rfm_analysis", "first_transaction_date", "DATE"], ["intermediate", "int_user_rfm_analysis", "last_transaction_date", "DATE"], ["intermediate", "int_user_rfm_analysis", "total_transactions", "BIGINT"], ["intermediate", "int_user_rfm_analysis", "avg_transaction_value", "DOUBLE"], ["intermediate", "int_user_rfm_analysis", "subscription_count", "HUGEINT"], ["intermediate", "int_user_rfm_analysis", "purchase_count", "HUGEINT"], ["intermediate", "int_user_rfm_analysis", "refund_count", "HUGEINT"], ["intermediate", "int_user_rfm_analysis", "customer_lifetime_days", "BIGINT"], ["intermediate", "int_user_rfm_analysis", "recency_score", "INTEGER"], ["intermediate", "int_user_rfm_analysis", "frequency_score", "INTEGER"], ["intermediate", "int_user_rfm_analysis", "monetary_score", "INTEGER"], ["intermediate", "int_user_rfm_analysis", "rfm_score", "INTEGER"], ["intermediate", "int_user_rfm_analysis", "rfm_segment_code", "VARCHAR"], ["intermediate", "int_user_rfm_analysis", "customer_segment", "VARCHAR"], ["intermediate", "int_user_rfm_analysis", "estimated_clv", "DOUBLE"], ["intermediate", "int_user_rfm_analysis", "customer_health_status", "VARCHAR"], ["intermediate", "int_user_rfm_analysis", "is_high_value_customer", "INTEGER"], ["intermediate", "int_user_rfm_analysis", "is_churn_risk", "INTEGER"], ["intermediate", "int_user_rfm_analysis", "is_recent_customer", "INTEGER"], ["intermediate", "int_user_rfm_analysis", "data_quality_flag", "VARCHAR"], ["intermediate", "int_user_rfm_analysis", "analysis_timestamp", "TIMESTAMP WITH TIME ZONE"]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=34 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-007_app_reporting__user_value_segmentation_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：3行 / 5格；重跑基线：3行 / 6格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:3行/6格 / L1:3行/6格 / L2:3行/3格 / L3:3行/3格 | 均未整表匹配 |
| gold_roi_labels_diagnostic | L0:3行/3格 / L1:3行/3格 / L2:0行/0格 / L3:0行/0格 | L2 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"global_avg_clv": 3, "roi_expectation": 3} |
| gold_roi_labels_diagnostic | {"global_avg_clv": 3} |

本表全部重跑证据文件：`records/020_reruns_impl-007_app_reporting__user_value_segmentation_report.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-007_app_reporting__user_value_segmentation_report.md`。
- 重跑：`records/020_reruns_impl-007_app_reporting__user_value_segmentation_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
