"""Alternative-evaluation diagnostics for explicitly permitted stochastic outputs."""
from annotate_dacomp_batch019 import *
from copy import deepcopy
out=[]
for t,cols in [('int_customer360__customer_lifecycle_metrics',['estimated_transaction_count']),('customer360__customer_activity_metrics',['estimated_monthly_activities','predicted_next_month_activity','seasonally_adjusted_activity'])]:
 p=REC/('019_reruns_impl-003_'+t+'.json');d=json.loads(p.read_text());b=d['basis'];work=WORK/('impl-003_'+t);dest=work/'diagnostic.duckdb'
 with duckdb.connect(str(dest)) as c:
  c.execute("SET threads=2;SET memory_limit='1500MB'");c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
  c.execute("ATTACH '"+str(work/'work.duckdb')+"' AS src (READ_ONLY)");c.execute("ATTACH '"+b['gold_database']+"' AS gold (READ_ONLY)")
  for ref in d['private_copy_tables']:
   c.execute('CREATE SCHEMA IF NOT EXISTS '+ref.split('.')[0]);c.execute('CREATE OR REPLACE TABLE '+ref+' AS SELECT * FROM src.'+ref)
  sql=(work/'baseline.sql').read_text();c.execute('SELECT setseed(0.019)');c.execute('CREATE OR REPLACE TABLE baseline AS '+sql)
  rep=','.join('0::DOUBLE AS "'+col+'"' for col in cols);rel=b['actual_schema']+'.'+t
  c.execute('CREATE OR REPLACE TABLE neutral_agent AS SELECT * REPLACE('+rep+') FROM baseline');c.execute('CREATE OR REPLACE TABLE neutral_gold AS SELECT * REPLACE('+rep+') FROM gold.'+rel)
  out.append(dict(table=t,kind='诊断：共同屏蔽契约允许随机模拟的字段；不替代官方判错',columns=cols,baseline=compare_sql(c,'baseline','gold.'+rel,b),comparison=compare_sql(c,'neutral_agent','neutral_gold',b),sql=rep))
save(REC/'019_stochastic_diagnostics.json',out)
