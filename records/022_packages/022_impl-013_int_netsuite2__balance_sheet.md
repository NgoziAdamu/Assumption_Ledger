# impl-013 | intermediate | int_netsuite2__balance_sheet | 差异：S1；日期 原记录

## 契约完整原文

S3:1277–1362

```yaml
    - name: int_netsuite2__balance_sheet
      description: Balance sheet presentation rows per transaction line and reporting period with account reclassification (Net Income/Retained Earnings/CTA), subsidiary details, and converted/unconverted amounts
      grain: One row per transaction_line_id × transaction_id × reporting accounting_period_id × derived presentation account (account_name + account_id/null)
      source_models:
      - intermediate.int_netsuite2__tran_with_converted_amounts
      - intermediate.int_netsuite2__accounts
      - intermediate.int_netsuite2__accounting_periods
      - staging.stg_netsuite2__subsidiaries
      - staging.stg_netsuite2__currencies
      business_logic: '- Start from intermediate.int_netsuite2__tran_with_converted_amounts (driving transaction lines), keeping rows where the account is a balance sheet account or the driving row is flagged is_income_statement. - Left join: - intermediate.int_netsuite2__accounts by account_id to get account properties (is_balancesheet, type_name, is_leftside, general_rate_type, name, account_number). - intermediate.int_netsuite2__accounting_periods twice: - reporting_accounting_periods via reporting_accounting_period_id (provides accounting_period_id, ending_at, name, is_adjustment, is_closed, fiscal_year_trunc, fiscal_calendar_id). - transaction_accounting_periods via transaction_accounting_period_id (used only to compare fiscal_year_trunc and fiscal_calendar_id with the reporting period). - staging.stg_netsuite2__subsidiaries by subsidiary_id and staging.stg_netsuite2__currencies via subsidiaries.currency_id to get the subsidiary currency symbol. - Create the main balance sheet row with presentation account reclassification: - If the account is not a balance sheet account and the reporting period’s fiscal year/calendar matches the transaction period → account_name/display/type_name/id are "Net Income"/"net_income". - Else if the account is not a balance sheet account → account_name/display/type_name/id are "Retained Earnings"/"retained_earnings". - Else → account_name/display come from accounts.name; for type_name: map lower(type_name)=''retearnings'' to "Retained Earnings", lower(type_name) in (''cta-e'',''cumultransadj'') to "Cumulative Translation Adjustment", otherwise use accounts.type_name; for account_type_id apply the same mappings to ''retained_earnings'' and ''cumulative_translation_adjustment'', otherwise use accounts.type_name. - account_id is null for non-balance-sheet rows; otherwise use accounts.account_id. - account_number is the Retained Earnings account_number selected from any account of type ''retearnings'' when non-balance-sheet; otherwise use accounts.account_number. - is_account_intercompany is always false. - is_account_leftside is false for non-balance-sheet; otherwise use accounts.is_leftside. - converted_amount: - Non-balance-sheet: use a negative sign; use transaction accounting period for historical/average rates, otherwise use reporting month. - Balance-sheet: for right-side (not is_leftside) use negative sign; choose transaction accounting period for historical/average rates, otherwise reporting month; for left-side use positive sign with the same rate selection. - Else → 0. - transaction_amount: - Non-balance-sheet → negative unconverted_amount. - Balance-sheet right-side → negative unconverted_amount; left-side → positive unconverted_amount. - Else → 0. - balance_sheet_sort_helper: - bank=1, acctrec=2, unbilledrec=3, othcurrasset=4, fixedasset=5, othasset=6, deferexpense=7, acctpay=8, credcard=9, othcurrliab=10, longtermliab=11, deferrevenue=12, equity=13, retained earnings=14, net income=15, CTA (''cta-e''/''cumultransadj'')=16; non-balance-sheet reclassification to Retained Earnings also =14; else null. - Union all a second row per included transaction line to represent Cumulative Translation Adjustment (CTA): - account_category=''Equity''; account_name/display/type_name=''Cumulative Translation Adjustment''; account_type_id=''cumulative_translation_adjustment''; account_id=null; account_number selected from any account where lower(type_name)=''cumultransadj''. - is_account_intercompany=false; is_account_leftside=false. - converted_amount: use transaction accounting period for historical/average rates, otherwise reporting month (no sign flip). - transaction_amount: unconverted_amount. - balance_sheet_sort_helper=16. - Create balance_sheet_id by concatenating transaction_line_id, transaction_id, accounting_period_id, account_name, and coalesced account_id using "_" as a delimiter and hashing the result with MD5 to produce a deterministic unique identifier.'
      columns:
      - name: balance_sheet_id
        data_type: VARCHAR
        description: Deterministic row id hashing transaction_line_id, transaction_id, accounting_period_id, account_name, and coalesced account_id joined by '_'
        tests:
        - not_null
        - unique
      - name: transaction_id
        data_type: VARCHAR
        description: Source transaction identifier carried through from the driving transaction line
      - name: transaction_line_id
        data_type: VARCHAR
        description: Source transaction line identifier used in the surrogate key and as the row driver
      - name: subsidiary_id
        data_type: VARCHAR
        description: Subsidiary id from the driving transaction line; used to join subsidiary attributes
      - name: subsidiary_full_name
        data_type: VARCHAR
        description: Full name from subsidiaries; null if no match
      - name: subsidiary_name
        data_type: VARCHAR
        description: Name from subsidiaries; null if no match
      - name: subsidiary_currency_symbol
        data_type: VARCHAR
        description: Subsidiary currency symbol resolved via subsidiaries.currency_id to currencies; null if no match
      - name: accounting_period_id
        data_type: VARCHAR
        description: Reporting accounting period id from the reporting_accounting_periods join
      - name: accounting_period_ending
        data_type: DATE
        description: Reporting accounting period end date from reporting_accounting_periods
      - name: accounting_period_name
        data_type: VARCHAR
        description: Reporting accounting period name from reporting_accounting_periods
      - name: is_accounting_period_adjustment
        data_type: BOOLEAN
        description: Value from reporting_accounting_periods.is_adjustment; null if no match
      - name: is_accounting_period_closed
        data_type: BOOLEAN
        description: Value from reporting_accounting_periods.is_closed; null if no match
      - name: account_category
        data_type: VARCHAR
        description: Category from the driving row; CTA union sets 'Equity'
      - name: account_name
        data_type: VARCHAR
        description: 'Presentation name: Net Income for non-balance-sheet with matching FY/calendar; Retained Earnings for other non-balance-sheet; otherwise accounts.name; CTA union sets ''Cumulative Translation Adjustment'''
      - name: account_display_name
        data_type: VARCHAR
        description: Same as account_name for display
      - name: account_type_name
        data_type: VARCHAR
        description: 'Presentation type name with mappings: Net Income/Retained Earnings for non-balance-sheet; ''Retained Earnings'' for retearnings; ''Cumulative Translation Adjustment'' for ''cta-e''/''cumultransadj''; else accounts.type_name'
      - name: account_type_id
        data_type: VARCHAR
        description: 'Presentation type id: ''net_income''/''retained_earnings'' for non-balance-sheet and retearnings; ''cumulative_translation_adjustment'' for CTA; else accounts.type_name'
      - name: account_id
        data_type: VARCHAR
        description: Null for non-balance-sheet and CTA rows; otherwise accounts.account_id
      - name: account_number
        data_type: VARCHAR
        description: Retained Earnings account_number when non-balance-sheet; CTA union uses a cumultransadj account_number; else accounts.account_number
      - name: is_account_intercompany
        data_type: BOOLEAN
        description: Always false
      - name: is_account_leftside
        data_type: BOOLEAN
        description: False for non-balance-sheet and CTA union; otherwise accounts.is_leftside
      - name: converted_amount
        data_type: DOUBLE
        description: 'Converted amount with sign and rate selection: non-balance-sheet uses negative sign (transaction period for historical/average, else reporting month); balance-sheet uses is_leftside and general_rate_type to choose transaction vs reporting month and apply sign; else 0'
      - name: transaction_amount
        data_type: DOUBLE
        description: 'Unconverted amount signed by side: non-balance-sheet and right-side balance-sheet negative; left-side balance-sheet positive; CTA union uses unconverted_amount'
      - name: balance_sheet_sort_helper
        data_type: INTEGER
        description: 'Sort code by type and reclassification: bank=1, acctrec=2, unbilledrec=3, othcurrasset=4, fixedasset=5, othasset=6, deferexpense=7, acctpay=8, credcard=9, othcurrliab=10, longtermliab=11, deferrevenue=12, equity=13, retained earnings=14, net income=15, CTA=16; else null'
```

## agent 最终 SQL

S4

```sql
WITH base AS (SELECT t.*, a.name, a.type_name, a.account_number, a.is_balancesheet, a.is_leftside, a.general_rate_type, p.ending_at, p.name AS period_name, p.is_adjustment, p.is_closed, p.fiscal_year_trunc, tp.fiscal_year_trunc AS transaction_fiscal_year, tp.fiscal_calendar_id AS transaction_calendar, p.fiscal_calendar_id, s.full_name AS subsidiary_full_name, s.name AS subsidiary_name, cur.symbol AS subsidiary_currency_symbol FROM intermediate.int_netsuite2__tran_with_converted_amounts t LEFT JOIN intermediate.int_netsuite2__accounts a ON a.account_id=t.account_id LEFT JOIN intermediate.int_netsuite2__accounting_periods p ON p.accounting_period_id=t.reporting_accounting_period_id LEFT JOIN intermediate.int_netsuite2__accounting_periods tp ON tp.accounting_period_id=t.transaction_accounting_period_id LEFT JOIN staging.stg_netsuite2__subsidiaries s ON s.subsidiary_id=t.subsidiary_id LEFT JOIN staging.stg_netsuite2__currencies cur ON cur.currency_id=s.currency_id WHERE a.is_balancesheet OR t.is_income_statement), presented AS (SELECT *, CASE WHEN NOT is_balancesheet AND fiscal_year_trunc=transaction_fiscal_year AND fiscal_calendar_id=transaction_calendar THEN 'Net Income' WHEN NOT is_balancesheet THEN 'Retained Earnings' ELSE name END AS out_name, CASE WHEN NOT is_balancesheet AND fiscal_year_trunc=transaction_fiscal_year AND fiscal_calendar_id=transaction_calendar THEN 'Net Income' WHEN NOT is_balancesheet THEN 'Retained Earnings' ELSE type_name END AS out_type FROM base) SELECT md5(transaction_line_id||'_'||transaction_id||'_'||reporting_accounting_period_id||'_'||out_name||'_'||coalesce(CASE WHEN is_balancesheet THEN account_id END,'')) AS balance_sheet_id, transaction_id, transaction_line_id, subsidiary_id, subsidiary_full_name, subsidiary_name, subsidiary_currency_symbol, reporting_accounting_period_id AS accounting_period_id, ending_at AS accounting_period_ending, period_name AS accounting_period_name, is_adjustment AS is_accounting_period_adjustment, is_closed AS is_accounting_period_closed, account_category, out_name AS account_name, out_name AS account_display_name, out_type AS account_type_name, lower(replace(out_type,' ', '_')) AS account_type_id, CASE WHEN is_balancesheet THEN account_id END AS account_id, CASE WHEN is_balancesheet THEN account_number END AS account_number, FALSE AS is_account_intercompany, CASE WHEN is_balancesheet THEN is_leftside ELSE FALSE END AS is_account_leftside, CASE WHEN NOT is_balancesheet OR is_leftside IS FALSE THEN -coalesce(converted_amount_using_transaction_accounting_period, converted_amount_using_reporting_month) ELSE coalesce(converted_amount_using_transaction_accounting_period, converted_amount_using_reporting_month) END AS converted_amount, CASE WHEN NOT is_balancesheet OR is_leftside IS FALSE THEN -unconverted_amount ELSE unconverted_amount END AS transaction_amount, CASE lower(type_name) WHEN 'bank' THEN 1 WHEN 'acctrec' THEN 2 WHEN 'unbilledrec' THEN 3 WHEN 'othcurrasset' THEN 4 WHEN 'fixedasset' THEN 5 WHEN 'othasset' THEN 6 WHEN 'deferexpense' THEN 7 WHEN 'acctpay' THEN 8 WHEN 'credcard' THEN 9 WHEN 'othcurrliab' THEN 10 WHEN 'longtermliab' THEN 11 WHEN 'deferrevenue' THEN 12 WHEN 'equity' THEN 13 ELSE CASE WHEN out_name='Retained Earnings' THEN 14 WHEN out_name='Net Income' THEN 15 END END::INTEGER AS balance_sheet_sort_helper FROM presented
```

## gold SQL（仅供定位差异）

S5

```sql
with transactions_with_converted_amounts as (
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

currencies as (
    select *
    from staging.stg_netsuite2__currencies
),

balance_sheet as ( 
    select
        transactions_with_converted_amounts.transaction_id,
        transactions_with_converted_amounts.transaction_line_id,
        transactions_with_converted_amounts.subsidiary_id,
        subsidiaries.full_name as subsidiary_full_name,
        subsidiaries.name as subsidiary_name,
        subsidiaries_currencies.symbol as subsidiary_currency_symbol,

        reporting_accounting_periods.accounting_period_id as accounting_period_id,
        reporting_accounting_periods.ending_at as accounting_period_ending,
        reporting_accounting_periods.name as accounting_period_name,
        reporting_accounting_periods.is_adjustment as is_accounting_period_adjustment,
        reporting_accounting_periods.is_closed as is_accounting_period_closed,
        transactions_with_converted_amounts.account_category as account_category,
        case
        when (not accounts.is_balancesheet 
                and reporting_accounting_periods.fiscal_year_trunc = transaction_accounting_periods.fiscal_year_trunc 
                and reporting_accounting_periods.fiscal_calendar_id = transaction_accounting_periods.fiscal_calendar_id) then 'Net Income'
        when not accounts.is_balancesheet then 'Retained Earnings'
        else accounts.name
            end as account_name,
        case
        when (not accounts.is_balancesheet 
                and reporting_accounting_periods.fiscal_year_trunc = transaction_accounting_periods.fiscal_year_trunc 
                and reporting_accounting_periods.fiscal_calendar_id = transaction_accounting_periods.fiscal_calendar_id) then 'Net Income'
        when not accounts.is_balancesheet then 'Retained Earnings'
        else accounts.name
            end as account_display_name,
        case
        when (not accounts.is_balancesheet 
                and reporting_accounting_periods.fiscal_year_trunc = transaction_accounting_periods.fiscal_year_trunc 
                and reporting_accounting_periods.fiscal_calendar_id = transaction_accounting_periods.fiscal_calendar_id) then 'Net Income'
        when not accounts.is_balancesheet then 'Retained Earnings'
        when lower(accounts.type_name) = 'retearnings' then 'Retained Earnings'
        when lower(accounts.type_name) in ('cta-e', 'cumultransadj') then 'Cumulative Translation Adjustment'
        else accounts.type_name
            end as account_type_name,
        case
        when (not accounts.is_balancesheet 
                and reporting_accounting_periods.fiscal_year_trunc = transaction_accounting_periods.fiscal_year_trunc 
                and reporting_accounting_periods.fiscal_calendar_id = transaction_accounting_periods.fiscal_calendar_id) then 'net_income'
        when not accounts.is_balancesheet then 'retained_earnings'
        when lower(accounts.type_name) = 'retearnings' then 'retained_earnings'
        when lower(accounts.type_name) in ('cta-e', 'cumultransadj') then 'cumulative_translation_adjustment'
        else accounts.type_name
            end as account_type_id,
        case
        when not accounts.is_balancesheet then null
        else accounts.account_id
            end as account_id,
        case
        when not accounts.is_balancesheet then (select accounts.account_number from accounts where lower(accounts.type_name) = 'retearnings' limit 1)
        else accounts.account_number
            end as account_number,
        case
        when not accounts.is_balancesheet then false
        else false
            end as is_account_intercompany,
        case
        when not accounts.is_balancesheet then false
        else accounts.is_leftside
            end as is_account_leftside,

        case
        when not accounts.is_balancesheet and lower(accounts.general_rate_type) in ('historical', 'average') then -converted_amount_using_transaction_accounting_period
        when not accounts.is_balancesheet then -converted_amount_using_reporting_month
        when accounts.is_balancesheet and not accounts.is_leftside and lower(accounts.general_rate_type) in ('historical', 'average') then -converted_amount_using_transaction_accounting_period
        when accounts.is_balancesheet and accounts.is_leftside and lower(accounts.general_rate_type) in ('historical', 'average') then converted_amount_using_transaction_accounting_period
        when accounts.is_balancesheet and not accounts.is_leftside then -converted_amount_using_reporting_month
        when accounts.is_balancesheet and accounts.is_leftside then converted_amount_using_reporting_month
        else 0
            end as converted_amount,

        case
        when not accounts.is_balancesheet then -unconverted_amount
        when accounts.is_balancesheet and not accounts.is_leftside then -unconverted_amount
        when accounts.is_balancesheet and accounts.is_leftside then unconverted_amount
        else 0
            end as transaction_amount,

        case
        when lower(accounts.type_name) = 'bank' then 1
        when lower(accounts.type_name) = 'acctrec' then 2
        when lower(accounts.type_name) = 'unbilledrec' then 3
        when lower(accounts.type_name) = 'othcurrasset' then 4
        when lower(accounts.type_name) = 'fixedasset' then 5
        when lower(accounts.type_name) = 'othasset' then 6
        when lower(accounts.type_name) = 'deferexpense' then 7
        when lower(accounts.type_name) = 'acctpay' then 8
        when lower(accounts.type_name) = 'credcard' then 9
        when lower(accounts.type_name) = 'othcurrliab' then 10
        when lower(accounts.type_name) = 'longtermliab' then 11
        when lower(accounts.type_name) = 'deferrevenue' then 12
        when lower(accounts.type_name) = 'retearnings' then 14
        when lower(accounts.type_name) in ('cta-e', 'cumultransadj') then 16
        when lower(accounts.type_name) = 'equity' then 13
        when (not accounts.is_balancesheet 
                and reporting_accounting_periods.fiscal_year_trunc = transaction_accounting_periods.fiscal_year_trunc
                and reporting_accounting_periods.fiscal_calendar_id = transaction_accounting_periods.fiscal_calendar_id) then 15
        when not accounts.is_balancesheet then 14
        else null
            end as balance_sheet_sort_helper

    from transactions_with_converted_amounts

    left join accounts 
        on accounts.account_id = transactions_with_converted_amounts.account_id

    left join accounting_periods as reporting_accounting_periods 
        on reporting_accounting_periods.accounting_period_id = transactions_with_converted_amounts.reporting_accounting_period_id

    left join accounting_periods as transaction_accounting_periods 
        on transaction_accounting_periods.accounting_period_id = transactions_with_converted_amounts.transaction_accounting_period_id

    left join subsidiaries
        on subsidiaries.subsidiary_id = transactions_with_converted_amounts.subsidiary_id

    left join currencies subsidiaries_currencies
        on subsidiaries_currencies.currency_id = subsidiaries.currency_id

    where 1=1 -- fiscal_calendar_id filters removed for mock data compatibility
        -- and reporting_accounting_periods.fiscal_calendar_id = (select fiscal_calendar_id from subsidiaries where parent_id is null)
        -- and transaction_accounting_periods.fiscal_calendar_id = (select fiscal_calendar_id from subsidiaries where parent_id is null)
        and (accounts.is_balancesheet
        or transactions_with_converted_amounts.is_income_statement)

    union all

    select
        transactions_with_converted_amounts.transaction_id,
        transactions_with_converted_amounts.transaction_line_id,
        transactions_with_converted_amounts.subsidiary_id,
        subsidiaries.full_name as subsidiary_full_name,
        subsidiaries.name as subsidiary_name,
        subsidiaries_currencies.symbol as subsidiary_currency_symbol,
        
        reporting_accounting_periods.accounting_period_id as accounting_period_id,
        reporting_accounting_periods.ending_at as accounting_period_ending,
        reporting_accounting_periods.name as accounting_period_name,
        reporting_accounting_periods.is_adjustment as is_accounting_period_adjustment,
        reporting_accounting_periods.is_closed as is_accounting_period_closed,
        'Equity' as account_category,
        'Cumulative Translation Adjustment' as account_name,
        'Cumulative Translation Adjustment' as account_display_name,
        'Cumulative Translation Adjustment' as account_type_name,
        'cumulative_translation_adjustment' as account_type_id,
        null as account_id,
        (select accounts.account_number from accounts where lower(accounts.type_name) = 'cumultransadj' limit 1) as account_number,
        false as is_account_intercompany,
        false as is_account_leftside,

        case
        when lower(accounts.general_rate_type) in ('historical', 'average') then converted_amount_using_transaction_accounting_period
        else converted_amount_using_reporting_month
            end as converted_amount,

        unconverted_amount as transaction_amount,

        16 as balance_sheet_sort_helper

    from transactions_with_converted_amounts

    left join accounts
        on accounts.account_id = transactions_with_converted_amounts.account_id

    left join accounting_periods as reporting_accounting_periods 
        on reporting_accounting_periods.accounting_period_id = transactions_with_converted_amounts.reporting_accounting_period_id

    left join subsidiaries
        on subsidiaries.subsidiary_id = transactions_with_converted_amounts.subsidiary_id

    left join currencies subsidiaries_currencies
        on subsidiaries_currencies.currency_id = subsidiaries.currency_id

    where 1=1 -- fiscal_calendar_id filter removed for mock data compatibility
        -- and reporting_accounting_periods.fiscal_calendar_id = (select fiscal_calendar_id from subsidiaries where parent_id is null)
        and (accounts.is_balancesheet
        or transactions_with_converted_amounts.is_income_statement)
    ),

    surrogate_key as ( 
    select 
        *,
        md5(
          cast(transaction_line_id as varchar) || '_' ||
          cast(transaction_id as varchar) || '_' ||
          cast(accounting_period_id as varchar) || '_' ||
          cast(account_name as varchar) || '_' ||
          cast(coalesce(account_id, '0') as varchar)
        ) as balance_sheet_id
    from balance_sheet
)

select *
from surrogate_key
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 388 | 776 | 219 | 607 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| transaction_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| transaction_line_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subsidiary_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subsidiary_full_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subsidiary_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subsidiary_currency_symbol | 0 | 0 | 0 | VARCHAR | VARCHAR |
| accounting_period_ending | 0 | 0 | 0 | DATE | DATE |
| accounting_period_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_accounting_period_adjustment | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_accounting_period_closed | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| account_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_display_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_type_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_number | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_account_intercompany | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_account_leftside | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| converted_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| transaction_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| balance_sheet_sort_helper | 0 | 0 | 0 | INTEGER | INTEGER |
| balance_sheet_id | 0 | 0 | 0 | VARCHAR | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"balance_sheet_id":"010137fc225e16fba67314a68de6a2b0"}]</code> | <code>[{"balance_sheet_id":"0024da8258fffb668745bdf674f27838"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>6列；[{"column":"subsidiary_full_name","table_rows":219}]</code> |
| A3_constant_nonnull_column | <code>3列；[{"column":"is_accounting_period_adjustment","value":"false"}]</code> |
| A4_equal_columns | <code>4组；[{"columns":["is_accounting_period_adjustment","is_account_intercompany","is_account_leftside"],"nonnull_equal_rows":219,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>4组；[{"columns":["is_accounting_period_adjustment","is_account_intercompany","is_account_leftside"],"nonnull_equal_rows":219,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"is_account_intercompany","expression":["FALSE"]}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory (p/'int_netsuite2__financial_ratios.sql').write_text("""WITH latest AS (SELECT max(accounting_period_ending) latest_date FROM intermediate.int_netsuite2__balance_sheet), bs AS (SELECT subsidiary_id,accounting_period_id,accounting_period_ending,account_type_name,sum(converted_amount) period_balance FROM intermediate.int_netsuite2__balance_sheet CROSS JOIN latest WHERE accounting_period_ending=latest_date GROUP BY ALL), assets AS (SELECT subsidiary_id,accounting_period_id,sum(period_balance) FILTER(WHERE account_type_name IN ('Bank','AcctRec','UnbilledRec','OthCurrAsset')) total_current_assets,sum(period_balance) FILTER(WHERE account_type_name='Bank') cash_and_equivalents,sum(period_balance) FILTER(WHERE account_type_name IN ('AcctRec','UnbilledRec')) accounts_receivable FROM bs GROUP BY subsidiary_id,accounting_period_id), liabs AS (SELECT subsidiary_id,accounting_period_id,sum(abs(period_balance)) FILTER(WHERE account_type_name IN ('AcctPay','CredCard','OthCurrLiab')) total_current_liabilities FROM bs GROUP BY subsidiary_id,accounting_period_id), eq AS (SELECT subsidiary_id,accounting_period_id,sum(period_balance) FILTER(WHERE account_type_name IN ('Equity','Retained Earnings','Net Income')) total_equity FROM bs GROUP BY subsidiary_id,accounting_period_id), inc AS (SELECT subsidiary_id,sum(converted_amount) FILTER(WHERE account_type_name='Income') total_revenue,sum(converted_amount) FILTER(WHERE account_type_name='COGS') total_cogs,sum(converted_amount) FILTER(WHERE account_type_name IN ('Income','COGS','Expense','OthIncome','OthExpense')) net_income FROM intermediate.int_netsuite2__income_statement WHERE accounting_period_ending&gt;=current_date-interval '12 months' GROUP BY subsidiary_id), ratios AS (SELECT a.*,l.total_current_liabilities,e.total_equity,i.total_revenue,i.total_cogs,i.net_income,a.total_current_assets/nullif(l.total_current_liabilities,0) current_ratio,(a.cash_and_equivalents+a.accounts_receivable)/nullif(l.total_current_liabilities,0) quick_ratio,a.cash_and_equivalents/nullif(l.total_current_liabilities,0) cash_ratio,i.net_income/nullif(e.total_equity,0) return_on_equity,(i.total_revenue-i.total_cogs)/nullif(i.total_revenue,0) gross_margin_ratio,i.net_income/nullif(i.total_revenue,0) net_profit_margin,i.total_revenue/nullif(a.accounts_receivable,0) receivables_turnover FROM assets a LEFT JOIN liabs l USING(subsidiary_id,accounting_period_id) LEFT JOIN eq e USING(subsidiary_id,accounting_period_id) LEFT JOIN inc i USING(subsidiary_id)) , scores AS (SELECT *,CASE WHEN current_ratio&gt;=2 THEN 100 WHEN current_ratio&gt;=1.5 THEN 80 WHEN current_ratio&gt;=1 THEN 60 WHEN current_ratio&gt;=.8 THEN 40 WHEN current_ratio&gt;=.5 THEN 20 ELSE 0 END liquidity_score,CASE WHEN net_profit_margin&gt;=.15 THEN 100 WHEN net_profit_margin&gt;=.1 THEN 80 WHEN net_profit_margin&gt;=.05 THEN 60 WHEN net_profit_margin&gt;=.02 THEN 40 WHEN net_profit_margin&gt;=0 THEN 20 ELSE 0 END profitability_score,CASE WHEN receivables_turnover&gt;=12 THEN 100 WHEN receivables_turnover&gt;=8 THEN 80 WHEN receivables_turnover&gt;=6 THEN 60 WHEN receivables_turnover&gt;=4 THEN 40 WHEN receivables_turnover&gt;=2 THEN 20 ELSE 0 END efficiency_score FROM ratios) SELECT subsidiary_id,accounting_period_id,current_ratio,quick_ratio,cash_ratio,return_on_equity,gross_margin_ratio,net_profit_margin,receivables_turnover,total_current_assets,total_current_liabilities,cash_and_equivalents,accounts_receivable,total_equity,total_revenue,total_cogs,net_income,current_date calculation_date,liquidity_score,profitability_score,efficiency_score,round((liquidity_score+profitability_score+efficiency_score)/3.0,2) overall_financial_health_score,CASE WHEN (liquidity_score+profitability_score+efficiency_score)/3.0&gt;=80 THEN 'Excellent' WHEN (liquidity_score+profitability_score+efficiency_score)/3.0&gt;=60 THEN 'Good' WHEN (liquidity_score+profitability_score+efficiency_score)/3.0&gt;=40 THEN 'Fair' WHEN (liquidity_score+profitability_score+efficiency_score)/3.0&gt;=20 THEN 'Poor' ELSE 'Critical' END financial_health_grade,md5(subsidiary_id&#124;&#124;'_'&#124;&#124;accounting_period_id) financial_ratios_id FROM scores WHERE subsidiary_id IS NOT NULL""")</code> |

## 轨迹索引（不放输出原文）

本题事件总数：67；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f &#124; sort &#124; wc -l; find sql -type f &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,220p' run.py</code> | 16959 | true | false |
| 9 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(len(c['staging_contract']['tables']),len(c['modeling_spec']['intermediate_models']),len(c['modeling_spec']['marts_mo</code> | 5234 | false | false |
| 15 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/generate.py &lt;&lt;'PY'<br>import yaml, os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>raw=yaml.safe_load(open('netsuite_start.yaml'))<br># per-table</code> | 0 | false | false |
| 17 | run | <code>cat &gt; /tmp/inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>base=Path('sql/intermediate')<br>models={<br>'int_netsuite2__accounts':'''SELECT account_id, parent_id, account_number, name, type_name, general_rate_type</code> | 0 | false | false |
| 21 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -80 /tmp/runlog</code> | 8156 | true | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_netsuite2__consolidated_exchange_rates.sql');s=p.read_text().replace('raw.netsuite2_exchange_rate_data','raw.netsuite2_consolidated_exc</code> | 0 | false | false |
| 29 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>m=Path('sql/marts')<br>passmodels={'netsuite2_balance_sheet':'intermediate.int_netsuite2__balance_sheet','netsuite2_income_statement':'intermediate.int</code> | 0 | false | false |
| 35 | run | <code>find sql/intermediate -type f -printf '%f\n' &#124; sort; grep 'ERROR - ✗' /tmp/runlog2</code> | 1304 | true | false |
| 39 | run | <code>cat &gt; /tmp/marts_more.py &lt;&lt;'PY'<br>from pathlib import Path<br>m=Path('sql/marts')<br>for name,src in [('netsuite__transaction_details','staging.stg_netsuite__transaction_lines'),('netsuite__transaction_detail</code> | 817 | false | false |

### agent action 的 thought/message 命中原句

event 17 / message

```text
'int_netsuite2__balance_sheet':'''WITH base AS (SELECT t.*, a.name, a.type_name, a.account_number, a.is_balancesheet, a.is_leftside, a.general_rate_type, p.ending_at, p.name AS period_name, p.is_adjustment, p.is_closed, p.fiscal_year_trunc, tp.fiscal_year_trunc AS transaction_fiscal_year, tp.fiscal_calendar_id AS transaction_calendar, p.fiscal_calendar_id, s.full_name AS subsidiary_full_name, s.name AS subsidiary_name, cur.symbol AS subsidiary_currency_symbol FROM intermediate.int_netsuite2__tran_with_converted_amounts t LEFT JOIN intermediate.int_netsuite2__accounts a ON a.account_id=t.account_id LEFT JOIN intermediate.int_netsuite2__accounting_periods p ON p.accounting_period_id=t.reporting_accounting_period_id LEFT JOIN intermediate.int_netsuite2__accounting_periods tp ON tp.accounting_period_id=t.transaction_accounting_period_id LEFT JOIN staging.stg_netsuite2__subsidiaries s ON s.subsidiary_id=t.subsidiary_id LEFT JOIN staging.stg_netsuite2__currencies cur ON cur.currency_id=s.currency_id WHERE a.is_balancesheet OR t.is_income_statement), presented AS (SELECT *, CASE WHEN NOT is_balancesheet AND fiscal_year_trunc=transaction_fiscal_year AND fiscal_calendar_id=transaction_calendar THEN 'Net Income' WHEN NOT is_balancesheet THEN 'Retained Earnings' ELSE name END AS out_name, CASE WHEN NOT is_balancesheet AND fiscal_year_trunc=transaction_fiscal_year AND fiscal_calendar_id=transaction_calendar THEN 'Net Income' WHEN NOT is_balancesheet THEN 'Retained Earnings' ELSE type_name END AS out_type FROM base) SELECT md5(transaction_line_id||'_'||transaction_id||'_'||reporting_accounting_period_id||'_'||out_name||'_'||coalesce(CASE WHEN is_balancesheet THEN account_id END,'')) AS balance_sheet_id, transaction_id, transaction_line_id, subsidiary_id, subsidiary_full_name, subsidiary_name, subsidiary_currency_symbol, reporting_accounting_period_id AS accounting_period_id, ending_at AS accounting_period_ending, period_name AS accounting_period_name, is_adjustment AS is_accounting_period_adjustment, is_closed AS is_accounting_period_closed, account_category, out_name AS account_name, out_name AS account_display_name, out_type AS account_type_name, lower(replace(out_type,' ', '_')) AS account_type_id, CASE WHEN is_balancesheet THEN account_id END AS account_id, CASE WHEN is_balancesheet THEN account_number END AS account_number, FALSE AS is_account_intercompany, CASE WHEN is_balancesheet THEN is_leftside ELSE FALSE END AS is_account_leftside, CASE WHEN NOT is_balancesheet OR is_leftside IS FALSE THEN -coalesce(converted_amount_using_transaction_accounting_period, converted_amount_using_reporting_month) ELSE coalesce(converted_amount_using_transaction_accounting_period, converted_amount_using_reporting_month) END AS converted_amount, CASE WHEN NOT is_balancesheet OR is_leftside IS FALSE THEN -unconverted_amount ELSE unconverted_amount END AS transaction_amount, CASE lower(type_name) WHEN 'bank' THEN 1 WHEN 'acctrec' THEN 2 WHEN 'unbilledrec' THEN 3 WHEN 'othcurrasset' THEN 4 WHEN 'fixedasset' THEN 5 WHEN 'othasset' THEN 6 WHEN 'deferexpense' THEN 7 WHEN 'acctpay' THEN 8 WHEN 'credcard' THEN 9 WHEN 'othcurrliab' THEN 10 WHEN 'longtermliab' THEN 11 WHEN 'deferrevenue' THEN 12 WHEN 'equity' THEN 13 ELSE CASE WHEN out_name='Retained Earnings' THEN 14 WHEN out_name='Net Income' THEN 15 END END::INTEGER AS balance_sheet_sort_helper FROM presented''',
```
event 25 / message

```text
(p/'int_netsuite2__financial_ratios.sql').write_text("""WITH latest AS (SELECT max(accounting_period_ending) latest_date FROM intermediate.int_netsuite2__balance_sheet), bs AS (SELECT subsidiary_id,accounting_period_id,accounting_period_ending,account_type_name,sum(converted_amount) period_balance FROM intermediate.int_netsuite2__balance_sheet CROSS JOIN latest WHERE accounting_period_ending=latest_date GROUP BY ALL), assets AS (SELECT subsidiary_id,accounting_period_id,sum(period_balance) FILTER(WHERE account_type_name IN ('Bank','AcctRec','UnbilledRec','OthCurrAsset')) total_current_assets,sum(period_balance) FILTER(WHERE account_type_name='Bank') cash_and_equivalents,sum(period_balance) FILTER(WHERE account_type_name IN ('AcctRec','UnbilledRec')) accounts_receivable FROM bs GROUP BY subsidiary_id,accounting_period_id), liabs AS (SELECT subsidiary_id,accounting_period_id,sum(abs(period_balance)) FILTER(WHERE account_type_name IN ('AcctPay','CredCard','OthCurrLiab')) total_current_liabilities FROM bs GROUP BY subsidiary_id,accounting_period_id), eq AS (SELECT subsidiary_id,accounting_period_id,sum(period_balance) FILTER(WHERE account_type_name IN ('Equity','Retained Earnings','Net Income')) total_equity FROM bs GROUP BY subsidiary_id,accounting_period_id), inc AS (SELECT subsidiary_id,sum(converted_amount) FILTER(WHERE account_type_name='Income') total_revenue,sum(converted_amount) FILTER(WHERE account_type_name='COGS') total_cogs,sum(converted_amount) FILTER(WHERE account_type_name IN ('Income','COGS','Expense','OthIncome','OthExpense')) net_income FROM intermediate.int_netsuite2__income_statement WHERE accounting_period_ending>=current_date-interval '12 months' GROUP BY subsidiary_id), ratios AS (SELECT a.*,l.total_current_liabilities,e.total_equity,i.total_revenue,i.total_cogs,i.net_income,a.total_current_assets/nullif(l.total_current_liabilities,0) current_ratio,(a.cash_and_equivalents+a.accounts_receivable)/nullif(l.total_current_liabilities,0) quick_ratio,a.cash_and_equivalents/nullif(l.total_current_liabilities,0) cash_ratio,i.net_income/nullif(e.total_equity,0) return_on_equity,(i.total_revenue-i.total_cogs)/nullif(i.total_revenue,0) gross_margin_ratio,i.net_income/nullif(i.total_revenue,0) net_profit_margin,i.total_revenue/nullif(a.accounts_receivable,0) receivables_turnover FROM assets a LEFT JOIN liabs l USING(subsidiary_id,accounting_period_id) LEFT JOIN eq e USING(subsidiary_id,accounting_period_id) LEFT JOIN inc i USING(subsidiary_id)) , scores AS (SELECT *,CASE WHEN current_ratio>=2 THEN 100 WHEN current_ratio>=1.5 THEN 80 WHEN current_ratio>=1 THEN 60 WHEN current_ratio>=.8 THEN 40 WHEN current_ratio>=.5 THEN 20 ELSE 0 END liquidity_score,CASE WHEN net_profit_margin>=.15 THEN 100 WHEN net_profit_margin>=.1 THEN 80 WHEN net_profit_margin>=.05 THEN 60 WHEN net_profit_margin>=.02 THEN 40 WHEN net_profit_margin>=0 THEN 20 ELSE 0 END profitability_score,CASE WHEN receivables_turnover>=12 THEN 100 WHEN receivables_turnover>=8 THEN 80 WHEN receivables_turnover>=6 THEN 60 WHEN receivables_turnover>=4 THEN 40 WHEN receivables_turnover>=2 THEN 20 ELSE 0 END efficiency_score FROM ratios) SELECT subsidiary_id,accounting_period_id,current_ratio,quick_ratio,cash_ratio,return_on_equity,gross_margin_ratio,net_profit_margin,receivables_turnover,total_current_assets,total_current_liabilities,cash_and_equivalents,accounts_receivable,total_equity,total_revenue,total_cogs,net_income,current_date calculation_date,liquidity_score,profitability_score,efficiency_score,round((liquidity_score+profitability_score+efficiency_score)/3.0,2) overall_financial_health_score,CASE WHEN (liquidity_score+profitability_score+efficiency_score)/3.0>=80 THEN 'Excellent' WHEN (liquidity_score+profitability_score+efficiency_score)/3.0>=60 THEN 'Good' WHEN (liquidity_score+profitability_score+efficiency_score)/3.0>=40 THEN 'Fair' WHEN (liquidity_score+profitability_score+efficiency_score)/3.0>=20 THEN 'Poor' ELSE 'Critical' END financial_health_grade,md5(subsidiary_id||'_'||accounting_period_id) financial_ratios_id FROM scores WHERE subsidiary_id IS NOT NULL""")
```
event 29 / message

```text
passmodels={'netsuite2_balance_sheet':'intermediate.int_netsuite2__balance_sheet','netsuite2_income_statement':'intermediate.int_netsuite2__income_statement','netsuite2_transaction_details':'intermediate.int_netsuite2__transaction_details'}
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-013.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__balance_sheet.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/intermediate/int_netsuite2__balance_sheet.sql`
- S6: `records/006_contract_impl-013.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/result.md`
- S10: `data/022_packages_work/022_impl-013_int_netsuite2__balance_sheet/022_impl-013_int_netsuite2__balance_sheet.json`
- S11: `data/005_cs_work/impl-013/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions`
