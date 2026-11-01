# 042 校准标注：impl-024_stg_tiktok_ads__advertiser

## 任务

按冻结v3.2第3～8节盲标、封存后解盲。此说明为解盲后校准定稿；盲标原件不改。

## 结论

主要原因：**Unstated Choice**；把握中；1个点。不是只能组合修复。023旧主要原因 `A` 只存档，不作分类依据。

## 详细发现

盲标主因：Unstated Choice。解盲后变动：无

先排除代码写错、非agent处理原因与raw版本不同；本表复用staging agent留存raw的重跑。逐点区分纯形式、占位替代、契约明定算法和未定选择；不把gold实现当契约。按行减量优先，行数相同再比格子；不同单改减量不相加。

### email_pattern：email正则对连续点domain的接受边界

主要；**Unstated Choice**；把握中。

契约写standard pattern (local@domain.tld)，未给可执行正则。agent逐段域名正则比gold宽字符集严格，差异取决于未定正则边界；不以gold接受结果证明数据合法。

是否说出：第2档——交付物里只有通用说明。finish说明可选邮箱等验证失败置NULL，属于这类处理的通用说明，未说明连续点domain的边界。

证据在场：不适用。非探索类别不填。

曾经理解对过：不适用。系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |

|---|---:|---:|---:|---:|

| L0 | 1 | 0 | 1 | 0 |

| L1 | 1 | 0 | 1 | 0 |

| L2 | 1 | 0 | 1 | 0 |

| L3 | 1 | 0 | 1 | 0 |

来源 `records/017_reruns_impl-024.json` / `email_pattern`；L0减少1行/1格。

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/.events/sessions/06ab78b3-1c60-4e-ba8aaeb602afee5/events/63.json` / event 63 / `args.final_thought`。

```text
可选邮箱/名称/手机号字段验证失败时置 NULL，记录仍保留。
```

核实查询：records/017_queries_impl-024.json#V1。

## 证据来源

- `records/013_packages/013_impl-024_staging_stg_tiktok_ads__advertiser.md`

- `records/017_trace_impl-024.json`

- `records/017_reruns_impl-024.json`

- `records/017_queries_impl-024.json`

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-024/docs/data_contract.yaml`，SHA-256 `b43ee99b585f76719b935a1234dd0fbdd2fb975d72c8e2c5b393421e1b1fa8cb`。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-024/agent/dacomp-de-impl-024/sql/staging/stg_tiktok_ads__advertiser.sql`，SHA-256 `0fc81c8ecdcac4c1812c6b6a33de9a1866d1187c37c3a49fad45415833f00df0`。

- 原文引用核验：`records/042_checks/quote_checks.json`；盲标/解盲：`records/042_calibration_blind_sealed.json`、`records/042_calibration_comparison.json`。

- 未新开数据库/新查询/重跑。复用核实查询1条。

## 不确定或没查到的（含规则问题）

标准email pattern是否足以排除连续点domain，存在其他（gold与标准不一致）读法；本次未援引未经核实的领域标准，以契约未给正则归Choice。

## 建议的下一步

校准定稿保留；在同一会话继续39张正式表。阶段二保护封存件、解盲对比和本校准定稿，不重新盲标。
