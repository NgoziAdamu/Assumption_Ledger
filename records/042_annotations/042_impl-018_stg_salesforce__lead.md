# 042 正式标注：impl-018_stg_salesforce__lead

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**Unstated Choice**；把握高；13点。只能组合修复：否。023旧主要原因`A`仅存档。

## 详细发现

### 比较口径与原始数据

013未发现raw结构/类型/行数变化；这项检查不被扩张为所有格子内容的字节等同。staging用agent留存raw，marts用gold上游。

直接raw逐表013核对：`[{"table": "lead", "found_in_013": true, "different": false, "columns_types_equal": true, "row_counts_equal": true}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### null_empty_email_bounced_reason

**Unstated Choice**；参与；把握高。

email_bounced_reason没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__lead.json` / `null_empty_email_bounced_reason`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 19710 | 16779 |
| L1 | 3000 | 3000 | 18488 | 15557 |
| L2 | 3000 | 3000 | 18488 | 15557 |
| L3 | 3000 | 3000 | 18488 | 15557 |

L0减少：[0, 2931]（行、格）。

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

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql` / `text`。

```text
email_bounced_reason as email_bounced_reason
```

### null_empty_fax

**Unstated Choice**；参与；把握高。

fax没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__lead.json` / `null_empty_fax`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 19710 | 17007 |
| L1 | 3000 | 3000 | 18488 | 15785 |
| L2 | 3000 | 3000 | 18488 | 15785 |
| L3 | 3000 | 3000 | 18488 | 15785 |

L0减少：[0, 2703]（行、格）。

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

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql` / `text`。

```text
fax as fax
```

### null_empty_geocode_accuracy

**Unstated Choice**；参与；把握高。

geocode_accuracy没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__lead.json` / `null_empty_geocode_accuracy`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 19710 | 17607 |
| L1 | 3000 | 3000 | 18488 | 16385 |
| L2 | 3000 | 3000 | 18488 | 16385 |
| L3 | 3000 | 3000 | 18488 | 16385 |

L0减少：[0, 2103]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: geocode_accuracy
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: geocode_accuracy
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql` / `text`。

```text
geocode_accuracy as geocode_accuracy
```

### null_empty_industry

**Unstated Choice**；参与；把握高。

industry没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__lead.json` / `null_empty_industry`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 19710 | 18815 |
| L1 | 3000 | 3000 | 18488 | 17593 |
| L2 | 3000 | 3000 | 18488 | 17593 |
| L3 | 3000 | 3000 | 18488 | 17593 |

L0减少：[0, 895]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: industry
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: industry
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql` / `text`。

```text
industry as industry
```

### null_empty_master_record_id

**Unstated Choice**；主要；把握高。

master_record_id没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__lead.json` / `null_empty_master_record_id`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 19710 | 16714 |
| L1 | 3000 | 3000 | 18488 | 15492 |
| L2 | 3000 | 3000 | 18488 | 15492 |
| L3 | 3000 | 3000 | 18488 | 15492 |

L0减少：[0, 2996]（行、格）。

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

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql` / `text`。

```text
master_record_id as master_record_id
```

### null_empty_photo_url

**Unstated Choice**；参与；把握高。

photo_url没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__lead.json` / `null_empty_photo_url`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 19710 | 16863 |
| L1 | 3000 | 3000 | 18488 | 15641 |
| L2 | 3000 | 3000 | 18488 | 15641 |
| L3 | 3000 | 3000 | 18488 | 15641 |

L0减少：[0, 2847]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: photo_url
          data_type: VARCHAR
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: photo_url
          data_type: VARCHAR
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql` / `text`。

```text
photo_url as photo_url
```

### null_empty_salutation

**Unstated Choice**；参与；把握高。

salutation没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__lead.json` / `null_empty_salutation`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 19710 | 18240 |
| L1 | 3000 | 3000 | 18488 | 17018 |
| L2 | 3000 | 3000 | 18488 | 17018 |
| L3 | 3000 | 3000 | 18488 | 17018 |

L0减少：[0, 1470]（行、格）。

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

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql` / `text`。

```text
salutation as salutation
```

### null_empty_title

**Unstated Choice**；参与；把握高。

title没有非空/缺失默认值明文；agent保留NULL，gold补空字符串。空值与空字符串是不同单元格值，不是纯展示形式；两种缺失处理材料未定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__lead.json` / `null_empty_title`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 19710 | 19102 |
| L1 | 3000 | 3000 | 18488 | 17880 |
| L2 | 3000 | 3000 | 18488 | 17880 |
| L3 | 3000 | 3000 | 18488 | 17880 |

L0减少：[0, 608]（行、格）。

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

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql` / `text`。

```text
title as title
```

### status_filter

**其他**；参与；把握高。

契约非法status要求delete_row；agent删除4条，gold保留。解除过滤仅定位规范/参照不一致。

是否说出：第2档——交付物里只有通用说明。最终报告有适用于此类处理的通用说明，未逐表点名本处，记第2档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__lead.json` / `status_filter`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 19710 | 19565 |
| L1 | 3000 | 3000 | 18488 | 18342 |
| L2 | 3000 | 3000 | 18488 | 18342 |
| L3 | 3000 | 3000 | 18488 | 18342 |

L0减少：[0, 145]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: status
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "status IS NOT NULL"
              on_failure: delete_row
            - rule: "status IN ('Open - Not Contacted', 'Working - Contacted', 'Closed - Converted', 'Closed - Not Converted')"
              on_failure: delete_row
            - rule: "status = TRIM(status)"
              on_failure: correct
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: status
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "status IS NOT NULL"
              on_failure: delete_row
            - rule: "status IN ('Open - Not Contacted', 'Working - Contacted', 'Closed - Converted', 'Closed - Not Converted')"
              on_failure: delete_row
            - rule: "status = TRIM(status)"
              on_failure: correct
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json` / event 99 / `args.final_thought`。

```text
严重问题按契约删除行或过滤软删除数据；非关键字段中的无效关系键、格式值或数值按契约置空；规范化处理保留可用记录。
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql` / `text`。

```text
and trim(status) in ('Open - Not Contacted', 'Working - Contacted', 'Closed - Converted', 'Closed - Not Converted')
```

### status_value

**其他**；参与；把握高。

契约允许Open - Not Contacted；agent保留该合法枚举，gold变成Open。值不同不是agent误读规范。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__lead.json` / `status_value`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 19710 | 18222 |
| L1 | 3000 | 3000 | 18488 | 17000 |
| L2 | 3000 | 3000 | 18488 | 17000 |
| L3 | 3000 | 3000 | 18488 | 17000 |

L0减少：[0, 1488]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: status
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "status IS NOT NULL"
              on_failure: delete_row
            - rule: "status IN ('Open - Not Contacted', 'Working - Contacted', 'Closed - Converted', 'Closed - Not Converted')"
              on_failure: delete_row
            - rule: "status = TRIM(status)"
              on_failure: correct
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: status
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "status IS NOT NULL"
              on_failure: delete_row
            - rule: "status IN ('Open - Not Contacted', 'Working - Contacted', 'Closed - Converted', 'Closed - Not Converted')"
              on_failure: delete_row
            - rule: "status = TRIM(status)"
              on_failure: correct
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql` / `text`。

```text
trim(status) as status
```

### revenue_precision

**其他**；参与；把握高。

annual_revenue明定DECIMAL(18,3)，agent符合；goldDECIMAL(18,2)改变1222格。042仅改精度，不混入范围过滤；L1～L3精度差消除。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用+新做；`records/042_checks/supplement_impl-018_stg_salesforce__lead.json` / `revenue_precision`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 19710 | 18488 |
| L1 | 3000 | 3000 | 18488 | 18488 |
| L2 | 3000 | 3000 | 18488 | 18488 |
| L3 | 3000 | 3000 | 18488 | 18488 |

L0减少：[0, 1222]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: annual_revenue
          data_type: DECIMAL(18,3)
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: annual_revenue
          data_type: DECIMAL(18,3)
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql` / `text`。

```text
try_cast(annual_revenue as DECIMAL(18,3))
```

### revenue_range_only

**Unstated Choice**；非原因；把握高。

是否把负收入/极大收入业务值置空未写明；收入不天然等同非负计数硬约束。042保持DECIMAL(18,3)只改范围，收益0，不再把旧混合补丁的精度收益归范围处理。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用+新做；`records/042_checks/supplement_impl-018_stg_salesforce__lead.json` / `revenue_range_only`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 19710 | 19710 |
| L1 | 3000 | 3000 | 18488 | 18488 |
| L2 | 3000 | 3000 | 18488 | 18488 |
| L3 | 3000 | 3000 | 18488 | 18488 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: annual_revenue
          data_type: DECIMAL(18,3)
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: annual_revenue
          data_type: DECIMAL(18,3)
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql` / `text`。

```text
try_cast(annual_revenue as DECIMAL(18,3))
```

### converted_date

**Unstated Choice**；参与；把握高。

契约给DATE类型但未给该列的1900至current_date+1年边界；agent仅转换，gold额外置空边界外日期。日期范围属未规定业务选择。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-018_stg_salesforce__lead.json` / `converted_date`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 3000 | 3000 | 19710 | 19435 |
| L1 | 3000 | 3000 | 18488 | 18213 |
| L2 | 3000 | 3000 | 18488 | 18213 |
| L3 | 3000 | 3000 | 18488 | 18213 |

L0减少：[0, 275]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml` / `text`。

```text
- name: converted_date
          data_type: TIMESTAMP
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json` / event 1 / `message`。

```text
- name: converted_date
          data_type: TIMESTAMP
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql` / `text`。

```text
try_cast(converted_date as TIMESTAMP)
```

### 排除的旧控制/混合补丁

- `records/023_reruns_impl-018_stg_salesforce__lead.json#revenue_range`：旧补丁同时变精度与范围，已拆开，不能把精度收益算范围收益。

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql`；SHA-256 `0c27be47fffe6caeea74f98483c946b23932f44c10ebaa44a8ba2c311e877885`。
- 023材料包：`records/023_packages/023_impl-018_stg_salesforce__lead.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引20，status 与缺失字段。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
