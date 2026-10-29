# impl-021 / int_klaviyo__person_metrics（校准，盲标封存）

## 结论

主要原因：**C**；把握：高；标记：无。

契约明确同日多事件不得改变 missing_day_count；JOIN 后 count(*) 减 count(distinct date) 将同日多条事件误算成 missing day。只去掉 distinct，行/格规模2→0，L0完全匹配。无足够正确意图证据归 I。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/013_packages/013_impl-021_intermediate_int_klaviyo__person_metrics.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：2/2。本次固定控制下 baseline 行/格规模：2/2。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml`；原文行段 820–920。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/intermediate/int_klaviyo__person_metrics.sql`，L1–20；SHA-256 `5ecf0dcb9d3310d0cd3e40454bc70b560efc4a78b8877ee672f15ed1853d7e9c`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/sql/intermediate/int_klaviyo__person_metrics.sql`，L1–86；SHA-256 `3ec710d804c87db3c5e49954e47c51de7618298ac4b800786939b355ee7e8362`。

count_events：agent SQL L7，盲标单处改动。
```sql
count(*)-count(distinct e.occurred_on)
```
替换为：
```sql
count(*)-count(e.occurred_on)
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-021_int_klaviyo__person_metrics.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 1 条（上限5）；代价档：一条查询。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

核实：
```sql
SELECT count(*) AS repeated_groups, sum(n-1) extra_events FROM (SELECT person_id,source_relation,cast(occurred_at AS DATE),count(*) n FROM staging.stg_klaviyo__event GROUP BY ALL HAVING count(*)>1)
```
结果（仅统计/类型）：`[[707, 1027]]`

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 2 | 2 | {"missing_day_count": 2} | L0–L3均不匹配 |
| baseline | L1 | 2 | 2 | {"missing_day_count": 2} | L0–L3均不匹配 |
| baseline | L2 | 2 | 2 | {"missing_day_count": 2} | L0–L3均不匹配 |
| baseline | L3 | 2 | 2 | {"missing_day_count": 2} | L0–L3均不匹配 |
| count_events | L0 | 0 | 0 | {} | L0 |
| count_events | L1 | 0 | 0 | {} | L0 |
| count_events | L2 | 0 | 0 | {} | L0 |
| count_events | L3 | 0 | 0 | {} | L0 |

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/1.json`，字段字符偏移 54333。

> int_klaviyo__person_metrics
>       description: Per-person metrics from Klaviyo events including activity windows, continuity diagnostics, event counts, revenue sums, and conversion rates
>       grain: One row per person_id per source_relation
>       source_models:
>       - staging.stg_klaviyo__event
>       business_logic: '- Inputs: person_id, source_relation, occurred_at (timestamp), type (event name), numeric_value. - Event normalization: - occurred_on is the calendar date of occurred_at (time rem

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

亦可把算法视为假定每天只有一条事件而归 U；采用 C，因为契约直接规定同日多事件不改变计数。

盲标封存：`records/019_calibration_blind_sealed.json`，时间 2026-10-29T13:45:23.213382+00:00。封存前未读取014–018标注；封存后比较只报告分歧，不回写本表盲标结论。
