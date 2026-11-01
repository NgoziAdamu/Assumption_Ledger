# impl-009_stg_google_play__earnings（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**多因并列**；把握：中；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`A`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 8000, "cell_scale": 184000}, "L1": {"row_scale": 8000, "cell_scale": 184000}, "L2": {"row_scale": 8000, "cell_scale": 184000}, "L3": {"row_scale": 8000, "cell_scale": 184000}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| transaction_date_source_policy | 已说出的选择 | 并列 | 8000 | 184000 | 1 |
| sku_source_policy | 已说出的选择 | 并列 | 8000 | 184000 | 1 |
| package_source_policy | Unstated Choice | 并列 | 8000 | 184000 | 4 |
| contract_other_default | Intent Misreading | 非原因 | 0 | 0 | 4 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: stg_google_play__earnings
      description: "Cleaned and standardized earnings transaction data from Google Play Console"
      source_table: "raw.earnings"
      columns:
        - name: amount_buyer_currency
          data_type: DECIMAL(18,3)
          validation_rules:
            - rule: "amount_buyer_currency >= -999999.99 AND amount_buyer_currency <= 999999.99"
              on_failure: nullify_field
        - name: amount_merchant_currency
          data_type: DECIMAL(18,3)
        - name: base_plan_id
          data_type: VARCHAR
        - name: buyer_country
          data_type: VARCHAR
        - name: buyer_currency
          data_type: VARCHAR
          validation_rules:
            - rule: "buyer_currency = UPPER(TRIM(buyer_currency))"
              on_failure: correct
            - rule: "LENGTH(buyer_currency) = 3"
              on_failure: nullify_field
        - name: buyer_postal_code
          data_type: DOUBLE
        - name: buyer_state
          data_type: VARCHAR
        - name: currency_conversion_rate
          data_type: DOUBLE
        - name: order_id
          data_type: VARCHAR
        - name: buyer_hardware
          data_type: DOUBLE
        - name: merchant_currency
          data_type: VARCHAR
        - name: offer_id
          data_type: VARCHAR
        - name: package_name
          data_type: VARCHAR
          constraints: [not_null]
        - name: product_title
          data_type: VARCHAR
        - name: product_type
          data_type: BOOLEAN
        - name: refund_type
          data_type: DOUBLE
        - name: sku_id
          data_type: VARCHAR
          constraints: [not_null]
        - name: tax_type
          data_type: DOUBLE
        - name: transaction_date
          data_type: DATE
          constraints: [not_null]
        - name: transaction_pt_timestamp
          data_type: TIMESTAMP
        - name: transaction_timezone
          data_type: VARCHAR
        - name: transaction_type
          data_type: VARCHAR
          constraints: [not_null]
          validation_rules:
            - rule: "transaction_type IN ('Charge', 'Refund', 'Other')"
              on_failure: nullify_field
            - rule: "transaction_type = COALESCE(transaction_type, 'Other')"
              on_failure: correct
        - name: _fivetran_synced
          data_type: VARCHAR

```

### 逐点结论

#### transaction_date_source_policy

并列；**已说出的选择**；把握中。

P：缺失必填transaction_date时，用transaction_time日期保留记录。契约未给来源映射或缺失源的补值政策；同名源全空而时间候选可解析，不能判定回填不合理。反事实选择不回填并执行该列必填约束。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 8000 | 0 | 184000 | 0 |
| L1 | 8000 | 0 | 184000 | 0 |
| L2 | 8000 | 0 | 184000 | 0 |
| L3 | 8000 | 0 | 184000 | 0 |

重跑：`records/039_checks/supplement_impl-009_stg_google_play__earnings.json` / `transaction_date_source_policy`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
Earnings 源数据 `transaction_date` 为空而 `transaction_time` 有值；为提供可用日期，暂用 `transaction_time` 日期部分回填。源 SKU 为空时用可用的 product/base-plan 值兜底。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__earnings.sql` / `SQL.text`（sql）：

```text
try_cast(substr(transaction_time, 1, 10) AS DATE) AS transaction_date
```

#### sku_source_policy

并列；**已说出的选择**；把握中。

P：缺失sku_id时可用product/base-plan兜底保留记录。契约未指定替代来源；核实显示sku_id/product_id全空、base_plan_id可用。反事实是不替代并执行该列必填约束。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 8000 | 0 | 184000 | 0 |
| L1 | 8000 | 0 | 184000 | 0 |
| L2 | 8000 | 0 | 184000 | 0 |
| L3 | 8000 | 0 | 184000 | 0 |

重跑：`records/039_checks/supplement_impl-009_stg_google_play__earnings.json` / `sku_source_policy`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / `67.args.final_thought`（delivery）：

```text
Earnings 源数据 `transaction_date` 为空而 `transaction_time` 有值；为提供可用日期，暂用 `transaction_time` 日期部分回填。源 SKU 为空时用可用的 product/base-plan 值兜底。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__earnings.sql` / `SQL.text`（sql）：

```text
CAST(coalesce(sku_id, product_id, base_plan_id) AS VARCHAR) AS sku_id
```

#### package_source_policy

并列；**Unstated Choice**；把握中。

P：package_name可以映射base_plan_id。没有同名原始字段，契约未给映射；product_id也是候选但本数据全空，不能仅凭gold选它认定Data。反事实用product_id并执行该列必填约束。finish的SKU说明不能推广到package_name。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 8000 | 0 | 184000 | 0 |
| L1 | 8000 | 0 | 184000 | 0 |
| L2 | 8000 | 0 | 184000 | 0 |
| L3 | 8000 | 0 | 184000 | 0 |

重跑：`records/039_checks/supplement_impl-009_stg_google_play__earnings.json` / `package_source_policy`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__earnings.sql` / `SQL.text`（sql）：

```text
CAST(base_plan_id AS VARCHAR) AS package_name
```

否定披露的审计范围：finish event 67 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### contract_other_default

非原因；**Intent Misreading**；把握高。

P：非法或缺失transaction_type保持NULL。契约明确COALESCE(transaction_type, Other)，应补Other；单改无改善仍保留非原因，不把旧output_not_null过滤的全匹配当正确算法。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 8000 | 8000 | 184000 | 184000 |
| L1 | 8000 | 8000 | 184000 | 184000 |
| L2 | 8000 | 8000 | 184000 | 184000 |
| L3 | 8000 | 8000 | 184000 | 184000 |

重跑：`records/021_extra_reruns_impl-009_stg_google_play__earnings.json` / `contract_other_default`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

标记：存在未确立的前提，但不是判错原因。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__earnings.sql` / `SQL.text`（sql）：

```text
CASE WHEN lower(trim(transaction_type)) = 'charge' THEN 'Charge' WHEN lower(trim(transaction_type)) = 'refund' THEN 'Refund' WHEN lower(trim(transaction_type)) = 'other' THEN 'Other' ELSE NULL END
```

否定披露的审计范围：finish event 67 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`，行[30, 97]；材料包 `records/021_packages/021_impl-009_stg_google_play__earnings.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__earnings.sql`；SHA-256 `e328a7b890e38f944ae156b02142671495d8f7df2470bbd1d4f738616f1af880`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/67.json` / event 67。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 16，失败=False。
  - `records/021_earnings_diagnostic.json` / index 0，失败=False。

## 不确定或没查到的（含规则问题）

- 规则问题：来源政策的“回填并保留/不回填并按必填排除”各含映射与该列过滤两步，按一个逻辑政策比较；三项反事实重叠，不相加贡献。把握中。
- 旧missing_required_source_policy替换整表，混入其他校验；output_not_null_policy仅因错误的transaction_type NULL删光而对上，均不用于主因排序。039拆开三列政策，保留Other默认的独立零贡献点。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
