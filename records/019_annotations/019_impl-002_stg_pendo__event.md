# impl-002 / stg_pendo__event

## 结论

主要原因：**A**；把握：中；标记：无。

契约规定 MD5 的六个来源字段，但没有规定连接分隔符；agent 与 gold 分别使用带分隔符和直接连接。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-002_stg_pendo__event.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：50000/50000。本次固定控制下 baseline 行/格规模：100000/1100000。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml`；原文行段 78–136。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__event.sql`，L1–24；SHA-256 `03deea93cc538aec0f18d23f3c57fed13d3f54a655904738d5f393e9ddff891c`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/staging/stg_pendo__event.sql`，L1–73；SHA-256 `067a810ec4648ab064b72c84e9a22c9cae4e9ccee01c5416a995c2bc175a5c05`。

event_key：agent SQL L12，替换原片段如下。
```sql
md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), ''), coalesce(server_name, ''), coalesce(user_agent, ''), coalesce(remote_ip, ''))) AS event_key
```
替换为：
```sql
CASE WHEN NOT visitor_id IS NULL AND NOT timestamp IS NULL AND NOT account_id IS NULL THEN MD5(CONCAT(COALESCE(CAST(visitor_id AS TEXT), ''), COALESCE(CAST(timestamp AS TEXT), ''), COALESCE(CAST(account_id AS TEXT), ''), COALESCE(server_name, ''), COALESCE(user_agent, ''), COALESCE(remote_ip, ''))) ELSE NULL END AS event_key
```

account_id_validation：agent SQL L3，替换原片段如下。
```sql
CAST(account_id AS VARCHAR) AS account_id
```
替换为：
```sql
CASE WHEN account_id ~ '^(ACC[0-9]+|[0-9]+)$' THEN CAST(account_id AS VARCHAR) END AS account_id
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-002_stg_pendo__event.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 100000 | 1100000 | {} | L0–L3均不匹配 |
| baseline | L1 | 100000 | 1100000 | {} | L0–L3均不匹配 |
| baseline | L2 | 100000 | 1100000 | {} | L0–L3均不匹配 |
| baseline | L3 | 100000 | 1100000 | {} | L0–L3均不匹配 |
| event_key | L0 | 3535 | 3535 | {"account_id": 3535} | L0–L3均不匹配 |
| event_key | L1 | 3535 | 3535 | {"account_id": 3535} | L0–L3均不匹配 |
| event_key | L2 | 3535 | 3535 | {"account_id": 3535} | L0–L3均不匹配 |
| event_key | L3 | 3535 | 3535 | {"account_id": 3535} | L0–L3均不匹配 |
| account_id_validation | L0 | 100000 | 1100000 | {} | L0–L3均不匹配 |
| account_id_validation | L1 | 100000 | 1100000 | {} | L0–L3均不匹配 |
| account_id_validation | L2 | 100000 | 1100000 | {} | L0–L3均不匹配 |
| account_id_validation | L3 | 100000 | 1100000 | {} | L0–L3均不匹配 |

- event_key（A，单处 SQL 改动）：行减少 96465，格减少 1096465。契约规定 MD5 的六个来源字段，但没有规定连接分隔符；agent 与 gold 分别使用带分隔符和直接连接。

- account_id_validation（C，单处 SQL 改动）：行减少 0，格减少 0。契约指定 account_id 正则，不合法应 nullify_field。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/1.json`，字段字符偏移 6600。

> stg_pendo__event
>       description: "Cleaned user interaction events with validated IDs and standardized timestamps"
>       source_table: "raw.event"
>       where_conditions:
>         - "visitor_id IS NOT NULL"
>         - "visitor_id != ''"
>         - "account_id IS NOT NULL"
>         - "account_id != ''"
>         - "app_id IS NOT NULL"
>         - "app_id != ''"
>         - "timestamp IS NOT NULL"
>       columns:
>         - name: visitor_id
>           data_type: VARCHAR(50)
>           constraints: [not_null]
> 

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
