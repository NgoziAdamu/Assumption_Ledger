from pathlib import Path
import json,re,sys
catalog=json.loads(Path('records/039_checks/evidence_catalog.json').read_text())
for c in catalog:
 if c['object'].split('_')[0]!=sys.argv[1]:continue
 s=Path(c['package']).read_text();contract=re.search(r'```yaml\n([\s\S]*?)\n```',s).group(1)
 print('\n###',c['object']);print(contract)
 print('AGENT SQL\n',Path(c['agent_sql']).read_text())
