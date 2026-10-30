# impl-012 | intermediate | int_marketo__lead | 差异：S1；日期 原记录

## 契约完整原文

S3:651–699

```yaml
    - name: int_marketo__lead
      description: Lead dimension with merge/delete flags derived from activity tables; all leads from staging are retained (no filtering)
      grain: One row per input row in staging.stg_marketo__lead; duplicates on lead_id are preserved
      source_models:
      - staging.stg_marketo__lead
      - staging.stg_marketo__activity_merge_leads
      - staging.stg_marketo__activity_delete_lead
      business_logic: '- Start with all rows from staging.stg_marketo__lead (no filtering or deduping in this model). - Build deleted_leads as the distinct set of lead_id from staging.stg_marketo__activity_delete_lead. - Build unique_merges from staging.stg_marketo__activity_merge_leads by: - Grouping by lead_id and concatenating distinct merged_lead_ids separated by ", ". - Null policy: null merged_lead_ids are ignored; if no non-null values exist for a lead, the result is null. - Ordering: no explicit ordering is applied during concatenation, so the sequence is not guaranteed. - Left join deleted_leads and unique_merges to the lead base on lead_id. - Compute flags: - is_deleted = TRUE if a matching deleted_leads.lead_id exists, else FALSE. - is_merged = TRUE if merged_into_lead_id is not null, else FALSE. - Select all original lead attributes unchanged (formatting preserved), plus is_deleted, merged_into_lead_id, and is_merged.'
      columns:
      - name: lead_id
        data_type: VARCHAR
        description: Lead identifier from staging; grain follows source and duplicates (if any) are preserved.
        tests:
        - not_null
        - unique
      - name: email
        data_type: VARCHAR
        description: Email from staging; passed through unchanged
        tests:
        - not_null
      - name: first_name
        data_type: VARCHAR
        description: First name from staging; passed through unchanged
      - name: last_name
        data_type: VARCHAR
        description: Last name from staging; passed through unchanged
      - name: created_timestamp
        data_type: VARCHAR
        description: Creation timestamp from staging; passed through as VARCHAR
        tests:
        - not_null
      - name: updated_timestamp
        data_type: VARCHAR
        description: Last updated timestamp from staging; passed through as VARCHAR
        tests:
        - not_null
      - name: is_deleted
        data_type: BOOLEAN
        description: TRUE if lead_id appears in staging.stg_marketo__activity_delete_lead, else FALSE (never NULL)
        tests:
        - not_null
      - name: merged_into_lead_id
        data_type: VARCHAR
        description: Comma+space separated distinct merged_lead_ids per lead_id; nulls excluded; order not guaranteed; null when no non-null values exist.
      - name: is_merged
        data_type: BOOLEAN
        description: TRUE if merged_into_lead_id is not null, else FALSE (never NULL)
        tests:
        - not_null
```

## agent 最终 SQL

S4

```sql
WITH deleted_leads AS (SELECT DISTINCT lead_id FROM staging.stg_marketo__activity_delete_lead), unique_merges AS (SELECT lead_id, STRING_AGG(DISTINCT merged_lead_ids, ', ') AS merged_into_lead_id FROM staging.stg_marketo__activity_merge_leads GROUP BY lead_id) SELECT l.lead_id,l.email,l.first_name,l.last_name,l.created_timestamp,l.updated_timestamp,(d.lead_id IS NOT NULL) AS is_deleted,m.merged_into_lead_id,(m.merged_into_lead_id IS NOT NULL) AS is_merged FROM staging.stg_marketo__lead l LEFT JOIN deleted_leads d USING (lead_id) LEFT JOIN unique_merges m USING (lead_id)
```

## gold SQL（仅供定位差异）

S5

```sql
-- Intermediate: Lead dimension with merge and delete flags
WITH leads AS (
    SELECT *
    FROM staging.stg_marketo__lead
), activity_merge_leads AS (
    SELECT *
    FROM staging.stg_marketo__activity_merge_leads
), unique_merges AS (
    SELECT
        lead_id,
        STRING_AGG(DISTINCT merged_lead_ids::VARCHAR, ', ') as merged_into_lead_id
    FROM activity_merge_leads
    GROUP BY 1
), deleted_leads AS (
    SELECT DISTINCT lead_id
    FROM staging.stg_marketo__activity_delete_lead
), joined AS (
    SELECT
        leads.*,
        CASE WHEN deleted_leads.lead_id IS NOT NULL THEN TRUE ELSE FALSE END as is_deleted,
        unique_merges.merged_into_lead_id,
        CASE WHEN unique_merges.merged_into_lead_id IS NOT NULL THEN TRUE ELSE FALSE END as is_merged
    FROM leads
    LEFT JOIN deleted_leads ON leads.lead_id = deleted_leads.lead_id
    LEFT JOIN unique_merges ON leads.lead_id = unique_merges.lead_id
)
SELECT *
FROM joined
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5990 | 5990 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"lead_id":"mar10000455844"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| lead_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_timestamp | 0 | 0 | 0 | VARCHAR | VARCHAR |
| updated_timestamp | 0 | 0 | 0 | VARCHAR | VARCHAR |
| email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| first_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| last_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_deleted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| merged_into_lead_id | 18 | 18 | 18 | VARCHAR | VARCHAR |
| is_merged | 0 | 0 | 0 | BOOLEAN | BOOLEAN |

merged_into_lead_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | MAR10002564722, MAR10000582682,MAR10000837353,MAR10002290544 | MAR10000582682,MAR10000837353,MAR10002290544, MAR10002564722 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| D10_keyword_in_any_result_field | <code>命中数=10；assistant_trajectory w(I,'marketo__lead_calendar_spine',"""SELECT c.date_day,l.lead_id,MD5(COALESCE(CAST(c.date_day AS VARCHAR),'') &#124;&#124; '_' &#124;&#124; COALESCE(l.lead_id,'')) AS lead_day_id FROM utils.marketo__calendar_spine c JOIN intermediate.int_marketo__lead l ON c.date_day&gt;=TRY_CAST(SUBSTR(l.created_timestamp,1,10) AS DATE) WHERE l.created_timestamp IS NOT NULL""")</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 9927 | true | false |
| 15 | run | <code>find docs -type f -maxdepth 2 -print &amp;&amp; grep -n '^    - name:' docs/data_contract.yaml</code> | 2040 | true | false |
| 23 | run | <code>cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>root=Path('sql')<br># staging: (file, raw table, projected cols, filters)<br>models={<br>'stg_marketo__lead':('marketo_lead',[('lead_id','id','VARCHAR'),('crea</code> | 3170 | false | false |
| 29 | run | <code>sed -n '3,10p' /tmp/gen.py</code> | 3760 | false | false |
| 33 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>I=Path('sql/intermediate'); M=Path('sql/marts')<br>def w(dir,n,s): (dir/f'{n}.sql').write_text(s.strip())<br>w(I,'int_marketo__lead',"""WITH deleted_lead</code> | 0 | false | false |
| 35 | run | <code>cat &gt; /tmp/more.py &lt;&lt;'PY'<br>from pathlib import Path<br>M=Path('sql/marts')<br>def w(n,s): (M/f'{n}.sql').write_text(s.strip())<br>w('marketo__email_funnel_dashboard',"""WITH source_sends AS (SELECT *,CAST(activ</code> | 0 | false | false |
| 37 | run | <code>cat &gt;&gt; /tmp/more.py &lt;&lt;'PY'<br>w('marketo__operational_health_simple',"""WITH daily AS (SELECT CAST(activity_timestamp AS DATE) AS activity_date,COUNT(*) AS daily_emails_sent,COUNT(DISTINCT lead_id) AS un</code> | 0 | false | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect()<br>for fmt in ['%Y-%m-%d %H:%M:%S.%f %z','%Y-%m-%d %H:%M:%S %z']:<br> print(fmt,c.execute("select try_strptime('2024-03-11 11:00:59.000 +0800', ?)",[fmt]).fe</code> | 10648 | true | false |
| 41 | run | <code>python - &lt;&lt;'PY'<br>p='sql/marts/marketo__email_templates.sql'<br>s=open(p).read()<br>s=s.replace("WITH stats AS (", "WITH template_versions AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY email_template_id ORDER</code> | 13730 | true | false |
| 43 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_marketo__email_template_history.sql';s=open(p).read();s=s.replace("CAST(operational AS BOOLEAN) AS operational,", "CAST(operational AS BOOLEAN) AS operational, (vers</code> | 2390 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('marketo.duckdb',read_only=True)<br>checks={<br>'lead staged null/duplicates':"select count(*) filter(where lead_id is null),count(*)-count(distinct lead_id) f</code> | 2154 | true | false |
| 47 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>## 已完成<br><br>已根据 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 实现 Marketo SQL 数据流水线，SQL 位于 `sql/staging/`、`sql/intermediate/</code> | 117 | false | false |
| 53 | run | <code>cat &gt; result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>## 已完成<br><br>已根据 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 实现 Marketo SQL 数据流水线，SQL 位于 `sql/staging/`、`sql/intermediate/`、`sql/marts/`，并实现依赖配置所需的 `sql/uti</code> | 1900 | true | false |

### agent action 的 thought/message 命中原句

event 33 / message

```text
w(I,'int_marketo__lead',"""WITH deleted_leads AS (SELECT DISTINCT lead_id FROM staging.stg_marketo__activity_delete_lead), unique_merges AS (SELECT lead_id, STRING_AGG(DISTINCT merged_lead_ids, ', ') AS merged_into_lead_id FROM staging.stg_marketo__activity_merge_leads GROUP BY lead_id) SELECT l.lead_id,l.email,l.first_name,l.last_name,l.created_timestamp,l.updated_timestamp,(d.lead_id IS NOT NULL) AS is_deleted,m.merged_into_lead_id,(m.merged_into_lead_id IS NOT NULL) AS is_merged FROM staging.stg_marketo__lead l LEFT JOIN deleted_leads d USING (lead_id) LEFT JOIN unique_merges m USING (lead_id)""")
```
event 33 / message

```text
w(I,'marketo__change_data_scd',"""WITH source_rows AS (SELECT CURRENT_DATE AS valid_to,lead_id,email AS email_c,first_name AS first_name_c,last_name AS last_name_c,NULL::VARCHAR AS company_c,NULL::VARCHAR AS lead_status_c FROM intermediate.int_marketo__lead UNION ALL SELECT date_day,lead_id,email_c,first_name_c,last_name_c,company_c,lead_status_c FROM intermediate.marketo__change_data_pivot), flagged AS (SELECT s.*,COALESCE(d.email_c,FALSE) AS email_changed,COALESCE(d.first_name_c,FALSE) AS first_name_changed,COALESCE(d.last_name_c,FALSE) AS last_name_changed FROM source_rows s LEFT JOIN intermediate.marketo__change_data_details d ON s.lead_id=d.lead_id AND s.valid_to=d.date_day), groups AS (SELECT *,SUM(CASE WHEN email_c IS NULL AND NOT email_changed THEN 0 ELSE 1 END) OVER (PARTITION BY lead_id ORDER BY valid_to DESC ROWS UNBOUNDED PRECEDING) AS email_grp,SUM(CASE WHEN first_name_c IS NULL AND NOT first_name_changed THEN 0 ELSE 1 END) OVER (PARTITION BY lead_id ORDER BY valid_to DESC ROWS UNBOUNDED PRECEDING) AS first_grp,SUM(CASE WHEN last_name_c IS NULL AND NOT last_name_changed THEN 0 ELSE 1 END) OVER (PARTITION BY lead_id ORDER BY valid_to DESC ROWS UNBOUNDED PRECEDING) AS last_grp FROM flagged), filled AS (SELECT *,FIRST_VALUE(email_c IGNORE NULLS) OVER (PARTITION BY lead_id,email_grp ORDER BY valid_to DESC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS filled_email,FIRST_VALUE(first_name_c IGNORE NULLS) OVER (PARTITION BY lead_id,first_grp ORDER BY valid_to DESC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS filled_first,FIRST_VALUE(last_name_c IGNORE NULLS) OVER (PARTITION BY lead_id,last_grp ORDER BY valid_to DESC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS filled_last FROM groups) SELECT valid_to,lead_id,filled_email AS email_c,filled_first AS first_name_c,filled_last AS last_name_c,company_c,lead_status_c,MD5(COALESCE(lead_id,'') || '_' || COALESCE(CAST(valid_to AS VARCHAR),'')) AS lead_day_id FROM filled""")
```
event 33 / message

```text
w(I,'marketo__lead_calendar_spine',"""SELECT c.date_day,l.lead_id,MD5(COALESCE(CAST(c.date_day AS VARCHAR),'') || '_' || COALESCE(l.lead_id,'')) AS lead_day_id FROM utils.marketo__calendar_spine c JOIN intermediate.int_marketo__lead l ON c.date_day>=TRY_CAST(SUBSTR(l.created_timestamp,1,10) AS DATE) WHERE l.created_timestamp IS NOT NULL""")
```
event 35 / message

```text
w('marketo__lead_intelligence_simple',"""WITH lead_base AS (SELECT lead_id,email,first_name,last_name,created_timestamp,updated_timestamp FROM intermediate.int_marketo__lead WHERE NOT is_deleted AND NOT is_merged), engagement AS (SELECT lead_id,COUNT(*)::BIGINT AS total_emails_sent,COUNT(*) FILTER(WHERE was_opened)::BIGINT AS total_emails_opened,COUNT(*) FILTER(WHERE was_clicked)::BIGINT AS total_emails_clicked,COUNT(*) FILTER(WHERE was_bounced)::BIGINT AS total_emails_bounced,COUNT(*) FILTER(WHERE was_unsubscribed)::BIGINT AS total_unsubscribes,COUNT(DISTINCT campaign_id)::BIGINT AS unique_campaigns_participated,MIN(activity_timestamp) AS first_email_sent_at,MAX(activity_timestamp) AS last_email_sent_at,MAX(activity_timestamp) FILTER(WHERE was_opened) AS last_email_opened_at,MAX(activity_timestamp) FILTER(WHERE was_clicked) AS last_email_clicked_at FROM marts.marketo__email_sends WHERE lead_id IS NOT NULL GROUP BY lead_id), metrics AS (SELECT l.*,COALESCE(e.total_emails_sent,0)::BIGINT AS total_emails_sent,COALESCE(e.total_emails_opened,0)::BIGINT AS total_emails_opened,COALESCE(e.total_emails_clicked,0)::BIGINT AS total_emails_clicked,COALESCE(e.total_emails_bounced,0)::BIGINT AS total_emails_bounced,COALESCE(e.total_unsubscribes,0)::BIGINT AS total_unsubscribes,COALESCE(e.unique_campaigns_participated,0)::BIGINT AS unique_campaigns_participated,e.first_email_sent_at,e.last_email_sent_at,e.last_email_opened_at,e.last_email_clicked_at,CASE WHEN COALESCE(e.total_emails_sent,0)=0 THEN 0 ELSE ROUND(e.total_emails_opened::DOUBLE/e.total_emails_sent*100,2) END AS email_open_rate_pct,CASE WHEN COALESCE(e.total_emails_sent,0)=0 THEN 0 ELSE ROUND(e.total_emails_clicked::DOUBLE/e.total_emails_sent*100,2) END AS email_click_rate_pct,COALESCE(e.total_emails_opened,0)*5+COALESCE(e.total_emails_clicked,0)*10 AS total_lead_score FROM lead_base l LEFT JOIN engagement e USING(lead_id)), segmented AS (SELECT *,CASE WHEN total_lead_score>=100 THEN 'Champion' WHEN total_lead_score>=50 THEN 'Loyal Customer' WHEN total_lead_score>=25 THEN 'Potential Loyalist' WHEN total_lead_score>=10 THEN 'Regular Subscriber' WHEN total_lead_score>=5 THEN 'At Risk' ELSE 'Inactive' END AS rfm_segment,CASE WHEN total_lead_score>=80 THEN 'Platinum' WHEN total_lead_score>=50 THEN 'Gold' WHEN total_lead_score>=25 THEN 'Silver' WHEN total_lead_score>=10 THEN 'Bronze' ELSE 'Basic' END AS value_tier,CASE WHEN email_open_rate_pct>=50 AND email_click_rate_pct>=10 THEN 'A-Tier' WHEN email_open_rate_pct>=30 AND email_click_rate_pct>=5 THEN 'B-Tier' WHEN email_open_rate_pct>=15 THEN 'C-Tier' WHEN email_open_rate_pct>=5 THEN 'D-Tier' ELSE 'Unqualified' END AS lead_quality_tier FROM metrics) SELECT lead_id,email,first_name,last_name,created_timestamp AS lead_created_at,total_emails_sent,total_emails_opened,total_emails_clicked,total_emails_bounced,total_unsubscribes,unique_campaigns_participated,email_open_rate_pct,email_click_rate_pct,total_lead_score,first_email_sent_at,last_email_sent_at,last_email_opened_at,last_email_clicked_at,COALESCE(DATE_DIFF('day',CAST(last_email_sent_at AS DATE),CURRENT_DATE),9999)::BIGINT AS days_since_last_email,COALESCE(DATE_DIFF('day',CAST(last_email_opened_at AS DATE),CURRENT_DATE),9999)::BIGINT AS days_since_last_open,COALESCE(DATE_DIFF('day',CAST(last_email_clicked_at AS DATE),CURRENT_DATE),9999)::BIGINT AS days_since_last_click,rfm_segment,value_tier,lead_quality_tier,COALESCE(DATE_DIFF('day',TRY_CAST(SUBSTR(created_timestamp,1,10) AS DATE),CURRENT_DATE),0)::BIGINT AS lead_tenure_days,CASE WHEN total_lead_score>=50 AND COALESCE(DATE_DIFF('day',CAST(last_email_opened_at AS DATE),CURRENT_DATE),9999)<=30 THEN 'Healthy' WHEN total_lead_score>=25 AND COALESCE(DATE_DIFF('day',CAST(last_email_opened_at AS DATE),CURRENT_DATE),9999)<=60 THEN 'Good' WHEN total_lead_score>=10 AND COALESCE(DATE_DIFF('day',CAST(last_email_opened_at AS DATE),CURRENT_DATE),9999)<=90 THEN 'Fair' WHEN total_lead_score>=5 THEN 'Poor' ELSE 'Critical' END AS lead_health_status,CASE WHEN email_click_rate_pct>=10 AND COALESCE(DATE_DIFF('day',CAST(last_email_clicked_at AS DATE),CURRENT_DATE),9999)<=7 THEN 'Schedule Sales Call' WHEN email_open_rate_pct>=30 THEN 'Send Product Demo' WHEN days_since_last_open>60 AND total_emails_opened>0 THEN 'Re-engagement Campaign' WHEN total_emails_opened=0 THEN 'Welcome Series' ELSE 'Standard Campaign Flow' END AS next_best_action,CURRENT_TIMESTAMP AS last_updated_at FROM (SELECT *,COALESCE(DATE_DIFF('day',CAST(last_email_opened_at AS DATE),CURRENT_DATE),9999) AS days_since_last_open FROM segmented) final_rows""")
```
event 37 / message

```text
w('marketo__operational_health_simple',"""WITH daily AS (SELECT CAST(activity_timestamp AS DATE) AS activity_date,COUNT(*) AS daily_emails_sent,COUNT(DISTINCT lead_id) AS unique_recipients,COUNT(DISTINCT campaign_id) AS active_campaigns,COUNT(DISTINCT email_template_id) AS unique_templates,COUNT(*) FILTER(WHERE was_delivered) AS delivered,COUNT(*) FILTER(WHERE was_opened) AS opened,COUNT(*) FILTER(WHERE was_clicked) AS clicked,COUNT(*) FILTER(WHERE was_bounced) AS bounced,COUNT(*) FILTER(WHERE was_unsubscribed) AS unsubscribes,ROUND(COUNT(*) FILTER(WHERE was_delivered)::DOUBLE/COUNT(*)*100,2) AS daily_delivery_rate_pct,ROUND(CASE WHEN COUNT(*) FILTER(WHERE was_delivered)=0 THEN 0 ELSE COUNT(*) FILTER(WHERE was_opened)::DOUBLE/COUNT(*) FILTER(WHERE was_delivered)*100 END,2) AS daily_open_rate_pct,ROUND(COUNT(*) FILTER(WHERE was_bounced)::DOUBLE/COUNT(*)*100,2) AS daily_bounce_rate_pct FROM marts.marketo__email_sends WHERE activity_timestamp IS NOT NULL GROUP BY 1), daily_summary AS (SELECT CASE WHEN AVG(daily_emails_sent)>=1000 THEN 'High Volume System' WHEN AVG(daily_emails_sent)>=500 THEN 'Medium Volume System' WHEN AVG(daily_emails_sent)>=100 THEN 'Low Volume System' ELSE 'Minimal Volume System' END AS system_volume_classification,CASE WHEN STDDEV_SAMP(daily_delivery_rate_pct)<=5 THEN 'Stable' WHEN STDDEV_SAMP(daily_delivery_rate_pct)<=10 THEN 'Moderate Variance' ELSE 'High Variance' END AS delivery_stability,COUNT(*)::BIGINT AS days_of_data,MIN(activity_date) AS earliest_activity_date,MAX(activity_date) AS latest_activity_date,STDDEV_SAMP(daily_delivery_rate_pct) AS delivery_rate_volatility,STDDEV_SAMP(daily_open_rate_pct) AS open_rate_volatility,STDDEV_SAMP(daily_bounce_rate_pct) AS bounce_rate_volatility,AVG(daily_emails_sent) FILTER(WHERE activity_date>=CURRENT_DATE-INTERVAL 6 DAY) AS avg_daily_volume_last_7_days,AVG(daily_delivery_rate_pct) FILTER(WHERE activity_date>=CURRENT_DATE-INTERVAL 6 DAY) AS avg_delivery_rate_last_7_days,AVG(daily_open_rate_pct) FILTER(WHERE activity_date>=CURRENT_DATE-INTERVAL 6 DAY) AS avg_open_rate_last_7_days FROM daily), deliverability AS (SELECT COUNT(*)::BIGINT AS total_email_attempts,COUNT(*) FILTER(WHERE was_delivered)::BIGINT AS successful_deliveries,COUNT(*) FILTER(WHERE was_bounced)::BIGINT AS total_bounces,ROUND(COUNT(*) FILTER(WHERE was_delivered)::DOUBLE/NULLIF(COUNT(*),0)*100,2) AS overall_delivery_rate_pct,ROUND(COUNT(*) FILTER(WHERE was_bounced)::DOUBLE/NULLIF(COUNT(*),0)*100,2) AS overall_bounce_rate_pct,ROUND(COUNT(*) FILTER(WHERE was_delivered AND activity_timestamp>=CURRENT_TIMESTAMP-INTERVAL 30 DAY)::DOUBLE/NULLIF(COUNT(*) FILTER(WHERE activity_timestamp>=CURRENT_TIMESTAMP-INTERVAL 30 DAY),0)*100,2) AS recent_delivery_rate_pct FROM marts.marketo__email_sends), campaign_summary AS (SELECT COUNT(*)::BIGINT AS total_campaigns,COUNT(*) FILTER(WHERE open_rate>=25)::BIGINT AS healthy_campaigns,COUNT(*) FILTER(WHERE open_rate<5)::BIGINT AS critical_campaigns,COUNT(*) FILTER(WHERE bounce_rate>10)::BIGINT AS campaigns_with_bounce_issues FROM (SELECT campaign_id,AVG(CASE WHEN was_delivered THEN 100.0 ELSE 0.0 END) AS open_rate,AVG(CASE WHEN was_bounced THEN 100.0 ELSE 0.0 END) AS bounce_rate FROM marts.marketo__email_sends WHERE campaign_id IS NOT NULL GROUP BY campaign_id) c), lead_rows AS (SELECT l.lead_id,es.activity_id,es.was_clicked,es.was_opened,es.was_delivered,es.count_opens,es.count_clicks FROM intermediate.int_marketo__lead l LEFT JOIN marts.marketo__email_sends es USING(lead_id) WHERE NOT l.is_deleted AND NOT l.is_merged), lead_summary AS (SELECT COUNT(*)::BIGINT AS total_leads,COUNT(*) FILTER(WHERE activity_id IS NOT NULL AND was_clicked)::BIGINT AS engaged_leads,COUNT(*) FILTER(WHERE activity_id IS NOT NULL AND was_opened AND NOT was_clicked)::BIGINT AS moderately_engaged_leads,COUNT(*) FILTER(WHERE activity_id IS NOT NULL AND NOT was_opened)::BIGINT AS low_engaged_leads,COUNT(*) FILTER(WHERE activity_id IS NULL)::BIGINT AS inactive_leads,ROUND(COUNT(*) FILTER(WHERE activity_id IS NOT NULL AND was_clicked)::DOUBLE/NULLIF(COUNT(*),0)*100,2) AS engaged_leads_pct,ROUND(COUNT(*) FILTER(WHERE activity_id IS NULL OR NOT was_delivered)::DOUBLE/NULLIF(COUNT(*),0)*100,2) AS at_risk_leads_pct,ROUND(AVG(CASE WHEN activity_id IS NULL THEN 0 ELSE COALESCE(count_opens,0)*5+COALESCE(count_clicks,0)*10 END),2) AS avg_lead_score FROM lead_rows), combined AS (SELECT CURRENT_DATE AS health_check_date,CURRENT_TIMESTAMP AS health_check_timestamp,d.*,COALESCE(x.total_email_attempts,0) AS total_email_attempts,COALESCE(x.successful_deliveries,0) AS successful_deliveries,COALESCE(x.total_bounces,0) AS total_bounces,COALESCE(x.overall_delivery_rate_pct,0) AS overall_delivery_rate_pct,COALESCE(x.overall_bounce_rate_pct,0) AS overall_bounce_rate_pct,COALESCE(x.recent_delivery_rate_pct,0) AS recent_delivery_rate_pct,l.*,c.*,ROUND(CASE WHEN c.total_campaigns=0 THEN 0 ELSE c.healthy_campaigns::DOUBLE/c.total_campaigns*100 END,2) AS healthy_campaigns_pct FROM daily_summary d CROSS JOIN deliverability x CROSS JOIN campaign_summary c CROSS JOIN lead_summary l) SELECT health_check_date,health_check_timestamp,system_volume_classification,delivery_stability,days_of_data,earliest_activity_date,latest_activity_date,total_email_attempts,successful_deliveries,total_bounces,overall_delivery_rate_pct,overall_bounce_rate_pct,recent_delivery_rate_pct,CASE WHEN overall_delivery_rate_pct>=95 THEN 'Excellent' WHEN overall_delivery_rate_pct>=90 THEN 'Good' WHEN overall_delivery_rate_pct>=85 THEN 'Fair' WHEN overall_delivery_rate_pct>=80 THEN 'Poor' ELSE 'Critical' END AS deliverability_health_status,total_leads,engaged_leads,moderately_engaged_leads,low_engaged_leads,inactive_leads,COALESCE(engaged_leads_pct,0) AS engaged_leads_pct,COALESCE(at_risk_leads_pct,0) AS at_risk_leads_pct,COALESCE(avg_lead_score,0) AS avg_lead_score,CASE WHEN engaged_leads_pct>=40 AND at_risk_leads_pct<=20 THEN 'Excellent' WHEN engaged_leads_pct>=25 AND at_risk_leads_pct<=30 THEN 'Good' WHEN engaged_leads_pct>=15 AND at_risk_leads_pct<=40 THEN 'Fair' WHEN engaged_leads_pct>=5 THEN 'Poor' ELSE 'Critical' END AS lead_database_health_status,total_campaigns,healthy_campaigns,critical_campaigns,campaigns_with_bounce_issues,healthy_campaigns_pct,avg_daily_volume_last_7_days,avg_delivery_rate_last_7_days,avg_open_rate_last_7_days,ROUND(delivery_rate_volatility,2) AS delivery_rate_volatility,ROUND(open_rate_volatility,2) AS open_rate_volatility,ROUND(bounce_rate_volatility,2) AS bounce_rate_volatility,CAST(ROUND((CASE WHEN overall_delivery_rate_pct>=95 THEN 25 WHEN overall_delivery_rate_pct>=90 THEN 20 WHEN overall_delivery_rate_pct>=85 THEN 15 ELSE 5 END)+(CASE WHEN engaged_leads_pct>=40 THEN 25 WHEN engaged_leads_pct>=25 THEN 20 WHEN engaged_leads_pct>=15 THEN 15 ELSE 5 END)+(CASE WHEN healthy_campaigns_pct>=50 THEN 25 WHEN healthy_campaigns_pct>=25 THEN 20 WHEN healthy_campaigns_pct>=10 THEN 15 ELSE 5 END)+(CASE WHEN delivery_stability='Stable' THEN 25 WHEN delivery_stability='Moderate Variance' THEN 15 ELSE 5 END)) AS INTEGER) AS overall_health_score,CASE WHEN overall_delivery_rate_pct<85 THEN 'Focus on improving email deliverability' WHEN at_risk_leads_pct>30 THEN 'Launch re-engagement campaigns for at-risk leads' WHEN critical_campaigns>3 THEN 'Optimize underperforming campaigns' WHEN delivery_stability='High Variance' THEN 'Stabilize email sending patterns' ELSE 'Continue current efforts' END AS primary_recommendation FROM combined""")
```
event 47 / message

```text
- `int_marketo__lead` 按其明示逻辑保留 staging 的全部行；mart email template 元数据则限于推导出的最新版本。
```
event 47 / message

```text
契约内部分测试（如 `int_marketo__lead` 的 unique 测试）与明确写出的重复保留逻辑存在张力，实现遵循模型业务逻辑并在 staging 实施已声明的唯一主键处理。
```
event 53 / message

```text
- `int_marketo__lead` 依照其业务逻辑保留全部 staging 行；contract 中其 unique 测试与“保留重复”的 grain 描述有冲突。
```

## result.md 本表名原句

S9:31

```text
- `int_marketo__lead` 依照其业务逻辑保留全部 staging 行；contract 中其 unique 测试与“保留重复”的 grain 描述有冲突。
```

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-012.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/intermediate/int_marketo__lead.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/sql/intermediate/int_marketo__lead.sql`
- S6: `records/006_contract_impl-012.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/result.md`
- S10: `data/022_packages_work/022_impl-012_int_marketo__lead/022_impl-012_int_marketo__lead.json`
- S11: `data/005_cs_work/impl-012/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/marketo.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions`
