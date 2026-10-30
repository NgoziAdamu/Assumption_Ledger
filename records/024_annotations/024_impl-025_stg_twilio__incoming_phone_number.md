# impl-025 · stg_twilio__incoming_phone_number

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**C**；把握：高。

agent先剥离电话标点并补+1，再校验；契约要求原电话格式失败置NULL，1484行单改后L0全匹配。

参与因素：无。
标记：无。

## 材料与比较口径

[024_impl-025_stg_twilio__incoming_phone_number.md](../024_packages/024_impl-025_stg_twilio__incoming_phone_number.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-025/docs/data_contract.yaml`。

```text
192:     - name: stg_twilio__incoming_phone_number
193:       description: "Validated inventory of incoming phone numbers with capabilities and metadata (matching current SQL behavior)."
194:       source_table: raw.twilio_incoming_phone_number_data
195:       columns:
196:         - name: account_id
197:           data_type: VARCHAR
198:         - name: address_requirements
199:           data_type: VARCHAR
200:         - name: beta
201:           data_type: BOOLEAN
202:         - name: capability_mms
203:           data_type: BOOLEAN
204:         - name: capability_sms
205:           data_type: BOOLEAN
206:         - name: capability_voice
207:           data_type: BOOLEAN
208:         - name: created_at
209:           data_type: TIMESTAMP
210:           constraints: [not_null]
211:           validation_rules:
212:             - rule: "created_at <= CURRENT_TIMESTAMP"
213:               on_failure: delete_row
214:         - name: updated_at
215:           data_type: TIMESTAMP
216:         - name: friendly_name
217:           data_type: VARCHAR
218:           validation_rules:
219:             - rule: "TRIM(friendly_name) RLIKE '^[A-Za-z0-9\\s._-]*$' AND LENGTH(TRIM(friendly_name)) <= 100"
220:               on_failure: nullify_field
221:         - name: phone_number
222:           data_type: VARCHAR
223:           validation_rules:
224:             - rule: "phone_number RLIKE '^\\+1[0-9]{10}$'"
225:               on_failure: nullify_field
226:         - name: emergency_status
227:           data_type: VARCHAR
228:           validation_rules:
229:             - rule: "emergency_status IN ('Active','Inactive','Pending') OR emergency_status IS NULL"
230:               on_failure: nullify_field
231:         - name: incoming_phone_number_id
232:           data_type: VARCHAR
233:         - name: voice_caller_id_lookup
234:           data_type: BOOLEAN
235:         - name: voice_url
236:           data_type: VARCHAR
237:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/sql/staging/stg_twilio__incoming_phone_number.sql`；SHA-256 `4b882bea82d12e038dcbe9621837de4aa81798d0bdd36d781ab5198d7cd0c1ef`。

```text
1: with source_data as (
2:     select
3:         account_id::varchar as account_id,
4:         address_requirements::varchar as address_requirements,
5:         beta::boolean as beta,
6:         capabilities_mms::boolean as capability_mms,
7:         capabilities_sms::boolean as capability_sms,
8:         capabilities_voice::boolean as capability_voice,
9:         try_cast(replace(created_at, ' UTC', '') as timestamp) as created_at,
10:         try_cast(replace(updated_at, ' UTC', '') as timestamp) as updated_at,
11:         friendly_name::varchar as friendly_name,
12:         regexp_replace(regexp_replace(phone_number, '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as phone_number_normalized,
13:         emergency_status::varchar as emergency_status,
14:         id::varchar as incoming_phone_number_id,
15:         voice_caller_id_lookup::boolean as voice_caller_id_lookup,
16:         voice_url::varchar as voice_url
17:     from raw.incoming_phone_number_data
18: ),
19: cleaned as (
20:     select
21:         account_id, address_requirements, beta, capability_mms, capability_sms, capability_voice,
22:         created_at, updated_at,
23:         case when friendly_name is null then null
24:              when regexp_matches(trim(friendly_name), '^[A-Za-z0-9\s._-]*$') and length(trim(friendly_name)) <= 100 then friendly_name
25:              else null end as friendly_name,
26:         case when regexp_matches(phone_number_normalized, '^\+1[0-9]{10}$') then phone_number_normalized else null end as phone_number,
27:         case when emergency_status in ('Active','Inactive','Pending') or emergency_status is null then emergency_status else null end as emergency_status,
28:         incoming_phone_number_id, voice_caller_id_lookup, voice_url
29:     from source_data
30: )
31: select account_id, address_requirements, beta, capability_mms, capability_sms, capability_voice,
32:        created_at, updated_at, friendly_name, phone_number, emergency_status,
33:        incoming_phone_number_id, voice_caller_id_lookup, voice_url
34: from cleaned
35: where created_at is not null and created_at <= current_timestamp
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-025/sql/staging/stg_twilio__incoming_phone_number.sql`；SHA-256 `e051b1fb2f6e8a1706504bfed875700ab75d9485f2c637026fbd3b0a39b6d2c4`。

```text
1: with base as (
2:     select *
3:     from raw.incoming_phone_number_data
4: ),
5: 
6: fields as (
7:     select
8:         account_id,
9:         address_requirements,
10:         beta,
11:         capabilities_mms as capability_mms,
12:         capabilities_sms as capability_sms,
13:         capabilities_voice as capability_voice,
14:         try_cast(created_at as timestamp) as created_at,
15:         try_cast(updated_at as timestamp) as updated_at,
16:         cast(emergency_status as varchar) as emergency_status,
17:         friendly_name,
18:         cast(phone_number as varchar) as phone_number,
19:         cast(id as varchar) as incoming_phone_number_id,
20:         voice_caller_id_lookup,
21:         voice_url
22:     from base
23: ),
24: 
25: filtered as (
26:     select *
27:     from fields
28:     where
29:         created_at is not null
30:         and created_at <= current_timestamp
31: ),
32: 
33: final as (
34:     select
35:         account_id,
36:         address_requirements,
37:         beta,
38:         capability_mms,
39:         capability_sms,
40:         capability_voice,
41:         created_at,
42:         updated_at,
43:         case when friendly_name is null then null
44:              when trim(cast(friendly_name as varchar)) ~ '^[A-Za-z0-9\s._-]*$' and length(trim(cast(friendly_name as varchar))) <= 100
45:              then trim(cast(friendly_name as varchar))
46:              else null end as friendly_name,
47:         case when phone_number ~ '^\+1[0-9]{10}$' then phone_number else null end as phone_number,
48:         case when emergency_status in ('Active', 'Inactive', 'Pending') or emergency_status is null then emergency_status else null end as emergency_status,
49:         incoming_phone_number_id,
50:         voice_caller_id_lookup,
51:         voice_url
52:     from filtered
53: )
54: 
55: select *
56: from final
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- phone_number_normalized（C）：**看到了但没提**；事件 15、16、17、21、22、25、26。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/15.json`；命令首行：`python - <<'PY'`。
event 16：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/16.json`；原始观察输出。
event 17：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/17.json`；命令首行：`mkdir -p sql/staging sql/intermediate sql/marts && cat > /tmp/write_sql.py <<'PY'`。
event 21：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/21.json`；命令首行：`sed -n '1,240p' test_single_sql.py && python - <<'PY'`。
event 22：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/22.json`；原始观察输出。
event 25：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/25.json`；命令首行：`python - <<'PY'`。
event 26：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/26.json`；原始观察输出。

最终报告原文（用于复核说明和工作清单边界）：

```
【回复用户】

已按照 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 SQL 实现，按 staging → intermediate → marts 顺序生成了 16 个模型文件：

- `sql/staging/`：8 个 staging 表
- `sql/intermediate/`：5 个 intermediate 模型
- `sql/marts/`：3 个 marts 模型

实现使用 DuckDB SQL、显式 `schema.table` 上游引用，不含 dbt `ref()`，并且所有 SQL 文件均未以分号结尾。模型输出字段名称与契约定义逐项核对一致。

**验证结果**

- 执行 `python run.py` 成功，staging 8/8、intermediate 5/5、marts 3/3 全部生成。
- 使用 DuckDB 对契约模型输出字段名进行检查，16 个模型全部匹配。
- 对完成后微调过的 incoming/outgoing phone number staging SQL 额外进行了 DuckDB 执行检查；语句可执行。
- 依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。未执行去重，除契约明确要求的账户 latest 选择外保留重复记录。

**数据质量说明**

`stg_twilio__outgoing_caller_id` 产出 0 行。源表样例中 `friendly_name` 值为类似编码标识的字符串，而 `phone_number` 值为 `(555) 555-6062` 这类非 E.164 标签；因此无法满足契约要求的有效 `+1XXXXXXXXXX` 电话格式，按该表的 delete-row 规则过滤。残余影响是该批数据没有可用于下游的 outgoing caller ID 记录；没有为保留数据而推测或交换源字段含义。

本次验证没有失败的 SQL 语句；无需进行 SQL 错误修复。

**交付环境说明**

尝试写入指定的 `/workspace/result.md` 时，运行环境因根文件系统只读且 `/workspace` 路径不存在而拒绝创建该文件。报告内容保存在项目根目录 `result.md`。
```

## 查询

核实查询 **2** 条；代价档：**多条查询**。含失败后重试的每条SQL；诊断查询不计入5条上限。

### 核实：直接raw列名类型
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/twilio.duckdb`。

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('incoming_phone_number_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["incoming_phone_number_data","id","VARCHAR"],["incoming_phone_number_data","_fivetran_synced","VARCHAR"],["incoming_phone_number_data","account_id","VARCHAR"],["incoming_phone_number_data","address_id","VARCHAR"],["incoming_phone_number_data","address_requirements","VARCHAR"],["incoming_phone_number_data","beta","BOOLEAN"],["incoming_phone_number_data","capabilities_mms","BOOLEAN"],["incoming_phone_number_data","capabilities_sms","BOOLEAN"],["incoming_phone_number_data","capabilities_voice","BOOLEAN"],["incoming_phone_number_data","created_at","VARCHAR"],["incoming_phone_number_data","emergency_address_id","VARCHAR"],["incoming_phone_number_data","emergency_status","VARCHAR"],["incoming_phone_number_data","friendly_name","VARCHAR"],["incoming_phone_number_data","origin","VARCHAR"],["incoming_phone_number_data","phone_number","VARCHAR"],["incoming_phone_number_data","trunk_id","DOUBLE"],["incoming_phone_number_data","updated_at","VARCHAR"],["incoming_phone_number_data","voice_caller_id_lookup","BOOLEAN"],["incoming_phone_number_data","voice_url","VARCHAR"]]}
```


### 核实：原始电话格式与name空白
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/twilio.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE regexp_matches(phone_number,'^\+1[0-9]{10}$')) valid_phone,count(*) FILTER(WHERE friendly_name<>trim(friendly_name)) whitespace_name FROM raw.incoming_phone_number_data
```


```json
{"columns":["n","valid_phone","whitespace_name"],"rows":[[1500,0,0]]}
```

## 独立单点重跑

### 024_reruns_impl-025_stg_twilio__incoming_phone_number.json
[024_reruns_impl-025_stg_twilio__incoming_phone_number.json](../024_reruns_impl-025_stg_twilio__incoming_phone_number.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/twilio.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-12 00:00:00+00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-12'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1484|1484|否|
|L1|1495|1495|1484|1484|否|
|L2|1495|1495|1484|1484|否|
|L3|1495|1495|1484|1484|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"phone_number":1484}`
- L1：`{"phone_number":1484}`
- L2：`{"phone_number":1484}`
- L3：`{"phone_number":1484}`

#### baseline
私有SQL：`data/024_work/impl-025_stg_twilio__incoming_phone_number/baseline.sql`；SHA-256 `69e797969c0cbbc905a78ea8e18167c8a9e93189a6438be238003da1801448a4`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1484|1484|否|
|L1|1495|1495|1484|1484|否|
|L2|1495|1495|1484|1484|否|
|L3|1495|1495|1484|1484|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"phone_number":1484}`
- L1：`{"phone_number":1484}`
- L2：`{"phone_number":1484}`
- L3：`{"phone_number":1484}`

#### phone_number_normalized
主因；类别候选C。契约失败动作是nullify；agent预先去标点补+1，使不合法原值变成合法电话。
相对本轮基线：行减少1484，格减少1484。严格U第4条件：达到（非U不据此改类）。
共同控制后SQL第12行、offset 546起替换；其他字节相同。
原表达式：
```sql
regexp_replace(regexp_replace(phone_number, '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as phone_number_normalized
```

修改后：
```sql
phone_number as phone_number_normalized
```

私有SQL：`data/024_work/impl-025_stg_twilio__incoming_phone_number/phone_number_normalized.sql`；SHA-256 `d2e4c495cf7a2ebcd6dd19840b60e1582ffa6fb2979640b3098f47e1e7b271dd`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|0|0|是|
|L1|1495|1495|0|0|是|
|L2|1495|1495|0|0|是|
|L3|1495|1495|0|0|是|

首次整表匹配：**L0**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

#### friendly_trim
不计参与因素；类别候选A。契约验证TRIM后的文本，但未明确输出是否trim；gold输出trim。
相对本轮基线：行减少0，格减少0。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第24行、offset 1239起替换；其他字节相同。
原表达式：
```sql
then friendly_name
```

修改后：
```sql
then trim(friendly_name)
```

私有SQL：`data/024_work/impl-025_stg_twilio__incoming_phone_number/friendly_trim.sql`；SHA-256 `7c446123d7d6e5967f15193bddd2503862cd9e433c173fc36b8ac6fcf2af7b37`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1495|1495|1484|1484|否|
|L1|1495|1495|1484|1484|否|
|L2|1495|1495|1484|1484|否|
|L3|1495|1495|1484|1484|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"phone_number":1484}`
- L1：`{"phone_number":1484}`
- L2：`{"phone_number":1484}`
- L3：`{"phone_number":1484}`
## 规则问题

无。

