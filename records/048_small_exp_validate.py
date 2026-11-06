"""Independent source/coverage/token audit; never runs agent code or models.

Print JSON to stdout. Only --save creates a new validation.json, exclusively.
Requires tiktoken and duckdb. Does not import the preparation script.
"""
from collections import Counter
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import statistics
import subprocess
import sys
import tarfile

sys.dont_write_bytecode = True
import duckdb
import tiktoken

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'records/048_small_exp_inputs'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def original_block(text, key):
    header = re.search(r'<!-- original:' + re.escape(key) + r' chars:(\d+) -->\n(`{3,})[^\n]*\n', text)
    assert header, key
    return text[header.end():header.end()+int(header[1])]


def main():
    state = json.loads((BASE / 'start_state.json').read_text())
    # Includes the pre-existing dirty 044 report: compare working-tree bytes,
    # rather than requiring them to match HEAD.
    for name, expected in state['tracked_file_sha256'].items():
        assert digest((ROOT/name).read_bytes()) == expected, name
    sources = json.loads((BASE / 'source_hashes.json').read_text())
    for name, expected in sources.items():
        assert digest(Path(name).read_bytes()) == expected, name
    source_rows = list(csv.DictReader((ROOT/'records/047_premise_sentences_draft.csv').read_text(encoding='utf-8-sig').splitlines()))
    expected_da = sorted({re.match(r'impl-\d+', r['对象编号'])[0] for r in source_rows if r['benchmark']=='DAComp'})
    expected_kb = sorted({r['对象编号'] for r in source_rows if r['benchmark']=='KramaBench'})
    assert len(expected_da)==20 and len(expected_kb)==9
    ms = [json.loads(p.read_text()) for p in sorted(BASE.glob('*/manifest.json'))]
    assert sorted(m['task'] for m in ms)==sorted(expected_da+expected_kb)
    # Independent sequential archive reads, no assembler cache/helper involved.
    archives = {}
    for name in ['dacomp_deimpl_prev','kramabench_luna_baseline']:
        rel = f'traces/{name}.tar.gz'
        with tarfile.open(ROOT/rel) as tar:
            archives[rel] = {m.name:tar.extractfile(m).read() for m in tar if m.isfile() and
                             ('/events/' in m.name or m.name.endswith(('messages.jsonl','steps.jsonl')))}
    def read(r):
        data = archives[r['archive']][r['member']] if 'archive' in r else (ROOT/r['path']).read_bytes()
        if 'source_sha256' in r:
            assert digest(data)==r['source_sha256']
        val = data.decode()
        if 'field' in r:
            val = json.loads(val.splitlines()[r['line']-1] if 'line' in r else val)
            for k in r['field']:
                val=val[k]
        if 'start' in r:
            val=val[r['start']:r['end']]
        assert isinstance(val,str)
        if 'text_sha256' in r:
            assert digest(val.encode())==r['text_sha256']
        return val
    counts=Counter()
    issues=json.loads((BASE/'decisions_for_claude.json').read_text())
    issue_ids={r['id'] for r in issues}
    index028=json.loads((ROOT/'records/028_kramabench_package_index.json').read_text())
    for m in ms:
        task=m['task']; pdir=BASE/task
        prompt=read(m['fixed']['prompt'])
        if m['benchmark']=='DAComp':
            event_map={json.loads(data)['id']:json.loads(data) for path,data in archives['traces/dacomp_deimpl_prev.tar.gz'].items()
                       if f'/20261025_de_official_batch_01/{task}/agent/.events/' in path and path.endswith('.json')}
            assert prompt==event_map[1]['message']
            raw_actions=[e for i,e in sorted(event_map.items()) if e['source']=='agent' and e.get('action')=='run']
            assert [a['id'] for a in m['actions']]==[e['id'] for e in raw_actions]
            fin=[e['id'] for e in event_map.values() if e['source']=='agent' and e.get('action')=='finish']
            assert fin==[c['position'] for c in m['calls'] if c['kind']=='final']
            for a,e in zip(m['actions'],raw_actions):
                command=read(a['command']); assert command==e['args']['command']
                assert read(a['feedback'])==event_map[e['id']+1]['content']
                assert event_map[e['id']+1]['cause']==e['id']
                d=bool(re.search(r'\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW)\b',command,re.I))
                assert d==('d' in a['rules_a_to_d'])
                for ev in a['trigger_evidence']:
                    if ev['rule']=='b':
                        assert ev['previous_write_events'] and all(i<a['id'] for i in ev['previous_write_events'])
                        for i in ev['previous_write_events']:
                            assert ev['path'] in event_map[i]['args']['command']
                counts['da_commands_and_visible_results']+=1
            # Verify every contract section is a literal complete source span,
            # and all four-space name entries are represented, including duplicates.
            contract=Path(m['sections'][0]['source_path']).read_text()
            assert contract in prompt
            raw_names=[n.strip().strip('\"\'') for n in re.findall(r'^    - name: ([^\r\n]+)',contract,re.M)]
            assert Counter(s['name'] for s in m['sections'])==Counter(raw_names)
            for s in m['sections']:
                span=read(s['ref'])
                assert span.splitlines()[0].startswith('    - name: ') and s['name'] in span.splitlines()[0]
                assert span==''.join(contract.splitlines(keepends=True)[s['line_start']-1:s['line_end']])
                assert len(re.findall(r'^    - name:',span,re.M))==1
                counts['contract_spans']+=1
            idx=json.loads((pdir/'material_index.json').read_text())
            with duckdb.connect(idx['database_path'],read_only=True) as con:
                raw=con.execute('SELECT table_catalog,table_schema,table_name,column_name FROM information_schema.columns ORDER BY 1,2,3,ordinal_position').fetchall()
            expected=[(t['catalog'],t['schema'],t['table'],col) for t in idx['tables'] for col in t['columns']]
            assert raw==expected
            counts['database_schema_columns']+=len(raw)
        else:
            pi=index028[task]
            meta=json.loads((ROOT/pi['meta']).read_text())
            assert prompt==meta['prompt_values']['query']
            ex=[json.loads(line) for line in archives['traces/kramabench_luna_baseline.tar.gz'][pi['steps_member']].decode().splitlines()]
            ex=[e for e in ex if e.get('kind')=='execution']
            assert [a['id'] for a in m['actions']]==[e['step'] for e in ex]
            old=(ROOT/f'records/028_kramabench_packages/{task}.md').read_text()
            by_step={s['execution_step']:s for s in pi['steps'] if s['execution_step'] is not None}
            for a,e in zip(m['actions'],ex):
                n=by_step[a['id']]['ordinal']
                assert read(a['code'])==e['code']==original_block(old,f'step.{n}.code')
                assert a['files_read']==e['files_read']
                if a['feedback']:
                    txt=read(a['feedback'])
                    assert txt==original_block(old,f'step.{n}.feedback')
                    full=e['full_observation']
                    assert txt==(full if len(full)<=4000 else full[:1986]+'\n... [output truncated] ...\n'+full[-1986:])
                    counts['kb_visible_feedback']+=1
                    counts['kb_truncated_feedback']+=int(len(full)>4000)
                else:
                    assert by_step[a['id']]['feedback_line'] is None
                    counts['kb_missing_feedback']+=1
                old_reasoning=[original_block(old,r['field']) for r in by_step[a['id']]['reasoning'] if 'field' in r]
                assert [read(r) for r in a['reasoning']]==old_reasoning
                counts['kb_code_and_reasoning_steps']+=1
            idx=json.loads((pdir/'material_index.json').read_text())
            folder=Path(idx['input_directory'])
            files=sorted(p for p in folder.rglob('*') if p.is_file())
            assert len(files)==idx['total_files']
            for row in idx['listed_rows']:
                p=folder/row['file']
                if 'file_count' in row:
                    siblings=sorted(p.parent.glob('*'))
                    siblings=[s for s in siblings if s.is_file()]
                    assert len(siblings)==row['file_count']>50 and siblings[0]==p
                if 'first_line_sha256' in row:
                    with p.open('rb') as f: raw=f.readline()
                    assert digest(raw)==row['first_line_sha256']
                    assert raw.decode(row['encoding'])==row['csv_first_physical_line']
                counts['kb_index_rows']+=1
        lookup={a['id']:a for a in m['actions']}
        regular=[c for c in m['calls'] if c['kind']=='regular']
        covered=[i for c in regular for i in c['action_ids']]
        assert covered+m['uncalled_tail_action_ids']==[a['id'] for a in m['actions']]
        assert len(covered)==len(set(covered))
        union=list(dict.fromkeys(s for c in regular for s in c['section_ids']))
        assert m['method2']['action_ids']==covered
        assert m['method2']['section_ids']==union
        assert json.loads((pdir/'method2_components.json').read_text())==m['method2']
        assert [json.loads(line) for line in (pdir/'calls.jsonl').read_text().splitlines()]==m['calls']
        for c in regular:
            assert c['assumptions']=={'runtime':True,'initial_tokens':0}
            assert set(c['pending_decision_ids'])<=issue_ids
            if m['benchmark']=='DAComp':
                commands=[read(lookup[i]['command']) for i in c['action_ids']]
                expect=[s['id'] for s in m['sections'] if any(s['name'] in cmd for cmd in commands)]
                assert c['section_ids']==expect
                final_action=lookup[c['action_ids'][-1]]
                if c['rules']==['e']:
                    assert len(c['action_ids'])==5
                    assert all(not lookup[i]['rules_a_to_d'] for i in c['action_ids'])
                else:
                    assert c['rules']==final_action['rules_a_to_d']
                    assert len(c['action_ids'])<=5
                assert all(not lookup[i]['rules_a_to_d'] for i in c['action_ids'][:-1])
            else:
                assert len(c['action_ids'])==1
            counts['regular_calls']+=1
        for s in m['sections']:
            read(s['ref'])
        # The canonical runtime assembler must reject unresolved records by
        # default and reject final calls without runtime assumptions.
    spec=importlib.util.spec_from_file_location('assembler048',ROOT/'records/048_small_exp_assemble.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    enc=tiktoken.get_encoding('o200k_base')
    table=list(csv.DictReader((ROOT/'records/048_small_exp_token_counts.csv').open()))
    vals=[]
    for row in table:
        if row['method']=='method1_final':
            assert row['tokens']=='' and row['status']=='runtime_only'
            try:
                module.assemble(row['task'],int(row['call']))
            except ValueError:
                counts['final_input_correctly_deferred']+=1
            else:
                raise AssertionError('Final input must require runtime assumptions')
            continue
        method2=row['method']=='method2'
        text=module.assemble(row['task'],int(row['call']) if row['call'] else None,
                             method2=method2,allow_pending=True)
        assert len(enc.encode(text,disallowed_special=()))==int(row['tokens'])
        if row['status']=='pending_decisions':
            try:
                module.assemble(row['task'],int(row['call']) if row['call'] else None,method2=method2)
            except ValueError:
                counts['pending_inputs_correctly_guarded']+=1
            else:
                raise AssertionError('Unresolved inputs must require explicit review flag')
        if row['method']=='method1':
            vals.append(int(row['tokens']))
        counts['canonical_token_counts_checked']+=1
    summary=json.loads((BASE/'summary.json').read_text())
    assert len(vals)==summary['ordinary_calls']==counts['regular_calls']
    assert (sum(vals),max(vals),statistics.median(vals))==(summary['method1_sum'],summary['method1_max'],summary['method1_median'])
    m2=[r for r in table if r['method']=='method2']
    assert len(m2)==29
    for limit,key in [(272000,'over_272000'),(1050000,'over_1050000')]:
        assert sorted(r['task'] for r in m2 if int(r['tokens'])>limit)==sorted(summary[key])
    # Check numbering again, excluding exactly this task's new names.
    other=[]
    for dirname in ['notes','records']:
        for p in (ROOT/dirname).rglob('*'):
            if p.name.startswith('048_') or (p.is_relative_to(BASE)):
                continue
            match=re.match(r'^(\d{3})_',p.name)
            if match:
                other.append(int(match[1]))
    maximum=max(other)
    assert maximum==47, f'Number conflict: max={maximum}; must renumber before delivery'
    result={'passed':True,'checks':dict(counts),'original_tracked_files_unchanged':len(state['tracked_file_sha256']),
            'source_hashes_checked':len(sources),'scope':{'DAComp':len(expected_da),'KramaBench':len(expected_kb)},
            'number_recheck':{'max_other_number':maximum,'number':48,'renumbered':False},
            'method1_final_inputs_are_unknown_not_zero':True,
            'pending_design_decisions_are_not_resolved_by_validation':True}
    if '--save' in sys.argv:
        with (BASE/'validation.json').open('x',encoding='utf-8') as f:
            json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
