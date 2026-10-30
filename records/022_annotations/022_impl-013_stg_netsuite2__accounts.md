# impl-013 / stg_netsuite2__accounts（全量；v2）

## 1. 差异与结论

raw accounts无两布尔列，契约没有派生公式；gold从accttype分类推导，agent NULL。按v2“原始表根本没有对应列、填法未规定”归A。

主要原因：**A**；参与因素：无；把握：中；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**格子**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| derive_is_leftside | A | 0 | 184 |
| derive_is_balancesheet | A | 0 | 184 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_stg_netsuite2__accounts.md](../../records/022_packages/022_impl-013_stg_netsuite2__accounts.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_stg_netsuite2__accounts/022_impl-013_stg_netsuite2__accounts.json`。
- 比较结果：[022_reruns_impl-013_stg_netsuite2__accounts.json](../022_reruns_impl-013_stg_netsuite2__accounts.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第30–55行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__accounts.sql`；原件第1–17行。

```sql
   1: WITH source_data AS (
   2:     SELECT
   3:     TRY_CAST(r."id" AS VARCHAR) AS account_id,
   4:     TRY_CAST(r."parent" AS VARCHAR) AS parent_id,
   5:     TRY_CAST(r."acctnumber" AS VARCHAR) AS account_number,
   6:     TRY_CAST(r."fullname" AS VARCHAR) AS name,
   7:     TRY_CAST(r."accttype" AS VARCHAR) AS type_name,
   8:     TRY_CAST(r."generalrate" AS VARCHAR) AS general_rate_type,
   9:     CAST(NULL AS BOOLEAN) AS is_leftside,
  10:     CAST(NULL AS BOOLEAN) AS is_balancesheet
  11:     FROM raw.netsuite2_account_data r
  12: )
  13: SELECT *
  14: FROM source_data
  15: WHERE account_id IS NOT NULL
  16:   AND account_id IS NOT NULL AND LENGTH(CAST(account_id AS VARCHAR)) > 0
  17:   AND name IS NOT NULL
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/staging/stg_netsuite2__accounts.sql`；原件第1–22行。

```sql
   1: with base as (
   2:     select *
   3:     from raw.netsuite2_account_data
   4:     -- Removed date_deleted filter for mock data
   5: ),
   6: 
   7: final as (
   8:     select
   9:         id as account_id,
  10:         parent as parent_id,
  11:         cast(acctnumber as varchar) as account_number,
  12:         fullname as name,
  13:         accttype as type_name,
  14:         generalrate as general_rate_type,
  15:         case when lower(accttype) in ('bank', 'acctrec', 'fixedasset', 'othasset', 'equity') then true else false end as is_leftside,
  16:         case when lower(accttype) in ('bank', 'acctrec', 'fixedasset', 'othasset', 'acctpay', 'credcard', 'othcurrliab', 'longtermliab', 'equity') then true else false end as is_balancesheet
  17:     from base
  18: )
  19: 
  20: select *
  21: from final
  22: where account_id is not null and length(trim(account_id)) > 0
```

## 3. agent看到的材料与不确定性

已检视该题全部67个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 13 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/13.json`。
- event 14 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/14.json`。
- event 15 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/15.json`。

四档：**看到了但没提**。

未找到针对本表主项选择的说明。“看到了但没提”只表示上述实际输出包含相关schema、样例、代码/运行结果；不把写SQL本身或通用功能清单当作具体说明。“没有迹象”不推断agent内部没有意识到。

## 4. 核实查询与诊断

核实查询共**3条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'raw.netsuite2_account_data' source_table,count(*) rows FROM raw.netsuite2_account_data
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.netsuite2_account_data' source_table,count(*) rows FROM raw.netsuite2_account_data\n                                                                  ^"}
```

### 核实 V2：可见字段

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name='netsuite2_account_data' ORDER BY ordinal_position
```

```json
{"columns": ["column_name", "data_type"], "result": [["id", "VARCHAR"], ["id", "VARCHAR"], ["accountsearchdisplayname", "VARCHAR"], ["accountsearchdisplayname", "VARCHAR"], ["accountsearchdisplaynamecopy", "VARCHAR"], ["accountsearchdisplaynamecopy", "VARCHAR"], ["acctnumber", "BIGINT"], ["acctnumber", "BIGINT"], ["accttype", "VARCHAR"], ["accttype", "VARCHAR"], ["billableexpensesacct", "VARCHAR"], ["billableexpensesacct", "VARCHAR"], ["cashflowrate", "VARCHAR"], ["cashflowrate", "VARCHAR"], ["category1099misc", "VARCHAR"], ["category1099misc", "VARCHAR"], ["class", "VARCHAR"], ["class", "VARCHAR"], ["currency", "VARCHAR"], ["currency", "VARCHAR"], ["custrecord_fam_account_showinfixedasset", "VARCHAR"], ["custrecord_fam_account_showinfixedasset", "VARCHAR"], ["date_deleted", "VARCHAR"], ["date_deleted", "VARCHAR"], ["deferralacct", "VARCHAR"], ["deferralacct", "VARCHAR"], ["department", "VARCHAR"], ["department", "VARCHAR"], ["description", "VARCHAR"], ["description", "VARCHAR"], ["displaynamewithhierarchy", "VARCHAR"], ["displaynamewithhierarchy", "VARCHAR"], ["eliminate", "VARCHAR"], ["eliminate", "VARCHAR"], ["externalid", "VARCHAR"], ["externalid", "VARCHAR"], ["fullname", "VARCHAR"], ["fullname", "VARCHAR"], ["generalrate", "VARCHAR"], ["generalrate", "VARCHAR"], ["includechildren", "VARCHAR"], ["includechildren", "VARCHAR"], ["inventory", "VARCHAR"], ["inventory", "VARCHAR"], ["isinactive", "BOOLEAN"], ["isinactive", "BOOLEAN"], ["issummary", "BOOLEAN"], ["issummary", "BOOLEAN"], ["lastmodifieddate", "VARCHAR"], ["lastmodifieddate", "VARCHAR"], ["location", "VARCHAR"], ["location", "VARCHAR"], ["parent", "VARCHAR"], ["parent", "VARCHAR"], ["reconcilewithmatching", "VARCHAR"], ["reconcilewithmatching", "VARCHAR"], ["revalue", "VARCHAR"], ["revalue", "VARCHAR"], ["sbankname", "VARCHAR"], ["sbankname", "VARCHAR"], ["sbankroutingnumber", "VARCHAR"], ["sbankroutingnumber", "VARCHAR"], ["sspecacct", "VARCHAR"], ["sspecacct", "VARCHAR"], ["subsidiary", "VARCHAR"], ["subsidiary", "VARCHAR"], ["eliminate.1", "VARCHAR"], ["eliminate.1", "VARCHAR"]]}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'raw.netsuite2_account_data' source_table,count(*) source_rows FROM raw.netsuite2_account_data
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.netsuite2_account_data", 200]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["account_id"]`；比较列：`["account_id", "account_number", "general_rate_type", "is_balancesheet", "is_leftside", "name", "parent_id", "type_name"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 184/184 | 0/0 | 0/0 | 184 | 184 | 368 | False |
| L1 | 184/184 | 0/0 | 0/0 | 184 | 184 | 368 | False |
| L2 | 184/184 | 0/0 | 0/0 | 184 | 184 | 368 | False |
| L3 | 184/184 | 0/0 | 0/0 | 184 | 184 | 368 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| account_id | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| general_rate_type | 0 | 0 | 0 | 0 |
| is_balancesheet | 184 | 184 | 184 | 184 |
| is_leftside | 184 | 184 | 184 | 184 |
| name | 0 | 0 | 0 | 0 |
| parent_id | 0 | 0 | 0 | 0 |
| type_name | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_stg_netsuite2__accounts/baseline.sql`；SHA-256：`5e2c54c0aa2cbf2607344647cdc16039ec30741001288762649c8d317861b33a`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 184/184 | 0/0 | 0/0 | 184 | 184 | 368 | False |
| L1 | 184/184 | 0/0 | 0/0 | 184 | 184 | 368 | False |
| L2 | 184/184 | 0/0 | 0/0 | 184 | 184 | 368 | False |
| L3 | 184/184 | 0/0 | 0/0 | 184 | 184 | 368 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| account_id | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| general_rate_type | 0 | 0 | 0 | 0 |
| is_balancesheet | 184 | 184 | 184 | 184 |
| is_leftside | 184 | 184 | 184 | 184 |
| name | 0 | 0 | 0 | 0 |
| parent_id | 0 | 0 | 0 | 0 |
| type_name | 0 | 0 | 0 | 0 |

### derive_is_leftside

SQL：`data/022_work/impl-013_stg_netsuite2__accounts/derive_is_leftside.sql`；SHA-256：`40fa2eae2125a903704c3255c9978b476a499908b0ccb83c0571432cf0488a32`。

替换offset=355，原表达式所在行约9（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS BOOLEAN) AS is_leftside
-- 新
lower(r.accttype) IN ('bank','acctrec','fixedasset','othasset','equity') AS is_leftside
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 184/184 | 0/0 | 0/0 | 184 | 184 | 184 | False |
| L1 | 184/184 | 0/0 | 0/0 | 184 | 184 | 184 | False |
| L2 | 184/184 | 0/0 | 0/0 | 184 | 184 | 184 | False |
| L3 | 184/184 | 0/0 | 0/0 | 184 | 184 | 184 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| account_id | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| general_rate_type | 0 | 0 | 0 | 0 |
| is_balancesheet | 184 | 184 | 184 | 184 |
| is_leftside | 0 | 0 | 0 | 0 |
| name | 0 | 0 | 0 | 0 |
| parent_id | 0 | 0 | 0 | 0 |
| type_name | 0 | 0 | 0 | 0 |

### derive_is_balancesheet

SQL：`data/022_work/impl-013_stg_netsuite2__accounts/derive_is_balancesheet.sql`；SHA-256：`16c87862c5135acc50f5911e29391bfb88a89cfb7c74cf99be9ab5dda8b45ae0`。

替换offset=397，原表达式所在行约10（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
CAST(NULL AS BOOLEAN) AS is_balancesheet
-- 新
lower(r.accttype) IN ('bank','acctrec','fixedasset','othasset','acctpay','credcard','othcurrliab','longtermliab','equity') AS is_balancesheet
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 184/184 | 0/0 | 0/0 | 184 | 184 | 184 | False |
| L1 | 184/184 | 0/0 | 0/0 | 184 | 184 | 184 | False |
| L2 | 184/184 | 0/0 | 0/0 | 184 | 184 | 184 | False |
| L3 | 184/184 | 0/0 | 0/0 | 184 | 184 | 184 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| account_id | 0 | 0 | 0 | 0 |
| account_number | 0 | 0 | 0 | 0 |
| general_rate_type | 0 | 0 | 0 | 0 |
| is_balancesheet | 0 | 0 | 0 | 0 |
| is_leftside | 184 | 184 | 184 | 184 |
| name | 0 | 0 | 0 | 0 |
| parent_id | 0 | 0 | 0 | 0 |
| type_name | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：derive_is_leftside,derive_is_balancesheet；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- derive_is_leftside：A；主项。raw无对应布尔列；契约未说明派生映射，gold根据accttype派生。（行减少0，格减少184）
- derive_is_balancesheet：A；主项。raw无对应布尔列；契约未说明派生映射，gold根据accttype派生。（行减少0，格减少184）

## 规则问题

raw无布尔列时A与D/I边界：event15注释说flags lookup，后续未落地；但契约从未定义分类映射，按第3节无对应列的A，不以gold的金融分类作为唯一正确解。
