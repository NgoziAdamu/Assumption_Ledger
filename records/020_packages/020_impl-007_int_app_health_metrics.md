# impl-007 | intermediate | int_app_health_metrics | 差异：S1；日期 原记录

## 契约完整原文

S3:901–1064

```yaml
    - name: int_app_health_metrics
      description: Unified daily app health metrics across Google Play and Apple Store with crashes, installs, ratings, rolling stats, trends, scores, classifications, flags, and data quality
      grain: One row per app_name per platform per date_day
      source_models:
      - staging.stg_google_play__stats_crashes_overview
      - staging.stg_google_play__stats_installs_overview
      - staging.stg_google_play__stats_ratings_overview
      - staging.stg_apple_store__app_crash_daily
      - staging.stg_apple_store__app_store_download_standard_daily
      business_logic: 'Inputs and key mapping: - Crashes: - Google Play: stg_google_play__stats_crashes_overview (date_day, package_name→app_name, crashes) - Apple Store: stg_apple_store__app_crash_daily (date_day, app_name, crashes) - Installs/Downloads: - Google Play: stg_google_play__stats_installs_overview (date_day, package_name→app_name, device_installs, device_uninstalls) - Apple Store: stg_apple_store__app_store_download_standard_daily (date_day, app_name, total_downloads) - Ratings: - Google Play only: stg_google_play__stats_ratings_overview (date_day, package_name→app_name, average_rating, rolling_total_average_rating), including only rows where average_rating is present (rows with NULL average_rating are excluded). - Platform is set to ''google_play'' or ''apple_store'' per source row. Record assembly (full outer joins; assumes sources are unique per (date_day, app_name, platform)): - Full outer join crashes and installs on (date_day, app_name, platform). - Full outer join ratings using the coalesced (date_day, app_name, platform) from the prior join. - Coalesced keys: date_day = coalesce(crashes.date_day, installs.date_day, ratings.date_day); app_name and platform likewise. Metrics null policy: - crash_count = coalesce(source crashes, 0). - Installs/uninstalls/total_activity: - Google Play: installs = device_installs; uninstalls = device_uninstalls; total_activity = installs + uninstalls. - Apple Store: installs = total_downloads; uninstalls = 0; total_activity = installs. - daily_average_rating and total_average_rating come from Google Play ratings; they are NULL when no rating row exists. Rate calculations (double precision; no rounding): - crash_rate_per_thousand = crashes per 1,000 activities using crash_count and total_activity; if total_activity is 0 or missing, set to 0. - uninstall_rate_percentage = uninstalls as a percent of installs; if installs is 0 or missing, set to 0. Rolling windows and lags (partitioned by app_name and platform; ordered by date_day; row-based using available records only): - 7-row averages: crash_rate_7d_avg = average of crash_rate_per_thousand over up to the last 7 records (including current); uninstall_rate_7d_avg = average of uninstall_rate_percentage over the same; rating_7d_avg = average of daily_average_rating over the same (NULL if all values in the window are NULL). - 30-row metrics: crash_rate_30d_avg = average of crash_rate_per_thousand over up to the last 30 records; installs_30d_sum = sum of installs over up to the last 30 records; crashes_30d_sum = sum of crash_count over up to the last 30 records. - Lags: rating_7d_ago and crash_rate_7d_ago are the values from 7 records earlier. Trends (default to 0 when insufficient history or NULL inputs): - rating_trend_7d = daily_average_rating minus rating_7d_ago when both exist; else 0. - crash_rate_trend_7d = crash_rate_per_thousand minus crash_rate_7d_ago when both exist; else 0. Health score (integer 0–100): - Start at 50. - Rating adjustment using daily_average_rating: +30 (≥4.5), +20 (≥4.0), +10 (≥3.5), +0 (≥3.0), -10 otherwise; if rating is missing it falls to the -10 adjustment. - Crash-rate penalty using crash_rate_7d_avg: 0 (≤1), -5 (≤5), -10 (≤10), -15 (≤20), -20 otherwise. - Uninstall-rate penalty using uninstall_rate_7d_avg: 0 (≤2), -5 (≤5), -10 (≤10), -15 (≤20), -20 otherwise. - Bound the final score to 0–100. Health status (first-match precedence): - Critical if crash_rate_7d_avg > 15. - High Risk if uninstall_rate_7d_avg > 15. - Poor Quality if daily_average_rating < 3.0. - Declining if rating_trend_7d < -0.3. - Unstable if crash_rate_trend_7d > 5. - Excellent if daily_average_rating ≥ 4.0 and crash_rate_7d_avg ≤ 5. - Good if daily_average_rating ≥ 3.5 and crash_rate_7d_avg ≤ 10. - Average otherwise. Volume tier by installs_30d_sum: - High Volume (≥10,000), Medium Volume (≥1,000), Low Volume (≥100), Minimal Volume (<100). Flags (0/1 integers): - needs_immediate_attention = 1 for health_status in (''Critical'',''High Risk''); else 0. - is_high_performing = 1 for health_status=''Excellent''; else 0. - is_declining_quality = 1 if rating_trend_7d < -0.2; else 0. - is_stability_degrading = 1 if crash_rate_trend_7d > 3; else 0. Data quality flag (first-match precedence): - Invalid Health Score if health_score < 0 or > 100. - Invalid Crash Rate if crash_rate_per_thousand < 0. - Invalid Uninstall Rate if uninstall_rate_percentage < 0. - Invalid Rating if daily_average_rating < 0 or > 5. - Valid otherwise. Output filter and timestamp: - Include only rows where date_day, app_name, and platform are not NULL. - analysis_timestamp = current runtime timestamp in the warehouse/session time zone.'
      columns:
      - name: date_day
        data_type: DATE
        description: Metric date for the aggregated daily health record
        tests:
        - not_null
      - name: app_name
        data_type: VARCHAR
        description: Application identifier; Google uses package_name mapped to app_name; Apple uses app_name as-is
        tests:
        - not_null
      - name: platform
        data_type: VARCHAR
        description: 'Source platform literal identifying the ecosystem: ''google_play'' or ''apple_store'''
        tests:
        - not_null
        - platform IN ('google_play','apple_store')
      - name: crash_count
        data_type: BIGINT
        description: Daily crashes from source data, set to 0 when missing
        tests:
        - not_null
        - crash_count >= 0
      - name: installs
        data_type: BIGINT
        description: 'Daily installs/downloads (Google: device_installs; Apple: total_downloads) set to 0 when missing'
        tests:
        - not_null
        - installs >= 0
      - name: uninstalls
        data_type: BIGINT
        description: Daily uninstalls (Google only) else 0 for Apple and when missing
        tests:
        - not_null
        - uninstalls >= 0
      - name: total_activity
        data_type: BIGINT
        description: 'Activity denominator (Google: installs+uninstalls; Apple: installs) set to 0 when missing'
        tests:
        - not_null
        - total_activity >= 0
      - name: daily_average_rating
        data_type: DECIMAL(10,2)
        description: Google Play daily average rating; NULL if no rating row; intended range 0–5 with 2-decimal precision
      - name: total_average_rating
        data_type: DECIMAL(10,2)
        description: Google Play rolling total average rating; NULL if absent; intended range 0–5 with 2-decimal precision
      - name: crash_rate_per_thousand
        data_type: DOUBLE
        description: Crashes per 1,000 activities using crash_count and total_activity; set to 0 when total_activity is 0 or missing
        tests:
        - not_null
        - crash_rate_per_thousand >= 0
      - name: uninstall_rate_percentage
        data_type: DOUBLE
        description: Uninstalls as a percent of installs; set to 0 when installs is 0 or missing; can exceed 100% when uninstalls > installs
        tests:
        - not_null
        - uninstall_rate_percentage >= 0 AND uninstall_rate_percentage <= 100
      - name: crash_rate_7d_avg
        data_type: DOUBLE
        description: Rolling average of crash_rate_per_thousand over up to the last 7 records by app/platform; non-null
        tests:
        - not_null
        - crash_rate_7d_avg >= 0
      - name: uninstall_rate_7d_avg
        data_type: DOUBLE
        description: Rolling average of uninstall_rate_percentage over up to the last 7 records by app/platform; non-null
        tests:
        - not_null
        - uninstall_rate_7d_avg >= 0
      - name: rating_7d_avg
        data_type: DOUBLE
        description: Rolling average of daily_average_rating over up to the last 7 records by app/platform; NULL if the window has no ratings
      - name: crash_rate_30d_avg
        data_type: DOUBLE
        description: Rolling average of crash_rate_per_thousand over up to the last 30 records by app/platform; non-null
        tests:
        - not_null
        - crash_rate_30d_avg >= 0
      - name: installs_30d_sum
        data_type: HUGEINT
        description: Rolling sum of installs over up to the last 30 records by app/platform; non-null and non-negative
        tests:
        - not_null
        - installs_30d_sum >= 0
      - name: crashes_30d_sum
        data_type: HUGEINT
        description: Rolling sum of crash_count over up to the last 30 records by app/platform; non-null and non-negative
        tests:
        - not_null
        - crashes_30d_sum >= 0
      - name: rating_trend_7d
        data_type: DECIMAL(12,2)
        description: Change in rating versus the value from 7 records earlier; 0 if missing history or inputs
        tests:
        - not_null
        - rating_trend_7d >= -5.00 AND rating_trend_7d <= 5.00
      - name: crash_rate_trend_7d
        data_type: DOUBLE
        description: Change in crash_rate_per_thousand versus the value from 7 records earlier; 0 if missing history or inputs
      - name: health_score
        data_type: INTEGER
        description: Composite score 0–100 from base 50 plus rating adjustment and penalties based on 7-row averages; bounded to [0,100]
        tests:
        - not_null
        - health_score >= 0 AND health_score <= 100
      - name: health_status
        data_type: VARCHAR
        description: Categorical status from ordered rules using crash/uninstall 7-row averages, rating, and trends
        tests:
        - not_null
        - health_status IN ('Critical','High Risk','Poor Quality','Declining','Unstable','Excellent','Good','Average')
      - name: volume_tier
        data_type: VARCHAR
        description: 'Usage volume class by installs_30d_sum thresholds: High (≥10000), Medium (≥1000), Low (≥100), Minimal (<100)'
        tests:
        - not_null
        - volume_tier IN ('High Volume','Medium Volume','Low Volume','Minimal Volume')
      - name: needs_immediate_attention
        data_type: INTEGER
        description: Urgency flag as 0/1 where 1 for health_status in ('Critical','High Risk')
        tests:
        - not_null
        - needs_immediate_attention IN (0,1)
      - name: is_high_performing
        data_type: INTEGER
        description: Performance flag as 0/1 where 1 for health_status='Excellent'
        tests:
        - not_null
        - is_high_performing IN (0,1)
      - name: is_declining_quality
        data_type: INTEGER
        description: Trend flag as 0/1 where 1 if rating_trend_7d < -0.2
        tests:
        - not_null
        - is_declining_quality IN (0,1)
      - name: is_stability_degrading
        data_type: INTEGER
        description: Stability flag as 0/1 where 1 if crash_rate_trend_7d > 3
        tests:
        - not_null
        - is_stability_degrading IN (0,1)
      - name: data_quality_flag
        data_type: VARCHAR
        description: 'Quality check result with precedence: Invalid Health Score, Invalid Crash Rate, Invalid Uninstall Rate, Invalid Rating, else Valid'
        tests:
        - not_null
        - data_quality_flag IN ('Valid','Invalid Health Score','Invalid Crash Rate','Invalid Uninstall Rate','Invalid Rating')
      - name: analysis_timestamp
        data_type: TIMESTAMP WITH TIME ZONE
        description: Runtime timestamp set via current_timestamp in warehouse/session time zone
        tests:
        - not_null
```

## agent 最终 SQL

S4

```sql
WITH crash AS (
 SELECT date_day,package_name app_name,'google_play' platform,crashes FROM staging.stg_google_play__stats_crashes_overview
 UNION ALL SELECT date_day,app_name,'apple_store',crashes FROM staging.stg_apple_store__app_crash_daily
), inst AS (
 SELECT date_day,package_name app_name,'google_play' platform,device_installs installs,device_uninstalls uninstalls FROM staging.stg_google_play__stats_installs_overview
 UNION ALL SELECT date_day,app_name,'apple_store',total_downloads,0::BIGINT FROM staging.stg_apple_store__app_store_download_standard_daily
), ratings AS (SELECT date_day,package_name app_name,'google_play' platform,average_rating daily_average_rating,rolling_total_average_rating total_average_rating FROM staging.stg_google_play__stats_ratings_overview WHERE average_rating IS NOT NULL),
 joined AS (SELECT coalesce(c.date_day,i.date_day,r.date_day) date_day,coalesce(c.app_name,i.app_name,r.app_name) app_name,coalesce(c.platform,i.platform,r.platform) platform,coalesce(c.crashes,0)::BIGINT crash_count,coalesce(i.installs,0)::BIGINT installs,coalesce(i.uninstalls,0)::BIGINT uninstalls,coalesce(r.daily_average_rating) daily_average_rating,coalesce(r.total_average_rating) total_average_rating
 FROM crash c FULL JOIN inst i USING(date_day,app_name,platform) FULL JOIN ratings r ON coalesce(c.date_day,i.date_day)=r.date_day AND coalesce(c.app_name,i.app_name)=r.app_name AND coalesce(c.platform,i.platform)=r.platform),
 rates AS (SELECT *,installs+uninstalls total_activity,CASE WHEN installs+uninstalls=0 THEN 0.0 ELSE crash_count*1000.0/(installs+uninstalls) END crash_rate_per_thousand,CASE WHEN installs=0 THEN 0.0 ELSE uninstalls*100.0/installs END uninstall_rate_percentage FROM joined),
 roll AS (SELECT *,avg(crash_rate_per_thousand) OVER w7 crash_rate_7d_avg,avg(uninstall_rate_percentage) OVER w7 uninstall_rate_7d_avg,avg(daily_average_rating) OVER w7 rating_7d_avg,avg(crash_rate_per_thousand) OVER w30 crash_rate_30d_avg,sum(installs) OVER w30 installs_30d_sum,sum(crash_count) OVER w30 crashes_30d_sum,lag(daily_average_rating,7) OVER win rating_7d_ago,lag(crash_rate_per_thousand,7) OVER win crash_rate_7d_ago FROM rates WINDOW win AS(PARTITION BY app_name,platform ORDER BY date_day),w7 AS(PARTITION BY app_name,platform ORDER BY date_day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW),w30 AS(PARTITION BY app_name,platform ORDER BY date_day ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)),
 trends AS(SELECT *,coalesce(daily_average_rating-rating_7d_ago,0)::DECIMAL(12,2) rating_trend_7d,coalesce(crash_rate_per_thousand-crash_rate_7d_ago,0.0) crash_rate_trend_7d FROM roll),
 scored AS(SELECT *,greatest(0,least(100,50+CASE WHEN daily_average_rating>=4.5 THEN 30 WHEN daily_average_rating>=4 THEN 20 WHEN daily_average_rating>=3.5 THEN 10 WHEN daily_average_rating>=3 THEN 0 ELSE -10 END+CASE WHEN crash_rate_7d_avg<=1 THEN 0 WHEN crash_rate_7d_avg<=5 THEN -5 WHEN crash_rate_7d_avg<=10 THEN -10 WHEN crash_rate_7d_avg<=20 THEN -15 ELSE -20 END+CASE WHEN uninstall_rate_7d_avg<=2 THEN 0 WHEN uninstall_rate_7d_avg<=5 THEN -5 WHEN uninstall_rate_7d_avg<=10 THEN -10 WHEN uninstall_rate_7d_avg<=20 THEN -15 ELSE -20 END))::INTEGER health_score,
 CASE WHEN crash_rate_7d_avg>15 THEN 'Critical' WHEN uninstall_rate_7d_avg>15 THEN 'High Risk' WHEN daily_average_rating<3 THEN 'Poor Quality' WHEN rating_trend_7d<-.3 THEN 'Declining' WHEN crash_rate_trend_7d>5 THEN 'Unstable' WHEN daily_average_rating>=4 AND crash_rate_7d_avg<=5 THEN 'Excellent' WHEN daily_average_rating>=3.5 AND crash_rate_7d_avg<=10 THEN 'Good' ELSE 'Average' END health_status,
 CASE WHEN installs_30d_sum>=10000 THEN 'High Volume' WHEN installs_30d_sum>=1000 THEN 'Medium Volume' WHEN installs_30d_sum>=100 THEN 'Low Volume' ELSE 'Minimal Volume' END volume_tier FROM trends),
 flags AS(SELECT *, (health_status IN ('Critical','High Risk'))::INTEGER needs_immediate_attention,(health_status='Excellent')::INTEGER is_high_performing,(rating_trend_7d<-.2)::INTEGER is_declining_quality,(crash_rate_trend_7d>3)::INTEGER is_stability_degrading,
 CASE WHEN health_score<0 OR health_score>100 THEN 'Invalid Health Score' WHEN crash_rate_per_thousand<0 THEN 'Invalid Crash Rate' WHEN uninstall_rate_percentage<0 THEN 'Invalid Uninstall Rate' WHEN daily_average_rating<0 OR daily_average_rating>5 THEN 'Invalid Rating' ELSE 'Valid' END data_quality_flag FROM scored)
SELECT date_day,app_name,platform,crash_count,installs,uninstalls,total_activity,daily_average_rating,total_average_rating,crash_rate_per_thousand,uninstall_rate_percentage,crash_rate_7d_avg,uninstall_rate_7d_avg,rating_7d_avg,crash_rate_30d_avg,installs_30d_sum,crashes_30d_sum,rating_trend_7d,crash_rate_trend_7d,health_score,health_status,volume_tier,needs_immediate_attention,is_high_performing,is_declining_quality,is_stability_degrading,data_quality_flag,current_timestamp::TIMESTAMP WITH TIME ZONE analysis_timestamp FROM flags WHERE date_day IS NOT NULL AND app_name IS NOT NULL AND platform IS NOT NULL
```

## gold SQL（仅供定位差异）

S5

```sql
-- Application health comprehensive assessment intermediate model
-- Function: Comprehensive analysis of application crash rates, rating trends, user satisfaction and other health indicators
-- Author: Data Engineering Team
-- Update time: 2024

with app_crash_metrics as (
    -- Google Play crash data
    select 
        date_day,
        package_name as app_name,
        'google_play' as platform,
        crashes as crash_count,
        case when crashes > 0 then 1 else 0 end as has_crashes
    from staging.stg_google_play__stats_crashes_overview
    
    union all
    
    -- Apple Store crash data
    select 
        date_day,
        app_name,
        'apple_store' as platform,
        crashes as crash_count,
        case when crashes > 0 then 1 else 0 end as has_crashes
    from staging.stg_apple_store__app_crash_daily
),

app_install_metrics as (
    -- Google Play installation data
    select 
        date_day,
        package_name as app_name,
        'google_play' as platform,
        device_installs as installs,
        device_uninstalls as uninstalls,
        device_installs + device_uninstalls as total_activity
    from staging.stg_google_play__stats_installs_overview
    
    union all
    
    -- Apple Store download data
    select 
        date_day,
        app_name,
        'apple_store' as platform,
        total_downloads as installs,
        0 as uninstalls,  -- There is no direct uninstall data in Apple data
        total_downloads as total_activity
    from staging.stg_apple_store__app_store_download_standard_daily
),

app_rating_metrics as (
    -- Google Play rating data
    select 
        date_day,
        package_name as app_name,
        'google_play' as platform,
        average_rating as daily_average_rating,
        rolling_total_average_rating as total_average_rating
    from staging.stg_google_play__stats_ratings_overview
    where average_rating is not null
),

daily_app_health as (
    select 
        coalesce(acm.date_day, aim.date_day, arm.date_day) as date_day,
        coalesce(acm.app_name, aim.app_name, arm.app_name) as app_name,
        coalesce(acm.platform, aim.platform, arm.platform) as platform,
        
        -- crash indicator
        coalesce(acm.crash_count, 0) as crash_count,
        coalesce(acm.has_crashes, 0) as has_crashes,
        
        -- activity indicators
        coalesce(aim.installs, 0) as installs,
        coalesce(aim.uninstalls, 0) as uninstalls,
        coalesce(aim.total_activity, 0) as total_activity,
        
        -- Rating indicators
        arm.daily_average_rating,
        arm.total_average_rating,
        
        -- Calculate crash rate (crashes per thousand installs)
        case 
            when coalesce(aim.total_activity, 0) > 0 
            then (coalesce(acm.crash_count, 0) * 1000.0) / aim.total_activity
            else 0 
        end as crash_rate_per_thousand,
        
        -- Uninstall rate
        case 
            when coalesce(aim.installs, 0) > 0 
            then (coalesce(aim.uninstalls, 0) * 100.0) / aim.installs
            else 0 
        end as uninstall_rate_percentage
        
    from app_crash_metrics acm
    full outer join app_install_metrics aim
        on acm.date_day = aim.date_day 
        and acm.app_name = aim.app_name 
        and acm.platform = aim.platform
    full outer join app_rating_metrics arm
        on coalesce(acm.date_day, aim.date_day) = arm.date_day 
        and coalesce(acm.app_name, aim.app_name) = arm.app_name 
        and coalesce(acm.platform, aim.platform) = arm.platform
),

app_health_trends as (
    select 
        *,
        
        -- 7-day sliding window indicator
        avg(crash_rate_per_thousand) over (
            partition by app_name, platform 
            order by date_day 
            rows between 6 preceding and current row
        ) as crash_rate_7d_avg,
        
        avg(uninstall_rate_percentage) over (
            partition by app_name, platform 
            order by date_day 
            rows between 6 preceding and current row
        ) as uninstall_rate_7d_avg,
        
        avg(daily_average_rating) over (
            partition by app_name, platform 
            order by date_day 
            rows between 6 preceding and current row
        ) as rating_7d_avg,
        
        -- 30-day sliding window indicator
        avg(crash_rate_per_thousand) over (
            partition by app_name, platform 
            order by date_day 
            rows between 29 preceding and current row
        ) as crash_rate_30d_avg,
        
        sum(installs) over (
            partition by app_name, platform 
            order by date_day 
            rows between 29 preceding and current row
        ) as installs_30d_sum,
        
        sum(crash_count) over (
            partition by app_name, platform 
            order by date_day 
            rows between 29 preceding and current row
        ) as crashes_30d_sum,
        
        -- trend analysis
        lag(daily_average_rating, 7) over (
            partition by app_name, platform 
            order by date_day
        ) as rating_7d_ago,
        
        lag(crash_rate_per_thousand, 7) over (
            partition by app_name, platform 
            order by date_day
        ) as crash_rate_7d_ago
        
    from daily_app_health
),

app_health_classification as (
    select 
        *,
        
        -- Rating trend analysis
        case 
            when daily_average_rating is not null and rating_7d_ago is not null
            then daily_average_rating - rating_7d_ago
            else 0
        end as rating_trend_7d,
        
        -- Crash rate trend analysis
        case 
            when crash_rate_per_thousand is not null and crash_rate_7d_ago is not null
            then crash_rate_per_thousand - crash_rate_7d_ago
            else 0
        end as crash_rate_trend_7d,
        
        -- App health score (0-100)
        greatest(0, least(100,
            -- Base score 50
            50 +
            -- Bonus points for rating (up to +30 points)
            case 
                when daily_average_rating >= 4.5 then 30
                when daily_average_rating >= 4.0 then 20
                when daily_average_rating >= 3.5 then 10
                when daily_average_rating >= 3.0 then 0
                else -10
            end +
            -- Points deducted for crash rate (up to 20 points)
            case 
                when crash_rate_7d_avg <= 1 then 0
                when crash_rate_7d_avg <= 5 then -5
                when crash_rate_7d_avg <= 10 then -10
                when crash_rate_7d_avg <= 20 then -15
                else -20
            end +
            -- Uninstall rate扣分（最高扣20分）
            case 
                when uninstall_rate_7d_avg <= 2 then 0
                when uninstall_rate_7d_avg <= 5 then -5
                when uninstall_rate_7d_avg <= 10 then -10
                when uninstall_rate_7d_avg <= 20 then -15
                else -20
            end
        )) as health_score,
        
        -- Application status classification
        case 
            when crash_rate_7d_avg > 15 then 'Critical'
            when uninstall_rate_7d_avg > 15 then 'High Risk'
            when daily_average_rating < 3.0 then 'Poor Quality'
            when rating_trend_7d < -0.3 then 'Declining'
            when crash_rate_trend_7d > 5 then 'Unstable'
            when daily_average_rating >= 4.0 and crash_rate_7d_avg <= 5 then 'Excellent'
            when daily_average_rating >= 3.5 and crash_rate_7d_avg <= 10 then 'Good'
            else 'Average'
        end as health_status,
        
        -- attention level
        case 
            when installs_30d_sum >= 10000 then 'High Volume'
            when installs_30d_sum >= 1000 then 'Medium Volume'
            when installs_30d_sum >= 100 then 'Low Volume'
            else 'Minimal Volume'
        end as volume_tier
        
    from app_health_trends
),

final as (
    select 
        date_day,
        app_name,
        platform,
        crash_count,
        installs,
        uninstalls,
        total_activity,
        daily_average_rating,
        total_average_rating,
        crash_rate_per_thousand,
        uninstall_rate_percentage,
        crash_rate_7d_avg,
        uninstall_rate_7d_avg,
        rating_7d_avg,
        crash_rate_30d_avg,
        installs_30d_sum,
        crashes_30d_sum,
        rating_trend_7d,
        crash_rate_trend_7d,
        health_score,
        health_status,
        volume_tier,
        
        -- business identifier
        case when health_status in ('Critical', 'High Risk') then 1 else 0 end as needs_immediate_attention,
        case when health_status = 'Excellent' then 1 else 0 end as is_high_performing,
        case when rating_trend_7d < -0.2 then 1 else 0 end as is_declining_quality,
        case when crash_rate_trend_7d > 3 then 1 else 0 end as is_stability_degrading,
        
        -- Data quality mark
        case 
            when health_score < 0 or health_score > 100 then 'Invalid Health Score'
            when crash_rate_per_thousand < 0 then 'Invalid Crash Rate'
            when uninstall_rate_percentage < 0 then 'Invalid Uninstall Rate'
            when daily_average_rating < 0 or daily_average_rating > 5 then 'Invalid Rating'
            else 'Valid'
        end as data_quality_flag,
        
        current_timestamp as analysis_timestamp
        
    from app_health_classification
    where date_day is not null 
      and app_name is not null 
      and platform is not null
)

select * from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 8670 | 8670 | 0 | 0 | 366 | 366 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"date_day":"2024-09-06"}</code> |
| K2 | <code>{"date_day":"2024-09-07"}</code> |
| K3 | <code>{"date_day":"2024-09-08"}</code> |
| K4 | <code>{"date_day":"2024-11-21"}</code> |
| K5 | <code>{"date_day":"2025-01-23"}</code> |
| K6 | <code>{"date_day":"2025-03-31"}</code> |
| K7 | <code>{"date_day":"2024-09-18"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| app_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| crash_count | 0 | 0 | 0 | BIGINT | BIGINT |
| installs | 0 | 0 | 0 | BIGINT | BIGINT |
| uninstalls | 0 | 0 | 0 | BIGINT | BIGINT |
| total_activity | 0 | 0 | 0 | BIGINT | BIGINT |
| crash_rate_per_thousand | 0 | 0 | 0 | DOUBLE | DOUBLE |
| uninstall_rate_percentage | 0 | 0 | 0 | DOUBLE | DOUBLE |
| crash_rate_7d_avg | 0 | 0 | 0 | DOUBLE | DOUBLE |
| uninstall_rate_7d_avg | 379 | 379 | 379 | DOUBLE | DOUBLE |
| crash_rate_30d_avg | 0 | 0 | 0 | DOUBLE | DOUBLE |
| installs_30d_sum | 199 | 199 | 199 | HUGEINT | HUGEINT |
| crashes_30d_sum | 4 | 4 | 4 | HUGEINT | HUGEINT |
| crash_rate_trend_7d | 0 | 0 | 0 | DOUBLE | DOUBLE |
| health_score | 0 | 0 | 0 | INTEGER | INTEGER |
| health_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| volume_tier | 12 | 12 | 12 | VARCHAR | VARCHAR |
| data_quality_flag | 0 | 0 | 0 | VARCHAR | VARCHAR |

uninstall_rate_7d_avg 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0.0","rows":7},{"value":"120.3125","rows":1},{"value":"130.98039215686273","rows":1},{"value":"146.89507494646682","rows":1},{"value":"190.65533980582524","rows":1}]</code> | <code>[{"value":"0.0","rows":7},{"value":"120.3125","rows":1},{"value":"126.57218777679363","rows":1},{"value":"130.98039215686273","rows":1},{"value":"146.89507494646682","rows":1}]</code> |
| K2 | <code>[{"value":"0.0","rows":5},{"value":"116.48351648351648","rows":1},{"value":"122.43346007604563","rows":1},{"value":"1269.6941612604264","rows":1},{"value":"1683.8709677419354","rows":1}]</code> | <code>[{"value":"0.0","rows":5},{"value":"116.48351648351648","rows":1},{"value":"122.43346007604563","rows":1},{"value":"1269.6941612604264","rows":1},{"value":"1683.8709677419354","rows":1}]</code> |
| K3 | <code>[{"value":"0.0","rows":3},{"value":"10855.792682926829","rows":1},{"value":"1298.360655737705","rows":1},{"value":"158.48556463975473","rows":1},{"value":"1644.4444444444443","rows":1}]</code> | <code>[{"value":"0.0","rows":3},{"value":"10855.792682926829","rows":1},{"value":"1298.360655737705","rows":1},{"value":"158.48556463975473","rows":1},{"value":"1644.4444444444443","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

installs_30d_sum 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":4},{"value":"14","rows":1},{"value":"1570","rows":1},{"value":"172","rows":1},{"value":"182","rows":1}]</code> | <code>[{"value":"0","rows":4},{"value":"1129","rows":1},{"value":"14","rows":1},{"value":"1570","rows":1},{"value":"172","rows":1}]</code> |
| K2 | <code>[{"value":"0","rows":2},{"value":"12","rows":1},{"value":"133","rows":1},{"value":"163","rows":1},{"value":"182","rows":1}]</code> | <code>[{"value":"0","rows":2},{"value":"121","rows":1},{"value":"133","rows":1},{"value":"163","rows":1},{"value":"182","rows":1}]</code> |
| K3 | <code>[{"value":"0","rows":2},{"value":"111","rows":1},{"value":"115","rows":2},{"value":"18","rows":1},{"value":"199","rows":1}]</code> | <code>[{"value":"0","rows":2},{"value":"111","rows":1},{"value":"115","rows":2},{"value":"18","rows":1},{"value":"199","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

crashes_30d_sum 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | <code>[{"value":"0","rows":6},{"value":"102","rows":1},{"value":"121","rows":1},{"value":"131","rows":1},{"value":"140","rows":1}]</code> | <code>[{"value":"0","rows":6},{"value":"10","rows":1},{"value":"102","rows":1},{"value":"121","rows":1},{"value":"131","rows":1}]</code> |
| K5 | <code>[{"value":"0","rows":4},{"value":"119","rows":1},{"value":"124","rows":1},{"value":"146","rows":1},{"value":"148","rows":1}]</code> | <code>[{"value":"0","rows":4},{"value":"119","rows":1},{"value":"124","rows":1},{"value":"132","rows":1},{"value":"146","rows":1}]</code> |
| K6 | <code>[{"value":"0","rows":3},{"value":"129","rows":1},{"value":"158","rows":1},{"value":"169","rows":1},{"value":"178","rows":2}]</code> | <code>[{"value":"0","rows":3},{"value":"129","rows":1},{"value":"158","rows":1},{"value":"169","rows":1},{"value":"178","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

volume_tier 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Low Volume","rows":14},{"value":"Medium Volume","rows":1},{"value":"Minimal Volume","rows":12}]</code> | <code>[{"value":"Low Volume","rows":13},{"value":"Medium Volume","rows":2},{"value":"Minimal Volume","rows":12}]</code> |
| K2 | <code>[{"value":"Low Volume","rows":15},{"value":"Minimal Volume","rows":8}]</code> | <code>[{"value":"Low Volume","rows":17},{"value":"Minimal Volume","rows":6}]</code> |
| K7 | <code>[{"value":"Low Volume","rows":19},{"value":"Medium Volume","rows":3},{"value":"Minimal Volume","rows":5}]</code> | <code>[{"value":"Low Volume","rows":18},{"value":"Medium Volume","rows":3},{"value":"Minimal Volume","rows":6}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

| 约束 | 列 | 违反计数 |
|---|---|---|
| grain | app_name,platform,date_day | <code>{"distinct_key_groups":8359,"duplicate_key_groups":297,"rows_in_duplicate_groups":601,"excess_duplicate_rows":304,"null_key_rows":0,"nonnull_duplicate_key_groups":297,"nonnull_rows_in_duplicate_groups":601,"nonnull_excess_duplicate_rows":304,"null_containing_duplicate_key_groups":0,"rows_in_null_containing_duplicate_groups":0}</code> |

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>2列；[{"column":"data_quality_flag","value":"Valid"},{"column":"analysis_timestamp","value":"2026-10-25 01:58:32.918769+08"}]</code> |
| C9_agent_runtime_text | <code>S4:18 current_timestamp；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:275 current_timestamp；命中数=1</code> |
| C9_contract_runtime_text | <code>S3:1062 current_timestamp；命中数=1</code> |

## 轨迹索引（不放输出原文）

本题事件总数：70；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions/4b972c8e-5e78-4c-989fe818d782cdb/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 6041 | true | false |
| 17 | run | <code>wc -l docs/data_contract.yaml &amp;&amp; sed -n '1,160p' docs/data_contract.yaml</code> | 6299 | false | false |
| 19 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c['staging_contract']['tables']:<br> print(t['name'],t['source_table'],','.join(x['name'] for x in t['columns']))<br>pr</code> | 5964 | true | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer in ['intermediate_models','marts_models']:<br> for m in c['modeling_spec'][layer]:<br>  print(m['name'],m['description</code> | 2844 | true | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c['staging_contract']['tables']:<br> f='sql/staging/'+t['name']+'.sql'<br> s=open(f).read()<br> print(t['name'],s.replace(</code> | 8133 | false | false |
| 27 | run | <code>cat &gt; /tmp/inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>out=Path('sql/intermediate')<br>queries={<br>'int_google_play__overview':"""WITH installs AS (SELECT * FROM staging.stg_google_play__stats_installs_overvi</code> | 0 | false | false |
| 29 | run | <code>cat &gt; /tmp/advanced.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/intermediate')<br>(p/'int_user_lifecycle_analysis.sql').write_text('''WITH first_install AS (<br>    SELECT package_name, min(date_day) AS </code> | 0 | false | false |
| 41 | run | <code>cat &gt; /tmp/report_health.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/marts')<br>(p/'app_reporting__app_health_monitoring_report.sql').write_text('''WITH base AS(SELECT * FROM intermediate.int_app_heal</code> | 0 | false | false |
| 43 | run | <code>python run.py &gt; /tmp/pipeline.log 2&gt;&amp;1; echo EXIT:$?; tail -100 /tmp/pipeline.log</code> | 7846 | true | false |
| 45 | run | <code>grep -E 'staging\.&#124;ERROR&#124;WARNING' /tmp/pipeline.log &#124; head -100</code> | 18912 | false | false |
| 47 | run | <code>rm -f app_reporting.duckdb; python - &lt;&lt;'PY'<br>import duckdb<br>src=duckdb.connect('app_reporting_start.duckdb',read_only=True); out=duckdb.connect('app_reporting.duckdb'); out.execute('create schema raw')<br></code> | 8738 | true | false |
| 55 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,glob,os<br>cfg=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('app_reporting.duckdb',read_only=True)<br>for layer,schema,models in [('staging','staging'</code> | 5387 | true | false |
| 57 | run | <code>python - &lt;&lt;'PY'<br>p='sql/intermediate/int_app_health_metrics.sql';s=open(p).read();s=s.replace("SELECT *,current_timestamp::TIMESTAMP WITH TIME ZONE analysis_timestamp FROM flags WHERE", "SELECT date_da</code> | 285 | false | false |
| 61 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for f in Path('sql/staging').glob('*.sql'):<br> s=f.read_text()<br> if 'CASE WHEN average_rating BETWEEN 0 AND 1' in s:<br>  s=s.replace('CASE WHEN average_rating BETWE</code> | 586 | false | false |
| 63 | run | <code>rm -f app_reporting.duckdb; python run.py &gt;/tmp/finalrun.log 2&gt;&amp;1; grep -E 'layer complete&#124;Errors occurred&#124;completed successfully' /tmp/finalrun.log; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ap</code> | 515 | false | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
(p/'int_app_health_metrics.sql').write_text('''WITH crash AS (
```
event 41 / message

```text
(p/'app_reporting__app_health_monitoring_report.sql').write_text('''WITH base AS(SELECT * FROM intermediate.int_app_health_metrics WHERE data_quality_flag='Valid'), platform AS(
```
event 57 / message

```text
p='sql/intermediate/int_app_health_metrics.sql';s=open(p).read();s=s.replace("SELECT *,current_timestamp::TIMESTAMP WITH TIME ZONE analysis_timestamp FROM flags WHERE", "SELECT date_day,app_name,platform,crash_count,installs,uninstalls,total_activity,daily_average_rating,total_average_rating,crash_rate_per_thousand,uninstall_rate_percentage,crash_rate_7d_avg,uninstall_rate_7d_avg,rating_7d_avg,crash_rate_30d_avg,installs_30d_sum,crashes_30d_sum,rating_trend_7d,crash_rate_trend_7d,health_score,health_status,volume_tier,needs_immediate_attention,is_high_performing,is_declining_quality,is_stability_degrading,data_quality_flag,current_timestamp::TIMESTAMP WITH TIME ZONE analysis_timestamp FROM flags WHERE")
```
event 63 / message

```text
checks=[("invalid rating", "select count(*) from staging.stg_google_play__stats_ratings_overview where average_rating not between 1 and 5 or rolling_total_average_rating not between 1 and 5"),("channel conversion outside 0-100", "select count(*) from intermediate.int_channel_performance where conversion_rate_percentage not between 0 and 100"),("lifecycle invalid ages", "select count(*) from intermediate.int_user_lifecycle_analysis where user_age_days<0"),("rfm duplicate grain", "select count(*) from (select app_id,buyer_country,buyer_currency from intermediate.int_user_rfm_analysis group by all having count(*)>1)"),("health score bounds", "select count(*) from intermediate.int_app_health_metrics where health_score not between 0 and 100")]
```

## result.md 本表名原句

未找到 result.md。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-007.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-007/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-007/agent/dacomp-de-impl-007/sql/intermediate/int_app_health_metrics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/sql/intermediate/int_app_health_metrics.sql`
- S6: `records/006_contract_impl-007.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/020_packages_work/020_impl-007_int_app_health_metrics/020_impl-007_int_app_health_metrics.json`
- S10: `data/005_cs_work/impl-007/node_results.duckdb`
- S11: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-007/app_reporting.duckdb`
- S12: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-007/agent/.events/sessions`
