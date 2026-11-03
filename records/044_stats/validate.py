"""直接从源CSV独立核对044审计层；不导入统计构建逻辑。"""
import csv,json,hashlib
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'records/044_stats'
def j(p):return json.loads((OUT/p).read_text())
def run():
    cache={}
    def source(path,row):
        if path not in cache:
            assert not any(p.startswith('041') for p in Path(path).parts)
            with (ROOT/path).open() as f:cache[path]=list(csv.DictReader(f))
        return cache[path][int(row)-2]
    fixes=j('corrections_applied.json');assert len(fixes)==13 and all(x['applied'] for x in fixes)
    byloc={(x['source'],x['source_row'],x['field']):x for x in fixes}
    points=j('point_audit.json');objects=j('object_audit.json');pi=defaultdict(list)
    norm=lambda c:{'已说出的选择':'Unstated Choice','已说出的降级':'Quiet Downgrade'}.get(c,c)
    grades=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
    changed=[]
    for p in points:
        raw=source(p['source'],p['source_row'])
        for key,old in raw.items():
            f=byloc.get((p['source'],p['source_row'],key))
            expected=f['new'] if f else old
            assert p[key]==expected,(p['point_id'],key)
            if f:assert old==f['expected_old'];changed.append((p['point_id'],key))
        assert p['normalized_category']==norm(raw['类别'])
        assert p['grade']==grades.index(p['是否说出（五档）'])+1
        pi[p['对象编号']].append(p)
    assert len(changed)==13
    d2=[];collapsed=[]
    for o in objects:
        raw=source(o['source'],o['source_row']);id=o['object_id']
        if o['source']=='records/013_statuses.csv':
            assert raw['status'] in ['格式差异','日期差异'] and raw['task']+'_'+raw['table']==id
            assert o['original_main']==o['main_category']=='其他';continue
        assert raw['对象编号']==id and raw['主要原因']==o['original_main']
        combo=raw['是否只能组合修复']=='是'
        primary=[p for p in pi[id] if p['角色'] in {'主要','并列','同类候选'} or (combo and p['角色']=='组合项')]
        categories={norm(p['类别']) for p in primary};expected=norm(raw['主要原因'])
        if combo:expected='只能组合修复'
        elif expected=='多因并列' and len(categories)==1:expected=next(iter(categories));collapsed.append(id)
        assert expected==o['main_category']
        gs=[p['grade'] for p in primary]
        assert o['primary_grades']==gs and o['grade']==(max(gs) if gs else None)
        for suffix,allowed,fn in [('all_1',{1},all),('any_1',{1},any),('all_12',{1,2},all),('any_12',{1,2},any)]:
            assert o['disclosed_'+suffix]==(bool(gs) and fn(g in allowed for g in gs))
        assert o['denominator2']==(expected not in {'其他','不可评估','无法判定','未交卷','只能组合修复'})
    assert collapsed==['impl-009_stg_google_play__earnings']
    for b,n in [('DAComp',336),('KramaBench',42)]:
        selected=[o for o in objects if o['benchmark']==b];assert len(selected)==len({o['object_id'] for o in selected})==n
        counts=Counter(o['main_category'] for o in selected)
        with (OUT/f'main_{b}.csv').open() as f:rr=list(csv.DictReader(f))
        assert sum(int(r['numerator']) for r in rr if r['denominator_scope']=='分母一' and r['metric']!='跨阶段并列')==n
        for r in rr:
            if r['metric']=='跨阶段并列':continue
            pool=[o for o in selected if r['denominator_scope']=='分母一' or o['denominator2']]
            assert int(r['numerator'])==sum(o['main_category']==r['metric'] for o in pool)
            assert int(r['denominator'])==len(pool)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in j('input_hashes.json').items())
    v=j('validation.json');v['independent_source_csv_checks']={'every_point_field_reconstructed':True,'exactly_13_field_changes':True,'roles_categories_original_main_unchanged':True,'all_object_categories_and_disclosure_recomputed':True,'homogeneous_tie_objects':collapsed,'all_main_distribution_counts_recomputed':True}
    (OUT/'validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    print('独立源CSV核查通过。')
if __name__=='__main__':run()
