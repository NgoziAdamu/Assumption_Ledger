# impl-002 / stg_pendo__visitor_history

## 结论

主要原因：**I**；把握：高；标记：无。

同一个 SQL 对 first_visit/last_updated_at 正确截取，对 last_visit 遗漏。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**只有通用策略说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-002_stg_pendo__visitor_history.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：8000/8000。本次固定控制下 baseline 行/格规模：8000/8000。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml`；原文行段 201–231。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__visitor_history.sql`，L1–14；SHA-256 `bee54197735a2dd30e8bd22ce55f394df4a40c791df230ac93c48fed8e6ef489`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/staging/stg_pendo__visitor_history.sql`，L1–38；SHA-256 `1bcee607306f6504543a8b00d0094387ef7e2595d096ef0ca8fdfbe065a508cf`。

last_visit_parse：agent SQL L12，替换原片段如下。
```sql
TRY_CAST(last_visit AS TIMESTAMP)
```
替换为：
```sql
TRY_CAST(SUBSTRING(last_visit,1,23) AS TIMESTAMP)
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-002_stg_pendo__visitor_history.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 1 条（上限5）；代价档：一条查询。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

核实：
```sql
SELECT count(*) n,count(*) FILTER(WHERE try_cast(last_visit AS TIMESTAMP) IS NULL AND try_cast(substring(last_visit,1,23) AS TIMESTAMP) IS NOT NULL) failed_direct FROM raw.visitor_history
```
结果（仅统计/类型）：`[[8000, 8000]]`

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 8000 | 8000 | {"last_visit": 8000} | L0–L3均不匹配 |
| baseline | L1 | 8000 | 8000 | {"last_visit": 8000} | L0–L3均不匹配 |
| baseline | L2 | 8000 | 8000 | {"last_visit": 8000} | L0–L3均不匹配 |
| baseline | L3 | 8000 | 8000 | {"last_visit": 8000} | L0–L3均不匹配 |
| last_visit_parse | L0 | 0 | 0 | {} | L0 |
| last_visit_parse | L1 | 0 | 0 | {} | L0 |
| last_visit_parse | L2 | 0 | 0 | {} | L0 |
| last_visit_parse | L3 | 0 | 0 | {} | L0 |

- last_visit_parse（I，单处 SQL 改动）：行减少 8000，格减少 8000。同一个 SQL 对 first_visit/last_updated_at 正确截取，对 last_visit 遗漏。

## agent 可见证据及不确定性

event 59 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，字段字符偏移 756。

> Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
