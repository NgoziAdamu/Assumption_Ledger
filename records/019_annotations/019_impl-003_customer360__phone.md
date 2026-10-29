# impl-003 / customer360__phone

## 结论

主要原因：**O**；把握：中；标记：无。

契约允许的并列选择或聚合顺序不同；诊断确认其余内容/候选最大时间记录一致。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**只有通用策略说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-003_customer360__phone.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：25986/25986。本次固定控制下 baseline 行/格规模：3485/3485。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`；原文行段 2069–2090。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__phone.sql`，L1–9；SHA-256 `fc90fa81e430f73c72ec086b0365e56a02a3e6390d7c2e0a9aed32f6ff0df29f`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__phone.sql`，L1–115；SHA-256 `46d53c248b4e064fae02121ae13d288ff429f450470778d64aee6c6db8a64147`。

phone_tie：agent SQL L9，替换原片段如下。
```sql
order by phone
```
替换为：
```sql
order by phone,extension
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-003_customer360__phone.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

诊断：
```sql
SELECT (SELECT count(*) FROM ((SELECT "customer360_id","extension","phone" FROM marts.customer360__phone) EXCEPT ALL (SELECT "customer360_id","extension","phone" FROM g.marts.customer360__phone))) agent_only,(SELECT count(*) FROM ((SELECT "customer360_id","extension","phone" FROM g.marts.customer360__phone) EXCEPT ALL (SELECT "customer360_id","extension","phone" FROM marts.customer360__phone))) gold_only
```
结果（仅统计/类型）：`[[0, 0]]`

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 3485 | 3485 | {"index": 3485} | L0–L3均不匹配 |
| baseline | L1 | 3485 | 3485 | {"index": 3485} | L0–L3均不匹配 |
| baseline | L2 | 3485 | 3485 | {"index": 3485} | L0–L3均不匹配 |
| baseline | L3 | 3485 | 3485 | {"index": 3485} | L0–L3均不匹配 |
| phone_tie | L0 | 3405 | 3405 | {"index": 3405} | L0–L3均不匹配 |
| phone_tie | L1 | 3405 | 3405 | {"index": 3405} | L0–L3均不匹配 |
| phone_tie | L2 | 3405 | 3405 | {"index": 3405} | L0–L3均不匹配 |
| phone_tie | L3 | 3405 | 3405 | {"index": 3405} | L0–L3均不匹配 |

- phone_tie（O，单处 SQL 改动）：行减少 80，格减少 80。相同 phone 不同 extension 的 row_number 并列顺序。

## agent 可见证据及不确定性

event 51 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，字段字符偏移 1205。

> 契约对来源重复记录以及部分聚合排序并未规定唯一 tie-breaker；按 DuckDB 实际行为保留未指定并列顺序，不额外引入业务假设。

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

契约明确相同 phone 的 extension 并列次序未规定；只改变排序不能保证复现 gold。O 依据去除 index 后两侧 EXCEPT ALL 为0，而非任一碰巧匹配的重跑。
