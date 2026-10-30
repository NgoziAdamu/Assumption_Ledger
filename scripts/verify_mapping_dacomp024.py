from annotate_dacomp_batch024 import *
inv=json.loads((REC/'024_package_inventory.json').read_text());cases=json.loads((REC/'013_cases.json').read_text());out=[]
for r in inv:
 if r['task']!='impl-030' or r['layer']!='staging':continue
 d=json.loads((ROOT/r['full_json']).read_text());a=d['agent_final_SQL'][0]['text'];ids=[x for x in re.findall(r'try_cast\("id" AS VARCHAR\) AS (\w+)',a) if x!=r['table'].replace('stg_zuora__','')+'_id'];qs=[]
 for col in ids:qs.append(f"SELECT '{col}' col,count(*) n,count({col}) nonnull,count(*) FILTER(WHERE regexp_full_match(cast({col} AS VARCHAR),'[A-Fa-f0-9]{{32}}')) hex32,count(*) FILTER(WHERE try_cast({col} AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows")
 if not qs:continue
 sql=a.split('\nSELECT\n')[0]+'\n'+' UNION ALL '.join(qs);db=cases[29]['agent_database']
 with duckdb.connect(db,read_only=True) as c:v=c.execute(sql);out.append(dict(task=r['task'],table=r['table'],kind='核实',label='外键字段格式诊断（原可见数据）',sql=sql,columns=[x[0] for x in v.description],rows=v.fetchall(),database=db))
save(REC/'024_mapping_queries.json',out)
for x in out:print(x['table'],x['rows'])
