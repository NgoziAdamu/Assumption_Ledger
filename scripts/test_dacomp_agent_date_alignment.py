"""Fixture checks for task 011's fixed keys, clock lineage and degeneracy flags."""

from pathlib import Path
import tempfile
import unittest

import duckdb

from align_dacomp_agent_dates import compare, degeneracy, output_clock_columns


class AlignmentTests(unittest.TestCase):
    def test_fixed_key_and_l1_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);pred=root/'pred.duckdb';gold=root/'gold.duckdb'
            for path,query in [(pred,"SELECT 'A' id,'1573.0' v"),(gold,"SELECT 'a' id,'1573' v")]:
                with duckdb.connect(str(path)) as con:con.execute('CREATE SCHEMA staging; CREATE TABLE staging.x AS '+query)
            row={'table':'x','comparison_schema':'staging','comparison_columns':['id','v'],'key_columns':['id'],
                 'before':{'alignment':{'pred_duplicate_key_groups':0,'gold_duplicate_key_groups':0}}}
            r=compare(pred,gold,row,root)
            self.assertEqual(r['whole_match_level'],'L1')
            self.assertEqual(r['alignment']['columns'],['id'])
            self.assertEqual(r['current_key_statistics']['shared_keys'],1)
            self.assertEqual(next(c['mismatch_rows_or_minimum_pairs'] for c in r['l0_column_differences'] if c['column']=='v'),1)
            self.assertEqual(next(c['mismatch_rows_or_minimum_pairs'] for c in r['l3_column_differences'] if c['column']=='v'),0)

    def test_lineage_reaches_cte_arithmetic_but_not_filter(self):
        raw="WITH q AS (SELECT id, date_diff('day',d,current_date) age FROM raw.x WHERE d<current_date) SELECT id,age+1 AS adjusted FROM q"
        with duckdb.connect() as con:
            con.execute("CREATE SCHEMA raw; CREATE TABLE raw.x AS SELECT 1 id,DATE '2025-01-01' d; CREATE SCHEMA staging; CREATE TABLE staging.x AS "+raw)
            result=output_clock_columns(raw,con,'x','staging')
            self.assertEqual([c['column'] for c in result['runtime_output_columns']],['adjusted'])
            self.assertFalse(result['unresolved_outputs'])

    def test_l0_keeps_official_delimiter_hash_anchor_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);pred=root/'pred.duckdb';gold=root/'gold.duckdb'
            for path,query in [(pred,"SELECT 1 id,'a|b' a,'c' b"),(gold,"SELECT 1 id,'a' a,'b|c' b")]:
                with duckdb.connect(str(path)) as con:con.execute('CREATE SCHEMA staging; CREATE TABLE staging.x AS '+query)
            row={'table':'x','comparison_schema':'staging','comparison_columns':['a','b'],'key_columns':['id'],
                 'before':{'alignment':{'pred_duplicate_key_groups':0,'gold_duplicate_key_groups':0}}}
            result=compare(pred,gold,row,root)
            self.assertEqual(result['whole_match_level'],'L0')
            self.assertTrue(result['l0_official_hash_multiset_match'])
            self.assertFalse(result['l0_exact_row_tuple_match'])

    def test_empty_and_null_are_distinct_flags(self):
        with duckdb.connect() as pred,duckdb.connect() as gold:
            for con in [pred,gold]:con.execute('CREATE SCHEMA staging; CREATE TABLE staging.x(id INTEGER,clock INTEGER)')
            line={'runtime_output_columns':[{'column':'clock'}],'unresolved_outputs':[]}
            result=degeneracy(pred,gold,'x','staging',line)
            self.assertTrue(result['both_zero_rows']);self.assertFalse(result['clock_output_degeneracy'])
            for con in [pred,gold]:con.execute('INSERT INTO staging.x VALUES (1,NULL),(2,NULL)')
            result=degeneracy(pred,gold,'x','staging',line)
            self.assertFalse(result['both_zero_rows']);self.assertTrue(result['clock_output_degeneracy'])

    def test_single_value_mixed_with_null_is_not_whole_column_constant(self):
        with duckdb.connect() as pred,duckdb.connect() as gold:
            for con in [pred,gold]:con.execute('CREATE SCHEMA staging; CREATE TABLE staging.x AS SELECT 1 id,4 clock UNION ALL SELECT 2,NULL')
            result=degeneracy(pred,gold,'x','staging',{'runtime_output_columns':[{'column':'clock'}],'unresolved_outputs':[]})
            self.assertFalse(result['flagged'])

    def test_unaliased_cast_output_is_checked_by_projection_ordinal(self):
        raw="SELECT CAST(date_diff('day',DATE '2025-01-01',CURRENT_DATE) AS INTEGER), CAST(1 AS FLOAT)"
        with duckdb.connect() as con:
            con.execute('CREATE SCHEMA staging; CREATE TABLE staging.x AS '+raw)
            result=output_clock_columns(raw,con,'x','staging')
            self.assertFalse(result['unresolved_outputs'])
            self.assertEqual(len(result['runtime_output_columns']),1)



if __name__=='__main__':unittest.main()
