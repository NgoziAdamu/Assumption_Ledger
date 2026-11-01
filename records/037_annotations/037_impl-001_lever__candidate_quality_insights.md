# impl-001_lever__candidate_quality_insights（037 正式批次）

主要原因：**其他**；把握：高。019旧主要原因原样保留：`A`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_quality_insights.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，finish 67 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-001_lever__candidate_quality_insights.json`；037补充：`records/037_checks/`。

## 逐点标注

### key_finding_source

- 类别：其他；角色：并列；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

条件和分类内容一致，仅英文消息写法不同；契约规定消息含义而未写死字符串。019只替换文字即消去该列差异，按第5节归其他。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: key_finding_source
>         data_type: VARCHAR
>         description: 'Message based on source-type averages: Referred or Internal exceeding External by >10 triggers respective message; otherwise note no significant difference.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_quality_insights.sql`，第 1–1 行：

```sql
CASE WHEN referred>external_avg+10 THEN 'Referral sources produce higher-quality candidates' WHEN internal>external_avg+10 THEN 'Internal mobility produces higher-quality candidates' ELSE 'No significant source difference' END key_finding_source
```

单改/诊断：`records/019_reruns_impl-001_lever__candidate_quality_insights.json#key_finding_source`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1/4 | 1/3 | 0/1 |
| L1 | 1/4 | 1/3 | 0/1 |
| L2 | 1/4 | 1/3 | 0/1 |
| L3 | 1/4 | 1/3 | 0/1 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：

> - name: key_finding_source
>         data_type: VARCHAR
>         description: 'Message based on source-type averages: Referred or Internal exceeding External by >10 triggers respective message; otherwise note no significant difference.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### key_finding_overall

- 类别：其他；角色：并列；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

条件和分类内容一致，仅英文消息写法不同；契约规定消息含义而未写死字符串。019只替换文字即消去该列差异，按第5节归其他。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: key_finding_overall
>         data_type: VARCHAR
>         description: 'Message based on the share of high/exceptional candidates: ≥40% Strong, ≥25% Good, otherwise Opportunity.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_quality_insights.sql`，第 1–1 行：

```sql
CASE WHEN (exceptional+highq)*1.0/nullif(total,0)>=.4 THEN 'Strong candidate quality distribution' WHEN (exceptional+highq)*1.0/nullif(total,0)>=.25 THEN 'Good candidate quality distribution' ELSE 'Opportunity to improve candidate quality' END key_finding_overall
```

单改/诊断：`records/019_reruns_impl-001_lever__candidate_quality_insights.json#key_finding_overall`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1/4 | 1/3 | 0/1 |
| L1 | 1/4 | 1/3 | 0/1 |
| L2 | 1/4 | 1/3 | 0/1 |
| L3 | 1/4 | 1/3 | 0/1 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：

> - name: key_finding_overall
>         data_type: VARCHAR
>         description: 'Message based on the share of high/exceptional candidates: ≥40% Strong, ≥25% Good, otherwise Opportunity.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### primary_recommendation

- 类别：其他；角色：并列；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

条件和分类内容一致，仅英文消息写法不同；契约规定消息含义而未写死字符串。019只替换文字即消去该列差异，按第5节归其他。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: primary_recommendation
>         data_type: VARCHAR
>         description: 'Recommendation driven by best source type: Referred → invest in referrals; Internal → promote mobility; otherwise optimize external channels.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_quality_insights.sql`，第 1–1 行：

```sql
CASE WHEN (SELECT source_type FROM src WHERE rn=1)='Referred' THEN 'Invest in referral programs' WHEN (SELECT source_type FROM src WHERE rn=1)='Internal' THEN 'Promote internal mobility' ELSE 'Optimize external channels' END primary_recommendation
```

单改/诊断：`records/019_reruns_impl-001_lever__candidate_quality_insights.json#primary_recommendation`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1/4 | 1/3 | 0/1 |
| L1 | 1/4 | 1/3 | 0/1 |
| L2 | 1/4 | 1/3 | 0/1 |
| L3 | 1/4 | 1/3 | 0/1 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：

> - name: primary_recommendation
>         data_type: VARCHAR
>         description: 'Recommendation driven by best source type: Referred → invest in referrals; Internal → promote mobility; otherwise optimize external channels.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### process_recommendation

- 类别：其他；角色：并列；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

条件和分类内容一致，仅英文消息写法不同；契约规定消息含义而未写死字符串。019只替换文字即消去该列差异，按第5节归其他。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: process_recommendation
>         data_type: VARCHAR
>         description: 'Recommendation from comparing rounded average lifecycle days: if high-quality is faster, fast-track; otherwise improve early screening.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_quality_insights.sql`，第 1–1 行：

```sql
CASE WHEN highdays<lowdays THEN 'Fast-track high-quality candidates' ELSE 'Improve early screening' END process_recommendation
```

单改/诊断：`records/019_reruns_impl-001_lever__candidate_quality_insights.json#process_recommendation`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1/4 | 1/3 | 0/1 |
| L1 | 1/4 | 1/3 | 0/1 |
| L2 | 1/4 | 1/3 | 0/1 |
| L3 | 1/4 | 1/3 | 0/1 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：

> - name: process_recommendation
>         data_type: VARCHAR
>         description: 'Recommendation from comparing rounded average lifecycle days: if high-quality is faster, fast-track; otherwise improve early screening.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
