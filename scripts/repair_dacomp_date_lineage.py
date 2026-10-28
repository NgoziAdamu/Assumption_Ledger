"""Complete output lineage metadata from saved 011 snapshots, without executing SQL nodes."""

import json
from pathlib import Path
import sys

import duckdb

from align_dacomp_agent_dates import output_clock_columns, degeneracy
from complete_dacomp_comparisons import PROJECT, RECORDS, save, stamp


def main():
    sys.path.insert(0,str(PROJECT/'src'));from de_gold_dependencies import source_dependency
    corrections=[]
    for path in sorted(RECORDS.glob('011_alignment_impl-*.json')):
        doc=json.loads(path.read_text());changed=False
        for entry in doc['tables']:
            for attempt in entry['attempts']:
                previous=attempt.get('output_lineage',{}).get('unresolved_outputs',[])
                if not previous or attempt.get('after',{}).get('comparison_status')!='compared':continue
                snapshot=Path(attempt['prediction_snapshot']);hybrid=snapshot.parent/(entry['scope']+'_inputs.duckdb')
                raw=Path(entry['agent_sql_path']).read_bytes().decode('utf-8')
                source=source_dependency(Path(entry['initial_database'] if entry['scope']=='staging' else entry['gold_database']))
                with duckdb.connect(str(hybrid),read_only=True) as inputs:
                    if source:inputs.execute("ATTACH '"+str(source).replace("'","''")+"' AS source (READ_ONLY)")
                    lineage=output_clock_columns(raw,inputs,entry['table'],entry['comparison_schema'],[c['name'] for c in attempt['after']['prediction']['columns']])
                with duckdb.connect(str(snapshot),read_only=True) as pred,duckdb.connect(entry['gold_database'],read_only=True) as gold:
                    flags=degeneracy(pred,gold,entry['table'],entry['comparison_schema'],lineage)
                corrections.append({'task':entry['task'],'table':entry['table'],'candidate_date':attempt['candidate_date'],
                    'previous_unresolved':previous,'remaining_unresolved':lineage['unresolved_outputs'],
                    'fix':'Assign analysis-only aliases to unaliased output expressions by output ordinal; never execute the modified analysis AST.',
                    'agent_SQL_reexecuted':False,'comparison_numbers_changed':False})
                attempt['output_lineage']=lineage;attempt['degeneracy']=flags;changed=True
        if changed:save(path,doc)
    save(RECORDS/'011_lineage_refinement.json',{'completed_at':stamp(),'corrections':corrections,'SQL_node_executions':0})
    print('Lineage refinements',len(corrections),'remaining unresolved',sum(len(c['remaining_unresolved']) for c in corrections))


if __name__=='__main__':main()
