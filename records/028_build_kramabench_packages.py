"""Extract verbatim baseline material and mechanical statistics; no evaluation."""
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
ARCHIVE = ROOT / 'traces/kramabench_luna_baseline.tar.gz'
SOURCE = ROOT / 'records/027_kramabench_source/runs'
OUT = ROOT / 'records/028_kramabench_packages'
DOMAINS = {'archeology': '考古', 'astronomy': '天文', 'biomedical': '生物医学', 'environment': '环境', 'legal': '法律', 'wildfire': '野火'}

def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def parse_spans(text):
    """Locate exact source JSON value spans, without reserializing answers."""
    decoder = json.JSONDecoder()
    spans = {}
    def ws(i):
        while i < len(text) and text[i].isspace():
            i += 1
        return i
    def value(i, path):
        i = ws(i)
        start = i
        if text[i] == '{':
            obj = {}
            i = ws(i + 1)
            while text[i] != '}':
                key, i = decoder.raw_decode(text, i)
                i = ws(i)
                assert text[i] == ':'
                obj[key], i = value(i + 1, path + (key,))
                i = ws(i)
                if text[i] == ',':
                    i = ws(i + 1)
                else:
                    assert text[i] == '}'
            i += 1
        elif text[i] == '[':
            obj = []
            i = ws(i + 1)
            while text[i] != ']':
                child, i = value(i, path + (len(obj),))
                obj.append(child)
                i = ws(i)
                if text[i] == ',':
                    i = ws(i + 1)
                else:
                    assert text[i] == ']'
            i += 1
        else:
            obj, i = decoder.raw_decode(text, i)
        spans[path] = (start, i)
        return obj, i
    obj, end = value(0, ())
    assert not text[end:].strip()
    return obj, spans

def lookup(obj, path):
    for part in path:
        obj = obj[part]
    return obj

def block(key, text, language='text'):
    fence = '`' * max(3, 1 + max([len(m.group()) for m in re.finditer(r'`+', text)] or [0]))
    separator = '' if text.endswith('\n') else '\n'
    return f'<!-- original:{key} chars:{len(text)} -->\n{fence}{language}\n{text}{separator}{fence}\n<!-- /original:{key} -->\n\n'

def main():
    assert not OUT.exists(), 'Refuse to overwrite material packages'
    OUT.mkdir(parents=True)
    originals = {}
    def source_file(path):
        text = path.read_bytes().decode('utf-8')
        originals[str(path.relative_to(ROOT))] = sha(text)
        return text
    workloads = {}
    for domain in DOMAINS:
        path = ROOT / f'data/kramabench/workload/{domain}.json'
        text = source_file(path)
        obj, spans = parse_spans(text)
        for i, task in enumerate(obj):
            workloads[task['id']] = (str(path.relative_to(ROOT)), text, obj, spans, i)
    selected = []
    for path in sorted(SOURCE.glob('*/*/meta.json')):
        text = source_file(path)
        meta, spans = parse_spans(text)
        if meta['score'].get('success') == 0 or meta['score']['status'] == 'needs_judge':
            selected.append((meta['task_id'], path, text, meta, spans))
    selected.sort()
    assert len(selected) == 50
    assert collections.Counter(m['score']['status'] for _,_,_,m,_ in selected) == {'scored':39, 'unanswered':1, 'needs_judge':10}
    index, stats = {}, []
    total_counts = collections.Counter()
    report_step_text = {}
    archive_hash = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    with tarfile.open(ARCHIVE) as tar:
        for task_id, meta_path, meta_text, meta, meta_spans in selected:
            prefix = '/'.join(meta_path.parts[-3:-1])
            msg_name, ex_name = prefix + '/messages.jsonl', prefix + '/steps.jsonl'
            msg_text = tar.extractfile(msg_name).read().decode('utf-8')
            ex_text = tar.extractfile(ex_name).read().decode('utf-8')
            msg_lines = msg_text.splitlines(keepends=True)
            ex_lines = ex_text.splitlines(keepends=True)
            messages = [json.loads(line) for line in msg_lines]
            executions = [(i, json.loads(line)) for i,line in enumerate(ex_lines,1) if json.loads(line).get('kind') == 'execution']
            responses = [(i,d) for i,d in enumerate(messages,1) if d['direction']=='response' and 'message' in d]
            assert len(responses) == meta['model_calls']
            assert len(executions) == meta['executed_steps']
            ex_by_tool = {e['tool_call_id']:(i,e) for i,e in executions}
            assert len(ex_by_tool)==len(executions)
            feedback = {}
            for i,d in enumerate(messages,1):
                if d['direction'] == 'request':
                    for j,h in enumerate(d['messages']):
                        if h.get('role') == 'tool':
                            tid = h['tool_call_id']
                            assert tid in ex_by_tool
                            assert ex_by_tool[tid][1]['model_call'] < d['call']
                            if tid in feedback:
                                assert feedback[tid]['text'] == h['content']
                            else:
                                feedback[tid] = {'text':h['content'], 'line':i, 'history_index':j}
            wname, wtext, wobj, wspans, wi = workloads[task_id]
            task = wobj[wi]
            assert meta['prompt_values']['query'] == task['query']
            assert int(meta['parameters']['max_output_chars']) == 4000
            parts = []
            evidence = {'task_id':task_id, 'meta':str(meta_path.relative_to(ROOT)), 'messages_member':msg_name,
                        'steps_member':ex_name, 'workload':wname, 'workload_index':wi,
                        'fields':{}, 'steps':[], 'raw_trace_chars':len(msg_text)+len(ex_text)}
            def add(text=''):
                parts.append(text + '\n\n')
            def original(key, src, text, obj, spans, path, line=None):
                val = lookup(obj, path)
                start,end = spans[tuple(path)]
                payload = val if isinstance(val,str) else text[start:end]
                assert isinstance(payload,str)
                evidence['fields'][key] = {'source':src, 'line':line, 'path':list(path),
                                            'mode':'decoded_string' if isinstance(val,str) else 'raw_json',
                                            'chars':len(payload), 'sha256':sha(payload)}
                language = 'python' if key.endswith('.code') else ('text' if isinstance(val,str) else 'json')
                parts.append(block(key,payload,language))
                return payload
            def from_line(key, member, lines, line, path):
                text=lines[line-1];obj,spans=parse_spans(text)
                return original(key, 'traces/kramabench_luna_baseline.tar.gz::'+member, text,obj,spans,path,line)
            add(f'# {task_id}')
            add('## 1. 题目信息')
            add(f'- 题号：`{task_id}`\n- 领域：{DOMAINS[task_id.split("-")[0]]}（`{task_id.split("-")[0]}`）\n- 难度：`{task_id.split("-")[1]}`\n- 答案类型：`{task["answer_type"]}`')
            add('- 官方评分状态：以下为旧基线适配器记录的原始 `score`，不是完整官方评测入口的新结果。')
            original('score',str(meta_path.relative_to(ROOT)),meta_text,meta,meta_spans,('score',))
            add(f'来源：`{meta_path.relative_to(ROOT)}`；归档成员 `{prefix}/messages.jsonl`、`steps.jsonl`；`{wname}` 中 `id={task_id}`。')
            add('## 2. agent 收到的题面原文')
            add('来源字段：`meta.prompt_values.query`。')
            original('query',str(meta_path.relative_to(ROOT)),meta_text,meta,meta_spans,('prompt_values','query'))
            add('## 3. 最终答案与标准答案')
            add('### agent 最终答案原文')
            if meta['final_answer'] is None:
                add('原字段为 `null`；原运行状态为 `max_steps_unanswered`，没有已提交的最终答案。')
            original('final_answer',str(meta_path.relative_to(ROOT)),meta_text,meta,meta_spans,('final_answer',))
            add('### 标准答案原文')
            original('gold_answer',wname,wtext,wobj,wspans,(wi,'answer'))
            add('## 4. 子任务')
            add('以下内容 agent 看不到，只供标注使用')
            for si,subtask in enumerate(task['subtasks']):
                add(f'### 子任务 {si+1}：{subtask["id"]}')
                add('问题原文：')
                original(f'subtask.{si+1}.query',wname,wtext,wobj,wspans,(wi,'subtasks',si,'query'))
                add('标准答案原文：')
                original(f'subtask.{si+1}.answer',wname,wtext,wobj,wspans,(wi,'subtasks',si,'answer'))
            add('## 5. 逐步记录')
            add('每一步对应一次模型回复；原 `call` 和执行 `step` 另列。只保存该次回复一份，不重复请求历史或 provider_response 副本。没有 tool 历史反馈时不以本地输出补写。原文字段由 HTML 标记和字符长度定位，代码围栏前的展示换行不计入原文。')
            readable_chars = truncated_steps = 0
            files = set()
            used_exec = set()
            step_sections = []
            for n,(line,d) in enumerate(responses,1):
                start_parts = len(parts)
                msg=d['message'];calls=msg.get('tool_calls') or []
                assert len(calls)<=1
                execution = ex_by_tool.get(calls[0]['id']) if calls else None
                step = {'ordinal':n, 'model_call':d['call'], 'attempt':d.get('attempt'), 'response_line':line,
                        'execution_line':execution[0] if execution else None, 'execution_step':execution[1]['step'] if execution else None,
                        'tool_call_id':calls[0]['id'] if calls else None, 'reasoning':[], 'encrypted_chars':0,
                        'feedback_line':None, 'feedback_history_index':None, 'truncated':False}
                add(f'### 第 {n} 步（模型 call={d["call"]}；执行 step={execution[1]["step"] if execution else "无"}）')
                add('#### 模型可读输出')
                if msg.get('content') is not None:
                    add('`content` 原文：')
                    from_line(f'step.{n}.content',msg_name,msg_lines,line,('message','content'))
                else:
                    add('`content=null`。')
                readable = []
                if msg.get('reasoning'):
                    readable.append((('message','reasoning'), msg['reasoning']))
                for ri,rd in enumerate(msg.get('reasoning_details') or []):
                    if rd['type']=='reasoning.encrypted':
                        assert isinstance(rd['data'],str)
                        step['encrypted_chars']+=len(rd['data'])
                    else:
                        assert rd['type'] in {'reasoning.summary','reasoning.text'}
                        for key in ['summary','text']:
                            if rd.get(key):
                                assert isinstance(rd[key],str)
                                readable.append((('message','reasoning_details',ri,key),rd[key]))
                seen={}
                for path,text in readable:
                    if text in seen:
                        step['reasoning'].append({'path':list(path), 'duplicate_of':seen[text]})
                        continue
                    key=f'step.{n}.reasoning.{len(seen)+1}'
                    seen[text]=key
                    add('可读 reasoning 原文（`'+'.'.join(map(str,path[1:]))+'`）：')
                    from_line(key,msg_name,msg_lines,line,path)
                    step['reasoning'].append({'path':list(path), 'field':key})
                    readable_chars+=len(text)
                if not seen:
                    add('无可读 reasoning 文本。')
                if step['encrypted_chars']:
                    add(f'有加密 reasoning，{step["encrypted_chars"]} 字符')
                if any('duplicate_of' in x for x in step['reasoning']):
                    add('同一步中逐字相同的 reasoning / reasoning_details 文本只保留一份。')
                if seen:
                    total_counts['steps_with_readable_reasoning']+=1
                add('#### 执行的代码')
                if execution:
                    el,e=execution
                    assert e['model_call']==d['call']
                    used_exec.add(el)
                    from_line(f'step.{n}.code',ex_name,ex_lines,el,('code',))
                    add('#### 模型实际看到的执行反馈')
                    fb=feedback.get(e['tool_call_id'])
                    if fb:
                        step.update(feedback_line=fb['line'],feedback_history_index=fb['history_index'])
                        full=e['full_observation']
                        assert isinstance(full,str)
                        step.update(feedback_chars=len(fb['text']),full_output_chars=len(full))
                        if len(fb['text'])<len(full):
                            step['truncated']=True;truncated_steps+=1
                            add(f'模型看到的被截断：看到 {len(fb["text"])} 字符，完整输出 {len(full)} 字符')
                            marker='\n... [output truncated] ...\n'
                            assert len(full)>4000 and fb['text']==full[:1986]+marker+full[-1986:]
                        else:
                            assert fb['text']==full and len(full)<=4000
                        from_line(f'step.{n}.feedback',msg_name,msg_lines,fb['line'],('messages',fb['history_index'],'content'))
                        total_counts['observed_tool_feedback']+=1
                    else:
                        add('消息历史中未发现对应的 role=tool 反馈；没有后续请求记录可证明模型看到的反馈原文。不放入本地完整输出。')
                        total_counts['executions_without_observed_feedback']+=1
                    add('#### files_read 原字段')
                    from_line(f'step.{n}.files_read',ex_name,ex_lines,el,('files_read',))
                    files.update(e['files_read'])
                else:
                    assert not calls
                    add('该次模型回复没有工具调用；无执行代码记录。')
                    add('#### 模型实际看到的执行反馈')
                    add('该次回复没有工具调用，无对应 role=tool 执行反馈。')
                    add('#### files_read 原字段')
                    add('无对应 execution 记录，因此没有 files_read 字段；不推断读文件行为。')
                evidence['steps'].append(step)
                step_sections.append(''.join(parts[start_parts:]))
            assert used_exec=={i for i,e in executions}
            add('## 6. 机械统计')
            add(f'- 步数：{len(responses)}（模型回复次数；其中 {len(executions)} 步有执行代码，{len(responses)-len(executions)} 步没有执行代码）。\n- 读过的文件清单：{len(files)} 个不同原始路径字符串；只对 execution.files_read 去重，不归一化路径，不推断未记录的访问。')
            for fi, filename in enumerate(sorted(files), 1):
                parts.append(block('file.'+str(fi),filename))
            if not files:
                add('清单为空。')
            evidence['unique_files_read']=sorted(files)
            package=''.join(parts)
            path=OUT/(task_id+'.md');path.write_text(package,encoding='utf-8')
            evidence['package_chars']=len(package);evidence['package_sha256']=sha(package)
            index[task_id]=evidence
            stats.append({'题号':task_id,'原始轨迹字符数':len(msg_text)+len(ex_text),'材料包字符数':len(package),
                          '步数':len(responses),'有没有可读的 reasoning':'是' if readable_chars else '否',
                          '可读 reasoning 的字符数':readable_chars,'被截断的步数':truncated_steps})
            total_counts.update(model_response_steps=len(responses),execution_steps=len(executions),
                                no_execution_steps=len(responses)-len(executions),truncated_steps=truncated_steps,
                                readable_reasoning_chars=readable_chars,subtasks=len(task['subtasks']))
            report_step_text[task_id]=''.join(step_sections[:3])
    assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()==archive_hash
    for name,expected in originals.items():
        assert sha((ROOT/name).read_bytes().decode('utf-8'))==expected
    random_seed=20261031
    chosen=random.Random(random_seed).choice(sorted(index))
    values=[x['材料包字符数'] for x in stats]
    summary={'tasks':50,'failed':40,'needs_judge':10,'package_total_chars':sum(values),
             'package_min_chars':min(values),'package_median_chars':statistics.median(values),'package_max_chars':max(values),
             'smallest_tasks':[x['题号'] for x in stats if x['材料包字符数']==min(values)],
             'largest_tasks':[x['题号'] for x in stats if x['材料包字符数']==max(values)],
             'raw_total_chars':sum(x['原始轨迹字符数'] for x in stats),
             'tasks_with_readable_reasoning':sum(x['有没有可读的 reasoning']=='是' for x in stats),
             **total_counts,'truncation_limit':4000,'observed_truncation_head_chars':1986,'observed_truncation_tail_chars':1986,
             'random_sample_seed':random_seed,'random_sample_task':chosen,
             'source_archive_sha256':archive_hash,'all_selected_input_hashes_unchanged':True,
             'source_file_sha256':originals}
    with (ROOT/'records/028_kramabench_package_stats.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(stats[0]),lineterminator='\n');writer.writeheader();writer.writerows(stats)
    dump(ROOT/'records/028_kramabench_package_index.json',index)
    dump(ROOT/'records/028_kramabench_package_summary.json',summary)
    sample=ROOT/'records/028_kramabench_report_sample.txt';sample.write_text(report_step_text[chosen],encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='source_file_sha256'},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
