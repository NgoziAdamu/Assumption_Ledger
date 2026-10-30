from annotate_dacomp_batch024 import *
inv=json.loads((REC/'024_package_inventory.json').read_text())
plans=json.loads((REC/'024_patch_plan.json').read_text()) if (REC/'024_patch_plan.json').exists() else []
for r in inv:
 if r['purpose']=='校准' or (len(sys.argv)>1 and r['task'] not in sys.argv[1:]):continue
 p=next((p for p in plans if p['table']==r['table']),{'patches':[]})
 path=REC/f"024_reruns_{r['task']}_{r['table']}.json"
 if path.exists() and {x['label'] for x in json.loads(path.read_text())['runs']}=={'baseline',*[x['label'] for x in p['patches']]}:continue
 pkg=json.loads((ROOT/r['full_json']).read_text());b=pkg['differences'];clock=p.get('clock') or b.get('candidate_date')
 if clock and len(clock)==10:clock+=' 00:00:00+00'
 if not clock:clock='2025-10-13 00:00:00+00'
 try:rerun(int(r['task'][-3:]),[(x['label'],x['edits']) for x in p['patches']],clock=clock,pkg=pkg)
 except Exception as e:save(REC/f"024_error_{r['task']}_{r['table']}.json",{'error':str(e)});print(r['table'],repr(e),flush=True)
