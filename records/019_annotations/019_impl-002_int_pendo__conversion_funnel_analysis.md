# impl-002 / int_pendo__conversion_funnel_analysis

## 结论

主要原因：**D**；把握：中；标记：已披露。

feature use 被换成 event.num_events>0；恢复规定 feature_event 来源。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**针对本表的具体说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-002_int_pendo__conversion_funnel_analysis.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：49963/104898。本次固定控制下 baseline 行/格规模：104898/1821794。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml`；原文行段 691–771。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，L1–1；SHA-256 `0e2aebecf921dd969d62e7d5c640fd5bd780c11e8286680e448aa4adb1594736`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，L1–211；SHA-256 `19487065f9397929672c27745d2f94b670211cf81b806974c9b87f121098c4c9`。

feature_source：agent SQL L1，替换原片段如下。
```sql
count(DISTINCT CASE WHEN num_events>0 THEN visitor_id END) visitors_with_feature_use
```
替换为：
```sql
(SELECT count(DISTINCT f.visitor_id) FROM staging.stg_pendo__feature_event f WHERE f.account_id=staging.stg_pendo__event.account_id AND f.app_id=staging.stg_pendo__event.app_id AND cast(f.occurred_at AS DATE)=cast(staging.stg_pendo__event.occurred_at AS DATE)) visitors_with_feature_use
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-002_int_pendo__conversion_funnel_analysis.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 104898 | 1821794 | {"avg_30d_feature_to_deep_rate": 49963, "avg_30d_overall_conversion_rate": 49963, "avg_30d_page_to_feature_rate": 49963, "avg_engagement_score": 49963, "avg_features_per_user": 14, "avg_pages_per_visitor": 49963, "bounce_rate": 49963, "event_date": 15037, "feature_to_deep_conversion_rate": 49963, "funnel_health_rating": 3511, "high_quality_session_rate": 49963, "optimization_recommendation": 49963, "overall_conversion_rate": 49935, "page_to_feature_conversion_rate": 49949, "total_visitors": 102, "visitors_with_deep_engagement": 49935, "visitors_with_feature_use": 49949, "visitors_with_page_views": 60} | L0–L3均不匹配 |
| baseline | L1 | 104898 | 1821792 | {"avg_30d_feature_to_deep_rate": 49963, "avg_30d_overall_conversion_rate": 49963, "avg_30d_page_to_feature_rate": 49963, "avg_engagement_score": 49963, "avg_features_per_user": 14, "avg_pages_per_visitor": 49963, "bounce_rate": 49963, "event_date": 15043, "feature_to_deep_conversion_rate": 49963, "funnel_health_rating": 3511, "high_quality_session_rate": 49963, "optimization_recommendation": 49963, "overall_conversion_rate": 49935, "page_to_feature_conversion_rate": 49949, "total_visitors": 98, "visitors_with_deep_engagement": 49935, "visitors_with_feature_use": 49949, "visitors_with_page_views": 56} | L0–L3均不匹配 |
| baseline | L2 | 104898 | 1821806 | {"avg_30d_feature_to_deep_rate": 49963, "avg_30d_overall_conversion_rate": 49963, "avg_30d_page_to_feature_rate": 49963, "avg_engagement_score": 49963, "avg_features_per_user": 14, "avg_pages_per_visitor": 49963, "bounce_rate": 49963, "event_date": 15057, "feature_to_deep_conversion_rate": 49963, "funnel_health_rating": 3511, "high_quality_session_rate": 49963, "optimization_recommendation": 49963, "overall_conversion_rate": 49935, "page_to_feature_conversion_rate": 49949, "total_visitors": 98, "visitors_with_deep_engagement": 49935, "visitors_with_feature_use": 49949, "visitors_with_page_views": 56} | L0–L3均不匹配 |
| baseline | L3 | 104898 | 1821806 | {"avg_30d_feature_to_deep_rate": 49963, "avg_30d_overall_conversion_rate": 49963, "avg_30d_page_to_feature_rate": 49963, "avg_engagement_score": 49963, "avg_features_per_user": 14, "avg_pages_per_visitor": 49963, "bounce_rate": 49963, "event_date": 15057, "feature_to_deep_conversion_rate": 49963, "funnel_health_rating": 3511, "high_quality_session_rate": 49963, "optimization_recommendation": 49963, "overall_conversion_rate": 49935, "page_to_feature_conversion_rate": 49949, "total_visitors": 98, "visitors_with_deep_engagement": 49935, "visitors_with_feature_use": 49949, "visitors_with_page_views": 56} | L0–L3均不匹配 |
| feature_source | L0 | 104898 | 1622105 | {"avg_30d_feature_to_deep_rate": 76, "avg_30d_overall_conversion_rate": 49963, "avg_30d_page_to_feature_rate": 49963, "avg_engagement_score": 49963, "avg_features_per_user": 14, "avg_pages_per_visitor": 49963, "bounce_rate": 49963, "event_date": 15037, "feature_to_deep_conversion_rate": 23, "funnel_health_rating": 3511, "high_quality_session_rate": 49963, "optimization_recommendation": 49963, "overall_conversion_rate": 49935, "page_to_feature_conversion_rate": 18, "total_visitors": 102, "visitors_with_deep_engagement": 49935, "visitors_with_feature_use": 18, "visitors_with_page_views": 60} | L0–L3均不匹配 |
| feature_source | L1 | 104898 | 1622103 | {"avg_30d_feature_to_deep_rate": 76, "avg_30d_overall_conversion_rate": 49963, "avg_30d_page_to_feature_rate": 49963, "avg_engagement_score": 49963, "avg_features_per_user": 14, "avg_pages_per_visitor": 49963, "bounce_rate": 49963, "event_date": 15043, "feature_to_deep_conversion_rate": 23, "funnel_health_rating": 3511, "high_quality_session_rate": 49963, "optimization_recommendation": 49963, "overall_conversion_rate": 49935, "page_to_feature_conversion_rate": 18, "total_visitors": 98, "visitors_with_deep_engagement": 49935, "visitors_with_feature_use": 18, "visitors_with_page_views": 56} | L0–L3均不匹配 |
| feature_source | L2 | 104898 | 1622117 | {"avg_30d_feature_to_deep_rate": 76, "avg_30d_overall_conversion_rate": 49963, "avg_30d_page_to_feature_rate": 49963, "avg_engagement_score": 49963, "avg_features_per_user": 14, "avg_pages_per_visitor": 49963, "bounce_rate": 49963, "event_date": 15057, "feature_to_deep_conversion_rate": 23, "funnel_health_rating": 3511, "high_quality_session_rate": 49963, "optimization_recommendation": 49963, "overall_conversion_rate": 49935, "page_to_feature_conversion_rate": 18, "total_visitors": 98, "visitors_with_deep_engagement": 49935, "visitors_with_feature_use": 18, "visitors_with_page_views": 56} | L0–L3均不匹配 |
| feature_source | L3 | 104898 | 1622117 | {"avg_30d_feature_to_deep_rate": 76, "avg_30d_overall_conversion_rate": 49963, "avg_30d_page_to_feature_rate": 49963, "avg_engagement_score": 49963, "avg_features_per_user": 14, "avg_pages_per_visitor": 49963, "bounce_rate": 49963, "event_date": 15057, "feature_to_deep_conversion_rate": 23, "funnel_health_rating": 3511, "high_quality_session_rate": 49963, "optimization_recommendation": 49963, "overall_conversion_rate": 49935, "page_to_feature_conversion_rate": 18, "total_visitors": 98, "visitors_with_deep_engagement": 49935, "visitors_with_feature_use": 18, "visitors_with_page_views": 56} | L0–L3均不匹配 |

- feature_source（D，单处 SQL 改动）：行减少 0，格减少 199689。feature use 被换成 event.num_events>0；恢复规定 feature_event 来源。

## agent 可见证据及不确定性

event 59 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，字段字符偏移 1215。

> Several complex outputs remain simplified relative to the detailed contract: product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations; the data-quality report is summary-only; RFM account-level metrics are NULL placeholders; and advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

错误点粒度存在两种读法：每个占位输出列分别算一处，或将同一遗漏聚合/规则模块视为一个降级错误点。本次以模块为错误点，列出全部可见占位及残余列统计，以局部恢复模块内表达式/来源证明贡献；没有用整份 gold SQL 替换来宣称因果成立。未逐一补齐全部占位列，不能据局部修法宣称已覆盖模块内所有修复。若后续决定按列拆分，需重新比较这些因素的贡献排序。
