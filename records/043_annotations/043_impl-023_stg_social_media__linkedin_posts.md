# 043：impl-023_stg_social_media__linkedin_posts

## 结论

主要原因：**已说出的选择**；把握：中；只能组合修复：否。

先比行减量，再比格减量；最大减量为100行/100格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`A`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__linkedin_posts.sql`；无SQL注释。材料包：`records/024_packages/024_impl-023_stg_social_media__linkedin_posts.md`。

staging采用agent留存raw；013直接源对照逐项列出。

已逐张读取 `records/013_raw_impl-023.json`；与gold关系见 `records/015_raw_impl-023.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.linkedin_pages_organization_ugc_post`：initial 100行/3列；agent留存 100行/3列；013差异=False。

- `raw.linkedin_pages_post_content`：initial 2500行/8列；agent留存 2500行/8列；013差异=False。

- `raw.linkedin_pages_share_statistic`：initial 100行/10列；agent留存 100行/10列；013差异=False。

- `raw.linkedin_pages_ugc_post_history`：initial 75行/16列；agent留存 75行/16列；013差异=False。

## 同源决定

同源决定：event 29,31,33，`/tmp/write_sql.py`：同一files字典脚本分三次写入staging、中间层、marts；各表表达式分别定义。 目录编号：`023-write-sql`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共2条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引2（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `UGC历史关联覆盖`：`records/024_queries.json` 数组索引3（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

## 点：created_source

类别：**已说出的选择**；角色：主要；把握：中。

created_timestamp只声明类型，未指定历史created_time或同步时间。交付报告明确LinkedIn历史时间无匹配会为空；不能从gold同步时间倒推要求。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__linkedin_posts.json`，条目 `created_source`。

基线：L0=100行/100格; L1=100行/100格; L2=100行/100格; L3=100行/100格。

单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：100行/100格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "h.created_time::timestamp",
    "new": "o._fivetran_synced::timestamp",
    "offset": 501
  }
]
```

是否说出：**第1档——交付物里针对本处说明了**。LinkedIn staging一一对应本表，并说明历史created_time来源及缺失后果。

event 55 / `args.final_thought`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
LinkedIn staging 契约指定的关联源表缺少可直接匹配的 UGC 历史主键，关联历史中的 `created_time` 无匹配时为空，此类记录随后按中间层的非空时间要求排除。
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: post_id
          data_type: VARCHAR
        - name: created_timestamp
          data_type: TIMESTAMP
        - name: platform
          data_type: VARCHAR
        - name: post_message
          data_type: VARCHAR
        - name: content_type
          data_type: VARCHAR
        - name: post_url
          data_type: VARCHAR
          validation_rules:
            - rule: "post_url RLIKE '^https://www.linkedin.com/feed/update/.+'"
              on_failure: correct
```


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__linkedin_posts:created_source`。

## 点：message_source

类别：**Unstated Choice**；角色：非原因；把握：中。

post_message未指定article_title/media_title/commentary或合成字符串，内容选择未被材料定下。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__linkedin_posts.json`，条目 `message_source`。

基线：L0=100行/100格; L1=100行/100格; L2=100行/100格; L3=100行/100格。

单改后：L0=100行/100格; L1=100行/100格; L2=100行/100格; L3=100行/100格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "coalesce(pc.article_title, pc.media_title, h.commentary)::varchar",
    "new": "concat('LinkedIn Post ',o.ugc_post_id)::varchar",
    "offset": 590
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: platform
          data_type: VARCHAR
        - name: post_message
          data_type: VARCHAR
        - name: content_type
          data_type: VARCHAR
        - name: post_url
          data_type: VARCHAR
          validation_rules:
            - rule: "post_url RLIKE '^https://www.linkedin.com/feed/update/.+'"
              on_failure: correct
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__linkedin_posts:message_source`。

## 点：content_type

类别：**Unstated Choice**；角色：非原因；把握：中。

content_type无映射或默认值规则；从content.type取值与常量text属于未定选择。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__linkedin_posts.json`，条目 `content_type`。

基线：L0=100行/100格; L1=100行/100格; L2=100行/100格; L3=100行/100格。

单改后：L0=100行/100格; L1=100行/100格; L2=100行/100格; L3=100行/100格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "pc.type::varchar",
    "new": "'text'::varchar",
    "offset": 677
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: post_message
          data_type: VARCHAR
        - name: content_type
          data_type: VARCHAR
        - name: post_url
          data_type: VARCHAR
          validation_rules:
            - rule: "post_url RLIKE '^https://www.linkedin.com/feed/update/.+'"
              on_failure: correct
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__linkedin_posts:content_type`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
