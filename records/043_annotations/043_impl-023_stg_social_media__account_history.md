# 043：impl-023_stg_social_media__account_history

## 结论

主要原因：**其他**；把握：中；只能组合修复：是。

所有逐点单改均不减少行或格，组合减少；不将零改善点记为参与因素。

层：staging。024旧主要原因原样保留：`O`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__account_history.sql`；无SQL注释。材料包：`records/024_packages/024_impl-023_stg_social_media__account_history.md`。

staging采用agent留存raw；013直接源对照逐项列出。

已逐张读取 `records/013_raw_impl-023.json`；与gold关系见 `records/015_raw_impl-023.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.account_history`：initial 2500行/13列；agent留存 2500行/13列；013差异=False。

## 同源决定

同源决定：event 29,31,33，`/tmp/write_sql.py`：同一files字典脚本分三次写入staging、中间层、marts；各表表达式分别定义。 目录编号：`023-write-sql`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共2条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引0（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `契约键及timezone过滤计数`：`records/024_queries.json` 数组索引1（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 诊断 `多处组合仅诊断（不用于单点原因排名）`：`records/024_extra_diagnostics.json` 数组索引20（从0开始）。

- 诊断 `agent实际类型`：`records/024_diagnostics.json` 数组索引12（从0开始）。

- 诊断 `agent有限差异样例`：`records/024_diagnostics.json` 数组索引13（从0开始）。

- 诊断 `gold实际类型`：`records/024_diagnostics.json` 数组索引14（从0开始）。

- 诊断 `gold有限差异样例`：`records/024_diagnostics.json` 数组索引15（从0开始）。

- 诊断 `gold SQL同gold输入重跑`：`records/024_diagnostics.json` 数组索引31（从0开始）。

组合诊断：`records/024_extra_diagnostics.json` 索引20，只改['id_type', 'id_filter', 'timezone_filter']；L0=11行/11格; L1=11行/11格; L2=11行/11格; L3=11行/11格。只用于确认组合改善，不冒充任何单点的收益。

## 点：id_type

类别：**其他**；角色：组合项；把握：高。

契约id明确BIGINT且not_null；原始2500个id均不可转数值，agent按契约转换，gold保留文本。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__account_history.json`，条目 `id_type`。

基线：L0=2500行/22500格; L1=2500行/22500格; L2=2500行/22500格; L3=2500行/22500格。

单改后：L0=2500行/22500格; L1=2500行/22500格; L2=2500行/22500格; L3=2500行/22500格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(id as bigint) as id",
    "new": "id as id",
    "offset": 11
  }
]
```

是否说出：**第1档——交付物里针对本处说明了**。点名account_history.id并说明不能转换的键被删除，只覆盖id转换/过滤。

event 55 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
`account_history.id` 在源中为 VARCHAR，但契约要求 BIGINT；不可转换的键按无效主键处理并删除。
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
      source_table: raw.account_history
      columns:
        - name: id
          data_type: BIGINT
          constraints: [not_null]
        - name: updated_at
          data_type: TIMESTAMP
        - name: approval_status
          data_type: VARCHAR
        - name: business_id
          data_type: VARCHAR
        - name: business_name
          data_type: VARCHAR
        - name: created_at
          data_type: TIMESTAMP
```


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__account_history:id_type`。

## 点：id_filter

类别：**其他**；角色：组合项；把握：高。

BIGINT转换后NULL键按明确not_null排除；输出0行符合该要求，不能归为agent误解数据。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__account_history.json`，条目 `id_filter`。

基线：L0=2500行/22500格; L1=2500行/22500格; L2=2500行/22500格; L3=2500行/22500格。

单改后：L0=3965行/35685格; L1=3965行/35685格; L2=3965行/35685格; L3=3965行/35685格。L0减量（先行后格）：-1465行/-13185格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "where try_cast(id as bigint) is not null",
    "new": "where true",
    "offset": 506
  }
]
```

是否说出：**第1档——交付物里针对本处说明了**。点名account_history.id并说明不能转换的键被删除，只覆盖id转换/过滤。

event 55 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
`account_history.id` 在源中为 VARCHAR，但契约要求 BIGINT；不可转换的键按无效主键处理并删除。
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: id
          data_type: BIGINT
          constraints: [not_null]
        - name: updated_at
          data_type: TIMESTAMP
        - name: approval_status
          data_type: VARCHAR
        - name: business_id
          data_type: VARCHAR
        - name: business_name
          data_type: VARCHAR
        - name: created_at
          data_type: TIMESTAMP
        - name: deleted
          data_type: BOOLEAN
```


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__account_history:id_filter`。

## 点：timezone_filter

类别：**其他**；角色：组合项；把握：高。

契约给出timezone正则并要求delete_row；agent按该表达式过滤，gold保留部分不合规则值。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__account_history.json`，条目 `timezone_filter`。

基线：L0=2500行/22500格; L1=2500行/22500格; L2=2500行/22500格; L3=2500行/22500格。

单改后：L0=2500行/22500格; L1=2500行/22500格; L2=2500行/22500格; L3=2500行/22500格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "  and regexp_matches(timezone, '^[A-Z][a-z]+/[A-Z][a-z_]+$')",
    "new": "",
    "offset": 574
  }
]
```

是否说出：**第2档——交付物里只有通用说明**。通用说明明确提到无效时区行过滤，没有逐项说明此表的正则边界。

event 55 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
包含字段映射、类型转换、数据清洗、无效键/时区行过滤、指标空值处理及平台相关源表连接。
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
          constraints: [not_null]
          validation_rules:
            - rule: "timezone ~ '^[A-Z][a-z]+/[A-Z][a-z_]+$'"
              on_failure: delete_row
        - name: timezone_switch_at
          data_type: TIMESTAMP
```


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__account_history:timezone_filter`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
