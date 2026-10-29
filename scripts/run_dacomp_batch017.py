from annotate_dacomp_batch017 import *
P={
21:[('missing_count', [('count(*)-count(distinct e.occurred_on)','count(*)-count(e.occurred_on)')]),('spine_days_count',[('count(*)-count(distinct e.occurred_on)','count(distinct d.day)-count(distinct e.occurred_on)')])],
22:[('source_id_projection',[('subscription_id as subscription_id','coalesce(cast(id as bigint), cast(subscription_id as bigint)) as subscription_id')]),('source_id_group',[('partition by subscription_id','partition by coalesce(cast(id as bigint), cast(subscription_id as bigint))')]),('deleted_filter',[('from raw.subscription_history','from raw.subscription_history\nwhere not coalesce(_fivetran_deleted,false)')])],
23:[('url_route',[("('https://facebook.com/' || p.id)","('https://facebook.com/' || coalesce(pg.id,p.page_id) || '/posts/' || p.id)")]),('followers_representation',[('coalesce(try_cast(pg.fan_count as bigint), 0)::bigint','coalesce(pg.fan_count, 0)')]),('impressions_default',[('coalesce(pm.impressions, 0)::bigint as impressions','0::bigint as impressions')])],
24:[('email_pattern',[(r"^[a-z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$",r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$')])],
25:[('user_phone_no_repair',[(r'''regexp_replace(regexp_replace(try_cast("from" as varchar), '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1')''','try_cast("from" as varchar)')]),('contact_phone_no_repair',[(r'''regexp_replace(regexp_replace(try_cast("to" as varchar), '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1')''','try_cast("to" as varchar)')])],
26:[('date_day_type',[('try_cast(date as timestamp) as date_day',"date_trunc('day', try_cast(date as timestamp)) as date_day")])],
27:[('account_keep_duplicates',[('    QUALIFY row_number() OVER (PARTITION BY account_code ORDER BY account_id) = 1','')])],
28:[],
29:[('date_prefix',[('try_cast("start_date" as DATE)','try_cast(substr(cast("start_date" as VARCHAR),1,10) as DATE)')]),('deleted_filter',[('where try_cast("id" as BIGINT) is not null','where try_cast("id" as BIGINT) is not null AND coalesce(try_cast(_fivetran_deleted as BOOLEAN),false)=false')])],
30:[('account_source',[('try_cast("id" AS VARCHAR) AS account_id','try_cast("account_id" AS VARCHAR) AS account_id')]),('created_null_allowed',[("try_cast(created_date AS timestamp) IS NOT NULL AND try_cast(created_date AS timestamp) <= current_timestamp AND try_cast(created_date AS timestamp) >= timestamp '2000-01-01 00:00:00'","(try_cast(created_date AS timestamp) IS NULL OR (try_cast(created_date AS timestamp) <= current_timestamp AND try_cast(created_date AS timestamp) >= timestamp '2000-01-01 00:00:00'))")])]
}
for col,typ in [('adjustment_amount','DOUBLE'),('amount_without_tax','BIGINT'),('amount_without_tax_home_currency','BIGINT'),('balance','DOUBLE'),('credit_balance_adjustment_amount','DOUBLE'),('credit_memo_amount','DOUBLE'),('exchange_rate','DOUBLE'),('exchange_rate_date','DATE'),('target_date','DATE')]:P[30].append((col+'_representation',[(f'try_cast("{col}" AS {typ}) AS {col}',f'"{col}" AS {col}')]))
CLOCK={23:'2025-10-17 12:00:00+08',25:'2025-10-12 12:00:00+08',28:'2024-01-30 12:00:00+08',30:'2025-10-13 12:00:00+08'}
if __name__=='__main__':
 for n in map(int,sys.argv[1:]):
  clock=CLOCK.get(n);patches=P[n]
  if clock:patches=[(label,[(re.sub(r'\bcurrent_timestamp\b',f"TIMESTAMPTZ '{clock}'",old,flags=re.I),re.sub(r'\bcurrent_timestamp\b',f"TIMESTAMPTZ '{clock}'",new,flags=re.I)) for old,new in edits]) for label,edits in patches]
  rerun(n,patches,clock=clock)
