# impl-001 | marts | lever__candidate_quality_insights | 差异：S1；日期 2025-10-27

## 契约完整原文

S3:2057–2147

```yaml
    - name: lever__candidate_quality_insights
      description: Single-row snapshot computed at run time summarizing candidate quality distributions, percentiles, and top contributing factors.
      grain: Exactly one row per run (point-in-time snapshot)
      source_models:
      - intermediate.int_lever__candidate_insights (opportunity_id, candidate_quality_score, total_lifecycle_days, total_interviews, interview_completion_rate, positive_feedback_rate, candidate_status_category, candidate_experience_quality, current_stage_order)
      - staging.stg_lever__application (opportunity_id, posting_id, referrer_user_id, type)
      - staging.stg_lever__posting (posting_id, categories_department, categories_team, categories_location, categories_level)
      business_logic: '1) Build candidate_base: - Join candidate insights to applications on opportunity_id, then to postings on posting_id. - Retain fields needed for segmentation and aggregation (quality score, lifecycle days, interviews, completion rate, feedback rate, status, experience quality, stage order, posting_id, referrer_user_id, application type, department, team, location, level). 2) Derive per-candidate attributes (quality_segments): - quality_segment: score >=80 → "Exceptional (80+)", 60–79 → "High Quality (60-79)", 40–59 → "Good Quality (40-59)", 20–39 → "Basic Quality (20-39)", otherwise → "Low Quality (<20)" (NULL scores fall into the last bucket). - funnel_stage_group: stage order >=5 → "Offer/Hire Stage"; >=3 → "Advanced Interview Stage"; >=2 → "Initial Interview Stage"; otherwise → "Early Stage". - source_type: referrer present → "Referred"; else if application type = ''user'' → "Internal"; otherwise → "External". 3) Compute top_quality_indicators: - Independently for Source Type, Department (non-NULL), and Job Level (non-NULL), calculate the average quality score per group and its sample size. - Only consider groups with at least five candidates; rank groups by descending average quality; the best group is rank 1. If multiple groups tie for top rank, selecting a single best group is ambiguous and may fail. 4) Final summary (single row): - analysis_date and generated_at capture the run date and timestamp; report_title is a fixed string. - Totals: total_candidates_analyzed is the count of all segmented candidates; segment counts are the number of candidates in each quality bucket. - Score metrics: overall average, median (50th percentile), and 75th percentile of quality score, each rounded to one decimal; NULL scores are ignored; if no valid values, results are NULL. - Best factors: for each factor type, take the top-ranked group (with at least five candidates) as the best_* fields; corresponding average quality is rounded to one decimal; if no qualifying group, values are NULL. - Process metrics by quality: high-quality groups = Exceptional and High Quality; low-quality groups = Basic Quality and Low Quality. • Average lifecycle days for each group set, rounded to one decimal; NULLs ignored; NULL if no qualifying values. • Interview completion rate averages for each group set, rounded to one decimal; NULLs ignored; NULL if none. - key_finding_source: if the average score for Referred exceeds External by more than 10, recommend referrals; else if Internal exceeds External by more than 10, highlight internal mobility; otherwise note no significant source difference. Any NULL average prevents a match. - key_finding_overall: share of high/exceptional candidates (count of those groups divided by all candidates) drives messaging: ≥40% → "Strong", ≥25% → "Good", otherwise → "Opportunity". - primary_recommendation: driven by the best source type (Referred → invest in referrals; Internal → promote mobility; otherwise optimize external channels). - process_recommendation: compare rounded average lifecycle days between high- and low-quality groups; if high-quality is faster, recommend fast-tracking; otherwise recommend improving early screening. If either average is NULL, the comparison does not match and defaults to the latter. 5) Notes: - Aggregations cover all joined candidates without date partitioning or de-duplication beyond the joins. - Other derived summaries not referenced in the final output do not affect results.'
      columns:
      - name: analysis_date
        data_type: DATE
        description: Run date captured at execution time.
        tests:
        - not_null
      - name: generated_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Run timestamp captured at execution time.
        tests:
        - not_null
      - name: report_title
        data_type: VARCHAR
        description: 'Fixed title: ''Candidate Quality Intelligence Report''.'
      - name: total_candidates_analyzed
        data_type: BIGINT
        description: Total number of segmented candidates after joins.
      - name: exceptional_candidates
        data_type: BIGINT
        description: Count of candidates with score ≥80.
      - name: high_quality_candidates
        data_type: BIGINT
        description: Count of candidates with score 60–79.
      - name: good_quality_candidates
        data_type: BIGINT
        description: Count of candidates with score 40–59.
      - name: basic_quality_candidates
        data_type: BIGINT
        description: Count of candidates with score 20–39.
      - name: low_quality_candidates
        data_type: BIGINT
        description: Count of candidates with score <20 or NULL.
      - name: overall_avg_quality_score
        data_type: DOUBLE
        description: Average quality score rounded to 1 decimal; NULLs ignored; NULL if none.
      - name: median_quality_score
        data_type: DOUBLE
        description: 50th percentile of quality score rounded to 1 decimal; NULLs ignored; NULL if none.
      - name: p75_quality_score
        data_type: DOUBLE
        description: 75th percentile of quality score rounded to 1 decimal; NULLs ignored; NULL if none.
      - name: best_source_type
        data_type: VARCHAR
        description: Top source type by average score among groups with ≥5 candidates; ties unresolved; NULL if none.
      - name: best_source_avg_quality
        data_type: DOUBLE
        description: Average quality score for the best source type rounded to 1 decimal; NULL if best_source_type is NULL.
      - name: best_department
        data_type: VARCHAR
        description: Top department (non-NULL) by average score among groups with ≥5 candidates; ties unresolved; NULL if none.
      - name: best_department_avg_quality
        data_type: DOUBLE
        description: Average quality score for the best department rounded to 1 decimal; NULL if best_department is NULL.
      - name: best_job_level
        data_type: VARCHAR
        description: Top job level (non-NULL) by average score among groups with ≥5 candidates; ties unresolved; NULL if none.
      - name: best_job_level_avg_quality
        data_type: DOUBLE
        description: Average quality score for the best job level rounded to 1 decimal; NULL if best_job_level is NULL.
      - name: high_quality_avg_lifecycle_days
        data_type: DOUBLE
        description: Average lifecycle days for Exceptional/High Quality rounded to 1 decimal; NULLs ignored; NULL if none.
      - name: low_quality_avg_lifecycle_days
        data_type: DOUBLE
        description: Average lifecycle days for Basic/Low Quality rounded to 1 decimal; NULLs ignored; NULL if none.
      - name: high_quality_interview_completion_rate
        data_type: DOUBLE
        description: Average interview completion rate for Exceptional/High Quality rounded to 1 decimal; NULLs ignored; NULL if none.
      - name: low_quality_interview_completion_rate
        data_type: DOUBLE
        description: Average interview completion rate for Basic/Low Quality rounded to 1 decimal; NULLs ignored; NULL if none.
      - name: key_finding_source
        data_type: VARCHAR
        description: 'Message based on source-type averages: Referred or Internal exceeding External by >10 triggers respective message; otherwise note no significant difference.'
      - name: key_finding_overall
        data_type: VARCHAR
        description: 'Message based on the share of high/exceptional candidates: ≥40% Strong, ≥25% Good, otherwise Opportunity.'
      - name: primary_recommendation
        data_type: VARCHAR
        description: 'Recommendation driven by best source type: Referred → invest in referrals; Internal → promote mobility; otherwise optimize external channels.'
      - name: process_recommendation
        data_type: VARCHAR
        description: 'Recommendation from comparing rounded average lifecycle days: if high-quality is faster, fast-track; otherwise improve early screening.'
```

## agent 最终 SQL

S4

```sql
WITH cb AS (SELECT ci.*,a.posting_id,a.referrer_user_id,a.type application_type,p.categories_department,p.categories_level,CASE WHEN candidate_quality_score>=80 THEN 'Exceptional (80+)' WHEN candidate_quality_score>=60 THEN 'High Quality (60-79)' WHEN candidate_quality_score>=40 THEN 'Good Quality (40-59)' WHEN candidate_quality_score>=20 THEN 'Basic Quality (20-39)' ELSE 'Low Quality (<20)' END quality_segment,CASE WHEN current_stage_order>=5 THEN 'Offer/Hire Stage' WHEN current_stage_order>=3 THEN 'Advanced Interview Stage' WHEN current_stage_order>=2 THEN 'Initial Interview Stage' ELSE 'Early Stage' END funnel_stage_group,CASE WHEN referrer_user_id IS NOT NULL THEN 'Referred' WHEN a.type='user' THEN 'Internal' ELSE 'External' END source_type FROM intermediate.int_lever__candidate_insights ci LEFT JOIN staging.stg_lever__application a USING(opportunity_id) LEFT JOIN staging.stg_lever__posting p USING(posting_id)), src AS (SELECT source_type,avg(candidate_quality_score) avgq,count(*) n,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb GROUP BY source_type HAVING count(*)>=5), dep AS (SELECT categories_department,avg(candidate_quality_score) avgq,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb WHERE categories_department IS NOT NULL GROUP BY categories_department HAVING count(*)>=5), lvl AS (SELECT categories_level,avg(candidate_quality_score) avgq,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb WHERE categories_level IS NOT NULL GROUP BY categories_level HAVING count(*)>=5), summary AS (SELECT count(*) total, count(*) FILTER(WHERE quality_segment='Exceptional (80+)') exceptional,count(*) FILTER(WHERE quality_segment='High Quality (60-79)') highq,count(*) FILTER(WHERE quality_segment='Good Quality (40-59)') goodq,count(*) FILTER(WHERE quality_segment='Basic Quality (20-39)') basicq,count(*) FILTER(WHERE quality_segment='Low Quality (<20)') lowq,round(avg(candidate_quality_score),1) avgq,round(quantile_cont(candidate_quality_score,.5),1) medianq,round(quantile_cont(candidate_quality_score,.75),1) p75,round(avg(total_lifecycle_days) FILTER(WHERE quality_segment IN ('Exceptional (80+)','High Quality (60-79)')),1) highdays,round(avg(total_lifecycle_days) FILTER(WHERE quality_segment IN ('Basic Quality (20-39)','Low Quality (<20)')),1) lowdays,round(avg(interview_completion_rate) FILTER(WHERE quality_segment IN ('Exceptional (80+)','High Quality (60-79)')),1) highrate,round(avg(interview_completion_rate) FILTER(WHERE quality_segment IN ('Basic Quality (20-39)','Low Quality (<20)')),1) lowrate,avg(candidate_quality_score) FILTER(WHERE source_type='Referred') referred,avg(candidate_quality_score) FILTER(WHERE source_type='Internal') internal,avg(candidate_quality_score) FILTER(WHERE source_type='External') external_avg FROM cb) SELECT current_date analysis_date,current_timestamp generated_at,'Candidate Quality Intelligence Report' report_title,total total_candidates_analyzed,exceptional exceptional_candidates,highq high_quality_candidates,goodq good_quality_candidates,basicq basic_quality_candidates,lowq low_quality_candidates,avgq overall_avg_quality_score,medianq median_quality_score,p75 p75_quality_score,(SELECT source_type FROM src WHERE rn=1) best_source_type,round((SELECT avgq FROM src WHERE rn=1),1) best_source_avg_quality,(SELECT categories_department FROM dep WHERE rn=1) best_department,round((SELECT avgq FROM dep WHERE rn=1),1) best_department_avg_quality,(SELECT categories_level FROM lvl WHERE rn=1) best_job_level,round((SELECT avgq FROM lvl WHERE rn=1),1) best_job_level_avg_quality,highdays high_quality_avg_lifecycle_days,lowdays low_quality_avg_lifecycle_days,highrate high_quality_interview_completion_rate,lowrate low_quality_interview_completion_rate,CASE WHEN referred>external_avg+10 THEN 'Referral sources produce higher-quality candidates' WHEN internal>external_avg+10 THEN 'Internal mobility produces higher-quality candidates' ELSE 'No significant source difference' END key_finding_source,CASE WHEN (exceptional+highq)*1.0/nullif(total,0)>=.4 THEN 'Strong candidate quality distribution' WHEN (exceptional+highq)*1.0/nullif(total,0)>=.25 THEN 'Good candidate quality distribution' ELSE 'Opportunity to improve candidate quality' END key_finding_overall,CASE WHEN (SELECT source_type FROM src WHERE rn=1)='Referred' THEN 'Invest in referral programs' WHEN (SELECT source_type FROM src WHERE rn=1)='Internal' THEN 'Promote internal mobility' ELSE 'Optimize external channels' END primary_recommendation,CASE WHEN highdays<lowdays THEN 'Fast-track high-quality candidates' ELSE 'Improve early screening' END process_recommendation FROM summary
```

## gold SQL（仅供定位差异）

S5

```sql
-- Candidate quality insight analysis form
-- In-depth analysis of candidate quality patterns and success factors

with candidate_base as (
    select 
        ci.*,
        a.posting_id,
        a.referrer_user_id,
        a.type as application_type,
        p.categories_department,
        p.categories_team,
        p.categories_location,
        p.categories_level
    from intermediate.int_lever__candidate_insights ci
    left join staging.stg_lever__application a on ci.opportunity_id = a.opportunity_id
    left join staging.stg_lever__posting p on a.posting_id = p.posting_id
),

quality_segments as (
    select 
        cb.*,
        case 
            when cb.candidate_quality_score >= 80 then 'Exceptional (80+)'
            when cb.candidate_quality_score >= 60 then 'High Quality (60-79)'
            when cb.candidate_quality_score >= 40 then 'Good Quality (40-59)'
            when cb.candidate_quality_score >= 20 then 'Basic Quality (20-39)'
            else 'Low Quality (<20)'
        end as quality_segment,
        
        case 
            when cb.current_stage_order >= 5 then 'Offer/Hire Stage'
            when cb.current_stage_order >= 3 then 'Advanced Interview Stage'
            when cb.current_stage_order >= 2 then 'Initial Interview Stage'
            else 'Early Stage'
        end as funnel_stage_group,
        
        case 
            when cb.referrer_user_id is not null then 'Referred'
            when cb.application_type = 'user' then 'Internal'
            else 'External'
        end as source_type
    from candidate_base cb
),

quality_patterns as (
    select 
        qs.quality_segment,
        qs.source_type,
        qs.categories_department,
        qs.funnel_stage_group,
        
        count(*) as candidate_count,
        avg(qs.candidate_quality_score) as avg_quality_score,
        avg(qs.total_lifecycle_days) as avg_lifecycle_days,
        avg(qs.total_interviews) as avg_interviews,
        avg(qs.interview_completion_rate) as avg_interview_completion_rate,
        avg(qs.positive_feedback_rate) as avg_positive_feedback_rate,
        
        count(case when qs.candidate_status_category = 'Successfully Hired' then 1 end) as hired_count,
        count(case when qs.candidate_experience_quality = 'Excellent Experience' then 1 end) as excellent_experience_count,
        
        case 
            when count(*) > 0 
            then round(count(case when qs.candidate_status_category = 'Successfully Hired' then 1 end)::numeric / count(*) * 100, 1)
            else 0 
        end as hire_rate_pct,
        
        case 
            when count(*) > 0 
            then round(count(case when qs.candidate_experience_quality = 'Excellent Experience' then 1 end)::numeric / count(*) * 100, 1)
            else 0 
        end as excellent_experience_rate_pct
        
    from quality_segments qs
    group by qs.quality_segment, qs.source_type, qs.categories_department, qs.funnel_stage_group
),

top_quality_indicators as (
    select 
        'Source Type' as factor_type,
        qs.source_type as factor_value,
        avg(qs.candidate_quality_score) as avg_quality_score,
        count(*) as sample_size,
        rank() over (order by avg(qs.candidate_quality_score) desc) as quality_rank
    from quality_segments qs
    group by qs.source_type
    having count(*) >= 5  -- At least 5 samples
    
    union all
    
    select 
        'Department' as factor_type,
        qs.categories_department as factor_value,
        avg(qs.candidate_quality_score) as avg_quality_score,
        count(*) as sample_size,
        rank() over (order by avg(qs.candidate_quality_score) desc) as quality_rank
    from quality_segments qs
    where qs.categories_department is not null
    group by qs.categories_department
    having count(*) >= 5
    
    union all
    
    select 
        'Job Level' as factor_type,
        qs.categories_level as factor_value,
        avg(qs.candidate_quality_score) as avg_quality_score,
        count(*) as sample_size,
        rank() over (order by avg(qs.candidate_quality_score) desc) as quality_rank
    from quality_segments qs
    where qs.categories_level is not null
    group by qs.categories_level
    having count(*) >= 5
),

success_correlations as (
    select 
        'Interview Completion Rate' as metric_name,
        case 
            when avg(case when qs.candidate_status_category = 'Successfully Hired' then qs.interview_completion_rate end) > 
                 avg(case when qs.candidate_status_category != 'Successfully Hired' then qs.interview_completion_rate end)
            then 'Positive Correlation'
            else 'Negative Correlation'
        end as correlation_with_success,
        avg(case when qs.candidate_status_category = 'Successfully Hired' then qs.interview_completion_rate end) as hired_avg,
        avg(case when qs.candidate_status_category != 'Successfully Hired' then qs.interview_completion_rate end) as not_hired_avg
    from quality_segments qs
    
    union all
    
    select 
        'Positive Feedback Rate' as metric_name,
        case 
            when avg(case when qs.candidate_status_category = 'Successfully Hired' then qs.positive_feedback_rate end) > 
                 avg(case when qs.candidate_status_category != 'Successfully Hired' then qs.positive_feedback_rate end)
            then 'Positive Correlation'
            else 'Negative Correlation'
        end as correlation_with_success,
        avg(case when qs.candidate_status_category = 'Successfully Hired' then qs.positive_feedback_rate end) as hired_avg,
        avg(case when qs.candidate_status_category != 'Successfully Hired' then qs.positive_feedback_rate end) as not_hired_avg
    from quality_segments qs
    
    union all
    
    select 
        'Process Speed' as metric_name,
        case 
            when avg(case when qs.candidate_status_category = 'Successfully Hired' then qs.total_lifecycle_days end) < 
                 avg(case when qs.candidate_status_category != 'Successfully Hired' then qs.total_lifecycle_days end)
            then 'Positive Correlation (Faster = Better)'
            else 'Negative Correlation'
        end as correlation_with_success,
        avg(case when qs.candidate_status_category = 'Successfully Hired' then qs.total_lifecycle_days end) as hired_avg,
        avg(case when qs.candidate_status_category != 'Successfully Hired' then qs.total_lifecycle_days end) as not_hired_avg
    from quality_segments qs
),

final_summary as (
    select 
        current_date as analysis_date,
        current_timestamp as generated_at,
        'Candidate Quality Intelligence Report' as report_title,
        
        -- overall mass distribution
        count(*) as total_candidates_analyzed,
        count(case when qs.quality_segment = 'Exceptional (80+)' then 1 end) as exceptional_candidates,
        count(case when qs.quality_segment = 'High Quality (60-79)' then 1 end) as high_quality_candidates,
        count(case when qs.quality_segment = 'Good Quality (40-59)' then 1 end) as good_quality_candidates,
        count(case when qs.quality_segment = 'Basic Quality (20-39)' then 1 end) as basic_quality_candidates,
        count(case when qs.quality_segment = 'Low Quality (<20)' then 1 end) as low_quality_candidates,
        
        round(avg(qs.candidate_quality_score), 1) as overall_avg_quality_score,
        round(percentile_cont(0.5) within group (order by qs.candidate_quality_score), 1) as median_quality_score,
        round(percentile_cont(0.75) within group (order by qs.candidate_quality_score), 1) as p75_quality_score,
        
        -- Success factor analysis
        (select tqi.factor_value from top_quality_indicators tqi where tqi.factor_type = 'Source Type' and tqi.quality_rank = 1) as best_source_type,
        (select round(tqi.avg_quality_score, 1) from top_quality_indicators tqi where tqi.factor_type = 'Source Type' and tqi.quality_rank = 1) as best_source_avg_quality,
        
        (select tqi.factor_value from top_quality_indicators tqi where tqi.factor_type = 'Department' and tqi.quality_rank = 1) as best_department,
        (select round(tqi.avg_quality_score, 1) from top_quality_indicators tqi where tqi.factor_type = 'Department' and tqi.quality_rank = 1) as best_department_avg_quality,
        
        (select tqi.factor_value from top_quality_indicators tqi where tqi.factor_type = 'Job Level' and tqi.quality_rank = 1) as best_job_level,
        (select round(tqi.avg_quality_score, 1) from top_quality_indicators tqi where tqi.factor_type = 'Job Level' and tqi.quality_rank = 1) as best_job_level_avg_quality,
        
        -- Process optimization insights
        round(avg(case when qs.quality_segment in ('Exceptional (80+)', 'High Quality (60-79)') then qs.total_lifecycle_days end), 1) as high_quality_avg_lifecycle_days,
        round(avg(case when qs.quality_segment in ('Basic Quality (20-39)', 'Low Quality (<20)') then qs.total_lifecycle_days end), 1) as low_quality_avg_lifecycle_days,
        
        round(avg(case when qs.quality_segment in ('Exceptional (80+)', 'High Quality (60-79)') then qs.interview_completion_rate end), 1) as high_quality_interview_completion_rate,
        round(avg(case when qs.quality_segment in ('Basic Quality (20-39)', 'Low Quality (<20)') then qs.interview_completion_rate end), 1) as low_quality_interview_completion_rate,
        
        -- Key findings
        case 
            when avg(case when qs.source_type = 'Referred' then qs.candidate_quality_score end) > 
                 avg(case when qs.source_type = 'External' then qs.candidate_quality_score end) + 10
            then 'Referrals produce significantly higher quality candidates'
            when avg(case when qs.source_type = 'Internal' then qs.candidate_quality_score end) > 
                 avg(case when qs.source_type = 'External' then qs.candidate_quality_score end) + 10
            then 'Internal candidates show higher quality scores'
            else 'No significant source quality difference observed'
        end as key_finding_source,
        
        case 
            when count(case when qs.quality_segment in ('Exceptional (80+)', 'High Quality (60-79)') then 1 end)::numeric / count(*) >= 0.4
            then 'Strong candidate quality - 40%+ are high/exceptional quality'
            when count(case when qs.quality_segment in ('Exceptional (80+)', 'High Quality (60-79)') then 1 end)::numeric / count(*) >= 0.25
            then 'Good candidate quality - 25%+ are high/exceptional quality'
            else 'Opportunity to improve candidate quality - focus on sourcing'
        end as key_finding_overall,
        
        -- Suggestions for action
        case 
            when (select tqi.factor_value from top_quality_indicators tqi where tqi.factor_type = 'Source Type' and tqi.quality_rank = 1) = 'Referred'
            then 'Invest more in employee referral programs'
            when (select tqi.factor_value from top_quality_indicators tqi where tqi.factor_type = 'Source Type' and tqi.quality_rank = 1) = 'Internal'
            then 'Promote internal mobility and development'
            else 'Optimize external sourcing channels'
        end as primary_recommendation,
        
        case 
            when round(avg(case when qs.quality_segment in ('Exceptional (80+)', 'High Quality (60-79)') then qs.total_lifecycle_days end), 1) < 
                 round(avg(case when qs.quality_segment in ('Basic Quality (20-39)', 'Low Quality (<20)') then qs.total_lifecycle_days end), 1)
            then 'Fast-track high-quality candidates to reduce time-to-hire'
            else 'Review screening process to identify quality candidates earlier'
        end as process_recommendation
        
    from quality_segments qs
)

select * from final_summary
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1 | 1 | 1 | 1 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| analysis_date | 0 | 0 | 0 | DATE | DATE |
| basic_quality_candidates | 0 | 0 | 0 | BIGINT | BIGINT |
| best_department | 0 | 0 | 0 | VARCHAR | VARCHAR |
| best_job_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| best_source_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| exceptional_candidates | 0 | 0 | 0 | BIGINT | BIGINT |
| good_quality_candidates | 0 | 0 | 0 | BIGINT | BIGINT |
| high_quality_candidates | 0 | 0 | 0 | BIGINT | BIGINT |
| key_finding_overall | 0 | 0 | 0 | VARCHAR | VARCHAR |
| key_finding_source | 0 | 0 | 0 | VARCHAR | VARCHAR |
| low_quality_avg_lifecycle_days | 0 | 0 | 0 | DOUBLE | DOUBLE |
| low_quality_candidates | 0 | 0 | 0 | BIGINT | BIGINT |
| low_quality_interview_completion_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| median_quality_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| overall_avg_quality_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| p75_quality_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| primary_recommendation | 0 | 0 | 0 | VARCHAR | VARCHAR |
| process_recommendation | 0 | 0 | 0 | VARCHAR | VARCHAR |
| report_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| total_candidates_analyzed | 0 | 0 | 0 | BIGINT | BIGINT |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"analysis_date":"2025-10-27","generated_at":"2025-10-27 08:00:00+08"}]</code> | <code>[{"analysis_date":"2025-10-27","generated_at":"2025-10-27 15:31:02.618842+08"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>6列；[{"column":"best_department","table_rows":1}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["exceptional_candidates","basic_quality_candidates","low_quality_candidates"],"nonnull_equal_rows":1,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["exceptional_candidates","basic_quality_candidates","low_quality_candidates"],"nonnull_equal_rows":1,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"report_title","expression":["'Candidate Quality Intelligence Report'"]}]</code> |
| B7_specified_not_read | <code>["intermediate.int_lever__candidate_insights (opportunity_id, candidate_quality_score, total_lifecycle_days, total_interviews, interview_completion_rate, positive_feedback_rate, candidate_status_category, candidate_experience_quality, current_stage_order)"]</code> |
| C9_agent_runtime_text | <code>S4:1 current_date；命中数=2</code> |
| C9_gold_runtime_text | <code>S5:160 current_date；命中数=2</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory 'lever__candidate_quality_insights':'''WITH cb AS (SELECT ci.*,a.posting_id,a.referrer_user_id,a.type application_type,p.categories_department,p.categories_level,CASE WHEN candidate_quality_score&gt;=80 THEN 'Exceptional (80+)' WHEN candidate_quality_score&gt;=60 THEN 'High Quality (60-79)' WHEN candidate_quality_score&gt;=40 THEN 'Good Quality (40-59)' WHEN candidate_quality_score&gt;=20 THEN 'Basic Quality (20-39)' ELSE 'Low Quality (&lt;20)' END quality_segment,CASE WHEN current_stage_order&gt;=5 THEN 'Offer/Hire Stage' WHEN current_stage_order&gt;=3 THEN 'Advanced Interview Stage' WHEN current_stage_order&gt;=2 THEN 'Initial Interview Stage' ELSE 'Early Stage' END funnel_stage_group,CASE WHEN referrer_user_id IS NOT NULL THEN 'Referred' WHEN a.type='user' THEN 'Internal' ELSE 'External' END source_type FROM intermediate.int_lever__candidate_insights ci LEFT JOIN staging.stg_lever__application a USING(opportunity_id) LEFT JOIN staging.stg_lever__posting p USING(posting_id)), src AS (SELECT source_type,avg(candidate_quality_score) avgq,count(*) n,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb GROUP BY source_type HAVING count(*)&gt;=5), dep AS (SELECT categories_department,avg(candidate_quality_score) avgq,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb WHERE categories_department IS NOT NULL GROUP BY categories_department HAVING count(*)&gt;=5), lvl AS (SELECT categories_level,avg(candidate_quality_score) avgq,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb WHERE categories_level IS NOT NULL GROUP BY categories_level HAVING count(*)&gt;=5), summary AS (SELECT count(*) total, count(*) FILTER(WHERE quality_segment='Exceptional (80+)') exceptional,count(*) FILTER(WHERE quality_segment='High Quality (60-79)') highq,count(*) FILTER(WHERE quality_segment='Good Quality (40-59)') goodq,count(*) FILTER(WHERE quality_segment='Basic Quality (20-39)') basicq,count(*) FILTER(WHERE quality_segment='Low Quality (&lt;20)') lowq,round(avg(candidate_quality_score),1) avgq,round(quantile_cont(candidate_quality_score,.5),1) medianq,round(quantile_cont(candidate_quality_score,.75),1) p75,round(avg(total_lifecycle_days) FILTER(WHERE quality_segment IN ('Exceptional (80+)','High Quality (60-79)')),1) highdays,round(avg(total_lifecycle_days) FILTER(WHERE quality_segment IN ('Basic Quality (20-39)','Low Quality (&lt;20)')),1) lowdays,round(avg(interview_completion_rate) FILTER(WHERE quality_segment IN ('Exceptional (80+)','High Quality (60-79)')),1) highrate,round(avg(interview_completion_rate) FILTER(WHERE quality_segment IN ('Basic Quality (20-39)','Low Quality (&lt;20)')),1) lowrate,avg(candidate_quality_score) FILTER(WHERE source_type='Referred') referred,avg(candidate_quality_score) FILTER(WHERE source_type='Internal') internal,avg(candidate_quality_score) FILTER(WHERE source_type='External') external FROM cb) SELECT current_date analysis_date,current_timestamp generated_at,'Candidate Quality Intelligence Report' report_title,total total_candidates_analyzed,exceptional exceptional_candidates,highq high_quality_candidates,goodq good_quality_candidates,basicq basic_quality_candidates,lowq low_quality_candidates,avgq overall_avg_quality_score,medianq median_quality_score,p75 p75_quality_score,(SELECT source_type FROM src WHERE rn=1) best_source_type,round((SELECT avgq FROM src WHERE rn=1),1) best_source_avg_quality,(SELECT categories_department FROM dep WHERE rn=1) best_department,round((SELECT avgq FROM dep WHERE rn=1),1) best_department_avg_quality,(SELECT categories_level FROM lvl WHERE rn=1) best_job_level,round((SELECT avgq FROM lvl WHERE rn=1),1) best_job_level_avg_quality,highdays high_quality_avg_lifecycle_days,lowdays low_quality_avg_lifecycle_days,highrate high_quality_interview_completion_rate,lowrate low_quality_interview_completion_rate,CASE WHEN referred&gt;external+10 THEN 'Referral sources produce higher-quality candidates' WHEN internal&gt;external+10 THEN 'Internal mobility produces higher-quality candidates' ELSE 'No significant source difference' END key_finding_source,CASE WHEN (exceptional+highq)*1.0/nullif(total,0)&gt;=.4 THEN 'Strong candidate quality distribution' WHEN (exceptional+highq)*1.0/nullif(total,0)&gt;=.25 THEN 'Good candidate quality distribution' ELSE 'Opportunity to improve candidate quality' END key_finding_overall,CASE WHEN (SELECT source_type FROM src WHERE rn=1)='Referred' THEN 'Invest in referral programs' WHEN (SELECT source_type FROM src WHERE rn=1)='Internal' THEN 'Promote internal mobility' ELSE 'Optimize external channels' END primary_recommendation,CASE WHEN highdays&lt;lowdays THEN 'Fast-track high-quality candidates' ELSE 'Improve early screening' END process_recommendation FROM summary''',</code> |

## 轨迹索引（不放输出原文）

本题事件总数：69；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find sql -maxdepth 3 -type f &#124; sort &#124; head -100 &amp;&amp; cat config/layer_dependencies.yaml</code> | 4500 | true | false |
| 19 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/intermediate')<br>models={<br>'int_lever__contact_info':'''WITH emails AS (SELECT contact_id, string_agg('&lt;' &#124;&#124; email &#124;&#124; '&gt;', ', ') AS emails</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/models.py &lt;&lt;'PY'<br>models={<br>'int_lever__hiring_funnel_metrics':'''WITH sm AS (SELECT stage_id, CASE WHEN lower(stage_name) LIKE '%new%' OR lower(stage_name) LIKE '%lead%' THEN 1 WHEN lower(s</code> | 0 | false | false |
| 23 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/marts')<br>models={<br>'lever__interview_enhanced':'''SELECT iu.canceled_at,iu.created_at,iu.creator_user_id,iu.interview_date,iu.duration,iu.</code> | 0 | false | false |
| 25 | run | <code>cat &gt;&gt; /tmp/marts.py &lt;&lt;'PY'<br>models={<br>'lever__candidate_quality_insights':'''WITH cb AS (SELECT ci.*,a.posting_id,a.referrer_user_id,a.type application_type,p.categories_department,p.categories_level,C</code> | 6312 | true | false |
| 27 | run | <code>grep -E 'ERROR -&#124;Executing: staging&#124;STAGING layer complete' /tmp/run.log</code> | 5620 | true | false |
| 35 | run | <code>find sql -type f &#124; sort</code> | 2341 | true | false |
| 37 | run | <code>sed -i "s/) external FROM cb/) external_avg FROM cb/; s/referred&gt;external+10/referred&gt;external_avg+10/; s/internal&gt;external+10/internal&gt;external_avg+10/" sql/marts/lever__candidate_quality_insights.sq</code> | 2929 | true | false |
| 41 | run | <code>sed -i 's/r\\."/r."/g' sql/staging/*.sql; python run.py &gt;/tmp/run3.log 2&gt;&amp;1; grep 'ERROR -' /tmp/run3.log</code> | 2929 | true | false |

### agent action 的 thought/message 命中原句

event 25 / message

```text
'lever__candidate_quality_insights':'''WITH cb AS (SELECT ci.*,a.posting_id,a.referrer_user_id,a.type application_type,p.categories_department,p.categories_level,CASE WHEN candidate_quality_score>=80 THEN 'Exceptional (80+)' WHEN candidate_quality_score>=60 THEN 'High Quality (60-79)' WHEN candidate_quality_score>=40 THEN 'Good Quality (40-59)' WHEN candidate_quality_score>=20 THEN 'Basic Quality (20-39)' ELSE 'Low Quality (<20)' END quality_segment,CASE WHEN current_stage_order>=5 THEN 'Offer/Hire Stage' WHEN current_stage_order>=3 THEN 'Advanced Interview Stage' WHEN current_stage_order>=2 THEN 'Initial Interview Stage' ELSE 'Early Stage' END funnel_stage_group,CASE WHEN referrer_user_id IS NOT NULL THEN 'Referred' WHEN a.type='user' THEN 'Internal' ELSE 'External' END source_type FROM intermediate.int_lever__candidate_insights ci LEFT JOIN staging.stg_lever__application a USING(opportunity_id) LEFT JOIN staging.stg_lever__posting p USING(posting_id)), src AS (SELECT source_type,avg(candidate_quality_score) avgq,count(*) n,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb GROUP BY source_type HAVING count(*)>=5), dep AS (SELECT categories_department,avg(candidate_quality_score) avgq,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb WHERE categories_department IS NOT NULL GROUP BY categories_department HAVING count(*)>=5), lvl AS (SELECT categories_level,avg(candidate_quality_score) avgq,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb WHERE categories_level IS NOT NULL GROUP BY categories_level HAVING count(*)>=5), summary AS (SELECT count(*) total, count(*) FILTER(WHERE quality_segment='Exceptional (80+)') exceptional,count(*) FILTER(WHERE quality_segment='High Quality (60-79)') highq,count(*) FILTER(WHERE quality_segment='Good Quality (40-59)') goodq,count(*) FILTER(WHERE quality_segment='Basic Quality (20-39)') basicq,count(*) FILTER(WHERE quality_segment='Low Quality (<20)') lowq,round(avg(candidate_quality_score),1) avgq,round(quantile_cont(candidate_quality_score,.5),1) medianq,round(quantile_cont(candidate_quality_score,.75),1) p75,round(avg(total_lifecycle_days) FILTER(WHERE quality_segment IN ('Exceptional (80+)','High Quality (60-79)')),1) highdays,round(avg(total_lifecycle_days) FILTER(WHERE quality_segment IN ('Basic Quality (20-39)','Low Quality (<20)')),1) lowdays,round(avg(interview_completion_rate) FILTER(WHERE quality_segment IN ('Exceptional (80+)','High Quality (60-79)')),1) highrate,round(avg(interview_completion_rate) FILTER(WHERE quality_segment IN ('Basic Quality (20-39)','Low Quality (<20)')),1) lowrate,avg(candidate_quality_score) FILTER(WHERE source_type='Referred') referred,avg(candidate_quality_score) FILTER(WHERE source_type='Internal') internal,avg(candidate_quality_score) FILTER(WHERE source_type='External') external FROM cb) SELECT current_date analysis_date,current_timestamp generated_at,'Candidate Quality Intelligence Report' report_title,total total_candidates_analyzed,exceptional exceptional_candidates,highq high_quality_candidates,goodq good_quality_candidates,basicq basic_quality_candidates,lowq low_quality_candidates,avgq overall_avg_quality_score,medianq median_quality_score,p75 p75_quality_score,(SELECT source_type FROM src WHERE rn=1) best_source_type,round((SELECT avgq FROM src WHERE rn=1),1) best_source_avg_quality,(SELECT categories_department FROM dep WHERE rn=1) best_department,round((SELECT avgq FROM dep WHERE rn=1),1) best_department_avg_quality,(SELECT categories_level FROM lvl WHERE rn=1) best_job_level,round((SELECT avgq FROM lvl WHERE rn=1),1) best_job_level_avg_quality,highdays high_quality_avg_lifecycle_days,lowdays low_quality_avg_lifecycle_days,highrate high_quality_interview_completion_rate,lowrate low_quality_interview_completion_rate,CASE WHEN referred>external+10 THEN 'Referral sources produce higher-quality candidates' WHEN internal>external+10 THEN 'Internal mobility produces higher-quality candidates' ELSE 'No significant source difference' END key_finding_source,CASE WHEN (exceptional+highq)*1.0/nullif(total,0)>=.4 THEN 'Strong candidate quality distribution' WHEN (exceptional+highq)*1.0/nullif(total,0)>=.25 THEN 'Good candidate quality distribution' ELSE 'Opportunity to improve candidate quality' END key_finding_overall,CASE WHEN (SELECT source_type FROM src WHERE rn=1)='Referred' THEN 'Invest in referral programs' WHEN (SELECT source_type FROM src WHERE rn=1)='Internal' THEN 'Promote internal mobility' ELSE 'Optimize external channels' END primary_recommendation,CASE WHEN highdays<lowdays THEN 'Fast-track high-quality candidates' ELSE 'Improve early screening' END process_recommendation FROM summary''',
```
event 37 / message

```text
Running command: sed -i "s/) external FROM cb/) external_avg FROM cb/; s/referred>external+10/referred>external_avg+10/; s/internal>external+10/internal>external_avg+10/" sql/marts/lever__candidate_quality_insights.sql
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-001.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_quality_insights.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/marts/lever__candidate_quality_insights.sql`
- S6: `records/006_contract_impl-001.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md`
- S10: `data/019_packages_work/019_impl-001_lever__candidate_quality_insights/019_impl-001_lever__candidate_quality_insights.json`
- S11: `data/011_agent_alignment/impl-001_attempt_01/lever__candidate_quality_insights_2025-10-27.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions`
