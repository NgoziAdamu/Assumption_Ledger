"""Private in-memory diagnosis; original DuckDB files are READ_ONLY."""
import sys,json,re
from pathlib import Path
sys.path[:0]=['scripts','data/005_tools']
import duckdb
from annotate_dacomp_batch016 import compare_sql,udf_forms
r=Path('records');d=json.loads((r/'021_reruns_impl-030_stg_zuora__invoice.json').read_text());b=d['basis']
sql=Path('/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__invoice.sql').read_text()
for ce in d['clock_control']:sql=re.sub(ce['pattern'],ce['replacement'],sql,flags=re.I)
out={'purpose':'诊断所有单改 L0 行规模均被其他列遮蔽，组合能否减少；不是新的单改排序','source':'records/021_reruns_impl-030_stg_zuora__invoice.json','runs':[]}
with duckdb.connect(':memory:') as c:
 c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
 for alias,p in d['attached']:c.execute("ATTACH '"+p+f"' AS {alias} (READ_ONLY)")
 c.execute('CREATE SCHEMA raw');c.execute('CREATE TABLE raw.zuora_invoice_data AS SELECT * FROM src.raw.zuora_invoice_data');c.execute('CREATE SCHEMA staging')
 for label,runs in [('baseline',[]),('all_points',d['runs'][1:])]:
  s=sql;edits=[]
  for run in runs:
   for edit in run['edits']:
    assert s.count(edit['old'])==1;s=s.replace(edit['old'],edit['new'],1);edits.append(edit)
  c.execute('CREATE OR REPLACE TABLE staging.stg_zuora__invoice AS '+s.strip().rstrip(';'))
  out['runs'].append({'label':label,'edits':edits,'comparison':compare_sql(c,'staging.stg_zuora__invoice','gold.staging.stg_zuora__invoice',b)})
(r/'039_checks/calibration_combo.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
for x in out['runs']:print(x['label'],[(v['level'],v['row_scale'],v['cell_scale']) for v in x['comparison']['levels']])
