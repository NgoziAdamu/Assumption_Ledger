# impl-013 | staging | stg_netsuite2__entities | 差异：S1；日期 原记录

## 契约完整原文

S3:145–170

```yaml
    - name: stg_netsuite2__entities
      description: "Master entity table including customers, vendors, and other business entities"
      source_table: raw.netsuite2_entity_data
      columns:
        - name: entity_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: parent_id
          data_type: VARCHAR
        - name: entity_name
          data_type: VARCHAR
        - name: entity_type
          data_type: VARCHAR
        - name: is_person
          data_type: BOOLEAN
        - name: contact_id
          data_type: DOUBLE
        - name: customer_id
          data_type: VARCHAR
        - name: employee_id
          data_type: DOUBLE
        - name: job_id
          data_type: DOUBLE
        - name: vendor_id
          data_type: DOUBLE

```

## agent 最终 SQL

S4

```sql
WITH source_data AS (
    SELECT
    CAST(NULL AS VARCHAR) AS entity_id,
    CAST(NULL AS VARCHAR) AS parent_id,
    CAST(NULL AS VARCHAR) AS entity_name,
    CAST(NULL AS VARCHAR) AS entity_type,
    CAST(NULL AS BOOLEAN) AS is_person,
    CAST(NULL AS DOUBLE) AS contact_id,
    CAST(NULL AS VARCHAR) AS customer_id,
    CAST(NULL AS DOUBLE) AS employee_id,
    CAST(NULL AS DOUBLE) AS job_id,
    CAST(NULL AS DOUBLE) AS vendor_id
    FROM raw.netsuite2_entities_data r
)
SELECT *
FROM source_data
WHERE entity_id IS NOT NULL
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select *
    from raw.netsuite2_entities_data
    -- Removed date_deleted filter for mock data
),

final as (
    select
        id as entity_id,
        parent as parent_id,
        entitytitle as entity_name,
        type as entity_type,
        isperson = 'T' as is_person,
        try_cast(contact as double) as contact_id,
        cast(customer as varchar) as customer_id,
        try_cast(employee as double) as employee_id,
        try_cast(project as double) as job_id,
        try_cast(vendor as double) as vendor_id
    from base
)

select *
from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 0 | 700 | 0 | 700 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| entity_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| entity_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| entity_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| customer_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| employee_id | 0 | 0 | 0 | DOUBLE | DOUBLE |
| job_id | 0 | 0 | 0 | DOUBLE | DOUBLE |
| vendor_id | 0 | 0 | 0 | DOUBLE | DOUBLE |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"entity_id":"NET00059457051"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A1_zero_rows | 行数=0 |
| B5_null_literal_output | <code>10输出列；[{"column":"entity_id","expression":["CAST(NULL AS TEXT)"]}]</code> |
| B7_specified_not_read | <code>["raw.netsuite2_entity_data"]</code> |
| B7_read_not_specified | <code>["raw.netsuite2_entities_data"]</code> |
| D10_keyword_in_any_result_field | <code>命中数=6；assistant_trajectory (p/'int_netsuite2__data_quality_metrics.sql').write_text("""WITH stats AS (SELECT 'Transactions' table_name,count(*) total_records,count(DISTINCT transaction_id) unique_records,count(*) FILTER(WHERE transaction_id IS NULL) null_primary_keys,count(*) FILTER(WHERE transaction_date IS NULL) null_dates,count(*) FILTER(WHERE entity_id IS NULL) null_subsidiaries,count(*) FILTER(WHERE status IS NULL) null_status,min(transaction_date) earliest_date,max(transaction_date) latest_date FROM staging.stg_netsuite2__transactions UNION ALL SELECT 'Transaction lines',count(*),count(DISTINCT transaction_line_id),count(*) FILTER(WHERE transaction_line_id IS NULL),NULL,NULL,NULL,NULL,min(transaction_id),max(transaction_id) FROM staging.stg_netsuite2__transaction_lines UNION ALL SELECT 'Customers',count(*),count(DISTINCT customer_id),count(*) FILTER(WHERE customer_id IS NULL),NULL,NULL,NULL,NULL,min(company_name),max(company_name) FROM staging.stg_netsuite2__customers), integ AS (SELECT 'transaction_lines_to_transactions' check_name,count(t.transaction_id) matched,count(*) total FROM staging.stg_netsuite2__transaction_lines l LEFT JOIN staging.stg_netsuite2__transactions t USING(transaction_id) UNION ALL SELECT 'transaction_lines_to_entities',count(e.entity_id),count(*) FROM staging.stg_netsuite2__transaction_lines l LEFT JOIN staging.stg_netsuite2__entities e ON e.entity_id=l.entity_id UNION ALL SELECT 'transactions_to_entities',count(e.entity_id),count(*) FROM staging.stg_netsuite2__transactions t LEFT JOIN staging.stg_netsuite2__entities e ON e.entity_id=t.entity_id), summary AS (SELECT avg(CASE WHEN table_name='Transactions' AND null_primary_keys+null_dates+null_subsidiaries=0 THEN 100 WHEN table_name='Customers' AND null_primary_keys=0 THEN 100 WHEN table_name='Transaction lines' THEN 85 ELSE 70 END) completeness_score FROM stats) SELECT 'Data Quality Assessment' report_type,completeness_score,NULL::DOUBLE consistency_score,NULL::DOUBLE accuracy_score,NULL::DOUBLE overall_quality_score,'Assessment' quality_grade,'Assessment complete' primary_concern,'Regular Data Quality Monitoring Recommended' recommended_action,3::BIGINT tables_assessed,3::BIGINT integrity_checks_performed,4::BIGINT business_rules_validated,current_timestamp::TIMESTAMPTZ assessment_timestamp,md5(cast(current_timestamp AS VARCHAR)) quality_assessment_id FROM summary""")</code> |

## 轨迹索引（不放输出原文）

本题事件总数：67；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f &#124; sort &#124; wc -l; find sql -type f &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,220p' run.py</code> | 16959 | true | false |
| 9 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(len(c['staging_contract']['tables']),len(c['modeling_spec']['intermediate_models']),len(c['modeling_spec']['marts_mo</code> | 5234 | true | false |
| 11 | run | <code>cat test_single_sql.py; python - &lt;&lt;'PY'<br>import yaml<br>s=yaml.safe_load(open('netsuite_start.yaml'))<br>for table,cols in s.items():<br> print('\n',table,':', ', '.join(cols))<br>PY</code> | 16290 | false | false |
| 15 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/generate.py &lt;&lt;'PY'<br>import yaml, os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>raw=yaml.safe_load(open('netsuite_start.yaml'))<br># per-table</code> | 0 | false | false |
| 19 | run | <code>cat &gt;&gt; /tmp/inter.py &lt;&lt;'PY'<br>models2={<br>'int_netsuite2__customer_profitability':'''WITH tx AS (SELECT t.*, l.entity_id AS customer_id, 'Customer_'&#124;&#124;left(l.entity_id,8) AS customer_name, 'customer_'&#124;&#124;lef</code> | 0 | false | false |
| 21 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -80 /tmp/runlog</code> | 8156 | true | false |
| 23 | run | <code>grep -E 'ERROR - ✗ staging&#124;LINE 1' /tmp/runlog &#124; head -30; grep -A3 'ERROR - ✗ staging' /tmp/runlog</code> | 1659 | true | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_netsuite2__consolidated_exchange_rates.sql');s=p.read_text().replace('raw.netsuite2_exchange_rate_data','raw.netsuite2_consolidated_exc</code> | 0 | false | false |
| 27 | run | <code>cat &gt;&gt; /tmp/more.py &lt;&lt;'PY'<br>(p/'int_netsuite2__cash_flow_forecasting.sql').write_text("""WITH hist AS (SELECT * FROM intermediate.int_netsuite2__cash_flow_analysis WHERE analysis_month&gt;=date_trunc('mon</code> | 0 | false | false |
| 33 | run | <code>cat sql/intermediate/int_netsuite2__data_quality_metrics.sql; sed -n '1,60p' sql/intermediate/int_netsuite2__cash_flow_forecasting.sql</code> | 7098 | true | false |
| 41 | run | <code>grep -o 'count(DISTINCT[^)]*) total_transactions' sql/marts/netsuite2_vendor_risk_analysis.sql; head -c 1600 sql/marts/netsuite2_vendor_risk_analysis.sql; cat sql/intermediate/int_netsuite2__data_qual</code> | 3957 | true | false |
| 57 | run | <code>cat &gt; sql/intermediate/int_netsuite2__data_quality_metrics.sql &lt;&lt;'SQL'<br>WITH transaction_stats AS (<br>    SELECT<br>        'Transactions' AS table_name,<br>        count(*)::BIGINT AS total_records,<br>        c</code> | 331 | false | false |

### agent action 的 thought/message 命中原句

event 15 / message

```text
'stg_netsuite2__entities':dict(entity_id='id',entity_name='entityid',entity_type='type',is_person='isperson',contact_id='contact',customer_id='customer',employee_id='employee',job_id='project',vendor_id='vendor'),
```
event 19 / message

```text
'int_netsuite2__ar_aging_analysis':'''WITH ar AS (SELECT l.entity_id customer_id,c.company_name customer_name,c.email_address customer_email,c.phone_number customer_phone,c.receivables_account_id customer_credit_limit,t.subsidiary_id,t.converted_amount,t.transaction_id,try_cast(tr.transaction_date AS DATE) transaction_date,try_cast(tr.due_date_at AS DATE) due_date,coalesce(try_cast(tr.due_date_at AS DATE),try_cast(tr.transaction_date AS DATE)+30) calculated_due_date,date_diff('day',coalesce(try_cast(tr.due_date_at AS DATE),try_cast(tr.transaction_date AS DATE)),current_date) days_past_due FROM intermediate.int_netsuite2__transaction_details t JOIN staging.stg_netsuite2__transaction_lines l USING(transaction_line_id) LEFT JOIN staging.stg_netsuite2__entities e ON e.entity_id=l.entity_id LEFT JOIN staging.stg_netsuite2__customers c ON c.customer_id=e.customer_id LEFT JOIN staging.stg_netsuite2__transactions tr ON tr.transaction_id=t.transaction_id WHERE t.account_type_name IN ('AcctRec','UnbilledRec') AND t.converted_amount>0 AND l.entity_id IS NOT NULL), agg AS (SELECT customer_id,customer_name,customer_email,customer_phone,customer_credit_limit,subsidiary_id,sum(converted_amount) total_ar_amount,count(DISTINCT transaction_id) total_invoices,sum(converted_amount) FILTER(WHERE days_past_due>0) overdue_amount,sum(converted_amount) FILTER(WHERE days_past_due<=0) current_amount,sum(converted_amount) FILTER(WHERE days_past_due BETWEEN 1 AND 30) days_1_30_amount,sum(converted_amount) FILTER(WHERE days_past_due BETWEEN 31 AND 60) days_31_60_amount,sum(converted_amount) FILTER(WHERE days_past_due BETWEEN 61 AND 90) days_61_90_amount,sum(converted_amount) FILTER(WHERE days_past_due BETWEEN 91 AND 120) days_91_120_amount,sum(converted_amount) FILTER(WHERE days_past_due BETWEEN 121 AND 180) days_121_180_amount,sum(converted_amount) FILTER(WHERE days_past_due>180) over_180_days_amount,max(days_past_due) max_days_past_due,sum(days_past_due*converted_amount)/nullif(sum(converted_amount),0) weighted_average_days_outstanding,sum(converted_amount*CASE WHEN days_past_due<=0 THEN .98 WHEN days_past_due<=30 THEN .95 WHEN days_past_due<=60 THEN .85 WHEN days_past_due<=90 THEN .7 WHEN days_past_due<=120 THEN .5 WHEN days_past_due<=180 THEN .3 ELSE .1 END) expected_recoverable_amount,sum(converted_amount*CASE WHEN days_past_due<=0 THEN .02 WHEN days_past_due<=30 THEN .05 WHEN days_past_due<=60 THEN .15 WHEN days_past_due<=90 THEN .3 WHEN days_past_due<=120 THEN .5 WHEN days_past_due<=180 THEN .7 ELSE .9 END) expected_loss_amount,min(calculated_due_date) earliest_due_date,max(calculated_due_date) latest_due_date FROM ar GROUP BY ALL) SELECT customer_id,customer_name,customer_email,customer_phone,customer_credit_limit,subsidiary_id,total_ar_amount,coalesce(overdue_amount,0) overdue_amount,expected_recoverable_amount,expected_loss_amount,coalesce(current_amount,0) current_amount,coalesce(days_1_30_amount,0) days_1_30_amount,coalesce(days_31_60_amount,0) days_31_60_amount,coalesce(days_61_90_amount,0) days_61_90_amount,coalesce(days_91_120_amount,0) days_91_120_amount,coalesce(days_121_180_amount,0) days_121_180_amount,coalesce(over_180_days_amount,0) over_180_days_amount,coalesce(overdue_amount,0)/nullif(total_ar_amount,0) overdue_percentage,total_ar_amount/try_cast(customer_credit_limit AS DOUBLE) credit_utilization_ratio,weighted_average_days_outstanding,least(100,coalesce(overdue_amount,0)/nullif(total_ar_amount,0)*100+CASE WHEN weighted_average_days_outstanding>=180 THEN 20 WHEN weighted_average_days_outstanding>=90 THEN 15 WHEN weighted_average_days_outstanding>=60 THEN 10 WHEN weighted_average_days_outstanding>=30 THEN 5 ELSE 0 END) customer_risk_score,CASE WHEN total_ar_amount>=10000 AND overdue_amount/total_ar_amount>=.5 THEN 'Critical' WHEN total_ar_amount>=5000 AND overdue_amount/total_ar_amount>=.3 THEN 'High' WHEN overdue_amount/total_ar_amount>=.2 THEN 'Medium' WHEN overdue_amount>0 THEN 'Low' ELSE 'Monitor' END collection_priority,CASE WHEN overdue_amount/total_ar_amount>=.8 AND max_days_past_due>=180 THEN 'Consider Write-off' WHEN overdue_amount/total_ar_amount>=.6 AND max_days_past_due>=120 THEN 'Legal Action Required' WHEN overdue_amount/total_ar_amount>=.4 AND max_days_past_due>=90 THEN 'Urgent Follow-up' WHEN overdue_amount/total_ar_amount>=.2 AND max_days_past_due>=60 THEN 'Follow-up Required' WHEN overdue_amount/total_ar_amount>=.1 THEN 'Gentle Reminder' ELSE 'No Action Required' END recommended_action,CASE WHEN try_cast(customer_credit_limit AS DOUBLE)>0 AND total_ar_amount/try_cast(customer_credit_limit AS DOUBLE)>=1 THEN 'Credit Limit Exceeded' WHEN try_cast(customer_credit_limit AS DOUBLE)>0 AND total_ar_amount/try_cast(customer_credit_limit AS DOUBLE)>=.8 THEN 'Approaching Credit Limit' WHEN overdue_amount/total_ar_amount>=.3 THEN 'Credit Hold Recommended' ELSE 'Good Standing' END credit_status,CASE WHEN overdue_amount>=10000 THEN 'High Cash Flow Impact' WHEN overdue_amount>=5000 THEN 'Medium Cash Flow Impact' WHEN overdue_amount>0 THEN 'Low Cash Flow Impact' ELSE 'No Impact' END cash_flow_impact,total_invoices,max_days_past_due,CASE WHEN weighted_average_days_outstanding<=30 THEN 30 WHEN weighted_average_days_outstanding<=60 THEN 45 WHEN weighted_average_days_outstanding<=90 THEN 75 WHEN weighted_average_days_outstanding<=120 THEN 100 ELSE 150 END estimated_collection_days,earliest_due_date::TIMESTAMP earliest_due_date,latest_due_date::TIMESTAMP latest_due_date,current_date analysis_date,md5(customer_id||'_'||subsidiary_id||'_'||cast(current_date AS VARCHAR)) ar_aging_id FROM agg WHERE total_ar_amount>0''',
```
event 25 / message

```text
p=Path('sql/staging/stg_netsuite2__entities.sql');s=p.read_text().replace('raw.netsuite2_entity_data','raw.netsuite2_entities_data');p.write_text(s)
```
event 27 / message

```text
(p/'int_netsuite2__data_quality_metrics.sql').write_text("""WITH stats AS (SELECT 'Transactions' table_name,count(*) total_records,count(DISTINCT transaction_id) unique_records,count(*) FILTER(WHERE transaction_id IS NULL) null_primary_keys,count(*) FILTER(WHERE transaction_date IS NULL) null_dates,count(*) FILTER(WHERE entity_id IS NULL) null_subsidiaries,count(*) FILTER(WHERE status IS NULL) null_status,min(transaction_date) earliest_date,max(transaction_date) latest_date FROM staging.stg_netsuite2__transactions UNION ALL SELECT 'Transaction lines',count(*),count(DISTINCT transaction_line_id),count(*) FILTER(WHERE transaction_line_id IS NULL),NULL,NULL,NULL,NULL,min(transaction_id),max(transaction_id) FROM staging.stg_netsuite2__transaction_lines UNION ALL SELECT 'Customers',count(*),count(DISTINCT customer_id),count(*) FILTER(WHERE customer_id IS NULL),NULL,NULL,NULL,NULL,min(company_name),max(company_name) FROM staging.stg_netsuite2__customers), integ AS (SELECT 'transaction_lines_to_transactions' check_name,count(t.transaction_id) matched,count(*) total FROM staging.stg_netsuite2__transaction_lines l LEFT JOIN staging.stg_netsuite2__transactions t USING(transaction_id) UNION ALL SELECT 'transaction_lines_to_entities',count(e.entity_id),count(*) FROM staging.stg_netsuite2__transaction_lines l LEFT JOIN staging.stg_netsuite2__entities e ON e.entity_id=l.entity_id UNION ALL SELECT 'transactions_to_entities',count(e.entity_id),count(*) FROM staging.stg_netsuite2__transactions t LEFT JOIN staging.stg_netsuite2__entities e ON e.entity_id=t.entity_id), summary AS (SELECT avg(CASE WHEN table_name='Transactions' AND null_primary_keys+null_dates+null_subsidiaries=0 THEN 100 WHEN table_name='Customers' AND null_primary_keys=0 THEN 100 WHEN table_name='Transaction lines' THEN 85 ELSE 70 END) completeness_score FROM stats) SELECT 'Data Quality Assessment' report_type,completeness_score,NULL::DOUBLE consistency_score,NULL::DOUBLE accuracy_score,NULL::DOUBLE overall_quality_score,'Assessment' quality_grade,'Assessment complete' primary_concern,'Regular Data Quality Monitoring Recommended' recommended_action,3::BIGINT tables_assessed,3::BIGINT integrity_checks_performed,4::BIGINT business_rules_validated,current_timestamp::TIMESTAMPTZ assessment_timestamp,md5(cast(current_timestamp AS VARCHAR)) quality_assessment_id FROM summary""")
```
event 57 / message

```text
    LEFT JOIN staging.stg_netsuite2__entities e ON e.entity_id = l.entity_id
```
event 57 / message

```text
    LEFT JOIN staging.stg_netsuite2__entities e ON e.entity_id = t.entity_id
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-013.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/staging/stg_netsuite2__entities.sql`
- S6: `records/006_contract_impl-013.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/result.md`
- S10: `data/022_packages_work/022_impl-013_stg_netsuite2__entities/022_impl-013_stg_netsuite2__entities.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions`
