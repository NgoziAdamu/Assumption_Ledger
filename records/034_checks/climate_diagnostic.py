import json
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[2]
p=R/'data/kramabench/data/archeology/input/climateMeasurements.xlsx'
d=pd.read_excel(p,header=5)
out={'shape':d.shape,'columns':list(d.columns),'variants':[]}
for sort in ['Age_ky','Age_ky.3']:
 for asc in [True,False]:
  s=d.sort_values(sort,ascending=asc)['ODP 967 wet-dry index']; n=int(s.diff().gt(0).sum());out['variants'].append({'sort':sort,'ascending':asc,'n':n,'all_rows':len(s),'non_null':int(s.notna().sum()),'percent_all':100*n/len(s),'percent_nonnull':100*n/(s.notna().sum()-1)})
(R/'records/034_checks/climate_diagnostic.json').write_text(json.dumps(out,indent=2,default=str));print(out)
