"""v3.2逐点判定。键名来自单改定位；类别根据契约/轨迹重新指定，不转换024标签。"""
I='Intent Misreading'; U='Unstated Choice'; O='其他'; D='Data Misconception'; C='代码写错'
# table -> label -> (category, reason, relevant contract term)
RULES={
'social_media_reporting__twitter_posts_reporting':{
 'created_timestamp':(I,'契约明确取组内earliest date；实现改取tweet_created_at，改变时间值，是算法理解而非形式。','earliest')},
'social_media_reporting__youtube_videos_reporting':{
 'page_name':(U,'契约称channel title，但上游channel_title与page_name两列并存，没有指定源列；不以gold选择page_name作为映射事实。','page_name'),
 'impressions':(I,'契约明确views来自source clicks，agent使用impressions；本数据单改无改善，仍记录未落实的规格前提。','views come from the source clicks field')},
'social_media_reporting__retention_kpis':{
 'cohort_date_type':(O,'cohort_week契约为DATE；agent显式DATE符合要求，改成gold的时间类型反而增加差异。','cohort_week'),
 'null_page':(I,'输入规则只按created_timestamp是否存在过滤，随后为每个page/platform建立cohort；额外排除NULL page_id丢失13个spine行。','only keep rows where created_timestamp is present')},
'stg_social_media__account_history':{
 'id_type':(O,'契约id明确BIGINT且not_null；原始2500个id均不可转数值，agent按契约转换，gold保留文本。','name: id'),
 'id_filter':(O,'BIGINT转换后NULL键按明确not_null排除；输出0行符合该要求，不能归为agent误解数据。','constraints: [not_null]'),
 'timezone_filter':(O,'契约给出timezone正则并要求delete_row；agent按该表达式过滤，gold保留部分不合规则值。','timezone ~')},
'stg_social_media__linkedin_posts':{
 'created_source':(U,'created_timestamp只声明类型，未指定历史created_time或同步时间。交付报告明确LinkedIn历史时间无匹配会为空；不能从gold同步时间倒推要求。','created_timestamp'),
 'message_source':(U,'post_message未指定article_title/media_title/commentary或合成字符串，内容选择未被材料定下。','post_message'),
 'content_type':(U,'content_type无映射或默认值规则；从content.type取值与常量text属于未定选择。','content_type')},
'stg_social_media__twitter_organic_tweets':{
 'tweet_join_account':(U,'契约未指定完整联接条件；是否附带account_id限制未定，单改未改善。','source_table'),
 'user_join_source':(U,'source列表不足以确定由account_id还是tweet.user_id关联用户，现有核实未证明唯一正确对应；保留Choice。','source_table'),
 'user_latest':(U,'契约没有明确用户历史版本选择算法；去掉latest限定单改不改善。','source_table'),
 'screen_clean':(U,'此表未给screen_name清洗表达式，不能借另一张user_history契约推广到本表。','screen_name'),
 'date_projection':(O,'本表契约date为DATE，agent据此截为日；gold保留时刻且date在评测键中，差异源于规格与gold类型不同。','name: date')},
'stg_social_media__twitter_user_history':{
 'screen_regex':(I,'契约给出可执行REGEXP_REPLACE且无g，agent添加全局替换；按字面表达式而非推测清洗本意。','REGEXP_REPLACE'),
 'harmful_filter':(I,'契约描述含有害字符的行删除；agent先全部清洗后保留，未保留原值删除检查。规则先后有另一读法，列入规则问题。','harmful characters'),
 'empty_filter':(O,'契约描述NULL/blank行删除；agent排除清洗后空串有自然读法支持。gold保留不构成agent未确立的错误前提；先后边界记中把握。','NULL/blank'),
 'id_projection':(O,'id要求BIGINT，gold保留非数值文本，agent类型符合规格。','name: id'),
 'id_filter':(O,'id明确not_null，转换失败后排除符合规格；单改放行反而增差。','constraints: [not_null]')},
'stg_social_media__youtube_videos':{
 'channel_relation':(U,'契约未规定同channel资料多版本如何选；max与保留distinct资料属于未定选择。','channel_info'),
 'channel_title':(U,'channel_title没有Unknown默认值规则；NULL与占位字符串未定。','channel_title'),
 'page_name':(U,'page_name未指定视频snippet标题或channel_display_name，属于源字段选择。','page_name'),
 'estimated_shares':(O,'契约明确FLOOR(likes/10)，agent照做；gold的整数CAST采用不同取整。','FLOOR'),
 'engagement_shares':(O,'契约明确engagement使用estimated_shares，agent使用其FLOOR值；gold分子用未FLOOR值。','likes + comments + estimated_shares')},
'tiktok_ads__ad_report':{
 'campaign_projection':(I,'维度属性来自最新匹配维表，缺匹配应NULL；直接投影ads外键保留孤儿值违背规定。','Dimension attributes come from the latest snapshots'),
 'ad_group_projection':(I,'输出ad_group维度属性应来自匹配维表；直接投影ads外键改变缺失时行为。','if a joined record is missing'),
 'advertiser_join':(U,'本表仅写matching advertiser_id，没有指定从ads还是ad_groups取；不能借url_report的更具体规则推断本表。','advertiser on matching advertiser_id'),
 'ads_source_join':(I,'契约首个ads联接只写ad_id，后两个联接明确另列source_relation；统一补source条件改变给定联接。','ads on matching ad_id')},
'tiktok_ads__url_report':{
 'adgroup_source_join':(I,'契约列出ads.ad_group_id对应维表，未要求附加source_relation；附加条件使CS中来源名不同的维度无法匹配。','ads.ad_group_id'),
 'campaign_source_join':(I,'契约明确ads.campaign_id对应维表；额外source_relation条件改变规则。','ads.campaign_id'),
 'ads_source_join':(I,'契约明确hourly.ad_id对应ads；额外source_relation条件改变规则。','hourly.ad_id')},
'stg_tiktok_ads__ad_group_history':{
 'source_relation':(U,'契约未定来源标识粒度：平台tiktok_ads还是各raw表名。它影响后续跨表对应，不只是同标签换拼法。','source_relation'),
 'interest_category':(O,'原始header将INTEREST_CATEGORY_V_2放在59位；agent按header取列，gold读56位AUDIENCE。来源列证据而非gold选择确定含义。','interest_category'),
 'languages':(O,'原始header的LANGUAGES位于65，agent按该位置；gold的67是NETWORK_TYPES。差异不由agent误读源列造成。','languages'),
 'budget':(O,'header的BUDGET为39位，gold读取38位FALLBACK_TYPE；agent按明确列名取预算并遵循numeric校验。','budget is numeric'),
 'age_groups_parser':(U,'原始AGE_GROUPS含引号及内部逗号；契约只要求VARCHAR，未定解析/序列化写法。agent保留完整数组字符串，gold逗号切割截断；不把gold失败当作数据事实。','age_groups')},
'stg_tiktok_ads__ad_history':{
 'source_relation':(U,'平台标识还是具体raw表标识的粒度未规定。','source_relation'),
 'base_url':(U,'契约未规定base_url是否保留query等拆解算法；差异是材料未定的选择。','base_url'),
 'url_path':(U,'契约未规定路径前导斜杠和空值表示；两种提取结果未由规格定下。','url_path')},
'stg_twilio__incoming_phone_number':{
 'phone_number_normalized':(I,'明确要求原电话匹配+1正则，失败nullify_field；先去标点补+1将本应置空的值改成有效，改变失败动作。','phone_number RLIKE'),
 'friendly_trim':(U,'规格验证TRIM(friendly_name)，没明确输出值也须TRIM。','TRIM(friendly_name)')},
'stg_twilio__message':{
 'from_normalized':(I,'契约规定from正则验证失败置空；预先去标点补+1改变验证对象和失败动作。','name: message_from'),
 'to_normalized':(I,'契约规定to正则验证失败置空；预先标准化将非法原值变为合法值。','name: message_to')},
'twitter_ads__promoted_tweet_report':{
 'currency_source':(I,'currency的来源明确是campaigns，agent改取line_items。','currency'),
 'campaign_projection':(I,'campaign_id应来自匹配后的campaigns；直接用line_items外键保留了无对应维度的值。','campaign_id'),
 'line_item_projection':(I,'line_item_id应来自匹配line_items，直接用promoted_tweets外键；单改不改善。','line_item_id')},
'twitter_ads__url_report':{
 'campaign_projection':(I,'契约明确campaign_id来自campaigns，agent取line_items的外键，缺维度时结果不同。','campaign_id')},
'stg_twitter_ads__account_history':{
 'timezone_trim':(U,'契约要求correct不支持的时区，未定trim还是UTC兜底；agent说明了UTC处理。','timezone')},
'stg_twitter_ads__line_item_history':{
 'bid_amount_local_micro':(O,'契约明确BIGINT，agent照做；gold保留DOUBLE。','bid_amount_local_micro'),
 'bid_amount':(O,'契约明确DECIMAL(18,2)，agent照做；gold以DOUBLE输出。','name: bid_amount'),
 'total_budget_amount_local_micro':(O,'契约明确BIGINT，agent照做；gold保留DOUBLE。','total_budget_amount_local_micro'),
 'total_budget_amount':(O,'契约明确DECIMAL(18,1)，agent按一位小数输出；gold使用两位小数。','name: total_budget_amount')},
'stg_twitter_ads__tweet':{
 'language_normalize':(O,'契约给出语言枚举、非法值nullify；agent按原值验证，gold另做lower/trim接受不在原枚举的值。','language')},
'xero__invoice_line_items':{
 'sum_gross':(O,'窗口SUM与分组SUM的浮点累加末位不同，L2数值容差与其余列诊断定位此差异；不是未确立的数据前提。','invoice_gross_nonneg'),
 'sum_net':(O,'同一非负net求和仅累加方式不同，末位差异在L2消失；契约没有规定浮点累加次序。','invoice_net_nonneg')},
'xero__profit_and_loss_report':{
 'window_frame':(O,'契约running total允许并列行顺序不确定，agent ROWS逐行累计符合自然读法；gold RANGE将并列组一起累计，其他内容诊断一致。另一读法是仅允许展示顺序不确定，本次按逐行累计的自然读法取其他、中把握。','ties are nondeterministic')},
'stg_xero__journal':{
 'processed_at':(U,'raw没有处理时间列，规格只声明TIMESTAMP，NULL或执行时刻未规定。','processed_at'),
 'created_date_type':(O,'契约要求TIMESTAMP，agent转换；gold保留含UTC后缀的原文本。','created_date_utc'),
 'journal_date_type':(O,'契约要求TIMESTAMP，agent转换；gold保留日期字符串。','journal_date'),
 'invalid_prefix':(O,'契约明确移除字母/特殊符号后保留有效数字；agent照做，gold额外将INVALID/BAD前缀置NULL。','journal_number')},
'int_youtube__video':{
 'default_regex':(C,'SQL意图匹配JSON-like的default.url和空白/花括号，但quoted heredoc中双反斜杠使正则匹配字面反斜杠；是实现转义错误。','default'),
 'medium_regex':(C,'同一JSON-like提取写法的medium表达式多一层转义；逐列单改可复原值，不以原始NULL推断CS不可评估。','medium'),
 'high_regex':(C,'同一JSON-like提取写法的high表达式多一层转义。','high'),
 'default_missing':(O,'缺section/url返回NULL在契约写明；agent NULLIF符合要求，gold返回空串。','if the section or url is missing, return NULL'),
 'medium_missing':(O,'缺section/url返回NULL符合契约；gold空串。','if the section or url is missing, return NULL'),
 'high_missing':(O,'缺section/url返回NULL符合契约；gold空串。','if the section or url is missing, return NULL'),
 'published_type':(O,'契约列声明DATE但又要求原样透传；agent用DATE符合显式列类型，当前单改无改善。两条规格的张力单列规则问题。','snippet_published_at')},
'zuora__account_overview':{
 'invoice_items_left':(I,'契约明确有invoice而无item时计数0；INNER JOIN丢掉这样的账户分组。做法可由规格确定，不用Data覆盖事实替代。','no items')},
'zuora__monthly_recurring_revenue':{
 'spine_null_month':(I,'契约要求覆盖spine的所有account/month；额外非空服务日期过滤丢掉NULL月份行。','spine'),
 'items_null_month':(I,'对分类输入另加非空日期过滤，规则未允许删掉这部分输入；单改未影响最终输出。','service_start_day')},
}
