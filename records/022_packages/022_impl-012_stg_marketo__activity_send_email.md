# impl-012 | staging | stg_marketo__activity_send_email | 差异：S1；日期 原记录

## 契约完整原文

S3:316–345

```yaml
    - name: stg_marketo__activity_send_email
      description: "Cleaned email send activity records showing when emails were sent to leads"
      source_table: "raw.marketo_activity_send_email"
      grain: "One row per email send event"
      columns:
        - name: activity_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: lead_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: campaign_id
          data_type: VARCHAR
        - name: email_template_id
          data_type: VARCHAR
        - name: activity_timestamp
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: activity_type_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: campaign_run_id
          data_type: VARCHAR
        - name: primary_attribute_value
          data_type: VARCHAR
        - name: primary_attribute_value_id
          data_type: VARCHAR
        - name: email_send_id
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
SELECT
    CAST(id AS VARCHAR) AS activity_id,
    CAST(lead_id AS VARCHAR) AS lead_id,
    CAST(campaign_id AS VARCHAR) AS campaign_id,
    CAST(email_template_id AS VARCHAR) AS email_template_id,
    TRY_STRPTIME(activity_date, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP AS activity_timestamp,
    CAST(activity_type_id AS VARCHAR) AS activity_type_id,
    CAST(campaign_run_id AS VARCHAR) AS campaign_run_id,
    CAST(primary_attribute_value AS VARCHAR) AS primary_attribute_value,
    CAST(primary_attribute_value_id AS VARCHAR) AS primary_attribute_value_id,
    CAST(id AS VARCHAR) AS email_send_id
FROM raw.marketo_activity_send_email
WHERE id IS NOT NULL AND lead_id IS NOT NULL AND activity_date IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY id ORDER BY activity_date) = 1
```

## gold SQL（仅供定位差异）

S5

```sql
-- Staging: Email send activity with surrogate key and data quality transformations
-- Transform raw Marketo data into clean staging table with standardized naming, data types, and quality constraints
-- Note: Converting timezone-aware timestamps to TIMESTAMP by removing timezone info and using UTC
SELECT
    CAST(SUBSTRING(activity_date, 1, LENGTH(activity_date) - 6) AS TIMESTAMP) as activity_timestamp,
    CAST(activity_type_id AS VARCHAR) as activity_type_id,
    CAST(campaign_id AS VARCHAR) as campaign_id,
    CAST(campaign_run_id AS VARCHAR) as campaign_run_id,
    CAST(email_template_id AS VARCHAR) as email_template_id,
    CAST(id AS VARCHAR) as activity_id,
    CAST(lead_id AS VARCHAR) as lead_id,
    CAST(primary_attribute_value AS VARCHAR) as primary_attribute_value,
    CAST(primary_attribute_value_id AS VARCHAR) as primary_attribute_value_id,
    MD5(CONCAT(COALESCE(CAST(primary_attribute_value_id AS VARCHAR), ''),
               COALESCE(CAST(campaign_id AS VARCHAR), ''),
               COALESCE(CAST(campaign_run_id AS VARCHAR), ''),
               COALESCE(CAST(lead_id AS VARCHAR), ''))) as email_send_id
FROM raw.marketo_activity_send_email
WHERE id IS NOT NULL
    AND activity_type_id IS NOT NULL
    AND lead_id IS NOT NULL
    AND activity_date IS NOT NULL
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 15000 | 15000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"activity_id":"mar10022044711"}</code> |
| K2 | <code>{"activity_id":"mar10022047844"}</code> |
| K3 | <code>{"activity_id":"mar10022050465"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| activity_type_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_run_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| email_template_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| activity_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| lead_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| primary_attribute_value | 0 | 0 | 0 | VARCHAR | VARCHAR |
| primary_attribute_value_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| email_send_id | 15000 | 15000 | 15000 | VARCHAR | VARCHAR |

email_send_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | MAR10022044711 | abfa625b1a81c8956f1f48fa94b6cfbe |
| K2 | MAR10022047844 | 6738d103ed0d3711e941d314e8bc92c8 |
| K3 | MAR10022050465 | b1359ab2d27ec20a722f239a7852ba7f |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A4_equal_columns | <code>1组；[{"columns":["activity_id","email_send_id"],"nonnull_equal_rows":15000,"meaning_status":"契约未描述含义差别"}]</code> |

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
| 17 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('marketo_start.duckdb',read_only=True)<br>for col in ['primary_attribute_value_id','primary_attribute_value','campaign_run_id','id']:<br> print(col)<br> for t in </code> | 807 | false | false |
| 19 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts sql/utils &amp;&amp; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('marketo_start.duckdb',read_only=True)<br>for q in ["select try_cast(activity_date as timestamp</code> | 39 | false | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('marketo_start.duckdb',read_only=True)<br>for col in ['campaign_run_id','campaign_id','email_template_id','primary_attribute_value_id','primary_attribute_va</code> | 538 | false | false |
| 33 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>I=Path('sql/intermediate'); M=Path('sql/marts')<br>def w(dir,n,s): (dir/f'{n}.sql').write_text(s.strip())<br>w(I,'int_marketo__lead',"""WITH deleted_lead</code> | 0 | false | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect()<br>for fmt in ['%Y-%m-%d %H:%M:%S.%f %z','%Y-%m-%d %H:%M:%S %z']:<br> print(fmt,c.execute("select try_strptime('2024-03-11 11:00:59.000 +0800', ?)",[fmt]).fe</code> | 10648 | true | false |
| 41 | run | <code>python - &lt;&lt;'PY'<br>p='sql/marts/marketo__email_templates.sql'<br>s=open(p).read()<br>s=s.replace("WITH stats AS (", "WITH template_versions AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY email_template_id ORDER</code> | 13730 | true | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('marketo.duckdb',read_only=True)<br>checks={<br>'lead staged null/duplicates':"select count(*) filter(where lead_id is null),count(*)-count(distinct lead_id) f</code> | 2154 | true | false |

### agent action 的 thought/message 命中原句

event 33 / message

```text
w(I,'marketo__email_sends_deduped',"""WITH ranked_sends AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY email_send_id ORDER BY activity_timestamp ASC) AS activity_rank FROM staging.stg_marketo__activity_send_email) SELECT activity_timestamp,activity_type_id,campaign_id,campaign_run_id,email_template_id,activity_id,lead_id,primary_attribute_value,primary_attribute_value_id,email_send_id,activity_rank FROM ranked_sends WHERE activity_rank = 1""")
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-012.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-012/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/sql/staging/stg_marketo__activity_send_email.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/sql/staging/stg_marketo__activity_send_email.sql`
- S6: `records/006_contract_impl-012.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/result.md`
- S10: `data/022_packages_work/022_impl-012_stg_marketo__activity_send_email/022_impl-012_stg_marketo__activity_send_email.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-012/agent/dacomp-de-impl-012/marketo.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-012/marketo.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-012/agent/.events/sessions`
