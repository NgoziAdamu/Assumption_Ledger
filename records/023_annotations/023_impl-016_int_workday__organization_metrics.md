# impl-016 · int_workday__organization_metrics

用途：**全量**；层：`intermediate`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**C**；把握：高；主要错误点：tenure_all_assignments。

avg_tenure_days 从仅当前 assignment 的 current_stats 取值，违反契约要求覆盖历史与当前 assignment。

参与因素：无。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-016_int_workday__organization_metrics.md](../023_packages/023_impl-016_int_workday__organization_metrics.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml`；SHA-256 `8f0707fc595c6f2f1e46a1983436959278e10315cb723e975c2811858d737c91`。
契约行 599–777：

```
599:     - name: int_workday__organization_metrics
600:       description: Organizational health and efficiency metrics aggregated for active Workday organizations
601:       grain: One row per (organization_id, source_relation) for active organizations (is_inactive = false)
602:       source_models:
603:       - staging.stg_workday__organization
604:       - staging.stg_workday__worker_position_organization
605:       - staging.stg_workday__position
606:       - staging.stg_workday__position_job_profile
607:       - staging.stg_workday__job_profile
608:       - staging.stg_workday__job_family_job_profile
609:       - staging.stg_workday__job_family
610:       - staging.stg_workday__job_family_job_family_group
611:       - staging.stg_workday__job_family_group
612:       business_logic: 'Build the base set from organizations marked active. Derive current employee distribution from worker-position-organization joined to position and job profile, restricted to current assignments (no end date): count distinct workers and positions; count distinct current workers by employee type (Regular, Contingent, Intern); compute average and total weekly hours treating missing weekly hours as 40 before aggregation; count distinct current workers by management level (Manager, Senior Manager, Director, Individual Contributor). Derive mobility from all assignments (historical and current), grouped by organization and source: new_hires_last_year counts distinct workers whose assignment started in the past year; departures_last_year counts distinct workers whose assignment ended in the past year; internal_transfers_in counts distinct workers who started in the past year and had any earlier assignment in a different organization within the same source; internal_transfers_out counts distinct workers who ended in the past year and had any later assignment in a different organization within the same source; avg_tenure_days averages days between start and end (or start and today if still active). Derive compensation distribution from current assignments: count distinct compensation grades, job families, and job family groups; most_common_grade is the most frequent compensation grade with ties resolved to the smallest grade ID; count distinct current workers whose job requires shift work or is union eligible. Left join all aggregates to the active organizations and apply defaults: counts to 0, most_common_grade to ''Unknown'', avg_weekly_hours to 40 if no current positions, total_weekly_hours to 0. Compute metrics: organization_health_score (0–100) is 0 when there are no current employees; otherwise sum five 20-point checks capped at 100: has employees; turnover (departures_last_year/current employees) below 20%; management share (managers/current employees) between 10% and 30% inclusive; at least two job families; average tenure at least 365 days. Compute ratios rounded to two decimals: position_fill_rate is current employees divided by total positions times 100 when positions exist, else 0; annual_turnover_rate is departures_last_year divided by current employees times 100 when employees exist, else 0; management_ratio is managers divided by current employees times 100 when employees exist, else 0. Classify performance by health score: ≥80 High Performance, ≥60 Good Performance, ≥40 Average Performance, ≥20 Below Average, else Needs Attention. Classify size by current employee count: 0 Empty, ≤10 Small Team, ≤50 Medium Team, ≤200 Large Team, else Enterprise Unit. Set data_quality_flag with precedence: ERROR if employee count is negative; else WARNING if employees exceed positions, or turnover rate >100%, or management ratio >50%; else VALID.'
613:       columns:
614:       - name: organization_id
615:         data_type: VARCHAR
616:         description: Primary grouping key from stg_workday__organization; one row per organization_id + source_relation
617:         tests:
618:         - not_null
619:       - name: source_relation
620:         data_type: VARCHAR
621:         description: Source system identifier propagated from staging tables
622:         tests:
623:         - not_null
624:       - name: organization_name
625:         data_type: VARCHAR
626:         description: Display name copied from stg_workday__organization (may be NULL)
627:       - name: organization_code
628:         data_type: VARCHAR
629:         description: Organization code copied from stg_workday__organization (may be NULL)
630:       - name: organization_type
631:         data_type: VARCHAR
632:         description: Type copied from stg_workday__organization (may be NULL)
633:       - name: organization_sub_type
634:         data_type: VARCHAR
635:         description: Sub-type copied from stg_workday__organization (may be NULL)
636:       - name: staffing_model
637:         data_type: VARCHAR
638:         description: Staffing model copied from stg_workday__organization (may be NULL)
639:       - name: current_employee_count
640:         data_type: BIGINT
641:         description: Distinct current workers per organization (assignments with no end date); defaults to 0
642:         tests:
643:         - not_null
644:       - name: total_positions
645:         data_type: BIGINT
646:         description: Distinct current positions per organization (assignments with no end date); defaults to 0
647:         tests:
648:         - not_null
649:       - name: regular_employees
650:         data_type: BIGINT
651:         description: Distinct current workers in positions labeled Regular; defaults to 0
652:         tests:
653:         - not_null
654:       - name: contingent_employees
655:         data_type: BIGINT
656:         description: Distinct current workers in positions labeled Contingent; defaults to 0
657:         tests:
658:         - not_null
659:       - name: intern_employees
660:         data_type: BIGINT
661:         description: Distinct current workers in positions labeled Intern; defaults to 0
662:         tests:
663:         - not_null
664:       - name: avg_weekly_hours
665:         data_type: DOUBLE
666:         description: Average weekly hours over current positions, treating missing hours as 40; defaults to 40 when no current positions
667:         tests:
668:         - not_null
669:       - name: total_weekly_hours
670:         data_type: HUGEINT
671:         description: Total weekly hours over current positions, treating missing hours as 40; defaults to 0
672:         tests:
673:         - not_null
674:       - name: managers_count
675:         data_type: BIGINT
676:         description: Distinct current workers with management level Manager; defaults to 0
677:         tests:
678:         - not_null
679:       - name: senior_managers_count
680:         data_type: BIGINT
681:         description: Distinct current workers with management level Senior Manager; defaults to 0
682:         tests:
683:         - not_null
684:       - name: directors_count
685:         data_type: BIGINT
686:         description: Distinct current workers with management level Director; defaults to 0
687:         tests:
688:         - not_null
689:       - name: individual_contributors
690:         data_type: BIGINT
691:         description: Distinct current workers with management level Individual Contributor; defaults to 0
692:         tests:
693:         - not_null
694:       - name: new_hires_last_year
695:         data_type: BIGINT
696:         description: Distinct workers whose assignment started within the past year; defaults to 0
697:         tests:
698:         - not_null
699:       - name: departures_last_year
700:         data_type: BIGINT
701:         description: Distinct workers whose assignment ended within the past year; defaults to 0
702:         tests:
703:         - not_null
704:       - name: internal_transfers_in
705:         data_type: BIGINT
706:         description: Distinct workers who started within the past year and had any earlier assignment in a different organization; defaults to 0
707:         tests:
708:         - not_null
709:       - name: internal_transfers_out
710:         data_type: BIGINT
711:         description: Distinct workers who ended within the past year and had any later assignment in a different organization; defaults to 0
712:         tests:
713:         - not_null
714:       - name: avg_tenure_days
715:         data_type: DOUBLE
716:         description: Average days from assignment start to end (or to today if active) across all assignments; defaults to 0
717:         tests:
718:         - not_null
719:       - name: unique_compensation_grades
720:         data_type: BIGINT
721:         description: Distinct compensation grades across current positions; defaults to 0
722:         tests:
723:         - not_null
724:       - name: most_common_grade
725:         data_type: VARCHAR
726:         description: Most frequent compensation grade across current positions, breaking ties to the smallest grade ID; defaults to 'Unknown'
727:         tests:
728:         - not_null
729:       - name: unique_job_families
730:         data_type: BIGINT
731:         description: Distinct job families across current positions; defaults to 0
732:         tests:
733:         - not_null
734:       - name: unique_job_family_groups
735:         data_type: BIGINT
736:         description: Distinct job family groups across current positions; defaults to 0
737:         tests:
738:         - not_null
739:       - name: shift_required_positions
740:         data_type: BIGINT
741:         description: Distinct current workers whose job profile requires shift work; defaults to 0
742:         tests:
743:         - not_null
744:       - name: union_eligible_positions
745:         data_type: BIGINT
746:         description: Distinct current workers whose job profile is union eligible; defaults to 0
747:         tests:
748:         - not_null
749:       - name: organization_health_score
750:         data_type: INTEGER
751:         description: Five 20-point checks summed and capped at 100, or 0 when there are no current employees
752:         tests:
753:         - not_null
754:       - name: position_fill_rate
755:         data_type: DOUBLE
756:         description: Current employees as a percentage of total positions when positions exist, else 0, rounded to two decimals
757:       - name: annual_turnover_rate
758:         data_type: DOUBLE
759:         description: Departures in the past year as a percentage of current employees when employees exist, else 0, rounded to two decimals
760:         tests:
761:         - not_null
762:       - name: management_ratio
763:         data_type: DOUBLE
764:         description: Managers as a percentage of current employees when employees exist, else 0, rounded to two decimals
765:         tests:
766:         - not_null
767:       - name: performance_category
768:         data_type: VARCHAR
769:         description: 'Bucketed from organization_health_score: ≥80 High Performance, ≥60 Good Performance, ≥40 Average Performance, ≥20 Below Average, else Needs Attention'
770:         tests:
771:         - performance_category IN ('High Performance','Good Performance','Average Performance','Below Average','Needs Attention')
772:       - name: organization_size_category
773:         data_type: VARCHAR
774:         description: 'Size by current_employee_count: 0 Empty, ≤10 Small Team, ≤50 Medium Team, ≤200 Large Team, else Enterprise Unit'
775:       - name: data_quality_flag
776:         data_type: VARCHAR
777:         description: 'Precedence: ERROR if negative employees; else WARNING if employees exceed positions or turnover >100% or management ratio >50%; else VALID'
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/intermediate/int_workday__organization_metrics.sql`，SHA-256 `48a68b720ccfe1acaac3c2ba6ec665c87c317b28e32d769df198341174bc8bc9`，行 1–70。

```
1: WITH active_org AS (
2:     SELECT * FROM staging.stg_workday__organization WHERE is_inactive = FALSE
3: ), assignments AS (
4:     SELECT wpo.worker_id, wpo.position_id, wpo.organization_id, wpo.source_relation,
5:            wpo.effective_start, wpo.effective_end,
6:            p.employee_type, p.default_weekly_hours, jp.management_level, jp.compensation_grade_id,
7:            jp.is_work_shift_required, jp.is_union_eligible, jf.job_family_id, jfg.job_family_group_id
8:     FROM staging.stg_workday__worker_position_organization AS wpo
9:     LEFT JOIN staging.stg_workday__position AS p ON wpo.position_id=p.position_id
10:     LEFT JOIN staging.stg_workday__position_job_profile AS pjp ON p.position_id=pjp.position_id AND p.source_relation=pjp.source_relation
11:     LEFT JOIN staging.stg_workday__job_profile AS jp ON pjp.job_profile_id=jp.job_profile_id AND pjp.source_relation=jp.source_relation
12:     LEFT JOIN staging.stg_workday__job_family_job_profile AS jfjp ON jp.job_profile_id=jfjp.job_profile_id AND jp.source_relation=jfjp.source_relation
13:     LEFT JOIN staging.stg_workday__job_family AS jf ON jfjp.job_family_id=jf.job_family_id AND jfjp.source_relation=jf.source_relation
14:     LEFT JOIN staging.stg_workday__job_family_job_family_group AS jfjg ON jf.job_family_id=jfjg.job_family_id AND jf.source_relation=jfjg.source_relation
15:     LEFT JOIN staging.stg_workday__job_family_group AS jfg ON jfjg.job_family_group_id=jfg.job_family_group_id AND jfjg.source_relation=jfg.source_relation
16: ), current_stats AS (
17:  SELECT organization_id, source_relation, count(DISTINCT worker_id) current_employee_count,
18:  count(DISTINCT position_id) total_positions,
19:  count(DISTINCT worker_id) FILTER(WHERE employee_type='Regular') regular_employees,
20:  count(DISTINCT worker_id) FILTER(WHERE employee_type='Contingent') contingent_employees,
21:  count(DISTINCT worker_id) FILTER(WHERE employee_type='Intern') intern_employees,
22:  coalesce(avg(coalesce(default_weekly_hours,40)),40)::DOUBLE avg_weekly_hours,
23:  coalesce(sum(coalesce(default_weekly_hours,40)),0)::HUGEINT total_weekly_hours,
24:  count(DISTINCT worker_id) FILTER(WHERE management_level='Manager') managers_count,
25:  count(DISTINCT worker_id) FILTER(WHERE management_level='Senior Manager') senior_managers_count,
26:  count(DISTINCT worker_id) FILTER(WHERE management_level='Director') directors_count,
27:  count(DISTINCT worker_id) FILTER(WHERE management_level='Individual Contributor') individual_contributors,
28:  count(DISTINCT compensation_grade_id) unique_compensation_grades,
29:  count(DISTINCT job_family_id) unique_job_families,count(DISTINCT job_family_group_id) unique_job_family_groups,
30:  count(DISTINCT worker_id) FILTER(WHERE is_work_shift_required) shift_required_positions,
31:  count(DISTINCT worker_id) FILTER(WHERE is_union_eligible) union_eligible_positions,
32:  avg(date_diff('day',effective_start,coalesce(effective_end,current_date))) avg_tenure_days
33:  FROM assignments WHERE effective_end IS NULL GROUP BY organization_id,source_relation
34: ), mobility AS (
35:  SELECT a.organization_id,a.source_relation,
36:  count(DISTINCT worker_id) FILTER(WHERE effective_start >= current_date - INTERVAL '1 year') new_hires_last_year,
37:  count(DISTINCT worker_id) FILTER(WHERE effective_end >= current_date - INTERVAL '1 year') departures_last_year,
38:  count(DISTINCT worker_id) FILTER(WHERE effective_start >= current_date - INTERVAL '1 year' AND EXISTS (SELECT 1 FROM assignments x WHERE x.worker_id=a.worker_id AND x.source_relation=a.source_relation AND x.organization_id<>a.organization_id AND x.effective_start<a.effective_start)) internal_transfers_in,
39:  count(DISTINCT worker_id) FILTER(WHERE effective_end >= current_date - INTERVAL '1 year' AND EXISTS (SELECT 1 FROM assignments x WHERE x.worker_id=a.worker_id AND x.source_relation=a.source_relation AND x.organization_id<>a.organization_id AND x.effective_start>a.effective_end)) internal_transfers_out
40:  FROM assignments a GROUP BY organization_id,source_relation
41: ), grade_freq AS (
42:  SELECT organization_id,source_relation,compensation_grade_id,
43:  row_number() over(partition by organization_id,source_relation order by count(*) desc, compensation_grade_id asc) rn
44:  FROM assignments WHERE effective_end IS NULL AND compensation_grade_id IS NOT NULL
45:  GROUP BY organization_id,source_relation,compensation_grade_id
46: )
47: SELECT o.organization_id,o.source_relation,o.organization_name,o.organization_code,o.organization_type,o.organization_sub_type,o.staffing_model,
48:  coalesce(c.current_employee_count,0)::BIGINT current_employee_count,coalesce(c.total_positions,0)::BIGINT total_positions,
49:  coalesce(c.regular_employees,0)::BIGINT regular_employees,coalesce(c.contingent_employees,0)::BIGINT contingent_employees,coalesce(c.intern_employees,0)::BIGINT intern_employees,
50:  coalesce(c.avg_weekly_hours,40)::DOUBLE avg_weekly_hours,coalesce(c.total_weekly_hours,0)::HUGEINT total_weekly_hours,
51:  coalesce(c.managers_count,0)::BIGINT managers_count,coalesce(c.senior_managers_count,0)::BIGINT senior_managers_count,coalesce(c.directors_count,0)::BIGINT directors_count,coalesce(c.individual_contributors,0)::BIGINT individual_contributors,
52:  coalesce(m.new_hires_last_year,0)::BIGINT new_hires_last_year,coalesce(m.departures_last_year,0)::BIGINT departures_last_year,
53:  coalesce(m.internal_transfers_in,0)::BIGINT internal_transfers_in,coalesce(m.internal_transfers_out,0)::BIGINT internal_transfers_out,
54:  coalesce(c.avg_tenure_days,0)::DOUBLE avg_tenure_days,coalesce(c.unique_compensation_grades,0)::BIGINT unique_compensation_grades,
55:  coalesce(g.compensation_grade_id,'Unknown')::VARCHAR most_common_grade,coalesce(c.unique_job_families,0)::BIGINT unique_job_families,coalesce(c.unique_job_family_groups,0)::BIGINT unique_job_family_groups,
56:  coalesce(c.shift_required_positions,0)::BIGINT shift_required_positions,coalesce(c.union_eligible_positions,0)::BIGINT union_eligible_positions,
57:  CASE WHEN coalesce(c.current_employee_count,0)=0 THEN 0 ELSE
58:  (20 + CASE WHEN coalesce(m.departures_last_year,0)*1.0/c.current_employee_count<0.2 THEN 20 ELSE 0 END+
59:  CASE WHEN c.managers_count*1.0/c.current_employee_count BETWEEN .1 AND .3 THEN 20 ELSE 0 END+
60:  CASE WHEN c.unique_job_families>=2 THEN 20 ELSE 0 END+CASE WHEN c.avg_tenure_days>=365 THEN 20 ELSE 0 END)::INTEGER END organization_health_score,
61:  CASE WHEN coalesce(c.total_positions,0)>0 THEN round(c.current_employee_count*100.0/c.total_positions,2) ELSE 0 END::DOUBLE position_fill_rate,
62:  CASE WHEN coalesce(c.current_employee_count,0)>0 THEN round(coalesce(m.departures_last_year,0)*100.0/c.current_employee_count,2) ELSE 0 END::DOUBLE annual_turnover_rate,
63:  CASE WHEN coalesce(c.current_employee_count,0)>0 THEN round(coalesce(c.managers_count,0)*100.0/c.current_employee_count,2) ELSE 0 END::DOUBLE management_ratio,
64:  CASE WHEN coalesce(c.current_employee_count,0)=0 THEN 'Needs Attention' WHEN c.current_employee_count>0 AND (20+CASE WHEN coalesce(m.departures_last_year,0)*1.0/c.current_employee_count<.2 THEN 20 ELSE 0 END+CASE WHEN c.managers_count*1.0/c.current_employee_count BETWEEN .1 AND .3 THEN 20 ELSE 0 END+CASE WHEN c.unique_job_families>=2 THEN 20 ELSE 0 END+CASE WHEN c.avg_tenure_days>=365 THEN 20 ELSE 0 END)>=80 THEN 'High Performance'
65:  WHEN coalesce(c.current_employee_count,0)>0 THEN CASE WHEN (20+CASE WHEN coalesce(m.departures_last_year,0)*1.0/c.current_employee_count<.2 THEN 20 ELSE 0 END+CASE WHEN c.managers_count*1.0/c.current_employee_count BETWEEN .1 AND .3 THEN 20 ELSE 0 END+CASE WHEN c.unique_job_families>=2 THEN 20 ELSE 0 END+CASE WHEN c.avg_tenure_days>=365 THEN 20 ELSE 0 END)>=60 THEN 'Good Performance' WHEN (20+CASE WHEN coalesce(m.departures_last_year,0)*1.0/c.current_employee_count<.2 THEN 20 ELSE 0 END+CASE WHEN c.managers_count*1.0/c.current_employee_count BETWEEN .1 AND .3 THEN 20 ELSE 0 END+CASE WHEN c.unique_job_families>=2 THEN 20 ELSE 0 END+CASE WHEN c.avg_tenure_days>=365 THEN 20 ELSE 0 END)>=40 THEN 'Average Performance' WHEN (20+CASE WHEN coalesce(m.departures_last_year,0)*1.0/c.current_employee_count<.2 THEN 20 ELSE 0 END+CASE WHEN c.managers_count*1.0/c.current_employee_count BETWEEN .1 AND .3 THEN 20 ELSE 0 END+CASE WHEN c.unique_job_families>=2 THEN 20 ELSE 0 END+CASE WHEN c.avg_tenure_days>=365 THEN 20 ELSE 0 END)>=20 THEN 'Below Average' ELSE 'Needs Attention' END END performance_category,
66:  CASE WHEN coalesce(c.current_employee_count,0)=0 THEN 'Empty' WHEN c.current_employee_count<=10 THEN 'Small Team' WHEN c.current_employee_count<=50 THEN 'Medium Team' WHEN c.current_employee_count<=200 THEN 'Large Team' ELSE 'Enterprise Unit' END organization_size_category,
67:  CASE WHEN c.current_employee_count<0 THEN 'ERROR' WHEN c.current_employee_count>c.total_positions OR (c.current_employee_count>0 AND coalesce(m.departures_last_year,0)*100.0/c.current_employee_count>100) OR (c.current_employee_count>0 AND coalesce(c.managers_count,0)*100.0/c.current_employee_count>50) THEN 'WARNING' ELSE 'VALID' END data_quality_flag
68: FROM active_org o LEFT JOIN current_stats c USING(organization_id,source_relation)
69: LEFT JOIN mobility m USING(organization_id,source_relation)
70: LEFT JOIN grade_freq g ON o.organization_id=g.organization_id AND o.source_relation=g.source_relation AND g.rn=1
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/intermediate/int_workday__organization_metrics.sql`，SHA-256 `f96011b122fdf699842e0436caa8125b738ec524f1d8ed55fcf743dd1c3f9be6`，行 1–256。

```
1: -- Intermediate table of organizational health and efficiency indicators
2: -- Calculate complex indicators such as department allocation efficiency, management level distribution, cross-department mobility, etc.
3: 
4: with organization_base as (
5:     select 
6:         o.organization_id,
7:         o.source_relation,
8:         o.organization_name,
9:         o.organization_code,
10:         o.organization_type,
11:         o.organization_sub_type,
12:         o.staffing_model,
13:         o.is_inactive
14:     from staging.stg_workday__organization o
15:     where not o.is_inactive
16: ),
17: 
18: -- Current employee distribution statistics
19: current_employee_distribution as (
20:     select 
21:         wpo.organization_id,
22:         wpo.source_relation,
23:         count(distinct wpo.worker_id) as current_employee_count,
24:         count(distinct wpo.position_id) as total_positions,
25:         
26:         -- Statistics by employee type
27:         count(distinct case when p.employee_type = 'Regular' then wpo.worker_id end) as regular_employees,
28:         count(distinct case when p.employee_type = 'Contingent' then wpo.worker_id end) as contingent_employees,
29:         count(distinct case when p.employee_type = 'Intern' then wpo.worker_id end) as intern_employees,
30:         
31:         -- Distribution of working hours
32:         avg(coalesce(p.default_weekly_hours, 40)) as avg_weekly_hours,
33:         sum(coalesce(p.default_weekly_hours, 40)) as total_weekly_hours,
34:         
35:         -- Management level analysis
36:         count(distinct case when jp.management_level = 'Manager' then wpo.worker_id end) as managers_count,
37:         count(distinct case when jp.management_level = 'Senior Manager' then wpo.worker_id end) as senior_managers_count,
38:         count(distinct case when jp.management_level = 'Director' then wpo.worker_id end) as directors_count,
39:         count(distinct case when jp.management_level = 'Individual Contributor' then wpo.worker_id end) as individual_contributors
40:         
41:     from staging.stg_workday__worker_position_organization wpo
42:     inner join staging.stg_workday__position p 
43:         on wpo.position_id = p.position_id 
44:         and wpo.source_relation = p.source_relation
45:     left join staging.stg_workday__position_job_profile pjp
46:         on p.position_id = pjp.position_id
47:         and p.source_relation = pjp.source_relation
48:     left join staging.stg_workday__job_profile jp
49:         on pjp.job_profile_id = jp.job_profile_id
50:         and pjp.source_relation = jp.source_relation
51:     where wpo.effective_end is null  -- Currently active positions
52:     group by wpo.organization_id, wpo.source_relation
53: ),
54: 
55: -- Historical employee turnover analysis
56: employee_mobility_analysis as (
57:     select 
58:         wpo.organization_id,
59:         wpo.source_relation,
60:         
61:         -- Inflow and outflow statistics
62:         count(distinct case when wpo.effective_start >= current_date - interval '1 year' 
63:               then wpo.worker_id end) as new_hires_last_year,
64:         count(distinct case when wpo.effective_end >= current_date - interval '1 year' 
65:               and wpo.effective_end is not null then wpo.worker_id end) as departures_last_year,
66:         
67:         -- internal mobility statistics
68:         count(distinct case when wpo.effective_start >= current_date - interval '1 year'
69:               and exists (
70:                   select 1 from staging.stg_workday__worker_position_organization wpo2
71:                   where wpo2.worker_id = wpo.worker_id 
72:                   and wpo2.source_relation = wpo.source_relation
73:                   and wpo2.organization_id != wpo.organization_id
74:                   and wpo2.effective_start < wpo.effective_start
75:               ) then wpo.worker_id end) as internal_transfers_in,
76:               
77:         count(distinct case when wpo.effective_end >= current_date - interval '1 year'
78:               and wpo.effective_end is not null
79:               and exists (
80:                   select 1 from staging.stg_workday__worker_position_organization wpo3
81:                   where wpo3.worker_id = wpo.worker_id 
82:                   and wpo3.source_relation = wpo.source_relation
83:                   and wpo3.organization_id != wpo.organization_id
84:                   and wpo3.effective_start > wpo.effective_end
85:               ) then wpo.worker_id end) as internal_transfers_out,
86:               
87:         -- Average tenure
88:         avg(case when wpo.effective_end is not null 
89:             then date_diff('day', wpo.effective_start, wpo.effective_end)
90:             else date_diff('day', wpo.effective_start, current_date)
91:         end) as avg_tenure_days
92:         
93:     from staging.stg_workday__worker_position_organization wpo
94:     group by wpo.organization_id, wpo.source_relation
95: ),
96: 
97: -- Salary grade distribution analysis
98: compensation_distribution as (
99:     select 
100:         wpo.organization_id,
101:         wpo.source_relation,
102:         
103:         -- Pay grade distribution
104:         count(distinct jp.compensation_grade_id) as unique_compensation_grades,
105:         mode() within group (order by jp.compensation_grade_id) as most_common_grade,
106:         
107:         -- career family diversity
108:         count(distinct jf.job_family_id) as unique_job_families,
109:         count(distinct jfg.job_family_group_id) as unique_job_family_groups,
110:         
111:         -- Special request statistics
112:         count(distinct case when jp.is_work_shift_required then wpo.worker_id end) as shift_required_positions,
113:         count(distinct case when jp.is_union_eligible then wpo.worker_id end) as union_eligible_positions
114:         
115:     from staging.stg_workday__worker_position_organization wpo
116:     inner join staging.stg_workday__position p 
117:         on wpo.position_id = p.position_id 
118:         and wpo.source_relation = p.source_relation
119:     left join staging.stg_workday__position_job_profile pjp
120:         on p.position_id = pjp.position_id
121:         and p.source_relation = pjp.source_relation
122:     left join staging.stg_workday__job_profile jp
123:         on pjp.job_profile_id = jp.job_profile_id
124:         and pjp.source_relation = jp.source_relation
125:     left join staging.stg_workday__job_family_job_profile jfjp
126:         on jp.job_profile_id = jfjp.job_profile_id
127:         and jp.source_relation = jfjp.source_relation
128:     left join staging.stg_workday__job_family jf
129:         on jfjp.job_family_id = jf.job_family_id
130:         and jfjp.source_relation = jf.source_relation
131:     left join staging.stg_workday__job_family_job_family_group jfjfg
132:         on jf.job_family_id = jfjfg.job_family_id
133:         and jf.source_relation = jfjfg.source_relation
134:     left join staging.stg_workday__job_family_group jfg
135:         on jfjfg.job_family_group_id = jfg.job_family_group_id
136:         and jfjfg.source_relation = jfg.source_relation
137:     where wpo.effective_end is null  -- Currently active positions
138:     group by wpo.organization_id, wpo.source_relation
139: ),
140: 
141: -- Overall organizational health score
142: organization_health_metrics as (
143:     select 
144:         ob.organization_id,
145:         ob.source_relation,
146:         ob.organization_name,
147:         ob.organization_code,
148:         ob.organization_type,
149:         ob.organization_sub_type,
150:         ob.staffing_model,
151:         
152:         -- Staff size indicator
153:         coalesce(ced.current_employee_count, 0) as current_employee_count,
154:         coalesce(ced.total_positions, 0) as total_positions,
155:         coalesce(ced.regular_employees, 0) as regular_employees,
156:         coalesce(ced.contingent_employees, 0) as contingent_employees,
157:         coalesce(ced.intern_employees, 0) as intern_employees,
158:         
159:         -- Workload Metrics
160:         coalesce(ced.avg_weekly_hours, 40) as avg_weekly_hours,
161:         coalesce(ced.total_weekly_hours, 0) as total_weekly_hours,
162:         
163:         -- management level indicators
164:         coalesce(ced.managers_count, 0) as managers_count,
165:         coalesce(ced.senior_managers_count, 0) as senior_managers_count,
166:         coalesce(ced.directors_count, 0) as directors_count,
167:         coalesce(ced.individual_contributors, 0) as individual_contributors,
168:         
169:         -- liquidity indicator
170:         coalesce(ema.new_hires_last_year, 0) as new_hires_last_year,
171:         coalesce(ema.departures_last_year, 0) as departures_last_year,
172:         coalesce(ema.internal_transfers_in, 0) as internal_transfers_in,
173:         coalesce(ema.internal_transfers_out, 0) as internal_transfers_out,
174:         coalesce(ema.avg_tenure_days, 0) as avg_tenure_days,
175:         
176:         -- diversity index
177:         coalesce(cd.unique_compensation_grades, 0) as unique_compensation_grades,
178:         coalesce(cd.most_common_grade, 'Unknown') as most_common_grade,
179:         coalesce(cd.unique_job_families, 0) as unique_job_families,
180:         coalesce(cd.unique_job_family_groups, 0) as unique_job_family_groups,
181:         coalesce(cd.shift_required_positions, 0) as shift_required_positions,
182:         coalesce(cd.union_eligible_positions, 0) as union_eligible_positions,
183:         
184:         -- Calculate health score (0-100)
185:         case 
186:             when coalesce(ced.current_employee_count, 0) = 0 then 0
187:             else least(100, 
188:                 (case when coalesce(ced.current_employee_count, 0) > 0 then 20 else 0 end) +  -- Have employee base points
189:                 (case when coalesce(ema.departures_last_year, 0) / nullif(coalesce(ced.current_employee_count, 1), 0) < 0.2 then 20 else 0 end) +  -- low churn rate
190:                 (case when coalesce(ced.managers_count, 0) / nullif(coalesce(ced.current_employee_count, 1), 0) between 0.1 and 0.3 then 20 else 0 end) +  -- Reasonable management ratio
191:                 (case when coalesce(cd.unique_job_families, 0) >= 2 then 20 else 0 end) +  -- functional diversity
192:                 (case when coalesce(ema.avg_tenure_days, 0) >= 365 then 20 else 0 end)  -- employee stability
193:             )
194:         end as organization_health_score,
195:         
196:         -- Efficiency Ratio Calculation
197:         case 
198:             when coalesce(ced.total_positions, 0) > 0 then 
199:                 round(coalesce(ced.current_employee_count, 0) * 100.0 / ced.total_positions, 2)
200:             else 0 
201:         end as position_fill_rate,
202:         
203:         case 
204:             when coalesce(ced.current_employee_count, 0) > 0 then 
205:                 round(coalesce(ema.departures_last_year, 0) * 100.0 / ced.current_employee_count, 2)
206:             else 0 
207:         end as annual_turnover_rate,
208:         
209:         case 
210:             when coalesce(ced.current_employee_count, 0) > 0 then 
211:                 round(coalesce(ced.managers_count, 0) * 100.0 / ced.current_employee_count, 2)
212:             else 0 
213:         end as management_ratio
214:         
215:     from organization_base ob
216:     left join current_employee_distribution ced
217:         on ob.organization_id = ced.organization_id
218:         and ob.source_relation = ced.source_relation
219:     left join employee_mobility_analysis ema
220:         on ob.organization_id = ema.organization_id
221:         and ob.source_relation = ema.source_relation
222:     left join compensation_distribution cd
223:         on ob.organization_id = cd.organization_id
224:         and ob.source_relation = cd.source_relation
225: )
226: 
227: select 
228:     *,
229:     -- Organization type classification
230:     case 
231:         when organization_health_score >= 80 then 'High Performance'
232:         when organization_health_score >= 60 then 'Good Performance'
233:         when organization_health_score >= 40 then 'Average Performance'
234:         when organization_health_score >= 20 then 'Below Average'
235:         else 'Needs Attention'
236:     end as performance_category,
237:     
238:     -- Size classification
239:     case 
240:         when current_employee_count = 0 then 'Empty'
241:         when current_employee_count <= 10 then 'Small Team'
242:         when current_employee_count <= 50 then 'Medium Team'
243:         when current_employee_count <= 200 then 'Large Team'
244:         else 'Enterprise Unit'
245:     end as organization_size_category,
246:     
247:     -- Data quality check
248:     case 
249:         when current_employee_count < 0 then 'ERROR: Negative employee count'
250:         when total_positions < current_employee_count then 'WARNING: More employees than positions'
251:         when annual_turnover_rate > 100 then 'WARNING: Turnover rate exceeds 100%'
252:         when management_ratio > 50 then 'WARNING: High management ratio'
253:         else 'VALID'
254:     end as data_quality_flag
255:     
256: from organization_health_metrics
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 1 契约明确 all assignments；event 25 生成 current_stats 取值；event 55/56 观察当前 assignment 为0。event 83 仅解释当前 headcount，不解释历史任期被排除。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 1：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json`。
- event 25：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/25.json`。
- event 55：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/55.json`。
- event 56：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/56.json`。
- event 83：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/83.json`。
## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：当前与历史

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/workday.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE effective_end IS NULL) current_rows FROM staging.stg_workday__worker_position_organization
```


```json
{"columns":["n","current_rows"],"rows":[[10317,0]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-016_int_workday__organization_metrics.json](../023_reruns_impl-016_int_workday__organization_metrics.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`。

共同时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":5}]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|117|否|
|L1|117|117|117|117|否|
|L2|117|117|117|117|否|
|L3|117|117|117|117|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"avg_tenure_days":117}`
- L1：`{"avg_tenure_days":117}`
- L2：`{"avg_tenure_days":117}`
- L3：`{"avg_tenure_days":117}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-016_int_workday__organization_metrics/baseline.sql`；SHA-256 `651dd9e9ba55ea1b18a09bbeead3926acdecee24c64d38821298049d8ac328b5`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|117|117|否|
|L1|117|117|117|117|否|
|L2|117|117|117|117|否|
|L3|117|117|117|117|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"avg_tenure_days":117}`
- L1：`{"avg_tenure_days":117}`
- L2：`{"avg_tenure_days":117}`
- L3：`{"avg_tenure_days":117}`

#### tenure_all_assignments

判定：主因；类别候选 C。契约明确平均任期涵盖全部历史与当前 assignment，代码只取当前。

相对本轮基线减少行 117、格 117；按行优先、格次之排序。
共同控制后 SQL 第 54 行起、字符 offset 5375 的唯一连续替换；其余字节不动。
替换前：
```sql
coalesce(c.avg_tenure_days,0)::DOUBLE avg_tenure_days
```

替换后：
```sql
coalesce((SELECT avg(date_diff('day',w.effective_start,coalesce(w.effective_end,DATE '2025-10-13'))) FROM staging.stg_workday__worker_position_organization w WHERE w.organization_id=o.organization_id AND w.source_relation=o.source_relation),0)::DOUBLE avg_tenure_days
```

私有 SQL：`data/023_work/impl-016_int_workday__organization_metrics/tenure_all_assignments.sql`；SHA-256 `7256b4874528c0ac8ba557372a9425653a515db81f319b29b94a986972288753`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|117|117|0|0|是|
|L1|117|117|0|0|是|
|L2|117|117|0|0|是|
|L3|117|117|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 原始表改动核对

raw.person_contact_email_address initial/gold 7284、agent 2448。查完原始事件0–84、run.py 导入源码及013写操作清单，只有event39/40、53/54、65/66导入事件，输出均为7284；未找到削减到2448的命令或原因。不能把导入日志当作削减证据。

初始/gold 一致而 agent 有变化，依第 3 节照常标注，不标不可评估。完整表清单见 [023_raw_trace_review.json](../023_raw_trace_review.json)；输入不变性另由前后指纹验证。

## 规则问题

无
