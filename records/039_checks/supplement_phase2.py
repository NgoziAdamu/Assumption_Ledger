"""Single-output recovery diagnoses, reusing 021's contract implementation on CS upstream.
No raw/gold output values are copied into SQL; expected outputs are recomputed from CS inputs.
"""
import sys,json,re,hashlib
from pathlib import Path
sys.path[:0]=['scripts','data/005_tools']
import duckdb
from annotate_dacomp_batch016 import compare_sql,udf_forms
R=Path('records');C=R/'039_checks';cat=json.loads((C/'evidence_catalog.json').read_text())
plans={8:['active_versions_count','supported_os_versions','version_with_most_crashes','os_with_most_crashes','worst_version_crashes','worst_version_anrs','worst_os_crashes','worst_os_anrs','stability_trend'],9:['crashes','anrs','average_rating','rolling_total_average_rating','total_device_installs','total_device_uninstalls','net_device_installs'],12:['average_rating','rolling_total_average_rating','total_device_installs','total_device_uninstalls','net_device_installs'],14:['crashes','anrs','average_rating','rolling_total_average_rating','total_device_installs','total_device_uninstalls','net_device_installs']}
for i,cols in plans.items():
 o=cat[i];key=o['object'];d=json.loads((R/('021_reruns_'+key+'.json')).read_text());b=d['basis'];orig=Path(o['agent_sql']).read_text().strip().rstrip(';');goldrun=next(x for x in d['runs'] if x['label']=='whole_implementation_diagnostic');recovered=goldrun['edits'][0]['new'].strip().rstrip(';');base=orig
 for ce in d['clock_control']:
  base=re.sub(ce['pattern'],ce['replacement'],base,flags=re.I);recovered=re.sub(ce['pattern'],ce['replacement'],recovered,flags=re.I)
 out={'object':key,'kind':'单输出恢复诊断','source_record':str(R/('021_reruns_'+key+'.json')),'source':d['source'],'original_databases_read_only':True,'private_database':':memory:','baseline_sql':base,'recovery_sql':recovered,'recovery_basis':'021 whole_implementation_diagnostic 按契约从gold上游重算；不查询gold目标输出填值。每次仅替换一个最终输出，其余输出及行范围保持agent原样。','clock_control':d['clock_control'],'runs':[]}
 with duckdb.connect(':memory:') as c:
  c.execute("SET threads=1; SET memory_limit='1500MB'");c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
  c.execute("ATTACH '"+d['source']+"' AS src (READ_ONLY)");ga='src'
  if b['gold_database']!=d['source']:c.execute("ATTACH '"+b['gold_database']+"' AS gold (READ_ONLY)");ga='gold'
  refs=set(re.findall(r'\b(?:FROM|JOIN)\s+((?:staging|intermediate|marts|mart|raw)\.[\w]+)',base+' '+recovered,re.I))
  for ref in refs:
   c.execute('CREATE SCHEMA IF NOT EXISTS '+ref.split('.')[0]);c.execute('CREATE TABLE '+ref+' AS SELECT * FROM src.'+ref)
  c.execute('CREATE TABLE original_result AS '+base);c.execute('CREATE TABLE recovered_result AS '+recovered)
  keys=b['key_columns']+(['android_os_version'] if i==14 else [])
  dup=c.execute('SELECT count(*) FROM (SELECT '+','.join(keys)+',count(*) n FROM recovered_result GROUP BY ALL HAVING count(*)>1)').fetchone()[0]
  assert dup==0,(key,dup)
  out['recovery_unique_keys']=keys;out['recovery_duplicate_groups']=dup
  # Recovery joined only to original keys. No fabricated or extra rows.
  condition=' AND '.join(f'original_result."{k}" IS NOT DISTINCT FROM recovered_result."{k}"' for k in keys)
  for label in ['baseline']+cols:
   sql='SELECT * FROM original_result' if label=='baseline' else f'SELECT original_result.* REPLACE((SELECT recovered_result."{label}" FROM recovered_result WHERE {condition}) AS "{label}") FROM original_result'
   c.execute('CREATE OR REPLACE TABLE candidate AS '+sql)
   run={'label':label,'sql':sql,'sql_sha256':hashlib.sha256(sql.encode()).hexdigest(),'comparison':compare_sql(c,'candidate',ga+'.'+b['actual_schema']+'.'+b['table'],b)};out['runs'].append(run)
   (C/('supplement_'+key+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
   z=run['comparison']['levels'][0];print(key,label,z['row_scale'],z['cell_scale'],flush=True)
