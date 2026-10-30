# impl-030 | staging | stg_zuora__product_rate_plan | 差异：S1；日期 原记录

## 契约完整原文

S3:624–657

```yaml
    - name: stg_zuora__product_rate_plan
      description: "Cleaned product rate plans; latest snapshot indicator."
      source_table: raw.zuora_product_rate_plan_data
      columns:
        - name: product_rate_plan_id
          data_type: VARCHAR
          source_expression: "id"
        - name: created_by_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
          source_expression: "cast(created_date as TIMESTAMP)"
        - name: description
          data_type: VARCHAR
        - name: effective_end_date
          data_type: DATE
        - name: effective_start_date
          data_type: DATE
        - name: name
          data_type: VARCHAR
        - name: product_id
          data_type: VARCHAR
        - name: updated_by_id
          data_type: VARCHAR
        - name: updated_date
          data_type: TIMESTAMP
          source_expression: "cast(updated_date as TIMESTAMP)"
        - name: is_most_recent_record
          data_type: BOOLEAN
          source_expression: "row_number() over (partition by id order by updated_date desc) = 1"
      row_filters:
        - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
          on_failure: delete_row

```

## agent 最终 SQL

S4

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_product_rate_plan_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT
        id AS product_rate_plan_id,
        try_cast("created_by_id" AS VARCHAR) AS created_by_id,
        try_cast(created_date as TIMESTAMP) AS created_date,
        try_cast("description" AS VARCHAR) AS description,
        try_cast("effective_end_date" AS DATE) AS effective_end_date,
        try_cast("effective_start_date" AS DATE) AS effective_start_date,
        try_cast("name" AS VARCHAR) AS name,
        try_cast("id" AS VARCHAR) AS product_id,
        try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
        try_cast(updated_date as TIMESTAMP) AS updated_date,
        row_number() over (partition by id order by updated_date desc) = 1 AS is_most_recent_record
FROM source_rows
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select * from raw.zuora_product_rate_plan_data
    where _fivetran_deleted is null or _fivetran_deleted = false
),
final as (
    select
        id as product_rate_plan_id,
        created_by_id,
        cast(created_date as TIMESTAMP) as created_date,
        description,
        effective_end_date,
        effective_start_date,
        name,
        product_id,
        updated_by_id,
        cast(updated_date as TIMESTAMP) as updated_date,
        row_number() over (partition by id order by updated_date desc) = 1 as is_most_recent_record
    from base
)
select * from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 505 | 505 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"product_rate_plan_id":"0061f009500e40478ff6e5b65918cb50"}</code> |
| K2 | <code>{"product_rate_plan_id":"019629ba9fdd4961afb3fabdefc0d431"}</code> |
| K3 | <code>{"product_rate_plan_id":"02482cba1f394e35ba591f004b217add"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| product_rate_plan_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_by_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| effective_end_date | 501 | 501 | 501 | DATE | VARCHAR |
| effective_start_date | 501 | 501 | 501 | DATE | VARCHAR |
| name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| product_id | 505 | 505 | 505 | VARCHAR | VARCHAR |
| is_most_recent_record | 0 | 0 | 0 | BOOLEAN | BOOLEAN |

effective_end_date 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2028-06-11 | 2028-06-11 08:38:38.000000 |
| K2 | 2027-02-17 | 2027-02-17 12:40:14.000000 |
| K3 | 2025-09-07 | 2025-09-07 10:39:21.000000 |

effective_start_date 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2016-12-20 | 2016-12-20 17:07:00.000000 |
| K2 | 2015-01-31 | 2015-01-31 23:41:55.000000 |
| K3 | 2017-05-08 | 2017-05-08 18:32:23.000000 |

product_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0061f009500e40478ff6e5b65918cb50 | dff38ac0c94b11b94a7a297293d10e08 |
| K2 | 019629ba9fdd4961afb3fabdefc0d431 | 2c92c0946736733a016750d344222932 |
| K3 | 02482cba1f394e35ba591f004b217add | 2c92c0946736733a016750d344222932 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"is_most_recent_record","value":"true"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["product_rate_plan_id","product_id"],"nonnull_equal_rows":505,"meaning_status":"契约未描述含义差别"}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；task_instruction_not_agent_report       business_logic: Read from staging.stg_zuora__product_rate_plan and keep only rows where is_most_recent_record is TRUE; rows where the flag is FALSE or NULL are excluded.</code> |

## 轨迹索引（不放输出原文）

本题事件总数：73；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print -exec sh -c 'echo --- $1; wc -l "$1"' _ {} \; &amp;&amp; cat config/layer_dependencies.yaml</code> | 3638 | true | false |
| 13 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('zuora_start.duckdb',read_only=True)<br>print(c.execute("select table_name from information_schema.tables where table_schema='raw'").fetchall())<br>for t, in </code> | 39412 | false | false |
| 15 | run | <code>python3 - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(len(x['staging_contract']['tables']), [t['name'] for t in x['staging_contract']['tables']])<br>print('inter', [m['name</code> | 1273 | true | false |
| 17 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb,yaml<br>c=duckdb.connect('zuora_start.duckdb',read_only=True)<br>y=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in y['staging_contract']['tables']:<br> raw=t['source_tab</code> | 3209 | true | false |
| 27 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb,glob<br>c=duckdb.connect(':memory:'); c.execute('ATTACH \'zuora_start.duckdb\' AS src_db')<br># import raw alias relevant exact as run logic<br>for tbl, in c.execute("select tabl</code> | 3906 | true | false |
| 29 | run | <code>cat &gt; /tmp/build_models.py &lt;&lt;'PY'<br>from pathlib import Path<br>P=Path('sql/intermediate')<br>pass_models={<br>'int_zuora__account_current':('stg_zuora__account','is_most_recent_record = TRUE'),<br>'int_zuora__cont</code> | 0 | false | false |
| 31 | run | <code>python3 run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 8482 | true | false |
| 51 | run | <code>python3 run.py &gt; /tmp/runlog 2&gt;&amp;1; grep -E 'ERROR&#124;WARNING:&#124;✓&#124;Execution failed&#124;successfully' /tmp/runlog &#124; tail -80</code> | 3588 | true | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
'int_zuora__product_rate_plan_current':('stg_zuora__product_rate_plan','is_most_recent_record = TRUE'),
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-030.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__product_rate_plan.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__product_rate_plan.sql`
- S6: `records/006_contract_impl-030.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/result.md`
- S10: `data/024_packages_work/024_impl-030_stg_zuora__product_rate_plan/024_impl-030_stg_zuora__product_rate_plan.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/zuora.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions`
