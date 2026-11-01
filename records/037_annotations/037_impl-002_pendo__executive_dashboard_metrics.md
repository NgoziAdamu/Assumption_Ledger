# impl-002_pendo__executive_dashboard_metrics（037 正式批次）

主要原因：**已说出的降级**；把握：高。019旧主要原因原样保留：`D`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/executive_dashboard_metrics.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，finish 59 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/pendo.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-002_pendo__executive_dashboard_metrics.json`；037补充：`records/037_checks/`。

## 逐点标注

### avg_feature_adoption

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

账户级feature adoption汇总被NULL占位；019按每账户max后求平均的单改可复用。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_feature_adoption
>         data_type: DOUBLE
>         description: Average of per-account feature_adoption_rate; NULLs are ignored

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/executive_dashboard_metrics.sql`，第 1–1 行：

```sql
NULL::DOUBLE avg_feature_adoption
```

单改/诊断：`records/019_reruns_impl-002_pendo__executive_dashboard_metrics.json#avg_feature_adoption`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1/7 | 1/6 | 0/1 |
| L1 | 1/7 | 1/6 | 0/1 |
| L2 | 1/7 | 1/6 | 0/1 |
| L3 | 1/7 | 1/6 | 0/1 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

### avg_platform_health_score

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_platform_health_score
>         data_type: DOUBLE
>         description: Average of per-account product_health_score; NULLs are ignored

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/executive_dashboard_metrics.sql`，第 1–1 行：

```sql
NULL::DOUBLE avg_platform_health_score
```

单改/诊断：`records/037_checks/rerun_impl-002_pendo__executive_dashboard_metrics.json#avg_platform_health_score`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1/7 | 1/6 | 0/1 |
| L1 | 1/7 | 1/6 | 0/1 |
| L2 | 1/7 | 1/6 | 0/1 |
| L3 | 1/7 | 1/6 | 0/1 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

### avg_retention_rate

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: avg_retention_rate
>         data_type: DOUBLE
>         description: Average of per-account customer_retention_30d; NULLs are ignored

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/executive_dashboard_metrics.sql`，第 1–1 行：

```sql
NULL::DOUBLE avg_retention_rate
```

单改/诊断：`records/037_checks/rerun_impl-002_pendo__executive_dashboard_metrics.json#avg_retention_rate`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1/7 | 1/6 | 0/1 |
| L1 | 1/7 | 1/6 | 0/1 |
| L2 | 1/7 | 1/6 | 0/1 |
| L3 | 1/7 | 1/6 | 0/1 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

### medium_risk_accounts

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: medium_risk_accounts
>         data_type: BIGINT
>         description: Number of accounts labeled Medium Risk

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/executive_dashboard_metrics.sql`，第 1–1 行：

```sql
0::BIGINT medium_risk_accounts
```

单改/诊断：`records/037_checks/rerun_impl-002_pendo__executive_dashboard_metrics.json#medium_risk_accounts`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1/7 | 1/6 | 0/1 |
| L1 | 1/7 | 1/6 | 0/1 |
| L2 | 1/7 | 1/6 | 0/1 |
| L3 | 1/7 | 1/6 | 0/1 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

### low_risk_accounts

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: low_risk_accounts
>         data_type: BIGINT
>         description: Number of accounts labeled Low Risk

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/executive_dashboard_metrics.sql`，第 1–1 行：

```sql
0::BIGINT low_risk_accounts
```

单改/诊断：`records/037_checks/rerun_impl-002_pendo__executive_dashboard_metrics.json#low_risk_accounts`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1/7 | 1/6 | 0/1 |
| L1 | 1/7 | 1/6 | 0/1 |
| L2 | 1/7 | 1/6 | 0/1 |
| L3 | 1/7 | 1/6 | 0/1 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

### overall_business_health_score

- 类别：已说出的降级；角色：并列；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: overall_business_health_score
>         data_type: DOUBLE
>         description: Weighted composite of platform KPIs and growth component capped at 100; NULL if any non-growth component is NULL

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/executive_dashboard_metrics.sql`，第 1–1 行：

```sql
NULL::DOUBLE overall_business_health_score
```

单改/诊断：`records/037_checks/rerun_impl-002_pendo__executive_dashboard_metrics.json#overall_business_health_score`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1/7 | 1/6 | 0/1 |
| L1 | 1/7 | 1/6 | 0/1 |
| L2 | 1/7 | 1/6 | 0/1 |
| L3 | 1/7 | 1/6 | 0/1 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

### primary_alert_status

- 类别：已说出的降级；角色：非原因；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

恢复契约规定的这一列；其余SQL字节不动。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: primary_alert_status
>         data_type: VARCHAR
>         description: Primary alert determined by ordered rules for risk share, NPS, growth decline, retention, and customer health

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/executive_dashboard_metrics.sql`，第 1–1 行：

```sql
'All Systems Normal' primary_alert_status
```

单改/诊断：`records/037_checks/rerun_impl-002_pendo__executive_dashboard_metrics.json#primary_alert_status`。单改重跑；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1/7 | 1/7 | 0/0 |
| L1 | 1/7 | 1/7 | 0/0 |
| L2 | 1/7 | 1/7 | 0/0 |
| L3 | 1/7 | 1/7 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
