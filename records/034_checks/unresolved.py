from replay import *
run('astronomy-hard-8',[1,4,5,6,7,8,9],(9,'n=len(sub); tr=np.arange(int(n*.8)); te=np.arange(int(n*.8),n)','n=len(sub); tr=np.arange(int(n*.7)); te=np.arange(int(n*.7),n)'),label='chrono70_retry',extra="answer=[]\nfor col in ['kp','pdyn']:\n m=LinearRegression().fit(sub.loc[tr,[col]],sub.loc[tr,'y']);answer.append(mean_squared_error(sub.loc[te,'y'],m.predict(sub.loc[te,[col]]))**.5)")

import pandas as pd
p=ROOT/'data/kramabench/data/archeology/input/conflict_brecke.csv'
d=pd.read_csv(p)
x=d[d.StartYear.between(800,1400)&((d.EndYear-d.StartYear)>=1)]
n=0
for name,g in x.groupby('Conflict'):
 end=-99999
 for row in g.sort_values('StartYear').itertuples():
  if row.StartYear>end:n+=1
  end=max(end,row.EndYear)
out={'query':'StartYear between 800 and 1400 and EndYear-StartYear>=1; group exact Conflict; merge overlapping intervals','baseline':len(x),'merged':{'Conflict':n}}
(OUT/'conflict_diagnostic.json').write_text(json.dumps(out,indent=2))
