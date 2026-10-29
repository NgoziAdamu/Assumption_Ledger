from annotate_dacomp_batch016 import *
P={
3:[],
11:[(f'{col}_priority',[(f'coalesce(_{col},{col})',f'coalesce({col},_{col})')]) for col in ['original_estimate','remaining_estimate','time_spent']],
12:[('first_name_trim_policy', [('(first_name IS NULL OR (first_name = TRIM(first_name) AND LENGTH(first_name) <= 100))','LENGTH(TRIM(first_name)) <= 100')]),('last_name_trim_policy',[('(last_name IS NULL OR (last_name = TRIM(last_name) AND LENGTH(last_name) <= 100))','LENGTH(TRIM(last_name)) <= 100')]),('no_dedupe',[('QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC NULLS LAST) = 1','')])],
13:[('percentile_score',[('ntile(5) OVER(ORDER BY total_revenue)',"CASE WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.8) FROM metrics) THEN 5 WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.6) FROM metrics) THEN 4 WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.4) FROM metrics) THEN 3 WHEN total_revenue >= (SELECT quantile_cont(total_revenue,0.2) FROM metrics) THEN 2 ELSE 1 END")]),('clv_month_denominator',[('net_profit/nullif(active_months,0)*greatest(12,1.2*coalesce(customer_lifetime_months,1))','CASE WHEN customer_lifetime_months>0 AND active_months>0 THEN net_profit/customer_lifetime_months*greatest(12,1.2*customer_lifetime_months) ELSE net_profit END')])],
14:[('gold_timestamp_parser',[("try_strptime(cast(src.\"creation_date\" AS VARCHAR), '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP",'try_cast(src."creation_date" AS TIMESTAMP)')])],
15:[('tax_code_null',[('CAST(r.sales_tax_code_id AS VARCHAR) AS "tax_code_id"','CAST(NULL AS VARCHAR) AS "tax_code_id"')])],
17:[('preserve_duplicate',[('WHERE _row_num = 1','WHERE TRUE')])],
18:[('opportunity_source',[('id as opportunity_id','opportunity_id as opportunity_id')]),('product_source',[('id as product_2_id','product_2_id as product_2_id')]),('deleted_filter',[('where id is not null','where id is not null AND NOT COALESCE(is_deleted,false)')])],
20:[('part_type_direct',[('coalesce(try_cast(part_type as varchar), try_cast(subject as varchar))','try_cast(part_type as varchar)')]),('conversation_direct',[("try_cast(split_part(id, '_', 1) as bigint)",'conversation_id')]),('created_contract',[('coalesce(try_cast(raw_part_time as timestamp), try_cast(updated_at as timestamp))','try_cast(created_at as timestamp)')])]
}
# A join predicate is one distinct error point; summary/event joins are tested separately.
s=Path(package(19)['agent_final_SQL'][0]['path']).read_text()
P[19]=[(name,[(line,line.replace(' IS NOT DISTINCT FROM ',' = '))]) for name,needle in [('summary_null_join','LEFT JOIN s ON'),('event_null_join','LEFT JOIN e ON')] for line in s.splitlines() if line.startswith(needle)]
if __name__=='__main__':
 for n in map(int,sys.argv[1:]):rerun(n,P[n],clock='2025-10-14 12:00:00+08' if n==13 else None)
