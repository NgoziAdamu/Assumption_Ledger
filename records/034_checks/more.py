from replay import *
# Re-express final Boolean from exactly the retained computed rates.
extra="answer=bool((__import__('numpy').sign(allf.groupby('year').is_exceed.mean().diff().dropna()).to_numpy()==__import__('numpy').sign(rain_df.loc[2020:2023].mean(axis=1).diff().dropna()).to_numpy()).all())"
run('environment-hard-18',[1,2,3,4,5],(5,"allf['Violation'].eq('Yes')","allf['Violation'].str.lower().eq('yes')"),extra=extra,label='normalize_only')
# Combination explicitly logged separately, never described as single change.
b=blocks('environment-hard-18'); src=b['step.3.code'].replace(" & d['Community'].isin(fresh_comms)",'')
run('environment-hard-18',[1,2,3,4,5],(5,"allf['Violation'].eq('Yes')","allf['Violation'].str.lower().eq('yes')"),extra=src+"\nallf['is_exceed']=allf['Violation'].str.lower().eq('yes')\n"+extra,label='combination')
run('environment-hard-16',[1,2,3,4],extra="names=set(marine['Beach Name']); bad=set(all.loc[all.Violation.astype(str).str.lower().eq('yes'),'Beach Name']); answer=len(names-bad)",label='all_types_violations')
run('archeology-hard-9',[1,2,3,4,5,6,7],extra="m['rank_num']=m['rank'].map(rank_num); answer=round(float(m['rank_num'].corr(m['pop'])),6)",label='last_row')
run('archeology-hard-9',[1,2,3,4,5,6,7],(6,"matched.sort_values('anc_idx')","matched.assign(rank_numeric=matched['rank'].map(lambda x: sum(map(float,str(x).split('or')))/len(str(x).split('or')))).sort_values('rank_numeric')"),extra="answer=round(float(m['rank_num'].corr(m['pop'])),6)",label='highest_rank_diagnostic')
(OUT/'more_summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2,default=str))
