"""Gold-aware diagnostics separated from <=5 agent-visible verification queries."""
from annotate_dacomp_batch023 import *
inv=json.loads((REC/'023_package_inventory.json').read_text());out=[]
def pkg(t):return json.loads((ROOT/next(r['full_json'] for r in inv if r['table']==t)).read_text())
def run(t,label,sql,side='gold'):
 p=pkg(t);b=p['differences'];db=b['gold_database'] if side=='gold' else b['prediction_database'];r=dict(table=t,label=label,kind='诊断',database=db,sql=sql)
 with duckdb.connect(db,read_only=True) as c:
  x=c.execute(sql);r.update(columns=[a[0] for a in x.description],rows=x.fetchall())
 out.append(r);save(REC/'023_diagnostics.json',out)
t='quickbooks__general_ledger';p=pkg(t);b=p['differences'];work=ROOT/'data/023_diagnostics';work.mkdir(exist_ok=True)
with duckdb.connect(str(work/'diagnostics.duckdb')) as c:
 c.execute("SET memory_limit='1GB'; SET threads=2");c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
 for a,key in [('p','prediction_database'),('g','gold_database')]:c.execute(f"ATTACH '{b[key]}' AS {a} (READ_ONLY)")
 b2={**b,'comparison_columns':[x for x in b['comparison_columns'] if x not in ['running_balance','running_converted_balance']]}
 result=compare_sql(c,'p.marts.'+t,'g.marts.'+t,b2);out.append(dict(table=t,label='排除两列窗口累计后整表含键比较',kind='诊断',comparison=result))
 sql="SELECT count(*) tie_groups,sum(n) tied_rows FROM (SELECT count(*) n FROM g.marts.quickbooks__general_ledger GROUP BY account_id,class_id,source_relation,transaction_date HAVING count(*)>1)"
 out.append(dict(table=t,label='窗口排序键并列',kind='诊断',sql=sql,rows=c.execute(sql).fetchall()))
 save(REC/'023_diagnostics.json',out)
run('stg_apple_store__app_session_daily','格式解析差异',"SELECT date,count(*) FROM raw.app_session_standard_daily WHERE try_cast(date AS DATE) IS NOT NULL AND coalesce(try_strptime(date,'%Y-%m-%d'),try_strptime(date,'%d-%m-%Y'),try_strptime(date,'%b %d, %Y')) IS NULL GROUP BY 1")
run('stg_apple_store__app_session_daily','版本regex效果',r"SELECT count(*) FILTER(WHERE regexp_matches(app_version,'^[0-9]+\.[0-9]+\.[0-9]+$')) normal_semver,count(*) FILTER(WHERE regexp_matches(app_version,'^[0-9]+\\.[0-9]+\\.[0-9]+$')) gold_semver FROM raw.app_session_standard_daily")
run('stg_intercom__conversation_contact_history','gold类型与契约',"DESCRIBE staging.stg_intercom__conversation_contact_history")
run('stg_klaviyo__person','去除ID筛选后的 residual 姓名',"SELECT count(*) FILTER(WHERE first_name IS NULL OR last_name IS NULL) one_name_null FROM raw.person")
# Diagnostic tie-equivalence for Klaviyo: omit tied window-derived columns; compare the rest exactly.
t='int_klaviyo__events';p=pkg(t);b=p['differences']
with duckdb.connect(str(work/'klaviyo.duckdb')) as c:
 c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
 for a,key in [('p','prediction_database'),('g','gold_database')]:c.execute(f"ATTACH '{b[key]}' AS {a} (READ_ONLY)")
 cols=[x for x in b['comparison_columns'] if x not in ['inter_event_minutes','session_seq','prev_event_at']]
 out.append(dict(table=t,label='除并列窗口列外一致性',kind='诊断',comparison=compare_sql(c,'p.intermediate.'+t,'g.intermediate.'+t,{**b,'comparison_columns':cols})))
 save(REC/'023_diagnostics.json',out)
print('diagnostics',len(out))
