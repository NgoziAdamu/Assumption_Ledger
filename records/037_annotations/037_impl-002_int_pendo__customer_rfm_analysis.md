# impl-002_int_pendo__customer_rfm_analysis（037 正式批次）

主要原因：**Unstated Choice**；把握：中。019旧主要原因原样保留：`A`，不作为新类别依据。

## 范围与材料

- 层：intermediate；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__customer_rfm_analysis.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，finish 59 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/pendo.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-002_int_pendo__customer_rfm_analysis.json`；037补充：`records/037_checks/`。

## 逐点标注

### recommended_strategy

- 类别：Unstated Choice；角色：主要；把握：中。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约给出业务用途/大致类别但没有完整segment到策略、CLV或优先级映射；几种规则均说得通。差异取决于未规定的选择，不把gold映射当要求。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: recommended_strategy
>         data_type: VARCHAR
>         description: Deterministic recommendation text mapped from rfm_segment; default is Standard engagement tactics.

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__customer_rfm_analysis.sql`，第 1–1 行：

```sql
CASE WHEN rfm_segment IN ('Champions','Loyal Customers') THEN 'Reward loyalty and advocate' WHEN rfm_segment IN ('At Risk','Cannot Be Retrieved','Hibernating') THEN 'Re-engage customer' ELSE 'Standard engagement tactics' END recommended_strategy
```

单改/诊断：`records/019_reruns_impl-002_int_pendo__customer_rfm_analysis.json#recommended_strategy`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 7977/60241 | 7976/52264 | 1/7977 |
| L1 | 7977/60241 | 7976/52264 | 1/7977 |
| L2 | 7977/60241 | 7976/52264 | 1/7977 |
| L3 | 7977/60241 | 7976/52264 | 1/7977 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/1.json`，event `1.message`：

> - name: recommended_strategy
>         data_type: VARCHAR
>         description: Deterministic recommendation text mapped from rfm_segment; default is Standard engagement tactics.

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### predicted_clv_tier

- 类别：Unstated Choice；角色：参与；把握：中。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约给出业务用途/大致类别但没有完整segment到策略、CLV或优先级映射；几种规则均说得通。差异取决于未规定的选择，不把gold映射当要求。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: predicted_clv_tier
>         data_type: VARCHAR
>         description: CLV tier from rfm_segment; Very High requires Champions or Loyal Customers with lifetime >180 days.

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__customer_rfm_analysis.sql`，第 1–1 行：

```sql
CASE WHEN rfm_segment IN ('Champions','Loyal Customers') AND customer_lifetime_days>180 THEN 'Very High CLV' WHEN rfm_segment IN ('Champions','Loyal Customers') THEN 'High CLV' WHEN rfm_segment IN ('Potential Loyalists','Promising') THEN 'Medium CLV' ELSE 'Low CLV' END predicted_clv_tier
```

单改/诊断：`records/019_reruns_impl-002_int_pendo__customer_rfm_analysis.json#predicted_clv_tier`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 7977/60241 | 7977/53002 | 0/7239 |
| L1 | 7977/60241 | 7977/53002 | 0/7239 |
| L2 | 7977/60241 | 7977/53002 | 0/7239 |
| L3 | 7977/60241 | 7977/53002 | 0/7239 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/1.json`，event `1.message`：

> - name: predicted_clv_tier
>         data_type: VARCHAR
>         description: CLV tier from rfm_segment; Very High requires Champions or Loyal Customers with lifetime >180 days.

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### action_priority

- 类别：Unstated Choice；角色：参与；把握：中。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约给出业务用途/大致类别但没有完整segment到策略、CLV或优先级映射；几种规则均说得通。差异取决于未规定的选择，不把gold映射当要求。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: action_priority
>         data_type: VARCHAR
>         description: 'Next-step priority mapped from rfm_segment: Retention & Advocacy, Growth & Upsell, Onboarding & Education, Re-engagement, Win-back or Deprioritize, Reactivation, or Monitor.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__customer_rfm_analysis.sql`，第 1–1 行：

```sql
CASE WHEN rfm_segment IN ('Champions','Loyal Customers') THEN 'Retention & Advocacy' WHEN rfm_segment IN ('Potential Loyalists','Promising') THEN 'Growth & Upsell' WHEN rfm_segment='New Customers' THEN 'Onboarding & Education' WHEN rfm_segment IN ('At Risk','Cannot Be Retrieved','Hibernating') THEN 'Re-engagement' ELSE 'Monitor' END action_priority
```

单改/诊断：`records/019_reruns_impl-002_int_pendo__customer_rfm_analysis.json#action_priority`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 7977/60241 | 7977/52326 | 0/7915 |
| L1 | 7977/60241 | 7977/52326 | 0/7915 |
| L2 | 7977/60241 | 7977/52326 | 0/7915 |
| L3 | 7977/60241 | 7977/52326 | 0/7915 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/1.json`，event `1.message`：

> - name: action_priority
>         data_type: VARCHAR
>         description: 'Next-step priority mapped from rfm_segment: Retention & Advocacy, Growth & Upsell, Onboarding & Education, Re-engagement, Win-back or Deprioritize, Reactivation, or Monitor.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### account_total_visitors

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约要求账户级聚合，SQL整列NULL；最终报告明确说RFM account-level metrics为NULL placeholders，按025更正归第1档。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: account_total_visitors
>         data_type: BIGINT
>         description: Number of visitor rows for the account; denominator for the ratios.

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__customer_rfm_analysis.sql`，第 1–1 行：

```sql
CAST(NULL AS BIGINT) account_total_visitors
```

单改/诊断：`records/019_reruns_impl-002_int_pendo__customer_rfm_analysis.json#account_total_visitors`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 7977/60241 | 7977/53374 | 0/6867 |
| L1 | 7977/60241 | 7977/53374 | 0/6867 |
| L2 | 7977/60241 | 7977/53374 | 0/6867 |
| L3 | 7977/60241 | 7977/53374 | 0/6867 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> RFM account-level metrics are NULL placeholders;

交付报告明确点到这张表/这类指标及其占位或选择。

### account_high_value_ratio

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约要求账户级聚合，SQL整列NULL；最终报告明确说RFM account-level metrics为NULL placeholders，按025更正归第1档。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: account_high_value_ratio
>         data_type: FLOAT
>         description: Share of High Value visitors over total_visitors using floating-point division.

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__customer_rfm_analysis.sql`，第 1–1 行：

```sql
CAST(NULL AS FLOAT) account_high_value_ratio
```

单改/诊断：`records/019_reruns_impl-002_int_pendo__customer_rfm_analysis.json#account_high_value_ratio`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 7977/60241 | 7977/53374 | 0/6867 |
| L1 | 7977/60241 | 7977/53374 | 0/6867 |
| L2 | 7977/60241 | 7977/53374 | 0/6867 |
| L3 | 7977/60241 | 7977/53374 | 0/6867 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> RFM account-level metrics are NULL placeholders;

交付报告明确点到这张表/这类指标及其占位或选择。

### account_top_segment_ratio

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约要求账户级聚合，SQL整列NULL；最终报告明确说RFM account-level metrics为NULL placeholders，按025更正归第1档。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: account_top_segment_ratio
>         data_type: FLOAT
>         description: Share of Champions or Loyal Customers over total_visitors using floating-point division.

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__customer_rfm_analysis.sql`，第 1–1 行：

```sql
CAST(NULL AS FLOAT) account_top_segment_ratio
```

单改/诊断：`records/019_reruns_impl-002_int_pendo__customer_rfm_analysis.json#account_top_segment_ratio`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 7977/60241 | 7977/53374 | 0/6867 |
| L1 | 7977/60241 | 7977/53374 | 0/6867 |
| L2 | 7977/60241 | 7977/53374 | 0/6867 |
| L3 | 7977/60241 | 7977/53374 | 0/6867 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> RFM account-level metrics are NULL placeholders;

交付报告明确点到这张表/这类指标及其占位或选择。

### account_at_risk_ratio

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约要求账户级聚合，SQL整列NULL；最终报告明确说RFM account-level metrics为NULL placeholders，按025更正归第1档。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: account_at_risk_ratio
>         data_type: FLOAT
>         description: Share of At Risk or Cannot Be Retrieved visitors over total_visitors using floating-point division.

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__customer_rfm_analysis.sql`，第 1–1 行：

```sql
CAST(NULL AS FLOAT) account_at_risk_ratio
```

单改/诊断：`records/019_reruns_impl-002_int_pendo__customer_rfm_analysis.json#account_at_risk_ratio`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 7977/60241 | 7977/53374 | 0/6867 |
| L1 | 7977/60241 | 7977/53374 | 0/6867 |
| L2 | 7977/60241 | 7977/53374 | 0/6867 |
| L3 | 7977/60241 | 7977/53374 | 0/6867 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> RFM account-level metrics are NULL placeholders;

交付报告明确点到这张表/这类指标及其占位或选择。

### account_avg_rfm_score

- 类别：已说出的降级；角色：参与；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约要求账户级聚合，SQL整列NULL；最终报告明确说RFM account-level metrics为NULL placeholders，按025更正归第1档。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: account_avg_rfm_score
>         data_type: DOUBLE
>         description: Mean rfm_composite_score across all visitors in the account.

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__customer_rfm_analysis.sql`，第 1–1 行：

```sql
CAST(NULL AS DOUBLE) account_avg_rfm_score
```

单改/诊断：`records/019_reruns_impl-002_int_pendo__customer_rfm_analysis.json#account_avg_rfm_score`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 7977/60241 | 7977/52819 | 0/7422 |
| L1 | 7977/60241 | 7977/52819 | 0/7422 |
| L2 | 7977/60241 | 7977/52819 | 0/7422 |
| L3 | 7977/60241 | 7977/52819 | 0/7422 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> RFM account-level metrics are NULL placeholders;

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
