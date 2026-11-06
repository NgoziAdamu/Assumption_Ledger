"""Prepare static, provenance-backed experiment inputs. Never executes agent code.

Requires tiktoken, duckdb, PyYAML, bashlex. All new files are created exclusively.
Reproduction: use a clean checkout without records/048_small_exp_inputs (apart
from start_state.json), then run this script. Archives are extracted to /tmp.
Only information_schema.columns is queried, on *_start.duckdb in read-only mode.
"""
import ast
from collections import Counter, defaultdict
import csv
import functools
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import posixpath
import re
import statistics
import subprocess
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET
import zipfile

sys.dont_write_bytecode = True
import bashlex
import duckdb
import tiktoken
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'records/048_small_exp_inputs'
DA_RUN = Path('/home/katherine/dac/runs/20261025_de_official_batch_01')
DA_INITIAL = Path('/home/katherine/dac/benchmarks/dacomp-de')
KB_DATA = ROOT / 'data/kramabench/data'
spec = importlib.util.spec_from_file_location('assemble048', ROOT / 'records/048_small_exp_assemble.py')
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
ISSUES = []
SOURCES = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


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
        w.writeheader()
        w.writerows(rows)


def source(path):
    path = Path(path)
    data = path.read_bytes()
    SOURCES[str(path)] = sha(data)
    return data


def ref_file(path, text=None, start=None, end=None):
    path = Path(path)
    data = source(path)
    r = {'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
         'source_sha256': sha(data)}
    if start is not None:
        r.update(start=start, end=end)
    if text is not None:
        r['text_sha256'] = sha(text.encode())
    return r


def ref_event(archive, member, field, obj, line=None):
    for k in field:
        obj = obj[k]
    assert isinstance(obj, str)
    r = {'archive': archive, 'member': member, 'field': field,
         'text_sha256': sha(obj.encode())}
    if line is not None:
        r['line'] = line
    return r


def issue(task, kind, detail, action=None, blocking=True):
    row = {'id': f'D{len(ISSUES)+1:04}', 'task': task, 'kind': kind,
           'action': action, 'blocking': blocking, 'detail': detail}
    ISSUES.append(row)
    return row['id']


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


def python_sql_write(code):
    """Literal .sql occurrence plus open(...,w/a) or .write_text; no inference."""
    # Invalid read-only code cannot match the writing condition in rule a.
    if not re.search(r'write_text|[\'\"](?:w|a)[\'\"]', code):
        return False, []
    tree = ast.parse(code)
    sql = any(isinstance(n, ast.Constant) and isinstance(n.value, str) and '.sql' in n.value
              for n in ast.walk(tree))
    writes = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        if isinstance(n.func, ast.Attribute) and n.func.attr == 'write_text':
            writes.append({'operation': 'write_text', 'line': n.lineno})
        if isinstance(n.func, ast.Name) and n.func.id == 'open':
            modes = n.args[1:2] + [v.value for v in n.keywords if v.arg == 'mode']
            if any(isinstance(v, ast.Constant) and v.value in ['w', 'a'] for v in modes):
                writes.append({'operation': 'open(w/a)', 'line': n.lineno})
    return sql and bool(writes), writes


def classify(task, action, command, previous_scripts, cwd):
    rules, evidence, newly_written = set(), [], set()
    shell, bodies = shell_parts(command)
    trees = bashlex.parse(shell)
    ns = [n for t in trees for n in nodes(t)]
    commands = [n for n in ns if n.kind == 'command']
    for n in ns:
        if n.kind != 'redirect' or n.type not in ['>', '>>']:
            continue
        path = getattr(n.output, 'word', '')
        if path.endswith('.sql'):
            rules.add('a'); evidence.append({'rule': 'a', 'operation': 'redirect', 'path': path})
        if path.endswith(('.py', '.sh')):
            newly_written.add(posixpath.normpath(posixpath.join(cwd, path)))
    py_sources = []
    for n in commands:
        words = [p.word for p in n.parts if p.kind == 'word']
        if not words:
            continue
        prog = posixpath.basename(words[0])
        if prog == 'sed' and any(w == '-i' or w.startswith('-i') for w in words[1:]):
            for path in words[1:]:
                if path.endswith('.sql'):
                    rules.add('a'); evidence.append({'rule': 'a', 'operation': 'sed -i', 'path': path})
        if prog == 'perl' and any(re.match(r'^-[A-Za-z]*p[A-Za-z]*i|^-[A-Za-z]*i[A-Za-z]*p', w)
                                  for w in words[1:]):
            for path in words[1:]:
                if path.endswith('.sql'):
                    rules.add('a'); evidence.append({'rule': 'a', 'operation': 'perl -pi', 'path': path})
        run_paths = []
        if re.fullmatch(r'python(?:\d+(?:\.\d+)*)?', prog) or prog in ['bash', 'sh']:
            if '-c' in words:
                ix = words.index('-c')
                if prog.startswith('python') and ix + 1 < len(words):
                    py_sources.append(words[ix + 1])
                elif ix + 1 < len(words) and any(s in words[ix + 1] for s in ['run.py', '.py', '.sh']):
                    issue(task, 'nested_shell_command', 'sh/bash -c 内含脚本路径，未递归推断运行目标。', action)
            else:
                args = [w for w in words[1:] if not w.startswith('-')]
                if args:
                    run_paths.append(args[0])
        else:
            run_paths.append(words[0])
        for path in run_paths:
            normalized = posixpath.normpath(posixpath.join(cwd, path))
            if normalized in previous_scripts:
                rules.add('b'); evidence.append({'rule': 'b', 'path': path,
                                                'previous_write_events': list(previous_scripts[normalized])})
            if posixpath.basename(path) == 'run.py':
                rules.add('c'); evidence.append({'rule': 'c', 'path': path})
    for body in bodies:
        if not body['terminated']:
            issue(task, 'unterminated_heredoc',
                  {'delimiter':body['delimiter'], 'handling':'按Bash原有EOF语义读取正文，未补分隔符；原命令及可见警告保持原样。'}, action, False)
        if re.search(r'\bpython(?:\d+(?:\.\d+)*)?\s+(?:-\s*)?<<', body['header']):
            py_sources.append(body['body'])
        elif re.search(r'>+\s*[^\s]+\.py\b', body['header']):
            try:
                candidate, _ = python_sql_write(body['body'])
                if candidate:
                    issue(task, 'saved_python_sql_writer',
                          '命令把含 .sql 路径和 write_text/open(w/a) 的 Python 写入脚本文件；'
                          '规则 a 是否也涵盖尚未运行的脚本正文未规定。当前只记录候选 a，未按 a 触发。', action)
            except SyntaxError:
                # Appended script fragments are often not standalone modules.
                if '.sql' in body['body'] and re.search(r'write_text|open\(', body['body']):
                    issue(task, 'saved_python_fragment',
                          '写入 .py 的片段含 .sql 和写文件字样，但不是独立合法模块；规则 a 是否涵盖待定。', action)
    for code in py_sources:
        try:
            yes, ev = python_sql_write(code)
        except SyntaxError as e:
            issue(task, 'python_parse_error', str(e), action)
            continue
        if yes:
            rules.add('a'); evidence.append({'rule': 'a', 'operation': 'inline_python', 'writes': ev})
    if re.search(r'\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW)\b', command, re.I):
        rules.add('d'); evidence.append({'rule': 'd', 'operation': 'literal_case_insensitive_match'})
    return sorted(rules), evidence, newly_written


def contract_sections(task, path):
    data = source(path); text = data.decode()
    try:
        yaml.compose(text)
    except yaml.YAMLError as e:
        issue(task, 'invalid_contract_yaml',
              '原契约不能被严格YAML解析；未修复，按原文缩进定位表节。' + str(e), blocking=False)
    # The source format uses four-space model list items and deeper columns.
    # Slice original characters, never dump/reformat YAML or repair bad escapes.
    headers = list(re.finditer(r'^    - name: (?P<name>[^\r\n]+)', text, re.M))
    result = []
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    for h in headers:
        name = yaml.safe_load(h['name'])
        start = h.start()
        first_line = text.count('\n', 0, start)
        end = len(text)
        for n in range(first_line + 1, len(lines)):
            line = lines[n]
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            indent = len(line) - len(line.lstrip(' '))
            if indent < 4 or (indent == 4 and line.lstrip().startswith('- ')):
                end = offsets[n]
                break
        parents = list(re.finditer(r'^  (\w+):', text[:start], re.M))
        assert parents, task
        layer = parents[-1][1]
        payload = text[start:end]
        result.append({'id': name, 'name': name, 'layer': layer,
                       'source_path': str(path), 'line_start': first_line+1,
                       'line_end': text.count('\n', 0, end),
                       'ref': ref_file(path, payload, start, end)})
    if not result:
        issue(task, 'no_contract_sections', str(path))
    names = [s['id'] for s in result]
    duplicate_names = [name for name, n in Counter(names).items() if n > 1]
    if duplicate_names:
        issue(task, 'duplicate_contract_names',
              {'names': duplicate_names, 'handling': '同名原文节均保留，用行号区分，不择一、不修复。'}, blocking=False)
        for s in result:
            if s['name'] in duplicate_names:
                s['id'] = s['name'] + '@L' + str(s['line_start'])
    return result, text


def da_index(task, run_dir, prompt):
    dbs = sorted(run_dir.glob('*_start.duckdb'))
    assert len(dbs) == 1, (task, dbs)
    db = dbs[0]
    before = sha(source(db))
    initial = DA_INITIAL / f'dacomp-de-{task}' / db.name
    assert before == sha(source(initial)), task
    query = ('SELECT table_catalog, table_schema, table_name, column_name, ordinal_position '
             'FROM information_schema.columns '
             'ORDER BY table_catalog, table_schema, table_name, ordinal_position')
    with duckdb.connect(str(db), read_only=True) as c:
        rows = c.execute(query).fetchall()
    assert sha(source(db)) == before
    groups = defaultdict(list)
    for cat, schema, table, column, ordinal in rows:
        groups[(cat, schema, table)].append(column)
    result = {'database_path': str(db), 'initial_copy_path': str(initial), 'sha256': before,
              'initial_copy_sha256_identical': True, 'query': query,
              'tables': [{'catalog': k[0], 'schema': k[1], 'table': k[2], 'columns': v}
                         for k, v in groups.items()]}
    text = f'数据库：{db}\n'
    text += ''.join(json.dumps({'table': f'{k[1]}.{k[2]}', 'columns': v}, ensure_ascii=False) + '\n'
                    for k, v in groups.items())
    return result, text


def fixed(out, prompt, index_text, index_details):
    write(out / 'prompt.txt', prompt)
    write(out / 'material_index.txt', index_text)
    dump(out / 'material_index.json', index_details)
    return {'prompt': ref_file(out / 'prompt.txt', prompt),
            'index': ref_file(out / 'material_index.txt', index_text)}


def build_da(task, temp):
    out = BASE / task; out.mkdir()
    folder = temp / 'da/dacomp_deimpl_prev/runs/20261025_de_official_batch_01' / task
    paths = list(folder.glob('agent/.events/sessions/*/events/*.json'))
    events = sorted([(p, json.loads(p.read_text())) for p in paths], key=lambda pe: pe[1]['id'])
    assert len(set(e['id'] for p, e in events)) == len(events)
    by_id = {e['id']: (p, e) for p, e in events}
    prompt = by_id[1][1]['message']
    run_dir = DA_RUN / task / 'agent' / f'dacomp-de-{task}'
    sections, contract = contract_sections(task, DA_INITIAL / f'dacomp-de-{task}' / 'docs/data_contract.yaml')
    assert contract in prompt
    assert contract == source(run_dir / 'docs/data_contract.yaml').decode()
    index_details, index_text = da_index(task, run_dir, prompt)
    m = {'task': task, 'benchmark': 'DAComp', 'fixed': fixed(out, prompt, index_text, index_details),
         'prompt_source': {'archive': 'traces/dacomp_deimpl_prev.tar.gz',
                           'member': str(by_id[1][0].relative_to(temp / 'da')), 'field': ['message']},
         'full_contract_is_literal_substring_of_prompt': True,
         'sections': sections, 'actions': [], 'calls': [], 'suspicious_actions': [],
         'non_shell_events': [], 'uncalled_tail_action_ids': []}
    segment, scripts, since = [], {}, 0
    for p, e in events:
        if e['source'] != 'agent' or 'action' not in e:
            continue
        if e['action'] == 'finish':
            m['uncalled_tail_action_ids'] = list(segment)
            m['calls'].append({'task': task, 'call': len(m['calls'])+1, 'kind': 'final',
                               'rules': ['f'], 'position': e['id'], 'action_ids': [],
                               'action_range': None, 'section_ids': [], 'sections': [],
                               'assumptions': {'runtime': True, 'scope': 'all_previous_hypotheses'},
                               'pending_decision_ids': []})
            continue
        if e['action'] != 'run':
            m['non_shell_events'].append({'id': e['id'], 'action': e['action']})
            continue
        command = e['args']['command']
        member = str(p.relative_to(temp / 'da'))
        a = {'id': e['id'], 'label': f"event {e['id']}",
             'command': ref_event('traces/dacomp_deimpl_prev.tar.gz', member, ['args', 'command'], e)}
        next_event = by_id.get(e['id'] + 1)
        if next_event and next_event[1].get('observation') in ['run','error'] and next_event[1].get('cause') == e['id']:
            rp, result = next_event
            a['feedback'] = ref_event('traces/dacomp_deimpl_prev.tar.gz', str(rp.relative_to(temp / 'da')),
                                      ['content'], result)
            a['result_event'] = result['id']
        else:
            a['feedback'] = None
            issue(task, 'missing_adjacent_result', '未发现紧跟动作且 cause 匹配的 run 结果。', e['id'])
        try:
            rules, evidence, new_scripts = classify(task, e['id'], command, scripts, str(run_dir))
        except Exception as ex:
            issue(task, 'shell_parse_error', f'{type(ex).__name__}: {ex}', e['id'])
            rules = ['d'] if re.search(r'\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW)\b', command, re.I) else []
            evidence, new_scripts = [], set()
        for path in new_scripts:
            scripts.setdefault(path, []).append(e['id'])
        a.update(rules_a_to_d=rules, trigger_evidence=evidence,
                 scripts_written_literal_paths=sorted(new_scripts))
        m['actions'].append(a)
        segment.append(a['id']); since += 1
        if not rules and any(x in command for x in ['sql/', '.sql', 'open(', 'write_text']):
            m['suspicious_actions'].append({'task': task, 'event': e['id'], 'command_first_300': command[:300]})
        if not rules and since == 5:
            rules = ['e']
        if rules:
            commands_text = [A.text_ref(x['command']) for x in m['actions'] if x['id'] in segment]
            used = [s for s in sections if any(s['name'] in c for c in commands_text)]
            m['calls'].append({'task': task, 'call': len(m['calls'])+1, 'kind': 'regular',
                               'rules': rules, 'position': e['id'], 'action_ids': list(segment),
                               'action_range': [segment[0], segment[-1]],
                               'section_ids': [s['id'] for s in used],
                               'sections': [{k: s[k] for k in ['id', 'source_path', 'line_start', 'line_end']} for s in used],
                               'assumptions': {'runtime': True, 'initial_tokens': 0}, 'pending_decision_ids': []})
            segment, since = [], 0
    if m['uncalled_tail_action_ids']:
        issue(task, 'uncalled_tail',
              {'events': m['uncalled_tail_action_ids'],
               'problem': 'finish 前不足5步且未触发 a–d，交卷规则只记录位置；'
                          '做法二“整条轨迹”与“做法一用过的信息合并”不等价。两种文本均可拼装，未替 Claude 选择。'})
    assert sum(c['kind']=='final' for c in m['calls']) == 1
    return m


@functools.lru_cache(maxsize=None)
def kb_sections(domain):
    path = ROOT / f'records/031_kramabench_docs/{domain}.md'
    text = source(path).decode()
    starts = list(re.finditer(r'^## (?:文件：|本地仓库说明文档：)`([^`]+)`.*$', text, re.M))
    sections = []
    for i, h in enumerate(starts):
        start = h.start(); end = starts[i+1].start() if i+1 < len(starts) else len(text)
        sections.append({'id': h[1], 'name': h[1], 'source_path': str(path.relative_to(ROOT)),
                         'line_start': text.count('\n', 0, start)+1,
                         'line_end': text.count('\n', 0, end),
                         'ref': ref_file(path, text[start:end], start, end)})
    return sections


def kb_index(task):
    domain = task.split('-')[0]
    folder = KB_DATA / domain / 'input'
    groups = defaultdict(list)
    for p in sorted(folder.rglob('*')):
        if p.is_file():
            groups[p.parent].append(p)
    rows = []
    for parent, files in sorted(groups.items()):
        selected = files[:1] if len(files)>50 else files
        for p in selected:
            row = {'file': str(p.relative_to(folder))}
            if len(files)>50:
                row.update(directory=str(parent.relative_to(folder)), file_count=len(files),
                           first_sorted_filename=p.name)
            if p.suffix.lower() == '.csv':
                # Read only the first physical line; do not search data rows for headers.
                with p.open('rb') as f:
                    raw = f.readline()
                encoding = 'utf-8'
                try:
                    first_line = raw.decode(encoding)
                except UnicodeDecodeError:
                    encoding = 'cp1252'
                    first_line = raw.decode(encoding)
                row.update(csv_first_physical_line=first_line,
                           csv_first_line_fields=next(csv.reader([first_line])), encoding=encoding,
                           first_line_sha256=sha(raw), source_path=str(p))
                if encoding != 'utf-8':
                    issue(task, 'csv_encoding', f'{p}: UTF-8 失败；沿用031 CP1252回退，作者编码未独立核实。', blocking=False)
            elif p.suffix.lower() in ['.xlsx', '.xlsm']:
                # workbook.xml contains sheet metadata only; never read sheet cells.
                with zipfile.ZipFile(p) as z:
                    data = z.read('xl/workbook.xml')
                ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
                row.update(sheets=[s.attrib['name'] for s in ET.fromstring(data).find(ns+'sheets')],
                           workbook_xml_sha256=sha(data), source_path=str(p))
            else:
                row['metadata'] = '仅文件名；本任务只规定 CSV 列名或 Excel 工作表名。'
                if len(files)>50:
                    issue(task, 'group_first_non_csv_excel',
                          {'file':str(p), 'files':len(files),
                           'problem':'超过50文件目录的首文件不是CSV/Excel；规则未定义列名的获取方法，当前仅记录文件名。'})
            rows.append(row)
    # First-row interpretation cannot be repaired by inspecting business data.
    csv_rows = [r['file'] for r in rows if 'csv_first_physical_line' in r]
    if csv_rows:
        issue(task, 'csv_header_row',
              {'files': csv_rows, 'problem': '仅机械读取CSV首个物理行，未判断该行是否真正表头。'
               '含说明前言或无表头时，规则未指定如何定位列名；未向下查询数据。'
               '当前token是原样首行候选输入，待Claude确认。'})
    text = f'领域数据目录：{folder}\n'
    for r in rows:
        view = {k: v for k, v in r.items() if k in ['file','directory','file_count','first_sorted_filename',
                                                    'csv_first_physical_line','sheets']}
        text += json.dumps(view, ensure_ascii=False) + '\n'
    return {'input_directory': str(folder), 'total_files': sum(map(len, groups.values())),
            'listed_rows': rows, 'directory_groups': [{'directory': str(p.relative_to(folder)), 'files': len(v)}
                                                     for p, v in sorted(groups.items())]}, text


def build_kb(task, temp, package_index):
    out = BASE / task; out.mkdir()
    pi = package_index[task]
    meta = json.loads(source(ROOT / pi['meta']))
    prompt = meta['prompt_values']['query']
    index_details, index_text = kb_index(task)
    msg_member, ex_member = pi['messages_member'], pi['steps_member']
    msgs = [json.loads(line) for line in (temp / 'kb' / msg_member).read_text().splitlines()]
    exs = [(i, json.loads(line)) for i, line in enumerate((temp / 'kb' / ex_member).read_text().splitlines(), 1)]
    exs = [(i, e) for i, e in exs if e.get('kind') == 'execution']
    resp = [(i, d) for i, d in enumerate(msgs, 1) if d['direction'] == 'response' and 'message' in d]
    assert len(resp) == meta['model_calls']
    by_tool = {e['tool_call_id']: (i, e) for i, e in exs}
    feedback = {}
    for i, d in enumerate(msgs, 1):
        if d['direction'] == 'request':
            for j, h in enumerate(d['messages']):
                if h.get('role') == 'tool':
                    tid = h['tool_call_id']
                    if tid in feedback:
                        assert feedback[tid][2]['content'] == h['content']
                    else:
                        feedback[tid] = (i, j, h)
    sections = kb_sections(task.split('-')[0])
    m = {'task': task, 'benchmark': 'KramaBench', 'fixed': fixed(out, prompt, index_text, index_details),
         'prompt_source': {'path': pi['meta'], 'field': ['prompt_values', 'query']},
         'sections': sections, 'actions': [], 'calls': [], 'suspicious_actions': [],
         'uncalled_tail_action_ids': [], 'responses_without_execution': []}
    matched_resp = set()
    for lineno, e in exs:
        matching = [(li, r) for li, r in resp if r['call'] == e['model_call']
                    and any(tc['id'] == e['tool_call_id'] for tc in r['message'].get('tool_calls', []))]
        assert len(matching) == 1
        li, response = matching[0]; matched_resp.add(li)
        msg = response['message']
        a = {'id': e['step'], 'label': f"执行 step {e['step']} / model call {e['model_call']}",
             'execution_line': lineno, 'response_line': li,
             'code': ref_event('traces/kramabench_luna_baseline.tar.gz', ex_member, ['code'], e, lineno),
             'reasoning': [], 'files_read': e['files_read'], 'is_final_answer': e['is_final_answer']}
        assert any(tc['function']['name'] == 'run_python' and json.loads(tc['function']['arguments'])['code'] == e['code']
                   for tc in msg['tool_calls'])
        readable = []
        if msg.get('reasoning'):
            readable.append((['message','reasoning'], msg['reasoning']))
        for ri, rd in enumerate(msg.get('reasoning_details') or []):
            if rd['type'] == 'reasoning.encrypted':
                continue
            for key in ['summary', 'text']:
                if rd.get(key):
                    readable.append((['message', 'reasoning_details', ri, key], rd[key]))
        seen = set()
        for field, text in readable:
            if text not in seen:
                seen.add(text)
                a['reasoning'].append(ref_event('traces/kramabench_luna_baseline.tar.gz', msg_member,
                                                field, response, li))
        if msg.get('content'):
            a['content'] = ref_event('traces/kramabench_luna_baseline.tar.gz', msg_member,
                                     ['message','content'], response, li)
        if e['tool_call_id'] in feedback:
            fl, hi, h = feedback[e['tool_call_id']]
            content = h['content']; full = e['full_observation']
            expected = full if len(full)<=4000 else full[:1986]+'\n... [output truncated] ...\n'+full[-1986:]
            assert content == expected
            a['feedback'] = ref_event('traces/kramabench_luna_baseline.tar.gz', msg_member,
                                     ['messages', hi, 'content'], msgs[fl-1], fl)
            a['feedback_truncated'] = len(full)>4000
        else:
            a['feedback'] = None
            issue(task, 'missing_final_feedback',
                  '末次执行无后续request role=tool反馈；沿用028仅标明缺失，不补本地输出。', e['step'], False)
        used = []
        for raw in e['files_read']:
            matches = []
            for s in sections:
                parent = s['name']
                prefix = task.split('-')[0]+'/input/'
                inside = parent[len(prefix):] if parent.startswith(prefix) else None
                aliases = ({parent} if inside is None else {
                    'data/'+inside,
                    str(Path('/home/katherine/dac/benchmarks/KramaBench/data') / prefix / inside),
                    str(KB_DATA / prefix / inside), 'data/kramabench/data/'+prefix+inside})
                if raw in aliases:
                    matches.append(s)
            if not matches:
                issue(task, 'unmapped_files_read', {'raw_path': raw, 'searched': f'records/031_kramabench_docs/{task.split("-")[0]}.md'}, e['step'])
            for s in matches:
                if s['id'] not in [v['id'] for v in used]:
                    used.append(s)
        m['actions'].append(a)
        m['calls'].append({'task': task, 'call': len(m['calls'])+1, 'kind': 'regular',
                           'rules': ['execution_step'], 'position': e['step'], 'action_ids': [e['step']],
                           'action_range': [e['step'],e['step']], 'section_ids': [s['id'] for s in used],
                           'sections': [{k: s[k] for k in ['id','source_path','line_start','line_end']} for s in used],
                           'assumptions': {'runtime': True, 'initial_tokens': 0}, 'pending_decision_ids': []})
        if e['is_final_answer']:
            m['calls'].append({'task': task, 'call': len(m['calls'])+1, 'kind': 'final',
                               'rules': ['f'], 'position': e['step'], 'action_ids': [], 'action_range': None,
                               'section_ids': [], 'sections': [],
                               'assumptions': {'runtime': True, 'scope': 'all_previous_hypotheses'},
                               'pending_decision_ids': []})
    for li, r in resp:
        if li not in matched_resp:
            m['responses_without_execution'].append({'line': li, 'call': r['call']})
            issue(task, 'response_without_execution', '无执行步骤的模型回复是否纳入轨迹未规定。', r['call'])
    assert sum(c['kind']=='final' for c in m['calls']) == 1
    return m


def main():
    start = json.loads((BASE / 'start_state.json').read_text())
    rows = list(csv.DictReader(source(ROOT / 'records/047_premise_sentences_draft.csv').decode('utf-8-sig').splitlines()))
    da = sorted({re.match(r'impl-\d+',r['对象编号'])[0] for r in rows if r['benchmark']=='DAComp'})
    kb = sorted({r['对象编号'] for r in rows if r['benchmark']=='KramaBench'})
    assert len(da)==20 and len(kb)==9, (len(da),len(kb))
    temp = Path(start['temp_dir'])
    if not temp.exists():
        temp = Path(tempfile.mkdtemp(prefix='assumption-ledger-048-'))
        for name, sub in [('dacomp_deimpl_prev', 'da'), ('kramabench_luna_baseline', 'kb')]:
            with tarfile.open(ROOT / f'traces/{name}.tar.gz') as t:
                ms = [m for m in t.getmembers() if m.isfile() and (sub=='kb' or '20261025_de_official_batch_01/' in m.name)]
                t.extractall(temp / sub, members=ms, filter='data')
    for name in ['dacomp_deimpl_prev', 'kramabench_luna_baseline']:
        source(ROOT / f'traces/{name}.tar.gz')
    pi = json.loads(source(ROOT / 'records/028_kramabench_package_index.json'))
    manifests = []
    for task in da:
        manifests.append(build_da(task, temp))
    for task in kb:
        manifests.append(build_kb(task, temp, pi))
    enc = tiktoken.get_encoding('o200k_base')
    def tokens(text):
        return len(enc.encode(text, disallowed_special=()))
    counts, task_stats, all_regular = [], [], []
    for m in manifests:
        task = m['task']; calls = m['calls']
        blockers = [i['id'] for i in ISSUES if i['task']==task and i['blocking']]
        segmentation = [i['id'] for i in ISSUES if i['task']==task and i['blocking']
                        and i['kind'] not in ['uncalled_tail','csv_header_row','unmapped_files_read']]
        action_ids = [a for c in calls if c['kind']=='regular' for a in c['action_ids']]
        assert len(set(action_ids))==len(action_ids)
        used_sections = list(dict.fromkeys(s for c in calls if c['kind']=='regular' for s in c['section_ids']))
        m['method2'] = {'task': task, 'action_ids': action_ids, 'section_ids': used_sections,
                        'fixed_parts': m['fixed'], 'pending_decision_ids': blockers,
                        'definition': '做法一普通叫起实际用到的第1/2/3/5部分；题面、索引各一次，契约/文档按section id去重。',
                        'uncalled_tail_action_ids': m['uncalled_tail_action_ids']}
        vals = []
        for c in calls:
            if c['kind']=='final':
                counts.append({'benchmark': m['benchmark'], 'task': task, 'method': 'method1_final',
                               'call': c['call'], 'rules': '|'.join(c['rules']),
                               'part1_tokens':'','part2_tokens':'','part3_tokens':'','part5_tokens':'',
                               'tokens':'','payload_tokens':'', 'status':'runtime_only', 'pending_decision_ids':''})
                continue
            c['pending_decision_ids'] = [i['id'] for i in ISSUES if i['task']==task and i['blocking'] and (
                i['id'] in segmentation or i['kind']=='csv_header_row' or
                (i['kind']=='unmapped_files_read' and i['action'] in c['action_ids']))]
            p = A.parts(m, c['action_ids'], c['section_ids'])
            text = A.render_parts(p)
            n = tokens(text); vals.append(n); all_regular.append(n)
            counts.append({'benchmark': m['benchmark'], 'task': task, 'method': 'method1',
                           'call': c['call'], 'rules': '|'.join(c['rules']),
                           **{f'part{k}_tokens': tokens(p[k]) for k in ['1','2','3','5']},
                           'tokens': n, 'payload_tokens': tokens(''.join(p[k] for k in ['1','2','3','5'])),
                           'status': 'pending_decisions' if c['pending_decision_ids'] else 'ready',
                           'pending_decision_ids': '|'.join(c['pending_decision_ids'])})
        p = A.parts(m, action_ids, used_sections)
        n2 = tokens(A.render_parts(p))
        counts.append({'benchmark': m['benchmark'], 'task': task, 'method': 'method2', 'call':'', 'rules':'',
                       **{f'part{k}_tokens': tokens(p[k]) for k in ['1','2','3','5']}, 'tokens':n2,
                       'payload_tokens': tokens(''.join(p[k] for k in ['1','2','3','5'])),
                       'status':'pending_decisions' if blockers else 'ready',
                       'pending_decision_ids':'|'.join(blockers)})
        rule_counts = Counter(r for c in calls for r in c['rules'])
        task_stats.append({'task':task, 'benchmark':m['benchmark'], 'actions':len(m['actions']),
                           'calls':len(calls), 'regular_calls':len(vals), 'final_calls':sum(c['kind']=='final' for c in calls),
                           'rule_counts':dict(rule_counts), 'method1_median':statistics.median(vals),
                           'method1_max':max(vals), 'method1_sum':sum(vals), 'method2_tokens':n2,
                           'method2_full_trace_candidate_tokens':tokens(A.render_parts(A.parts(m,[a['id'] for a in m['actions']],used_sections))),
                           'uncalled_tail_action_ids':m['uncalled_tail_action_ids'], 'blocking_decisions':blockers})
        dump(BASE/task/'manifest.json', m)
        dump(BASE/task/'method2_components.json', m['method2'])
        with (BASE/task/'calls.jsonl').open('x',encoding='utf-8') as f:
            for c in calls:
                f.write(json.dumps(c,ensure_ascii=False)+'\n')
    write_csv(ROOT / 'records/048_small_exp_token_counts.csv', counts)
    suspicious = [s for m in manifests for s in m['suspicious_actions']]
    write_csv(BASE / 'suspicious_actions.csv', suspicious)
    dump(BASE / 'decisions_for_claude.json', ISSUES)
    dump(BASE / 'source_hashes.json', SOURCES)
    summary = {'number':48, 'start_commit':start['start_commit'], 'counts_are_provisional':any(i['blocking'] for i in ISSUES),
               'task_count':len(manifests), 'task_benchmarks':dict(Counter(m['benchmark'] for m in manifests)),
               'ordinary_calls':len(all_regular), 'final_calls':sum(c['kind']=='final' for m in manifests for c in m['calls']),
               'method1_median':statistics.median(all_regular), 'method1_max':max(all_regular), 'method1_sum':sum(all_regular),
               'method2_sum':sum(s['method2_tokens'] for s in task_stats),
               'over_272000':[s['task'] for s in task_stats if s['method2_tokens']>272000],
               'over_1050000':[s['task'] for s in task_stats if s['method2_tokens']>1050000],
               'suspicious_actions':len(suspicious), 'issues_by_kind':dict(Counter(i['kind'] for i in ISSUES)),
               'tasks':task_stats, 'dependencies':{name:importlib.metadata.version(name) for name in ['tiktoken','duckdb','PyYAML','bashlex']},
               'python':sys.version, 'encoding':'o200k_base', 'format':'048 assembler render_parts; headers/separators included, assumptions omitted',
               'excluded_from_counts':['system/prompt instructions not yet written','chat/API envelope','prior hypotheses','final re-ranking hypotheses','model outputs/reasoning','judge inputs/outputs'],
               'temp_dir':str(temp)}
    dump(BASE / 'summary.json', summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='tasks'},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
