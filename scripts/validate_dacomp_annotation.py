"""Audit 012 statuses, sampling, verbatim packages, source values and input integrity."""

from collections import Counter,defaultdict
import csv
import hashlib
import json
from pathlib import Path
import random
import re
import tarfile

from build_dacomp_annotation_packages import render_package
from check_dacomp_constraints import open_readonly
from compare_dacomp_staging import fingerprint,quote
from complete_dacomp_comparisons import ROOT,RECORDS,PROJECT,save,stamp
from prepare_dacomp_annotation import ARCHIVE,EXPORT
from reconcile_dacomp_scope import key,jsonl
from validate_dacomp_agent_dates import forms as independent_forms


def json_at(path,trail):
    value=json.loads(Path(path).read_text())
    for part in trail:value=value[part]
    return value


def read_key_values(connection,basis,column,normalized_key):
    condition=' AND '.join("coalesce(lower(trim(cast("+quote(k)+" as varchar))),'null')=?" for k in basis['key_columns'])
    relation=quote(basis['actual_schema'])+'.'+quote(basis['table'])
    return connection.execute('SELECT cast('+quote(column)+' AS VARCHAR),count(*) FROM '+relation+' WHERE '+condition+' GROUP BY 1 ORDER BY 1 NULLS FIRST',[normalized_key[k] for k in basis['key_columns']]).fetchall()


def verify_sample(connection_pair,basis,column,sample,cleared_level=None):
    a,b=[read_key_values(connection,basis,column,sample['key_normalized']) for connection in connection_pair]
    if sample['kind']=='one_to_one':
        assert a==[(sample['agent_value'],1)] and b==[(sample['gold_value'],1)]
    else:
        for actual,field in [(a,'agent_values'),(b,'gold_values')]:assert [{'value':v,'rows':n} for v,n in actual[:5]]==sample[field]
    if cleared_level:
        level=int(cleared_level[-1]);convert=lambda v:'null' if v is None else v.strip(' ').lower()
        ap=Counter();bg=Counter()
        for raw,n in a:ap[independent_forms(convert(raw),level)]+=n
        for raw,n in b:bg[independent_forms(convert(raw),level)]+=n
        assert ap==bg,('Independent normalization did not clear a sample key',basis['table'],column,sample['key_normalized'])


def main():
    states=jsonl(RECORDS/'012_statuses.jsonl');old={key(r['task'],r['layer'],r['table']):r for r in jsonl(RECORDS/'009_corrected_statuses.jsonl')}
    index={key(r['task'],r['layer'],r['table']):r for r in states};assert len(states)==len(index)==1069
    gold={key(r['task'],r['layer'],r['table']):r for r in jsonl(RECORDS/'010_table_verification.jsonl')}
    aligned={key(r['task'],r['layer'],r['table']):r for r in jsonl(RECORDS/'011_table_alignment.jsonl')}
    task_verified=defaultdict(set)
    for g in gold.values():
        if g['verification'] in ['L0整表一致','仅日期层面一致']:task_verified[g['task']].update(g['validated_dates']+g['date_only_validated_dates'])
    expected_changes=set();protected_l0_l3=[]
    for identity,previous in old.items():
        result=index[identity];assert previous['status']==result['status_009']
        if previous['status']=='待标注' and identity in aligned:
            g=gold[identity];own=set(g['validated_dates']+g['date_only_validated_dates']) if g['verification']!='未能验证' else set()
            for a in aligned[identity]['attempts']:
                level=a.get('after',{}).get('whole_match_level');day=a['candidate_date']
                if not a['executed']:continue
                eligible=day in own or g['verification']=='未能验证' and day in task_verified[identity[0]]
                if eligible and level in ['L0','L1','L2']:expected_changes.add(identity)
                if g['verification']=='仅日期层面一致' and day in own and level=='L3':expected_changes.add(identity)
                if g['verification']=='L0整表一致' and level=='L3':protected_l0_l3.append(identity)
        if result['status']=='日期差异':assert identity in expected_changes
        if result['status']=='待标注':
            basis=result['difference_basis']
            if basis['kind']=='date_aligned_011':
                assert basis['candidate_date'] in gold[identity]['validated_dates']+gold[identity]['date_only_validated_dates']
                assert gold[identity]['verification']!='未能验证'
                attempt=next(a for a in aligned[identity]['attempts'] if a['candidate_date']==basis['candidate_date']);assert attempt['executed']
                assert basis['prediction_database']==attempt['prediction_snapshot']
                assert basis['l0_column_differences']==attempt['after']['l0_column_differences']
                assert basis['l3_column_differences']==attempt['after']['l3_column_differences']
            else:assert basis['kind']=='original_007_009'
    actual={k for k,r in index.items() if r['status']=='日期差异'};assert actual==expected_changes and len(actual)==34
    pending=[r for r in states if r['status']=='待标注'];assert len(pending)==283
    assert all(index[k]['status']=='待标注' for k in protected_l0_l3 if k not in expected_changes)
    annotations={key(r['task'],r['layer'],r['table']):r for r in json.loads((RECORDS/'010_impl002_replay_annotations.json').read_text())}
    assert sum(r['official_failed_replay_equal'] for r in states)==12
    for identity,annotation in annotations.items():assert index[identity]['official_failed_replay_equal_annotation']==annotation
    sampler=random.Random(20261029);expected=[]
    for task in sorted({r['task'] for r in pending}):
        pool=sorted((r for r in pending if r['task']==task),key=lambda r:(r['layer'],r['table']))
        selected=pool[sampler.randrange(len(pool))];expected.append((selected['task'],selected['layer'],selected['table']))
    sampling=json.loads((RECORDS/'012_sampling.json').read_text());assert expected==[(r['task'],r['layer'],r['table']) for r in sampling['samples']]
    assert len(expected)==30
    scans={key(r['task'],r['layer'],r['table']):r for r in jsonl(RECORDS/'008_table_scan.jsonl')}
    quoted_paths=set();trace_steps=raw_value_samples=sql_files=contract_blocks=0;inventory=json.loads((RECORDS/'012_package_inventory.json').read_text())
    for item in inventory:
        path=RECORDS/'012_packages'/(item['stem']+'.json');doc=json.loads(path.read_text());identity=key(item['task'],item['layer'],item['table'])
        assert identity in expected and doc['basic_information']['status']=='待标注'
        markdown=path.with_suffix('.md').read_bytes().decode('utf-8')
        assert markdown==render_package(doc)
        assert len(markdown)==item['markdown_characters'];assert len(path.read_text())==item['json_characters']
        basis=index[identity]['difference_basis']
        for name,value in basis.items():assert doc['differences'][name]==value,(identity,name)
        assert doc['all_markers_and_evidence_008']['verbatim_record']==scans[identity]
        case=json.loads((RECORDS/f'006_contract_{item["task"]}.json').read_text())
        c=next(c for c in case['tables'] if key(item['task'],c['layer'],c['table'])==identity)
        assert doc['agent_constraints_006']['agent']==c['agent'];assert doc['agent_constraints_006']['declarations']==c['declarations']
        for block in doc['contract_specification']['blocks']:
            text=Path(doc['contract_specification']['source_path']).read_bytes().decode('utf-8')
            assert ''.join(text.splitlines(keepends=True)[block['start_line']-1:block['end_line']])==block['original_text'];contract_blocks+=1
        for source in doc['agent_final_SQL']+doc['gold_SQL_仅供定位差异']:
            raw=Path(source['path']).read_bytes();assert source['text'].encode('utf-8')==raw
            assert hashlib.sha256(raw).hexdigest()==source['sha256'];sql_files+=1
        trace=doc['trace_excerpts'];all_events=[(p,json.loads(p.read_text())) for p in Path(trace['event_source_root']).glob('.events/sessions/*/events/*.json')]
        actions={e['id']:(p,e) for p,e in all_events if e.get('action')=='run'};observations=defaultdict(list)
        for p,e in all_events:
            if 'observation' in e:observations[e.get('cause')].append(e)
        terms={identity[2],*[name for source in trace['actual_read_sources_from_008_B7'] for name in (source,source.split('.')[-1])]}
        name_pattern=re.compile(r'(?<![A-Za-z0-9_])(?:'+'|'.join(re.escape(t) for t in terms)+r')(?![A-Za-z0-9_])',re.I)
        matches=set()
        for eid,(p,e) in actions.items():
            combined='\n'.join([e['args'].get('command','')]+[o.get('content','') for o in observations[eid]])
            if name_pattern.search(combined):matches.add(eid)
        assert matches=={s['event_id'] for s in trace['steps']}
        for step in trace['steps']:
            command=json_at(step['action_location']['file'],['args','command']);trace_steps+=1
            if step['retention']=='full_original':assert step['command']==command
            else:assert step['first_line_original']==command.splitlines(keepends=True)[0] and not step['target_table_name_hits']
            if step['target_table_name_hits']:assert step['retention']=='full_original'
            for output in step['outputs']:
                original=json_at(output['location']['file'],['content'])
                if step['retention']=='full_original':assert output['content']==original
                else:assert 'content' not in output
        result=doc['result_md_table_sentences']
        if result['present']:
            text=Path(result['path']).read_bytes().decode('utf-8')
            for sentence in result['sentences']:assert text[sentence['start_offset']:sentence['end_offset']]==sentence['original_text']
        quoted_paths.update(doc['original_files']['paths'])
        scratch=ROOT/'data/012_validation_scratch'/item['task'];scratch.mkdir(parents=True,exist_ok=True)
        with open_readonly(Path(basis['prediction_database']),scratch/'p') as pred,open_readonly(Path(basis['gold_database']),scratch/'g') as goldcon:
            for col in doc['differences']['column_details']:
                for sample in col['sample_key_groups']:verify_sample((pred,goldcon),basis,col['column'],sample);raw_value_samples+=1
    assert len(list((RECORDS/'012_packages').glob('*.json')))==len(list((RECORDS/'012_packages').glob('*.md')))==30
    formats=jsonl(RECORDS/'012_format_contracts.jsonl');assert len(formats)==19
    format_samples=0
    for record in formats:
        identity=key(record['task'],record['layer'],record['table']);assert index[identity]['status']=='格式差异（待核契约）'
        basis=record['difference_basis'];scratch=ROOT/'data/012_validation_scratch'/('format_'+record['task']);scratch.mkdir(parents=True,exist_ok=True)
        with open_readonly(Path(basis['prediction_database']),scratch/'p') as pred,open_readonly(Path(basis['gold_database']),scratch/'g') as goldcon:
            for column in record['columns']:
                assert column['column_first_cleared_level'] in ['L1','L2']
                assert column['agent_actual_type'] and column['gold_actual_type']
                for d in column['contract']['definitions']:
                    text=Path(d['path']).read_bytes().decode('utf-8')
                    assert ''.join(text.splitlines(keepends=True)[d['start_line']-1:d['end_line']])==d['original_text']
                for sample in column['sample_key_groups']:
                    verify_sample((pred,goldcon),basis,column['column'],sample,column['column_first_cleared_level']);format_samples+=1
    before=json.loads((RECORDS/'012_input_before.json').read_text())['files']
    expected_archive={}
    for path in quoted_paths:
        path=Path(path)
        if path.is_relative_to(EXPORT):member='dacomp_deimpl_prev/'+path.relative_to(EXPORT).as_posix()
        elif path.is_relative_to(PROJECT/'runs') and path.suffix=='.sql':member='dacomp_deimpl_prev/'+path.relative_to(PROJECT).as_posix()
        else:continue
        expected_archive[member]=fingerprint(path)['sha256']
    archive_verified=set()
    with tarfile.open(ARCHIVE,'r:gz') as archive:
        for member in archive:
            if member.name in expected_archive:
                assert hashlib.sha256(archive.extractfile(member).read()).hexdigest()==expected_archive[member.name],member.name
                archive_verified.add(member.name)
    assert archive_verified==set(expected_archive),set(expected_archive)-archive_verified
    after={p:fingerprint(Path(p)) for p in before};changed=[p for p in before if before[p]!=after[p]]
    assert not changed,changed
    save(RECORDS/'012_input_integrity.json',{'before':before,'after':after,'changed_files':changed,'all_unchanged':True,'finished_at':stamp()})
    with (RECORDS/'012_statuses.csv').open(newline='') as stream:csvrows=list(csv.DictReader(stream))
    assert len(csvrows)==1069
    for row in csvrows:assert index[key(row['task'],row['layer'],row['table'])]['status']==row['status']
    save(RECORDS/'012_validation.json',{'passed':True,'status_rows':1069,'date_changes_independently_verified':34,'pending_tables':283,
        'random_sample_reproduced':30,'package_MD_JSON_pairs_verified':30,'verbatim_contract_blocks_verified':contract_blocks,
        'complete_SQL_files_verified':sql_files,'complete_trace_step_selection_verified':trace_steps,
        'raw_package_value_samples_verified':raw_value_samples,'raw_format_samples_and_independent_normalization_verified':format_samples,
        'archive_source_files_verified':len(archive_verified),'format_tables':19,'format_columns':sum(len(r['columns']) for r in formats),
        'protected_L0_gold_L3_agent_tables_still_pending':[list(k) for k in protected_l0_l3 if k not in expected_changes],
        'original_input_files_unchanged':len(before),'original_databases_unchanged':sum(Path(p).suffix=='.duckdb' for p in before),
        'old_004_011_records_unchanged':True,'agent_SQL_executions':0,'gold_SQL_executions':0,'completed_at':stamp()})
    print('012 validation passed',len(before),'unchanged inputs,',trace_steps,'trace steps,',raw_value_samples+format_samples,'raw sample groups',flush=True)


if __name__=='__main__':main()
