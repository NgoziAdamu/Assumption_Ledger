# impl-006_ad_reporting__predictive_analytics（038 正式表）

主要原因：**已说出的降级**；把握：中。020定稿旧主要原因：`D`，仅原样保留。

## 范围与材料

- 层：marts。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[4040, 4139]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__predictive_analytics.sql`。

- 对比执行输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### 首源投影/整表NULL替代模型（同类缺口组）

- 类别：已说出的降级；角色：主要；把握：中。

- 是否说出：第1档（交付物里针对本处说明了）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

要求平台月度汇总、滚动趋势、预测/风险/建议和6个月筛选；31个字段全NULL逐行读取统一指标源，不是预测分析。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> business_logic: '- Build the baseline from unified campaign metrics limited to the last 12 months. - Group by platform and the calendar month of date_day; compute monthly totals (spend, impressions, clicks, conversions, 30-day revenue) and monthly averages (CTR rounded to 4 decimals, CPC rounded to 2, ROAS rounded to 4); all aggregations ignore NULLs. - Count distinct campaigns: active (all), new (lifecycle LAUNCH), and established (lifecycle ESTABLISHED); NULL campaign IDs are excluded. - Compute volatility as the standard deviation of CTR and CPC within each platform-month; if fewer than two non-NULL observations, volatility is NULL. - Per platform, order months chronologically to derive: - Month-over-month spend growth: percent change from the prior month (rounded to 2 decimals); if the prior value is not positive, set to 0. - Month-over-month CTR change: percent change from the prior month (rounded to 2 decimals); if the prior value is not positive, set to 0. - 3-month rolling averages for spend, CTR, and ROAS using the current month and two preceding months. - Spend momentum: ACCELERATING if current spend is >10% above prior month, DECELERATING if >10% below, otherwise STABLE; if no prior month, STABLE. - CTR momentum: IMPROVING if current CTR is >5% above prior month, DECLINING if >5% below, otherwise STABLE; if no prior month, STABLE. - Predictions: - Next-month spend: 3-month spend average scaled by 1.15 when accelerating, 0.85 when decelerating, otherwise unchanged. - Next-month CTR: 3-month CTR average scaled by 1.10 when improving, 0.90 when declining, otherwise unchanged. - Risk level: HIGH_RISK when CTR volatility > 0.5 and MoM spend growth > 50%; MEDIUM_RISK when CTR volatility > 0.3 or absolute MoM spend growth > 25%; otherwise LOW_RISK. - Anomaly probability: 35 when CTR volatility > 1.0 or CPC volatility > 2.0; 20 when CTR volatility > 0.5 or CPC volatility > 1.0; 25 when absolute MoM spend growth > 50%; otherwise 10. - Confidence: HIGH_CONFIDENCE when absolute MoM spend growth < 10% and CTR volatility < 0.3; MEDIUM_CONFIDENCE when absolute MoM spend growth < 25% and CTR volatility < 0.5; otherwise LOW_CONFIDENCE. - Final output per platform-month: - Baselines: current_monthly_spend, current_avg_ctr, current_avg_cpc, current_avg_roas from the monthly aggregates. - Budget recommendation: increase if accelerating and ROAS ≥ 2.0; decrease if decelerating or ROAS < 1.0; otherwise maintain. - Predicted ROAS: +10% when ROAS ≥ 2.5 and CTR momentum improving; −10% when ROAS < 1.5 and CTR momentum declining; otherwise unchanged. - Risk mitigation and strategic recommendation are set to the exact strings defined by the CASE rules. - Revenue scenarios: expected revenue at current ROAS = predicted spend × current avg ROAS; optimized = predicted spend × predicted ROAS; incremental = predicted spend × (predicted ROAS − current avg ROAS). - Success probability: VERY_HIGH when confidence is HIGH and risk is LOW; HIGH when confidence is HIGH/MEDIUM and risk is not HIGH; MEDIUM when confidence is MEDIUM; otherwise LOW. - Metadata: generated timestamp at query run, base date is today, target date is 30 days after the base date. - Filter to months within the last six months; results are ordered by platform ascending and performance month descending.'

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__predictive_analytics.sql`，`delivered SQL`：

> SELECT
>     NULL::VARCHAR AS "platform",
>     NULL::DATE AS "performance_month",
>     NULL::DOUBLE AS "current_monthly_spend",
>     NULL::DOUBLE AS "current_avg_ctr",
>     NULL::DOUBLE AS "current_avg_cpc",
>     NULL::DOUBLE AS "current_avg_roas",
>     NULL::DOUBLE AS "mom_spend_growth",
>     NULL::DOUBLE AS "mom_ctr_change",
>     NULL::VARCHAR AS "spend_momentum",
>     NULL::VARCHAR AS "ctr_momentum",
>     NULL::DOUBLE AS "predicted_next_month_spend",
>     NULL::DOUBLE AS "predicted_next_month_ctr",
>     NULL::VARCHAR AS "budget_recommendation",
>     NULL::DOUBLE AS "predicted_roas",
>     NULL::VARCHAR AS "forecast_risk_level",
>     NULL::INTEGER AS "anomaly_probability_next_month",
>     NULL::VARCHAR AS "forecast_confidence",
>     NULL::DOUBLE AS "ctr_volatility",
>     NULL::DOUBLE AS "cpc_volatility",
>     NULL::BIGINT AS "active_campaigns",
>     NULL::BIGINT AS "new_campaigns",
>     NULL::BIGINT AS "established_campaigns",
>     NULL::VARCHAR AS "risk_mitigation_plan",
>     NULL::VARCHAR AS "strategic_recommendation",
>     NULL::DOUBLE AS "expected_revenue_current_performance",
>     NULL::DOUBLE AS "expected_revenue_optimized_performance",
>     NULL::DOUBLE AS "incremental_revenue_opportunity",
>     NULL::VARCHAR AS "prediction_success_probability",
>     NULL::TIMESTAMP WITH TIME ZONE AS "forecast_generated_at",
>     NULL::DATE AS "forecast_base_date",
>     NULL::TIMESTAMP AS "forecast_target_date"
> FROM intermediate.int_ad_reporting__unified_campaign_metrics

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。

fallback生成证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/27.json`，`27.args.command`：

> sql='SELECT\n'+',\n'.join(fields)+f'\nFROM {src[0]}'

finish 97以“预测”点名本表并说明占位/未实现；按037表级粒度仅用于本表的该类缺口。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__predictive_analytics.json#whole_implementation_diagnostic`。仅为整体/共享前提诊断，不据此宣称单点贡献。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1474/45694 | 0/0 | 1474/45694 |
| L1 | 1474/45694 | 0/0 | 1474/45694 |
| L2 | 1474/45694 | 0/0 | 1474/45694 |
| L3 | 1474/45694 | 0/0 | 1474/45694 |

## 规模、覆盖和不确定

同类候选/共享前提无法逐项排序，按手册第7节以中把握记该类。整段替换或多位置诊断的差异仅定位，不声称为单点修复贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[11]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='intermediate' AND table_name='int_ad_reporting__unified_campaign_metrics') ORDER BY table_schema,table_name,ordinal_position`。

规则问题：采用手册第7节同类候选无法逐项排序的口径，合并记录共享缺口组；整段诊断不是每个字段的单改，不声称独立字段贡献已知。
