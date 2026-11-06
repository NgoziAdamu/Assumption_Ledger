"""Frozen-v2 first-batch experiment: 049 inputs, compact Excel, no judges/gold.

Commands: prepare; assemble TASK [CALL|--final-rank|--method2]; run --batch first;
analyze; publish; verify. --batch remaining is only for a later user-authorized run.
All model traffic and statistics use data/051_formal_run_full, never redacted copies.
"""
import argparse
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import hashlib
import importlib.metadata
import importlib.util
import io
import json
import logging
import os
from pathlib import Path
import random
import re
import statistics
import subprocess
import sys
import time

sys.dont_write_bytecode=True
logging.disable(logging.CRITICAL)
os.environ.pop('OPENAI_LOG',None)
import openai
from openai import OpenAI
import tiktoken

ROOT=Path(__file__).resolve().parents[1]
PUB=ROOT/'records/051_formal_run'
OUT=ROOT/'data/051_formal_run_full'
PROMPTS=ROOT/'records/051_prompts'
PREREG='bd97e3ef9cd40ab243480de5687b05ffa6e66c5e'
MODEL='gpt-6.1-sol'
BUDGET=20
SECRETS=[]
ENC=tiktoken.get_encoding('o200k_base')
spec=importlib.util.spec_from_file_location('a049_formal',ROOT/'records/049_small_exp_assemble.py')
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
REVIEW_FIELDS={'statement','about','target','evidence_of_dependence','alternative','importance','reason','updates'}
PROBLEMS_FIELDS={'problem','about','evidence_in_work','source','importance','reason'}
_COMPACT={}


def now():return datetime.now(timezone.utc).isoformat()
def sha(data):return hashlib.sha256(data).hexdigest()
def tokens(text):return len(ENC.encode(text,disallowed_special=()))


def scrub(value):
    if isinstance(value,str):
        for key in SECRETS:
            if key:value=value.replace(key,'[REDACTED_AUTH_CREDENTIAL]')
        return value
    if isinstance(value,dict):return {scrub(k) if isinstance(k,str) else k:scrub(v) for k,v in value.items()}
    if isinstance(value,list):return [scrub(v) for v in value]
    return value


def dump(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:json.dump(scrub(value),f,ensure_ascii=False,indent=2);f.write('\n')


def write(path,text):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='') as f:f.write(scrub(text))


def load(path):
    p=Path(path)
    if not p.is_absolute():p=ROOT/p
    if p==PUB or p.is_relative_to(PUB):p=OUT/p.relative_to(PUB)
    return json.loads(p.read_bytes().decode('utf-8'))


def store(path,value):
    if Path(path).exists():
        if load(path)!=scrub(value):raise ValueError('Existing formal artifact differs: '+str(path))
    else:dump(path,value)


def write_csv(path,rows):
    if not rows:return
    with Path(path).open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def freeze_check():
    audit=json.loads((PUB/'frozen_text_source_check.json').read_bytes())
    committed=subprocess.check_output(['git','show','-s','--format=%cI',PREREG],text=True).strip()
    for path,record in audit['files'].items():
        data=(ROOT/path).read_bytes();assert sha(data)==record['sha256'],path
        assert subprocess.check_output(['git','show',PREREG+':'+path])==data,path
    return {'commit':PREREG,'commit_time':committed,'models_started_after_commit':True}


def selection():
    summary=json.loads((ROOT/'records/049_small_exp_inputs/summary.json').read_bytes())
    da=sorted(t['task'] for t in summary['tasks'] if t['benchmark']=='DAComp')
    kb=sorted(t['task'] for t in summary['tasks'] if t['benchmark']=='KramaBench')
    assert len(da)==20 and len(kb)==9
    rng=random.Random(1234);chosen_da=rng.sample(da,7);chosen_kb=rng.sample(kb,3)
    selected=chosen_da+chosen_kb
    return {'seed':1234,'rule':'One random.Random(1234); sample(sorted(DAComp),7), then sample(sorted(KramaBench),3). Preserve returned sample order.',
            'DAComp':chosen_da,'KramaBench':chosen_kb,'first':selected,
            'remaining':[t for t in da+kb if t not in selected],'all':da+kb}


def colnum(address):
    m=re.fullmatch(r'([A-Z]+)([0-9]+)',address);assert m,address
    n=0
    for c in m[1]:n=n*26+ord(c)-64
    return n,int(m[2])


def cell_text(cell):
    value=cell['text'] if 'text' in cell else cell.get('raw_value')
    if value is None:return ''
    if not isinstance(value,str):raise ValueError('Unsupported non-string cell value: '+str(cell['cell']))
    if any(c in value for c in ['\r','\n','\t']):raise ValueError('Cell contains control delimiters: '+str(cell['cell']))
    return value


def build_compact_blocks():
    excerpts=json.loads((ROOT/'records/031_kramabench_docs_excerpts.json').read_bytes())
    sheets=json.loads((ROOT/'records/031_kramabench_docs_sheets.json').read_bytes())
    lookup={(s['path'],s['name']):s for s in sheets};replacements={};checks=[];cells_checked=0
    for meta in excerpts:
        if meta['kind'] not in ['excel_first_10_physical_rows','excel_all_rows']:continue
        path=ROOT/f'records/031_kramabench_docs/{meta["domain"]}.md';text=path.read_bytes().decode('utf-8')
        header=re.search(r'<!-- excerpt:'+re.escape(meta['id'])+r' chars:(\d+) -->\n(`{3,})jsonl\n',text)
        assert header,meta['id'];body=text[header.end():header.end()+int(header[1])]
        assert sha(body.encode())==meta['text_sha256'] and len(body)==meta['chars']
        rows=[json.loads(line) for line in body.splitlines() if line]
        rel=str(Path(meta['source']).relative_to(ROOT/'data/kramabench/data'))
        independent=lookup[(rel,meta['sheet'])];assert rows==independent['rows']
        width=max((colnum(c['cell'])[0] for row in rows for c in row['cells']),default=0)
        lines=[];row_proofs=[]
        for row in rows:
            fields=['']*width;occupied=set()
            for cell in row['cells']:
                column,rn=colnum(cell['cell']);assert rn==row['row'] and column not in occupied
                occupied.add(column);fields[column-1]=cell_text(cell)
            line=str(row['row'])+'\t'+'\t'.join(fields);lines.append(line)
            # Independent source metadata verifies exact column text and ordered
            # occurrence in the same logical/physical row, including sparse gaps.
            expected=next(r for r in independent['rows'] if r['row']==row['row'])
            decoded=line.split('\t');assert decoded[0]==str(row['row']) and len(decoded)==width+1
            cursor=len(decoded[0])+1;positions=[]
            for cell in sorted(expected['cells'],key=lambda c:colnum(c['cell'])[0]):
                column,_=colnum(cell['cell']);value=cell_text(cell)
                assert decoded[column]==value
                start=len(decoded[0])+1+sum(len(v)+1 for v in fields[:column-1])
                assert line[start:start+len(value)]==value and start>=cursor
                cursor=start+len(value);positions.append({'cell':cell['cell'],'chars':[start,cursor],
                    'text_sha256':sha(value.encode()),'empty':value==''});cells_checked+=1
            row_proofs.append({'row':row['row'],'row_sha256':sha(line.encode()),'cells':positions})
        compact='\n'.join(lines)
        closing=re.search(r'<!-- /excerpt:'+re.escape(meta['id'])+r' -->',text[header.end()+int(header[1]):])
        assert closing
        end=header.end()+int(header[1])+closing.end()
        original=text[header.start():end]
        fence=header[2]
        replacement=f'<!-- excerpt:{meta["id"]} chars:{len(compact)} -->\n{fence}tsv\n{compact}\n{fence}\n<!-- /excerpt:{meta["id"]} -->'
        replacements[meta['id']]={'original':original,'replacement':replacement}
        checks.append({'id':meta['id'],'path':rel,'sheet':meta['sheet'],'kind':meta['kind'],
                       'row_count':len(rows),'column_width':width,'cells':sum(len(r['cells']) for r in rows),
                       'before_chars':len(body),'after_chars':len(compact),'before_sha256':sha(body.encode()),
                       'after_sha256':sha(compact.encode()),'rows':row_proofs,'passed':True})
    assert len(checks)==32 and cells_checked==10921
    return replacements,checks


def compact_section(section):
    text=A.text_ref(section['ref'])
    if not _COMPACT:return text,[]
    changed=[]
    for bid,r in _COMPACT.items():
        if r['original'] in text:
            assert text.count(r['original'])==1;text=text.replace(r['original'],r['replacement'],1);changed.append(bid)
    return text,changed


def fill(name,values):
    template=(PROMPTS/name).read_bytes().decode('utf-8')
    frozen=json.loads((PUB/'frozen_text_source_check.json').read_bytes())['files']['records/051_prompts/'+name]
    assert sha(template.encode())==frozen['sha256']
    # JSON examples contain ordinary braces: replace only explicitly named
    # placeholders once. Inserted source text is never treated as a template.
    return re.sub(r'\{(task|material_index|spec_sections|ledger|steps|trajectory)\}',lambda m:values[m[1]],template)


def assembled(task,call=None,final_rank=False,method2=False,ledger=None,compact=True):
    m=A.manifest(task)
    if final_rank:return fill('method1_final_rank_v2.txt',{'task':A.text_ref(m['fixed']['prompt']),'ledger':A.ledger_text(ledger)})
    c=m['method2'] if method2 else next(c for c in m['calls'] if c['call']==call and c['kind']=='regular')
    if c['pending_decision_ids']:raise ValueError('Unresolved 049 rules: '+', '.join(c['pending_decision_ids']))
    # Obtain the original five-part body directly from the immutable 049 code;
    # only the explicitly authorized Excel formatting and frozen template differ.
    values=A.parts(m,c['action_ids'],c['section_ids']);sections={s['id']:s for s in m['sections']}
    specs=[]
    for sid in c['section_ids']:
        sec=sections[sid];text=compact_section(sec)[0] if compact else A.text_ref(sec['ref'])
        specs.append(A.wrap(sid,text))
    values['spec_sections']=''.join(specs);values['ledger']=A.ledger_text(ledger)
    if method2:values['trajectory']=values.pop('steps')
    return fill('method2_review_v2.txt' if method2 else 'method1_review_v2.txt',values)


def prepare():
    global _COMPACT
    OUT.mkdir(parents=True,exist_ok=True);frozen=freeze_check()
    store(OUT/'start_state.json',json.loads((PUB/'start_state.json').read_bytes()))
    try:_COMPACT,checks=build_compact_blocks()
    except Exception as e:
        dump(OUT/'STOP.json',{'reason':'excel_compact_verification_failed','time':now(),'error_type':type(e).__name__,'error':str(e)})
        raise
    store(OUT/'excel_compact_validation.json',{'passed':True,'blocks':32,'rows':327,'cells':10921,
         'rules':'Row number, then tab-separated column values; width=max observed column in preview; text else raw_value string, null=empty; no formatting/truncation; all cell fields checked exactly in order.',
         'checks':checks})
    store(OUT/'compact_blocks.json',_COMPACT)
    selected=selection();store(OUT/'selection.json',selected);store(OUT/'preregistration.json',frozen)
    rows=[];tasks=[]
    for task in selected['all']:
        m=A.manifest(task);before=[];after=[];used_blocks=set()
        for c in m['calls']:
            if c['kind']=='final':continue
            original=assembled(task,c['call'],compact=False);new=assembled(task,c['call'],compact=True)
            ids={sid for sid in c['section_ids']}
            for sec in m['sections']:
                if sec['id'] in ids:used_blocks.update(compact_section(sec)[1])
            nb,na=tokens(original),tokens(new);before.append(nb);after.append(na)
            rows.append({'task':task,'method':'method1','call':c['call'],'rules':'|'.join(c['rules']),
                         'before_excel_tokens':nb,'after_excel_tokens':na,'after_sha256':sha(new.encode())})
        original=assembled(task,method2=True,compact=False);new=assembled(task,method2=True,compact=True)
        rows.append({'task':task,'method':'method2','call':'','rules':'','before_excel_tokens':tokens(original),
                     'after_excel_tokens':tokens(new),'after_sha256':sha(new.encode())})
        tasks.append({'task':task,'benchmark':m['benchmark'],'ordinary_calls':len(after),'final_rank_calls':1,
                      'excel_affected':bool(used_blocks),'excel_blocks':sorted(used_blocks),
                      'method1_before_sum':sum(before),'method1_after_sum':sum(after),
                      'method1_before_median':statistics.median(before),'method1_after_median':statistics.median(after),
                      'method1_before_max':max(before),'method1_after_max':max(after),
                      'method2_before_tokens':tokens(original),'method2_after_tokens':tokens(new)})
    write_csv(OUT/'input_token_counts.csv',rows)
    store(OUT/'preparation_summary.json',{'frozen':frozen,'selection':selected,'all_29_tasks':tasks,
         'excel_affected_tasks':[t['task'] for t in tasks if t['excel_affected']],
         'counts':'Full frozen-v2 prompts; empty ledger=(none); before/after differ only Excel rendering.',
         'model_calls_in_preparation':0,'database_queries':0})
    print(json.dumps({'event':'prepared','excel_cells_checked':10921,'affected_tasks':[t['task'] for t in tasks if t['excel_affected']],
                      'first_batch':selected['first'],'remaining_count':len(selected['remaining'])},ensure_ascii=False),flush=True)


def load_prepared():
    global _COMPACT
    freeze_check()
    if not (OUT/'preparation_summary.json').exists():raise ValueError('Run prepare and pass Excel verification first.')
    assert load(OUT/'excel_compact_validation.json')['passed']
    _COMPACT=load(OUT/'compact_blocks.json')
    regenerated,checks=build_compact_blocks()
    assert regenerated==_COMPACT
    assert checks==load(OUT/'excel_compact_validation.json')['checks']


def baseline(task,kind,call):
    if kind=='method1_final':return None
    for r in csv.DictReader((OUT/'input_token_counts.csv').open()):
        if r['task']==task and r['method']==kind and (kind!='method1' or int(r['call'])==call):return int(r['after_excel_tokens'])
    return None


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


class StopFormal(Exception):
    pass


def stop(reason,details):
    if not (OUT/'STOP.json').exists():dump(OUT/'STOP.json',{'time':now(),'reason':reason,'details':details,'estimated_usd':total_cost()})
    raise StopFormal(reason)


def fatal_error(status,body):
    text=json.dumps(body,ensure_ascii=False).lower() if body is not None else ''
    if status in [401,403]:return 'authentication_or_access_denied'
    if status in [400,404,422] and any(s in text for s in ['model_not_found','model not found','does not exist',
        'model is not available','unsupported model','model_not_available','invalid model','not have access to model',
        'model is not supported','model_not_supported']):return 'model_missing_or_rejected'
    return None


def call_api(task,kind,prompt,call_number=None,point_id=None,method=None):
    assert kind in ['method1','method1_final','method2'], 'No judges are permitted.'
    if (OUT/'STOP.json').exists():raise StopFormal(load(OUT/'STOP.json')['reason'])
    if total_cost()>BUDGET:stop('estimated_cost_exceeds_20_usd',{})
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
    saved_prompt=folder/'assembled_prompt.txt'
    if not saved_prompt.exists():write(saved_prompt,prompt)
    assert saved_prompt.read_bytes()==prompt.encode('utf-8')
    prompt=saved_prompt.read_bytes().decode('utf-8')
    provider='openai'
    model=MODEL
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
            'prompt_o200k_tokens':tokens(prompt),'baseline_v2_none_tokens':old_est,
            'actual_input_to_v2_none_ratio':u['input_tokens']/old_est if u['input_tokens'] is not None and old_est else None,
            'actual_input_to_current_o200k_ratio':u['input_tokens']/tokens(prompt) if u['input_tokens'] is not None else None,
            'cached_input_fraction':u['cached_input_tokens']/u['input_tokens'] if u['input_tokens'] and u['cached_input_tokens'] is not None else None,
            'reasoning_item_count':reasoning_items,'has_reasoning_summary_text':any(s for s in summaries),
            'reasoning_summary_texts':summaries,'request_path':str((folder/'request.json').relative_to(ROOT)),
            'response_path':str((folder/f'attempt_{attempts[-1]["attempt"]}_response.json').relative_to(ROOT)) if raw else None,
            'parse_path':str((folder/'parse.json').relative_to(ROOT)),'prompt_sha256':sha(prompt.encode()),
            'input_read_mode':'read_bytes().decode(utf-8); CR/LF preserved','script_sha256_at_call':sha(Path(__file__).read_bytes()),'error':last_error if raw is None else None,
            'billing_uncertainty':'失败的网络/5xx尝试没有usage；未把缺失计费用量称为确定免费。' if any(not a['success'] for a in attempts) else None}
    dump(folder/'record.json',record)
    print(json.dumps({'event':'call_finished','task':task,'kind':kind,'call':call_number,'api_success':record['api_success'],
                      'parse_success':record['parse_success'],'status':status,'cost_usd':cost['estimated_usd'],
                      'cumulative_estimated_usd':total_cost()},ensure_ascii=False),flush=True)
    if raw is None:
        fatal=fatal_error((last_error or {}).get('http_status'),(last_error or {}).get('body'))
        if fatal:stop(fatal,{'tag':tag,'error':last_error})
    if total_cost()>BUDGET:stop('estimated_cost_exceeds_20_usd',{'tag':tag})
    return load(folder/'record.json')


def parsed_value(record):
    p=load(ROOT/record['parse_path'])
    return p.get('parsed') if p.get('success') else None


def ledger_additions(value,number):
    issues=[];result=[]
    if not isinstance(value,dict) or not isinstance(value.get('premises'),list):
        return [],[{'kind':'method1_premises_not_array','call':number}],None
    for index,item in enumerate(value['premises'],1):
        identity={'id':f'c{number}-{index}','call':number}
        if isinstance(item,dict):
            entry=dict(item)
            collisions={k:entry[k] for k in identity if k in entry}
            if collisions:entry['_original_identity_fields']=collisions;issues.append({'kind':'identity_collision','call':number,'index':index})
            entry.update(identity)
        else:
            entry={**identity,'_non_object_output':item};issues.append({'kind':'non_object_premise','call':number,'index':index})
        result.append(entry)
    return result,issues,value.get('fewer')


def local_input_failure(task,kind,number,error):
    tag=f'{task}_{kind}'+(f'_{number}' if number is not None else '');folder=OUT/'calls'/tag
    if (folder/'record.json').exists():return load(folder/'record.json')
    folder.mkdir(parents=True,exist_ok=True);dump(folder/'parse.json',{'success':False,'error':'input_assembly_failed'})
    record={'tag':tag,'task':task,'kind':kind,'call':number,'started_at':now(),'finished_at':now(),'attempts':[],
        'api_success':False,'status':'input_assembly_failed','completed':False,'truncated':None,'parse_success':False,
        'parse_path':str((folder/'parse.json').relative_to(ROOT)),'request_path':None,
        'usage':{k:None for k in ['input_tokens','cached_input_tokens','output_tokens','reasoning_tokens']},
        'cost':{'estimated_usd':0,'long_input_price_unverified':False},'error':scrub(str(error)),
        'has_reasoning_summary_text':False,'cached_input_fraction':None,'prompt_o200k_tokens':None,
        'actual_input_to_current_o200k_ratio':None,'baseline_v2_none_tokens':None}
    dump(folder/'record.json',record);return record


def run_batch(batch):
    load_prepared();chosen=load(OUT/'selection.json')[batch]
    if (OUT/f'batch_{batch}_complete.json').exists():
        print(json.dumps({'event':'batch_already_complete','batch':batch,'no_api_calls':True}),flush=True);return
    for name in ['.openai_key','.deepseek_key']:
        p=Path.home()/name
        if p.exists():SECRETS.append(p.read_bytes().decode().strip())
    store(OUT/'environment.json',{'python':sys.version,'openai_sdk':importlib.metadata.version('openai'),
           'tiktoken':importlib.metadata.version('tiktoken'),'model':MODEL,'reasoning':{'effort':'medium','summary':'auto'},
           'max_output_tokens':32000,'budget_usd':BUDGET,'no_judges_or_gold':True})
    for task in chosen:
        folder=OUT/'tasks'/task;folder.mkdir(parents=True,exist_ok=True)
        if (folder/'complete.json').exists():continue
        if not (folder/'started.json').exists():dump(folder/'started.json',{'task':task,'started_at':now(),'batch':batch})
        ledger=[];reviews=[];issues=[]
        for c in A.manifest(task)['calls']:
            if c['kind']=='final':continue
            number=c['call'];store(folder/f'ledger_before_call_{number}.json',ledger)
            # Reload serialized JSON using bytes, as the future assembler CLI does.
            previous=load(folder/f'ledger_before_call_{number}.json')
            try:prompt=assembled(task,number,ledger=previous)
            except Exception as e:record=local_input_failure(task,'method1',number,e)
            else:record=call_api(task,'method1',prompt,call_number=number)
            reviews.append(record['tag'])
            value=parsed_value(record)
            if record['parse_success']:
                added,new_issues,fewer=ledger_additions(value,number);ledger.extend(added);issues.extend(new_issues)
                store(folder/f'fewer_call_{number}.json',{'call':number,'fewer':fewer})
            store(folder/f'ledger_after_call_{number}.json',ledger)
        store(folder/'ledger_all.json',ledger)
        finals={}
        for kind in ['method1_final','method2']:
            try:
                prompt=assembled(task,final_rank=kind=='method1_final',method2=kind=='method2',
                                 ledger=load(folder/'ledger_all.json') if kind=='method1_final' else None)
            except Exception as e:record=local_input_failure(task,kind,None,e)
            else:record=call_api(task,kind,prompt)
            finals[kind]=record['tag']
        end=now();started=load(folder/'started.json')['started_at']
        store(folder/'complete.json',{'task':task,'review_calls':reviews,'ledger_items':len(ledger),
              'outputs':finals,'issues_for_claude':issues,'started_at':started,'finished_at':end,
              'wall_seconds':(datetime.fromisoformat(end)-datetime.fromisoformat(started)).total_seconds()})
        print(json.dumps({'event':'task_finished','task':task,'ledger_items':len(ledger),'cumulative_usd':total_cost()},ensure_ascii=False),flush=True)
    store(OUT/f'batch_{batch}_complete.json',{'tasks':chosen,'finished_at':now(),'estimated_usd':total_cost()})



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

def final_summary(task,kind,value,ledger):
    result={'task':task,'kind':kind,'raw_key_counts':{},'resolved_lists':{},'unknown_ids':[],
            'fewer_reasons':{},'issues':[],'krama_aggregate_count':None}
    if not isinstance(value,dict):result['issues'].append({'kind':'root_not_object'});return result
    by_id={x['id']:x for x in ledger};id_occurrences=defaultdict(list)
    for key,body in value.items():
        entries=body.get('items') if kind=='method2' and isinstance(body,dict) else body
        if kind=='method2':result['fewer_reasons'][key]=body.get('fewer_reason') if isinstance(body,dict) else None
        if not isinstance(entries,list):
            result['issues'].append({'kind':'table_items_not_array','key':key});result['raw_key_counts'][key]=None;continue
        result['raw_key_counts'][key]=len(entries);rows=[]
        for rank,item in enumerate(entries,1):
            if kind=='method1_final':
                pid=item.get('id') if isinstance(item,dict) else None
                if isinstance(pid,str):id_occurrences[pid].append({'key':key,'rank':rank})
                if not isinstance(pid,str) or pid not in by_id:result['unknown_ids'].append({'key':key,'rank':rank,'id':pid});continue
                rows.append(by_id[pid])
            else:rows.append(item)
        result['resolved_lists'][key]=rows
    result['resolved_key_counts']={key:len(items) for key,items in result['resolved_lists'].items()}
    result['raw_total']=sum(n for n in result['raw_key_counts'].values() if n is not None)
    result['resolved_total']=sum(result['resolved_key_counts'].values())
    result['repeated_ledger_id_occurrences']={pid:locations for pid,locations in id_occurrences.items() if len(locations)>1}
    if kind=='method1_final':result['unique_resolved_ledger_ids']=len({item['id'] for items in result['resolved_lists'].values() for item in items})
    manifest=A.manifest(task)
    if manifest['benchmark']=='DAComp':
        sections={s['id']:s for s in manifest['sections']}
        proxy=list(dict.fromkeys(sections[sid]['name'].rsplit('.',1)[-1].lower() for sid in manifest['method2']['section_ids']))
        returned=[{'original_key':k,'normalized_key':k.rsplit('.',1)[-1].lower(),'count':n} for k,n in result['raw_key_counts'].items()]
        present={r['normalized_key'] for r in returned}
        result['coverage_proxy']={'definition':'Unique method2 contract-section table names; literal output key present, including an empty list. Schema prefix removed, lowercase, exact match. Not actual write detection.',
                'tables':proxy,'denominator':len(proxy),'present':[t for t in proxy if t in present],
                'numerator':sum(t in present for t in proxy),'ratio':sum(t in present for t in proxy)/len(proxy) if proxy else None,
                'key_mapping':returned,'unmatched_keys':[r['original_key'] for r in returned if r['normalized_key'] not in proxy],
                'nonempty_numerator':sum(any(r['normalized_key']==t and (r['count'] or 0)>0 for r in returned) for t in proxy)}
        result['coverage_proxy']['nonempty_ratio']=result['coverage_proxy']['nonempty_numerator']/len(proxy) if proxy else None
    else:
        lists=result['resolved_lists']
        if len(value)<=1:result['krama_aggregate_count']=sum(map(len,lists.values()))
        else:
            collected=[];bad=[]
            for ki,(key,items) in enumerate(lists.items()):
                for ri,item in enumerate(items):
                    importance=item.get('importance') if isinstance(item,dict) else None
                    if not isinstance(importance,(int,float)) or isinstance(importance,bool):bad.append([key,ri+1])
                    else:collected.append((-importance,ki,ri,item))
            if bad:result['issues'].append({'kind':'krama_sort_undefined_importance','locations':bad})
            else:
                collected.sort(key=lambda row:row[:3]);result['krama_aggregate_count']=min(10,len(collected))
                result['krama_aggregate_items']=[r[3] for r in collected[:10]]
        result['krama_rule']='050: one key preserves its list; multiple keys importance desc, key order, within-key order, top 10. Raw per-key counts separately retained.'
    return result


def audit_format(record,value):
    issues=[]
    def issue(kind,**kwargs):issues.append({'tag':record['tag'],'kind':kind,**kwargs})
    def fields(item,expected,where):
        if not isinstance(item,dict):issue('item_not_object',location=where);return
        missing=sorted(expected-set(item))
        if missing:issue('missing_fields',location=where,fields=missing)
    if not record['parse_success']:return issues
    if not isinstance(value,dict):issue('root_not_object');return issues
    if record['kind']=='method1':
        fields(value,{'premises','fewer'},'root');entries=value.get('premises');fewer=value.get('fewer')
        if not isinstance(entries,list):issue('premises_not_array');return issues
        groups=Counter()
        for i,item in enumerate(entries,1):
            fields(item,REVIEW_FIELDS,f'premises[{i}]')
            if isinstance(item,dict):groups[json.dumps(item.get('target'),ensure_ascii=False)]+=1
        for target,n in groups.items():
            if n>5:issue('more_than_5_for_literal_target',target=target,count=n)
        if not isinstance(fewer,list):issue('fewer_not_array')
        else:
            for i,item in enumerate(fewer,1):fields(item,{'target','count','reason'},f'fewer[{i}]')
    else:
        for key,body in value.items():
            if record['kind']=='method2':fields(body,{'items','fewer_reason'},key)
            entries=body.get('items') if record['kind']=='method2' and isinstance(body,dict) else body
            if not isinstance(entries,list):issue('items_not_array',key=key);continue
            if len(entries)>10:issue('more_than_10',key=key,count=len(entries))
            for i,item in enumerate(entries,1):fields(item,PROBLEMS_FIELDS if record['kind']=='method2' else {'id','merged','reason'},f'{key}[{i}]')
    return issues


def records_all():
    return sorted([load(p) for p in (OUT/'calls').glob('*/record.json')],key=lambda r:r['started_at'])


def analyze():
    load_prepared();records=records_all();calls=[];quotes=[];formats=[];reviews=defaultdict(list);tasks=[]
    selected=load(OUT/'selection.json')['first'];by_tag={r['tag']:r for r in records}
    for r in records:
        assert r['kind'] in ['method1','method1_final','method2']
        value=parsed_value(r);formats.extend(audit_format(r,value));u=r['usage']
        if r['status']=='input_assembly_failed':formats.append({'tag':r['tag'],'kind':'input_assembly_failed','error':r['error']})
        calls.append({'task':r['task'],'type':r['kind'],'call':r['call'],'tag':r['tag'],
            'api_success':r['api_success'],'completed':r['completed'],'parse_success':r['parse_success'],'status':r['status'],
            'truncated':r['truncated'],'attempts':len(r['attempts']),'started_at':r['started_at'],'finished_at':r['finished_at'],
            'wall_seconds':(datetime.fromisoformat(r['finished_at'])-datetime.fromisoformat(r['started_at'])).total_seconds(),
            **{k:u[k] for k in ['input_tokens','cached_input_tokens','output_tokens','reasoning_tokens']},
            'estimated_usd':r['cost']['estimated_usd'],'long_input_price_unverified':r['cost']['long_input_price_unverified'],
            'cached_input_fraction':r['cached_input_fraction'],'prompt_o200k_tokens':r['prompt_o200k_tokens'],
            'actual_input_to_current_o200k_ratio':r['actual_input_to_current_o200k_ratio'],
            'baseline_v2_none_tokens':r['baseline_v2_none_tokens'],'has_reasoning_summary_text':r['has_reasoning_summary_text']})
        if not isinstance(value,dict):continue
        prompt=load(ROOT/r['request_path'])['json']['input']
        if r['kind']=='method1':
            entries=value.get('premises');entries=entries if isinstance(entries,list) else []
            counts=Counter(json.dumps(i.get('target'),ensure_ascii=False) for i in entries if isinstance(i,dict))
            reviews[r['task']].append({'call':r['call'],'rules':next(c['rules'] for c in A.manifest(r['task'])['calls'] if c['call']==r['call']),
                'premises_count':len(entries),'literal_target_count':len(counts),'target_counts':dict(counts),
                'fewer':value.get('fewer'),'zero_items':len(entries)==0})
            groups=[('premises',entries)]
        elif r['kind']=='method2':groups=[(key,body.get('items',[]) if isinstance(body,dict) else []) for key,body in value.items()]
        else:continue
        for key,entries in groups:
            if not isinstance(entries,list):continue
            for index,item in enumerate(entries,1):
                if not isinstance(item,dict):continue
                evidence='evidence_of_dependence' if r['kind']=='method1' else 'evidence_in_work'
                other='alternative' if r['kind']=='method1' else 'source'
                base={'tag':r['tag'],'task':r['task'],'method':r['kind'],'call':r['call'],'key':key,'item':index}
                quotes.append(quote_check(item.get(evidence),[prompt],f'{key}[{index}].{evidence}','complete unredacted actual request',base|{'field':evidence,'mode':'whole_field'}))
                source=item.get(other)
                if source is None:
                    quotes.append(base|{'field':other,'mode':'quoted_parts_only','status':'null_not_applicable','quote':None,'exact':None,'whitespace_collapsed':None})
                elif not isinstance(source,str):
                    quotes.append(base|{'field':other,'mode':'quoted_parts_only','status':'non_string_not_checked','quote':source,'exact':None,'whitespace_collapsed':None})
                else:
                    spans=delimiter_spans(source)
                    if not spans:quotes.append(base|{'field':other,'mode':'quoted_parts_only','status':'未给出原文','quote':source,'exact':None,'whitespace_collapsed':None})
                    for si,span in enumerate(spans,1):
                        quotes.append(quote_check(span['text'],[prompt],f'{key}[{index}].{other}.quote[{si}]','complete unredacted actual request',base|{'field':other,'mode':'quoted_parts_only','delimiter':span['delimiter']}))
    for task in selected:
        folder=OUT/'tasks'/task;complete=load(folder/'complete.json') if (folder/'complete.json').exists() else None
        ledger=load(folder/'ledger_all.json') if (folder/'ledger_all.json').exists() else []
        finals={}
        for kind in ['method1_final','method2']:
            record=by_tag.get(task+'_'+kind)
            finals[kind]=final_summary(task,kind,parsed_value(record),ledger) if record else None
        task_calls=[c for c in calls if c['task']==task]
        tasks.append({'task':task,'benchmark':A.manifest(task)['benchmark'],'finished':bool(complete),
            'ordinary_calls_planned':sum(c['kind']=='regular' for c in A.manifest(task)['calls']),
            'ordinary_calls_recorded':sum(c['type']=='method1' for c in task_calls),'reviews':reviews[task],
            'ledger_count':len(ledger),'zero_reviews':[r for r in reviews[task] if r['zero_items']],
            'distinct_literal_targets_across_reviews':len({target for r in reviews[task] for target in r['target_counts']}),
            'finals':finals,'cost_usd':sum(c['estimated_usd'] or 0 for c in task_calls),
            'wall_seconds':complete['wall_seconds'] if complete else None,'issues':complete['issues_for_claude'] if complete else []})
    group=[]
    for field in ['evidence_of_dependence','alternative','evidence_in_work','source']:
        q=[x for x in quotes if x['field']==field];checked=[x for x in q if x['status']=='checked']
        parents=defaultdict(list)
        for x in q:parents[(x['tag'],x['key'],x['item'])].append(x)
        checked_parents=[rows for rows in parents.values() if all(x['status']=='checked' for x in rows)]
        group.append({'field':field,'entries_or_quote_spans':len(q),'checked':len(checked),'exact':sum(x['exact'] for x in checked),
            'whitespace_collapsed':sum(x['whitespace_collapsed'] for x in checked),'statuses':dict(Counter(x['status'] for x in q)),
            'parent_fields_total':len(parents),'parent_fields_with_checkable_quotes':len(checked_parents),
            'parent_fields_all_exact':sum(all(x['exact'] for x in rows) for rows in checked_parents),
            'parent_fields_all_whitespace_collapsed':sum(all(x['whitespace_collapsed'] for x in rows) for rows in checked_parents)})
    coverage={}
    for kind in ['method1_final','method2']:
        ps=[t['finals'][kind]['coverage_proxy'] for t in tasks if t['finals'][kind] and 'coverage_proxy' in t['finals'][kind]]
        denominator=sum(p['denominator'] for p in ps);numerator=sum(p['numerator'] for p in ps)
        coverage[kind]={'numerator':numerator,'denominator':denominator,'ratio':numerator/denominator if denominator else None,
                        'nonempty_numerator':sum(p['nonempty_numerator'] for p in ps),
                        'nonempty_ratio':sum(p['nonempty_numerator'] for p in ps)/denominator if denominator else None}
    pilot=[]
    for task in ['impl-025','legal-hard-18']:
        if task not in selected:continue
        base=ROOT/'data/050_pilot_full'
        old=[]
        for p in (base/'calls').glob(task+'_method1_*/parse.json'):
            if '_final' in p.parent.name:continue
            data=json.loads(p.read_bytes());v=data.get('parsed')
            old.append({'call':int(p.parent.name.rsplit('_',1)[1]),'premises_count':len(v) if isinstance(v,list) else None})
        old.sort(key=lambda r:r['call']);old_final={}
        for kind in ['method1_final','method2']:
            p=base/'calls'/(task+'_'+kind)/'parse.json';v=json.loads(p.read_bytes()).get('parsed') if p.exists() else None
            old_final[kind]={k:len(items) for k,items in v.items()} if isinstance(v,dict) else None
        pilot.append({'task':task,'050_reviews':old,'050_final_key_counts':old_final,
                      '051_reviews':reviews[task],'note':'Only model response counts read. No judge records or known-error files read. 050 legal inputs had documented CRLF issue.'})
    aggregate={'tasks_planned':10,'tasks_completed':sum(t['finished'] for t in tasks),'calls':len(calls),
        'ordinary_calls':sum(c['type']=='method1' for c in calls),'final_rank_calls':sum(c['type']=='method1_final' for c in calls),
        'method2_calls':sum(c['type']=='method2' for c in calls),'premises_total':sum(r['premises_count'] for rs in reviews.values() for r in rs),
        'sum_literal_target_counts_across_reviews':sum(r['literal_target_count'] for rs in reviews.values() for r in rs),
        'distinct_task_and_literal_target_pairs':sum(t['distinct_literal_targets_across_reviews'] for t in tasks),
        'zero_reviews':sum(r['zero_items'] for rs in reviews.values() for r in rs),'coverage_proxy':coverage,
        'fewer_entries_total':sum(len(r['fewer']) for rs in reviews.values() for r in rs if isinstance(r['fewer'],list)),
        'final_raw_totals':{kind:sum(t['finals'][kind].get('raw_total',0) for t in tasks if t['finals'][kind]) for kind in ['method1_final','method2']},
        'final_resolved_totals':{kind:sum(t['finals'][kind].get('resolved_total',0) for t in tasks if t['finals'][kind]) for kind in ['method1_final','method2']},
        'krama_aggregate_totals':{kind:sum(t['finals'][kind].get('krama_aggregate_count') or 0 for t in tasks if t['benchmark']=='KramaBench' and t['finals'][kind]) for kind in ['method1_final','method2']},
        **{field:sum(c[field] or 0 for c in calls) for field in ['input_tokens','cached_input_tokens','output_tokens','reasoning_tokens','estimated_usd']},
        'api_success':sum(c['api_success'] for c in calls),'parse_success':sum(c['parse_success'] for c in calls),
        'truncated':sum(bool(c['truncated']) for c in calls),'reasoning_summaries':sum(c['has_reasoning_summary_text'] for c in calls)}
    for name,value in [('call_statistics.json',calls),('quote_checks.json',quotes),('format_issues.json',formats),
                       ('task_statistics.json',tasks),('quote_summary.json',group),('pilot_count_comparison.json',pilot),('aggregate_statistics.json',aggregate)]:
        store(OUT/name,value)
    write_csv(OUT/'call_statistics.csv',calls)
    print(json.dumps({'event':'analyzed','aggregate':aggregate,'quote_summary':group},ensure_ascii=False),flush=True)


SECRET_PATTERNS=[
    ('TWILIO_SID',re.compile(rb'AC[0-9a-fA-F]{32}')),
    ('OPENAI_LIKE_KEY',re.compile(rb'sk-(?:proj-|svcacct-)[A-Za-z0-9_-]{24,}|(?<![A-Za-z0-9_-])sk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}(?![A-Za-z0-9_-])')),
    ('DEEPSEEK_LIKE_KEY',re.compile(rb'(?<![A-Za-z0-9_-])sk-[0-9a-fA-F]{32}(?![A-Za-z0-9_-])')),
    ('GITHUB_TOKEN',re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})')),
    ('AWS_ACCESS_KEY',re.compile(rb'(?:AKIA|ASIA)[A-Z0-9]{16}')),
    ('GOOGLE_API_KEY',re.compile(rb'AIza[A-Za-z0-9_-]{35}')),
    ('SLACK_TOKEN',re.compile(rb'xox[baprs]-[A-Za-z0-9-]{20,}')),
    ('PRIVATE_KEY',re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'))]


def credentials():
    values=[]
    for name in ['.openai_key','.deepseek_key']:
        p=Path.home()/name
        if p.exists():values.append(p.read_bytes().strip())
    return [v for v in values if v]


def secret_hits(data):
    return [(kind,m.group(0)) for kind,pattern in SECRET_PATTERNS for m in pattern.finditer(data)]


def publish():
    assert (OUT/'batch_first_complete.json').exists() or (OUT/'STOP.json').exists()
    assert (OUT/'aggregate_statistics.json').exists()
    for file in OUT.rglob('*'):
        if file.is_file():
            b=file.read_bytes();assert not any(key in b for key in credentials()),str(file)
    # Retain the 050 SID placeholder when the exact same value recurs. The map
    # itself is private. All other substitutions replace only matched values.
    previous=ROOT/'data/050_pilot_full/private_sid_mapping.json';mapping={}
    if previous.exists():
        old=json.loads(previous.read_bytes())['mapping']
        if isinstance(old,dict):
            for key,value in old.items():
                if key.startswith('AC'):mapping[key.encode()]=value.encode()
                elif isinstance(value,str) and value.startswith('AC'):mapping[value.encode()]=key.encode()
        elif isinstance(old,list):
            for row in old:
                if isinstance(row,dict):
                    raw=row.get('original') or row.get('value');placeholder=row.get('placeholder')
                    if raw and placeholder:mapping[raw.encode()]=placeholder.encode()
    found=defaultdict(set)
    for p in OUT.rglob('*'):
        if p.is_file() and p.name not in ['private_redaction_mapping.json']:
            for kind,value in secret_hits(p.read_bytes()):found[kind].add(value)
    for kind,values in sorted(found.items()):
        used={v for v in mapping.values()};index=1
        for value in sorted(values):
            if value in mapping:continue
            while f'[REDACTED_{kind}_{index}]'.encode() in used:index+=1
            placeholder=f'[REDACTED_{kind}_{index}]'.encode();mapping[value]=placeholder;used.add(placeholder);index+=1
    mapping_json={k.decode():v.decode() for k,v in mapping.items()}
    store(OUT/'private_redaction_mapping.json',mapping_json)
    excluded={'private_redaction_mapping.json'};manifest=[];changed=[]
    for p in sorted(OUT.rglob('*')):
        if not p.is_file() or p.name in excluded:continue
        relative=p.relative_to(OUT);target=PUB/relative;full=p.read_bytes();public=full;counts={}
        for value,placeholder in mapping.items():
            count=public.count(value)
            if count:counts[placeholder.decode()]=count;public=public.replace(value,placeholder)
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():assert target.read_bytes()==public,str(target)
        else:target.write_bytes(public)
        manifest.append({'full_path':str(p.relative_to(ROOT)),'public_path':str(target.relative_to(ROOT)),
                         'bytes':len(full),'sha256':sha(full),'public_sha256':sha(public)})
        if counts:changed.append({'full_path':str(p.relative_to(ROOT)),'public_path':str(target.relative_to(ROOT)),
            'replacements':counts,'total_replacements':sum(counts.values()),'full_sha256':sha(full),'public_sha256':sha(public)})
    metadata={'full_archive':str(OUT.relative_to(ROOT)),'git_ignored':True,'files':manifest,
              'statistics_basis':'All quote, token, count and cost statistics use the unredacted archive.'}
    redaction={'full_archive':str(OUT.relative_to(ROOT)),'unique_values_in_this_archive':sum(len(v) for v in found.values()),
        'classes':{k:len(v) for k,v in found.items()},'total_replacements':sum(r['total_replacements'] for r in changed),
        'affected_files':changed,'only_matched_value_bytes_replaced':True,
        'mapping_path':str((OUT/'private_redaction_mapping.json').relative_to(ROOT)),
        'statistics_basis':'All statistics are calculated from full files before public redaction.'}
    for name,value in [('full_archive_manifest.json',metadata),('redaction_manifest.json',redaction)]:
        target=PUB/name
        if target.exists():assert json.loads(target.read_bytes())==value
        else:dump(target,value)
    print(json.dumps({'event':'published','files':len(manifest),'replacements':redaction['total_replacements'],'affected_files':len(changed)}),flush=True)


def verify():
    load_prepared();checks=Counter();state=load(OUT/'start_state.json')
    for name,expected in state['tracked_file_sha256'].items():
        assert sha((ROOT/name).read_bytes())==expected,name;checks['original_files_unchanged']+=1
    chosen=load(OUT/'selection.json')['first'];records=records_all();by_tag={r['tag']:r for r in records}
    assert not any(r['task'] not in chosen for r in records)
    assert not any(r['kind'] not in ['method1','method1_final','method2'] for r in records)
    started=min(r['started_at'] for r in records);frozen=freeze_check()
    assert datetime.fromisoformat(started)>datetime.fromisoformat(frozen['commit_time'])
    for task in chosen:
        folder=OUT/'tasks'/task;ledger=[]
        for c in A.manifest(task)['calls']:
            if c['kind']=='final':continue
            record=by_tag.get(f'{task}_method1_{c["call"]}')
            if not record:continue
            assert load(folder/f'ledger_before_call_{c["call"]}.json')==ledger
            if record.get('request_path'):
                prompt=assembled(task,c['call'],ledger=ledger)
                request=load(ROOT/record['request_path']);assert request['json']['input'].encode()==prompt.encode()
                assert (ROOT/record['request_path']).with_name('assembled_prompt.txt').read_bytes()==prompt.encode()
                assert sha(prompt.encode())==record['prompt_sha256'];checks['byte_exact_review_inputs']+=1
            if record['parse_success']:
                additions,_,fewer=ledger_additions(parsed_value(record),c['call']);ledger.extend(additions)
                assert load(folder/f'fewer_call_{c["call"]}.json')['fewer']==fewer
            assert load(folder/f'ledger_after_call_{c["call"]}.json')==ledger
        if (folder/'ledger_all.json').exists():assert load(folder/'ledger_all.json')==ledger
        for kind in ['method1_final','method2']:
            record=by_tag.get(f'{task}_{kind}')
            if not record or not record.get('request_path'):continue
            prompt=assembled(task,final_rank=kind=='method1_final',method2=kind=='method2',ledger=ledger if kind=='method1_final' else None)
            assert load(ROOT/record['request_path'])['json']['input'].encode()==prompt.encode();checks['byte_exact_final_inputs']+=1
    for r in records:
        if not r.get('request_path'):checks['local_assembly_failures']+=1;continue
        body=load(ROOT/r['request_path'])['json'];assert set(body)=={'model','input','reasoning','max_output_tokens'}
        assert body['model']==MODEL and body['reasoning']=={'effort':'medium','summary':'auto'} and body['max_output_tokens']==32000
        assert load(ROOT/r['request_path'])['url']=='https://api.openai.com/v1/responses'
        if r['api_success']:
            raw=load(ROOT/r['response_path']);assert usage_record(raw,'openai')==r['usage']
            assert response_text(raw,'openai')==(ROOT/r['response_path']).with_name('text.txt').read_bytes().decode()
            assert parse_text(response_text(raw,'openai'))==load(ROOT/r['parse_path']);checks['raw_response_reconciled']+=1
        checks['request_parameters_verified']+=1
    secrets=credentials()
    for p in OUT.rglob('*'):
        if p.is_file():assert not any(value in p.read_bytes() for value in secrets),str(p)
    public_files=[p for p in PUB.rglob('*') if p.is_file()]+list(PROMPTS.glob('*'))+[Path(__file__)]
    for p in public_files:
        b=p.read_bytes();assert not secret_hits(b),str(p);assert not any(value in b for value in secrets),str(p);checks['public_files_secret_scanned']+=1
    for entry in json.loads((PUB/'full_archive_manifest.json').read_bytes())['files']:
        assert sha((ROOT/entry['full_path']).read_bytes())==entry['sha256']
        assert sha((ROOT/entry['public_path']).read_bytes())==entry['public_sha256'];checks['full_and_public_hash_pairs']+=1
    result={'time':now(),'passed':True,'checks':dict(checks),'first_api_call':started,'preregistration':frozen,
        'remaining_19_called':False,'judge_called':False,'gold_or_047_loaded':False,
        'all_statistics_basis':str(OUT.relative_to(ROOT)),'secret_values_logged':False}
    target=PUB/'verification.json'
    if target.exists():target.unlink()
    dump(target,result);print(json.dumps({'event':'verified','checks':dict(checks)}),flush=True)


def report():
    aggregate=load(OUT/'aggregate_statistics.json');tasks=load(OUT/'task_statistics.json');calls=load(OUT/'call_statistics.json')
    prep=load(OUT/'preparation_summary.json');state=load(OUT/'start_state.json');frozen=freeze_check()
    quotes=load(OUT/'quote_summary.json');formats=load(OUT/'format_issues.json')
    redact=json.loads((PUB/'redaction_manifest.json').read_bytes());verification=json.loads((PUB/'verification.json').read_bytes())
    delivery=json.loads((PUB/'delivery_commit.json').read_bytes()) if (PUB/'delivery_commit.json').exists() else None
    def j(value):return json.dumps(value,ensure_ascii=False,indent=2)
    def inline(value):return str(value).replace('|','\\|').replace('\n','<br>').replace('\r','')
    def table(headers,rows):
        return '\n'+'| '+' | '.join(headers)+' |\n'+'| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(inline(v) for v in row)+' |\n' for row in rows)+'\n'
    lines=['# 小实验正式跑第一批\n','## 任务\n',
        '按用户给出的冻结 v2 提示词，在 049 的 29 道题中随机抽 DAComp 7 道、KramaBench 3 道，运行做法一、交卷重排与做法二。只记录条数和技术信息；未运行裁判、未读取 047 或标准答案、未计算任何命中情况。\n',
        '## 结论\n',
        f'完成 {aggregate["tasks_completed"]}/10 道题，记录 {aggregate["calls"]} 次调用（普通叫起 {aggregate["ordinary_calls"]}、交卷重排 {aggregate["final_rank_calls"]}、做法二 {aggregate["method2_calls"]}）。API 成功 {aggregate["api_success"]} 次，JSON 解析成功 {aggregate["parse_success"]} 次，截断 {aggregate["truncated"]} 次；累计估算 ${aggregate["estimated_usd"]:.8f}，以账单为准。剩余 19 道未调用。\n',
        f'做法一普通叫起共列 {aggregate["premises_total"]} 条，零条叫起 {aggregate["zero_reviews"]} 次；最终按模型各键的原始清单合计：做法一 {aggregate["final_raw_totals"]["method1_final"]} 条、做法二 {aggregate["final_raw_totals"]["method2"]} 条。下文另列 id 回查后的数量与 KramaBench 按 050 规则合并后的数量。这些数不作充分性判断。\n',
        '**所有条数、引用核对、token 和花费统计均以 `data/051_formal_run_full/` 完整版为准；公开脱敏后不重算。**\n',
        '## 详细发现\n','### 存档、提交与输入\n',
        f'- 开工 commit：`{state["start_commit"]}`；开始时间：`{state["started_at"]}`。\n',
        '- 开工时 notes/ 与 records/ 的最大编号为 050，本任务使用 051；交付前再次检查编号，051 为本任务使用，未顺延。\n',
        f'- 事先存档 commit：`{frozen["commit"]}`，时间 `{frozen["commit_time"]}`；三份提示词和统计口径均逐字匹配用户原文，先单独提交并推送，然后才调用模型。\n',
        f'- 第一条 API 开始时间：`{verification["first_api_call"]}`；SDK：OpenAI `{load(OUT/"environment.json")["openai_sdk"]}`、tiktoken `{load(OUT/"environment.json")["tiktoken"]}`。\n',
        '- 提示词：`records/051_prompts/`；裁判提示词仍在 `records/049_prompts/`，本批未使用。统计口径为同编号的《小实验统计口径（事先定）》报告。\n',
        '- 输入沿用 `records/049_small_exp_inputs/`，不修改 047、049、050。049 的题面、动作、截断和材料取法不变，唯一输入格式变化是 Excel 预览紧凑化。拼装、保存后再以 `read_bytes().decode("utf-8")` 读入请求，保留 CRLF；JSON 示例的普通大括号原样保留，只替换六个具名占位符。\n',
        '- `random.Random(1234)` 只创建一个实例；先对已按题号排序的 DAComp 取样 7 道，再对已排序的 KramaBench 取样 3 道，保留返回顺序。\n',
        '- DAComp：'+', '.join(prep['selection']['DAComp'])+'。\n','- KramaBench：'+', '.join(prep['selection']['KramaBench'])+'。\n',
        '- 余下未跑的 19 道：'+', '.join(prep['selection']['remaining'])+'。\n',
        '### Excel 改写核对与 29 道题 token\n',
        '检查了 031 中全部 32 个 Excel 行预览块（327 行、10,921 个格子），含 first_10_physical_rows 和 README 的 all_rows。逐块核对原 JSONL 与独立 sheets 元数据一致；按最大出现列号保留空格子，行号开头、列文字以制表符分隔，text 或 raw_value 原字符串保持大小写和内容，空值留空。逐格同时核对相同列位置、相同行内顺序与文字 SHA256。所有格子无换行/制表符冲突，全部核对通过，先通过后才调用。保留工作表名等非行预览信息。\n',
        '实际组装输入受影响的题：'+', '.join(prep['excel_affected_tasks'])+'。下表均为**同一 v2 完整提示词**、空账本 `(none)`，改写前后只改变 Excel 格式；做法一为全部普通叫起 token 合计。逐次的中位数、最大值和 SHA256 见 `preparation_summary.json`、`input_token_counts.csv`。o200k_base 是近似计数。\n']
    lines.append(table(['题号','普通叫起','做法一改前→改后','做法二改前→改后','Excel 影响'],[
        [t['task'],t['ordinary_calls'],f'{t["method1_before_sum"]} → {t["method1_after_sum"]}',f'{t["method2_before_tokens"]} → {t["method2_after_tokens"]}',t['excel_affected']] for t in prep['all_29_tasks']]))
    lines+=['### 统计定义\n',
        '- 每次涉及几个 target：按模型 `target` 完整字符串的不同值计数；不推断多个字符串是否代表同一张表。交卷重排按返回 id 回查账本，不应用 updates 删除旧条目；`fewer` 单独保存、不进入账本。最终条数按每个键中的出现次数计，同一 id 出现在多个位置也分别计数，并另列重复位置。\n',
        '- “agent 写过的表”为机械近似：做法二实际拿到的契约节对应的表名去重。模型键去 schema 前缀并转小写后完全匹配才计“出现”；空列表的键也算出现，同时另外记录非空数量。不读取标准答案决定表名，不作实际写表推断。\n',
        '- KramaBench 同时报告各原始键的条数之和与 050 规则合并条数：单键保留；多键按 importance 降序、键出现顺序、键内顺序取前 10。模型原始键、条目和理由全部保留。DAComp 不跨键合并。\n',
        '### 10 道合计\n',f'```json\n{j(aggregate)}\n```\n',
        '### 每道题的条数、target、fewer 原文与最终清单\n']
    overview=[]
    for t in tasks:
        a=t['finals']['method1_final'] or {};b=t['finals']['method2'] or {}
        pa=a.get('coverage_proxy');pb=b.get('coverage_proxy')
        cov=f'{pa["numerator"]}/{pa["denominator"]}；{pb["numerator"]}/{pb["denominator"]}' if pa and pb else '不计'
        kb=f'{a.get("krama_aggregate_count")} / {b.get("krama_aggregate_count")}' if t['benchmark']=='KramaBench' else '不计'
        overview.append([t['task'],t['ordinary_calls_recorded'],t['ledger_count'],len(t['zero_reviews']),
             f'{a.get("raw_total")} / {b.get("raw_total")}',kb,cov])
    lines.insert(-1,table(['题号','普通叫起','新增前提','零条叫起','最终各键合计：一/二','Krama 合并：一/二','DA 表名出现：一；二'],overview))
    if aggregate['input_tokens']:
        lines.insert(-1,f'已返回 usage 的缓存输入合计比例：{aggregate["cached_input_tokens"]}/{aggregate["input_tokens"]} = {aggregate["cached_input_tokens"]/aggregate["input_tokens"]:.6%}；各题 wall time 合计 {sum(t["wall_seconds"] or 0 for t in tasks):.3f} 秒。\n')
    for t in tasks:
        lines.append(f'#### {t["task"]}\n')
        lines.append(f'普通叫起计划 {t["ordinary_calls_planned"]} 次、记录 {t["ordinary_calls_recorded"]} 次；另交卷重排 1 次、做法二 1 次。账本 {t["ledger_count"]} 条；题用时 {t["wall_seconds"]} 秒；估算 ${t["cost_usd"]:.8f}。\n')
        lines.append(table(['叫起','规则','条数','不同 target','零条'],[[r['call'],','.join(r['rules']),r['premises_count'],r['literal_target_count'],r['zero_items']] for r in t['reviews']]))
        lines.append('每次的 target 计数及 `fewer` 全部原文（零条叫起的理由也在此列出；未提供时保留原值）：\n')
        lines.append('```json\n'+j([{'call':r['call'],'target_counts':r['target_counts'],'fewer':r['fewer'],'zero_items':r['zero_items']} for r in t['reviews']])+'\n```\n')
        for kind,label in [('method1_final','做法一交卷重排'),('method2','做法二')]:
            f=t['finals'][kind];lines.append(f'**{label}**\n')
            if not f:lines.append('尚无调用记录。\n');continue
            lines.append(table(['模型表/结果键','原始条数','id 回查后/实际条数'],[[key,n,f.get('resolved_key_counts',{}).get(key)] for key,n in f['raw_key_counts'].items()]))
            if kind=='method2':lines.append('`fewer_reason` 原文：\n```json\n'+j(f['fewer_reasons'])+'\n```\n')
            if 'coverage_proxy' in f:
                p=f['coverage_proxy'];lines.append(f'写过的表近似覆盖：{p["numerator"]}/{p["denominator"]}（{p["ratio"]}）；非空键覆盖数 {p["nonempty_numerator"]}。\n')
                lines.append('表名机械对照：\n```json\n'+j(p)+'\n```\n')
            else:lines.append(f'KramaBench：原始键条数合计 {f.get("raw_total")}，id 回查后合计 {f.get("resolved_total")}，按 050 规则合并 {f["krama_aggregate_count"]} 条。\n')
            if f['unknown_ids'] or f['issues']:lines.append('技术异常：\n```json\n'+j({'unknown_ids':f['unknown_ids'],'issues':f['issues']})+'\n```\n')
            if f.get('repeated_ledger_id_occurrences'):lines.append('同一账本 id 的重复出现位置（只记录；不推断是否应跨结果保留）：\n```json\n'+j(f['repeated_ledger_id_occurrences'])+'\n```\n')
    lines+=['### 与 050 只比较条数\n',
        '`impl-025` 未抽中，不调用、不作本批对照；`legal-hard-18` 抽中。以下只读 050 被测模型的输出条数，未读裁判结果。050 已记录 legal 输入 CRLF 被文本模式转换，051 保留原始换行，因此两次输入也有这一技术差别。\n',
        '```json\n'+j(load(OUT/'pilot_count_comparison.json'))+'\n```\n',
        '### 每次调用的状态、用量、缓存、推理、花费与用时\n',
        '输入、输出、缓存、推理 token 均来自 API usage；缓存 token 是输入的子集，推理 token 是输出的子集。估算沿用 050：每百万未缓存输入 $2、缓存输入 $0.10、输出 $10，长输入标“价格待核”，不把缺失 usage 称为免费。未改变 medium、summary=auto、32000 或任何模型参数。所有完整请求、原始 HTTP 返回、SDK 返回、reasoning 条目和摘要均保存。重试仅网络错误/429/5xx，初次以外最多 3 次，等待 2/4/8 秒。\n']
    lines.append(table(['题号/类型/次','API/解析/完成','截断/尝试','输入/缓存','输出/推理','缓存比例','实际/o200k','估算 USD','秒','摘要'],[
        [f'{r["task"]}/{r["type"]}/{r["call"]}',f'{r["api_success"]}/{r["parse_success"]}/{r["completed"]}',f'{r["truncated"]}/{r["attempts"]}',
         f'{r["input_tokens"]}/{r["cached_input_tokens"]}',f'{r["output_tokens"]}/{r["reasoning_tokens"]}',r['cached_input_fraction'],r['actual_input_to_current_o200k_ratio'],
         r['estimated_usd'],r['wall_seconds'],r['has_reasoning_summary_text']] for r in calls]))
    lines.append('长输入、价格待核的调用：'+j([r['tag'] for r in calls if r['long_input_price_unverified']])+'。\n')
    failed_attempts=[{'tag':r['tag'],**attempt} for r in records_all() for attempt in r['attempts'] if not attempt['success']]
    lines.append(f'失败尝试共 {len(failed_attempts)} 次，逐次记录如下（这些尝试未返回 usage，不能据此断言不收费）：\n```json\n'+j(failed_attempts)+'\n```\n')
    lines+=['### 格式与引用核对\n',
        '`evidence_of_dependence`、`evidence_in_work` 整栏逐字查对应的实际完整输入；`alternative`、`source` 仅查 json.loads 后字符串内部显式引号内的部分（沿用 050 的 ASCII 单/双引号、弯引号、反引号/代码块分隔符的机械提取；JSON 外围引号不算）；不从无引号的文字猜原文，无引号记“未给出原文”，null 记不适用。每个抽出的片段独立计数，另报同一条目的该字段中全部片段都找到的数量，不按语义选择；完全逐字与连续空白压成一个空格两种口径并列，不修复省略号、拼写或大小写。\n',
        '```json\n'+j(quotes)+'\n```\n',
        f'字段缺失、每 target 超 5 条、最终某键超 10 条等格式异常共 {len(formats)} 项，原样如下：\n```json\n'+j(formats)+'\n```\n',
        '逐条引用、原文、定位、两口径结果见 `records/051_formal_run/quote_checks.json`；未找到只是字符串核对结果，不做语义判断。\n',
        '### 完整版、脱敏、SHA256 与保护检查\n',
        '`data/051_formal_run_full/` 为不进 git 的完整版；`records/051_formal_run/` 为公开版。每个完整请求和返回及其他文件的路径、大小、SHA256 对应清单在 `records/051_formal_run/full_archive_manifest.json`；本报告统计全部以完整版本为准。\n',
        f'脱敏共替换 {redact["total_replacements"]} 处，涉及 {len(redact["affected_files"])} 个文件、{redact["unique_values_in_this_archive"]} 个不同值；同值使用同一固定占位符，只替换命中的字符串。原值映射仅在 data/ 下。\n',
        '受影响文件及各自完整/公开 SHA256：\n```json\n'+j(redact['affected_files'])+'\n```\n',
        '复核结果：\n```json\n'+j(verification)+'\n```\n',
        '归档的原始材料含尾空白、CRLF 和末尾空行，完整 `git diff --check` 因这些保留字节给出格式提示；没有清理或改写。脚本及报告单独做空白检查；归档按逐字节/SHA256 验证。\n',
        '## 证据来源\n',
        '- 冻结原文核对：`records/051_formal_run/frozen_text_source_check.json`；事先提交时间：`preregistration_commit.json`。\n',
        '- 固定输入和切段：`records/049_small_exp_inputs/`、`records/049_small_exp_assemble.py`；Excel 原行和独立格子元数据：`records/031_kramabench_docs/`、`records/031_kramabench_docs_excerpts.json`、`records/031_kramabench_docs_sheets.json`。只读文件，无数据库数据查询。\n',
        '- 主脚本：`records/051_formal_run.py`；公开的 `selection.json`、`preparation_summary.json`、`input_token_counts.csv`、`excel_compact_validation.json`、`call_statistics.csv`、`task_statistics.json`、`quote_checks.json`、`format_issues.json`、`run.log`。\n',
        '- SDK 接口细节参考 OpenAI Docs：[Reasoning models](https://developers.openai.com/api/docs/guides/reasoning)、[GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)。实际参数以每次保存的请求为准，价格估算口径沿用 050。\n',
        '- 等价复现命令（环境 `/tmp/assumption-ledger-050-venv`，tokenizer cache `/tmp/assumption-ledger-048-tiktoken-cache`；实际准备阶段通过导入本脚本调用 `prepare()`，其余子命令已执行）：\n',
        '```bash\npython records/051_formal_run.py prepare\npython records/051_formal_run.py run --batch first\npython records/051_formal_run.py analyze\npython records/051_formal_run.py publish\npython records/051_formal_run.py verify\n```\n',
        '后续获准后可使用 `run --batch remaining`；本次没有执行此命令。脚本通过现存 record 和账本快照恢复，不重复已有调用。\n',
        '## 不确定或没查到的\n',
        '- 本批不判断列出的条数是否足够、条目是否正确，不运行裁判或报告命中。是否更改推理强度、剩余 19 道如何继续，由用户和 Claude 决定。\n',
        '- 表名机械近似和不同 target 的字符串计数不能代替实际写表识别；复合 target、不完全相同的别名不自行归并。字段和 id 异常在上文原样列出，交 Claude 决定。\n',
        '- 引号提取是纯文本规则，不能判定引号里的文字是否是模型意图引用的整句；完整 input 的字符串出现不代表语义支持。\n',
        '- 花费按用户指定估算，缓存及 reasoning 来自返回 usage；未取得账单。\n',
        '## 建议的下一步\n',
        '请用户和 Claude 查看本批条数及少列理由，决定剩余 19 道的执行方式；提示词继续冻结。\n']
    if (OUT/'STOP.json').exists():lines.append('停止记录：\n```json\n'+j(load(OUT/'STOP.json'))+'\n```\n')
    if delivery:lines.append(f'交付产物 commit：`{delivery["commit"]}`，时间 `{delivery["time"]}`。本报告的提交在其后；事先存档 commit 保持不变。\n')
    archive=json.loads((PUB/'full_archive_manifest.json').read_bytes())
    hashes={entry['full_path']:entry['sha256'] for entry in archive['files']};archive_rows=[]
    for record in records_all():
        paths=[('完整请求',record.get('request_path')),('原始返回 JSON',record.get('response_path'))]
        if record.get('response_path'):
            p=Path(record['response_path']);paths.append(('原始 HTTP 正文',str(p.with_name(p.stem+'_body.txt'))))
        for label,path in paths:
            if path:archive_rows.append([record['tag'],label,path,hashes[path]])
    at=lines.index('## 证据来源\n')
    lines.insert(at,'完整请求、原始返回 JSON 和原始 HTTP 正文的路径与 SHA256（SDK 返回和其他文件的校验值见完整清单）：\n')
    lines.insert(at+1,table(['调用','文件类型','data/ 完整路径','SHA256'],archive_rows))
    target=ROOT/'notes/051_2026-11-06_小实验正式跑第一批.md'
    full=re.sub(r'(?m)^(#{1,6} .*)\n(?!\n)',r'\1\n\n',''.join(lines)).encode('utf-8');public=full;replacements={}
    mapping=load(OUT/'private_redaction_mapping.json')
    for value,placeholder in mapping.items():
        n=public.count(value.encode())
        if n:replacements[placeholder]=n;public=public.replace(value.encode(),placeholder.encode())
    assert not secret_hits(public) and not any(k in public for k in credentials())
    # Report statistics originate in the full archive; redact literal values only
    # when publishing the prose. Keep a separate full report and its hash too.
    private_report=OUT/'report_unredacted.md';private_report.write_bytes(full);target.write_bytes(public)
    report_meta={'full_path':str(private_report.relative_to(ROOT)),'sha256':sha(full),
        'public_path':str(target.relative_to(ROOT)),'public_sha256':sha(public),'replacements':replacements,
        'statistics_basis':'Unredacted full archive; no recomputation after redaction.'}
    (PUB/'report_archive_manifest.json').write_text(j(report_meta)+'\n',encoding='utf-8')
    print(json.dumps({'event':'report_written','path':str(target.relative_to(ROOT)),'bytes':target.stat().st_size}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('prepare')
    run=sub.add_parser('run');run.add_argument('--batch',choices=['first','remaining'],default='first')
    ap=sub.add_parser('assemble');ap.add_argument('task');ap.add_argument('call',type=int,nargs='?')
    modes=ap.add_mutually_exclusive_group();modes.add_argument('--method2',action='store_true');modes.add_argument('--final-rank',action='store_true')
    ap.add_argument('--ledger-json',type=Path)
    for name in ['analyze','publish','verify','report']:sub.add_parser(name)
    args=parser.parse_args()
    if args.command=='prepare':prepare()
    elif args.command=='run':
        try:run_batch(args.batch)
        except StopFormal as e:print(json.dumps({'event':'stopped','reason':str(e),'estimated_usd':total_cost()}),flush=True)
    elif args.command=='assemble':
        load_prepared();ledger=load(args.ledger_json) if args.ledger_json else None
        text=assembled(args.task,args.call,args.final_rank,args.method2,ledger)
        sys.stdout.buffer.write(text.encode('utf-8'))
    else:globals()[args.command]()


if __name__=='__main__':main()
