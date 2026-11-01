# impl-003_customer360__phone（037 正式批次）

主要原因：**其他**；把握：中。019旧主要原因原样保留：`O`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__phone.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，finish 51 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-003_customer360__phone.json`；037补充：`records/037_checks/`。

## 逐点标注

### phone_tie

- 类别：其他；角色：主要；把握：中。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

相同phone不同extension的row_number并列顺序未被规定；019去掉序号后双方多重集完全一致，且SQL按规定phone排序。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: phone
>         data_type: VARCHAR
>         description: Phone string from sources; NULL phones are excluded; value is preserved; used for deduplication and ascending sort for indexing.

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__phone.sql`，第 9–9 行：

```sql
order by phone
```

单改/诊断：`records/019_reruns_impl-003_customer360__phone.json#phone_tie`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 3485/3485 | 3405/3405 | 80/80 |
| L1 | 3485/3485 | 3405/3405 | 80/80 |
| L2 | 3485/3485 | 3405/3405 | 80/80 |
| L3 | 3485/3485 | 3405/3405 | 80/80 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，event `51.args.final_thought`：

> 契约对来源重复记录以及部分聚合排序并未规定唯一 tie-breaker；按 DuckDB 实际行为保留未指定并列顺序，不额外引入业务假设。

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：

`records/019_queries.json` / 诊断：
```sql
SELECT (SELECT count(*) FROM ((SELECT "customer360_id","extension","phone" FROM marts.customer360__phone) EXCEPT ALL (SELECT "customer360_id","extension","phone" FROM g.marts.customer360__phone))) agent_only,(SELECT count(*) FROM ((SELECT "customer360_id","extension","phone" FROM g.marts.customer360__phone) EXCEPT ALL (SELECT "customer360_id","extension","phone" FROM marts.customer360__phone))) gold_only
```
结果：`[[0, 0]]`
