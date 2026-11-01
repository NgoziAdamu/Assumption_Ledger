# impl-002_stg_pendo__visitor_history（037 正式批次）

主要原因：**代码写错**；把握：高。019旧主要原因原样保留：`I`，不作为新类别依据。

## 范围与材料

- 层：staging；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__visitor_history.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，finish 59 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-002_stg_pendo__visitor_history.json`；037补充：`records/037_checks/`。

## 逐点标注

### last_visit_parse

- 类别：代码写错；角色：主要；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

同一最终SQL对first_visit和last_updated_at已用截取解析，只有last_visit遗漏，存在正确实现意图的代码内证据。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: stg_pendo__visitor_history
>       description: "Cleaned visitor tracking data with validated visitor and account associations"
>       source_table: "raw.visitor_history"
>       columns:
>         - name: visitor_id
>           data_type: VARCHAR(50)
>           constraints: [not_null]
>         - name: account_id
>           data_type: VARCHAR(50)
>           constraints: [not_null]
>         - name: first_visit_at
>           data_type: TIMESTAMP
>         - name: visitor_id_hash
>           data_type: DOUBLE
>         - name: last_browser_name
>           data_type: VARCHAR(255)
>         - name: last_browser_version
>           data_type: VARCHAR(255)
>         - name: last_operating_system
>           data_type: V

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__visitor_history.sql`，第 12–12 行：

```sql
TRY_CAST(last_visit AS TIMESTAMP)
```

单改/诊断：`records/019_reruns_impl-002_stg_pendo__visitor_history.json#last_visit_parse`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 8000/8000 | 0/0 | 8000/8000 |
| L1 | 8000/8000 | 0/0 | 8000/8000 |
| L2 | 8000/8000 | 0/0 | 8000/8000 |
| L3 | 8000/8000 | 0/0 | 8000/8000 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，event `59.args.final_thought`：

> The work includes staging raw-field mapping, timestamp parsing, event-key generation, filtering and nullification; latest-record models; daily aggregates and calendar spines; and mart entities.

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：

`records/019_queries.json` / 核实：
```sql
SELECT count(*) n,count(*) FILTER(WHERE try_cast(last_visit AS TIMESTAMP) IS NULL AND try_cast(substring(last_visit,1,23) AS TIMESTAMP) IS NOT NULL) failed_direct FROM raw.visitor_history
```
结果：`[[8000, 8000]]`
