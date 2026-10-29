# impl-024 / stg_tiktok_ads__advertiser（v2定稿）

## 1. 差异描述与判定

email正则的域名接受范围不同：agent把adv12@sub..example.com置NULL，gold保留。

已核实：200行仅ID12的email不同。agent模式要求各域名段非空，gold的[a-z0-9.-]+接受连续点；017-V1对同一可见值分别返回false/true。只替换这一处模式便L0匹配。契约写standard pattern (local@domain.tld)，没有给出可执行的完整模式或边界例子；本次把正则边界未指定归A，中把握，不把agent拒绝该值说成未发现异常。 A项仅表示差异取决于契约未定的选择，不据gold实现认定agent做错。

主要原因：**A**；把握：**中**。
参与因素：无。标记：无。

与上一版（017）相比：原因类别及参与因素不变。不确定性由017的“看到了但没提”改按四档逐项记录：email_pattern=只有通用策略说明。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../017_annotations/017_impl-024_stg_tiktok_ads__advertiser.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自017，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

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

## 3. agent实际看到的信息与不确定性四档

event15→16看EMAIL列及前2行fake-email样例，不能据此说看过ID12；event23写正则，event31→32看到生成SQL；event49→50查到189/200 email非NULL。event63只泛述可选邮箱校验失败置NULL，没有点名连续点域名或两种正则边界。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|email_pattern|A|只有通用策略说明|63|

### email_pattern：只有通用策略说明

相关可选字段失败处理的一般策略，未解释本表邮箱正则接受集合或双点域名。017的三档未区分此层，本次按v2记通用策略。

事件 **63**，字段`args.final_thought`；[轨迹原文](../017_trace_impl-024.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/63.json`。
```text
可选邮箱/名称/手机号字段验证失败时置 NULL，记录仍保留。
```

已检视65个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **1条**；018新增核实查询 **0条**。核实代价：需要查业务说明。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../017_reruns_impl-024.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用017的查询与重跑证据；其中“新增/本次”的执行归属仍为017，018没有重复执行。
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

## 5. 逐项类别及U门槛

表级主要原因：**A**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|email_pattern|A|1→0|1→0|L0|

重跑是否满足U第4条件：**是：单换正则1行/1格→0，L0匹配；非U**。

agent明确使用更窄的匹配集合；没有“所有源email都有效”的依赖。单改能匹配gold不是U证据。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。不确定性由017的“看到了但没提”改按四档逐项记录：email_pattern=只有通用策略说明。

与014相比的历史对比沿用原字段：不适用：第三批首次标注。此字段不代替本次与016/017的对比。

## 规则问题

v2新增通用策略档后，邮箱等可选字段验证失败置NULL的声明记此档；并未说明双点域名正则边界，故不记具体说明。原因仍A：契约无可执行完整正则；不自行引入外部邮件规范改定O。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
