# impl-013 / stg_netsuite2__customers（全量；v2）

## 1. 差异与结论

gold仅用@/点位置弱校验，保留two@@signs.com、missing@.com；agent按契约正则置NULL。改单处为gold弱校验后L0一致，O。

主要原因：**O**；参与因素：无；把握：高；标记：无。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| loose_email | O | 2 | 2 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_stg_netsuite2__customers.md](../../records/022_packages/022_impl-013_stg_netsuite2__customers.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_stg_netsuite2__customers/022_impl-013_stg_netsuite2__customers.json`。
- 比较结果：[022_reruns_impl-013_stg_netsuite2__customers.json](../022_reruns_impl-013_stg_netsuite2__customers.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第232–279行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__customers.sql`；原件第1–54行。

```sql
   1: WITH source_data AS (
   2:     SELECT
   3:         TRY_CAST(r."id" AS VARCHAR) AS customer_id,
   4:         TRY_CAST(r."entityid" AS VARCHAR) AS entity_id,
   5:         TRY_CAST(r."externalid" AS VARCHAR) AS customer_external_id,
   6:         TRY_CAST(r."parent" AS VARCHAR) AS parent_id,
   7:         TRY_CAST(r."isperson" AS BOOLEAN) AS is_person,
   8:         TRY_CAST(r."altname" AS VARCHAR) AS alt_name,
   9:         TRY_CAST(r."companyname" AS VARCHAR) AS company_name,
  10:         TRY_CAST(r."firstname" AS VARCHAR) AS first_name,
  11:         TRY_CAST(r."lastname" AS VARCHAR) AS last_name,
  12:         TRY_CAST(r."email" AS VARCHAR) AS source_email,
  13:         TRY_CAST(r."phone" AS VARCHAR) AS source_phone,
  14:         TRY_CAST(r."defaultbillingaddress" AS VARCHAR) AS default_billing_address_id,
  15:         TRY_CAST(r."defaultshippingaddress" AS VARCHAR) AS default_shipping_address_id,
  16:         TRY_CAST(r."receivablesaccount" AS VARCHAR) AS receivables_account_id,
  17:         TRY_CAST(r."currency" AS VARCHAR) AS currency_id,
  18:         TRY_CAST(r."firstorderdate" AS DATE) AS date_first_order_at
  19:     FROM raw.netsuite2_customer_data r
  20: ), cleaned AS (
  21:     SELECT *,
  22:         CASE
  23:             WHEN source_email IS NULL THEN NULL
  24:             WHEN regexp_full_match(trim(source_email), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}$')
  25:                 THEN lower(trim(source_email))
  26:             ELSE NULL
  27:         END AS email_address,
  28:         CASE
  29:             WHEN source_phone IS NULL THEN NULL
  30:             WHEN length(trim(source_phone)) BETWEEN 8 AND 20
  31:                 THEN regexp_replace(trim(source_phone), '[^0-9+()-]', '')
  32:             ELSE NULL
  33:         END AS phone_number
  34:     FROM source_data
  35: )
  36: SELECT
  37:     customer_id,
  38:     entity_id,
  39:     customer_external_id,
  40:     parent_id,
  41:     is_person,
  42:     alt_name,
  43:     company_name,
  44:     first_name,
  45:     last_name,
  46:     email_address,
  47:     phone_number,
  48:     default_billing_address_id,
  49:     default_shipping_address_id,
  50:     receivables_account_id,
  51:     currency_id,
  52:     date_first_order_at
  53: FROM cleaned
  54: WHERE customer_id IS NOT NULL
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/staging/stg_netsuite2__customers.sql`；原件第1–37行。

```sql
   1: with base as (
   2:     select *
   3:     from raw.netsuite2_customer_data
   4:     -- Removed date_deleted filter for mock data
   5: ),
   6: 
   7: final as (
   8:     select
   9:         id as customer_id,
  10:         entityid as entity_id,
  11:         externalid as customer_external_id,
  12:         parent as parent_id,
  13:         isperson = 'T' as is_person,
  14:         altname as alt_name,
  15:         companyname as company_name,
  16:         firstname as first_name,
  17:         lastname as last_name,
  18:         case
  19:             when email is null then null
  20:             when strpos(email, '@') > 1 and strpos(email, '.') > strpos(email, '@') then lower(trim(email))
  21:             else null
  22:         end as email_address,
  23:         case
  24:             when phone is null then null
  25:             when length(trim(phone)) >= 8 and length(trim(phone)) <= 20 then regexp_replace(trim(phone), '[^0-9+()-]', '')
  26:             else null
  27:         end as phone_number,
  28:         defaultbillingaddress as default_billing_address_id,
  29:         defaultshippingaddress as default_shipping_address_id,
  30:         receivablesaccount as receivables_account_id,
  31:         currency as currency_id,
  32:         cast(firstorderdate as date) as date_first_order_at
  33:     from base
  34: )
  35: 
  36: select *
  37: from final
```

## 3. agent看到的材料与不确定性

已检视该题全部67个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 53 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/53.json`。
- event 54 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/54.json`。
- event 55 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/55.json`。

四档：**看到了但没提**。

未找到针对本表主项选择的说明。“看到了但没提”只表示上述实际输出包含相关schema、样例、代码/运行结果；不把写SQL本身或通用功能清单当作具体说明。“没有迹象”不推断agent内部没有意识到。

## 4. 核实查询与诊断

核实查询共**3条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'raw.netsuite2_customer_data' source_table,count(*) rows FROM raw.netsuite2_customer_data
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: SELECT 'raw.netsuite2_customer_data' source_table,count(*) rows FROM raw.netsuite2_customer_data\n                                                                   ^"}
```

### 核实 V2：邮箱检验

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE strpos(email,'@')>1 AND strpos(email,'.')>strpos(email,'@') AND NOT regexp_full_match(trim(email),'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}$')) loose_only FROM raw.netsuite2_customer_data
```

```json
{"columns": ["n", "loose_only"], "result": [[2000, 2]]}
```

### 核实 V3：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'raw.netsuite2_customer_data' source_table,count(*) source_rows FROM raw.netsuite2_customer_data
```

```json
{"columns": ["source_table", "source_rows"], "result": [["raw.netsuite2_customer_data", 2000]]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["customer_id"]`；比较列：`["alt_name", "company_name", "currency_id", "customer_external_id", "customer_id", "default_billing_address_id", "default_shipping_address_id", "email_address", "entity_id", "first_name", "is_person", "last_name", "parent_id", "phone_number", "receivables_account_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 2000/2000 | 0/0 | 0/0 | 2 | 2 | 2 | False |
| L1 | 2000/2000 | 0/0 | 0/0 | 2 | 2 | 2 | False |
| L2 | 2000/2000 | 0/0 | 0/0 | 2 | 2 | 2 | False |
| L3 | 2000/2000 | 0/0 | 0/0 | 2 | 2 | 2 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_id | 0 | 0 | 0 | 0 |
| alt_name | 0 | 0 | 0 | 0 |
| company_name | 0 | 0 | 0 | 0 |
| currency_id | 0 | 0 | 0 | 0 |
| customer_external_id | 0 | 0 | 0 | 0 |
| default_billing_address_id | 0 | 0 | 0 | 0 |
| default_shipping_address_id | 0 | 0 | 0 | 0 |
| email_address | 2 | 2 | 2 | 2 |
| entity_id | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| is_person | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| parent_id | 0 | 0 | 0 | 0 |
| phone_number | 0 | 0 | 0 | 0 |
| receivables_account_id | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_stg_netsuite2__customers/baseline.sql`；SHA-256：`22a86f33b6e9e0bded34f8f495d5374597848679fac15ac5d855b3e3613560e6`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 2000/2000 | 0/0 | 0/0 | 2 | 2 | 2 | False |
| L1 | 2000/2000 | 0/0 | 0/0 | 2 | 2 | 2 | False |
| L2 | 2000/2000 | 0/0 | 0/0 | 2 | 2 | 2 | False |
| L3 | 2000/2000 | 0/0 | 0/0 | 2 | 2 | 2 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_id | 0 | 0 | 0 | 0 |
| alt_name | 0 | 0 | 0 | 0 |
| company_name | 0 | 0 | 0 | 0 |
| currency_id | 0 | 0 | 0 | 0 |
| customer_external_id | 0 | 0 | 0 | 0 |
| default_billing_address_id | 0 | 0 | 0 | 0 |
| default_shipping_address_id | 0 | 0 | 0 | 0 |
| email_address | 2 | 2 | 2 | 2 |
| entity_id | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| is_person | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| parent_id | 0 | 0 | 0 | 0 |
| phone_number | 0 | 0 | 0 | 0 |
| receivables_account_id | 0 | 0 | 0 | 0 |

### email_order

SQL：`data/022_work/impl-013_stg_netsuite2__customers/email_order.sql`；SHA-256：`53409375e85dbaf98d112046765baf81c024fa655411cb74f5d33c2b9f2f1987`。

替换offset=1188，原表达式所在行约24（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
regexp_full_match(trim(source_email),
-- 新
regexp_full_match(source_email,
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 2000/2000 | 0/0 | 0/0 | 2 | 2 | 2 | False |
| L1 | 2000/2000 | 0/0 | 0/0 | 2 | 2 | 2 | False |
| L2 | 2000/2000 | 0/0 | 0/0 | 2 | 2 | 2 | False |
| L3 | 2000/2000 | 0/0 | 0/0 | 2 | 2 | 2 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_id | 0 | 0 | 0 | 0 |
| alt_name | 0 | 0 | 0 | 0 |
| company_name | 0 | 0 | 0 | 0 |
| currency_id | 0 | 0 | 0 | 0 |
| customer_external_id | 0 | 0 | 0 | 0 |
| default_billing_address_id | 0 | 0 | 0 | 0 |
| default_shipping_address_id | 0 | 0 | 0 | 0 |
| email_address | 2 | 2 | 2 | 2 |
| entity_id | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| is_person | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| parent_id | 0 | 0 | 0 | 0 |
| phone_number | 0 | 0 | 0 | 0 |
| receivables_account_id | 0 | 0 | 0 | 0 |

### loose_email

SQL：`data/022_work/impl-013_stg_netsuite2__customers/loose_email.sql`；SHA-256：`93e5208814c215fcfabf208a2c03f4cfe31def4d47df8fa755f6e864e4b64331`。

替换offset=1188，原表达式所在行约24（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
regexp_full_match(trim(source_email), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}$')
-- 新
strpos(source_email,'@')>1 AND strpos(source_email,'.')>strpos(source_email,'@')
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 2000/2000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L1 | 2000/2000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L2 | 2000/2000 | 0/0 | 0/0 | 0 | 0 | 0 | True |
| L3 | 2000/2000 | 0/0 | 0/0 | 0 | 0 | 0 | True |

整表首次匹配：L0。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| customer_id | 0 | 0 | 0 | 0 |
| alt_name | 0 | 0 | 0 | 0 |
| company_name | 0 | 0 | 0 | 0 |
| currency_id | 0 | 0 | 0 | 0 |
| customer_external_id | 0 | 0 | 0 | 0 |
| default_billing_address_id | 0 | 0 | 0 | 0 |
| default_shipping_address_id | 0 | 0 | 0 | 0 |
| email_address | 0 | 0 | 0 | 0 |
| entity_id | 0 | 0 | 0 | 0 |
| first_name | 0 | 0 | 0 | 0 |
| is_person | 0 | 0 | 0 | 0 |
| last_name | 0 | 0 | 0 | 0 |
| parent_id | 0 | 0 | 0 | 0 |
| phone_number | 0 | 0 | 0 | 0 |
| receivables_account_id | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：loose_email；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- email_order：C；单修未满足本表所选尺度的参与门槛。契约列出的验证在清洗之前；agent先trim再验证保留空白邮箱。（行减少0，格减少0）
- loose_email：O；主项。gold弱校验保留two@@signs.com和missing@.com；契约正则排除，agent照做。（行减少2，格减少2）

## 规则问题

无。按v2冻结定义执行。
