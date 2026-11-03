#!/usr/bin/env python3
"""044完整重算入口。Python >=3.10 + NumPy；只读原输入，写044目录及044报告。"""
import csv,json,hashlib,sys,platform
from collections import defaultdict, Counter
import numpy as np
import prepare as P
OUT=P.OUT
SEED=20261103; REPS=10000
CATS=['Data Misconception','Intent Misreading','Unstated Choice','Quiet Downgrade','Form Mismatch','代码写错','多因并列','只能组合修复','其他','不可评估','无法判定','未交卷']
EXCLUDED={'其他','不可评估','无法判定','未交卷','只能组合修复'}
EXP={'Data Misconception','Intent Misreading'}; CON={'Unstated Choice','Quiet Downgrade','Form Mismatch'}
PRIMARY={'主要','并列','同类候选'}
ACTIVE=PRIMARY|{'参与'}
TABLES=defaultdict(list); MEMBERS={}; ENTITIES={}; WEIGHTS={}; GROUPS={}
def writecsv(name, rows):
    if not rows:return
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys,lineterminator="\n");w.writeheader();w.writerows(rows)
def entity(id, benchmark, task, **kw):
    assert id not in ENTITIES
    ENTITIES[id]=dict(benchmark=benchmark,task=task,**kw);return id

def measure(file,benchmark,metric,num,den,**meta):
    num=sorted(set(num));den=sorted(set(den));assert set(num)<=set(den),(file,metric)
    groups=GROUPS[benchmark]; gi={g:i for i,g in enumerate(groups)}
    n=np.zeros(len(groups),dtype=np.int64);d=n.copy()
    for ids,vec in [(num,n),(den,d)]:
        for id in ids:
            e=ENTITIES[id];assert e['benchmark']==benchmark
            vec[gi[e['task']]]+=1
    bn=WEIGHTS[benchmark]@n;bd=WEIGHTS[benchmark]@d;valid=bd>0
    lo,hi=np.quantile(bn[valid]/bd[valid],[.025,.975],method='linear') if valid.any() else (None,None)
    key=f'{file}:{len(TABLES[file])+1:04}'
    row=dict(metric_id=key,benchmark=benchmark,metric=metric,**meta,numerator=len(num),denominator=len(den),proportion=len(num)/len(den) if den else None,ci95_low=lo,ci95_high=hi,numerator_ci95_low=float(np.quantile(bn,.025)),numerator_ci95_high=float(np.quantile(bn,.975)),bootstrap_valid=int(valid.sum()),bootstrap_zero_denominator=int((~valid).sum()))
    TABLES[file].append(row);MEMBERS[key]={'numerator_ids':num,'denominator_ids':den}
    return row

def main():
    objects,points,status,scope=P.load(); catalog=P.roots(objects,points);P.delivery()
    pidx=defaultdict(list)
    for i,p in enumerate(points):
        p['point_id']=f"{p['source']}:{p['source_row']}";p['normalized_category']=P.cat(p['类别']);p['grade']=P.GRADES.index(p['是否说出（五档）'])+1
        pidx[p['对象编号']].append(p)
    audit=[]
    for r in objects:
        o=r['对象编号'];b=r['benchmark'];ps=pidx[o];mainpoints=[p for p in ps if p['角色'] in PRIMARY or (r['是否只能组合修复']=='是' and p['角色']=='组合项')]
        base=P.cat(r['主要原因']);combo=r['是否只能组合修复']=='是';c='只能组合修复' if combo else base
        active=[p for p in ps if p['角色'] in ACTIVE]
        primary_cats={p['normalized_category'] for p in mainpoints}
        if not combo and base=='多因并列' and len(primary_cats)==1:
            c=next(iter(primary_cats))
        inc={p['normalized_category'] for p in active}
        # 对象列自身及并列项（包括组合项）也是“参与其中”的依据。
        if base not in ['多因并列','只能组合修复','未交卷']:inc.add(base)
        inc.update(primary_cats)
        gs=[p['grade'] for p in mainpoints]
        assert gs or c in EXCLUDED,(o,c)
        # 用户044会话确认：归并后同类别的主因点按最弱档，any敏感性保留每个点。
        exppts=[p for p in active if p['normalized_category'] in EXP]
        row=dict(object_id=o,benchmark=b,task=o[:8] if b=='DAComp' else o,source=r['source'],source_row=r['source_row'],layer='marts' if r['层'] in ['sales','utils'] else r['层'],original_layer=r['层'],original_main=r['主要原因'],main_category=c,base_category=base,combination_only=combo,denominator2=c not in EXCLUDED,primary_point_ids=[p['point_id'] for p in mainpoints],primary_categories=sorted(primary_cats),incidence_categories=sorted(inc),primary_grades=gs,grade=max(gs) if gs else None,disclosed_all_1=bool(gs) and all(g==1 for g in gs),disclosed_any_1=bool(gs) and any(g==1 for g in gs),disclosed_all_12=bool(gs) and all(g<=2 for g in gs),disclosed_any_12=bool(gs) and any(g<=2 for g in gs),cross_stage_tie=c=='多因并列' and bool(primary_cats&EXP) and bool(primary_cats&CON),exploration_point_ids=[p['point_id'] for p in exppts],evidence_present=any(p['证据在场']=='是' for p in exppts),ever_correct=any(p['曾经理解对过']=='是' for p in exppts),agent_own_error=base not in ['其他','不可评估','无法判定','未交卷'])
        audit.append(row);entity(o,b,row['task'],kind='object')
    merges=[]
    for r in audit:
        if r['original_main']!=r['main_category']:
            reason='只能组合修复优先单列' if r['combination_only'] else ('并列项归并后只有同一类别；用户044会话确认' if r['original_main']=='多因并列' else '已说出的选择/降级归入基础类别')
            merges.append({'benchmark':r['benchmark'],'object_id':r['object_id'],'source':r['source'],'source_row':r['source_row'],'original_main':r['original_main'],'statistical_main':r['main_category'],'reason':reason,'normalized_primary_categories':r['primary_categories'],'primary_grades':r['primary_grades'],'object_grade':r['grade'],'disclosed_all_1':r['disclosed_all_1'],'disclosed_any_1':r['disclosed_any_1']})
    P.dump('statistical_merges.json',{'authorization':'用户044会话确认：并列项归并后只有同一类别时统计归入该类别；主口径取最弱档，敏感性保留任一点1档。原CSV不改，独立于13条更正。','objects':merges})
    byid={r['object_id']:r for r in audit}
    GROUPS.update(DAComp=[f'impl-{i:03}' for i in range(1,31)],KramaBench=sorted(r['object_id'] for r in audit if r['benchmark']=='KramaBench'))
    for b,gs in GROUPS.items():
        # 每个benchmark独立初始化同一个种子；每次抽取全部题群，保留零贡献群。
        rng=np.random.Generator(np.random.PCG64(SEED));draws=rng.integers(0,len(gs),size=(REPS,len(gs)))
        WEIGHTS[b]=np.array([np.bincount(row,minlength=len(gs)) for row in draws],dtype=np.int64)
    for b in GROUPS:
        aa=[r for r in audit if r['benchmark']==b];allids={r['object_id'] for r in aa};eligible={r['object_id'] for r in aa if r['denominator2']}
        for c in CATS:
            for label,den in [('分母一',allids),('分母二',eligible)]:
                measure(f'main_{b}.csv',b,c,{r['object_id'] for r in aa if r['main_category']==c}&den,den,denominator_scope=label,excluded_from_denominator2=label=='分母二' and c in EXCLUDED)
        for c in CATS[:6]+['其他','不可评估','无法判定']:
            for label,den in [('分母一',allids),('分母二',eligible)]:
                measure('incidence.csv',b,c,{r['object_id'] for r in aa if c in r['incidence_categories']}&den,den,denominator_scope=label)
        for label,den in [('分母一',allids),('分母二',eligible)]:measure(f'main_{b}.csv',b,'跨阶段并列',{r['object_id'] for r in aa if r['cross_stage_tie']}&den,den,denominator_scope=label,excluded_from_denominator2=False)
        # 说出率只纳入有主因档位的五机制/多因并列；代码写错仅在悄悄出错中使用原档位。
        disclosure_set={r['object_id'] for r in aa if r['main_category'] in EXP|CON|{'多因并列'}}
        for variant in ['all_1','any_1','all_12','any_12']:
            yes={r['object_id'] for r in aa if r['disclosed_'+variant]}
            for name,sub in [('分母二全部对象',eligible),('五机制及多因并列',disclosure_set),('五机制单一主因',{r['object_id'] for r in aa if r['main_category'] in EXP|CON})]:
                measure('disclosure.csv',b,'说出来',yes&sub,sub,scope=name,variant=variant)
                measure('disclosure.csv',b,'没有说出来',sub-yes,sub,scope=name,variant=variant)
        for c in ['Unstated Choice','Quiet Downgrade','Unstated Choice + Quiet Downgrade','Data Misconception','Intent Misreading']:
            cs=set(c.split(' + '));sub={r['object_id'] for r in aa if r['main_category'] in cs}
            for g in range(1,6):measure('awareness.csv',b,P.GRADES[g-1],{r['object_id'] for r in aa if r['grade']==g}&sub,sub,main_category=c,grade=g,is_awareness_target=c in ['Unstated Choice','Quiet Downgrade','Unstated Choice + Quiet Downgrade'])
        for c in ['Data Misconception','Intent Misreading','探索阶段合计']:
            cs=EXP if c=='探索阶段合计' else {c};selected={};
            for r in aa:
                pp=[p for p in pidx[r['object_id']] if p['角色'] in ACTIVE and p['normalized_category'] in cs]
                if pp:selected[r['object_id']]=pp
            den=set(selected)
            for field,label in [('证据在场','证据在场率'),('曾经理解对过','曾经理解对过')]:
                num={o for o,pp in selected.items() if any(p[field]=='是' for p in pp)}
                measure('exploration.csv',b,label,num,den,category=c)
        # 按点附表：逐点去重，排除了校准；所有角色均保留且分开报。
        pp=[p for p in points if p['benchmark']==b]
        for p in pp:entity(p['point_id'],b,byid[p['对象编号']]['task'],kind='point',object_id=p['对象编号'])
        for role in ['全部','主要','并列','参与','非原因','组合项','同类候选']:
            sub={p['point_id'] for p in pp if role=='全部' or p['角色']==role}
            for c in sorted({p['normalized_category'] for p in pp}):measure('points_appendix.csv',b,c,{p['point_id'] for p in pp if p['normalized_category']==c}&sub,sub,role=role)
        for c in sorted({p['normalized_category'] for p in pp} & (EXP|CON)):
            den={p['point_id'] for p in pp if p['normalized_category']==c}
            for g in range(1,6):measure('points_disclosure_appendix.csv',b,P.GRADES[g-1],{p['point_id'] for p in pp if p['grade']==g}&den,den,category=c,grade=g)
    for layer in ['staging','intermediate','marts']:
        aa=[r for r in audit if r['benchmark']=='DAComp' and r['layer']==layer]
        for lab,den in [('分母一',{r['object_id'] for r in aa}),('分母二',{r['object_id'] for r in aa if r['denominator2']})]:
            for c in CATS:measure('layers.csv','DAComp',c,{r['object_id'] for r in aa if r['main_category']==c}&den,den,layer=layer,denominator_scope=lab,excluded_from_denominator2=lab=='分母二' and c in EXCLUDED)
    # 同根源多表折叠。类别不一致时保留“混合主因集合”，不给根源重新判类别。
    root_units=[]
    for b in GROUPS:
        for lab in ['分母一','分母二']:
            pool={r['object_id'] for r in audit if r['benchmark']==b and (lab=='分母一' or r['denominator2'])}
            grouped=set();units=[]
            for group in catalog['merged_object_groups'] if b=='DAComp' else []:
                ids=sorted(set(group['objects']) & pool)
                if len(ids)<2:continue
                grouped.update(ids);cats=sorted({byid[o]['main_category'] for o in ids});id='root:'+lab+':'+group['root_id']
                entity(id,b,group['task'],kind='root',objects=ids)
                units.append(dict(unit_id=id,benchmark=b,denominator_scope=lab,objects=ids,category=cats[0] if len(cats)==1 else '混合主因集合：'+' + '.join(cats)))
            for o in sorted(pool-grouped):units.append(dict(unit_id=o,benchmark=b,denominator_scope=lab,objects=[o],category=byid[o]['main_category']))
            root_units.extend(units);den={u['unit_id'] for u in units}
            for c in CATS+sorted({u['category'] for u in units}-set(CATS)):
                measure('root_comparison.csv',b,c,{u['unit_id'] for u in units if u['category']==c},den,denominator_scope=lab,excluded_from_denominator2=lab=='分母二' and c in EXCLUDED)
    delivered=set()
    for s in status:
        o=P.oid(s);delivered.add(o)
        if o not in ENTITIES:entity(o,'DAComp',s['task'],kind='delivery_table')
    assert len(delivered)==1069
    for rule,excluded_task in [('新口径','impl-007'),('旧口径','impl-011')]:
        own={r['object_id'] for r in audit if r['benchmark']=='DAComp' and r['task']!=excluded_task and r['agent_own_error']}
        silent={o for o in own if not byid[o]['disclosed_all_1']}
        measure('silent_errors.csv','DAComp','悄悄出错',silent,delivered,completion_rule=rule,denominator_scope='全部1069张交付表')
        measure('silent_errors.csv','DAComp','悄悄出错',silent,own,completion_rule=rule,denominator_scope='宣称完成题中agent自己错的表')
        measure('silent_errors.csv','DAComp','宣称完成题中agent自己错的表',own,delivered,completion_rule=rule,denominator_scope='全部1069张交付表')
    from historical import load_old
    oldown,oldsilent,oldtable=load_old()
    measure('silent_errors.csv','DAComp','历史158张参照',oldsilent,delivered,completion_rule='2026-10-30旧标签/旧完成口径',denominator_scope='全部1069张交付表')
    measure('silent_errors.csv','DAComp','历史158张参照',oldsilent,oldown,completion_rule='2026-10-30旧标签/旧完成口径',denominator_scope='宣称完成题中agent自己错的表')
    newoldown={r['object_id'] for r in audit if r['benchmark']=='DAComp' and r['task']!='impl-011' and r['agent_own_error']}
    newoldsilent={o for o in newoldown if not byid[o]['disclosed_all_1']}
    changes=[]
    for o in sorted(oldsilent^newoldsilent):
        changes.append({'object_id':o,'old_silent':o in oldsilent,'new_labels_old_completion_silent':o in newoldsilent,'old_agent_own_error_eligible':o in oldown,'new_agent_own_error_eligible':o in newoldown,'old_items':oldtable[o]['items'],'old_combination_only':oldtable[o]['combo'],'new_original_main':byid[o]['original_main'],'new_statistical_main':byid[o]['main_category'],'new_primary_grades':byid[o]['primary_grades']})
    P.dump('historical_bridge.json',{'old_158':158,'current_labels_old_completion':len(newoldsilent),'added':sorted(newoldsilent-oldsilent),'removed':sorted(oldsilent-newoldsilent),'old_own_count':len(oldown),'new_own_count':len(newoldown),'own_added':sorted(newoldown-oldown),'own_removed':sorted(oldown-newoldown),'changes':changes,'completion_switch':'当前标签旧完成160 - impl007七张 + impl011九张 = 新完成162；agent自己错分母183 - 7 + 11 = 187'})
    for f,rr in TABLES.items():writecsv(f,rr)
    P.dump('object_audit.json',audit);P.dump('point_audit.json',points);P.dump('root_units.json',root_units);P.dump('metric_membership.json',MEMBERS);P.dump('entity_index.json',ENTITIES)
    P.dump('ever_correct_objects.json',[{'benchmark':r['benchmark'],'object_id':r['object_id'],'points':[{'point':p['错误点名称'],'category':p['类别'],'role':p['角色'],'source':p['source'],'source_row':p['source_row']} for p in pidx[r['object_id']] if p['角色'] in ACTIVE and p['normalized_category'] in EXP and p['曾经理解对过']=='是']} for r in audit if r['ever_correct']])
    P.dump('input_hashes.json',P.INPUTS)
    validation={'scope':scope,'DAComp_preclassified_other':53,'DAComp_total_wrong':336,'corrections_all_applied':all(x['applied'] for x in json.loads((OUT/'corrections_applied.json').read_text())),'calibration_excluded':True,'category_role_main_unchanged':True,'seed':SEED,'replicates':REPS,'rng':'numpy.random.Generator(PCG64)','quantile':'linear','python':platform.python_version(),'numpy':np.__version__,'cluster_universe':GROUPS,'metrics':sum(map(len,TABLES.values())),'all_input_hashes_unchanged':all(hashlib.sha256((P.ROOT/p).read_bytes()).hexdigest()==h for p,h in P.INPUTS.items()),'main_totals':{b:dict(Counter(r['main_category'] for r in audit if r['benchmark']==b)) for b in GROUPS},'denominator2':{b:sum(r['denominator2'] for r in audit if r['benchmark']==b) for b in GROUPS},'known_conventions':['只能组合修复优先单列；悄悄出错仍依原主要原因判断是否agent自己的错','参与其中含对象主要原因、并列/组合项、参与因素；非原因不计','探索证据仅主要/并列/同类候选/参与点；组合项单改零改善不作为参与因素','同类别并列统计归入该类别，主档位取max；all/any保留原主点；跨类多因并列不纳入单一类别五档','分母二已排除类别的零分子行仅为审计占位，报告显示不适用','分母为0的bootstrap抽样不定义比例；记明有效次数，不补0','158张通过只读重放026存档脚本恢复成员；历史参照区间统一按044种子/10000重抽样新算，不冒充026原区间']}
    # 独立重数所有CSV的成员、簇分子分母与区间。
    checks=[]
    for file,rr in TABLES.items():
        for r in rr:
            m=MEMBERS[r['metric_id']];n=len(m['numerator_ids']);d=len(m['denominator_ids']);assert n==r['numerator'] and d==r['denominator']
            assert r['proportion']==(n/d if d else None)
            groups=GROUPS[r['benchmark']]
            nc=Counter(ENTITIES[i]['task'] for i in m['numerator_ids']);dc=Counter(ENTITIES[i]['task'] for i in m['denominator_ids']);w=WEIGHTS[r['benchmark']]
            bn=sum(w[:,j]*nc[g] for j,g in enumerate(groups));bd=sum(w[:,j]*dc[g] for j,g in enumerate(groups));valid=bd>0
            if valid.any():assert np.allclose(np.quantile(bn[valid]/bd[valid],[.025,.975]),[r['ci95_low'],r['ci95_high']],rtol=0,atol=1e-15)
        checks.append({'csv':file,'rows':len(rr),'numerators_denominators_ratios_and_ci_recomputed':True})
    validation['ratio_checks']=checks;P.dump('validation.json',validation)
    print(json.dumps({'main':validation['main_totals'],'denominator2':validation['denominator2'],'silent':TABLES['silent_errors.csv'],'root_groups':catalog['merged_object_groups']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
