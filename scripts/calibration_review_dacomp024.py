from annotate_dacomp_batch024 import *
import annotate_dacomp_batch024 as engine
engine.WORK=ROOT/'data/024_calibration_review';engine.WORK.mkdir(exist_ok=True)
pkg=package(16);a=pkg['agent_final_SQL'][0]['text'];old='count(DISTINCT r.organization_role_id) unique_organization_roles';new="(SELECT count(DISTINCT orw.role_id) FROM staging.stg_workday__worker_position_organization w LEFT JOIN staging.stg_workday__organization_role_worker orw ON w.worker_id=orw.organization_worker_code AND w.source_relation=orw.source_relation WHERE w.organization_id=ow.organization_id AND w.source_relation='workday') unique_organization_roles"
patches=[('role_count_expression',[(old,new)])]
for word,col in [('Manager','management_role_employees'),('Director','director_role_employees'),('Lead','lead_role_employees')]:
 old_role=f"count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%{word}%') {col}"
 new_role=f"(SELECT count(DISTINCT w.worker_id) FILTER(WHERE rr.organization_role_code ILIKE '%{word}%') FROM staging.stg_workday__worker_position_organization w LEFT JOIN staging.stg_workday__organization_role_worker orw ON w.worker_id=orw.organization_worker_code AND w.source_relation=orw.source_relation LEFT JOIN staging.stg_workday__organization_role rr ON orw.role_id=rr.organization_role_id AND orw.source_relation=rr.source_relation AND w.organization_id=rr.organization_id WHERE w.organization_id=ow.organization_id AND w.source_relation='workday') {col}"
 patches.append(('role_'+col,[(old_role,new_role)]))
patches.append(('role_input_relation', [('FROM staging.stg_workday__organization_role_worker ow', "FROM (SELECT w.organization_id,orw.organization_worker_code,orw.role_id FROM staging.stg_workday__worker_position_organization w LEFT JOIN staging.stg_workday__organization_role_worker orw ON w.worker_id=orw.organization_worker_code AND w.source_relation=orw.source_relation) ow")]))
p=REC/'024_reruns_impl-016_workday__organization_overview.json';hold=p.read_bytes();d=json.loads(hold);clock=d['clock_control'][0]['replacement'].split("'")[1]
try:
 engine.rerun(16,patches,clock=clock,pkg=pkg)
 (REC/'024_supplement_reruns_impl-016_workday__organization_overview.json').write_bytes(p.read_bytes())
finally:p.write_bytes(hold)
ps=json.loads((REC/'024_supplement_patch_plan.json').read_text())
ps=[p for p in ps if p['table']!='workday__organization_overview']
ps.append(dict(task='impl-016',table='workday__organization_overview',patches=[dict(label=label,edits=edits,category='C',reason=('仅替换roles的FROM关系源为worker assignment与role_worker的关系，其余聚合表达式和role连接保持不动。' if label=='role_input_relation' else '仅替换一个角色统计表达式，恢复契约通过worker assignment的角色计数，其余三个统计和连接不动。'),P=None) for label,edits in patches]))
save(REC/'024_supplement_patch_plan.json',ps)
