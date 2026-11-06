"""Independent, model-free audit of sources, final rules, templates, and tokens.

Does not import the preparation script, open databases, or execute agent code.
Print JSON; --save exclusively creates records/049_small_exp_inputs/validation.json.
"""
from collections import Counter
import copy
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
import tempfile

sys.dont_write_bytecode = True
import bashlex
import tiktoken

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'records/049_small_exp_inputs'
OLD = ROOT/'records/048_small_exp_inputs'
PROMPTS = ROOT/'records/049_prompts'
MARKER = '[Per-table sections of the data contract are omitted here. The sections relevant to each review appear under "Relevant specification and documentation".]'
CSV_LABEL = 'first line of file (may not be a header)'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def masked_shell(command):
    """Independent mask: retain original character coordinates, hide heredoc data."""
    output=[]; waiting=[]
    for line in command.splitlines(keepends=True):
        if waiting:
            marker, tabs=waiting[0]
            probe=line.rstrip('\r\n')
            if tabs:probe=probe.lstrip('\t')
            output.append(''.join('\n' if c=='\n' else ' ' for c in line))
            if probe==marker:waiting.pop(0)
            continue
        matches=list(re.finditer(r"<<(-?)\s*(['\"]?)([A-Za-z_]\w*)\2",line))
        waiting.extend((m[3],bool(m[1])) for m in matches)
        chars=list(line)
        for m in matches:
            chars[m.start():m.end()]=[' ']*(m.end()-m.start())
        output.append(''.join(chars))
    return ''.join(output)


def walk(obj):
    if isinstance(obj,bashlex.ast.node):
        yield obj
        for v in vars(obj).values():yield from walk(v)
    elif isinstance(obj,list):
        for v in obj:yield from walk(v)


def expected_same_command_paths(command):
    writes=[];runs=[]
    for root in bashlex.parse(masked_shell(command)):
        for n in walk(root):
            if n.kind!='command':continue
            words=[p.word for p in n.parts if p.kind=='word']
            for p in n.parts:
                if p.kind=='redirect' and p.type in ['>','>>'] and hasattr(p.output,'word'):
                    path=p.output.word
                    if not any(c in path for c in '$`*?['):writes.append((path,n.pos[1]))
            if words and Path(words[0]).name in ['python','python3','bash','sh'] and not ({'-c','-m'}&set(words)):
                args=[w for w in words[1:] if not w.startswith('-')]
                if args:runs.append((args[0],n.pos[0]))
    return Counter(path for path,end in writes for target,start in runs if path==target and end<=start)


def check_number():
    own_files={ROOT/'records'/name for name in ['049_small_exp_assemble.py',
               '049_small_exp_prepare.py','049_small_exp_validate.py','049_small_exp_token_counts.csv']}
    own_files.add(ROOT/'notes/049_2026-11-06_小实验输入重建.md')
    numbers=[]
    for dirname in ['notes','records']:
        for p in (ROOT/dirname).rglob('*'):
            if p in own_files or p==BASE or p==PROMPTS or p.is_relative_to(BASE) or p.is_relative_to(PROMPTS):
                continue
            match=re.match(r'^(\d{3})_',p.name)
            if match:numbers.append(int(match[1]))
    assert max(numbers)==48,'Number occupied; renumber before delivery'
    return {'number':49,'max_other_number':48,'renumbered':False}


def main():
    stats=Counter()
    state=json.loads((BASE/'start_state.json').read_text())
    for name,h in state['tracked_file_sha256'].items():
        assert sha((ROOT/name).read_bytes())==h,name
    for name,h in json.loads((BASE/'source_hashes.json').read_text()).items():
        assert sha(Path(name).read_bytes())==h,name
    prompt_check=json.loads((BASE/'prompt_source_check.json').read_text())
    inventory=json.loads((BASE/'prompt_inventory.json').read_text())
    for name,row in inventory.items():
        data=(PROMPTS/name).read_bytes()
        assert sha(data)==row['sha256']==prompt_check['prompts'][name]['source_sha256']
        assert prompt_check['prompts'][name]['matches']
        stats['verbatim_prompt_templates']+=1
    # The immutable user message can also be checked when the local transcript exists.
    session=Path(prompt_check['source_session'])
    if session.exists():
        with session.open() as f:
            for i,line in enumerate(f,1):
                if i==prompt_check['user_message_line']:
                    source_msg=json.loads(line)['payload'];break
        txt=''.join(v.get('text','') for v in source_msg['content'] if v.get('type') in ['input_text','text'])
        assert sha(txt.encode())==prompt_check['source_message_sha256']
        for name in inventory:
            block=re.search(r'^----- '+re.escape(name)+r' -----\n(.*?)^----- end -----',txt,re.M|re.S)[1]
            assert block.encode()==(PROMPTS/name).read_bytes()
        stats['templates_checked_against_user_message']=5
    src_rows=list(csv.DictReader((ROOT/'records/047_premise_sentences_draft.csv').read_text(encoding='utf-8-sig').splitlines()))
    expected_da=sorted({re.match(r'impl-\d+',r['对象编号'])[0] for r in src_rows if r['benchmark']=='DAComp'})
    expected_kb=sorted({r['对象编号'] for r in src_rows if r['benchmark']=='KramaBench'})
    assert len(expected_da)==20 and len(expected_kb)==9
    manifests=[json.loads(p.read_text()) for p in sorted(BASE.glob('*/manifest.json'))]
    assert sorted(m['task'] for m in manifests)==sorted(expected_da+expected_kb)
    archives={}
    for archive in ['traces/dacomp_deimpl_prev.tar.gz','traces/kramabench_luna_baseline.tar.gz']:
        with tarfile.open(ROOT/archive) as tar:
            archives[archive]={m.name:tar.extractfile(m).read() for m in tar if m.isfile() and
                               ('/events/' in m.name or m.name.endswith(('/messages.jsonl','/steps.jsonl')))}
    def read(ref):
        data=archives[ref['archive']][ref['member']] if 'archive' in ref else (ROOT/ref['path']).read_bytes()
        if 'source_sha256' in ref:assert sha(data)==ref['source_sha256']
        text=data.decode('utf-8')
        if 'field' in ref:
            value=json.loads(text.splitlines()[ref['line']-1] if 'line' in ref else text)
            for key in ref['field']:value=value[key]
            text=value
        if 'start' in ref:text=text[ref['start']:ref['end']]
        if 'text_sha256' in ref:assert sha(text.encode())==ref['text_sha256']
        return text
    def wrap(title,text):return f'## {title}\n\n{text}\n\n'
    def render_source_actions(actions):
        pieces=[]
        for a in actions:
            pieces.append(f"### {a['label']}\n\n")
            for key,title in [('command','命令原文'),('code','代码原文')]:
                if key in a:pieces.append(wrap(title,read(a[key])))
            for ref in a.get('reasoning',[]):pieces.append(wrap('思考摘要原文',read(ref)))
            if a.get('content'):pieces.append(wrap('模型可读输出原文',read(a['content'])))
            if a.get('kind')=='response_without_execution':
                pieces.append('本次回复没有执行步骤。\n\n')
            elif a.get('feedback'):
                pieces.append(wrap('agent 实际看到的执行结果',read(a['feedback'])))
            else:
                pieces.append('执行结果：消息历史中未发现 agent 实际看到的对应反馈；未以本地完整输出补写。\n\n')
        return ''.join(pieces)
    for m in manifests:
        task=m['task'];old=json.loads((OLD/task/'manifest.json').read_text())
        assert m['sections']==old['sections']
        for sec in m['sections']:read(sec['ref'])
        idx=json.loads((BASE/task/'material_index.json').read_text());old_idx=json.loads((OLD/task/'material_index.json').read_text())
        idx_cmp=copy.deepcopy(idx);idx_cmp.pop('reused_from')
        if task in expected_da:
            assert idx_cmp==old_idx
            assert read(m['fixed']['index'])==read(old['fixed']['index'])
            original=read(old['fixed']['prompt']);contract=Path(old['sections'][0]['source_path']).read_text()
            assert original.count(contract)==1
            raw_lines=contract.splitlines(keepends=True);mask=[False]*len(raw_lines)
            for sec in old['sections']:
                for i in range(sec['line_start']-1,sec['line_end']):
                    assert not mask[i];mask[i]=True
                stats['removed_table_sections']+=1
            remaining=[];inserted=False
            for i,line in enumerate(raw_lines):
                if mask[i]:
                    if not inserted:remaining.append(MARKER+'\n');inserted=True
                else:remaining.append(line)
            expected=original.replace(contract,''.join(remaining),1)
            assert read(m['fixed']['prompt'])==expected
            assert expected.count(MARKER)==1
            removal=json.loads((BASE/task/'prompt_removal.json').read_text())
            assert len(removal['removed_sections'])==len(old['sections'])
            expected_calls=[];waiting=[]
            assert [a['id'] for a in m['actions']]==[a['id'] for a in old['actions']]
            for a,prior in zip(m['actions'],old['actions']):
                for key in ['command','feedback','result_event']:
                    assert a.get(key)==prior.get(key)
                command=read(a['command']);read(a['feedback'])
                paths=expected_same_command_paths(command)
                assert paths==Counter(e['path'] for e in a['rule_a_same_command_evidence'])
                rules=sorted(set(prior['rules_a_to_d'])|({'a'} if paths else set()))
                assert a['rules_a_to_d']==rules
                assert set(rules)-{'a'}==set(prior['rules_a_to_d'])-{'a'}
                waiting.append(a['id'])
                if rules or len(waiting)==5:
                    expected_calls.append((list(waiting),rules or ['e']));waiting=[]
                stats['da_commands_and_results']+=1
                stats['same_command_write_run_actions']+=bool(paths)
            if waiting:expected_calls.append((waiting,['f_tail']))
            assert [(c['action_ids'],c['rules']) for c in m['calls'] if c['kind']=='regular']==expected_calls
            for c in m['calls']:
                if c['kind']=='final':continue
                lookup={a['id']:a for a in m['actions']}
                commands=[read(lookup[i]['command']) for i in c['action_ids']]
                expect=[s['id'] for s in m['sections'] if any(s['name'] in cmd for cmd in commands)]
                assert c['section_ids']==expect
        else:
            assert read(m['fixed']['prompt'])==read(old['fixed']['prompt'])
            lines=read(m['fixed']['index']).splitlines()
            assert len(lines)==1+len(old_idx['listed_rows'])
            for n,(row,prior) in enumerate(zip(idx_cmp['listed_rows'],old_idx['listed_rows']),1):
                if 'csv_first_physical_line' in row:
                    assert row.pop('first_line_label')==CSV_LABEL
                    prefix,payload=lines[n].split('\t'+CSV_LABEL+': ',1)
                    assert json.loads(payload)==prior['csv_first_physical_line']
                    stats['labelled_csv_first_lines']+=1
                assert row==prior
            assert idx_cmp==old_idx
            prior_by_id={a['id']:a for a in old['actions']}
            for a in m['actions']:
                if a.get('kind')!='response_without_execution':
                    assert a==prior_by_id[a['id']]
                    for key in ['code','content','feedback']:
                        if a.get(key):read(a[key])
                    for ref in a['reasoning']:read(ref)
                    stats['unchanged_kb_execution_steps']+=1
                else:
                    pi=json.loads((ROOT/'records/028_kramabench_package_index.json').read_text())[task]
                    r=json.loads(archives['traces/kramabench_luna_baseline.tar.gz'][pi['messages_member']].decode().splitlines()[a['response_line']-1])
                    assert r['direction']=='response' and not r['message'].get('tool_calls')
                    assert read(a['content'])==r['message']['content']
                    for ref in a['reasoning']:read(ref)
                    stats['nonexecuting_responses_included']+=1
            assert [a['response_line'] for a in m['actions']]==sorted(a['response_line'] for a in m['actions'])
            lookup={a['id']:a for a in m['actions']}
            prior_calls={c['action_ids'][0]:c for c in old['calls'] if c['kind']=='regular'}
            for c in m['calls']:
                if c['kind']=='final':continue
                if c['rules']==['f_tail']:
                    assert all(lookup[i].get('kind')=='response_without_execution' for i in c['action_ids'])
                else:
                    ids=c['action_ids'];assert all(lookup[i].get('kind')=='response_without_execution' for i in ids[:-1])
                    assert ids[-1] in prior_by_id
                    assert c['section_ids']==prior_calls[ids[-1]]['section_ids']
            if task=='environment-hard-16':
                attached=next(c for c in m['calls'] if 'response_call_7' in c['action_ids'])
                assert attached['action_ids']==['response_call_7',7] and attached['call']==7
        regular=[c for c in m['calls'] if c['kind']=='regular']
        covered=[i for c in regular for i in c['action_ids']]
        assert covered==[a['id'] for a in m['actions']]
        assert len(covered)==len(set(covered))
        assert m['method2']['action_ids']==covered
        union=list(dict.fromkeys(s for c in regular for s in c['section_ids']))
        assert union==m['method2']['section_ids']
        assert not any(c['pending_decision_ids'] for c in m['calls'])
        assert not m['method2']['pending_decision_ids']
        assert [c['call'] for c in m['calls']]==list(range(1,len(m['calls'])+1))
        assert len([c for c in m['calls'] if c['kind']=='final'])==1
        assert m['calls'][-1]['kind']=='final'
        assert json.loads((BASE/task/'method2_components.json').read_text())==m['method2']
        assert [json.loads(line) for line in (BASE/task/'calls.jsonl').read_text().splitlines()]==m['calls']
        stats['ordinary_calls']+=len(regular)
        stats['f_tail_calls']+=sum(c['rules']==['f_tail'] for c in regular)
    spec=importlib.util.spec_from_file_location('assembler049',ROOT/'records/049_small_exp_assemble.py')
    A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
    enc=tiktoken.get_encoding('o200k_base')
    table=list(csv.DictReader((ROOT/'records/049_small_exp_token_counts.csv').open()))
    by_task={m['task']:m for m in manifests};values=[]
    for row in table:
        if row['method']=='method1_final':
            assert row['tokens']=='' and row['status']=='runtime_only'
            stats['final_rank_tokens_deferred']+=1;continue
        m=by_task[row['task']];lookup={a['id']:a for a in m['actions']};secs={s['id']:s for s in m['sections']}
        is_m2=row['method']=='method2'
        c=m['method2'] if is_m2 else next(c for c in m['calls'] if c['call']==int(row['call']))
        substitutions={'task':read(m['fixed']['prompt']),'material_index':read(m['fixed']['index']),
                       'spec_sections':''.join(wrap(i,read(secs[i]['ref'])) for i in c['section_ids'])}
        substitutions['trajectory' if is_m2 else 'steps']=render_source_actions([lookup[i] for i in c['action_ids']])
        if not is_m2:substitutions['ledger']='(none)'
        template='method2_review.txt' if is_m2 else 'method1_review.txt'
        expected=(PROMPTS/template).read_text().format_map(substitutions)
        actual=A.assemble(row['task'],int(row['call']) if row['call'] else None,method2=is_m2)
        assert actual==expected
        assert sha(actual.encode())==row['prompt_sha256']
        assert len(enc.encode(actual,disallowed_special=()))==int(row['tokens'])
        assert row['status']=='ready'
        if not is_m2:values.append(int(row['tokens']))
        stats['complete_prompt_text_and_tokens_checked']+=1
    summary=json.loads((BASE/'summary.json').read_text())
    assert len(values)==summary['ordinary_calls']==stats['ordinary_calls']
    assert (sum(values),max(values),statistics.median(values))==(summary['method1_sum'],summary['method1_max'],summary['method1_median'])
    old_stats={r['task']:r for r in json.loads((OLD/'summary.json').read_text())['tasks']}
    for t in summary['tasks']:
        m=by_task[t['task']]
        assert t['calls']==len(m['calls'])
        assert t['delta_calls_vs_048']==len(m['calls'])-old_stats[t['task']]['calls']
        assert t['rule_counts']==dict(Counter(r for c in m['calls'] for r in c['rules']))
        prior=read(json.loads((OLD/t['task']/'manifest.json').read_text())['fixed']['prompt'])
        after=read(m['fixed']['prompt']);ps=t['prompt_before_after']
        assert (len(prior),len(after))==(ps['before_characters'],ps['after_characters'])
        assert (len(enc.encode(prior,disallowed_special=())),len(enc.encode(after,disallowed_special=())))==(ps['before_tokens'],ps['after_tokens'])
        stats['prompt_before_after_stats']+=1
    for limit,key in [(272000,'over_272000'),(1050000,'over_1050000')]:
        assert sorted(r['task'] for r in table if r['method']=='method2' and int(r['tokens'])>limit)==sorted(summary[key])
    assert json.loads((BASE/'decisions_for_claude.json').read_text())==[]
    assert stats['removed_table_sections']==774
    # CLI tests exercise ordinary, f_tail, final-rank, method2, and supplied JSON.
    tmp=Path(tempfile.mkdtemp(prefix='assumption-ledger-049-cli-'))
    sample={'id':'sample-1','call':1,'statement':'Literal {task} and {steps} remain data.',
            'about':'data','target':'sample_table','evidence_of_dependence':'原文 {ledger}',
            'alternative':None,'importance':1,'reason':'仅作拼装接口核验。','updates':None}
    ledger=tmp/'ledger.json';ledger.write_text(json.dumps([sample],ensure_ascii=False))
    tail=next((m,c) for m in manifests for c in m['calls'] if c['rules']==['f_tail'])
    cases=[['impl-001','1'],[tail[0]['task'],str(tail[1]['call'])],
           ['impl-001','1','--ledger-json',str(ledger)],['impl-001','--final-rank','--ledger-json',str(ledger)],
           ['biomedical-hard-5','--method2']]
    for args in cases:
        r=subprocess.run([sys.executable,str(ROOT/'records/049_small_exp_assemble.py'),*args],capture_output=True)
        assert r.returncode==0,r.stderr.decode()
        if '--ledger-json' in args:
            output=r.stdout.decode();assert 'Literal {task} and {steps} remain data.' in output
            section='=== Recorded premises ===\n' if '--final-rank' in args else '=== Premises recorded in earlier reviews ===\n'
            body=output.split(section,1)[1].split('\n\n=== Agent steps since the last review ===',1)[0]
            assert json.loads(body)==[sample]
        stats['cli_cases_passed']+=1
    number_recheck=check_number()
    result={'passed':True,'checks':dict(stats),'original_tracked_files_unchanged':len(state['tracked_file_sha256']),
            'number_recheck':number_recheck,
            'database_opened_or_queried':False,'model_api_calls':0,'new_rule_gaps':0}
    if '--save' in sys.argv:
        with (BASE/'validation.json').open('x',encoding='utf-8') as f:
            json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
