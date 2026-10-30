# impl-012 / stg_marketo__activity_send_email（全量；v2）

## 1. 差异与结论

email_send_id采用原id还是四列MD5未在契约定义。agent核查过跨活动ID缺乏关联，明确披露了选择；不能用gold的hash作为正确映射的依据。

主要原因：**A**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| send_id | A | 15000 | 15000 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-012_stg_marketo__activity_send_email.md](../../records/022_packages/022_impl-012_stg_marketo__activity_send_email.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-012_stg_marketo__activity_send_email/022_impl-012_stg_marketo__activity_send_email.json`。
- 比较结果：[022_reruns_impl-012_stg_marketo__activity_send_email.json](../022_reruns_impl-012_stg_marketo__activity_send_email.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`。

原件第316–345行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/staging/stg_marketo__activity_send_email.sql`；原件第1–14行。

```sql
   1: SELECT
   2:     CAST(id AS VARCHAR) AS activity_id,
   3:     CAST(lead_id AS VARCHAR) AS lead_id,
   4:     CAST(campaign_id AS VARCHAR) AS campaign_id,
   5:     CAST(email_template_id AS VARCHAR) AS email_template_id,
   6:     TRY_STRPTIME(activity_date, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS activity_timestamp,
   7:     CAST(activity_type_id AS VARCHAR) AS activity_type_id,
   8:     CAST(campaign_run_id AS VARCHAR) AS campaign_run_id,
   9:     CAST(primary_attribute_value AS VARCHAR) AS primary_attribute_value,
  10:     CAST(primary_attribute_value_id AS VARCHAR) AS primary_attribute_value_id,
  11:     CAST(id AS VARCHAR) AS email_send_id
  12: FROM raw.marketo_activity_send_email
  13: WHERE id IS NOT NULL AND lead_id IS NOT NULL AND activity_date IS NOT NULL
  14: QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY activity_date) = 1
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/sql/staging/stg_marketo__activity_send_email.sql`；原件第1–22行。

```sql
   1: -- Staging: Email send activity with surrogate key and data quality transformations
   2: -- Transform raw Marketo data into clean staging table with standardized naming, data types, and quality constraints
   3: -- Note: Converting timezone-aware timestamps to TIMESTAMP by removing timezone info and using UTC
   4: SELECT
   5:     CAST(SUBSTRING(activity_date, 1, LENGTH(activity_date) - 6) AS TIMESTAMP) as activity_timestamp,
   6:     CAST(activity_type_id AS VARCHAR) as activity_type_id,
   7:     CAST(campaign_id AS VARCHAR) as campaign_id,
   8:     CAST(campaign_run_id AS VARCHAR) as campaign_run_id,
   9:     CAST(email_template_id AS VARCHAR) as email_template_id,
  10:     CAST(id AS VARCHAR) as activity_id,
  11:     CAST(lead_id AS VARCHAR) as lead_id,
  12:     CAST(primary_attribute_value AS VARCHAR) as primary_attribute_value,
  13:     CAST(primary_attribute_value_id AS VARCHAR) as primary_attribute_value_id,
  14:     MD5(CONCAT(COALESCE(CAST(primary_attribute_value_id AS VARCHAR), ''),
  15:                COALESCE(CAST(campaign_id AS VARCHAR), ''),
  16:                COALESCE(CAST(campaign_run_id AS VARCHAR), ''),
  17:                COALESCE(CAST(lead_id AS VARCHAR), ''))) as email_send_id
  18: FROM raw.marketo_activity_send_email
  19: WHERE id IS NOT NULL
  20:     AND activity_type_id IS NOT NULL
  21:     AND lead_id IS NOT NULL
  22:     AND activity_date IS NOT NULL
```

## 3. agent看到的材料与不确定性

已检视该题全部57个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 17 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/17.json`。
- event 18 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/18.json`。
- event 21 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/21.json`。
- event 22 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/22.json`。
- event 55 / finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/55.json`。

四档：**针对本表的具体说明**。

原句（见上述最终报告事件）：

```text
原始活动表没有独立 `email_send_id`，发送表使用 `id` 映射；其他活动表也按原始活动 ID 输出 `email_send_id`。源数据未提供可确认的跨活动发送键，因此打开、点击、投递等跨事件连接存在来源标识的局限，计数仍按 contract 在各活动自身分组。
```

## 4. 核实查询与诊断

核实查询共**3条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT 'raw.marketo_activity_send_email' source_table,count(*) rows FROM raw.marketo_activity_send_email
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ... 'raw.marketo_activity_send_email' source_table,count(*) rows FROM raw.marketo_activity_send_email\n                                                                    ^"}
```

### 核实 V2：send_id源列核实

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT count(*) n,count(DISTINCT id) unique_id,count(*) FILTER(WHERE id IS NULL) null_id FROM raw.marketo_activity_send_email
```

```json
{"columns": ["n", "unique_id", "null_id"], "result": [[15000, 15000, 0]]}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`。

```sql
SELECT 'raw.marketo_activity_send_email' source_table,count(*) source_rows FROM raw.marketo_activity_send_email
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.marketo_activity_send_email", 15000]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["activity_id"]`；比较列：`["activity_id", "activity_type_id", "campaign_id", "campaign_run_id", "email_send_id", "email_template_id", "lead_id", "primary_attribute_value", "primary_attribute_value_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 15000/15000 | 0/0 | 0/0 | 15000 | 15000 | 15000 | False |
| L1 | 15000/15000 | 0/0 | 0/0 | 15000 | 15000 | 15000 | False |
| L2 | 15000/15000 | 0/0 | 0/0 | 15000 | 15000 | 15000 | False |
| L3 | 15000/15000 | 0/0 | 0/0 | 15000 | 15000 | 15000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| activity_id | 0 | 0 | 0 | 0 |
| activity_type_id | 0 | 0 | 0 | 0 |
| campaign_id | 0 | 0 | 0 | 0 |
| campaign_run_id | 0 | 0 | 0 | 0 |
| email_send_id | 15000 | 15000 | 15000 | 15000 |
| email_template_id | 0 | 0 | 0 | 0 |
| lead_id | 0 | 0 | 0 | 0 |
| primary_attribute_value | 0 | 0 | 0 | 0 |
| primary_attribute_value_id | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-012_stg_marketo__activity_send_email/baseline.sql`；SHA-256：`7fdf3f17d68fa72409b8afe92c0b22084d99ba91f9f7b21bc33d1f3e0d660867`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 15000/15000 | 0/0 | 0/0 | 15000 | 15000 | 15000 | False |
| L1 | 15000/15000 | 0/0 | 0/0 | 15000 | 15000 | 15000 | False |
| L2 | 15000/15000 | 0/0 | 0/0 | 15000 | 15000 | 15000 | False |
| L3 | 15000/15000 | 0/0 | 0/0 | 15000 | 15000 | 15000 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| activity_id | 0 | 0 | 0 | 0 |
| activity_type_id | 0 | 0 | 0 | 0 |
| campaign_id | 0 | 0 | 0 | 0 |
| campaign_run_id | 0 | 0 | 0 | 0 |
| email_send_id | 15000 | 15000 | 15000 | 15000 |
| email_template_id | 0 | 0 | 0 | 0 |
| lead_id | 0 | 0 | 0 | 0 |
| primary_attribute_value | 0 | 0 | 0 | 0 |
| primary_attribute_value_id | 0 | 0 | 0 | 0 |

### send_id

SQL：`data/022_work/impl-012_stg_marketo__activity_send_email/send_id.sql`；SHA-256：`5a858bdeb2b7f658b1034e0264110ea838639e8c9b7a3e4725198f72aa1f7fed`。

替换offset=563，原表达式所在行约11（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(id AS VARCHAR) AS email_send_id
-- 新
MD5(CONCAT(COALESCE(CAST(primary_attribute_value_id AS VARCHAR), ''),COALESCE(CAST(campaign_id AS VARCHAR), ''),COALESCE(CAST(campaign_run_id AS VARCHAR), ''),COALESCE(CAST(lead_id AS VARCHAR), ''))) AS email_send_id
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 15000/15000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 15000/15000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 15000/15000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 15000/15000 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| activity_id | 0 | 0 | 0 | 0 |
| activity_type_id | 0 | 0 | 0 | 0 |
| campaign_id | 0 | 0 | 0 | 0 |
| campaign_run_id | 0 | 0 | 0 | 0 |
| email_send_id | 0 | 0 | 0 | 0 |
| email_template_id | 0 | 0 | 0 | 0 |
| lead_id | 0 | 0 | 0 | 0 |
| primary_attribute_value | 0 | 0 | 0 | 0 |
| primary_attribute_value_id | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：send_id；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- send_id：A；主项。email_send_id派生方式契约未规定；agent源id、gold组合MD5。（行减少15000，格减少15000）

## 规则问题

无。按v2冻结定义执行。
