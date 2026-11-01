# impl-002_stg_pendo__poll_event（037 正式批次）

主要原因：**多因并列**；把握：中。019旧主要原因原样保留：`多因并列`，不作为新类别依据。

## 范围与材料

- 层：staging；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__poll_event.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，finish 59 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-002_stg_pendo__poll_event.json`；037补充：`records/037_checks/`。

## 逐点标注

### poll_event_key

- 类别：Unstated Choice；角色：并列；把握：中。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

代理键算法/拼接未规定；不拿gold键算法作为规格。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: poll_event_key
>           data_type: VARCHAR(255)

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__poll_event.sql`，第 19–19 行：

```sql
md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(poll_id AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), ''))) AS poll_event_key
```

单改/诊断：`records/019_reruns_impl-002_stg_pendo__poll_event.json#poll_event_key`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 5000/10000 | 5000/5000 | 0/5000 |
| L1 | 5000/10000 | 5000/5000 | 0/5000 |
| L2 | 5000/10000 | 5000/5000 | 0/5000 |
| L3 | 5000/10000 | 5000/5000 | 0/5000 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/1.json`，event `1.message`：

> - name: poll_event_key
>           data_type: VARCHAR(255)

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### url

- 类别：Intent Misreading；角色：并列；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约给出可执行的URL正则字面规则；agent只做trim。按第5节以DuckDB实际正则效果为准。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: url
>           data_type: VARCHAR(255)
>           validation_rules:
>             - rule: "url = NULLIF(TRIM(url), '')"
>               on_failure: correct
>             - rule: "url IS NULL OR url ~ '^https?://'"
>               on_failure: nullify_field

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__poll_event.sql`，第 18–18 行：

```sql
CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS VARCHAR)), '') END AS url
```

单改/诊断：`records/019_reruns_impl-002_stg_pendo__poll_event.json#url`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 5000/10000 | 5000/5000 | 0/5000 |
| L1 | 5000/10000 | 5000/5000 | 0/5000 |
| L2 | 5000/10000 | 5000/5000 | 0/5000 |
| L3 | 5000/10000 | 5000/5000 | 0/5000 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
