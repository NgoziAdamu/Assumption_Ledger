"""Independent read-only evidence checks for task 008; no attribution."""

from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import tarfile

import duckdb

from check_dacomp_constraints import open_readonly, save
from compare_dacomp_staging import fingerprint, quote
from scan_dacomp_delivery import ARCHIVE, RECORDS, ROOT, info


def scalar_checks(rows):
    checked=[]
    for number in range(1,31):
        case=info(number)
        selected=[r for r in rows if r['task']==case['task'] and r['output']['status']=='checked']
        scratch=ROOT/'data/008_validation_scratch'/case['task'];scratch.mkdir(parents=True,exist_ok=True)
        with open_readonly(Path(case['agent_database']),scratch/'spill') as connection:
            for row in selected:
                output=row['output'];relation=quote(output['actual_schema'])+'.'+quote(output['actual_table'])
                expressions=['count(*)']
                for c in output['columns']:
                    name=quote(c['name']);expressions.extend([f'count(*) FILTER(WHERE {name} IS NULL)',f'count(DISTINCT CAST({name} AS VARCHAR))'])
                sql='SELECT '+','.join(expressions)+' FROM '+relation
                values=connection.execute(sql).fetchone();count=values[0]
                assert count==output['row_count']
                nulls,constants=[],[]
                for i,c in enumerate(output['columns']):
                    null,distinct=values[1+2*i:3+2*i]
                    assert null==c['sql_null_rows']
                    if count>0 and null==count:nulls.append(c['name'])
                    if count>1 and null==0 and distinct==1:constants.append(c['name'])
                assert nulls==[c['column'] for c in output['all_null_columns']],(row['task'],row['table'],'nulls')
                assert constants==[c['column'] for c in output['constant_nonnull_columns']],(row['task'],row['table'],'constants')
                # All equal groups need exact confirmation and positive non-NULL support.
                pairs=[]
                for group in output['equal_column_groups']:
                    left=quote(group['columns'][0])
                    for other in group['columns'][1:]:
                        right=quote(other)
                        pairs.append(f"sum(CASE WHEN {left} IS NULL AND {right} IS NULL THEN 0 WHEN {left} IS NULL OR {right} IS NULL THEN 1 WHEN CAST({left} AS VARCHAR)<>CAST({right} AS VARCHAR) THEN 1 ELSE 0 END)")
                if pairs:
                    mismatches=connection.execute('SELECT '+','.join(pairs)+' FROM '+relation).fetchone()
                    assert all(v==0 for v in mismatches)
                checked.append({'task':row['task'],'layer':row['layer'],'table':row['table'],'rows':count,
                    'column_count':len(output['columns']),'equal_column_pairs_checked':len(pairs),'all_counts_agree':True})
        print(case['task'],'independent count/distinct checks',len(selected),flush=True)
    return checked


def reference_equal_groups(rows):
    """Compare complete column vectors, independent of SQL aggregate signatures."""
    checks=[]
    for number in (1,3,13,15,21,30):
        case=info(number)
        candidates=[r for r in rows if r['task']==case['task'] and r['output']['status']=='checked' and r['output']['row_count']<=2500]
        candidates=sorted(candidates,key=lambda r:(-bool(r['output']['equal_column_groups']),r['table']))[:3]
        scratch=ROOT/'data/008_validation_scratch'/case['task'];scratch.mkdir(parents=True,exist_ok=True)
        with open_readonly(Path(case['agent_database']),scratch/'spill') as connection:
            for row in candidates:
                o=row['output'];cols=[c['name'] for c in o['columns']]
                data=connection.execute('SELECT '+','.join('CAST('+quote(c)+' AS VARCHAR)' for c in cols)+' FROM '+quote(o['actual_schema'])+'.'+quote(o['actual_table'])).fetchall()
                groups=defaultdict(list)
                for i,name in enumerate(cols):
                    vector=tuple(record[i] for record in data)
                    if any(v is not None for v in vector):groups[vector].append(name)
                expected=sorted(sorted(names) for names in groups.values() if len(names)>1)
                actual=sorted(sorted(g['columns']) for g in o['equal_column_groups'])
                assert expected==actual,(row['task'],row['table'])
                checks.append({'task':row['task'],'layer':row['layer'],'table':row['table'],'rows':len(data),
                    'equal_groups':actual,'independent_complete_vectors_agree':True})
    return checks


def known_results(rows):
    selected013=[];selected015=[];selected030=[]
    for row in rows:
        if row['task']=='impl-013' and row['layer']=='staging':
            scans=row['agent_sql']
            if len(scans)==1 and scans[0]['outputs'] and len(scans[0]['outputs'])==len(scans[0]['null_literal_outputs']):
                text=Path(scans[0]['path']).read_text()
                count=len(re.findall(r'\bCAST\s*\(\s*NULL\s+AS\b',text,re.I))
                selected013.append({'table':row['table'],'rows':row['output']['row_count'],'output_columns':len(scans[0]['outputs']),
                    'literal_cast_null_occurrences_independent_regex':count,'sql_path':scans[0]['path']})
        if row['task']=='impl-015' and 'vendor' in row['table']:
            selected015.append({'table':row['table'],'rows':row['output']['row_count'],
                'all_null_name_columns':[c['column'] for c in row['output'].get('all_null_columns') or [] if c['column'] in ('name','vendor_name')]})
        if row['task']=='impl-030' and 'invoice_item' in row['table']:
            groups=[g for g in row['output'].get('equal_column_groups') or [] if 'invoice_item_id' in g['columns']]
            copied=[]
            for scan in row['agent_sql']:
                text=Path(scan['path']).read_text()
                copied.extend({'source_expression':m.group(1),'output_alias':m.group(2),
                    'path':scan['path'],'line':text.count('\n',0,m.start())+1}
                    for m in re.finditer(r'(?im)(\bid\b|try_cast\(\s*"?id"?\s+AS\s+VARCHAR\s*\))\s+AS\s+(\w+_id)\b',text))
            selected030.append({'table':row['table'],'rows':row['output']['row_count'],'equal_id_groups':groups,
                                'independent_direct_id_projection_regex_matches':copied})
    checks={'impl013':{'matches_known_observation':len(selected013)==3 and all(r['rows']==0 and r['output_columns']==r['literal_cast_null_occurrences_independent_regex'] for r in selected013),'tables':selected013},
        'impl015':{'matches_known_observation':any(r['table']=='stg_quickbooks__vendor' and 'name' in r['all_null_name_columns'] for r in selected015),'tables':selected015},
        'impl030':{'matches_known_observation':any(r['equal_id_groups'] and len(r['independent_direct_id_projection_regex_matches'])>=5 for r in selected030),'tables':selected030}}
    save(RECORDS/'008_known_results.json',checks)
    return {k:v['matches_known_observation'] for k,v in checks.items()}


def archive_checks(rows):
    versions=[]; excerpt_checks=0
    excerpts=[json.loads(line) for line in (RECORDS/'008_keyword_excerpts.jsonl').read_text().splitlines()]
    by_member=defaultdict(list)
    for e in excerpts:by_member[e['archive_member']].append(e)
    with tarfile.open(ARCHIVE,'r:gz') as archive:
        members={m.name:m for m in archive.getmembers() if m.isfile()}
        for row in rows:
            for path in row['inventory_sources']['agent_final_sql_files']:
                suffix=path.split('/runs/',1)[1];name='dacomp_deimpl_prev/runs/'+suffix
                archived=archive.extractfile(members[name]).read()
                current=Path(path).read_bytes();agree=current==archived
                assert agree,path
                versions.append({'path':path,'archive_member':name,'sha256':hashlib.sha256(current).hexdigest(),'same_bytes':agree})
        for name,items in by_member.items():
            source=archive.extractfile(members[name]).read().decode()
            parsed=json.loads(source) if name.endswith('.json') else None
            for e in items:
                if parsed is not None:
                    value=parsed
                    for part in e['json_path']:value=value[part]
                    token,_=json.JSONDecoder().raw_decode(source,e['json_string_token_start_offset'])
                    assert token==value
                    assert source.count('\n',0,e['json_string_token_start_offset'])+1==e['file_line']
                else:value=source
                first,last=e['decoded_sentence_start_offset'],e['decoded_sentence_end_offset']
                assert value[first:last]==e['original_text']
                assert value.count('\n',0,first)+1==e['decoded_field_line']
                for keyword in e['keywords']:assert keyword.lower() in e['original_text'].lower()
                for table in e['table_name_strings_in_sentence']:assert re.search(r'(?<![A-Za-z0-9_])'+re.escape(table)+r'(?![A-Za-z0-9_])',e['original_text'],re.I)
                if parsed is None:assert value.count('\n',0,first)+1==e['file_line']
                excerpt_checks+=1
    save(RECORDS/'008_sql_archive_version_checks.json',versions)
    return {'final_sql_files_same_as_archive':len(versions),'keyword_excerpts_exact_source_offsets_verified':excerpt_checks}


def metadata_checks(rows):
    assert len({(r['task'],r['layer'],r['table']) for r in rows})==len(rows)
    with (RECORDS/'008_table_scan.csv').open() as stream:csv_rows=list(csv.DictReader(stream))
    assert len(csv_rows)==len(rows)
    projection_discrepancies=[];literal_locations=0;runtime_locations=0;contract_excerpts=0
    for row in rows:
        for block in row['contract']['blocks']:
            lines=Path(block['path']).read_text().splitlines(keepends=True)
            assert ''.join(lines[block['start_line']-1:block['end_line']])==block['original_text']
            contract_excerpts+=1
        for data in row['time_dependencies'].values():
            for hit in data['hits']:
                lines=Path(hit['path']).read_text().splitlines()
                assert lines[hit['line']-1]==hit['line_text']
                assert hit['matched_text'] in hit['line_text']
                runtime_locations+=1
        if row['output']['status']=='checked' and len(row['agent_sql'])==1:
            actual=[c['name'].lower() for c in row['output']['columns']]
            projected=[c['name'].lower() for c in row['agent_sql'][0]['outputs']]
            if actual!=projected:projection_discrepancies.append({'task':row['task'],'layer':row['layer'],'table':row['table'],
                'actual_columns':actual,'sql_projection_names':projected})
        for scan in row['agent_sql']:
            lines=Path(scan['path']).read_text().splitlines()
            for column in scan['null_literal_outputs']+scan['constant_literal_outputs']:
                for alternative in column['alternatives']:
                    if alternative['kind']=='nonliteral':continue
                    if alternative['line'] is not None:
                        assert 1<=alternative['line']<=len(lines)
                        literal_locations+=1
    return {'csv_jsonl_rows':len(rows),'contract_original_blocks_verified':contract_excerpts,
        'runtime_original_line_locations_verified':runtime_locations,'literal_locations_in_range':literal_locations,
        'projection_name_discrepancies':projection_discrepancies}


def main():
    rows=[json.loads(line) for line in (RECORDS/'008_table_scan.jsonl').read_text().splitlines()]
    result={'metadata':metadata_checks(rows),'known_results':known_results(rows),'archive':archive_checks(rows)}
    assert all(result['known_results'].values()),result['known_results']
    result['independent_count_distinct_checks']=scalar_checks(rows)
    result['independent_complete_vector_checks']=reference_equal_groups(rows)
    integrity=json.loads((RECORDS/'008_input_integrity.json').read_text())
    assert integrity['all_unchanged']
    changed=[p for p,old in integrity['before'].items() if fingerprint(Path(p))!=old]
    assert not changed,changed
    mapping=json.loads((RECORDS/'008_mapping_input_integrity.json').read_text())
    mapping['after']={p:fingerprint(Path(p)) for p in mapping['before']}
    mapping['all_unchanged']=mapping['before']==mapping['after'];assert mapping['all_unchanged']
    save(RECORDS/'008_mapping_input_integrity.json',mapping)
    result['input_files_unchanged']=len(integrity['before'])+len(mapping['before'])
    result['passed']=True
    save(RECORDS/'008_validation.json',result)
    print('Validation passed',len(rows),'targets',flush=True)


if __name__=='__main__':main()
