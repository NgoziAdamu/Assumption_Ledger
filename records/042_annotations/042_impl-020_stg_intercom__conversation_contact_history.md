# 042 正式标注：impl-020_stg_intercom__conversation_contact_history

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**其他**；把握高；2点。只能组合修复：是。023旧主要原因`O`仅存档。

## 详细发现

### 比较口径与原始数据

原始数据变化在gold raw同样存在，包含本批两张staging直接源。按指定口径用agent留存raw并照常标注，列错位据此核查；benchmark加载原因是015推测，不归为agent自己改raw。

直接raw逐表013核对：`[{"table": "conversation_contact_history_data", "found_in_013": true, "different": true, "columns_types_equal": false, "row_counts_equal": true}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/intercom.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### contact_column

**其他**；并列；把握高。

原始字段错位：数值conversation ID在contact_id，contact文本ID在conversation_id；agent交付按含义交换，符合目标列含义及BIGINT要求。gold同名直取导致不符含义/类型。contact_id单独改到gold仍全行不匹配，二者组合才清零；不因此要求agent采纳错位。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event22看到了列与样例；event25同名映射、event35互换映射，但未找到比较本关系表两种映射结果或点出本处疑问的文字。不能仅凭前后改代码推定第3档，保守记第4档。finish只点名conversation part错位，不推广到conversation contact关系表。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-020_stg_intercom__conversation_contact_history.json` / `contact_column`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 8066 | 8066 | 16132 | 16132 |
| L1 | 8066 | 8066 | 16132 | 16132 |
| L2 | 8066 | 8066 | 16132 | 16132 |
| L3 | 8066 | 8066 | 16132 | 16132 |

L0减少：[0, 0]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml` / `text`。

```text
- name: contact_id
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/1.json` / event 1 / `message`。

```text
- name: contact_id
          data_type: VARCHAR
```

原句（alternative_reading）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/25.json` / event 25 / `args.command`。

```text
('conversation_contact_history','contact_id::varchar as contact_id, try_cast(conversation_id as bigint) as conversation_id')
```

原句（alternative_reading）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/35.json` / event 35 / `args.command`。

```text
try_cast(conversation_id as varchar) as contact_id,
    try_cast(contact_id as bigint) as conversation_id
```

原句（mapping_sample）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/22.json` / event 22 / `content`。

```text
('5ed93beb39021efc4ccd4ea5', '156643300000684'
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/staging/stg_intercom__conversation_contact_history.sql` / `text`。

```text
try_cast(conversation_id as varchar) as contact_id
```

### conversation_column

**其他**；并列；把握高。

原始字段错位：数值conversation ID在contact_id，contact文本ID在conversation_id；agent交付按含义交换，符合目标列含义及BIGINT要求。gold同名直取导致不符含义/类型。conversation_id单独改到gold仍全行不匹配，二者组合才清零；不因此要求agent采纳错位。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event22看到了列与样例；event25同名映射、event35互换映射，但未找到比较本关系表两种映射结果或点出本处疑问的文字。不能仅凭前后改代码推定第3档，保守记第4档。finish只点名conversation part错位，不推广到conversation contact关系表。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-020_stg_intercom__conversation_contact_history.json` / `conversation_column`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 8066 | 8066 | 16132 | 16132 |
| L1 | 8066 | 8066 | 16132 | 16132 |
| L2 | 8066 | 8066 | 16132 | 16132 |
| L3 | 8066 | 8066 | 16132 | 16132 |

L0减少：[0, 0]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml` / `text`。

```text
- name: conversation_id
          data_type: BIGINT
      row_filters:
        - rule: "coalesce(try_cast(_fivetran_active as BOOLEAN), true)"
          on_failure: delete_row
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/1.json` / event 1 / `message`。

```text
- name: conversation_id
          data_type: BIGINT
      row_filters:
        - rule: "coalesce(try_cast(_fivetran_active as BOOLEAN), true)"
          on_failure: delete_row
```

原句（alternative_reading）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/25.json` / event 25 / `args.command`。

```text
('conversation_contact_history','contact_id::varchar as contact_id, try_cast(conversation_id as bigint) as conversation_id')
```

原句（alternative_reading）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/35.json` / event 35 / `args.command`。

```text
try_cast(conversation_id as varchar) as contact_id,
    try_cast(contact_id as bigint) as conversation_id
```

原句（mapping_sample）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/22.json` / event 22 / `content`。

```text
('5ed93beb39021efc4ccd4ea5', '156643300000684'
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/staging/stg_intercom__conversation_contact_history.sql` / `text`。

```text
try_cast(contact_id as bigint) as conversation_id
```

### 组合诊断

两处各单改均减少0行0格；`records/042_checks/supplement_impl-020_stg_intercom__conversation_contact_history.json` / mapping_combination从8066行16132格到L0～L3全0。两点同为Other，单列只能组合修复，不虚报各自收益。

### 排除的旧控制/混合补丁

- `records/042_checks/supplement_impl-020_stg_intercom__conversation_contact_history.json#mapping_combination`：单列为组合诊断，非单点。

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml`；SHA-256 `b19cdce65b55dd44086f5a7ef864055abfe48bd66f5d6f430785084ab3cd5314`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/staging/stg_intercom__conversation_contact_history.sql`；SHA-256 `e92597ffc92f0690c4d37859cf0756bc316e15119344abe5d551f3e84d83a2b5`。
- 023材料包：`records/023_packages/023_impl-020_stg_intercom__conversation_contact_history.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引32，列值域与主表覆盖。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
