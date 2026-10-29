"""Readable exhaustive raw metadata/count differences from task 013 records."""

import csv
import json

from build_dacomp_annotation_packages import fence
from complete_dacomp_comparisons import RECORDS
from reconcile_dacomp_scope import jsonl


def main():
    rows=[r for r in jsonl(RECORDS/'013_raw_tables.jsonl') if r['different']]
    text='# 全部 raw 表清单 / 列结构 / 行数差异\n\n仅记录元数据与计数，不比较单元格值，不判断原因或操作是否正确。\n'
    task=None;flat=[]
    for row in rows:
        if row['task']!=task:task=row['task'];text+='\n## '+task+'\n'
        text+='\n### raw.'+row['table']+'\n\n'
        initial,agent=row['initial'],row['agent']
        text+='初始存在：'+str(row['initial_exists'])+'；agent 存在：'+str(row['agent_exists'])+'；初始行数：'+str(initial['row_count'] if initial else None)+'；agent 行数：'+str(agent['row_count'] if agent else None)+'。\n'
        for name in ('initial_only_columns','agent_only_columns','type_differences','column_order_differences'):
            if row[name]:text+='\n'+name+'\n\n'+fence(json.dumps(row[name],ensure_ascii=False,indent=2),'json')
        if not row['initial_exists'] or not row['agent_exists']:
            text+='\n存在一侧的完整列清单\n\n'+fence(json.dumps((initial or agent)['columns'],ensure_ascii=False,indent=2),'json')
        flat.append({'task':row['task'],'table':row['table'],'initial_exists':row['initial_exists'],'agent_exists':row['agent_exists'],
            'initial_rows':initial['row_count'] if initial else None,'agent_rows':agent['row_count'] if agent else None,
            'row_delta_agent_minus_initial':row['row_delta_agent_minus_initial'],
            **{name:json.dumps(row[name],ensure_ascii=False) for name in ('initial_only_columns','agent_only_columns','type_differences','column_order_differences')}})
    (RECORDS/'013_raw_differences.md').write_text(text)
    with (RECORDS/'013_raw_differences.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(flat[0]),lineterminator='\n');writer.writeheader();writer.writerows(flat)
    print('Exhaustive raw differences:',len(rows),'tables')


if __name__=='__main__':main()
