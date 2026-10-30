# impl-013 | marts | netsuite2_financial_dashboard | 差异：S1；日期 2025-10-14

## 契约完整原文

S3:2870–3006

```yaml
    - name: netsuite2_financial_dashboard
      description: Executive financial dashboard aggregating ratios, cash flow, AR, customer metrics, trends, risk and benchmarks per subsidiary-period
      grain: One row per subsidiary_id and accounting_period_id present in intermediate.int_netsuite2__financial_ratios
      source_models:
      - intermediate.int_netsuite2__financial_ratios
      - intermediate.int_netsuite2__cash_flow_analysis
      - intermediate.int_netsuite2__ar_aging_analysis
      - intermediate.int_netsuite2__customer_profitability
      business_logic: '- Base rows come from intermediate.int_netsuite2__financial_ratios (fr); dashboard_date is set to the current_date at execution for all rows. - Left join cash_flow_analysis (cf) by subsidiary_id, filtering to the previous calendar month (the month of current_date minus one month); bring net_cash_flow, operating_cash_flow, cash_flow_health, predicted_next_month_cash_flow, cash_flow_risk_level. If no prior-month CF row exists for the subsidiary, CF outputs are NULL. - Left join AR aging (ar) by subsidiary_id, aggregating across all ar rows per subsidiary: - total_ar_amount and overdue_amount are summed across rows (ignoring NULLs). - overdue_percentage is the ratio of total overdue amount to total AR amount when total AR > 0; otherwise 0. If no AR rows exist for the subsidiary, all AR outputs are NULL. - weighted_average_days_outstanding is the simple average across rows (ignoring NULLs). - Left join customer profitability (cp_summary) by subsidiary_id, aggregating across all cp rows per subsidiary: - total_customers is the row count. - high_value_customers counts rows where customer_segment is Champion or Loyal. - at_risk_customers counts rows where customer_segment is At Risk or activity_status is At Risk. - total_customer_revenue is the sum of total_revenue (ignoring NULLs); average_customer_value is the average of total_revenue (ignoring NULLs). - No de-duplication; if no cp rows for the subsidiary, cp outputs are NULL. - Compute trends (ft) by aggregating financial_kpis per subsidiary_id: - avg_financial_health is the average of overall_financial_health_score; financial_health_volatility is its standard deviation. - avg_net_margin is the average of net_profit_margin; avg_current_ratio is the average of current_ratio. - positive_cash_flow_periods counts rows with cash_flow_health in Excellent or Good; total_periods counts all rows. - Compute risk assessment (ra) per subsidiary_id: - total_risk_score is the sum of four components: - overall_financial_health_score: <40 → 30; <60 → 20; <80 → 10; else 5. - cash_flow_risk_level: High Risk - Negative Trend → 25; contains High Risk → 20; contains Medium Risk → 10; else 5. - overdue_percentage: >0.30 → 20; >0.20 → 15; >0.10 → 10; else 5. - current_ratio: <1.0 → 25; <1.5 → 15; <2.0 → 10; else 5. - When any compared input is NULL, the corresponding component contributes 5. - risk_level buckets: total_risk_score ≥70 → Critical Risk; ≥50 → High Risk; ≥30 → Medium Risk; else Low Risk. - primary_risk_factor priority: overall_financial_health_score<40 → Poor Financial Health; cash_flow_risk_level contains High Risk → Cash Flow Issues; overdue_percentage>0.30 → High Receivables Risk; current_ratio<1.0 → Liquidity Concerns; else No Major Risk Factors. - Compute performance benchmarks (pb) per subsidiary_id: - liquidity_performance from current_ratio: ≥2.0 → Above Target; ≥1.5 → At Target; else Below Target. - profitability_performance from net_profit_margin: ≥0.15 → Above Target; ≥0.05 → At Target; else Below Target. - roe_performance from return_on_equity: ≥0.15 → Above Target; ≥0.10 → At Target; else Below Target. - collection_performance from overdue_percentage: ≤0.05 → Above Target; ≤0.15 → At Target; else Below Target. - improvement_recommendation priority: - If current_ratio<1.5 and net_profit_margin<0.05 → Focus on Operations & Liquidity; - Else if current_ratio<1.5 → Improve Working Capital Management; - Else if net_profit_margin<0.05 → Review Cost Structure; - Else if overdue_percentage>0.15 → Strengthen Collections; - Else → Maintain Current Performance. - Final output: - Select fk.* plus ft, ra, pb by subsidiary_id; filter out rows with NULL subsidiary_id. - cash_flow_consistency_percentage = (positive_cash_flow_periods / total_periods) × 100, rounded to 1 decimal; if total_periods=0, set to 0. - overall_rating, in order: overall_financial_health_score≥80 and risk_level=Low Risk → A+ Excellent; ≥70 and risk_level in Low/Medium Risk → A Good; ≥60 and risk_level≠Critical Risk → B Fair; ≥40 → C Poor; else → D Critical. - key_alert, first match wins: risk_level=Critical Risk → URGENT: Multiple Critical Risk Factors; cash_flow_risk_level contains High Risk → WARNING: Cash Flow Issues; current_ratio<1.0 → ALERT: Liquidity Below Safe Levels; overdue_percentage>0.30 → CAUTION: High Receivables Risk; else → Normal Operations. - dashboard_id is the MD5 hash of the string formed by subsidiary_id, a single underscore, and dashboard_date; casing and spacing are preserved. - Result ordering: descending by total_risk_score, then descending by overall_financial_health_score.'
      columns:
      - name: subsidiary_id
        data_type: VARCHAR
        description: Subsidiary identifier; rows with NULL are excluded
        tests:
        - not_null
      - name: accounting_period_id
        data_type: VARCHAR
        description: Accounting period from financial_ratios for the row
        tests:
        - not_null
      - name: dashboard_date
        data_type: DATE
        description: Build date set to current_date at query execution (same for all rows in a run)
      - name: current_ratio
        data_type: DOUBLE
        description: Liquidity ratio from financial_ratios; no rounding; NULL if missing in source
      - name: quick_ratio
        data_type: DOUBLE
        description: Quick ratio from financial_ratios; no rounding; NULL if missing in source
      - name: return_on_equity
        data_type: DOUBLE
        description: ROE from financial_ratios; no rounding; NULL if missing in source
      - name: gross_margin_ratio
        data_type: DOUBLE
        description: Gross margin ratio from financial_ratios; no rounding; NULL if missing in source
      - name: net_profit_margin
        data_type: DOUBLE
        description: Net profit margin from financial_ratios; no rounding; NULL if missing in source
      - name: overall_financial_health_score
        data_type: DOUBLE
        description: Composite financial health score from financial_ratios; NULL if missing in source
      - name: financial_health_grade
        data_type: VARCHAR
        description: Letter grade from financial_ratios corresponding to the health score; NULL if missing
      - name: net_cash_flow
        data_type: DOUBLE
        description: Net cash flow for prior calendar month per subsidiary; NULL if no CF row for that month
      - name: operating_cash_flow
        data_type: DOUBLE
        description: Operating cash flow for prior calendar month per subsidiary; NULL if no CF row for that month
      - name: cash_flow_health
        data_type: VARCHAR
        description: Cash flow health label from CF for prior month; NULL if no CF row
      - name: predicted_next_month_cash_flow
        data_type: DOUBLE
        description: Predicted next month cash flow from CF; NULL if no prior-month CF row
      - name: cash_flow_risk_level
        data_type: VARCHAR
        description: Cash flow risk level from CF; used in risk scoring; NULL if no prior-month CF row
      - name: total_ar_amount
        data_type: DOUBLE
        description: Total AR amount summed across AR aging rows per subsidiary; NULL if no AR rows
      - name: overdue_amount
        data_type: DOUBLE
        description: Total overdue AR amount summed across AR aging rows per subsidiary; NULL if no AR rows
      - name: overdue_percentage
        data_type: DOUBLE
        description: Ratio of overdue amount to total AR when total AR>0; otherwise 0; NULL if no AR rows
      - name: weighted_average_days_outstanding
        data_type: DOUBLE
        description: Simple average of weighted_average_days_outstanding across AR rows; NULLs ignored; NULL if no AR rows
      - name: total_customers
        data_type: BIGINT
        description: Count of customer_profitability rows per subsidiary; NULL if no customer rows
      - name: high_value_customers
        data_type: BIGINT
        description: Count where customer_segment in ('Champion','Loyal'); duplicates preserved; NULL if no customer rows
      - name: at_risk_customers
        data_type: BIGINT
        description: Count where customer_segment='At Risk' or activity_status='At Risk'; duplicates preserved; NULL if no customer rows
      - name: total_customer_revenue
        data_type: DOUBLE
        description: Sum of total_revenue across customer rows per subsidiary; NULL if no customer rows
      - name: average_customer_value
        data_type: DOUBLE
        description: Average of total_revenue across customer rows per subsidiary; NULLs ignored; NULL if no customer rows
      - name: avg_financial_health
        data_type: DOUBLE
        description: Average of overall_financial_health_score across fk rows per subsidiary; NULLs ignored
      - name: financial_health_volatility
        data_type: DOUBLE
        description: Standard deviation of overall_financial_health_score across fk rows per subsidiary; NULLs ignored
      - name: avg_net_margin
        data_type: DOUBLE
        description: Average of net_profit_margin across fk rows per subsidiary; NULLs ignored
      - name: avg_current_ratio
        data_type: DOUBLE
        description: Average of current_ratio across fk rows per subsidiary; NULLs ignored
      - name: cash_flow_consistency_percentage
        data_type: FLOAT
        description: Percentage of fk rows with cash_flow_health in ('Excellent','Good'), rounded to 1 decimal; 0 when no rows
      - name: total_risk_score
        data_type: INTEGER
        description: Sum of four risk components using defined thresholds; NULL inputs default each component to 5 points
      - name: risk_level
        data_type: VARCHAR
        description: 'Risk bucket from total_risk_score: ≥70 Critical Risk, ≥50 High Risk, ≥30 Medium Risk, else Low Risk'
      - name: primary_risk_factor
        data_type: VARCHAR
        description: 'Primary risk driver by priority: poor health, cash flow, receivables, liquidity; else No Major Risk Factors'
      - name: liquidity_performance
        data_type: VARCHAR
        description: 'Target category from current_ratio: ≥2.0 Above, ≥1.5 At, else Below Target'
      - name: profitability_performance
        data_type: VARCHAR
        description: 'Target category from net_profit_margin: ≥0.15 Above, ≥0.05 At, else Below Target'
      - name: roe_performance
        data_type: VARCHAR
        description: 'Target category from return_on_equity: ≥0.15 Above, ≥0.10 At, else Below Target'
      - name: collection_performance
        data_type: VARCHAR
        description: 'Target category from overdue_percentage: ≤0.05 Above, ≤0.15 At, else Below Target'
      - name: improvement_recommendation
        data_type: VARCHAR
        description: 'Recommendation per priority: Ops & Liquidity, Working Capital, Cost, Collections, else Maintain'
      - name: overall_rating
        data_type: VARCHAR
        description: Composite rating from overall_financial_health_score and risk_level per case order
      - name: key_alert
        data_type: VARCHAR
        description: 'First-match alert: Critical Risk→URGENT, High Risk cash flow→WARNING, current_ratio<1.0→ALERT, overdue>0.3→CAUTION, else Normal'
      - name: dashboard_id
        data_type: VARCHAR
        description: MD5 hash of subsidiary_id+'_'+dashboard_date; unique per (subsidiary_id, dashboard_date); casing/spacing preserved
        tests:
        - not_null
        - unique
```

## agent 最终 SQL

S4

```sql
WITH cf AS (SELECT * FROM intermediate.int_netsuite2__cash_flow_analysis WHERE analysis_month=date_trunc('month',current_date-interval '1 month')), ar AS (SELECT subsidiary_id,sum(total_ar_amount) total_ar_amount,sum(overdue_amount) overdue_amount,sum(overdue_amount)/nullif(sum(total_ar_amount),0) overdue_percentage,avg(weighted_average_days_outstanding) weighted_average_days_outstanding FROM intermediate.int_netsuite2__ar_aging_analysis GROUP BY subsidiary_id), cp AS (SELECT subsidiary_id,count(*) total_customers,count(*) FILTER(WHERE customer_segment IN ('Champion','Loyal')) high_value_customers,count(*) FILTER(WHERE customer_segment='At Risk' OR activity_status='At Risk') at_risk_customers,sum(total_revenue) total_customer_revenue,avg(total_revenue) average_customer_value FROM intermediate.int_netsuite2__customer_profitability GROUP BY subsidiary_id), base AS (SELECT fr.*,current_date dashboard_date,cf.net_cash_flow,cf.operating_cash_flow,cf.cash_flow_health,cf.predicted_next_month_cash_flow,cf.cash_flow_risk_level,ar.total_ar_amount,ar.overdue_amount,ar.overdue_percentage,ar.weighted_average_days_outstanding,cp.total_customers,cp.high_value_customers,cp.at_risk_customers,cp.total_customer_revenue,cp.average_customer_value FROM intermediate.int_netsuite2__financial_ratios fr LEFT JOIN cf USING(subsidiary_id) LEFT JOIN ar USING(subsidiary_id) LEFT JOIN cp USING(subsidiary_id)), trends AS (SELECT *,overall_financial_health_score avg_financial_health,overall_financial_health_score*0 financial_health_volatility,net_profit_margin avg_net_margin,current_ratio avg_current_ratio,CASE WHEN cash_flow_health IN ('Excellent','Good') THEN 100.0 ELSE 0 END cash_flow_consistency_percentage FROM base), risk AS (SELECT *,CASE WHEN overall_financial_health_score<40 THEN 30 WHEN overall_financial_health_score<60 THEN 20 WHEN overall_financial_health_score<80 THEN 10 ELSE 5 END + CASE WHEN cash_flow_risk_level='High Risk - Negative Trend' THEN 25 WHEN cash_flow_risk_level LIKE '%High Risk%' THEN 20 WHEN cash_flow_risk_level LIKE '%Medium Risk%' THEN 10 ELSE 5 END + CASE WHEN overdue_percentage>.30 THEN 20 WHEN overdue_percentage>.20 THEN 15 WHEN overdue_percentage>.10 THEN 10 ELSE 5 END + CASE WHEN current_ratio<1 THEN 25 WHEN current_ratio<1.5 THEN 15 WHEN current_ratio<2 THEN 10 ELSE 5 END total_risk_score FROM trends) SELECT subsidiary_id,accounting_period_id,dashboard_date,current_ratio,quick_ratio,return_on_equity,gross_margin_ratio,net_profit_margin,overall_financial_health_score,financial_health_grade,net_cash_flow,operating_cash_flow,cash_flow_health,predicted_next_month_cash_flow,cash_flow_risk_level,total_ar_amount,overdue_amount,overdue_percentage,weighted_average_days_outstanding,total_customers,high_value_customers,at_risk_customers,total_customer_revenue,average_customer_value,avg_financial_health,financial_health_volatility,avg_net_margin,avg_current_ratio,cash_flow_consistency_percentage::FLOAT, total_risk_score::INTEGER,CASE WHEN total_risk_score>=70 THEN 'Critical Risk' WHEN total_risk_score>=50 THEN 'High Risk' WHEN total_risk_score>=30 THEN 'Medium Risk' ELSE 'Low Risk' END risk_level,CASE WHEN overall_financial_health_score<40 THEN 'Poor Financial Health' WHEN cash_flow_risk_level LIKE '%High Risk%' THEN 'Cash Flow Issues' WHEN overdue_percentage>.3 THEN 'High Receivables Risk' WHEN current_ratio<1 THEN 'Liquidity Concerns' ELSE 'No Major Risk Factors' END primary_risk_factor,CASE WHEN current_ratio>=2 THEN 'Above Target' WHEN current_ratio>=1.5 THEN 'At Target' ELSE 'Below Target' END liquidity_performance,CASE WHEN net_profit_margin>=.15 THEN 'Above Target' WHEN net_profit_margin>=.05 THEN 'At Target' ELSE 'Below Target' END profitability_performance,CASE WHEN return_on_equity>=.15 THEN 'Above Target' WHEN return_on_equity>=.1 THEN 'At Target' ELSE 'Below Target' END roe_performance,CASE WHEN overdue_percentage<=.05 THEN 'Above Target' WHEN overdue_percentage<=.15 THEN 'At Target' ELSE 'Below Target' END collection_performance,'Maintain Current Performance' improvement_recommendation,CASE WHEN overall_financial_health_score>=80 AND total_risk_score<30 THEN 'A+ Excellent' WHEN overall_financial_health_score>=70 AND total_risk_score<50 THEN 'A Good' WHEN overall_financial_health_score>=60 AND total_risk_score<70 THEN 'B Fair' WHEN overall_financial_health_score>=40 THEN 'C Poor' ELSE 'D Critical' END overall_rating,CASE WHEN total_risk_score>=70 THEN 'URGENT: Multiple Critical Risk Factors' WHEN cash_flow_risk_level LIKE '%High Risk%' THEN 'WARNING: Cash Flow Issues' WHEN current_ratio<1 THEN 'ALERT: Liquidity Below Safe Levels' WHEN overdue_percentage>.3 THEN 'CAUTION: High Receivables Risk' ELSE 'Normal Operations' END key_alert,md5(subsidiary_id||'_'||cast(dashboard_date AS VARCHAR)) dashboard_id FROM risk WHERE subsidiary_id IS NOT NULL
```

## gold SQL（仅供定位差异）

S5

```sql
-- Financial Dashboard KPIs
-- Financial dashboard core metrics that provide high-level financial overview and trend analysis
with financial_ratios as (
    select * from intermediate.int_netsuite2__financial_ratios
),

customer_profitability as (
    select * from intermediate.int_netsuite2__customer_profitability
),

cash_flow_analysis as (
    select * from intermediate.int_netsuite2__cash_flow_analysis
),

ar_aging as (
    select * from intermediate.int_netsuite2__ar_aging_analysis
),

-- Summary of core financial indicators
financial_kpis as (
    select 
        fr.subsidiary_id,
        fr.accounting_period_id,
        current_date as dashboard_date,
        
        -- financial ratio indicator
        fr.current_ratio,
        fr.quick_ratio,
        fr.return_on_equity,
        fr.gross_margin_ratio,
        fr.net_profit_margin,
        fr.overall_financial_health_score,
        fr.financial_health_grade,
        
        -- cash flow indicator
        cf.net_cash_flow,
        cf.operating_cash_flow,
        cf.cash_flow_health,
        cf.predicted_next_month_cash_flow,
        cf.cash_flow_risk_level,
        
        -- Accounts Receivable Metrics
        ar.total_ar_amount,
        ar.overdue_amount,
        ar.overdue_percentage,
        ar.weighted_average_days_outstanding,
        
        -- Customer Metrics
        cp_summary.total_customers,
        cp_summary.high_value_customers,
        cp_summary.at_risk_customers,
        cp_summary.total_customer_revenue,
        cp_summary.average_customer_value
        
    from financial_ratios fr
    left join (
        select 
            subsidiary_id,
            analysis_month,
            net_cash_flow,
            operating_cash_flow,
            cash_flow_health,
            predicted_next_month_cash_flow,
            cash_flow_risk_level
        from cash_flow_analysis
        where analysis_month = date_trunc('month', current_date - interval '1 month')
    ) cf on fr.subsidiary_id = cf.subsidiary_id
    left join (
        select 
            subsidiary_id,
            sum(total_ar_amount) as total_ar_amount,
            sum(overdue_amount) as overdue_amount,
            case 
                when sum(total_ar_amount) > 0 
                then sum(overdue_amount) / sum(total_ar_amount)
                else 0 
            end as overdue_percentage,
            avg(weighted_average_days_outstanding) as weighted_average_days_outstanding
        from ar_aging
        group by subsidiary_id
    ) ar on fr.subsidiary_id = ar.subsidiary_id
    left join (
        select 
            subsidiary_id,
            count(*) as total_customers,
            count(case when customer_segment in ('Champion', 'Loyal') then 1 end) as high_value_customers,
            count(case when customer_segment = 'At Risk' or activity_status = 'At Risk' then 1 end) as at_risk_customers,
            sum(total_revenue) as total_customer_revenue,
            avg(total_revenue) as average_customer_value
        from customer_profitability
        group by subsidiary_id
    ) cp_summary on fr.subsidiary_id = cp_summary.subsidiary_id
),

-- trend analysis
financial_trends as (
    select 
        subsidiary_id,
        
        -- Financial Wellness Trends
        avg(overall_financial_health_score) as avg_financial_health,
        stddev(overall_financial_health_score) as financial_health_volatility,
        
        -- Profitability Trends
        avg(net_profit_margin) as avg_net_margin,
        max(net_profit_margin) - min(net_profit_margin) as margin_range,
        
        -- liquidity trends
        avg(current_ratio) as avg_current_ratio,
        min(current_ratio) as min_current_ratio,
        
        -- cash flow trends
        sum(case when cash_flow_health in ('Excellent', 'Good') then 1 else 0 end) as positive_cash_flow_periods,
        count(*) as total_periods,
        
        current_date as trend_analysis_date
        
    from financial_kpis
    group by subsidiary_id
),

-- risk assessment
risk_assessment as (
    select 
        fk.subsidiary_id,
        
        -- Comprehensive risk score (0-100, higher is more dangerous)
        case 
            when fk.overall_financial_health_score < 40 then 30
            when fk.overall_financial_health_score < 60 then 20
            when fk.overall_financial_health_score < 80 then 10
            else 5
        end +
        case 
            when fk.cash_flow_risk_level = 'High Risk - Negative Trend' then 25
            when fk.cash_flow_risk_level like '%High Risk%' then 20
            when fk.cash_flow_risk_level like '%Medium Risk%' then 10
            else 5
        end +
        case 
            when fk.overdue_percentage > 0.3 then 20
            when fk.overdue_percentage > 0.2 then 15
            when fk.overdue_percentage > 0.1 then 10
            else 5
        end +
        case 
            when fk.current_ratio < 1.0 then 25
            when fk.current_ratio < 1.5 then 15
            when fk.current_ratio < 2.0 then 10
            else 5
        end as total_risk_score,
        
        -- risk level
        case 
            when (
                case 
                    when fk.overall_financial_health_score < 40 then 30
                    when fk.overall_financial_health_score < 60 then 20
                    when fk.overall_financial_health_score < 80 then 10
                    else 5
                end +
                case 
                    when fk.cash_flow_risk_level = 'High Risk - Negative Trend' then 25
                    when fk.cash_flow_risk_level like '%High Risk%' then 20
                    when fk.cash_flow_risk_level like '%Medium Risk%' then 10
                    else 5
                end +
                case 
                    when fk.overdue_percentage > 0.3 then 20
                    when fk.overdue_percentage > 0.2 then 15
                    when fk.overdue_percentage > 0.1 then 10
                    else 5
                end +
                case 
                    when fk.current_ratio < 1.0 then 25
                    when fk.current_ratio < 1.5 then 15
                    when fk.current_ratio < 2.0 then 10
                    else 5
                end
            ) >= 70 then 'Critical Risk'
            when (
                case 
                    when fk.overall_financial_health_score < 40 then 30
                    when fk.overall_financial_health_score < 60 then 20
                    when fk.overall_financial_health_score < 80 then 10
                    else 5
                end +
                case 
                    when fk.cash_flow_risk_level = 'High Risk - Negative Trend' then 25
                    when fk.cash_flow_risk_level like '%High Risk%' then 20
                    when fk.cash_flow_risk_level like '%Medium Risk%' then 10
                    else 5
                end +
                case 
                    when fk.overdue_percentage > 0.3 then 20
                    when fk.overdue_percentage > 0.2 then 15
                    when fk.overdue_percentage > 0.1 then 10
                    else 5
                end +
                case 
                    when fk.current_ratio < 1.0 then 25
                    when fk.current_ratio < 1.5 then 15
                    when fk.current_ratio < 2.0 then 10
                    else 5
                end
            ) >= 50 then 'High Risk'
            when (
                case 
                    when fk.overall_financial_health_score < 40 then 30
                    when fk.overall_financial_health_score < 60 then 20
                    when fk.overall_financial_health_score < 80 then 10
                    else 5
                end +
                case 
                    when fk.cash_flow_risk_level = 'High Risk - Negative Trend' then 25
                    when fk.cash_flow_risk_level like '%High Risk%' then 20
                    when fk.cash_flow_risk_level like '%Medium Risk%' then 10
                    else 5
                end +
                case 
                    when fk.overdue_percentage > 0.3 then 20
                    when fk.overdue_percentage > 0.2 then 15
                    when fk.overdue_percentage > 0.1 then 10
                    else 5
                end +
                case 
                    when fk.current_ratio < 1.0 then 25
                    when fk.current_ratio < 1.5 then 15
                    when fk.current_ratio < 2.0 then 10
                    else 5
                end
            ) >= 30 then 'Medium Risk'
            else 'Low Risk'
        end as risk_level,
        
        -- Main risk factors
        case 
            when fk.overall_financial_health_score < 40 then 'Poor Financial Health'
            when fk.cash_flow_risk_level like '%High Risk%' then 'Cash Flow Issues'
            when fk.overdue_percentage > 0.3 then 'High Receivables Risk'
            when fk.current_ratio < 1.0 then 'Liquidity Concerns'
            else 'No Major Risk Factors'
        end as primary_risk_factor,
        
        current_date as risk_assessment_date
        
    from financial_kpis fk
),

-- Performance goals and benchmarks
performance_benchmarks as (
    select 
        fk.subsidiary_id,
        
        -- Set performance targets (industry benchmarks)
        case when fk.current_ratio >= 2.0 then 'Above Target' when fk.current_ratio >= 1.5 then 'At Target' else 'Below Target' end as liquidity_performance,
        case when fk.net_profit_margin >= 0.15 then 'Above Target' when fk.net_profit_margin >= 0.05 then 'At Target' else 'Below Target' end as profitability_performance,
        case when fk.return_on_equity >= 0.15 then 'Above Target' when fk.return_on_equity >= 0.10 then 'At Target' else 'Below Target' end as roe_performance,
        case when fk.overdue_percentage <= 0.05 then 'Above Target' when fk.overdue_percentage <= 0.15 then 'At Target' else 'Below Target' end as collection_performance,
        
        -- Improvement suggestions
        case 
            when fk.current_ratio < 1.5 and fk.net_profit_margin < 0.05 then 'Focus on Operations & Liquidity'
            when fk.current_ratio < 1.5 then 'Improve Working Capital Management'
            when fk.net_profit_margin < 0.05 then 'Review Cost Structure'
            when fk.overdue_percentage > 0.15 then 'Strengthen Collections'
            else 'Maintain Current Performance'
        end as improvement_recommendation,
        
        current_date as benchmark_date
        
    from financial_kpis fk
)

select 
    fk.subsidiary_id,
    fk.accounting_period_id,
    fk.dashboard_date,
    
    -- core financial indicators
    fk.current_ratio,
    fk.quick_ratio,
    fk.return_on_equity,
    fk.gross_margin_ratio,
    fk.net_profit_margin,
    fk.overall_financial_health_score,
    fk.financial_health_grade,
    
    -- cash flow indicator
    fk.net_cash_flow,
    fk.operating_cash_flow,
    fk.cash_flow_health,
    fk.predicted_next_month_cash_flow,
    fk.cash_flow_risk_level,
    
    -- Accounts Receivable Metrics
    fk.total_ar_amount,
    fk.overdue_amount,
    fk.overdue_percentage,
    fk.weighted_average_days_outstanding,
    
    -- Customer Metrics
    fk.total_customers,
    fk.high_value_customers,
    fk.at_risk_customers,
    fk.total_customer_revenue,
    fk.average_customer_value,
    
    -- trend analysis
    ft.avg_financial_health,
    ft.financial_health_volatility,
    ft.avg_net_margin,
    ft.avg_current_ratio,
    case 
        when ft.total_periods > 0 
        then round((ft.positive_cash_flow_periods::float / ft.total_periods) * 100, 1)
        else 0 
    end as cash_flow_consistency_percentage,
    
    -- risk assessment
    ra.total_risk_score,
    ra.risk_level,
    ra.primary_risk_factor,
    
    -- performance benchmark
    pb.liquidity_performance,
    pb.profitability_performance,
    pb.roe_performance,
    pb.collection_performance,
    pb.improvement_recommendation,
    
    -- Overall rating
    case 
        when fk.overall_financial_health_score >= 80 and ra.risk_level = 'Low Risk' then 'A+ Excellent'
        when fk.overall_financial_health_score >= 70 and ra.risk_level in ('Low Risk', 'Medium Risk') then 'A Good'
        when fk.overall_financial_health_score >= 60 and ra.risk_level != 'Critical Risk' then 'B Fair'
        when fk.overall_financial_health_score >= 40 then 'C Poor'
        else 'D Critical'
    end as overall_rating,
    
    -- Key warnings
    case 
        when ra.risk_level = 'Critical Risk' then 'URGENT: Multiple Critical Risk Factors'
        when fk.cash_flow_risk_level like '%High Risk%' then 'WARNING: Cash Flow Issues'
        when fk.current_ratio < 1.0 then 'ALERT: Liquidity Below Safe Levels'
        when fk.overdue_percentage > 0.3 then 'CAUTION: High Receivables Risk'
        else 'Normal Operations'
    end as key_alert,
    
    md5(cast(fk.subsidiary_id as varchar) || '_' || cast(fk.dashboard_date as varchar)) as dashboard_id
    
from financial_kpis fk
left join financial_trends ft on fk.subsidiary_id = ft.subsidiary_id
left join risk_assessment ra on fk.subsidiary_id = ra.subsidiary_id
left join performance_benchmarks pb on fk.subsidiary_id = pb.subsidiary_id
where fk.subsidiary_id is not null
order by ra.total_risk_score desc, fk.overall_financial_health_score desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 13 | 13 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"dashboard_id":"06f0b75ca375760c9c880f75abb235a2"}</code> |
| K2 | <code>{"dashboard_id":"331bc6ee1452474dd883e9ab098e9f75"}</code> |
| K3 | <code>{"dashboard_id":"3b1424e6fd2587ffb91aee06e7eb3ec8"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| dashboard_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| subsidiary_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| accounting_period_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| dashboard_date | 0 | 0 | 0 | DATE | DATE |
| current_ratio | 0 | 0 | 0 | DOUBLE | DOUBLE |
| quick_ratio | 0 | 0 | 0 | DOUBLE | DOUBLE |
| return_on_equity | 0 | 0 | 0 | DOUBLE | DOUBLE |
| gross_margin_ratio | 0 | 0 | 0 | DOUBLE | DOUBLE |
| net_profit_margin | 0 | 0 | 0 | DOUBLE | DOUBLE |
| overall_financial_health_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| financial_health_grade | 0 | 0 | 0 | VARCHAR | VARCHAR |
| net_cash_flow | 0 | 0 | 0 | DOUBLE | DOUBLE |
| operating_cash_flow | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cash_flow_health | 0 | 0 | 0 | VARCHAR | VARCHAR |
| predicted_next_month_cash_flow | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cash_flow_risk_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| total_ar_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| overdue_amount | 0 | 0 | 0 | DOUBLE | DOUBLE |
| overdue_percentage | 0 | 0 | 0 | DOUBLE | DOUBLE |
| weighted_average_days_outstanding | 0 | 0 | 0 | DOUBLE | DOUBLE |
| total_customers | 0 | 0 | 0 | BIGINT | BIGINT |
| high_value_customers | 0 | 0 | 0 | BIGINT | BIGINT |
| at_risk_customers | 0 | 0 | 0 | BIGINT | BIGINT |
| total_customer_revenue | 0 | 0 | 0 | DOUBLE | DOUBLE |
| average_customer_value | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_financial_health | 0 | 0 | 0 | DOUBLE | DOUBLE |
| financial_health_volatility | 13 | 13 | 13 | DOUBLE | DOUBLE |
| avg_net_margin | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_current_ratio | 0 | 0 | 0 | DOUBLE | DOUBLE |
| risk_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| primary_risk_factor | 0 | 0 | 0 | VARCHAR | VARCHAR |
| liquidity_performance | 0 | 0 | 0 | VARCHAR | VARCHAR |
| profitability_performance | 0 | 0 | 0 | VARCHAR | VARCHAR |
| roe_performance | 0 | 0 | 0 | VARCHAR | VARCHAR |
| collection_performance | 0 | 0 | 0 | VARCHAR | VARCHAR |
| improvement_recommendation | 0 | 0 | 0 | VARCHAR | VARCHAR |
| overall_rating | 0 | 0 | 0 | VARCHAR | VARCHAR |
| key_alert | 0 | 0 | 0 | VARCHAR | VARCHAR |

financial_health_volatility 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.0 | null |
| K2 | 0.0 | null |
| K3 | 0.0 | null |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>16列；[{"column":"current_ratio","table_rows":7},{"column":"quick_ratio","table_rows":7},{"column":"return_on_equity","table_rows":7}]</code> |
| A3_constant_nonnull_column | <code>17列；[{"column":"accounting_period_id","value":"NET26632601180"},{"column":"dashboard_date","value":"2026-10-25"},{"column":"overall_financial_health_score","value":"0.0"}]</code> |
| A4_equal_columns | <code>4组；[{"columns":["overall_financial_health_score","avg_financial_health","financial_health_volatility","CAST(cash_flow_consistency_percentage AS FLOAT)"],"nonnull_equal_rows":7,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["total_customers","high_value_customers"],"nonnull_equal_rows":3,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["total_customer_revenue","average_customer_value"],"nonnull_equal_rows":3,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>4组；[{"columns":["overall_financial_health_score","avg_financial_health","financial_health_volatility","CAST(cash_flow_consistency_percentage AS FLOAT)"],"nonnull_equal_rows":7,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["total_customers","high_value_customers"],"nonnull_equal_rows":3,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["total_customer_revenue","average_customer_value"],"nonnull_equal_rows":3,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"improvement_recommendation","expression":["'Maintain Current Performance'"]}]</code> |
| C9_agent_runtime_text | <code>S4:1 current_date；命中数=2</code> |
| C9_gold_runtime_text | <code>S5:24 current_date；命中数=5</code> |
| C9_contract_runtime_text | <code>S3:2878 current_date；命中数=3</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory 2026-10-25 02:32:19,445 - WARNING - Skipping netsuite2_financial_dashboard: SQL file does not exist (sql/marts/netsuite2_financial_dashboard.sql)</code> |

## 轨迹索引（不放输出原文）

本题事件总数：67；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f &#124; sort &#124; wc -l; find sql -type f &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,220p' run.py</code> | 16959 | true | false |
| 19 | run | <code>cat &gt;&gt; /tmp/inter.py &lt;&lt;'PY'<br>models2={<br>'int_netsuite2__customer_profitability':'''WITH tx AS (SELECT t.*, l.entity_id AS customer_id, 'Customer_'&#124;&#124;left(l.entity_id,8) AS customer_name, 'customer_'&#124;&#124;lef</code> | 0 | false | false |
| 21 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -80 /tmp/runlog</code> | 8156 | true | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_netsuite2__consolidated_exchange_rates.sql');s=p.read_text().replace('raw.netsuite2_exchange_rate_data','raw.netsuite2_consolidated_exc</code> | 0 | false | false |
| 27 | run | <code>cat &gt;&gt; /tmp/more.py &lt;&lt;'PY'<br>(p/'int_netsuite2__cash_flow_forecasting.sql').write_text("""WITH hist AS (SELECT * FROM intermediate.int_netsuite2__cash_flow_analysis WHERE analysis_month&gt;=date_trunc('mon</code> | 0 | false | false |
| 29 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>m=Path('sql/marts')<br>passmodels={'netsuite2_balance_sheet':'intermediate.int_netsuite2__balance_sheet','netsuite2_income_statement':'intermediate.int</code> | 0 | false | false |
| 33 | run | <code>cat sql/intermediate/int_netsuite2__data_quality_metrics.sql; sed -n '1,60p' sql/intermediate/int_netsuite2__cash_flow_forecasting.sql</code> | 7098 | false | false |
| 35 | run | <code>find sql/intermediate -type f -printf '%f\n' &#124; sort; grep 'ERROR - ✗' /tmp/runlog2</code> | 1304 | false | false |
| 39 | run | <code>cat &gt; /tmp/marts_more.py &lt;&lt;'PY'<br>from pathlib import Path<br>m=Path('sql/marts')<br>for name,src in [('netsuite__transaction_details','staging.stg_netsuite__transaction_lines'),('netsuite__transaction_detail</code> | 817 | false | false |
| 51 | run | <code>cat sql/intermediate/int_netsuite2__transaction_lines.sql; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('netsuite.duckdb',read_only=True)<br>for t in ['stg_netsuite2__transaction_lines','int_netsuite2_</code> | 7032 | false | false |

### agent action 的 thought/message 命中原句

event 39 / message

```text
(m/'netsuite2_financial_dashboard.sql').write_text("""WITH cf AS (SELECT * FROM intermediate.int_netsuite2__cash_flow_analysis WHERE analysis_month=date_trunc('month',current_date-interval '1 month')), ar AS (SELECT subsidiary_id,sum(total_ar_amount) total_ar_amount,sum(overdue_amount) overdue_amount,sum(overdue_amount)/nullif(sum(total_ar_amount),0) overdue_percentage,avg(weighted_average_days_outstanding) weighted_average_days_outstanding FROM intermediate.int_netsuite2__ar_aging_analysis GROUP BY subsidiary_id), cp AS (SELECT subsidiary_id,count(*) total_customers,count(*) FILTER(WHERE customer_segment IN ('Champion','Loyal')) high_value_customers,count(*) FILTER(WHERE customer_segment='At Risk' OR activity_status='At Risk') at_risk_customers,sum(total_revenue) total_customer_revenue,avg(total_revenue) average_customer_value FROM intermediate.int_netsuite2__customer_profitability GROUP BY subsidiary_id), base AS (SELECT fr.*,current_date dashboard_date,cf.net_cash_flow,cf.operating_cash_flow,cf.cash_flow_health,cf.predicted_next_month_cash_flow,cf.cash_flow_risk_level,ar.total_ar_amount,ar.overdue_amount,ar.overdue_percentage,ar.weighted_average_days_outstanding,cp.total_customers,cp.high_value_customers,cp.at_risk_customers,cp.total_customer_revenue,cp.average_customer_value FROM intermediate.int_netsuite2__financial_ratios fr LEFT JOIN cf USING(subsidiary_id) LEFT JOIN ar USING(subsidiary_id) LEFT JOIN cp USING(subsidiary_id)), trends AS (SELECT *,overall_financial_health_score avg_financial_health,overall_financial_health_score*0 financial_health_volatility,net_profit_margin avg_net_margin,current_ratio avg_current_ratio,CASE WHEN cash_flow_health IN ('Excellent','Good') THEN 100.0 ELSE 0 END cash_flow_consistency_percentage FROM base), risk AS (SELECT *,CASE WHEN overall_financial_health_score<40 THEN 30 WHEN overall_financial_health_score<60 THEN 20 WHEN overall_financial_health_score<80 THEN 10 ELSE 5 END + CASE WHEN cash_flow_risk_level='High Risk - Negative Trend' THEN 25 WHEN cash_flow_risk_level LIKE '%High Risk%' THEN 20 WHEN cash_flow_risk_level LIKE '%Medium Risk%' THEN 10 ELSE 5 END + CASE WHEN overdue_percentage>.30 THEN 20 WHEN overdue_percentage>.20 THEN 15 WHEN overdue_percentage>.10 THEN 10 ELSE 5 END + CASE WHEN current_ratio<1 THEN 25 WHEN current_ratio<1.5 THEN 15 WHEN current_ratio<2 THEN 10 ELSE 5 END total_risk_score FROM trends) SELECT subsidiary_id,accounting_period_id,dashboard_date,current_ratio,quick_ratio,return_on_equity,gross_margin_ratio,net_profit_margin,overall_financial_health_score,financial_health_grade,net_cash_flow,operating_cash_flow,cash_flow_health,predicted_next_month_cash_flow,cash_flow_risk_level,total_ar_amount,overdue_amount,overdue_percentage,weighted_average_days_outstanding,total_customers,high_value_customers,at_risk_customers,total_customer_revenue,average_customer_value,avg_financial_health,financial_health_volatility,avg_net_margin,avg_current_ratio,cash_flow_consistency_percentage::FLOAT, total_risk_score::INTEGER,CASE WHEN total_risk_score>=70 THEN 'Critical Risk' WHEN total_risk_score>=50 THEN 'High Risk' WHEN total_risk_score>=30 THEN 'Medium Risk' ELSE 'Low Risk' END risk_level,CASE WHEN overall_financial_health_score<40 THEN 'Poor Financial Health' WHEN cash_flow_risk_level LIKE '%High Risk%' THEN 'Cash Flow Issues' WHEN overdue_percentage>.3 THEN 'High Receivables Risk' WHEN current_ratio<1 THEN 'Liquidity Concerns' ELSE 'No Major Risk Factors' END primary_risk_factor,CASE WHEN current_ratio>=2 THEN 'Above Target' WHEN current_ratio>=1.5 THEN 'At Target' ELSE 'Below Target' END liquidity_performance,CASE WHEN net_profit_margin>=.15 THEN 'Above Target' WHEN net_profit_margin>=.05 THEN 'At Target' ELSE 'Below Target' END profitability_performance,CASE WHEN return_on_equity>=.15 THEN 'Above Target' WHEN return_on_equity>=.1 THEN 'At Target' ELSE 'Below Target' END roe_performance,CASE WHEN overdue_percentage<=.05 THEN 'Above Target' WHEN overdue_percentage<=.15 THEN 'At Target' ELSE 'Below Target' END collection_performance,'Maintain Current Performance' improvement_recommendation,CASE WHEN overall_financial_health_score>=80 AND total_risk_score<30 THEN 'A+ Excellent' WHEN overall_financial_health_score>=70 AND total_risk_score<50 THEN 'A Good' WHEN overall_financial_health_score>=60 AND total_risk_score<70 THEN 'B Fair' WHEN overall_financial_health_score>=40 THEN 'C Poor' ELSE 'D Critical' END overall_rating,CASE WHEN total_risk_score>=70 THEN 'URGENT: Multiple Critical Risk Factors' WHEN cash_flow_risk_level LIKE '%High Risk%' THEN 'WARNING: Cash Flow Issues' WHEN current_ratio<1 THEN 'ALERT: Liquidity Below Safe Levels' WHEN overdue_percentage>.3 THEN 'CAUTION: High Receivables Risk' ELSE 'Normal Operations' END key_alert,md5(subsidiary_id||'_'||cast(dashboard_date AS VARCHAR)) dashboard_id FROM risk WHERE subsidiary_id IS NOT NULL""")
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-013.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_financial_dashboard.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/marts/netsuite2_financial_dashboard.sql`
- S6: `records/006_contract_impl-013.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/result.md`
- S10: `data/022_packages_work/022_impl-013_netsuite2_financial_dashboard/022_impl-013_netsuite2_financial_dashboard.json`
- S11: `data/011_agent_alignment/impl-013/netsuite2_financial_dashboard_2025-10-14.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions`
