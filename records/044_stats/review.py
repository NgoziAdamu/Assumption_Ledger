"""生成条件影响清单；不改对象/点标签，不把备选读法当作已成立的判定。"""
import json
from collections import Counter
import prepare as P

def build():
    aa=json.loads((P.OUT/'object_audit.json').read_text());oo={r['object_id']:r for r in aa};out=[]
    counts={b:Counter(r['main_category'] for r in aa if r['benchmark']==b) for b in ['DAComp','KramaBench']}
    def shift(o,new):
        r=oo[o];old=r['main_category'];c=counts[r['benchmark']];excluded={'其他','不可评估','无法判定','未交卷','只能组合修复'};d=191 if r['benchmark']=='DAComp' else 19
        dd=int(new not in excluded)-int(old not in excluded)
        return f'主因{old} {c[old]}→{c[old]-1}，{new} {c[new]}→{c[new]+1}；分母一不变；分母二 {d}→{d+dd}'+('，分母二所有非零类别比例均随分母变化' if dd else '')+'。'
    def add(o,source,alternative,impact,group='v3人工复核清单'):
        out.append(dict(object_id=o,benchmark=oo[o]['benchmark'],current_main=oo[o]['original_main'],source=source,group=group,conditional_alternative=alternative,conditional_impact=impact))
    src='用户在044会话补充的《标注检查台账_v3》6对象清单（2026-11-03）'
    add('archeology-hard-2',src,'Unstated Choice主因，Data Misconception参与',shift('archeology-hard-2','Unstated Choice')+'参与其中Choice和Data各+1；探索对象10→11、Data对象3→4。若原主点第3档保持：Choice第3档4/8→5/9，Choice+Downgrade第3档5/9→6/10，五机制说出2/18→2/19。新增Data点的证据/曾正确字段未给，不能确定对应分子增量。根源口径同样变化。')
    add('archeology-hard-5',src,'Unstated Choice + Intent Misreading跨阶段并列',shift('archeology-hard-5','多因并列')+'跨阶段并列0→1；Choice与Intent参与各+1，其他参与−1。若保持未披露：五机制说出2/18→2/19。探索对象10→11，Intent对象8→9；新探索点字段未定，证据/曾正确分子不能预设。单一Choice/Downgrade五档不纳入该并列对象。')
    add('archeology-hard-12',src,'不认候选组第1档；已说出的选择改为Unstated Choice','两标签本已合并为Choice，主因8/42、8/19及参与其中完全不变。第1档说出2/18→1/18（分母二总说出2/19→1/19）；Choice第1档2/8→1/8。第2～5档归属尚未指定，因此第3档4/8与合计5/9是否+1不能确定；第1+2档敏感性是否下降亦取决于新档位。')
    add('archeology-easy-8',src,'脏条目合并的性质仍未定','不能预设类别。若最终仍为其他，所有数字不变；若转为分母二内任一类别，其他18→17、该类别+1、分母二19→20，分母二各类非零比例随分母变化；若转为不可评估/无法判定，分母二仍19。档位/证据分子随具体复核结果而定。')
    add('impl-018_stg_salesforce__opportunity_line_item',src,'两个外键点的第3档改第4档','对象主因仍为代码写错13/336、13/191；两点的类别和角色不变。代码写错不进五档分布，Choice/Downgrade第3档2/98不变；“说出”布尔值仍为否，悄悄出错仍162（旧160）。仅逐点审计记录的两个档位由3变4；依任务要求不汇报代码写错档位分布，根源计主因不变。')
    add('impl-020_int_intercom__conversation_part_aggregates',src,'Data Misconception主因改Intent Misreading',shift('impl-020_int_intercom__conversation_part_aggregates','Intent Misreading')+'两类参与其中Data17→16、Intent61→62，探索去重对象75不变；证据是原否，Data证据1/17→1/16、Intent61/61→61/62，探索合计62/75不变；曾正确Data12/17→12/16、Intent0/61→0/62，合计12/75不变。两类主因第4档分别−1/+1；说出与悄悄出错不变。根源分母二Data3→2、Intent37→38，分母168不变。')
    extra='036～043仍保留的对象边界（不是照搬026旧建议）'
    add('impl-007_stg_apple_store__sales_subscription_event_summary','notes/036_2026-10-31_按v3.1修订试点.md §新的规则问题1','组级意识第3档→第4档','主因Choice和参与数不变。Choice第3档2/60→1/60，Choice+Downgrade第3档2/98→1/98；第4档相应+1。第1/第1+2档说出不变；新旧悄悄出错都不变。',extra)
    add('environment-hard-18','notes/036_2026-10-31_按v3.1修订试点.md §新的规则问题3','若定性终点不足以支持组合修复、改为无法判定（仅条件示例）',shift('environment-hard-18','无法判定')+'主要类别之外的探索参与字段是否保留，取决于复核是否也撤销现有点证据；不可预定。',extra)
    scenarios=[
      ('impl-003_customer360__customer','037','Unstated Choice→Intent Misreading','Intent Misreading','Choice参与−1、Intent参与+1；Choice五档第2档−1、Intent第2档+1。探索证据/曾正确字段需复核补定；第1档说出、悄悄出错不变。'),
      ('impl-002_stg_pendo__user','037','Data Misconception→Unstated Choice','Unstated Choice','Data参与−1、Choice参与+1；该对象另有Intent参与，探索合计对象数不变。Data证据1/17→1/16、曾正确12/17→12/16；探索合计62/75和12/75不变；第2档从Data移入Choice；悄悄出错不变。'),
      ('impl-008_int_asana__project_health_indicators','039','zero_denominator_policy：代码写错→Intent Misreading','Intent Misreading','Intent参与+1；探索对象+1，证据/曾正确新字段未定；Intent第4档+1。代码写错移出后五机制说出分母178→179，分子25不变；悄悄出错不变。count_joined_tasks已经按新标签Choice参与，不执行026旧建议。'),
      ('impl-013_netsuite2_customer_analytics','040','主因second_join：Intent Misreading→Unstated Choice','Unstated Choice','该对象仍有另一Intent参与且已有Choice参与，两类参与对象数均不变；两类主因第4档−1/+1。探索对象/证据/曾正确按仍在的Intent点保留；悄悄出错不变。'),
      ('impl-015_stg_quickbooks__invoice_line','042','代码写错→Data Misconception','Data Misconception','Data参与+1、探索对象+1；新探索字段未给，证据/曾正确分子不预设。Data第4档+1；五机制说出分母178→179、分子25不变；悄悄出错不变。'),
      ('impl-030_stg_zuora__product_rate_plan','043','少量目标匹配是否足以定Data；若改Unstated Choice','Unstated Choice','Data参与−1、Choice参与+1；该对象Data点证据否、曾正确是：探索对象75→74、证据62/75→62/74、曾正确12/75→11/74。Data证据1/17→1/16、曾正确12/17→11/16；两类主因第2档−1/+1。悄悄出错不变；同根源混合集合已有两类，根源主因集合不变。')]
    for o,n,alt,new,detail in scenarios:
        source=str(next((P.ROOT/'notes').glob(n+'_*.md')).relative_to(P.ROOT))+' §规则问题/不确定'
        add(o,source,alt,shift(o,new)+detail,extra)
    add('impl-012_marketo__calendar_spine','notes/040_2026-11-01_DAComp重标第四批.md §规则问题1','通用说明第2档→针对本处说明第1档','基础Choice类别60不变；五机制主口径说出25/178→26/178，分母二说出25/191→26/191；第1+2档口径不变。Choice第2档−1、第1档+1。新悄悄出错162/1069→161/1069、162/187→161/187；旧160/1069→159/1069、160/183→159/183。',extra)
    add('impl-011_int_jira__issue_calendar_spine','notes/039_2026-11-01_DAComp重标第三批.md §规则问题4','仅history_driver参与点：其他→Choice','主因Intent及两个分母不变；Choice参与+1、其他参与−1；档位取主点所以所有说出/意识数字不变。新旧悄悄出错均不变。',extra)
    add('impl-011_jira__stakeholder_engagement_insights','notes/039_2026-11-01_DAComp重标第三批.md §规则问题4','仅cross_functional_projects参与点：其他→Choice（若采用另一读法）','主因多因并列30不变，Choice参与+1，其他参与仍存在所以不减；主点和披露口径不变，悄悄出错不变。若连带更改其他并列点或排序，现有指定不足以确定增量。',extra)
    add('impl-013_int_netsuite2__financial_ratios','notes/040_2026-11-01_DAComp重标第四批.md §规则问题2','若五个空集总额点全部从Choice改Intent',shift('impl-013_int_netsuite2__financial_ratios','Intent Misreading')+'Choice参与−1、Intent参与+1，探索对象+1；主因第4档从Choice移到Intent。若只改两个并列主点之一，则Choice主因−1、多因并列+1、跨阶段并列+1；分母二不变。未给新证据/曾正确字段，不推算相应分子。',extra)
    add('impl-027_xero__profit_and_loss_report','notes/043_2026-11-03_DAComp重标第六批.md §规则问题4','若累计窗口差异改为Choice（条件示例）',shift('impl-027_xero__profit_and_loss_report','Unstated Choice')+'Choice参与+1、其他参与−1；Choice第4档+1，五机制说出25/178→25/179。新悄悄出错162→163、agent错分母187→188；旧160→161、183→184。',extra)
    # 038关于可恢复数值的边界按当前角色列清楚，非原因绝不自动晋升。
    for suffix in ['google_ads__account_report','google_ads__ad_group_report','twitter_ads__campaign_report','linkedin_ads__campaign_report','snapchat_ads__campaign_report','tiktok_ads__campaign_report']:
        o='impl-006_stg_'+suffix
        if suffix=='google_ads__account_report':impact=shift(o,'Data Misconception')+'若仅两个并列主点之一改Data，则Choice−1、多因并列+1、跨阶段并列+1。Data参与+1；五档第2档随主因迁移；悄悄出错不变。'
        elif suffix in ['google_ads__ad_group_report','tiktok_ads__campaign_report']:impact='涉及数值政策的点当前为非原因；只改其类别且角色不动时，所有对象级主因、参与、档位、证据、悄悄出错数字均不变，仅按点附表对应类别转移。'
        else:impact='若只把相关数值政策Choice点改Data且角色不动，主因仍多因并列；Data参与对象+1，其他Choice点仍在，Choice参与不减少。Twitter/LinkedIn这些点为参与，跨阶段并列不变；Snapchat若改的是quartile等并列点，跨阶段并列+1。新增探索字段需复核；悄悄出错不变。'
        add(o,'notes/038_2026-11-01_DAComp重标第二批.md §规则问题1','相关数值恢复政策Choice→Data（保持角色）',impact,extra)
    add('impl-007_int_app_health_metrics','notes/038_2026-11-01_DAComp重标第二批.md §规则问题3','若把窗口并列顺序明确视为允许、改其他',shift('impl-007_int_app_health_metrics','其他')+'Choice参与−1、其他参与+1；Choice五档相应档位−1。新悄悄出错已排除impl-007，所以162/187不变；旧悄悄出错160/183→159/182。',extra)
    for o,impact in [
      ('impl-023_stg_social_media__twitter_user_history','harmful_filter、empty_filter均非原因；仅类别互换对所有对象统计影响0。'),
      ('impl-024_stg_tiktok_ads__ad_group_history','age_groups_parser并列Choice若改其他，另有source_relation并列Choice、budget并列其他，故主因仍多因并列，Choice/其他参与计数不变。只有若改为探索类别，才新增该类参与1、跨阶段并列1；当前主口径未说出不变。'),
      ('impl-028_int_youtube__video','published_type为非原因，只改该点类别影响对象统计0，三处代码写错主因不变。'),
      ('impl-009_stg_google_play__store_performance_country','若只把主因编码Choice改Form，Choice主因−1、Form+1，分母不变；该对象另有Data参与，Choice参与−1、Form参与+1，探索合计不变；五档从Choice移出，悄悄出错不变。'),
      ('impl-006_stg_reddit_ads__campaign_report','若四个候选指标由Choice改Downgrade，现有并列项仍含代码写错、Choice、Downgrade，因此主要原因、参与对象数、说出与悄悄出错全不变；只变按点类别数。')]:
        batch='043' if not o.startswith('impl-009') else '042'
        add(o,str(next((P.ROOT/'notes').glob(batch+'_*.md')).relative_to(P.ROOT))+' §规则问题','按报告所列另一读法；保持已有角色和其他点',impact,extra)
    P.dump('manual_review_impacts.json',out)
    return out
if __name__=='__main__':build()
