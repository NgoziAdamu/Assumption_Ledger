"""Validate annotation evidence, single edits, scales, and immutable input inventory."""
from annotate_dacomp_batch016 import *
import csv,hashlib

def validate_comparator():
 with duckdb.connect(':memory:') as c:
  c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
  c.execute('CREATE TABLE a(id INT,x INT,y INT); CREATE TABLE b(id INT,x INT,y INT)')
  c.execute('INSERT INTO a VALUES(1,0,0),(1,1,1),(2,3,4)');c.execute('INSERT INTO b VALUES(1,0,1),(1,1,0),(3,3,4)')
  result=compare_sql(c,'a','b',{'key_columns':['id'],'comparison_columns':['x','y']})
  for x in result['levels']:
   assert x['row_scale']==4 and x['cell_scale']==8,x
   assert sum(x['column_mismatches'].values())==2,x
  c.execute('CREATE TABLE af(id INT,x DOUBLE);CREATE TABLE bf(id INT,x DOUBLE)')
  c.execute('INSERT INTO af VALUES(1,1.234)');c.execute('INSERT INTO bf VALUES(1,1.233)')
  result=compare_sql(c,'af','bf',{'key_columns':['id'],'comparison_columns':['x']})
  assert result['first_match']=='L2',result
 return ['duplicate-key row/cell pairing with identical column marginals','exclusive-key cells include key column','L2 first-match tolerance']
def validate():
 comparator_tests=validate_comparator();checks=[];decisions=json.loads((REC/'016_decisions.json').read_text())
 rows=list(csv.DictReader((REC/'016_annotations/016_summary.csv').open()));assert len(rows)==20
 assert len(list((REC/'016_annotations').glob('*.md')))==20
 for n in range(1,21):
  task=f'impl-{n:03}';p=package(n);r=json.loads((REC/f'016_reruns_{task}.json').read_text());orig=Path(p['agent_final_SQL'][0]['path']).read_text()
  # The reusable 014 runner uses explicit one-off history clock diagnostics, encoded in edits.
  controlled=orig
  for e in r.get('clock_control',[]):controlled=re.sub(e['pattern'],e['replacement'],controlled,flags=re.I)
  for trial in r['runs']:
   assert not trial.get('error'),(n,trial)
   expected=controlled
   for edit in trial['edits']:
    assert expected.count(edit['old'])==1,(n,trial['label'],'ambiguous patch')
    assert expected.index(edit['old'])==edit['offset'],(n,trial['label'],'offset')
    expected=expected.replace(edit['old'],edit['new'],1)
   actual=(ROOT/trial['sql_path']).read_text();assert expected==actual,(n,trial['label'],'extra edit')
   assert hashlib.sha256(actual.encode()).hexdigest()==trial['sql_sha256']
   c=trial['comparison'];assert c['first_match']==next((x['level'] for x in c['levels'] if x['whole_match']),None)
   for x in c['levels']:
    side=x['agent_only_key_rows']+x['gold_only_key_rows']+x.get('common_key_agent_excess_rows',0)+x.get('common_key_gold_excess_rows',0)
    assert x['row_scale']==side+x['common_key_different_rows_or_min_pairs']
    assert x['cell_scale']==side*len(set(r['basis']['comparison_columns']+r['basis']['key_columns']))+sum(x['column_mismatches'].values())
    assert x['cell_scale']>=x['row_scale'],(n,trial['label'],'inconsistent pairing')
    assert x['whole_match']==(x['row_scale']==0 and x['cell_scale']==0)
   checks.append({'task':task,'trial':trial['label'],'unchanged_outside_declared_edits':True,'scales_valid':True})
  assert int(rows[n-1]['核实查询条数'])<=5
  md=next((REC/'016_annotations').glob(f'016_{task}_*.md')).read_text();assert '## 规则问题' in md
  assert rows[n-1]['主要原因类别']==decisions[str(n)]['cat']
 assert (ROOT/'docs/标注手册_v1.md').read_bytes()==Path('/mnt/c/Users/jucc116/Desktop/标注手册_v1.md').read_bytes()
 save(REC/'016_validation.json',{'checks':checks,'comparator_tests':comparator_tests,'annotation_count':20,'manual_exact_copy':True,'all_passed':True});print('PASS',len(checks),'baseline/intervention SQL checks; 20 annotations')
def fingerprint_after():
 before=json.loads((REC/'016_input_before.json').read_text());after={};delta=[]
 for p,v in before['files'].items():
  if not Path(p).exists():delta.append({'path':p,'missing':True});continue
  now=fp(Path(p));after[p]=now
  if now!=v:delta.append({'path':p,'before':v,'after':now})
 out={'files':after,'changes':delta,'unchanged_count':len(after)-len(delta),'historical_015_comparison_changes':before['comparison_to_015_before_changes'],'snapshot_timing_exception':before['timing_note'],'missing_prior_external_files':before['missing_prior_external_files']}
 save(REC/'016_input_after.json',out);assert not delta,delta;print('PASS immutable size/mtime/SHA256',len(after),'files',flush=True)
if __name__=='__main__':
 if 'fingerprints' in sys.argv:fingerprint_after()
 else:validate()
