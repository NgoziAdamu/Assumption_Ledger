from pathlib import Path
import json,sys,re
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'scripts'),str(R/'data/005_tools')]
import duckdb
from annotate_dacomp_batch016 import compare_sql,udf_forms
C=json.loads((R/'records/037_checks/evidence_catalog.json').read_text());out=[]
def canon(s):
 if s is None:return None
 v=json.loads(s)
 return json.dumps({k:sorted(x) if isinstance(x,list) else x for k,x in v.items()},sort_keys=True,separators=(',',':'))
for table in (sys.argv[1:] or ['customer360__mapping','customer360__updates','customer360__status']):
 id='impl-003_'+table;o=C[id];b=o['basis'];orig=(R/o['runs'][0]['sql_path']).read_text()
 with duckdb.connect(':memory:') as c:
  c.execute("SET threads=2; SET memory_limit='1500MB'");c.create_function('canon',canon,['VARCHAR'],'VARCHAR');c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
  c.execute(f"ATTACH '{o['source']}' AS src (READ_ONLY)")
  for ref in sorted(set(re.findall(r'\b(?:FROM|JOIN)\s+((?:raw|staging|intermediate|marts)\.\w+)',orig,re.I))):c.execute(f'CREATE SCHEMA IF NOT EXISTS {ref.split(".")[0]}');c.execute(f'CREATE TABLE {ref} AS SELECT * FROM src.{ref}')

  if table=='customer360__status':
   c.execute(f"ATTACH '{b['prediction_database']}' AS retained (READ_ONLY)");c.execute(f"CREATE TABLE agent_base AS SELECT * FROM retained.{b['actual_schema']}.{table}")
  else:c.execute('CREATE TABLE agent_base AS '+orig)
  gold='src.'+b['actual_schema']+'.'+table
  base=compare_sql(c,'agent_base',gold,b)
  cols=['source_ids'] if table.endswith('mapping') else ['source_systems'] if table.endswith('status') else ['update_types','updated_by_systems']
  for col in cols:
   expr=f'canon({col})' if col=='source_ids' else f"list_sort(string_split({col}, ', '))::VARCHAR"
   a=f'SELECT * REPLACE({expr} AS {col}) FROM agent_base';g=f'SELECT * REPLACE({expr} AS {col}) FROM {gold}'
   c.execute('CREATE OR REPLACE TABLE a_sorted AS '+a);c.execute('CREATE OR REPLACE TABLE g_sorted AS '+g)
   out.append(dict(object=id,label='string_order' if table.endswith('status') else col+'_order',kind='只改呈现的双侧诊断；未改变SQL计算链',baseline=base,comparison=compare_sql(c,'a_sorted','g_sorted',b),agent_sql=a,gold_sql=g,source=o['source'],original_database_read_only=True))
f=R/'records/037_checks/order_diagnostics.json'
if f.exists():out=[x for x in json.loads(f.read_text()) if x['object'] not in {y['object'] for y in out}]+out
(R/'records/037_checks/order_diagnostics.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
for x in out: print(x['object'],x['label'],[(l['row_scale'],l['cell_scale']) for l in x['comparison']['levels']])
