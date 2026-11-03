# 043：impl-024_stg_tiktok_ads__ad_history

## 结论

主要原因：**Unstated Choice**；把握：中；只能组合修复：否。

先比行减量，再比格减量；最大减量为2509行/2509格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`A`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-024/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/sql/staging/stg_tiktok_ads__ad_history.sql`；无SQL注释。材料包：`records/024_packages/024_impl-024_stg_tiktok_ads__ad_history.md`。

staging采用agent留存raw；013直接源对照逐项列出。

已逐张读取 `records/013_raw_impl-024.json`；与gold关系见 `records/015_raw_impl-024.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.tiktok_ad_history_data`：initial 2509行/1列；agent留存 2509行/1列；013差异=False。

## 同源决定

同源决定：event 23，`/tmp/gen.py`：循环读取契约与header生成staging；event25/27/29修订，event39修订数组解析。 目录编号：`024-gen-staging`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 23，两个staging统一把source_relation生成为平台常量tiktok_ads。 本表点：source_relation；编号 `024-source-relation`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共1条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引11（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

## 点：source_relation

类别：**Unstated Choice**；角色：非原因；把握：中。

平台标识还是具体raw表标识的粒度未规定。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-024_stg_tiktok_ads__ad_history.json`，条目 `source_relation`。

基线：L0=2509行/2509格; L1=2509行/2509格; L2=2509行/2509格; L3=2509行/2509格。

单改后：L0=2509行/2509格; L1=2509行/2509格; L2=2509行/2509格; L3=2509行/2509格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "'tiktok_ads' as source_relation",
    "new": "'raw.tiktok_ad_history_data' as source_relation",
    "offset": 444
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
      source_table: raw.tiktok_ad_history_data
      columns:
        - name: source_relation
          data_type: VARCHAR
        - name: ad_id
          data_type: VARCHAR
        - name: updated_at
          data_type: TIMESTAMP
          validation_rules:
            - rule: "updated_at is a valid timestamp"
              on_failure: nullify_field
        - name: ad_group_id
          data_type: VARCHAR
        - name: advertiser_id
          data_type: VARCHAR
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `024-gen-staging`；根源决定单元 `024-source-relation`。

## 点：base_url

类别：**Unstated Choice**；角色：主要；把握：中。

契约未规定base_url是否保留query等拆解算法；差异是材料未定的选择。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-024_stg_tiktok_ads__ad_history.json`，条目 `base_url`。

基线：L0=2509行/2509格; L1=2509行/2509格; L2=2509行/2509格; L3=2509行/2509格。

单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：2509行/2509格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "case when regexp_matches(trim(both '\"' from list_extract(regexp_extract_all(record, '(^|,)(\"(?:[^\"]|\"\")*\"|\\[[^\\]]*\\]|[^,]*)', 2), 15)), '^https?://') then regexp_extract(trim(both '\"' from list_extract(regexp_extract_all(record, '(^|,)(\"(?:[^\"]|\"\")*\"|\\[[^\\]]*\\]|[^,]*)', 2), 15)), '^(https?://[^/?#]+)', 1) || coalesce(regexp_extract(trim(both '\"' from list_extract(regexp_extract_all(record, '(^|,)(\"(?:[^\"]|\"\")*\"|\\[[^\\]]*\\]|[^,]*)', 2), 15)), '^[^?#]*?(/[^?#]*)', 1), '') else null end as base_url",
    "new": "trim(both '\"' from list_extract(regexp_extract_all(record, '(^|,)(\"(?:[^\"]|\"\")*\"|\\[[^\\]]*\\]|[^,]*)', 2), 15)) as base_url",
    "offset": 2054
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
        - name: impression_tracking_url
          data_type: VARCHAR
        - name: base_url
          data_type: VARCHAR
        - name: url_host
          data_type: VARCHAR
        - name: url_path
          data_type: VARCHAR
        - name: utm_source
          data_type: VARCHAR
        - name: utm_medium
          data_type: VARCHAR
        - name: utm_campaign
          data_type: VARCHAR
        - name: utm_content
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `024-gen-staging`；根源决定单元 `impl-024_stg_tiktok_ads__ad_history:base_url`。

## 点：url_path

类别：**Unstated Choice**；角色：非原因；把握：中。

契约未规定路径前导斜杠和空值表示；两种提取结果未由规格定下。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-024_stg_tiktok_ads__ad_history.json`，条目 `url_path`。

基线：L0=2509行/2509格; L1=2509行/2509格; L2=2509行/2509格; L3=2509行/2509格。

单改后：L0=2509行/2509格; L1=2509行/2509格; L2=2509行/2509格; L3=2509行/2509格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "regexp_extract(trim(both '\"' from list_extract(regexp_extract_all(record, '(^|,)(\"(?:[^\"]|\"\")*\"|\\[[^\\]]*\\]|[^,]*)', 2), 15)), '^https?://[^/?#]+(/[^?#]*)', 1) as url_path",
    "new": "'/' || coalesce(regexp_extract(trim(both '\"' from list_extract(regexp_extract_all(record, '(^|,)(\"(?:[^\"]|\"\")*\"|\\[[^\\]]*\\]|[^,]*)', 2), 15)), '^[a-zA-Z]+://[^/]+(/[^?#]*)', 1), '') as url_path",
    "offset": 2736
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
        - name: url_host
          data_type: VARCHAR
        - name: url_path
          data_type: VARCHAR
        - name: utm_source
          data_type: VARCHAR
        - name: utm_medium
          data_type: VARCHAR
        - name: utm_campaign
          data_type: VARCHAR
        - name: utm_content
          data_type: VARCHAR
        - name: utm_term
          data_type: VARCHAR
        - name: landing_page_url
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `024-gen-staging`；根源决定单元 `impl-024_stg_tiktok_ads__ad_history:url_path`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
