"""Compare retained agent inputs, task-011 initial inputs and retained raw schemas."""

import json
from pathlib import Path
import re

import duckdb

from compare_dacomp_staging import fingerprint
from complete_dacomp_comparisons import RECORDS,PROJECT,save,stamp
from prepare_dacomp_annotation import EXPORT
from reconcile_dacomp_scope import jsonl


def raw_schemas(path):
    with duckdb.connect(str(path),read_only=True) as connection:
        rows=connection.execute("SELECT table_name,column_name,data_type,ordinal_position FROM information_schema.columns WHERE table_catalog=current_database() AND table_schema='raw' ORDER BY table_name,ordinal_position").fetchall()
    result={}
    for table,name,kind,ordinal in rows:result.setdefault(table,[]).append({'name':name,'type':kind,'ordinal_position':ordinal})
    return result


def compare(left,right):
    tables=[]
    for name in sorted(set(left)|set(right)):
        a,b=left.get(name),right.get(name);ac={c['name']:c for c in a or []};bc={c['name']:c for c in b or []}
        tables.append({'table':name,'left_exists':a is not None,'right_exists':b is not None,'same_ordered_columns_and_types':a==b,
            'left_only_columns':[c for c in a or [] if c['name'] not in bc],
            'right_only_columns':[c for c in b or [] if c['name'] not in ac],
            'type_differences':[{'column':c,'left_type':ac[c]['type'],'right_type':bc[c]['type']} for c in ac.keys()&bc.keys() if ac[c]['type']!=bc[c]['type']],
            'left_columns':a,'right_columns':b})
    return {'all_raw_schemas_equal':left==right,'tables':tables}


def main():
    initial={r['task']:r['initial_database'] for r in jsonl(RECORDS/'011_table_alignment.jsonl')}
    results=[]
    for number,table in [(19,'stg_apple_store__app_session_daily'),(30,'stg_zuora__invoice')]:
        task=f'impl-{number:03d}';case=json.loads((RECORDS/f'006_contract_{task}.json').read_text())
        retained=Path(case['agent_database']);agent_input=retained.with_name(retained.stem+'_start.duckdb');used=Path(initial[task])
        inputs={label:{'path':str(path),'fingerprint':fingerprint(path),'raw_tables':raw_schemas(path)} for label,path in [('retained_agent_start',agent_input),('initial_used_011',used),('retained_agent_output_raw',retained)]}
        runner=retained.parent/'run.py';lines=runner.read_bytes().decode('utf-8').splitlines(keepends=True)
        code=[{'path':str(runner),'line':i+1,'original_text':line} for i,line in enumerate(lines) if '_start.duckdb' in line or 'source_db_path' in line]
        tracecalls=[];root=EXPORT/'runs/20261025_de_official_batch_01'/task/'agent'
        for path in root.glob('.events/sessions/*/events/*.json'):
            e=json.loads(path.read_text());command=e.get('args',{}).get('command','') if e.get('action')=='run' else ''
            for i,line in enumerate(command.splitlines(keepends=True),1):
                if re.search(r'\bpython\S*\s+run\.py\b',line):tracecalls.append({'path':str(path),'event_id':e['id'],'decoded_command_line':i,'original_text':line})
        comparison=compare(inputs['retained_agent_start']['raw_tables'],inputs['initial_used_011']['raw_tables'])
        results.append({'task':task,'table':table,'inputs':inputs,
            'retained_start_vs_011_initial':comparison,
            'same_start_file_sha256':inputs['retained_agent_start']['fingerprint']['sha256']==inputs['initial_used_011']['fingerprint']['sha256'],
            'agent_output_raw_vs_011_initial':compare(inputs['retained_agent_output_raw']['raw_tables'],inputs['initial_used_011']['raw_tables']),
            'runner_source_path_original_lines':code,'recorded_runner_command_lines':tracecalls,
            'historical_limit':'核对的是当前留存的 agent 工作目录 *_start.duckdb 与 011 所用初始库；未用文件 mtime 推断历史内容。运行前单独的数据库指纹未在所查 run_summary / 轨迹索引中找到。',
            'old_011_failure_records_modified':False,'comparison_or_status_conclusions_changed':False})
    save(RECORDS/'012_input_schema_checks.json',{'completed_at':stamp(),'tasks':results,'inspection':'原始库只读，仅比较表结构和原文，不判断错误原因'})
    for r in results:
        print(r['task'],'same SHA',r['same_start_file_sha256'],'same raw schema',r['retained_start_vs_011_initial']['all_raw_schemas_equal'],
            'different raw tables',[t['table'] for t in r['retained_start_vs_011_initial']['tables'] if not t['same_ordered_columns_and_types']])


if __name__=='__main__':main()
