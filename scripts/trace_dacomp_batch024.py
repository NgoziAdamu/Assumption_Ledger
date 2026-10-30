"""Mechanical full-action trace audit; originals remain unchanged."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];out=[]
for n in [6,16,22,23,24,25,26,27,28,29,30]:
 events=[]
 for p in sorted((ROOT/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-{n:03}/agent').glob('.events/sessions/*/events/*.json'),key=lambda p:int(p.stem)):
  e=json.loads(p.read_text());a=e.get('args',{})
  events.append(dict(id=e['id'],path=str(p.relative_to(ROOT)),action=e.get('action'),observation=e.get('observation'),cause=e.get('cause'),command=a.get('command'),thought=a.get('thought'),final=a.get('final_thought'),content=e.get('content') if e.get('observation') else None))
 out.append(dict(task=f'impl-{n:03}',events=events))
(ROOT/'data/024_trace_review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
# Only indexed actions/final statements in committed record; raw query outputs remain in data.
for t in out:
 for e in t['events']:e.pop('content',None)
(ROOT/'records/024_trace_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
