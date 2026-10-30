# impl-018 | staging | stg_salesforce__lead | 差异：S1；日期 原记录

## 契约完整原文

S3:482–594

```yaml
    - name: stg_salesforce__lead
      description: "Cleaned prospect/lead records with validated contact information and lead qualification data"
      source_table: raw.lead
      columns:
        - name: lead_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: first_name
          data_type: VARCHAR
        - name: last_name
          data_type: VARCHAR
          constraints: [not_null]
        - name: lead_name
          data_type: VARCHAR
          constraints: [not_null]
        - name: email
          data_type: VARCHAR
        - name: company
          data_type: VARCHAR
        - name: title
          data_type: VARCHAR
        - name: phone
          data_type: VARCHAR
        - name: lead_source
          data_type: VARCHAR
        - name: status
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "status IS NOT NULL"
              on_failure: delete_row
            - rule: "status IN ('Open - Not Contacted', 'Working - Contacted', 'Closed - Converted', 'Closed - Not Converted')"
              on_failure: delete_row
            - rule: "status = TRIM(status)"
              on_failure: correct
        - name: owner_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: is_deleted
          data_type: BOOLEAN
        - name: lead_description
          data_type: VARCHAR
        - name: annual_revenue
          data_type: DECIMAL(18,3)
        - name: city
          data_type: VARCHAR
        - name: converted_account_id
          data_type: VARCHAR
        - name: converted_contact_id
          data_type: VARCHAR
        - name: converted_date
          data_type: TIMESTAMP
        - name: converted_opportunity_id
          data_type: VARCHAR
        - name: country
          data_type: VARCHAR
        - name: country_code
          data_type: VARCHAR
        - name: created_by_id
          data_type: VARCHAR
        - name: created_date
          data_type: TIMESTAMP
        - name: email_bounced_date
          data_type: TIMESTAMP
        - name: email_bounced_reason
          data_type: VARCHAR
        - name: fax
          data_type: VARCHAR
        - name: geocode_accuracy
          data_type: VARCHAR
        - name: has_opted_out_of_email
          data_type: BOOLEAN
        - name: industry
          data_type: VARCHAR
        - name: is_converted
          data_type: BOOLEAN
        - name: is_unread_by_owner
          data_type: BOOLEAN
        - name: last_activity_date
          data_type: DATE
        - name: last_modified_date
          data_type: TIMESTAMP
        - name: last_referenced_date
          data_type: TIMESTAMP
        - name: last_viewed_date
          data_type: TIMESTAMP
        - name: latitude
          data_type: DECIMAL(18,3)
        - name: longitude
          data_type: DECIMAL(18,3)
        - name: master_record_id
          data_type: VARCHAR
        - name: mobile_phone
          data_type: VARCHAR
        - name: number_of_employees
          data_type: INTEGER
        - name: photo_url
          data_type: VARCHAR
        - name: postal_code
          data_type: VARCHAR
        - name: salutation
          data_type: VARCHAR
        - name: state
          data_type: VARCHAR
        - name: state_code
          data_type: VARCHAR
        - name: street
          data_type: VARCHAR
        - name: system_modstamp
          data_type: TIMESTAMP
        - name: website
          data_type: VARCHAR

```

## agent 最终 SQL

S4

```sql
select
      id as lead_id,
      first_name as first_name,
      last_name as last_name,
      name as lead_name,
      email as email,
      company as company,
      title as title,
      phone as phone,
      lead_source as lead_source,
      trim(status) as status,
      owner_id as owner_id,
      is_deleted as is_deleted,
      description as lead_description,
      try_cast(annual_revenue as DECIMAL(18,3)) as annual_revenue,
      city as city,
      converted_account_id as converted_account_id,
      converted_contact_id as converted_contact_id,
      try_cast(converted_date as TIMESTAMP) as converted_date,
      converted_opportunity_id as converted_opportunity_id,
      country as country,
      country_code as country_code,
      created_by_id as created_by_id,
      try_cast(created_date as TIMESTAMP) as created_date,
      try_cast(email_bounced_date as TIMESTAMP) as email_bounced_date,
      email_bounced_reason as email_bounced_reason,
      fax as fax,
      geocode_accuracy as geocode_accuracy,
      has_opted_out_of_email as has_opted_out_of_email,
      industry as industry,
      is_converted as is_converted,
      is_unread_by_owner as is_unread_by_owner,
      try_cast(last_activity_date as DATE) as last_activity_date,
      try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
      try_cast(last_referenced_date as TIMESTAMP) as last_referenced_date,
      try_cast(last_viewed_date as TIMESTAMP) as last_viewed_date,
      try_cast(latitude as DECIMAL(18,3)) as latitude,
      try_cast(longitude as DECIMAL(18,3)) as longitude,
      master_record_id as master_record_id,
      mobile_phone as mobile_phone,
      try_cast(number_of_employees as INTEGER) as number_of_employees,
      photo_url as photo_url,
      postal_code as postal_code,
      salutation as salutation,
      state as state,
      state_code as state_code,
      street as street,
      try_cast(system_modstamp as TIMESTAMP) as system_modstamp,
      website as website
from raw.lead
where id is not null
  and last_name is not null
  and name is not null
  and trim(status) in ('Open - Not Contacted', 'Working - Contacted', 'Closed - Converted', 'Closed - Not Converted')
qualify row_number() over (partition by id order by id) = 1
```

## gold SQL（仅供定位差异）

S5

```sql
with fields as (
    select *
    from raw.lead
),

validated as (
    select
        *,

        -- Primary key validation
        case
            when id is null then 1
            when not (id ~ '^[A-Za-z0-9]{15,18}$') then 1
            else 0
        end as lead_id_validation_failed,

        -- Email validation - format and length per YAML spec
        case
            when email is null then 0 -- Optional field, null OK
            when trim(email) = '' then 0 -- Empty is OK
            when length(trim(email)) > 255 then 1 -- Too long per YAML spec
            when not (lower(trim(email)) ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') then 1 -- Invalid format
            else 0
        end as email_validation_failed,

        -- Phone number validation - basic format check per YAML spec
        case
            when phone is null then 0 -- Optional field, null OK
            when length(phone) > 50 then 1 -- Too long per YAML spec
            else 0
        end as phone_validation_failed,

        -- Mobile phone validation
        case
            when mobile_phone is null then 0 -- Optional field, null OK
            when length(mobile_phone) > 50 then 1 -- Too long per YAML spec
            else 0
        end as mobile_phone_validation_failed,

        -- Name validation - required field per YAML spec
        case
            when name is null then 1 -- Required field
            when trim(name) = '' then 1 -- Empty name not allowed
            when length(trim(name)) > 255 then 1 -- Length validation per YAML spec
            else 0
        end as lead_name_validation_failed,

        -- Company validation - business requirement
        case
            when company is null then 1 -- Required field per business rules
            when trim(company) = '' then 1 -- Empty company not allowed
            when length(trim(company)) > 255 then 1 -- Length validation
            else 0
        end as company_validation_failed,

        -- Owner ID foreign key validation
        case
            when owner_id is not null and not (owner_id ~ '^[A-Za-z0-9]{15,18}$') then 1
            when owner_id is not null and owner_id not in (select id from raw.user) then 1
            else 0
        end as owner_id_validation_failed,

        -- Status validation per YAML spec - validate against allowed values
        case
            when status is null then 0 -- Status can be null
            when trim(status) in ('Open', 'Closed - Converted', 'Closed - Not Converted') then 0 -- Valid values
            when trim(status) not in ('Open', 'Closed - Converted', 'Closed - Not Converted') then 1 -- Invalid values
            else 0
        end as status_validation_failed,

        -- Date validation - converted date validation per YAML spec
        case
            when converted_date is null then 0 -- Converted date can be null
            when converted_date < '1900-01-01' then 1 -- Too old per YAML spec
            when converted_date > current_date + interval '1 year' then 1 -- Too far future per YAML spec
            when converted_date < created_date::DATE then 1 -- Logical violation
            else 0
        end as converted_date_validation_failed,

        -- Annual revenue validation
        case
            when annual_revenue is null then 0 -- Annual revenue can be null
            when annual_revenue < 0 then 1 -- Negative revenue not allowed per YAML spec
            when annual_revenue > 999999999999.99 then 1 -- Revenue too large per YAML spec
            else 0
        end as annual_revenue_validation_failed,

        -- Website validation per YAML spec
        case
            when website is null then 0 -- Website can be null
            when length(website) > 255 then 1 -- Too long per YAML spec
            when not (website ~ '^https?://[A-Za-z0-9\-\.]+\.[A-Za-z]{2,}.*$') then 1 -- URL format validation
            else 0
        end as website_validation_failed

    from fields
),

final as (
    select
        case
            when lead_id_validation_failed = 1 then null
            else cast(id as varchar)
        end as lead_id,
        case
            when annual_revenue_validation_failed = 1 then null
            else cast(annual_revenue as decimal(18,2))  -- Per YAML spec precision
        end as annual_revenue,
        cast(trim(coalesce(city, '')) as varchar) as city,
        case
            when company_validation_failed = 1 then trim(company)
            else trim(company)
        end as company,
        cast(converted_account_id as varchar) as converted_account_id,
        cast(converted_contact_id as varchar) as converted_contact_id,
        case
            when converted_date_validation_failed = 1 then null
            else cast(converted_date as timestamp)
        end as converted_date,
        cast(converted_opportunity_id as varchar) as converted_opportunity_id,
        cast(trim(coalesce(country, '')) as varchar) as country,
        cast(trim(coalesce(country_code, '')) as varchar) as country_code,
        cast(created_by_id as varchar) as created_by_id,
        cast(created_date as timestamp) as created_date,
        cast(trim(coalesce(description, '')) as varchar) as lead_description,
        case
            when email_validation_failed = 1 then null
            when trim(email) = '' then null
            else lower(trim(email))
        end as email,
        cast(email_bounced_date as timestamp) as email_bounced_date,
        cast(trim(coalesce(email_bounced_reason, '')) as varchar) as email_bounced_reason,
        cast(trim(coalesce(fax, '')) as varchar) as fax,
        cast(trim(coalesce(first_name, '')) as varchar) as first_name,
        cast(trim(coalesce(geocode_accuracy, '')) as varchar) as geocode_accuracy,
        cast(coalesce(has_opted_out_of_email, false) as boolean) as has_opted_out_of_email,
        cast(trim(coalesce(industry, '')) as varchar) as industry,
        cast(coalesce(is_converted, false) as boolean) as is_converted,
        cast(coalesce(is_deleted, false) as boolean) as is_deleted,
        cast(coalesce(is_unread_by_owner, false) as boolean) as is_unread_by_owner,
        cast(last_activity_date as date) as last_activity_date,
        cast(last_modified_date as timestamp) as last_modified_date,
        cast(trim(coalesce(last_name, '')) as varchar) as last_name,
        cast(last_referenced_date as timestamp) as last_referenced_date,
        cast(last_viewed_date as timestamp) as last_viewed_date,
        cast(latitude as decimal(10,6)) as latitude,
        cast(trim(coalesce(lead_source, '')) as varchar) as lead_source,
        cast(longitude as decimal(10,6)) as longitude,
        cast(trim(coalesce(master_record_id, '')) as varchar) as master_record_id,
        case
            when mobile_phone_validation_failed = 1 then null
            when mobile_phone is null then null
            when length(mobile_phone) > 50 then null
            else cast(trim(mobile_phone) as varchar)
        end as mobile_phone,
        case
            when lead_name_validation_failed = 1 then trim(name)
            else trim(name)
        end as lead_name,
        cast(number_of_employees as integer) as number_of_employees,
        case
            when owner_id_validation_failed = 1 then null
            else cast(owner_id as varchar)
        end as owner_id,
        case
            when phone_validation_failed = 1 then null
            when phone is null then null
            when length(phone) > 50 then null
            else cast(trim(phone) as varchar)
        end as phone,
        case
            when photo_url is not null and length(photo_url) > 500 then null
            else cast(trim(coalesce(photo_url, '')) as varchar)
        end as photo_url,
        cast(trim(coalesce(postal_code, '')) as varchar) as postal_code,
        cast(trim(coalesce(salutation, '')) as varchar) as salutation,
        cast(trim(coalesce(state, '')) as varchar) as state,
        cast(trim(coalesce(state_code, '')) as varchar) as state_code,
        case
            when status_validation_failed = 1 then null -- nullify invalid status
            else cast(trim(status) as varchar)
        end as status,
        cast(trim(coalesce(street, '')) as varchar) as street,
        cast(system_modstamp as timestamp) as system_modstamp,
        cast(trim(coalesce(title, '')) as varchar) as title,
        case
            when website_validation_failed = 1 then null
            else trim(website)
        end as website,

        -- Standard audit trail field per YAML spec
        current_timestamp as _dbt_loaded_at

    from validated
    where lead_id_validation_failed = 0
      and lead_name_validation_failed = 0
      and company_validation_failed = 0
)

select *
from final
where not coalesce(is_deleted, false)
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 2996 | 3000 | 0 | 4 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"lead_id":"00q027ps5kaof3k"}</code> |
| K2 | <code>{"lead_id":"00q03amxe2c3puv"}</code> |
| K3 | <code>{"lead_id":"00q05qjo4vfvoye"}</code> |
| K4 | <code>{"lead_id":"00q04jezppo3id1"}</code> |
| K5 | <code>{"lead_id":"00q06iwlc2rpr5k"}</code> |
| K6 | <code>{"lead_id":"00q0migbo3pftkz"}</code> |
| K7 | <code>{"lead_id":"00q041ijbl0mrnl"}</code> |
| K8 | <code>{"lead_id":"00q072qycq1b0hn"}</code> |
| K9 | <code>{"lead_id":"00q07suzkv7jgnn"}</code> |
| K10 | <code>{"lead_id":"00q04v4fe6oxl7q"}</code> |
| K11 | <code>{"lead_id":"00q0ecsxvkgawq3"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| annual_revenue | 1222 | 1222 | 1222 | DECIMAL(18,3) | DECIMAL(18,2) |
| city | 0 | 0 | 0 | VARCHAR | VARCHAR |
| company | 0 | 0 | 0 | VARCHAR | VARCHAR |
| converted_account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| converted_contact_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| converted_date | 275 | 275 | 275 | TIMESTAMP | TIMESTAMP |
| converted_opportunity_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_by_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| email_bounced_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| email_bounced_reason | 2931 | 2931 | 2931 | VARCHAR | VARCHAR |
| fax | 2703 | 2703 | 2703 | VARCHAR | VARCHAR |
| first_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| geocode_accuracy | 2103 | 2103 | 2103 | VARCHAR | VARCHAR |
| has_opted_out_of_email | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| industry | 895 | 895 | 895 | VARCHAR | VARCHAR |
| is_converted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_deleted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_unread_by_owner | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| last_activity_date | 0 | 0 | 0 | DATE | DATE |
| last_modified_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| last_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| last_referenced_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| last_viewed_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| lead_source | 0 | 0 | 0 | VARCHAR | VARCHAR |
| master_record_id | 2996 | 2996 | 2996 | VARCHAR | VARCHAR |
| mobile_phone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| number_of_employees | 0 | 0 | 0 | INTEGER | INTEGER |
| owner_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| phone | 0 | 0 | 0 | VARCHAR | VARCHAR |
| photo_url | 2847 | 2847 | 2847 | VARCHAR | VARCHAR |
| postal_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| salutation | 1470 | 1470 | 1470 | VARCHAR | VARCHAR |
| state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| state_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| status | 1488 | 1488 | 1488 | VARCHAR | VARCHAR |
| street | 0 | 0 | 0 | VARCHAR | VARCHAR |
| system_modstamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| title | 608 | 608 | 608 | VARCHAR | VARCHAR |
| website | 0 | 0 | 0 | VARCHAR | VARCHAR |

annual_revenue 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 45729093.000 | 45729093.00 |
| K2 | 12553719.000 | 12553719.00 |
| K3 | 39703351.000 | 39703351.00 |

converted_date 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | 2020-03-04 04:47:38 | null |
| K5 | 2020-12-22 01:05:12 | null |
| K6 | 2022-07-14 20:50:34 | null |

email_bounced_reason 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | <code></code> |
| K2 | null | <code></code> |
| K7 | null | <code></code> |

fax 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | <code></code> |
| K2 | null | <code></code> |
| K4 | null | <code></code> |

geocode_accuracy 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | null | <code></code> |
| K7 | null | <code></code> |
| K4 | null | <code></code> |

industry 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K5 | null | <code></code> |
| K8 | null | <code></code> |
| K9 | null | <code></code> |

master_record_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | <code></code> |
| K2 | null | <code></code> |
| K7 | null | <code></code> |

photo_url 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | <code></code> |
| K2 | null | <code></code> |
| K7 | null | <code></code> |

salutation 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | null | <code></code> |
| K4 | null | <code></code> |
| K10 | null | <code></code> |

status 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | Open - Not Contacted | null |
| K7 | Working - Contacted | null |
| K4 | Open - Not Contacted | null |

title 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | null | <code></code> |
| K9 | null | <code></code> |
| K11 | null | <code></code> |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"lead_id":"00QfCinPvpULvmU"},{"lead_id":"00QUEzvJlRgzZR1"},{"lead_id":"00Qupias6dVP95N"},{"lead_id":"00QxbG2AzbNbOQz"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>2列；[{"column":"converted_opportunity_id","table_rows":2996},{"column":"master_record_id","table_rows":2996}]</code> |
| A3_constant_nonnull_column | <code>1列；[{"column":"is_deleted","value":"false"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["owner_id","created_by_id"],"nonnull_equal_rows":2996,"meaning_status":"契约未描述含义差别"}]</code> |
| C9_gold_runtime_text | <code>S5:75 current_date；命中数=2</code> |
| D10_keyword_in_any_result_field | <code>命中数=6；assistant_trajectory     from staging.stg_salesforce__lead where not coalesce(is_deleted, false) and owner_id is not null group by owner_id</code> |

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
| 23 | run | <code>cat &gt; sql/intermediate/int_salesforce__lead_conversion_funnel.sql &lt;&lt;'SQL'<br>with lead_base as (<br>    select * from staging.stg_salesforce__lead where not coalesce(is_deleted, false)<br>),<br>scored as (<br>    se</code> | 0 | false | false |
| 31 | run | <code>cat &gt; sql/marts/salesforce__opportunity_line_item_enhanced.sql &lt;&lt;'SQL'<br>with line_items as (<br> select oli.*,opp.opportunity_name,opp.account_id,opp.owner_id as opportunity_owner_id,opp.stage_name,opp.cl</code> | 0 | false | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>src=yaml.safe_load(open('salesforce_start.yaml')); co=yaml.safe_load(open('docs/data_contract.yaml'))['staging_contract']['tables']<br>mp={'account_id':'id','account_name':'na</code> | 847 | true | false |
| 39 | run | <code>tail -120 /tmp/run.log &amp;&amp; ls -lh salesforce.duckdb</code> | 1338 | false | false |
| 43 | run | <code>tail -180 /tmp/run2.log; grep -E '✗&#124;ERROR&#124;layer complete' /tmp/run2.log</code> | 15611 | true | false |
| 49 | run | <code>for f in sql/staging/*.sql; do echo ==== $f; grep -E 'md5&#124;history_unique_key&#124;created_date as&#124;last_modified_date' $f; done; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=</code> | 14873 | true | false |
| 53 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_salesforce__contact_history.sql');s=p.read_text().replace('id as account_id,','account_id as account_id,');p.write_text(s)<br>p=Path('sql/</code> | 331 | false | false |
| 63 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml,pathlib<br>c=duckdb.connect('salesforce.duckdb',read_only=True)<br>con=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer, schema, key in [('staging_contract','stag</code> | 589 | true | false |
| 67 | run | <code>for f in sql/staging/*.sql; do printf '%-55s ' "$(basename "$f")"; sed -n '2p' "$f"; done</code> | 1156 | true | false |
| 83 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('salesforce.duckdb',read_only=True)<br>for layer,sch in [('staging_contract','staging</code> | 225 | false | false |
| 85 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb,pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml')); c=duckdb.connect('salesforce.duckdb',read_only=True)<br>for layer,sch in [('staging_contract','staging</code> | 295 | true | false |
| 89 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=True); spec=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in spec['staging_contract']['tables']:<br> name=t['name</code> | 1149 | true | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
 if n=='stg_salesforce__lead': filters=['id is not null','last_name is not null','name is not null','status in (\'Open - Not Contacted\', \'Working - Contacted\', \'Closed - Converted\', \'Closed - Not Converted\')']
```
event 23 / message

```text
    select * from staging.stg_salesforce__lead where not coalesce(is_deleted, false)
```
event 23 / message

```text
    from staging.stg_salesforce__lead where not coalesce(is_deleted, false) and owner_id is not null group by owner_id
```
event 31 / message

```text
 select created_date::date as date_day,count(*) as leads_created from staging.stg_salesforce__lead where created_date is not null group by 1
```
event 31 / message

```text
 select converted_date::date as date_day,count(*) as leads_converted from staging.stg_salesforce__lead
```
event 31 / message

```text
 from staging.stg_salesforce__lead where not coalesce(is_deleted,false)
```
event 49 / message

```text
for t in ['stg_salesforce__account','stg_salesforce__contact','stg_salesforce__opportunity','stg_salesforce__user','stg_salesforce__lead','stg_salesforce__event']:
```
event 83 / message

```text
for t,col in [('stg_salesforce__contact','contact_id'),('stg_salesforce__opportunity','opportunity_id'),('stg_salesforce__user','user_id'),('stg_salesforce__lead','lead_id'),('stg_salesforce__event','event_id'),('stg_salesforce__task','task_id')]:
```
event 85 / message

```text
for t,col in [('stg_salesforce__contact','contact_id'),('stg_salesforce__opportunity','opportunity_id'),('stg_salesforce__user','user_id'),('stg_salesforce__lead','lead_id'),('stg_salesforce__event','event_id'),('stg_salesforce__task','task_id')]:
```
event 89 / message

```text
for sch,tbl,key in [('staging','stg_salesforce__account','account_id'),('staging','stg_salesforce__contact','contact_id'),('staging','stg_salesforce__opportunity','opportunity_id'),('staging','stg_salesforce__user','user_id'),('staging','stg_salesforce__lead','lead_id'),('staging','stg_salesforce__task','task_id'),('staging','stg_salesforce__event','event_id'),('staging','stg_salesforce__account_history','history_unique_key'),('staging','stg_salesforce__contact_history','history_unique_key'),('staging','stg_salesforce__opportunity_history','history_unique_key')]:
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-018.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__lead.sql`
- S6: `records/006_contract_impl-018.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/.tmp/result.md`
- S10: `data/023_packages_work/023_impl-018_stg_salesforce__lead/023_impl-018_stg_salesforce__lead.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions`
