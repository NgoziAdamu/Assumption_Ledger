"""Independent Decimal/Counter spot checks and full artifact/baseline validation."""

from collections import Counter,defaultdict
import csv
from datetime import date,datetime
from decimal import Decimal,localcontext,ROUND_HALF_UP
from functools import lru_cache
import json
from pathlib import Path
import re
import duckdb

from compare_dacomp_staging import fingerprint,quote

ROOT=Path(__file__).resolve().parents[1]


@lru_cache(maxsize=150000)
def reference_value(value,level):
    if level==0:return value
    if value in ('true','t','false','f'):
        return ('number',Decimal(1 if value in ('true','t') else 0))
    numeric=re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?',value,re.ASCII)
    if numeric or value in ('inf','+inf','infinity','+infinity','-inf','-infinity'):
        d=Decimal(value)
        if level>=2 and d.is_finite() and d.as_tuple().exponent<-2:
            with localcontext() as ctx:
                ctx.prec=max(100,len(d.as_tuple().digits)+abs(d.adjusted())+10)
                d=d.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
        return ('number',d)
    if level==3 and re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:$|[ t].*)',value,re.ASCII):
        try:
            d=date.fromisoformat(value) if len(value)==10 else datetime.fromisoformat(value.replace('z','Z'))
            return ('date',d.date().isoformat() if isinstance(d,datetime) else d.isoformat())
        except ValueError:pass
    return ('string',value)


def spot_check(record):
    columns=record['comparison_columns'];keys=record['baseline_alignment']['columns'];names=list(dict.fromkeys(keys+columns))
    sql='SELECT '+','.join("coalesce(lower(trim(cast("+quote(c)+" as varchar))),'null')" for c in names)+' FROM '+quote(record['layer'])+'.'+quote(record['table'])
    data={}
    for side,path in [('p',record['prediction_database']),('g',record['gold_database'])]:
        with duckdb.connect(path,read_only=True) as conn:rows=conn.execute(sql).fetchall()
        data[side]=[(tuple(r[names.index(c)] for c in keys),tuple(r[names.index(c)] for c in columns)) for r in rows]
    pk,gk=Counter(k for k,v in data['p']),Counter(k for k,v in data['g']);common=set(pk)&set(gk)
    levels=[]
    for level in range(4):
        counters={}
        for side in ('p','g'):
            allrows=Counter();shared=Counter()
            for key,row in data[side]:
                value=tuple(reference_value(v,level) for v in row)
                allrows[value]+=1
                if key in common:shared[(key,value)]+=1
            counters[side]=(allrows,shared)
        levels.append({'level':f'L{level}','whole_match':counters['p'][0]==counters['g'][0],
                       'keyed_match':counters['p'][1]==counters['g'][1] if common else None})
    assert levels[0]['whole_match']==record['l0_exact_row_tuple_match']
    levels[0]['whole_match']=record['baseline_l0_whole_match']
    assert levels==record['levels'],(record['scope'],record['task'],record['table'],levels)
    differences=[]
    if common:
        grouped={}
        for side in ('p','g'):
            groups=defaultdict(list)
            for key,row in data[side]:
                if key in common:groups[key].append(row)
            grouped[side]=groups
        for i,column in enumerate(columns):
            exact=minimum=pu=gu=0
            for key in common:
                p=Counter(reference_value(r[i],3) for r in grouped['p'][key]);g=Counter(reference_value(r[i],3) for r in grouped['g'][key])
                pp,gg=sum((p-g).values()),sum((g-p).values());pu+=pp;gu+=gg
                if pk[key]==gk[key]==1:exact+=min(pp,gg)
                else:minimum+=min(pp,gg)
            expected=record['l3_column_differences'][i]
            actual=(exact,minimum,pu,gu)
            assert actual==tuple(expected[k] for k in ('one_to_one_mismatch_rows','nonunique_key_minimum_value_mismatch_pairs','pred_unmatched_value_occurrences','gold_unmatched_value_occurrences'))
            differences.append({'column':column,'exact_rows':exact,'minimum_pairs':minimum,'pred_unmatched':pu,'gold_unmatched':gu})
    return {'scope':record['scope'],'task':record['task'],'table':record['table'],'levels':levels,
            'l3_column_counts_verified':len(differences),'reference':'Decimal objects and ROUND_HALF_UP quantize, independent of canonical digit/exponent implementation'}


def main():
    records=[json.loads(s) for s in (ROOT/'records/007_tolerance_tables.jsonl').read_text().splitlines()]
    summary=json.loads((ROOT/'records/007_tolerance_summary.json').read_text());assert len(records)==331
    expected={};baselines={}
    for scope,prefix in [('staging','004_staging'),('cs','005_cs')]:
        for path in sorted((ROOT/'records').glob(prefix+'_impl-*.json')):
            source=json.loads(path.read_text())
            for t in source['tables']:
                if scope=='cs' and not(t['prediction']['exists'] and t['gold']['exists'] and t['current_pred_execution']):continue
                expected[(scope,source['task'],t['table'])]=t
    assert set(expected)=={(r['scope'],r['task'],r['table']) for r in records}
    for r in records:
        baseline=expected[(r['scope'],r['task'],r['table'])]
        assert r['baseline_alignment']==baseline['alignment']
        assert r['baseline_prediction_rows']==baseline['prediction']['row_count']
        assert r['baseline_gold_rows']==baseline['gold']['row_count']
        assert r['baseline_row_delta']==baseline['row_count_delta_pred_minus_gold']
        assert r['baseline_l0_whole_match']==baseline['official_current_match']
        for field in ('keyed_match','whole_match'):
            seen=False
            for level in r['levels']:
                if level[field] is True:seen=True
                if seen:assert level[field] is True,'A tolerance became stricter'
        if r['comparison_status']=='compared':
            assert r['input_row_counts_match_baseline'] and r['key_statistics_match_baseline'] and r['l0_whole_reproduced'],(r['scope'],r['task'],r['table'])
        if r['keyed_availability']=='no_shared_keys':
            assert r['keyed_match_level'] is None and r['l3_column_differences'] is None
    with (ROOT/'records/007_tolerance_tables.csv').open() as stream:csvrows=list(csv.DictReader(stream))
    assert len(csvrows)==len(records)
    for row,r in zip(csvrows,records):
        assert (row['scope'],row['task'],row['table'])==(r['scope'],r['task'],r['table'])
        assert row['keyed_level']==(r['keyed_match_level'] or '不可比较')
        assert row['whole_level']==(r['whole_match_level'] or '不可比较')
        assert json.loads(row['l3_columns'])==r['l3_inconsistent_columns']
    for scope in ('staging','cs'):
        for kind in ('keyed','whole'):
            actual=dict(Counter(r[kind+'_match_level'] or '不可比较' for r in records if r['scope']==scope))
            assert actual==summary['scopes'][scope][kind+'_levels']
    chosen=[];covered=set()
    for r in records:
        if r['comparison_status']!='compared':continue
        cells=(r['current_prediction']['row_count']+r['current_gold']['row_count'])*len(set(r['comparison_columns']+r['baseline_alignment']['columns']))
        labels={(r['scope'],kind,r[kind+'_match_level']) for kind in ('keyed','whole')}
        if cells<=200000 and labels-covered:
            chosen.append(r);covered.update(labels)
    # Include a real nonunique-key table, independently checking lower-bound counts.
    if not any(r['baseline_alignment'].get('shared_nonunique_key_groups',0)>0 for r in chosen):
        chosen.append(next(r for r in records if r['baseline_alignment'].get('shared_nonunique_key_groups',0)>0 and (r['current_prediction']['row_count']+r['current_gold']['row_count'])*len(r['comparison_columns'])<=200000))
    for r in records:
        if r['l0_exact_tuple_agrees_with_original_official'] is False and r not in chosen:chosen.append(r)
    checks=[spot_check(r) for r in chosen]
    remaining=[r for r in records if r['keyed_match_level']=='仍不匹配' or r['whole_match_level']=='仍不匹配']
    with (ROOT/'records/007_l3_remaining.jsonl').open('w') as stream:
        for r in remaining:stream.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
    unavailable=[{'scope':r['scope'],'task':r['task'],'table':r['table'],'keyed_availability':r['keyed_availability'],'whole_level':r['whole_match_level'] or '不可比较'} for r in records if r['keyed_match_level'] is None or r['whole_match_level'] is None]
    with (ROOT/'records/007_unavailable.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(unavailable[0]),lineterminator='\n');writer.writeheader();writer.writerows(unavailable)
    integrity=json.loads((ROOT/'records/007_input_integrity.json').read_text());assert integrity['unchanged'] is True
    assert all(fingerprint(Path(p))==f for p,f in integrity['before'].items())
    result={'passed':True,'tables':len(records),'baseline_scope_and_statistics_unchanged':True,'l0_baseline_reproduced_tables':sum(r['l0_whole_reproduced'] is True for r in records),
            'levels_monotone':True,'independent_reference_checks':checks,'original_files_verified':len(integrity['before']),
            'remaining_records':len(remaining),'unavailable_keyed_records':len(unavailable)}
    temporary=ROOT/'records/007_validation.json.pending';temporary.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');temporary.replace(ROOT/'records/007_validation.json')
    print(json.dumps({k:v for k,v in result.items() if k!='independent_reference_checks'},ensure_ascii=False))


if __name__=='__main__':main()
