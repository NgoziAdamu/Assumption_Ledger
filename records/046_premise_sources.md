# Data Misconception 与 Intent Misreading：标注原文摘录

仅按字段、标题和格式规则摘录。各点正文保留原文；不写前提句、不概括、不合并。

字符计数、逐字核对和完整查找记录见同名 JSON；源段落行号包含原始标题行。

## DAComp / impl-001_lever__departmental_hiring_trends | main_category：Quiet Downgrade

### referral_count | Intent Misreading | 参与 | records/037_annotations/037_impl-001_lever__departmental_hiring_trends.md:16-60

point_id：`records/037_points.csv:38`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约数有referrer的distinct application；agent数distinct referrer，漏算同一推荐人关联的多个申请。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: referral_rate
>         data_type: DOUBLE
>         description: Percentage with 2 decimals; referred applications divided by total applications *100; 0 when no applications; joined on department+team only
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`，第 13–13 行：
```sql
count(DISTINCT referrer_user_id) AS referred
```
单改/诊断：`records/019_reruns_impl-001_lever__departmental_hiring_trends.json#referral_count`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：
> - name: referral_rate
>         data_type: DOUBLE
>         description: Percentage with 2 decimals; referred applications divided by total applications *100; 0 when no applications; joined on department+team only
契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

## DAComp / impl-001_lever__hiring_manager_scorecard | main_category：Quiet Downgrade

### unweighted_total_applications | Intent Misreading | 参与 | records/037_annotations/037_impl-001_lever__hiring_manager_scorecard.md:55-95

point_id：`records/037_points.csv:49`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约要求每posting简单均值；agent在application扩行后求AVG，形成按申请量加权。知道契约规定的汇总层次即可改正，归Intent。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> business_logic: '- Define hiring_manager_base: - From users keep access_role in {''admin'',''team_admin'',''limited''}. - Left join requisitions, postings, and applications (via postings) to compute workload: - total_requisitions_owned, total_postings_owned, total_applications_received, total_candidates_managed as distinct counts. - Keep only users with at least one requisition or posting. - Req[截断，原长 4546 字符]
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 18–18 行：
```sql
avg(pp.total_applications)
```
单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#unweighted_total_applications`。单改重跑；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：
> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### unweighted_posting_performance_score | Intent Misreading | 参与 | records/037_annotations/037_impl-001_lever__hiring_manager_scorecard.md:96-136

point_id：`records/037_points.csv:50`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约要求每posting简单均值；agent在application扩行后求AVG，形成按申请量加权。知道契约规定的汇总层次即可改正，归Intent。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> business_logic: '- Define hiring_manager_base: - From users keep access_role in {''admin'',''team_admin'',''limited''}. - Left join requisitions, postings, and applications (via postings) to compute workload: - total_requisitions_owned, total_postings_owned, total_applications_received, total_candidates_managed as distinct counts. - Keep only users with at least one requisition or posting. - Req[截断，原长 4546 字符]
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`，第 20–20 行：
```sql
avg(pp.posting_performance_score)
```
单改/诊断：`records/037_checks/rerun_impl-001_lever__hiring_manager_scorecard.json#unweighted_posting_performance_score`。单改重跑；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：
> 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## DAComp / impl-001_lever__opportunity_enhanced | main_category：Intent Misreading

### candidate_partition | Intent Misreading | 主要 | records/037_annotations/037_impl-001_lever__opportunity_enhanced.md:16-56

point_id：`records/037_points.csv:61`；定位状态：已定位。

- 类别：Intent Misreading；角色：主要；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约明确按candidate选择最新offer，agent按opportunity分区；改动涉及行对应，不是文字形式。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> business_logic: '- Use intermediate.int_lever__opportunity_contact_info as the base; each output row represents one opportunity_id from this base. - Inner join staging.stg_lever__stage on stage_id to add current_stage; opportunities without a matching stage are excluded. - Left join staging.stg_lever__archive_reason on archived_reason_id to add archive_reason; if no match, archive_reason is NULL[截断，原长 1334 字符]
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__opportunity_enhanced.sql`，第 1–1 行：
```sql
PARTITION BY opportunity_id ORDER BY created_at DESC
```
单改/诊断：`records/019_reruns_impl-001_lever__opportunity_enhanced.json#candidate_partition`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：
> business_logic: '- Use intermediate.int_lever__opportunity_contact_info as the base; each output row represents one opportunity_id from this base. - Inner join staging.stg_lever__stage on stage_id to add current_stage; opportunities without a matching stage are excluded. - Left join staging.stg_lever__archive_reason on archived_reason_id to add archive_reason; if no match, archive_reason is NULL[截断，原长 1334 字符]
契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

## DAComp / impl-001_stg_lever__offer | main_category：Intent Misreading

### status_filter | Intent Misreading | 主要 | records/037_annotations/037_impl-001_stg_lever__offer.md:16-60

point_id：`records/037_points.csv:62`；定位状态：已定位。

- 类别：Intent Misreading；角色：主要；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
offer.status无效枚举应置NULL；agent套用requisition的枚举并删整行。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: status
>           data_type: VARCHAR(50)
>           validation_rules:
>             - rule: "status IS NULL OR status IN ('draft', 'pending', 'sent', 'accepted', 'declined', 'rescinded')"
>               on_failure: nullify_field
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__offer.sql`，第 13–13 行：
```sql
status IN ('open','closed','cancelled','draft','pending') AND
```
单改/诊断：`records/019_reruns_impl-001_stg_lever__offer.json#status_filter`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：
> 转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。唯一键重复仅保留一行。
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## DAComp / impl-001_stg_lever__posting | main_category：Intent Misreading

### categories_commitment | Intent Misreading | 主要 | records/037_annotations/037_impl-001_stg_lever__posting.md:16-60

point_id：`records/037_points.csv:64`；定位状态：已定位。

- 类别：Intent Misreading；角色：主要；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约已逐字段给出合法枚举及nullify_field；agent未执行，改变保留值而不只是呈现。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: categories_commitment
>           data_type: VARCHAR(50)
>           validation_rules:
>             - rule: "categories_commitment IS NULL OR categories_commitment IN ('full-time', 'part-time', 'contract', 'internship')"
>               on_failure: nullify_field
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__posting.sql`，第 7–7 行：
```sql
try_cast(r."categories_commitment" AS VARCHAR(50)) AS categories_commitment
```
单改/诊断：`records/019_reruns_impl-001_stg_lever__posting.json#categories_commitment`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：
> 转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。唯一键重复仅保留一行。
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### categories_level | Intent Misreading | 参与 | records/037_annotations/037_impl-001_stg_lever__posting.md:61-105

point_id：`records/037_points.csv:65`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约已逐字段给出合法枚举及nullify_field；agent未执行，改变保留值而不只是呈现。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: categories_level
>           data_type: VARCHAR(50)
>           validation_rules:
>             - rule: "categories_level IS NULL OR categories_level IN ('Entry', 'Mid', 'Senior', 'Lead', 'Principal', 'Executive')"
>               on_failure: nullify_field
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__posting.sql`，第 9–9 行：
```sql
try_cast(r."categories_level" AS VARCHAR(50)) AS categories_level
```
单改/诊断：`records/019_reruns_impl-001_stg_lever__posting.json#categories_level`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：
> 转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。唯一键重复仅保留一行。
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## DAComp / impl-001_stg_lever__requisition | main_category：Intent Misreading

### compensation_band_currency | Intent Misreading | 主要 | records/037_annotations/037_impl-001_stg_lever__requisition.md:16-60

point_id：`records/037_points.csv:66`；定位状态：已定位。

- 类别：Intent Misreading；角色：主要；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约已逐字段给出合法枚举及nullify_field；agent未执行，改变保留值而不只是呈现。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: compensation_band_currency
>           data_type: VARCHAR(3)
>           validation_rules:
>             - rule: "compensation_band_currency IS NULL OR compensation_band_currency IN ('USD', 'EUR', 'GBP', 'CNY', 'CAD', 'AUD')"
>               on_failure: nullify_field
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__requisition.sql`，第 8–8 行：
```sql
try_cast(r."compensation_band_currency" AS VARCHAR(3)) AS compensation_band_currency
```
单改/诊断：`records/019_reruns_impl-001_stg_lever__requisition.json#compensation_band_currency`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：
> 转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。唯一键重复仅保留一行。
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### compensation_band_interval | Intent Misreading | 参与 | records/037_annotations/037_impl-001_stg_lever__requisition.md:61-105

point_id：`records/037_points.csv:67`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约已逐字段给出合法枚举及nullify_field；agent未执行，改变保留值而不只是呈现。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: compensation_band_interval
>           data_type: VARCHAR(10)
>           validation_rules:
>             - rule: "compensation_band_interval IS NULL OR compensation_band_interval IN ('hourly', 'monthly', 'yearly')"
>               on_failure: nullify_field
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__requisition.sql`，第 9–9 行：
```sql
try_cast(r."compensation_band_interval" AS VARCHAR(10)) AS compensation_band_interval
```
单改/诊断：`records/019_reruns_impl-001_stg_lever__requisition.json#compensation_band_interval`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，event `67.args.final_thought`：
> 转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。唯一键重复仅保留一行。
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## DAComp / impl-002_int_pendo__conversion_funnel_analysis | main_category：Quiet Downgrade

### avg_30d_page_to_feature_rate | Intent Misreading | 参与 | records/037_annotations/037_impl-002_int_pendo__conversion_funnel_analysis.md:250-292

point_id：`records/037_points.csv:74`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约明确相对today的30日下界、cohort按account/app等值连接；agent对全历史做窗口平均，未执行规定算法。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: avg_30d_page_to_feature_rate
>         data_type: DOUBLE
>         description: Average of daily page_to_feature_conversion_rate for dates on or after 30 days before today (inclusive); NULL if no data
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：
```sql
avg(page_to_feature_conversion_rate) OVER(PARTITION BY account_id,app_id) avg_30d_page_to_feature_rate
```
单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#avg_30d_page_to_feature_rate`。单改重跑；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：
> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### avg_30d_feature_to_deep_rate | Intent Misreading | 参与 | records/037_annotations/037_impl-002_int_pendo__conversion_funnel_analysis.md:293-335

point_id：`records/037_points.csv:75`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约明确相对today的30日下界、cohort按account/app等值连接；agent对全历史做窗口平均，未执行规定算法。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: avg_30d_feature_to_deep_rate
>         data_type: DOUBLE
>         description: Average of daily feature_to_deep_conversion_rate for dates on or after 30 days before today (inclusive); NULL if no data
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：
```sql
avg(feature_to_deep_conversion_rate) OVER(PARTITION BY account_id,app_id) avg_30d_feature_to_deep_rate
```
单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#avg_30d_feature_to_deep_rate`。单改重跑；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：
> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### avg_30d_overall_conversion_rate | Intent Misreading | 参与 | records/037_annotations/037_impl-002_int_pendo__conversion_funnel_analysis.md:336-378

point_id：`records/037_points.csv:76`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约明确相对today的30日下界、cohort按account/app等值连接；agent对全历史做窗口平均，未执行规定算法。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: avg_30d_overall_conversion_rate
>         data_type: DOUBLE
>         description: Average of daily overall_conversion_rate for dates on or after 30 days before today (inclusive); NULL if no data
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__conversion_funnel_analysis.sql`，第 1–1 行：
```sql
avg(overall_conversion_rate) OVER(PARTITION BY account_id,app_id) avg_30d_overall_conversion_rate
```
单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__conversion_funnel_analysis.json#avg_30d_overall_conversion_rate`。单改重跑；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：
> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## DAComp / impl-002_int_pendo__product_health_metrics | main_category：Quiet Downgrade

### retention_join | Intent Misreading | 参与 | records/037_annotations/037_impl-002_int_pendo__product_health_metrics.md:16-56

point_id：`records/037_points.csv:97`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约规定feature先FULL OUTER JOIN账户retention，再接engagement；agent省略中间账户来源，只f/e连接。连接算法已写明，归Intent。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> business_logic: '- NPS metrics (by account_id from intermediate.int_pendo__latest_nps_rating): - total_nps_responses is the total row count per account; avg_nps_score is the mean of nps_rating (ignoring NULLs). - promoter_rate is the share of rows with nps_rating ≥ 9 using total_nps_responses as the denominator (NULL ratings not counted in the numerator but included in the denominator). - detrac[截断，原长 4656 字符]
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__product_health_metrics.sql`，第 1–1 行：
```sql
FROM f FULL OUTER JOIN e ON f.account_id=e.account_id AND f.app_id=e.app_id
```
单改/诊断：`records/037_checks/rerun_impl-002_int_pendo__product_health_metrics.json#retention_join`。单改重跑；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：
> product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations;
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## DAComp / impl-002_pendo__customer_lifecycle_insights | main_category：多因并列

### customer_segment_branches | Intent Misreading | 并列 | records/037_annotations/037_impl-002_pendo__customer_lifecycle_insights.md:252-292

point_id：`records/037_points.csv:117`；定位状态：已定位。

- 类别：Intent Misreading；角色：并列；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
已实现有条件的分类，但漏掉契约明写的四个分支；不是数据性质假设。报告只泛称lifecycle简化，没有点出这几个被漏分支。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> business_logic: 'Build a comprehensive customer record per visitor_id by joining base visitor activity with lifecycle, RFM, and product health, then derive journey labels, values, and recommendations: 1) Base rowset and joins - Start from marts.pendo__visitor (vb), one row per visitor_id; carry: visitor_id, account_id, first_event_on, last_event_on, count_active_days, count_active_months, sum_ev[截断，原长 5398 字符]
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/customer_lifecycle_insights.sql`，第 1–1 行：
```sql
WHEN l.lifecycle_stage='New User' AND r.rfm_segment='New Customers' THEN 'Fresh Prospect' ELSE 'Standard Customer' END customer_segment_label
```
单改/诊断：`records/037_checks/rerun_impl-002_pendo__customer_lifecycle_insights.json#customer_segment_branches`。单改重跑；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：
> advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## DAComp / impl-002_stg_pendo__guide_event | main_category：多因并列

### url_rule | Intent Misreading | 并列 | records/034_annotations/dacomp_impl-002_stg_pendo__guide_event.md:19-29

point_id：`records/036_points.csv:4`；定位状态：已定位。

- 角色：并列；类别：**Intent Misreading**；把握：中。
- 依据：规格 url IS NULL OR url ~ '^https?://' 可执行；agent只trim，15000格差异。不是对现实URL有效性的判断。
- 是否说出：只有通用策略说明。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/014_trace_impl-002.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 59 / args.final_thought：
```text
Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.
```

### latitude_range | Data Misconception | 参与 | records/034_annotations/dacomp_impl-002_stg_pendo__guide_event.md:30-44

point_id：`records/036_points.csv:5`；定位状态：已定位。

- 角色：参与；类别：**Data Misconception**；把握：中。
- 依据：P：latitude均在±90内。已有核实查询反证13655个超界值；单改减少13655格。
- 是否说出：看到了但没提。
- 证据在场：否；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/014_trace_impl-002.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
实际可见列名/通用输出不能单凭它确定匹配或唯一性；核实查询为标注者事后执行。
event 14 / content：
```text
', None, None, None), ('name', 'VARCHAR', 'YES', None, None, None)]
 guide_event [('account_id', 'VARCHAR', 'YES', None, None, None), ('guide_id', 'VARCHAR', 'YES', None, None, None), ('remote_ip', 'VARCHAR', 'YES', None, None, None), ('server_name', 'VARCHAR', 'YES', None, None, None), ('timestamp', 'VARCHAR', 'YES', None, None, None), ('user_agent', 'VARCHAR', 'YES', None, None, None), ('visitor[截断，原长 919 字符]
```
四档引句为关联证据；本处可见性另按在场栏判断，未将通用策略算成具体披露。

## DAComp / impl-002_stg_pendo__poll_event | main_category：多因并列

### url | Intent Misreading | 并列 | records/037_annotations/037_impl-002_stg_pendo__poll_event.md:55-101

point_id：`records/037_points.csv:131`；定位状态：已定位。

- 类别：Intent Misreading；角色：并列；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约给出可执行的URL正则字面规则；agent只做trim。按第5节以DuckDB实际正则效果为准。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: url
>           data_type: VARCHAR(255)
>           validation_rules:
>             - rule: "url = NULLIF(TRIM(url), '')"
>               on_failure: correct
>             - rule: "url IS NULL OR url ~ '^https?://'"
>               on_failure: nullify_field
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__poll_event.sql`，第 18–18 行：
```sql
CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS VARCHAR)), '') END AS url
```
单改/诊断：`records/019_reruns_impl-002_stg_pendo__poll_event.json#url`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：
> Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## DAComp / impl-002_stg_pendo__user | main_category：Data Misconception

### deleted_at_parse | Data Misconception | 主要 | records/037_annotations/037_impl-002_stg_pendo__user.md:16-66

point_id：`records/037_points.csv:132`；定位状态：已定位。

- 类别：Data Misconception；角色：主要；把握：中。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：否；曾经理解对过：否；系统提示：不适用。
P：raw.user中非空deleted_at文本可由直接TRY_CAST(... AS TIMESTAMP)解析。契约只给目标类型/空值规则，未指定解析算法；019在agent留存raw上核实17行中12行直接转换失败而截取前23字符成功，证伪P。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: deleted_at
>           data_type: TIMESTAMP
>           validation_rules:
>             - rule: "deleted_at = CASE WHEN deleted_at = '' THEN NULL ELSE deleted_at END"
>               on_failure: nullify_field
已检查deleted_at完整契约：只给TIMESTAMP及空值规则，未指定解析算法。P由agent可见raw核实；未使用gold证伪。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
P：raw.user中非空deleted_at文本可由直接TRY_CAST(... AS TIMESTAMP)解析。
初始契约只规定目标类型，列清单只能看到VARCHAR；未见agent查询直接转换失败的原始格式。单凭这些不能证伪P，所以证据在场=否。
反证：`records/019_queries.json` 中impl-002 / stg_pendo__user的只读raw核实，17行中12行直接解析失败但substring(1,23)成功。查询的是agent当时可见数据。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__user.sql`，第 3–3 行：
```sql
TRY_CAST(NULLIF(deleted_at, '') AS TIMESTAMP)
```
单改/诊断：`records/019_reruns_impl-002_stg_pendo__user.json#deleted_at_parse`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：
> The work includes staging raw-field mapping, timestamp parsing, event-key generation, filtering and nullification; latest-record models; daily aggregates and calendar spines; and mart entities.
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### normalized_user_type | Intent Misreading | 参与 | records/037_annotations/037_impl-002_stg_pendo__user.md:67-114

point_id：`records/037_points.csv:133`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约要求先规范化user_type再枚举校验，agent在原始值上过滤。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: user_type
>           data_type: VARCHAR(50)
>           constraints: [not_null]
>           validation_rules:
>             - rule: "user_type IN ('system', 'internal', 'api', 'external')"
>               on_failure: delete_row
>             - rule: "user_type = LOWER(TRIM(user_type))"
>               on_failure: correct
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__user.sql`，第 9–9 行：
```sql
WHERE user_type IN
```
单改/诊断：`records/019_reruns_impl-002_stg_pendo__user.json#normalized_user_type`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：
> Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.
交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## DAComp / impl-003_customer360__customer_activity_metrics | main_category：Intent Misreading

### cross_platform_consistency | Intent Misreading | 主要 | records/037_annotations/037_impl-003_customer360__customer_activity_metrics.md:16-60

point_id：`records/037_points.csv:147`；定位状态：已定位。

- 类别：Intent Misreading；角色：主要；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约规定按在场平台数取平均，agent只相加未除；算法已写明，归Intent。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: cross_platform_consistency
>         data_type: DOUBLE
>         description: Average of raw engagement across active platforms (in_*=1) rounded to 2 decimals; NULL if no active platforms or any included operand is NULL
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__customer_activity_metrics.sql`，第 41–41 行：
```sql
round(case when in_marketo=1 then marketo_engagement else 0 end + case when in_stripe=1 then stripe_engagement else 0 end + case when in_zendesk=1 then zendesk_engagement else 0 end,2) as cross_platform_consistency
```
单改/诊断：`records/019_reruns_impl-003_customer360__customer_activity_metrics.json#cross_platform_consistency`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，event `1.message`：
> - name: cross_platform_consistency
>         data_type: DOUBLE
>         description: Average of raw engagement across active platforms (in_*=1) rounded to 2 decimals; NULL if no active platforms or any included operand is NULL
契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### primary_engagement_channel | Intent Misreading | 参与 | records/037_annotations/037_impl-003_customer360__customer_activity_metrics.md:61-106

point_id：`records/037_points.csv:148`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约要求比较原始engagement，agent比较时间衰减后score，属于规定的指标定义未落实。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> - name: primary_engagement_channel
>         data_type: VARCHAR
>         description: Channel with highest raw engagement; ties break Marketing Driven > Sales Driven > Support Driven; fallback Balanced when comparisons cannot be resolved (e.g., NULL inputs)
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__customer_activity_metrics.sql`，第 30–31 行：
```sql
case when marketing_engagement_score>=sales_engagement_score and marketing_engagement_score>=support_engagement_score then 'Marketing Driven'
 when sales_engagement_score>=support_engagement_score then 'Sales Driven' when support_engagement_score is not null then 'Support Driven' else 'Balanced' end as primary_engagement_channel
```
单改/诊断：`records/019_reruns_impl-003_customer360__customer_activity_metrics.json#primary_engagement_channel`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，event `1.message`：
> - name: primary_engagement_channel
>         data_type: VARCHAR
>         description: Channel with highest raw engagement; ties break Marketing Driven > Sales Driven > Support Driven; fallback Balanced when comparisons cannot be resolved (e.g., NULL inputs)
契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

## DAComp / impl-003_customer360__mapping | main_category：Intent Misreading

### outer_source | Intent Misreading | 主要 | records/037_annotations/037_impl-003_customer360__mapping.md:16-66

point_id：`records/037_points.csv:150`；定位状态：已定位。

- 类别：Intent Misreading；角色：主要；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约明确FULL OUTER JOIN后再UNION unmatched，agent把第一组连接写成LEFT JOIN；此算法已规定，不归Data。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> business_logic: '1) Load four inputs: source_matches, marketo, stripe, zendesk. 2) Build combine_all_results: - Chain full outer joins: source_matches to marketo on lead_id, then to stripe on customer_id from source_matches, then to zendesk on user_id from source_matches, retaining all records from every source. - For IDs, prefer the value from source_matches when present; otherwise use the corr[截断，原长 2743 字符]
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__mapping.sql`，第 1–11 行：
```sql
 select sm.marketo_lead_id, sm.stripe_customer_id, sm.zendesk_user_id,
        m.organization_name_no_suffix as m_org, m.inferred_organization_name_no_suffix as mi_org,
        s.customer_organization_name_no_suffix as s_org, s.shipping_organization_name_no_suffix as ss_org,
        z.organization_id, sm.marketo_updated_at, sm.marketo_created_at, sm.stripe_updated_at, sm.stripe_created_at,
       [截断，原长 826 字符]
```
单改/诊断：`records/019_reruns_impl-003_customer360__mapping.json#outer_source`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，event `1.message`：
> business_logic: '1) Load four inputs: source_matches, marketo, stripe, zendesk. 2) Build combine_all_results: - Chain full outer joins: source_matches to marketo on lead_id, then to stripe on customer_id from source_matches, then to zendesk on user_id from source_matches, retaining all records from every source. - For IDs, prefer the value from source_matches when present; otherwise use the corr[截断，原长 2743 字符]
契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

## DAComp / impl-005_google_ads__executive_dashboard | main_category：代码写错

### scale_null | Intent Misreading | 参与 | records/037_annotations/037_impl-005_google_ads__executive_dashboard.md:53-93

point_id：`records/037_points.csv:171`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约规定扩张标志默认false，agent布尔比较留下NULL；修改值的语义而非形式。
契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：
> business_logic: '1) Start from intermediate.int_google_ads__account_performance_metrics and rename core metrics to account-level totals: total_spend=spend; total_clicks=clicks; total_impressions=impressions; total_conversions=conversions; total_conversions_value=conversions_value; overall_ctr=ctr; overall_cpc=cpc; overall_cost_per_conversion=cost_per_conversion; overall_roas=roas. Also carry: so[截断，原长 4906 字符]
契约已规定算法/做法，按第5节归Intent。
曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。
SQL原处：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__executive_dashboard.sql`，第 24–24 行：
```sql
(star_pct>15) scale_opportunity
```
单改/诊断：`records/019_reruns_impl-005_google_ads__executive_dashboard.json#scale_null`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，event `1.message`：
> business_logic: '1) Start from intermediate.int_google_ads__account_performance_metrics and rename core metrics to account-level totals: total_spend=spend; total_clicks=clicks; total_impressions=impressions; total_conversions=conversions; total_conversions_value=conversions_value; overall_ctr=ctr; overall_cpc=cpc; overall_cost_per_conversion=cost_per_conversion; overall_roas=roas. Also carry: so[截断，原长 4906 字符]
契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### trending_null | Intent Misreading | 参与 | records/037_annotations/037_impl-005_google_ads__executive_dashboard.md:94-142

point_id：`records/037_points.csv:172`；定位状态：已定位。

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
披露/相关信息原句：
`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，event `1.message`：
> - name: trending_alert
>         data_type: BOOLEAN
>         description: True if spend_wow_growth_pct > 50 or conversions_wow_growth_pct < -30, else false
>         tests:
>         - not_null
契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

## DAComp / impl-006_int_ad_reporting__unified_campaign_metrics | main_category：Intent Misreading

### google_roas_rounding | Intent Misreading | 主要 | records/038_annotations/038_impl-006_int_ad_reporting__unified_campaign_metrics.md:21-55

point_id：`records/038_points.csv:23`；定位状态：已定位。

- 类别：Intent Misreading；角色：主要；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约明确Google ROAS为revenue_7d/cost，只对CTR/CPC等列规定舍入；agent在ROAS计算链中额外ROUND(...,4)，改变数值。不是只改展示，也不是数据格式事实。
判定顺序：不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。
契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：
> business_logic: 'Combine four platform feeds into a standardized base and apply filters per source: - Amazon Ads (staging.stg_amazon_ads__campaign_report): - Map fields: platform=''amazon_ads''; campaign_type from campaign_bidding_strategy; daily_budget from campaign_budget_amount; currency from campaign_budget_currency_code; cost from source; revenue_7d from sales_7_d; revenue_30d from sales_30[截断，原长 4944 字符]
交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql`，`delivered SQL`：
> ROUND(conversions_value / spend, 4)
披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：
> business_logic: 'Combine four platform feeds into a standardized base and apply filters per source: - Amazon Ads (staging.stg_amazon_ads__campaign_report): - Map fields: platform=''amazon_ads''; campaign_type from campaign_bidding_strategy; daily_budget from campaign_budget_amount; currency from campaign_budget_currency_code; cost from source; revenue_7d from sales_7_d; revenue_30d from sales_30[截断，原长 4944 字符]
完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。
重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__unified_campaign_metrics.json#google_roas_rounding`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

### ctr_platform_fallthrough | Intent Misreading | 参与 | records/038_annotations/038_impl-006_int_ad_reporting__unified_campaign_metrics.md:56-94

point_id：`records/038_points.csv:24`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约为每个已命名平台规定HIGH/MEDIUM/else LOW，others才用1.0/0.5；SQL把低于本平台阈值的Google/Facebook也落入others分支，6行错分。两处WHEN属于同一个兜底条件点。
判定顺序：不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。
契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：
> business_logic: 'Combine four platform feeds into a standardized base and apply filters per source: - Amazon Ads (staging.stg_amazon_ads__campaign_report): - Map fields: platform=''amazon_ads''; campaign_type from campaign_bidding_strategy; daily_budget from campaign_budget_amount; currency from campaign_budget_currency_code; cost from source; revenue_7d from sales_7_d; revenue_30d from sales_30[截断，原长 4944 字符]
交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql`，`delivered SQL`：
> WHEN base.click_through_rate >= 1.0 THEN 'HIGH'
交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql`，`delivered SQL`：
> WHEN base.click_through_rate >= 0.5 THEN 'MEDIUM'
披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：
> business_logic: 'Combine four platform feeds into a standardized base and apply filters per source: - Amazon Ads (staging.stg_amazon_ads__campaign_report): - Map fields: platform=''amazon_ads''; campaign_type from campaign_bidding_strategy; daily_budget from campaign_budget_amount; currency from campaign_budget_currency_code; cost from source; revenue_7d from sales_7_d; revenue_30d from sales_30[截断，原长 4944 字符]
完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。
重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__unified_campaign_metrics.json#ctr_platform_fallthrough`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

## DAComp / impl-006_stg_amazon_ads__ad_group_report | main_category：Intent Misreading

### invalid_id_contract_delete | Intent Misreading | 主要 | records/038_annotations/038_impl-006_stg_amazon_ads__ad_group_report.md:21-69

point_id：`records/038_points.csv:45`；定位状态：已定位。

- 类别：Intent Misreading；角色：主要；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
ad_group_id的正则与delete_row动作均在契约写明；agent未过滤非法ID。采用契约删除实验，拒绝把gold置NULL诊断当作契约修复。
判定顺序：不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。
契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：
> - name: "ad_group_id"
>           data_type: VARCHAR
>           constraints: [not_null]
>           validation_rules:
>             - rule: "ad_group_id IS NOT NULL AND TRIM(ad_group_id) != ''"
>               on_failure: delete_row
>             - rule: "REGEXP_LIKE(ad_group_id, '^[A-Za-z0-9_-]{1,128}$')"
>               on_failure: delete_row
交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__ad_group_report.sql`，`delivered SQL`：
> SELECT * FROM cleaned
披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：
> - name: "ad_group_id"
>           data_type: VARCHAR
>           constraints: [not_null]
>           validation_rules:
>             - rule: "ad_group_id IS NOT NULL AND TRIM(ad_group_id) != ''"
>               on_failure: delete_row
>             - rule: "REGEXP_LIKE(ad_group_id, '^[A-Za-z0-9_-]{1,128}$')"
>               on_failure: delete_row
完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。
重跑/诊断：`records/020_reruns_impl-006_stg_amazon_ads__ad_group_report.json#invalid_id_contract_delete`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

## DAComp / impl-006_stg_apple_search_ads__ad_group_report | main_category：多因并列

### avg_cpa_currency | Intent Misreading | 并列 | records/038_annotations/038_impl-006_stg_apple_search_ads__ad_group_report.md:21-71

point_id：`records/038_points.csv:77`；定位状态：已定位。

- 类别：Intent Misreading；角色：并列；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约规定avg_cpa_currency须trim/upper后在USD/EUR/GBP/JPY/AUD/CAD中且长度3，否则nullify。038核实1500行均不在允许集，差异是非法值清理，不仅大小写呈现；按契约算法归Intent。
判定顺序：不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。
契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：
> - name: "avg_cpa_currency"
>           data_type: VARCHAR
>           validation_rules:
>             - rule: "avg_cpa_currency IS NULL OR avg_cpa_currency IN ('USD','EUR','GBP','JPY','AUD','CAD')"
>               on_failure: nullify_field
>             - rule: "LENGTH(avg_cpa_currency) <= 3"
>               on_failure: nullify_field
>             - rule: "avg_cpa_currency = UPPER(TRIM(avg_cpa_c[截断，原长 446 字符]
交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql`，`delivered SQL`：
> TRY_CAST("avg_cpa_currency" AS VARCHAR) AS avg_cpa_currency
披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：
> - name: "avg_cpa_currency"
>           data_type: VARCHAR
>           validation_rules:
>             - rule: "avg_cpa_currency IS NULL OR avg_cpa_currency IN ('USD','EUR','GBP','JPY','AUD','CAD')"
>               on_failure: nullify_field
>             - rule: "LENGTH(avg_cpa_currency) <= 3"
>               on_failure: nullify_field
>             - rule: "avg_cpa_currency = UPPER(TRIM(avg_cpa_c[截断，原长 446 字符]
完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。
重跑/诊断：`records/020_reruns_impl-006_stg_apple_search_ads__ad_group_report.json#avg_cpa_currency`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

### avg_cpt_currency | Intent Misreading | 并列 | records/038_annotations/038_impl-006_stg_apple_search_ads__ad_group_report.md:72-122

point_id：`records/038_points.csv:78`；定位状态：已定位。

- 类别：Intent Misreading；角色：并列；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约规定avg_cpt_currency须trim/upper后在USD/EUR/GBP/JPY/AUD/CAD中且长度3，否则nullify。038核实1500行均不在允许集，差异是非法值清理，不仅大小写呈现；按契约算法归Intent。
判定顺序：不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。
契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：
> - name: "avg_cpt_currency"
>           data_type: VARCHAR
>           validation_rules:
>             - rule: "avg_cpt_currency IS NULL OR avg_cpt_currency IN ('USD','EUR','GBP','JPY','AUD','CAD')"
>               on_failure: nullify_field
>             - rule: "LENGTH(avg_cpt_currency) <= 3"
>               on_failure: nullify_field
>             - rule: "avg_cpt_currency = UPPER(TRIM(avg_cpt_c[截断，原长 446 字符]
交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql`，`delivered SQL`：
> TRY_CAST("avg_cpt_currency" AS VARCHAR) AS avg_cpt_currency
披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：
> - name: "avg_cpt_currency"
>           data_type: VARCHAR
>           validation_rules:
>             - rule: "avg_cpt_currency IS NULL OR avg_cpt_currency IN ('USD','EUR','GBP','JPY','AUD','CAD')"
>               on_failure: nullify_field
>             - rule: "LENGTH(avg_cpt_currency) <= 3"
>               on_failure: nullify_field
>             - rule: "avg_cpt_currency = UPPER(TRIM(avg_cpt_c[截断，原长 446 字符]
完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。
重跑/诊断：`records/020_reruns_impl-006_stg_apple_search_ads__ad_group_report.json#avg_cpt_currency`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

### conversion_rate | Intent Misreading | 参与 | records/038_annotations/038_impl-006_stg_apple_search_ads__ad_group_report.md:123-165

point_id：`records/038_points.csv:79`；定位状态：已定位。

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。
契约明确0–1范围及nullify；未检查范围导致1469格差异。先适用契约算法，不因比例硬约束再记Data。
判定顺序：不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。
契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：
> - name: "conversion_rate"
>           data_type: DECIMAL(10,6)
>           validation_rules:
>             - rule: "conversion_rate BETWEEN 0 AND 1"
>               on_failure: nullify_field
交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql`，`delivered SQL`：
> TRY_CAST("conversion_rate" AS DECIMAL(10,6)) AS conversion_rate
披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：
> - name: "conversion_rate"
>           data_type: DECIMAL(10,6)
>           validation_rules:
>             - rule: "conversion_rate BETWEEN 0 AND 1"
>               on_failure: nullify_field
完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。
重跑/诊断：`records/020_reruns_impl-006_stg_apple_search_ads__ad_group_report.json#conversion_rate`。指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。

## DAComp / impl-008_asana__project_analytics | main_category：Intent Misreading

### time_management | Intent Misreading | 主要 | records/039_annotations/039_impl-008_asana__project_analytics.md:174-200

point_id：`records/039_points.csv:19`；定位状态：已定位。

主要；**Intent Misreading**；把握高。
P：time_management_score由完成比例及剩余天数决定。契约明确按schedule_forecast各档映射25/20/15/10/5，其他12；改变算法而非只改标签。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_reruns_impl-008_asana__project_analytics.json` / `time_management`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__project_analytics.sql` / `SQL.text`（sql）：
```text
CASE WHEN completion_percentage=100 THEN 25 WHEN remaining_days<0 THEN 5 ELSE 12 END time_management_score
```
否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

## DAComp / impl-008_asana__task_lifecycle_analysis | main_category：Unstated Choice

### modification_source | Intent Misreading | 参与 | records/039_annotations/039_impl-008_asana__task_lifecycle_analysis.md:253-298

point_id：`records/039_points.csv:23`；定位状态：已定位。

参与；**Intent Misreading**；把握高。
P：latest modification可直接取task.modified_at。契约要求最近故事活动时间；已有候选源，偏差在明文来源限定而非解析。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_supplement_reruns_impl-008_asana__task_lifecycle_analysis.json` / `modification_source`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__task_lifecycle_analysis.sql` / `SQL.text`（sql）：
```text
WITH story_agg AS (SELECT target_task_id,MIN(created_at) FILTER(WHERE action_taken='created') creation_timestamp,MIN(created_at) FILTER(WHERE action_taken='assigned') first_assignment_timestamp,MAX(created_at) FILTER(WHERE action_taken='assigned') last_assignment_timestamp,MAX(created_at) last_modification_timestamp,MIN(created_at) FILTER(WHERE action_taken='completed') completion_timestamp,COUNT([截断，原长 8845 字符]
```
否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

## DAComp / impl-008_asana__team_efficiency_metrics | main_category：多因并列

### medium_projects | Intent Misreading | 并列 | records/039_annotations/039_impl-008_asana__team_efficiency_metrics.md:209-234

point_id：`records/039_points.csv:24`；定位状态：已定位。

并列；**Intent Misreading**；把握高。
P：medium_projects按实际任务量分桶。契约本层project_size_category固定medium，分类来源与该规则不符。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json` / `medium_projects`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql` / `SQL.text`（sql）：
```text
COALESCE(ps.medium_projects,0)::BIGINT medium_projects
```
否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

### small_projects | Intent Misreading | 并列 | records/039_annotations/039_impl-008_asana__team_efficiency_metrics.md:235-260

point_id：`records/039_points.csv:25`；定位状态：已定位。

并列；**Intent Misreading**；把握高。
P：small_projects按实际任务量分桶。契约本层project_size_category固定medium，分类来源与该规则不符。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json` / `small_projects`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql` / `SQL.text`（sql）：
```text
COALESCE(ps.small_projects,0)::BIGINT small_projects
```
否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

## DAComp / impl-008_int_asana__task_performance_metrics | main_category：Intent Misreading

### timestamp_status | Intent Misreading | 主要 | records/039_annotations/039_impl-008_int_asana__task_performance_metrics.md:117-144

point_id：`records/039_points.csv:17`；定位状态：已定位。

主要；**Intent Misreading**；把握高。
P：完成是否及时可把completed_at与due_date都截为DATE。契约在完成状态使用时间戳比较，只有overdue使用日历日。截日会把同日迟交算成及时；按明文算法归Intent。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_reruns_impl-008_int_asana__task_performance_metrics.json` / `timestamp_status`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__task_performance_metrics.sql` / `SQL.text`（sql）：
```text
WHEN is_completed AND completed_at::DATE <= due_date::DATE THEN 'completed_on_time'
 WHEN is_completed AND completed_at::DATE > due_date::DATE THEN 'completed_late'
```
否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

## DAComp / impl-008_int_asana__task_projects | main_category：Data Misconception

### project_source | Data Misconception | 主要 | records/034_annotations/dacomp_impl-008_int_asana__task_projects.md:8-27

point_id：`records/036_points.csv:32`；定位状态：已定位。

- 角色：主要；类别：**Data Misconception**；把握：中。
- 依据：P：project_task中的project_id都能在project找到。可见上游查询44条不能匹配；只改p.project_id为pt.project_id，187→71行；同一来源也改变排序类型，不重复计算。
- 是否说出：看到了但没提。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/014_trace_impl-008.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 1 / args.content：
```text
int_asana__task_projects
      description: Task-project relationships with aggregated project IDs, names, and sections
      grain: One row per task_id
      source_models:
      - staging.stg_asana__project_task
      - staging.stg_asana__project
      - staging.stg_asana__task_section
      - staging.stg_asana__section
      business_logic: 'Build task-project relationships and aggregates: - St[截断，原长 866 字符]
```

## DAComp / impl-008_stg_asana__section | main_category：Intent Misreading

### required_project_id | Intent Misreading | 主要 | records/039_annotations/039_impl-008_stg_asana__section.md:54-84

point_id：`records/039_points.csv:33`；定位状态：已定位。

主要；**Intent Misreading**；把握高。
P：只检查原始project_id非空就满足BIGINT not_null。契约约束的是转换后的字段；解析后NULL仍被交出。
是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_reruns_impl-008_stg_asana__section.json` / `required_project_id`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/53.json` / `53.args.final_thought`（delivery）：
```text
staging 中对必需键为空或严重无效的记录进行过滤
```
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/staging/stg_asana__section.sql` / `SQL.text`（sql）：
```text
WHERE _rn = 1
```

## DAComp / impl-009_stg_google_play__stats_ratings_overview | main_category：Intent Misreading

### required_fields | Intent Misreading | 主要 | records/039_annotations/039_impl-009_stg_google_play__stats_ratings_overview.md:47-73

point_id：`records/039_points.csv:102`；定位状态：已定位。

主要；**Intent Misreading**；把握高。
P：date_day可以保留NULL。契约date_day/package_name显式not_null，交付SQL无必填过滤。finish点名installs_overview的缺日期不是本张ratings_overview；“基础投影/部分校验”不是对本处缺键政策的说明，故第4档。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_reruns_impl-009_stg_google_play__stats_ratings_overview.json` / `required_fields`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__stats_ratings_overview.sql` / `SQL.text`（sql）：
```text
FROM raw.stats_ratings_overview
```
否定披露的审计范围：finish event 67 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

## DAComp / impl-009_stg_google_play__store_performance_country | main_category：Unstated Choice

### lookup_dedup | Data Misconception | 参与 | records/034_annotations/dacomp_impl-009_stg_google_play__store_performance_country.md:20-35

point_id：`records/036_points.csv:34`；定位状态：已定位。

- 角色：参与；类别：**Data Misconception**；把握：中。
- 依据：P：lookup数值国家码唯一。250行只有246个码，4码各两条；单独去重15200→12800行。
- 是否说出：看到了但没提。
- 证据在场：否；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/014_trace_impl-009.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
实际可见列名/通用输出不能单凭它确定匹配或唯一性；核实查询为标注者事后执行。
event 14 / content：
```text
 None, None), ('package_name', 'VARCHAR', 'YES', None, None, None), ('country_region', 'BIGINT', 'YES', None, None, None), ('store_listing_acquisitions', 'BIGINT', 'YES', None, None, None), ('store_listing_visitors', 'BIGINT', 'YES', None, None, None), ('store_listing_conversion_rate', 'DOUBLE', 'YES', None, None, None)]
('store_performance_com.example.gameapp_US_202001_country.csv', 851, '2025-09[截断，原长 919 字符]
```
四档引句为关联证据；本处可见性另按在场栏判断，未将通用策略算成具体披露。

## DAComp / impl-010_stg_hubspot__engagement_email | main_category：Intent Misreading

### unique_engagement | Intent Misreading | 主要 | records/039_annotations/039_impl-010_stg_hubspot__engagement_email.md:62-88

point_id：`records/039_points.csv:120`；定位状态：已定位。

主要；**Intent Misreading**；把握高。
P：engagement_id重复可直接保留。契约明确unique；单改仅落实该约束。用last_modified选择保留项是诊断具体实现，不据此创造契约未写的优先级要求。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_reruns_impl-010_stg_hubspot__engagement_email.json` / `unique_engagement`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/staging/stg_hubspot__engagement_email.sql` / `SQL.text`（sql）：
```text
where engagement_id is not null
```
否定披露的审计范围：finish event 73 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

## DAComp / impl-011_int_jira__issue_calendar_spine | main_category：Intent Misreading

### unresolved_open_until | Intent Misreading | 主要 | records/039_annotations/039_impl-011_int_jira__issue_calendar_spine.md:61-87

point_id：`records/039_points.csv:123`；定位状态：已定位。

主要；**Intent Misreading**；把握高。
P：未解决issue也以最后历史记录日期作为结束日。契约明确未解决者延续到today；该条件改变日历范围。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_fast_reruns_impl-011_int_jira__issue_calendar_spine.json` / `unresolved_open_until`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_calendar_spine.sql` / `SQL.text`（sql）：
```text
with dates as (select unnest(generate_series(date '2016-01-01',current_date,interval 1 day))::date date_day), bounds as (select issue_id,cast(created_at as date) created_on,coalesce(cast(valid_starting_on as date),current_date) open_until from staging.stg_jira__issue i left join intermediate.int_jira__field_history_scd f using(issue_id)), joined as (select b.issue_id,d.date_day,min(b.open_until) e[截断，原长 755 字符]
```
否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

## DAComp / impl-011_int_jira__issue_lifecycle_analysis | main_category：Intent Misreading

### remove_many_to_many | Intent Misreading | 主要 | records/039_annotations/039_impl-011_int_jira__issue_lifecycle_analysis.md:110-136

point_id：`records/039_points.csv:125`；定位状态：已定位。

主要；**Intent Misreading**；把握高。
P：按issue聚合生命周期之前可额外连接该issue的所有history行。契约明确基于相邻活动变更区间计算次数和平均时长；这个额外多对多放大转移数，做法由规格定下，归Intent而非Data。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_reruns_impl-011_int_jira__issue_lifecycle_analysis.json` / `remove_many_to_many`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__issue_lifecycle_analysis.sql` / `SQL.text`（sql）：
```text
select h.issue_id,h.change_time,a.days_between_changes from h join a using(issue_id) where h.previous_change_time is not null
```
否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

## DAComp / impl-011_int_jira__pivot_daily_field_history | main_category：Intent Misreading

### status | Intent Misreading | 参与 | records/039_annotations/039_impl-011_int_jira__pivot_daily_field_history.md:71-96

point_id：`records/039_points.csv:127`；定位状态：已定位。

参与；**Intent Misreading**；把握高。
P：status在透视后统一COALESCE为is_null。契约要求在透视前把真实NULL变更标为is_null，未变更字段在透视后仍为NULL；agent把未变更也写成is_null，改变明确的状态语义。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_reruns_impl-011_int_jira__pivot_daily_field_history.json` / `status`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__pivot_daily_field_history.sql` / `SQL.text`（sql）：
```text
max(field_value) filter(where lower(field_id)='status') status
```
否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

### sprint | Intent Misreading | 参与 | records/039_annotations/039_impl-011_int_jira__pivot_daily_field_history.md:97-122

point_id：`records/039_points.csv:128`；定位状态：已定位。

参与；**Intent Misreading**；把握高。
P：sprint在透视后统一COALESCE为is_null。契约要求在透视前把真实NULL变更标为is_null，未变更字段在透视后仍为NULL；agent把未变更也写成is_null，改变明确的状态语义。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_reruns_impl-011_int_jira__pivot_daily_field_history.json` / `sprint`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__pivot_daily_field_history.sql` / `SQL.text`（sql）：
```text
max(field_value) filter(where lower(field_name)='sprint') sprint
```
否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

### story_points | Intent Misreading | 参与 | records/039_annotations/039_impl-011_int_jira__pivot_daily_field_history.md:123-148

point_id：`records/039_points.csv:129`；定位状态：已定位。

参与；**Intent Misreading**；把握高。
P：story_points在透视后统一COALESCE为is_null。契约要求在透视前把真实NULL变更标为is_null，未变更字段在透视后仍为NULL；agent把未变更也写成is_null，改变明确的状态语义。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_reruns_impl-011_int_jira__pivot_daily_field_history.json` / `story_points`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__pivot_daily_field_history.sql` / `SQL.text`（sql）：
```text
max(field_value) filter(where lower(field_name)='story points') story_points
```
否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

### story_point_estimate | Intent Misreading | 主要 | records/039_annotations/039_impl-011_int_jira__pivot_daily_field_history.md:149-175

point_id：`records/039_points.csv:130`；定位状态：已定位。

主要；**Intent Misreading**；把握高。
P：story_point_estimate在透视后统一COALESCE为is_null。契约要求在透视前把真实NULL变更标为is_null，未变更字段在透视后仍为NULL；agent把未变更也写成is_null，改变明确的状态语义。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_reruns_impl-011_int_jira__pivot_daily_field_history.json` / `story_point_estimate`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__pivot_daily_field_history.sql` / `SQL.text`（sql）：
```text
max(field_value) filter(where lower(field_name)='story point estimate') story_point_estimate
```
否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

## DAComp / impl-011_int_jira__sprint_performance_analytics | main_category：Quiet Downgrade

### timestamp_window | Intent Misreading | 参与 | records/039_annotations/039_impl-011_int_jira__sprint_performance_analytics.md:275-300

point_id：`records/039_points.csv:135`；定位状态：已定位。

参与；**Intent Misreading**；把握高。
P：sprint边界可以截为DATE。契约用时间戳限定承诺/完成窗口，截日会改变同日窗口内外。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_extra_reruns_impl-011_int_jira__sprint_performance_analytics.json` / `timestamp_window`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__sprint_performance_analytics.sql` / `SQL.text`（sql）：
```text
cast(i.created_at as date) between s.start_date
```
否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

### velocity_null_default | Intent Misreading | 参与 | records/039_annotations/039_impl-011_int_jira__sprint_performance_analytics.md:301-326

point_id：`records/039_points.csv:136`；定位状态：已定位。

参与；**Intent Misreading**；把握高。
P：没有速度基线可先COALESCE为0再分档。契约CASE明确NULL落ELSE Negative Velocity；不是任意缺失政策或纯标签呈现。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_detailed_reruns_impl-011_int_jira__sprint_performance_analytics.json` / `velocity_null_default`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__sprint_performance_analytics.sql` / `SQL.text`（sql）：
```text
case when coalesce(prev_remaining-remaining,0)>5 then 'High Velocity' when coalesce(prev_remaining-remaining,0)>2 then 'Good Velocity' when coalesce(prev_remaining-remaining,0)>0 then 'Low Velocity' when coalesce(prev_remaining-remaining,0)=0 then 'No Progress' else 'Negative Velocity' end
```
否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

## DAComp / impl-011_jira__issue_intelligence_analytics | main_category：Intent Misreading

### comparative_join_multiplicity | Intent Misreading | 主要 | records/039_annotations/039_impl-011_jira__issue_intelligence_analytics.md:154-179

point_id：`records/039_points.csv:138`；定位状态：已定位。

主要；**Intent Misreading**；把握高。
P：每issue输出一行足以满足本表。契约grain及self-join条款明确保留项目内自连接的重复行；漏掉规定关系改变粒度及计算输入，不是只改变呈现的Form。只恢复重复传播，不替代其他占位列。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_fast_reruns_impl-011_jira__issue_intelligence_analytics.json` / `comparative_join_multiplicity`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__issue_intelligence_analytics.sql` / `SQL.text`（sql）：
```text
from marts.jira__issue_enhanced
```
否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

## DAComp / impl-011_jira__team_performance_dashboard | main_category：Intent Misreading

### user_metrics_driver | Intent Misreading | 主要 | records/039_annotations/039_impl-011_jira__team_performance_dashboard.md:168-193

point_id：`records/039_points.csv:183`；定位状态：已定位。

主要；**Intent Misreading**；把握高。
P：以所有user为驱动并LEFT JOIN活动即可。契约明确从user metrics驱动并连接用户，agent多出无活动用户；范围由条款决定。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json` / `user_metrics_driver`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql` / `SQL.text`（sql）：
```text
from staging.stg_jira__user u left join intermediate.int_jira__user_metrics m using(user_id)
```
否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

### avg_daily_activity_score | Intent Misreading | 参与 | records/039_annotations/039_impl-011_jira__team_performance_dashboard.md:194-219

point_id：`records/039_points.csv:184`；定位状态：已定位。

参与；**Intent Misreading**；把握高。
avg_daily_activity_score对契约未COALESCE的nullable平均值额外补0；这是明文计算链的改动，不能被“团队dashboard简化”泛化为披露此NULL政策。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json` / `avg_daily_activity_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql` / `SQL.text`（sql）：
```text
coalesce(m.avg_close_time_days,0)::decimal(18,0) avg_daily_activity_score
```
否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

### avg_weekly_activity_score | Intent Misreading | 参与 | records/039_annotations/039_impl-011_jira__team_performance_dashboard.md:220-245

point_id：`records/039_points.csv:185`；定位状态：已定位。

参与；**Intent Misreading**；把握高。
avg_weekly_activity_score对契约未COALESCE的nullable平均值额外补0；这是明文计算链的改动，不能被“团队dashboard简化”泛化为披露此NULL政策。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。
重跑：`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json` / `avg_weekly_activity_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。
原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql` / `SQL.text`（sql）：
```text
coalesce(m.avg_close_time_days,0)::decimal(18,0) avg_weekly_activity_score
```
否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

## DAComp / impl-012_marketo__lead_intelligence_simple | main_category：多因并列

### missing_segment | Intent Misreading | 并列 | records/040_annotations/040_impl-012_marketo__lead_intelligence_simple.md:21-69

point_id：`records/040_points.csv:8`；定位状态：已定位。

并列；**Intent Misreading**；把握高。
没有engagement时应默认Unknown，agent先把次数补0再分段得到Inactive；这是默认业务规则未应用，不是数据事实误解。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。
证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。
曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。
系统提示是否适用：不适用。
来源：`records/022_reruns_impl-012_marketo__lead_intelligence_simple.json` / `missing_segment`。L0减少0行、376格。
原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）
```text
rfm_segment defaults to "Unknown", value_tier to "Basic", and lead_quality_tier to "Unqualified" when segmentation is missing.
```
原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）
```text
rfm_segment defaults to "Unknown", value_tier to "Basic", and lead_quality_tier to "Unqualified" when segmentation is missing.
```
原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/marts/marketo__lead_intelligence_simple.sql` / `text`（sql；普通SQL表达式不是披露）
```text
CASE WHEN total_lead_score>=100
```

## DAComp / impl-013_int_netsuite2__balance_sheet | main_category：Unstated Choice

### cta_branch | Intent Misreading | 参与 | records/040_annotations/040_impl-013_int_netsuite2__balance_sheet.md:21-69

point_id：`records/040_points.csv:16`；定位状态：已定位。

参与；**Intent Misreading**；把握高。
契约明确每条驱动交易再UNION ALL一条CTA；agent只输出主分支，遗漏规定的行范围。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。
证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。
曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。
系统提示是否适用：不适用。
来源：`records/022_reruns_impl-013_int_netsuite2__balance_sheet.json` / `cta_branch`。L0减少388行、8536格。
原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）
```text
Union all a second row per included transaction line to represent Cumulative Translation Adjustment (CTA):
```
原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）
```text
Union all a second row per included transaction line to represent Cumulative Translation Adjustment (CTA):
```
原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__balance_sheet.sql` / `text`（sql；普通SQL表达式不是披露）
```text
FROM presented
```

## DAComp / impl-013_int_netsuite2__customer_credit_risk | main_category：Intent Misreading

### zero_total_receivables | Intent Misreading | 并列 | records/040_annotations/040_impl-013_int_netsuite2__customer_credit_risk.md:21-69

point_id：`records/040_points.csv:20`；定位状态：已定位。

并列；**Intent Misreading**；把握高。
相关列描述always populated并有非空要求；空类别SUM FILTER返回NULL不符合此要求。依据非空明文，不能声称契约直接给了SUM CASE表达式。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。
证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。
曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。
系统提示是否适用：不适用。
来源：`records/022_reruns_impl-013_int_netsuite2__customer_credit_risk.json` / `zero_total_receivables`。L0减少0行、115格。
原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）
```text
        description: Sum of absolute converted_amount for Receivable transactions; always populated.
```
原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）
```text
        description: Sum of absolute converted_amount for Receivable transactions; always populated.
```
原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_credit_risk.sql` / `text`（sql；普通SQL表达式不是披露）
```text
sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctRec','Accounts Receivable')) total_receivables
```

### zero_total_collections | Intent Misreading | 并列 | records/040_annotations/040_impl-013_int_netsuite2__customer_credit_risk.md:70-118

point_id：`records/040_points.csv:21`；定位状态：已定位。

并列；**Intent Misreading**；把握高。
Payment类别没有行时SUM FILTER得到NULL；列描述要求always populated。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。
证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。
曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。
系统提示是否适用：不适用。
来源：`records/022_reruns_impl-013_int_netsuite2__customer_credit_risk.json` / `zero_total_collections`。L0减少0行、115格。
原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）
```text
        description: Sum of absolute converted_amount for Payment transactions; always populated.
```
原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）
```text
        description: Sum of absolute converted_amount for Payment transactions; always populated.
```
原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_credit_risk.sql` / `text`（sql；普通SQL表达式不是披露）
```text
sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Bank') total_collections
```

### zero_outstanding_receivables | Intent Misreading | 并列 | records/040_annotations/040_impl-013_int_netsuite2__customer_credit_risk.md:119-167

point_id：`records/040_points.csv:22`；定位状态：已定位。

并列；**Intent Misreading**；把握高。
Outstanding类别无行时输出NULL，违反该列always populated的明文。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。
证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。
曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。
系统提示是否适用：不适用。
来源：`records/022_reruns_impl-013_int_netsuite2__customer_credit_risk.json` / `zero_outstanding_receivables`。L0减少0行、115格。
原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）
```text
        description: Sum of absolute converted_amount where collection_status is Outstanding; always populated.
```
原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）
```text
        description: Sum of absolute converted_amount where collection_status is Outstanding; always populated.
```
原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__customer_credit_risk.sql` / `text`（sql；普通SQL表达式不是披露）
```text
sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctRec','Accounts Receivable')) outstanding_receivables
```

## DAComp / impl-013_int_netsuite2__customer_profitability | main_category：Intent Misreading

### percentile_score | Intent Misreading | 主要 | records/034_annotations/dacomp_impl-013_int_netsuite2__customer_profitability.md:8-18

point_id：`records/036_points.csv:41`；定位状态：已定位。

- 角色：主要；类别：**Intent Misreading**；把握：中。
- 依据：规格20/40/60/80百分位阈值，agent ntile(5)等量桶；2行4格→0。
- 是否说出：看到了但没提。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/016_trace_impl-013.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 1 / args.content：
```text
r_value_scoring: - revenue_score: 5 for total_revenue at or above the 80th percentile; 4 at or above the 60th; 3 at or above the 40th; 2 at or above the 20th; otherwise 1. Percentiles are computed over all rows in customer_segmentation (before the final filter). - frequency_score: 5 for 20 or more transactions; 4 for 10–19; 3 for 5–9; 2 for 2–4; otherwise 1. - margin_score: 5 for net_margin_pct at[截断，原长 920 字符]
```

## DAComp / impl-013_int_netsuite2__supplier_credit_monitoring | main_category：多因并列

### payment_zero | Intent Misreading | 并列 | records/040_annotations/040_impl-013_int_netsuite2__supplier_credit_monitoring.md:21-69

point_id：`records/040_points.csv:32`；定位状态：已定位。

并列；**Intent Misreading**；把握高。
契约明确total_payables非正时payment_ratio为0；agent NULLIF分母导致NULL。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。
证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。
曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。
系统提示是否适用：不适用。
来源：`records/022_reruns_impl-013_int_netsuite2__supplier_credit_monitoring.json` / `payment_zero`。L0减少0行、104格。
原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）
```text
payment_ratio: total_payments divided by total_payables when total_payables is positive; otherwise 0.
```
原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）
```text
payment_ratio: total_payments divided by total_payables when total_payables is positive; otherwise 0.
```
原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__supplier_credit_monitoring.sql` / `text`（sql；普通SQL表达式不是披露）
```text
coalesce(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name='Bank'),0)/nullif(sum(abs(t.converted_amount)) FILTER(WHERE t.account_type_name IN ('AcctPay','Accounts Payable')),0)
```

## DAComp / impl-013_int_netsuite__transaction_and_reporting_periods | main_category：Intent Misreading

### parse_period | Intent Misreading | 主要 | records/040_annotations/040_impl-013_int_netsuite__transaction_and_reporting_periods.md:21-77

point_id：`records/040_points.csv:45`；定位状态：已定位。

主要；**Intent Misreading**；把握高。
契约已经规定starting_at截到秒后解释timestamp；agent直接TRY_CAST偏移文本失败并过滤成空表。按给定算法优先判Intent，不把该事实改判Data。
是否说出：第2档——交付物里只有通用说明。交付物有适用于本类处理的通用说明，没有针对本表本处逐项说明。
证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。
曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。
系统提示是否适用：不适用。
来源：`records/022_reruns_impl-013_int_netsuite__transaction_and_reporting_periods.json` / `parse_period`。L0减少2230行、4460格。
原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）
```text
the multiplier''s starting_at, truncated to seconds and interpreted as a timestamp, is not later than the current time at evaluation.
```
原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）
```text
the multiplier''s starting_at, truncated to seconds and interpreted as a timestamp, is not later than the current time at evaluation.
```
原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/65.json` / `args.final_thought` / event 65（delivery；普通SQL表达式不是披露）
```text
采用 TRY_CAST 安全解析原始日期/类型；不可解析的值成为 NULL。
```
原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite__transaction_and_reporting_periods.sql` / `text`（sql；普通SQL表达式不是披露）
```text
try_cast(m.starting_at AS TIMESTAMP)
```

## DAComp / impl-013_netsuite2_customer_analytics | main_category：Intent Misreading

### second_join | Intent Misreading | 主要 | records/040_annotations/040_impl-013_netsuite2_customer_analytics.md:21-69

point_id：`records/040_points.csv:46`；定位状态：已定位。

主要；**Intent Misreading**；把握高。
业务逻辑明确customer_insights再从ecs LEFT JOIN cbp；agent跳过该连接，丢失44行的多重性。明文连接优先于笼统一客户一行描述。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。
证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。
曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。
系统提示是否适用：不适用。
来源：`records/022_reruns_impl-013_netsuite2_customer_analytics.json` / `second_join`。L0减少0行、1078格。
原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）
```text
customer_insights by left joining ecs to cbp on customer_id:
```
原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）
```text
customer_insights by left joining ecs to cbp on customer_id:
```
原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_customer_analytics.sql` / `text`（sql；普通SQL表达式不是披露）
```text
FROM enriched)
```

### frequency_zero | Intent Misreading | 参与 | records/040_annotations/040_impl-013_netsuite2_customer_analytics.md:70-118

point_id：`records/040_points.csv:47`；定位状态：已定位。

参与；**Intent Misreading**；把握高。
lifespan或active_months不正时频率应0；agent NULLIF得到NULL。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。
证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。
曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。
系统提示是否适用：不适用。
来源：`records/022_reruns_impl-013_netsuite2_customer_analytics.json` / `frequency_zero`。L0减少0行、137格。
原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）
```text
avg_transactions_per_month = total_transactions divided by (customer_lifespan_days/30.0) when active_months > 0 and customer_lifespan_days > 0; otherwise 0; no rounding.
```
原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）
```text
avg_transactions_per_month = total_transactions divided by (customer_lifespan_days/30.0) when active_months > 0 and customer_lifespan_days > 0; otherwise 0; no rounding.
```
原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_customer_analytics.sql` / `text`（sql；普通SQL表达式不是披露）
```text
total_transactions/nullif(customer_lifespan_days/30.0,0) avg_transactions_per_month
```

## DAComp / impl-013_netsuite2_operational_metrics | main_category：Intent Misreading

### zero_department_revenue | Intent Misreading | 主要 | records/040_annotations/040_impl-013_netsuite2_operational_metrics.md:21-69

point_id：`records/040_points.csv:56`；定位状态：已定位。

主要；**Intent Misreading**；把握高。
契约明确Income无匹配时revenue=0，agent SUM FILTER为NULL且最终排掉这些组，影响行数及后续窗口。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。
证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。
曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。
系统提示是否适用：不适用。
来源：`records/022_reruns_impl-013_netsuite2_operational_metrics.json` / `zero_department_revenue`。L0减少0行、12661格。
原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）
```text
department_revenue: sum of converted_amount where account type is Income; 0 if none.
```
原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）
```text
department_revenue: sum of converted_amount where account type is Income; 0 if none.
```
原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_operational_metrics.sql` / `text`（sql；普通SQL表达式不是披露）
```text
sum(t.converted_amount) FILTER(WHERE t.account_type_name='Income') department_revenue
```

### zero_net_margin_percentage | Intent Misreading | 参与 | records/040_annotations/040_impl-013_netsuite2_operational_metrics.md:223-271

point_id：`records/040_points.csv:60`；定位状态：已定位。

参与；**Intent Misreading**；把握高。
契约收入非正时净利率应0；agent NULLIF输出NULL。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整契约在event1初始提示中，构成相关信息；交付物未针对本处说明，也未找到比较其他做法或点出疑问的过程证据。只写实现本身不算第3档。
证据在场：是。相关条款完整出现在event1.user.message，与完整契约逐字匹配；不是被截断的命令输出。
曾经理解对过：否。逐表核读相关生成/修改事件，未见本点曾用正确规则计算后又回退；仅看到契约或写出实现计划不算曾经理解正确。
系统提示是否适用：不适用。
来源：`records/022_reruns_impl-013_netsuite2_operational_metrics.json` / `zero_net_margin_percentage`。L0减少0行、78格。
原句：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml` / `text`（contract；普通SQL表达式不是披露）
```text
net_margin_percentage: net_profit divided by revenue when revenue > 0; otherwise 0.
```
原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/1.json` / `message` / event 1（presence；普通SQL表达式不是披露）
```text
net_margin_percentage: net_profit divided by revenue when revenue > 0; otherwise 0.
```
原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_operational_metrics.sql` / `text`（sql；普通SQL表达式不是披露）
```text
(coalesce(department_revenue,0)-coalesce(department_cogs,0)-coalesce(department_expenses,0))/nullif(department_revenue,0) net_margin_percentage
```

## DAComp / impl-016_int_workday__organization_metrics | main_category：Intent Misreading

### tenure_all_assignments | Intent Misreading | 主要 | records/042_annotations/042_impl-016_int_workday__organization_metrics.md:25-65

point_id：`records/042_points.csv:10`；定位状态：已定位。

**Intent Misreading**；主要；把握高。
契约把avg_tenure_days列在all assignments的mobility段；agent从仅当前任职的current_stats取平均。本数据当前任职0不改变历史任职应纳入的明文要求。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。
证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。
曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。
证据：复用；`records/023_reruns_impl-016_int_workday__organization_metrics.json` / `tenure_all_assignments`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。
L0减少：[117, 117]（行、格）。
原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml` / `text`。
```text
Derive mobility from all assignments (historical and current), grouped by organization and source: new_hires_last_year counts distinct workers whose assignment started in the past year; departures_last_year counts distinct workers whose assignment ended in the past year; internal_transfers_in counts distinct workers who started in the past year and had any earlier assignment in a different organiz[截断，原长 850 字符]
```
原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json` / event 1 / `message`。
```text
Derive mobility from all assignments (historical and current), grouped by organization and source: new_hires_last_year counts distinct workers whose assignment started in the past year; departures_last_year counts distinct workers whose assignment ended in the past year; internal_transfers_in counts distinct workers who started in the past year and had any earlier assignment in a different organiz[截断，原长 850 字符]
```
原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/intermediate/int_workday__organization_metrics.sql` / `text`。
```text
coalesce(c.avg_tenure_days,0)::DOUBLE avg_tenure_days
```

## DAComp / impl-016_stg_workday__position | main_category：Intent Misreading

### validation_order | Intent Misreading | 主要 | records/042_annotations/042_impl-016_stg_workday__position.md:25-77

point_id：`records/042_points.csv:18`；定位状态：已定位。

**Intent Misreading**；主要；把握高。
employee_type规则先检查原值枚举，再TRIM纠正；agent先TRIM再验证，使2个原值非法的记录被救回。规则已有可执行条件，按Intent而非解析Choice或Data。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。
证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。
曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。
证据：复用；`records/023_reruns_impl-016_stg_workday__position.json` / `validation_order`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。
L0减少：[2, 2]（行、格）。
原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml` / `text`。
```text
- name: employee_type
          data_type: VARCHAR
          validation_rules:
            - rule: "employee_type IS NULL OR employee_type IN ('Regular', 'Contingent', 'Intern', 'Contractor')"
              on_failure: nullify_field
            - rule: "employee_type = TRIM(employee_type)"
              on_failure: correct
```
原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json` / event 1 / `message`。
```text
- name: employee_type
          data_type: VARCHAR
          validation_rules:
            - rule: "employee_type IS NULL OR employee_type IN ('Regular', 'Contingent', 'Intern', 'Contractor')"
              on_failure: nullify_field
            - rule: "employee_type = TRIM(employee_type)"
              on_failure: correct
```
原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/staging/stg_workday__position.sql` / `text`。
```text
TRIM(r.employee_type) NOT IN
```

## DAComp / impl-016_workday__organization_overview | main_category：多因并列

### annual_zero | Intent Misreading | 并列 | records/034_annotations/dacomp_impl-016_workday__organization_overview.md:8-18

point_id：`records/036_points.csv:45`；定位状态：已定位。

- 角色：并列；类别：**Intent Misreading**；把握：中。
- 依据：规格分母0返回0，NULLIF未补0；单改减少117格。
- 是否说出：看到了但没提。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/016_trace_impl-016.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 1 / args.content：
```text
employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_emp[截断，原长 920 字符]
```

### management_zero | Intent Misreading | 并列 | records/034_annotations/dacomp_impl-016_workday__organization_overview.md:19-29

point_id：`records/036_points.csv:46`；定位状态：已定位。

- 角色：并列；类别：**Intent Misreading**；把握：中。
- 依据：规格分母0返回0；单改减少117格。
- 是否说出：看到了但没提。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/016_trace_impl-016.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 1 / args.content：
```text
 average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum o[截断，原长 920 字符]
```

### roles_relationship | Intent Misreading | 参与 | records/034_annotations/dacomp_impl-016_workday__organization_overview.md:48-59

point_id：`records/036_points.csv:49`；定位状态：已定位。

- 角色：参与；类别：**Intent Misreading**；把握：中。
- 依据：规格明确worker/source/role/org连接，单改减少106格。
- 是否说出：看到了但没提。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/016_trace_impl-016.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 1 / args.content：
```text
employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_emp[截断，原长 920 字符]
```
四档引句为关联证据；本处可见性另按在场栏判断，未将通用策略算成具体披露。

### tenure_join_weight | Intent Misreading | 参与 | records/034_annotations/dacomp_impl-016_workday__organization_overview.md:60-72

point_id：`records/036_points.csv:50`；定位状态：已定位。

- 角色：参与；类别：**Intent Misreading**；把握：中。
- 依据：任期均值漏规格指定连接产生的权重，单改减少5格。
- 是否说出：看到了但没提。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/016_trace_impl-016.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 1 / args.content：
```text
employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_emp[截断，原长 920 字符]
```
四档引句为关联证据；本处可见性另按在场栏判断，未将通用策略算成具体披露。

## DAComp / impl-017_greenhouse__job_enhanced | main_category：Intent Misreading

### days_clock | Intent Misreading | 主要 | records/042_annotations/042_impl-017_greenhouse__job_enhanced.md:25-63

point_id：`records/042_points.csv:20`；定位状态：已定位。

**Intent Misreading**；主要；把握高。
days_since_created明定当前日期与created_at之间的天数；agent改用CURRENT_TIMESTAMP，改变时间范围，不是仅运行时点差异。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。
证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。
曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。
证据：复用；`records/023_reruns_impl-017_greenhouse__job_enhanced.json` / `days_clock`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。
L0减少：[1098, 1200]（行、格）。
原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml` / `text`。
```text
- name: days_since_created
        data_type: DOUBLE
        description: Days between the current date and created_at; updates daily and may be fractional
```
原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/1.json` / event 1 / `message`。
```text
- name: days_since_created
        data_type: DOUBLE
        description: Days between the current date and created_at; updates daily and may be fractional
```

### prospect_cast | Intent Misreading | 参与 | records/042_annotations/042_impl-017_greenhouse__job_enhanced.md:64-104

point_id：`records/042_points.csv:21`；定位状态：已定位。

**Intent Misreading**；参与；把握高。
契约给出prospect = 'True'可执行比较；agent先转VARCHAR，BOOLEAN转为小写true后不等于True。按引擎字面效果遵从规则，不推测契约本意。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。
证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。
曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。
证据：复用；`records/023_reruns_impl-017_greenhouse__job_enhanced.json` / `prospect_cast`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。
L0减少：[0, 40]（行、格）。
原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml` / `text`。
```text
prospect equals the string ''True''. Notes: all comparisons are exact, case-sensitive.
```
原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/1.json` / event 1 / `message`。
```text
prospect equals the string ''True''. Notes: all comparisons are exact, case-sensitive.
```
原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/marts/greenhouse__job_enhanced.sql` / `text`。
```text
prospect::VARCHAR = 'True'
```

## DAComp / impl-018_salesforce__daily_activity | main_category：Intent Misreading

### won_amount_null | Intent Misreading | 主要 | records/042_annotations/042_impl-018_salesforce__daily_activity.md:25-69

point_id：`records/042_points.csv:30`；定位状态：已定位。

**Intent Misreading**；主要；把握高。
契约仅在没有任何Won记录时补0；存在Won行但amount全NULL时SUM应为NULL。agent无条件COALESCE(sum,0)扩大补零范围。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。
证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。
曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。
证据：复用；`records/023_reruns_impl-018_salesforce__daily_activity.json` / `won_amount_null`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。
L0减少：[8, 8]（行、格）。
原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。
```text
- name: opportunities_won_amount
        data_type: DECIMAL(38,0)
        description: Sum of amounts for opportunities with close_date on date_day and status Won, rounded to 0 decimals; zero when close_date records exist but none Won; null when no close_date records.
```
原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。
```text
- name: opportunities_won_amount
        data_type: DECIMAL(38,0)
        description: Sum of amounts for opportunities with close_date on date_day and status Won, rounded to 0 decimals; zero when close_date records exist but none Won; null when no close_date records.
```
原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__daily_activity.sql` / `text`。
```text
coalesce(round(sum(amount) filter(where deal_status='Won')),0)
```

## DAComp / impl-018_salesforce__team_performance | main_category：Intent Misreading

### health_growth_null | Intent Misreading | 主要 | records/042_annotations/042_impl-018_salesforce__team_performance.md:25-65

point_id：`records/042_points.csv:31`；定位状态：已定位。

**Intent Misreading**；主要；把握高。
Revenue growth贡献明定>10给20、>0给15、>=-10给10、否则5；agent将NULL growth补0，落10而不是else5，改变健康分。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。
证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。
曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。
证据：复用；`records/023_reruns_impl-018_salesforce__team_performance.json` / `health_growth_null`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。
L0减少：[204, 496]（行、格）。
原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。
```text
Revenue growth: 20 if > 10%, else 15 if > 0%, else 10 if ≥ -10%, else 5
```
原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。
```text
Revenue growth: 20 if > 10%, else 15 if > 0%, else 10 if ≥ -10%, else 5
```
原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__team_performance.sql` / `text`。
```text
case when coalesce(revenue_growth_qoq_percentage,0)>10 then 20 when coalesce(revenue_growth_qoq_percentage,0)>0 then 15 when coalesce(revenue_growth_qoq_percentage,0)>=-10 then 10 else 5 end
```

### revenue_top | Intent Misreading | 参与 | records/042_annotations/042_impl-018_salesforce__team_performance.md:156-196

point_id：`records/042_points.csv:34`；定位状态：已定位。

**Intent Misreading**；参与；把握高。
top_revenue_performer明确按highest total won amount排名；agent按另一revenue_data聚合量排名。此处有明文，不把相邻sum/avg的歧义推广过来。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。
证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。
曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。
证据：复用；`records/023_reruns_impl-018_salesforce__team_performance.json` / `revenue_top`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。
L0减少：[0, 270]（行、格）。
原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。
```text
top_revenue_performer = the full_name of the member with the highest total won amount; members without a value are ranked last; ties are arbitrary
```
原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。
```text
top_revenue_performer = the full_name of the member with the highest total won amount; members without a value are ranked last; ties are arbitrary
```
原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__team_performance.sql` / `text`。
```text
arg_max(full_name,total_revenue_won) filter(where total_revenue_won is not null)
```

## DAComp / impl-020_int_intercom__conversation_part_aggregates | main_category：Data Misconception

### conversation_coverage | Data Misconception | 主要 | records/042_annotations/042_impl-020_int_intercom__conversation_part_aggregates.md:25-67

point_id：`records/042_points.csv:90`；定位状态：已定位。

**Data Misconception**；主要；把握中。
P：每个conversation至少有一条可连接的part，所以以part聚合为基表足以覆盖所有对话。契约For each conversation但没有指定LEFT JOIN算法；缺的是覆盖事实。023在agent可见库核实6703对话中5726个无匹配part；CS换gold上游时6703个全部无匹配，导致全表消失。以conversation为基表覆盖修复清零。
P：每个conversation至少有一条可连接的part。
是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。
证据在场：否。只看见相关字段/样例，未找到足以定下本点P的全量唯一性或覆盖核实出现在轨迹；不能用本次查询反填证据在场。
曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。
证据：复用；`records/023_supplement_reruns_impl-020_int_intercom__conversation_part_aggregates.json` / `conversation_coverage`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。
L0减少：[6703, 26812]（行、格）。
原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml` / `text`。
```text
For each conversation, compute counts of parts, assignments, and reopen events.
```
原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/1.json` / event 1 / `message`。
```text
For each conversation, compute counts of parts, assignments, and reopen events.
```
原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/intermediate/int_intercom__conversation_part_aggregates.sql` / `text`。
```text
from rollup r join staging.stg_intercom__conversation_history c on r.conversation_id=c.conversation_id
```

## DAComp / impl-021_int_klaviyo__person_metrics | main_category：Intent Misreading

### spine_days_count | Intent Misreading | 主要 | records/034_annotations/dacomp_impl-021_int_klaviyo__person_metrics.md:8-19

point_id：`records/036_points.csv:59`；定位状态：已定位。

- 角色：主要；类别：**Intent Misreading**；把握：中。
- 依据：规格明确missing_day_count equals the number of spine days that have no events on that exact date; multiple events on a day do not change this count。count(*)减distinct事件日违背指标定义；SQL第7行，2行2格→0。
- 是否说出：只有通用策略说明。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/017_trace_impl-021.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 41 / args.final_thought：
```text
事件 attribution 解析按契约优先级提取 JSON 子事件 ID，查找限定同一 `source_relation`；事件重复保留且照常计数。
```

## DAComp / impl-023_social_media_reporting__retention_kpis | main_category：Intent Misreading

### null_page | Intent Misreading | 主要 | records/043_annotations/043_impl-023_social_media_reporting__retention_kpis.md:86-140

point_id：`records/043_points.csv:41`；定位状态：已定位。

类别：**Intent Misreading**；角色：主要；把握：高。
输入规则只按created_timestamp是否存在过滤，随后为每个page/platform建立cohort；额外排除NULL page_id丢失13个spine行。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。
证据：`records/024_reruns_impl-023_social_media_reporting__retention_kpis.json`，条目 `null_page`。
基线：L0=13行/91格; L1=13行/91格; L2=13行/91格; L3=13行/91格。
单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：13行/91格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "    where page_id is not null",
    "new": "    where true",
    "offset": 1134
  }
]
```
是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：
```text
      - intermediate.social_media_reporting__twitter_posts_reporting
      - intermediate.social_media_reporting__youtube_videos_reporting
      business_logic: '- Inputs: - Union page activity from the five source models; only keep rows where created_timestamp is present. - Assign platform as one of: "facebook", "instagram", "linkedin", "twitter", "youtube". - Weekly normalization: - Bucket activ[截断，原长 2053 字符]
```
契约／过程证据（与上段重复的引句略）：
共同生成动作 `023-write-sql`；根源决定单元 `impl-023_social_media_reporting__retention_kpis:null_page`。

## DAComp / impl-023_social_media_reporting__twitter_posts_reporting | main_category：Intent Misreading

### created_timestamp | Intent Misreading | 主要 | records/043_annotations/043_impl-023_social_media_reporting__twitter_posts_reporting.md:31-85

point_id：`records/043_points.csv:37`；定位状态：已定位。

类别：**Intent Misreading**；角色：主要；把握：高。
契约明确取组内earliest date；实现改取tweet_created_at，改变时间值，是算法理解而非形式。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。
证据：`records/024_reruns_impl-023_social_media_reporting__twitter_posts_reporting.json`，条目 `created_timestamp`。
基线：L0=75行/75格; L1=75行/75格; L2=75行/75格; L3=75行/75格。
单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：75行/75格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "min(tweet_created_at)",
    "new": "min(date)",
    "offset": 536
  }
]
```
是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：
```text
      source_models:
      - staging.stg_social_media__twitter_organic_tweets
      business_logic: '- Input: include only records where organic_tweet_id is present. - Grouping: aggregate by organic_tweet_id and account_id to form post-level groups. - created_timestamp: earliest date in the group; null if all dates are missing. - post_message: the lexicographically last non-null tweet_text in the [截断，原长 2410 字符]
```
契约／过程证据（与上段重复的引句略）：
共同生成动作 `023-write-sql`；根源决定单元 `impl-023_social_media_reporting__twitter_posts_reporting:created_timestamp`。

## DAComp / impl-025_stg_twilio__call | main_category：Intent Misreading

### contact_phone_no_repair | Intent Misreading | 主要 | records/034_annotations/dacomp_impl-025_stg_twilio__call.md:8-18

point_id：`records/036_points.csv:65`；定位状态：已定位。

- 角色：主要；类别：**Intent Misreading**；把握：中。
- 依据：明确格式失败nullify_field，agent先去符号补国家码；2492→2482行。
- 是否说出：只有通用策略说明。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/017_trace_impl-025.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 41 / args.final_thought：
```text
依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。
```

### user_phone_no_repair | Intent Misreading | 参与 | records/034_annotations/dacomp_impl-025_stg_twilio__call.md:19-30

point_id：`records/036_points.csv:66`；定位状态：已定位。

- 角色：参与；类别：**Intent Misreading**；把握：中。
- 依据：同一策略用于另一独立列；2492→2483行。
- 是否说出：只有通用策略说明。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/017_trace_impl-025.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 41 / args.final_thought：
```text
依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。
```

## DAComp / impl-025_stg_twilio__incoming_phone_number | main_category：Intent Misreading

### phone_number_normalized | Intent Misreading | 主要 | records/043_annotations/043_impl-025_stg_twilio__incoming_phone_number.md:41-95

point_id：`records/043_points.csv:85`；定位状态：已定位。

类别：**Intent Misreading**；角色：主要；把握：高。
明确要求原电话匹配+1正则，失败nullify_field；先去标点补+1将本应置空的值改成有效，改变失败动作。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。
证据：`records/024_reruns_impl-025_stg_twilio__incoming_phone_number.json`，条目 `phone_number_normalized`。
基线：L0=1484行/1484格; L1=1484行/1484格; L2=1484行/1484格; L3=1484行/1484格。
单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：1484行/1484格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "regexp_replace(regexp_replace(phone_number, '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\\1') as phone_number_normalized",
    "new": "phone_number as phone_number_normalized",
    "offset": 546
  }
]
```
是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。报告说明验证失败置NULL，没有说明本点先去标点补+1、把本应失败的原值改成有效电话的处理；另一张outgoing_caller_id的点名说明也不推广。
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/output.jsonl`：
```text
          data_type: VARCHAR
          validation_rules:
            - rule: "phone_number RLIKE '^\\+1[0-9]{10}$'"
              on_failure: nullify_field
        - name: emergency_status
          data_type: VARCHAR
          validation_rules:
            - rule: "emergency_status IN ('Active','Inactive','Pending') OR emergency_status IS NULL"
              on_failure: nullify_field
        - na[截断，原长 580 字符]
```
契约／过程证据（与上段重复的引句略）：
共同生成动作 `025-write-sql`；根源决定单元 `025-phone-normalize`。

## DAComp / impl-025_stg_twilio__message | main_category：Intent Misreading

### from_normalized | Intent Misreading | 参与 | records/043_annotations/043_impl-025_stg_twilio__message.md:41-95

point_id：`records/043_points.csv:87`；定位状态：已定位。

类别：**Intent Misreading**；角色：参与；把握：高。
契约规定from正则验证失败置空；预先去标点补+1改变验证对象和失败动作。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。
证据：`records/024_reruns_impl-025_stg_twilio__message.json`，条目 `from_normalized`。
基线：L0=2495行/4972格; L1=2495行/4972格; L2=2495行/4972格; L3=2495行/4972格。
单改后：L0=2487行/2487格; L1=2487行/2487格; L2=2487行/2487格; L3=2487行/2487格。L0减量（先行后格）：8行/2485格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "regexp_replace(regexp_replace(\"from\", '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\\1') as from_normalized",
    "new": "\"from\" as from_normalized",
    "offset": 405
  }
]
```
是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。报告说明验证失败置NULL，没有说明本点先去标点补+1、把本应失败的原值改成有效电话的处理；另一张outgoing_caller_id的点名说明也不推广。
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/output.jsonl`：
```text
        - name: error_message
          data_type: VARCHAR
        - name: message_from
          data_type: VARCHAR
          validation_rules:
            - rule: "message_from RLIKE '^\\+1[0-9]{10}$'"
              on_failure: nullify_field
        - name: message_id
          data_type: VARCHAR
        - name: messaging_service_id
          data_type: VARCHAR
        - name: num_media
        [截断，原长 476 字符]
```
契约／过程证据（与上段重复的引句略）：
共同生成动作 `025-write-sql`；根源决定单元 `025-phone-normalize`。

### to_normalized | Intent Misreading | 主要 | records/043_annotations/043_impl-025_stg_twilio__message.md:96-147

point_id：`records/043_points.csv:88`；定位状态：已定位。

类别：**Intent Misreading**；角色：主要；把握：高。
契约规定to正则验证失败置空；预先标准化将非法原值变为合法值。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。
证据：`records/024_reruns_impl-025_stg_twilio__message.json`，条目 `to_normalized`。
基线：L0=2495行/4972格; L1=2495行/4972格; L2=2495行/4972格; L3=2495行/4972格。
单改后：L0=2485行/2485格; L1=2485行/2485格; L2=2485行/2485格; L3=2485行/2485格。L0减量（先行后格）：10行/2487格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "regexp_replace(regexp_replace(\"to\", '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\\1') as to_normalized",
    "new": "\"to\" as to_normalized",
    "offset": 813
  }
]
```
是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。报告说明验证失败置NULL，没有说明本点先去标点补+1、把本应失败的原值改成有效电话的处理；另一张outgoing_caller_id的点名说明也不推广。
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/output.jsonl`：
```text
            - rule: "status IN ('accepted','queued','sending','sent','failed','delivered','undelivered','receiving','received')"
              on_failure: nullify_field
        - name: message_to
          data_type: VARCHAR
          validation_rules:
            - rule: "message_to RLIKE '^\\+1[0-9]{10}$'"
              on_failure: nullify_field
        - name: updated_at
          data_type: TI[截断，原长 541 字符]
```
契约／过程证据（与上段重复的引句略）：
共同生成动作 `025-write-sql`；根源决定单元 `025-phone-normalize`。

## DAComp / impl-026_twitter_ads__promoted_tweet_report | main_category：Intent Misreading

### currency_source | Intent Misreading | 主要 | records/043_annotations/043_impl-026_twitter_ads__promoted_tweet_report.md:33-87

point_id：`records/043_points.csv:89`；定位状态：已定位。

类别：**Intent Misreading**；角色：主要；把握：高。
currency的来源明确是campaigns，agent改取line_items。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。
证据：`records/024_reruns_impl-026_twitter_ads__promoted_tweet_report.json`，条目 `currency_source`。
基线：L0=2032行/2532格; L1=2032行/2532格; L2=2032行/2532格; L3=2032行/2532格。
单改后：L0=20行/520格; L1=20行/520格; L2=20行/520格; L3=20行/520格。L0减量（先行后格）：2012行/2012格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "li.currency",
    "new": "c.currency",
    "offset": 202
  }
]
```
是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：
```text
    - name: twitter_ads__promoted_tweet_report
      description: Daily promoted tweet performance aggregated by placement and enriched with tweet, line item, campaign, and account attributes via left joins.
      grain: One row per unique combination of date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name,[截断，原长 2178 字符]
```
契约／过程证据（与上段重复的引句略）：
共同生成动作 `026-gen`；根源决定单元 `impl-026_twitter_ads__promoted_tweet_report:currency_source`。

### campaign_projection | Intent Misreading | 参与 | records/043_annotations/043_impl-026_twitter_ads__promoted_tweet_report.md:88-142

point_id：`records/043_points.csv:90`；定位状态：已定位。

类别：**Intent Misreading**；角色：参与；把握：高。
campaign_id应来自匹配后的campaigns；直接用line_items外键保留了无对应维度的值。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。
证据：`records/024_supplement_reruns_impl-026_twitter_ads__promoted_tweet_report.json`，条目 `campaign_projection`。
基线：L0=2032行/2532格; L1=2032行/2532格; L2=2032行/2532格; L3=2032行/2532格。
单改后：L0=2022行/2022格; L1=2022行/2022格; L2=2022行/2022格; L3=2022行/2022格。L0减量（先行后格）：10行/510格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "a.account_name, li.campaign_id",
    "new": "a.account_name, c.campaign_id",
    "offset": 50
  }
]
```
是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：
```text
    - name: twitter_ads__promoted_tweet_report
      description: Daily promoted tweet performance aggregated by placement and enriched with tweet, line item, campaign, and account attributes via left joins.
      grain: One row per unique combination of date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item_name, promoted_tweet_id, tweet_id, tweet_name,[截断，原长 2178 字符]
```
契约／过程证据（与上段重复的引句略）：
共同生成动作 `026-gen`；根源决定单元 `026-mart-campaign-projection`。

## DAComp / impl-026_twitter_ads__url_report | main_category：Intent Misreading

### campaign_projection | Intent Misreading | 主要 | records/043_annotations/043_impl-026_twitter_ads__url_report.md:33-87

point_id：`records/043_points.csv:92`；定位状态：已定位。

类别：**Intent Misreading**；角色：主要；把握：高。
契约明确campaign_id来自campaigns，agent取line_items的外键，缺维度时结果不同。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。
证据：`records/024_reruns_impl-026_twitter_ads__url_report.json`，条目 `campaign_projection`。
基线：L0=8行/8格; L1=8行/8格; L2=8行/8格; L3=8行/8格。
单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：8行/8格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "a.account_name, li.campaign_id",
    "new": "a.account_name, c.campaign_id",
    "offset": 50
  }
]
```
是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：
```text
    - name: twitter_ads__url_report
      description: Daily placement-level metrics for promoted tweets that have a first expanded URL, enriched with URL components and campaign/account/tweet attributes; metrics are summed across the grouped dimensions.
      grain: One row per unique combination of date_day, placement, account_id, account_name, campaign_id, campaign_name, line_item_id, line_item[截断，原长 2616 字符]
```
契约／过程证据（与上段重复的引句略）：
共同生成动作 `026-gen`；根源决定单元 `026-mart-campaign-projection`。

## DAComp / impl-030_stg_zuora__contact | main_category：Data Misconception

### source_account_id | Data Misconception | 主要 | records/043_annotations/043_impl-030_stg_zuora__contact.md:45-124

point_id：`records/043_points.csv:156`；定位状态：已定位。

类别：**Data Misconception**；角色：主要；把握：高。
P：本表实体id可作为account_id对应目标实体的关系键。实际纳入3741行，所选id匹配0，具名account_id匹配3738；非空候选3741个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为account_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 1, "result": {"col": "account_id", "n": 3741, "nonnull": 3741, "hex32": 3741, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 4, "result": {"col": "account_id", "n": 3741, "nonnull": 3741, "chosen_matches": 0, "named_matches": 3738}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__contact.json`，条目 `source_account_id`。
基线：L0=3741行/3741格; L1=3741行/3741格; L2=3741行/3741格; L3=3741行/3741格。
单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：3741行/3741格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS account_id",
    "new": "try_cast(\"account_id\" AS VARCHAR) AS account_id",
    "offset": 206
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
          data_type: VARCHAR
          source_expression: "id"
        - name: account_id
          data_type: VARCHAR
        - name: address_1
          data_type: VARCHAR
        - name: address_2
          data_type: VARCHAR
        - name: city
          data_type: VARCHAR
        - name: country
          data_type: VARCHAR
        - name: created_by_id
          data_type: VARCHAR
        -[截断，原长 419 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

## DAComp / impl-030_stg_zuora__credit_balance_adjustment | main_category：Data Misconception

### source_account_id | Data Misconception | 并列 | records/043_annotations/043_impl-030_stg_zuora__credit_balance_adjustment.md:45-124

point_id：`records/043_points.csv:157`；定位状态：已定位。

类别：**Data Misconception**；角色：并列；把握：高。
P：本表实体id可作为account_id对应目标实体的关系键。实际纳入6行，所选id匹配0，具名account_id匹配2；非空候选6个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为account_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 2, "result": {"col": "account_id", "n": 6, "nonnull": 6, "hex32": 6, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 5, "result": {"col": "account_id", "n": 6, "nonnull": 6, "chosen_matches": 0, "named_matches": 2}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__credit_balance_adjustment.json`，条目 `source_account_id`。
基线：L0=6行/12格; L1=6行/12格; L2=6行/12格; L3=6行/12格。
单改后：L0=6行/6格; L1=6行/6格; L2=6行/6格; L3=6行/6格。L0减量（先行后格）：0行/6格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS account_id",
    "new": "try_cast(\"account_id\" AS VARCHAR) AS account_id",
    "offset": 265
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: credit_balance_adjustment_id
          data_type: VARCHAR
        - name: account_id
          data_type: VARCHAR
        - name: account_receivable_accounting_code_id
          data_type: VARCHAR
        - name: accounting_code
          data_type: VARCHAR
        - name: adjustment_date
          data_type: DATE
        - name: amount
          data_type: DOUBLE
        - name: a[截断，原长 483 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

### source_invoice_id | Data Misconception | 并列 | records/043_annotations/043_impl-030_stg_zuora__credit_balance_adjustment.md:125-204

point_id：`records/043_points.csv:158`；定位状态：已定位。

类别：**Data Misconception**；角色：并列；把握：高。
P：本表实体id可作为invoice_id对应目标实体的关系键。实际纳入6行，所选id匹配0，具名invoice_id匹配6；非空候选6个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为invoice_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 2, "result": {"col": "invoice_id", "n": 6, "nonnull": 6, "hex32": 6, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 5, "result": {"col": "invoice_id", "n": 6, "nonnull": 6, "chosen_matches": 0, "named_matches": 6}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__credit_balance_adjustment.json`，条目 `source_invoice_id`。
基线：L0=6行/12格; L1=6行/12格; L2=6行/12格; L3=6行/12格。
单改后：L0=6行/6格; L1=6行/6格; L2=6行/6格; L3=6行/6格。L0减量（先行后格）：0行/6格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS invoice_id",
    "new": "try_cast(\"invoice_id\" AS VARCHAR) AS invoice_id",
    "offset": 1277
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: home_currency
          data_type: VARCHAR
        - name: invoice_id
          data_type: VARCHAR
        - name: journal_entry_id
          data_type: VARCHAR
        - name: number
          data_type: VARCHAR
        - name: parent_account_id
          data_type: VARCHAR
        - name: reason_code
          data_type: VARCHAR
        - name: reference_id
          data_type: V[截断，原长 441 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

## DAComp / impl-030_stg_zuora__invoice | main_category：多因并列

### account_source | Data Misconception | 并列 | records/036_annotations/dacomp_impl-030_stg_zuora__invoice.md:11-25

point_id：`records/036_points.csv:71`；定位状态：已定位。

- 角色：并列；类别：Data Misconception → **Data Misconception**。
- 是否说出：只有通用策略说明 → **交付物里只有通用说明**。
- 证据在场：否；曾经理解对过：否；系统提示是否适用：不适用（均沿用034）。
交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。
来源：`records/017_trace_impl-030.json`，事件/位置 `71.args.final_thought`。
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。非关键不可解析值转为 NULL。
```
证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-030_stg_zuora__invoice.md;records/017_trace_impl-030.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

### created_date_nullable | Intent Misreading | 参与 | records/036_annotations/dacomp_impl-030_stg_zuora__invoice.md:86-100

point_id：`records/036_points.csv:76`；定位状态：已定位。

- 角色：参与；类别：Intent Misreading → **Intent Misreading**。
- 是否说出：看到了但没提 → **交付物里只有通用说明**。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用（均沿用034）。
交付报告有适用于该类处理的通用说明，未点出本字段的具体约定/失误；不提升为第1档。
来源：`records/017_trace_impl-030.json`，事件/位置 `71.args.final_thought`。
```text
Staging 采用安全类型转换、删除标记过滤、更新时间驱动的最新记录标记；账户状态按契约规范化/过滤，invoice 创建日期按契约限制时间范围。
```
证据复用/新增：复用；036新核交付物/轨迹。来源：records/018_annotations/018_impl-030_stg_zuora__invoice.md;records/017_trace_impl-030.json;records/034_checks/dacomp_trace_presence.json;records/036_checks/disclosure_audit.json。

## DAComp / impl-030_stg_zuora__order | main_category：Data Misconception

### source_account_id | Data Misconception | 主要 | records/043_annotations/043_impl-030_stg_zuora__order.md:45-124

point_id：`records/043_points.csv:175`；定位状态：已定位。

类别：**Data Misconception**；角色：主要；把握：高。
P：本表实体id可作为account_id对应目标实体的关系键。实际纳入5行，所选id匹配0，具名account_id匹配2；非空候选5个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为account_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 5, "result": {"col": "account_id", "n": 5, "nonnull": 5, "hex32": 5, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 8, "result": {"col": "account_id", "n": 5, "nonnull": 5, "chosen_matches": 0, "named_matches": 2}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__order.json`，条目 `source_account_id`。
基线：L0=5行/5格; L1=5行/5格; L2=5行/5格; L3=5行/5格。
单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：5行/5格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS account_id",
    "new": "try_cast(\"account_id\" AS VARCHAR) AS account_id",
    "offset": 225
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: order_id
          data_type: VARCHAR
        - name: account_id
          data_type: VARCHAR
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: category
          data_type: VARCHAR
        - name: created_by_id
          data_type: BIGINT
        - name: created_date
          data_type: TIMESTAMP
        - name: default_payment_method_id
          da[截断，原长 444 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

## DAComp / impl-030_stg_zuora__payment | main_category：多因并列

### source_account_id | Data Misconception | 并列 | records/043_annotations/043_impl-030_stg_zuora__payment.md:47-126

point_id：`records/043_points.csv:176`；定位状态：已定位。

类别：**Data Misconception**；角色：并列；把握：高。
P：本表实体id可作为account_id对应目标实体的关系键。实际纳入722行，所选id匹配0，具名account_id匹配718；非空候选722个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为account_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 6, "result": {"col": "account_id", "n": 722, "nonnull": 722, "hex32": 722, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 9, "result": {"col": "account_id", "n": 722, "nonnull": 722, "chosen_matches": 0, "named_matches": 718}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__payment.json`，条目 `source_account_id`。
基线：L0=722行/4337格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。
单改后：L0=722行/3615格; L1=722行/2162格; L2=722行/2162格; L3=722行/726格。L0减量（先行后格）：0行/722格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS account_id",
    "new": "try_cast(\"account_id\" AS VARCHAR) AS account_id",
    "offset": 206
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
          data_type: VARCHAR
          source_expression: "id"
        - name: account_id
          data_type: VARCHAR
        - name: accounting_code
          data_type: VARCHAR
        - name: amount
          data_type: DOUBLE
        - name: amount_home_currency
          data_type: DOUBLE
        - name: applied_amount
          data_type: DOUBLE
        - name: applied_credit_balance_amount[截断，原长 463 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

### source_payment_method_id | Data Misconception | 并列 | records/043_annotations/043_impl-030_stg_zuora__payment.md:481-560

point_id：`records/043_points.csv:183`；定位状态：已定位。

类别：**Data Misconception**；角色：并列；把握：高。
P：本表实体id可作为payment_method_id对应目标实体的关系键。实际纳入722行，所选id匹配0，具名payment_method_id匹配718；非空候选722个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为payment_method_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 6, "result": {"col": "payment_method_id", "n": 722, "nonnull": 722, "hex32": 722, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 9, "result": {"col": "payment_method_id", "n": 722, "nonnull": 722, "chosen_matches": 0, "named_matches": 718}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__payment.json`，条目 `source_payment_method_id`。
基线：L0=722行/4337格; L1=722行/2884格; L2=722行/2884格; L3=722行/1448格。
单改后：L0=722行/3615格; L1=722行/2162格; L2=722行/2162格; L3=722行/726格。L0减量（先行后格）：0行/722格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS payment_method_id",
    "new": "try_cast(\"payment_method_id\" AS VARCHAR) AS payment_method_id",
    "offset": 1295
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: parent_account_id
          data_type: VARCHAR
        - name: payment_method_id
          data_type: VARCHAR
        - name: payment_number
          data_type: VARCHAR
        - name: refund_amount
          data_type: DOUBLE
        - name: settled_on
          data_type: TIMESTAMP
          source_expression: "try_cast(settled_on as TIMESTAMP)"
        - name: sold_to_contact_i[截断，原长 482 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

## DAComp / impl-030_stg_zuora__payment_method | main_category：Data Misconception

### source_account_id | Data Misconception | 主要 | records/043_annotations/043_impl-030_stg_zuora__payment_method.md:45-124

point_id：`records/043_points.csv:186`；定位状态：已定位。

类别：**Data Misconception**；角色：主要；把握：高。
P：本表实体id可作为account_id对应目标实体的关系键。实际纳入1037行，所选id匹配0，具名account_id匹配1030；非空候选1030个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为account_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 7, "result": {"col": "account_id", "n": 1037, "nonnull": 1030, "hex32": 1030, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 10, "result": {"col": "account_id", "n": 1037, "nonnull": 1030, "chosen_matches": 0, "named_matches": 1030}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__payment_method.json`，条目 `source_account_id`。
基线：L0=1037行/1037格; L1=1037行/1037格; L2=1037行/1037格; L3=1037行/1037格。
单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：1037行/1037格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS account_id",
    "new": "try_cast(\"account_id\" AS VARCHAR) AS account_id",
    "offset": 220
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
          data_type: VARCHAR
          source_expression: "id"
        - name: account_id
          data_type: VARCHAR
        - name: ach_account_type
          data_type: VARCHAR
        - name: active
          data_type: BOOLEAN
        - name: bank_transfer_account_type
          data_type: VARCHAR
        - name: created_by_id
          data_type: VARCHAR
        - name: created_date
       [截断，原长 486 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

## DAComp / impl-030_stg_zuora__product_rate_plan | main_category：Data Misconception

### source_product_id | Data Misconception | 主要 | records/043_annotations/043_impl-030_stg_zuora__product_rate_plan.md:165-244

point_id：`records/043_points.csv:191`；定位状态：已定位。

类别：**Data Misconception**；角色：主要；把握：中。
P：本表实体id可作为product_id对应目标实体的关系键。实际纳入505行，所选id匹配0，具名product_id匹配2；非空候选505个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。 目标覆盖仅2/505，支持该关系的匹配样本稀疏，因此把握为中；不另设类别最低匹配率门槛。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为product_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 8, "result": {"col": "product_id", "n": 505, "nonnull": 505, "hex32": 505, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 11, "result": {"col": "product_id", "n": 505, "nonnull": 505, "chosen_matches": 0, "named_matches": 2}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__product_rate_plan.json`，条目 `source_product_id`。
基线：L0=505行/1507格; L1=505行/1507格; L2=505行/1507格; L3=505行/505格。
单改后：L0=501行/1002格; L1=501行/1002格; L2=501行/1002格; L3=0行/0格。L0减量（先行后格）：4行/505格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS product_id",
    "new": "try_cast(\"product_id\" AS VARCHAR) AS product_id",
    "offset": 598
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: name
          data_type: VARCHAR
        - name: product_id
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_date
          data_type: TIMESTAMP
          source_expression: "cast(updated_date as TIMESTAMP)"
        - name: is_most_recent_record
          data_type: BOOLEAN
          source_expression: "row_number() ov[截断，原长 577 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

## DAComp / impl-030_stg_zuora__rate_plan | main_category：多因并列

### source_account_id | Data Misconception | 并列 | records/043_annotations/043_impl-030_stg_zuora__rate_plan.md:45-124

point_id：`records/043_points.csv:192`；定位状态：已定位。

类别：**Data Misconception**；角色：并列；把握：高。
P：本表实体id可作为account_id对应目标实体的关系键。实际纳入5行，所选id匹配0，具名account_id匹配1；非空候选5个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为account_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 9, "result": {"col": "account_id", "n": 5, "nonnull": 5, "hex32": 5, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 12, "result": {"col": "account_id", "n": 5, "nonnull": 5, "chosen_matches": 0, "named_matches": 1}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__rate_plan.json`，条目 `source_account_id`。
基线：L0=5行/25格; L1=5行/25格; L2=5行/25格; L3=5行/25格。
单改后：L0=5行/20格; L1=5行/20格; L2=5行/20格; L3=5行/20格。L0减量（先行后格）：0行/5格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS account_id",
    "new": "try_cast(\"account_id\" AS VARCHAR) AS account_id",
    "offset": 233
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: rate_plan_id
          data_type: VARCHAR
        - name: account_id
          data_type: VARCHAR
        - name: amendment_id
          data_type: VARCHAR
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: created_by_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
        - name: default_payment_method_id
   [截断，原长 446 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

### source_product_id | Data Misconception | 并列 | records/043_annotations/043_impl-030_stg_zuora__rate_plan.md:199-278

point_id：`records/043_points.csv:194`；定位状态：已定位。

类别：**Data Misconception**；角色：并列；把握：高。
P：本表实体id可作为product_id对应目标实体的关系键。实际纳入5行，所选id匹配0，具名product_id匹配5；非空候选5个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为product_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 9, "result": {"col": "product_id", "n": 5, "nonnull": 5, "hex32": 5, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 12, "result": {"col": "product_id", "n": 5, "nonnull": 5, "chosen_matches": 0, "named_matches": 5}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__rate_plan.json`，条目 `source_product_id`。
基线：L0=5行/25格; L1=5行/25格; L2=5行/25格; L3=5行/25格。
单改后：L0=5行/20格; L1=5行/20格; L2=5行/20格; L3=5行/20格。L0减量（先行后格）：0行/5格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS product_id",
    "new": "try_cast(\"product_id\" AS VARCHAR) AS product_id",
    "offset": 743
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: original_rate_plan_id
          data_type: VARCHAR
        - name: product_id
          data_type: VARCHAR
        - name: product_rate_plan_id
          data_type: VARCHAR
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: subscription_id
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_dat[截断，原长 470 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

### source_product_rate_plan_id | Data Misconception | 并列 | records/043_annotations/043_impl-030_stg_zuora__rate_plan.md:279-357

point_id：`records/043_points.csv:195`；定位状态：已定位。

类别：**Data Misconception**；角色：并列；把握：高。
P：本表实体id可作为product_rate_plan_id对应目标实体的关系键。实际纳入5行，所选id匹配0，具名product_rate_plan_id匹配1；非空候选5个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为product_rate_plan_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 9, "result": {"col": "product_rate_plan_id", "n": 5, "nonnull": 5, "hex32": 5, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 12, "result": {"col": "product_rate_plan_id", "n": 5, "nonnull": 5, "chosen_matches": 0, "named_matches": 1}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__rate_plan.json`，条目 `source_product_rate_plan_id`。
基线：L0=5行/25格; L1=5行/25格; L2=5行/25格; L3=5行/25格。
单改后：L0=5行/20格; L1=5行/20格; L2=5行/20格; L3=5行/20格。L0减量（先行后格）：0行/5格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS product_rate_plan_id",
    "new": "try_cast(\"product_rate_plan_id\" AS VARCHAR) AS product_rate_plan_id",
    "offset": 792
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: product_id
          data_type: VARCHAR
        - name: product_rate_plan_id
          data_type: VARCHAR
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: subscription_id
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_date
          data_type: TIMESTAMP
        - name: is_most_recent_rec[截断，原长 432 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

### source_subscription_id | Data Misconception | 并列 | records/043_annotations/043_impl-030_stg_zuora__rate_plan.md:358-432

point_id：`records/043_points.csv:196`；定位状态：已定位。

类别：**Data Misconception**；角色：并列；把握：高。
P：本表实体id可作为subscription_id对应目标实体的关系键。实际纳入5行，所选id匹配0，具名subscription_id匹配1；非空候选5个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为subscription_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 9, "result": {"col": "subscription_id", "n": 5, "nonnull": 5, "hex32": 5, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 12, "result": {"col": "subscription_id", "n": 5, "nonnull": 5, "chosen_matches": 0, "named_matches": 1}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__rate_plan.json`，条目 `source_subscription_id`。
基线：L0=5行/25格; L1=5行/25格; L2=5行/25格; L3=5行/25格。
单改后：L0=5行/20格; L1=5行/20格; L2=5行/20格; L3=5行/20格。L0减量（先行后格）：0行/5格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS subscription_id",
    "new": "try_cast(\"subscription_id\" AS VARCHAR) AS subscription_id",
    "offset": 924
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: subscription_id
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_date
          data_type: TIMESTAMP
        - name: is_most_recent_record
          data_type: BOOLEAN
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

## DAComp / impl-030_stg_zuora__rate_plan_charge | main_category：多因并列

### source_account_id | Data Misconception | 并列 | records/043_annotations/043_impl-030_stg_zuora__rate_plan_charge.md:45-124

point_id：`records/043_points.csv:197`；定位状态：已定位。

类别：**Data Misconception**；角色：并列；把握：高。
P：本表实体id可作为account_id对应目标实体的关系键。实际纳入4行，所选id匹配0，具名account_id匹配4；非空候选4个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为account_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 10, "result": {"col": "account_id", "n": 4, "nonnull": 4, "hex32": 4, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 13, "result": {"col": "account_id", "n": 4, "nonnull": 4, "chosen_matches": 0, "named_matches": 4}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__rate_plan_charge.json`，条目 `source_account_id`。
基线：L0=4行/24格; L1=4行/24格; L2=4行/24格; L3=4行/24格。
单改后：L0=4行/20格; L1=4行/20格; L2=4行/20格; L3=4行/20格。L0减量（先行后格）：0行/4格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS account_id",
    "new": "try_cast(\"account_id\" AS VARCHAR) AS account_id",
    "offset": 224
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
          data_type: VARCHAR
          source_expression: "id"
        - name: account_id
          data_type: VARCHAR
        - name: account_receivable_accounting_code_id
          data_type: VARCHAR
        - name: accounting_code
          data_type: VARCHAR
        - name: amended_by_order_on
          data_type: DATE
        - name: amendment_id
          data_type: VARCHAR
        - name: a[截断，原长 476 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

### source_product_id | Data Misconception | 并列 | records/043_annotations/043_impl-030_stg_zuora__rate_plan_charge.md:199-278

point_id：`records/043_points.csv:199`；定位状态：已定位。

类别：**Data Misconception**；角色：并列；把握：高。
P：本表实体id可作为product_id对应目标实体的关系键。实际纳入4行，所选id匹配0，具名product_id匹配2；非空候选4个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为product_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 10, "result": {"col": "product_id", "n": 4, "nonnull": 4, "hex32": 4, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 13, "result": {"col": "product_id", "n": 4, "nonnull": 4, "chosen_matches": 0, "named_matches": 2}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__rate_plan_charge.json`，条目 `source_product_id`。
基线：L0=4行/24格; L1=4行/24格; L2=4行/24格; L3=4行/24格。
单改后：L0=4行/20格; L1=4行/20格; L2=4行/20格; L3=4行/20格。L0减量（先行后格）：0行/4格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS product_id",
    "new": "try_cast(\"product_id\" AS VARCHAR) AS product_id",
    "offset": 3352
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: processed_through_date
          data_type: DATE
        - name: product_id
          data_type: VARCHAR
        - name: product_rate_plan_charge_id
          data_type: VARCHAR
        - name: product_rate_plan_id
          data_type: VARCHAR
        - name: quantity
          data_type: BIGINT
        - name: rate_plan_id
          data_type: VARCHAR
        - name: recognized_re[截断，原长 477 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

### source_product_rate_plan_id | Data Misconception | 并列 | records/043_annotations/043_impl-030_stg_zuora__rate_plan_charge.md:279-358

point_id：`records/043_points.csv:200`；定位状态：已定位。

类别：**Data Misconception**；角色：并列；把握：高。
P：本表实体id可作为product_rate_plan_id对应目标实体的关系键。实际纳入4行，所选id匹配0，具名product_rate_plan_id匹配3；非空候选4个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为product_rate_plan_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 10, "result": {"col": "product_rate_plan_id", "n": 4, "nonnull": 4, "hex32": 4, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 13, "result": {"col": "product_rate_plan_id", "n": 4, "nonnull": 4, "chosen_matches": 0, "named_matches": 3}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__rate_plan_charge.json`，条目 `source_product_rate_plan_id`。
基线：L0=4行/24格; L1=4行/24格; L2=4行/24格; L3=4行/24格。
单改后：L0=4行/20格; L1=4行/20格; L2=4行/20格; L3=4行/20格。L0减量（先行后格）：0行/4格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS product_rate_plan_id",
    "new": "try_cast(\"product_rate_plan_id\" AS VARCHAR) AS product_rate_plan_id",
    "offset": 3492
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: product_rate_plan_charge_id
          data_type: VARCHAR
        - name: product_rate_plan_id
          data_type: VARCHAR
        - name: quantity
          data_type: BIGINT
        - name: rate_plan_id
          data_type: VARCHAR
        - name: recognized_revenue_accounting_code_id
          data_type: VARCHAR
        - name: segment
          data_type: BOOLEAN
        - name[截断，原长 489 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

### source_rate_plan_id | Data Misconception | 并列 | records/043_annotations/043_impl-030_stg_zuora__rate_plan_charge.md:359-438

point_id：`records/043_points.csv:201`；定位状态：已定位。

类别：**Data Misconception**；角色：并列；把握：高。
P：本表实体id可作为rate_plan_id对应目标实体的关系键。实际纳入4行，所选id匹配0，具名rate_plan_id匹配1；非空候选4个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为rate_plan_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 10, "result": {"col": "rate_plan_id", "n": 4, "nonnull": 4, "hex32": 4, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 13, "result": {"col": "rate_plan_id", "n": 4, "nonnull": 4, "chosen_matches": 0, "named_matches": 1}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__rate_plan_charge.json`，条目 `source_rate_plan_id`。
基线：L0=4行/24格; L1=4行/24格; L2=4行/24格; L3=4行/24格。
单改后：L0=4行/20格; L1=4行/20格; L2=4行/20格; L3=4行/20格。L0减量（先行后格）：0行/4格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS rate_plan_id",
    "new": "try_cast(\"rate_plan_id\" AS VARCHAR) AS rate_plan_id",
    "offset": 3603
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: quantity
          data_type: BIGINT
        - name: rate_plan_id
          data_type: VARCHAR
        - name: recognized_revenue_accounting_code_id
          data_type: VARCHAR
        - name: segment
          data_type: BOOLEAN
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: specific_billing_period
          data_type: VARCHAR
        - name: spec[截断，原长 483 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

## DAComp / impl-030_stg_zuora__refund | main_category：Data Misconception

### source_payment_method_id | Data Misconception | 主要 | records/043_annotations/043_impl-030_stg_zuora__refund.md:45-124

point_id：`records/043_points.csv:203`；定位状态：已定位。

类别：**Data Misconception**；角色：主要；把握：高。
P：本表实体id可作为payment_method_id对应目标实体的关系键。实际纳入3行，所选id匹配0，具名payment_method_id匹配3；非空候选3个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为payment_method_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 11, "result": {"col": "payment_method_id", "n": 3, "nonnull": 3, "hex32": 3, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 14, "result": {"col": "payment_method_id", "n": 3, "nonnull": 3, "chosen_matches": 0, "named_matches": 3}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__refund.json`，条目 `source_payment_method_id`。
基线：L0=3行/3格; L1=3行/3格; L2=3行/3格; L3=3行/3格。
单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：3行/3格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS payment_method_id",
    "new": "try_cast(\"payment_method_id\" AS VARCHAR) AS payment_method_id",
    "offset": 614
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: method_type
          data_type: VARCHAR
        - name: payment_method_id
          data_type: VARCHAR
        - name: refund_date
          data_type: VARCHAR
        - name: refund_number
          data_type: VARCHAR
        - name: refund_transaction_time
          data_type: TIMESTAMP
          source_expression: "cast(refund_transaction_time as TIMESTAMP)"
        - name: sou[截断，原长 489 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

## DAComp / impl-030_stg_zuora__subscription | main_category：Data Misconception

### source_account_id | Data Misconception | 主要 | records/043_annotations/043_impl-030_stg_zuora__subscription.md:45-124

point_id：`records/043_points.csv:204`；定位状态：已定位。

类别：**Data Misconception**；角色：主要；把握：高。
P：本表实体id可作为account_id对应目标实体的关系键。实际纳入732行，所选id匹配0，具名account_id匹配730；非空候选732个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为account_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 12, "result": {"col": "account_id", "n": 732, "nonnull": 732, "hex32": 732, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 15, "result": {"col": "account_id", "n": 732, "nonnull": 732, "chosen_matches": 0, "named_matches": 730}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__subscription.json`，条目 `source_account_id`。
基线：L0=732行/732格; L1=732行/732格; L2=732行/732格; L3=732行/732格。
单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：732行/732格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS account_id",
    "new": "try_cast(\"account_id\" AS VARCHAR) AS account_id",
    "offset": 216
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
          data_type: VARCHAR
          source_expression: "id"
        - name: account_id
          data_type: VARCHAR
        - name: auto_renew
          data_type: BOOLEAN
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: cancel_reason
          data_type: VARCHAR
        - name: cancelled_date
          data_type: TIMESTAMP
          source_expression: "cast(cance[截断，原长 496 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

## DAComp / impl-030_stg_zuora__taxation_item | main_category：多因并列

### source_product_id | Data Misconception | 并列 | records/043_annotations/043_impl-030_stg_zuora__taxation_item.md:579-658

point_id：`records/043_points.csv:213`；定位状态：已定位。

类别：**Data Misconception**；角色：并列；把握：高。
P：本表实体id可作为product_id对应目标实体的关系键。实际纳入534行，所选id匹配0，具名product_id匹配5；非空候选5个均为ID格式。契约未指定该外键source_expression，数据关系足以否定P，归Data Misconception。
证据在场：否；曾经理解对过：是；系统提示是否适用：不适用。
P：本表实体id可作为product_id对应目标实体的关系键。
agent见过列名和自身SQL，未见目标实体匹配对照或足以定下此关系的反证；不能把列清单当作P已被否定的在场证据。
反证核实结果：`{"format_query": {"source": "records/024_mapping_queries.json", "index": 13, "result": {"col": "product_id", "n": 534, "nonnull": 5, "hex32": 5, "timestamps": 0}}, "mapping_query": {"source": "records/024_extra_diagnostics.json", "index": 16, "result": {"col": "product_id", "n": 534, "nonnull": 5, "chosen_matches": 0, "named_matches": 5}}}`。
同源决定：event45 将pk_alias集合中外键名一律改取本表id；event19曾按正确同名源列写代码。event45是为处理实体主键缺列报错而主动引入的统一映射，不是同一字典的无意重复键覆盖；故不因曾写对过就改判代码写错。
证据：`records/024_reruns_impl-030_stg_zuora__taxation_item.json`，条目 `source_product_id`。
基线：L0=534行/5884格; L1=534行/5864格; L2=534行/5864格; L3=534行/5864格。
单改后：L0=534行/5350格; L1=534行/5330格; L2=534行/5330格; L3=534行/5330格。L0减量（先行后格）：0行/534格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "try_cast(\"id\" AS VARCHAR) AS product_id",
    "new": "try_cast(\"product_id\" AS VARCHAR) AS product_id",
    "offset": 1438
  }
]
```
是否说出：**第2档——交付物里只有通用说明**。说明了id映射这一类做法，但未点名此表外键，也未说明关系未核实；只记第2档。
event 71 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```
契约／过程证据（与上段重复的引句略）：
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
        - name: payment_amount
          data_type: DOUBLE
        - name: product_id
          data_type: VARCHAR
        - name: product_rate_plan_charge_id
          data_type: VARCHAR
        - name: product_rate_plan_id
          data_type: VARCHAR
        - name: rate_plan_charge_id
          data_type: VARCHAR
        - name: rate_plan_id
          data_type: VARCHAR
        - name: sales_t[截断，原长 493 字符]
```
event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
srcname=n
            e=f'try_cast("{srcname}" AS {typ})'
```
event 45 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
if n in pk_alias: srcname='id'
```
共同生成动作 `030-gen-stage`；根源决定单元 `impl-030-event45-pk_alias`。

## DAComp / impl-030_zuora__account_overview | main_category：Intent Misreading

### invoice_items_left | Intent Misreading | 主要 | records/043_annotations/043_impl-030_zuora__account_overview.md:33-87

point_id：`records/043_points.csv:146`；定位状态：已定位。

类别：**Intent Misreading**；角色：主要；把握：高。
契约明确有invoice而无item时计数0；INNER JOIN丢掉这样的账户分组。做法可由规格确定，不用Data覆盖事实替代。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。
证据：`records/024_reruns_impl-030_zuora__account_overview.json`，条目 `invoice_items_left`。
基线：L0=454行/454格; L1=454行/454格; L2=454行/454格; L3=454行/454格。
单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：454行/454格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "JOIN intermediate.int_zuora__invoice_item_base AS ii",
    "new": "LEFT JOIN intermediate.int_zuora__invoice_item_base AS ii",
    "offset": 168
  }
]
```
是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
      - intermediate.int_zuora__invoice_item_base
      - intermediate.int_zuora__billing_enriched
      business_logic: '- Base: Start from intermediate.int_zuora__account_current (assumed one current row per account_id). - Contact: Left join intermediate.int_zuora__contact_current on account_id; if no contact row, all contact fields are NULL. - Invoice item count: - Build items_by_account by joi[截断，原长 2420 字符]
```
契约／过程证据（与上段重复的引句略）：
共同生成动作 `030-account-command`；根源决定单元 `impl-030_zuora__account_overview:invoice_items_left`。

## DAComp / impl-030_zuora__monthly_recurring_revenue | main_category：Intent Misreading

### spine_null_month | Intent Misreading | 主要 | records/043_annotations/043_impl-030_zuora__monthly_recurring_revenue.md:33-87

point_id：`records/043_points.csv:147`；定位状态：已定位。

类别：**Intent Misreading**；角色：主要；把握：高。
契约要求覆盖spine的所有account/month；额外非空服务日期过滤丢掉NULL月份行。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。
证据：`records/024_reruns_impl-030_zuora__monthly_recurring_revenue.json`，条目 `spine_null_month`。
基线：L0=1行/8格; L1=1行/8格; L2=1行/8格; L3=1行/8格。
单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：1行/8格。
单改替换（除此之外不变；复用024重跑记录）：
```json
[
  {
    "old": "    WHERE service_start_day IS NOT NULL",
    "new": "    WHERE TRUE",
    "offset": 175
  }
]
```
是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。
event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/output.jsonl`：
```text
      - intermediate.int_zuora__invoice_item_base
      - intermediate.int_zuora__rate_plan_charge_current
      business_logic: '- Inputs: - From intermediate.int_zuora__invoice_item_base: account_id, service_start_day, rate_plan_charge_id, charge_amount, discount_amount. - From intermediate.int_zuora__rate_plan_charge_current: rate_plan_charge_id, charge_type. - Build the month spine as distinct[截断，原长 2397 字符]
```
契约／过程证据（与上段重复的引句略）：
共同生成动作 `030-mrr-command`；根源决定单元 `impl-030_zuora__monthly_recurring_revenue:spine_null_month`。

## KramaBench / archeology-hard-1 | main_category：Intent Misreading

### 只平均两个端点 | Intent Misreading | 主要 | records/036_annotations/kramabench_archeology-hard-1.md:11-26

point_id：`records/036_points.csv:83`；定位状态：已定位。

- 角色：主要；类别：Intent Misreading → **Intent Misreading**。
- 是否说出：针对本处的具体说明 → **过程中意识到了，交付物里没提**。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用（均沿用034）。
中间明确用两端日期插值取平均；最终仅数值，未解释这个范围口径。
来源：`records/028_kramabench_packages/archeology-hard-1.md`，事件/位置 `step.8.reasoning.1`。
```text
**Calculating average potassium levels**
I need to determine the average potassium level in ppm from the first and last recorded times of a study in the Maltese area. I'm looking at the earliest date, around 6412 BP, and the latest at about 6005 BP. It seems like I should use these direct radiocarbon dates to interpolate and calculate the average. So, I’ll get started on that calculation!
```
证据复用/新增：复用；036新核交付物/轨迹。来源：records/028_kramabench_packages/archeology-hard-1.md;records/032_kramabench_queries/04_archeology_hard_1.stdout.txt;records/034_checks/archeology-hard-1_interval_mean.json;records/036_checks/disclosure_audit.json;records/036_checks/endpoint_audit.json。

## KramaBench / astronomy-hard-9 | main_category：Data Misconception

### OMNI列号错位 | Data Misconception | 主要 | records/034_annotations/kramabench_astronomy-hard-9.md:20-35

point_id：`records/036_points.csv:93`；定位状态：已定位。

- 角色：主要；类别：**Data Misconception**；把握：高。
P：header=None的om[50]是ap-index。文档WORD50=ap-index、WORD51=f10.7，Python列49才是ap；032只改om[50]→om[49]，lag47→24，差23→0。
- 是否说出：看到了但没提；证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
在场判断：题面本身已提供范围/规则的项以query原文为证；数据值与编码项只认实际反馈保留内容。没有把子任务作为agent依据。
轨迹事件 `step.5.code` 原文（代码行从本代码块1起计）：
```text
for i,line in enumerate(spec.splitlines()):
 if 'ap-index' in line.lower() or 'F10.7' in line: print(i,line)
```
轨迹事件 `step.5.feedback` 原文（代码行从本代码块1起计）：
```text
25     ap-index and f10.7_index
166 50       I4   999      ap-index                     nT
```
证据：records/028_kramabench_packages/astronomy-hard-9.md；records/032_kramabench_queries/06_astronomy_hard_9.stdout.txt。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。

## KramaBench / biomedical-easy-2 | main_category：Intent Misreading

### 未落实研究纳入范围 | Intent Misreading | 主要 | records/034_annotations/kramabench_biomedical-easy-2.md:20-35

point_id：`records/036_points.csv:94`；定位状态：已定位。

- 角色：主要；类别：**Intent Misreading**；把握：中。
题面限定研究中的Serous样本；Case_excluded的含义明确，agent未落实排除标记。68.1对68.5；排除Case_excluded=Yes后12行平均68.5。只见列名不足确定这14行中的具体排除事实。
- 是否说出：看到了但没提；证据在场：否；曾经理解对过：否；系统提示是否适用：不适用。
在场判断：题面本身已提供范围/规则的项以query原文为证；数据值与编码项只认实际反馈保留内容。没有把子任务作为agent依据。
轨迹事件 `step.4.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Calculating mean age of tumor samples**
I want to calculate the mean age of serous tumor samples, which might involve looking at metadata that includes tumor types and patient age. I think I need to filter the data for the histologic type "serous" and I’m estimating that there are likely about 14 samples here. Maybe I should also consider if any age data is missing. I’ll need to check the rows t[截断，原长 437 字符]
```
轨迹事件 `step.4.code` 原文（代码行从本代码块1起计）：
```text
ser=d[(d['Histologic_type'].astype(str).str.strip().str.lower()=='serous') & (d['Proteomics_Tumor_Normal']=='Tumor')]; print(ser.shape); print(ser[['Proteomics_Participant_ID','Proteomics_Tumor_Normal','Histologic_type','Age']].to_string(index=False)); print('mean',ser.Age.mean(),'count',ser.Age.count(),'missing',ser.Age.isna().sum())
```
证据：records/028_kramabench_packages/biomedical-easy-2.md；records/032_kramabench_queries/07_biomedical_serous.stdout.txt。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。

## KramaBench / biomedical-hard-5 | main_category：Intent Misreading

### 未落实研究纳入范围 | Intent Misreading | 主要 | records/034_annotations/kramabench_biomedical-hard-5.md:20-39

point_id：`records/036_points.csv:96`；定位状态：已定位。

- 角色：主要；类别：**Intent Misreading**；把握：中。
题面限定研究中的Serous样本；Case_excluded的含义明确，agent未落实排除标记。2.4241对2.6563；排除后12行线性尺度中位数2.6563。只见列名不足确定这14行中的具体排除事实。
- 是否说出：看到了但没提；证据在场：否；曾经理解对过：否；系统提示是否适用：不适用。
在场判断：题面本身已提供范围/规则的项以query原文为证；数据值与编码项只认实际反馈保留内容。没有把子任务作为agent依据。
轨迹事件 `step.6.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Analyzing variant density**
I’m working on understanding the number of variants per Mbp and considering that it might relate to base 2 log values. It seems important to check the B-APM subtypes and possibly focus on serious tumor samples based on Histology. I’m also weighing the possibility of using log2 values, like log2(variants per Mbp +1). If my calculations are right, I believe I can derive[截断，原长 898 字符]
```
轨迹事件 `step.6.code` 原文（代码行从本代码块1起计）：
```text
s=meta[meta.Histologic_type.eq('Serous')]
print(s.shape, s['Log2_variant_per_Mbp'].isna().sum()); print(s[['Proteomics_Participant_ID','Log2_variant_per_Mbp','Log2_variant_total']].to_string(index=False)); import numpy as np
print('median log',s.Log2_variant_per_Mbp.median(),'2^median',2**s.Log2_variant_per_Mbp.median(),'median pow',np.median(2**s.Log2_variant_per_Mbp))
```
证据：records/028_kramabench_packages/biomedical-hard-5.md；records/032_kramabench_queries/07_biomedical_serous.stdout.txt。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。

## KramaBench / environment-easy-3 | main_category：Intent Misreading

### 擅限Boston Harbor | Intent Misreading | 主要 | records/036_annotations/kramabench_environment-easy-3.md:11-32

point_id：`records/036_points.csv:99`；定位状态：已定位。

- 角色：主要；类别：Intent Misreading → **Intent Misreading**。
- 是否说出：针对本处的具体说明 → **过程中意识到了，交付物里没提**。
- 证据在场：是；曾经理解对过：是；系统提示是否适用：不适用（均沿用034）。
最终答案没有说明该处；第3档依据所引中间事件对做法、前提或呈现的明确表述。
来源：`records/028_kramabench_packages/environment-easy-3.md`，事件/位置 `step.9.reasoning.1`。
```text
**Evaluating beach data**
I need to identify the beaches mentioned in the user's question. The reference to Boston Harbor points to nine specific beaches, and I should focus on those. My task likely involves comparing bacterial exceedance rates from 2013 and 2012, which means I'll check the datasets to find relevant violations. It's important to exclude beaches without 2012 samples when counting, [截断，原长 1582 字符]
```
证据复用/新增：复用；036新核交付物/轨迹。来源：records/028_kramabench_packages/environment-easy-3.md;records/034_checks/environment-easy-3_all_beaches.json;records/036_checks/disclosure_audit.json;records/036_checks/endpoint_audit.json。

## KramaBench / environment-hard-16 | main_category：Intent Misreading

### 擅限Boston Harbor | Intent Misreading | 主要 | records/036_annotations/kramabench_environment-hard-16.md:11-26

point_id：`records/036_points.csv:102`；定位状态：已定位。

- 角色：主要；类别：Intent Misreading → **Intent Misreading**。
- 是否说出：看到了但没提 → **过程中意识到了，交付物里没提**。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用（均沿用034）。
最终答案没有说明该处；第3档依据所引中间事件对做法、前提或呈现的明确表述。
来源：`records/028_kramabench_packages/environment-hard-16.md`，事件/位置 `step.4.reasoning.1`。
```text
**Identifying beach violations**
I need to identify target beaches and look for all occurrences of violations, even though there are multiple sampling locations. For Boston, there seems to be a list of nine beaches, and Castle Island might also go by other names. I’ll aggregate marine records to find relevant patterns and violations from 2002 to 2023. Then, I’ll load all the files by year, normali[截断，原长 473 字符]
```
证据复用/新增：复用；036新核交付物/轨迹。来源：records/028_kramabench_packages/environment-hard-16.md;records/034_checks/environment-hard-16_identity_diagnostic.json;records/036_checks/disclosure_audit.json;records/036_checks/endpoint_audit.json。

## KramaBench / legal-hard-18 | main_category：Intent Misreading

### 保留2007身份盗窃数量 | Intent Misreading | 主要 | records/034_annotations/kramabench_legal-hard-18.md:20-36

point_id：`records/036_points.csv:110`；定位状态：已定位。

- 角色：主要；类别：**Intent Misreading**；把握：高。
题面If the 2007 reports were distributed exactly like the 2024 ones；agent用2007已观测identity count259314而非总1070447乘2024类别比率。替换该基数得到91000，126000差35000→0。
- 是否说出：看到了但没提；证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
在场判断：题面本身已提供范围/规则的项以query原文为证；数据值与编码项只认实际反馈保留内容。没有把子任务作为agent依据。
轨迹事件 `step.5.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Calculating age distribution for reports**
I could calculate the sum of age 40+ for overall identity theft reports in 2024. It seems like this approach would adjust the statistics by excluding ages that aren't reported as 40 or older. The user's intention might be to determine the percentage of reports that fall into the 40+ age range. I'd need to apply this distribution, parse the data, and com[截断，原长 452 字符]
```
轨迹事件 `step.5.code` 原文（代码行从本代码块1起计）：
```text
vals=[21420,187195,291807,207658,135758,83485,36790,9605]
known=sum(vals); over40=sum(vals[4:]); print(known,over40,over40/known,259314*over40/known, round(259314*over40/known/1000)*1000, 259314*over40/1135291)
```
证据：records/028_kramabench_packages/legal-hard-18.md；records/034_checks/legal-hard-18_retry.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。

## KramaBench / wildfire-hard-17 | main_category：Intent Misreading

### 未限定实际火场监测站 | Intent Misreading | 主要 | records/034_annotations/kramabench_wildfire-hard-17.md:20-43

point_id：`records/036_points.csv:119`；定位状态：已定位。

- 角色：主要；类别：**Intent Misreading**；把握：中。
题面weather stations used for fire site monitoring，agent平均全部2965个registry记录，未按fire.station_verified_in_psa筛。以NWS ID匹配759行均值4830.8524，round1=4830.9；3317.37差1513.53→0。
- 是否说出：看到了但没提；证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
在场判断：题面本身已提供范围/规则的项以query原文为证；数据值与编码项只认实际反馈保留内容。没有把子任务作为agent依据。
轨迹事件 `step.3.reasoning.1` 原文（代码行从本代码块1起计）：
```text
**Calculating average elevation**
I'm considering the user's request about the average elevation of weather stations used for fire site monitoring in the NOAA dataset. I'll need to calculate the mean elevation, likely removing any null values. First, I should inspect the dataset's shape, check for missing data, and gather some descriptive statistics, especially around station uniqueness and total [截断，原长 514 字符]
```
轨迹事件 `step.3.code` 原文（代码行从本代码块1起计）：
```text
p=os.path.join(base,'PublicView_RAWS_-3515561676727363726.csv')
raw=pd.read_csv(p,encoding='cp1252',low_memory=False)
print(raw.shape)
print([(repr(c),raw[c].dtype,raw[c].isna().sum()) for c in raw.columns[:12]])
elevcol=[c for c in raw.columns if 'Elevation' in c][0]
e= pd.to_numeric(raw[elevcol],errors='coerce')
print('elevation count',e.count(),'missing',e.isna().sum(),'mean',e.mean(),'median',[截断，原长 542 字符]
```
证据：records/028_kramabench_packages/wildfire-hard-17.md；records/034_checks/wildfire-hard-17_id_diagnostic.json。复用028/030/032；034新增确定性诊断或原代码局部重放（如存在链接）。

## KramaBench / wildfire-hard-6 | main_category：Data Misconception

### 误缩短NOAA覆盖起点 | Data Misconception | 主要 | records/036_annotations/kramabench_wildfire-hard-6.md:11-26

point_id：`records/036_points.csv:124`；定位状态：已定位。

- 角色：主要；类别：Data Misconception → **Data Misconception**。
- 是否说出：针对本处的具体说明 → **过程中意识到了，交付物里没提**。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用（均沿用034）。
中间明确声称NOAA从2000开始；最终相关覆盖前提没有交代。
来源：`records/028_kramabench_packages/wildfire-hard-6.md`，事件/位置 `step.4.reasoning.1`。
```text
**Assessing NOAA and NIFC data**
I’m looking at NOAA monthly stats beginning from the year 2000, which include annual totals. I’ll compute the sums for each year, especially since there's overlap with NIFC data. To do this, I might focus on the monthly aggregates provided by NOAA. I’ll parse the data using `pd.read_csv`, skipping the first two rows to get relevant info. Also, I want to assess the [截断，原长 489 字符]
```
证据复用/新增：复用；036新核交付物/轨迹。来源：records/028_kramabench_packages/wildfire-hard-6.md;records/032_kramabench_queries/08_wildfire_hard_6.stdout.txt;records/036_checks/disclosure_audit.json。
