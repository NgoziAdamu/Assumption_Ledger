# 042 正式标注：impl-017_stg_greenhouse__hiring_team

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**其他**；把握高；1点。只能组合修复：否。023旧主要原因`O`仅存档。

## 详细发现

### 比较口径与原始数据

013/015的变更发生在scheduled_interview_snowflake，gold raw也有同样变化；本批七张staging的直接源不在变更清单，两个marts用gold上游。benchmark加载导致是015推测，非agent行为的独立证明；按用户指定口径照常标注。

直接raw逐表013核对：`[{"table": "hiring_team", "found_in_013": true, "different": false, "columns_types_equal": true, "row_counts_equal": true}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/greenhouse.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### uniqueness

**其他**；主要；把握高。

本表契约明确声明primary_key/unique；agent按对应键只保留一条，gold保留重复记录。去掉唯一化的单改使含键差异清零，证明是规范/参照不一致，不是默认数据唯一的Data或静默降级。

是否说出：第2档——交付物里只有通用说明。最终报告有适用于此类处理的通用说明，未逐表点名本处，记第2档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-017_stg_greenhouse__hiring_team.json` / `uniqueness`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 1 | 0 | 2 | 0 |
| L1 | 1 | 0 | 2 | 0 |
| L2 | 1 | 0 | 2 | 0 |
| L3 | 1 | 0 | 2 | 0 |

L0减少：[1, 2]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml` / `text`。

```text
primary_key: ["job_id", "user_id"]
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/1.json` / event 1 / `message`。

```text
primary_key: ["job_id", "user_id"]
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/53.json` / event 53 / `args.final_thought`。

```text
staging 对声明为主键的空值行进行过滤，并按主键分组只保留一条记录以满足唯一性
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/staging/stg_greenhouse__hiring_team.sql` / `text`。

```text
WHERE _row_num = 1
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml`；SHA-256 `f4a1c779c8359b7fd5d9c8cae9760669aceb5b35f661d0fab07d0bf376762e41`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/staging/stg_greenhouse__hiring_team.sql`；SHA-256 `959bcbd3fe8395bd72545f2e7364468238111acc5ab415ef6e3e04c7309346de`。
- 023材料包：`records/023_packages/023_impl-017_stg_greenhouse__hiring_team.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引9，契约主键重复。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
