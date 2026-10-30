# impl-021 · stg_klaviyo__person

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**A**；把握：高；主要错误点：null_id_filter。

person_id没有非空要求，agent额外删除NULL ID行而gold保留；属契约未规定的过滤取舍。

参与因素：无。

标记：无。

单改ID过滤1190行/19040格→1行/1格；剩余phone_number归一化差异只在原来被筛掉的行，未作为可独立改善的参与因素。full_name_null单改无改善，不列因素。

## 材料与比较口径

精简材料包：[023_impl-021_stg_klaviyo__person.md](../023_packages/023_impl-021_stg_klaviyo__person.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-021/docs/data_contract.yaml`；SHA-256 `db04fb84955b6385dd63b72bdf7aae27ac9f612a685f938eabf7051f12cd675f`。
契约行 164–223：

```
164:     - name: stg_klaviyo__person
165:       description: "Cleaned person dimension with normalized phone numbers and standardized email/timezone."
166:       source_table: raw.person
167:       columns:
168:         - name: person_id
169:           data_type: VARCHAR
170:         - name: address_1
171:           data_type: VARCHAR
172:         - name: address_2
173:           data_type: VARCHAR
174:         - name: city
175:           data_type: VARCHAR
176:         - name: country
177:           data_type: VARCHAR
178:         - name: zip
179:           data_type: VARCHAR
180:         - name: created_at
181:           data_type: TIMESTAMP
182:         - name: email
183:           data_type: VARCHAR
184:           validation_rules:
185:             - rule: "email is NULL or matches RFC5322-like basic regex"
186:               on_failure: delete_row
187:             - rule: "when present and length(email) > 255 then nullify; otherwise lower-trim"
188:               on_failure: nullify_field
189:         - name: full_name
190:           data_type: VARCHAR
191:           description: Concatenation of first_name and last_name; may be NULL if both are missing
192:         - name: latitude
193:           data_type: DOUBLE
194:         - name: longitude
195:           data_type: DOUBLE
196:         - name: organization
197:           data_type: VARCHAR
198:         - name: phone_number
199:           data_type: VARCHAR
200:           validation_rules:
201:             - rule: "phone_number is NULL or normalized by removing non-digits and prefixing with '+' (E.164-like)"
202:               on_failure: correct
203:         - name: region
204:           data_type: VARCHAR
205:         - name: timezone
206:           data_type: VARCHAR
207:           validation_rules:
208:             - rule: "timezone is lower-trimmed"
209:               on_failure: correct
210:           description: Stored as lower-trimmed string; no further IANA standardization applied
211:         - name: title
212:           data_type: VARCHAR
213:         - name: updated_at
214:           data_type: TIMESTAMP
215:         - name: last_event_date
216:           data_type: TIMESTAMP
217:         - name: source_relation
218:           data_type: VARCHAR
219:           constraints: [not_null]
220: 
221: # --------------------------------------------------------------------------- #
222: # PHASE 2: Defines the business logic from staging tables to analytical models. #
223: # --------------------------------------------------------------------------- #
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/sql/staging/stg_klaviyo__person.sql`，SHA-256 `c1c19d10e6d80bd7fe487cd7564f89908c00ee7f951133962e90cb7950dfebf6`，行 1–17。

```
1: with base as (
2:  select *, lower(trim(cast(email as varchar))) cleaned_email,
3:         regexp_replace(coalesce(cast(phone_number as varchar), ''), '[^0-9]', '', 'g') phone_digits
4:  from raw.person
5: )
6: select cast(id as varchar) person_id, cast(address_1 as varchar) address_1, cast(address_2 as varchar) address_2,
7:  cast(city as varchar) city, cast(country as varchar) country, cast(zip as varchar) zip,
8:  try_cast(created as timestamp) created_at,
9:  case when length(cleaned_email)>255 then null else cleaned_email end email,
10:  nullif(trim(concat_ws(' ', nullif(trim(cast(first_name as varchar)), ''), nullif(trim(cast(last_name as varchar)), ''))), '') full_name,
11:  try_cast(latitude as double) latitude, try_cast(longitude as double) longitude, cast(organization as varchar) organization,
12:  case when phone_digits='' then null else '+' || phone_digits end phone_number, cast(region as varchar) region,
13:  lower(trim(cast(timezone as varchar))) timezone, cast(title as varchar) title, try_cast(updated as timestamp) updated_at,
14:  try_cast(last_event_date as timestamp) last_event_date, 'klaviyo'::varchar source_relation
15: from base
16: where nullif(trim(cast(id as varchar)), '') is not null
17:  and (email is null or regexp_full_match(lower(trim(cast(email as varchar))), '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+[.][A-Za-z]{2,}'))
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/sql/staging/stg_klaviyo__person.sql`，SHA-256 `bec65364de8ef1619f1fbdba6dad2620b88542e11db613bd3f364c1f50357b12`，行 1–66。

```
1: with base as (
2:     select * from raw.person
3: ),
4: 
5: validated as (
6:     select
7:         cast(id as VARCHAR) as person_id,
8:         address_1,
9:         address_2,
10:         city,
11:         country,
12:         zip,
13:         created as created_at,
14:         email,
15:         first_name,
16:         last_name,
17:         latitude,
18:         longitude,
19:         organization,
20:         -- normalize phone number to a simple E.164-like form
21:         case
22:             when phone_number is null then null
23:             else
24:                 case
25:                     when left(regexp_replace(phone_number, '[^0-9]+', ''), 1) = '0'
26:                         then '+' || ltrim(regexp_replace(phone_number, '[^0-9]+', ''), '0')
27:                     else '+' || regexp_replace(phone_number, '[^0-9]+', '')
28:                 end
29:         end as phone_number,
30:         region,
31:         lower(trim(timezone)) as timezone,
32:         title,
33:         updated as updated_at,
34:         last_event_date,
35:         -- provide a constant source identifier for lineage
36:         'klaviyo' as source_relation
37:     from base
38:     where (email is null OR regexp_matches(lower(trim(email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'))
39: ),
40: 
41: final as (
42:     select
43:         person_id,
44:         address_1,
45:         address_2,
46:         city,
47:         country,
48:         zip,
49:         created_at,
50:         -- email length rule: nullify if too long
51:         case when email is not null and length(email) > 255 then null else lower(trim(email)) end as email,
52:         first_name || ' ' || last_name as full_name,
53:         latitude,
54:         longitude,
55:         organization,
56:         phone_number,
57:         region,
58:         timezone,
59:         title,
60:         updated_at,
61:         last_event_date,
62:         source_relation
63:     from validated
64: )
65: 
66: select * from final
```

## 轨迹可见性与不确定性

**四档：只有通用策略说明**。

event 19/20、23/24 已看见person的ID大量为空；event 41：「无效关键 ID 和非法邮件记录被排除」。未专门说明person无not_null却过滤的选择。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 19：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/19.json`。
- event 20：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/20.json`。
- event 23：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/23.json`。
- event 24：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/24.json`。
- event 41：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-021/agent/.events/sessions/0df4fe0e-334b-44-2a6f52c73a5acb3/events/41.json`。

event 41 最终报告原文（用于检查说明是否超出工作清单）：

```
【回复用户】

已根据 `docs/data_contract.yaml` 和 `config/layer_dependencies.yaml` 完成 Klaviyo SQL 数据管道，SQL 文件均放置在 `sql/staging/`、`sql/intermediate/`、`sql/marts/`，共 18 个模型文件。SQL 使用 DuckDB 语法、直接以 `schema.table` 引用上游、不含 dbt `ref()`，且文件末尾无分号。

**执行验证**
- `python run.py` 成功完成 staging → intermediate → marts 全部层级转换。
- 构建行数：staging campaign 2、event 2,500、flow 1、metric 1、person 2；intermediate event_attribution 2,500、events 2,500、person_campaign_flow 9、campaign_flow_metrics 7、person_metrics 3、campaigns_enriched 2、flows_enriched 1、persons_enriched 2；marts events 2,500、campaigns 2、flows 1、persons 2、person_campaign_flow 9。
- 检查 campaign/person/event/flow/metric staging 主键字段无空值及重复；event 的 `(source_relation, event_id)` 在 staging、intermediate 与 marts 均无空值及重复。

**数据质量处理与边界说明**
- staging 清洗邮件和 timezone 大小写、空白，标准化电话，安全转换时间/数值；无效关键 ID 和非法邮件记录被排除，超长 person email 置空，负的 price/compare-at-price 置空。
- 事件 attribution 解析按契约优先级提取 JSON 子事件 ID，查找限定同一 `source_relation`；事件重复保留且照常计数。
- 契约未指定 `source_relation` 的字面值，本实现使用固定来源键 `'klaviyo'`。电话号码按 E.164-like 格式加前缀 `+`，未推断国家码。
- 所有 SQL 文件遵循 DuckDB/直接 schema-table 引用规范。`python run.py` 成功，无失败 SQL 语句；目标数据库为 `klaviyo.duckdb`。
```

## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：ID 空值

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE id IS NULL) null_id,count(*) FILTER(WHERE trim(id)='') blank_id FROM raw.person
```


```json
{"columns":["n","null_id","blank_id"],"rows":[[1200,1198,0]]}
```


### 诊断：去除ID筛选后的 residual 姓名

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-021/klaviyo.duckdb`。

```sql
SELECT count(*) FILTER(WHERE first_name IS NULL OR last_name IS NULL) one_name_null FROM raw.person
```


```json
{"columns":["one_name_null"],"rows":[[1]]}
```


### 诊断：补充差异定位


```sql
SELECT count(*) FILTER(WHERE first_name IS NULL OR last_name IS NULL),count(*) FILTER(WHERE phone_number IS NOT NULL) FROM g.raw.person WHERE id IS NULL
```


```json
{"columns":["count_star() FILTER (WHERE ((first_name IS NULL) OR (last_name IS NULL)))","count_star() FILTER (WHERE (phone_number IS NOT NULL))"],"rows":[[0,1198]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-021_stg_klaviyo__person.json](../023_reruns_impl-021_stg_klaviyo__person.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2|1192|1190|19040|否|
|L1|2|1192|1190|19040|否|
|L2|2|1192|1190|19040|否|
|L3|2|1192|1190|19040|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L1：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L2：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L3：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-021_stg_klaviyo__person/baseline.sql`；SHA-256 `c1c19d10e6d80bd7fe487cd7564f89908c00ee7f951133962e90cb7950dfebf6`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2|1192|1190|19040|否|
|L1|2|1192|1190|19040|否|
|L2|2|1192|1190|19040|否|
|L3|2|1192|1190|19040|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L1：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L2：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L3：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`

#### null_id_filter

判定：主因；类别候选 A。前三表契约明确 ID not_null，gold 保留 NULL；person 没有非空要求，额外删除为未规定取舍。

相对本轮基线减少行 1189、格 19039；按行优先、格次之排序。
共同控制后 SQL 第 16 行起、字符 offset 1126 的唯一连续替换；其余字节不动。
替换前：
```sql
nullif(trim(cast(id as varchar)), '') is not null
```

替换后：
```sql
TRUE
```

私有 SQL：`data/023_work/impl-021_stg_klaviyo__person/null_id_filter.sql`；SHA-256 `3b984b03d2879df3195b41e415152ec1d0a3add1e79ba28c9712d0b96dbd2c00`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|1192|1192|1|1|否|
|L1|1192|1192|1|1|否|
|L2|1192|1192|1|1|否|
|L3|1192|1192|1|1|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"phone_number":1}`
- L1：`{"phone_number":1}`
- L2：`{"phone_number":1}`
- L3：`{"phone_number":1}`
### 补充轮：[023_supplement_reruns_impl-021_stg_klaviyo__person.json](../023_supplement_reruns_impl-021_stg_klaviyo__person.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-021/agent/dacomp-de-impl-021/klaviyo.duckdb`。

共同时间控制：`[]`。

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_supplement_work/impl-021_stg_klaviyo__person/baseline.sql`；SHA-256 `c1c19d10e6d80bd7fe487cd7564f89908c00ee7f951133962e90cb7950dfebf6`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2|1192|1190|19040|否|
|L1|2|1192|1190|19040|否|
|L2|2|1192|1190|19040|否|
|L3|2|1192|1190|19040|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L1：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L2：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L3：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`

#### full_name_null

判定：不计参与因素；类别候选 A。只缺一侧姓名时拼接剩余姓名还是 NULL，契约未明确。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 10 行起、字符 offset 521 的唯一连续替换；其余字节不动。
替换前：
```sql
nullif(trim(concat_ws(' ', nullif(trim(cast(first_name as varchar)), ''), nullif(trim(cast(last_name as varchar)), ''))), '') full_name
```

替换后：
```sql
first_name || ' ' || last_name full_name
```

私有 SQL：`data/023_supplement_work/impl-021_stg_klaviyo__person/full_name_null.sql`；SHA-256 `42d4e3a943a1faa3bf77191e0fe0a0171b0613e41ddbaa37908ebec107c479ca`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2|1192|1190|19040|否|
|L1|2|1192|1190|19040|否|
|L2|2|1192|1190|19040|否|
|L3|2|1192|1190|19040|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L1：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L2：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L3：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`

#### phone_normalization

判定：不计参与因素；类别候选 O。契约要求移除非数字并加+；gold还移除前导0且regexp_replace未指定全局。仅改一个phone CASE，检验其是否独立改善。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 12 行起、字符 offset 784 的唯一连续替换；其余字节不动。
替换前：
```sql
case when phone_digits='' then null else '+' || phone_digits end
```

替换后：
```sql
case when phone_number is null then null when left(regexp_replace(phone_number, '[^0-9]+', ''),1)='0' then '+' || ltrim(regexp_replace(phone_number, '[^0-9]+', ''),'0') else '+' || regexp_replace(phone_number, '[^0-9]+', '') end
```

私有 SQL：`data/023_supplement_work/impl-021_stg_klaviyo__person/phone_normalization.sql`；SHA-256 `1353362bacc41b3b5aa5b0f34dfee2145184b6c37abc1eae9654a2e8a58049e8`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2|1192|1190|19040|否|
|L1|2|1192|1190|19040|否|
|L2|2|1192|1190|19040|否|
|L3|2|1192|1190|19040|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L1：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L2：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`
- L3：`{"person_id":1190,"ADDRESS_1":1190,"ADDRESS_2":1190,"CITY":1190,"COUNTRY":1190,"email":1190,"full_name":1190,"LAST_EVENT_DATE":1190,"LATITUDE":1190,"LONGITUDE":1190,"ORGANIZATION":1190,"phone_number":1190,"REGION":1190,"timezone":1190,"TITLE":1190,"ZIP":1190}`

## 规则问题

无
