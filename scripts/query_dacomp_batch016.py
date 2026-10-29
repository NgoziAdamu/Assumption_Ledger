from annotate_dacomp_batch016 import *
Q={
5:["SELECT count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.campaign_history_data h WHERE h.id=cast(s.campaign_id as varchar))) direct_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.campaign_history_data h WHERE h.id=cast(s.campaign_base_campaign as varchar))) base_matches FROM raw.ad_group_stats_data s"],
7:["SELECT count(*) n,count(*) FILTER(WHERE marketing_opt_in_duration IS DISTINCT FROM subscription_offer_duration) different_duration,count(*) FILTER(WHERE marketing_opt_in_duration IS NULL) marketing_null FROM raw.sales_subscription_event_summary"],
11:["SELECT count(*) n,count(*) FILTER(WHERE original_estimate IS DISTINCT FROM _original_estimate) original_diff,count(*) FILTER(WHERE remaining_estimate IS DISTINCT FROM _remaining_estimate) remaining_diff,count(*) FILTER(WHERE time_spent IS DISTINCT FROM _time_spent) spent_diff,min(original_estimate),min(_original_estimate) FROM raw.issue"],
12:["SELECT count(*) n,count(*) FILTER(WHERE first_name IS DISTINCT FROM trim(first_name)) first_whitespace,count(*) FILTER(WHERE last_name IS DISTINCT FROM trim(last_name)) last_whitespace,count(*)-count(distinct id) duplicate_excess FROM raw.marketo_lead"],
13:[],
14:["SELECT count(*) n,count(try_cast(creation_date as timestamp)) cast_nonnull,count(try_strptime(cast(creation_date as varchar),'%Y-%m-%d %H:%M:%S.%f %z')) strptime_nonnull FROM raw.survey_version"],
15:["SELECT count(*) n,count(sales_tax_code_id) sales_present,count(purchase_tax_code_id) purchase_present,count(*) FILTER(WHERE cast(sales_tax_code_id as varchar) IS DISTINCT FROM cast(purchase_tax_code_id as varchar)) unequal FROM raw.item_data"],
16:[],
17:["SELECT candidate_id,tag_id,count(*) n FROM raw.candidate_tag GROUP BY 1,2 HAVING count(*)>1"],
18:["SELECT count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.opportunity o WHERE o.id=i.opportunity_id)) opportunity_source_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.opportunity o WHERE o.id=i.id)) generic_id_matches,count(*) FILTER(WHERE is_deleted) deleted FROM raw.opportunity_line_item i"],
19:[],
20:["SELECT count(*) n,count(part_type) part_type_present,count(subject) subject_present,count(*) FILTER(WHERE coalesce(try_cast(_fivetran_active as BOOLEAN),true)) active_rows,count(*) FILTER(WHERE try_cast(conversation_id AS BIGINT) IS NOT NULL) numeric_conversation FROM raw.conversation_part_history_data"]}
def main():
 for n,qs in Q.items():
  case=json.loads((REC/'013_cases.json').read_text())[n-1];out=[]
  with duckdb.connect(case['agent_database'],read_only=True) as c:
   for i,q in enumerate(qs,1):
    x={'id':f'V{i}','kind':'核实查询','database':case['agent_database'],'sql':q}
    try:r=c.execute(q);x.update(columns=[d[0] for d in r.description],rows=r.fetchall())
    except Exception as e:x['error']=str(e)
    out.append(x)
  save(REC/f'016_queries_impl-{n:03}.json',out);print(n,out,flush=True)
if __name__=='__main__':main()
