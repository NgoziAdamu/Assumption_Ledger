from rerun_dacomp_extra021 import *
from review_dacomp_batch021 import pkg
p=pkg(8);patches=[]
for col,source in [('avg_7d_crashes','crashes'),('avg_7d_anrs','anrs')]:patches.append((col,[(f'CAST(NULL AS DOUBLE) AS {col}',f'CAST(round(AVG({source}) OVER(PARTITION BY package_name ORDER BY date_day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),2) AS DOUBLE) AS {col}')]))
rerun(9,patches,clock='2025-10-12 00:00:00+00',pkg=p)
# Correct runtime-only diagnostic for 039, preserving all previous experiments.
p=pkg(39);rerun(11,[('gold_sql_same_clock',[(p['agent_final_SQL'][0]['text'],p['gold_SQL_仅供定位差异'][0]['text'])])],clock='2025-10-13 00:00:00+00',pkg=p)
