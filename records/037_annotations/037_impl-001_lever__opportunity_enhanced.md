# impl-001_lever__opportunity_enhanced（037 正式批次）

主要原因：**Intent Misreading**；把握：高。019旧主要原因原样保留：`C`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__opportunity_enhanced.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，finish 67 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-001_lever__opportunity_enhanced.json`；037补充：`records/037_checks/`。

## 逐点标注

### candidate_partition

- 类别：Intent Misreading；角色：主要；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约明确按candidate选择最新offer，agent按opportunity分区；改动涉及行对应，不是文字形式。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: '- Use intermediate.int_lever__opportunity_contact_info as the base; each output row represents one opportunity_id from this base. - Inner join staging.stg_lever__stage on stage_id to add current_stage; opportunities without a matching stage are excluded. - Left join staging.stg_lever__archive_reason on archived_reason_id to add archive_reason; if no match, archive_reason is NULL. - Left join intermediate.int_lever__opportunity_tags on opportunity_id to add tags; if no match, tags is NULL. - Determine the most recent offer per candidate by ordering each candidate’s offers by created_at descending and selecting the single most recent record; if multiple offers have the same created_at for a candidate, one is chosen arbitrarily. - Left join this most recent offer to opportunities on opportunity_id; set has_offer to true when a most recent offer exists for this opportunity, otherwise false; set current_offer_status to the joined offer’s status or NULL if no offer joined. - Left join staging.stg_lever__posting on posting_id to add job_title, job_commitment, job_location, job_team, and current_state_of_job_posting; if no match, these fields are NULL. - All other columns are passed through unchanged from the base; NULLs and original values are preserved. No explicit ordering is applied in the result.'

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__opportunity_enhanced.sql`，第 1–1 行：

```sql
PARTITION BY opportunity_id ORDER BY created_at DESC
```

单改/诊断：`records/019_reruns_impl-001_lever__opportunity_enhanced.json#candidate_partition`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 285/9975 | 0/0 | 285/9975 |
| L1 | 285/9975 | 0/0 | 285/9975 |
| L2 | 285/9975 | 0/0 | 285/9975 |
| L3 | 285/9975 | 0/0 | 285/9975 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：

> business_logic: '- Use intermediate.int_lever__opportunity_contact_info as the base; each output row represents one opportunity_id from this base. - Inner join staging.stg_lever__stage on stage_id to add current_stage; opportunities without a matching stage are excluded. - Left join staging.stg_lever__archive_reason on archived_reason_id to add archive_reason; if no match, archive_reason is NULL. - Left join intermediate.int_lever__opportunity_tags on opportunity_id to add tags; if no match, tags is NULL. - Determine the most recent offer per candidate by ordering each candidate’s offers by created_at descending and selecting the single most recent record; if multiple offers have the same created_at for a candidate, one is chosen arbitrarily. - Left join this most recent offer to opportunities on opportunity_id; set has_offer to true when a most recent offer exists for this opportunity, otherwise false; set current_offer_status to the joined offer’s status or NULL if no offer joined. - Left join staging.stg_lever__posting on posting_id to add job_title, job_commitment, job_location, job_team, and current_state_of_job_posting; if no match, these fields are NULL. - All other columns are passed through unchanged from the base; NULLs and original values are preserved. No explicit ordering is applied in the result.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
