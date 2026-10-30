# impl-013 | staging | stg_netsuite2__account_types | 差异：S1；日期 原记录

## 契约完整原文

S3:443–455

```yaml
    - name: stg_netsuite2__account_types
      description: "Account type classifications for chart of accounts structure"
      source_table: raw.netsuite2_account_type_data
      columns:
        - name: account_type_id
          data_type: BIGINT
          constraints: [not_null, unique]
        - name: type_name
          data_type: VARCHAR
        - name: is_balancesheet
          data_type: BOOLEAN
        - name: is_leftside
          data_type: BOOLEAN
```

## agent 最终 SQL

S4

```sql
WITH source_data AS (
    SELECT
    TRY_CAST(r."internalid" AS BIGINT) AS account_type_id,
    TRY_CAST(r."longname" AS VARCHAR) AS type_name,
    CASE WHEN lower(trim(cast(r."balancesheet" AS VARCHAR))) IN ('true','t','1','yes','y') THEN TRUE WHEN lower(trim(cast(r."balancesheet" AS VARCHAR))) IN ('false','f','0','no','n') THEN FALSE ELSE TRY_CAST(r."balancesheet" AS BOOLEAN) END AS is_balancesheet,
    CASE WHEN lower(trim(cast(r."left" AS VARCHAR))) IN ('true','t','1','yes','y') THEN TRUE WHEN lower(trim(cast(r."left" AS VARCHAR))) IN ('false','f','0','no','n') THEN FALSE ELSE TRY_CAST(r."left" AS BOOLEAN) END AS is_leftside
    FROM raw.netsuite2_account_type_data r
)
SELECT *
FROM source_data
WHERE account_type_id IS NOT NULL
```

## gold SQL（仅供定位差异）

S5

```sql
with base as (
    select distinct
        longname as type_name,
        "left" as is_leftside,
        balancesheet as is_balancesheet
    from raw.netsuite2_account_type_data
    -- Removed date_deleted filter for mock data OR date_deleted = ''
),

final as (
    select 
        row_number() over (order by type_name) as account_type_id,
        type_name,
        case when is_balancesheet = 'T' then true else false end as is_balancesheet,
        case when is_leftside = 'T' then true else false end as is_leftside
    from base
)

select *
from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 8 | 8 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"account_type_id":"1"}</code> |
| K2 | <code>{"account_type_id":"3"}</code> |
| K3 | <code>{"account_type_id":"4"}</code> |
| K4 | <code>{"account_type_id":"7"}</code> |
| K5 | <code>{"account_type_id":"6"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_type_id | 0 | 0 | 0 | BIGINT | BIGINT |
| type_name | 6 | 6 | 6 | VARCHAR | VARCHAR |
| is_balancesheet | 2 | 2 | 2 | BOOLEAN | BOOLEAN |
| is_leftside | 4 | 4 | 4 | BOOLEAN | BOOLEAN |

type_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Bank | Accounts Payable |
| K2 | Fixed Asset | Bank |
| K3 | Accounts Payable | Cost of Goods Sold |

is_balancesheet 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | true | false |
| K4 | false | true |

is_leftside 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | true | false |
| K3 | false | true |
| K5 | false | true |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

没有 True 痕迹。

## 轨迹索引（不放输出原文）

本题事件总数：67；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f &#124; sort &#124; wc -l; find sql -type f &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,220p' run.py</code> | 16959 | true | false |
| 9 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(len(c['staging_contract']['tables']),len(c['modeling_spec']['intermediate_models']),len(c['modeling_spec']['marts_mo</code> | 5234 | true | false |
| 11 | run | <code>cat test_single_sql.py; python - &lt;&lt;'PY'<br>import yaml<br>s=yaml.safe_load(open('netsuite_start.yaml'))<br>for table,cols in s.items():<br> print('\n',table,':', ', '.join(cols))<br>PY</code> | 16290 | false | false |
| 15 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/generate.py &lt;&lt;'PY'<br>import yaml, os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>raw=yaml.safe_load(open('netsuite_start.yaml'))<br># per-table</code> | 0 | false | false |

### agent action 的 thought/message 命中原句

event 15 / message

```text
'stg_netsuite2__account_types':dict(account_type_id='internalid',type_name='longname',is_balancesheet='balancesheet',is_leftside='left'),
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-013.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/staging/stg_netsuite2__account_types.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/staging/stg_netsuite2__account_types.sql`
- S6: `records/006_contract_impl-013.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/result.md`
- S10: `data/022_packages_work/022_impl-013_stg_netsuite2__account_types/022_impl-013_stg_netsuite2__account_types.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/netsuite.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions`
