from common import *
import os
base=str(DATA/'wildfire/input')
# Agent step 4 input, unchanged parsing options.
noaa=pd.read_csv(os.path.join(base,'noaa_wildfires_monthly_stats.csv'),skiprows=2)
# BEGIN MODIFIED STEP 5
noaa['Year']=noaa['Date']//100
noaa_ann=noaa[noaa['Year'].between(2000,2024)].groupby('Year').agg(noaa_fires=('Number of Fires','sum'),noaa_acres=('Acres Burned','sum'))
nifc=pd.read_csv(os.path.join(base,'nifc_wildfires.csv'),sep='\t',dtype=str)
nifc['Year']=nifc['Year'].astype(int)
for c in ['Fires','Acres']:
 nifc[c]=pd.to_numeric(nifc[c].str.replace(',','',regex=False).str.replace('*','',regex=False),errors='coerce')
nifc_ann=nifc.set_index('Year')[['Fires','Acres']].rename(columns={'Fires':'nifc_fires','Acres':'nifc_acres'})
annual=noaa_ann.join(nifc_ann,how='inner')
annual['fire_diff']=annual.noaa_fires-annual.nifc_fires
annual['acres_diff']=annual.noaa_acres-annual.nifc_acres
print(annual.to_string())
print('count',len(annual),'correlation',annual[['fire_diff','acres_diff']].corr().iloc[0,1])# END MODIFIED STEP 5
value=float(annual[['fire_diff','acres_diff']].corr().iloc[0,1]);target=0.519
RESULT=finish({'years':annual.index.tolist(),'n_years':len(annual),'correlation':value,'rounded_3':round(value,3),'comparison':target,
 'difference_computed_minus_comparison':value-target,'rounded_3_difference':round(value,3)-target})
