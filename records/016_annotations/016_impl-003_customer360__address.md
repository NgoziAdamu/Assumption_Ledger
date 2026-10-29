# impl-003 / customer360__address

## 1. 错在哪里

地址内容一致，差异仅为契约明确允许任意排列的同priority地址rank。

已核实：CS上下游地址内容多重集合一致，契约明确同priority的顺序unspecified and non-deterministic；两侧窗口均只ORDER BY priority。014_relaxed_impl-003.json的双侧去rank诊断完全一致。016重跑基线6904行/6904格差异，仅rank列。重复键先抵消完全相同行，再对剩余元组固定排序一一配对；014的3192是独立逐列最少值差异，不是这次同一配对的格子数。归O，未把任选并列排序当作数据假设错误。

## 2. 依据

- 起点：[013精简材料包](../013_packages/013_impl-003_marts_customer360__address.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml` 第1204–1256行。
- [原始轨迹转录](../014_trace_impl-003.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-003.json)；[015三方raw核对](../015_raw_impl-003.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: customer360__address
      description: Consolidated customer addresses from Marketo and Stripe enriched with standardized country/state names and priority-based ranking
      grain: One row per sourced address per customer360_id (duplicates preserved)
      source_models:
      - marts.customer360__mapping
      - intermediate.int_customer360__marketo
      - intermediate.int_customer360__stripe
      - staging.stg_customer360__country_codes
      - staging.stg_customer360__state_territory_codes
      business_logic: '- Read pass-through datasets: - marts.customer360__mapping as mapping (provides marketo_lead_id and stripe_customer_id per customer360_id) - staging.stg_customer360__country_codes as country_codes - staging.stg_customer360__state_territory_codes as state_codes - Build Marketo addresses (inner join mapping.marketo_lead_id = int_customer360__marketo.lead_id): - Primary address: include rows where address_line_1 is not NULL; set source_system = "marketo", address_type = "primary", priority = 1; select address_line_1, address_line_2, city, state_code, country_code, postal_code - Billing address: include rows where billing_address_line_1 is not NULL; set source_system = "marketo", address_type = "billing", priority = 2; map billing_* fields to output columns - Build Stripe addresses (inner join mapping.stripe_customer_id = int_customer360__stripe.customer_id): - Customer address: include rows where customer_address_line_1 is not NULL; set source_system = "stripe", address_type = "customer", priority = 1; map customer_* fields - Shipping address: include rows where shipping_address_line_1 is not NULL; set source_system = "stripe", address_type = "shipping", priority = 2; map shipping_* fields - Union all Marketo and Stripe address rows; no de-duplication; only addresses with non-NULL address_line_1 are included. - Enrich with geographic names via left joins: - state: join state_codes on (state_code AND country_code) to derive state_territory; unmatched → NULL - country and country_alt_name: join country_codes on alpha-2 country code; unmatched → NULL - Compute rank: per customer360_id, assign row numbers ordered by priority ascending; within the same priority, order is unspecified and non-deterministic. - Output passes through source text as-is (casing/whitespace preserved); no normalization beyond the joins.'
      columns:
      - name: customer360_id
        data_type: VARCHAR
        description: Customer key from mapping used to group and rank addresses; multiple rows per customer360_id
      - name: source_system
        data_type: VARCHAR
        description: Origin system literal ('marketo' or 'stripe'); set per source and always non-null
      - name: address_type
        data_type: VARCHAR
        description: 'Address category set per source: Marketo → ''primary'' or ''billing''; Stripe → ''customer'' or ''shipping'''
      - name: address_line_1
        data_type: VARCHAR
        description: Primary address line; rows are included only when this is non-null; text is passed through without trimming or case changes
      - name: address_line_2
        data_type: VARCHAR
        description: Secondary address line from source; may be null; text is passed through without trimming or case changes
      - name: city
        data_type: VARCHAR
        description: City from source; may be null; no transformation
      - name: state_code
        data_type: VARCHAR
        description: State/province code from source used for state name enrichment; may be null; case preserved
      - name: state
        data_type: VARCHAR
        description: Resolved state/territory name from stg_customer360__state_territory_codes via (state_code,country_code) match; null if no match
      - name: country_code
        data_type: VARCHAR
        description: ISO alpha-2 country code from source used for joins; may be null; case preserved
      - name: country
        data_type: VARCHAR
        description: Resolved country name from stg_customer360__country_codes via country_code_alpha_2; null if no match
      - name: country_alt_name
        data_type: VARCHAR
        description: Alternative country name from stg_customer360__country_codes; null if no match
      - name: postal_code
        data_type: BIGINT
        description: Postal code from source stored as BIGINT; may be null; numeric-only storage means leading zeros are not preserved
      - name: priority
        data_type: INTEGER
        description: Address priority set by source (1 for primary/customer, 2 for billing/shipping); lower number indicates higher priority
      - name: rank
        data_type: BIGINT
        description: Row number per customer360_id ordered by priority ascending; ties within the same priority have arbitrary order
```

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__address.sql`
```sql
   1: with mapping as (select * from marts.customer360__mapping), addresses as (
   2:  select m.customer360_id,'marketo' as source_system,'primary' as address_type,s.address_line_1,s.address_line_2,s.city,s.state_code,s.country_code,s.postal_code,1 as priority
   3:  from mapping m join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.address_line_1 is not null
   4:  union all select m.customer360_id,'marketo','billing',s.billing_address_line_1,s.billing_address_line_2,s.billing_city,s.billing_state_code,s.billing_country_code,s.billing_postal_code,2
   5:  from mapping m join intermediate.int_customer360__marketo s on m.marketo_lead_id=s.lead_id where s.billing_address_line_1 is not null
   6:  union all select m.customer360_id,'stripe','customer',s.customer_address_line_1,s.customer_address_line_2,s.customer_city,s.customer_state_code,s.customer_country_code,s.customer_postal_code,1
   7:  from mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id where s.customer_address_line_1 is not null
   8:  union all select m.customer360_id,'stripe','shipping',s.shipping_address_line_1,s.shipping_address_line_2,s.shipping_city,s.shipping_state_code,s.shipping_country_code,s.shipping_postal_code,2
   9:  from mapping m join intermediate.int_customer360__stripe s on m.stripe_customer_id=s.customer_id where s.shipping_address_line_1 is not null
  10: ), enriched as (
  11:  select a.*, st.state_territory as state,cc.country_name as country,cc.alternative_country_name as country_alt_name
  12:  from addresses a left join staging.stg_customer360__state_territory_codes st on a.state_code=st.state_code and a.country_code=st.alpha2_country_code
  13:  left join staging.stg_customer360__country_codes cc on a.country_code=cc.country_code_alpha_2
  14: )
  15: select customer360_id,source_system,address_type,address_line_1,address_line_2,city,state_code,state,country_code,country,country_alt_name,postal_code,priority,
  16:  row_number() over(partition by customer360_id order by priority) as rank from enriched
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__address.sql`
```sql
   1: -- Extract address information from the actual source data
   2: with mapping as (
   3:     select * from marts.customer360__mapping
   4: ),
   5: 
   6: country_codes as (
   7:     select * from staging.stg_customer360__country_codes
   8: ),
   9: 
  10: state_codes as (
  11:     select * from staging.stg_customer360__state_territory_codes
  12: ),
  13: 
  14: -- Extract addresses from Marketo data
  15: marketo_addresses as (
  16:     select 
  17:         m.customer360_id,
  18:         'marketo' as source_system,
  19:         mk.address_line_1,
  20:         mk.address_line_2,
  21:         mk.city,
  22:         mk.state_code,
  23:         mk.country_code,
  24:         mk.postal_code,
  25:         1 as priority,
  26:         'primary' as address_type
  27:     from mapping m
  28:     inner join intermediate.int_customer360__marketo mk 
  29:         on m.marketo_lead_id = mk.lead_id
  30:     where mk.address_line_1 is not null
  31:     
  32:     union all
  33:     
  34:     -- Marketo billing addresses
  35:     select 
  36:         m.customer360_id,
  37:         'marketo' as source_system,
  38:         mk.billing_address_line_1 as address_line_1,
  39:         mk.billing_address_line_2 as address_line_2,
  40:         mk.billing_city as city,
  41:         mk.billing_state_code as state_code,
  42:         mk.billing_country_code as country_code,
  43:         mk.billing_postal_code as postal_code,
  44:         2 as priority,
  45:         'billing' as address_type
  46:     from mapping m
  47:     inner join intermediate.int_customer360__marketo mk 
  48:         on m.marketo_lead_id = mk.lead_id
  49:     where mk.billing_address_line_1 is not null
  50: ),
  51: 
  52: -- Extract addresses from Stripe data
  53: stripe_addresses as (
  54:     select 
  55:         m.customer360_id,
  56:         'stripe' as source_system,
  57:         sc.customer_address_line_1 as address_line_1,
  58:         sc.customer_address_line_2 as address_line_2,
  59:         sc.customer_city as city,
  60:         sc.customer_state_code as state_code,
  61:         sc.customer_country_code as country_code,
  62:         sc.customer_postal_code as postal_code,
  63:         1 as priority,
  64:         'customer' as address_type
  65:     from mapping m
  66:     inner join intermediate.int_customer360__stripe sc 
  67:         on m.stripe_customer_id = sc.customer_id
  68:     where sc.customer_address_line_1 is not null
  69:     
  70:     union all
  71:     
  72:     -- Stripe shipping addresses
  73:     select 
  74:         m.customer360_id,
  75:         'stripe' as source_system,
  76:         sc.shipping_address_line_1 as address_line_1,
  77:         sc.shipping_address_line_2 as address_line_2,
  78:         sc.shipping_city as city,
  79:         sc.shipping_state_code as state_code,
  80:         sc.shipping_country_code as country_code,
  81:         sc.shipping_postal_code as postal_code,
  82:         2 as priority,
  83:         'shipping' as address_type
  84:     from mapping m
  85:     inner join intermediate.int_customer360__stripe sc 
  86:         on m.stripe_customer_id = sc.customer_id
  87:     where sc.shipping_address_line_1 is not null
  88: ),
  89: 
  90: -- Merge all addresses and enhance
  91: all_addresses as (
  92:     select * from marketo_addresses
  93:     union all 
  94:     select * from stripe_addresses
  95: ),
  96: 
  97: enhanced_addresses as (
  98:     select 
  99:         all_addresses.customer360_id,
 100:         all_addresses.source_system,
 101:         all_addresses.address_type,
 102:         all_addresses.address_line_1,
 103:         all_addresses.address_line_2,
 104:         all_addresses.city,
 105:         all_addresses.state_code,
 106:         state_codes.state_territory as state,
 107:         all_addresses.country_code,
 108:         country_codes.country_name as country,
 109:         country_codes.alternative_country_name as country_alt_name,
 110:         all_addresses.postal_code,
 111:         all_addresses.priority,
 112:         row_number() over (partition by all_addresses.customer360_id order by all_addresses.priority) as rank
 113:     from all_addresses
 114:     left join state_codes 
 115:         on all_addresses.state_code = state_codes.state_code 
 116:         and all_addresses.country_code = state_codes.alpha2_country_code
 117:     left join country_codes 
 118:         on all_addresses.country_code = country_codes.country_code_alpha_2
 119: )
 120: 
 121: select * from enhanced_addresses
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.country_codes|gold_vs_initial|True|True|True||
|raw.marketo_leads|gold_vs_initial|True|True|True||
|raw.state_territory_codes|gold_vs_initial|True|True|True||
|raw.stripe_customers|gold_vs_initial|True|True|True||
|raw.zendesk_users|gold_vs_initial|True|True|True||
|raw.country_codes|gold_vs_agent|True|True|True||
|raw.marketo_leads|gold_vs_agent|True|True|True||
|raw.state_territory_codes|gold_vs_agent|True|True|True||
|raw.stripe_customers|gold_vs_agent|True|True|True||
|raw.zendesk_users|gold_vs_agent|True|True|True||

## 3. agent看过什么

event 1提供“within the same priority, order is unspecified and non-deterministic”；event 23直接写入该窗口表达式；event 45检查其他模型约束，没有证据表明本表要求更细排序。

区分event实际展示的契约/数据与磁盘上存在的资料；截断输出中未出现的部分不算agent已经看到。核实查询是标注者新增查询，不冒充agent执行过。

## 4. 查询与重跑

核实查询合计 **0条**（含014复用；本轮新增0条）；核实代价档：**需要查业务说明**。诊断不计入5条上限。查询失败与重复执行如实保留。

无新增数据核实查询；本表依据契约/SQL和只读诊断或重跑判断。

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['customer360_id', 'state_code', 'state', 'country_code', 'country', 'postal_code']`；比较列（与键取并集）：`['address_line_1', 'address_line_2', 'address_type', 'city', 'country', 'country_alt_name', 'country_code', 'customer360_id', 'postal_code', 'priority', 'rank', 'source_system', 'state', 'state_code']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：本次重新执行；原013留存输出另列

共同时间控制：`[]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|38482|38482|0|0|0/0|6663|6663|6663|False|
|L1|38482|38482|0|0|0/0|6663|6663|6663|False|
|L2|38482|38482|0|0|0/0|6663|6663|6663|False|
|L3|38482|38482|0|0|0/0|6663|6663|6663|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|customer360_id|0|0|0|0|
|state_code|0|0|0|0|
|state|0|0|0|0|
|country_code|0|0|0|0|
|country|0|0|0|0|
|postal_code|0|0|0|0|
|address_line_1|0|0|0|0|
|address_line_2|0|0|0|0|
|address_type|0|0|0|0|
|city|0|0|0|0|
|country_alt_name|0|0|0|0|
|priority|0|0|0|0|
|rank|6663|6663|6663|6663|
|source_system|0|0|0|0|

### 重跑 baseline

SQL：`data/016_work/impl-003/baseline.sql`；SHA-256：`27aa8f74a4e65f7b98239b73a67a2bb192c9398550ce744d7cd7807a0d680a5b`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|38482|38482|0|0|0/0|6904|6904|6904|False|
|L1|38482|38482|0|0|0/0|6904|6904|6904|False|
|L2|38482|38482|0|0|0/0|6904|6904|6904|False|
|L3|38482|38482|0|0|0/0|6904|6904|6904|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|customer360_id|0|0|0|0|
|state_code|0|0|0|0|
|state|0|0|0|0|
|country_code|0|0|0|0|
|country|0|0|0|0|
|postal_code|0|0|0|0|
|address_line_1|0|0|0|0|
|address_line_2|0|0|0|0|
|address_type|0|0|0|0|
|city|0|0|0|0|
|country_alt_name|0|0|0|0|
|priority|0|0|0|0|
|rank|6904|6904|6904|6904|
|source_system|0|0|0|0|

排序内容诊断复用：[014_relaxed_impl-003.json](../014_relaxed_impl-003.json)，查询原文及双侧放宽结果在该记录；不把放宽评测叫作单侧修复。

## 5. 类别、把握及与014对比

- 主要原因：**O**。
- 主因对应单项：不适用（评测条件诊断）。
- 参与因素：无。
- 标记：无。
- 把握：**高**。
- 重跑是否满足U第4条件：否：放宽双侧rank比较属于O诊断，不是单侧修复。

不存在必须满足的“priority唯一”假设：契约明确允许并列，代码也能合法处理并列。

与014相比：**否：仍O；本次以一致的重复键配对重算行/格子，数值不与014逐列下界混用。**

## 规则问题

契约已明确允许任意并列顺序，按v1归O。重复键残余行如何配对手册未规定；本次使用完整元组字典序固定配对，保持行/格子/每列计数内部一致，不声称全局最少格子数。

2026-10-29用户确认的第3节补充：仅当本表依赖raw满足agent留存=初始、gold不同，且诊断确认影响可评估性时标“不可评估”；gold=初始、agent不同则照常标注，查轨迹改动。不能把两类混为一谈。若gold与agent一致但二者不同于初始（019/020），当前本节点仍可比较；初始差异另记。

共同执行例外：最初指纹快照因外部v0附件已不在原桌面路径而失败；成功的016快照晚于首批私有重跑。已逐文件与015任务前的大小、mtime、SHA-256比较，覆盖原始库的历史指纹无变化；不把晚快照伪称执行前快照。仓库v0与004–015记录保留。
