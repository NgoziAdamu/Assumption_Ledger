# 042 正式标注：impl-018_stg_salesforce__contact_history

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**Unstated Choice**；把握高；2点。只能组合修复：否。023旧主要原因`A`仅存档。

## 详细发现

### 比较口径与原始数据

013未发现raw结构/类型/行数变化；这项检查不被扩张为所有格子内容的字节等同。staging用agent留存raw，marts用gold上游。

直接raw逐表013核对：`[{"table": "contact_history", "found_in_013": true, "different": false, "columns_types_equal": true, "row_counts_equal": true}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### history_key_clock

**Unstated Choice**；主要；把握高。

契约只有history_unique_key非空唯一，没有生成算法；agent用实体ID与Fivetran版本边界MD5，gold用ID与运行时刻拼接。固定同一时刻的单改减少4868行82756格；不使用把created_date误当运行时刻的旧history_key试验。

是否说出：第2档——交付物里只有通用说明。“History”涵盖account/contact/opportunity三张history，未一一对应contact_history；因此只记第2档。该句讲生成键和精确重复，不覆盖仅按实体id删不同版本。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用+新做；`records/023_supplement_reruns_impl-018_stg_salesforce__contact_history.json` / `history_key_clock`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 5434 | 566 | 92378 | 9622 |
| L1 | 5434 | 566 | 92378 | 9622 |
| L2 | 5434 | 566 | 92378 | 9622 |
| L3 | 5434 | 566 | 92378 | 9622 |

L0减少：[4868, 82756]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: history_unique_key
          data_type: VARCHAR
          constraints: [not_null, unique]
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: history_unique_key
          data_type: VARCHAR
          constraints: [not_null, unique]
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json` / event 99 / `args.final_thought`。

```text
History 源数据没有契约所需的 `history_unique_key` 原始列，因此以实体记录 ID 与 Fivetran 起止时间生成确定性 MD5 键，用于稳定标识历史版本。
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact_history.sql` / `text`。

```text
md5(concat_ws('|', coalesce(cast(contact_id as varchar), ''), coalesce(cast(_fivetran_start as varchar), ''), coalesce(cast(_fivetran_end as varchar), '')))
```

### unique_contact

**Data Misconception**；非原因；把握中。

P：raw.contact_history的id足以唯一标识一条历史版本。契约只约束history_unique_key，未要求contact_id唯一；042对agent raw核实3000行、2434个id、517个id有多个不同Fivetran版本，P不成立。按id QUALIFY删566行。去重单改被不同评测键遮蔽且反而增差，故非原因，不算参与因素。

P：raw.contact_history的id足以唯一标识一条历史版本。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：否。只看见相关字段/样例，未找到足以定下本点P的全量唯一性或覆盖核实出现在轨迹；不能用本次查询反填证据在场。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用+新做；`records/023_reruns_impl-018_stg_salesforce__contact_history.json` / `unique_contact`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 5434 | 6000 | 92378 | 102000 |
| L1 | 5434 | 6000 | 92378 | 102000 |
| L2 | 5434 | 6000 | 92378 | 102000 |
| L3 | 5434 | 6000 | 92378 | 102000 |

L0减少：[-566, -9622]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: contact_id
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: contact_id
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact_history.sql` / `text`。

```text
qualify row_number() over (partition by id order by id) = 1
```

### 排除的旧控制/混合补丁

- `records/023_reruns_impl-018_stg_salesforce__contact_history.json#history_key`：旧补丁使用created_date而不是gold运行时刻；用相同固定时刻history_key_clock替代。

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact_history.sql`；SHA-256 `597034deb4aba0ef9445d1d388b4aa580cf22751326201018619b95bcd002061`。
- 023材料包：`records/023_packages/023_impl-018_stg_salesforce__contact_history.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：3条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引19，gold 时间型键。
- 查询：`records/042_checks/new_verification_queries.json` 数组索引0，id与历史版本（同SQL执行2次，保守计2条）。

## 不确定或没查到的（含规则问题）

history实体ID去重不是契约唯一性要求；新查版本关系证明P错误。event77只去掉account_history去重，无明确组级疑问文字，不据此把contact_history提高到第3档或曾理解对过。其单改增差，故不算参与因素。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
