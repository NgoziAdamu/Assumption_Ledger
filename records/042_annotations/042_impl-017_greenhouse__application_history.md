# 042 正式标注：impl-017_greenhouse__application_history

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。

## 结论

主要原因：**其他**；把握中；1点。只能组合修复：否。023旧主要原因`O`仅存档。

## 详细发现

### 比较口径与原始数据

013/015的变更发生在scheduled_interview_snowflake，gold raw也有同样变化；本批七张staging的直接源不在变更清单，两个marts用gold上游。benchmark加载导致是015推测，非agent行为的独立证明；按用户指定口径照常标注。

直接raw逐表013核对：`[]`。

重跑输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/greenhouse.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-24 18:32:44.279463+08:00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-24'", "count": 0}]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。

唯一Other点，以同钟L0～L3差异及契约定位，不虚构修复。

### floating_days

**其他**；主要；把握中。

未结束区间用current_timestamp符合契约。023同一固定时刻重跑后仅days_in_stage浮点运算剩40行40格，L2/L3为0；两种等价秒差/微秒差换算的精度与运行时间条件造成差异，不是未定义的业务算法选择。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-017_greenhouse__application_history.json` / `baseline`。仅同钟L0～L3诊断；只有同一Other原因，无实际单改排名。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 40 | 40 | 40 | 40 |
| L1 | 40 | 40 | 40 | 40 |
| L2 | 0 | 0 | 0 | 0 |
| L3 | 0 | 0 | 0 | 0 |

同钟基线即上表；不把L2容差清零伪装成SQL单改。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml` / `text`。

```text
- name: days_in_stage
        data_type: DOUBLE
        description: Fractional days in the interval computed from the exact seconds between bounds divided by 86,400; no rounding
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/1.json` / event 1 / `message`。

```text
- name: days_in_stage
        data_type: DOUBLE
        description: Fractional days in the interval computed from the exact seconds between bounds divided by 86,400; no rounding
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml`；SHA-256 `f4a1c779c8359b7fd5d9c8cae9760669aceb5b35f661d0fab07d0bf376762e41`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/marts/greenhouse__application_history.sql`；SHA-256 `858519d3e09ec304887d05e672eb703614e6f876305085492523aa49a3a75c69`。
- 023材料包：`records/023_packages/023_impl-017_greenhouse__application_history.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引14，时间边界。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
