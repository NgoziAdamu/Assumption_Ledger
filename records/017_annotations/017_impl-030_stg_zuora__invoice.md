# impl-030 / stg_zuora__invoice

## 1. 错在哪里

account_id误取invoice id与四项数值表示差异各1040格并列；另有日期/金额类型差异及错误丢弃5条空日期记录。

已核实：同用2025-10-13共同时间后agent1040行、gold1045行，行规模1045、格子9565。account_id来源、adjustment_amount、credit_balance_adjustment_amount、credit_memo_amount和exchange_rate五项单修均减1040格且行数不降，按v1并列。四项数值表示中agent遵守DOUBLE、gold保留VARCHAR，归O；account来源错误可见数据已明确：raw.account_id关联账户1999行、raw.id关联0行。该项具备U前三项证据但单改仅减1040格，不满足U4；轨迹也不足以确认agent原本知道本表FK应保留而只是手误，故此并列原因暂记X。其他类型干预分别减少1035或5格，归O参与因素。契约row_filter明确允许created_date不可解析，agent额外要求非空；恢复OR NULL分支使5条保留，格子减175，记C参与因素。

## 2. 依据

- 起点：[013精简材料包](../013_packages/013_impl-030_staging_stg_zuora__invoice.md)；不修改既有官方判错状态。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml` 第169–281行。
- [完整轨迹](../017_trace_impl-030.json)，保留事件原文和原始路径；可回查授权归档`traces/dacomp_deimpl_prev.tar.gz`。
- [查询原文及结果](../017_queries_impl-030.json)、[重跑完整记录](../017_reruns_impl-030.json)、[原始表库存](../015_raw_impl-030.json)。
- [新增不确定性字段审计](../017_uncertainty_audit.json)、[本表依赖raw核对](../017_dependency_raw_audit.json)。
- [执行前指纹](../017_input_before.json)、[结束后指纹](../017_input_after.json)。本次前快照完成后才开始标注、查询和重跑。

### 契约原文

```yaml
    - name: stg_zuora__invoice
      description: "Cleaned invoices with safe casting and temporal validity checks; latest snapshot indicator provided."
      source_table: raw.zuora_invoice_data
      columns:
        - name: invoice_id
          data_type: VARCHAR
          source_expression: "id"
        - name: account_id
          data_type: VARCHAR
        - name: adjustment_amount
          data_type: DOUBLE
        - name: amount
          data_type: DOUBLE
          source_expression: "case when nullif(amount,'') is null then null else cast(amount as DOUBLE) end"
        - name: amount_home_currency
          data_type: DOUBLE
          source_expression: "case when nullif(amount_home_currency,'') is null then null else cast(amount_home_currency as DOUBLE) end"
        - name: amount_without_tax
          data_type: BIGINT
        - name: amount_without_tax_home_currency
          data_type: BIGINT
        - name: auto_pay
          data_type: BOOLEAN
        - name: balance
          data_type: DOUBLE
        - name: bill_to_contact_id
          data_type: VARCHAR
        - name: comments
          data_type: VARCHAR
        - name: created_by_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
          source_expression: "case when try_cast(created_date as TIMESTAMP) is null then null when try_cast(created_date as TIMESTAMP) > current_timestamp then null when try_cast(created_date as TIMESTAMP) < timestamp '2000-01-01 00:00:00' then null else cast(created_date as TIMESTAMP) end"
        - name: credit_balance_adjustment_amount
          data_type: DOUBLE
        - name: credit_memo_amount
          data_type: DOUBLE
        - name: default_payment_method_id
          data_type: VARCHAR
        - name: due_date
          data_type: DATE
          source_expression: "try_cast(due_date as DATE)"
        - name: exchange_rate
          data_type: DOUBLE
        - name: exchange_rate_date
          data_type: DATE
        - name: home_currency
          data_type: VARCHAR
        - name: includes_one_time
          data_type: BOOLEAN
        - name: includes_recurring
          data_type: BOOLEAN
        - name: includes_usage
          data_type: BOOLEAN
        - name: invoice_date
          data_type: DATE
          source_expression: "try_cast(invoice_date as DATE)"
        - name: invoice_number
          data_type: VARCHAR
        - name: last_email_sent_date
          data_type: TIMESTAMP
          source_expression: "case when nullif(last_email_sent_date,'') is null then null else cast(last_email_sent_date as TIMESTAMP) end"
        - name: parent_account_id
          data_type: VARCHAR
        - name: payment_amount
          data_type: DOUBLE
          source_expression: "case when nullif(payment_amount,'') is null then null else cast(payment_amount as DOUBLE) end"
        - name: payment_term
          data_type: VARCHAR
        - name: posted_by
          data_type: VARCHAR
        - name: posted_date
          data_type: TIMESTAMP
          source_expression: "cast(posted_date as TIMESTAMP)"
        - name: refund_amount
          data_type: DOUBLE
          source_expression: "case when nullif(refund_amount,'') is null then null else cast(refund_amount as DOUBLE) end"
        - name: sold_to_contact_id
          data_type: VARCHAR
        - name: source
          data_type: VARCHAR
        - name: source_id
          data_type: VARCHAR
        - name: source_type
          data_type: VARCHAR
        - name: status
          data_type: VARCHAR
        - name: target_date
          data_type: DATE
        - name: tax_amount
          data_type: DOUBLE
          source_expression: "case when nullif(tax_amount,'') is null then null else cast(tax_amount as DOUBLE) end"
        - name: tax_status
          data_type: VARCHAR
        - name: transaction_currency
          data_type: VARCHAR
        - name: transferred_to_accounting
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_date
          data_type: TIMESTAMP
          source_expression: "cast(updated_date as TIMESTAMP)"
        - name: is_most_recent_record
          data_type: BOOLEAN
          source_expression: "row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1"
      row_filters:
        - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
          on_failure: delete_row
        - rule: "try_cast(created_date as TIMESTAMP) is null OR (try_cast(created_date as TIMESTAMP) <= current_timestamp AND try_cast(created_date as TIMESTAMP) >= timestamp '2000-01-01 00:00:00')"
          on_failure: delete_row
```

### SQL定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: WITH source_rows AS (
   2:     SELECT *
   3:     FROM raw.zuora_invoice_data
   4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't') AND try_cast(created_date AS timestamp) IS NOT NULL AND try_cast(created_date AS timestamp) <= current_timestamp AND try_cast(created_date AS timestamp) >= timestamp '2000-01-01 00:00:00')
   5: SELECT
   6:         id AS invoice_id,
   7:         try_cast("id" AS VARCHAR) AS account_id,
   8:         try_cast("adjustment_amount" AS DOUBLE) AS adjustment_amount,
   9:         try_cast(nullif(amount, '') AS DOUBLE) AS amount,
  10:         try_cast(nullif(amount_home_currency, '') AS DOUBLE) AS amount_home_currency,
  11:         try_cast("amount_without_tax" AS BIGINT) AS amount_without_tax,
  12:         try_cast("amount_without_tax_home_currency" AS BIGINT) AS amount_without_tax_home_currency,
  13:         try_cast("auto_pay" AS BOOLEAN) AS auto_pay,
  14:         try_cast("balance" AS DOUBLE) AS balance,
  15:         try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
  16:         try_cast("comments" AS VARCHAR) AS comments,
  17:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
  18:         case when try_cast(created_date as TIMESTAMP) is null then null when try_cast(created_date as TIMESTAMP) > current_timestamp then null when try_cast(created_date as TIMESTAMP) < timestamp '2000-01-01 00:00:00' then null else cast(created_date as TIMESTAMP) end AS created_date,
  19:         try_cast("credit_balance_adjustment_amount" AS DOUBLE) AS credit_balance_adjustment_amount,
  20:         try_cast("credit_memo_amount" AS DOUBLE) AS credit_memo_amount,
  21:         try_cast("default_payment_method_id" AS VARCHAR) AS default_payment_method_id,
  22:         try_cast(due_date as DATE) AS due_date,
  23:         try_cast("exchange_rate" AS DOUBLE) AS exchange_rate,
  24:         try_cast("exchange_rate_date" AS DATE) AS exchange_rate_date,
  25:         try_cast("home_currency" AS VARCHAR) AS home_currency,
  26:         try_cast("includes_one_time" AS BOOLEAN) AS includes_one_time,
  27:         try_cast("includes_recurring" AS BOOLEAN) AS includes_recurring,
  28:         try_cast("includes_usage" AS BOOLEAN) AS includes_usage,
  29:         try_cast(invoice_date as DATE) AS invoice_date,
  30:         try_cast("invoice_number" AS VARCHAR) AS invoice_number,
  31:         case when nullif(last_email_sent_date,'') is null then null else try_cast(last_email_sent_date as TIMESTAMP) end AS last_email_sent_date,
  32:         try_cast("parent_account_id" AS VARCHAR) AS parent_account_id,
  33:         try_cast(nullif(payment_amount, '') AS DOUBLE) AS payment_amount,
  34:         try_cast("payment_term" AS VARCHAR) AS payment_term,
  35:         try_cast("posted_by" AS VARCHAR) AS posted_by,
  36:         try_cast(posted_date as TIMESTAMP) AS posted_date,
  37:         try_cast(nullif(refund_amount, '') AS DOUBLE) AS refund_amount,
  38:         try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
  39:         try_cast("source" AS VARCHAR) AS source,
  40:         try_cast("source_id" AS VARCHAR) AS source_id,
  41:         try_cast("source_type" AS VARCHAR) AS source_type,
  42:         try_cast("status" AS VARCHAR) AS status,
  43:         try_cast("target_date" AS DATE) AS target_date,
  44:         try_cast(nullif(tax_amount, '') AS DOUBLE) AS tax_amount,
  45:         try_cast("tax_status" AS VARCHAR) AS tax_status,
  46:         try_cast("transaction_currency" AS VARCHAR) AS transaction_currency,
  47:         try_cast("transferred_to_accounting" AS VARCHAR) AS transferred_to_accounting,
  48:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
  49:         try_cast(updated_date as TIMESTAMP) AS updated_date,
  50:         row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 AS is_most_recent_record
  51: FROM source_rows
```

gold（仅用于定位差异）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
   1: with base as (
   2:     select * from raw.zuora_invoice_data where _fivetran_deleted is null or _fivetran_deleted = false
   3: ),
   4: final as (
   5:     select
   6:         id as invoice_id,
   7:         account_id,
   8:         adjustment_amount,
   9:         case when nullif(amount,'') is null then null else cast(amount as DOUBLE) end as amount,
  10:         case when nullif(amount_home_currency,'') is null then null else cast(amount_home_currency as DOUBLE) end as amount_home_currency,
  11:         amount_without_tax,
  12:         amount_without_tax_home_currency,
  13:         auto_pay,
  14:         balance,
  15:         bill_to_contact_id,
  16:         comments,
  17:         created_by_id,
  18:         -- created_date cleaning: drop future or pre-2000 dates; null if unparsable
  19:         case
  20:             when try_cast(created_date as TIMESTAMP) is null then null
  21:             when try_cast(created_date as TIMESTAMP) > current_timestamp then null
  22:             when try_cast(created_date as TIMESTAMP) < timestamp '2000-01-01 00:00:00' then null
  23:             else cast(created_date as TIMESTAMP)
  24:         end as created_date,
  25:         credit_balance_adjustment_amount,
  26:         credit_memo_amount,
  27:         default_payment_method_id,
  28:         try_cast(due_date as DATE) as due_date,
  29:         exchange_rate,
  30:         exchange_rate_date,
  31:         home_currency,
  32:         includes_one_time,
  33:         includes_recurring,
  34:         includes_usage,
  35:         try_cast(invoice_date as DATE) as invoice_date,
  36:         invoice_number,
  37:         case when nullif(last_email_sent_date,'') is null then null else cast(last_email_sent_date as TIMESTAMP) end as last_email_sent_date,
  38:         parent_account_id,
  39:         case when nullif(payment_amount,'') is null then null else cast(payment_amount as DOUBLE) end as payment_amount,
  40:         payment_term,
  41:         posted_by,
  42:         cast(posted_date as TIMESTAMP) as posted_date,
  43:         case when nullif(refund_amount,'') is null then null else cast(refund_amount as DOUBLE) end as refund_amount,
  44:         sold_to_contact_id,
  45:         source,
  46:         source_id,
  47:         source_type,
  48:         status,
  49:         target_date,
  50:         case when nullif(tax_amount,'') is null then null else cast(tax_amount as DOUBLE) end as tax_amount,
  51:         tax_status,
  52:         transaction_currency,
  53:         transferred_to_accounting,
  54:         updated_by_id,
  55:         cast(updated_date as TIMESTAMP) as updated_date,
  56:         row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 as is_most_recent_record
  57:     from base
  58:     where (
  59:         try_cast(created_date as TIMESTAMP) is null
  60:         or (try_cast(created_date as TIMESTAMP) <= current_timestamp and try_cast(created_date as TIMESTAMP) >= timestamp '2000-01-01 00:00:00')
  61:     )
  62: )
  63: select * from final
```

### 原始数据可评估性

下表复用015的完整表schema/行数/typed行哈希比较，只列本表静态传递依赖及双方SQL直接引用的raw。缺表不当作空表；gold与agent一致但二者不同于初始不自动排除（021/030）。

|依赖raw|比较|类型/列序相同|行数相同|typed行哈希相同|差异原因|
|---|---|---|---|---|---|
|raw.zuora_invoice_data|gold_vs_initial|False|True|False|ordered_columns_or_types_differ,sorted_content_hash_differ|
|raw.zuora_invoice_data|gold_vs_agent|True|True|True||

## 3. agent看过什么

event13→14最初看到打包CSV式列名；event39→40已显示解析后的invoice同时有id与account_id。event44显示通用同名列fallback；event45把多种*_id统一放进pk_alias并映射id，未限定所属表；event71最终报告明确声称Fivetran id映射实体标识。未找到invoice.account_id与账户主表的关联核实，也未找到本表外键保留的明确正确意图陈述。

只把归档实际展示的内容视为已看到；磁盘有文件、命令包含表名或截断掉的部分，不等于看到相应数据值。

### 新增字段：是否意识到或提到相关不确定性

**已提到**。只记录可见表述/信息，不由该档位推定错误类别。

明确说明id映射选择；不等于核实本表invoice id可以当account id。类型方面另说明严格按staging类型输出，但例子不是本表。

event **71**，字段`args.final_thought`；原路径`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/71.json`。
```text
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。非关键不可解析值转为 NULL。
```

event **40**，字段`content`；原路径`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/40.json`。
```text
zuora_invoice_data ['id', '_fivetran_deleted', '_fivetran_synced', 'account_id', 'adjustment_amount', 'amount', 'amount_currency_rounding', 'amount_home_currency', 'amount_without_tax', 'amount_without_tax_currency_rounding', 'amount_without_tax_home_currency', 'auto_pay', 'balance', 'bill_to_contact_id', 'comments', 'created_by_id', 'created_date', 'credit_balance_adjustment_amount', 'default_payment_method_id', 'due_date', 'exchange_rate', 'exchange_rate_date', 'home_currency', 'includes_one_time', 'includes_recurring', 'includes_usage', 'invoice_date', 'invoice_number', 'last_email_sent_date', 'parent_account_id', 'payment_amount', 'payment_term', 'posted_by', 'posted_date', 'provider_exchange_rate_date', 'refund_amount', 'reversed', 'sold_to_contact_id', 'source', 'source_id', 'source_type', 'status', 'target_date', 'tax_amount', 'tax_exempt_amount', 'tax_message', 'tax_status', 'template_id', 'transaction_currency', 'transferred_to_accounting', 'updated_by_id', 'updated_date', 'sequence_set_id', 'credit_memo_amount']

 zuora_contact_data ['id', '_fivetran_deleted', '_fivetran_synced', 'account_id', 'address_1', 'address_2', 'city', 'country', 'county', 'created_by_id', 'created_date', 'description', 'fax', 'first_name', 'home_phone', 'last_name', 'mobile_phone', 'nick_name', 'other_phone', 'other_phone_type', 'personal_email', 'postal_code', 'state', 'tax_region', 'updated_by_id', 'updated_date', 'work_email', 'work_phone']

 zuora_invoice_payment_data ['id', '_fivetran_deleted', '_fivetran_synced', 'account_id', 'account_receivable_accounting_code_id', 'accounting_period_id', 'amount', 'amount_currency_rounding', 'amount_home_currency', 'bill_to_contact_id', 'cash_accounting_code_id', 'created_by_id', 'created_date', 'default_payment_method_id', 'exchange_rate', 'exchange_rate_date', 'home_currency', 'invoice_id', 'journal_entry_id', 'journal_run_id', 'parent_ac
```

归档逐项扫描73个事件；本批thought/args.thought字段均为空，不能由此推断agent没有内部思考。“已提到”的原句来自final_thought中的最终报告；“看到了但没提”依据可见工具返回，不把SQL代码本身当口头说明。长工具输出仅摘录连续原文，截取范围见JSON；不是说agent只看到了这个摘录。

## 4. 查询与重跑

核实查询执行 **2条**（失败尝试也计入）；核实代价档：**多条查询**。每张≤5条，均只查agent当时可见数据。诊断可以查gold，不计入此数。

### V1 / 核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
```sql
SELECT count(*) n,count(*) FILTER(WHERE i.id=i.account_id) id_equal_fk,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data a WHERE a.id=i.account_id)) fk_matches_account,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data a WHERE a.id=i.id)) invoice_id_matches_account,count(*) FILTER(WHERE try_cast(created_date AS TIMESTAMP) IS NULL) invalid_created FROM raw.zuora_invoice_data i
```
结果原文：
```json
{
  "executed_utc": "2026-10-29T11:33:05.885075+00:00",
  "columns": [
    "n",
    "id_equal_fk",
    "fk_matches_account",
    "invoice_id_matches_account",
    "invalid_created"
  ],
  "rows": [
    [
      2004,
      0,
      1999,
      0,
      9
    ]
  ]
}
```

### V2 / 核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
```sql
SELECT count(*) AS nondeleted_invalid_created FROM raw.zuora_invoice_data WHERE coalesce(lower(cast(_fivetran_deleted AS VARCHAR)),'false') NOT IN ('true','1','t') AND try_cast(created_date AS TIMESTAMP) IS NULL
```
结果原文：
```json
{
  "executed_utc": "2026-10-29T11:39:37.214130+00:00",
  "columns": [
    "nondeleted_invalid_created"
  ],
  "rows": [
    [
      5
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['invoice_id']`；原评分比较列：`['account_id', 'adjustment_amount', 'amount', 'amount_home_currency', 'amount_without_tax', 'amount_without_tax_home_currency', 'auto_pay', 'balance', 'bill_to_contact_id', 'comments', 'created_by_id', 'credit_balance_adjustment_amount', 'credit_memo_amount', 'default_payment_method_id', 'due_date', 'exchange_rate', 'exchange_rate_date', 'home_currency', 'includes_one_time', 'includes_recurring', 'includes_usage', 'invoice_date', 'invoice_id', 'invoice_number', 'is_most_recent_record', 'last_email_sent_date', 'parent_account_id', 'payment_amount', 'payment_term', 'posted_by', 'posted_date', 'refund_amount', 'sold_to_contact_id', 'source', 'source_id', 'source_type', 'status', 'target_date', 'tax_amount', 'tax_status', 'transaction_currency', 'transferred_to_accounting', 'updated_by_id', 'updated_date']`。与键取并集，不自行纳入原评分排除列。

全部原数据库以READ_ONLY连接或ATTACH；本次建表和改SQL只在`data/017_work/`。staging用agent留存raw，021/027用gold上游CS。每个试验从相同原SQL独立替换，不累积其他修复。

共同时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 12:00:00+08'", "count": 2}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 0}]`。023/025/028沿原筛查候选日期；030沿010已经验证的兼容2025-10-13日期（不声称唯一执行日）；共同控制先应用到基线及全部干预，不能作为某个局部修复的功劳。

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|account_source|1045→1045|9565→8525|无|
|created_null_allowed|1045→1045|9565→9390|无|
|adjustment_amount_representation|1045→1045|9565→8525|无|
|amount_without_tax_representation|1045→1045|9565→8530|无|
|amount_without_tax_home_currency_representation|1045→1045|9565→8530|无|
|balance_representation|1045→1045|9565→9560|无|
|credit_balance_adjustment_amount_representation|1045→1045|9565→8525|无|
|credit_memo_amount_representation|1045→1045|9565→8525|无|
|exchange_rate_representation|1045→1045|9565→8525|无|
|exchange_rate_date_representation|1045→1045|9565→8530|无|
|target_date_representation|1045→1045|9565→8530|无|

### 原留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1041|1045|1|5|0/0|1040|1046|9609|False|
|L1|1041|1045|1|5|0/0|1040|1046|5441|False|
|L2|1041|1045|1|5|0/0|1040|1046|5425|False|
|L3|1041|1045|1|5|0/0|1040|1046|3355|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|invoice_id|0|0|0|0|
|account_id|1040|1040|1040|1040|
|adjustment_amount|1040|0|0|0|
|amount|0|0|0|0|
|amount_home_currency|0|0|0|0|
|amount_without_tax|1035|1033|1025|1025|
|amount_without_tax_home_currency|1035|1033|1025|1025|
|auto_pay|0|0|0|0|
|balance|5|0|0|0|
|bill_to_contact_id|0|0|0|0|
|comments|0|0|0|0|
|created_by_id|0|0|0|0|
|credit_balance_adjustment_amount|1040|0|0|0|
|credit_memo_amount|1040|1|1|1|
|default_payment_method_id|0|0|0|0|
|due_date|0|0|0|0|
|exchange_rate|1040|0|0|0|
|exchange_rate_date|1035|1035|1035|0|
|home_currency|0|0|0|0|
|includes_one_time|0|0|0|0|
|includes_recurring|0|0|0|0|
|includes_usage|0|0|0|0|
|invoice_date|0|0|0|0|
|invoice_number|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|last_email_sent_date|0|0|0|0|
|parent_account_id|0|0|0|0|
|payment_amount|0|0|0|0|
|payment_term|0|0|0|0|
|posted_by|0|0|0|0|
|posted_date|0|0|0|0|
|refund_amount|0|0|0|0|
|sold_to_contact_id|0|0|0|0|
|source|0|0|0|0|
|source_id|0|0|0|0|
|source_type|0|0|0|0|
|status|0|0|0|0|
|target_date|1035|1035|1035|0|
|tax_amount|0|0|0|0|
|tax_status|0|0|0|0|
|transaction_currency|0|0|0|0|
|transferred_to_accounting|0|0|0|0|
|updated_by_id|0|0|0|0|
|updated_date|0|0|0|0|

### 重跑 baseline

SQL：`data/017_work/impl-030/baseline.sql`；SHA-256：`42f383cb2d81afd4efa2d9d0c9065b49da2dd7606bb9e8266bcd83f993c39f5f`。

同输入、同时间控制、不增加因果改动的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1040|1045|0|5|0/0|1040|1045|9565|False|
|L1|1040|1045|0|5|0/0|1040|1045|5397|False|
|L2|1040|1045|0|5|0/0|1040|1045|5381|False|
|L3|1040|1045|0|5|0/0|1040|1045|3311|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|invoice_id|0|0|0|0|
|account_id|1040|1040|1040|1040|
|adjustment_amount|1040|0|0|0|
|amount|0|0|0|0|
|amount_home_currency|0|0|0|0|
|amount_without_tax|1035|1033|1025|1025|
|amount_without_tax_home_currency|1035|1033|1025|1025|
|auto_pay|0|0|0|0|
|balance|5|0|0|0|
|bill_to_contact_id|0|0|0|0|
|comments|0|0|0|0|
|created_by_id|0|0|0|0|
|credit_balance_adjustment_amount|1040|0|0|0|
|credit_memo_amount|1040|1|1|1|
|default_payment_method_id|0|0|0|0|
|due_date|0|0|0|0|
|exchange_rate|1040|0|0|0|
|exchange_rate_date|1035|1035|1035|0|
|home_currency|0|0|0|0|
|includes_one_time|0|0|0|0|
|includes_recurring|0|0|0|0|
|includes_usage|0|0|0|0|
|invoice_date|0|0|0|0|
|invoice_number|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|last_email_sent_date|0|0|0|0|
|parent_account_id|0|0|0|0|
|payment_amount|0|0|0|0|
|payment_term|0|0|0|0|
|posted_by|0|0|0|0|
|posted_date|0|0|0|0|
|refund_amount|0|0|0|0|
|sold_to_contact_id|0|0|0|0|
|source|0|0|0|0|
|source_id|0|0|0|0|
|source_type|0|0|0|0|
|status|0|0|0|0|
|target_date|1035|1035|1035|0|
|tax_amount|0|0|0|0|
|tax_status|0|0|0|0|
|transaction_currency|0|0|0|0|
|transferred_to_accounting|0|0|0|0|
|updated_by_id|0|0|0|0|
|updated_date|0|0|0|0|

### 重跑 account_source

SQL：`data/017_work/impl-030/account_source.sql`；SHA-256：`19f7e90f482b43e57784aadd948e89445329cd208d76b225449e9afd53742186`。

唯一替换位置offset=413；原文：
```sql
try_cast("id" AS VARCHAR) AS account_id
```
新文：
```sql
try_cast("account_id" AS VARCHAR) AS account_id
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1040|1045|0|5|0/0|1040|1045|8525|False|
|L1|1040|1045|0|5|0/0|1036|1041|4357|False|
|L2|1040|1045|0|5|0/0|1036|1041|4341|False|
|L3|1040|1045|0|5|0/0|1026|1031|2271|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|invoice_id|0|0|0|0|
|account_id|0|0|0|0|
|adjustment_amount|1040|0|0|0|
|amount|0|0|0|0|
|amount_home_currency|0|0|0|0|
|amount_without_tax|1035|1033|1025|1025|
|amount_without_tax_home_currency|1035|1033|1025|1025|
|auto_pay|0|0|0|0|
|balance|5|0|0|0|
|bill_to_contact_id|0|0|0|0|
|comments|0|0|0|0|
|created_by_id|0|0|0|0|
|credit_balance_adjustment_amount|1040|0|0|0|
|credit_memo_amount|1040|1|1|1|
|default_payment_method_id|0|0|0|0|
|due_date|0|0|0|0|
|exchange_rate|1040|0|0|0|
|exchange_rate_date|1035|1035|1035|0|
|home_currency|0|0|0|0|
|includes_one_time|0|0|0|0|
|includes_recurring|0|0|0|0|
|includes_usage|0|0|0|0|
|invoice_date|0|0|0|0|
|invoice_number|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|last_email_sent_date|0|0|0|0|
|parent_account_id|0|0|0|0|
|payment_amount|0|0|0|0|
|payment_term|0|0|0|0|
|posted_by|0|0|0|0|
|posted_date|0|0|0|0|
|refund_amount|0|0|0|0|
|sold_to_contact_id|0|0|0|0|
|source|0|0|0|0|
|source_id|0|0|0|0|
|source_type|0|0|0|0|
|status|0|0|0|0|
|target_date|1035|1035|1035|0|
|tax_amount|0|0|0|0|
|tax_status|0|0|0|0|
|transaction_currency|0|0|0|0|
|transferred_to_accounting|0|0|0|0|
|updated_by_id|0|0|0|0|
|updated_date|0|0|0|0|

### 重跑 created_null_allowed

SQL：`data/017_work/impl-030/created_null_allowed.sql`；SHA-256：`94ddf6ab6e6ab438dc7cc8614189eb6139e5d05cb56d1703e3dfed47aa72ab96`。

唯一替换位置offset=168；原文：
```sql
try_cast(created_date AS timestamp) IS NOT NULL AND try_cast(created_date AS timestamp) <= TIMESTAMPTZ '2025-10-13 12:00:00+08' AND try_cast(created_date AS timestamp) >= timestamp '2000-01-01 00:00:00'
```
新文：
```sql
(try_cast(created_date AS timestamp) IS NULL OR (try_cast(created_date AS timestamp) <= TIMESTAMPTZ '2025-10-13 12:00:00+08' AND try_cast(created_date AS timestamp) >= timestamp '2000-01-01 00:00:00'))
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1045|1045|0|0|0/0|1045|1045|9390|False|
|L1|1045|1045|0|0|0/0|1045|1045|5202|False|
|L2|1045|1045|0|0|0/0|1045|1045|5186|False|
|L3|1045|1045|0|0|0/0|1045|1045|3106|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|invoice_id|0|0|0|0|
|account_id|1045|1045|1045|1045|
|adjustment_amount|1045|0|0|0|
|amount|0|0|0|0|
|amount_home_currency|0|0|0|0|
|amount_without_tax|1040|1038|1030|1030|
|amount_without_tax_home_currency|1040|1038|1030|1030|
|auto_pay|0|0|0|0|
|balance|5|0|0|0|
|bill_to_contact_id|0|0|0|0|
|comments|0|0|0|0|
|created_by_id|0|0|0|0|
|credit_balance_adjustment_amount|1045|0|0|0|
|credit_memo_amount|1045|1|1|1|
|default_payment_method_id|0|0|0|0|
|due_date|0|0|0|0|
|exchange_rate|1045|0|0|0|
|exchange_rate_date|1040|1040|1040|0|
|home_currency|0|0|0|0|
|includes_one_time|0|0|0|0|
|includes_recurring|0|0|0|0|
|includes_usage|0|0|0|0|
|invoice_date|0|0|0|0|
|invoice_number|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|last_email_sent_date|0|0|0|0|
|parent_account_id|0|0|0|0|
|payment_amount|0|0|0|0|
|payment_term|0|0|0|0|
|posted_by|0|0|0|0|
|posted_date|0|0|0|0|
|refund_amount|0|0|0|0|
|sold_to_contact_id|0|0|0|0|
|source|0|0|0|0|
|source_id|0|0|0|0|
|source_type|0|0|0|0|
|status|0|0|0|0|
|target_date|1040|1040|1040|0|
|tax_amount|0|0|0|0|
|tax_status|0|0|0|0|
|transaction_currency|0|0|0|0|
|transferred_to_accounting|0|0|0|0|
|updated_by_id|0|0|0|0|
|updated_date|0|0|0|0|

### 重跑 adjustment_amount_representation

SQL：`data/017_work/impl-030/adjustment_amount_representation.sql`；SHA-256：`a1c4aaa03fb22f23db7d2af60f3993f1b1ba0382d671e3fdeddcf89f5242d50c`。

唯一替换位置offset=462；原文：
```sql
try_cast("adjustment_amount" AS DOUBLE) AS adjustment_amount
```
新文：
```sql
"adjustment_amount" AS adjustment_amount
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1040|1045|0|5|0/0|1040|1045|8525|False|
|L1|1040|1045|0|5|0/0|1040|1045|5397|False|
|L2|1040|1045|0|5|0/0|1040|1045|5381|False|
|L3|1040|1045|0|5|0/0|1040|1045|3311|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|invoice_id|0|0|0|0|
|account_id|1040|1040|1040|1040|
|adjustment_amount|0|0|0|0|
|amount|0|0|0|0|
|amount_home_currency|0|0|0|0|
|amount_without_tax|1035|1033|1025|1025|
|amount_without_tax_home_currency|1035|1033|1025|1025|
|auto_pay|0|0|0|0|
|balance|5|0|0|0|
|bill_to_contact_id|0|0|0|0|
|comments|0|0|0|0|
|created_by_id|0|0|0|0|
|credit_balance_adjustment_amount|1040|0|0|0|
|credit_memo_amount|1040|1|1|1|
|default_payment_method_id|0|0|0|0|
|due_date|0|0|0|0|
|exchange_rate|1040|0|0|0|
|exchange_rate_date|1035|1035|1035|0|
|home_currency|0|0|0|0|
|includes_one_time|0|0|0|0|
|includes_recurring|0|0|0|0|
|includes_usage|0|0|0|0|
|invoice_date|0|0|0|0|
|invoice_number|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|last_email_sent_date|0|0|0|0|
|parent_account_id|0|0|0|0|
|payment_amount|0|0|0|0|
|payment_term|0|0|0|0|
|posted_by|0|0|0|0|
|posted_date|0|0|0|0|
|refund_amount|0|0|0|0|
|sold_to_contact_id|0|0|0|0|
|source|0|0|0|0|
|source_id|0|0|0|0|
|source_type|0|0|0|0|
|status|0|0|0|0|
|target_date|1035|1035|1035|0|
|tax_amount|0|0|0|0|
|tax_status|0|0|0|0|
|transaction_currency|0|0|0|0|
|transferred_to_accounting|0|0|0|0|
|updated_by_id|0|0|0|0|
|updated_date|0|0|0|0|

### 重跑 amount_without_tax_representation

SQL：`data/017_work/impl-030/amount_without_tax_representation.sql`；SHA-256：`5dec1088e322c1d4cbb8abb5392a429f370359db191e591a0f3739676bf27d11`。

唯一替换位置offset=676；原文：
```sql
try_cast("amount_without_tax" AS BIGINT) AS amount_without_tax
```
新文：
```sql
"amount_without_tax" AS amount_without_tax
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1040|1045|0|5|0/0|1040|1045|8530|False|
|L1|1040|1045|0|5|0/0|1040|1045|4364|False|
|L2|1040|1045|0|5|0/0|1040|1045|4356|False|
|L3|1040|1045|0|5|0/0|1040|1045|2286|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|invoice_id|0|0|0|0|
|account_id|1040|1040|1040|1040|
|adjustment_amount|1040|0|0|0|
|amount|0|0|0|0|
|amount_home_currency|0|0|0|0|
|amount_without_tax|0|0|0|0|
|amount_without_tax_home_currency|1035|1033|1025|1025|
|auto_pay|0|0|0|0|
|balance|5|0|0|0|
|bill_to_contact_id|0|0|0|0|
|comments|0|0|0|0|
|created_by_id|0|0|0|0|
|credit_balance_adjustment_amount|1040|0|0|0|
|credit_memo_amount|1040|1|1|1|
|default_payment_method_id|0|0|0|0|
|due_date|0|0|0|0|
|exchange_rate|1040|0|0|0|
|exchange_rate_date|1035|1035|1035|0|
|home_currency|0|0|0|0|
|includes_one_time|0|0|0|0|
|includes_recurring|0|0|0|0|
|includes_usage|0|0|0|0|
|invoice_date|0|0|0|0|
|invoice_number|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|last_email_sent_date|0|0|0|0|
|parent_account_id|0|0|0|0|
|payment_amount|0|0|0|0|
|payment_term|0|0|0|0|
|posted_by|0|0|0|0|
|posted_date|0|0|0|0|
|refund_amount|0|0|0|0|
|sold_to_contact_id|0|0|0|0|
|source|0|0|0|0|
|source_id|0|0|0|0|
|source_type|0|0|0|0|
|status|0|0|0|0|
|target_date|1035|1035|1035|0|
|tax_amount|0|0|0|0|
|tax_status|0|0|0|0|
|transaction_currency|0|0|0|0|
|transferred_to_accounting|0|0|0|0|
|updated_by_id|0|0|0|0|
|updated_date|0|0|0|0|

### 重跑 amount_without_tax_home_currency_representation

SQL：`data/017_work/impl-030/amount_without_tax_home_currency_representation.sql`；SHA-256：`01bfd704e841c658e95dd682648404a678205a0d72a51f376631d6e6cb8cff55`。

唯一替换位置offset=748；原文：
```sql
try_cast("amount_without_tax_home_currency" AS BIGINT) AS amount_without_tax_home_currency
```
新文：
```sql
"amount_without_tax_home_currency" AS amount_without_tax_home_currency
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1040|1045|0|5|0/0|1040|1045|8530|False|
|L1|1040|1045|0|5|0/0|1040|1045|4364|False|
|L2|1040|1045|0|5|0/0|1040|1045|4356|False|
|L3|1040|1045|0|5|0/0|1040|1045|2286|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|invoice_id|0|0|0|0|
|account_id|1040|1040|1040|1040|
|adjustment_amount|1040|0|0|0|
|amount|0|0|0|0|
|amount_home_currency|0|0|0|0|
|amount_without_tax|1035|1033|1025|1025|
|amount_without_tax_home_currency|0|0|0|0|
|auto_pay|0|0|0|0|
|balance|5|0|0|0|
|bill_to_contact_id|0|0|0|0|
|comments|0|0|0|0|
|created_by_id|0|0|0|0|
|credit_balance_adjustment_amount|1040|0|0|0|
|credit_memo_amount|1040|1|1|1|
|default_payment_method_id|0|0|0|0|
|due_date|0|0|0|0|
|exchange_rate|1040|0|0|0|
|exchange_rate_date|1035|1035|1035|0|
|home_currency|0|0|0|0|
|includes_one_time|0|0|0|0|
|includes_recurring|0|0|0|0|
|includes_usage|0|0|0|0|
|invoice_date|0|0|0|0|
|invoice_number|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|last_email_sent_date|0|0|0|0|
|parent_account_id|0|0|0|0|
|payment_amount|0|0|0|0|
|payment_term|0|0|0|0|
|posted_by|0|0|0|0|
|posted_date|0|0|0|0|
|refund_amount|0|0|0|0|
|sold_to_contact_id|0|0|0|0|
|source|0|0|0|0|
|source_id|0|0|0|0|
|source_type|0|0|0|0|
|status|0|0|0|0|
|target_date|1035|1035|1035|0|
|tax_amount|0|0|0|0|
|tax_status|0|0|0|0|
|transaction_currency|0|0|0|0|
|transferred_to_accounting|0|0|0|0|
|updated_by_id|0|0|0|0|
|updated_date|0|0|0|0|

### 重跑 balance_representation

SQL：`data/017_work/impl-030/balance_representation.sql`；SHA-256：`3ff8acf5d537304785e2f8909d37af24847aeec46ef65442e0a61a50319813b6`。

唯一替换位置offset=901；原文：
```sql
try_cast("balance" AS DOUBLE) AS balance
```
新文：
```sql
"balance" AS balance
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1040|1045|0|5|0/0|1040|1045|9560|False|
|L1|1040|1045|0|5|0/0|1040|1045|5397|False|
|L2|1040|1045|0|5|0/0|1040|1045|5381|False|
|L3|1040|1045|0|5|0/0|1040|1045|3311|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|invoice_id|0|0|0|0|
|account_id|1040|1040|1040|1040|
|adjustment_amount|1040|0|0|0|
|amount|0|0|0|0|
|amount_home_currency|0|0|0|0|
|amount_without_tax|1035|1033|1025|1025|
|amount_without_tax_home_currency|1035|1033|1025|1025|
|auto_pay|0|0|0|0|
|balance|0|0|0|0|
|bill_to_contact_id|0|0|0|0|
|comments|0|0|0|0|
|created_by_id|0|0|0|0|
|credit_balance_adjustment_amount|1040|0|0|0|
|credit_memo_amount|1040|1|1|1|
|default_payment_method_id|0|0|0|0|
|due_date|0|0|0|0|
|exchange_rate|1040|0|0|0|
|exchange_rate_date|1035|1035|1035|0|
|home_currency|0|0|0|0|
|includes_one_time|0|0|0|0|
|includes_recurring|0|0|0|0|
|includes_usage|0|0|0|0|
|invoice_date|0|0|0|0|
|invoice_number|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|last_email_sent_date|0|0|0|0|
|parent_account_id|0|0|0|0|
|payment_amount|0|0|0|0|
|payment_term|0|0|0|0|
|posted_by|0|0|0|0|
|posted_date|0|0|0|0|
|refund_amount|0|0|0|0|
|sold_to_contact_id|0|0|0|0|
|source|0|0|0|0|
|source_id|0|0|0|0|
|source_type|0|0|0|0|
|status|0|0|0|0|
|target_date|1035|1035|1035|0|
|tax_amount|0|0|0|0|
|tax_status|0|0|0|0|
|transaction_currency|0|0|0|0|
|transferred_to_accounting|0|0|0|0|
|updated_by_id|0|0|0|0|
|updated_date|0|0|0|0|

### 重跑 credit_balance_adjustment_amount_representation

SQL：`data/017_work/impl-030/credit_balance_adjustment_amount_representation.sql`；SHA-256：`13d364301103d85519a2eb780b31d4f746ea9a93253b41efb475b5bdbafa75cd`。

唯一替换位置offset=1445；原文：
```sql
try_cast("credit_balance_adjustment_amount" AS DOUBLE) AS credit_balance_adjustment_amount
```
新文：
```sql
"credit_balance_adjustment_amount" AS credit_balance_adjustment_amount
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1040|1045|0|5|0/0|1040|1045|8525|False|
|L1|1040|1045|0|5|0/0|1040|1045|5397|False|
|L2|1040|1045|0|5|0/0|1040|1045|5381|False|
|L3|1040|1045|0|5|0/0|1040|1045|3311|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|invoice_id|0|0|0|0|
|account_id|1040|1040|1040|1040|
|adjustment_amount|1040|0|0|0|
|amount|0|0|0|0|
|amount_home_currency|0|0|0|0|
|amount_without_tax|1035|1033|1025|1025|
|amount_without_tax_home_currency|1035|1033|1025|1025|
|auto_pay|0|0|0|0|
|balance|5|0|0|0|
|bill_to_contact_id|0|0|0|0|
|comments|0|0|0|0|
|created_by_id|0|0|0|0|
|credit_balance_adjustment_amount|0|0|0|0|
|credit_memo_amount|1040|1|1|1|
|default_payment_method_id|0|0|0|0|
|due_date|0|0|0|0|
|exchange_rate|1040|0|0|0|
|exchange_rate_date|1035|1035|1035|0|
|home_currency|0|0|0|0|
|includes_one_time|0|0|0|0|
|includes_recurring|0|0|0|0|
|includes_usage|0|0|0|0|
|invoice_date|0|0|0|0|
|invoice_number|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|last_email_sent_date|0|0|0|0|
|parent_account_id|0|0|0|0|
|payment_amount|0|0|0|0|
|payment_term|0|0|0|0|
|posted_by|0|0|0|0|
|posted_date|0|0|0|0|
|refund_amount|0|0|0|0|
|sold_to_contact_id|0|0|0|0|
|source|0|0|0|0|
|source_id|0|0|0|0|
|source_type|0|0|0|0|
|status|0|0|0|0|
|target_date|1035|1035|1035|0|
|tax_amount|0|0|0|0|
|tax_status|0|0|0|0|
|transaction_currency|0|0|0|0|
|transferred_to_accounting|0|0|0|0|
|updated_by_id|0|0|0|0|
|updated_date|0|0|0|0|

### 重跑 credit_memo_amount_representation

SQL：`data/017_work/impl-030/credit_memo_amount_representation.sql`；SHA-256：`7b7edda4733bf1522b84c3268ca85e60db836edc9b2dba876f04f0ea2d2f1f7e`。

唯一替换位置offset=1545；原文：
```sql
try_cast("credit_memo_amount" AS DOUBLE) AS credit_memo_amount
```
新文：
```sql
"credit_memo_amount" AS credit_memo_amount
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1040|1045|0|5|0/0|1040|1045|8525|False|
|L1|1040|1045|0|5|0/0|1040|1045|5396|False|
|L2|1040|1045|0|5|0/0|1040|1045|5380|False|
|L3|1040|1045|0|5|0/0|1040|1045|3310|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|invoice_id|0|0|0|0|
|account_id|1040|1040|1040|1040|
|adjustment_amount|1040|0|0|0|
|amount|0|0|0|0|
|amount_home_currency|0|0|0|0|
|amount_without_tax|1035|1033|1025|1025|
|amount_without_tax_home_currency|1035|1033|1025|1025|
|auto_pay|0|0|0|0|
|balance|5|0|0|0|
|bill_to_contact_id|0|0|0|0|
|comments|0|0|0|0|
|created_by_id|0|0|0|0|
|credit_balance_adjustment_amount|1040|0|0|0|
|credit_memo_amount|0|0|0|0|
|default_payment_method_id|0|0|0|0|
|due_date|0|0|0|0|
|exchange_rate|1040|0|0|0|
|exchange_rate_date|1035|1035|1035|0|
|home_currency|0|0|0|0|
|includes_one_time|0|0|0|0|
|includes_recurring|0|0|0|0|
|includes_usage|0|0|0|0|
|invoice_date|0|0|0|0|
|invoice_number|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|last_email_sent_date|0|0|0|0|
|parent_account_id|0|0|0|0|
|payment_amount|0|0|0|0|
|payment_term|0|0|0|0|
|posted_by|0|0|0|0|
|posted_date|0|0|0|0|
|refund_amount|0|0|0|0|
|sold_to_contact_id|0|0|0|0|
|source|0|0|0|0|
|source_id|0|0|0|0|
|source_type|0|0|0|0|
|status|0|0|0|0|
|target_date|1035|1035|1035|0|
|tax_amount|0|0|0|0|
|tax_status|0|0|0|0|
|transaction_currency|0|0|0|0|
|transferred_to_accounting|0|0|0|0|
|updated_by_id|0|0|0|0|
|updated_date|0|0|0|0|

### 重跑 exchange_rate_representation

SQL：`data/017_work/impl-030/exchange_rate_representation.sql`；SHA-256：`8fa80c8df8fe317a776b4461b6e9b50af30281987a3ce48e452bec63c9cb070e`。

唯一替换位置offset=1752；原文：
```sql
try_cast("exchange_rate" AS DOUBLE) AS exchange_rate
```
新文：
```sql
"exchange_rate" AS exchange_rate
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1040|1045|0|5|0/0|1040|1045|8525|False|
|L1|1040|1045|0|5|0/0|1040|1045|5397|False|
|L2|1040|1045|0|5|0/0|1040|1045|5381|False|
|L3|1040|1045|0|5|0/0|1040|1045|3311|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|invoice_id|0|0|0|0|
|account_id|1040|1040|1040|1040|
|adjustment_amount|1040|0|0|0|
|amount|0|0|0|0|
|amount_home_currency|0|0|0|0|
|amount_without_tax|1035|1033|1025|1025|
|amount_without_tax_home_currency|1035|1033|1025|1025|
|auto_pay|0|0|0|0|
|balance|5|0|0|0|
|bill_to_contact_id|0|0|0|0|
|comments|0|0|0|0|
|created_by_id|0|0|0|0|
|credit_balance_adjustment_amount|1040|0|0|0|
|credit_memo_amount|1040|1|1|1|
|default_payment_method_id|0|0|0|0|
|due_date|0|0|0|0|
|exchange_rate|0|0|0|0|
|exchange_rate_date|1035|1035|1035|0|
|home_currency|0|0|0|0|
|includes_one_time|0|0|0|0|
|includes_recurring|0|0|0|0|
|includes_usage|0|0|0|0|
|invoice_date|0|0|0|0|
|invoice_number|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|last_email_sent_date|0|0|0|0|
|parent_account_id|0|0|0|0|
|payment_amount|0|0|0|0|
|payment_term|0|0|0|0|
|posted_by|0|0|0|0|
|posted_date|0|0|0|0|
|refund_amount|0|0|0|0|
|sold_to_contact_id|0|0|0|0|
|source|0|0|0|0|
|source_id|0|0|0|0|
|source_type|0|0|0|0|
|status|0|0|0|0|
|target_date|1035|1035|1035|0|
|tax_amount|0|0|0|0|
|tax_status|0|0|0|0|
|transaction_currency|0|0|0|0|
|transferred_to_accounting|0|0|0|0|
|updated_by_id|0|0|0|0|
|updated_date|0|0|0|0|

### 重跑 exchange_rate_date_representation

SQL：`data/017_work/impl-030/exchange_rate_date_representation.sql`；SHA-256：`1cfcca063d2d93b9b06cd9b6f70793dcc96aff900cd38ab5c258c2e100223bca`。

唯一替换位置offset=1814；原文：
```sql
try_cast("exchange_rate_date" AS DATE) AS exchange_rate_date
```
新文：
```sql
"exchange_rate_date" AS exchange_rate_date
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1040|1045|0|5|0/0|1040|1045|8530|False|
|L1|1040|1045|0|5|0/0|1040|1045|4362|False|
|L2|1040|1045|0|5|0/0|1040|1045|4346|False|
|L3|1040|1045|0|5|0/0|1040|1045|3311|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|invoice_id|0|0|0|0|
|account_id|1040|1040|1040|1040|
|adjustment_amount|1040|0|0|0|
|amount|0|0|0|0|
|amount_home_currency|0|0|0|0|
|amount_without_tax|1035|1033|1025|1025|
|amount_without_tax_home_currency|1035|1033|1025|1025|
|auto_pay|0|0|0|0|
|balance|5|0|0|0|
|bill_to_contact_id|0|0|0|0|
|comments|0|0|0|0|
|created_by_id|0|0|0|0|
|credit_balance_adjustment_amount|1040|0|0|0|
|credit_memo_amount|1040|1|1|1|
|default_payment_method_id|0|0|0|0|
|due_date|0|0|0|0|
|exchange_rate|1040|0|0|0|
|exchange_rate_date|0|0|0|0|
|home_currency|0|0|0|0|
|includes_one_time|0|0|0|0|
|includes_recurring|0|0|0|0|
|includes_usage|0|0|0|0|
|invoice_date|0|0|0|0|
|invoice_number|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|last_email_sent_date|0|0|0|0|
|parent_account_id|0|0|0|0|
|payment_amount|0|0|0|0|
|payment_term|0|0|0|0|
|posted_by|0|0|0|0|
|posted_date|0|0|0|0|
|refund_amount|0|0|0|0|
|sold_to_contact_id|0|0|0|0|
|source|0|0|0|0|
|source_id|0|0|0|0|
|source_type|0|0|0|0|
|status|0|0|0|0|
|target_date|1035|1035|1035|0|
|tax_amount|0|0|0|0|
|tax_status|0|0|0|0|
|transaction_currency|0|0|0|0|
|transferred_to_accounting|0|0|0|0|
|updated_by_id|0|0|0|0|
|updated_date|0|0|0|0|

### 重跑 target_date_representation

SQL：`data/017_work/impl-030/target_date_representation.sql`；SHA-256：`84bb3a92699d2d61e1dd464ee6bff336af48e9b743b74b17a3f84fcc2eee4223`。

唯一替换位置offset=3100；原文：
```sql
try_cast("target_date" AS DATE) AS target_date
```
新文：
```sql
"target_date" AS target_date
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|1040|1045|0|5|0/0|1040|1045|8530|False|
|L1|1040|1045|0|5|0/0|1040|1045|4362|False|
|L2|1040|1045|0|5|0/0|1040|1045|4346|False|
|L3|1040|1045|0|5|0/0|1040|1045|3311|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|invoice_id|0|0|0|0|
|account_id|1040|1040|1040|1040|
|adjustment_amount|1040|0|0|0|
|amount|0|0|0|0|
|amount_home_currency|0|0|0|0|
|amount_without_tax|1035|1033|1025|1025|
|amount_without_tax_home_currency|1035|1033|1025|1025|
|auto_pay|0|0|0|0|
|balance|5|0|0|0|
|bill_to_contact_id|0|0|0|0|
|comments|0|0|0|0|
|created_by_id|0|0|0|0|
|credit_balance_adjustment_amount|1040|0|0|0|
|credit_memo_amount|1040|1|1|1|
|default_payment_method_id|0|0|0|0|
|due_date|0|0|0|0|
|exchange_rate|1040|0|0|0|
|exchange_rate_date|1035|1035|1035|0|
|home_currency|0|0|0|0|
|includes_one_time|0|0|0|0|
|includes_recurring|0|0|0|0|
|includes_usage|0|0|0|0|
|invoice_date|0|0|0|0|
|invoice_number|0|0|0|0|
|is_most_recent_record|0|0|0|0|
|last_email_sent_date|0|0|0|0|
|parent_account_id|0|0|0|0|
|payment_amount|0|0|0|0|
|payment_term|0|0|0|0|
|posted_by|0|0|0|0|
|posted_date|0|0|0|0|
|refund_amount|0|0|0|0|
|sold_to_contact_id|0|0|0|0|
|source|0|0|0|0|
|source_id|0|0|0|0|
|source_type|0|0|0|0|
|status|0|0|0|0|
|target_date|0|0|0|0|
|tax_amount|0|0|0|0|
|tax_status|0|0|0|0|
|transaction_currency|0|0|0|0|
|transferred_to_accounting|0|0|0|0|
|updated_by_id|0|0|0|0|
|updated_date|0|0|0|0|

## 5. 类别、把握和对比

- 主要原因：**多因并列（X、O）**（归因判断）。
- 主因单项：account_source, adjustment_amount_representation, credit_balance_adjustment_amount_representation, credit_memo_amount_representation, exchange_rate_representation。
- 参与因素：C：created_date错误非空过滤（减少175格）；O：amount_without_tax及其home_currency表示（各1035格）、exchange_rate_date和target_date表示（各1035格）、balance表示（5格）。
- 标记：无。
- 把握：**中**。
- 重跑是否满足U第4条件：否：所选L0格子口径最大仅1040/9565，所有单项都未达一半，且L0–L2均未整表匹配。

P：对invoice记录，raw.id可以作为该发票的account_id并与账户主键关联。017-V1给出raw.account_id匹配1999行而invoice id为0（2004行总数），源列区分可被数据明确核实。未见agent执行此核实。但account_source单改L0仅9565→8525格，L1/L2也未整表匹配或减半，U4失败。X表示这个已定位错误的类别门槛未满足，不是说差异位置不明。

与014相比是否变化：不适用（第三批首次标注）；也未修改016任何结论。

## 规则问题

U前三项成立、单改有效但与其他最大项并列且不到一半：第4节只放宽“除主因之外”的参与因素，不能借该例外把并列主因硬记U。故记X并列，建议手册明确此边界。也可读为I（pk_alias范围写错），但同名fallback被有意覆盖不足以证明本表正确意图，本次不据变量名推断。所有主因按L0比较；若先归一格式再选会改变权重，公开各档结果但不改手册。固定时间控制从所有运行共同剥离原留存1条日期边界差异，不能把它计入某个字段干预。

2026-10-29用户确认补充：本表依赖原始表若agent留存与初始一致而gold不同，先诊断再标不可评估；若gold与初始一致而agent不同，则正常标注并追踪agent运行中的改动。不能把两种情况混淆。raw差异须限定到本表依赖；CS上游用gold。

新增字段统一口径：记录与实际差异机制相关的明确选择/可疑数据表述；不要求agent预知gold，也不把泛称“完成清洗”算作识别具体边界。021关于重复计数、029关于可选字段失败置NULL为适用范围较广的声明，单独注明并未点名本表异常；可见证据只能支持这一有限范围。该字段不增减U/C/D/I/A/O/X条件。
