# 042 正式标注：impl-021_stg_klaviyo__person

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**Unstated Choice**；把握高；3点。只能组合修复：否。023旧主要原因`A`仅存档。

## 详细发现

### 比较口径与原始数据

五张raw均有013/015记录的变化，gold raw也包含变化；按指定口径用agent留存raw标五张staging，intermediate用gold上游。ID稀疏是实际可见事实，其形成原因未查证，不能从稀疏反推agent删raw。

直接raw逐表013核对：`[{"table": "person", "found_in_013": true, "different": true, "columns_types_equal": false, "row_counts_equal": false}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### null_id_filter

**Unstated Choice**；主要；把握高。

person_id没有not_null约束，agent将其他实体通用ID非空过滤扩展到person；按源缺失person是否保留，契约未定。解除后仅剩1格差异，此过滤为主要原因；不把campaign等三表的约束推广到person。

是否说出：第2档——交付物里只有通用说明。最终报告有适用于此类处理的通用说明，未逐表点名本处，记第2档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-021_stg_klaviyo__person.json` / `null_id_filter`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 1190 | 1 | 19040 | 1 |
| L1 | 1190 | 1 | 19040 | 1 |
| L2 | 1190 | 1 | 19040 | 1 |
| L3 | 1190 | 1 | 19040 | 1 |

L0减少：[1189, 19039]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml` / `text`。

```text
- name: person_id
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/1.json` / event 1 / `message`。

```text
- name: person_id
          data_type: VARCHAR
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/41.json` / event 41 / `args.final_thought`。

```text
无效关键 ID 和非法邮件记录被排除
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/staging/stg_klaviyo__person.sql` / `text`。

```text
nullif(trim(cast(id as varchar)), '') is not null
```

### full_name_null

**Unstated Choice**；非原因；把握中。

契约描述first/last拼接、两者都缺失可NULL，未给单边缺失的可执行拼接规则；concat_ws保留单侧姓名与NULL传播拼接是不同读法。单改被ID过滤遮蔽，未减少规模，记非原因。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-021_stg_klaviyo__person.json` / `full_name_null`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 1190 | 1190 | 19040 | 19040 |
| L1 | 1190 | 1190 | 19040 | 19040 |
| L2 | 1190 | 1190 | 19040 | 19040 |
| L3 | 1190 | 1190 | 19040 | 19040 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml` / `text`。

```text
- name: full_name
          data_type: VARCHAR
          description: Concatenation of first_name and last_name; may be NULL if both are missing
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/1.json` / event 1 / `message`。

```text
- name: full_name
          data_type: VARCHAR
          description: Concatenation of first_name and last_name; may be NULL if both are missing
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/staging/stg_klaviyo__person.sql` / `text`。

```text
nullif(trim(concat_ws(' ', nullif(trim(cast(first_name as varchar)), ''), nullif(trim(cast(last_name as varchar)), ''))), '') full_name
```

### phone_normalization

**其他**；非原因；把握高。

契约明确去非数字并加+，agent符合；gold额外去前导0且替换范围不同。单改无收益，是规范参照不同的非原因控制，不算参与。

是否说出：第1档——交付物里针对本处说明了。本题只有person staging输出phone_number，电话号码功能一一对应；该句点明加+而不推断国家码。类别Other不因第1档改名。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-021_stg_klaviyo__person.json` / `phone_normalization`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 1190 | 1190 | 19040 | 19040 |
| L1 | 1190 | 1190 | 19040 | 19040 |
| L2 | 1190 | 1190 | 19040 | 19040 |
| L3 | 1190 | 1190 | 19040 | 19040 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml` / `text`。

```text
- name: phone_number
          data_type: VARCHAR
          validation_rules:
            - rule: "phone_number is NULL or normalized by removing non-digits and prefixing with '+' (E.164-like)"
              on_failure: correct
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/1.json` / event 1 / `message`。

```text
- name: phone_number
          data_type: VARCHAR
          validation_rules:
            - rule: "phone_number is NULL or normalized by removing non-digits and prefixing with '+' (E.164-like)"
              on_failure: correct
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/41.json` / event 41 / `args.final_thought`。

```text
电话号码按 E.164-like 格式加前缀 `+`，未推断国家码。
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/staging/stg_klaviyo__person.sql` / `text`。

```text
case when phone_digits='' then null else '+' || phone_digits end
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml`；SHA-256 `db04fb84955b6385dd63b72bdf7aae27ac9f612a685f938eabf7051f12cd675f`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/staging/stg_klaviyo__person.sql`；SHA-256 `c1c19d10e6d80bd7fe487cd7564f89908c00ee7f951133962e90cb7950dfebf6`。
- 023材料包：`records/023_packages/023_impl-021_stg_klaviyo__person.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引38，ID 空值。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
