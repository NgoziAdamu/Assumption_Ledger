# impl-003 / stg_customer360__state_territory_codes

## 结论

主要原因：**A**；把握：中；标记：无。

契约未规定整行去重；gold DISTINCT 删除完全重复行，agent 保留。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-003_stg_customer360__state_territory_codes.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：772/717。本次固定控制下 baseline 行/格规模：55/165。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`；原文行段 69–96。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/staging/stg_customer360__state_territory_codes.sql`，L1–15；SHA-256 `219a4d320246ac389820db3374b9c3c701a89025e6deb4093940d42f593f24a9`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/staging/stg_customer360__state_territory_codes.sql`，L1–33；SHA-256 `84b0679358daa5237dc01c1f35abd0ec89fa91c43dee0ef6e0c213696767db07`。

membership：agent SQL L14，替换原片段如下。
```sql
inner join staging.stg_customer360__country_codes cc
    on c.alpha2_country_code = cc.country_code_alpha_2
```
替换为：
```sql
where c.alpha2_country_code IN (SELECT country_code_alpha_2 FROM staging.stg_customer360__country_codes)
```

distinct_rows：agent SQL L12，替换原片段如下。
```sql
select c.state_territory, c.state_code, c.alpha2_country_code
```
替换为：
```sql
select distinct c.state_territory, c.state_code, c.alpha2_country_code
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-003_stg_customer360__state_territory_codes.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 55 | 165 | {} | L0–L3均不匹配 |
| baseline | L1 | 55 | 165 | {} | L0–L3均不匹配 |
| baseline | L2 | 55 | 165 | {} | L0–L3均不匹配 |
| baseline | L3 | 55 | 165 | {} | L0–L3均不匹配 |
| membership | L0 | 55 | 165 | {} | L0–L3均不匹配 |
| membership | L1 | 55 | 165 | {} | L0–L3均不匹配 |
| membership | L2 | 55 | 165 | {} | L0–L3均不匹配 |
| membership | L3 | 55 | 165 | {} | L0–L3均不匹配 |
| distinct_rows | L0 | 0 | 0 | {} | L0 |
| distinct_rows | L1 | 0 | 0 | {} | L0 |
| distinct_rows | L2 | 0 | 0 | {} | L0 |
| distinct_rows | L3 | 0 | 0 | {} | L0 |

- membership（I，单处 SQL 改动）：行减少 0，格减少 0。契约要求集合成员检查，inner join 在 reference 重复时扩行。

- distinct_rows（A，单处 SQL 改动）：行减少 55，格减少 165。契约未规定整行去重；gold DISTINCT 删除完全重复行，agent 保留。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，字段字符偏移 6136。

> stg_customer360__state_territory_codes
>       description: "Standardized state and territory code reference data with country relationships for address validation"
>       source_table: raw.state_territory_codes
>       columns:
>         - name: state_territory
>           data_type: VARCHAR(255)
>           constraints: [not_null]
>         - name: state_code
>           data_type: VARCHAR(5)
>           constraints: [not_null]
>           validation_rules:
>             - rule: "LENGTH(TRIM(state_code)) BETWEEN 2

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

契约没有整行 DISTINCT 要求。两种读法：把 gold 去重作为隐含粒度要求，或认为重复保留策略未定。本次选 A，不自行补 unique 规则。
