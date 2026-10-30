# impl-013 / int_netsuite2__data_quality_metrics（全量；v2）

## 1. 差异与结论

固定到同一留存时刻后，3条Table Statistics的短名称/全限定名称导致不同hash键。名字字符串没有规定，单项修复减少5行，为A；accuracy_score=100占位的D单修再减1行为参与因素。客户Date Range误用NULL计数可定位，但被不同键遮住，独修规模不减，不列参与因素。

主要原因：**A**；参与因素：D：accuracy_rules；把握：中；标记：已披露。

依据L0先行后格，本表用于选择主因及参与因素的尺度：**行**。

| 主项/并列项 | 类别 | 单修行减少 | 单修格减少 |
|---|---|---|---|
| table_label | A | 5 | 77 |

## 2. 来源、契约及SQL位置

- 精简材料包：[records/022_packages/022_impl-013_int_netsuite2__data_quality_metrics.md](../../records/022_packages/022_impl-013_int_netsuite2__data_quality_metrics.md)，只摘原文与机械统计。
- 完整材料JSON（可用脚本再生成，位于忽略的数据工作区）：`data/022_packages_work/022_impl-013_int_netsuite2__data_quality_metrics/022_impl-013_int_netsuite2__data_quality_metrics.json`。
- 比较结果：[022_reruns_impl-013_int_netsuite2__data_quality_metrics.json](../022_reruns_impl-013_int_netsuite2__data_quality_metrics.json)。
- 原始库一致性：`records/022_raw_reuse_audit.json`；015已做raw内容比较，022验证数据库及外部raw依赖SHA-256与015相同；未发现gold与agent原始输入不同。
- 手册：`docs/标注手册_v2.md`，未改。

契约原件：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`。

原件第2114–2167行；完整原文见材料包。

### agent SQL

`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/intermediate/int_netsuite2__data_quality_metrics.sql`；原件第1–124行。

```sql
   1: WITH transaction_stats AS (
   2:     SELECT
   3:         'Transactions' AS table_name,
   4:         count(*)::BIGINT AS total_records,
   5:         count(DISTINCT transaction_id)::BIGINT AS unique_records,
   6:         count(*) FILTER (WHERE transaction_id IS NULL)::BIGINT AS null_primary_keys,
   7:         min(transaction_date) AS earliest_value,
   8:         max(transaction_date) AS latest_value,
   9:         count(*) FILTER (WHERE transaction_date IS NULL)::BIGINT AS null_dates,
  10:         count(*) FILTER (WHERE entity_id IS NULL)::BIGINT AS null_entities
  11:     FROM staging.stg_netsuite2__transactions
  12: ), line_stats AS (
  13:     SELECT
  14:         'Transaction lines' AS table_name,
  15:         count(*)::BIGINT AS total_records,
  16:         count(DISTINCT transaction_line_id)::BIGINT AS unique_records,
  17:         count(*) FILTER (WHERE transaction_line_id IS NULL)::BIGINT AS null_primary_keys,
  18:         min(transaction_id) AS earliest_value,
  19:         max(transaction_id) AS latest_value,
  20:         0::BIGINT AS null_dates,
  21:         count(*) FILTER (WHERE transaction_id IS NULL)::BIGINT AS null_entities
  22:     FROM staging.stg_netsuite2__transaction_lines
  23: ), customer_stats AS (
  24:     SELECT
  25:         'Customers' AS table_name,
  26:         count(*)::BIGINT AS total_records,
  27:         count(DISTINCT customer_id)::BIGINT AS unique_records,
  28:         count(*) FILTER (WHERE customer_id IS NULL)::BIGINT AS null_primary_keys,
  29:         min(company_name) AS earliest_value,
  30:         max(company_name) AS latest_value,
  31:         count(*) FILTER (WHERE company_name IS NULL)::BIGINT AS null_dates,
  32:         count(*) FILTER (WHERE email_address IS NULL)::BIGINT AS null_entities
  33:     FROM staging.stg_netsuite2__customers
  34: ), table_stats AS (
  35:     SELECT * FROM transaction_stats
  36:     UNION ALL SELECT * FROM line_stats
  37:     UNION ALL SELECT * FROM customer_stats
  38: ), integrity AS (
  39:     SELECT 'transaction_lines_to_transactions' AS check_name,
  40:            count(t.transaction_id)::BIGINT AS matched,
  41:            count(*)::BIGINT AS total
  42:     FROM staging.stg_netsuite2__transaction_lines l
  43:     LEFT JOIN staging.stg_netsuite2__transactions t USING (transaction_id)
  44:     UNION ALL
  45:     SELECT 'transaction_lines_to_entities', count(e.entity_id)::BIGINT, count(*)::BIGINT
  46:     FROM staging.stg_netsuite2__transaction_lines l
  47:     LEFT JOIN staging.stg_netsuite2__entities e ON e.entity_id = l.entity_id
  48:     UNION ALL
  49:     SELECT 'transactions_to_entities', count(e.entity_id)::BIGINT, count(*)::BIGINT
  50:     FROM staging.stg_netsuite2__transactions t
  51:     LEFT JOIN staging.stg_netsuite2__entities e ON e.entity_id = t.entity_id
  52: ), assessment AS (
  53:     SELECT
  54:         avg(CASE
  55:             WHEN table_name = 'Transactions' AND null_primary_keys + null_dates + null_entities = 0 THEN 100.0
  56:             WHEN table_name = 'Customers' AND null_primary_keys + null_dates = 0 THEN 100.0
  57:             WHEN table_name = 'Transaction lines' THEN 85.0
  58:             ELSE 70.0
  59:         END) AS completeness_score,
  60:         (SELECT avg(round(100.0 * matched / nullif(total, 0), 2)) FROM integrity) AS consistency_score,
  61:         100.0 AS accuracy_score,
  62:         current_timestamp AS assessment_timestamp
  63:     FROM table_stats
  64: ), report AS (
  65:     SELECT
  66:         'Data Quality Assessment'::VARCHAR AS report_type,
  67:         completeness_score,
  68:         consistency_score,
  69:         accuracy_score,
  70:         round((completeness_score + consistency_score + accuracy_score) / 3.0, 2) AS overall_quality_score,
  71:         CASE WHEN (completeness_score + consistency_score + accuracy_score) / 3.0 >= 95 THEN 'Excellent'
  72:              WHEN (completeness_score + consistency_score + accuracy_score) / 3.0 >= 85 THEN 'Good'
  73:              WHEN (completeness_score + consistency_score + accuracy_score) / 3.0 >= 70 THEN 'Fair'
  74:              WHEN (completeness_score + consistency_score + accuracy_score) / 3.0 >= 50 THEN 'Poor' ELSE 'Critical' END::VARCHAR AS quality_grade,
  75:         CASE WHEN completeness_score < 80 THEN 'Data Completeness Issues'
  76:              WHEN consistency_score < 80 THEN 'Referential Integrity Issues'
  77:              WHEN accuracy_score < 80 THEN 'Business Rule Violations' ELSE 'No Major Issues' END::VARCHAR AS primary_concern,
  78:         CASE WHEN (completeness_score + consistency_score + accuracy_score) / 3.0 < 70 THEN 'Immediate Data Cleansing Required'
  79:              WHEN (completeness_score + consistency_score + accuracy_score) / 3.0 < 85 THEN 'Regular Data Quality Monitoring Recommended'
  80:              ELSE 'Maintain Current Data Quality Standards' END::VARCHAR AS recommended_action,
  81:         (SELECT count(*)::BIGINT FROM table_stats) AS tables_assessed,
  82:         (SELECT count(*)::BIGINT FROM integrity) AS integrity_checks_performed,
  83:         4::BIGINT AS business_rules_validated,
  84:         assessment_timestamp,
  85:         md5(cast(assessment_timestamp AS VARCHAR)) AS quality_assessment_id
  86:     FROM assessment
  87: ), detail_stats AS (
  88:     SELECT
  89:         'Table Statistics'::VARCHAR AS report_type,
  90:         NULL::DOUBLE AS completeness_score,
  91:         NULL::DOUBLE AS consistency_score,
  92:         NULL::DOUBLE AS accuracy_score,
  93:         NULL::DOUBLE AS overall_quality_score,
  94:         table_name::VARCHAR AS quality_grade,
  95:         ('Records: ' || total_records || ', Unique: ' || unique_records || ', Null PKs: ' || null_primary_keys)::VARCHAR AS primary_concern,
  96:         CASE WHEN table_name = 'Transactions' THEN 'Date Range: ' || earliest_value || ' to ' || latest_value
  97:              WHEN table_name = 'Transaction lines' THEN 'Date Range: ' || earliest_value || ' to ' || latest_value
  98:              ELSE 'Date Range: ' || null_dates || ' to ' || null_entities END::VARCHAR AS recommended_action,
  99:         NULL::BIGINT AS tables_assessed,
 100:         NULL::BIGINT AS integrity_checks_performed,
 101:         NULL::BIGINT AS business_rules_validated,
 102:         current_timestamp AS assessment_timestamp,
 103:         md5(table_name || cast(current_timestamp AS VARCHAR)) AS quality_assessment_id
 104:     FROM table_stats
 105: ), detail_integrity AS (
 106:     SELECT
 107:         'Integrity Checks'::VARCHAR AS report_type,
 108:         NULL::DOUBLE AS completeness_score,
 109:         NULL::DOUBLE AS consistency_score,
 110:         NULL::DOUBLE AS accuracy_score,
 111:         round(100.0 * matched / nullif(total, 0), 2) AS overall_quality_score,
 112:         check_name::VARCHAR AS quality_grade,
 113:         ('Matched: ' || matched || '/' || total)::VARCHAR AS primary_concern,
 114:         ('Orphaned Records: ' || (total - matched))::VARCHAR AS recommended_action,
 115:         NULL::BIGINT AS tables_assessed,
 116:         NULL::BIGINT AS integrity_checks_performed,
 117:         NULL::BIGINT AS business_rules_validated,
 118:         current_timestamp AS assessment_timestamp,
 119:         md5(check_name || cast(current_timestamp AS VARCHAR)) AS quality_assessment_id
 120:     FROM integrity
 121: )
 122: SELECT * FROM report
 123: UNION ALL SELECT * FROM detail_stats
 124: UNION ALL SELECT * FROM detail_integrity
```

### gold SQL（诊断）

`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/intermediate/int_netsuite2__data_quality_metrics.sql`；原件第1–359行。

```sql
   1: -- Data Quality Metrics and Monitoring
   2: -- Data quality monitoring, including completeness, accuracy, and consistency checks
   3: with source_table_stats as (
   4:     -- Check the data quality of each core table
   5:     select 
   6:         'staging.stg_netsuite2__transactions' as table_name,
   7:         count(*) as total_records,
   8:         count(distinct transaction_id) as unique_records,
   9:         count(case when transaction_id is null then 1 end) as null_primary_keys,
  10:         count(case when transaction_date is null then 1 end) as null_dates,
  11:         count(case when entity_id is null then 1 end) as null_subsidiaries,
  12:         count(case when status is null then 1 end) as null_status,
  13:         min(transaction_date) as earliest_date,
  14:         max(transaction_date) as latest_date,
  15:         current_timestamp as check_timestamp
  16:     from staging.stg_netsuite2__transactions
  17:     
  18:     union all
  19:     
  20:     select 
  21:         'staging.stg_netsuite2__transaction_lines' as table_name,
  22:         count(*) as total_records,
  23:         count(distinct transaction_line_id) as unique_records,
  24:         count(case when transaction_line_id is null then 1 end) as null_primary_keys,
  25:         count(case when transaction_id is null then 1 end) as null_foreign_keys,
  26:         count(case when entity_id is null then 1 end) as null_accounts,
  27:         count(case when entity_id is null then 1 end) as null_amounts,
  28:         min(transaction_id) as earliest_transaction,
  29:         max(transaction_id) as latest_transaction,
  30:         current_timestamp as check_timestamp
  31:     from staging.stg_netsuite2__transaction_lines
  32:     
  33:     union all
  34:     
  35:     select 
  36:         'staging.stg_netsuite2__customers' as table_name,
  37:         count(*) as total_records,
  38:         count(distinct customer_id) as unique_records,
  39:         count(case when customer_id is null then 1 end) as null_primary_keys,
  40:         count(case when company_name is null then 1 end) as null_names,
  41:         count(case when email_address is null then 1 end) as null_emails,
  42:         count(case when date_first_order_at is null then 1 end) as null_creation_dates,
  43:         count(distinct company_name) as unique_names,
  44:         count(distinct email_address) as unique_emails,
  45:         current_timestamp as check_timestamp
  46:     from staging.stg_netsuite2__customers
  47: ),
  48: 
  49: referential_integrity_checks as (
  50:     -- Check referential integrity
  51:     select 
  52:         'transaction_lines_to_transactions' as check_name,
  53:         count(*) as total_transaction_lines,
  54:         count(t.transaction_id) as matched_transactions,
  55:         count(*) - count(t.transaction_id) as orphaned_records,
  56:         case 
  57:             when count(*) > 0 
  58:             then round((count(t.transaction_id)::float / count(*)) * 100, 2)
  59:             else 0 
  60:         end as integrity_percentage,
  61:         current_timestamp as check_timestamp
  62:     from staging.stg_netsuite2__transaction_lines tl
  63:     left join staging.stg_netsuite2__transactions t
  64:         on tl.transaction_id = t.transaction_id
  65:     
  66:     union all
  67:     
  68:     select 
  69:         'transaction_lines_to_entities' as check_name,
  70:         count(*) as total_transaction_lines,
  71:         count(e.entity_id) as matched_entities,
  72:         count(*) - count(e.entity_id) as orphaned_records,
  73:         case 
  74:             when count(*) > 0 
  75:             then round((count(e.entity_id)::float / count(*)) * 100, 2)
  76:             else 0 
  77:         end as integrity_percentage,
  78:         current_timestamp as check_timestamp
  79:     from staging.stg_netsuite2__transaction_lines tl
  80:     left join staging.stg_netsuite2__entities e
  81:         on tl.entity_id = e.entity_id
  82:     
  83:     union all
  84:     
  85:     select 
  86:         'transactions_to_entities' as check_name,
  87:         count(*) as total_transactions,
  88:         count(e.entity_id) as matched_entities,
  89:         count(*) - count(e.entity_id) as orphaned_records,
  90:         case 
  91:             when count(*) > 0 
  92:             then round((count(e.entity_id)::float / count(*)) * 100, 2)
  93:             else 0 
  94:         end as integrity_percentage,
  95:         current_timestamp as check_timestamp
  96:     from staging.stg_netsuite2__transactions t
  97:     left join staging.stg_netsuite2__entities e
  98:         on t.entity_id = e.entity_id
  99: ),
 100: 
 101: business_rule_validations as (
 102:     -- Business rules validation
 103:     select 
 104:         'transaction_id_uniqueness' as rule_name,
 105:         count(*) as total_transactions,
 106:         count(*) - count(distinct transaction_id) as rule_violations,
 107:         case 
 108:             when count(*) > 0 
 109:             then round((count(distinct transaction_id)::float / count(*)) * 100, 2)
 110:             else 0 
 111:         end as compliance_percentage,
 112:         'Transaction IDs should be unique' as rule_description,
 113:         current_timestamp as check_timestamp
 114:     from staging.stg_netsuite2__transactions
 115:     
 116:     union all
 117:     
 118:     select 
 119:         'customer_id_uniqueness' as rule_name,
 120:         count(*) as total_customers,
 121:         count(*) - count(distinct customer_id) as rule_violations,
 122:         case 
 123:             when count(*) > 0 
 124:             then round((count(distinct customer_id)::float / count(*)) * 100, 2)
 125:             else 0 
 126:         end as compliance_percentage,
 127:         'Customer IDs should be unique' as rule_description,
 128:         current_timestamp as check_timestamp
 129:     from staging.stg_netsuite2__customers
 130:     
 131:     union all
 132:     
 133:     select 
 134:         'future_transaction_dates' as rule_name,
 135:         count(*) as total_transactions,
 136:         count(case when transaction_date > current_date + interval '1 day' then 1 end) as rule_violations,
 137:         case 
 138:             when count(*) > 0 
 139:             then round((count(case when transaction_date <= current_date + interval '1 day' then 1 end)::float / count(*)) * 100, 2)
 140:             else 0 
 141:         end as compliance_percentage,
 142:         'Transaction dates should not be more than 1 day in the future' as rule_description,
 143:         current_timestamp as check_timestamp
 144:     from staging.stg_netsuite2__transactions
 145:     
 146:     union all
 147:     
 148:     select 
 149:         'balanced_journal_entries' as rule_name,
 150:         count(distinct transaction_id) as total_transactions,
 151:         count(distinct case when abs(total_amount) > 0.01 then transaction_id end) as rule_violations,
 152:         case 
 153:             when count(distinct transaction_id) > 0 
 154:             then round((count(distinct case when abs(total_amount) <= 0.01 then transaction_id end)::float / count(distinct transaction_id)) * 100, 2)
 155:             else 0 
 156:         end as compliance_percentage,
 157:         'Transaction lines should balance to zero for each transaction' as rule_description,
 158:         current_timestamp as check_timestamp
 159:     from (
 160:         select 
 161:             transaction_id,
 162:             sum(netamount) as total_amount
 163:         from staging.stg_netsuite2__transaction_lines
 164:         group by transaction_id
 165:     ) balanced_check
 166: ),
 167: 
 168: data_completeness_analysis as (
 169:     -- Data integrity analysis
 170:     select 
 171:         'customers_contact_info' as metric_name,
 172:         count(*) as total_records,
 173:         count(case when email is not null and email != '' then 1 end) as records_with_email,
 174:         count(case when phone is not null and phone != '' then 1 end) as records_with_phone,
 175:         count(case when (email is not null and email != '') or (phone is not null and phone != '') then 1 end) as records_with_contact,
 176:         case 
 177:             when count(*) > 0 
 178:             then round((count(case when (email is not null and email != '') or (phone is not null and phone != '') then 1 end)::float / count(*)) * 100, 2)
 179:             else 0 
 180:         end as contact_completeness_percentage,
 181:         current_timestamp as check_timestamp
 182:     from staging.stg_netsuite2__customers
 183:     
 184:     union all
 185:     
 186:     select 
 187:         'transaction_lines_account_assignment' as metric_name,
 188:         count(*) as total_records,
 189:         count(case when account_id is not null then 1 end) as records_with_account,
 190:         count(case when department_id is not null then 1 end) as records_with_department,
 191:         count(case when class_id is not null then 1 end) as records_with_class,
 192:         count(case when location_id is not null then 1 end) as records_with_location,
 193:         case 
 194:             when count(*) > 0 
 195:             then round((count(case when account_id is not null then 1 end)::float / count(*)) * 100, 2)
 196:             else 0 
 197:         end as account_assignment_percentage,
 198:         current_timestamp as check_timestamp
 199:     from staging.stg_netsuite2__transaction_lines
 200: ),
 201: 
 202: data_accuracy_checks as (
 203:     -- Data accuracy check
 204:     select 
 205:         'email_format_validation' as check_name,
 206:         count(*) as total_emails,
 207:         count(case when email_address like '%@%.%' and email_address not like '%@%@%' then 1 end) as valid_emails,
 208:         count(*) - count(case when email_address like '%@%.%' and email_address not like '%@%@%' then 1 end) as invalid_emails,
 209:         case 
 210:             when count(*) > 0 
 211:             then round((count(case when email_address like '%@%.%' and email_address not like '%@%@%' then 1 end)::float / count(*)) * 100, 2)
 212:             else 0 
 213:         end as accuracy_percentage,
 214:         current_timestamp as check_timestamp
 215:     from staging.stg_netsuite2__customers
 216:     where email_address is not null and email_address != ''
 217:     
 218:     union all
 219:     
 220:     select 
 221:         'amount_range_validation' as check_name,
 222:         count(*) as total_amounts,
 223:         count(case when netamount between -1000000 and 1000000 then 1 end) as reasonable_amounts,
 224:         count(case when netamount > 1000000 or netamount < -1000000 then 1 end) as extreme_amounts,
 225:         case 
 226:             when count(*) > 0 
 227:             then round((count(case when netamount between -1000000 and 1000000 then 1 end)::float / count(*)) * 100, 2)
 228:             else 0 
 229:         end as accuracy_percentage,
 230:         current_timestamp as check_timestamp
 231:     from staging.stg_netsuite2__transaction_lines
 232:     where netamount is not null
 233: ),
 234: 
 235: overall_quality_summary as (
 236:     -- Overall quality summary
 237:     select 
 238:         'overall_data_quality' as summary_type,
 239:         
 240:         -- Completeness score (based on proportion of non-null key fields)
 241:         (
 242:             select avg(
 243:                 case 
 244:                     when table_name like '%transactions' then 
 245:                         case when null_primary_keys + null_dates + null_subsidiaries = 0 then 100 else 70 end
 246:                     when table_name like '%customers' then 
 247:                         case when null_primary_keys + null_dates = 0 then 100 else 70 end
 248:                     else 85
 249:                 end
 250:             )
 251:             from source_table_stats
 252:         ) as completeness_score,
 253:         
 254:         -- Consistency score (based on referential integrity)
 255:         (
 256:             select avg(integrity_percentage)
 257:             from referential_integrity_checks
 258:         ) as consistency_score,
 259:         
 260:         -- Accuracy score (based on business rule compliance rate)
 261:         (
 262:             select avg(compliance_percentage)
 263:             from business_rule_validations
 264:         ) as accuracy_score,
 265:         
 266:         current_timestamp as assessment_timestamp
 267: )
 268: 
 269: -- Final output: comprehensive data quality report
 270: select 
 271:     'Data Quality Assessment' as report_type,
 272:     
 273:     -- Score for each dimension
 274:     os.completeness_score,
 275:     os.consistency_score,
 276:     os.accuracy_score,
 277:     
 278:     -- overall quality score
 279:     round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) as overall_quality_score,
 280:     
 281:     -- quality level
 282:     case 
 283:         when round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) >= 95 then 'Excellent'
 284:         when round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) >= 85 then 'Good'
 285:         when round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) >= 70 then 'Fair'
 286:         when round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) >= 50 then 'Poor'
 287:         else 'Critical'
 288:     end as quality_grade,
 289:     
 290:     -- Main problem identification
 291:     case 
 292:         when os.completeness_score < 80 then 'Data Completeness Issues'
 293:         when os.consistency_score < 80 then 'Referential Integrity Issues'
 294:         when os.accuracy_score < 80 then 'Business Rule Violations'
 295:         else 'No Major Issues'
 296:     end as primary_concern,
 297:     
 298:     -- Recommended actions
 299:     case 
 300:         when round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) < 70 then 'Immediate Data Cleansing Required'
 301:         when round((os.completeness_score + os.consistency_score + os.accuracy_score) / 3, 2) < 85 then 'Regular Data Quality Monitoring Recommended'
 302:         else 'Maintain Current Data Quality Standards'
 303:     end as recommended_action,
 304:     
 305:     -- Statistics
 306:     (select count(*) from source_table_stats) as tables_assessed,
 307:     (select count(*) from referential_integrity_checks) as integrity_checks_performed,
 308:     (select count(*) from business_rule_validations) as business_rules_validated,
 309:     
 310:     os.assessment_timestamp,
 311:     
 312:     md5(cast(os.assessment_timestamp as varchar)) as quality_assessment_id
 313:     
 314: from overall_quality_summary os
 315: 
 316: union all
 317: 
 318: -- Detailed inspection results
 319: select 
 320:     'Table Statistics' as report_type,
 321:     null as completeness_score,
 322:     null as consistency_score,
 323:     null as accuracy_score,
 324:     null as overall_quality_score,
 325:     
 326:     table_name as quality_grade,
 327:     concat('Records: ', total_records, ', Unique: ', unique_records, ', Null PKs: ', null_primary_keys) as primary_concern,
 328:     concat('Date Range: ', earliest_date, ' to ', latest_date) as recommended_action,
 329:     
 330:     null as tables_assessed,
 331:     null as integrity_checks_performed,
 332:     null as business_rules_validated,
 333:     check_timestamp as assessment_timestamp,
 334:     md5(table_name || cast(check_timestamp as varchar)) as quality_assessment_id
 335:     
 336: from source_table_stats
 337: 
 338: union all
 339: 
 340: select 
 341:     'Integrity Checks' as report_type,
 342:     null as completeness_score,
 343:     null as consistency_score,
 344:     null as accuracy_score,
 345:     integrity_percentage as overall_quality_score,
 346:     
 347:     check_name as quality_grade,
 348:     concat('Matched: ', matched_transactions, '/', total_transaction_lines) as primary_concern,
 349:     concat('Orphaned Records: ', orphaned_records) as recommended_action,
 350:     
 351:     null as tables_assessed,
 352:     null as integrity_checks_performed,
 353:     null as business_rules_validated,
 354:     check_timestamp as assessment_timestamp,
 355:     md5(check_name || cast(check_timestamp as varchar)) as quality_assessment_id
 356:     
 357: from referential_integrity_checks
 358: 
 359: order by report_type, quality_grade
```

## 3. agent看到的材料与不确定性

已检视该题全部67个原始归档事件（原输出显式截断事件：[]），最终报告与写报告动作。程序读取YAML不等于把完整YAML显示给agent；不推断未留存思考。

- event 33 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/33.json`。
- event 34 / run：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/34.json`。

四档：**看到了但没提**。

未找到针对本表主项选择的说明。“看到了但没提”只表示上述实际输出包含相关schema、样例、代码/运行结果；不把写SQL本身或通用功能清单当作具体说明。“没有迹象”不推断agent内部没有意识到。

参与因素D的披露见event65：业务规则精确逐条合规率未完整验证；这是参与因素的披露，主项A的四档仍按名称选择填写。

## 4. 核实查询与诊断

核实查询共**2条**（含失败尝试），代价档：**多条查询**，≤5；只查agent当时可见库。原始库READ_ONLY；所有写表在data/022_work等私有目录。

### 核实 V1：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'staging.stg_netsuite2__customers' source_table,count(*) rows FROM staging.stg_netsuite2__customers UNION ALL SELECT 'staging.stg_netsuite2__entities' source_table,count(*) rows FROM staging.stg_netsuite2__entities UNION ALL SELECT 'staging.stg_netsuite2__transaction_lines' source_table,count(*) rows FROM staging.stg_netsuite2__transaction_lines UNION ALL SELECT 'staging.stg_netsuite2__transactions' source_table,count(*) rows FROM staging.stg_netsuite2__transactions
```

```json
{"error": "Parser Error: syntax error at or near \"rows\"\n\nLINE 1: ... 'staging.stg_netsuite2__customers' source_table,count(*) rows FROM staging.stg_netsuite2__customers UNION ALL SELECT...\n                                                                     ^"}
```

### 核实 V2：上游可见行数

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`。

```sql
SELECT 'staging.stg_netsuite2__customers' source_table,count(*) source_rows FROM staging.stg_netsuite2__customers UNION ALL SELECT 'staging.stg_netsuite2__entities' source_table,count(*) source_rows FROM staging.stg_netsuite2__entities UNION ALL SELECT 'staging.stg_netsuite2__transaction_lines' source_table,count(*) source_rows FROM staging.stg_netsuite2__transaction_lines UNION ALL SELECT 'staging.stg_netsuite2__transactions' source_table,count(*) source_rows FROM staging.stg_netsuite2__transactions
```

```json
{"columns": ["source_table", "source_rows"], "result": [["staging.stg_netsuite2__customers", 2000], ["staging.stg_netsuite2__entities", 0], ["staging.stg_netsuite2__transaction_lines", 700], ["staging.stg_netsuite2__transactions", 9997]]}
```

### 诊断（允许gold，不计5条）

`records/022_diagnostics.json` 本表条目：

```json
{"index": 9, "kind": "诊断查询", "queries": [{"label": "三类报告键和payload", "sql": "SELECT report_type,quality_grade,primary_concern,recommended_action,accuracy_score,overall_quality_score,quality_assessment_id FROM gold.intermediate.int_netsuite2__data_quality_metrics", "columns": ["report_type", "quality_grade", "primary_concern", "recommended_action", "accuracy_score", "overall_quality_score", "quality_assessment_id"], "result": [["Data Quality Assessment", "Poor", "Referential Integrity Issues", "Immediate Data Cleansing Required", 75.0, 64.44, "cea64ad3b9006b87ef2d5e9458177a3e"], ["Integrity Checks", "transaction_lines_to_entities", "Matched: 700/700", "Orphaned Records: 0", null, 100.0, "3944d5b1937a85c512a5a55347d9642c"], ["Integrity Checks", "transaction_lines_to_transactions", "Matched: 0/700", "Orphaned Records: 700", null, 0.0, "7cda8bbad13157f00c6049e7b8f9320a"], ["Integrity Checks", "transactions_to_entities", "Matched: 0/9997", "Orphaned Records: 9997", null, 0.0, "7e2cbe46528d77c0a13beb47d99ff9c9"], ["Table Statistics", "staging.stg_netsuite2__customers", "Records: 2000, Unique: 2000, Null PKs: 0", "Date Range: 1354 to 1990", null, null, "90fd22496ca53ff685290df011e3051c"], ["Table Statistics", "staging.stg_netsuite2__transaction_lines", "Records: 700, Unique: 700, Null PKs: 0", "Date Range: NET00149183622 to NET99557381359", null, null, "4df7fe2fd491ec7b5a19b0bb0c45b654"], ["Table Statistics", "staging.stg_netsuite2__transactions", "Records: 9997, Unique: 9997, Null PKs: 0", "Date Range: 2023-01-01 to 2024-12-31", null, null, "0ae8b19e16baf20f906145757d0e16f7"]]}]}
```

## 5. 单改重跑与L0–L3

输入口径：/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb。staging使用agent raw，intermediate及以后使用gold上游CS；utils依赖raw已核对三方一致。固定时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-14 10:20:49.607+08'", "count": 5}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-14'", "count": 0}]`。所有基线与单改使用相同控制；原件只读ATTACH。

键：`["quality_assessment_id"]`；比较列：`["report_type", "completeness_score", "consistency_score", "accuracy_score", "overall_quality_score", "quality_grade", "primary_concern", "recommended_action", "tables_assessed", "integrity_checks_performed", "business_rules_validated", "assessment_timestamp", "quality_assessment_id"]`。比较包含二者并集；键固定L0，L1数值/布尔归一，L2两位小数，L3再宽松日期。行规模=独有行+共同键多出行+不同配对行；格子规模=独有/多出行×比较列数+共同键不同格。重复键先抵消相同行，再按完整元组字典序配对。

### 原留存输出

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 7/7 | 7/7 | 0/0 | 0 | 14 | 182 | False |
| L1 | 7/7 | 7/7 | 0/0 | 0 | 14 | 182 | False |
| L2 | 7/7 | 7/7 | 0/0 | 0 | 14 | 182 | False |
| L3 | 7/7 | 7/7 | 0/0 | 0 | 14 | 182 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| quality_assessment_id | 0 | 0 | 0 | 0 |
| report_type | 0 | 0 | 0 | 0 |
| completeness_score | 0 | 0 | 0 | 0 |
| consistency_score | 0 | 0 | 0 | 0 |
| accuracy_score | 0 | 0 | 0 | 0 |
| overall_quality_score | 0 | 0 | 0 | 0 |
| quality_grade | 0 | 0 | 0 | 0 |
| primary_concern | 0 | 0 | 0 | 0 |
| recommended_action | 0 | 0 | 0 | 0 |
| tables_assessed | 0 | 0 | 0 | 0 |
| integrity_checks_performed | 0 | 0 | 0 | 0 |
| business_rules_validated | 0 | 0 | 0 | 0 |
| assessment_timestamp | 0 | 0 | 0 | 0 |

### baseline

SQL：`data/022_work/impl-013_int_netsuite2__data_quality_metrics/baseline.sql`；SHA-256：`1d340db74dc42847eec5abba1e97fd478b98ee8955a70dfd3b544afe95cd4615`。

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 7/7 | 3/3 | 0/0 | 1 | 7 | 82 | False |
| L1 | 7/7 | 3/3 | 0/0 | 1 | 7 | 82 | False |
| L2 | 7/7 | 3/3 | 0/0 | 1 | 7 | 82 | False |
| L3 | 7/7 | 3/3 | 0/0 | 1 | 7 | 82 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| quality_assessment_id | 0 | 0 | 0 | 0 |
| report_type | 0 | 0 | 0 | 0 |
| completeness_score | 0 | 0 | 0 | 0 |
| consistency_score | 0 | 0 | 0 | 0 |
| accuracy_score | 1 | 1 | 1 | 1 |
| overall_quality_score | 1 | 1 | 1 | 1 |
| quality_grade | 1 | 1 | 1 | 1 |
| primary_concern | 0 | 0 | 0 | 0 |
| recommended_action | 1 | 1 | 1 | 1 |
| tables_assessed | 0 | 0 | 0 | 0 |
| integrity_checks_performed | 0 | 0 | 0 | 0 |
| business_rules_validated | 0 | 0 | 0 | 0 |
| assessment_timestamp | 0 | 0 | 0 | 0 |

### accuracy_rules

SQL：`data/022_work/impl-013_int_netsuite2__data_quality_metrics/accuracy_rules.sql`；SHA-256：`8655b3ca655fd640ee102cf77682c84ea6b9e99a4f9b4bdcd9aba8ecf987f63a`。

替换offset=3012，原表达式所在行约61（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
100.0 AS accuracy_score
-- 新
(SELECT avg(compliance_percentage) FROM (-- Business rules validation
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
        TIMESTAMPTZ '2025-10-14 10:20:49.607+08' as check_timestamp
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
        TIMESTAMPTZ '2025-10-14 10:20:49.607+08' as check_timestamp
    from staging.stg_netsuite2__customers
    
    union all
    
    select 
        'future_transaction_dates' as rule_name,
        count(*) as total_transactions,
        count(case when transaction_date > DATE '2025-10-14' + interval '1 day' then 1 end) as rule_violations,
        case 
            when count(*) > 0 
            then round((count(case when transaction_date <= DATE '2025-10-14' + interval '1 day' then 1 end)::float / count(*)) * 100, 2)
            else 0 
        end as compliance_percentage,
        'Transaction dates should not be more than 1 day in the future' as rule_description,
        TIMESTAMPTZ '2025-10-14 10:20:49.607+08' as check_timestamp
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
        TIMESTAMPTZ '2025-10-14 10:20:49.607+08' as check_timestamp
    from (
        select 
            transaction_id,
            sum(netamount) as total_amount
        from staging.stg_netsuite2__transaction_lines
        group by transaction_id
    ) balanced_check) rules) AS accuracy_score
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 7/7 | 3/3 | 0/0 | 0 | 6 | 78 | False |
| L1 | 7/7 | 3/3 | 0/0 | 0 | 6 | 78 | False |
| L2 | 7/7 | 3/3 | 0/0 | 0 | 6 | 78 | False |
| L3 | 7/7 | 3/3 | 0/0 | 0 | 6 | 78 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| quality_assessment_id | 0 | 0 | 0 | 0 |
| report_type | 0 | 0 | 0 | 0 |
| completeness_score | 0 | 0 | 0 | 0 |
| consistency_score | 0 | 0 | 0 | 0 |
| accuracy_score | 0 | 0 | 0 | 0 |
| overall_quality_score | 0 | 0 | 0 | 0 |
| quality_grade | 0 | 0 | 0 | 0 |
| primary_concern | 0 | 0 | 0 | 0 |
| recommended_action | 0 | 0 | 0 | 0 |
| tables_assessed | 0 | 0 | 0 | 0 |
| integrity_checks_performed | 0 | 0 | 0 | 0 |
| business_rules_validated | 0 | 0 | 0 | 0 |
| assessment_timestamp | 0 | 0 | 0 | 0 |

### customer_counts

SQL：`data/022_work/impl-013_int_netsuite2__data_quality_metrics/customer_counts.sql`；SHA-256：`9f17cd06e3491ae2858dbafb74a14fd1b90711be718ef4cb081f470134ff9275`。

替换offset=5501，原表达式所在行约98（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
ELSE 'Date Range: ' || null_dates || ' to ' || null_entities
-- 新
ELSE 'Date Range: ' || (SELECT count(DISTINCT company_name) FROM staging.stg_netsuite2__customers) || ' to ' || (SELECT count(DISTINCT email_address) FROM staging.stg_netsuite2__customers)
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 7/7 | 3/3 | 0/0 | 1 | 7 | 82 | False |
| L1 | 7/7 | 3/3 | 0/0 | 1 | 7 | 82 | False |
| L2 | 7/7 | 3/3 | 0/0 | 1 | 7 | 82 | False |
| L3 | 7/7 | 3/3 | 0/0 | 1 | 7 | 82 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| quality_assessment_id | 0 | 0 | 0 | 0 |
| report_type | 0 | 0 | 0 | 0 |
| completeness_score | 0 | 0 | 0 | 0 |
| consistency_score | 0 | 0 | 0 | 0 |
| accuracy_score | 1 | 1 | 1 | 1 |
| overall_quality_score | 1 | 1 | 1 | 1 |
| quality_grade | 1 | 1 | 1 | 1 |
| primary_concern | 0 | 0 | 0 | 0 |
| recommended_action | 1 | 1 | 1 | 1 |
| tables_assessed | 0 | 0 | 0 | 0 |
| integrity_checks_performed | 0 | 0 | 0 | 0 |
| business_rules_validated | 0 | 0 | 0 | 0 |
| assessment_timestamp | 0 | 0 | 0 | 0 |

### table_label

SQL：`data/022_work/impl-013_int_netsuite2__data_quality_metrics/table_label.sql`；SHA-256：`a3f001adb7556ad0dcd3c58ef00473dc283402450de89f18e2ad9c8b9cb5d121`。

替换offset=5084，原表达式所在行约94（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
table_name::VARCHAR AS quality_grade
-- 新
CASE table_name WHEN 'Transactions' THEN 'staging.stg_netsuite2__transactions' WHEN 'Transaction lines' THEN 'staging.stg_netsuite2__transaction_lines' ELSE 'staging.stg_netsuite2__customers' END::VARCHAR AS quality_grade
```

替换offset=6008，原表达式所在行约124（时间控制前后长度可能不同；精确offset对应受控SQL）。其余字节保持不动。

```sql
-- 旧
md5(table_name || cast(TIMESTAMPTZ '2025-10-14 10:20:49.607+08' AS VARCHAR))
-- 新
md5((CASE table_name WHEN 'Transactions' THEN 'staging.stg_netsuite2__transactions' WHEN 'Transaction lines' THEN 'staging.stg_netsuite2__transaction_lines' ELSE 'staging.stg_netsuite2__customers' END) || cast(TIMESTAMPTZ '2025-10-14 10:20:49.607+08' AS VARCHAR))
```

| L档 | agent/gold行 | 独有A/G | 共同键多出A/G | 共同键不同配对行 | 行规模 | 格子规模 | 整表匹配 |
|---|---|---|---|---|---|---|---|
| L0 | 7/7 | 0/0 | 0/0 | 2 | 2 | 5 | False |
| L1 | 7/7 | 0/0 | 0/0 | 2 | 2 | 5 | False |
| L2 | 7/7 | 0/0 | 0/0 | 2 | 2 | 5 | False |
| L3 | 7/7 | 0/0 | 0/0 | 2 | 2 | 5 | False |

整表首次匹配：L0–L3均不匹配。

| 共同键比较列 | L0不同格 | L1 | L2 | L3 |
|---|---|---|---|---|
| quality_assessment_id | 0 | 0 | 0 | 0 |
| report_type | 0 | 0 | 0 | 0 |
| completeness_score | 0 | 0 | 0 | 0 |
| consistency_score | 0 | 0 | 0 | 0 |
| accuracy_score | 1 | 1 | 1 | 1 |
| overall_quality_score | 1 | 1 | 1 | 1 |
| quality_grade | 1 | 1 | 1 | 1 |
| primary_concern | 0 | 0 | 0 | 0 |
| recommended_action | 2 | 2 | 2 | 2 |
| tables_assessed | 0 | 0 | 0 | 0 |
| integrity_checks_performed | 0 | 0 | 0 | 0 |
| business_rules_validated | 0 | 0 | 0 | 0 |
| assessment_timestamp | 0 | 0 | 0 | 0 |

### 类别门槛与未计入因素

数值门槛达到：table_label；非U，未据此改类。U必须四条件同时满足，本表类别不根据重跑改善程度单独推断。

- accuracy_rules：D；参与因素。agent用100常数占位四条规则合规率，并在报告披露未完整验证。（行减少1，格减少4）
- customer_counts：C；单修未满足本表所选尺度的参与门槛。契约客户Date Range是distinct names/emails，不是缺失数。（行减少0，格减少0）
- table_label：A；主项。契约未固定table_name字符串；agent简写、gold全限定名，使3个Table Statistics键及标签不同。（行减少5，格减少77）

## 规则问题

table_name可读作全限定源表名（C）或未规定展示名（A）。契约没有字面赋值，按A；精确时间戳取gold留存列并共同控制所有运行，不归标签修复收益。
