# impl-002 / stg_pendo__guide_event（v2定稿）

## 1. 差异描述与判定

URL校验遗漏与未规定的hash公式各造成15000格差异，并列主因；另有13655个超界纬度。

已核实：基线15000行、43655格。key_formula和url_rule单改均保持15000行，但各减少15000格；latitude_range单改减少13655格。按v2第5节改用格子后C/A并列。契约给出可执行URL正则，agent只trim，按字面执行归C；生成键公式未给出，归A。纬度超出±90违反列本身硬约束，按v2补充归U参与因素。URL的SQL全匹配与现实URL是否有效是不同问题，不评价这些地址在现实中有效与否。 A项仅表示差异取决于契约未定的选择，不据gold实现认定agent做错。

主要原因：**多因并列（C、A）**；把握：**高**。
参与因素：U：latitude硬约束（单改减少13655格）。标记：无。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-002_stg_pendo__guide_event.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-002_staging_stg_pendo__guide_event.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml` 第268–321行。
- [原始轨迹转录](../014_trace_impl-002.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-002.json)；[015三方raw核对](../015_raw_impl-002.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_pendo__guide_event
      description: "Cleaned guide interaction events with validated guide steps and timing"
      source_table: "raw.guide_event"
      columns:
        - name: account_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: guide_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: remote_ip
          data_type: VARCHAR(255)
          validation_rules:
            - rule: "remote_ip IS NULL OR remote_ip ~ '^([0-9]{1,3}){3}[0-9]{1,3}$' OR remote_ip ~ '^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'"
              on_failure: nullify_field
        - name: server_name
          data_type: VARCHAR(255)
        - name: occurred_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: user_agent
          data_type: VARCHAR(255)
        - name: visitor_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: app_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: country
          data_type: VARCHAR(255)
        - name: guide_step_id
          data_type: BIGINT
        - name: latitude
          data_type: DOUBLE
        - name: longitude
          data_type: DOUBLE
          validation_rules:
            - rule: "longitude BETWEEN -180 AND 180 OR longitude IS NULL"
              on_failure: nullify_field
        - name: region
          data_type: VARCHAR(255)
        - name: type
          data_type: VARCHAR(255)
        - name: url
          data_type: VARCHAR(255)
          validation_rules:
            - rule: "url = NULLIF(TRIM(url), '')"
              on_failure: correct
            - rule: "url IS NULL OR url ~ '^https?://'"
              on_failure: nullify_field
        - name: guide_event_key
          data_type: VARCHAR(255)
          description: "Generated surrogate key"
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql`
```sql
   1: SELECT
   2:     CAST(account_id AS VARCHAR) AS account_id,
   3:     CAST(guide_id AS VARCHAR) AS guide_id,
   4:     CASE WHEN remote_ip IS NULL OR regexp_matches(CAST(remote_ip AS VARCHAR), '^([0-9]{1,3}\.){3}[0-9]{1,3}$') OR regexp_matches(CAST(remote_ip AS VARCHAR), '^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$') THEN CAST(remote_ip AS VARCHAR) ELSE NULL END AS remote_ip,
   5:     NULLIF(TRIM(CAST(server_name AS VARCHAR)), '') AS server_name,
   6:     TRY_CAST(SUBSTRING(CAST(timestamp AS VARCHAR), 1, 23) AS TIMESTAMP) AS occurred_at,
   7:     NULLIF(TRIM(CAST(user_agent AS VARCHAR)), '') AS user_agent,
   8:     CAST(visitor_id AS VARCHAR) AS visitor_id,
   9:     CAST(app_id AS VARCHAR) AS app_id,
  10:     CAST(country AS VARCHAR) AS country,
  11:     TRY_CAST(guide_step_id AS BIGINT) AS guide_step_id,
  12:     TRY_CAST(latitude AS DOUBLE) AS latitude,
  13:     CASE WHEN TRY_CAST(longitude AS DOUBLE) BETWEEN -180 AND 180 THEN TRY_CAST(longitude AS DOUBLE) ELSE NULL END AS longitude,
  14:     CAST(region AS VARCHAR) AS region,
  15:     CAST(type AS VARCHAR) AS type,
  16:     CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS VARCHAR)), '') END AS url,
  17:     md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(guide_id AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), ''))) AS guide_event_key
  18: FROM raw.guide_event
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql`
```sql
   1: -- Staging model for guide_event
   2: -- Converted from DBT to DuckDB-compatible SQL
   3: -- Implements data quality checks per staging_data_specification.yaml
   4: 
   5: SELECT
   6:     -- Account ID with proper data type and validation
   7:     CAST(account_id AS VARCHAR(50)) as account_id,
   8: 
   9:     -- App ID with proper data type and validation
  10:     CAST(app_id AS VARCHAR(50)) as app_id,
  11: 
  12:     -- Geographic and location data
  13:     CAST(country AS VARCHAR(255)) as country,
  14:     CAST(guide_id AS VARCHAR(50)) as guide_id,
  15:     CAST(guide_step_id AS BIGINT) as guide_step_id,
  16: 
  17:     -- Latitude with range validation
  18:     CASE
  19:         WHEN latitude BETWEEN -90 AND 90 THEN CAST(latitude AS DOUBLE)
  20:         ELSE NULL
  21:     END as latitude,
  22: 
  23:     -- Longitude with range validation
  24:     CASE
  25:         WHEN longitude BETWEEN -180 AND 180 THEN CAST(longitude AS DOUBLE)
  26:         ELSE NULL
  27:     END as longitude,
  28: 
  29:     CAST(region AS VARCHAR(255)) as region,
  30: 
  31:     -- Remote IP with validation pattern
  32:     CASE
  33:         WHEN remote_ip IS NULL THEN NULL
  34:         WHEN remote_ip ~ '^([0-9]{1,3}\.){3}[0-9]{1,3}$' OR remote_ip ~ '^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$' THEN CAST(remote_ip AS VARCHAR(255))
  35:         ELSE NULL
  36:     END as remote_ip,
  37: 
  38:     CAST(server_name AS VARCHAR(255)) as server_name,
  39: 
  40:     -- Occurred at with timestamp casting and not null constraint
  41:     TRY_CAST(SUBSTRING(timestamp, 1, 23) AS TIMESTAMP) as occurred_at,
  42: 
  43:     CAST(type AS VARCHAR(255)) as type,
  44: 
  45:     -- URL with validation and correction rules
  46:     CASE
  47:         WHEN TRIM(url) = '' THEN NULL
  48:         WHEN url IS NOT NULL AND url ~ '^https?://' THEN TRIM(url)
  49:         ELSE NULL
  50:     END as url,
  51: 
  52:     CAST(user_agent AS VARCHAR(255)) as user_agent,
  53: 
  54:     -- Visitor ID with proper data type and validation
  55:     CAST(visitor_id AS VARCHAR(50)) as visitor_id,
  56: 
  57:     -- Generate a surrogate key using MD5 hash of concatenated fields
  58:     CASE
  59:         WHEN account_id IS NOT NULL AND guide_id IS NOT NULL AND timestamp IS NOT NULL AND visitor_id IS NOT NULL
  60:         THEN MD5(CONCAT(
  61:             COALESCE(CAST(visitor_id AS VARCHAR), ''),
  62:             COALESCE(CAST(timestamp AS VARCHAR), ''),
  63:             COALESCE(CAST(account_id AS VARCHAR), ''),
  64:             COALESCE(server_name, ''),
  65:             COALESCE(CAST(guide_id AS VARCHAR), ''),
  66:             COALESCE(user_agent, ''),
  67:             COALESCE(remote_ip, '')
  68:         ))
  69:         ELSE NULL
  70:     END as guide_event_key
  71: 
  72: FROM raw.guide_event
  73: WHERE
  74:     -- Filter records with severe data quality issues
  75:     account_id IS NOT NULL
  76:     AND account_id != ''
  77:     AND guide_id IS NOT NULL
  78:     AND guide_id != ''
  79:     AND timestamp IS NOT NULL
  80:     AND visitor_id IS NOT NULL
  81:     AND visitor_id != ''
  82:     AND app_id IS NOT NULL
  83:     AND app_id != ''
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.guide_event|gold_vs_initial|True|True|True||
|raw.guide_event|gold_vs_agent|True|True|True||

## 3. agent实际看到的信息与不确定性四档

event 1完整提供本表规则；event 13→14看raw schema；event 19生成staging表达式。未找到支持“所有URL符合契约SQL正则”的完整查询。V1显示前缀匹配15000、DuckDB全匹配0：实际观察到的差异来自规则写法和SQL实现，不能把这15000个URL说成现实中的无效URL。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|key_formula|A|看到了但没提|14|
|url_rule|C|只有通用策略说明|59|

### key_formula：看到了但没提

列清单可见原始事件字段。最终报告的event-key generation只是功能清单，没有说明生成键的具体约定；不把该词视为选择及原因。

事件 **14**，字段`content`；[轨迹原文](../014_trace_impl-002.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/14.json`。
```text
', None, None, None), ('name', 'VARCHAR', 'YES', None, None, None)]

 guide_event [('account_id', 'VARCHAR', 'YES', None, None, None), ('guide_id', 'VARCHAR', 'YES', None, None, None), ('remote_ip', 'VARCHAR', 'YES', None, None, None), ('server_name', 'VARCHAR', 'YES', None, None, None), ('timestamp', 'VARCHAR', 'YES', None, None, None), ('user_agent', 'VARCHAR', 'YES', None, None, None), ('visitor_id', 'VARCHAR', 'YES', None, None, None), ('app_id', 'VARCHAR', 'YES', None, None, None), ('country', 'VARCHAR', 'YES', None, None, None), ('element_path', 'VARCHAR', 'YES', None, None, None), ('event_id', 'BIGINT', 'YES', None, None, None), ('guide_step_id', 'BIGINT', 'YES', None, None, None), ('latitude', 'DOUBLE', 'YES', None, None, None), ('load_time', 'VARCHAR', 'YES', None, None, None), ('longitude', 'DOUBLE', 'YES', None, None, None), ('region', 'VARCHAR', 'YES', None, None, None), ('type', 'VARCHAR', 'YES
```

### url_rule：只有通用策略说明

说明无效可选字段置空的一般策略，未点名guide_event URL正则，也没有证明该规则已落实。

事件 **59**，字段`args.final_thought`；[轨迹原文](../014_trace_impl-002.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`。
```text
Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.
```

已检视61个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：一条查询。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-002.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **1条**（含014复用；本轮新增0条）；核实代价档：**一条查询**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 014-V1 / 核实查询

来源：`records/014_queries_impl-002.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE url IS NOT NULL) urls,count(*) FILTER(WHERE url ~ '^https?://') full_regex,count(*) FILTER(WHERE regexp_matches(url,'^https?://')) prefix_regex,count(*) FILTER(WHERE latitude NOT BETWEEN -90 AND 90) invalid_lat,count(*) FILTER(WHERE account_id IS NULL OR guide_id IS NULL OR timestamp IS NULL OR visitor_id IS NULL OR app_id IS NULL) missing_required FROM raw.guide_event
```
结果原文：
```json
{
  "columns": [
    "n",
    "urls",
    "full_regex",
    "prefix_regex",
    "invalid_lat",
    "missing_required"
  ],
  "rows": [
    [
      15000,
      15000,
      0,
      15000,
      13655,
      0
    ]
  ]
}
```

### 014-D1 / 诊断查询

来源：`records/014_queries_impl-002.json`；数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/pendo.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE url IS NOT NULL) urls,count(*) FILTER(WHERE url ~ '^https?://') full_regex,count(*) FILTER(WHERE regexp_matches(url,'^https?://')) prefix_regex,count(*) FILTER(WHERE latitude NOT BETWEEN -90 AND 90) invalid_lat,count(*) FILTER(WHERE account_id IS NULL OR guide_id IS NULL OR timestamp IS NULL OR visitor_id IS NULL OR app_id IS NULL) missing_required FROM raw.guide_event
```
结果原文：
```json
{
  "columns": [
    "n",
    "urls",
    "full_regex",
    "prefix_regex",
    "invalid_lat",
    "missing_required"
  ],
  "rows": [
    [
      15000,
      15000,
      0,
      15000,
      13655,
      0
    ]
  ]
}
```

### 014-D_raw / 诊断查询

来源：`records/014_queries_impl-002.json`；数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/pendo.duckdb']`。

```sql
SELECT * FROM raw.guide_event
```
结果原文：
```json
{
  "result": {
    "columns_identical": true,
    "agent_rows": 15000,
    "gold_rows": 15000,
    "agent_only_rows": 0,
    "gold_only_rows": 0
  },
  "operation": "Python Counter of full typed rows, exact multiset difference"
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['account_id', 'app_id', 'guide_id', 'visitor_id']`；比较列（与键取并集）：`['account_id', 'app_id', 'country', 'guide_event_key', 'guide_id', 'guide_step_id', 'latitude', 'longitude', 'region', 'remote_ip', 'server_name', 'type', 'url', 'user_agent', 'visitor_id']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：records/014_reruns_impl-002.json

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|key_formula|15000→15000|43655→28655|无|
|url_rule|15000→15000|43655→28655|无|
|latitude_range|15000→15000|43655→30000|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|15000|15000|0|0|0/0|15000|15000|43655|False|
|L1|15000|15000|0|0|0/0|15000|15000|43655|False|
|L2|15000|15000|0|0|0/0|15000|15000|43655|False|
|L3|15000|15000|0|0|0/0|15000|15000|43655|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|app_id|0|0|0|0|
|country|0|0|0|0|
|guide_event_key|15000|15000|15000|15000|
|guide_id|0|0|0|0|
|guide_step_id|0|0|0|0|
|latitude|13655|13655|13655|13655|
|longitude|0|0|0|0|
|region|0|0|0|0|
|remote_ip|0|0|0|0|
|server_name|0|0|0|0|
|type|0|0|0|0|
|url|15000|15000|15000|15000|
|user_agent|0|0|0|0|
|visitor_id|0|0|0|0|

### 重跑 baseline

SQL：`data/014_work/impl-002/baseline.sql`；SHA-256：`8388508da34d60acc3a1ee931015fa1be0dbc093a5c8c16de6061c092f8268b4`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|15000|15000|0|0|0/0|15000|15000|43655|False|
|L1|15000|15000|0|0|0/0|15000|15000|43655|False|
|L2|15000|15000|0|0|0/0|15000|15000|43655|False|
|L3|15000|15000|0|0|0/0|15000|15000|43655|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|app_id|0|0|0|0|
|country|0|0|0|0|
|guide_event_key|15000|15000|15000|15000|
|guide_id|0|0|0|0|
|guide_step_id|0|0|0|0|
|latitude|13655|13655|13655|13655|
|longitude|0|0|0|0|
|region|0|0|0|0|
|remote_ip|0|0|0|0|
|server_name|0|0|0|0|
|type|0|0|0|0|
|url|15000|15000|15000|15000|
|user_agent|0|0|0|0|
|visitor_id|0|0|0|0|

### 重跑 key_formula

SQL：`data/014_work/impl-002/key_formula.sql`；SHA-256：`321dd1b12b1a15b24dd7199f3755b4cb962149666e1ef492c8e6f9b26e89a251`。

唯一原文位置offset=1107，替换前：
```sql
md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(guide_id AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), '')))
```
替换后：
```sql
CASE WHEN account_id IS NOT NULL AND guide_id IS NOT NULL AND timestamp IS NOT NULL AND visitor_id IS NOT NULL THEN md5(concat(coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), ''), coalesce(server_name, ''), coalesce(CAST(guide_id AS VARCHAR), ''), coalesce(user_agent, ''), coalesce(remote_ip, ''))) ELSE NULL END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|15000|15000|0|0|0/0|15000|15000|28655|False|
|L1|15000|15000|0|0|0/0|15000|15000|28655|False|
|L2|15000|15000|0|0|0/0|15000|15000|28655|False|
|L3|15000|15000|0|0|0/0|15000|15000|28655|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|app_id|0|0|0|0|
|country|0|0|0|0|
|guide_event_key|0|0|0|0|
|guide_id|0|0|0|0|
|guide_step_id|0|0|0|0|
|latitude|13655|13655|13655|13655|
|longitude|0|0|0|0|
|region|0|0|0|0|
|remote_ip|0|0|0|0|
|server_name|0|0|0|0|
|type|0|0|0|0|
|url|15000|15000|15000|15000|
|user_agent|0|0|0|0|
|visitor_id|0|0|0|0|

### 重跑 url_rule

SQL：`data/014_work/impl-002/url_rule.sql`；SHA-256：`fbf1b47cc4865abf6d50526cff6e76ceccf3975cbf7013747f625fa6d59c67ab`。

唯一原文位置offset=1015，替换前：
```sql
CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS VARCHAR)), '') END
```
替换后：
```sql
CASE WHEN TRIM(url) = '' THEN NULL WHEN url IS NOT NULL AND url ~ '^https?://' THEN TRIM(url) ELSE NULL END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|15000|15000|0|0|0/0|15000|15000|28655|False|
|L1|15000|15000|0|0|0/0|15000|15000|28655|False|
|L2|15000|15000|0|0|0/0|15000|15000|28655|False|
|L3|15000|15000|0|0|0/0|15000|15000|28655|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|app_id|0|0|0|0|
|country|0|0|0|0|
|guide_event_key|15000|15000|15000|15000|
|guide_id|0|0|0|0|
|guide_step_id|0|0|0|0|
|latitude|13655|13655|13655|13655|
|longitude|0|0|0|0|
|region|0|0|0|0|
|remote_ip|0|0|0|0|
|server_name|0|0|0|0|
|type|0|0|0|0|
|url|0|0|0|0|
|user_agent|0|0|0|0|
|visitor_id|0|0|0|0|

### 重跑 latitude_range

SQL：`data/014_work/impl-002/latitude_range.sql`；SHA-256：`7f75dbcea9ec791e35e5dfe6fa44ee4ca83bfac952ad914b54f7b613e5323d30`。

唯一原文位置offset=767，替换前：
```sql
TRY_CAST(latitude AS DOUBLE)
```
替换后：
```sql
CASE WHEN latitude BETWEEN -90 AND 90 THEN CAST(latitude AS DOUBLE) ELSE NULL END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|15000|15000|0|0|0/0|15000|15000|30000|False|
|L1|15000|15000|0|0|0/0|15000|15000|30000|False|
|L2|15000|15000|0|0|0/0|15000|15000|30000|False|
|L3|15000|15000|0|0|0/0|15000|15000|30000|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|app_id|0|0|0|0|
|country|0|0|0|0|
|guide_event_key|15000|15000|15000|15000|
|guide_id|0|0|0|0|
|guide_step_id|0|0|0|0|
|latitude|0|0|0|0|
|longitude|0|0|0|0|
|region|0|0|0|0|
|remote_ip|0|0|0|0|
|server_name|0|0|0|0|
|type|0|0|0|0|
|url|15000|15000|15000|15000|
|user_agent|0|0|0|0|
|visitor_id|0|0|0|0|

### 复用gold SQL同输入诊断

用于诊断，不是单点修复证据。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|15000|15000|0|0|0/0|0|0|0|True|
|L1|15000|15000|0|0|0/0|0|0|0|True|
|L2|15000|15000|0|0|0/0|0|0|0|True|
|L3|15000|15000|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|app_id|0|0|0|0|
|country|0|0|0|0|
|guide_event_key|0|0|0|0|
|guide_id|0|0|0|0|
|guide_step_id|0|0|0|0|
|latitude|0|0|0|0|
|longitude|0|0|0|0|
|region|0|0|0|0|
|remote_ip|0|0|0|0|
|server_name|0|0|0|0|
|type|0|0|0|0|
|url|0|0|0|0|
|user_agent|0|0|0|0|
|visitor_id|0|0|0|0|

## 5. 逐项类别及U门槛

表级主要原因：**多因并列（C、A）**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|key_formula|A|15000→15000|43655→28655|无|
|url_rule|C|15000→15000|43655→28655|无|

重跑是否满足U第4条件：**主因C/A的严格数值条件否；latitude满足v2第4节U参与因素条件（前三项及减少13655格），不要求一半**。

P（参与因素）：非空latitude均在[-90,90]。014-V1反证13655行；轨迹只有schema，没有范围核实。latitude单改减少13655格但不满足U4的一半门槛，依据v1第4节对参与因素的放宽记U；不是U主因。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：是：C改为C/A并列；latitude从O候选改为U参与因素。。此字段不代替本次与016/017的对比。

## 规则问题

v2第4节已明确U参与因素只需前三项及正改善，latitude不再依赖对v1的例外解释。C/A并列项仍分别记录；URL通用置空说明不代表落实了可执行正则。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
