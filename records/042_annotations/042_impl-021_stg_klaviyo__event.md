# 042 正式标注：impl-021_stg_klaviyo__event

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**其他**；把握高；1点。只能组合修复：否。023旧主要原因`O`仅存档。

## 详细发现

### 比较口径与原始数据

五张raw均有013/015记录的变化，gold raw也包含变化；按指定口径用agent留存raw标五张staging，intermediate用gold上游。ID稀疏是实际可见事实，其形成原因未查证，不能从稀疏反推agent删raw。

直接raw逐表013核对：`[{"table": "event", "found_in_013": true, "different": true, "columns_types_equal": false, "row_counts_equal": false}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### email_regex

**其他**；主要；把握高。

契约要求非法property email删除；agent正确匹配普通合法邮箱，gold双反斜杠正则拒绝2496个本可识别合法邮箱。属于明确格式验证与参照实现差异，不是源数据真实全非法。

是否说出：第2档——交付物里只有通用说明。最终报告有适用于此类处理的通用说明，未逐表点名本处，记第2档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-021_stg_klaviyo__event.json` / `email_regex`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 2496 | 0 | 34944 | 0 |
| L1 | 2496 | 0 | 34944 | 0 |
| L2 | 2496 | 0 | 34944 | 0 |
| L3 | 2496 | 0 | 34944 | 0 |

L0减少：[2496, 34944]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml` / `text`。

```text
Rows with an invalid property_email (when present) are dropped."
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/1.json` / event 1 / `message`。

```text
Rows with an invalid property_email (when present) are dropped."
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/41.json` / event 41 / `args.final_thought`。

```text
无效关键 ID 和非法邮件记录被排除
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/staging/stg_klaviyo__event.sql` / `text`。

```text
(property_email is null or regexp_full_match(lower(trim(cast(property_email as varchar))), '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}'))
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml`；SHA-256 `db04fb84955b6385dd63b72bdf7aae27ac9f612a685f938eabf7051f12cd675f`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/staging/stg_klaviyo__event.sql`；SHA-256 `e55a5b163d45b28faeba2260896a33b05c20f675a93d5ec4192202b1e1563956`。
- 023材料包：`records/023_packages/023_impl-021_stg_klaviyo__event.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引39，email 两种正则。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
