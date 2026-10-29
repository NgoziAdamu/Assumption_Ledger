"""v1 annotation evidence. All original databases READ_ONLY; new execution under data/016_work."""
from annotate_dacomp_batch014 import ROOT,REC,fp,save,package
from dacomp_tolerance import normalized,udf_forms
from pathlib import Path
from collections import Counter
import duckdb,json,re,sys
WORK=ROOT/'data/016_work';WORK.mkdir(exist_ok=True)
def prepare():
 files={Path(p) for p in json.loads((REC/'015_input_before.json').read_text())['files']}
 for i in range(4,16):
  files.update(p for p in REC.rglob(f'{i:03}_*') if p.is_file());files.update((ROOT/'notes').glob(f'{i:03}_*'))
 files.update([ROOT/'docs/标注手册_v1.md',Path('/mnt/c/Users/jucc116/Desktop/标注手册_v1.md')])
 missing=[str(p) for p in sorted(files) if not p.exists()]; current={str(p):fp(p) for p in sorted(files) if p.exists()}; previous=json.loads((REC/'015_input_before.json').read_text())['files']; delta=[p for p in previous if p in current and {'size':previous[p].get('size',previous[p].get('bytes')),'mtime_ns':previous[p]['mtime_ns'],'sha256':previous[p]['sha256']}!=current[p]]; save(REC/'016_input_before.json',{'files':current,'missing_prior_external_files':missing,'comparison_to_015_before_changes':delta,'timing_note':'First snapshot failed on missing external v0 attachment; successful snapshot after first private reruns, with original files independently compared to task015 pre-snapshot.'}); assert not delta,delta
 for n in range(11,21):
  events=[]
  for p in sorted((ROOT/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-{n:03}/agent/.events/sessions').glob('*/events/*.json'),key=lambda x:int(x.stem)):
   e=json.loads(p.read_text());events.append({'path':str(p.relative_to(ROOT)),**{k:e[k] for k in ['id','action','observation','args','message','content','thought','cause'] if k in e}})
  save(REC/f'016_trace_impl-{n:03}.json',events)
 print('prepared',len(files),flush=True)
def add_scales(result,b):
 cols=list(dict.fromkeys(b['key_columns']+b['comparison_columns']))
 for x in result['levels']:
  a=x['agent_only_key_rows']+x.get('common_key_agent_excess_rows',0);g=x['gold_only_key_rows']+x.get('common_key_gold_excess_rows',0)
  x['row_scale']=a+g+x['common_key_different_rows_or_min_pairs'];x['cell_scale']=(a+g)*len(cols)+sum(x['column_mismatches'].values());x['comparison_column_count_including_keys']=len(cols)
 return result
def reuse():
 for n in range(1,11):
  if (REC/f'016_reruns_impl-{n:03}.json').exists():continue
  x=json.loads((REC/f'014_reruns_impl-{n:03}.json').read_text());x['reused_from']=f'records/014_reruns_impl-{n:03}.json';add_scales(x['retained'],x['basis'])
  for r in x['runs']:add_scales(r['comparison'],x['basis'])
  if 'levels' in x.get('gold_sql_same_input_diagnostic',{}):add_scales(x['gold_sql_same_input_diagnostic'],x['basis'])
  save(REC/f'016_reruns_impl-{n:03}.json',x)
 print('reused first10')
def compare_sql(c,pref,gref,b):
 keys=b['key_columns'];cols=list(dict.fromkeys(keys+b['comparison_columns']));out=[]
 for side,ref in [('p',pref),('g',gref)]:
  select=','.join(normalized(col)+f' c{i}' for i,col in enumerate(cols));key='list_value('+','.join(normalized(k) for k in keys)+') key0'
  c.execute(f'CREATE OR REPLACE TEMP TABLE {side}0 AS SELECT {key},{select},count(*)::BIGINT w FROM {ref} GROUP BY ALL')
  c.execute(f'CREATE OR REPLACE TEMP TABLE {side}k AS SELECT key0,sum(w) n FROM {side}0 GROUP BY key0')
 c.execute('CREATE OR REPLACE TEMP TABLE kg AS SELECT key0,pk.n pn,gk.n gn FROM pk FULL JOIN gk USING(key0)')
 a,g,ea,eg,pr,gr=c.execute('''SELECT coalesce(sum(pn) FILTER(WHERE gn IS NULL),0),coalesce(sum(gn) FILTER(WHERE pn IS NULL),0),coalesce(sum(greatest(pn-gn,0)) FILTER(WHERE pn IS NOT NULL AND gn IS NOT NULL),0),coalesce(sum(greatest(gn-pn,0)) FILTER(WHERE pn IS NOT NULL AND gn IS NOT NULL),0),sum(pn),sum(gn) FROM kg''').fetchone()
 # Dictionary normalizes each distinct literal once, using established L1-L3 rules.
 c.execute('CREATE OR REPLACE TEMP TABLE vals AS '+ ' UNION '.join(f'SELECT c{i} v FROM {s}0' for s in ('p','g') for i in range(len(cols))))
 c.execute('CREATE OR REPLACE TEMP TABLE forms AS SELECT v,tolerance_forms(v) f FROM vals')
 for lev in range(4):
  for side in ('p','g'):
   sel=','.join((f'c{i}' if lev==0 else (f'c{i}' if cols[i] in keys else f'd{i}.f.l{lev}'))+f' AS c{i}' for i in range(len(cols)))
   joins='' if not lev else ''.join(f' JOIN forms d{i} ON c{i}=d{i}.v' for i in range(len(cols)) if cols[i] not in keys)
   c.execute(f'CREATE OR REPLACE TEMP TABLE {side}v AS SELECT key0,{sel},sum(w)::BIGINT w FROM {side}0{joins} GROUP BY ALL')
  names=','.join(['key0']+[f'c{i}' for i in range(len(cols))]);c.execute(f'CREATE OR REPLACE TEMP TABLE residual AS SELECT {names},greatest(coalesce(pv.w,0)-coalesce(gv.w,0),0) a,greatest(coalesce(gv.w,0)-coalesce(pv.w,0),0) g FROM pv FULL JOIN gv USING({names})')
  au,gu,joint=c.execute('''WITH r AS(SELECT key0,sum(a) a,sum(g) g FROM residual GROUP BY key0) SELECT sum(a),sum(g),coalesce(sum(least(a,g)) FILTER(WHERE pn IS NOT NULL AND gn IS NOT NULL),0) FROM r JOIN kg USING(key0)''').fetchone()
  # After exact row cancellation, pair residual rows by fixed-key + lexical tuple order.
  # This keeps row and cell counts on the same pairing, including duplicate keys.
  order=','.join(f'c{i}' for i in range(len(cols)))
  for side,weight in [('pa','a'),('ga','g')]:
   c.execute(f'CREATE OR REPLACE TEMP TABLE {side} AS SELECT key0,{order},row_number() OVER(PARTITION BY key0 ORDER BY {order},ordinal) rn FROM residual,UNNEST(range(cast({weight} AS BIGINT))) AS u(ordinal) WHERE {weight}>0')
  q='SELECT '+','.join(f"coalesce(sum(CASE WHEN pa.c{i}<>ga.c{i} THEN 1 ELSE 0 END),0)" for i in range(len(cols)))+' FROM pa JOIN ga USING(key0,rn)'
  counts=dict(zip(cols,map(int,c.execute(q).fetchone())))
  out.append(dict(level=f'L{lev}',agent_rows=int(pr or 0),gold_rows=int(gr or 0),agent_only_key_rows=int(a),gold_only_key_rows=int(g),common_key_agent_excess_rows=int(ea),common_key_gold_excess_rows=int(eg),common_key_different_rows_or_min_pairs=int(joint or 0),column_mismatches=counts,key_aware_agent_unmatched=int(au or 0),key_aware_gold_unmatched=int(gu or 0),whole_match=not au and not gu))
 return add_scales({'levels':out,'first_match':next((r['level'] for r in out if r['whole_match']),None)},b)
def rerun(n,patches,clock=None):
 pkg=package(n);b=pkg['differences'];case=json.loads((REC/'013_cases.json').read_text())[n-1];source=case['agent_database'] if b['actual_schema']=='staging' else b['gold_database'];orig=Path(pkg['agent_final_SQL'][0]['path']).read_text();sql=orig
 clock_edits=[]
 if clock:
  for pat,new in [(r'\bcurrent_timestamp\b',f"TIMESTAMPTZ '{clock}'"),(r'\bcurrent_date\b',f"DATE '{clock[:10]}'")]:
   sql,k=re.subn(pat,new,sql,flags=re.I);clock_edits.append({'pattern':pat,'replacement':new,'count':k})
 work=WORK/f'impl-{n:03}';work.mkdir(exist_ok=True);out={'task':f'impl-{n:03}','basis':b,'source':source,'clock_control':clock_edits,'runs':[]}
 with duckdb.connect(str(work/'work.duckdb')) as c:
  c.execute("SET threads=2; SET memory_limit='1500MB'");c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
  for alias,path in [('src',source),('gold',b['gold_database']),('retained',b['prediction_database'])]:
   # same path aliases are allowed if already attached: use original alias in refs instead.
   existing=next((a for a,p in out.get('attached',[]) if p==path),None)
   if not existing:c.execute("ATTACH '"+path+f"' AS {alias} (READ_ONLY)");out.setdefault('attached',[]).append((alias,path))
   out[alias+'_alias']=existing or alias
  refs=set(re.findall(r'\b(?:FROM|JOIN)\s+((?:raw|staging|intermediate|marts|mart)\.[a-zA-Z_0-9]+)',sql,re.I));out['private_copy_tables']=sorted(refs)
  for ref in sorted(refs):
   sch=ref.split('.')[0];c.execute(f'CREATE SCHEMA IF NOT EXISTS {sch}');c.execute(f'CREATE OR REPLACE TABLE {ref} AS SELECT * FROM {out["src_alias"]}.{ref}')
  rel=b['actual_schema']+'.'+b['table'];c.execute(f'CREATE SCHEMA IF NOT EXISTS {b["actual_schema"]}')
  out['retained']=compare_sql(c,out['retained_alias']+'.'+rel,out['gold_alias']+'.'+rel,b)
  for name,edits in [('baseline',[])]+patches:
   modified=sql;detail=[]
   for old,new in edits:
    assert modified.count(old)==1,(n,name,old,modified.count(old));detail.append({'old':old,'new':new,'offset':modified.index(old)});modified=modified.replace(old,new,1)
   p=work/f'{name}.sql';p.write_text(modified);trial={'label':name,'edits':detail,'sql_path':str(p.relative_to(ROOT)),'sql_sha256':fp(p)['sha256']}
   try:
    c.execute(f'CREATE OR REPLACE TABLE {rel} AS '+modified.strip().rstrip(';'));trial['comparison']=compare_sql(c,rel,out['gold_alias']+'.'+rel,b)
   except Exception as e:trial['error']=str(e)
   out['runs'].append(trial);save(REC/f'016_reruns_impl-{n:03}.json',out);print(n,name,'done',trial.get('error',''),flush=True)
 save(REC/f'016_reruns_impl-{n:03}.json',out)
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare();reuse()
