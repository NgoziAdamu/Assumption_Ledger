# impl-002_stg_pendo__user（037 正式批次）

主要原因：**Data Misconception**；把握：中。019旧主要原因原样保留：`U`，不作为新类别依据。

## 范围与材料

- 层：staging；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__user.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，finish 59 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-002_stg_pendo__user.json`；037补充：`records/037_checks/`。

## 逐点标注

### deleted_at_parse

- 类别：Data Misconception；角色：主要；把握：中。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：否；曾经理解对过：否；系统提示：不适用。

P：raw.user中非空deleted_at文本可由直接TRY_CAST(... AS TIMESTAMP)解析。契约只给目标类型/空值规则，未指定解析算法；019在agent留存raw上核实17行中12行直接转换失败而截取前23字符成功，证伪P。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: deleted_at
>           data_type: TIMESTAMP
>           validation_rules:
>             - rule: "deleted_at = CASE WHEN deleted_at = '' THEN NULL ELSE deleted_at END"
>               on_failure: nullify_field

已检查deleted_at完整契约：只给TIMESTAMP及空值规则，未指定解析算法。P由agent可见raw核实；未使用gold证伪。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

P：raw.user中非空deleted_at文本可由直接TRY_CAST(... AS TIMESTAMP)解析。

初始契约只规定目标类型，列清单只能看到VARCHAR；未见agent查询直接转换失败的原始格式。单凭这些不能证伪P，所以证据在场=否。

反证：`records/019_queries.json` 中impl-002 / stg_pendo__user的只读raw核实，17行中12行直接解析失败但substring(1,23)成功。查询的是agent当时可见数据。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__user.sql`，第 3–3 行：

```sql
TRY_CAST(NULLIF(deleted_at, '') AS TIMESTAMP)
```

单改/诊断：`records/019_reruns_impl-002_stg_pendo__user.json#deleted_at_parse`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 8/18 | 2/12 | 6/6 |
| L1 | 8/18 | 2/12 | 6/6 |
| L2 | 8/18 | 2/12 | 6/6 |
| L3 | 8/18 | 2/12 | 6/6 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> The work includes staging raw-field mapping, timestamp parsing, event-key generation, filtering and nullification; latest-record models; daily aggregates and calendar spines; and mart entities.

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### normalized_user_type

- 类别：Intent Misreading；角色：参与；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约要求先规范化user_type再枚举校验，agent在原始值上过滤。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: user_type
>           data_type: VARCHAR(50)
>           constraints: [not_null]
>           validation_rules:
>             - rule: "user_type IN ('system', 'internal', 'api', 'external')"
>               on_failure: delete_row
>             - rule: "user_type = LOWER(TRIM(user_type))"
>               on_failure: correct

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__user.sql`，第 9–9 行：

```sql
WHERE user_type IN
```

单改/诊断：`records/019_reruns_impl-002_stg_pendo__user.json#normalized_user_type`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 8/18 | 8/8 | 0/10 |
| L1 | 8/18 | 8/8 | 0/10 |
| L2 | 8/18 | 8/8 | 0/10 |
| L3 | 8/18 | 8/8 | 0/10 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### required_user_id

- 类别：Intent Misreading；角色：非原因；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约要求必需user_id校验；遗漏该条件但单改未减少本次差异。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: user_id
>           data_type: VARCHAR(50)
>           constraints: [not_null]

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__user.sql`，第 9–9 行：

```sql
WHERE user_type IN
```

单改/诊断：`records/019_reruns_impl-002_stg_pendo__user.json#required_user_id`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 8/18 | 8/18 | 0/0 |
| L1 | 8/18 | 8/18 | 0/0 |
| L2 | 8/18 | 8/18 | 0/0 |
| L3 | 8/18 | 8/18 | 0/0 |

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

`records/019_queries.json` / 核实：
```sql
SELECT count(*) n,count(*) FILTER(WHERE deleted_at IS NOT NULL AND deleted_at<>'' AND try_cast(deleted_at AS TIMESTAMP) IS NULL AND try_cast(substring(deleted_at,1,23) AS TIMESTAMP) IS NOT NULL) failed_direct FROM raw.user
```
结果：`[[17, 12]]`

规则问题：时间解析也可能读成未规定解析方式的Choice。本点区分的是直接解析可成功这一可核实数据事实；反证来自raw，而非gold选了另一解析器，因此按Data，置信中。
