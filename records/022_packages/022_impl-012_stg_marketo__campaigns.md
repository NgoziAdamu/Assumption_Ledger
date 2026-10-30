# impl-012 | staging | stg_marketo__campaigns | 差异：S1；日期 原记录

## 契约完整原文

S3:82–209

```yaml
    - name: stg_marketo__campaigns
      description: "Cleaned campaign records with standardized attributes and campaign configuration details"
      source_table: "raw.marketo_campaign"
      grain: "One row per unique campaign in Marketo"
      columns:
        - name: campaign_id
          data_type: VARCHAR
          constraints: [not_null, unique]
          validation_rules:
            - rule: "campaign_id IS NOT NULL"
              on_failure: delete_row
        - name: campaign_name
          data_type: VARCHAR
          constraints: [not_null]
          description: "Human-readable name of the campaign"
          validation_rules:
            - rule: "campaign_name = TRIM(campaign_name)"
              description: "Clean campaign name from source"
              on_failure: correct
            - rule: "campaign_name IS NOT NULL AND TRIM(campaign_name) <> ''"
              description: "Campaign name must be present"
              on_failure: delete_row
            - rule: "LENGTH(campaign_name) <= 255"
              description: "Campaign name cannot exceed 255 characters"
              on_failure: delete_row
        - name: program_id
          data_type: VARCHAR
          description: "ID of the parent program this campaign belongs to"
          validation_rules:
            - rule: "program_id IS NULL OR program_id ~ '^MAR[0-9]+$'"
              description: "Program ID must follow Marketo format when present"
              on_failure: nullify_field
        - name: campaign_type
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "campaign_type IS NOT NULL"
              on_failure: delete_row
        - name: is_active
          data_type: BOOLEAN
          constraints: [not_null]
          description: "Whether the campaign is currently active"
          validation_rules:
            - rule: "is_active = COALESCE(is_active, FALSE)"
              description: "Default NULL active flag to FALSE"
              on_failure: correct
        - name: created_timestamp
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "created_timestamp IS NOT NULL"
              on_failure: delete_row
        - name: updated_timestamp
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "updated_timestamp IS NOT NULL"
              on_failure: delete_row
        - name: description
          data_type: VARCHAR
        - name: workspace_name
          data_type: VARCHAR
          description: "Marketo workspace where campaign resides"
        - name: computed_url
          data_type: VARCHAR
          description: "Computed URL for the campaign"
        - name: flow_id
          data_type: VARCHAR
          description: "Flow ID associated with the campaign"
        - name: folder_id
          data_type: VARCHAR
          description: "Folder ID where campaign is stored"
        - name: folder_type
          data_type: VARCHAR
          description: "Type of folder containing the campaign"
        - name: is_communication_limit_enabled
          data_type: BOOLEAN
          description: "Whether communication limits are enabled"
        - name: is_requestable
          data_type: BOOLEAN
          description: "Whether the campaign is requestable"
        - name: is_system
          data_type: BOOLEAN
          description: "Whether this is a system campaign"
        - name: max_members
          data_type: BIGINT
          description: "Maximum number of members allowed"
        - name: qualification_rule_type
          data_type: VARCHAR
          description: "Type of qualification rule"
        - name: qualification_rule_interval
          data_type: BIGINT
          description: "Qualification rule interval"
        - name: qualification_rule_unit
          data_type: VARCHAR
          description: "Unit for qualification rule interval"
        - name: recurrence_start_at
          data_type: VARCHAR
          description: "When recurrence starts (passed through as text per SQL)"
        - name: recurrence_end_at
          data_type: VARCHAR
          description: "When recurrence ends (passed through as text per SQL)"
        - name: recurrence_interval_type
          data_type: VARCHAR
          description: "Type of recurrence interval"
        - name: recurrence_interval
          data_type: BIGINT
          description: "Recurrence interval value"
        - name: recurrence_weekday_only
          data_type: BOOLEAN
          description: "Whether recurrence is weekdays only"
        - name: recurrence_day_of_month
          data_type: BIGINT
          description: "Day of month for recurrence"
        - name: recurrence_day_of_week
          data_type: BIGINT
          description: "Day of week for recurrence"
        - name: recurrence_week_of_month
          data_type: BIGINT
          description: "Week of month for recurrence"
        - name: smart_list_id
          data_type: VARCHAR
          description: "Associated smart list ID"
        - name: status
          data_type: VARCHAR
          description: "Current status of the campaign"


```

## agent 最终 SQL

S4

```sql
SELECT
    CAST(id AS VARCHAR) AS campaign_id,
    TRIM(name) AS campaign_name,
    CASE WHEN program_id IS NULL OR program_id ~ '^MAR[0-9]+$' THEN CAST(program_id AS VARCHAR) ELSE NULL END AS program_id,
    CAST(type AS VARCHAR) AS campaign_type,
    COALESCE(CAST(active AS BOOLEAN), FALSE) AS is_active,
    CAST(created_at AS VARCHAR) AS created_timestamp,
    CAST(updated_at AS VARCHAR) AS updated_timestamp,
    CAST(description AS VARCHAR) AS description,
    CAST(workspace_name AS VARCHAR) AS workspace_name,
    CAST(computed_url AS VARCHAR) AS computed_url,
    CAST(flow_id AS VARCHAR) AS flow_id,
    CAST(folder_id AS VARCHAR) AS folder_id,
    CAST(folder_type AS VARCHAR) AS folder_type,
    CAST(is_communication_limit_enabled AS BOOLEAN) AS is_communication_limit_enabled,
    CAST(is_requestable AS BOOLEAN) AS is_requestable,
    CAST(is_system AS BOOLEAN) AS is_system,
    CAST(max_members AS BIGINT) AS max_members,
    CAST(qualification_rule_type AS VARCHAR) AS qualification_rule_type,
    CAST(qualification_rule_interval AS BIGINT) AS qualification_rule_interval,
    CAST(qualification_rule_unit AS VARCHAR) AS qualification_rule_unit,
    CAST(recurrence_start_at AS VARCHAR) AS recurrence_start_at,
    CAST(recurrence_end_at AS VARCHAR) AS recurrence_end_at,
    CAST(recurrence_interval_type AS VARCHAR) AS recurrence_interval_type,
    CAST(recurrence_interval AS BIGINT) AS recurrence_interval,
    CAST(recurrence_weekday_only AS BOOLEAN) AS recurrence_weekday_only,
    CAST(recurrence_day_of_month AS BIGINT) AS recurrence_day_of_month,
    CAST(recurrence_day_of_week AS BIGINT) AS recurrence_day_of_week,
    CAST(recurrence_week_of_month AS BIGINT) AS recurrence_week_of_month,
    CAST(smart_list_id AS VARCHAR) AS smart_list_id,
    CAST(status AS VARCHAR) AS status
FROM raw.marketo_campaign
WHERE id IS NOT NULL AND name IS NOT NULL AND TRIM(name) <> '' AND LENGTH(TRIM(name)) <= 255 AND type IS NOT NULL AND created_at IS NOT NULL AND updated_at IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC NULLS LAST) = 1
```

## gold SQL（仅供定位差异）

S5

```sql
-- Staging: Campaign data with standardized columns and data quality transformations
-- Transform raw Marketo data into clean staging table with standardized naming, data types, and quality constraints
SELECT
    CAST(COALESCE(active, FALSE) AS BOOLEAN) as is_active,
    CAST(created_at AS VARCHAR) as created_timestamp,
    description,
    CAST(id AS VARCHAR) as campaign_id,
    CASE
        WHEN TRIM(name) IS NULL THEN NULL
        WHEN LENGTH(TRIM(name)) > 255 THEN NULL
        ELSE TRIM(name)
    END as campaign_name,
    CASE
        WHEN program_id IS NULL THEN NULL
        WHEN program_id !~ '^MAR[0-9]+$' THEN NULL
        ELSE CAST(program_id AS VARCHAR)
    END as program_id,
    CAST(type AS VARCHAR) as campaign_type,
    CAST(updated_at AS VARCHAR) as updated_timestamp,
    CAST(workspace_name AS VARCHAR) as workspace_name,
    CAST(computed_url AS VARCHAR) as computed_url,
    CAST(flow_id AS VARCHAR) as flow_id,
    CAST(folder_id AS VARCHAR) as folder_id,
    CAST(folder_type AS VARCHAR) as folder_type,
    CAST(is_communication_limit_enabled AS BOOLEAN) as is_communication_limit_enabled,
    CAST(is_requestable AS BOOLEAN) as is_requestable,
    CAST(is_system AS BOOLEAN) as is_system,
    CAST(max_members AS BIGINT) as max_members,
    CAST(qualification_rule_type AS VARCHAR) as qualification_rule_type,
    CAST(qualification_rule_interval AS BIGINT) as qualification_rule_interval,
    CAST(qualification_rule_unit AS VARCHAR) as qualification_rule_unit,
    CAST(recurrence_start_at AS VARCHAR) as recurrence_start_at,
    CAST(recurrence_end_at AS VARCHAR) as recurrence_end_at,
    CAST(recurrence_interval_type AS VARCHAR) as recurrence_interval_type,
    CAST(recurrence_interval AS BIGINT) as recurrence_interval,
    CAST(recurrence_weekday_only AS BOOLEAN) as recurrence_weekday_only,
    CAST(recurrence_day_of_month AS BIGINT) as recurrence_day_of_month,
    CAST(recurrence_day_of_week AS BIGINT) as recurrence_day_of_week,
    CAST(recurrence_week_of_month AS BIGINT) as recurrence_week_of_month,
    CAST(smart_list_id AS VARCHAR) as smart_list_id,
    CAST(status AS VARCHAR) as status
FROM raw.marketo_campaign
WHERE id IS NOT NULL
    AND TRIM(name) IS NOT NULL
    AND type IS NOT NULL
    AND created_at IS NOT NULL
    AND updated_at IS NOT NULL
    AND LENGTH(TRIM(name)) <= 255
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 4996 | 4997 | 0 | 1 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| is_active | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| created_timestamp | 0 | 0 | 0 | VARCHAR | VARCHAR |
| description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| program_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| updated_timestamp | 0 | 0 | 0 | VARCHAR | VARCHAR |
| workspace_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| computed_url | 0 | 0 | 0 | VARCHAR | VARCHAR |
| flow_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| folder_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| folder_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_communication_limit_enabled | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_requestable | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_system | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| max_members | 0 | 0 | 0 | BIGINT | BIGINT |
| qualification_rule_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| qualification_rule_unit | 0 | 0 | 0 | VARCHAR | VARCHAR |
| recurrence_start_at | 0 | 0 | 0 | VARCHAR | VARCHAR |
| recurrence_end_at | 0 | 0 | 0 | VARCHAR | VARCHAR |
| recurrence_interval_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| recurrence_weekday_only | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| recurrence_day_of_month | 0 | 0 | 0 | BIGINT | BIGINT |
| recurrence_day_of_week | 0 | 0 | 0 | BIGINT | BIGINT |
| recurrence_week_of_month | 0 | 0 | 0 | BIGINT | BIGINT |
| smart_list_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| status | 0 | 0 | 0 | VARCHAR | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"campaign_id":"MAR10014460609"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| D10_keyword_in_any_result_field | <code>命中数=3；task_instruction_not_agent_report  - Left join campaigns (staging.stg_marketo__campaigns) on campaign_id to add campaign_type and program_id; if no match, these remain null.</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions/f972c6ee-d3e4-46-3f01a7d60602dbd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 9927 | true | false |
| 9 | run | cat marketo_start.yaml | 5137 | false | false |
| 13 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('marketo_start.duckdb',read_only=True)<br>for t in ['marketo_activity_send_email','marketo_activity_open_email','marketo_activity_click_email','marketo_acti</code> | 11983 | false | false |
| 15 | run | <code>find docs -type f -maxdepth 2 -print &amp;&amp; grep -n '^    - name:' docs/data_contract.yaml</code> | 2040 | true | false |
| 23 | run | <code>cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>root=Path('sql')<br># staging: (file, raw table, projected cols, filters)<br>models={<br>'stg_marketo__lead':('marketo_lead',[('lead_id','id','VARCHAR'),('crea</code> | 3170 | true | false |
| 25 | run | <code>sed -i "s/('status','status','VARCHAR')]),'campaign')/('status','status','VARCHAR')]),/" /tmp/gen.py; python /tmp/gen.py</code> | 3159 | true | false |
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
'stg_marketo__campaigns':('marketo_campaign',[(a,b,t) for a,b,t in [('campaign_id','id','VARCHAR'),('campaign_name','name','VARCHAR'),('program_id','program_id','VARCHAR'),('campaign_type','type','VARCHAR'),('is_active','active','BOOLEAN'),('created_timestamp','created_at','VARCHAR'),('updated_timestamp','updated_at','VARCHAR'),('description','description','VARCHAR'),('workspace_name','workspace_name','VARCHAR'),('computed_url','computed_url','VARCHAR'),('flow_id','flow_id','VARCHAR'),('folder_id','folder_id','VARCHAR'),('folder_type','folder_type','VARCHAR'),('is_communication_limit_enabled','is_communication_limit_enabled','BOOLEAN'),('is_requestable','is_requestable','BOOLEAN'),('is_system','is_system','BOOLEAN'),('max_members','max_members','BIGINT'),('qualification_rule_type','qualification_rule_type','VARCHAR'),('qualification_rule_interval','qualification_rule_interval','BIGINT'),('qualification_rule_unit','qualification_rule_unit','VARCHAR'),('recurrence_start_at','recurrence_start_at','VARCHAR'),('recurrence_end_at','recurrence_end_at','VARCHAR'),('recurrence_interval_type','recurrence_interval_type','VARCHAR'),('recurrence_interval','recurrence_interval','BIGINT'),('recurrence_weekday_only','recurrence_weekday_only','BOOLEAN'),('recurrence_day_of_month','recurrence_day_of_month','BIGINT'),('recurrence_day_of_week','recurrence_day_of_week','BIGINT'),('recurrence_week_of_month','recurrence_week_of_month','BIGINT'),('smart_list_id','smart_list_id','VARCHAR'),('status','status','VARCHAR')]),'campaign'),
```
event 23 / message

```text
  if key=='stg_marketo__campaigns' and out=='campaign_name': expr='TRIM(name)'
```
event 23 / message

```text
 if key=='stg_marketo__campaigns': where="\nWHERE id IS NOT NULL AND name IS NOT NULL AND TRIM(name) <> '' AND LENGTH(TRIM(name)) <= 255 AND type IS NOT NULL AND created_at IS NOT NULL AND updated_at IS NOT NULL\nQUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC NULLS LAST) = 1"
```
event 33 / message

```text
w(M,'marketo__email_sends',"""WITH base AS (SELECT * FROM intermediate.marketo__email_sends_deduped), joined AS (SELECT b.*,COALESCE(o.count_opens,0)::BIGINT AS count_opens,COALESCE(bo.count_bounces,0)::BIGINT AS count_bounces,COALESCE(c.count_clicks,0)::BIGINT AS count_clicks,COALESCE(d.count_deliveries,0)::BIGINT AS count_deliveries,COALESCE(u.count_unsubscribes,0)::BIGINT AS count_unsubscribes FROM base b LEFT JOIN intermediate.marketo__opens__by_sent_email o USING(email_send_id) LEFT JOIN intermediate.marketo__bounces__by_sent_email bo USING(email_send_id) LEFT JOIN intermediate.marketo__clicks__by_sent_email c USING(email_send_id) LEFT JOIN intermediate.marketo__deliveries__by_sent_email d USING(email_send_id) LEFT JOIN intermediate.marketo__unsubscribes__by_sent_email u USING(email_send_id)) SELECT j.*,count_opens>0 AS was_opened,count_bounces>0 AS was_bounced,count_clicks>0 AS was_clicked,count_deliveries>0 AS was_delivered,count_unsubscribes>0 AS was_unsubscribed,c.campaign_type,c.program_id,t.operational AS is_operational FROM joined j LEFT JOIN staging.stg_marketo__campaigns c USING(campaign_id) LEFT JOIN staging.stg_marketo__email_template_history t USING(email_template_id)""")
```
event 33 / message

```text
w(M,'marketo__campaigns',f"""WITH stats AS ({stats} GROUP BY campaign_id) SELECT c.*,COALESCE(s.count_sends,0)::BIGINT AS count_sends,COALESCE(s.count_opens,0) AS count_opens,COALESCE(s.count_bounces,0) AS count_bounces,COALESCE(s.count_clicks,0) AS count_clicks,COALESCE(s.count_deliveries,0) AS count_deliveries,COALESCE(s.count_unsubscribes,0) AS count_unsubscribes,COALESCE(s.count_unique_opens,0)::BIGINT AS count_unique_opens,COALESCE(s.count_unique_clicks,0)::BIGINT AS count_unique_clicks FROM staging.stg_marketo__campaigns c LEFT JOIN stats s USING(campaign_id)""")
```
event 43 / message

```text
p='sql/staging/stg_marketo__campaigns.sql';s=open(p).read().replace('CAST(program_id AS VARCHAR) AS program_id','CASE WHEN program_id IS NULL OR program_id ~ \'^MAR[0-9]+$\' THEN CAST(program_id AS VARCHAR) ELSE NULL END AS program_id').replace('CAST(active AS BOOLEAN) AS is_active','COALESCE(CAST(active AS BOOLEAN), FALSE) AS is_active');open(p,'w').write(s)
```
event 45 / message

```text
'campaign staging duplicate IDs':"select count(*)-count(distinct campaign_id) from staging.stg_marketo__campaigns",
```
event 47 / message

```text
- `staging.stg_marketo__campaigns`：campaign_id 重复 0。
```
event 53 / message

```text
- `staging.stg_marketo__campaigns`：campaign_id 重复 0。
```

## result.md 本表名原句

S9:20

```text
- `staging.stg_marketo__campaigns`：campaign_id 重复 0。
```

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-012.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/staging/stg_marketo__campaigns.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/sql/staging/stg_marketo__campaigns.sql`
- S6: `records/006_contract_impl-012.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/result.md`
- S10: `data/022_packages_work/022_impl-012_stg_marketo__campaigns/022_impl-012_stg_marketo__campaigns.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/marketo.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions`
