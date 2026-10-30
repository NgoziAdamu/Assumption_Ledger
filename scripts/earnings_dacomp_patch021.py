from rerun_dacomp_extra021 import *
from review_dacomp_batch021 import pkg
p=pkg(16);s=p['agent_final_SQL'][0]['text'];old="CASE WHEN lower(trim(transaction_type)) = 'charge' THEN 'Charge' WHEN lower(trim(transaction_type)) = 'refund' THEN 'Refund' WHEN lower(trim(transaction_type)) = 'other' THEN 'Other' ELSE NULL END"
rerun(9,[('contract_other_default',[(old,"COALESCE("+old+",'Other')")])],clock='2025-10-12 00:00:00+00',pkg=p)
