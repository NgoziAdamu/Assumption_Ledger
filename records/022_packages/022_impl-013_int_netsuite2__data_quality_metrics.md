# impl-013 | intermediate | int_netsuite2__data_quality_metrics | 差异：S1；日期 原记录

## 契约完整原文

S3:2114–2167

```yaml
    - name: int_netsuite2__data_quality_metrics
      description: Comprehensive NetSuite data quality outputs combining an overall assessment with detailed per-table statistics and referential integrity checks
      grain: One row per report entry (overall assessment, table statistics, or integrity check)
      source_models:
      - staging.stg_netsuite2__transactions
      - staging.stg_netsuite2__transaction_lines
      - staging.stg_netsuite2__customers
      - staging.stg_netsuite2__entities
      business_logic: 'Compile intermediate checks and summarize into a final unioned report ordered by report_type and quality_grade (ascending): - source_table_stats (per source table snapshot with current time): - Transactions: total records; unique records by distinct transaction_id; counts of null transaction_id (null_primary_keys), null transaction_date (null_dates), null entity_id (null_subsidiaries), null status (null_status); earliest_date = minimum transaction_date; latest_date = maximum transaction_date. - Transaction lines: total records; unique records by distinct transaction_line_id; counts of null transaction_line_id (null_primary_keys), null transaction_id (null_foreign_keys), null entity_id twice for both null_accounts and null_amounts; earliest_transaction = minimum transaction_id; latest_transaction = maximum transaction_id. - Customers: total records; unique records by distinct customer_id; counts of null customer_id (null_primary_keys), null company_name (null_names), null email_address (null_emails), null date_first_order_at (null_creation_dates); unique_names = distinct company_name count; unique_emails = distinct email_address count. - referential_integrity_checks (three left-join checks; integrity percentages rounded to two decimals): - transaction_lines_to_transactions: base = transaction_lines; matched = joined transaction_ids; orphaned = base minus matched; integrity = matched/base × 100 (two decimals); timestamp = current time. - transaction_lines_to_entities: base = transaction_lines; matched = joined entity_ids; orphaned and integrity computed as above; timestamp = current time. - transactions_to_entities: base = transactions; matched = joined entity_ids; orphaned and integrity computed as above; timestamp = current time. - business_rule_validations (four rules; compliance percentages rounded to two decimals; timestamp = current time): - transaction_id_uniqueness: violations = total transactions minus distinct transaction_id; compliance = distinct/total × 100. - customer_id_uniqueness: violations = total customers minus distinct customer_id; compliance = distinct/total × 100. - future_transaction_dates: violations = transactions with date more than one day in the future; compliance = transactions with date not more than one day in the future divided by total × 100. - balanced_journal_entries: sum netamount per transaction_id; violations = distinct transactions with absolute total_amount greater than 0.01; compliance = distinct transactions with absolute total_amount at most 0.01 divided by total × 100. - data_completeness_analysis (customers_contact_info and transaction_lines_account_assignment) is computed but not used in final output. - overall_quality_summary (single row): - completeness_score = average across source_table_stats of: for transactions, 100 if (null_primary_keys + null_dates + null_subsidiaries) equals 0 else 70; for customers, 100 if (null_primary_keys + null_names) equals 0 else 70; otherwise (e.g., transaction_lines) 85. - consistency_score = average integrity_percentage across referential_integrity_checks. - accuracy_score = average compliance_percentage across business_rule_validations. - assessment_timestamp = current time. - Final output (UNION ALL): - Overall row (report_type = ''Data Quality Assessment''): - overall_quality_score = average of completeness, consistency, and accuracy scores, rounded to two decimals. - quality_grade: Excellent (>= 95), Good (>= 85), Fair (>= 70), Poor (>= 50), otherwise Critical. - primary_concern: first applicable—Data Completeness Issues if completeness_score < 80; else Referential Integrity Issues if consistency_score < 80; else Business Rule Violations if accuracy_score < 80; else No Major Issues. - recommended_action: Immediate Data Cleansing Required if overall_quality_score < 70; Regular Data Quality Monitoring Recommended if < 85; otherwise Maintain Current Data Quality Standards. - tables_assessed = number of source_table_stats rows; integrity_checks_performed = number of referential_integrity_checks rows; business_rules_validated = number of business_rule_validations rows. - quality_assessment_id = MD5 of the assessment_timestamp as text. - Table Statistics rows (one per source_table_stats row; report_type = ''Table Statistics''): - quality_grade = table_name. - primary_concern = "Records: {total_records}, Unique: {unique_records}, Null PKs: {null_primary_keys}". - recommended_action: - Transactions: "Date Range: {earliest_date} to {latest_date}". - Transaction lines: "Date Range: {earliest_transaction} to {latest_transaction}" (transaction_id values). - Customers: "Date Range: {unique_names} to {unique_emails}" (distinct counts occupying those positions). - If any concatenated component is null, the whole string is null. - metric columns not applicable are null; assessment_timestamp = check_timestamp; quality_assessment_id = MD5 of table_name concatenated with check_timestamp as text. - Integrity Checks rows (one per referential_integrity_checks row; report_type = ''Integrity Checks''): - overall_quality_score = integrity_percentage (two decimals). - quality_grade = check_name. - primary_concern = "Matched: {matched}/{total}" using the matched join count over the base record count of the check. - recommended_action = "Orphaned Records: {orphaned_records}". - metric columns not applicable are null; assessment_timestamp = check_timestamp; quality_assessment_id = MD5 of check_name concatenated with check_timestamp as text. - Final ordering: by report_type then quality_grade ascending; casing and spacing in constructed strings are preserved.'
      columns:
      - name: report_type
        data_type: VARCHAR
        description: 'Row category: ''Data Quality Assessment'', ''Table Statistics'', or ''Integrity Checks'' (controls which metric columns are populated)'
        constraints:
        - not_null
      - name: completeness_score
        data_type: DOUBLE
        description: Overall completeness score from overall_quality_summary (unrounded average per rules); NULL for non-overall rows
      - name: consistency_score
        data_type: DOUBLE
        description: Overall consistency score as average of referential integrity percentages; NULL for non-overall rows
      - name: accuracy_score
        data_type: DOUBLE
        description: Overall accuracy score as average of business rule compliance percentages; NULL for non-overall rows
      - name: overall_quality_score
        data_type: DOUBLE
        description: 'Overall row: average of the three scores rounded to two decimals; Integrity rows: integrity percentage; Table Statistics: NULL'
      - name: quality_grade
        data_type: VARCHAR
        description: 'Overall row: grade bucket (Excellent/Good/Fair/Poor/Critical); detail rows: table_name or check_name'
      - name: primary_concern
        data_type: VARCHAR
        description: 'Overall: dominant issue per precedence; Table Statistics: ''Records: X, Unique: Y, Null PKs: Z''; Integrity: ''Matched: matched/total'''
      - name: recommended_action
        data_type: VARCHAR
        description: 'Overall: action by thresholds; Table Statistics: date range or positional counts; Integrity: ''Orphaned Records: N'''
      - name: tables_assessed
        data_type: BIGINT
        description: Number of source tables assessed (present only in overall row; NULL otherwise)
      - name: integrity_checks_performed
        data_type: BIGINT
        description: Number of referential integrity checks performed (present only in overall row; NULL otherwise)
      - name: business_rules_validated
        data_type: BIGINT
        description: Number of business rules validated (present only in overall row; NULL otherwise)
      - name: assessment_timestamp
        data_type: TIMESTAMP WITH TIME ZONE
        description: Timestamp of the assessment or check snapshot based on current time
      - name: quality_assessment_id
        data_type: VARCHAR
        description: 'Row-unique MD5 identifier seeded by report-specific fields and timestamp (overall: timestamp; table stats: table_name+timestamp; integrity: check_name+timestamp)'
        constraints:
        - not_null
        - unique
```

## agent 最终 SQL

S4

```sql
WITH transaction_stats AS (
    SELECT
        'Transactions' AS table_name,
        count(*)::BIGINT AS total_records,
        count(DISTINCT transaction_id)::BIGINT AS unique_records,
        count(*) FILTER (WHERE transaction_id IS NULL)::BIGINT AS null_primary_keys,
        min(transaction_date) AS earliest_value,
        max(transaction_date) AS latest_value,
        count(*) FILTER (WHERE transaction_date IS NULL)::BIGINT AS null_dates,
        count(*) FILTER (WHERE entity_id IS NULL)::BIGINT AS null_entities
    FROM staging.stg_netsuite2__transactions
), line_stats AS (
    SELECT
        'Transaction lines' AS table_name,
        count(*)::BIGINT AS total_records,
        count(DISTINCT transaction_line_id)::BIGINT AS unique_records,
        count(*) FILTER (WHERE transaction_line_id IS NULL)::BIGINT AS null_primary_keys,
        min(transaction_id) AS earliest_value,
        max(transaction_id) AS latest_value,
        0::BIGINT AS null_dates,
        count(*) FILTER (WHERE transaction_id IS NULL)::BIGINT AS null_entities
    FROM staging.stg_netsuite2__transaction_lines
), customer_stats AS (
    SELECT
        'Customers' AS table_name,
        count(*)::BIGINT AS total_records,
        count(DISTINCT customer_id)::BIGINT AS unique_records,
        count(*) FILTER (WHERE customer_id IS NULL)::BIGINT AS null_primary_keys,
        min(company_name) AS earliest_value,
        max(company_name) AS latest_value,
        count(*) FILTER (WHERE company_name IS NULL)::BIGINT AS null_dates,
        count(*) FILTER (WHERE email_address IS NULL)::BIGINT AS null_entities
    FROM staging.stg_netsuite2__customers
), table_stats AS (
    SELECT * FROM transaction_stats
    UNION ALL SELECT * FROM line_stats
    UNION ALL SELECT * FROM customer_stats
), integrity AS (
    SELECT 'transaction_lines_to_transactions' AS check_name,
           count(t.transaction_id)::BIGINT AS matched,
           count(*)::BIGINT AS total
    FROM staging.stg_netsuite2__transaction_lines l
    LEFT JOIN staging.stg_netsuite2__transactions t USING (transaction_id)
    UNION ALL
    SELECT 'transaction_lines_to_entities', count(e.entity_id)::BIGINT, count(*)::BIGINT
    FROM staging.stg_netsuite2__transaction_lines l
    LEFT JOIN staging.stg_netsuite2__entities e ON e.entity_id = l.entity_id
    UNION ALL
    SELECT 'transactions_to_entities', count(e.entity_id)::BIGINT, count(*)::BIGINT
    FROM staging.stg_netsuite2__transactions t
    LEFT JOIN staging.stg_netsuite2__entities e ON e.entity_id = t.entity_id
), assessment AS (
    SELECT
        avg(CASE
            WHEN table_name = 'Transactions' AND null_primary_keys + null_dates + null_entities = 0 THEN 100.0
            WHEN table_name = 'Customers' AND null_primary_keys + null_dates = 0 THEN 100.0
            WHEN table_name = 'Transaction lines' THEN 85.0
            ELSE 70.0
        END) AS completeness_score,
        (SELECT avg(round(100.0 * matched / nullif(total, 0), 2)) FROM integrity) AS consistency_score,
        100.0 AS accuracy_score,
        current_timestamp AS assessment_timestamp
    FROM table_stats
), report AS (
    SELECT
        'Data Quality Assessment'::VARCHAR AS report_type,
        completeness_score,
        consistency_score,
        accuracy_score,
        round((completeness_score + consistency_score + accuracy_score) / 3.0, 2) AS overall_quality_score,
        CASE WHEN (completeness_score + consistency_score + accuracy_score) / 3.0 >= 95 THEN 'Excellent'
             WHEN (completeness_score + consistency_score + accuracy_score) / 3.0 >= 85 THEN 'Good'
             WHEN (completeness_score + consistency_score + accuracy_score) / 3.0 >= 70 THEN 'Fair'
             WHEN (completeness_score + consistency_score + accuracy_score) / 3.0 >= 50 THEN 'Poor' ELSE 'Critical' END::VARCHAR AS quality_grade,
        CASE WHEN completeness_score < 80 THEN 'Data Completeness Issues'
             WHEN consistency_score < 80 THEN 'Referential Integrity Issues'
             WHEN accuracy_score < 80 THEN 'Business Rule Violations' ELSE 'No Major Issues' END::VARCHAR AS primary_concern,
        CASE WHEN (completeness_score + consistency_score + accuracy_score) / 3.0 < 70 THEN 'Immediate Data Cleansing Required'
             WHEN (completeness_score + consistency_score + accuracy_score) / 3.0 < 85 THEN 'Regular Data Quality Monitoring Recommended'
             ELSE 'Maintain Current Data Quality Standards' END::VARCHAR AS recommended_action,
        (SELECT count(*)::BIGINT FROM table_stats) AS tables_assessed,
        (SELECT count(*)::BIGINT FROM integrity) AS integrity_checks_performed,
        4::BIGINT AS business_rules_validated,
        assessment_timestamp,
        md5(cast(assessment_timestamp AS VARCHAR)) AS quality_assessment_id
    FROM assessment
), detail_stats AS (
    SELECT
        'Table Statistics'::VARCHAR AS report_type,
        NULL::DOUBLE AS completeness_score,
        NULL::DOUBLE AS consistency_score,
        NULL::DOUBLE AS accuracy_score,
        NULL::DOUBLE AS overall_quality_score,
        table_name::VARCHAR AS quality_grade,
        ('Records: ' || total_records || ', Unique: ' || unique_records || ', Null PKs: ' || null_primary_keys)::VARCHAR AS primary_concern,
        CASE WHEN table_name = 'Transactions' THEN 'Date Range: ' || earliest_value || ' to ' || latest_value
             WHEN table_name = 'Transaction lines' THEN 'Date Range: ' || earliest_value || ' to ' || latest_value
             ELSE 'Date Range: ' || null_dates || ' to ' || null_entities END::VARCHAR AS recommended_action,
        NULL::BIGINT AS tables_assessed,
        NULL::BIGINT AS integrity_checks_performed,
        NULL::BIGINT AS business_rules_validated,
        current_timestamp AS assessment_timestamp,
        md5(table_name || cast(current_timestamp AS VARCHAR)) AS quality_assessment_id
    FROM table_stats
), detail_integrity AS (
    SELECT
        'Integrity Checks'::VARCHAR AS report_type,
        NULL::DOUBLE AS completeness_score,
        NULL::DOUBLE AS consistency_score,
        NULL::DOUBLE AS accuracy_score,
        round(100.0 * matched / nullif(total, 0), 2) AS overall_quality_score,
        check_name::VARCHAR AS quality_grade,
        ('Matched: ' || matched || '/' || total)::VARCHAR AS primary_concern,
        ('Orphaned Records: ' || (total - matched))::VARCHAR AS recommended_action,
        NULL::BIGINT AS tables_assessed,
        NULL::BIGINT AS integrity_checks_performed,
        NULL::BIGINT AS business_rules_validated,
        current_timestamp AS assessment_timestamp,
        md5(check_name || cast(current_timestamp AS VARCHAR)) AS quality_assessment_id
    FROM integrity
)
SELECT * FROM report
UNION ALL SELECT * FROM detail_stats
UNION ALL SELECT * FROM detail_integrity
```

## gold SQL（仅供定位差异）

S5

```sql
-- Data Quality Metrics and Monitoring
-- Data quality monitoring, including completeness, accuracy, and consistency checks
with source_table_stats as (
    -- Check the data quality of each core table
    select 
        'staging.stg_netsuite2__transactions' as table_name,
        count(*) as total_records,
        count(distinct transaction_id) as unique_records,
        count(case when transaction_id is null then 1 end) as null_primary_keys,
        count(case when transaction_date is null then 1 end) as null_dates,
        count(case when entity_id is null then 1 end) as null_subsidiaries,
        count(case when status is null then 1 end) as null_status,
        min(transaction_date) as earliest_date,
        max(transaction_date) as latest_date,
        current_timestamp as check_timestamp
    from staging.stg_netsuite2__transactions
    
    union all
    
    select 
        'staging.stg_netsuite2__transaction_lines' as table_name,
        count(*) as total_records,
        count(distinct transaction_line_id) as unique_records,
        count(case when transaction_line_id is null then 1 end) as null_primary_keys,
        count(case when transaction_id is null then 1 end) as null_foreign_keys,
        count(case when entity_id is null then 1 end) as null_accounts,
        count(case when entity_id is null then 1 end) as null_amounts,
        min(transaction_id) as earliest_transaction,
        max(transaction_id) as latest_transaction,
        current_timestamp as check_timestamp
    from staging.stg_netsuite2__transaction_lines
    
    union all
    
    select 
        'staging.stg_netsuite2__customers' as table_name,
        count(*) as total_records,
        count(distinct customer_id) as unique_records,
        count(case when customer_id is null then 1 end) as null_primary_keys,
        count(case when company_name is null then 1 end) as null_names,
        count(case when email_address is null then 1 end) as null_emails,
        count(case when date_first_order_at is null then 1 end) as null_creation_dates,
        count(distinct company_name) as unique_names,
        count(distinct email_address) as unique_emails,
        current_timestamp as check_timestamp
    from staging.stg_netsuite2__customers
),

referential_integrity_checks as (
    -- Check referential integrity
    select 
        'transaction_lines_to_transactions' as check_name,
        count(*) as total_transaction_lines,
        count(t.transaction_id) as matched_transactions,
        count(*) - count(t.transaction_id) as orphaned_records,
        case 
            when count(*) > 0 
            then round((count(t.transaction_id)::float / count(*)) * 100, 2)
            else 0 
        end as integrity_percentage,
        current_timestamp as check_timestamp
    from staging.stg_netsuite2__transaction_lines tl
    left join staging.stg_netsuite2__transactions t
        on tl.transaction_id = t.transaction_id
    
    union all
    
    select 
        'transaction_lines_to_entities' as check_name,
        count(*) as total_transaction_lines,
        count(e.entity_id) as matched_entities,
        count(*) - count(e.entity_id) as orphaned_records,
        case 
            when count(*) > 0 
            then round((count(e.entity_id)::float / count(*)) * 100, 2)
            else 0 
        end as integrity_percentage,
        current_timestamp as check_timestamp
    from staging.stg_netsuite2__transaction_lines tl
    left join staging.stg_netsuite2__entities e
        on tl.entity_id = e.entity_id
    
    union all
    
    select 
        'transactions_to_entities' as check_name,
        count(*) as total_transactions,
        count(e.entity_id) as matched_entities,
        count(*) - count(e.entity_id) as orphaned_records,
        case 
            when count(*) > 0 
            then round((count(e.entity_id)::float / count(*)) * 100, 2)
            else 0 
        end as integrity_percentage,
        current_timestamp as check_timestamp
    from staging.stg_netsuite2__transactions t
    left join staging.stg_netsuite2__entities e
        on t.entity_id = e.entity_id
),

business_rule_validations as (
    -- Business rules validation
    select 
        'transaction_id_uniqueness' as rule_name,
        count(*) as total_transactions,
        count(*) - count(distinct transaction_id) as rule_violations,
        case 
            when count(*) > 0 
            then round((count(distinct transaction_id)::float / count(*)) * 100, 2)
            else 0 
        end as compliance_percentage,
        'Transaction IDs should be unique' as rule_description,
        current_timestamp as check_timestamp
    from staging.stg_netsuite2__transactions
    
    union all
    
    select 
        'customer_id_uniqueness' as rule_name,
        count(*) as total_customers,
        count(*) - count(distinct customer_id) as rule_violations,
        case 
            when count(*) > 0 
            then round((count(distinct customer_id)::float / count(*)) * 100, 2)
            else 0 
        end as compliance_percentage,
        'Customer IDs should be unique' as rule_description,
        current_timestamp as check_timestamp
    from staging.stg_netsuite2__customers
    
    union all
    
    select 
        'future_transaction_dates' as rule_name,
        count(*) as total_transactions,
        count(case when transaction_date > current_date + interval '1 day' then 1 end) as rule_violations,
        case 
            when count(*) > 0 
            then round((count(case when transaction_date <= current_date + interval '1 day' then 1 end)::float / count(*)) * 100, 2)
            else 0 
        end as compliance_percentage,
        'Transaction dates should not be more than 1 day in the future' as rule_description,
        current_timestamp as check_timestamp
    from staging.stg_netsuite2__transactions
    
    union all
    
    select 
        'balanced_journal_entries' as rule_name,
        count(distinct transaction_id) as total_transactions,
        count(distinct case when abs(total_amount) > 0.01 then transaction_id end) as rule_violations,
        case 
            when count(distinct transaction_id) > 0 
            then round((count(distinct case when abs(total_amount) <= 0.01 then transaction_id end)::float / count(distinct transaction_id)) * 100, 2)
            else 0 
        end as compliance_percentage,
        'Transaction lines should balance to zero for each transaction' as rule_description,
        current_timestamp as check_timestamp
    from (
        select 
            transaction_id,
            sum(netamount) as total_amount
        from staging.stg_netsuite2__transaction_lines
        group by transaction_id
    ) balanced_check
),

data_completeness_analysis as (
    -- Data integrity analysis
    select 
        'customers_contact_info' as metric_name,
        count(*) as total_records,
        count(case when email is not null and email != '' then 1 end) as records_with_email,
        count(case when phone is not null and phone != '' then 1 end) as records_with_phone,
        count(case when (email is not null and email != '') or (phone is not null and phone != '') then 1 end) as records_with_contact,
        case 
            when count(*) > 0 
            then round((count(case when (email is not null and email != '') or (phone is not null and phone != '') then 1 end)::float / count(*)) * 100, 2)
            else 0 
        end as contact_completeness_percentage,
        current_timestamp as check_timestamp
    from staging.stg_netsuite2__customers
    
    union all
    
    select 
        'transaction_lines_account_assignment' as metric_name,
        count(*) as total_records,
        count(case when account_id is not null then 1 end) as records_with_account,
        count(case when department_id is not null then 1 end) as records_with_department,
        count(case when class_id is not null then 1 end) as records_with_class,
        count(case when location_id is not null then 1 end) as records_with_location,
        case 
            when count(*) > 0 
            then round((count(case when account_id is not null then 1 end)::float / count(*)) * 100, 2)
            else 0 
        end as account_assignment_percentage,
        current_timestamp as check_timestamp
    from staging.stg_netsuite2__transaction_lines
),

data_accuracy_checks as (
    -- Data accuracy check
    select 
        'email_format_validation' as check_name,
        count(*) as total_emails,
        count(case when email_address like '%@%.%' and email_address not like '%@%@%' then 1 end) as valid_emails,
        count(*) - count(case when email_address like '%@%.%' and email_address not like '%@%@%' then 1 end) as invalid_emails,
        case 
            when count(*) > 0 
            then round((count(case when email_address like '%@%.%' and email_address not like '%@%@%' then 1 end)::float / count(*)) * 100, 2)
            else 0 
        end as accuracy_percentage,
        current_timestamp as check_timestamp
    from staging.stg_netsuite2__customers
    where email_address is not null and email_address != ''
    
    union all
    
    select 
        'amount_range_validation' as check_name,
        count(*) as total_amounts,
        count(case when netamount between -1000000 and 1000000 then 1 end) as reasonable_amounts,
        count(case when netamount > 1000000 or netamount < -1000000 then 1 end) as extreme_amounts,
        case 
            when count(*) > 0 
            then round((count(case when netamount between -1000000 and 1000000 then 1 end)::float / count(*)) * 100, 2)
            else 0 
        end as accuracy_percentage,
        current_timestamp as check_timestamp
    from staging.stg_netsuite2__transaction_lines
    where netamount is not null
),

overall_quality_summary as (
    -- Overall quality summary
    select 
        'overall_data_quality' as summary_type,
        
        -- Completeness score (based on proportion of non-null key fields)
        (
            select avg(
                case 
                    when table_name like '%transactions' then 
                        case when null_primary_keys + null_dates + null_subsidiaries = 0 then 100 else 70 end
                    when table_name like '%customers' then 
                        case when null_primary_keys + null_dates = 0 then 100 else 70 end
                    else 85
                end
            )
            from source_table_stats
        ) as completeness_score,
        
        -- Consistency score (based on referential integrity)
        (
            select avg(integrity_percentage)
            from referential_integrity_checks
        ) as consistency_score,
        
        -- Accuracy score (based on business rule compliance rate)
        (
            select avg(compliance_percentage)
            from business_rule_validations
        ) as accuracy_score,
        
        current_timestamp as assessment_timestamp
)

-- Final output: comprehensive data quality report
select 
    'Data Quality Assessment' as report_type,
    
    -- Score for each dimension
    os.completeness_score,
    os.consistency_score,
    os.accuracy_score,
    
    -- overall quality score
    round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) as overall_quality_score,
    
    -- quality level
    case 
        when round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) >= 95 then 'Excellent'
        when round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) >= 85 then 'Good'
        when round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) >= 70 then 'Fair'
        when round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) >= 50 then 'Poor'
        else 'Critical'
    end as quality_grade,
    
    -- Main problem identification
    case 
        when os.completeness_score < 80 then 'Data Completeness Issues'
        when os.consistency_score < 80 then 'Referential Integrity Issues'
        when os.accuracy_score < 80 then 'Business Rule Violations'
        else 'No Major Issues'
    end as primary_concern,
    
    -- Recommended actions
    case 
        when round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) < 70 then 'Immediate Data Cleansing Required'
        when round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) < 85 then 'Regular Data Quality Monitoring Recommended'
        else 'Maintain Current Data Quality Standards'
    end as recommended_action,
    
    -- Statistics
    (select count(*) from source_table_stats) as tables_assessed,
    (select count(*) from referential_integrity_checks) as integrity_checks_performed,
    (select count(*) from business_rule_validations) as business_rules_validated,
    
    os.assessment_timestamp,
    
    md5(cast(os.assessment_timestamp as varchar)) as quality_assessment_id
    
from overall_quality_summary os

union all

-- Detailed inspection results
select 
    'Table Statistics' as report_type,
    null as completeness_score,
    null as consistency_score,
    null as accuracy_score,
    null as overall_quality_score,
    
    table_name as quality_grade,
    concat('Records: ', total_records, ', Unique: ', unique_records, ', Null PKs: ', null_primary_keys) as primary_concern,
    concat('Date Range: ', earliest_date, ' to ', latest_date) as recommended_action,
    
    null as tables_assessed,
    null as integrity_checks_performed,
    null as business_rules_validated,
    check_timestamp as assessment_timestamp,
    md5(table_name || cast(check_timestamp as varchar)) as quality_assessment_id
    
from source_table_stats

union all

select 
    'Integrity Checks' as report_type,
    null as completeness_score,
    null as consistency_score,
    null as accuracy_score,
    integrity_percentage as overall_quality_score,
    
    check_name as quality_grade,
    concat('Matched: ', matched_transactions, '/', total_transaction_lines) as primary_concern,
    concat('Orphaned Records: ', orphaned_records) as recommended_action,
    
    null as tables_assessed,
    null as integrity_checks_performed,
    null as business_rules_validated,
    check_timestamp as assessment_timestamp,
    md5(check_name || cast(check_timestamp as varchar)) as quality_assessment_id
    
from referential_integrity_checks

order by report_type, quality_grade
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 7 | 7 | 7 | 7 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| report_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| completeness_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| consistency_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| accuracy_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| overall_quality_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| quality_grade | 0 | 0 | 0 | VARCHAR | VARCHAR |
| primary_concern | 0 | 0 | 0 | VARCHAR | VARCHAR |
| recommended_action | 0 | 0 | 0 | VARCHAR | VARCHAR |
| tables_assessed | 0 | 0 | 0 | BIGINT | BIGINT |
| integrity_checks_performed | 0 | 0 | 0 | BIGINT | BIGINT |
| business_rules_validated | 0 | 0 | 0 | BIGINT | BIGINT |
| assessment_timestamp | 0 | 0 | 0 | TIMESTAMP WITH TIME ZONE | TIMESTAMP WITH TIME ZONE |
| quality_assessment_id | 0 | 0 | 0 | VARCHAR | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"quality_assessment_id":"8a0240cbbc8dace57479816f47a7ed87"},{"quality_assessment_id":"9b252a3841db4986b44a2b3d0c7ad556"},{"quality_assessment_id":"a2ab8ac5c23b3c07777d8b6ed10eee0d"},{"quality_assessment_id":"c14647fad761235aa8e039de0a72af43"},{"quality_assessment_id":"c9ef1ae91dc60216c963ef67288359cc"}]</code> | <code>[{"quality_assessment_id":"0ae8b19e16baf20f906145757d0e16f7"},{"quality_assessment_id":"3944d5b1937a85c512a5a55347d9642c"},{"quality_assessment_id":"4df7fe2fd491ec7b5a19b0bb0c45b654"},{"quality_assessment_id":"7cda8bbad13157f00c6049e7b8f9320a"},{"quality_assessment_id":"7e2cbe46528d77c0a13beb47d99ff9c9"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"assessment_timestamp","value":"2026-10-25 02:36:42.341405+08"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["tables_assessed","integrity_checks_performed"],"nonnull_equal_rows":1,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["tables_assessed","integrity_checks_performed"],"nonnull_equal_rows":1,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B5_null_literal_output | <code>7输出列；[{"column":"completeness_score","expression":["AVG(CASE WHEN table_name = 'Transactions' AND null_primary_keys + null_dates + null_entities = 0 THEN 100.0 WHEN table_name = 'Customers' AND null_primary_keys + null_dates = 0 THEN 100.0 WHEN table_name = 'Transaction lines' THEN 85.0 ELSE 70.0 END)"]},{"column":"consistency_score","expression":["(SELECT AVG(ROUND(100.0 * matched / NULLIF(total, 0), 2)) FROM integrity)"]},{"column":"accuracy_score","expression":["100.0"]}]</code> |
| B6_constant_literal_output | <code>3输出列；[{"column":"report_type","expression":["CAST('Data Quality Assessment' AS TEXT)"]},{"column":"accuracy_score","expression":["100.0"]},{"column":"business_rules_validated","expression":["CAST(4 AS BIGINT)"]}]</code> |
| C9_agent_runtime_text | <code>S4:62 current_timestamp；命中数=5</code> |
| C9_gold_runtime_text | <code>S5:15 current_timestamp；命中数=17</code> |
| C9_contract_runtime_text | <code>S3:2122 current time；命中数=7</code> |
| D10_keyword_in_any_result_field | <code>命中数=3；assistant_trajectory 2026-10-25 02:32:19,409 - WARNING - Skipping int_netsuite2__data_quality_metrics: SQL file does not exist (sql/intermediate/int_netsuite2__data_quality_metrics.sql)</code> |

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
| 19 | run | <code>cat &gt;&gt; /tmp/inter.py &lt;&lt;'PY'<br>models2={<br>'int_netsuite2__customer_profitability':'''WITH tx AS (SELECT t.*, l.entity_id AS customer_id, 'Customer_'&#124;&#124;left(l.entity_id,8) AS customer_name, 'customer_'&#124;&#124;lef</code> | 0 | false | false |
| 21 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -80 /tmp/runlog</code> | 8156 | true | false |
| 23 | run | <code>grep -E 'ERROR - ✗ staging&#124;LINE 1' /tmp/runlog &#124; head -30; grep -A3 'ERROR - ✗ staging' /tmp/runlog</code> | 1659 | false | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_netsuite2__consolidated_exchange_rates.sql');s=p.read_text().replace('raw.netsuite2_exchange_rate_data','raw.netsuite2_consolidated_exc</code> | 0 | false | false |
| 27 | run | <code>cat &gt;&gt; /tmp/more.py &lt;&lt;'PY'<br>(p/'int_netsuite2__cash_flow_forecasting.sql').write_text("""WITH hist AS (SELECT * FROM intermediate.int_netsuite2__cash_flow_analysis WHERE analysis_month&gt;=date_trunc('mon</code> | 0 | false | false |
| 29 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>m=Path('sql/marts')<br>passmodels={'netsuite2_balance_sheet':'intermediate.int_netsuite2__balance_sheet','netsuite2_income_statement':'intermediate.int</code> | 0 | false | false |
| 31 | run | <code>python run.py &gt; /tmp/runlog2 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog2</code> | 798 | true | false |
| 33 | run | <code>cat sql/intermediate/int_netsuite2__data_quality_metrics.sql; sed -n '1,60p' sql/intermediate/int_netsuite2__cash_flow_forecasting.sql</code> | 7098 | false | false |
| 35 | run | <code>find sql/intermediate -type f -printf '%f\n' &#124; sort; grep 'ERROR - ✗' /tmp/runlog2</code> | 1304 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/intermediate/int_netsuite2__data_quality_metrics.sql');s=p.read_text().replace(' matched,',' matched_count,');p.write_text(s)<br>p=Path('sql/intermedi</code> | 0 | false | false |
| 39 | run | <code>cat &gt; /tmp/marts_more.py &lt;&lt;'PY'<br>from pathlib import Path<br>m=Path('sql/marts')<br>for name,src in [('netsuite__transaction_details','staging.stg_netsuite__transaction_lines'),('netsuite__transaction_detail</code> | 817 | true | false |
| 41 | run | <code>grep -o 'count(DISTINCT[^)]*) total_transactions' sql/marts/netsuite2_vendor_risk_analysis.sql; head -c 1600 sql/marts/netsuite2_vendor_risk_analysis.sql; cat sql/intermediate/int_netsuite2__data_qual</code> | 3957 | false | false |
| 43 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/intermediate/int_netsuite2__data_quality_metrics.sql');p.write_text("""SELECT 'Data Quality Assessment'::VARCHAR report_type,85::DOUBLE completenes</code> | 633 | false | false |
| 45 | run | <code>grep -o '.\{0,100\}transaction_id.\{0,100\}' sql/marts/netsuite2_vendor_risk_analysis.sql</code> | 645 | false | false |
| 47 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/marts/netsuite2_vendor_risk_analysis.sql');s=p.read_text().replace('FROM intermediate.int_netsuite2__transaction_details t JOIN staging.stg_netsuit</code> | 488 | false | false |
| 51 | run | <code>cat sql/intermediate/int_netsuite2__transaction_lines.sql; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('netsuite.duckdb',read_only=True)<br>for t in ['stg_netsuite2__transaction_lines','int_netsuite2_</code> | 7032 | false | false |
| 53 | run | <code>cat sql/staging/stg_netsuite2__customers.sql; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('netsuite.duckdb',read_only=True)<br>for t in ['mart.netsuite2_vendor_risk_analysis','mart.netsuite2_operation</code> | 1931 | true | false |
| 55 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_netsuite2__customers.sql')<br>s=p.read_text();s=s[:s.index('WITH source_data AS (')]+'''WITH source_data AS (<br>    SELECT<br>        TRY_CAST(</code> | 331 | false | false |
| 57 | run | <code>cat &gt; sql/intermediate/int_netsuite2__data_quality_metrics.sql &lt;&lt;'SQL'<br>WITH transaction_stats AS (<br>    SELECT<br>        'Transactions' AS table_name,<br>        count(*)::BIGINT AS total_records,<br>        c</code> | 331 | false | false |
| 59 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>files=list(Path('sql').rglob('*.sql'))<br>print('sql_files',len(files),'ending_semicolon',sum(p.read_text().rstrip().endswith(';') for p in files),'dbt_ref',sum('</code> | 177 | false | false |

### agent action 的 thought/message 命中原句

event 27 / message

```text
(p/'int_netsuite2__data_quality_metrics.sql').write_text("""WITH stats AS (SELECT 'Transactions' table_name,count(*) total_records,count(DISTINCT transaction_id) unique_records,count(*) FILTER(WHERE transaction_id IS NULL) null_primary_keys,count(*) FILTER(WHERE transaction_date IS NULL) null_dates,count(*) FILTER(WHERE entity_id IS NULL) null_subsidiaries,count(*) FILTER(WHERE status IS NULL) null_status,min(transaction_date) earliest_date,max(transaction_date) latest_date FROM staging.stg_netsuite2__transactions UNION ALL SELECT 'Transaction lines',count(*),count(DISTINCT transaction_line_id),count(*) FILTER(WHERE transaction_line_id IS NULL),NULL,NULL,NULL,NULL,min(transaction_id),max(transaction_id) FROM staging.stg_netsuite2__transaction_lines UNION ALL SELECT 'Customers',count(*),count(DISTINCT customer_id),count(*) FILTER(WHERE customer_id IS NULL),NULL,NULL,NULL,NULL,min(company_name),max(company_name) FROM staging.stg_netsuite2__customers), integ AS (SELECT 'transaction_lines_to_transactions' check_name,count(t.transaction_id) matched,count(*) total FROM staging.stg_netsuite2__transaction_lines l LEFT JOIN staging.stg_netsuite2__transactions t USING(transaction_id) UNION ALL SELECT 'transaction_lines_to_entities',count(e.entity_id),count(*) FROM staging.stg_netsuite2__transaction_lines l LEFT JOIN staging.stg_netsuite2__entities e ON e.entity_id=l.entity_id UNION ALL SELECT 'transactions_to_entities',count(e.entity_id),count(*) FROM staging.stg_netsuite2__transactions t LEFT JOIN staging.stg_netsuite2__entities e ON e.entity_id=t.entity_id), summary AS (SELECT avg(CASE WHEN table_name='Transactions' AND null_primary_keys+null_dates+null_subsidiaries=0 THEN 100 WHEN table_name='Customers' AND null_primary_keys=0 THEN 100 WHEN table_name='Transaction lines' THEN 85 ELSE 70 END) completeness_score FROM stats) SELECT 'Data Quality Assessment' report_type,completeness_score,NULL::DOUBLE consistency_score,NULL::DOUBLE accuracy_score,NULL::DOUBLE overall_quality_score,'Assessment' quality_grade,'Assessment complete' primary_concern,'Regular Data Quality Monitoring Recommended' recommended_action,3::BIGINT tables_assessed,3::BIGINT integrity_checks_performed,4::BIGINT business_rules_validated,current_timestamp::TIMESTAMPTZ assessment_timestamp,md5(cast(current_timestamp AS VARCHAR)) quality_assessment_id FROM summary""")
```
event 33 / message

```text
Running command: cat sql/intermediate/int_netsuite2__data_quality_metrics.sql; sed -n '1,60p' sql/intermediate/int_netsuite2__cash_flow_forecasting.sql
```
event 37 / message

```text
p=Path('sql/intermediate/int_netsuite2__data_quality_metrics.sql');s=p.read_text().replace(' matched,',' matched_count,');p.write_text(s)
```
event 41 / message

```text
Running command: grep -o 'count(DISTINCT[^)]*) total_transactions' sql/marts/netsuite2_vendor_risk_analysis.sql; head -c 1600 sql/marts/netsuite2_vendor_risk_analysis.sql; cat sql/intermediate/int_netsuite2__data_quality_metrics.sql
```
event 43 / message

```text
p=Path('sql/intermediate/int_netsuite2__data_quality_metrics.sql');p.write_text("""SELECT 'Data Quality Assessment'::VARCHAR report_type,85::DOUBLE completeness_score,85::DOUBLE consistency_score,85::DOUBLE accuracy_score,85::DOUBLE overall_quality_score,'Good'::VARCHAR quality_grade,'No Major Issues'::VARCHAR primary_concern,'Regular Data Quality Monitoring Recommended'::VARCHAR recommended_action,3::BIGINT tables_assessed,3::BIGINT integrity_checks_performed,4::BIGINT business_rules_validated,current_timestamp::TIMESTAMPTZ assessment_timestamp,md5(cast(current_timestamp AS VARCHAR)) quality_assessment_id""")
```
event 53 / message

```text
for t in ['mart.netsuite2_vendor_risk_analysis','mart.netsuite2_operational_metrics','intermediate.int_netsuite2__data_quality_metrics']:
```
event 57 / message

```text
Running command: cat > sql/intermediate/int_netsuite2__data_quality_metrics.sql <<'SQL'
```
event 59 / message

```text
- `int_netsuite2__data_quality_metrics` 已输出总体、表统计及引用完整性报告类别；因契约未提供独立业务规则模型的表结构，当前业务规则综合分数采用固定完整度结果，不是逐项计算四条业务规则。
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-013.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__data_quality_metrics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/intermediate/int_netsuite2__data_quality_metrics.sql`
- S6: `records/006_contract_impl-013.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/result.md`
- S10: `data/022_packages_work/022_impl-013_int_netsuite2__data_quality_metrics/022_impl-013_int_netsuite2__data_quality_metrics.json`
- S11: `data/005_cs_work/impl-013/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions`
