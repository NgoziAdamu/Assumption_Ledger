"""Independently compare Markdown payloads with archived JSONL and source JSON.

Does not import the builder, execute recorded code, or call evaluation/model APIs.
Run: python3 records/028_check_kramabench_packages.py
"""
from pathlib import Path
import collections
import csv
import hashlib
import json
import random
import re
import statistics
import tarfile

ROOT = Path(__file__).resolve().parents[1]
HEADER = re.compile(r'^<!-- original:([\w.]+) chars:(\d+) -->\n(`{3,})(text|json|python)\n', re.M)

def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def get(obj, path):
    for part in path:
        obj = obj[part]
    return obj

def extract_blocks(package):
    found = {}
    pos = 0
    while match := HEADER.search(package, pos):
        key, count, fence, language = match.groups()
        assert key not in found, ('duplicate block', key)
        end = match.end() + int(count)
        payload = package[match.end():end]
        separator = '' if payload.endswith('\n') else '\n'
        suffix = separator + fence + '\n<!-- /original:' + key + ' -->\n'
        assert package[end:end+len(suffix)] == suffix, ('malformed payload boundary', key)
        found[key] = payload
        pos = end + len(suffix)
    return found

def equal_text(actual, expected, label):
    assert actual == expected, ('verbatim mismatch', label)
    assert actual.encode('utf-8') == expected.encode('utf-8'), ('byte mismatch', label)

def main():
    records=ROOT/'records'
    index=json.loads((records/'028_kramabench_package_index.json').read_bytes())
    summary=json.loads((records/'028_kramabench_package_summary.json').read_bytes())
    stats={r['题号']:r for r in csv.DictReader((records/'028_kramabench_package_stats.csv').open())}
    old_stats={r['task_id']:r for r in csv.DictReader((records/'027_kramabench_trace_characters.csv').open())}
    source_cache={}
    def file_source(path):
        if path not in source_cache:
            text=(ROOT/path).read_bytes().decode('utf-8')
            source_cache[path]=(text,json.loads(text))
        return source_cache[path]
    selected={}
    for p in sorted((records/'027_kramabench_source/runs').glob('*/*/meta.json')):
        name=str(p.relative_to(ROOT));text,meta=file_source(name)
        if meta['score'].get('success')==0 or meta['score']['status']=='needs_judge':
            selected[meta['task_id']]=(name,meta)
    assert len(selected)==50
    assert set(index)==set(stats)==set(selected)
    out=records/'028_kramabench_packages'
    assert {p.name for p in out.iterdir()}=={task+'.md' for task in selected}
    counts=collections.Counter(); per_task=[]; feedback_lengths=[]; reasoning_tasks=0
    content_totals=collections.Counter()
    archive=ROOT/'traces/kramabench_luna_baseline.tar.gz'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==summary['source_archive_sha256']
    with tarfile.open(archive) as tar:
        for task_id,(meta_name,meta) in sorted(selected.items()):
            package=(out/(task_id+'.md')).read_bytes().decode('utf-8')
            blocks=extract_blocks(package)
            entry=index[task_id]
            prefix='/'.join(Path(meta_name).parts[-3:-1])
            msg_name=prefix+'/messages.jsonl';ex_name=prefix+'/steps.jsonl'
            assert entry['messages_member']==msg_name and entry['steps_member']==ex_name
            msg_text=tar.extractfile(msg_name).read().decode('utf-8')
            ex_text=tar.extractfile(ex_name).read().decode('utf-8')
            msg_raw=msg_text.splitlines(keepends=True);ex_raw=ex_text.splitlines(keepends=True)
            msgs=[json.loads(line) for line in msg_raw];steps=[json.loads(line) for line in ex_raw]
            response_lines=[i for i,d in enumerate(msgs,1) if d['direction']=='response' and 'message' in d]
            execution_lines=[i for i,d in enumerate(steps,1) if d.get('kind')=='execution']
            assert len(response_lines)==meta['model_calls']
            assert len(execution_lines)==meta['executed_steps']
            assert len(entry['steps'])==len(response_lines)
            expected_fields={}
            def expect(key, source, line, path):
                expected_fields[key]=(source,line,list(path))
            expect('query',meta_name,None,('prompt_values','query'))
            expect('score',meta_name,None,('score',))
            expect('final_answer',meta_name,None,('final_answer',))
            domain=task_id.split('-')[0]
            wname=f'data/kramabench/workload/{domain}.json';wtext,workload=file_source(wname)
            wi=next(i for i,t in enumerate(workload) if t['id']==task_id)
            task=workload[wi]
            expect('gold_answer',wname,None,(wi,'answer'))
            assert meta['prompt_values']['query']==task['query']
            for si,sub in enumerate(task['subtasks'],1):
                expect(f'subtask.{si}.query',wname,None,(wi,'subtasks',si-1,'query'))
                expect(f'subtask.{si}.answer',wname,None,(wi,'subtasks',si-1,'answer'))
            counts['subtask_questions_and_answers_checked']+=len(task['subtasks'])
            assert '以下内容 agent 看不到，只供标注使用' in package
            unique_files=set();used_execution=set();readable_chars=0;truncated=0
            for n,line in enumerate(response_lines,1):
                response=msgs[line-1];msg=response['message'];rec=entry['steps'][n-1]
                assert rec['ordinal']==n and rec['response_line']==line and rec['model_call']==response['call']
                msg_source='traces/kramabench_luna_baseline.tar.gz::'+msg_name
                ex_source='traces/kramabench_luna_baseline.tar.gz::'+ex_name
                if msg.get('content') is not None:
                    expect(f'step.{n}.content',msg_source,line,('message','content'))
                # Each distinct readable string appears once within this response.
                readable=[]
                if msg.get('reasoning'):
                    readable.append((['message','reasoning'],msg['reasoning']))
                encrypted=0
                for j,rd in enumerate(msg.get('reasoning_details') or []):
                    if rd['type']=='reasoning.encrypted':
                        encrypted+=len(rd['data'])
                        assert rd['data'] not in package
                        counts['encrypted_payloads_confirmed_absent']+=1
                    else:
                        assert rd['type'] in ['reasoning.summary','reasoning.text']
                        for key in ['summary','text']:
                            if rd.get(key):readable.append((['message','reasoning_details',j,key],rd[key]))
                unique=[]
                for path,text in readable:
                    if text not in [v for p,v in unique]:unique.append((path,text))
                for j,(path,text) in enumerate(unique,1):
                    expect(f'step.{n}.reasoning.{j}',msg_source,line,path)
                    readable_chars+=len(text)
                if unique:counts['steps_with_readable_reasoning']+=1
                assert rec['encrypted_chars']==encrypted
                if encrypted:assert f'有加密 reasoning，{encrypted} 字符' in package
                calls=msg.get('tool_calls') or []
                assert len(calls)<=1
                if not calls:
                    assert rec['execution_line'] is None
                    assert f'step.{n}.code' not in blocks and f'step.{n}.feedback' not in blocks
                    counts['no_execution_response_steps']+=1
                    continue
                call_id=calls[0]['id']
                candidates=[i for i in execution_lines if steps[i-1]['tool_call_id']==call_id]
                assert len(candidates)==1
                el=candidates[0];execution=steps[el-1]
                assert execution['model_call']==response['call']
                assert rec['execution_line']==el and rec['execution_step']==execution['step'] and rec['tool_call_id']==call_id
                used_execution.add(el)
                expect(f'step.{n}.code',ex_source,el,('code',))
                expect(f'step.{n}.files_read',ex_source,el,('files_read',))
                equal_text(blocks[f'step.{n}.code'],execution['code'],(task_id,n,'code'))
                # Cross-check execution code against model tool arguments as well.
                arguments=json.loads(calls[0]['function']['arguments'])
                equal_text(execution['code'],arguments['code'],(task_id,n,'model_argument_code'))
                counts['verbatim_code_checks']+=1
                unique_files.update(execution['files_read'])
                matches=[]
                for mi,request in enumerate(msgs,1):
                    if request['direction']=='request':
                        for hi,h in enumerate(request['messages']):
                            if h.get('role')=='tool' and h['tool_call_id']==call_id:
                                assert request['call']>response['call']
                                matches.append((mi,hi,h['content']))
                if matches:
                    mi,hi,text=matches[0]
                    assert all(v==text for _,_,v in matches)
                    assert rec['feedback_line']==mi and rec['feedback_history_index']==hi
                    expect(f'step.{n}.feedback',msg_source,mi,('messages',hi,'content'))
                    equal_text(blocks[f'step.{n}.feedback'],text,(task_id,n,'feedback'))
                    counts['verbatim_feedback_checks']+=1
                    full=execution['full_observation']
                    if len(text)<len(full):
                        truncated+=1
                        assert f'模型看到的被截断：看到 {len(text)} 字符，完整输出 {len(full)} 字符' in package
                        assert text==full[:1986]+'\n... [output truncated] ...\n'+full[-1986:]
                        assert len(text)==4000 and len(full)>4000
                        assert full not in package, (task_id,n,'full truncated output must not be copied')
                    else:
                        equal_text(text,full,(task_id,n,'untruncated_feedback'))
                        assert len(full)<=4000
                    assert rec['truncated']==(len(text)<len(full))
                    feedback_lengths.append(len(text))
                else:
                    assert f'step.{n}.feedback' not in blocks and rec['feedback_line'] is None
                    assert el==execution_lines[-1]
                    counts['last_executions_without_observed_feedback']+=1
                    counts['last_execution_final_answer' if execution['is_final_answer'] else 'last_execution_without_final_answer']+=1
            assert used_execution==set(execution_lines)
            assert set(entry['fields'])==set(expected_fields)
            assert set(blocks)==set(expected_fields)|{f'file.{i}' for i in range(1,len(unique_files)+1)}
            for i,name in enumerate(sorted(unique_files),1):equal_text(blocks[f'file.{i}'],name,(task_id,'file',i))
            assert entry['unique_files_read']==sorted(unique_files)
            for key,(src,line,path) in expected_fields.items():
                ref=entry['fields'][key]
                assert (ref['source'],ref['line'],ref['path'])==(src,line,path)
                if '::' in src:
                    member=src.split('::',1)[1]
                    raw=(msg_raw if member==msg_name else ex_raw)[line-1]
                    obj=json.loads(raw)
                else:
                    raw,obj=file_source(src)
                original=get(obj,path);payload=blocks[key]
                if isinstance(original,str):
                    equal_text(payload,original,(task_id,key))
                    assert ref['mode']=='decoded_string'
                else:
                    assert json.loads(payload)==original and payload in raw,(task_id,key,'raw JSON literal')
                    assert ref['mode']=='raw_json'
                assert len(payload)==ref['chars'] and digest(payload)==ref['sha256']
                counts['verbatim_original_fields_checked']+=1
                if key.startswith('subtask.'):group='subtask_question_answer_chars'
                elif key=='gold_answer':group='gold_answer_chars'
                elif key.startswith('step.'):group='step_original_fields_chars'
                else:group='other_original_fields_chars'
                content_totals[group]+=len(payload)
            r=stats[task_id]
            assert int(r['原始轨迹字符数'])==len(msg_text)+len(ex_text)==int(old_stats[task_id]['total_chars'])
            assert int(r['材料包字符数'])==len(package)==entry['package_chars']
            assert digest(package)==entry['package_sha256']
            assert int(r['步数'])==len(response_lines)
            assert int(r['可读 reasoning 的字符数'])==readable_chars
            assert r['有没有可读的 reasoning']==('是' if readable_chars else '否')
            assert int(r['被截断的步数'])==truncated
            counts['model_response_steps']+=len(response_lines)
            counts['truncated_steps']+=truncated
            counts['readable_reasoning_chars']+=readable_chars
            if readable_chars:reasoning_tasks+=1
            per_task.append({'task_id':task_id,'code_checks':len(execution_lines),
                             'feedback_checks':sum(s['feedback_line'] is not None for s in entry['steps']),
                             'package_chars':len(package),'passed':True})
    assert summary['tasks_with_readable_reasoning']==reasoning_tasks
    assert summary['readable_reasoning_chars']==counts['readable_reasoning_chars']
    assert summary['model_response_steps']==counts['model_response_steps']
    assert summary['execution_steps']==counts['verbatim_code_checks']
    assert summary['truncated_steps']==counts['truncated_steps']
    vals=[x['package_chars'] for x in per_task]
    assert summary['package_total_chars']==sum(vals)
    assert summary['package_min_chars']==min(vals) and summary['package_median_chars']==statistics.median(vals) and summary['package_max_chars']==max(vals)
    for name,expected in summary['source_file_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==summary['source_archive_sha256']
    sample_id=random.Random(summary['random_sample_seed']).choice(sorted(selected))
    assert sample_id==summary['random_sample_task']
    package=(out/(sample_id+'.md')).read_bytes().decode('utf-8')
    first=package.index('### 第 1 步（')
    end=package.find('### 第 4 步（',first)
    if end<0:end=package.index('## 6. 机械统计',first)
    sample=(records/'028_kramabench_report_sample.txt').read_bytes().decode('utf-8')
    equal_text(sample,package[first:end],'report sample')
    # Confirm the exact comparison rejects single-character changes in memory.
    negative_checks=0
    for kind in ['code','feedback']:
        payload=next(v for k,v in extract_blocks(package).items() if k.endswith('.'+kind) and v)
        try:
            equal_text(('X' if payload[0]!='X' else 'Y')+payload[1:],payload,'intentional in-memory mutation')
        except AssertionError:
            negative_checks+=1
    assert negative_checks==2
    result={'passed':True,'tasks':50,**counts,'tasks_with_readable_reasoning':reasoning_tasks,
            'original_text_character_breakdown':dict(content_totals),'single_character_mutations_rejected':negative_checks,
            'all_source_hashes_unchanged':True,'all_package_csv_counts_match':True,
            'random_sample_first_three_steps_match_package':True,'per_task':per_task}
    (records/'028_kramabench_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='per_task'},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
