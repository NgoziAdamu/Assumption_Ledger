"""Build reviewable single-expression diagnostic patches, preserving all other SQL bytes."""
import json,re,sys
from pathlib import Path
import sqlglot
from sqlglot import exp
ROOT=Path(__file__).resolve().parents[1];REC=ROOT/'records'
rows=json.loads((REC/'020_package_inventory.json').read_text())
def pkg(i):return json.loads((ROOT/rows[i]['full_json']).read_text())
def goldexpr(d,col):
 tree=sqlglot.parse_one(d['gold_SQL_仅供定位差异'][0]['text'],read='duckdb');ctes={x.alias:x.this for x in tree.find_all(exp.CTE)}
 def resolve(sel,col,depth=0):
  assert depth<12
  src=sel.args.get('from_');src=src.this if src else None
  upstream=ctes.get(src.name) if isinstance(src,exp.Table) else None
  vals=[x for x in sel.expressions if x.alias_or_name.lower()==col.lower()]
  if not vals:
   if upstream is not None:return resolve(upstream,col,depth+1)
   return exp.column(col)
  v=vals[0].this.copy() if isinstance(vals[0],exp.Alias) else vals[0].copy()
  if upstream is not None:
   v=v.transform(lambda x:resolve(upstream,x.name,depth+1) if isinstance(x,exp.Column) else x)
  return v
 x=resolve(tree,col)
 for node in x.walk():node.comments=None
 return x.sql(dialect='duckdb')
def oldexpr(d,col):
 s=d['agent_final_SQL'][0]['text'];lines=[l.strip().rstrip(',') for l in s.splitlines() if re.search(r'\sAS\s+"?'+re.escape(col)+r'"?\s*,?$',l,re.I)]
 assert len(lines)==1,(col,lines)
 return lines[0]
def main():
 out=[]
 for i in list(range(13,32))+list(range(35,41)):
  d=pkg(i);b=d['differences'];cols=[x['column'] for x in b['column_details'] if x['l0_counts_verbatim']['mismatch_rows_or_minimum_pairs']]
  if i in [20,24,25,30]:cols+= {'20':['campaign_id'],'24':['ad_group_id'],'25':['campaign_id'],'30':['date_day']}[str(i)]
  patches=[]
  for col in cols:
   old=oldexpr(d,col);new=goldexpr(d,col)+' AS '+col
   patches.append({'label':col,'edits':[(old,new)]})
  out.append({'index':i,'task':rows[i]['task'],'table':rows[i]['table'],'patches':patches})
 (REC/'020_patch_plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 for r in out:
  print('\n',r['index'],r['table'])
  for p in r['patches']:print(p['label'],p['edits'][0][1])
if __name__=='__main__':main()
