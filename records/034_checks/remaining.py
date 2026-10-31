from replay import *
run('astronomy-easy-6',[1,2,3],extra="answer=[]\nfor fn in ['58214_quiet.csv','58214_storm.csv']:\n d=pd.read_csv(os.path.join(base,fn));t=pd.to_datetime(d.EPOCH);n=d.MEAN_MOTION.to_numpy()*2*np.pi/86400;a=(mu/n**2)**(1/3);day=(t-t.min()).dt.total_seconds().to_numpy()/86400;answer.append(round(float((a[-1]-a[0])/(day[-1]-day[0])),4))",label='endpoint_diagnostic')
run('astronomy-hard-8',[1,4,5,6,7,8,9],extra="answer=sub.shape",label='split_candidates')
run('legal-hard-17',[1,2,3,4,5],(5,'auto_2024/total_2024','.0304'),label='printed_share')
run('legal-hard-22',[2,3,4],(4,'denom=6471708','denom=1135291'),label='identity_denominator')
run('archeology-hard-1',[1,2,3,4,5,6,7,8],(8,'ages=np.array([6.005,6.412])','ages=np.arange(6005,6413)/1000'),extra='answer=round(float(vals.mean()),4)',label='interval_mean')
(OUT/'remaining_summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2,default=str))
