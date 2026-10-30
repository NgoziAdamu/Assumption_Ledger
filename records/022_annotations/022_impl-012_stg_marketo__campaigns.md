# impl-012 / stg_marketo__campaigns（全量；v2）

## 1. 差异与结论

gold多保留1条空白campaign_name，契约显式delete_row；agent过滤符合契约。

主要原因：**O**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| blank_names | O | 1 | 28 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-012_stg_marketo__campaigns.md](../../records/022_packages/022_impl-012_stg_marketo__campaigns.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-012_stg_marketo__campaigns/022_impl-012_stg_marketo__campaigns.json`。
- 比较结果：[022_reruns_impl-012_stg_marketo__campaigns.json](../022_reruns_impl-012_stg_marketo__campaigns.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`。

原件第82–209行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/staging/stg_marketo__campaigns.sql`；原件第1–34行。

```sql
   1: SELECT
   2:     CAST(id AS VARCHAR) AS campaign_id,
   3:     TRIM(name) AS campaign_name,
   4:     CASE WHEN program_id IS NULL OR program_id ~ '^MAR[0-9]+$' THEN CAST(program_id AS VARCHAR) ELSE NULL END AS program_id,
   5:     CAST(type AS VARCHAR) AS campaign_type,
   6:     COALESCE(CAST(active AS BOOLEAN), FALSE) AS is_active,
   7:     CAST(created_at AS VARCHAR) AS created_timestamp,
   8:     CAST(updated_at AS VARCHAR) AS updated_timestamp,
   9:     CAST(description AS VARCHAR) AS description,
  10:     CAST(workspace_name AS VARCHAR) AS workspace_name,
  11:     CAST(computed_url AS VARCHAR) AS computed_url,
  12:     CAST(flow_id AS VARCHAR) AS flow_id,
  13:     CAST(folder_id AS VARCHAR) AS folder_id,
  14:     CAST(folder_type AS VARCHAR) AS folder_type,
  15:     CAST(is_communication_limit_enabled AS BOOLEAN) AS is_communication_limit_enabled,
  16:     CAST(is_requestable AS BOOLEAN) AS is_requestable,
  17:     CAST(is_system AS BOOLEAN) AS is_system,
  18:     CAST(max_members AS BIGINT) AS max_members,
  19:     CAST(qualification_rule_type AS VARCHAR) AS qualification_rule_type,
  20:     CAST(qualification_rule_interval AS BIGINT) AS qualification_rule_interval,
  21:     CAST(qualification_rule_unit AS VARCHAR) AS qualification_rule_unit,
  22:     CAST(recurrence_start_at AS VARCHAR) AS recurrence_start_at,
  23:     CAST(recurrence_end_at AS VARCHAR) AS recurrence_end_at,
  24:     CAST(recurrence_interval_type AS VARCHAR) AS recurrence_interval_type,
  25:     CAST(recurrence_interval AS BIGINT) AS recurrence_interval,
  26:     CAST(recurrence_weekday_only AS BOOLEAN) AS recurrence_weekday_only,
  27:     CAST(recurrence_day_of_month AS BIGINT) AS recurrence_day_of_month,
  28:     CAST(recurrence_day_of_week AS BIGINT) AS recurrence_day_of_week,
  29:     CAST(recurrence_week_of_month AS BIGINT) AS recurrence_week_of_month,
  30:     CAST(smart_list_id AS VARCHAR) AS smart_list_id,
  31:     CAST(status AS VARCHAR) AS status
  32: FROM raw.marketo_campaign
  33: WHERE id IS NOT NULL AND name IS NOT NULL AND TRIM(name) <> '' AND LENGTH(TRIM(name)) <= 255 AND type IS NOT NULL AND created_at IS NOT NULL AND updated_at IS NOT NULL
  34: QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC NULLS LAST) = 1
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/sql/staging/stg_marketo__campaigns.sql`；原件第1–48行。

```sql
   1: -- Staging: Campaign data with standardized columns and data quality transformations
   2: -- Transform raw Marketo data into clean staging table with standardized naming, data types, and quality constraints
   3: SELECT
   4:     CAST(COALESCE(active, FALSE) AS BOOLEAN) as is_active,
   5:     CAST(created_at AS VARCHAR) as created_timestamp,
   6:     description,
   7:     CAST(id AS VARCHAR) as campaign_id,
   8:     CASE
   9:         WHEN TRIM(name) IS NULL THEN NULL
  10:         WHEN LENGTH(TRIM(name)) > 255 THEN NULL
  11:         ELSE TRIM(name)
  12:     END as campaign_name,
  13:     CASE
  14:         WHEN program_id IS NULL THEN NULL
  15:         WHEN program_id !~ '^MAR[0-9]+$' THEN NULL
  16:         ELSE CAST(program_id AS VARCHAR)
  17:     END as program_id,
  18:     CAST(type AS VARCHAR) as campaign_type,
  19:     CAST(updated_at AS VARCHAR) as updated_timestamp,
  20:     CAST(workspace_name AS VARCHAR) as workspace_name,
  21:     CAST(computed_url AS VARCHAR) as computed_url,
  22:     CAST(flow_id AS VARCHAR) as flow_id,
  23:     CAST(folder_id AS VARCHAR) as folder_id,
  24:     CAST(folder_type AS VARCHAR) as folder_type,
  25:     CAST(is_communication_limit_enabled AS BOOLEAN) as is_communication_limit_enabled,
  26:     CAST(is_requestable AS BOOLEAN) as is_requestable,
  27:     CAST(is_system AS BOOLEAN) as is_system,
  28:     CAST(max_members AS BIGINT) as max_members,
  29:     CAST(qualification_rule_type AS VARCHAR) as qualification_rule_type,
  30:     CAST(qualification_rule_interval AS BIGINT) as qualification_rule_interval,
  31:     CAST(qualification_rule_unit AS VARCHAR) as qualification_rule_unit,
  32:     CAST(recurrence_start_at AS VARCHAR) as recurrence_start_at,
  33:     CAST(recurrence_end_at AS VARCHAR) as recurrence_end_at,
  34:     CAST(recurrence_interval_type AS VARCHAR) as recurrence_interval_type,
  35:     CAST(recurrence_interval AS BIGINT) as recurrence_interval,
  36:     CAST(recurrence_weekday_only AS BOOLEAN) as recurrence_weekday_only,
  37:     CAST(recurrence_day_of_month AS BIGINT) as recurrence_day_of_month,
  38:     CAST(recurrence_day_of_week AS BIGINT) as recurrence_day_of_week,
  39:     CAST(recurrence_week_of_month AS BIGINT) as recurrence_week_of_month,
  40:     CAST(smart_list_id AS VARCHAR) as smart_list_id,
  41:     CAST(status AS VARCHAR) as status
  42: FROM raw.marketo_campaign
  43: WHERE id IS NOT NULL
  44:     AND TRIM(name) IS NOT NULL
  45:     AND type IS NOT NULL
  46:     AND created_at IS NOT NULL
  47:     AND updated_at IS NOT NULL
  48:     AND LENGTH(TRIM(name)) <= 255
```

## 3. agent看到的材料与不确定性

已检视该题全部57个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 55 / finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/55.json`。

四档：**只有通用策略说明**。

原句（见上述最终报告事件）：

```text
依据 staging 契约去除缺少关键 ID/时间/必需属性的行，并对重复主键保留更新时间较新的记录（活动重复时保留较早记录）。这保全了声明的唯一粒度，但剔除记录不会进入后续分析。
```

## 4. 核实查询与诊断

核实查询共**3条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT 'raw.marketo_campaign' source_table,count(*) rows FROM raw.marketo_campaign
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.marketo_campaign' source_table,count(*) rows FROM raw.marketo_campaign\n                                                            ^"}
```

### 核实 V2：空白名称

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT count(*) FILTER(WHERE name IS NOT NULL AND trim(name)='') blanks FROM raw.marketo_campaign
```

```json
{"columns": ["blanks"], "result": [[1]]}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT 'raw.marketo_campaign' source_table,count(*) source_rows FROM raw.marketo_campaign
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.marketo_campaign", 5000]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["campaign_id"]`；比较列：`["campaign_id", "campaign_name", "campaign_type", "computed_url", "created_timestamp", "description", "flow_id", "folder_id", "folder_type", "is_active", "is_communication_limit_enabled", "is_requestable", "is_system", "max_members", "program_id", "qualification_rule_type", "qualification_rule_unit", "recurrence_day_of_month", "recurrence_day_of_week", "recurrence_end_at", "recurrence_interval_type", "recurrence_start_at", "recurrence_week_of_month", "recurrence_weekday_only", "smart_list_id", "status", "updated_timestamp", "workspace_name"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 4996/4997 | 0/1 | 0/0 | 0 | 1 | 28 | False |
| L1 | 4996/4997 | 0/1 | 0/0 | 0 | 1 | 28 | False |
| L2 | 4996/4997 | 0/1 | 0/0 | 0 | 1 | 28 | False |
| L3 | 4996/4997 | 0/1 | 0/0 | 0 | 1 | 28 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| campaign_id | 0 | 0 | 0 | 0 |
| campaign_name | 0 | 0 | 0 | 0 |
| campaign_type | 0 | 0 | 0 | 0 |
| computed_url | 0 | 0 | 0 | 0 |
| created_timestamp | 0 | 0 | 0 | 0 |
| description | 0 | 0 | 0 | 0 |
| flow_id | 0 | 0 | 0 | 0 |
| folder_id | 0 | 0 | 0 | 0 |
| folder_type | 0 | 0 | 0 | 0 |
| is_active | 0 | 0 | 0 | 0 |
| is_communication_limit_enabled | 0 | 0 | 0 | 0 |
| is_requestable | 0 | 0 | 0 | 0 |
| is_system | 0 | 0 | 0 | 0 |
| max_members | 0 | 0 | 0 | 0 |
| program_id | 0 | 0 | 0 | 0 |
| qualification_rule_type | 0 | 0 | 0 | 0 |
| qualification_rule_unit | 0 | 0 | 0 | 0 |
| recurrence_day_of_month | 0 | 0 | 0 | 0 |
| recurrence_day_of_week | 0 | 0 | 0 | 0 |
| recurrence_end_at | 0 | 0 | 0 | 0 |
| recurrence_interval_type | 0 | 0 | 0 | 0 |
| recurrence_start_at | 0 | 0 | 0 | 0 |
| recurrence_week_of_month | 0 | 0 | 0 | 0 |
| recurrence_weekday_only | 0 | 0 | 0 | 0 |
| smart_list_id | 0 | 0 | 0 | 0 |
| status | 0 | 0 | 0 | 0 |
| updated_timestamp | 0 | 0 | 0 | 0 |
| workspace_name | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-012_stg_marketo__campaigns/baseline.sql`；SHA-256：`4c117e0580542961ddfe64e6e5939f75d1aa75ce0072d5ac2490a4ecc77c1197`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 4996/4997 | 0/1 | 0/0 | 0 | 1 | 28 | False |
| L1 | 4996/4997 | 0/1 | 0/0 | 0 | 1 | 28 | False |
| L2 | 4996/4997 | 0/1 | 0/0 | 0 | 1 | 28 | False |
| L3 | 4996/4997 | 0/1 | 0/0 | 0 | 1 | 28 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| campaign_id | 0 | 0 | 0 | 0 |
| campaign_name | 0 | 0 | 0 | 0 |
| campaign_type | 0 | 0 | 0 | 0 |
| computed_url | 0 | 0 | 0 | 0 |
| created_timestamp | 0 | 0 | 0 | 0 |
| description | 0 | 0 | 0 | 0 |
| flow_id | 0 | 0 | 0 | 0 |
| folder_id | 0 | 0 | 0 | 0 |
| folder_type | 0 | 0 | 0 | 0 |
| is_active | 0 | 0 | 0 | 0 |
| is_communication_limit_enabled | 0 | 0 | 0 | 0 |
| is_requestable | 0 | 0 | 0 | 0 |
| is_system | 0 | 0 | 0 | 0 |
| max_members | 0 | 0 | 0 | 0 |
| program_id | 0 | 0 | 0 | 0 |
| qualification_rule_type | 0 | 0 | 0 | 0 |
| qualification_rule_unit | 0 | 0 | 0 | 0 |
| recurrence_day_of_month | 0 | 0 | 0 | 0 |
| recurrence_day_of_week | 0 | 0 | 0 | 0 |
| recurrence_end_at | 0 | 0 | 0 | 0 |
| recurrence_interval_type | 0 | 0 | 0 | 0 |
| recurrence_start_at | 0 | 0 | 0 | 0 |
| recurrence_week_of_month | 0 | 0 | 0 | 0 |
| recurrence_weekday_only | 0 | 0 | 0 | 0 |
| smart_list_id | 0 | 0 | 0 | 0 |
| status | 0 | 0 | 0 | 0 |
| updated_timestamp | 0 | 0 | 0 | 0 |
| workspace_name | 0 | 0 | 0 | 0 |

### blank_names

SQL：`data/022_work/impl-012_stg_marketo__campaigns/blank_names.sql`；SHA-256：`b6c722baf6ddf09d247bce3bf0ed5144b3b177aa8d1c21baab8f3cc9c6e7ebfb`。

替换offset=1879，原表达式所在行约33（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
 AND TRIM(name) <> ''
-- 新

```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 4997/4997 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 4997/4997 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 4997/4997 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 4997/4997 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| campaign_id | 0 | 0 | 0 | 0 |
| campaign_name | 0 | 0 | 0 | 0 |
| campaign_type | 0 | 0 | 0 | 0 |
| computed_url | 0 | 0 | 0 | 0 |
| created_timestamp | 0 | 0 | 0 | 0 |
| description | 0 | 0 | 0 | 0 |
| flow_id | 0 | 0 | 0 | 0 |
| folder_id | 0 | 0 | 0 | 0 |
| folder_type | 0 | 0 | 0 | 0 |
| is_active | 0 | 0 | 0 | 0 |
| is_communication_limit_enabled | 0 | 0 | 0 | 0 |
| is_requestable | 0 | 0 | 0 | 0 |
| is_system | 0 | 0 | 0 | 0 |
| max_members | 0 | 0 | 0 | 0 |
| program_id | 0 | 0 | 0 | 0 |
| qualification_rule_type | 0 | 0 | 0 | 0 |
| qualification_rule_unit | 0 | 0 | 0 | 0 |
| recurrence_day_of_month | 0 | 0 | 0 | 0 |
| recurrence_day_of_week | 0 | 0 | 0 | 0 |
| recurrence_end_at | 0 | 0 | 0 | 0 |
| recurrence_interval_type | 0 | 0 | 0 | 0 |
| recurrence_start_at | 0 | 0 | 0 | 0 |
| recurrence_week_of_month | 0 | 0 | 0 | 0 |
| recurrence_weekday_only | 0 | 0 | 0 | 0 |
| smart_list_id | 0 | 0 | 0 | 0 |
| status | 0 | 0 | 0 | 0 |
| updated_timestamp | 0 | 0 | 0 | 0 |
| workspace_name | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：blank_names；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- blank_names：O；主项。契约显式删除空白campaign_name；gold保留一行。（行减少1，格减少28）

## 规则问题

无。按v2冻结定义执行。
