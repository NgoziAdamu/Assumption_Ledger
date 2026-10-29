"""Validate compact originals/indexes, raw metadata/counts and supplied human review."""

from collections import Counter,defaultdict
import csv
import json
from pathlib import Path
import re

from build_dacomp_slim_packages import render,constraints
from check_dacomp_constraints import open_readonly
from compare_dacomp_staging import fingerprint,quote
from complete_dacomp_comparisons import ROOT,RECORDS,save,stamp
from prepare_dacomp_annotation import EXPORT
from reconcile_dacomp_scope import jsonl


def original_field(event,field):
    if field.startswith('args.'):return event.get('args',{}).get(field[5:])
    return event.get(field)


def main():
    previous=jsonl(RECORDS/'012_statuses.jsonl');states=jsonl(RECORDS/'013_statuses.jsonl')
    index={(r['task'],r['layer'],r['table']):r for r in states};assert len(index)==len(previous)==1069
    formats={(r['task'],r['table']) for r in previous if r['status']=='格式差异（待核契约）'}
    review=json.loads((RECORDS/'013_review_basis.json').read_text());review_index={}
    for group,values in review['groups'].items():
        for task,tables in values['tables'].items():
            for table in tables:review_index[(task,table)]=(group,values['original_basis'])
    assert set(review_index)==formats and len(formats)==19
    assert Counter(v[0] for v in review_index.values())=={'A':9,'B':8,'C':2}
    changed=0
    specifics={(r['task'],r['table']):r['original_basis'] for r in review['specific_original_basis']}
    for old in previous:
        row=index[(old['task'],old['layer'],old['table'])]
        assert row['status_basis_012']==old['status_basis']
        if (old['task'],old['table']) in formats:
            changed+=1;assert row['status']=='格式差异';group,basis=review_index[(old['task'],old['table'])]
            r=row['human_review'];assert r['group']==group and r['group_basis_original']==basis
            assert r['specific_basis_original']==specifics.get((old['task'],old['table']))
            assert r['review_date']=='2026-10-29' and r['independent_Codex_classification'] is False
        else:assert row['status']==old['status'] and row['human_review'] is None
        for k,v in old.items():
            if k not in ('status','status_basis','status_source','prior_records_modified'):assert row[k]==v,(old['table'],k)
    assert changed==19
    inventory=json.loads((RECORDS/'013_package_inventory.json').read_text());old_inventory=json.loads((RECORDS/'012_package_inventory.json').read_text())
    old_index={(r['task'],r['layer'],r['table']):r for r in old_inventory};assert len(inventory)==30
    total_index_rows=sentence_occurrences=exempt_originals=0
    for item in inventory:
        identity=(item['task'],item['layer'],item['table']);old=old_index[identity]
        doc=json.loads((ROOT/item['source_012']).read_text());text=(ROOT/item['path']).read_bytes().decode('utf-8')
        expected,counts=render(doc,old,item['examples_per_column_limit'],item['exclusive_key_examples_limit'],item['008_evidence_examples_limit'])
        assert text==expected and len(text)==item['characters']
        assert item['without_SQL_contract_original_characters']==counts['without_SQL_contract_original_characters']
        rawtexts=[b['original_text'] for b in doc['contract_specification']['blocks']]+[s['text'] for s in doc['agent_final_SQL']+doc['gold_SQL_仅供定位差异']]
        for raw in rawtexts:assert raw in text;exempt_originals+=1
        assert len(text)-sum(len(raw) for raw in rawtexts)==item['without_SQL_contract_original_characters']
        assert item['examples_per_column_limit']<=3 and item['exclusive_key_examples_limit']<=5
        flags=doc['all_markers_and_evidence_008']['verbatim_record']['trace_flags']
        assert item['true_flag_count']==sum(value is True for value in flags.values())
        assert item['violated_constraint_count']==len(constraints(doc['agent_constraints_006']['agent']))
        directory=EXPORT/'runs/20261025_de_official_batch_01'/item['task']/'agent'
        events={}
        for path in directory.glob('.events/sessions/*/events/*.json'):
            e=json.loads(path.read_text());events[e['id']]=e
        assert item['event_count']==len(events)
        assert [r['event_id'] for r in item['trace_index']]==[r['event_id'] for r in doc['trace_excerpts']['steps']]
        for row in item['trace_index']:
            e=events[row['event_id']];command=e.get('args',{}).get('command','')
            assert row['command_prefix']==command[:200] and row['action']==e['action']
            observations=[o for o in events.values() if o.get('observation') and o.get('cause')==e['id']]
            assert row['output_characters']==sum(len(o.get('content','')) for o in observations)
            assert row['output_mentions_table']==any(re.search(r'(?<![A-Za-z0-9_])'+re.escape(item['table'])+r'(?![A-Za-z0-9_])',o.get('content',''),re.I) is not None for o in observations)
            truncated=any(re.search(r'^\[.*Observation truncated due to length.*\]$',o.get('content',''),re.M|re.I) for o in observations)
            assert row['original_truncation_marker']==bool(truncated)
            total_index_rows+=1
        from scan_dacomp_delivery import sentence_units
        expected_sentences=[]
        for e in sorted(events.values(),key=lambda r:r['id']):
            if e.get('source')!='agent' or 'action' not in e:continue
            for field in ('thought','message','args.thought','args.message'):
                value=original_field(e,field)
                if not isinstance(value,str):continue
                for sentence,start,end in sentence_units(value):
                    if re.search(r'(?<![A-Za-z0-9_])'+re.escape(item['table'])+r'(?![A-Za-z0-9_])',sentence,re.I):
                        expected_sentences.append((e['id'],field,sentence));assert sentence in text
        assert [(e,f,len(s)) for e,f,s in expected_sentences]==[(r['event_id'],r['field'],r['characters']) for r in item['thought_message_events']]
        sentence_occurrences+=len(expected_sentences)
        for s in doc['result_md_table_sentences']['sentences']:assert s['original_text'] in text
    assert len(list((RECORDS/'013_packages').glob('*.md')))==30
    pairs=jsonl(RECORDS/'013_raw_tables.jsonl');cases=json.loads((RECORDS/'013_cases.json').read_text());checked_tables=0
    for case in cases:
        recorded={r['table']:r for r in pairs if r['task']==case['task']}
        observed={}
        for side,pathkey in [('initial','initial_database'),('agent','agent_database')]:
            scratch=ROOT/'data/013_validation'/case['task']/side;scratch.mkdir(parents=True,exist_ok=True)
            with open_readonly(Path(case[pathkey]),scratch) as con:
                names=[r[0] for r in con.execute("SELECT table_name FROM information_schema.tables WHERE table_catalog=current_database() AND table_schema='raw' ORDER BY table_name").fetchall()]
                observed[side]=set(names)
                for table in names:
                    assert recorded[table][side] is not None
                    columns=con.execute("SELECT column_name,data_type,ordinal_position FROM information_schema.columns WHERE table_catalog=current_database() AND table_schema='raw' AND table_name=? ORDER BY ordinal_position",[table]).fetchall()
                    assert [{'name':n,'type':t,'ordinal_position':i} for n,t,i in columns]==recorded[table][side]['columns']
                    assert con.execute('SELECT count(*) FROM raw.'+quote(table)).fetchone()[0]==recorded[table][side]['row_count']
                    checked_tables+=1
        assert set(recorded)==observed['initial']|observed['agent']
        for table,row in recorded.items():
            expected=(table not in observed['initial'] or table not in observed['agent'] or row['initial']['columns']!=row['agent']['columns'] or row['initial']['row_count']!=row['agent']['row_count'])
            assert expected==row['different']
    writes=jsonl(RECORDS/'013_raw_write_steps.jsonl')
    for step in writes:
        event=json.loads(Path(step['event_file']).read_text());assert event['id']==step['event_id'] and event['args']['command']==step['command']
        assert step['command_direct_write_syntax'] or step['invoked_script_write_syntax']
        for hit in step['command_direct_write_syntax']:assert hit['original_match'] in step['command'] and hit['original_context'] in step['command']
        for call in step['invoked_script_write_syntax']:
            assert call['runtime_branch_execution_proven'] is False and call['exact_runtime_file_version_verified'] is False
            if call['provenance'].startswith('final retained'):
                text=Path(call['script_path']).read_bytes().decode('utf-8')
                for hit in call['matching_original_statements']:assert hit['original_context'] in text
    assert len({(r['task'],r['event_id']) for r in writes})==len(writes)
    before=json.loads((RECORDS/'013_input_before.json').read_text())['files'];after={p:fingerprint(Path(p)) for p in before}
    changed_files=[p for p in before if before[p]!=after[p]];assert not changed_files,changed_files
    save(RECORDS/'013_input_integrity.json',{'before':before,'after':after,'changed_files':changed_files,'all_unchanged':True,'finished_at':stamp()})
    with (RECORDS/'013_statuses.csv').open(newline='') as f:assert len(list(csv.DictReader(f)))==1069
    save(RECORDS/'013_validation.json',{'passed':True,'status_rows':1069,'reviewed_format_tables':19,'review_groups':{'A':9,'B':8,'C':2},
        'slim_packages':30,'contract_and_SQL_original_blocks_preserved':exempt_originals,'trace_index_rows_verified':total_index_rows,
        'agent_thought_message_sentences_verified':sentence_occurrences,'raw_table_pairs_verified':len(pairs),
        'raw_side_table_counts_and_ordered_schemas_rechecked':checked_tables,'raw_write_step_commands_verified':len(writes),
        'original_input_files_unchanged':len(before),'original_databases_unchanged':sum(Path(p).suffix=='.duckdb' for p in before),
        'old_004_012_records_unchanged':True,'old_012_packages_unchanged':True,'agent_or_gold_node_SQL_executions':0,
        'completed_at':stamp()})
    print('013 validation passed:',len(inventory),'packages,',len(pairs),'raw table pairs,',len(writes),'write-syntax steps',flush=True)


if __name__=='__main__':main()
