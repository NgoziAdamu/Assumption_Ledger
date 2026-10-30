from annotate_dacomp_batch022 import *
from review_dacomp_batch022 import pkg,inventory
out=[]
for i in range(38):
 p=pkg(i);r=inventory()[i];case=json.loads((REC/'013_cases.json').read_text())[int(r['task'][-3:])-1]
 refs=sorted(set(re.findall(r'\b(?:FROM|JOIN)\s+((?:raw|staging|intermediate|marts|mart|utils)\.[a-zA-Z_0-9]+)',p['agent_final_SQL'][0]['text'],re.I)))
 qs=[]
 if refs:qs.append(('上游可见行数', ' UNION ALL '.join(f"SELECT '{ref}' source_table,count(*) rows FROM {ref}" for ref in refs)))
 if i in [0,2]:qs.append(('merge重复组',"SELECT count(*) leads,sum(n) merge_rows,count(*) FILTER(WHERE n>1) multi_value_leads FROM (SELECT lead_id,count(DISTINCT merged_lead_ids) n FROM staging.stg_marketo__activity_merge_leads GROUP BY lead_id)"))
 if i==4:qs.append(('send_id源列核实',"SELECT count(*) n,count(DISTINCT id) unique_id,count(*) FILTER(WHERE id IS NULL) null_id FROM raw.marketo_activity_send_email"))
 if i==5:qs.append(('空白名称',"SELECT count(*) FILTER(WHERE name IS NOT NULL AND trim(name)='') blanks FROM raw.marketo_campaign"))
 if i==11:qs.append(('维表外键匹配',"SELECT count(*) n,count(*) FILTER(WHERE s.subsidiary_id IS NULL) unmatched FROM intermediate.int_netsuite2__tran_with_converted_amounts t LEFT JOIN staging.stg_netsuite2__subsidiaries s ON s.subsidiary_id=t.subsidiary_id WHERE t.is_income_statement"))
 if i==13:qs.append(('期间解析',"SELECT count(*) n,count(try_cast(starting_at AS TIMESTAMP)) direct_parsed,count(try_strptime(substr(starting_at,1,19),'%Y-%m-%d %H:%M:%S')) seconds_parsed FROM staging.stg_netsuite__accounting_periods"))
 if i==19:qs.append(('两种type标识',"SELECT internalid,longname,row_number() OVER(ORDER BY longname) ordered_id FROM raw.netsuite2_account_type_data ORDER BY internalid"))
 if i==20:qs.append(('可见字段',"SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name='netsuite2_account_data' ORDER BY ordinal_position"))
 if i in [21,22,24]:
  ref=refs[0];qs.append(('候选ID列',f'SELECT count(*) n,count(id) nonnull_ids,count(DISTINCT id) distinct_ids FROM {ref}'))
 if i==23:qs.append(('邮箱检验',"SELECT count(*) n,count(*) FILTER(WHERE strpos(email,'@')>1 AND strpos(email,'.')>strpos(email,'@') AND NOT regexp_full_match(trim(email),'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}$')) loose_only FROM raw.netsuite2_customer_data"))
 if i>=26:
  # Raw duplicate counts use source mapped keys, no gold involved.
  s=p['agent_final_SQL'][0]['text'];keys=p['differences']['key_columns'];mapping={m[2]:m[1] for m in re.finditer(r'try_cast\(src\."([^\"]+)" AS \w+\) AS (\w+)',s)}
  if all(k in mapping for k in keys):
   cols=','.join('"'+mapping[k]+'"' for k in keys);qs.append(('原始重复键',f'SELECT count(*) groups,count(*) FILTER(WHERE n>1) duplicate_groups,sum(n-1) excess FROM (SELECT {cols},count(*) n FROM {refs[0]} GROUP BY {cols})'))
  times=re.findall(r"try_strptime\(cast\(src\.\"([^\"]+)\" AS VARCHAR\), '%Y-%m-%d %H:%M:%S.%f %z'\)::TIMESTAMP AS (\w+)",s)
  if times:qs.append(('两种时间解析', ' UNION ALL '.join(f'''SELECT '{a}' field,count(*) n,count(try_cast("{a}" AS TIMESTAMP)) direct_parsed,count(try_strptime(cast("{a}" AS VARCHAR),'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM {refs[0]}''' for a,b in times)))
 if i==25:qs.append(('cohort时间解析',"SELECT count(*) n,count(try_cast(recorded_date AS TIMESTAMP)) direct_parsed,count(try_strptime(recorded_date,'%Y-%m-%d %H:%M:%S.%f %z')) format_parsed FROM staging.stg_qualtrics__survey_response WHERE recorded_date IS NOT NULL"))
 with duckdb.connect(case['agent_database'],read_only=True) as c:
  if r['task']=='impl-013':c.execute("ATTACH '"+case['initial_database']+"' AS source (READ_ONLY)")
  for label,sql in qs:
   row=dict(index=i,kind='核实查询',label=label,sql=sql,database=case['agent_database'])
   try:
    cur=c.execute(sql);row.update(columns=[x[0] for x in cur.description],result=cur.fetchall())
   except Exception as e:row['error']=str(e)
   out.append(row)
 save(REC/'022_queries.json',out)
print('queries',len(out),flush=True)
