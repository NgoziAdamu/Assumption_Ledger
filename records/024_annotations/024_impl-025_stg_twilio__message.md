# impl-025 · stg_twilio__message

用途：**全量**；层：**staging**；013状态：待标注；手册：v2冻结版。

## 结论

主要原因：**C**；把握：高。

from与to两处均先规范化电话再校验，违背格式失败置NULL；to单改按行减少10，from单改减少8，故to主因、from参与。

参与因素：C：from_normalized（行减8，格减2485）。
标记：无。

## 材料与比较口径

[024_impl-025_stg_twilio__message.md](../024_packages/024_impl-025_stg_twilio__message.md)；[标注手册_v2.md](../../docs/标注手册_v2.md)。
官方状态不重定；全表比较列为评测键与原评测列的并集。staging用agent留存raw，intermediate/marts用gold上游（CS）。原数据库READ_ONLY；执行只写data/024_*私有库。日期/时间为共同控制，不算错误点。
规模按行优先，再按格子排序。重复键先消去相同整行，再按同键字典序配对残余行；独有行乘全部比较列计入格子。
本表完整结果见下列L0–L3记录。正向单改才列参与因素；零改善项明确不列。组合诊断不用于单点排名。

## 契约与两边 SQL 原文

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-025/docs/data_contract.yaml`。

```text
238:     - name: stg_twilio__message
239:       description: "Cleaned and standardized SMS/MMS message records with validated phone/status fields (types aligned to current implementation)."
240:       source_table: raw.twilio_message_data
241:       columns:
242:         - name: account_id
243:           data_type: VARCHAR
244:         - name: body
245:           data_type: VARCHAR
246:         - name: created_at
247:           data_type: TIMESTAMP
248:           constraints: [not_null]
249:           validation_rules:
250:             - rule: "created_at <= CURRENT_TIMESTAMP"
251:               on_failure: delete_row
252:         - name: timestamp_sent
253:           data_type: TIMESTAMP
254:           description: "Normalized send timestamp from raw date_sent."
255:         - name: direction
256:           data_type: VARCHAR
257:         - name: error_code
258:           data_type: VARCHAR
259:         - name: error_message
260:           data_type: VARCHAR
261:         - name: message_from
262:           data_type: VARCHAR
263:           validation_rules:
264:             - rule: "message_from RLIKE '^\\+1[0-9]{10}$'"
265:               on_failure: nullify_field
266:         - name: message_id
267:           data_type: VARCHAR
268:         - name: messaging_service_id
269:           data_type: VARCHAR
270:         - name: num_media
271:           data_type: DOUBLE
272:         - name: num_segments
273:           data_type: DOUBLE
274:         - name: price
275:           data_type: DOUBLE
276:         - name: price_unit
277:           data_type: VARCHAR
278:         - name: status
279:           data_type: VARCHAR
280:           validation_rules:
281:             - rule: "status IN ('accepted','queued','sending','sent','failed','delivered','undelivered','receiving','received')"
282:               on_failure: nullify_field
283:         - name: message_to
284:           data_type: VARCHAR
285:           validation_rules:
286:             - rule: "message_to RLIKE '^\\+1[0-9]{10}$'"
287:               on_failure: nullify_field
288:         - name: updated_at
289:           data_type: TIMESTAMP
290:           validation_rules:
291:             - rule: "updated_at IS NULL OR updated_at >= created_at"
292:               on_failure: delete_row
293:
```

agent最终SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/sql/staging/stg_twilio__message.sql`；SHA-256 `7700c47dfaf009545823a89f2b95910ae42dfe93ca80e5dcee1b93b3e2d8891f`。

```text
1: with source_data as (
2:     select
3:         account_id::varchar as account_id,
4:         body::varchar as body,
5:         try_cast(replace(created_at, ' UTC', '') as timestamp) as created_at,
6:         try_cast(replace(date_sent, ' UTC', '') as timestamp) as timestamp_sent,
7:         direction::varchar as direction,
8:         error_code::double as error_code,
9:         error_message::double as error_message,
10:         regexp_replace(regexp_replace("from", '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as from_normalized,
11:         id::varchar as message_id,
12:         messaging_service_sid::varchar as messaging_service_id,
13:         num_media::double as num_media,
14:         num_segments::double as num_segments,
15:         price::double as price,
16:         price_unit::varchar as price_unit,
17:         status::varchar as status,
18:         regexp_replace(regexp_replace("to", '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as to_normalized,
19:         try_cast(replace(updated_at, ' UTC', '') as timestamp) as updated_at
20:     from raw.message_data
21: ),
22: cleaned as (
23:     select
24:         account_id, body, created_at, timestamp_sent, direction, error_code, error_message,
25:         case when regexp_matches(from_normalized, '^\+1[0-9]{10}$') then from_normalized else null end as message_from,
26:         message_id, messaging_service_id, num_media, num_segments, price, price_unit,
27:         case when status in ('accepted','queued','sending','sent','failed','delivered','undelivered','receiving','received') then status else null end as status,
28:         case when regexp_matches(to_normalized, '^\+1[0-9]{10}$') then to_normalized else null end as message_to,
29:         updated_at
30:     from source_data
31: )
32: select account_id, body, created_at, timestamp_sent, direction, error_code, error_message,
33:        message_from, message_id, messaging_service_id, num_media, num_segments, price, price_unit,
34:        status, message_to, updated_at
35: from cleaned
36: where created_at is not null and created_at <= current_timestamp
37:   and (updated_at is null or updated_at >= created_at)
```

gold SQL（仅诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-025/sql/staging/stg_twilio__message.sql`；SHA-256 `bca9d12fd1a849b956b4b2edfa8f8f7b93eb9088349a28986df235030a5b8daa`。

```text
1: with base as (
2:     select *
3:     from raw.message_data
4: ),
5: 
6: fields as (
7:     select
8:         account_id,
9:         body,
10:         try_cast(created_at as timestamp) as created_at,
11:         try_cast(date_sent as timestamp) as timestamp_sent,
12:         direction,
13:         error_code,
14:         error_message,
15:         "from" as message_from,
16:         id as message_id,
17:         messaging_service_sid as messaging_service_id,
18:         num_media,
19:         num_segments,
20:         price,
21:         price_unit,
22:         status,
23:         "to" as message_to,
24:         try_cast(updated_at as timestamp) as updated_at
25:     from base
26: ),
27: 
28: filtered as (
29:     select *
30:     from fields
31:     where
32:         created_at is not null
33:         and created_at <= current_timestamp
34:         and (updated_at is null or created_at <= updated_at)
35: ),
36: 
37: final as (
38:     select
39:         account_id,
40:         body,
41:         created_at,
42:         timestamp_sent,
43:         direction,
44:         error_code,
45:         error_message,
46:         case when message_from ~ '^\+1[0-9]{10}$' then message_from else null end as message_from,
47:         message_id,
48:         cast(messaging_service_id as varchar) as messaging_service_id,
49:         cast(num_media as double) as num_media,
50:         cast(num_segments as double) as num_segments,
51:         cast(price as double) as price,
52:         price_unit,
53:         case when status in ('accepted', 'queued', 'sending', 'sent', 'failed', 'delivered', 'undelivered', 'receiving', 'received') then status else null end as status,
54:         case when message_to ~ '^\+1[0-9]{10}$' then message_to else null end as message_to,
55:         updated_at
56:     from filtered
57: )
58: 
59: select *
60: from final
```

## 轨迹可见性与不确定性

已逐题检查原始事件的action、观察输出及最终result.md；原记录截断之外不推定agent看过。代码写入命令本身不视为核实数据。工作清单不算策略。
轨迹索引：[024_trace_audit.json](../024_trace_audit.json)。

- to_normalized（C）：**看到了但没提**；事件 15、16、17、21、22。
未找到针对这个差异选择的说明；上列可见资料/执行检查不等于讨论了该差异。
event 15：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/15.json`；命令首行：`python - <<'PY'`。
event 16：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/16.json`；原始观察输出。
event 17：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/17.json`；命令首行：`mkdir -p sql/staging sql/intermediate sql/marts && cat > /tmp/write_sql.py <<'PY'`。
event 21：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/21.json`；命令首行：`sed -n '1,240p' test_single_sql.py && python - <<'PY'`。
event 22：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-025/agent/.events/sessions/8c5a61dc-1100-47-e057d2ed98d5a5a/events/22.json`；原始观察输出。

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
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ('message_data') ORDER BY table_name,ordinal_position
```


```json
{"columns":["table_name","column_name","data_type"],"rows":[["message_data","id","VARCHAR"],["message_data","_fivetran_synced","VARCHAR"],["message_data","account_id","VARCHAR"],["message_data","body","VARCHAR"],["message_data","created_at","VARCHAR"],["message_data","date_sent","VARCHAR"],["message_data","direction","VARCHAR"],["message_data","error_code","DOUBLE"],["message_data","error_message","DOUBLE"],["message_data","from","VARCHAR"],["message_data","messaging_service_sid","VARCHAR"],["message_data","num_media","BIGINT"],["message_data","num_segments","BIGINT"],["message_data","price","DOUBLE"],["message_data","price_unit","VARCHAR"],["message_data","status","VARCHAR"],["message_data","to","VARCHAR"],["message_data","updated_at","VARCHAR"]]}
```


### 核实：两处原始电话格式
[024_queries.json](../024_queries.json)
数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/twilio.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE regexp_matches("from",'^\+1[0-9]{10}$')) valid_from,count(*) FILTER(WHERE regexp_matches("to",'^\+1[0-9]{10}$')) valid_to FROM raw.message_data
```


```json
{"columns":["n","valid_from","valid_to"],"rows":[[2500,0,0]]}
```

## 独立单点重跑

### 024_reruns_impl-025_stg_twilio__message.json
[024_reruns_impl-025_stg_twilio__message.json](../024_reruns_impl-025_stg_twilio__message.json)
上游：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-025/agent/dacomp-de-impl-025/twilio.duckdb`。
时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-12 00:00:00+00'","count":1},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-12'","count":0}]`。
历史留存结果：
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2495|2495|2495|4972|否|
|L1|2495|2495|2495|4972|否|
|L2|2495|2495|2495|4972|否|
|L3|2495|2495|2495|4972|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"message_from":2485,"message_to":2487}`
- L1：`{"message_from":2485,"message_to":2487}`
- L2：`{"message_from":2485,"message_to":2487}`
- L3：`{"message_from":2485,"message_to":2487}`

#### baseline
私有SQL：`data/024_work/impl-025_stg_twilio__message/baseline.sql`；SHA-256 `a483d61dec8327f5d52a66eb08ee16e3befd6842465801e5ce66a58590f18593`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2495|2495|2495|4972|否|
|L1|2495|2495|2495|4972|否|
|L2|2495|2495|2495|4972|否|
|L3|2495|2495|2495|4972|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"message_from":2485,"message_to":2487}`
- L1：`{"message_from":2485,"message_to":2487}`
- L2：`{"message_from":2485,"message_to":2487}`
- L3：`{"message_from":2485,"message_to":2487}`

#### from_normalized
参与因素；类别候选C。契约失败动作是nullify；agent预先去标点补+1，使不合法原值变成合法电话。
相对本轮基线：行减少8，格减少2485。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第10行、offset 405起替换；其他字节相同。
原表达式：
```sql
regexp_replace(regexp_replace("from", '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as from_normalized
```

修改后：
```sql
"from" as from_normalized
```

私有SQL：`data/024_work/impl-025_stg_twilio__message/from_normalized.sql`；SHA-256 `cae6c08819af2e8532d2991e3468b052cb443a0432ff196e36b6181e857db0e3`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2495|2495|2487|2487|否|
|L1|2495|2495|2487|2487|否|
|L2|2495|2495|2487|2487|否|
|L3|2495|2495|2487|2487|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"message_to":2487}`
- L1：`{"message_to":2487}`
- L2：`{"message_to":2487}`
- L3：`{"message_to":2487}`

#### to_normalized
主因；类别候选C。契约失败动作是nullify；agent预先去标点补+1，使不合法原值变成合法电话。
相对本轮基线：行减少10，格减少2487。严格U第4条件：未达到（非U不据此改类）。
共同控制后SQL第18行、offset 813起替换；其他字节相同。
原表达式：
```sql
regexp_replace(regexp_replace("to", '[^0-9]', '', 'g'), '^1?([0-9]{10})$', '+1\1') as to_normalized
```

修改后：
```sql
"to" as to_normalized
```

私有SQL：`data/024_work/impl-025_stg_twilio__message/to_normalized.sql`；SHA-256 `8d97411740d8384f775056806604fa14d2fb14c9ab027ff7c0e3573dec2c4834`。
|档位|agent行|gold行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2495|2495|2485|2485|否|
|L1|2495|2495|2485|2485|否|
|L2|2495|2495|2485|2485|否|
|L3|2495|2495|2485|2485|否|

首次整表匹配：**仍不匹配**。
每列不一致数（含独有行/重复余量，未列为0）：
- L0：`{"message_from":2485}`
- L1：`{"message_from":2485}`
- L2：`{"message_from":2485}`
- L3：`{"message_from":2485}`
## 规则问题

无。

