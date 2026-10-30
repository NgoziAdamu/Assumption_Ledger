# impl-010 / int_hubspot__owner_performance_metrics（全量，更正A）

## 结论

主要原因：**O**；把握：高；标记：无。

主要差异是契约允许任意顺序的ROW_NUMBER并列排名。按完整行/格单点改善量，deals_won_rank的允许顺序对齐为主因O；另有large_deal_win_rate无closed deals时NULL而非契约0的C，以及浮点运算次序和另一排名的O因素。

主要原因位置：deals_won_rank_peer_order（行减少15，格减少175）。

参与因素：C：large_deal_win_rate（行减少0，格减少74）；O：score_arithmetic（行减少1，格减少88）；O：cycle_time_rank_peer_order（行减少0，格减少2）。

不确定性四档：**看到了但没提**（针对主要原因）。

## 更正范围与CS口径

撤回021原“不可评估”。按手册v2第1、7节，本表只读intermediate上游，全部从gold复制；raw版本差异不传播为本节点不可评估。021原始raw诊断仍保留为历史事实，但不作为本表排除依据。官方待标注/判错状态不重定。

本次仅更正这份逐表记录；旧021汇总CSV、统计、重跑JSON和其他表不改。更正清单见[025报告](../../notes/025_2026-10-30_收尾A更正清单.md)。

## 差异与归因依据

实际schema：intermediate；评测键：owner_id。按键与原评测列并集比较，不删除评测键。

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml`；相关行：1031、1088–1108、1121–1123。完整契约摘录见[021材料包](../021_packages/021_impl-010_int_hubspot__owner_performance_metrics.md)。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/intermediate/int_hubspot__owner_performance_metrics.sql`；SHA-256 `95e15c6279c4d9059fbb12e403c1b29145a06cb12434c32bdb2a136b1a8088b6`。
- gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/sql/intermediate/int_hubspot__owner_performance_metrics.sql`；SHA-256 `fb03e6668cbbcb93b3547c763ec0f8a15c3b599371457fa9d186e50387ee29cc`。

deals_won_rank单处对齐后，183个该列差异消失，但另一个允许并列顺序的cycle_time_rank由2格变为10格，所以净减175格，不把183格当作净减少量。

各改动都是一个唯一出现的SQL位置，准确old/new、offset及其余字节不变的哈希证据见末尾机器记录。同做法出现在不同表达式时分别修改、分别计数；零改善/变差候选不列参与因素。

## agent可见证据与不确定性

event 1的message含完整契约，路径：`/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/1.json`。
原字段字符偏移60228起摘录：

```text
Size-specific win rates: within Enterprise and Large respectively, wins divided by (wins + losses) times 100; if no closed deals in that size then 0. - Keep only owners with total_deals > 0. - Compute window metrics across all remaining owners (no partitions): - revenue_rank: position when ordering by total_won_revenue descending (1 = highest; ties break arbitrarily). - win_rate_rank: position when ordering by win_rate_percentage descending (1 =
```

复查impl-010全部75个事件：event21/27写入模型，event49/50比对字段和行数，event63/64列模型及部分行数；没有对本表主要排名顺序或分类标签作说明，也没有核验这些差异。event73最终报告只列完成模型、执行/字段检查及其他输入清洗注意事项。工作清单不计“只有通用策略说明”；报告关于原始缺失属性/关联缺失的一般描述不说明这里的排名或标签选择。

本表主因不确定性因此由原“没有迹象（不知gold raw版本）”改为“看到了但没提（已看到契约要求，未讨论本表差异）”。不把agent不能访问gold当作未见自己契约。

最终报告事件：`/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/73.json`。历史完整轨迹索引仍见`records/021_trace_audit.json`。

## 查询与诊断

核实查询0条；代价档：需要查业务说明。类别由契约/代码直接判断，不虚构P或agent可见核实查询。下列允许读gold的诊断不计入5条核实额度；原件均READ_ONLY，诊断与重跑仅写data/025_closure私有库。

### win_rate_rank_tie_multisets
```sql
WITH a AS (SELECT win_rate_percentage k,list(win_rate_rank ORDER BY win_rate_rank) ranks FROM baseline GROUP BY 1),g AS (SELECT win_rate_percentage k,list(win_rate_rank ORDER BY win_rate_rank) ranks FROM gold.intermediate.int_hubspot__owner_performance_metrics GROUP BY 1) SELECT count(*) group_count,count(*) FILTER(WHERE a.ranks IS DISTINCT FROM g.ranks) bad_groups FROM a FULL JOIN g ON a.k IS NOT DISTINCT FROM g.k
```
```json
{"columns": ["group_count", "bad_groups"], "rows": [[1, 0]]}
```

### deals_won_rank_tie_multisets
```sql
WITH a AS (SELECT won_deals k,list(deals_won_rank ORDER BY deals_won_rank) ranks FROM baseline GROUP BY 1),g AS (SELECT won_deals k,list(deals_won_rank ORDER BY deals_won_rank) ranks FROM gold.intermediate.int_hubspot__owner_performance_metrics GROUP BY 1) SELECT count(*) group_count,count(*) FILTER(WHERE a.ranks IS DISTINCT FROM g.ranks) bad_groups FROM a FULL JOIN g ON a.k IS NOT DISTINCT FROM g.k
```
```json
{"columns": ["group_count", "bad_groups"], "rows": [[17, 0]]}
```

### cycle_time_rank_tie_multisets
```sql
WITH a AS (SELECT coalesce(avg_won_cycle_time,999) k,list(cycle_time_rank ORDER BY cycle_time_rank) ranks FROM baseline GROUP BY 1),g AS (SELECT coalesce(avg_won_cycle_time,999) k,list(cycle_time_rank ORDER BY cycle_time_rank) ranks FROM gold.intermediate.int_hubspot__owner_performance_metrics GROUP BY 1) SELECT count(*) group_count,count(*) FILTER(WHERE a.ranks IS DISTINCT FROM g.ranks) bad_groups FROM a FULL JOIN g ON a.k IS NOT DISTINCT FROM g.k
```
```json
{"columns": ["group_count", "bad_groups"], "rows": [[195, 0]]}
```

### cycle_time_rank_difference
```sql
SELECT cast(a.cycle_time_rank as varchar) agent_value,cast(g.cycle_time_rank as varchar) gold_value,count(*) n FROM baseline a JOIN gold.intermediate.int_hubspot__owner_performance_metrics g USING(owner_id) WHERE cast(a.cycle_time_rank as varchar) IS DISTINCT FROM cast(g.cycle_time_rank as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [["48", "49", 1], ["49", "48", 1]]}
```

### deals_won_rank_difference
```sql
SELECT cast(a.deals_won_rank as varchar) agent_value,cast(g.deals_won_rank as varchar) gold_value,count(*) n FROM baseline a JOIN gold.intermediate.int_hubspot__owner_performance_metrics g USING(owner_id) WHERE cast(a.deals_won_rank as varchar) IS DISTINCT FROM cast(g.deals_won_rank as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [["100", "102", 1], ["101", "92", 1], ["102", "91", 1], ["103", "88", 1], ["104", "103", 1]]}
```

### large_deal_win_rate_difference
```sql
SELECT cast(a.large_deal_win_rate as varchar) agent_value,cast(g.large_deal_win_rate as varchar) gold_value,count(*) n FROM baseline a JOIN gold.intermediate.int_hubspot__owner_performance_metrics g USING(owner_id) WHERE cast(a.large_deal_win_rate as varchar) IS DISTINCT FROM cast(g.large_deal_win_rate as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [[null, "0.0", 74]]}
```

### overall_performance_score_difference
```sql
SELECT cast(a.overall_performance_score as varchar) agent_value,cast(g.overall_performance_score as varchar) gold_value,count(*) n FROM baseline a JOIN gold.intermediate.int_hubspot__owner_performance_metrics g USING(owner_id) WHERE cast(a.overall_performance_score as varchar) IS DISTINCT FROM cast(g.overall_performance_score as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [["1243.718592964824", "1243.7185929648242", 1], ["1271.356783919598", "1271.3567839195982", 1], ["1278.8944723618092", "1278.894472361809", 1], ["1296.4824120603016", "1296.4824120603014", 1], ["1321.6080402010052", "1321.608040201005", 1]]}
```

### win_rate_rank_difference
```sql
SELECT cast(a.win_rate_rank as varchar) agent_value,cast(g.win_rate_rank as varchar) gold_value,count(*) n FROM baseline a JOIN gold.intermediate.int_hubspot__owner_performance_metrics g USING(owner_id) WHERE cast(a.win_rate_rank as varchar) IS DISTINCT FROM cast(g.win_rate_rank as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [["100", "182", 1], ["101", "183", 1], ["102", "184", 1], ["103", "185", 1], ["104", "186", 1]]}
```

辅助诊断：排除已定位列`win_rate_rank,deals_won_rank,cycle_time_rank,overall_performance_score,large_deal_win_rate`后，其余内容首次整表匹配为L0。此排除仅确认剩余差异范围，不进入主要原因排序。排名每个排序键组内rank多重集相同的查询单独列出。

## 时间控制、单点重跑与规模

复用021留存/基线记录核对源、时钟和SQL；新增干预统一使用threads=1和2025-10-13固定日期。源数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`；私有复制上游：`intermediate.int_hubspot__deals_enhanced, intermediate.int_hubspot__owners_enhanced`。所有减量对新增同控制基线计算；旧基线仅并列展示。

|记录|L0行/格|L1行/格|L2行/格|L3行/格|整表首次匹配|
|---|---:|---:|---:|---:|---|
|021留存|199/511|199/511|198/423|198/423|均未匹配|
|021原基线|199/511|199/511|198/423|198/423|均未匹配|
|baseline|199/511|199/511|198/423|198/423|均未匹配|
|win_rate_percentage|199/511|199/511|198/423|198/423|均未匹配|
|enterprise_win_rate|199/511|199/511|198/423|198/423|均未匹配|
|large_deal_win_rate|199/437|199/437|195/349|195/349|均未匹配|
|score_arithmetic|198/423|198/423|198/423|198/423|均未匹配|
|win_rate_rank_peer_order|200/359|200/359|195/271|195/271|均未匹配|
|deals_won_rank_peer_order|184/336|184/336|176/248|176/248|均未匹配|
|cycle_time_rank_peer_order|199/509|199/509|198/421|198/421|均未匹配|

|单处修改|类别|行减少|格减少|角色|
|---|---|---:|---:|---|
|win_rate_percentage|C|0|0|不计因素|
|enterprise_win_rate|C|0|0|不计因素|
|large_deal_win_rate|C|0|74|参与因素|
|score_arithmetic|O|1|88|参与因素|
|win_rate_rank_peer_order|O|-1|152|不计因素|
|deals_won_rank_peer_order|O|15|175|主因|
|cycle_time_rank_peer_order|O|0|2|参与因素|

**win_rate_percentage**：契约规定无closed deals返回0，原式NULLIF分母给NULL；每一处分开改。

**enterprise_win_rate**：契约规定无closed deals返回0，原式NULLIF分母给NULL；每一处分开改。

**large_deal_win_rate**：契约规定无closed deals返回0，原式NULLIF分母给NULL；每一处分开改。

**score_arithmetic**：代数等价计算的浮点运算次序；不修改权重/数据。

**win_rate_rank_peer_order**：诊断：仅在原排序键相同的peer内选用gold留存序号作为确定顺序；跨组排序不变。该CASE仅用于允许并列顺序的定位，不是生产修复，也不用于U证据。

**deals_won_rank_peer_order**：诊断：仅在原排序键相同的peer内选用gold留存序号作为确定顺序；跨组排序不变。该CASE仅用于允许并列顺序的定位，不是生产修复，也不用于U证据。

**cycle_time_rank_peer_order**：诊断：仅在原排序键相同的peer内选用gold留存序号作为确定顺序；跨组排序不变。该CASE仅用于允许并列顺序的定位，不是生产修复，也不用于U证据。

### 各档每列差异（共同键；本批均无独有/超额行）

|执行|档位|每列非零不一致数|
|---|---|---|
|baseline|L0|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "overall_performance_score": 88, "win_rate_rank": 164}`|
|baseline|L1|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "overall_performance_score": 88, "win_rate_rank": 164}`|
|baseline|L2|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "win_rate_rank": 164}`|
|baseline|L3|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "win_rate_rank": 164}`|
|win_rate_percentage|L0|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "overall_performance_score": 88, "win_rate_rank": 164}`|
|win_rate_percentage|L1|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "overall_performance_score": 88, "win_rate_rank": 164}`|
|win_rate_percentage|L2|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "win_rate_rank": 164}`|
|win_rate_percentage|L3|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "win_rate_rank": 164}`|
|enterprise_win_rate|L0|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "overall_performance_score": 88, "win_rate_rank": 164}`|
|enterprise_win_rate|L1|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "overall_performance_score": 88, "win_rate_rank": 164}`|
|enterprise_win_rate|L2|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "win_rate_rank": 164}`|
|enterprise_win_rate|L3|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "win_rate_rank": 164}`|
|large_deal_win_rate|L0|`{"cycle_time_rank": 2, "deals_won_rank": 183, "overall_performance_score": 88, "win_rate_rank": 164}`|
|large_deal_win_rate|L1|`{"cycle_time_rank": 2, "deals_won_rank": 183, "overall_performance_score": 88, "win_rate_rank": 164}`|
|large_deal_win_rate|L2|`{"cycle_time_rank": 2, "deals_won_rank": 183, "win_rate_rank": 164}`|
|large_deal_win_rate|L3|`{"cycle_time_rank": 2, "deals_won_rank": 183, "win_rate_rank": 164}`|
|score_arithmetic|L0|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "win_rate_rank": 164}`|
|score_arithmetic|L1|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "win_rate_rank": 164}`|
|score_arithmetic|L2|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "win_rate_rank": 164}`|
|score_arithmetic|L3|`{"cycle_time_rank": 2, "deals_won_rank": 183, "large_deal_win_rate": 74, "win_rate_rank": 164}`|
|win_rate_rank_peer_order|L0|`{"cycle_time_rank": 6, "deals_won_rank": 191, "large_deal_win_rate": 74, "overall_performance_score": 88}`|
|win_rate_rank_peer_order|L1|`{"cycle_time_rank": 6, "deals_won_rank": 191, "large_deal_win_rate": 74, "overall_performance_score": 88}`|
|win_rate_rank_peer_order|L2|`{"cycle_time_rank": 6, "deals_won_rank": 191, "large_deal_win_rate": 74}`|
|win_rate_rank_peer_order|L3|`{"cycle_time_rank": 6, "deals_won_rank": 191, "large_deal_win_rate": 74}`|
|deals_won_rank_peer_order|L0|`{"cycle_time_rank": 10, "large_deal_win_rate": 74, "overall_performance_score": 88, "win_rate_rank": 164}`|
|deals_won_rank_peer_order|L1|`{"cycle_time_rank": 10, "large_deal_win_rate": 74, "overall_performance_score": 88, "win_rate_rank": 164}`|
|deals_won_rank_peer_order|L2|`{"cycle_time_rank": 10, "large_deal_win_rate": 74, "win_rate_rank": 164}`|
|deals_won_rank_peer_order|L3|`{"cycle_time_rank": 10, "large_deal_win_rate": 74, "win_rate_rank": 164}`|
|cycle_time_rank_peer_order|L0|`{"deals_won_rank": 183, "large_deal_win_rate": 74, "overall_performance_score": 88, "win_rate_rank": 164}`|
|cycle_time_rank_peer_order|L1|`{"deals_won_rank": 183, "large_deal_win_rate": 74, "overall_performance_score": 88, "win_rate_rank": 164}`|
|cycle_time_rank_peer_order|L2|`{"deals_won_rank": 183, "large_deal_win_rate": 74, "win_rate_rank": 164}`|
|cycle_time_rank_peer_order|L3|`{"deals_won_rank": 183, "large_deal_win_rate": 74, "win_rate_rank": 164}`|

## 规则问题

允许并列顺序的O不能用数据假设检验来定义。本次先以每个排序键分组的排名多重集确认仅peer顺序不同，再将单个ROW_NUMBER增加gold留存顺序作诊断对齐；这是允许顺序的比较诊断，不是生产修复或U证据。一个窗口的顺序变化可能改变另一个窗口的隐式peer序，按实际全表净变化计数，不剔除该副作用。

没有改动手册定义。使用gold排序作为诊断的目的只是在契约允许的peer顺序内使比较条件一致；它不证明agent需要知道gold，也不构成U的单改证据。

## 完整机器证据及复现

旧记录：`records/021_reruns_impl-010_int_hubspot__owner_performance_metrics.json`（未修改）。下列JSON是本次新增单点重跑的完整结果，随本逐表记录交付，未另行更新汇总。

<details><summary>共同控制、原/新片段、位置、私有SQL路径及L0–L3完整计数</summary>

<!-- correction-A-rerun-json -->
```json
{
  "started_utc": "2026-10-30T11:03:54.975708+00:00",
  "task": "impl-010",
  "basis": {
    "kind": "original_007_009",
    "record": "records/007_tolerance_tables.jsonl",
    "detail_record": "/home/katherine/Assumption_Ledger/records/005_cs_impl-010.json",
    "prediction_database": "/home/katherine/Assumption_Ledger/data/005_cs_work/impl-010/node_results.duckdb",
    "gold_database": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb",
    "actual_schema": "intermediate",
    "table": "int_hubspot__owner_performance_metrics",
    "candidate_date": null,
    "comparison_columns": [
      "avg_lost_cycle_time",
      "avg_won_cycle_time",
      "avg_won_deal_size",
      "cycle_time_rank",
      "deals_won_rank",
      "development_focus",
      "efficiency_percentile",
      "enterprise_deals",
      "enterprise_win_rate",
      "large_deal_win_rate",
      "large_deals",
      "lost_deals",
      "medium_deals",
      "open_deals",
      "overall_performance_score",
      "owner_email",
      "owner_id",
      "owner_name",
      "performance_tier",
      "pipeline_health_status",
      "pipeline_value",
      "revenue_percentile",
      "revenue_rank",
      "sales_specialization",
      "small_deals",
      "total_deals",
      "total_won_revenue",
      "volume_percentile",
      "win_rate_percentage",
      "win_rate_percentile",
      "win_rate_rank",
      "won_deals"
    ],
    "key_columns": [
      "owner_id"
    ],
    "prediction_rows": 200,
    "gold_rows": 200,
    "row_delta": 0,
    "key_statistics": {
      "pred_distinct_keys": 200,
      "gold_distinct_keys": 200,
      "pred_duplicate_key_groups": 0,
      "gold_duplicate_key_groups": 0,
      "pred_only_keys": 0,
      "gold_only_keys": 0,
      "shared_keys": 200,
      "shared_nonunique_key_groups": 0
    },
    "l0_column_differences": [
      {
        "column": "owner_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "owner_name",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "owner_email",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "total_deals",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "won_deals",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "lost_deals",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "open_deals",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "win_rate_percentage",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "total_won_revenue",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "avg_won_deal_size",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "pipeline_value",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "avg_won_cycle_time",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "avg_lost_cycle_time",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "enterprise_deals",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "large_deals",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "medium_deals",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "small_deals",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "enterprise_win_rate",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "large_deal_win_rate",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 74,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 74,
        "pred_unmatched_value_occurrences": 74,
        "gold_unmatched_value_occurrences": 74,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "revenue_rank",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "win_rate_rank",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 164,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 164,
        "pred_unmatched_value_occurrences": 164,
        "gold_unmatched_value_occurrences": 164,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "deals_won_rank",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 183,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 183,
        "pred_unmatched_value_occurrences": 183,
        "gold_unmatched_value_occurrences": 183,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "cycle_time_rank",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 2,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 2,
        "pred_unmatched_value_occurrences": 2,
        "gold_unmatched_value_occurrences": 2,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "revenue_percentile",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "win_rate_percentile",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "volume_percentile",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "efficiency_percentile",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "overall_performance_score",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 88,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 88,
        "pred_unmatched_value_occurrences": 88,
        "gold_unmatched_value_occurrences": 88,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "performance_tier",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "sales_specialization",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "development_focus",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "pipeline_health_status",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      }
    ],
    "l3_column_differences": [
      {
        "column": "avg_lost_cycle_time",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "avg_won_cycle_time",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "avg_won_deal_size",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "cycle_time_rank",
        "one_to_one_mismatch_rows": 2,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 2,
        "pred_unmatched_value_occurrences": 2,
        "gold_unmatched_value_occurrences": 2,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "deals_won_rank",
        "one_to_one_mismatch_rows": 183,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 183,
        "pred_unmatched_value_occurrences": 183,
        "gold_unmatched_value_occurrences": 183,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "development_focus",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "efficiency_percentile",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "enterprise_deals",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "enterprise_win_rate",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "large_deal_win_rate",
        "one_to_one_mismatch_rows": 74,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 74,
        "pred_unmatched_value_occurrences": 74,
        "gold_unmatched_value_occurrences": 74,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "large_deals",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "lost_deals",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "medium_deals",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "open_deals",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "overall_performance_score",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "owner_email",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "owner_id",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "owner_name",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "performance_tier",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "pipeline_health_status",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "pipeline_value",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "revenue_percentile",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "revenue_rank",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "sales_specialization",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "small_deals",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "total_deals",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "total_won_revenue",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "volume_percentile",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "win_rate_percentage",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "win_rate_percentile",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "win_rate_rank",
        "one_to_one_mismatch_rows": 164,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 164,
        "pred_unmatched_value_occurrences": 164,
        "gold_unmatched_value_occurrences": 164,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "won_deals",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      }
    ],
    "whole_match_level": "仍不匹配",
    "keyed_match_level": "仍不匹配",
    "selection_reason": "未进入 011，沿用原差异",
    "value_representation": "Unmodified DuckDB CAST AS VARCHAR; SQL NULL is JSON null. Keys use the unchanged historical L0 normalization.",
    "new_queries_only_read_existing_results": true,
    "one_side_key_examples": {
      "prediction_only": [],
      "gold_only": []
    },
    "column_details": [
      {
        "column": "owner_id",
        "l0_counts_verbatim": {
          "column": "owner_id",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "owner_id",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "VARCHAR",
        "gold_actual_type": "VARCHAR"
      },
      {
        "column": "owner_name",
        "l0_counts_verbatim": {
          "column": "owner_name",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "owner_name",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "VARCHAR",
        "gold_actual_type": "VARCHAR"
      },
      {
        "column": "owner_email",
        "l0_counts_verbatim": {
          "column": "owner_email",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "owner_email",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "VARCHAR",
        "gold_actual_type": "VARCHAR"
      },
      {
        "column": "total_deals",
        "l0_counts_verbatim": {
          "column": "total_deals",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "total_deals",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "won_deals",
        "l0_counts_verbatim": {
          "column": "won_deals",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "won_deals",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "lost_deals",
        "l0_counts_verbatim": {
          "column": "lost_deals",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "lost_deals",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "open_deals",
        "l0_counts_verbatim": {
          "column": "open_deals",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "open_deals",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "win_rate_percentage",
        "l0_counts_verbatim": {
          "column": "win_rate_percentage",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "win_rate_percentage",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "total_won_revenue",
        "l0_counts_verbatim": {
          "column": "total_won_revenue",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "total_won_revenue",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
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
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "avg_won_deal_size",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "pipeline_value",
        "l0_counts_verbatim": {
          "column": "pipeline_value",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "pipeline_value",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DECIMAL(38,2)",
        "gold_actual_type": "DECIMAL(38,2)"
      },
      {
        "column": "avg_won_cycle_time",
        "l0_counts_verbatim": {
          "column": "avg_won_cycle_time",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "avg_won_cycle_time",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "avg_lost_cycle_time",
        "l0_counts_verbatim": {
          "column": "avg_lost_cycle_time",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "avg_lost_cycle_time",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "enterprise_deals",
        "l0_counts_verbatim": {
          "column": "enterprise_deals",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "enterprise_deals",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "large_deals",
        "l0_counts_verbatim": {
          "column": "large_deals",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "large_deals",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "medium_deals",
        "l0_counts_verbatim": {
          "column": "medium_deals",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "medium_deals",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "small_deals",
        "l0_counts_verbatim": {
          "column": "small_deals",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "small_deals",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "enterprise_win_rate",
        "l0_counts_verbatim": {
          "column": "enterprise_win_rate",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "enterprise_win_rate",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "large_deal_win_rate",
        "l0_counts_verbatim": {
          "column": "large_deal_win_rate",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 74,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 74,
          "pred_unmatched_value_occurrences": 74,
          "gold_unmatched_value_occurrences": 74,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "large_deal_win_rate",
          "one_to_one_mismatch_rows": 74,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 74,
          "pred_unmatched_value_occurrences": 74,
          "gold_unmatched_value_occurrences": 74,
          "marginal_multisets_equal": false,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [
          {
            "key_normalized": {
              "owner_id": "1000"
            },
            "agent_key_raw_text": {
              "owner_id": "1000"
            },
            "gold_key_raw_text": {
              "owner_id": "1000"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": null,
            "gold_value": "0.0"
          },
          {
            "key_normalized": {
              "owner_id": "1006"
            },
            "agent_key_raw_text": {
              "owner_id": "1006"
            },
            "gold_key_raw_text": {
              "owner_id": "1006"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": null,
            "gold_value": "0.0"
          },
          {
            "key_normalized": {
              "owner_id": "1007"
            },
            "agent_key_raw_text": {
              "owner_id": "1007"
            },
            "gold_key_raw_text": {
              "owner_id": "1007"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": null,
            "gold_value": "0.0"
          },
          {
            "key_normalized": {
              "owner_id": "1012"
            },
            "agent_key_raw_text": {
              "owner_id": "1012"
            },
            "gold_key_raw_text": {
              "owner_id": "1012"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": null,
            "gold_value": "0.0"
          },
          {
            "key_normalized": {
              "owner_id": "1016"
            },
            "agent_key_raw_text": {
              "owner_id": "1016"
            },
            "gold_key_raw_text": {
              "owner_id": "1016"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": null,
            "gold_value": "0.0"
          }
        ],
        "sample_counts_recheck": {
          "mismatch_rows_or_minimum_pairs": 74,
          "pred_unmatched_value_occurrences": 74,
          "gold_unmatched_value_occurrences": 74
        },
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "revenue_rank",
        "l0_counts_verbatim": {
          "column": "revenue_rank",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "revenue_rank",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "win_rate_rank",
        "l0_counts_verbatim": {
          "column": "win_rate_rank",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 164,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 164,
          "pred_unmatched_value_occurrences": 164,
          "gold_unmatched_value_occurrences": 164,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "win_rate_rank",
          "one_to_one_mismatch_rows": 164,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 164,
          "pred_unmatched_value_occurrences": 164,
          "gold_unmatched_value_occurrences": 164,
          "marginal_multisets_equal": false,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [
          {
            "key_normalized": {
              "owner_id": "1000"
            },
            "agent_key_raw_text": {
              "owner_id": "1000"
            },
            "gold_key_raw_text": {
              "owner_id": "1000"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "86",
            "gold_value": "168"
          },
          {
            "key_normalized": {
              "owner_id": "1001"
            },
            "agent_key_raw_text": {
              "owner_id": "1001"
            },
            "gold_key_raw_text": {
              "owner_id": "1001"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "89",
            "gold_value": "171"
          },
          {
            "key_normalized": {
              "owner_id": "1002"
            },
            "agent_key_raw_text": {
              "owner_id": "1002"
            },
            "gold_key_raw_text": {
              "owner_id": "1002"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "94",
            "gold_value": "176"
          },
          {
            "key_normalized": {
              "owner_id": "1004"
            },
            "agent_key_raw_text": {
              "owner_id": "1004"
            },
            "gold_key_raw_text": {
              "owner_id": "1004"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "60",
            "gold_value": "142"
          },
          {
            "key_normalized": {
              "owner_id": "1005"
            },
            "agent_key_raw_text": {
              "owner_id": "1005"
            },
            "gold_key_raw_text": {
              "owner_id": "1005"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "126",
            "gold_value": "44"
          }
        ],
        "sample_counts_recheck": {
          "mismatch_rows_or_minimum_pairs": 164,
          "pred_unmatched_value_occurrences": 164,
          "gold_unmatched_value_occurrences": 164
        },
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "deals_won_rank",
        "l0_counts_verbatim": {
          "column": "deals_won_rank",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 183,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 183,
          "pred_unmatched_value_occurrences": 183,
          "gold_unmatched_value_occurrences": 183,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "deals_won_rank",
          "one_to_one_mismatch_rows": 183,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 183,
          "pred_unmatched_value_occurrences": 183,
          "gold_unmatched_value_occurrences": 183,
          "marginal_multisets_equal": false,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [
          {
            "key_normalized": {
              "owner_id": "1000"
            },
            "agent_key_raw_text": {
              "owner_id": "1000"
            },
            "gold_key_raw_text": {
              "owner_id": "1000"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "119",
            "gold_value": "117"
          },
          {
            "key_normalized": {
              "owner_id": "1001"
            },
            "agent_key_raw_text": {
              "owner_id": "1001"
            },
            "gold_key_raw_text": {
              "owner_id": "1001"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "120",
            "gold_value": "118"
          },
          {
            "key_normalized": {
              "owner_id": "1002"
            },
            "agent_key_raw_text": {
              "owner_id": "1002"
            },
            "gold_key_raw_text": {
              "owner_id": "1002"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "60",
            "gold_value": "61"
          },
          {
            "key_normalized": {
              "owner_id": "1003"
            },
            "agent_key_raw_text": {
              "owner_id": "1003"
            },
            "gold_key_raw_text": {
              "owner_id": "1003"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "31",
            "gold_value": "33"
          },
          {
            "key_normalized": {
              "owner_id": "1004"
            },
            "agent_key_raw_text": {
              "owner_id": "1004"
            },
            "gold_key_raw_text": {
              "owner_id": "1004"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "102",
            "gold_value": "91"
          }
        ],
        "sample_counts_recheck": {
          "mismatch_rows_or_minimum_pairs": 183,
          "pred_unmatched_value_occurrences": 183,
          "gold_unmatched_value_occurrences": 183
        },
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "cycle_time_rank",
        "l0_counts_verbatim": {
          "column": "cycle_time_rank",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 2,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 2,
          "pred_unmatched_value_occurrences": 2,
          "gold_unmatched_value_occurrences": 2,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "cycle_time_rank",
          "one_to_one_mismatch_rows": 2,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 2,
          "pred_unmatched_value_occurrences": 2,
          "gold_unmatched_value_occurrences": 2,
          "marginal_multisets_equal": false,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [
          {
            "key_normalized": {
              "owner_id": "1001"
            },
            "agent_key_raw_text": {
              "owner_id": "1001"
            },
            "gold_key_raw_text": {
              "owner_id": "1001"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "48",
            "gold_value": "49"
          },
          {
            "key_normalized": {
              "owner_id": "1088"
            },
            "agent_key_raw_text": {
              "owner_id": "1088"
            },
            "gold_key_raw_text": {
              "owner_id": "1088"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "49",
            "gold_value": "48"
          }
        ],
        "sample_counts_recheck": {
          "mismatch_rows_or_minimum_pairs": 2,
          "pred_unmatched_value_occurrences": 2,
          "gold_unmatched_value_occurrences": 2
        },
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "revenue_percentile",
        "l0_counts_verbatim": {
          "column": "revenue_percentile",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "revenue_percentile",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "win_rate_percentile",
        "l0_counts_verbatim": {
          "column": "win_rate_percentile",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "win_rate_percentile",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "volume_percentile",
        "l0_counts_verbatim": {
          "column": "volume_percentile",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "volume_percentile",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "efficiency_percentile",
        "l0_counts_verbatim": {
          "column": "efficiency_percentile",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "efficiency_percentile",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "overall_performance_score",
        "l0_counts_verbatim": {
          "column": "overall_performance_score",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 88,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 88,
          "pred_unmatched_value_occurrences": 88,
          "gold_unmatched_value_occurrences": 88,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "overall_performance_score",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [
          {
            "key_normalized": {
              "owner_id": "1002"
            },
            "agent_key_raw_text": {
              "owner_id": "1002"
            },
            "gold_key_raw_text": {
              "owner_id": "1002"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "3934.6733668341712",
            "gold_value": "3934.673366834171"
          },
          {
            "key_normalized": {
              "owner_id": "1004"
            },
            "agent_key_raw_text": {
              "owner_id": "1004"
            },
            "gold_key_raw_text": {
              "owner_id": "1004"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "5148.241206030151",
            "gold_value": "5148.24120603015"
          },
          {
            "key_normalized": {
              "owner_id": "1008"
            },
            "agent_key_raw_text": {
              "owner_id": "1008"
            },
            "gold_key_raw_text": {
              "owner_id": "1008"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "2711.0552763819096",
            "gold_value": "2711.055276381909"
          },
          {
            "key_normalized": {
              "owner_id": "1011"
            },
            "agent_key_raw_text": {
              "owner_id": "1011"
            },
            "gold_key_raw_text": {
              "owner_id": "1011"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "6291.457286432161",
            "gold_value": "6291.457286432162"
          },
          {
            "key_normalized": {
              "owner_id": "1014"
            },
            "agent_key_raw_text": {
              "owner_id": "1014"
            },
            "gold_key_raw_text": {
              "owner_id": "1014"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "1364.3216080402008",
            "gold_value": "1364.321608040201"
          }
        ],
        "sample_counts_recheck": {
          "mismatch_rows_or_minimum_pairs": 88,
          "pred_unmatched_value_occurrences": 88,
          "gold_unmatched_value_occurrences": 88
        },
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "performance_tier",
        "l0_counts_verbatim": {
          "column": "performance_tier",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "performance_tier",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "VARCHAR",
        "gold_actual_type": "VARCHAR"
      },
      {
        "column": "sales_specialization",
        "l0_counts_verbatim": {
          "column": "sales_specialization",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "sales_specialization",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "VARCHAR",
        "gold_actual_type": "VARCHAR"
      },
      {
        "column": "development_focus",
        "l0_counts_verbatim": {
          "column": "development_focus",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "development_focus",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
        },
        "sample_level": "L0",
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "VARCHAR",
        "gold_actual_type": "VARCHAR"
      },
      {
        "column": "pipeline_health_status",
        "l0_counts_verbatim": {
          "column": "pipeline_health_status",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "pipeline_health_status",
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "marginal_multisets_equal": true,
          "count_semantics": "exact_one_to_one_rows"
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
      "count": 0
    }
  ],
  "runs": [
    {
      "label": "baseline",
      "edits": [],
      "sql_path": "data/025_closure/work/impl-010_int_hubspot__owner_performance_metrics/baseline.sql",
      "sql_sha256": "95e15c6279c4d9059fbb12e403c1b29145a06cb12434c32bdb2a136b1a8088b6",
      "comparison": {
        "levels": [
          {
            "level": "L0",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 511,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L1",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 511,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 198,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 423,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 198,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 423,
            "comparison_column_count_including_keys": 32
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "win_rate_percentage",
      "edits": [
        {
          "old": "100.0*count(*) filter(where status='Won')/nullif(count(*) filter(where status in ('Won','Lost')),0) win_rate_percentage",
          "new": "coalesce(100.0*count(*) filter(where status='Won')/nullif(count(*) filter(where status in ('Won','Lost')),0),0) win_rate_percentage",
          "offset": 740
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_int_hubspot__owner_performance_metrics/win_rate_percentage.sql",
      "sql_sha256": "0fc4061362e20930c10bfbecd734f7f8e310bbb4c8b3efed1c960599cfd8dde2",
      "comparison": {
        "levels": [
          {
            "level": "L0",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 511,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L1",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 511,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 198,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 423,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 198,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 423,
            "comparison_column_count_including_keys": 32
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "enterprise_win_rate",
      "edits": [
        {
          "old": "100.0*count(*) filter(where size='Enterprise' and status='Won')/nullif(count(*) filter(where size='Enterprise' and status in('Won','Lost')),0) enterprise_win_rate",
          "new": "coalesce(100.0*count(*) filter(where size='Enterprise' and status='Won')/nullif(count(*) filter(where size='Enterprise' and status in('Won','Lost')),0),0) enterprise_win_rate",
          "offset": 1542
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_int_hubspot__owner_performance_metrics/enterprise_win_rate.sql",
      "sql_sha256": "d645b41bdde3b2fe766c2a042ff81255fb88eb13c99ae811d9d040d63386e174",
      "comparison": {
        "levels": [
          {
            "level": "L0",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 511,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L1",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 511,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 198,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 423,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 198,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 423,
            "comparison_column_count_including_keys": 32
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "large_deal_win_rate",
      "edits": [
        {
          "old": "100.0*count(*) filter(where size='Large' and status='Won')/nullif(count(*) filter(where size='Large' and status in('Won','Lost')),0) large_deal_win_rate",
          "new": "coalesce(100.0*count(*) filter(where size='Large' and status='Won')/nullif(count(*) filter(where size='Large' and status in('Won','Lost')),0),0) large_deal_win_rate",
          "offset": 1705
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_int_hubspot__owner_performance_metrics/large_deal_win_rate.sql",
      "sql_sha256": "4aa89c584631b30ca0d56a2f84df109d397f94b00056ed786ec70fae913d2b62",
      "comparison": {
        "levels": [
          {
            "level": "L0",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 437,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L1",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 437,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 195,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 195,
            "key_aware_gold_unmatched": 195,
            "whole_match": false,
            "row_scale": 195,
            "cell_scale": 349,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 195,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 195,
            "key_aware_gold_unmatched": 195,
            "whole_match": false,
            "row_scale": 195,
            "cell_scale": 349,
            "comparison_column_count_including_keys": 32
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "score_arithmetic",
      "edits": [
        {
          "old": "revenue_percentile*40+win_rate_percentile*25+volume_percentile*20+efficiency_percentile*15",
          "new": "(percent_rank() over(order by total_won_revenue)*40+percent_rank() over(order by win_rate_percentage)*25+percent_rank() over(order by won_deals)*20+percent_rank() over(order by coalesce(avg_won_cycle_time,999) desc)*15)*100",
          "offset": 2615
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_int_hubspot__owner_performance_metrics/score_arithmetic.sql",
      "sql_sha256": "c8ea0e8c8e87ec9879ac16f3ba5bcbed12ba3c80a4f9453f067701b61ba1f8ea",
      "comparison": {
        "levels": [
          {
            "level": "L0",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 198,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 423,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L1",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 198,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 423,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 198,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 423,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 198,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 2,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 423,
            "comparison_column_count_including_keys": 32
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "win_rate_rank_peer_order",
      "edits": [
        {
          "old": "row_number() over(order by win_rate_percentage desc nulls last)",
          "new": "row_number() over(order by win_rate_percentage desc, CASE owner_id WHEN '1000' THEN 168 WHEN '1001' THEN 171 WHEN '1002' THEN 176 WHEN '1003' THEN 28 WHEN '1004' THEN 142 WHEN '1005' THEN 44 WHEN '1006' THEN 144 WHEN '1007' THEN 165 WHEN '1008' THEN 60 WHEN '1009' THEN 148 WHEN '1010' THEN 14 WHEN '1011' THEN 124 WHEN '1012' THEN 38 WHEN '1013' THEN 143 WHEN '1014' THEN 93 WHEN '1015' THEN 59 WHEN '1016' THEN 151 WHEN '1017' THEN 163 WHEN '1018' THEN 157 WHEN '1019' THEN 74 WHEN '1020' THEN 187 WHEN '1021' THEN 3 WHEN '1022' THEN 40 WHEN '1023' THEN 160 WHEN '1024' THEN 33 WHEN '1025' THEN 107 WHEN '1026' THEN 95 WHEN '1027' THEN 43 WHEN '1028' THEN 84 WHEN '1029' THEN 159 WHEN '1030' THEN 99 WHEN '1031' THEN 20 WHEN '1032' THEN 199 WHEN '1033' THEN 82 WHEN '1034' THEN 174 WHEN '1035' THEN 57 WHEN '1036' THEN 69 WHEN '1037' THEN 47 WHEN '1038' THEN 185 WHEN '1039' THEN 1 WHEN '1040' THEN 29 WHEN '1041' THEN 123 WHEN '1042' THEN 77 WHEN '1043' THEN 17 WHEN '1044' THEN 8 WHEN '1045' THEN 180 WHEN '1046' THEN 25 WHEN '1047' THEN 31 WHEN '1048' THEN 196 WHEN '1049' THEN 81 WHEN '1050' THEN 118 WHEN '1051' THEN 32 WHEN '1052' THEN 179 WHEN '1053' THEN 106 WHEN '1054' THEN 109 WHEN '1055' THEN 191 WHEN '1056' THEN 140 WHEN '1057' THEN 16 WHEN '1058' THEN 68 WHEN '1059' THEN 141 WHEN '1060' THEN 90 WHEN '1061' THEN 195 WHEN '1062' THEN 19 WHEN '1063' THEN 12 WHEN '1064' THEN 96 WHEN '1065' THEN 22 WHEN '1066' THEN 194 WHEN '1067' THEN 64 WHEN '1068' THEN 127 WHEN '1069' THEN 71 WHEN '1070' THEN 125 WHEN '1071' THEN 113 WHEN '1072' THEN 2 WHEN '1073' THEN 170 WHEN '1074' THEN 134 WHEN '1075' THEN 63 WHEN '1076' THEN 173 WHEN '1077' THEN 11 WHEN '1078' THEN 130 WHEN '1079' THEN 172 WHEN '1080' THEN 114 WHEN '1081' THEN 100 WHEN '1082' THEN 92 WHEN '1083' THEN 169 WHEN '1084' THEN 78 WHEN '1085' THEN 26 WHEN '1086' THEN 42 WHEN '1087' THEN 30 WHEN '1088' THEN 167 WHEN '1089' THEN 86 WHEN '1090' THEN 105 WHEN '1091' THEN 158 WHEN '1092' THEN 67 WHEN '1093' THEN 155 WHEN '1094' THEN 197 WHEN '1095' THEN 46 WHEN '1096' THEN 175 WHEN '1097' THEN 10 WHEN '1098' THEN 49 WHEN '1099' THEN 147 WHEN '1100' THEN 146 WHEN '1101' THEN 120 WHEN '1102' THEN 27 WHEN '1103' THEN 37 WHEN '1104' THEN 50 WHEN '1105' THEN 121 WHEN '1106' THEN 154 WHEN '1107' THEN 54 WHEN '1108' THEN 112 WHEN '1109' THEN 35 WHEN '1110' THEN 52 WHEN '1111' THEN 138 WHEN '1112' THEN 9 WHEN '1113' THEN 91 WHEN '1114' THEN 89 WHEN '1115' THEN 189 WHEN '1116' THEN 178 WHEN '1117' THEN 45 WHEN '1118' THEN 97 WHEN '1119' THEN 166 WHEN '1120' THEN 51 WHEN '1121' THEN 36 WHEN '1122' THEN 5 WHEN '1123' THEN 94 WHEN '1124' THEN 135 WHEN '1125' THEN 80 WHEN '1126' THEN 183 WHEN '1127' THEN 119 WHEN '1128' THEN 184 WHEN '1129' THEN 186 WHEN '1130' THEN 132 WHEN '1131' THEN 98 WHEN '1132' THEN 85 WHEN '1133' THEN 193 WHEN '1134' THEN 137 WHEN '1135' THEN 115 WHEN '1136' THEN 23 WHEN '1137' THEN 152 WHEN '1138' THEN 21 WHEN '1139' THEN 181 WHEN '1140' THEN 182 WHEN '1141' THEN 153 WHEN '1142' THEN 110 WHEN '1143' THEN 88 WHEN '1144' THEN 87 WHEN '1145' THEN 128 WHEN '1146' THEN 192 WHEN '1147' THEN 41 WHEN '1148' THEN 39 WHEN '1149' THEN 75 WHEN '1150' THEN 104 WHEN '1151' THEN 13 WHEN '1152' THEN 73 WHEN '1153' THEN 161 WHEN '1154' THEN 56 WHEN '1155' THEN 103 WHEN '1156' THEN 66 WHEN '1157' THEN 162 WHEN '1158' THEN 188 WHEN '1159' THEN 55 WHEN '1160' THEN 117 WHEN '1161' THEN 15 WHEN '1162' THEN 61 WHEN '1163' THEN 58 WHEN '1164' THEN 83 WHEN '1165' THEN 150 WHEN '1166' THEN 7 WHEN '1167' THEN 4 WHEN '1168' THEN 34 WHEN '1169' THEN 53 WHEN '1170' THEN 70 WHEN '1171' THEN 111 WHEN '1172' THEN 48 WHEN '1173' THEN 156 WHEN '1174' THEN 62 WHEN '1175' THEN 24 WHEN '1176' THEN 72 WHEN '1177' THEN 149 WHEN '1178' THEN 164 WHEN '1179' THEN 79 WHEN '1180' THEN 198 WHEN '1181' THEN 126 WHEN '1182' THEN 129 WHEN '1183' THEN 122 WHEN '1184' THEN 177 WHEN '1185' THEN 18 WHEN '1186' THEN 190 WHEN '1187' THEN 6 WHEN '1188' THEN 133 WHEN '1189' THEN 101 WHEN '1190' THEN 139 WHEN '1191' THEN 131 WHEN '1192' THEN 76 WHEN '1193' THEN 65 WHEN '1194' THEN 200 WHEN '1195' THEN 116 WHEN '1196' THEN 145 WHEN '1197' THEN 108 WHEN '1198' THEN 136 WHEN '1199' THEN 102 END)",
          "offset": 2076
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_int_hubspot__owner_performance_metrics/win_rate_rank_peer_order.sql",
      "sql_sha256": "8b596e80d85bd3ee0fe852cc275045fad82705aa57a98205c62f2b29104aea79",
      "comparison": {
        "levels": [
          {
            "level": "L0",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 6,
              "deals_won_rank": 191,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 0,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 359,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L1",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 6,
              "deals_won_rank": 191,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 0,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 359,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 195,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 6,
              "deals_won_rank": 191,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 0,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 195,
            "key_aware_gold_unmatched": 195,
            "whole_match": false,
            "row_scale": 195,
            "cell_scale": 271,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 195,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 6,
              "deals_won_rank": 191,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 0,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 195,
            "key_aware_gold_unmatched": 195,
            "whole_match": false,
            "row_scale": 195,
            "cell_scale": 271,
            "comparison_column_count_including_keys": 32
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "deals_won_rank_peer_order",
      "edits": [
        {
          "old": "row_number() over(order by won_deals desc)",
          "new": "row_number() over(order by won_deals desc, CASE owner_id WHEN '1000' THEN 117 WHEN '1001' THEN 118 WHEN '1002' THEN 61 WHEN '1003' THEN 33 WHEN '1004' THEN 91 WHEN '1005' THEN 108 WHEN '1006' THEN 70 WHEN '1007' THEN 97 WHEN '1008' THEN 132 WHEN '1009' THEN 93 WHEN '1010' THEN 21 WHEN '1011' THEN 9 WHEN '1012' THEN 150 WHEN '1013' THEN 56 WHEN '1014' THEN 173 WHEN '1015' THEN 152 WHEN '1016' THEN 71 WHEN '1017' THEN 77 WHEN '1018' THEN 116 WHEN '1019' THEN 182 WHEN '1020' THEN 147 WHEN '1021' THEN 2 WHEN '1022' THEN 82 WHEN '1023' THEN 74 WHEN '1024' THEN 17 WHEN '1025' THEN 198 WHEN '1026' THEN 194 WHEN '1027' THEN 50 WHEN '1028' THEN 138 WHEN '1029' THEN 59 WHEN '1030' THEN 175 WHEN '1031' THEN 44 WHEN '1032' THEN 105 WHEN '1033' THEN 192 WHEN '1034' THEN 120 WHEN '1035' THEN 111 WHEN '1036' THEN 87 WHEN '1037' THEN 63 WHEN '1038' THEN 162 WHEN '1039' THEN 1 WHEN '1040' THEN 47 WHEN '1041' THEN 51 WHEN '1042' THEN 36 WHEN '1043' THEN 22 WHEN '1044' THEN 27 WHEN '1045' THEN 101 WHEN '1046' THEN 16 WHEN '1047' THEN 35 WHEN '1048' THEN 124 WHEN '1049' THEN 136 WHEN '1050' THEN 200 WHEN '1051' THEN 23 WHEN '1052' THEN 145 WHEN '1053' THEN 187 WHEN '1054' THEN 179 WHEN '1055' THEN 163 WHEN '1056' THEN 55 WHEN '1057' THEN 32 WHEN '1058' THEN 167 WHEN '1059' THEN 69 WHEN '1060' THEN 140 WHEN '1061' THEN 148 WHEN '1062' THEN 14 WHEN '1063' THEN 30 WHEN '1064' THEN 174 WHEN '1065' THEN 15 WHEN '1066' THEN 123 WHEN '1067' THEN 166 WHEN '1068' THEN 26 WHEN '1069' THEN 168 WHEN '1070' THEN 52 WHEN '1071' THEN 197 WHEN '1072' THEN 11 WHEN '1073' THEN 99 WHEN '1074' THEN 53 WHEN '1075' THEN 154 WHEN '1076' THEN 42 WHEN '1077' THEN 20 WHEN '1078' THEN 39 WHEN '1079' THEN 119 WHEN '1080' THEN 181 WHEN '1081' THEN 184 WHEN '1082' THEN 141 WHEN '1083' THEN 98 WHEN '1084' THEN 157 WHEN '1085' THEN 45 WHEN '1086' THEN 107 WHEN '1087' THEN 34 WHEN '1088' THEN 41 WHEN '1089' THEN 139 WHEN '1090' THEN 186 WHEN '1091' THEN 142 WHEN '1092' THEN 113 WHEN '1093' THEN 73 WHEN '1094' THEN 149 WHEN '1095' THEN 129 WHEN '1096' THEN 143 WHEN '1097' THEN 29 WHEN '1098' THEN 84 WHEN '1099' THEN 57 WHEN '1100' THEN 18 WHEN '1101' THEN 24 WHEN '1102' THEN 46 WHEN '1103' THEN 81 WHEN '1104' THEN 109 WHEN '1105' THEN 37 WHEN '1106' THEN 10 WHEN '1107' THEN 151 WHEN '1108' THEN 189 WHEN '1109' THEN 48 WHEN '1110' THEN 110 WHEN '1111' THEN 68 WHEN '1112' THEN 28 WHEN '1113' THEN 160 WHEN '1114' THEN 193 WHEN '1115' THEN 78 WHEN '1116' THEN 144 WHEN '1117' THEN 128 WHEN '1118' THEN 183 WHEN '1119' THEN 60 WHEN '1120' THEN 85 WHEN '1121' THEN 49 WHEN '1122' THEN 3 WHEN '1123' THEN 161 WHEN '1124' THEN 89 WHEN '1125' THEN 171 WHEN '1126' THEN 102 WHEN '1127' THEN 64 WHEN '1128' THEN 122 WHEN '1129' THEN 103 WHEN '1130' THEN 67 WHEN '1131' THEN 195 WHEN '1132' THEN 172 WHEN '1133' THEN 164 WHEN '1134' THEN 54 WHEN '1135' THEN 190 WHEN '1136' THEN 7 WHEN '1137' THEN 95 WHEN '1138' THEN 6 WHEN '1139' THEN 146 WHEN '1140' THEN 121 WHEN '1141' THEN 72 WHEN '1142' THEN 188 WHEN '1143' THEN 159 WHEN '1144' THEN 158 WHEN '1145' THEN 65 WHEN '1146' THEN 80 WHEN '1147' THEN 106 WHEN '1148' THEN 127 WHEN '1149' THEN 135 WHEN '1150' THEN 185 WHEN '1151' THEN 31 WHEN '1152' THEN 170 WHEN '1153' THEN 75 WHEN '1154' THEN 131 WHEN '1155' THEN 178 WHEN '1156' THEN 112 WHEN '1157' THEN 76 WHEN '1158' THEN 104 WHEN '1159' THEN 86 WHEN '1160' THEN 191 WHEN '1161' THEN 13 WHEN '1162' THEN 133 WHEN '1163' THEN 165 WHEN '1164' THEN 137 WHEN '1165' THEN 94 WHEN '1166' THEN 4 WHEN '1167' THEN 12 WHEN '1168' THEN 62 WHEN '1169' THEN 130 WHEN '1170' THEN 155 WHEN '1171' THEN 180 WHEN '1172' THEN 83 WHEN '1173' THEN 19 WHEN '1174' THEN 153 WHEN '1175' THEN 8 WHEN '1176' THEN 169 WHEN '1177' THEN 58 WHEN '1178' THEN 96 WHEN '1179' THEN 114 WHEN '1180' THEN 125 WHEN '1181' THEN 88 WHEN '1182' THEN 38 WHEN '1183' THEN 25 WHEN '1184' THEN 100 WHEN '1185' THEN 5 WHEN '1186' THEN 79 WHEN '1187' THEN 43 WHEN '1188' THEN 40 WHEN '1189' THEN 176 WHEN '1190' THEN 115 WHEN '1191' THEN 66 WHEN '1192' THEN 156 WHEN '1193' THEN 134 WHEN '1194' THEN 126 WHEN '1195' THEN 199 WHEN '1196' THEN 92 WHEN '1197' THEN 196 WHEN '1198' THEN 90 WHEN '1199' THEN 177 END)",
          "offset": 2154
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_int_hubspot__owner_performance_metrics/deals_won_rank_peer_order.sql",
      "sql_sha256": "6fe1b26a21be3107726cf130086916429db2a4a8b7048e1eb372561ebee8ca0d",
      "comparison": {
        "levels": [
          {
            "level": "L0",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 184,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 10,
              "deals_won_rank": 0,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 184,
            "key_aware_gold_unmatched": 184,
            "whole_match": false,
            "row_scale": 184,
            "cell_scale": 336,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L1",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 184,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 10,
              "deals_won_rank": 0,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 184,
            "key_aware_gold_unmatched": 184,
            "whole_match": false,
            "row_scale": 184,
            "cell_scale": 336,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 176,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 10,
              "deals_won_rank": 0,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 176,
            "key_aware_gold_unmatched": 176,
            "whole_match": false,
            "row_scale": 176,
            "cell_scale": 248,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 176,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 10,
              "deals_won_rank": 0,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 176,
            "key_aware_gold_unmatched": 176,
            "whole_match": false,
            "row_scale": 176,
            "cell_scale": 248,
            "comparison_column_count_including_keys": 32
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "cycle_time_rank_peer_order",
      "edits": [
        {
          "old": "row_number() over(order by coalesce(avg_won_cycle_time,999))",
          "new": "row_number() over(order by coalesce(avg_won_cycle_time,999), CASE owner_id WHEN '1000' THEN 182 WHEN '1001' THEN 49 WHEN '1002' THEN 146 WHEN '1003' THEN 123 WHEN '1004' THEN 17 WHEN '1005' THEN 127 WHEN '1006' THEN 117 WHEN '1007' THEN 139 WHEN '1008' THEN 63 WHEN '1009' THEN 21 WHEN '1010' THEN 105 WHEN '1011' THEN 40 WHEN '1012' THEN 128 WHEN '1013' THEN 116 WHEN '1014' THEN 111 WHEN '1015' THEN 1 WHEN '1016' THEN 86 WHEN '1017' THEN 33 WHEN '1018' THEN 77 WHEN '1019' THEN 72 WHEN '1020' THEN 85 WHEN '1021' THEN 145 WHEN '1022' THEN 29 WHEN '1023' THEN 10 WHEN '1024' THEN 84 WHEN '1025' THEN 151 WHEN '1026' THEN 7 WHEN '1027' THEN 83 WHEN '1028' THEN 173 WHEN '1029' THEN 178 WHEN '1030' THEN 19 WHEN '1031' THEN 97 WHEN '1032' THEN 82 WHEN '1033' THEN 198 WHEN '1034' THEN 34 WHEN '1035' THEN 5 WHEN '1036' THEN 25 WHEN '1037' THEN 70 WHEN '1038' THEN 31 WHEN '1039' THEN 138 WHEN '1040' THEN 32 WHEN '1041' THEN 103 WHEN '1042' THEN 20 WHEN '1043' THEN 163 WHEN '1044' THEN 110 WHEN '1045' THEN 13 WHEN '1046' THEN 124 WHEN '1047' THEN 106 WHEN '1048' THEN 155 WHEN '1049' THEN 197 WHEN '1050' THEN 39 WHEN '1051' THEN 44 WHEN '1052' THEN 195 WHEN '1053' THEN 172 WHEN '1054' THEN 59 WHEN '1055' THEN 171 WHEN '1056' THEN 24 WHEN '1057' THEN 16 WHEN '1058' THEN 47 WHEN '1059' THEN 64 WHEN '1060' THEN 67 WHEN '1061' THEN 14 WHEN '1062' THEN 79 WHEN '1063' THEN 148 WHEN '1064' THEN 190 WHEN '1065' THEN 94 WHEN '1066' THEN 114 WHEN '1067' THEN 194 WHEN '1068' THEN 143 WHEN '1069' THEN 73 WHEN '1070' THEN 157 WHEN '1071' THEN 2 WHEN '1072' THEN 183 WHEN '1073' THEN 68 WHEN '1074' THEN 23 WHEN '1075' THEN 42 WHEN '1076' THEN 125 WHEN '1077' THEN 136 WHEN '1078' THEN 112 WHEN '1079' THEN 98 WHEN '1080' THEN 71 WHEN '1081' THEN 122 WHEN '1082' THEN 129 WHEN '1083' THEN 57 WHEN '1084' THEN 186 WHEN '1085' THEN 187 WHEN '1086' THEN 46 WHEN '1087' THEN 177 WHEN '1088' THEN 48 WHEN '1089' THEN 152 WHEN '1090' THEN 199 WHEN '1091' THEN 37 WHEN '1092' THEN 18 WHEN '1093' THEN 99 WHEN '1094' THEN 41 WHEN '1095' THEN 142 WHEN '1096' THEN 130 WHEN '1097' THEN 161 WHEN '1098' THEN 150 WHEN '1099' THEN 140 WHEN '1100' THEN 115 WHEN '1101' THEN 50 WHEN '1102' THEN 87 WHEN '1103' THEN 164 WHEN '1104' THEN 104 WHEN '1105' THEN 89 WHEN '1106' THEN 61 WHEN '1107' THEN 28 WHEN '1108' THEN 22 WHEN '1109' THEN 35 WHEN '1110' THEN 76 WHEN '1111' THEN 181 WHEN '1112' THEN 53 WHEN '1113' THEN 43 WHEN '1114' THEN 4 WHEN '1115' THEN 45 WHEN '1116' THEN 55 WHEN '1117' THEN 60 WHEN '1118' THEN 36 WHEN '1119' THEN 168 WHEN '1120' THEN 54 WHEN '1121' THEN 56 WHEN '1122' THEN 174 WHEN '1123' THEN 8 WHEN '1124' THEN 91 WHEN '1125' THEN 119 WHEN '1126' THEN 169 WHEN '1127' THEN 193 WHEN '1128' THEN 121 WHEN '1129' THEN 118 WHEN '1130' THEN 11 WHEN '1131' THEN 78 WHEN '1132' THEN 189 WHEN '1133' THEN 185 WHEN '1134' THEN 158 WHEN '1135' THEN 101 WHEN '1136' THEN 180 WHEN '1137' THEN 81 WHEN '1138' THEN 15 WHEN '1139' THEN 92 WHEN '1140' THEN 95 WHEN '1141' THEN 113 WHEN '1142' THEN 154 WHEN '1143' THEN 149 WHEN '1144' THEN 184 WHEN '1145' THEN 102 WHEN '1146' THEN 108 WHEN '1147' THEN 131 WHEN '1148' THEN 160 WHEN '1149' THEN 153 WHEN '1150' THEN 200 WHEN '1151' THEN 126 WHEN '1152' THEN 75 WHEN '1153' THEN 109 WHEN '1154' THEN 191 WHEN '1155' THEN 196 WHEN '1156' THEN 65 WHEN '1157' THEN 52 WHEN '1158' THEN 62 WHEN '1159' THEN 51 WHEN '1160' THEN 96 WHEN '1161' THEN 88 WHEN '1162' THEN 74 WHEN '1163' THEN 58 WHEN '1164' THEN 120 WHEN '1165' THEN 137 WHEN '1166' THEN 134 WHEN '1167' THEN 144 WHEN '1168' THEN 167 WHEN '1169' THEN 162 WHEN '1170' THEN 179 WHEN '1171' THEN 132 WHEN '1172' THEN 188 WHEN '1173' THEN 159 WHEN '1174' THEN 69 WHEN '1175' THEN 165 WHEN '1176' THEN 176 WHEN '1177' THEN 93 WHEN '1178' THEN 100 WHEN '1179' THEN 141 WHEN '1180' THEN 107 WHEN '1181' THEN 38 WHEN '1182' THEN 133 WHEN '1183' THEN 26 WHEN '1184' THEN 80 WHEN '1185' THEN 166 WHEN '1186' THEN 192 WHEN '1187' THEN 90 WHEN '1188' THEN 170 WHEN '1189' THEN 27 WHEN '1190' THEN 12 WHEN '1191' THEN 156 WHEN '1192' THEN 30 WHEN '1193' THEN 135 WHEN '1194' THEN 66 WHEN '1195' THEN 3 WHEN '1196' THEN 175 WHEN '1197' THEN 9 WHEN '1198' THEN 147 WHEN '1199' THEN 6 END)",
          "offset": 2212
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_int_hubspot__owner_performance_metrics/cycle_time_rank_peer_order.sql",
      "sql_sha256": "b7e54b4ec0649b4ee14aa02e9b5efe8806693f7c518bc2c9e63a745f4f4d9879",
      "comparison": {
        "levels": [
          {
            "level": "L0",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 0,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 509,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L1",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 0,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 88,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 509,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 198,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 0,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 421,
            "comparison_column_count_including_keys": 32
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 198,
            "column_mismatches": {
              "owner_id": 0,
              "avg_lost_cycle_time": 0,
              "avg_won_cycle_time": 0,
              "avg_won_deal_size": 0,
              "cycle_time_rank": 0,
              "deals_won_rank": 183,
              "development_focus": 0,
              "efficiency_percentile": 0,
              "enterprise_deals": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 74,
              "large_deals": 0,
              "lost_deals": 0,
              "medium_deals": 0,
              "open_deals": 0,
              "overall_performance_score": 0,
              "owner_email": 0,
              "owner_name": 0,
              "performance_tier": 0,
              "pipeline_health_status": 0,
              "pipeline_value": 0,
              "revenue_percentile": 0,
              "revenue_rank": 0,
              "sales_specialization": 0,
              "small_deals": 0,
              "total_deals": 0,
              "total_won_revenue": 0,
              "volume_percentile": 0,
              "win_rate_percentage": 0,
              "win_rate_percentile": 0,
              "win_rate_rank": 164,
              "won_deals": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 421,
            "comparison_column_count_including_keys": 32
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
      "/home/katherine/Assumption_Ledger/data/005_cs_work/impl-010/node_results.duckdb"
    ]
  ],
  "src_alias": "src",
  "gold_alias": "src",
  "retained_alias": "retained",
  "private_copy_tables": [
    "intermediate.int_hubspot__deals_enhanced",
    "intermediate.int_hubspot__owners_enhanced"
  ],
  "retained": {
    "levels": [
      {
        "level": "L0",
        "agent_rows": 200,
        "gold_rows": 200,
        "agent_only_key_rows": 0,
        "gold_only_key_rows": 0,
        "common_key_agent_excess_rows": 0,
        "common_key_gold_excess_rows": 0,
        "common_key_different_rows_or_min_pairs": 199,
        "column_mismatches": {
          "owner_id": 0,
          "avg_lost_cycle_time": 0,
          "avg_won_cycle_time": 0,
          "avg_won_deal_size": 0,
          "cycle_time_rank": 2,
          "deals_won_rank": 183,
          "development_focus": 0,
          "efficiency_percentile": 0,
          "enterprise_deals": 0,
          "enterprise_win_rate": 0,
          "large_deal_win_rate": 74,
          "large_deals": 0,
          "lost_deals": 0,
          "medium_deals": 0,
          "open_deals": 0,
          "overall_performance_score": 88,
          "owner_email": 0,
          "owner_name": 0,
          "performance_tier": 0,
          "pipeline_health_status": 0,
          "pipeline_value": 0,
          "revenue_percentile": 0,
          "revenue_rank": 0,
          "sales_specialization": 0,
          "small_deals": 0,
          "total_deals": 0,
          "total_won_revenue": 0,
          "volume_percentile": 0,
          "win_rate_percentage": 0,
          "win_rate_percentile": 0,
          "win_rate_rank": 164,
          "won_deals": 0
        },
        "key_aware_agent_unmatched": 199,
        "key_aware_gold_unmatched": 199,
        "whole_match": false,
        "row_scale": 199,
        "cell_scale": 511,
        "comparison_column_count_including_keys": 32
      },
      {
        "level": "L1",
        "agent_rows": 200,
        "gold_rows": 200,
        "agent_only_key_rows": 0,
        "gold_only_key_rows": 0,
        "common_key_agent_excess_rows": 0,
        "common_key_gold_excess_rows": 0,
        "common_key_different_rows_or_min_pairs": 199,
        "column_mismatches": {
          "owner_id": 0,
          "avg_lost_cycle_time": 0,
          "avg_won_cycle_time": 0,
          "avg_won_deal_size": 0,
          "cycle_time_rank": 2,
          "deals_won_rank": 183,
          "development_focus": 0,
          "efficiency_percentile": 0,
          "enterprise_deals": 0,
          "enterprise_win_rate": 0,
          "large_deal_win_rate": 74,
          "large_deals": 0,
          "lost_deals": 0,
          "medium_deals": 0,
          "open_deals": 0,
          "overall_performance_score": 88,
          "owner_email": 0,
          "owner_name": 0,
          "performance_tier": 0,
          "pipeline_health_status": 0,
          "pipeline_value": 0,
          "revenue_percentile": 0,
          "revenue_rank": 0,
          "sales_specialization": 0,
          "small_deals": 0,
          "total_deals": 0,
          "total_won_revenue": 0,
          "volume_percentile": 0,
          "win_rate_percentage": 0,
          "win_rate_percentile": 0,
          "win_rate_rank": 164,
          "won_deals": 0
        },
        "key_aware_agent_unmatched": 199,
        "key_aware_gold_unmatched": 199,
        "whole_match": false,
        "row_scale": 199,
        "cell_scale": 511,
        "comparison_column_count_including_keys": 32
      },
      {
        "level": "L2",
        "agent_rows": 200,
        "gold_rows": 200,
        "agent_only_key_rows": 0,
        "gold_only_key_rows": 0,
        "common_key_agent_excess_rows": 0,
        "common_key_gold_excess_rows": 0,
        "common_key_different_rows_or_min_pairs": 198,
        "column_mismatches": {
          "owner_id": 0,
          "avg_lost_cycle_time": 0,
          "avg_won_cycle_time": 0,
          "avg_won_deal_size": 0,
          "cycle_time_rank": 2,
          "deals_won_rank": 183,
          "development_focus": 0,
          "efficiency_percentile": 0,
          "enterprise_deals": 0,
          "enterprise_win_rate": 0,
          "large_deal_win_rate": 74,
          "large_deals": 0,
          "lost_deals": 0,
          "medium_deals": 0,
          "open_deals": 0,
          "overall_performance_score": 0,
          "owner_email": 0,
          "owner_name": 0,
          "performance_tier": 0,
          "pipeline_health_status": 0,
          "pipeline_value": 0,
          "revenue_percentile": 0,
          "revenue_rank": 0,
          "sales_specialization": 0,
          "small_deals": 0,
          "total_deals": 0,
          "total_won_revenue": 0,
          "volume_percentile": 0,
          "win_rate_percentage": 0,
          "win_rate_percentile": 0,
          "win_rate_rank": 164,
          "won_deals": 0
        },
        "key_aware_agent_unmatched": 198,
        "key_aware_gold_unmatched": 198,
        "whole_match": false,
        "row_scale": 198,
        "cell_scale": 423,
        "comparison_column_count_including_keys": 32
      },
      {
        "level": "L3",
        "agent_rows": 200,
        "gold_rows": 200,
        "agent_only_key_rows": 0,
        "gold_only_key_rows": 0,
        "common_key_agent_excess_rows": 0,
        "common_key_gold_excess_rows": 0,
        "common_key_different_rows_or_min_pairs": 198,
        "column_mismatches": {
          "owner_id": 0,
          "avg_lost_cycle_time": 0,
          "avg_won_cycle_time": 0,
          "avg_won_deal_size": 0,
          "cycle_time_rank": 2,
          "deals_won_rank": 183,
          "development_focus": 0,
          "efficiency_percentile": 0,
          "enterprise_deals": 0,
          "enterprise_win_rate": 0,
          "large_deal_win_rate": 74,
          "large_deals": 0,
          "lost_deals": 0,
          "medium_deals": 0,
          "open_deals": 0,
          "overall_performance_score": 0,
          "owner_email": 0,
          "owner_name": 0,
          "performance_tier": 0,
          "pipeline_health_status": 0,
          "pipeline_value": 0,
          "revenue_percentile": 0,
          "revenue_rank": 0,
          "sales_specialization": 0,
          "small_deals": 0,
          "total_deals": 0,
          "total_won_revenue": 0,
          "volume_percentile": 0,
          "win_rate_percentage": 0,
          "win_rate_percentile": 0,
          "win_rate_rank": 164,
          "won_deals": 0
        },
        "key_aware_agent_unmatched": 198,
        "key_aware_gold_unmatched": 198,
        "whole_match": false,
        "row_scale": 198,
        "cell_scale": 423,
        "comparison_column_count_including_keys": 32
      }
    ],
    "first_match": null
  },
  "execution_threads": 1
}
```
</details>

复现：从JSON读取basis/source/clock_control；以只读方式挂载源和gold，在私有库复制private_copy_tables；对原agent SQL先应用共同clock_control，再逐个独立应用runs中的唯一old/new替换；threads固定1，比较沿用scripts/annotate_dacomp_batch016.py的compare_sql及udf_forms。不得向旧021路径写出新结果。
