from common import *
import os,math
base=str(DATA/'astronomy/input')
spec=Path(base,'omni2_low_res/omni2.text').read_text()
print('Original field definitions:')
for line in spec.splitlines():
    if re_match:=__import__('re').match(r'^\s*(50|51)\s+\S+\s+\S+\s+(ap-index|f10\.7_index)',line,__import__('re').I):
        print(line)
print('pandas header=None: column 49 = WORD 50 ap-index; column 50 = WORD 51 f10.7_index')
df=pd.read_csv(os.path.join(base,'omni2_low_res/omni2_2024.dat'),sep=r'\s+',header=None)
lines=Path(base,'TLE/43180.tle').read_text().splitlines()
# Prerequisite computation copied verbatim from agent step 8.
tle=[]
for i in range(0,len(lines),2):
 l1,l2=lines[i:i+2]
 epoch=float(l1[18:32]); yy=int(epoch//1000); doy=epoch%1000
 ts=pd.Timestamp(year=2000+yy,month=1,day=1)+pd.Timedelta(days=doy-1)
 n=float(l2[52:63])
 a=(398600.4418/(n*2*np.pi/86400)**2)**(1/3)
 tle.append((ts,n,a))
t=pd.DataFrame(tle,columns=['epoch','n','a'])
t['hour']=t.epoch.dt.round('h')
print(t.head(), t.tail(),t.shape)
print('repeated rounded hours',t.hour.duplicated().sum(),'hour span',t.hour.min(),t.hour.max())
print(t.groupby('hour').size().value_counts().sort_index())
print('daily sample counts',t.groupby(t.hour.dt.date).size().describe())
# BEGIN MODIFIED STEP 9
# AP construct timestamps from year, day-of-year, hour
om=df.copy(); om['dt']=pd.to_datetime(om[0].astype(int).astype(str)+om[1].astype(int).astype(str).str.zfill(3),format='%Y%j')+pd.to_timedelta(om[2],unit='h')
om=om.set_index('dt'); ap=om[49].replace(999,np.nan)
print(ap.loc['2024-05-01':'2024-05-30'].describe(), ap.loc['2024-05-01':'2024-05-30'].isna().sum())
t['da']=t.a.diff()
# Difference in a (later minus prior)
obs=t.set_index('hour').da.dropna()
print('n obs',len(obs),'range',obs.min(),obs.max(), 'obs date range',obs.index.min(),obs.index.max())
# calculate correlation for positive lag means AP earlier (t-lag)
results=[]
for lag in range(49):
 x=ap.reindex(obs.index-pd.Timedelta(hours=lag))
 valid=pd.DataFrame({'drag':obs.values,'ap':x.values}).dropna()
 r=valid.drag.corr(valid.ap)
 results.append((lag,r,r*r,len(valid)))
print(sorted(results,key=lambda x:x[2],reverse=True)[:10])# END MODIFIED STEP 9
ranked=sorted(results,key=lambda x:x[2],reverse=True)
print('All 49 lag results:')
print(pd.DataFrame(results,columns=['lag_hours','r','r_squared','n']).to_string(index=False))
RESULT=finish({'column_49':'ap-index','column_50':'f10.7_index','ranking':'r_squared descending, same as original step 9',
 'top_5':[{'lag_hours':int(lag),'r':float(r),'r_squared':float(r2),'n':int(n)} for lag,r,r2,n in ranked[:5]]})
