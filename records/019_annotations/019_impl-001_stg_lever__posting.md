# impl-001 / stg_lever__posting

## 结论

主要原因：**C**；把握：高；标记：无。

遗漏契约枚举 nullify_field。

参与因素：categories_level=C。

不确定性四档：**只有通用策略说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-001_stg_lever__posting.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：148/148。本次固定控制下 baseline 行/格规模：59/65。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`；原文行段 235–303。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__posting.sql`，L1–39；SHA-256 `6ad1fd65810cdf7db3eb28e382e2c744ce7abc55774e412bd677f1128eaa87ef`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/staging/stg_lever__posting.sql`，L1–45；SHA-256 `14402cb2ddbe24bdfe8c3c2b55044a79b6e84b645b1f31a62c46f669b204ee18`。

categories_commitment：agent SQL L7，替换原片段如下。
```sql
try_cast(r."categories_commitment" AS VARCHAR(50)) AS categories_commitment
```
替换为：
```sql
CASE WHEN r.categories_commitment IN ('full-time','part-time','contract','internship') THEN r.categories_commitment END AS categories_commitment
```

categories_level：agent SQL L9，替换原片段如下。
```sql
try_cast(r."categories_level" AS VARCHAR(50)) AS categories_level
```
替换为：
```sql
CASE WHEN r.categories_level IN ('Entry','Mid','Senior','Lead','Principal','Executive') THEN r.categories_level END AS categories_level
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-001_stg_lever__posting.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 59 | 65 | {"categories_commitment": 40, "categories_level": 25} | L0–L3均不匹配 |
| baseline | L1 | 59 | 65 | {"categories_commitment": 40, "categories_level": 25} | L0–L3均不匹配 |
| baseline | L2 | 59 | 65 | {"categories_commitment": 40, "categories_level": 25} | L0–L3均不匹配 |
| baseline | L3 | 59 | 65 | {"categories_commitment": 40, "categories_level": 25} | L0–L3均不匹配 |
| categories_commitment | L0 | 25 | 25 | {"categories_level": 25} | L0–L3均不匹配 |
| categories_commitment | L1 | 25 | 25 | {"categories_level": 25} | L0–L3均不匹配 |
| categories_commitment | L2 | 25 | 25 | {"categories_level": 25} | L0–L3均不匹配 |
| categories_commitment | L3 | 25 | 25 | {"categories_level": 25} | L0–L3均不匹配 |
| categories_level | L0 | 40 | 40 | {"categories_commitment": 40} | L0–L3均不匹配 |
| categories_level | L1 | 40 | 40 | {"categories_commitment": 40} | L0–L3均不匹配 |
| categories_level | L2 | 40 | 40 | {"categories_commitment": 40} | L0–L3均不匹配 |
| categories_level | L3 | 40 | 40 | {"categories_commitment": 40} | L0–L3均不匹配 |

- categories_commitment（C，单处 SQL 改动）：行减少 34，格减少 40。遗漏契约枚举 nullify_field。

- categories_level（C，单处 SQL 改动）：行减少 19，格减少 25。遗漏契约枚举 nullify_field。

## agent 可见证据及不确定性

event 67 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，字段字符偏移 461。

> 转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
