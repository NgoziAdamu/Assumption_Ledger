from annotate_dacomp_batch019 import *
from copy import deepcopy
t='customer360__conversion_funnel_analysis';d=json.loads((REC/('019_reruns_impl-003_'+t+'.json')).read_text());b=deepcopy(d['basis']);work=WORK/('impl-003_'+t)
with duckdb.connect(str(work/'keydiagnostic.duckdb')) as c:
 c.execute("SET threads=2;SET memory_limit='1500MB'");c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}));c.execute("ATTACH '"+str(work/'work.duckdb')+"' AS src (READ_ONLY)");c.execute("ATTACH '"+b['gold_database']+"' AS gold (READ_ONLY)")
 for ref in d['private_copy_tables']:
  c.execute('CREATE SCHEMA IF NOT EXISTS '+ref.split('.')[0]);c.execute('CREATE OR REPLACE TABLE '+ref+' AS SELECT * FROM src.'+ref)
 c.execute('CREATE TABLE a AS '+(work/'revenue_velocity_monthly.sql').read_text());rel=b['actual_schema']+'.'+t
 b['key_columns'].remove('journey_efficiency_index');b['comparison_columns']=list(dict.fromkeys(b['comparison_columns']+['journey_efficiency_index']))
 out={'diagnostic_only':'journey_efficiency_index 从键移至比较列，保留整表值，仅诊断键不匹配原因','comparison':compare_sql(c,'a','gold.'+rel,b)};save(REC/'019_funnel_key_diagnostic.json',out)
