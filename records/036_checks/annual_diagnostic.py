import re,json
from pathlib import Path
import pandas as pd,numpy as np
R=Path(__file__).resolve().parents[2];p=R/'data/kramabench/data/archeology/input'
f=next(p.rglob('climateMeasurements.xlsx'));df=pd.read_excel(f,header=5)
b=dict(re.findall(r'<!-- original:(.*?) chars:\d+ -->\n```[^\n]*\n(.*?)\n```',(R/'records/028_kramabench_packages/archeology-hard-2.md').read_text(),re.S))
years=json.loads(b['subtask.4.answer']);goldbits=json.loads(b['subtask.5.answer']);results=[]
for col in ['Age_ky','Age_ky.3']:
 age=pd.to_numeric(df[col],errors='coerce');idx=pd.to_numeric(df['ODP 967 wet-dry index'],errors='coerce')
 for op,yr in [('round_age',1950-age.round()*1000),('floor_age',1950-np.floor(age)*1000),('round_year',1950-(age*1000).round())]:
  x=pd.DataFrame({'year':yr,'index':idx}).dropna();target=np.array(years);n=min(len(target),len(yr));match=int(np.equal(yr.iloc[:n].to_numpy(),target[:n]).sum())
  for ascending in [True,False]:
   z=x.sort_values('year',ascending=ascending);r=round(100*z['index'].diff().gt(0).sum()/(len(z)-1),2)
   results.append({'axis':col,'calendar_conversion':op,'ascending':ascending,'n':len(z),'answer':r,'scale':abs(r-38.42),'calendar_reference_length':len(target),'calendar_agreement_rows':match,'compared_rows':n})
out={'purpose':'diagnostic only: alternate axis and quantization are NOT proved fixes; assess unresolved hidden calendar pipeline','source':str(f.relative_to(R)),'variants':results,'reference_indicator_length':len(goldbits),'reference_indicator_mean':100*np.mean(goldbits)}
(R/'records/036_checks/archeology-hard-2_annual_diagnostic.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
