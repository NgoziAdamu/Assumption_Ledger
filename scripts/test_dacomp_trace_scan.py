"""Known-answer checks for the task 008 mechanical scan rules."""

import json
from pathlib import Path
import tempfile
import unittest

import duckdb

from dacomp_trace_scan import contract_index, contract_sources, profile_table, protect_constant_values, runtime_hits, sql_scan
from scan_dacomp_delivery import json_strings, sentence_units, status_for


class ScanTests(unittest.TestCase):
    def sql(self,text,columns=None):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'query.sql';path.write_text(text)
            return sql_scan(path,columns)

    def test_literals_and_functions(self):
        result=self.sql('SELECT CAST(NULL AS VARCHAR) AS a, NULL AS b, 0 AS c, -2 AS d, true AS e, CAST(1 AS BIGINT) AS f, coalesce(x,0) AS g, 1+2 AS h FROM raw.x')
        self.assertEqual([o['name'] for o in result['null_literal_outputs']],['a','b'])
        self.assertEqual([o['name'] for o in result['constant_literal_outputs']],['c','d','e','f'])

    def test_reachable_ctes_and_scalar_subquery(self):
        result=self.sql('WITH unused AS (SELECT * FROM raw.unused), used AS (SELECT * FROM raw.used) SELECT (SELECT max(v) FROM raw.scalar) AS v FROM used')
        self.assertEqual({s['canonical'] for s in result['sources']},{'raw.used','raw.scalar'})

    def test_cte_star_propagates_null_and_union_branches(self):
        result=self.sql('WITH t AS (SELECT CAST(NULL AS VARCHAR) AS a, 3 AS b) SELECT * FROM t UNION ALL SELECT x AS a, 4 AS b FROM raw.other')
        self.assertEqual([o['name'] for o in result['null_literal_outputs']],['a'])
        self.assertEqual(len(result['outputs'][0]['alternatives']),2)
        self.assertEqual({s['canonical'] for s in result['sources']},{'raw.other'})

    def test_values_projection_and_generated_rows(self):
        result=self.sql("SELECT * FROM (VALUES ('US',NULL,1,CURRENT_TIMESTAMP),('UK',NULL,2,CURRENT_TIMESTAMP)) t(code,x,n,at)")
        self.assertEqual([o['name'] for o in result['outputs']],['code','x','n','at'])
        self.assertEqual([o['name'] for o in result['null_literal_outputs']],['x'])
        self.assertEqual([o['name'] for o in result['constant_literal_outputs']],['code','n'])
        result=self.sql('SELECT * FROM raw.x CROSS JOIN range(1,3) r')
        self.assertEqual({s['canonical'] for s in result['sources']},{'raw.x'})
        self.assertEqual(result['unresolved_source_expressions'],[])
        self.assertEqual(len(result['row_generator_expressions']),1)

    def test_profiles_null_and_constants(self):
        with duckdb.connect(':memory:') as connection:
            connection.execute('CREATE TABLE x AS SELECT * FROM (VALUES (1,1,NULL,7),(2,2,NULL,7),(NULL,NULL,NULL,7)) t(a,b,c,d)')
            result=profile_table(connection,'main','x',[])
            self.assertEqual([c['column'] for c in result['all_null_columns']],['c'])
            self.assertEqual([c['column'] for c in result['constant_nonnull_columns']],['d'])
            group=result['equal_column_groups'][0]
            self.assertEqual(group['columns'],['a','b'])
            self.assertEqual(group['nonnull_equal_rows'],2)
            self.assertEqual(group['both_null_rows_ignored'],1)
        output={'constant_nonnull_columns':[{'column':'sid','value':'AC'+'0'*32}]}
        protect_constant_values(output)
        self.assertIsNone(output['constant_nonnull_columns'][0]['value'])
        self.assertEqual(output['constant_nonnull_columns'][0]['value_length'],34)
        self.assertEqual(len(output['constant_nonnull_columns'][0]['value_sha256']),64)

    def test_equal_marginals_are_not_equal_columns(self):
        with duckdb.connect(':memory:') as connection:
            connection.execute('CREATE TABLE x AS SELECT * FROM (VALUES (1,2),(2,1)) t(a,b)')
            result=profile_table(connection,'main','x',[])
            self.assertEqual(result['equal_column_groups'],[])
            self.assertEqual(result['equal_column_confirmation_queries'][0]['mismatch_rows'],2)

    def test_one_sided_null_differs_and_empty_not_all_null(self):
        with duckdb.connect(':memory:') as connection:
            connection.execute('CREATE TABLE x AS SELECT * FROM (VALUES (1,1),(NULL,2)) t(a,b)')
            self.assertEqual(profile_table(connection,'main','x',[])['equal_column_groups'],[])
            connection.execute('DELETE FROM x')
            result=profile_table(connection,'main','x',[])
            self.assertTrue(result['zero_rows']);self.assertEqual(result['all_null_columns'],[])
            self.assertEqual(result['equal_column_groups'],[])

    def test_runtime_locations_and_context(self):
        text="SELECT CURRENT_DATE, now(), today();\n-- GETDATE()\nSELECT 'CURRENT_TIMESTAMP', \"TODAY\", 'now';"
        hits=runtime_hits(text,'query.sql',sql=True)
        self.assertEqual([h['line'] for h in hits],[1,1,1,2,3,3,3])
        self.assertEqual([h['context'] for h in hits],['code','code','code','comment','string','quoted_identifier','relative_time_string_lexeme_uninterpreted'])

    def test_contract_originals_and_no_inferred_source(self):
        text='staging_contract:\n  tables:\n    - name: x\n      description: something\n      source_table: raw.x\n      columns:\n        - name: id\n          description: ID one\n        - name: other_id\n          data_type: VARCHAR\n    - name: y\n      description: no source\n      columns:\n        - name: id\n          data_type: INTEGER\nmodeling_spec: {}\n'
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'contract.yaml';path.write_text(text)
            index,_=contract_index(path)
            self.assertNotIn('name: y',index[('staging','x')][0]['original_text'])
            self.assertNotIn('name: other_id',index[('staging','x')][0]['columns']['id']['original_text'])
            self.assertEqual(contract_sources(index[('staging','x')])['canonical_names'],['raw.x'])
            self.assertEqual(contract_sources(index[('staging','y')])['status'],'契约未指定')

    def test_json_paths_offsets_and_sentence_boundaries(self):
        text=json.dumps({'instruction':'placeholder.','trajectory':[{'content':'NULL\nTable x is empty. Keep x.y!'}]},indent=2)
        fields=list(json_strings(text))
        self.assertEqual(fields[-1][0],['trajectory',0,'content'])
        for trail,value,start,end in fields:self.assertEqual(json.loads(text[start:end]),value)
        self.assertEqual([s[0] for s in sentence_units(fields[-1][1])],['NULL','Table x is empty.',' Keep x.y!'])

    def test_status_priority_and_original_sources(self):
        task='impl-001';key=('marts','x');full=(task,*key)
        tolerance={full:{'whole_match_level':'L3','scope':'cs','prediction_database':'private'}}
        failed={'004':set(),'005':{full}}
        self.assertEqual(status_for(task,key,True,tolerance,{},failed)['status'],'待标注')
        self.assertEqual(status_for(task,key,False,tolerance,{},failed)['status'],'不可评估')
        self.assertEqual(status_for(task,key,True,tolerance,{full:{'current_pred_execution':False,'gold':{'exists':True}}},failed)['status'],'不可评估')
        outside=status_for('impl-025',key,True,{}, {}, {'004':set(),'005':set()})
        self.assertEqual(outside['status'],'官方判为通过')
        self.assertIn('records/005_cs_selection.json',outside['status_sources'][0]['records'])


if __name__=='__main__':unittest.main()
