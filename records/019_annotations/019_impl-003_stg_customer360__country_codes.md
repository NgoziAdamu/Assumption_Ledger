# impl-003 / stg_customer360__country_codes

## 结论

主要原因：**O**；把握：高；标记：无。

契约 country_code_alpha_2 unique；gold 未去重，移除去重作诊断。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**针对本表的具体说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-003_stg_customer360__country_codes.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：30/31。本次固定控制下 baseline 行/格规模：1/5。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`；原文行段 31–68。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/staging/stg_customer360__country_codes.sql`，L1–20；SHA-256 `198d9d7eda82b5f65880a9bf79b2b31d4d2d65fbd4107b79109593caea8cb8a3`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/staging/stg_customer360__country_codes.sql`，L1–30；SHA-256 `eccc7353983e498e2d39c1ed90a9b7b8d6c7cf8f84a49a804971e2ee7f48a100`。

dedup：agent SQL L20，替换原片段如下。
```sql
where _row_num = 1
```
替换为：
```sql
where TRUE
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-003_stg_customer360__country_codes.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

诊断：
```sql
SELECT count(*) duplicate_keys,sum(n-1) excess_rows FROM (SELECT country_code_alpha_2,count(*) n FROM staging.stg_customer360__country_codes GROUP BY 1 HAVING count(*)>1)
```
结果（仅统计/类型）：`[[1, 1]]`

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 1 | 5 | {} | L0–L3均不匹配 |
| baseline | L1 | 1 | 5 | {} | L0–L3均不匹配 |
| baseline | L2 | 1 | 5 | {} | L0–L3均不匹配 |
| baseline | L3 | 1 | 5 | {} | L0–L3均不匹配 |
| dedup | L0 | 0 | 0 | {} | L0 |
| dedup | L1 | 0 | 0 | {} | L0 |
| dedup | L2 | 0 | 0 | {} | L0 |
| dedup | L3 | 0 | 0 | {} | L0 |

- dedup（O，单处 SQL 改动）：行减少 1，格减少 5。契约 country_code_alpha_2 unique；gold 未去重，移除去重作诊断。

## agent 可见证据及不确定性

event 51 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，字段字符偏移 965。

> country alpha-2 冲突记录通过稳定字段排序保留一条，避免唯一键重复。

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
