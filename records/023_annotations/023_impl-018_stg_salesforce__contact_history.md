# impl-018 · stg_salesforce__contact_history

用途：**全量**；层：`staging`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**A**；把握：高；主要错误点：history_key_clock。

契约未规定评测历史键算法；agent 使用 ID/Fivetran 起止时间的 MD5，gold 使用 ID/运行时间串。

参与因素：无。

标记：无。

共同固定到 gold created_date 后仅改键表达式，5434→566行；剩余566来自契约contact_id唯一性去重与gold保留重复。去重单改因键未对齐反增规模，不列参与因素。

## 材料与比较口径

精简材料包：[023_impl-018_stg_salesforce__contact_history.md](../023_packages/023_impl-018_stg_salesforce__contact_history.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
契约行 917–966：

```
917:     - name: stg_salesforce__contact_history
918:       description: "Cleaned contact history records tracking changes to contact data over time"
919:       source_table: raw.contact_history
920:       columns:
921:         - name: contact_id
922:           data_type: VARCHAR
923:         - name: account_id
924:           data_type: VARCHAR
925:         - name: created_date
926:           data_type: TIMESTAMP
927:         - name: contact_description
928:           data_type: VARCHAR
929:         - name: email
930:           data_type: VARCHAR
931:         - name: first_name
932:           data_type: VARCHAR
933:         - name: is_deleted
934:           data_type: BOOLEAN
935:         - name: last_activity_date
936:           data_type: DATE
937:         - name: last_modified_date
938:           data_type: TIMESTAMP
939:         - name: last_name
940:           data_type: VARCHAR
941:         - name: lead_source
942:           data_type: VARCHAR
943:         - name: mailing_city
944:           data_type: VARCHAR
945:         - name: mailing_country
946:           data_type: VARCHAR
947:         - name: mailing_postal_code
948:           data_type: VARCHAR
949:         - name: mailing_state
950:           data_type: VARCHAR
951:         - name: mailing_street
952:           data_type: VARCHAR
953:         - name: mobile_phone
954:           data_type: VARCHAR
955:         - name: contact_name
956:           data_type: VARCHAR
957:         - name: owner_id
958:           data_type: VARCHAR
959:         - name: phone
960:           data_type: VARCHAR
961:         - name: title
962:           data_type: VARCHAR
963:         - name: history_unique_key
964:           data_type: VARCHAR
965:           constraints: [not_null, unique]
966:
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/staging/stg_salesforce__contact_history.sql`，SHA-256 `597034deb4aba0ef9445d1d388b4aa580cf22751326201018619b95bcd002061`，行 1–26。

```
1: select
2:       id as contact_id,
3:       account_id as account_id,
4:       try_cast(_fivetran_start as TIMESTAMP) as created_date,
5:       description as contact_description,
6:       email as email,
7:       first_name as first_name,
8:       is_deleted as is_deleted,
9:       try_cast(last_activity_date as DATE) as last_activity_date,
10:       try_cast(last_modified_date as TIMESTAMP) as last_modified_date,
11:       last_name as last_name,
12:       lead_source as lead_source,
13:       mailing_city as mailing_city,
14:       mailing_country as mailing_country,
15:       mailing_postal_code as mailing_postal_code,
16:       mailing_state as mailing_state,
17:       mailing_street as mailing_street,
18:       mobile_phone as mobile_phone,
19:       name as contact_name,
20:       owner_id as owner_id,
21:       phone as phone,
22:       title as title,
23:       md5(concat_ws('|', coalesce(cast(contact_id as varchar), ''), coalesce(cast(_fivetran_start as varchar), ''), coalesce(cast(_fivetran_end as varchar), ''))) as history_unique_key
24: from raw.contact_history
25: where id is not null
26: qualify row_number() over (partition by id order by id) = 1
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/staging/stg_salesforce__contact_history.sql`，SHA-256 `d4391f9267947cf66cd623551952effde1d5c99425e8a10dba63402ce60e8be8`，行 1–35。

```
1: with base as (
2:     select *   
3:     from raw.contact_history
4: ),
5: 
6: final as (
7:     select 
8:         cast(id as varchar) as contact_id,
9:         cast(account_id as varchar) as account_id,
10:         cast(current_timestamp as timestamp) as created_date,
11:         cast(description as varchar) as contact_description,
12:         cast(email as varchar) as email,
13:         cast(first_name as varchar) as first_name,
14:         cast(coalesce(is_deleted, false) as boolean) as is_deleted,
15:         cast(last_activity_date as date) as last_activity_date,
16:         cast(last_modified_date as timestamp) as last_modified_date,
17:         cast(last_name as varchar) as last_name,
18:         cast(lead_source as varchar) as lead_source,
19:         cast(mailing_city as varchar) as mailing_city,
20:         cast(mailing_country as varchar) as mailing_country,
21:         cast(mailing_postal_code as varchar) as mailing_postal_code,
22:         cast(mailing_state as varchar) as mailing_state,
23:         cast(mailing_street as varchar) as mailing_street,
24:         cast(mobile_phone as varchar) as mobile_phone,
25:         cast(name as varchar) as contact_name,
26:         cast(owner_id as varchar) as owner_id,
27:         cast(phone as varchar) as phone,
28:         cast(title as varchar) as title,
29:         -- Generate unique key for history tracking
30:         concat(id, '_', created_date::varchar) as history_unique_key
31:     from base
32: )
33: 
34: select *
35: from final
```

## 轨迹可见性与不确定性

**四档：针对本表的具体说明**。

event 99：「History 源数据没有契约所需的 history_unique_key 原始列，因此以实体记录 ID 与 Fivetran 起止时间生成确定性 MD5 键，用于稳定标识历史版本」。event 53/69 修复本表映射。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 53：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/53.json`。
- event 69：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/69.json`。
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

核实查询 **0** 条；核实代价档：**需要查业务说明**。诊断查询不计入 5 条上限。

未追加 agent 可见数据核实；判断依据为契约、SQL 和明确标为诊断的查询，不用 gold 结果证明 U。

### 诊断：gold 时间型键

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`。

```sql
SELECT min(created_date),max(created_date),min(history_unique_key),max(history_unique_key) FROM staging.stg_salesforce__contact_history
```


```json
{"columns":["min(created_date)","max(created_date)","min(history_unique_key)","max(history_unique_key)"],"rows":[["2025-10-24 15:24:19.642344","2025-10-24 15:24:19.642344","00301oeYPsRAbxH_2025-10-24 15:24:19.642344","003zzyPo1cN6qDC_2025-10-24 15:24:19.642344"]]}
```


## 独立单点重跑

### 首轮：[023_reruns_impl-018_stg_salesforce__contact_history.json](../023_reruns_impl-018_stg_salesforce__contact_history.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2434|3000|5434|92378|否|
|L1|2434|3000|5434|92378|否|
|L2|2434|3000|5434|92378|否|
|L3|2434|3000|5434|92378|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`
- L1：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`
- L2：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`
- L3：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-018_stg_salesforce__contact_history/baseline.sql`；SHA-256 `597034deb4aba0ef9445d1d388b4aa580cf22751326201018619b95bcd002061`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2434|3000|5434|92378|否|
|L1|2434|3000|5434|92378|否|
|L2|2434|3000|5434|92378|否|
|L3|2434|3000|5434|92378|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`
- L1：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`
- L2：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`
- L3：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`

#### history_key

判定：不计参与因素；类别候选 A。契约没有规定 history_unique_key 的构造算法。

相对本轮基线减少行 0、格 0；按行优先、格次之排序。
共同控制后 SQL 第 23 行起、字符 offset 802 的唯一连续替换；其余字节不动。
替换前：
```sql
md5(concat_ws('|', coalesce(cast(contact_id as varchar), ''), coalesce(cast(_fivetran_start as varchar), ''), coalesce(cast(_fivetran_end as varchar), '')))
```

替换后：
```sql
concat(id, '_', created_date::varchar)
```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact_history/history_key.sql`；SHA-256 `536032e3619fed94ee3d1fe862798d282fe65d9fd9de4069e0d3a282f392763c`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2434|3000|5434|92378|否|
|L1|2434|3000|5434|92378|否|
|L2|2434|3000|5434|92378|否|
|L3|2434|3000|5434|92378|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`
- L1：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`
- L2：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`
- L3：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`

#### unique_contact

判定：不计参与因素；类别候选 O。契约 contact_id unique 而 gold 保留重复。

相对本轮基线减少行 -566、格 -9622；按行优先、格次之排序。
共同控制后 SQL 第 26 行起、字符 offset 1027 的唯一连续替换；其余字节不动。
替换前：
```sql
qualify row_number() over (partition by id order by id) = 1
```

替换后：
```sql

```

私有 SQL：`data/023_work/impl-018_stg_salesforce__contact_history/unique_contact.sql`；SHA-256 `6e6bc3f9c6d3f8d880c74b51589a922bfc7cb996a8aa51747e30a59d05bce6ad`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|3000|3000|6000|102000|否|
|L1|3000|3000|6000|102000|否|
|L2|3000|3000|6000|102000|否|
|L3|3000|3000|6000|102000|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"history_unique_key":6000,"account_id":6000,"email":6000,"first_name":6000,"is_deleted":6000,"last_modified_date":6000,"last_name":6000,"lead_source":6000,"mailing_city":6000,"mailing_country":6000,"mailing_postal_code":6000,"mailing_state":6000,"mailing_street":6000,"mobile_phone":6000,"owner_id":6000,"phone":6000,"title":6000}`
- L1：`{"history_unique_key":6000,"account_id":6000,"email":6000,"first_name":6000,"is_deleted":6000,"last_modified_date":6000,"last_name":6000,"lead_source":6000,"mailing_city":6000,"mailing_country":6000,"mailing_postal_code":6000,"mailing_state":6000,"mailing_street":6000,"mobile_phone":6000,"owner_id":6000,"phone":6000,"title":6000}`
- L2：`{"history_unique_key":6000,"account_id":6000,"email":6000,"first_name":6000,"is_deleted":6000,"last_modified_date":6000,"last_name":6000,"lead_source":6000,"mailing_city":6000,"mailing_country":6000,"mailing_postal_code":6000,"mailing_state":6000,"mailing_street":6000,"mobile_phone":6000,"owner_id":6000,"phone":6000,"title":6000}`
- L3：`{"history_unique_key":6000,"account_id":6000,"email":6000,"first_name":6000,"is_deleted":6000,"last_modified_date":6000,"last_name":6000,"lead_source":6000,"mailing_city":6000,"mailing_country":6000,"mailing_postal_code":6000,"mailing_state":6000,"mailing_street":6000,"mobile_phone":6000,"owner_id":6000,"phone":6000,"title":6000}`
### 补充轮：[023_supplement_reruns_impl-018_stg_salesforce__contact_history.json](../023_supplement_reruns_impl-018_stg_salesforce__contact_history.json)

上游副本来源：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/salesforce.duckdb`。

共同时间控制：`[{"pattern":"\\bcurrent_timestamp\\b","replacement":"TIMESTAMPTZ '2025-10-24 15:24:19.642344+08:00'","count":0},{"pattern":"\\bcurrent_date\\b","replacement":"DATE '2025-10-24'","count":0}]`。

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_supplement_work/impl-018_stg_salesforce__contact_history/baseline.sql`；SHA-256 `597034deb4aba0ef9445d1d388b4aa580cf22751326201018619b95bcd002061`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2434|3000|5434|92378|否|
|L1|2434|3000|5434|92378|否|
|L2|2434|3000|5434|92378|否|
|L3|2434|3000|5434|92378|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`
- L1：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`
- L2：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`
- L3：`{"history_unique_key":5434,"account_id":5434,"email":5434,"first_name":5434,"is_deleted":5434,"last_modified_date":5434,"last_name":5434,"lead_source":5434,"mailing_city":5434,"mailing_country":5434,"mailing_postal_code":5434,"mailing_state":5434,"mailing_street":5434,"mobile_phone":5434,"owner_id":5434,"phone":5434,"title":5434}`

#### history_key_clock

判定：主因；类别候选 A。history_unique_key 算法未规定；在 gold 生成时刻共同固定时间后单改键表达式。

相对本轮基线减少行 4868、格 82756；按行优先、格次之排序。
共同控制后 SQL 第 23 行起、字符 offset 802 的唯一连续替换；其余字节不动。
替换前：
```sql
md5(concat_ws('|', coalesce(cast(contact_id as varchar), ''), coalesce(cast(_fivetran_start as varchar), ''), coalesce(cast(_fivetran_end as varchar), '')))
```

替换后：
```sql
concat(id, '_', cast(TIMESTAMPTZ '2025-10-24 15:24:19.642344+08:00' as timestamp)::varchar)
```

私有 SQL：`data/023_supplement_work/impl-018_stg_salesforce__contact_history/history_key_clock.sql`；SHA-256 `e86db440824a903d3c0c37d89b4408d21051132a94fee9623213b7c3c7e11ab9`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|2434|3000|566|9622|否|
|L1|2434|3000|566|9622|否|
|L2|2434|3000|566|9622|否|
|L3|2434|3000|566|9622|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"history_unique_key":566,"account_id":566,"email":566,"first_name":566,"is_deleted":566,"last_modified_date":566,"last_name":566,"lead_source":566,"mailing_city":566,"mailing_country":566,"mailing_postal_code":566,"mailing_state":566,"mailing_street":566,"mobile_phone":566,"owner_id":566,"phone":566,"title":566}`
- L1：`{"history_unique_key":566,"account_id":566,"email":566,"first_name":566,"is_deleted":566,"last_modified_date":566,"last_name":566,"lead_source":566,"mailing_city":566,"mailing_country":566,"mailing_postal_code":566,"mailing_state":566,"mailing_street":566,"mobile_phone":566,"owner_id":566,"phone":566,"title":566}`
- L2：`{"history_unique_key":566,"account_id":566,"email":566,"first_name":566,"is_deleted":566,"last_modified_date":566,"last_name":566,"lead_source":566,"mailing_city":566,"mailing_country":566,"mailing_postal_code":566,"mailing_state":566,"mailing_street":566,"mobile_phone":566,"owner_id":566,"phone":566,"title":566}`
- L3：`{"history_unique_key":566,"account_id":566,"email":566,"first_name":566,"is_deleted":566,"last_modified_date":566,"last_name":566,"lead_source":566,"mailing_city":566,"mailing_country":566,"mailing_postal_code":566,"mailing_state":566,"mailing_street":566,"mobile_phone":566,"owner_id":566,"phone":566,"title":566}`

## 规则问题

时间参与评测键且公式未规定：共同时间控制用于对照生成时刻，不把时间差另算原因；历史键公式仍作为一个 A 错误点。
