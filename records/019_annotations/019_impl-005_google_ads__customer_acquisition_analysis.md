# impl-005 / google_ads__customer_acquisition_analysis

## 结论

主要原因：**A**；把握：中；标记：无。

契约没有可直接执行排序表达式/完整公式阈值表；higher rank 的名次与数值读法，以及细分规则存在歧义。

参与因素：ltv_cac_performance_percentile=A；acquisition_sophistication_score=A；strategic_customer_segment=A；acquisition_recommendation=A。

不确定性四档：**针对本表的具体说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-005_google_ads__customer_acquisition_analysis.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：10000/10000。本次固定控制下 baseline 行/格规模：10000/80029。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-005/docs/data_contract.yaml`；原文行段 1643–1794。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__customer_acquisition_analysis.sql`，L1–34；SHA-256 `6415fb49ab680446afd09f177a09db9810d12a0b8b0c8f2a2ffcdbbf8ea36d4b`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/sql/marts/google_ads__customer_acquisition_analysis.sql`，L1–288；SHA-256 `0ba4f1e060a9a97dcb2c0daf471f8dd804509259d2abfc99375cea45e9219cd9`。

cohort_avg_cac：agent SQL L16，替换原片段如下。
```sql
avg(customer_acquisition_cost) FILTER(WHERE cumulative_conversions>0) over(partition by acquisition_cohort,advertising_channel_type) cohort_avg_cac
```
替换为：
```sql
AVG(CASE WHEN cumulative_conversions > 0 THEN cumulative_acquisition_cost / cumulative_conversions END) OVER (PARTITION BY acquisition_cohort, advertising_channel_type) AS cohort_avg_cac
```

cohort_avg_ltv：agent SQL L17，替换原片段如下。
```sql
avg(average_customer_ltv) FILTER(WHERE cumulative_conversions>0) over(partition by acquisition_cohort,advertising_channel_type) cohort_avg_ltv
```
替换为：
```sql
AVG(CASE WHEN cumulative_conversions > 0 THEN cumulative_ltv / cumulative_conversions END) OVER (PARTITION BY acquisition_cohort, advertising_channel_type) AS cohort_avg_ltv
```

cac_efficiency_percentile：agent SQL L18，替换原片段如下。
```sql
percent_rank() over(partition by acquisition_cohort order by customer_acquisition_cost desc) cac_efficiency_percentile
```
替换为：
```sql
PERCENT_RANK() OVER (PARTITION BY acquisition_cohort ORDER BY customer_acquisition_cost ASC) AS cac_efficiency_percentile
```

ltv_cac_performance_percentile：agent SQL L19，替换原片段如下。
```sql
percent_rank() over(partition by acquisition_cohort order by ltv_cac_ratio) ltv_cac_performance_percentile
```
替换为：
```sql
PERCENT_RANK() OVER (PARTITION BY acquisition_cohort ORDER BY ltv_cac_ratio DESC) AS ltv_cac_performance_percentile
```

acquisition_sophistication_score：agent SQL L26，替换原片段如下。
```sql
least(100.0,greatest(0.0,channel_diversity_count*15+active_campaigns_count*5+least(average_customer_ltv/100,30)+least(ltv_cac_ratio*5,25))) acquisition_sophistication_score
```
替换为：
```sql
LEAST(100, GREATEST(0, COALESCE(channel_diversity_count * 15, 0) + COALESCE(active_campaigns_count * 5, 0) + CASE WHEN average_customer_ltv > 500 THEN 30 ELSE average_customer_ltv / 500 * 30 END + CASE WHEN ltv_cac_ratio >= 2.0 THEN 25 ELSE ltv_cac_ratio / 2.0 * 25 END)) AS acquisition_sophistication_score
```

strategic_customer_segment：agent SQL L30，替换原片段如下。
```sql
CASE WHEN ltv_cac_ratio>=4 AND average_customer_ltv>1000 THEN 'High-value scale customer' WHEN ltv_cac_ratio<.5 THEN 'Unprofitable customer' WHEN days_since_first_conversion<=30 THEN 'New customer development' WHEN cac_vs_cohort_pct>50 THEN 'High CAC customer' ELSE 'Core customer' END strategic_customer_segment
```
替换为：
```sql
CASE WHEN ltv_cac_ratio >= 3.0 AND average_customer_ltv >= 1000 THEN 'Premium Customer' WHEN ltv_cac_ratio >= 2.0 AND customer_acquisition_cost <= cohort_avg_cac THEN 'High Value Customer' WHEN ltv_cac_ratio >= 1.5 AND days_since_first_conversion <= 90 THEN 'Growth Opportunity' WHEN ltv_cac_ratio < 1.0 AND days_since_first_conversion > 180 THEN 'At Risk Customer' WHEN customer_acquisition_cost > cohort_avg_cac * 1.5 THEN 'High Cost Customer' ELSE 'Standard Customer' END AS strategic_customer_segment
```

acquisition_recommendation：agent SQL L32，替换原片段如下。
```sql
CASE WHEN ltv_cac_ratio>=3 AND cac_efficiency_percentile>=.8 THEN 'Scale acquisition investment' WHEN ltv_cac_ratio<.5 THEN 'Reduce acquisition cost' WHEN channel_diversity_count<2 THEN 'Diversify acquisition channels' WHEN cac_vs_cohort_pct>30 THEN 'Optimize CAC versus cohort' ELSE 'Maintain acquisition strategy' END acquisition_recommendation
```
替换为：
```sql
CASE WHEN ltv_cac_ratio >= 3.0 AND cac_efficiency_percentile >= 0.8 THEN 'Scale Aggressively' WHEN ltv_cac_ratio >= 2.0 AND channel_diversity_count < 3 THEN 'Expand Channels' WHEN ltv_cac_ratio < 1.0 AND days_since_first_conversion > 90 THEN 'Optimize or Pause' WHEN customer_acquisition_cost > cohort_avg_cac * 1.3 THEN 'Reduce Acquisition Spend' WHEN ltv_cac_ratio >= 1.5 AND active_campaigns_count < 5 THEN 'Increase Investment' ELSE 'Maintain Current Strategy' END AS acquisition_recommendation
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-005_google_ads__customer_acquisition_analysis.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 10000 | 80029 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 106, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8005, "clicks": 120, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 120, "conversions_value": 122, "cost_per_conversion": 122, "cpc": 122, "ctr": 122, "cumulative_acquisition_cost": 122, "cumulative_conversions": 110, "cumulative_ltv": 110, "customer_acquisition_cost": 122, "estimated_payback_days": 120, "high_cac_alert": 2, "impressions": 122, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 108, "retention_risk": 4, "roas": 122, "scale_opportunity": 145, "spend": 122, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| baseline | L1 | 10000 | 80764 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8008, "clicks": 164, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 166, "conversions_value": 168, "cost_per_conversion": 168, "cpc": 168, "ctr": 168, "cumulative_acquisition_cost": 168, "cumulative_conversions": 156, "cumulative_ltv": 156, "customer_acquisition_cost": 168, "estimated_payback_days": 166, "high_cac_alert": 2, "impressions": 168, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 154, "retention_risk": 2, "roas": 168, "scale_opportunity": 145, "spend": 168, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| baseline | L2 | 10000 | 60521 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9901, "cac_performance_tier": 8008, "clicks": 152, "conversions": 154, "conversions_value": 156, "cost_per_conversion": 156, "cpc": 156, "ctr": 156, "cumulative_acquisition_cost": 156, "cumulative_conversions": 152, "cumulative_ltv": 152, "customer_acquisition_cost": 156, "estimated_payback_days": 154, "high_cac_alert": 2, "impressions": 156, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 152, "retention_risk": 2, "roas": 156, "scale_opportunity": 145, "spend": 156, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| baseline | L3 | 10000 | 60521 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9901, "cac_performance_tier": 8008, "clicks": 152, "conversions": 154, "conversions_value": 156, "cost_per_conversion": 156, "cpc": 156, "ctr": 156, "cumulative_acquisition_cost": 156, "cumulative_conversions": 152, "cumulative_ltv": 152, "customer_acquisition_cost": 156, "estimated_payback_days": 154, "high_cac_alert": 2, "impressions": 156, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 152, "retention_risk": 2, "roas": 156, "scale_opportunity": 145, "spend": 156, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| cohort_avg_cac | L0 | 10000 | 80029 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 106, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8005, "clicks": 120, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 120, "conversions_value": 122, "cost_per_conversion": 122, "cpc": 122, "ctr": 122, "cumulative_acquisition_cost": 122, "cumulative_conversions": 110, "cumulative_ltv": 110, "customer_acquisition_cost": 122, "estimated_payback_days": 120, "high_cac_alert": 2, "impressions": 122, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 108, "retention_risk": 4, "roas": 122, "scale_opportunity": 145, "spend": 122, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| cohort_avg_cac | L1 | 10000 | 80764 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8008, "clicks": 164, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 166, "conversions_value": 168, "cost_per_conversion": 168, "cpc": 168, "ctr": 168, "cumulative_acquisition_cost": 168, "cumulative_conversions": 156, "cumulative_ltv": 156, "customer_acquisition_cost": 168, "estimated_payback_days": 166, "high_cac_alert": 2, "impressions": 168, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 154, "retention_risk": 2, "roas": 168, "scale_opportunity": 145, "spend": 168, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| cohort_avg_cac | L2 | 10000 | 60521 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9901, "cac_performance_tier": 8008, "clicks": 152, "conversions": 154, "conversions_value": 156, "cost_per_conversion": 156, "cpc": 156, "ctr": 156, "cumulative_acquisition_cost": 156, "cumulative_conversions": 152, "cumulative_ltv": 152, "customer_acquisition_cost": 156, "estimated_payback_days": 154, "high_cac_alert": 2, "impressions": 156, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 152, "retention_risk": 2, "roas": 156, "scale_opportunity": 145, "spend": 156, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| cohort_avg_cac | L3 | 10000 | 60521 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9901, "cac_performance_tier": 8008, "clicks": 152, "conversions": 154, "conversions_value": 156, "cost_per_conversion": 156, "cpc": 156, "ctr": 156, "cumulative_acquisition_cost": 156, "cumulative_conversions": 152, "cumulative_ltv": 152, "customer_acquisition_cost": 156, "estimated_payback_days": 154, "high_cac_alert": 2, "impressions": 156, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 152, "retention_risk": 2, "roas": 156, "scale_opportunity": 145, "spend": 156, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| cohort_avg_ltv | L0 | 10000 | 80029 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 106, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8005, "clicks": 120, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 120, "conversions_value": 122, "cost_per_conversion": 122, "cpc": 122, "ctr": 122, "cumulative_acquisition_cost": 122, "cumulative_conversions": 110, "cumulative_ltv": 110, "customer_acquisition_cost": 122, "estimated_payback_days": 120, "high_cac_alert": 2, "impressions": 122, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 108, "retention_risk": 4, "roas": 122, "scale_opportunity": 145, "spend": 122, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| cohort_avg_ltv | L1 | 10000 | 80764 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8008, "clicks": 164, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 166, "conversions_value": 168, "cost_per_conversion": 168, "cpc": 168, "ctr": 168, "cumulative_acquisition_cost": 168, "cumulative_conversions": 156, "cumulative_ltv": 156, "customer_acquisition_cost": 168, "estimated_payback_days": 166, "high_cac_alert": 2, "impressions": 168, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 154, "retention_risk": 2, "roas": 168, "scale_opportunity": 145, "spend": 168, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| cohort_avg_ltv | L2 | 10000 | 60521 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9901, "cac_performance_tier": 8008, "clicks": 152, "conversions": 154, "conversions_value": 156, "cost_per_conversion": 156, "cpc": 156, "ctr": 156, "cumulative_acquisition_cost": 156, "cumulative_conversions": 152, "cumulative_ltv": 152, "customer_acquisition_cost": 156, "estimated_payback_days": 154, "high_cac_alert": 2, "impressions": 156, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 152, "retention_risk": 2, "roas": 156, "scale_opportunity": 145, "spend": 156, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| cohort_avg_ltv | L3 | 10000 | 60521 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9901, "cac_performance_tier": 8008, "clicks": 152, "conversions": 154, "conversions_value": 156, "cost_per_conversion": 156, "cpc": 156, "ctr": 156, "cumulative_acquisition_cost": 156, "cumulative_conversions": 152, "cumulative_ltv": 152, "customer_acquisition_cost": 156, "estimated_payback_days": 154, "high_cac_alert": 2, "impressions": 156, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 152, "retention_risk": 2, "roas": 156, "scale_opportunity": 145, "spend": 156, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| cac_efficiency_percentile | L0 | 10000 | 61865 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 106, "cac_efficiency_percentile": 110, "cac_performance_tier": 18, "clicks": 108, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 108, "conversions_value": 110, "cost_per_conversion": 110, "cpc": 110, "ctr": 110, "cumulative_acquisition_cost": 110, "cumulative_conversions": 106, "cumulative_ltv": 106, "customer_acquisition_cost": 110, "estimated_payback_days": 108, "high_cac_alert": 2, "impressions": 110, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 108, "retention_risk": 4, "roas": 110, "spend": 110, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| cac_efficiency_percentile | L1 | 10000 | 62653 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 156, "cac_performance_tier": 28, "clicks": 152, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 154, "conversions_value": 156, "cost_per_conversion": 156, "cpc": 156, "ctr": 156, "cumulative_acquisition_cost": 156, "cumulative_conversions": 152, "cumulative_ltv": 152, "customer_acquisition_cost": 156, "estimated_payback_days": 154, "high_cac_alert": 2, "impressions": 156, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 154, "retention_risk": 2, "roas": 156, "spend": 156, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| cac_efficiency_percentile | L2 | 10000 | 42595 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 124, "cac_performance_tier": 28, "clicks": 150, "conversions": 152, "conversions_value": 154, "cost_per_conversion": 154, "cpc": 154, "ctr": 154, "cumulative_acquisition_cost": 154, "cumulative_conversions": 152, "cumulative_ltv": 152, "customer_acquisition_cost": 154, "estimated_payback_days": 152, "high_cac_alert": 2, "impressions": 154, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 152, "retention_risk": 2, "roas": 154, "spend": 154, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| cac_efficiency_percentile | L3 | 10000 | 42595 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 124, "cac_performance_tier": 28, "clicks": 150, "conversions": 152, "conversions_value": 154, "cost_per_conversion": 154, "cpc": 154, "ctr": 154, "cumulative_acquisition_cost": 154, "cumulative_conversions": 152, "cumulative_ltv": 152, "customer_acquisition_cost": 154, "estimated_payback_days": 152, "high_cac_alert": 2, "impressions": 154, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 152, "retention_risk": 2, "roas": 154, "spend": 154, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| ltv_cac_performance_percentile | L0 | 10000 | 70146 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 106, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8005, "clicks": 120, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 120, "conversions_value": 122, "cost_per_conversion": 122, "cpc": 122, "ctr": 122, "cumulative_acquisition_cost": 122, "cumulative_conversions": 110, "cumulative_ltv": 110, "customer_acquisition_cost": 122, "estimated_payback_days": 120, "high_cac_alert": 2, "impressions": 122, "ltv_cac_performance_percentile": 108, "ltv_cac_ratio": 108, "retention_risk": 4, "roas": 122, "scale_opportunity": 145, "spend": 122, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| ltv_cac_performance_percentile | L1 | 10000 | 70927 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8008, "clicks": 164, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 166, "conversions_value": 168, "cost_per_conversion": 168, "cpc": 168, "ctr": 168, "cumulative_acquisition_cost": 168, "cumulative_conversions": 156, "cumulative_ltv": 156, "customer_acquisition_cost": 168, "estimated_payback_days": 166, "high_cac_alert": 2, "impressions": 168, "ltv_cac_performance_percentile": 154, "ltv_cac_ratio": 154, "retention_risk": 2, "roas": 168, "scale_opportunity": 145, "spend": 168, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| ltv_cac_performance_percentile | L2 | 10000 | 50660 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9901, "cac_performance_tier": 8008, "clicks": 152, "conversions": 154, "conversions_value": 156, "cost_per_conversion": 156, "cpc": 156, "ctr": 156, "cumulative_acquisition_cost": 156, "cumulative_conversions": 152, "cumulative_ltv": 152, "customer_acquisition_cost": 156, "estimated_payback_days": 154, "high_cac_alert": 2, "impressions": 156, "ltv_cac_performance_percentile": 130, "ltv_cac_ratio": 152, "retention_risk": 2, "roas": 156, "scale_opportunity": 145, "spend": 156, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| ltv_cac_performance_percentile | L3 | 10000 | 50660 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9901, "cac_performance_tier": 8008, "clicks": 152, "conversions": 154, "conversions_value": 156, "cost_per_conversion": 156, "cpc": 156, "ctr": 156, "cumulative_acquisition_cost": 156, "cumulative_conversions": 152, "cumulative_ltv": 152, "customer_acquisition_cost": 156, "estimated_payback_days": 154, "high_cac_alert": 2, "impressions": 156, "ltv_cac_performance_percentile": 130, "ltv_cac_ratio": 152, "retention_risk": 2, "roas": 156, "scale_opportunity": 145, "spend": 156, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| acquisition_sophistication_score | L0 | 10000 | 68406 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 4, "average_customer_ltv": 4, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8004, "clicks": 20, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 20, "conversions_value": 20, "cost_per_conversion": 20, "cpc": 20, "ctr": 20, "cumulative_acquisition_cost": 20, "cumulative_conversions": 8, "cumulative_ltv": 8, "customer_acquisition_cost": 20, "estimated_payback_days": 20, "impressions": 20, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 8, "retention_risk": 4, "roas": 20, "scale_opportunity": 145, "spend": 20, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| acquisition_sophistication_score | L1 | 10000 | 68370 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 2, "average_customer_ltv": 2, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8004, "clicks": 18, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 18, "conversions_value": 18, "cost_per_conversion": 18, "cpc": 18, "ctr": 18, "cumulative_acquisition_cost": 18, "cumulative_conversions": 6, "cumulative_ltv": 6, "customer_acquisition_cost": 18, "estimated_payback_days": 18, "impressions": 18, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 6, "retention_risk": 2, "roas": 18, "scale_opportunity": 145, "spend": 18, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| acquisition_sophistication_score | L2 | 10000 | 48125 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 2, "average_customer_ltv": 2, "cac_efficiency_percentile": 9899, "cac_performance_tier": 8004, "clicks": 6, "conversions": 6, "conversions_value": 6, "cost_per_conversion": 6, "cpc": 6, "ctr": 6, "cumulative_acquisition_cost": 6, "cumulative_conversions": 2, "cumulative_ltv": 2, "customer_acquisition_cost": 6, "estimated_payback_days": 6, "impressions": 6, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 4, "retention_risk": 2, "roas": 6, "scale_opportunity": 145, "spend": 6, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| acquisition_sophistication_score | L3 | 10000 | 48125 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 2, "average_customer_ltv": 2, "cac_efficiency_percentile": 9899, "cac_performance_tier": 8004, "clicks": 6, "conversions": 6, "conversions_value": 6, "cost_per_conversion": 6, "cpc": 6, "ctr": 6, "cumulative_acquisition_cost": 6, "cumulative_conversions": 2, "cumulative_ltv": 2, "customer_acquisition_cost": 6, "estimated_payback_days": 6, "impressions": 6, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 4, "retention_risk": 2, "roas": 6, "scale_opportunity": 145, "spend": 6, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| strategic_customer_segment | L0 | 10000 | 70037 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 106, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8005, "clicks": 120, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 120, "conversions_value": 122, "cost_per_conversion": 122, "cpc": 122, "ctr": 122, "cumulative_acquisition_cost": 122, "cumulative_conversions": 110, "cumulative_ltv": 110, "customer_acquisition_cost": 122, "estimated_payback_days": 120, "high_cac_alert": 2, "impressions": 122, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 108, "retention_risk": 4, "roas": 122, "scale_opportunity": 145, "spend": 122, "strategic_customer_segment": 8} | L0–L3均不匹配 |
| strategic_customer_segment | L1 | 10000 | 70772 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8008, "clicks": 164, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 166, "conversions_value": 168, "cost_per_conversion": 168, "cpc": 168, "ctr": 168, "cumulative_acquisition_cost": 168, "cumulative_conversions": 156, "cumulative_ltv": 156, "customer_acquisition_cost": 168, "estimated_payback_days": 166, "high_cac_alert": 2, "impressions": 168, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 154, "retention_risk": 2, "roas": 168, "scale_opportunity": 145, "spend": 168, "strategic_customer_segment": 8} | L0–L3均不匹配 |
| strategic_customer_segment | L2 | 10000 | 50529 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9901, "cac_performance_tier": 8008, "clicks": 152, "conversions": 154, "conversions_value": 156, "cost_per_conversion": 156, "cpc": 156, "ctr": 156, "cumulative_acquisition_cost": 156, "cumulative_conversions": 152, "cumulative_ltv": 152, "customer_acquisition_cost": 156, "estimated_payback_days": 154, "high_cac_alert": 2, "impressions": 156, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 152, "retention_risk": 2, "roas": 156, "scale_opportunity": 145, "spend": 156, "strategic_customer_segment": 8} | L0–L3均不匹配 |
| strategic_customer_segment | L3 | 10000 | 50529 | {"acquisition_recommendation": 10000, "acquisition_sophistication_score": 10000, "average_customer_ltv": 152, "cac_efficiency_percentile": 9901, "cac_performance_tier": 8008, "clicks": 152, "conversions": 154, "conversions_value": 156, "cost_per_conversion": 156, "cpc": 156, "ctr": 156, "cumulative_acquisition_cost": 156, "cumulative_conversions": 152, "cumulative_ltv": 152, "customer_acquisition_cost": 156, "estimated_payback_days": 154, "high_cac_alert": 2, "impressions": 156, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 152, "retention_risk": 2, "roas": 156, "scale_opportunity": 145, "spend": 156, "strategic_customer_segment": 8} | L0–L3均不匹配 |
| acquisition_recommendation | L0 | 10000 | 70516 | {"acquisition_recommendation": 555, "acquisition_sophistication_score": 10000, "average_customer_ltv": 102, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8005, "clicks": 116, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 116, "conversions_value": 118, "cost_per_conversion": 118, "cpc": 118, "ctr": 118, "cumulative_acquisition_cost": 118, "cumulative_conversions": 106, "cumulative_ltv": 106, "customer_acquisition_cost": 118, "estimated_payback_days": 116, "high_cac_alert": 2, "impressions": 118, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 104, "roas": 118, "scale_opportunity": 145, "spend": 118, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| acquisition_recommendation | L1 | 10000 | 71285 | {"acquisition_recommendation": 555, "acquisition_sophistication_score": 10000, "average_customer_ltv": 150, "cac_efficiency_percentile": 9990, "cac_performance_tier": 8008, "clicks": 162, "cohort_avg_cac": 10000, "cohort_avg_ltv": 10000, "conversions": 164, "conversions_value": 166, "cost_per_conversion": 166, "cpc": 166, "ctr": 166, "cumulative_acquisition_cost": 166, "cumulative_conversions": 154, "cumulative_ltv": 154, "customer_acquisition_cost": 166, "estimated_payback_days": 164, "high_cac_alert": 2, "impressions": 166, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 152, "roas": 166, "scale_opportunity": 145, "spend": 166, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| acquisition_recommendation | L2 | 10000 | 51042 | {"acquisition_recommendation": 555, "acquisition_sophistication_score": 10000, "average_customer_ltv": 150, "cac_efficiency_percentile": 9901, "cac_performance_tier": 8008, "clicks": 150, "conversions": 152, "conversions_value": 154, "cost_per_conversion": 154, "cpc": 154, "ctr": 154, "cumulative_acquisition_cost": 154, "cumulative_conversions": 150, "cumulative_ltv": 150, "customer_acquisition_cost": 154, "estimated_payback_days": 152, "high_cac_alert": 2, "impressions": 154, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 150, "roas": 154, "scale_opportunity": 145, "spend": 154, "strategic_customer_segment": 10000} | L0–L3均不匹配 |
| acquisition_recommendation | L3 | 10000 | 51042 | {"acquisition_recommendation": 555, "acquisition_sophistication_score": 10000, "average_customer_ltv": 150, "cac_efficiency_percentile": 9901, "cac_performance_tier": 8008, "clicks": 150, "conversions": 152, "conversions_value": 154, "cost_per_conversion": 154, "cpc": 154, "ctr": 154, "cumulative_acquisition_cost": 154, "cumulative_conversions": 150, "cumulative_ltv": 150, "customer_acquisition_cost": 154, "estimated_payback_days": 152, "high_cac_alert": 2, "impressions": 154, "ltv_cac_performance_percentile": 9991, "ltv_cac_ratio": 150, "roas": 154, "scale_opportunity": 145, "spend": 154, "strategic_customer_segment": 10000} | L0–L3均不匹配 |

- cohort_avg_cac（C，单处 SQL 改动）：行减少 0，格减少 0。输出表达式/排序与契约规定不一致。

- cohort_avg_ltv（C，单处 SQL 改动）：行减少 0，格减少 0。输出表达式/排序与契约规定不一致。

- cac_efficiency_percentile（A，单处 SQL 改动）：行减少 0，格减少 18164。契约没有可直接执行排序表达式/完整公式阈值表；higher rank 的名次与数值读法，以及细分规则存在歧义。

- ltv_cac_performance_percentile（A，单处 SQL 改动）：行减少 0，格减少 9883。契约没有可直接执行排序表达式/完整公式阈值表；higher rank 的名次与数值读法，以及细分规则存在歧义。

- acquisition_sophistication_score（A，单处 SQL 改动）：行减少 0，格减少 11623。契约没有可直接执行排序表达式/完整公式阈值表；higher rank 的名次与数值读法，以及细分规则存在歧义。

- strategic_customer_segment（A，单处 SQL 改动）：行减少 0，格减少 9992。契约没有可直接执行排序表达式/完整公式阈值表；higher rank 的名次与数值读法，以及细分规则存在歧义。

- acquisition_recommendation（A，单处 SQL 改动）：行减少 0，格减少 9513。契约没有可直接执行排序表达式/完整公式阈值表；higher rank 的名次与数值读法，以及细分规则存在歧义。

## agent 可见证据及不确定性

event 47 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/47.json`，字段字符偏移 816。

> customer acquisition 的细分/建议规则未提供完整精确规则表，channel strategic recommendation 也未规定完整优先级；已采用保守、透明的 CASE 规则。

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

契约的“lower CAC ranked higher / higher ratio ranked higher”可解释成较大的 percentile 或较前的排序名次；未给 ORDER BY 表达式。本次按 A 处理，不用 gold 排序替契约补定义。sophistication/segment/recommendation 也没有完整斜率和阈值表。
