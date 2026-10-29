# impl-005 | staging | stg_google_ads__campaign_history | 差异：S1；日期 2025-10-11

## 契约完整原文

S3:72–118

```yaml
    - name: stg_google_ads__campaign_history
      description: "Cleaned and validated Google Ads campaign configuration data with hierarchical relationships"
      source_table: "raw.campaign_history_data"
      columns:
        - name: source_relation
          data_type: VARCHAR(100)
        - name: campaign_id
          data_type: VARCHAR(20)
          constraints: [not_null]
        - name: updated_at
          data_type: TIMESTAMP
          constraints: [not_null]
        - name: campaign_name
          data_type: VARCHAR(255)
          constraints: [not_null]
        - name: account_id
          data_type: VARCHAR(20)
          constraints: [not_null]
        - name: advertising_channel_type
          data_type: VARCHAR(50)
          constraints: [not_null]
          validation_rules:
            - rule: "advertising_channel_type IN ('SEARCH', 'DISPLAY', 'SHOPPING', 'VIDEO', 'MULTI_CHANNEL')"
              on_failure: nullify_field
        - name: advertising_channel_subtype
          data_type: VARCHAR(100)
        - name: start_date
          data_type: DATE
          validation_rules:
            - rule: "start_date <= CURRENT_DATE"
              on_failure: delete_row
        - name: end_date
          data_type: DATE
          validation_rules:
            - rule: "end_date IS NULL OR end_date >= start_date"
              on_failure: delete_row
        - name: serving_status
          data_type: VARCHAR(20)
        - name: status
          data_type: VARCHAR(20)
          constraints: [not_null]
        - name: tracking_url_template
          data_type: VARCHAR(500)
        - name: is_most_recent_record
          data_type: BOOLEAN
          constraints: [not_null]

```

## agent 最终 SQL

S4

```sql
WITH base AS (
    SELECT 'google_ads'::VARCHAR AS source_relation, *
    FROM raw.campaign_history_data
),
validated AS (
    SELECT source_relation, CAST(id AS VARCHAR(20)) campaign_id, try_strptime(updated_at, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP updated_at, name campaign_name, CAST(customer_id AS VARCHAR(20)) account_id, case when advertising_channel_type in ('SEARCH','DISPLAY','SHOPPING','VIDEO','MULTI_CHANNEL') then advertising_channel_type end advertising_channel_type, advertising_channel_subtype, try_cast(start_date AS DATE) start_date, try_cast(end_date AS DATE) end_date, serving_status, status, tracking_url_template, row_number() over(partition by id order by try_cast(updated_at AS TIMESTAMPTZ) desc nulls last)=1 is_most_recent_record
    FROM base
)
SELECT *
FROM validated
WHERE campaign_id is not null and updated_at is not null and campaign_name is not null and account_id is not null and advertising_channel_type is not null and status is not null and (start_date is null or start_date <= current_date) and (end_date is null or start_date is null or end_date >= start_date)
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select *
    from raw.campaign_history_data
),

validated as (
    select
        'google_ads' as source_relation,
        CAST(id AS VARCHAR(20)) as campaign_id,
        try_cast(updated_at AS TIMESTAMP) as updated_at,
        CAST(name AS VARCHAR(255)) as campaign_name,
        CAST(customer_id AS VARCHAR(20)) as account_id,
        CAST(advertising_channel_type AS VARCHAR(50)) as advertising_channel_type,
        CAST(advertising_channel_subtype AS VARCHAR(100)) as advertising_channel_subtype,
        CAST(try_cast(start_date as date) AS DATE) as start_date,
        CAST(try_cast(end_date as date) AS DATE) as end_date,
        CAST(serving_status AS VARCHAR(20)) as serving_status,
        CAST(status AS VARCHAR(20)) as status,
        CAST(tracking_url_template AS VARCHAR(500)) as tracking_url_template,
        CAST(row_number() over (partition by id order by updated_at desc) = 1 AS BOOLEAN) as is_most_recent_record
    from base

    -- Validation rules per YAML specification
    WHERE try_cast(updated_at AS TIMESTAMP) <= CURRENT_TIMESTAMP
      AND (advertising_channel_type is null OR advertising_channel_type IN ('SEARCH', 'DISPLAY', 'SHOPPING', 'VIDEO', 'MULTI_CHANNEL'))
      AND (start_date is null OR try_cast(start_date as DATE) <= CURRENT_DATE)
      AND (start_date is null OR end_date is null OR end_date >= start_date)
),

final as (
    select
        source_relation,
        campaign_id,
        updated_at,
        campaign_name,
        account_id,
        advertising_channel_type,
        advertising_channel_subtype,
        start_date,
        end_date,
        serving_status,
        status,
        tracking_url_template,
        is_most_recent_record
    from validated

    -- Apply data quality corrections and nullifications
    WHERE campaign_id is not null
      and account_id is not null
      and campaign_name is not null
      and status is not null
      and is_most_recent_record is not null
)

select *
from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1000 | 0 | 1000 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| advertising_channel_subtype | 0 | 0 | 0 | VARCHAR | VARCHAR |
| advertising_channel_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| end_date | 0 | 0 | 0 | DATE | DATE |
| is_most_recent_record | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| serving_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| start_date | 0 | 0 | 0 | DATE | DATE |
| status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| tracking_url_template | 0 | 0 | 0 | VARCHAR | VARCHAR |
| updated_at | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"campaign_id":"CAM00008577575"},{"campaign_id":"CAM00175881930"},{"campaign_id":"CAM00188840205"},{"campaign_id":"CAM00484558306"},{"campaign_id":"CAM00639555210"}]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>2列；[{"column":"source_relation","value":"google_ads"},{"column":"is_most_recent_record","value":"true"}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"source_relation","expression":["CAST('google_ads' AS TEXT)"]}]</code> |
| C9_agent_runtime_text | <code>S4:11 current_date；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:24 CURRENT_TIMESTAMP；命中数=2</code> |
| C9_contract_runtime_text | <code>S3:101 CURRENT_DATE；命中数=1</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory 'stg_google_ads__campaign_history':('campaign_history_data', '''source_relation, CAST(id AS VARCHAR(20)) campaign_id, try_cast(updated_at AS TIMESTAMPTZ)::TIMESTAMP updated_at, name campaign_name, CAST(customer_id AS VARCHAR(20)) account_id, case when advertising_channel_type in ('SEARCH','DISPLAY','SHOPPING','VIDEO','MULTI_CHANNEL') then advertising_channel_type end advertising_channel_type, advertising_channel_subtype, try_cast(start_date AS TIMESTAMPTZ)::DATE start_date, try_cast(end_date AS TIMESTAMPTZ)::DATE end_date, serving_status, status, tracking_url_template, row_number() over(partition by id order by try_cast(updated_at AS TIMESTAMPTZ) desc nulls last)=1 is_most_recent_record''','''campaign_id is not null and updated_at is not null and campaign_name is not null and account_id is not null and advertising_channel_type is not null and status is not null and (start_date is null or start_date &lt;= current_date) and (end_date is null or start_date is null or end_date &gt;= start_date)'''),</code> |

## 轨迹索引（不放输出原文）

本题事件总数：49；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print -exec wc -l {} \;</code> | 2838 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9858 | false | false |
| 11 | run | cat google_ads_start.yaml | 4209 | false | false |
| 13 | run | <code>find sql -maxdepth 2 -type f -print; sed -n '240,450p' run.py; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('google_ads_start.duckdb',read_only=True)<br>for (t,) in c.execute("select table_name from in</code> | 16568 | false | false |
| 15 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>S=Path('sql/staging')<br># helper CTE SQL table<br>spec={<br>'stg_google_ads__account_history':('account_history_d</code> | 0 | false | false |
| 19 | run | <code>cat &gt; sql/intermediate/int_google_ads__campaign_cohort_analysis.sql &lt;&lt;'SQL'<br>WITH history AS (<br>    SELECT * FROM staging.stg_google_ads__campaign_history WHERE is_most_recent_record<br>),<br>stats AS (<br>    S</code> | 0 | false | false |
| 21 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>M=Path('sql/marts')<br># common basic report templates<br><br>def write(name,sql): (M/f'{name}.sql').write_text(sql)<br>write('google_ads__account_report',"""WI</code> | 0 | false | false |
| 25 | run | <code>sed -i "s/and ad_network_type in ('SEARCH','DISPLAY','MIXED','YOUTUBE') or ad_network_type is null/and (ad_network_type in ('SEARCH','DISPLAY','MIXED','YOUTUBE') or ad_network_type is null)/" sql/stag</code> | 8152 | true | false |
| 27 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('google_ads.duckdb',read_only=True)<br>for t,f in [('account_stats_data','date'),('account_history_data','updated_at'),('campaign_history_data','start_date'</code> | 687 | false | false |
| 31 | run | <code>python run.py &gt; /tmp/run2.log 2&gt;&amp;1; grep -E 'ERROR&#124;Layer complete&#124;rows$' /tmp/run2.log &#124; tail -60</code> | 2499 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb, pathlib<br>c=duckdb.connect('google_ads.duckdb',read_only=True)<br>for schema in ('staging','intermediate','marts'):<br> for (t,) in c.execute(f"select table_name from informatio</code> | 2322 | true | false |

### agent action 的 thought/message 命中原句

event 15 / message

```text
'stg_google_ads__campaign_history':('campaign_history_data', '''source_relation, CAST(id AS VARCHAR(20)) campaign_id, try_cast(updated_at AS TIMESTAMPTZ)::TIMESTAMP updated_at, name campaign_name, CAST(customer_id AS VARCHAR(20)) account_id, case when advertising_channel_type in ('SEARCH','DISPLAY','SHOPPING','VIDEO','MULTI_CHANNEL') then advertising_channel_type end advertising_channel_type, advertising_channel_subtype, try_cast(start_date AS TIMESTAMPTZ)::DATE start_date, try_cast(end_date AS TIMESTAMPTZ)::DATE end_date, serving_status, status, tracking_url_template, row_number() over(partition by id order by try_cast(updated_at AS TIMESTAMPTZ) desc nulls last)=1 is_most_recent_record''','''campaign_id is not null and updated_at is not null and campaign_name is not null and account_id is not null and advertising_channel_type is not null and status is not null and (start_date is null or start_date <= current_date) and (end_date is null or start_date is null or end_date >= start_date)'''),
```
event 19 / message

```text
    SELECT * FROM staging.stg_google_ads__campaign_history WHERE is_most_recent_record
```
event 19 / message

```text
    LEFT JOIN staging.stg_google_ads__campaign_history ch ON ks.campaign_id=ch.campaign_id AND ks.source_relation=ch.source_relation AND ch.is_most_recent_record
```
event 21 / message

```text
write('google_ads__campaign_report',"""WITH stats AS (SELECT * FROM staging.stg_google_ads__campaign_stats), c AS (SELECT * FROM staging.stg_google_ads__campaign_history WHERE is_most_recent_record), a AS (SELECT * FROM staging.stg_google_ads__account_history WHERE is_most_recent_record)
```
event 21 / message

```text
write('google_ads__ad_group_report',"""WITH s AS (SELECT * FROM staging.stg_google_ads__ad_group_stats), ag AS (SELECT * FROM staging.stg_google_ads__ad_group_history WHERE is_most_recent_record), c AS (SELECT * FROM staging.stg_google_ads__campaign_history WHERE is_most_recent_record), a AS (SELECT * FROM staging.stg_google_ads__account_history WHERE is_most_recent_record)
```
event 21 / message

```text
write('google_ads__ad_report',"""WITH s AS (SELECT * FROM staging.stg_google_ads__ad_stats), ad AS (SELECT * FROM staging.stg_google_ads__ad_history WHERE is_most_recent_record), ag AS (SELECT * FROM staging.stg_google_ads__ad_group_history WHERE is_most_recent_record), c AS (SELECT * FROM staging.stg_google_ads__campaign_history WHERE is_most_recent_record), a AS (SELECT * FROM staging.stg_google_ads__account_history WHERE is_most_recent_record)
```
event 21 / message

```text
write('google_ads__keyword_report',"""WITH s AS (SELECT * FROM staging.stg_google_ads__keyword_stats), cr AS (SELECT * FROM staging.stg_google_ads__ad_group_criterion_history WHERE is_most_recent_record), ag AS (SELECT * FROM staging.stg_google_ads__ad_group_history WHERE is_most_recent_record), c AS (SELECT * FROM staging.stg_google_ads__campaign_history WHERE is_most_recent_record), a AS (SELECT * FROM staging.stg_google_ads__account_history WHERE is_most_recent_record)
```
event 21 / message

```text
write('google_ads__search_term_report',"""WITH s AS (SELECT * FROM staging.stg_google_ads__search_term_keyword_stats), cr AS (SELECT * FROM staging.stg_google_ads__ad_group_criterion_history WHERE is_most_recent_record), ag AS (SELECT * FROM staging.stg_google_ads__ad_group_history WHERE is_most_recent_record), c AS (SELECT * FROM staging.stg_google_ads__campaign_history WHERE is_most_recent_record), a AS (SELECT * FROM staging.stg_google_ads__account_history WHERE is_most_recent_record)
```
event 21 / message

```text
write('google_ads__url_report',"""WITH s AS (SELECT * FROM staging.stg_google_ads__ad_stats), ad AS (SELECT * FROM staging.stg_google_ads__ad_history WHERE is_most_recent_record), ag AS (SELECT * FROM staging.stg_google_ads__ad_group_history WHERE is_most_recent_record), c AS (SELECT * FROM staging.stg_google_ads__campaign_history WHERE is_most_recent_record), a AS (SELECT * FROM staging.stg_google_ads__account_history WHERE is_most_recent_record), enriched AS (
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-005.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-005/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/staging/stg_google_ads__campaign_history.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/sql/staging/stg_google_ads__campaign_history.sql`
- S6: `records/006_contract_impl-005.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/result.md`
- S10: `data/019_packages_work/019_impl-005_stg_google_ads__campaign_history/019_impl-005_stg_google_ads__campaign_history.json`
- S11: `data/011_agent_alignment/impl-005_attempt_01/stg_google_ads__campaign_history_2025-10-11.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/google_ads.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions`
