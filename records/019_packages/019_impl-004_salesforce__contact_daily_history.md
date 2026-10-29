# impl-004 | marts | salesforce__contact_daily_history | 差异：S1；日期 原记录

## 契约完整原文

S3:763–820

```yaml
    - name: salesforce__contact_daily_history
      description: Daily snapshots of Salesforce contacts, keeping the latest non-deleted change per contact per calendar date.
      grain: One row per (contact_id, snapshot_date)
      source_models:
      - staging.stg_salesforce__contact_history
      business_logic: '- Source rows from staging.stg_salesforce__contact_history and exclude records marked as deleted. - Derive snapshot_date as the calendar date from created_date by truncating the time component; no timezone conversion is applied. - For each (contact_id, snapshot_date), order changes by created_date descending and select the latest change of that day. - If multiple rows share the exact same created_date timestamp within a day, the selected row is arbitrary due to ties. - Project the selected row''s fields as-is: account_id, contact_name, first_name, last_name, email, phone, mobile_phone, title, lead_source, owner_id, mailing_city, mailing_state, mailing_country, mailing_postal_code, last_activity_date. - All values are pass-through with NULLs preserved; no formatting or normalization is applied. - Output is ordered by contact_id ascending, then snapshot_date ascending.'
      columns:
      - name: contact_id
        data_type: VARCHAR
        description: Salesforce contact ID used to group daily snapshots; pass-through from source.
      - name: snapshot_date
        data_type: DATE
        description: Calendar date derived from created_date by truncating the time component.
      - name: account_id
        data_type: VARCHAR
        description: Associated account ID at the selected daily change; pass-through.
      - name: contact_name
        data_type: VARCHAR
        description: Full contact name at the selected daily change; pass-through.
      - name: first_name
        data_type: VARCHAR
        description: First name at the selected daily change; pass-through.
      - name: last_name
        data_type: VARCHAR
        description: Last name at the selected daily change; pass-through.
      - name: email
        data_type: VARCHAR
        description: Email address at the selected daily change; pass-through without normalization.
      - name: phone
        data_type: VARCHAR
        description: Primary phone at the selected daily change; pass-through without reformatting.
      - name: mobile_phone
        data_type: VARCHAR
        description: Mobile phone at the selected daily change; pass-through.
      - name: title
        data_type: VARCHAR
        description: Job title at the selected daily change; pass-through.
      - name: lead_source
        data_type: VARCHAR
        description: Lead source at the selected daily change; pass-through.
      - name: owner_id
        data_type: VARCHAR
        description: Record owner (user) ID at the selected daily change; pass-through.
      - name: mailing_city
        data_type: VARCHAR
        description: Mailing city at the selected daily change; pass-through.
      - name: mailing_state
        data_type: VARCHAR
        description: Mailing state/province at the selected daily change; pass-through.
      - name: mailing_country
        data_type: VARCHAR
        description: Mailing country at the selected daily change; pass-through.
      - name: mailing_postal_code
        data_type: VARCHAR
        description: Mailing postal/ZIP code at the selected daily change; pass-through.
      - name: last_activity_date
        data_type: DATE
        description: Last activity date at the selected daily change; pass-through.
```

## agent 最终 SQL

S4

```sql
WITH history_rows AS (
    SELECT
        contact_id,
        CAST(created_date AS DATE) AS snapshot_date,
        account_id,
        contact_name,
        first_name,
        last_name,
        email,
        phone,
        mobile_phone,
        title,
        lead_source,
        owner_id,
        mailing_city,
        mailing_state,
        mailing_country,
        mailing_postal_code,
        last_activity_date,
        created_date
    FROM staging.stg_salesforce__contact_history
    WHERE COALESCE(is_deleted, FALSE) = FALSE
),
ranked_history AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY contact_id, snapshot_date
            ORDER BY created_date DESC
        ) AS row_num
    FROM history_rows
)
SELECT
    contact_id,
    snapshot_date,
    account_id,
    contact_name,
    first_name,
    last_name,
    email,
    phone,
    mobile_phone,
    title,
    lead_source,
    owner_id,
    mailing_city,
    mailing_state,
    mailing_country,
    mailing_postal_code,
    last_activity_date
FROM ranked_history
WHERE row_num = 1
ORDER BY contact_id, snapshot_date
```

## gold SQL（仅供定位差异）

S5

```sql
with contact_history as (
    select *
    from staging.stg_salesforce__contact_history
),

daily_snapshots as (
    select 
        contact_id,
        created_date::date as snapshot_date,
        account_id,
        contact_name,
        first_name,
        last_name,
        email,
        phone,
        mobile_phone,
        title,
        lead_source,
        owner_id,
        mailing_city,
        mailing_state,
        mailing_country,
        mailing_postal_code,
        last_activity_date,
        -- Add row number to handle multiple changes per day
        row_number() over (partition by contact_id, created_date::date order by created_date desc) as daily_rank
    from contact_history
    where not is_deleted
)

select 
    contact_id,
    snapshot_date,
    account_id,
    contact_name,
    first_name,
    last_name,
    email,
    phone,
    mobile_phone,
    title,
    lead_source,
    owner_id,
    mailing_city,
    mailing_state,
    mailing_country,
    mailing_postal_code,
    last_activity_date
from daily_snapshots
where daily_rank = 1  -- Keep only the latest change per day
order by contact_id, snapshot_date
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2369 | 2369 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"contact_id":"0030h6oj5srzddc","account_id":"001ycorp9lb0dpd","owner_id":"00529akxzfwnvpo","mailing_postal_code":"09023"}</code> |
| K2 | <code>{"contact_id":"0031h3efq9qrj0l","account_id":"001mgdxurye9wft","owner_id":"005rx8wx9dzubsk","mailing_postal_code":"59037"}</code> |
| K3 | <code>{"contact_id":"0031l6552guxlvp","account_id":"001gytptitqjv1g","owner_id":"005oz856npmmk7b","mailing_postal_code":"29738"}</code> |
| K4 | <code>{"contact_id":"0031cvkckthlt2k","account_id":"001jl2nyrupbrj7","owner_id":"005dkphpbokh6es","mailing_postal_code":"06462"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| snapshot_date | 0 | 0 | 0 | DATE | DATE |
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| contact_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| first_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| last_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| phone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mobile_phone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| title | 155 | 155 | 155 | VARCHAR | VARCHAR |
| lead_source | 0 | 0 | 0 | VARCHAR | VARCHAR |
| owner_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mailing_city | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mailing_state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| mailing_country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| last_activity_date | 288 | 288 | 288 | DATE | DATE |

title 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Training and development officer | Designer, fashion/clothing |
| K2 | Acupuncturist | International aid/development worker |
| K3 | Electrical engineer | Administrator, education |

last_activity_date 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2022-06-27 | 2024-04-01 |
| K4 | 2025-02-25 | 2023-12-05 |
| K2 | 2022-07-13 | 2024-11-04 |

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
cat > sql/marts/salesforce__contact_daily_history.sql <<'SQL'
```
event 41 / message

```text
| Marts | `salesforce__contact_daily_history` | 3,000 |
```
event 43 / message

```text
| Marts | `salesforce__contact_daily_history` | 3,000 |
```
event 47 / message

```text
| Marts | `salesforce__contact_daily_history` | 3,000 |
```

## result.md 本表名原句

S9:20

```text
| Marts | `salesforce__contact_daily_history` | 3,000 |
```

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-004.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-004/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/sql/marts/salesforce__contact_daily_history.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/sql/marts/salesforce__contact_daily_history.sql`
- S6: `records/006_contract_impl-004.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/dacomp-de-impl-004/result.md`
- S10: `data/019_packages_work/019_impl-004_salesforce__contact_daily_history/019_impl-004_salesforce__contact_daily_history.json`
- S11: `data/005_cs_work/impl-004/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-004/salesforce.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-004/agent/.events/sessions`
