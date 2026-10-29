# impl-001 / stg_lever__application

## 1. 错在哪里

agent 按契约删除解析后创建时间为空的全部5000行；gold保留这些行，去掉该筛选即完全匹配。

已核实：raw 的5000个 created_at 非空，但 TRY_CAST 后全部为空；agent 输出0行，gold输出5000行。agent SQL 第23行执行 created_at IS NOT NULL，契约明确要求 created_at not_null，gold SQL 明确写“do not drop rows because created_at is empty”。只删除这一项过滤，L0–L3均完全匹配。归因判断：主要是 gold 保留空创建时间与契约非空要求冲突，归 O；不是看到空表就判 D，也不能仅凭解析失败就判 U。

## 2. 依据

- 起点：[013精简包](../013_packages/013_impl-001_staging_stg_lever__application.md)。原013状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`，第390–428行。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql`；gold SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/staging/stg_lever__application.sql`。精简包完整收录；下列补丁逐字给出定位原文。
- [完整事件记录](../014_trace_impl-001.json)；事件文件在该JSON的path中，可回查traces/dacomp_deimpl_prev.tar.gz。
- [查询原文与结果](../014_queries_impl-001.json)、[全部重跑记录](../014_reruns_impl-001.json)。

### SQL行号定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql`
```text
13:         try_cast(r."archived_at" AS TIMESTAMP) AS archived_at,
16:         try_cast(r."created_at" AS TIMESTAMP) AS created_at
23:               created_at IS NOT NULL
26:     SELECT *, row_number() OVER (PARTITION BY application_id ORDER BY application_id) AS _row_num
29: SELECT application_id, opportunity_id, posting_id, type, candidate_id, posting_hiring_manager_user_id, posting_owner_user_id, company, referrer_user_id, requisition_id, archived_at, archived_reason_id, comments, created_at
31: WHERE _row_num = 1
```

gold：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/staging/stg_lever__application.sql`
```text
15:         try_cast(archived_at as timestamp) as archived_at,
18:         try_cast(created_at as timestamp) as created_at
26:         -- Relax time filtering: do not drop rows because created_at is empty, only compare when comparable
27:         and (archived_at is null or created_at is null or archived_at >= created_at)
```

## 3. agent看过什么

event 1 含完整契约；event 17 用通用生成器把 not_null 转成筛选条件，并把时间统一 TRY_CAST。全69事件未找到 application 创建时间样例或解析成功率查询；event 28 只回显执行日志，不能证明看过源时间值。

已逐题核对event 1 message，包含本表契约完整原文；这不是把磁盘上存在的文档等同于agent已经阅读。schema输出、源数据值、运行日志分别处理。轨迹全量转录未删去截断标记；被截断的未显示部分不作为看到的证据。

## 4. 查询与重跑

核实查询实际执行 **1条**；核实代价：**一条查询**。诊断查询不计入5条限制。重复执行的查询仍计数。

### V1：核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/lever.duckdb`

```sql
SELECT count(*) n,count(created_at) raw_created_nonnull,count(try_cast(created_at AS TIMESTAMP)) parsed_created_nonnull,count(*) FILTER(WHERE try_cast(archived_at AS TIMESTAMP)<try_cast(created_at AS TIMESTAMP)) inverted,count(distinct id) ids FROM raw.application
```

结果：
```json
{
  "columns": [
    "n",
    "raw_created_nonnull",
    "parsed_created_nonnull",
    "inverted",
    "ids"
  ],
  "rows": [
    [
      5000,
      5000,
      0,
      0,
      5000
    ]
  ]
}
```

### D1：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`

```sql
SELECT count(*) n,count(created_at) raw_created_nonnull,count(try_cast(created_at AS TIMESTAMP)) parsed_created_nonnull,count(*) FILTER(WHERE try_cast(archived_at AS TIMESTAMP)<try_cast(created_at AS TIMESTAMP)) inverted,count(distinct id) ids FROM raw.application
```

结果：
```json
{
  "columns": [
    "n",
    "raw_created_nonnull",
    "parsed_created_nonnull",
    "inverted",
    "ids"
  ],
  "rows": [
    [
      5000,
      5000,
      0,
      0,
      5000
    ]
  ]
}
```

### D_raw：诊断查询

数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/lever.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb']`

```sql
SELECT * FROM raw.application
```

结果：
```json
{
  "result": {
    "columns_identical": true,
    "agent_rows": 5000,
    "gold_rows": 5000,
    "agent_only_rows": 0,
    "gold_only_rows": 0
  },
  "operation": "Python Counter of full typed rows, exact multiset difference"
}
```

### 比较口径

原件均READ_ONLY；只把本节点引用表复制到data/014_work私有DuckDB后执行。staging输入来自agent留存库raw；003/008上游直接复制gold，实现CS。固定原评分的comparison_columns与key_columns；L0为lower/trim/NULL规范化，L1数字及布尔归一，L2数值两位小数，L3再放宽日期时间到日期。键始终固定L0，不在宽松档位重新归一。

无共同键时逐列0表示无可比较行，不表示一致。重复键按值/行多重集合抵消，报告最少不一致对数；同时公开额外行次数。为避免键被漏出整表判断，含键整表匹配用于本次U4；旧007式仅值列整表匹配并列展示。这里没有重定义原官方对错或修改旧状态。

比较列：`['application_id', 'opportunity_id', 'posting_id', 'type', 'candidate_id', 'posting_hiring_manager_user_id', 'posting_owner_user_id', 'company', 'referrer_user_id', 'requisition_id', 'archived_at', 'archived_reason_id', 'comments', 'created_at']`；键：`['application_id']`。

### 留存基线（013材料来源）

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|0|5000|0|5000|0|0/0|0/5000|False|False|
|L1|0|5000|0|5000|0|0/0|0/5000|False|False|
|L2|0|5000|0|5000|0|0/0|0/5000|False|False|
|L3|0|5000|0|5000|0|0/0|0/5000|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|application_id|0|0|0|0|
|opportunity_id|0|0|0|0|
|posting_id|0|0|0|0|
|type|0|0|0|0|
|candidate_id|0|0|0|0|
|posting_hiring_manager_user_id|0|0|0|0|
|posting_owner_user_id|0|0|0|0|
|company|0|0|0|0|
|referrer_user_id|0|0|0|0|
|requisition_id|0|0|0|0|
|archived_at|0|0|0|0|
|archived_reason_id|0|0|0|0|
|comments|0|0|0|0|
|created_at|0|0|0|0|

### 重跑：baseline

不改SQL；建立本轮相同引擎、相同输入的比较基线。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|0|5000|0|5000|0|0/0|0/5000|False|False|
|L1|0|5000|0|5000|0|0/0|0/5000|False|False|
|L2|0|5000|0|5000|0|0/0|0/5000|False|False|
|L3|0|5000|0|5000|0|0/0|0/5000|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|application_id|0|0|0|0|
|opportunity_id|0|0|0|0|
|posting_id|0|0|0|0|
|type|0|0|0|0|
|candidate_id|0|0|0|0|
|posting_hiring_manager_user_id|0|0|0|0|
|posting_owner_user_id|0|0|0|0|
|company|0|0|0|0|
|referrer_user_id|0|0|0|0|
|requisition_id|0|0|0|0|
|archived_at|0|0|0|0|
|archived_reason_id|0|0|0|0|
|comments|0|0|0|0|
|created_at|0|0|0|0|

### 重跑：allow_null_created

只替换以下原文（其余字节经验证不变）：
```sql
opportunity_id IS NOT NULL AND
              created_at IS NOT NULL
```
替换为：
```sql
opportunity_id IS NOT NULL
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|5000|5000|0|0|0|0/0|0/0|True|True|
|L1|5000|5000|0|0|0|0/0|0/0|True|True|
|L2|5000|5000|0|0|0|0/0|0/0|True|True|
|L3|5000|5000|0|0|0|0/0|0/0|True|True|

含键整表首次匹配档位：**L0**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|application_id|0|0|0|0|
|opportunity_id|0|0|0|0|
|posting_id|0|0|0|0|
|type|0|0|0|0|
|candidate_id|0|0|0|0|
|posting_hiring_manager_user_id|0|0|0|0|
|posting_owner_user_id|0|0|0|0|
|company|0|0|0|0|
|referrer_user_id|0|0|0|0|
|requisition_id|0|0|0|0|
|archived_at|0|0|0|0|
|archived_reason_id|0|0|0|0|
|comments|0|0|0|0|
|created_at|0|0|0|0|

### 重跑：archive_check

只替换以下原文（其余字节经验证不变）：
```sql
WHERE _row_num = 1
```
替换为：
```sql
WHERE _row_num = 1 AND (archived_at IS NULL OR created_at IS NULL OR archived_at >= created_at)
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|0|5000|0|5000|0|0/0|0/5000|False|False|
|L1|0|5000|0|5000|0|0/0|0/5000|False|False|
|L2|0|5000|0|5000|0|0/0|0/5000|False|False|
|L3|0|5000|0|5000|0|0/0|0/5000|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|application_id|0|0|0|0|
|opportunity_id|0|0|0|0|
|posting_id|0|0|0|0|
|type|0|0|0|0|
|candidate_id|0|0|0|0|
|posting_hiring_manager_user_id|0|0|0|0|
|posting_owner_user_id|0|0|0|0|
|company|0|0|0|0|
|referrer_user_id|0|0|0|0|
|requisition_id|0|0|0|0|
|archived_at|0|0|0|0|
|archived_reason_id|0|0|0|0|
|comments|0|0|0|0|
|created_at|0|0|0|0|

### gold SQL在同一私有输入上的诊断

这是诊断，不是局部修复，也不用于证明U4。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|5000|5000|0|0|0|0/0|0/0|True|True|
|L1|5000|5000|0|0|0|0/0|0/0|True|True|
|L2|5000|5000|0|0|0|0/0|0/0|True|True|
|L3|5000|5000|0|0|0|0/0|0/0|True|True|

含键整表首次匹配档位：**L0**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|application_id|0|0|0|0|
|opportunity_id|0|0|0|0|
|posting_id|0|0|0|0|
|type|0|0|0|0|
|candidate_id|0|0|0|0|
|posting_hiring_manager_user_id|0|0|0|0|
|posting_owner_user_id|0|0|0|0|
|company|0|0|0|0|
|referrer_user_id|0|0|0|0|
|requisition_id|0|0|0|0|
|archived_at|0|0|0|0|
|archived_reason_id|0|0|0|0|
|comments|0|0|0|0|
|created_at|0|0|0|0|

## 5. 类别和把握

- 主要原因：**O**（归因判断）。
- 参与因素：无。
- 标记：无。
- 把握：**高**。
- 重跑是否满足U第4条件：是（allow_null_created 完全匹配L0；不代表归U）。

候选 P：raw.created_at 可以直接 TRY_CAST 为 TIMESTAMP。V1反证；但本次导致官方差异的是遵照契约执行非空过滤，删除过滤的干预也不是修复时间解析，故不把这个成功干预作为P的U证据。

## 规则问题

O与U竞争：可以把时间解析失败解释为未核实格式；也可以按契约/gold冲突解释。选择O，因为匹配gold所需的最小改动恰好放宽契约，解析器没有改变。archived_at检查确实漏写，但单独补写差异不变，不列参与因素。

共同问题：手册第1节“不预设类别分布”与末句“希望未核实假设多”存在张力；本次以逐条证据条件为准，不按期望调整分布。U3“没看过任何足以判断P的东西”与“证据曾出现但被忽略仍归U”按后者作为例外解释。
