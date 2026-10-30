# impl-023 | staging | stg_social_media__linkedin_posts | 差异：S1；日期 原记录

## 契约完整原文

S3:331–352

```yaml
    - name: stg_social_media__linkedin_posts
      description: "Minimal staging representation of LinkedIn organization UGC posts with standardized identifiers and URL."
      source_table: raw.linkedin_pages_organization_ugc_post
      columns:
        - name: organization_id
          data_type: VARCHAR
        - name: post_id
          data_type: VARCHAR
        - name: created_timestamp
          data_type: TIMESTAMP
        - name: platform
          data_type: VARCHAR
        - name: post_message
          data_type: VARCHAR
        - name: content_type
          data_type: VARCHAR
        - name: post_url
          data_type: VARCHAR
          validation_rules:
            - rule: "post_url RLIKE '^https://www.linkedin.com/feed/update/.+'"
              on_failure: correct

```

## agent 最终 SQL

S4

```sql
with post_metrics as (
    select
        _share_entity_urn,
        max(click_count) as click_count,
        max(impression_count) as impression_count,
        max(like_count) as like_count,
        max(share_count) as share_count,
        max(comment_count) as comment_count,
        max(engagement) as engagement
    from raw.linkedin_pages_share_statistic
    group by _share_entity_urn
)
select
    cast(o.organiation_id as varchar) as organization_id,
    o.ugc_post_id::varchar as post_id,
    h.created_time::timestamp as created_timestamp,
    'linkedin'::varchar as platform,
    coalesce(pc.article_title, pc.media_title, h.commentary)::varchar as post_message,
    pc.type::varchar as content_type,
    ('https://www.linkedin.com/feed/update/' || o.ugc_post_id)::varchar as post_url
from raw.linkedin_pages_organization_ugc_post o
left join raw.linkedin_pages_ugc_post_history h on h.id = o.ugc_post_id
left join raw.linkedin_pages_post_content pc on pc.post_id = regexp_replace(o.ugc_post_id, '^urn:li:share:', 'urn:li:share:')
left join post_metrics pm on pm._share_entity_urn = o.ugc_post_id
where o.organiation_id is not null
```

## gold SQL（仅供定位差异）

S5

```sql
-- LinkedIn posts staging table - Simplified version
-- Based on actual table structure

-- Source posts from organization UGC posts
SELECT
    CAST(organiation_id AS VARCHAR) AS organization_id,
    CAST(ugc_post_id AS VARCHAR) AS post_id,
    _fivetran_synced AS created_timestamp,
    'linkedin' AS platform,
    CONCAT('LinkedIn Post ', ugc_post_id) AS post_message,
    'text' AS content_type,
    CONCAT('https://www.linkedin.com/feed/update/', ugc_post_id) AS post_url
FROM raw.linkedin_pages_organization_ugc_post
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 100 | 100 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"organization_id":"10429","post_id":"urn:li:share:1034655442"}</code> |
| K2 | <code>{"organization_id":"10429","post_id":"urn:li:share:1034687017"}</code> |
| K3 | <code>{"organization_id":"10429","post_id":"urn:li:share:1035074525"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| organization_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| post_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_timestamp | 100 | 100 | 100 | TIMESTAMP | TIMESTAMP |
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| post_url | 0 | 0 | 0 | VARCHAR | VARCHAR |

created_timestamp 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 2021-10-27 14:40:10.56 |
| K2 | null | 2021-10-27 14:40:10.56 |
| K3 | null | 2021-10-27 14:40:10.56 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>3列；[{"column":"created_timestamp","table_rows":100},{"column":"post_message","table_rows":100},{"column":"content_type","table_rows":100}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"organization_id","value":"10429"},{"column":"platform","value":"linkedin"}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"platform","expression":["CAST('linkedin' AS TEXT)"]}]</code> |
| B7_read_not_specified | <code>["raw.linkedin_pages_post_content","raw.linkedin_pages_share_statistic","raw.linkedin_pages_ugc_post_history"]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions/93c59abd-420e-4d-83698adfc12a3fd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 2094 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9937 | true | false |
| 15 | run | <code>sed -n '220,520p' docs/data_contract.yaml</code> | 16556 | true | false |
| 17 | run | <code>sed -n '520,790p' docs/data_contract.yaml</code> | 19316 | true | false |
| 23 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb',read_only=True)<br>for t, in c.execute("select table_name from information_schema.tables where table_schema='raw' orde</code> | 30939 | false | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb',read_only=True)<br>for t in ['instagram_business_user_history','instagram_business_media_insights','linkedin_pages_ugc</code> | 1705 | false | false |
| 27 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb',read_only=True)<br>for t in ['linkedin_pages_organization_ugc_post','linkedin_pages_ugc_post_history','linkedin_pages_</code> | 12482 | false | false |
| 29 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts &amp;&amp; cat &gt; /tmp/write_sql.py &lt;&lt;'PY'<br>from pathlib import Path<br>files={}<br>files['staging/stg_social_media__account_history.sql'] = '''select<br>    try_cast(id a</code> | 0 | false | false |
| 31 | run | <code>cat &gt;&gt; /tmp/write_sql.py &lt;&lt;'PY'<br>files['intermediate/social_media_reporting__facebook_posts_reporting.sql'] = '''with source_posts as (<br>    select<br>        cast(page_id as varchar) as page_id,<br>        p</code> | 0 | false | false |
| 33 | run | <code>cat &gt;&gt; /tmp/write_sql.py &lt;&lt;'PY'<br>files['marts/social_media_reporting__rollup_report.sql'] = '''with all_posts as (<br>    select page_id, page_name, post_id, post_message, created_timestamp, platform,<br>   </code> | 917 | true | false |
| 37 | run | <code>grep 'staging\.&#124;intermediate\.&#124;marts\.' /tmp/pipeline.log &#124; tail -35; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting.duckdb',read_only=True)<br>for schema in ['staging','intermedi</code> | 1464 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb',read_only=True)<br>for t,col in [('account_history','timezone'),('facebook_pages_post_history','created_time'),('insta</code> | 1457 | false | false |
| 41 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting.duckdb',read_only=True)<br>for t in ['stg_social_media__linkedin_posts','social_media_reporting__linkedin_posts_reporting']:<br> print(</code> | 977 | true | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('social_media_reporting_start.duckdb')<br>print('ids linkedin match',c.execute("select count(*) from raw.linkedin_pages_organization_ugc_post o join raw.lin</code> | 639 | false | false |
| 49 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql').rglob('*.sql'):<br> s=p.read_text()<br> assert not s.rstrip().endswith(';'), p<br> assert 'ref(' not in s.lower(), p<br> print(f'{p}: {len(s.splitline</code> | 1600 | true | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
files['staging/stg_social_media__linkedin_posts.sql'] = '''with post_metrics as (
```
event 31 / message

```text
    from staging.stg_social_media__linkedin_posts
```
event 41 / message

```text
for t in ['stg_social_media__linkedin_posts','social_media_reporting__linkedin_posts_reporting']:
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-023.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__linkedin_posts.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/sql/staging/stg_social_media__linkedin_posts.sql`
- S6: `records/006_contract_impl-023.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/result.md`
- S10: `data/024_packages_work/024_impl-023_stg_social_media__linkedin_posts/024_impl-023_stg_social_media__linkedin_posts.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/social_media_reporting.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-023/social_media_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/.events/sessions`
