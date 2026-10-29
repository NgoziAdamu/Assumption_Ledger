# impl-004 | marts | salesforce__account_daily_history | 差异：S1；日期 原记录

## 契约完整原文

S3:705–762

```yaml
    - name: salesforce__account_daily_history
      description: Daily snapshots of Salesforce account history, keeping the latest change per account per calendar day
      grain: One row per account_id per snapshot_date
      source_models:
      - staging.stg_salesforce__account_history
      business_logic: '- Read all records from staging.stg_salesforce__account_history. - Exclude records marked as deleted. - For each account and calendar day (based on the date part of created_date), sort records by created_date in descending order and keep the first record; if multiple records share the exact same created_date within that day, the choice among them is not deterministic. - Define snapshot_date as the calendar date of created_date from the kept record. - All other fields are taken directly from the kept record without transformation or aggregation; data types are preserved and NULLs are retained. - The final result is ordered by account_id and snapshot_date for readability only.'
      columns:
      - name: account_id
        data_type: VARCHAR
        description: Salesforce Account ID for the snapshot.
      - name: snapshot_date
        data_type: DATE
        description: Calendar date of the kept change for the account; one row per account and date; ties on identical created timestamps that day are non-deterministic.
      - name: account_name
        data_type: VARCHAR
        description: Account name from the kept change that day.
      - name: account_source
        data_type: VARCHAR
        description: Account source from the kept change that day.
      - name: industry
        data_type: VARCHAR
        description: Industry from the kept change that day.
      - name: annual_revenue
        data_type: DECIMAL(18,3)
        description: Annual revenue from the kept change that day.
      - name: number_of_employees
        data_type: INTEGER
        description: Employee count from the kept change that day.
      - name: owner_id
        data_type: VARCHAR
        description: Owner user ID from the kept change that day.
      - name: type
        data_type: VARCHAR
        description: Account type from the kept change that day.
      - name: billing_city
        data_type: VARCHAR
        description: Billing city from the kept change that day.
      - name: billing_state
        data_type: VARCHAR
        description: Billing state from the kept change that day.
      - name: billing_country
        data_type: VARCHAR
        description: Billing country from the kept change that day.
      - name: website
        data_type: VARCHAR
        description: Website from the kept change that day.
      - name: rating
        data_type: VARCHAR
        description: Rating from the kept change that day.
      - name: ownership
        data_type: VARCHAR
        description: Ownership from the kept change that day.
      - name: parent_id
        data_type: VARCHAR
        description: Parent account ID from the kept change that day.
      - name: last_activity_date
        data_type: DATE
        description: Last activity date from the kept change that day.
```

## agent 最终 SQL

S4

```sql
WITH history_rows AS (
    SELECT
        account_id,
        CAST(created_date AS DATE) AS snapshot_date,
        account_name,
        account_source,
        industry,
        annual_revenue,
        number_of_employees,
        owner_id,
        type,
        billing_city,
        billing_state,
        billing_country,
        website,
        rating,
        ownership,
        parent_id,
        last_activity_date,
        created_date
    FROM staging.stg_salesforce__account_history
    WHERE COALESCE(is_deleted, FALSE) = FALSE
),
ranked_history AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY account_id, snapshot_date
            ORDER BY created_date DESC
        ) AS row_num
    FROM history_rows
)
SELECT
    account_id,
    snapshot_date,
    account_name,
    account_source,
    industry,
    annual_revenue,
    number_of_employees,
    owner_id,
    type,
    billing_city,
    billing_state,
    billing_country,
    website,
    rating,
    ownership,
    parent_id,
    last_activity_date
FROM ranked_history
WHERE row_num = 1
ORDER BY account_id, snapshot_date
```

## gold SQL（仅供定位差异）

S5

```sql
with account_history as (
    select *
    from staging.stg_salesforce__account_history
),

daily_snapshots as (
    select 
        account_id,
        created_date::date as snapshot_date,
        account_name,
        account_source,
        industry,
        annual_revenue,
        number_of_employees,
        owner_id,
        type,
        billing_city,
        billing_state,
        billing_country,
        website,
        rating,
        ownership,
        parent_id,
        last_activity_date,
        -- Add row number to handle multiple changes per day
        row_number() over (partition by account_id, created_date::date order by created_date desc) as daily_rank
    from account_history
    where not is_deleted
)

select 
    account_id,
    snapshot_date,
    account_name,
    account_source,
    industry,
    annual_revenue,
    number_of_employees,
    owner_id,
    type,
    billing_city,
    billing_state,
    billing_country,
    website,
    rating,
    ownership,
    parent_id,
    last_activity_date
from daily_snapshots
where daily_rank = 1  -- Keep only the latest change per day
order by account_id, snapshot_date
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1985 | 1985 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"account_id":"00105excmyam2m5","owner_id":"005cesi7eaz3awk","parent_id":"001dikfdgv70llx"}</code> |
| K2 | <code>{"account_id":"0010sl1d5r9kbkt","owner_id":"005ogrpwle5me3e","parent_id":"null"}</code> |
| K3 | <code>{"account_id":"00112twwk7qdnnf","owner_id":"0055kdfi2h7wc98","parent_id":"null"}</code> |
| K4 | <code>{"account_id":"00113pgctnxjx6e","owner_id":"005ynmwe8ybgqxk","parent_id":"null"}</code> |
| K5 | <code>{"account_id":"0010ctbeciboise","owner_id":"0051oewoezghrxx","parent_id":"null"}</code> |
| K6 | <code>{"account_id":"00115xdymjslgzg","owner_id":"0058xxblezcc8n4","parent_id":"null"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| snapshot_date | 0 | 0 | 0 | DATE | DATE |
| account_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_source | 0 | 0 | 0 | VARCHAR | VARCHAR |
| industry | 0 | 0 | 0 | VARCHAR | VARCHAR |
| annual_revenue | 295 | 295 | 295 | DECIMAL(18,3) | DECIMAL(18,3) |
| number_of_employees | 333 | 333 | 333 | INTEGER | INTEGER |
| owner_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| billing_city | 0 | 0 | 0 | VARCHAR | VARCHAR |
| billing_state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| billing_country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| website | 0 | 0 | 0 | VARCHAR | VARCHAR |
| rating | 278 | 278 | 278 | VARCHAR | VARCHAR |
| ownership | 0 | 0 | 0 | VARCHAR | VARCHAR |
| parent_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| last_activity_date | 410 | 410 | 410 | DATE | DATE |

annual_revenue 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 69743456.000 | 69954499.000 |
| K2 | 59835935.000 | 60071082.000 |
| K3 | 57557289.000 | 58325953.000 |

number_of_employees 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 111 | 29 |
| K2 | 1316 | 1314 |
| K4 | 628 | 613 |

rating 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K5 | Hot | Cold |
| K4 | null | Hot |
| K6 | null | Hot |

last_activity_date 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2021-02-02 | 2021-06-06 |
| K5 | 2024-03-19 | 2024-06-17 |
| K2 | 2025-02-20 | 2024-12-24 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

没有 True 痕迹。

## 轨迹索引（不放输出原文）

本题事件总数：53；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/.events/sessions/024a80d8-934c-43-4e69514191069ca/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print -exec wc -l {} \; &amp;&amp; cat config/layer_dependencies.yaml</code> | 1475 | true | false |
| 11 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print('tables', [a['name'] for a in x['staging_contract']['tables']])<br>print('intermediate', [a['name'] for a in x['modelin</code> | 354 | true | false |
| 21 | run | <code>cat &gt; sql/marts/salesforce__account_daily_history.sql &lt;&lt;'SQL'<br>WITH history_rows AS (<br>    SELECT<br>        account_id,<br>        CAST(created_date AS DATE) AS snapshot_date,<br>        account_name,<br>        a</code> | 6930 | true | false |
| 31 | run | <code>python - &lt;&lt;'PY'<br>import duckdb, pathlib<br>c=duckdb.connect('salesforce_start.duckdb')<br>for schema in ('staging','intermediate','marts'): c.execute(f'create schema if not exists {schema}')<br>for layer in ('s</code> | 639 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_salesforce__contact.sql'; s=open(p).read().replace('CAST("created_date" AS TIMESTAMP) AS created_date','CAST(NULL AS TIMESTAMP) AS created_date'); open(p,'w').write(</code> | 501 | true | false |
| 39 | run | python run.py | 6107 | true | false |
| 41 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已根据 `docs/data_contract.yaml` 与 `config/layer_dependencies.yaml` 完成 Salesforce SQL pipeline，实现顺序为 staging → intermediate → marts，SQL 位</code> | 82 | false | false |
| 43 | run | <code>ls -ld /workspace /tmp &amp;&amp; cat &gt; result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已根据 `docs/data_contract.yaml` 与 `config/layer_dependencies.yaml` 完成 Salesforce SQL pipeline，实现顺序为 staging → intermediate → marts，SQL 位于规定的 `sq</code> | 169 | false | false |
| 47 | run | <code>id &amp;&amp; cat &gt; .tmp/report/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已根据 `docs/data_contract.yaml` 与 `config/layer_dependencies.yaml` 完成 Salesforce SQL pipeline，实现顺序为 staging → intermediate → marts，SQL 位于规定的 `sql/&lt;layer</code> | 153 | false | false |
| 49 | run | <code>cp .tmp/report/result.md result.md &amp;&amp; cat result.md</code> | 1797 | true | false |

### agent action 的 thought/message 命中原句

event 21 / message

```text
Running command: cat > sql/marts/salesforce__account_daily_history.sql <<'SQL'
```
event 41 / message

```text
| Marts | `salesforce__account_daily_history` | 3,000 |
```
event 43 / message

```text
| Marts | `salesforce__account_daily_history` | 3,000 |
```
event 47 / message

```text
| Marts | `salesforce__account_daily_history` | 3,000 |
```

## result.md 本表名原句

S9:19

```text
| Marts | `salesforce__account_daily_history` | 3,000 |
```

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-004.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-004/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/sql/marts/salesforce__account_daily_history.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/sql/marts/salesforce__account_daily_history.sql`
- S6: `records/006_contract_impl-004.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/result.md`
- S10: `data/019_packages_work/019_impl-004_salesforce__account_daily_history/019_impl-004_salesforce__account_daily_history.json`
- S11: `data/005_cs_work/impl-004/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/.events/sessions`
