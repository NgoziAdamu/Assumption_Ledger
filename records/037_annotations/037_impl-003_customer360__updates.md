# impl-003_customer360__updates（037 正式批次）

主要原因：**其他**；把握：中。019旧主要原因原样保留：`O`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__updates.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，finish 51 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-003_customer360__updates.json`；037补充：`records/037_checks/`。

## 逐点标注

### update_types_order

- 类别：其他；角色：参与；把握：中。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

STRING_AGG DISTINCT的成员先后未规定；019共同规范两列后多重集完全一致，037分别规范每列以测量各自贡献。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: update_types
>         data_type: VARCHAR
>         description: Distinct update types concatenated with ', '; order not guaranteed; case preserved; nulls excluded.
>
> ```
>
> Important: You can only interact with the provided environment. Do not ask a human for help.
>
>
> When you believe the task is completed, you must call the "finish" tool to end the session. If you still need to develop or debug code, do not call "finish"; continue and complete everything first.

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__updates.sql`，第 7–7 行：

```sql
 string_agg(distinct source_system,', ') as updated_by_systems,string_agg(distinct update_type,', ') as update_types
```

单改/诊断：`records/037_checks/order_diagnostics.json#update_types_order`。双侧只改呈现的诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4291/6008 | 3121/3121 | 1170/2887 |
| L1 | 4291/6008 | 3121/3121 | 1170/2887 |
| L2 | 4291/6008 | 3121/3121 | 1170/2887 |
| L3 | 4291/6008 | 3121/3121 | 1170/2887 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，event `51.args.final_thought`：

> 契约对来源重复记录以及部分聚合排序并未规定唯一 tie-breaker；按 DuckDB 实际行为保留未指定并列顺序，不额外引入业务假设。

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### updated_by_systems_order

- 类别：其他；角色：主要；把握：中。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

STRING_AGG DISTINCT的成员先后未规定；019共同规范两列后多重集完全一致，037分别规范每列以测量各自贡献。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: updated_by_systems
>         data_type: VARCHAR
>         description: Distinct source systems concatenated with ', '; order not guaranteed; case preserved; nulls excluded.

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__updates.sql`，第 7–7 行：

```sql
 string_agg(distinct source_system,', ') as updated_by_systems,string_agg(distinct update_type,', ') as update_types
```

单改/诊断：`records/037_checks/order_diagnostics.json#updated_by_systems_order`。双侧只改呈现的诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 4291/6008 | 2887/2887 | 1404/3121 |
| L1 | 4291/6008 | 2887/2887 | 1404/3121 |
| L2 | 4291/6008 | 2887/2887 | 1404/3121 |
| L3 | 4291/6008 | 2887/2887 | 1404/3121 |

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
SELECT (SELECT count(*) FROM ((SELECT "customer360_id","first_seen","last_updated","total_updates",list_sort(string_split("update_types", ', ')) AS "update_types",list_sort(string_split("updated_by_systems", ', ')) AS "updated_by_systems" FROM marts.customer360__updates) EXCEPT ALL (SELECT "customer360_id","first_seen","last_updated","total_updates",list_sort(string_split("update_types", ', ')) AS "update_types",list_sort(string_split("updated_by_systems", ', ')) AS "updated_by_systems" FROM g.marts.customer360__updates))) agent_only,(SELECT count(*) FROM ((SELECT "customer360_id","first_seen","last_updated","total_updates",list_sort(string_split("update_types", ', ')) AS "update_types",list_sort(string_split("updated_by_systems", ', ')) AS "updated_by_systems" FROM g.marts.customer360__updates) EXCEPT ALL (SELECT "customer360_id","first_seen","last_updated","total_updates",list_sort(string_split("update_types", ', ')) AS "update_types",list_sort(string_split("updated_by_systems", ', ')) AS "updated_by_systems" FROM marts.customer360__updates))) gold_only
```
结果：`[[0, 0]]`
