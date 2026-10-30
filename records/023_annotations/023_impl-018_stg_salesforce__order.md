# impl-018 · stg_salesforce__order

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**I**；把握：高；主要错误点：account_mapping。

account_id 被写成订单自身 id；轨迹已明确意图应保留 FK 列，但 order 未被该修正覆盖。

参与因素：无。

标记：无。

原始数据核实：订单id与account表0匹配，account_id有894匹配；分类依据是轨迹中明确正确意图，因此用I，不用U。

## 材料与比较口径

精简材料包：[023_impl-018_stg_salesforce__order.md](../023_packages/023_impl-018_stg_salesforce__order.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
契约行 787–854：

```
787:     - name: stg_salesforce__order
788:       description: "Cleaned order records with validated order information and status"
789:       source_table: raw.order_data
790:       columns:
791:         - name: order_id
792:           data_type: VARCHAR
793:         - name: account_id
794:           data_type: VARCHAR
795:         - name: activated_by_id
796:           data_type: VARCHAR
797:         - name: activated_date
798:           data_type: TIMESTAMP
799:         - name: billing_city
800:           data_type: VARCHAR
801:         - name: billing_country
802:           data_type: VARCHAR
803:         - name: billing_postal_code
804:           data_type: VARCHAR
805:         - name: billing_state
806:           data_type: VARCHAR
807:         - name: billing_street
808:           data_type: VARCHAR
809:         - name: company_authorized_by_id
810:           data_type: VARCHAR
811:         - name: contract_id
812:           data_type: VARCHAR
813:         - name: created_date
814:           data_type: TIMESTAMP
815:         - name: customer_authorized_by_id
816:           data_type: VARCHAR
817:         - name: order_description
818:           data_type: VARCHAR
819:         - name: effective_date
820:           data_type: DATE
821:         - name: end_date
822:           data_type: DATE
823:         - name: is_deleted
824:           data_type: BOOLEAN
825:           validation_rules:
826:             - rule: "NOT COALESCE(is_deleted, false)"
827:               on_failure: delete_row
828:         - name: last_modified_date
829:           data_type: TIMESTAMP
830:         - name: order_number
831:           data_type: VARCHAR
832:         - name: original_order_id
833:           data_type: VARCHAR
834:         - name: owner_id
835:           data_type: VARCHAR
836:         - name: status
837:           data_type: VARCHAR
838:         - name: total_amount
839:           data_type: DECIMAL
840:         - name: pricebook_2_id
841:           data_type: VARCHAR
842:         - name: shipping_city
843:           data_type: VARCHAR
844:         - name: shipping_country
845:           data_type: VARCHAR
846:         - name: shipping_postal_code
847:           data_type: VARCHAR
848:         - name: shipping_state
849:           data_type: VARCHAR
850:         - name: shipping_street
851:           data_type: VARCHAR
852:         - name: type
853:           data_type: VARCHAR
854:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__order.sql`，SHA-256 `e1f14d5b781f3a097ec4788859850da2c20a39e5abfa51c255856c1d9d1055b5`，行 1–32。

```
1: select
2:       id as order_id,
3:       id as account_id,
4:       activated_by_id as activated_by_id,
5:       try_cast(activated_date as TIMESTAMP) as activated_date,
6:       billing_city as billing_city,
7:       billing_country as billing_country,
8:       billing_postal_code as billing_postal_code,
9:       billing_state as billing_state,
10:       billing_street as billing_street,
11:       company_authorized_by_id as company_authorized_by_id,
12:       contract_id as contract_id,
13:       try_cast(created_date as TIMESTAMP) as created_date,
14:       customer_authorized_by_id as customer_authorized_by_id,
15:       description as order_description,
16:       try_cast(effective_date as DATE) as effective_date,
17:       try_cast(end_date as DATE) as end_date,
18:       is_deleted as is_deleted,
19:       try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
20:       order_number as order_number,
21:       original_order_id as original_order_id,
22:       owner_id as owner_id,
23:       status as status,
24:       try_cast(total_amount as DECIMAL) as total_amount,
25:       pricebook_2_id as pricebook_2_id,
26:       shipping_city as shipping_city,
27:       shipping_country as shipping_country,
28:       shipping_postal_code as shipping_postal_code,
29:       shipping_state as shipping_state,
30:       shipping_street as shipping_street,
31:       "type" as type
32: from raw.order_data
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__order.sql`，SHA-256 `98fb338fa240ac6809f12c3b83bdab1a64e403e60312b4a56ab3d28c4d4e358a`，行 1–43。

```
1: with fields as (
2:     select *
3:     from raw.order_data
4: ), 
5: 
6: final as (
7:     select
8:         cast(id as varchar) as order_id,
9:         cast(account_id as varchar) as account_id,
10:         cast(activated_by_id as varchar) as activated_by_id,
11:         cast(activated_date as timestamp) as activated_date,
12:         cast(billing_city as varchar) as billing_city,
13:         cast(billing_country as varchar) as billing_country,
14:         cast(billing_postal_code as varchar) as billing_postal_code,
15:         cast(billing_state as varchar) as billing_state,
16:         cast(billing_street as varchar) as billing_street,
17:         cast(company_authorized_by_id as varchar) as company_authorized_by_id,
18:         cast(contract_id as varchar) as contract_id,
19:         cast(created_date as timestamp) as created_date,
20:         cast(customer_authorized_by_id as varchar) as customer_authorized_by_id,
21:         cast(description as varchar) as order_description,
22:         cast(effective_date as date) as effective_date,
23:         cast(end_date as date) as end_date,
24:         cast(coalesce(is_deleted, false) as boolean) as is_deleted,
25:         cast(last_modified_date as timestamp) as last_modified_date,
26:         cast(order_number as varchar) as order_number,
27:         cast(original_order_id as varchar) as original_order_id,
28:         cast(owner_id as varchar) as owner_id,
29:         cast(pricebook_2_id as varchar) as pricebook_2_id,
30:         cast(shipping_city as varchar) as shipping_city,
31:         cast(shipping_country as varchar) as shipping_country,
32:         cast(shipping_postal_code as varchar) as shipping_postal_code,
33:         cast(shipping_state as varchar) as shipping_state,
34:         cast(shipping_street as varchar) as shipping_street,
35:         cast(status as varchar) as status,
36:         cast(total_amount as decimal) as total_amount,
37:         cast(type as varchar) as type
38:     from fields
39: )
40: 
41: select *
42: from final
43: where not coalesce(is_deleted, false)
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 57 注释：「Correct field source mapping; canonical foreign keys should remain FK columns, not the row's own id.」；event 67/68 查看各staging首列；event 99 未说明 order 留有这处错误。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 57：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/57.json`。
- event 67：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/67.json`。
- event 68：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/68.json`。
- event 99：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json`。
## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：ID 对应 account

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE id IN(SELECT id FROM raw.account)) order_matches_account,count(*) FILTER(WHERE account_id IN(SELECT id FROM raw.account)) fk_matches_account FROM raw.order_data
```


```json
{"columns":["n","order_matches_account","fk_matches_account"],"rows":[[3000,0,894]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-018_stg_salesforce__order.json](../023_reruns_impl-018_stg_salesforce__order.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|3000|否|
|L1|3000|3000|3000|3000|否|
|L2|3000|3000|3000|3000|否|
|L3|3000|3000|3000|3000|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"account_id":3000}`
- L1：`{"account_id":3000}`
- L2：`{"account_id":3000}`
- L3：`{"account_id":3000}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-018_stg_salesforce__order/baseline.sql`；SHA-256 `e1f14d5b781f3a097ec4788859850da2c20a39e5abfa51c255856c1d9d1055b5`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|3000|3000|否|
|L1|3000|3000|3000|3000|否|
|L2|3000|3000|3000|3000|否|
|L3|3000|3000|3000|3000|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"account_id":3000}`
- L1：`{"account_id":3000}`
- L2：`{"account_id":3000}`
- L3：`{"account_id":3000}`

#### account_mapping

判定：主因；类别候选 I。ID 指订单，不对应 raw.account；需查询证实可见数据唯一指向 account_id。

相对本轮基线减少行 3000、格 3000；按行优先、格次之排序。
共同控制后 SQL 第 3 行起、字符 offset 35 的唯一连续替换；其余字节不动。
替换前：
```sql
id as account_id
```

替换后：
```sql
account_id as account_id
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__order/account_mapping.sql`；SHA-256 `90712e1cf53499a4afc7eba08402a24c71f3e13f343c521b71e1e3b417698648`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|0|0|是|
|L1|3000|3000|0|0|是|
|L2|3000|3000|0|0|是|
|L3|3000|3000|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 规则问题

无
