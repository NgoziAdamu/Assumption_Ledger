# impl-009 | marts | google_play__finance_report | 差异：S1；日期 原记录

## 契约完整原文

S3:1723–1792

```yaml
    - name: google_play__finance_report
      description: Daily Google Play earnings and subscription activity, fully outer-joined and enriched with product and country metadata.
      grain: One row per (date_day, package_name, country_short, sku_id); source duplicates are preserved and may multiply across the join.
      source_models:
      - intermediate.int_google_play__earnings
      - staging.stg_google_play__subscriptions_country
      - intermediate.int_google_play__latest_product_info
      - staging.stg_google_play__country_codes
      business_logic: 'Inputs: - Earnings: intermediate.int_google_play__earnings (monetary amounts and transaction counts, merchant_currency). - Subscriptions: staging.stg_google_play__subscriptions_country (new, cancelled, active by country). - Product metadata: intermediate.int_google_play__latest_product_info (title by package_name and sku_id). - Country metadata: staging.stg_google_play__country_codes (names, region, sub_region by ISO alpha-2). Steps: - Join earnings and subscriptions with a full outer join on date_day, package_name, SKU (earnings.sku_id = subscriptions.product_id), and country code; null country codes are treated as equal between the two sources for matching (a temporary placeholder is used only for join matching and never appears in outputs). - For each output row, choose identifiers as follows: - date_day: from earnings if present; otherwise from subscriptions. - country_short: from earnings if present; otherwise from subscriptions. - package_name: from earnings if present; otherwise from subscriptions. - sku_id: from earnings if present; otherwise from subscriptions. - merchant_currency: taken from earnings (subscriptions do not supply currency). - Metric null handling: - Earnings metrics (net_amount, transactions, charge_amount, charge_transactions, refund_amount, refund_transactions, other_amount, other_transactions): if missing, output 0; amounts use merchant_currency; signs are preserved; no additional rounding beyond source precision (3 decimal places). - Subscription flow metrics (new_subscriptions, cancelled_subscriptions): if missing, output 0. - Active subscriptions forward-fill: - For each (country_short, sku_id), sort rows by date_day ascending. - When a non-null active count appears, carry that value forward to later days until another non-null value replaces it. - Days before the first non-null active count remain unset during filling and are finally output as 0. - Enrichment: - Left join product metadata by (package_name, sku_id) to add product_title. - Left join country metadata by country_short to add country_long (alternative name when available, else standard name), region, and sub_region. - No aggregation or de-duplication is applied; output row order is not enforced.'
      columns:
      - name: date_day
        data_type: DATE
        description: Reporting date from earnings if present, otherwise from subscriptions; may be null.
      - name: country_short
        data_type: VARCHAR
        description: ISO alpha-2 country code from earnings if present, otherwise from subscriptions; may be null; used to join country metadata.
      - name: package_name
        data_type: VARCHAR
        description: Google Play package identifier from earnings if present, otherwise from subscriptions; may be null; used to join product metadata.
      - name: sku_id
        data_type: VARCHAR
        description: Product SKU from earnings if present, otherwise from subscriptions; may be null; used to join product metadata.
      - name: merchant_currency
        data_type: VARCHAR
        description: Currency code sourced from earnings; may be null; unit for all amount columns.
      - name: net_amount
        data_type: DECIMAL(38,3)
        description: Net amount from earnings; missing values output as 0; uses merchant_currency; sign preserved.
      - name: transactions
        data_type: BIGINT
        description: Total transaction count from earnings; missing values output as 0.
      - name: charge_amount
        data_type: DECIMAL(38,3)
        description: Charge amount from earnings; missing values output as 0; uses merchant_currency; sign preserved.
      - name: charge_transactions
        data_type: BIGINT
        description: Charge transaction count from earnings; missing values output as 0.
      - name: refund_amount
        data_type: DECIMAL(38,3)
        description: Refund amount from earnings; missing values output as 0; uses merchant_currency; sign preserved.
      - name: refund_transactions
        data_type: BIGINT
        description: Refund transaction count from earnings; missing values output as 0.
      - name: other_amount
        data_type: DECIMAL(38,3)
        description: Other amount from earnings; missing values output as 0; uses merchant_currency; sign preserved.
      - name: other_transactions
        data_type: BIGINT
        description: Other transaction count from earnings; missing values output as 0.
      - name: new_subscriptions
        data_type: BIGINT
        description: New subscriptions from the subscriptions source; missing values output as 0.
      - name: cancelled_subscriptions
        data_type: BIGINT
        description: Cancelled subscriptions from the subscriptions source; missing values output as 0.
      - name: total_active_subscriptions
        data_type: BIGINT
        description: Active subscriptions after forward-filling within (country_short, sku_id) by ascending date; if no prior non-null exists on a date, output 0.
      - name: product_title
        data_type: VARCHAR
        description: Product title from product metadata joined by (package_name, sku_id); null if no match.
      - name: country_long
        data_type: VARCHAR
        description: Country name from country metadata by country_short using alternative name when available, else standard name; null if no match.
      - name: region
        data_type: VARCHAR
        description: Region from country metadata joined by country_short; null if no match.
      - name: sub_region
        data_type: VARCHAR
        description: Sub-region from country metadata joined by country_short; null if no match.
```

## agent 最终 SQL

S4

```sql
SELECT
cast(src.date_day as DATE) AS date_day,
cast(NULL as VARCHAR) AS country_short,
cast(src.package_name as VARCHAR) AS package_name,
cast(src.sku_id as VARCHAR) AS sku_id,
cast(src.merchant_currency as VARCHAR) AS merchant_currency,
cast(NULL as DECIMAL(38,3)) AS net_amount,
cast(0 as BIGINT) AS transactions,
cast(NULL as DECIMAL(38,3)) AS charge_amount,
cast(NULL as BIGINT) AS charge_transactions,
cast(NULL as DECIMAL(38,3)) AS refund_amount,
cast(NULL as BIGINT) AS refund_transactions,
cast(NULL as DECIMAL(38,3)) AS other_amount,
cast(NULL as BIGINT) AS other_transactions,
cast(0 as BIGINT) AS new_subscriptions,
cast(NULL as BIGINT) AS cancelled_subscriptions,
cast(NULL as BIGINT) AS total_active_subscriptions,
cast(NULL as VARCHAR) AS product_title,
cast(NULL as VARCHAR) AS country_long,
cast(NULL as VARCHAR) AS region,
cast(NULL as VARCHAR) AS sub_region
FROM intermediate.int_google_play__earnings AS src
WHERE src.date_day IS NOT NULL
```

## gold SQL（仅供定位差异）

S5

```sql
with earnings as (
    select *
    from intermediate.int_google_play__earnings
), 

country_codes as (
    select *
    from staging.stg_google_play__country_codes
),

product_info as (
    select *
    from intermediate.int_google_play__latest_product_info
),

subscriptions as (
    select *
    from staging.stg_google_play__subscriptions_country
), 

daily_join as (
    select
        coalesce(earnings.date_day, subscriptions.date_day) as date_day,
        coalesce(earnings.country_short, subscriptions.country) as country_short,
        coalesce(earnings.package_name, subscriptions.package_name) as package_name,
        coalesce(earnings.sku_id, subscriptions.product_id) as sku_id,
        earnings.merchant_currency,
        
        coalesce(earnings.net_amount, 0) as net_amount,
        coalesce(earnings.transactions, 0) as transactions,
        coalesce(earnings.charge_amount, 0) as charge_amount,
        coalesce(earnings.charge_transactions, 0) as charge_transactions,
        coalesce(earnings.refund_amount, 0) as refund_amount,
        coalesce(earnings.refund_transactions, 0) as refund_transactions,
        coalesce(earnings.other_amount, 0) as other_amount,
        coalesce(earnings.other_transactions, 0) as other_transactions,

        coalesce(subscriptions.new_subscriptions, 0) as new_subscriptions,
        coalesce(subscriptions.cancelled_subscriptions, 0) as cancelled_subscriptions,
        subscriptions.total_active_subscriptions
    from earnings
    full outer join subscriptions
        on earnings.date_day = subscriptions.date_day
        and earnings.package_name = subscriptions.package_name
        and coalesce(earnings.country_short, 'null_country') = coalesce(subscriptions.country, 'null_country')
        and earnings.sku_id = subscriptions.product_id
), 

create_partitions as (
    select 
        *,
        sum(case when total_active_subscriptions is null 
                then 0 else 1 end) over (
            partition by country_short, sku_id 
            order by date_day asc 
            rows unbounded preceding
        ) as total_active_subscriptions_partition
    from daily_join
), 

fill_values as (
    select 
        date_day,
        country_short,
        package_name, 
        sku_id,
        merchant_currency,
        net_amount,
        transactions,
        charge_amount,
        charge_transactions,
        refund_amount,
        refund_transactions,
        other_amount,
        other_transactions,
        new_subscriptions,
        cancelled_subscriptions,
        
        first_value(total_active_subscriptions) over (
            partition by total_active_subscriptions_partition, country_short, sku_id 
            order by date_day asc 
            rows between unbounded preceding and current row
        ) as total_active_subscriptions
    from create_partitions
), 

final_values as (
    select 
        date_day,
        country_short,
        package_name, 
        sku_id,
        merchant_currency,
        net_amount,
        transactions,
        charge_amount,
        charge_transactions,
        refund_amount,
        refund_transactions,
        other_amount,
        other_transactions,
        new_subscriptions,
        cancelled_subscriptions,
        coalesce(total_active_subscriptions, 0) as total_active_subscriptions
    from fill_values
), 

add_product_country_info as (
    select 
        base.*,
        product_info.product_title,
        coalesce(country_codes.alternative_country_name, country_codes.country_name) as country_long,
        country_codes.region,
        country_codes.sub_region
    from final_values as base
    left join product_info 
        on base.package_name = product_info.package_name
        and base.sku_id = product_info.sku_id
    left join country_codes 
        on country_codes.country_code_alpha_2 = base.country_short
)

select *
from add_product_country_info
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 0 | 3144 | 0 | 2304 | 0 | 731 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| date_day | 0 | 0 | 0 | DATE | DATE |
| country_short | 0 | 0 | 0 | VARCHAR | VARCHAR |
| package_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sku_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| merchant_currency | 0 | 0 | 0 | VARCHAR | VARCHAR |
| net_amount | 0 | 0 | 0 | DECIMAL(38,3) | DECIMAL(38,3) |
| transactions | 0 | 0 | 0 | BIGINT | BIGINT |
| charge_amount | 0 | 0 | 0 | DECIMAL(38,3) | DECIMAL(38,3) |
| charge_transactions | 0 | 0 | 0 | BIGINT | BIGINT |
| refund_amount | 0 | 0 | 0 | DECIMAL(38,3) | DECIMAL(38,3) |
| refund_transactions | 0 | 0 | 0 | BIGINT | BIGINT |
| other_amount | 0 | 0 | 0 | DECIMAL(38,3) | DECIMAL(38,3) |
| other_transactions | 0 | 0 | 0 | BIGINT | BIGINT |
| new_subscriptions | 0 | 0 | 0 | BIGINT | BIGINT |
| cancelled_subscriptions | 0 | 0 | 0 | BIGINT | BIGINT |
| total_active_subscriptions | 0 | 0 | 0 | BIGINT | BIGINT |
| product_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| country_long | 0 | 0 | 0 | VARCHAR | VARCHAR |
| region | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sub_region | 0 | 0 | 0 | VARCHAR | VARCHAR |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"date_day":"2020-01-01","package_name":"com.app.musicplayer","sku_id":"com.app.musicplayer.premium","region":"Americas"},{"date_day":"2020-01-01","package_name":"com.app.musicplayer","sku_id":"com.app.musicplayer.premium","region":"Asia"},{"date_day":"2020-01-01","package_name":"com.app.musicplayer","sku_id":"com.app.musicplayer.premium","region":"Europe"},{"date_day":"2020-01-01","package_name":"com.app.musicplayer","sku_id":"com.app.musicplayer.pro","region":"Asia"},{"date_day":"2020-01-01","package_name":"com.sample.productivity","sku_id":"com.sample.productivity.basic","region":"Asia"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>14列；[{"column":"country_short","table_rows":7990},{"column":"net_amount","table_rows":7990},{"column":"charge_amount","table_rows":7990}]</code> |
| A3_constant_nonnull_column | <code>3列；[{"column":"merchant_currency","value":"USD"},{"column":"transactions","value":"0"},{"column":"new_subscriptions","value":"0"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["package_name","sku_id"],"nonnull_equal_rows":7990,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["transactions","new_subscriptions"],"nonnull_equal_rows":7990,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["package_name","sku_id"],"nonnull_equal_rows":7990,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["transactions","new_subscriptions"],"nonnull_equal_rows":7990,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B5_null_literal_output | <code>14输出列；[{"column":"country_short","expression":["CAST(NULL AS TEXT)"]},{"column":"net_amount","expression":["CAST(NULL AS DECIMAL(38, 3))"]},{"column":"charge_amount","expression":["CAST(NULL AS DECIMAL(38, 3))"]}]</code> |
| B6_constant_literal_output | <code>2输出列；[{"column":"transactions","expression":["CAST(0 AS BIGINT)"]},{"column":"new_subscriptions","expression":["CAST(0 AS BIGINT)"]}]</code> |
| B7_specified_not_read | <code>["intermediate.int_google_play__latest_product_info","staging.stg_google_play__country_codes","staging.stg_google_play__subscriptions_country"]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：69；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -exec sh -c 'echo ===$1; wc -c "$1"' _ {} \;</code> | 3902 | true | false |
| 33 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>I=Path('sql/intermediate'); M=Path('sql/marts')<br>def w(path,s): Path(path).write_text(s.strip()+'\n')<br>w(I/'int_google_play__latest_product_info.sql'</code> | 0 | false | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob,os<br>c=duckdb.connect(); c.execute("ATTACH 'google_play_start.duckdb' AS src (READ_ONLY)")<br>for s in ['raw','staging','intermediate','mart']: c.execute(f'create schema </code> | 4516 | true | false |
| 39 | run | <code>sed -i 's/) prior,/) prior_value,/g;s/ prior, / prior_value, /g;s/(daily_device_installs-prior)::DOUBLE/(daily_device_installs-prior_value)::DOUBLE/g;s/nullif(prior,0)/nullif(prior_value,0)/g' sql/int</code> | 0 | false | false |
| 41 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,glob,os<br>c=duckdb.connect(); c.execute("ATTACH 'google_play_start.duckdb' AS src (READ_ONLY)")<br>for s in ['raw','staging','intermediate','mart']:c.execute(f'create schema {</code> | 967 | true | false |
| 43 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; code=$?; tail -60 /tmp/runlog; exit $code</code> | 4495 | true | false |
| 53 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_google_play__earnings.sql'); s=p.read_text().replace('CAST(sku_id AS VARCHAR) AS sku_id','CAST(coalesce(sku_id, product_id, base_plan_i</code> | 2857 | true | false |

### agent action 的 thought/message 命中原句

未找到命中原句。

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-009.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__finance_report.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/sql/marts/google_play__finance_report.sql`
- S6: `records/006_contract_impl-009.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/result.md`
- S10: `data/021_packages_work/021_impl-009_google_play__finance_report/021_impl-009_google_play__finance_report.json`
- S11: `data/005_cs_work/impl-009/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-009/google_play.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions`
