# impl-024 | staging | stg_tiktok_ads__advertiser | 差异：S1；日期 原记录

## 契约完整原文

S3:40–94

```yaml
    - name: stg_tiktok_ads__advertiser
      description: "Cleaned advertiser master data with normalized contact fields and type-safe numeric conversions."
      source_table: raw.tiktok_advertiser_data
      columns:
        - name: source_relation
          data_type: VARCHAR
        - name: advertiser_id
          data_type: VARCHAR
        - name: address
          data_type: VARCHAR
        - name: balance
          data_type: DOUBLE
          validation_rules:
            - rule: "balance is numeric"
              on_failure: nullify_field
        - name: company
          data_type: VARCHAR
        - name: contacter
          data_type: VARCHAR
        - name: country
          data_type: VARCHAR
        - name: currency
          data_type: VARCHAR
        - name: description
          data_type: VARCHAR
        - name: email
          data_type: VARCHAR
          validation_rules:
            - rule: "email normalized to lowercase and trimmed"
              on_failure: correct
            - rule: "email matches standard pattern (local@domain.tld)"
              on_failure: nullify_field
        - name: industry
          data_type: VARCHAR
        - name: language
          data_type: VARCHAR
        - name: advertiser_name
          data_type: VARCHAR
          validation_rules:
            - rule: "name trimmed"
              on_failure: correct
            - rule: "name length between 3 and 100 and only alphanumeric plus spaces"
              on_failure: nullify_field
        - name: cellphone_number
          data_type: VARCHAR
          validation_rules:
            - rule: "strip non-digit characters except leading '+'"
              on_failure: correct
            - rule: "must conform to E.164 format"
              on_failure: nullify_field
        - name: telephone_number
          data_type: VARCHAR
        - name: timezone
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
with source_data as (
    select * from raw.tiktok_advertiser_data
)
select
        'tiktok_ads' as source_relation,
        cast("ID" as VARCHAR) as advertiser_id,
        cast("ADDRESS" as VARCHAR) as address,
        try_cast(nullif(trim("BALANCE"), '') as DOUBLE) as balance,
        cast("COMPANY" as VARCHAR) as company,
        cast("CONTACTER" as VARCHAR) as contacter,
        cast("COUNTRY" as VARCHAR) as country,
        cast("CURRENCY" as VARCHAR) as currency,
        cast("DESCRIPTION" as VARCHAR) as description,
        case when regexp_matches(lower(trim("EMAIL")), '^[a-z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$') then lower(trim("EMAIL")) else null end as email,
        cast("INDUSTRY" as VARCHAR) as industry,
        cast("LANGUAGE" as VARCHAR) as language,
        case when length(trim("NAME")) between 3 and 100 and regexp_matches(trim("NAME"), '^[A-Za-z0-9 ]+$') then trim("NAME") else null end as advertiser_name,
        case when regexp_matches(regexp_replace(trim("CELLPHONE_NUMBER"), '[^0-9+]', '', 'g'), '^\+[1-9][0-9]{7,14}$') then regexp_replace(trim("CELLPHONE_NUMBER"), '[^0-9+]', '', 'g') else null end as cellphone_number,
        cast("TELEPHONE_NUMBER" as VARCHAR) as telephone_number,
        cast("TIMEZONE" as VARCHAR) as timezone
from source_data
```

## gold SQL（仅供定位差异）

S5

```sql
with raw_adv as (
  select
    'raw.tiktok_advertiser_data' as source_relation,
    "ID" as advertiser_id,
    "ADDRESS" as address,
    "BALANCE" as balance,
    "COMPANY" as company,
    "CONTACTER" as contacter,
    "COUNTRY" as country,
    "CURRENCY" as currency,
    "DESCRIPTION" as description,
    "EMAIL" as email,
    "INDUSTRY" as industry,
    "LANGUAGE" as language,
    "NAME" as name,
    "CELLPHONE_NUMBER" as cellphone_number,
    "TELEPHONE_NUMBER" as telephone_number,
    "TIMEZONE" as timezone
  from raw.tiktok_advertiser_data
), cleaned as (
  select
    source_relation,
    advertiser_id,
    address,
    try_cast(balance as double) as balance,
    company,
    contacter,
    country,
    currency,
    description,
    -- email normalization and validation
    case
      when regexp_full_match(lower(trim(email)), '^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$') then lower(trim(email))
      else null
    end as email,
    industry,
    language,
    -- name cleaning and validation
    case
      when name is null then null
      when length(trim(name)) between 3 and 100 and regexp_full_match(trim(name), '^[A-Za-z0-9 ]+$') then trim(name)
      else null
    end as advertiser_name,
    -- cellphone cleaning and validation (E.164)
    case
      when "CELLPHONE_NUMBER" is not null then regexp_replace("CELLPHONE_NUMBER", '[^0-9+]', '')
      else null
    end as cellphone_number_raw,
    telephone_number as telephone_number_raw,
    timezone
  from raw_adv
), final as (
  select
    source_relation,
    advertiser_id,
    address,
    balance,
    company,
    contacter,
    country,
    currency,
    description,
    email,
    industry,
    language,
    advertiser_name,
    case when cellphone_number_raw is not null and regexp_full_match(cellphone_number_raw, '^\+[1-9][0-9]{7,14}$') then cellphone_number_raw else null end as cellphone_number,
    telephone_number_raw as telephone_number,
    timezone
  from cleaned
)
select *
from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 200 | 200 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"advertiser_id":"12"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| advertiser_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| address | 0 | 0 | 0 | VARCHAR | VARCHAR |
| balance | 0 | 0 | 0 | DOUBLE | DOUBLE |
| company | 0 | 0 | 0 | VARCHAR | VARCHAR |
| contacter | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| currency | 0 | 0 | 0 | VARCHAR | VARCHAR |
| description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| email | 1 | 1 | 1 | VARCHAR | VARCHAR |
| industry | 0 | 0 | 0 | VARCHAR | VARCHAR |
| language | 0 | 0 | 0 | VARCHAR | VARCHAR |
| advertiser_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| telephone_number | 0 | 0 | 0 | VARCHAR | VARCHAR |
| timezone | 0 | 0 | 0 | VARCHAR | VARCHAR |

email 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | <code>adv12@sub..example.com</code> |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"source_relation","value":"tiktok_ads"}]</code> |
| B6_constant_literal_output | <code>1输出列；[{"column":"source_relation","expression":["'tiktok_ads'"]}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory print('staging advertiser email valid/non-null:',c.execute("select count(*) filter(where email is not null), count(*) from staging.stg_tiktok_ads__advertiser").fetchone())</code> |

## 轨迹索引（不放输出原文）

本题事件总数：65；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find sql -maxdepth 3 -type f -print &#124; sort &amp;&amp; echo '--- config ---' &amp;&amp; cat config/layer_dependencies.yaml</code> | 3033 | true | false |
| 11 | run | cat tiktok_ads_start.yaml | 4854 | false | false |
| 13 | run | <code>find sql -maxdepth 2 -type d -print; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('tiktok_ads_start.duckdb',read_only=True)<br>print(c.execute("select table_schema,table_name from information_schema.ta</code> | 377 | false | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('tiktok_ads_start.duckdb',read_only=True)<br>for t, in c.execute("select table_name from information_schema.tables where table_schema='raw'").fetchall():<br> p</code> | 10620 | false | false |
| 23 | run | <code>cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>import yaml<br>root=Path('sql')<br>for layer in ('staging','intermediate','marts'):(root/layer).mkdir(exist_ok=True)<br># Contract table specifications<br>numeric</code> | 256 | false | false |
| 31 | run | <code>sed -n '1,120p' sql/staging/stg_tiktok_ads__ad_report_hourly.sql &amp;&amp; sed -n '1,100p' sql/staging/stg_tiktok_ads__advertiser.sql</code> | 7570 | false | false |
| 37 | run | <code>cat &gt; /tmp/fixcampaign.py &lt;&lt;'PY'<br>from pathlib import Path<br>fields=[('source_relation',"'tiktok_ads'"),('campaign_id','CAMPAIGN_ID'),('updated_at','try_cast(nullif(trim(UPDATED_AT), \'\') as TIMESTAMP)'</code> | 3378 | true | false |
| 43 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('tiktok_ads.duckdb',read_only=True)<br>for schema,t in [('staging','stg_tiktok_ads__advertiser'),('staging','stg_tiktok_ads__campaign_history'),('staging','</code> | 457 | true | false |
| 49 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>from pathlib import Path<br>c=duckdb.connect('tiktok_ads.duckdb',read_only=True)<br>for layer, pref in [('staging','stg_'),('intermediate','int_'),('marts','tiktok_ads__')]:<br> p</code> | 1078 | true | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
'stg_tiktok_ads__advertiser':('tiktok_advertiser_data',{'advertiser_id':'ID','advertiser_name':'NAME'}),
```
event 31 / message

```text
Running command: sed -n '1,120p' sql/staging/stg_tiktok_ads__ad_report_hourly.sql && sed -n '1,100p' sql/staging/stg_tiktok_ads__advertiser.sql
```
event 43 / message

```text
for schema,t in [('staging','stg_tiktok_ads__advertiser'),('staging','stg_tiktok_ads__campaign_history'),('staging','stg_tiktok_ads__ad_group_history'),('staging','stg_tiktok_ads__ad_history'),('marts','tiktok_ads__ad_report'),('marts','tiktok_ads__campaign_country_report')]:
```
event 49 / message

```text
print('staging advertiser email valid/non-null:',c.execute("select count(*) filter(where email is not null), count(*) from staging.stg_tiktok_ads__advertiser").fetchone())
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-024.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-024/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/sql/staging/stg_tiktok_ads__advertiser.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/sql/staging/stg_tiktok_ads__advertiser.sql`
- S6: `records/006_contract_impl-024.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/result.md`
- S10: `records/012_packages/012_impl-024_staging_stg_tiktok_ads__advertiser.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/tiktok_ads.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/tiktok_ads.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions`
