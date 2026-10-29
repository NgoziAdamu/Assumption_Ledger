# impl-018 | staging | stg_salesforce__opportunity_line_item | 差异：S1；日期 原记录

## 契约完整原文

S3:747–786

```yaml
    - name: stg_salesforce__opportunity_line_item
      description: "Cleaned opportunity line item records with validated product and pricing information"
      source_table: raw.opportunity_line_item
      columns:
        - name: opportunity_line_item_id
          data_type: VARCHAR
        - name: opportunity_id
          data_type: VARCHAR
        - name: product_2_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
        - name: opportunity_line_item_description
          data_type: VARCHAR
        - name: has_quantity_schedule
          data_type: BOOLEAN
        - name: has_revenue_schedule
          data_type: BOOLEAN
        - name: is_deleted
          data_type: BOOLEAN
          validation_rules:
            - rule: "NOT COALESCE(is_deleted, false)"
              on_failure: delete_row
        - name: last_modified_date
          data_type: TIMESTAMP
        - name: list_price
          data_type: DECIMAL
        - name: pricebook_entry_id
          data_type: VARCHAR
        - name: quantity
          data_type: DECIMAL
        - name: service_date
          data_type: DATE
        - name: sort_order
          data_type: INTEGER
        - name: total_price
          data_type: DECIMAL
        - name: unit_price
          data_type: DECIMAL

```

## agent 最终 SQL

S4

```sql
select
      id as opportunity_line_item_id,
      id as opportunity_id,
      id as product_2_id,
      try_cast(created_date as TIMESTAMP) as created_date,
      description as opportunity_line_item_description,
      has_quantity_schedule as has_quantity_schedule,
      has_revenue_schedule as has_revenue_schedule,
      is_deleted as is_deleted,
      try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
      try_cast(list_price as DECIMAL) as list_price,
      pricebook_entry_id as pricebook_entry_id,
      try_cast(quantity as DECIMAL) as quantity,
      try_cast(service_date as DATE) as service_date,
      try_cast(sort_order as INTEGER) as sort_order,
      try_cast(total_price as DECIMAL) as total_price,
      try_cast(unit_price as DECIMAL) as unit_price
from raw.opportunity_line_item
where id is not null
```

## gold SQL（仅供定位差异）

S5

```sql
with fields as (
    select *
    from raw.opportunity_line_item
), 

final as (
    select
        cast(id as varchar) as opportunity_line_item_id,
        cast(opportunity_id as varchar) as opportunity_id,
        cast(product_2_id as varchar) as product_2_id,
        cast(created_date as timestamp) as created_date,
        cast(description as varchar) as opportunity_line_item_description,
        cast(coalesce(has_quantity_schedule, false) as boolean) as has_quantity_schedule,
        cast(coalesce(has_revenue_schedule, false) as boolean) as has_revenue_schedule,
        cast(coalesce(is_deleted, false) as boolean) as is_deleted,
        cast(last_modified_date as timestamp) as last_modified_date,
        cast(list_price as decimal) as list_price,
        cast(pricebook_entry_id as varchar) as pricebook_entry_id,
        cast(quantity as decimal) as quantity,
        cast(service_date as date) as service_date,
        cast(sort_order as integer) as sort_order,
        cast(total_price as decimal) as total_price,
        cast(unit_price as decimal) as unit_price
    from fields
)

select *
from final
where not coalesce(is_deleted, false)
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 3000 | 3000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"opportunity_line_item_id":"00k029dqfahx6ne"}</code> |
| K2 | <code>{"opportunity_line_item_id":"00k031neiuy8t7u"}</code> |
| K3 | <code>{"opportunity_line_item_id":"00k03mk8nktyeqn"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| opportunity_id | 3000 | 3000 | 3000 | VARCHAR | VARCHAR |
| product_2_id | 3000 | 3000 | 3000 | VARCHAR | VARCHAR |
| created_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| has_quantity_schedule | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| has_revenue_schedule | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_deleted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| last_modified_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| list_price | 0 | 0 | 0 | DECIMAL(18,3) | DECIMAL(18,3) |
| pricebook_entry_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| quantity | 0 | 0 | 0 | DECIMAL(18,3) | DECIMAL(18,3) |
| service_date | 0 | 0 | 0 | DATE | DATE |
| sort_order | 0 | 0 | 0 | INTEGER | INTEGER |
| total_price | 0 | 0 | 0 | DECIMAL(18,3) | DECIMAL(18,3) |
| unit_price | 0 | 0 | 0 | DECIMAL(18,3) | DECIMAL(18,3) |

opportunity_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 00k029DQfAHx6ne | 006qOaMamPeRpWP |
| K2 | 00k031NEIUy8T7U | 006xzqLEcGYSYmZ |
| K3 | 00k03MK8NKTyEQn | 006neRhwd0tjLlF |

product_2_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 00k029DQfAHx6ne | 01tmdUhPdsLSok7 |
| K2 | 00k031NEIUy8T7U | 01tIDWfK9qMB7tQ |
| K3 | 00k03MK8NKTyEQn | 01tSH1dHUrvv9z3 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"is_deleted","value":"false"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["opportunity_line_item_id","opportunity_id","product_2_id"],"nonnull_equal_rows":3000,"meaning_status":"契约未描述含义差别"}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory  if n=='stg_salesforce__opportunity_line_item': filters=['id is not null']</code> |

## 轨迹索引（不放输出原文）

本题事件总数：101；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,220p' run.py</code> | 11932 | true | false |
| 13 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>s=yaml.safe_load(open('salesforce_start.yaml'))<br>for t,c in s.items(): print(t,', '.join(c))<br>PY</code> | 8872 | false | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print([t['name'] for t in x['staging_contract']['tables']])<br>for t in x['staging_contract']['tables']:<br> print(t['name'], [c</code> | 6786 | true | false |
| 17 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('salesforce_start.duckdb',read_only=True)<br>for t in ['account','contact','opportunity','user','lead','task','event','user_role','product_2','opportunity_l</code> | 31400 | false | false |
| 19 | run | <code>mkdir -p sql/staging sql/intermediate sql/marts; cat &gt; /tmp/build.py &lt;&lt;'PY'<br>import yaml, pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))<br>source=yaml.safe_load(open('salesforce_start.y</code> | 0 | false | false |
| 31 | run | <code>cat &gt; sql/marts/salesforce__opportunity_line_item_enhanced.sql &lt;&lt;'SQL'<br>with line_items as (<br> select oli.*,opp.opportunity_name,opp.account_id,opp.owner_id as opportunity_owner_id,opp.stage_name,opp.cl</code> | 0 | false | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>src=yaml.safe_load(open('salesforce_start.yaml')); co=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']['tables']<br>mp={'account_id':'id','account_name':'na</code> | 847 | true | false |
| 43 | run | <code>tail -180 /tmp/run2.log; grep -E '✗&#124;ERROR&#124;layer complete' /tmp/run2.log</code> | 15611 | true | false |
| 49 | run | <code>for f in sql/staging/*.sql; do echo ==== $f; grep -E 'md5&#124;history_unique_key&#124;created_date as&#124;last_modified_date' $f; done; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=</code> | 14873 | true | false |
| 63 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml,pathlib<br>c=duckdb.connect('salesforce.duckdb',read_only=True)<br>con=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer, schema, key in [('staging_contract','stag</code> | 589 | true | false |
| 67 | run | <code>for f in sql/staging/*.sql; do printf '%-55s ' "$(basename "$f")"; sed -n '2p' "$f"; done</code> | 1156 | true | false |
| 89 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=True); spec=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in spec['staging_contract']['tables']:<br> name=t['name</code> | 1149 | true | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
 if n=='stg_salesforce__opportunity_line_item': filters=['id is not null']
```
event 31 / message

```text
 from staging.stg_salesforce__opportunity_line_item oli
```

## result.md 本表名原句

未找到 result.md。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-018.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__opportunity_line_item.sql`
- S6: `records/006_contract_impl-018.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `records/012_packages/012_impl-018_staging_stg_salesforce__opportunity_line_item.json`
- S10: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`
- S11: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`
- S12: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions`
