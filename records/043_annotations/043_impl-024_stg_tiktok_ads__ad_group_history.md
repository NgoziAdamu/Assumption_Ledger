# 043：impl-024_stg_tiktok_ads__ad_group_history

## 结论

主要原因：**多因并列**；把握：中；只能组合修复：否。

先比行减量，再比格减量；最大减量为0行/2504格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`多因并列（A、O）`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-024/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/sql/staging/stg_tiktok_ads__ad_group_history.sql`；无SQL注释。材料包：`records/024_packages/024_impl-024_stg_tiktok_ads__ad_group_history.md`。

staging采用agent留存raw；013直接源对照逐项列出。

已逐张读取 `records/013_raw_impl-024.json`；与gold关系见 `records/015_raw_impl-024.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.tiktok_adgroup_history_data`：initial 2504行/1列；agent留存 2504行/1列；013差异=False。

## 同源决定

同源决定：event 23，`/tmp/gen.py`：循环读取契约与header生成staging；event25/27/29修订，event39修订数组解析。 目录编号：`024-gen-staging`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

同源决定：event 23，两个staging统一把source_relation生成为平台常量tiktok_ads。 本表点：source_relation；编号 `024-source-relation`。

同源决定：event 23，同一header索引/CSV提取生成分支读取ad_group字段；event39统一修订数组分支。 本表点：interest_category, languages, budget, age_groups_parser；编号 `024-csv-parser`。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共1条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引10（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 诊断 `agent实际类型`：`records/024_diagnostics.json` 数组索引20（从0开始）。

- 诊断 `agent有限差异样例`：`records/024_diagnostics.json` 数组索引21（从0开始）。

- 诊断 `gold实际类型`：`records/024_diagnostics.json` 数组索引22（从0开始）。

- 诊断 `gold有限差异样例`：`records/024_diagnostics.json` 数组索引23（从0开始）。

- 诊断 `gold SQL同gold输入重跑`：`records/024_diagnostics.json` 数组索引30（从0开始）。

## 点：source_relation

类别：**Unstated Choice**；角色：并列；把握：中。

契约未定来源标识粒度：平台tiktok_ads还是各raw表名。它影响后续跨表对应，不只是同标签换拼法。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-024_stg_tiktok_ads__ad_group_history.json`，条目 `source_relation`。

基线：L0=2504行/7512格; L1=2504行/7512格; L2=2504行/7512格; L3=2504行/7512格。

单改后：L0=2504行/5008格; L1=2504行/5008格; L2=2504行/5008格; L3=2504行/5008格。L0减量（先行后格）：0行/2504格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "'tiktok_ads' as source_relation",
    "new": "'raw.tiktok_adgroup_history_data' as source_relation",
    "offset": 1139
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
      source_table: raw.tiktok_adgroup_history_data
      columns:
        - name: source_relation
          data_type: VARCHAR
        - name: ad_group_id
          data_type: VARCHAR
        - name: updated_at
          data_type: TIMESTAMP
          validation_rules:
            - rule: "updated_at is a valid timestamp"
              on_failure: nullify_field
        - name: advertiser_id
          data_type: VARCHAR
        - name: campaign_id
          data_type: VARCHAR
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `024-gen-staging`；根源决定单元 `024-source-relation`。

## 点：interest_category

类别：**其他**；角色：非原因；把握：高。

原始header将INTEREST_CATEGORY_V_2放在59位；agent按header取列，gold读56位AUDIENCE。来源列证据而非gold选择确定含义。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-024_stg_tiktok_ads__ad_group_history.json`，条目 `interest_category`。

基线：L0=2504行/7512格; L1=2504行/7512格; L2=2504行/7512格; L3=2504行/7512格。

单改后：L0=2504行/7512格; L1=2504行/7512格; L2=2504行/7512格; L3=2504行/7512格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "cast(trim(both '\"' from replace(list_extract(regexp_extract_all(record, '(^|,)(\"(?:[^\"]|\"\")*\"|\\[[^\\]]*\\]|[^,]*)', 2), 59), '\"\"', '\"')) as VARCHAR) as interest_category",
    "new": "split_part(record, ',', 56) as interest_category",
    "offset": 1885
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第3档——过程中意识到了，交付物里没提**。event19实际比较正则分割与string_split，event39改写数组解析分支，显示对共同解析问题有替代方案意识；交付报告没有解释这一处。组级意识只覆盖CSV提取点，不推广来源常量。

event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
for q in ["select regexp_extract_all(?, '(^|,)(\"(?:[^\"]|\"\")*\"|[^,]*)', 2)","select string_split(?, ',')"]:
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
        - name: campaign_id
          data_type: VARCHAR
        - name: interest_category
          data_type: VARCHAR
        - name: ad_group_name
          data_type: VARCHAR
        - name: frequency
          data_type: VARCHAR
        - name: frequency_schedule
          data_type: VARCHAR
        - name: age_groups
          data_type: VARCHAR
        - name: languages
          data_type: VARCHAR
        - name: gender
```


共同生成动作 `024-gen-staging`；根源决定单元 `024-csv-parser`。

## 点：languages

类别：**其他**；角色：非原因；把握：高。

原始header的LANGUAGES位于65，agent按该位置；gold的67是NETWORK_TYPES。差异不由agent误读源列造成。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-024_stg_tiktok_ads__ad_group_history.json`，条目 `languages`。

基线：L0=2504行/7512格; L1=2504行/7512格; L2=2504行/7512格; L3=2504行/7512格。

单改后：L0=2504行/7512格; L1=2504行/7512格; L2=2504行/7512格; L3=2504行/7512格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "cast(trim(both '\"' from replace(list_extract(regexp_extract_all(record, '(^|,)(\"(?:[^\"]|\"\")*\"|\\[[^\\]]*\\]|[^,]*)', 2), 65), '\"\"', '\"')) as VARCHAR) as languages",
    "new": "split_part(record, ',', 67) as languages",
    "offset": 2751
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第3档——过程中意识到了，交付物里没提**。event19实际比较正则分割与string_split，event39改写数组解析分支，显示对共同解析问题有替代方案意识；交付报告没有解释这一处。组级意识只覆盖CSV提取点，不推广来源常量。

event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
for q in ["select regexp_extract_all(?, '(^|,)(\"(?:[^\"]|\"\")*\"|[^,]*)', 2)","select string_split(?, ',')"]:
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
        - name: age_groups
          data_type: VARCHAR
        - name: languages
          data_type: VARCHAR
        - name: gender
          data_type: VARCHAR
        - name: budget_mode
          data_type: VARCHAR
        - name: budget
          data_type: DOUBLE
          validation_rules:
            - rule: "budget is numeric"
              on_failure: nullify_field
        - name: landing_page_url
          data_type: VARCHAR
```


共同生成动作 `024-gen-staging`；根源决定单元 `024-csv-parser`。

## 点：budget

类别：**其他**；角色：并列；把握：高。

header的BUDGET为39位，gold读取38位FALLBACK_TYPE；agent按明确列名取预算并遵循numeric校验。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-024_stg_tiktok_ads__ad_group_history.json`，条目 `budget`。

基线：L0=2504行/7512格; L1=2504行/7512格; L2=2504行/7512格; L3=2504行/7512格。

单改后：L0=2504行/5008格; L1=2504行/5008格; L2=2504行/5008格; L3=2504行/5008格。L0减量（先行后格）：0行/2504格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(nullif(trim(trim(both '\"' from replace(list_extract(regexp_extract_all(record, '(^|,)(\"(?:[^\"]|\"\")*\"|\\[[^\\]]*\\]|[^,]*)', 2), 39), '\"\"', '\"'))), '') as DOUBLE) as budget",
    "new": "try_cast(split_part(record, ',', 38) as DOUBLE) as budget",
    "offset": 3257
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。报告的try_cast通用说明只覆盖转换，不覆盖本点BUDGET与FALLBACK_TYPE的取列差异；不把转换声明算成来源选择的披露。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
          data_type: DOUBLE
          validation_rules:
            - rule: "budget is numeric"
              on_failure: nullify_field
        - name: landing_page_url
          data_type: VARCHAR
        - name: secondary_optimization_event
          data_type: VARCHAR
        - name: creative_material_mode
          data_type: VARCHAR
        - name: audience_type
          data_type: VARCHAR
        - name: is_most_recent_record
          data_type: BOOLEAN
          validation_rules:
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `024-gen-staging`；根源决定单元 `024-csv-parser`。

## 点：age_groups_parser

类别：**Unstated Choice**；角色：并列；把握：中。

原始AGE_GROUPS含引号及内部逗号；契约只要求VARCHAR，未定解析/序列化写法。agent保留完整数组字符串，gold逗号切割截断；不把gold失败当作数据事实。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_supplement_reruns_impl-024_stg_tiktok_ads__ad_group_history.json`，条目 `age_groups_parser`。

基线：L0=2504行/7512格; L1=2504行/7512格; L2=2504行/7512格; L3=2504行/7512格。

单改后：L0=2504行/5008格; L1=2504行/5008格; L2=2504行/5008格; L3=2504行/5008格。L0减量（先行后格）：0行/2504格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "cast(trim(both '\"' from replace(list_extract(regexp_extract_all(record, '(^|,)(\"(?:[^\"]|\"\")*\"|\\[[^\\]]*\\]|[^,]*)', 2), 64), '\"\"', '\"')) as VARCHAR) as age_groups",
    "new": "split_part(record, ',', 64) as age_groups",
    "offset": 2581
  }
]
```

是否说出：**第3档——过程中意识到了，交付物里没提**。event19实际比较正则分割与string_split，event39改写数组解析分支，显示对共同解析问题有替代方案意识；交付报告没有解释这一处。组级意识只覆盖CSV提取点，不推广来源常量。

event 19 / `args.command`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
for q in ["select regexp_extract_all(?, '(^|,)(\"(?:[^\"]|\"\")*\"|[^,]*)', 2)","select string_split(?, ',')"]:
```

契约／过程证据（与上段重复的引句略）：

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/output.jsonl`：

```text
        - name: frequency_schedule
          data_type: VARCHAR
        - name: age_groups
          data_type: VARCHAR
        - name: languages
          data_type: VARCHAR
        - name: gender
          data_type: VARCHAR
        - name: budget_mode
          data_type: VARCHAR
        - name: budget
          data_type: DOUBLE
          validation_rules:
            - rule: "budget is numeric"
              on_failure: nullify_field
```


共同生成动作 `024-gen-staging`；根源决定单元 `024-csv-parser`。

## 规则问题与限制

- age_groups_parser：原始AGE_GROUPS含引号及内部逗号；契约只要求VARCHAR，未定解析/序列化写法。agent保留完整数组字符串，gold逗号切割截断；不把gold失败当作数据事实。
