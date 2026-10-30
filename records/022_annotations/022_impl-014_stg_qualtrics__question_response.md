# impl-014 / stg_qualtrics__question_response（全量；v2）

## 1. 差异与结论

response_id/question_id主键去重11行，撤QUALIFY全表L0一致，O。

主要原因：**O**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| preserve_duplicates | O | 11 | 99 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-014_stg_qualtrics__question_response.md](../../records/022_packages/022_impl-014_stg_qualtrics__question_response.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-014_stg_qualtrics__question_response/022_impl-014_stg_qualtrics__question_response.json`。
- 比较结果：[022_reruns_impl-014_stg_qualtrics__question_response.json](../022_reruns_impl-014_stg_qualtrics__question_response.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`。

原件第258–287行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__question_response.sql`；原件第1–28行。

```sql
   1: WITH source_rows AS (
   2:     SELECT
   3:         try_cast(src."response_id" AS VARCHAR) AS response_id,
   4:         try_cast(src."question_id" AS VARCHAR) AS question_id,
   5:         try_cast(src."question_option_key" AS DOUBLE) AS question_option_key,
   6:         try_cast(src."value" AS DOUBLE) AS value,
   7:         try_cast(src."text" AS VARCHAR) AS response_text,
   8:         try_cast(src."loop_id" AS BIGINT) AS loop_id,
   9:         try_cast(src."question" AS VARCHAR) AS question,
  10:         trim(try_cast(src."sub_question_key" AS VARCHAR)) AS sub_question_key,
  11:         try_cast(src."sub_question_text" AS DOUBLE) AS sub_question_text
  12:     FROM raw.question_response AS src
  13: ),
  14: validated_rows AS (
  15:     SELECT *
  16:     FROM source_rows
  17:     WHERE 1 = 1
  18:       AND response_id IS NOT NULL AND question_id IS NOT NULL
  19:       AND response_id IS NOT NULL
  20:       AND question_id IS NOT NULL
  21: ),
  22: deduplicated_rows AS (
  23:     SELECT *
  24:     FROM validated_rows
  25:     QUALIFY row_number() OVER (PARTITION BY response_id, question_id ORDER BY response_id, question_id) = 1
  26: )
  27: SELECT *
  28: FROM deduplicated_rows
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__question_response.sql`；原件第1–45行。

```sql
   1: -- DuckDB-compatible staging model for question_response table
   2: -- Converted from dbt stg_qualtrics__question_response.sql
   3: -- Implements validation rules and data quality transformations per staging_data_specification.yaml
   4: 
   5: with validated_question_response_data as (
   6:     select
   7:         -- Required field validation
   8:         case
   9:             when response_id is not null and trim(response_id) != ''
  10:             then response_id
  11:             else null
  12:         end as response_id,
  13:         case
  14:             when question_id is not null and trim(question_id) != ''
  15:             then question_id
  16:             else null
  17:         end as question_id,
  18:         cast(question_option_key as double) as question_option_key,
  19:         cast(value as double) as value,
  20:         text as response_text,
  21:         cast(loop_id as bigint) as loop_id,
  22:         question,
  23:         -- Sub-question key trimming validation
  24:         case
  25:             when sub_question_key is not null
  26:             then trim(cast(sub_question_key as varchar))
  27:             else null
  28:         end as sub_question_key,
  29:         cast(sub_question_text as double) as sub_question_text
  30:     from raw.question_response
  31: )
  32: 
  33: select
  34:     response_id,
  35:     question_id,
  36:     question_option_key,
  37:     value,
  38:     response_text,
  39:     loop_id,
  40:     question,
  41:     sub_question_key,
  42:     sub_question_text
  43: from validated_question_response_data
  44: where response_id is not null
  45:   and question_id is not null  -- Required fields for primary key
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
SELECT 'raw.question_response' source_table,count(*) rows FROM raw.question_response
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.question_response' source_table,count(*) rows FROM raw.question_response\n                                                             ^"}
```

### 核实 V2：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "response_id","question_id",count(*) n FROM raw.question_response GROUP BY "response_id","question_id")
```

```json
{"error": "Parser Error: syntax error at or near \"groups\"\n\nLINE 1: SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n...\n                        ^"}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.question_response' source_table,count(*) source_rows FROM raw.question_response
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.question_response", 72000]]}
```

### 核实 V4：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) key_groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "response_id","question_id",count(*) n FROM raw.question_response GROUP BY "response_id","question_id")
```

```json
{"columns": ["key_groups", "duplicate_groups", "excess"], "result": [[71989, 11, 11]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["response_id", "question_id"]`；比较列：`["loop_id", "question", "question_id", "question_option_key", "response_id", "response_text", "sub_question_key", "sub_question_text", "value"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 71989/72000 | 0/0 | 0/11 | 0 | 11 | 99 | False |
| L1 | 71989/72000 | 0/0 | 0/11 | 0 | 11 | 99 | False |
| L2 | 71989/72000 | 0/0 | 0/11 | 0 | 11 | 99 | False |
| L3 | 71989/72000 | 0/0 | 0/11 | 0 | 11 | 99 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| response_id | 0 | 0 | 0 | 0 |
| question_id | 0 | 0 | 0 | 0 |
| loop_id | 0 | 0 | 0 | 0 |
| question | 0 | 0 | 0 | 0 |
| question_option_key | 0 | 0 | 0 | 0 |
| response_text | 0 | 0 | 0 | 0 |
| sub_question_key | 0 | 0 | 0 | 0 |
| sub_question_text | 0 | 0 | 0 | 0 |
| value | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-014_stg_qualtrics__question_response/baseline.sql`；SHA-256：`8b690f0dd06012c21aa8a99a3f8f24704f5f03a8728f5d9afc0c4fc6df36515b`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 71989/72000 | 0/0 | 0/11 | 0 | 11 | 99 | False |
| L1 | 71989/72000 | 0/0 | 0/11 | 0 | 11 | 99 | False |
| L2 | 71989/72000 | 0/0 | 0/11 | 0 | 11 | 99 | False |
| L3 | 71989/72000 | 0/0 | 0/11 | 0 | 11 | 99 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| response_id | 0 | 0 | 0 | 0 |
| question_id | 0 | 0 | 0 | 0 |
| loop_id | 0 | 0 | 0 | 0 |
| question | 0 | 0 | 0 | 0 |
| question_option_key | 0 | 0 | 0 | 0 |
| response_text | 0 | 0 | 0 | 0 |
| sub_question_key | 0 | 0 | 0 | 0 |
| sub_question_text | 0 | 0 | 0 | 0 |
| value | 0 | 0 | 0 | 0 |

### preserve_duplicates

SQL：`data/022_work/impl-014_stg_qualtrics__question_response/preserve_duplicates.sql`；SHA-256：`20a49db632e799d5aa36b7fc273df7ac926006f38784fce4528577f0253df7d3`。

替换offset=912，原表达式所在行约25（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
    QUALIFY row_number() OVER (PARTITION BY response_id, question_id ORDER BY response_id, question_id) = 1
-- 新

```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 72000/72000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 72000/72000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 72000/72000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 72000/72000 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| response_id | 0 | 0 | 0 | 0 |
| question_id | 0 | 0 | 0 | 0 |
| loop_id | 0 | 0 | 0 | 0 |
| question | 0 | 0 | 0 | 0 |
| question_option_key | 0 | 0 | 0 | 0 |
| response_text | 0 | 0 | 0 | 0 |
| sub_question_key | 0 | 0 | 0 | 0 |
| sub_question_text | 0 | 0 | 0 | 0 |
| value | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：preserve_duplicates；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- preserve_duplicates：O；主项。契约primary_key/unique；gold未去重。（行减少11，格减少99）

## 规则问题

无。按v2冻结定义执行。
