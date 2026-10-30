"""Reviewed table-level findings; rank independent changes by manual §5."""
from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'records'
inv=json.loads((R/'024_package_inventory.json').read_text());plans={x['table']:x for x in json.loads((R/'024_patch_plan.json').read_text())}
for x in json.loads((R/'024_supplement_patch_plan.json').read_text()):
 if x['table'] in plans:plans[x['table']]['patches']+=x['patches']
def setcat(t,label,cat,why=None):
 x=next(x for x in plans[t]['patches'] if x['label']==label);x['category']=cat
 if why:x['reason']=why
for label in ['tweet_join_account','user_join_source','user_latest','screen_clean']:setcat('stg_social_media__twitter_organic_tweets',label,'A','契约给来源但未细定连接关系；本项仅检验SQL差异，单改不减少评测规模。')
# U requires a decisive agent-visible alternative, not agreement with gold alone.
ucs={
 'stg_zuora__contact':['account_id'],
 'stg_zuora__credit_balance_adjustment':['account_id','invoice_id'],
 'stg_zuora__order':['account_id'],
 'stg_zuora__payment':['account_id','payment_method_id'],
 'stg_zuora__payment_method':['account_id'],
 'stg_zuora__rate_plan':['account_id','product_id','product_rate_plan_id','subscription_id'],
 'stg_zuora__rate_plan_charge':['account_id','product_id','product_rate_plan_id','rate_plan_id'],
 'stg_zuora__refund':['payment_method_id'],
 'stg_zuora__subscription':['account_id'],
 'stg_zuora__taxation_item':['product_id'],
 'stg_zuora__invoice_payment':['account_id','payment_id','payment_method_id']}
for t,cols in ucs.items():
 for col in cols:setcat(t,'source_'+col,'U','P：本实体id可替代'+col+'。原可见数据中所选id与相应实体表零匹配，具名外键有匹配且非空候选为ID格式；轨迹event45按统一pk_alias盲目覆盖，未核对该关系。核实数字见实际纳入行的候选映射及格式查询。')
# Trace findings, never classify a work checklist as strategy disclosure.
meta={}
def put(t,summary,tier='看到了但没提',events=None,quote='',rule='',direct=None,confidence='高',flags=None):meta[t]=dict(summary=summary,tier=tier,events=events or [],quote=quote,rule=rule,direct=direct,confidence=confidence,flags=flags or [])
put('social_media_reporting__twitter_posts_reporting','created_timestamp取tweet_created_at而非契约明确的组内min(date)，75行差异单改后L0全匹配。',events=[17,18,31])
put('social_media_reporting__youtube_videos_reporting','page_name来自channel_title；gold来自上游page_name，152个名称不同。契约没有把“channel title”唯一绑定至两列之一。',events=[17,18,31],confidence='中',rule='契约“channel title”可理解为上游channel_title（O），或两种名称列未明确映射（A）。选择A；没有只凭gold选列判断U。')
put('social_media_reporting__retention_kpis','额外过滤NULL page_id，丢掉一个cohort的13个week-offset行；删除这一处过滤L0全匹配。',events=[19,20,33])
put('social_media_reporting__rollup_report','只有两种rank在impressions并列块内重新分配；去掉rank后L0全匹配，每个并列块rank多重集也完全一致。',events=[19,20,33],direct='O')
put('stg_social_media__account_history','agent按BIGINT及非空键契约过滤后0行；gold保留2500个VARCHAR键，另保留或置空不合timezone表达式的值。','针对本表的具体说明',[53],"`account_history.id` 在源中为 VARCHAR，但契约要求 BIGINT；不可转换的键按无效主键处理并删除。",rule='类型投影、键非空过滤与timezone过滤相互遮蔽，单改均不降低规模。直接核实gold类型和契约冲突归O，不按零改善标X；组合诊断剩11个timezone格。',direct='O')
put('stg_social_media__linkedin_posts','created_timestamp采用历史created_time；该关联全不匹配，gold采用同步时间。契约未指定该时间源；同步时间可用不等于业务创建时间正确。','针对本表的具体说明',[53],"LinkedIn staging 契约指定的关联源表缺少可直接匹配的 UGC 历史主键，关联历史中的 `created_time` 无匹配时为空",confidence='中',rule='历史关联零匹配可读为U，但同步时间不证明创建时间语义，选择A。')
put('stg_social_media__twitter_organic_tweets','契约date为DATE；gold保留带时刻TIMESTAMP，导致129+129行键全不配对。仅放宽日期投影后L0全匹配。',events=[15,16,23,24,29])
put('stg_social_media__twitter_user_history','agent输出契约BIGINT id及计数，gold保留非数值VARCHAR id和DOUBLE计数；11行因此过滤，另有4格类型表示差异。',events=[15,16,23,24,29],direct='O',rule='BIGINT投影与非空过滤两处互相遮蔽；分别修不会恢复有正确原键的行，直接类型诊断归O。五个计数字段按五处单改。')
put('stg_social_media__youtube_videos','page_name两种源列选择造成152格，gold与契约FLOOR不一致另外影响estimated_shares 66格及engagement_rate 133格。',events=[15,16,23,24,29],confidence='中')
for t in ['tiktok_ads__ad_report','tiktok_ads__url_report']:
 put(t,'CS各上游source_relation是不同raw表名。agent额外要求相等，使ads/维度连接失配；多处连接和投影叠加，单改均未减少规模，组合诊断L0全匹配。',events=[33,41,42],rule='多处C互相遮蔽，最大单项改善为0或负数，§5未规定这种已定位交互如何排序。依§9主要类别记C（直接契约诊断），不选虚构的唯一主因，不把联改记为单改，也不将零改善项列参与因素。ad_report另有advertiser_id来源未明A选择；单改无贡献。',direct='C',confidence='中')
put('stg_tiktok_ads__ad_group_history','source_relation字面量未规定；agent按header解析完整age_groups和budget，gold取截断数组/前一位置。三处各减少2504格。',events=[11,12,15,16,41,42],confidence='中',rule='CSV header提供字段定位，agent完整解析和gold简单split不同；按字段含义/原值冲突归O，未规定source_relation常量归A。若将字段含义也视作不够明确，可读A；保留该边界供审阅。')
put('stg_tiktok_ads__ad_history','base_url在landing_page无http scheme时为NULL，gold直接保留原文本；契约没有规定base_url构造法，单改此处L0全匹配。',events=[41,42,45,46],confidence='中')
put('stg_twilio__incoming_phone_number','agent先剥离电话标点并补+1，再校验；契约要求原电话格式失败置NULL，1484行单改后L0全匹配。',events=[15,16,17,21,22,25,26])
put('stg_twilio__message','from与to两处均先规范化电话再校验，违背格式失败置NULL；to单改按行减少10，from单改减少8，故to主因、from参与。',events=[15,16,17,21,22])
put('stg_twitter_ads__account_history','一条带空白timezone，agent直接fallback UTC；gold先trim。契约correct未指定策略。','针对本表的具体说明',[35],'The contract requests correction of unsupported timezones without specifying a fallback; invalid timezone values are set to `UTC`.',confidence='中')
put('stg_twitter_ads__tweet','一条非规范lang按契约不在枚举置NULL，gold先lower/trim得到en。',events=[9,10,13],rule='枚举失败nullify的原式执行支持O；若把标准化视为隐含可读A。本次不新增隐含标准化，选择O。')
for suffix in ['campaign_regions_report','campaign_report','line_item_keywords_report','line_item_report','promoted_tweet_report']:
 t='stg_twitter_ads__'+suffix
 summary='契约date_day为TIMESTAMP，gold实际为DATE；键中含日期时格式差异造成独有行。未提供的conversion指标0/NULL另逐列检验，未命中评测列或被键遮蔽的不算因素。'
 if suffix=='line_item_keywords_report':summary+=' keyword_id文本或组合MD5也未在契约定义，单改与日期改动各减少1500格。'
 put(t,summary,events=[9,10,13,21,22,35],confidence='中' if suffix in ['campaign_report','line_item_keywords_report'] else '高')
put('stg_twitter_ads__line_item_history','agent按契约BIGINT、DECIMAL(18,2)/(18,1)输出，gold为DOUBLE且budget两位小数。四个位置分别诊断，主要类型差异按行排序。',events=[9,10,13])
put('twitter_ads__promoted_tweet_report','currency错取line_items而非契约campaigns；2012行改善为主因，另campaign_id错误保留未匹配外键影响20行。',events=[9,10,19])
put('twitter_ads__url_report','campaign_id错取line_items外键而非匹配后的campaigns维度；8行单改L0全匹配。',events=[9,10,19])
put('stg_xero__invoice_line_item','五个数值表达式按契约DECIMAL(18,2)输出，gold保留DOUBLE；quantity单改减少最多行，其余四处各有较小贡献。',events=[17,18,19])
put('stg_xero__journal','两个时间字段依契约转TIMESTAMP，gold保留原文本；另INVALID/BAD前缀数字契约允许清洗，gold置NULL。',events=[17,18,19])
put('xero__invoice_line_items','除浮点SUM累加末位外，差异在契约明确允许任意序的重复line_item_id上产生line_seq和累计值变化；209个并列组，去掉两列后L2全匹配。',events=[21,23,27,28,39],direct='O',rule='运行时浮点累加顺序与允许的并列行序同属O；不把SUM改写造成的偶然行数改善解释为agent数据错误。诊断排除列仅用于确认O，官方判错状态不变。')
put('xero__profit_and_loss_report','契约允许并列项任意序的逐行累计，agent ROWS而gold默认RANGE使并列组累计相同；8个并列组，其他列L0全匹配。',events=[23,39],direct='O',rule='ROWS逐行任意序与RANGE整组累计并非单纯重排，但契约描述running total且ties nondeterministic支持agent；按gold与契约行为冲突归O，另浮点差异L2消失。')
put('int_youtube__video','CS gold staging的5条thumbnail文本均可解析；default/medium/high三处regex各多转义一层，单处修复各减少5格，均I。','针对本表的具体说明',[41,42,55],'视频表 `snippet_thumbnails`、`snippet_tags` 等原始字段类型为 DOUBLE 且样例中为空，不能提供 YAML 描述的 URL/标签字符串；视频 thumbnail URLs 因而为空',confidence='高',rule='该说明描述agent自己输入未能验证URL解析；CS改用gold上游后仍须评估本节点代码。不把原输入缺失传播成不可评估。')
for t in ['stg_youtube__channel_basic','stg_youtube__video']:
 put(t,'逐张确认直接读取agent/initial同一raw表且内容差集为0；gold读取另一组名称、schema和行数均不同的raw表，满足不可评估。','针对本表的具体说明',[23,24,55],'原始数据的 `channel_basic` 缺少 contract 字段 `channel_title`、`video_title`、`deleted`、`viewers`、`views_percentage`、部分 card/playlist 字段等；`video` 源缺少或类型与 contract 不同的缩略图、标签、语言、区域限制等字段。',direct='不可评估')
put('zuora__account_overview','items_by_account使用INNER JOIN，遗漏有invoice但无item的账户0计数；契约明确应0，454行单改L0全匹配。',events=[47,59,60])
put('zuora__monthly_recurring_revenue','month_spine额外排除NULL service_start_day，少一行；移除spine过滤L0全匹配，另一处分类输入过滤单改无贡献。',events=[49,59,60])
for r in inv:
 t=r['table']
 if r['task']!='impl-030' or r['layer']!='staging':continue
 if t=='stg_zuora__account':put(t,'gold未按契约类型转换tax_exempt_status、余额等字段；agent BOOLEAN/BIGINT/DOUBLE符合契约，主要是tax_exempt_status。','只有通用策略说明',[69],'非关键不可解析值转为 NULL。')
 elif t=='stg_zuora__product':put(t,'契约两个有效日期为DATE，gold保留含时刻VARCHAR；两处各减少160格且L3消失。','只有通用策略说明',[69],'非关键不可解析值转为 NULL。')
 else:
  put(t,'统一pk_alias将不同关系字段都映射本实体id；各输出位置独立修复。具名候选能与相关表形成明确对应的按U，其余源字段错位或无法定语义的按A；契约类型与gold透传冲突按O。','只有通用策略说明',[13,14,39,40,45,69],'Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。',confidence='中',flags=['证据曾出现但被忽略'] if t in ucs else [])
meta['stg_zuora__amendment']['summary']='subscription_id的具名源267条中261条是时间文本，仅2条匹配subscription；数据不足以确定业务映射，归A。created_by_id按契约BIGINT但gold透传文本，另为O因素。'
meta['stg_zuora__product_rate_plan']['summary']='product_id具名候选仅2/505匹配product，其余与所选id均无关系证据；契约未给映射，保守A。两处DATE与gold文本的O因素独立列出。'
meta['stg_zuora__invoice_payment']['rule']='四处关系键互相遮蔽，单改行/格减量全为0。§5所有单项仍并列，§3并列U只需前三条件且减量相等；§4又规定零改善不算因素。按§9选择仅把三个已验证U与未定invoice_id来源A记为零改善多因并列（低把握），不声称U严格第4条件通过；另一读法是只能保留U标记而无法指定主因。组合诊断L1匹配仅定位交互，不作单点证据。'
meta['stg_zuora__invoice_payment']['direct']='多因并列（A、U）';meta['stg_zuora__invoice_payment']['confidence']='低'
meta['stg_zuora__invoice_item']['rule']='多数具名候选呈错位文本/时间或NULL，不能只因gold选同名列就归U；选择A。processing_type等显式类型冲突为O；互相并列按格子比较。'
meta['stg_zuora__taxation_item']['rule']='多数ID候选和主表均不匹配，按A；只有product_id的5个非空值全部匹配product而本实体id零匹配，按U。不把完整表大部分NULL当成有匹配证据。'
# Lock remains unchanged; post-blind corrections are explicitly distinguished from blind conclusions.
cal=json.loads((R/'024_calibration_blind_decisions.json').read_text())
for r in inv:
 if r['purpose']!='校准':continue
 t=r['table'];rr=json.loads((R/f"024_reruns_{r['task']}_{t}.json").read_text());patches=[]
 for v in rr['runs'][1:]:
  label=v['label']
  if r['task']=='impl-006':cat='I' if label=='spend' else 'D' if label in ['video_views','upvotes','downvotes','comments'] else 'A'
  else:cat='O' if label in ['organization_maturity_level','organization_size_category'] else 'C'
  patches.append(dict(label=label,edits=[[e['old'],e['new']] for e in v['edits']],category=cat,reason=('生成字典先正确映射spend后被重复key覆盖' if cat=='I' else '有明确可用原始候选列却直接NULL' if cat=='D' else '契约没有指定来源/公式/缺失默认值；不能从gold选择反推唯一语义' if cat=='A' else '契约短枚举与gold全称冲突' if cat=='O' else '契约给出了零分母及连接/计分做法'),P=None))
 if t=='workday__organization_overview':
  for z in json.loads((R/'024_supplement_patch_plan.json').read_text()):
   if z['table']==t:patches+=z['patches']
 plans[t]=dict(task=r['task'],table=t,patches=patches)
 if r['task']=='impl-006':put(t,'20处各减少1200格；spend字典被覆盖I，四个可映射原指标直接NULL为D，其余未定口径/默认值为A。','只有通用策略说明',[18,19,30,95],'对缺失源字段采用类型明确的 NULL',rule='盲标把三处直接TRY_CAST不可解析指标记U、部分派生NULL记D；复核契约未给公式，观察到不可解析也不能证明agent假设可解析，撤回U。派生口径亦未规定，改A。本修订发生在解盲后，不计作盲标一致。',confidence='中',flags=['已披露'])
 else:put(t,'两处零分母漏0为C，两处契约短枚举与gold全称冲突为O，各减少117格；连接权重5格、角色聚合106格为C参与因素。',events=[30,56,72,81],rule='盲标将短枚举看作描述性缩写而归A；解盲后逐列复核契约确实列出New/Young及Empty/Micro等标签，按字面规则归O。锁定盲标原判断不改。',confidence='中')
# Derive §5 scale rankings; positive contribution is lexicographic row/cell reduction.
dec=[]
for r in inv:
 t=r['table'];m=meta[t];paths=[R/f"024_reruns_{r['task']}_{t}.json",R/f"024_supplement_reruns_{r['task']}_{t}.json"];runs={};base=None
 for path in paths:
  if not path.exists():continue
  d=json.loads(path.read_text());base=base or d['runs'][0]['comparison']
  for v in d['runs'][1:]:runs[v['label']]=(v,str(path.relative_to(ROOT)))
 b=base['levels'][0];ps=[]
 for x in plans.get(t,{}).get('patches',[]):
  v,path=runs[x['label']];c=v['comparison']['levels'][0];dr=b['row_scale']-c['row_scale'];dc=b['cell_scale']-c['cell_scale'];strict=v['comparison']['first_match'] in ['L0','L1','L2'] or (dr>=b['row_scale']/2 if dr else dc>=b['cell_scale']/2)
  tier=m['tier'];quote=m['quote'];events=m['events']
  if t=='stg_reddit_ads__campaign_report' and x['label'] in ['click_through_rate','cost_per_click','cost_per_thousand_impressions']:tier='看到了但没提';quote='';events=[18,30]
  if t.startswith('stg_twitter_ads__') and x['label'] in ['keyword_id','conversion_purchases_metric','conversion_custom_metric','conversion_purchases_sale_amount','conversion_custom_sale_amount']:
   tier='针对本表的具体说明' if x['label']=='keyword_id' else '只有通用策略说明';events=[35];quote='The raw keyword report does not contain `keyword_id`; that field is derived from available `keyword` text, so uniqueness beyond keyword text is not guaranteed.' if x['label']=='keyword_id' else 'The raw Twitter report tables do not contain the contract’s conversion metric or conversion sale amount columns. Staging emits typed NULLs for these unavailable values; the intermediate logic treats them as zero per contract.'
  ps.append({**x,'row_reduction':dr,'cell_reduction':dc,'strict_u4':strict,'comparison':v['comparison'],'record':path,'tier':tier,'quote':quote,'events':events})
 positive=[x for x in ps if (x['row_reduction'],x['cell_reduction'])>(0,0) and x['label']!='roles_join']
 if m['direct']:
  main=[];factors=[];category=m['direct']
  if t=='stg_zuora__invoice_payment':main=[x for x in ps if x['label'].startswith('source_')]
 else:
  assert positive,t
  best=max((x['row_reduction'],x['cell_reduction']) for x in positive);main=[x for x in positive if (x['row_reduction'],x['cell_reduction'])==best];factors=[x for x in positive if x not in main];cats=sorted({x['category'] for x in main});category=cats[0] if len(cats)==1 else '多因并列（'+'、'.join(cats)+'）'
  for x in main:
   if x['category']=='U' and len(main)==1:assert x['strict_u4'],(t,x['label'],'U4 failed')
 # direct O tables still retain real independent reductions for transparency, no arbitrary ranking of execution order.
 if m['direct']=='O':factors=[]
 dec.append({**r,**m,'category':category,'main_labels':[x['label'] for x in main],'main':main,'factors':factors,'patches':ps,'baseline':base})
(R/'024_decisions.json').write_text(json.dumps(dec,ensure_ascii=False,indent=2)+'\n')
print([(d['table'],d['category']) for d in dec])
