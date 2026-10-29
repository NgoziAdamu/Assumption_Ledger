# impl-005 / stg_google_ads__account_history

## 结论

主要原因：**A**；把握：中；标记：无。

契约只指定 TIMESTAMP 及校验，没有规定源时区文本解析器与失败策略；agent STRPTIME 与 gold TRY_CAST 产生有效时间/NULL 两种结果。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**只有通用策略说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-005_stg_google_ads__account_history.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：100/0。本次固定控制下 baseline 行/格规模：100/700。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-005/docs/data_contract.yaml`；原文行段 43–71。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__account_history.sql`，L1–11；SHA-256 `f45fc54a9edccdb5c9423af562221a467e30774686d9dd84a706ef9e3e30f4d6`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/sql/staging/stg_google_ads__account_history.sql`，L1–42；SHA-256 `0f17d385efbaf65a56a00c1dab0c8a9c16bea6e50258621eb181515819b215b3`。

timestamp_cast：agent SQL L6，替换原片段如下。
```sql
try_strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP
```
替换为：
```sql
try_cast(updated_at AS TIMESTAMP)
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-005_stg_google_ads__account_history.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 100 | 700 | {} | L0–L3均不匹配 |
| baseline | L1 | 100 | 700 | {} | L0–L3均不匹配 |
| baseline | L2 | 100 | 700 | {} | L0–L3均不匹配 |
| baseline | L3 | 100 | 700 | {} | L0–L3均不匹配 |
| timestamp_cast | L0 | 0 | 0 | {} | L0 |
| timestamp_cast | L1 | 0 | 0 | {} | L0 |
| timestamp_cast | L2 | 0 | 0 | {} | L0 |
| timestamp_cast | L3 | 0 | 0 | {} | L0 |

- timestamp_cast（A，单处 SQL 改动）：行减少 100，格减少 700。契约只指定 TIMESTAMP 及校验，没有规定源时区文本解析器与失败策略；agent STRPTIME 与 gold TRY_CAST 产生有效时间/NULL 两种结果。

## agent 可见证据及不确定性

event 47 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/47.json`，字段字符偏移 758。

> 源时间戳含时区偏移，使用 DuckDB `try_strptime` 解析更新时间；统计日期转换为 DATE。

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

契约只有 TIMESTAMP 类型及 updated_at <= CURRENT_TIMESTAMP，没有指定 TRY_CAST 或 STRPTIME，也未规定格式解析失败处理。日期值可读不等于契约规定了解析器；本次按解析策略未定记 A，不能将 gold 的 TRY_CAST 写法冒充契约字面要求。
