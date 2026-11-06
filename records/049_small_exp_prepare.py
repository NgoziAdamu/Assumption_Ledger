"""Rebuild 049 inputs from verified 048 references, without opening any database.

Requires tiktoken and bashlex. Never executes agent code or calls any model.
Creates new files exclusively. Existing 048 files are read-only inputs.
"""
import copy
from collections import Counter
import csv
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import re
import statistics
import string
import sys
import tarfile
import tempfile

sys.dont_write_bytecode = True
import bashlex
import tiktoken

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'records/049_small_exp_inputs'
OLD = ROOT / 'records/048_small_exp_inputs'
PROMPTS = ROOT / 'records/049_prompts'
spec = importlib.util.spec_from_file_location('assemble049', ROOT / 'records/049_small_exp_assemble.py')
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
SOURCES = {}
ISSUES = []
OMISSION = '[Per-table sections of the data contract are omitted here. The sections relevant to each review appear under "Relevant specification and documentation".]'
CSV_LABEL = 'first line of file (may not be a header)'


def nodes(tree):
    yield tree
    for v in vars(tree).values():
        if isinstance(v, bashlex.ast.node):
            yield from nodes(v)
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, bashlex.ast.node):
                    yield from nodes(x)

def shell_parts(command):
    """Remove heredoc bodies before parsing shell syntax; retain exact bodies."""
    lines = command.splitlines(keepends=True)
    shell, bodies = [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        matches = list(re.finditer(r"<<(-?)\s*(['\"]?)([A-Za-z_][\w]*)\2", line))
        shell.append(re.sub(r"<<(-?)\s*(['\"]?)([A-Za-z_][\w]*)\2", '', line))
        i += 1
        for m in matches:
            body = []
            while i < len(lines):
                probe = lines[i].rstrip('\r\n')
                if m[1]:
                    probe = probe.lstrip('\t')
                if probe == m[3]:
                    break
                body.append(lines[i])
                i += 1
            terminated = i < len(lines)
            if terminated:
                i += 1
            # Bash accepts end-of-file as the end of an unterminated heredoc
            # (with a warning). Preserve that body; never repair its delimiter.
            bodies.append({'header': line, 'body': ''.join(body), 'delimiter': m[3],
                           'terminated': terminated})
    return ''.join(shell), bodies


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source(path):
    p = Path(path)
    data = p.read_bytes()
    SOURCES[str(p)] = sha(data)
    return data


def dump(path, obj):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def write(path, text):
    with Path(path).open('x', encoding='utf-8', newline='') as f:
        f.write(text)


def write_csv(path, rows):
    with Path(path).open('x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def file_ref(path):
    p = Path(path); data = source(p)
    return {'path':str(p.relative_to(ROOT)), 'source_sha256':sha(data), 'text_sha256':sha(data)}


def new_issue(task, kind, detail, action=None):
    row = {'id':f'N{len(ISSUES)+1:04}', 'task':task, 'kind':kind, 'action':action,
           'blocking':True, 'detail':detail}
    ISSUES.append(row)


def same_command_write_run(command):
    """Rule-a addition: earlier output redirection + later interpreter, same literal path."""
    shell, bodies = shell_parts(command)
    commands = [n for t in bashlex.parse(shell) for n in nodes(t) if n.kind=='command']
    writes, runs = [], []
    for n in commands:
        words = [p.word for p in n.parts if p.kind=='word']
        for p in n.parts:
            if p.kind=='redirect' and p.type in ['>','>>'] and hasattr(p.output,'word'):
                target=p.output.word
                if any(c in target for c in ['$','`','*','?','[']):
                    continue
                writes.append({'path':target, 'shell_command_range':list(n.pos),
                               'operator':p.type, 'shell_redirect_range':list(p.pos)})
        if words and Path(words[0]).name in ['python','python3','bash','sh']:
            if '-c' in words or '-m' in words:
                continue
            args = [w for w in words[1:] if not w.startswith('-')]
            if args:
                runs.append({'path':args[0], 'interpreter':words[0], 'shell_command_range':list(n.pos)})
    return [{'operation':'write_then_run_same_command', 'path':w['path'],
             'write':w, 'run':r, 'coordinate_system':'heredoc-body-stripped shell text'}
            for w in writes for r in runs
            if w['path']==r['path'] and w['shell_command_range'][1]<=r['shell_command_range'][0]]


def remove_table_sections(old):
    original = A.text_ref(old['fixed']['prompt'])
    path=Path(old['sections'][0]['source_path']); contract=source(path).decode('utf-8')
    if original.count(contract)!=1:
        raise ValueError('Expected exactly one full contract in event1: '+old['task'])
    offset=original.index(contract)
    spans=[]
    for s in old['sections']:
        r=s['ref']; text=A.text_ref(r)
        assert contract[r['start']:r['end']]==text
        assert text==''.join(contract.splitlines(keepends=True)[s['line_start']-1:s['line_end']])
        start,end=offset+r['start'],offset+r['end']
        spans.append({'id':s['id'],'contract_lines':[s['line_start'],s['line_end']],
                      'prompt_chars':[start,end], 'source_ref':r,'removed_text_sha256':sha(text.encode())})
    spans.sort(key=lambda r:r['prompt_chars'][0])
    cursor=0; pieces=[]
    for i,row in enumerate(spans):
        start,end=row['prompt_chars']
        assert cursor<=start<end
        pieces.append(original[cursor:start])
        if i==0:
            pieces.append(OMISSION+'\n')
        cursor=end
    pieces.append(original[cursor:])
    return original,''.join(pieces), {'contract_source':str(path),'contract_offset_in_prompt':offset,
           'omission_marker':OMISSION, 'removed_sections':spans,
           'removed_characters':sum(r['prompt_chars'][1]-r['prompt_chars'][0] for r in spans)}


def fixed(old, out):
    before=A.text_ref(old['fixed']['prompt'])
    if old['benchmark']=='DAComp':
        before,after,removal=remove_table_sections(old)
        dump(out/'prompt_removal.json',removal)
    else:
        after=before
    write(out/'prompt.txt',after)
    idx=json.loads(source(OLD/old['task']/'material_index.json'))
    index_text=A.text_ref(old['fixed']['index'])
    if old['benchmark']=='KramaBench':
        lines=index_text.splitlines(keepends=True)
        result=[lines[0]]
        for line in lines[1:]:
            view=json.loads(line)
            first=view.pop('csv_first_physical_line',None)
            result.append(json.dumps(view,ensure_ascii=False)+
                          ('\t'+CSV_LABEL+': '+json.dumps(first,ensure_ascii=False) if first is not None else '')+'\n')
        index_text=''.join(result)
        for row in idx['listed_rows']:
            if 'csv_first_physical_line' in row:
                row['first_line_label']=CSV_LABEL
    idx['reused_from']=f'records/048_small_exp_inputs/{old["task"]}/material_index.json'
    write(out/'material_index.txt',index_text)
    dump(out/'material_index.json',idx)
    return {'prompt':file_ref(out/'prompt.txt'),'index':file_ref(out/'material_index.txt')},before,after


def add_call(m, ids, rules, position, section_ids=None):
    lookup={a['id']:a for a in m['actions']}
    if section_ids is None:
        commands=[A.text_ref(lookup[i]['command']) for i in ids]
        section_ids=[s['id'] for s in m['sections'] if any(s['name'] in c for c in commands)]
    secs={s['id']:s for s in m['sections']}
    c={'task':m['task'],'call':len(m['calls'])+1,'kind':'regular','rules':rules,
       'position':position,'action_ids':list(ids),'action_range':[ids[0],ids[-1]],
       'section_ids':section_ids,
       'sections':[{k:secs[i][k] for k in ['id','source_path','line_start','line_end']} for i in section_ids],
       'assumptions':{'runtime':True,'empty_text':'(none)'},'pending_decision_ids':[]}
    m['calls'].append(c)


def add_final(m, old_final):
    c=copy.deepcopy(old_final)
    c.update(call=len(m['calls'])+1, pending_decision_ids=[],
             template='records/049_prompts/method1_final_rank.txt')
    m['calls'].append(c)


def build_da(m, old):
    segment=[]
    for a in m['actions']:
        cmd=A.text_ref(a['command'])
        a['rules_a_to_d_048']=list(a['rules_a_to_d'])
        ev=same_command_write_run(cmd)
        a['rule_a_same_command_evidence']=ev
        if ev:
            a['rules_a_to_d']=sorted(set(a['rules_a_to_d'])|{'a'})
            a['trigger_evidence'].extend({'rule':'a',**e} for e in ev)
        if not a['rules_a_to_d'] and any(x in cmd for x in ['sql/','.sql','open(','write_text']):
            m['suspicious_actions'].append({'task':m['task'],'event':a['id'],'command_first_300':cmd[:300]})
        segment.append(a['id'])
        rules=a['rules_a_to_d'] or (['e'] if len(segment)==5 else [])
        if rules:
            add_call(m,segment,rules,a['id']); segment=[]
    old_final=next(c for c in old['calls'] if c['kind']=='final')
    if segment:
        add_call(m,segment,['f_tail'],old_final['position'])
    add_final(m,old_final)


def response_ref(member, line, field, response):
    text=response
    for k in field:
        text=text[k]
    assert isinstance(text,str)
    return {'archive':'traces/kramabench_luna_baseline.tar.gz','member':member,
            'line':line,'field':field,'text_sha256':sha(text.encode())}


def build_kb(m, old, package_index):
    pi=package_index[m['task']]
    member=pi['messages_member']
    messages=[json.loads(line) for line in A.archive_member('traces/kramabench_luna_baseline.tar.gz',member).decode().splitlines()]
    acts=copy.deepcopy(m['actions'])
    existing={a['response_line'] for a in acts}
    nonexec=[]
    for line,r in enumerate(messages,1):
        if r.get('direction')!='response' or 'message' not in r or line in existing:
            continue
        msg=r['message']
        a={'id':f'response_call_{r["call"]}','label':f'模型 call {r["call"]}（无执行步骤）',
           'kind':'response_without_execution','model_call':r['call'],'response_line':line,
           'reasoning':[],'files_read':[]}
        if msg.get('content') is not None:
            a['content']=response_ref(member,line,['message','content'],r)
        seen=set()
        candidates=[]
        if msg.get('reasoning'):
            candidates.append((['message','reasoning'],msg['reasoning']))
        for j,rd in enumerate(msg.get('reasoning_details') or []):
            if rd['type']=='reasoning.encrypted':
                continue
            for k in ['summary','text']:
                if rd.get(k):candidates.append((['message','reasoning_details',j,k],rd[k]))
        for field,text in candidates:
            if text not in seen:
                seen.add(text);a['reasoning'].append(response_ref(member,line,field,r))
        if msg.get('tool_calls'):
            new_issue(m['task'],'response_has_unmatched_tool_call',
                      '没有对应execution的回复带tool_calls，未推断工具是否执行。',a['id'])
        acts.append(a);nonexec.append(a['id'])
    acts.sort(key=lambda a:a['response_line'])
    m['actions']=acts
    m['responses_without_execution']=[]
    old_calls={c['action_ids'][0]:c for c in old['calls'] if c['kind']=='regular'}
    waiting=[]
    for a in acts:
        waiting.append(a['id'])
        if a.get('kind')=='response_without_execution':
            continue
        old_call=old_calls[a['id']]
        add_call(m,waiting,['execution_step'],a['id'],old_call['section_ids'])
        for rid in waiting[:-1]:
            m['responses_without_execution'].append({'id':rid,'merged_into_call':m['calls'][-1]['call'],
                                                      'merged_into_execution_step':a['id']})
        waiting=[]
    old_final=next(c for c in old['calls'] if c['kind']=='final')
    if waiting:
        add_call(m,waiting,['f_tail'],old_final['position'],[])
        for rid in waiting:
            m['responses_without_execution'].append({'id':rid,'merged_into_call':m['calls'][-1]['call'],
                                                      'merged_into_execution_step':None})
    add_final(m,old_final)


def main():
    start=json.loads((BASE/'start_state.json').read_text())
    rows=list(csv.DictReader(source(ROOT/'records/047_premise_sentences_draft.csv').decode('utf-8-sig').splitlines()))
    da=sorted({re.match(r'impl-\d+',r['对象编号'])[0] for r in rows if r['benchmark']=='DAComp'})
    kb=sorted({r['对象编号'] for r in rows if r['benchmark']=='KramaBench'})
    assert len(da)==20 and len(kb)==9,(len(da),len(kb))
    old_summary=json.loads(source(OLD/'summary.json'))
    old_stats={t['task']:t for t in old_summary['tasks']}
    pi=json.loads(source(ROOT/'records/028_kramabench_package_index.json'))
    temp=Path(tempfile.mkdtemp(prefix='assumption-ledger-049-'))
    for archive in ['traces/dacomp_deimpl_prev.tar.gz','traces/kramabench_luna_baseline.tar.gz']:
        source(ROOT/archive)
        with tarfile.open(ROOT/archive) as t:
            if 'dacomp_deimpl' in archive:
                selected=[x for x in t.getmembers() if x.isfile() and '/events/' in x.name and
                          any(f'/20261025_de_official_batch_01/{task}/' in x.name for task in da)]
            else:
                names={pi[task][key] for task in kb for key in ['messages_member','steps_member']}
                selected=[x for x in t.getmembers() if x.name in names]
            t.extractall(temp,members=selected,filter='data')
    expected_fields={'method1_review.txt':{'task','material_index','spec_sections','ledger','steps'},
                     'method1_final_rank.txt':{'task','ledger'},
                     'method2_review.txt':{'task','material_index','spec_sections','trajectory'},
                     'judge_match.txt':{'table','premise','truth','items'},
                     'judge_stated.txt':{'table','premise','truth','agent_text'}}
    inv={}
    for name,fields in expected_fields.items():
        data=source(PROMPTS/name);text=data.decode('utf-8')
        found={field for _,field,_,_ in string.Formatter().parse(text) if field}
        assert found==fields,(name,found)
        inv[name]={'sha256':sha(data),'characters':len(text),'bytes':len(data),'placeholders':sorted(fields),
                   'source':'用户本轮给出的定稿原文；LF换行，末尾一个LF，未包含分隔标记。',
                   'archived_only':name.startswith('judge_')}
    dump(BASE/'prompt_inventory.json',inv)
    enc=tiktoken.get_encoding('o200k_base')
    def tokens(text):return len(enc.encode(text,disallowed_special=()))
    counts=[];task_stats=[];allvals=[];removal_stats=[]
    for task in da+kb:
        old=json.loads(source(OLD/task/'manifest.json'))
        out=BASE/task;out.mkdir()
        m={k:copy.deepcopy(v) for k,v in old.items() if k not in ['fixed','calls','method2','suspicious_actions',
             'uncalled_tail_action_ids','responses_without_execution','full_contract_is_literal_substring_of_prompt']}
        m.update(calls=[],suspicious_actions=[],uncalled_tail_action_ids=[],
                 baseline_manifest=f'records/048_small_exp_inputs/{task}/manifest.json')
        m['fixed'],before,after=fixed(old,out)
        if task in da:build_da(m,old)
        else:build_kb(m,old,pi)
        blockers=[r['id'] for r in ISSUES if r['task']==task]
        for c in m['calls']:c['pending_decision_ids']=blockers
        all_actions=[a['id'] for a in m['actions']]
        covered=[i for c in m['calls'] if c['kind']=='regular' for i in c['action_ids']]
        assert covered==all_actions
        used=list(dict.fromkeys(sid for c in m['calls'] if c['kind']=='regular' for sid in c['section_ids']))
        m['method2']={'task':task,'action_ids':all_actions,'section_ids':used,'fixed_parts':m['fixed'],
                       'pending_decision_ids':blockers,'definition':'所有动作/执行步骤与无执行回复；题面/索引各一份，所有普通叫起（含f_tail）材料节去重。'}
        dump(out/'manifest.json',m)
        dump(out/'method2_components.json',m['method2'])
        with (out/'calls.jsonl').open('x',encoding='utf-8') as f:
            for c in m['calls']:f.write(json.dumps(c,ensure_ascii=False)+'\n')
        pstat={'task':task,'benchmark':m['benchmark'],'removed_sections':len(old['sections']) if task in da else 0,
               'before_characters':len(before),'after_characters':len(after),
               'before_tokens':tokens(before),'after_tokens':tokens(after)}
        removal_stats.append(pstat)
        vals=[]
        for c in m['calls']:
            row={'benchmark':m['benchmark'],'task':task,'method':'method1','call':c['call'],
                 'rules':'|'.join(c['rules']),'tokens':'','ledger':'(none)',
                 'status':'pending_decisions' if blockers else 'ready','prompt_sha256':'',
                 'pending_decision_ids':'|'.join(blockers)}
            if c['kind']=='final':
                row.update(method='method1_final',ledger='runtime',status='runtime_only')
            elif not blockers:
                text=A.assemble(task,c['call']);n=tokens(text);vals.append(n);allvals.append(n)
                row.update(tokens=n,prompt_sha256=sha(text.encode()))
            counts.append(row)
        row={'benchmark':m['benchmark'],'task':task,'method':'method2','call':'','rules':'','tokens':'',
             'ledger':'not_applicable','status':'pending_decisions' if blockers else 'ready','prompt_sha256':'',
             'pending_decision_ids':'|'.join(blockers)}
        n2=None
        if not blockers:
            text=A.assemble(task,method2=True);n2=tokens(text)
            row.update(tokens=n2,prompt_sha256=sha(text.encode()))
        counts.append(row)
        rules=Counter(r for c in m['calls'] for r in c['rules'])
        tstat={'task':task,'benchmark':m['benchmark'],'actions':len(m['actions']),
               'execution_or_shell_actions':len(old['actions']),'calls':len(m['calls']),
               'regular_calls':sum(c['kind']=='regular' for c in m['calls']),
               'final_calls':sum(c['kind']=='final' for c in m['calls']),
               'delta_calls_vs_048':len(m['calls'])-old_stats[task]['calls'],
               'calls_048':old_stats[task]['calls'],'rule_counts':dict(rules),
               'method1_median':statistics.median(vals) if vals else None,
               'method1_max':max(vals) if vals else None,'method1_sum':sum(vals) if vals else None,
               'method2_tokens':n2,'prompt_before_after':pstat,'blocking_decisions':blockers,
               'same_command_a_events':[a['id'] for a in m['actions'] if a.get('rule_a_same_command_evidence')],
               'responses_without_execution':m.get('responses_without_execution',[])}
        task_stats.append(tstat)
    assert sum(r['removed_sections'] for r in removal_stats)==774
    write_csv(ROOT/'records/049_small_exp_token_counts.csv',counts)
    write_csv(BASE/'prompt_before_after.csv',removal_stats)
    suspicious=[r for task in da for r in json.loads((BASE/task/'manifest.json').read_text())['suspicious_actions']]
    write_csv(BASE/'suspicious_actions.csv',suspicious)
    dump(BASE/'decisions_for_claude.json',ISSUES)
    dump(BASE/'source_hashes.json',SOURCES)
    summary={'number':49,'start_commit':start['start_commit'],'baseline':'048','counts_are_provisional':bool(ISSUES),
             'task_count':29,'task_benchmarks':{'DAComp':20,'KramaBench':9},
             'ordinary_calls':sum(t['regular_calls'] for t in task_stats),'final_calls':sum(t['final_calls'] for t in task_stats),
             'delta_calls_vs_048':sum(t['delta_calls_vs_048'] for t in task_stats),
             'method1_median':statistics.median(allvals) if allvals else None,'method1_max':max(allvals) if allvals else None,
             'method1_sum':sum(allvals),'method2_sum':sum(t['method2_tokens'] or 0 for t in task_stats),
             'over_272000':[t['task'] for t in task_stats if t['method2_tokens'] and t['method2_tokens']>272000],
             'over_1050000':[t['task'] for t in task_stats if t['method2_tokens'] and t['method2_tokens']>1050000],
             'removed_table_sections':774,'suspicious_actions':len(suspicious),'new_issues':len(ISSUES),
             'tasks':task_stats,'temp_dir':str(temp),'encoding':'o200k_base',
             'counting':'完整模板填充文本（UTF-8解码）；ledger=(none)；交卷重排token留空，不计入合计。',
             'dependencies':{n:importlib.metadata.version(n) for n in ['tiktoken','bashlex']},'python':sys.version,
             'database_opened_or_queried':False,'model_api_calls':0,
             'excluded_from_counts':['API/chat envelope','nonempty runtime ledgers','final ranking prompts','outputs/reasoning','judge inputs/outputs']}
    dump(BASE/'summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='tasks'},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
