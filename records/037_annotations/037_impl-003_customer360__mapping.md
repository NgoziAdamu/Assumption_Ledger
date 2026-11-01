# impl-003_customer360__mapping（037 正式批次）

主要原因：**Intent Misreading**；把握：高。019旧主要原因原样保留：`C`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__mapping.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，finish 51 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-003_customer360__mapping.json`；037补充：`records/037_checks/`。

## 逐点标注

### outer_source

- 类别：Intent Misreading；角色：主要；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约明确FULL OUTER JOIN后再UNION unmatched，agent把第一组连接写成LEFT JOIN；此算法已规定，不归Data。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: '1) Load four inputs: source_matches, marketo, stripe, zendesk. 2) Build combine_all_results: - Chain full outer joins: source_matches to marketo on lead_id, then to stripe on customer_id from source_matches, then to zendesk on user_id from source_matches, retaining all records from every source. - For IDs, prefer the value from source_matches when present; otherwise use the corresponding source table value. - Per-row timestamps: - marketo_updated_at = the most recent non-null updated_at among marketo/stripe/zendesk for that row, taking source_matches timestamps when available, else the source table’s. - marketo_created_at = the earliest non-null created_at among marketo/stripe/zendesk for that row, taking source_matches timestamps when available, else the source table’s. - stripe_updated_at / stripe_created_at = the stripe timestamp from source_matches when present, otherwise from stripe. - zendesk_updated_at / zendesk_created_at = the zendesk timestamp from source_matches when present, otherwise from zendesk. - zendesk_organization_* = the zendesk organization timestamps from source_matches when present, otherwise from zendesk.organization_*. - Union in three additional sets to also include any marketo/stripe/zendesk records whose IDs are not present in source_matches; these rows carry only their own system fields, others null. This can yield duplicates relative to the full outer joins. 3) For each row, derive customer360_organization_id by hashing the pipe-joined values (marketo org name without suffix, marketo inferred org name without suffix, stripe customer org name without suffix, stripe shipping org name without suffix, zendesk organization_id), treating nulls as empty strings. 4) Emit two row types: - Individual rows (is_organization_header=false): include the three source IDs; source_ids is a compact JSON-like object {"marketo":"...","stripe":"...","zendesk":"..."} where null IDs are rendered as empty strings; timestamps are the per-row values from step 2. - One organization header row per customer360_organization_id (is_organization_header=true): source IDs are null; source_ids is a JSON-like object with arrays per system containing distinct quoted IDs for that organization (comma-delimited, no spaces), with nulls rendered as empty strings; timestamps aggregated per organization as latest updated_at and earliest created_at for each system; zendesk organization timestamps use latest for updated and earliest for created. 5) Assign customer360_id by hashing the pipe-joined values (marketo_lead_id, stripe_customer_id, zendesk_user_id, is_organization_header, customer360_organization_id), treating nulls as empty strings and using the engine’s string form of the boolean.'

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__mapping.sql`，第 1–11 行：

```sql

 select sm.marketo_lead_id, sm.stripe_customer_id, sm.zendesk_user_id,
        m.organization_name_no_suffix as m_org, m.inferred_organization_name_no_suffix as mi_org,
        s.customer_organization_name_no_suffix as s_org, s.shipping_organization_name_no_suffix as ss_org,
        z.organization_id, sm.marketo_updated_at, sm.marketo_created_at, sm.stripe_updated_at, sm.stripe_created_at,
        sm.zendesk_updated_at, sm.zendesk_organization_updated_at, sm.zendesk_created_at, sm.zendesk_organization_created_at
 from intermediate.int_customer360__source_matches sm
 left join intermediate.int_customer360__marketo m on sm.marketo_lead_id=m.lead_id
 left join intermediate.int_customer360__stripe s on sm.stripe_customer_id=s.customer_id
 left join intermediate.int_customer360__zendesk z on sm.zendesk_user_id=z.user_id

```

单改/诊断：`records/019_reruns_impl-003_customer360__mapping.json#outer_source`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 6515/41771 | 663/663 | 5852/41108 |
| L1 | 6515/41771 | 663/663 | 5852/41108 |
| L2 | 6515/41771 | 663/663 | 5852/41108 |
| L3 | 6515/41771 | 663/663 | 5852/41108 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，event `1.message`：

> business_logic: '1) Load four inputs: source_matches, marketo, stripe, zendesk. 2) Build combine_all_results: - Chain full outer joins: source_matches to marketo on lead_id, then to stripe on customer_id from source_matches, then to zendesk on user_id from source_matches, retaining all records from every source. - For IDs, prefer the value from source_matches when present; otherwise use the corresponding source table value. - Per-row timestamps: - marketo_updated_at = the most recent non-null updated_at among marketo/stripe/zendesk for that row, taking source_matches timestamps when available, else the source table’s. - marketo_created_at = the earliest non-null created_at among marketo/stripe/zendesk for that row, taking source_matches timestamps when available, else the source table’s. - stripe_updated_at / stripe_created_at = the stripe timestamp from source_matches when present, otherwise from stripe. - zendesk_updated_at / zendesk_created_at = the zendesk timestamp from source_matches when present, otherwise from zendesk. - zendesk_organization_* = the zendesk organization timestamps from source_matches when present, otherwise from zendesk.organization_*. - Union in three additional sets to also include any marketo/stripe/zendesk records whose IDs are not present in source_matches; these rows carry only their own system fields, others null. This can yield duplicates relative to the full outer joins. 3) For each row, derive customer360_organization_id by hashing the pipe-joined values (marketo org name without suffix, marketo inferred org name without suffix, stripe customer org name without suffix, stripe shipping org name without suffix, zendesk organization_id), treating nulls as empty strings. 4) Emit two row types: - Individual rows (is_organization_header=false): include the three source IDs; source_ids is a compact JSON-like object {"marketo":"...","stripe":"...","zendesk":"..."} where null IDs are rendered as empty strings; timestamps are the per-row values from step 2. - One organization header row per customer360_organization_id (is_organization_header=true): source IDs are null; source_ids is a JSON-like object with arrays per system containing distinct quoted IDs for that organization (comma-delimited, no spaces), with nulls rendered as empty strings; timestamps aggregated per organization as latest updated_at and earliest created_at for each system; zendesk organization timestamps use latest for updated and earliest for created. 5) Assign customer360_id by hashing the pipe-joined values (marketo_lead_id, stripe_customer_id, zendesk_user_id, is_organization_header, customer360_organization_id), treating nulls as empty strings and using the engine’s string form of the boolean.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### source_ids_order

- 类别：其他；角色：参与；把握：中。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

source_ids的JSON数组只有无序集合成员先后差异；契约未规定数组排序。037双侧只规范数组顺序的诊断隔离此点。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: source_ids
>         data_type: VARCHAR
>         description: 'JSON-like string; individual rows: {"marketo":"...","stripe":"...","zendesk":"..."} with nulls as empty strings; header rows: arrays per system of distinct quoted IDs joined by commas (no spaces), nulls as empty strings, order not enforced.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__mapping.sql`，第 26–26 行：

```sql
 '{"marketo":"'||coalesce(marketo_lead_id::varchar,'')||'","stripe":"'||coalesce(stripe_customer_id,'')||'","zendesk":"'||coalesce(zendesk_user_id::varchar,'')||'"}' as source_ids,
```

单改/诊断：`records/037_checks/order_diagnostics.json#source_ids_order`。双侧只改呈现的诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 6523/41779 | 5876/41132 | 647/647 |
| L1 | 6523/41779 | 5876/41132 | 647/647 |
| L2 | 6523/41779 | 5876/41132 | 647/647 |
| L3 | 6523/41779 | 5876/41132 | 647/647 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，event `51.args.final_thought`：

> 契约对来源重复记录以及部分聚合排序并未规定唯一 tie-breaker；按 DuckDB 实际行为保留未指定并列顺序，不额外引入业务假设。

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
