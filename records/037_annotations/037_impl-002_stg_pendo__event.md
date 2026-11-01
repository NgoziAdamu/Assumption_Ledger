# impl-002_stg_pendo__event（037 正式批次）

主要原因：**Unstated Choice**；把握：中。019旧主要原因原样保留：`A`，不作为新类别依据。

## 范围与材料

- 层：staging；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__event.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，finish 59 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-002_stg_pendo__event.json`；037补充：`records/037_checks/`。

## 逐点标注

### event_key

- 类别：Unstated Choice；角色：主要；把握：中。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约指定六个MD5来源字段但没有指定拼接分隔符；带分隔符与直接拼接造成键值不同。hash是计算值，不归Form。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: event_key
>           data_type: VARCHAR(255)
>           description: "Generated MD5 hash surrogate key based on visitor_id, timestamp, account_id, server_name, user_agent, and remote_ip"

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__event.sql`，第 12–12 行：

```sql
md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), ''), coalesce(server_name, ''), coalesce(user_agent, ''), coalesce(remote_ip, ''))) AS event_key
```

单改/诊断：`records/019_reruns_impl-002_stg_pendo__event.json#event_key`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 100000/1100000 | 3535/3535 | 96465/1096465 |
| L1 | 100000/1100000 | 3535/3535 | 96465/1096465 |
| L2 | 100000/1100000 | 3535/3535 | 96465/1096465 |
| L3 | 100000/1100000 | 3535/3535 | 96465/1096465 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/1.json`，event `1.message`：

> - name: event_key
>           data_type: VARCHAR(255)
>           description: "Generated MD5 hash surrogate key based on visitor_id, timestamp, account_id, server_name, user_agent, and remote_ip"

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### account_id_validation

- 类别：Intent Misreading；角色：非原因；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约的account_id校验规则被省略；当前hash差异掩盖其整表规模贡献。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: account_id
>           data_type: VARCHAR(50)
>           constraints: [not_null]
>           validation_rules:
>             - rule: "account_id IS NOT NULL AND account_id != ''"
>               on_failure: delete_row
>             - rule: "account_id ~ '^(ACC[0-9]+|[0-9]+)$'"
>               on_failure: nullify_field

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__event.sql`，第 3–3 行：

```sql
CAST(account_id AS VARCHAR) AS account_id
```

单改/诊断：`records/019_reruns_impl-002_stg_pendo__event.json#account_id_validation`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 100000/1100000 | 100000/1100000 | 0/0 |
| L1 | 100000/1100000 | 100000/1100000 | 0/0 |
| L2 | 100000/1100000 | 100000/1100000 | 0/0 |
| L3 | 100000/1100000 | 100000/1100000 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
