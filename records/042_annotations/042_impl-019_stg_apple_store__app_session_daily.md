# 042 正式标注：impl-019_stg_apple_store__app_session_daily

## 任务

按冻结v3.2第3～8节逐点重标；层：staging。

## 结论

主要原因：**其他**；把握高；5点。只能组合修复：否。023旧主要原因`O`仅存档。

## 详细发现

### 比较口径与原始数据

原始session相关变化在gold raw同样存在；按015结论及本次要求照常标注，staging仍使用agent留存raw。benchmark加载原因仅记为推测；两个marts按CS取gold上游。

直接raw逐表013核对：`[{"table": "app_session_standard_daily", "found_in_013": true, "different": true, "columns_types_equal": false, "row_counts_equal": true}]`。

重跑输入：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/apple_store.duckdb`；staging取agent留存raw，非staging取gold上游，最终仍比较本表。固定时间：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-24 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-24'", "count": 1}]`。

先排除代码想法/实现冲突、规范参照不一致和raw版本问题；改变取值/记录的点不判纯Form。候选列占位和无候选默认分开；契约明文算法优先判Intent，不用gold实现补契约。以下按独立单改L0先行减量、再格减量排序，不相加、不用组合收益回分单点。



### semver_regex

**其他**；主要；把握高。

契约明确用数值三段版本或纯数字的正则判定合法性；agent正常正则可解析，gold多重反斜杠匹配失败。这里有明文算法，归其他；不是把gold失败当作真实格式不可解析。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-019_stg_apple_store__app_session_daily.json` / `semver_regex`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 3 | 68 | 24 |
| L1 | 7 | 3 | 68 | 24 |
| L2 | 7 | 3 | 68 | 24 |
| L3 | 7 | 3 | 68 | 24 |

L0减少：[4, 44]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
- name: app_version
          data_type: VARCHAR
          validation_rules:
            - rule: "(app_version RLIKE '^[0-9]+\\.[0-9]+\\.[0-9]+$' OR app_version RLIKE '^[0-9]+$') AND NOT (app_version RLIKE '[A-Za-z]')"
              on_failure: nullify_field
            - rule: "NOT (app_version RLIKE '[A-Za-z]')"
              on_failure: delete_row
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
- name: app_version
          data_type: VARCHAR
          validation_rules:
            - rule: "(app_version RLIKE '^[0-9]+\\.[0-9]+\\.[0-9]+$' OR app_version RLIKE '^[0-9]+$') AND NOT (app_version RLIKE '[A-Za-z]')"
              on_failure: nullify_field
            - rule: "NOT (app_version RLIKE '[A-Za-z]')"
              on_failure: delete_row
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/staging/stg_apple_store__app_session_daily.sql` / `text`。

```text
CASE WHEN r.app_version IS NULL THEN NULL WHEN regexp_matches(trim(cast(r.app_version AS VARCHAR)), '^[0-9]+(\.[0-9]+\.[0-9]+|)$') THEN trim(cast(r.app_version AS VARCHAR)) ELSE NULL END AS app_version
```

### date_filter_null

**已说出的选择**；参与；把握高。

契约给日期有效性和上下界，但未指定字符串解析器；TRY_CAST与多格式try_strptime对1条边界源文本结果不同。未证明agent在可确定格式上大面积失败，属材料未定解析选择；三个过滤位置分别单改。

是否说出：第1档——交付物里针对本处说明了。“会话 staging”一一对应app_session_daily，点明TRY_CAST及日期过滤，覆盖三个解析过滤点；不推广至其他feed或版本号规则。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-019_stg_apple_store__app_session_daily.json` / `date_filter_null`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 6 | 68 | 66 |
| L1 | 7 | 6 | 68 | 66 |
| L2 | 7 | 6 | 68 | 66 |
| L3 | 7 | 6 | 68 | 66 |

L0减少：[1, 2]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
- name: date_day
          data_type: DATE
          constraints: [not_null]
          validation_rules:
            - rule: "date_day IS NOT NULL AND date_day <= CURRENT_DATE AND date_day >= '2020-01-01'"
              on_failure: delete_row
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
- name: date_day
          data_type: DATE
          constraints: [not_null]
          validation_rules:
            - rule: "date_day IS NOT NULL AND date_day <= CURRENT_DATE AND date_day >= '2020-01-01'"
              on_failure: delete_row
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/63.json` / event 63 / `args.final_thought`。

```text
会话来源原始日期/下载日期字段以字符串形式提供；使用 `TRY_CAST` 转为日期。会话 staging 按契约过滤无效、未来及 2020-01-01 以前日期
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/staging/stg_apple_store__app_session_daily.sql` / `text`。

```text
WHERE try_cast(r.date AS DATE) IS NOT NULL
```

### date_filter_upper

**已说出的选择**；参与；把握高。

契约给日期有效性和上下界，但未指定字符串解析器；TRY_CAST与多格式try_strptime对1条边界源文本结果不同。未证明agent在可确定格式上大面积失败，属材料未定解析选择；三个过滤位置分别单改。

是否说出：第1档——交付物里针对本处说明了。“会话 staging”一一对应app_session_daily，点明TRY_CAST及日期过滤，覆盖三个解析过滤点；不推广至其他feed或版本号规则。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-019_stg_apple_store__app_session_daily.json` / `date_filter_upper`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 6 | 68 | 66 |
| L1 | 7 | 6 | 68 | 66 |
| L2 | 7 | 6 | 68 | 66 |
| L3 | 7 | 6 | 68 | 66 |

L0减少：[1, 2]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
- name: date_day
          data_type: DATE
          constraints: [not_null]
          validation_rules:
            - rule: "date_day IS NOT NULL AND date_day <= CURRENT_DATE AND date_day >= '2020-01-01'"
              on_failure: delete_row
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
- name: date_day
          data_type: DATE
          constraints: [not_null]
          validation_rules:
            - rule: "date_day IS NOT NULL AND date_day <= CURRENT_DATE AND date_day >= '2020-01-01'"
              on_failure: delete_row
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/63.json` / event 63 / `args.final_thought`。

```text
会话来源原始日期/下载日期字段以字符串形式提供；使用 `TRY_CAST` 转为日期。会话 staging 按契约过滤无效、未来及 2020-01-01 以前日期
```

### date_filter_lower

**已说出的选择**；参与；把握高。

契约给日期有效性和上下界，但未指定字符串解析器；TRY_CAST与多格式try_strptime对1条边界源文本结果不同。未证明agent在可确定格式上大面积失败，属材料未定解析选择；三个过滤位置分别单改。

是否说出：第1档——交付物里针对本处说明了。“会话 staging”一一对应app_session_daily，点明TRY_CAST及日期过滤，覆盖三个解析过滤点；不推广至其他feed或版本号规则。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。非探索类别不填。 系统提示是否适用：不适用。

证据：复用；`records/023_supplement_reruns_impl-019_stg_apple_store__app_session_daily.json` / `date_filter_lower`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 6 | 68 | 66 |
| L1 | 7 | 6 | 68 | 66 |
| L2 | 7 | 6 | 68 | 66 |
| L3 | 7 | 6 | 68 | 66 |

L0减少：[1, 2]（行、格）。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
- name: date_day
          data_type: DATE
          constraints: [not_null]
          validation_rules:
            - rule: "date_day IS NOT NULL AND date_day <= CURRENT_DATE AND date_day >= '2020-01-01'"
              on_failure: delete_row
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
- name: date_day
          data_type: DATE
          constraints: [not_null]
          validation_rules:
            - rule: "date_day IS NOT NULL AND date_day <= CURRENT_DATE AND date_day >= '2020-01-01'"
              on_failure: delete_row
```

原句（delivery）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/63.json` / event 63 / `args.final_thought`。

```text
会话来源原始日期/下载日期字段以字符串形式提供；使用 `TRY_CAST` 转为日期。会话 staging 按契约过滤无效、未来及 2020-01-01 以前日期
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/staging/stg_apple_store__app_session_daily.sql` / `text`。

```text
AND try_cast(r.date AS DATE) >= DATE '2020-01-01'
```

### null_version_filter

**Intent Misreading**；非原因；把握中。

契约提供NOT regexp_matches原app_version字面的可执行过滤；agentCOALESCE(NULL,空串)后检查，会把原NULL的UNKNOWN变为通过。去掉COALESCE单改无收益，记非原因。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event1完整契约包含相关列/规则；已查finish、留存result及最终SQL（无注释），未找到本处的具体或通用解释。轨迹未见点出本处疑问或比较不同读法的证据，不能只因写出做法而记第3档。

证据在场：是。event1原始提示含完整相关契约，逐句匹配成功。

曾经理解对过：否。按本点列名、条件及源表回查轨迹，未找到该表本点已正确实现的直接证据；邻表修改不算本表曾理解正确。 系统提示是否适用：不适用。

证据：复用；`records/023_reruns_impl-019_stg_apple_store__app_session_daily.json` / `null_version_filter`。指定一处替换后按原链重算（Other的对齐gold替换仅用于诊断）。

| 口径 | 基线行 | 修改/诊断后行 | 基线格 | 修改/诊断后格 |
|---|---:|---:|---:|---:|
| L0 | 7 | 7 | 68 | 68 |
| L1 | 7 | 7 | 68 | 68 |
| L2 | 7 | 7 | 68 | 68 |
| L3 | 7 | 7 | 68 | 68 |

L0减少：[0, 0]（行、格）。

本点单改未减少判错规模，不计参与因素；有未确立前提时保留非原因标记。对Other仅记录规范参照差异控制，不声称存在错误的数据前提。

原句（contract）：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml` / `text`。

```text
app_version
```

原句（contract_presence）：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-019/agent/.events/sessions/930347a5-330f-4c-6d04eb40e4a9b41/events/1.json` / event 1 / `message`。

```text
app_version
```

原句（delivered_sql_expression）：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/staging/stg_apple_store__app_session_daily.sql` / `text`。

```text
coalesce(cast(r.app_version AS VARCHAR), '')
```

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-019/docs/data_contract.yaml`；SHA-256 `0546320393fa39035bd8afc85a91a28a2aedccc8bcd9f41662f8fb862b7f5be2`。
- 最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-019/agent/dacomp-de-impl-019/sql/staging/stg_apple_store__app_session_daily.sql`；SHA-256 `75d005836cef1cd433a64c33eff3de8f34e3c0b50a37d84b624d0b6cddb1bafc`。
- 023材料包：`records/023_packages/023_impl-019_stg_apple_store__app_session_daily.md`；数据诊断、查询及轨迹引用按`records/042_checks/evidence_catalog.json`复用。
- 引句逐一回查：`records/042_checks/quote_checks.json`；披露审计：`records/042_checks/disclosure_audit.json`。
- raw证据：对应`records/013_raw_impl-NNN.json`、`records/015_raw_impl-NNN.json`及`records/042_checks/raw_integrity_review.json`。
- 核实预算（含复用/失败的保守上限）：1条；诊断不计5条上限。
- 查询：`records/023_queries.json` 数组索引27，NULL 版本与字母。

## 不确定或没查到的（含规则问题）

没有新增规则覆盖缺口；单改非原因不能证明组合后也无影响。引用精确匹配不替代语义判断。

## 建议的下一步

交用户与Claude复核本批；本任务不修改手册，不扩展其他批次。
