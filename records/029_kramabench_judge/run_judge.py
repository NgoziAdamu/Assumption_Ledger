"""Thirty official-metric calls; raw transport observations do not alter requests.

Each immutable call intent prevents accidental reissuing after an interrupted run.
All model parsing is performed by the original official files, not this script.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import logging
import sys
import time

sys.dont_write_bytecode = True
from openai import OpenAI
import httpx
from official_wrapper import official_metric, ROOT, OFFICIAL, BASE_URL, MODEL

OUT = Path(__file__).resolve().parent

def now():
    return datetime.now(timezone.utc).isoformat()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if (OUT/'run_manifest.json').exists():
        raise SystemExit('Run already started: refusing to issue any additional model calls.')
    all_metas=[]
    for p in sorted((ROOT/'records/027_kramabench_source/runs').glob('*/*/meta.json')):
        all_metas.append((p,json.loads(p.read_bytes())))
    pending=sorted([(p,m) for p,m in all_metas if m['score']['status']=='needs_judge'],key=lambda x:x[1]['task_id'])
    assert len(all_metas)==104 and len(pending)==10
    workload_paths=sorted((ROOT/'data/kramabench/workload').glob('*.json'))
    tasks={t['id']:(p,t) for p in workload_paths for t in json.loads(p.read_bytes())}
    assert len(tasks)==104
    sources=sorted(set([p for p in OFFICIAL.rglob('*') if p.is_file()]
                       +[p for p,m in all_metas]+workload_paths
                       +list((ROOT/'records/027_kramabench_source/runs').glob('*/summary.json'))))
    before={str(p.relative_to(ROOT)):digest(p) for p in sources}
    key=(Path.home()/'.openrouter_key').read_text(encoding='utf-8').strip()
    if not key or any(c.isspace() for c in key):
        raise SystemExit('The credential file must contain a single nonempty key. Value not displayed.')

    def safe(text):
        return text.replace(key,'[REDACTED_CREDENTIAL]')

    def save(path,obj):
        text=json.dumps(obj,ensure_ascii=False,indent=2)+'\n'
        assert key not in text, 'Credential detected before writing; value suppressed.'
        with path.open('x',encoding='utf-8') as f:
            f.write(text)
            f.flush()

    state={'record':None,'clients':[]}
    class CaptureLogs(logging.Handler):
        def emit(self,record):
            if state['record'] is not None:
                state['record']['official_logs'].append({'time_utc':now(),'level':record.levelname,
                                                         'logger':record.name,'message':safe(record.getMessage())})
    logging.getLogger().handlers=[CaptureLogs()]
    logging.getLogger().setLevel(logging.WARNING)
    for name in ['openai','httpx','httpcore']:
        logging.getLogger(name).setLevel(logging.WARNING)

    def observe_request(request):
        assert request.url.host=='openrouter.ai' and request.url.path=='/api/v1/chat/completions'
        body=json.loads(request.content)
        assert set(body)=={'model','messages'} and body['model']==MODEL
        # Never save request headers or a client object: both contain credentials.
        state['record']['http_attempts'].append({'started_at_utc':now(),'method':request.method,
                                                'url':str(request.url),'request_body':body})

    def observe_response(response):
        response.read()
        text=response.content.decode('utf-8')
        record=state['record']['http_attempts'][-1]
        record.update(received_at_utc=now(),http_status=response.status_code,
                      raw_response_text=safe(text),credential_redaction_applied=(key in text))
        try:
            record['raw_response_json']=json.loads(safe(text))
        except json.JSONDecodeError:
            record['raw_response_json']=None
        # Only this harmless response header is retained; no authentication headers.
        record['request_id']=response.headers.get('x-request-id')

    def client_factory(**kwargs):
        assert set(kwargs)=={'api_key'}
        client=OpenAI(api_key=key,base_url=BASE_URL)
        # Observation hooks on the SDK's existing default transport: no sampling,
        # timeout, retry, routing, prompt, or request-body settings are changed.
        client._client.event_hooks['request'].append(observe_request)
        client._client.event_hooks['response'].append(observe_response)
        state['clients'].append(client)
        return client

    metric=official_metric(client_factory)
    manifest={'started_at_utc':now(),'tasks':[m['task_id'] for p,m in pending],
              'calls_per_task':3,'official_score_repetition':1,'stability_only_repetitions':[2,3],
              'base_url':BASE_URL,'model':MODEL,'credential_source':'~/.openrouter_key (not copied)',
              'sdk_default_retries_preserved':2,'sdk_default_timeout_preserved':True,
              'request_body_keys':['model','messages'],'source_sha256_before':before,
              'python':sys.version,'dependencies':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
              'only_adaptations':['OpenRouter client base_url and file-loaded key','gpt-5-mini -> openai/gpt-5-mini'],
              'raw_response_recording':'HTTP response body observed without altering official result parsing'}
    save(OUT/'run_manifest.json',manifest)
    for meta_path,meta in pending:
        task_id=meta['task_id'];wp,task=tasks[task_id]
        assert task['answer_type']=='string_approximate' and meta['final_answer'] is not None
        for repetition in range(1,4):
            stem=f'{task_id}_call{repetition}'
            intent={'task_id':task_id,'repetition':repetition,'purpose':'official_score' if repetition==1 else 'stability_only',
                    'started_at_utc':now(),'meta_source':str(meta_path.relative_to(ROOT)),
                    'workload_source':str(wp.relative_to(ROOT)),'answer_type':task['answer_type'],
                    'predicted_original':meta['final_answer'],'target_original':task['answer'],
                    'predicted_type':type(meta['final_answer']).__name__,'target_type':type(task['answer']).__name__}
            save(OUT/(stem+'_intent.json'),intent)
            record={**intent,'http_attempts':[],'official_logs':[]}
            state['record']=record
            start=time.monotonic()
            try:
                result=metric(meta['final_answer'],task['answer'])
                record['official_metric_return']=list(result)
                record['score']=result[0]
                record['judge_status']='裁判失败' if result[0] is None else ('通过' if result[0]==1 else '未通过')
            except Exception as error:
                # No replacement scoring rule. Unexpected errors remain unscored.
                record['official_metric_return']=None
                record['score']=None
                record['judge_status']='裁判失败'
                record['unhandled_exception']={'type':type(error).__name__,'message':safe(str(error))}
            finally:
                record['ended_at_utc']=now()
                record['elapsed_seconds']=time.monotonic()-start
                for client in state['clients']:
                    client.close()
                state['clients'].clear()
            successful=[a for a in record['http_attempts'] if a.get('http_status')==200 and isinstance(a.get('raw_response_json'),dict)]
            raw=successful[-1]['raw_response_json'] if successful else {}
            usage=raw.get('usage') or {}
            record.update(returned_model=raw.get('model'),returned_provider=raw.get('provider'),
                          usage=usage,cost_usd=usage.get('cost'),cost_source='response.usage.cost' if usage.get('cost') is not None else None)
            # A metadata GET, only when the completion omitted its cost. This is
            # not another model invocation and cannot change the official score.
            if record['cost_usd'] is None and raw.get('id'):
                metadata={'requested_at_utc':now(),'generation_id':raw['id']}
                try:
                    response=httpx.get(BASE_URL+'/generation',params={'id':raw['id']},headers={'Authorization':'Bearer '+key},timeout=30)
                    text=safe(response.text)
                    metadata.update(http_status=response.status_code,raw_response_text=text)
                    if response.status_code==200:
                        data=json.loads(text).get('data') or {}
                        record['cost_usd']=data.get('total_cost')
                        record['cost_source']='generation.data.total_cost' if record['cost_usd'] is not None else None
                except Exception as error:
                    metadata['error']={'type':type(error).__name__,'message':safe(str(error))}
                metadata['finished_at_utc']=now();record['cost_metadata_lookup']=metadata
            save(OUT/(stem+'.json'),record)
            state['record']=None
            print(json.dumps({'task_id':task_id,'call':repetition,'status':record['judge_status'],
                              'model':record['returned_model'],'provider':record['returned_provider'],
                              'cost_usd':record['cost_usd'],'http_attempts':len(record['http_attempts'])},ensure_ascii=False),flush=True)
    after={str(p.relative_to(ROOT)):digest(p) for p in sources}
    assert before==after
    save(OUT/'run_completed.json',{'finished_at_utc':now(),'metric_calls':30,'source_sha256_after':after,
                                   'all_sources_unchanged':True})

if __name__=='__main__':
    main()
