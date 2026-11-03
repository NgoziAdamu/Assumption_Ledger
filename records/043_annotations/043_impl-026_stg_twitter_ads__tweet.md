# 043：impl-026_stg_twitter_ads__tweet

## 结论

主要原因：**其他**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为1行/1格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`O`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-026/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-026/agent/dacomp-de-impl-026/sql/staging/stg_twitter_ads__tweet.sql`；无SQL注释。材料包：`records/024_packages/024_impl-026_stg_twitter_ads__tweet.md`。

staging采用agent留存raw；013直接源对照逐项列出。

已逐张读取 `records/013_raw_impl-026.json`；与gold关系见 `records/015_raw_impl-026.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.twitter_tweet_data`：initial 2500行/25列；agent留存 2500行/25列；013差异=False。

## 同源决定

同源决定：event 13,17,19，`/tmp/gen.py`：report辅助函数批量生成report staging；同一脚本追加agg_model和marts，keyword在event21修正。 目录编号：`026-gen`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共2条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引24（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `language原值与规范值`：`records/024_queries.json` 数组索引25（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

## 点：language_normalize

类别：**其他**；角色：主要；把握：高。

契约给出语言枚举、非法值nullify；agent按原值验证，gold另做lower/trim接受不在原枚举的值。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-026_stg_twitter_ads__tweet.json`，条目 `language_normalize`。

基线：L0=1行/1格; L1=1行/1格; L2=1行/1格; L3=1行/1格。

单改后：L0=0行/0格; L1=0行/0格; L2=0行/0格; L3=0行/0格。L0减量（先行后格）：1行/1格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "case when lang in ('en','es','fr','de','ja','zh','ar','pt','ru','ko') then lang else null end as language",
    "new": "case when lower(trim(lang)) in ('en','es','fr','de','ja','zh','ar','pt','ru','ko') then lower(trim(lang)) else null end as language",
    "offset": 73
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-026/agent/output.jsonl`：

```text
    - name: stg_twitter_ads__tweet
      description: "Cleaned tweets with validated language and reasonable created_at bounds applied at staging filter."
      source_table: raw.twitter_tweet_data
      columns:
        - name: account_id
          data_type: VARCHAR
        - name: tweet_id
          data_type: VARCHAR
        - name: name
          data_type: VARCHAR
        - name: full_text
          data_type: VARCHAR
        - name: language
          data_type: VARCHAR
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `026-gen`；根源决定单元 `impl-026_stg_twitter_ads__tweet:language_normalize`。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
