# impl-024 / stg_tiktok_ads__advertiser

## 1. 错在哪里

email正则的域名接受范围不同：agent把adv12@sub..example.com置NULL，gold保留。

已核实：200行仅ID12的email不同。agent模式要求各域名段非空，gold的[a-z0-9.-]+接受连续点；017-V1对同一可见值分别返回false/true。只替换这一处模式便L0匹配。契约写standard pattern (local@domain.tld)，没有给出可执行的完整模式或边界例子；本次把正则边界未指定归A，中把握，不把agent拒绝该值说成未发现异常。

## 2. 依据

- 起点：[013精简材料包](../013_packages/013_impl-024_staging_stg_tiktok_ads__advertiser.md)；不修改既有官方判错状态。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-024/docs/data_contract.yaml` 第40–94行。
- [完整轨迹](../017_trace_impl-024.json)，保留事件原文和原始路径；可回查授权归档`traces/dacomp_deimpl_prev.tar.gz`。
- [查询原文及结果](../017_queries_impl-024.json)、[重跑完整记录](../017_reruns_impl-024.json)、[原始表库存](../015_raw_impl-024.json)。
- [新增不确定性字段审计](../017_uncertainty_audit.json)、[本表依赖raw核对](../017_dependency_raw_audit.json)。
- [执行前指纹](../017_input_before.json)、[结束后指纹](../017_input_after.json)。本次前快照完成后才开始标注、查询和重跑。

### 契约原文

```yaml
    - name: stg_tiktok_ads__advertiser
      description: "Cleaned advertiser master data with normalized contact fields and type-safe numeric conversions."
      source_table: raw.tiktok_advertiser_data
      columns:
        - name: source_relation
          data_type: VARCHAR
        - name: advertiser_id
          data_type: VARCHAR
        - name: address
          data_type: VARCHAR
        - name: balance
          data_type: DOUBLE
          validation_rules:
            - rule: "balance is numeric"
              on_failure: nullify_field
        - name: company
          data_type: VARCHAR
        - name: contacter
          data_type: VARCHAR
        - name: country
          data_type: VARCHAR
        - name: currency
          data_type: VARCHAR
        - name: description
          data_type: VARCHAR
        - name: email
          data_type: VARCHAR
          validation_rules:
            - rule: "email normalized to lowercase and trimmed"
              on_failure: correct
            - rule: "email matches standard pattern (local@domain.tld)"
              on_failure: nullify_field
        - name: industry
          data_type: VARCHAR
        - name: language
          data_type: VARCHAR
        - name: advertiser_name
          data_type: VARCHAR
          validation_rules:
            - rule: "name trimmed"
              on_failure: correct
            - rule: "name length between 3 and 100 and only alphanumeric plus spaces"
              on_failure: nullify_field
        - name: cellphone_number
          data_type: VARCHAR
          validation_rules:
            - rule: "strip non-digit characters except leading '+'"
              on_failure: correct
            - rule: "must conform to E.164 format"
              on_failure: nullify_field
        - name: telephone_number
          data_type: VARCHAR
        - name: timezone
          data_type: VARCHAR
```

### SQL定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/sql/staging/stg_tiktok_ads__advertiser.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
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

gold（仅用于定位差异）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-024/sql/staging/stg_tiktok_ads__advertiser.sql`；下列为行号视图（显示时去除行尾空白，补丁原文在JSON中逐字保留）。
```sql
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

### 原始数据可评估性

下表复用015的完整表schema/行数/typed行哈希比较，只列本表静态传递依赖及双方SQL直接引用的raw。缺表不当作空表；gold与agent一致但二者不同于初始不自动排除（021/030）。

|依赖raw|比较|类型/列序相同|行数相同|typed行哈希相同|差异原因|
|---|---|---|---|---|---|
|raw.tiktok_advertiser_data|gold_vs_initial|True|True|True||
|raw.tiktok_advertiser_data|gold_vs_agent|True|True|True||

## 3. agent看过什么

event15→16看EMAIL列及前2行fake-email样例，不能据此说看过ID12；event23写正则，event31→32看到生成SQL；event49→50查到189/200 email非NULL。event63只泛述可选邮箱校验失败置NULL，没有点名连续点域名或两种正则边界。

只把归档实际展示的内容视为已看到；磁盘有文件、命令包含表名或截断掉的部分，不等于看到相应数据值。

### 新增字段：是否意识到或提到相关不确定性

**看到了但没提**。只记录可见表述/信息，不由该档位推定错误类别。

event63提到可选邮箱校验失败置NULL，但未明确两种正则接受集合的选择，也未提到双点域名。普通“做过校验”不足以证明提到本表差异的边界。

event **16**，字段`content`；原路径`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/16.json`。
```text
tiktok_advertiser_data [('ID', VARCHAR, None, None, None, None, None), ('NAME', VARCHAR, None, None, None, None, None), ('ADDRESS', VARCHAR, None, None, None, None, None), ('COMPANY', VARCHAR, None, None, None, None, None), ('CONTACTER', VARCHAR, None, None, None, None, None), ('COUNTRY', VARCHAR, None, None, None, None, None), ('CURRENCY', VARCHAR, None, None, None, None, None), ('DESCRIPTION', VARCHAR, None, None, None, None, None), ('EMAIL', VARCHAR, None, None, None, None, None), ('INDUSTRY', VARCHAR, None, None, None, None, None), ('LICENSE_NO', VARCHAR, None, None, None, None, None), ('LICENSE_URL', VARCHAR, None, None, None, None, None), ('PROMOTION_AREA', VARCHAR, None, None, None, None, None), ('REJECTED_REASON', VARCHAR, None, None, None, None, None), ('ROLE', VARCHAR, None, None, None, None, None), ('STATUS', VARCHAR, None, None, None, None, None), ('TELEPHONE_NUMBER', VARCHAR, None, None, None, None, None), ('TIMEZONE', VARCHAR, None, None, None, None, None), ('BALANCE', VARCHAR, None, None, None, None, None), ('CREATE_TIME', VARCHAR, None, None, None, None, None), ('LANGUAGE', VARCHAR, None, None, None, None, None), ('CELLPHONE_NUMBER', VARCHAR, None, None, None, None, None), ('_FIVETRAN_SYNCED', VARCHAR, None, None, None, None, None)]
[('1', 'US', '222 address', 'Comany X', None, 'US', 'USD', 'hello', 'fake-email', '123', None, None, '111', None, 'ROLE_ADVERTISER', 'STATUS_ENABLE', '111-222-3333', 'Etc/GMT+5', '32.12', '2021-08-27 18:13:41.000', 'en', '001-002-0003', '2021-09-15 15:53:18.938'), ('2', 'Canada', '111 address', 'Company Y', None, 'CAN', 'CAN', 'world', 'fake-email', '321', None, None, '0', None, 'ROLE_ADVERTISER', 'STATUS_ENABLE', '222-333-4444', 'Etc/GMT+5', '321.22', '2021-03-09 20:55:37.000', 'en', '001-003-0004', '2021-09-15 15:53:07.6213')]

 tiktok_ad_history_data [('AD_ID,UPDATED_AT,ADVERTISER_ID,ADGROUP_ID,CAMPAIGN_ID,CREATE_TIME,AD
```

event **50**，字段`content`；原路径`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/50.json`。
```text
staging advertiser email valid/non-null: (189, 200)
files with trailing semicolon: []

```

归档逐项扫描65个事件；本批thought/args.thought字段均为空，不能由此推断agent没有内部思考。“已提到”的原句来自final_thought中的最终报告；“看到了但没提”依据可见工具返回，不把SQL代码本身当口头说明。长工具输出仅摘录连续原文，截取范围见JSON；不是说agent只看到了这个摘录。

## 4. 查询与重跑

核实查询执行 **1条**（失败尝试也计入）；核实代价档：**需要查业务说明**。每张≤5条，均只查agent当时可见数据。诊断可以查gold，不计入此数。

### V1 / 核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/tiktok_ads.duckdb`。
```sql
SELECT "ID","EMAIL",regexp_matches(lower(trim("EMAIL")), '^[a-z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$') agent_accept,regexp_full_match(lower(trim("EMAIL")), '^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$') alternative_accept FROM raw.tiktok_advertiser_data WHERE agent_accept IS DISTINCT FROM alternative_accept
```
结果原文：
```json
{
  "executed_utc": "2026-10-29T11:33:05.717665+00:00",
  "columns": [
    "ID",
    "EMAIL",
    "agent_accept",
    "alternative_accept"
  ],
  "rows": [
    [
      "12",
      "adv12@sub..example.com",
      false,
      true
    ]
  ]
}
```

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['advertiser_id']`；原评分比较列：`['address', 'advertiser_id', 'advertiser_name', 'balance', 'company', 'contacter', 'country', 'currency', 'description', 'email', 'industry', 'language', 'telephone_number', 'timezone']`。与键取并集，不自行纳入原评分排除列。

全部原数据库以READ_ONLY连接或ATTACH；本次建表和改SQL只在`data/017_work/`。staging用agent留存raw，021/027用gold上游CS。每个试验从相同原SQL独立替换，不累积其他修复。

共同时间控制：`[]`。023/025/028沿原筛查候选日期；030沿010已经验证的兼容2025-10-13日期（不声称唯一执行日）；共同控制先应用到基线及全部干预，不能作为某个局部修复的功劳。

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|email_pattern|1→0|1→0|L0|

### 原留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|200|200|0|0|0/0|1|1|1|False|
|L1|200|200|0|0|0/0|1|1|1|False|
|L2|200|200|0|0|0/0|1|1|1|False|
|L3|200|200|0|0|0/0|1|1|1|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|advertiser_id|0|0|0|0|
|address|0|0|0|0|
|advertiser_name|0|0|0|0|
|balance|0|0|0|0|
|company|0|0|0|0|
|contacter|0|0|0|0|
|country|0|0|0|0|
|currency|0|0|0|0|
|description|0|0|0|0|
|email|1|1|1|1|
|industry|0|0|0|0|
|language|0|0|0|0|
|telephone_number|0|0|0|0|
|timezone|0|0|0|0|

### 重跑 baseline

SQL：`data/017_work/impl-024/baseline.sql`；SHA-256：`0fc81c8ecdcac4c1812c6b6a33de9a1866d1187c37c3a49fad45415833f00df0`。

同输入、同时间控制、不增加因果改动的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|200|200|0|0|0/0|1|1|1|False|
|L1|200|200|0|0|0/0|1|1|1|False|
|L2|200|200|0|0|0/0|1|1|1|False|
|L3|200|200|0|0|0/0|1|1|1|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|advertiser_id|0|0|0|0|
|address|0|0|0|0|
|advertiser_name|0|0|0|0|
|balance|0|0|0|0|
|company|0|0|0|0|
|contacter|0|0|0|0|
|country|0|0|0|0|
|currency|0|0|0|0|
|description|0|0|0|0|
|email|1|1|1|1|
|industry|0|0|0|0|
|language|0|0|0|0|
|telephone_number|0|0|0|0|
|timezone|0|0|0|0|

### 重跑 email_pattern

SQL：`data/017_work/impl-024/email_pattern.sql`；SHA-256：`cd9c3dfeea323f113bfeda2602bc16a10a0160e20c02d6605bb7d47216a27e87`。

唯一替换位置offset=585；原文：
```sql
^[a-z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$
```
新文：
```sql
^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|200|200|0|0|0/0|0|0|0|True|
|L1|200|200|0|0|0/0|0|0|0|True|
|L2|200|200|0|0|0/0|0|0|0|True|
|L3|200|200|0|0|0/0|0|0|0|True|

整表首次匹配档位：**L0**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|advertiser_id|0|0|0|0|
|address|0|0|0|0|
|advertiser_name|0|0|0|0|
|balance|0|0|0|0|
|company|0|0|0|0|
|contacter|0|0|0|0|
|country|0|0|0|0|
|currency|0|0|0|0|
|description|0|0|0|0|
|email|0|0|0|0|
|industry|0|0|0|0|
|language|0|0|0|0|
|telephone_number|0|0|0|0|
|timezone|0|0|0|0|

## 5. 类别、把握和对比

- 主要原因：**A**（归因判断）。
- 主因单项：email_pattern。
- 参与因素：无。
- 标记：无。
- 把握：**中**。
- 重跑是否满足U第4条件：是：单换正则1行/1格→0，L0匹配；非U。

agent明确使用更窄的匹配集合；没有“所有源email都有效”的依赖。单改能匹配gold不是U证据。

与014相比是否变化：不适用（第三批首次标注）；也未修改016任何结论。

## 规则问题

可读为O（若standard pattern已唯一排除连续点），也可读为A（没有指定可执行正则）。本次不自行引入额外邮件规范作为契约，选择A。这里不裁定现实邮件地址是否可投递，也不评价gold边界设计。

2026-10-29用户确认补充：本表依赖原始表若agent留存与初始一致而gold不同，先诊断再标不可评估；若gold与初始一致而agent不同，则正常标注并追踪agent运行中的改动。不能把两种情况混淆。raw差异须限定到本表依赖；CS上游用gold。

新增字段统一口径：记录与实际差异机制相关的明确选择/可疑数据表述；不要求agent预知gold，也不把泛称“完成清洗”算作识别具体边界。021关于重复计数、029关于可选字段失败置NULL为适用范围较广的声明，单独注明并未点名本表异常；可见证据只能支持这一有限范围。该字段不增减U/C/D/I/A/O/X条件。
