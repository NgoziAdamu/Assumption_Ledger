# impl-026 | staging | stg_twitter_ads__line_item_history | 差异：S1；日期 原记录

## 契约完整原文

S3:229–292

```yaml
    - name: stg_twitter_ads__line_item_history
      description: "Cleaned line item attributes with monetary conversions and latest-version flag."
      source_table: raw.twitter_line_item_history_data
      columns:
        - name: advertiser_domain
          data_type: VARCHAR
        - name: advertiser_user_id
          data_type: BIGINT
        - name: automatically_select_bid
          data_type: BOOLEAN
        - name: bid_amount_local_micro
          data_type: BIGINT
        - name: bid_amount
          data_type: DECIMAL(18,2)
        - name: bid_type
          data_type: VARCHAR
        - name: bid_unit
          data_type: VARCHAR
        - name: campaign_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: charge_by
          data_type: VARCHAR
        - name: created_timestamp
          data_type: TIMESTAMP
        - name: creative_source
          data_type: VARCHAR
        - name: currency
          data_type: VARCHAR
        - name: is_deleted
          data_type: BOOLEAN
        - name: end_timestamp
          data_type: TIMESTAMP
        - name: entity_status
          data_type: VARCHAR
        - name: line_item_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: name
          data_type: VARCHAR
        - name: objective
          data_type: VARCHAR
        - name: optimization
          data_type: VARCHAR
        - name: primary_web_event_tag
          data_type: VARCHAR
        - name: product_type
          data_type: VARCHAR
        - name: start_timestamp
          data_type: TIMESTAMP
        - name: target_cpa_local_micro
          data_type: BIGINT
        - name: target_cpa
          data_type: DOUBLE
        - name: total_budget_amount_local_micro
          data_type: BIGINT
        - name: total_budget_amount
          data_type: DECIMAL(18,1)
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
    select advertiser_domain, advertiser_user_id, automatically_select_bid,
        cast(bid_amount_local_micro as bigint) as bid_amount_local_micro,
        cast(round(bid_amount_local_micro / 1000000.0, 2) as decimal(18,2)) as bid_amount,
        bid_type, bid_unit, campaign_id, charge_by,
        try_cast(replace(created_at, ' UTC', '') as timestamp) as created_timestamp,
        creative_source, currency, deleted as is_deleted,
        try_cast(replace(cast(end_time as varchar), ' UTC', '') as timestamp) as end_timestamp,
        entity_status, id as line_item_id, name,
        objective, optimization, cast(primary_web_event_tag as varchar) as primary_web_event_tag,
        product_type, try_cast(replace(start_time, ' UTC', '') as timestamp) as start_timestamp,
        cast(target_cpa_local_micro as bigint) as target_cpa_local_micro,
        target_cpa_local_micro / 1000000.0 as target_cpa,
        cast(total_budget_amount_local_micro as bigint) as total_budget_amount_local_micro,
        cast(round(total_budget_amount_local_micro / 1000000.0, 1) as decimal(18,1)) as total_budget_amount,
        try_cast(replace(updated_at, ' UTC', '') as timestamp) as updated_timestamp
    from raw.twitter_line_item_history_data where id is not null and campaign_id is not null
), versioned as (
    select *, row_number() over (partition by line_item_id order by updated_timestamp desc nulls last) = 1 as is_latest_version from cleaned
)
select * from versioned
```

## gold SQL（仅供定位差异）

S5

```sql
with src as (
  select
    advertiser_domain,
    advertiser_user_id,
    automatically_select_bid,
    bid_amount_local_micro,
    bid_type,
    bid_unit,
    campaign_id,
    charge_by,
    try_cast(created_at as timestamp) as created_timestamp,
    creative_source,
    currency,
    coalesce(cast(deleted as boolean), false) as is_deleted,
    try_cast(end_time as timestamp) as end_timestamp,
    upper(trim(entity_status)) as entity_status,
    id as line_item_id,
    name,
    objective,
    optimization,
    primary_web_event_tag,
    product_type,
    try_cast(start_time as timestamp) as start_timestamp,
    target_cpa_local_micro,
    total_budget_amount_local_micro,
    try_cast(updated_at as timestamp) as updated_timestamp
  from raw.twitter_line_item_history_data
), latest as (
  select *, row_number() over(partition by line_item_id order by updated_timestamp desc nulls last) as rn
  from src
)
select
  advertiser_domain,
  advertiser_user_id,
  automatically_select_bid,
  bid_amount_local_micro,
  round(bid_amount_local_micro/1000000.0, 2) as bid_amount,
  bid_type,
  bid_unit,
  campaign_id,
  charge_by,
  created_timestamp,
  creative_source,
  currency,
  is_deleted,
  end_timestamp,
  entity_status,
  line_item_id,
  name,
  objective,
  optimization,
  primary_web_event_tag,
  product_type,
  start_timestamp,
  target_cpa_local_micro,
  round(target_cpa_local_micro/1000000.0, 2) as target_cpa,
  total_budget_amount_local_micro,
  round(total_budget_amount_local_micro/1000000.0, 2) as total_budget_amount,
  updated_timestamp,
  (rn = 1) as is_latest_version
from latest
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2500 | 2500 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"line_item_id":"00s83o"}</code> |
| K2 | <code>{"line_item_id":"010os4"}</code> |
| K3 | <code>{"line_item_id":"018xl2"}</code> |
| K4 | <code>{"line_item_id":"02b8zs"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| advertiser_domain | 0 | 0 | 0 | VARCHAR | VARCHAR |
| advertiser_user_id | 0 | 0 | 0 | BIGINT | BIGINT |
| automatically_select_bid | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| bid_amount_local_micro | 2499 | 2499 | 2499 | BIGINT | DOUBLE |
| bid_amount | 1375 | 1375 | 1375 | DECIMAL(18,2) | DOUBLE |
| bid_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| bid_unit | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| charge_by | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| creative_source | 0 | 0 | 0 | VARCHAR | VARCHAR |
| currency | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_deleted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| end_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| entity_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| line_item_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| objective | 0 | 0 | 0 | VARCHAR | VARCHAR |
| optimization | 0 | 0 | 0 | VARCHAR | VARCHAR |
| primary_web_event_tag | 0 | 0 | 0 | VARCHAR | DOUBLE |
| product_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| start_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| target_cpa_local_micro | 0 | 0 | 0 | BIGINT | DOUBLE |
| target_cpa | 0 | 0 | 0 | DOUBLE | DOUBLE |
| total_budget_amount_local_micro | 2487 | 2487 | 2487 | BIGINT | DOUBLE |
| total_budget_amount | 2240 | 2240 | 2240 | DECIMAL(18,1) | DOUBLE |
| updated_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| is_latest_version | 0 | 0 | 0 | BOOLEAN | BOOLEAN |

bid_amount_local_micro 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 0.0 |
| K2 | 0 | 0.0 |
| K3 | 1113583 | 1113583.0 |

bid_amount 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.00 | 0.0 |
| K2 | 0.00 | 0.0 |
| K4 | 0.00 | 0.0 |

total_budget_amount_local_micro 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 35398162 | 35398162.0 |
| K2 | 89344648 | 89344648.0 |
| K3 | 87625679 | 87625679.0 |

total_budget_amount 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 89.3 | 89.34 |
| K3 | 87.6 | 87.63 |
| K4 | 15.2 | 15.22 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>4列；[{"column":"end_timestamp","table_rows":2500},{"column":"primary_web_event_tag","table_rows":2500},{"column":"target_cpa_local_micro","table_rows":2500}]</code> |
| A3_constant_nonnull_column | <code>3列；[{"column":"creative_source","value":"MANUAL"},{"column":"optimization","value":"DEFAULT"},{"column":"is_latest_version","value":"true"}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：39；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions/6ef6ea16-a56d-43-853379cddede9ee/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print; cat config/layer_dependencies.yaml; sed -n '1,220p' run.py; cat twitter_start.yaml</code> | 15102 | true | false |
| 9 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('twitter_start.duckdb',read_only=True)<br>for t, in c.execute("select table_name from information_schema.tables where table_schema='raw' order by 1").fetcha</code> | 20910 | false | false |
| 11 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('twitter_start.duckdb',read_only=True)<br>for t,cols in [('twitter_line_item_history_data',['end_time','start_time','bid_amount_local_micro','target_cpa_loc</code> | 1511 | false | false |
| 13 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>S=Path('sql/staging'); I=Path('sql/intermediate'); M=Path('sql/marts')<br>def put(d,n,s): (d/f'{n}.sql')</code> | 0 | false | false |
| 15 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br># Intermediate projection models<br>put(I,'int_twitter_ads__accounts',"""select account_id, approval_status, business_id, business_name, created_timestamp, is_deleted,<br>    indus</code> | 0 | false | false |
| 19 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br>ptdims=['r.date_day','r.placement','r.account_id','a.account_name','li.campaign_id','c.campaign_name','pt.line_item_id','li.line_item_name','r.promoted_tweet_id','pt.tweet_id</code> | 4754 | true | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_twitter_ads__line_item_keywords_report.sql'<br>s=open(p).read().replace('    placement,\n    clicks,', '    placement,\n    clicks,')<br># add keyword_id projection next t</code> | 4229 | true | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql/intermediate').glob('*_report_base.sql'):<br> s=p.read_text().replace('select date_day, ', 'select cast(date_day as date) as date_day, ')<br> p.wr</code> | 2974 | true | false |

### agent action 的 thought/message 命中原句

event 13 / message

```text
put(S,'stg_twitter_ads__line_item_history',"""with cleaned as (
```
event 15 / message

```text
from staging.stg_twitter_ads__line_item_history
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-026.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__line_item_history.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/sql/staging/stg_twitter_ads__line_item_history.sql`
- S6: `records/006_contract_impl-026.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/result.md`
- S10: `data/024_packages_work/024_impl-026_stg_twitter_ads__line_item_history/024_impl-026_stg_twitter_ads__line_item_history.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/twitter.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-026/twitter.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/.events/sessions`
