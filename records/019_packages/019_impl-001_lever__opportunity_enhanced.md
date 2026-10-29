# impl-001 | marts | lever__opportunity_enhanced | 差异：S1；日期 原记录

## 契约完整原文

S3:2601–2748

```yaml
    - name: lever__opportunity_enhanced
      description: Enhanced opportunity records joined with stage name, tags, archive reason, most recent offer, and posting context.
      grain: One row per opportunity_id with a valid stage_id
      source_models:
      - intermediate.int_lever__opportunity_contact_info
      - staging.stg_lever__stage
      - staging.stg_lever__archive_reason
      - intermediate.int_lever__opportunity_tags
      - staging.stg_lever__offer
      - staging.stg_lever__posting
      business_logic: '- Use intermediate.int_lever__opportunity_contact_info as the base; each output row represents one opportunity_id from this base. - Inner join staging.stg_lever__stage on stage_id to add current_stage; opportunities without a matching stage are excluded. - Left join staging.stg_lever__archive_reason on archived_reason_id to add archive_reason; if no match, archive_reason is NULL. - Left join intermediate.int_lever__opportunity_tags on opportunity_id to add tags; if no match, tags is NULL. - Determine the most recent offer per candidate by ordering each candidate’s offers by created_at descending and selecting the single most recent record; if multiple offers have the same created_at for a candidate, one is chosen arbitrarily. - Left join this most recent offer to opportunities on opportunity_id; set has_offer to true when a most recent offer exists for this opportunity, otherwise false; set current_offer_status to the joined offer’s status or NULL if no offer joined. - Left join staging.stg_lever__posting on posting_id to add job_title, job_commitment, job_location, job_team, and current_state_of_job_posting; if no match, these fields are NULL. - All other columns are passed through unchanged from the base; NULLs and original values are preserved. No explicit ordering is applied in the result.'
      columns:
      - name: archived_at
        data_type: TIMESTAMP
        description: Timestamp when the opportunity was archived (passthrough from base).
      - name: archived_reason_id
        data_type: VARCHAR
        description: Archive reason identifier from the base opportunity record.
      - name: contact_id
        data_type: VARCHAR
        description: Candidate contact identifier from the base opportunity record.
        tests:
        - not_null
      - name: created_at
        data_type: TIMESTAMP
        description: Timestamp when the opportunity was created (passthrough from base).
        tests:
        - not_null
      - name: is_data_protection_contact_allowed
        data_type: BOOLEAN
        description: Whether contact is allowed under data protection (passthrough from base).
      - name: data_protection_contact_expires_at
        data_type: TIMESTAMP
        description: Expiration timestamp for data protection contact permission (passthrough from base).
      - name: is_data_protection_store_allowed
        data_type: BOOLEAN
        description: Whether data storage is allowed under data protection (passthrough from base).
      - name: data_protection_store_expires_at
        data_type: TIMESTAMP
        description: Expiration timestamp for data protection storage permission (passthrough from base).
      - name: contact_headline
        data_type: VARCHAR
        description: Professional headline of the contact (passthrough from base).
      - name: opportunity_id
        data_type: VARCHAR
        description: Primary key of the opportunity; exactly one output row per value.
        tests:
        - not_null
        - unique
      - name: is_anonymized
        data_type: BOOLEAN
        description: Whether the opportunity data is anonymized (passthrough from base).
      - name: last_advanced_at
        data_type: TIMESTAMP
        description: Timestamp when the opportunity last advanced stages (passthrough from base).
      - name: last_interaction_at
        data_type: TIMESTAMP
        description: Timestamp of the last candidate interaction (passthrough from base).
      - name: contact_location
        data_type: VARCHAR
        description: Location of the contact (passthrough from base).
      - name: contact_name
        data_type: VARCHAR
        description: Full name of the contact (passthrough from base).
      - name: origin
        data_type: VARCHAR
        description: Source/origin of the opportunity (passthrough from base).
      - name: owner_user_id
        data_type: VARCHAR
        description: User ID of the opportunity owner (passthrough from base).
      - name: snoozed_until
        data_type: TIMESTAMP
        description: Timestamp until which the opportunity is snoozed (passthrough from base).
      - name: stage_id
        data_type: VARCHAR
        description: Stage identifier used to join to stg_lever__stage (inner join key).
      - name: updated_at
        data_type: TIMESTAMP
        description: Timestamp when the opportunity was last updated (passthrough from base).
      - name: application_id
        data_type: VARCHAR
        description: Associated application identifier (passthrough from base).
      - name: comments
        data_type: VARCHAR
        description: Free-text comments on the opportunity (passthrough from base).
      - name: company
        data_type: VARCHAR
        description: Current company of the candidate (passthrough from base).
      - name: posting_hiring_manager_user_id
        data_type: VARCHAR
        description: Hiring manager user ID for the posting (passthrough from base).
      - name: posting_id
        data_type: VARCHAR
        description: Posting identifier used to join to stg_lever__posting (left join key).
      - name: posting_owner_user_id
        data_type: VARCHAR
        description: Posting owner user ID (passthrough from base).
      - name: referrer_user_id
        data_type: VARCHAR
        description: User ID of the referrer (passthrough from base).
      - name: requisition_id
        data_type: VARCHAR
        description: Associated requisition identifier (passthrough from base).
      - name: application_type
        data_type: VARCHAR
        description: Application type (passthrough from base).
      - name: emails
        data_type: VARCHAR
        description: Contact email addresses (passthrough from base).
      - name: phones
        data_type: VARCHAR
        description: Contact phone numbers (passthrough from base).
      - name: linkedin_link
        data_type: VARCHAR
        description: LinkedIn profile URL (passthrough from base).
      - name: github_link
        data_type: VARCHAR
        description: GitHub profile URL (passthrough from base).
      - name: current_stage
        data_type: VARCHAR
        description: Stage name joined from stg_lever__stage using stage_id; non-null due to inner join.
      - name: tags
        data_type: VARCHAR
        description: Tags string from int_lever__opportunity_tags joined on opportunity_id; NULL if no tag record.
      - name: archive_reason
        data_type: VARCHAR
        description: Archive reason title from stg_lever__archive_reason via archived_reason_id; NULL if no match.
      - name: job_title
        data_type: VARCHAR
        description: Posting title from stg_lever__posting.posting_title; NULL if no posting match.
      - name: job_commitment
        data_type: VARCHAR
        description: Posting commitment from stg_lever__posting.categories_commitment; NULL if no posting match.
      - name: job_location
        data_type: VARCHAR
        description: Posting location from stg_lever__posting.categories_location; NULL if no posting match.
      - name: job_team
        data_type: VARCHAR
        description: Posting team from stg_lever__posting.categories_team; NULL if no posting match.
      - name: current_state_of_job_posting
        data_type: VARCHAR
        description: Posting state from stg_lever__posting.state; NULL if no posting match.
      - name: has_offer
        data_type: BOOLEAN
        description: True when the candidate’s most recent offer (by created_at) belongs to this opportunity; false otherwise.
      - name: current_offer_status
        data_type: VARCHAR
        description: Status of the candidate’s most recent offer joined to this opportunity; NULL if none joined.
```

## agent 最终 SQL

S4

```sql
WITH offer_rank AS (SELECT *,row_number() OVER(PARTITION BY opportunity_id ORDER BY created_at DESC) rn FROM staging.stg_lever__offer) SELECT b.*,s.stage_name current_stage,t.tags,ar.archive_reason_title archive_reason,p.posting_title job_title,p.categories_commitment job_commitment,p.categories_location job_location,p.categories_team job_team,p.state current_state_of_job_posting,(o.offer_id IS NOT NULL) has_offer,o.status current_offer_status FROM intermediate.int_lever__opportunity_contact_info b JOIN staging.stg_lever__stage s USING(stage_id) LEFT JOIN staging.stg_lever__archive_reason ar ON b.archived_reason_id=ar.archive_reason_id LEFT JOIN intermediate.int_lever__opportunity_tags t USING(opportunity_id) LEFT JOIN offer_rank o ON b.opportunity_id=o.opportunity_id AND o.rn=1 LEFT JOIN staging.stg_lever__posting p USING(posting_id)
```

## gold SQL（仅供定位差异）

S5

```sql
-- Enhanced opportunity summary
-- Integrate all relevant information such as opportunities, contact information, tags, stages, filing reasons, job offers, and more

with opportunity as (
    select *
    from intermediate.int_lever__opportunity_contact_info
),

stage as (
    select *
    from staging.stg_lever__stage
),

archive_reason as (
    select *
    from staging.stg_lever__archive_reason
),

opportunity_tags as (
    select *
    from intermediate.int_lever__opportunity_tags
),

-- Get the latest offer information
order_offers as (
    select 
        *,
        row_number() over(
            partition by candidate_id 
            order by created_at desc
        ) as row_num 
    from staging.stg_lever__offer
),

last_offer as (
    select *
    from order_offers 
    where row_num = 1
),

posting as (
    select *
    from staging.stg_lever__posting
),

final as (
    select 
        opportunity.*,
        
        stage.stage_name as current_stage,
        opportunity_tags.tags, 
        archive_reason.archive_reason_title as archive_reason,
        
        posting.posting_title as job_title,
        posting.categories_commitment as job_commitment,
        posting.categories_location as job_location,
        posting.categories_team as job_team,
        posting.state as current_state_of_job_posting,
        
        last_offer.candidate_id is not null as has_offer,
        last_offer.status as current_offer_status
        
    from opportunity
    join stage  
        on opportunity.stage_id = stage.stage_id
    left join archive_reason
        on opportunity.archived_reason_id = archive_reason.archive_reason_id
    left join opportunity_tags
        on opportunity.opportunity_id = opportunity_tags.opportunity_id
    left join last_offer
        on opportunity.opportunity_id = last_offer.opportunity_id
    left join posting
        on opportunity.posting_id = posting.posting_id
)

select * from final
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5576 | 5861 | 0 | 0 | 1511 | 1579 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"opportunity_id":"opp10012841575"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| opportunity_id | 0 | 0 | 285 | VARCHAR | VARCHAR |
| contact_name | 0 | 0 | 285 | VARCHAR | VARCHAR |
| contact_location | 0 | 0 | 285 | VARCHAR | VARCHAR |
| contact_headline | 0 | 0 | 285 | VARCHAR | VARCHAR |
| stage_id | 0 | 0 | 285 | VARCHAR | VARCHAR |
| owner_user_id | 0 | 0 | 285 | VARCHAR | VARCHAR |
| contact_id | 0 | 0 | 285 | VARCHAR | VARCHAR |
| origin | 0 | 0 | 285 | VARCHAR | VARCHAR |
| archived_reason_id | 0 | 0 | 285 | VARCHAR | VARCHAR |
| snoozed_until | 0 | 0 | 285 | TIMESTAMP | TIMESTAMP |
| is_data_protection_contact_allowed | 0 | 0 | 285 | BOOLEAN | BOOLEAN |
| is_data_protection_store_allowed | 0 | 0 | 285 | BOOLEAN | BOOLEAN |
| is_anonymized | 0 | 0 | 285 | BOOLEAN | BOOLEAN |
| application_id | 0 | 0 | 285 | VARCHAR | VARCHAR |
| comments | 0 | 0 | 285 | VARCHAR | VARCHAR |
| company | 0 | 0 | 285 | VARCHAR | VARCHAR |
| posting_hiring_manager_user_id | 0 | 0 | 285 | VARCHAR | VARCHAR |
| posting_id | 0 | 0 | 285 | VARCHAR | VARCHAR |
| posting_owner_user_id | 0 | 0 | 285 | VARCHAR | VARCHAR |
| referrer_user_id | 0 | 0 | 285 | VARCHAR | VARCHAR |
| requisition_id | 0 | 0 | 285 | VARCHAR | VARCHAR |
| application_type | 0 | 0 | 285 | VARCHAR | VARCHAR |
| emails | 0 | 0 | 285 | VARCHAR | VARCHAR |
| linkedin_link | 0 | 0 | 285 | VARCHAR | VARCHAR |
| github_link | 0 | 0 | 285 | VARCHAR | VARCHAR |
| current_stage | 0 | 0 | 285 | VARCHAR | VARCHAR |
| tags | 0 | 0 | 285 | VARCHAR | VARCHAR |
| archive_reason | 0 | 0 | 285 | VARCHAR | VARCHAR |
| job_title | 0 | 0 | 285 | VARCHAR | VARCHAR |
| job_commitment | 0 | 0 | 285 | VARCHAR | VARCHAR |
| job_location | 0 | 0 | 285 | VARCHAR | VARCHAR |
| job_team | 0 | 0 | 285 | VARCHAR | VARCHAR |
| current_state_of_job_posting | 0 | 0 | 285 | VARCHAR | VARCHAR |
| has_offer | 0 | 0 | 285 | BOOLEAN | BOOLEAN |
| current_offer_status | 0 | 0 | 285 | VARCHAR | VARCHAR |

opportunity_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"OPP10012841575","rows":1}]</code> | <code>[{"value":"OPP10012841575","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

contact_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Amanda Murphy","rows":1}]</code> | <code>[{"value":"Amanda Murphy","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

contact_location 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Port Amanda","rows":1}]</code> | <code>[{"value":"Port Amanda","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

contact_headline 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Theatre manager","rows":1}]</code> | <code>[{"value":"Theatre manager","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

stage_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"STA84621748638","rows":1}]</code> | <code>[{"value":"STA84621748638","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

owner_user_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"USE29350664910","rows":1}]</code> | <code>[{"value":"USE29350664910","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

contact_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"e6c25144-4ae4-4172-b550-448cef204571","rows":1}]</code> | <code>[{"value":"e6c25144-4ae4-4172-b550-448cef204571","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

origin 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"university","rows":1}]</code> | <code>[{"value":"university","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

archived_reason_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"ARC43352458550","rows":1}]</code> | <code>[{"value":"ARC43352458550","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

snoozed_until 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

is_data_protection_contact_allowed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"false","rows":1}]</code> | <code>[{"value":"false","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

is_data_protection_store_allowed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"true","rows":1}]</code> | <code>[{"value":"true","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

is_anonymized 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"true","rows":1}]</code> | <code>[{"value":"true","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

application_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"APP65889098226","rows":1}]</code> | <code>[{"value":"APP65889098226","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

comments 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Officer money choice big believe scientist. Market cost instead result. Investment mouth culture mother stock also. Former watch go future leave single enjoy.\nSignificant receive leg price.","rows":1}]</code> | <code>[{"value":"Officer money choice big believe scientist. Market cost instead result. Investment mouth culture mother stock also. Former watch go future leave single enjoy.\nSignificant receive leg price.","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

company 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Calhoun, Barrett and Thompson","rows":1}]</code> | <code>[{"value":"Calhoun, Barrett and Thompson","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

posting_hiring_manager_user_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"USE55252701991","rows":1}]</code> | <code>[{"value":"USE55252701991","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

posting_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"POS18888783527","rows":1}]</code> | <code>[{"value":"POS18888783527","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

posting_owner_user_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"USE80422233545","rows":1}]</code> | <code>[{"value":"USE80422233545","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

referrer_user_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

requisition_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"REQ37976843575","rows":1}]</code> | <code>[{"value":"REQ37976843575","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

application_type 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"agency","rows":1}]</code> | <code>[{"value":"agency","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

emails 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"&lt;barryedwards@example.com&gt;","rows":1}]</code> | <code>[{"value":"&lt;barryedwards@example.com&gt;","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

linkedin_link 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

github_link 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

current_stage 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Doctor, hospital Interview","rows":1}]</code> | <code>[{"value":"Doctor, hospital Interview","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

tags 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

archive_reason 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Availability issues","rows":1}]</code> | <code>[{"value":"Availability issues","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

job_title 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

job_commitment 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

job_location 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

job_team 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

current_state_of_job_posting 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1}]</code> | <code>[{"value":null,"rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

has_offer 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"true","rows":1}]</code> | <code>[{"value":"true","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

current_offer_status 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"pending","rows":1}]</code> | <code>[{"value":"pending","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

| 约束 | 列 | 违反计数 |
|---|---|---|
| not_null | created_at | <code>{"sql_null_rows":3000}</code> |

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>24列；[{"column":"archived_at","table_rows":3000}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory 'lever__opportunity_enhanced':'''WITH offer_rank AS (SELECT *,row_number() OVER(PARTITION BY opportunity_id ORDER BY created_at DESC) rn FROM staging.stg_lever__offer) SELECT b.*,s.stage_name current_stage,t.tags,ar.archive_reason_title archive_reason,p.posting_title job_title,p.categories_commitment job_commitment,p.categories_location job_location,p.categories_team job_team,p.state current_state_of_job_posting,(o.offer_id IS NOT NULL) has_offer,o.status current_offer_status FROM intermediate.int_lever__opportunity_contact_info b JOIN staging.stg_lever__stage s USING(stage_id) LEFT JOIN staging.stg_lever__archive_reason ar ON b.archived_reason_id=ar.archive_reason_id LEFT JOIN intermediate.int_lever__opportunity_tags t USING(opportunity_id) LEFT JOIN offer_rank o ON b.opportunity_id=o.opportunity_id AND o.rn=1 LEFT JOIN staging.stg_lever__posting p USING(posting_id)''',</code> |

## 轨迹索引（不放输出原文）

本题事件总数：69；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find sql -maxdepth 3 -type f &#124; sort &#124; head -100 &amp;&amp; cat config/layer_dependencies.yaml</code> | 4500 | true | false |
| 19 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/intermediate')<br>models={<br>'int_lever__contact_info':'''WITH emails AS (SELECT contact_id, string_agg('&lt;' &#124;&#124; email &#124;&#124; '&gt;', ', ') AS emails</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/models.py &lt;&lt;'PY'<br>models={<br>'int_lever__hiring_funnel_metrics':'''WITH sm AS (SELECT stage_id, CASE WHEN lower(stage_name) LIKE '%new%' OR lower(stage_name) LIKE '%lead%' THEN 1 WHEN lower(s</code> | 0 | false | false |
| 23 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/marts')<br>models={<br>'lever__interview_enhanced':'''SELECT iu.canceled_at,iu.created_at,iu.creator_user_id,iu.interview_date,iu.duration,iu.</code> | 0 | false | false |
| 25 | run | <code>cat &gt;&gt; /tmp/marts.py &lt;&lt;'PY'<br>models={<br>'lever__candidate_quality_insights':'''WITH cb AS (SELECT ci.*,a.posting_id,a.referrer_user_id,a.type application_type,p.categories_department,p.categories_level,C</code> | 6312 | true | false |
| 27 | run | <code>grep -E 'ERROR -&#124;Executing: staging&#124;STAGING layer complete' /tmp/run.log</code> | 5620 | true | false |
| 31 | run | <code>sed -n '1,100p' sql/staging/stg_lever__stage.sql; sed -n '1,80p' sql/staging/stg_lever__interview.sql</code> | 2303 | false | false |
| 33 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql').rglob('*.sql'):<br> s=p.read_text().replace(' ~* ', ' ~* ')<br> # DuckDB regex case insensitive via regexp_matches(..., 'i')<br> import re<br> s=re.su</code> | 0 | false | false |
| 35 | run | <code>find sql -type f &#124; sort</code> | 2341 | true | false |
| 37 | run | <code>sed -i "s/) external FROM cb/) external_avg FROM cb/; s/referred&gt;external+10/referred&gt;external_avg+10/; s/internal&gt;external+10/internal&gt;external_avg+10/" sql/marts/lever__candidate_quality_insights.sq</code> | 2929 | true | false |
| 41 | run | <code>sed -i 's/r\\."/r."/g' sql/staging/*.sql; python run.py &gt;/tmp/run3.log 2&gt;&amp;1; grep 'ERROR -' /tmp/run3.log</code> | 2929 | true | false |
| 47 | run | <code>sed -i 's/LEFT JOIN staging.stg_lever__stage s USING(stage_id)/LEFT JOIN staging.stg_lever__stage s ON i.stage_id=s.stage_id/' sql/intermediate/int_lever__interviewer_performance.sql; sed -i 's/GROUP </code> | 1220 | false | false |
| 49 | run | <code>sed -i 's/SELECT owner_user_id, count(DISTINCT posting_id)/SELECT p.owner_user_id AS owner_user_id, count(DISTINCT p.posting_id)/' sql/marts/lever__hiring_manager_scorecard.sql; python run.py &gt;/tmp/ru</code> | 1018 | true | false |
| 51 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml<br>c=duckdb.connect('lever.duckdb',read_only=True); y=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer,models in [('intermediate',y['modeling_spec']['intermedi</code> | 798 | true | false |
| 57 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml<br>c=duckdb.connect('lever.duckdb',read_only=True);y=yaml.safe_load(open('docs/data_contract.yaml'))<br>for schema, specs in [('intermediate',y['modeling_spec']['intermedi</code> | 799 | true | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
'lever__opportunity_enhanced':'''WITH offer_rank AS (SELECT *,row_number() OVER(PARTITION BY opportunity_id ORDER BY created_at DESC) rn FROM staging.stg_lever__offer) SELECT b.*,s.stage_name current_stage,t.tags,ar.archive_reason_title archive_reason,p.posting_title job_title,p.categories_commitment job_commitment,p.categories_location job_location,p.categories_team job_team,p.state current_state_of_job_posting,(o.offer_id IS NOT NULL) has_offer,o.status current_offer_status FROM intermediate.int_lever__opportunity_contact_info b JOIN staging.stg_lever__stage s USING(stage_id) LEFT JOIN staging.stg_lever__archive_reason ar ON b.archived_reason_id=ar.archive_reason_id LEFT JOIN intermediate.int_lever__opportunity_tags t USING(opportunity_id) LEFT JOIN offer_rank o ON b.opportunity_id=o.opportunity_id AND o.rn=1 LEFT JOIN staging.stg_lever__posting p USING(posting_id)''',
```
event 23 / message

```text
'lever__opportunity_stage_history':'''WITH timeline AS (SELECT h.opportunity_id,h.stage_id,h.updated_at valid_from,lead(h.updated_at) OVER(PARTITION BY h.opportunity_id ORDER BY h.updated_at) next_at,h.updater_user_id FROM staging.stg_lever__opportunity_stage_history h) SELECT t.opportunity_id,o.contact_name opportunity_contact_name,t.valid_from,coalesce(t.next_at,o.archived_at,current_timestamp) valid_ending_at,s.stage_name stage,t.stage_id,u.user_name updater_user_name,o.archive_reason,o.job_title,o.job_location,o.job_team,o.tags application_sources,date_diff('day',cast(t.valid_from AS DATE),cast(coalesce(t.next_at,o.archived_at,current_timestamp) AS DATE)) days_in_stage FROM timeline t JOIN staging.stg_lever__stage s USING(stage_id) JOIN marts.lever__opportunity_enhanced o USING(opportunity_id) LEFT JOIN staging.stg_lever__user u ON t.updater_user_id=u.user_id''',
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-001.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__opportunity_enhanced.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/marts/lever__opportunity_enhanced.sql`
- S6: `records/006_contract_impl-001.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md`
- S10: `data/019_packages_work/019_impl-001_lever__opportunity_enhanced/019_impl-001_lever__opportunity_enhanced.json`
- S11: `data/005_cs_work/impl-001/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions`
