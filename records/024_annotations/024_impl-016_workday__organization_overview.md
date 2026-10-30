# impl-016 · workday__organization_overview

用途：**校准**；层：**marts**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**多因并列（C、O）**；把握：中。

两处零分母漏0为C，两处契约短枚举与gold全称冲突为O，各减少117格；连接权重5格、角色聚合106格为C参与因素。

参与因素：C：assignment_join（行减0，格减5）；C：role_count_expression（行减0，格减71）。
标记：无。

## 材料与比较口径

[013_impl-016_marts_workday__organization_overview.md](../013_packages/013_impl-016_marts_workday__organization_overview.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml`。

```text
2024:     - name: workday__organization_overview
2025:       description: Executive-ready overview of each active organization with headcount, roles, tenure, mobility, risk, performance, diversity, compensation tiers, promotions, derived scores, recommendations, and data quality
2026:       grain: One row per active organization_id and source_relation
2027:       source_models:
2028:       - staging.stg_workday__organization (filtered to is_inactive = false)
2029:       - staging.stg_workday__worker_position_organization
2030:       - staging.stg_workday__organization_role_worker
2031:       - staging.stg_workday__organization_role
2032:       - mart.workday__employee_overview (filtered to organization_id != 'Unknown')
2033:       business_logic: '1) Filter organizations to active only and expose attributes and effective_start as the creation date. 2) Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id. For each assignment: - assignment_status: ''Active Assignment'' if end date is null, else ''Former Assignment''. - assignment_duration_days: days between start and end; if end is null, days between start and current_date. - carry organization_role_id and organization_role_code from the role join. 3) Aggregate organization_employee_stats by (organization_id, source_relation): - total_employees_ever: distinct workers across all assignments. - current_active_employees: distinct workers with Active Assignment. - former_employees: distinct workers with Former Assignment. - total_positions_in_org: distinct positions across all assignments. - active_positions_count: distinct positions with Active Assignment. - new_assignments_last_year: distinct workers with start date in the last year relative to current_date. - departures_last_year: distinct workers with a non-null end date in the last year. - avg_current_tenure_days: average assignment_duration_days for Active Assignments. - avg_former_tenure_days: average assignment_duration_days for Former Assignments. - unique_organization_roles: distinct organization_role_id. - management_role_employees / director_role_employees / lead_role_employees: distinct workers where role code contains ''Manager'' / ''Director'' / ''Lead''. - last_new_assignment_date: most recent start date; last_departure_date: most recent end date. 4) Aggregate organization_performance_metrics from mart.workday__employee_overview by (organization_id, source_relation), excluding organization_id = ''Unknown'': - Averages over currently employed workers only: overall_employee_score and career_development_score rounded to 2 decimals; retention_stability_score rounded to 2 decimals; age rounded to 1 decimal. - Employee value segments: distinct workers by segment (''High Value - High Retention'', ''High Value - Flight Risk'', ''Stable - Development Needed'', ''Development Required''); no employment filter. - Risk distribution: distinct workers by employee_risk_level (High/Medium/Low); no employment filter. - Maturity segments: distinct employed workers where maturity contains ''New Hire'' / ''Junior'' / ''Experienced'' / ''Senior'' / ''Veteran''. - Diversity: distinct ethnicity_codes among employed; military_veterans_count is distinct employed workers flagged for military service. - Compensation tiers: distinct employed workers by compensation_tier (Entry/Mid/Senior/Executive Level). - Promotions among employed: total_promotions summed; high_achievers_count is distinct workers with total_promotions ≥ 2; fast_track_employees_count is distinct workers with fast_promotions > 0. 5) Derive organization attributes per active organization: - organization_created_date from effective_start. - organization_age_days as days from creation to current_date; organization_age_years is that divided by 365, rounded to 2 decimals. - organization_maturity_level by age_days: <1 year New; 1–3 years Young; 3–10 years Mature; 10+ years Legacy. - organizational_level from organization_type: Company/Division/Department/Team mapped to corresponding Level; others to Other Level. - access_level from visibility: Public→Open Access, Private→Restricted Access, others Unknown Access. 6) Final metrics and rules (rates rounded to 2 decimals; missing metrics default to 0 unless noted): - position_fill_rate (%) = current_active_employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), and risk (10/7/4/2 by high_risk_employee_percentage thresholds); final score rounded to 2 decimals. - performance_category uses a weighted composite with thresholds: Excellent if composite ≥ 80; else Good if ≥ 60; else Average if ≥ 40; otherwise Needs Improvement (weights and constants follow the detailed rules above). - organization_size_category by current_active_employees: 0 Empty; ≤5 Micro; ≤15 Small; ≤50 Medium; ≤200 Large; else Enterprise. - last_activity_date is the most recent assignment start; if none, use organization_created_date. - last_departure_date is the most recent assignment end; if none, use 1900-01-01. - management_recommendation (first match): if no active employees then review necessity; else if turnover > 30% then focus on retention; else if high-risk % > 25% then address risk; else if fill rate < 70% then improve staffing; else if average performance < 50 then enhance performance management; else if management_ratio > 40% then optimize structure; else maintain excellence. - data_quality_flag precedence: missing or blank organization name → ERROR; active employees exceed positions by more than 10 → WARNING; turnover rate > 100% → WARNING; negative age days → ERROR; otherwise VALID. - analysis_timestamp is the query execution timestamp. 7) Join logic: left join employee stats and performance metrics to active organizations on (organization_id, source_relation); missing measures default to 0. The final ordering is for presentation only and does not affect grain.'
2034:       columns:
2035:       - name: organization_id
2036:         data_type: VARCHAR
2037:         description: Organization identifier; join key to stats and metrics; one output row per active (organization_id, source_relation)
2038:         tests:
2039:         - not_null
2040:       - name: source_relation
2041:         data_type: VARCHAR
2042:         description: Source system code carried from staging and used in all joins
2043:         tests:
2044:         - not_null
2045:       - name: organization_name
2046:         data_type: VARCHAR
2047:         description: Organization display name from the active organization record
2048:       - name: organization_code
2049:         data_type: VARCHAR
2050:         description: Organization code from the active organization record
2051:       - name: organization_type
2052:         data_type: VARCHAR
2053:         description: Organization type (e.g., Company, Division, Department, Team)
2054:       - name: organization_sub_type
2055:         data_type: VARCHAR
2056:         description: Subtype of the organization if provided in source
2057:       - name: staffing_model
2058:         data_type: VARCHAR
2059:         description: Staffing model from source organization attributes
2060:       - name: visibility
2061:         data_type: VARCHAR
2062:         description: Visibility setting from source; drives access_level mapping
2063:       - name: access_level
2064:         data_type: VARCHAR
2065:         description: 'Derived access control: Public→Open Access, Private→Restricted Access, else Unknown Access'
2066:       - name: organization_created_date
2067:         data_type: DATE
2068:         description: Effective start date of the active organization record
2069:       - name: organization_age_days
2070:         data_type: BIGINT
2071:         description: Days since organization_created_date to current_date at run time
2072:       - name: organization_age_years
2073:         data_type: DOUBLE
2074:         description: Rounded years since creation = round(organization_age_days/365.0, 2)
2075:       - name: organization_maturity_level
2076:         data_type: VARCHAR
2077:         description: 'Age bucket: <1y New; 1–3y Young; 3–10y Mature; 10+y Legacy based on organization_age_days'
2078:       - name: organizational_level
2079:         data_type: VARCHAR
2080:         description: 'Level mapped from organization_type: Company/Division/Department/Team→Corporate/Division/Department/Team Level; else Other Level'
2081:       - name: total_employees_ever
2082:         data_type: BIGINT
2083:         description: Distinct workers ever assigned to the org; defaults to 0 when missing
2084:       - name: current_active_employees
2085:         data_type: BIGINT
2086:         description: Distinct workers with Active Assignment at run time; defaults to 0 when missing
2087:       - name: former_employees
2088:         data_type: BIGINT
2089:         description: Distinct workers with Former Assignment; defaults to 0 when missing
2090:       - name: total_positions
2091:         data_type: BIGINT
2092:         description: Distinct positions ever assigned within the org; defaults to 0 when missing
2093:       - name: active_positions_count
2094:         data_type: BIGINT
2095:         description: Distinct positions with Active Assignment; defaults to 0 when missing
2096:       - name: position_fill_rate
2097:         data_type: DOUBLE
2098:         description: Filled positions % = round(current_active_employees*100.0/total_positions, 2); 0 if total_positions=0
2099:       - name: new_assignments_last_year
2100:         data_type: BIGINT
2101:         description: Distinct workers with assignment start in the last year; defaults to 0 when missing
2102:       - name: departures_last_year
2103:         data_type: BIGINT
2104:         description: Distinct workers with non-null assignment end in the last year; defaults to 0 when missing
2105:       - name: annual_turnover_rate
2106:         data_type: DOUBLE
2107:         description: Departures % = round(departures_last_year*100.0/current_active_employees, 2); 0 if denominator=0
2108:       - name: avg_current_tenure_years
2109:         data_type: DOUBLE
2110:         description: Average tenure (years) for Active Assignments = round(avg_current_tenure_days/365.0, 2) with NULL→0
2111:       - name: avg_former_tenure_years
2112:         data_type: DOUBLE
2113:         description: Average tenure (years) for Former Assignments = round(avg_former_tenure_days/365.0, 2) with NULL→0
2114:       - name: unique_organization_roles
2115:         data_type: BIGINT
2116:         description: Distinct organization_role_id linked to the org; defaults to 0 when missing
2117:       - name: management_role_employees
2118:         data_type: BIGINT
2119:         description: Distinct workers with role code containing 'Manager'; defaults to 0 when missing
2120:       - name: director_role_employees
2121:         data_type: BIGINT
2122:         description: Distinct workers with role code containing 'Director'; defaults to 0 when missing
2123:       - name: lead_role_employees
2124:         data_type: BIGINT
2125:         description: Distinct workers with role code containing 'Lead'; defaults to 0 when missing
2126:       - name: management_ratio
2127:         data_type: DOUBLE
2128:         description: Management share % = round((management_role_employees+director_role_employees)*100.0/current_active_employees, 2); 0 if denominator=0
2129:       - name: avg_employee_performance_score
2130:         data_type: DOUBLE
2131:         description: Avg overall_employee_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved
2132:       - name: avg_career_development_score
2133:         data_type: DOUBLE
2134:         description: Avg career_development_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved
2135:       - name: avg_retention_stability_score
2136:         data_type: DOUBLE
2137:         description: Avg retention_stability_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved
2138:       - name: high_value_stable_employees
2139:         data_type: BIGINT
2140:         description: Distinct workers in 'High Value - High Retention'; defaults to 0 when missing
2141:       - name: high_value_flight_risk_employees
2142:         data_type: BIGINT
2143:         description: Distinct workers in 'High Value - Flight Risk'; defaults to 0 when missing
2144:       - name: stable_development_employees
2145:         data_type: BIGINT
2146:         description: Distinct workers in 'Stable - Development Needed'; defaults to 0 when missing
2147:       - name: development_required_employees
2148:         data_type: BIGINT
2149:         description: Distinct workers in 'Development Required'; defaults to 0 when missing
2150:       - name: high_risk_employees
2151:         data_type: BIGINT
2152:         description: Distinct workers with employee_risk_level = 'High Risk'; defaults to 0 when missing
2153:       - name: medium_risk_employees
2154:         data_type: BIGINT
2155:         description: Distinct workers with employee_risk_level = 'Medium Risk'; defaults to 0 when missing
2156:       - name: low_risk_employees
2157:         data_type: BIGINT
2158:         description: Distinct workers with employee_risk_level = 'Low Risk'; defaults to 0 when missing
2159:       - name: high_risk_employee_percentage
2160:         data_type: DOUBLE
2161:         description: High-risk share % = round(high_risk_employees*100.0/current_active_employees, 2); 0 if denominator=0
2162:       - name: new_hire_employees
2163:         data_type: BIGINT
2164:         description: Distinct employed workers with maturity containing 'New Hire'; defaults to 0 when missing
2165:       - name: junior_employees
2166:         data_type: BIGINT
2167:         description: Distinct employed workers with maturity containing 'Junior'; defaults to 0 when missing
2168:       - name: experienced_employees
2169:         data_type: BIGINT
2170:         description: Distinct employed workers with maturity containing 'Experienced'; defaults to 0 when missing
2171:       - name: senior_employees
2172:         data_type: BIGINT
2173:         description: Distinct employed workers with maturity containing 'Senior'; defaults to 0 when missing
2174:       - name: veteran_employees
2175:         data_type: BIGINT
2176:         description: Distinct employed workers with maturity containing 'Veteran'; defaults to 0 when missing
2177:       - name: ethnic_diversity_count
2178:         data_type: BIGINT
2179:         description: Count of distinct ethnicity_codes among employed; defaults to 0 when missing
2180:       - name: military_veterans_count
2181:         data_type: BIGINT
2182:         description: Distinct employed workers with military service flag; defaults to 0 when missing
2183:       - name: avg_employee_age
2184:         data_type: DOUBLE
2185:         description: Average age among employed, rounded to 1 in source aggregation; defaults to 0 when missing
2186:       - name: entry_level_employees
2187:         data_type: BIGINT
2188:         description: Distinct employed workers in compensation_tier = 'Entry Level'; defaults to 0 when missing
2189:       - name: mid_level_employees
2190:         data_type: BIGINT
2191:         description: Distinct employed workers in compensation_tier = 'Mid Level'; defaults to 0 when missing
2192:       - name: senior_level_employees
2193:         data_type: BIGINT
2194:         description: Distinct employed workers in compensation_tier = 'Senior Level'; defaults to 0 when missing
2195:       - name: executive_level_employees
2196:         data_type: BIGINT
2197:         description: Distinct employed workers in compensation_tier = 'Executive Level'; defaults to 0 when missing
2198:       - name: total_promotions_in_organization
2199:         data_type: HUGEINT
2200:         description: Sum of total_promotions for employed workers in the org; defaults to 0 when missing
2201:       - name: high_achievers_count
2202:         data_type: BIGINT
2203:         description: Distinct employed workers with total_promotions >= 2; defaults to 0 when missing
2204:       - name: fast_track_employees_count
2205:         data_type: BIGINT
2206:         description: Distinct employed workers with fast_promotions > 0; defaults to 0 when missing
2207:       - name: organization_health_score
2208:         data_type: DOUBLE
2209:         description: Composite 0–100 score from performance, turnover, development, fill-rate efficiency, and risk components; rounded to 2
2210:       - name: performance_category
2211:         data_type: VARCHAR
2212:         description: 'Category from the weighted composite: Excellent (>=80), Good (>=60), Average (>=40), else Needs Improvement'
2213:       - name: organization_size_category
2214:         data_type: VARCHAR
2215:         description: 'Size bucket by current_active_employees: Empty, Micro (<=5), Small (<=15), Medium (<=50), Large (<=200), Enterprise (>200)'
2216:       - name: last_activity_date
2217:         data_type: DATE
2218:         description: Most recent assignment start date; if none, falls back to organization_created_date
2219:       - name: last_departure_date
2220:         data_type: DATE
2221:         description: Most recent assignment end date; if none, defaults to 1900-01-01
2222:       - name: management_recommendation
2223:         data_type: VARCHAR
2224:         description: Recommendation based on thresholds of size, turnover, high-risk %, fill rate, performance, and management ratio; first matching rule applies
2225:       - name: data_quality_flag
2226:         data_type: VARCHAR
2227:         description: VALID or specific ERROR/WARNING based on missing name, employee>position anomaly, turnover >100%, or negative age days
2228:       - name: analysis_timestamp
2229:         data_type: TIMESTAMP WITH TIME ZONE
2230:         description: current_timestamp at run time indicating when the analysis was computed
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql`；SHA-256 `b59173eeea3ae826802f8b6de9e99a323a7fbc82ab691ec5c31009dc9b51a552`。

```text
1: WITH active_org AS (SELECT * FROM staging.stg_workday__organization WHERE is_inactive=FALSE), rel AS (
2:  SELECT worker_id,organization_id,source_relation,position_id,effective_start,effective_end,
3:  date_diff('day',effective_start,coalesce(effective_end,current_date)) duration,
4:  CASE WHEN effective_end IS NULL THEN 'Active Assignment' ELSE 'Former Assignment' END status
5:  FROM staging.stg_workday__worker_position_organization
6: ), stats AS (
7:  SELECT organization_id,source_relation,count(DISTINCT worker_id) total_employees_ever,count(DISTINCT worker_id) FILTER(WHERE effective_end IS NULL) current_active_employees,count(DISTINCT worker_id) FILTER(WHERE effective_end IS NOT NULL) former_employees,count(DISTINCT position_id) total_positions,count(DISTINCT position_id) FILTER(WHERE effective_end IS NULL) active_positions_count,
8:  count(DISTINCT worker_id) FILTER(WHERE effective_start>=current_date-INTERVAL '1 year') new_assignments_last_year,count(DISTINCT worker_id) FILTER(WHERE effective_end>=current_date-INTERVAL '1 year') departures_last_year,avg(duration) FILTER(WHERE effective_end IS NULL) avg_current_days,avg(duration) FILTER(WHERE effective_end IS NOT NULL) avg_former_days,max(effective_start) last_activity_date,max(effective_end) last_departure_date
9:  FROM rel GROUP BY organization_id,source_relation
10: ), roles AS (
11:  SELECT ow.organization_id,'workday' source_relation,count(DISTINCT r.organization_role_id) unique_organization_roles,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Manager%') management_role_employees,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Director%') director_role_employees,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Lead%') lead_role_employees FROM staging.stg_workday__organization_role_worker ow LEFT JOIN staging.stg_workday__organization_role r ON ow.organization_id=r.organization_id AND ow.role_id=r.organization_role_id GROUP BY ow.organization_id
12: ), perf AS (
13:  SELECT organization_id,source_relation,avg(overall_employee_score) FILTER(WHERE is_employed) avg_employee_performance_score,avg(career_development_score) FILTER(WHERE is_employed) avg_career_development_score,avg(retention_stability_score) FILTER(WHERE is_employed) avg_retention_stability_score,
14:  count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='High Value - High Retention') high_value_stable_employees,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='High Value - Flight Risk') high_value_flight_risk_employees,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='Stable - Development Needed') stable_development_employees,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='Development Required') development_required_employees,
15:  count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='High Risk') high_risk_employees,count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='Medium Risk') medium_risk_employees,count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='Low Risk') low_risk_employees,
16:  count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%New Hire%') new_hire_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Junior%') junior_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Experienced%') experienced_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Senior%') senior_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Veteran%') veteran_employees,
17:  count(DISTINCT ethnicity_codes) FILTER(WHERE is_employed AND ethnicity_codes IS NOT NULL) ethnic_diversity_count,count(DISTINCT worker_id) FILTER(WHERE is_employed AND is_military_service) military_veterans_count,avg(age) FILTER(WHERE is_employed) avg_employee_age,
18:  count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Entry Level') entry_level_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Mid Level') mid_level_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Senior Level') senior_level_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Executive Level') executive_level_employees,
19:  sum(total_promotions) FILTER(WHERE is_employed) total_promotions_in_organization,count(DISTINCT worker_id) FILTER(WHERE is_employed AND total_promotions>=2) high_achievers_count,count(DISTINCT worker_id) FILTER(WHERE is_employed AND fast_promotions>0) fast_track_employees_count
20:  FROM mart.workday__employee_overview WHERE organization_id<>'Unknown' GROUP BY organization_id,source_relation
21: ), joined AS (SELECT o.*,s.*,r.unique_organization_roles,r.management_role_employees,r.director_role_employees,r.lead_role_employees,p.* EXCLUDE(organization_id,source_relation) FROM active_org o LEFT JOIN stats s USING(organization_id,source_relation) LEFT JOIN roles r USING(organization_id,source_relation) LEFT JOIN perf p USING(organization_id,source_relation))
22: SELECT organization_id,source_relation,organization_name,organization_code,organization_type,organization_sub_type,staffing_model,visibility,
23: CASE visibility WHEN 'Public' THEN 'Open Access' WHEN 'Private' THEN 'Restricted Access' ELSE 'Unknown Access' END access_level,effective_start organization_created_date,date_diff('day',effective_start,current_date)::BIGINT organization_age_days,round(date_diff('day',effective_start,current_date)/365.0,2)::DOUBLE organization_age_years,
24: CASE WHEN date_diff('day',effective_start,current_date)<365 THEN 'New' WHEN date_diff('day',effective_start,current_date)<1095 THEN 'Young' WHEN date_diff('day',effective_start,current_date)<3650 THEN 'Mature' ELSE 'Legacy' END organization_maturity_level,
25: CASE organization_type WHEN 'Company' THEN 'Corporate Level' WHEN 'Division' THEN 'Division Level' WHEN 'Department' THEN 'Department Level' WHEN 'Team' THEN 'Team Level' ELSE 'Other Level' END organizational_level,
26: coalesce(total_employees_ever,0)::BIGINT total_employees_ever,coalesce(current_active_employees,0)::BIGINT current_active_employees,coalesce(former_employees,0)::BIGINT former_employees,coalesce(total_positions,0)::BIGINT total_positions,coalesce(active_positions_count,0)::BIGINT active_positions_count,
27: round(coalesce(current_active_employees,0)*100.0/NULLIF(total_positions,0),2)::DOUBLE position_fill_rate,coalesce(new_assignments_last_year,0)::BIGINT new_assignments_last_year,coalesce(departures_last_year,0)::BIGINT departures_last_year,round(coalesce(departures_last_year,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE annual_turnover_rate,
28: round(coalesce(avg_current_days,0)/365.0,2)::DOUBLE avg_current_tenure_years,round(coalesce(avg_former_days,0)/365.0,2)::DOUBLE avg_former_tenure_years,coalesce(unique_organization_roles,0)::BIGINT unique_organization_roles,coalesce(management_role_employees,0)::BIGINT management_role_employees,coalesce(director_role_employees,0)::BIGINT director_role_employees,coalesce(lead_role_employees,0)::BIGINT lead_role_employees,
29: round((coalesce(management_role_employees,0)+coalesce(director_role_employees,0))*100.0/NULLIF(current_active_employees,0),2)::DOUBLE management_ratio,coalesce(avg_employee_performance_score,0)::DOUBLE avg_employee_performance_score,coalesce(avg_career_development_score,0)::DOUBLE avg_career_development_score,coalesce(avg_retention_stability_score,0)::DOUBLE avg_retention_stability_score,
30: coalesce(high_value_stable_employees,0)::BIGINT high_value_stable_employees,coalesce(high_value_flight_risk_employees,0)::BIGINT high_value_flight_risk_employees,coalesce(stable_development_employees,0)::BIGINT stable_development_employees,coalesce(development_required_employees,0)::BIGINT development_required_employees,coalesce(high_risk_employees,0)::BIGINT high_risk_employees,coalesce(medium_risk_employees,0)::BIGINT medium_risk_employees,coalesce(low_risk_employees,0)::BIGINT low_risk_employees,
31: round(coalesce(high_risk_employees,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE high_risk_employee_percentage,coalesce(new_hire_employees,0)::BIGINT new_hire_employees,coalesce(junior_employees,0)::BIGINT junior_employees,coalesce(experienced_employees,0)::BIGINT experienced_employees,coalesce(senior_employees,0)::BIGINT senior_employees,coalesce(veteran_employees,0)::BIGINT veteran_employees,coalesce(ethnic_diversity_count,0)::BIGINT ethnic_diversity_count,coalesce(military_veterans_count,0)::BIGINT military_veterans_count,coalesce(avg_employee_age,0)::DOUBLE avg_employee_age,
32: coalesce(entry_level_employees,0)::BIGINT entry_level_employees,coalesce(mid_level_employees,0)::BIGINT mid_level_employees,coalesce(senior_level_employees,0)::BIGINT senior_level_employees,coalesce(executive_level_employees,0)::BIGINT executive_level_employees,coalesce(total_promotions_in_organization,0)::HUGEINT total_promotions_in_organization,coalesce(high_achievers_count,0)::BIGINT high_achievers_count,coalesce(fast_track_employees_count,0)::BIGINT fast_track_employees_count,
33: round(least(30,coalesce(avg_employee_performance_score,0)*.3)+CASE WHEN departures_last_year=0 THEN 25 WHEN annual_turnover_rate<=10 THEN 25 WHEN annual_turnover_rate<=20 THEN 20 WHEN annual_turnover_rate<=30 THEN 15 WHEN annual_turnover_rate<=40 THEN 10 ELSE 5 END+least(20,coalesce(avg_career_development_score,0)*.2)+CASE WHEN position_fill_rate>=90 THEN 15 WHEN position_fill_rate>=75 THEN 12 WHEN position_fill_rate>=60 THEN 9 ELSE 6 END+CASE WHEN high_risk_employee_percentage<=10 THEN 10 WHEN high_risk_employee_percentage<=20 THEN 7 WHEN high_risk_employee_percentage<=30 THEN 4 ELSE 2 END,2)::DOUBLE organization_health_score,
34: CASE WHEN avg_employee_performance_score>=80 THEN 'Excellent' WHEN avg_employee_performance_score>=60 THEN 'Good' WHEN avg_employee_performance_score>=40 THEN 'Average' ELSE 'Needs Improvement' END performance_category,
35: CASE WHEN current_active_employees=0 THEN 'Empty' WHEN current_active_employees<=5 THEN 'Micro' WHEN current_active_employees<=15 THEN 'Small' WHEN current_active_employees<=50 THEN 'Medium' WHEN current_active_employees<=200 THEN 'Large' ELSE 'Enterprise' END organization_size_category,
36: coalesce(last_activity_date,effective_start) last_activity_date,coalesce(last_departure_date,DATE '1900-01-01') last_departure_date,
37: CASE WHEN current_active_employees=0 THEN 'Review Organization Necessity' WHEN annual_turnover_rate>30 THEN 'Focus on Retention' WHEN high_risk_employee_percentage>25 THEN 'Address Employee Risk' WHEN position_fill_rate<70 THEN 'Improve Staffing' WHEN avg_employee_performance_score<50 THEN 'Enhance Performance Management' WHEN management_ratio>40 THEN 'Optimize Structure' ELSE 'Maintain Excellence' END management_recommendation,
38: CASE WHEN organization_name IS NULL OR trim(organization_name)='' THEN 'ERROR: Missing organization name' WHEN current_active_employees>total_positions+10 THEN 'WARNING: Employees exceed positions' WHEN annual_turnover_rate>100 THEN 'WARNING: Turnover exceeds 100%' WHEN organization_age_days<0 THEN 'ERROR: Negative organization age' ELSE 'VALID' END data_quality_flag,current_timestamp::TIMESTAMPTZ analysis_timestamp
39: FROM joined
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql`；SHA-256 `9136e4c5f8b13dee3c505ecfa78716722fea6b404d492a942905c25777d64526`。

```text
1: -- Organizational structure and relationship overview data mart - provides a comprehensive view of organizational hierarchy, role assignments, and employee distribution
2: -- Support organizational structure analysis, management level optimization, and cross-department collaboration analysis
3: 
4: with organization_base as (
5:     select * 
6:     from staging.stg_workday__organization
7:     where not is_inactive  -- Only include active organizations
8: ),
9: 
10: -- Organizational roles and employee relations
11: organization_employee_relationships as (
12:     select 
13:         wpo.organization_id,
14:         wpo.source_relation,
15:         wpo.worker_id,
16:         wpo.position_id,
17:         wpo.effective_start as assignment_start_date,
18:         wpo.effective_end as assignment_end_date,
19:         
20:         -- current allocation status
21:         case when wpo.effective_end is null then 'Active Assignment' else 'Former Assignment' end as assignment_status,
22:         
23:         -- Assign duration
24:         case 
25:             when wpo.effective_end is not null then 
26:                 date_diff('day', wpo.effective_start, wpo.effective_end)
27:             else 
28:                 date_diff('day', wpo.effective_start, current_date)
29:         end as assignment_duration_days,
30:         
31:         -- Organization role information  
32:         orw.role_id as organization_role_id,
33:         org_role.organization_role_code
34:         
35:     from staging.stg_workday__worker_position_organization wpo
36:     left join staging.stg_workday__organization_role_worker orw
37:         on wpo.worker_id = orw.organization_worker_code
38:         and wpo.source_relation = orw.source_relation
39:     left join staging.stg_workday__organization_role org_role
40:         on orw.role_id = org_role.organization_role_id
41:         and orw.source_relation = org_role.source_relation
42:         and wpo.organization_id = org_role.organization_id
43: ),
44: 
45: -- Organizational employee statistics and performance summary
46: organization_employee_stats as (
47:     select 
48:         oer.organization_id,
49:         oer.source_relation,
50:         
51:         -- Basic employee statistics
52:         count(distinct oer.worker_id) as total_employees_ever,
53:         count(distinct case when oer.assignment_status = 'Active Assignment' then oer.worker_id end) as current_active_employees,
54:         count(distinct case when oer.assignment_status = 'Former Assignment' then oer.worker_id end) as former_employees,
55:         count(distinct oer.position_id) as total_positions_in_org,
56:         count(distinct case when oer.assignment_status = 'Active Assignment' then oer.position_id end) as active_positions_count,
57:         
58:         -- Employee turnover statistics
59:         count(distinct case when oer.assignment_start_date >= current_date - interval '1 year' then oer.worker_id end) as new_assignments_last_year,
60:         count(distinct case when oer.assignment_end_date >= current_date - interval '1 year' and oer.assignment_end_date is not null then oer.worker_id end) as departures_last_year,
61:         
62:         -- Average tenure
63:         avg(case when oer.assignment_status = 'Active Assignment' then oer.assignment_duration_days end) as avg_current_tenure_days,
64:         avg(case when oer.assignment_status = 'Former Assignment' then oer.assignment_duration_days end) as avg_former_tenure_days,
65:         
66:         -- Organizational role distribution
67:         count(distinct oer.organization_role_id) as unique_organization_roles,
68:         count(distinct case when oer.organization_role_code like '%Manager%' then oer.worker_id end) as management_role_employees,
69:         count(distinct case when oer.organization_role_code like '%Director%' then oer.worker_id end) as director_role_employees,
70:         count(distinct case when oer.organization_role_code like '%Lead%' then oer.worker_id end) as lead_role_employees,
71:         
72:         -- Latest event date
73:         max(oer.assignment_start_date) as last_new_assignment_date,
74:         max(oer.assignment_end_date) as last_departure_date
75:         
76:     from organization_employee_relationships oer
77:     group by oer.organization_id, oer.source_relation
78: ),
79: 
80: -- Organizational performance and employee quality indicators (based on employee overview data)
81: organization_performance_metrics as (
82:     select 
83:         eo.organization_id,
84:         eo.source_relation,
85:         
86:         -- employee performance indicators
87:         round(avg(case when eo.is_employed then eo.overall_employee_score end), 2) as avg_employee_performance,
88:         round(avg(case when eo.is_employed then eo.career_development_score end), 2) as avg_career_development,
89:         round(avg(case when eo.is_employed then eo.retention_stability_score end), 2) as avg_retention_stability,
90:         
91:         -- Employee value distribution
92:         count(distinct case when eo.employee_value_segment = 'High Value - High Retention' then eo.worker_id end) as high_value_stable_employees,
93:         count(distinct case when eo.employee_value_segment = 'High Value - Flight Risk' then eo.worker_id end) as high_value_flight_risk_employees,
94:         count(distinct case when eo.employee_value_segment = 'Stable - Development Needed' then eo.worker_id end) as stable_development_employees,
95:         count(distinct case when eo.employee_value_segment = 'Development Required' then eo.worker_id end) as development_required_employees,
96:         
97:         -- risk distribution
98:         count(distinct case when eo.employee_risk_level = 'High Risk' then eo.worker_id end) as high_risk_employees,
99:         count(distinct case when eo.employee_risk_level = 'Medium Risk' then eo.worker_id end) as medium_risk_employees,
100:         count(distinct case when eo.employee_risk_level = 'Low Risk' then eo.worker_id end) as low_risk_employees,
101:         
102:         -- Employee maturity distribution
103:         count(distinct case when eo.employee_maturity_segment like '%New Hire%' and eo.is_employed then eo.worker_id end) as new_hire_employees,
104:         count(distinct case when eo.employee_maturity_segment like '%Junior%' and eo.is_employed then eo.worker_id end) as junior_employees,
105:         count(distinct case when eo.employee_maturity_segment like '%Experienced%' and eo.is_employed then eo.worker_id end) as experienced_employees,
106:         count(distinct case when eo.employee_maturity_segment like '%Senior%' and eo.is_employed then eo.worker_id end) as senior_employees,
107:         count(distinct case when eo.employee_maturity_segment like '%Veteran%' and eo.is_employed then eo.worker_id end) as veteran_employees,
108:         
109:         -- diversity index
110:         count(distinct case when eo.is_employed then eo.ethnicity_codes end) as ethnic_diversity_count,
111:         count(distinct case when eo.is_employed and eo.is_military_service then eo.worker_id end) as military_veterans_count,
112:         round(avg(case when eo.is_employed then eo.age end), 1) as avg_employee_age,
113:         
114:         -- Salary distribution
115:         count(distinct case when eo.compensation_tier = 'Entry Level' and eo.is_employed then eo.worker_id end) as entry_level_employees,
116:         count(distinct case when eo.compensation_tier = 'Mid Level' and eo.is_employed then eo.worker_id end) as mid_level_employees,
117:         count(distinct case when eo.compensation_tier = 'Senior Level' and eo.is_employed then eo.worker_id end) as senior_level_employees,
118:         count(distinct case when eo.compensation_tier = 'Executive Level' and eo.is_employed then eo.worker_id end) as executive_level_employees,
119:         
120:         -- career development statistics
121:         sum(case when eo.is_employed then eo.total_promotions end) as total_promotions_in_org,
122:         count(distinct case when eo.total_promotions >= 2 and eo.is_employed then eo.worker_id end) as high_achievers_count,
123:         count(distinct case when eo.fast_promotions > 0 and eo.is_employed then eo.worker_id end) as fast_track_employees_count
124:         
125:     from mart.workday__employee_overview eo
126:     where eo.organization_id != 'Unknown'
127:     group by eo.organization_id, eo.source_relation
128: ),
129: 
130: -- Organizational Hierarchy and Relationship Analysis
131: organization_hierarchy_analysis as (
132:     select 
133:         ob.organization_id,
134:         ob.source_relation,
135:         ob.organization_name,
136:         ob.organization_code,
137:         ob.organization_type,
138:         ob.organization_sub_type,
139:         ob.staffing_model,
140:         ob.visibility,
141:         ob.effective_start as organization_created_date,
142:         
143:         -- Calculate organization age
144:         date_diff('day', ob.effective_start, current_date) as organization_age_days,
145:         case 
146:             when date_diff('day', ob.effective_start, current_date) < 365 then 'New Organization (<1 year)'
147:             when date_diff('day', ob.effective_start, current_date) < 365*3 then 'Young Organization (1-3 years)'
148:             when date_diff('day', ob.effective_start, current_date) < 365*10 then 'Mature Organization (3-10 years)'
149:             else 'Legacy Organization (10+ years)'
150:         end as organization_maturity_level,
151:         
152:         -- Organization type analysis
153:         case 
154:             when ob.organization_type = 'Company' then 'Corporate Level'
155:             when ob.organization_type = 'Division' then 'Division Level'
156:             when ob.organization_type = 'Department' then 'Department Level'
157:             when ob.organization_type = 'Team' then 'Team Level'
158:             else 'Other Level'
159:         end as organizational_level,
160:         
161:         -- Visibility and access control
162:         case 
163:             when ob.visibility = 'Public' then 'Open Access'
164:             when ob.visibility = 'Private' then 'Restricted Access'
165:             else 'Unknown Access'
166:         end as access_level
167:         
168:     from organization_base ob
169: )
170: 
171: select 
172:     oha.organization_id,
173:     oha.source_relation,
174:     oha.organization_name,
175:     oha.organization_code,
176:     oha.organization_type,
177:     oha.organization_sub_type,
178:     oha.staffing_model,
179:     oha.visibility,
180:     oha.access_level,
181:     oha.organization_created_date,
182:     oha.organization_age_days,
183:     round(oha.organization_age_days / 365.0, 2) as organization_age_years,
184:     oha.organization_maturity_level,
185:     oha.organizational_level,
186:     
187:     -- Staff size and distribution
188:     coalesce(oes.total_employees_ever, 0) as total_employees_ever,
189:     coalesce(oes.current_active_employees, 0) as current_active_employees,
190:     coalesce(oes.former_employees, 0) as former_employees,
191:     coalesce(oes.total_positions_in_org, 0) as total_positions,
192:     coalesce(oes.active_positions_count, 0) as active_positions_count,
193:     
194:     -- Calculate fill and utilization rates
195:     case 
196:         when coalesce(oes.total_positions_in_org, 0) > 0 then 
197:             round(coalesce(oes.current_active_employees, 0) * 100.0 / oes.total_positions_in_org, 2)
198:         else 0 
199:     end as position_fill_rate,
200:     
201:     -- liquidity indicator
202:     coalesce(oes.new_assignments_last_year, 0) as new_assignments_last_year,
203:     coalesce(oes.departures_last_year, 0) as departures_last_year,
204:     
205:     -- annual churn rate
206:     case 
207:         when coalesce(oes.current_active_employees, 0) > 0 then 
208:             round(coalesce(oes.departures_last_year, 0) * 100.0 / oes.current_active_employees, 2)
209:         else 0 
210:     end as annual_turnover_rate,
211:     
212:     -- tenure indicator
213:     round(coalesce(oes.avg_current_tenure_days, 0) / 365.0, 2) as avg_current_tenure_years,
214:     round(coalesce(oes.avg_former_tenure_days, 0) / 365.0, 2) as avg_former_tenure_years,
215:     
216:     -- organizational role structure
217:     coalesce(oes.unique_organization_roles, 0) as unique_organization_roles,
218:     coalesce(oes.management_role_employees, 0) as management_role_employees,
219:     coalesce(oes.director_role_employees, 0) as director_role_employees,
220:     coalesce(oes.lead_role_employees, 0) as lead_role_employees,
221:     
222:     -- management ratio
223:     case 
224:         when coalesce(oes.current_active_employees, 0) > 0 then 
225:             round((coalesce(oes.management_role_employees, 0) + coalesce(oes.director_role_employees, 0)) * 100.0 / oes.current_active_employees, 2)
226:         else 0 
227:     end as management_ratio,
228:     
229:     -- Performance and Quality Metrics
230:     coalesce(opm.avg_employee_performance, 0) as avg_employee_performance_score,
231:     coalesce(opm.avg_career_development, 0) as avg_career_development_score,
232:     coalesce(opm.avg_retention_stability, 0) as avg_retention_stability_score,
233:     
234:     -- Employee value distribution
235:     coalesce(opm.high_value_stable_employees, 0) as high_value_stable_employees,
236:     coalesce(opm.high_value_flight_risk_employees, 0) as high_value_flight_risk_employees,
237:     coalesce(opm.stable_development_employees, 0) as stable_development_employees,
238:     coalesce(opm.development_required_employees, 0) as development_required_employees,
239:     
240:     -- risk distribution
241:     coalesce(opm.high_risk_employees, 0) as high_risk_employees,
242:     coalesce(opm.medium_risk_employees, 0) as medium_risk_employees,
243:     coalesce(opm.low_risk_employees, 0) as low_risk_employees,
244:     
245:     -- risk ratio
246:     case 
247:         when coalesce(oes.current_active_employees, 0) > 0 then 
248:             round(coalesce(opm.high_risk_employees, 0) * 100.0 / oes.current_active_employees, 2)
249:         else 0 
250:     end as high_risk_employee_percentage,
251:     
252:     -- Employee maturity distribution
253:     coalesce(opm.new_hire_employees, 0) as new_hire_employees,
254:     coalesce(opm.junior_employees, 0) as junior_employees,
255:     coalesce(opm.experienced_employees, 0) as experienced_employees,
256:     coalesce(opm.senior_employees, 0) as senior_employees,
257:     coalesce(opm.veteran_employees, 0) as veteran_employees,
258:     
259:     -- diversity index
260:     coalesce(opm.ethnic_diversity_count, 0) as ethnic_diversity_count,
261:     coalesce(opm.military_veterans_count, 0) as military_veterans_count,
262:     coalesce(opm.avg_employee_age, 0) as avg_employee_age,
263:     
264:     -- Salary level distribution
265:     coalesce(opm.entry_level_employees, 0) as entry_level_employees,
266:     coalesce(opm.mid_level_employees, 0) as mid_level_employees,
267:     coalesce(opm.senior_level_employees, 0) as senior_level_employees,
268:     coalesce(opm.executive_level_employees, 0) as executive_level_employees,
269:     
270:     -- career development indicators
271:     coalesce(opm.total_promotions_in_org, 0) as total_promotions_in_organization,
272:     coalesce(opm.high_achievers_count, 0) as high_achievers_count,
273:     coalesce(opm.fast_track_employees_count, 0) as fast_track_employees_count,
274:     
275:     -- Overall organizational health score (0-100)
276:     round(
277:         (-- Employee performance (30%)
278:          least(30, coalesce(opm.avg_employee_performance, 0) * 0.3) +
279:          -- Retention stability (25%)
280:          (case when coalesce(oes.departures_last_year, 0) = 0 and coalesce(oes.current_active_employees, 0) > 0 then 25
281:                when annual_turnover_rate <= 10 then 20
282:                when annual_turnover_rate <= 20 then 15
283:                when annual_turnover_rate <= 30 then 10
284:                else 5 end) +
285:          -- Employee development (20%)
286:          least(20, coalesce(opm.avg_career_development, 0) * 0.2) +
287:          -- Organizational efficiency (15%)
288:          (case when position_fill_rate >= 90 then 15
289:                when position_fill_rate >= 80 then 12
290:                when position_fill_rate >= 70 then 9
291:                else 6 end) +
292:          -- Risk Control (10%)
293:          (case when high_risk_employee_percentage <= 5 then 10
294:                when high_risk_employee_percentage <= 15 then 7
295:                when high_risk_employee_percentage <= 25 then 4
296:                else 2 end))
297:     , 2) as organization_health_score,
298:     
299:     -- Organizational Performance Classification
300:     case 
301:         when round(
302:             (least(30, coalesce(opm.avg_employee_performance, 0) * 0.3) +
303:              (case when coalesce(oes.departures_last_year, 0) = 0 and coalesce(oes.current_active_employees, 0) > 0 then 25
304:                    when (case when coalesce(oes.current_active_employees, 0) > 0 then round(coalesce(oes.departures_last_year, 0) * 100.0 / oes.current_active_employees, 2) else 0 end) <= 10 then 20
305:                    when (case when coalesce(oes.current_active_employees, 0) > 0 then round(coalesce(oes.departures_last_year, 0) * 100.0 / oes.current_active_employees, 2) else 0 end) <= 20 then 15
306:                    else 10 end) +
307:              least(20, coalesce(opm.avg_career_development, 0) * 0.2) +
308:              (case when (case when coalesce(oes.total_positions_in_org, 0) > 0 then round(coalesce(oes.current_active_employees, 0) * 100.0 / oes.total_positions_in_org, 2) else 0 end) >= 90 then 15 else 10 end) +
309:              10), 2) >= 80 then 'Excellent Performance'
310:         when round(
311:             (least(30, coalesce(opm.avg_employee_performance, 0) * 0.3) +
312:              (case when coalesce(oes.departures_last_year, 0) = 0 and coalesce(oes.current_active_employees, 0) > 0 then 25 else 15 end) +
313:              least(20, coalesce(opm.avg_career_development, 0) * 0.2) +
314:              15 + 10), 2) >= 60 then 'Good Performance'
315:         when round(
316:             (least(30, coalesce(opm.avg_employee_performance, 0) * 0.3) +
317:              15 + least(20, coalesce(opm.avg_career_development, 0) * 0.2) +
318:              10 + 5), 2) >= 40 then 'Average Performance'
319:         else 'Needs Improvement'
320:     end as performance_category,
321:     
322:     -- Organization size classification
323:     case 
324:         when coalesce(oes.current_active_employees, 0) = 0 then 'Empty Organization'
325:         when coalesce(oes.current_active_employees, 0) <= 5 then 'Micro Team'
326:         when coalesce(oes.current_active_employees, 0) <= 15 then 'Small Team'
327:         when coalesce(oes.current_active_employees, 0) <= 50 then 'Medium Team'
328:         when coalesce(oes.current_active_employees, 0) <= 200 then 'Large Team'
329:         else 'Enterprise Unit'
330:     end as organization_size_category,
331:     
332:     -- Latest event date
333:     coalesce(oes.last_new_assignment_date, oha.organization_created_date) as last_activity_date,
334:     coalesce(oes.last_departure_date, '1900-01-01'::date) as last_departure_date,
335:     
336:     -- management advice
337:     case 
338:         when coalesce(oes.current_active_employees, 0) = 0 then 'Review Organization Necessity'
339:         when annual_turnover_rate > 30 then 'Critical: Focus on Retention'
340:         when high_risk_employee_percentage > 25 then 'Address Employee Risk Factors'
341:         when position_fill_rate < 70 then 'Improve Recruitment and Staffing'
342:         when coalesce(opm.avg_employee_performance, 0) < 50 then 'Enhance Performance Management'
343:         when management_ratio > 40 then 'Optimize Management Structure'
344:         else 'Maintain Current Excellence'
345:     end as management_recommendation,
346:     
347:     -- Data quality check
348:     case 
349:         when oha.organization_name is null or oha.organization_name = '' then 'ERROR: Missing organization name'
350:         when coalesce(oes.current_active_employees, 0) > coalesce(oes.total_positions_in_org, 0) + 10 then 'WARNING: More employees than positions'
351:         when annual_turnover_rate > 100 then 'WARNING: Turnover rate exceeds 100%'
352:         when oha.organization_age_days < 0 then 'ERROR: Invalid organization creation date'
353:         else 'VALID'
354:     end as data_quality_flag,
355:     
356:     -- Analysis timestamp
357:     current_timestamp as analysis_timestamp
358:     
359: from organization_hierarchy_analysis oha
360: left join organization_employee_stats oes
361:     on oha.organization_id = oes.organization_id
362:     and oha.source_relation = oes.source_relation
363: left join organization_performance_metrics opm
364:     on oha.organization_id = opm.organization_id
365:     and oha.source_relation = opm.source_relation
366: order by 
367:     coalesce(oes.current_active_employees, 0) desc,
368:     coalesce(opm.avg_employee_performance, 0) desc,
369:     oha.organization_name
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- annual_turnover_rate（C）：**看到了但没提**；事件 30、56、72、81。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。

- management_ratio（C）：**看到了但没提**；事件 30、56、72、81。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。

- organization_maturity_level（O）：**看到了但没提**；事件 30、56、72、81。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。

- organization_size_category（O）：**看到了但没提**；事件 30、56、72、81。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 30：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/30.json`；原始观察输出。
event 56：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/56.json`；原始观察输出。
event 72：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/72.json`；原始观察输出。
event 81：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/81.json`；命令首行：`cat > result.md <<'EOF'`。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

Implemented the Workday SQL pipeline in `sql/` across all three layers, following the dependency execution order (staging → intermediate → marts) and the model/column specifications in `docs/data_contract.yaml`.

- Added SQL for all 21 staging tables, 7 intermediate models, and 6 marts (34 SQL files total).
- Used DuckDB-compatible SQL, direct `schema.table` references, and no dbt `ref()` syntax or trailing semicolons.
- Applied contract cleaning and row-removal rules, derived lifecycle/career/organization measures, and handled nulls and categories in the requested model layers.
- Validated mart column names against the contract: all 6 marts have the expected columns, with no missing or additional columns.
- Ran `python run.py` successfully; all configured SQL models executed and the pipeline generated `workday.duckdb`.

Validation notes and residual impact:
- Staging key checks on the executed data found no nulls or duplicates for worker history IDs, organization IDs, and position IDs.
- Source data contains no worker-position-organization records with a null end date. Therefore current-assignment headcount is zero and the contract-filtered `workday__organization_performance` mart contains zero rows. This is attributable to the input data, rather than a SQL execution failure; current workforce/organization measures are consequently limited.
- Person-based source data was mapped through `raw.worker_to_person` to worker IDs and assigned `'workday'` as `source_relation`, consistent with the single-source dataset and downstream contract joins.
- Source naming variants such as `worker_position_history` and `worker_position_organization_history` were mapped to their corresponding contract tables.

Initial validation identified raw table-name mismatches and SQL parser/binding issues. These were corrected, followed by a successful full pipeline run. No SQL execution failures remain in the final run.
```

## 查询

核实查询 **1** 条；代价档：**一条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：agent 可见零活动分母
[024_calibration_queries.json](../024_calibration_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/workday.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE effective_end IS NULL) active FROM staging.stg_workday__worker_position_organization
```


```json
{"columns":["n","active"],"rows":[[10317,0]]}
```


### 诊断：gold 固定时钟
[024_calibration_queries.json](../024_calibration_queries.json)
数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`。

```sql
SELECT min(analysis_timestamp),max(analysis_timestamp) FROM mart.workday__organization_overview
```


```json
{"columns":["min(analysis_timestamp)","max(analysis_timestamp)"],"rows":[["2025-10-13 13:18:28.226000+08:00","2025-10-13 13:18:28.226000+08:00"]]}
```

## 独立单点重跑

### 024_reruns_impl-016_workday__organization_overview.json
[024_reruns_impl-016_workday__organization_overview.json](../024_reruns_impl-016_workday__organization_overview.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 13:18:28.226000+08:00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":8}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|813|否|
|L1|117|117|117|813|否|
|L2|117|117|117|813|否|
|L3|117|117|117|696|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"analysis_timestamp":117,"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"analysis_timestamp":117,"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"analysis_timestamp":117,"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### baseline
私有SQL：`data/024_work/impl-016_workday__organization_overview/baseline.sql`；SHA-256 `e2385609747bf95c5de2adae6a50548939fee15b2283ce3a617e704087b6c071`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|696|否|
|L1|117|117|117|696|否|
|L2|117|117|117|696|否|
|L3|117|117|117|696|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### position_fill_rate
不计参与因素；类别候选C。契约给出了零分母及连接/计分做法
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第27行、offset 6475起替换；其他字节相同。
原表达式：
```sql
round(coalesce(current_active_employees,0)*100.0/NULLIF(total_positions,0),2)
```

修改后：
```sql
coalesce(round(coalesce(current_active_employees,0)*100.0/NULLIF(total_positions,0),2),0)
```

私有SQL：`data/024_work/impl-016_workday__organization_overview/position_fill_rate.sql`；SHA-256 `c8caee17db005f9a3edfd386722c72aa913a99ed50277edac2cf94aa11b2c7a4`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|696|否|
|L1|117|117|117|696|否|
|L2|117|117|117|696|否|
|L3|117|117|117|696|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### annual_turnover_rate
主因；类别候选C。契约给出了零分母及连接/计分做法
相对本轮基线：行减少0，格减少117。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第27行、offset 6714起替换；其他字节相同。
原表达式：
```sql
round(coalesce(departures_last_year,0)*100.0/NULLIF(current_active_employees,0),2)
```

修改后：
```sql
coalesce(round(coalesce(departures_last_year,0)*100.0/NULLIF(current_active_employees,0),2),0)
```

私有SQL：`data/024_work/impl-016_workday__organization_overview/annual_turnover_rate.sql`；SHA-256 `0672f96ad6734ca0096c3b2be4c542ef4ced1e29dbb0cd9af7272c96b4a0a56f`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|579|否|
|L1|117|117|117|579|否|
|L2|117|117|117|579|否|
|L3|117|117|117|579|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### management_ratio
主因；类别候选C。契约给出了零分母及连接/计分做法
相对本轮基线：行减少0，格减少117。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第29行、offset 7252起替换；其他字节相同。
原表达式：
```sql
round((coalesce(management_role_employees,0)+coalesce(director_role_employees,0))*100.0/NULLIF(current_active_employees,0),2)
```

修改后：
```sql
coalesce(round((coalesce(management_role_employees,0)+coalesce(director_role_employees,0))*100.0/NULLIF(current_active_employees,0),2),0)
```

私有SQL：`data/024_work/impl-016_workday__organization_overview/management_ratio.sql`；SHA-256 `245e0cf33c27c0cad772b3d76a694ebd083264f806ef7ee6fb045bd6d60d0d8e`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|579|否|
|L1|117|117|117|579|否|
|L2|117|117|117|579|否|
|L3|117|117|117|579|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### high_risk_employee_percentage
不计参与因素；类别候选C。契约给出了零分母及连接/计分做法
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第31行、offset 8149起替换；其他字节相同。
原表达式：
```sql
round(coalesce(high_risk_employees,0)*100.0/NULLIF(current_active_employees,0),2)
```

修改后：
```sql
coalesce(round(coalesce(high_risk_employees,0)*100.0/NULLIF(current_active_employees,0),2),0)
```

私有SQL：`data/024_work/impl-016_workday__organization_overview/high_risk_employee_percentage.sql`；SHA-256 `83a4c578b860bb291e295d09fb7bc94c4dd74bcf1afa6d5c7c41d9d210585057`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|696|否|
|L1|117|117|117|696|否|
|L2|117|117|117|696|否|
|L3|117|117|117|696|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### organization_maturity_level
主因；类别候选O。契约短枚举与gold全称冲突
相对本轮基线：行减少0，格减少117。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第24行、offset 5682起替换；其他字节相同。
原表达式：
```sql
CASE WHEN date_diff('day',effective_start,DATE '2025-10-13')<365 THEN 'New' WHEN date_diff('day',effective_start,DATE '2025-10-13')<1095 THEN 'Young' WHEN date_diff('day',effective_start,DATE '2025-10-13')<3650 THEN 'Mature' ELSE 'Legacy' END organization_maturity_level,
```

修改后：
```sql
CASE WHEN date_diff('day',effective_start,DATE '2025-10-13')<365 THEN 'New Organization (<1 year)' WHEN date_diff('day',effective_start,DATE '2025-10-13')<1095 THEN 'Young Organization (1-3 years)' WHEN date_diff('day',effective_start,DATE '2025-10-13')<3650 THEN 'Mature Organization (3-10 years)' ELSE 'Legacy Organization (10+ years)' END organization_maturity_level,
```

私有SQL：`data/024_work/impl-016_workday__organization_overview/organization_maturity_level.sql`；SHA-256 `33a4b88fc26a69ee989229330066b26cc6983b2dffb0826d947e533a96e33e9c`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|579|否|
|L1|117|117|117|579|否|
|L2|117|117|117|579|否|
|L3|117|117|117|579|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_size_category":117,"unique_organization_roles":106}`

#### organization_size_category
主因；类别候选O。契约短枚举与gold全称冲突
相对本轮基线：行减少0，格减少117。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第35行、offset 10086起替换；其他字节相同。
原表达式：
```sql
CASE WHEN current_active_employees=0 THEN 'Empty' WHEN current_active_employees<=5 THEN 'Micro' WHEN current_active_employees<=15 THEN 'Small' WHEN current_active_employees<=50 THEN 'Medium' WHEN current_active_employees<=200 THEN 'Large' ELSE 'Enterprise' END organization_size_category,
```

修改后：
```sql
CASE WHEN current_active_employees=0 THEN 'Empty Organization' WHEN current_active_employees<=5 THEN 'Micro Team' WHEN current_active_employees<=15 THEN 'Small Team' WHEN current_active_employees<=50 THEN 'Medium Team' WHEN current_active_employees<=200 THEN 'Large Team' ELSE 'Enterprise Unit' END organization_size_category,
```

私有SQL：`data/024_work/impl-016_workday__organization_overview/organization_size_category.sql`；SHA-256 `d1f0218a87e8cc9dcec565ac8addfb3be8b14c8b8f6d57a07eedd901197b6f06`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|579|否|
|L1|117|117|117|579|否|
|L2|117|117|117|579|否|
|L3|117|117|117|579|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"unique_organization_roles":106}`

#### assignment_join
参与因素；类别候选C。契约给出了零分母及连接/计分做法
相对本轮基线：行减少0，格减少5。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第9行、offset 1284起替换；其他字节相同。
原表达式：
```sql
FROM rel GROUP BY organization_id,source_relation
```

修改后：
```sql
FROM (SELECT w.* FROM rel w LEFT JOIN staging.stg_workday__organization_role_worker ow ON w.worker_id=ow.organization_worker_code AND w.source_relation=ow.source_relation LEFT JOIN staging.stg_workday__organization_role r ON ow.role_id=r.organization_role_id AND ow.source_relation=r.source_relation AND w.organization_id=r.organization_id) rel GROUP BY organization_id,source_relation
```

私有SQL：`data/024_work/impl-016_workday__organization_overview/assignment_join.sql`；SHA-256 `88367c6b2208553dd3e5a1b9a06d7fe218a650a0bd1abc683a32017e4406e931`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|691|否|
|L1|117|117|117|691|否|
|L2|117|117|117|691|否|
|L3|117|117|117|691|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### roles_join
盲标探索：整段roles替换不计最终独立因素；另以role_count_expression单表达式重查；类别候选C。契约给出了零分母及连接/计分做法
相对本轮基线：行减少0，格减少106。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 1348起替换；其他字节相同。
原表达式：
```sql
 SELECT ow.organization_id,'workday' source_relation,count(DISTINCT r.organization_role_id) unique_organization_roles,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Manager%') management_role_employees,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Director%') director_role_employees,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Lead%') lead_role_employees FROM staging.stg_workday__organization_role_worker ow LEFT JOIN staging.stg_workday__organization_role r ON ow.organization_id=r.organization_id AND ow.role_id=r.organization_role_id GROUP BY ow.organization_id
```

修改后：
```sql
 SELECT w.organization_id,w.source_relation,count(DISTINCT ow.role_id) unique_organization_roles,count(DISTINCT w.worker_id) FILTER(WHERE r.organization_role_code LIKE '%Manager%') management_role_employees,count(DISTINCT w.worker_id) FILTER(WHERE r.organization_role_code LIKE '%Director%') director_role_employees,count(DISTINCT w.worker_id) FILTER(WHERE r.organization_role_code LIKE '%Lead%') lead_role_employees FROM staging.stg_workday__worker_position_organization w LEFT JOIN staging.stg_workday__organization_role_worker ow ON w.worker_id=ow.organization_worker_code AND w.source_relation=ow.source_relation LEFT JOIN staging.stg_workday__organization_role r ON ow.role_id=r.organization_role_id AND ow.source_relation=r.source_relation AND w.organization_id=r.organization_id GROUP BY w.organization_id,w.source_relation
```

私有SQL：`data/024_work/impl-016_workday__organization_overview/roles_join.sql`；SHA-256 `083ec7810a86951cbdd03d4e80b24945726bc1b7c5eaf44dcd4b7c96937825bb`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|590|否|
|L1|117|117|117|590|否|
|L2|117|117|117|590|否|
|L3|117|117|117|590|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117}`

#### score_turnover
不计参与因素；类别候选C。契约给出了零分母及连接/计分做法
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第33行、offset 9292起替换；其他字节相同。
原表达式：
```sql
CASE WHEN departures_last_year=0 THEN 25 WHEN annual_turnover_rate<=10 THEN 25 WHEN annual_turnover_rate<=20 THEN 20 WHEN annual_turnover_rate<=30 THEN 15 WHEN annual_turnover_rate<=40 THEN 10 ELSE 5 END
```

修改后：
```sql
CASE WHEN coalesce(departures_last_year,0)=0 AND coalesce(current_active_employees,0)>0 THEN 25 WHEN annual_turnover_rate<=10 THEN 20 WHEN annual_turnover_rate<=20 THEN 15 WHEN annual_turnover_rate<=30 THEN 10 ELSE 5 END
```

私有SQL：`data/024_work/impl-016_workday__organization_overview/score_turnover.sql`；SHA-256 `02ee9859b3048c500ead7ddb05b9bad8da02661d6caffdddd2ce0ec0fb02b785`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|696|否|
|L1|117|117|117|696|否|
|L2|117|117|117|696|否|
|L3|117|117|117|696|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### score_efficiency
不计参与因素；类别候选C。契约给出了零分母及连接/计分做法
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第33行、offset 9550起替换；其他字节相同。
原表达式：
```sql
CASE WHEN position_fill_rate>=90 THEN 15 WHEN position_fill_rate>=75 THEN 12 WHEN position_fill_rate>=60 THEN 9 ELSE 6 END
```

修改后：
```sql
CASE WHEN position_fill_rate>=90 THEN 15 WHEN position_fill_rate>=80 THEN 12 WHEN position_fill_rate>=70 THEN 9 ELSE 6 END
```

私有SQL：`data/024_work/impl-016_workday__organization_overview/score_efficiency.sql`；SHA-256 `53ff2b83ca5d8c42a3e81b43de97d3d1170c4a119d86056b65ebbf78bd97d604`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|696|否|
|L1|117|117|117|696|否|
|L2|117|117|117|696|否|
|L3|117|117|117|696|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### score_risk
不计参与因素；类别候选C。契约给出了零分母及连接/计分做法
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第33行、offset 9673起替换；其他字节相同。
原表达式：
```sql
CASE WHEN high_risk_employee_percentage<=10 THEN 10 WHEN high_risk_employee_percentage<=20 THEN 7 WHEN high_risk_employee_percentage<=30 THEN 4 ELSE 2 END
```

修改后：
```sql
CASE WHEN high_risk_employee_percentage<=5 THEN 10 WHEN high_risk_employee_percentage<=15 THEN 7 WHEN high_risk_employee_percentage<=25 THEN 4 ELSE 2 END
```

私有SQL：`data/024_work/impl-016_workday__organization_overview/score_risk.sql`；SHA-256 `40399c13b7caa8767729f5fcb7c0efd4bd5e21fc6d6969c30e74ffce4139cb99`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|696|否|
|L1|117|117|117|696|否|
|L2|117|117|117|696|否|
|L3|117|117|117|696|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
### 024_supplement_reruns_impl-016_workday__organization_overview.json
[024_supplement_reruns_impl-016_workday__organization_overview.json](../024_supplement_reruns_impl-016_workday__organization_overview.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 13:18:28.226000+08:00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":8}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|813|否|
|L1|117|117|117|813|否|
|L2|117|117|117|813|否|
|L3|117|117|117|696|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"analysis_timestamp":117,"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"analysis_timestamp":117,"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"analysis_timestamp":117,"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### baseline
私有SQL：`data/024_calibration_review/impl-016_workday__organization_overview/baseline.sql`；SHA-256 `e2385609747bf95c5de2adae6a50548939fee15b2283ce3a617e704087b6c071`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|696|否|
|L1|117|117|117|696|否|
|L2|117|117|117|696|否|
|L3|117|117|117|696|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### role_count_expression
参与因素；类别候选C。仅替换一个角色统计表达式，恢复契约通过worker assignment的角色计数，其余三个统计和连接不动。
相对本轮基线：行减少0，格减少71。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 1401起替换；其他字节相同。
原表达式：
```sql
count(DISTINCT r.organization_role_id) unique_organization_roles
```

修改后：
```sql
(SELECT count(DISTINCT orw.role_id) FROM staging.stg_workday__worker_position_organization w LEFT JOIN staging.stg_workday__organization_role_worker orw ON w.worker_id=orw.organization_worker_code AND w.source_relation=orw.source_relation WHERE w.organization_id=ow.organization_id AND w.source_relation='workday') unique_organization_roles
```

私有SQL：`data/024_calibration_review/impl-016_workday__organization_overview/role_count_expression.sql`；SHA-256 `d1c40caaf69488f9286a17601d35b29b044baecf25d560dd30ced52464a0236c`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|625|否|
|L1|117|117|117|625|否|
|L2|117|117|117|625|否|
|L3|117|117|117|625|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":35}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":35}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":35}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":35}`

#### role_management_role_employees
不计参与因素；类别候选C。仅替换一个角色统计表达式，恢复契约通过worker assignment的角色计数，其余三个统计和连接不动。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 1466起替换；其他字节相同。
原表达式：
```sql
count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Manager%') management_role_employees
```

修改后：
```sql
(SELECT count(DISTINCT w.worker_id) FILTER(WHERE rr.organization_role_code ILIKE '%Manager%') FROM staging.stg_workday__worker_position_organization w LEFT JOIN staging.stg_workday__organization_role_worker orw ON w.worker_id=orw.organization_worker_code AND w.source_relation=orw.source_relation LEFT JOIN staging.stg_workday__organization_role rr ON orw.role_id=rr.organization_role_id AND orw.source_relation=rr.source_relation AND w.organization_id=rr.organization_id WHERE w.organization_id=ow.organization_id AND w.source_relation='workday') management_role_employees
```

私有SQL：`data/024_calibration_review/impl-016_workday__organization_overview/role_management_role_employees.sql`；SHA-256 `e92ca623624d2d2ea8e69c669bd29d86ed78c6719cbdffee2f826e9b7113e08f`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|696|否|
|L1|117|117|117|696|否|
|L2|117|117|117|696|否|
|L3|117|117|117|696|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### role_director_role_employees
不计参与因素；类别候选C。仅替换一个角色统计表达式，恢复契约通过worker assignment的角色计数，其余三个统计和连接不动。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 1593起替换；其他字节相同。
原表达式：
```sql
count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Director%') director_role_employees
```

修改后：
```sql
(SELECT count(DISTINCT w.worker_id) FILTER(WHERE rr.organization_role_code ILIKE '%Director%') FROM staging.stg_workday__worker_position_organization w LEFT JOIN staging.stg_workday__organization_role_worker orw ON w.worker_id=orw.organization_worker_code AND w.source_relation=orw.source_relation LEFT JOIN staging.stg_workday__organization_role rr ON orw.role_id=rr.organization_role_id AND orw.source_relation=rr.source_relation AND w.organization_id=rr.organization_id WHERE w.organization_id=ow.organization_id AND w.source_relation='workday') director_role_employees
```

私有SQL：`data/024_calibration_review/impl-016_workday__organization_overview/role_director_role_employees.sql`；SHA-256 `a0f0307452469163a54c8b92c3c9293fe6c7acf4d0eaef38407ab113a67e6b7f`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|696|否|
|L1|117|117|117|696|否|
|L2|117|117|117|696|否|
|L3|117|117|117|696|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### role_lead_role_employees
不计参与因素；类别候选C。仅替换一个角色统计表达式，恢复契约通过worker assignment的角色计数，其余三个统计和连接不动。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 1719起替换；其他字节相同。
原表达式：
```sql
count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Lead%') lead_role_employees
```

修改后：
```sql
(SELECT count(DISTINCT w.worker_id) FILTER(WHERE rr.organization_role_code ILIKE '%Lead%') FROM staging.stg_workday__worker_position_organization w LEFT JOIN staging.stg_workday__organization_role_worker orw ON w.worker_id=orw.organization_worker_code AND w.source_relation=orw.source_relation LEFT JOIN staging.stg_workday__organization_role rr ON orw.role_id=rr.organization_role_id AND orw.source_relation=rr.source_relation AND w.organization_id=rr.organization_id WHERE w.organization_id=ow.organization_id AND w.source_relation='workday') lead_role_employees
```

私有SQL：`data/024_calibration_review/impl-016_workday__organization_overview/role_lead_role_employees.sql`；SHA-256 `e037b32579dd5733e01594e99cf3a98ab436f0affaf4d0bbf46cb58febe1014f`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|696|否|
|L1|117|117|117|696|否|
|L2|117|117|117|696|否|
|L3|117|117|117|696|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":106}`

#### role_input_relation
不计参与因素；类别候选C。仅替换roles的FROM关系源为worker assignment与role_worker的关系，其余聚合表达式和role连接保持不动。
相对本轮基线：行减少0，格减少-7。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 1837起替换；其他字节相同。
原表达式：
```sql
FROM staging.stg_workday__organization_role_worker ow
```

修改后：
```sql
FROM (SELECT w.organization_id,orw.organization_worker_code,orw.role_id FROM staging.stg_workday__worker_position_organization w LEFT JOIN staging.stg_workday__organization_role_worker orw ON w.worker_id=orw.organization_worker_code AND w.source_relation=orw.source_relation) ow
```

私有SQL：`data/024_calibration_review/impl-016_workday__organization_overview/role_input_relation.sql`；SHA-256 `70ccdf7d0151a5b94ef2a69729b11a3fb72ef92f6c7bdaf730516fa1b0391e92`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|703|否|
|L1|117|117|117|703|否|
|L2|117|117|117|703|否|
|L3|117|117|117|703|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":113}`
- L1：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":113}`
- L2：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":113}`
- L3：`{"annual_turnover_rate":117,"avg_former_tenure_years":5,"management_ratio":117,"organization_health_score":117,"organization_maturity_level":117,"organization_size_category":117,"unique_organization_roles":113}`
## 规则问题

盲标将短枚举看作描述性缩写而归A；解盲后逐列复核契约确实列出New/Young及Empty/Micro等标签，按字面规则归O。锁定盲标原判断不改。

## 盲标锁定与解盲复核

[024_blind_lock.json](../024_blind_lock.json)锁定原始盲标，后读取018；盲标与最终修订分别保存。

```json
{"task":"impl-016","table":"workday__organization_overview","blind_category":"多因并列（C、A）","category_018":"多因并列（C、O）","blind_category_agrees":false,"blind_uncertainty":"看到了但没提","blind_uncertainty_agrees":true,"final_category":"多因并列（C、O）","final_category_agrees":true,"final_uncertainty_agrees":true,"final_factors_agree":false,"factor_comparison_note":"类别方向均为C；024将角色问题分开单改，不能将018整段角色聚合106格直接等同于本次各处效应。详见独立重跑和参与因素。","post_blind_revision":"盲标将短枚举看作描述性缩写而归A；解盲后逐列复核契约确实列出New/Young及Empty/Micro等标签，按字面规则归O。锁定盲标原判断不改。"}
```

