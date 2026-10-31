from common import *
d=pd.read_excel(DATA/'archeology/input/climateMeasurements.xlsx',header=5)
age='Age_ky.3';value='ODP 967 wet-dry index'
c=d[[age,value]].dropna()
results={}
for ascending in [False,True]:
    s=c.sort_values(age,ascending=ascending)
    differences=s[value].diff().iloc[1:]
    rise=int(differences.gt(0).sum());fall=int(differences.lt(0).sum());ties=int(differences.eq(0).sum())
    pct=100*rise/len(differences)
    results['ascending' if ascending else 'descending']={'points':len(s),'adjacent_pairs':len(differences),
      'age_first':float(s[age].iloc[0]),'age_last':float(s[age].iloc[-1]),'increases':rise,'decreases':fall,'ties':ties,
      'percentage':pct,'percentage_2dp':f'{pct:.2f}'}
RESULT=finish({'valid_rows':len(c),'duplicate_age_rows':int(c[age].duplicated().sum()),'orders':results})
