# 040 校准：impl-027_int_xero__invoice_line_items_enriched

## 任务

按冻结v3.2第3～8节盲标；层：intermediate。本说明来自封存结果，没有用036改写结论。

## 结论

主要原因：**其他**；把握高；共1点；不是只能组合修复。

## 详细发现

### 判断顺序与范围

先检查契约、交付SQL及单改结果，排除代码意图错误、raw版本差异及gold与契约不一致。未采用领域惯例补出未写明的规则。主因按L0含评测键全表行规模优先、格子规模次之；L1～L3仅辅助定位，不跨口径排序。

### account_code去重满足line_item_id唯一性

主要；**其他**；把握高。

契约明确One row per line_item_id及unique；agent输出5000行满足唯一性，gold5209行多209行。去掉account_by_code的QUALIFY后与gold在L0–L3完全一致，证明差异来源；按第6节属于标准答案与唯一性规格不一致。

是否说出：第1档——交付物里针对本处说明了。finish明确点名invoice enrichment并说明按最低account_id去重及舍弃其他属性的影响。

证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 209 | 0 | 4807 | 0 |
| L1 | 209 | 0 | 4807 | 0 |
| L2 | 209 | 0 | 4807 | 0 |
| L3 | 209 | 0 | 4807 | 0 |



单改来源：`records/022_reruns_impl-027_int_xero__invoice_line_items_enriched.json` / `account_duplicates`。L0减少209行、4807格；不同单改收益不相加。

原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-027/agent/.events/sessions/53adbf82-e9e9-44-234a6229b6699d5/events/41.json` / `args.final_thought` / event 41

```text

Duplicate account codes exist in source; the invoice enrichment chooses one account deterministically by lowest `account_id` to prevent duplicate output line rows. This can discard alternate account attributes for colliding codes.

```

原句：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql` / `text`

```text

QUALIFY row_number() OVER (PARTITION BY account_code ORDER BY account_id) = 1

```

核实证据：`records/017_queries_impl-027.json#V2`。

### 契约依据

完整契约原文已在`records/012_packages/012_impl-027_intermediate_int_xero__invoice_line_items_enriched.json`核对到`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-027/docs/data_contract.yaml`；SHA-256 `61ecf2358ccdfd717fb69bc6c6a6b5336ef7eae90ca5bb486aaae106afa5a9c9`。

契约原句：`Unique identifier for the invoice line item; exactly one output row per value`。gold直接JOIN的多重性不符合这里的唯一粒度；移除去重用于定位差异，不表示agent应当复制gold的行数。

## 证据来源

- 材料包：`records/012_packages/012_impl-027_intermediate_int_xero__invoice_line_items_enriched.json`。

- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-027/agent/dacomp-de-impl-027/sql/intermediate/int_xero__invoice_line_items_enriched.sql`；SHA-256 `60f138a9ab8273d7ab5d23b13fbdcefde6237f7b2c9e14169f87b8cb3066ce6c`。

- `records/040_calibration_blind_sealed.json`、`records/040_calibration_comparison.json`、`records/040_checks/quote_checks.json`。

- Google Ads复用014 V1及016 V1/V2共3条；Xero实际证据用017 V2，保守把已读V1失败也算入为2条。封存件verification_query_count记录成功采用数，原件不改。

- 本阶段没有新执行数据库查询或重跑；Google Ads复用022的agent留存raw，Xero复用CS gold上游；执行路径与clock_control见各重跑JSON。

## 不确定或没查到的（含规则问题）

- 未发现需要修改手册的规则问题；没有因为gold结果不同而补出唯一业务规则。

- 去重可能舍弃其他账户属性；交付报告已针对invoice enrichment说明。当前判错差异仅由209条重复行解释。

## 建议的下一步

保留该校准结果和封存hash，在同一会话继续38张正式表；不把本阶段2张校准误作40张完成。
