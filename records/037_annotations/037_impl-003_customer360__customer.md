# impl-003_customer360__customer（037 正式批次）

主要原因：**Unstated Choice**；把握：中。019旧主要原因原样保留：`U`，不作为新类别依据。

## 范围与材料

- 层：marts；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__customer.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，finish 51 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-003_customer360__customer.json`；037补充：`records/037_checks/`。

## 逐点标注

### metrics_key_multiplicity

- 类别：Unstated Choice；角色：主要；把握：中。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约一方面声明每customer360_id一行，另一方面明确要求metrics按id与dimensions结合；上游重复id使两者发生冲突。agent直接内联保留dimensions重数，gold重新按id连接扩行。按第11节选择Unstated Choice（两个要求不能同时照字面满足），不沿用019的Data。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: customer360_id
>         data_type: VARCHAR
>         description: Primary identifier; one output row per id; also the join key between mapping and summary.

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__customer.sql`，第 23–23 行：

```sql
select * from non_headers union all select * from headers
```

单改/诊断：`records/019_reruns_impl-003_customer360__customer.json#metrics_key_multiplicity`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 72408/1303344 | 0/0 | 72408/1303344 |
| L1 | 72408/1303344 | 0/0 | 72408/1303344 |
| L2 | 72408/1303344 | 0/0 | 72408/1303344 |
| L3 | 72408/1303344 | 0/0 | 72408/1303344 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，event `51.args.final_thought`：

> 中间层按契约保留源业务数据的重复记录，不对 source IDs 做全局去重。下游按这些 ID 关联时，若上游相同 ID 对应多行，可能发生行数扩增；此项属于合同指定的重复保留行为。

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：

`records/019_queries.json` / 核实：
```sql
SELECT count(*) duplicate_keys,sum(n-1) excess_rows FROM (SELECT m.customer360_id,count(*) n FROM marts.customer360__mapping m JOIN marts.customer360__summary s USING(customer360_id) GROUP BY m.customer360_id HAVING count(*)>1)
```
结果：`[[78, 314]]`

规则问题：按id结合的明确步骤与每id一行的grain互相冲突。可读成Intent（强调步骤）或Choice（不能同时满足）。本批采用Choice，置信中；026仅提供冲突事实，019旧标签仍保留U，不改规则。
