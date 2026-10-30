import annotate_dacomp_batch022 as h
from pathlib import Path
import json
oldsave=h.save
def save(p,x):
 if p.name.startswith('022_reruns'):p=p.with_name(p.name.replace('022_reruns','022_calibration_supplement_reruns'))
 oldsave(p,x)
h.save=save;h.WORK=h.ROOT/'data/022_calibration_supplement';h.WORK.mkdir(exist_ok=True)
h.rerun(5,[('spend',[('CAST(cost_micros / 1000000.0 AS DECIMAL(15,2))','cost_micros / 1000000.0')]),('conversions',[('CAST(conversions AS DECIMAL(10,2))','CAST(conversions AS DOUBLE)')]),('conversion_value',[('CAST(conversions_value AS DECIMAL(15,2))','CAST(conversions_value AS DOUBLE)')])])
