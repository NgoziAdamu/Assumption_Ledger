# impl-014 / stg_qualtrics__survey_version（v2定稿）

## 1. 差异描述与判定

agent按显式时区格式成功解析12000个created_at，gold用TRY_CAST得到全NULL，契约未规定解析策略。

已核实：两边raw一致；016-V1中creation_date直接TRY_CAST成功0行，显式STRPTIME成功12000行。契约只有created_at TIMESTAMP，未指定源表达式、失败策略或非空。单把agent解析改为gold TRY_CAST即L0匹配，但这不证明agent未核实或数据处理有误。按未规定的解析/保留规则归A，中把握。 A项仅表示差异取决于契约未定的选择，不据gold实现认定agent做错。

主要原因：**A**；把握：**中**。
参与因素：无。标记：无。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-014_stg_qualtrics__survey_version.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

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

## 3. agent实际看到的信息与不确定性四档

event14显示survey_version.creation_date为VARCHAR。event57→58在raw.survey_response.recorded_date上实际测试带时区格式；event59把staging TRY_CAST替成STRPTIME。这是相邻源字段的可见测试，不夸大成已经查询本列全体；本次V1确认本列可完整解析。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|gold_timestamp_parser|A|只有通用策略说明|79|

### gold_timestamp_parser：只有通用策略说明

明确说明日期解析策略，但适用于多个日期模型，未点名survey_version.created_at。

事件 **79**，字段`args.final_thought`；[轨迹原文](../016_trace_impl-014.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-014/agent/.events/sessions/ca3bf0d3-3383-4f-b1d08418fd8e104/events/79.json`。
```text
原始 Qualtrics 时间文本带时区后缀（例如 `+0800`），DuckDB 直接 `try_cast(... AS TIMESTAMP)` 无法解析。日期相关 SQL 改用 `try_strptime(..., '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP`；不可解析日期在日期计算中排除。
```

已检视81个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：需要查业务说明。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-014.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
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

## 5. 逐项类别及U门槛

表级主要原因：**A**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|gold_timestamp_parser|A|12000→0|12000→0|L0|

重跑是否满足U第4条件：**是（改解析策略后L0整表一致；非U）**。

“格式可以解析本列”在本次核实中成立，不满足U条件2；不能为了匹配gold的NULL构造错误P。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：不适用：第二批首次标注。此字段不代替本次与016/017的对比。

## 规则问题

可读为O（gold解析丢值），也可读为A（未指定解析规则）。选择A：此契约允许NULL且没有与gold直接矛盾的表达式，差异确实来自双方处理方式；不扩张O到所有更保守或更宽松的解析。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
