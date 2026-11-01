# impl-005_google_ads__executive_dashboard（037 正式批次）

主要原因：**代码写错**；把握：高。019旧主要原因原样保留：`I`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__executive_dashboard.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/47.json`，finish 47 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/google_ads.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-005_google_ads__executive_dashboard.json`；037补充：`records/037_checks/`。

## 逐点标注

### rounded_alias

- 类别：代码写错；角色：主要；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

agent已经写出正确round表达式，但SELECT *中的同名列优先，后列被自动改名，最终仍输出旧列；正确意图有明确代码证据。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: '1) Start from intermediate.int_google_ads__account_performance_metrics and rename core metrics to account-level totals: total_spend=spend; total_clicks=clicks; total_impressions=impressions; total_conversions=conversions; total_conversions_value=conversions_value; overall_ctr=ctr; overall_cpc=cpc; overall_cost_per_conversion=cost_per_conversion; overall_roas=roas. Also carry: source_relation, account_id, account_name, currency_code, date_day, account_maturity_stage, performance_score, performance_tier, spend_mom_change_pct, conversions_mom_change_pct. 2) Build campaign_aggregates by date_day (global scope) from intermediate.int_google_ads__campaign_cohort_analysis: active_campaigns=count of distinct campaigns; campaigns_in_launch/growth/maturity=count of distinct campaigns in each lifecycle stage; high_momentum_campaigns=count with momentum_indicator=''High Momentum''; underperforming_campaigns=count with underperforming_flag=true; premium_investment_campaigns=count with investment_tier=''Premium Investment''; premium_investment_spend=sum of spend for ''Premium Investment''. Null campaign/category values are not counted; missing dates yield no records. 3) Build keyword_aggregates by date_day (global scope) from intermediate.int_google_ads__keyword_performance_segmentation: active_keywords=count of distinct keywords; star_performer_keywords=count with performance_tier=''Star Performer''; bid_increase_opportunities=count where bid_recommendation starts with ''Increase''; pause_candidate_keywords=count with pause_candidate_flag=true; avg_keyword_efficiency_score=average efficiency_score. Missing dates yield no records. 4) Join account-level metrics to campaign_aggregates and keyword_aggregates on date_day; replace missing aggregate counts and premium_investment_spend with 0; set avg_keyword_efficiency_score to 0 when missing. 5) Compute trends per account_id ordered by date_day: - spend_wow_growth_pct: percent change in total_spend vs the value 7 days prior; round to 2 decimals; set to null if the prior value is missing or <= 0. - conversions_wow_growth_pct: percent change in total_conversions vs the value 7 days prior; round to 2 decimals; set to null if the prior value is missing or <= 0. - spend_30d_avg: rolling average of total_spend over the current day and the 29 preceding rows for the same account; rounded in final to 2 decimals. - roas_30d_avg: rolling average of overall_roas over the current day and the 29 preceding rows for the same account; rounded in final to 4 decimals. - performance_score_30d_avg: rolling average of performance_score over the current day and the 29 preceding rows for the same account; rounded in final to 1 decimal. Window partition: by account_id; order: date_day ascending. 6) Derive classifications and flags: - premium_investment_pct: premium_investment_spend/total_spend*100; round to 2 decimals; if total_spend=0 then null (rows with 0 spend are excluded by filter). - performance_alert (first match wins): spend_wow_growth_pct > 50 → ''High Spend Growth Alert''; spend_wow_growth_pct < -30 → ''Spend Decline Alert''; conversions_wow_growth_pct > 50 → ''Conversion Growth Opportunity''; conversions_wow_growth_pct < -30 → ''Conversion Decline Alert''; overall_roas < 1.0 and total_spend > 1000 → ''ROI Optimization Needed''; underperforming_campaigns/active_campaigns > 0.3 using safe divide → ''Portfolio Health Issue''; else ''Normal Performance''. - strategic_recommendation (first match wins): star_performer_keywords/active_keywords > 0.2 and bid_increase_opportunities > 10 using safe divide → ''Scale High Performers''; pause_candidate_keywords/active_keywords > 0.2 using safe divide → ''Portfolio Optimization Needed''; high_momentum_campaigns/active_campaigns > 0.3 using safe divide → ''Invest in Growth''; avg_keyword_efficiency_score < 40 → ''Keyword Strategy Review''; premium_investment_spend/total_spend < 0.1 using safe divide → ''Consider Premium Investments''; else ''Maintain Current Strategy''. - budget_efficiency_tier: ''Highly Efficient'' if overall_roas >= 4.0; ''Efficient'' if >= 2.0; ''Break-even'' if >= 1.0; ''Underperforming'' if >= 0.5; else ''Poor Performance''. - overall_account_health_score: cap to [0,100] after combining performance_score*0.6 and avg_keyword_efficiency_score*0.4; treat missing inputs as 0. - immediate_attention_required: true if overall_roas < 1.0 and total_spend > 1000; else false. - trending_alert: true if spend_wow_growth_pct > 50 or conversions_wow_growth_pct < -30; else false. - scale_opportunity: true if star_performer_keywords/active_keywords > 0.15 using safe divide; else false. - top_performer_account: true if performance_score*0.6 + avg_keyword_efficiency_score*0.4 >= 80; else false. 7) Filter to executive-relevant rows: total_spend > 0, account_id present, date_day present. Order by account_id ascending and date_day descending.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__executive_dashboard.sql`，第 15–15 行：

```sql
SELECT *,round(spend_30d_avg,2)
```

单改/诊断：`records/019_reruns_impl-005_google_ads__executive_dashboard.json#rounded_alias`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 10000/30474 | 805/1029 | 9195/29445 |
| L1 | 10000/30474 | 805/1029 | 9195/29445 |
| L2 | 9090/10024 | 805/1028 | 8285/8996 |
| L3 | 9090/10024 | 805/1028 | 8285/8996 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，event `1.message`：

> business_logic: '1) Start from intermediate.int_google_ads__account_performance_metrics and rename core metrics to account-level totals: total_spend=spend; total_clicks=clicks; total_impressions=impressions; total_conversions=conversions; total_conversions_value=conversions_value; overall_ctr=ctr; overall_cpc=cpc; overall_cost_per_conversion=cost_per_conversion; overall_roas=roas. Also carry: source_relation, account_id, account_name, currency_code, date_day, account_maturity_stage, performance_score, performance_tier, spend_mom_change_pct, conversions_mom_change_pct. 2) Build campaign_aggregates by date_day (global scope) from intermediate.int_google_ads__campaign_cohort_analysis: active_campaigns=count of distinct campaigns; campaigns_in_launch/growth/maturity=count of distinct campaigns in each lifecycle stage; high_momentum_campaigns=count with momentum_indicator=''High Momentum''; underperforming_campaigns=count with underperforming_flag=true; premium_investment_campaigns=count with investment_tier=''Premium Investment''; premium_investment_spend=sum of spend for ''Premium Investment''. Null campaign/category values are not counted; missing dates yield no records. 3) Build keyword_aggregates by date_day (global scope) from intermediate.int_google_ads__keyword_performance_segmentation: active_keywords=count of distinct keywords; star_performer_keywords=count with performance_tier=''Star Performer''; bid_increase_opportunities=count where bid_recommendation starts with ''Increase''; pause_candidate_keywords=count with pause_candidate_flag=true; avg_keyword_efficiency_score=average efficiency_score. Missing dates yield no records. 4) Join account-level metrics to campaign_aggregates and keyword_aggregates on date_day; replace missing aggregate counts and premium_investment_spend with 0; set avg_keyword_efficiency_score to 0 when missing. 5) Compute trends per account_id ordered by date_day: - spend_wow_growth_pct: percent change in total_spend vs the value 7 days prior; round to 2 decimals; set to null if the prior value is missing or <= 0. - conversions_wow_growth_pct: percent change in total_conversions vs the value 7 days prior; round to 2 decimals; set to null if the prior value is missing or <= 0. - spend_30d_avg: rolling average of total_spend over the current day and the 29 preceding rows for the same account; rounded in final to 2 decimals. - roas_30d_avg: rolling average of overall_roas over the current day and the 29 preceding rows for the same account; rounded in final to 4 decimals. - performance_score_30d_avg: rolling average of performance_score over the current day and the 29 preceding rows for the same account; rounded in final to 1 decimal. Window partition: by account_id; order: date_day ascending. 6) Derive classifications and flags: - premium_investment_pct: premium_investment_spend/total_spend*100; round to 2 decimals; if total_spend=0 then null (rows with 0 spend are excluded by filter). - performance_alert (first match wins): spend_wow_growth_pct > 50 → ''High Spend Growth Alert''; spend_wow_growth_pct < -30 → ''Spend Decline Alert''; conversions_wow_growth_pct > 50 → ''Conversion Growth Opportunity''; conversions_wow_growth_pct < -30 → ''Conversion Decline Alert''; overall_roas < 1.0 and total_spend > 1000 → ''ROI Optimization Needed''; underperforming_campaigns/active_campaigns > 0.3 using safe divide → ''Portfolio Health Issue''; else ''Normal Performance''. - strategic_recommendation (first match wins): star_performer_keywords/active_keywords > 0.2 and bid_increase_opportunities > 10 using safe divide → ''Scale High Performers''; pause_candidate_keywords/active_keywords > 0.2 using safe divide → ''Portfolio Optimization Needed''; high_momentum_campaigns/active_campaigns > 0.3 using safe divide → ''Invest in Growth''; avg_keyword_efficiency_score < 40 → ''Keyword Strategy Review''; premium_investment_spend/total_spend < 0.1 using safe divide → ''Consider Premium Investments''; else ''Maintain Current Strategy''. - budget_efficiency_tier: ''Highly Efficient'' if overall_roas >= 4.0; ''Efficient'' if >= 2.0; ''Break-even'' if >= 1.0; ''Underperforming'' if >= 0.5; else ''Poor Performance''. - overall_account_health_score: cap to [0,100] after combining performance_score*0.6 and avg_keyword_efficiency_score*0.4; treat missing inputs as 0. - immediate_attention_required: true if overall_roas < 1.0 and total_spend > 1000; else false. - trending_alert: true if spend_wow_growth_pct > 50 or conversions_wow_growth_pct < -30; else false. - scale_opportunity: true if star_performer_keywords/active_keywords > 0.15 using safe divide; else false. - top_performer_account: true if performance_score*0.6 + avg_keyword_efficiency_score*0.4 >= 80; else false. 7) Filter to executive-relevant rows: total_spend > 0, account_id present, date_day present. Order by account_id ascending and date_day descending.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### scale_null

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约规定扩张标志默认false，agent布尔比较留下NULL；修改值的语义而非形式。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: '1) Start from intermediate.int_google_ads__account_performance_metrics and rename core metrics to account-level totals: total_spend=spend; total_clicks=clicks; total_impressions=impressions; total_conversions=conversions; total_conversions_value=conversions_value; overall_ctr=ctr; overall_cpc=cpc; overall_cost_per_conversion=cost_per_conversion; overall_roas=roas. Also carry: source_relation, account_id, account_name, currency_code, date_day, account_maturity_stage, performance_score, performance_tier, spend_mom_change_pct, conversions_mom_change_pct. 2) Build campaign_aggregates by date_day (global scope) from intermediate.int_google_ads__campaign_cohort_analysis: active_campaigns=count of distinct campaigns; campaigns_in_launch/growth/maturity=count of distinct campaigns in each lifecycle stage; high_momentum_campaigns=count with momentum_indicator=''High Momentum''; underperforming_campaigns=count with underperforming_flag=true; premium_investment_campaigns=count with investment_tier=''Premium Investment''; premium_investment_spend=sum of spend for ''Premium Investment''. Null campaign/category values are not counted; missing dates yield no records. 3) Build keyword_aggregates by date_day (global scope) from intermediate.int_google_ads__keyword_performance_segmentation: active_keywords=count of distinct keywords; star_performer_keywords=count with performance_tier=''Star Performer''; bid_increase_opportunities=count where bid_recommendation starts with ''Increase''; pause_candidate_keywords=count with pause_candidate_flag=true; avg_keyword_efficiency_score=average efficiency_score. Missing dates yield no records. 4) Join account-level metrics to campaign_aggregates and keyword_aggregates on date_day; replace missing aggregate counts and premium_investment_spend with 0; set avg_keyword_efficiency_score to 0 when missing. 5) Compute trends per account_id ordered by date_day: - spend_wow_growth_pct: percent change in total_spend vs the value 7 days prior; round to 2 decimals; set to null if the prior value is missing or <= 0. - conversions_wow_growth_pct: percent change in total_conversions vs the value 7 days prior; round to 2 decimals; set to null if the prior value is missing or <= 0. - spend_30d_avg: rolling average of total_spend over the current day and the 29 preceding rows for the same account; rounded in final to 2 decimals. - roas_30d_avg: rolling average of overall_roas over the current day and the 29 preceding rows for the same account; rounded in final to 4 decimals. - performance_score_30d_avg: rolling average of performance_score over the current day and the 29 preceding rows for the same account; rounded in final to 1 decimal. Window partition: by account_id; order: date_day ascending. 6) Derive classifications and flags: - premium_investment_pct: premium_investment_spend/total_spend*100; round to 2 decimals; if total_spend=0 then null (rows with 0 spend are excluded by filter). - performance_alert (first match wins): spend_wow_growth_pct > 50 → ''High Spend Growth Alert''; spend_wow_growth_pct < -30 → ''Spend Decline Alert''; conversions_wow_growth_pct > 50 → ''Conversion Growth Opportunity''; conversions_wow_growth_pct < -30 → ''Conversion Decline Alert''; overall_roas < 1.0 and total_spend > 1000 → ''ROI Optimization Needed''; underperforming_campaigns/active_campaigns > 0.3 using safe divide → ''Portfolio Health Issue''; else ''Normal Performance''. - strategic_recommendation (first match wins): star_performer_keywords/active_keywords > 0.2 and bid_increase_opportunities > 10 using safe divide → ''Scale High Performers''; pause_candidate_keywords/active_keywords > 0.2 using safe divide → ''Portfolio Optimization Needed''; high_momentum_campaigns/active_campaigns > 0.3 using safe divide → ''Invest in Growth''; avg_keyword_efficiency_score < 40 → ''Keyword Strategy Review''; premium_investment_spend/total_spend < 0.1 using safe divide → ''Consider Premium Investments''; else ''Maintain Current Strategy''. - budget_efficiency_tier: ''Highly Efficient'' if overall_roas >= 4.0; ''Efficient'' if >= 2.0; ''Break-even'' if >= 1.0; ''Underperforming'' if >= 0.5; else ''Poor Performance''. - overall_account_health_score: cap to [0,100] after combining performance_score*0.6 and avg_keyword_efficiency_score*0.4; treat missing inputs as 0. - immediate_attention_required: true if overall_roas < 1.0 and total_spend > 1000; else false. - trending_alert: true if spend_wow_growth_pct > 50 or conversions_wow_growth_pct < -30; else false. - scale_opportunity: true if star_performer_keywords/active_keywords > 0.15 using safe divide; else false. - top_performer_account: true if performance_score*0.6 + avg_keyword_efficiency_score*0.4 >= 80; else false. 7) Filter to executive-relevant rows: total_spend > 0, account_id present, date_day present. Order by account_id ascending and date_day descending.'

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__executive_dashboard.sql`，第 24–24 行：

```sql
(star_pct>15) scale_opportunity
```

单改/诊断：`records/019_reruns_impl-005_google_ads__executive_dashboard.json#scale_null`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 10000/30474 | 10000/30458 | 0/16 |
| L1 | 10000/30474 | 10000/30458 | 0/16 |
| L2 | 9090/10024 | 9087/10008 | 3/16 |
| L3 | 9090/10024 | 9087/10008 | 3/16 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，event `1.message`：

> business_logic: '1) Start from intermediate.int_google_ads__account_performance_metrics and rename core metrics to account-level totals: total_spend=spend; total_clicks=clicks; total_impressions=impressions; total_conversions=conversions; total_conversions_value=conversions_value; overall_ctr=ctr; overall_cpc=cpc; overall_cost_per_conversion=cost_per_conversion; overall_roas=roas. Also carry: source_relation, account_id, account_name, currency_code, date_day, account_maturity_stage, performance_score, performance_tier, spend_mom_change_pct, conversions_mom_change_pct. 2) Build campaign_aggregates by date_day (global scope) from intermediate.int_google_ads__campaign_cohort_analysis: active_campaigns=count of distinct campaigns; campaigns_in_launch/growth/maturity=count of distinct campaigns in each lifecycle stage; high_momentum_campaigns=count with momentum_indicator=''High Momentum''; underperforming_campaigns=count with underperforming_flag=true; premium_investment_campaigns=count with investment_tier=''Premium Investment''; premium_investment_spend=sum of spend for ''Premium Investment''. Null campaign/category values are not counted; missing dates yield no records. 3) Build keyword_aggregates by date_day (global scope) from intermediate.int_google_ads__keyword_performance_segmentation: active_keywords=count of distinct keywords; star_performer_keywords=count with performance_tier=''Star Performer''; bid_increase_opportunities=count where bid_recommendation starts with ''Increase''; pause_candidate_keywords=count with pause_candidate_flag=true; avg_keyword_efficiency_score=average efficiency_score. Missing dates yield no records. 4) Join account-level metrics to campaign_aggregates and keyword_aggregates on date_day; replace missing aggregate counts and premium_investment_spend with 0; set avg_keyword_efficiency_score to 0 when missing. 5) Compute trends per account_id ordered by date_day: - spend_wow_growth_pct: percent change in total_spend vs the value 7 days prior; round to 2 decimals; set to null if the prior value is missing or <= 0. - conversions_wow_growth_pct: percent change in total_conversions vs the value 7 days prior; round to 2 decimals; set to null if the prior value is missing or <= 0. - spend_30d_avg: rolling average of total_spend over the current day and the 29 preceding rows for the same account; rounded in final to 2 decimals. - roas_30d_avg: rolling average of overall_roas over the current day and the 29 preceding rows for the same account; rounded in final to 4 decimals. - performance_score_30d_avg: rolling average of performance_score over the current day and the 29 preceding rows for the same account; rounded in final to 1 decimal. Window partition: by account_id; order: date_day ascending. 6) Derive classifications and flags: - premium_investment_pct: premium_investment_spend/total_spend*100; round to 2 decimals; if total_spend=0 then null (rows with 0 spend are excluded by filter). - performance_alert (first match wins): spend_wow_growth_pct > 50 → ''High Spend Growth Alert''; spend_wow_growth_pct < -30 → ''Spend Decline Alert''; conversions_wow_growth_pct > 50 → ''Conversion Growth Opportunity''; conversions_wow_growth_pct < -30 → ''Conversion Decline Alert''; overall_roas < 1.0 and total_spend > 1000 → ''ROI Optimization Needed''; underperforming_campaigns/active_campaigns > 0.3 using safe divide → ''Portfolio Health Issue''; else ''Normal Performance''. - strategic_recommendation (first match wins): star_performer_keywords/active_keywords > 0.2 and bid_increase_opportunities > 10 using safe divide → ''Scale High Performers''; pause_candidate_keywords/active_keywords > 0.2 using safe divide → ''Portfolio Optimization Needed''; high_momentum_campaigns/active_campaigns > 0.3 using safe divide → ''Invest in Growth''; avg_keyword_efficiency_score < 40 → ''Keyword Strategy Review''; premium_investment_spend/total_spend < 0.1 using safe divide → ''Consider Premium Investments''; else ''Maintain Current Strategy''. - budget_efficiency_tier: ''Highly Efficient'' if overall_roas >= 4.0; ''Efficient'' if >= 2.0; ''Break-even'' if >= 1.0; ''Underperforming'' if >= 0.5; else ''Poor Performance''. - overall_account_health_score: cap to [0,100] after combining performance_score*0.6 and avg_keyword_efficiency_score*0.4; treat missing inputs as 0. - immediate_attention_required: true if overall_roas < 1.0 and total_spend > 1000; else false. - trending_alert: true if spend_wow_growth_pct > 50 or conversions_wow_growth_pct < -30; else false. - scale_opportunity: true if star_performer_keywords/active_keywords > 0.15 using safe divide; else false. - top_performer_account: true if performance_score*0.6 + avg_keyword_efficiency_score*0.4 >= 80; else false. 7) Filter to executive-relevant rows: total_spend > 0, account_id present, date_day present. Order by account_id ascending and date_day descending.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### trending_null

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约trending_alert的else为false，agent三值逻辑留下NULL；算法已规定。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: trending_alert
>         data_type: BOOLEAN
>         description: True if spend_wow_growth_pct > 50 or conversions_wow_growth_pct < -30, else false
>         tests:
>         - not_null

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__executive_dashboard.sql`，第 24–24 行：

```sql
(spend_wow_growth_pct>50 OR conversions_wow_growth_pct< -30) trending_alert
```

单改/诊断：`records/037_checks/rerun_impl-005_google_ads__executive_dashboard.json#trending_null`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 10000/30474 | 10000/29769 | 0/705 |
| L1 | 10000/30474 | 10000/29769 | 0/705 |
| L2 | 9090/10024 | 9003/9319 | 87/705 |
| L3 | 9090/10024 | 9003/9319 | 87/705 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，event `1.message`：

> - name: trending_alert
>         data_type: BOOLEAN
>         description: True if spend_wow_growth_pct > 50 or conversions_wow_growth_pct < -30, else false
>         tests:
>         - not_null

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
