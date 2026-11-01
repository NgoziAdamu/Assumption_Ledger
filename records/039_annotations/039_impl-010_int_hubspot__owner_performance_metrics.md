# impl-010_int_hubspot__owner_performance_metrics（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**其他**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`O`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 199, "cell_scale": 511}, "L1": {"row_scale": 199, "cell_scale": 511}, "L2": {"row_scale": 198, "cell_scale": 423}, "L3": {"row_scale": 198, "cell_scale": 423}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| deals_won_rank_peer_order | 其他 | 主要 | 15 | 175 | 4 |
| cycle_time_rank_peer_order | 其他 | 参与 | 0 | 2 | 4 |
| win_rate_rank_peer_order | 其他 | 非原因 | -1 | 152 | 4 |
| score_arithmetic | 其他 | 参与 | 1 | 88 | 4 |
| win_rate_percentage | Intent Misreading | 非原因 | 0 | 0 | 4 |
| enterprise_win_rate | Intent Misreading | 非原因 | 0 | 0 | 4 |
| large_deal_win_rate | Intent Misreading | 参与 | 0 | 74 | 4 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: int_hubspot__owner_performance_metrics
      schema: intermediate
      description: Sales owner performance metrics with counts, revenue, cycle times, rankings, percentiles, and rule-based classifications
      grain: One row per owner_id with at least one deal
      source_models:
      - intermediate.int_hubspot__deals_enhanced (owner_id, amount, pipeline_stage_label, pipeline_label, deal_pipeline_stage_id, created_date, closed_date)
      - intermediate.int_hubspot__owners_enhanced (owner_id, owner_full_name, owner_email_address)
      business_logic: '- Start from intermediate.int_hubspot__deals_enhanced, keeping only deals with a non-NULL owner_id. - For each deal, derive: - deal_status: Won if closed_date is present and amount > 0; Lost if closed_date is present and amount = 0; Open if closed_date is missing; otherwise Unknown. - deal_size_category: Enterprise (100K+) if amount >= 100000; Large (50K-100K) if amount >= 50000; Medium (10K-50K) if amount >= 10000; Small (<10K) if amount > 0; else No Value. - deal_cycle_time_days: number of days between created_date and closed_date when both exist; otherwise NULL. - Left join to intermediate.int_hubspot__owners_enhanced on owner_id to bring owner_full_name and owner_email_address. - Aggregate by owner_id, owner_name, owner_email: - Counts: total_deals (all deals); won_deals (status Won); lost_deals (status Lost); open_deals (status Open). - Win rate: wins divided by (wins + losses) times 100; if there are no closed (Won/Lost) deals then 0. - Revenue: total_won_revenue = sum of amounts from Won deals (non-won contribute 0; NULL amounts are ignored); avg_won_deal_size = average amount for Won deals (NULL if none); pipeline_value = sum of amounts from Open deals (non-open contribute 0; NULL amounts are ignored). - Velocity: avg_won_cycle_time = average cycle days for Won; avg_lost_cycle_time = average cycle days for Lost (both NULL if none). - Dates: first_deal_date = earliest created_date; latest_deal_date = latest created_date; last_won_date = latest close_date among Won. - Size distribution: counts of Enterprise, Large, Medium, and Small as defined above. - Size-specific win rates: within Enterprise and Large respectively, wins divided by (wins + losses) times 100; if no closed deals in that size then 0. - Keep only owners with total_deals > 0. - Compute window metrics across all remaining owners (no partitions): - revenue_rank: position when ordering by total_won_revenue descending (1 = highest; ties break arbitrarily). - win_rate_rank: position when ordering by win_rate_percentage descending (1 = highest; ties break arbitrarily). - deals_won_rank: position when ordering by won_deals descending (1 = highest; ties break arbitrarily). - cycle_time_rank: position when ordering by average won cycle time ascending; missing averages are treated as 999 days (1 = shortest). - revenue_percentile: percentile rank scaled 0–100 by total_won_revenue (lowest = 0, highest = 100). - win_rate_percentile: percentile rank scaled 0–100 by win_rate_percentage (lowest = 0, highest = 100). - volume_percentile: percentile rank scaled 0–100 by won_deals (lowest = 0, highest = 100). - efficiency_percentile: percentile rank scaled 0–100 by average won cycle time in descending order with missing treated as 999 (0 = slowest or NULL, 100 = fastest). - overall_performance_score: take the percentile ranks (0–1) for revenue, win rate, won deals, and cycle time (faster = higher), weight them 40/25/20/15 respectively, sum them, then multiply by 100; the score ranges from 0 to 10000. - Classifications: - performance_tier: Top Performer if score >= 80; High Performer if >= 60; Core Performer if >= 40; Developing Performer if >= 20; else Needs Improvement. - sales_specialization: Enterprise Specialist if enterprise_deals > (large_deals + medium_deals + small_deals); Large Deal Specialist if large_deals > (enterprise_deals + medium_deals + small_deals); Generalist if the total across size categories >= 3; else Focused Seller. - development_focus (first match applies): if win_rate_percentage < 15 and avg_won_cycle_time > 90 then Focus on Qualification and Process; else if win_rate_percentage < 15 then Improve Win Rate; else if avg_won_cycle_time > 120 then Accelerate Sales Cycle; else if won_deals < 5 then Increase Activity Volume; else Maintain Current Performance. - pipeline_health_status (evaluated in order): Strong Pipeline if pipeline_value >= 2 × total_won_revenue; Healthy Pipeline if >= total_won_revenue; Adequate Pipeline if >= 0.5 × total_won_revenue; else Weak Pipeline.'
      columns:
      - name: owner_id
        data_type: VARCHAR
        description: Sales owner identifier and grouping key; one row per owner with at least one deal
        tests:
        - not_null
        - unique
      - name: owner_name
        data_type: VARCHAR
        description: Owner full name from owners_enhanced; may be NULL if no match
      - name: owner_email
        data_type: VARCHAR
        description: Owner email from owners_enhanced; may be NULL if no match
      - name: total_deals
        data_type: BIGINT
        description: Total number of the owner's deals across all statuses
      - name: won_deals
        data_type: BIGINT
        description: Number of closed deals with amount > 0
      - name: lost_deals
        data_type: BIGINT
        description: Number of closed deals with amount = 0
      - name: open_deals
        data_type: BIGINT
        description: Number of deals with no closed_date
      - name: win_rate_percentage
        data_type: DOUBLE
        description: Wins divided by (wins + losses) times 100; returns 0 if there are no closed deals; no rounding
      - name: total_won_revenue
        data_type: DECIMAL(38,2)
        description: Total amount from won deals; non-won contribute 0 and NULL amounts are ignored; 2-decimal scale
      - name: avg_won_deal_size
        data_type: DOUBLE
        description: Average amount for won deals; excludes NULLs; NULL if no won deals
      - name: pipeline_value
        data_type: DECIMAL(38,2)
        description: Total amount from open deals; non-open contribute 0 and NULL amounts are ignored; 2-decimal scale
      - name: avg_won_cycle_time
        data_type: DOUBLE
        description: Average days from created to closed for won deals; NULL if none
      - name: avg_lost_cycle_time
        data_type: DOUBLE
        description: Average days from created to closed for lost deals; NULL if none
      - name: first_deal_date
        data_type: TIMESTAMP
        description: Earliest created_date across the owner's deals; NULL if all created_date values are NULL
      - name: latest_deal_date
        data_type: TIMESTAMP
        description: Latest created_date across the owner's deals; NULL if all created_date values are NULL
      - name: last_won_date
        data_type: TIMESTAMP
        description: Most recent close_date among won deals; NULL if no won deals
      - name: enterprise_deals
        data_type: BIGINT
        description: Number of deals with amount >= 100000
      - name: large_deals
        data_type: BIGINT
        description: Number of deals with 50000 <= amount < 100000
      - name: medium_deals
        data_type: BIGINT
        description: Number of deals with 10000 <= amount < 50000
      - name: small_deals
        data_type: BIGINT
        description: Number of deals with 0 < amount < 10000
      - name: enterprise_win_rate
        data_type: DOUBLE
        description: Within Enterprise size, wins divided by (wins + losses) times 100; returns 0 if no closed Enterprise deals
      - name: large_deal_win_rate
        data_type: DOUBLE
        description: Within Large size, wins divided by (wins + losses) times 100; returns 0 if no closed Large deals
      - name: revenue_rank
        data_type: BIGINT
        description: Position when ordering all owners by total won revenue descending; 1 is highest; ties break arbitrarily
      - name: win_rate_rank
        data_type: BIGINT
        description: Position when ordering all owners by win rate percentage descending; 1 is highest; ties break arbitrarily
      - name: deals_won_rank
        data_type: BIGINT
        description: Position when ordering all owners by number of won deals descending; 1 is highest; ties break arbitrarily
      - name: cycle_time_rank
        data_type: BIGINT
        description: Position when ordering by average won cycle time ascending; 1 is shortest; missing averages treated as 999 days; ties break arbitrarily
      - name: revenue_percentile
        data_type: DOUBLE
        description: Percentile rank scaled 0–100 by total won revenue; 0 = lowest, 100 = highest
      - name: win_rate_percentile
        data_type: DOUBLE
        description: Percentile rank scaled 0–100 by win rate percentage; 0 = lowest, 100 = highest
      - name: volume_percentile
        data_type: DOUBLE
        description: Percentile rank scaled 0–100 by number of won deals; 0 = lowest, 100 = highest
      - name: efficiency_percentile
        data_type: DOUBLE
        description: Percentile rank scaled 0–100 by average won cycle time in descending order with missing treated as 999; 0 = slowest/NULL, 100 = fastest
      - name: overall_performance_score
        data_type: DOUBLE
        description: Weighted sum of percentile ranks (0–1) for revenue, win rate, won deals, and cycle time (faster is higher) with weights 40/25/20/15, multiplied by 100; range 0–10000
      - name: performance_tier
        data_type: VARCHAR
        description: 'Tier from overall_performance_score: >=80 Top Performer; >=60 High Performer; >=40 Core Performer; >=20 Developing Performer; else Needs Improvement'
      - name: sales_specialization
        data_type: VARCHAR
        description: Enterprise Specialist if enterprise_deals > (large+medium+small); Large Deal Specialist if large_deals > (enterprise+medium+small); Generalist if total size-deal count >= 3; else Focused Seller
      - name: development_focus
        data_type: VARCHAR
        description: 'Priority rules: if win_rate_percentage < 15 and avg_won_cycle_time > 90 then Focus on Qualification and Process; else if win_rate_percentage < 15 then Improve Win Rate; else if avg_won_cycle_time > 120 then Accelerate Sales Cycle; else if won_deals < 5 then Increase Activity Volume; else Maintain Current Performance'
      - name: pipeline_health_status
        data_type: VARCHAR
        description: 'Pipeline status by comparing pipeline_value to total_won_revenue: >=2x Strong; >=1x Healthy; >=0.5x Adequate; else Weak'
```

### 逐点结论

#### deals_won_rank_peer_order

主要；**其他**；把握高。

契约允许ROW_NUMBER并列任意顺序；025诊断并列组与rank多重集相同，差异在同值行被分配的序号。该替换仅用于对齐gold同值次序，不要求agent另加tie-breaker。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 199 | 184 | 511 | 336 |
| L1 | 199 | 184 | 511 | 336 |
| L2 | 198 | 176 | 423 | 248 |
| L3 | 198 | 176 | 423 | 248 |

重跑：`records/039_checks/025_evidence_impl-010_int_hubspot__owner_performance_metrics.json` / `deals_won_rank_peer_order`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/intermediate/int_hubspot__owner_performance_metrics.sql` / `SQL.text`（sql）：

```text
row_number() over(order by won_deals desc)
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### cycle_time_rank_peer_order

参与；**其他**；把握高。

契约允许ROW_NUMBER并列任意顺序；025诊断并列组与rank多重集相同，差异在同值行被分配的序号。该替换仅用于对齐gold同值次序，不要求agent另加tie-breaker。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 199 | 199 | 511 | 509 |
| L1 | 199 | 199 | 511 | 509 |
| L2 | 198 | 198 | 423 | 421 |
| L3 | 198 | 198 | 423 | 421 |

重跑：`records/039_checks/025_evidence_impl-010_int_hubspot__owner_performance_metrics.json` / `cycle_time_rank_peer_order`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/intermediate/int_hubspot__owner_performance_metrics.sql` / `SQL.text`（sql）：

```text
row_number() over(order by coalesce(avg_won_cycle_time,999))
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### win_rate_rank_peer_order

非原因；**其他**；把握高。

契约允许ROW_NUMBER并列任意顺序；025诊断并列组与rank多重集相同，差异在同值行被分配的序号。该替换仅用于对齐gold同值次序，不要求agent另加tie-breaker。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 199 | 200 | 511 | 359 |
| L1 | 199 | 200 | 511 | 359 |
| L2 | 198 | 195 | 423 | 271 |
| L3 | 198 | 195 | 423 | 271 |

重跑：`records/039_checks/025_evidence_impl-010_int_hubspot__owner_performance_metrics.json` / `win_rate_rank_peer_order`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

标记：单改未产生行优先口径的净改善，不记参与。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/intermediate/int_hubspot__owner_performance_metrics.sql` / `SQL.text`（sql）：

```text
row_number() over(order by win_rate_percentage desc nulls last)
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### score_arithmetic

参与；**其他**；把握高。

相同契约评分公式的浮点乘除结合顺序导致末位差异；宽松层及025诊断确认。不是新业务算法。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 199 | 198 | 511 | 423 |
| L1 | 199 | 198 | 511 | 423 |
| L2 | 198 | 198 | 423 | 423 |
| L3 | 198 | 198 | 423 | 423 |

重跑：`records/039_checks/025_evidence_impl-010_int_hubspot__owner_performance_metrics.json` / `score_arithmetic`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/intermediate/int_hubspot__owner_performance_metrics.sql` / `SQL.text`（sql）：

```text
revenue_percentile*40+win_rate_percentile*25+volume_percentile*20+efficiency_percentile*15
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### win_rate_percentage

非原因；**Intent Misreading**；把握高。

P：win_rate_percentage零分母可留NULL。契约对无对应deals的win rate明确返回0；不是未规定NULL策略。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 199 | 199 | 511 | 511 |
| L1 | 199 | 199 | 511 | 511 |
| L2 | 198 | 198 | 423 | 423 |
| L3 | 198 | 198 | 423 | 423 |

重跑：`records/039_checks/025_evidence_impl-010_int_hubspot__owner_performance_metrics.json` / `win_rate_percentage`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

标记：存在未确立的前提，但不是判错原因。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/intermediate/int_hubspot__owner_performance_metrics.sql` / `SQL.text`（sql）：

```text
100.0*count(*) filter(where status='Won')/nullif(count(*) filter(where status in ('Won','Lost')),0) win_rate_percentage
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### enterprise_win_rate

非原因；**Intent Misreading**；把握高。

P：enterprise_win_rate零分母可留NULL。契约对无对应deals的win rate明确返回0；不是未规定NULL策略。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 199 | 199 | 511 | 511 |
| L1 | 199 | 199 | 511 | 511 |
| L2 | 198 | 198 | 423 | 423 |
| L3 | 198 | 198 | 423 | 423 |

重跑：`records/039_checks/025_evidence_impl-010_int_hubspot__owner_performance_metrics.json` / `enterprise_win_rate`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

标记：存在未确立的前提，但不是判错原因。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/intermediate/int_hubspot__owner_performance_metrics.sql` / `SQL.text`（sql）：

```text
100.0*count(*) filter(where size='Enterprise' and status='Won')/nullif(count(*) filter(where size='Enterprise' and status in('Won','Lost')),0) enterprise_win_rate
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### large_deal_win_rate

参与；**Intent Misreading**；把握高。

P：large_deal_win_rate零分母可留NULL。契约对无对应deals的win rate明确返回0；不是未规定NULL策略。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 199 | 199 | 511 | 437 |
| L1 | 199 | 199 | 511 | 437 |
| L2 | 198 | 195 | 423 | 349 |
| L3 | 198 | 195 | 423 | 349 |

重跑：`records/039_checks/025_evidence_impl-010_int_hubspot__owner_performance_metrics.json` / `large_deal_win_rate`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/intermediate/int_hubspot__owner_performance_metrics.sql` / `SQL.text`（sql）：

```text
100.0*count(*) filter(where size='Large' and status='Won')/nullif(count(*) filter(where size='Large' and status in('Won','Lost')),0) large_deal_win_rate
```

否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml`，行[1024, 1140]；材料包 `records/021_packages/021_impl-010_int_hubspot__owner_performance_metrics.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/intermediate/int_hubspot__owner_performance_metrics.sql`；SHA-256 `95e15c6279c4d9059fbb12e403c1b29145a06cb12434c32bdb2a136b1a8088b6`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/73.json` / event 73。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共0条，新核实0条（总数≤5）。诊断/单改不计作核实查询：


## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。
- 025明确此表在CS下不受raw版本差异影响；本次上游均用gold，原021“不可评估”不再使用。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
