# DAComp DE-Impl staging 逐表机械比对

## 任务

只比对 DAComp DE-Impl 30 题中，留存最终 CFS 评分标记为不匹配的 staging 表。记录预测/gold 行数、列名和类型差异、对齐键差异、共同键内逐列值差异与样例。单列 impl-021 五张 staging 表。日期：2026-10-27，Asia/Singapore。

原始数据库均以 `read_only=True` 打开；独立 SQL 抽查也使用 `ATTACH ... (READ_ONLY)`。本次没有运行 agent、run.py、任务 SQL 管线或其他层的比对，没有判定错误原因或未核实假设。

## 结论

30 题共配置 **459 张 staging 表**，本次目标为留存 CFS 标记不匹配的 **176 张**；使用当前官方 `CoreAccuracyEvaluator.compare_table` 逐表只读复核，176 张仍均返回不匹配。全部目标表已生成结构化记录与总表。**3 张表在预测和 gold 中均不存在**，相关统计记为未知；**30 张表存在非唯一的共同键组**，其逐列差异采用明确标注的多重集合下界，不虚构唯一逐行对应。122 个输入文件的大小、SHA-256 和修改时间在比对前后完全一致。

## 详细发现

### 1. 比对口径，以及与官方的差异

已亲自读取本机官方 `evaluation_suite/utils.py` 和 `evaluation_config_compare.yaml`。实际代码与任务中提到的“两位小数四舍五入、忽略时间列”并不完全一致：

- 官方先按每表 `compare_cols` 及双方实际列的交集选列，使用 `COALESCE(LOWER(TRIM(CAST(column AS VARCHAR))), 'null')` 规范化值，再做整行字符串 hash 的多重集合比较。
- **没有统一的两位小数四舍五入，也没有数值容差。** 本次不额外 round；数值转字符串后不同就计为不同，类型差异另行记录。字段本身存为 `DECIMAL(...,2)`，不等于比较器对所有数值执行两位小数舍入。
- **没有全局忽略时间列。** 是否参加主口径比较由 `compare_cols` 决定。例如 impl-001 的 application 比较列含 `created_at`，其他表也有 `date_day` 等。配置未选中的时间列和其他列不进入主口径列数，但本次额外保留所有共同列的差异记录，并以 `included_in_official_comparison=false` 标记。
- 主表的“不一致列数”只统计官方可用比较列中，共同键内有值差异的列。完整物理列名、类型、仅预测/仅 gold 的列、类型不一致列表和所有共同列的值差异都在逐题 JSON 中。缺列与类型变化没有自动混入“值差异列数”。
- 官方按整行多重集合判断匹配，不使用主键；行数不同会提前返回 False。本次为满足逐键核查要求，即使行数不同仍继续对齐共同键、比较每列。这个拆解是机械诊断视角，不是官方分数的重新定义。
- key 和比较值使用同一字符串规范化。大小写和首尾空白被忽略；SQL NULL 变成字符串 `null`，因此与字面字符串 `null` 不再区分。空字符串键和 NULL 规范化键都保留，并单列其行数，不悄悄丢弃。

[方法及范围元数据](../records/004_staging_overview.json)。官方代码 SHA-256 为 `e8fc0d525d0a3894f13f070defe99586690f49310522cd22e059d1726fa14e0b`，与 003 号记录一致。

### 2. 对齐字段的选择和非唯一键处理

优先使用契约明确的 `primary_key`，其次是标为 not_null/unique 的 ID。没有明确主键时，从可用 not_null ID、命名 key、实体 ID，以及 ID/date/dimension 组合中按固定顺序尝试；双边唯一性只用于判断是否可一对一，不以“共同键最多”为挑选标准。契约声明的主键即使实际重复，也保留该声明并记录重复情况。

每张表实际使用的字段都写在下方总表中；逐题 JSON 的 `alignment.reason`、`contract_not_null_id_candidates`、`candidate_profiles` 记录选择依据、尝试字段及双方不同键数和重复键组数。推定字段只称为“对齐字段”，不认定其一定是业务主键。仅靠 not_null 无法证明唯一性。

- 键数均是规范化后不同键元组的数量，不是行数。`pred_only_keys`、`gold_only_keys`、`shared_keys` 分别表示只在预测、只在 gold、双方都有的键。
- 共同键为一对一时，`one_to_one_mismatch_rows` 是精确的逐行值差异计数，最多给出 3 个不同键的真实样例。样例保留预测/gold 的原始 CAST-to-VARCHAR 值（SQL NULL 用 JSON null）和规范化值。
- 共同键非唯一时，**不做多对多笛卡尔积，也不任取一行或按未声明顺序硬配对**。对同键、同列的双方值多重集合先抵消相同值：若剩余预测值有 P 个、gold 值有 G 个，则至少 `min(P,G)` 对值必然不同。结果记录这个下界、双方未抵消值的出现次数，并给出真实残余值及频次（每侧最多 3 种）。此类样例明确标注为值多重集合，不宣称是唯一原始行对。
- `mismatch_rows_or_minimum_pairs` = 一对一精确差异行数 + 非唯一键组的上述下界。对 30 张含非唯一共同键的表，它不是唯一逐行错误数；每列单独抵消，也不意味着各列共享同一种行配对。
- 只有重复次数不同、可配对值相同的情况，行数差和未抵消出现次数仍会记录，但不额外虚构“值不同”的行。样例不足 3 个不同键时只给实际存在的数量；非唯一键不能伪造 3 个确定行对。
- 35 张表的共同键数为 0；它们的共同键值差异列数为 0 仅表示没有可比共同键，不表示全表匹配。缺表则行数、键数及值差异列数均以空值/“—”表示。

### 3. impl-021 五张 staging 表的行数

以下为直接对原始留存预测库和 gold 执行 `SELECT count(*)` 的结果，不引用旧分析表的计数。[完整结构化记录](../records/004_staging_impl-021.json)。

| 表名 | 预测行数 | gold 行数 | Δ行 |
| --- | ---: | ---: | ---: |
| `stg_klaviyo__campaign` | 2 | 184 | -182 |
| `stg_klaviyo__event` | 2,500 | 4 | +2,496 |
| `stg_klaviyo__flow` | 1 | 79 | -78 |
| `stg_klaviyo__metric` | 1 | 29 | -28 |
| `stg_klaviyo__person` | 2 | 1,192 | -1,190 |

### 4. 全部 176 张目标表的总表

Δ行 = 预测行数 − gold 行数。“键 P/G/共同”依次是只在预测、只在 gold、两边都有的不同键数。**† 表示有非唯一共同键组**，该行的逐列值差异计数包含下界统计，详见上节；精确部分与下界部分在 JSON 中分开。**— 表示表不存在或无法建立列比较，不是 0。** 表名链接指向对应任务的完整记录，逐列计数和样例可按表名搜索。

[可处理的 CSV 总表](../records/004_staging_summary.csv)。

| 任务 | 失败 staging 表 | 预测行 | gold 行 | Δ行 | 对齐字段 | 键 P/G/共同 | 不一致列数 |
| --- | --- | ---: | ---: | ---: | --- | --- | ---: |
| impl-001 | [stg_lever__application](../records/004_staging_impl-001.json) | 0 | 5,000 | -5,000 | `application_id` | 0/5,000/0 | 0 |
| impl-001 | [stg_lever__offer](../records/004_staging_impl-001.json) | 236 | 1,000 | -764 | `offer_id` | 0/764/236 | 0 |
| impl-001 | [stg_lever__posting](../records/004_staging_impl-001.json) | 148 | 148 | +0 | `posting_id` | 0/0/148 | 2 |
| impl-001 | [stg_lever__requisition](../records/004_staging_impl-001.json) | 146 | 146 | +0 | `requisition_id` | 0/0/146 | 2 |
| impl-002 | [stg_pendo__event](../records/004_staging_impl-002.json) | 50,000 | 50,000 | +0 | `event_key` | 50,000/50,000/0 | 0 |
| impl-002 | [stg_pendo__guide_event](../records/004_staging_impl-002.json) | 15,000 | 15,000 | +0 | `account_id, app_id, guide_id, visitor_id` | 0/0/15,000 | 3 |
| impl-002 | [stg_pendo__page_event](../records/004_staging_impl-002.json) | 30,000 | 30,000 | +0 | `account_id, app_id, page_id, visitor_id` | 0/0/30,000 | 1 |
| impl-002 | [stg_pendo__poll_event](../records/004_staging_impl-002.json) | 5,000 | 5,000 | +0 | `account_id, guide_id, poll_id, visitor_id, app_id` | 0/0/5,000 | 2 |
| impl-002 | [stg_pendo__user](../records/004_staging_impl-002.json) | 11 | 13 | -2 | `user_id` | 0/2/11 | 1 |
| impl-002 | [stg_pendo__visitor_history](../records/004_staging_impl-002.json) | 8,000 | 8,000 | +0 | `visitor_id` | 0/0/8,000 | 1 |
| impl-003† | [stg_customer360__country_codes](../records/004_staging_impl-003.json) | 30 | 31 | -1 | `country_code_alpha_2` | 0/0/30 | 0† |
| impl-003† | [stg_customer360__state_territory_codes](../records/004_staging_impl-003.json) | 772 | 717 | +55 | `state_code, alpha2_country_code` | 0/0/675 | 0† |
| impl-004 | [stg_salesforce__contact_history](../records/004_staging_impl-004.json) | 3,000 | 3,000 | +0 | `contact_id, account_id, mailing_postal_code, owner_id, history_unique_key` | 3,000/2,369/0 | 0 |
| impl-005 | [stg_google_ads__account_history](../records/004_staging_impl-005.json) | 100 | 0 | +100 | `account_id` | 100/0/0 | 0 |
| impl-005† | [stg_google_ads__account_stats](../records/004_staging_impl-005.json) | 10,000 | 10,000 | +0 | `account_id, date_day, ad_network_type, device` | 0/0/9,968 | 3† |
| impl-005 | [stg_google_ads__ad_group_history](../records/004_staging_impl-005.json) | 5,000 | 5,000 | +0 | `ad_group_id` | 0/0/5,000 | 1 |
| impl-005 | [stg_google_ads__ad_group_stats](../records/004_staging_impl-005.json) | 10,000 | 10,000 | +0 | `account_id, ad_group_id, campaign_id` | 9,985/9,985/15 | 3 |
| impl-005 | [stg_google_ads__ad_history](../records/004_staging_impl-005.json) | 10,000 | 0 | +10,000 | `ad_id` | 10,000/0/0 | 0 |
| impl-005 | [stg_google_ads__campaign_history](../records/004_staging_impl-005.json) | 1,000 | 0 | +1,000 | `campaign_id` | 1,000/0/0 | 0 |
| impl-005 | [stg_google_ads__campaign_stats](../records/004_staging_impl-005.json) | 10,000 | 10,000 | +0 | `account_id, campaign_id, date_day, ad_network_type, device` | 0/0/10,000 | 3 |
| impl-005 | [stg_google_ads__keyword_stats](../records/004_staging_impl-005.json) | 10,000 | 10,000 | +0 | `account_id, ad_group_id, campaign_id, criterion_id` | 0/0/10,000 | 3 |
| impl-006† | [stg_amazon_ads__ad_group_report](../records/004_staging_impl-006.json) | 17,868 | 17,868 | +0 | `ad_group_id, date_day` | 8/1/17,213 | 3† |
| impl-006† | [stg_amazon_ads__campaign_report](../records/004_staging_impl-006.json) | 12,990 | 12,990 | +0 | `campaign_id, date_day, campaign_applicable_budget_rule_id, campaign_budget_currency_code` | 0/0/12,361 | 4† |
| impl-006 | [stg_amazon_ads__keyword_report](../records/004_staging_impl-006.json) | 710 | 710 | +0 | `keyword_id, date_day, campaign_id, ad_group_id, currency_code` | 0/0/710 | 7 |
| impl-006 | [stg_amazon_ads__product_report](../records/004_staging_impl-006.json) | 700 | 700 | +0 | `date_day, campaign_id, ad_group_id, ad_id, currency_code` | 0/0/700 | 9 |
| impl-006 | [stg_amazon_ads__search_report](../records/004_staging_impl-006.json) | 710 | 710 | +0 | `date_day, campaign_id, ad_group_id, keyword_id, currency_code` | 0/0/710 | 8 |
| impl-006 | [stg_apple_search_ads__ad_group_report](../records/004_staging_impl-006.json) | 1,500 | 1,500 | +0 | `ad_group_id` | 0/0/1,500 | 6 |
| impl-006 | [stg_apple_search_ads__ad_report](../records/004_staging_impl-006.json) | 1,500 | 1,500 | +0 | `ad_id` | 0/0/1,500 | 4 |
| impl-006 | [stg_apple_search_ads__campaign_report](../records/004_staging_impl-006.json) | 1,500 | 1,500 | +0 | `campaign_id, date_day` | 1,023/1,500/0 | 0 |
| impl-006† | [stg_facebook_ads__ad_actions](../records/004_staging_impl-006.json) | 700 | 700 | +0 | `ad_id, date_day` | 0/0/699 | 5† |
| impl-006 | [stg_facebook_ads__ad_report](../records/004_staging_impl-006.json) | 1,000 | 1,000 | +0 | `ad_id` | 0/0/1,000 | 4 |
| impl-006† | [stg_google_ads__account_report](../records/004_staging_impl-006.json) | 719 | 719 | +0 | `account_id, date_day, ad_network_type, device` | 0/0/718 | 2† |
| impl-006 | [stg_google_ads__ad_group_report](../records/004_staging_impl-006.json) | 715 | 715 | +0 | `account_id, ad_group_id, date_day, ad_network_type, device` | 715/715/0 | 0 |
| impl-006 | [stg_google_ads__campaign_report](../records/004_staging_impl-006.json) | 26,031 | 26,031 | +0 | `account_id, date_day, campaign_id, ad_network_type, device` | 24,558/25,856/0 | 0 |
| impl-006 | [stg_linkedin_ads__campaign_report](../records/004_staging_impl-006.json) | 1,500 | 1,500 | +0 | `campaign_id` | 0/0/1,500 | 10 |
| impl-006 | [stg_microsoft_ads__campaign_report](../records/004_staging_impl-006.json) | 1,500 | 1,500 | +0 | `campaign_id` | 0/0/1,500 | 9 |
| impl-006 | [stg_pinterest_ads__campaign_report](../records/004_staging_impl-006.json) | 900 | 900 | +0 | `campaign_id` | 0/0/900 | 13 |
| impl-006 | [stg_reddit_ads__campaign_report](../records/004_staging_impl-006.json) | 1,200 | 1,200 | +0 | `campaign_id` | 0/0/1,200 | 20 |
| impl-006 | [stg_snapchat_ads__campaign_report](../records/004_staging_impl-006.json) | 900 | 900 | +0 | `campaign_id` | 0/0/900 | 16 |
| impl-006 | [stg_tiktok_ads__campaign_report](../records/004_staging_impl-006.json) | 900 | 900 | +0 | `campaign_id, date_day, advertiser_id` | 900/900/0 | 0 |
| impl-006 | [stg_twitter_ads__campaign_report](../records/004_staging_impl-006.json) | 900 | 900 | +0 | `campaign_id` | 0/0/900 | 10 |
| impl-007 | [stg_apple_store__financial_stats_subscriptions_country](../records/004_staging_impl-007.json) | 700 | 700 | +0 | `date_day, app_id, country` | 4/4/696 | 2 |
| impl-007 | [stg_apple_store__sales_subscription_event_summary](../records/004_staging_impl-007.json) | 700 | 700 | +0 | `date_day, app_id, subscription_id, subscriber_id, country` | 700/700/0 | 0 |
| impl-007 | [stg_apple_store__sales_subscription_summary](../records/004_staging_impl-007.json) | 700 | 700 | +0 | `date_day, app_id, country` | 0/0/700 | 2 |
| impl-007 | [stg_google_play__stats_installs_app_version](../records/004_staging_impl-007.json) | 6,000 | 6,000 | +0 | `date_day, package_name, app_version_code` | 0/0/6,000 | 1 |
| impl-007† | [stg_google_play__stats_installs_device](../records/004_staging_impl-007.json) | 6,000 | 6,000 | +0 | `date_day, package_name, device` | 0/0/5,974 | 1† |
| impl-007† | [stg_google_play__stats_installs_os_version](../records/004_staging_impl-007.json) | 6,000 | 6,000 | +0 | `date_day, package_name, os_version` | 0/0/5,981 | 2† |
| impl-007† | [stg_google_play__stats_installs_overview](../records/004_staging_impl-007.json) | 6,000 | 6,000 | +0 | `date_day, package_name` | 0/0/5,719 | 1† |
| impl-007† | [stg_google_play__stats_ratings_overview](../records/004_staging_impl-007.json) | 691 | 700 | -9 | `date_day, package_name` | 0/9/683 | 0† |
| impl-007 | [stg_google_play__stats_store_performance_traffic_source](../records/004_staging_impl-007.json) | 700 | 700 | +0 | `date_day, package_name, traffic_source` | 0/0/700 | 1 |
| impl-008 | [stg_asana__section](../records/004_staging_impl-008.json) | 197 | 190 | +7 | `section_id` | 7/0/190 | 0 |
| impl-008 | [stg_asana__task](../records/004_staging_impl-008.json) | 2,986 | 2,986 | +0 | `task_id` | 0/0/2,986 | 2 |
| impl-009 | [stg_google_play__earnings](../records/004_staging_impl-009.json) | 8,000 | 0 | +8,000 | `sku_id, base_plan_id, buyer_postal_code, order_id, offer_id, package_name` | 8,000/0/0 | 0 |
| impl-009 | [stg_google_play__stats_ratings_overview](../records/004_staging_impl-009.json) | 2,928 | 0 | +2,928 | `date_day, package_name` | 8/0/0 | 0 |
| impl-009 | [stg_google_play__store_performance_country](../records/004_staging_impl-009.json) | 8,800 | 6,400 | +2,400 | `date_day, package_name, country` | 8,800/6,400/0 | 0 |
| impl-010 | [stg_hubspot__deal_pipeline](../records/004_staging_impl-010.json) | 20 | 20 | +0 | `deal_pipeline_id` | 0/0/20 | 3 |
| impl-010 | [stg_hubspot__deal_pipeline_stage](../records/004_staging_impl-010.json) | 104 | 104 | +0 | `deal_pipeline_stage_id` | 0/0/104 | 5 |
| impl-010 | [stg_hubspot__email_event](../records/004_staging_impl-010.json) | 736 | 736 | +0 | `email_event_id` | 0/0/736 | 3 |
| impl-010† | [stg_hubspot__engagement_email](../records/004_staging_impl-010.json) | 1,171 | 1,164 | +7 | `engagement_id` | 0/0/1,164 | 0† |
| impl-010 | [stg_hubspot__form](../records/004_staging_impl-010.json) | 1,150 | 1,142 | +8 | `form_id` | 1,150/1,142/0 | 0 |
| impl-010 | [stg_hubspot__owner](../records/004_staging_impl-010.json) | 200 | 200 | +0 | `owner_id` | 0/0/200 | 2 |
| impl-010 | [stg_hubspot__ticket](../records/004_staging_impl-010.json) | 1,150 | 1,150 | +0 | `ticket_id` | 0/0/1,150 | 1 |
| impl-010 | [stg_hubspot__ticket_pipeline](../records/004_staging_impl-010.json) | 200 | 1,028 | -828 | `ticket_pipeline_id` | 200/1,028/0 | 0 |
| impl-010 | [stg_hubspot__ticket_pipeline_stage](../records/004_staging_impl-010.json) | 400 | 801 | -401 | `ticket_pipeline_stage_id` | 400/801/0 | 0 |
| impl-011 | [stg_jira__issue](../records/004_staging_impl-011.json) | 8,000 | 8,000 | +0 | `issue_id` | 0/0/8,000 | 3 |
| impl-012 | [stg_marketo__activity_send_email](../records/004_staging_impl-012.json) | 15,000 | 15,000 | +0 | `activity_id` | 0/0/15,000 | 1 |
| impl-012 | [stg_marketo__campaigns](../records/004_staging_impl-012.json) | 4,996 | 4,997 | -1 | `campaign_id` | 0/1/4,996 | 0 |
| impl-012 | [stg_marketo__lead](../records/004_staging_impl-012.json) | 5,984 | 5,990 | -6 | `lead_id` | 0/6/5,984 | 0 |
| impl-013 | [stg_netsuite2__account_types](../records/004_staging_impl-013.json) | 8 | 8 | +0 | `account_type_id` | 0/0/8 | 3 |
| impl-013 | [stg_netsuite2__accounts](../records/004_staging_impl-013.json) | 184 | 184 | +0 | `account_id` | 0/0/184 | 2 |
| impl-013 | [stg_netsuite2__classes](../records/004_staging_impl-013.json) | 0 | 100 | -100 | `class_id` | 0/100/0 | 0 |
| impl-013 | [stg_netsuite2__consolidated_exchange_rates](../records/004_staging_impl-013.json) | 0 | 700 | -700 | `consolidated_exchange_rate_id` | 0/700/0 | 0 |
| impl-013 | [stg_netsuite2__customers](../records/004_staging_impl-013.json) | 2,000 | 2,000 | +0 | `customer_id` | 0/0/2,000 | 1 |
| impl-013 | [stg_netsuite2__entities](../records/004_staging_impl-013.json) | 0 | 700 | -700 | `entity_id` | 0/700/0 | 0 |
| impl-014† | [stg_qualtrics__block_question](../records/004_staging_impl-014.json) | 23,996 | 24,000 | -4 | `block_id, question_id` | 0/0/23,996 | 0† |
| impl-014† | [stg_qualtrics__contact_mailing_list_membership](../records/004_staging_impl-014.json) | 7,981 | 8,000 | -19 | `contact_id, mailing_list_id` | 0/0/7,981 | 1† |
| impl-014† | [stg_qualtrics__core_contact](../records/004_staging_impl-014.json) | 4,994 | 8,000 | -3,006 | `contact_id` | 0/0/4,994 | 0† |
| impl-014 | [stg_qualtrics__directory_mailing_list](../records/004_staging_impl-014.json) | 1,000 | 1,000 | +0 | `mailing_list_id` | 0/0/1,000 | 2 |
| impl-014 | [stg_qualtrics__distribution](../records/004_staging_impl-014.json) | 3,000 | 3,000 | +0 | `distribution_id` | 0/0/3,000 | 4 |
| impl-014† | [stg_qualtrics__distribution_contact](../records/004_staging_impl-014.json) | 5,996 | 6,000 | -4 | `distribution_id, contact_id` | 0/0/5,996 | 0† |
| impl-014† | [stg_qualtrics__question_option](../records/004_staging_impl-014.json) | 43,506 | 48,000 | -4,494 | `question_id, key` | 0/0/43,506 | 0† |
| impl-014† | [stg_qualtrics__question_response](../records/004_staging_impl-014.json) | 71,989 | 72,000 | -11 | `response_id, question_id` | 0/0/71,989 | 0† |
| impl-014† | [stg_qualtrics__sub_question](../records/004_staging_impl-014.json) | 11,693 | 12,000 | -307 | `question_id, key` | 0/0/11,693 | 0† |
| impl-014 | [stg_qualtrics__survey](../records/004_staging_impl-014.json) | 6,000 | 6,000 | +0 | `survey_id` | 0/0/6,000 | 2 |
| impl-014† | [stg_qualtrics__survey_embedded_data](../records/004_staging_impl-014.json) | 5,998 | 6,000 | -2 | `response_id, key` | 0/0/5,998 | 0† |
| impl-014 | [stg_qualtrics__survey_version](../records/004_staging_impl-014.json) | 12,000 | 12,000 | +0 | `version_id` | 0/0/12,000 | 1 |
| impl-014 | [stg_qualtrics__user](../records/004_staging_impl-014.json) | 1,987 | 1,982 | +5 | `user_id` | 5/0/1,982 | 0 |
| impl-015 | [stg_quickbooks__invoice_line](../records/004_staging_impl-015.json) | 20,000 | 20,000 | +0 | `invoice_id, bundle_id, sales_item_item_id, sales_item_account_id, sales_item_class_id, sales_item_tax_code_id, account_id, discount_account_id, discount_class_id, discount_tax_code_id, group_line_detail_group_item_id` | 20,000/20,000/0 | 0 |
| impl-015 | [stg_quickbooks__item](../records/004_staging_impl-015.json) | 2,000 | 2,000 | +0 | `item_id` | 0/0/2,000 | 1 |
| impl-015 | [stg_quickbooks__payment_line](../records/004_staging_impl-015.json) | 6,000 | 6,000 | +0 | `payment_id, linked_txn_payment_id` | 3,762/6,000/0 | 0 |
| impl-015 | [stg_quickbooks__vendor](../records/004_staging_impl-015.json) | 1,500 | 1,500 | +0 | `vendor_id` | 0/0/1,500 | 1 |
| impl-016 | [stg_workday__personal_information](../records/004_staging_impl-016.json) | 5,196 | 5,195 | +1 | `personal_info_history_id` | 1/0/5,195 | 0 |
| impl-016 | [stg_workday__position](../records/004_staging_impl-016.json) | 4,000 | 4,000 | +0 | `position_id` | 0/0/4,000 | 1 |
| impl-017 | [stg_greenhouse__candidate](../records/004_staging_impl-017.json) | 2,000 | 1,999 | +1 | `candidate_id` | 1/0/1,999 | 0 |
| impl-017† | [stg_greenhouse__candidate_tag](../records/004_staging_impl-017.json) | 1,999 | 2,000 | -1 | `candidate_id, tag_id` | 0/0/1,999 | 0† |
| impl-017† | [stg_greenhouse__eeoc](../records/004_staging_impl-017.json) | 1,846 | 2,000 | -154 | `application_id` | 0/0/1,846 | 0† |
| impl-017† | [stg_greenhouse__email_address](../records/004_staging_impl-017.json) | 1,890 | 2,000 | -110 | `candidate_id` | 0/0/1,699 | 0† |
| impl-017† | [stg_greenhouse__hiring_team](../records/004_staging_impl-017.json) | 1,999 | 2,000 | -1 | `job_id, user_id` | 0/0/1,999 | 0† |
| impl-017† | [stg_greenhouse__job_department](../records/004_staging_impl-017.json) | 1,488 | 1,500 | -12 | `job_id, department_id` | 0/0/1,488 | 0† |
| impl-017† | [stg_greenhouse__job_office](../records/004_staging_impl-017.json) | 1,193 | 1,200 | -7 | `job_id, office_id` | 0/0/1,193 | 0† |
| impl-017† | [stg_greenhouse__phone_number](../records/004_staging_impl-017.json) | 1,900 | 2,000 | -100 | `candidate_id, phone_index` | 0/0/1,900 | 0† |
| impl-017† | [stg_greenhouse__social_media_address](../records/004_staging_impl-017.json) | 1,879 | 2,000 | -121 | `candidate_id` | 0/0/1,674 | 0† |
| impl-018 | [stg_salesforce__contact](../records/004_staging_impl-018.json) | 3,000 | 3,000 | +0 | `contact_id` | 0/0/3,000 | 14 |
| impl-018 | [stg_salesforce__contact_history](../records/004_staging_impl-018.json) | 2,434 | 3,000 | -566 | `history_unique_key` | 2,434/2,434/0 | 0 |
| impl-018 | [stg_salesforce__lead](../records/004_staging_impl-018.json) | 2,996 | 3,000 | -4 | `lead_id` | 0/4/2,996 | 11 |
| impl-018 | [stg_salesforce__opportunity](../records/004_staging_impl-018.json) | 3,000 | 3,000 | +0 | `opportunity_id` | 0/0/3,000 | 2 |
| impl-018 | [stg_salesforce__opportunity_line_item](../records/004_staging_impl-018.json) | 3,000 | 3,000 | +0 | `opportunity_line_item_id` | 0/0/3,000 | 2 |
| impl-018 | [stg_salesforce__order](../records/004_staging_impl-018.json) | 3,000 | 3,000 | +0 | `order_id` | 0/0/3,000 | 1 |
| impl-018 | [stg_salesforce__task](../records/004_staging_impl-018.json) | 2,998 | 3,000 | -2 | `task_id` | 0/2/2,998 | 0 |
| impl-018 | [stg_salesforce__user](../records/004_staging_impl-018.json) | 993 | 1,000 | -7 | `user_id` | 0/7/993 | 0 |
| impl-019† | [stg_apple_store__app_session_daily](../records/004_staging_impl-019.json) | 2,963 | 2,959 | +4 | `date_day, app_id, app_version, device` | 3/0/84 | 7† |
| impl-020 | [stg_intercom__admin](../records/004_staging_impl-020.json) | — | — | — | `—` | —/—/— | — |
| impl-020 | [stg_intercom__contact_history](../records/004_staging_impl-020.json) | 2,707 | 2,707 | +0 | `contact_id` | 0/0/2,707 | 1 |
| impl-020 | [stg_intercom__conversation_contact_history](../records/004_staging_impl-020.json) | 4,033 | 4,033 | +0 | `contact_id, conversation_id` | 4,033/4,033/0 | 0 |
| impl-020 | [stg_intercom__conversation_part_history](../records/004_staging_impl-020.json) | 7,524 | 7,524 | +0 | `conversation_part_id` | 0/0/7,524 | 2 |
| impl-020 | [stg_intercom__team](../records/004_staging_impl-020.json) | — | — | — | `—` | —/—/— | — |
| impl-020 | [stg_intercom__team_admin](../records/004_staging_impl-020.json) | — | — | — | `—` | —/—/— | — |
| impl-021 | [stg_klaviyo__campaign](../records/004_staging_impl-021.json) | 2 | 184 | -182 | `campaign_id` | 0/1/2 | 0 |
| impl-021 | [stg_klaviyo__event](../records/004_staging_impl-021.json) | 2,500 | 4 | +2,496 | `event_id` | 2,496/0/4 | 0 |
| impl-021 | [stg_klaviyo__flow](../records/004_staging_impl-021.json) | 1 | 79 | -78 | `flow_id` | 0/1/1 | 0 |
| impl-021 | [stg_klaviyo__metric](../records/004_staging_impl-021.json) | 1 | 29 | -28 | `metric_id, integration_id` | 0/28/1 | 0 |
| impl-021 | [stg_klaviyo__person](../records/004_staging_impl-021.json) | 2 | 1,192 | -1,190 | `person_id` | 0/1/2 | 0 |
| impl-022 | [stg_recharge__address](../records/004_staging_impl-022.json) | 3,000 | 3,000 | +0 | `address_id` | 0/0/3,000 | 1 |
| impl-022 | [stg_recharge__charge_line_item](../records/004_staging_impl-022.json) | 4,000 | 4,000 | +0 | `charge_line_item_id` | 0/0/4,000 | 1 |
| impl-022 | [stg_recharge__customer](../records/004_staging_impl-022.json) | 2,463 | 2,460 | +3 | `customer_id` | 3/0/2,460 | 0 |
| impl-022 | [stg_recharge__order_line_item](../records/004_staging_impl-022.json) | 2,500 | 2,500 | +0 | `order_line_item_id` | 0/0/2,500 | 1 |
| impl-022† | [stg_recharge__subscription_history](../records/004_staging_impl-022.json) | 3,500 | 3,500 | +0 | `subscription_id` | 0/1,833/1,667 | 1† |
| impl-023 | [stg_social_media__account_history](../records/004_staging_impl-023.json) | 0 | 2,500 | -2,500 | `id, business_id` | 0/2,498/0 | 0 |
| impl-023 | [stg_social_media__facebook_posts](../records/004_staging_impl-023.json) | 0 | 138 | -138 | `id` | 0/138/0 | 0 |
| impl-023 | [stg_social_media__instagram_posts](../records/004_staging_impl-023.json) | 0 | 119 | -119 | `post_id, ig_post_id, page_id` | 0/119/0 | 0 |
| impl-023 | [stg_social_media__linkedin_posts](../records/004_staging_impl-023.json) | 100 | 100 | +0 | `organization_id, post_id` | 0/0/100 | 1 |
| impl-023 | [stg_social_media__twitter_organic_tweets](../records/004_staging_impl-023.json) | 0 | 129 | -129 | `account_id, date, organic_tweet_id, placement` | 0/129/0 | 0 |
| impl-023 | [stg_social_media__twitter_user_history](../records/004_staging_impl-023.json) | 1 | 12 | -11 | `id` | 0/3/1 | 4 |
| impl-023 | [stg_social_media__youtube_videos](../records/004_staging_impl-023.json) | 0 | 152 | -152 | `video_id, channel_id` | 0/152/0 | 0 |
| impl-024 | [stg_tiktok_ads__ad_group_history](../records/004_staging_impl-024.json) | 2,504 | 2,504 | +0 | `ad_group_id` | 0/0/2,504 | 3 |
| impl-024 | [stg_tiktok_ads__ad_history](../records/004_staging_impl-024.json) | 2,509 | 2,509 | +0 | `ad_id` | 0/0/2,509 | 1 |
| impl-024 | [stg_tiktok_ads__advertiser](../records/004_staging_impl-024.json) | 200 | 200 | +0 | `advertiser_id` | 0/0/200 | 1 |
| impl-025 | [stg_twilio__account_history](../records/004_staging_impl-025.json) | 2,475 | 2,470 | +5 | `account_id` | 5/0/2,470 | 0 |
| impl-025 | [stg_twilio__call](../records/004_staging_impl-025.json) | 2,492 | 2,492 | +0 | `call_id` | 0/0/2,492 | 2 |
| impl-025 | [stg_twilio__incoming_phone_number](../records/004_staging_impl-025.json) | 1,495 | 1,495 | +0 | `incoming_phone_number_id` | 0/0/1,495 | 1 |
| impl-025 | [stg_twilio__message](../records/004_staging_impl-025.json) | 2,495 | 2,495 | +0 | `message_id` | 0/0/2,495 | 2 |
| impl-026 | [stg_twitter_ads__account_history](../records/004_staging_impl-026.json) | 2,487 | 2,487 | +0 | `account_id` | 0/0/2,487 | 1 |
| impl-026 | [stg_twitter_ads__campaign_history](../records/004_staging_impl-026.json) | 2,489 | 2,489 | +0 | `campaign_id` | 0/0/2,489 | 2 |
| impl-026 | [stg_twitter_ads__campaign_locations_report](../records/004_staging_impl-026.json) | 1,500 | 1,500 | +0 | `account_id, campaign_id` | 0/0/1,500 | 1 |
| impl-026 | [stg_twitter_ads__campaign_regions_report](../records/004_staging_impl-026.json) | 1,500 | 1,500 | +0 | `account_id, campaign_id, date_day, region, country, placement` | 1,500/1,500/0 | 0 |
| impl-026 | [stg_twitter_ads__campaign_report](../records/004_staging_impl-026.json) | 2,000 | 2,000 | +0 | `account_id, campaign_id` | 0/0/2,000 | 3 |
| impl-026 | [stg_twitter_ads__line_item_history](../records/004_staging_impl-026.json) | 2,500 | 2,500 | +0 | `line_item_id` | 0/0/2,500 | 4 |
| impl-026 | [stg_twitter_ads__line_item_keywords_report](../records/004_staging_impl-026.json) | 1,500 | 1,500 | +0 | `account_id, line_item_id` | 0/0/1,500 | 2 |
| impl-026 | [stg_twitter_ads__line_item_report](../records/004_staging_impl-026.json) | 2,000 | 2,000 | +0 | `account_id, line_item_id` | 0/0/2,000 | 1 |
| impl-026 | [stg_twitter_ads__promoted_tweet_report](../records/004_staging_impl-026.json) | 2,500 | 2,500 | +0 | `account_id, promoted_tweet_id, date_day, placement` | 2,500/2,500/0 | 0 |
| impl-026 | [stg_twitter_ads__tweet](../records/004_staging_impl-026.json) | 2,489 | 2,489 | +0 | `tweet_id` | 0/0/2,489 | 1 |
| impl-027 | [stg_xero__invoice_line_item](../records/004_staging_impl-027.json) | 5,000 | 5,000 | +0 | `invoice_id, line_item_id` | 0/0/5,000 | 5 |
| impl-027 | [stg_xero__journal](../records/004_staging_impl-027.json) | 3,500 | 3,500 | +0 | `journal_id` | 0/0/3,500 | 3 |
| impl-027 | [stg_xero__journal_line](../records/004_staging_impl-027.json) | 8,000 | 8,000 | +0 | `journal_line_id` | 0/0/8,000 | 4 |
| impl-028 | [stg_youtube__channel_basic](../records/004_staging_impl-028.json) | 3,500 | 150 | +3,350 | `date_day, channel_id, video_id` | 2,951/30/0 | 0 |
| impl-028 | [stg_youtube__channel_demographics](../records/004_staging_impl-028.json) | 2,509 | 9,450 | -6,941 | `date_day, channel_id, video_id, country_code` | 2,504/450/0 | 0 |
| impl-028 | [stg_youtube__video](../records/004_staging_impl-028.json) | 2,501 | 5 | +2,496 | `video_id` | 2,501/5/0 | 0 |
| impl-029 | [stg_zendesk__schedule_holiday](../records/004_staging_impl-029.json) | 51 | 51 | +0 | `schedule_holiday_id` | 0/0/51 | 1 |
| impl-030 | [stg_zuora__account](../records/004_staging_impl-030.json) | 3,791 | 3,791 | +0 | `account_id` | 0/0/3,791 | 5 |
| impl-030 | [stg_zuora__amendment](../records/004_staging_impl-030.json) | 267 | 267 | +0 | `amendment_id` | 0/0/267 | 2 |
| impl-030 | [stg_zuora__contact](../records/004_staging_impl-030.json) | 3,741 | 3,741 | +0 | `contact_id` | 0/0/3,741 | 1 |
| impl-030 | [stg_zuora__credit_balance_adjustment](../records/004_staging_impl-030.json) | 6 | 6 | +0 | `credit_balance_adjustment_id` | 0/0/6 | 2 |
| impl-030 | [stg_zuora__invoice](../records/004_staging_impl-030.json) | 1,041 | 1,045 | -4 | `invoice_id` | 1/5/1,040 | 10 |
| impl-030 | [stg_zuora__invoice_item](../records/004_staging_impl-030.json) | 1,495 | 1,495 | +0 | `invoice_item_id` | 0/0/1,495 | 11 |
| impl-030 | [stg_zuora__invoice_payment](../records/004_staging_impl-030.json) | 6 | 6 | +0 | `invoice_payment_id, account_id, account_receivable_accounting_code_id, accounting_period_id, bill_to_contact_id, cash_accounting_code_id, created_by_id, default_payment_method_id, invoice_id, journal_entry_id, journal_run_id, parent_account_id, payment_id, payment_method_id, sold_to_contact_id, updated_by_id` | 5/6/0 | 0 |
| impl-030 | [stg_zuora__order](../records/004_staging_impl-030.json) | 5 | 5 | +0 | `order_id` | 0/0/5 | 1 |
| impl-030 | [stg_zuora__payment](../records/004_staging_impl-030.json) | 722 | 722 | +0 | `payment_id` | 0/0/722 | 10 |
| impl-030 | [stg_zuora__payment_method](../records/004_staging_impl-030.json) | 1,037 | 1,037 | +0 | `payment_method_id` | 0/0/1,037 | 1 |
| impl-030 | [stg_zuora__product](../records/004_staging_impl-030.json) | 164 | 164 | +0 | `product_id` | 0/0/164 | 2 |
| impl-030 | [stg_zuora__product_rate_plan](../records/004_staging_impl-030.json) | 505 | 505 | +0 | `product_rate_plan_id` | 0/0/505 | 3 |
| impl-030 | [stg_zuora__rate_plan](../records/004_staging_impl-030.json) | 5 | 5 | +0 | `rate_plan_id` | 0/0/5 | 5 |
| impl-030 | [stg_zuora__rate_plan_charge](../records/004_staging_impl-030.json) | 4 | 4 | +0 | `rate_plan_charge_id` | 0/0/4 | 6 |
| impl-030 | [stg_zuora__refund](../records/004_staging_impl-030.json) | 3 | 3 | +0 | `refund_id` | 0/0/3 | 1 |
| impl-030 | [stg_zuora__refund_invoice_payment](../records/004_staging_impl-030.json) | 3 | 3 | +0 | `refund_invoice_payment_id` | 0/0/3 | 1 |
| impl-030 | [stg_zuora__subscription](../records/004_staging_impl-030.json) | 732 | 732 | +0 | `subscription_id` | 0/0/732 | 1 |
| impl-030 | [stg_zuora__taxation_item](../records/004_staging_impl-030.json) | 534 | 534 | +0 | `taxation_item_id` | 0/0/534 | 14 |

impl-020 的 `stg_intercom__admin`、`stg_intercom__team`、`stg_intercom__team_admin` 在两边都没有实际表，原 CFS 仍将其列为不匹配；本次照实列入，不补建表或假设行数为零。

### 5. 结构化文件与核对结果

- `records/004_staging_impl-001.json` 至 `004_staging_impl-030.json`：逐题完整表结构、行数、键字段与选择依据、NULL/空键数量、键集合差异、逐列差异计数和真实样例。
- [004_staging_summary.csv](../records/004_staging_summary.csv)：176 行总表，另含全部共同列的差异列数、类型差异列数、键选择规则和当前官方匹配布尔值。
- [004_staging_overview.json](../records/004_staging_overview.json)：任务范围、每题目标表数、比较口径、Python/DuckDB 版本与官方代码哈希。
- [004_staging_input_integrity.json](../records/004_staging_input_integrity.json)：60 个预测/gold 数据库、30 份契约、30 份最终 CFS JSON、官方配置和代码，共 122 个原件的前后大小、mtime 和 SHA-256，全部一致。
- [004_staging_independent_checks.json](../records/004_staging_independent_checks.json)：对 4 个真实任务的选定表/列，用独立 SQL 重算不同键数、共同键数与列值多重集合最少差异配对数，全部与程序结果一致。
- [004_staging_validation.json](../records/004_staging_validation.json)：目标数和 CSV 行数、键集合恒等式、样例数量、缺表未知值和计数分解检查均通过；10 个内存数据夹具测试通过。全体共同列中有正值差异的列共 478 个，保存 1,383 条样例键记录；这两个计数包含官方配置外的补充列，不能当作官方评分指标。

结构化文件只保存汇总、schema 和有限样例，没有复制数据库或完整数据表。没有读取真实凭据；已知凭据格式检查未命中。

## 证据来源

- 位置说明：[HANDOVER](../traces/dacomp_deimpl_prev/HANDOVER.md)、[003 号报告](003_2026-10-27_DAComp轨迹接收核对.md)。
- 预测库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-NNN/agent/dacomp-de-impl-NNN/<database_file>`。
- gold：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-NNN/<database_file>`；初始契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-NNN/docs/data_contract.yaml`。实际逐题库名、读取路径和哈希见输入完整性文件。
- 选集依据：`data/dacomp_deimpl_prev/runs/20261025_de_batch_review_02/scoring/impl-NNN/cfs/score.json` 的 staging `comparison_results=false`，即 003 号核实的最终 CFS 文件。
- 官方口径：`/home/katherine/dac/benchmarks/DAComp-code/dacomp-de/evaluation_suite/utils.py` 的 `CoreAccuracyEvaluator.compare_table`，重点为第 155–175 行的 compare_cols、第 198–209 行的字符串规范化与 hash；同目录 `evaluation_config_compare.yaml` 给出逐表列清单。
- [机械比对脚本](../scripts/compare_dacomp_staging.py)、[内存夹具测试](../scripts/test_compare_dacomp_staging.py)。本次实际执行：

```bash
PYTHONDONTWRITEBYTECODE=1 /home/katherine/dac/.venv-openhands/bin/python scripts/compare_dacomp_staging.py
PYTHONDONTWRITEBYTECODE=1 /home/katherine/dac/.venv-openhands/bin/python -m unittest discover -s scripts -p test_compare_dacomp_staging.py -v
```

另用 Python/DuckDB 只读 SQL 对真实结果抽查，并用标准库核对文件哈希、结构化计数和样例数量。运行环境为 Python 3.12.15、DuckDB 1.5.6，没有安装或升级依赖。

## 不确定或没查到的

- 30 张表存在非唯一共同键组，无法据现有对齐字段确认唯一原始行对应；本次提供每列值多重集合与最少差异配对数，精确逐行差异仍需额外的唯一键定义。总表 † 行不应当作已获得精确错误行数。
- 没有明确业务主键的表采用了已列出的推定字段/组合；即使观察到双边唯一，也不能据此证明其业务含义。选择依据和候选唯一性均已记录。
- impl-020 的三张配置表在双方均不存在，行数、键和值比较无法计算；已检查双方 `information_schema.columns`，没有用猜测补成空表。
- impl-020 原契约含不合法 YAML 转义，严格解析失败；本次仅在内存中转义反斜杠以提取表名、列名和约束标识，逐题 JSON 标明该 parse mode。没有改原文件、执行契约规则或据此解释数据差异。
- 本次不判断差异来源、责任、静默失败、gold 正确性或未核实假设。对 intermediate/marts 等其他层没有开展比对。

## 建议的下一步

先审阅 staging 总表及逐列样例。若需要把 † 表的下界进一步变成唯一逐行差异，需由用户明确更细的对齐键或重复行对应规则，再按明确规则复算；其他层的比对另行指定。
