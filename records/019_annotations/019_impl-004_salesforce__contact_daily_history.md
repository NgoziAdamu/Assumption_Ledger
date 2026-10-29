# impl-004 / salesforce__contact_daily_history

## 结论

主要原因：**O**；把握：高；标记：无。

契约允许的并列选择或聚合顺序不同；诊断确认其余内容/候选最大时间记录一致。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**针对本表的具体说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-004_salesforce__contact_daily_history.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：2369/2369。本次固定控制下 baseline 行/格规模：288/443。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-004/docs/data_contract.yaml`；原文行段 763–820。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/sql/marts/salesforce__contact_daily_history.sql`，L1–53；SHA-256 `3745310020907fc4b6a04b431be65482fa0b910f3bfce2894c4a8e189b56e3eb`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/sql/marts/salesforce__contact_daily_history.sql`，L1–51；SHA-256 `052878863f144bfbed469c64c5dcf30bc0ad11bf4c3d90e86aea2bea079a9da6`。

tie_order：agent SQL L29，替换原片段如下。
```sql
ORDER BY created_date DESC
```
替换为：
```sql
ORDER BY created_date DESC, title ASC
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-004_salesforce__contact_daily_history.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 1 条（上限5）；代价档：一条查询。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

核实：
```sql
SELECT count(*) tied_groups,sum(n-1) excess_rows FROM (SELECT contact_id,created_date,count(*) n FROM staging.stg_salesforce__contact_history GROUP BY ALL HAVING count(*)>1)
```
结果（仅统计/类型）：`[[0, null]]`

诊断：
```sql
SELECT count(*) non_admissible FROM a.marts.salesforce__contact_daily_history o WHERE NOT EXISTS(SELECT 1 FROM (SELECT * FROM staging.stg_salesforce__contact_history WHERE coalesce(is_deleted,false)=false QUALIFY rank() OVER(PARTITION BY contact_id,cast(created_date AS DATE) ORDER BY created_date DESC)=1) s WHERE o."contact_id" IS NOT DISTINCT FROM s."contact_id" AND o."account_id" IS NOT DISTINCT FROM s."account_id" AND o."contact_name" IS NOT DISTINCT FROM s."contact_name" AND o."email" IS NOT DISTINCT FROM s."email" AND o."first_name" IS NOT DISTINCT FROM s."first_name" AND o."last_activity_date" IS NOT DISTINCT FROM s."last_activity_date" AND o."last_name" IS NOT DISTINCT FROM s."last_name" AND o."lead_source" IS NOT DISTINCT FROM s."lead_source" AND o."mailing_city" IS NOT DISTINCT FROM s."mailing_city" AND o."mailing_country" IS NOT DISTINCT FROM s."mailing_country" AND o."mailing_state" IS NOT DISTINCT FROM s."mailing_state" AND o."mobile_phone" IS NOT DISTINCT FROM s."mobile_phone" AND o."owner_id" IS NOT DISTINCT FROM s."owner_id" AND o."phone" IS NOT DISTINCT FROM s."phone" AND o."title" IS NOT DISTINCT FROM s."title")
```
结果（仅统计/类型）：`[[0]]`

诊断：
```sql
SELECT count(*) non_admissible FROM marts.salesforce__contact_daily_history o WHERE NOT EXISTS(SELECT 1 FROM (SELECT * FROM staging.stg_salesforce__contact_history WHERE coalesce(is_deleted,false)=false QUALIFY rank() OVER(PARTITION BY contact_id,cast(created_date AS DATE) ORDER BY created_date DESC)=1) s WHERE o."contact_id" IS NOT DISTINCT FROM s."contact_id" AND o."account_id" IS NOT DISTINCT FROM s."account_id" AND o."contact_name" IS NOT DISTINCT FROM s."contact_name" AND o."email" IS NOT DISTINCT FROM s."email" AND o."first_name" IS NOT DISTINCT FROM s."first_name" AND o."last_activity_date" IS NOT DISTINCT FROM s."last_activity_date" AND o."last_name" IS NOT DISTINCT FROM s."last_name" AND o."lead_source" IS NOT DISTINCT FROM s."lead_source" AND o."mailing_city" IS NOT DISTINCT FROM s."mailing_city" AND o."mailing_country" IS NOT DISTINCT FROM s."mailing_country" AND o."mailing_state" IS NOT DISTINCT FROM s."mailing_state" AND o."mobile_phone" IS NOT DISTINCT FROM s."mobile_phone" AND o."owner_id" IS NOT DISTINCT FROM s."owner_id" AND o."phone" IS NOT DISTINCT FROM s."phone" AND o."title" IS NOT DISTINCT FROM s."title")
```
结果（仅统计/类型）：`[[0]]`

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 288 | 443 | {"last_activity_date": 288, "title": 155} | L0–L3均不匹配 |
| baseline | L1 | 288 | 443 | {"last_activity_date": 288, "title": 155} | L0–L3均不匹配 |
| baseline | L2 | 288 | 443 | {"last_activity_date": 288, "title": 155} | L0–L3均不匹配 |
| baseline | L3 | 288 | 443 | {"last_activity_date": 288, "title": 155} | L0–L3均不匹配 |
| tie_order | L0 | 153 | 306 | {"last_activity_date": 153, "title": 153} | L0–L3均不匹配 |
| tie_order | L1 | 153 | 306 | {"last_activity_date": 153, "title": 153} | L0–L3均不匹配 |
| tie_order | L2 | 153 | 306 | {"last_activity_date": 153, "title": 153} | L0–L3均不匹配 |
| tie_order | L3 | 153 | 306 | {"last_activity_date": 153, "title": 153} | L0–L3均不匹配 |

- tie_order（O，单处 SQL 改动）：行减少 135，格减少 137。契约明确同时间记录任取；改变并列次序诊断。

## agent 可见证据及不确定性

event 51 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/.events/sessions/024a80d8-934c-43-4e69514191069ca/events/51.json`，字段字符偏移 1534。

> 历史记录同一实体同日时间戳完全相同的并列记录，按契约定义仍可能任意选取。

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
