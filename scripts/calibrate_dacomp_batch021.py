"""Independent calibration from 012/013 originals only; no prior annotations."""
from annotate_dacomp_batch021 import *
p=package(13)
expr="CASE " + ' '.join(f"WHEN total_revenue >= (SELECT quantile_cont(total_revenue,{v}) FROM metrics) THEN {k}" for v,k in [(0.8,5),(0.6,4),(0.4,3),(0.2,2)])+" ELSE 1 END"
rerun(13,[('percentiles',[('ntile(5) OVER(ORDER BY total_revenue)',expr)])],clock='2025-10-14 12:00:00+00',pkg=p)
p=package(30);s=p['agent_final_SQL'][0]['text']
old="try_cast(created_date AS timestamp) IS NOT NULL AND try_cast(created_date AS timestamp) <= current_timestamp AND try_cast(created_date AS timestamp) >= timestamp '2000-01-01 00:00:00'"
new="(try_cast(created_date AS timestamp) IS NULL OR (try_cast(created_date AS timestamp) <= current_timestamp AND try_cast(created_date AS timestamp) >= timestamp '2000-01-01 00:00:00'))"
patches=[('keep_null_dates',[(old,new)]),('account_mapping',[('try_cast("id" AS VARCHAR) AS account_id','try_cast("account_id" AS VARCHAR) AS account_id')])]
for col in ['adjustment_amount','amount_without_tax','amount_without_tax_home_currency','balance','credit_balance_adjustment_amount','credit_memo_amount','exchange_rate','exchange_rate_date','target_date']:
 m=re.search(r'try_cast\("'+col+r'" AS \w+\)',s)
 patches.append((col,[(m[0],'"'+col+'"')]))
rerun(30,patches,clock='2025-10-12 12:00:00+00',pkg=p)
