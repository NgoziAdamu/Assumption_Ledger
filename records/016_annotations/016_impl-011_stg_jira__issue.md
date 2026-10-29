# impl-011 / stg_jira__issue

## 1. 错在哪里

三个估算/耗时字段优先使用带下划线列，gold优先同名列，契约未规定优先级。

已核实：8000行、23998格。original/remaining/time_spent两种源值分别7999/7999/8000行不等；分别反转COALESCE后减少7999/7999/8000格。行数均8000，按格子主因为time_spent来源优先级A，另外两项A参与因素。契约只给输出字段和类型，数据不存在足以确定哪组代表业务正式估算的证据。

## 2. 依据

- 起点：[013精简材料包](../013_packages/013_impl-011_staging_stg_jira__issue.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml` 第91–146行。
- [原始轨迹转录](../016_trace_impl-011.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-011.json)；[015三方raw核对](../015_raw_impl-011.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: stg_jira__issue
      description: "Cleaned JIRA issues with validated statuses, standardized timestamps, and consistent foreign key references"
      source_table: "raw.issue"
      columns:
        - name: issue_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: issue_key
          data_type: VARCHAR
          constraints: [not_null]
        - name: issue_name
          data_type: VARCHAR
        - name: issue_description
          data_type: VARCHAR
        - name: created_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: resolved_at
          data_type: TIMESTAMP
        - name: updated_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: project_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: assignee_user_id
          data_type: VARCHAR
        - name: reporter_user_id
          data_type: VARCHAR
        - name: creator_user_id
          data_type: VARCHAR
        - name: status_id
          data_type: VARCHAR
        - name: priority_id
          data_type: VARCHAR
        - name: issue_type_id
          data_type: VARCHAR
        - name: resolution_id
          data_type: VARCHAR
        - name: parent_issue_id
          data_type: VARCHAR
        - name: due_date
          data_type: VARCHAR
        - name: environment
          data_type: VARCHAR
        - name: status_changed_at
          data_type: TIMESTAMP
        - name: original_estimate_seconds
          data_type: DOUBLE
        - name: remaining_estimate_seconds
          data_type: DOUBLE
        - name: time_spent_seconds
          data_type: DOUBLE
        - name: work_ratio
          data_type: DOUBLE
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/staging/stg_jira__issue.sql`
```sql
   1: select cast(id as varchar) issue_id, cast(key as varchar) issue_key, summary issue_name, description issue_description, try_cast(regexp_replace(created, ' [+-][0-9]{4}$', '') as timestamp) created_at, try_cast(regexp_replace(resolved, ' [+-][0-9]{4}$', '') as timestamp) resolved_at, try_cast(regexp_replace(updated, ' [+-][0-9]{4}$', '') as timestamp) updated_at, cast(project as varchar) project_id, cast(assignee as varchar) assignee_user_id, cast(reporter as varchar) reporter_user_id, cast(creator as varchar) creator_user_id, cast(status as varchar) status_id, cast(priority as varchar) priority_id, cast(issue_type as varchar) issue_type_id, cast(resolution as varchar) resolution_id, cast(parent_id as varchar) parent_issue_id, due_date, environment, try_cast(regexp_replace(status_category_changed, ' [+-][0-9]{4}$', '') as timestamp) status_changed_at, cast(coalesce(_original_estimate,original_estimate) as double) original_estimate_seconds, cast(coalesce(_remaining_estimate,remaining_estimate) as double) remaining_estimate_seconds, cast(coalesce(_time_spent,time_spent) as double) time_spent_seconds, cast(work_ratio as double) work_ratio from raw.issue where id is not null and created is not null and updated is not null and project is not null qualify row_number() over(partition by id order by updated desc nulls last)=1
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/staging/stg_jira__issue.sql`
```sql
   1: -- Staging table for Jira issues
   2: -- Cleaned JIRA issues with validated statuses, standardized timestamps, and consistent foreign key references
   3: select
   4:     -- Required fields with validation
   5:     TRIM(id) as issue_id,  -- issue_id IS NOT NULL AND TRIM(issue_id) != ''
   6: 
   7:     -- issue_key validation: issue_key = UPPER(TRIM(issue_key))
   8:     CASE
   9:         WHEN key IS NULL OR TRIM(key) = '' THEN NULL
  10:         ELSE UPPER(TRIM(key))
  11:     END as issue_key,
  12: 
  13:     -- issue_name validation: issue_name = TRIM(issue_name)
  14:     CASE
  15:         WHEN summary IS NULL OR TRIM(summary) = '' THEN NULL
  16:         ELSE TRIM(summary)
  17:     END as issue_name,  -- issue_name = TRIM(issue_name)
  18: 
  19:     -- issue_description validation: issue_description = TRIM(issue_description)
  20:     CASE
  21:         WHEN description IS NULL OR TRIM(description) = '' THEN NULL
  22:         ELSE TRIM(description)
  23:     END as issue_description,  -- issue_description = TRIM(issue_description)
  24: 
  25:     -- Timestamp standardization
  26:     CASE
  27:         when created like '% +____' then CAST(SUBSTR(created, 1, LENGTH(created) - 6) AS TIMESTAMP)
  28:         when created like '%+%' then CAST(SUBSTR(created, 1, LENGTH(created) - 6) AS TIMESTAMP)
  29:         WHEN created IS NOT NULL THEN CAST(created AS TIMESTAMP)
  30:         ELSE NULL
  31:     end as created_at,  -- created_at IS NOT NULL
  32: 
  33:     CASE
  34:         when resolved like '% +____' then CAST(SUBSTR(resolved, 1, LENGTH(resolved) - 6) AS TIMESTAMP)
  35:         when resolved like '%+%' then CAST(SUBSTR(resolved, 1, LENGTH(resolved) - 6) AS TIMESTAMP)
  36:         WHEN resolved IS NOT NULL THEN CAST(resolved AS TIMESTAMP)
  37:         ELSE NULL
  38:     end as resolved_at,
  39: 
  40:     CASE
  41:         when updated like '% +____' then CAST(SUBSTR(updated, 1, LENGTH(updated) - 6) AS TIMESTAMP)
  42:         when updated like '%+%' then CAST(SUBSTR(updated, 1, LENGTH(updated) - 6) AS TIMESTAMP)
  43:         WHEN updated IS NOT NULL THEN CAST(updated AS TIMESTAMP)
  44:         ELSE NULL
  45:     end as updated_at,  -- updated_at IS NOT NULL
  46: 
  47:     -- Required project_id validation
  48:     CASE
  49:         WHEN project IS NULL OR TRIM(project) = '' THEN NULL
  50:         ELSE TRIM(project)
  51:     END as project_id,  -- project_id IS NOT NULL
  52: 
  53:     -- Optional foreign key fields
  54:     CASE
  55:         WHEN assignee IS NULL OR TRIM(assignee) = '' THEN NULL
  56:         ELSE TRIM(assignee)
  57:     END as assignee_user_id,
  58: 
  59:     CASE
  60:         WHEN reporter IS NULL OR TRIM(reporter) = '' THEN NULL
  61:         ELSE TRIM(reporter)
  62:     END as reporter_user_id,
  63: 
  64:     CASE
  65:         WHEN creator IS NULL OR TRIM(creator) = '' THEN NULL
  66:         ELSE TRIM(creator)
  67:     END as creator_user_id,
  68: 
  69:     CASE
  70:         WHEN status IS NULL OR TRIM(status) = '' THEN NULL
  71:         ELSE TRIM(status)
  72:     END as status_id,
  73: 
  74:     CASE
  75:         WHEN priority IS NULL OR TRIM(priority) = '' THEN NULL
  76:         ELSE TRIM(priority)
  77:     END as priority_id,
  78: 
  79:     CASE
  80:         WHEN coalesce(cast(work_type as varchar), issue_type) IS NULL OR TRIM(coalesce(cast(work_type as varchar), issue_type)) = '' THEN NULL
  81:         ELSE TRIM(coalesce(cast(work_type as varchar), issue_type))
  82:     END as issue_type_id,
  83: 
  84:     CASE
  85:         WHEN resolution IS NULL OR TRIM(resolution) = '' THEN NULL
  86:         ELSE TRIM(resolution)
  87:     END as resolution_id,
  88: 
  89:     CASE
  90:         WHEN parent_id IS NULL OR TRIM(parent_id) = '' THEN NULL
  91:         ELSE TRIM(parent_id)
  92:     END as parent_issue_id,
  93: 
  94:     -- Additional fields
  95:     due_date,
  96:     environment,
  97: 
  98:     -- Status change timestamp
  99:     CASE
 100:         when status_category_changed like '% +____' then CAST(SUBSTR(status_category_changed, 1, LENGTH(status_category_changed) - 6) AS TIMESTAMP)
 101:         when status_category_changed like '%+%' then CAST(SUBSTR(status_category_changed, 1, LENGTH(status_category_changed) - 6) AS TIMESTAMP)
 102:         WHEN status_category_changed IS NOT NULL THEN CAST(status_category_changed AS TIMESTAMP)
 103:         ELSE NULL
 104:     end as status_changed_at,
 105: 
 106:     -- Work estimate fields
 107:     cast(coalesce(original_estimate, _original_estimate) as double) as original_estimate_seconds,
 108:     cast(coalesce(remaining_estimate, _remaining_estimate) as double) as remaining_estimate_seconds,
 109:     cast(coalesce(time_spent, _time_spent) as double) as time_spent_seconds,
 110:     cast(work_ratio as double) as work_ratio
 111: 
 112: from raw.issue
 113: where id IS NOT NULL AND TRIM(id) != ''  -- Quarantine on failure: issue_id IS NOT NULL AND TRIM(issue_id) != ''
 114:     AND created IS NOT NULL  -- Quarantine on failure: created_at IS NOT NULL
 115:     AND updated IS NOT NULL  -- Quarantine on failure: updated_at IS NOT NULL
 116:     AND project IS NOT NULL AND TRIM(project) != ''  -- Quarantine on failure: project_id IS NOT NULL
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.issue|gold_vs_initial|True|True|True||
|raw.issue|gold_vs_agent|True|True|True||

## 3. agent看过什么

event1完整契约；event9查结构；event11生成COALESCE(_field,field)。event29/31/37修日期，event45检查键，不是估算来源优先级核实。没有找到业务口径或两组耗时来源可信度比较。

区分event实际展示的契约/数据与磁盘上存在的资料；截断输出中未出现的部分不算agent已经看到。核实查询是标注者新增查询，不冒充agent执行过。

## 4. 查询与重跑

核实查询合计 **1条**（含014复用；本轮新增1条）；核实代价档：**需要查业务说明**。诊断不计入5条上限。查询失败与重复执行如实保留。

### 016-V1 / 核实查询

来源：`records/016_queries_impl-011.json`；数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE original_estimate IS DISTINCT FROM _original_estimate) original_diff,count(*) FILTER(WHERE remaining_estimate IS DISTINCT FROM _remaining_estimate) remaining_diff,count(*) FILTER(WHERE time_spent IS DISTINCT FROM _time_spent) spent_diff,min(original_estimate),min(_original_estimate) FROM raw.issue
```
结果原文：
```json
{
  "columns": [
    "n",
    "original_diff",
    "remaining_diff",
    "spent_diff",
    "min(original_estimate)",
    "min(_original_estimate)"
  ],
  "rows": [
    [
      8000,
      7999,
      7999,
      8000,
      1.02,
      1.0
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['issue_id']`；比较列（与键取并集）：`['assignee_user_id', 'creator_user_id', 'due_date', 'environment', 'issue_description', 'issue_id', 'issue_key', 'issue_name', 'issue_type_id', 'original_estimate_seconds', 'parent_issue_id', 'priority_id', 'project_id', 'remaining_estimate_seconds', 'reporter_user_id', 'resolution_id', 'status_id', 'time_spent_seconds', 'work_ratio']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：本次重新执行；原013留存输出另列

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|original_estimate_priority|8000→8000|23998→15999|无|
|remaining_estimate_priority|8000→8000|23998→15999|无|
|time_spent_priority|8000→8000|23998→15998|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|8000|8000|0|0|0/0|8000|8000|23998|False|
|L1|8000|8000|0|0|0/0|8000|8000|23998|False|
|L2|8000|8000|0|0|0/0|8000|8000|23998|False|
|L3|8000|8000|0|0|0/0|8000|8000|23998|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|issue_id|0|0|0|0|
|assignee_user_id|0|0|0|0|
|creator_user_id|0|0|0|0|
|due_date|0|0|0|0|
|environment|0|0|0|0|
|issue_description|0|0|0|0|
|issue_key|0|0|0|0|
|issue_name|0|0|0|0|
|issue_type_id|0|0|0|0|
|original_estimate_seconds|7999|7999|7999|7999|
|parent_issue_id|0|0|0|0|
|priority_id|0|0|0|0|
|project_id|0|0|0|0|
|remaining_estimate_seconds|7999|7999|7999|7999|
|reporter_user_id|0|0|0|0|
|resolution_id|0|0|0|0|
|status_id|0|0|0|0|
|time_spent_seconds|8000|8000|8000|8000|
|work_ratio|0|0|0|0|

### 重跑 baseline

SQL：`data/016_work/impl-011/baseline.sql`；SHA-256：`fc8560dd003186b02c9f969f8eeece8940ac0f81a516e24f8f5130f7e649ee59`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|8000|8000|0|0|0/0|8000|8000|23998|False|
|L1|8000|8000|0|0|0/0|8000|8000|23998|False|
|L2|8000|8000|0|0|0/0|8000|8000|23998|False|
|L3|8000|8000|0|0|0/0|8000|8000|23998|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|issue_id|0|0|0|0|
|assignee_user_id|0|0|0|0|
|creator_user_id|0|0|0|0|
|due_date|0|0|0|0|
|environment|0|0|0|0|
|issue_description|0|0|0|0|
|issue_key|0|0|0|0|
|issue_name|0|0|0|0|
|issue_type_id|0|0|0|0|
|original_estimate_seconds|7999|7999|7999|7999|
|parent_issue_id|0|0|0|0|
|priority_id|0|0|0|0|
|project_id|0|0|0|0|
|remaining_estimate_seconds|7999|7999|7999|7999|
|reporter_user_id|0|0|0|0|
|resolution_id|0|0|0|0|
|status_id|0|0|0|0|
|time_spent_seconds|8000|8000|8000|8000|
|work_ratio|0|0|0|0|

### 重跑 original_estimate_priority

SQL：`data/016_work/impl-011/original_estimate_priority.sql`；SHA-256：`1e1a981caf465fe3043412770ded527a40542b3f22a8e5aeccb8ecd389e89c7f`。

唯一原文位置offset=868，替换前：
```sql
coalesce(_original_estimate,original_estimate)
```
替换后：
```sql
coalesce(original_estimate,_original_estimate)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|8000|8000|0|0|0/0|8000|8000|15999|False|
|L1|8000|8000|0|0|0/0|8000|8000|15999|False|
|L2|8000|8000|0|0|0/0|8000|8000|15999|False|
|L3|8000|8000|0|0|0/0|8000|8000|15999|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|issue_id|0|0|0|0|
|assignee_user_id|0|0|0|0|
|creator_user_id|0|0|0|0|
|due_date|0|0|0|0|
|environment|0|0|0|0|
|issue_description|0|0|0|0|
|issue_key|0|0|0|0|
|issue_name|0|0|0|0|
|issue_type_id|0|0|0|0|
|original_estimate_seconds|0|0|0|0|
|parent_issue_id|0|0|0|0|
|priority_id|0|0|0|0|
|project_id|0|0|0|0|
|remaining_estimate_seconds|7999|7999|7999|7999|
|reporter_user_id|0|0|0|0|
|resolution_id|0|0|0|0|
|status_id|0|0|0|0|
|time_spent_seconds|8000|8000|8000|8000|
|work_ratio|0|0|0|0|

### 重跑 remaining_estimate_priority

SQL：`data/016_work/impl-011/remaining_estimate_priority.sql`；SHA-256：`48da92536c5531652e8e42ab88031fe491dba34480725fe76af9f4d26807cbdf`。

唯一原文位置offset=958，替换前：
```sql
coalesce(_remaining_estimate,remaining_estimate)
```
替换后：
```sql
coalesce(remaining_estimate,_remaining_estimate)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|8000|8000|0|0|0/0|8000|8000|15999|False|
|L1|8000|8000|0|0|0/0|8000|8000|15999|False|
|L2|8000|8000|0|0|0/0|8000|8000|15999|False|
|L3|8000|8000|0|0|0/0|8000|8000|15999|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|issue_id|0|0|0|0|
|assignee_user_id|0|0|0|0|
|creator_user_id|0|0|0|0|
|due_date|0|0|0|0|
|environment|0|0|0|0|
|issue_description|0|0|0|0|
|issue_key|0|0|0|0|
|issue_name|0|0|0|0|
|issue_type_id|0|0|0|0|
|original_estimate_seconds|7999|7999|7999|7999|
|parent_issue_id|0|0|0|0|
|priority_id|0|0|0|0|
|project_id|0|0|0|0|
|remaining_estimate_seconds|0|0|0|0|
|reporter_user_id|0|0|0|0|
|resolution_id|0|0|0|0|
|status_id|0|0|0|0|
|time_spent_seconds|8000|8000|8000|8000|
|work_ratio|0|0|0|0|

### 重跑 time_spent_priority

SQL：`data/016_work/impl-011/time_spent_priority.sql`；SHA-256：`96771130fd630e926d8e52e81841aa76c41f18b510a3d7a4ca46e29dc8b06c4e`。

唯一原文位置offset=1051，替换前：
```sql
coalesce(_time_spent,time_spent)
```
替换后：
```sql
coalesce(time_spent,_time_spent)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|8000|8000|0|0|0/0|8000|8000|15998|False|
|L1|8000|8000|0|0|0/0|8000|8000|15998|False|
|L2|8000|8000|0|0|0/0|8000|8000|15998|False|
|L3|8000|8000|0|0|0/0|8000|8000|15998|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|issue_id|0|0|0|0|
|assignee_user_id|0|0|0|0|
|creator_user_id|0|0|0|0|
|due_date|0|0|0|0|
|environment|0|0|0|0|
|issue_description|0|0|0|0|
|issue_key|0|0|0|0|
|issue_name|0|0|0|0|
|issue_type_id|0|0|0|0|
|original_estimate_seconds|7999|7999|7999|7999|
|parent_issue_id|0|0|0|0|
|priority_id|0|0|0|0|
|project_id|0|0|0|0|
|remaining_estimate_seconds|7999|7999|7999|7999|
|reporter_user_id|0|0|0|0|
|resolution_id|0|0|0|0|
|status_id|0|0|0|0|
|time_spent_seconds|0|0|0|0|
|work_ratio|0|0|0|0|

## 5. 类别、把握及与014对比

- 主要原因：**A**。
- 主因对应单项：time_spent_priority。
- 参与因素：A：original_estimate优先级；A：remaining_estimate优先级。
- 标记：无。
- 把握：**中**。
- 重跑是否满足U第4条件：否：最大单改8000/23998格，不达一半。

两组值不等只能否定等价，不能决定应优先哪列；故A而非U。

与014相比：**不适用：第二批首次标注**

## 规则问题

同类别的三个错误仍分别干预，不因都属于A便合并。time_spent比其余多减少1格，按v1数字规则选主因，不另设实质差异阈值。

2026-10-29用户确认的第3节补充：仅当本表依赖raw满足agent留存=初始、gold不同，且诊断确认影响可评估性时标“不可评估”；gold=初始、agent不同则照常标注，查轨迹改动。不能把两类混为一谈。若gold与agent一致但二者不同于初始（019/020），当前本节点仍可比较；初始差异另记。

共同执行例外：最初指纹快照因外部v0附件已不在原桌面路径而失败；成功的016快照晚于首批私有重跑。已逐文件与015任务前的大小、mtime、SHA-256比较，覆盖原始库的历史指纹无变化；不把晚快照伪称执行前快照。仓库v0与004–015记录保留。
