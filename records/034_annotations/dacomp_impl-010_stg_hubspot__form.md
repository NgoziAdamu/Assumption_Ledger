# DAComp / impl-010_stg_hubspot__form（v3）

## 错在哪里
agent与gold使用不同form_data：前者1150个FORM_ ID，后者1150行/1142个数值ID，全部原始行不相同。

证据复用入口：[018_impl-010_stg_hubspot__form.md](../018_annotations/018_impl-010_stg_hubspot__form.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## raw_input_mismatch
- 角色：主要；类别：**不可评估**；把握：中。
- 依据：agent=初始raw，gold不同；1150个FORM_ ID与1142个数值ID的输出源数据不相交。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 14 / content：
```text
pe:VARCHAR, task_type:VARCHAR, property_hs_engagement_source:VARCHAR

form_data: guid:VARCHAR, portal_id:INTEGER, name:VARCHAR, form_type:VARCHAR, method:VARCHAR, action:VARCHAR, redirect:VARCHAR, lead_nurturing_campaign_id:VARCHAR, follow_up_id:VARCHAR, created_at:VARCHAR, updated_at:VARCHAR, css_class:VARCHAR, notify_recipients:VARCHAR, submit_text:VARCHAR

merged_deal_data: deal_id:BIGINT, merged_deal_id:BIGINT

owner_data: owner_id:BIGINT, created_at:VARCHAR, portal_id:BIGINT, type:VARCHAR, updated_at:VARCHAR, email:VARCHAR, first_name:VARCHAR, last_name:VARCHAR, active_user_id:BIGINT

owner_team_data: owner_id:VARCHAR, team_id:BIGINT, is_team_primary:VARCHAR

property_data: calculated:VARCHAR, created_at:VARCHAR, description:VARCHAR, field_type:VARCHAR, group_name:VARCHAR, hubspot_defined:VARCHAR, hubspot_object:VARCHAR, label:VARCHAR, name:VARCHAR, show_currency_symbol:VARCHAR, type:VARCHAR, updated_a
```

## 规模、证据复用与新做
主要原因：不可评估。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-010_stg_hubspot__form.md](../018_annotations/018_impl-010_stg_hubspot__form.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_hubspot__form
      description: "HubSpot form definitions and submission tracking"
      source_table: raw.form_data
      columns:
        - name: form_id
          data_type: VARCHAR
          constraints: [unique]
        - name: portal_id
          data_type: BIGINT
        - name: form_name
          data_type: VARCHAR
        - name: form_type
          data_type: VARCHAR
        - name: form_method
          data_type: VARCHAR
        - name: form_action
          data_type: VARCHAR
        - name: form_css_class
          data_type: VARCHAR
        - name: form_submit_text
          data_type: VARCHAR
        - name: form_redirect
          data_type: VARCHAR
        - name: lead_nurturing_campaign_id
          data_type: VARCHAR
        - name: follow_up_id
          data_type: VARCHAR
        - name: notify_recipients
          data_type: VARCHAR
        - name: created_timestamp
          data_type: TIMESTAMP
        - name: updated_timestamp
          data_type: TIMESTAMP
        - name: _fivetran_synced
          data_type: TIMESTAMP WITH TIME ZONE

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-010_stg_hubspot__form.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-010_stg_hubspot__form.md:68)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-010_stg_hubspot__form.md:434)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-010_stg_hubspot__form.md:468)
- [重跑 deduplicate](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-010_stg_hubspot__form.md:499)
- [重跑 created_rule](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-010_stg_hubspot__form.md:538)
