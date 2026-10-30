# impl-018 · stg_salesforce__user

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**O**；把握：高；主要错误点：email_filter。

agent 执行契约显式删除规则，gold 保留违反规则的记录。

参与因素：O：email_length（行减少1，格减少27）。

标记：无。

user 长邮箱删除另有单独O因素；email NULL 与regex/length过滤相互遮蔽，单放开not_null不减少规模，不列因素。

## 材料与比较口径

精简材料包：[023_impl-018_stg_salesforce__user.md](../023_packages/023_impl-018_stg_salesforce__user.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
契约行 406–481：

```
406:     - name: stg_salesforce__user
407:       description: "Cleaned user/employee records with validated authentication and profile information"
408:       source_table: raw.user
409:       columns:
410:         - name: account_id
411:           data_type: VARCHAR
412:         - name: alias
413:           data_type: VARCHAR
414:         - name: city
415:           data_type: VARCHAR
416:         - name: company_name
417:           data_type: VARCHAR
418:         - name: contact_id
419:           data_type: VARCHAR
420:         - name: country
421:           data_type: VARCHAR
422:         - name: country_code
423:           data_type: VARCHAR
424:         - name: department
425:           data_type: VARCHAR
426:         - name: email
427:           data_type: VARCHAR
428:           constraints: [not_null]
429:           validation_rules:
430:             - rule: "email IS NOT NULL"
431:               on_failure: delete_row
432:             - rule: "email = LOWER(TRIM(email))"
433:               on_failure: correct
434:             - rule: "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
435:               on_failure: delete_row
436:             - rule: "LENGTH(email) <= 255"
437:               on_failure: delete_row
438:         - name: first_name
439:           data_type: VARCHAR
440:         - name: user_id
441:           data_type: VARCHAR
442:           constraints: [not_null, unique]
443:         - name: individual_id
444:           data_type: VARCHAR
445:         - name: is_active
446:           data_type: BOOLEAN
447:           constraints: [not_null]
448:         - name: last_login_date
449:           data_type: TIMESTAMP
450:         - name: last_name
451:           data_type: VARCHAR
452:           constraints: [not_null]
453:         - name: last_referenced_date
454:           data_type: TIMESTAMP
455:         - name: last_viewed_date
456:           data_type: TIMESTAMP
457:         - name: manager_id
458:           data_type: VARCHAR
459:         - name: user_name
460:           data_type: VARCHAR
461:           constraints: [not_null]
462:         - name: postal_code
463:           data_type: VARCHAR
464:         - name: profile_id
465:           data_type: VARCHAR
466:         - name: state
467:           data_type: VARCHAR
468:         - name: state_code
469:           data_type: VARCHAR
470:         - name: street
471:           data_type: VARCHAR
472:         - name: title
473:           data_type: VARCHAR
474:         - name: user_role_id
475:           data_type: VARCHAR
476:         - name: user_type
477:           data_type: VARCHAR
478:         - name: username
479:           data_type: VARCHAR
480:           constraints: [not_null, unique]
481:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__user.sql`，SHA-256 `cca4c7cf2ff74050466df829d496915608f94ccafcc2b33b9672a760c9b82cc7`，行 1–39。

```
1: select
2:       account_id as account_id,
3:       alias as alias,
4:       city as city,
5:       company_name as company_name,
6:       contact_id as contact_id,
7:       country as country,
8:       country_code as country_code,
9:       department as department,
10:       lower(trim(email)) as email,
11:       first_name as first_name,
12:       id as user_id,
13:       individual_id as individual_id,
14:       is_active as is_active,
15:       try_cast(last_login_date as TIMESTAMP) as last_login_date,
16:       last_name as last_name,
17:       try_cast(last_referenced_date as TIMESTAMP) as last_referenced_date,
18:       try_cast(last_viewed_date as TIMESTAMP) as last_viewed_date,
19:       manager_id as manager_id,
20:       name as user_name,
21:       postal_code as postal_code,
22:       profile_id as profile_id,
23:       state as state,
24:       state_code as state_code,
25:       street as street,
26:       title as title,
27:       user_role_id as user_role_id,
28:       user_type as user_type,
29:       username as username
30: from raw.user
31: where id is not null
32:   and email is not null
33:   and regexp_matches(lower(trim(email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
34:   and length(lower(trim(email))) <= 255
35:   and is_active is not null
36:   and last_name is not null
37:   and name is not null
38:   and username is not null
39: qualify row_number() over (partition by id order by id) = 1
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__user.sql`，SHA-256 `95fb00802b56720423d0dd8a645663e8ecb6d88e4abccd41e123a7f2b473f6c0`，行 1–68。

```
1: with fields as (
2:     select
3:         account_id,
4:         alias,
5:         city,
6:         company_name,
7:         contact_id,
8:         country,
9:         country_code,
10:         department,
11:         email,
12:         first_name,
13:         id,
14:         individual_id,
15:         is_active,
16:         last_login_date,
17:         last_name,
18:         last_referenced_date,
19:         last_viewed_date,
20:         manager_id,
21:         name,
22:         postal_code,
23:         profile_id,
24:         state,
25:         state_code,
26:         street,
27:         title,
28:         user_role_id,
29:         user_type,
30:         username
31:     from raw."user"
32: ), 
33: 
34: final as (
35:     select 
36:         cast(account_id as varchar) as account_id,
37:         cast(alias as varchar) as alias,
38:         cast(city as varchar) as city,
39:         cast(company_name as varchar) as company_name,
40:         cast(contact_id as varchar) as contact_id,
41:         cast(country as varchar) as country,
42:         cast(country_code as varchar) as country_code,
43:         cast(department as varchar) as department,
44:         cast(email as varchar) as email,
45:         cast(first_name as varchar) as first_name,
46:         cast(id as varchar) as user_id,
47:         cast(individual_id as varchar) as individual_id,
48:         cast(coalesce(is_active, false) as boolean) as is_active,
49:         cast(last_login_date as timestamp) as last_login_date,
50:         cast(last_name as varchar) as last_name,
51:         cast(last_referenced_date as timestamp) as last_referenced_date,
52:         cast(last_viewed_date as timestamp) as last_viewed_date,
53:         cast(manager_id as varchar) as manager_id,
54:         cast(name as varchar) as user_name,
55:         cast(postal_code as varchar) as postal_code,
56:         cast(profile_id as varchar) as profile_id,
57:         cast(state as varchar) as state,
58:         cast(state_code as varchar) as state_code,
59:         cast(street as varchar) as street,
60:         cast(title as varchar) as title,
61:         cast(user_role_id as varchar) as user_role_id,
62:         cast(user_type as varchar) as user_type,
63:         cast(username as varchar) as username
64:     from fields
65: )
66: 
67: select * 
68: from final
```

## 轨迹可见性与不确定性

**四档：只有通用策略说明**。

event 1 提供校验表达式；event 17/18 查看raw；event 99：「严重问题按契约删除行或过滤软删除数据；非关键字段中的无效关系键、格式值或数值按契约置空」。这是实际条件处理策略，不取实施清单。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 1：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json`。
- event 17：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/17.json`。
- event 18：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/18.json`。
- event 99：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json`。

event 99 最终报告原文（用于检查说明是否超出工作清单）：

```
【回复用户】

已依据 `docs/data_contract.yaml` 与 `config/layer_dependencies.yaml` 完成 Salesforce SQL pipeline，文件写入 `sql/staging/`、`sql/intermediate/` 和 `sql/marts/`，命名与配置模型一致。

### 实施内容
- 实现全部 14 个 staging 表：按字段配置选择来源、重命名与类型转换，并落实适用的数据质量处理，例如删除无效/软删除记录、修正名称或状态空格、规范邮件、将无效可选字段置空及去除重复主键。
- 实现全部 7 个 intermediate 模型：覆盖账户增强、机会管道、活动摘要、线索转化、日期维度、用户绩效和 owner 级机会汇总。
- 实现全部 16 个 marts 模型：涵盖机会/线索事实表、账户 engagement、用户维度、owner/manager/team 绩效、日常活动、snapshot、history 及增强模型。
- SQL 使用 DuckDB 语法和显式 `schema.table` 引用；无 dbt `ref()`，SQL 文件末尾均无分号。

### 验证结果
- `python run.py` 成功完成：staging 14/14、intermediate 7/7、marts 16/16，无失败模型。
- 校验了模型输出字段与契约字段集合一致，以及指定业务键的非空/唯一性；核心账户、联系人、机会、用户、线索和活动表的键检查通过。数据质量过滤后示例行数：账户 2,999、用户 993、线索 2,996、任务 2,998。
- 所有 37 个 SQL 文件均已检查无结尾分号。

### 数据质量处理及边界说明
- 严重问题按契约删除行或过滤软删除数据；非关键字段中的无效关系键、格式值或数值按契约置空；规范化处理保留可用记录。
- History 源数据没有契约所需的 `history_unique_key` 原始列，因此以实体记录 ID 与 Fivetran 起止时间生成确定性 MD5 键，用于稳定标识历史版本。精确重复输入仍会被视作同一历史键；源记录缺乏更细粒度的版本标识时，此类重复的区分能力有限。
- 原始 contact 缺少 `created_date`，opportunity history 缺少 `last_modified_date`；对应 staging 字段按目标类型输出 NULL，没有从不等价字段推断值。
- 日期依赖 `current_date` / `current_timestamp`，因此时间衍生值会随执行日期变化；活动摘要中的固定占位指标按契约保留。

### 排错记录
首次执行遇到的 SQL binder 错误由同一 SELECT 中引用尚未生成的计算字段所致，已改为直接由原始字段计算；后续因上游模型未创建而产生的依赖错误随之消除。最终全链路重跑成功，无未解决的 SQL 错误。
```

## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：各过滤条件

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

```sql
SELECT count(*) FILTER(WHERE email IS NULL) null_email,count(*) FILTER(WHERE NOT regexp_matches(lower(trim(email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')) invalid_email,count(*) FILTER(WHERE length(email)>255) long_email,count(*) FILTER(WHERE is_active IS NULL) null_active,count(*) FILTER(WHERE last_name IS NULL) null_last_name,count(*) FILTER(WHERE name IS NULL) null_name,count(*) FILTER(WHERE username IS NULL) null_username FROM raw.user
```


```json
{"columns":["null_email","invalid_email","long_email","null_active","null_last_name","null_name","null_username"],"rows":[[1,5,1,0,0,0,0]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-018_stg_salesforce__user.json](../023_reruns_impl-018_stg_salesforce__user.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|993|1000|7|189|否|
|L1|993|1000|7|189|否|
|L2|993|1000|7|189|否|
|L3|993|1000|7|189|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`
- L1：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`
- L2：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`
- L3：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-018_stg_salesforce__user/baseline.sql`；SHA-256 `cca4c7cf2ff74050466df829d496915608f94ccafcc2b33b9672a760c9b82cc7`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|993|1000|7|189|否|
|L1|993|1000|7|189|否|
|L2|993|1000|7|189|否|
|L3|993|1000|7|189|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`
- L1：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`
- L2：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`
- L3：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`

#### email_filter

判定：主因；类别候选 O。契约 email 正则校验删除，gold 未执行。

相对本轮基线减少行 5、格 135；按行优先、格次之排序。
共同控制后 SQL 第 33 行起、字符 offset 1013 的唯一连续替换；其余字节不动。
替换前：
```sql
and regexp_matches(lower(trim(email)), '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
```

替换后：
```sql
and TRUE
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__user/email_filter.sql`；SHA-256 `be1fd1788fa11bfbc1309df0b49885c82ef8a312274dbef99edc4ed852706c28`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|998|1000|2|54|否|
|L1|998|1000|2|54|否|
|L2|998|1000|2|54|否|
|L3|998|1000|2|54|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"user_id":2,"account_id":2,"alias":2,"city":2,"company_name":2,"contact_id":2,"country":2,"country_code":2,"department":2,"email":2,"first_name":2,"individual_id":2,"is_active":2,"last_login_date":2,"last_name":2,"last_referenced_date":2,"last_viewed_date":2,"manager_id":2,"postal_code":2,"profile_id":2,"state":2,"state_code":2,"street":2,"title":2,"user_role_id":2,"user_type":2,"username":2}`
- L1：`{"user_id":2,"account_id":2,"alias":2,"city":2,"company_name":2,"contact_id":2,"country":2,"country_code":2,"department":2,"email":2,"first_name":2,"individual_id":2,"is_active":2,"last_login_date":2,"last_name":2,"last_referenced_date":2,"last_viewed_date":2,"manager_id":2,"postal_code":2,"profile_id":2,"state":2,"state_code":2,"street":2,"title":2,"user_role_id":2,"user_type":2,"username":2}`
- L2：`{"user_id":2,"account_id":2,"alias":2,"city":2,"company_name":2,"contact_id":2,"country":2,"country_code":2,"department":2,"email":2,"first_name":2,"individual_id":2,"is_active":2,"last_login_date":2,"last_name":2,"last_referenced_date":2,"last_viewed_date":2,"manager_id":2,"postal_code":2,"profile_id":2,"state":2,"state_code":2,"street":2,"title":2,"user_role_id":2,"user_type":2,"username":2}`
- L3：`{"user_id":2,"account_id":2,"alias":2,"city":2,"company_name":2,"contact_id":2,"country":2,"country_code":2,"department":2,"email":2,"first_name":2,"individual_id":2,"is_active":2,"last_login_date":2,"last_name":2,"last_referenced_date":2,"last_viewed_date":2,"manager_id":2,"postal_code":2,"profile_id":2,"state":2,"state_code":2,"street":2,"title":2,"user_role_id":2,"user_type":2,"username":2}`
### 补充轮：[023_supplement_reruns_impl-018_stg_salesforce__user.json](../023_supplement_reruns_impl-018_stg_salesforce__user.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

共同时间控制：`[]`。

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_supplement_work/impl-018_stg_salesforce__user/baseline.sql`；SHA-256 `cca4c7cf2ff74050466df829d496915608f94ccafcc2b33b9672a760c9b82cc7`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|993|1000|7|189|否|
|L1|993|1000|7|189|否|
|L2|993|1000|7|189|否|
|L3|993|1000|7|189|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`
- L1：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`
- L2：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`
- L3：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`

#### email_not_null

判定：不计参与因素；类别候选 O。契约 email not_null；gold 保留空 email。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 32 行起、字符 offset 989 的唯一连续替换；其余字节不动。
替换前：
```sql
and email is not null
```

替换后：
```sql
and TRUE
```

私有 SQL：`data/023_supplement_work/impl-018_stg_salesforce__user/email_not_null.sql`；SHA-256 `c664be462eb41d0d86672786314e72d01ea03bbd69eb285a55049e14d455126a`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|993|1000|7|189|否|
|L1|993|1000|7|189|否|
|L2|993|1000|7|189|否|
|L3|993|1000|7|189|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`
- L1：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`
- L2：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`
- L3：`{"user_id":7,"account_id":7,"alias":7,"city":7,"company_name":7,"contact_id":7,"country":7,"country_code":7,"department":7,"email":7,"first_name":7,"individual_id":7,"is_active":7,"last_login_date":7,"last_name":7,"last_referenced_date":7,"last_viewed_date":7,"manager_id":7,"postal_code":7,"profile_id":7,"state":7,"state_code":7,"street":7,"title":7,"user_role_id":7,"user_type":7,"username":7}`

#### email_length

判定：参与因素；类别候选 O。契约明确长邮箱删除，gold 保留。

相对本轮基线减少行 1、格 27；按行优先、格次之排序。
共同控制后 SQL 第 34 行起、字符 offset 1106 的唯一连续替换；其余字节不动。
替换前：
```sql
and length(lower(trim(email))) <= 255
```

替换后：
```sql
and TRUE
```

私有 SQL：`data/023_supplement_work/impl-018_stg_salesforce__user/email_length.sql`；SHA-256 `291c75bab89314099651d592d8e07bd27d60d41d4cc1e824783e504c7cbb979b`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|994|1000|6|162|否|
|L1|994|1000|6|162|否|
|L2|994|1000|6|162|否|
|L3|994|1000|6|162|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"user_id":6,"account_id":6,"alias":6,"city":6,"company_name":6,"contact_id":6,"country":6,"country_code":6,"department":6,"email":6,"first_name":6,"individual_id":6,"is_active":6,"last_login_date":6,"last_name":6,"last_referenced_date":6,"last_viewed_date":6,"manager_id":6,"postal_code":6,"profile_id":6,"state":6,"state_code":6,"street":6,"title":6,"user_role_id":6,"user_type":6,"username":6}`
- L1：`{"user_id":6,"account_id":6,"alias":6,"city":6,"company_name":6,"contact_id":6,"country":6,"country_code":6,"department":6,"email":6,"first_name":6,"individual_id":6,"is_active":6,"last_login_date":6,"last_name":6,"last_referenced_date":6,"last_viewed_date":6,"manager_id":6,"postal_code":6,"profile_id":6,"state":6,"state_code":6,"street":6,"title":6,"user_role_id":6,"user_type":6,"username":6}`
- L2：`{"user_id":6,"account_id":6,"alias":6,"city":6,"company_name":6,"contact_id":6,"country":6,"country_code":6,"department":6,"email":6,"first_name":6,"individual_id":6,"is_active":6,"last_login_date":6,"last_name":6,"last_referenced_date":6,"last_viewed_date":6,"manager_id":6,"postal_code":6,"profile_id":6,"state":6,"state_code":6,"street":6,"title":6,"user_role_id":6,"user_type":6,"username":6}`
- L3：`{"user_id":6,"account_id":6,"alias":6,"city":6,"company_name":6,"contact_id":6,"country":6,"country_code":6,"department":6,"email":6,"first_name":6,"individual_id":6,"is_active":6,"last_login_date":6,"last_name":6,"last_referenced_date":6,"last_viewed_date":6,"manager_id":6,"postal_code":6,"profile_id":6,"state":6,"state_code":6,"street":6,"title":6,"user_role_id":6,"user_type":6,"username":6}`

## 规则问题

无
