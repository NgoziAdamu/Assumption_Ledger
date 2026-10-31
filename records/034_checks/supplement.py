from replay import *
run('wildfire-easy-9',[1,3,4,5],label='retry')
run('legal-hard-18',[1,2,3,5,6],extra='answer=round(1070447*.1754*over40/known/1000)*1000',label='retry')
run('environment-hard-18',[1,2,3,4,5],(3," & d['Community'].isin(fresh_comms)",''),extra="answer={'rates':allf.groupby('year').is_exceed.mean().to_dict(),'rain':rain_df.loc[2020:2023].mean(axis=1).to_dict()}",label='scope_only')
run('wildfire-hard-17',[1,2,3],extra="fires=pd.read_csv(base+'/noaa_wildfires.csv'); ids=set(fires.station_verified_in_psa.dropna()); out={};\nfor col in ['NWS ID','WX ID','Station ID','OBJECTID']:\n if col in raw:\n  sel=raw[pd.to_numeric(raw[col],errors='coerce').isin(ids)]; out[col]={'matched_rows':len(sel),'mean':pd.to_numeric(sel.Elevation,errors='coerce').mean()}\nanswer=out",label='id_diagnostic')
run('environment-hard-16',[1,2,3,4],extra="answer={};\nfor keys in [['Beach Name'],['Community','Beach Name']]:\n for case in [False,True]:\n  m=marine.assign(v=marine.Violation.astype(str).str.lower().eq('yes') if case else marine.Violation.eq('yes')); answer[str(keys)+str(case)]=int((~m.groupby(keys).v.any()).sum())",label='identity_diagnostic')
(OUT/'supplement_summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2,default=str))
