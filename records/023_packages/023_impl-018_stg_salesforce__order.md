# impl-018 | staging | stg_salesforce__order | 差异：S1；日期 原记录

## 契约完整原文

S3:787–854

```yaml
    - name: stg_salesforce__order
      description: "Cleaned order records with validated order information and status"
      source_table: raw.order_data
      columns:
        - name: order_id
          data_type: VARCHAR
        - name: account_id
          data_type: VARCHAR
        - name: activated_by_id
          data_type: VARCHAR
        - name: activated_date
          data_type: TIMESTAMP
        - name: billing_city
          data_type: VARCHAR
        - name: billing_country
          data_type: VARCHAR
        - name: billing_postal_code
          data_type: VARCHAR
        - name: billing_state
          data_type: VARCHAR
        - name: billing_street
          data_type: VARCHAR
        - name: company_authorized_by_id
          data_type: VARCHAR
        - name: contract_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
        - name: customer_authorized_by_id
          data_type: VARCHAR
        - name: order_description
          data_type: VARCHAR
        - name: effective_date
          data_type: DATE
        - name: end_date
          data_type: DATE
        - name: is_deleted
          data_type: BOOLEAN
          validation_rules:
            - rule: "NOT COALESCE(is_deleted, false)"
              on_failure: delete_row
        - name: last_modified_date
          data_type: TIMESTAMP
        - name: order_number
          data_type: VARCHAR
        - name: original_order_id
          data_type: VARCHAR
        - name: owner_id
          data_type: VARCHAR
        - name: status
          data_type: VARCHAR
        - name: total_amount
          data_type: DECIMAL
        - name: pricebook_2_id
          data_type: VARCHAR
        - name: shipping_city
          data_type: VARCHAR
        - name: shipping_country
          data_type: VARCHAR
        - name: shipping_postal_code
          data_type: VARCHAR
        - name: shipping_state
          data_type: VARCHAR
        - name: shipping_street
          data_type: VARCHAR
        - name: type
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
select
      id as order_id,
      id as account_id,
      activated_by_id as activated_by_id,
      try_cast(activated_date as TIMESTAMP) as activated_date,
      billing_city as billing_city,
      billing_country as billing_country,
      billing_postal_code as billing_postal_code,
      billing_state as billing_state,
      billing_street as billing_street,
      company_authorized_by_id as company_authorized_by_id,
      contract_id as contract_id,
      try_cast(created_date as TIMESTAMP) as created_date,
      customer_authorized_by_id as customer_authorized_by_id,
      description as order_description,
      try_cast(effective_date as DATE) as effective_date,
      try_cast(end_date as DATE) as end_date,
      is_deleted as is_deleted,
      try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
      order_number as order_number,
      original_order_id as original_order_id,
      owner_id as owner_id,
      status as status,
      try_cast(total_amount as DECIMAL) as total_amount,
      pricebook_2_id as pricebook_2_id,
      shipping_city as shipping_city,
      shipping_country as shipping_country,
      shipping_postal_code as shipping_postal_code,
      shipping_state as shipping_state,
      shipping_street as shipping_street,
      "type" as type
from raw.order_data
```

## gold SQL（仅供定位差异）

S5

```sql
with fields as (
    select *
    from raw.order_data
), 

final as (
    select
        cast(id as varchar) as order_id,
        cast(account_id as varchar) as account_id,
        cast(activated_by_id as varchar) as activated_by_id,
        cast(activated_date as timestamp) as activated_date,
        cast(billing_city as varchar) as billing_city,
        cast(billing_country as varchar) as billing_country,
        cast(billing_postal_code as varchar) as billing_postal_code,
        cast(billing_state as varchar) as billing_state,
        cast(billing_street as varchar) as billing_street,
        cast(company_authorized_by_id as varchar) as company_authorized_by_id,
        cast(contract_id as varchar) as contract_id,
        cast(created_date as timestamp) as created_date,
        cast(customer_authorized_by_id as varchar) as customer_authorized_by_id,
        cast(description as varchar) as order_description,
        cast(effective_date as date) as effective_date,
        cast(end_date as date) as end_date,
        cast(coalesce(is_deleted, false) as boolean) as is_deleted,
        cast(last_modified_date as timestamp) as last_modified_date,
        cast(order_number as varchar) as order_number,
        cast(original_order_id as varchar) as original_order_id,
        cast(owner_id as varchar) as owner_id,
        cast(pricebook_2_id as varchar) as pricebook_2_id,
        cast(shipping_city as varchar) as shipping_city,
        cast(shipping_country as varchar) as shipping_country,
        cast(shipping_postal_code as varchar) as shipping_postal_code,
        cast(shipping_state as varchar) as shipping_state,
        cast(shipping_street as varchar) as shipping_street,
        cast(status as varchar) as status,
        cast(total_amount as decimal) as total_amount,
        cast(type as varchar) as type
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
| K1 | <code>{"order_id":"80101wgbfcbfwuf"}</code> |
| K2 | <code>{"order_id":"801025fvcjumc2d"}</code> |
| K3 | <code>{"order_id":"80104o21pm4y1jh"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 3000 | 3000 | 3000 | VARCHAR | VARCHAR |
| activated_by_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| activated_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| billing_city | 0 | 0 | 0 | VARCHAR | VARCHAR |
| billing_country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| billing_postal_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| billing_state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| billing_street | 0 | 0 | 0 | VARCHAR | VARCHAR |
| company_authorized_by_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| contract_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| customer_authorized_by_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_deleted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| last_modified_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| order_number | 0 | 0 | 0 | VARCHAR | VARCHAR |
| original_order_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| owner_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| pricebook_2_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| shipping_city | 0 | 0 | 0 | VARCHAR | VARCHAR |
| shipping_country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| shipping_postal_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| shipping_state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| shipping_street | 0 | 0 | 0 | VARCHAR | VARCHAR |
| status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| total_amount | 0 | 0 | 0 | DECIMAL(18,3) | DECIMAL(18,3) |
| type | 0 | 0 | 0 | VARCHAR | VARCHAR |

account_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 80101WgbfCBFwUf | 001xgV4ardEQzGv |
| K2 | 801025fvcJUMC2D | 0019gTLX3JwHTWh |
| K3 | 80104o21pm4Y1jh | 001y7ZJWpHLzsj4 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>1列；[{"column":"original_order_id","table_rows":3000}]</code> |
| A3_constant_nonnull_column | <code>1列；[{"column":"is_deleted","value":"false"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["order_id","account_id"],"nonnull_equal_rows":3000,"meaning_status":"契约未描述含义差别"}]</code> |

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
| 35 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>src=yaml.safe_load(open('salesforce_start.yaml')); co=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']['tables']<br>mp={'account_id':'id','account_name':'na</code> | 847 | true | false |
| 43 | run | <code>tail -180 /tmp/run2.log; grep -E '✗&#124;ERROR&#124;layer complete' /tmp/run2.log</code> | 15611 | true | false |
| 49 | run | <code>for f in sql/staging/*.sql; do echo ==== $f; grep -E 'md5&#124;history_unique_key&#124;created_date as&#124;last_modified_date' $f; done; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=</code> | 14873 | true | false |
| 63 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml,pathlib<br>c=duckdb.connect('salesforce.duckdb',read_only=True)<br>con=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer, schema, key in [('staging_contract','stag</code> | 589 | true | false |
| 67 | run | <code>for f in sql/staging/*.sql; do printf '%-55s ' "$(basename "$f")"; sed -n '2p' "$f"; done</code> | 1156 | true | false |
| 89 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=True); spec=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in spec['staging_contract']['tables']:<br> name=t['name</code> | 1149 | true | false |

### agent action 的 thought/message 命中原句

未找到命中原句。

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-018.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__order.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__order.sql`
- S6: `records/006_contract_impl-018.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/.tmp/result.md`
- S10: `data/023_packages_work/023_impl-018_stg_salesforce__order/023_impl-018_stg_salesforce__order.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions`
