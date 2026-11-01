# impl-010_stg_hubspot__ticket_pipeline（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

**不可评估**。原始数据一致性诊断满足“初始库＝agent留存库≠标准答案库”，按第6节停止agent错因归类。没有逐点五档行。

## 详细发现

| raw表 | 初始行 | agent行 | gold行 | 初始/agent SHA-256 | gold SHA-256 |
|---|---:|---:|---:|---|---|
| raw.ticket_pipeline_data | 200 | 200 | 1033 | 2fb3d797201b0a5792f182c2b907de39eb1b69da1f0d0a056c044da1700dda0e | 7128d5113db8b4494a4db2d22914baf70a1b2de74e344d31d680e433d0e21e05 |

逐表内容hash及依赖路径：`records/039_checks/raw_integrity_review.json`；原诊断：`records/021_raw_diagnosis.json`（015序列化口径）。这不是仅凭行数不同推断。

025三张间接下游的上游在CS中换成标准答案，不能套用本表不可评估结论。

## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml`，行[528, 551]；材料包 `records/021_packages/021_impl-010_stg_hubspot__ticket_pipeline.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/staging/stg_hubspot__ticket_pipeline.sql`；SHA-256 `ae5730315c276d13df0d825c256dd9636271260a5b7e3feefb5e00bc021bd87b`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/73.json` / event 73。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共0条，新核实0条（总数≤5）。诊断/单改不计作核实查询：


## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
