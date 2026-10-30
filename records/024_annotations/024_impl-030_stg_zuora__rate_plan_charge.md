# impl-030 · stg_zuora__rate_plan_charge

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**多因并列（A、U）**；把握：中。

统一pk_alias将不同关系字段都映射本实体id；各输出位置独立修复。具名候选能与相关表形成明确对应的按U，其余源字段错位或无法定语义的按A；契约类型与gold透传冲突按O。

参与因素：无。
标记：证据曾出现但被忽略。

## 材料与比较口径

[024_impl-030_stg_zuora__rate_plan_charge.md](../024_packages/024_impl-030_stg_zuora__rate_plan_charge.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
695:     - name: stg_zuora__rate_plan_charge
696:       description: "Cleaned rate plan charges with monetary and timing metadata; latest snapshot indicator."
697:       source_table: raw.zuora_rate_plan_charge_data
698:       columns:
699:         - name: rate_plan_charge_id
700:           data_type: VARCHAR
701:           source_expression: "id"
702:         - name: account_id
703:           data_type: VARCHAR
704:         - name: account_receivable_accounting_code_id
705:           data_type: VARCHAR
706:         - name: accounting_code
707:           data_type: VARCHAR
708:         - name: amended_by_order_on
709:           data_type: DATE
710:         - name: amendment_id
711:           data_type: VARCHAR
712:         - name: apply_discount_to
713:           data_type: VARCHAR
714:         - name: bill_cycle_day
715:           data_type: BOOLEAN
716:         - name: bill_cycle_type
717:           data_type: VARCHAR
718:         - name: bill_to_contact_id
719:           data_type: VARCHAR
720:         - name: bill_to_contact_snapshot_id
721:           data_type: VARCHAR
722:         - name: billing_period
723:           data_type: VARCHAR
724:         - name: billing_timing
725:           data_type: VARCHAR
726:         - name: booking_exchange_rate
727:           data_type: BIGINT
728:         - name: booking_exchange_rate_date
729:           data_type: DATE
730:         - name: charge_model
731:           data_type: VARCHAR
732:         - name: charge_number
733:           data_type: VARCHAR
734:         - name: charge_type
735:           data_type: VARCHAR
736:         - name: charged_through_date
737:           data_type: DATE
738:         - name: created_by_id
739:           data_type: VARCHAR
740:         - name: created_date
741:           data_type: TIMESTAMP
742:           source_expression: "cast(created_date as TIMESTAMP)"
743:         - name: credit_option
744:           data_type: VARCHAR
745:         - name: default_payment_method_id
746:           data_type: VARCHAR
747:         - name: deferred_revenue_accounting_code_id
748:           data_type: VARCHAR
749:         - name: description
750:           data_type: VARCHAR
751:         - name: discount_level
752:           data_type: VARCHAR
753:         - name: dmrc
754:           data_type: BIGINT
755:         - name: dmrchome_currency
756:           data_type: BIGINT
757:         - name: dtcv
758:           data_type: BIGINT
759:         - name: dtcvhome_currency
760:           data_type: BIGINT
761:         - name: effective_end_date
762:           data_type: DATE
763:         - name: effective_start_date
764:           data_type: DATE
765:         - name: end_date_condition
766:           data_type: VARCHAR
767:         - name: exchange_rate
768:           data_type: BIGINT
769:         - name: exchange_rate_date
770:           data_type: DATE
771:         - name: home_currency
772:           data_type: VARCHAR
773:         - name: is_prepaid
774:           data_type: BOOLEAN
775:         - name: is_processed
776:           data_type: BOOLEAN
777:         - name: mrr
778:           data_type: BIGINT
779:         - name: mrrhome_currency
780:           data_type: BIGINT
781:         - name: name
782:           data_type: VARCHAR
783:         - name: number_of_periods
784:           data_type: VARCHAR
785:         - name: original_id
786:           data_type: VARCHAR
787:         - name: original_order_date
788:           data_type: DATE
789:         - name: price_change_option
790:           data_type: VARCHAR
791:         - name: price_increase_percentage
792:           data_type: BOOLEAN
793:         - name: processed_through_date
794:           data_type: DATE
795:         - name: product_id
796:           data_type: VARCHAR
797:         - name: product_rate_plan_charge_id
798:           data_type: VARCHAR
799:         - name: product_rate_plan_id
800:           data_type: VARCHAR
801:         - name: quantity
802:           data_type: BIGINT
803:         - name: rate_plan_id
804:           data_type: VARCHAR
805:         - name: recognized_revenue_accounting_code_id
806:           data_type: VARCHAR
807:         - name: segment
808:           data_type: BOOLEAN
809:         - name: sold_to_contact_id
810:           data_type: VARCHAR
811:         - name: specific_billing_period
812:           data_type: VARCHAR
813:         - name: specific_end_date
814:           data_type: VARCHAR
815:         - name: specific_list_price_base
816:           data_type: VARCHAR
817:         - name: subscription_id
818:           data_type: VARCHAR
819:         - name: tcv
820:           data_type: BIGINT
821:         - name: tcvhome_currency
822:           data_type: BIGINT
823:         - name: transaction_currency
824:           data_type: VARCHAR
825:         - name: trigger_date
826:           data_type: VARCHAR
827:         - name: trigger_event
828:           data_type: VARCHAR
829:         - name: uom
830:           data_type: VARCHAR
831:         - name: up_to_periods
832:           data_type: VARCHAR
833:         - name: up_to_periods_type
834:           data_type: VARCHAR
835:         - name: updated_by_id
836:           data_type: VARCHAR
837:         - name: updated_date
838:           data_type: TIMESTAMP
839:           source_expression: "cast(updated_date as TIMESTAMP)"
840:         - name: version
841:           data_type: BIGINT
842:         - name: weekly_bill_cycle_day
843:           data_type: VARCHAR
844:         - name: is_most_recent_record
845:           data_type: BOOLEAN
846:           source_expression: "row_number() over (partition by id order by updated_date desc) = 1"
847:       row_filters:
848:         - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
849:           on_failure: delete_row
850:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__rate_plan_charge.sql`；SHA-256 `e12db07ba829aa50b998dad02c8c78c22436d62aaab89db5f62c6665d3717c6b`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_rate_plan_charge_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         id AS rate_plan_charge_id,
7:         try_cast("id" AS VARCHAR) AS account_id,
8:         try_cast("account_receivable_accounting_code_id" AS VARCHAR) AS account_receivable_accounting_code_id,
9:         try_cast("accounting_code" AS VARCHAR) AS accounting_code,
10:         try_cast("amended_by_order_on" AS DATE) AS amended_by_order_on,
11:         try_cast("id" AS VARCHAR) AS amendment_id,
12:         try_cast("apply_discount_to" AS VARCHAR) AS apply_discount_to,
13:         try_cast("bill_cycle_day" AS BOOLEAN) AS bill_cycle_day,
14:         try_cast("bill_cycle_type" AS VARCHAR) AS bill_cycle_type,
15:         try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
16:         try_cast("bill_to_contact_snapshot_id" AS VARCHAR) AS bill_to_contact_snapshot_id,
17:         try_cast("billing_period" AS VARCHAR) AS billing_period,
18:         try_cast("billing_timing" AS VARCHAR) AS billing_timing,
19:         try_cast("booking_exchange_rate" AS BIGINT) AS booking_exchange_rate,
20:         try_cast("booking_exchange_rate_date" AS DATE) AS booking_exchange_rate_date,
21:         try_cast("charge_model" AS VARCHAR) AS charge_model,
22:         try_cast("charge_number" AS VARCHAR) AS charge_number,
23:         try_cast("charge_type" AS VARCHAR) AS charge_type,
24:         try_cast("charged_through_date" AS DATE) AS charged_through_date,
25:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
26:         try_cast(created_date as TIMESTAMP) AS created_date,
27:         try_cast("credit_option" AS VARCHAR) AS credit_option,
28:         try_cast("default_payment_method_id" AS VARCHAR) AS default_payment_method_id,
29:         try_cast("deferred_revenue_accounting_code_id" AS VARCHAR) AS deferred_revenue_accounting_code_id,
30:         try_cast("description" AS VARCHAR) AS description,
31:         try_cast("discount_level" AS VARCHAR) AS discount_level,
32:         try_cast("dmrc" AS BIGINT) AS dmrc,
33:         try_cast("dmrchome_currency" AS BIGINT) AS dmrchome_currency,
34:         try_cast("dtcv" AS BIGINT) AS dtcv,
35:         try_cast("dtcvhome_currency" AS BIGINT) AS dtcvhome_currency,
36:         try_cast("effective_end_date" AS DATE) AS effective_end_date,
37:         try_cast("effective_start_date" AS DATE) AS effective_start_date,
38:         try_cast("end_date_condition" AS VARCHAR) AS end_date_condition,
39:         try_cast("exchange_rate" AS BIGINT) AS exchange_rate,
40:         try_cast("exchange_rate_date" AS DATE) AS exchange_rate_date,
41:         try_cast("home_currency" AS VARCHAR) AS home_currency,
42:         try_cast("is_prepaid" AS BOOLEAN) AS is_prepaid,
43:         try_cast("is_processed" AS BOOLEAN) AS is_processed,
44:         try_cast("mrr" AS BIGINT) AS mrr,
45:         try_cast("mrrhome_currency" AS BIGINT) AS mrrhome_currency,
46:         try_cast("name" AS VARCHAR) AS name,
47:         try_cast("number_of_periods" AS VARCHAR) AS number_of_periods,
48:         try_cast("original_id" AS VARCHAR) AS original_id,
49:         try_cast("original_order_date" AS DATE) AS original_order_date,
50:         try_cast("price_change_option" AS VARCHAR) AS price_change_option,
51:         try_cast("price_increase_percentage" AS BOOLEAN) AS price_increase_percentage,
52:         try_cast("processed_through_date" AS DATE) AS processed_through_date,
53:         try_cast("id" AS VARCHAR) AS product_id,
54:         try_cast("product_rate_plan_charge_id" AS VARCHAR) AS product_rate_plan_charge_id,
55:         try_cast("id" AS VARCHAR) AS product_rate_plan_id,
56:         try_cast("quantity" AS BIGINT) AS quantity,
57:         try_cast("id" AS VARCHAR) AS rate_plan_id,
58:         try_cast("recognized_revenue_accounting_code_id" AS VARCHAR) AS recognized_revenue_accounting_code_id,
59:         try_cast("segment" AS BOOLEAN) AS segment,
60:         try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
61:         try_cast("specific_billing_period" AS VARCHAR) AS specific_billing_period,
62:         try_cast("specific_end_date" AS VARCHAR) AS specific_end_date,
63:         try_cast("specific_list_price_base" AS VARCHAR) AS specific_list_price_base,
64:         try_cast("id" AS VARCHAR) AS subscription_id,
65:         try_cast("tcv" AS BIGINT) AS tcv,
66:         try_cast("tcvhome_currency" AS BIGINT) AS tcvhome_currency,
67:         try_cast("transaction_currency" AS VARCHAR) AS transaction_currency,
68:         try_cast("trigger_date" AS VARCHAR) AS trigger_date,
69:         try_cast("trigger_event" AS VARCHAR) AS trigger_event,
70:         try_cast("uom" AS VARCHAR) AS uom,
71:         try_cast("up_to_periods" AS VARCHAR) AS up_to_periods,
72:         try_cast("up_to_periods_type" AS VARCHAR) AS up_to_periods_type,
73:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
74:         try_cast(updated_date as TIMESTAMP) AS updated_date,
75:         try_cast("version" AS BIGINT) AS version,
76:         try_cast("weekly_bill_cycle_day" AS VARCHAR) AS weekly_bill_cycle_day,
77:         row_number() over (partition by id order by updated_date desc) = 1 AS is_most_recent_record
78: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__rate_plan_charge.sql`；SHA-256 `c9525c53169aab957d677522981226a1d75ad37ed69cecd90b213194a9298076`。

```text
1: with base as (
2:     select * from raw.zuora_rate_plan_charge_data
3:     where _fivetran_deleted is null or _fivetran_deleted = false
4: ),
5: final as (
6:     select
7:         id as rate_plan_charge_id,
8:         account_id,
9:         account_receivable_accounting_code_id,
10:         accounting_code,
11:         amended_by_order_on,
12:         amendment_id,
13:         apply_discount_to,
14:         bill_cycle_day,
15:         bill_cycle_type,
16:         bill_to_contact_id,
17:         bill_to_contact_snapshot_id,
18:         billing_period,
19:         billing_timing,
20:         booking_exchange_rate,
21:         booking_exchange_rate_date,
22:         charge_model,
23:         charge_number,
24:         charge_type,
25:         charged_through_date,
26:         created_by_id,
27:         cast(created_date as TIMESTAMP) as created_date,
28:         credit_option,
29:         default_payment_method_id,
30:         deferred_revenue_accounting_code_id,
31:         description,
32:         discount_level,
33:         dmrc,
34:         dmrchome_currency,
35:         dtcv,
36:         dtcvhome_currency,
37:         effective_end_date,
38:         effective_start_date,
39:         end_date_condition,
40:         exchange_rate,
41:         exchange_rate_date,
42:         home_currency,
43:         is_prepaid,
44:         is_processed,
45:         mrr,
46:         mrrhome_currency,
47:         name,
48:         number_of_periods,
49:         original_id,
50:         original_order_date,
51:         price_change_option,
52:         price_increase_percentage,
53:         processed_through_date,
54:         product_id,
55:         product_rate_plan_charge_id,
56:         product_rate_plan_id,
57:         quantity,
58:         rate_plan_id,
59:         recognized_revenue_accounting_code_id,
60:         segment,
61:         sold_to_contact_id,
62:         specific_billing_period,
63:         specific_end_date,
64:         specific_list_price_base,
65:         subscription_id,
66:         tcv,
67:         tcvhome_currency,
68:         transaction_currency,
69:         trigger_date,
70:         trigger_event,
71:         uom,
72:         up_to_periods,
73:         up_to_periods_type,
74:         updated_by_id,
75:         cast(updated_date as TIMESTAMP) as updated_date,
76:         version,
77:         weekly_bill_cycle_day,
78:         row_number() over (partition by id order by updated_date desc) = 1 as is_most_recent_record
79:     from base
80: )
81: select * from final
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- source_account_id（U）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

P：本实体 id 可以代表 account_id。
P：本实体id可替代account_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
U前三条件依据agent可见查询和event45生成规则；报告给出的统一id映射策略未核验具体关系。

- source_amendment_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```


- source_product_id（U）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

P：本实体 id 可以代表 product_id。
P：本实体id可替代product_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
U前三条件依据agent可见查询和event45生成规则；报告给出的统一id映射策略未核验具体关系。

- source_product_rate_plan_id（U）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

P：本实体 id 可以代表 product_rate_plan_id。
P：本实体id可替代product_rate_plan_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
U前三条件依据agent可见查询和event45生成规则；报告给出的统一id映射策略未核验具体关系。

- source_rate_plan_id（U）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

P：本实体 id 可以代表 rate_plan_id。
P：本实体id可替代rate_plan_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
U前三条件依据agent可见查询和event45生成规则；报告给出的统一id映射策略未核验具体关系。

- source_subscription_id（A）：**只有通用策略说明**；事件 13、14、39、40、45、69。
原句：

```
Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。
```

event 13：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/13.json`；命令首行：`python3 - <<'PY'`。
event 14：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/14.json`；原始观察输出。
event 39：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/39.json`；命令首行：`python3 - <<'PY'`。
event 40：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/40.json`；原始观察输出。
event 45：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/45.json`；命令首行：`python3 - <<'PY'`。
event 69：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-030/agent/.events/sessions/f8c97c43-02e0-4b-4f9e73ebc5e1791/events/69.json`；命令首行：`find / -maxdepth 3 -type d -name workspace 2>/dev/null | head; cat > result.md <<'EOF'`。

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

核实查询 **5** 条；代价档：**多条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：直接raw列名类型
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_rate_plan_charge_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_rate_plan_charge_data","id","VARCHAR"],["zuora_rate_plan_charge_data","_fivetran_deleted","BOOLEAN"],["zuora_rate_plan_charge_data","_fivetran_synced","TIMESTAMP"],["zuora_rate_plan_charge_data","account_id","VARCHAR"],["zuora_rate_plan_charge_data","account_receivable_accounting_code_id","VARCHAR"],["zuora_rate_plan_charge_data","accounting_code","VARCHAR"],["zuora_rate_plan_charge_data","amended_by_order_on","DATE"],["zuora_rate_plan_charge_data","amendment_id","VARCHAR"],["zuora_rate_plan_charge_data","apply_discount_to","VARCHAR"],["zuora_rate_plan_charge_data","bill_cycle_day","BIGINT"],["zuora_rate_plan_charge_data","bill_cycle_type","VARCHAR"],["zuora_rate_plan_charge_data","bill_to_contact_id","VARCHAR"],["zuora_rate_plan_charge_data","bill_to_contact_snapshot_id","VARCHAR"],["zuora_rate_plan_charge_data","billing_period","VARCHAR"],["zuora_rate_plan_charge_data","billing_period_alignment","VARCHAR"],["zuora_rate_plan_charge_data","billing_timing","VARCHAR"],["zuora_rate_plan_charge_data","booking_exchange_rate","BIGINT"],["zuora_rate_plan_charge_data","booking_exchange_rate_date","DATE"],["zuora_rate_plan_charge_data","booking_provider_exchange_rate_date","DATE"],["zuora_rate_plan_charge_data","charge_model","VARCHAR"],["zuora_rate_plan_charge_data","charge_number","VARCHAR"],["zuora_rate_plan_charge_data","charge_type","VARCHAR"],["zuora_rate_plan_charge_data","charged_through_date","DATE"],["zuora_rate_plan_charge_data","created_by_id","VARCHAR"],["zuora_rate_plan_charge_data","created_date","TIMESTAMP"],["zuora_rate_plan_charge_data","default_payment_method_id","VARCHAR"],["zuora_rate_plan_charge_data","deferred_revenue_accounting_code_id","VARCHAR"],["zuora_rate_plan_charge_data","description","VARCHAR"],["zuora_rate_plan_charge_data","discount_level","VARCHAR"],["zuora_rate_plan_charge_data","dmrc","BIGINT"],["zuora_rate_plan_charge_data","dmrccurrency_rounding","BIGINT"],["zuora_rate_plan_charge_data","dmrchome_currency","BIGINT"],["zuora_rate_plan_charge_data","drawdown_rate","BIGINT"],["zuora_rate_plan_charge_data","drawdown_uom","VARCHAR"],["zuora_rate_plan_charge_data","dtcv","BIGINT"],["zuora_rate_plan_charge_data","dtcvcurrency_rounding","BIGINT"],["zuora_rate_plan_charge_data","dtcvhome_currency","BIGINT"],["zuora_rate_plan_charge_data","effective_end_date","DATE"],["zuora_rate_plan_charge_data","effective_start_date","DATE"],["zuora_rate_plan_charge_data","end_date_condition","VARCHAR"],["zuora_rate_plan_charge_data","exchange_rate","BIGINT"],["zuora_rate_plan_charge_data","exchange_rate_date","DATE"],["zuora_rate_plan_charge_data","exclude_item_billing_from_revenue_accounting","BOOLEAN"],["zuora_rate_plan_charge_data","exclude_item_booking_from_revenue_accounting","BOOLEAN"],["zuora_rate_plan_charge_data","home_currency","VARCHAR"],["zuora_rate_plan_charge_data","is_last_segment","BOOLEAN"],["zuora_rate_plan_charge_data","is_prepaid","BOOLEAN"],["zuora_rate_plan_charge_data","is_processed","BOOLEAN"],["zuora_rate_plan_charge_data","list_price_base","VARCHAR"],["zuora_rate_plan_charge_data","mrr","BIGINT"],["zuora_rate_plan_charge_data","mrrcurrency_rounding","BIGINT"],["zuora_rate_plan_charge_data","mrrhome_currency","BIGINT"],["zuora_rate_plan_charge_data","name","VARCHAR"],["zuora_rate_plan_charge_data","number_of_periods","VARCHAR"],["zuora_rate_plan_charge_data","original_id","VARCHAR"],["zuora_rate_plan_charge_data","original_order_date","DATE"],["zuora_rate_plan_charge_data","overage_calculation_option","VARCHAR"],["zuora_rate_plan_charge_data","overage_unused_units_credit_option","VARCHAR"],["zuora_rate_plan_charge_data","parent_account_id","VARCHAR"],["zuora_rate_plan_charge_data","payment_term_snapshot","VARCHAR"],["zuora_rate_plan_charge_data","prepaid_operation_type","VARCHAR"],["zuora_rate_plan_charge_data","prepaid_quantity","VARCHAR"],["zuora_rate_plan_charge_data","prepaid_total_quantity","VARCHAR"],["zuora_rate_plan_charge_data","prepaid_uom","VARCHAR"],["zuora_rate_plan_charge_data","price_change_option","VARCHAR"],["zuora_rate_plan_charge_data","price_increase_percentage","BIGINT"],["zuora_rate_plan_charge_data","processed_through_date","DATE"],["zuora_rate_plan_charge_data","product_id","VARCHAR"],["zuora_rate_plan_charge_data","product_rate_plan_charge_id","VARCHAR"],["zuora_rate_plan_charge_data","product_rate_plan_id","VARCHAR"],["zuora_rate_plan_charge_data","provider_exchange_rate_date","DATE"],["zuora_rate_plan_charge_data","quantity","BIGINT"],["zuora_rate_plan_charge_data","rate_plan_id","VARCHAR"],["zuora_rate_plan_charge_data","rating_group","VARCHAR"],["zuora_rate_plan_charge_data","recognized_revenue_accounting_code_id","VARCHAR"],["zuora_rate_plan_charge_data","rev_rec_code","VARCHAR"],["zuora_rate_plan_charge_data","rev_rec_trigger_condition","VARCHAR"],["zuora_rate_plan_charge_data","revenue_recognition_rule_name","VARCHAR"],["zuora_rate_plan_charge_data","segment","BIGINT"],["zuora_rate_plan_charge_data","sold_to_contact_id","VARCHAR"],["zuora_rate_plan_charge_data","sold_to_contact_snapshot_id","VARCHAR"],["zuora_rate_plan_charge_data","specific_billing_period","VARCHAR"],["zuora_rate_plan_charge_data","specific_end_date","VARCHAR"],["zuora_rate_plan_charge_data","subscription_id","VARCHAR"],["zuora_rate_plan_charge_data","tcv","BIGINT"],["zuora_rate_plan_charge_data","tcvcurrency_rounding","BIGINT"],["zuora_rate_plan_charge_data","tcvhome_currency","BIGINT"],["zuora_rate_plan_charge_data","transaction_currency","VARCHAR"],["zuora_rate_plan_charge_data","trigger_date","VARCHAR"],["zuora_rate_plan_charge_data","trigger_event","VARCHAR"],["zuora_rate_plan_charge_data","uom","VARCHAR"],["zuora_rate_plan_charge_data","up_to_periods","VARCHAR"],["zuora_rate_plan_charge_data","up_to_periods_type","VARCHAR"],["zuora_rate_plan_charge_data","updated_by_id","VARCHAR"],["zuora_rate_plan_charge_data","updated_date","TIMESTAMP"],["zuora_rate_plan_charge_data","validity_period_type","VARCHAR"],["zuora_rate_plan_charge_data","version","BIGINT"],["zuora_rate_plan_charge_data","weekly_bill_cycle_day","VARCHAR"],["zuora_rate_plan_charge_data","invoice_owner_id","VARCHAR"],["zuora_rate_plan_charge_data","subscription_owner_id","VARCHAR"],["zuora_rate_plan_charge_data","credit_option","VARCHAR"],["zuora_rate_plan_charge_data","rollover_apply","VARCHAR"],["zuora_rate_plan_charge_data","rollover_periods","BIGINT"],["zuora_rate_plan_charge_data","is_rollover","BOOLEAN"],["zuora_rate_plan_charge_data","specific_list_price_base","VARCHAR"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(account_id as varchar)) same_as_id FROM raw.zuora_rate_plan_charge_data UNION ALL SELECT 'amendment_id' col,count(*) n,count(amendment_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(amendment_id as varchar)) same_as_id FROM raw.zuora_rate_plan_charge_data UNION ALL SELECT 'product_id' col,count(*) n,count(product_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(product_id as varchar)) same_as_id FROM raw.zuora_rate_plan_charge_data UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(product_rate_plan_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(product_rate_plan_id as varchar)) same_as_id FROM raw.zuora_rate_plan_charge_data UNION ALL SELECT 'rate_plan_id' col,count(*) n,count(rate_plan_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(rate_plan_id as varchar)) same_as_id FROM raw.zuora_rate_plan_charge_data UNION ALL SELECT 'subscription_id' col,count(*) n,count(subscription_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(subscription_id as varchar)) same_as_id FROM raw.zuora_rate_plan_charge_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["account_id",5,5,0],["amendment_id",5,1,0],["product_id",5,5,0],["product_rate_plan_id",5,5,0],["rate_plan_id",5,5,0],["subscription_id",5,5,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_col_matches FROM raw.zuora_rate_plan_charge_data s UNION ALL SELECT 'amendment_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.amendment_id as varchar))) named_col_matches FROM raw.zuora_rate_plan_charge_data s UNION ALL SELECT 'product_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.product_id as varchar))) named_col_matches FROM raw.zuora_rate_plan_charge_data s UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.product_rate_plan_id as varchar))) named_col_matches FROM raw.zuora_rate_plan_charge_data s UNION ALL SELECT 'rate_plan_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.rate_plan_id as varchar))) named_col_matches FROM raw.zuora_rate_plan_charge_data s UNION ALL SELECT 'subscription_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.subscription_id as varchar))) named_col_matches FROM raw.zuora_rate_plan_charge_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["account_id",5,0,5],["amendment_id",5,0,0],["product_id",5,0,2],["product_rate_plan_id",5,0,4],["rate_plan_id",5,0,1],["subscription_id",5,0,0]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_rate_plan_charge_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(s.account_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'amendment_id' col,count(*) n,count(s.amendment_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_amendment_data t WHERE cast(t.id as varchar)=cast(s.amendment_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'product_id' col,count(*) n,count(s.product_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_data t WHERE cast(t.id as varchar)=cast(s.product_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(s.product_rate_plan_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_product_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.product_rate_plan_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'rate_plan_id' col,count(*) n,count(s.rate_plan_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_rate_plan_data t WHERE cast(t.id as varchar)=cast(s.rate_plan_id as varchar))) named_matches FROM source_rows s UNION ALL SELECT 'subscription_id' col,count(*) n,count(s.subscription_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_subscription_data t WHERE cast(t.id as varchar)=cast(s.subscription_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["account_id",4,4,0,4],["amendment_id",4,1,0,0],["product_id",4,4,0,2],["product_rate_plan_id",4,4,0,3],["rate_plan_id",4,4,0,1],["subscription_id",4,4,0,0]]}
```


### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_rate_plan_charge_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(account_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(account_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'amendment_id' col,count(*) n,count(amendment_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(amendment_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(amendment_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'product_id' col,count(*) n,count(product_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(product_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(product_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'product_rate_plan_id' col,count(*) n,count(product_rate_plan_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(product_rate_plan_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(product_rate_plan_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'rate_plan_id' col,count(*) n,count(rate_plan_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(rate_plan_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(rate_plan_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows UNION ALL SELECT 'subscription_id' col,count(*) n,count(subscription_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(subscription_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(subscription_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["account_id",4,4,4,0],["amendment_id",4,1,1,0],["product_id",4,4,4,0],["product_rate_plan_id",4,4,4,0],["rate_plan_id",4,4,4,0],["subscription_id",4,4,4,0]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__rate_plan_charge.json
[024_reruns_impl-030_stg_zuora__rate_plan_charge.json](../024_reruns_impl-030_stg_zuora__rate_plan_charge.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4|4|4|24|否|
|L1|4|4|4|24|否|
|L2|4|4|4|24|否|
|L3|4|4|4|24|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L1：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L2：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L3：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__rate_plan_charge/baseline.sql`；SHA-256 `e12db07ba829aa50b998dad02c8c78c22436d62aaab89db5f62c6665d3717c6b`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4|4|4|24|否|
|L1|4|4|4|24|否|
|L2|4|4|4|24|否|
|L3|4|4|4|24|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L1：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L2：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L3：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`

#### source_account_id
主因；类别候选U。P：本实体id可替代account_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少4。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第7行、offset 224起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS account_id
```

修改后：
```sql
try_cast("account_id" AS VARCHAR) AS account_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__rate_plan_charge/source_account_id.sql`；SHA-256 `d0558c613549245db789f1a1380fb2ad4f5b2b94ce570d97abc04672401a4366`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4|4|4|20|否|
|L1|4|4|4|20|否|
|L2|4|4|4|20|否|
|L3|4|4|4|20|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L1：`{"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L2：`{"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L3：`{"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`

#### source_amendment_id
主因；类别候选A。把本实体 id 当作 amendment_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少4。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第11行、offset 523起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS amendment_id
```

修改后：
```sql
try_cast("amendment_id" AS VARCHAR) AS amendment_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__rate_plan_charge/source_amendment_id.sql`；SHA-256 `3aa8660255b4e2c51c070995948818a9c93685aa26c9320347cafabcfbf1e1b8`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4|4|4|20|否|
|L1|4|4|4|20|否|
|L2|4|4|4|20|否|
|L3|4|4|4|20|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L1：`{"account_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L2：`{"account_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L3：`{"account_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`

#### source_product_id
主因；类别候选U。P：本实体id可替代product_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少4。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第53行、offset 3352起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS product_id
```

修改后：
```sql
try_cast("product_id" AS VARCHAR) AS product_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__rate_plan_charge/source_product_id.sql`；SHA-256 `978777be64ec426b93d12d1650efefdcb0cd2eb68c78d41831622ba8b66e5029`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4|4|4|20|否|
|L1|4|4|4|20|否|
|L2|4|4|4|20|否|
|L3|4|4|4|20|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":4,"amendment_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L1：`{"account_id":4,"amendment_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L2：`{"account_id":4,"amendment_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`
- L3：`{"account_id":4,"amendment_id":4,"product_rate_plan_id":4,"rate_plan_id":4,"subscription_id":4}`

#### source_product_rate_plan_id
主因；类别候选U。P：本实体id可替代product_rate_plan_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少4。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第55行、offset 3492起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS product_rate_plan_id
```

修改后：
```sql
try_cast("product_rate_plan_id" AS VARCHAR) AS product_rate_plan_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__rate_plan_charge/source_product_rate_plan_id.sql`；SHA-256 `25bdf560a17ea5d5abea95426bcab876c33ef1d766c7784c04d64a66cbe310be`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4|4|4|20|否|
|L1|4|4|4|20|否|
|L2|4|4|4|20|否|
|L3|4|4|4|20|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":4,"amendment_id":4,"product_id":4,"rate_plan_id":4,"subscription_id":4}`
- L1：`{"account_id":4,"amendment_id":4,"product_id":4,"rate_plan_id":4,"subscription_id":4}`
- L2：`{"account_id":4,"amendment_id":4,"product_id":4,"rate_plan_id":4,"subscription_id":4}`
- L3：`{"account_id":4,"amendment_id":4,"product_id":4,"rate_plan_id":4,"subscription_id":4}`

#### source_rate_plan_id
主因；类别候选U。P：本实体id可替代rate_plan_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少0，格减少4。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第57行、offset 3603起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS rate_plan_id
```

修改后：
```sql
try_cast("rate_plan_id" AS VARCHAR) AS rate_plan_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__rate_plan_charge/source_rate_plan_id.sql`；SHA-256 `c281c75cf5b9afb11f0a86e7efbb7adf84f28af1a4abe0b2ce59748fed3685e5`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4|4|4|20|否|
|L1|4|4|4|20|否|
|L2|4|4|4|20|否|
|L3|4|4|4|20|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"subscription_id":4}`
- L1：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"subscription_id":4}`
- L2：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"subscription_id":4}`
- L3：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"subscription_id":4}`

#### source_subscription_id
主因；类别候选A。把本实体 id 当作 subscription_id；契约未给源列映射，按可见数据关系另核 U。
相对本轮基线：行减少0，格减少4。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第64行、offset 4128起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS subscription_id
```

修改后：
```sql
try_cast("subscription_id" AS VARCHAR) AS subscription_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__rate_plan_charge/source_subscription_id.sql`；SHA-256 `aa9ae4553f21201788b75b7a9b844aa2f1187d8f7d04cde562965925c3bdb1eb`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|4|4|4|20|否|
|L1|4|4|4|20|否|
|L2|4|4|4|20|否|
|L3|4|4|4|20|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4}`
- L1：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4}`
- L2：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4}`
- L3：`{"account_id":4,"amendment_id":4,"product_id":4,"product_rate_plan_id":4,"rate_plan_id":4}`
## 规则问题

无。

