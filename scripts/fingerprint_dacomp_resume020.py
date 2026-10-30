"""Continuation snapshot; preserve both original task020 and pause snapshots."""
from fingerprint_dacomp_batch020 import ROOT,REC,fp
import json,sys,subprocess,datetime
phase=sys.argv[1]
assert phase in ('before','after')
p=REC/f'020_resume_input_{phase}.json'
assert not p.exists(), f'Refusing to overwrite {p}'
prior=json.loads((REC/('020_input_after.json' if phase=='before' else '020_resume_input_before.json')).read_text())
paths={ROOT/x for x in subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()}|{__import__('pathlib').Path(x) for x in prior['files']}
files={str(x):fp(x) for x in sorted(paths) if x.is_file()}
changed=[x for x,y in prior['files'].items() if files.get(x)!=y]
original=json.loads((REC/'020_input_before.json').read_text())
immutable_changes=[x for x,y in original['files'].items() if files.get(x)!=y]
result=dict(phase=phase,timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files,changes_since_previous=changed,original_input_changes=immutable_changes)
p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(len(files),'previous changes',len(changed),'original changes',immutable_changes)
assert not immutable_changes
