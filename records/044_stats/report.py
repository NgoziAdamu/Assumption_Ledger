"""从044结果表生成中文报告，不内嵌手填统计数字。"""
import csv,json
from collections import Counter
import prepare as P
from review import build as review_build
OUT=P.OUT
CATS=['Data Misconception','Intent Misreading','Unstated Choice','Quiet Downgrade','Form Mismatch','代码写错','多因并列','只能组合修复','其他','不可评估','无法判定','未交卷','跨阶段并列']
def load(name):return list(csv.DictReader((OUT/name).open()))
def js(name):return json.loads((OUT/name).read_text())
def fmt(r):
    if r.get('excluded_from_denominator2')=='True':return '—（排除）'
    if not r['proportion']:return f"{r['numerator']}/{r['denominator']}；未定义"
    return f"{r['numerator']}/{r['denominator']} = {float(r['proportion']):.1%} [{float(r['ci95_low']):.1%}, {float(r['ci95_high']):.1%}]"
def table(headers,rows):
    esc=lambda s:str(s).replace('|','\\|').replace('\n','<br>')
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(esc(x) for x in row)+' |' for row in rows])
def main():
    report=[];add=report.append
    v=js('validation.json');aa=js('object_audit.json');root=js('shared_root_catalog.json');bridge=js('historical_bridge.json');reviews=review_build()
    add('# 任务044：错误机制重标总统计（DAComp + KramaBench）\n\n日期：2026-11-03。状态：完成统计，保留人工复核边界。')
    add('## 结论\n\n所有下列比例均写成“分子/分母 = 比例 [95%范围]”。范围是按题聚类的 percentile bootstrap（10,000次，种子20261103），不是标注正确率或人工复核后的确定性范围。')
    for b in ['DAComp','KramaBench']:
        rr=load('main_'+b+'.csv');lookup={(r['metric'],r['denominator_scope']):r for r in rr}
        add('### '+b)
        add(('DAComp 283张正式重标表与013的待标注集合完全一致，另计格式差异19张、日期差异34张；分母一336，分母二191。' if b=='DAComp' else 'KramaBench沿用036的42个对象（包含1个未交卷）；分母一42，分母二19。')+'已说出的选择/降级并回对应基础类别。')
        add(table(['主要原因','分母一','分母二'],[[c,fmt(lookup[(c,'分母一')]),fmt(lookup[(c,'分母二')])] for c in CATS]))
    silent=load('silent_errors.csv');aware=load('awareness.csv')
    add('DAComp悄悄出错：'+fmt(silent[0])+'（全部交付表），'+fmt(silent[1])+'（宣称完成题中agent自己的错）。旧完成判断为'+fmt(silent[3])+'；历史158张参照与本次旧完成160张的逐表净变化是新增7、移出5，再换新完成判断净增2。')
    for b in ['DAComp','KramaBench']:
        r=next(r for r in aware if r['benchmark']==b and r['main_category']=='Unstated Choice + Quiet Downgrade' and r['grade']=='3')
        add(b+'“意识到了却没交代”（只限单一Choice/Downgrade主因）为 '+fmt(r)+'。探索阶段档位另报，不混入此比例。')
    add('## 任务\n\n只汇总冻结手册v3.2下的已完成标注。开始时已确认notes/、records/没有044编号；未顺延编号。未重新判类、未改变任何既有类别/角色/主要原因，13条更正仅在内存作用于036权威试点点记录。未读041；未查询数据库、重跑SQL或调用agent。原标签与统计用类别分别保存在object_audit.json中。')
    add('## 详细发现\n\n### 范围、校准、更正与可复算性')
    add(table(['来源','正式对象数','排除校准对象'],[['036','DAComp 30；KramaBench 42','无']]+[[x['batch'],x['formal_count'],'；'.join(x['excluded_calibration_objects'])] for x in v['scope']['batch_scope']]))
    add('正式DAComp合计30+43+43+40+38+39+50=283，缺漏0、重复0；六批校准共12行对象记录及其全部点均排除，试点只用036标签。全部确认做错336=283+53；sales、utils在分层统计并入marts。13条原值均匹配并生效；逐条见[corrections_applied.json](../records/044_stats/corrections_applied.json)。另存[statistical_merges.json](../records/044_stats/statistical_merges.json)，列出类别合并、同类并列归并与组合修复优先的原主要原因及统计归属；两类日志互不混用。impl-009_stg_google_play__earnings的三项原为已说出的选择/已说出的选择/Unstated Choice，基础类别合并后统计记Choice，原主要原因仍保存为多因并列。')
    combos=[r for r in aa if r['combination_only']]
    add('“只能组合修复”优先单列，不能仅查看主要原因列来排除。DAComp有5张、KramaBench有1道：')
    add(table(['对象','原主要原因','统计行'],[[r['object_id'],r['original_main'],'只能组合修复'] for r in combos]))
    add('参与其中使用主要、并列/组合项和参与因素；同类候选按对象已有主因计，不把非原因点变成参与因素。探索证据率使用主要、并列、同类候选和参与点；组合项单改为零，不当作独立参与因素。两个分母的参与比例都先与对应分母取交集。')
    add('### 参与其中（对象可重复进入不同类别）')
    rr=load('incidence.csv')
    for b in ['DAComp','KramaBench']:
        cats=list(dict.fromkeys(r['metric'] for r in rr if r['benchmark']==b));idx={(r['metric'],r['denominator_scope']):r for r in rr if r['benchmark']==b}
        add('**'+b+'**\n\n'+table(['类别','分母一','分母二'],[[c,fmt(idx[(c,'分母一')]),fmt(idx[(c,'分母二')])] for c in cats]))
    add('### DAComp按层主要原因\n\nsales（2张重标表）、utils（1张重标表）并入marts；额外53张其他也按013中的层加入分母一。')
    rr=load('layers.csv')
    for layer in ['staging','intermediate','marts']:
        idx={(r['metric'],r['denominator_scope']):r for r in rr if r['layer']==layer}
        add('**'+layer+'**\n\n'+table(['主要原因','层内分母一','层内分母二'],[[c,fmt(idx[(c,'分母一')]),fmt(idx[(c,'分母二')])] for c in CATS[:-1]]))
    add('### 说没说出来\n\n主点取角色“主要”；同类主因并列取全部主点。用户确认：并列项经基础类别归并后若只剩一种，统计归入该类别，主口径取最弱档（最大档号），敏感性仍对原主点取any。仅earnings符合此例，档位1/1/4归第4档。跨类并列直接计算all/any布尔条件，不纳入单一类别五档。分母二全部对象的二元说出率含代码写错；五档分布不含代码写错、其他或不可评估。')
    rr=load('disclosure.csv');variants={'all_1':'主口径：全部主因/并列项均第1档','any_1':'敏感性：任一主因/并列项第1档','all_12':'敏感性：全部主因/并列项第1或2档','any_12':'交叉敏感性：任一主因/并列项第1或2档'}
    for b in ['DAComp','KramaBench']:
        idx={(r['scope'],r['variant'],r['metric']):r for r in rr if r['benchmark']==b}
        for scope in ['分母二全部对象','五机制及多因并列']:
            add('**'+b+'／'+scope+'**\n\n'+table(['口径','说出来','没有说出来'],[[variants[k],fmt(idx[(scope,k,'说出来')]),fmt(idx[(scope,k,'没有说出来')])] for k in variants]))
    add('仅五机制单一主因的补充口径见[disclosure.csv](../records/044_stats/disclosure.csv)。')
    add('### “意识到了却没交代”及探索阶段的五档\n\n以下只按单一主因类别分组，含“已说出”的基础类别合并。表中1～5依次为针对本处说明、通用说明、意识到未交代、见过相关信息但无意识迹象、没有迹象。合并Choice+Downgrade的第3档才是本任务的目标数字；Data与Intent不混入。')
    for b in ['DAComp','KramaBench']:
        rr=[r for r in aware if r['benchmark']==b]
        add('**'+b+'**\n\n'+table(['主因组','第1档','第2档','第3档','第4档','第5档'],[[c]+[fmt(next(r for r in rr if r['main_category']==c and r['grade']==str(g))) for g in range(1,6)] for c in ['Unstated Choice','Quiet Downgrade','Unstated Choice + Quiet Downgrade','Data Misconception','Intent Misreading']]))
    add('### 探索阶段：证据在场与曾经理解对过\n\n先按合格探索点核对“是”，再以对象取any；不同探索类别可共享对象，合计去重。')
    rr=load('exploration.csv')
    add(table(['benchmark','探索类别','指标','结果'],[[r['benchmark'],r['category'],r['metric'],fmt(r)] for r in rr]))
    ever=js('ever_correct_objects.json')
    add('曾经理解对过的对象清单（点名、类别、角色及CSV行号另见[ever_correct_objects.json](../records/044_stats/ever_correct_objects.json)）：\n\n'+table(['benchmark','对象'],[[r['benchmark'],r['object_id']] for r in ever]))
    add('DAComp这12张全部来自impl-030；不能把12张当作12次独立纠错/遗忘行为。invoice的“曾经理解对过”更正使该计数从11变12。组合项invoice_payment没有单独计入探索参与率。')
    add('### 按根源决定计的对照\n\n只按已有记录找共同具体规则。先确定对象全部主因点被同一规则覆盖，才整对象折叠；只涉及参与因素或部分并列项的对象保守保留。先按各分母排除对象，再在各自范围折叠，因此组合修复不会使同根源的可分析对象被一起排除。不同对象的主因类别不一致时保留“混合主因集合”行，不给根源重新判类。此保守实现是对照，不是完整因果去重或新的主结果。')
    add(table(['根源','事件','折叠前对象数','涉及对象'],[[g['root_id'],','.join(str(c['event']) for d in root['decisions'] if d['id']==g['root_id'] for c in d['citations'] if c.get('event') is not None),len(g['objects']),'；'.join(g['objects'])] for g in root['merged_object_groups']]))
    add('指定核查均已记录event、原句和对象：impl-006 event27 fallback；impl-001 events21/37与impl-002 events23/41/43占位；impl-007 event23字段映射（另查Apple event39）；impl-018 event19外键映射及event57修复遗漏；impl-030 event45 pk_alias（含036的invoice，并明确039为校准）。001/002的SQL逐表独立编写，未找到足以证明同一具体决定的规则，不因共用文件而并。030的invoice虽属于共同外键规则，但还有独立类型并列项，故进入根源目录、未整对象折叠。全部未并入理由与原句见[shared_root_catalog.json](../records/044_stats/shared_root_catalog.json)。')
    rr=load('root_comparison.csv')
    for b in ['DAComp','KramaBench']:
        cats=list(dict.fromkeys(r['metric'] for r in rr if r['benchmark']==b));idx={(r['metric'],r['denominator_scope']):r for r in rr if r['benchmark']==b}
        add('**'+b+'根源单位**\n\n'+table(['主要原因/原主因集合','根源分母一','根源分母二'],[[c,fmt(idx[(c,'分母一')]) if (c,'分母一') in idx else '—',fmt(idx[(c,'分母二')]) if (c,'分母二') in idx else '—'] for c in cats]))
    add('KramaBench没有已核实的跨题共同决定，因此仍一题一个单位。DAComp根源分母一309、分母二168；混合集合保留了同一外键规则在Data/Choice/多因并列之间的异质性，不应把Data单独行的下降全部解读为机制消失。')
    add('### DAComp“悄悄出错”及158张历史参照\n\n同时满足：原主要原因不属于其他/不可评估/无法判定、题宣称完成、全部主因/并列项并非都第1档。按任务明确条件，agent自己的组合修复仍可计入悄悄出错；这与分母二排除组合修复是两个不同筛选。')
    add(table(['完成/标签口径','指标','分母','结果'],[[r['completion_rule'],r['metric'],r['denominator_scope'],fmt(r)] for r in silent]))
    add('已逐题核实29个finish事件：impl-007无finish、无留存报告，写报告失败；impl-011有finish报告。新口径排007纳011；旧口径反之。其余28题都有finish。来源与事件路径见[completion_claims.json](../records/044_stats/completion_claims.json)；043来源实际名称为formal_delivery_sources.json。')
    add('历史158已通过只读重放026存档脚本核实，并恢复逐表成员；历史行的95%范围是044用同一20261103/10000规则新算，未冒充2026-10-30原有区间。精确算术：**158 + 7 − 5 = 160；160 − 7（impl-007）+ 9（impl-011）= 162**。agent自己错的旧完成分母仍183，但移出candidate_quality_insights、加入invoice_payment；换新完成后183−7+11=187。')
    add(table(['对象','历史→现标签旧完成：悄悄出错','旧主因/档位','现主因/档位'],[[r['object_id'],str(r['old_silent'])+'→'+str(r['new_labels_old_completion_silent']),str(r['old_items']),r['new_statistical_main']+' / '+str(r['new_primary_grades'])] for r in bridge['changes']]))
    add('变化不只是“只认交付物”：也包括并列项集合改变、已有交付物与本处的对应重新核定、主要原因转其他，以及本任务的组合修复纳入条件。新增7中6张是从旧“全部具体说明”变成至少一项未具体说明，另1张是组合修复invoice_payment；移出5中4张现在主因有具体披露，另1张主要原因改为其他。不对缺少独立控制的变化硬拆因果贡献；逐对象原值见[historical_bridge.json](../records/044_stats/historical_bridge.json)。')
    add('### 按点附表\n\n统计主结论均以对象为单位。点数受拆点粒度影响（含038同类缺口组），不用于两个benchmark之间的机制频率比较。完整按角色/类别比例见[points_appendix.csv](../records/044_stats/points_appendix.csv)，按点五档见[points_disclosure_appendix.csv](../records/044_stats/points_disclosure_appendix.csv)，均带分子、分母与按题bootstrap范围。逐点权威来源及13条内存更正见[point_audit.json](../records/044_stats/point_audit.json)。')
    add('## 人工复核清单上的对象\n\n以下均是条件影响分析，不改现有标签。以用户本会话给出的v3六对象为准；后面只补036～043仍明确保留的对象边界，未把026已经解决的旧建议再次应用。每个情景单独作用于本次基线，不应把相互重叠的情景增量直接相加。没有给出新的档位、证据字段或角色排序时不补造；只有数量增量，不把条件情景当作新的估计结果。分母不变的单对象主因迁移，在DAComp分母一/二分别对应1/336、1/191；KramaBench分别1/42、1/19；涉及分母变化的已逐条注明。层内主因按同一增量迁移，使用该层分母。')
    for group in list(dict.fromkeys(r['group'] for r in reviews)):
        add('### '+group)
        add(table(['对象（当前主因）','若采用另一读法','受影响的数字','依据'],[[r['object_id']+'（'+r['current_main']+'）',r['conditional_alternative'],r['conditional_impact'],r['source']] for r in reviews if r['group']==group]))
    add('对报告里只讨论“补充拆点、重新排序、联合修复或数据来源未知”，但没有给出另一种对象判定的项目，不造出数字：038的8张fallback与country_mapping、039的4张Google Play fallback、037负贡献点、042 Workday raw email动作未找到等，若只改点切分/说明而保留主要原因与角色，所有对象统计增量为0；若实际改变排序，须先有新的复核记录，才能量化。这些限制保留在相应源报告；本次未执行任何新查询。')
    add('## 证据来源与复算\n\n- 权威输入：records/036_objects.csv、036_points.csv；037、038、039、040、042、043各自的objects/points.csv及scope.json；records/013_statuses.csv。\n- 规则：docs/标注手册_v3.2.md；13条更正、v3六对象复核清单、同类并列的统计归并及最弱档口径来自用户本会话。\n- 根源：records/043_checks/shared_root_decisions.json、036～043逐表/批次说明、026检查台账及留存event文字；具体引句和路径写入shared_root_catalog.json。\n- 交付：036～042的delivery_sources.json和043的formal_delivery_sources.json；对036覆盖的全部30题逐个打开finish事件核实action=finish。\n- 历史：scripts/compute_dacomp_preliminary_results.py、018～024的summary.csv，仅用于恢复158成员和差异说明，不作为新标签来源。\n- [input_hashes.json](../records/044_stats/input_hashes.json)列出所有脚本读入材料的SHA-256；[validation.json](../records/044_stats/validation.json)保存范围、更正、逐比例复算与历史保护检查。')
    add('从仓库根目录重算全部044输出及本报告（需Python≥3.10与NumPy；此次使用Python '+v['python']+' / NumPy '+v['numpy']+'）：\n\n```bash\nPYTHONDONTWRITEBYTECODE=1 /home/katherine/dac/.venv/bin/python -B records/044_stats/run.py\nPYTHONDONTWRITEBYTECODE=1 /home/katherine/dac/.venv/bin/python -B records/044_stats/verify_reproducibility.py\ngit diff --check\n```\n\nrun.py只写records/044_stats/和本044报告；prepare.py只读既有材料、核对范围/更正/目录；stats.py生成CSV、成员与bootstrap验证；historical.py只读重放026统计；review.py和report.py生成条件影响与报告，validate.py独立从源CSV逐字段核对类别/角色、更正、归并与披露。verify_reproducibility.py连续运行完整入口两次并比较全部输出字节，结果见reproducibility.json。没有下载数据或建立数据库连接。')
    add('来源中的source_row表示含表头的CSV记录序号（不是含多行字段时的物理文本行号）。每个CSV结果行都有metric_id，映射到[metric_membership.json](../records/044_stats/metric_membership.json)的分子/分母成员；[entity_index.json](../records/044_stats/entity_index.json)给出题群。DAComp始终从全部30题抽30群，KramaBench从42题抽42群，群内保留对象；分层、根源和按点表仍按原题群抽样。分母二已排除类别的CSV零分子行只是对齐审计占位，报告写“排除”，不能当作该类发生率为0。')
    zero=[r for f in OUT.glob('*.csv') for r in load(f.name) if 'bootstrap_zero_denominator' in r and int(r['bootstrap_zero_denominator'])>0 and int(r['denominator'])>0]
    add('## 不确定或没查到的／局限\n\n1. **Codex初标、Claude抽查、尚未人工复核**。标签争议见上节；区间只反映题群抽样波动，不包含标注错误和概念定义的不确定性。\n2. 各题是留存失败对象集合，两个分母都不是所有任务的失败概率；“全部确认做错”沿用任务名称，包括Other/不可评估/未交卷等预先指定成员。Unstated Choice不自动等于能唯一判定agent错。\n3. 同类候选/缺口组的点切分不统一，点级结果仅附表；非原因点不当作可独立修复原因。\n4. 30题bootstrap会反映impl-030聚集，但根源目录仅核查指定组及043已列规则，不是完整的因果独立单位证明；部分并列对象保守未合并。\n5. 小样本子组有抽样分母为0的轮次，比例取有定义轮次的2.5%/97.5%分位数，未填0，也未额外重抽至10000个有效值；各行注明有效次数。KramaBench Downgrade仅1题，五档比例有效6359轮，100%～100%的区间只是经验分布退化，不意味着总体确定。其他0%/100%退化区间同理。\n6. 13条更正全部原值吻合，没有跳过项；档位变化不替代类别复核。041未读取、未修改。')
    add('## 建议的下一步\n\n由用户与Claude按v3六对象及仍保留的边界进行人工复核；确认后另开更正任务，再用本脚本重算。研究设定与标签不在044内调整。主结果使用对象口径，按根源结果只作对照。')
    path=P.ROOT/'notes/044_2026-11-03_重标总统计.md';path.write_text('\n\n'.join(report)+'\n')
    P.dump('manual_review_sources.json',{'primary_list_source':'用户在044会话于2026-11-03补充；以v3六对象为准；无需查找知识库原文','primary_objects':[r['object_id'] for r in reviews if r['group']=='v3人工复核清单'],'supplemental_rule':'仅036～043仍保留的对象边界，不将已解决的026建议再应用','scenario_rule':'只描述条件增量；不改变object_audit或原CSV标签'})
    print('报告：',path,'；复核条目',len(reviews))
if __name__=='__main__':main()
