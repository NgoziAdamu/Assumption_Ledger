# impl-030 · stg_zuora__contact

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**U**；把握：中。

统一pk_alias将不同关系字段都映射本实体id；各输出位置独立修复。具名候选能与相关表形成明确对应的按U，其余源字段错位或无法定语义的按A；契约类型与gold透传冲突按O。

参与因素：无。
标记：证据曾出现但被忽略。

## 材料与比较口径

[024_impl-030_stg_zuora__contact.md](../024_packages/024_impl-030_stg_zuora__contact.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-030/docs/data_contract.yaml`。

```text
111:     - name: stg_zuora__contact
112:       description: "Cleaned contacts with email normalization and phone format standardization; latest per contact and per account-contact flags."
113:       source_table: raw.zuora_contact_data
114:       columns:
115:         - name: contact_id
116:           data_type: VARCHAR
117:           source_expression: "id"
118:         - name: account_id
119:           data_type: VARCHAR
120:         - name: address_1
121:           data_type: VARCHAR
122:         - name: address_2
123:           data_type: VARCHAR
124:         - name: city
125:           data_type: VARCHAR
126:         - name: country
127:           data_type: VARCHAR
128:         - name: created_by_id
129:           data_type: VARCHAR
130:         - name: created_date
131:           data_type: TIMESTAMP
132:           source_expression: "cast(created_date as TIMESTAMP)"
133:         - name: description
134:           data_type: VARCHAR
135:         - name: first_name
136:           data_type: VARCHAR
137:         - name: last_name
138:           data_type: VARCHAR
139:         - name: postal_code
140:           data_type: VARCHAR
141:         - name: state
142:           data_type: VARCHAR
143:         - name: updated_by_id
144:           data_type: VARCHAR
145:         - name: updated_date
146:           data_type: TIMESTAMP
147:           source_expression: "cast(updated_date as TIMESTAMP)"
148:         - name: work_email
149:           data_type: VARCHAR
150:           source_expression: "lower(trim(work_email))"
151:           validation_rules:
152:             - rule: "work_email IS NULL OR work_email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
153:               on_failure: nullify_field
154:         - name: work_phone
155:           data_type: VARCHAR
156:         - name: mobile_phone
157:           data_type: VARCHAR
158:           source_expression: "case when mobile_phone is null then null else (case when length(regexp_replace(mobile_phone, '[^0-9]', '')) = 10 then '(' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),1,3) || ') ' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),4,3) || '-' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),7,4) when length(regexp_replace(mobile_phone, '[^0-9]', '')) = 11 then '(' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),2,3) || ') ' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),5,3) || '-' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),8,4) else null end) end"
159:         - name: is_most_recent_record
160:           data_type: BOOLEAN
161:           source_expression: "row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1"
162:         - name: is_most_recent_account_contact
163:           data_type: BOOLEAN
164:           source_expression: "row_number() over (partition by account_id order by try_cast(created_date as TIMESTAMP) desc) = 1"
165:       row_filters:
166:         - rule: "_fivetran_deleted IS NULL OR _fivetran_deleted = false"
167:           on_failure: delete_row
168:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/sql/staging/stg_zuora__contact.sql`；SHA-256 `bf54f51510529ae30a5018d891c3b79117fbe5e3f9e7f15edafa03757a618e2b`。

```text
1: WITH source_rows AS (
2:     SELECT *
3:     FROM raw.zuora_contact_data
4:     WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
5: SELECT
6:         id AS contact_id,
7:         try_cast("id" AS VARCHAR) AS account_id,
8:         try_cast("address_1" AS VARCHAR) AS address_1,
9:         try_cast("address_2" AS VARCHAR) AS address_2,
10:         try_cast("city" AS VARCHAR) AS city,
11:         try_cast("country" AS VARCHAR) AS country,
12:         try_cast("created_by_id" AS VARCHAR) AS created_by_id,
13:         try_cast(created_date as TIMESTAMP) AS created_date,
14:         try_cast("description" AS VARCHAR) AS description,
15:         try_cast("first_name" AS VARCHAR) AS first_name,
16:         try_cast("last_name" AS VARCHAR) AS last_name,
17:         try_cast("postal_code" AS VARCHAR) AS postal_code,
18:         try_cast("state" AS VARCHAR) AS state,
19:         try_cast("updated_by_id" AS VARCHAR) AS updated_by_id,
20:         try_cast(updated_date as TIMESTAMP) AS updated_date,
21:         CASE WHEN work_email IS NULL OR regexp_matches(lower(trim(work_email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') THEN lower(trim(work_email)) ELSE NULL END AS work_email,
22:         try_cast("work_phone" AS VARCHAR) AS work_phone,
23:         case when mobile_phone is null then null else (case when length(regexp_replace(mobile_phone, '[^0-9]', '')) = 10 then '(' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),1,3) || ') ' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),4,3) || '-' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),7,4) when length(regexp_replace(mobile_phone, '[^0-9]', '')) = 11 then '(' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),2,3) || ') ' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),5,3) || '-' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),8,4) else null end) end AS mobile_phone,
24:         row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 AS is_most_recent_record,
25:         row_number() over (partition by account_id order by try_cast(created_date as TIMESTAMP) desc) = 1 AS is_most_recent_account_contact
26: FROM source_rows
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-030/sql/staging/stg_zuora__contact.sql`；SHA-256 `3755ecf95ba35050207304a7972db172bed8285bca7fb693ef2a83bf32d5c4dd`。

```text
1: with base as (
2:     select * from raw.zuora_contact_data where _fivetran_deleted is null or _fivetran_deleted = false
3: ),
4: normalized as (
5:     select
6:         id as contact_id,
7:         account_id,
8:         address_1,
9:         address_2,
10:         city,
11:         country,
12:         created_by_id,
13:         cast(created_date as TIMESTAMP) as created_date,
14:         description,
15:         first_name,
16:         last_name,
17:         postal_code,
18:         state,
19:         updated_by_id,
20:         cast(updated_date as TIMESTAMP) as updated_date,
21:         -- email normalization and validation
22:         lower(trim(work_email)) as work_email_norm,
23:         work_phone,
24:         mobile_phone,
25:         row_number() over (partition by id order by try_cast(updated_date as TIMESTAMP) desc) = 1 as is_most_recent_record,
26:         row_number() over (partition by account_id order by try_cast(created_date as TIMESTAMP) desc) = 1 as is_most_recent_account_contact
27:     from base
28: ),
29: cleaned as (
30:     select
31:         contact_id,
32:         account_id,
33:         address_1,
34:         address_2,
35:         city,
36:         country,
37:         created_by_id,
38:         created_date,
39:         description,
40:         first_name,
41:         last_name,
42:         postal_code,
43:         state,
44:         updated_by_id,
45:         updated_date,
46:         case
47:             when work_email_norm is null then null
48:             when regexp_matches(work_email_norm, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') then work_email_norm
49:             else null
50:         end as work_email,
51:         work_phone,
52:         -- phone standardization: keep digits, format (XXX) XXX-XXXX if 10 digits; else null
53:         case
54:             when mobile_phone is null then null
55:             else (
56:                 case
57:                     when length(regexp_replace(mobile_phone, '[^0-9]', '')) = 10 then
58:                         '(' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),1,3) || ') ' ||
59:                         substr(regexp_replace(mobile_phone, '[^0-9]', ''),4,3) || '-' ||
60:                         substr(regexp_replace(mobile_phone, '[^0-9]', ''),7,4)
61:                     when length(regexp_replace(mobile_phone, '[^0-9]', '')) = 11 then
62:                         '(' || substr(regexp_replace(mobile_phone, '[^0-9]', ''),2,3) || ') ' ||
63:                         substr(regexp_replace(mobile_phone, '[^0-9]', ''),5,3) || '-' ||
64:                         substr(regexp_replace(mobile_phone, '[^0-9]', ''),8,4)
65:                     else null
66:                 end
67:             )
68:         end as mobile_phone,
69:         is_most_recent_record,
70:         is_most_recent_account_contact
71:     from normalized
72: )
73: select * from cleaned
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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('zuora_contact_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["zuora_contact_data","id","VARCHAR"],["zuora_contact_data","_fivetran_deleted","VARCHAR"],["zuora_contact_data","_fivetran_synced","VARCHAR"],["zuora_contact_data","account_id","VARCHAR"],["zuora_contact_data","address_1","VARCHAR"],["zuora_contact_data","address_2","VARCHAR"],["zuora_contact_data","city","VARCHAR"],["zuora_contact_data","country","VARCHAR"],["zuora_contact_data","county","VARCHAR"],["zuora_contact_data","created_by_id","VARCHAR"],["zuora_contact_data","created_date","VARCHAR"],["zuora_contact_data","description","VARCHAR"],["zuora_contact_data","fax","VARCHAR"],["zuora_contact_data","first_name","VARCHAR"],["zuora_contact_data","home_phone","VARCHAR"],["zuora_contact_data","last_name","VARCHAR"],["zuora_contact_data","mobile_phone","VARCHAR"],["zuora_contact_data","nick_name","VARCHAR"],["zuora_contact_data","other_phone","VARCHAR"],["zuora_contact_data","other_phone_type","VARCHAR"],["zuora_contact_data","personal_email","VARCHAR"],["zuora_contact_data","postal_code","VARCHAR"],["zuora_contact_data","state","VARCHAR"],["zuora_contact_data","tax_region","VARCHAR"],["zuora_contact_data","updated_by_id","VARCHAR"],["zuora_contact_data","updated_date","VARCHAR"],["zuora_contact_data","work_email","VARCHAR"],["zuora_contact_data","work_phone","VARCHAR"]]}
```


### 核实：本实体id与各外键是否相同
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast(account_id as varchar)) same_as_id FROM raw.zuora_contact_data
```


```json
{"columns":["col","n","nonnull","same_as_id"],"rows":[["account_id",7504,7504,0]]}
```


### 核实：候选外键匹配对照
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
SELECT 'account_id' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_col_matches FROM raw.zuora_contact_data s
```


```json
{"columns":["col","n","chosen_id_matches","named_col_matches"],"rows":[["account_id",7504,0,7501]]}
```


### 核实：实际纳入行的候选映射
[024_extra_diagnostics.json](../024_extra_diagnostics.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_contact_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(s.account_id) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data t WHERE cast(t.id as varchar)=cast(s.account_id as varchar))) named_matches FROM source_rows s
```


```json
{"columns":["col","n","nonnull","chosen_matches","named_matches"],"rows":[["account_id",3741,3741,0,3738]]}
```


### 核实：外键字段格式诊断（原可见数据）
[024_mapping_queries.json](../024_mapping_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。

```sql
WITH source_rows AS (
    SELECT *
    FROM raw.zuora_contact_data
    WHERE coalesce(lower(cast(_fivetran_deleted AS varchar)), 'false') NOT IN ('true', '1', 't'))
SELECT 'account_id' col,count(*) n,count(account_id) nonnull,count(*) FILTER(WHERE regexp_full_match(cast(account_id AS VARCHAR),'[A-Fa-f0-9]{32}')) hex32,count(*) FILTER(WHERE try_cast(account_id AS TIMESTAMP) IS NOT NULL) timestamps FROM source_rows
```


```json
{"columns":["col","n","nonnull","hex32","timestamps"],"rows":[["account_id",3741,3741,3741,0]]}
```

## 独立单点重跑

### 024_reruns_impl-030_stg_zuora__contact.json
[024_reruns_impl-030_stg_zuora__contact.json](../024_reruns_impl-030_stg_zuora__contact.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-030/agent/dacomp-de-impl-030/zuora.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-13 00:00:00+00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-13'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3741|3741|3741|3741|否|
|L1|3741|3741|3741|3741|否|
|L2|3741|3741|3741|3741|否|
|L3|3741|3741|3741|3741|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":3741}`
- L1：`{"account_id":3741}`
- L2：`{"account_id":3741}`
- L3：`{"account_id":3741}`

#### baseline
私有SQL：`data/024_work/impl-030_stg_zuora__contact/baseline.sql`；SHA-256 `bf54f51510529ae30a5018d891c3b79117fbe5e3f9e7f15edafa03757a618e2b`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3741|3741|3741|3741|否|
|L1|3741|3741|3741|3741|否|
|L2|3741|3741|3741|3741|否|
|L3|3741|3741|3741|3741|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"account_id":3741}`
- L1：`{"account_id":3741}`
- L2：`{"account_id":3741}`
- L3：`{"account_id":3741}`

#### source_account_id
主因；类别候选U。P：本实体id可替代account_id。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。
相对本轮基线：行减少3741，格减少3741。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第7行、offset 206起替换；其他字节相同。
原表达式：
```sql
try_cast("id" AS VARCHAR) AS account_id
```

修改后：
```sql
try_cast("account_id" AS VARCHAR) AS account_id
```

私有SQL：`data/024_work/impl-030_stg_zuora__contact/source_account_id.sql`；SHA-256 `e4ee70646802a38e9ea2ec8c345fafc4453bedded05c0d8cbbb141745d408868`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3741|3741|0|0|是|
|L1|3741|3741|0|0|是|
|L2|3741|3741|0|0|是|
|L3|3741|3741|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`
## 规则问题

无。

