# impl-003_customer360__conversion_funnel_analysis（037 正式批次）

主要原因：**Form Mismatch**；把握：高。019旧主要原因原样保留：`C`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__conversion_funnel_analysis.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，finish 51 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-003_customer360__conversion_funnel_analysis.json`；037补充：`records/037_checks/`。

## 逐点标注

### presentation_round_revenue

- 类别：Form Mismatch；角色：主要；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

037只对最终revenue_velocity_monthly round(...,2)，L0差异由99356行/449116格变为8744行/358504格。原表达式除以days/30与LTV/days×30代数相同；019称分母/单位错误不成立，按明确两位小数要求归Form。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: revenue_velocity_monthly
>         data_type: DOUBLE
>         description: If reached_conversion=1, monthly velocity = round(LTV ÷ days to sales (use 30 if missing or <30) × 30, 2); else 0; NULL if LTV is NULL

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__conversion_funnel_analysis.sql`，第 18–18 行：

```sql
 case when in_stripe=1 then estimated_customer_ltv*30.0/greatest(coalesce(marketing_to_sales_days,30),30) else 0 end as revenue_velocity_monthly,
```

单改/诊断：`records/037_checks/rerun_impl-003_customer360__conversion_funnel_analysis.json#presentation_round_revenue`。呈现诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 99356/449116 | 8744/358504 | 90612/90612 |
| L1 | 99356/449116 | 8744/358504 | 90612/90612 |
| L2 | 8744/358504 | 8744/358504 | 0/0 |
| L3 | 8744/358504 | 8744/358504 | 0/0 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，event `1.message`：

> - name: revenue_velocity_monthly
>         data_type: DOUBLE
>         description: If reached_conversion=1, monthly velocity = round(LTV ÷ days to sales (use 30 if missing or <30) × 30, 2); else 0; NULL if LTV is NULL

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### rounded_consistency

- 类别：Intent Misreading；角色：非原因；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约要求用于journey_efficiency_index的中间consistency先舍入；agent使用未舍入值。会进入计算链，不是Form；单改未减少当前规模。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: journey_efficiency_index
>         data_type: DOUBLE
>         description: Rounded to 2 decimals; index = 0.3*completeness + 0.3*velocity_score + 0.4*cross_stage_engagement_consistency

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__conversion_funnel_analysis.sql`，第 41–41 行：

```sql
.4*cross_stage_engagement_consistency,2) as journey_efficiency_index
```

单改/诊断：`records/019_reruns_impl-003_customer360__conversion_funnel_analysis.json#rounded_consistency`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 99356/449116 | 99356/449116 | 0/0 |
| L1 | 99356/449116 | 99356/449116 | 0/0 |
| L2 | 8744/358504 | 8744/358504 | 0/0 |
| L3 | 8744/358504 | 8744/358504 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，event `1.message`：

> - name: journey_efficiency_index
>         data_type: DOUBLE
>         description: Rounded to 2 decimals; index = 0.3*completeness + 0.3*velocity_score + 0.4*cross_stage_engagement_consistency

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### journey_completeness_score

- 类别：其他；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约任意两个平台应得2；gold遗漏Marketo+Zendesk组合，agent按在场平台数实现符合契约。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: journey_completeness_score
>         data_type: INTEGER
>         description: 'Score: 3 if all stages reached, 2 if any two, 1 if any one, else 0'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__conversion_funnel_analysis.sql`，第 8–8 行：

```sql
case when in_marketo=1 and in_stripe=1 and in_zendesk=1 then 3 when in_marketo+in_stripe+in_zendesk>=2 then 2 when in_marketo+in_stripe+in_zendesk=1 then 1 else 0 end as journey_completeness_score
```

单改/诊断：`records/019_reruns_impl-003_customer360__conversion_funnel_analysis.json#journey_completeness_score`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 99356/449116 | 90612/90612 | 8744/358504 |
| L1 | 99356/449116 | 90612/90612 | 8744/358504 |
| L2 | 8744/358504 | 0/0 | 8744/358504 |
| L3 | 8744/358504 | 0/0 | 8744/358504 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，event `1.message`：

> - name: journey_completeness_score
>         data_type: INTEGER
>         description: 'Score: 3 if all stages reached, 2 if any two, 1 if any one, else 0'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
