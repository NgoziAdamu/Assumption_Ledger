# impl-001_int_lever__posting_applications（037 正式批次）

主要原因：**其他**；把握：高。019旧主要原因原样保留：`O`，不作为新类别依据。

## 范围与材料

- 层：intermediate；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_applications.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，finish 67 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-001_int_lever__posting_applications.json`；037补充：`records/037_checks/`。

## 逐点标注

### tie_order

- 类别：其他；角色：主要；把握：高。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约允许created_at并列时由引擎任取。019双侧admissible诊断均为0；本点是允许的并列先后，不是取错经理。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: '- Read all application rows from staging.stg_lever__application. - Aggregate per posting_id: - first_app_sent_at: the earliest non-null created_at; if all created_at values are NULL, this is NULL. - count_referred_applications: number of rows where type equals ''referral''; exact match, NULL or other values do not count. - count_posting_applications: number of rows where type equals ''posting'' or ''agency''; exact matches only. - count_manual_user_applications: number of rows where type equals ''user''; exact match. - count_opportunities: number of distinct non-null opportunity_id. - count_open_opportunities: number of distinct non-null opportunity_id where archived_at is NULL. - Determine posting_hiring_manager_user_id by selecting, for each posting_id, the application with the latest created_at; if multiple rows share the same created_at or created_at is NULL, tie-breaking and NULL ordering follow the engine defaults; take that row''s posting_hiring_manager_user_id (may be NULL). - Inner join the aggregates with the latest-application selection on posting_id; posting_id values that are NULL do not match and are excluded, and only posting_ids with at least one application appear. - Output one row per non-null posting_id present in the application data.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_applications.sql`，第 1–1 行：

```sql
ORDER BY created_at DESC
```

单改/诊断：`records/019_reruns_impl-001_int_lever__posting_applications.json#tie_order`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 299/299 | 280/280 | 19/19 |
| L1 | 299/299 | 280/280 | 19/19 |
| L2 | 299/299 | 280/280 | 19/19 |
| L3 | 299/299 | 280/280 | 19/19 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，event `1.message`：

> business_logic: '- Read all application rows from staging.stg_lever__application. - Aggregate per posting_id: - first_app_sent_at: the earliest non-null created_at; if all created_at values are NULL, this is NULL. - count_referred_applications: number of rows where type equals ''referral''; exact match, NULL or other values do not count. - count_posting_applications: number of rows where type equals ''posting'' or ''agency''; exact matches only. - count_manual_user_applications: number of rows where type equals ''user''; exact match. - count_opportunities: number of distinct non-null opportunity_id. - count_open_opportunities: number of distinct non-null opportunity_id where archived_at is NULL. - Determine posting_hiring_manager_user_id by selecting, for each posting_id, the application with the latest created_at; if multiple rows share the same created_at or created_at is NULL, tie-breaking and NULL ordering follow the engine defaults; take that row''s posting_hiring_manager_user_id (may be NULL). - Inner join the aggregates with the latest-application selection on posting_id; posting_id values that are NULL do not match and are excluded, and only posting_ids with at least one application appear. - Output one row per non-null posting_id present in the application data.'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：

`records/019_queries.json` / 核实：
```sql
SELECT count(*) tied_groups,sum(n-1) excess_rows FROM (SELECT posting_id,created_at,count(*) n FROM staging.stg_lever__application GROUP BY ALL HAVING count(*)>1)
```
结果：`[[0, null]]`

`records/019_queries.json` / 诊断：
```sql
SELECT count(*) non_admissible FROM a.intermediate.int_lever__posting_applications o WHERE NOT EXISTS(SELECT 1 FROM (SELECT * FROM staging.stg_lever__application QUALIFY rank() OVER(PARTITION BY posting_id ORDER BY created_at DESC)=1) s WHERE o."posting_id" IS NOT DISTINCT FROM s."posting_id" AND o."posting_hiring_manager_user_id" IS NOT DISTINCT FROM s."posting_hiring_manager_user_id")
```
结果：`[[0]]`

`records/019_queries.json` / 诊断：
```sql
SELECT count(*) non_admissible FROM intermediate.int_lever__posting_applications o WHERE NOT EXISTS(SELECT 1 FROM (SELECT * FROM staging.stg_lever__application QUALIFY rank() OVER(PARTITION BY posting_id ORDER BY created_at DESC)=1) s WHERE o."posting_id" IS NOT DISTINCT FROM s."posting_id" AND o."posting_hiring_manager_user_id" IS NOT DISTINCT FROM s."posting_hiring_manager_user_id")
```
结果：`[[0]]`
