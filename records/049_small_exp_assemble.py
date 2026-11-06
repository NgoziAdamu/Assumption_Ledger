"""Model-free runtime assembler for the finalized 049 input rules.

python3 records/049_small_exp_assemble.py impl-001 1
python3 records/049_small_exp_assemble.py impl-001 --final-rank --ledger-json /tmp/ledger.json
python3 records/049_small_exp_assemble.py impl-001 --method2

Ledger: JSON array; each entry preserves id, call (or 第几次叫起), and all
review output fields. No entries are filtered or inferred. Empty = (none).
"""
import argparse
import functools
import hashlib
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'records/049_small_exp_inputs'
PROMPTS = ROOT / 'records/049_prompts'


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
        if a.get('kind') == 'response_without_execution':
            pieces.append('本次回复没有执行步骤。\n\n')
            continue
        if a.get('feedback'):
            pieces.append(wrap('agent 实际看到的执行结果', text_ref(a['feedback'])))
        else:
            pieces.append('执行结果：消息历史中未发现 agent 实际看到的对应反馈；未以本地完整输出补写。\n\n')
    return ''.join(pieces)


REVIEW_FIELDS = {'statement', 'about', 'target', 'evidence_of_dependence',
                 'alternative', 'importance', 'reason', 'updates'}


def ledger_text(ledger=None):
    if ledger is None or ledger == []:
        return '(none)'
    if not isinstance(ledger, list):
        raise ValueError('Ledger JSON must be an array.')
    for row in ledger:
        if not isinstance(row, dict) or 'id' not in row:
            raise ValueError('Every ledger entry must be an object with id.')
        if not ('call' in row or '第几次叫起' in row):
            raise ValueError('Every ledger entry must contain call (or 第几次叫起).')
        if not REVIEW_FIELDS <= set(row):
            raise ValueError('Missing review output fields: ' + ', '.join(sorted(REVIEW_FIELDS - set(row))))
    return json.dumps(ledger, ensure_ascii=False, indent=2)


def parts(m, action_ids, section_ids):
    lookup = {a['id']: a for a in m['actions']}
    sec = {s['id']: s for s in m['sections']}
    return {
        'task': text_ref(m['fixed']['prompt']),
        'material_index': text_ref(m['fixed']['index']),
        'spec_sections': ''.join(wrap(sid, text_ref(sec[sid]['ref'])) for sid in section_ids),
        'steps': render_actions([lookup[i] for i in action_ids]),
    }


def fill_template(name, values):
    template = (PROMPTS / name).read_text(encoding='utf-8')
    expected = json.loads((BASE / 'prompt_inventory.json').read_text())[name]['sha256']
    if sha(template.encode()) != expected:
        raise ValueError('Prompt template changed: ' + name)
    # format_map runs only on the template. Braces inside data remain literal.
    return template.format_map(values)


def assemble(task, call=None, method2=False, final_rank=False, ledger=None):
    if method2 and final_rank:
        raise ValueError('Choose one mode: method2 or final-rank.')
    m = manifest(task)
    if final_rank:
        return fill_template('method1_final_rank.txt', {
            'task': text_ref(m['fixed']['prompt']), 'ledger': ledger_text(ledger)})
    if method2:
        row = m['method2']
    else:
        matches = [r for r in m['calls'] if r['call'] == call]
        if not matches:
            raise ValueError('Unknown call number: ' + str(call))
        row = matches[0]
        if row['kind'] == 'final':
            raise ValueError('This call is final ranking; use --final-rank.')
    if row['pending_decision_ids']:
        raise ValueError('Unresolved rules: ' + ', '.join(row['pending_decision_ids']))
    values = parts(m, row['action_ids'], row['section_ids'])
    if method2:
        values['trajectory'] = values.pop('steps')
        return fill_template('method2_review.txt', values)
    values['ledger'] = ledger_text(ledger)
    return fill_template('method1_review.txt', values)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('task')
    p.add_argument('call', type=int, nargs='?')
    modes = p.add_mutually_exclusive_group()
    modes.add_argument('--method2', action='store_true')
    modes.add_argument('--final-rank', action='store_true')
    p.add_argument('--ledger-json', '--ledger-file', dest='ledger_json', type=Path)
    args = p.parse_args()
    if not (args.method2 or args.final_rank) and args.call is None:
        p.error('Provide a call number, --method2, or --final-rank.')
    if (args.method2 or args.final_rank) and args.call is not None:
        p.error('A call number is only used for an ordinary review.')
    if args.method2 and args.ledger_json:
        p.error('Method2 does not use a ledger.')
    try:
        ledger = json.loads(args.ledger_json.read_text(encoding='utf-8')) if args.ledger_json else None
        if args.ledger_json and not isinstance(ledger, list):
            raise ValueError('Ledger JSON file must contain an array.')
        sys.stdout.write(assemble(args.task, args.call, args.method2, args.final_rank, ledger))
    except (ValueError, KeyError, FileNotFoundError) as e:
        p.exit(2, str(e) + '\n')


if __name__ == '__main__':
    main()
