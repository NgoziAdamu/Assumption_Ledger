from annotate_dacomp_batch016 import *
def main():
 n=5;case=json.loads((REC/'013_cases.json').read_text())[n-1]
 q="""SELECT count(*) matched_pairs,count(*) FILTER(WHERE cast(h.campaign_id AS VARCHAR)=cast(s.campaign_id AS VARCHAR)) direct_parent_matches,count(*) FILTER(WHERE cast(h.campaign_id AS VARCHAR)=cast(s.campaign_base_campaign AS VARCHAR)) base_parent_matches FROM raw.ad_group_stats_data s JOIN raw.ad_group_history_data h ON cast(s.base_ad_group AS VARCHAR)=cast(h.id AS VARCHAR)"""
 with duckdb.connect(case['agent_database'],read_only=True) as c:
  r=c.execute(q);x={'id':'V2','kind':'核实查询','database':case['agent_database'],'sql':q,'columns':[d[0] for d in r.description],'rows':r.fetchall()}
 p=REC/'016_queries_impl-005.json';qs=json.loads(p.read_text());qs=[a for a in qs if a['id']!='V2'];qs.append(x);save(p,qs);print(x,flush=True)
 old=json.loads((REC/'014_reruns_impl-008.json').read_text())
 patches=[(r['label'],[(e['old'],e['new']) for e in r['edits']]) for r in old['runs'] if r['edits']]
 patches.append(('section_tie_order',[("STRING_AGG(project_name || ' (' || section_name || ')', ', ' ORDER BY project_name)","STRING_AGG(project_name || ' (' || section_name || ')', ', ' ORDER BY project_name,section_name)")]))
 rerun(8,patches)
if __name__=='__main__':main()
