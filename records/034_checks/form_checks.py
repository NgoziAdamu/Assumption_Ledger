from replay import *
import ast
checks={
'environment-easy-2':lambda a: [int(x) for x in re.findall(r'(\d{4}) \(',a)],
'environment-easy-5':lambda a:a.split(' — ')[0],
'environment-hard-15':lambda a:a.split(' — ')[0],
'environment-hard-20':lambda a:[re.sub(r' \(\d+ violations?\)$','',x) for x in a],
'environment-hard-7':lambda a:float(a.split()[0]),
'legal-hard-14':lambda a:[x[0] for x in a],
'legal-hard-24':lambda a:a.split(' (')[0].replace(', CA',' CA'),
'legal-hard-29':lambda a:a.split(' — ')[0],
'legal-hard-8':lambda a:str(a),
'wildfire-easy-1':lambda a:int(re.search(r'([\d,]+) acres',a)[1].replace(',','')),
'wildfire-hard-4':lambda a:float(re.search(r'\$([\d,.]+)',a)[1].replace(',','')),
'wildfire-hard-16':lambda a:[round(x,3) for x in a],
'biomedical-hard-8':lambda a:sorted(set(x.split('-')[0] for x in a)),
}
r=[]
for id,fn in checks.items():
 b=blocks(id)
 def val(s):
  try:return json.loads(s)
  except:return s
 a=val(b['final_answer']); g=val(b['gold_answer']); v=fn(a)
 r.append({'id':id,'before':a,'after':v,'gold':g,'equal':v==g,'operation':__import__('inspect').getsource(fn).strip(),'kind':'output-only diagnostic; no recomputation'})
(OUT/'form_checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print([(x['id'],x['equal']) for x in r])
