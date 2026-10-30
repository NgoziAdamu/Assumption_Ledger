# impl-014 / stg_qualtrics__question_option（全量；v2）

## 1. 差异与结论

question_id/key主键去重4494行，撤QUALIFY全表L0一致，O。

主要原因：**O**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| preserve_duplicates | O | 4494 | 22470 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-014_stg_qualtrics__question_option.md](../../records/022_packages/022_impl-014_stg_qualtrics__question_option.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-014_stg_qualtrics__question_option/022_impl-014_stg_qualtrics__question_option.json`。
- 比较结果：[022_reruns_impl-014_stg_qualtrics__question_option.json](../022_reruns_impl-014_stg_qualtrics__question_option.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`。

原件第614–631行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__question_option.sql`；原件第1–23行。

```sql
   1: WITH source_rows AS (
   2:     SELECT
   3:         try_cast(src."question_id" AS VARCHAR) AS question_id,
   4:         try_cast(src."survey_id" AS VARCHAR) AS survey_id,
   5:         try_cast(src."key" AS VARCHAR) AS key,
   6:         try_cast(src."recode_value" AS BIGINT) AS recode_value,
   7:         try_cast(src."text" AS VARCHAR) AS text
   8:     FROM raw.question_option AS src
   9: ),
  10: validated_rows AS (
  11:     SELECT *
  12:     FROM source_rows
  13:     WHERE 1 = 1
  14:       AND question_id IS NOT NULL
  15:       AND key IS NOT NULL
  16: ),
  17: deduplicated_rows AS (
  18:     SELECT *
  19:     FROM validated_rows
  20:     QUALIFY row_number() OVER (PARTITION BY question_id, key ORDER BY question_id, key) = 1
  21: )
  22: SELECT *
  23: FROM deduplicated_rows
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__question_option.sql`；原件第1–33行。

```sql
   1: -- DuckDB-compatible staging model for question_option table
   2: -- Converted from dbt stg_qualtrics__question_option.sql
   3: -- Implements validation rules and data quality transformations per staging_data_specification.yaml
   4: 
   5: with validated_question_option_data as (
   6:     select
   7:         -- Required field validation
   8:         case
   9:             when question_id is not null and trim(question_id) != ''
  10:             then question_id
  11:             else null
  12:         end as question_id,
  13:         survey_id,
  14:         -- Required field validation
  15:         case
  16:             when key is not null and trim(key) != ''
  17:             then key
  18:             else null
  19:         end as key,
  20:         cast(recode_value as bigint) as recode_value,
  21:         text
  22:     from raw.question_option
  23: )
  24: 
  25: select
  26:     question_id,
  27:     survey_id,
  28:     key,
  29:     recode_value,
  30:     text
  31: from validated_question_option_data
  32: where question_id is not null
  33:   and key is not null  -- Required fields for composite primary key
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
SELECT 'raw.question_option' source_table,count(*) rows FROM raw.question_option
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.question_option' source_table,count(*) rows FROM raw.question_option\n                                                           ^"}
```

### 核实 V2：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "question_id","key",count(*) n FROM raw.question_option GROUP BY "question_id","key")
```

```json
{"error": "Parser Error: syntax error at or near \"groups\"\n\nLINE 1: SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n...\n                        ^"}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.question_option' source_table,count(*) source_rows FROM raw.question_option
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.question_option", 48000]]}
```

### 核实 V4：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) key_groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "question_id","key",count(*) n FROM raw.question_option GROUP BY "question_id","key")
```

```json
{"columns": ["key_groups", "duplicate_groups", "excess"], "result": [[43506, 4213, 4494]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["question_id", "key"]`；比较列：`["key", "question_id", "recode_value", "survey_id", "text"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 43506/48000 | 0/0 | 0/4494 | 0 | 4494 | 22470 | False |
| L1 | 43506/48000 | 0/0 | 0/4494 | 0 | 4494 | 22470 | False |
| L2 | 43506/48000 | 0/0 | 0/4494 | 0 | 4494 | 22470 | False |
| L3 | 43506/48000 | 0/0 | 0/4494 | 0 | 4494 | 22470 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| question_id | 0 | 0 | 0 | 0 |
| key | 0 | 0 | 0 | 0 |
| recode_value | 0 | 0 | 0 | 0 |
| survey_id | 0 | 0 | 0 | 0 |
| text | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-014_stg_qualtrics__question_option/baseline.sql`；SHA-256：`68500716c82851c141782524194bea03eb8ebff52be939faf38117c8ad9632cf`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 43506/48000 | 0/0 | 0/4494 | 0 | 4494 | 22470 | False |
| L1 | 43506/48000 | 0/0 | 0/4494 | 0 | 4494 | 22470 | False |
| L2 | 43506/48000 | 0/0 | 0/4494 | 0 | 4494 | 22470 | False |
| L3 | 43506/48000 | 0/0 | 0/4494 | 0 | 4494 | 22470 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| question_id | 0 | 0 | 0 | 0 |
| key | 0 | 0 | 0 | 0 |
| recode_value | 0 | 0 | 0 | 0 |
| survey_id | 0 | 0 | 0 | 0 |
| text | 0 | 0 | 0 | 0 |

### preserve_duplicates

SQL：`data/022_work/impl-014_stg_qualtrics__question_option/preserve_duplicates.sql`；SHA-256：`89b6867924d48f192589f0a5076d940f8ca769e586b46a5828ee2b1d6731aa77`。

替换offset=546，原表达式所在行约20（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
    QUALIFY row_number() OVER (PARTITION BY question_id, key ORDER BY question_id, key) = 1
-- 新

```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 48000/48000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 48000/48000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 48000/48000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 48000/48000 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| question_id | 0 | 0 | 0 | 0 |
| key | 0 | 0 | 0 | 0 |
| recode_value | 0 | 0 | 0 | 0 |
| survey_id | 0 | 0 | 0 | 0 |
| text | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：preserve_duplicates；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- preserve_duplicates：O；主项。契约primary_key/unique；gold未去重。（行减少4494，格减少22470）

## 规则问题

无。按v2冻结定义执行。
