from annotate_dacomp_batch021 import *
from review_dacomp_batch021 import pkg,rows
out=[]
custom={
0:["SELECT count(*) links, count(*) FILTER(WHERE t.task_id IS NULL) dangling_links FROM staging.stg_asana__project_task pt LEFT JOIN staging.stg_asana__task t ON pt.task_id::VARCHAR=t.task_id"],
2:["SELECT typeof(min(created_at)) created_type,typeof(min(completed_at)) completed_type,min(created_at)::varchar first_created,max(created_at)::varchar last_created FROM staging.stg_asana__task"],
6:["SELECT count(*) n,count(*) FILTER(WHERE project_id IS NOT NULL AND try_cast(project_id AS BIGINT) IS NULL) invalid_numeric_project FROM raw.section_data"],
7:["SELECT count(*) n,"+','.join(f"count(*) FILTER(WHERE {x} IS NOT NULL AND TRY_STRPTIME({x}, '%Y-%m-%d %H:%M:%S.%f %z') IS NULL AND TRY_CAST({x} AS TIMESTAMP) IS NOT NULL) {x}_parseable_other_format" for x in ['due_on','start_on'])+" FROM raw.task_data"],
16:["SELECT count(*) n,count(*) FILTER(WHERE transaction_date IS NULL) raw_date_null,count(*) FILTER(WHERE product_id IS NULL) product_null,count(*) FILTER(WHERE base_plan_id IS NULL) base_null,count(*) FILTER(WHERE sku_id IS NULL) sku_null,count(*) FILTER(WHERE try_cast(substr(transaction_time,1,10) AS DATE) IS NOT NULL) alternative_date_parseable FROM raw.earnings"],
17:["SELECT count(*) n,count(*) FILTER(WHERE date IS NULL) null_date,count(*) FILTER(WHERE package_name IS NULL) null_package FROM raw.stats_ratings_overview"],
24:["SELECT count(*) n,count(distinct engagement_id) ids FROM raw.engagement_email_data"],
25:["SELECT count(*) n,count(*) FILTER(WHERE try_cast(created_at AS TIMESTAMP) IS NOT NULL) created_parseable,count(*) FILTER(WHERE created_at ~ '^\\d{4}-\\d{2}-\\d{2}') created_regex_full_matches,count(*) FILTER(WHERE try_cast(updated_at AS TIMESTAMP) IS NOT NULL) updated_parseable FROM raw.owner_data"],
29:["SELECT count(*) n,count(*) FILTER(WHERE resolved_at IS NULL) unresolved FROM staging.stg_jira__issue"],
30:["WITH a AS(SELECT issue_id,count(*) n FROM staging.stg_jira__issue_field_history WHERE field_value IS NOT NULL GROUP BY issue_id) SELECT count(*) issues_with_history,count(*) FILTER(WHERE n>2) multi_intervals,sum(greatest(n-1,0)) intervals,sum(greatest(n-1,0)*greatest(n-1,0)) issue_only_join_rows FROM a"],
31:["SELECT count(*) n,count(*) FILTER(WHERE revised_parent_issue_id IS NOT NULL AND revised_parent_issue_id::VARCHAR IS DISTINCT FROM parent_issue_id::VARCHAR) revised_diff FROM intermediate.int_jira__issue_type_parents"],
32:["SELECT count(*) n,count(*) FILTER(WHERE field_value IS NULL) null_updates,count(distinct field_id) fields FROM intermediate.int_jira__issue_field_history"],
}
for i,r in enumerate(rows[:40]):
 if 18<=i<=28 and i not in [24,25]:continue
 d=pkg(i);case=json.loads((REC/'013_cases.json').read_text())[int(r['task'][-3:])-1];database=case['agent_database'];sqls=custom.get(i)
 if not sqls:
  refs=d['trace_excerpts']['actual_read_sources_from_008_B7']
  sqls=[' UNION ALL '.join("SELECT '"+ref+"' source,count(*) n FROM "+ref for ref in refs)]
 with duckdb.connect(database,read_only=True) as c:
  for sql in sqls:
   rec=dict(index=i,task=r['task'],table=r['table'],kind='核实',database=database,sql=sql)
   try:
    cur=c.execute(sql);rec.update(columns=[x[0] for x in cur.description],result=cur.fetchall())
   except Exception as e:rec['error']=str(e)
   out.append(rec)
(REC/'021_queries.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str)+'\n')
for r in out:print(r['index'],r.get('result',r.get('error')))
