"""Finalize 30 v2 annotations from immutable prior evidence and explicit reclassification."""
from pathlib import Path
from collections import Counter
import csv,hashlib,json,re
from uncertainty_dacomp_batch018 import GRADES,previous,trace_path

ROOT=Path(__file__).resolve().parents[1];REC=ROOT/'records'
MULTI={
2:{'key_formula':'A','url_rule':'C'},
6:{'spend':'I','video_views':'D','video_view_rate':'A','upvotes':'D','downvotes':'D','comments':'D',**{k:'A' for k in ['shares','saves','post_visits','profile_visits','community_joins','conversions','conversion_value','cost_per_video_view','cost_per_conversion','total_engagements','engagement_rate','click_through_rate','cost_per_click','cost_per_thousand_impressions']}},
12:{'first_name_trim_policy':'O','last_name_trim_policy':'O'},
16:{'annual_zero':'C','management_zero':'C','maturity_labels':'O','size_labels':'O'},
18:{'opportunity_source':'I','product_source':'I'},
23:{'url_route':'A','followers_representation':'O'},
30:{'account_source':'U','adjustment_amount_representation':'O','credit_balance_adjustment_amount_representation':'O','credit_memo_amount_representation':'O','exchange_rate_representation':'O'},
}
NEW_RULE={
2:'v2第4节已明确U参与因素只需前三项及正改善，latitude不再依赖对v1的例外解释。C/A并列项仍分别记录；URL通用置空说明不代表落实了可执行正则。',
3:'契约明确允许priority并列，按v2归O；固定残余完整元组配对仍是未由手册指定的计数约定，不声称全局最小格子。最终报告的未指定tie-breaker说明属通用层。',
4:'旧history_key_frozen与activity_rule_gold_day均使用2025-10-24同一日期；基线本身不引用运行时间。018仅复用这两个固定条件单项，实时history_key/activity_rule仅保留旧诊断，不参与主因选择。固定key原时刻是匹配gold未规定身份约定的诊断，不构造U。',
6:'20个单项仍分别归I/D/A，不按同一种NULL外观合并；D候选列与需业务定义的A派生字段边界保持中把握。v2要求共同时间，本轮固定加载时间后全部比较数值不变。缺列填NULL的通用披露只覆盖17个占位项，不延伸为CTR/CPC/eCPM直接字段与重算公式的说明。',
7:'最终报告写入命令中有订阅字段语义不完全一致的一般警示，但未点名subscriber_id；按通用策略记档。写文件失败不消除轨迹中已经写出的文字，但不宣称用户收到最终报告。字段选择缺契约定义，描述为A差异，不说agent做错。',
9:'v2第4节明文放宽U参与因素；lookup仍为U，独立改善2400行。主因country编码A不因此改为U。组合去翻译对照不代替两个独立干预。',
10:'v2已将不可评估区分写入第3节。没有正常归因主项时，四档仍针对输入差异/源选择填写，不把不可评估当成第五档。',
12:'v2第5节规定所有并列项同类直接记该类，因此表级由多因并列（O）变O；first/last两项仍各列O及独立四档。报告提到必需属性过滤，但没有说明本处原字符串空白与trim处理，保守记看到了但没提。',
16:'v2保留两个C与两个O并列；不把有关另一张organization_performance空表的说明升级为本表比率/枚举说明。gold=初始≠agent照常标注；raw邮箱缩减步骤仍未找到，CS节点归因不补猜。',
18:'两个外键原因均I，按v2表级直接I。event57代码注释能支持第3节正确意图，但第6节明确要求思考或最终报告；本次不把代码注释自动转成该字段的口头披露，因此两个外键均记看到了但没提。这是跨字段证据用途区别，不更改I门槛。',
19:'报告提到聚合NULL语义及输出补零，没有说明连接中NULL键是否彼此匹配；不以无关NULL文字提升四档。NULL等值仍是契约未定选择A；同一固定配对口径不变。',
21:'按v2，重复保留计数的一般声明归只有通用策略说明；仍未指出本表date spine扩行。主要U及忽略证据标记不变。计数的两种替换是同一错误的替代修法，不当作两个并列原因。',
23:'URL的A与followers类型的O仍各138格并列，沿用L0贡献比较并公开L1–L3。报告的字段转换功能清单或LinkedIn示例不算本表这两个选择的说明。',
24:'v2新增通用策略档后，邮箱等可选字段验证失败置NULL的声明记此档；并未说明双点域名正则边界，故不记具体说明。原因仍A：契约无可执行完整正则；不自行引入外部邮件规范改定O。',
25:'v2新增通用策略档，最终报告一般电话处理声明可放此档，尽管未解释本表预修复且声明不能证明代码遵约。主因C按行数选contact，user为C参与因素；不换格子来达到半数门槛。',
26:'已知L3整表匹配以及留存gold DATE与当前gold SQL TIMESTAMP不一致，仍按用户指定对象完成O；不改013状态，不推测历史成因。时间解析功能概述不等于说明本表DATE/TIMESTAMP取舍。',
28:'按v2第3节，agent=初始而gold输入不同，诊断后不可评估。四档针对源输入选择；报告对channel_basic/video另表的缺列说明不能迁移到demographics。',
29:'v2明确将“转换失败成为NULL”这种跨表说明归通用策略，原三档已提到据此细分。解析/截前缀仍缺约定，A不变；不能把TRY_CAST主动允许失败说成假设每行可解析。',
30:'v2第5节明确并列U不要求减半，account_source满足U前三项且与四个O各减少1040格，改为U/O并列，X撤下。表级四档不能照搬017的单一已提到：映射示例未点明invoice外键，类型示例是invoice-item；五项均只有通用策略说明。',
}

def section(text,num):
    start=text.index(f'## {num}. ');m=re.search(r'^## ',text[start+4:],re.M)
    return text[start:start+4+m.start()] if m else text[start:]
def comparison(c):
    lines=['|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|不同配对行|行规模|格子规模|整表匹配|','|---|---:|---:|---:|---:|---|---:|---:|---:|---|']
    for x in c['levels']:
        lines.append('|'+ '|'.join(str(x.get(k,0)) for k in ['level','agent_rows','gold_rows','agent_only_key_rows','gold_only_key_rows'])+f'|{x.get("common_key_agent_excess_rows",0)}/{x.get("common_key_gold_excess_rows",0)}|'+ '|'.join(str(x[k]) for k in ['common_key_different_rows_or_min_pairs','row_scale','cell_scale','whole_match'])+'|')
    lines+=['',f'整表首次匹配：{c.get("first_match") or "L0–L3均不匹配"}。','','|比较列|L0|L1|L2|L3|','|---|---:|---:|---:|---:|']
    for col in c['levels'][0]['column_mismatches']:lines.append('|'+col+'|'+'|'.join(str(x['column_mismatches'][col]) for x in c['levels'])+'|')
    return '\n'.join(lines)
def main():
    dest=REC/'018_annotations';dest.mkdir(exist_ok=True)
    unc=json.loads((REC/'018_uncertainty_audit.json').read_text());rows=[];decisions={};manifest=[]
    oldrows={}
    for pre in [16,17]:
        for row in csv.DictReader((REC/f'{pre:03}_annotations/{pre:03}_summary.csv').open()):oldrows[row['题目']]=row
    for n in range(1,31):
        task=f'impl-{n:03}';pre=16 if n<=20 else 17;old=previous(n);a=dict(old);row=dict(oldrows[task]);u=unc[task]
        oldmd=next((REC/f'{pre:03}_annotations').glob(f'{pre:03}_{task}_*.md'));body=oldmd.read_text()
        rp=REC/f'{18 if n==6 else pre:03}_reruns_{task}.json';r=json.loads(rp.read_text());base=r['runs'][0]['comparison']['levels'][0];bylabel={t['label']:t for t in r['runs']}
        itemcats=MULTI.get(n,{i['item']:a['cat'] for i in u['items']})
        assert list(itemcats)==[i['item'] for i in u['items']],n
        if n==12:a['cat']='O'
        if n==18:a['cat']='I'
        if n==30:
            a['cat']='多因并列（U、O）'
            a['reason']='已核实：共同时间基线为1045行/9565格差异。account_source与四项数值表示单改各减少1040格、行规模均不降，按v2第5节并列。raw.account_id关联账户1999行，而invoice的raw.id关联0行；轨迹未做对应核实。故P“invoice.id可充当account_id”被agent可见数据反证，满足U前三项；并列项无需减半，account_source归U。其余四项agent遵守DOUBLE、gold保留VARCHAR，归O。created_date漏写契约OR NULL分支单改减少175格，为C参与因素；其他数值/日期类型干预各减少1035或5格，为O参与因素。'
            a['p']='P：invoice记录的raw.id可作为account_id并关联账户主键。017-V1以agent可见数据反证，event39→40只显示列存在，不是关联核实；未找到该核实。单改减少1040格，与其他最大项相同，满足v2第5节对U并列项的要求。原严格减半/L2整表条件仍未满足，两种门槛不混称。'
            a['u4']='是（v2并列项放宽）：account_source满足U前三项且与其他主项各减1040格；原严格半数/L0–L2整表条件仍为否'
        if n==2:a['u4']='主因C/A的严格数值条件否；latitude满足v2第4节U参与因素条件（前三项及减少13655格），不要求一半'
        if n==9:a['u4']='A主因单改15200→2400行；U参与因素lookup单改15200→12800行，满足v2第4节放宽，严格减半条件否'
        if n in [10,28]:a['u4']='不适用：不可评估，旧单改仅作输入差异诊断'
        if n==6:a['reason']=a['reason'].replace('20处并列','20处按v2分别归类后并列')+' 018统一固定加载时间补跑，L0–L3行/格子数和各列差异均与旧结果一致。'
        a['reason']=a['reason'].replace('按v1','按v2')
        if 'A' in itemcats.values():a['reason']+=' A项仅表示差异取决于契约未定的选择，不据gold实现认定agent做错。'
        a['rules']=NEW_RULE.get(n,a['rules'].replace('v1','v2'))
        if n==6:a['p']=a['p'].replace('20个不同错误','20个不同差异点')
        if n==11:a['rules']=a['rules'].replace('同类别的三个错误','同类别的三个差异点')
        cat_change=a['cat']!=old['cat']
        cause_change=f'原因类别：{old["cat"]}→{a["cat"]}。' if cat_change else '原因类别及参与因素不变。'
        if n in [12,18]:cause_change+='v2第5节要求同类并列直接记该类，独立项及数值均保留。'
        if n==30:cause_change+='v2第5节放宽并列U门槛、第3节禁止用X表示门槛未满足。'
        grades='；'.join(i['item']+'='+i['grade'] for i in u['items'])
        if n<=20:uncchange='上一版未设不确定性字段，本次按v2第6节逐项新增。'
        else:
            oldstatus=oldrows[task]['agent 是否意识到或提到了与本表差异相关的不确定性'].split('；')[0]
            uncchange=f'不确定性由017的“{oldstatus}”改按四档逐项记录：'+grades+'。'
        change=cause_change+uncchange+('按v2第7节补做共同固定时间，比较数值不变。' if n==6 else '')
        a.update(item_categories=itemcats,uncertainty_items=u['items'],previous_annotation=str(oldmd.relative_to(ROOT)),change_from_previous=change,reused_rerun_file=str(rp.relative_to(ROOT)),new_verification_queries=0)
        decisions[str(n)]=a
        src2=section(body,2);src4=section(body,4)
        lines=[f'# {task} / {row["表"]}（v2定稿）','','## 1. 差异描述与判定','',a['desc'],'',a['reason'],'',f'主要原因：**{a["cat"]}**；把握：**{a["confidence"]}**。',f'参与因素：{a["factors"]}。标记：{a["flags"]}。','',f'与上一版（{pre:03}）相比：{change}','','## 2. 依据与复用范围','',f'- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../{pre:03}_annotations/{oldmd.name})。',f'- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。',f'- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。','',f'以下契约、SQL及raw审计摘自{pre:03}，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。','',src2.split('\n',1)[1].strip(),'','## 3. agent实际看到的信息与不确定性四档','',a['seen'],'','四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。','','|主项/输入差异|类别|不确定性四档|事件|','|---|---|---|---|']
        for i in u['items']:lines.append('|'+i['item']+'|'+itemcats[i['item']]+'|'+i['grade']+'|'+','.join(str(e['event']) for e in i['evidence'])+'|')
        for i in u['items']:
            lines+=['',f'### {i["item"]}：{i["grade"]}','',i['scope_limit']]
            for e in i['evidence']:lines += ['',f'事件 **{e["event"]}**，字段`{e["field"]}`；[轨迹原文](../{Path(u["trace_file"]).name})；原文件`{e["original_path"]}`。','```text',e['quote'],'```']
        lines+=['',f'已检视{len(u["all_event_ids"])}个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。','', '## 4. 查询、重跑与规模','',f'复用核实查询 **{row["核实查询条数"]}条**；018新增核实查询 **0条**。核实代价：{a["cost"]}。每表累计仍≤5，失败尝试按旧记录计数。',f'[采用的重跑JSON](../{rp.name})保存SQL单处替换、基线/干预及L0–L3每列计数。','']
        if n!=6:
            lines += [f'下面完整复用{pre:03}的查询与重跑证据；其中“新增/本次”的执行归属仍为{pre:03}，018没有重复执行。',src4.split('\n',1)[1].strip()]
        else:
            query=src4.split('### 比较口径')[0].split('\n',1)[1]
            lines += [query,'### v2共同时间补跑','',"原始CURRENT_TIMESTAMP仅用于未评分的_dbt_loaded_at。按v2仍固定所有21次执行为2025-10-25 12:00:00+08；这是任意共同控制，不推断原执行日期。其余单项补丁直接复用014/016，不增加数据核实查询。",'','原件以READ_ONLY附加，复制raw到data/018_work后执行。比较器沿用016/017；键固定L0并纳入比较列，独有行计格子时包含键。']
            for t in r['runs']:
                lines += ['',f'### 重跑 {t["label"]}','',f'SQL：`{t["sql_path"]}`；SHA-256：`{t["sql_sha256"]}`。']
                for edit in t['edits']:lines += ['',f'单处替换offset={edit["offset"]}；原文：','```sql',edit['old'],'```','新文：','```sql',edit['new'],'```']
                lines+=['',comparison(t['comparison'])]
        lines+=['','## 5. 逐项类别及U门槛','',f'表级主要原因：**{a["cat"]}**。','', '|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|','|---|---|---|---|---|']
        for label,cat in itemcats.items():
            t=bylabel.get(label)
            if t:
                c=t['comparison'];x=c['levels'][0];lines.append(f'|{label}|{cat}|{base["row_scale"]}→{x["row_scale"]}|{base["cell_scale"]}→{x["cell_scale"]}|{c.get("first_match") or "无"}|')
            else:lines.append(f'|{label}|{cat}|不适用：见诊断|不适用：见诊断|不作为单侧U修复|')
        lines+=['',f'重跑是否满足U第4条件：**{a["u4"]}**。','',a['p'],'','主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。','','## 6. 版本对比','',change,'',f'与014相比的历史对比沿用原字段：{row["与 014 相比是否变化"]}。此字段不代替本次与016/017的对比。','','## 规则问题','',a['rules'],'','v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。','']
        (dest/f'018_{task}_{row["表"]}.md').write_text('\n'.join(lines))
        row.update({'一句话描述':a['desc'],'主要原因类别':a['cat'],'参与因素':a['factors'],'标记':a['flags'],'把握':a['confidence'],'重跑是否满足 U 的第 4 个条件':a['u4'],'并列项类别':('；'.join(k+'='+v for k,v in itemcats.items()) if len(itemcats)>1 else '不适用：单一主因或不可评估'),'不确定性四档':grades,'与上一版相比是否变化及原因':change})
        row['agent 是否意识到或提到了与本表差异相关的不确定性']=('017旧三档，仅回溯：'+row['agent 是否意识到或提到了与本表差异相关的不确定性']) if n>20 else '上一版未设置；018判断见“不确定性四档”列'
        rows.append(row)
        sources={oldmd,rp,trace_path(n),REC/f'{pre:03}_decisions.json',REC/f'015_raw_{task}.json'}
        for match in re.findall(r'\]\(([^)]+)\)',body):
            p=(oldmd.parent/match).resolve()
            if p.is_file():sources.add(p)
        qs=[REC/f'{p:03}_queries_{task}.json' for p in ([14,16] if n<=10 else [pre])]
        sources.update(p for p in qs if p.exists())
        manifest.append({'task':task,'previous_annotation':str(oldmd.relative_to(ROOT)),'rerun_file':str(rp.relative_to(ROOT)),'new_sql_trials':21 if n==6 else 0,'new_verification_queries':0,'files':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(sources)]})
    keys=list(rows[-1]);keys=[k for k in keys if k not in ['并列项类别','不确定性四档','与上一版相比是否变化及原因']]+['并列项类别','不确定性四档','与上一版相比是否变化及原因']
    with (dest/'018_summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');w.writeheader();w.writerows(rows)
    cats=Counter(a['cat'] if not a['cat'].startswith('多因并列') else '多因并列' for a in decisions.values())
    per_item=Counter(i['grade'] for u in unc.values() for i in u['items']);sets=Counter(' / '.join(g for g in GRADES if g in {i['grade'] for i in u['items']}) for u in unc.values());table_presence={g:sum(any(i['grade']==g for i in u['items']) for u in unc.values()) for g in GRADES}
    stats={'tables':30,'category_counts':dict(cats),'item_count':sum(per_item.values()),'uncertainty_per_item':{g:per_item[g] for g in GRADES},'uncertainty_table_grade_sets':dict(sets),'uncertainty_table_presence_nonexclusive':table_presence,'changed_category_tasks':[f'impl-{n:03}' for n in range(1,31) if decisions[str(n)]['cat']!=previous(n)['cat']]}
    for file,obj in [('018_decisions.json',decisions),('018_reuse_manifest.json',manifest),('018_statistics.json',stats)]: (REC/file).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(stats,ensure_ascii=False))
if __name__=='__main__':main()
