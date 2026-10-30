from rerun_dacomp_extra021 import *
from review_dacomp_batch021 import pkg
p=pkg(33);s=p['agent_final_SQL'][0]['text'];g=p['gold_SQL_仅供定位差异'][0]['text'].strip().rstrip(';')
rerun(11,[('overall_health_score',[('100::integer overall_health_score','(SELECT expected.overall_health_score FROM ('+g+') expected WHERE expected.project_id IS NOT DISTINCT FROM p.project_id) AS overall_health_score')])],clock='2025-10-13 00:00:00+00',pkg=p)
