# impl-001 / stg_lever__offer

## 结论

主要原因：**C**；把握：高；标记：无。

契约对 offer.status 要求非法枚举置空，agent 使用 requisition 枚举删行。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**只有通用策略说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-001_stg_lever__offer.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：236/1000。本次固定控制下 baseline 行/格规模：764/3820。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`；原文行段 439–461。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__offer.sql`，L1–24；SHA-256 `20d86827b926385fe52cbf12eea94fa8db9d30bf54df74454f467b6433507a82`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/staging/stg_lever__offer.sql`，L1–21；SHA-256 `fb45a0027666b7f0d37d7c323508d0b1691396d7cf6d1f2b9e383bf6ce39b923`。

status_filter：agent SQL L13，替换原片段如下。
```sql
status IN ('open','closed','cancelled','draft','pending') AND
```
替换为：
```sql
TRUE AND
```

status：agent SQL L7，替换原片段如下。
```sql
try_cast(r."status" AS VARCHAR(50)) AS status
```
替换为：
```sql
CASE WHEN r.status IN ('draft','pending','sent','accepted','declined','rescinded') THEN r.status END AS status
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-001_stg_lever__offer.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 764 | 3820 | {} | L0–L3均不匹配 |
| baseline | L1 | 764 | 3820 | {} | L0–L3均不匹配 |
| baseline | L2 | 764 | 3820 | {} | L0–L3均不匹配 |
| baseline | L3 | 764 | 3820 | {} | L0–L3均不匹配 |
| status_filter | L0 | 254 | 254 | {"status": 254} | L0–L3均不匹配 |
| status_filter | L1 | 254 | 254 | {"status": 254} | L0–L3均不匹配 |
| status_filter | L2 | 254 | 254 | {"status": 254} | L0–L3均不匹配 |
| status_filter | L3 | 254 | 254 | {"status": 254} | L0–L3均不匹配 |
| status | L0 | 764 | 3820 | {} | L0–L3均不匹配 |
| status | L1 | 764 | 3820 | {} | L0–L3均不匹配 |
| status | L2 | 764 | 3820 | {} | L0–L3均不匹配 |
| status | L3 | 764 | 3820 | {} | L0–L3均不匹配 |

- status_filter（C，单处 SQL 改动）：行减少 510，格减少 3566。契约对 offer.status 要求非法枚举置空，agent 使用 requisition 枚举删行。

- status（C，单处 SQL 改动）：行减少 0，格减少 0。非法 status 应 nullify_field。

## agent 可见证据及不确定性

event 67 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，字段字符偏移 461。

> 转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
