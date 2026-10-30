# impl-030 · stg_zuora__subscription

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**U**；把握：中。

统一pk_alias将不同关系字段都映射本实体id；各输出位置独立修复。具名候选能与相关表形成明确对应的按U，其余源字段错位或无法定语义的按A；契约类型与gold透传冲突按O。

参与因素：无。
标记：证据曾出现但被忽略。

## 材料与比较口径

[024_impl-030_stg_zuora__subscription.md](../024_packages/024_impl-030_stg_zuora__subscription.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
851:     - name: stg_zuora__subscription
852:       description: "Cleaned subscriptions with status, term and key dates; latest snapshot indicator."
853:       source_table: raw.zuora_subscription_data
854:       columns:
855:         - name: subscription_id
856:           data_type: VARCHAR
857:           source_expression: "id"
858:         - name: account_id
859:           data_type: VARCHAR
860:         - name: auto_renew
861:           data_type: BOOLEAN
862:         - name: bill_to_contact_id
863:           data_type: VARCHAR
864:         - name: cancel_reason
865:           data_type: VARCHAR
866:         - name: cancelled_date
867:           data_type: TIMESTAMP
868:           source_expression: "cast(cancelled_date as TIMESTAMP)"
869:         - name: contract_acceptance_date
870:           data_type: TIMESTAMP
871:           source_expression: "cast(contract_acceptance_date as TIMESTAMP)"
872:         - name: contract_effective_date
873:           data_type: TIMESTAMP
874:           source_expression: "cast(contract_effective_date as TIMESTAMP)"
875:         - name: created_by_id
876:           data_type: VARCHAR
877:         - name: created_date
878:           data_type: TIMESTAMP
879:           source_expression: "cast(created_date as TIMESTAMP)"
880:         - name: current_term
881:           data_type: BIGINT
882:         - name: current_term_period_type
883:           data_type: VARCHAR
884:         - name: default_payment_method_id
885:           data_type: VARCHAR
886:         - name: externally_managed_by
887:           data_type: VARCHAR
888:         - name: initial_term
889:           data_type: BIGINT
890:         - name: initial_term_period_type
891:           data_type: VARCHAR
892:         - name: invoice_owner_id
893:           data_type: VARCHAR
894:         - name: is_invoice_separate
895:           data_type: BOOLEAN
896:         - name: is_latest_version
897:           data_type: BOOLEAN
898:         - name: last_booking_date
899:           data_type: DATE
900:         - name: subscription_name
901:           data_type: VARCHAR
902:           source_expression: "_name"
903:         - name: notes
904:           data_type: VARCHAR
905:         - name: original_created_date
906:           data_type: TIMESTAMP
907:           source_expression: "cast(original_created_date as TIMESTAMP)"
908:         - name: original_id
909:           data_type: VARCHAR
910:         - name: parent_account_id
911:           data_type: VARCHAR
912:         - name: payment_term
913:           data_type: VARCHAR
914:         - name: previous_subscription_id
915:           data_type: VARCHAR
916:         - name: renewal_term
917:           data_type: BIGINT
918:         - name: renewal_term_period_type
919:           data_type: VARCHAR
920:         - name: revision
921:           data_type: BIGINT
922:         - name: service_activation_date
923:           data_type: TIMESTAMP
924:           source_expression: "cast(service_activation_date as TIMESTAMP)"
925:         - name: sold_to_contact_id
926:           data_type: VARCHAR
927:         - name: status
928:           data_type: VARCHAR
929:         - name: subscription_end_date
930:           data_type: TIMESTAMP
931:         - name: subscription_start_date
932:           data_type: TIMESTAMP
933:         - name: term_end_date
934:           data_type: TIMESTAMP
935:           source_expression: "cast(term_end_date as TIMESTAMP)"
936:         - name: term_start_date
937:           data_type: TIMESTAMP
938:           source_expression: "cast(term_start_date as TIMESTAMP)"
939:         - name: term_type
940:           data_type: VARCHAR
941:         - name: updated_by_id
942:           data_type: VARCHAR
943:         - name: updated_date
944:           data_type: TIMESTAMP
945:           source_expression: "cast(updated_date as TIMESTAMP)"
946:         - name: version
947:           data_type: VARCHAR
948:           source_expression: "_version"
949:         - name: is_most_recent_record
950:           data_type: BOOLEAN
951:           source_expression: "row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1"
952:       row_filters:
953:         - rule: "coalesce(lower(cast(_fivetran_deleted as varchar)),'false') = 'false'"
954:           on_failure: delete_row
955:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__subscription.sql`；SHA-256 `9d3d4125ed3d8bab688877ccd05961647b7f0c9aab9a330d72e636f88a1dcf0a`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_subscription_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         id AS subscription_id,
7:         try_cast("id" AS VARCHAR) AS account_id,
8:         try_cast("auto_renew" AS BOOLEAN) AS auto_renew,
9:         try_cast("bill_to_contact_id" AS VARCHAR) AS bill_to_contact_id,
10:         try_cast("cancel_reason" AS VARCHAR) AS cancel_reason,
11:         try_cast(cancelled_date as TIMESTAMP) AS cancelled_date,
12:         try_cast(contract_acceptance_date as TIMESTAMP) AS contract_acceptance_date,
13:         try_cast(contract_effective_date as TIMESTAMP) AS contract_effective_date,
14:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
15:         try_cast(created_date as TIMESTAMP) AS created_date,
16:         try_cast("current_term" AS BIGINT) AS current_term,
17:         try_cast("current_term_period_type" AS VARCHAR) AS current_term_period_type,
18:         try_cast("default_payment_method_id" AS VARCHAR) AS default_payment_method_id,
19:         try_cast("externally_managed_by" AS VARCHAR) AS externally_managed_by,
20:         try_cast("initial_term" AS BIGINT) AS initial_term,
21:         try_cast("initial_term_period_type" AS VARCHAR) AS initial_term_period_type,
22:         try_cast("invoice_owner_id" AS VARCHAR) AS invoice_owner_id,
23:         try_cast("is_invoice_separate" AS BOOLEAN) AS is_invoice_separate,
24:         try_cast("is_latest_version" AS BOOLEAN) AS is_latest_version,
25:         try_cast("last_booking_date" AS DATE) AS last_booking_date,
26:         _name AS subscription_name,
27:         try_cast("notes" AS VARCHAR) AS notes,
28:         try_cast(original_created_date as TIMESTAMP) AS original_created_date,
29:         try_cast("original_id" AS VARCHAR) AS original_id,
30:         try_cast("parent_account_id" AS VARCHAR) AS parent_account_id,
31:         try_cast("payment_term" AS VARCHAR) AS payment_term,
32:         try_cast("previous_subscription_id" AS VARCHAR) AS previous_subscription_id,
33:         try_cast("renewal_term" AS BIGINT) AS renewal_term,
34:         try_cast("renewal_term_period_type" AS VARCHAR) AS renewal_term_period_type,
35:         try_cast("revision" AS BIGINT) AS revision,
36:         try_cast(service_activation_date as TIMESTAMP) AS service_activation_date,
37:         try_cast("sold_to_contact_id" AS VARCHAR) AS sold_to_contact_id,
38:         try_cast("status" AS VARCHAR) AS status,
39:         try_cast("subscription_end_date" AS TIMESTAMP) AS subscription_end_date,
40:         try_cast("subscription_start_date" AS TIMESTAMP) AS subscription_start_date,
41:         try_cast(term_end_date as TIMESTAMP) AS term_end_date,
42:         try_cast(term_start_date as TIMESTAMP) AS term_start_date,
43:         try_cast("term_type" AS VARCHAR) AS term_type,
44:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
45:         try_cast(updated_date as TIMESTAMP) AS updated_date,
46:         _version AS version,
47:         row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 AS is_most_recent_record
48: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__subscription.sql`；SHA-256 `b5a4f96b5c1aacc6be5b1634856bfc9c501ea1e5dc3708d4175d7b906e64c2c1`。

```text
1: with base as (
2:     select * from raw.zuora_subscription_data
3:     where coalesce(lower(cast(_fivetran_deleted as varchar)),'false') = 'false'
4: ),
5: final as (
6:     select
7:         id as subscription_id,
8:         account_id,
9:         auto_renew,
10:         bill_to_contact_id,
11:         cancel_reason,
12:         cast(cancelled_date as TIMESTAMP) as cancelled_date,
13:         cast(contract_acceptance_date as TIMESTAMP) as contract_acceptance_date,
14:         cast(contract_effective_date as TIMESTAMP) as contract_effective_date,
15:         created_by_id,
16:         cast(created_date as TIMESTAMP) as created_date,
17:         current_term,
18:         current_term_period_type,
19:         default_payment_method_id,
20:         externally_managed_by,
21:         initial_term,
22:         initial_term_period_type,
23:         invoice_owner_id,
24:         is_invoice_separate,
25:         is_latest_version,
26:         last_booking_date,
27:         _name as subscription_name,
28:         notes,
29:         cast(original_created_date as TIMESTAMP) as original_created_date,
30:         original_id,
31:         parent_account_id,
32:         payment_term,
33:         previous_subscription_id,
34:         renewal_term,
35:         renewal_term_period_type,
36:         revision,
37:         cast(service_activation_date as TIMESTAMP) as service_activation_date,
38:         sold_to_contact_id,
39:         status,
40:         subscription_end_date,
41:         subscription_start_date,
42:         cast(term_end_date as TIMESTAMP) as term_end_date,
43:         cast(term_start_date as TIMESTAMP) as term_start_date,
44:         term_type,
45:         updated_by_id,
46:         cast(updated_date as TIMESTAMP) as updated_date,
47:         _version as version,
48:         row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 as is_most_recent_record
49:     from base
50: )
51: select * from final
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_subscription_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_subscription_data","id","VARCHAR"],["zuora_subscription_data","_fivetran_deleted","VARCHAR"],["zuora_subscription_data","_fivetran_synced","VARCHAR"],["zuora_subscription_data","account_id","VARCHAR"],["zuora_subscription_data","auto_renew","VARCHAR"],["zuora_subscription_data","bill_to_contact_id","VARCHAR"],["zuora_subscription_data","cancelled_date","VARCHAR"],["zuora_subscription_data","contract_acceptance_date","VARCHAR"],["zuora_subscription_data","contract_effective_date","VARCHAR"],["zuora_subscription_data","cpq_bundle_json_id_qt","VARCHAR"],["zuora_subscription_data","created_by_id","VARCHAR"],["zuora_subscription_data","created_date","VARCHAR"],["zuora_subscription_data","creator_account_id","VARCHAR"],["zuora_subscription_data","creator_invoice_owner_id","VARCHAR"],["zuora_subscription_data","current_term","VARCHAR"],["zuora_subscription_data","current_term_period_type","VARCHAR"],["zuora_subscription_data","default_payment_method_id","VARCHAR"],["zuora_subscription_data","initial_term","VARCHAR"],["zuora_subscription_data","initial_term_period_type","VARCHAR"],["zuora_subscription_data","invoice_owner_id","VARCHAR"],["zuora_subscription_data","is_invoice_separate","VARCHAR"],["zuora_subscription_data","_name","VARCHAR"],["zuora_subscription_data","notes","VARCHAR"],["zuora_subscription_data","opportunity_close_date_qt","VARCHAR"],["zuora_subscription_data","opportunity_name_qt","VARCHAR"],["zuora_subscription_data","original_created_date","VARCHAR"],["zuora_subscription_data","original_id","VARCHAR"],["zuora_subscription_data","parent_account_id","VARCHAR"],["zuora_subscription_data","previous_subscription_id","VARCHAR"],["zuora_subscription_data","quote_business_type_qt","VARCHAR"],["zuora_subscription_data","quote_number_qt","VARCHAR"],["zuora_subscription_data","quote_type_qt","VARCHAR"],["zuora_subscription_data","renewal_setting","VARCHAR"],["zuora_subscription_data","renewal_term","VARCHAR"],["zuora_subscription_data","renewal_term_period_type","VARCHAR"],["zuora_subscription_data","service_activation_date","VARCHAR"],["zuora_subscription_data","sold_to_contact_id","VARCHAR"],["zuora_subscription_data","status","VARCHAR"],["zuora_subscription_data","subscription_end_date","VARCHAR"],["zuora_subscription_data","subscription_start_date","VARCHAR"],["zuora_subscription_data","subscription_version_amendment_id","VARCHAR"],["zuora_subscription_data","term_end_date","VARCHAR"],["zuora_subscription_data","term_start_date","VARCHAR"],["zuora_subscription_data","term_type","VARCHAR"],["zuora_subscription_data","updated_by_id","VARCHAR"],["zuora_subscription_data","updated_date","VARCHAR"],["zuora_subscription_data","_version","VARCHAR"],["zuora_subscription_data","is_latest_version","VARCHAR"],["zuora_subscription_data","cancel_reason","VARCHAR"],["zuora_subscription_data","externally_managed_by","VARCHAR"],["zuora_subscription_data","payment_term","VARCHAR"],["zuora_subscription_data","testcustomaakash_c","VARCHAR"],["zuora_subscription_data","last_booking_date","VARCHAR"],["zuora_subscription_data","revision","VARCHAR"],["zuora_subscription_data","custom_date_field_c","VARCHAR"],["zuora_subscription_data","invoice_template_id","VARCHAR"],["zuora_subscription_data","sequence_set_id","VARCHAR"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(account_id as varchar)) same_as_id FROM raw.zuora_subscription_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["account_id",1503,1502,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_col_matches FROM raw.zuora_subscription_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["account_id",1503,0,1500]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_subscription_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(s.account_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["account_id",732,732,0,730]]}
```


### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_subscription_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(account_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(account_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["account_id",732,732,732,0]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__subscription.json
[024_reruns_impl-030_stg_zuora__subscription.json](../024_reruns_impl-030_stg_zuora__subscription.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|732|732|732|732|否|
|L1|732|732|732|732|否|
|L2|732|732|732|732|否|
|L3|732|732|732|732|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":732}`
- L1：`{"account_id":732}`
- L2：`{"account_id":732}`
- L3：`{"account_id":732}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__subscription/baseline.sql`；SHA-256 `9d3d4125ed3d8bab688877ccd05961647b7f0c9aab9a330d72e636f88a1dcf0a`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|732|732|732|732|否|
|L1|732|732|732|732|否|
|L2|732|732|732|732|否|
|L3|732|732|732|732|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":732}`
- L1：`{"account_id":732}`
- L2：`{"account_id":732}`
- L3：`{"account_id":732}`

#### source_account_id
主因；类别候选U。P：本实体id可替代account_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少732，格减少732。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第7行、offset 216起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS account_id
```

修改后：
```sql
try_cast("account_id" AS VARCHAR) AS account_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__subscription/source_account_id.sql`；SHA-256 `dfe6c198a60b7478b1b1d2299a6f0d7afe0212711314314e538c53db150354b8`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|732|732|0|0|是|
|L1|732|732|0|0|是|
|L2|732|732|0|0|是|
|L3|732|732|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 规则问题

无。

