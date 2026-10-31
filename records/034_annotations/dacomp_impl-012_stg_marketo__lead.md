# DAComp / impl-012_stg_marketo__lead（v3）

## 错在哪里
agent按契约排除首尾带空白的姓名，gold只trim后保留；first/last两项各缺3行并列。

证据复用入口：[018_impl-012_stg_marketo__lead.md](../018_annotations/018_impl-012_stg_marketo__lead.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## first_name_trim_policy
- 角色：并列；类别：**其他**；把握：中。
- 依据：可执行first_name=TRIM(first_name)失败delete_row；agent照做，gold修整后保留。6→3行。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 1 / args.content：
```text
st name of the lead"
          validation_rules:
            - rule: "first_name = TRIM(first_name)"
              description: "Remove leading and trailing whitespace"
              on_failure: delete_row
            - rule: "LENGTH(first_name) <= 100"
              description: "First name cannot exceed 100 characters"
              on_failure: delete_row
        - name: last_name
          data_type: VARCHAR
          description: "Last name of the lead"
          validation_rules:
            - rule: "last_name = TRIM(last_name)"
              description: "Remove leading and trailing whitespace"
              on_failure: delete_row
            - rule: "LENGTH(last_name) <= 100"
              description: "Last name cannot exceed 100 characters"
              on_failure: delete_row

    - name: stg_marketo__campaigns
      description: "Cleaned campaign records with standardized attributes and campaign
```
## last_name_trim_policy
- 角色：并列；类别：**其他**；把握：中。
- 依据：可执行last_name=TRIM(last_name)失败delete_row；agent照做，gold修整后保留。6→3行。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 1 / args.content：
```text
st name of the lead"
          validation_rules:
            - rule: "last_name = TRIM(last_name)"
              description: "Remove leading and trailing whitespace"
              on_failure: delete_row
            - rule: "LENGTH(last_name) <= 100"
              description: "Last name cannot exceed 100 characters"
              on_failure: delete_row

    - name: stg_marketo__campaigns
      description: "Cleaned campaign records with standardized attributes and campaign configuration details"
      source_table: "raw.marketo_campaign"
      grain: "One row per unique campaign in Marketo"
      columns:
        - name: campaign_id
          data_type: VARCHAR
          constraints: [not_null, unique]
          validation_rules:
            - rule: "campaign_id IS NOT NULL"
              on_failure: delete_row
        - name: campaign_name
          data_type: VARCHAR
          constraints: [not_null]

```

## 规模、证据复用与新做
主要原因：其他。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-012_stg_marketo__lead.md](../018_annotations/018_impl-012_stg_marketo__lead.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_marketo__lead
      description: "Cleaned and standardized lead (contact) records from Marketo with basic contact information and timestamps"
      source_table: "raw.marketo_lead"
      grain: "One row per unique lead in Marketo"
      columns:
        - name: lead_id
          data_type: VARCHAR
          constraints: [not_null, unique]
        - name: created_timestamp
          data_type: VARCHAR
          constraints: [not_null]
        - name: updated_timestamp
          data_type: VARCHAR
          constraints: [not_null]
        - name: email
          data_type: VARCHAR
          constraints: [not_null]
          description: "Email address of the lead"
          validation_rules:
            - rule: "email = LOWER(TRIM(email))"
              description: "Normalize email to lowercase and remove whitespace"
              on_failure: delete_row
            - rule: "email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'"
              description: "Email must follow valid email format"
              on_failure: delete_row
        - name: first_name
          data_type: VARCHAR
          description: "First name of the lead"
          validation_rules:
            - rule: "first_name = TRIM(first_name)"
              description: "Remove leading and trailing whitespace"
              on_failure: delete_row
            - rule: "LENGTH(first_name) <= 100"
              description: "First name cannot exceed 100 characters"
              on_failure: delete_row
        - name: last_name
          data_type: VARCHAR
          description: "Last name of the lead"
          validation_rules:
            - rule: "last_name = TRIM(last_name)"
              description: "Remove leading and trailing whitespace"
              on_failure: delete_row
            - rule: "LENGTH(last_name) <= 100"
              description: "Last name cannot exceed 100 characters"
              on_failure: delete_row

```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-012_stg_marketo__lead.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-012_stg_marketo__lead.md:78)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-012_stg_marketo__lead.md:257)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-012_stg_marketo__lead.md:285)
- [重跑 first_name_trim_policy](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-012_stg_marketo__lead.md:309)
- [重跑 last_name_trim_policy](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-012_stg_marketo__lead.md:340)
- [重跑 no_dedupe](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-012_stg_marketo__lead.md:371)
