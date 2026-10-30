# impl-010 / hubspot__sales_rep_performance（全量，更正A）

## 结论

主要原因：**O**；把握：高；标记：无。

并列排名仅在契约允许的数据库隐式peer顺序上不同。volume_rank单处对齐按行/格净改善最大，主因O。large/medium/small_revenue三处无本类Won时，FILTER求和为NULL、gold CASE ELSE 0为0；契约未明确这一空分类口径，分别归A参与因素。

主要原因位置：volume_rank_peer_order（行减少1，格减少178）。

参与因素：A：large_revenue（行减少1，格减少74）；A：medium_revenue（行减少0，格减少108）；A：small_revenue（行减少0，格减少171）；O：efficiency_rank_peer_order（行减少0，格减少4）；O：win_rate_rank_projection（行减少0，格减少164）。

不确定性四档：**看到了但没提**（针对主要原因）。

## 更正范围与CS口径

撤回021原“不可评估”。按手册v2第1、7节，本表只读intermediate上游，全部从gold复制；raw版本差异不传播为本节点不可评估。021原始raw诊断仍保留为历史事实，但不作为本表排除依据。官方待标注/判错状态不重定。

本次仅更正这份逐表记录；旧021汇总CSV、统计、重跑JSON和其他表不改。更正清单见[025报告](../../notes/025_2026-10-30_收尾A更正清单.md)。

## 差异与归因依据

实际schema：sales；评测键：owner_id。按键与原评测列并集比较，不删除评测键。

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml`；相关行：1804、1848–1874、1894–1905。完整契约摘录见[021材料包](../021_packages/021_impl-010_hubspot__sales_rep_performance.md)。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_rep_performance.sql`；SHA-256 `ab6365e72caaf455ecfe91dd2f6bf33c7b5b7a3caa49f2d9b978ecaa34ab59e2`。
- gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/sql/sales/hubspot__sales_rep_performance.sql`；SHA-256 `cd57395fef292c5beab654d5710db45a90cadb0c845524201a1d88e5080b6288`。

volume_rank单改消除180格该列差异，另一个允许顺序的efficiency_rank由4格变为6格，净减178格。win_rate_rank原最终投影选到gold上游同名列，本节点新算列被DuckDB命名为win_rate_rank_1；改最终投影净减164格。两种排名的排序键及peer排名多重集均相同，差异仍属于允许顺序O，不因同名遮蔽推断为I。

各改动都是一个唯一出现的SQL位置，准确old/new、offset及其余字节不变的哈希证据见末尾机器记录。同做法出现在不同表达式时分别修改、分别计数；零改善/变差候选不列参与因素。

## agent可见证据与不确定性

event 1的message含完整契约，路径：`/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/1.json`。
原字段字符偏移116957起摘录：

```text
Ties in ranks are resolved by the database’s implicit peer order. - Join rankings to trends and territory by owner_id (cast trend/territory owner_id to VARCHAR); unmatched trend/territory values remain NULL. - Derivations: - revenue_trend_percentage: if prior_6m_avg_revenue > 0 and recent_6m_avg_revenue is not NULL, compute 100 × (recent - prior) / prior; else NULL. - win_rate_trend_points: if prior_6m_avg_win_rate > 0 and recent_6m_avg_win_rate
```

复查impl-010全部75个事件：event21/27写入模型，event49/50比对字段和行数，event63/64列模型及部分行数；没有对本表主要排名顺序或分类标签作说明，也没有核验这些差异。event73最终报告只列完成模型、执行/字段检查及其他输入清洗注意事项。工作清单不计“只有通用策略说明”；报告关于原始缺失属性/关联缺失的一般描述不说明这里的排名或标签选择。

本表主因不确定性因此由原“没有迹象（不知gold raw版本）”改为“看到了但没提（已看到契约要求，未讨论本表差异）”。不把agent不能访问gold当作未见自己契约。

最终报告事件：`/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/73.json`。历史完整轨迹索引仍见`records/021_trace_audit.json`。

## 查询与诊断

核实查询0条；代价档：需要查业务说明。类别由契约/代码直接判断，不虚构P或agent可见核实查询。下列允许读gold的诊断不计入5条核实额度；原件均READ_ONLY，诊断与重跑仅写data/025_closure私有库。

### win_rate_rank_tie_multisets
```sql
WITH a AS (SELECT win_rate_percentage k,list(win_rate_rank ORDER BY win_rate_rank) ranks FROM baseline GROUP BY 1),g AS (SELECT win_rate_percentage k,list(win_rate_rank ORDER BY win_rate_rank) ranks FROM gold.sales.hubspot__sales_rep_performance GROUP BY 1) SELECT count(*) group_count,count(*) FILTER(WHERE a.ranks IS DISTINCT FROM g.ranks) bad_groups FROM a FULL JOIN g ON a.k IS NOT DISTINCT FROM g.k
```
```json
{"columns": ["group_count", "bad_groups"], "rows": [[1, 0]]}
```

### volume_rank_tie_multisets
```sql
WITH a AS (SELECT won_deals k,list(volume_rank ORDER BY volume_rank) ranks FROM baseline GROUP BY 1),g AS (SELECT won_deals k,list(volume_rank ORDER BY volume_rank) ranks FROM gold.sales.hubspot__sales_rep_performance GROUP BY 1) SELECT count(*) group_count,count(*) FILTER(WHERE a.ranks IS DISTINCT FROM g.ranks) bad_groups FROM a FULL JOIN g ON a.k IS NOT DISTINCT FROM g.k
```
```json
{"columns": ["group_count", "bad_groups"], "rows": [[17, 0]]}
```

### efficiency_rank_tie_multisets
```sql
WITH a AS (SELECT coalesce(avg_won_cycle_time,999) k,list(efficiency_rank ORDER BY efficiency_rank) ranks FROM baseline GROUP BY 1),g AS (SELECT coalesce(avg_won_cycle_time,999) k,list(efficiency_rank ORDER BY efficiency_rank) ranks FROM gold.sales.hubspot__sales_rep_performance GROUP BY 1) SELECT count(*) group_count,count(*) FILTER(WHERE a.ranks IS DISTINCT FROM g.ranks) bad_groups FROM a FULL JOIN g ON a.k IS NOT DISTINCT FROM g.k
```
```json
{"columns": ["group_count", "bad_groups"], "rows": [[195, 0]]}
```

### large_revenue_difference
```sql
SELECT cast(a.large_revenue as varchar) agent_value,cast(g.large_revenue as varchar) gold_value,count(*) n FROM baseline a JOIN gold.sales.hubspot__sales_rep_performance g USING(owner_id) WHERE cast(a.large_revenue as varchar) IS DISTINCT FROM cast(g.large_revenue as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [[null, "0.00", 74]]}
```

### medium_revenue_difference
```sql
SELECT cast(a.medium_revenue as varchar) agent_value,cast(g.medium_revenue as varchar) gold_value,count(*) n FROM baseline a JOIN gold.sales.hubspot__sales_rep_performance g USING(owner_id) WHERE cast(a.medium_revenue as varchar) IS DISTINCT FROM cast(g.medium_revenue as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [[null, "0.00", 108]]}
```

### small_revenue_difference
```sql
SELECT cast(a.small_revenue as varchar) agent_value,cast(g.small_revenue as varchar) gold_value,count(*) n FROM baseline a JOIN gold.sales.hubspot__sales_rep_performance g USING(owner_id) WHERE cast(a.small_revenue as varchar) IS DISTINCT FROM cast(g.small_revenue as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [[null, "0.00", 171]]}
```

### win_rate_rank_difference
```sql
SELECT cast(a.win_rate_rank as varchar) agent_value,cast(g.win_rate_rank as varchar) gold_value,count(*) n FROM baseline a JOIN gold.sales.hubspot__sales_rep_performance g USING(owner_id) WHERE cast(a.win_rate_rank as varchar) IS DISTINCT FROM cast(g.win_rate_rank as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [["100", "182", 1], ["101", "183", 1], ["102", "184", 1], ["103", "185", 1], ["104", "186", 1]]}
```

### volume_rank_difference
```sql
SELECT cast(a.volume_rank as varchar) agent_value,cast(g.volume_rank as varchar) gold_value,count(*) n FROM baseline a JOIN gold.sales.hubspot__sales_rep_performance g USING(owner_id) WHERE cast(a.volume_rank as varchar) IS DISTINCT FROM cast(g.volume_rank as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [["100", "95", 1], ["101", "85", 1], ["102", "84", 1], ["103", "81", 1], ["104", "96", 1]]}
```

### efficiency_rank_difference
```sql
SELECT cast(a.efficiency_rank as varchar) agent_value,cast(g.efficiency_rank as varchar) gold_value,count(*) n FROM baseline a JOIN gold.sales.hubspot__sales_rep_performance g USING(owner_id) WHERE cast(a.efficiency_rank as varchar) IS DISTINCT FROM cast(g.efficiency_rank as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [["184", "185", 1], ["185", "184", 1], ["48", "49", 1], ["49", "48", 1]]}
```

### activity_consistency_difference
```sql
SELECT cast(a.activity_consistency as varchar) agent_value,cast(g.activity_consistency as varchar) gold_value,count(*) n FROM baseline a JOIN gold.sales.hubspot__sales_rep_performance g USING(owner_id) WHERE cast(a.activity_consistency as varchar) IS DISTINCT FROM cast(g.activity_consistency as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [["0.33210558207753577", "0.3321055820775357", 1], ["0.4972451580988469", "0.49724515809884684", 1], ["0.5135525910130954", "0.5135525910130955", 1], ["0.6020797289396149", "0.6020797289396147", 1], ["0.6191391873668904", "0.6191391873668902", 1]]}
```

### revenue_volatility_difference
```sql
SELECT cast(a.revenue_volatility as varchar) agent_value,cast(g.revenue_volatility as varchar) gold_value,count(*) n FROM baseline a JOIN gold.sales.hubspot__sales_rep_performance g USING(owner_id) WHERE cast(a.revenue_volatility as varchar) IS DISTINCT FROM cast(g.revenue_volatility as varchar) GROUP BY 1,2 ORDER BY n DESC,1 LIMIT 5
```
```json
{"columns": ["agent_value", "gold_value", "n"], "rows": [["112282.64199470227", "112282.64199470228", 1], ["113371.46779642814", "113371.46779642813", 1], ["127159.77185144377", "127159.77185144374", 1], ["127891.55581079556", "127891.55581079557", 1], ["128481.26857301523", "128481.26857301522", 1]]}
```

辅助诊断：排除已定位列`win_rate_rank,volume_rank,efficiency_rank,activity_consistency,revenue_volatility,large_revenue,medium_revenue,small_revenue`后，其余内容首次整表匹配为L0。此排除仅确认剩余差异范围，不进入主要原因排序。排名每个排序键组内rank多重集相同的查询单独列出。

## 时间控制、单点重跑与规模

复用021留存/基线记录核对源、时钟和SQL；新增干预统一使用threads=1和2025-10-13固定日期。源数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`；私有复制上游：`intermediate.int_hubspot__deal_performance_metrics, intermediate.int_hubspot__owner_performance_metrics`。所有减量对新增同控制基线计算；旧基线仅并列展示。

|记录|L0行/格|L1行/格|L2行/格|L3行/格|整表首次匹配|
|---|---:|---:|---:|---:|---|
|021留存|200/850|200/850|200/701|200/701|均未匹配|
|021原基线|200/865|200/865|200/701|200/701|均未匹配|
|baseline|200/862|200/862|200/701|200/701|均未匹配|
|enterprise_revenue|200/862|200/862|200/701|200/701|均未匹配|
|large_revenue|199/788|199/788|199/627|199/627|均未匹配|
|medium_revenue|200/754|200/754|199/593|199/593|均未匹配|
|small_revenue|200/691|200/691|200/530|200/530|均未匹配|
|activity_consistency|200/862|200/862|200/701|200/701|均未匹配|
|revenue_volatility|200/862|200/862|200/701|200/701|均未匹配|
|recent_month_window|200/862|200/862|200/701|200/701|均未匹配|
|win_rate_rank_peer_order|200/862|200/862|200/701|200/701|均未匹配|
|volume_rank_peer_order|199/684|199/684|198/523|198/523|均未匹配|
|efficiency_rank_peer_order|200/858|200/858|200/697|200/697|均未匹配|
|win_rate_rank_projection|200/698|200/698|199/537|199/537|均未匹配|

|单处修改|类别|行减少|格减少|角色|
|---|---|---:|---:|---|
|enterprise_revenue|A|0|0|不计因素|
|large_revenue|A|1|74|参与因素|
|medium_revenue|A|0|108|参与因素|
|small_revenue|A|0|171|参与因素|
|activity_consistency|O|0|0|不计因素|
|revenue_volatility|O|0|0|不计因素|
|recent_month_window|O|0|0|不计因素|
|win_rate_rank_peer_order|O|0|0|不计因素|
|volume_rank_peer_order|O|1|178|主因|
|efficiency_rank_peer_order|O|0|4|参与因素|
|win_rate_rank_projection|O|0|164|参与因素|

**enterprise_revenue**：契约只说分类内won金额求和，未规定无该类won时NULL或0；gold CASE ELSE 0。

**large_revenue**：契约只说分类内won金额求和，未规定无该类won时NULL或0；gold CASE ELSE 0。

**medium_revenue**：契约只说分类内won金额求和，未规定无该类won时NULL或0；gold CASE ELSE 0。

**small_revenue**：契约只说分类内won金额求和，未规定无该类won时NULL或0；gold CASE ELSE 0。

**activity_consistency**：使用gold的STDDEV别名（与STDDEV_SAMP同义），检验表达形式是否有实际贡献；原差异L2消失。

**revenue_volatility**：使用gold的STDDEV别名（与STDDEV_SAMP同义），检验表达形式是否有实际贡献；原差异L2消失。

**recent_month_window**：agent按最近3个日历月，gold使用-3含当前共4个月；诊断有无实际贡献。

**win_rate_rank_peer_order**：诊断：仅在原排序键相同的peer内选用gold留存序号作为确定顺序；跨组排序不变。该CASE仅用于允许并列顺序的定位，不是生产修复，也不用于U证据。

**volume_rank_peer_order**：诊断：仅在原排序键相同的peer内选用gold留存序号作为确定顺序；跨组排序不变。该CASE仅用于允许并列顺序的定位，不是生产修复，也不用于U证据。

**efficiency_rank_peer_order**：诊断：仅在原排序键相同的peer内选用gold留存序号作为确定顺序；跨组排序不变。该CASE仅用于允许并列顺序的定位，不是生产修复，也不用于U证据。

**win_rate_rank_projection**：最终SELECT选择本节点重新计算的win_rate_rank_1；原名指向上游同名排名。两者仅允许的并列顺序不同，诊断已验证每个peer排名多重集相同，不据此判I。

### 各档每列差异（共同键；本批均无独有/超额行）

|执行|档位|每列非零不一致数|
|---|---|---|
|baseline|L0|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|baseline|L1|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|baseline|L2|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|baseline|L3|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|enterprise_revenue|L0|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|enterprise_revenue|L1|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|enterprise_revenue|L2|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|enterprise_revenue|L3|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|large_revenue|L0|`{"medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|large_revenue|L1|`{"medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|large_revenue|L2|`{"medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|large_revenue|L3|`{"medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|medium_revenue|L0|`{"large_revenue": 74, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|medium_revenue|L1|`{"large_revenue": 74, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|medium_revenue|L2|`{"large_revenue": 74, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|medium_revenue|L3|`{"large_revenue": 74, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|small_revenue|L0|`{"large_revenue": 74, "medium_revenue": 108, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|small_revenue|L1|`{"large_revenue": 74, "medium_revenue": 108, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|small_revenue|L2|`{"large_revenue": 74, "medium_revenue": 108, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|small_revenue|L3|`{"large_revenue": 74, "medium_revenue": 108, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|activity_consistency|L0|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|activity_consistency|L1|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|activity_consistency|L2|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|activity_consistency|L3|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|revenue_volatility|L0|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|revenue_volatility|L1|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|revenue_volatility|L2|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|revenue_volatility|L3|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|recent_month_window|L0|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|recent_month_window|L1|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|recent_month_window|L2|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|recent_month_window|L3|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|win_rate_rank_peer_order|L0|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|win_rate_rank_peer_order|L1|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|win_rate_rank_peer_order|L2|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|win_rate_rank_peer_order|L3|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "efficiency_rank": 4}`|
|volume_rank_peer_order|L0|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "efficiency_rank": 6, "activity_consistency": 80, "revenue_volatility": 81}`|
|volume_rank_peer_order|L1|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "efficiency_rank": 6, "activity_consistency": 80, "revenue_volatility": 81}`|
|volume_rank_peer_order|L2|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "efficiency_rank": 6}`|
|volume_rank_peer_order|L3|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "efficiency_rank": 6}`|
|efficiency_rank_peer_order|L0|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "activity_consistency": 80, "revenue_volatility": 81}`|
|efficiency_rank_peer_order|L1|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180, "activity_consistency": 80, "revenue_volatility": 81}`|
|efficiency_rank_peer_order|L2|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180}`|
|efficiency_rank_peer_order|L3|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "win_rate_rank": 164, "volume_rank": 180}`|
|win_rate_rank_projection|L0|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|win_rate_rank_projection|L1|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "volume_rank": 180, "efficiency_rank": 4, "activity_consistency": 80, "revenue_volatility": 81}`|
|win_rate_rank_projection|L2|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "volume_rank": 180, "efficiency_rank": 4}`|
|win_rate_rank_projection|L3|`{"large_revenue": 74, "medium_revenue": 108, "small_revenue": 171, "volume_rank": 180, "efficiency_rank": 4}`|

## 规则问题

三处分类收入契约只要求sum won deal_amount within each named category，未指定该分类没有Won时返回NULL还是0；列说明还写有“NULL if no territory data joined”，但没有说明已关联到territory、只是该分类没有Won的情况；一种读法隐含此时应0，另一种读法允许FILTER SUM的NULL。数据能展示两种SQL效果，不能替代这一业务选择，按第9节选择A。排名O采用与owner表相同的单窗口peer对齐诊断。STDDEV_SAMP与gold STDDEV同义，末位差异L2消失；并行时末位会波动，新增重跑统一threads=1，所有减量仅对本轮同控制基线计算。

没有改动手册定义。使用gold排序作为诊断的目的只是在契约允许的peer顺序内使比较条件一致；它不证明agent需要知道gold，也不构成U的单改证据。

## 完整机器证据及复现

旧记录：`records/021_reruns_impl-010_hubspot__sales_rep_performance.json`（未修改）。下列JSON是本次新增单点重跑的完整结果，随本逐表记录交付，未另行更新汇总。

<details><summary>共同控制、原/新片段、位置、私有SQL路径及L0–L3完整计数</summary>

<!-- correction-A-rerun-json -->
```json
{
  "started_utc": "2026-10-30T11:04:07.135376+00:00",
  "task": "impl-010",
  "basis": {
    "kind": "original_007_009",
    "record": "records/009_tolerance_tables.jsonl",
    "detail_record": "/home/katherine/Assumption_Ledger/records/009_cs_impl-010.json",
    "prediction_database": "/home/katherine/Assumption_Ledger/data/009_cs_work/impl-010/node_results.duckdb",
    "gold_database": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb",
    "actual_schema": "sales",
    "table": "hubspot__sales_rep_performance",
    "candidate_date": null,
    "comparison_columns": [
      "owner_id",
      "owner_name",
      "owner_email",
      "total_deals",
      "won_deals",
      "total_won_revenue",
      "win_rate_percentage",
      "avg_won_cycle_time",
      "current_pipeline_value",
      "enterprise_win_rate",
      "large_deal_win_rate",
      "enterprise_revenue",
      "large_revenue",
      "medium_revenue",
      "small_revenue",
      "revenue_rank",
      "win_rate_rank",
      "volume_rank",
      "efficiency_rank",
      "revenue_percentile",
      "win_rate_percentile",
      "volume_percentile",
      "efficiency_percentile",
      "overall_performance_score",
      "performance_tier",
      "sales_specialization",
      "development_focus",
      "pipeline_health_status",
      "primary_deal_segment",
      "segments_covered",
      "activity_level",
      "activity_consistency",
      "recent_active_months",
      "performance_trend",
      "revenue_trend_percentage",
      "win_rate_trend_points",
      "revenue_volatility"
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
        "column": "current_pipeline_value",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
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
        "column": "volume_rank",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 180,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 180,
        "pred_unmatched_value_occurrences": 180,
        "gold_unmatched_value_occurrences": 180,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "efficiency_rank",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 4,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 4,
        "pred_unmatched_value_occurrences": 4,
        "gold_unmatched_value_occurrences": 4,
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
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "revenue_volatility",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 75,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 75,
        "pred_unmatched_value_occurrences": 75,
        "gold_unmatched_value_occurrences": 75,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "activity_consistency",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 74,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 74,
        "pred_unmatched_value_occurrences": 74,
        "gold_unmatched_value_occurrences": 74,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "recent_active_months",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "primary_deal_segment",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "segments_covered",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "enterprise_revenue",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "large_revenue",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 74,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 74,
        "pred_unmatched_value_occurrences": 74,
        "gold_unmatched_value_occurrences": 74,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "medium_revenue",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 108,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 108,
        "pred_unmatched_value_occurrences": 108,
        "gold_unmatched_value_occurrences": 108,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "small_revenue",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 171,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 171,
        "pred_unmatched_value_occurrences": 171,
        "gold_unmatched_value_occurrences": 171,
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
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "revenue_trend_percentage",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "win_rate_trend_points",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
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
        "column": "performance_trend",
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
        "column": "activity_level",
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
        "column": "won_deals",
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
        "column": "current_pipeline_value",
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
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "enterprise_revenue",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "large_revenue",
        "one_to_one_mismatch_rows": 74,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 74,
        "pred_unmatched_value_occurrences": 74,
        "gold_unmatched_value_occurrences": 74,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "medium_revenue",
        "one_to_one_mismatch_rows": 108,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 108,
        "pred_unmatched_value_occurrences": 108,
        "gold_unmatched_value_occurrences": 108,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "small_revenue",
        "one_to_one_mismatch_rows": 171,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 171,
        "pred_unmatched_value_occurrences": 171,
        "gold_unmatched_value_occurrences": 171,
        "marginal_multisets_equal": false,
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
        "column": "volume_rank",
        "one_to_one_mismatch_rows": 180,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 180,
        "pred_unmatched_value_occurrences": 180,
        "gold_unmatched_value_occurrences": 180,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "efficiency_rank",
        "one_to_one_mismatch_rows": 4,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 4,
        "pred_unmatched_value_occurrences": 4,
        "gold_unmatched_value_occurrences": 4,
        "marginal_multisets_equal": false,
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
        "column": "primary_deal_segment",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "segments_covered",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "activity_level",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "activity_consistency",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "recent_active_months",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "performance_trend",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "revenue_trend_percentage",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "win_rate_trend_points",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      {
        "column": "revenue_volatility",
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
    "selection_reason": "该表 gold 日期未能验证，沿用原差异",
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
        "column": "current_pipeline_value",
        "l0_counts_verbatim": {
          "column": "current_pipeline_value",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "current_pipeline_value",
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
            "agent_value": "168",
            "gold_value": "86"
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
            "agent_value": "171",
            "gold_value": "89"
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
            "agent_value": "176",
            "gold_value": "94"
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
            "agent_value": "142",
            "gold_value": "60"
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
            "agent_value": "44",
            "gold_value": "126"
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
        "column": "volume_rank",
        "l0_counts_verbatim": {
          "column": "volume_rank",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 180,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 180,
          "pred_unmatched_value_occurrences": 180,
          "gold_unmatched_value_occurrences": 180,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "volume_rank",
          "one_to_one_mismatch_rows": 180,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 180,
          "pred_unmatched_value_occurrences": 180,
          "gold_unmatched_value_occurrences": 180,
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
            "gold_value": "108"
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
            "gold_value": "109"
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
            "gold_value": "84"
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
            "gold_value": "120"
          }
        ],
        "sample_counts_recheck": {
          "mismatch_rows_or_minimum_pairs": 180,
          "pred_unmatched_value_occurrences": 180,
          "gold_unmatched_value_occurrences": 180
        },
        "agent_actual_type": "BIGINT",
        "gold_actual_type": "BIGINT"
      },
      {
        "column": "efficiency_rank",
        "l0_counts_verbatim": {
          "column": "efficiency_rank",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 4,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 4,
          "pred_unmatched_value_occurrences": 4,
          "gold_unmatched_value_occurrences": 4,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "efficiency_rank",
          "one_to_one_mismatch_rows": 4,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 4,
          "pred_unmatched_value_occurrences": 4,
          "gold_unmatched_value_occurrences": 4,
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
          },
          {
            "key_normalized": {
              "owner_id": "1133"
            },
            "agent_key_raw_text": {
              "owner_id": "1133"
            },
            "gold_key_raw_text": {
              "owner_id": "1133"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "185",
            "gold_value": "184"
          },
          {
            "key_normalized": {
              "owner_id": "1144"
            },
            "agent_key_raw_text": {
              "owner_id": "1144"
            },
            "gold_key_raw_text": {
              "owner_id": "1144"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "184",
            "gold_value": "185"
          }
        ],
        "sample_counts_recheck": {
          "mismatch_rows_or_minimum_pairs": 4,
          "pred_unmatched_value_occurrences": 4,
          "gold_unmatched_value_occurrences": 4
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
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
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
        "sample_key_groups": [],
        "sample_counts_recheck": null,
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "revenue_volatility",
        "l0_counts_verbatim": {
          "column": "revenue_volatility",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 75,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 75,
          "pred_unmatched_value_occurrences": 75,
          "gold_unmatched_value_occurrences": 75,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "revenue_volatility",
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
            "agent_value": "172510.35865790994",
            "gold_value": "172510.3586579099"
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
            "agent_value": "203348.2401182509",
            "gold_value": "203348.24011825086"
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
            "agent_value": "338113.048183792",
            "gold_value": "338113.04818379204"
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
            "agent_value": "218198.88822283776",
            "gold_value": "218198.8882228378"
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
            "agent_value": "203107.04923300716",
            "gold_value": "203107.04923300722"
          }
        ],
        "sample_counts_recheck": {
          "mismatch_rows_or_minimum_pairs": 75,
          "pred_unmatched_value_occurrences": 75,
          "gold_unmatched_value_occurrences": 75
        },
        "agent_actual_type": "DOUBLE",
        "gold_actual_type": "DOUBLE"
      },
      {
        "column": "activity_consistency",
        "l0_counts_verbatim": {
          "column": "activity_consistency",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 74,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 74,
          "pred_unmatched_value_occurrences": 74,
          "gold_unmatched_value_occurrences": 74,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "activity_consistency",
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
            "agent_value": "0.8819171036881969",
            "gold_value": "0.8819171036881968"
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
            "agent_value": "0.806225774829855",
            "gold_value": "0.8062257748298549"
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
            "agent_value": "1.1281521496355325",
            "gold_value": "1.1281521496355322"
          },
          {
            "key_normalized": {
              "owner_id": "1015"
            },
            "agent_key_raw_text": {
              "owner_id": "1015"
            },
            "gold_key_raw_text": {
              "owner_id": "1015"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "0.7859052479933758",
            "gold_value": "0.7859052479933757"
          },
          {
            "key_normalized": {
              "owner_id": "1021"
            },
            "agent_key_raw_text": {
              "owner_id": "1021"
            },
            "gold_key_raw_text": {
              "owner_id": "1021"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": "0.8264420947336313",
            "gold_value": "0.8264420947336314"
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
        "column": "recent_active_months",
        "l0_counts_verbatim": {
          "column": "recent_active_months",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "recent_active_months",
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
        "column": "primary_deal_segment",
        "l0_counts_verbatim": {
          "column": "primary_deal_segment",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "primary_deal_segment",
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
        "column": "segments_covered",
        "l0_counts_verbatim": {
          "column": "segments_covered",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "segments_covered",
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
        "column": "enterprise_revenue",
        "l0_counts_verbatim": {
          "column": "enterprise_revenue",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "enterprise_revenue",
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
        "column": "large_revenue",
        "l0_counts_verbatim": {
          "column": "large_revenue",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 74,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 74,
          "pred_unmatched_value_occurrences": 74,
          "gold_unmatched_value_occurrences": 74,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "large_revenue",
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
            "gold_value": "0.00"
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
            "gold_value": "0.00"
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
            "gold_value": "0.00"
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
            "gold_value": "0.00"
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
            "gold_value": "0.00"
          }
        ],
        "sample_counts_recheck": {
          "mismatch_rows_or_minimum_pairs": 74,
          "pred_unmatched_value_occurrences": 74,
          "gold_unmatched_value_occurrences": 74
        },
        "agent_actual_type": "DECIMAL(38,2)",
        "gold_actual_type": "DECIMAL(38,2)"
      },
      {
        "column": "medium_revenue",
        "l0_counts_verbatim": {
          "column": "medium_revenue",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 108,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 108,
          "pred_unmatched_value_occurrences": 108,
          "gold_unmatched_value_occurrences": 108,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "medium_revenue",
          "one_to_one_mismatch_rows": 108,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 108,
          "pred_unmatched_value_occurrences": 108,
          "gold_unmatched_value_occurrences": 108,
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
            "agent_value": null,
            "gold_value": "0.00"
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
            "agent_value": null,
            "gold_value": "0.00"
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
            "agent_value": null,
            "gold_value": "0.00"
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
            "gold_value": "0.00"
          },
          {
            "key_normalized": {
              "owner_id": "1009"
            },
            "agent_key_raw_text": {
              "owner_id": "1009"
            },
            "gold_key_raw_text": {
              "owner_id": "1009"
            },
            "agent_rows_with_key": 1,
            "gold_rows_with_key": 1,
            "kind": "one_to_one",
            "agent_value": null,
            "gold_value": "0.00"
          }
        ],
        "sample_counts_recheck": {
          "mismatch_rows_or_minimum_pairs": 108,
          "pred_unmatched_value_occurrences": 108,
          "gold_unmatched_value_occurrences": 108
        },
        "agent_actual_type": "DECIMAL(38,2)",
        "gold_actual_type": "DECIMAL(38,2)"
      },
      {
        "column": "small_revenue",
        "l0_counts_verbatim": {
          "column": "small_revenue",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 171,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 171,
          "pred_unmatched_value_occurrences": 171,
          "gold_unmatched_value_occurrences": 171,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "small_revenue",
          "one_to_one_mismatch_rows": 171,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 171,
          "pred_unmatched_value_occurrences": 171,
          "gold_unmatched_value_occurrences": 171,
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
            "gold_value": "0.00"
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
            "agent_value": null,
            "gold_value": "0.00"
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
            "agent_value": null,
            "gold_value": "0.00"
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
            "gold_value": "0.00"
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
            "gold_value": "0.00"
          }
        ],
        "sample_counts_recheck": {
          "mismatch_rows_or_minimum_pairs": 171,
          "pred_unmatched_value_occurrences": 171,
          "gold_unmatched_value_occurrences": 171
        },
        "agent_actual_type": "DECIMAL(38,2)",
        "gold_actual_type": "DECIMAL(38,2)"
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
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "large_deal_win_rate",
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
        "column": "revenue_trend_percentage",
        "l0_counts_verbatim": {
          "column": "revenue_trend_percentage",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "revenue_trend_percentage",
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
        "column": "win_rate_trend_points",
        "l0_counts_verbatim": {
          "column": "win_rate_trend_points",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "win_rate_trend_points",
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
        "column": "performance_trend",
        "l0_counts_verbatim": {
          "column": "performance_trend",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "performance_trend",
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
        "column": "activity_level",
        "l0_counts_verbatim": {
          "column": "activity_level",
          "included_in_official_comparison": true,
          "one_to_one_mismatch_rows": 0,
          "nonunique_key_minimum_value_mismatch_pairs": 0,
          "mismatch_rows_or_minimum_pairs": 0,
          "pred_unmatched_value_occurrences": 0,
          "gold_unmatched_value_occurrences": 0,
          "count_semantics": "exact_one_to_one_rows"
        },
        "l3_counts_verbatim": {
          "column": "activity_level",
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
      "count": 14
    }
  ],
  "runs": [
    {
      "label": "baseline",
      "edits": [],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_rep_performance/baseline.sql",
      "sql_sha256": "6204b5e3228eb54d3df71cc88bdbc8a4aef4184047f1c14dc698b9be4283c0f3",
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 862,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 862,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 701,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 701,
            "comparison_column_count_including_keys": 37
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "enterprise_revenue",
      "edits": [
        {
          "old": "sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Enterprise (100K+)')",
          "new": "sum(case when deal_status='Won' and deal_size_category='Enterprise (100K+)' then deal_amount else 0 end)",
          "offset": 1893
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_rep_performance/enterprise_revenue.sql",
      "sql_sha256": "87ee16be614600ec104f5cb21518f116cfcbb43326c7f2da5d8a5d6ad30a6b51",
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 862,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 862,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 701,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 701,
            "comparison_column_count_including_keys": 37
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "large_revenue",
      "edits": [
        {
          "old": "sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Large (50K-100K)')",
          "new": "sum(case when deal_status='Won' and deal_size_category='Large (50K-100K)' then deal_amount else 0 end)",
          "offset": 2005
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_rep_performance/large_revenue.sql",
      "sql_sha256": "6042c53ea0a3e3d54071a05192de74609e38d32726da10ff3bbc9377975d8df5",
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 0,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 788,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 0,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 788,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 0,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 627,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 0,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 627,
            "comparison_column_count_including_keys": 37
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "medium_revenue",
      "edits": [
        {
          "old": "sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Medium (10K-50K)')",
          "new": "sum(case when deal_status='Won' and deal_size_category='Medium (10K-50K)' then deal_amount else 0 end)",
          "offset": 2110
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_rep_performance/medium_revenue.sql",
      "sql_sha256": "223a8d85979a8b40b0f97fa059b6ae79d469e10198ba744df888018e8d6fc088",
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 0,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 754,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 0,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 754,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 0,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 593,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 0,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 593,
            "comparison_column_count_including_keys": 37
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "small_revenue",
      "edits": [
        {
          "old": "sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Small (<10K)')",
          "new": "sum(case when deal_status='Won' and deal_size_category='Small (<10K)' then deal_amount else 0 end)",
          "offset": 2216
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_rep_performance/small_revenue.sql",
      "sql_sha256": "d796ce2a4687e5ec3c51f01df986272701807c8ba82a9257f9c096e59643ddf4",
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 0,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 691,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 0,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 691,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 0,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 530,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 0,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 530,
            "comparison_column_count_including_keys": 37
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "activity_consistency",
      "edits": [
        {
          "old": "stddev_samp(monthly_deals_created)",
          "new": "stddev(monthly_deals_created)",
          "offset": 1546
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_rep_performance/activity_consistency.sql",
      "sql_sha256": "0a452bfd98368b729355152ff3c45699a3f8a2949d5c8bd970be5ee0c8916457",
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 862,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 862,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 701,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 701,
            "comparison_column_count_including_keys": 37
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "revenue_volatility",
      "edits": [
        {
          "old": "stddev_samp(monthly_revenue)",
          "new": "stddev(monthly_revenue)",
          "offset": 1498
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_rep_performance/revenue_volatility.sql",
      "sql_sha256": "150753f8dee4736c813d1c308c177d6aa7f35ab916a5cd14491d992ce9c92d82",
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 862,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 862,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 701,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 701,
            "comparison_column_count_including_keys": 37
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "recent_month_window",
      "edits": [
        {
          "old": "month(DATE '2025-10-13')-2",
          "new": "month(DATE '2025-10-13')-3",
          "offset": 1664
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_rep_performance/recent_month_window.sql",
      "sql_sha256": "7aa67839d28269f3d1454cd0504bb49e1d03f7f560eee02c1d5253912dd113df",
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 862,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 862,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 701,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 701,
            "comparison_column_count_including_keys": 37
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "win_rate_rank_peer_order",
      "edits": [
        {
          "old": "row_number() over(order by win_rate_percentage desc)",
          "new": "row_number() over(order by win_rate_percentage desc, CASE owner_id WHEN '1000' THEN 86 WHEN '1001' THEN 89 WHEN '1002' THEN 94 WHEN '1003' THEN 28 WHEN '1004' THEN 60 WHEN '1005' THEN 126 WHEN '1006' THEN 62 WHEN '1007' THEN 83 WHEN '1008' THEN 142 WHEN '1009' THEN 66 WHEN '1010' THEN 14 WHEN '1011' THEN 42 WHEN '1012' THEN 120 WHEN '1013' THEN 61 WHEN '1014' THEN 175 WHEN '1015' THEN 141 WHEN '1016' THEN 69 WHEN '1017' THEN 81 WHEN '1018' THEN 75 WHEN '1019' THEN 156 WHEN '1020' THEN 105 WHEN '1021' THEN 3 WHEN '1022' THEN 122 WHEN '1023' THEN 78 WHEN '1024' THEN 33 WHEN '1025' THEN 189 WHEN '1026' THEN 177 WHEN '1027' THEN 125 WHEN '1028' THEN 166 WHEN '1029' THEN 77 WHEN '1030' THEN 181 WHEN '1031' THEN 20 WHEN '1032' THEN 117 WHEN '1033' THEN 164 WHEN '1034' THEN 92 WHEN '1035' THEN 139 WHEN '1036' THEN 151 WHEN '1037' THEN 129 WHEN '1038' THEN 103 WHEN '1039' THEN 1 WHEN '1040' THEN 29 WHEN '1041' THEN 41 WHEN '1042' THEN 159 WHEN '1043' THEN 17 WHEN '1044' THEN 8 WHEN '1045' THEN 98 WHEN '1046' THEN 25 WHEN '1047' THEN 31 WHEN '1048' THEN 114 WHEN '1049' THEN 163 WHEN '1050' THEN 200 WHEN '1051' THEN 32 WHEN '1052' THEN 97 WHEN '1053' THEN 188 WHEN '1054' THEN 191 WHEN '1055' THEN 109 WHEN '1056' THEN 58 WHEN '1057' THEN 16 WHEN '1058' THEN 150 WHEN '1059' THEN 59 WHEN '1060' THEN 172 WHEN '1061' THEN 113 WHEN '1062' THEN 19 WHEN '1063' THEN 12 WHEN '1064' THEN 178 WHEN '1065' THEN 22 WHEN '1066' THEN 112 WHEN '1067' THEN 146 WHEN '1068' THEN 45 WHEN '1069' THEN 153 WHEN '1070' THEN 43 WHEN '1071' THEN 195 WHEN '1072' THEN 2 WHEN '1073' THEN 88 WHEN '1074' THEN 52 WHEN '1075' THEN 145 WHEN '1076' THEN 91 WHEN '1077' THEN 11 WHEN '1078' THEN 48 WHEN '1079' THEN 90 WHEN '1080' THEN 196 WHEN '1081' THEN 182 WHEN '1082' THEN 174 WHEN '1083' THEN 87 WHEN '1084' THEN 160 WHEN '1085' THEN 26 WHEN '1086' THEN 124 WHEN '1087' THEN 30 WHEN '1088' THEN 85 WHEN '1089' THEN 168 WHEN '1090' THEN 187 WHEN '1091' THEN 76 WHEN '1092' THEN 149 WHEN '1093' THEN 73 WHEN '1094' THEN 115 WHEN '1095' THEN 128 WHEN '1096' THEN 93 WHEN '1097' THEN 10 WHEN '1098' THEN 131 WHEN '1099' THEN 65 WHEN '1100' THEN 64 WHEN '1101' THEN 38 WHEN '1102' THEN 27 WHEN '1103' THEN 119 WHEN '1104' THEN 132 WHEN '1105' THEN 39 WHEN '1106' THEN 72 WHEN '1107' THEN 136 WHEN '1108' THEN 194 WHEN '1109' THEN 35 WHEN '1110' THEN 134 WHEN '1111' THEN 56 WHEN '1112' THEN 9 WHEN '1113' THEN 173 WHEN '1114' THEN 171 WHEN '1115' THEN 107 WHEN '1116' THEN 96 WHEN '1117' THEN 127 WHEN '1118' THEN 179 WHEN '1119' THEN 84 WHEN '1120' THEN 133 WHEN '1121' THEN 36 WHEN '1122' THEN 5 WHEN '1123' THEN 176 WHEN '1124' THEN 53 WHEN '1125' THEN 162 WHEN '1126' THEN 101 WHEN '1127' THEN 37 WHEN '1128' THEN 102 WHEN '1129' THEN 104 WHEN '1130' THEN 50 WHEN '1131' THEN 180 WHEN '1132' THEN 167 WHEN '1133' THEN 111 WHEN '1134' THEN 55 WHEN '1135' THEN 197 WHEN '1136' THEN 23 WHEN '1137' THEN 70 WHEN '1138' THEN 21 WHEN '1139' THEN 99 WHEN '1140' THEN 100 WHEN '1141' THEN 71 WHEN '1142' THEN 192 WHEN '1143' THEN 170 WHEN '1144' THEN 169 WHEN '1145' THEN 46 WHEN '1146' THEN 110 WHEN '1147' THEN 123 WHEN '1148' THEN 121 WHEN '1149' THEN 157 WHEN '1150' THEN 186 WHEN '1151' THEN 13 WHEN '1152' THEN 155 WHEN '1153' THEN 79 WHEN '1154' THEN 138 WHEN '1155' THEN 185 WHEN '1156' THEN 148 WHEN '1157' THEN 80 WHEN '1158' THEN 106 WHEN '1159' THEN 137 WHEN '1160' THEN 199 WHEN '1161' THEN 15 WHEN '1162' THEN 143 WHEN '1163' THEN 140 WHEN '1164' THEN 165 WHEN '1165' THEN 68 WHEN '1166' THEN 7 WHEN '1167' THEN 4 WHEN '1168' THEN 34 WHEN '1169' THEN 135 WHEN '1170' THEN 152 WHEN '1171' THEN 193 WHEN '1172' THEN 130 WHEN '1173' THEN 74 WHEN '1174' THEN 144 WHEN '1175' THEN 24 WHEN '1176' THEN 154 WHEN '1177' THEN 67 WHEN '1178' THEN 82 WHEN '1179' THEN 161 WHEN '1180' THEN 116 WHEN '1181' THEN 44 WHEN '1182' THEN 47 WHEN '1183' THEN 40 WHEN '1184' THEN 95 WHEN '1185' THEN 18 WHEN '1186' THEN 108 WHEN '1187' THEN 6 WHEN '1188' THEN 51 WHEN '1189' THEN 183 WHEN '1190' THEN 57 WHEN '1191' THEN 49 WHEN '1192' THEN 158 WHEN '1193' THEN 147 WHEN '1194' THEN 118 WHEN '1195' THEN 198 WHEN '1196' THEN 63 WHEN '1197' THEN 190 WHEN '1198' THEN 54 WHEN '1199' THEN 184 END)",
          "offset": 2420
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_rep_performance/win_rate_rank_peer_order.sql",
      "sql_sha256": "5573c1f370da54785630ad5f7f2190c3f5d59430ef9ae0b1ffe0f332d51319b4",
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 862,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 862,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 701,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 701,
            "comparison_column_count_including_keys": 37
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "volume_rank_peer_order",
      "edits": [
        {
          "old": "row_number() over(order by won_deals desc)",
          "new": "row_number() over(order by won_deals desc, CASE owner_id WHEN '1000' THEN 108 WHEN '1001' THEN 109 WHEN '1002' THEN 60 WHEN '1003' THEN 33 WHEN '1004' THEN 84 WHEN '1005' THEN 120 WHEN '1006' THEN 69 WHEN '1007' THEN 90 WHEN '1008' THEN 140 WHEN '1009' THEN 86 WHEN '1010' THEN 21 WHEN '1011' THEN 9 WHEN '1012' THEN 153 WHEN '1013' THEN 55 WHEN '1014' THEN 173 WHEN '1015' THEN 155 WHEN '1016' THEN 70 WHEN '1017' THEN 76 WHEN '1018' THEN 107 WHEN '1019' THEN 182 WHEN '1020' THEN 132 WHEN '1021' THEN 2 WHEN '1022' THEN 100 WHEN '1023' THEN 73 WHEN '1024' THEN 17 WHEN '1025' THEN 198 WHEN '1026' THEN 194 WHEN '1027' THEN 61 WHEN '1028' THEN 146 WHEN '1029' THEN 58 WHEN '1030' THEN 175 WHEN '1031' THEN 44 WHEN '1032' THEN 98 WHEN '1033' THEN 192 WHEN '1034' THEN 111 WHEN '1035' THEN 123 WHEN '1036' THEN 105 WHEN '1037' THEN 80 WHEN '1038' THEN 150 WHEN '1039' THEN 1 WHEN '1040' THEN 47 WHEN '1041' THEN 50 WHEN '1042' THEN 42 WHEN '1043' THEN 22 WHEN '1044' THEN 27 WHEN '1045' THEN 94 WHEN '1046' THEN 16 WHEN '1047' THEN 35 WHEN '1048' THEN 115 WHEN '1049' THEN 144 WHEN '1050' THEN 200 WHEN '1051' THEN 23 WHEN '1052' THEN 130 WHEN '1053' THEN 187 WHEN '1054' THEN 179 WHEN '1055' THEN 151 WHEN '1056' THEN 54 WHEN '1057' THEN 32 WHEN '1058' THEN 167 WHEN '1059' THEN 68 WHEN '1060' THEN 148 WHEN '1061' THEN 133 WHEN '1062' THEN 14 WHEN '1063' THEN 30 WHEN '1064' THEN 174 WHEN '1065' THEN 15 WHEN '1066' THEN 114 WHEN '1067' THEN 166 WHEN '1068' THEN 26 WHEN '1069' THEN 168 WHEN '1070' THEN 51 WHEN '1071' THEN 197 WHEN '1072' THEN 11 WHEN '1073' THEN 92 WHEN '1074' THEN 52 WHEN '1075' THEN 157 WHEN '1076' THEN 41 WHEN '1077' THEN 20 WHEN '1078' THEN 38 WHEN '1079' THEN 110 WHEN '1080' THEN 181 WHEN '1081' THEN 184 WHEN '1082' THEN 149 WHEN '1083' THEN 91 WHEN '1084' THEN 160 WHEN '1085' THEN 45 WHEN '1086' THEN 119 WHEN '1087' THEN 34 WHEN '1088' THEN 40 WHEN '1089' THEN 147 WHEN '1090' THEN 186 WHEN '1091' THEN 127 WHEN '1092' THEN 125 WHEN '1093' THEN 72 WHEN '1094' THEN 134 WHEN '1095' THEN 137 WHEN '1096' THEN 128 WHEN '1097' THEN 29 WHEN '1098' THEN 102 WHEN '1099' THEN 56 WHEN '1100' THEN 18 WHEN '1101' THEN 24 WHEN '1102' THEN 46 WHEN '1103' THEN 99 WHEN '1104' THEN 121 WHEN '1105' THEN 36 WHEN '1106' THEN 10 WHEN '1107' THEN 154 WHEN '1108' THEN 189 WHEN '1109' THEN 48 WHEN '1110' THEN 122 WHEN '1111' THEN 67 WHEN '1112' THEN 28 WHEN '1113' THEN 163 WHEN '1114' THEN 193 WHEN '1115' THEN 77 WHEN '1116' THEN 129 WHEN '1117' THEN 136 WHEN '1118' THEN 183 WHEN '1119' THEN 59 WHEN '1120' THEN 103 WHEN '1121' THEN 49 WHEN '1122' THEN 3 WHEN '1123' THEN 164 WHEN '1124' THEN 82 WHEN '1125' THEN 171 WHEN '1126' THEN 95 WHEN '1127' THEN 63 WHEN '1128' THEN 113 WHEN '1129' THEN 96 WHEN '1130' THEN 66 WHEN '1131' THEN 195 WHEN '1132' THEN 172 WHEN '1133' THEN 152 WHEN '1134' THEN 53 WHEN '1135' THEN 190 WHEN '1136' THEN 7 WHEN '1137' THEN 88 WHEN '1138' THEN 6 WHEN '1139' THEN 131 WHEN '1140' THEN 112 WHEN '1141' THEN 71 WHEN '1142' THEN 188 WHEN '1143' THEN 162 WHEN '1144' THEN 161 WHEN '1145' THEN 64 WHEN '1146' THEN 79 WHEN '1147' THEN 118 WHEN '1148' THEN 135 WHEN '1149' THEN 143 WHEN '1150' THEN 185 WHEN '1151' THEN 31 WHEN '1152' THEN 170 WHEN '1153' THEN 74 WHEN '1154' THEN 139 WHEN '1155' THEN 178 WHEN '1156' THEN 124 WHEN '1157' THEN 75 WHEN '1158' THEN 97 WHEN '1159' THEN 104 WHEN '1160' THEN 191 WHEN '1161' THEN 13 WHEN '1162' THEN 141 WHEN '1163' THEN 165 WHEN '1164' THEN 145 WHEN '1165' THEN 87 WHEN '1166' THEN 4 WHEN '1167' THEN 12 WHEN '1168' THEN 62 WHEN '1169' THEN 138 WHEN '1170' THEN 158 WHEN '1171' THEN 180 WHEN '1172' THEN 101 WHEN '1173' THEN 19 WHEN '1174' THEN 156 WHEN '1175' THEN 8 WHEN '1176' THEN 169 WHEN '1177' THEN 57 WHEN '1178' THEN 89 WHEN '1179' THEN 126 WHEN '1180' THEN 116 WHEN '1181' THEN 81 WHEN '1182' THEN 37 WHEN '1183' THEN 25 WHEN '1184' THEN 93 WHEN '1185' THEN 5 WHEN '1186' THEN 78 WHEN '1187' THEN 43 WHEN '1188' THEN 39 WHEN '1189' THEN 176 WHEN '1190' THEN 106 WHEN '1191' THEN 65 WHEN '1192' THEN 159 WHEN '1193' THEN 142 WHEN '1194' THEN 117 WHEN '1195' THEN 199 WHEN '1196' THEN 85 WHEN '1197' THEN 196 WHEN '1198' THEN 83 WHEN '1199' THEN 177 END)",
          "offset": 2487
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_rep_performance/volume_rank_peer_order.sql",
      "sql_sha256": "00173742e18deffa101b0a2e5179d9804c89eda7ce8c1998c2909a79bd11a045",
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 0,
              "efficiency_rank": 6,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 684,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 0,
              "efficiency_rank": 6,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 684,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 0,
              "efficiency_rank": 6,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 523,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 0,
              "efficiency_rank": 6,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 198,
            "key_aware_gold_unmatched": 198,
            "whole_match": false,
            "row_scale": 198,
            "cell_scale": 523,
            "comparison_column_count_including_keys": 37
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "efficiency_rank_peer_order",
      "edits": [
        {
          "old": "row_number() over(order by coalesce(avg_won_cycle_time,999))",
          "new": "row_number() over(order by coalesce(avg_won_cycle_time,999), CASE owner_id WHEN '1000' THEN 182 WHEN '1001' THEN 49 WHEN '1002' THEN 146 WHEN '1003' THEN 123 WHEN '1004' THEN 17 WHEN '1005' THEN 127 WHEN '1006' THEN 117 WHEN '1007' THEN 139 WHEN '1008' THEN 63 WHEN '1009' THEN 21 WHEN '1010' THEN 105 WHEN '1011' THEN 40 WHEN '1012' THEN 128 WHEN '1013' THEN 116 WHEN '1014' THEN 111 WHEN '1015' THEN 1 WHEN '1016' THEN 86 WHEN '1017' THEN 33 WHEN '1018' THEN 77 WHEN '1019' THEN 72 WHEN '1020' THEN 85 WHEN '1021' THEN 145 WHEN '1022' THEN 29 WHEN '1023' THEN 10 WHEN '1024' THEN 84 WHEN '1025' THEN 151 WHEN '1026' THEN 7 WHEN '1027' THEN 83 WHEN '1028' THEN 173 WHEN '1029' THEN 178 WHEN '1030' THEN 19 WHEN '1031' THEN 97 WHEN '1032' THEN 82 WHEN '1033' THEN 198 WHEN '1034' THEN 34 WHEN '1035' THEN 5 WHEN '1036' THEN 25 WHEN '1037' THEN 70 WHEN '1038' THEN 31 WHEN '1039' THEN 138 WHEN '1040' THEN 32 WHEN '1041' THEN 103 WHEN '1042' THEN 20 WHEN '1043' THEN 163 WHEN '1044' THEN 110 WHEN '1045' THEN 13 WHEN '1046' THEN 124 WHEN '1047' THEN 106 WHEN '1048' THEN 155 WHEN '1049' THEN 197 WHEN '1050' THEN 39 WHEN '1051' THEN 44 WHEN '1052' THEN 195 WHEN '1053' THEN 172 WHEN '1054' THEN 59 WHEN '1055' THEN 171 WHEN '1056' THEN 24 WHEN '1057' THEN 16 WHEN '1058' THEN 47 WHEN '1059' THEN 64 WHEN '1060' THEN 67 WHEN '1061' THEN 14 WHEN '1062' THEN 79 WHEN '1063' THEN 148 WHEN '1064' THEN 190 WHEN '1065' THEN 94 WHEN '1066' THEN 114 WHEN '1067' THEN 194 WHEN '1068' THEN 143 WHEN '1069' THEN 73 WHEN '1070' THEN 157 WHEN '1071' THEN 2 WHEN '1072' THEN 183 WHEN '1073' THEN 68 WHEN '1074' THEN 23 WHEN '1075' THEN 42 WHEN '1076' THEN 125 WHEN '1077' THEN 136 WHEN '1078' THEN 112 WHEN '1079' THEN 98 WHEN '1080' THEN 71 WHEN '1081' THEN 122 WHEN '1082' THEN 129 WHEN '1083' THEN 57 WHEN '1084' THEN 186 WHEN '1085' THEN 187 WHEN '1086' THEN 46 WHEN '1087' THEN 177 WHEN '1088' THEN 48 WHEN '1089' THEN 152 WHEN '1090' THEN 199 WHEN '1091' THEN 37 WHEN '1092' THEN 18 WHEN '1093' THEN 99 WHEN '1094' THEN 41 WHEN '1095' THEN 142 WHEN '1096' THEN 130 WHEN '1097' THEN 161 WHEN '1098' THEN 150 WHEN '1099' THEN 140 WHEN '1100' THEN 115 WHEN '1101' THEN 50 WHEN '1102' THEN 87 WHEN '1103' THEN 164 WHEN '1104' THEN 104 WHEN '1105' THEN 89 WHEN '1106' THEN 61 WHEN '1107' THEN 28 WHEN '1108' THEN 22 WHEN '1109' THEN 35 WHEN '1110' THEN 76 WHEN '1111' THEN 181 WHEN '1112' THEN 53 WHEN '1113' THEN 43 WHEN '1114' THEN 4 WHEN '1115' THEN 45 WHEN '1116' THEN 55 WHEN '1117' THEN 60 WHEN '1118' THEN 36 WHEN '1119' THEN 168 WHEN '1120' THEN 54 WHEN '1121' THEN 56 WHEN '1122' THEN 174 WHEN '1123' THEN 8 WHEN '1124' THEN 91 WHEN '1125' THEN 119 WHEN '1126' THEN 169 WHEN '1127' THEN 193 WHEN '1128' THEN 121 WHEN '1129' THEN 118 WHEN '1130' THEN 11 WHEN '1131' THEN 78 WHEN '1132' THEN 189 WHEN '1133' THEN 184 WHEN '1134' THEN 158 WHEN '1135' THEN 101 WHEN '1136' THEN 180 WHEN '1137' THEN 81 WHEN '1138' THEN 15 WHEN '1139' THEN 92 WHEN '1140' THEN 95 WHEN '1141' THEN 113 WHEN '1142' THEN 154 WHEN '1143' THEN 149 WHEN '1144' THEN 185 WHEN '1145' THEN 102 WHEN '1146' THEN 108 WHEN '1147' THEN 131 WHEN '1148' THEN 160 WHEN '1149' THEN 153 WHEN '1150' THEN 200 WHEN '1151' THEN 126 WHEN '1152' THEN 75 WHEN '1153' THEN 109 WHEN '1154' THEN 191 WHEN '1155' THEN 196 WHEN '1156' THEN 65 WHEN '1157' THEN 52 WHEN '1158' THEN 62 WHEN '1159' THEN 51 WHEN '1160' THEN 96 WHEN '1161' THEN 88 WHEN '1162' THEN 74 WHEN '1163' THEN 58 WHEN '1164' THEN 120 WHEN '1165' THEN 137 WHEN '1166' THEN 134 WHEN '1167' THEN 144 WHEN '1168' THEN 167 WHEN '1169' THEN 162 WHEN '1170' THEN 179 WHEN '1171' THEN 132 WHEN '1172' THEN 188 WHEN '1173' THEN 159 WHEN '1174' THEN 69 WHEN '1175' THEN 165 WHEN '1176' THEN 176 WHEN '1177' THEN 93 WHEN '1178' THEN 100 WHEN '1179' THEN 141 WHEN '1180' THEN 107 WHEN '1181' THEN 38 WHEN '1182' THEN 133 WHEN '1183' THEN 26 WHEN '1184' THEN 80 WHEN '1185' THEN 166 WHEN '1186' THEN 192 WHEN '1187' THEN 90 WHEN '1188' THEN 170 WHEN '1189' THEN 27 WHEN '1190' THEN 12 WHEN '1191' THEN 156 WHEN '1192' THEN 30 WHEN '1193' THEN 135 WHEN '1194' THEN 66 WHEN '1195' THEN 3 WHEN '1196' THEN 175 WHEN '1197' THEN 9 WHEN '1198' THEN 147 WHEN '1199' THEN 6 END)",
          "offset": 2542
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_rep_performance/efficiency_rank_peer_order.sql",
      "sql_sha256": "433f86a2e12ae21f1589a718e731f1ade424010db14637e9352c09cff30232ea",
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 0,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 858,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 0,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 858,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 0,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 697,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 200,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 164,
              "volume_rank": 180,
              "efficiency_rank": 0,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 697,
            "comparison_column_count_including_keys": 37
          }
        ],
        "first_match": null
      }
    },
    {
      "label": "win_rate_rank_projection",
      "edits": [
        {
          "old": "revenue_rank,win_rate_rank,volume_rank,efficiency_rank,",
          "new": "revenue_rank,win_rate_rank_1 AS win_rate_rank,volume_rank,efficiency_rank,",
          "offset": 4064
        }
      ],
      "sql_path": "data/025_closure/work/impl-010_hubspot__sales_rep_performance/win_rate_rank_projection.sql",
      "sql_sha256": "7b688ee62ff38c5a5d67d66eba6e4dc7bdcfd6a4a58d6b20639295bca134d8aa",
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 0,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 698,
            "comparison_column_count_including_keys": 37
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
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 0,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 80,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 81
            },
            "key_aware_agent_unmatched": 200,
            "key_aware_gold_unmatched": 200,
            "whole_match": false,
            "row_scale": 200,
            "cell_scale": 698,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L2",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 0,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 537,
            "comparison_column_count_including_keys": 37
          },
          {
            "level": "L3",
            "agent_rows": 200,
            "gold_rows": 200,
            "agent_only_key_rows": 0,
            "gold_only_key_rows": 0,
            "common_key_agent_excess_rows": 0,
            "common_key_gold_excess_rows": 0,
            "common_key_different_rows_or_min_pairs": 199,
            "column_mismatches": {
              "owner_id": 0,
              "owner_name": 0,
              "owner_email": 0,
              "total_deals": 0,
              "won_deals": 0,
              "total_won_revenue": 0,
              "win_rate_percentage": 0,
              "avg_won_cycle_time": 0,
              "current_pipeline_value": 0,
              "enterprise_win_rate": 0,
              "large_deal_win_rate": 0,
              "enterprise_revenue": 0,
              "large_revenue": 74,
              "medium_revenue": 108,
              "small_revenue": 171,
              "revenue_rank": 0,
              "win_rate_rank": 0,
              "volume_rank": 180,
              "efficiency_rank": 4,
              "revenue_percentile": 0,
              "win_rate_percentile": 0,
              "volume_percentile": 0,
              "efficiency_percentile": 0,
              "overall_performance_score": 0,
              "performance_tier": 0,
              "sales_specialization": 0,
              "development_focus": 0,
              "pipeline_health_status": 0,
              "primary_deal_segment": 0,
              "segments_covered": 0,
              "activity_level": 0,
              "activity_consistency": 0,
              "recent_active_months": 0,
              "performance_trend": 0,
              "revenue_trend_percentage": 0,
              "win_rate_trend_points": 0,
              "revenue_volatility": 0
            },
            "key_aware_agent_unmatched": 199,
            "key_aware_gold_unmatched": 199,
            "whole_match": false,
            "row_scale": 199,
            "cell_scale": 537,
            "comparison_column_count_including_keys": 37
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
    "intermediate.int_hubspot__deal_performance_metrics",
    "intermediate.int_hubspot__owner_performance_metrics"
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
        "common_key_different_rows_or_min_pairs": 200,
        "column_mismatches": {
          "owner_id": 0,
          "owner_name": 0,
          "owner_email": 0,
          "total_deals": 0,
          "won_deals": 0,
          "total_won_revenue": 0,
          "win_rate_percentage": 0,
          "avg_won_cycle_time": 0,
          "current_pipeline_value": 0,
          "enterprise_win_rate": 0,
          "large_deal_win_rate": 0,
          "enterprise_revenue": 0,
          "large_revenue": 74,
          "medium_revenue": 108,
          "small_revenue": 171,
          "revenue_rank": 0,
          "win_rate_rank": 164,
          "volume_rank": 180,
          "efficiency_rank": 4,
          "revenue_percentile": 0,
          "win_rate_percentile": 0,
          "volume_percentile": 0,
          "efficiency_percentile": 0,
          "overall_performance_score": 0,
          "performance_tier": 0,
          "sales_specialization": 0,
          "development_focus": 0,
          "pipeline_health_status": 0,
          "primary_deal_segment": 0,
          "segments_covered": 0,
          "activity_level": 0,
          "activity_consistency": 74,
          "recent_active_months": 0,
          "performance_trend": 0,
          "revenue_trend_percentage": 0,
          "win_rate_trend_points": 0,
          "revenue_volatility": 75
        },
        "key_aware_agent_unmatched": 200,
        "key_aware_gold_unmatched": 200,
        "whole_match": false,
        "row_scale": 200,
        "cell_scale": 850,
        "comparison_column_count_including_keys": 37
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
          "owner_name": 0,
          "owner_email": 0,
          "total_deals": 0,
          "won_deals": 0,
          "total_won_revenue": 0,
          "win_rate_percentage": 0,
          "avg_won_cycle_time": 0,
          "current_pipeline_value": 0,
          "enterprise_win_rate": 0,
          "large_deal_win_rate": 0,
          "enterprise_revenue": 0,
          "large_revenue": 74,
          "medium_revenue": 108,
          "small_revenue": 171,
          "revenue_rank": 0,
          "win_rate_rank": 164,
          "volume_rank": 180,
          "efficiency_rank": 4,
          "revenue_percentile": 0,
          "win_rate_percentile": 0,
          "volume_percentile": 0,
          "efficiency_percentile": 0,
          "overall_performance_score": 0,
          "performance_tier": 0,
          "sales_specialization": 0,
          "development_focus": 0,
          "pipeline_health_status": 0,
          "primary_deal_segment": 0,
          "segments_covered": 0,
          "activity_level": 0,
          "activity_consistency": 74,
          "recent_active_months": 0,
          "performance_trend": 0,
          "revenue_trend_percentage": 0,
          "win_rate_trend_points": 0,
          "revenue_volatility": 75
        },
        "key_aware_agent_unmatched": 200,
        "key_aware_gold_unmatched": 200,
        "whole_match": false,
        "row_scale": 200,
        "cell_scale": 850,
        "comparison_column_count_including_keys": 37
      },
      {
        "level": "L2",
        "agent_rows": 200,
        "gold_rows": 200,
        "agent_only_key_rows": 0,
        "gold_only_key_rows": 0,
        "common_key_agent_excess_rows": 0,
        "common_key_gold_excess_rows": 0,
        "common_key_different_rows_or_min_pairs": 200,
        "column_mismatches": {
          "owner_id": 0,
          "owner_name": 0,
          "owner_email": 0,
          "total_deals": 0,
          "won_deals": 0,
          "total_won_revenue": 0,
          "win_rate_percentage": 0,
          "avg_won_cycle_time": 0,
          "current_pipeline_value": 0,
          "enterprise_win_rate": 0,
          "large_deal_win_rate": 0,
          "enterprise_revenue": 0,
          "large_revenue": 74,
          "medium_revenue": 108,
          "small_revenue": 171,
          "revenue_rank": 0,
          "win_rate_rank": 164,
          "volume_rank": 180,
          "efficiency_rank": 4,
          "revenue_percentile": 0,
          "win_rate_percentile": 0,
          "volume_percentile": 0,
          "efficiency_percentile": 0,
          "overall_performance_score": 0,
          "performance_tier": 0,
          "sales_specialization": 0,
          "development_focus": 0,
          "pipeline_health_status": 0,
          "primary_deal_segment": 0,
          "segments_covered": 0,
          "activity_level": 0,
          "activity_consistency": 0,
          "recent_active_months": 0,
          "performance_trend": 0,
          "revenue_trend_percentage": 0,
          "win_rate_trend_points": 0,
          "revenue_volatility": 0
        },
        "key_aware_agent_unmatched": 200,
        "key_aware_gold_unmatched": 200,
        "whole_match": false,
        "row_scale": 200,
        "cell_scale": 701,
        "comparison_column_count_including_keys": 37
      },
      {
        "level": "L3",
        "agent_rows": 200,
        "gold_rows": 200,
        "agent_only_key_rows": 0,
        "gold_only_key_rows": 0,
        "common_key_agent_excess_rows": 0,
        "common_key_gold_excess_rows": 0,
        "common_key_different_rows_or_min_pairs": 200,
        "column_mismatches": {
          "owner_id": 0,
          "owner_name": 0,
          "owner_email": 0,
          "total_deals": 0,
          "won_deals": 0,
          "total_won_revenue": 0,
          "win_rate_percentage": 0,
          "avg_won_cycle_time": 0,
          "current_pipeline_value": 0,
          "enterprise_win_rate": 0,
          "large_deal_win_rate": 0,
          "enterprise_revenue": 0,
          "large_revenue": 74,
          "medium_revenue": 108,
          "small_revenue": 171,
          "revenue_rank": 0,
          "win_rate_rank": 164,
          "volume_rank": 180,
          "efficiency_rank": 4,
          "revenue_percentile": 0,
          "win_rate_percentile": 0,
          "volume_percentile": 0,
          "efficiency_percentile": 0,
          "overall_performance_score": 0,
          "performance_tier": 0,
          "sales_specialization": 0,
          "development_focus": 0,
          "pipeline_health_status": 0,
          "primary_deal_segment": 0,
          "segments_covered": 0,
          "activity_level": 0,
          "activity_consistency": 0,
          "recent_active_months": 0,
          "performance_trend": 0,
          "revenue_trend_percentage": 0,
          "win_rate_trend_points": 0,
          "revenue_volatility": 0
        },
        "key_aware_agent_unmatched": 200,
        "key_aware_gold_unmatched": 200,
        "whole_match": false,
        "row_scale": 200,
        "cell_scale": 701,
        "comparison_column_count_including_keys": 37
      }
    ],
    "first_match": null
  },
  "execution_threads": 1
}
```
</details>

复现：从JSON读取basis/source/clock_control；以只读方式挂载源和gold，在私有库复制private_copy_tables；对原agent SQL先应用共同clock_control，再逐个独立应用runs中的唯一old/new替换；threads固定1，比较沿用scripts/annotate_dacomp_batch016.py的compare_sql及udf_forms。不得向旧021路径写出新结果。
