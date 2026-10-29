# impl-029 | staging | stg_zendesk__schedule_holiday | 差异：S1；日期 原记录

## 契约完整原文

S3:131–146

```yaml
    - name: stg_zendesk__schedule_holiday
      description: "Holiday exceptions per schedule."
      source_table: raw.schedule_holiday_data
      columns:
        - name: schedule_holiday_id
          data_type: BIGINT
          constraints: [not_null]
        - name: schedule_id
          data_type: BIGINT
        - name: name
          data_type: VARCHAR
        - name: start_date
          data_type: DATE
        - name: end_date
          data_type: DATE

```

## agent 最终 SQL

S4

```sql
select
    try_cast("id" as BIGINT) as schedule_holiday_id,
    try_cast("schedule_id" as BIGINT) as schedule_id,
    try_cast("name" as VARCHAR) as name,
    try_cast("start_date" as DATE) as start_date,
    try_cast("end_date" as DATE) as end_date
from raw.schedule_holiday_data
where try_cast("id" as BIGINT) is not null
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
  select id, schedule_id, name, start_date, end_date, _fivetran_deleted from raw.schedule_holiday_data
), cleaned as (
  select cast(id as BIGINT) as schedule_holiday_id,
         cast(schedule_id as BIGINT) as schedule_id,
         name,
         cast(substr(cast(start_date as varchar), 1, 10) as DATE) as start_date,
         cast(substr(cast(end_date as varchar), 1, 10) as DATE) as end_date
  from base
  where id is not null and coalesce(try_cast(_fivetran_deleted as BOOLEAN), false) = false
)
select *
from cleaned
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 51 | 51 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"schedule_holiday_id":"1163027"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| schedule_holiday_id | 0 | 0 | 0 | BIGINT | BIGINT |
| start_date | 1 | 1 | 1 | DATE | DATE |
| end_date | 0 | 0 | 0 | DATE | DATE |

start_date 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 2022-12-29 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"schedule_id","value":"360000"}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：57；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-029/agent/.events/sessions/68a7ea61-4e9f-46-b468b8adb71510e/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find . -maxdepth 3 -type f &#124; sort &#124; head -100</code> | 1864 | false | false |
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print -exec wc -c {} \;</code> | 2953 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 8967 | false | false |
| 11 | run | <code>sed -n '1,240p' docs/data_contract.yaml</code> | 7773 | true | false |
| 17 | run | <code>sed -n '240,520p' run.py &amp;&amp; cat zendesk_start.yaml</code> | 16826 | false | false |
| 21 | run | <code>cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml, pathlib<br>spec=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']['tables']<br># map staging column names to raw names where they differ<br>maps={<br>'stg_z</code> | 0 | false | false |
| 29 | run | <code>python run.py &gt; /tmp/pipeline.log 2&gt;&amp;1; status=$?; tail -100 /tmp/pipeline.log; exit $status</code> | 7239 | true | false |

### agent action 的 thought/message 命中原句

event 21 / message

```text
'stg_zendesk__schedule':{'schedule_id':'id'},'stg_zendesk__schedule_holiday':{'schedule_holiday_id':'id'},
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-029.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-029/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-029/agent/dacomp-de-impl-029/sql/staging/stg_zendesk__schedule_holiday.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-029/sql/staging/stg_zendesk__schedule_holiday.sql`
- S6: `records/006_contract_impl-029.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-029/agent/dacomp-de-impl-029/result.md`
- S10: `records/012_packages/012_impl-029_staging_stg_zendesk__schedule_holiday.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-029/agent/dacomp-de-impl-029/zendesk.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-029/zendesk.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-029/agent/.events/sessions`
