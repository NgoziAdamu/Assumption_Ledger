# impl-030 · zuora__monthly_recurring_revenue

用途：**全量**；层：**marts**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**C**；把握：高。

month_spine额外排除NULL service_start_day，少一行；移除spine过滤L0全匹配，另一处分类输入过滤单改无贡献。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-030_zuora__monthly_recurring_revenue.md](../024_packages/024_impl-030_zuora__monthly_recurring_revenue.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
3742:     - name: zuora__monthly_recurring_revenue
3743:       description: Monthly sums of recurring vs non-recurring invoice amounts per account using the current rate plan charge type.
3744:       grain: One row per account_id and account_month (month of service_start_day)
3745:       source_models:
3746:       - intermediate.int_zuora__invoice_item_base
3747:       - intermediate.int_zuora__rate_plan_charge_current
3748:       business_logic: '- Inputs: - From intermediate.int_zuora__invoice_item_base: account_id, service_start_day, rate_plan_charge_id, charge_amount, discount_amount. - From intermediate.int_zuora__rate_plan_charge_current: rate_plan_charge_id, charge_type. - Build the month spine as distinct pairs of (account_id, month of service_start_day set to the first day). - Left join invoice items to the month spine on account_id and month; then left join the current rate plan charge on rate_plan_charge_id. - Classification for each invoice item: - Recurring (MRR): charge_type equals "recurring" when compared case-insensitively (no trimming). - Non-MRR: charge_type is present and, case-insensitively, not equal to "recurring". - If the rate plan charge is missing or charge_type is NULL, the item contributes 0 to both categories. - Per-line numeric handling: - charge_amount is converted to a DOUBLE; invalid or NULL values are treated as 0.0. - discount_amount treats NULL as 0.0; signs are preserved; no rounding or currency conversion. - If the rate plan charge join returns multiple matches for a line, that line’s amounts are counted multiple times. - Aggregations per (account_id, account_month): - Gross MRR: sum of charge_amount over recurring items. - Discount MRR: sum of discount_amount over recurring items. - Net MRR: sum over recurring items of (charge_amount minus discount_amount). - Gross non-MRR: sum of charge_amount over non-MRR items. - Discount non-MRR: sum of discount_amount over non-MRR items. - Net non-MRR: sum over non-MRR items of (charge_amount minus discount_amount). - Output includes every (account_id, account_month) from the month spine; if no items match a category, the corresponding sums are 0.0.'
3749:       columns:
3750:       - name: account_id
3751:         data_type: VARCHAR
3752:         description: Account identifier used for grouping.
3753:       - name: account_month
3754:         data_type: DATE
3755:         description: Month derived from service_start_day, set to the first day of that month.
3756:       - name: gross_current_month_mrr
3757:         data_type: DOUBLE
3758:         description: Sum of charge_amount (invalid or NULL treated as 0.0) for items classified as recurring (case-insensitive match to 'recurring').
3759:       - name: discount_current_month_mrr
3760:         data_type: DOUBLE
3761:         description: Sum of discount_amount (NULL treated as 0.0) for items classified as recurring.
3762:       - name: net_current_month_mrr
3763:         data_type: DOUBLE
3764:         description: Sum over recurring items of charge_amount minus discount_amount with the same null handling.
3765:       - name: gross_current_month_non_mrr
3766:         data_type: DOUBLE
3767:         description: Sum of charge_amount (invalid or NULL treated as 0.0) for items where charge_type is present and not 'recurring' (case-insensitive).
3768:       - name: discount_current_month_non_mrr
3769:         data_type: DOUBLE
3770:         description: Sum of discount_amount (NULL treated as 0.0) for items where charge_type is present and not 'recurring' (case-insensitive).
3771:       - name: net_current_month_non_mrr
3772:         data_type: DOUBLE
3773:         description: Sum over non-MRR items of charge_amount minus discount_amount with the same null handling.
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/marts/zuora__monthly_recurring_revenue.sql`；SHA-256 `8f2cd312a97b9f1fecf0970e0dbd324b4fedc276aa657a5541376e3533cbf068`。

```text
1: WITH month_spine AS (
2:     SELECT DISTINCT account_id, CAST(date_trunc('month', service_start_day) AS DATE) AS account_month
3:     FROM intermediate.int_zuora__invoice_item_base
4:     WHERE service_start_day IS NOT NULL
5: ),
6: classified_items AS (
7:     SELECT ii.account_id, CAST(date_trunc('month', ii.service_start_day) AS DATE) AS account_month,
8:            coalesce(try_cast(ii.charge_amount AS DOUBLE), 0.0) AS charge_amount,
9:            coalesce(ii.discount_amount, 0.0) AS discount_amount,
10:            lower(rpc.charge_type) = 'recurring' AS is_recurring,
11:            rpc.charge_type IS NOT NULL AND lower(rpc.charge_type) <> 'recurring' AS is_non_mrr
12:     FROM intermediate.int_zuora__invoice_item_base AS ii
13:     LEFT JOIN intermediate.int_zuora__rate_plan_charge_current AS rpc
14:         ON ii.rate_plan_charge_id = rpc.rate_plan_charge_id
15:     WHERE ii.service_start_day IS NOT NULL
16: )
17: SELECT ms.account_id, ms.account_month,
18:        coalesce(sum(CASE WHEN ci.is_recurring THEN ci.charge_amount ELSE 0.0 END), 0.0) AS gross_current_month_mrr,
19:        coalesce(sum(CASE WHEN ci.is_recurring THEN ci.discount_amount ELSE 0.0 END), 0.0) AS discount_current_month_mrr,
20:        coalesce(sum(CASE WHEN ci.is_recurring THEN ci.charge_amount - ci.discount_amount ELSE 0.0 END), 0.0) AS net_current_month_mrr,
21:        coalesce(sum(CASE WHEN ci.is_non_mrr THEN ci.charge_amount ELSE 0.0 END), 0.0) AS gross_current_month_non_mrr,
22:        coalesce(sum(CASE WHEN ci.is_non_mrr THEN ci.discount_amount ELSE 0.0 END), 0.0) AS discount_current_month_non_mrr,
23:        coalesce(sum(CASE WHEN ci.is_non_mrr THEN ci.charge_amount - ci.discount_amount ELSE 0.0 END), 0.0) AS net_current_month_non_mrr
24: FROM month_spine AS ms
25: LEFT JOIN classified_items AS ci ON ms.account_id = ci.account_id AND ms.account_month = ci.account_month
26: GROUP BY ms.account_id, ms.account_month
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/marts/zuora__monthly_recurring_revenue.sql`；SHA-256 `e75821dabe14b18c807b299a8243c39fa23a0e60a741545ad5233565c0b9132d`。

```text
1: with line_items as (
2:     select * from intermediate.int_zuora__invoice_item_base
3: ), month_spine as (
4:     select
5:         li.account_id,
6:         cast(date_trunc('month', li.service_start_day) as date) as account_month
7:     from line_items li
8:     group by 1,2
9: ), mrr_by_account as (
10:     select
11:         coalesce(ms.account_id, li.account_id) as account_id,
12:         coalesce(ms.account_month, cast(date_trunc('month', li.service_start_day) as date)) as account_month,
13:         sum(case when lower(rpc.charge_type) = 'recurring' then coalesce(try_cast(li.charge_amount as double), 0.0) else 0.0 end) as gross_current_month_mrr,
14:         sum(case when lower(rpc.charge_type) = 'recurring' then coalesce(li.discount_amount, 0.0) else 0.0 end) as discount_current_month_mrr,
15:         sum(case when lower(rpc.charge_type) = 'recurring' then coalesce(try_cast(li.charge_amount as double),0.0) - coalesce(li.discount_amount,0.0) else 0.0 end) as net_current_month_mrr,
16:         sum(case when lower(rpc.charge_type) != 'recurring' then coalesce(try_cast(li.charge_amount as double), 0.0) else 0.0 end) as gross_current_month_non_mrr,
17:         sum(case when lower(rpc.charge_type) != 'recurring' then coalesce(li.discount_amount, 0.0) else 0.0 end) as discount_current_month_non_mrr,
18:         sum(case when lower(rpc.charge_type) != 'recurring' then coalesce(try_cast(li.charge_amount as double),0.0) - coalesce(li.discount_amount,0.0) else 0.0 end) as net_current_month_non_mrr
19:     from month_spine ms
20:     left join line_items li
21:       on ms.account_id = li.account_id
22:      and ms.account_month = cast(date_trunc('month', li.service_start_day) as date)
23:     left join intermediate.int_zuora__rate_plan_charge_current rpc
24:       on rpc.rate_plan_charge_id = li.rate_plan_charge_id
25:     group by 1,2
26: )
27: select * from mrr_by_account
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- spine_null_month（C）：**看到了但没提**；事件 49、59、60。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 49：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/49.json`；命令首行：`cat > sql/marts/zuora__monthly_recurring_revenue.sql <<'SQL'`。
event 59：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/59.json`；命令首行：`sed -i 's/ip.payment_method_id AS invoice_payment_method_id,/-- invoice payment method is not projected; method is taken from the matched payment\n           /' sql/marts/zuora__line_item_enhanced.sql`。
event 60：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/60.json`；原始观察输出。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

已基于 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 Zuora SQL pipeline，按 staging → intermediate → marts 顺序写入 `sql/`，共 42 个 SQL 文件（18 staging、17 intermediate、7 marts）。SQL 使用 DuckDB 语法和直接的 `schema.table` 上游引用，不含 dbt `ref()`，文件末尾均无分号。

**验证结果**
- `python3 run.py` 成功，构建 `zuora.duckdb`；三个层级所有模型均成功执行。
- 数据质量抽查：staging account 的状态均在 Active/Draft/Cancelled 内，account_id 无重复；invoice_base 的 invoice_id 无重复；line_item_history 的 invoice_item_id 无 NULL。
- 生成 SQL 文件未以分号结束。

**契约说明**
- Staging 采用安全类型转换、删除标记过滤、更新时间驱动的最新记录标记；账户状态按契约规范化/过滤，invoice 创建日期按契约限制时间范围。
- Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。非关键不可解析值转为 NULL。
- 合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。
- 最新记录出现并列时按源更新时间标记，不额外去重；上游重复最新记录可能导致下游一对多连接放大，符合模型保留重复记录的合同语义。

开发期间修复了标识字段映射和 processing_type 比较问题；最终运行无失败 SQL。
```

## 查询

核实查询 **1** 条；代价档：**一条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：agent可见NULL服务日期
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE service_start_day IS NULL) missing FROM intermediate.int_zuora__invoice_item_base
```


```json
{"columns":["n","missing"],"rows":[[1495,1490]]}
```

## 独立单点重跑

### 024_reruns_impl-030_zuora__monthly_recurring_revenue.json
[024_reruns_impl-030_zuora__monthly_recurring_revenue.json](../024_reruns_impl-030_zuora__monthly_recurring_revenue.json)
上游：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|6|1|8|否|
|L1|5|6|1|8|否|
|L2|5|6|1|8|否|
|L3|5|6|1|8|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1,"account_month":1,"discount_current_month_mrr":1,"discount_current_month_non_mrr":1,"gross_current_month_mrr":1,"gross_current_month_non_mrr":1,"net_current_month_mrr":1,"net_current_month_non_mrr":1}`
- L1：`{"account_id":1,"account_month":1,"discount_current_month_mrr":1,"discount_current_month_non_mrr":1,"gross_current_month_mrr":1,"gross_current_month_non_mrr":1,"net_current_month_mrr":1,"net_current_month_non_mrr":1}`
- L2：`{"account_id":1,"account_month":1,"discount_current_month_mrr":1,"discount_current_month_non_mrr":1,"gross_current_month_mrr":1,"gross_current_month_non_mrr":1,"net_current_month_mrr":1,"net_current_month_non_mrr":1}`
- L3：`{"account_id":1,"account_month":1,"discount_current_month_mrr":1,"discount_current_month_non_mrr":1,"gross_current_month_mrr":1,"gross_current_month_non_mrr":1,"net_current_month_mrr":1,"net_current_month_non_mrr":1}`

#### baseline
私有SQL：`data/024_work/impl-030_zuora__monthly_recurring_revenue/baseline.sql`；SHA-256 `8f2cd312a97b9f1fecf0970e0dbd324b4fedc276aa657a5541376e3533cbf068`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|6|1|8|否|
|L1|5|6|1|8|否|
|L2|5|6|1|8|否|
|L3|5|6|1|8|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1,"account_month":1,"discount_current_month_mrr":1,"discount_current_month_non_mrr":1,"gross_current_month_mrr":1,"gross_current_month_non_mrr":1,"net_current_month_mrr":1,"net_current_month_non_mrr":1}`
- L1：`{"account_id":1,"account_month":1,"discount_current_month_mrr":1,"discount_current_month_non_mrr":1,"gross_current_month_mrr":1,"gross_current_month_non_mrr":1,"net_current_month_mrr":1,"net_current_month_non_mrr":1}`
- L2：`{"account_id":1,"account_month":1,"discount_current_month_mrr":1,"discount_current_month_non_mrr":1,"gross_current_month_mrr":1,"gross_current_month_non_mrr":1,"net_current_month_mrr":1,"net_current_month_non_mrr":1}`
- L3：`{"account_id":1,"account_month":1,"discount_current_month_mrr":1,"discount_current_month_non_mrr":1,"gross_current_month_mrr":1,"gross_current_month_non_mrr":1,"net_current_month_mrr":1,"net_current_month_non_mrr":1}`

#### spine_null_month
主因；类别候选C。契约要求输出spine的每个account/month；额外过滤NULL月份丢一行。
相对本轮基线：行减少1，格减少8。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第4行、offset 175起替换；其他字节相同。
原表达式：
```sql
    WHERE service_start_day IS NOT NULL
```

修改后：
```sql
    WHERE TRUE
```

私有SQL：`data/024_work/impl-030_zuora__monthly_recurring_revenue/spine_null_month.sql`；SHA-256 `53e6dd588c591aae98870087ca1217d6ea7ee6f7a4f7d7c35f9b80d75a18ae39`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|6|6|0|0|是|
|L1|6|6|0|0|是|
|L2|6|6|0|0|是|
|L3|6|6|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

#### items_null_month
不计参与因素；类别候选C。分类输入另有一个非空日期过滤，独立检验其贡献。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第15行、offset 833起替换；其他字节相同。
原表达式：
```sql
    WHERE ii.service_start_day IS NOT NULL
```

修改后：
```sql
    WHERE TRUE
```

私有SQL：`data/024_work/impl-030_zuora__monthly_recurring_revenue/items_null_month.sql`；SHA-256 `66d1a4cbef1435cb7a83461ad85f3f955071abee8859197873be99ff0dfa7fae`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|5|6|1|8|否|
|L1|5|6|1|8|否|
|L2|5|6|1|8|否|
|L3|5|6|1|8|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":1,"account_month":1,"discount_current_month_mrr":1,"discount_current_month_non_mrr":1,"gross_current_month_mrr":1,"gross_current_month_non_mrr":1,"net_current_month_mrr":1,"net_current_month_non_mrr":1}`
- L1：`{"account_id":1,"account_month":1,"discount_current_month_mrr":1,"discount_current_month_non_mrr":1,"gross_current_month_mrr":1,"gross_current_month_non_mrr":1,"net_current_month_mrr":1,"net_current_month_non_mrr":1}`
- L2：`{"account_id":1,"account_month":1,"discount_current_month_mrr":1,"discount_current_month_non_mrr":1,"gross_current_month_mrr":1,"gross_current_month_non_mrr":1,"net_current_month_mrr":1,"net_current_month_non_mrr":1}`
- L3：`{"account_id":1,"account_month":1,"discount_current_month_mrr":1,"discount_current_month_non_mrr":1,"gross_current_month_mrr":1,"gross_current_month_non_mrr":1,"net_current_month_mrr":1,"net_current_month_non_mrr":1}`
## 规则问题

无。

