from rerun_dacomp_supplement023 import *
inv=json.loads((REC/'023_package_inventory.json').read_text());plans=[]
def get(t):return json.loads((ROOT/next(r['full_json'] for r in inv if r['table']==t)).read_text())
def add(t,label,old,new,cat,why,clock=None):
 p=get(t);s=p['agent_final_SQL'][0]['text'];assert s.count(old)==1,(t,label,s.count(old),old)
 x=next((x for x in plans if x['table']==t),None)
 if not x:x=dict(task=p['basic_information']['task'],table=t,clock=clock or ((p['differences'].get('candidate_date') or '2025-10-24')+' 00:00:00+00' if re.search('current_date|current_timestamp',s,re.I) else None),patches=[]);plans.append(x)
 x['patches'].append(dict(label=label,edits=[[old,new]],category=cat,reason=why))
t='workday__employee_overview';s=get(t)['agent_final_SQL'][0]['text'];old='LEFT JOIN comp ON b.position_id=comp.position_id AND b.source_relation=comp.source_relation'
new='LEFT JOIN (SELECT eb.worker_id,eb.position_id,eb.source_relation,c.compensation_grade_id,c.is_work_shift_required,c.is_union_eligible FROM intermediate.int_workday__worker_employee_enhanced eb LEFT JOIN comp c ON eb.position_id=c.position_id AND eb.source_relation=c.source_relation) comp ON b.worker_id=comp.worker_id AND b.position_id=comp.position_id AND b.source_relation=comp.source_relation'
add(t,'comp_ebe_join',old,new,'C','恢复契约规定 ebe 派生 compensation 后按 worker/source/position 回接的重复度；仅修改该 JOIN 一处。')
t='workday__position_overview';s=get(t)['agent_final_SQL'][0]['text'];old=next(l for l in s.splitlines() if l.strip().startswith('SELECT po.organization_id,pr.job_profile_id,count'))
new=" SELECT o.organization_id,pr.job_profile_id,count(*) similar_positions_in_department FROM base b LEFT JOIN po ON b.position_id=po.position_id AND b.source_relation=po.source_relation AND po.rn=1 LEFT JOIN staging.stg_workday__organization o ON po.organization_id=o.organization_id AND po.source_relation=o.source_relation LEFT JOIN profiles pr ON b.position_id=pr.position_id AND b.source_relation=pr.source_relation GROUP BY o.organization_id,pr.job_profile_id"
add(t,'similar_group',old,new,'C','相似岗位按实际组织维度分组；孤儿组织关系归 NULL 组。')
t='greenhouse__job_enhanced';add(t,'ratio_zero_vs_null','count_total_interviews * 100.0 / count_total_applications','nullif(count_total_interviews,0) * 100.0 / count_total_applications','O','契约先将 count 默认0；gold 用未补零的原始聚合生成 NULL 比率。')
t='stg_salesforce__contact_history';s=get(t)['agent_final_SQL'][0]['text'];old=re.search(r'md5\(.*\) as history_unique_key',s).group().rsplit(' as ',1)[0]
add(t,'history_key_clock',old,"concat(id, '_', cast(current_timestamp as timestamp)::varchar)",'A','history_unique_key 算法未规定；在 gold 生成时刻共同固定时间后单改键表达式。',clock='2025-10-24 15:24:19.642344+08:00')
t='stg_salesforce__user';add(t,'email_not_null','and email is not null','and TRUE','O','契约 email not_null；gold 保留空 email。');add(t,'email_length','and length(lower(trim(email))) <= 255','and TRUE','O','契约明确长邮箱删除，gold 保留。')
t='stg_apple_store__app_session_daily';s=get(t)['agent_final_SQL'][0]['text'];old=next(l.strip().rstrip(',') for l in s.splitlines() if ' AS app_version' in l)
add(t,'semver_regex',old,"CASE WHEN regexp_matches(cast(r.app_version AS VARCHAR), '^[0-9]+\\\\.[0-9]+\\\\.[0-9]+$') OR regexp_matches(cast(r.app_version AS VARCHAR), '^[0-9]+$') THEN cast(r.app_version AS VARCHAR) ELSE NULL END AS app_version",'O','gold 使用双反斜杠而不接受普通三段数字版本；契约 YAML 解析后接受。')
for label,old in [('date_filter_null','WHERE try_cast(r.date AS DATE) IS NOT NULL'),('date_filter_upper','AND try_cast(r.date AS DATE) <= CURRENT_DATE'),('date_filter_lower',"AND try_cast(r.date AS DATE) >= DATE '2020-01-01'")]:
 new=old.replace('try_cast(r.date AS DATE)',"cast(coalesce(try_strptime(r.date,'%Y-%m-%d'),try_strptime(r.date,'%d-%m-%Y'),try_strptime(r.date,'%b %d, %Y')) as date)")
 add(t,label,old,new,'A','日期输入格式支持范围未明确；每处过滤表达式分别修改。')
t='int_intercom__conversation_part_aggregates';s=get(t)['agent_final_SQL'][0]['text'];old='from rollup r join staging.stg_intercom__conversation_history c on r.conversation_id=c.conversation_id'
new='from (SELECT c0.conversation_id,coalesce(r0.count_total_parts,0) count_total_parts,r0.first_contact_reply_at,r0.first_assignment_at,r0.first_admin_response_at,r0.first_reopen_at,r0.last_assignment_at,r0.last_contact_reply_at,r0.last_admin_response_at,r0.last_reopen_at,coalesce(r0.count_assignments,0) count_assignments,coalesce(r0.count_reopens,0) count_reopens FROM staging.stg_intercom__conversation_history c0 LEFT JOIN rollup r0 ON c0.conversation_id=r0.conversation_id) r join staging.stg_intercom__conversation_history c on r.conversation_id=c.conversation_id'
add(t,'conversation_coverage',old,new,'U','P=每个 conversation 都有匹配的 part；由 part 驱动的内连接丢失无 part 对话。可见库5726个对话无 part；CS 全部无匹配。')
t='stg_intercom__contact_history';add(t,'phone_gold_regex',"regexp_matches(normalized_phone, '^\\+[1-9][0-9]{1,14}$')",r"regexp_matches(normalized_phone, '^\\+[1-9]\\d{1,14}$')",'O','契约显式 E.164 允许的1079条，gold 双反斜杠表达式全部拒绝。')
t='stg_intercom__conversation_contact_history'
add(t,'contact_column','try_cast(conversation_id as varchar) as contact_id','contact_id as contact_id','O','原始列错位，agent 输出 contact VARCHAR 与数据关系一致；gold 按原名透传。')
add(t,'conversation_column','try_cast(contact_id as bigint) as conversation_id','conversation_id as conversation_id','O','agent 遵守 conversation_id BIGINT；gold 保留无法转成 BIGINT 的原始字符串。')
t='stg_klaviyo__person';s=get(t)['agent_final_SQL'][0]['text'];old=next(l.strip().rstrip(',') for l in s.splitlines() if ' full_name' in l)
add(t,'full_name_null',old,"first_name || ' ' || last_name full_name",'A','只缺一侧姓名时拼接剩余姓名还是 NULL，契约未明确。')
add(t,'phone_normalization',"case when phone_digits='' then null else '+' || phone_digits end", "case when phone_number is null then null when left(regexp_replace(phone_number, '[^0-9]+', ''),1)='0' then '+' || ltrim(regexp_replace(phone_number, '[^0-9]+', ''),'0') else '+' || regexp_replace(phone_number, '[^0-9]+', '') end",'O','契约要求移除非数字并加+；gold还移除前导0且regexp_replace未指定全局。仅改一个phone CASE，检验其是否独立改善。')
save(REC/'023_supplement_patch_plan.json',plans)
for p in plans:
 if len(sys.argv)>1 and p['task'] not in sys.argv[1:]:continue
 if (REC/f"023_supplement_reruns_{p['task']}_{p['table']}.json").exists():continue
 rerun(int(p['task'][-3:]),[(x['label'],x['edits']) for x in p['patches']],clock=p['clock'],pkg=get(p['table']))
