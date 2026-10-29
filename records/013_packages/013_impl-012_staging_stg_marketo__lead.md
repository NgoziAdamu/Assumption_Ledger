# impl-012 | staging | stg_marketo__lead | 差异：S1；日期 原记录

## 契约完整原文

S3:36–81

```yaml
    - name: stg_marketo__lead
      description: "Cleaned and standardized lead (contact) records from Marketo with basic contact information and timestamps"
      source_table: "raw.marketo_lead"
      grain: "One row per unique lead in Marketo"
      columns:
        - name: lead_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: created_timestamp
          data_type: VARCHAR
          constraints: [not_null]
        - name: updated_timestamp
          data_type: VARCHAR
          constraints: [not_null]
        - name: email
          data_type: VARCHAR
          constraints: [not_null]
          description: "Email address of the lead"
          validation_rules:
            - rule: "email = LOWER(TRIM(email))"
              description: "Normalize email to lowercase and remove whitespace"
              on_failure: delete_row
            - rule: "email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'"
              description: "Email must follow valid email format"
              on_failure: delete_row
        - name: first_name
          data_type: VARCHAR
          description: "First name of the lead"
          validation_rules:
            - rule: "first_name = TRIM(first_name)"
              description: "Remove leading and trailing whitespace"
              on_failure: delete_row
            - rule: "LENGTH(first_name) <= 100"
              description: "First name cannot exceed 100 characters"
              on_failure: delete_row
        - name: last_name
          data_type: VARCHAR
          description: "Last name of the lead"
          validation_rules:
            - rule: "last_name = TRIM(last_name)"
              description: "Remove leading and trailing whitespace"
              on_failure: delete_row
            - rule: "LENGTH(last_name) <= 100"
              description: "Last name cannot exceed 100 characters"
              on_failure: delete_row

```

## agent 最终 SQL

S4

```sql
SELECT
    CAST(id AS VARCHAR) AS lead_id,
    CAST(created_at AS VARCHAR) AS created_timestamp,
    CAST(updated_at AS VARCHAR) AS updated_timestamp,
    LOWER(TRIM(email)) AS email,
    TRIM(first_name) AS first_name,
    TRIM(last_name) AS last_name
FROM raw.marketo_lead
WHERE id IS NOT NULL AND created_at IS NOT NULL AND updated_at IS NOT NULL AND email IS NOT NULL AND LOWER(TRIM(email)) ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' AND (first_name IS NULL OR (first_name = TRIM(first_name) AND LENGTH(first_name) <= 100)) AND (last_name IS NULL OR (last_name = TRIM(last_name) AND LENGTH(last_name) <= 100))
QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC NULLS LAST) = 1
```

## gold SQL（仅供定位差异）

S5

```sql
-- Staging: Lead data with standardized columns and data quality transformations
-- Transform raw Marketo data into clean staging table with standardized naming, data types, and quality constraints
SELECT
    CAST(id AS VARCHAR) as lead_id,
    CAST(created_at AS VARCHAR) as created_timestamp,
    CAST(updated_at AS VARCHAR) as updated_timestamp,
    CASE
        WHEN LOWER(TRIM(email)) !~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' THEN NULL
        WHEN email IS NULL THEN NULL
        ELSE LOWER(TRIM(email))
    END as email,
    CASE
        WHEN LENGTH(TRIM(first_name)) > 100 THEN NULL
        WHEN first_name IS NULL THEN NULL
        ELSE TRIM(first_name)
    END as first_name,
    CASE
        WHEN LENGTH(TRIM(last_name)) > 100 THEN NULL
        WHEN last_name IS NULL THEN NULL
        ELSE TRIM(last_name)
    END as last_name
FROM raw.marketo_lead
WHERE id IS NOT NULL
    AND created_at IS NOT NULL
    AND updated_at IS NOT NULL
    AND LOWER(TRIM(email)) ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    AND TRIM(email) IS NOT NULL
    AND LENGTH(TRIM(first_name)) <= 100
    AND LENGTH(TRIM(last_name)) <= 100
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5984 | 5990 | 0 | 6 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| lead_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_timestamp | 0 | 0 | 0 | VARCHAR | VARCHAR |
| updated_timestamp | 0 | 0 | 0 | VARCHAR | VARCHAR |
| email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| first_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| last_name | 0 | 0 | 0 | VARCHAR | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"lead_id":"MAR10000228817"},{"lead_id":"MAR10000346749"},{"lead_id":"MAR10001145454"},{"lead_id":"MAR10001419927"},{"lead_id":"MAR10001601917"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| B8_shared_single_source | <code>唯一源=raw.marketo_lead；目标数=2；例=["staging.stg_marketo__lead","utils.marketo__calendar_spine"]</code> |
| D10_keyword_in_any_result_field | <code>命中数=9；task_instruction_not_agent_report         description: Last name from stg_marketo__lead; may be NULL.</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 9927 | true | false |
| 9 | run | cat marketo_start.yaml | 5137 | false | false |
| 15 | run | <code>find docs -type f -maxdepth 2 -print &amp;&amp; grep -n '^    - name:' docs/data_contract.yaml</code> | 2040 | true | false |
| 23 | run | <code>cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>root=Path('sql')<br># staging: (file, raw table, projected cols, filters)<br>models={<br>'stg_marketo__lead':('marketo_lead',[('lead_id','id','VARCHAR'),('crea</code> | 3170 | false | false |
| 29 | run | <code>sed -n '3,10p' /tmp/gen.py</code> | 3760 | true | false |
| 33 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>I=Path('sql/intermediate'); M=Path('sql/marts')<br>def w(dir,n,s): (dir/f'{n}.sql').write_text(s.strip())<br>w(I,'int_marketo__lead',"""WITH deleted_lead</code> | 0 | false | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect()<br>for fmt in ['%Y-%m-%d %H:%M:%S.%f %z','%Y-%m-%d %H:%M:%S %z']:<br> print(fmt,c.execute("select try_strptime('2024-03-11 11:00:59.000 +0800', ?)",[fmt]).fe</code> | 10648 | true | false |
| 41 | run | <code>python - &lt;&lt;'PY'<br>p='sql/marts/marketo__email_templates.sql'<br>s=open(p).read()<br>s=s.replace("WITH stats AS (", "WITH template_versions AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY email_template_id ORDER</code> | 13730 | true | false |
| 43 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_marketo__email_template_history.sql';s=open(p).read();s=s.replace("CAST(operational AS BOOLEAN) AS operational,", "CAST(operational AS BOOLEAN) AS operational, (vers</code> | 2390 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('marketo.duckdb',read_only=True)<br>checks={<br>'lead staged null/duplicates':"select count(*) filter(where lead_id is null),count(*)-count(distinct lead_id) f</code> | 2154 | true | false |
| 47 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>## 已完成<br><br>已根据 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 实现 Marketo SQL 数据流水线，SQL 位于 `sql/staging/`、`sql/intermediate/</code> | 117 | false | false |
| 53 | run | <code>cat &gt; result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>## 已完成<br><br>已根据 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 实现 Marketo SQL 数据流水线，SQL 位于 `sql/staging/`、`sql/intermediate/`、`sql/marts/`，并实现依赖配置所需的 `sql/uti</code> | 1900 | true | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
'stg_marketo__lead':('marketo_lead',[('lead_id','id','VARCHAR'),('created_timestamp','created_at','VARCHAR'),('updated_timestamp','updated_at','VARCHAR'),('email','email','VARCHAR'),('first_name','first_name','VARCHAR'),('last_name','last_name','VARCHAR')]),
```
event 23 / message

```text
  if key=='stg_marketo__lead' and out=='email': expr='LOWER(TRIM(email))'
```
event 23 / message

```text
  if key=='stg_marketo__lead' and out in ('first_name','last_name'): expr=f'TRIM({src})'
```
event 23 / message

```text
 if key=='stg_marketo__lead': where="\nWHERE id IS NOT NULL AND created_at IS NOT NULL AND updated_at IS NOT NULL AND email IS NOT NULL AND LOWER(TRIM(email)) ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$' AND first_name = TRIM(first_name) AND LENGTH(first_name) <= 100 AND last_name = TRIM(last_name) AND LENGTH(last_name) <= 100\nQUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC NULLS LAST) = 1"
```
event 33 / message

```text
w(I,'int_marketo__lead',"""WITH deleted_leads AS (SELECT DISTINCT lead_id FROM staging.stg_marketo__activity_delete_lead), unique_merges AS (SELECT lead_id, STRING_AGG(DISTINCT merged_lead_ids, ', ') AS merged_into_lead_id FROM staging.stg_marketo__activity_merge_leads GROUP BY lead_id) SELECT l.lead_id,l.email,l.first_name,l.last_name,l.created_timestamp,l.updated_timestamp,(d.lead_id IS NOT NULL) AS is_deleted,m.merged_into_lead_id,(m.merged_into_lead_id IS NOT NULL) AS is_merged FROM staging.stg_marketo__lead l LEFT JOIN deleted_leads d USING (lead_id) LEFT JOIN unique_merges m USING (lead_id)""")
```
event 33 / message

```text
w(M,'marketo__leads',"""WITH merges AS (SELECT lead_id,STRING_AGG(DISTINCT merged_lead_ids, ', ') AS merged_into_lead_id FROM staging.stg_marketo__activity_merge_leads GROUP BY lead_id), deleted AS (SELECT DISTINCT lead_id FROM staging.stg_marketo__activity_delete_lead), engagement AS (SELECT lead_id,COUNT(*)::BIGINT AS count_sends,SUM(count_opens) AS count_opens,SUM(count_bounces) AS count_bounces,SUM(count_clicks) AS count_clicks,SUM(count_deliveries) AS count_deliveries,SUM(count_unsubscribes) AS count_unsubscribes,COUNT(DISTINCT email_send_id) FILTER(WHERE was_opened) AS count_unique_opens,COUNT(DISTINCT email_send_id) FILTER(WHERE was_clicked) AS count_unique_clicks FROM marts.marketo__email_sends GROUP BY lead_id) SELECT l.*,d.lead_id IS NOT NULL AS is_deleted,m.merged_into_lead_id,m.merged_into_lead_id IS NOT NULL AS is_merged,COALESCE(e.count_sends,0)::BIGINT AS count_sends,COALESCE(e.count_opens,0) AS count_opens,COALESCE(e.count_bounces,0) AS count_bounces,COALESCE(e.count_clicks,0) AS count_clicks,COALESCE(e.count_deliveries,0) AS count_deliveries,COALESCE(e.count_unsubscribes,0) AS count_unsubscribes,COALESCE(e.count_unique_opens,0)::BIGINT AS count_unique_opens,COALESCE(e.count_unique_clicks,0)::BIGINT AS count_unique_clicks FROM staging.stg_marketo__lead l LEFT JOIN deleted d USING(lead_id) LEFT JOIN merges m USING(lead_id) LEFT JOIN engagement e USING(lead_id)""")
```
event 43 / message

```text
p='sql/staging/stg_marketo__lead.sql';s=open(p).read().replace('AND first_name = TRIM(first_name) AND LENGTH(first_name) <= 100 AND last_name = TRIM(last_name) AND LENGTH(last_name) <= 100','AND (first_name IS NULL OR (first_name = TRIM(first_name) AND LENGTH(first_name) <= 100)) AND (last_name IS NULL OR (last_name = TRIM(last_name) AND LENGTH(last_name) <= 100))');open(p,'w').write(s)
```
event 45 / message

```text
'lead staged null/duplicates':"select count(*) filter(where lead_id is null),count(*)-count(distinct lead_id) from staging.stg_marketo__lead",
```
event 47 / message

```text
- `staging.stg_marketo__lead`：5,984 行；lead_id 空值 0、重复 0。
```
event 53 / message

```text
- `staging.stg_marketo__lead`：5,984 行；lead_id 空值 0、重复 0。
```

## result.md 本表名原句

S9:18

```text
- `staging.stg_marketo__lead`：5,984 行；lead_id 空值 0、重复 0。
```

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-012.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/staging/stg_marketo__lead.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/sql/staging/stg_marketo__lead.sql`
- S6: `records/006_contract_impl-012.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/result.md`
- S10: `records/012_packages/012_impl-012_staging_stg_marketo__lead.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/marketo.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions`
