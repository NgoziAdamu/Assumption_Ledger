# impl-015 | marts | quickbooks__general_ledger | 差异：S1；日期 原记录

## 契约完整原文

S3:1901–2000

```yaml
    - name: quickbooks__general_ledger
      description: Unified general ledger combining bill, journal entry, and payment double-entry records enriched with account attributes, signed amounts, and running balances
      grain: One row per unique_id (double-entry line item)
      source_models:
      - intermediate.int_quickbooks__bill_double_entry
      - intermediate.int_quickbooks__journal_entry_double_entry
      - intermediate.int_quickbooks__payment_double_entry
      - intermediate.int_quickbooks__account_classifications
      business_logic: '- Union all rows from intermediate.int_quickbooks__bill_double_entry, intermediate.int_quickbooks__journal_entry_double_entry, and intermediate.int_quickbooks__payment_double_entry; duplicates are preserved. - From the union, select: transaction_id, source_relation, index, transaction_date, customer_id, vendor_id, amount, converted_amount, account_id, class_id, department_id, transaction_type, transaction_source, created_at, updated_at. - Left join intermediate.int_quickbooks__account_classifications on (account_id, source_relation) to enrich account fields; if no match, account_* fields are NULL. - Compute unique_id by building a pipe-delimited string from transaction_id, source_relation, index, account_id, transaction_type, transaction_source in that exact order; treat NULL components as empty strings; hash this string with MD5 to produce a lowercase hex identifier. - Compute adjusted_amount: if account_transaction_type equals transaction_type, use amount; otherwise use amount multiplied by -1; if amount is NULL, adjusted_amount is NULL; when either type is NULL, treat as a mismatch and negate. - Compute adjusted_converted_amount the same way using converted_amount from the union (converted_amount itself is not included in the final output); NULLs propagate. - Compute running_balance as a cumulative sum of adjusted_amount within each (account_id, class_id, source_relation) partition, ordered by source_relation, transaction_date, account_id, class_id with rows unbounded preceding. - Compute running_converted_balance similarly using adjusted_converted_amount with the same partitioning and ordering. - Window ties on all ordering keys are engine-defined; cumulative sums skip NULL values and return NULL only when the entire frame is NULL. - Output one row per double-entry line enriched with account fields, signed amounts, and running balances.'
      columns:
      - name: unique_id
        data_type: VARCHAR
        description: Lowercase MD5 of the pipe-delimited string built from transaction_id, source_relation, index, account_id, transaction_type, transaction_source in that order; NULL inputs are treated as empty strings.
      - name: transaction_id
        data_type: VARCHAR
        description: Source transaction identifier from the unioned double-entry models; preserved as-is.
      - name: source_relation
        data_type: VARCHAR
        description: Originating model for the entry (bill, journal_entry, payment); used in the account join and in window partitioning and ordering.
      - name: transaction_index
        data_type: INTEGER
        description: Line index within the source transaction (from 'index'); preserved as-is.
      - name: transaction_date
        data_type: DATE
        description: Transaction posting date from source; used in window ordering.
      - name: customer_id
        data_type: VARCHAR
        description: Customer identifier associated with the transaction when applicable; may be NULL.
      - name: vendor_id
        data_type: VARCHAR
        description: Vendor identifier associated with the transaction when applicable; may be NULL.
      - name: amount
        data_type: DECIMAL(28,6)
        description: Raw amount from source used to compute adjusted_amount; may be NULL.
      - name: account_id
        data_type: VARCHAR
        description: Account identifier from source; used to join classifications and to partition running balances.
      - name: class_id
        data_type: VARCHAR
        description: Class identifier from source; used to partition running balances; may be NULL.
      - name: department_id
        data_type: VARCHAR
        description: Department identifier from source; preserved as-is; may be NULL.
      - name: account_number
        data_type: VARCHAR
        description: Account number from classifications; NULL if no account match.
      - name: account_name
        data_type: VARCHAR
        description: Account name from classifications; NULL if no account match.
      - name: is_sub_account
        data_type: BOOLEAN
        description: TRUE if the account is a sub-account per classifications; NULL if no account match.
      - name: parent_account_number
        data_type: VARCHAR
        description: Parent account number from classifications; NULL if none or no match.
      - name: parent_account_name
        data_type: VARCHAR
        description: Parent account name from classifications; NULL if none or no match.
      - name: account_type
        data_type: VARCHAR
        description: High-level account type from classifications (e.g., Asset, Liability); NULL if no match.
      - name: account_sub_type
        data_type: VARCHAR
        description: Sub-type within the account_type from classifications; NULL if no match.
      - name: financial_statement_helper
        data_type: VARCHAR
        description: Helper label from classifications indicating financial statement grouping; NULL if no match.
      - name: account_current_balance
        data_type: DECIMAL(28,6)
        description: Current account balance from classifications; NULL if no match.
      - name: account_class
        data_type: VARCHAR
        description: Classification label from classifications; NULL if no match.
      - name: transaction_type
        data_type: VARCHAR
        description: Entry type from source (e.g., Debit/Credit or analogous); determines adjusted_amount sign.
      - name: transaction_source
        data_type: VARCHAR
        description: Source subtype label from the unioned models; included in unique_id but not used in window partitioning.
      - name: account_transaction_type
        data_type: VARCHAR
        description: Account-side transaction type from classifications; compared to transaction_type to set amount sign; may be NULL.
      - name: created_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Row creation timestamp from source; preserved as-is.
      - name: updated_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Row update timestamp from source; preserved as-is.
      - name: adjusted_amount
        data_type: DECIMAL(38,6)
        description: 'Signed amount: equals amount when account_transaction_type equals transaction_type; otherwise amount multiplied by -1; NULL if amount is NULL.'
      - name: adjusted_converted_amount
        data_type: DECIMAL(38,12)
        description: 'Signed converted amount derived from source converted_amount: equals converted_amount when types match, otherwise negated; NULL if converted_amount is NULL.'
      - name: running_balance
        data_type: DECIMAL(38,6)
        description: Cumulative sum of adjusted_amount within each (account_id, class_id, source_relation) partition ordered by source_relation, transaction_date, account_id, class_id; NULLs are skipped.
      - name: running_converted_balance
        data_type: DECIMAL(38,12)
        description: Cumulative sum of adjusted_converted_amount within each (account_id, class_id, source_relation) partition ordered by source_relation, transaction_date, account_id, class_id; NULLs are skipped.
```

## agent 最终 SQL

S4

```sql
WITH entries AS (
 SELECT * FROM intermediate.int_quickbooks__bill_double_entry
 UNION ALL SELECT * FROM intermediate.int_quickbooks__journal_entry_double_entry
 UNION ALL SELECT * FROM intermediate.int_quickbooks__payment_double_entry
), enriched AS (
 SELECT e.*,a.account_number,a.name account_name,a.is_sub_account,a.parent_account_number,a.parent_account_name,a.account_type account_type,a.account_sub_type,a.financial_statement_helper,a.balance account_current_balance,a.classification account_class,a.transaction_type account_transaction_type,
 md5(concat_ws('|',coalesce(e.transaction_id,''),coalesce(e.source_relation,''),coalesce(cast(e.index as varchar),''),coalesce(e.account_id,''),coalesce(e.transaction_type,''),coalesce(e.transaction_source,''))) unique_id,
 CASE WHEN a.transaction_type=e.transaction_type THEN e.amount ELSE e.amount*-1 END adjusted_amount,
 CASE WHEN a.transaction_type=e.transaction_type THEN e.converted_amount ELSE e.converted_amount*-1 END adjusted_converted_amount
 FROM entries e LEFT JOIN intermediate.int_quickbooks__account_classifications a ON e.account_id=a.account_id AND e.source_relation=a.source_relation
), running AS (
 SELECT *,sum(adjusted_amount) OVER(PARTITION BY account_id,class_id,source_relation ORDER BY source_relation,transaction_date,account_id,class_id ROWS UNBOUNDED PRECEDING)::DECIMAL(38,6) running_balance,
 sum(adjusted_converted_amount) OVER(PARTITION BY account_id,class_id,source_relation ORDER BY source_relation,transaction_date,account_id,class_id ROWS UNBOUNDED PRECEDING)::DECIMAL(38,12) running_converted_balance FROM enriched
)
SELECT unique_id,transaction_id,source_relation,index transaction_index,transaction_date,customer_id,vendor_id,amount,account_id,class_id,department_id,account_number,account_name,is_sub_account,parent_account_number,parent_account_name,account_type,account_sub_type,financial_statement_helper,account_current_balance,account_class,transaction_type,transaction_source,account_transaction_type,created_at,updated_at,adjusted_amount,adjusted_converted_amount,running_balance,running_converted_balance FROM running
```

## gold SQL（仅供定位差异）

S5

```sql
with unioned_models as (
    select * from intermediate.int_quickbooks__bill_double_entry
    union all  
    select * from intermediate.int_quickbooks__journal_entry_double_entry
    union all
    select * from intermediate.int_quickbooks__payment_double_entry
),

gl_union as (
    select transaction_id,
        source_relation,
        index,
        transaction_date,
        customer_id,
        vendor_id,
        amount,
        converted_amount,
        account_id,
        class_id,
        department_id,
        transaction_type,
        transaction_source,
        created_at,
        updated_at
    from unioned_models
),

accounts as (
    select *
    from intermediate.int_quickbooks__account_classifications
),

adjusted_gl as (
    select
        md5(concat(gl_union.transaction_id, '|', gl_union.source_relation, '|', gl_union.index, '|',
            gl_union.account_id, '|', gl_union.transaction_type, '|', gl_union.transaction_source)) 
            as unique_id,
        gl_union.transaction_id,
        gl_union.source_relation,
        gl_union.index as transaction_index,
        gl_union.transaction_date,
        gl_union.customer_id,
        gl_union.vendor_id,
        gl_union.amount,
        gl_union.account_id,
        gl_union.class_id,
        gl_union.department_id,
        accounts.account_number,
        accounts.name as account_name,
        accounts.is_sub_account,
        accounts.parent_account_number,
        accounts.parent_account_name,
        accounts.account_type,
        accounts.account_sub_type,
        accounts.financial_statement_helper,
        accounts.balance as account_current_balance,
        accounts.classification as account_class,
        gl_union.transaction_type,
        gl_union.transaction_source,
        accounts.transaction_type as account_transaction_type,
        gl_union.created_at,
        gl_union.updated_at,
        case when accounts.transaction_type = gl_union.transaction_type
            then gl_union.amount
            else gl_union.amount * -1
        end as adjusted_amount,
        case when accounts.transaction_type = gl_union.transaction_type
            then gl_union.converted_amount
            else gl_union.converted_amount * -1
        end as adjusted_converted_amount
    from gl_union

    left join accounts
        on gl_union.account_id = accounts.account_id
        and gl_union.source_relation = accounts.source_relation
),

final as (
    select
        *,
        sum(adjusted_amount) over (partition by account_id, class_id, source_relation
            order by source_relation, transaction_date, account_id, class_id rows unbounded preceding) as running_balance,
        sum(adjusted_converted_amount) over (partition by account_id, class_id, source_relation
            order by source_relation, transaction_date, account_id, class_id rows unbounded preceding) as running_converted_balance
    from adjusted_gl
)

select *
from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 147000 | 147000 | 0 | 0 | 1370 | 1370 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"unique_id":"0002f2590e3814555ec9eb0a28cc87c9","transaction_id":"pay31672435987","transaction_index":"2","customer_id":"cus47489410925","vendor_id":"null","account_id":"acc36924181594","class_id":"null","department_id":"null"}</code> |
| K2 | <code>{"unique_id":"0005b3f5aa741afd8762f22c5e46eeda","transaction_id":"pay66485403485","transaction_index":"2","customer_id":"cus20939247174","vendor_id":"null","account_id":"acc94463616705","class_id":"null","department_id":"null"}</code> |
| K3 | <code>{"unique_id":"0007cdb032a94e7c949009fe7618a745","transaction_id":"pay02611670835","transaction_index":"7","customer_id":"cus81159062396","vendor_id":"null","account_id":"acc11345168464","class_id":"null","department_id":"null"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| unique_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| transaction_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| transaction_index | 0 | 0 | 0 | INTEGER | INTEGER |
| customer_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| vendor_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| amount | 0 | 0 | 0 | DECIMAL(28,6) | DECIMAL(28,6) |
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| class_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| department_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_number | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| parent_account_number | 0 | 0 | 0 | VARCHAR | VARCHAR |
| parent_account_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_sub_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| financial_statement_helper | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_class | 0 | 0 | 0 | VARCHAR | VARCHAR |
| transaction_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| transaction_source | 0 | 0 | 0 | VARCHAR | VARCHAR |
| adjusted_amount | 0 | 0 | 0 | DECIMAL(38,6) | DECIMAL(38,6) |
| adjusted_converted_amount | 0 | 0 | 0 | DECIMAL(38,12) | DECIMAL(38,12) |
| running_balance | 22781 | 22781 | 22781 | DECIMAL(38,6) | DECIMAL(38,6) |
| running_converted_balance | 22781 | 22781 | 22781 | DECIMAL(38,12) | DECIMAL(38,12) |

running_balance 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | -11894784.350000 | -11912693.480000 |
| K2 | -1157637.590000 | -1148148.930000 |
| K3 | 45861.490000 | 60900.150000 |

running_converted_balance 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | -11894784.350000000000 | -11912693.480000000000 |
| K2 | -1157637.590000000000 | -1148148.930000000000 |
| K3 | 45861.490000000000 | 60900.150000000000 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

| 约束 | 列 | 违反计数 |
|---|---|---|
| grain | unique_id | <code>{"distinct_key_groups":105127,"duplicate_key_groups":28428,"rows_in_duplicate_groups":70301,"excess_duplicate_rows":41873,"null_key_rows":0,"nonnull_duplicate_key_groups":28428,"nonnull_rows_in_duplicate_groups":70301,"nonnull_excess_duplicate_rows":41873,"null_containing_duplicate_key_groups":0,"rows_in_null_containing_duplicate_groups":0}</code> |

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>2列；[{"column":"created_at","table_rows":147000},{"column":"updated_at","table_rows":147000}]</code> |
| A3_constant_nonnull_column | <code>1列；[{"column":"source_relation","value":"quickbooks"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["account_type","account_sub_type"],"nonnull_equal_rows":144175,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["account_type","account_sub_type"],"nonnull_equal_rows":144175,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：75；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions/b532323f-3e6c-45-9be5564f8a80cd2/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 9 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 12257 | true | false |
| 25 | run | <code>cat &gt; sql/intermediate/int_quickbooks__account_classifications.sql &lt;&lt;'SQL'<br>WITH account_base AS (<br>    SELECT * FROM staging.stg_quickbooks__account<br>),<br>classified AS (<br>    SELECT a.*,<br>        COALESCE(</code> | 0 | false | false |
| 27 | run | <code>cat &gt; sql/intermediate/int_quickbooks__invoice_double_entry.sql &lt;&lt;'SQL'<br>WITH ar_accounts AS (<br> SELECT account_id,source_relation FROM staging.stg_quickbooks__account WHERE account_type='Accounts Recei</code> | 0 | false | false |
| 33 | run | <code>cat &gt; sql/marts/quickbooks__general_ledger.sql &lt;&lt;'SQL'<br>WITH entries AS (<br> SELECT * FROM intermediate.int_quickbooks__bill_double_entry<br> UNION ALL SELECT * FROM intermediate.int_quickbooks__journal_ent</code> | 0 | false | false |
| 39 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 7253 | true | false |
| 41 | run | <code>grep -E 'ERROR - ✗&#124;Executing: staging&#124;staging\.' /tmp/runlog &#124; head -100</code> | 6111 | true | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>p='run.py';s=open(p).read();old='''                    self.conn.execute(f"ATTACH '{self.source_db_path}' AS source_db")<br>                    create_sql = f"CREATE OR REPLACE TABLE raw.</code> | 3827 | true | false |
| 61 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob,os<br>c=duckdb.connect('quickbooks.duckdb',read_only=True)<br>for s in ['staging','intermediate','marts']:<br> print('\n',s)<br> for (t,) in c.execute(f"select table_name from i</code> | 1080 | true | false |

### agent action 的 thought/message 命中原句

event 33 / message

```text
Running command: cat > sql/marts/quickbooks__general_ledger.sql <<'SQL'
```
event 33 / message

```text
FROM marts.quickbooks__general_ledger WHERE financial_statement_helper='balance_sheet'
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-015.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-015/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/sql/marts/quickbooks__general_ledger.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-015/sql/marts/quickbooks__general_ledger.sql`
- S6: `records/006_contract_impl-015.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/dacomp-de-impl-015/workspace/result.md`
- S10: `data/023_packages_work/023_impl-015_quickbooks__general_ledger/023_impl-015_quickbooks__general_ledger.json`
- S11: `data/005_cs_work/impl-015_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-015/quickbooks.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-015/agent/.events/sessions`
