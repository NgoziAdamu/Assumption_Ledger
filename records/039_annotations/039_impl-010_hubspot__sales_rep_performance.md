# impl-010_hubspot__sales_rep_performance（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**其他**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`O`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 200, "cell_scale": 862}, "L1": {"row_scale": 200, "cell_scale": 862}, "L2": {"row_scale": 200, "cell_scale": 701}, "L3": {"row_scale": 200, "cell_scale": 701}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| enterprise_revenue | Unstated Choice | 非原因 | 0 | 0 | 4 |
| large_revenue | Unstated Choice | 参与 | 1 | 74 | 4 |
| medium_revenue | Unstated Choice | 参与 | 0 | 108 | 4 |
| small_revenue | Unstated Choice | 参与 | 0 | 171 | 4 |
| volume_rank_peer_order | 其他 | 主要 | 1 | 178 | 4 |
| efficiency_rank_peer_order | 其他 | 参与 | 0 | 4 | 4 |
| win_rate_rank_projection | 其他 | 参与 | 0 | 164 | 4 |
| recent_month_window | Intent Misreading | 非原因 | 0 | 0 | 4 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: hubspot__sales_rep_performance
      schema: sales
      description: Sales representative performance analytics with rankings, segment metrics, trends, and derived classifications
      grain: One row per owner_id (only reps with total_deals > 0)
      source_models:
      - intermediate.int_hubspot__owner_performance_metrics
      - intermediate.int_hubspot__deal_performance_metrics
      business_logic: '- Start from intermediate.int_hubspot__owner_performance_metrics and retain only owners where total_deals > 0. - Build monthly deal performance per owner from intermediate.int_hubspot__deal_performance_metrics: - Group by owner_id and the year/month of created_date; exclude rows where created_date is NULL. - monthly_deals_created: count distinct deal_id per month. - monthly_deals_won: count distinct deal_id where deal_status = ''Won''. - monthly_revenue: sum deal_amount where deal_status = ''Won'' (0 otherwise). - monthly_pipeline_added: sum deal_amount where deal_status = ''Open'' (0 otherwise). - monthly_win_rate: if decided deals (Won or Lost) exist, compute 100 × (won / decided); otherwise 0. - monthly_avg_cycle_time: average deal_cycle_time_days for won deals; NULL if none. - Aggregate per-owner trends over monthly data: - Use month_index = performance_year*12 + performance_month and current_month_index from current_date. - recent_6m_avg_revenue: average monthly_revenue where month_index >= current_month_index - 6 (inclusive). - prior_6m_avg_revenue: average monthly_revenue where month_index between current_month_index - 12 and current_month_index - 7 (inclusive). - recent_6m_avg_win_rate / prior_6m_avg_win_rate: analogous averages over monthly_win_rate (percent values). - revenue_volatility: standard deviation of monthly_revenue; activity_consistency: standard deviation of monthly_deals_created. - recent_active_months: count of monthly rows in the last 3 calendar months (relative to current_date), inclusive. - Territory and segment analysis per owner from all deals: - primary_deal_segment: most frequent deal_size_category; ties break by ascending category label. - segments_covered: count distinct deal_size_category. - enterprise/large/medium/small_revenue: sum won deal_amount within each named deal_size_category. - enterprise_win_rate / large_deal_win_rate: if decided deals in the segment exist, compute 100 × (won / decided); otherwise 0. - Rankings and percentiles from owner metrics: - revenue_rank: best-to-worst by total_won_revenue; win_rate_rank: best-to-worst by win_rate_percentage; volume_rank: best-to-worst by won_deals. - efficiency_rank: best-to-worst by avg_won_cycle_time, treating NULL as 999. - revenue_percentile / win_rate_percentile / volume_percentile: percentile position (0–100) across all reps using ascending order of each metric; peers share the same percentile. - efficiency_percentile: percentile position (0–100) using descending order of avg_won_cycle_time, treating NULL as 999 (longer cycles → higher percentile). - overall_performance_score: weighted sum of these percentiles (revenue 40%, win rate 25%, volume 20%, efficiency 15%), then scaled by ×100 to a 0–10,000 range. - Ties in ranks are resolved by the database’s implicit peer order. - Join rankings to trends and territory by owner_id (cast trend/territory owner_id to VARCHAR); unmatched trend/territory values remain NULL. - Derivations: - revenue_trend_percentage: if prior_6m_avg_revenue > 0 and recent_6m_avg_revenue is not NULL, compute 100 × (recent - prior) / prior; else NULL. - win_rate_trend_points: if prior_6m_avg_win_rate > 0 and recent_6m_avg_win_rate is not NULL, compute recent - prior; else NULL. - performance_tier: >=80 Top Performer; >=60 High Performer; >=40 Core Performer; >=20 Developing Performer; else Needs Improvement. - performance_trend: >=20 Strong Growth; >=5 Steady Growth; >=-5 Stable; >=-20 Declining; else Significant Decline (NULLs map to the else). - sales_specialization: Enterprise Specialist if enterprise_revenue strictly exceeds (large + medium + small); Large Deal Specialist if large_revenue strictly exceeds (enterprise + medium + small); else if segments_covered >= 3 then Generalist; otherwise Focused Seller. - development_focus (first-match order): low win rate + long cycle → Focus on Qualification and Process; low win rate → Improve Win Rate; very long cycle → Accelerate Sales Cycle; few wins → Increase Activity Volume; declining revenue trend → Address Performance Decline; else Maintain Current Performance. - activity_level (first-match): Highly Active (recent_active_months >= 3 and total_deals >= 10); Active (recent_active_months >= 2 and total_deals >= 5); Moderately Active (recent_active_months >= 1); else Low Activity. - pipeline_health_status: compare current_pipeline_value to total_won_revenue thresholds: >=2× Strong Pipeline; >=1× Healthy Pipeline; >=0.5× Adequate Pipeline; else Weak Pipeline. - Output rows are ordered by overall_performance_score descending.'
      columns:
      - name: owner_id
        data_type: VARCHAR
        description: Sales rep identifier; grouping key; exactly one output row per owner_id with total_deals > 0
        tests:
        - not_null
        - unique
      - name: owner_name
        data_type: VARCHAR
        description: Sales rep name from owner metrics; passed through from source (may be NULL)
      - name: owner_email
        data_type: VARCHAR
        description: Sales rep email from owner metrics; passed through from source (may be NULL)
      - name: total_deals
        data_type: BIGINT
        description: Total number of deals attributed to the rep from owner metrics; used for filters and activity_level thresholds
      - name: won_deals
        data_type: BIGINT
        description: Count of won deals from owner metrics; used for volume_rank and development_focus
      - name: total_won_revenue
        data_type: DECIMAL(38,2)
        description: Sum of deal_amount for won deals from owner metrics; basis for revenue_rank, revenue_percentile, and pipeline health thresholds
      - name: win_rate_percentage
        data_type: DOUBLE
        description: Overall win rate percentage (0–100) from owner metrics; used for win_rate_rank and percentiles
      - name: avg_won_cycle_time
        data_type: DOUBLE
        description: Average days to close for won deals from owner metrics; NULL permitted; for ranking, NULL treated as 999
      - name: current_pipeline_value
        data_type: DECIMAL(38,2)
        description: Current open pipeline value from owner metrics (alias of pipeline_value); used for pipeline_health_status thresholds
      - name: enterprise_win_rate
        data_type: DOUBLE
        description: Enterprise (100K+) segment win rate in percent; if no decided enterprise deals then 0; computed as 100×won/decided
      - name: large_deal_win_rate
        data_type: DOUBLE
        description: Large (50K-100K) segment win rate in percent; if no decided large deals then 0; computed as 100×won/decided
      - name: enterprise_revenue
        data_type: DECIMAL(38,2)
        description: Sum of won deal_amount in Enterprise (100K+) segment; NULL if no territory data joined
      - name: large_revenue
        data_type: DECIMAL(38,2)
        description: Sum of won deal_amount in Large (50K-100K) segment; NULL if no territory data joined
      - name: medium_revenue
        data_type: DECIMAL(38,2)
        description: Sum of won deal_amount in Medium (10K-50K) segment; NULL if no territory data joined
      - name: small_revenue
        data_type: DECIMAL(38,2)
        description: Sum of won deal_amount in Small (<10K) segment; NULL if no territory data joined
      - name: revenue_rank
        data_type: BIGINT
        description: Integer rank by total_won_revenue descending across all reps; 1 is highest revenue; ties resolved by peer order
      - name: win_rate_rank
        data_type: BIGINT
        description: Integer rank by win_rate_percentage descending across all reps; 1 is highest win rate; ties resolved by peer order
      - name: volume_rank
        data_type: BIGINT
        description: Integer rank by won_deals descending across all reps; 1 is most wins; ties resolved by peer order
      - name: efficiency_rank
        data_type: BIGINT
        description: Integer rank by avg_won_cycle_time ascending, treating NULL as 999; 1 is shortest cycle; ties resolved by peer order
      - name: revenue_percentile
        data_type: DOUBLE
        description: Percentile (0–100) using ascending order of total_won_revenue; peers share the same percentile
      - name: win_rate_percentile
        data_type: DOUBLE
        description: Percentile (0–100) using ascending order of win_rate_percentage; peers share the same percentile
      - name: volume_percentile
        data_type: DOUBLE
        description: Percentile (0–100) using ascending order of won_deals; peers share the same percentile
      - name: efficiency_percentile
        data_type: DOUBLE
        description: Percentile (0–100) using descending order of avg_won_cycle_time with NULL treated as 999; higher values indicate longer cycles
      - name: overall_performance_score
        data_type: DOUBLE
        description: Weighted sum of percentiles (revenue 40%, win rate 25%, volume 20%, efficiency 15%) scaled by ×100; range 0–10,000
      - name: performance_tier
        data_type: VARCHAR
        description: 'Tier by overall_performance_score: >=80 Top, >=60 High, >=40 Core, >=20 Developing, else Needs Improvement'
      - name: sales_specialization
        data_type: VARCHAR
        description: Enterprise Specialist if enterprise_revenue > (large + medium + small), Large Deal Specialist if large_revenue > (enterprise + medium + small), else Generalist if segments_covered >= 3, otherwise Focused Seller
      - name: development_focus
        data_type: VARCHAR
        description: 'First-match guidance: low win rate + long cycle → process; low win rate → improve; very long cycle → accelerate; few wins → increase volume; declining trend → address; else maintain'
      - name: pipeline_health_status
        data_type: VARCHAR
        description: 'Pipeline health by current_pipeline_value versus total_won_revenue: >=2x Strong, >=1x Healthy, >=0.5x Adequate, else Weak'
      - name: primary_deal_segment
        data_type: VARCHAR
        description: Most frequent deal_size_category with tie-break by ascending label; NULL if no deal data
      - name: segments_covered
        data_type: BIGINT
        description: Count of distinct deal_size_category values across the rep’s deals; NULL if no deal data
      - name: activity_level
        data_type: VARCHAR
        description: 'Activity classification by recent_active_months and total_deals with ordered thresholds: Highly Active, Active, Moderately Active, or Low Activity'
      - name: activity_consistency
        data_type: DOUBLE
        description: Standard deviation of monthly_deals_created; higher implies more variability; may be NULL with limited data
      - name: recent_active_months
        data_type: BIGINT
        description: Count of months in the last 3-month window with any monthly activity row (based on created_date); integer >= 0
      - name: performance_trend
        data_type: VARCHAR
        description: 'Trend label from revenue_trend_percentage: >=20 Strong Growth, >=5 Steady Growth, >=-5 Stable, >=-20 Declining, else Significant Decline (NULLs map to else)'
      - name: revenue_trend_percentage
        data_type: DOUBLE
        description: Percent change between recent_6m_avg_revenue and prior_6m_avg_revenue; NULL if prior <= 0 or recent is NULL
      - name: win_rate_trend_points
        data_type: DOUBLE
        description: Difference in percentage points between recent_6m_avg_win_rate and prior_6m_avg_win_rate; NULL if prior <= 0 or recent is NULL
      - name: revenue_volatility
        data_type: DOUBLE
        description: Standard deviation of monthly_revenue; may be NULL with limited data
      - name: recent_6m_avg_revenue
        data_type: DOUBLE
        description: Average monthly_revenue where month_index >= current_month_index - 6; includes months with zero revenue if present; NULL if no months
      - name: prior_6m_avg_revenue
        data_type: DOUBLE
        description: Average monthly_revenue where month_index is between current_month_index - 12 and current_month_index - 7; NULL if no months
      - name: recent_6m_avg_win_rate
        data_type: DOUBLE
        description: Average monthly_win_rate (percent) where month_index >= current_month_index - 6; NULL if no months
      - name: prior_6m_avg_win_rate
        data_type: DOUBLE
        description: Average monthly_win_rate (percent) where month_index is between current_month_index - 12 and current_month_index - 7; NULL if no months
```

### 逐点结论

#### enterprise_revenue

非原因；**Unstated Choice**；把握高。

P：enterprise_revenue在没有符合条件的won deal时返回NULL而非0。契约给分类范围但未规定空条件求和的默认值；两种聚合写法合理。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 200 | 200 | 862 | 862 |
| L1 | 200 | 200 | 862 | 862 |
| L2 | 200 | 200 | 701 | 701 |
| L3 | 200 | 200 | 701 | 701 |

重跑：`records/039_checks/025_evidence_impl-010_hubspot__sales_rep_performance.json` / `enterprise_revenue`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

标记：存在未确立的前提，但不是判错原因。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_rep_performance.sql` / `SQL.text`（sql）：

```text
sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Enterprise (100K+)')
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### large_revenue

参与；**Unstated Choice**；把握高。

P：large_revenue在没有符合条件的won deal时返回NULL而非0。契约给分类范围但未规定空条件求和的默认值；两种聚合写法合理。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 200 | 199 | 862 | 788 |
| L1 | 200 | 199 | 862 | 788 |
| L2 | 200 | 199 | 701 | 627 |
| L3 | 200 | 199 | 701 | 627 |

重跑：`records/039_checks/025_evidence_impl-010_hubspot__sales_rep_performance.json` / `large_revenue`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_rep_performance.sql` / `SQL.text`（sql）：

```text
sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Large (50K-100K)')
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### medium_revenue

参与；**Unstated Choice**；把握高。

P：medium_revenue在没有符合条件的won deal时返回NULL而非0。契约给分类范围但未规定空条件求和的默认值；两种聚合写法合理。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 200 | 200 | 862 | 754 |
| L1 | 200 | 200 | 862 | 754 |
| L2 | 200 | 199 | 701 | 593 |
| L3 | 200 | 199 | 701 | 593 |

重跑：`records/039_checks/025_evidence_impl-010_hubspot__sales_rep_performance.json` / `medium_revenue`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_rep_performance.sql` / `SQL.text`（sql）：

```text
sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Medium (10K-50K)')
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### small_revenue

参与；**Unstated Choice**；把握高。

P：small_revenue在没有符合条件的won deal时返回NULL而非0。契约给分类范围但未规定空条件求和的默认值；两种聚合写法合理。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 200 | 200 | 862 | 691 |
| L1 | 200 | 200 | 862 | 691 |
| L2 | 200 | 200 | 701 | 530 |
| L3 | 200 | 200 | 701 | 530 |

重跑：`records/039_checks/025_evidence_impl-010_hubspot__sales_rep_performance.json` / `small_revenue`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_rep_performance.sql` / `SQL.text`（sql）：

```text
sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Small (<10K)')
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### volume_rank_peer_order

主要；**其他**；把握高。

契约允许同值任意排序；025确认peer组的内容和rank集合一致。直接投影已有rank与重新分配同值rank产生差异，不能据gold序号判Intent。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 200 | 199 | 862 | 684 |
| L1 | 200 | 199 | 862 | 684 |
| L2 | 200 | 198 | 701 | 523 |
| L3 | 200 | 198 | 701 | 523 |

重跑：`records/039_checks/025_evidence_impl-010_hubspot__sales_rep_performance.json` / `volume_rank_peer_order`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_rep_performance.sql` / `SQL.text`（sql）：

```text
row_number() over(order by won_deals desc)
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### efficiency_rank_peer_order

参与；**其他**；把握高。

契约允许同值任意排序；025确认peer组的内容和rank集合一致。直接投影已有rank与重新分配同值rank产生差异，不能据gold序号判Intent。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 200 | 200 | 862 | 858 |
| L1 | 200 | 200 | 862 | 858 |
| L2 | 200 | 200 | 701 | 697 |
| L3 | 200 | 200 | 701 | 697 |

重跑：`records/039_checks/025_evidence_impl-010_hubspot__sales_rep_performance.json` / `efficiency_rank_peer_order`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_rep_performance.sql` / `SQL.text`（sql）：

```text
row_number() over(order by coalesce(avg_won_cycle_time,999))
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### win_rate_rank_projection

参与；**其他**；把握高。

契约允许同值任意排序；025确认peer组的内容和rank集合一致。直接投影已有rank与重新分配同值rank产生差异，不能据gold序号判Intent。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 200 | 200 | 862 | 698 |
| L1 | 200 | 200 | 862 | 698 |
| L2 | 200 | 199 | 701 | 537 |
| L3 | 200 | 199 | 701 | 537 |

重跑：`records/039_checks/025_evidence_impl-010_hubspot__sales_rep_performance.json` / `win_rate_rank_projection`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_rep_performance.sql` / `SQL.text`（sql）：

```text
revenue_rank,win_rate_rank,volume_rank,efficiency_rank,
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### recent_month_window

非原因；**Intent Misreading**；把握高。

P：最近月份窗口是当前月及前2月。契约给出的边界是当前月减3个月，含边界；范围算法已有明文。该数据单改不减少规模。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 200 | 200 | 862 | 862 |
| L1 | 200 | 200 | 862 | 862 |
| L2 | 200 | 200 | 701 | 701 |
| L3 | 200 | 200 | 701 | 701 |

重跑：`records/039_checks/025_evidence_impl-010_hubspot__sales_rep_performance.json` / `recent_month_window`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

标记：存在未确立的前提，但不是判错原因。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_rep_performance.sql` / `SQL.text`（sql）：

```text
with om as (select * from intermediate.int_hubspot__owner_performance_metrics where total_deals>0), d as (select *,year(created_date) y,month(created_date) m from intermediate.int_hubspot__deal_performance_metrics), monthly as (select owner_id,y performance_year,m performance_month,y*12+m month_index,count(distinct deal_id) monthly_deals_created,sum(case when deal_status='Won' then 1 else 0 end) monthly_deals_won,sum(case when deal_status='Won' then deal_amount else 0 end) monthly_revenue,sum(case when deal_status='Open' then deal_amount else 0 end) monthly_pipeline_added,100.0*count(*) filter(where deal_status='Won')/nullif(count(*) filter(where deal_status in('Won','Lost')),0) monthly_win_rate,avg(deal_cycle_time_days) filter(where deal_status='Won') monthly_avg_cycle_time from d where created_date is not null group by 1,2,3), trends as (select owner_id,avg(monthly_revenue) filter(where month_index>=year(current_date)*12+month(current_date)-6) recent_6m_avg_revenue,avg(monthly_revenue) filter(where month_index between year(current_date)*12+month(current_date)-12 and year(current_date)*12+month(current_date)-7) prior_6m_avg_revenue,avg(monthly_win_rate) filter(where month_index>=year(current_date)*12+month(current_date)-6) recent_6m_avg_win_rate,avg(monthly_win_rate) filter(where month_index between year(current_date)*12+month(current_date)-12 and year(current_date)*12+month(current_date)-7) prior_6m_avg_win_rate,stddev_samp(monthly_revenue) revenue_volatility,stddev_samp(monthly_deals_created) activity_consistency,count(*) filter(where month_index>=year(current_date)*12+month(current_date)-2) recent_active_months from monthly group by 1), seg as (select owner_id,mode() within group(order by deal_size_category) primary_deal_segment,count(distinct deal_size_category)::bigint segments_covered,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Enterprise (100K+)') enterprise_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Large (50K-100K)') large_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Medium (10K-50K)') medium_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Small (<10K)') small_revenue from d group by 1), ranks as (select *,row_number() over(order by total_won_revenue desc) revenue_rank,row_number() over(order by win_rate_percentage desc) win_rate_rank,row_number() over(order by won_deals desc) volume_rank,row_number() over(order by coalesce(avg_won_cycle_time,999)) efficiency_rank,100*percent_rank() over(order by total_won_revenue) revenue_percentile,100*percent_rank() over(order by win_rate_percentage) win_rate_percentile,100*percent_rank() over(order by won_deals) volume_percentile,100*percent_rank() over(order by coalesce(avg_won_cycle_time,999) desc) efficiency_percentile from om), joined as (select r.*,s.primary_deal_segment,s.segments_covered,s.enterprise_revenue,s.large_revenue,s.medium_revenue,s.small_revenue,t.activity_consistency,t.recent_active_months,t.revenue_volatility,t.recent_6m_avg_revenue,t.prior_6m_avg_revenue,t.recent_6m_avg_win_rate,t.prior_6m_avg_win_rate,case when t.prior_6m_avg_revenue>0 then 100*(t.recent_6m_avg_revenue-t.prior_6m_avg_revenue)/t.prior_6m_avg_revenue end revenue_trend_percentage,case when t.prior_6m_avg_win_rate>0 then t.recent_6m_avg_win_rate-t.prior_6m_avg_win_rate end win_rate_trend_points from ranks r left join seg s on cast(r.owner_id as varchar)=cast(s.owner_id as varchar) left join trends t on cast(r.owner_id as varchar)=cast(t.owner_id as varchar)), scored as (select *,revenue_percentile*40+win_rate_percentile*25+volume_percentile*20+efficiency_percentile*15 overall_performance_score from joined) select owner_id,owner_name,owner_email,total_deals,won_deals,total_won_revenue,win_rate_percentage,avg_won_cycle_time,pipeline_value current_pipeline_value,enterprise_win_rate,large_deal_win_rate,enterprise_revenue,large_revenue,medium_revenue,small_revenue,revenue_rank,win_rate_rank,volume_rank,efficiency_rank,revenue_percentile,win_rate_percentile,volume_percentile,efficiency_percentile,overall_performance_score,case when overall_performance_score>=80 then 'Top Performer' when overall_performance_score>=60 then 'High Performer' when overall_performance_score>=40 then 'Core Performer' when overall_performance_score>=20 then 'Developing Performer' else 'Needs Improvement' end performance_tier,case when enterprise_revenue>coalesce(large_revenue,0)+coalesce(medium_revenue,0)+coalesce(small_revenue,0) then 'Enterprise Specialist' when large_revenue>coalesce(enterprise_revenue,0)+coalesce(medium_revenue,0)+coalesce(small_revenue,0) then 'Large Deal Specialist' when segments_covered>=3 then 'Generalist' else 'Focused Seller' end sales_specialization,case when win_rate_percentage<15 and avg_won_cycle_time>90 then 'Focus on Qualification and Process' when win_rate_percentage<15 then 'Improve Win Rate' when avg_won_cycle_time>120 then 'Accelerate Sales Cycle' when won_deals<5 then 'Increase Activity Volume' when revenue_trend_percentage< -5 then 'Address Performance Decline' else 'Maintain Current Performance' end development_focus,case when pipeline_value>=2*total_won_revenue then 'Strong Pipeline' when pipeline_value>=total_won_revenue then 'Healthy Pipeline' when pipeline_value>=0.5*total_won_revenue then 'Adequate Pipeline' else 'Weak Pipeline' end pipeline_health_status,primary_deal_segment,segments_covered,case when recent_active_months>=3 and total_deals>=10 then 'Highly Active' when recent_active_months>=2 and total_deals>=5 then 'Active' when recent_active_months>=1 then 'Moderately Active' else 'Low Activity' end activity_level,activity_consistency,recent_active_months,case when revenue_trend_percentage>=20 then 'Strong Growth' when revenue_trend_percentage>=5 then 'Steady Growth' when revenue_trend_percentage>=-5 then 'Stable' when revenue_trend_percentage>=-20 then 'Declining' else 'Significant Decline' end performance_trend,revenue_trend_percentage,win_rate_trend_points,revenue_volatility,recent_6m_avg_revenue,prior_6m_avg_revenue,recent_6m_avg_win_rate,prior_6m_avg_win_rate from scored order by overall_performance_score desc

```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml`，行[1797, 1931]；材料包 `records/021_packages/021_impl-010_hubspot__sales_rep_performance.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_rep_performance.sql`；SHA-256 `ab6365e72caaf455ecfe91dd2f6bf33c7b5b7a3caa49f2d9b978ecaa34ab59e2`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/73.json` / event 73。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共0条，新核实0条（总数≤5）。诊断/单改不计作核实查询：


## 不确定或没查到的（含规则问题）

- 025使用threads=1的共同基线200行/862格，不能混用旧865格。stddev/stddev_samp别名、未被最终投影使用的rank探针没有独立错误，不重复记点。
- 025明确此表在CS下不受raw版本差异影响；本次上游均用gold，原021“不可评估”不再使用。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
