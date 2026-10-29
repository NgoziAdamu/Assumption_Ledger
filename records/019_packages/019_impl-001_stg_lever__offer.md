# impl-001 | staging | stg_lever__offer | 差异：S1；日期 原记录

## 契约完整原文

S3:439–461

```yaml
    - name: stg_lever__offer
      description: "Cleaned job offers with status tracking and candidate opportunity linkage"
      source_table: "raw.offer"
      columns:
        - name: offer_id
          data_type: VARCHAR(50)
          constraints: [not_null, unique]
        - name: opportunity_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: candidate_id
          data_type: BIGINT
        - name: creator_user_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: status
          data_type: VARCHAR(50)
          validation_rules:
            - rule: "status IS NULL OR status IN ('draft', 'pending', 'sent', 'accepted', 'declined', 'rescinded')"
              on_failure: nullify_field
        - name: created_at
          data_type: TIMESTAMP

```

## agent 最终 SQL

S4

```sql
WITH typed AS (
    SELECT
        try_cast(r."id" AS VARCHAR(50)) AS offer_id,
        trim(cast(r."opportunity_id" AS VARCHAR)) AS opportunity_id,
        try_cast(r."candidate_id" AS BIGINT) AS candidate_id,
        try_cast(r."creator_id" AS VARCHAR(50)) AS creator_user_id,
        try_cast(r."status" AS VARCHAR(50)) AS status,
        try_cast(r."created_at" AS TIMESTAMP) AS created_at
    FROM raw.offer AS r
),
valid AS (
    SELECT * FROM typed
    WHERE         status IN ('open','closed','cancelled','draft','pending') AND
              offer_id IS NOT NULL AND
              opportunity_id IS NOT NULL AND
              creator_user_id IS NOT NULL
),
ranked AS (
    SELECT *, row_number() OVER (PARTITION BY offer_id ORDER BY offer_id) AS _row_num
    FROM valid
)
SELECT offer_id, opportunity_id, candidate_id, creator_user_id, status, created_at
FROM ranked
WHERE _row_num = 1
```

## gold SQL（仅供定位差异）

S5

```sql
-- Standardized cleaning of job invitation information (aligned with docs/staging_data_specification.yaml)

with cleaned as (
    select
        trim(id) as offer_id,
        opportunity_id,
        candidate_id,
        creator_id as creator_user_id,
        case when status is null or status in ('draft','pending','sent','accepted','declined','rescinded') then status else null end as status,
        try_cast(created_at as timestamp) as created_at
    from raw.offer
), filtered as (
    select * from cleaned
    where
        -- Delete row: primary key, opportunity, creator required
        length(offer_id) > 0
        and opportunity_id is not null
        and creator_user_id is not null
)

select * from filtered
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 236 | 1000 | 0 | 764 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| offer_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| opportunity_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| candidate_id | 0 | 0 | 0 | BIGINT | BIGINT |
| creator_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| status | 0 | 0 | 0 | VARCHAR | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"offer_id":"OFF10051416830"},{"offer_id":"OFF10125679178"},{"offer_id":"OFF10183738444"},{"offer_id":"OFF10256118135"},{"offer_id":"OFF10293434342"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>1列；[{"column":"created_at","table_rows":236}]</code> |
| A3_constant_nonnull_column | <code>1列；[{"column":"status","value":"pending"}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory 'lever__opportunity_enhanced':'''WITH offer_rank AS (SELECT *,row_number() OVER(PARTITION BY opportunity_id ORDER BY created_at DESC) rn FROM staging.stg_lever__offer) SELECT b.*,s.stage_name current_stage,t.tags,ar.archive_reason_title archive_reason,p.posting_title job_title,p.categories_commitment job_commitment,p.categories_location job_location,p.categories_team job_team,p.state current_state_of_job_posting,(o.offer_id IS NOT NULL) has_offer,o.status current_offer_status FROM intermediate.int_lever__opportunity_contact_info b JOIN staging.stg_lever__stage s USING(stage_id) LEFT JOIN staging.stg_lever__archive_reason ar ON b.archived_reason_id=ar.archive_reason_id LEFT JOIN intermediate.int_lever__opportunity_tags t USING(opportunity_id) LEFT JOIN offer_rank o ON b.opportunity_id=o.opportunity_id AND o.rn=1 LEFT JOIN staging.stg_lever__posting p USING(posting_id)''',</code> |

## 轨迹索引（不放输出原文）

本题事件总数：69；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find sql -maxdepth 3 -type f &#124; sort &#124; head -100 &amp;&amp; cat config/layer_dependencies.yaml</code> | 4500 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9689 | false | false |
| 11 | run | cat lever_start.yaml | 4283 | false | false |
| 17 | run | <code>cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml, pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))<br>base=pathlib.Path('sql'); rawmaps={<br>'application':{'application_id':'id','posting_hiring_manager_</code> | 0 | false | false |
| 19 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/intermediate')<br>models={<br>'int_lever__contact_info':'''WITH emails AS (SELECT contact_id, string_agg('&lt;' &#124;&#124; email &#124;&#124; '&gt;', ', ') AS emails</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/models.py &lt;&lt;'PY'<br>models={<br>'int_lever__hiring_funnel_metrics':'''WITH sm AS (SELECT stage_id, CASE WHEN lower(stage_name) LIKE '%new%' OR lower(stage_name) LIKE '%lead%' THEN 1 WHEN lower(s</code> | 0 | false | false |
| 23 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/marts')<br>models={<br>'lever__interview_enhanced':'''SELECT iu.canceled_at,iu.created_at,iu.creator_user_id,iu.interview_date,iu.duration,iu.</code> | 0 | false | false |
| 25 | run | <code>cat &gt;&gt; /tmp/marts.py &lt;&lt;'PY'<br>models={<br>'lever__candidate_quality_insights':'''WITH cb AS (SELECT ci.*,a.posting_id,a.referrer_user_id,a.type application_type,p.categories_department,p.categories_level,C</code> | 6312 | true | false |
| 27 | run | <code>grep -E 'ERROR -&#124;Executing: staging&#124;STAGING layer complete' /tmp/run.log</code> | 5620 | true | false |
| 35 | run | <code>find sql -type f &#124; sort</code> | 2341 | true | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
'lever__opportunity_enhanced':'''WITH offer_rank AS (SELECT *,row_number() OVER(PARTITION BY opportunity_id ORDER BY created_at DESC) rn FROM staging.stg_lever__offer) SELECT b.*,s.stage_name current_stage,t.tags,ar.archive_reason_title archive_reason,p.posting_title job_title,p.categories_commitment job_commitment,p.categories_location job_location,p.categories_team job_team,p.state current_state_of_job_posting,(o.offer_id IS NOT NULL) has_offer,o.status current_offer_status FROM intermediate.int_lever__opportunity_contact_info b JOIN staging.stg_lever__stage s USING(stage_id) LEFT JOIN staging.stg_lever__archive_reason ar ON b.archived_reason_id=ar.archive_reason_id LEFT JOIN intermediate.int_lever__opportunity_tags t USING(opportunity_id) LEFT JOIN offer_rank o ON b.opportunity_id=o.opportunity_id AND o.rn=1 LEFT JOIN staging.stg_lever__posting p USING(posting_id)''',
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-001.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__offer.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/staging/stg_lever__offer.sql`
- S6: `records/006_contract_impl-001.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md`
- S10: `data/019_packages_work/019_impl-001_stg_lever__offer/019_impl-001_stg_lever__offer.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/lever.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions`
