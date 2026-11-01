# impl-009_google_play__finance_report（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Quiet Downgrade**；把握：中；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`D`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 3144, "cell_scale": 62880}, "L1": {"row_scale": 3144, "cell_scale": 62880}, "L2": {"row_scale": 3144, "cell_scale": 62880}, "L3": {"row_scale": 3144, "cell_scale": 62880}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| 同类缺口组：机械fallback投影 | Quiet Downgrade | 主要 | 3144 | 62880 | 2 |

### 契约原句（所有点共用，逐字回查event1）

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

### 逐点结论

#### 同类缺口组：机械fallback投影

主要；**Quiet Downgrade**；把握中。

同类缺口组：earnings和subscription事件连接；国家/商品维度、收入转换/汇总、订阅及滚动窗口。event39用同一个fallback循环，取source_models[0]、只投影少数维度，其余常量/NULL；整表没有实现要求的关系。该首源在CS可为空，缺少其他分支仍是本表自己的缺口。只能整体诊断的机械生成模型按第7节同类候选处理，不能称每个字段都已单改。

是否说出：第2档——交付物里只有通用说明。报告未针对本处，只给适用于本类处理的通用说明；不把它升级成第1档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 3144 | 0 | 62880 | 0 |
| L1 | 3144 | 0 | 62880 | 0 |
| L2 | 3144 | 0 | 62880 | 0 |
| L3 | 3144 | 0 | 62880 | 0 |

重跑：`records/021_reruns_impl-009_google_play__finance_report.json` / `whole_implementation_diagnostic`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
留存、app quality 及多项 marts 的完整 join、窗口计算、聚合、评分和分类逻辑尚未实现；部分模型仅提供兼容字段结构的可执行 SQL，其中若干指标为 NULL 或常量占位。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__finance_report.sql` / `SQL.text`（sql）：

```text
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


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`，行[1723, 1792]；材料包 `records/021_packages/021_impl-009_google_play__finance_report.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/marts/google_play__finance_report.sql`；SHA-256 `30ff9e99089346b996333ceab16e8d7cf309a534d9e6c58d269fbb7314398b71`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / event 67。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 13，失败=True。
  - `records/021_supplement_queries.json` / index 14，失败=False。

## 不确定或没查到的（含规则问题）

- 规则问题：按用户允许的同脚本机械生成例外记一个同类缺口组；只确立类别，不从整表恢复推导各子指标贡献。event39原脚本见轨迹审计。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
