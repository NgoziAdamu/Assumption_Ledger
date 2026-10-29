from annotate_dacomp_batch020 import *
from plan_dacomp_batch020 import pkg,rows,oldexpr,goldexpr

def augment(i,patches):
 d=pkg(i);n=int(rows[i]['task'][-3:]);path=REC/f'020_reruns_impl-{n:03}_{rows[i]["table"]}.json';before=json.loads(path.read_text());clock=(d['differences'].get('candidate_date') or '2025-10-12')+' 12:00:00+00'
 rerun(n,patches,clock=clock,pkg=d);after=json.loads(path.read_text());before['additional_baseline_checks']=before.get('additional_baseline_checks',[])+[after['runs'][0]];before['runs']+=after['runs'][1:];save(path,before)
if __name__=='__main__':
 for i,cols in [(13,['ad_group_id']),(30,['advertiser_id','spend','conversions','calculated_cost_per_click','cost_per_thousand_impressions','cost_per_thousand_reached']),(35,['country'])]:
  d=pkg(i);ps=[(c+'_gold_diagnostic' if i==13 else c,[(oldexpr(d,c),goldexpr(d,c)+' AS '+c)]) for c in cols]
  if i==13:ps.append(('invalid_id_contract_delete', [('SELECT * FROM cleaned',"SELECT * FROM cleaned WHERE ad_group_id IS NOT NULL AND TRIM(ad_group_id) != '' AND regexp_matches(ad_group_id, '^[A-Za-z0-9_-]{1,128}$')")]))
  augment(i,ps)
 d=pkg(42);old='CASE WHEN store_listing_conversion_rate BETWEEN 0 AND 1 THEN store_listing_conversion_rate ELSE NULL END AS store_listing_conversion_rate';ratio=goldexpr(d,'store_listing_conversion_rate')
 augment(42,[('invalid_rate_policy_diagnostic',[(old,f'CASE WHEN store_listing_conversion_rate NOT BETWEEN 0 AND 1 THEN {ratio} ELSE store_listing_conversion_rate END AS store_listing_conversion_rate')]),('valid_rate_formula_choice',[(old,f'CASE WHEN store_listing_conversion_rate BETWEEN 0 AND 1 THEN {ratio} ELSE NULL END AS store_listing_conversion_rate')])])
