# impl-005_stg_google_ads__ad_history（037 正式批次）

主要原因：**已说出的选择**；把握：中。019旧主要原因原样保留：`A`，不作为新类别依据。

## 范围与材料

- 层：staging；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_history.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/47.json`，finish 47 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/google_ads.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-005_stg_google_ads__ad_history.json`；037补充：`records/037_checks/`。

## 逐点标注

### timestamp_cast

- 类别：已说出的选择；角色：主要；把握：中。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约只指定TIMESTAMP目标及有效性检查，没有规定源时区文本解析器。agent用try_strptime保留可解析时间，gold直接TRY_CAST得到NULL；这是未指定的解析选择。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: updated_at
>           data_type: TIMESTAMP
>           constraints: [not_null]
>           validation_rules:
>             - rule: "updated_at <= CURRENT_TIMESTAMP"
>               on_failure: delete_row

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__ad_history.sql`，第 6–6 行：

```sql
try_strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP
```

单改/诊断：`records/019_reruns_impl-005_stg_google_ads__ad_history.json#timestamp_cast`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 10000/90000 | 0/0 | 10000/90000 |
| L1 | 10000/90000 | 0/0 | 10000/90000 |
| L2 | 10000/90000 | 0/0 | 10000/90000 |
| L3 | 10000/90000 | 0/0 | 10000/90000 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/47.json`，event `47.args.final_thought`：

> 源时间戳含时区偏移，使用 DuckDB `try_strptime` 解析更新时间；统计日期转换为 DATE。

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
