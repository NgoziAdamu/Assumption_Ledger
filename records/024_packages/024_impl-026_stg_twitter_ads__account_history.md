# impl-026 | staging | stg_twitter_ads__account_history | 差异：S1；日期 原记录

## 契约完整原文

S3:24–60

```yaml
    - name: stg_twitter_ads__account_history
      description: "Cleaned and standardized Twitter Ads account attributes with latest-version flag."
      source_table: raw.twitter_account_history_data
      columns:
        - name: account_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: approval_status
          data_type: VARCHAR
          validation_rules:
            - rule: "approval_status IN ('ACCEPTED','PENDING','REJECTED')"
              on_failure: delete_row
        - name: business_id
          data_type: VARCHAR
        - name: business_name
          data_type: VARCHAR
        - name: created_timestamp
          data_type: TIMESTAMP
        - name: is_deleted
          data_type: BOOLEAN
        - name: industry_type
          data_type: VARCHAR
        - name: name
          data_type: VARCHAR
        - name: timezone
          data_type: VARCHAR
          validation_rules:
            - rule: "timezone IN ('America/Los_Angeles','America/New_York','Europe/London','Asia/Tokyo','Australia/Sydney','UTC')"
              on_failure: correct
        - name: timezone_switched_timestamp
          data_type: TIMESTAMP
        - name: updated_timestamp
          data_type: TIMESTAMP
        - name: is_latest_version
          data_type: BOOLEAN
          constraints: [not_null]

```

## agent 最终 SQL

S4

```sql
with cleaned as (
    select
        id as account_id,
        upper(trim(approval_status)) as approval_status,
        business_id,
        business_name,
        try_cast(replace(created_at, ' UTC', '') as timestamp) as created_timestamp,
        deleted as is_deleted,
        industry_type,
        name,
        case when timezone in ('America/Los_Angeles','America/New_York','Europe/London','Asia/Tokyo','Australia/Sydney','UTC') then timezone else 'UTC' end as timezone,
        try_cast(replace(timezone_switch_at, ' UTC', '') as timestamp) as timezone_switched_timestamp,
        try_cast(replace(updated_at, ' UTC', '') as timestamp) as updated_timestamp
    from raw.twitter_account_history_data
    where id is not null
), valid_rows as (
    select * from cleaned where approval_status in ('ACCEPTED','PENDING','REJECTED')
), versioned as (
    select *, row_number() over (partition by account_id order by updated_timestamp desc nulls last) = 1 as is_latest_version from valid_rows
)
select * from versioned
```

## gold SQL（仅供定位差异）

S5

```sql
with src as (
  select
    id as account_id,
    upper(trim(approval_status)) as approval_status_raw,
    business_id,
    business_name,
    try_cast(created_at as timestamp) as created_timestamp,
    coalesce(cast(deleted as boolean), false) as is_deleted,
    industry_type,
    name,
    trim(timezone) as timezone_raw,
    try_cast(timezone_switch_at as timestamp) as timezone_switched_timestamp,
    try_cast(updated_at as timestamp) as updated_timestamp,
    salt
  from raw.twitter_account_history_data
), cleaned as (
  select
    account_id,
    case
      when approval_status_raw in ('ACCEPTED','PENDING','REJECTED') then approval_status_raw
      when approval_status_raw in ('accepted','pending','rejected') then upper(approval_status_raw)
      else null
    end as approval_status,
    business_id,
    business_name,
    created_timestamp,
    is_deleted,
    account_id as id_for_version,
    industry_type,
    name,
    case when timezone_raw in ('America/Los_Angeles','America/New_York','Europe/London','Asia/Tokyo','Australia/Sydney','UTC') then timezone_raw else 'UTC' end as timezone,
    timezone_switched_timestamp,
    updated_timestamp
  from src
  where approval_status_raw is not null
), latest as (
  select *, row_number() over(partition by id_for_version order by updated_timestamp desc nulls last) as rn
  from cleaned
)
select
  account_id,
  approval_status,
  business_id,
  business_name,
  created_timestamp,
  is_deleted,
  industry_type,
  name,
  timezone,
  timezone_switched_timestamp,
  updated_timestamp,
  (rn = 1) as is_latest_version
from latest
where approval_status is not null
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2487 | 2487 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"account_id":"18ce5ig3qj77q64"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| approval_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| business_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| business_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| is_deleted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| industry_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| timezone | 1 | 1 | 1 | VARCHAR | VARCHAR |
| timezone_switched_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| updated_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| is_latest_version | 0 | 0 | 0 | BOOLEAN | BOOLEAN |

timezone 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | UTC | America/Los_Angeles |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"is_latest_version","value":"true"}]</code> |

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

### agent action 的 thought/message 命中原句

event 13 / message

```text
put(S,'stg_twitter_ads__account_history',"""with cleaned as (
```
event 15 / message

```text
from staging.stg_twitter_ads__account_history
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-026.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__account_history.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/staging/stg_twitter_ads__account_history.sql`
- S6: `records/006_contract_impl-026.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/result.md`
- S10: `data/024_packages_work/024_impl-026_stg_twitter_ads__account_history/024_impl-026_stg_twitter_ads__account_history.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/twitter.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions`
