# impl-013 | intermediate | int_netsuite2__income_statement | 差异：S1；日期 原记录

## 契约完整原文

S3:1363–1458

```yaml
    - name: int_netsuite2__income_statement
      description: Income statement lines with joined dimensions and converted amounts for profitability analysis
      grain: One row per transaction_id + transaction_line_id for income-statement transactions in their reporting period
      source_models:
      - intermediate.int_netsuite2__tran_with_converted_amounts
      - intermediate.int_netsuite2__transaction_lines
      - intermediate.int_netsuite2__accounts
      - intermediate.int_netsuite2__accounting_periods
      - staging.stg_netsuite2__subsidiaries
      - staging.stg_netsuite2__currencies
      - staging.stg_netsuite2__classes
      - staging.stg_netsuite2__locations
      - staging.stg_netsuite2__departments
      business_logic: '- Start from intermediate.int_netsuite2__tran_with_converted_amounts. - Inner join intermediate.int_netsuite2__transaction_lines on both transaction_id and transaction_line_id to bring line-level attributes. - Left join dimensions: - Accounts by account_id. - Accounting periods (as reporting_accounting_periods) by reporting_accounting_period_id. - Subsidiaries by subsidiary_id, then currencies by subsidiaries.currency_id to get the subsidiary currency symbol. - Classes by class_id, locations by location_id, and departments by department_id from the transaction line. - Keep only rows where is_income_statement is true and the transaction accounting period equals the reporting accounting period. - Select identifiers and attributes from the joined tables, including reporting period, account, subsidiary, class, location, department, and account_category. - Derivations: - account_number_and_name: join account_number and account_name with a single "-" (no spaces); if either input is NULL, the result is NULL. - income_statement_sort_helper: map the lowercase account_type_name as income→1, cogs→2, expense→3, othincome→4, othexpense→5; otherwise NULL. - converted_amount: negate converted_amount_using_transaction_accounting_period; transaction_amount: negate unconverted_amount; NULLs propagate. - Surrogate key income_statement_id: MD5 of transaction_line_id, transaction_id, accounting_period_id, and account_name joined by underscores; if any component is NULL, the key is NULL. - No aggregation or de-duplication is performed; duplicates from sources are preserved.'
      columns:
      - name: income_statement_id
        data_type: VARCHAR
        description: MD5 of transaction_line_id, transaction_id, accounting_period_id, and account_name joined with '_' (NULL in any component yields NULL)
      - name: transaction_id
        data_type: VARCHAR
        description: Source transaction identifier from int_netsuite2__tran_with_converted_amounts
      - name: transaction_line_id
        data_type: VARCHAR
        description: Source transaction line identifier aligned via int_netsuite2__transaction_lines
      - name: accounting_period_id
        data_type: VARCHAR
        description: Reporting accounting period identifier from int_netsuite2__accounting_periods
      - name: accounting_period_ending
        data_type: DATE
        description: Reporting accounting period end date
      - name: accounting_period_name
        data_type: VARCHAR
        description: Reporting accounting period name
      - name: is_accounting_period_adjustment
        data_type: BOOLEAN
        description: True if the reporting accounting period is an adjustment period
      - name: is_accounting_period_closed
        data_type: BOOLEAN
        description: True if the reporting accounting period is closed
      - name: account_name
        data_type: VARCHAR
        description: Account name from intermediate.int_netsuite2__accounts
      - name: account_type_name
        data_type: VARCHAR
        description: Account type name from intermediate.int_netsuite2__accounts
      - name: account_id
        data_type: VARCHAR
        description: Account identifier from the accounts dimension
      - name: account_number
        data_type: VARCHAR
        description: Account number from intermediate.int_netsuite2__accounts
      - name: subsidiary_id
        data_type: VARCHAR
        description: Identifier of the subsidiary associated with the transaction
      - name: subsidiary_full_name
        data_type: VARCHAR
        description: Subsidiary full name from staging.stg_netsuite2__subsidiaries
      - name: subsidiary_name
        data_type: VARCHAR
        description: Subsidiary short name from staging.stg_netsuite2__subsidiaries
      - name: subsidiary_currency_symbol
        data_type: VARCHAR
        description: Currency symbol of the transaction’s subsidiary from staging.stg_netsuite2__currencies
      - name: account_number_and_name
        data_type: VARCHAR
        description: account_number and account_name joined by '-' with no spaces; NULL if either part is NULL
      - name: class_id
        data_type: VARCHAR
        description: Class identifier from the transaction line
      - name: class_full_name
        data_type: VARCHAR
        description: Full class name from staging.stg_netsuite2__classes
      - name: location_id
        data_type: VARCHAR
        description: Location identifier from the transaction line
      - name: location_full_name
        data_type: VARCHAR
        description: Full location name from staging.stg_netsuite2__locations
      - name: department_id
        data_type: VARCHAR
        description: Department identifier from the transaction line
      - name: department_full_name
        data_type: VARCHAR
        description: Full department name from staging.stg_netsuite2__departments
      - name: account_category
        data_type: VARCHAR
        description: Account category copied from int_netsuite2__tran_with_converted_amounts
      - name: income_statement_sort_helper
        data_type: INTEGER
        description: 'Sort rank from account_type_name (lowercased): income=1, cogs=2, expense=3, othincome=4, othexpense=5; else NULL'
      - name: converted_amount
        data_type: DOUBLE
        description: Negated converted_amount_using_transaction_accounting_period (NULL if source is NULL)
      - name: transaction_amount
        data_type: DOUBLE
        description: Negated unconverted_amount (NULL if source is NULL)
```

## agent 最终 SQL

S4

```sql
SELECT md5(t.transaction_line_id||'_'||t.transaction_id||'_'||p.accounting_period_id||'_'||a.name) AS income_statement_id, t.transaction_id, t.transaction_line_id, p.accounting_period_id, p.ending_at AS accounting_period_ending, p.name AS accounting_period_name, p.is_adjustment AS is_accounting_period_adjustment, p.is_closed AS is_accounting_period_closed, a.name AS account_name, a.type_name AS account_type_name, a.account_id, a.account_number, t.subsidiary_id, s.full_name AS subsidiary_full_name, s.name AS subsidiary_name, cur.symbol AS subsidiary_currency_symbol, CASE WHEN a.account_number IS NULL OR a.name IS NULL THEN NULL ELSE a.account_number||'-'||a.name END AS account_number_and_name, l.class_id, cl.full_name AS class_full_name, l.location_id, loc.full_name AS location_full_name, l.department_id, d.full_name AS department_full_name, t.account_category, CASE lower(a.type_name) WHEN 'income' THEN 1 WHEN 'cogs' THEN 2 WHEN 'expense' THEN 3 WHEN 'othincome' THEN 4 WHEN 'othexpense' THEN 5 END::INTEGER AS income_statement_sort_helper, -t.converted_amount_using_transaction_accounting_period AS converted_amount, -t.unconverted_amount AS transaction_amount FROM intermediate.int_netsuite2__tran_with_converted_amounts t JOIN intermediate.int_netsuite2__transaction_lines l ON l.transaction_id=t.transaction_id AND l.transaction_line_id=t.transaction_line_id LEFT JOIN intermediate.int_netsuite2__accounts a ON a.account_id=t.account_id JOIN intermediate.int_netsuite2__accounting_periods p ON p.accounting_period_id=t.reporting_accounting_period_id LEFT JOIN staging.stg_netsuite2__subsidiaries s ON s.subsidiary_id=t.subsidiary_id LEFT JOIN staging.stg_netsuite2__currencies cur ON cur.currency_id=s.currency_id LEFT JOIN staging.stg_netsuite2__classes cl ON cl.class_id=l.class_id LEFT JOIN staging.stg_netsuite2__locations loc ON loc.location_id=l.location_id LEFT JOIN staging.stg_netsuite2__departments d ON d.department_id=l.department_id WHERE t.is_income_statement AND t.transaction_accounting_period_id=t.reporting_accounting_period_id
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

transaction_lines as (
    select * 
    from intermediate.int_netsuite2__transaction_lines
),

classes as (
    select * 
    from staging.stg_netsuite2__classes
),

locations as (
    select * 
    from staging.stg_netsuite2__locations
),

departments as (
    select * 
    from staging.stg_netsuite2__departments
),

income_statement as (
    select
        transactions_with_converted_amounts.transaction_id,
        transactions_with_converted_amounts.transaction_line_id,

        reporting_accounting_periods.accounting_period_id as accounting_period_id,
        reporting_accounting_periods.ending_at as accounting_period_ending,
        reporting_accounting_periods.name as accounting_period_name,
        reporting_accounting_periods.is_adjustment as is_accounting_period_adjustment,
        reporting_accounting_periods.is_closed as is_accounting_period_closed,
        accounts.name as account_name,
        accounts.type_name as account_type_name,
        accounts.account_id as account_id,
        accounts.account_number,
        subsidiaries.subsidiary_id,
        subsidiaries.full_name as subsidiary_full_name,
        subsidiaries.name as subsidiary_name,
        subsidiaries_currencies.symbol as subsidiary_currency_symbol,

        (accounts.account_number || '-' || accounts.name) as account_number_and_name,
        classes.class_id,
        classes.full_name as class_full_name,

        locations.location_id,
        locations.full_name as location_full_name,
        departments.department_id,
        departments.full_name as department_full_name,

        transactions_with_converted_amounts.account_category as account_category,
        case when lower(accounts.type_name) = 'income' then 1
            when lower(accounts.type_name) = 'cogs' then 2
            when lower(accounts.type_name) = 'expense' then 3
            when lower(accounts.type_name) = 'othincome' then 4
            when lower(accounts.type_name) = 'othexpense' then 5
            else null
            end as income_statement_sort_helper,

        -converted_amount_using_transaction_accounting_period as converted_amount,
        -unconverted_amount as transaction_amount
        
    from transactions_with_converted_amounts

    join transaction_lines as transaction_lines
        on transaction_lines.transaction_line_id = transactions_with_converted_amounts.transaction_line_id
            and transaction_lines.transaction_id = transactions_with_converted_amounts.transaction_id

    left join departments 
        on departments.department_id = transaction_lines.department_id
    
    left join accounts 
        on accounts.account_id = transactions_with_converted_amounts.account_id

    left join locations
        on locations.location_id = transaction_lines.location_id

    left join classes 
        on classes.class_id = transaction_lines.class_id

    left join accounting_periods as reporting_accounting_periods 
        on reporting_accounting_periods.accounting_period_id = transactions_with_converted_amounts.reporting_accounting_period_id
    
    left join subsidiaries
        on transactions_with_converted_amounts.subsidiary_id = subsidiaries.subsidiary_id

    left join currencies subsidiaries_currencies
        on subsidiaries_currencies.currency_id = subsidiaries.currency_id

    where 1=1 -- fiscal_calendar_id filter removed for mock data compatibility
        -- and reporting_accounting_periods.fiscal_calendar_id = (select fiscal_calendar_id from subsidiaries where parent_id is null)
        and transactions_with_converted_amounts.transaction_accounting_period_id = transactions_with_converted_amounts.reporting_accounting_period_id
        and transactions_with_converted_amounts.is_income_statement
),

surrogate_key as ( 
    select 
        *,
        md5(
          cast(transaction_line_id as varchar) || '_' ||
          cast(transaction_id as varchar) || '_' ||
          cast(accounting_period_id as varchar) || '_' ||
          cast(account_name as varchar)
        ) as income_statement_id
    from income_statement
)

select *
from surrogate_key
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 219 | 219 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"income_statement_id":"03676bf5f4a529704a78cee61ae722e8"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| transaction_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| transaction_line_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| accounting_period_ending | 0 | 0 | 0 | DATE | DATE |
| accounting_period_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_accounting_period_adjustment | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_accounting_period_closed | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| account_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_type_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_number | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subsidiary_id | 219 | 219 | 219 | VARCHAR | VARCHAR |
| subsidiary_full_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subsidiary_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subsidiary_currency_symbol | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_number_and_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| class_full_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| location_full_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| department_full_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| income_statement_sort_helper | 0 | 0 | 0 | INTEGER | INTEGER |
| converted_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| transaction_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| income_statement_id | 0 | 0 | 0 | VARCHAR | VARCHAR |

subsidiary_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | NET10866067046 | null |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>6列；[{"column":"subsidiary_full_name","table_rows":219}]</code> |
| A3_constant_nonnull_column | <code>1列；[{"column":"is_accounting_period_adjustment","value":"false"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["account_type_name","account_category"],"nonnull_equal_rows":219,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["account_type_name","account_category"],"nonnull_equal_rows":219,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=4；assistant_trajectory 'int_netsuite2__income_statement':'''SELECT md5(t.transaction_line_id&#124;&#124;'_'&#124;&#124;t.transaction_id&#124;&#124;'_'&#124;&#124;p.accounting_period_id&#124;&#124;'_'&#124;&#124;a.name) AS income_statement_id, t.transaction_id, t.transaction_line_id, p.accounting_period_id, p.ending_at AS accounting_period_ending, p.name AS accounting_period_name, p.is_adjustment AS is_accounting_period_adjustment, p.is_closed AS is_accounting_period_closed, a.name AS account_name, a.type_name AS account_type_name, a.account_id, a.account_number, t.subsidiary_id, s.full_name AS subsidiary_full_name, s.name AS subsidiary_name, cur.symbol AS subsidiary_currency_symbol, CASE WHEN a.account_number IS NULL OR a.name IS NULL THEN NULL ELSE a.account_number&#124;&#124;'-'&#124;&#124;a.name END AS account_number_and_name, l.class_id, cl.full_name AS class_full_name, l.location_id, loc.full_name AS location_full_name, l.department_id, d.full_name AS department_full_name, t.account_category, CASE lower(a.type_name) WHEN 'income' THEN 1 WHEN 'cogs' THEN 2 WHEN 'expense' THEN 3 WHEN 'othincome' THEN 4 WHEN 'othexpense' THEN 5 END::INTEGER AS income_statement_sort_helper, -t.converted_amount_using_transaction_accounting_period AS converted_amount, -t.unconverted_amount AS transaction_amount FROM intermediate.int_netsuite2__tran_with_converted_amounts t JOIN intermediate.int_netsuite2__transaction_lines l ON l.transaction_id=t.transaction_id AND l.transaction_line_id=t.transaction_line_id LEFT JOIN intermediate.int_netsuite2__accounts a ON a.account_id=t.account_id JOIN intermediate.int_netsuite2__accounting_periods p ON p.accounting_period_id=t.reporting_accounting_period_id LEFT JOIN staging.stg_netsuite2__subsidiaries s ON s.subsidiary_id=t.subsidiary_id LEFT JOIN staging.stg_netsuite2__currencies cur ON cur.currency_id=s.currency_id LEFT JOIN staging.stg_netsuite2__classes cl ON cl.class_id=l.class_id LEFT JOIN staging.stg_netsuite2__locations loc ON loc.location_id=l.location_id LEFT JOIN staging.stg_netsuite2__departments d ON d.department_id=l.department_id WHERE t.is_income_statement AND t.transaction_accounting_period_id=t.reporting_accounting_period_id''',</code> |

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
| 23 | run | <code>grep -E 'ERROR - ✗ staging&#124;LINE 1' /tmp/runlog &#124; head -30; grep -A3 'ERROR - ✗ staging' /tmp/runlog</code> | 1659 | false | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_netsuite2__consolidated_exchange_rates.sql');s=p.read_text().replace('raw.netsuite2_exchange_rate_data','raw.netsuite2_consolidated_exc</code> | 0 | false | false |
| 29 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>m=Path('sql/marts')<br>passmodels={'netsuite2_balance_sheet':'intermediate.int_netsuite2__balance_sheet','netsuite2_income_statement':'intermediate.int</code> | 0 | false | false |
| 35 | run | <code>find sql/intermediate -type f -printf '%f\n' &#124; sort; grep 'ERROR - ✗' /tmp/runlog2</code> | 1304 | true | false |
| 39 | run | <code>cat &gt; /tmp/marts_more.py &lt;&lt;'PY'<br>from pathlib import Path<br>m=Path('sql/marts')<br>for name,src in [('netsuite__transaction_details','staging.stg_netsuite__transaction_lines'),('netsuite__transaction_detail</code> | 817 | false | false |
| 51 | run | <code>cat sql/intermediate/int_netsuite2__transaction_lines.sql; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('netsuite.duckdb',read_only=True)<br>for t in ['stg_netsuite2__transaction_lines','int_netsuite2_</code> | 7032 | false | false |

### agent action 的 thought/message 命中原句

event 17 / message

```text
'int_netsuite2__income_statement':'''SELECT md5(t.transaction_line_id||'_'||t.transaction_id||'_'||p.accounting_period_id||'_'||a.name) AS income_statement_id, t.transaction_id, t.transaction_line_id, p.accounting_period_id, p.ending_at AS accounting_period_ending, p.name AS accounting_period_name, p.is_adjustment AS is_accounting_period_adjustment, p.is_closed AS is_accounting_period_closed, a.name AS account_name, a.type_name AS account_type_name, a.account_id, a.account_number, t.subsidiary_id, s.full_name AS subsidiary_full_name, s.name AS subsidiary_name, cur.symbol AS subsidiary_currency_symbol, CASE WHEN a.account_number IS NULL OR a.name IS NULL THEN NULL ELSE a.account_number||'-'||a.name END AS account_number_and_name, l.class_id, cl.full_name AS class_full_name, l.location_id, loc.full_name AS location_full_name, l.department_id, d.full_name AS department_full_name, t.account_category, CASE lower(a.type_name) WHEN 'income' THEN 1 WHEN 'cogs' THEN 2 WHEN 'expense' THEN 3 WHEN 'othincome' THEN 4 WHEN 'othexpense' THEN 5 END::INTEGER AS income_statement_sort_helper, -t.converted_amount_using_transaction_accounting_period AS converted_amount, -t.unconverted_amount AS transaction_amount FROM intermediate.int_netsuite2__tran_with_converted_amounts t JOIN intermediate.int_netsuite2__transaction_lines l ON l.transaction_id=t.transaction_id AND l.transaction_line_id=t.transaction_line_id LEFT JOIN intermediate.int_netsuite2__accounts a ON a.account_id=t.account_id JOIN intermediate.int_netsuite2__accounting_periods p ON p.accounting_period_id=t.reporting_accounting_period_id LEFT JOIN staging.stg_netsuite2__subsidiaries s ON s.subsidiary_id=t.subsidiary_id LEFT JOIN staging.stg_netsuite2__currencies cur ON cur.currency_id=s.currency_id LEFT JOIN staging.stg_netsuite2__classes cl ON cl.class_id=l.class_id LEFT JOIN staging.stg_netsuite2__locations loc ON loc.location_id=l.location_id LEFT JOIN staging.stg_netsuite2__departments d ON d.department_id=l.department_id WHERE t.is_income_statement AND t.transaction_accounting_period_id=t.reporting_accounting_period_id''',
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__income_statement.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/intermediate/int_netsuite2__income_statement.sql`
- S6: `records/006_contract_impl-013.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/result.md`
- S10: `data/022_packages_work/022_impl-013_int_netsuite2__income_statement/022_impl-013_int_netsuite2__income_statement.json`
- S11: `data/005_cs_work/impl-013/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions`
