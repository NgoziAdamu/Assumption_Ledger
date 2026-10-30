# impl-017 · stg_greenhouse__eeoc

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：uniqueness。

agent 按契约 primary_key/unique 去重，gold 保留重复；移除去重后按评测列和键 L0 全匹配。

参与因素：无。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-017_stg_greenhouse__eeoc.md](../023_packages/023_impl-017_stg_greenhouse__eeoc.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml`；SHA-256 `f4a1c779c8359b7fd5d9c8cae9760669aceb5b35f661d0fab07d0bf376762e41`。
契约行 200–237：

```
200:     - name: stg_greenhouse__eeoc
201:       description: "Cleaned EEOC demographic data with standardized category values and privacy compliance"
202:       source_table: "raw.eeoc"
203:       primary_key: ["application_id"]
204:       columns:
205:         - name: application_id
206:           data_type: BIGINT
207:           constraints: [not_null, unique]
208:         - name: disability_status_description
209:           data_type: VARCHAR(100)
210:           validation_rules:
211:             - rule: "disability_status_description = TRIM(disability_status_description)"
212:               on_failure: correct
213:             - rule: "disability_status_description IN ('Yes', 'No', 'Prefer not to answer') OR disability_status_description IS NULL"
214:               on_failure: nullify_field
215:         - name: disability_status_id
216:           data_type: BIGINT
217:         - name: gender_description
218:           data_type: VARCHAR(100)
219:         - name: gender_id
220:           data_type: BIGINT
221:         - name: race_description
222:           data_type: VARCHAR(100)
223:         - name: race_id
224:           data_type: BIGINT
225:         - name: veteran_status_id
226:           data_type: BIGINT
227:         - name: veteran_status_description
228:           data_type: VARCHAR(100)
229:           validation_rules:
230:             - rule: "veteran_status_description = TRIM(veteran_status_description)"
231:               on_failure: correct
232:             - rule: "veteran_status_description IN ('Yes', 'No', 'Prefer not to answer') OR veteran_status_description IS NULL"
233:               on_failure: nullify_field
234:         - name: submitted_at
235:           data_type: TIMESTAMP
236: 
237:     # Additional staging tables for complete coverage of database schema
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/staging/stg_greenhouse__eeoc.sql`，SHA-256 `5312ae3e8655d201613746e454260a5c7dde5bd56fe61c82e313d224154830b5`，行 1–23。

```
1: WITH source_rows AS (
2:     SELECT
3:         TRY_CAST(application_id AS BIGINT) AS "application_id",
4:         CASE WHEN TRIM(disability_status_description) IN ('Yes', 'No', 'Prefer not to answer') THEN TRIM(disability_status_description) ELSE NULL END AS disability_status_description,
5:         TRY_CAST(disability_status_id AS BIGINT) AS "disability_status_id",
6:         TRY_CAST(gender_description AS VARCHAR(100)) AS "gender_description",
7:         TRY_CAST(gender_id AS BIGINT) AS "gender_id",
8:         TRY_CAST(race_description AS VARCHAR(100)) AS "race_description",
9:         TRY_CAST(race_id AS BIGINT) AS "race_id",
10:         TRY_CAST(veteran_status_id AS BIGINT) AS "veteran_status_id",
11:         CASE WHEN TRIM(veteran_status_description) IN ('Yes', 'No', 'Prefer not to answer') THEN TRIM(veteran_status_description) ELSE NULL END AS veteran_status_description,
12:         TRY_CAST(submitted_at AS TIMESTAMP) AS "submitted_at",
13:         ROW_NUMBER() OVER (PARTITION BY "application_id" ORDER BY "application_id") AS _row_num
14:     FROM raw.eeoc
15: ),
16: validated_rows AS (
17:     SELECT *
18:     FROM source_rows
19:     WHERE "application_id" IS NOT NULL AND "application_id" IS NOT NULL
20: )
21: SELECT "application_id", "disability_status_description", "disability_status_id", "gender_description", "gender_id", "race_description", "race_id", "veteran_status_id", "veteran_status_description", "submitted_at"
22: FROM validated_rows
23: WHERE _row_num = 1
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/sql/staging/stg_greenhouse__eeoc.sql`，SHA-256 `cc06aeae670f8faab0313594428fd2263691a0311ec3f70ea02adc3d405821b8`，行 1–55。

```
1: -- Purpose: Standardize EEOC demographic data with validation
2: -- Source: raw.eeoc
3: -- Target: staging.stg_greenhouse__eeoc
4: 
5: with source as (
6:     select * from raw.eeoc
7: ),
8: 
9: renamed as (
10:     select
11:         application_id,
12:         LTRIM(RTRIM(disability_status_description)) as disability_status_description,
13:         disability_status_id,
14:         gender_description,
15:         gender_id,
16:         race_description,
17:         race_id,
18:         veteran_status_id,
19:         LTRIM(RTRIM(veteran_status_description)) as veteran_status_description,
20:         submitted_at
21: 
22:     from source
23: ),
24: 
25: validated as (
26:     select
27:         application_id,
28:         -- Validate disability status values
29:         case
30:             when disability_status_description in ('Yes', 'No', 'Prefer not to answer') or disability_status_description is null
31:             then disability_status_description
32:             else null
33:         end as disability_status_description,
34:         disability_status_id,
35:         gender_description,
36:         gender_id,
37:         race_description,
38:         race_id,
39:         veteran_status_id,
40:         -- Validate veteran status values
41:         case
42:             when veteran_status_description in ('Yes', 'No', 'Prefer not to answer') or veteran_status_description is null
43:             then veteran_status_description
44:             else null
45:         end as veteran_status_description,
46:         submitted_at
47: 
48:     from renamed
49: 
50:     where
51:         -- Ensure primary key field is not null
52:         application_id is not null
53: )
54: 
55: select * from validated
```

## 轨迹可见性与不确定性

**四档：只有通用策略说明**。

event 1 提供主键声明；event 15/16 看过 raw schema/样例；event 17 统一生成去重。event 53：「staging 对声明为主键的空值行进行过滤，并按主键分组只保留一条记录以满足唯一性；若重复键的内容不一致，合同没有规定优先版本」。此为跨表处理策略，非实施清单。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 1：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/1.json`。
- event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/15.json`。
- event 16：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/16.json`。
- event 17：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/17.json`。
- event 53：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-017/agent/.events/sessions/d546fc89-3859-42-15204be21f2c115/events/53.json`。

event 53 最终报告原文（用于检查说明是否超出工作清单）：

```
【回复用户】

已完成 `sql/` 数据流水线实现，依照配置顺序覆盖 staging、intermediate、marts 三层，共生成 52 个 DuckDB SQL 文件。所有上游引用使用 schema.table 格式，无 dbt `ref()` 调用，也没有以分号结束的 SQL 语句。

实现内容包括：
- **Staging：** 基于合同逐表映射 raw 字段到契约列，执行类型转换、必填/主键空值过滤、重复主键保留一条及合同明确要求的状态和字段清理。原始表与合同字段名不一致时，按实际 raw schema 映射（例如 `candidate.id` → `candidate_id`、`phone_number.value` → `phone_number`）。
- **Intermediate：** 实现用户邮箱、候选人联系方式/标签/联系日期、招聘团队、职位地点/部门、应用整合和面试评分卡等模型。
- **Marts：** 实现增强应用、面试及职位模型，以及申请历史、候选人摘要、DEI、招聘表现和人才来源分析模型。

**验证结果：** 执行 `python run.py` 成功，日志显示所有配置的 staging、intermediate 和 marts 模型均执行完成；输出数据库 `greenhouse.duckdb` 包含三层模型表。再次执行后流水线同样成功。SQL 文件保留了 `STRING_AGG` 中作为分隔符的 `'; '` 文本，该字符只是字符串常量，并非语句结束符。

**处理策略与残余影响：** staging 对声明为主键的空值行进行过滤，并按主键分组只保留一条记录以满足唯一性；若重复键的内容不一致，合同没有规定优先版本，因而保留记录选择未定义，重复记录中的非键值可能丢失。合同没有要求的外键缺失通常在 intermediate/marts 中按左连接保留并产生 NULL；明确要求 inner join 的模型会排除不匹配记录。可选字段只在合同明确要求时进行 nullify 或标准化，未配置清理规则的字段按类型转换并透传。

**合同注意事项：** 部分 raw 字段名称与合同字段名称不同，已采用源表实际字段映射。候选人及用户的 `full_name` 在 raw schema 不存在独立字段，因此由名字与姓氏组合得出；职位办公室的原字段名 `name` 映射为契约 `office_name`。对没有给出唯一裁决逻辑的并列最大索引记录，使用窗口排序选择一条，平局时具体选中行未保证。未发现导致运行失败的 SQL 语句；实现期间曾发现并修复字段引用/关键字转义问题，最终流水线验证无 SQL 错误。
```

## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：契约主键重复

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/greenhouse.duckdb`。

```sql
SELECT count(*) raw_rows,count(*)-count(DISTINCT row("application_id")) duplicate_excess FROM raw.eeoc
```


```json
{"columns":["raw_rows","duplicate_excess"],"rows":[[2000,154]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-017_stg_greenhouse__eeoc.json](../023_reruns_impl-017_stg_greenhouse__eeoc.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/greenhouse.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1846|2000|154|1386|否|
|L1|1846|2000|154|1386|否|
|L2|1846|2000|154|1386|否|
|L3|1846|2000|154|1386|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"application_id":154,"disability_status_description":154,"disability_status_id":154,"gender_description":154,"gender_id":154,"race_description":154,"race_id":154,"veteran_status_description":154,"veteran_status_id":154}`
- L1：`{"application_id":154,"disability_status_description":154,"disability_status_id":154,"gender_description":154,"gender_id":154,"race_description":154,"race_id":154,"veteran_status_description":154,"veteran_status_id":154}`
- L2：`{"application_id":154,"disability_status_description":154,"disability_status_id":154,"gender_description":154,"gender_id":154,"race_description":154,"race_id":154,"veteran_status_description":154,"veteran_status_id":154}`
- L3：`{"application_id":154,"disability_status_description":154,"disability_status_id":154,"gender_description":154,"gender_id":154,"race_description":154,"race_id":154,"veteran_status_description":154,"veteran_status_id":154}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-017_stg_greenhouse__eeoc/baseline.sql`；SHA-256 `5312ae3e8655d201613746e454260a5c7dde5bd56fe61c82e313d224154830b5`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1846|2000|154|1386|否|
|L1|1846|2000|154|1386|否|
|L2|1846|2000|154|1386|否|
|L3|1846|2000|154|1386|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"application_id":154,"disability_status_description":154,"disability_status_id":154,"gender_description":154,"gender_id":154,"race_description":154,"race_id":154,"veteran_status_description":154,"veteran_status_id":154}`
- L1：`{"application_id":154,"disability_status_description":154,"disability_status_id":154,"gender_description":154,"gender_id":154,"race_description":154,"race_id":154,"veteran_status_description":154,"veteran_status_id":154}`
- L2：`{"application_id":154,"disability_status_description":154,"disability_status_id":154,"gender_description":154,"gender_id":154,"race_description":154,"race_id":154,"veteran_status_description":154,"veteran_status_id":154}`
- L3：`{"application_id":154,"disability_status_description":154,"disability_status_id":154,"gender_description":154,"gender_id":154,"race_description":154,"race_id":154,"veteran_status_description":154,"veteran_status_id":154}`

#### uniqueness

判定：主因；类别候选 O。契约声明 primary_key/unique，agent 去重而 gold 保留重复。移除去重仅为定位诊断。

相对本轮基线减少行 154、格 1386；按行优先、格次之排序。
共同控制后 SQL 第 23 行起、字符 offset 1400 的唯一连续替换；其余字节不动。
替换前：
```sql
WHERE _row_num = 1
```

替换后：
```sql
WHERE TRUE
```

私有 SQL：`data/023_work/impl-017_stg_greenhouse__eeoc/uniqueness.sql`；SHA-256 `e3bcc45ae76f9e0bfc1f547c29a12d425422f32be435dbb723c7a4e228cfd10a`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2000|2000|0|0|是|
|L1|2000|2000|0|0|是|
|L2|2000|2000|0|0|是|
|L3|2000|2000|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 规则问题

无
