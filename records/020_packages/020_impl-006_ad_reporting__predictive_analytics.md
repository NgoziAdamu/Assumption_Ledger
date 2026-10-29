# impl-006 | marts | ad_reporting__predictive_analytics | 差异：S1；日期 原记录

## 契约完整原文

S3:4040–4139

```yaml
    - name: ad_reporting__predictive_analytics
      description: Predictive analytics per platform-month with trend analysis, forecasts, risk/confidence scoring, and strategy recommendations over the last 6 months
      grain: One row per platform per performance_month (months within last 6 months)
      source_models:
      - intermediate.int_ad_reporting__unified_campaign_metrics (platform, date_day, cost, impressions, clicks, conversions, revenue_30d, click_through_rate, cost_per_click, return_on_ad_spend, campaign_id, lifecycle_stage)
      business_logic: '- Build the baseline from unified campaign metrics limited to the last 12 months. - Group by platform and the calendar month of date_day; compute monthly totals (spend, impressions, clicks, conversions, 30-day revenue) and monthly averages (CTR rounded to 4 decimals, CPC rounded to 2, ROAS rounded to 4); all aggregations ignore NULLs. - Count distinct campaigns: active (all), new (lifecycle LAUNCH), and established (lifecycle ESTABLISHED); NULL campaign IDs are excluded. - Compute volatility as the standard deviation of CTR and CPC within each platform-month; if fewer than two non-NULL observations, volatility is NULL. - Per platform, order months chronologically to derive: - Month-over-month spend growth: percent change from the prior month (rounded to 2 decimals); if the prior value is not positive, set to 0. - Month-over-month CTR change: percent change from the prior month (rounded to 2 decimals); if the prior value is not positive, set to 0. - 3-month rolling averages for spend, CTR, and ROAS using the current month and two preceding months. - Spend momentum: ACCELERATING if current spend is >10% above prior month, DECELERATING if >10% below, otherwise STABLE; if no prior month, STABLE. - CTR momentum: IMPROVING if current CTR is >5% above prior month, DECLINING if >5% below, otherwise STABLE; if no prior month, STABLE. - Predictions: - Next-month spend: 3-month spend average scaled by 1.15 when accelerating, 0.85 when decelerating, otherwise unchanged. - Next-month CTR: 3-month CTR average scaled by 1.10 when improving, 0.90 when declining, otherwise unchanged. - Risk level: HIGH_RISK when CTR volatility > 0.5 and MoM spend growth > 50%; MEDIUM_RISK when CTR volatility > 0.3 or absolute MoM spend growth > 25%; otherwise LOW_RISK. - Anomaly probability: 35 when CTR volatility > 1.0 or CPC volatility > 2.0; 20 when CTR volatility > 0.5 or CPC volatility > 1.0; 25 when absolute MoM spend growth > 50%; otherwise 10. - Confidence: HIGH_CONFIDENCE when absolute MoM spend growth < 10% and CTR volatility < 0.3; MEDIUM_CONFIDENCE when absolute MoM spend growth < 25% and CTR volatility < 0.5; otherwise LOW_CONFIDENCE. - Final output per platform-month: - Baselines: current_monthly_spend, current_avg_ctr, current_avg_cpc, current_avg_roas from the monthly aggregates. - Budget recommendation: increase if accelerating and ROAS ≥ 2.0; decrease if decelerating or ROAS < 1.0; otherwise maintain. - Predicted ROAS: +10% when ROAS ≥ 2.5 and CTR momentum improving; −10% when ROAS < 1.5 and CTR momentum declining; otherwise unchanged. - Risk mitigation and strategic recommendation are set to the exact strings defined by the CASE rules. - Revenue scenarios: expected revenue at current ROAS = predicted spend × current avg ROAS; optimized = predicted spend × predicted ROAS; incremental = predicted spend × (predicted ROAS − current avg ROAS). - Success probability: VERY_HIGH when confidence is HIGH and risk is LOW; HIGH when confidence is HIGH/MEDIUM and risk is not HIGH; MEDIUM when confidence is MEDIUM; otherwise LOW. - Metadata: generated timestamp at query run, base date is today, target date is 30 days after the base date. - Filter to months within the last six months; results are ordered by platform ascending and performance month descending.'
      columns:
      - name: platform
        data_type: VARCHAR
        description: Ad platform identifier; one row per platform-month
      - name: performance_month
        data_type: DATE
        description: Calendar month derived from date_day for the performance period
      - name: current_monthly_spend
        data_type: DOUBLE
        description: Total spend for the platform-month; ignores NULLs; no rounding applied
      - name: current_avg_ctr
        data_type: DOUBLE
        description: Average CTR for the month rounded to 4 decimals; NULLs ignored
      - name: current_avg_cpc
        data_type: DOUBLE
        description: Average CPC for the month rounded to 2 decimals; NULLs ignored
      - name: current_avg_roas
        data_type: DOUBLE
        description: Average ROAS for the month rounded to 4 decimals; NULLs ignored
      - name: mom_spend_growth
        data_type: DOUBLE
        description: Percent change vs prior month spend, rounded to 2 decimals; returns 0 if prior is not positive
      - name: mom_ctr_change
        data_type: DOUBLE
        description: Percent change vs prior month average CTR, rounded to 2 decimals; returns 0 if prior is not positive
      - name: spend_momentum
        data_type: VARCHAR
        description: ACCELERATING if spend >10% above prior month; DECELERATING if >10% below; else STABLE; no prior yields STABLE
      - name: ctr_momentum
        data_type: VARCHAR
        description: IMPROVING if average CTR >5% above prior; DECLINING if >5% below; else STABLE; no prior yields STABLE
      - name: predicted_next_month_spend
        data_type: DOUBLE
        description: 3-month spend average scaled by momentum (1.15 if accelerating, 0.85 if decelerating; else unchanged)
      - name: predicted_next_month_ctr
        data_type: DOUBLE
        description: 3-month CTR average scaled by momentum (1.10 if improving, 0.90 if declining; else unchanged)
      - name: budget_recommendation
        data_type: VARCHAR
        description: INCREASE_BUDGET if accelerating and ROAS ≥ 2.0; DECREASE_BUDGET if decelerating or ROAS < 1.0; else MAINTAIN_BUDGET
      - name: predicted_roas
        data_type: DOUBLE
        description: ROAS +10% when ROAS ≥ 2.5 and CTR momentum improving; −10% when ROAS < 1.5 and CTR momentum declining; else unchanged
      - name: forecast_risk_level
        data_type: VARCHAR
        description: HIGH_RISK if CTR volatility > 0.5 and MoM spend growth > 50%; MEDIUM_RISK if CTR volatility > 0.3 or absolute MoM spend growth > 25%; else LOW_RISK
      - name: anomaly_probability_next_month
        data_type: INTEGER
        description: 'Probability bucket: 35 when CTR volatility > 1.0 or CPC volatility > 2.0; 20 when CTR volatility > 0.5 or CPC volatility > 1.0; 25 when absolute MoM spend growth > 50%; else 10'
      - name: forecast_confidence
        data_type: VARCHAR
        description: HIGH_CONFIDENCE if absolute MoM spend growth < 10% and CTR volatility < 0.3; MEDIUM_CONFIDENCE if absolute MoM spend growth < 25% and CTR volatility < 0.5; else LOW_CONFIDENCE
      - name: ctr_volatility
        data_type: DOUBLE
        description: Standard deviation of CTR within the platform-month; NULL if fewer than two non-NULL observations
      - name: cpc_volatility
        data_type: DOUBLE
        description: Standard deviation of CPC within the platform-month; NULL if fewer than two non-NULL observations
      - name: active_campaigns
        data_type: BIGINT
        description: Distinct count of campaigns active in the platform-month; NULLs excluded
      - name: new_campaigns
        data_type: BIGINT
        description: Distinct count of campaigns with lifecycle_stage LAUNCH in the month; NULLs excluded
      - name: established_campaigns
        data_type: BIGINT
        description: Distinct count of campaigns with lifecycle_stage ESTABLISHED in the month; NULLs excluded
      - name: risk_mitigation_plan
        data_type: VARCHAR
        description: Daily monitoring/manual oversight for HIGH_RISK; weekly reviews/alerts/backup strategies when anomaly probability > 20; else standard monitoring
      - name: strategic_recommendation
        data_type: VARCHAR
        description: Strategy label combining budget recommendation, risk, ROAS, CTR momentum, and anomaly risk; strings exactly as defined
      - name: expected_revenue_current_performance
        data_type: DOUBLE
        description: Predicted spend × current average ROAS
      - name: expected_revenue_optimized_performance
        data_type: DOUBLE
        description: Predicted spend × predicted ROAS
      - name: incremental_revenue_opportunity
        data_type: DOUBLE
        description: Predicted spend × (predicted ROAS − current average ROAS)
      - name: prediction_success_probability
        data_type: VARCHAR
        description: VERY_HIGH when confidence is HIGH and risk is LOW; HIGH when confidence HIGH/MEDIUM and risk not HIGH; MEDIUM when confidence MEDIUM; else LOW
      - name: forecast_generated_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Timestamp when the query runs (timezone-aware)
      - name: forecast_base_date
        data_type: DATE
        description: Date when the query runs
      - name: forecast_target_date
        data_type: TIMESTAMP
        description: Target timestamp 30 days after the base date
```

## agent 最终 SQL

S4

```sql
SELECT
    NULL::VARCHAR AS "platform",
    NULL::DATE AS "performance_month",
    NULL::DOUBLE AS "current_monthly_spend",
    NULL::DOUBLE AS "current_avg_ctr",
    NULL::DOUBLE AS "current_avg_cpc",
    NULL::DOUBLE AS "current_avg_roas",
    NULL::DOUBLE AS "mom_spend_growth",
    NULL::DOUBLE AS "mom_ctr_change",
    NULL::VARCHAR AS "spend_momentum",
    NULL::VARCHAR AS "ctr_momentum",
    NULL::DOUBLE AS "predicted_next_month_spend",
    NULL::DOUBLE AS "predicted_next_month_ctr",
    NULL::VARCHAR AS "budget_recommendation",
    NULL::DOUBLE AS "predicted_roas",
    NULL::VARCHAR AS "forecast_risk_level",
    NULL::INTEGER AS "anomaly_probability_next_month",
    NULL::VARCHAR AS "forecast_confidence",
    NULL::DOUBLE AS "ctr_volatility",
    NULL::DOUBLE AS "cpc_volatility",
    NULL::BIGINT AS "active_campaigns",
    NULL::BIGINT AS "new_campaigns",
    NULL::BIGINT AS "established_campaigns",
    NULL::VARCHAR AS "risk_mitigation_plan",
    NULL::VARCHAR AS "strategic_recommendation",
    NULL::DOUBLE AS "expected_revenue_current_performance",
    NULL::DOUBLE AS "expected_revenue_optimized_performance",
    NULL::DOUBLE AS "incremental_revenue_opportunity",
    NULL::VARCHAR AS "prediction_success_probability",
    NULL::TIMESTAMP WITH TIME ZONE AS "forecast_generated_at",
    NULL::DATE AS "forecast_base_date",
    NULL::TIMESTAMP AS "forecast_target_date"
FROM intermediate.int_ad_reporting__unified_campaign_metrics
```

## gold SQL（仅供定位差异）

S5

```sql
-- Predictive Analytics Report (Simplified)
-- Basic forecasting and predictive insights based on unified campaign metrics
-- Provides trend analysis and performance predictions

WITH performance_baseline AS (
    -- Calculate baseline performance metrics from unified campaign data
    SELECT 
        platform,
        DATE_TRUNC('month', date_day) AS performance_month,
        
        -- Monthly aggregated metrics
        SUM(cost) AS monthly_spend,
        SUM(impressions) AS monthly_impressions,
        SUM(clicks) AS monthly_clicks,
        SUM(conversions) AS monthly_conversions,
        SUM(revenue_30d) AS monthly_revenue,
        
        -- Monthly performance KPIs
        ROUND(AVG(click_through_rate), 4) AS avg_ctr,
        ROUND(AVG(cost_per_click), 2) AS avg_cpc,
        ROUND(AVG(return_on_ad_spend), 4) AS avg_roas,
        
        -- Campaign diversity
        COUNT(DISTINCT campaign_id) AS active_campaigns,
        COUNT(DISTINCT CASE WHEN lifecycle_stage = 'LAUNCH' THEN campaign_id END) AS new_campaigns,
        COUNT(DISTINCT CASE WHEN lifecycle_stage = 'ESTABLISHED' THEN campaign_id END) AS established_campaigns,
        
        -- Performance distribution
        STDDEV(click_through_rate) AS ctr_volatility,
        STDDEV(cost_per_click) AS cpc_volatility
        
    FROM intermediate.int_ad_reporting__unified_campaign_metrics
    WHERE date_day >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY platform, DATE_TRUNC('month', date_day)
),

trend_analysis AS (
    -- Analyze trends and generate predictions
    SELECT 
        *,
        -- Month-over-month growth rates
        CASE 
            WHEN LAG(monthly_spend) OVER (PARTITION BY platform ORDER BY performance_month) > 0
            THEN ROUND(((monthly_spend - LAG(monthly_spend) OVER (PARTITION BY platform ORDER BY performance_month)) / 
                  LAG(monthly_spend) OVER (PARTITION BY platform ORDER BY performance_month)) * 100, 2)
            ELSE 0
        END AS mom_spend_growth,
        
        CASE 
            WHEN LAG(avg_ctr) OVER (PARTITION BY platform ORDER BY performance_month) > 0
            THEN ROUND(((avg_ctr - LAG(avg_ctr) OVER (PARTITION BY platform ORDER BY performance_month)) / 
                  LAG(avg_ctr) OVER (PARTITION BY platform ORDER BY performance_month)) * 100, 2)
            ELSE 0
        END AS mom_ctr_change,
        
        -- 3-month rolling averages for stability
        AVG(monthly_spend) OVER (
            PARTITION BY platform 
            ORDER BY performance_month 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS spend_3m_avg,
        
        AVG(avg_ctr) OVER (
            PARTITION BY platform 
            ORDER BY performance_month 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS ctr_3m_avg,
        
        AVG(avg_roas) OVER (
            PARTITION BY platform 
            ORDER BY performance_month 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS roas_3m_avg,
        
        -- Performance momentum
        CASE 
            WHEN monthly_spend > LAG(monthly_spend, 1) OVER (PARTITION BY platform ORDER BY performance_month) * 1.1 THEN 'ACCELERATING'
            WHEN monthly_spend < LAG(monthly_spend, 1) OVER (PARTITION BY platform ORDER BY performance_month) * 0.9 THEN 'DECELERATING'
            ELSE 'STABLE'
        END AS spend_momentum,
        
        CASE 
            WHEN avg_ctr > LAG(avg_ctr, 1) OVER (PARTITION BY platform ORDER BY performance_month) * 1.05 THEN 'IMPROVING'
            WHEN avg_ctr < LAG(avg_ctr, 1) OVER (PARTITION BY platform ORDER BY performance_month) * 0.95 THEN 'DECLINING'
            ELSE 'STABLE'
        END AS ctr_momentum
        
    FROM performance_baseline
),

predictions AS (
    -- Generate predictions based on trends
    SELECT 
        *,
        -- Simple trend-based forecasts (next month)
        CASE 
            WHEN spend_momentum = 'ACCELERATING' THEN spend_3m_avg * 1.15
            WHEN spend_momentum = 'DECELERATING' THEN spend_3m_avg * 0.85
            ELSE spend_3m_avg
        END AS predicted_next_month_spend,
        
        CASE 
            WHEN ctr_momentum = 'IMPROVING' THEN ctr_3m_avg * 1.10
            WHEN ctr_momentum = 'DECLINING' THEN ctr_3m_avg * 0.90
            ELSE ctr_3m_avg
        END AS predicted_next_month_ctr,
        
        -- Risk assessment
        CASE 
            WHEN ctr_volatility > 0.5 AND mom_spend_growth > 50 THEN 'HIGH_RISK'
            WHEN ctr_volatility > 0.3 OR ABS(mom_spend_growth) > 25 THEN 'MEDIUM_RISK'
            ELSE 'LOW_RISK'
        END AS forecast_risk_level,
        
        -- Anomaly probability
        CASE 
            WHEN ctr_volatility > 1.0 OR cpc_volatility > 2.0 THEN 35
            WHEN ctr_volatility > 0.5 OR cpc_volatility > 1.0 THEN 20
            WHEN ABS(mom_spend_growth) > 50 THEN 25
            ELSE 10
        END AS anomaly_probability_next_month,
        
        -- Confidence level
        CASE 
            WHEN ABS(mom_spend_growth) < 10 AND ctr_volatility < 0.3 THEN 'HIGH_CONFIDENCE'
            WHEN ABS(mom_spend_growth) < 25 AND ctr_volatility < 0.5 THEN 'MEDIUM_CONFIDENCE'
            ELSE 'LOW_CONFIDENCE'
        END AS forecast_confidence
        
    FROM trend_analysis
)

-- Final predictive analytics output
SELECT 
    -- Platform identification
    platform,
    performance_month,
    
    -- Current performance baseline
    monthly_spend AS current_monthly_spend,
    avg_ctr AS current_avg_ctr,
    avg_cpc AS current_avg_cpc,
    avg_roas AS current_avg_roas,
    
    -- Trend indicators
    mom_spend_growth,
    mom_ctr_change,
    spend_momentum,
    ctr_momentum,
    
    -- Forecasts
    predicted_next_month_spend,
    predicted_next_month_ctr,
    
    -- Budget recommendations
    CASE 
        WHEN spend_momentum = 'ACCELERATING' AND avg_roas >= 2.0 THEN 'INCREASE_BUDGET'
        WHEN spend_momentum = 'DECELERATING' OR avg_roas < 1.0 THEN 'DECREASE_BUDGET'
        ELSE 'MAINTAIN_BUDGET'
    END AS budget_recommendation,
    
    -- Performance predictions
    CASE 
        WHEN avg_roas >= 2.5 AND ctr_momentum = 'IMPROVING' THEN avg_roas * 1.1
        WHEN avg_roas < 1.5 AND ctr_momentum = 'DECLINING' THEN avg_roas * 0.9
        ELSE avg_roas
    END AS predicted_roas,
    
    -- Risk assessment
    forecast_risk_level,
    anomaly_probability_next_month,
    forecast_confidence,
    
    -- Volatility indicators
    ctr_volatility,
    cpc_volatility,
    
    -- Campaign insights
    active_campaigns,
    new_campaigns,
    established_campaigns,
    
    -- Strategic recommendations
    CASE 
        WHEN forecast_risk_level = 'HIGH_RISK' 
        THEN 'Implement daily monitoring, reduce bid automation, increase manual oversight'
        WHEN anomaly_probability_next_month > 20
        THEN 'Weekly performance reviews, alert thresholds, backup campaign strategies'
        ELSE 'Standard monitoring protocols'
    END AS risk_mitigation_plan,
    
    CASE 
        WHEN budget_recommendation = 'INCREASE_BUDGET' AND forecast_risk_level = 'LOW_RISK' 
        THEN 'SCALE: Low risk, strong performance - increase investment'
        WHEN budget_recommendation = 'INCREASE_BUDGET' AND forecast_risk_level = 'HIGH_RISK'
        THEN 'CAUTIOUS_GROWTH: Monitor closely while scaling'
        WHEN avg_roas < 1.5 AND ctr_momentum = 'DECLINING'
        THEN 'OPTIMIZE_FIRST: Improve performance before scaling'
        WHEN anomaly_probability_next_month > 25
        THEN 'MONITOR_CLOSELY: High anomaly risk predicted'
        ELSE 'MAINTAIN: Continue current strategy'
    END AS strategic_recommendation,
    
    -- Investment scenarios
    predicted_next_month_spend * current_avg_roas AS expected_revenue_current_performance,
    predicted_next_month_spend * predicted_roas AS expected_revenue_optimized_performance,
    predicted_next_month_spend * (predicted_roas - current_avg_roas) AS incremental_revenue_opportunity,
    
    -- Success probability
    CASE 
        WHEN forecast_confidence = 'HIGH_CONFIDENCE' AND forecast_risk_level = 'LOW_RISK' THEN 'VERY_HIGH'
        WHEN forecast_confidence IN ('HIGH_CONFIDENCE', 'MEDIUM_CONFIDENCE') AND forecast_risk_level != 'HIGH_RISK' THEN 'HIGH'
        WHEN forecast_confidence = 'MEDIUM_CONFIDENCE' THEN 'MEDIUM'
        ELSE 'LOW'
    END AS prediction_success_probability,
    
    -- Analysis metadata
    CURRENT_TIMESTAMP AS forecast_generated_at,
    CURRENT_DATE AS forecast_base_date,
    CURRENT_DATE + INTERVAL '30 days' AS forecast_target_date

FROM predictions
WHERE performance_month >= CURRENT_DATE - INTERVAL '6 months'
ORDER BY platform, performance_month DESC
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1474 | 0 | 1 | 0 | 1 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| performance_month | 0 | 0 | 0 | DATE | DATE |
| current_monthly_spend | 0 | 0 | 0 | DOUBLE | DOUBLE |
| current_avg_ctr | 0 | 0 | 0 | DOUBLE | DOUBLE |
| current_avg_cpc | 0 | 0 | 0 | DOUBLE | DOUBLE |
| current_avg_roas | 0 | 0 | 0 | DOUBLE | DOUBLE |
| mom_spend_growth | 0 | 0 | 0 | DOUBLE | DOUBLE |
| mom_ctr_change | 0 | 0 | 0 | DOUBLE | DOUBLE |
| spend_momentum | 0 | 0 | 0 | VARCHAR | VARCHAR |
| ctr_momentum | 0 | 0 | 0 | VARCHAR | VARCHAR |
| predicted_next_month_spend | 0 | 0 | 0 | DOUBLE | DOUBLE |
| predicted_next_month_ctr | 0 | 0 | 0 | DOUBLE | DOUBLE |
| budget_recommendation | 0 | 0 | 0 | VARCHAR | VARCHAR |
| predicted_roas | 0 | 0 | 0 | DOUBLE | DOUBLE |
| forecast_risk_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| anomaly_probability_next_month | 0 | 0 | 0 | INTEGER | INTEGER |
| forecast_confidence | 0 | 0 | 0 | VARCHAR | VARCHAR |
| ctr_volatility | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cpc_volatility | 0 | 0 | 0 | DOUBLE | DOUBLE |
| active_campaigns | 0 | 0 | 0 | BIGINT | BIGINT |
| new_campaigns | 0 | 0 | 0 | BIGINT | BIGINT |
| established_campaigns | 0 | 0 | 0 | BIGINT | BIGINT |
| risk_mitigation_plan | 0 | 0 | 0 | VARCHAR | VARCHAR |
| strategic_recommendation | 0 | 0 | 0 | VARCHAR | VARCHAR |
| expected_revenue_current_performance | 0 | 0 | 0 | DOUBLE | DOUBLE |
| expected_revenue_optimized_performance | 0 | 0 | 0 | DOUBLE | DOUBLE |
| incremental_revenue_opportunity | 0 | 0 | 0 | DOUBLE | DOUBLE |
| prediction_success_probability | 0 | 0 | 0 | VARCHAR | VARCHAR |
| forecast_generated_at | 0 | 0 | 0 | TIMESTAMP WITH TIME ZONE | TIMESTAMP WITH TIME ZONE |
| forecast_base_date | 0 | 0 | 0 | DATE | DATE |
| forecast_target_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"platform":null}]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A1_zero_rows | 行数=0 |
| B5_null_literal_output | <code>31输出列；[{"column":"platform","expression":["CAST(NULL AS TEXT)"]},{"column":"performance_month","expression":["CAST(NULL AS DATE)"]},{"column":"current_monthly_spend","expression":["CAST(NULL AS DOUBLE)"]}]</code> |
| B7_specified_not_read | <code>["intermediate.int_ad_reporting__unified_campaign_metrics (platform, date_day, cost, impressions, clicks, conversions, revenue_30d, click_through_rate, cost_per_click, return_on_ad_spend, campaign_id, lifecycle_stage)"]</code> |
| B8_shared_single_source | <code>唯一源=intermediate.int_ad_reporting__unified_campaign_metrics；目标数=2；例=["marts.ad_reporting__executive_dashboard","marts.ad_reporting__predictive_analytics"]</code> |
| C9_gold_runtime_text | <code>S5:33 CURRENT_DATE；命中数=5</code> |
| C9_contract_runtime_text | <code>S3:4045 today；命中数=1</code> |

## 轨迹索引（不放输出原文）

本题事件总数：99；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort &amp;&amp; cat config/layer_dependencies.yaml</code> | 7365 | true | false |
| 23 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>import yaml,re,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))['modeling_spec']<br># output schema<br><br>def parse_src(s):<br> x=s.split('.')[-1]<br> if x.startswith('int_'): return</code> | 0 | false | false |
| 25 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 8424 | true | false |
| 29 | run | <code>python run.py &gt; /tmp/runlog2 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete&#124;ERROR - Failed&#124;Binder Error&#124;Catalog Error' /tmp/runlog2</code> | 1956 | true | false |
| 31 | run | <code>cat sql/intermediate/int_ad_reporting__time_series_analytics.sql &#124; head -20; head -35 sql/marts/ad_reporting__predictive_analytics.sql; head -20 sql/staging/stg_google_ads__account_report.sql</code> | 3170 | false | false |
| 33 | run | <code>grep -n 'FROM\&#124;JOIN' sql/intermediate/int_ad_reporting__time_series_analytics.sql sql/marts/ad_reporting__predictive_analytics.sql</code> | 466 | true | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> # only raw source casts rather than casts of computed values; make raw conversions tole</code> | 0 | false | false |
| 37 | run | <code>python run.py &gt; /tmp/runlog3 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog3;</code> | 6937 | true | false |
| 43 | run | <code>cat &gt; sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql &lt;&lt;'SQL'<br>WITH execution_clock AS (<br>    SELECT CURRENT_TIMESTAMP AS processed_at<br>),<br>amazon_rows AS (<br>    SELECT<br>        'amazon_ads'</code> | 0 | false | false |
| 45 | run | <code>python run.py &gt; /tmp/runlog5 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog5</code> | 843 | true | false |
| 47 | run | <code>grep -A12 -B2 'unified_campaign_metrics' /tmp/runlog5 &#124; head -25;</code> | 2253 | false | false |
| 49 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting.duckdb')<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()<br>try:c.execute('create or replace table intermedia</code> | 139 | false | false |
| 51 | run | <code>python - &lt;&lt;'PY'<br>p='sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql';s=open(p).read();s=s.replace('CASE WHEN conversions &gt; 0 THEN ROUND(cost / conversions, 2) ELSE 0 END AS cost_per_con</code> | 506 | false | false |
| 53 | run | <code>sed -n '115,145p' sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql; python run.py &gt;/tmp/runlog6 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog6</code> | 2241 | true | false |
| 55 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting.duckdb')<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()<br>for needle in ['CASE WHEN metrics.conversions &gt; 0</code> | 290 | false | false |
| 57 | run | <code>sed -n '97,118p' sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql</code> | 1596 | false | false |
| 59 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting.duckdb')<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()<br>for ix in [s.index('base AS ('),s.index('metrics </code> | 454 | false | false |
| 61 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read(); c=duckdb.connect('ad_reporting.duckdb')<br># Build each section by CTE text manually staged</code> | 828 | false | false |
| 63 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read();c=duckdb.connect('ad_reporting.duckdb')<br>for end in ['amazon_rows AS (','google_rows AS ('</code> | 139 | false | false |
| 65 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting.duckdb')<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()<br># replace select list final output<br>p=s.index('SEL</code> | 512 | false | false |
| 67 | run | <code>python - &lt;&lt;'PY'<br>p='sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql';s=open(p).read()<br>for old,new in [('WHEN platform = \'amazon_ads\' AND click_through_rate','WHEN base.platform = \'am</code> | 843 | true | false |
| 69 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting.duckdb');s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read();p=s.index('metrics AS (')<br>q=s[:p]+'SELECT * FROM </code> | 87 | false | false |
| 71 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,re<br>c=duckdb.connect('ad_reporting.duckdb');s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()<br>for marker,final in [('metrics AS (','SELECT *</code> | 384 | false | false |
| 73 | run | <code>sed -n '96,130p' sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql;</code> | 2534 | false | false |
| 75 | run | grep -n conversions sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql | 743 | false | false |
| 77 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read();c=duckdb.connect('ad_reporting.duckdb')<br>for key in ['amazon_rows','google_rows','facebook</code> | 1078 | false | false |
| 79 | run | <code>python - &lt;&lt;'PY'<br>p='sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql';s=open(p).read();s=s.replace("CAST(COALESCE(impressions, 0) AS BIGINT) AS impressions,\n        CAST(COALESCE(clicks</code> | 276 | false | false |
| 83 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer in ('intermediate_models','marts_models'):<br> for m in c['modeling_spec'][layer]: print(m['name'],len(m['columns']</code> | 1029 | true | false |

### agent action 的 thought/message 命中原句

event 31 / message

```text
Running command: cat sql/intermediate/int_ad_reporting__time_series_analytics.sql | head -20; head -35 sql/marts/ad_reporting__predictive_analytics.sql; head -20 sql/staging/stg_google_ads__account_report.sql
```
event 33 / message

```text
Running command: grep -n 'FROM\|JOIN' sql/intermediate/int_ad_reporting__time_series_analytics.sql sql/marts/ad_reporting__predictive_analytics.sql
```
event 35 / message

```text
for p in [Path('sql/intermediate/int_ad_reporting__time_series_analytics.sql'),Path('sql/marts/ad_reporting__predictive_analytics.sql')]:
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-006.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__predictive_analytics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/marts/ad_reporting__predictive_analytics.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_ad_reporting__predictive_analytics/020_impl-006_ad_reporting__predictive_analytics.json`
- S11: `data/005_cs_work/impl-006/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
