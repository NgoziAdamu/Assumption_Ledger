"""Additional independent interventions revealed by the baseline diagnostics."""
from annotate_dacomp_batch024 import *
import annotate_dacomp_batch024 as engine
engine.WORK=ROOT/'data/024_supplement_work';engine.WORK.mkdir(exist_ok=True)
inv=json.loads((REC/'024_package_inventory.json').read_text());plans=json.loads((REC/'024_patch_plan.json').read_text());extra=[]
def run(t,patches):
 r=next(r for r in inv if r['table']==t);pkg=json.loads((ROOT/r['full_json']).read_text());b=pkg['differences'];before=REC/f"024_reruns_{r['task']}_{t}.json";hold=before.read_bytes();clock=next(p.get('clock') for p in plans if p['table']==t) or (b.get('candidate_date') or '2025-10-13')+' 00:00:00+00'
 try:
  engine.rerun(int(r['task'][-3:]),[(x['label'],x['edits']) for x in patches],clock=clock,pkg=pkg)
  (REC/f"024_supplement_reruns_{r['task']}_{t}.json").write_bytes(before.read_bytes())
 finally:before.write_bytes(hold)
 extra.append(dict(task=r['task'],table=t,patches=patches));save(REC/'024_supplement_patch_plan.json',extra)
def patch(label,old,new,cat,why):return dict(label=label,edits=[[old,new]],category=cat,reason=why,P=None)
def doc(t):return json.loads((ROOT/next(r['full_json'] for r in inv if r['table']==t)).read_text())
t='stg_social_media__twitter_organic_tweets';run(t,[patch('date_projection','cast(o.date as date) as date','o.date as date','O','契约date为DATE，gold保留带时刻TIMESTAMP，评测键不做容差。')])
t='stg_social_media__twitter_user_history';d=doc(t);a=d['agent_final_SQL'][0]['text'];ps=[patch('id_projection','try_cast(id as bigint) as id','id as id','O','契约id BIGINT，gold保留非数值VARCHAR。'),patch('id_filter','where id is not null','where true','O','转换后NULL键按契约删行，gold留存非数值键。')]
for col,raw in [('followers_count','followers_count'),('following_count','friends_count'),('listed_count','listed_count'),('favourites_count','favourites_count'),('statuses_count','statuses_count')]:ps.append(patch('type_'+col,f'try_cast({raw} as bigint) as {col}',f'{raw} as {col}','O','契约BIGINT，gold保留DOUBLE。'))
run(t,ps)
t='stg_tiktok_ads__ad_group_history';a=doc(t)['agent_final_SQL'][0]['text'];old=next(l.strip().rstrip(',') for l in a.splitlines() if l.rstrip().endswith(' as age_groups,'));run(t,[patch('age_groups_parser',old,"split_part(record, ',', 64) as age_groups",'O','agent正确保留quoted array完整字段，gold简单按逗号分割截断；以header和CSV诊断为证。')])
t='stg_xero__journal';a=doc(t)['agent_final_SQL'][0]['text'];g=doc(t)['gold_SQL_仅供定位差异'][0]['text'];old=a[a.index('    CASE'):a.index(' AS journal_number')];new="    CASE WHEN journal_number LIKE 'INVALID%' OR journal_number LIKE 'BAD%' THEN NULL ELSE "+old.strip()+" END";run(t,[patch('invalid_prefix',old,new,'O','契约要求移除字母/特殊字符后保留有效数字，gold额外将INVALID/BAD前缀置NULL。')])
t='twitter_ads__promoted_tweet_report';run(t,[patch('campaign_projection','a.account_name, li.campaign_id','a.account_name, c.campaign_id','C','契约指定campaign id来自campaigns，20行缺匹配维度时原外键不等于NULL。'),patch('line_item_projection','c.campaign_name, pt.line_item_id','c.campaign_name, li.line_item_id','C','契约line item id来自匹配维度；独立检查。')])
t='stg_zuora__invoice_payment';a=doc(t)['agent_final_SQL'][0]['text'];run(t,[patch('refund_type','try_cast("refund_amount" AS BOOLEAN) AS refund_amount','refund_amount AS refund_amount','O','契约BOOLEAN，gold BIGINT，单独诊断。')])
