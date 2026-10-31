# DAComp / impl-003_customer360__address（v3）

## 错在哪里
地址内容一致，差异仅为契约明确允许任意排列的同priority地址rank。

证据复用入口：[018_impl-003_customer360__address.md](../018_annotations/018_impl-003_customer360__address.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## rank_tie_order
- 角色：主要；类别：**其他**；把握：中。
- 依据：契约明确同priority顺序unspecified and non-deterministic；双侧去rank多重集合一致，6904行/格仅rank差异。
- 是否说出：只有通用策略说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 51 / args.final_thought：
```text
契约对来源重复记录以及部分聚合排序并未规定唯一 tie-breaker；按 DuckDB 实际行为保留未指定并列顺序，不额外引入业务假设。
```

## 规模、证据复用与新做
主要原因：其他。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-003_customer360__address.md](../018_annotations/018_impl-003_customer360__address.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: customer360__address
      description: Consolidated customer addresses from Marketo and Stripe enriched with standardized country/state names and priority-based ranking
      grain: One row per sourced address per customer360_id (duplicates preserved)
      source_models:
      - marts.customer360__mapping
      - intermediate.int_customer360__marketo
      - intermediate.int_customer360__stripe
      - staging.stg_customer360__country_codes
      - staging.stg_customer360__state_territory_codes
      business_logic: '- Read pass-through datasets: - marts.customer360__mapping as mapping (provides marketo_lead_id and stripe_customer_id per customer360_id) - staging.stg_customer360__country_codes as country_codes - staging.stg_customer360__state_territory_codes as state_codes - Build Marketo addresses (inner join mapping.marketo_lead_id = int_customer360__marketo.lead_id): - Primary address: include rows where address_line_1 is not NULL; set source_system = "marketo", address_type = "primary", priority = 1; select address_line_1, address_line_2, city, state_code, country_code, postal_code - Billing address: include rows where billing_address_line_1 is not NULL; set source_system = "marketo", address_type = "billing", priority = 2; map billing_* fields to output columns - Build Stripe addresses (inner join mapping.stripe_customer_id = int_customer360__stripe.customer_id): - Customer address: include rows where customer_address_line_1 is not NULL; set source_system = "stripe", address_type = "customer", priority = 1; map customer_* fields - Shipping address: include rows where shipping_address_line_1 is not NULL; set source_system = "stripe", address_type = "shipping", priority = 2; map shipping_* fields - Union all Marketo and Stripe address rows; no de-duplication; only addresses with non-NULL address_line_1 are included. - Enrich with geographic names via left joins: - state: join state_codes on (state_code AND country_code) to derive state_territory; unmatched → NULL - country and country_alt_name: join country_codes on alpha-2 country code; unmatched → NULL - Compute rank: per customer360_id, assign row numbers ordered by priority ascending; within the same priority, order is unspecified and non-deterministic. - Output passes through source text as-is (casing/whitespace preserved); no normalization beyond the joins.'
      columns:
      - name: customer360_id
        data_type: VARCHAR
        description: Customer key from mapping used to group and rank addresses; multiple rows per customer360_id
      - name: source_system
        data_type: VARCHAR
        description: Origin system literal ('marketo' or 'stripe'); set per source and always non-null
      - name: address_type
        data_type: VARCHAR
        description: 'Address category set per source: Marketo → ''primary'' or ''billing''; Stripe → ''customer'' or ''shipping'''
      - name: address_line_1
        data_type: VARCHAR
        description: Primary address line; rows are included only when this is non-null; text is passed through without trimming or case changes
      - name: address_line_2
        data_type: VARCHAR
        description: Secondary address line from source; may be null; text is passed through without trimming or case changes
      - name: city
        data_type: VARCHAR
        description: City from source; may be null; no transformation
      - name: state_code
        data_type: VARCHAR
        description: State/province code from source used for state name enrichment; may be null; case preserved
      - name: state
        data_type: VARCHAR
        description: Resolved state/territory name from stg_customer360__state_territory_codes via (state_code,country_code) match; null if no match
      - name: country_code
        data_type: VARCHAR
        description: ISO alpha-2 country code from source used for joins; may be null; case preserved
      - name: country
        data_type: VARCHAR
        description: Resolved country name from stg_customer360__country_codes via country_code_alpha_2; null if no match
      - name: country_alt_name
        data_type: VARCHAR
        description: Alternative country name from stg_customer360__country_codes; null if no match
      - name: postal_code
        data_type: BIGINT
        description: Postal code from source stored as BIGINT; may be null; numeric-only storage means leading zeros are not preserved
      - name: priority
        data_type: INTEGER
        description: Address priority set by source (1 for primary/customer, 2 for billing/shipping); lower number indicates higher priority
      - name: rank
        data_type: BIGINT
        description: Row number per customer360_id ordered by priority ascending; ties within the same priority have arbitrary order
```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-003_customer360__address.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-003_customer360__address.md:86)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-003_customer360__address.md:293)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-003_customer360__address.md:326)
