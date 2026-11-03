# 042 正式标注：impl-016_workday__position_overview

## 任务

按冻结v3.2第3～8节逐点重标；层：marts。

## 结论

主要原因：**其他**；把握高；5点。只能组合修复：否。023旧主要原因`O`仅存档。

## 详细发现

### 比较口径与原始数据

raw.person_contact_email_address由7284降至2448，少4836行；已回查85个事件及013/015记录，改动步骤和原因均未找到。不得编造是哪次run导致。当前stg_position直读position没有该变化；三个非staging表采用gold上游，不能把email原始减量直接计入本表CS误差。

直接raw逐表013核对：`[]`。

重跑输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 00:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 4}]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### compensation_regex

**其他**；主要；把握高。

契约明确从compensation_grade_id提取第一段数字并分档；agent实现该算法。023核实中900个grade都能提取，gold双反斜杠模式匹配0，落Ungraded。单改成Ungraded仅定位gold差异，不把其解析失败当数据事实，也不要求agent违反契约。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-016_workday__position_overview.json` / `compensation_regex`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 4000 | 1976 | 11816 | 7816 |
| L1 | 4000 | 1976 | 11816 | 7816 |
| L2 | 4000 | 1976 | 11816 | 7816 |
| L3 | 4000 | 1976 | 11816 | 7816 |

L0减少：[2024, 4000]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml` / `text`。

```text
- name: compensation_tier
        data_type: VARCHAR
        description: 'Tier derived from compensation_grade_id digits: Entry ≤5; Mid ≤10; Senior ≤15; Executive >15; ''Ungraded'' when NULL or not numeric'
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json` / event 1 / `message`。

```text
- name: compensation_tier
        data_type: VARCHAR
        description: 'Tier derived from compensation_grade_id digits: Entry ≤5; Mid ≤10; Senior ≤15; Executive >15; ''Ungraded'' when NULL or not numeric'
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__position_overview.sql` / `text`。

```text
CASE WHEN regexp_extract(compensation_grade_id,'([0-9]+)',1)='' THEN 'Ungraded' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=5 THEN 'Entry Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=10 THEN 'Mid Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=15 THEN 'Senior Level' ELSE 'Executive Level' END
```

### organization_dimension

**Intent Misreading**；参与；把握高。

契约要求连接organization及organization metrics；agent只用后者，active限制导致inactive组织维度缺失。补齐维度连接改善7784格，行不变仍算参与。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-016_workday__position_overview.json` / `organization_dimension`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 4000 | 4000 | 11816 | 4032 |
| L1 | 4000 | 4000 | 11816 | 4032 |
| L2 | 4000 | 4000 | 11816 | 4032 |
| L3 | 4000 | 4000 | 11816 | 4032 |

L0减少：[0, 7784]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml` / `text`。

```text
Organizational context: Link positions to organizations and organization metrics. Also link to job profile. similar_positions_in_department is the count of positions sharing the same organization_id and job_profile_id across the dataset.
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json` / event 1 / `message`。

```text
Organizational context: Link positions to organizations and organization metrics. Also link to job profile. similar_positions_in_department is the count of positions sharing the same organization_id and job_profile_id across the dataset.
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__position_overview.sql` / `text`。

```text
SELECT organization_id,source_relation,organization_name,organization_type,organization_sub_type,staffing_model,current_employee_count,organization_health_score,annual_turnover_rate,performance_category,organization_size_category FROM intermediate.int_workday__organization_metrics
```

### similar_count_only

**Unstated Choice**；非原因；把握中。

同组织同job的position计数采用distinct position_id或连接后行数，契约没有给COUNT表达式；本数据单独切换计数无收益。与组织来源选择分开，避免沿用同时改两处的旧similar_group。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用+新做；`records/042_checks/supplement_impl-016_workday__position_overview.json` / `similar_count_only`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 4000 | 4000 | 11816 | 11816 |
| L1 | 4000 | 4000 | 11816 | 11816 |
| L2 | 4000 | 4000 | 11816 | 11816 |
| L3 | 4000 | 4000 | 11816 | 11816 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml` / `text`。

```text
similar_positions_in_department is the count of positions sharing the same organization_id and job_profile_id across the dataset.
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json` / event 1 / `message`。

```text
similar_positions_in_department is the count of positions sharing the same organization_id and job_profile_id across the dataset.
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__position_overview.sql` / `text`。

```text
count(DISTINCT b.position_id) similar_positions_in_department
```

### similar_organization_only

**Unstated Choice**；非原因；把握中。

similar_positions按关系表中的organization_id分组，或先解析组织维度再分组；孤儿键是否保留未明确。保持distinct计数，只换组织来源诊断，不把gold选法当唯一规范。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用+新做；`records/042_checks/supplement_impl-016_workday__position_overview.json` / `similar_organization_only`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 4000 | 4000 | 11816 | 11844 |
| L1 | 4000 | 4000 | 11816 | 11844 |
| L2 | 4000 | 4000 | 11816 | 11844 |
| L3 | 4000 | 4000 | 11816 | 11844 |

L0减少：[0, -28]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml` / `text`。

```text
similar_positions_in_department is the count of positions sharing the same organization_id and job_profile_id across the dataset.
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json` / event 1 / `message`。

```text
similar_positions_in_department is the count of positions sharing the same organization_id and job_profile_id across the dataset.
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__position_overview.sql` / `text`。

```text
 SELECT po.organization_id,pr.job_profile_id,count(DISTINCT b.position_id) similar_positions_in_department FROM base b LEFT JOIN po ON b.position_id=po.position_id AND b.source_relation=po.source_relation AND po.rn=1 LEFT JOIN profiles pr ON b.position_id=pr.position_id AND b.source_relation=pr.source_relation GROUP BY po.organization_id,pr.job_profile_id
```

### organization_id

**Unstated Choice**；非原因；把握中。

最终organization_id保留关系表可用ID，或只认可匹配维度的ID；契约没有说明孤儿关系键应如何投影。单改到gold来源反而增加差异，记非原因，不用该试验推断违反契约。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-016_workday__position_overview.json` / `organization_id`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 4000 | 4000 | 11816 | 13732 |
| L1 | 4000 | 4000 | 11816 | 13732 |
| L2 | 4000 | 4000 | 11816 | 13732 |
| L3 | 4000 | 4000 | 11816 | 13732 |

L0减少：[0, -1916]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml` / `text`。

```text
- name: organization_id
        data_type: VARCHAR
        description: Organization identifier for the position; defaults to 'Unknown' when absent
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json` / event 1 / `message`。

```text
- name: organization_id
        data_type: VARCHAR
        description: Organization identifier for the position; defaults to 'Unknown' when absent
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__position_overview.sql` / `text`。

```text
coalesce(po.organization_id,'Unknown') organization_id
```

### 排除的旧控制/混合补丁

- `records/023_supplement_reruns_impl-016_workday__position_overview.json#similar_group`：同时改计数及组织来源，已拆成两个042单改；原混合补丁不参与排序。

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml`；SHA-256 `8f0707fc595c6f2f1e46a1983436959278e10315cb723e975c2811858d737c91`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__position_overview.sql`；SHA-256 `fc830506f229efeb49c2fedefbf1364067881b2b3975f9ab2c40da7c586b9d8c`。
- 023材料包：`records/023_packages/023_impl-016_workday__position_overview.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引6，组织和 NULL 连接。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
