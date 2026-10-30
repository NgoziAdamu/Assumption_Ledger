# impl-014 / stg_qualtrics__block_question（全量；v2）

## 1. 差异与结论

契约复合primary_key，agent去重；gold多4行。仅撤QUALIFY后L0一致，O。

主要原因：**O**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| preserve_duplicates | O | 4 | 12 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-014_stg_qualtrics__block_question.md](../../records/022_packages/022_impl-014_stg_qualtrics__block_question.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-014_stg_qualtrics__block_question/022_impl-014_stg_qualtrics__block_question.json`。
- 比较结果：[022_reruns_impl-014_stg_qualtrics__block_question.json](../022_reruns_impl-014_stg_qualtrics__block_question.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml`。

原件第492–505行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__block_question.sql`；原件第1–21行。

```sql
   1: WITH source_rows AS (
   2:     SELECT
   3:         try_cast(src."block_id" AS VARCHAR) AS block_id,
   4:         try_cast(src."question_id" AS VARCHAR) AS question_id,
   5:         try_cast(src."survey_id" AS VARCHAR) AS survey_id
   6:     FROM raw.block_question AS src
   7: ),
   8: validated_rows AS (
   9:     SELECT *
  10:     FROM source_rows
  11:     WHERE 1 = 1
  12:       AND block_id IS NOT NULL
  13:       AND question_id IS NOT NULL
  14: ),
  15: deduplicated_rows AS (
  16:     SELECT *
  17:     FROM validated_rows
  18:     QUALIFY row_number() OVER (PARTITION BY block_id, question_id ORDER BY block_id, question_id) = 1
  19: )
  20: SELECT *
  21: FROM deduplicated_rows
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__block_question.sql`；原件第1–21行。

```sql
   1: -- DuckDB-compatible staging model for block_question table
   2: -- Converted from dbt stg_qualtrics__block_question.sql
   3: -- Implements validation rules and data quality transformations per staging_data_specification.yaml
   4: 
   5: with validated_block_question_data as (
   6:     select
   7:         trim(block_id) as block_id,
   8:         trim(question_id) as question_id,
   9:         trim(survey_id) as survey_id
  10:     from raw.block_question
  11:     where block_id is not null
  12:       and question_id is not null  -- Composite primary key validation
  13: )
  14: 
  15: select
  16:     block_id,
  17:     question_id,
  18:     survey_id
  19: from validated_block_question_data
  20: where block_id is not null
  21:   and question_id is not null
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
SELECT 'raw.block_question' source_table,count(*) rows FROM raw.block_question
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.block_question' source_table,count(*) rows FROM raw.block_question\n                                                          ^"}
```

### 核实 V2：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "block_id","question_id",count(*) n FROM raw.block_question GROUP BY "block_id","question_id")
```

```json
{"error": "Parser Error: syntax error at or near \"groups\"\n\nLINE 1: SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n...\n                        ^"}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT 'raw.block_question' source_table,count(*) source_rows FROM raw.block_question
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.block_question", 24000]]}
```

### 核实 V4：原始重复键

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) key_groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT "block_id","question_id",count(*) n FROM raw.block_question GROUP BY "block_id","question_id")
```

```json
{"columns": ["key_groups", "duplicate_groups", "excess"], "result": [[23996, 4, 4]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["block_id", "question_id"]`；比较列：`["block_id", "question_id", "survey_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 23996/24000 | 0/0 | 0/4 | 0 | 4 | 12 | False |
| L1 | 23996/24000 | 0/0 | 0/4 | 0 | 4 | 12 | False |
| L2 | 23996/24000 | 0/0 | 0/4 | 0 | 4 | 12 | False |
| L3 | 23996/24000 | 0/0 | 0/4 | 0 | 4 | 12 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| block_id | 0 | 0 | 0 | 0 |
| question_id | 0 | 0 | 0 | 0 |
| survey_id | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-014_stg_qualtrics__block_question/baseline.sql`；SHA-256：`346176e769bdaa86975c23248d9846dfe2227072ff6b258b52d1430762d704e7`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 23996/24000 | 0/0 | 0/4 | 0 | 4 | 12 | False |
| L1 | 23996/24000 | 0/0 | 0/4 | 0 | 4 | 12 | False |
| L2 | 23996/24000 | 0/0 | 0/4 | 0 | 4 | 12 | False |
| L3 | 23996/24000 | 0/0 | 0/4 | 0 | 4 | 12 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| block_id | 0 | 0 | 0 | 0 |
| question_id | 0 | 0 | 0 | 0 |
| survey_id | 0 | 0 | 0 | 0 |

### preserve_duplicates

SQL：`data/022_work/impl-014_stg_qualtrics__block_question/preserve_duplicates.sql`；SHA-256：`a22d54b8559f54db78120475c1d5c7ea387a390bef4ef3dfeb7b3e24981b52b5`。

替换offset=447，原表达式所在行约18（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
    QUALIFY row_number() OVER (PARTITION BY block_id, question_id ORDER BY block_id, question_id) = 1
-- 新

```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 24000/24000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 24000/24000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 24000/24000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 24000/24000 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| block_id | 0 | 0 | 0 | 0 |
| question_id | 0 | 0 | 0 | 0 |
| survey_id | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：preserve_duplicates；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- preserve_duplicates：O；主项。契约primary_key/unique；gold未去重。（行减少4，格减少12）

## 规则问题

无。按v2冻结定义执行。
