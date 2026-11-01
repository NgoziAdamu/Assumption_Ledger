# impl-004_salesforce__account_daily_history（037 正式批次）

主要原因：**其他**；把握：高。019旧主要原因原样保留：`O`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/sql/marts/salesforce__account_daily_history.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/.events/sessions/024a80d8-934c-43-4e69514191069ca/events/51.json`，finish 51 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-004_salesforce__account_daily_history.json`；037补充：`records/037_checks/`。

## 逐点标注

### tie_order

- 类别：其他；角色：主要；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约允许同实体同日最新时间并列时任取；019双侧非admissible记录数均0。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: '- Read all records from staging.stg_salesforce__account_history. - Exclude records marked as deleted. - For each account and calendar day (based on the date part of created_date), sort records by created_date in descending order and keep the first record; if multiple records share the exact same created_date within that day, the choice among them is not deterministic. - Define snapshot_date as the calendar date of created_date from the kept record. - All other fields are taken directly from the kept record without transformation or aggregation; data types are preserved and NULLs are retained. - The final result is ordered by account_id and snapshot_date for readability only.'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/sql/marts/salesforce__account_daily_history.sql`，第 29–29 行：

```sql
ORDER BY created_date DESC
```

单改/诊断：`records/019_reruns_impl-004_salesforce__account_daily_history.json#tie_order`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 410/1316 | 297/1025 | 113/291 |
| L1 | 410/1316 | 297/1025 | 113/291 |
| L2 | 410/1316 | 297/1025 | 113/291 |
| L3 | 410/1316 | 297/1025 | 113/291 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/.events/sessions/024a80d8-934c-43-4e69514191069ca/events/51.json`，event `51.args.final_thought`：

> 日快照同一时间戳存在并列时按契约接受非确定性选择。

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：

`records/019_queries.json` / 核实：
```sql
SELECT count(*) tied_groups,sum(n-1) excess_rows FROM (SELECT account_id,created_date,count(*) n FROM staging.stg_salesforce__account_history GROUP BY ALL HAVING count(*)>1)
```
结果：`[[0, null]]`

`records/019_queries.json` / 诊断：
```sql
SELECT count(*) non_admissible FROM a.marts.salesforce__account_daily_history o WHERE NOT EXISTS(SELECT 1 FROM (SELECT * FROM staging.stg_salesforce__account_history WHERE coalesce(is_deleted,false)=false QUALIFY rank() OVER(PARTITION BY account_id,cast(created_date AS DATE) ORDER BY created_date DESC)=1) s WHERE o."account_id" IS NOT DISTINCT FROM s."account_id" AND o."account_name" IS NOT DISTINCT FROM s."account_name" AND o."account_source" IS NOT DISTINCT FROM s."account_source" AND o."annual_revenue" IS NOT DISTINCT FROM s."annual_revenue" AND o."billing_city" IS NOT DISTINCT FROM s."billing_city" AND o."billing_country" IS NOT DISTINCT FROM s."billing_country" AND o."billing_state" IS NOT DISTINCT FROM s."billing_state" AND o."industry" IS NOT DISTINCT FROM s."industry" AND o."last_activity_date" IS NOT DISTINCT FROM s."last_activity_date" AND o."number_of_employees" IS NOT DISTINCT FROM s."number_of_employees" AND o."owner_id" IS NOT DISTINCT FROM s."owner_id" AND o."ownership" IS NOT DISTINCT FROM s."ownership" AND o."parent_id" IS NOT DISTINCT FROM s."parent_id" AND o."rating" IS NOT DISTINCT FROM s."rating" AND o."type" IS NOT DISTINCT FROM s."type" AND o."website" IS NOT DISTINCT FROM s."website")
```
结果：`[[0]]`

`records/019_queries.json` / 诊断：
```sql
SELECT count(*) non_admissible FROM marts.salesforce__account_daily_history o WHERE NOT EXISTS(SELECT 1 FROM (SELECT * FROM staging.stg_salesforce__account_history WHERE coalesce(is_deleted,false)=false QUALIFY rank() OVER(PARTITION BY account_id,cast(created_date AS DATE) ORDER BY created_date DESC)=1) s WHERE o."account_id" IS NOT DISTINCT FROM s."account_id" AND o."account_name" IS NOT DISTINCT FROM s."account_name" AND o."account_source" IS NOT DISTINCT FROM s."account_source" AND o."annual_revenue" IS NOT DISTINCT FROM s."annual_revenue" AND o."billing_city" IS NOT DISTINCT FROM s."billing_city" AND o."billing_country" IS NOT DISTINCT FROM s."billing_country" AND o."billing_state" IS NOT DISTINCT FROM s."billing_state" AND o."industry" IS NOT DISTINCT FROM s."industry" AND o."last_activity_date" IS NOT DISTINCT FROM s."last_activity_date" AND o."number_of_employees" IS NOT DISTINCT FROM s."number_of_employees" AND o."owner_id" IS NOT DISTINCT FROM s."owner_id" AND o."ownership" IS NOT DISTINCT FROM s."ownership" AND o."parent_id" IS NOT DISTINCT FROM s."parent_id" AND o."rating" IS NOT DISTINCT FROM s."rating" AND o."type" IS NOT DISTINCT FROM s."type" AND o."website" IS NOT DISTINCT FROM s."website")
```
结果：`[[0]]`
