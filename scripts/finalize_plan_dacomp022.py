from review_dacomp_batch022 import *
p=REC/'022_patch_plan.json';d=json.loads(p.read_text())
for x in d[9]['patches']:
 if x['label']=='table_label':
  expr="CASE table_name WHEN 'Transactions' THEN 'staging.stg_netsuite2__transactions' WHEN 'Transaction lines' THEN 'staging.stg_netsuite2__transaction_lines' ELSE 'staging.stg_netsuite2__customers' END"
  x['edits']=[['table_name::VARCHAR AS quality_grade',expr+'::VARCHAR AS quality_grade'],['md5(table_name || cast(current_timestamp AS VARCHAR))','md5(('+expr+') || cast(current_timestamp AS VARCHAR))']]
  x['reason']='契约未固定table_name字符串；agent简写、gold全限定名，使3个Table Statistics键及标签不同。'
for x in d[14]['patches']:
 if x['label']=='second_join':x['edits'][0][1]='FROM enriched e LEFT JOIN (SELECT customer_id AS b_id FROM behavior) b ON e.customer_id=b.b_id)'
for x in d[11]['patches']:x['category']='A';x['reason']='subsidiary_id契约只说明关联交易的subsidiary标识，未定驱动外键或维表匹配键；维表对应缺失，gold NULL、agent保留外键。'
for x in d[3]['patches']:
 if x['label']=='recommendation_wording':x['edits']=[["'Focus on improving email deliverability'","'Focus on deliverability improvement'"]]
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
