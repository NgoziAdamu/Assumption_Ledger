from common import *
base=DATA/'archeology/input'
r=pd.read_csv(base/'roman_cities.csv')
w=pd.read_csv(base/'worldcities.csv')
istanbul=w[w['city_ascii'].eq('Istanbul')]
assert len(istanbul)==1
print('Istanbul row:');print(istanbul.to_string(index=True))
lat=float(istanbul.iloc[0]['lat']);lon=float(istanbul.iloc[0]['lng'])
distance=np.hypot(r['Latitude (Y)']-lat,r['Longitude (X)']-lon)
hits=r.loc[distance.lt(0.1),['Ancient Toponym','Barrington Atlas Rank']].copy()
hits['distance_degrees']=distance[distance.lt(0.1)]
hits.index.name='row_0_based'
print(hits.to_string())
b=hits.index[hits['Ancient Toponym'].eq('Byzantium')].tolist()
c=hits.index[hits['Ancient Toponym'].eq('Chalcedon')].tolist()
RESULT=finish({'Istanbul_lat':lat,'Istanbul_lng':lon,'matches':json.loads(hits.reset_index().to_json(orient='records',double_precision=15)),
 'Byzantium_rows':b,'max_matching_row':int(hits.index.max()),'Byzantium_is_max_row':bool(b and max(b)==hits.index.max()),'Chalcedon_rows':c})
