# 042 正式标注：impl-018_stg_salesforce__contact

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**Unstated Choice**；把握高；14点。只能组合修复：否。023旧主要原因`A`仅存档。

## 详细发现

### 比较口径与原始数据

013未发现raw结构/类型/行数变化；这项检查不被扩张为所有格子内容的字节等同。staging用agent留存raw，marts用gold上游。

直接raw逐表013核对：`[{"table": "account", "found_in_013": true, "different": false, "columns_types_equal": true, "row_counts_equal": true}, {"table": "contact", "found_in_013": true, "different": false, "columns_types_equal": true, "row_counts_equal": true}, {"table": "user", "found_in_013": true, "different": false, "columns_types_equal": true, "row_counts_equal": true}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-24 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-24'", "count": 1}]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### null_empty_assistant_name

**Unstated Choice**；参与；把握高。

assistant_name没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_assistant_name`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 27523 |
| L1 | 3000 | 3000 | 30190 | 27523 |
| L2 | 3000 | 3000 | 30190 | 27523 |
| L3 | 3000 | 3000 | 30190 | 27523 |

L0减少：[0, 2667]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: assistant_name
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: assistant_name
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
assistant_name as assistant_name
```

### null_empty_department

**Unstated Choice**；参与；把握高。

department没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_department`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 28980 |
| L1 | 3000 | 3000 | 30190 | 28980 |
| L2 | 3000 | 3000 | 30190 | 28980 |
| L3 | 3000 | 3000 | 30190 | 28980 |

L0减少：[0, 1210]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: department
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: department
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
department as department
```

### null_empty_email_bounced_reason

**Unstated Choice**；参与；把握高。

email_bounced_reason没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_email_bounced_reason`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 27235 |
| L1 | 3000 | 3000 | 30190 | 27235 |
| L2 | 3000 | 3000 | 30190 | 27235 |
| L3 | 3000 | 3000 | 30190 | 27235 |

L0减少：[0, 2955]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: email_bounced_reason
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: email_bounced_reason
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
email_bounced_reason as email_bounced_reason
```

### null_empty_fax

**Unstated Choice**；参与；把握高。

fax没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_fax`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 27336 |
| L1 | 3000 | 3000 | 30190 | 27336 |
| L2 | 3000 | 3000 | 30190 | 27336 |
| L3 | 3000 | 3000 | 30190 | 27336 |

L0减少：[0, 2854]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: fax
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: fax
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
fax as fax
```

### null_empty_lead_source

**Unstated Choice**；参与；把握高。

lead_source没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_lead_source`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 29284 |
| L1 | 3000 | 3000 | 30190 | 29284 |
| L2 | 3000 | 3000 | 30190 | 29284 |
| L3 | 3000 | 3000 | 30190 | 29284 |

L0减少：[0, 906]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: lead_source
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: lead_source
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
lead_source as lead_source
```

### null_empty_master_record_id

**Unstated Choice**；主要；把握高。

master_record_id没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_master_record_id`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 27190 |
| L1 | 3000 | 3000 | 30190 | 27190 |
| L2 | 3000 | 3000 | 30190 | 27190 |
| L3 | 3000 | 3000 | 30190 | 27190 |

L0减少：[0, 3000]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: master_record_id
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: master_record_id
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
master_record_id as master_record_id
```

### null_empty_other_city

**Unstated Choice**；参与；把握高。

other_city没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_other_city`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 27783 |
| L1 | 3000 | 3000 | 30190 | 27783 |
| L2 | 3000 | 3000 | 30190 | 27783 |
| L3 | 3000 | 3000 | 30190 | 27783 |

L0减少：[0, 2407]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: other_city
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: other_city
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
other_city as other_city
```

### null_empty_other_country

**Unstated Choice**；参与；把握高。

other_country没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_other_country`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 27801 |
| L1 | 3000 | 3000 | 30190 | 27801 |
| L2 | 3000 | 3000 | 30190 | 27801 |
| L3 | 3000 | 3000 | 30190 | 27801 |

L0减少：[0, 2389]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: other_country
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: other_country
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
other_country as other_country
```

### null_empty_other_postal_code

**Unstated Choice**；参与；把握高。

other_postal_code没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_other_postal_code`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 27781 |
| L1 | 3000 | 3000 | 30190 | 27781 |
| L2 | 3000 | 3000 | 30190 | 27781 |
| L3 | 3000 | 3000 | 30190 | 27781 |

L0减少：[0, 2409]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: other_postal_code
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: other_postal_code
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
other_postal_code as other_postal_code
```

### null_empty_other_state

**Unstated Choice**；参与；把握高。

other_state没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_other_state`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 27760 |
| L1 | 3000 | 3000 | 30190 | 27760 |
| L2 | 3000 | 3000 | 30190 | 27760 |
| L3 | 3000 | 3000 | 30190 | 27760 |

L0减少：[0, 2430]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: other_state
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: other_state
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
other_state as other_state
```

### null_empty_other_street

**Unstated Choice**；参与；把握高。

other_street没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_other_street`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 27769 |
| L1 | 3000 | 3000 | 30190 | 27769 |
| L2 | 3000 | 3000 | 30190 | 27769 |
| L3 | 3000 | 3000 | 30190 | 27769 |

L0减少：[0, 2421]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: other_street
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: other_street
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
other_street as other_street
```

### null_empty_photo_url

**Unstated Choice**；参与；把握高。

photo_url没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_photo_url`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 27477 |
| L1 | 3000 | 3000 | 30190 | 27477 |
| L2 | 3000 | 3000 | 30190 | 27477 |
| L3 | 3000 | 3000 | 30190 | 27477 |

L0减少：[0, 2713]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: photo_url
          data_type: VARCHAR
          validation_rules:
            - rule: "photo_url IS NULL OR LENGTH(photo_url) <= 500"
              on_failure: nullify_field
            - rule: "photo_url IS NULL OR photo_url = TRIM(photo_url)"
              on_failure: correct
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: photo_url
          data_type: VARCHAR
          validation_rules:
            - rule: "photo_url IS NULL OR LENGTH(photo_url) <= 500"
              on_failure: nullify_field
            - rule: "photo_url IS NULL OR photo_url = TRIM(photo_url)"
              on_failure: correct
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
case when photo_url is null or length(trim(photo_url)) <= 500 then trim(photo_url) end as photo_url
```

### null_empty_salutation

**Unstated Choice**；参与；把握高。

salutation没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_salutation`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 28940 |
| L1 | 3000 | 3000 | 30190 | 28940 |
| L2 | 3000 | 3000 | 30190 | 28940 |
| L3 | 3000 | 3000 | 30190 | 28940 |

L0减少：[0, 1250]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: salutation
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: salutation
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
salutation as salutation
```

### null_empty_title

**Unstated Choice**；参与；把握高。

title没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__contact.json` / `null_empty_title`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 30190 | 29611 |
| L1 | 3000 | 3000 | 30190 | 29611 |
| L2 | 3000 | 3000 | 30190 | 29611 |
| L3 | 3000 | 3000 | 30190 | 29611 |

L0减少：[0, 579]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: title
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: title
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql` / `text`。

```text
title as title
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact.sql`；SHA-256 `8976caf476c66d76c48755f33237c4aa1504a5359decca61fc8955c9807e96ce`。
- 023材料包：`records/023_packages/023_impl-018_stg_salesforce__contact.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引18，非必填字段 NULL。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
