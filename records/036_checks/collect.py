import csv,json,hashlib,re
from pathlib import Path
R=Path(__file__).resolve().parents[2]
paths=[p for p in (R/'records').rglob('*') if p.is_file() and re.match(r'(018|019|020|021|022|023|024|025|034)',p.relative_to(R/'records').parts[0])]+[R/'docs/标注手册_v3.md']
baseline=R/'records/036_checks/protected_before.json'
current={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
if baseline.exists():
 assert json.loads(baseline.read_text())==current, 'Protected inputs changed; do not overwrite baseline'
else: baseline.write_text(json.dumps(current,ensure_ascii=False,indent=2))
objs=list(csv.DictReader(open(R/'records/034_objects.csv'))); out={}; audit=json.load(open(R/'records/018_uncertainty_audit.json'))
for o in objs:
 if o['benchmark']!='DAComp':continue
 obj=o['对象编号'];id,table=obj.split('_',1);base=Path('/home/katherine/dac/runs/20261025_de_official_batch_01')/id/'agent'/('dacomp-de-'+id)
 sqls=list((base/'sql').rglob(table+'.sql')); assert len(sqls)==1
 sql=sqls[0].read_text(); report=base/'result.md';report=report if report.exists() else base/'workspace/result.md';final=report.read_text() if report.exists() else ''; comments=[{'line':i,'text':l} for i,l in enumerate(sql.splitlines(),1) if '--' in l or '/*' in l or '*/' in l]
 trace=json.load(open(R/audit[id]['trace_file']));finish=[e for e in trace if e.get('action')=='finish' or e.get('args',{}).get('final_thought')]
 out[obj]={'report_path':str(report),'report':final,'sql_path':str(sqls[0]),'sql_comments':comments,'finish':finish,'report_sha256':hashlib.sha256(final.encode()).hexdigest(),'sql_sha256':hashlib.sha256(sqls[0].read_bytes()).hexdigest()}
(R/'records/036_checks/delivery_sources.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
for k,v in out.items():
 print('\n###',k,'COMMENTS',v['sql_comments']);print(v['report']);print('FINISH',[(e.get('id'),e.get('args',{}).get('final_thought','')) for e in v['finish']])
