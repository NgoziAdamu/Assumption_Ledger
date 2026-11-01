# impl-005_google_ads__customer_acquisition_analysis（037 正式批次）

主要原因：**Unstated Choice**；把握：中。019旧主要原因原样保留：`A`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__customer_acquisition_analysis.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/47.json`，finish 47 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/google_ads.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-005_google_ads__customer_acquisition_analysis.json`；037补充：`records/037_checks/`。

## 逐点标注

### cohort_avg_cac

- 类别：Intent Misreading；角色：非原因；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约cohort均值使用已舍入的CAC输入，agent使用未舍入表达式；影响计算链，单改无净改善。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: cohort_avg_cac
>         data_type: DOUBLE
>         description: Average running CAC within the same acquisition_cohort and advertising_channel_type; rows with zero cumulative_conversions are excluded; not rounded

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__customer_acquisition_analysis.sql`，第 16–16 行：

```sql
avg(customer_acquisition_cost) FILTER(WHERE cumulative_conversions>0) over(partition by acquisition_cohort,advertising_channel_type) cohort_avg_cac
```

单改/诊断：`records/019_reruns_impl-005_google_ads__customer_acquisition_analysis.json#cohort_avg_cac`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 10000/80029 | 10000/80029 | 0/0 |
| L1 | 10000/80764 | 10000/80764 | 0/0 |
| L2 | 10000/60521 | 10000/60521 | 0/0 |
| L3 | 10000/60521 | 10000/60521 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，event `1.message`：

> - name: cohort_avg_cac
>         data_type: DOUBLE
>         description: Average running CAC within the same acquisition_cohort and advertising_channel_type; rows with zero cumulative_conversions are excluded; not rounded

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### cohort_avg_ltv

- 类别：Intent Misreading；角色：非原因；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约cohort均值使用已舍入的LTV输入，agent使用未舍入表达式；单改无净改善。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: cohort_avg_ltv
>         data_type: DOUBLE
>         description: Average running LTV per conversion within the same acquisition_cohort and advertising_channel_type; rows with zero cumulative_conversions are excluded; not rounded

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__customer_acquisition_analysis.sql`，第 17–17 行：

```sql
avg(average_customer_ltv) FILTER(WHERE cumulative_conversions>0) over(partition by acquisition_cohort,advertising_channel_type) cohort_avg_ltv
```

单改/诊断：`records/019_reruns_impl-005_google_ads__customer_acquisition_analysis.json#cohort_avg_ltv`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 10000/80029 | 10000/80029 | 0/0 |
| L1 | 10000/80764 | 10000/80764 | 0/0 |
| L2 | 10000/60521 | 10000/60521 | 0/0 |
| L3 | 10000/60521 | 10000/60521 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，event `1.message`：

> - name: cohort_avg_ltv
>         data_type: DOUBLE
>         description: Average running LTV per conversion within the same acquisition_cohort and advertising_channel_type; rows with zero cumulative_conversions are excluded; not rounded

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### cac_efficiency_percentile

- 类别：Unstated Choice；角色：主要；把握：中。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约未给可直接执行的排序方向/完整计分斜率与上限；higher rank可指名次靠前或百分位数更高。这里保留未规定的选择，不用gold公式反推要求。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: cac_efficiency_percentile
>         data_type: DOUBLE
>         description: Percentile rank (0–1) of CAC within the acquisition_cohort, with lower CAC ranked higher; ties share rank

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__customer_acquisition_analysis.sql`，第 18–18 行：

```sql
percent_rank() over(partition by acquisition_cohort order by customer_acquisition_cost desc) cac_efficiency_percentile
```

单改/诊断：`records/019_reruns_impl-005_google_ads__customer_acquisition_analysis.json#cac_efficiency_percentile`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 10000/80029 | 10000/61865 | 0/18164 |
| L1 | 10000/80764 | 10000/62653 | 0/18111 |
| L2 | 10000/60521 | 10000/42595 | 0/17926 |
| L3 | 10000/60521 | 10000/42595 | 0/17926 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，event `1.message`：

> - name: cac_efficiency_percentile
>         data_type: DOUBLE
>         description: Percentile rank (0–1) of CAC within the acquisition_cohort, with lower CAC ranked higher; ties share rank

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### ltv_cac_performance_percentile

- 类别：Unstated Choice；角色：参与；把握：中。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约未给可直接执行的排序方向/完整计分斜率与上限；higher rank可指名次靠前或百分位数更高。这里保留未规定的选择，不用gold公式反推要求。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: ltv_cac_performance_percentile
>         data_type: DOUBLE
>         description: Percentile rank (0–1) of LTV:CAC within the acquisition_cohort, with higher ratios ranked higher; ties share rank

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__customer_acquisition_analysis.sql`，第 19–19 行：

```sql
percent_rank() over(partition by acquisition_cohort order by ltv_cac_ratio) ltv_cac_performance_percentile
```

单改/诊断：`records/019_reruns_impl-005_google_ads__customer_acquisition_analysis.json#ltv_cac_performance_percentile`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 10000/80029 | 10000/70146 | 0/9883 |
| L1 | 10000/80764 | 10000/70927 | 0/9837 |
| L2 | 10000/60521 | 10000/50660 | 0/9861 |
| L3 | 10000/60521 | 10000/50660 | 0/9861 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，event `1.message`：

> - name: ltv_cac_performance_percentile
>         data_type: DOUBLE
>         description: Percentile rank (0–1) of LTV:CAC within the acquisition_cohort, with higher ratios ranked higher; ties share rank

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### acquisition_sophistication_score

- 类别：Unstated Choice；角色：参与；把握：中。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约未给可直接执行的排序方向/完整计分斜率与上限；higher rank可指名次靠前或百分位数更高。这里保留未规定的选择，不用gold公式反推要求。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: acquisition_sophistication_score
>         data_type: DOUBLE
>         description: Score clamped to [0,100] using channel diversity, active campaigns, LTV, and LTV:CAC; rounded to 1 decimal in the final output

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__customer_acquisition_analysis.sql`，第 26–26 行：

```sql
least(100.0,greatest(0.0,channel_diversity_count*15+active_campaigns_count*5+least(average_customer_ltv/100,30)+least(ltv_cac_ratio*5,25))) acquisition_sophistication_score
```

单改/诊断：`records/019_reruns_impl-005_google_ads__customer_acquisition_analysis.json#acquisition_sophistication_score`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 10000/80029 | 10000/68406 | 0/11623 |
| L1 | 10000/80764 | 10000/68370 | 0/12394 |
| L2 | 10000/60521 | 10000/48125 | 0/12396 |
| L3 | 10000/60521 | 10000/48125 | 0/12396 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，event `1.message`：

> - name: acquisition_sophistication_score
>         data_type: DOUBLE
>         description: Score clamped to [0,100] using channel diversity, active campaigns, LTV, and LTV:CAC; rounded to 1 decimal in the final output

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### strategic_customer_segment

- 类别：已说出的选择；角色：参与；把握：中。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

细分/建议规则缺少完整阈值和优先级；最终报告针对customer acquisition明确承认此缺口并说明选择CASE规则。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: strategic_customer_segment
>         data_type: VARCHAR
>         description: Strategic segment chosen by ordered rules using ltv_cac_ratio, average_customer_ltv, days_since_first_conversion, and CAC vs cohort

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__customer_acquisition_analysis.sql`，第 30–30 行：

```sql
CASE WHEN ltv_cac_ratio>=4 AND average_customer_ltv>1000 THEN 'High-value scale customer' WHEN ltv_cac_ratio<.5 THEN 'Unprofitable customer' WHEN days_since_first_conversion<=30 THEN 'New customer development' WHEN cac_vs_cohort_pct>50 THEN 'High CAC customer' ELSE 'Core customer' END strategic_customer_segment
```

单改/诊断：`records/019_reruns_impl-005_google_ads__customer_acquisition_analysis.json#strategic_customer_segment`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 10000/80029 | 10000/70037 | 0/9992 |
| L1 | 10000/80764 | 10000/70772 | 0/9992 |
| L2 | 10000/60521 | 10000/50529 | 0/9992 |
| L3 | 10000/60521 | 10000/50529 | 0/9992 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/47.json`，event `47.args.final_thought`：

> customer acquisition 的细分/建议规则未提供完整精确规则表，channel strategic recommendation 也未规定完整优先级；已采用保守、透明的 CASE 规则。

交付报告明确点到这张表/这类指标及其占位或选择。

### acquisition_recommendation

- 类别：已说出的选择；角色：参与；把握：中。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

细分/建议规则缺少完整阈值和优先级；最终报告针对customer acquisition明确承认此缺口并说明选择CASE规则。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: acquisition_recommendation
>         data_type: VARCHAR
>         description: Recommendation selected by ordered rules using LTV:CAC, CAC percentile, channel diversity, days since first conversion, CAC vs cohort, and active campaigns

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__customer_acquisition_analysis.sql`，第 32–32 行：

```sql
CASE WHEN ltv_cac_ratio>=3 AND cac_efficiency_percentile>=.8 THEN 'Scale acquisition investment' WHEN ltv_cac_ratio<.5 THEN 'Reduce acquisition cost' WHEN channel_diversity_count<2 THEN 'Diversify acquisition channels' WHEN cac_vs_cohort_pct>30 THEN 'Optimize CAC versus cohort' ELSE 'Maintain acquisition strategy' END acquisition_recommendation
```

单改/诊断：`records/019_reruns_impl-005_google_ads__customer_acquisition_analysis.json#acquisition_recommendation`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 10000/80029 | 10000/70516 | 0/9513 |
| L1 | 10000/80764 | 10000/71285 | 0/9479 |
| L2 | 10000/60521 | 10000/51042 | 0/9479 |
| L3 | 10000/60521 | 10000/51042 | 0/9479 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/47.json`，event `47.args.final_thought`：

> customer acquisition 的细分/建议规则未提供完整精确规则表，channel strategic recommendation 也未规定完整优先级；已采用保守、透明的 CASE 规则。

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
