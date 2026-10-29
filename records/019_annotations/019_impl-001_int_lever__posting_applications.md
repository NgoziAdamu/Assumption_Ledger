# impl-001 / int_lever__posting_applications

## 结论

主要原因：**O**；把握：高；标记：无。

契约允许的并列选择或聚合顺序不同；诊断确认其余内容/候选最大时间记录一致。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-001_int_lever__posting_applications.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：300/300。本次固定控制下 baseline 行/格规模：299/299。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`；原文行段 1655–1688。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_applications.sql`，L1–1；SHA-256 `a4972bec8e45a3821fe507b3b9323d9f0494b018409b8896b52e782535874802`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/intermediate/int_lever__posting_applications.sql`，L1–52；SHA-256 `52d85c7ef901cd60d157cc2e59b3a2f9b2b91a5de8504eb9ff8b2f7fd3ab4838`。

tie_order：agent SQL L1，替换原片段如下。
```sql
ORDER BY created_at DESC
```
替换为：
```sql
ORDER BY created_at DESC, posting_hiring_manager_user_id
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-001_int_lever__posting_applications.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 1 条（上限5）；代价档：一条查询。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

核实：
```sql
SELECT count(*) tied_groups,sum(n-1) excess_rows FROM (SELECT posting_id,created_at,count(*) n FROM staging.stg_lever__application GROUP BY ALL HAVING count(*)>1)
```
结果（仅统计/类型）：`[[0, null]]`

诊断：
```sql
SELECT count(*) non_admissible FROM a.intermediate.int_lever__posting_applications o WHERE NOT EXISTS(SELECT 1 FROM (SELECT * FROM staging.stg_lever__application QUALIFY rank() OVER(PARTITION BY posting_id ORDER BY created_at DESC)=1) s WHERE o."posting_id" IS NOT DISTINCT FROM s."posting_id" AND o."posting_hiring_manager_user_id" IS NOT DISTINCT FROM s."posting_hiring_manager_user_id")
```
结果（仅统计/类型）：`[[0]]`

诊断：
```sql
SELECT count(*) non_admissible FROM intermediate.int_lever__posting_applications o WHERE NOT EXISTS(SELECT 1 FROM (SELECT * FROM staging.stg_lever__application QUALIFY rank() OVER(PARTITION BY posting_id ORDER BY created_at DESC)=1) s WHERE o."posting_id" IS NOT DISTINCT FROM s."posting_id" AND o."posting_hiring_manager_user_id" IS NOT DISTINCT FROM s."posting_hiring_manager_user_id")
```
结果（仅统计/类型）：`[[0]]`

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 299 | 299 | {"posting_hiring_manager_user_id": 299} | L0–L3均不匹配 |
| baseline | L1 | 299 | 299 | {"posting_hiring_manager_user_id": 299} | L0–L3均不匹配 |
| baseline | L2 | 299 | 299 | {"posting_hiring_manager_user_id": 299} | L0–L3均不匹配 |
| baseline | L3 | 299 | 299 | {"posting_hiring_manager_user_id": 299} | L0–L3均不匹配 |
| tie_order | L0 | 280 | 280 | {"posting_hiring_manager_user_id": 280} | L0–L3均不匹配 |
| tie_order | L1 | 280 | 280 | {"posting_hiring_manager_user_id": 280} | L0–L3均不匹配 |
| tie_order | L2 | 280 | 280 | {"posting_hiring_manager_user_id": 280} | L0–L3均不匹配 |
| tie_order | L3 | 280 | 280 | {"posting_hiring_manager_user_id": 280} | L0–L3均不匹配 |

- tie_order（O，单处 SQL 改动）：行减少 19，格减少 19。契约允许引擎默认并列次序。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/1.json`，字段字符偏移 98889。

> int_lever__posting_applications
>       description: Aggregates application metrics per posting and selects the latest hiring manager user ID by created_at.
>       grain: One row per non-null posting_id with applications in staging.stg_lever__application
>       source_models:
>       - staging.stg_lever__application
>       business_logic: '- Read all application rows from staging.stg_lever__application. - Aggregate per posting_id: - first_app_sent_at: the earliest non-null created_at; if all created_at

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
