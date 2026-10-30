# impl-026 | staging | stg_twitter_ads__tweet | 差异：S1；日期 原记录

## 契约完整原文

S3:429–446

```yaml
    - name: stg_twitter_ads__tweet
      description: "Cleaned tweets with validated language and reasonable created_at bounds applied at staging filter."
      source_table: raw.twitter_tweet_data
      columns:
        - name: account_id
          data_type: VARCHAR
        - name: tweet_id
          data_type: VARCHAR
        - name: name
          data_type: VARCHAR
        - name: full_text
          data_type: VARCHAR
        - name: language
          data_type: VARCHAR
          validation_rules:
            - rule: "language IN ('en','es','fr','de','ja','zh','ar','pt','ru','ko')"
              on_failure: nullify_field

```

## agent 最终 SQL

S4

```sql
select account_id, cast(id as varchar) as tweet_id, name, full_text,
    case when lang in ('en','es','fr','de','ja','zh','ar','pt','ru','ko') then lang else null end as language
from raw.twitter_tweet_data
where try_cast(replace(created_at, ' UTC', '') as timestamp) between timestamp '2006-01-01' and timestamp '2100-01-01'
```

## gold SQL（仅供定位差异）

S5

```sql
with src as (
  select
    account_id,
    id as tweet_id,
    name,
    full_text,
    lower(trim(lang)) as lang_raw,
    try_cast(created_at as timestamp) as created_at_ts
  from raw.twitter_tweet_data
), cleaned as (
  select
    account_id,
    tweet_id,
    name,
    full_text,
    case when lang_raw ~ '^[a-z]{2}$' and lang_raw in ('en','es','fr','de','ja','zh','ar','pt','ru','ko') then lang_raw else null end as language,
    created_at_ts
  from src
)
select
  account_id,
  tweet_id,
  name,
  full_text,
  language
from cleaned
where created_at_ts is not null and created_at_ts >= timestamp '2010-01-01' and created_at_ts <= current_localtimestamp()
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2489 | 2489 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"tweet_id":"1686504562803008478"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| tweet_id | 0 | 0 | 0 | VARCHAR | BIGINT |
| name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| language | 1 | 1 | 1 | VARCHAR | VARCHAR |

language 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | en |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| D10_keyword_in_any_result_field | <code>命中数=1；task_instruction_not_agent_report       business_logic: '- Read rows from staging.stg_twitter_ads__tweet - Select fields: account_id, tweet_id, name, full_text, language - Rename: name -&gt; tweet_name; full_text -&gt; tweet_full_text - No filters, joins, or aggregations; duplicates are allowed; ordering is not enforced - Pass through values as stored; casing, punctuation, and whitespace are preserved; NULLs are preserved'</code> |

## 轨迹索引（不放输出原文）

本题事件总数：39；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print; cat config/layer_dependencies.yaml; sed -n '1,220p' run.py; cat twitter_start.yaml</code> | 15102 | true | false |
| 9 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('twitter_start.duckdb',read_only=True)<br>for t, in c.execute("select table_name from information_schema.tables where table_schema='raw' order by 1").fetcha</code> | 20910 | false | false |
| 13 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>S=Path('sql/staging'); I=Path('sql/intermediate'); M=Path('sql/marts')<br>def put(d,n,s): (d/f'{n}.sql')</code> | 0 | false | false |
| 15 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br># Intermediate projection models<br>put(I,'int_twitter_ads__accounts',"""select account_id, approval_status, business_id, business_name, created_timestamp, is_deleted,<br>    indus</code> | 0 | false | false |
| 19 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br>ptdims=['r.date_day','r.placement','r.account_id','a.account_name','li.campaign_id','c.campaign_name','pt.line_item_id','li.line_item_name','r.promoted_tweet_id','pt.tweet_id</code> | 4754 | true | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_twitter_ads__line_item_keywords_report.sql'<br>s=open(p).read().replace('    placement,\n    clicks,', '    placement,\n    clicks,')<br># add keyword_id projection next t</code> | 4229 | true | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql/intermediate').glob('*_report_base.sql'):<br> s=p.read_text().replace('select date_day, ', 'select cast(date_day as date) as date_day, ')<br> p.wr</code> | 2974 | true | false |

### agent action 的 thought/message 命中原句

event 13 / message

```text
put(S,'stg_twitter_ads__tweet',"""select account_id, cast(id as varchar) as tweet_id, name, full_text,
```
event 15 / message

```text
from staging.stg_twitter_ads__tweet""")
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-026.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__tweet.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/staging/stg_twitter_ads__tweet.sql`
- S6: `records/006_contract_impl-026.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/result.md`
- S10: `data/024_packages_work/024_impl-026_stg_twitter_ads__tweet/024_impl-026_stg_twitter_ads__tweet.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/twitter.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions`
