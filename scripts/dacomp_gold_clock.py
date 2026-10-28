"""Task 010: replace only runtime tokens and compare complete gold rows."""

from collections import Counter
from datetime import date,datetime
import hashlib
from pathlib import Path
import re
import tempfile

import duckdb

from compare_dacomp_staging import quote
from dacomp_trace_scan import lexical_regions
from dacomp_tolerance import normal_forms


CLOCK=re.compile(r'\b(?:CURRENT_DATE|CURRENT_TIMESTAMP|CURRENT_TIME|LOCALTIME|LOCALTIMESTAMP|SYSDATE|SYSTIMESTAMP)\b(?:\s*\(\s*\))?'
    r'|\b(?:NOW|TODAY|GETDATE|GETUTCDATE|SYSDATETIME|SYSUTCDATETIME|UTC_DATE|UTC_TIMESTAMP|CLOCK_TIMESTAMP|STATEMENT_TIMESTAMP|TRANSACTION_TIMESTAMP)\s*\(\s*\)',re.I)
DATE_NAMES={'CURRENT_DATE','TODAY','UTC_DATE'}
TIME_NAMES={'CURRENT_TIME','LOCALTIME'}


def runtime_tokens(text):
    regions=lexical_regions(text)
    return [m for m in CLOCK.finditer(text) if regions[m.start()]=='code']


def freeze_sql(text,day,path=''):
    date.fromisoformat(day)
    pieces=[];last=0;records=[]
    for match in runtime_tokens(text):
        name=re.sub(r'\s*\(\s*\)$','',match.group()).upper()
        if name in DATE_NAMES:literal=f"DATE '{day}'";kind='date'
        elif name in TIME_NAMES:literal="TIME '00:00:00'";kind='time_unknown_midnight_placeholder'
        else:literal=f"TIMESTAMPTZ '{day} 00:00:00+00:00'";kind='timestamp_unknown_midnight_UTC_placeholder'
        start,end=match.span();pieces.extend([text[last:start],literal]);last=end
        records.append({'path':str(path),'start_offset':start,'end_offset':end,'line':text.count('\n',0,start)+1,
            'column':start-text.rfind('\n',0,start),'original_text':match.group(),'replacement_text':literal,
            'function_name':name,'replacement_kind':kind,'candidate_date':day,'time_of_day_known':kind=='date'})
    pieces.append(text[last:]);frozen=''.join(pieces)
    # Reconstruct without SQL reserialization; every other byte is preserved.
    cursor=0;reconstructed=[]
    for item in records:
        assert text[item['start_offset']:item['end_offset']]==item['original_text']
        reconstructed.extend([text[cursor:item['start_offset']],item['replacement_text']]);cursor=item['end_offset']
    reconstructed.append(text[cursor:]);assert ''.join(reconstructed)==frozen
    return frozen,records


def date_only(value):
    if re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}(?:$|[ t].*)',value):
        try:
            parsed=date.fromisoformat(value) if len(value)==10 else datetime.fromisoformat(value.replace('z','Z'))
            return 'D'+(parsed.date() if isinstance(parsed,datetime) else parsed).isoformat()
        except ValueError:pass
    return 'S'+value


def compare_full_rows(connection,schema,table,gold_schema,columns,work):
    """Exact full-row multisets; date-only does not coerce or round numbers."""
    predicted=quote(schema)+'.'+quote(table)
    retained='gold_clock_reference.'+quote(gold_schema)+'.'+quote(table)
    counts=[connection.execute('SELECT count(*) FROM '+relation).fetchone()[0] for relation in (predicted,retained)]
    types={}
    for label,relation in [('prediction',predicted),('gold',retained)]:
        types[label]=[(r[0],r[1]) for r in connection.execute('DESCRIBE SELECT * FROM '+relation).fetchall()]
    schema_equal=[n.lower() for n,t in types['prediction']]==[n.lower() for n,t in types['gold']]
    result={'prediction_rows':counts[0],'gold_rows':counts[1],'prediction_columns':types['prediction'],'gold_columns':types['gold'],
        'same_column_names_and_order':schema_equal,'same_column_types':types['prediction']==types['gold'],
        'l0_full_match':False,'date_only_full_match':False,'l3_007_full_match':False,
        'column_scope':'all retained gold columns; no official compare_cols exclusion',
        'date_only_policy':'L0 text normalization then only ISO date/time -> date; no numeric/boolean coercion or rounding'}
    if not schema_equal or counts[0]!=counts[1]:return result
    expressions=','.join("coalesce(lower(trim(cast("+quote(c)+" as varchar))),'null')" for c in columns)
    if counts[0]*max(1,len(columns))<=500000:
        rows={label:connection.execute('SELECT '+expressions+' FROM '+relation).fetchall() for label,relation in [('p',predicted),('g',retained)]}
        for level,name in [(0,'l0_full_match'),(1,'date_only_full_match')]:
            convert=(lambda v:v) if level==0 else date_only
            result[name]=Counter(tuple(convert(v) for v in row) for row in rows['p'])==Counter(tuple(convert(v) for v in row) for row in rows['g'])
        result['l3_007_full_match']=True if result['date_only_full_match'] else None
        result['engine']='python_exact_counters';return result
    # Temporary tables live in the private connection, avoiding a second RW/RO
    # attachment of the hybrid file. Memory limits and spill paths are set by the worker.
    compare=connection
    for name,fn in [('clock_date_only',date_only)]:
        try:compare.remove_function(name)
        except Exception:pass
        compare.create_function(name,fn,['VARCHAR'],'VARCHAR')
    names=[f'c{i}' for i in range(len(columns))]
    temporary_names=['__clock_p','__clock_g','__clock_pcur','__clock_gcur']
    try:
        for label,relation in [('p',predicted),('g',retained)]:
            cells=','.join("coalesce(lower(trim(cast("+quote(c)+" as varchar))),'null') AS "+n for c,n in zip(columns,names))
            compare.execute(f'CREATE OR REPLACE TEMP TABLE __clock_{label} AS SELECT {cells},count(*) AS w FROM {relation} GROUP BY ALL')
        for fn,name in [('', 'l0_full_match'),('clock_date_only','date_only_full_match')]:
            value=','.join((f'{fn}({c})' if fn else c)+' AS '+c for c in names)
            for label in ('p','g'):
                compare.execute(f'CREATE OR REPLACE TEMP TABLE __clock_{label}cur AS SELECT {value},sum(w) w FROM __clock_{label} GROUP BY ALL')
            joins=' AND '.join(f'p.{c}=g.{c}' for c in names)
            result[name]=compare.execute(f'SELECT count(*)=0 FROM __clock_pcur p FULL JOIN __clock_gcur g ON {joins} WHERE coalesce(p.w,0)<>coalesce(g.w,0)').fetchone()[0]
            if result[name] and fn=='':result['date_only_full_match']=result['l3_007_full_match']=True;break
        result['l3_007_full_match']=True if result['date_only_full_match'] else None
    finally:
        for name in temporary_names:compare.execute('DROP TABLE IF EXISTS temp.'+name)
    result['engine']='duckdb_exact_weighted_rows';return result
