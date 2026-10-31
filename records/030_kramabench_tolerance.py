"""Offline, mechanical tolerance comparisons; no model or agent execution."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP, localcontext
from typing import Generic, List, Tuple, TypeVar
import ast
import collections
import csv
import hashlib
import json
import logging
import re
import socket

ROOT=Path(__file__).resolve().parents[1]
METRICS=ROOT/'records/027_kramabench_source/official/benchmark/metrics.py'
SCORES=ROOT/'records/029_kramabench_final_scores.csv'
PREFIX=ROOT/'records/030_kramabench'
NUMBER=re.compile(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?')
FORMAT=re.compile(r'\b(?:round(?:ed|ing)?|decimals?|percentages?|percent|nearest|format|list|answer|report|pair|positive|negative|true|false)\b|full names|no explanation|%',re.I)

def no_network(*args,**kwargs):
    raise RuntimeError('Network is disabled for this offline task')
socket.create_connection=no_network
socket.socket.connect=no_network
socket.socket.connect_ex=no_network

def dump(path,value):
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

def hashfile(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def official_functions():
    # Compile unchanged definitions from the source file, excluding all model
    # imports and unrelated metrics. This is not a reimplementation of scoring.
    text=METRICS.read_text(encoding='utf-8')
    tree=ast.parse(text)
    names={'Metric','str_to_float','try_convert_to_number','Success','F1'}
    nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names]
    assert {n.name for n in nodes}==names
    ns={'Generic':Generic,'List':List,'Tuple':Tuple,'P':TypeVar('P'),'T':TypeVar('T'),'json':json,'logging':logging}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(METRICS),'exec'),ns)
    return ns['Success'](),ns['F1'](),[{'name':n.name,'line':n.lineno,'end_line':n.end_lineno,
        'source_sha256':hashlib.sha256(ast.get_source_segment(text,n).encode()).hexdigest()} for n in nodes]

def parse_list(value):
    if isinstance(value,(list,tuple)):
        return list(value),'original_list_or_tuple'
    if isinstance(value,str):
        try:
            parsed=json.loads(value)
        except (ValueError,TypeError):
            try:parsed=ast.literal_eval(value)
            except (ValueError,SyntaxError):parsed=None
        if isinstance(parsed,(list,tuple)):
            return list(parsed),'safe_literal_list_or_tuple'
        # Same fallback as official F1, but never evaluate text as Python code.
        return [x.strip() for x in value.split(',') if x.strip()],'official_comma_split_fallback'
    raise TypeError('List answer has an unsupported container type')

def normalize(value):
    if isinstance(value,str):
        value=value.strip().lower()
        if value=='true':return True
        if value=='false':return False
        if NUMBER.fullmatch(value):
            number=Decimal(value)
            return int(number) if re.fullmatch(r'[+-]?\d+',value) else float(number)
        return value
    if isinstance(value,(list,tuple)):
        return [normalize(x) for x in value]
    return value

def display(value):
    return value if isinstance(value,str) else json.dumps(value,ensure_ascii=False)

def numeric_candidates(value):
    text=display(value)
    # Remove only commas used between digits in thousands groups, plus $ and %.
    cleaned=re.sub(r'(?<=\d),(?=\d{3}(?:\D|$))','',text).replace('$','').replace('%','')
    candidates=[]
    for match in NUMBER.finditer(cleaned):
        token=match.group();d=Decimal(token)
        if d.is_finite():
            candidates.append({'operation':'extract_number','token':token,'cleaned_text_span':list(match.span()),
                               'value':int(d) if re.fullmatch(r'[+-]?\d+',token) else float(d)})
    return cleaned,candidates

def decimal_places(value):
    if not isinstance(value,Decimal):return None
    return max(0,-value.as_tuple().exponent)

def rounded(value,places):
    with localcontext() as context:
        context.prec=max(50,len(str(value))+places+10)
        d=Decimal(str(value)).quantize(Decimal(1).scaleb(-places),rounding=ROUND_HALF_UP)
    return (int(d) if places==0 else float(d)),format(d,'f')

def list_core(value):
    notes=[]
    if value and all(isinstance(x,(list,tuple)) and len(x)>0 for x in value):
        value=[x[0] for x in value];notes.append('all_items_list_or_tuple_take_first')
    cleaned=[]
    for x in value:
        if isinstance(x,str):
            # Strip only terminal parenthesized suffixes, with balanced nesting.
            x=x.rstrip()
            while x.endswith(')'):
                depth=0;start=None
                for i in range(len(x)-1,-1,-1):
                    if x[i]==')':depth+=1
                    elif x[i]=='(':
                        depth-=1
                        if depth==0:start=i;break
                if start is None:break
                x=x[:start].rstrip()
        cleaned.append(normalize(x))
    notes.append('remove_terminal_parenthesized_suffix_then_normalize')
    return cleaned,notes

def format_sentences(query):
    found=[];start=0
    # Punctuation followed by whitespace/end; decimal points and URL-internal
    # dots are not sentence boundaries. Keep original substring offsets.
    for boundary in list(re.finditer(r'[.!?](?=\s|$)',query))+[None]:
        end=boundary.end() if boundary else len(query)
        left=start
        while left<end and query[left].isspace():left+=1
        right=end
        while right>left and query[right-1].isspace():right-=1
        sentence=query[left:right]
        hits=[m.group() for m in FORMAT.finditer(sentence)]
        if sentence and hits:found.append({'start':left,'end':right,'text':sentence,'keyword_hits':hits})
        start=end
    return found

def main():
    success,f1,definitions=official_functions()
    # Small offline rule checks, including preservation of official semantics.
    assert success(True,True)[0]==1 and success(True,'True')[0]==0
    assert normalize(' TRUE ')==True and normalize(' 12.50 ')==12.5
    assert numeric_candidates('$7,805,421; 10.87%; -2.3e-4')[1][0]['value']==7805421
    assert rounded(1.235,2)==(1.24,'1.24') and rounded(-1.235,2)==(-1.24,'-1.24')
    assert decimal_places(Decimal('6.1655e-7'))==11
    assert list_core([['A',2],['B',3]])[0]==['a','b']
    assert list_core(['A (one)','B (nested (two))'])[0]==['a','b']
    assert f1([6.326,0.787],[6.326,0.787])[0]==1
    logging.getLogger().handlers=[logging.NullHandler()]
    sources={str(SCORES.relative_to(ROOT)):hashfile(SCORES),str(METRICS.relative_to(ROOT)):hashfile(METRICS)}
    score_rows=list(csv.DictReader(SCORES.open(encoding='utf-8')))
    selected=[r for r in score_rows if r['最终状态'] in {'未通过','未交卷'}]
    assert len(selected)==42
    metas={}
    for p in sorted((ROOT/'records/027_kramabench_source/runs').glob('*/*/meta.json')):
        meta=json.loads(p.read_bytes());metas[meta['task_id']]=(p,meta)
    tasks={}
    for p in sorted((ROOT/'data/kramabench/workload').glob('*.json')):
        text=p.read_text(encoding='utf-8');normal=json.loads(text)
        exact=json.loads(text,parse_float=Decimal,parse_int=Decimal)
        sources[str(p.relative_to(ROOT))]=hashfile(p)
        for t,e in zip(normal,exact):tasks[t['id']]=(p,t,e)
    events=[]
    def compare(metric,predicted,target):
        if metric=='F1':
            # Both list arguments mean official F1's eval branch is unreachable.
            assert isinstance(predicted,list) and isinstance(target,list)
            result=f1(predicted,target)
        else:result=success(predicted,target)
        events.append({'metric':metric,'predicted':predicted,'target':target,'return':list(result)})
        return result[0],len(events)-1
    records=[];rows=[]
    for old in selected:
        tid=old['题号'];mp,m=metas[tid];wp,t,exact=tasks[tid]
        sources[str(mp.relative_to(ROOT))]=hashfile(mp)
        answer=m['final_answer'];gold=t['answer'];kind=t['answer_type'];query=m['prompt_values']['query']
        assert query==t['query']
        rec={'task_id':tid,'answer_type':kind,'answer_original':answer,'gold_original':gold,
             'meta_source':str(mp.relative_to(ROOT)),'workload_source':str(wp.relative_to(ROOT)),
             'official_029_row':old,'query':query,'format_sentences':format_sentences(query),
             'stages':{'0':{'status':'未对上','source':'029 CSV copied','score':old['最终分数']}},
             'gold_literal_substring_in_answer':None,'first_match':None,'matched_using':None}
        assert old['最终分数']=='0'
        if answer is None:
            for stage in ['1','2','3']:rec['stages'][stage]={'status':'无答案'}
            rec['first_match']='无答案'
        elif kind=='string_approximate':
            for stage in ['1','2','3']:rec['stages'][stage]={'status':'不适用'}
            rec['first_match']='不适用'
        else:
            is_list=kind.startswith('list_');is_numeric=kind.startswith('numeric_')
            if is_list:
                a,parsing=parse_list(answer);g,gparsing=parse_list(gold)
                norm_answer,norm_gold=normalize(a),normalize(g)
                rec['list_parse']={'answer':parsing,'gold':gparsing}
            else:norm_answer,norm_gold=normalize(answer),normalize(gold)
            metric='F1' if is_list else 'Success'
            score,event=compare(metric,norm_answer,norm_gold)
            c1={'operation':'normalize_types_strip_case','value':norm_answer}
            rec['stages']['1']={'status':'对上' if score==1 else '未对上','metric':metric,'score':score,
                                 'candidate':c1,'target':norm_gold,'event':event}
            if score==1:rec.update(first_match=1,matched_using=c1)
            if is_numeric:
                cleaned,candidates=numeric_candidates(answer)
                rec['numeric_cleaned_text']=cleaned
            elif kind=='string_exact':
                rec['gold_literal_substring_in_answer']=(gold in answer) if isinstance(answer,str) and isinstance(gold,str) else None
                candidates=[{'operation':'stage1_value_retained','value':norm_answer}]
                if isinstance(answer,str):
                    for delimiter in [' — ',' (',':']:
                        if delimiter in answer:
                            core=answer.split(delimiter,1)[0]
                            candidates.append({'operation':'prefix_before_delimiter','delimiter':delimiter,'original_core':core,'value':normalize(core)})
            else:
                core,operations=list_core(norm_answer)
                candidates=[{'operation':operations,'value':core}]
            trials=[];match=None
            for candidate in candidates:
                score,event=compare(metric,candidate['value'],norm_gold)
                trials.append({'candidate':candidate,'score':score,'event':event})
                if score==1 and match is None:match=candidate
            rec['stages']['2']={'status':'对上' if match is not None else '未对上','metric':metric,'trials':trials,'matched_candidate':match}
            if match is not None and rec['first_match'] is None:rec.update(first_match=2,matched_using=match)
            round_candidates=[]
            if is_numeric:
                places=decimal_places(exact['answer']);assert places is not None
                rec['rounding_decimal_places']=places
                for c in candidates:
                    val,decimal_text=rounded(Decimal(c['token']),places)
                    round_candidates.append({'operation':'round_half_up','source_candidate':c,'decimal_places':places,'rounded_decimal_text':decimal_text,'value':val})
            elif is_list:
                decimals=exact['answer']
                if isinstance(decimals,str):
                    try:decimals=json.loads(decimals,parse_float=Decimal,parse_int=Decimal)
                    except ValueError:decimals=[]
                core=candidates[0]['value'];rounded_list=[];details=[]
                for i,value in enumerate(core):
                    target=decimals[i] if isinstance(decimals,list) and i<len(decimals) else None
                    places=decimal_places(target)
                    if isinstance(value,(int,float)) and not isinstance(value,bool) and places is not None:
                        val,text=rounded(value,places);rounded_list.append(val)
                        details.append({'index':i,'before':value,'decimal_places':places,'rounded_decimal_text':text,'after':val})
                    else:rounded_list.append(value)
                if details:round_candidates=[{'operation':'round_numeric_list_items_by_target_position','items':details,'value':rounded_list}]
            if not round_candidates:
                rec['stages']['3']={'status':'不适用','reason':'string_exact or list without aligned numeric items' if not is_numeric else 'no numeric candidate'}
            else:
                trials=[];match=None
                for candidate in round_candidates:
                    score,event=compare(metric,candidate['value'],norm_gold)
                    trials.append({'candidate':candidate,'score':score,'event':event})
                    if score==1 and match is None:match=candidate
                rec['stages']['3']={'status':'对上' if match is not None else '未对上','metric':metric,'trials':trials,'matched_candidate':match}
                if match is not None and rec['first_match'] is None:rec.update(first_match=3,matched_using=match)
            if rec['first_match'] is None:rec['first_match']='各适用档均未对上'
        rows.append({'题号':tid,'答案类型':kind,'最终答案原文':display(answer),'标准答案原文':display(gold),
                     '最终答案原值类型':type(answer).__name__,'标准答案原值类型':type(gold).__name__,
                     '第0档_029最终状态':old['最终状态'],'第0档_029分数':old['最终分数'],'第0档是否对上':rec['stages']['0']['status'],
                     **{f'第{i}档是否对上':rec['stages'][str(i)]['status'] for i in [1,2,3]},
                     '第一次对上的档':rec['first_match'],
                     '对上时用的是什么':json.dumps(rec['matched_using'],ensure_ascii=False) if rec['matched_using'] is not None else '',
                     '标准答案是否原样出现在答案文本里':('不适用' if rec['gold_literal_substring_in_answer'] is None else ('是' if rec['gold_literal_substring_in_answer'] else '否')),
                     '题面中关于答案形式的原句':'\n'.join(x['text'] for x in rec['format_sentences']),
                     '第0档分数来源':old['来源文件字段']})
        records.append(rec)
    first=collections.Counter(str(r['first_match']) for r in records)
    stage_counts={str(i):dict(collections.Counter(r['stages'][str(i)]['status'] for r in records)) for i in range(4)}
    assert first['不适用']==2 and first['无答案']==1
    for p,h in sources.items():assert hashfile(ROOT/p)==h
    summary={'selected_tasks':42,'eligible_tasks':39,'first_match_counts':dict(first),'each_stage_status_counts':stage_counts,
             'matched_tasks':[r['task_id'] for r in records if isinstance(r['first_match'],int)],
             'unmatched_eligible_tasks':[r['task_id'] for r in records if r['first_match']=='各适用档均未对上'],
             'not_applicable_tasks':[r['task_id'] for r in records if r['first_match']=='不适用'],
             'no_answer_tasks':[r['task_id'] for r in records if r['first_match']=='无答案'],
             'format_sentence_tasks':sum(bool(r['format_sentences']) for r in records),
             'format_sentence_count':sum(len(r['format_sentences']) for r in records),
             'metric_calls':len(events),'model_calls':0,'network_disabled':True,
             'official_definition_provenance':definitions,'source_sha256_before_and_after':sources,'all_sources_unchanged':True}
    with Path(str(PREFIX)+'_tolerance.csv').open('x',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    dump(Path(str(PREFIX)+'_tolerance_details.json'),records)
    dump(Path(str(PREFIX)+'_metric_calls.json'),events)
    dump(Path(str(PREFIX)+'_tolerance_summary.json'),summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ['source_sha256_before_and_after','official_definition_provenance']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
