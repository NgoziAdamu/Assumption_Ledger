# 042 校准标注：impl-009_stg_google_play__store_performance_country

## 任务

按冻结v3.2第3～8节盲标、封存后解盲。此说明为解盲后校准定稿；盲标原件不改。

## 结论

主要原因：**Unstated Choice**；把握中；2个点。不是只能组合修复。023旧主要原因 `A` 只存档，不作分类依据。

## 详细发现

盲标主因：其他。解盲后变动：盲标将country编码看作形式未规定；解盲复核后改为Unstated Choice。该投影通过lookup选择输出键值，014查询V2显示同一numeric码有多个alpha-2候选，不能证明所有输出仅是同一内容的另一种呈现；不满足第3节只改呈现的前提。契约没有指定country编码及映射策略，故按材料没定的映射选择处理。扩行的唯一性前提仍独立归Data Misconception。不以036标签本身作证据；两种读法保留为规则问题。

先排除代码写错、非agent处理原因与raw版本不同；本表复用staging agent留存raw的重跑。逐点区分纯形式、占位替代、契约明定算法和未定选择；不把gold实现当契约。按行减量优先，行数相同再比格子；不同单改减量不相加。

### country_value_only：country表示使用alpha-2而非numeric文本

主要；**Unstated Choice**；把握中。

盲标将country编码看作形式未规定；解盲复核后改为Unstated Choice。该投影通过lookup选择输出键值，014查询V2显示同一numeric码有多个alpha-2候选，不能证明所有输出仅是同一内容的另一种呈现；不满足第3节只改呈现的前提。契约没有指定country编码及映射策略，故按材料没定的映射选择处理。扩行的唯一性前提仍独立归Data Misconception。不以036标签本身作证据；两种读法保留为规则问题。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event67只称处理国家码，并未说明此处编码选择；不是该差异的通用解释。event15直接选择alpha-2，未见比较或疑问。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 15200 | 2400 | 91200 | 14400 |

| L1 | 15200 | 2400 | 91200 | 14400 |

| L2 | 15200 | 2400 | 91200 | 14400 |

| L3 | 15200 | 2400 | 91200 | 14400 |

来源 `records/016_reruns_impl-009.json` / `country_value_only`；L0减少12800行/76800格。

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/15.json` / event 15 / `args.command`。

```text
elif n=='country' and name=='stg_google_play__store_performance_country': expr='cc.country_code_alpha_2'
```

### lookup_dedup：国家码lookup默认numeric键唯一导致扩行

参与；**Data Misconception**；把握高。

014查询V2明确124/156/250/276各有两行，源中156/250/276有数据，join从6400扩到8800。契约未规定此join算法。

P：raw.google_play__country_codes中的country_code_numeric对源记录最多匹配一行。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。event14看到维表schema和一行样例，但没有numeric键唯一性统计或意识到冲突的迹象。

证据在场：否。一行样例不能证明numeric键不唯一；未找到重复键统计出现在轨迹中。

曾经理解对过：否。系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 15200 | 12800 | 91200 | 76800 |

| L1 | 15200 | 12800 | 91200 | 76800 |

| L2 | 15200 | 12800 | 91200 | 76800 |

| L3 | 15200 | 12800 | 91200 | 76800 |

来源 `records/016_reruns_impl-009.json` / `unique_lookup`；L0减少2400行/14400格。

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/.events/sessions/7564fe9b-59a3-44-5483969dccf9623/events/14.json` / event 14 / `content`。

```text
('United States', 'United States', 840, 'US', 'USA', 'Americas', 19, 'Northern America', 21)
```

核实查询：records/014_queries_impl-009.json#V1；records/014_queries_impl-009.json#V2。

最终报告的相关完成陈述：

```text
staging 做了基础字段投影及类型转换，并处理日期、币种、国家码和合同中明确的部分校验。
```

这句话没有说明此表选择哪种country码，也未说明lookup的非唯一性；不作第1或第2档依据。交付SQL无注释。

## 证据来源

- `records/013_packages/013_impl-009_staging_stg_google_play__store_performance_country.md`

- `records/014_trace_impl-009.json`

- `records/016_reruns_impl-009.json`

- `records/014_queries_impl-009.json`

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-009/docs/data_contract.yaml`，SHA-256 `ed3e3a4a943b8504299100aa6acd2684c9371bb8a4ddeaa2eca7a1ebc8c32494`。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-009/agent/dacomp-de-impl-009/sql/staging/stg_google_play__store_performance_country.sql`，SHA-256 `52c299334f985027ac5c9f9bbc0be0f8f76f78b2da858fe65f68521477775ec5`。

- 原文引用核验：`records/042_checks/quote_checks.json`；盲标/解盲：`records/042_calibration_blind_sealed.json`、`records/042_calibration_comparison.json`。

- 未新开数据库/新查询/重跑。保守计已读重复核实查询为3条（Google Play封存件采用V1/V2两条，另已读相同SQL的V3计入预算）。

## 不确定或没查到的（含规则问题）

国家码映射可读作表示格式，也可读作生成键值的选择。盲标采用前者，解盲复核后采用后者：未证明lookup映射的语义等价，不满足只改呈现条件。正式口径保留Choice，供用户与Claude复核，不改手册。

## 建议的下一步

校准定稿保留；在同一会话继续39张正式表。阶段二保护封存件、解盲对比和本校准定稿，不重新盲标。
