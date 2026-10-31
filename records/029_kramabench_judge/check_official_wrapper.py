"""Offline fidelity checks. No API key is read and no network calls are made."""
from pathlib import Path
import hashlib
import inspect
import json
import logging
from types import SimpleNamespace
from official_wrapper import official_metric, OFFICIAL, MODEL

logging.disable(logging.CRITICAL)
state = {}

def create(**kwargs):
    state['request'] = kwargs
    if state.get('raise_error'):
        raise RuntimeError('offline simulated API error')
    return SimpleNamespace(usage=SimpleNamespace(total_tokens=13,prompt_tokens=10,completion_tokens=3),
                           choices=[SimpleNamespace(finish_reason=state['finish'],message=SimpleNamespace(content=state['text']))])

def factory(**kwargs):
    assert set(kwargs) == {'api_key'}
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

metric=official_metric(factory)
import benchmark.llm_tools.gpt_interface as gpt
from benchmark.llm_tools.prompts import PARAPHRASE_INSTRUCTION_PROMPT

cases=[('yes','stop',1),('No','stop',0),('YES','length',1),('no, YES','stop',1),
       ('yEs','stop',None),('unclear','stop',None),('yes','tool_calls',None)]
for text,finish,expected in cases:
    state.update(text=text,finish=finish,raise_error=False)
    result=metric(False,{'answer': True})
    assert result[0]==expected and result[1:]==(13,10,3)
    assert set(state['request'])=={'model','messages'} and state['request']['model']==MODEL
    messages=state['request']['messages']
    assert messages[:-1]==[{'role':p['role'],'content':[{'type':'text','text':p['content']}]} for p in PARAPHRASE_INSTRUCTION_PROMPT]
    assert messages[-1]['content'][0]['text']=='A:"False"; B:"{\'answer\': True}"'
state['raise_error']=True
assert metric('a','b')==(None,0,0,0)
methods=[metric.__class__.__call__,gpt.GPTInterface.evaluate_paraphrase,gpt.GPTInterface._format_paraphrase_evaluation_messages]
identities=[]
for method in methods:
    source=Path(inspect.getsourcefile(method)).resolve()
    assert source.is_relative_to(OFFICIAL.resolve())
    identities.append({'method':method.__qualname__,'source':str(source),'function_source_sha256':hashlib.sha256(inspect.getsource(method).encode()).hexdigest()})
result={'passed':True,'offline_cases':len(cases)+1,'network_calls':0,'key_file_read':False,
        'original_functions_executed':identities,'prompt_exact':True,'official_str_conversion_preserved':True,
        'yes_no_priority_and_case_rules_preserved':True,'none_branches_preserved':True}
target=Path(__file__).with_name('offline_validation.json')
with target.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
