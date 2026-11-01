# impl-003_stg_customer360__country_codes（037 正式批次）

主要原因：**其他**；把握：高。019旧主要原因原样保留：`O`，不作为新类别依据。

## 范围与材料

- 层：staging；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/staging/stg_customer360__country_codes.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，finish 51 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/customer360.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-003_stg_customer360__country_codes.json`；037补充：`records/037_checks/`。

## 逐点标注

### dedup

- 类别：其他；角色：主要；把握：高。
- 是否说出：第1档（交付物里针对本处说明了）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约要求alpha-2唯一，agent稳定去重，gold保留重复；移除去重仅作差异诊断。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: country_code_alpha_2
>           data_type: VARCHAR(2)
>           constraints: [not_null, unique]
>           validation_rules:
>             - rule: "LENGTH(country_code_alpha_2) = 2"
>               on_failure: delete_row
>             - rule: "country_code_alpha_2 = UPPER(TRIM(country_code_alpha_2))"
>               on_failure: correct
>             - rule: "country_code_alpha_2 ~ '^[A-Z]{2}$'"
>               on_failure: delete_row

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/staging/stg_customer360__country_codes.sql`，第 20–20 行：

```sql
where _row_num = 1
```

单改/诊断：`records/019_reruns_impl-003_stg_customer360__country_codes.json#dedup`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1/5 | 0/0 | 1/5 |
| L1 | 1/5 | 0/0 | 1/5 |
| L2 | 1/5 | 0/0 | 1/5 |
| L3 | 1/5 | 0/0 | 1/5 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，event `51.args.final_thought`：

> country alpha-2 冲突记录通过稳定字段排序保留一条，避免唯一键重复。

交付报告明确点到这张表/这类指标及其占位或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：

`records/019_queries.json` / 诊断：
```sql
SELECT count(*) duplicate_keys,sum(n-1) excess_rows FROM (SELECT country_code_alpha_2,count(*) n FROM staging.stg_customer360__country_codes GROUP BY 1 HAVING count(*)>1)
```
结果：`[[1, 1]]`
