"""Index every original event and retain disclosure text; no inferred labels."""
from review_dacomp_batch021 import *
import hashlib,re
out=[]
for task in sorted(set(x['task'] for x in rows)):
 root=ROOT/'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01'/task/'agent'
 events=[]
 for p in sorted(root.glob('.events/sessions/*/events/*.json'),key=lambda p:int(p.stem)):
  e=json.loads(p.read_text());events.append((p,e))
 relevant=[(i,r) for i,r in enumerate(rows) if r['task']==task]
 for i,r in relevant:
  d=pkg(i);terms=set([r['table']]+d['trace_excerpts']['actual_read_sources_from_008_B7']);terms.update(x.split('.')[-1] for x in list(terms));visible=[];actions=[]
  for p,e in events:
   content=e.get('content','');command=e.get('args',{}).get('command','');hits=[t for t in terms if t in content]
   if hits:
    excerpts=[(j+1,l) for j,l in enumerate(content.splitlines()) if any(t in l for t in hits)]
    visible.append({'event':e['id'],'cause':e.get('cause'),'path':str(p.relative_to(ROOT)),'hits':hits,'explicit_truncation':bool(re.search(r'Observation truncated|response clipped|output truncated',content,re.I)),'matching_lines':excerpts})
   if any(t in command for t in terms):actions.append({'event':e['id'],'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  report=root/f'dacomp-de-{task}'/'result.md';out.append({'index':i,'task':task,'table':r['table'],'events_scanned':len(events),'visible':visible,'actions':actions,'report_path':str(report.relative_to(ROOT)),'report_text':report.read_text() if report.exists() else None})
 print('\n',task,'events',len(events))
 for p,e in events:
  args=e.get('args',{});s=args.get('thought','') or args.get('final_thought','') or (e.get('message','') if e.get('action') in ['message','finish'] and e['id']>2 else '')
  if s:print(e['id'],s)
 report=root/f'dacomp-de-{task}'/'result.md'
 if report.exists():print('REPORT',report.read_text())
(REC/'021_trace_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
