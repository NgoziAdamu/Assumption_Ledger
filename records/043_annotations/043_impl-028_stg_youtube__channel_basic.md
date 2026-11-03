# 043：impl-028_stg_youtube__channel_basic

## 结论

主要原因：**不可评估**；把握：高；只能组合修复：否。

不进行机制归因或五档统计。

层：staging。024旧主要原因原样保留：`不可评估`；旧标签不用于判类。

## 材料与输入

契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-028/docs/data_contract.yaml`。相关块完整出现在event1，逐表hash见 `records/043_checks/formal_material_audit.json`。

交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-028/agent/dacomp-de-impl-028/sql/staging/stg_youtube__channel_basic.sql`；无SQL注释。材料包：`records/024_packages/024_impl-028_stg_youtube__channel_basic.md`。

agent留存与initial直接raw内容差集为0；gold读取另一组名称、schema和行数不同的raw。按第6节不可评估；不将此结论推广到int_youtube__video。

已逐张读取 `records/013_raw_impl-028.json`；与gold关系见 `records/015_raw_impl-028.json`、`records/043_checks/raw_integrity_review.json`。

- `raw.youtube_channel_basic_data`：initial 3500行/35列；agent留存 3500行/35列；013差异=False。

## 同源决定

同源决定：event 25，`event25 shell heredoc批量写SQL`：同一命令写两个正式staging，event27另作修订；原始输入与gold不同，不建立错误点或因果计数。 目录编号：`028-staging-command`。共同脚本覆盖本表全部点；不改变逐点类别和排序。

全批共同脚本、同规则成员及按根源计的统计见 `records/043_checks/shared_root_decisions.json`。

## 核实与诊断

核实查询共1条，全部复用，未新查数据库或重跑。每表上限5条，诊断另列。

- 核实 `直接raw列名类型`：`records/024_queries.json` 数组索引30（从0开始）；SQL及结果原样见 `formal_query_inventory.json`。

- 诊断 `initial_database直接原始表规模`：`records/024_queries.json` 数组索引31（从0开始）。

- 诊断 `agent_database直接原始表规模`：`records/024_queries.json` 数组索引32（从0开始）。

- 诊断 `gold实际raw表清单`：`records/024_queries.json` 数组索引33（从0开始）。

- 诊断 `initial-agent逐值差集`：`records/024_queries.json` 数组索引34（从0开始）。

gold raw名为channel_basic_a_2/channel_demographics_a_1/video；agent/initial名为youtube_channel_basic_data/youtube_channel_demographics_data/youtube_video_data。024诊断直接比较本表读取raw的agent与initial内容，差集为0；gold结构及行数不同。按第6节，不赋错误点、五档或主因排序；同题中间层按CS另行标注。

## 规则问题与限制

无新增未覆盖情形；上述把握与证据限制照实保留。
