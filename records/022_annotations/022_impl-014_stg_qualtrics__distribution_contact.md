# impl-014 / stg_qualtrics__distribution_contact（全量；v2）

## 1. 差异与结论

复合主键去重4行，撤QUALIFY全表L0一致，O。

主要原因：**O**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| preserve_duplicates | O | 4 | 32 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-014_stg_qualtrics__distribution_contact.md](../../records/022_packages/022_impl-014_stg_qualtrics__distribution_contact.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-014_stg_qualtrics__distribution_contact/022_impl-014_stg_qualtrics__distribution_contact.json`。
- 比较结果：[022_reruns_impl-014_stg_qualtrics__distribution_contact.json](../022_reruns_impl-014_stg_qualtrics__distribution_contact.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`。

原件第352–383行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__distribution_contact.sql`；原件第1–30行。

```sql
   1: WITH source_rows AS (
   2:     SELECT
   3:         try_cast(src."contact_frequency_rule_id" AS VARCHAR) AS contact_frequency_rule_id,
   4:         try_cast(src."contact_id" AS VARCHAR) AS contact_id,
   5:         try_cast(src."contact_lookup_id" AS VARCHAR) AS contact_lookup_id,
   6:         try_cast(src."distribution_id" AS VARCHAR) AS distribution_id,
   7:         try_cast(src."opened_at" AS VARCHAR) AS opened_at,
   8:         try_cast(src."response_completed_at" AS VARCHAR) AS response_completed_at,
   9:         try_cast(src."response_id" AS VARCHAR) AS response_id,
  10:         try_cast(src."response_started_at" AS VARCHAR) AS response_started_at,
  11:         try_cast(src."sent_at" AS VARCHAR) AS sent_at,
  12:         try_cast(src."status" AS VARCHAR) AS status,
  13:         try_cast(src."survey_link" AS VARCHAR) AS survey_link,
  14:         try_cast(src."survey_session_id" AS VARCHAR) AS survey_session_id
  15:     FROM raw.distribution_contact AS src
  16: ),
  17: validated_rows AS (
  18:     SELECT *
  19:     FROM source_rows
  20:     WHERE 1 = 1
  21:       AND distribution_id IS NOT NULL
  22:       AND contact_id IS NOT NULL
  23: ),
  24: deduplicated_rows AS (
  25:     SELECT *
  26:     FROM validated_rows
  27:     QUALIFY row_number() OVER (PARTITION BY distribution_id, contact_id ORDER BY distribution_id, contact_id) = 1
  28: )
  29: SELECT *
  30: FROM deduplicated_rows
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__distribution_contact.sql`；原件第1–39行。

```sql
   1: -- DuckDB-compatible staging model for distribution_contact table
   2: -- Converted from dbt stg_qualtrics__distribution_contact.sql
   3: -- Implements validation rules and data quality transformations per staging_data_specification.yaml
   4: 
   5: with validated_distribution_contact_data as (
   6:     select
   7:         trim(contact_frequency_rule_id) as contact_frequency_rule_id,
   8:         trim(contact_id) as contact_id,
   9:         trim(contact_lookup_id) as contact_lookup_id,
  10:         trim(distribution_id) as distribution_id,
  11:         try_cast(opened_at as timestamp) as opened_at,
  12:         try_cast(response_completed_at as timestamp) as response_completed_at,
  13:         trim(response_id) as response_id,
  14:         try_cast(response_started_at as timestamp) as response_started_at,
  15:         try_cast(sent_at as timestamp) as sent_at,
  16:         trim(status) as status,
  17:         trim(survey_link) as survey_link,
  18:         trim(survey_session_id) as survey_session_id
  19:     from raw.distribution_contact
  20:     where distribution_id is not null
  21:       and contact_id is not null  -- Composite primary key validation
  22: )
  23: 
  24: select
  25:     contact_frequency_rule_id,
  26:     contact_id,
  27:     contact_lookup_id,
  28:     distribution_id,
  29:     opened_at,
  30:     response_completed_at,
  31:     response_id,
  32:     response_started_at,
  33:     sent_at,
  34:     status,
  35:     survey_link,
  36:     survey_session_id
  37: from validated_distribution_contact_data
  38: where distribution_id is not null
  39:   and contact_id is not null
```

## 3. agent看到的材料与不确定性

已检视该题全部81个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 79 / finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/79.json`。

四档：**只有通用策略说明**。

原句（见上述最终报告事件）：

```text
重复主键记录按主键仅保留一条；合同未指定冲突记录排序规则，因此非主键字段冲突时，具体保留行不保证业务优先级，可能丢失冲突值。
```

## 4. 核实查询与诊断

核实查询共**4条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.distribution_contact' source_table,count(*) rows FROM raw.distribution_contact
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.distribution_contact' source_table,count(*) rows FROM raw.distribution_contact\n                                                                ^"}
```

### 核实 V2：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "distribution_id","contact_id",count(*) n FROM raw.distribution_contact GROUP BY "distribution_id","contact_id")
```

```json
{"error": "Parser Error: syntax error at or near \"groups\"\n\nLINE 1: SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n...\n                        ^"}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.distribution_contact' source_table,count(*) source_rows FROM raw.distribution_contact
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.distribution_contact", 6000]]}
```

### 核实 V4：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) key_groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "distribution_id","contact_id",count(*) n FROM raw.distribution_contact GROUP BY "distribution_id","contact_id")
```

```json
{"columns": ["key_groups", "duplicate_groups", "excess"], "result": [[5996, 4, 4]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["distribution_id", "contact_id"]`；比较列：`["contact_frequency_rule_id", "contact_id", "contact_lookup_id", "distribution_id", "response_id", "status", "survey_link", "survey_session_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 5996/6000 | 0/0 | 0/4 | 0 | 4 | 32 | False |
| L1 | 5996/6000 | 0/0 | 0/4 | 0 | 4 | 32 | False |
| L2 | 5996/6000 | 0/0 | 0/4 | 0 | 4 | 32 | False |
| L3 | 5996/6000 | 0/0 | 0/4 | 0 | 4 | 32 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| distribution_id | 0 | 0 | 0 | 0 |
| contact_id | 0 | 0 | 0 | 0 |
| contact_frequency_rule_id | 0 | 0 | 0 | 0 |
| contact_lookup_id | 0 | 0 | 0 | 0 |
| response_id | 0 | 0 | 0 | 0 |
| status | 0 | 0 | 0 | 0 |
| survey_link | 0 | 0 | 0 | 0 |
| survey_session_id | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-014_stg_qualtrics__distribution_contact/baseline.sql`；SHA-256：`6102295159ae01b8fb73734f2a1a43e99e290cd835907d162e2cef300ccfeea8`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 5996/6000 | 0/0 | 0/4 | 0 | 4 | 32 | False |
| L1 | 5996/6000 | 0/0 | 0/4 | 0 | 4 | 32 | False |
| L2 | 5996/6000 | 0/0 | 0/4 | 0 | 4 | 32 | False |
| L3 | 5996/6000 | 0/0 | 0/4 | 0 | 4 | 32 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| distribution_id | 0 | 0 | 0 | 0 |
| contact_id | 0 | 0 | 0 | 0 |
| contact_frequency_rule_id | 0 | 0 | 0 | 0 |
| contact_lookup_id | 0 | 0 | 0 | 0 |
| response_id | 0 | 0 | 0 | 0 |
| status | 0 | 0 | 0 | 0 |
| survey_link | 0 | 0 | 0 | 0 |
| survey_session_id | 0 | 0 | 0 | 0 |

### preserve_duplicates

SQL：`data/022_work/impl-014_stg_qualtrics__distribution_contact/preserve_duplicates.sql`；SHA-256：`6c12752a3dac2f9ab275e5fc08c8fcd25beafea7aae4a8fa83c5e1629a2c3ac0`。

替换offset=1108，原表达式所在行约27（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
    QUALIFY row_number() OVER (PARTITION BY distribution_id, contact_id ORDER BY distribution_id, contact_id) = 1
-- 新

```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 6000/6000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 6000/6000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 6000/6000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 6000/6000 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| distribution_id | 0 | 0 | 0 | 0 |
| contact_id | 0 | 0 | 0 | 0 |
| contact_frequency_rule_id | 0 | 0 | 0 | 0 |
| contact_lookup_id | 0 | 0 | 0 | 0 |
| response_id | 0 | 0 | 0 | 0 |
| status | 0 | 0 | 0 | 0 |
| survey_link | 0 | 0 | 0 | 0 |
| survey_session_id | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：preserve_duplicates；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- preserve_duplicates：O；主项。契约primary_key/unique；gold未去重。（行减少4，格减少32）

## 规则问题

无。按v2冻结定义执行。
