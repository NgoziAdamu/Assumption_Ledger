"""Read selected verbatim contract/SQL sections for manual annotation."""
import json,sys,re
from pathlib import Path
import sqlglot
from sqlglot import exp
r=next(r for r in json.loads(Path('records/019_package_inventory.json').read_text()) if r['table']==sys.argv[1]);d=json.loads(Path(r['full_json']).read_text())
if len(sys.argv)>2 and sys.argv[2]=='contract':
 for b in d['contract_specification']['blocks']:print(b['original_text'])
elif len(sys.argv)>2 and sys.argv[2]=='agent':print(d['agent_final_SQL'][0]['text'])
else:
 s=d['gold_SQL_仅供定位差异'][0]['text'];tree=sqlglot.parse_one(s,read='duckdb');names=sys.argv[2:]
 for select in tree.find_all(exp.Select):
  for e in select.expressions:
   if names and e.alias_or_name not in names:continue
   if isinstance(e,exp.Star):continue
   print(e.sql(dialect='duckdb'))
