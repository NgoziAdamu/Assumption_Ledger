# impl-016 · workday__employee_overview

用途：**全量**；层：`marts`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：compensation_regex。

主要差异是 gold 的 grade 正则未提取数字，agent 的 compensation_tier 符合契约；另有 compensation 回接重复度 C 因素。

参与因素：C：comp_ebe_join（行减少0，格减少7919407）。

标记：无。

comp_ebe_join 为有效单处 JOIN 干预；初轮 comp_base_multiplicity 未按 worker 约束复制，扩大错误，已排除归因。按第5节行数优先，O 单改减少51965行，C 单改行数不变但格数显著减少。

## 材料与比较口径

精简材料包：[023_impl-016_workday__employee_overview.md](../023_packages/023_impl-016_workday__employee_overview.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml`；SHA-256 `8f0707fc595c6f2f1e46a1983436959278e10315cb723e975c2811858d737c91`。
契约行 1184–1433：

```
1184:     - name: workday__employee_overview
1185:       description: 360-degree employee overview combining worker, lifecycle, career, organization, and compensation context with derived scores, risk/value segments, data-quality flag, and analysis timestamp
1186:       grain: One row per (worker_id, source_relation, position_id, position_start_date)
1187:       source_models:
1188:       - intermediate.int_workday__worker_employee_enhanced
1189:       - intermediate.int_workday__employee_lifecycle
1190:       - intermediate.int_workday__career_progression
1191:       - intermediate.int_workday__organization_metrics
1192:       - staging.stg_workday__worker_position_organization
1193:       - staging.stg_workday__position_job_profile
1194:       - staging.stg_workday__job_profile
1195:       business_logic: '- Build employee_base_enhanced from intermediate.int_workday__worker_employee_enhanced (ebe): - employee_id is an MD5 of "<worker_id>-<source_relation>-<position_id>-<position_start_date>" using "-" as delimiter and replacing NULL components with "_dbt_utils_surrogate_key_null_". - Retain all ebe columns for downstream logic. - Lifecycle metrics (elm) from intermediate.int_workday__employee_lifecycle: select retention indicators, churn risk, maturity segment, departure category, tenure_years, hire cohorts (quarter, year, month, season), retention_stability_score; lifecycle data quality is selected but not used later. - Career metrics (cdc) from intermediate.int_workday__career_progression: - Group by worker_id, source_relation, position_id. - Numeric totals take the largest recorded value in the group; career_development_score is the mean. - Categorical fields (career_stability_category, career_growth_pace, career_phase) choose the most frequent value; when tied, pick the alphabetically earliest. - Also derive the most frequent data_quality_flag (unused downstream). - Organization context (oc): - Join worker_position_organization to organization_metrics on organization_id and source_relation; keep only current relationships (effective_end is NULL). - Retain organization details and department KPIs (size, health, turnover, management ratio, performance, size category). - Join to ebe on worker_id and source_relation so the current organization applies across that worker’s positions. - Compensation/benefits (cb): - Join ebe to position_job_profile by position_id and source_relation, then to job_profile by job_profile_id and source_relation. - Read compensation_grade_id and classify compensation_tier by the first sequence of digits found in the grade id converted to a number: missing/non-numeric → ''Ungraded''; ≤5 → ''Entry Level''; ≤10 → ''Mid Level''; ≤15 → ''Senior Level''; >15 → ''Executive Level''. - work_conditions_score is the sum of three components (0–3): shift required → 0 else 1; union eligible → 1 else 0; default_weekly_hours ≤40 → 1 else 0; NULLs follow the else branch. - Build the comprehensive profile by left joining ebe to elm (worker_id, source_relation), cdc (worker_id, source_relation, position_id), oc (worker_id, source_relation), and cb (worker_id, source_relation, position_id). Compute: - age from date_of_birth relative to current_date with birthday adjustment; NULL when date_of_birth is NULL. - tenure_group from days_as_worker: <365 ''< 1 year''; <730 ''1-2 years''; <1825 ''2-5 years''; <3650 ''5-10 years''; else ''10+ years'' (NULL falls to else). - Default NULLs using these rules: - Lifecycle: retained_30_days/90_days/1_year/3_years → 0; churn_risk_category → ''Unknown''; employee_maturity_segment → ''Unknown''; departure_category → ''Active Employee''; tenure_years → 0; hire_quarter_cohort → ''Unknown''; hire_year_cohort → calendar year of hire_date; retention_stability_score → 0; hire_month → month number of hire_date; hire_season → ''Unknown''. - Career: total_positions_held → 1; total_promotions/demotions/lateral_moves/fast_promotions/management_positions_held → 0; highest_management_level_reached → 1; career_stability_category → ''Unknown''; career_growth_pace → ''Stable Career''; career_development_score → 0; career_phase → ''Unknown''. - Organization: organization_id/name/type/sub_type → ''Unknown''; dept_size → 0; dept_health_score → 0; dept_turnover_rate → 0; dept_management_ratio → 0; dept_performance_category → ''Unknown''; dept_size_category → ''Unknown''. - Compensation: compensation_grade_id → ''Ungraded''; compensation_tier → ''Ungraded''; is_work_shift_required/is_union_eligible → false; work_conditions_score → 0. - overall_employee_score = round(retention_stability_score*0.3 + career_development_score*0.4 + dept_health_score*0.2 + work_conditions_score*10*0.1, to 2 decimals); may fall outside 0–100. - employee_risk_level: - not employed → ''Former Employee'' - else: ''High Risk'' if churn risk is ''High Risk''; ''Medium-High Risk'' if churn risk is ''Medium Risk'' and career_development_score < 40; ''Medium Risk'' if churn risk is ''Medium Risk''; ''Medium-Low Risk'' if churn risk is ''Low Risk'' and dept_turnover_rate > 20; else ''Low Risk''. - employee_value_segment: - not employed → ''Former Employee'' - else: career_development_score ≥80 and retention_stability_score ≥80 → ''High Value - High Retention''; career_development_score ≥80 and retention_stability_score <80 → ''High Value - Flight Risk''; career_development_score <80 and retention_stability_score ≥80 → ''Stable - Development Needed''; career_development_score ≥60 → ''Moderate Value''; else ''Development Required''. - comprehensive_data_quality_flag (first match wins): invalid age (<16 or >80); future hire date; departure before hire; negative tenure; score out of range (<0 or >100); else ''VALID''. - analysis_timestamp is the current timestamp at execution.'
1196:       columns:
1197:       - name: employee_id
1198:         data_type: VARCHAR
1199:         description: MD5 hash of '<worker_id>-<source_relation>-<position_id>-<position_start_date>' with '-' delimiter and '_dbt_utils_surrogate_key_null_' for NULLs; grouping key for the table
1200:       - name: worker_id
1201:         data_type: BIGINT
1202:         description: Worker identifier from int_workday__worker_employee_enhanced; passed through as-is (nullable)
1203:       - name: source_relation
1204:         data_type: VARCHAR
1205:         description: Source system tag from int_workday__worker_employee_enhanced; passed through as-is (nullable)
1206:       - name: position_id
1207:         data_type: VARCHAR
1208:         description: Position identifier from int_workday__worker_employee_enhanced; passed through as-is (nullable)
1209:       - name: position_start_date
1210:         data_type: DATE
1211:         description: Position start date from int_workday__worker_employee_enhanced; used in employee_id hashing
1212:       - name: worker_history_id
1213:         data_type: VARCHAR
1214:         description: Worker history identifier from int_workday__worker_employee_enhanced; passed through as-is
1215:       - name: event_type
1216:         data_type: VARCHAR
1217:         description: Employment event type from int_workday__worker_employee_enhanced; passed through as-is
1218:       - name: is_employed
1219:         data_type: BOOLEAN
1220:         description: Current employment status from int_workday__worker_employee_enhanced; drives 'Former Employee' classifications
1221:       - name: hire_date
1222:         data_type: DATE
1223:         description: Original hire date; used for cohort defaults and data-quality checks
1224:       - name: departure_date
1225:         data_type: DATE
1226:         description: Departure date if applicable; used in data-quality checks
1227:       - name: days_as_worker
1228:         data_type: BIGINT
1229:         description: Total days as worker from int_workday__worker_employee_enhanced; must be >= 0 to avoid error flag
1230:       - name: first_name
1231:         data_type: VARCHAR
1232:         description: First name from int_workday__worker_employee_enhanced; passed through as-is
1233:       - name: last_name
1234:         data_type: VARCHAR
1235:         description: Last name from int_workday__worker_employee_enhanced; passed through as-is
1236:       - name: full_name
1237:         data_type: VARCHAR
1238:         description: Full name from int_workday__worker_employee_enhanced; passed through as-is
1239:       - name: date_of_birth
1240:         data_type: DATE
1241:         description: Date of birth; used to compute age relative to current_date
1242:       - name: marital_status
1243:         data_type: VARCHAR
1244:         description: Marital status from int_workday__worker_employee_enhanced; passed through as-is
1245:       - name: city_of_birth
1246:         data_type: VARCHAR
1247:         description: City of birth from int_workday__worker_employee_enhanced; passed through as-is
1248:       - name: country_of_birth
1249:         data_type: VARCHAR
1250:         description: Country of birth from int_workday__worker_employee_enhanced; passed through as-is
1251:       - name: email_address
1252:         data_type: VARCHAR
1253:         description: Primary email from int_workday__worker_employee_enhanced; passed through as-is
1254:       - name: ethnicity_codes
1255:         data_type: VARCHAR
1256:         description: Ethnicity codes from int_workday__worker_employee_enhanced; passed through as-is
1257:       - name: is_military_service
1258:         data_type: BOOLEAN
1259:         description: Military service indicator from int_workday__worker_employee_enhanced; passed through as-is
1260:       - name: military_status
1261:         data_type: VARCHAR
1262:         description: Military status from int_workday__worker_employee_enhanced; passed through as-is
1263:       - name: business_title
1264:         data_type: VARCHAR
1265:         description: Business title from int_workday__worker_employee_enhanced; passed through as-is
1266:       - name: employee_type
1267:         data_type: VARCHAR
1268:         description: Employee type from int_workday__worker_employee_enhanced; passed through as-is
1269:       - name: default_weekly_hours
1270:         data_type: BIGINT
1271:         description: Default weekly hours from int_workday__worker_employee_enhanced; used in work_conditions_score (≤40 contributes 1, else 0; NULL contributes 0)
1272:       - name: position_end_date
1273:         data_type: DATE
1274:         description: Position end date from int_workday__worker_employee_enhanced; passed through as-is
1275:       - name: days_in_position
1276:         data_type: BIGINT
1277:         description: Days in position from int_workday__worker_employee_enhanced; passed through as-is
1278:       - name: is_employed_one_year
1279:         data_type: BOOLEAN
1280:         description: Has been employed for at least one year; passed through from int_workday__worker_employee_enhanced
1281:       - name: is_employed_five_years
1282:         data_type: BOOLEAN
1283:         description: Has been employed for at least five years; passed through from int_workday__worker_employee_enhanced
1284:       - name: is_employed_ten_years
1285:         data_type: BOOLEAN
1286:         description: Has been employed for at least ten years; passed through from int_workday__worker_employee_enhanced
1287:       - name: is_current_employee_one_year
1288:         data_type: BOOLEAN
1289:         description: Current employee for at least one year; passed through from int_workday__worker_employee_enhanced
1290:       - name: is_current_employee_five_years
1291:         data_type: BOOLEAN
1292:         description: Current employee for at least five years; passed through from int_workday__worker_employee_enhanced
1293:       - name: is_current_employee_ten_years
1294:         data_type: BOOLEAN
1295:         description: Current employee for at least ten years; passed through from int_workday__worker_employee_enhanced
1296:       - name: age
1297:         data_type: BIGINT
1298:         description: Age in years as of current_date using birthday adjustment; NULL if date_of_birth is NULL
1299:       - name: tenure_group
1300:         data_type: VARCHAR
1301:         description: 'Bucketed tenure from days_as_worker: <365 ''< 1 year''; <730 ''1-2 years''; <1825 ''2-5 years''; <3650 ''5-10 years''; else ''10+ years'' (NULL falls to ''10+ years'')'
1302:       - name: retained_30_days
1303:         data_type: INTEGER
1304:         description: Lifecycle retention flag; elm.retained_30_days with NULL → 0
1305:       - name: retained_90_days
1306:         data_type: INTEGER
1307:         description: Lifecycle retention flag; elm.retained_90_days with NULL → 0
1308:       - name: retained_1_year
1309:         data_type: INTEGER
1310:         description: Lifecycle retention flag; elm.retained_1_year with NULL → 0
1311:       - name: retained_3_years
1312:         data_type: INTEGER
1313:         description: Lifecycle retention flag; elm.retained_3_years with NULL → 0
1314:       - name: churn_risk_category
1315:         data_type: VARCHAR
1316:         description: Churn risk segment from lifecycle with NULL → 'Unknown'
1317:       - name: employee_maturity_segment
1318:         data_type: VARCHAR
1319:         description: Maturity segment from lifecycle with NULL → 'Unknown'
1320:       - name: departure_category
1321:         data_type: VARCHAR
1322:         description: Departure category from lifecycle with NULL → 'Active Employee'
1323:       - name: tenure_years
1324:         data_type: DOUBLE
1325:         description: Total tenure in years from lifecycle with NULL → 0
1326:       - name: hire_quarter_cohort
1327:         data_type: VARCHAR
1328:         description: Hire quarter cohort from lifecycle with NULL → 'Unknown'
1329:       - name: hire_year_cohort
1330:         data_type: BIGINT
1331:         description: Hire year cohort from lifecycle; if NULL, defaults to the calendar year of hire_date (can remain NULL if hire_date is NULL)
1332:       - name: retention_stability_score
1333:         data_type: INTEGER
1334:         description: Lifecycle retention stability score 0–100 with NULL → 0
1335:       - name: hire_month
1336:         data_type: BIGINT
1337:         description: Hire month number from lifecycle; if NULL, defaults to the month number of hire_date (can be NULL)
1338:       - name: hire_season
1339:         data_type: VARCHAR
1340:         description: Hire season from lifecycle with NULL → 'Unknown'
1341:       - name: total_positions_held
1342:         data_type: BIGINT
1343:         description: Largest recorded total_positions_held per worker_id, source_relation, position_id with NULL → 1
1344:       - name: total_promotions
1345:         data_type: BIGINT
1346:         description: Largest recorded total_promotions per worker_id, source_relation, position_id with NULL → 0
1347:       - name: total_demotions
1348:         data_type: BIGINT
1349:         description: Largest recorded total_demotions per worker_id, source_relation, position_id with NULL → 0
1350:       - name: lateral_moves
1351:         data_type: BIGINT
1352:         description: Largest recorded lateral_moves per worker_id, source_relation, position_id with NULL → 0
1353:       - name: fast_promotions
1354:         data_type: BIGINT
1355:         description: Largest recorded fast_promotions per worker_id, source_relation, position_id with NULL → 0
1356:       - name: management_positions_held
1357:         data_type: BIGINT
1358:         description: Largest recorded management_positions_held per worker_id, source_relation, position_id with NULL → 0
1359:       - name: highest_management_level_reached
1360:         data_type: INTEGER
1361:         description: Largest recorded highest_management_level_reached per worker_id, source_relation, position_id with NULL → 1
1362:       - name: career_stability_category
1363:         data_type: VARCHAR
1364:         description: Most frequent category per worker_id, source_relation, position_id; ties broken alphabetically; NULL → 'Unknown'
1365:       - name: career_growth_pace
1366:         data_type: VARCHAR
1367:         description: Most frequent growth pace per worker_id, source_relation, position_id; ties broken alphabetically; NULL → 'Stable Career'
1368:       - name: career_development_score
1369:         data_type: DOUBLE
1370:         description: Average career_development_score per worker_id, source_relation, position_id with NULL → 0
1371:       - name: career_phase
1372:         data_type: VARCHAR
1373:         description: Most frequent phase per worker_id, source_relation, position_id; ties broken alphabetically; NULL → 'Unknown'
1374:       - name: organization_id
1375:         data_type: VARCHAR
1376:         description: Current organization_id from join of worker_position_organization→organization_metrics; NULL → 'Unknown'
1377:       - name: organization_name
1378:         data_type: VARCHAR
1379:         description: Current organization name; NULL → 'Unknown'
1380:       - name: organization_type
1381:         data_type: VARCHAR
1382:         description: Organization type; NULL → 'Unknown'
1383:       - name: organization_sub_type
1384:         data_type: VARCHAR
1385:         description: Organization sub-type; NULL → 'Unknown'
1386:       - name: dept_size
1387:         data_type: BIGINT
1388:         description: Department size (current_employee_count) with NULL → 0
1389:       - name: dept_health_score
1390:         data_type: INTEGER
1391:         description: Organization health score 0–100 with NULL → 0
1392:       - name: dept_turnover_rate
1393:         data_type: DOUBLE
1394:         description: Annual turnover rate with NULL → 0; used in risk level ('Low Risk' + >20 → 'Medium-Low Risk')
1395:       - name: dept_management_ratio
1396:         data_type: DOUBLE
1397:         description: Management ratio with NULL → 0
1398:       - name: dept_performance_category
1399:         data_type: VARCHAR
1400:         description: Organization performance category with NULL → 'Unknown'
1401:       - name: dept_size_category
1402:         data_type: VARCHAR
1403:         description: Organization size category with NULL → 'Unknown'
1404:       - name: compensation_grade_id
1405:         data_type: VARCHAR
1406:         description: Job profile compensation grade id; NULL → 'Ungraded'
1407:       - name: compensation_tier
1408:         data_type: VARCHAR
1409:         description: 'Tier from the first digit sequence in compensation_grade_id: ≤5 ''Entry Level'', ≤10 ''Mid Level'', ≤15 ''Senior Level'', >15 ''Executive Level'', else ''Ungraded'''
1410:       - name: is_work_shift_required
1411:         data_type: BOOLEAN
1412:         description: Job profile flag; final output NULL → false; contributes 0 if true else 1 to work_conditions_score
1413:       - name: is_union_eligible
1414:         data_type: BOOLEAN
1415:         description: Job profile flag; final output NULL → false; contributes 1 if true else 0 to work_conditions_score
1416:       - name: work_conditions_score
1417:         data_type: INTEGER
1418:         description: 'Sum of three components (range 0–3): not shift required=1, union eligible=1, default_weekly_hours≤40=1; computed with NULLs treated as false/0 and final NULL → 0'
1419:       - name: overall_employee_score
1420:         data_type: DOUBLE
1421:         description: 'Rounded to 2 decimals: retention_stability_score*0.3 + career_development_score*0.4 + dept_health_score*0.2 + work_conditions_score*10*0.1; not force-bounded to [0,100]'
1422:       - name: employee_risk_level
1423:         data_type: VARCHAR
1424:         description: 'Risk level: not employed ''Former Employee''; else High/Medium/Medium-High/Medium-Low/Low per churn risk, career_development_score<40, and dept_turnover_rate>20'
1425:       - name: employee_value_segment
1426:         data_type: VARCHAR
1427:         description: 'Value segment: not employed ''Former Employee''; else rules on career_development_score and retention_stability_score'
1428:       - name: comprehensive_data_quality_flag
1429:         data_type: VARCHAR
1430:         description: 'First-match checks: invalid age, future hire date, departure before hire, negative tenure, score out of range; else ''VALID'''
1431:       - name: analysis_timestamp
1432:         data_type: TIMESTAMP WITH TIME ZONE
1433:         description: Current timestamp at query execution time for the record build
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__employee_overview.sql`，SHA-256 `60a17999d38a8c037348475fbd70782821d52282340690dde24803b7dc7a8751`，行 1–55。

```
1: WITH base AS (
2:  SELECT e.*, md5(coalesce(cast(worker_id as varchar),'_dbt_utils_surrogate_key_null_')||'-'||coalesce(source_relation,'_dbt_utils_surrogate_key_null_')||'-'||coalesce(position_id,'_dbt_utils_surrogate_key_null_')||'-'||coalesce(cast(position_start_date as varchar),'_dbt_utils_surrogate_key_null_')) employee_id
3:  FROM intermediate.int_workday__worker_employee_enhanced e
4: ), career AS (
5:  SELECT worker_id,source_relation,position_id,max(total_positions_held) total_positions_held,max(total_promotions) total_promotions,
6:  max(total_demotions) total_demotions,max(lateral_moves) lateral_moves,max(fast_promotions) fast_promotions,max(management_positions_held) management_positions_held,
7:  max(highest_management_level_reached) highest_management_level_reached,
8:  mode() within group(order by career_stability_category) career_stability_category,
9:  mode() within group(order by career_growth_pace) career_growth_pace,avg(career_development_score) career_development_score,
10:  mode() within group(order by career_phase) career_phase
11:  FROM intermediate.int_workday__career_progression GROUP BY worker_id,source_relation,position_id
12: ), org AS (
13:  SELECT w.worker_id,w.source_relation,o.organization_id,o.organization_name,o.organization_type,o.organization_sub_type,
14:  o.current_employee_count,o.organization_health_score,o.annual_turnover_rate,o.management_ratio,o.performance_category,o.organization_size_category
15:  FROM staging.stg_workday__worker_position_organization w
16:  LEFT JOIN intermediate.int_workday__organization_metrics o ON w.organization_id=o.organization_id AND w.source_relation=o.source_relation
17:  WHERE w.effective_end IS NULL
18: ), comp AS (
19:  SELECT p.position_id,p.source_relation,jp.compensation_grade_id,jp.is_work_shift_required,jp.is_union_eligible
20:  FROM staging.stg_workday__position_job_profile p
21:  LEFT JOIN staging.stg_workday__job_profile jp ON p.job_profile_id=jp.job_profile_id AND p.source_relation=jp.source_relation
22: ), enriched AS (
23:  SELECT b.*,l.retained_30_days,l.retained_90_days,l.retained_1_year,l.retained_3_years,l.churn_risk_category,l.employee_maturity_segment,l.departure_category,l.tenure_years,
24:  l.hire_quarter_cohort,l.hire_year_cohort,l.retention_stability_score,l.hire_month,l.hire_season,
25:  c.total_positions_held,c.total_promotions,c.total_demotions,c.lateral_moves,c.fast_promotions,c.management_positions_held,c.highest_management_level_reached,c.career_stability_category,c.career_growth_pace,c.career_development_score,c.career_phase,
26:  o.organization_id,o.organization_name,o.organization_type,o.organization_sub_type,o.current_employee_count,o.organization_health_score,o.annual_turnover_rate,o.management_ratio,o.performance_category,o.organization_size_category,
27:  comp.compensation_grade_id,comp.is_work_shift_required,comp.is_union_eligible
28:  FROM base b LEFT JOIN intermediate.int_workday__employee_lifecycle l USING(worker_id,source_relation)
29:  LEFT JOIN career c ON b.worker_id=c.worker_id AND b.source_relation=c.source_relation AND b.position_id=c.position_id
30:  LEFT JOIN org o ON b.worker_id=o.worker_id AND b.source_relation=o.source_relation
31:  LEFT JOIN comp ON b.position_id=comp.position_id AND b.source_relation=comp.source_relation
32: ), calc AS (
33:  SELECT *, CASE WHEN date_of_birth IS NULL THEN NULL ELSE date_diff('year',date_of_birth,current_date)-CASE WHEN strftime(current_date,'%m-%d')<strftime(date_of_birth,'%m-%d') THEN 1 ELSE 0 END END::BIGINT age,
34:  CASE WHEN days_as_worker<365 THEN '< 1 year' WHEN days_as_worker<730 THEN '1-2 years' WHEN days_as_worker<1825 THEN '2-5 years' WHEN days_as_worker<3650 THEN '5-10 years' ELSE '10+ years' END tenure_group,
35:  CASE WHEN regexp_extract(coalesce(compensation_grade_id,''),'([0-9]+)',1)='' THEN 'Ungraded' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=5 THEN 'Entry Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=10 THEN 'Mid Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=15 THEN 'Senior Level' ELSE 'Executive Level' END compensation_tier,
36:  (CASE WHEN coalesce(is_work_shift_required,FALSE) THEN 0 ELSE 1 END + CASE WHEN coalesce(is_union_eligible,FALSE) THEN 1 ELSE 0 END + CASE WHEN default_weekly_hours<=40 THEN 1 ELSE 0 END)::INTEGER work_conditions_score
37:  FROM enriched
38: ), finalized AS (
39:  SELECT *,round(coalesce(retention_stability_score,0)*.3+coalesce(career_development_score,0)*.4+coalesce(organization_health_score,0)*.2+work_conditions_score*10*.1,2)::DOUBLE overall_employee_score,
40:  CASE WHEN is_employed=FALSE THEN 'Former Employee' WHEN churn_risk_category='High Risk' THEN 'High Risk' WHEN churn_risk_category='Medium Risk' AND coalesce(career_development_score,0)<40 THEN 'Medium-High Risk' WHEN churn_risk_category='Medium Risk' THEN 'Medium Risk' WHEN churn_risk_category='Low Risk' AND coalesce(annual_turnover_rate,0)>20 THEN 'Medium-Low Risk' ELSE 'Low Risk' END employee_risk_level,
41:  CASE WHEN is_employed=FALSE THEN 'Former Employee' WHEN career_development_score>=80 AND retention_stability_score>=80 THEN 'High Value - High Retention' WHEN career_development_score>=80 THEN 'High Value - Flight Risk' WHEN retention_stability_score>=80 THEN 'Stable - Development Needed' WHEN career_development_score>=60 THEN 'Moderate Value' ELSE 'Development Required' END employee_value_segment
42:  FROM calc
43: )
44: SELECT employee_id,worker_id,source_relation,position_id,position_start_date,worker_history_id,event_type,is_employed,hire_date,departure_date,days_as_worker,first_name,last_name,full_name,date_of_birth,marital_status,city_of_birth,country_of_birth,email_address,ethnicity_codes,is_military_service,military_status,business_title,employee_type,default_weekly_hours,position_end_date,days_in_position,
45:  is_employed_one_year,is_employed_five_years,is_employed_ten_years,is_current_employee_one_year,is_current_employee_five_years,is_current_employee_ten_years,age,tenure_group,
46:  coalesce(retained_30_days,0)::INTEGER retained_30_days,coalesce(retained_90_days,0)::INTEGER retained_90_days,coalesce(retained_1_year,0)::INTEGER retained_1_year,coalesce(retained_3_years,0)::INTEGER retained_3_years,
47:  coalesce(churn_risk_category,'Unknown') churn_risk_category,coalesce(employee_maturity_segment,'Unknown') employee_maturity_segment,coalesce(departure_category,'Active Employee') departure_category,coalesce(tenure_years,0)::DOUBLE tenure_years,
48:  coalesce(hire_quarter_cohort,'Unknown') hire_quarter_cohort,coalesce(hire_year_cohort,year(hire_date))::BIGINT hire_year_cohort,coalesce(retention_stability_score,0)::INTEGER retention_stability_score,coalesce(hire_month,month(hire_date))::BIGINT hire_month,coalesce(hire_season,'Unknown') hire_season,
49:  coalesce(total_positions_held,1)::BIGINT total_positions_held,coalesce(total_promotions,0)::BIGINT total_promotions,coalesce(total_demotions,0)::BIGINT total_demotions,coalesce(lateral_moves,0)::BIGINT lateral_moves,coalesce(fast_promotions,0)::BIGINT fast_promotions,coalesce(management_positions_held,0)::BIGINT management_positions_held,coalesce(highest_management_level_reached,1)::INTEGER highest_management_level_reached,
50:  coalesce(career_stability_category,'Unknown') career_stability_category,coalesce(career_growth_pace,'Stable Career') career_growth_pace,coalesce(career_development_score,0)::DOUBLE career_development_score,coalesce(career_phase,'Unknown') career_phase,
51:  coalesce(organization_id,'Unknown') organization_id,coalesce(organization_name,'Unknown') organization_name,coalesce(organization_type,'Unknown') organization_type,coalesce(organization_sub_type,'Unknown') organization_sub_type,coalesce(current_employee_count,0)::BIGINT dept_size,coalesce(organization_health_score,0)::INTEGER dept_health_score,coalesce(annual_turnover_rate,0)::DOUBLE dept_turnover_rate,coalesce(management_ratio,0)::DOUBLE dept_management_ratio,coalesce(performance_category,'Unknown') dept_performance_category,coalesce(organization_size_category,'Unknown') dept_size_category,
52:  coalesce(compensation_grade_id,'Ungraded') compensation_grade_id,compensation_tier,coalesce(is_work_shift_required,FALSE) is_work_shift_required,coalesce(is_union_eligible,FALSE) is_union_eligible,work_conditions_score,overall_employee_score,employee_risk_level,employee_value_segment,
53:  CASE WHEN age<16 OR age>80 THEN 'ERROR: Invalid age' WHEN hire_date>CURRENT_DATE THEN 'ERROR: Future hire date' WHEN departure_date<hire_date THEN 'ERROR: Departure before hire' WHEN days_as_worker<0 THEN 'ERROR: Negative tenure' WHEN overall_employee_score<0 OR overall_employee_score>100 THEN 'ERROR: Score out of range' ELSE 'VALID' END comprehensive_data_quality_flag,
54:  current_timestamp::TIMESTAMPTZ analysis_timestamp
55: FROM finalized
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__employee_overview.sql`，SHA-256 `ae3576669f04538c27a4f598b0bf6fae20e5fd6ad98b5b2bde5225b326719ec5`，行 1–271。

```
1: -- Employee panoramic analysis table - a comprehensive view integrating life cycle, career development, and organizational relationships
2: -- Provide employees with 360-degree analysis capabilities to support multi-dimensional insights such as retention, performance, and development.
3: 
4: with employee_base_enhanced as (
5:     select 
6:         md5(cast(coalesce(cast(worker_id as varchar), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(source_relation as varchar), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(position_id as varchar), '_dbt_utils_surrogate_key_null_') || '-' || coalesce(cast(position_start_date as varchar), '_dbt_utils_surrogate_key_null_') as varchar)) as employee_id,
7:         iwe.*
8:     from intermediate.int_workday__worker_employee_enhanced iwe
9: ),
10: 
11: -- Integrate employee lifecycle metrics
12: employee_lifecycle_metrics as (
13:     select 
14:         worker_id,
15:         source_relation,
16:         retained_30_days,
17:         retained_90_days,
18:         retained_1_year,
19:         retained_3_years,
20:         churn_risk_category,
21:         employee_maturity_segment,
22:         departure_category,
23:         tenure_years,
24:         hire_quarter_cohort,
25:         hire_year_cohort,
26:         retention_stability_score,
27:         hire_month,
28:         hire_season,
29:         data_quality_flag as lifecycle_data_quality
30:     from intermediate.int_workday__employee_lifecycle
31: ),
32: 
33: -- Career trajectory information (get the latest job developments)
34: career_development_current as (
35:     select 
36:         worker_id,
37:         source_relation,
38:         position_id,
39:         max(total_positions_held) as total_positions_held,
40:         max(total_promotions) as total_promotions,
41:         max(total_demotions) as total_demotions,
42:         max(lateral_moves) as lateral_moves,
43:         max(fast_promotions) as fast_promotions,
44:         max(management_positions_held) as management_positions_held,
45:         max(highest_management_level_reached) as highest_management_level_reached,
46:         mode() within group (order by career_stability_category) as career_stability_category,
47:         mode() within group (order by career_growth_pace) as career_growth_pace,
48:         avg(career_development_score) as career_development_score,
49:         mode() within group (order by career_phase) as career_phase,
50:         mode() within group (order by data_quality_flag) as career_data_quality
51:     from intermediate.int_workday__career_progression
52:     group by worker_id, source_relation, position_id
53: ),
54: 
55: -- Organizational environmental information
56: organization_context as (
57:     select 
58:         wpo.worker_id,
59:         wpo.source_relation,
60:         wpo.organization_id,
61:         om.organization_name,
62:         om.organization_type,
63:         om.organization_sub_type,
64:         om.current_employee_count as dept_size,
65:         om.organization_health_score as dept_health_score,
66:         om.annual_turnover_rate as dept_turnover_rate,
67:         om.management_ratio as dept_management_ratio,
68:         om.performance_category as dept_performance_category,
69:         om.organization_size_category as dept_size_category
70:     from staging.stg_workday__worker_position_organization wpo
71:     inner join intermediate.int_workday__organization_metrics om
72:         on wpo.organization_id = om.organization_id
73:         and wpo.source_relation = om.source_relation
74:     where wpo.effective_end is null  -- Current organizational relationships
75: ),
76: 
77: -- Compensation and benefits information aggregation
78: compensation_benefits as (
79:     select 
80:         ebe.worker_id,
81:         ebe.source_relation,
82:         ebe.position_id,
83:         jp.compensation_grade_id,
84:         jp.is_work_shift_required,
85:         jp.is_union_eligible,
86:         
87:         -- Pay grade evaluation (based on hypothetical pay grade values)
88:         case 
89:             when jp.compensation_grade_id is null then 'Ungraded'
90:             when try_cast(regexp_extract(jp.compensation_grade_id, '\\d+', 0) as int) <= 5 then 'Entry Level'
91:             when try_cast(regexp_extract(jp.compensation_grade_id, '\\d+', 0) as int) <= 10 then 'Mid Level'
92:             when try_cast(regexp_extract(jp.compensation_grade_id, '\\d+', 0) as int) <= 15 then 'Senior Level'
93:             when try_cast(regexp_extract(jp.compensation_grade_id, '\\d+', 0) as int) > 15 then 'Executive Level'
94:             else 'Ungraded'
95:         end as compensation_tier,
96:         
97:         -- working conditions rating
98:         (case when jp.is_work_shift_required then 0 else 1 end +
99:          case when jp.is_union_eligible then 1 else 0 end +
100:          case when ebe.default_weekly_hours <= 40 then 1 else 0 end) as work_conditions_score
101:         
102:     from employee_base_enhanced ebe
103:     left join staging.stg_workday__position_job_profile pjp
104:         on ebe.position_id = pjp.position_id
105:         and ebe.source_relation = pjp.source_relation
106:     left join staging.stg_workday__job_profile jp
107:         on pjp.job_profile_id = jp.job_profile_id
108:         and pjp.source_relation = jp.source_relation
109: ),
110: 
111: -- Comprehensive employee portraits
112: comprehensive_employee_profile as (
113:     select 
114:         ebe.employee_id,
115:         ebe.worker_id,
116:         ebe.source_relation,
117:         ebe.position_id,
118:         ebe.position_start_date,
119:         ebe.worker_history_id,
120:         ebe.event_type,
121:         ebe.is_employed,
122:         ebe.hire_date,
123:         ebe.departure_date,
124:         ebe.days_as_worker,
125:         ebe.first_name,
126:         ebe.last_name,
127:         ebe.full_name,
128:         ebe.date_of_birth,
129:         ebe.marital_status,
130:         ebe.city_of_birth,
131:         ebe.country_of_birth,
132:         ebe.email_address,
133:         ebe.ethnicity_codes,
134:         ebe.is_military_service,
135:         ebe.military_status,
136:         ebe.business_title,
137:         ebe.employee_type,
138:         ebe.default_weekly_hours,
139:         ebe.position_end_date,
140:         ebe.days_in_position,
141:         ebe.is_employed_one_year,
142:         ebe.is_employed_five_years,
143:         ebe.is_employed_ten_years,
144:         ebe.is_current_employee_one_year,
145:         ebe.is_current_employee_five_years,
146:         ebe.is_current_employee_ten_years,
147:         
148:         -- The underlying calculated fields remain unchanged
149:         case 
150:             when extract(month from ebe.date_of_birth) < extract(month from current_date) 
151:                 or (extract(month from ebe.date_of_birth) = extract(month from current_date) 
152:                     and extract(day from ebe.date_of_birth) <= extract(day from current_date))
153:             then extract(year from current_date) - extract(year from ebe.date_of_birth)
154:             else extract(year from current_date) - extract(year from ebe.date_of_birth) - 1
155:         end as age,
156:         
157:         case when ebe.days_as_worker < 365 then '< 1 year'
158:              when ebe.days_as_worker < 365*2 then '1-2 years'
159:              when ebe.days_as_worker < 365*5 then '2-5 years'
160:              when ebe.days_as_worker < 365*10 then '5-10 years'
161:              else '10+ years'
162:         end as tenure_group,
163:         
164:         -- lifecycle metrics
165:         coalesce(elm.retained_30_days, 0) as retained_30_days,
166:         coalesce(elm.retained_90_days, 0) as retained_90_days,
167:         coalesce(elm.retained_1_year, 0) as retained_1_year,
168:         coalesce(elm.retained_3_years, 0) as retained_3_years,
169:         coalesce(elm.churn_risk_category, 'Unknown') as churn_risk_category,
170:         coalesce(elm.employee_maturity_segment, 'Unknown') as employee_maturity_segment,
171:         coalesce(elm.departure_category, 'Active Employee') as departure_category,
172:         coalesce(elm.tenure_years, 0) as tenure_years,
173:         coalesce(elm.hire_quarter_cohort, 'Unknown') as hire_quarter_cohort,
174:         coalesce(elm.hire_year_cohort, extract(year from ebe.hire_date)) as hire_year_cohort,
175:         coalesce(elm.retention_stability_score, 0) as retention_stability_score,
176:         coalesce(elm.hire_month, extract(month from ebe.hire_date)) as hire_month,
177:         coalesce(elm.hire_season, 'Unknown') as hire_season,
178:         
179:         -- career development indicators
180:         coalesce(cdc.total_positions_held, 1) as total_positions_held,
181:         coalesce(cdc.total_promotions, 0) as total_promotions,
182:         coalesce(cdc.total_demotions, 0) as total_demotions,
183:         coalesce(cdc.lateral_moves, 0) as lateral_moves,
184:         coalesce(cdc.fast_promotions, 0) as fast_promotions,
185:         coalesce(cdc.management_positions_held, 0) as management_positions_held,
186:         coalesce(cdc.highest_management_level_reached, 1) as highest_management_level_reached,
187:         coalesce(cdc.career_stability_category, 'Unknown') as career_stability_category,
188:         coalesce(cdc.career_growth_pace, 'Stable Career') as career_growth_pace,
189:         coalesce(cdc.career_development_score, 0) as career_development_score,
190:         coalesce(cdc.career_phase, 'Unknown') as career_phase,
191:         
192:         -- organizational environment indicators
193:         coalesce(oc.organization_id, 'Unknown') as organization_id,
194:         coalesce(oc.organization_name, 'Unknown') as organization_name,
195:         coalesce(oc.organization_type, 'Unknown') as organization_type,
196:         coalesce(oc.organization_sub_type, 'Unknown') as organization_sub_type,
197:         coalesce(oc.dept_size, 0) as dept_size,
198:         coalesce(oc.dept_health_score, 0) as dept_health_score,
199:         coalesce(oc.dept_turnover_rate, 0) as dept_turnover_rate,
200:         coalesce(oc.dept_management_ratio, 0) as dept_management_ratio,
201:         coalesce(oc.dept_performance_category, 'Unknown') as dept_performance_category,
202:         coalesce(oc.dept_size_category, 'Unknown') as dept_size_category,
203:         
204:         -- Salary and welfare indicators
205:         coalesce(cb.compensation_grade_id, 'Ungraded') as compensation_grade_id,
206:         coalesce(cb.compensation_tier, 'Ungraded') as compensation_tier,
207:         coalesce(cb.is_work_shift_required, false) as is_work_shift_required,
208:         coalesce(cb.is_union_eligible, false) as is_union_eligible,
209:         coalesce(cb.work_conditions_score, 0) as work_conditions_score,
210:         
211:         -- Comprehensive score calculation
212:         round(
213:             (coalesce(elm.retention_stability_score, 0) * 0.3 +
214:              coalesce(cdc.career_development_score, 0) * 0.4 +
215:              coalesce(oc.dept_health_score, 0) * 0.2 +
216:              coalesce(cb.work_conditions_score, 0) * 10 * 0.1), 2
217:         ) as overall_employee_score,
218:         
219:         -- Employee risk level
220:         case 
221:             when not ebe.is_employed then 'Former Employee'
222:             when elm.churn_risk_category = 'High Risk' then 'High Risk'
223:             when elm.churn_risk_category = 'Medium Risk' and cdc.career_development_score < 40 then 'Medium-High Risk'
224:             when elm.churn_risk_category = 'Medium Risk' then 'Medium Risk'
225:             when elm.churn_risk_category = 'Low Risk' and oc.dept_turnover_rate > 20 then 'Medium-Low Risk'
226:             else 'Low Risk'
227:         end as employee_risk_level,
228:         
229:         -- employee value segments
230:         case 
231:             when not ebe.is_employed then 'Former Employee'
232:             when cdc.career_development_score >= 80 and elm.retention_stability_score >= 80 then 'High Value - High Retention'
233:             when cdc.career_development_score >= 80 and elm.retention_stability_score < 80 then 'High Value - Flight Risk'
234:             when cdc.career_development_score < 80 and elm.retention_stability_score >= 80 then 'Stable - Development Needed'
235:             when cdc.career_development_score >= 60 then 'Moderate Value'
236:             else 'Development Required'
237:         end as employee_value_segment
238:         
239:     from employee_base_enhanced ebe
240:     left join employee_lifecycle_metrics elm
241:         on ebe.worker_id = elm.worker_id
242:         and ebe.source_relation = elm.source_relation
243:     left join career_development_current cdc
244:         on ebe.worker_id = cdc.worker_id
245:         and ebe.source_relation = cdc.source_relation
246:         and ebe.position_id = cdc.position_id
247:     left join organization_context oc
248:         on ebe.worker_id = oc.worker_id
249:         and ebe.source_relation = oc.source_relation
250:     left join compensation_benefits cb
251:         on ebe.worker_id = cb.worker_id
252:         and ebe.source_relation = cb.source_relation
253:         and ebe.position_id = cb.position_id
254: )
255: 
256: select 
257:     *,
258:     -- Comprehensive inspection of data quality
259:     case 
260:         when age < 16 or age > 80 then 'ERROR: Invalid age'
261:         when hire_date > current_date then 'ERROR: Future hire date'
262:         when departure_date is not null and departure_date < hire_date then 'ERROR: Departure before hire'
263:         when days_as_worker < 0 then 'ERROR: Negative tenure'
264:         when overall_employee_score < 0 or overall_employee_score > 100 then 'WARNING: Score out of range'
265:         else 'VALID'
266:     end as comprehensive_data_quality_flag,
267:     
268:     -- Record update timestamp
269:     current_timestamp as analysis_timestamp
270:     
271: from comprehensive_employee_profile
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 15/16 已查看 job_profile 列清单；event 31 写 compensation_tier 数字提取；event 83 实施清单未讨论该正则或回接重复度。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/15.json`。
- event 16：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/16.json`。
- event 31：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/31.json`。
- event 83：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/83.json`。
## 查询

核实查询 **0** 条；核实代价档：**需要查业务说明**。诊断查询不计入 5 条上限。

未追加 agent 可见数据核实；判断依据为契约、SQL 和明确标为诊断的查询，不用 gold 结果证明 U。

### 诊断：grade regexp

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE regexp_extract(compensation_grade_id,'([0-9]+)',1)<>'') agent_matches,count(*) FILTER(WHERE regexp_extract(compensation_grade_id,'\\d+',0)<>'') gold_matches FROM staging.stg_workday__job_profile
```


```json
{"columns":["n","agent_matches","gold_matches"],"rows":[[900,900,0]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-016_workday__employee_overview.json](../023_reruns_impl-016_workday__employee_overview.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`。

共同时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":3}]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|51965|156187|156187|8075594|否|
|L1|51965|156187|156187|8075594|否|
|L2|51965|156187|156187|8075594|否|
|L3|51965|156187|156187|8075594|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":156187,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":125907,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":125907,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":132786,"hire_quarter_cohort":133756,"hire_season":127614,"hire_year_cohort":129170,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":119507,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":114939,"retention_stability_score":104222,"tenure_years":135391,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`
- L1：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":156187,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":125907,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":125907,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":132781,"hire_quarter_cohort":133771,"hire_season":127653,"hire_year_cohort":129121,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":119507,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":114939,"retention_stability_score":104222,"tenure_years":135391,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`
- L2：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":156187,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":125907,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":125907,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":132781,"hire_quarter_cohort":133771,"hire_season":127653,"hire_year_cohort":129121,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":119507,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":114939,"retention_stability_score":104222,"tenure_years":135391,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`
- L3：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":156187,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":125907,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":125907,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":132781,"hire_quarter_cohort":133771,"hire_season":127653,"hire_year_cohort":129121,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":119507,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":114939,"retention_stability_score":104222,"tenure_years":135391,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-016_workday__employee_overview/baseline.sql`；SHA-256 `70bae469ba378083d22ac4265b464b9c7d1f97d194a5d91bd341504aeed42aca`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|51965|156187|156187|8075594|否|
|L1|51965|156187|156187|8075594|否|
|L2|51965|156187|156187|8075594|否|
|L3|51965|156187|156187|8075594|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":156187,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":125907,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":125907,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":132786,"hire_quarter_cohort":133756,"hire_season":127614,"hire_year_cohort":129170,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":119507,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":114939,"retention_stability_score":104222,"tenure_years":135391,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`
- L1：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":156187,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":125907,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":125907,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":132781,"hire_quarter_cohort":133771,"hire_season":127653,"hire_year_cohort":129121,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":119507,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":114939,"retention_stability_score":104222,"tenure_years":135391,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`
- L2：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":156187,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":125907,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":125907,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":132781,"hire_quarter_cohort":133771,"hire_season":127653,"hire_year_cohort":129121,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":119507,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":114939,"retention_stability_score":104222,"tenure_years":135391,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`
- L3：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":156187,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":125907,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":125907,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":132781,"hire_quarter_cohort":133771,"hire_season":127653,"hire_year_cohort":129121,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":119507,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":114939,"retention_stability_score":104222,"tenure_years":135391,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`

#### compensation_regex

判定：主因；类别候选 O。契约要求提取首段数字，agent 符合；gold 双反斜杠正则对当前 grade 未提取数字。常量仅为定位 gold 差异的诊断。

相对本轮基线减少行 51965、格 258944；按行优先、格次之排序。
共同控制后 SQL 第 35 行起、字符 offset 3637 的唯一连续替换；其余字节不动。
替换前：
```sql
CASE WHEN regexp_extract(coalesce(compensation_grade_id,''),'([0-9]+)',1)='' THEN 'Ungraded' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=5 THEN 'Entry Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=10 THEN 'Mid Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=15 THEN 'Senior Level' ELSE 'Executive Level' END
```

替换后：
```sql
'Ungraded'
```

私有 SQL：`data/023_work/impl-016_workday__employee_overview/compensation_regex.sql`；SHA-256 `eaa1cb1ee23fff07955a0a194996e36556ba93958f6ce77a89888b8d17b71ae0`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|51965|156187|104222|7816650|否|
|L1|51965|156187|104222|7816650|否|
|L2|51965|156187|104222|7816650|否|
|L3|51965|156187|104222|7816650|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":104222,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":104222,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":104222,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":104222,"hire_quarter_cohort":104222,"hire_season":104222,"hire_year_cohort":104222,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":104222,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":104222,"retention_stability_score":104222,"tenure_years":104222,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`
- L1：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":104222,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":104222,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":104222,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":104222,"hire_quarter_cohort":104222,"hire_season":104222,"hire_year_cohort":104222,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":104222,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":104222,"retention_stability_score":104222,"tenure_years":104222,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`
- L2：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":104222,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":104222,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":104222,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":104222,"hire_quarter_cohort":104222,"hire_season":104222,"hire_year_cohort":104222,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":104222,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":104222,"retention_stability_score":104222,"tenure_years":104222,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`
- L3：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":104222,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":104222,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":104222,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":104222,"hire_quarter_cohort":104222,"hire_season":104222,"hire_year_cohort":104222,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":104222,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":104222,"retention_stability_score":104222,"tenure_years":104222,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`

#### comp_base_multiplicity

判定：探索修正方向不成立，排除归因；类别候选 C。契约明确 compensation 从 ebe 出发并按 worker/source/position 回接；agent 直接按 position profile 连接省略 ebe 重复。

相对本轮基线减少行 -271780、格 -13022913；按行优先、格次之排序。
共同控制后 SQL 第 20 行起、字符 offset 1772 的唯一连续替换；其余字节不动。
替换前：
```sql
FROM staging.stg_workday__position_job_profile p
 LEFT JOIN staging.stg_workday__job_profile jp ON p.job_profile_id=jp.job_profile_id AND p.source_relation=jp.source_relation
```

替换后：
```sql
FROM staging.stg_workday__position_job_profile p
 LEFT JOIN staging.stg_workday__job_profile jp ON p.job_profile_id=jp.job_profile_id AND p.source_relation=jp.source_relation
 JOIN intermediate.int_workday__worker_employee_enhanced eb ON eb.position_id=p.position_id AND eb.source_relation=p.source_relation
```

私有 SQL：`data/023_work/impl-016_workday__employee_overview/comp_base_multiplicity.sql`；SHA-256 `27d862cb26657e83680bf74800fabf616976a3531ad41dfe49de244e2b545bd4`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|427967|156187|427967|21098507|否|
|L1|427967|156187|427967|21098602|否|
|L2|427967|156187|427967|21098602|否|
|L3|427967|156187|427967|21098602|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"employee_id":271780,"worker_id":271780,"position_id":271780,"worker_history_id":271780,"organization_id":271780,"compensation_grade_id":271780,"business_title":271780,"career_development_score":271780,"career_growth_pace":271780,"career_phase":271780,"career_stability_category":271780,"churn_risk_category":271780,"city_of_birth":271780,"compensation_tier":427967,"comprehensive_data_quality_flag":271780,"country_of_birth":271780,"date_of_birth":271780,"days_as_worker":271780,"days_in_position":271780,"default_weekly_hours":271780,"departure_category":323074,"departure_date":271780,"dept_health_score":271780,"dept_management_ratio":271780,"dept_performance_category":271780,"dept_size":271780,"dept_size_category":271780,"dept_turnover_rate":271780,"email_address":271780,"employee_maturity_segment":323074,"employee_risk_level":271780,"employee_type":271780,"employee_value_segment":271780,"ethnicity_codes":271780,"event_type":271780,"fast_promotions":271780,"first_name":271780,"full_name":271780,"highest_management_level_reached":271780,"hire_date":271780,"hire_month":353888,"hire_quarter_cohort":356378,"hire_season":338673,"hire_year_cohort":343196,"is_current_employee_five_years":271780,"is_current_employee_one_year":271780,"is_current_employee_ten_years":271780,"is_employed":271780,"is_employed_five_years":271780,"is_employed_one_year":271780,"is_employed_ten_years":271780,"is_military_service":271780,"is_union_eligible":271780,"is_work_shift_required":271780,"last_name":271780,"lateral_moves":271780,"management_positions_held":271780,"marital_status":271780,"military_status":271780,"organization_name":271780,"organization_sub_type":271780,"organization_type":271780,"overall_employee_score":271780,"position_end_date":271780,"position_start_date":271780,"retained_1_year":313371,"retained_30_days":271780,"retained_3_years":271780,"retained_90_days":292136,"retention_stability_score":271780,"tenure_years":361050,"total_demotions":271780,"total_positions_held":271780,"total_promotions":271780,"work_conditions_score":271780}`
- L1：`{"employee_id":271780,"worker_id":271780,"position_id":271780,"worker_history_id":271780,"organization_id":271780,"compensation_grade_id":271780,"business_title":271780,"career_development_score":271780,"career_growth_pace":271780,"career_phase":271780,"career_stability_category":271780,"churn_risk_category":271780,"city_of_birth":271780,"compensation_tier":427967,"comprehensive_data_quality_flag":271780,"country_of_birth":271780,"date_of_birth":271780,"days_as_worker":271780,"days_in_position":271780,"default_weekly_hours":271780,"departure_category":323074,"departure_date":271780,"dept_health_score":271780,"dept_management_ratio":271780,"dept_performance_category":271780,"dept_size":271780,"dept_size_category":271780,"dept_turnover_rate":271780,"email_address":271780,"employee_maturity_segment":323074,"employee_risk_level":271780,"employee_type":271780,"employee_value_segment":271780,"ethnicity_codes":271780,"event_type":271780,"fast_promotions":271780,"first_name":271780,"full_name":271780,"highest_management_level_reached":271780,"hire_date":271780,"hire_month":353852,"hire_quarter_cohort":356456,"hire_season":338653,"hire_year_cohort":343275,"is_current_employee_five_years":271780,"is_current_employee_one_year":271780,"is_current_employee_ten_years":271780,"is_employed":271780,"is_employed_five_years":271780,"is_employed_one_year":271780,"is_employed_ten_years":271780,"is_military_service":271780,"is_union_eligible":271780,"is_work_shift_required":271780,"last_name":271780,"lateral_moves":271780,"management_positions_held":271780,"marital_status":271780,"military_status":271780,"organization_name":271780,"organization_sub_type":271780,"organization_type":271780,"overall_employee_score":271780,"position_end_date":271780,"position_start_date":271780,"retained_1_year":313371,"retained_30_days":271780,"retained_3_years":271780,"retained_90_days":292136,"retention_stability_score":271780,"tenure_years":361044,"total_demotions":271780,"total_positions_held":271780,"total_promotions":271780,"work_conditions_score":271780}`
- L2：`{"employee_id":271780,"worker_id":271780,"position_id":271780,"worker_history_id":271780,"organization_id":271780,"compensation_grade_id":271780,"business_title":271780,"career_development_score":271780,"career_growth_pace":271780,"career_phase":271780,"career_stability_category":271780,"churn_risk_category":271780,"city_of_birth":271780,"compensation_tier":427967,"comprehensive_data_quality_flag":271780,"country_of_birth":271780,"date_of_birth":271780,"days_as_worker":271780,"days_in_position":271780,"default_weekly_hours":271780,"departure_category":323074,"departure_date":271780,"dept_health_score":271780,"dept_management_ratio":271780,"dept_performance_category":271780,"dept_size":271780,"dept_size_category":271780,"dept_turnover_rate":271780,"email_address":271780,"employee_maturity_segment":323074,"employee_risk_level":271780,"employee_type":271780,"employee_value_segment":271780,"ethnicity_codes":271780,"event_type":271780,"fast_promotions":271780,"first_name":271780,"full_name":271780,"highest_management_level_reached":271780,"hire_date":271780,"hire_month":353852,"hire_quarter_cohort":356456,"hire_season":338653,"hire_year_cohort":343275,"is_current_employee_five_years":271780,"is_current_employee_one_year":271780,"is_current_employee_ten_years":271780,"is_employed":271780,"is_employed_five_years":271780,"is_employed_one_year":271780,"is_employed_ten_years":271780,"is_military_service":271780,"is_union_eligible":271780,"is_work_shift_required":271780,"last_name":271780,"lateral_moves":271780,"management_positions_held":271780,"marital_status":271780,"military_status":271780,"organization_name":271780,"organization_sub_type":271780,"organization_type":271780,"overall_employee_score":271780,"position_end_date":271780,"position_start_date":271780,"retained_1_year":313371,"retained_30_days":271780,"retained_3_years":271780,"retained_90_days":292136,"retention_stability_score":271780,"tenure_years":361044,"total_demotions":271780,"total_positions_held":271780,"total_promotions":271780,"work_conditions_score":271780}`
- L3：`{"employee_id":271780,"worker_id":271780,"position_id":271780,"worker_history_id":271780,"organization_id":271780,"compensation_grade_id":271780,"business_title":271780,"career_development_score":271780,"career_growth_pace":271780,"career_phase":271780,"career_stability_category":271780,"churn_risk_category":271780,"city_of_birth":271780,"compensation_tier":427967,"comprehensive_data_quality_flag":271780,"country_of_birth":271780,"date_of_birth":271780,"days_as_worker":271780,"days_in_position":271780,"default_weekly_hours":271780,"departure_category":323074,"departure_date":271780,"dept_health_score":271780,"dept_management_ratio":271780,"dept_performance_category":271780,"dept_size":271780,"dept_size_category":271780,"dept_turnover_rate":271780,"email_address":271780,"employee_maturity_segment":323074,"employee_risk_level":271780,"employee_type":271780,"employee_value_segment":271780,"ethnicity_codes":271780,"event_type":271780,"fast_promotions":271780,"first_name":271780,"full_name":271780,"highest_management_level_reached":271780,"hire_date":271780,"hire_month":353852,"hire_quarter_cohort":356456,"hire_season":338653,"hire_year_cohort":343275,"is_current_employee_five_years":271780,"is_current_employee_one_year":271780,"is_current_employee_ten_years":271780,"is_employed":271780,"is_employed_five_years":271780,"is_employed_one_year":271780,"is_employed_ten_years":271780,"is_military_service":271780,"is_union_eligible":271780,"is_work_shift_required":271780,"last_name":271780,"lateral_moves":271780,"management_positions_held":271780,"marital_status":271780,"military_status":271780,"organization_name":271780,"organization_sub_type":271780,"organization_type":271780,"overall_employee_score":271780,"position_end_date":271780,"position_start_date":271780,"retained_1_year":313371,"retained_30_days":271780,"retained_3_years":271780,"retained_90_days":292136,"retention_stability_score":271780,"tenure_years":361044,"total_demotions":271780,"total_positions_held":271780,"total_promotions":271780,"work_conditions_score":271780}`
### 补充轮：[023_supplement_reruns_impl-016_workday__employee_overview.json](../023_supplement_reruns_impl-016_workday__employee_overview.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`。

共同时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":3}]`。

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_supplement_work/impl-016_workday__employee_overview/baseline.sql`；SHA-256 `70bae469ba378083d22ac4265b464b9c7d1f97d194a5d91bd341504aeed42aca`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|51965|156187|156187|8075594|否|
|L1|51965|156187|156187|8075594|否|
|L2|51965|156187|156187|8075594|否|
|L3|51965|156187|156187|8075594|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":156187,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":125907,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":125907,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":132786,"hire_quarter_cohort":133756,"hire_season":127614,"hire_year_cohort":129170,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":119507,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":114939,"retention_stability_score":104222,"tenure_years":135391,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`
- L1：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":156187,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":125907,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":125907,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":132781,"hire_quarter_cohort":133771,"hire_season":127653,"hire_year_cohort":129121,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":119507,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":114939,"retention_stability_score":104222,"tenure_years":135391,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`
- L2：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":156187,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":125907,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":125907,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":132781,"hire_quarter_cohort":133771,"hire_season":127653,"hire_year_cohort":129121,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":119507,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":114939,"retention_stability_score":104222,"tenure_years":135391,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`
- L3：`{"employee_id":104222,"worker_id":104222,"position_id":104222,"worker_history_id":104222,"organization_id":104222,"compensation_grade_id":104222,"business_title":104222,"career_development_score":104222,"career_growth_pace":104222,"career_phase":104222,"career_stability_category":104222,"churn_risk_category":104222,"city_of_birth":104222,"compensation_tier":156187,"comprehensive_data_quality_flag":104222,"country_of_birth":104222,"date_of_birth":104222,"days_as_worker":104222,"days_in_position":104222,"default_weekly_hours":104222,"departure_category":125907,"departure_date":104222,"dept_health_score":104222,"dept_management_ratio":104222,"dept_performance_category":104222,"dept_size":104222,"dept_size_category":104222,"dept_turnover_rate":104222,"email_address":104222,"employee_maturity_segment":125907,"employee_risk_level":104222,"employee_type":104222,"employee_value_segment":104222,"ethnicity_codes":104222,"event_type":104222,"fast_promotions":104222,"first_name":104222,"full_name":104222,"highest_management_level_reached":104222,"hire_date":104222,"hire_month":132781,"hire_quarter_cohort":133771,"hire_season":127653,"hire_year_cohort":129121,"is_current_employee_five_years":104222,"is_current_employee_one_year":104222,"is_current_employee_ten_years":104222,"is_employed":104222,"is_employed_five_years":104222,"is_employed_one_year":104222,"is_employed_ten_years":104222,"is_military_service":104222,"is_union_eligible":104222,"is_work_shift_required":104222,"last_name":104222,"lateral_moves":104222,"management_positions_held":104222,"marital_status":104222,"military_status":104222,"organization_name":104222,"organization_sub_type":104222,"organization_type":104222,"overall_employee_score":104222,"position_end_date":104222,"position_start_date":104222,"retained_1_year":119507,"retained_30_days":104222,"retained_3_years":104222,"retained_90_days":114939,"retention_stability_score":104222,"tenure_years":135391,"total_demotions":104222,"total_positions_held":104222,"total_promotions":104222,"work_conditions_score":104222}`

#### comp_ebe_join

判定：参与因素；类别候选 C。恢复契约规定 ebe 派生 compensation 后按 worker/source/position 回接的重复度；仅修改该 JOIN 一处。

相对本轮基线减少行 0、格 7919407；按行优先、格次之排序。
共同控制后 SQL 第 31 行起、字符 offset 3103 的唯一连续替换；其余字节不动。
替换前：
```sql
LEFT JOIN comp ON b.position_id=comp.position_id AND b.source_relation=comp.source_relation
```

替换后：
```sql
LEFT JOIN (SELECT eb.worker_id,eb.position_id,eb.source_relation,c.compensation_grade_id,c.is_work_shift_required,c.is_union_eligible FROM intermediate.int_workday__worker_employee_enhanced eb LEFT JOIN comp c ON eb.position_id=c.position_id AND eb.source_relation=c.source_relation) comp ON b.worker_id=comp.worker_id AND b.position_id=comp.position_id AND b.source_relation=comp.source_relation
```

私有 SQL：`data/023_supplement_work/impl-016_workday__employee_overview/comp_ebe_join.sql`；SHA-256 `e2ee3f2c3496e6363df8df5db3656256c94034b3ef4ab46a8d14f5360afd625b`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|156187|156187|156187|156187|否|
|L1|156187|156187|156187|156187|否|
|L2|156187|156187|156187|156187|否|
|L3|156187|156187|156187|156187|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"compensation_tier":156187}`
- L1：`{"compensation_tier":156187}`
- L2：`{"compensation_tier":156187}`
- L3：`{"compensation_tier":156187}`

## 原始表改动核对

raw.person_contact_email_address initial/gold 7284、agent 2448。查完原始事件0–84、run.py 导入源码及013写操作清单，只有event39/40、53/54、65/66导入事件，输出均为7284；未找到削减到2448的命令或原因。不能把导入日志当作削减证据。

初始/gold 一致而 agent 有变化，依第 3 节照常标注，不标不可评估。完整表清单见 [023_raw_trace_review.json](../023_raw_trace_review.json)；输入不变性另由前后指纹验证。

## 规则问题

无
