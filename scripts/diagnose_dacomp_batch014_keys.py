from annotate_dacomp_batch014 import *
for n,keys in [(4,['contact_id']),(7,['date_day','app_id','subscription_id','country']),(9,['date_day','package_name']),(10,['form_id'])]:
 b=package(n)['differences']
 with duckdb.connect(b['prediction_database'],read_only=True) as a,duckdb.connect(b['gold_database'],read_only=True) as g:
  x=compare(a,g,b['actual_schema'],b['table'],b['comparison_columns'],keys)
 save(REC/f'014_alternate_keys_impl-{n:03}.json',{'diagnostic_only':True,'keys':keys,'comparison':x})
 print(n,[(v['level'],v['whole_agent_unmatched'],v['whole_gold_unmatched'],{k:c for k,c in v['column_mismatches'].items() if c}) for v in x['levels']])
