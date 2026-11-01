# impl-003_int_customer360__risk_assessment（037 正式批次）

主要原因：**Form Mismatch**；把握：高。019旧主要原因原样保留：`C`，不作为新类别依据。

## 范围与材料

- 层：intermediate；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/intermediate/int_customer360__risk_assessment.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，finish 51 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-003_int_customer360__risk_assessment.json`；037补充：`records/037_checks/`。

## 逐点标注

### probability_type

- 类别：Form Mismatch；角色：主要；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

七项风险和阈值计算一致，输出推断为DECIMAL(2,2)，契约明确DECIMAL(3,2)。019只cast同一CASE值即可消除这部分差异，不改变后续计算值。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: intervention_success_probability
>         data_type: DECIMAL(3,2)
>         description: 'Success probability from the sum of seven risk components: ≥8 → 0.30; ≥5 → 0.60; ≥3 → 0.80; ≥1 → 0.90; else → 0.95'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/intermediate/int_customer360__risk_assessment.sql`，第 39–39 行：

```sql
case when S>=8 then .30 when S>=5 then .60 when S>=3 then .80 when S>=1 then .90 else .95 end as intervention_success_probability
```

单改/诊断：`records/019_reruns_impl-003_int_customer360__risk_assessment.json#probability_type`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 6947/9180 | 1570/2233 | 5377/6947 |
| L1 | 1570/2233 | 1570/2233 | 0/0 |
| L2 | 1570/2233 | 1570/2233 | 0/0 |
| L3 | 1570/2233 | 1570/2233 | 0/0 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，event `1.message`：

> - name: intervention_success_probability
>         data_type: DECIMAL(3,2)
>         description: 'Success probability from the sum of seven risk components: ≥8 → 0.30; ≥5 → 0.60; ≥3 → 0.80; ≥1 → 0.90; else → 0.95'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### primary_risk_factor

- 类别：Unstated Choice；角色：参与；把握：中。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

规定类别优先级但没有完整触发阈值；这里是数值阈值选择，非纯标签差异。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: primary_risk_factor
>         data_type: VARCHAR
>         description: 'Primary factor by precedence: Payment Issues; Engagement Decline; Lifecycle Transition; High Value at Risk; Support Issues; Communication Breakdown; else Standard Monitoring'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/intermediate/int_customer360__risk_assessment.sql`，第 34–34 行：

```sql
case when payment_behavior_risk>0 then 'Payment Issues' when activity_decline_risk>0 then 'Engagement Decline' when lifecycle_transition_risk>0 then 'Lifecycle Transition' when revenue_at_risk_score>0 then 'High Value at Risk' when support_engagement_risk>0 then 'Support Issues' when email_engagement_risk>0 then 'Communication Breakdown' else 'Standard Monitoring' end as primary_risk_factor
```

单改/诊断：`records/019_reruns_impl-003_int_customer360__risk_assessment.json#primary_risk_factor`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 6947/9180 | 6947/8069 | 0/1111 |
| L1 | 1570/2233 | 561/1122 | 1009/1111 |
| L2 | 1570/2233 | 561/1122 | 1009/1111 |
| L3 | 1570/2233 | 561/1122 | 1009/1111 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，event `1.message`：

> - name: primary_risk_factor
>         data_type: VARCHAR
>         description: 'Primary factor by precedence: Payment Issues; Engagement Decline; Lifecycle Transition; High Value at Risk; Support Issues; Communication Breakdown; else Standard Monitoring'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### recommended_intervention

- 类别：Unstated Choice；角色：参与；把握：中。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约给优先顺序/含义但未给所有触发阈值，无法以gold阈值作要求。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: recommended_intervention
>         data_type: VARCHAR
>         description: 'Intervention by precedence: Account Management Call; Executive Outreach; Customer Success Check-in; Personalized Email Campaign; Product Adoption Workshop; Lifecycle-specific Campaign; else Automated Monitoring'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/intermediate/int_customer360__risk_assessment.sql`，第 38–38 行：

```sql
case when payment_behavior_risk>0 then 'Account Management Call' when activity_decline_risk>=2 and estimated_customer_ltv>=5000 then 'Executive Outreach' when support_engagement_risk>0 then 'Customer Success Check-in' when email_engagement_risk>0 then 'Personalized Email Campaign' when platform_abandonment_risk>0 then 'Product Adoption Workshop' when lifecycle_stage is not null then 'Lifecycle-specific Campaign' else 'Automated Monitoring' end as recommended_intervention
```

单改/诊断：`records/019_reruns_impl-003_int_customer360__risk_assessment.json#recommended_intervention`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 6947/9180 | 6947/8058 | 0/1122 |
| L1 | 1570/2233 | 1111/1111 | 459/1122 |
| L2 | 1570/2233 | 1111/1111 | 459/1122 |
| L3 | 1570/2233 | 1111/1111 | 459/1122 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，event `1.message`：

> - name: recommended_intervention
>         data_type: VARCHAR
>         description: 'Intervention by precedence: Account Management Call; Executive Outreach; Customer Success Check-in; Personalized Email Campaign; Product Adoption Workshop; Lifecycle-specific Campaign; else Automated Monitoring'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：

`records/019_queries.json` / 诊断：
```sql
SELECT typeof(intervention_success_probability) AS type,count(*) n FROM intermediate.int_customer360__risk_assessment GROUP BY ALL
```
结果：`[["DECIMAL(2,2)", 6947]]`

`records/019_queries.json` / 诊断：
```sql
SELECT typeof(intervention_success_probability) AS type,count(*) n FROM intermediate.int_customer360__risk_assessment GROUP BY ALL
```
结果：`[["DECIMAL(3,2)", 6947]]`
