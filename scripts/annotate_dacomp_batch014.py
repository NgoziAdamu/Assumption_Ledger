"""Task 014 evidence harness. Original inputs read only; reruns under data/014_work."""
import json, hashlib, re, shutil, sys
from pathlib import Path
from collections import Counter,defaultdict
import duckdb
from dacomp_tolerance import normalized,normal_forms
ROOT=Path(__file__).resolve().parents[1]
REC=ROOT/'records'; WORK=ROOT/'data/014_work'; WORK.mkdir(exist_ok=True)
def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+'\n')
def fp(p):
 s=p.stat(); h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return {'size':s.st_size,'mtime_ns':s.st_mtime_ns,'sha256':h.hexdigest()}
def package(n):return json.loads(next((REC/'012_packages').glob(f'012_impl-{n:03}_*.json')).read_text())
def prepare():
 files={Path(p) for p in json.loads((REC/'013_input_before.json').read_text())['files']}
 for n in range(4,14):
  files.update(p for p in REC.rglob(f'{n:03}_*') if p.is_file());files.update((ROOT/'notes').glob(f'{n:03}_*'))
 for n in range(1,11):
  p=package(n);files.update(Path(p['differences'][k]) for k in ('prediction_database','gold_database'))
 files.add(Path('/mnt/c/Users/jucc116/Desktop/标注手册_v0.md'));files.add(ROOT/'docs/标注手册_v0.md')
 save(REC/'014_input_before.json',{'files':{str(p):fp(p) for p in sorted(files)}})
 trace=[]
 for n in range(1,11):
  task=f'impl-{n:03}';events=[]
  for p in sorted((ROOT/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent/.events/sessions').glob('*/events/*.json'),key=lambda p:int(p.stem)):
   e=json.loads(p.read_text());events.append({'path':str(p.relative_to(ROOT)),**{k:e[k] for k in ('id','source','action','observation','message','args','content','cause') if k in e}})
  save(REC/f'014_trace_{task}.json',events)
  trace.append((task,len(events)))
 print('fingerprinted',len(files),'traces',trace,flush=True)
def compare(c,g,schema,table,cols,keys):
 names=list(dict.fromkeys(keys+cols));ki=[names.index(k) for k in keys];ci=[names.index(k) for k in cols]
 def read(conn):return conn.execute('select '+','.join(normalized(k) for k in names)+f' from "{schema}"."{table}"').fetchall()
 pr,gr=read(c),read(g);out=[]
 for lev in range(4):
  def group(rows):
   d=defaultdict(Counter)
   for r in rows:d[tuple(r[i] for i in ki)][tuple(r[i] if not lev else normal_forms(r[i])[lev-1] for i in ci)]+=1
   return d
  p,gp=group(pr),group(gr);common=p.keys()&gp.keys();onlyp=sum(sum(p[k].values()) for k in p.keys()-gp.keys());onlyg=sum(sum(gp[k].values()) for k in gp.keys()-p.keys())
  joint=sum(min(sum((p[k]-gp[k]).values()),sum((gp[k]-p[k]).values())) for k in common)
  count={}
  for i,col in enumerate(cols):
   diff=0
   for k in common:
    a,b=Counter(),Counter()
    for v,w in p[k].items():a[v[i]]+=w
    for v,w in gp[k].items():b[v[i]]+=w
    diff+=min(sum((a-b).values()),sum((b-a).values()))
   count[col]=diff
  a,b=Counter(),Counter()
  for cnt in p.values():a.update(cnt)
  for cnt in gp.values():b.update(cnt)
  out.append({'level':f'L{lev}','agent_rows':len(pr),'gold_rows':len(gr),'agent_only_key_rows':onlyp,'gold_only_key_rows':onlyg,'common_key_different_rows_or_min_pairs':joint,'column_mismatches':count,'whole_agent_unmatched':sum((a-b).values()),'whole_gold_unmatched':sum((b-a).values()),'value_only_whole_match':a==b,'whole_match':p==gp,'key_aware_agent_unmatched':sum(sum((p[k]-gp.get(k,Counter())).values()) for k in p),'key_aware_gold_unmatched':sum(sum((gp[k]-p.get(k,Counter())).values()) for k in gp),'common_key_agent_excess_rows':sum(max(sum(p[k].values())-sum(gp[k].values()),0) for k in common),'common_key_gold_excess_rows':sum(max(sum(gp[k].values())-sum(p[k].values()),0) for k in common)})
 return {'levels':out,'first_match':next((r['level'] for r in out if r['whole_match']),None)}
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()

def reruns(n,patches):
 pkg=package(n);b=pkg['differences'];sqlpath=Path(pkg['agent_final_SQL'][0]['path']);original=sqlpath.read_text();goldsql=Path(pkg['gold_SQL_仅供定位差异'][0]['path']).read_text()
 case=json.loads((REC/'013_cases.json').read_text())[n-1];source=case['agent_database'] if n not in (3,8) else b['gold_database']
 work=WORK/f'impl-{n:03}';work.mkdir(exist_ok=True);out={'task':f'impl-{n:03}','source':source,'basis':b,'original_sql_sha256':fp(sqlpath)['sha256'],'runs':[]}
 with duckdb.connect(str(work/'rerun.duckdb')) as c,duckdb.connect(b['gold_database'],read_only=True) as g,duckdb.connect(b['prediction_database'],read_only=True) as retained:
  c.execute('SET threads=1');c.execute("SET memory_limit='1GB'")
  c.execute("ATTACH '"+source+"' AS src (READ_ONLY)")
  refs=set(re.findall(r'\b(?:FROM|JOIN)\s+((?:raw|staging|intermediate|marts)\.[a-zA-Z_0-9]+)',original,re.I))
  for ref in sorted(refs):
   schema,table=ref.split('.');c.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"');c.execute(f'CREATE OR REPLACE TABLE {ref} AS SELECT * FROM src.{ref}')
  c.execute(f'CREATE SCHEMA IF NOT EXISTS "{b["actual_schema"]}"')
  out['private_copy_tables']=sorted(refs);out['retained']=compare(retained,g,b['actual_schema'],b['table'],b['comparison_columns'],b['key_columns'])
  for label,changes in [('baseline',[])]+patches:
   modified=original;edits=[]
   for old,new in changes:
    assert modified.count(old)==1,(n,label,old,modified.count(old))
    start=modified.index(old);edits.append({'old':old,'new':new,'offset':start});modified=modified.replace(old,new,1)
   p=work/f'{label}.sql';p.write_text(modified);row={'label':label,'edits':edits,'sql_path':str(p.relative_to(ROOT)),'sql_sha256':fp(p)['sha256'],'unchanged_outside_replacements':True}
   try:
    c.execute(f'CREATE OR REPLACE TABLE "{b["actual_schema"]}"."{b["table"]}" AS '+modified.rstrip().rstrip(';'))
    row['comparison']=compare(c,g,b['actual_schema'],b['table'],b['comparison_columns'],b['key_columns'])
   except Exception as e:row['error']=str(e)
   out['runs'].append(row);save(REC/f'014_reruns_impl-{n:03}.json',out)
  # Evaluate gold SQL on the exact same private source; diagnostic only, never a U intervention.
  try:
   c.execute(f'CREATE OR REPLACE TABLE "{b["actual_schema"]}"."{b["table"]}" AS '+goldsql.rstrip().rstrip(';'))
   out['gold_sql_same_input_diagnostic']=compare(c,g,b['actual_schema'],b['table'],b['comparison_columns'],b['key_columns'])
  except Exception as e:out['gold_sql_same_input_diagnostic']={'error':str(e)}
 save(REC/f'014_reruns_impl-{n:03}.json',out)
 print(n,'completed',len(out['runs']),flush=True)
