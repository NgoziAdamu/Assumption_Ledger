# impl-024 · stg_tiktok_ads__advertiser

用途：**校准**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**A**；把握：中；主要错误点：email_pattern。

契约只给 email matches standard pattern (local@domain.tld)，未给可执行正则。agent 和 gold 对 adv12@sub..example.com 的接受边界不同。只改 email CASE 一处后，行/格规模 1/1→0/0，L0 全匹配。原始数据不能决定契约所指正则的具体字符集合。

参与因素：无。

标记：无。

盲标冻结文件023_calibration_blind_decisions.json；018仅在锁定后读取比较。

## 材料与比较口径

精简材料包：[013_impl-024_staging_stg_tiktok_ads__advertiser.md](../013_packages/013_impl-024_staging_stg_tiktok_ads__advertiser.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-024/docs/data_contract.yaml`；SHA-256 `b43ee99b585f76719b935a1234dd0fbdd2fb975d72c8e2c5b393421e1b1fa8cb`。
契约行 40–94：

```
40:     - name: stg_tiktok_ads__advertiser
41:       description: "Cleaned advertiser master data with normalized contact fields and type-safe numeric conversions."
42:       source_table: raw.tiktok_advertiser_data
43:       columns:
44:         - name: source_relation
45:           data_type: VARCHAR
46:         - name: advertiser_id
47:           data_type: VARCHAR
48:         - name: address
49:           data_type: VARCHAR
50:         - name: balance
51:           data_type: DOUBLE
52:           validation_rules:
53:             - rule: "balance is numeric"
54:               on_failure: nullify_field
55:         - name: company
56:           data_type: VARCHAR
57:         - name: contacter
58:           data_type: VARCHAR
59:         - name: country
60:           data_type: VARCHAR
61:         - name: currency
62:           data_type: VARCHAR
63:         - name: description
64:           data_type: VARCHAR
65:         - name: email
66:           data_type: VARCHAR
67:           validation_rules:
68:             - rule: "email normalized to lowercase and trimmed"
69:               on_failure: correct
70:             - rule: "email matches standard pattern (local@domain.tld)"
71:               on_failure: nullify_field
72:         - name: industry
73:           data_type: VARCHAR
74:         - name: language
75:           data_type: VARCHAR
76:         - name: advertiser_name
77:           data_type: VARCHAR
78:           validation_rules:
79:             - rule: "name trimmed"
80:               on_failure: correct
81:             - rule: "name length between 3 and 100 and only alphanumeric plus spaces"
82:               on_failure: nullify_field
83:         - name: cellphone_number
84:           data_type: VARCHAR
85:           validation_rules:
86:             - rule: "strip non-digit characters except leading '+'"
87:               on_failure: correct
88:             - rule: "must conform to E.164 format"
89:               on_failure: nullify_field
90:         - name: telephone_number
91:           data_type: VARCHAR
92:         - name: timezone
93:           data_type: VARCHAR
94:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/sql/staging/stg_tiktok_ads__advertiser.sql`，SHA-256 `0fc81c8ecdcac4c1812c6b6a33de9a1866d1187c37c3a49fad45415833f00df0`，行 1–21。

```
1: with source_data as (
2:     select * from raw.tiktok_advertiser_data
3: )
4: select
5:         'tiktok_ads' as source_relation,
6:         cast("ID" as VARCHAR) as advertiser_id,
7:         cast("ADDRESS" as VARCHAR) as address,
8:         try_cast(nullif(trim("BALANCE"), '') as DOUBLE) as balance,
9:         cast("COMPANY" as VARCHAR) as company,
10:         cast("CONTACTER" as VARCHAR) as contacter,
11:         cast("COUNTRY" as VARCHAR) as country,
12:         cast("CURRENCY" as VARCHAR) as currency,
13:         cast("DESCRIPTION" as VARCHAR) as description,
14:         case when regexp_matches(lower(trim("EMAIL")), '^[a-z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$') then lower(trim("EMAIL")) else null end as email,
15:         cast("INDUSTRY" as VARCHAR) as industry,
16:         cast("LANGUAGE" as VARCHAR) as language,
17:         case when length(trim("NAME")) between 3 and 100 and regexp_matches(trim("NAME"), '^[A-Za-z0-9 ]+$') then trim("NAME") else null end as advertiser_name,
18:         case when regexp_matches(regexp_replace(trim("CELLPHONE_NUMBER"), '[^0-9+]', '', 'g'), '^\+[1-9][0-9]{7,14}$') then regexp_replace(trim("CELLPHONE_NUMBER"), '[^0-9+]', '', 'g') else null end as cellphone_number,
19:         cast("TELEPHONE_NUMBER" as VARCHAR) as telephone_number,
20:         cast("TIMEZONE" as VARCHAR) as timezone
21: from source_data
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/sql/staging/stg_tiktok_ads__advertiser.sql`，SHA-256 `b0479a70e4db457fa26b3cbc9c993c1eed2a953d2b3a2fd06432516884c1e358`，行 1–73。

```
1: with raw_adv as (
2:   select
3:     'raw.tiktok_advertiser_data' as source_relation,
4:     "ID" as advertiser_id,
5:     "ADDRESS" as address,
6:     "BALANCE" as balance,
7:     "COMPANY" as company,
8:     "CONTACTER" as contacter,
9:     "COUNTRY" as country,
10:     "CURRENCY" as currency,
11:     "DESCRIPTION" as description,
12:     "EMAIL" as email,
13:     "INDUSTRY" as industry,
14:     "LANGUAGE" as language,
15:     "NAME" as name,
16:     "CELLPHONE_NUMBER" as cellphone_number,
17:     "TELEPHONE_NUMBER" as telephone_number,
18:     "TIMEZONE" as timezone
19:   from raw.tiktok_advertiser_data
20: ), cleaned as (
21:   select
22:     source_relation,
23:     advertiser_id,
24:     address,
25:     try_cast(balance as double) as balance,
26:     company,
27:     contacter,
28:     country,
29:     currency,
30:     description,
31:     -- email normalization and validation
32:     case
33:       when regexp_full_match(lower(trim(email)), '^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$') then lower(trim(email))
34:       else null
35:     end as email,
36:     industry,
37:     language,
38:     -- name cleaning and validation
39:     case
40:       when name is null then null
41:       when length(trim(name)) between 3 and 100 and regexp_full_match(trim(name), '^[A-Za-z0-9 ]+$') then trim(name)
42:       else null
43:     end as advertiser_name,
44:     -- cellphone cleaning and validation (E.164)
45:     case
46:       when "CELLPHONE_NUMBER" is not null then regexp_replace("CELLPHONE_NUMBER", '[^0-9+]', '')
47:       else null
48:     end as cellphone_number_raw,
49:     telephone_number as telephone_number_raw,
50:     timezone
51:   from raw_adv
52: ), final as (
53:   select
54:     source_relation,
55:     advertiser_id,
56:     address,
57:     balance,
58:     company,
59:     contacter,
60:     country,
61:     currency,
62:     description,
63:     email,
64:     industry,
65:     language,
66:     advertiser_name,
67:     case when cellphone_number_raw is not null and regexp_full_match(cellphone_number_raw, '^\+[1-9][0-9]{7,14}$') then cellphone_number_raw else null end as cellphone_number,
68:     telephone_number_raw as telephone_number,
69:     timezone
70:   from cleaned
71: )
72: select *
73: from final
```

## 轨迹可见性与不确定性

**四档：只有通用策略说明**。

event 61/63：可选邮箱/名称/手机号字段验证失败时置 NULL，记录仍保留。这是跨字段的失败处理策略，未说明连续点域名边界。实施内容中的清理 advertiser 邮箱工作清单不计入。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 61：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/61.json`。
- event 63：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/63.json`。

event 63 最终报告原文（用于检查说明是否超出工作清单）：

```
【回复用户】

已按 staging → intermediate → marts 顺序实现 SQL，文件均位于要求的 `sql/<layer>/<model_name>.sql` 路径下，共 22 个模型文件。

### 实施内容
- **Staging（8 张表）**：按契约投影字段并进行安全类型转换；数值指标按约定缺失时默认 0；清理 advertiser 邮箱、名称及手机号；生成 URL/UTM 字段；通过 `updated_at` 为历史数据标记最新记录。
- **Intermediate（8 个模型）**：按契约实现字段直通和最新记录筛选，来源仅引用 staging。
- **Marts（6 个模型）**：实现小时指标按日汇总、维度左连接、conversion value 汇总及零安全的 CPC/CPM/CTR 计算。来源仅引用 intermediate。

### 验证结果
- 执行 `python run.py` 成功，最终日志显示 staging `8/8`、intermediate `8/8`、marts `6/6` 模型创建成功。
- 各模型行数与源记录规模相符；ad report、campaign-country report 的分组主键未检测到重复。
- 最新 campaign 标记检查无异常；ad report 和 campaign-country report 的契约必填字段无 NULL；advertiser report 核心指标未发现负数。
- 检查确认 SQL 文件无文件末尾分号，也未使用 dbt `ref()`。

### 数据质量处理与残余影响
- 数值与日期采用 DuckDB `try_cast`，不可解析值置 NULL；报表数值列按 staging 合约对转换后的 NULL 默认 0。可选邮箱/名称/手机号字段验证失败时置 NULL，记录仍保留。
- 历史模型按 source relation 和实体 ID 标记最大更新时间；并列最大时间可能保留多行，符合契约保留重复记录的行为。
- 中间层与模型合约要求保留重复和 NULL，因此未做去重；原始重复可能继续影响下游汇总，属于配置明确要求的保留行为。

### 合约歧义及环境说明
- `stg_tiktok_ads__campaign_history.is_new_structure` 声明为 BOOLEAN，而 intermediate 列定义为 VARCHAR；intermediate 同时要求不转换、逐值透传。本实现遵守透传要求，因此输出保留 staging 的 BOOLEAN 类型。
- 运行环境根目录挂载为只读，无法创建 `/workspace/result.md`；报告已写入项目目录 `result.md`，内容与此提交一致。
```

## 查询

核实查询 **1** 条；核实代价档：**一条查询**。诊断查询不计入 5 条上限。

### 核实：email 边界样例

只读数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/tiktok_ads.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE EMAIL LIKE '%..%') consecutive_dot_emails FROM raw.tiktok_advertiser_data
```


```json
{"columns":["n","consecutive_dot_emails"],"rows":[[200,1]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-024_stg_tiktok_ads__advertiser.json](../023_reruns_impl-024_stg_tiktok_ads__advertiser.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/tiktok_ads.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|200|200|1|1|否|
|L1|200|200|1|1|否|
|L2|200|200|1|1|否|
|L3|200|200|1|1|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"email":1}`
- L1：`{"email":1}`
- L2：`{"email":1}`
- L3：`{"email":1}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-024_stg_tiktok_ads__advertiser/baseline.sql`；SHA-256 `0fc81c8ecdcac4c1812c6b6a33de9a1866d1187c37c3a49fad45415833f00df0`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|200|200|1|1|否|
|L1|200|200|1|1|否|
|L2|200|200|1|1|否|
|L3|200|200|1|1|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"email":1}`
- L1：`{"email":1}`
- L2：`{"email":1}`
- L3：`{"email":1}`

#### email_pattern

判定：主因；类别候选 A。见盲标记录

相对本轮基线减少行 1、格 1；按行优先、格次之排序。
共同控制后 SQL 第 14 行起、字符 offset 537 的唯一连续替换；其余字节不动。
替换前：
```sql
case when regexp_matches(lower(trim("EMAIL")), '^[a-z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$') then lower(trim("EMAIL")) else null end
```

替换后：
```sql
case when regexp_full_match(lower(trim("EMAIL")), '^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$') then lower(trim("EMAIL")) else null end
```

私有 SQL：`data/023_work/impl-024_stg_tiktok_ads__advertiser/email_pattern.sql`；SHA-256 `7ba3fd5c6d86b9e6298f3fb948aca38864ae652b7fe8c70f14e885a813d2d68f`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|200|200|0|0|是|
|L1|200|200|0|0|是|
|L2|200|200|0|0|是|
|L3|200|200|0|0|是|

整表首次匹配档位：L0。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{}`
- L1：`{}`
- L2：`{}`
- L3：`{}`

## 规则问题

A/O 边界：可将连续点域名理解为违反 standard pattern 而归 O，也可将未给具体正则视为 A。本次选 A，因为契约只有自然语言模板，未定义边界且数据不能决定接受集合；不以 gold 的正则为规范。

## 冻结后校准比较

先盲标并写入 [023_calibration_blind_decisions.json](../023_calibration_blind_decisions.json)，SHA-256 锁定于 [023_blind_lock.json](../023_blind_lock.json)，随后才读取 018。

与 018 的主因类别、参与因素、不确定性四档均一致。核实查询数量/代价档、把握可能不同，逐字段记录见 [023_calibration_comparison.json](../023_calibration_comparison.json)。
