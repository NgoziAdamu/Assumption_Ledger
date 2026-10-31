# DAComp / impl-014_stg_qualtrics__survey_version（v3）

## 错在哪里
agent按显式时区格式成功解析12000个created_at，gold用TRY_CAST得到全NULL，契约未规定解析策略。

证据复用入口：[018_impl-014_stg_qualtrics__survey_version.md](../018_annotations/018_impl-014_stg_qualtrics__survey_version.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## gold_timestamp_parser
- 角色：主要；类别：**已说出的选择**；把握：中。
- 依据：TIMESTAMP未规定解析格式，显式STRPTIME保留12000值而TRY_CAST全空；差异取决于解析选择。
- 是否说出：针对本处的具体说明。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 79 / args.final_thought：
```text
原始 Qualtrics 时间文本带时区后缀（例如 `+0800`），DuckDB 直接 `try_cast(... AS TIMESTAMP)` 无法解析。日期相关 SQL 改用 `try_strptime(..., '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP`；不可解析日期在日期计算中排除。
```

## 规模、证据复用与新做
主要原因：已说出的选择。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-014_stg_qualtrics__survey_version.md](../018_annotations/018_impl-014_stg_qualtrics__survey_version.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: stg_qualtrics__survey_version
      description: "Survey version history and metadata"
      source_table: "raw.survey_version"
      primary_key: ["version_id"]
      columns:
        - name: version_id
          data_type: BIGINT
          constraints: [not_null, unique]
        - name: survey_id
          data_type: VARCHAR
        - name: created_at
          data_type: TIMESTAMP
        - name: version_description
          data_type: VARCHAR
        - name: is_published
          data_type: BOOLEAN
        - name: publisher_user_id
          data_type: VARCHAR
        - name: version_number
          data_type: BIGINT
        - name: was_published
          data_type: BOOLEAN

# --------------------------------------------------------------------------- #
# PHASE 2: Defines the business logic from staging tables to analytical models. #
# --------------------------------------------------------------------------- #
modeling_spec:
  purpose: "Transform staging data into business-ready analytical models that provide deep insights into survey performance, user engagement, response quality, and channel effectiveness. This phase applies complex business logic, creates derived metrics, and builds decision-support tools for survey optimization."

  design_principles:
    intermediate_purpose: "Create reusable, business-centric data models that implement core analytical logic and can be composed into multiple mart models. Each intermediate model should focus on a specific analytical domain."
    mart_purpose: "Provide analysis-ready tables optimized for specific business use cases, dashboard consumption, and decision-making workflows."
    grain_importance: "Every model must have an explicitly defined grain to ensure proper aggregation and prevent analytical errors."
    performance_consideration: "Models should be designed for optimal query performance in downstream analytics and BI tools."

  intermediate_models:
```

## 规则问题

v2将全局日期说明视为通用；v3要求针对本处。这里已说明源时区、TRY_CAST失败和替代精确格式，覆盖本表同一解析前提，因此选具体说明，改记已说出的选择。

## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-014_stg_qualtrics__survey_version.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-014_stg_qualtrics__survey_version.md:59)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-014_stg_qualtrics__survey_version.md:198)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-014_stg_qualtrics__survey_version.md:226)
- [重跑 gold_timestamp_parser](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-014_stg_qualtrics__survey_version.md:252)
