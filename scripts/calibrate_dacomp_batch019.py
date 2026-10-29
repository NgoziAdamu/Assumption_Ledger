"""Blind calibration: imports harness code only, no 014–018 annotation records."""
from annotate_dacomp_batch019 import *
for n,patches in [(8,[('project_source',[('pt.task_id, p.project_id,','pt.task_id, pt.project_id,')])]),(21,[('count_events',[('count(*)-count(distinct e.occurred_on)','count(*)-count(e.occurred_on)')])])]:
 rerun(n,patches)
