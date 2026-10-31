from common import *
base=DATA/'wildfire/input'
aq=pd.read_csv(base/'annual_aqi_by_county_2024.csv')
acres=pd.read_csv(base/'Wildfire_Acres_by_State.csv')
cols=['Unhealthy Days','Very Unhealthy Days','Hazardous Days']
assert not aq['Days with AQI'].eq(0).any()
aq['county_ratio']=(aq[cols[0]]+aq[cols[1]]+aq[cols[2]])/aq['Days with AQI']
state=aq.groupby('State')['county_ratio'].mean().rename('mean_county_ratio').reset_index()
merged=state.merge(acres[['State','Total Acres Burned']],on='State',how='inner',validate='one_to_one')
joined=merged.dropna(subset=['mean_county_ratio','Total Acres Burned'])
print('Joined states, after dropping missing values:');print(joined.to_string(index=False))
value=float(joined['mean_county_ratio'].corr(joined['Total Acres Burned']));target=0.6469
RESULT=finish({'county_rows':len(aq),'missing_county_ratios':int(aq.county_ratio.isna().sum()),'AQI_states':len(state),
 'joined_states_before_dropna':len(merged),'joined_states_after_dropna':len(joined),
 'AQI_states_without_acre_match':sorted(set(state.State)-set(acres.State)),
 'acre_states_without_AQI_match':sorted(set(acres.State)-set(state.State)),
 'joined_states_dropped_missing':merged.loc[~merged.index.isin(joined.index),'State'].tolist(),
 'correlation':value,'rounded_4':round(value,4),'comparison':target,'difference_computed_minus_comparison':value-target,'rounded_4_difference':round(value,4)-target})
