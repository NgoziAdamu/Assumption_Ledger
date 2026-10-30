"""Same comparator, weighted residual pairing and no unused key normalization."""
import inspect
import annotate_dacomp_batch016 as base
src=inspect.getsource(base.compare_sql)
src=src.replace("for i in range(len(cols))))", "for i in range(len(cols)) if cols[i] not in keys))",1)
old="""for side,weight in [('pa','a'),('ga','g')]:
   c.execute(f'CREATE OR REPLACE TEMP TABLE {side} AS SELECT key0,{order},row_number() OVER(PARTITION BY key0 ORDER BY {order},ordinal) rn FROM residual,UNNEST(range(cast({weight} AS BIGINT))) AS u(ordinal) WHERE {weight}>0')
  q='SELECT '+','.join(f\"coalesce(sum(CASE WHEN pa.c{i}<>ga.c{i} THEN 1 ELSE 0 END),0)\" for i in range(len(cols)))+' FROM pa JOIN ga USING(key0,rn)'"""
new="""for side,weight in [('pa','a'),('ga','g')]:
   c.execute(f'CREATE OR REPLACE TEMP TABLE {side} AS SELECT key0,{order},sum({weight}) OVER(PARTITION BY key0 ORDER BY {order} ROWS UNBOUNDED PRECEDING)-{weight} lo,sum({weight}) OVER(PARTITION BY key0 ORDER BY {order} ROWS UNBOUNDED PRECEDING) hi FROM residual WHERE {weight}>0')
  q='SELECT '+','.join(f\"coalesce(sum(CASE WHEN pa.c{i}<>ga.c{i} THEN least(pa.hi,ga.hi)-greatest(pa.lo,ga.lo) ELSE 0 END),0)\" for i in range(len(cols)))+' FROM pa JOIN ga ON pa.key0=ga.key0 AND pa.lo<ga.hi AND ga.lo<pa.hi'"""
assert old in src
src=src.replace(old,new)
ns=dict(vars(base));exec(src,ns);compare_sql=ns['compare_sql']
if __name__=='__main__':
 import duckdb,json,random
 from pathlib import Path
 cases=[]
 with duckdb.connect(':memory:') as c:
  c.create_function('tolerance_forms',base.udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
  b={'key_columns':['id'],'comparison_columns':['id','x','y']}
  random.seed(21)
  for n in range(12):
   c.execute('create or replace table ap(id varchar,x varchar,y varchar)');c.execute('create or replace table ag as select * from ap')
   for table in ['ap','ag']:
    data=[(random.choice(['1','2',None]),random.choice(['a','1.000','1',None]),random.choice(['2.001','2.004','z',None])) for _ in range(50+n)]
    c.executemany('insert into '+table+' values (?,?,?)',data)
   slow=base.compare_sql(c,'ap','ag',b);fast=compare_sql(c,'ap','ag',b);assert fast==slow,(n,fast,slow);cases.append({'case':n,'all_levels_exact_equal':True})
 Path('records/021_comparator_validation.json').write_text(json.dumps(cases,indent=2)+'\n');print('12 duplicated-key/null/multiplicity/tolerance comparisons equal')
