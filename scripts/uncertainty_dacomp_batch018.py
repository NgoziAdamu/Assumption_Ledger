"""Explicit, reviewable per-cause v2 decisions; no database queries or source edits."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1];REC=ROOT/'records'
GRADES=['针对本表的具体说明','只有通用策略说明','看到了但没提','没有迹象']

def trace_path(n):return REC/f'{14 if n<=10 else 16 if n<=20 else 17:03}_trace_impl-{n:03}.json'
def previous(n):return json.loads((REC/f'{16 if n<=20 else 17:03}_decisions.json').read_text())[str(n)]
def field(e,name):
    value=e
    for part in name.split('.'):value=value[part]
    return value

# Explicit narrative evidence. A final-report body inside a write command is
# identified as such, including whether the write actually succeeded.
SPEECH={
1:(1,67,'args.final_thought','转换中无法解析的可选字段通过 `TRY_CAST` 保留为 NULL；无效必需值或不合规枚举的记录按适用合同规则过滤。','说明必需值失败过滤的一般策略，未指出application.created_at全部解析失败。'),
3:(1,51,'args.final_thought','契约对来源重复记录以及部分聚合排序并未规定唯一 tie-breaker；按 DuckDB 实际行为保留未指定并列顺序，不额外引入业务假设。','谈多模型未指定并列排序，未点名address的priority/rank。'),
4:(0,51,'args.final_thought','History 原始表没有契约字段 `created_date` / `history_unique_key`，使用源 `_fivetran_start` 作为变更时间，并以 `_fivetran_start` 与 `_fivetran_end` 计算字符串唯一标识；该映射使快照能够按源可用的版本时间运行。','明确指出History同一目标字段的缺源、替代来源及原因；虽然覆盖两张History表，已经定位本表这一选择，不要求重复完整模型名。'),
7:(1,65,'args.command','Apple 订阅 summary/event 字段有若干原始字段与 staging 字段语义不完全一致，使用可用列映射且转换兼容字段类型。若这类字段用于正式订阅财务决策，应以源端字段定义进一步确认。','最终报告正文的写入尝试；event66返回路径不存在，event67再次尝试也失败，归档没有finish.final_thought。仅证明轨迹里写出了报告文字，不声称报告成功送达。未点明subscriber_id选vendor而非促销ID。'),
14:(1,79,'args.final_thought',"原始 Qualtrics 时间文本带时区后缀（例如 `+0800`），DuckDB 直接 `try_cast(... AS TIMESTAMP)` 无法解析。日期相关 SQL 改用 `try_strptime(..., '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP`；不可解析日期在日期计算中排除。",'明确说明日期解析策略，但适用于多个日期模型，未点名survey_version.created_at。'),
17:(1,53,'args.final_thought','staging 对声明为主键的空值行进行过滤，并按主键分组只保留一条记录以满足唯一性；若重复键的内容不一致，合同没有规定优先版本，因而保留记录选择未定义，重复记录中的非键值可能丢失。','主键去重策略及代价明确，未点名candidate_tag这一复合主键或其重复行。'),
20:(0,61,'args.final_thought','原始 conversation part 文件中的实际列数据与源 schema 声明不一致：对话 ID 实际可从 part `id` 的前缀提取，事件时间可从错位的原始 `conversation_id` 字段解析，事件类型可从 `subject` 字段回退获取。','明确点出conversation part错位、conversation_id的替代来源和原因，针对主因。'),
21:(1,41,'args.final_thought','事件 attribution 解析按契约优先级提取 JSON 子事件 ID，查找限定同一 `source_relation`；事件重复保留且照常计数。','共享事件输入的重复保留/计数策略，没有点到person_metrics的missing_day_count或date spine扩行。'),
24:(1,63,'args.final_thought','可选邮箱/名称/手机号字段验证失败时置 NULL，记录仍保留。','相关可选字段失败处理的一般策略，未解释本表邮箱正则接受集合或双点域名。017的三档未区分此层，本次按v2记通用策略。'),
25:(1,41,'args.final_thought','依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。','相关电话失败处理的一般声明；没有说明call.contact_phone_number校验前去符号/补+1。声明与实际代码可有差别，本字段不判断声明正确。另表outgoing_caller_id的具体说明不迁移到本表。'),
27:(0,41,'args.final_thought','Duplicate account codes exist in source; the invoice enrichment chooses one account deterministically by lowest `account_id` to prevent duplicate output line rows. This can discard alternate account attributes for colliding codes.','明确指出invoice enrichment重复account_code、确定性选行、原因和丢失属性的代价。'),
29:(1,55,'args.final_thought','必填字段空值或转换失败的记录按契约过滤；可选字段转换失败会成为 `NULL`。重复记录、枚举和文本规范化没有超出契约进行更改。','适用于本表可选日期的转换失败策略，未点名畸形start_date或是否截前缀。'),
}
URL_SPEECH=(1,59,'args.final_thought','Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.','说明无效可选字段置空的一般策略，未点名guide_event URL正则，也没有证明该规则已落实。')
NULL_SPEECH=(1,97,'args.final_thought','对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。','仅为跨模型缺字段占位策略，不说明本指标为何认为没有候选列或其具体口径；也不能由披露推翻I/D/A归因。')
ACCOUNT_SPEECH=(1,71,'args.final_thought','Fivetran 源表以 `id` 提供若干实体标识，故映射到对应契约目标键（例如 account_id、invoice_id）。非关键不可解析值转为 NULL。','通用实体键映射举例，未说明invoice.account_id这个外键为什么也应取invoice.id；按v2不算针对本表这一处的具体说明。')
TYPE_SPEECH=(1,71,'args.final_thought','合同中少量 staging 与建模字段类型不一致（例如 invoice-item 的 processing_type/金额字段）；严格按 staging 类型输出，在业务比较时对枚举做文本转换。类型不匹配且不可安全解析的数据留下 NULL，不额外推断。','声明跨模型类型冲突时优先staging的一般策略；例子为invoice-item，未点名invoice本项。')

# Relevant actually visible information, not off-screen data or future queries.
# (event, field, exact needle, optional model scope anchor)
OBS={
2:(14,'content',"guide_event [('",None),
5:(14,'content','campaign_base_campaign',None),
6:(18,'content','reddit_ads_campaign_report_data [',None),
8:(1,'args.content','project', 'int_asana__task_projects'),
9:(14,'content','country_region',None),
10:(14,'content','form_data:',None),
11:(10,'content','_time_spent',None),
12:(1,'args.content','first_name = TRIM(first_name)',None),
13:(1,'args.content','80th percentile',None),
15:(14,'content','sales_tax_code_id',None),
16:(1,'args.content','annual_turnover_rate','name: workday__organization_overview'),
18:(14,'content','opportunity_line_item ',None),
19:(1,'args.content','summary','name: apple_store__subscription_report'),
22:(10,'content','subscription_history:',None),
23:(24,'content','facebook_pages_page_data',None),
26:(10,'content','twitter_campaign_locations_report_data',None),
28:(22,'content','youtube_channel_demographics_data',None),
}
LIMIT={
2:'列清单可见原始事件字段。最终报告的event-key generation只是功能清单，没有说明生成键的具体约定；不把该词视为选择及原因。',
5:'看到了两个campaign来源列；最终报告讨论数值/日期、其他mart规则及source_relation，未说明这两个campaign候选的取舍。',
6:'CTR/CPC/eCPM源列可见；最终报告TRY_CAST/缺列占位说明不解释优先直接指标列还是重算公式，不能覆盖这三项来源选择。',
8:'契约已提供项目可缺失信息；最终报告没有说明为什么用右表project_id替代左表。',
9:'看到了数值country_region；最终报告只说处理国家码并讨论另表xyz，没有说明本表转alpha-2的选择。',
10:'可见form_data的schema；没有关于本表原始输入与初始/gold不一致的说明。不可评估仍填写四档，不要求agent能看到gold。',
11:'两个耗时来源字段在schema可见；没有说明COALESCE优先级。',
12:'看到了first/last_name的可执行trim相等校验。报告的缺关键ID/时间/必需属性过滤没有说明首尾空白是先trim还是按原值删行；一般“按契约清理”不当作相关策略说明。',
13:'契约中的分位阈值可见；没有说明采用NTILE而不是连续分位阈值。',
15:'看到了sales/purchase税码候选；报告的缺列填NULL不解释本表实际取sales_tax_code_id的选择。',
16:'契约比率默认0和枚举值均可见。最终报告提到当前任职人数为0及另一张performance表为空，但没有说明本表两个比率零分母处理或枚举取值；“handled nulls and categories”只是功能概述。',
18:'源schema中两个外键可见。event57代码注释表达正确的通用FK意图，用于I归因；它不在思考字段或最终报告中，不自动当作v2第6节的说明。最终报告未讨论本表两外键来源。',
19:'契约连接键和NULL可见；报告的SQL聚合保留NULL、marts缺指标补零指聚合/输出策略，不说明连接键的NULL是否彼此相等。',
22:'本表id和subscription_id可见；关于其他subscription缺列及删除过滤的报告不解释本表历史行身份选择。',
23:'page id与fan_count的schema/样例可见；报告“类型转换”仅功能清单，另有LinkedIn类型说明，均未说明本表URL路由或BIGINT选择。',
26:'看到了VARCHAR日期及样例；报告UTC标记处理、tweet/keyword及conversion缺口不解释本表date_day保留TIMESTAMP还是DATE。',
28:'看到了实际raw表名清单；报告的channel_basic/video缺列说明未点到demographics替代原始表及输入差异。',
}

def main():
    out={}
    for n in range(1,31):
        p=trace_path(n);events=json.loads(p.read_text());byid={e['id']:e for e in events};old=previous(n)
        labels=old['primary'] or (['rank_tie_order'] if n==3 else ['raw_input_mismatch'])
        items=[]
        for label in labels:
            speech=SPEECH.get(n)
            if n==2 and label=='url_rule':speech=URL_SPEECH
            if n==6 and label not in ['click_through_rate','cost_per_click','cost_per_thousand_impressions']:speech=NULL_SPEECH
            if n==30:speech=ACCOUNT_SPEECH if label=='account_source' else TYPE_SPEECH
            if speech:
                grade,event,f,quote,limit=speech
                assert quote in field(byid[event],f),(n,label,event,quote)
                evidence={'event':event,'field':f,'quote':quote,'original_path':byid[event]['path']}
            else:
                grade=2;event,f,needle,anchor=OBS[n];s=field(byid[event],f)
                if n==6:needle={'click_through_rate':"'ctr'",'cost_per_click':"'cpc'",'cost_per_thousand_impressions':"'ecpm'"}[label];anchor='reddit_ads_campaign_report_data ['
                if n==12:needle='first_name = TRIM(first_name)' if label=='first_name_trim_policy' else 'last_name = TRIM(last_name)'
                if n==16:needle={'annual_zero':'annual_turnover_rate','management_zero':'management_ratio','maturity_labels':'organization_maturity_level by','size_labels':'organization_size_category by'}[label]
                if n==23 and label=='followers_representation':needle="'fan_count'";anchor='facebook_pages_page_data'
                start=s.index(anchor) if anchor else 0;pos=s.index(needle,start)
                quote=s[max(start,pos-70):pos+850]
                evidence={'event':event,'field':f,'quote':quote,'original_path':byid[event]['path'],'excerpt_note':'连续原文摘录；不把本次摘录长度当作agent原始可见长度'}
                limit=LIMIT[n]
            items.append({'item':label,'grade':GRADES[grade],'evidence':[evidence],'scope_limit':limit})
        # Audit coverage includes report-writing commands, not just finish events.
        narrative=[];thought=[]
        for e in events:
            if e.get('args',{}).get('final_thought'):narrative.append({'event':e['id'],'field':'args.final_thought'})
            command=e.get('args',{}).get('command','')
            if 'result.md' in command and ('cat >' in command or 'write_text' in command):narrative.append({'event':e['id'],'field':'args.command','kind':'report-writing body; inspect success separately'})
            for f in ['thought','args.thought']:
                try:v=field(e,f)
                except KeyError:continue
                if v:thought.append({'event':e['id'],'field':f,'value':v})
        out[f'impl-{n:03}']={'trace_file':str(p.relative_to(ROOT)),'trace_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'all_event_ids':[e['id'] for e in events],'narrative_fields_reviewed':narrative,'nonempty_thought_fields':thought,'items':items}
    (REC/'018_uncertainty_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print('Wrote per-item v2 uncertainty audit:',len(out),'tables;',sum(len(x['items']) for x in out.values()),'items')
if __name__=='__main__':main()
