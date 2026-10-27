"""Audit coverage/declaration provenance and verify counts with independent SQL windows."""

from collections import Counter
import csv
import json
from pathlib import Path
import re
import yaml

from check_dacomp_constraints import ROOT, KINDS, open_readonly, save
from compare_dacomp_staging import fingerprint, quote, plain


def load(name):
    return json.loads((ROOT/'records'/name).read_text())


def independent_count(task, table, side, kind, check):
    scratch=ROOT/'data/006_validation_scratch'/task['task']/side
    scratch.mkdir(parents=True,exist_ok=True)
    mapping={c.lower():c for c in table[side]['actual_columns']}
    keys=[mapping[c.lower()] for c in check['columns']]
    relation=quote(table[side]['actual_schema'])+'.'+quote(table[side]['actual_table'])
    with open_readonly(Path(task[side+'_database']),scratch) as conn:
        if kind=='not_null':
            sql=f'SELECT count(*)-count({quote(keys[0])}) FROM {relation}'
            actual={'sql_null_rows':conn.execute(sql).fetchone()[0]}
        else:
            names=','.join(quote(c) for c in keys)
            nulls=' OR '.join(quote(c)+' IS NULL' for c in keys)
            freq='__window_frequency';sequence='__window_sequence'
            while freq.lower() in mapping:
                freq+='_'
            while sequence.lower() in mapping:
                sequence+='_'
            freq,sequence=quote(freq),quote(sequence)
            predicate=f'{freq}>1'+(f' AND NOT ({nulls})' if kind=='unique' else '')
            sql=f'''WITH numbered AS (SELECT {names},count(*) OVER(PARTITION BY {names}) AS {freq},
              row_number() OVER(PARTITION BY {names}) AS {sequence} FROM {relation})
              SELECT count(*) FILTER(WHERE {predicate} AND {sequence}=1),count(*) FILTER(WHERE {predicate}),
              count(*) FILTER(WHERE {predicate} AND {sequence}>1),count(*) FILTER(WHERE {nulls}) FROM numbered'''
            row=conn.execute(sql).fetchone()
            actual=dict(zip(('duplicate_key_groups','rows_in_duplicate_groups','excess_duplicate_rows','null_key_rows'),row))
    expected={k:check[k] for k in actual}
    return {'task':task['task'],'layer':table['layer'],'table':table['table'],'side':side,'kind':kind,
            'columns':check['columns'],'query_sql':sql,'actual':actual,'reported':expected,'equal':actual==expected}


def main():
    tasks=[load(f'006_contract_impl-{n:03d}.json') for n in range(1,31)]
    records=[r for t in tasks for r in t['tables']]
    jsonlines=[json.loads(line) for line in (ROOT/'records/006_contract_checks.jsonl').read_text().splitlines()]
    assert jsonlines==records
    keys={(r['task'],r['layer'],r['table']) for r in records}
    assert len(keys)==len(records)==1068
    preflight=json.loads((ROOT/'data/006_table_preflight.json').read_text())
    assert keys=={(r['task'],r['layer'],r['table']) for r in preflight}
    raw_occurrences,extracted_occurrences=Counter(),Counter()
    source_excerpts=0
    for task in tasks:
        path=Path(task['contract']['path']);text=path.read_text();lines=text.splitlines(keepends=True)
        try:
            root=yaml.safe_load(text)
            lexical=plain(yaml.compose(text))
        except yaml.YAMLError:
            escaped=text.replace('\\','\\\\')
            root=yaml.safe_load(escaped)
            lexical=plain(yaml.compose(escaped))
        def walk(value,trail):
            if isinstance(value,dict):
                for key,child in value.items():
                    if key=='grain':raw_occurrences[(task['task'],'grain',json.dumps(trail+[key]))]+=1
                    if key in ('primary_key','primary_keys'):raw_occurrences[(task['task'],'primary_key',json.dumps(trail+[key]))]+=1
                    if key in ('constraints','tests'):
                        for i,item in enumerate(child):
                            if isinstance(item,str) and item.strip().lower().replace(' ','_') in KINDS[1:]:
                                raw_occurrences[(task['task'],item.strip().lower().replace(' ','_'),json.dumps(trail+[key,i]))]+=1
                    walk(child,trail+[key])
            elif isinstance(value,list):
                for i,child in enumerate(value):walk(child,trail+[i])
        walk(root,[])
        for table in task['tables']:
            for kind in KINDS:
                for declaration in table['declarations'][kind]:
                    for source in declaration['sources']:
                        extracted_occurrences[(task['task'],kind,json.dumps(source['yaml_path']))]+=1
                        assert source['original_excerpt']==''.join(lines[source['start_line']-1:source['end_line']])
                        field_path=source['yaml_path'][:-1] if isinstance(source['yaml_path'][-1],int) else source['yaml_path']
                        value=lexical
                        for token in field_path:value=value[token]
                        assert value==source['decoded_value'],(task['task'],table['table'],kind)
                        literal=root
                        for token in source['yaml_path']:literal=literal[token]
                        if kind=='grain':assert literal==declaration['raw_text']
                        elif isinstance(literal,str):assert literal.strip().lower().replace(' ','_')==kind
                        else:assert literal==declaration['columns']
                        source_excerpts+=1
            for side in ('agent','gold'):
                out=table[side]
                if not out['table_exists']:assert out['row_count'] is None
                for kind in KINDS:
                    for check in out['checks'][kind]:
                        if check['status']!='checked':assert check['violated'] is None
                        elif kind=='not_null':assert check['sql_null_rows']<=out['row_count']
                        else:
                            assert check['rows_in_duplicate_groups']>=2*check['duplicate_key_groups']
                            assert check['excess_duplicate_rows']==check['rows_in_duplicate_groups']-check['duplicate_key_groups']
                            assert check['rows_in_duplicate_groups']<=out['row_count']
    assert raw_occurrences==extracted_occurrences,'A literal declaration was missed or duplicated'
    independent=[]
    for kind in KINDS:
        for side in ('agent','gold'):
            for violation in (True,False):
                chosen=None
                for task in tasks:
                    for table in task['tables']:
                        if not table[side]['table_exists'] or not table[side]['row_count'] or table[side]['row_count']>100000:continue
                        for check in table[side]['checks'][kind]:
                            if check['status']=='checked' and check['violated'] is violation:
                                chosen=(task,table,check);break
                        if chosen:break
                    if chosen:break
                if chosen:
                    result=independent_count(chosen[0],chosen[1],side,kind,chosen[2]);independent.append(result)
                    assert result['equal'],result
    unparsed=[];unknown=[]
    for table in records:
        for grain in table['declarations']['grain']:
            if grain['status']!='parsed':unparsed.append({'task':table['task'],'layer':table['layer'],'table':table['table'],'grain_original':grain['raw_text'],'reason':grain['reason']})
        for side in ('agent','gold'):
            for kind in KINDS:
                for check in table[side]['checks'][kind]:
                    if check['status']!='checked':unknown.append({'task':table['task'],'layer':table['layer'],'table':table['table'],'side':side,'kind':kind,'columns':json.dumps(check['columns'],ensure_ascii=False),'status':check['status'],'missing_columns':';'.join(check.get('missing_columns',[]))})
    for name,rows in [('006_unparsed_grains.csv',unparsed),('006_unknown_checks.csv',unknown)]:
        with (ROOT/'records'/name).open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    with (ROOT/'records/006_contract_checks.csv').open() as stream:
        csv_rows=list(csv.DictReader(stream))
    assert len(csv_rows)==len(records)
    for row,record in zip(csv_rows,records):
        assert (row['task'],row['layer'],row['table'])==(record['task'],record['layer'],record['table'])
        for side in ('agent','gold'):
            for kind in KINDS:assert json.loads(row[side+'_'+kind+'_checks'])==record[side]['checks'][kind]
    summary=load('006_contract_summary.json')
    for kind in (*KINDS,'any'):
        sets={}
        for side in ('agent','gold'):
            sets[side]={(r['task'],r['layer'],r['table']) for r in records if (r[side]['any_constraint_violated'] if kind=='any' else r[side]['categories'][kind]['violated']) is True}
            assert len(sets[side])==summary['summary'][kind][side]['violating_tables']
            assert len({r[0] for r in sets[side]})==summary['summary'][kind][side]['violating_tasks']
        assert len(sets['agent']&sets['gold'])==summary['summary'][kind]['both_violating_tables']
    integrity=load('006_input_integrity.json');assert integrity['unchanged'] is True
    assert all(fingerprint(Path(p))==v for p,v in integrity['before'].items())
    result={'passed':True,'tables':len(records),'raw_definition_entries':len(preflight),'literal_constraint_occurrences':dict(Counter(k[1] for k,n in raw_occurrences.items() for _ in range(n))),
            'source_excerpts_verified':source_excerpts,'independent_sql_checks':independent,'unparsed_grain_records':len(unparsed),
            'unknown_check_records':len(unknown),'original_files_verified':len(integrity['before']),
            'jsonl_csv_and_task_records_consistent':True,'summary_counts_independently_recounted':True}
    save(ROOT/'records/006_validation.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='independent_sql_checks'},ensure_ascii=False))


if __name__=='__main__':main()
