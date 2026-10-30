# impl-013 | marts | netsuite2_transaction_details_original | 差异：S1；日期 原记录

## 契约完整原文

S3:3219–3473

```yaml
    - name: netsuite2_transaction_details_original
      description: Original Netsuite transaction line details assembled from core line records joined to related dimensions; includes sign-adjusted amounts and a surrogate key
      grain: One row per transaction_line_id
      source_models:
      - intermediate.int_netsuite2__transaction_lines
      - staging.stg_netsuite2__transactions
      - intermediate.int_netsuite2__tran_with_converted_amounts
      - intermediate.int_netsuite2__accounts
      - intermediate.int_netsuite2__accounting_periods
      - intermediate.int_netsuite2__customers
      - staging.stg_netsuite2__items
      - intermediate.int_netsuite2__locations
      - staging.stg_netsuite2__vendors
      - staging.stg_netsuite2__vendor_categories
      - staging.stg_netsuite2__departments
      - staging.stg_netsuite2__currencies
      - staging.stg_netsuite2__subsidiaries
      - staging.stg_netsuite2__classes
      business_logic: 'Build one row per transaction_lines.transaction_line_id: - Start from transaction lines; inner join transactions by transaction_id; inner join subsidiaries by subsidiary_id from the line. - Left join: - Converted amounts on matching transaction_line_id and transaction_id, keeping rows where transaction_accounting_period_id equals reporting_accounting_period_id. - Accounts by line.account_id; and parent account by accounts.parent_id (treated as text). - Accounting periods by transactions.accounting_period_id. - Customers twice: transaction-side by transactions.entity_id; line-side by line.entity_id. - Classes by line.class_id; items by line.item_id; locations by line.location_id. - Vendors twice: transaction-side by transactions.entity_id; line-side by line.entity_id. - Vendor categories twice: from each joined vendor’s vendor_category_id. - Departments by line.department_id. - Currencies twice: transaction currency by transactions.currency_id; subsidiary currency by subsidiaries.currency_id. - Deterministic rules: - entity_id takes the line entity_id when present; otherwise the transaction entity_id. - is_transaction_non_posting is the opposite of line.is_posting; remains NULL when is_posting is NULL. - Accounting period fields come from the joined accounting period; transaction_due_date comes from transactions.due_date_at. - Account flags: - is_accounts_payable is true when account_type_name equals ''acctpay'' ignoring case; is_accounts_receivable is true when it equals ''acctrec'' ignoring case. - is_expense_account is true when account_type_name is one of ''expense'',''othexpense'',''deferexpense'' ignoring case; is_income_account is true when it is ''income'' or ''othincome'' ignoring case. - If account_type_name is NULL, these flags are NULL. - parent_account_id/name use the parent account when available; otherwise fall back to the current account id/name. - is_account_intercompany and is_eliminate are always false. - Customer fields (id/alt_name/company_name/city/state/zipcode/country/date_first_order/customer_external_id) are taken from the transaction-side customer when transaction_type is ''custinvc'' or ''custcred'' ignoring case; otherwise from the line-side customer. If transaction_type is NULL, use the line-side. - Vendor fields (vendor_category_id/name, vendor_id/alt_name/vendor_name/vendor_create_date) are taken from the transaction-side vendor and its category when transaction_type is ''vendbill'' or ''vendcred'' ignoring case; otherwise from the line-side vendor and its category. If transaction_type is NULL, use the line-side. - Location fields come from the joined location; transaction currency fields come from the joined transaction currency; subsidiary_currency_symbol comes from the joined subsidiary currency; department fields come from the joined department; class fields from the joined class; item fields and sales_description from the joined item. - Amounts: - converted_amount is the converted amount using the transaction’s accounting period; its sign is flipped when the account type is ''income'' or ''othincome'' ignoring case; otherwise the sign is unchanged. If the converted amount row is missing, the value is NULL. - transaction_amount and transaction_line_amount follow the same sign inversion rule above, applied to line.amount and line.netamount respectively. If account_type_name is NULL, no inversion is applied. - transaction_details_id is the MD5 hash of transaction_line_id and transaction_id concatenated with an underscore; inputs are treated as text; NULL when either input is NULL. - All rows from the joins are retained; NULLs from left joins are preserved; no explicit ordering is applied.'
      columns:
      - name: transaction_line_id
        data_type: VARCHAR
        constraints:
        - not_null
        description: Primary line key from transaction_lines.transaction_line_id; one output row per value
      - name: transaction_memo
        data_type: VARCHAR
        description: Line memo from transaction_lines.memo; NULLs preserved
      - name: is_transaction_non_posting
        data_type: BOOLEAN
        description: Opposite of transaction_lines.is_posting; NULL when is_posting is NULL
      - name: is_main_line
        data_type: BOOLEAN
        description: Flag from transaction_lines.is_main_line; NULLs preserved
      - name: is_tax_line
        data_type: BOOLEAN
        description: Flag from transaction_lines.is_tax_line; NULLs preserved
      - name: is_closed
        data_type: BOOLEAN
        description: Flag from transaction_lines.is_closed; NULLs preserved
      - name: transaction_id
        data_type: VARCHAR
        constraints:
        - not_null
        description: Transaction key from transactions.transaction_id
      - name: transaction_status
        data_type: VARCHAR
        description: Transaction status from transactions.status
      - name: transaction_date
        data_type: DATE
        description: Transaction date from transactions.transaction_date
      - name: transaction_due_date
        data_type: DATE
        description: Due date from transactions.due_date_at
      - name: transaction_type
        data_type: VARCHAR
        description: Transaction type from transactions.transaction_type; drives customer/vendor selection rules
      - name: transaction_number
        data_type: VARCHAR
        description: Transaction number from transactions.transaction_number
      - name: entity_id
        data_type: VARCHAR
        description: Line entity_id when present; otherwise transaction entity_id
      - name: is_transaction_intercompany_adjustment
        data_type: BOOLEAN
        description: Always false
      - name: is_reversal
        data_type: BOOLEAN
        description: Flag from transactions.is_reversal
      - name: reversal_transaction_id
        data_type: VARCHAR
        description: Reversal transaction identifier from transactions.reversal_transaction_id
      - name: reversal_date
        data_type: DATE
        description: Reversal date from transactions.reversal_date
      - name: is_reversal_defer
        data_type: BOOLEAN
        description: Flag from transactions.is_reversal_defer
      - name: accounting_period_ending
        data_type: DATE
        description: Accounting period end date from accounting_periods.ending_at
      - name: accounting_period_name
        data_type: VARCHAR
        description: Accounting period name from accounting_periods.name
      - name: accounting_period_id
        data_type: VARCHAR
        description: Accounting period identifier from accounting_periods.accounting_period_id
      - name: is_accounting_period_adjustment
        data_type: BOOLEAN
        description: Flag from accounting_periods.is_adjustment
      - name: is_accounting_period_closed
        data_type: BOOLEAN
        description: Flag from accounting_periods.is_closed
      - name: account_name
        data_type: VARCHAR
        description: Account name from accounts.name
      - name: account_type_name
        data_type: VARCHAR
        description: Account type name from accounts.type_name; drives account flags and amount sign
      - name: account_id
        data_type: VARCHAR
        description: Account identifier from accounts.account_id
      - name: account_number
        data_type: VARCHAR
        description: Account number from accounts.account_number
      - name: is_account_leftside
        data_type: BOOLEAN
        description: Flag from accounts.is_leftside
      - name: is_accounts_payable
        data_type: BOOLEAN
        description: True when account_type_name equals 'acctpay' ignoring case; NULL when account_type_name is NULL
      - name: is_accounts_receivable
        data_type: BOOLEAN
        description: True when account_type_name equals 'acctrec' ignoring case; NULL when account_type_name is NULL
      - name: is_account_intercompany
        data_type: BOOLEAN
        description: Always false
      - name: is_eliminate
        data_type: BOOLEAN
        description: Always false
      - name: parent_account_id
        data_type: VARCHAR
        description: Parent account_id when available; otherwise accounts.account_id
      - name: parent_account_name
        data_type: VARCHAR
        description: Parent account name when available; otherwise accounts.name
      - name: is_expense_account
        data_type: BOOLEAN
        description: True when account_type_name is one of 'expense','othexpense','deferexpense' ignoring case; NULL when account_type_name is NULL
      - name: is_income_account
        data_type: BOOLEAN
        description: True when account_type_name is 'income' or 'othincome' ignoring case; NULL when account_type_name is NULL
      - name: customer_id
        data_type: VARCHAR
        description: Taken from transactions entity_id for 'custinvc'/'custcred' ignoring case; otherwise from line entity_id; if transaction_type is NULL use line entity_id
      - name: customer_alt_name
        data_type: VARCHAR
        description: Selected using the same rule as customer_id
      - name: company_name
        data_type: VARCHAR
        description: Selected using the same rule as customer_id
      - name: customer_city
        data_type: VARCHAR
        description: Selected using the same rule as customer_id
      - name: customer_state
        data_type: VARCHAR
        description: Selected using the same rule as customer_id
      - name: customer_zipcode
        data_type: DOUBLE
        description: Selected using the same rule as customer_id; numeric value with NULLs preserved
      - name: customer_country
        data_type: VARCHAR
        description: Selected using the same rule as customer_id
      - name: customer_date_first_order
        data_type: DATE
        description: Selected using the same rule as customer_id
      - name: customer_external_id
        data_type: VARCHAR
        description: Selected using the same rule as customer_id
      - name: class_id
        data_type: VARCHAR
        description: Class identifier from classes.class_id
      - name: class_full_name
        data_type: VARCHAR
        description: Class full name from classes.full_name
      - name: item_id
        data_type: VARCHAR
        description: Item identifier from transaction_lines.item_id
      - name: item_name
        data_type: VARCHAR
        description: Item name from items.name
      - name: item_type_name
        data_type: VARCHAR
        description: Item type name from items.item_type
      - name: sales_description
        data_type: VARCHAR
        description: Sales description from items.description
      - name: location_id
        data_type: VARCHAR
        description: Location identifier from locations.location_id
      - name: location_name
        data_type: VARCHAR
        description: Location name from locations.name
      - name: location_city
        data_type: DOUBLE
        description: Location city from locations.city; numeric value with NULLs preserved
      - name: location_country
        data_type: DOUBLE
        description: Location country from locations.country; numeric value with NULLs preserved
      - name: vendor_category_id
        data_type: VARCHAR
        description: Taken from vendor category of the transaction-side vendor for 'vendbill'/'vendcred' ignoring case; otherwise from the line-side vendor
      - name: vendor_category_name
        data_type: VARCHAR
        description: Selected using the same rule as vendor_category_id
      - name: vendor_id
        data_type: VARCHAR
        description: Taken from transactions entity_id for 'vendbill'/'vendcred' ignoring case; otherwise from line entity_id
      - name: vendor_alt_name
        data_type: VARCHAR
        description: Selected using the same rule as vendor_id
      - name: vendor_name
        data_type: VARCHAR
        description: Vendor company_name selected using the same rule as vendor_id
      - name: vendor_create_date
        data_type: VARCHAR
        description: Vendor created_at selected using the same rule as vendor_id; string preserved as-is
      - name: currency_id
        data_type: VARCHAR
        description: Transaction currency id from currencies.currency_id via transactions.currency_id
      - name: currency_name
        data_type: VARCHAR
        description: Transaction currency name from currencies.name
      - name: currency_symbol
        data_type: VARCHAR
        description: Transaction currency symbol from currencies.symbol
      - name: department_id
        data_type: VARCHAR
        description: Department identifier from transaction_lines.department_id
      - name: exchange_rate
        data_type: DECIMAL(2,1)
        description: Exchange rate from transaction_lines.exchange_rate; no scaling or rounding applied
      - name: department_full_name
        data_type: VARCHAR
        description: Department full name from departments.full_name
      - name: department_name
        data_type: VARCHAR
        description: Department name from departments.name
      - name: subsidiary_id
        data_type: VARCHAR
        description: Subsidiary identifier from subsidiaries.subsidiary_id joined via transaction_lines.subsidiary_id
      - name: subsidiary_full_name
        data_type: VARCHAR
        description: Subsidiary full name from subsidiaries.full_name
      - name: subsidiary_name
        data_type: VARCHAR
        description: Subsidiary name from subsidiaries.name
      - name: subsidiary_currency_symbol
        data_type: VARCHAR
        description: Currency symbol of the subsidiary from currencies.symbol via subsidiaries.currency_id
      - name: converted_amount
        data_type: DOUBLE
        description: Amount converted using the transaction’s accounting period; sign inverted for income/othincome accounts; NULL if no converted amount row matches
      - name: transaction_amount
        data_type: DOUBLE
        description: Line amount with sign inverted for income/othincome accounts
      - name: transaction_line_amount
        data_type: DOUBLE
        description: Line net amount with sign inverted for income/othincome accounts
      - name: transaction_details_id
        data_type: VARCHAR
        constraints:
        - not_null
        - unique
        description: MD5 of transaction_line_id and transaction_id joined by an underscore; NULL when either input is NULL
```

## agent 最终 SQL

S4

```sql
SELECT * FROM intermediate.int_netsuite2__transaction_details
```

## gold SQL（仅供定位差异）

S5

```sql
with transaction_lines as (
    select *
    from intermediate.int_netsuite2__transaction_lines
),

transactions_with_converted_amounts as (
    select * 
    from intermediate.int_netsuite2__tran_with_converted_amounts
),

accounts as (
    select * 
    from intermediate.int_netsuite2__accounts
),

accounting_periods as (
    select * 
    from intermediate.int_netsuite2__accounting_periods
),

subsidiaries as (
    select * 
    from staging.stg_netsuite2__subsidiaries
),

transactions as (
    select * 
    from staging.stg_netsuite2__transactions
),

customers as (
    select * 
    from intermediate.int_netsuite2__customers
),

items as (
    select * 
    from staging.stg_netsuite2__items
),

locations as (
    select * 
    from intermediate.int_netsuite2__locations
),

vendors as (
    select * 
    from staging.stg_netsuite2__vendors
),

vendor_categories as (
    select * 
    from staging.stg_netsuite2__vendor_categories
),

departments as (
    select * 
    from staging.stg_netsuite2__departments
),

currencies as (
    select * 
    from staging.stg_netsuite2__currencies
),

classes as (
    select *
    from staging.stg_netsuite2__classes
),

transaction_details as (
  select
    transaction_lines.transaction_line_id,
    transaction_lines.memo as transaction_memo,
    not transaction_lines.is_posting as is_transaction_non_posting,
    transaction_lines.is_main_line,
    transaction_lines.is_tax_line,
    transaction_lines.is_closed,
    transactions.transaction_id,
    transactions.status as transaction_status,
    transactions.transaction_date,
    transactions.due_date_at as transaction_due_date,
    transactions.transaction_type as transaction_type,
    transactions.transaction_number,
    coalesce(transaction_lines.entity_id, transactions.entity_id) as entity_id,
    false as is_transaction_intercompany_adjustment,
    transactions.is_reversal,
    transactions.reversal_transaction_id,
    transactions.reversal_date,
    transactions.is_reversal_defer,

    accounting_periods.ending_at as accounting_period_ending,
    accounting_periods.name as accounting_period_name,
    accounting_periods.accounting_period_id as accounting_period_id,
    accounting_periods.is_adjustment as is_accounting_period_adjustment,
    accounting_periods.is_closed as is_accounting_period_closed,
    accounts.name as account_name,
    accounts.type_name as account_type_name,
    accounts.account_id as account_id,
    accounts.account_number,

    accounts.is_leftside as is_account_leftside,
    lower(accounts.type_name) = 'acctpay' as is_accounts_payable,
    lower(accounts.type_name) = 'acctrec' as is_accounts_receivable,
    false as is_account_intercompany,
    false as is_eliminate,
    coalesce(parent_account.account_id, accounts.account_id) as parent_account_id,
    coalesce(parent_account.name, accounts.name) as parent_account_name,
    lower(accounts.type_name) in ('expense', 'othexpense', 'deferexpense') as is_expense_account,
    lower(accounts.type_name) in ('income', 'othincome') as is_income_account,
    case 
      when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.customer_id
      else customers__transaction_lines.customer_id
        end as customer_id,
    case 
      when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.alt_name
      else customers__transaction_lines.alt_name
        end as customer_alt_name,
    case 
      when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.company_name
      else customers__transaction_lines.company_name
        end as company_name,
    case 
      when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.city
      else customers__transaction_lines.city
        end as customer_city,
    case 
      when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.state
      else customers__transaction_lines.state
        end as customer_state,
    case 
      when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.zipcode
      else customers__transaction_lines.zipcode
        end as customer_zipcode,
    case 
      when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.country
      else customers__transaction_lines.country
        end as customer_country,
    case 
      when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.date_first_order_at
      else customers__transaction_lines.date_first_order_at
        end as customer_date_first_order,
    case 
      when lower(transactions.transaction_type) in ('custinvc', 'custcred') then customers__transactions.customer_external_id
      else customers__transaction_lines.customer_external_id
        end as customer_external_id,
    classes.class_id,
    classes.full_name as class_full_name,
    transaction_lines.item_id,
    items.name as item_name,
    items.item_type as item_type_name,
    items.description as sales_description,
    locations.location_id,
    locations.name as location_name,
    locations.city as location_city,
    locations.country as location_country,

    case 
      when lower(transactions.transaction_type) in ('vendbill', 'vendcred') then vendor_categories__transactions.vendor_category_id
      else vendor_categories__transaction_lines.vendor_category_id
        end as vendor_category_id,
    case 
      when lower(transactions.transaction_type) in ('vendbill', 'vendcred') then vendor_categories__transactions.name
      else vendor_categories__transaction_lines.name
        end as vendor_category_name,
    case 
      when lower(transactions.transaction_type) in ('vendbill', 'vendcred') then vendors__transactions.vendor_id
      else vendors__transaction_lines.vendor_id
        end as vendor_id,
    case 
      when lower(transactions.transaction_type) in ('vendbill', 'vendcred') then vendors__transactions.alt_name
      else vendors__transaction_lines.alt_name
        end as vendor_alt_name,
    case 
      when lower(transactions.transaction_type) in ('vendbill', 'vendcred') then vendors__transactions.company_name
      else vendors__transaction_lines.company_name
        end as vendor_name,
    case 
      when lower(transactions.transaction_type) in ('vendbill', 'vendcred') then vendors__transactions.created_at
      else vendors__transaction_lines.created_at
        end as vendor_create_date,
    currencies.currency_id,
    currencies.name as currency_name,
    currencies.symbol as currency_symbol,
    transaction_lines.department_id,
    transaction_lines.exchange_rate,
    departments.full_name as department_full_name,
    departments.name as department_name,

    subsidiaries.subsidiary_id,
    subsidiaries.full_name as subsidiary_full_name,
    subsidiaries.name as subsidiary_name,
    subsidiaries_currencies.symbol as subsidiary_currency_symbol,

    case
      when lower(accounts.type_name) in ('income', 'othincome') then -transactions_with_converted_amounts.converted_amount_using_transaction_accounting_period
      else transactions_with_converted_amounts.converted_amount_using_transaction_accounting_period
        end as converted_amount,
    case
      when lower(accounts.type_name) in ('income', 'othincome') then -transaction_lines.amount
      else transaction_lines.amount
        end as transaction_amount,
    case
      when lower(accounts.type_name) in ('income', 'othincome') then -transaction_lines.netamount
      else transaction_lines.netamount
        end as transaction_line_amount  
  from transaction_lines

  join transactions
    on transactions.transaction_id = transaction_lines.transaction_id

  left join transactions_with_converted_amounts
    on transactions_with_converted_amounts.transaction_line_id = transaction_lines.transaction_line_id
      and transactions_with_converted_amounts.transaction_id = transaction_lines.transaction_id
      and transactions_with_converted_amounts.transaction_accounting_period_id = transactions_with_converted_amounts.reporting_accounting_period_id

  left join accounts 
    on accounts.account_id = transaction_lines.account_id

  left join accounts as parent_account 
    on parent_account.account_id = cast(accounts.parent_id as varchar)

  left join accounting_periods 
    on accounting_periods.accounting_period_id = transactions.accounting_period_id

  left join customers customers__transactions
    on customers__transactions.customer_id = transactions.entity_id

  left join customers customers__transaction_lines
    on customers__transaction_lines.customer_id = transaction_lines.entity_id

  left join classes
    on classes.class_id = transaction_lines.class_id

  left join items 
    on items.item_id = transaction_lines.item_id

  left join locations 
    on locations.location_id = transaction_lines.location_id

  left join vendors vendors__transactions
    on vendors__transactions.vendor_id = transactions.entity_id

  left join vendors vendors__transaction_lines
    on vendors__transaction_lines.vendor_id = transaction_lines.entity_id

  left join vendor_categories vendor_categories__transactions
    on vendor_categories__transactions.vendor_category_id = vendors__transactions.vendor_category_id

  left join vendor_categories vendor_categories__transaction_lines
    on vendor_categories__transaction_lines.vendor_category_id = vendors__transaction_lines.vendor_category_id

  left join currencies 
    on currencies.currency_id = transactions.currency_id

  left join departments 
    on departments.department_id = transaction_lines.department_id

  join subsidiaries 
    on subsidiaries.subsidiary_id = transaction_lines.subsidiary_id
 
  left join currencies subsidiaries_currencies
    on subsidiaries_currencies.currency_id = subsidiaries.currency_id
  
  -- Simplified WHERE clause for mock data compatibility
  where 1=1 -- always true, removes fiscal_calendar_id restriction for mock data
  -- Original condition: (accounting_periods.fiscal_calendar_id is null
  --   or accounting_periods.fiscal_calendar_id  = (select fiscal_calendar_id from subsidiaries where parent_id is null))
),

surrogate_key as ( 
    select 
        *,
        md5(cast(transaction_line_id as varchar) || '_' || cast(transaction_id as varchar)) as transaction_details_id
    from transaction_details
)

select *
from surrogate_key
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 700 | 0 | 700 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| transaction_line_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| transaction_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| accounting_period_ending | 0 | 0 | 0 | DATE | DATE |
| accounting_period_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_accounting_period_adjustment | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_accounting_period_closed | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| account_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_type_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_number | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_account_leftside | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| subsidiary_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subsidiary_full_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subsidiary_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| converted_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| transaction_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| transaction_line_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| transaction_details_id | 0 | 0 | 0 | VARCHAR | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"transaction_details_id":"00d205f3c08ff9a79214fcff7719d413"},{"transaction_details_id":"011afb931f84759bc90e908f647204c4"},{"transaction_details_id":"01906fe174d1c2bbdc6752369e448f2b"},{"transaction_details_id":"01e5321d0919597b4d4910b791c77c7f"},{"transaction_details_id":"02366e4c44f925fbe33f45e7bb60f1b9"}]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>4列；[{"column":"is_account_leftside","table_rows":700},{"column":"sub_id","table_rows":700},{"column":"subsidiary_full_name","table_rows":700}]</code> |
| A3_constant_nonnull_column | <code>4列；[{"column":"accounting_period_name","value":"mock_period"},{"column":"accounting_period_ending","value":"2026-10-25"},{"column":"is_accounting_period_adjustment","value":"false"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["converted_amount","transaction_amount","transaction_line_amount"],"nonnull_equal_rows":700,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["is_accounting_period_adjustment","is_accounting_period_closed"],"nonnull_equal_rows":700,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["converted_amount","transaction_amount","transaction_line_amount"],"nonnull_equal_rows":700,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["is_accounting_period_adjustment","is_accounting_period_closed"],"nonnull_equal_rows":700,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B7_specified_not_read | <code>["intermediate.int_netsuite2__accounting_periods","intermediate.int_netsuite2__accounts","intermediate.int_netsuite2__customers"]</code> |
| B7_read_not_specified | <code>["intermediate.int_netsuite2__transaction_details"]</code> |
| B8_shared_single_source | <code>唯一源=intermediate.int_netsuite2__transaction_details；目标数=2；例=["marts.netsuite2_transaction_details","marts.netsuite2_transaction_details_original"]</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory 2026-10-25 02:32:19,445 - WARNING - Skipping netsuite2_transaction_details_original: SQL file does not exist (sql/marts/netsuite2_transaction_details_original.sql)</code> |

## 轨迹索引（不放输出原文）

本题事件总数：67；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f &#124; sort &#124; wc -l; find sql -type f &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,220p' run.py</code> | 16959 | true | false |
| 17 | run | <code>cat &gt; /tmp/inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>base=Path('sql/intermediate')<br>models={<br>'int_netsuite2__accounts':'''SELECT account_id, parent_id, account_number, name, type_name, general_rate_type</code> | 0 | false | false |
| 19 | run | <code>cat &gt;&gt; /tmp/inter.py &lt;&lt;'PY'<br>models2={<br>'int_netsuite2__customer_profitability':'''WITH tx AS (SELECT t.*, l.entity_id AS customer_id, 'Customer_'&#124;&#124;left(l.entity_id,8) AS customer_name, 'customer_'&#124;&#124;lef</code> | 0 | false | false |
| 21 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -80 /tmp/runlog</code> | 8156 | true | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_netsuite2__consolidated_exchange_rates.sql');s=p.read_text().replace('raw.netsuite2_exchange_rate_data','raw.netsuite2_consolidated_exc</code> | 0 | false | false |
| 29 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>m=Path('sql/marts')<br>passmodels={'netsuite2_balance_sheet':'intermediate.int_netsuite2__balance_sheet','netsuite2_income_statement':'intermediate.int</code> | 0 | false | false |
| 35 | run | <code>find sql/intermediate -type f -printf '%f\n' &#124; sort; grep 'ERROR - ✗' /tmp/runlog2</code> | 1304 | false | false |
| 39 | run | <code>cat &gt; /tmp/marts_more.py &lt;&lt;'PY'<br>from pathlib import Path<br>m=Path('sql/marts')<br>for name,src in [('netsuite__transaction_details','staging.stg_netsuite__transaction_lines'),('netsuite__transaction_detail</code> | 817 | false | false |
| 41 | run | <code>grep -o 'count(DISTINCT[^)]*) total_transactions' sql/marts/netsuite2_vendor_risk_analysis.sql; head -c 1600 sql/marts/netsuite2_vendor_risk_analysis.sql; cat sql/intermediate/int_netsuite2__data_qual</code> | 3957 | false | false |
| 47 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/marts/netsuite2_vendor_risk_analysis.sql');s=p.read_text().replace('FROM intermediate.int_netsuite2__transaction_details t JOIN staging.stg_netsuit</code> | 488 | false | false |

### agent action 的 thought/message 命中原句

event 39 / message

```text
(m/'netsuite2_transaction_details_original.sql').write_text("""SELECT * FROM intermediate.int_netsuite2__transaction_details""")
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-013.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_transaction_details_original.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/marts/netsuite2_transaction_details_original.sql`
- S6: `records/006_contract_impl-013.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/result.md`
- S10: `data/022_packages_work/022_impl-013_netsuite2_transaction_details_original/022_impl-013_netsuite2_transaction_details_original.json`
- S11: `data/005_cs_work/impl-013/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions`
