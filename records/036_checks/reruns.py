import re,json,io,contextlib,hashlib,traceback
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[2];O=R/'records/036_checks'
def blocks(id):return dict(re.findall(r'<!-- original:(.*?) chars:\d+ -->\n```[^\n]*\n(.*?)\n```',(R/f'records/028_kramabench_packages/{id}.md').read_text(),re.S))
b=blocks('archeology-hard-2');variants={
'baseline':None,
'direction':(7,".sort_values('age')",".sort_values('age',ascending=False)"),
'annual_grid':(7,"delta=valid['index'].diff()","valid=pd.DataFrame({'age':np.arange(np.ceil(valid.age.min()*1000),np.floor(valid.age.max()*1000)+1)/1000}); valid['index']=np.interp(valid.age,ages[idx.notna()],idx[idx.notna()]); delta=valid['index'].diff()"),
'year_mean':(7,"delta=valid['index'].diff()","valid=valid.assign(year=(valid.age*1000).round().astype(int)).groupby('year',as_index=False)['index'].mean(); delta=valid['index'].diff()")}
results=[]
for label,patch in variants.items():
 ns={'np':np};ns['final_answer']=lambda a:ns.update(answer=a);out=io.StringIO();executed=[];err=None
 try:
  with contextlib.redirect_stdout(out):
   for n in range(1,9):
    src=b[f'step.{n}.code'];original=src
    if patch and n==patch[0]:assert src.count(patch[1])==1;src=src.replace(patch[1],patch[2])
    src=src.replace('/home/katherine/dac/benchmarks/KramaBench/data',str(R/'data/kramabench/data'));executed.append({'step':n,'original_sha256':hashlib.sha256(original.encode()).hexdigest(),'executed':src});exec(src,ns)
 except Exception:err=traceback.format_exc()
 ans=ns.get('answer');result={'id':'archeology-hard-2','variant':label,'patch':patch,'environment':'np available; input paths relocated only','steps':executed,'stdout':out.getvalue(),'error':err,'answer':ans,'gold':38.42,'scale':abs(ans-38.42) if ans is not None else None}
 (O/f'archeology-hard-2_{label}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str));results.append({k:result[k] for k in ['variant','answer','scale','error']})
# Endpoints recomputed from exact original step3; final constants refer to its printed estimates, retain original round(...,6).
b=blocks('astronomy-easy-6');ns={'pd':pd,'np':np,'os':__import__('os'),'base':str(R/'data/kramabench/data/astronomy/input/space-track')};buf=io.StringIO()
with contextlib.redirect_stdout(buf):exec(b['step.3.code'],ns)
est=[]
for f in ['58214_quiet.csv','58214_storm.csv']:
 d=pd.read_csv(Path(ns['base'])/f);t=pd.to_datetime(d.EPOCH);n=d.MEAN_MOTION.to_numpy()*2*np.pi/86400;a=(398600.4418/n**2)**(1/3);day=(t-t.min()).dt.total_seconds().to_numpy()/86400
 est.append({'regression':float(np.polyfit(day,a,1)[0]),'endpoint':float((a[-1]-a[0])/(day[-1]-day[0]))})
gold=[.0193,-.002];trials=[]
for name,method,sign in [('baseline','regression',-1),('estimator_only','endpoint',-1),('sign_only','regression',1),('both','endpoint',1)]:
 answer=[round(sign*x[method],6) for x in est];trials.append({'name':name,'answer':answer,'scale':sum(abs(x-y) for x,y in zip(answer,gold))})
(O/'astronomy-easy-6_scales.json').write_text(json.dumps({'original_step3':b['step.3.code'],'original_step4':b['step.4.code'],'stdout':buf.getvalue(),'estimates':est,'gold':gold,'trials':trials,'endpoint':'final constants reference original step3 rate estimates; round6 retained'},ensure_ascii=False,indent=2))
(O/'rerun_summary.json').write_text(json.dumps({'archeology-hard-2':results,'astronomy-easy-6':trials},ensure_ascii=False,indent=2));print(json.dumps({'archeology-hard-2':results,'astronomy-easy-6':trials},ensure_ascii=False,indent=2))
