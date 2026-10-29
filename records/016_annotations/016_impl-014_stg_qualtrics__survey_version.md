# impl-014 / stg_qualtrics__survey_version

## 1. 错在哪里

agent按显式时区格式成功解析12000个created_at，gold用TRY_CAST得到全NULL，契约未规定解析策略。

已核实：两边raw一致；016-V1中creation_date直接TRY_CAST成功0行，显式STRPTIME成功12000行。契约只有created_at TIMESTAMP，未指定源表达式、失败策略或非空。单把agent解析改为gold TRY_CAST即L0匹配，但这不证明agent未核实或数据处理有误。按未规定的解析/保留规则归A，中把握。

## 2. 依据

- 起点：[013精简材料包](../013_packages/013_impl-014_staging_stg_qualtrics__survey_version.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-014/docs/data_contract.yaml` 第632–657行。
- [原始轨迹转录](../016_trace_impl-014.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-014.json)；[015三方raw核对](../015_raw_impl-014.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_qualtrics__survey_version
      description: "Survey version history and metadata"
      source_table: "raw.survey_version"
      primary_key: ["version_id"]
      columns:
        - name: version_id
          data_type: BIGINT
          constraints: [not_null, unique]
        - name: survey_id
          data_type: VARCHAR
        - name: created_at
          data_type: TIMESTAMP
        - name: version_description
          data_type: VARCHAR
        - name: is_published
          data_type: BOOLEAN
        - name: publisher_user_id
          data_type: VARCHAR
        - name: version_number
          data_type: BIGINT
        - name: was_published
          data_type: BOOLEAN

# --------------------------------------------------------------------------- #
# PHASE 2: Defines the business logic from staging tables to analytical models. #
# --------------------------------------------------------------------------- #
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/sql/staging/stg_qualtrics__survey_version.sql`
```sql
   1: WITH source_rows AS (
   2:     SELECT
   3:         try_cast(src."id" AS BIGINT) AS version_id,
   4:         try_cast(src."survey_id" AS VARCHAR) AS survey_id,
   5:         try_strptime(cast(src."creation_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS created_at,
   6:         try_cast(src."description" AS VARCHAR) AS version_description,
   7:         try_cast(src."published" AS BOOLEAN) AS is_published,
   8:         try_cast(src."user_id" AS VARCHAR) AS publisher_user_id,
   9:         try_cast(src."version_number" AS BIGINT) AS version_number,
  10:         try_cast(src."was_published" AS BOOLEAN) AS was_published
  11:     FROM raw.survey_version AS src
  12: ),
  13: validated_rows AS (
  14:     SELECT *
  15:     FROM source_rows
  16:     WHERE 1 = 1
  17:       AND version_id IS NOT NULL
  18: ),
  19: deduplicated_rows AS (
  20:     SELECT *
  21:     FROM validated_rows
  22:     QUALIFY row_number() OVER (PARTITION BY version_id ORDER BY version_id) = 1
  23: )
  24: SELECT *
  25: FROM deduplicated_rows
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-014/sql/staging/stg_qualtrics__survey_version.sql`
```sql
   1: -- DuckDB-compatible staging model for survey_version table
   2: -- Converted from dbt stg_qualtrics__survey_version.sql
   3: -- Implements validation rules and data quality transformations per staging_data_specification.yaml
   4: 
   5: with validated_survey_version_data as (
   6:     select
   7:         id as version_id,
   8:         try_cast(creation_date as timestamp) as created_at,
   9:         trim(description) as version_description,
  10:         cast(published as boolean) as is_published,
  11:         trim(survey_id) as survey_id,
  12:         trim(user_id) as publisher_user_id,
  13:         cast(version_number as bigint) as version_number,
  14:         cast(was_published as boolean) as was_published
  15:     from raw.survey_version
  16:     where id is not null  -- Basic primary key validation
  17: )
  18: 
  19: select
  20:     version_id,
  21:     created_at,
  22:     version_description,
  23:     is_published,
  24:     survey_id,
  25:     publisher_user_id,
  26:     version_number,
  27:     was_published
  28: from validated_survey_version_data
  29: where version_id is not null
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.survey_version|gold_vs_initial|True|True|True||
|raw.survey_version|gold_vs_agent|True|True|True||

## 3. agent看过什么

event14显示survey_version.creation_date为VARCHAR。event57→58在raw.survey_response.recorded_date上实际测试带时区格式；event59把staging TRY_CAST替成STRPTIME。这是相邻源字段的可见测试，不夸大成已经查询本列全体；本次V1确认本列可完整解析。

区分event实际展示的契约/数据与磁盘上存在的资料；截断输出中未出现的部分不算agent已经看到。核实查询是标注者新增查询，不冒充agent执行过。

## 4. 查询与重跑

核实查询合计 **1条**（含014复用；本轮新增1条）；核实代价档：**需要查业务说明**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 016-V1 / 核实查询

来源：`records/016_queries_impl-014.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-014/agent/dacomp-de-impl-014/qualtrics.duckdb`。

```sql
SELECT count(*) n,count(try_cast(creation_date as timestamp)) cast_nonnull,count(try_strptime(cast(creation_date as varchar),'%Y-%m-%d %H:%M:%S.%f %z')) strptime_nonnull FROM raw.survey_version
```
结果原文：
```json
{
  "columns": [
    "n",
    "cast_nonnull",
    "strptime_nonnull"
  ],
  "rows": [
    [
      12000,
      0,
      12000
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['version_id']`；比较列（与键取并集）：`['created_at', 'is_published', 'publisher_user_id', 'survey_id', 'version_description', 'version_id', 'version_number', 'was_published']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：本次重新执行；原013留存输出另列

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|gold_timestamp_parser|12000→0|12000→0|L0|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|12000|12000|0|0|0/0|12000|12000|12000|False|
|L1|12000|12000|0|0|0/0|12000|12000|12000|False|
|L2|12000|12000|0|0|0/0|12000|12000|12000|False|
|L3|12000|12000|0|0|0/0|12000|12000|12000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|version_id|0|0|0|0|
|created_at|12000|12000|12000|12000|
|is_published|0|0|0|0|
|publisher_user_id|0|0|0|0|
|survey_id|0|0|0|0|
|version_description|0|0|0|0|
|version_number|0|0|0|0|
|was_published|0|0|0|0|

### 重跑 baseline

SQL：`data/016_work/impl-014/baseline.sql`；SHA-256：`26998e70d8c9cf376a0753ca3cde4d709537079c8f4ddaf5531d3cee9a3996de`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|12000|12000|0|0|0/0|12000|12000|12000|False|
|L1|12000|12000|0|0|0/0|12000|12000|12000|False|
|L2|12000|12000|0|0|0/0|12000|12000|12000|False|
|L3|12000|12000|0|0|0/0|12000|12000|12000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|version_id|0|0|0|0|
|created_at|12000|12000|12000|12000|
|is_published|0|0|0|0|
|publisher_user_id|0|0|0|0|
|survey_id|0|0|0|0|
|version_description|0|0|0|0|
|version_number|0|0|0|0|
|was_published|0|0|0|0|

### 重跑 gold_timestamp_parser

SQL：`data/016_work/impl-014/gold_timestamp_parser.sql`；SHA-256：`fdc20113b15da886dd9aaf2f9219ace612863c75773a444cdc5e6d36fe38a015`。

唯一原文位置offset=152，替换前：
```sql
try_strptime(cast(src."creation_date" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP
```
替换后：
```sql
try_cast(src."creation_date" AS TIMESTAMP)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|12000|12000|0|0|0/0|0|0|0|True|
|L1|12000|12000|0|0|0/0|0|0|0|True|
|L2|12000|12000|0|0|0/0|0|0|0|True|
|L3|12000|12000|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|version_id|0|0|0|0|
|created_at|0|0|0|0|
|is_published|0|0|0|0|
|publisher_user_id|0|0|0|0|
|survey_id|0|0|0|0|
|version_description|0|0|0|0|
|version_number|0|0|0|0|
|was_published|0|0|0|0|

## 5. 类别、把握及与014对比

- 主要原因：**A**。
- 主因对应单项：gold_timestamp_parser。
- 参与因素：无。
- 标记：无。
- 把握：**中**。
- 重跑是否满足U第4条件：是（改解析策略后L0整表一致；非U）。

“格式可以解析本列”在本次核实中成立，不满足U条件2；不能为了匹配gold的NULL构造错误P。

与014相比：**不适用：第二批首次标注**

## 规则问题

可读为O（gold解析丢值），也可读为A（未指定解析规则）。选择A：此契约允许NULL且没有与gold直接矛盾的表达式，差异确实来自双方处理方式；不扩张O到所有更保守或更宽松的解析。

2026-10-29用户确认的第3节补充：仅当本表依赖raw满足agent留存=初始、gold不同，且诊断确认影响可评估性时标“不可评估”；gold=初始、agent不同则照常标注，查轨迹改动。不能把两类混为一谈。若gold与agent一致但二者不同于初始（019/020），当前本节点仍可比较；初始差异另记。

共同执行例外：最初指纹快照因外部v0附件已不在原桌面路径而失败；成功的016快照晚于首批私有重跑。已逐文件与015任务前的大小、mtime、SHA-256比较，覆盖原始库的历史指纹无变化；不把晚快照伪称执行前快照。仓库v0与004–015记录保留。
