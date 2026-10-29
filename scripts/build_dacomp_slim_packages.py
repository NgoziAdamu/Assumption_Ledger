"""Render compact Markdown from 012 evidence, preserving all required originals."""

from collections import Counter
import html
import json
from pathlib import Path
import re

from build_dacomp_annotation_packages import fence
from complete_dacomp_comparisons import ROOT,RECORDS,save
from prepare_dacomp_annotation import EXPORT,ARCHIVE
from scan_dacomp_delivery import sentence_units


def compact(value):
    return json.dumps(value,ensure_ascii=False,separators=(',',':'))


def cell(value):
    """Reversible HTML display escaping for one Markdown table cell."""
    text=value if isinstance(value,str) else compact(value)
    if re.fullmatch(r'[\w .,:()/+=–-]+',text,re.UNICODE):return html.escape(text,quote=False)
    return '<code>'+html.escape(text,quote=False).replace('|','&#124;').replace('\r','&#13;').replace('\t','&#9;').replace('\n','<br>')+'</code>'


def grid(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']+['| '+' | '.join(cell(v) for v in row)+' |' for row in rows])+'\n'


class Paths:
    def __init__(self):self.paths=[]
    def ref(self,path):
        original=Path(path)
        path=str(original.relative_to(ROOT)) if original.is_absolute() and original.is_relative_to(ROOT) else str(original)
        if path not in self.paths:self.paths.append(path)
        return 'S'+str(self.paths.index(path)+1)
    def render(self):return '仓库相对路径基准：`'+str(ROOT)+'`。\n\n'+'\n'.join('- S'+str(i+1)+': `'+p+'`' for i,p in enumerate(self.paths))+'\n'


def thought_sentences(task,table):
    root=EXPORT/'runs/20261025_de_official_batch_01'/task/'agent';all_events=[];sentences=[]
    for path in root.glob('.events/sessions/*/events/*.json'):all_events.append((path,json.loads(path.read_text())))
    for path,event in sorted(all_events,key=lambda r:r[1].get('id',-1)):
        if event.get('source')!='agent' or 'action' not in event:continue
        fields=[(name,event.get(name)) for name in ('thought','message')]+[('args.'+name,event.get('args',{}).get(name)) for name in ('thought','message')]
        for field,text in fields:
            if not isinstance(text,str):continue
            for sentence,start,end in sentence_units(text):
                if re.search(r'(?<![A-Za-z0-9_])'+re.escape(table)+r'(?![A-Za-z0-9_])',sentence,re.I):
                    sentences.append({'event_id':event['id'],'field':field,'original_text':sentence,'file':str(path),
                        'start_offset':start,'end_offset':end})
    return all_events,sentences


def constraints(agent):
    rows=[]
    for category,checks in agent.get('checks',{}).items():
        for check in checks:
            if check.get('violated') is not True:continue
            numbers={k:v for k,v in check.items() if isinstance(v,(int,float)) and not isinstance(v,bool)}
            rows.append([category,','.join(check['columns']),compact(numbers)])
    return rows


def true_flags(scan,excerpts,paths,limit):
    output=scan['output'];result=[]
    for flag,value in scan['trace_flags'].items():
        if value is not True:continue
        evidence=''
        if flag=='A1_zero_rows':evidence='行数='+str(output['row_count'])
        elif flag=='A2_all_null_column':
            items=output.get('all_null_columns') or [];evidence=str(len(items))+'列；'+compact(items[:limit])
        elif flag=='A3_constant_nonnull_column':
            items=output.get('constant_nonnull_columns') or []
            minimal=[{k:c[k] for k in ('column','value','value_sha256','value_omitted_reason') if k in c} for c in items[:limit]]
            evidence=str(len(items))+'列；'+compact(minimal)
        elif flag.startswith('A4_'):
            items=output.get('equal_column_groups') or []
            if flag.endswith('different_description_texts'):items=[g for g in items if g.get('has_pair_with_different_explicit_description')]
            evidence=str(len(items))+'组；'+compact([{'columns':g['columns'],'nonnull_equal_rows':g.get('nonnull_equal_rows'),'meaning_status':g.get('meaning_status')} for g in items[:limit]])
        elif flag.startswith(('B5_','B6_')):
            name='null_literal_outputs' if flag.startswith('B5_') else 'constant_literal_outputs'
            items=[o for sql in scan['agent_sql'] for o in sql.get(name,[])]
            examples=[]
            for o in items[:limit]:
                examples.append({'column':o['name'],'expression':[v['expression_sql'] for v in o['alternatives'][:1]]})
            evidence=str(len(items))+'输出列；'+compact(examples)
        elif flag=='B7_specified_not_read':evidence=compact(scan['source_comparison']['specified_but_not_read'][:limit])
        elif flag=='B7_read_not_specified':evidence=compact(scan['source_comparison']['read_but_not_specified'][:limit])
        elif flag=='B8_shared_single_source':
            group=scan.get('shared_single_source_targets',{});evidence='唯一源='+str(group.get('source'))+'；目标数='+str(len(group.get('targets',[])))+'；例='+compact(group.get('targets',[])[:limit])
        elif flag.startswith('C9_'):
            side='agent_sql' if 'agent_' in flag else 'gold_sql' if 'gold_' in flag else 'contract'
            hits=scan['time_dependencies'][side]['hits'];hit=hits[0]
            evidence=paths.ref(hit['path'])+':'+str(hit['line'])+' '+hit['matched_text']+'；命中数='+str(len(hits))
        elif flag.startswith('D10_'):
            name='final_report_keyword_excerpt_ids' if 'final_report' in flag else 'any_result_keyword_excerpt_ids'
            ids=scan.get(name,[]);selected=[excerpts[i] for i in ids if i in excerpts]
            evidence='命中数='+str(len(selected))+'；'
            if selected:
                e=min(selected,key=lambda r:len(r['original_text']));evidence+=e['origin']+' '+e['original_text']
        result.append([flag,evidence or '008 记录为 True；证据见完整 012 材料包'])
    return result


def render(doc,inventory,examples=3,key_examples=5,evidence_limit=3):
    basic=doc['basic_information'];difference=doc['differences'];paths=Paths();parts=[];exempt=0
    basis=basic['difference_source'];record=paths.ref(str(ROOT/basis['record']));paths.ref(str(ROOT/basis['detail_record']))
    parts.append('# '+basic['task']+' | '+basic['layer']+' | '+basic['table']+' | 差异：'+record+'；日期 '+str(basis['candidate_date'] or '原记录')+'\n')
    contract=doc['contract_specification'];contract_ref=paths.ref(contract['source_path'])
    section='\n## 契约完整原文\n\n'
    for block in contract['blocks']:
        section+=contract_ref+':'+str(block['start_line'])+'–'+str(block['end_line'])+'\n\n'+fence(block['original_text'],'yaml');exempt+=len(block['original_text'])
    parts.append(section)
    for name,label in [('agent_final_SQL','agent 最终 SQL'),('gold_SQL_仅供定位差异','gold SQL（仅供定位差异）')]:
        section='\n## '+label+'\n\n'
        for source in doc[name]:
            section+=paths.ref(source['path'])+'\n\n'+fence(source['text'],'sql');exempt+=len(source['text'])
        parts.append(section)
    stats=difference['key_statistics']
    rest='\n## 差异（L0；沿用 012 选定结果）\n\n'
    rest+=grid(['agent 行','gold 行','仅 agent 键','仅 gold 键','agent 重复键组','gold 重复键组'],[[difference['prediction_rows'],difference['gold_rows'],stats['pred_only_keys'],stats['gold_only_keys'],stats['pred_duplicate_key_groups'],stats['gold_duplicate_key_groups']]])
    rest+='\n列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。\n\n'
    rows=[]
    key_ids={};key_values=[]
    for c in difference['column_details']:
        for sample in c['sample_key_groups'][:examples]:
            serialized=compact(sample['key_normalized'])
            if serialized not in key_ids:
                key_ids[serialized]='K'+str(len(key_ids)+1);key_values.append([key_ids[serialized],sample['key_normalized']])
    if key_values:rest+='\n样例键映射：\n\n'+grid(['键代号','完整规范化键'],key_values)
    for c in difference['column_details']:
        n=c['l0_counts_verbatim'];rows.append([c['column'],n['mismatch_rows_or_minimum_pairs'],n['pred_unmatched_value_occurrences'],n['gold_unmatched_value_occurrences'],c['agent_actual_type'],c['gold_actual_type']])
    rest+='\n'+grid(['列','不一致行/最少对数','agent 未抵消次数','gold 未抵消次数','agent 类型','gold 类型'],rows)
    for c in difference['column_details']:
        if not c['sample_key_groups']:continue
        rest+='\n'+c['column']+' 样例：\n\n';rows=[]
        for sample in c['sample_key_groups'][:examples]:
            if sample['kind']=='one_to_one':a,g=sample['agent_value'],sample['gold_value']
            else:a,g=sample['agent_values'],sample['gold_values']
            rows.append([key_ids[compact(sample['key_normalized'])],a,g])
        rest+=grid(['键','agent 值','gold 值'],rows)
        if any(s['kind']!='one_to_one' for s in c['sample_key_groups'][:examples]):rest+='重复键为同键值/次数，列表位置不是唯一配对。\n'
    rest+='\n独有键样例：\n\n'+grid(['仅 agent 原始键','仅 gold 原始键'],[[
        [e['key_raw_text'] for e in difference['one_side_key_examples']['prediction_only'][:key_examples]],
        [e['key_raw_text'] for e in difference['one_side_key_examples']['gold_only'][:key_examples]]]])
    rest+='\n## 006：仅 agent 违反的约束\n\n';paths.ref(str(ROOT/doc['agent_constraints_006']['source_record']))
    violations=constraints(doc['agent_constraints_006']['agent'])
    rest+=grid(['约束','列','违反计数'],violations) if violations else '未记录违反为 True 的约束。\n'
    rest+='\n## 008：仅 True 痕迹与最少证据\n\n';paths.ref(str(ROOT/'records/008_table_scan.jsonl'))
    excerpts={r['excerpt_id']:r for r in map(json.loads,(RECORDS/'008_keyword_excerpts.jsonl').read_text().splitlines())}
    flags=true_flags(doc['all_markers_and_evidence_008']['verbatim_record'],excerpts,paths,evidence_limit)
    rest+=grid(['标记','最少证据（多项只列少量例子）'],flags) if flags else '没有 True 痕迹。\n'
    events,sentences=thought_sentences(basic['task'],basic['table']);event_index={e['id']:(p,e) for p,e in events}
    eventdirs=sorted({'dacomp_deimpl_prev/'+p.parent.relative_to(EXPORT).as_posix()+'/' for p,e in events})
    rest+='\n## 轨迹索引（不放输出原文）\n\n本题事件总数：'+str(len(events))+'；归档：'+paths.ref(ARCHIVE)+'。\n'
    rest+='\n归档事件目录：\n'+''.join('- '+p+'\n' for p in eventdirs)+'\n';index_rows=[];manifest_index=[]
    for step in doc['trace_excerpts']['steps']:
        path,event=event_index[step['event_id']];command=event.get('args',{}).get('command','');output_events=[e for p,e in events if e.get('observation') and e.get('cause')==event['id']]
        text='\n'.join(e.get('content','') for e in output_events)
        mentions=bool(re.search(r'(?<![A-Za-z0-9_])'+re.escape(basic['table'])+r'(?![A-Za-z0-9_])',text,re.I))
        truncated=any(o['truncation']['status']=='原记录显式截断' for o in step['outputs'])
        count=sum(len(e.get('content','')) for e in output_events)
        index_rows.append([event['id'],event['action'],command[:200],count,mentions,truncated])
        manifest_index.append({'event_id':event['id'],'action':event['action'],'command_prefix':command[:200],
            'output_characters':count,'output_mentions_table':mentions,'original_truncation_marker':truncated})
    rest+=grid(['事件','动作','命令原文前 200 字符','输出字符','输出含本表名','显式截断'],index_rows)
    rest+='\n### agent action 的 thought/message 命中原句\n\n'
    for sentence in sentences:
        rest+='event '+str(sentence['event_id'])+' / '+sentence['field']+'\n\n'+fence(sentence['original_text'])
    if not sentences:rest+='未找到命中原句。\n'
    rest+='\n## result.md 本表名原句\n\n';result=doc['result_md_table_sentences']
    if result['present']:
        ref=paths.ref(result['path'])
        for sentence in result['sentences']:rest+=ref+':'+str(sentence['start_line'])+'\n\n'+fence(sentence['original_text'])
        if not result['sentences']:rest+='原文件未出现本表名。\n'
    else:rest+='未找到 result.md。\n'
    paths.ref(str(ROOT/'records/012_packages'/(inventory['stem']+'.json')))
    paths.ref(difference['prediction_database']);paths.ref(difference['gold_database'])
    paths.ref(str(EXPORT/'runs/20261025_de_official_batch_01'/basic['task']/'agent/.events/sessions'))
    rest+='\n## 原始文件路径（集中列一次）\n\n'+paths.render()
    parts.append(rest);text=''.join(parts)
    return text,{'characters':len(text),'SQL_contract_original_characters':exempt,'without_SQL_contract_original_characters':len(text)-exempt,
        'without_SQL_contract_sections_characters':len(parts[0])+len(rest),'thought_message_sentence_characters':sum(len(s['original_text']) for s in sentences),
        'thought_message_sentence_count':len(sentences),'thought_message_events':[{'event_id':s['event_id'],'field':s['field'],'characters':len(s['original_text'])} for s in sentences],
        'event_count':len(events),'event_directories':eventdirs,'trace_index':manifest_index,'true_flag_count':len(flags),
        'violated_constraint_count':len(violations),'examples_per_column_limit':examples,'exclusive_key_examples_limit':key_examples,
        '008_evidence_examples_limit':evidence_limit}


def main():
    inventory=json.loads((RECORDS/'012_package_inventory.json').read_text());directory=RECORDS/'013_packages';directory.mkdir(exist_ok=True)
    result=[]
    for item in inventory:
        doc=json.loads((RECORDS/'012_packages'/(item['stem']+'.json')).read_text())
        text,summary=render(doc,item)
        if summary['without_SQL_contract_original_characters']>15000:text,summary=render(doc,item,examples=1,key_examples=3,evidence_limit=1)
        if summary['without_SQL_contract_original_characters']>15000:text,summary=render(doc,item,examples=1,key_examples=1,evidence_limit=1)
        stem=item['stem'].replace('012_','013_',1);path=directory/(stem+'.md');path.write_bytes(text.encode('utf-8'))
        row={'task':item['task'],'layer':item['layer'],'table':item['table'],'path':str(path.relative_to(ROOT)),
            'source_012':f"records/012_packages/{item['stem']}.json",**summary,
            'exceeds_15000':summary['without_SQL_contract_original_characters']>15000,
            'required_originals_truncated':False}
        result.append(row);print(item['task'],'all',summary['characters'],'excluding originals',summary['without_SQL_contract_original_characters'],flush=True)
    save(RECORDS/'013_package_inventory.json',result)


if __name__=='__main__':main()
