# impl-002 / stg_pendo__user

## 结论

主要原因：**U**；把握：中；标记：无。

P：日期文本可直接 TRY_CAST；实际含时区后缀而解析失败。

参与因素：normalized_user_type=C。

不确定性四档：**只有通用策略说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-002_stg_pendo__user.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：11/13。本次固定控制下 baseline 行/格规模：8/18。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml`；原文行段 45–77。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__user.sql`，L1–10；SHA-256 `a2cd02b1558aaa86bdf659ddec29f7ed722c6d5220dd2479c3fe705ee53ae0f7`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/staging/stg_pendo__user.sql`，L1–9；SHA-256 `7e207071ee00b8f5f09d9adf17e9194c0e94485d578c3c74495cec65c7b1cd34`。

deleted_at_parse：agent SQL L3，替换原片段如下。
```sql
TRY_CAST(NULLIF(deleted_at, '') AS TIMESTAMP)
```
替换为：
```sql
TRY_CAST(SUBSTRING(NULLIF(deleted_at, ''),1,23) AS TIMESTAMP)
```

required_user_id：agent SQL L9，替换原片段如下。
```sql
WHERE user_type IN
```
替换为：
```sql
WHERE id IS NOT NULL AND id<>'' AND user_type IN
```

normalized_user_type：agent SQL L9，替换原片段如下。
```sql
WHERE user_type IN
```
替换为：
```sql
WHERE lower(trim(user_type)) IN
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-002_stg_pendo__user.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 1 条（上限5）；代价档：一条查询。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

核实：
```sql
SELECT count(*) n,count(*) FILTER(WHERE deleted_at IS NOT NULL AND deleted_at<>'' AND try_cast(deleted_at AS TIMESTAMP) IS NULL AND try_cast(substring(deleted_at,1,23) AS TIMESTAMP) IS NOT NULL) failed_direct FROM raw.user
```
结果（仅统计/类型）：`[[17, 12]]`

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 8 | 18 | {"deleted_at": 6} | L0–L3均不匹配 |
| baseline | L1 | 8 | 18 | {"deleted_at": 6} | L0–L3均不匹配 |
| baseline | L2 | 8 | 18 | {"deleted_at": 6} | L0–L3均不匹配 |
| baseline | L3 | 8 | 18 | {"deleted_at": 6} | L0–L3均不匹配 |
| deleted_at_parse | L0 | 2 | 12 | {} | L0–L3均不匹配 |
| deleted_at_parse | L1 | 2 | 12 | {} | L0–L3均不匹配 |
| deleted_at_parse | L2 | 2 | 12 | {} | L0–L3均不匹配 |
| deleted_at_parse | L3 | 2 | 12 | {} | L0–L3均不匹配 |
| required_user_id | L0 | 8 | 18 | {"deleted_at": 6} | L0–L3均不匹配 |
| required_user_id | L1 | 8 | 18 | {"deleted_at": 6} | L0–L3均不匹配 |
| required_user_id | L2 | 8 | 18 | {"deleted_at": 6} | L0–L3均不匹配 |
| required_user_id | L3 | 8 | 18 | {"deleted_at": 6} | L0–L3均不匹配 |
| normalized_user_type | L0 | 8 | 8 | {"deleted_at": 8} | L0–L3均不匹配 |
| normalized_user_type | L1 | 8 | 8 | {"deleted_at": 8} | L0–L3均不匹配 |
| normalized_user_type | L2 | 8 | 8 | {"deleted_at": 8} | L0–L3均不匹配 |
| normalized_user_type | L3 | 8 | 8 | {"deleted_at": 8} | L0–L3均不匹配 |

- deleted_at_parse（U，单处 SQL 改动）：行减少 6，格减少 6。P：日期文本可直接 TRY_CAST；实际含时区后缀而解析失败。

- required_user_id（C，单处 SQL 改动）：行减少 0，格减少 0。契约必需 user_id 过滤遗漏。

- normalized_user_type（C，单处 SQL 改动）：行减少 0，格减少 10。契约要求规范化后枚举判断；agent 在原始值上筛选。

U 条件：P 及反例见结论和核实查询；实际可见材料见下一节；仅指定取列/解析/同键结合的改动达到第4条件。原始轨迹未出现检验该格式可解析性的查询；schema 中 VARCHAR 本身不足以判定 P。

## agent 可见证据及不确定性

event 59 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，字段字符偏移 756。

> Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
