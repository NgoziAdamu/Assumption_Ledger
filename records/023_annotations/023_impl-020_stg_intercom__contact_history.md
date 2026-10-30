# impl-020 · stg_intercom__contact_history

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：phone_gold_regex。

agent 按契约显式 E.164 正则保留1079条合法号码，gold双反斜杠正则拒绝这些号码。

参与因素：无。

标记：无。



## 材料与比较口径

精简材料包：[023_impl-020_stg_intercom__contact_history.md](../023_packages/023_impl-020_stg_intercom__contact_history.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-020/docs/data_contract.yaml`；SHA-256 `b19cdce65b55dd44086f5a7ef864055abfe48bd66f5d6f430785084ab3cd5314`。
契约行 94–140：

```
94:     - name: stg_intercom__contact_history
95:       description: "Contact attributes over time with standardized identifiers, email, and phone normalization."
96:       source_table: raw.contact_history_data
97:       columns:
98:         - name: contact_id
99:           data_type: VARCHAR
100:         - name: admin_id
101:           data_type: BIGINT
102:         - name: created_at
103:           data_type: TIMESTAMP
104:         - name: updated_at
105:           data_type: TIMESTAMP
106:         - name: signed_up_at
107:           data_type: TIMESTAMP
108:         - name: contact_name
109:           data_type: VARCHAR
110:           validation_rules:
111:             - rule: "contact_name = TRIM(contact_name)"
112:               on_failure: correct
113:         - name: contact_role
114:           data_type: VARCHAR
115:         - name: contact_email
116:           data_type: VARCHAR
117:           validation_rules:
118:             - rule: "contact_email = LOWER(TRIM(contact_email))"
119:               on_failure: correct
120:         - name: last_replied_at
121:           data_type: TIMESTAMP
122:         - name: last_email_clicked_at
123:           data_type: TIMESTAMP
124:         - name: last_email_opened_at
125:           data_type: TIMESTAMP
126:         - name: last_contacted_at
127:           data_type: TIMESTAMP
128:         - name: is_unsubscribed_from_emails
129:           data_type: BOOLEAN
130:         - name: phone
131:           data_type: VARCHAR
132:           validation_rules:
133:             - rule: "Normalize to E.164 where deterministically possible"
134:               on_failure: correct
135:             - rule: "phone IS NULL OR phone matches E.164 (^[+][1-9][0-9]{1,14}$)"
136:               on_failure: nullify_field
137:       row_filters:
138:         - rule: "Retain record unless _fivetran_active is explicitly false after type coercion (null or missing treated as active)"
139:           on_failure: delete_row
140:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/sql/staging/stg_intercom__contact_history.sql`，SHA-256 `4fb7b8075a4174b44c4e5ba50b573400700d9803626cfb0a3bbba63a51e5c705`，行 1–32。

```
1: with typed as (
2:     select
3:         try_cast(id as varchar) as contact_id,
4:         try_cast(admin_id as bigint) as admin_id,
5:         try_cast(created_at as timestamp) as created_at,
6:         try_cast(updated_at as timestamp) as updated_at,
7:         try_cast(signed_up_at as timestamp) as signed_up_at,
8:         trim(try_cast(name as varchar)) as contact_name,
9:         try_cast(role as varchar) as contact_role,
10:         lower(trim(try_cast(email as varchar))) as contact_email,
11:         try_cast(last_replied_at as timestamp) as last_replied_at,
12:         try_cast(last_email_clicked_at as timestamp) as last_email_clicked_at,
13:         try_cast(last_email_opened_at as timestamp) as last_email_opened_at,
14:         try_cast(last_contacted_at as timestamp) as last_contacted_at,
15:         coalesce(try_cast(unsubscribed_from_emails as boolean), false) as is_unsubscribed_from_emails,
16:         nullif(regexp_replace(trim(try_cast(phone as varchar)), '[^0-9+]', '', 'g'), '') as normalized_phone,
17:         coalesce(try_cast(_fivetran_active as boolean), true) as is_active
18:     from raw.contact_history_data
19: ), normalized as (
20:     select *,
21:         case
22:             when normalized_phone is null then null
23:             when regexp_matches(normalized_phone, '^\+[1-9][0-9]{1,14}$') then normalized_phone
24:             else null
25:         end as phone_e164
26:     from typed
27: )
28: select contact_id, admin_id, created_at, updated_at, signed_up_at, contact_name, contact_role,
29:        contact_email, last_replied_at, last_email_clicked_at, last_email_opened_at, last_contacted_at,
30:        is_unsubscribed_from_emails, phone_e164 as phone
31: from normalized
32: where is_active
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/sql/staging/stg_intercom__contact_history.sql`，SHA-256 `b8fe5cd5c80fc013000852852ef992e74fec61ea222fe1867f5a0485b6f1da5d`，行 1–53。

```
1: with src as (
2:   select
3:     id as contact_id,
4:     admin_id,
5:     created_at,
6:     updated_at,
7:     signed_up_at,
8:     trim(name) as contact_name,
9:     role as contact_role,
10:     lower(trim(email)) as contact_email,
11:     last_replied_at,
12:     last_email_clicked_at,
13:     last_email_opened_at,
14:     last_contacted_at,
15:     unsubscribed_from_emails as is_unsubscribed_from_emails,
16:     phone
17:   from raw.contact_history_data
18:   where coalesce(try_cast(_fivetran_active as BOOLEAN), true)
19: ),
20: phone_clean as (
21:   select
22:     *,
23:     -- normalize phone by stripping non-digits and enforcing + prefix if possible
24:     case
25:       when phone is null then null
26:       else regexp_replace(phone, '[^0-9+]', '', 'g')
27:     end as phone_norm1
28:   from src
29: ),
30: phone_fix as (
31:   select
32:     contact_id,
33:     admin_id,
34:     created_at,
35:     updated_at,
36:     signed_up_at,
37:     contact_name,
38:     contact_role,
39:     contact_email,
40:     last_replied_at,
41:     last_email_clicked_at,
42:     last_email_opened_at,
43:     last_contacted_at,
44:     is_unsubscribed_from_emails,
45:     case
46:       when phone_norm1 ~ '^\\+[1-9]\\d{1,14}$' then phone_norm1
47:       when phone_norm1 ~ '^[1-9]\\d{1,14}$' then '+' || phone_norm1
48:       else null
49:     end as phone
50:   from phone_clean
51: )
52: select *
53: from phone_fix
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 21/22 读取raw；event 45 修改本表不推断无+前缀的国家码；event 61 的“电话满足E.164”是验证清单，未说明差异涉及的regex转义。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 21：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/21.json`。
- event 22：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/22.json`。
- event 45：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/45.json`。
- event 61：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-020/agent/.events/sessions/d941a7da-bdc4-45-53dddc7bd821982/events/61.json`。
## 查询

核实查询 **0** 条；核实代价档：**需要查业务说明**。诊断查询不计入 5 条上限。

未追加 agent 可见数据核实；判断依据为契约、SQL 和明确标为诊断的查询，不用 gold 结果证明 U。

### 诊断：显式 phone 规则与 gold regexp

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-020/intercom.duckdb`。

```sql
WITH x AS(SELECT regexp_replace(phone,'[^0-9+]','','g') p FROM raw.contact_history_data WHERE coalesce(try_cast(_fivetran_active AS BOOLEAN),true)) SELECT count(*) FILTER(WHERE regexp_full_match(p,'^[+][1-9][0-9]{1,14}$')) contract_valid,count(*) FILTER(WHERE regexp_full_match(p,'^\\+[1-9]\\d{1,14}$')) gold_valid FROM x
```


```json
{"columns":["contract_valid","gold_valid"],"rows":[[1079,0]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-020_stg_intercom__contact_history.json](../023_reruns_impl-020_stg_intercom__contact_history.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/intercom.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2707|2707|1079|1079|否|
|L1|2707|2707|1079|1079|否|
|L2|2707|2707|1079|1079|否|
|L3|2707|2707|1079|1079|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"phone":1079}`
- L1：`{"phone":1079}`
- L2：`{"phone":1079}`
- L3：`{"phone":1079}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-020_stg_intercom__contact_history/baseline.sql`；SHA-256 `4fb7b8075a4174b44c4e5ba50b573400700d9803626cfb0a3bbba63a51e5c705`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2707|2707|1079|1079|否|
|L1|2707|2707|1079|1079|否|
|L2|2707|2707|1079|1079|否|
|L3|2707|2707|1079|1079|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"phone":1079}`
- L1：`{"phone":1079}`
- L2：`{"phone":1079}`
- L3：`{"phone":1079}`
### 补充轮：[023_supplement_reruns_impl-020_stg_intercom__contact_history.json](../023_supplement_reruns_impl-020_stg_intercom__contact_history.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-020/agent/dacomp-de-impl-020/intercom.duckdb`。

共同时间控制：`[]`。

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_supplement_work/impl-020_stg_intercom__contact_history/baseline.sql`；SHA-256 `4fb7b8075a4174b44c4e5ba50b573400700d9803626cfb0a3bbba63a51e5c705`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2707|2707|1079|1079|否|
|L1|2707|2707|1079|1079|否|
|L2|2707|2707|1079|1079|否|
|L3|2707|2707|1079|1079|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"phone":1079}`
- L1：`{"phone":1079}`
- L2：`{"phone":1079}`
- L3：`{"phone":1079}`

#### phone_gold_regex

判定：主因；类别候选 O。契约显式 E.164 允许的1079条，gold 双反斜杠表达式全部拒绝。

相对本轮基线减少行 1079、格 1079；按行优先、格次之排序。
共同控制后 SQL 第 23 行起、字符 offset 1204 的唯一连续替换；其余字节不动。
替换前：
```sql
regexp_matches(normalized_phone, '^\+[1-9][0-9]{1,14}$')
```

替换后：
```sql
regexp_matches(normalized_phone, '^\\+[1-9]\\d{1,14}$')
```

私有 SQL：`data/023_supplement_work/impl-020_stg_intercom__contact_history/phone_gold_regex.sql`；SHA-256 `98d12b04ebb636f1665bc3191b8e27d7f3f17bdbb237790ce1eb2fe15c8a8efe`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2707|2707|0|0|是|
|L1|2707|2707|0|0|是|
|L2|2707|2707|0|0|是|
|L3|2707|2707|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 规则问题

无
