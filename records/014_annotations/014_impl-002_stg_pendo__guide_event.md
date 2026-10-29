# impl-002 / stg_pendo__guide_event

## 1. 错在哪里

URL未执行契约中的正则校验；另有未规定的hash公式差异和gold额外的latitude范围处理。

已核实：15000行的url和guide_event_key均不同，latitude有13655行不同，共43655个不一致列值。URL规则修复与key公式替换各减少15000个列差异；latitude修复减少13655个。归因判断：URL校验在契约中明确写出，agent只trim而不执行，选 C 为主要原因；key只描述Generated surrogate key、未给拼接字段与分隔符，归 A 参与因素；latitude契约只有DOUBLE，没有范围要求，gold新增范围处理，列为O候选。

## 2. 依据

- 起点：[013精简包](../013_packages/013_impl-002_staging_stg_pendo__guide_event.md)。原013状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml`，第268–321行。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql`；gold SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql`。精简包完整收录；下列补丁逐字给出定位原文。
- [完整事件记录](../014_trace_impl-002.json)；事件文件在该JSON的path中，可回查traces/dacomp_deimpl_prev.tar.gz。
- [查询原文与结果](../014_queries_impl-002.json)、[全部重跑记录](../014_reruns_impl-002.json)。

### SQL行号定位

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql`
```text
12:     TRY_CAST(latitude AS DOUBLE) AS latitude,
16:     CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS VARCHAR)), '') END AS url,
17:     md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(guide_id AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), ''))) AS guide_event_key
```

gold：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/staging/stg_pendo__guide_event.sql`
```text
19:         WHEN latitude BETWEEN -90 AND 90 THEN CAST(latitude AS DOUBLE)
21:     END as latitude,
47:         WHEN TRIM(url) = '' THEN NULL
48:         WHEN url IS NOT NULL AND url ~ '^https?://' THEN TRIM(url)
50:     END as url,
57:     -- Generate a surrogate key using MD5 hash of concatenated fields
60:         THEN MD5(CONCAT(
```

## 3. agent看过什么

event 1完整提供本表规则；event 13→14看raw schema；event 19生成staging表达式。未找到支持“所有URL符合契约SQL正则”的完整查询。V1显示前缀匹配15000、DuckDB全匹配0：实际观察到的差异来自规则写法和SQL实现，不能把这15000个URL说成现实中的无效URL。

已逐题核对event 1 message，包含本表契约完整原文；这不是把磁盘上存在的文档等同于agent已经阅读。schema输出、源数据值、运行日志分别处理。轨迹全量转录未删去截断标记；被截断的未显示部分不作为看到的证据。

## 4. 查询与重跑

核实查询实际执行 **1条**；核实代价：**一条查询**。诊断查询不计入5条限制。重复执行的查询仍计数。

### V1：核实查询

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE url IS NOT NULL) urls,count(*) FILTER(WHERE url ~ '^https?://') full_regex,count(*) FILTER(WHERE regexp_matches(url,'^https?://')) prefix_regex,count(*) FILTER(WHERE latitude NOT BETWEEN -90 AND 90) invalid_lat,count(*) FILTER(WHERE account_id IS NULL OR guide_id IS NULL OR timestamp IS NULL OR visitor_id IS NULL OR app_id IS NULL) missing_required FROM raw.guide_event
```

结果：
```json
{
  "columns": [
    "n",
    "urls",
    "full_regex",
    "prefix_regex",
    "invalid_lat",
    "missing_required"
  ],
  "rows": [
    [
      15000,
      15000,
      0,
      15000,
      13655,
      0
    ]
  ]
}
```

### D1：诊断查询

数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/pendo.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE url IS NOT NULL) urls,count(*) FILTER(WHERE url ~ '^https?://') full_regex,count(*) FILTER(WHERE regexp_matches(url,'^https?://')) prefix_regex,count(*) FILTER(WHERE latitude NOT BETWEEN -90 AND 90) invalid_lat,count(*) FILTER(WHERE account_id IS NULL OR guide_id IS NULL OR timestamp IS NULL OR visitor_id IS NULL OR app_id IS NULL) missing_required FROM raw.guide_event
```

结果：
```json
{
  "columns": [
    "n",
    "urls",
    "full_regex",
    "prefix_regex",
    "invalid_lat",
    "missing_required"
  ],
  "rows": [
    [
      15000,
      15000,
      0,
      15000,
      13655,
      0
    ]
  ]
}
```

### D_raw：诊断查询

数据库：`['/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/pendo.duckdb', '/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/pendo.duckdb']`

```sql
SELECT * FROM raw.guide_event
```

结果：
```json
{
  "result": {
    "columns_identical": true,
    "agent_rows": 15000,
    "gold_rows": 15000,
    "agent_only_rows": 0,
    "gold_only_rows": 0
  },
  "operation": "Python Counter of full typed rows, exact multiset difference"
}
```

### 比较口径

原件均READ_ONLY；只把本节点引用表复制到data/014_work私有DuckDB后执行。staging输入来自agent留存库raw；003/008上游直接复制gold，实现CS。固定原评分的comparison_columns与key_columns；L0为lower/trim/NULL规范化，L1数字及布尔归一，L2数值两位小数，L3再放宽日期时间到日期。键始终固定L0，不在宽松档位重新归一。

无共同键时逐列0表示无可比较行，不表示一致。重复键按值/行多重集合抵消，报告最少不一致对数；同时公开额外行次数。为避免键被漏出整表判断，含键整表匹配用于本次U4；旧007式仅值列整表匹配并列展示。这里没有重定义原官方对错或修改旧状态。

比较列：`['account_id', 'app_id', 'country', 'guide_event_key', 'guide_id', 'guide_step_id', 'latitude', 'longitude', 'region', 'remote_ip', 'server_name', 'type', 'url', 'user_agent', 'visitor_id']`；键：`['account_id', 'app_id', 'guide_id', 'visitor_id']`。

### 留存基线（013材料来源）

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L1|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L2|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L3|15000|15000|0|0|15000|0/0|15000/15000|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|app_id|0|0|0|0|
|country|0|0|0|0|
|guide_event_key|15000|15000|15000|15000|
|guide_id|0|0|0|0|
|guide_step_id|0|0|0|0|
|latitude|13655|13655|13655|13655|
|longitude|0|0|0|0|
|region|0|0|0|0|
|remote_ip|0|0|0|0|
|server_name|0|0|0|0|
|type|0|0|0|0|
|url|15000|15000|15000|15000|
|user_agent|0|0|0|0|
|visitor_id|0|0|0|0|

### 重跑：baseline

不改SQL；建立本轮相同引擎、相同输入的比较基线。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L1|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L2|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L3|15000|15000|0|0|15000|0/0|15000/15000|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|app_id|0|0|0|0|
|country|0|0|0|0|
|guide_event_key|15000|15000|15000|15000|
|guide_id|0|0|0|0|
|guide_step_id|0|0|0|0|
|latitude|13655|13655|13655|13655|
|longitude|0|0|0|0|
|region|0|0|0|0|
|remote_ip|0|0|0|0|
|server_name|0|0|0|0|
|type|0|0|0|0|
|url|15000|15000|15000|15000|
|user_agent|0|0|0|0|
|visitor_id|0|0|0|0|

### 重跑：key_formula

只替换以下原文（其余字节经验证不变）：
```sql
md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(guide_id AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), '')))
```
替换为：
```sql
CASE WHEN account_id IS NOT NULL AND guide_id IS NOT NULL AND timestamp IS NOT NULL AND visitor_id IS NOT NULL THEN md5(concat(coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), ''), coalesce(server_name, ''), coalesce(CAST(guide_id AS VARCHAR), ''), coalesce(user_agent, ''), coalesce(remote_ip, ''))) ELSE NULL END
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L1|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L2|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L3|15000|15000|0|0|15000|0/0|15000/15000|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|app_id|0|0|0|0|
|country|0|0|0|0|
|guide_event_key|0|0|0|0|
|guide_id|0|0|0|0|
|guide_step_id|0|0|0|0|
|latitude|13655|13655|13655|13655|
|longitude|0|0|0|0|
|region|0|0|0|0|
|remote_ip|0|0|0|0|
|server_name|0|0|0|0|
|type|0|0|0|0|
|url|15000|15000|15000|15000|
|user_agent|0|0|0|0|
|visitor_id|0|0|0|0|

### 重跑：url_rule

只替换以下原文（其余字节经验证不变）：
```sql
CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS VARCHAR)), '') END
```
替换为：
```sql
CASE WHEN TRIM(url) = '' THEN NULL WHEN url IS NOT NULL AND url ~ '^https?://' THEN TRIM(url) ELSE NULL END
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L1|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L2|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L3|15000|15000|0|0|15000|0/0|15000/15000|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|app_id|0|0|0|0|
|country|0|0|0|0|
|guide_event_key|15000|15000|15000|15000|
|guide_id|0|0|0|0|
|guide_step_id|0|0|0|0|
|latitude|13655|13655|13655|13655|
|longitude|0|0|0|0|
|region|0|0|0|0|
|remote_ip|0|0|0|0|
|server_name|0|0|0|0|
|type|0|0|0|0|
|url|0|0|0|0|
|user_agent|0|0|0|0|
|visitor_id|0|0|0|0|

### 重跑：latitude_range

只替换以下原文（其余字节经验证不变）：
```sql
TRY_CAST(latitude AS DOUBLE)
```
替换为：
```sql
CASE WHEN latitude BETWEEN -90 AND 90 THEN CAST(latitude AS DOUBLE) ELSE NULL END
```

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L1|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L2|15000|15000|0|0|15000|0/0|15000/15000|False|False|
|L3|15000|15000|0|0|15000|0/0|15000/15000|False|False|

含键整表首次匹配档位：**L0–L3均未匹配**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|app_id|0|0|0|0|
|country|0|0|0|0|
|guide_event_key|15000|15000|15000|15000|
|guide_id|0|0|0|0|
|guide_step_id|0|0|0|0|
|latitude|0|0|0|0|
|longitude|0|0|0|0|
|region|0|0|0|0|
|remote_ip|0|0|0|0|
|server_name|0|0|0|0|
|type|0|0|0|0|
|url|15000|15000|15000|15000|
|user_agent|0|0|0|0|
|visitor_id|0|0|0|0|

### gold SQL在同一私有输入上的诊断

这是诊断，不是局部修复，也不用于证明U4。

|档位|agent行|gold行|仅agent键中的行|仅gold键中的行|共同键不同整行/最少对数|共同键额外行 A/G|全键不匹配行出现 A/G|含键整表匹配|只比较值列匹配|
|---|---:|---:|---:|---:|---:|---|---|---|---|
|L0|15000|15000|0|0|0|0/0|0/0|True|True|
|L1|15000|15000|0|0|0|0/0|0/0|True|True|
|L2|15000|15000|0|0|0|0/0|0/0|True|True|
|L3|15000|15000|0|0|0|0/0|0/0|True|True|

含键整表首次匹配档位：**L0**。

|比较列|L0|L1|L2|L3|
|---|---:|---:|---:|---:|
|account_id|0|0|0|0|
|app_id|0|0|0|0|
|country|0|0|0|0|
|guide_event_key|0|0|0|0|
|guide_id|0|0|0|0|
|guide_step_id|0|0|0|0|
|latitude|0|0|0|0|
|longitude|0|0|0|0|
|region|0|0|0|0|
|remote_ip|0|0|0|0|
|server_name|0|0|0|0|
|type|0|0|0|0|
|url|0|0|0|0|
|user_agent|0|0|0|0|
|visitor_id|0|0|0|0|

## 5. 类别和把握

- 主要原因：**C**（归因判断）。
- 参与因素：A（surrogate key公式）；O候选（latitude额外范围规则）。
- 标记：证据曾出现但被忽略。
- 把握：**中**。
- 重跑是否满足U第4条件：否（每项修复后仍15000行不同）。

不设可直接成立的U结论。契约明确的URL规则优先按C；hash业务规则无法由数据唯一确定；latitude是否应限定范围也没有任务文字要求。

## 规则问题

三项错误单独修复后，整行差异均不降，按列差异却分别减少15000/15000/13655。手册未规定“差异减少”单位和并列决胜：本表按列差异识别参与因素，C与A并列时暂选有明确契约证据的C，把握中。O是否适用于gold增加未声明规则而非直接矛盾，也需复核。

共同问题：手册第1节“不预设类别分布”与末句“希望未核实假设多”存在张力；本次以逐条证据条件为准，不按期望调整分布。U3“没看过任何足以判断P的东西”与“证据曾出现但被忽略仍归U”按后者作为例外解释。
