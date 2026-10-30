from review_dacomp_batch022 import *
import re
plan=json.loads((REC/'022_patch_plan.json').read_text())
def add(i,label,old,new,cat,reason):
 assert pkg(i)['agent_final_SQL'][0]['text'].count(old)==1,(i,label,old)
 plan[i]['patches'].append(dict(label=label,edits=[[old,new]],category=cat,reason=reason))
def multi(i,label,edits,cat,reason):
 for old,new in edits:assert pkg(i)['agent_final_SQL'][0]['text'].count(old)==1,(i,label,old)
 plan[i]['patches'].append(dict(label=label,edits=edits,category=cat,reason=reason))
s=pkg(3)['agent_final_SQL'][0]['text'];old=re.search(r'CAST\(ROUND\(.*? AS INTEGER\) AS overall_health_score',s)[0]
new="CAST(ROUND((CASE WHEN overall_delivery_rate_pct>=95 THEN 30 WHEN overall_delivery_rate_pct>=90 THEN 25 WHEN overall_delivery_rate_pct>=85 THEN 20 WHEN overall_delivery_rate_pct>=80 THEN 15 ELSE 10 END)+(CASE WHEN engaged_leads_pct>=40 THEN 30 WHEN engaged_leads_pct>=25 THEN 25 WHEN engaged_leads_pct>=15 THEN 20 WHEN engaged_leads_pct>=5 THEN 15 ELSE 10 END)+(CASE WHEN healthy_campaigns_pct>=80 THEN 25 WHEN healthy_campaigns_pct>=60 THEN 20 WHEN healthy_campaigns_pct>=40 THEN 15 ELSE 10 END)+(CASE WHEN delivery_stability='Stable' THEN 15 WHEN delivery_stability='Moderate Variance' THEN 10 ELSE 5 END),2) AS INTEGER) AS overall_health_score"
add(3,'score_weights',old,new,'A','契约只说四项阈值加权，未给分值；agent与gold不同权重。')
add(3,'recommendation_wording',"'Launch re-engagement campaigns for at-risk leads'","'Implement lead re-engagement campaigns'",'A','契约只用自然语言re-engage leads说明，没有指定完整字面标签。')
# Missing CTA branch only; keep main projection byte-identical.
cta=""" UNION ALL SELECT md5(transaction_line_id||'_'||transaction_id||'_'||reporting_accounting_period_id||'_Cumulative Translation Adjustment_0'),transaction_id,transaction_line_id,subsidiary_id,subsidiary_full_name,subsidiary_name,subsidiary_currency_symbol,reporting_accounting_period_id,ending_at,period_name,is_adjustment,is_closed,'Equity','Cumulative Translation Adjustment','Cumulative Translation Adjustment','Cumulative Translation Adjustment','cumulative_translation_adjustment',NULL,(SELECT account_number FROM intermediate.int_netsuite2__accounts WHERE lower(type_name)='cumultransadj' LIMIT 1),FALSE,FALSE,CASE WHEN lower(general_rate_type) IN ('historical','average') THEN converted_amount_using_transaction_accounting_period ELSE converted_amount_using_reporting_month END,unconverted_amount,16 FROM presented"""
add(7,'cta_branch','FROM presented','FROM presented'+cta,'C','契约显式要求每行UNION ALL第二条CTA，agent完全遗漏。')
add(7,'key_null',"coalesce(CASE WHEN is_balancesheet THEN account_id END,'')","coalesce(CASE WHEN is_balancesheet THEN account_id END,'0')",'A','契约只说coalesced account_id，没有规定空值哨兵；gold用0、agent空串。')
add(7,'account_type_id',"lower(replace(out_type,' ', '_'))", "CASE WHEN NOT is_balancesheet THEN lower(replace(out_type,' ', '_')) WHEN lower(type_name)='retearnings' THEN 'retained_earnings' WHEN lower(type_name) IN ('cta-e','cumultransadj') THEN 'cumulative_translation_adjustment' ELSE type_name END",'C','契约正常账户type_id原样取type_name，agent全部小写。')
old="CASE WHEN NOT is_balancesheet OR is_leftside IS FALSE THEN -coalesce(converted_amount_using_transaction_accounting_period, converted_amount_using_reporting_month) ELSE coalesce(converted_amount_using_transaction_accounting_period, converted_amount_using_reporting_month) END AS converted_amount"
new="CASE WHEN NOT is_balancesheet OR is_leftside IS FALSE THEN -CASE WHEN lower(general_rate_type) IN ('historical','average') THEN converted_amount_using_transaction_accounting_period ELSE converted_amount_using_reporting_month END WHEN is_leftside THEN CASE WHEN lower(general_rate_type) IN ('historical','average') THEN converted_amount_using_transaction_accounting_period ELSE converted_amount_using_reporting_month END ELSE 0 END AS converted_amount"
add(7,'rate_selection',old,new,'C','契约按rate_type选换算金额，agent优先coalesce交易期间。')
# Quality accuracy computation: restore only constant accuracy placeholder, same other report code.
g=pkg(9)['gold_SQL_仅供定位差异'][0]['text'];section=g[g.index('business_rule_validations as (')+len('business_rule_validations as ('):g.index('),',g.index('business_rule_validations as ('))] if False else ''
start=g.index('business_rule_validations as (');end=g.index('data_completeness_analysis as (');rules=g[start+len('business_rule_validations as ('):end].strip().removesuffix(',').strip().removesuffix(')').strip()
# Gold CTE refers directly to staging; preserve as diagnostic arithmetic source, no gold table read in patch.
add(9,'accuracy_rules','100.0 AS accuracy_score','(SELECT avg(compliance_percentage) FROM ('+rules+') rules) AS accuracy_score','D','agent用100常数占位四条规则合规率，并在报告披露未完整验证。')
add(9,'customer_counts',"ELSE 'Date Range: ' || null_dates || ' to ' || null_entities", "ELSE 'Date Range: ' || (SELECT count(DISTINCT company_name) FROM staging.stg_netsuite2__customers) || ' to ' || (SELECT count(DISTINCT email_address) FROM staging.stg_netsuite2__customers)",'C','契约客户Date Range是distinct names/emails，不是缺失数。')
# Label spelling affects the timestamp hash key as well.
add(9,'table_label',"'Transaction lines' AS table_name", "'transaction_lines' AS table_name",'A','核对gold表名大小写与空格；契约没固定table_name字符串。')
s=pkg(12)['agent_final_SQL'][0]['text'];old=re.search(r"coalesce\(sum\(abs\(t.converted_amount\)\) FILTER\(WHERE t.account_type_name='Bank'\),0\)/nullif\(sum\(abs\(t.converted_amount\)\) FILTER\(WHERE t.account_type_name IN \('AcctPay','Accounts Payable'\)\),0\)",s)[0]
add(12,'payment_zero',old,'coalesce('+old+',0)','C','契约分母无应付时payment_ratio=0，agent返回NULL。')
add(12,'vendor_activity',"'Inactive' vendor_activity_status", "CASE WHEN date_diff('day',last_transaction_date,current_date)<=30 THEN 'Active' WHEN date_diff('day',last_transaction_date,current_date)<=90 THEN 'Recent' WHEN date_diff('day',last_transaction_date,current_date)<=180 THEN 'Dormant' ELSE 'Inactive' END vendor_activity_status",'D','agent用Inactive常数替代契约活动分档。')
# Restore prescribed second join separately; only projection aliases avoid duplicate-column shadowing.
add(14,'second_join','FROM enriched)', 'FROM enriched e LEFT JOIN behavior b ON e.customer_id=b.customer_id)', 'C','契约customer_insights再LEFT JOIN behavior；agent遗漏导致少44行。')
# second_join above inserted at scored CTE; affects multiplicity only, preserved metrics are already e.*.
add(14,'frequency_zero','total_transactions/nullif(customer_lifespan_days/30.0,0) avg_transactions_per_month','coalesce(total_transactions/nullif(customer_lifespan_days/30.0,0),0) avg_transactions_per_month','C','契约lifespan=0时频率为0，agent NULL。')
s=pkg(14)['agent_final_SQL'][0]['text'];old=re.search(r"CASE WHEN customer_lifespan_days>=365.*?END retention_category",s)[0]
new=old.replace("'Long-term'","'Long-term (1+ Years)'").replace("'Medium-term'","'Medium-term (6-12 Months)'").replace("'Short-term'","'Short-term (3-6 Months)'").replace("'New'","'New Customer (1-3 Months)'").replace("'Very New'","'Very New (<1 Month)'")
add(14,'retention_labels',old,new,'O','契约明确简短标签，gold输出带括号标签。')
old=re.search(r'least\(100,revenue_score.*?comprehensive_customer_score',s)[0]
new="least(100,revenue_score*20+frequency_score*15+margin_score*20+CASE WHEN activity_status='Highly Active' THEN 25 WHEN activity_status='Active' THEN 20 WHEN activity_status='At Risk' THEN 10 WHEN activity_status='Dormant' THEN 5 ELSE 0 END+CASE WHEN retention_category='Long-term' THEN 20 WHEN retention_category='Medium-term' THEN 15 WHEN retention_category='Short-term' THEN 10 WHEN retention_category='New' THEN 5 ELSE 0 END)::INTEGER comprehensive_customer_score"
add(14,'score_weights',old,new,'A','契约未给weighted sum的权重及bonus具体数字。')
add(15,'volatility','overall_financial_health_score*0 financial_health_volatility','stddev_samp(overall_financial_health_score) OVER(PARTITION BY subsidiary_id) financial_health_volatility','D','波动率以乘0占位，单观测sample stddev应为NULL。')
s=pkg(16)['agent_final_SQL'][0]['text']
for col in ['department_revenue','department_cogs','department_expenses']:
 end=s.index(' '+col);start=s.rfind('sum(',0,end);old=s[start:end];add(16,'zero_'+col,old+' '+col,'coalesce('+old+',0) '+col,'C','类别无匹配时SUM FILTER产生NULL；契约聚合为0。')
add(16,'class_group','date_trunc(\'month\',t.accounting_period_ending)::DATE performance_month', "l.class_id,date_trunc('month',t.accounting_period_ending)::DATE performance_month",'C','契约内部按class_id分组，agent遗漏。')
for col,expr in [('gross_margin_percentage',"(coalesce(department_revenue,0)-coalesce(department_cogs,0))/nullif(department_revenue,0)"),('net_margin_percentage',"(coalesce(department_revenue,0)-coalesce(department_cogs,0)-coalesce(department_expenses,0))/nullif(department_revenue,0)")]:
 add(16,'zero_'+col,expr+' '+col,'coalesce('+expr+',0) '+col,'C','契约revenue非正时margin为0，agent NULL。')
add(18,'contract_recommendation',"'Standard purchase agreement' contract_recommendation", "CASE WHEN supplier_tier='Strategic Partner' THEN 'Long-term strategic contract with SLA' WHEN supplier_tier='Key Supplier' THEN 'Multi-year contract with performance metrics' WHEN supplier_tier='Important Supplier' THEN 'Annual contract with review clause' ELSE 'Standard purchase agreement' END contract_recommendation",'D','合同建议直接固定为Standard purchase agreement而非契约分档。')
for col,expr in [('is_leftside',"lower(r.accttype) IN ('bank','acctrec','fixedasset','othasset','equity')"),('is_balancesheet',"lower(r.accttype) IN ('bank','acctrec','fixedasset','othasset','acctpay','credcard','othcurrliab','longtermliab','equity')")]:
 add(20,'derive_'+col,'CAST(NULL AS BOOLEAN) AS '+col,expr+' AS '+col,'A','raw无对应布尔列；契约未说明派生映射，gold根据accttype派生。')
for i in [21,22,24]:
 for x in plan[i]['patches']:
  x['category']='I';x['reason']='event15生成器已写出正确列映射，因契约旧源名取不到raw schema而填NULL；event25只修FROM，忘记重生投影。明确实现意图与最终SQL不一致。'
s=pkg(23)['agent_final_SQL'][0]['text'];old="regexp_full_match(trim(source_email), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}$')"
add(23,'loose_email',old,"strpos(source_email,'@')>1 AND strpos(source_email,'.')>strpos(source_email,'@')",'O','gold弱校验保留two@@signs.com和missing@.com；契约正则排除，agent照做。')
(REC/'022_patch_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
