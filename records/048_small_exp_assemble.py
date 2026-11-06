"""Read-only, model-free material assembler. No agent code is executed.

Examples:
  python3 records/048_small_exp_assemble.py impl-001 1
  python3 records/048_small_exp_assemble.py impl-001 --method2
  python3 records/048_small_exp_assemble.py impl-001 1 --assumptions-file /tmp/prior.txt

Calls with unresolved segmentation/input decisions require --allow-pending. This
flag exposes recorded material for review; it does not resolve those decisions.
Final calls contain runtime hypotheses only, so require --assumptions-file.
"""
import argparse
import functools
import hashlib
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'records/048_small_exp_inputs'


def sha(data):
    return hashlib.sha256(data).hexdigest()


@functools.lru_cache(maxsize=None)
def read_bytes(path):
    p = Path(path)
    return (p if p.is_absolute() else ROOT / p).read_bytes()


@functools.lru_cache(maxsize=None)
def archive_text_members(archive):
    """One sequential decompression; cache only events/messages/executions."""
    with tarfile.open(ROOT / archive, 'r:gz') as tar:
        return {m.name: tar.extractfile(m).read() for m in tar if m.isfile() and
                ('/events/' in m.name and m.name.endswith('.json') or
                 m.name.endswith(('/messages.jsonl', '/steps.jsonl')))}


def archive_member(archive, member):
    return archive_text_members(archive)[member]


def text_ref(ref):
    """Read and check exactly the referenced text; all offsets are characters."""
    data = (archive_member(ref['archive'], ref['member']) if 'archive' in ref
            else read_bytes(ref['path']))
    if 'source_sha256' in ref and sha(data) != ref['source_sha256']:
        raise ValueError(f'Source changed: {ref}')
    text = data.decode('utf-8')
    if 'line' in ref:
        obj = json.loads(text.splitlines()[ref['line'] - 1])
        for k in ref.get('field', []):
            obj = obj[k]
        text = obj
    elif 'field' in ref:
        obj = json.loads(text)
        for k in ref['field']:
            obj = obj[k]
        text = obj
    if 'start' in ref:
        text = text[ref['start']:ref['end']]
    if not isinstance(text, str):
        raise TypeError(f'Not a verbatim string: {ref}')
    if 'text_sha256' in ref and sha(text.encode()) != ref['text_sha256']:
        raise ValueError(f'Text changed: {ref}')
    return text


def manifest(task):
    return json.loads((BASE / task / 'manifest.json').read_text())


def wrap(title, text):
    return f'## {title}\n\n{text}\n\n'


def render_actions(actions):
    pieces = []
    for a in actions:
        pieces.append(f"### {a['label']}\n\n")
        if 'command' in a:
            pieces.append(wrap('命令原文', text_ref(a['command'])))
        if 'code' in a:
            pieces.append(wrap('代码原文', text_ref(a['code'])))
        for r in a.get('reasoning', []):
            pieces.append(wrap('思考摘要原文', text_ref(r)))
        if a.get('content'):
            pieces.append(wrap('模型可读输出原文', text_ref(a['content'])))
        if a.get('feedback'):
            pieces.append(wrap('agent 实际看到的执行结果', text_ref(a['feedback'])))
        else:
            pieces.append('执行结果：消息历史中未发现 agent 实际看到的对应反馈；未以本地完整输出补写。\n\n')
    return ''.join(pieces)


def parts(m, action_ids, section_ids):
    lookup = {a['id']: a for a in m['actions']}
    sec = {s['id']: s for s in m['sections']}
    return {
        '1': render_actions([lookup[i] for i in action_ids]),
        '2': text_ref(m['fixed']['prompt']),
        '3': ''.join(wrap(sid, text_ref(sec[sid]['ref'])) for sid in section_ids),
        '5': text_ref(m['fixed']['index']),
    }


def render_parts(p, assumptions=None):
    titles = {'1': '1. 这一段 agent 做了什么', '2': '2. 题面原文',
              '3': '3. 相关要求和材料原文', '5': '5. 全部材料的索引'}
    text = ''.join(wrap(titles[k], p[k]) for k in ['1', '2', '3'])
    if assumptions is not None:
        text += wrap('4. 之前已经找出的假设', assumptions)
    return text + wrap(titles['5'], p['5'])


def assemble(task, call=None, method2=False, assumptions=None, allow_pending=False,
             method2_full_trace=False):
    m = manifest(task)
    if method2:
        row = m['method2']
        if row['pending_decision_ids'] and not allow_pending:
            raise ValueError('Unresolved input decisions: ' + ', '.join(row['pending_decision_ids']))
        ids = ([a['id'] for a in m['actions']] if method2_full_trace else row['action_ids'])
        return render_parts(parts(m, ids, row['section_ids']))
    row = next(r for r in m['calls'] if r['call'] == call)
    if row['kind'] == 'final':
        if assumptions is None:
            raise ValueError('Final-call input is runtime-only; provide the accumulated assumptions.')
        return wrap('交卷：这道题前面列过的全部假设', assumptions)
    if row['pending_decision_ids'] and not allow_pending:
        raise ValueError('Unresolved input decisions: ' + ', '.join(row['pending_decision_ids']))
    return render_parts(parts(m, row['action_ids'], row['section_ids']), assumptions)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('task')
    p.add_argument('call', type=int, nargs='?')
    p.add_argument('--method2', action='store_true')
    p.add_argument('--allow-pending', action='store_true')
    p.add_argument('--method2-full-trace', action='store_true',
                   help='Review-only alternative for uncalled tail actions; never resolves a decision.')
    p.add_argument('--assumptions-file', type=Path)
    args = p.parse_args()
    if not args.method2 and args.call is None:
        p.error('Provide a call number or --method2.')
    if args.method2_full_trace and not args.method2:
        p.error('--method2-full-trace requires --method2.')
    prior = args.assumptions_file.read_text() if args.assumptions_file else None
    try:
        sys.stdout.write(assemble(args.task, args.call, args.method2, prior,
                                  args.allow_pending, args.method2_full_trace))
    except (ValueError, StopIteration) as e:
        p.exit(2, str(e) + '\n')


if __name__ == '__main__':
    main()
