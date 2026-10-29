# impl-001 / stg_lever__requisition

## 结论

主要原因：**C**；把握：高；标记：无。

遗漏契约枚举 nullify_field。

参与因素：compensation_band_interval=C。

不确定性四档：**只有通用策略说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-001_stg_lever__requisition.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：146/146。本次固定控制下 baseline 行/格规模：4/5。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`；原文行段 84–175。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__requisition.sql`，L1–46；SHA-256 `5d4cb66eccb8d207665b82dccb71763a880bbc30a5f940e190b861bc4a92b80d`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/staging/stg_lever__requisition.sql`，L1–100；SHA-256 `4165d29e0966b33994bebf29f9818134299b0dfac6686e0f259d2d327b9ae401`。

compensation_band_currency：agent SQL L8，替换原片段如下。
```sql
try_cast(r."compensation_band_currency" AS VARCHAR(3)) AS compensation_band_currency
```
替换为：
```sql
CASE WHEN r.compensation_band_currency IN ('USD','EUR','GBP','CNY','CAD','AUD') THEN r.compensation_band_currency END AS compensation_band_currency
```

compensation_band_interval：agent SQL L9，替换原片段如下。
```sql
try_cast(r."compensation_band_interval" AS VARCHAR(10)) AS compensation_band_interval
```
替换为：
```sql
CASE WHEN r.compensation_band_interval IN ('hourly','monthly','yearly') THEN r.compensation_band_interval END AS compensation_band_interval
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-001_stg_lever__requisition.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 4 | 5 | {"compensation_band_currency": 3, "compensation_band_interval": 2} | L0–L3均不匹配 |
| baseline | L1 | 4 | 5 | {"compensation_band_currency": 3, "compensation_band_interval": 2} | L0–L3均不匹配 |
| baseline | L2 | 4 | 5 | {"compensation_band_currency": 3, "compensation_band_interval": 2} | L0–L3均不匹配 |
| baseline | L3 | 4 | 5 | {"compensation_band_currency": 3, "compensation_band_interval": 2} | L0–L3均不匹配 |
| compensation_band_currency | L0 | 2 | 2 | {"compensation_band_interval": 2} | L0–L3均不匹配 |
| compensation_band_currency | L1 | 2 | 2 | {"compensation_band_interval": 2} | L0–L3均不匹配 |
| compensation_band_currency | L2 | 2 | 2 | {"compensation_band_interval": 2} | L0–L3均不匹配 |
| compensation_band_currency | L3 | 2 | 2 | {"compensation_band_interval": 2} | L0–L3均不匹配 |
| compensation_band_interval | L0 | 3 | 3 | {"compensation_band_currency": 3} | L0–L3均不匹配 |
| compensation_band_interval | L1 | 3 | 3 | {"compensation_band_currency": 3} | L0–L3均不匹配 |
| compensation_band_interval | L2 | 3 | 3 | {"compensation_band_currency": 3} | L0–L3均不匹配 |
| compensation_band_interval | L3 | 3 | 3 | {"compensation_band_currency": 3} | L0–L3均不匹配 |

- compensation_band_currency（C，单处 SQL 改动）：行减少 2，格减少 3。遗漏契约枚举 nullify_field。

- compensation_band_interval（C，单处 SQL 改动）：行减少 1，格减少 2。遗漏契约枚举 nullify_field。

## agent 可见证据及不确定性

event 67 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/67.json`，字段字符偏移 461。

> 转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
