from common import *
p=DATA/'archeology/input/radiocarbon_database_regional.xlsx'
d=pd.read_excel(p,header=0)
cols=['Region','Site','Culture','date','Latitude','Longitude']
r=d.iloc[766][cols]
print('data row index = 766; header excluded; Excel physical row = 768')
print(r.to_string())
RESULT=finish({'row_0_based':766,'values':json.loads(r.to_json(force_ascii=False,double_precision=15))})
