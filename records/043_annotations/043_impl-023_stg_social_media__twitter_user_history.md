# 043：impl-023_stg_social_media__twitter_user_history

## 结论

主要原因：**其他**；把握：高；只能组合修复：否。

先比行减量，再比格减量；最大减量为1行/87格。行增多时即使格减少也不作为改善。

层：staging。024旧主要原因原样保留：`O`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-023/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-023/agent/dacomp-de-impl-023/sql/staging/stg_social_media__twitter_user_history.sql`；无SQL注释。材料包：`records/024_packages/024_impl-023_stg_social_media__twitter_user_history.md`。

staging采用agent留存raw；013直接源对照逐项列出。

已逐张读取 `records/013_raw_impl-023.json`；与gold关系见 `records/015_raw_impl-023.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.twitter_user_history`：initial 2500行/31列；agent留存 2500行/31列；013差异=False。

## 同源决定

同源决定：event 29,31,33，`/tmp/write_sql.py`：同一files字典脚本分三次写入staging、中间层、marts；各表表达式分别定义。 目录编号：`023-write-sql`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共2条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引6（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 核实 `有害字符与全局替换差异`：`records/024_queries.json` 数组索引7（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 诊断 `agent实际类型`：`records/024_diagnostics.json` 数组索引8（从0开始）。

- 诊断 `agent有限差异样例`：`records/024_diagnostics.json` 数组索引9（从0开始）。

- 诊断 `gold实际类型`：`records/024_diagnostics.json` 数组索引10（从0开始）。

- 诊断 `gold有限差异样例`：`records/024_diagnostics.json` 数组索引11（从0开始）。

- 诊断 `gold SQL同gold输入重跑`：`records/024_diagnostics.json` 数组索引32（从0开始）。

## 点：screen_regex

类别：**Intent Misreading**；角色：非原因；把握：高。

契约给出可执行REGEXP_REPLACE且无g，agent添加全局替换；按字面表达式而非推测清洗本意。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-023_stg_social_media__twitter_user_history.json`，条目 `screen_regex`。

基线：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。

单改后：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "regexp_replace(screen_name, '[^A-Za-z0-9_]', '', 'g')",
    "new": "regexp_replace(screen_name, '[^A-Za-z0-9_]', '')",
    "offset": 221
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
            Best-effort cleaning to keep only [A-Za-z0-9_]; rows with NULL/blank or harmful characters are removed.
          validation_rules:
            - rule: "screen_name = CASE WHEN screen_name IS NULL OR TRIM(screen_name) = '' THEN NULL ELSE REGEXP_REPLACE(screen_name, '[^A-Za-z0-9_]', '') END"
              on_failure: correct
            - rule: "screen_name IS NOT NULL AND NOT (screen_name RLIKE '[!@#$%^&*()+=<>?}{|,]')"
              on_failure: delete_row
        - name: url
          data_type: VARCHAR
          validation_rules:
            - rule: "url IS NULL OR url RLIKE '^https?://[A-Za-z0-9.-]+\\.[A-Za-z]{2,}(/.*)?'"
              on_failure: nullify_field
            - rule: "url IS NULL OR (url RLIKE '^(https?://)?[A-Za-z0-9.-]+\\.[A-Za-z]{2,}(/.*)?' AND url RLIKE '^https?://')"
              on_failure: correct
        - name: created_at
          data_type: TIMESTAMP
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_user_history:screen_regex`。

## 点：harmful_filter

类别：**Intent Misreading**；角色：非原因；把握：中。

契约描述含有害字符的行删除；agent先全部清洗后保留，未保留原值删除检查。规则先后有另一读法，列入规则问题。

证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。

决定规则在event1完整契约块内；原句如下。逐步轨迹未发现本点曾先按正确规则实现的证据，故曾经理解对过填否。

证据：`records/024_reruns_impl-023_stg_social_media__twitter_user_history.json`，条目 `harmful_filter`。

基线：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。

单改后：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "from raw.twitter_user_history",
    "new": "from raw.twitter_user_history where NOT REGEXP_MATCHES(screen_name, '[!@#$%^&*()+=<>?}{|,]')",
    "offset": 1314
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
          constraints: [not_null]
          description: >
            Best-effort cleaning to keep only [A-Za-z0-9_]; rows with NULL/blank or harmful characters are removed.
          validation_rules:
            - rule: "screen_name = CASE WHEN screen_name IS NULL OR TRIM(screen_name) = '' THEN NULL ELSE REGEXP_REPLACE(screen_name, '[^A-Za-z0-9_]', '') END"
              on_failure: correct
            - rule: "screen_name IS NOT NULL AND NOT (screen_name RLIKE '[!@#$%^&*()+=<>?}{|,]')"
              on_failure: delete_row
        - name: url
          data_type: VARCHAR
          validation_rules:
            - rule: "url IS NULL OR url RLIKE '^https?://[A-Za-z0-9.-]+\\.[A-Za-z]{2,}(/.*)?'"
              on_failure: nullify_field
            - rule: "url IS NULL OR (url RLIKE '^(https?://)?[A-Za-z0-9.-]+\\.[A-Za-z]{2,}(/.*)?' AND url RLIKE '^https?://')"
              on_failure: correct
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_user_history:harmful_filter`。

## 点：empty_filter

类别：**其他**；角色：非原因；把握：中。

契约描述NULL/blank行删除；agent排除清洗后空串有自然读法支持。gold保留不构成agent未确立的错误前提；先后边界记中把握。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_reruns_impl-023_stg_social_media__twitter_user_history.json`，条目 `empty_filter`。

基线：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。

单改后：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "  and screen_name <> '' ",
    "new": "",
    "offset": 1424
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
          constraints: [not_null]
          description: >
            Best-effort cleaning to keep only [A-Za-z0-9_]; rows with NULL/blank or harmful characters are removed.
          validation_rules:
            - rule: "screen_name = CASE WHEN screen_name IS NULL OR TRIM(screen_name) = '' THEN NULL ELSE REGEXP_REPLACE(screen_name, '[^A-Za-z0-9_]', '') END"
              on_failure: correct
            - rule: "screen_name IS NOT NULL AND NOT (screen_name RLIKE '[!@#$%^&*()+=<>?}{|,]')"
              on_failure: delete_row
        - name: url
          data_type: VARCHAR
          validation_rules:
            - rule: "url IS NULL OR url RLIKE '^https?://[A-Za-z0-9.-]+\\.[A-Za-z]{2,}(/.*)?'"
              on_failure: nullify_field
            - rule: "url IS NULL OR (url RLIKE '^(https?://)?[A-Za-z0-9.-]+\\.[A-Za-z]{2,}(/.*)?' AND url RLIKE '^https?://')"
              on_failure: correct
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_user_history:empty_filter`。

## 点：id_projection

类别：**其他**；角色：主要；把握：高。

id要求BIGINT，gold保留非数值文本，agent类型符合规格。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_supplement_reruns_impl-023_stg_social_media__twitter_user_history.json`，条目 `id_projection`。

基线：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。

单改后：L0=11行/93格; L1=9行/84格; L2=9行/84格; L3=9行/84格。L0减量（先行后格）：1行/87格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(id as bigint) as id",
    "new": "id as id",
    "offset": 42
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
      source_table: raw.twitter_user_history
      columns:
        - name: id
          data_type: BIGINT
          constraints: [not_null]
        - name: _fivetran_synced
          data_type: TIMESTAMP
        - name: screen_name
          data_type: VARCHAR
          constraints: [not_null]
          description: >
            Best-effort cleaning to keep only [A-Za-z0-9_]; rows with NULL/blank or harmful characters are removed.
          validation_rules:
            - rule: "screen_name = CASE WHEN screen_name IS NULL OR TRIM(screen_name) = '' THEN NULL ELSE REGEXP_REPLACE(screen_name, '[^A-Za-z0-9_]', '') END"
              on_failure: correct
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_user_history:id_projection`。

## 点：id_filter

类别：**其他**；角色：非原因；把握：高。

id明确not_null，转换失败后排除符合规格；单改放行反而增差。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_supplement_reruns_impl-023_stg_social_media__twitter_user_history.json`，条目 `id_filter`。

基线：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。

单改后：L0=28行/436格; L1=27行/432格; L2=27行/432格; L3=27行/432格。L0减量（先行后格）：-16行/-256格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "where id is not null",
    "new": "where true",
    "offset": 1373
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: id
          data_type: BIGINT
          constraints: [not_null]
        - name: _fivetran_synced
          data_type: TIMESTAMP
        - name: screen_name
          data_type: VARCHAR
          constraints: [not_null]
          description: >
            Best-effort cleaning to keep only [A-Za-z0-9_]; rows with NULL/blank or harmful characters are removed.
          validation_rules:
            - rule: "screen_name = CASE WHEN screen_name IS NULL OR TRIM(screen_name) = '' THEN NULL ELSE REGEXP_REPLACE(screen_name, '[^A-Za-z0-9_]', '') END"
              on_failure: correct
            - rule: "screen_name IS NOT NULL AND NOT (screen_name RLIKE '[!@#$%^&*()+=<>?}{|,]')"
              on_failure: delete_row
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_user_history:id_filter`。

## 点：type_followers_count

类别：**其他**；角色：参与；把握：高。

followers_count契约为BIGINT，agent按类型转换，gold保留DOUBLE；不是只凭gold值定义应输出什么。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_supplement_reruns_impl-023_stg_social_media__twitter_user_history.json`，条目 `type_followers_count`。

基线：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。

单改后：L0=12行/179格; L1=11行/176格; L2=11行/176格; L3=11行/176格。L0减量（先行后格）：0行/1格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(followers_count as bigint) as followers_count",
    "new": "followers_count as followers_count",
    "offset": 631
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: created_at
          data_type: TIMESTAMP
        - name: followers_count
          data_type: BIGINT
        - name: following_count
          data_type: BIGINT
          description: "Renamed from friends_count."
        - name: listed_count
          data_type: BIGINT
        - name: favourites_count
          data_type: BIGINT
        - name: statuses_count
          data_type: BIGINT
        - name: verified
          data_type: BOOLEAN
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_user_history:type_followers_count`。

## 点：type_following_count

类别：**其他**；角色：参与；把握：高。

following_count契约为BIGINT，agent按类型转换，gold保留DOUBLE；不是只凭gold值定义应输出什么。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_supplement_reruns_impl-023_stg_social_media__twitter_user_history.json`，条目 `type_following_count`。

基线：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。

单改后：L0=12行/179格; L1=11行/176格; L2=11行/176格; L3=11行/176格。L0减量（先行后格）：0行/1格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(friends_count as bigint) as following_count",
    "new": "friends_count as following_count",
    "offset": 695
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: followers_count
          data_type: BIGINT
        - name: following_count
          data_type: BIGINT
          description: "Renamed from friends_count."
        - name: listed_count
          data_type: BIGINT
        - name: favourites_count
          data_type: BIGINT
        - name: statuses_count
          data_type: BIGINT
        - name: verified
          data_type: BOOLEAN
        - name: protected
          data_type: BOOLEAN
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_user_history:type_following_count`。

## 点：type_listed_count

类别：**其他**；角色：非原因；把握：高。

listed_count契约为BIGINT，agent按类型转换，gold保留DOUBLE；不是只凭gold值定义应输出什么。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_supplement_reruns_impl-023_stg_social_media__twitter_user_history.json`，条目 `type_listed_count`。

基线：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。

单改后：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。L0减量（先行后格）：0行/0格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(listed_count as bigint) as listed_count",
    "new": "listed_count as listed_count",
    "offset": 757
  }
]
```

本处单改不改善按行、格排序的规模；存在未落实规则/未确立前提时保留该点，但不是本次判错原因，不计参与因素。其他类点不因此变成前提错误。

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
          data_type: BIGINT
          description: "Renamed from friends_count."
        - name: listed_count
          data_type: BIGINT
        - name: favourites_count
          data_type: BIGINT
        - name: statuses_count
          data_type: BIGINT
        - name: verified
          data_type: BOOLEAN
        - name: protected
          data_type: BOOLEAN
          description: "Derived from protected_user: TRUE if protected_user=TRUE else FALSE."
        - name: default_profile
          data_type: BOOLEAN
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_user_history:type_listed_count`。

## 点：type_favourites_count

类别：**其他**；角色：参与；把握：高。

favourites_count契约为BIGINT，agent按类型转换，gold保留DOUBLE；不是只凭gold值定义应输出什么。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_supplement_reruns_impl-023_stg_social_media__twitter_user_history.json`，条目 `type_favourites_count`。

基线：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。

单改后：L0=12行/179格; L1=11行/176格; L2=11行/176格; L3=11行/176格。L0减量（先行后格）：0行/1格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(favourites_count as bigint) as favourites_count",
    "new": "favourites_count as favourites_count",
    "offset": 815
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: listed_count
          data_type: BIGINT
        - name: favourites_count
          data_type: BIGINT
        - name: statuses_count
          data_type: BIGINT
        - name: verified
          data_type: BOOLEAN
        - name: protected
          data_type: BOOLEAN
          description: "Derived from protected_user: TRUE if protected_user=TRUE else FALSE."
        - name: default_profile
          data_type: BOOLEAN
        - name: default_profile_image
          data_type: BOOLEAN
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_user_history:type_favourites_count`。

## 点：type_statuses_count

类别：**其他**；角色：参与；把握：高。

statuses_count契约为BIGINT，agent按类型转换，gold保留DOUBLE；不是只凭gold值定义应输出什么。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

证据：`records/024_supplement_reruns_impl-023_stg_social_media__twitter_user_history.json`，条目 `type_statuses_count`。

基线：L0=12行/180格; L1=11行/176格; L2=11行/176格; L3=11行/176格。

单改后：L0=12行/179格; L1=11行/176格; L2=11行/176格; L3=11行/176格。L0减量（先行后格）：0行/1格。

单改替换（除此之外不变；复用024重跑记录）：

```json
[
  {
    "old": "try_cast(statuses_count as bigint) as statuses_count",
    "new": "statuses_count as statuses_count",
    "offset": 881
  }
]
```

是否说出：**第4档——看到了相关信息，但没有意识到的迹象**。相关契约已完整出现在event1；最终报告及交付SQL未针对本点说明疑问、替代或取舍。写出实现不是第3档意识证据。

event 1 / `args.content`，来源 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-023/agent/output.jsonl`：

```text
        - name: favourites_count
          data_type: BIGINT
        - name: statuses_count
          data_type: BIGINT
        - name: verified
          data_type: BOOLEAN
        - name: protected
          data_type: BOOLEAN
          description: "Derived from protected_user: TRUE if protected_user=TRUE else FALSE."
        - name: default_profile
          data_type: BOOLEAN
        - name: default_profile_image
          data_type: BOOLEAN
        - name: location
          data_type: VARCHAR
```

契约／过程证据（与上段重复的引句略）：


共同生成动作 `023-write-sql`；根源决定单元 `impl-023_stg_social_media__twitter_user_history:type_statuses_count`。

## 规则问题与限制

- harmful_filter：契约描述含有害字符的行删除；agent先全部清洗后保留，未保留原值删除检查。规则先后有另一读法，列入规则问题。
- empty_filter：契约描述NULL/blank行删除；agent排除清洗后空串有自然读法支持。gold保留不构成agent未确立的错误前提；先后边界记中把握。
