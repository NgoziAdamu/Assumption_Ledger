# 042 正式标注：impl-016_workday__employee_overview

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。

## 结论

主要原因：**其他**；把握高；2点。只能组合修复：否。023旧主要原因`O`仅存档。

## 详细发现

### 比较口径与原始数据

raw.person_contact_email_address由7284降至2448，少4836行；已回查85个事件及013/015记录，改动步骤和原因均未找到。不得编造是哪次run导致。当前stg_position直读position没有该变化；三个非staging表采用gold上游，不能把email原始减量直接计入本表CS误差。

直接raw逐表013核对：`[]`。

重跑输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 00:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 3}]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### compensation_regex

**其他**；主要；把握高。

契约明确从compensation_grade_id提取第一段数字并分档；agent实现该算法。023核实中900个grade都能提取，gold双反斜杠模式匹配0，落Ungraded。单改成Ungraded仅定位gold差异，不把其解析失败当数据事实，也不要求agent违反契约。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-016_workday__employee_overview.json` / `compensation_regex`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 156187 | 104222 | 8075594 | 7816650 |
| L1 | 156187 | 104222 | 8075594 | 7816650 |
| L2 | 156187 | 104222 | 8075594 | 7816650 |
| L3 | 156187 | 104222 | 8075594 | 7816650 |

L0减少：[51965, 258944]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml` / `text`。

```text
- name: compensation_tier
        data_type: VARCHAR
        description: 'Tier from the first digit sequence in compensation_grade_id: ≤5 ''Entry Level'', ≤10 ''Mid Level'', ≤15 ''Senior Level'', >15 ''Executive Level'', else ''Ungraded'''
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json` / event 1 / `message`。

```text
- name: compensation_tier
        data_type: VARCHAR
        description: 'Tier from the first digit sequence in compensation_grade_id: ≤5 ''Entry Level'', ≤10 ''Mid Level'', ≤15 ''Senior Level'', >15 ''Executive Level'', else ''Ungraded'''
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__employee_overview.sql` / `text`。

```text
CASE WHEN regexp_extract(coalesce(compensation_grade_id,''),'([0-9]+)',1)='' THEN 'Ungraded' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=5 THEN 'Entry Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=10 THEN 'Mid Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=15 THEN 'Senior Level' ELSE 'Executive Level' END
```

### comp_ebe_join

**Intent Misreading**；参与；把握中。

契约要求从employee enhanced派生compensation/benefits，并以worker_id、source_relation、position_id连接；agent只从position profile派生并只按position/source连接，遗漏worker范围。补齐ebe链和worker键减少7919407格，虽行数不降仍是参与因素。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-016_workday__employee_overview.json` / `comp_ebe_join`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 156187 | 156187 | 8075594 | 156187 |
| L1 | 156187 | 156187 | 8075594 | 156187 |
| L2 | 156187 | 156187 | 8075594 | 156187 |
| L3 | 156187 | 156187 | 8075594 | 156187 |

L0减少：[0, 7919407]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml` / `text`。

```text
Compensation/benefits (cb):
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json` / event 1 / `message`。

```text
Compensation/benefits (cb):
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__employee_overview.sql` / `text`。

```text
LEFT JOIN comp ON b.position_id=comp.position_id AND b.source_relation=comp.source_relation
```

### 排除的旧控制/混合补丁

- `records/023_reruns_impl-016_workday__employee_overview.json#comp_base_multiplicity`：旧补丁仅按position扩增，没有补齐worker键，不能作为正确意图的修复；以comp_ebe_join替代。

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml`；SHA-256 `8f0707fc595c6f2f1e46a1983436959278e10315cb723e975c2811858d737c91`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__employee_overview.sql`；SHA-256 `60a17999d38a8c037348475fbd70782821d52282340690dde24803b7dc7a8751`。
- 023材料包：`records/023_packages/023_impl-016_workday__employee_overview.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引5，grade regexp。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
