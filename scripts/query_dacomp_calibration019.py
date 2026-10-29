from annotate_dacomp_batch019 import *
out=[]
for n,queries in [(8,["SELECT count(*) n, count(*) FILTER(WHERE p.id IS NULL) missing FROM raw.project_task_data pt LEFT JOIN raw.project_data p ON pt.project_id=p.id", "SELECT count(*) n,count(*) FILTER(WHERE p.project_id IS NULL) missing FROM staging.stg_asana__project_task pt LEFT JOIN staging.stg_asana__project p ON pt.project_id::VARCHAR=p.project_id"]),(21,["SELECT count(*) AS repeated_groups, sum(n-1) extra_events FROM (SELECT person_id,source_relation,cast(occurred_at AS DATE),count(*) n FROM staging.stg_klaviyo__event GROUP BY ALL HAVING count(*)>1)"])]:
 case=json.loads((REC/'013_cases.json').read_text())[n-1]
 with duckdb.connect(case['agent_database'],read_only=True) as c:
  for q in queries:
   try:result=c.execute(q);out.append(dict(task=n,kind='核实',database=case['agent_database'],sql=q,columns=[x[0] for x in result.description],result=result.fetchall()))
   except Exception as e:out.append(dict(task=n,error=str(e),sql=q))
 if n==8:
  p=package(n);db=WORK/'impl-008_int_asana__task_projects/work.duckdb'
  with duckdb.connect(str(db),read_only=True) as c:
   c.execute("ATTACH '"+p['differences']['gold_database']+"' AS gold (READ_ONLY)")
   q="SELECT count(*) FROM intermediate.int_asana__task_projects a JOIN gold.intermediate.int_asana__task_projects g USING(task_id) WHERE list_sort(string_split(a.projects_sections, ', ')) IS DISTINCT FROM list_sort(string_split(g.projects_sections, ', '))"
   out.append(dict(task=n,kind='诊断',sql=q,result=c.execute(q).fetchall()))
save(REC/'019_calibration_queries.json',out)
