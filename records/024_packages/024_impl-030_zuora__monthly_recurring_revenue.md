# impl-030 | marts | zuora__monthly_recurring_revenue | 差异：S1；日期 原记录

## 契约完整原文

S3:3742–3773

```yaml
    - name: zuora__monthly_recurring_revenue
      description: Monthly sums of recurring vs non-recurring invoice amounts per account using the current rate plan charge type.
      grain: One row per account_id and account_month (month of service_start_day)
      source_models:
      - intermediate.int_zuora__invoice_item_base
      - intermediate.int_zuora__rate_plan_charge_current
      business_logic: '- Inputs: - From intermediate.int_zuora__invoice_item_base: account_id, service_start_day, rate_plan_charge_id, charge_amount, discount_amount. - From intermediate.int_zuora__rate_plan_charge_current: rate_plan_charge_id, charge_type. - Build the month spine as distinct pairs of (account_id, month of service_start_day set to the first day). - Left join invoice items to the month spine on account_id and month; then left join the current rate plan charge on rate_plan_charge_id. - Classification for each invoice item: - Recurring (MRR): charge_type equals "recurring" when compared case-insensitively (no trimming). - Non-MRR: charge_type is present and, case-insensitively, not equal to "recurring". - If the rate plan charge is missing or charge_type is NULL, the item contributes 0 to both categories. - Per-line numeric handling: - charge_amount is converted to a DOUBLE; invalid or NULL values are treated as 0.0. - discount_amount treats NULL as 0.0; signs are preserved; no rounding or currency conversion. - If the rate plan charge join returns multiple matches for a line, that line’s amounts are counted multiple times. - Aggregations per (account_id, account_month): - Gross MRR: sum of charge_amount over recurring items. - Discount MRR: sum of discount_amount over recurring items. - Net MRR: sum over recurring items of (charge_amount minus discount_amount). - Gross non-MRR: sum of charge_amount over non-MRR items. - Discount non-MRR: sum of discount_amount over non-MRR items. - Net non-MRR: sum over non-MRR items of (charge_amount minus discount_amount). - Output includes every (account_id, account_month) from the month spine; if no items match a category, the corresponding sums are 0.0.'
      columns:
      - name: account_id
        data_type: VARCHAR
        description: Account identifier used for grouping.
      - name: account_month
        data_type: DATE
        description: Month derived from service_start_day, set to the first day of that month.
      - name: gross_current_month_mrr
        data_type: DOUBLE
        description: Sum of charge_amount (invalid or NULL treated as 0.0) for items classified as recurring (case-insensitive match to 'recurring').
      - name: discount_current_month_mrr
        data_type: DOUBLE
        description: Sum of discount_amount (NULL treated as 0.0) for items classified as recurring.
      - name: net_current_month_mrr
        data_type: DOUBLE
        description: Sum over recurring items of charge_amount minus discount_amount with the same null handling.
      - name: gross_current_month_non_mrr
        data_type: DOUBLE
        description: Sum of charge_amount (invalid or NULL treated as 0.0) for items where charge_type is present and not 'recurring' (case-insensitive).
      - name: discount_current_month_non_mrr
        data_type: DOUBLE
        description: Sum of discount_amount (NULL treated as 0.0) for items where charge_type is present and not 'recurring' (case-insensitive).
      - name: net_current_month_non_mrr
        data_type: DOUBLE
        description: Sum over non-MRR items of charge_amount minus discount_amount with the same null handling.
```

## agent 最终 SQL

S4

```sql
WITH month_spine AS (
    SELECT DISTINCT account_id, CAST(date_trunc('month', service_start_day) AS DATE) AS account_month
    FROM intermediate.int_zuora__invoice_item_base
    WHERE service_start_day IS NOT NULL
),
classified_items AS (
    SELECT ii.account_id, CAST(date_trunc('month', ii.service_start_day) AS DATE) AS account_month,
           coalesce(try_cast(ii.charge_amount AS DOUBLE), 0.0) AS charge_amount,
           coalesce(ii.discount_amount, 0.0) AS discount_amount,
           lower(rpc.charge_type) = 'recurring' AS is_recurring,
           rpc.charge_type IS NOT NULL AND lower(rpc.charge_type) <> 'recurring' AS is_non_mrr
    FROM intermediate.int_zuora__invoice_item_base AS ii
    LEFT JOIN intermediate.int_zuora__rate_plan_charge_current AS rpc
        ON ii.rate_plan_charge_id = rpc.rate_plan_charge_id
    WHERE ii.service_start_day IS NOT NULL
)
SELECT ms.account_id, ms.account_month,
       coalesce(sum(CASE WHEN ci.is_recurring THEN ci.charge_amount ELSE 0.0 END), 0.0) AS gross_current_month_mrr,
       coalesce(sum(CASE WHEN ci.is_recurring THEN ci.discount_amount ELSE 0.0 END), 0.0) AS discount_current_month_mrr,
       coalesce(sum(CASE WHEN ci.is_recurring THEN ci.charge_amount - ci.discount_amount ELSE 0.0 END), 0.0) AS net_current_month_mrr,
       coalesce(sum(CASE WHEN ci.is_non_mrr THEN ci.charge_amount ELSE 0.0 END), 0.0) AS gross_current_month_non_mrr,
       coalesce(sum(CASE WHEN ci.is_non_mrr THEN ci.discount_amount ELSE 0.0 END), 0.0) AS discount_current_month_non_mrr,
       coalesce(sum(CASE WHEN ci.is_non_mrr THEN ci.charge_amount - ci.discount_amount ELSE 0.0 END), 0.0) AS net_current_month_non_mrr
FROM month_spine AS ms
LEFT JOIN classified_items AS ci ON ms.account_id = ci.account_id AND ms.account_month = ci.account_month
GROUP BY ms.account_id, ms.account_month
```

## gold SQL（仅供定位差异）

S5

```sql
with line_items as (
    select * from intermediate.int_zuora__invoice_item_base
), month_spine as (
    select
        li.account_id,
        cast(date_trunc('month', li.service_start_day) as date) as account_month
    from line_items li
    group by 1,2
), mrr_by_account as (
    select
        coalesce(ms.account_id, li.account_id) as account_id,
        coalesce(ms.account_month, cast(date_trunc('month', li.service_start_day) as date)) as account_month,
        sum(case when lower(rpc.charge_type) = 'recurring' then coalesce(try_cast(li.charge_amount as double), 0.0) else 0.0 end) as gross_current_month_mrr,
        sum(case when lower(rpc.charge_type) = 'recurring' then coalesce(li.discount_amount, 0.0) else 0.0 end) as discount_current_month_mrr,
        sum(case when lower(rpc.charge_type) = 'recurring' then coalesce(try_cast(li.charge_amount as double),0.0) - coalesce(li.discount_amount,0.0) else 0.0 end) as net_current_month_mrr,
        sum(case when lower(rpc.charge_type) != 'recurring' then coalesce(try_cast(li.charge_amount as double), 0.0) else 0.0 end) as gross_current_month_non_mrr,
        sum(case when lower(rpc.charge_type) != 'recurring' then coalesce(li.discount_amount, 0.0) else 0.0 end) as discount_current_month_non_mrr,
        sum(case when lower(rpc.charge_type) != 'recurring' then coalesce(try_cast(li.charge_amount as double),0.0) - coalesce(li.discount_amount,0.0) else 0.0 end) as net_current_month_non_mrr
    from month_spine ms
    left join line_items li
      on ms.account_id = li.account_id
     and ms.account_month = cast(date_trunc('month', li.service_start_day) as date)
    left join intermediate.int_zuora__rate_plan_charge_current rpc
      on rpc.rate_plan_charge_id = li.rate_plan_charge_id
    group by 1,2
)
select * from mrr_by_account
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5 | 6 | 0 | 1 | 1 | 1 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_month | 0 | 0 | 0 | DATE | DATE |
| gross_current_month_mrr | 0 | 0 | 0 | DOUBLE | DOUBLE |
| discount_current_month_mrr | 0 | 0 | 0 | DOUBLE | DOUBLE |
| net_current_month_mrr | 0 | 0 | 0 | DOUBLE | DOUBLE |
| gross_current_month_non_mrr | 0 | 0 | 0 | DOUBLE | DOUBLE |
| discount_current_month_non_mrr | 0 | 0 | 0 | DOUBLE | DOUBLE |
| net_current_month_non_mrr | 0 | 0 | 0 | DOUBLE | DOUBLE |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"account_id":"Subscription Revenue"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>6列；[{"column":"gross_current_month_mrr","value":"0.0"},{"column":"discount_current_month_mrr","value":"0.0"},{"column":"net_current_month_mrr","value":"0.0"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["gross_current_month_mrr","discount_current_month_mrr","net_current_month_mrr","gross_current_month_non_mrr","discount_current_month_non_mrr","net_current_month_non_mrr"],"nonnull_equal_rows":5,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["gross_current_month_mrr","discount_current_month_mrr","net_current_month_mrr","gross_current_month_non_mrr","discount_current_month_non_mrr","net_current_month_non_mrr"],"nonnull_equal_rows":5,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory 2026-10-25 06:03:38,793 - WARNING - Skipping zuora__monthly_recurring_revenue: missing sql/marts/zuora__monthly_recurring_revenue.sql</code> |

## 轨迹索引（不放输出原文）

本题事件总数：73；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -print -exec sh -c 'echo --- $1; wc -l "$1"' _ {} \; &amp;&amp; cat config/layer_dependencies.yaml</code> | 3638 | true | false |
| 15 | run | <code>python3 - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(len(x['staging_contract']['tables']), [t['name'] for t in x['staging_contract']['tables']])<br>print('inter', [m['name</code> | 1273 | true | false |
| 29 | run | <code>cat &gt; /tmp/build_models.py &lt;&lt;'PY'<br>from pathlib import Path<br>P=Path('sql/intermediate')<br>pass_models={<br>'int_zuora__account_current':('stg_zuora__account','is_most_recent_record = TRUE'),<br>'int_zuora__cont</code> | 0 | false | false |
| 31 | run | <code>python3 run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 8482 | true | false |
| 47 | run | <code>cat &gt; sql/marts/zuora__account_overview.sql &lt;&lt;'SQL'<br>WITH items_by_account AS (<br>    SELECT inv.account_id, count(DISTINCT ii.invoice_item_id) AS invoice_item_count<br>    FROM intermediate.int_zuora__invo</code> | 0 | false | false |
| 49 | run | <code>cat &gt; sql/marts/zuora__monthly_recurring_revenue.sql &lt;&lt;'SQL'<br>WITH month_spine AS (<br>    SELECT DISTINCT account_id, CAST(date_trunc('month', service_start_day) AS DATE) AS account_month<br>    FROM interm</code> | 0 | false | false |
| 51 | run | <code>python3 run.py &gt; /tmp/runlog 2&gt;&amp;1; grep -E 'ERROR&#124;WARNING:&#124;✓&#124;Execution failed&#124;successfully' /tmp/runlog &#124; tail -80</code> | 3588 | true | false |
| 55 | run | <code>python3 - &lt;&lt;'PY'<br>p='sql/marts/zuora__line_item_enhanced.sql';s=open(p).read().replace('CASE ii.processing_type WHEN', 'CASE CAST(ii.processing_type AS VARCHAR) WHEN').replace("ii.processing_type = '1'</code> | 1694 | true | false |

### agent action 的 thought/message 命中原句

event 49 / message

```text
Running command: cat > sql/marts/zuora__monthly_recurring_revenue.sql <<'SQL'
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-030.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/marts/zuora__monthly_recurring_revenue.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/marts/zuora__monthly_recurring_revenue.sql`
- S6: `records/006_contract_impl-030.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/result.md`
- S10: `data/024_packages_work/024_impl-030_zuora__monthly_recurring_revenue/024_impl-030_zuora__monthly_recurring_revenue.json`
- S11: `data/005_cs_work/impl-030_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/zuora.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions`
