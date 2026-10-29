# impl-001 / lever__opportunity_enhanced

## 结论

主要原因：**C**；把握：高；标记：无。

契约规定每 candidate 的最新 offer，代码按 opportunity 分区。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-001_lever__opportunity_enhanced.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：5576/5861。本次固定控制下 baseline 行/格规模：285/9975。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`；原文行段 2601–2748。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__opportunity_enhanced.sql`，L1–1；SHA-256 `a50697e637ba13344373c2f838014f7191872ef4b947bd31dae594b925633145`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/marts/lever__opportunity_enhanced.sql`，L1–76；SHA-256 `8b286c32f9a79d0a0ead5a9b3380deb432aa269ad7924ef52442346b2cb15e95`。

candidate_partition：agent SQL L1，替换原片段如下。
```sql
PARTITION BY opportunity_id ORDER BY created_at DESC
```
替换为：
```sql
PARTITION BY candidate_id ORDER BY created_at DESC
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-001_lever__opportunity_enhanced.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 285 | 9975 | {} | L0–L3均不匹配 |
| baseline | L1 | 285 | 9975 | {} | L0–L3均不匹配 |
| baseline | L2 | 285 | 9975 | {} | L0–L3均不匹配 |
| baseline | L3 | 285 | 9975 | {} | L0–L3均不匹配 |
| candidate_partition | L0 | 0 | 0 | {} | L0 |
| candidate_partition | L1 | 0 | 0 | {} | L0 |
| candidate_partition | L2 | 0 | 0 | {} | L0 |
| candidate_partition | L3 | 0 | 0 | {} | L0 |

- candidate_partition（C，单处 SQL 改动）：行减少 285，格减少 9975。契约规定每 candidate 的最新 offer，代码按 opportunity 分区。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，字段字符偏移 182978。

> lever__opportunity_enhanced
>       description: Enhanced opportunity records joined with stage name, tags, archive reason, most recent offer, and posting context.
>       grain: One row per opportunity_id with a valid stage_id
>       source_models:
>       - intermediate.int_lever__opportunity_contact_info
>       - staging.stg_lever__stage
>       - staging.stg_lever__archive_reason
>       - intermediate.int_lever__opportunity_tags
>       - staging.stg_lever__offer
>       - staging.stg_lever__posting
>       

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
