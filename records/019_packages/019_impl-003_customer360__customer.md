# impl-003 | marts | customer360__customer | 差异：S1；日期 原记录

## 契约完整原文

S3:1395–1480

```yaml
    - name: customer360__customer
      description: Unified customer and organization header profile with pass-through attributes and deterministic sample metrics/aggregations.
      grain: One row per customer360_id
      source_models:
      - marts.customer360__mapping
      - marts.customer360__summary
      business_logic: '1) Build a dimensions set by inner joining marts.customer360__mapping to marts.customer360__summary on customer360_id, selecting: customer360_organization_id, is_organization_header, source_ids (from mapping) and email, full_name, organization_name, address_line_1, address_line_2, city, state, country, country_alt_name, postal_code, ip_address, phone (from summary). Only ids present in both sources are kept; all fields are passed through as stored. 2) For non-organization headers (is_organization_header = FALSE), assign sample metrics per customer360_id: - For ''sample_customer_1'': sends=10, opens=3, clicks=1, sales_amount=1250.00, sales_count=2, first_sale_date=2024-01-15, most_recent_sale_date=2024-03-15, tickets_created=3, tickets_resolved=2, avg_satisfaction=4.5. - For all others: sends=5, opens=2, clicks=0, sales_amount=750.00, sales_count=1, first_sale_date=2024-02-10, most_recent_sale_date=2024-02-10, tickets_created=1, tickets_resolved=1, avg_satisfaction=5.0. 3) Combine dimensions with these metrics by customer360_id. For rows without assigned metrics (headers), set numeric metrics to 0 (including avg_satisfaction_score) and leave first_sale_date and most_recent_sale_date as NULL. 4) For organization headers only, produce one row per unique header by aggregating the combined dataset across the header’s own rows: sum email sends/opens/clicks, sum sales amount and sales count, take the earliest first_sale_date, the latest most_recent_sale_date, sum tickets created/resolved, and average the satisfaction score. Aggregations consider only header rows (child/customer rows are not included in header rollups); standard null handling applies to aggregates (nulls are ignored in averages; earliest/latest dates return NULL if all inputs are NULL). 5) Output includes all non-header rows from step 3 and the aggregated header rows from step 4 appended together. No specific output ordering is enforced.'
      columns:
      - name: customer360_id
        data_type: VARCHAR
        description: Primary identifier; one output row per id; also the join key between mapping and summary.
      - name: customer360_organization_id
        data_type: VARCHAR
        description: Organization identifier from mapping; passed through unchanged.
      - name: is_organization_header
        data_type: BOOLEAN
        description: TRUE for organization headers (included via header aggregation), FALSE for individual/non-header customers (receive sample metrics).
      - name: source_ids
        data_type: VARCHAR
        description: Source system identifier(s) from mapping; passed through with original formatting.
      - name: email
        data_type: VARCHAR
        description: Email from summary; passed through.
      - name: full_name
        data_type: VARCHAR
        description: Full name from summary; passed through.
      - name: organization_name
        data_type: VARCHAR
        description: Organization name from summary; passed through.
      - name: address_line_1
        data_type: VARCHAR
        description: Address line 1 from summary; passed through.
      - name: address_line_2
        data_type: VARCHAR
        description: Address line 2 from summary; passed through.
      - name: city
        data_type: VARCHAR
        description: City from summary; passed through.
      - name: state
        data_type: VARCHAR
        description: State/region from summary; passed through.
      - name: country
        data_type: VARCHAR
        description: Country from summary; passed through.
      - name: country_alt_name
        data_type: VARCHAR
        description: Alternative country name from summary; passed through.
      - name: postal_code
        data_type: BIGINT
        description: Postal/ZIP code from summary stored as numeric; passed through.
      - name: ip_address
        data_type: VARCHAR
        description: IP address from summary; passed through.
      - name: phone
        data_type: VARCHAR
        description: Phone number from summary; passed through.
      - name: marketing_email_sends
        data_type: HUGEINT
        description: 'Count of marketing emails sent; non-headers: 10 for ''sample_customer_1'' else 5; headers: summed across header rows; missing metrics default to 0.'
      - name: marketing_email_opens
        data_type: HUGEINT
        description: 'Count of marketing email opens; non-headers: 3 for ''sample_customer_1'' else 2; headers: summed across header rows; missing metrics default to 0.'
      - name: marketing_email_clicks
        data_type: HUGEINT
        description: 'Count of marketing email clicks; non-headers: 1 for ''sample_customer_1'' else 0; headers: summed across header rows; missing metrics default to 0.'
      - name: total_sales_amount
        data_type: DECIMAL(38,2)
        description: 'Total sales amount; non-headers: 1250.00 for ''sample_customer_1'' else 750.00; headers: summed across header rows; missing metrics default to 0.00.'
      - name: total_sales_count
        data_type: HUGEINT
        description: 'Total number of sales; non-headers: 2 for ''sample_customer_1'' else 1; headers: summed across header rows; missing metrics default to 0.'
      - name: first_sale_date
        data_type: DATE
        description: 'First sale date; non-headers: 2024-01-15 for ''sample_customer_1'' else 2024-02-10; headers: earliest across header rows; NULL if no non-NULL values.'
      - name: most_recent_sale_date
        data_type: DATE
        description: 'Most recent sale date; non-headers: 2024-03-15 for ''sample_customer_1'' else 2024-02-10; headers: latest across header rows; NULL if no non-NULL values.'
      - name: support_tickets_created
        data_type: HUGEINT
        description: 'Count of support tickets created; non-headers: 3 for ''sample_customer_1'' else 1; headers: summed across header rows; missing metrics default to 0.'
      - name: support_tickets_resolved
        data_type: HUGEINT
        description: 'Count of support tickets resolved; non-headers: 2 for ''sample_customer_1'' else 1; headers: summed across header rows; missing metrics default to 0.'
      - name: avg_satisfaction_score
        data_type: DOUBLE
        description: 'Average satisfaction score; non-headers: 4.5 for ''sample_customer_1'' else 5.0; headers: averaged across header rows; missing metrics default to 0.0.'
```

## agent 最终 SQL

S4

```sql
with dimensions as (
 select m.customer360_id,m.customer360_organization_id,m.is_organization_header,m.source_ids,s.email,s.full_name,s.organization_name,
 s.address_line_1,s.address_line_2,s.city,s.state,s.country,s.country_alt_name,s.postal_code,s.ip_address,s.phone
 from marts.customer360__mapping m inner join marts.customer360__summary s using(customer360_id)
), non_headers as (
 select *,case when customer360_id='sample_customer_1' then 10 else 5 end::hugeint as marketing_email_sends,
 case when customer360_id='sample_customer_1' then 3 else 2 end::hugeint as marketing_email_opens,
 case when customer360_id='sample_customer_1' then 1 else 0 end::hugeint as marketing_email_clicks,
 case when customer360_id='sample_customer_1' then 1250.00 else 750.00 end::decimal(38,2) as total_sales_amount,
 case when customer360_id='sample_customer_1' then 2 else 1 end::hugeint as total_sales_count,
 case when customer360_id='sample_customer_1' then date '2024-01-15' else date '2024-02-10' end as first_sale_date,
 case when customer360_id='sample_customer_1' then date '2024-03-15' else date '2024-02-10' end as most_recent_sale_date,
 case when customer360_id='sample_customer_1' then 3 else 1 end::hugeint as support_tickets_created,
 case when customer360_id='sample_customer_1' then 2 else 1 end::hugeint as support_tickets_resolved,
 case when customer360_id='sample_customer_1' then 4.5 else 5.0 end::double as avg_satisfaction_score
 from dimensions where not is_organization_header
), headers as (
 select customer360_id,customer360_organization_id,is_organization_header,source_ids,email,full_name,organization_name,address_line_1,address_line_2,city,state,country,country_alt_name,postal_code,ip_address,phone,
 sum(0)::hugeint as marketing_email_sends,sum(0)::hugeint as marketing_email_opens,sum(0)::hugeint as marketing_email_clicks,sum(0.00)::decimal(38,2) as total_sales_amount,
 sum(0)::hugeint as total_sales_count,null::date as first_sale_date,null::date as most_recent_sale_date,sum(0)::hugeint as support_tickets_created,sum(0)::hugeint as support_tickets_resolved,avg(0.0)::double as avg_satisfaction_score
 from dimensions where is_organization_header group by all
)
select * from non_headers union all select * from headers
```

## gold SQL（仅供定位差异）

S5

```sql
with dimensions as (
    select
        summary.customer360_id,
        mapping.customer360_organization_id,
        mapping.is_organization_header,
        mapping.source_ids,
        summary.email,
        summary.full_name,
        summary.organization_name,
        summary.address_line_1,
        summary.address_line_2,
        summary.city,
        summary.state,
        summary.country,
        summary.country_alt_name,
        summary.postal_code,
        summary.ip_address,
        summary.phone

    from marts.customer360__mapping as mapping
    join marts.customer360__summary as summary 
        on mapping.customer360_id = summary.customer360_id
),

-- Sample metrics (since we don't have actual source systems)
sample_metrics as (
    select 
        customer360_id,
        -- Sample marketing metrics
        case when customer360_id = 'sample_customer_1' then 10 else 5 end as marketing_email_sends,
        case when customer360_id = 'sample_customer_1' then 3 else 2 end as marketing_email_opens,
        case when customer360_id = 'sample_customer_1' then 1 else 0 end as marketing_email_clicks,
        
        -- Sample sales metrics  
        case when customer360_id = 'sample_customer_1' then 1250.00 else 750.00 end as total_sales_amount,
        case when customer360_id = 'sample_customer_1' then 2 else 1 end as total_sales_count,
        case when customer360_id = 'sample_customer_1' then '2024-01-15'::date else '2024-02-10'::date end as first_sale_date,
        case when customer360_id = 'sample_customer_1' then '2024-03-15'::date else '2024-02-10'::date end as most_recent_sale_date,
        
        -- Sample support metrics
        case when customer360_id = 'sample_customer_1' then 3 else 1 end as support_tickets_created,
        case when customer360_id = 'sample_customer_1' then 2 else 1 end as support_tickets_resolved,
        case when customer360_id = 'sample_customer_1' then 4.5 else 5.0 end as avg_satisfaction_score
        
    from dimensions
    where not is_organization_header
),

combine_customers as (
    select 
        dimensions.*,
        coalesce(sample_metrics.marketing_email_sends, 0) as marketing_email_sends,
        coalesce(sample_metrics.marketing_email_opens, 0) as marketing_email_opens,
        coalesce(sample_metrics.marketing_email_clicks, 0) as marketing_email_clicks,
        coalesce(sample_metrics.total_sales_amount, 0) as total_sales_amount,
        coalesce(sample_metrics.total_sales_count, 0) as total_sales_count,
        sample_metrics.first_sale_date,
        sample_metrics.most_recent_sale_date,
        coalesce(sample_metrics.support_tickets_created, 0) as support_tickets_created,
        coalesce(sample_metrics.support_tickets_resolved, 0) as support_tickets_resolved,
        coalesce(sample_metrics.avg_satisfaction_score, 0) as avg_satisfaction_score

    from dimensions
    left join sample_metrics
        on dimensions.customer360_id = sample_metrics.customer360_id
),

rollup_to_orgs as (
    select 
        customer360_id,
        customer360_organization_id,
        is_organization_header,
        source_ids,
        email,
        full_name,
        organization_name,
        address_line_1,
        address_line_2,
        city,
        state,
        country,
        country_alt_name,
        postal_code,
        ip_address,
        phone,
        sum(marketing_email_sends) as marketing_email_sends,
        sum(marketing_email_opens) as marketing_email_opens,
        sum(marketing_email_clicks) as marketing_email_clicks,
        sum(total_sales_amount) as total_sales_amount,
        sum(total_sales_count) as total_sales_count,
        min(first_sale_date) as first_sale_date,
        max(most_recent_sale_date) as most_recent_sale_date,
        sum(support_tickets_created) as support_tickets_created,
        sum(support_tickets_resolved) as support_tickets_resolved,
        avg(avg_satisfaction_score) as avg_satisfaction_score

    from combine_customers
    where is_organization_header
    group by 
        customer360_id,
        customer360_organization_id,
        is_organization_header,
        source_ids,
        email,
        full_name,
        organization_name,
        address_line_1,
        address_line_2,
        city,
        state,
        country,
        country_alt_name,
        postal_code,
        ip_address,
        phone
),

final as (
    select *
    from combine_customers
    where not is_organization_header

    union all

    select *
    from rollup_to_orgs
)

select * from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 30008 | 102416 | 0 | 0 | 5954 | 5954 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"customer360_id":"000bd038cf03e102299f66d23ccfea08","customer360_organization_id":"9a41c3efc461aa5c412ecc525a5af14e","state":"null","country":"null","postal_code":"69448"}</code> |
| K2 | <code>{"customer360_id":"001b3c4a9048892c269e18d30d2dc36f","customer360_organization_id":"eb2e642dbd80f41d31b4a487905ec180","state":"null","country":"null","postal_code":"10437"}</code> |
| K3 | <code>{"customer360_id":"001d9d332be0770bac0b3ad6347990eb","customer360_organization_id":"d4f8a0c8b74879226da396f4d7303c36","state":"null","country":"null","postal_code":"88519"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| customer360_id | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| customer360_organization_id | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| is_organization_header | 0 | 0 | 72408 | BOOLEAN | BOOLEAN |
| source_ids | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| email | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| full_name | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| organization_name | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| address_line_1 | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| address_line_2 | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| city | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| state | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| country | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| country_alt_name | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| postal_code | 0 | 0 | 72408 | BIGINT | BIGINT |
| ip_address | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| phone | 0 | 0 | 72408 | VARCHAR | VARCHAR |
| first_sale_date | 0 | 0 | 72408 | DATE | DATE |
| most_recent_sale_date | 0 | 0 | 72408 | DATE | DATE |

customer360_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"000bd038cf03e102299f66d23ccfea08","rows":4}]</code> | <code>[{"value":"000bd038cf03e102299f66d23ccfea08","rows":16}]</code> |
| K2 | <code>[{"value":"001b3c4a9048892c269e18d30d2dc36f","rows":4}]</code> | <code>[{"value":"001b3c4a9048892c269e18d30d2dc36f","rows":16}]</code> |
| K3 | <code>[{"value":"001d9d332be0770bac0b3ad6347990eb","rows":4}]</code> | <code>[{"value":"001d9d332be0770bac0b3ad6347990eb","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

customer360_organization_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"9a41c3efc461aa5c412ecc525a5af14e","rows":4}]</code> | <code>[{"value":"9a41c3efc461aa5c412ecc525a5af14e","rows":16}]</code> |
| K2 | <code>[{"value":"eb2e642dbd80f41d31b4a487905ec180","rows":4}]</code> | <code>[{"value":"eb2e642dbd80f41d31b4a487905ec180","rows":16}]</code> |
| K3 | <code>[{"value":"d4f8a0c8b74879226da396f4d7303c36","rows":4}]</code> | <code>[{"value":"d4f8a0c8b74879226da396f4d7303c36","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

is_organization_header 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"false","rows":4}]</code> | <code>[{"value":"false","rows":16}]</code> |
| K2 | <code>[{"value":"false","rows":4}]</code> | <code>[{"value":"false","rows":16}]</code> |
| K3 | <code>[{"value":"false","rows":4}]</code> | <code>[{"value":"false","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

source_ids 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"{\"marketo\":\"3088\",\"stripe\":\"\",\"zendesk\":\"\"}","rows":4}]</code> | <code>[{"value":"{\"marketo\":\"3088\",\"stripe\":\"\",\"zendesk\":\"\"}","rows":16}]</code> |
| K2 | <code>[{"value":"{\"marketo\":\"928\",\"stripe\":\"\",\"zendesk\":\"\"}","rows":4}]</code> | <code>[{"value":"{\"marketo\":\"928\",\"stripe\":\"\",\"zendesk\":\"\"}","rows":16}]</code> |
| K3 | <code>[{"value":"{\"marketo\":\"2078\",\"stripe\":\"\",\"zendesk\":\"\"}","rows":4}]</code> | <code>[{"value":"{\"marketo\":\"2078\",\"stripe\":\"\",\"zendesk\":\"\"}","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

email 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"constance.martin@company.com","rows":4}]</code> | <code>[{"value":"constance.martin@company.com","rows":16}]</code> |
| K2 | <code>[{"value":"valentine.miller@startup.io","rows":4}]</code> | <code>[{"value":"valentine.miller@startup.io","rows":16}]</code> |
| K3 | <code>[{"value":"nathaniel.jackson@yahoo.com","rows":4}]</code> | <code>[{"value":"nathaniel.jackson@yahoo.com","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

full_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"connie Martin","rows":4}]</code> | <code>[{"value":"connie Martin","rows":16}]</code> |
| K2 | <code>[{"value":"Valentine Miller","rows":4}]</code> | <code>[{"value":"Valentine Miller","rows":16}]</code> |
| K3 | <code>[{"value":"Nathaniel Jackson","rows":4}]</code> | <code>[{"value":"Nathaniel Jackson","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

organization_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Innovate Dynamics","rows":4}]</code> | <code>[{"value":"Innovate Dynamics","rows":16}]</code> |
| K2 | <code>[{"value":"Digital Ventures","rows":4}]</code> | <code>[{"value":"Digital Ventures","rows":16}]</code> |
| K3 | <code>[{"value":"Global Solutions","rows":4}]</code> | <code>[{"value":"Global Solutions","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

address_line_1 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"436 Elm Dr","rows":4}]</code> | <code>[{"value":"436 Elm Dr","rows":16}]</code> |
| K2 | <code>[{"value":"1829 Oak Ave","rows":4}]</code> | <code>[{"value":"1829 Oak Ave","rows":16}]</code> |
| K3 | <code>[{"value":"7717 Market St","rows":4}]</code> | <code>[{"value":"7717 Market St","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

address_line_2 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":4}]</code> | <code>[{"value":null,"rows":16}]</code> |
| K2 | <code>[{"value":null,"rows":4}]</code> | <code>[{"value":null,"rows":16}]</code> |
| K3 | <code>[{"value":null,"rows":4}]</code> | <code>[{"value":null,"rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

city 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Houston","rows":4}]</code> | <code>[{"value":"Houston","rows":16}]</code> |
| K2 | <code>[{"value":"San Antonio","rows":4}]</code> | <code>[{"value":"San Antonio","rows":16}]</code> |
| K3 | <code>[{"value":"San Francisco","rows":4}]</code> | <code>[{"value":"San Francisco","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

state 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":4}]</code> | <code>[{"value":null,"rows":16}]</code> |
| K2 | <code>[{"value":null,"rows":4}]</code> | <code>[{"value":null,"rows":16}]</code> |
| K3 | <code>[{"value":null,"rows":4}]</code> | <code>[{"value":null,"rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

country 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":4}]</code> | <code>[{"value":null,"rows":16}]</code> |
| K2 | <code>[{"value":null,"rows":4}]</code> | <code>[{"value":null,"rows":16}]</code> |
| K3 | <code>[{"value":null,"rows":4}]</code> | <code>[{"value":null,"rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

country_alt_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":4}]</code> | <code>[{"value":null,"rows":16}]</code> |
| K2 | <code>[{"value":null,"rows":4}]</code> | <code>[{"value":null,"rows":16}]</code> |
| K3 | <code>[{"value":null,"rows":4}]</code> | <code>[{"value":null,"rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

postal_code 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"69448","rows":4}]</code> | <code>[{"value":"69448","rows":16}]</code> |
| K2 | <code>[{"value":"10437","rows":4}]</code> | <code>[{"value":"10437","rows":16}]</code> |
| K3 | <code>[{"value":"88519","rows":4}]</code> | <code>[{"value":"88519","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

ip_address 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"192.168.66.162","rows":4}]</code> | <code>[{"value":"192.168.66.162","rows":16}]</code> |
| K2 | <code>[{"value":"192.168.34.247","rows":4}]</code> | <code>[{"value":"192.168.34.247","rows":16}]</code> |
| K3 | <code>[{"value":"192.168.172.203","rows":4}]</code> | <code>[{"value":"192.168.172.203","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

phone 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"+15556408472","rows":4}]</code> | <code>[{"value":"+15556408472","rows":16}]</code> |
| K2 | <code>[{"value":"+15554914713","rows":4}]</code> | <code>[{"value":"+15554914713","rows":16}]</code> |
| K3 | <code>[{"value":"+15552832224","rows":4}]</code> | <code>[{"value":"+15552832224","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

first_sale_date 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"2024-02-10","rows":4}]</code> | <code>[{"value":"2024-02-10","rows":16}]</code> |
| K2 | <code>[{"value":"2024-02-10","rows":4}]</code> | <code>[{"value":"2024-02-10","rows":16}]</code> |
| K3 | <code>[{"value":"2024-02-10","rows":4}]</code> | <code>[{"value":"2024-02-10","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

most_recent_sale_date 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"2024-02-10","rows":4}]</code> | <code>[{"value":"2024-02-10","rows":16}]</code> |
| K2 | <code>[{"value":"2024-02-10","rows":4}]</code> | <code>[{"value":"2024-02-10","rows":16}]</code> |
| K3 | <code>[{"value":"2024-02-10","rows":4}]</code> | <code>[{"value":"2024-02-10","rows":16}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

| 约束 | 列 | 违反计数 |
|---|---|---|
| grain | customer360_id | <code>{"distinct_key_groups":12066,"duplicate_key_groups":78,"rows_in_duplicate_groups":392,"excess_duplicate_rows":314,"null_key_rows":0,"nonnull_duplicate_key_groups":78,"nonnull_rows_in_duplicate_groups":392,"nonnull_excess_duplicate_rows":314,"null_containing_duplicate_key_groups":0,"rows_in_null_containing_duplicate_groups":0}</code> |

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>1列；[{"column":"marketing_email_clicks","value":"0"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["total_sales_count","support_tickets_created","support_tickets_resolved"],"nonnull_equal_rows":12380,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["first_sale_date","most_recent_sale_date"],"nonnull_equal_rows":11097,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["total_sales_count","support_tickets_created","support_tickets_resolved"],"nonnull_equal_rows":12380,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["first_sale_date","most_recent_sale_date"],"nonnull_equal_rows":11097,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B5_null_literal_output | <code>2输出列；[{"column":"first_sale_date","expression":["CASE WHEN customer360_id = 'sample_customer_1' THEN CAST('2024-01-15' AS DATE) ELSE CAST('2024-02-10' AS DATE) END"]},{"column":"most_recent_sale_date","expression":["CASE WHEN customer360_id = 'sample_customer_1' THEN CAST('2024-03-15' AS DATE) ELSE CAST('2024-02-10' AS DATE) END"]}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：53；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort; cat config/layer_dependencies.yaml</code> | 3128 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 11047 | true | false |
| 21 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('intermediate','int_customer360__risk_assessment', '''<br>with behavior as (<br> select ba.*, lm.customer_health_score, lm.lifecycle_stage, lm.active_30_days, lm.active_90_day</code> | 0 | false | false |
| 23 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br># Generic distinct/index profile marts<br>put('marts','customer360__email', '''<br>with email_rows as (<br> select m.customer360_id, s.email from marts.customer360__mapping m inner j</code> | 0 | false | false |
| 29 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 7140 | true | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('customer360.duckdb',read_only=True)<br>checks={<br>'status_key_dups':"select count(*) from (select customer360_id from marts.customer360__status group by 1 ha</code> | 616 | false | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
put('marts','customer360__customer', '''
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-003.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__customer.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__customer.sql`
- S6: `records/006_contract_impl-003.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/result.md`
- S10: `data/019_packages_work/019_impl-003_customer360__customer/019_impl-003_customer360__customer.json`
- S11: `data/005_cs_work/impl-003/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions`
