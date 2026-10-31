"""Deterministic private in-memory replay. No model calls, no database writes."""
import re,json,contextlib,io,traceback,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'records/034_checks'
results=[]
def blocks(id):
 s=(ROOT/f'records/028_kramabench_packages/{id}.md').read_text()
 return dict(re.findall(r'<!-- original:(.*?) chars:\d+ -->\n```[^\n]*\n(.*?)\n```',s,re.S))
def run(id,steps,change=None,extra='',label='baseline',prelude=''):
 b=blocks(id); ns={}; buf=io.StringIO(); codes=[]
 ns['final_answer']=lambda x: ns.update(answer=x)
 try:
  with contextlib.redirect_stdout(buf),contextlib.redirect_stderr(buf):
   if prelude: exec(prelude,ns)
   for n in steps:
    src=b[f'step.{n}.code']; original=src
    if change and n==change[0]:
     assert src.count(change[1])==1,(id,n,change)
     src=src.replace(change[1],change[2])
    # Only relocate historical input path; numerical code otherwise unchanged.
    src=src.replace('/home/katherine/dac/benchmarks/KramaBench/data',str(ROOT/'data/kramabench/data'))
    codes.append({'step':n,'original_sha256':hashlib.sha256(original.encode()).hexdigest(),'executed':src})
    exec(compile(src,f'{id}/step{n}','exec'),ns)
   if extra: exec(extra,ns)
  ans=ns.get('answer'); err=None
 except Exception: ans=None;err=traceback.format_exc()
 record={'id':id,'label':label,'change':change,'steps':codes,'environment_prelude':prelude,'diagnostic_suffix':extra,'answer':ans,'error':err,'stdout':buf.getvalue()}
 (OUT/f'{id}_{label}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,default=str))
 results.append({k:record[k] for k in ['id','label','answer','error']})
 print(id,label,ans,err and err.splitlines()[-1],flush=True)
 return ns
if __name__=='__main__':
 run('archeology-hard-7',[1,2,3,5,6])
 run('archeology-hard-7',[1,2,3,5,6],(6,'mins<=0.1','dist<=0.1'),label='euclidean')
 run('environment-easy-3',[1,2,3,7],extra='answer=int(((wide[2012].notna())&(wide[2013]>wide[2012])).sum())',label='all_beaches')
 run('environment-hard-16',[1,2,3,4,5],extra="answer=int((~marine.assign(v=marine.Violation.astype(str).str.strip().str.lower().eq('yes')).groupby('Beach Name').v.any()).sum())",label='all_beaches')
 run('environment-hard-18',[1,2,3,4,5],extra="answer={'exceedance':allf.groupby('year').is_exceed.mean().to_dict(),'rain':rain_df.loc[2020:2023].mean(axis=1).to_dict()}",label='baseline_rates')
 run('environment-hard-18',[1,2,3,4,5],(5,"eq('Yes')","eq('yes')"),extra="answer={'exceedance':allf.groupby('year').is_exceed.mean().to_dict(),'rain':rain_df.loc[2020:2023].mean(axis=1).to_dict()}",label='case_only')
 run('wildfire-hard-17',[1,2,3,4,5,6])
 run('wildfire-hard-17',[1,2,3,4,5],extra="fires=pd.read_csv(base+'/noaa_wildfires.csv'); ids=set(fires.station_verified_in_psa.dropna()); sel=raw[pd.to_numeric(raw['WX ID'],errors='coerce').isin(ids)]; answer={'matched_rows':len(sel),'mean':pd.to_numeric(sel.Elevation,errors='coerce').mean()}",label='monitoring_stations')
 run('wildfire-easy-9',[1,2,3,4,5])
 run('legal-hard-18',[1,3,5,6],extra='answer=round(1070447*.1754*over40/known/1000)*1000',label='distribution_2024')
 # Existence diagnostics (no data copied).
 files=[str(p.relative_to(ROOT/'data/kramabench/data')) for p in (ROOT/'data/kramabench/data').rglob('*') if p.is_file() and ('WeatherEvents' in p.name or 'ZHVI' in p.name)]
 (OUT/'missing_files.json').write_text(json.dumps({'searched':'data/kramabench/data recursively','matches':files},indent=2))
 (OUT/'replay_summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2,default=str))
