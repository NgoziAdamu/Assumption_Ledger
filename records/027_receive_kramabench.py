"""Copy and inspect existing records only; never import or execute benchmark code."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import re
import shutil
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
OLD = Path('/home/katherine/dac')
BENCH = OLD / 'benchmarks/KramaBench'
DEST = ROOT / 'records/027_kramabench_source'
ARCHIVE = ROOT / 'traces/kramabench_luna_baseline.tar.gz'
DOMAINS = ['archeology', 'astronomy', 'biomedical', 'environment', 'legal', 'wildfire']

def digest(data):
    return hashlib.sha256(data).hexdigest()

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def git(*args, cwd=OLD):
    return subprocess.check_output(['git', '--no-optional-locks', '-C', str(cwd), *args], text=True)

# Do not emit potential credential values. Abort before copying if a value is found.
SECRET = re.compile(rb'(?<![A-Za-z0-9_-])(?:sk-(?:or-v1-|proj-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|Bearer\s+[A-Za-z0-9._-]{20,})')

def scan(data, name):
    if SECRET.search(data):
        raise RuntimeError('Potential credential in ' + name)

def character_parts(text, file_kind):
    """Partition raw JSONL characters, including repeats, quotes and escapes.

    Classify string-value token spans. All punctuation, keys, non-string values,
    whitespace and remaining value spans belong to other. No text is rewritten.
    """
    count = collections.Counter(model=0, code=0, output=0, other=0)
    decoder = json.JSONDecoder()
    for line in text.splitlines(keepends=True):
        def skip(i):
            while i < len(line) and line[i].isspace():
                i += 1
            return i

        def walk(i, category='other'):
            i = skip(i)
            if line[i] == '{':
                # Role determines the meaning of message.content in all copies.
                obj, _ = decoder.raw_decode(line, i)
                role = obj.get('role')
                i = skip(i + 1)
                while line[i] != '}':
                    key, i = decoder.raw_decode(line, i)
                    i = skip(i)
                    assert line[i] == ':'
                    child = category
                    if key == 'code' or (key == 'arguments' and obj.get('name') == 'run_python'):
                        child = 'code'
                    elif file_kind == 'steps' and key in {'stdout', 'stderr', 'error', 'display', 'traceback', 'full_observation'}:
                        child = 'output'
                    elif key == 'content' and role == 'tool':
                        child = 'output'
                    elif role == 'assistant' and key in {'content', 'refusal', 'reasoning', 'reasoning_details'}:
                        child = 'model'
                    i = skip(walk(i + 1, child))
                    if line[i] == ',':
                        i = skip(i + 1)
                    else:
                        assert line[i] == '}'
                return i + 1
            if line[i] == '[':
                i = skip(i + 1)
                while line[i] != ']':
                    i = skip(walk(i, category))
                    if line[i] == ',':
                        i = skip(i + 1)
                    else:
                        assert line[i] == ']'
                return i + 1
            value, end = decoder.raw_decode(line, i)
            if isinstance(value, str) and category != 'other':
                count[category] += end - i
            return end
        end = walk(0)
        assert not line[end:].strip()
    count['other'] = len(text) - count['model'] - count['code'] - count['output']
    assert count['other'] >= 0
    return count

def main():
    assert not DEST.exists(), 'Refuse to overwrite a previous receipt'
    assert not ARCHIVE.exists()
    assert not (ROOT / 'data/kramabench').exists()
    old_status = git('status', '--short')
    rows_all = list(csv.DictReader((OLD / 'notes/36_KramaBench基线逐题记录.csv').open()))
    rows = [r for r in rows_all if r['批次类型'] == '主基线']
    assert len(rows) == len({r['题号'] for r in rows}) == 104
    assert len(rows_all) - len(rows) == 15
    batches = sorted({r['批次'] for r in rows})
    manifest, pending, chars, exclusions = [], [], [], []
    planned = []

    def plan(src, target, group, archive=False):
        assert src.is_file() and not src.is_symlink(), src
        planned.append((src, str(target), group, archive))

    for name in ['36_KramaBench基线记录.md', '36_KramaBench基线逐题记录.csv']:
        plan(OLD / 'notes' / name, DEST / name, 'original_reports')
    for batch in batches:
        b = OLD / 'runs' / batch
        for name in ['batch_meta.json', 'summary.json', 'README.md', 'provider_capabilities.json']:
            plan(b / name, DEST / 'runs' / batch / name, 'batch_configuration_results')
        for f in sorted(b.rglob('*')):
            if f.is_symlink():
                exclusions.append({'source': str(f), 'reason': 'symlink_not_followed', 'target': str(f.readlink())})
            elif f.is_file() and (f.relative_to(b).parts[1:2] == ('artifacts',) or
                                  (len(f.relative_to(b).parts) > 2 and f.relative_to(b).parts[1] == 'workspace' and f.suffix == '.json')):
                exclusions.append({'source': str(f), 'bytes': f.stat().st_size, 'reason': 'data_snapshot_or_workspace_json'})

    for r in rows:
        src = Path(r['结果路径']).parent
        prefix = Path(r['批次']) / src.name
        plan(src / 'meta.json', DEST / 'runs' / prefix / 'meta.json', 'per_task_meta')
        for name in ['messages.jsonl', 'steps.jsonl', 'graph.json']:
            plan(src / name, prefix / name, name, True)
        for f in sorted((src / 'workspace').rglob('*')):
            if f.is_file() and not f.is_symlink() and f.suffix in {'.stdout', '.stderr', '.output', '.log'}:
                plan(f, prefix / f.relative_to(src), 'execution_capture_logs', True)

    for domain in DOMAINS:
        for f in sorted((BENCH / 'data' / domain / 'input').rglob('*')):
            assert not f.is_symlink(), f
            if f.is_file():
                plan(f, ROOT / 'data/kramabench' / f.relative_to(BENCH), 'data_lake_' + domain)
        plan(BENCH / 'workload' / (domain + '.json'), ROOT / 'data/kramabench/workload' / (domain + '.json'), 'gold_subtasks')

    official = [BENCH / n for n in ['evaluate.py', 'eval.sh', 'scripts/eval.sh', 'pyproject.toml']]
    official += sorted((BENCH / 'benchmark').glob('*.py'))
    official += sorted((BENCH / 'benchmark/fixtures').glob('*.json'))
    official += sorted((BENCH / 'benchmark/llm_tools').glob('*.py'))
    for f in official:
        plan(f, DEST / 'official' / f.relative_to(BENCH), 'official_evaluation')
    for n in ['scoring.py', 'run_kramabench.py', 'prompting.py']:
        plan(OLD / 'src/dac' / n, DEST / 'runtime/src/dac' / n, 'runtime_config_source')
    first_meta = json.loads(Path(rows[0]['结果路径']).read_text())
    for name in first_meta['prompt_sha256']:
        plan(OLD / name, DEST / 'runtime' / name, 'runtime_prompts')

    # Read, scan, hash every publishable source before writing it anywhere.
    for src, target, group, archive in planned:
        data = src.read_bytes()
        if not group.startswith('data_lake_') and group != 'gold_subtasks':
            scan(data, str(src))
        manifest.append({'source': str(src), 'destination': str(ARCHIVE.relative_to(ROOT)) + '::' + target if archive else str(Path(target).relative_to(ROOT)),
                         'group': group, 'bytes': len(data), 'sha256': digest(data), 'archive': archive})
    print('Preflight:', len(planned), 'source files scanned/hashed', flush=True)
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(ARCHIVE, 'w:gz', compresslevel=9) as tar:
        for (src, target, group, archive), item in zip(planned, manifest):
            if archive:
                tar.add(src, arcname=target, recursive=False)
            else:
                dest = Path(target)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
    print('Copied and archived; verifying bytes and SHA-256', flush=True)
    with tarfile.open(ARCHIVE, 'r:gz') as tar:
        actual_members = tar.getmembers()
        assert all(m.isfile() for m in actual_members)
        assert len(actual_members) == sum(x['archive'] for x in manifest)
        for (src, target, group, archive), item in zip(planned, manifest):
            data = tar.extractfile(target).read() if archive else Path(target).read_bytes()
            assert len(data) == item['bytes'] and digest(data) == item['sha256'], target
            assert digest(src.read_bytes()) == item['sha256'], src
            item['destination_verified'] = True
            item['source_unchanged'] = True

    tasks = {t['id']: t for domain in DOMAINS for t in json.loads((ROOT / 'data/kramabench/workload' / (domain + '.json')).read_text())}
    assert len(tasks) == 104 and sum(len(t.get('subtasks', [])) for t in tasks.values()) == 631
    scoring_hash = digest((DEST / 'runtime/src/dac/scoring.py').read_bytes())
    prompt_hash_checks = []
    for r in rows:
        src = Path(r['结果路径']).parent
        meta = json.loads((src / 'meta.json').read_text())
        assert meta['task_id'] == r['题号']
        assert meta['score'] == json.loads(r['原始评分JSON'])
        assert scoring_hash == meta['source_sha256']['src/dac/scoring.py']
        for name, expected in meta['prompt_sha256'].items():
            assert digest((DEST / 'runtime' / name).read_bytes()) == expected
        prompt_hash_checks.append(r['题号'])
        if r['是否做错'] == '待裁判':
            assert tasks[r['题号']]['answer_type'] == 'string_approximate'
            assert meta['final_answer'] is not None
            assert meta['score']['status'] == 'needs_judge'
            pending.append({'task_id': r['题号'], 'answer_type': tasks[r['题号']]['answer_type'],
                            'run_status': meta['status'], 'final_answer_type': type(meta['final_answer']).__name__,
                            'score': meta['score'], 'meta': str((DEST / 'runs' / r['批次'] / src.name / 'meta.json').relative_to(ROOT)),
                            'workload': 'data/kramabench/workload/' + r['题号'].split('-')[0] + '.json',
                            'reason': 'official_score returns needs_judge immediately for string_approximate; no model judge was run',
                            'adapter_quote': 'if kind == "string_approximate":\n        return {"status": "needs_judge", "success": None, "source": source}',
                            'official_metric': 'llm_paraphrase', 'judge_model_in_local_source': 'gpt-5-mini'})
        counts = collections.Counter(model=0, code=0, output=0, other=0)
        for name, kind in [('messages.jsonl', 'messages'), ('steps.jsonl', 'steps')]:
            text = (src / name).read_bytes().decode('utf-8')
            assert len(text) == int(r[kind + '字符数'])
            counts.update(character_parts(text, kind))
        assert sum(counts.values()) == int(r['轨迹字符数'])
        chars.append({'task_id': r['题号'], 'batch': r['批次'], 'recorded_result': r['是否做错'],
                      'model_chars': counts['model'], 'code_chars': counts['code'], 'execution_output_chars': counts['output'],
                      'other_chars': counts['other'], 'total_chars': sum(counts.values()), 'trace_bytes': int(r['轨迹字节数'])})
    assert len(pending) == 10
    with (ROOT / 'records/027_kramabench_trace_characters.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(chars[0]), lineterminator='\n'); w.writeheader(); w.writerows(chars)
    sample = OLD / 'runs/20261018_hard_all_01/archeology-hard-12_01/steps.jsonl'
    raw = [(i, line) for i, line in enumerate(sample.read_bytes().splitlines(keepends=True), 1)
           if json.loads(line).get('kind') == 'execution'][:3]
    sample_out = ROOT / 'records/027_kramabench_example_first3_steps.jsonl'
    sample_out.write_bytes(b''.join(line for i, line in raw))
    groups = {}
    for item in manifest:
        group = groups.setdefault(item['group'], {'files': 0, 'source_bytes': 0, 'destination_bytes': 0})
        group['files'] += 1
        group['source_bytes'] += item['bytes']
        group['destination_bytes'] += item['bytes']
    assert git('status', '--short') == old_status
    summary = {'source_root': str(OLD), 'main_tasks': len(rows), 'excluded_early_trials': 15,
               'source_csv_rows_preserved': len(rows_all), 'recorded_outcomes': dict(collections.Counter(r['是否做错'] for r in rows)),
               'groups': groups, 'copied_source_files': len(manifest), 'copied_source_bytes': sum(x['bytes'] for x in manifest),
               'all_destination_hashes_match': True, 'all_selected_source_hashes_unchanged': True,
               'old_git_status_unchanged': True, 'old_git_status': old_status,
               'archive': {'path': str(ARCHIVE.relative_to(ROOT)), 'compressed_bytes': ARCHIVE.stat().st_size,
                           'sha256': digest(ARCHIVE.read_bytes()), 'files': sum(x['archive'] for x in manifest),
                           'uncompressed_file_bytes': sum(x['bytes'] for x in manifest if x['archive'])},
               'trace_characters': sum(c['total_chars'] for c in chars), 'trace_bytes': sum(c['trace_bytes'] for c in chars),
               'gold_tasks': len(tasks), 'subtasks': sum(len(t.get('subtasks', [])) for t in tasks.values()),
               'pending_count': len(pending), 'scoring_source_matches_run_hashes': 104,
               'prompt_files_match_run_hashes_for_tasks': len(prompt_hash_checks),
               'credential_pattern_scan': {'publishable_source_files': sum(not x['group'].startswith('data_lake_') and x['group'] != 'gold_subtasks' for x in manifest), 'matches': 0, 'scope': 'specified credential patterns, not a proof of absence'},
               'official_local_git_commit': git('rev-parse', 'HEAD', cwd=BENCH).strip(),
               'official_local_git_status': git('status', '--short', cwd=BENCH),
               'example': {'task_id': 'archeology-hard-12', 'source': str(sample), 'source_line_numbers': [i for i,l in raw],
                           'destination': str(sample_out.relative_to(ROOT)), 'bytes': sample_out.stat().st_size},
               'excluded_snapshot_files': sum('bytes' in e for e in exclusions),
               'excluded_snapshot_bytes': sum(e.get('bytes', 0) for e in exclusions),
               'excluded_symlinks': sum(e['reason'] == 'symlink_not_followed' for e in exclusions)}
    write_json(ROOT / 'records/027_kramabench_copy_manifest.json', manifest)
    write_json(ROOT / 'records/027_kramabench_excluded_files.json', exclusions)
    write_json(ROOT / 'records/027_kramabench_pending_judge.json', pending)
    write_json(ROOT / 'records/027_kramabench_verification.json', summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
