# 042 正式标注：impl-015_stg_quickbooks__vendor

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**Quiet Downgrade**；把握高；1点。只能组合修复：否。023旧主要原因`D`仅存档。

## 详细发现

### 比较口径与原始数据

013显示30张raw列/类型不同，行数均未变。event45为解决同库重复ATTACH的Unique file handle conflict，改用fetchdf/register复制raw；这是agent改动，照常标注。直接源按下面逐表检查；CS表使用gold上游，不将本题全部raw变化归给该表。

直接raw逐表013核对：`[{"table": "vendor_data", "found_in_013": true, "different": true, "columns_types_equal": false, "row_counts_equal": true}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/quickbooks.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### vendor_name

**Quiet Downgrade**；主要；把握高。

raw.display_name和company_name均1500非空，有明显名称候选，agent未判断就整列NULL；不属于无对应源列且默认未定。

是否说出：第2档——交付物里只有通用说明。最终报告有适用于此类处理的通用说明，未逐表点名本处，记第2档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-015_stg_quickbooks__vendor.json` / `vendor_name`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 1500 | 0 | 1500 | 0 |
| L1 | 1500 | 0 | 1500 | 0 |
| L2 | 1500 | 0 | 1500 | 0 |
| L3 | 1500 | 0 | 1500 | 0 |

L0减少：[1500, 1500]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml` / `text`。

```text
- name: name
          data_type: VARCHAR
          constraints: [not_null]
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/1.json` / event 1 / `message`。

```text
- name: name
          data_type: VARCHAR
          constraints: [not_null]
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/73.json` / event 73 / `args.final_thought`。

```text
对原始字段中不存在的合同字段采用类型化 NULL
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/sql/staging/stg_quickbooks__vendor.sql` / `text`。

```text
CAST(NULL AS VARCHAR) AS "name"
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml`；SHA-256 `c7c31842035fff7336164f7713a735dde48f8f77e19e992d2dae072b0144c51a`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/sql/staging/stg_quickbooks__vendor.sql`；SHA-256 `9ddbba48c468abc9ea4e6b27c803eea775129be053fe2e4cea53d8b65d230590`。
- 023材料包：`records/023_packages/023_impl-015_stg_quickbooks__vendor.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引2，候选名称。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
