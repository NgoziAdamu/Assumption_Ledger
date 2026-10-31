import csv,json,hashlib,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'records/036_checks'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(n):return list(csv.DictReader((R/f'records/{n}.csv').open()))
old=rows('034_objects');objs=rows('036_objects');op=rows('034_points');pts=rows('036_points');aud=json.loads((O/'disclosure_audit.json').read_text());grades={1:'交付物里针对本处说明了',2:'交付物里只有通用说明',3:'过程中意识到了，交付物里没提',4:'看到了相关信息，但没有意识到的迹象',5:'没有迹象'}
assert len(objs)==72 and len(pts)==123 and len(aud)==123
assert {x['对象编号'] for x in old}=={x['对象编号'] for x in objs}
key=lambda x:(x['benchmark'],x['对象编号'],x['错误点名称'])
assert set(map(key,op))==set(map(key,pts))==set(map(key,aud))
assert len(set(map(key,pts)))==123
for p in pts:
 a=next(a for a in aud if key(a)==key(p));prior=next(x for x in op if key(x)==key(p));assert p['是否说出（五档）']==grades[a['grade']]
 assert p['相对034'] in ['未改','只改档位','改类别','补完无法判定']
 if a['grade']<=3:assert a['evidence'] and all(e['quote'] and e['event'] for e in a['evidence'])
 for field in ['证据在场','曾经理解对过','系统提示是否适用']:assert p[field]==prior[field]
 if p['类别'] in ['已说出的选择','已说出的降级']:assert a['grade']==1
 if a['grade']>=2:assert p['类别'] not in ['已说出的选择','已说出的降级']
 # Check evidence quotations against sources, including unchanged object rows.
 for e in a['evidence']:
  path=Path(e['source']);path=path if path.is_absolute() else R/path
  if path.suffix=='.md':assert e['quote'] in path.read_text(),(key(a),e['event'])
  elif 'trace_' in path.name and path.name!='dacomp_trace_presence.json':
   event,field=e['event'].split('.',1);v=next(v for v in json.loads(path.read_text()) if v['id']==int(event))
   for sub in field.split('.'):v=v[sub]
   assert e['quote'] in v,(key(a),e['event'])
  elif path.name=='dacomp_trace_presence.json':assert any(x['paragraph']==e['quote'] for x in json.loads(path.read_text()))
expected={('kramabench' if o['benchmark']=='KramaBench' else 'dacomp')+'_'+o['对象编号']+'.md' for o in objs if o['相对034']!='未改'}
assert expected=={p.name for p in (R/'records/036_annotations').glob('*.md')}
assert next(o for o in objs if o['对象编号']=='astronomy-hard-11')['主要原因']=='未交卷'
assert not any(p['对象编号']=='astronomy-hard-11' for p in pts)
assert next(o for o in objs if o['对象编号']=='archeology-hard-5')['相对034']=='未改'
protected=json.loads((O/'protected_before.json').read_text());changed=[p for p,h in protected.items() if not (R/p).exists() or sha(R/p)!=h];assert not changed,changed
src=Path('/mnt/c/Users/jucc116/Downloads/标注手册_v3.1.md');dst=R/'docs/标注手册_v3.1.md';assert src.read_bytes()==dst.read_bytes()
provenance={'source':str(src),'destination':str(dst.relative_to(R)),'source_sha256':sha(src),'destination_sha256':sha(dst),'bytes':dst.stat().st_size,'copy':'原始字节复制，未编辑；v3保留','task_number':'036','number_check':'开始时notes和records没有036编号，沿用036'}
(O/'manual_provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2))
inputs=[R/'data/kramabench/data/archeology/input/climateMeasurements.xlsx',*[R/f'data/kramabench/data/astronomy/input/space-track/58214_{t}.csv' for t in ['quiet','storm']]]
(O/'rerun_input_hashes.json').write_text(json.dumps({str(p.relative_to(R)):sha(p) for p in inputs},ensure_ascii=False,indent=2))
# No pre-existing tracked file changed. All additions must be this task or the copied manual.
status=subprocess.check_output(['git','status','--porcelain','-uall'],cwd=R,text=True)
head_changes=subprocess.check_output(['git','diff','HEAD','--name-status'],cwd=R,text=True).splitlines()
assert all(line.startswith('A\t') for line in head_changes), 'Pre-existing tracked file changed'
result={'objects':len(objs),'points':len(pts),'annotations':len(expected),'quote_checks':'all passed','protected_file_hashes_checked':len(protected),'protected_changes':changed,'manual_sha256':sha(dst),'original_tracked_changes':[],'status':'PASS'}
(O/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
