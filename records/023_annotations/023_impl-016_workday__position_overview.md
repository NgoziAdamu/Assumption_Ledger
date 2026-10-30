# impl-016 · workday__position_overview

用途：**全量**；层：`marts`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：compensation_regex。

gold 的 grade 正则不提取数字是主因；agent 仅从 active organization metrics 读取组织维度造成额外缺失。

参与因素：C：organization_dimension（行减少0，格减少7784）。

标记：无。

organization_dimension 为 C 参与因素；organization_id/similar_group 干预未减少规模，不列参与因素。

## 材料与比较口径

精简材料包：[023_impl-016_workday__position_overview.md](../023_packages/023_impl-016_workday__position_overview.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml`；SHA-256 `8f0707fc595c6f2f1e46a1983436959278e10315cb723e975c2811858d737c91`。
契约行 2231–2477：

```
2231:     - name: workday__position_overview
2232:       description: Position-level overview with occupancy history, organizational context, compensation/job profile attributes, current-employee metrics, and derived scores/flags
2233:       grain: One row per position_id and source_relation
2234:       source_models:
2235:       - staging.stg_workday__position
2236:       - staging.stg_workday__worker_position
2237:       - staging.stg_workday__position_organization
2238:       - staging.stg_workday__organization
2239:       - intermediate.int_workday__organization_metrics
2240:       - staging.stg_workday__position_job_profile
2241:       - staging.stg_workday__job_profile
2242:       - mart.workday__employee_overview
2243:       business_logic: '- Base: Start from positions. Compute position_age_days as the days from effective_start to today. Bucket position_age_category by age: <90 days "New Position (<3 months)"; <365 days "Recent Position (3-12 months)"; <2 years "Established Position (1-2 years)"; <5 years "Mature Position (2-5 years)"; otherwise "Legacy Position (5+ years)". - Utilization history: Join worker-position assignments by position and source. Count distinct workers ever assigned (total), with open end date (current), and with closed end date (former). Set position_occupancy_status to "Occupied" if current>0; else "Vacant (Previously Occupied)" if total>0; else "Vacant (Never Occupied)". Average tenure days uses assignment start-to-end when ended, or start-to-today when still open. Take the most recent assignment start as last_assignment_date and most recent end as last_departure_date. New assignments last year count distinct workers with assignment start within the past 12 months; departures last year count distinct workers with assignment end within the past 12 months. - Organizational context: Link positions to organizations and organization metrics. Also link to job profile. similar_positions_in_department is the count of positions sharing the same organization_id and job_profile_id across the dataset. - Compensation and job profile: Derive compensation_tier from the first number found in compensation_grade_id: missing or not numeric → "Ungraded"; ≤5 → "Entry Level"; ≤10 → "Mid Level"; ≤15 → "Senior Level"; >15 → "Executive Level". challenging_work_conditions_score is the sum of three indicators (shift required, union eligible, weekly hours>40), range 0–3. Map management_level to a numeric scale: Director 4, Senior Manager 3, Manager 2, Individual Contributor 1, otherwise 0. - Current employee metrics: From employee overview by position and source. Averages (overall performance, career development, retention stability) are computed only for currently employed workers. Risk counts (High/Medium/Low Risk) are distinct worker counts by risk level without restricting to current employment. Value segments (High Value - High Retention, High Value - Flight Risk) are distinct worker counts by segment. New and veteran counts include only currently employed workers with maturity containing "New Hire" or "Veteran". Average age and ethnic diversity use only currently employed workers; military_veterans_count counts currently employed workers with military service. - Final projection and defaults: If any numeric metric is missing, default to 0; booleans default to false; text dimensions default to "Unknown"; compensation grade/tier default to "Ungraded". last_assignment_date falls back to position_created_date when no assignments; last_departure_date remains null when none. - Rounding: avg_tenure_years_in_position is average tenure days divided by 365, rounded to two decimals. Average employee scores are rounded to two decimals. Average employee age is rounded to one decimal. position_turnover_rate and position_efficiency_score are rounded to two decimals. - Derived metrics: position_turnover_rate is 0 if total ever assigned is 0; otherwise departures in the last year divided by total ever assigned, expressed as a percentage. position_efficiency_score (0–100) is the sum of: 25 if occupied; a tenure bucket (25 if tenure≥2 years, 20 if ≥1 year, 15 if ≥180 days, else 10); up to 30 points from employee performance (performance score × 0.3, capped at 30); up to 20 points from department health (health score × 0.2, capped at 20); then rounded. - Categorization rules (first-match wins): position_performance_category: Vacant Position; High-Performance Stable Position (performance≥80 and tenure≥2 years); High-Performance Position (performance≥70); Stable Position (tenure≥2 years); High-Turnover Position (departures_last_year>1); else Standard Position. management_priority: Review Position Necessity (vacant and age>180 days); Focus on Retention (any high risk employees); Performance Improvement Needed (performance<50); Department Support Needed (department health<50); Maintain Excellence (performance≥80); else Standard Management. cost_performance_analysis: No Current Cost (vacant); High Cost - Low Performance (weekly hours>40 and performance<60); High Cost - High Performance (weekly hours>40 and performance≥80); Optimal Cost-Performance (weekly hours≤40 and performance≥80); else Standard Cost-Performance. strategic_recommendation: Consider Position Elimination (vacant and age>365 days); Consider Position Consolidation (similar positions>5); Develop Succession Plan (any flight risk employees); Consider Position Expansion (performance≥90); else Maintain Current Structure. - Data quality: Mark as ERROR when title is missing/blank, weekly hours≤0, or position_age_days<0; mark as WARNING when weekly hours>80 or current assignments>3; otherwise VALID. - Output ordering: Sort rows by current_workers_assigned descending, then average employee performance descending, then position_age_days descending. - Analysis timestamp: Set to the current timestamp at query execution (time zone aware).'
2244:       columns:
2245:       - name: position_id
2246:         data_type: VARCHAR
2247:         description: Unique position identifier; primary key with source_relation; exactly one output row per (position_id, source_relation)
2248:         tests:
2249:         - not_null
2250:         - unique
2251:       - name: source_relation
2252:         data_type: VARCHAR
2253:         description: Source system identifier associated with the position_id
2254:         tests:
2255:         - not_null
2256:       - name: business_title
2257:         data_type: VARCHAR
2258:         description: Business title from position source; may be NULL/empty and is validated in data_quality_flag
2259:       - name: employee_type
2260:         data_type: VARCHAR
2261:         description: Employee type as stored on the position record
2262:       - name: default_weekly_hours
2263:         data_type: BIGINT
2264:         description: Default scheduled weekly hours from position; used in cost and work-conditions scoring; may be <=0 or >80 (flagged in data_quality_flag)
2265:       - name: position_created_date
2266:         data_type: DATE
2267:         description: Position effective_start date from the source, treated as the created date
2268:       - name: position_age_days
2269:         data_type: BIGINT
2270:         description: Days between effective_start and today; can be negative for future-dated positions
2271:       - name: position_age_category
2272:         data_type: VARCHAR
2273:         description: 'Age bucket based on position_age_days: <90 New; <365 Recent; <730 Established; <1825 Mature; else Legacy'
2274:       - name: total_workers_ever_assigned
2275:         data_type: BIGINT
2276:         description: Distinct worker count ever assigned to the position; defaults to 0 when no history
2277:         tests:
2278:         - total_workers_ever_assigned >= 0
2279:       - name: current_workers_assigned
2280:         data_type: BIGINT
2281:         description: Distinct worker count with an open assignment (no end date); defaults to 0
2282:         tests:
2283:         - current_workers_assigned >= 0
2284:       - name: former_workers_assigned
2285:         data_type: BIGINT
2286:         description: Distinct worker count with a closed assignment (has end date); defaults to 0
2287:         tests:
2288:         - former_workers_assigned >= 0
2289:       - name: position_occupancy_status
2290:         data_type: VARCHAR
2291:         description: Occupied if current_workers_assigned>0; else Vacant (Previously Occupied) if total>0; else Vacant (Never Occupied); defaults to 'Unknown' if missing
2292:       - name: avg_tenure_years_in_position
2293:         data_type: DOUBLE
2294:         description: Average tenure in years based on assignment days/365, rounded to 2 decimals; open assignments use today; defaults to 0.00
2295:         tests:
2296:         - avg_tenure_years_in_position >= 0
2297:       - name: last_assignment_date
2298:         data_type: DATE
2299:         description: Most recent assignment start date; falls back to position_created_date when none
2300:       - name: last_departure_date
2301:         data_type: DATE
2302:         description: Most recent assignment end date; NULL when none
2303:       - name: new_assignments_last_year
2304:         data_type: BIGINT
2305:         description: Distinct worker count with assignment start within the past 12 months; defaults to 0
2306:         tests:
2307:         - new_assignments_last_year >= 0
2308:       - name: departures_last_year
2309:         data_type: BIGINT
2310:         description: Distinct worker count with assignment end within the past 12 months; defaults to 0
2311:         tests:
2312:         - departures_last_year >= 0
2313:       - name: position_turnover_rate
2314:         data_type: DOUBLE
2315:         description: If total_workers_ever_assigned=0 then 0; otherwise departures_last_year divided by total_workers_ever_assigned as a percentage, rounded to 2 decimals
2316:         tests:
2317:         - position_turnover_rate >= 0
2318:       - name: organization_id
2319:         data_type: VARCHAR
2320:         description: Organization identifier for the position; defaults to 'Unknown' when absent
2321:       - name: organization_name
2322:         data_type: VARCHAR
2323:         description: Organization name; defaults to 'Unknown' when absent
2324:       - name: organization_type
2325:         data_type: VARCHAR
2326:         description: Organization type; defaults to 'Unknown' when absent
2327:       - name: organization_sub_type
2328:         data_type: VARCHAR
2329:         description: Organization sub-type; defaults to 'Unknown' when absent
2330:       - name: staffing_model
2331:         data_type: VARCHAR
2332:         description: Organization staffing model; defaults to 'Unknown' when absent
2333:       - name: department_total_employees
2334:         data_type: BIGINT
2335:         description: Current employee count for the organization from org metrics; defaults to 0
2336:         tests:
2337:         - department_total_employees >= 0
2338:       - name: department_health_score
2339:         data_type: INTEGER
2340:         description: Organization health score (0–100) from org metrics; defaults to 0
2341:         tests:
2342:         - department_health_score BETWEEN 0 AND 100
2343:       - name: department_turnover_rate
2344:         data_type: DOUBLE
2345:         description: Annual turnover rate from org metrics; defaults to 0.0
2346:         tests:
2347:         - department_turnover_rate >= 0
2348:       - name: department_performance_level
2349:         data_type: VARCHAR
2350:         description: Organization performance category from org metrics; defaults to 'Unknown'
2351:       - name: department_size_category
2352:         data_type: VARCHAR
2353:         description: Organization size category from org metrics; defaults to 'Unknown'
2354:       - name: similar_positions_in_department
2355:         data_type: BIGINT
2356:         description: Count of positions with the same organization_id and job_profile_id across the dataset; defaults to 0
2357:         tests:
2358:         - similar_positions_in_department >= 0
2359:       - name: job_profile_id
2360:         data_type: VARCHAR
2361:         description: Job profile identifier linked to the position; defaults to 'Unknown'
2362:       - name: job_profile_title
2363:         data_type: VARCHAR
2364:         description: Job profile title; defaults to 'Unknown'
2365:       - name: management_level
2366:         data_type: VARCHAR
2367:         description: Management level from job profile; defaults to 'Unknown'
2368:       - name: compensation_grade_id
2369:         data_type: VARCHAR
2370:         description: Compensation grade identifier from job profile; defaults to 'Ungraded'
2371:       - name: compensation_tier
2372:         data_type: VARCHAR
2373:         description: 'Tier derived from compensation_grade_id digits: Entry ≤5; Mid ≤10; Senior ≤15; Executive >15; ''Ungraded'' when NULL or not numeric'
2374:       - name: is_work_shift_required
2375:         data_type: BOOLEAN
2376:         description: True if work shift is required per job profile; defaults to false when NULL
2377:       - name: is_union_eligible
2378:         data_type: BOOLEAN
2379:         description: True if union eligible per job profile; defaults to false when NULL
2380:       - name: challenging_work_conditions_score
2381:         data_type: INTEGER
2382:         description: Sum of indicators (shift required, union eligible, weekly hours>40); range 0–3; defaults to 0
2383:         tests:
2384:         - challenging_work_conditions_score BETWEEN 0 AND 3
2385:       - name: management_level_numeric
2386:         data_type: INTEGER
2387:         description: 'Numeric mapping of management_level: Director=4, Senior Manager=3, Manager=2, Individual Contributor=1, else 0'
2388:         tests:
2389:         - management_level_numeric >= 0
2390:       - name: avg_employee_performance_score
2391:         data_type: DOUBLE
2392:         description: Average overall_employee_score for currently employed workers; rounded to 2 decimals; defaults to 0.00
2393:         tests:
2394:         - avg_employee_performance_score BETWEEN 0 AND 100
2395:       - name: avg_career_development_score
2396:         data_type: DOUBLE
2397:         description: Average career_development_score for currently employed workers; rounded to 2 decimals; defaults to 0.00
2398:         tests:
2399:         - avg_career_development_score BETWEEN 0 AND 100
2400:       - name: avg_retention_score
2401:         data_type: DOUBLE
2402:         description: Average retention_stability_score for currently employed workers; rounded to 2 decimals; defaults to 0.00
2403:         tests:
2404:         - avg_retention_score BETWEEN 0 AND 100
2405:       - name: high_risk_employees_count
2406:         data_type: BIGINT
2407:         description: Distinct count of workers flagged 'High Risk' regardless of current employment; defaults to 0
2408:         tests:
2409:         - high_risk_employees_count >= 0
2410:       - name: medium_risk_employees_count
2411:         data_type: BIGINT
2412:         description: Distinct count of workers flagged 'Medium Risk' regardless of current employment; defaults to 0
2413:         tests:
2414:         - medium_risk_employees_count >= 0
2415:       - name: low_risk_employees_count
2416:         data_type: BIGINT
2417:         description: Distinct count of workers flagged 'Low Risk' regardless of current employment; defaults to 0
2418:         tests:
2419:         - low_risk_employees_count >= 0
2420:       - name: high_value_employees_count
2421:         data_type: BIGINT
2422:         description: Distinct count of workers in 'High Value - High Retention' segment; defaults to 0
2423:         tests:
2424:         - high_value_employees_count >= 0
2425:       - name: flight_risk_employees_count
2426:         data_type: BIGINT
2427:         description: Distinct count of workers in 'High Value - Flight Risk' segment; defaults to 0
2428:         tests:
2429:         - flight_risk_employees_count >= 0
2430:       - name: new_employees_count
2431:         data_type: BIGINT
2432:         description: Distinct count of currently employed workers with maturity like '%New Hire%'; defaults to 0
2433:         tests:
2434:         - new_employees_count >= 0
2435:       - name: veteran_employees_count
2436:         data_type: BIGINT
2437:         description: Distinct count of currently employed workers with maturity like '%Veteran%'; defaults to 0
2438:         tests:
2439:         - veteran_employees_count >= 0
2440:       - name: avg_employee_age
2441:         data_type: DOUBLE
2442:         description: Average age of currently employed workers; rounded to 1 decimal; defaults to 0.0
2443:         tests:
2444:         - avg_employee_age >= 0
2445:       - name: ethnic_diversity_count
2446:         data_type: BIGINT
2447:         description: Distinct count of ethnicity_codes among currently employed workers; defaults to 0
2448:         tests:
2449:         - ethnic_diversity_count >= 0
2450:       - name: military_veterans_count
2451:         data_type: BIGINT
2452:         description: Distinct count of currently employed workers with military service; defaults to 0
2453:         tests:
2454:         - military_veterans_count >= 0
2455:       - name: position_efficiency_score
2456:         data_type: DOUBLE
2457:         description: Composite score (0–100) of occupancy, tenure, employee performance, and department health; rounded to 2 decimals
2458:         tests:
2459:         - position_efficiency_score BETWEEN 0 AND 100
2460:       - name: position_performance_category
2461:         data_type: VARCHAR
2462:         description: Position classification by vacancy, performance, tenure, and turnover using ordered rules; see business_logic for precedence
2463:       - name: management_priority
2464:         data_type: VARCHAR
2465:         description: Recommended management focus based on vacancy, risk, performance, and department health; ordered rule evaluation
2466:       - name: cost_performance_analysis
2467:         data_type: VARCHAR
2468:         description: Cost-performance label based on default_weekly_hours and current employee performance; ordered rule evaluation
2469:       - name: strategic_recommendation
2470:         data_type: VARCHAR
2471:         description: Forward-looking recommendation using vacancy age, similar roles count, flight risk, and performance; ordered rule evaluation
2472:       - name: data_quality_flag
2473:         data_type: VARCHAR
2474:         description: Row-level quality status based on title presence, hours sanity, over-assignment, and age consistency; ordered checks return first match
2475:       - name: analysis_timestamp
2476:         data_type: TIMESTAMP WITH TIME ZONE
2477:         description: Query execution timestamp (time zone aware) for when the analysis was generated
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__position_overview.sql`，SHA-256 `fc830506f229efeb49c2fedefbf1364067881b2b3975f9ab2c40da7c586b9d8c`，行 1–43。

```
1: WITH base AS (SELECT * FROM staging.stg_workday__position), history AS (
2:  SELECT position_id,source_relation,count(DISTINCT worker_id) total_workers_ever_assigned,count(DISTINCT worker_id) FILTER(WHERE effective_end IS NULL) current_workers_assigned,count(DISTINCT worker_id) FILTER(WHERE effective_end IS NOT NULL) former_workers_assigned,
3:  avg(date_diff('day',effective_start,coalesce(effective_end,current_date))) avg_tenure_days,max(effective_start) last_assignment_date,max(effective_end) last_departure_date,
4:  count(DISTINCT worker_id) FILTER(WHERE effective_start>=current_date-INTERVAL '1 year') new_assignments_last_year,count(DISTINCT worker_id) FILTER(WHERE effective_end>=current_date-INTERVAL '1 year') departures_last_year
5:  FROM staging.stg_workday__worker_position GROUP BY position_id,source_relation
6: ), po AS (
7:  SELECT position_id,source_relation,organization_id,effective_end,row_number() over(partition by position_id,source_relation order by effective_start desc) rn FROM staging.stg_workday__position_organization
8: ), profiles AS (
9:  SELECT pjp.position_id,pjp.source_relation,pjp.job_profile_id,jp.job_profile_title,jp.management_level,jp.compensation_grade_id,jp.is_work_shift_required,jp.is_union_eligible FROM staging.stg_workday__position_job_profile pjp LEFT JOIN staging.stg_workday__job_profile jp USING(job_profile_id,source_relation)
10: ), orgs AS (
11:  SELECT organization_id,source_relation,organization_name,organization_type,organization_sub_type,staffing_model,current_employee_count,organization_health_score,annual_turnover_rate,performance_category,organization_size_category FROM intermediate.int_workday__organization_metrics
12: ), similar_positions AS (
13:  SELECT po.organization_id,pr.job_profile_id,count(DISTINCT b.position_id) similar_positions_in_department FROM base b LEFT JOIN po ON b.position_id=po.position_id AND b.source_relation=po.source_relation AND po.rn=1 LEFT JOIN profiles pr ON b.position_id=pr.position_id AND b.source_relation=pr.source_relation GROUP BY po.organization_id,pr.job_profile_id
14: ), emp AS (
15:  SELECT position_id,source_relation,avg(overall_employee_score) FILTER(WHERE is_employed) avg_employee_performance_score,avg(career_development_score) FILTER(WHERE is_employed) avg_career_development_score,avg(retention_stability_score) FILTER(WHERE is_employed) avg_retention_score,
16:  count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='High Risk') high_risk_employees_count,count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='Medium Risk') medium_risk_employees_count,count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='Low Risk') low_risk_employees_count,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='High Value - High Retention') high_value_employees_count,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='High Value - Flight Risk') flight_risk_employees_count,
17:  count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%New Hire%') new_employees_count,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Veteran%') veteran_employees_count,avg(age) FILTER(WHERE is_employed) avg_employee_age,count(DISTINCT ethnicity_codes) FILTER(WHERE is_employed AND ethnicity_codes IS NOT NULL) ethnic_diversity_count,count(DISTINCT worker_id) FILTER(WHERE is_employed AND is_military_service) military_veterans_count
18:  FROM mart.workday__employee_overview GROUP BY position_id,source_relation
19: ), joined AS (
20:  SELECT b.*,coalesce(h.total_workers_ever_assigned,0) total_workers_ever_assigned,coalesce(h.current_workers_assigned,0) current_workers_assigned,coalesce(h.former_workers_assigned,0) former_workers_assigned,coalesce(h.avg_tenure_days,0) avg_tenure_days,h.last_assignment_date,h.last_departure_date,coalesce(h.new_assignments_last_year,0) new_assignments_last_year,coalesce(h.departures_last_year,0) departures_last_year,
21:  coalesce(po.organization_id,'Unknown') organization_id,coalesce(o.organization_name,'Unknown') organization_name,coalesce(o.organization_type,'Unknown') organization_type,coalesce(o.organization_sub_type,'Unknown') organization_sub_type,coalesce(o.staffing_model,'Unknown') staffing_model,coalesce(o.current_employee_count,0) department_total_employees,coalesce(o.organization_health_score,0) department_health_score,coalesce(o.annual_turnover_rate,0) department_turnover_rate,coalesce(o.performance_category,'Unknown') department_performance_level,coalesce(o.organization_size_category,'Unknown') department_size_category,
22:  coalesce(pr.job_profile_id,'Unknown') job_profile_id,coalesce(pr.job_profile_title,'Unknown') job_profile_title,coalesce(pr.management_level,'Unknown') management_level,coalesce(pr.compensation_grade_id,'Ungraded') compensation_grade_id,coalesce(pr.is_work_shift_required,FALSE) is_work_shift_required,coalesce(pr.is_union_eligible,FALSE) is_union_eligible,
23:  coalesce(s.similar_positions_in_department,0) similar_positions_in_department,coalesce(e.avg_employee_performance_score,0) avg_employee_performance_score,coalesce(e.avg_career_development_score,0) avg_career_development_score,coalesce(e.avg_retention_score,0) avg_retention_score,coalesce(e.high_risk_employees_count,0) high_risk_employees_count,coalesce(e.medium_risk_employees_count,0) medium_risk_employees_count,coalesce(e.low_risk_employees_count,0) low_risk_employees_count,coalesce(e.high_value_employees_count,0) high_value_employees_count,coalesce(e.flight_risk_employees_count,0) flight_risk_employees_count,coalesce(e.new_employees_count,0) new_employees_count,coalesce(e.veteran_employees_count,0) veteran_employees_count,coalesce(e.avg_employee_age,0) avg_employee_age,coalesce(e.ethnic_diversity_count,0) ethnic_diversity_count,coalesce(e.military_veterans_count,0) military_veterans_count
24:  FROM base b LEFT JOIN history h USING(position_id,source_relation) LEFT JOIN po ON b.position_id=po.position_id AND b.source_relation=po.source_relation AND po.rn=1 LEFT JOIN orgs o ON po.organization_id=o.organization_id AND po.source_relation=o.source_relation LEFT JOIN profiles pr USING(position_id,source_relation) LEFT JOIN similar_positions s ON po.organization_id=s.organization_id AND pr.job_profile_id=s.job_profile_id LEFT JOIN emp e USING(position_id,source_relation)
25: ), final AS (
26:  SELECT *,date_diff('day',effective_start,current_date)::BIGINT position_age_days,coalesce(last_assignment_date,effective_start) last_assignment_date_out,
27:  CASE WHEN regexp_extract(compensation_grade_id,'([0-9]+)',1)='' THEN 'Ungraded' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=5 THEN 'Entry Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=10 THEN 'Mid Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=15 THEN 'Senior Level' ELSE 'Executive Level' END compensation_tier
28:  FROM joined
29: )
30: SELECT position_id,source_relation,business_title,employee_type,default_weekly_hours,effective_start position_created_date,position_age_days,
31: CASE WHEN position_age_days<90 THEN 'New Position (<3 months)' WHEN position_age_days<365 THEN 'Recent Position (3-12 months)' WHEN position_age_days<730 THEN 'Established Position (1-2 years)' WHEN position_age_days<1825 THEN 'Mature Position (2-5 years)' ELSE 'Legacy Position (5+ years)' END position_age_category,
32: total_workers_ever_assigned,current_workers_assigned,former_workers_assigned,CASE WHEN current_workers_assigned>0 THEN 'Occupied' WHEN total_workers_ever_assigned>0 THEN 'Vacant (Previously Occupied)' ELSE 'Vacant (Never Occupied)' END position_occupancy_status,round(avg_tenure_days/365.0,2)::DOUBLE avg_tenure_years_in_position,last_assignment_date_out last_assignment_date,last_departure_date,new_assignments_last_year,departures_last_year,CASE WHEN total_workers_ever_assigned=0 THEN 0 ELSE round(departures_last_year*100.0/total_workers_ever_assigned,2) END::DOUBLE position_turnover_rate,
33: organization_id,organization_name,organization_type,organization_sub_type,staffing_model,department_total_employees,department_health_score,department_turnover_rate,department_performance_level,department_size_category,similar_positions_in_department,job_profile_id,job_profile_title,management_level,compensation_grade_id,compensation_tier,is_work_shift_required,is_union_eligible,
34: (CASE WHEN is_work_shift_required THEN 1 ELSE 0 END+CASE WHEN is_union_eligible THEN 1 ELSE 0 END+CASE WHEN default_weekly_hours>40 THEN 1 ELSE 0 END)::INTEGER challenging_work_conditions_score,
35: CASE management_level WHEN 'Director' THEN 4 WHEN 'Senior Manager' THEN 3 WHEN 'Manager' THEN 2 WHEN 'Individual Contributor' THEN 1 ELSE 0 END::INTEGER management_level_numeric,round(avg_employee_performance_score,2)::DOUBLE avg_employee_performance_score,round(avg_career_development_score,2)::DOUBLE avg_career_development_score,round(avg_retention_score,2)::DOUBLE avg_retention_score,
36: high_risk_employees_count,medium_risk_employees_count,low_risk_employees_count,high_value_employees_count,flight_risk_employees_count,new_employees_count,veteran_employees_count,round(avg_employee_age,1)::DOUBLE avg_employee_age,ethnic_diversity_count,military_veterans_count,
37: round((CASE WHEN current_workers_assigned>0 THEN 25 ELSE 0 END+CASE WHEN avg_tenure_days>=730 THEN 25 WHEN avg_tenure_days>=365 THEN 20 WHEN avg_tenure_days>=180 THEN 15 ELSE 10 END+least(30,avg_employee_performance_score*.3)+least(20,department_health_score*.2)),2)::DOUBLE position_efficiency_score,
38: CASE WHEN current_workers_assigned=0 THEN 'Vacant Position' WHEN avg_employee_performance_score>=80 AND avg_tenure_days>=730 THEN 'High-Performance Stable Position' WHEN avg_employee_performance_score>=70 THEN 'High-Performance Position' WHEN avg_tenure_days>=730 THEN 'Stable Position' WHEN departures_last_year>1 THEN 'High-Turnover Position' ELSE 'Standard Position' END position_performance_category,
39: CASE WHEN current_workers_assigned=0 AND position_age_days>180 THEN 'Review Position Necessity' WHEN high_risk_employees_count>0 THEN 'Focus on Retention' WHEN avg_employee_performance_score<50 THEN 'Performance Improvement Needed' WHEN department_health_score<50 THEN 'Department Support Needed' WHEN avg_employee_performance_score>=80 THEN 'Maintain Excellence' ELSE 'Standard Management' END management_priority,
40: CASE WHEN current_workers_assigned=0 THEN 'No Current Cost' WHEN default_weekly_hours>40 AND avg_employee_performance_score<60 THEN 'High Cost - Low Performance' WHEN default_weekly_hours>40 AND avg_employee_performance_score>=80 THEN 'High Cost - High Performance' WHEN default_weekly_hours<=40 AND avg_employee_performance_score>=80 THEN 'Optimal Cost-Performance' ELSE 'Standard Cost-Performance' END cost_performance_analysis,
41: CASE WHEN current_workers_assigned=0 AND position_age_days>365 THEN 'Consider Position Elimination' WHEN similar_positions_in_department>5 THEN 'Consider Position Consolidation' WHEN flight_risk_employees_count>0 THEN 'Develop Succession Plan' WHEN avg_employee_performance_score>=90 THEN 'Consider Position Expansion' ELSE 'Maintain Current Structure' END strategic_recommendation,
42: CASE WHEN business_title IS NULL OR trim(business_title)='' THEN 'ERROR: Missing title' WHEN default_weekly_hours<=0 THEN 'ERROR: Invalid weekly hours' WHEN position_age_days<0 THEN 'ERROR: Future position date' WHEN default_weekly_hours>80 OR current_workers_assigned>3 THEN 'WARNING: Position anomaly' ELSE 'VALID' END data_quality_flag,current_timestamp::TIMESTAMPTZ analysis_timestamp
43: FROM final
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__position_overview.sql`，SHA-256 `80c4528ab6bc9f497a919c9287059040f1d49a51daec28f7e9300e167b54b0ea`，行 1–338。

```
1: -- Position configuration and efficiency analysis data mart - Provides position utilization, efficiency, and cost analysis
2: -- Support human resource allocation optimization and organizational structure design decisions
3: 
4: with position_base_info as (
5:     select 
6:         p.*,
7:         -- Position age calculation
8:         date_diff('day', p.effective_start, current_date) as position_age_days,
9:         case 
10:             when date_diff('day', p.effective_start, current_date) < 90 then 'New Position (<3 months)'
11:             when date_diff('day', p.effective_start, current_date) < 365 then 'Recent Position (3-12 months)'
12:             when date_diff('day', p.effective_start, current_date) < 365*2 then 'Established Position (1-2 years)'
13:             when date_diff('day', p.effective_start, current_date) < 365*5 then 'Mature Position (2-5 years)'
14:             else 'Legacy Position (5+ years)'
15:         end as position_age_category
16:     from staging.stg_workday__position p
17: ),
18: 
19: -- Job history and usage
20: position_utilization_history as (
21:     select 
22:         p.position_id,
23:         p.source_relation,
24:         
25:         -- Historical resume statistics
26:         count(distinct wph.worker_id) as total_workers_ever_assigned,
27:         count(distinct case when wph.effective_end is null then wph.worker_id end) as current_workers_assigned,
28:         count(distinct case when wph.effective_end is not null then wph.worker_id end) as former_workers_assigned,
29:         
30:         -- Position utilization calculation
31:         case 
32:             when count(distinct case when wph.effective_end is null then wph.worker_id end) > 0 then 'Occupied'
33:             when count(distinct wph.worker_id) > 0 then 'Vacant (Previously Occupied)'
34:             else 'Vacant (Never Occupied)'
35:         end as position_occupancy_status,
36:         
37:         -- Average tenure
38:         avg(case when wph.effective_end is not null 
39:             then date_diff('day', wph.effective_start, wph.effective_end)
40:             else date_diff('day', wph.effective_start, current_date)
41:         end) as avg_tenure_days_in_position,
42:         
43:         -- last change
44:         max(wph.effective_start) as last_assignment_date,
45:         max(wph.effective_end) as last_departure_date,
46:         
47:         -- liquidity indicator
48:         count(distinct case when wph.effective_start >= current_date - interval '1 year' then wph.worker_id end) as new_assignments_last_year,
49:         count(distinct case when wph.effective_end >= current_date - interval '1 year' and wph.effective_end is not null then wph.worker_id end) as departures_last_year
50:         
51:     from staging.stg_workday__position p
52:     left join staging.stg_workday__worker_position wph
53:         on p.position_id = wph.position_id
54:         and p.source_relation = wph.source_relation
55:     group by p.position_id, p.source_relation
56: ),
57: 
58: -- Position organizational relationships and geographical distribution
59: position_organizational_context as (
60:     select 
61:         p.position_id,
62:         p.source_relation,
63:         
64:         -- organize information
65:         o.organization_id,
66:         o.organization_name,
67:         o.organization_type,
68:         o.organization_sub_type,
69:         o.staffing_model,
70:         
71:         -- organizational performance indicators
72:         om.current_employee_count as dept_total_employees,
73:         om.organization_health_score as dept_health_score,
74:         om.annual_turnover_rate as dept_turnover_rate,
75:         om.performance_category as dept_performance_level,
76:         om.organization_size_category as dept_size_category,
77:         
78:         -- Number of similar positions in the organization
79:         count(*) over (partition by o.organization_id, jp.job_profile_id) as similar_positions_in_dept
80:         
81:     from staging.stg_workday__position p
82:     left join staging.stg_workday__position_organization po
83:         on p.position_id = po.position_id
84:         and p.source_relation = po.source_relation
85:     left join staging.stg_workday__organization o
86:         on po.organization_id = o.organization_id
87:         and po.source_relation = o.source_relation
88:     left join intermediate.int_workday__organization_metrics om
89:         on o.organization_id = om.organization_id
90:         and o.source_relation = om.source_relation
91:     left join staging.stg_workday__position_job_profile pjp
92:         on p.position_id = pjp.position_id
93:         and p.source_relation = pjp.source_relation
94:     left join staging.stg_workday__job_profile jp
95:         on pjp.job_profile_id = jp.job_profile_id
96:         and pjp.source_relation = jp.source_relation
97: ),
98: 
99: -- Job Compensation and Benefits Information
100: position_compensation_benefits as (
101:     select 
102:         p.position_id,
103:         p.source_relation,
104:         
105:         -- Position information
106:         jp.job_profile_id,
107:         jp.job_profile_title,
108:         jp.management_level,
109:         jp.compensation_grade_id,
110:         jp.is_work_shift_required,
111:         jp.is_union_eligible,
112:         
113:         -- Pay grade analysis
114:         case 
115:             when jp.compensation_grade_id is null then 'Ungraded'
116:             when try_cast(regexp_extract(jp.compensation_grade_id, '\\d+', 0) as int) <= 5 then 'Entry Level'
117:             when try_cast(regexp_extract(jp.compensation_grade_id, '\\d+', 0) as int) <= 10 then 'Mid Level'
118:             when try_cast(regexp_extract(jp.compensation_grade_id, '\\d+', 0) as int) <= 15 then 'Senior Level'
119:             when try_cast(regexp_extract(jp.compensation_grade_id, '\\d+', 0) as int) > 15 then 'Executive Level'
120:             else 'Ungraded'
121:         end as compensation_tier,
122:         
123:         -- working conditions rating
124:         (case when jp.is_work_shift_required then 1 else 0 end +
125:          case when jp.is_union_eligible then 1 else 0 end +
126:          case when p.default_weekly_hours > 40 then 1 else 0 end) as challenging_work_conditions_score,
127:         
128:         -- Digitizing management levels
129:         case 
130:             when jp.management_level = 'Director' then 4
131:             when jp.management_level = 'Senior Manager' then 3
132:             when jp.management_level = 'Manager' then 2
133:             when jp.management_level = 'Individual Contributor' then 1
134:             else 0
135:         end as management_level_numeric
136:         
137:     from staging.stg_workday__position p
138:     left join staging.stg_workday__position_job_profile pjp
139:         on p.position_id = pjp.position_id
140:         and p.source_relation = pjp.source_relation
141:     left join staging.stg_workday__job_profile jp
142:         on pjp.job_profile_id = jp.job_profile_id
143:         and pjp.source_relation = jp.source_relation
144: ),
145: 
146: -- Performance data of current employees
147: current_employee_performance as (
148:     select 
149:         p.position_id,
150:         p.source_relation,
151:         
152:         -- Current employee performance indicators
153:         avg(case when eo.is_employed then eo.overall_employee_score end) as avg_employee_performance_score,
154:         avg(case when eo.is_employed then eo.career_development_score end) as avg_career_development_score,
155:         avg(case when eo.is_employed then eo.retention_stability_score end) as avg_retention_score,
156:         
157:         -- Employee risk distribution
158:         count(distinct case when eo.employee_risk_level = 'High Risk' then eo.worker_id end) as high_risk_employees_count,
159:         count(distinct case when eo.employee_risk_level = 'Medium Risk' then eo.worker_id end) as medium_risk_employees_count,
160:         count(distinct case when eo.employee_risk_level = 'Low Risk' then eo.worker_id end) as low_risk_employees_count,
161:         
162:         -- employee value segments
163:         count(distinct case when eo.employee_value_segment = 'High Value - High Retention' then eo.worker_id end) as high_value_employees_count,
164:         count(distinct case when eo.employee_value_segment = 'High Value - Flight Risk' then eo.worker_id end) as flight_risk_employees_count,
165:         
166:         -- Employee maturity distribution
167:         count(distinct case when eo.employee_maturity_segment like '%New Hire%' and eo.is_employed then eo.worker_id end) as new_employees_count,
168:         count(distinct case when eo.employee_maturity_segment like '%Veteran%' and eo.is_employed then eo.worker_id end) as veteran_employees_count,
169:         
170:         -- age and diversity
171:         avg(case when eo.is_employed then eo.age end) as avg_employee_age,
172:         count(distinct case when eo.is_employed then eo.ethnicity_codes end) as ethnic_diversity_count,
173:         count(distinct case when eo.is_employed and eo.is_military_service then eo.worker_id end) as military_veterans_count
174:         
175:     from staging.stg_workday__position p
176:     left join mart.workday__employee_overview eo
177:         on p.position_id = eo.position_id
178:         and p.source_relation = eo.source_relation
179:     group by p.position_id, p.source_relation
180: )
181: 
182: select 
183:     pbi.position_id,
184:     pbi.source_relation,
185:     pbi.business_title,
186:     pbi.employee_type,
187:     pbi.default_weekly_hours,
188:     pbi.effective_start as position_created_date,
189:     pbi.position_age_days,
190:     pbi.position_age_category,
191:     
192:     -- Utilization and occupancy
193:     coalesce(puh.total_workers_ever_assigned, 0) as total_workers_ever_assigned,
194:     coalesce(puh.current_workers_assigned, 0) as current_workers_assigned,
195:     coalesce(puh.former_workers_assigned, 0) as former_workers_assigned,
196:     coalesce(puh.position_occupancy_status, 'Unknown') as position_occupancy_status,
197:     
198:     -- efficiency index
199:     round(coalesce(puh.avg_tenure_days_in_position, 0) / 365.0, 2) as avg_tenure_years_in_position,
200:     coalesce(puh.last_assignment_date, pbi.effective_start) as last_assignment_date,
201:     coalesce(puh.last_departure_date, null) as last_departure_date,
202:     coalesce(puh.new_assignments_last_year, 0) as new_assignments_last_year,
203:     coalesce(puh.departures_last_year, 0) as departures_last_year,
204:     
205:     -- liquidity indicator
206:     case 
207:         when coalesce(puh.total_workers_ever_assigned, 0) = 0 then 0
208:         else round(coalesce(puh.departures_last_year, 0) * 100.0 / puh.total_workers_ever_assigned, 2)
209:     end as position_turnover_rate,
210:     
211:     -- organizational context
212:     coalesce(poc.organization_id, 'Unknown') as organization_id,
213:     coalesce(poc.organization_name, 'Unknown') as organization_name,
214:     coalesce(poc.organization_type, 'Unknown') as organization_type,
215:     coalesce(poc.organization_sub_type, 'Unknown') as organization_sub_type,
216:     coalesce(poc.staffing_model, 'Unknown') as staffing_model,
217:     coalesce(poc.dept_total_employees, 0) as department_total_employees,
218:     coalesce(poc.dept_health_score, 0) as department_health_score,
219:     coalesce(poc.dept_turnover_rate, 0) as department_turnover_rate,
220:     coalesce(poc.dept_performance_level, 'Unknown') as department_performance_level,
221:     coalesce(poc.dept_size_category, 'Unknown') as department_size_category,
222:     coalesce(poc.similar_positions_in_dept, 0) as similar_positions_in_department,
223:     
224:     -- Salary and position information
225:     coalesce(pcb.job_profile_id, 'Unknown') as job_profile_id,
226:     coalesce(pcb.job_profile_title, 'Unknown') as job_profile_title,
227:     coalesce(pcb.management_level, 'Unknown') as management_level,
228:     coalesce(pcb.compensation_grade_id, 'Ungraded') as compensation_grade_id,
229:     coalesce(pcb.compensation_tier, 'Ungraded') as compensation_tier,
230:     coalesce(pcb.is_work_shift_required, false) as is_work_shift_required,
231:     coalesce(pcb.is_union_eligible, false) as is_union_eligible,
232:     coalesce(pcb.challenging_work_conditions_score, 0) as challenging_work_conditions_score,
233:     coalesce(pcb.management_level_numeric, 0) as management_level_numeric,
234:     
235:     -- Current employee performance
236:     round(coalesce(cep.avg_employee_performance_score, 0), 2) as avg_employee_performance_score,
237:     round(coalesce(cep.avg_career_development_score, 0), 2) as avg_career_development_score,
238:     round(coalesce(cep.avg_retention_score, 0), 2) as avg_retention_score,
239:     
240:     -- risk distribution
241:     coalesce(cep.high_risk_employees_count, 0) as high_risk_employees_count,
242:     coalesce(cep.medium_risk_employees_count, 0) as medium_risk_employees_count,
243:     coalesce(cep.low_risk_employees_count, 0) as low_risk_employees_count,
244:     
245:     -- value segment
246:     coalesce(cep.high_value_employees_count, 0) as high_value_employees_count,
247:     coalesce(cep.flight_risk_employees_count, 0) as flight_risk_employees_count,
248:     
249:     -- Staff composition
250:     coalesce(cep.new_employees_count, 0) as new_employees_count,
251:     coalesce(cep.veteran_employees_count, 0) as veteran_employees_count,
252:     round(coalesce(cep.avg_employee_age, 0), 1) as avg_employee_age,
253:     coalesce(cep.ethnic_diversity_count, 0) as ethnic_diversity_count,
254:     coalesce(cep.military_veterans_count, 0) as military_veterans_count,
255:     
256:     -- Job effectiveness rating (0-100)
257:     round(
258:         (-- Occupancy (25%)
259:          case when coalesce(puh.current_workers_assigned, 0) > 0 then 25 else 0 end +
260:          -- Retention stability (25%)
261:          case when coalesce(puh.avg_tenure_days_in_position, 0) >= 365*2 then 25
262:               when coalesce(puh.avg_tenure_days_in_position, 0) >= 365 then 20
263:               when coalesce(puh.avg_tenure_days_in_position, 0) >= 180 then 15
264:               else 10 end +
265:          -- Employee performance (30%)
266:          least(30, coalesce(cep.avg_employee_performance_score, 0) * 0.3) +
267:          -- Department Health (20%)
268:          least(20, coalesce(poc.dept_health_score, 0) * 0.2))
269:     , 2) as position_efficiency_score,
270:     
271:     -- Job type classification
272:     case 
273:         when coalesce(puh.current_workers_assigned, 0) = 0 then 'Vacant Position'
274:         when coalesce(cep.avg_employee_performance_score, 0) >= 80 and coalesce(puh.avg_tenure_days_in_position, 0) >= 365*2 then 'High-Performance Stable Position'
275:         when coalesce(cep.avg_employee_performance_score, 0) >= 70 then 'High-Performance Position'
276:         when coalesce(puh.avg_tenure_days_in_position, 0) >= 365*2 then 'Stable Position'
277:         when coalesce(puh.departures_last_year, 0) > 1 then 'High-Turnover Position'
278:         else 'Standard Position'
279:     end as position_performance_category,
280:     
281:     -- investment priorities
282:     case 
283:         when coalesce(puh.current_workers_assigned, 0) = 0 and pbi.position_age_days > 180 then 'Review Position Necessity'
284:         when coalesce(cep.high_risk_employees_count, 0) > 0 then 'Focus on Retention'
285:         when coalesce(cep.avg_employee_performance_score, 0) < 50 then 'Performance Improvement Needed'
286:         when coalesce(poc.dept_health_score, 0) < 50 then 'Department Support Needed'
287:         when coalesce(cep.avg_employee_performance_score, 0) >= 80 then 'Maintain Excellence'
288:         else 'Standard Management'
289:     end as management_priority,
290:     
291:     -- cost benefit analysis
292:     case 
293:         when coalesce(puh.current_workers_assigned, 0) = 0 then 'No Current Cost'
294:         when pbi.default_weekly_hours > 40 and coalesce(cep.avg_employee_performance_score, 0) < 60 then 'High Cost - Low Performance'
295:         when pbi.default_weekly_hours > 40 and coalesce(cep.avg_employee_performance_score, 0) >= 80 then 'High Cost - High Performance'
296:         when pbi.default_weekly_hours <= 40 and coalesce(cep.avg_employee_performance_score, 0) >= 80 then 'Optimal Cost-Performance'
297:         else 'Standard Cost-Performance'
298:     end as cost_performance_analysis,
299:     
300:     -- Suggestions for future planning
301:     case 
302:         when coalesce(puh.current_workers_assigned, 0) = 0 and pbi.position_age_days > 365 then 'Consider Position Elimination'
303:         when coalesce(poc.similar_positions_in_dept, 0) > 5 then 'Consider Position Consolidation'
304:         when coalesce(cep.flight_risk_employees_count, 0) > 0 then 'Develop Succession Plan'
305:         when coalesce(cep.avg_employee_performance_score, 0) >= 90 then 'Consider Position Expansion'
306:         else 'Maintain Current Structure'
307:     end as strategic_recommendation,
308:     
309:     -- Data quality check
310:     case 
311:         when pbi.business_title is null or pbi.business_title = '' then 'ERROR: Missing position title'
312:         when pbi.default_weekly_hours <= 0 then 'ERROR: Invalid working hours'
313:         when pbi.default_weekly_hours > 80 then 'WARNING: Excessive working hours'
314:         when coalesce(puh.current_workers_assigned, 0) > 3 then 'WARNING: Position may be over-assigned'
315:         when pbi.position_age_days < 0 then 'ERROR: Invalid position creation date'
316:         else 'VALID'
317:     end as data_quality_flag,
318:     
319:     -- Analysis timestamp
320:     current_timestamp as analysis_timestamp
321:     
322: from position_base_info pbi
323: left join position_utilization_history puh
324:     on pbi.position_id = puh.position_id
325:     and pbi.source_relation = puh.source_relation
326: left join position_organizational_context poc
327:     on pbi.position_id = poc.position_id
328:     and pbi.source_relation = poc.source_relation
329: left join position_compensation_benefits pcb
330:     on pbi.position_id = pcb.position_id
331:     and pbi.source_relation = pcb.source_relation
332: left join current_employee_performance cep
333:     on pbi.position_id = cep.position_id
334:     and pbi.source_relation = cep.source_relation
335: order by 
336:     coalesce(puh.current_workers_assigned, 0) desc,
337:     coalesce(cep.avg_employee_performance_score, 0) desc,
338:     pbi.position_age_days desc
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 15/16 已查看 job_profile/organization 列；event 51 写岗位模型；event 83 未解释 grade 正则及省略非 active 组织维度。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/15.json`。
- event 16：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/16.json`。
- event 51：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/51.json`。
- event 83：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/83.json`。
## 查询

核实查询 **0** 条；核实代价档：**需要查业务说明**。诊断查询不计入 5 条上限。

未追加 agent 可见数据核实；判断依据为契约、SQL 和明确标为诊断的查询，不用 gold 结果证明 U。

### 诊断：组织和 NULL 连接

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`。

```sql
SELECT (SELECT count(*) FROM staging.stg_workday__organization WHERE is_inactive) inactive_orgs,(SELECT count(*) FROM staging.stg_workday__position_organization po WHERE NOT EXISTS(SELECT 1 FROM staging.stg_workday__organization o WHERE po.organization_id=o.organization_id)) orphan_relations
```


```json
{"columns":["inactive_orgs","orphan_relations"],"rows":[[111,30]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-016_workday__position_overview.json](../023_reruns_impl-016_workday__position_overview.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`。

共同时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":4}]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4000|4000|4000|11816|否|
|L1|4000|4000|4000|11816|否|
|L2|4000|4000|4000|11816|否|
|L3|4000|4000|4000|11816|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L1：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L2：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L3：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-016_workday__position_overview/baseline.sql`；SHA-256 `0857da0b96164e3105c2c4f384a21eb91f94e1ff5d2f4a04f27163fd2bdf31bf`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4000|4000|4000|11816|否|
|L1|4000|4000|4000|11816|否|
|L2|4000|4000|4000|11816|否|
|L3|4000|4000|4000|11816|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L1：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L2：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L3：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`

#### compensation_regex

判定：主因；类别候选 O。契约要求提取首段数字，agent 符合；gold 双反斜杠正则对当前 grade 未提取数字。常量仅为定位 gold 差异的诊断。

相对本轮基线减少行 2024、格 4000；按行优先、格次之排序。
共同控制后 SQL 第 27 行起、字符 offset 6456 的唯一连续替换；其余字节不动。
替换前：
```sql
CASE WHEN regexp_extract(compensation_grade_id,'([0-9]+)',1)='' THEN 'Ungraded' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=5 THEN 'Entry Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=10 THEN 'Mid Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=15 THEN 'Senior Level' ELSE 'Executive Level' END
```

替换后：
```sql
'Ungraded'
```

私有 SQL：`data/023_work/impl-016_workday__position_overview/compensation_regex.sql`；SHA-256 `5cd218d27fecbc1414bf47226998a612d6a5c9c121b90a4502b15eb7a41f2337`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4000|4000|1976|7816|否|
|L1|4000|4000|1976|7816|否|
|L2|4000|4000|1976|7816|否|
|L3|4000|4000|1976|7816|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L1：`{"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L2：`{"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L3：`{"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`

#### organization_dimension

判定：参与因素；类别候选 C。契约组织维度应来自 organization，agent 只读 active organization metrics，丢失非 active 组织属性。

相对本轮基线减少行 0、格 7784；按行优先、格次之排序。
共同控制后 SQL 第 11 行起、字符 offset 1392 的唯一连续替换；其余字节不动。
替换前：
```sql
SELECT organization_id,source_relation,organization_name,organization_type,organization_sub_type,staffing_model,current_employee_count,organization_health_score,annual_turnover_rate,performance_category,organization_size_category FROM intermediate.int_workday__organization_metrics
```

替换后：
```sql
SELECT o.organization_id,o.source_relation,o.organization_name,o.organization_type,o.organization_sub_type,o.staffing_model,m.current_employee_count,m.organization_health_score,m.annual_turnover_rate,m.performance_category,m.organization_size_category FROM staging.stg_workday__organization o LEFT JOIN intermediate.int_workday__organization_metrics m USING(organization_id,source_relation)
```

私有 SQL：`data/023_work/impl-016_workday__position_overview/organization_dimension.sql`；SHA-256 `5ab0034a502517486d32c923606d235ba10e14bd5f3081b6a1a89b082a9b05d7`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4000|4000|4000|4032|否|
|L1|4000|4000|4000|4032|否|
|L2|4000|4000|4000|4032|否|
|L3|4000|4000|4000|4032|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"compensation_tier":4000,"organization_id":30,"similar_positions_in_department":2}`
- L1：`{"compensation_tier":4000,"organization_id":30,"similar_positions_in_department":2}`
- L2：`{"compensation_tier":4000,"organization_id":30,"similar_positions_in_department":2}`
- L3：`{"compensation_tier":4000,"organization_id":30,"similar_positions_in_department":2}`

#### organization_id

判定：不计参与因素；类别候选 A。组织关联不存在时保留关系 ID 还是输出 Unknown。

相对本轮基线减少行 0、格 -1916；按行优先、格次之排序。
共同控制后 SQL 第 21 行起、字符 offset 3912 的唯一连续替换；其余字节不动。
替换前：
```sql
coalesce(po.organization_id,'Unknown') organization_id
```

替换后：
```sql
coalesce(o.organization_id,'Unknown') organization_id
```

私有 SQL：`data/023_work/impl-016_workday__position_overview/organization_id.sql`；SHA-256 `a6e70360b81fd927fb4846e88a5fdc6954c0d98e15b15d965d0a963ff72ba501`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4000|4000|4000|13732|否|
|L1|4000|4000|4000|13732|否|
|L2|4000|4000|4000|13732|否|
|L3|4000|4000|4000|13732|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"compensation_tier":4000,"organization_id":1946,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L1：`{"compensation_tier":4000,"organization_id":1946,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L2：`{"compensation_tier":4000,"organization_id":1946,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L3：`{"compensation_tier":4000,"organization_id":1946,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
### 补充轮：[023_supplement_reruns_impl-016_workday__position_overview.json](../023_supplement_reruns_impl-016_workday__position_overview.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`。

共同时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":4}]`。

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_supplement_work/impl-016_workday__position_overview/baseline.sql`；SHA-256 `0857da0b96164e3105c2c4f384a21eb91f94e1ff5d2f4a04f27163fd2bdf31bf`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4000|4000|4000|11816|否|
|L1|4000|4000|4000|11816|否|
|L2|4000|4000|4000|11816|否|
|L3|4000|4000|4000|11816|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L1：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L2：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`
- L3：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":2,"staffing_model":1946}`

#### similar_group

判定：不计参与因素；类别候选 C。相似岗位按实际组织维度分组；孤儿组织关系归 NULL 组。

相对本轮基线减少行 0、格 -28；按行优先、格次之排序。
共同控制后 SQL 第 13 行起、字符 offset 1700 的唯一连续替换；其余字节不动。
替换前：
```sql
 SELECT po.organization_id,pr.job_profile_id,count(DISTINCT b.position_id) similar_positions_in_department FROM base b LEFT JOIN po ON b.position_id=po.position_id AND b.source_relation=po.source_relation AND po.rn=1 LEFT JOIN profiles pr ON b.position_id=pr.position_id AND b.source_relation=pr.source_relation GROUP BY po.organization_id,pr.job_profile_id
```

替换后：
```sql
 SELECT o.organization_id,pr.job_profile_id,count(*) similar_positions_in_department FROM base b LEFT JOIN po ON b.position_id=po.position_id AND b.source_relation=po.source_relation AND po.rn=1 LEFT JOIN staging.stg_workday__organization o ON po.organization_id=o.organization_id AND po.source_relation=o.source_relation LEFT JOIN profiles pr ON b.position_id=pr.position_id AND b.source_relation=pr.source_relation GROUP BY o.organization_id,pr.job_profile_id
```

私有 SQL：`data/023_supplement_work/impl-016_workday__position_overview/similar_group.sql`；SHA-256 `2a4a3f4df9ae8aa458de079137d169be1035cdbea20c73f364d18e145d00f576`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4000|4000|4000|11844|否|
|L1|4000|4000|4000|11844|否|
|L2|4000|4000|4000|11844|否|
|L3|4000|4000|4000|11844|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":30,"staffing_model":1946}`
- L1：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":30,"staffing_model":1946}`
- L2：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":30,"staffing_model":1946}`
- L3：`{"compensation_tier":4000,"organization_id":30,"organization_name":1946,"organization_sub_type":1946,"organization_type":1946,"similar_positions_in_department":30,"staffing_model":1946}`

## 原始表改动核对

raw.person_contact_email_address initial/gold 7284、agent 2448。查完原始事件0–84、run.py 导入源码及013写操作清单，只有event39/40、53/54、65/66导入事件，输出均为7284；未找到削减到2448的命令或原因。不能把导入日志当作削减证据。

初始/gold 一致而 agent 有变化，依第 3 节照常标注，不标不可评估。完整表清单见 [023_raw_trace_review.json](../023_raw_trace_review.json)；输入不变性另由前后指纹验证。

## 规则问题

无
