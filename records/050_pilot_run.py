"""Two-task pilot using official SDKs, immutable 049 inputs, no semantic grading.

Only runtime credentials come from ~/.openai_key and ~/.deepseek_key. They are
never serialized. --probe executes the first scheduled call, and a later normal
run reuses its immutable record instead of paying for it again.
"""
import argparse
import ast
from collections import Counter, defaultdict
import copy
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import io
import json
import logging
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import tokenize

sys.dont_write_bytecode = True
logging.disable(logging.CRITICAL)
os.environ.pop('OPENAI_LOG', None)
import openai
from openai import OpenAI
import tiktoken

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_OUT = ROOT/'records/050_pilot'
# Actual API requests/responses and all statistics are kept in this git-ignored
# archive. records/050_pilot contains explicitly labelled, redacted public copies.
OUT = ROOT/'data/050_pilot_full'
TASKS = ['impl-025', 'legal-hard-18']
MODEL = 'gpt-6.1-sol'
JUDGE = 'deepseek-flash'
SECRETS = []
ENC = tiktoken.get_encoding('o200k_base')
REVIEW_FIELDS = {'statement','about','target','evidence_of_dependence','alternative','importance','reason','updates'}
FINAL_FIELDS = {'id','merged','reason'}
METHOD2_FIELDS = {'problem','about','evidence_in_work','source','importance','reason'}
JUDGE_MATCH_FIELDS = {'verdict','rank','quote','reason'}
JUDGE_STATED_FIELDS = {'verdict','where','quote','reason'}


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def scrub(value):
    if isinstance(value,str):
        for secret in SECRETS:
            if secret:value=value.replace(secret,'[REDACTED_CREDENTIAL]')
        return re.sub(r'\bsk-[A-Za-z0-9_*.\-]{8,}', '[REDACTED_CREDENTIAL_PATTERN]',value)
    if isinstance(value,dict):return {scrub(k) if isinstance(k,str) else k:scrub(v) for k,v in value.items()}
    if isinstance(value,list):return [scrub(v) for v in value]
    return value


def dump(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:
        json.dump(scrub(value),f,ensure_ascii=False,indent=2);f.write('\n')


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='') as f:f.write(scrub(value))


def archive_path(path):
    p=Path(path)
    if not p.is_absolute():p=ROOT/p
    # Historical records keep their original paths verbatim; resolve those
    # paths to the complete private archive without editing the records.
    if p==PUBLIC_OUT or p.is_relative_to(PUBLIC_OUT):return OUT/p.relative_to(PUBLIC_OUT)
    return p


def load(path):
    return json.loads(archive_path(path).read_text(encoding='utf-8'))


def tokens(text):
    return len(ENC.encode(text,disallowed_special=()))


def baseline(task,kind,call):
    for r in csv.DictReader((ROOT/'records/049_small_exp_token_counts.csv').open()):
        if r['task']==task and r['method']==kind and (kind!='method1' or int(r['call'])==call):
            return int(r['tokens']) if r['tokens'] else None
    return None


def assemble(task,call=None,mode=None,ledger_file=None):
    cmd=[sys.executable,str(ROOT/'records/049_small_exp_assemble.py'),task]
    if call is not None:cmd.append(str(call))
    if mode:cmd.append(mode)
    if ledger_file:cmd.extend(['--ledger-json',str(ledger_file)])
    # Preserve CRLF and bare CR from the 049 assembler. text=True would apply
    # universal-newline conversion to its stdout and change source material.
    result=subprocess.run(cmd,cwd=ROOT,capture_output=True)
    if result.returncode:raise ValueError('049 assembly failed: '+result.stderr.decode('utf-8'))
    return result.stdout.decode('utf-8'),cmd


def parse_text(text):
    stripped=text.strip()
    if stripped.startswith('```'):
        stripped=re.sub(r'^```[^\r\n]*\r?\n','',stripped,count=1)
        stripped=re.sub(r'(?:\r?\n)?```\s*$','',stripped,count=1).strip()
    try:
        obj=json.loads(stripped)
        return {'success':True,'root_type':type(obj).__name__,'parsed':obj}
    except (ValueError,TypeError) as e:
        return {'success':False,'error_type':type(e).__name__,'error':str(e)}


def response_text(raw,provider):
    if provider=='openai':
        return ''.join(c.get('text','') for item in raw.get('output',[]) if item.get('type')=='message'
                       for c in item.get('content',[]) if c.get('type')=='output_text')
    choices=raw.get('choices') or []
    content=choices[0].get('message',{}).get('content') if choices else None
    return content if isinstance(content,str) else ''


def usage_record(raw,provider):
    u=raw.get('usage') or {}
    if provider=='openai':
        return {'input_tokens':u.get('input_tokens'),'cached_input_tokens':(u.get('input_tokens_details') or {}).get('cached_tokens'),
                'output_tokens':u.get('output_tokens'),'reasoning_tokens':(u.get('output_tokens_details') or {}).get('reasoning_tokens'),
                'raw_usage':u}
    hit=u.get('prompt_cache_hit_tokens',(u.get('prompt_tokens_details') or {}).get('cached_tokens'))
    return {'input_tokens':u.get('prompt_tokens'),'cached_input_tokens':hit,'output_tokens':u.get('completion_tokens'),
            'reasoning_tokens':(u.get('completion_tokens_details') or {}).get('reasoning_tokens'),'raw_usage':u}


def price(usage,provider,started):
    n=usage['input_tokens'];cached=usage['cached_input_tokens'];out=usage['output_tokens']
    dt=datetime.fromisoformat(started)
    peak=dt.weekday()<5 and (1<=dt.hour<4 or 6<=dt.hour<10)
    rates=({'input':2.0,'cached':0.10,'output':10.0} if provider=='openai' else
           {'input':0.30 if peak else 0.15,'cached':0.006 if peak else 0.003,'output':1.20 if peak else 0.60})
    if n is None or out is None:
        amount=None
    else:
        # Missing cache statistics use the uncached rate, explicitly marked.
        cached_for_cost=cached if cached is not None else 0
        amount=((n-cached_for_cost)*rates['input']+cached_for_cost*rates['cached']+out*rates['output'])/1e6
    return {'estimated_usd':amount,'rates_per_million':rates,'peak':peak if provider!='openai' else None,
            'peak_timestamp_rule':'request attempt start time, UTC',
            'cached_usage_missing_assumed_zero_for_cost':cached is None,
            'long_input_price_unverified':bool(provider=='openai' and n and n>272000),
            'price_source':'用户本轮指定，仅估算，以账单为准'}


def total_cost():
    return sum((load(p).get('cost',{}).get('estimated_usd') or 0) for p in (OUT/'calls').glob('*/record.json'))


class StopPilot(Exception):
    pass


def stop(reason,details):
    if not (OUT/'STOP.json').exists():dump(OUT/'STOP.json',{'time':now(),'reason':reason,'details':details,'estimated_usd':total_cost()})
    raise StopPilot(reason)


def fatal_error(status,body):
    text=json.dumps(body,ensure_ascii=False).lower() if body is not None else ''
    if status in [401,403]:return 'authentication_or_access_denied'
    if status in [400,404,422] and any(s in text for s in ['model_not_found','model not found','does not exist',
        'model is not available','unsupported model','model_not_available','invalid model','not have access to model',
        'model is not supported','model_not_supported']):return 'model_missing_or_rejected'
    return None


def call_api(task,kind,prompt,call_number=None,point_id=None,method=None):
    if (OUT/'STOP.json').exists():raise StopPilot(load(OUT/'STOP.json')['reason'])
    if total_cost()>5:stop('estimated_cost_exceeds_5_usd',{})
    tag=(f'{task}_{kind}'+(f'_{call_number}' if call_number is not None else '')+
         (f'_{point_id}' if point_id is not None else '')+(f'_{method}' if method else ''))
    tag=re.sub(r'[^A-Za-z0-9_.-]','_',tag)
    folder=OUT/'calls'/tag
    if (folder/'record.json').exists():
        archived=load(folder/'record.json')
        if archived.get('prompt_sha256')!=sha(prompt.encode()):
            print(json.dumps({'event':'historical_cached_input_differs','tag':tag,
                  'handling':'Reuse the actual historical record; no API call. A corrected trial requires a new archive.'}),flush=True)
        return archived
    folder.mkdir(parents=True,exist_ok=True)
    provider='openai' if kind in ['method1','method1_final','method2'] else 'deepseek'
    model=MODEL if provider=='openai' else JUDGE
    body=({'model':model,'input':prompt,'reasoning':{'effort':'medium','summary':'auto'},'max_output_tokens':32000}
          if provider=='openai' else {'model':model,'messages':[{'role':'user','content':prompt}]})
    endpoint='https://api.openai.com/v1/responses' if provider=='openai' else 'https://api.deepseek.com/chat/completions'
    if not (folder/'request.json').exists():dump(folder/'request.json',{'method':'POST','url':endpoint,'json':body})
    started=now();attempts=[];raw=None;last_error=None
    key=Path.home()/('.openai_key' if provider=='openai' else '.deepseek_key')
    secret=key.read_text(encoding='utf-8').strip()
    if secret not in SECRETS:SECRETS.append(secret)
    client=OpenAI(api_key=secret,base_url='https://api.openai.com/v1' if provider=='openai' else 'https://api.deepseek.com',max_retries=0)
    print(json.dumps({'event':'call_start','task':task,'kind':kind,'call':call_number,'point':point_id,
                      'provider':provider,'prompt_tokens_o200k':tokens(prompt),'spent_estimated_usd':total_cost()},ensure_ascii=False),flush=True)
    for attempt in range(1,5):
        attempt_start=now();t0=time.monotonic()
        try:
            api=client.responses if provider=='openai' else client.chat.completions
            wrapped=api.with_raw_response.create(**body)
            raw=wrapped.http_response.json()
            raw_text=wrapped.http_response.text
            dump(folder/f'attempt_{attempt}_response.json',raw)
            write(folder/f'attempt_{attempt}_response_body.txt',raw_text)
            try:dump(folder/f'attempt_{attempt}_sdk_response.json',wrapped.parse().model_dump(mode='json'))
            except Exception as e:dump(folder/f'attempt_{attempt}_sdk_parse_error.json',{'type':type(e).__name__,'message':str(e)})
            attempts.append({'attempt':attempt,'started_at':attempt_start,'finished_at':now(),
                             'seconds':time.monotonic()-t0,'http_status':wrapped.http_response.status_code,'success':True})
            break
        except (openai.APIConnectionError,openai.APIStatusError) as e:
            status=getattr(e,'status_code',None);error_body=getattr(e,'body',None)
            err={'attempt':attempt,'started_at':attempt_start,'finished_at':now(),'seconds':time.monotonic()-t0,
                 'http_status':status,'success':False,'error_type':type(e).__name__,'body':error_body,'message':scrub(str(e))}
            dump(folder/f'attempt_{attempt}_error.json',err)
            if getattr(e,'response',None) is not None:
                write(folder/f'attempt_{attempt}_response_body.txt',e.response.text)
            attempts.append(err);last_error=err
            fatal=fatal_error(status,error_body)
            retryable=isinstance(e,openai.APIConnectionError) or status==429 or (status is not None and 500<=status<600)
            if fatal or not retryable or attempt==4:break
            delay=2**attempt
            print(json.dumps({'event':'retry','task':task,'kind':kind,'attempt':attempt,'delay_seconds':delay,'http_status':status}),flush=True)
            time.sleep(delay)
        except Exception as e:
            err={'attempt':attempt,'started_at':attempt_start,'finished_at':now(),'seconds':time.monotonic()-t0,
                 'http_status':None,'success':False,'error_type':type(e).__name__,'message':scrub(str(e))}
            dump(folder/f'attempt_{attempt}_error.json',err);attempts.append(err);last_error=err;break
    client.close()
    u=usage_record(raw,provider) if raw else {'input_tokens':None,'cached_input_tokens':None,'output_tokens':None,'reasoning_tokens':None,'raw_usage':{}}
    cost=price(u,provider,attempts[-1]['started_at'])
    text=response_text(raw,provider) if raw else ''
    parsed=parse_text(text) if raw else {'success':False,'error':'no_api_response'}
    if not (folder/'text.txt').exists():write(folder/'text.txt',text)
    if not (folder/'parse.json').exists():dump(folder/'parse.json',parsed)
    if raw and provider=='openai':
        status=raw.get('status');incomplete=raw.get('incomplete_details')
        truncated=bool(status=='incomplete' and (incomplete or {}).get('reason') in ['max_output_tokens','context_length_exceeded'])
        summaries=[s.get('text','') for o in raw.get('output',[]) if o.get('type')=='reasoning' for s in o.get('summary',[]) if isinstance(s,dict)]
        reasoning_items=sum(o.get('type')=='reasoning' for o in raw.get('output',[]))
    elif raw:
        status=((raw.get('choices') or [{}])[0]).get('finish_reason');incomplete=None;truncated=status=='length'
        msg=((raw.get('choices') or [{}])[0]).get('message') or {}
        summaries=[msg['reasoning_content']] if msg.get('reasoning_content') else [];reasoning_items=None
    else:status='api_error';incomplete=None;truncated=None;summaries=[];reasoning_items=None
    old_est=baseline(task,kind,call_number)
    record={'tag':tag,'task':task,'kind':kind,'call':call_number,'point_id':point_id,'method':method,
            'provider':provider,'model_requested':model,'model_returned':raw.get('model') if raw else None,
            'started_at':started,'finished_at':now(),'attempts':attempts,'api_success':raw is not None,
            'status':status,'completed':status in ['completed','stop'],'incomplete_details':incomplete,'truncated':truncated,
            'parse_success':parsed['success'],'parse_root_type':parsed.get('root_type'),'usage':u,'cost':cost,
            'prompt_o200k_tokens':tokens(prompt),'baseline_049_none_tokens':old_est,
            'actual_input_to_049_ratio':u['input_tokens']/old_est if u['input_tokens'] is not None and old_est else None,
            'actual_input_to_current_o200k_ratio':u['input_tokens']/tokens(prompt) if u['input_tokens'] is not None else None,
            'cached_input_fraction':u['cached_input_tokens']/u['input_tokens'] if u['input_tokens'] and u['cached_input_tokens'] is not None else None,
            'reasoning_item_count':reasoning_items,'has_reasoning_summary_text':any(s for s in summaries),
            'reasoning_summary_texts':summaries,'request_path':str((folder/'request.json').relative_to(ROOT)),
            'response_path':str((folder/f'attempt_{attempts[-1]["attempt"]}_response.json').relative_to(ROOT)) if raw else None,
            'parse_path':str((folder/'parse.json').relative_to(ROOT)),'prompt_sha256':sha(prompt.encode()),
            'script_sha256_at_call':sha(Path(__file__).read_bytes()),'error':last_error if raw is None else None,
            'billing_uncertainty':'失败的网络/5xx尝试没有usage；未把缺失计费用量称为确定免费。' if any(not a['success'] for a in attempts) else None}
    dump(folder/'record.json',record)
    print(json.dumps({'event':'call_finished','task':task,'kind':kind,'call':call_number,'api_success':record['api_success'],
                      'parse_success':record['parse_success'],'status':status,'cost_usd':cost['estimated_usd'],
                      'cumulative_estimated_usd':total_cost()},ensure_ascii=False),flush=True)
    if raw is None:
        fatal=fatal_error((last_error or {}).get('http_status'),(last_error or {}).get('body'))
        if fatal:stop(fatal,{'tag':tag,'error':last_error})
    if total_cost()>5:stop('estimated_cost_exceeds_5_usd',{'tag':tag})
    return load(folder/'record.json')


def store_once(path,obj):
    if Path(path).exists():
        if load(path)!=scrub(obj):raise ValueError('Existing pilot artifact differs: '+str(path))
    else:dump(path,obj)


def parsed_value(record):
    p=load(ROOT/record['parse_path'])
    return p.get('parsed') if p.get('success') else None


def point_rows():
    with (ROOT/'records/047_premise_sentences_draft.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    selected=[r for r in rows if r['对象编号'].startswith('impl-025_') or r['对象编号']=='legal-hard-18']
    if len(selected)!=6:raise ValueError('Expected 6 known points, found '+str(len(selected)))
    return selected


def a049():
    spec=importlib.util.spec_from_file_location('a049_pilot',ROOT/'records/049_small_exp_assemble.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def sql_comments(text):
    """SQL lexical comments, excluding single/double/dollar quoted strings."""
    result=[];i=0
    while i<len(text):
        if text.startswith('--',i):
            end=text.find('\n',i)
            if end<0:end=len(text)
            result.append((i,end,text[i:end]));i=end
        elif text.startswith('/*',i):
            start=i;depth=1;i+=2
            while i<len(text) and depth:
                if text.startswith('/*',i):depth+=1;i+=2
                elif text.startswith('*/',i):depth-=1;i+=2
                else:i+=1
            result.append((start,i,text[start:i]))
        elif text[i] in ["'",'"']:
            quote=text[i];i+=1
            while i<len(text):
                if text[i]==quote:
                    if i+1<len(text) and text[i+1]==quote:i+=2;continue
                    i+=1;break
                i+=1
        elif text[i]=='$' and (match:=re.match(r'\$(?:[A-Za-z_]\w*)?\$',text[i:])):
            marker=match[0];end=text.find(marker,i+len(marker));i=len(text) if end<0 else end+len(marker)
        else:i+=1
    return result


def python_comments(code,source,include_sql_literals=False):
    pieces=[];issues=[];line_offsets=[0]
    for line in code.splitlines(keepends=True):line_offsets.append(line_offsets[-1]+len(line))
    def offset(pos):return line_offsets[pos[0]-1]+pos[1]
    try:
        stream=tokenize.generate_tokens(io.StringIO(code).readline)
        for tok in stream:
            if tok.type==tokenize.COMMENT:
                pieces.append({'kind':'code_comment','language':'python','text':tok.string,'source':source,
                               'code_chars':[offset(tok.start),offset(tok.end)],'code_line':tok.start[0],
                               'source_token_sha256':sha(tok.string.encode())})
            elif include_sql_literals and tok.type==tokenize.STRING and any(s in tok.string for s in ['--','/*']):
                try:
                    literal=ast.literal_eval(tok.string)
                    if not isinstance(literal,str):continue
                    mode='ast.literal_eval of a string token; no code execution'
                except Exception:
                    match=re.match(r"(?is)^[rubf]*(\"\"\"|'''|\"|')",tok.string)
                    if not match:
                        issues.append({'source':source,'kind':'unsupported_string_token','line':tok.start[0]});continue
                    marker=match[1];literal=tok.string[match.end():-len(marker)]
                    mode='raw token body; escapes/interpolation not evaluated'
                    issues.append({'source':source,'kind':'sql_comment_in_nonliteral_string','line':tok.start[0],
                                   'handling':'Only lexically delimited raw token body examined; no interpolation.'})
                for start,end,text in sql_comments(literal):
                    pieces.append({'kind':'code_comment','language':'sql_in_python_string','text':text,'source':source,
                                   'python_token_chars':[offset(tok.start),offset(tok.end)],'python_token_line':tok.start[0],
                                   'source_token_sha256':sha(tok.string.encode()),'literal_comment_chars':[start,end],
                                   'literal_decoding':mode})
    except (tokenize.TokenError,IndentationError,SyntaxError) as e:
        issues.append({'source':source,'kind':'python_tokenization_error','error':str(e)})
    return pieces,issues


def heredocs(command):
    lines=command.splitlines(keepends=True);offsets=[0]
    for line in lines:offsets.append(offsets[-1]+len(line))
    result=[];i=0
    while i<len(lines):
        header=lines[i];matches=list(re.finditer(r"<<(-?)\s*(['\"]?)([A-Za-z_]\w*)\2",header));i+=1
        for match in matches:
            begin=i
            while i<len(lines) and (lines[i].rstrip('\r\n').lstrip('\t') if match[1] else lines[i].rstrip('\r\n'))!=match[3]:i+=1
            result.append({'header':header,'delimiter':match[3],'body':''.join(lines[begin:i]),
                           'command_chars':[offsets[begin],offsets[i]],'terminated':i<len(lines)})
            if i<len(lines):i+=1
    return result


def extract_agent_text(task):
    path=OUT/task/'agent_text.json'
    if path.exists():return load(path)
    A=a049();m=A.manifest(task);pieces=[];issues=[]
    if task=='impl-025':
        for a in m['actions']:
            command=A.text_ref(a['command'])
            for index,h in enumerate(heredocs(command),1):
                src={'event':a['id'],'command_ref':a['command'],'heredoc':index,
                     'heredoc_command_chars':h['command_chars']}
                is_python=bool(re.search(r'\bpython(?:3)?\s+(?:-\s*)?<<',h['header']) or re.search(r'>+\s*[^\s]+\.py\b',h['header']))
                is_sql=h['delimiter'].upper()=='SQL' or bool(re.search(r'>+\s*[^\s]+\.sql\b',h['header']))
                if is_python:
                    comments,warnings=python_comments(h['body'],src,True);pieces.extend(comments);issues.extend(warnings)
                elif is_sql:
                    for begin,end,text in sql_comments(h['body']):
                        pieces.append({'kind':'code_comment','language':'sql','text':text,'source':src,'code_chars':[begin,end]})
            if re.search(r'\bpython(?:3)?\s+-c\b',command):
                issues.append({'kind':'inline_python_c_not_extracted','event':a['id']})
        final=next(c for c in m['calls'] if c['kind']=='final')
        member=m['prompt_source']['member'].rsplit('/',1)[0]+f'/{final["position"]}.json'
        event=json.loads(A.archive_member('traces/dacomp_deimpl_prev.tar.gz',member))
        if 'final_thought' in event.get('args',{}):
            pieces.append({'kind':'final_report','text':event['args']['final_thought'],
                           'source':{'event':event['id'],'archive':'traces/dacomp_deimpl_prev.tar.gz','member':member,'field':['args','final_thought']}})
        else:issues.append({'kind':'finish_final_thought_missing','event':final['position']})
    else:
        for a in m['actions']:
            for ref in a.get('reasoning',[]):
                pieces.append({'kind':'reasoning','text':A.text_ref(ref),'source':{'step':a['id'],'ref':ref}})
            if a.get('code'):
                code=A.text_ref(a['code'])
                comments,warnings=python_comments(code,{'step':a['id'],'code_ref':a['code']})
                pieces.extend(comments);issues.extend(warnings)
        pi=load(ROOT/'records/028_kramabench_package_index.json')[task]
        meta=load(ROOT/pi['meta']);answer=meta['final_answer']
        pieces.append({'kind':'final_report','text':answer if isinstance(answer,str) else json.dumps(answer,ensure_ascii=False),
                       'source':{'path':pi['meta'],'field':['final_answer']}})
    text=''.join(f"=== {p['kind']} ({'event '+str(p['source']['event']) if 'event' in p['source'] else 'step '+str(p['source'].get('step','final'))}; {p.get('language','text')}) ===\n{p['text']}\n\n" for p in pieces)
    result={'task':task,'rules':{
        'DAComp':'Only Python heredocs / .py writes are tokenized for # comments. SQL -- and /* */ are lexed in SQL heredocs and Python string tokens; SQL quoted strings are skipped. Finish args.final_thought is appended. No command/output or source file is executed.',
        'KramaBench':'All 049 reasoning summary references, tokenize COMMENT (#) from each execution code, and meta.final_answer. No encrypted reasoning or execution output is substituted.',
        'string_literals':'ast.literal_eval only decodes string tokens. Nonliteral/f-string bodies remain raw and are flagged. No interpolation or agent code execution.',
        'provenance':'Each excerpt retains event/step and source coordinates/hash. Repeated comments in different actions remain repeated.'},
        'pieces':pieces,'issues_for_claude':issues,'text':text,'characters':len(text),'text_sha256':sha(text.encode())}
    dump(path,result);write(OUT/task/'agent_text.txt',text)
    return result


def ledger_items(task,call_number,value):
    result=[];issues=[]
    if not isinstance(value,list):
        return [],[{'kind':'method1_root_not_array','task':task,'call':call_number,'actual':type(value).__name__}]
    for index,item in enumerate(value,1):
        identity={'id':f'c{call_number}-{index}','call':call_number}
        if isinstance(item,dict):
            entry=copy.deepcopy(item)
            collisions={k:entry[k] for k in identity if k in entry}
            if collisions:
                entry['_original_identity_fields']=collisions
                issues.append({'kind':'model_identity_field_collision','task':task,'call':call_number,'item':index,'fields':list(collisions)})
            entry.update(identity)
        else:
            entry={**identity,'_non_object_output':item}
            issues.append({'kind':'non_object_method1_item','task':task,'call':call_number,'item':index})
        result.append(entry)
    return result,issues


def final_lists(task,method,value,ledger):
    """Only literal table-key normalization, ledger id lookup, and specified sorting."""
    points=[r for r in point_rows() if (task=='impl-025' and r['benchmark']=='DAComp') or (task=='legal-hard-18' and r['benchmark']=='KramaBench')]
    targets=list(dict.fromkeys(r['对象编号'].removeprefix('impl-025_') if task=='impl-025' else r['对象编号'] for r in points))
    output={'task':task,'method':method,'raw_keys':list(value) if isinstance(value,dict) else None,
            'key_mapping':[],'unmatched_keys':[],'unknown_ids':[],'targets':{},'issues_for_claude':[]}
    if not isinstance(value,dict):
        for target in targets:output['targets'][target]={'status':'unavailable','reason':'parsed_root_not_object','items':[]}
        output['issues_for_claude'].append({'kind':'final_output_not_object','actual':type(value).__name__})
        return output
    by_id={row['id']:row for row in ledger}
    lists={}
    for key,entries in value.items():
        if not isinstance(entries,list):
            output['issues_for_claude'].append({'kind':'final_key_not_list','key':key});continue
        rows=[]
        for rank,entry in enumerate(entries,1):
            if method=='method1':
                pid=entry.get('id') if isinstance(entry,dict) else None
                if pid not in by_id:
                    output['unknown_ids'].append({'key':key,'rank':rank,'id':pid,'entry':entry});continue
                rows.append(copy.deepcopy(by_id[pid]))
            else:rows.append(copy.deepcopy(entry))
        lists[key]=rows
    if task=='impl-025':
        matched=defaultdict(list)
        for key in value:
            normalized=key.rsplit('.',1)[-1].lower()
            hit=normalized in targets
            output['key_mapping'].append({'original_key':key,'normalized_key':normalized,'matches':hit})
            if hit:matched[normalized].append(key)
            else:output['unmatched_keys'].append(key)
        for target in targets:
            keys=matched[target]
            if not keys:output['targets'][target]={'status':'not_listed','items':[]}
            elif len(keys)>1:
                output['targets'][target]={'status':'unavailable','reason':'multiple_keys_normalize_to_target','keys':keys,'items':[]}
                output['issues_for_claude'].append({'kind':'duplicate_normalized_table_keys','target':target,'keys':keys})
            elif keys[0] not in lists:
                output['targets'][target]={'status':'unavailable','reason':'key_value_not_list','keys':keys,'items':[]}
            else:output['targets'][target]={'status':'listed','keys':keys,'items':lists[keys[0]]}
    else:
        target=targets[0]
        if len(value)==1:
            key=next(iter(value));output['key_mapping'].append({'original_key':key,'assigned_task':target,'rule':'one key; preserve its list'})
            output['targets'][target]=({'status':'listed','keys':[key],'items':lists[key]} if key in lists else
                                        {'status':'unavailable','reason':'key_value_not_list','items':[]})
        elif len(value)>1:
            collected=[];bad=[]
            for key_index,key in enumerate(value):
                if key not in lists:bad.append(key);continue
                for rank,item in enumerate(lists[key]):
                    importance=item.get('importance') if isinstance(item,dict) else None
                    if not isinstance(importance,(int,float)) or isinstance(importance,bool):bad.append({'key':key,'rank':rank+1})
                    else:collected.append((-importance,key_index,rank,item))
            if bad:
                output['targets'][target]={'status':'unavailable','reason':'cannot_sort_missing_or_non_numeric_importance','items':[]}
                output['issues_for_claude'].append({'kind':'krama_multi_key_sort_undefined','locations':bad})
            else:
                collected.sort(key=lambda r:r[:3])
                output['targets'][target]={'status':'listed','keys':list(value),'items':[r[3] for r in collected[:10]],
                                           'sort_rule':'importance desc, key order, original entry order; top 10'}
        else:output['targets'][target]={'status':'not_listed','items':[]}
    return output


def judge_items(items):
    result=[]
    for i,item in enumerate(items[:10],1):
        if isinstance(item,dict):result.append({'rank':i,'item':{k:v for k,v in item.items() if k!='importance'}})
        else:result.append({'rank':i,'item':item})
    return result


def fill_judge(template,values):
    # Only fill the archived original template; no prompt text edits.
    return (ROOT/'records/049_prompts'/template).read_text(encoding='utf-8').format_map(values)


def local_input_failure(task,kind,call_number,error):
    tag=f'{task}_{kind}'+(f'_{call_number}' if call_number is not None else '')
    folder=OUT/'calls'/tag
    if (folder/'record.json').exists():return load(folder/'record.json')
    folder.mkdir(parents=True,exist_ok=True)
    dump(folder/'parse.json',{'success':False,'error':'input_assembly_failed'})
    record={'tag':tag,'task':task,'kind':kind,'call':call_number,'point_id':None,'method':None,'provider':'openai',
            'model_requested':MODEL,'started_at':now(),'finished_at':now(),'attempts':[],
            'api_success':False,'status':'input_assembly_failed','completed':False,'truncated':None,'parse_success':False,
            'parse_path':str((folder/'parse.json').relative_to(ROOT)),
            'usage':{'input_tokens':None,'cached_input_tokens':None,'output_tokens':None,'reasoning_tokens':None},
            'cost':{'estimated_usd':0},'error':scrub(str(error)),'has_reasoning_summary_text':False}
    dump(folder/'record.json',record)
    return record


def run_pipeline():
    points=point_rows();store_once(OUT/'selected_points.json',points)
    result={'tasks':{},'judge_match':[],'judge_stated':[],'issues_for_claude':[]}
    for task in TASKS:
        manifest=load(ROOT/f'records/049_small_exp_inputs/{task}/manifest.json')
        ledger=[];review_records=[]
        for c in manifest['calls']:
            if c['kind']=='final':continue
            number=c['call'];before=OUT/task/f'ledger_before_call_{number}.json';store_once(before,ledger)
            try:
                prompt,cmd=assemble(task,number,ledger_file=before)
                record=call_api(task,'method1',prompt,call_number=number)
            except StopPilot:raise
            except Exception as e:
                record=local_input_failure(task,'method1',number,e)
                result['issues_for_claude'].append({'task':task,'call':number,'kind':'input_assembly_failed','error':scrub(str(e))})
            review_records.append(record['tag'])
            if record['parse_success']:
                additions,issues=ledger_items(task,number,parsed_value(record));ledger.extend(additions)
                result['issues_for_claude'].extend(issues)
            store_once(OUT/task/f'ledger_after_call_{number}.json',ledger)
        all_ledger=OUT/task/'ledger_all.json';store_once(all_ledger,ledger)
        outputs={}
        for kind,mode in [('method1_final','--final-rank'),('method2','--method2')]:
            try:
                prompt,cmd=assemble(task,mode=mode,ledger_file=all_ledger if kind=='method1_final' else None)
                record=call_api(task,kind,prompt)
            except StopPilot:raise
            except Exception as e:
                record=local_input_failure(task,kind,None,e)
                result['issues_for_claude'].append({'task':task,'kind':kind,'error':scrub(str(e))})
            outputs['method1' if kind=='method1_final' else 'method2']=record
        final={}
        for method,record in outputs.items():
            final[method]=final_lists(task,method,parsed_value(record),ledger)
            store_once(OUT/task/f'{method}_final_lists.json',final[method])
            result['issues_for_claude'].extend(final[method]['issues_for_claude'])
        task_points=[r for r in points if (task=='impl-025' and r['benchmark']=='DAComp') or (task=='legal-hard-18' and r['benchmark']=='KramaBench')]
        for point in task_points:
            target=point['对象编号'].removeprefix('impl-025_') if task=='impl-025' else point['对象编号']
            for method in ['method1','method2']:
                listed=final[method]['targets'][target]
                item={'task':task,'point_id':point['point_id'],'point_number':int(point['序号']),
                      'target':target,'method':method,'list_status':listed['status']}
                if listed['status']=='not_listed':
                    item.update(called=False,result={'verdict':'no_match','rank':None,'quote':None,'reason':'未列出；按用户规则不调用裁判。'})
                elif listed['status']!='listed':
                    item.update(called=False,result=None,technical_status='unavailable_final_list')
                else:
                    ranked=judge_items(listed['items'])
                    if len(listed['items'])>10:
                        result['issues_for_claude'].append({'kind':'judge_uses_top10_of_overlong_model_list',
                              'task':task,'point':point['point_id'],'method':method,'original_count':len(listed['items']),
                              'handling':'原清单完整保存；items按用户规定只编号1到10。'})
                    prompt=fill_judge('judge_match.txt',{'table':target,'premise':point['agent默认的前提'],
                         'truth':point['实际要求或数据情况'],'items':json.dumps(ranked,ensure_ascii=False,indent=2)})
                    record=call_api(task,'judge_match',prompt,point_id=int(point['序号']),method=method)
                    item.update(called=True,tag=record['tag'],items=ranked,result=parsed_value(record),parse_success=record['parse_success'])
                result['judge_match'].append(item)
        agent_text=extract_agent_text(task)
        result['issues_for_claude'].extend({'task':task,**i} for i in agent_text['issues_for_claude'])
        for point in task_points:
            target=point['对象编号'].removeprefix('impl-025_') if task=='impl-025' else point['对象编号']
            prompt=fill_judge('judge_stated.txt',{'table':target,'premise':point['agent默认的前提'],
                       'truth':point['实际要求或数据情况'],'agent_text':agent_text['text']})
            record=call_api(task,'judge_stated',prompt,point_id=int(point['序号']))
            result['judge_stated'].append({'task':task,'point_id':point['point_id'],'point_number':int(point['序号']),
                          'target':target,'tag':record['tag'],'result':parsed_value(record),'parse_success':record['parse_success']})
        result['tasks'][task]={'review_calls':review_records,'ledger_items':len(ledger),'outputs':{k:v['tag'] for k,v in outputs.items()}}
    store_once(OUT/'pipeline_results.json',result)
    print(json.dumps({'event':'pipeline_models_complete','estimated_usd':total_cost()},ensure_ascii=False),flush=True)


def collapsed(text):
    return re.sub(r'\s+',' ',text)


def quote_check(value,candidates,location,scope,extra=None):
    row={'location':location,'scope':scope,'quote':value}
    if extra:row.update(extra)
    if value is None:
        row.update(status='null_not_applicable',exact=None,whitespace_collapsed=None)
    elif not isinstance(value,str):
        row.update(status='non_string_not_checked',exact=None,whitespace_collapsed=None,
                   actual_type=type(value).__name__)
    elif value=='':
        row.update(status='empty_string_not_counted_as_match',exact=False,whitespace_collapsed=False)
    else:
        exact=[i for i,c in enumerate(candidates) if value in c]
        normalized=[i for i,c in enumerate(candidates) if collapsed(value) in collapsed(c)]
        row.update(status='checked',exact=bool(exact),whitespace_collapsed=bool(normalized),
                   exact_candidate_indices=exact,normalized_candidate_indices=normalized)
    return row


def string_leaves(obj,path='$'):
    if isinstance(obj,str):return [(path,obj)]
    if isinstance(obj,list):return [pair for i,v in enumerate(obj) for pair in string_leaves(v,f'{path}[{i}]')]
    if isinstance(obj,dict):return [pair for k,v in obj.items() for pair in string_leaves(v,f'{path}.{k}')]
    return []


def delimiter_spans(text):
    """All explicitly delimited substrings; no selection of the intended quote."""
    patterns=[('fenced_code',r'```[^\n]*\n(.*?)\n```'),
              ('inline_code',r'(?<!`)`([^`\n]+)`(?!`)'),
              ('double_quote',r'"([^"\n]+)"'),('curly_double',r'“([^”]+)”'),
              ('curly_single',r'‘([^’]+)’'),('single_quote',r"(?<![A-Za-z0-9])'([^'\n]+)'(?![A-Za-z0-9])")]
    result=[]
    for kind,pattern in patterns:
        for m in re.finditer(pattern,text,re.S):
            result.append({'delimiter':kind,'start':m.start(1),'end':m.end(1),'text':m[1]})
    return sorted(result,key=lambda r:(r['start'],r['end'],r['delimiter']))


def format_audit(record,value):
    issues=[];groups=[];kind=record['kind'];task=record['task']
    def issue(kind,**fields):issues.append({'tag':record['tag'],'task':task,'kind':kind,**fields})
    def fields(item,expected,location):
        if not isinstance(item,dict):issue('item_not_object',location=location,actual=type(item).__name__);return
        missing=sorted(expected-set(item))
        if missing:issue('missing_fields',location=location,fields=missing)
    if not record['parse_success']:return issues,groups
    if kind=='method1':
        if not isinstance(value,list):issue('root_not_array',actual=type(value).__name__);return issues,groups
        table_names=[s['name'] for s in load(ROOT/f'records/049_small_exp_inputs/{task}/manifest.json')['sections']] if task=='impl-025' else []
        buckets=Counter()
        for i,item in enumerate(value,1):
            fields(item,REVIEW_FIELDS,f'item[{i}]')
            if not isinstance(item,dict):continue
            target=item.get('target')
            matches=[name for name in table_names if isinstance(target,str) and re.search(r'(?<![A-Za-z0-9_])'+re.escape(name)+r'(?![A-Za-z0-9_])',target)]
            keys=matches or [json.dumps(target,ensure_ascii=False)]
            for key in keys:buckets[key]+=1
            groups.append({'tag':record['tag'],'item':i,'target_as_written':target,'literal_table_matches':matches,
                           'grouping_rule':'literal contract-table-name occurrence in target; otherwise literal target as result label'})
        for target,n in buckets.items():
            if n>5:issue('more_than_5_in_single_review',target_group=target,count=n)
    elif kind in ['method1_final','method2']:
        if not isinstance(value,dict):issue('root_not_object',actual=type(value).__name__);return issues,groups
        expected=FINAL_FIELDS if kind=='method1_final' else METHOD2_FIELDS
        for key,items in value.items():
            if not isinstance(items,list):issue('table_value_not_array',key=key);continue
            if len(items)>10:issue('more_than_10_in_final_table',key=key,count=len(items))
            for i,item in enumerate(items,1):fields(item,expected,f'{key}[{i}]')
    else:fields(value,JUDGE_MATCH_FIELDS if kind=='judge_match' else JUDGE_STATED_FIELDS,'root')
    return issues,groups


def reconstruct_pipeline_results():
    """Preserve unattempted statuses if a user stop condition interrupted the run."""
    if (OUT/'pipeline_results.json').exists():return load(OUT/'pipeline_results.json')
    points=point_rows();records=[load(p) for p in (OUT/'calls').glob('*/record.json')]
    result={'tasks':{},'judge_match':[],'judge_stated':[],'issues_for_claude':[],
            'reconstructed_after_stop':(OUT/'STOP.json').exists()}
    for point in points:
        task='impl-025' if point['benchmark']=='DAComp' else 'legal-hard-18'
        target=point['对象编号'].removeprefix('impl-025_') if task=='impl-025' else point['对象编号']
        for method in ['method1','method2']:
            found=[r for r in records if r['kind']=='judge_match' and r.get('point_id')==int(point['序号']) and r.get('method')==method]
            item={'task':task,'point_id':point['point_id'],'point_number':int(point['序号']),'target':target,'method':method}
            if found:
                r=found[0];item.update(called=True,tag=r['tag'],result=parsed_value(r),parse_success=r['parse_success'])
                path=OUT/task/f'{method}_final_lists.json'
                if path.exists():item['items']=judge_items(load(path)['targets'][target]['items'])
            else:
                path=OUT/task/f'{method}_final_lists.json'
                status=load(path)['targets'][target]['status'] if path.exists() else 'not_attempted'
                item.update(called=False,list_status=status,result=({'verdict':'no_match','rank':None,'quote':None,'reason':'未列出；按用户规则不调用裁判。'} if status=='not_listed' else None))
            result['judge_match'].append(item)
        found=[r for r in records if r['kind']=='judge_stated' and r.get('point_id')==int(point['序号'])]
        item={'task':task,'point_id':point['point_id'],'point_number':int(point['序号']),'target':target}
        if found:
            r=found[0];item.update(tag=r['tag'],result=parsed_value(r),parse_success=r['parse_success'])
        else:item.update(result=None,technical_status='not_attempted')
        result['judge_stated'].append(item)
    return result


def audit_run():
    records=sorted([load(p) for p in (OUT/'calls').glob('*/record.json')],key=lambda r:r['started_at'])
    pipeline=reconstruct_pipeline_results();quote_rows=[];format_issues=[];grouping=[]
    for r in records:
        value=parsed_value(r);issues,groups=format_audit(r,value);format_issues.extend(issues);grouping.extend(groups)
        if not r['parse_success'] or not r.get('request_path'):continue
        body=load(ROOT/r['request_path'])['json'];prompt=body.get('input') or body['messages'][0]['content']
        if r['kind']=='method1' and isinstance(value,list):
            for i,item in enumerate(value,1):
                if not isinstance(item,dict):continue
                for key in ['evidence_of_dependence','alternative']:
                    if key in item:quote_rows.append(quote_check(item[key],[prompt],f'{r["tag"]}.item[{i}].{key}',
                                     'exact complete reviewer input',{'tag':r['tag'],'task':r['task'],'field':key}))
        if r['kind']=='method2' and isinstance(value,dict):
            for key,items in value.items():
                if not isinstance(items,list):continue
                for i,item in enumerate(items,1):
                    if not isinstance(item,dict):continue
                    for field in ['evidence_in_work','source']:
                        if field in item:quote_rows.append(quote_check(item[field],[prompt],f'{r["tag"]}.{key}[{i}].{field}',
                                      'exact complete reviewer input',{'tag':r['tag'],'task':r['task'],'field':field}))
    for item in pipeline['judge_match']:
        obj=item.get('result')
        if not item.get('called') or not isinstance(obj,dict):continue
        rank=obj.get('rank');items=item.get('items',[])
        ranked=next((i for i in items if i.get('rank')==rank),None)
        chosen=ranked['item'] if ranked is not None else items
        candidates=[json.dumps(chosen,ensure_ascii=False,indent=2)]+[v for path,v in string_leaves(chosen)]
        quote_rows.append(quote_check(obj.get('quote'),candidates,f'{item["tag"]}.quote',
           'rank-selected reviewed item (serialized JSON plus its decoded string leaves); all items if rank invalid',
           {'tag':item['tag'],'task':item['task'],'field':'judge_match.quote','rank_found':ranked is not None,
            'point_number':item['point_number'],'method':item['method']}))
    for item in pipeline['judge_stated']:
        obj=item.get('result');path=OUT/item['task']/'agent_text.json'
        if not isinstance(obj,dict) or not path.exists():continue
        quote_rows.append(quote_check(obj.get('quote'),[load(path)['text']],f'{item["tag"]}.quote',
             'extracted agent_text only (known-error wording excluded)',{'tag':item['tag'],'task':item['task'],
              'field':'judge_stated.quote','point_number':item['point_number']}))
    span_checks=[];framed_locations=[]
    by_tag={r['tag']:r for r in records}
    for row in quote_rows:
        if row['field'] not in ['evidence_of_dependence','alternative','evidence_in_work','source'] or not isinstance(row['quote'],str):continue
        request=load(ROOT/by_tag[row['tag']]['request_path'])['json'];prompt=request.get('input') or request['messages'][0]['content']
        spans=delimiter_spans(row['quote'])
        for span in spans:
            span_checks.append(quote_check(span['text'],[prompt],row['location']+f'.span[{span["start"]}:{span["end"]}]',
                    'explicit delimiter substring of returned field, complete original reviewer input',
                    {'tag':row['tag'],'task':row['task'],'field':row['field'],'delimiter':span['delimiter'],
                     'parent_field_chars':[span['start'],span['end']]}))
        if spans and not row.get('exact') and row['field'] in ['alternative','source']:
            framed_locations.append(row['location'])
    span_summary={}
    for field in sorted({r['field'] for r in span_checks}):
        rows=[r for r in span_checks if r['field']==field]
        span_summary[field]={'delimited_substrings':len(rows),'exact_found':sum(r['exact'] is True for r in rows),
                             'normalized_found':sum(r['whitespace_collapsed'] is True for r in rows)}
    store_once(OUT/'quote_delimiter_checks.json',{'rule':'Supplement only: enumerate all literal quote/backtick-delimited substrings; do not select which substring is the intended citation or replace whole-field checks.',
              'summary':span_summary,'checks':span_checks})
    quote_summary={}
    for field in sorted({r['field'] for r in quote_rows}):
        rows=[r for r in quote_rows if r['field']==field];checked=[r for r in rows if r['status']=='checked']
        quote_summary[field]={'total_rows':len(rows),'checked_nonempty_strings':len(checked),
                 'exact_found':sum(r['exact'] for r in checked),'normalized_found':sum(r['whitespace_collapsed'] for r in checked),
                 'not_applicable_or_non_string':len(rows)-len(checked)}
    store_once(OUT/'quote_checks.json',{'rules':{'whole_field':'Check the whole string exactly as returned; never select a more favorable fragment from alternative/source.',
              'normalization':'Only replace each run of Unicode whitespace with one ASCII space; no case/punctuation/ellipsis changes.',
              'judge_match':'Use the quoted rank item, checking JSON serialization and decoded string fields; record invalid/missing rank explicitly.',
              'null_and_empty':'null is not applicable; empty strings are not counted as matches.'},'summary':quote_summary,'checks':quote_rows})
    store_once(OUT/'format_checks.json',{'issues':format_issues,'method1_grouping':grouping,
           'grouping_limitation':'Only literal names/target labels are grouped. Table membership is not inferred from meaning.'})
    store_once(OUT/'judge_results.json',{'judge_match':pipeline['judge_match'],'judge_stated':pipeline['judge_stated']})
    table_maps={task:{method:load(OUT/task/f'{method}_final_lists.json') for method in ['method1','method2'] if (OUT/task/f'{method}_final_lists.json').exists()} for task in TASKS}
    store_once(OUT/'table_mapping.json',table_maps)
    gaps=list(pipeline.get('issues_for_claude',[]))
    if framed_locations:
        gaps.append({'kind':'citation_boundary_for_explanation_plus_quote','blocking':False,
           'detail':'alternative/source 中出现解释与引号片段并存。提示词未定义引用片段的机器边界；已分别保存整字段和全部显式定界子串的两种精确/空白归一匹配，不语义挑选、不展开省略号，也不据整字段未命中推断引用造假。请Claude决定以后如何汇总这一口径。',
           'locations':framed_locations})
    store_once(OUT/'decisions_for_claude.json',gaps)
    summary={'number':50,'start_commit':load(OUT/'start_state.json')['start_commit'],'tasks':TASKS,
       'recorded_calls':len(records),'api_attempts':sum(len(r['attempts']) for r in records),
       'api_successes':sum(r['api_success'] for r in records),'parse_successes':sum(r['parse_success'] for r in records),
       'completed':sum(r['completed'] for r in records),'truncated':sum(r.get('truncated') is True for r in records),
       'retry_attempts':sum(max(0,len(r['attempts'])-1) for r in records),
       'estimated_usd':sum(r['cost'].get('estimated_usd') or 0 for r in records),
       'unknown_cost_calls':[r['tag'] for r in records if r['cost'].get('estimated_usd') is None],
       'long_inputs':[r['tag'] for r in records if r['cost'].get('long_input_price_unverified')],
       'usage_totals':{key:sum(r['usage'].get(key) or 0 for r in records) for key in ['input_tokens','cached_input_tokens','output_tokens','reasoning_tokens']},
       'usage_missing':{key:[r['tag'] for r in records if r['usage'].get(key) is None] for key in ['input_tokens','cached_input_tokens','output_tokens','reasoning_tokens']},
       'reasoning_summary_text_calls':[r['tag'] for r in records if r.get('has_reasoning_summary_text')],
       'format_issue_count':len(format_issues),'quote_summary':quote_summary,'new_rule_gaps':len(gaps),
       'stop':load(OUT/'STOP.json') if (OUT/'STOP.json').exists() else None,
       'judge_match_skipped_not_listed':sum(not r.get('called') and r.get('list_status')=='not_listed' for r in pipeline['judge_match']),
       'sdk_version':importlib.metadata.version('openai')}
    store_once(OUT/'summary.json',summary)
    rows=[]
    for r in records:
        rows.append({'tag':r['tag'],'task':r['task'],'kind':r['kind'],'call':r.get('call'),
                     'point_number':r.get('point_id'),'method':r.get('method'),'started_at':r['started_at'],
                     'api_success':r['api_success'],'parse_success':r['parse_success'],'status':r['status'],
                     'truncated':r.get('truncated'),'input_tokens':r['usage'].get('input_tokens'),
                     'cached_input_tokens':r['usage'].get('cached_input_tokens'),'cached_fraction':r.get('cached_input_fraction'),
                     'output_tokens':r['usage'].get('output_tokens'),'reasoning_tokens':r['usage'].get('reasoning_tokens'),
                     'o200k_current':r.get('prompt_o200k_tokens'),'o200k_049_none':r.get('baseline_049_none_tokens'),
                     'input_to_049_ratio':r.get('actual_input_to_049_ratio'),'input_to_current_ratio':r.get('actual_input_to_current_o200k_ratio'),
                     'reasoning_summary_text':r.get('has_reasoning_summary_text'),'estimated_usd':r['cost'].get('estimated_usd'),
                     'attempts':len(r['attempts'])})
    csv_path=OUT/'call_summary.csv'
    if rows and not csv_path.exists():
        with csv_path.open('x',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print(json.dumps({'event':'audit_complete',**{k:v for k,v in summary.items() if k in ['recorded_calls','estimated_usd','format_issue_count','new_rule_gaps','stop']}},ensure_ascii=False),flush=True)


def validate_artifacts():
    """Read-only source and record reconciliation; no SDK request is issued."""
    checks=Counter();state=load(OUT/'start_state.json')
    for name,h in state['tracked_file_sha256'].items():
        assert sha((ROOT/name).read_bytes())==h,name
    A=a049();points=point_rows();assert load(OUT/'selected_points.json')==points
    records=sorted([load(p) for p in (OUT/'calls').glob('*/record.json')],key=lambda r:r['started_at'])
    by_tag={r['tag']:r for r in records};input_fidelity=[]
    for task in TASKS:
        accumulated=[];m=A.manifest(task)
        for c in m['calls']:
            if c['kind']=='final':continue
            n=c['call'];assert load(OUT/task/f'ledger_before_call_{n}.json')==accumulated
            record=by_tag[f'{task}_method1_{n}'];value=parsed_value(record)
            if record['parse_success']:
                assert isinstance(value,list)
                for i,item in enumerate(value,1):
                    assert isinstance(item,dict) and 'id' not in item and 'call' not in item
                    accumulated.append({**item,'id':f'c{n}-{i}','call':n})
            assert load(OUT/task/f'ledger_after_call_{n}.json')==accumulated
            checks['ledger_snapshot_pairs']+=1
        assert load(OUT/task/'ledger_all.json')==accumulated
        checks['ledger_items_preserved']+=len(accumulated)
        for method in ['method1','method2']:
            final=load(OUT/task/f'{method}_final_lists.json')
            expected=final_lists(task,method,parsed_value(by_tag[f'{task}_'+('method1_final' if method=='method1' else 'method2')]),accumulated)
            assert final==expected
            checks['final_lists_reconciled']+=1
        agent=load(OUT/task/'agent_text.json')
        assert (OUT/task/'agent_text.txt').read_text()==agent['text']
        assert sha(agent['text'].encode())==agent['text_sha256']
        for part in agent['pieces']:
            src=part['source']
            if part['kind']=='reasoning':assert A.text_ref(src['ref'])==part['text']
            elif part['kind']=='final_report':
                if 'archive' in src:
                    raw=json.loads(A.archive_member(src['archive'],src['member']));text=raw['args']['final_thought']
                else:
                    answer=load(ROOT/src['path'])['final_answer'];text=answer if isinstance(answer,str) else json.dumps(answer,ensure_ascii=False)
                assert text==part['text']
            checks['agent_text_source_excerpts']+=1
        # Independently count Python COMMENT tokens in saved Python bodies/code.
        independent_python_comments=0;literal_comment_markers=Counter()
        for action in m['actions']:
            if task=='impl-025':
                command=A.text_ref(action['command'])
                literal_comment_markers.update({'hash':command.count('#'),'dashdash':command.count('--'),'slashstar':command.count('/*')})
                blocks=[h['body'] for h in heredocs(command) if re.search(r'\bpython(?:3)?\s+(?:-\s*)?<<',h['header']) or re.search(r'>+\s*[^\s]+\.py\b',h['header'])]
            else:blocks=[A.text_ref(action['code'])] if action.get('code') else []
            for code in blocks:
                independent_python_comments+=sum(t.type==tokenize.COMMENT for t in tokenize.generate_tokens(io.StringIO(code).readline))
        assert independent_python_comments==sum(p.get('language')=='python' for p in agent['pieces'])
        if task=='impl-025':
            assert not any(literal_comment_markers.values()),dict(literal_comment_markers)
            assert not any(p['kind']=='code_comment' for p in agent['pieces'])
        checks['agent_comment_inventories']+=1
    for r in records:
        assert r['api_success'] and r['parse_success'] and r['completed'] and not r['truncated']
        assert len(r['attempts'])==1
        folder=archive_path(ROOT/r['parse_path']).parent
        raw=load(ROOT/r['response_path']);wire=json.loads((folder/'attempt_1_response_body.txt').read_text())
        assert wire==raw
        sdk=load(folder/'attempt_1_sdk_response.json')
        assert sdk['model']==raw['model']
        text=response_text(raw,r['provider'])
        assert (folder/'text.txt').read_text()==text
        clean=text.strip()
        if clean.startswith('```'):
            lines=clean.splitlines();assert lines[-1]=='```';clean='\n'.join(lines[1:-1])
        assert json.loads(clean)==load(folder/'parse.json')['parsed']
        request=load(folder/'request.json');body=request['json']
        if r['provider']=='openai':
            assert set(body)=={'model','input','reasoning','max_output_tokens'}
            assert body['model']==MODEL and body['reasoning']=={'effort':'medium','summary':'auto'} and body['max_output_tokens']==32000
            if r['kind']=='method1':expected=A.assemble(r['task'],r['call'],ledger=load(OUT/r['task']/f'ledger_before_call_{r["call"]}.json'))
            elif r['kind']=='method1_final':expected=A.assemble(r['task'],final_rank=True,ledger=load(OUT/r['task']/'ledger_all.json'))
            else:expected=A.assemble(r['task'],method2=True)
            actual_prompt=body['input']
            fidelity={'tag':r['tag'],'exact':actual_prompt==expected,
                      'expected_049_chars':len(expected),'actual_chars':len(actual_prompt),
                      'expected_049_o200k':tokens(expected),'actual_o200k':tokens(actual_prompt),
                      'expected_049_sha256':sha(expected.encode()),'actual_sha256':sha(actual_prompt.encode()),
                      'expected_CR_count':expected.count('\r'),'actual_CR_count':actual_prompt.count('\r')}
            if actual_prompt!=expected:
                assert actual_prompt==expected.replace('\r\n','\n').replace('\r','\n')
                fidelity['difference']='universal_newline_conversion_in_original_pilot_subprocess_capture'
                fidelity['edits']=[];j=0;i=0
                while i<len(expected):
                    if expected[i]=='\r':
                        has_lf=i+1<len(expected) and expected[i+1]=='\n'
                        fidelity['edits'].append({'expected_char':i,'actual_char':j,'from':'\r','to':'' if has_lf else '\n'})
                        if not has_lf:j+=1
                    else:
                        assert expected[i]==actual_prompt[j];j+=1
                    i+=1
                assert j==len(actual_prompt)
            input_fidelity.append(fidelity)
            # All subsequent record/usage checks refer to the prompt actually
            # sent and saved, never silently replace historical requests.
            expected=actual_prompt
            u=raw['usage'];actual=u['input_tokens'];cached=u['input_tokens_details']['cached_tokens'];output=u['output_tokens'];reasoning=u['output_tokens_details']['reasoning_tokens']
        else:
            assert set(body)=={'model','messages'} and body['model']==JUDGE
            assert len(body['messages'])==1 and body['messages'][0]['role']=='user'
            u=raw['usage'];actual=u['prompt_tokens'];cached=u.get('prompt_cache_hit_tokens',(u.get('prompt_tokens_details') or {}).get('cached_tokens'))
            output=u['completion_tokens'];reasoning=(u.get('completion_tokens_details') or {}).get('reasoning_tokens')
            expected=body['messages'][0]['content']
        assert sha(expected.encode())==r['prompt_sha256'] and tokens(expected)==r['prompt_o200k_tokens']
        assert [actual,cached,output,reasoning]==[r['usage'][k] for k in ['input_tokens','cached_input_tokens','output_tokens','reasoning_tokens']]
        assert 0<=cached<=actual and reasoning<=output
        assert abs(price(r['usage'],r['provider'],r['attempts'][0]['started_at'])['estimated_usd']-r['cost']['estimated_usd'])<1e-12
        checks['requests_raw_bodies_parses_and_usage']+=1
    pipeline=load(OUT/'pipeline_results.json')
    assert len(pipeline['judge_match'])==12 and len(pipeline['judge_stated'])==6
    for row in pipeline['judge_match']:
        point=next(p for p in points if int(p['序号'])==row['point_number'])
        if row['called']:
            final=load(OUT/row['task']/f'{row["method"]}_final_lists.json')['targets'][row['target']]
            assert row['items']==judge_items(final['items'])
            assert all(not isinstance(i['item'],dict) or 'importance' not in i['item'] for i in row['items'])
            prompt=fill_judge('judge_match.txt',{'table':row['target'],'premise':point['agent默认的前提'],'truth':point['实际要求或数据情况'],
                                                 'items':json.dumps(row['items'],ensure_ascii=False,indent=2)})
            request=load(ROOT/by_tag[row['tag']]['request_path'])['json']
            assert request['messages'][0]['content']==prompt
            assert row['result']==parsed_value(by_tag[row['tag']])
        else:
            assert row['list_status']=='not_listed' and row['result']['verdict']=='no_match'
        checks['judge_match_point_method_slots']+=1
    for row in pipeline['judge_stated']:
        point=next(p for p in points if int(p['序号'])==row['point_number'])
        prompt=fill_judge('judge_stated.txt',{'table':row['target'],'premise':point['agent默认的前提'],'truth':point['实际要求或数据情况'],
                                                'agent_text':load(OUT/row['task']/'agent_text.json')['text']})
        request=load(ROOT/by_tag[row['tag']]['request_path'])['json']
        assert request['messages'][0]['content']==prompt and row['result']==parsed_value(by_tag[row['tag']])
        checks['judge_stated_point_slots']+=1
    q=load(OUT/'quote_checks.json')
    for row in q['checks']:
        if row['status']!='checked':continue
        r=by_tag[row['tag']];body=load(ROOT/r['request_path'])['json']
        if row['field'] in ['evidence_of_dependence','alternative','evidence_in_work','source']:
            candidates=[body.get('input') or body['messages'][0]['content']]
        elif row['field']=='judge_stated.quote':candidates=[load(OUT/r['task']/'agent_text.json')['text']]
        else:
            match=next(x for x in pipeline['judge_match'] if x.get('tag')==r['tag'])
            obj=match['result'];item=next((x['item'] for x in match['items'] if x['rank']==obj.get('rank')),match['items'])
            candidates=[json.dumps(item,ensure_ascii=False,indent=2)]+[v for path,v in string_leaves(item)]
        assert row['exact']==any(row['quote'] in c for c in candidates)
        assert row['whitespace_collapsed']==any(re.sub(r'\s+',' ',row['quote']) in re.sub(r'\s+',' ',c) for c in candidates)
        checks['nonempty_whole_field_quotes_checked']+=1
    for row in load(OUT/'quote_delimiter_checks.json')['checks']:
        parent=next(x for x in q['checks'] if x['tag']==row['tag'] and x['field']==row['field'] and row['location'].startswith(x['location']+'.span['))
        begin,end=row['parent_field_chars'];assert parent['quote'][begin:end]==row['quote']
        request=load(ROOT/by_tag[row['tag']]['request_path'])['json'];prompt=request['input']
        assert row['exact']==(row['quote'] in prompt)
        assert row['whitespace_collapsed']==(collapsed(row['quote']) in collapsed(prompt))
        checks['explicit_delimiter_quotes_checked']+=1
    secrets=[(Path.home()/name).read_bytes().strip() for name in ['.openai_key','.deepseek_key']]
    scanned=[];leaks=[]
    paths=[p for p in OUT.rglob('*') if p.is_file()]+[Path(__file__)]
    note=ROOT/'notes/050_2026-11-06_小实验试跑.md'
    if note.exists():paths.append(note)
    for p in paths:
        data=p.read_bytes();scanned.append(str(p.relative_to(ROOT)))
        if any(secret and secret in data for secret in secrets):leaks.append(str(p.relative_to(ROOT)))
    assert not leaks,'Credential detected in output paths: '+repr(leaks)
    others=[]
    own={Path(__file__),note}
    for dirname in ['notes','records']:
        for p in (ROOT/dirname).rglob('*'):
            if p in own or p==PUBLIC_OUT or p.is_relative_to(PUBLIC_OUT):continue
            m=re.match(r'^(\d{3})_',p.name)
            if m:others.append(int(m[1]))
    assert max(others)==49,'Report number occupied; renumber before committing'
    store_once(OUT/'input_fidelity.json',{'strict_fidelity_passed':all(r['exact'] for r in input_fidelity),
        'reviewer_calls':len(input_fidelity),'exact_calls':sum(r['exact'] for r in input_fidelity),
        'different_calls':[r['tag'] for r in input_fidelity if not r['exact']],
        'root_cause':'Original runner used subprocess.run(text=True), converting CRLF to LF. 049 files were not changed.',
        'fix':'050 runner now captures stdout bytes and decodes UTF-8 without newline conversion.',
        'historical_requests_kept_unchanged':True,'models_not_recalled_for_fix':True,'checks':input_fidelity})
    result={'record_reconciliation_passed':True,'strict_049_input_fidelity_passed':all(r['exact'] for r in input_fidelity),
            'checks':dict(checks),'original_tracked_files_unchanged':len(state['tracked_file_sha256']),
            'number_recheck':{'number':50,'max_other_number':49,'renumbered':False},
            'credential_scan':{'files_scanned':len(scanned),'exact_key_matches':0,'keys_printed_or_saved':False},
            'calls':len(records),'estimated_usd':total_cost(),'no_extra_model_calls_during_validation':True}
    # Keep the original audit snapshot immutable. Later scans may legitimately
    # include a new report or scan file; repeated validation prints fresh facts.
    if not (OUT/'validation.json').exists():dump(OUT/'validation.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--probe',action='store_true');p.add_argument('--analyze-only',action='store_true');p.add_argument('--validate-only',action='store_true');args=p.parse_args()
    if not (OUT/'start_state.json').is_file():
        p.exit(2,'Complete private archive missing: data/050_pilot_full. Public redacted requests must not be used for token/quote/cost statistics.\n')
    # Both credentials are loaded before any saved request/response is created,
    # so all persistence paths can redact either credential defensively.
    for key in ['.openai_key','.deepseek_key']:
        secret=(Path.home()/key).read_text(encoding='utf-8').strip()
        if not secret:stop('authentication_missing_key',{'key_file':'~/'+key})
        SECRETS.append(secret)
    if args.analyze_only:
        audit_run();return
    if args.validate_only:
        validate_artifacts();return
    try:
        ledger=OUT/'impl-025/ledger_before_call_1.json'
        if not ledger.exists():dump(ledger,[])
        prompt,cmd=assemble('impl-025',1,ledger_file=ledger)
        call_api('impl-025','method1',prompt,call_number=1)
        if not args.probe:
            run_pipeline()
            audit_run()
    except StopPilot as e:
        print(json.dumps({'event':'stopped','reason':str(e),'estimated_usd':total_cost()},ensure_ascii=False),flush=True)
        if not args.probe:audit_run()


if __name__=='__main__':
    main()
