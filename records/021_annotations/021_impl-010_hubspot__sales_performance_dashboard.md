# impl-010 / hubspot__sales_performance_dashboard（全量，更正A）

## 结论

主要原因：**O**；把握：高；标记：无。

agent使用契约明确的Excellent/Good/Average/Below Average；gold追加Performance后缀，7行标签不同，归O。收入增长率另有3格浮点末位差异，乘除顺序对齐减少3格，为O因素。

主要原因位置：rating_labels（行减少4，格减少7）。

参与因素：O：growth_arithmetic（行减少0，格减少3）。

不确定性四档：**看到了但没提**（针对主要原因）。

## 更正范围与CS口径

撤回021原“不可评估”。按手册v2第1、7节，本表只读intermediate上游，全部从gold复制；raw版本差异不传播为本节点不可评估。021原始raw诊断仍保留为历史事实，但不作为本表排除依据。官方待标注/判错状态不重定。

本次仅更正这份逐表记录；旧021汇总CSV、统计、重跑JSON和其他表不改。更正清单见[025报告](../../notes/025_2026-10-30_收尾A更正清单.md)。

## 差异与归因依据

实际schema：sales；评测键：created_year。按键与原评测列并集比较，不删除评测键。

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml`；相关行：1938、2009–2011。完整契约摘录见[021材料包](../021_packages/021_impl-010_hubspot__sales_performance_dashboard.md)。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_performance_dashboard.sql`；SHA-256 `4320249c8643dcd2edd3778d5acec9177ffef0e322ae2eb9ae8ea792659b68f7`。
- gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/sql/sales/hubspot__sales_performance_dashboard.sql`；SHA-256 `a86c87c38a3b789df7fc31a58db5c2ae7c7b682a3a1acb65ea222fc28e5418e0`。

仅修改rating CASE后，L0剩3行/3格，L2整表匹配；契约标签不能被gold后缀替代成agent错误。

各改动都是一个唯一出现的SQL位置，准确old/new、offset及其余字节不变的哈希证据见末尾机器记录。同做法出现在不同表达式时分别修改、分别计数；零改善/变差候选不列参与因素。

## agent可见证据与不确定性

event 1的message含完整契约，路径：`/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/1.json`。
原字段字符偏移129309起摘录：

```text
quarterly_performance_rating: Excellent if win_rate ≥ 30 and avg cycle ≤ 60; Good if win_rate ≥ 20 and avg cycle ≤ 90; Average if win_rate ≥ 15 and avg cycle ≤ 120; otherwise Below Average. - revenue_per_sales_rep: revenue_won_in_quarter divided by active_sales_reps_in_quarter; returns 0 if rep count is 0. - revenue_per_deal_created: revenue_won_in_quarter divided by deals_created_in_quarter; returns 0 if deal count is 0. - quarterly_goal_status:
```

复查impl-010全部75个事件：event21/27写入模型，event49/50比对字段和行数，event63/64列模型及部分行数；没有对本表主要排名顺序或分类标签作说明，也没有核验这些差异。event73最终报告只列完成模型、执行/字段检查及其他输入清洗注意事项。工作清单不计“只有通用策略说明”；报告关于原始缺失属性/关联缺失的一般描述不说明这里的排名或标签选择。

本表主因不确定性因此由原“没有迹象（不知gold raw版本）”改为“看到了但没提（已看到契约要求，未讨论本表差异）”。不把agent不能访问gold当作未见自己契约。

最终报告事件：`/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/73.json`。历史完整轨迹索引仍见`records/021_trace_audit.json`。

## 查询与诊断

核实查询0条；代价档：需要查业务说明。类别由契约/代码直接判断，不虚构P或agent可见核实查询。下列允许读gold的诊断不计入5条核实额度；原件均READ_ONLY，诊断与重跑仅写data/025_closure私有库。

### revenue_growth_rate_difference
```sql
SELECT cast(a.revenue_growth_rate as varchar) agent_value,cast(g.revenue_growth_rate as varchar) gold_value,count(*) n FROM baseline a JOIN gold.sales.hubspot__sales_performance_dashboard g USING(created_year,created_quarter) WHERE cast(a.revenue_growth_rate as varchar) IS DISTINCT FROM cast(g.revenue_growth_rate as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [["-7.263725032671558", "-7.263725032671557", 1], ["-7.679052309149123", "-7.679052309149122", 1], ["4.380973035251921", "4.380973035251922", 1]]}
```

### quarterly_performance_rating_difference
```sql
SELECT cast(a.quarterly_performance_rating as varchar) agent_value,cast(g.quarterly_performance_rating as varchar) gold_value,count(*) n FROM baseline a JOIN gold.sales.hubspot__sales_performance_dashboard g USING(created_year,created_quarter) WHERE cast(a.quarterly_performance_rating as varchar) IS DISTINCT FROM cast(g.quarterly_performance_rating as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [["Below Average", "Below Average Performance", 5], ["Average", "Average Performance", 1], ["Good", "Good Performance", 1]]}
```

辅助诊断：排除已定位列`revenue_growth_rate,quarterly_performance_rating`后，其余内容首次整表匹配为L0。此排除仅确认剩余差异范围，不进入主要原因排序。排名每个排序键组内rank多重集相同的查询单独列出。

## 时间控制、单点重跑与规模

复用021留存/基线记录核对源、时钟和SQL；新增干预统一使用threads=1和2025-10-13固定日期。源数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`；私有复制上游：`intermediate.int_hubspot__deal_performance_metrics`。所有减量对新增同控制基线计算；旧基线仅并列展示。

|记录|L0行/格|L1行/格|L2行/格|L3行/格|整表首次匹配|
|---|---:|---:|---:|---:|---|
|021留存|7/10|7/10|7/7|7/7|均未匹配|
|021原基线|7/10|7/10|7/7|7/7|均未匹配|
|baseline|7/10|7/10|7/7|7/7|均未匹配|
|rating_labels|3/3|3/3|0/0|0/0|L2|
|growth_arithmetic|7/7|7/7|7/7|7/7|均未匹配|

|单处修改|类别|行减少|格减少|角色|
|---|---|---:|---:|---|
|rating_labels|O|4|7|主因|
|growth_arithmetic|O|0|3|参与因素|

**rating_labels**：契约给短标签，agent按字面；gold加Performance后缀。一个CASE表达式位置。

**growth_arithmetic**：乘除顺序浮点末位差异，代数定义相同。

### 各档每列差异（共同键；本批均无独有/超额行）

|执行|档位|每列非零不一致数|
|---|---|---|
|baseline|L0|`{"revenue_growth_rate": 3, "quarterly_performance_rating": 7}`|
|baseline|L1|`{"revenue_growth_rate": 3, "quarterly_performance_rating": 7}`|
|baseline|L2|`{"quarterly_performance_rating": 7}`|
|baseline|L3|`{"quarterly_performance_rating": 7}`|
|rating_labels|L0|`{"revenue_growth_rate": 3}`|
|rating_labels|L1|`{"revenue_growth_rate": 3}`|
|rating_labels|L2|`{}`|
|rating_labels|L3|`{}`|
|growth_arithmetic|L0|`{"quarterly_performance_rating": 7}`|
|growth_arithmetic|L1|`{"quarterly_performance_rating": 7}`|
|growth_arithmetic|L2|`{"quarterly_performance_rating": 7}`|
|growth_arithmetic|L3|`{"quarterly_performance_rating": 7}`|

## 规则问题

无新规则问题。CASE是一个分类表达式位置；将该处标签集合对齐算一个诊断点。收入增长率公式是另一个代码位置，分开重跑。

没有改动手册定义。使用gold排序作为诊断的目的只是在契约允许的peer顺序内使比较条件一致；它不证明agent需要知道gold，也不构成U的单改证据。

## 完整机器证据及复现

旧记录：`records/021_reruns_impl-010_hubspot__sales_performance_dashboard.json`（未修改）。下列JSON是本次新增单点重跑的完整结果，随本逐表记录交付，未另行更新汇总。

<details><summary>共同控制、原/新片段、位置、私有SQL路径及L0–L3完整计数</summary>

<!-- correction-A-rerun-json -->
```json
{
  "started_utc": "2026-10-30T11:04:06.247526+00:00",
  "task": "impl-010",
  "basis": {
    "kind": "original_007_009",
    "record": "records/009_tolerance_tables.jsonl",
    "detail_record": "/home/katherine/Assumption_Ledger/records/009_cs_impl-010.json",
    "prediction_database": "/home/katherine/Assumption_Ledger/data/009_cs_work/impl-010/node_results.duckdb",
    "gold_database": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb",
    "actual_schema": "sales",
    "table": "hubspot__sales_performance_dashboard",
    "candidate_date": null,
    "comparison_columns": [
      "created_year",
      "created_quarter",
      "deals_created_in_quarter",
      "deals_won_in_quarter",
      "deals_lost_in_quarter",
      "deals_still_open",
      "revenue_won_in_quarter",
      "pipeline_value_in_quarter",
      "total_open_pipeline",
      "quarterly_win_rate",
      "prev_quarter_win_rate",
      "prev_quarter_revenue",
      "revenue_growth_rate",
      "avg_won_deal_size",
      "p25_deal_size",
      "p75_deal_size",
      "active_sales_reps_in_quarter",
      "revenue_per_sales_rep",
      "weighted_pipeline_forecast",
      "time_weighted_forecast",
      "quarterly_performance_rating",
      "quarterly_goal_status"
    ],
    "key_columns": [
      "created_year"
    ],
    "prediction_rows": 7,
    "gold_rows": 7,
    "row_delta": 0,
    "key_statistics": {
      "pred_distinct_keys": 2,
      "gold_distinct_keys": 2,
      "pred_duplicate_key_groups": 2,
      "gold_duplicate_key_groups": 2,
      "pred_only_keys": 0,
      "gold_only_keys": 0,
      "shared_keys": 2,
      "shared_nonunique_key_groups": 2
    },
    "l0_column_differences": [
      {
        "column": "created_year",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "created_quarter",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "deals_created_in_quarter",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "deals_won_in_quarter",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "deals_lost_in_quarter",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "deals_still_open",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "revenue_won_in_quarter",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "pipeline_value_in_quarter",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "avg_won_deal_size",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "quarterly_win_rate",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "p25_deal_size",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "p75_deal_size",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "active_sales_reps_in_quarter",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "total_open_pipeline",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "weighted_pipeline_forecast",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "time_weighted_forecast",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "prev_quarter_revenue",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "prev_quarter_win_rate",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "revenue_growth_rate",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 3,
        "mismatch_rows_or_minimum_pairs": 3,
        "pred_unmatched_value_occurrences": 3,
        "gold_unmatched_value_occurrences": 3,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "quarterly_performance_rating",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 7,
        "mismatch_rows_or_minimum_pairs": 7,
        "pred_unmatched_value_occurrences": 7,
        "gold_unmatched_value_occurrences": 7,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "revenue_per_sales_rep",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "quarterly_goal_status",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "minimum_value_mismatch_pairs"
      }
    ],
    "l3_column_differences": [
      {
        "column": "created_year",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "created_quarter",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "deals_created_in_quarter",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "deals_won_in_quarter",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "deals_lost_in_quarter",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "deals_still_open",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "revenue_won_in_quarter",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "pipeline_value_in_quarter",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "total_open_pipeline",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "quarterly_win_rate",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "prev_quarter_win_rate",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "prev_quarter_revenue",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "revenue_growth_rate",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "avg_won_deal_size",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "p25_deal_size",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "p75_deal_size",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "active_sales_reps_in_quarter",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "revenue_per_sales_rep",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "weighted_pipeline_forecast",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "time_weighted_forecast",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "quarterly_performance_rating",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 7,
        "mismatch_rows_or_minimum_pairs": 7,
        "pred_unmatched_value_occurrences": 7,
        "gold_unmatched_value_occurrences": 7,
        "marginal_multisets_equal": false,
        "count_semantics": "minimum_value_mismatch_pairs"
      },
      {
        "column": "quarterly_goal_status",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "minimum_value_mismatch_pairs"
      }
    ],
    "whole_match_level": "仍不匹配",
    "keyed_match_level": "仍不匹配",
    "selection_reason": "该表 gold 日期未能验证，沿用原差异",
    "value_representation": "Unmodified DuckDB CAST AS VARCHAR; SQL NULL is JSON null. Keys use the unchanged historical L0 normalization.",
    "new_queries_only_read_existing_results": true,
    "one_side_key_examples": {
      "prediction_only": [],
      "gold_only": []
    },
    "column_details": [
      {
        "column": "created_year",
        "l0_counts_verbatim": {
          "column": "created_year",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "created_year",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "created_quarter",
        "l0_counts_verbatim": {
          "column": "created_quarter",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "created_quarter",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "deals_created_in_quarter",
        "l0_counts_verbatim": {
          "column": "deals_created_in_quarter",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "deals_created_in_quarter",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "deals_won_in_quarter",
        "l0_counts_verbatim": {
          "column": "deals_won_in_quarter",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "deals_won_in_quarter",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "deals_lost_in_quarter",
        "l0_counts_verbatim": {
          "column": "deals_lost_in_quarter",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "deals_lost_in_quarter",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "deals_still_open",
        "l0_counts_verbatim": {
          "column": "deals_still_open",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "deals_still_open",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "revenue_won_in_quarter",
        "l0_counts_verbatim": {
          "column": "revenue_won_in_quarter",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "revenue_won_in_quarter",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DECIMAL(38,2)",
        "gold_actual_type": "DECIMAL(38,2)"
      },
      {
        "column": "pipeline_value_in_quarter",
        "l0_counts_verbatim": {
          "column": "pipeline_value_in_quarter",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "pipeline_value_in_quarter",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DECIMAL(38,2)",
        "gold_actual_type": "DECIMAL(38,2)"
      },
      {
        "column": "avg_won_deal_size",
        "l0_counts_verbatim": {
          "column": "avg_won_deal_size",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "avg_won_deal_size",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "quarterly_win_rate",
        "l0_counts_verbatim": {
          "column": "quarterly_win_rate",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "quarterly_win_rate",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "p25_deal_size",
        "l0_counts_verbatim": {
          "column": "p25_deal_size",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "p25_deal_size",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DECIMAL(18,2)",
        "gold_actual_type": "DECIMAL(18,2)"
      },
      {
        "column": "p75_deal_size",
        "l0_counts_verbatim": {
          "column": "p75_deal_size",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "p75_deal_size",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DECIMAL(18,2)",
        "gold_actual_type": "DECIMAL(18,2)"
      },
      {
        "column": "active_sales_reps_in_quarter",
        "l0_counts_verbatim": {
          "column": "active_sales_reps_in_quarter",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "active_sales_reps_in_quarter",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "total_open_pipeline",
        "l0_counts_verbatim": {
          "column": "total_open_pipeline",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "total_open_pipeline",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DECIMAL(38,2)",
        "gold_actual_type": "DECIMAL(38,2)"
      },
      {
        "column": "weighted_pipeline_forecast",
        "l0_counts_verbatim": {
          "column": "weighted_pipeline_forecast",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "weighted_pipeline_forecast",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "time_weighted_forecast",
        "l0_counts_verbatim": {
          "column": "time_weighted_forecast",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "time_weighted_forecast",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DECIMAL(38,3)",
        "gold_actual_type": "DECIMAL(38,3)"
      },
      {
        "column": "prev_quarter_revenue",
        "l0_counts_verbatim": {
          "column": "prev_quarter_revenue",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "prev_quarter_revenue",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DECIMAL(38,2)",
        "gold_actual_type": "DECIMAL(38,2)"
      },
      {
        "column": "prev_quarter_win_rate",
        "l0_counts_verbatim": {
          "column": "prev_quarter_win_rate",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "prev_quarter_win_rate",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "revenue_growth_rate",
        "l0_counts_verbatim": {
          "column": "revenue_growth_rate",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 3,
          "mismatch_rows_or_minimum_pairs": 3,
          "pred_unmatched_value_occurrences": 3,
          "gold_unmatched_value_occurrences": 3,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "revenue_growth_rate",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [
          {
            "key_normalized": {
              "created_year": "2023"
            },
            "agent_key_raw_text": {
              "created_year": "2023"
            },
            "gold_key_raw_text": {
              "created_year": "2023"
            },
            "agent_rows_with_key": 4,
            "gold_rows_with_key": 4,
            "agent_values": [
              {
                "value": null,
                "rows": 1
              },
              {
                "value": "-7.263725032671558",
                "rows": 1
              },
              {
                "value": "-7.679052309149123",
                "rows": 1
              },
              {
                "value": "4.5169932653626175",
                "rows": 1
              }
            ],
            "gold_values": [
              {
                "value": null,
                "rows": 1
              },
              {
                "value": "-7.263725032671557",
                "rows": 1
              },
              {
                "value": "-7.679052309149122",
                "rows": 1
              },
              {
                "value": "4.5169932653626175",
                "rows": 1
              }
            ],
            "kind": "duplicate_key_group_not_a_unique_row_pair",
            "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
          },
          {
            "key_normalized": {
              "created_year": "2024"
            },
            "agent_key_raw_text": {
              "created_year": "2024"
            },
            "gold_key_raw_text": {
              "created_year": "2024"
            },
            "agent_rows_with_key": 3,
            "gold_rows_with_key": 3,
            "agent_values": [
              {
                "value": "1.1932315697002642",
                "rows": 1
              },
              {
                "value": "13.114744519523052",
                "rows": 1
              },
              {
                "value": "4.380973035251921",
                "rows": 1
              }
            ],
            "gold_values": [
              {
                "value": "1.1932315697002642",
                "rows": 1
              },
              {
                "value": "13.114744519523052",
                "rows": 1
              },
              {
                "value": "4.380973035251922",
                "rows": 1
              }
            ],
            "kind": "duplicate_key_group_not_a_unique_row_pair",
            "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
          }
        ],
        "sample_counts_recheck": {
          "mismatch_rows_or_minimum_pairs": 3,
          "pred_unmatched_value_occurrences": 3,
          "gold_unmatched_value_occurrences": 3
        },
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "quarterly_performance_rating",
        "l0_counts_verbatim": {
          "column": "quarterly_performance_rating",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 7,
          "mismatch_rows_or_minimum_pairs": 7,
          "pred_unmatched_value_occurrences": 7,
          "gold_unmatched_value_occurrences": 7,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "quarterly_performance_rating",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 7,
          "mismatch_rows_or_minimum_pairs": 7,
          "pred_unmatched_value_occurrences": 7,
          "gold_unmatched_value_occurrences": 7,
          "marginal_multisets_equal": false,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [
          {
            "key_normalized": {
              "created_year": "2023"
            },
            "agent_key_raw_text": {
              "created_year": "2023"
            },
            "gold_key_raw_text": {
              "created_year": "2023"
            },
            "agent_rows_with_key": 4,
            "gold_rows_with_key": 4,
            "agent_values": [
              {
                "value": "Below Average",
                "rows": 4
              }
            ],
            "gold_values": [
              {
                "value": "Below Average Performance",
                "rows": 4
              }
            ],
            "kind": "duplicate_key_group_not_a_unique_row_pair",
            "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
          },
          {
            "key_normalized": {
              "created_year": "2024"
            },
            "agent_key_raw_text": {
              "created_year": "2024"
            },
            "gold_key_raw_text": {
              "created_year": "2024"
            },
            "agent_rows_with_key": 3,
            "gold_rows_with_key": 3,
            "agent_values": [
              {
                "value": "Average",
                "rows": 1
              },
              {
                "value": "Below Average",
                "rows": 1
              },
              {
                "value": "Good",
                "rows": 1
              }
            ],
            "gold_values": [
              {
                "value": "Average Performance",
                "rows": 1
              },
              {
                "value": "Below Average Performance",
                "rows": 1
              },
              {
                "value": "Good Performance",
                "rows": 1
              }
            ],
            "kind": "duplicate_key_group_not_a_unique_row_pair",
            "sample_semantics": "At most 5 distinct raw values per side in this key group; do not pair entries by list position."
          }
        ],
        "sample_counts_recheck": {
          "mismatch_rows_or_minimum_pairs": 7,
          "pred_unmatched_value_occurrences": 7,
          "gold_unmatched_value_occurrences": 7
        },
        "agent_actual_type": "VARCHAR",
        "gold_actual_type": "VARCHAR"
      },
      {
        "column": "revenue_per_sales_rep",
        "l0_counts_verbatim": {
          "column": "revenue_per_sales_rep",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "revenue_per_sales_rep",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "quarterly_goal_status",
        "l0_counts_verbatim": {
          "column": "quarterly_goal_status",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "l3_counts_verbatim": {
          "column": "quarterly_goal_status",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "minimum_value_mismatch_pairs"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "VARCHAR",
        "gold_actual_type": "VARCHAR"
      }
    ]
  },
  "source": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb",
  "clock_control": [
    {
      "pattern": "\\bcurrent_timestamp\\b",
      "replacement": "TIMESTAMPTZ '2025-10-13 00:00:00+00'",
      "count": 0
    },
    {
      "pattern": "\\bcurrent_date\\b",
      "replacement": "DATE '2025-10-13'",
      "count": 2
    }
  ],
  "runs": [
    {
      "label": "baseline",
      "edits": [],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_performance_dashboard/baseline.sql",
      "sql_sha256": "03b91d1b2d0cd5607d884b6cb752ff8efe71a08367d6403f484e5a10920e2975",
      "comparison": {
        "levels": [
          {
            "level": "L0",
            "agent_rows": 7,
            "gold_rows": 7,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 7,
            "column_mismatches": {
              "created_year": 0,
              "created_quarter": 0,
              "deals_created_in_quarter": 0,
              "deals_won_in_quarter": 0,
              "deals_lost_in_quarter": 0,
              "deals_still_open": 0,
              "revenue_won_in_quarter": 0,
              "pipeline_value_in_quarter": 0,
              "total_open_pipeline": 0,
              "quarterly_win_rate": 0,
              "prev_quarter_win_rate": 0,
              "prev_quarter_revenue": 0,
              "revenue_growth_rate": 3,
              "avg_won_deal_size": 0,
              "p25_deal_size": 0,
              "p75_deal_size": 0,
              "active_sales_reps_in_quarter": 0,
              "revenue_per_sales_rep": 0,
              "weighted_pipeline_forecast": 0,
              "time_weighted_forecast": 0,
              "quarterly_performance_rating": 7,
              "quarterly_goal_status": 0
            },
            "key_aware_agent_unmatched": 7,
            "key_aware_gold_unmatched": 7,
            "whole_match": false,
            "row_scale": 7,
            "cell_scale": 10,
            "comparison_column_count_including_keys": 22
          },
          {
            "level": "L1",
            "agent_rows": 7,
            "gold_rows": 7,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 7,
            "column_mismatches": {
              "created_year": 0,
              "created_quarter": 0,
              "deals_created_in_quarter": 0,
              "deals_won_in_quarter": 0,
              "deals_lost_in_quarter": 0,
              "deals_still_open": 0,
              "revenue_won_in_quarter": 0,
              "pipeline_value_in_quarter": 0,
              "total_open_pipeline": 0,
              "quarterly_win_rate": 0,
              "prev_quarter_win_rate": 0,
              "prev_quarter_revenue": 0,
              "revenue_growth_rate": 3,
              "avg_won_deal_size": 0,
              "p25_deal_size": 0,
              "p75_deal_size": 0,
              "active_sales_reps_in_quarter": 0,
              "revenue_per_sales_rep": 0,
              "weighted_pipeline_forecast": 0,
              "time_weighted_forecast": 0,
              "quarterly_performance_rating": 7,
              "quarterly_goal_status": 0
            },
            "key_aware_agent_unmatched": 7,
            "key_aware_gold_unmatched": 7,
            "whole_match": false,
            "row_scale": 7,
            "cell_scale": 10,
            "comparison_column_count_including_keys": 22
          },
          {
            "level": "L2",
            "agent_rows": 7,
            "gold_rows": 7,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 7,
            "column_mismatches": {
              "created_year": 0,
              "created_quarter": 0,
              "deals_created_in_quarter": 0,
              "deals_won_in_quarter": 0,
              "deals_lost_in_quarter": 0,
              "deals_still_open": 0,
              "revenue_won_in_quarter": 0,
              "pipeline_value_in_quarter": 0,
              "total_open_pipeline": 0,
              "quarterly_win_rate": 0,
              "prev_quarter_win_rate": 0,
              "prev_quarter_revenue": 0,
              "revenue_growth_rate": 0,
              "avg_won_deal_size": 0,
              "p25_deal_size": 0,
              "p75_deal_size": 0,
              "active_sales_reps_in_quarter": 0,
              "revenue_per_sales_rep": 0,
              "weighted_pipeline_forecast": 0,
              "time_weighted_forecast": 0,
              "quarterly_performance_rating": 7,
              "quarterly_goal_status": 0
            },
            "key_aware_agent_unmatched": 7,
            "key_aware_gold_unmatched": 7,
            "whole_match": false,
            "row_scale": 7,
            "cell_scale": 7,
            "comparison_column_count_including_keys": 22
          },
          {
            "level": "L3",
            "agent_rows": 7,
            "gold_rows": 7,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 7,
            "column_mismatches": {
              "created_year": 0,
              "created_quarter": 0,
              "deals_created_in_quarter": 0,
              "deals_won_in_quarter": 0,
              "deals_lost_in_quarter": 0,
              "deals_still_open": 0,
              "revenue_won_in_quarter": 0,
              "pipeline_value_in_quarter": 0,
              "total_open_pipeline": 0,
              "quarterly_win_rate": 0,
              "prev_quarter_win_rate": 0,
              "prev_quarter_revenue": 0,
              "revenue_growth_rate": 0,
              "avg_won_deal_size": 0,
              "p25_deal_size": 0,
              "p75_deal_size": 0,
              "active_sales_reps_in_quarter": 0,
              "revenue_per_sales_rep": 0,
              "weighted_pipeline_forecast": 0,
              "time_weighted_forecast": 0,
              "quarterly_performance_rating": 7,
              "quarterly_goal_status": 0
            },
            "key_aware_agent_unmatched": 7,
            "key_aware_gold_unmatched": 7,
            "whole_match": false,
            "row_scale": 7,
            "cell_scale": 7,
            "comparison_column_count_including_keys": 22
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "rating_labels",
      "edits": [
        {
          "old": "case when quarterly_win_rate>=30 and avg_sales_cycle_days<=60 then 'Excellent' when quarterly_win_rate>=20 and avg_sales_cycle_days<=90 then 'Good' when quarterly_win_rate>=15 and avg_sales_cycle_days<=120 then 'Average' else 'Below Average' end",
          "new": "case when quarterly_win_rate>=30 and avg_sales_cycle_days<=60 then 'Excellent Performance' when quarterly_win_rate>=20 and avg_sales_cycle_days<=90 then 'Good Performance' when quarterly_win_rate>=15 and avg_sales_cycle_days<=120 then 'Average Performance' else 'Below Average Performance' end",
          "offset": 3548
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_performance_dashboard/rating_labels.sql",
      "sql_sha256": "61dc1ef56e9487d60e3572c8ff9fec2280f522159a204be064ebf4d61cd603ed",
      "comparison": {
        "levels": [
          {
            "level": "L0",
            "agent_rows": 7,
            "gold_rows": 7,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 3,
            "column_mismatches": {
              "created_year": 0,
              "created_quarter": 0,
              "deals_created_in_quarter": 0,
              "deals_won_in_quarter": 0,
              "deals_lost_in_quarter": 0,
              "deals_still_open": 0,
              "revenue_won_in_quarter": 0,
              "pipeline_value_in_quarter": 0,
              "total_open_pipeline": 0,
              "quarterly_win_rate": 0,
              "prev_quarter_win_rate": 0,
              "prev_quarter_revenue": 0,
              "revenue_growth_rate": 3,
              "avg_won_deal_size": 0,
              "p25_deal_size": 0,
              "p75_deal_size": 0,
              "active_sales_reps_in_quarter": 0,
              "revenue_per_sales_rep": 0,
              "weighted_pipeline_forecast": 0,
              "time_weighted_forecast": 0,
              "quarterly_performance_rating": 0,
              "quarterly_goal_status": 0
            },
            "key_aware_agent_unmatched": 3,
            "key_aware_gold_unmatched": 3,
            "whole_match": false,
            "row_scale": 3,
            "cell_scale": 3,
            "comparison_column_count_including_keys": 22
          },
          {
            "level": "L1",
            "agent_rows": 7,
            "gold_rows": 7,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 3,
            "column_mismatches": {
              "created_year": 0,
              "created_quarter": 0,
              "deals_created_in_quarter": 0,
              "deals_won_in_quarter": 0,
              "deals_lost_in_quarter": 0,
              "deals_still_open": 0,
              "revenue_won_in_quarter": 0,
              "pipeline_value_in_quarter": 0,
              "total_open_pipeline": 0,
              "quarterly_win_rate": 0,
              "prev_quarter_win_rate": 0,
              "prev_quarter_revenue": 0,
              "revenue_growth_rate": 3,
              "avg_won_deal_size": 0,
              "p25_deal_size": 0,
              "p75_deal_size": 0,
              "active_sales_reps_in_quarter": 0,
              "revenue_per_sales_rep": 0,
              "weighted_pipeline_forecast": 0,
              "time_weighted_forecast": 0,
              "quarterly_performance_rating": 0,
              "quarterly_goal_status": 0
            },
            "key_aware_agent_unmatched": 3,
            "key_aware_gold_unmatched": 3,
            "whole_match": false,
            "row_scale": 3,
            "cell_scale": 3,
            "comparison_column_count_including_keys": 22
          },
          {
            "level": "L2",
            "agent_rows": 7,
            "gold_rows": 7,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 0,
            "column_mismatches": {
              "created_year": 0,
              "created_quarter": 0,
              "deals_created_in_quarter": 0,
              "deals_won_in_quarter": 0,
              "deals_lost_in_quarter": 0,
              "deals_still_open": 0,
              "revenue_won_in_quarter": 0,
              "pipeline_value_in_quarter": 0,
              "total_open_pipeline": 0,
              "quarterly_win_rate": 0,
              "prev_quarter_win_rate": 0,
              "prev_quarter_revenue": 0,
              "revenue_growth_rate": 0,
              "avg_won_deal_size": 0,
              "p25_deal_size": 0,
              "p75_deal_size": 0,
              "active_sales_reps_in_quarter": 0,
              "revenue_per_sales_rep": 0,
              "weighted_pipeline_forecast": 0,
              "time_weighted_forecast": 0,
              "quarterly_performance_rating": 0,
              "quarterly_goal_status": 0
            },
            "key_aware_agent_unmatched": 0,
            "key_aware_gold_unmatched": 0,
            "whole_match": true,
            "row_scale": 0,
            "cell_scale": 0,
            "comparison_column_count_including_keys": 22
          },
          {
            "level": "L3",
            "agent_rows": 7,
            "gold_rows": 7,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 0,
            "column_mismatches": {
              "created_year": 0,
              "created_quarter": 0,
              "deals_created_in_quarter": 0,
              "deals_won_in_quarter": 0,
              "deals_lost_in_quarter": 0,
              "deals_still_open": 0,
              "revenue_won_in_quarter": 0,
              "pipeline_value_in_quarter": 0,
              "total_open_pipeline": 0,
              "quarterly_win_rate": 0,
              "prev_quarter_win_rate": 0,
              "prev_quarter_revenue": 0,
              "revenue_growth_rate": 0,
              "avg_won_deal_size": 0,
              "p25_deal_size": 0,
              "p75_deal_size": 0,
              "active_sales_reps_in_quarter": 0,
              "revenue_per_sales_rep": 0,
              "weighted_pipeline_forecast": 0,
              "time_weighted_forecast": 0,
              "quarterly_performance_rating": 0,
              "quarterly_goal_status": 0
            },
            "key_aware_agent_unmatched": 0,
            "key_aware_gold_unmatched": 0,
            "whole_match": true,
            "row_scale": 0,
            "cell_scale": 0,
            "comparison_column_count_including_keys": 22
          }
        ],
        "first_match": "L2"
      }
    },
    {
      "label": "growth_arithmetic",
      "edits": [
        {
          "old": "(revenue_won_in_quarter-prev_quarter_revenue)*100.0/prev_quarter_revenue",
          "new": "(revenue_won_in_quarter-prev_quarter_revenue)/prev_quarter_revenue*100",
          "offset": 2514
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_performance_dashboard/growth_arithmetic.sql",
      "sql_sha256": "c991ce9d4d1ac2bf0f54598832b31df3000134b16c81d605359c66cab957838a",
      "comparison": {
        "levels": [
          {
            "level": "L0",
            "agent_rows": 7,
            "gold_rows": 7,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 7,
            "column_mismatches": {
              "created_year": 0,
              "created_quarter": 0,
              "deals_created_in_quarter": 0,
              "deals_won_in_quarter": 0,
              "deals_lost_in_quarter": 0,
              "deals_still_open": 0,
              "revenue_won_in_quarter": 0,
              "pipeline_value_in_quarter": 0,
              "total_open_pipeline": 0,
              "quarterly_win_rate": 0,
              "prev_quarter_win_rate": 0,
              "prev_quarter_revenue": 0,
              "revenue_growth_rate": 0,
              "avg_won_deal_size": 0,
              "p25_deal_size": 0,
              "p75_deal_size": 0,
              "active_sales_reps_in_quarter": 0,
              "revenue_per_sales_rep": 0,
              "weighted_pipeline_forecast": 0,
              "time_weighted_forecast": 0,
              "quarterly_performance_rating": 7,
              "quarterly_goal_status": 0
            },
            "key_aware_agent_unmatched": 7,
            "key_aware_gold_unmatched": 7,
            "whole_match": false,
            "row_scale": 7,
            "cell_scale": 7,
            "comparison_column_count_including_keys": 22
          },
          {
            "level": "L1",
            "agent_rows": 7,
            "gold_rows": 7,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 7,
            "column_mismatches": {
              "created_year": 0,
              "created_quarter": 0,
              "deals_created_in_quarter": 0,
              "deals_won_in_quarter": 0,
              "deals_lost_in_quarter": 0,
              "deals_still_open": 0,
              "revenue_won_in_quarter": 0,
              "pipeline_value_in_quarter": 0,
              "total_open_pipeline": 0,
              "quarterly_win_rate": 0,
              "prev_quarter_win_rate": 0,
              "prev_quarter_revenue": 0,
              "revenue_growth_rate": 0,
              "avg_won_deal_size": 0,
              "p25_deal_size": 0,
              "p75_deal_size": 0,
              "active_sales_reps_in_quarter": 0,
              "revenue_per_sales_rep": 0,
              "weighted_pipeline_forecast": 0,
              "time_weighted_forecast": 0,
              "quarterly_performance_rating": 7,
              "quarterly_goal_status": 0
            },
            "key_aware_agent_unmatched": 7,
            "key_aware_gold_unmatched": 7,
            "whole_match": false,
            "row_scale": 7,
            "cell_scale": 7,
            "comparison_column_count_including_keys": 22
          },
          {
            "level": "L2",
            "agent_rows": 7,
            "gold_rows": 7,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 7,
            "column_mismatches": {
              "created_year": 0,
              "created_quarter": 0,
              "deals_created_in_quarter": 0,
              "deals_won_in_quarter": 0,
              "deals_lost_in_quarter": 0,
              "deals_still_open": 0,
              "revenue_won_in_quarter": 0,
              "pipeline_value_in_quarter": 0,
              "total_open_pipeline": 0,
              "quarterly_win_rate": 0,
              "prev_quarter_win_rate": 0,
              "prev_quarter_revenue": 0,
              "revenue_growth_rate": 0,
              "avg_won_deal_size": 0,
              "p25_deal_size": 0,
              "p75_deal_size": 0,
              "active_sales_reps_in_quarter": 0,
              "revenue_per_sales_rep": 0,
              "weighted_pipeline_forecast": 0,
              "time_weighted_forecast": 0,
              "quarterly_performance_rating": 7,
              "quarterly_goal_status": 0
            },
            "key_aware_agent_unmatched": 7,
            "key_aware_gold_unmatched": 7,
            "whole_match": false,
            "row_scale": 7,
            "cell_scale": 7,
            "comparison_column_count_including_keys": 22
          },
          {
            "level": "L3",
            "agent_rows": 7,
            "gold_rows": 7,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 7,
            "column_mismatches": {
              "created_year": 0,
              "created_quarter": 0,
              "deals_created_in_quarter": 0,
              "deals_won_in_quarter": 0,
              "deals_lost_in_quarter": 0,
              "deals_still_open": 0,
              "revenue_won_in_quarter": 0,
              "pipeline_value_in_quarter": 0,
              "total_open_pipeline": 0,
              "quarterly_win_rate": 0,
              "prev_quarter_win_rate": 0,
              "prev_quarter_revenue": 0,
              "revenue_growth_rate": 0,
              "avg_won_deal_size": 0,
              "p25_deal_size": 0,
              "p75_deal_size": 0,
              "active_sales_reps_in_quarter": 0,
              "revenue_per_sales_rep": 0,
              "weighted_pipeline_forecast": 0,
              "time_weighted_forecast": 0,
              "quarterly_performance_rating": 7,
              "quarterly_goal_status": 0
            },
            "key_aware_agent_unmatched": 7,
            "key_aware_gold_unmatched": 7,
            "whole_match": false,
            "row_scale": 7,
            "cell_scale": 7,
            "comparison_column_count_including_keys": 22
          }
        ],
        "first_match": null
      }
    }
  ],
  "attached": [
    [
      "src",
      "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb"
    ],
    [
      "retained",
      "/home/katherine/Assumption_Ledger/data/009_cs_work/impl-010/node_results.duckdb"
    ]
  ],
  "src_alias": "src",
  "gold_alias": "src",
  "retained_alias": "retained",
  "private_copy_tables": [
    "intermediate.int_hubspot__deal_performance_metrics"
  ],
  "retained": {
    "levels": [
      {
        "level": "L0",
        "agent_rows": 7,
        "gold_rows": 7,
        "agent_only_key_rows": 0,
        "gold_only_key_rows": 0,
        "common_key_agent_excess_rows": 0,
        "common_key_gold_excess_rows": 0,
        "common_key_different_rows_or_min_pairs": 7,
        "column_mismatches": {
          "created_year": 0,
          "created_quarter": 0,
          "deals_created_in_quarter": 0,
          "deals_won_in_quarter": 0,
          "deals_lost_in_quarter": 0,
          "deals_still_open": 0,
          "revenue_won_in_quarter": 0,
          "pipeline_value_in_quarter": 0,
          "total_open_pipeline": 0,
          "quarterly_win_rate": 0,
          "prev_quarter_win_rate": 0,
          "prev_quarter_revenue": 0,
          "revenue_growth_rate": 3,
          "avg_won_deal_size": 0,
          "p25_deal_size": 0,
          "p75_deal_size": 0,
          "active_sales_reps_in_quarter": 0,
          "revenue_per_sales_rep": 0,
          "weighted_pipeline_forecast": 0,
          "time_weighted_forecast": 0,
          "quarterly_performance_rating": 7,
          "quarterly_goal_status": 0
        },
        "key_aware_agent_unmatched": 7,
        "key_aware_gold_unmatched": 7,
        "whole_match": false,
        "row_scale": 7,
        "cell_scale": 10,
        "comparison_column_count_including_keys": 22
      },
      {
        "level": "L1",
        "agent_rows": 7,
        "gold_rows": 7,
        "agent_only_key_rows": 0,
        "gold_only_key_rows": 0,
        "common_key_agent_excess_rows": 0,
        "common_key_gold_excess_rows": 0,
        "common_key_different_rows_or_min_pairs": 7,
        "column_mismatches": {
          "created_year": 0,
          "created_quarter": 0,
          "deals_created_in_quarter": 0,
          "deals_won_in_quarter": 0,
          "deals_lost_in_quarter": 0,
          "deals_still_open": 0,
          "revenue_won_in_quarter": 0,
          "pipeline_value_in_quarter": 0,
          "total_open_pipeline": 0,
          "quarterly_win_rate": 0,
          "prev_quarter_win_rate": 0,
          "prev_quarter_revenue": 0,
          "revenue_growth_rate": 3,
          "avg_won_deal_size": 0,
          "p25_deal_size": 0,
          "p75_deal_size": 0,
          "active_sales_reps_in_quarter": 0,
          "revenue_per_sales_rep": 0,
          "weighted_pipeline_forecast": 0,
          "time_weighted_forecast": 0,
          "quarterly_performance_rating": 7,
          "quarterly_goal_status": 0
        },
        "key_aware_agent_unmatched": 7,
        "key_aware_gold_unmatched": 7,
        "whole_match": false,
        "row_scale": 7,
        "cell_scale": 10,
        "comparison_column_count_including_keys": 22
      },
      {
        "level": "L2",
        "agent_rows": 7,
        "gold_rows": 7,
        "agent_only_key_rows": 0,
        "gold_only_key_rows": 0,
        "common_key_agent_excess_rows": 0,
        "common_key_gold_excess_rows": 0,
        "common_key_different_rows_or_min_pairs": 7,
        "column_mismatches": {
          "created_year": 0,
          "created_quarter": 0,
          "deals_created_in_quarter": 0,
          "deals_won_in_quarter": 0,
          "deals_lost_in_quarter": 0,
          "deals_still_open": 0,
          "revenue_won_in_quarter": 0,
          "pipeline_value_in_quarter": 0,
          "total_open_pipeline": 0,
          "quarterly_win_rate": 0,
          "prev_quarter_win_rate": 0,
          "prev_quarter_revenue": 0,
          "revenue_growth_rate": 0,
          "avg_won_deal_size": 0,
          "p25_deal_size": 0,
          "p75_deal_size": 0,
          "active_sales_reps_in_quarter": 0,
          "revenue_per_sales_rep": 0,
          "weighted_pipeline_forecast": 0,
          "time_weighted_forecast": 0,
          "quarterly_performance_rating": 7,
          "quarterly_goal_status": 0
        },
        "key_aware_agent_unmatched": 7,
        "key_aware_gold_unmatched": 7,
        "whole_match": false,
        "row_scale": 7,
        "cell_scale": 7,
        "comparison_column_count_including_keys": 22
      },
      {
        "level": "L3",
        "agent_rows": 7,
        "gold_rows": 7,
        "agent_only_key_rows": 0,
        "gold_only_key_rows": 0,
        "common_key_agent_excess_rows": 0,
        "common_key_gold_excess_rows": 0,
        "common_key_different_rows_or_min_pairs": 7,
        "column_mismatches": {
          "created_year": 0,
          "created_quarter": 0,
          "deals_created_in_quarter": 0,
          "deals_won_in_quarter": 0,
          "deals_lost_in_quarter": 0,
          "deals_still_open": 0,
          "revenue_won_in_quarter": 0,
          "pipeline_value_in_quarter": 0,
          "total_open_pipeline": 0,
          "quarterly_win_rate": 0,
          "prev_quarter_win_rate": 0,
          "prev_quarter_revenue": 0,
          "revenue_growth_rate": 0,
          "avg_won_deal_size": 0,
          "p25_deal_size": 0,
          "p75_deal_size": 0,
          "active_sales_reps_in_quarter": 0,
          "revenue_per_sales_rep": 0,
          "weighted_pipeline_forecast": 0,
          "time_weighted_forecast": 0,
          "quarterly_performance_rating": 7,
          "quarterly_goal_status": 0
        },
        "key_aware_agent_unmatched": 7,
        "key_aware_gold_unmatched": 7,
        "whole_match": false,
        "row_scale": 7,
        "cell_scale": 7,
        "comparison_column_count_including_keys": 22
      }
    ],
    "first_match": null
  },
  "execution_threads": 1
}
```
</details>

复现：从JSON读取basis/source/clock_control；以只读方式挂载源和gold，在私有库复制private_copy_tables；对原agent SQL先应用共同clock_control，再逐个独立应用runs中的唯一old/new替换；threads固定1，比较沿用scripts/annotate_dacomp_batch016.py的compare_sql及udf_forms。不得向旧021路径写出新结果。
