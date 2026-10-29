# impl-003 / customer360__customer

## 结论

主要原因：**U**；把握：中；标记：证据曾出现但被忽略。

P：dimensions 的 customer360_id 唯一，直接内联 metrics 与按键结合等价；私有上游可核实重复。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**只有通用策略说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-003_customer360__customer.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：30008/102416。本次固定控制下 baseline 行/格规模：72408/1303344。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`；原文行段 1395–1480。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__customer.sql`，L1–23；SHA-256 `95077afe219ee06ce14a8a18e445b78c1851aced7153285c9fa59ec1212b4936`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__customer.sql`，L1–129；SHA-256 `b118a5d9a6908bcc84958f4f3a1b605310a61d7a3de47204126349a5626e24cc`。

metrics_key_multiplicity：agent SQL L23，替换原片段如下。
```sql
select * from non_headers union all select * from headers
```
替换为：
```sql
select n.* from non_headers n JOIN dimensions d USING(customer360_id) union all select * from headers
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-003_customer360__customer.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 1 条（上限5）；代价档：一条查询。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

核实：
```sql
SELECT count(*) duplicate_keys,sum(n-1) excess_rows FROM (SELECT m.customer360_id,count(*) n FROM marts.customer360__mapping m JOIN marts.customer360__summary s USING(customer360_id) GROUP BY m.customer360_id HAVING count(*)>1)
```
结果（仅统计/类型）：`[[78, 314]]`

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 72408 | 1303344 | {} | L0–L3均不匹配 |
| baseline | L1 | 72408 | 1303344 | {} | L0–L3均不匹配 |
| baseline | L2 | 72408 | 1303344 | {} | L0–L3均不匹配 |
| baseline | L3 | 72408 | 1303344 | {} | L0–L3均不匹配 |
| metrics_key_multiplicity | L0 | 0 | 0 | {} | L0 |
| metrics_key_multiplicity | L1 | 0 | 0 | {} | L0 |
| metrics_key_multiplicity | L2 | 0 | 0 | {} | L0 |
| metrics_key_multiplicity | L3 | 0 | 0 | {} | L0 |

- metrics_key_multiplicity（U，单处 SQL 改动）：行减少 72408，格减少 1303344。P：dimensions 的 customer360_id 唯一，直接内联 metrics 与按键结合等价；私有上游可核实重复。

U 条件：P 及反例见结论和核实查询；实际可见材料见下一节；仅指定取列/解析/同键结合的改动达到第4条件。对重复/缺失的已有提示不等于验证了代码依赖的等价性，按手册保留“证据曾出现但被忽略”（适用时）。

## agent 可见证据及不确定性

event 51 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，字段字符偏移 1027。

> 中间层按契约保留源业务数据的重复记录，不对 source IDs 做全局去重。下游按这些 ID 关联时，若上游相同 ID 对应多行，可能发生行数扩增；此项属于合同指定的重复保留行为。

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

两种读法：契约“combine by customer360_id”直接要求自连接（C），或 agent 内联 sample metrics 依赖 dimensions 唯一性（U）。本次选 U：P 可写为 dimensions 每 customer_id 唯一，agent 可见数据反例78组；同键结合单修后 L0 完全一致。契约的一行粒度不能抹去现有上游重复证据。
