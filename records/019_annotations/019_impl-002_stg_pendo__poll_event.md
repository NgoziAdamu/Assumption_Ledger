# impl-002 / stg_pendo__poll_event

## 结论

主要原因：**多因并列**；把握：中；标记：无。

契约只声明代理键及类型，没有规定生成字段和拼接公式；差异取决于未规定的键生成选择。；URL 校验没有执行契约正则字面规则。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-002_stg_pendo__poll_event.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：5000/5000。本次固定控制下 baseline 行/格规模：5000/10000。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml`；原文行段 461–521。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__poll_event.sql`，L1–20；SHA-256 `d5932f00d1714564e445907eb8e3bcc2e2f0a5130816d90065523d7abaee6991`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/staging/stg_pendo__poll_event.sql`，L1–89；SHA-256 `d060c7cb16570c0e84faa57d3eed995bb471b309d83e931277e271cf87d5f553`。

poll_event_key：agent SQL L19，替换原片段如下。
```sql
md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(poll_id AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), ''))) AS poll_event_key
```
替换为：
```sql
MD5(CONCAT(COALESCE(CAST(visitor_id AS TEXT), ''), COALESCE(CAST(timestamp AS TEXT), ''), COALESCE(CAST(account_id AS TEXT), ''), COALESCE(server_name, ''), COALESCE(CAST(poll_id AS TEXT), ''), COALESCE(CAST(guide_id AS TEXT), ''), COALESCE(user_agent, ''), COALESCE(remote_ip, ''))) AS poll_event_key
```

url：agent SQL L18，替换原片段如下。
```sql
CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS VARCHAR)), '') END AS url
```
替换为：
```sql
CASE WHEN TRIM(url) = '' THEN NULL WHEN NOT url IS NULL AND REGEXP_FULL_MATCH(url, '^https?://') THEN TRIM(url) ELSE NULL END AS url
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-002_stg_pendo__poll_event.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

并列项不确定性：poll_event_key=看到了但没提（event 1，同一下节可见证据）；url=看到了但没提（event 1，同一下节可见证据）。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 5000 | 10000 | {"poll_event_key": 5000, "url": 5000} | L0–L3均不匹配 |
| baseline | L1 | 5000 | 10000 | {"poll_event_key": 5000, "url": 5000} | L0–L3均不匹配 |
| baseline | L2 | 5000 | 10000 | {"poll_event_key": 5000, "url": 5000} | L0–L3均不匹配 |
| baseline | L3 | 5000 | 10000 | {"poll_event_key": 5000, "url": 5000} | L0–L3均不匹配 |
| poll_event_key | L0 | 5000 | 5000 | {"url": 5000} | L0–L3均不匹配 |
| poll_event_key | L1 | 5000 | 5000 | {"url": 5000} | L0–L3均不匹配 |
| poll_event_key | L2 | 5000 | 5000 | {"url": 5000} | L0–L3均不匹配 |
| poll_event_key | L3 | 5000 | 5000 | {"url": 5000} | L0–L3均不匹配 |
| url | L0 | 5000 | 5000 | {"poll_event_key": 5000} | L0–L3均不匹配 |
| url | L1 | 5000 | 5000 | {"poll_event_key": 5000} | L0–L3均不匹配 |
| url | L2 | 5000 | 5000 | {"poll_event_key": 5000} | L0–L3均不匹配 |
| url | L3 | 5000 | 5000 | {"poll_event_key": 5000} | L0–L3均不匹配 |

- poll_event_key（A，单处 SQL 改动）：行减少 0，格减少 5000。契约只声明代理键及类型，没有规定生成字段和拼接公式；差异取决于未规定的键生成选择。

- url（C，单处 SQL 改动）：行减少 0，格减少 5000。URL 校验没有执行契约正则字面规则。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/1.json`，字段字符偏移 19865。

> stg_pendo__poll_event
>       description: "Cleaned poll interaction events with validated responses"
>       source_table: "raw.poll_event"
>       columns:
>         - name: account_id
>           data_type: BIGINT
>           constraints: [not_null]
>         - name: guide_id
>           data_type: VARCHAR(50)
>           constraints: [not_null]
>         - name: poll_id
>           data_type: VARCHAR(50)
>           constraints: [not_null]
>         - name: remote_ip
>           data_type: VARCHAR(255)
>           valida

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
