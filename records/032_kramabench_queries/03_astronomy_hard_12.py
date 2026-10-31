from common import *
from datetime import datetime,timedelta
from pyproj import Transformer, network
network.set_network_enabled(False)
base=DATA/'astronomy/input/swarm/POD'
files=sorted(base.rglob('*201909*.sp3'))
start=datetime(2019,9,2);end=datetime(2019,9,29,23,59,59)
positions=[];times=[];counts=[];time_headers=set()
for p in files:
    epoch=None;all_points=selected=0
    for line in p.read_text().splitlines():
        if line.startswith('%c'):time_headers.add(line)
        if line.startswith('*'):
            v=line[1:].split()
            epoch=datetime(*map(int,v[:5]))+timedelta(seconds=float(v[5]))
        elif line.startswith('PL47'):
            assert epoch is not None
            all_points+=1
            if start<=epoch<=end:
                positions.append([float(line[4:18]),float(line[18:32]),float(line[32:46])])
                times.append(epoch);selected+=1
    counts.append({'file':str(p.relative_to(ROOT)),'PL47_points':all_points,'selected':selected})
print('SP3 time-system headers (timestamp comparison uses epoch fields as written, no time-system conversion):')
print('\n'.join(sorted(time_headers)))
print(pd.DataFrame(counts).to_string(index=False))
xyz=np.asarray(positions)*1000.0
transform=Transformer.from_crs('EPSG:4978','EPSG:4979',always_xy=True)
lon,lat,height_m=transform.transform(xyz[:,0],xyz[:,1],xyz[:,2])
h=np.asarray(height_m)/1000.0
assert np.isfinite(h).all()
R=6371.0;g=9.80665
value=float(np.mean(g*(R+h)*1000));target=66822738.84
RESULT=finish({'files':len(files),'points':len(positions),'unique_timestamps':len(set(times)),
 'first_timestamp':min(times).isoformat(' '),'last_timestamp':max(times).isoformat(' '),
 'geodetic_height_km_min':float(h.min()),'geodetic_height_km_max':float(h.max()),'geodetic_height_km_mean':float(h.mean()),
 'WGS84_transform':'EPSG:4978 -> EPSG:4979, input/output metres; h divided by 1000',
 'mean_g_R_plus_h_1000':value,'rounded_2':round(value,2),'comparison':target,'difference_computed_minus_comparison':value-target,
 'rounded_2_difference':round(value,2)-target})
