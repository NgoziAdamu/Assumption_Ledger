# impl-013_int_netsuite2__customer_profitability（039，v3.2校准工作结果）

## 任务

先独立盲标封存，后与036对照；本文件为解盲后的工作结果，不能替代封存件计算一致率。

## 结论

主要原因：**Intent Misreading**；把握：高。
021旧主要原因原样保留：`C`，不作为新类别依据。

## 详细发现

### 判定和规模口径

按038做法，以L0整表行规模优先，行规模并列时比较格子数；评测键计入。单改须从同一基线独立进行，不能相加贡献。L1–L3仅作宽松诊断。

基线：`{"L0": {"row_scale": 2, "cell_scale": 4}, "L1": {"row_scale": 2, "cell_scale": 4}, "L2": {"row_scale": 2, "cell_scale": 4}, "L3": {"row_scale": 2, "cell_scale": 4}}`。

重跑来源：`records/021_reruns_impl-013_int_netsuite2__customer_profitability.json`。原记录中clock_control、source、private_copy_tables和edits提供共同日期、CS/agent-raw来源与准确替换。

### percentile_score

角色：主要；类别：**Intent Misreading**；把握：高。

契约明确要求按 80/60/40/20 百分位的值阈值分档；ntile 按行排名分桶，不能等同。不是数据事实待核实。

前提P/处理选择：ntile(5) 可以实现契约所要求的百分位阈值评分
是否说出：第4档——看到了相关信息，但没有意识到的迹象。finish 65 和交付 SQL 无百分位/ntile 具体或通用说明；日期解析和占位高阶指标声明不适用于本处。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |
|---|---:|---:|---:|---:|
| L0 | 2 | 0 | 4 | 0 |
| L1 | 2 | 0 | 4 | 0 |
| L2 | 2 | 0 | 4 | 0 |
| L3 | 2 | 0 | 4 | 0 |

单改：`records/021_reruns_impl-013_int_netsuite2__customer_profitability.json` / `percentiles`；减少量（L0行、格）：`[2, 4]`。

准确old/new：

```json
[
  {
    "old": "ntile(5) OVER(ORDER BY total_revenue)",
    "new": "CASE WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.8) FROM metrics) THEN 5 WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.6) FROM metrics) THEN 4 WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.4) FROM metrics) THEN 3 WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.2) FROM metrics) THEN 2 ELSE 1 END",
    "offset": 1601
  }
]
```

引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `1.args.content` / process：

```text
revenue_score: 5 for total_revenue at or above the 80th percentile; 4 at or above the 60th; 3 at or above the 40th; 2 at or above the 20th; otherwise 1.
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/19.json` / `19.args.command` / process：

```text
ntile(5) OVER(ORDER BY total_revenue) revenue_score
```

- `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_profitability.sql` / `SQL.text` / delivered_code：

```text
ntile(5) OVER(ORDER BY total_revenue)
```

### clv_denominator

角色：非原因；类别：**Unstated Choice**；把握：中。

契约说net_profit per month，未指明用active_months还是customer_lifetime_months作分母；差异取决于未定的选择。单改结果仍2行4格，不是本表判错原因。

前提P/处理选择：月均利润按有交易的活跃月数计算
是否说出：第4档——看到了相关信息，但没有意识到的迹象。finish65未说明本处；初始event1完整提供相关业务说明，故第4档；没有比较两种分母或点出歧义，不能第3档。036第5档与本次原文回查结果不同。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |
|---|---:|---:|---:|---:|
| L0 | 2 | 2 | 4 | 4 |
| L1 | 2 | 2 | 4 | 4 |
| L2 | 2 | 2 | 4 | 4 |
| L3 | 2 | 2 | 4 | 4 |

单改：`records/016_reruns_impl-013.json` / `clv_month_denominator`；减少量（L0行、格）：`[0, 0]`。

标记：存在未确立的前提，但不是判错原因。

准确old/new：

```json
[
  {
    "old": "net_profit/nullif(active_months,0)*greatest(12,1.2*coalesce(customer_lifetime_months,1))",
    "new": "CASE WHEN customer_lifetime_months>0 AND active_months>0 THEN net_profit/customer_lifetime_months*greatest(12,1.2*customer_lifetime_months) ELSE net_profit END",
    "offset": 3419
  }
]
```

引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `1.args.content` / process：

```text
predicted_clv: if customer_lifetime_months and active_months are both greater than 0, multiply net_profit per month by the larger of 12 months and 1.2 times customer_lifetime_months; otherwise use net_profit.
```

- `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/19.json` / `19.args.command` / process：

```text
net_profit/nullif(active_months,0)*greatest(12,1.2*coalesce(customer_lifetime_months,1)) predicted_clv
```

- `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_profitability.sql` / `SQL.text` / delivered_code：

```text
net_profit/nullif(active_months,0)*greatest(12,1.2*coalesce(customer_lifetime_months,1))
```

## 证据来源

- 契约/SQL材料包：`records/013_packages/013_impl-013_intermediate_int_netsuite2__customer_profitability.md`。
- 原始契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_profitability.sql`。
- 原始交付报告及SQL注释清单：`records/039_checks/delivery_sources.json`。
- 核实查询复用（保守计入失败共2条，不超过5）：`records/021_calibration_queries.json#impl-013`。
- 盲标封存、解盲差异：`records/039_calibration_blind_sealed.json`、`records/039_calibration_comparison.json`。

## 不确定或没查到的（含规则问题）

- 盲标漏掉既有CLV分母非原因候选，解盲后补录。盲标一致率不包含补录结果。

## 建议的下一步

由用户与Claude复核校准中的规则读法和轨迹证据差异；第二阶段继续同一会话的40张正式表，不重新盲标、不改封存件。
