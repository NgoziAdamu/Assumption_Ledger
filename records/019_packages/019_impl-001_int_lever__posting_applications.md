# impl-001 | intermediate | int_lever__posting_applications | 差异：S1；日期 原记录

## 契约完整原文

S3:1655–1688

```yaml
    - name: int_lever__posting_applications
      description: Aggregates application metrics per posting and selects the latest hiring manager user ID by created_at.
      grain: One row per non-null posting_id with applications in staging.stg_lever__application
      source_models:
      - staging.stg_lever__application
      business_logic: '- Read all application rows from staging.stg_lever__application. - Aggregate per posting_id: - first_app_sent_at: the earliest non-null created_at; if all created_at values are NULL, this is NULL. - count_referred_applications: number of rows where type equals ''referral''; exact match, NULL or other values do not count. - count_posting_applications: number of rows where type equals ''posting'' or ''agency''; exact matches only. - count_manual_user_applications: number of rows where type equals ''user''; exact match. - count_opportunities: number of distinct non-null opportunity_id. - count_open_opportunities: number of distinct non-null opportunity_id where archived_at is NULL. - Determine posting_hiring_manager_user_id by selecting, for each posting_id, the application with the latest created_at; if multiple rows share the same created_at or created_at is NULL, tie-breaking and NULL ordering follow the engine defaults; take that row''s posting_hiring_manager_user_id (may be NULL). - Inner join the aggregates with the latest-application selection on posting_id; posting_id values that are NULL do not match and are excluded, and only posting_ids with at least one application appear. - Output one row per non-null posting_id present in the application data.'
      columns:
      - name: posting_id
        data_type: VARCHAR
        description: Grouping key; one row per non-null posting_id with applications
        tests:
        - not_null
        - unique
      - name: first_app_sent_at
        data_type: TIMESTAMP
        description: Earliest application created_at timestamp for the posting_id; NULL if all created_at are NULL
      - name: count_referred_applications
        data_type: HUGEINT
        description: Number of application rows with type exactly 'referral' for the posting_id
      - name: count_posting_applications
        data_type: HUGEINT
        description: Number of application rows with type 'posting' or 'agency' for the posting_id
      - name: count_manual_user_applications
        data_type: HUGEINT
        description: Number of application rows with type exactly 'user' for the posting_id
      - name: count_opportunities
        data_type: BIGINT
        description: Distinct count of non-null opportunity_id for the posting_id
      - name: count_open_opportunities
        data_type: BIGINT
        description: Distinct count of non-null opportunity_id with archived_at NULL for the posting_id
      - name: posting_hiring_manager_user_id
        data_type: VARCHAR
        description: User ID from the application with the latest created_at for the posting_id; ties are resolved arbitrarily
```

## agent 最终 SQL

S4

```sql
WITH agg AS (SELECT posting_id, min(created_at) AS first_app_sent_at, count(*) FILTER (WHERE type='referral') AS count_referred_applications, count(*) FILTER (WHERE type IN ('posting','agency')) AS count_posting_applications, count(*) FILTER (WHERE type='user') AS count_manual_user_applications, count(DISTINCT opportunity_id) AS count_opportunities, count(DISTINCT opportunity_id) FILTER (WHERE archived_at IS NULL) AS count_open_opportunities FROM staging.stg_lever__application WHERE posting_id IS NOT NULL GROUP BY posting_id), latest AS (SELECT posting_id, posting_hiring_manager_user_id, row_number() OVER(PARTITION BY posting_id ORDER BY created_at DESC) rn FROM staging.stg_lever__application WHERE posting_id IS NOT NULL) SELECT a.*, l.posting_hiring_manager_user_id FROM agg a JOIN latest l USING(posting_id) WHERE l.rn=1
```

## gold SQL（仅供定位差异）

S5

```sql
-- Job application aggregation intermediate table
-- Aggregate application data by position

with application as (
    select *
    from staging.stg_lever__application
),

agg_applications as (
    select 
        posting_id,
        min(created_at) as first_app_sent_at,

        -- Statistics for different types of applications
        sum(case when type = 'referral' then 1 else 0 end) as count_referred_applications,
        sum(case when type = 'posting' or type = 'agency' then 1 else 0 end) as count_posting_applications,
        sum(case when type = 'user' then 1 else 0 end) as count_manual_user_applications,

        count(distinct opportunity_id) as count_opportunities,
        count(distinct case when archived_at is null then opportunity_id end) as count_open_opportunities

    from application
    group by 1
),

order_hiring_managers as (
    select 
        posting_id,
        posting_hiring_manager_user_id,
        row_number() over(
            partition by posting_id 
            order by created_at desc) as row_num 
    from application
),

last_hiring_manager as (
    select *
    from order_hiring_managers 
    where row_num = 1
),

final as (
    select 
        agg_applications.*,
        last_hiring_manager.posting_hiring_manager_user_id

    from agg_applications
    join last_hiring_manager
        on agg_applications.posting_id = last_hiring_manager.posting_id
)

select * from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 300 | 300 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"posting_id":"pos10770075995"}</code> |
| K2 | <code>{"posting_id":"pos10779355497"}</code> |
| K3 | <code>{"posting_id":"pos10866306655"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| posting_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| count_referred_applications | 0 | 0 | 0 | BIGINT | HUGEINT |
| count_posting_applications | 0 | 0 | 0 | BIGINT | HUGEINT |
| count_manual_user_applications | 0 | 0 | 0 | BIGINT | HUGEINT |
| count_opportunities | 0 | 0 | 0 | BIGINT | BIGINT |
| count_open_opportunities | 0 | 0 | 0 | BIGINT | BIGINT |
| posting_hiring_manager_user_id | 299 | 299 | 299 | VARCHAR | VARCHAR |

posting_hiring_manager_user_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | USE19573232084 | USE66639416446 |
| K2 | USE87643933730 | USE78005193962 |
| K3 | USE15835459736 | USE26269852265 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A1_zero_rows | 行数=0 |
| B8_shared_single_source | <code>唯一源=staging.stg_lever__application；目标数=3；例=["intermediate.int_lever__posting_applications","marts.lever__hiring_dashboard_simple","marts.lever__recruitment_analytics_dashboard"]</code> |
| D10_keyword_in_any_result_field | <code>命中数=3；task_instruction_not_agent_report  - Left join intermediate.int_lever__posting_applications on posting_id to add: - first_app_sent_at (NULL when no applications).</code> |

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
| 27 | run | <code>grep -E 'ERROR -&#124;Executing: staging&#124;STAGING layer complete' /tmp/run.log</code> | 5620 | false | false |
| 35 | run | <code>find sql -type f &#124; sort</code> | 2341 | true | false |
| 37 | run | <code>sed -i "s/) external FROM cb/) external_avg FROM cb/; s/referred&gt;external+10/referred&gt;external_avg+10/; s/internal&gt;external+10/internal&gt;external_avg+10/" sql/marts/lever__candidate_quality_insights.sq</code> | 2929 | false | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
'int_lever__posting_applications':'''WITH agg AS (SELECT posting_id, min(created_at) AS first_app_sent_at, count(*) FILTER (WHERE type='referral') AS count_referred_applications, count(*) FILTER (WHERE type IN ('posting','agency')) AS count_posting_applications, count(*) FILTER (WHERE type='user') AS count_manual_user_applications, count(DISTINCT opportunity_id) AS count_opportunities, count(DISTINCT opportunity_id) FILTER (WHERE archived_at IS NULL) AS count_open_opportunities FROM staging.stg_lever__application WHERE posting_id IS NOT NULL GROUP BY posting_id), latest AS (SELECT posting_id, posting_hiring_manager_user_id, row_number() OVER(PARTITION BY posting_id ORDER BY created_at DESC) rn FROM staging.stg_lever__application WHERE posting_id IS NOT NULL) SELECT a.*, l.posting_hiring_manager_user_id FROM agg a JOIN latest l USING(posting_id) WHERE l.rn=1''',
```
event 23 / message

```text
'lever__posting_enhanced':'''WITH req AS (SELECT posting_id,count(*) count_requisitions FROM staging.stg_lever__requisition_posting GROUP BY posting_id) SELECT p.*,coalesce(r.count_requisitions,0) count_requisitions,coalesce(r.count_requisitions,0)>0 has_requisition,coalesce(a.first_app_sent_at,a.first_app_sent_at) first_app_sent_at,coalesce(a.count_referred_applications,0) count_referred_applications,coalesce(a.count_posting_applications,0) count_posting_applications,coalesce(a.count_manual_user_applications,0) count_manual_user_applications,coalesce(a.count_opportunities,0) count_opportunities,coalesce(a.count_open_opportunities,0) count_open_opportunities,coalesce(i.count_interviews,0) count_interviews,coalesce(i.count_interview_coordinators,0) count_interviewees,t.tags,u.user_name posting_hiring_manager_name FROM staging.stg_lever__posting p LEFT JOIN req r USING(posting_id) LEFT JOIN intermediate.int_lever__posting_applications a USING(posting_id) LEFT JOIN intermediate.int_lever__posting_interviews i USING(posting_id) LEFT JOIN intermediate.int_lever__posting_tags t USING(posting_id) LEFT JOIN staging.stg_lever__user u ON a.posting_hiring_manager_user_id=u.user_id''',
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-001.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_applications.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/intermediate/int_lever__posting_applications.sql`
- S6: `records/006_contract_impl-001.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md`
- S10: `data/019_packages_work/019_impl-001_int_lever__posting_applications/019_impl-001_int_lever__posting_applications.json`
- S11: `data/005_cs_work/impl-001/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions`
