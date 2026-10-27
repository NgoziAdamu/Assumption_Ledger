"""Monotone value tolerances with fixed L0 keys and exact row multisets."""

from collections import Counter, defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
import re
import tempfile

import duckdb
from compare_dacomp_staging import quote

NUMERIC = r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:e[+-]?[0-9]+)?'
DATE_LIKE = r'[0-9]{4}-[0-9]{2}-[0-9]{2}(?:$|[ t].*)'


def number_key(sign, digits, exponent):
    digits = digits.lstrip('0')
    if not digits:
        return 'N+0E0'
    tail = len(digits)-len(digits.rstrip('0'))
    return 'N'+('-' if sign else '+')+digits[:-tail]+'E'+str(exponent+tail) if tail else 'N'+('-' if sign else '+')+digits+'E'+str(exponent)


def increment(digits):
    tail = len(digits)-len(digits.rstrip('9'))
    if tail == len(digits):
        return '1'+'0'*tail
    return digits[:len(digits)-tail-1]+str(int(digits[len(digits)-tail-1])+1)+'0'*tail


def rounded_key(sign, digits, exponent):
    if exponent >= -2:
        return number_key(sign,digits,exponent)
    cut = -2-exponent
    if cut > len(digits):
        return 'N+0E0'
    keep = digits[:-cut] or '0'
    if digits[-cut] >= '5':
        keep = increment(keep)
    return number_key(sign,keep,-2)


@lru_cache(maxsize=200000)
def normal_forms(value):
    """Input is already L0 lower/trim/NULL-coalesced; output L1,L2,L3."""
    literal = 'S'+value
    if value in ('true','t','false','f'):
        key = 'N+1E0' if value in ('true','t') else 'N+0E0'
        return key,key,key
    if re.fullmatch(NUMERIC,value):
        try:
            parsed = Decimal(value)
            parts = parsed.as_tuple()
            digits = ''.join(map(str,parts.digits)) or '0'
            first = number_key(parts.sign,digits,parts.exponent)
            second = rounded_key(parts.sign,digits,parts.exponent)
            return first,second,second
        except (InvalidOperation,ValueError,OverflowError):
            return literal,literal,literal
    if value in ('inf','+inf','infinity','+infinity','-inf','-infinity'):
        key='N-Inf' if value.startswith('-') else 'N+Inf'
        return key,key,key
    if re.fullmatch(DATE_LIKE,value):
        try:
            parsed = date.fromisoformat(value) if len(value)==10 else datetime.fromisoformat(value[:-1]+'Z' if value.endswith('z') else value)
            day=parsed.date() if isinstance(parsed,datetime) else parsed
            return literal,literal,'D'+day.isoformat()
        except ValueError:
            pass
    return literal,literal,literal


def udf_forms(value):
    a,b,c=normal_forms(value)
    return {'l1':a,'l2':b,'l3':c}


def normalized(column):
    return "coalesce(lower(trim(cast("+quote(column)+" as varchar))),'null')"


def profile_keys(p,g):
    shared=set(p)&set(g)
    return {'pred_distinct_keys':len(p),'gold_distinct_keys':len(g),
            'pred_duplicate_key_groups':sum(n>1 for n in p.values()),'gold_duplicate_key_groups':sum(n>1 for n in g.values()),
            'pred_only_keys':len(set(p)-set(g)),'gold_only_keys':len(set(g)-set(p)),'shared_keys':len(shared),
            'shared_nonunique_key_groups':sum(p[k]!=1 or g[k]!=1 for k in shared)}


def diff_column(name,exact,minimum,pu,gu,ambiguous):
    return {'column':name,'one_to_one_mismatch_rows':int(exact),
            'nonunique_key_minimum_value_mismatch_pairs':int(minimum),
            'mismatch_rows_or_minimum_pairs':int(exact+minimum),
            'pred_unmatched_value_occurrences':int(pu),'gold_unmatched_value_occurrences':int(gu),
            'marginal_multisets_equal':pu==gu==0,
            'count_semantics':'minimum_value_mismatch_pairs' if ambiguous else 'exact_one_to_one_rows'}


def column_diffs(p,g,common,columns,pk,gk):
    if not common:return None
    ps,gs=defaultdict(list),defaultdict(list)
    for (key,values),weight in p.items():
        if key in common:ps[key].append((values,weight))
    for (key,values),weight in g.items():
        if key in common:gs[key].append((values,weight))
    ambiguous=any(pk[k]!=1 or gk[k]!=1 for k in common)
    output=[]
    for i,name in enumerate(columns):
        exact=minimum=pu=gu=0
        for key in common:
            pc,gc=Counter(),Counter()
            for values,w in ps[key]:pc[normal_forms(values[i])[2]]+=w
            for values,w in gs[key]:gc[normal_forms(values[i])[2]]+=w
            pn,gn=sum((pc-gc).values()),sum((gc-pc).values())
            pu+=pn;gu+=gn
            if pk[key]==gk[key]==1:exact+=min(pn,gn)
            else:minimum+=min(pn,gn)
        output.append(diff_column(name,exact,minimum,pu,gu,ambiguous))
    return output


def compare_python(pred,gold,table,schema,columns,keys):
    names=list(dict.fromkeys(keys+columns))
    def read(conn):
        rows=conn.execute('SELECT '+','.join(normalized(c) for c in names)+' FROM '+quote(schema)+'.'+quote(table)).fetchall()
        return Counter((tuple(r[names.index(c)] for c in keys),tuple(r[names.index(c)] for c in columns)) for r in rows)
    p,g=read(pred),read(gold)
    pk,gk=Counter(),Counter()
    for (k,v),n in p.items():pk[k]+=n
    for (k,v),n in g.items():gk[k]+=n
    common=set(pk)&set(gk)
    levels=[]
    for level in range(4):
        def transform(source,keyed):
            target=Counter()
            for (key,values),weight in source.items():
                if keyed and key not in common:continue
                converted=values if level==0 else tuple(normal_forms(v)[level-1] for v in values)
                target[(key,converted) if keyed else converted]+=weight
            return target
        levels.append({'level':f'L{level}','keyed_match':transform(p,True)==transform(g,True) if common else None,
                       'whole_match':transform(p,False)==transform(g,False)})
    return {'engine':'python_weighted_counters','levels':levels,'current_key_statistics':profile_keys(pk,gk),
            'l3_column_differences':column_diffs(p,g,common,columns,pk,gk)}


def sql_key_stats(conn):
    for side in ('p','g'):
        conn.execute(f'CREATE TABLE {side}k AS SELECT key0,sum(w) n FROM {side}0 GROUP BY key0')
    conn.execute('CREATE TABLE kg AS SELECT key0,pk.n pn,gk.n gn FROM pk FULL JOIN gk USING(key0)')
    row=conn.execute('''SELECT count(pn),count(gn),count(*) FILTER(WHERE pn>1),count(*) FILTER(WHERE gn>1),
      count(*) FILTER(WHERE pn IS NOT NULL AND gn IS NULL),count(*) FILTER(WHERE gn IS NOT NULL AND pn IS NULL),
      count(*) FILTER(WHERE pn IS NOT NULL AND gn IS NOT NULL),count(*) FILTER(WHERE pn IS NOT NULL AND gn IS NOT NULL AND (pn>1 OR gn>1)) FROM kg''').fetchone()
    return dict(zip(('pred_distinct_keys','gold_distinct_keys','pred_duplicate_key_groups','gold_duplicate_key_groups','pred_only_keys','gold_only_keys','shared_keys','shared_nonunique_key_groups'),row))


def compare_unique_different_sizes(conn,columns,stats):
    """A single key join; only distinct unequal value pairs need Decimal parsing."""
    expressions=','.join(f'p0.c{i} p{i},g0.c{i} g{i}' for i in range(len(columns)))
    conn.execute(f'CREATE TABLE aligned AS SELECT {expressions} FROM p0 JOIN g0 USING(key0) JOIN kg USING(key0) WHERE pn=1 AND gn=1')
    mismatches=[[0]*len(columns) for _ in range(4)]
    for i in range(len(columns)):
        cursor=conn.execute(f'SELECT p{i},g{i},count(*) n FROM aligned WHERE p{i}<>g{i} GROUP BY ALL')
        while rows:=cursor.fetchmany(10000):
            for p,g,n in rows:
                mismatches[0][i]+=n
                pp,gg=normal_forms(p),normal_forms(g)
                for level in range(3):mismatches[level+1][i]+=n*(pp[level]!=gg[level])
    return {'engine':'duckdb_unique_key_pair_histograms','levels':[{'level':f'L{i}','keyed_match':not any(mismatches[i]) if stats['shared_keys'] else None,'whole_match':False} for i in range(4)],
            'current_key_statistics':stats,'l3_column_differences':[diff_column(c,mismatches[3][i],0,mismatches[3][i],mismatches[3][i],False) for i,c in enumerate(columns)] if stats['shared_keys'] else None,
            'whole_proof':'row_count_mismatch_at_every_level'}


def joint_match(conn,pname,gname,columns,keyed):
    names=['c'+str(i) for i in range(len(columns))]
    group=['key0']+names if keyed else names
    cols=','.join(group)
    where=' JOIN kg USING(key0) WHERE pn IS NOT NULL AND gn IS NOT NULL' if keyed else ''
    for side,source in (('p',pname),('g',gname)):
        conn.execute(f'CREATE OR REPLACE TABLE {side}joint AS SELECT {cols},sum(w) w FROM {source}{where} GROUP BY ALL')
    return conn.execute(f'SELECT count(*)=0 FROM pjoint FULL JOIN gjoint USING({cols}) WHERE coalesce(pjoint.w,0)<>coalesce(gjoint.w,0)').fetchone()[0]


def compare_sql(pred_path,gold_path,table,schema,columns,keys,pred_rows,gold_rows,scratch,baseline_alignment):
    scratch.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='table_',dir=scratch) as tmp:
        with duckdb.connect(str(Path(tmp)/'comparison.duckdb')) as conn:
            conn.execute("SET memory_limit='768MB'; SET threads=2")
            conn.execute("SET temp_directory='"+str(Path(tmp)/'spill').replace("'","''")+"'")
            conn.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
            group_base=bool(baseline_alignment.get('pred_duplicate_key_groups') or baseline_alignment.get('gold_duplicate_key_groups'))
            for side,path in (('p',pred_path),('g',gold_path)):
                conn.execute("ATTACH '"+str(path).replace("'","''")+f"' AS {side}source (READ_ONLY)")
                key='list_value('+','.join(normalized(c) for c in keys)+') AS key0'
                values=','.join(normalized(c)+f' AS c{i}' for i,c in enumerate(columns))
                weight='count(*) AS w' if group_base else '1::BIGINT AS w'
                suffix=' GROUP BY ALL' if group_base else ''
                conn.execute(f'CREATE TABLE {side}0 AS SELECT {key},{values},{weight} FROM {side}source.{quote(schema)}.{quote(table)}{suffix}')
            stats=sql_key_stats(conn)
            if pred_rows!=gold_rows and not stats['shared_nonunique_key_groups']:
                return compare_unique_different_sizes(conn,columns,stats)
            differences=[];dictionaries=[];global_possible=pred_rows==gold_rows;key_possible=stats['shared_keys']>0
            for i,name in enumerate(columns):
                candidate=f"regexp_full_match(raw, '{NUMERIC}') OR regexp_full_match(raw,'{DATE_LIKE}') OR raw IN ('true','t','false','f','inf','+inf','-inf','infinity','+infinity','-infinity')"
                conn.execute(f'CREATE TABLE d{i} AS SELECT raw,tolerance_forms(raw) mapped FROM (SELECT c{i} raw FROM p0 UNION SELECT c{i} raw FROM g0) candidates WHERE {candidate}')
                exists=conn.execute(f'SELECT count(*)>0 FROM d{i}').fetchone()[0]
                dictionaries.append(exists)
                for side in ('p','g'):
                    expression=f"coalesce(d{i}.mapped.l3,'S'||c{i})" if exists else f"'S'||c{i}"
                    join=f' LEFT JOIN d{i} ON c{i}=d{i}.raw' if exists else ''
                    conn.execute(f'CREATE OR REPLACE TABLE {side}v AS SELECT key0,{expression} v,sum(w) n FROM {side}0{join} GROUP BY ALL')
                if stats['shared_keys']:
                    conn.execute('''CREATE OR REPLACE TABLE residual AS SELECT key0,
                      greatest(coalesce(pv.n,0)-coalesce(gv.n,0),0) pu,greatest(coalesce(gv.n,0)-coalesce(pv.n,0),0) gu
                      FROM pv FULL JOIN gv USING(key0,v)''')
                    conn.execute('''CREATE OR REPLACE TABLE perkey AS SELECT key0,max(pn) pn,max(gn) gn,sum(pu) pu,sum(gu) gu
                      FROM residual JOIN kg USING(key0) WHERE pn IS NOT NULL AND gn IS NOT NULL GROUP BY ALL''')
                    exact,minimum,pu,gu=conn.execute('''SELECT coalesce(sum(least(pu,gu)) FILTER(WHERE pn=1 AND gn=1),0),
                      coalesce(sum(least(pu,gu)) FILTER(WHERE pn>1 OR gn>1),0),coalesce(sum(pu),0),coalesce(sum(gu),0) FROM perkey''').fetchone()
                    differences.append(diff_column(name,exact,minimum,pu,gu,bool(stats['shared_nonunique_key_groups'])))
                    key_possible=key_possible and pu==gu==0
                if global_possible:
                    # Failure of one column's L3 marginal proves whole-row inequality at every level.
                    result=conn.execute('''WITH p AS(SELECT v,sum(n) n FROM pv GROUP BY v),g AS(SELECT v,sum(n) n FROM gv GROUP BY v)
                      SELECT count(*)=0 FROM p FULL JOIN g USING(v) WHERE coalesce(p.n,0)<>coalesce(g.n,0)''').fetchone()[0]
                    global_possible=global_possible and result
            levels=[];key_found=whole_found=False
            for level in range(4):
                need=(key_possible and not key_found) or (global_possible and not whole_found)
                pcur,gcur='p0','g0'
                if level and need:
                    for side in ('p','g'):
                        expressions=[];joins=[]
                        for i,exists in enumerate(dictionaries):
                            expressions.append((f"coalesce(d{i}.mapped.l{level},'S'||c{i})" if exists else f"'S'||c{i}")+f' AS c{i}')
                            if exists:joins.append(f' LEFT JOIN d{i} ON c{i}=d{i}.raw')
                        conn.execute(f"CREATE OR REPLACE TABLE {side}cur AS SELECT key0,{','.join(expressions)},sum(w) w FROM {side}0{''.join(joins)} GROUP BY ALL")
                    pcur,gcur='pcur','gcur'
                keyed=None if not stats['shared_keys'] else key_found or (key_possible and joint_match(conn,pcur,gcur,columns,True))
                whole=whole_found or (global_possible and joint_match(conn,pcur,gcur,columns,False))
                key_found=key_found or keyed is True;whole_found=whole_found or whole
                levels.append({'level':f'L{level}','keyed_match':keyed,'whole_match':whole})
            return {'engine':'duckdb_weighted_rows_and_value_dictionaries','levels':levels,'current_key_statistics':stats,
                    'l3_column_differences':differences if stats['shared_keys'] else None,
                    'l3_marginal_necessary_conditions':{'keyed':key_possible,'whole':global_possible},
                    'proof_policy':'a failed L3 column multiset or fixed row count proves failure at all finer levels; possible matches are checked using exact row tuples'}
