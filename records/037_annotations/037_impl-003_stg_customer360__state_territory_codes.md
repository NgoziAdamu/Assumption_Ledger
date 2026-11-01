# impl-003_stg_customer360__state_territory_codes（037 正式批次）

主要原因：**Unstated Choice**；把握：中。019旧主要原因原样保留：`A`，不作为新类别依据。

## 范围与材料

- 层：staging；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/staging/stg_customer360__state_territory_codes.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，finish 51 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/customer360.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-003_stg_customer360__state_territory_codes.json`；037补充：`records/037_checks/`。

## 逐点标注

### distinct_rows

- 类别：Unstated Choice；角色：主要；把握：中。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约未声明整行去重或唯一性，agent保留重复，gold DISTINCT删除；这是材料未定的保留策略。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: stg_customer360__state_territory_codes
>       description: "Standardized state and territory code reference data with country relationships for address validation"
>       source_table: raw.state_territory_codes
>       columns:
>         - name: state_territory
>           data_type: VARCHAR(255)
>           constraints: [not_null]
>         - name: state_code
>           data_type: VARCHAR(5)
>           constraints: [not_null]
>           validation_rules:
>             - rule: "LENGTH(TRIM(state_code)) BETWEEN 2 AND 5"
>               on_failure: delete_row
>             - rule: "state_code = UPPER(TRIM(state_code))"
>               on_failure: correct
>         - name: alpha2_country_code
>           data_typ

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/staging/stg_customer360__state_territory_codes.sql`，第 12–12 行：

```sql
select c.state_territory, c.state_code, c.alpha2_country_code
```

单改/诊断：`records/019_reruns_impl-003_stg_customer360__state_territory_codes.json#distinct_rows`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 55/165 | 0/0 | 55/165 |
| L1 | 55/165 | 0/0 | 55/165 |
| L2 | 55/165 | 0/0 | 55/165 |
| L3 | 55/165 | 0/0 | 55/165 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，event `51.args.final_thought`：

> 契约对来源重复记录以及部分聚合排序并未规定唯一 tie-breaker；按 DuckDB 实际行为保留未指定并列顺序，不额外引入业务假设。

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

### membership

- 类别：Intent Misreading；角色：非原因；把握：高。
- 是否说出：第2档（交付物里只有通用说明）。
- 证据在场：是；曾经理解对过：否；系统提示：不适用。

契约成员校验为存在性判断，agent使用可能扩行的连接；单改为IN不减少本次差异。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - rule: "regexp_matches(alpha2_country_code, '^[A-Z]{2}$')"
>               on_failure: delete_row
>             - rule: "alpha2_country_code IN (SELECT country_code_alpha_2 FROM stg_customer360__country_codes)"
>               on_failure: delete_row

契约已规定算法/做法，按第5节归Intent。

曾经理解对过=否：复核留存run/finish中的先前代码，没有找到该处先正确实现后退化的证据；仅读到正确契约不算曾实现正确。

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/staging/stg_customer360__state_territory_codes.sql`，第 14–15 行：

```sql
inner join staging.stg_customer360__country_codes cc
    on c.alpha2_country_code = cc.country_code_alpha_2
```

单改/诊断：`records/019_reruns_impl-003_stg_customer360__state_territory_codes.json#membership`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 55/165 | 55/165 | 0/0 |
| L1 | 55/165 | 55/165 | 0/0 |
| L2 | 55/165 | 55/165 | 0/0 |
| L3 | 55/165 | 55/165 | 0/0 |

本点存在未实现/未确立的前提，但按当前原始计算链单改没有净减少规模，不列参与因素。若单改反而增加差异，保留负数：其他占位、NULL、默认值和gold差异可能遮蔽该处；不把这种干预冒充完全修复。

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，event `51.args.final_thought`：

> staging 中无法满足必要名称、国家码格式/引用条件的记录被过滤；超出 1–999 的 numeric country code 置为 NULL。

交付报告只有覆盖多个点的通用说明；没有明确说明本点所缺规则、偏差或选择。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：
