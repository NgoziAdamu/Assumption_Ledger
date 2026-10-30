# impl-017 · stg_greenhouse__hiring_team

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：uniqueness。

agent 按契约 primary_key/unique 去重，gold 保留重复；移除去重后按评测列和键 L0 全匹配。

参与因素：无。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-017_stg_greenhouse__hiring_team.md](../023_packages/023_impl-017_stg_greenhouse__hiring_team.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-017/docs/data_contract.yaml`；SHA-256 `f4a1c779c8359b7fd5d9c8cae9760669aceb5b35f661d0fab07d0bf376762e41`。
契约行 387–400：

```
387:     - name: stg_greenhouse__hiring_team
388:       description: "Cleaned hiring team assignments"
389:       source_table: "raw.hiring_team"
390:       primary_key: ["job_id", "user_id"]
391:       columns:
392:         - name: job_id
393:           data_type: BIGINT
394:           constraints: [not_null]
395:         - name: user_id
396:           data_type: BIGINT
397:           constraints: [not_null]
398:         - name: role
399:           data_type: VARCHAR(100)
400:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/sql/staging/stg_greenhouse__hiring_team.sql`，SHA-256 `959bcbd3fe8395bd72545f2e7364468238111acc5ab415ef6e3e04c7309346de`，行 1–16。

```
1: WITH source_rows AS (
2:     SELECT
3:         TRY_CAST(job_id AS BIGINT) AS "job_id",
4:         TRY_CAST(user_id AS BIGINT) AS "user_id",
5:         TRY_CAST(role AS VARCHAR(100)) AS "role",
6:         ROW_NUMBER() OVER (PARTITION BY "job_id", "user_id" ORDER BY "job_id", "user_id") AS _row_num
7:     FROM raw.hiring_team
8: ),
9: validated_rows AS (
10:     SELECT *
11:     FROM source_rows
12:     WHERE "job_id" IS NOT NULL AND "user_id" IS NOT NULL AND "job_id" IS NOT NULL AND "user_id" IS NOT NULL
13: )
14: SELECT "job_id", "user_id", "role"
15: FROM validated_rows
16: WHERE _row_num = 1
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-017/sql/staging/stg_greenhouse__hiring_team.sql`，SHA-256 `579a3d6dc721174e9c2e3d1c737958c0d2baf8d3a807344954a4b92f2b3cab58`，行 1–30。

```
1: -- Purpose: Standardize hiring_team data with validation
2: -- Source: raw.hiring_team
3: -- Target: staging.stg_greenhouse__hiring_team
4: 
5: with source as (
6:     select * from raw.hiring_team
7: ),
8: 
9: renamed as (
10:     select
11:         cast(job_id as bigint) as job_id,
12:         cast(upper(trim(role)) as varchar) as hiring_team_role,
13:         cast(user_id as bigint) as user_id
14:     from source
15: ),
16: 
17: validated as (
18:     select
19:         job_id,
20:         hiring_team_role,
21:         user_id
22:     from renamed
23: 
24:     where
25:         -- Ensure required fields are not null (composite key)
26:         job_id is not null
27:         and user_id is not null
28: )
29: 
30: select * from validated
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
SELECT count(*) raw_rows,count(*)-count(DISTINCT row("job_id", "user_id")) duplicate_excess FROM raw.hiring_team
```


```json
{"columns":["raw_rows","duplicate_excess"],"rows":[[2000,1]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-017_stg_greenhouse__hiring_team.json](../023_reruns_impl-017_stg_greenhouse__hiring_team.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-017/agent/dacomp-de-impl-017/greenhouse.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1999|2000|1|2|否|
|L1|1999|2000|1|2|否|
|L2|1999|2000|1|2|否|
|L3|1999|2000|1|2|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"job_id":1,"user_id":1}`
- L1：`{"job_id":1,"user_id":1}`
- L2：`{"job_id":1,"user_id":1}`
- L3：`{"job_id":1,"user_id":1}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-017_stg_greenhouse__hiring_team/baseline.sql`；SHA-256 `959bcbd3fe8395bd72545f2e7364468238111acc5ab415ef6e3e04c7309346de`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1999|2000|1|2|否|
|L1|1999|2000|1|2|否|
|L2|1999|2000|1|2|否|
|L3|1999|2000|1|2|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"job_id":1,"user_id":1}`
- L1：`{"job_id":1,"user_id":1}`
- L2：`{"job_id":1,"user_id":1}`
- L3：`{"job_id":1,"user_id":1}`

#### uniqueness

判定：主因；类别候选 O。契约声明 primary_key/unique，agent 去重而 gold 保留重复。移除去重仅为定位诊断。

相对本轮基线减少行 1、格 2；按行优先、格次之排序。
共同控制后 SQL 第 16 行起、字符 offset 530 的唯一连续替换；其余字节不动。
替换前：
```sql
WHERE _row_num = 1
```

替换后：
```sql
WHERE TRUE
```

私有 SQL：`data/023_work/impl-017_stg_greenhouse__hiring_team/uniqueness.sql`；SHA-256 `79ecf1c62b9ff42a53c35c0a258564e06663a7ea27592ace5b850d22926d3118`。

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
