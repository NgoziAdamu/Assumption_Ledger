# impl-002 | staging | stg_pendo__poll_event | 差异：S1；日期 原记录

## 契约完整原文

S3:461–521

```yaml
    - name: stg_pendo__poll_event
      description: "Cleaned poll interaction events with validated responses"
      source_table: "raw.poll_event"
      columns:
        - name: account_id
          data_type: BIGINT
          constraints: [not_null]
        - name: guide_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: poll_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: remote_ip
          data_type: VARCHAR(255)
          validation_rules:
            - rule: "remote_ip IS NULL OR remote_ip ~ '^([0-9]{1,3}){3}[0-9]{1,3}$' OR remote_ip ~ '^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'"
              on_failure: nullify_field
        - name: server_name
          data_type: VARCHAR(255)
        - name: occurred_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: user_agent
          data_type: VARCHAR(255)
        - name: visitor_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: app_id
          data_type: BIGINT
          constraints: [not_null]
        - name: poll_response
          data_type: VARCHAR(255)
        - name: country
          data_type: VARCHAR(255)
        - name: guide_step_id
          data_type: BIGINT
        - name: latitude
          data_type: DOUBLE
          validation_rules:
            - rule: "latitude BETWEEN -90 AND 90 OR latitude IS NULL"
              on_failure: nullify_field
        - name: longitude
          data_type: DOUBLE
          validation_rules:
            - rule: "longitude BETWEEN -180 AND 180 OR longitude IS NULL"
              on_failure: nullify_field
        - name: region
          data_type: VARCHAR(255)
        - name: type
          data_type: VARCHAR(255)
        - name: url
          data_type: VARCHAR(255)
          validation_rules:
            - rule: "url = NULLIF(TRIM(url), '')"
              on_failure: correct
            - rule: "url IS NULL OR url ~ '^https?://'"
              on_failure: nullify_field
        - name: poll_event_key
          data_type: VARCHAR(255)

```

## agent 最终 SQL

S4

```sql
SELECT
    TRY_CAST(account_id AS BIGINT) AS account_id,
    CAST(guide_id AS VARCHAR) AS guide_id,
    CAST(poll_id AS VARCHAR) AS poll_id,
    CASE WHEN remote_ip IS NULL OR regexp_matches(CAST(remote_ip AS VARCHAR), '^([0-9]{1,3}\.){3}[0-9]{1,3}$') OR regexp_matches(CAST(remote_ip AS VARCHAR), '^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$') THEN CAST(remote_ip AS VARCHAR) ELSE NULL END AS remote_ip,
    NULLIF(TRIM(CAST(server_name AS VARCHAR)), '') AS server_name,
    TRY_CAST(SUBSTRING(CAST(timestamp AS VARCHAR), 1, 23) AS TIMESTAMP) AS occurred_at,
    NULLIF(TRIM(CAST(user_agent AS VARCHAR)), '') AS user_agent,
    CAST(visitor_id AS VARCHAR) AS visitor_id,
    TRY_CAST(app_id AS BIGINT) AS app_id,
    CAST(poll_response AS VARCHAR) AS poll_response,
    CAST(country AS VARCHAR) AS country,
    TRY_CAST(guide_step_id AS BIGINT) AS guide_step_id,
    CASE WHEN TRY_CAST(latitude AS DOUBLE) BETWEEN -90 AND 90 THEN TRY_CAST(latitude AS DOUBLE) ELSE NULL END AS latitude,
    CASE WHEN TRY_CAST(longitude AS DOUBLE) BETWEEN -180 AND 180 THEN TRY_CAST(longitude AS DOUBLE) ELSE NULL END AS longitude,
    CAST(region AS VARCHAR) AS region,
    CAST(type AS VARCHAR) AS type,
    CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS VARCHAR)), '') END AS url,
    md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(poll_id AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), ''))) AS poll_event_key
FROM raw.poll_event
```

## gold SQL（仅供定位差异）

S5

```sql
-- Staging model for poll_event
-- Converted from DBT to DuckDB-compatible SQL
-- Implements data quality checks per staging_data_specification.yaml

SELECT
    -- Account ID with proper data type and validation
    CAST(account_id AS VARCHAR(50)) as account_id,

    -- Guide ID with proper data type and validation
    CAST(guide_id AS VARCHAR(50)) as guide_id,

    -- Poll ID with proper data type and validation
    CAST(poll_id AS VARCHAR(50)) as poll_id,

    -- Remote IP with validation pattern
    CASE
        WHEN remote_ip IS NULL THEN NULL
        WHEN remote_ip ~ '^([0-9]{1,3}\.){3}[0-9]{1,3}$' OR remote_ip ~ '^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$' THEN CAST(remote_ip AS VARCHAR(255))
        ELSE NULL
    END as remote_ip,

    -- Server name with proper data type
    CAST(server_name AS VARCHAR(255)) as server_name,

    -- Occurred at with timestamp casting and not null constraint
    TRY_CAST(SUBSTRING(timestamp, 1, 23) AS TIMESTAMP) as occurred_at,

    -- User agent with proper data type
    CAST(user_agent AS VARCHAR(255)) as user_agent,

    -- Visitor ID with proper data type and validation
    CAST(visitor_id AS VARCHAR(50)) as visitor_id,

    -- App ID with proper data type and validation
    CAST(app_id AS BIGINT) as app_id,

    -- Poll response with proper data type
    CAST(poll_response AS VARCHAR(255)) as poll_response,

    -- Geographic data
    CAST(country AS VARCHAR(255)) as country,
    CAST(region AS VARCHAR(255)) as region,
    CAST(guide_step_id AS BIGINT) as guide_step_id,

    -- Latitude with range validation
    CASE
        WHEN latitude BETWEEN -90 AND 90 THEN CAST(latitude AS DOUBLE)
        ELSE NULL
    END as latitude,

    -- Longitude with range validation
    CASE
        WHEN longitude BETWEEN -180 AND 180 THEN CAST(longitude AS DOUBLE)
        ELSE NULL
    END as longitude,

    -- URL with validation and correction rules
    CASE
        WHEN TRIM(url) = '' THEN NULL
        WHEN url IS NOT NULL AND url ~ '^https?://' THEN TRIM(url)
        ELSE NULL
    END as url,

    -- Poll event key with proper data type
    -- Note: Account ID constraint requires unique account_id per poll_event, which is unusual
    -- We'll create the key but not enforce uniqueness in the query
    MD5(CONCAT(
        COALESCE(CAST(visitor_id AS VARCHAR), ''),
        COALESCE(CAST(timestamp AS VARCHAR), ''),
        COALESCE(CAST(account_id AS VARCHAR), ''),
        COALESCE(server_name, ''),
        COALESCE(CAST(poll_id AS VARCHAR), ''),
        COALESCE(CAST(guide_id AS VARCHAR), ''),
        COALESCE(user_agent, ''),
        COALESCE(remote_ip, '')
    )) as poll_event_key

FROM raw.poll_event
WHERE
    -- Filter records with severe data quality issues
    account_id IS NOT NULL
    AND guide_id IS NOT NULL
    AND guide_id != ''
    AND poll_id IS NOT NULL
    AND poll_id != ''
    AND timestamp IS NOT NULL
    AND visitor_id IS NOT NULL
    AND visitor_id != ''
    AND app_id IS NOT NULL
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5000 | 5000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"account_id":"100036762","guide_id":"2a09075c-fea6-42a1-a92e-fde","poll_id":"pol10000000045","visitor_id":"else_fish","app_id":"239587236"}</code> |
| K2 | <code>{"account_id":"100138737","guide_id":"c903c56a-e9a9-4404-bea1-e81","poll_id":"pol10000000010","visitor_id":"race_this","app_id":"239587236"}</code> |
| K3 | <code>{"account_id":"100150252","guide_id":"99629444-3be4-4d47-9764-5c8","poll_id":"pol10000000022","visitor_id":"fast_present","app_id":"239587236"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | BIGINT | VARCHAR |
| guide_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| poll_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| remote_ip | 0 | 0 | 0 | VARCHAR | VARCHAR |
| server_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| user_agent | 0 | 0 | 0 | VARCHAR | VARCHAR |
| visitor_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| app_id | 0 | 0 | 0 | BIGINT | BIGINT |
| poll_response | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| region | 0 | 0 | 0 | VARCHAR | VARCHAR |
| guide_step_id | 0 | 0 | 0 | BIGINT | BIGINT |
| latitude | 0 | 0 | 0 | DOUBLE | DOUBLE |
| longitude | 0 | 0 | 0 | DOUBLE | DOUBLE |
| url | 5000 | 5000 | 5000 | VARCHAR | VARCHAR |
| poll_event_key | 5000 | 5000 | 5000 | VARCHAR | VARCHAR |

url 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | http://www.sullivan.biz/ | null |
| K2 | http://www.clayton-butler.com/ | null |
| K3 | http://www.lang.org/ | null |

poll_event_key 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 16505a9ae98104e041eb2cda4a6e80dd | 249d30b9bc5a002fbf92afa9eb4b253b |
| K2 | 535987f69d0181ca50dc8a8a969f087c | fc875ae2fdbb145406b22e57169245e6 |
| K3 | b923985bf409f2549aaefabaecef7ccb | 03f1b9651a1cbcaafe80c2db5664a578 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>1列；[{"column":"remote_ip","table_rows":5000}]</code> |
| A3_constant_nonnull_column | <code>1列；[{"column":"app_id","value":"239587236"}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：61；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 9 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 14079 | true | false |
| 13 | run | <code>find sql -maxdepth 3 -print; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('pendo_start.duckdb',read_only=True)<br>print(c.execute("show all tables").fetchall()[:5])<br>print(c.execute("select table_name f</code> | 17275 | false | false |
| 19 | run | <code>cat &gt; /tmp/generate.py &lt;&lt;'PY'<br>import yaml,os<br>from pathlib import Path<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for d in ['sql/staging','sql/intermediate','sql/marts']: Path(d).mkdir(parents=T</code> | 0 | false | false |
| 21 | run | <code>cat &gt; /tmp/inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>I=Path('sql/intermediate')<br>def put(n,s): (I/(n+'.sql')).write_text(s.strip())<br># latest rank generation<br>for name,src,pk,ts,cols in [<br>('latest_account</code> | 0 | false | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
'stg_pendo__poll_event':{'occurred_at':'timestamp'}, 'stg_pendo__poll':{'poll_id':'id','follow_up_poll_id':'attribute_follow_up'},
```
event 19 / message

```text
   if name=='stg_pendo__poll_event' and n in ('latitude','longitude'):
```
event 21 / message

```text
put('int_pendo__latest_nps_rating','''WITH nps_polls AS (SELECT poll_id FROM staging.stg_pendo__poll WHERE lower(attribute_type) = 'npsrating'), ranked AS (SELECT e.visitor_id, CAST(e.account_id AS VARCHAR) AS account_id, TRY_CAST(e.poll_response AS INTEGER) AS nps_rating, row_number() OVER (PARTITION BY e.visitor_id ORDER BY e.occurred_at DESC) AS rn FROM staging.stg_pendo__poll_event e INNER JOIN nps_polls p USING (poll_id)) SELECT visitor_id, account_id, nps_rating FROM ranked WHERE rn = 1''')
```

## result.md 本表名原句

未找到 result.md。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-002.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__poll_event.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/staging/stg_pendo__poll_event.sql`
- S6: `records/006_contract_impl-002.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/019_packages_work/019_impl-002_stg_pendo__poll_event/019_impl-002_stg_pendo__poll_event.json`
- S10: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb`
- S11: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/pendo.duckdb`
- S12: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions`
