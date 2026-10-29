# impl-003 / customer360__mapping

## 结论

主要原因：**C**；把握：高；标记：无。

契约明确 full outer join 后还 union unmatched；agent left join 少了第一批 unmatched。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**只有通用策略说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-003_customer360__mapping.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：12160/18036。本次固定控制下 baseline 行/格规模：6515/41771。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`；原文行段 1820–1874。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__mapping.sql`，L1–39；SHA-256 `2eb09f66fc2b34dea30da9094448c2e91c14fd968fe4bf62dc0df9038e6bc5ec`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__mapping.sql`，L1–214；SHA-256 `0afee54bf7930332741f3fe055cd4ac0e989d14dd24730c113f277042be06c8e`。

outer_source：agent SQL L1，替换原片段如下。
```sql

 select sm.marketo_lead_id, sm.stripe_customer_id, sm.zendesk_user_id,
        m.organization_name_no_suffix as m_org, m.inferred_organization_name_no_suffix as mi_org,
        s.customer_organization_name_no_suffix as s_org, s.shipping_organization_name_no_suffix as ss_org,
        z.organization_id, sm.marketo_updated_at, sm.marketo_created_at, sm.stripe_updated_at, sm.stripe_created_at,
        sm.zendesk_updated_at, sm.zendesk_organization_updated_at, sm.zendesk_created_at, sm.zendesk_organization_created_at
 from intermediate.int_customer360__source_matches sm
 left join intermediate.int_customer360__marketo m on sm.marketo_lead_id=m.lead_id
 left join intermediate.int_customer360__stripe s on sm.stripe_customer_id=s.customer_id
 left join intermediate.int_customer360__zendesk z on sm.zendesk_user_id=z.user_id

```
替换为：
```sql

 select coalesce(sm.marketo_lead_id,m.lead_id) marketo_lead_id, coalesce(sm.stripe_customer_id,s.customer_id) stripe_customer_id, coalesce(sm.zendesk_user_id,z.user_id) zendesk_user_id,
        m.organization_name_no_suffix as m_org, m.inferred_organization_name_no_suffix as mi_org,
        s.customer_organization_name_no_suffix as s_org, s.shipping_organization_name_no_suffix as ss_org,
        z.organization_id, coalesce(sm.marketo_updated_at,m.updated_at) marketo_updated_at, coalesce(sm.marketo_created_at,m.created_at) marketo_created_at, coalesce(sm.stripe_updated_at,s.updated_at) stripe_updated_at, coalesce(sm.stripe_created_at,s.created_at) stripe_created_at,
        coalesce(sm.zendesk_updated_at,z.updated_at) zendesk_updated_at, coalesce(sm.zendesk_organization_updated_at,z.organization_updated_at) zendesk_organization_updated_at, coalesce(sm.zendesk_created_at,z.created_at) zendesk_created_at, coalesce(sm.zendesk_organization_created_at,z.organization_created_at) zendesk_organization_created_at
 from intermediate.int_customer360__source_matches sm
 full outer join intermediate.int_customer360__marketo m on sm.marketo_lead_id=m.lead_id
 full outer join intermediate.int_customer360__stripe s on sm.stripe_customer_id=s.customer_id
 full outer join intermediate.int_customer360__zendesk z on sm.zendesk_user_id=z.user_id

```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-003_customer360__mapping.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 6515 | 41771 | {"source_ids": 639} | L0–L3均不匹配 |
| baseline | L1 | 6515 | 41771 | {"source_ids": 639} | L0–L3均不匹配 |
| baseline | L2 | 6515 | 41771 | {"source_ids": 639} | L0–L3均不匹配 |
| baseline | L3 | 6515 | 41771 | {"source_ids": 639} | L0–L3均不匹配 |
| outer_source | L0 | 663 | 663 | {"source_ids": 663} | L0–L3均不匹配 |
| outer_source | L1 | 663 | 663 | {"source_ids": 663} | L0–L3均不匹配 |
| outer_source | L2 | 663 | 663 | {"source_ids": 663} | L0–L3均不匹配 |
| outer_source | L3 | 663 | 663 | {"source_ids": 663} | L0–L3均不匹配 |

- outer_source（C，单处 SQL 改动）：行减少 5852，格减少 41108。契约明确 full outer join 后还 union unmatched；agent left join 少了第一批 unmatched。

## agent 可见证据及不确定性

event 51 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/51.json`，字段字符偏移 1027。

> 中间层按契约保留源业务数据的重复记录，不对 source IDs 做全局去重。下游按这些 ID 关联时，若上游相同 ID 对应多行，可能发生行数扩增；此项属于合同指定的重复保留行为。

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
