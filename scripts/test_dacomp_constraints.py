"""Known-answer checks for literal declaration extraction and SQL constraint counts."""

import json
from pathlib import Path
import tempfile
import unittest
import duckdb

from check_dacomp_constraints import extract_contract, grain_columns, inspect_table, KINDS, summarize
from compare_dacomp_staging import fingerprint


def entry(grain=None, pk=None, not_null=None, unique=None, columns=None):
    return {"table":"fixture","layer":"staging","declared_columns":columns or ['id','other'],
            "declarations":{"grain":[{"raw_text":grain,**grain_columns(grain,columns or ['id','other'])}] if grain is not None else [],
                            "primary_key":[{"columns":pk}] if pk else [],
                            "not_null":[{"columns":[c]} for c in not_null or []],
                            "unique":[{"columns":[c]} for c in unique or []]}}


class ConstraintTests(unittest.TestCase):
    def test_constraint_forms_and_raw_grain(self):
        source = '''staging_contract:
  tables:
    - name: fixture
      grain: "One row per (id, other)"
      primary_key: [id, other]
      columns:
        - name: id
          constraints: [not_null, unique]
          tests: [not_null]
        - name: other
          tests: [not_null, {accepted_values: {values: [a, b]}}]
modeling_spec:
  intermediate_models: []
'''
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'contract.yaml';path.write_text(source)
            table=extract_contract(path)['tables'][0]
            self.assertEqual(table['declarations']['primary_key'][0]['columns'],['id','other'])
            self.assertEqual(len(table['declarations']['not_null']),2)
            self.assertEqual(len(table['declarations']['not_null'][0]['sources']),2)
            self.assertEqual(table['declarations']['grain'][0]['raw_text'],'One row per (id, other)')
            self.assertIn('grain: "One row per (id, other)"',table['declarations']['grain'][0]['sources'][0]['original_excerpt'])
            self.assertEqual(len(table['other_declared_tests_not_executed']),1)
            self.assertEqual(path.read_text(),source)

    def test_conservative_grain(self):
        columns=['id','date_day','source_relation']
        for text in ['One row per id per date_day','One row per (id, date_day)','One row per unique combination of id, date_day','One row per `id` + source_relation with active status']:
            self.assertEqual(grain_columns(text,columns)['status'],'parsed',text)
        for text in ['One row per lead','One row per id; duplicates preserved','One or more rows per id','One row per id per matching child record','One row per id and additional context fields','Exactly one row per run','One row per id-account scope']:
            self.assertEqual(grain_columns(text,columns)['status'],'unparsed',text)
        self.assertEqual(grain_columns(None,columns)['status'],'not_declared')
        annotated=grain_columns('One row per id (source_id) per date_day (source_date)',columns)
        self.assertEqual(annotated['columns'],['id','date_day'])
        self.assertEqual(grain_columns('One row per id (per build date = date_day)',columns)['status'],'unparsed')

    def test_repeated_table_definitions_preserve_sources_and_one_table(self):
        source='''staging_contract:
  tables:
    - name: fixture
      grain: One row per id
      columns:
        - name: id
          constraints: [not_null]
    - name: fixture
      grain: One row per id
      columns:
        - name: id
          tests: [not_null, unique]
modeling_spec:
  intermediate_models: []
'''
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'contract.yaml';path.write_text(source);result=extract_contract(path)
            self.assertEqual(result['table_definition_entries'],2);self.assertEqual(len(result['tables']),1)
            table=result['tables'][0]
            self.assertEqual(len(table['definitions']),2)
            self.assertEqual(len(table['declarations']['not_null'][0]['sources']),2)
            self.assertEqual(len(table['declarations']['grain'][0]['sources']),2)
            self.assertEqual(len(table['declarations']['unique']),1)

    def test_raw_values_and_unique_null_policy(self):
        with duckdb.connect(':memory:') as conn:
            conn.execute("CREATE SCHEMA staging; CREATE TABLE staging.fixture(id VARCHAR,other INTEGER)")
            conn.execute("INSERT INTO staging.fixture VALUES (' A',1),('a',2),('a ',3),('',4),('null',5),(NULL,6),(NULL,7)")
            result=inspect_table(conn,entry(grain='One row per id',pk=['id'],not_null=['id'],unique=['id']))
            self.assertEqual(result['checks']['grain'][0]['duplicate_key_groups'],1)
            self.assertEqual(result['checks']['grain'][0]['rows_in_duplicate_groups'],2)
            self.assertEqual(result['checks']['not_null'][0]['sql_null_rows'],2)
            self.assertEqual(result['checks']['unique'][0]['duplicate_key_groups'],0)
            self.assertEqual(result['checks']['unique'][0]['including_nulls_duplicate_key_groups'],1)
            self.assertTrue(result['categories']['primary_key']['violated'])
            self.assertFalse(result['categories']['unique']['violated'])

    def test_composite_pk_duplicate_rows_and_nulls(self):
        with duckdb.connect(':memory:') as conn:
            conn.execute('CREATE SCHEMA staging; CREATE TABLE staging.fixture(id INTEGER,other INTEGER)')
            conn.execute('INSERT INTO staging.fixture VALUES (1,1),(1,1),(1,1),(2,NULL),(2,NULL),(3,4)')
            result=inspect_table(conn,entry(pk=['id','other'],not_null=['other']))
            check=result['checks']['primary_key'][0]
            self.assertEqual((check['duplicate_key_groups'],check['rows_in_duplicate_groups'],check['excess_duplicate_rows'],check['null_key_rows']),(2,5,3,2))
            self.assertEqual(result['checks']['not_null'][0]['sql_null_rows'],2)

    def test_missing_is_unknown_and_empty_is_zero(self):
        with duckdb.connect(':memory:') as conn:
            conn.execute('CREATE SCHEMA staging')
            missing=inspect_table(conn,entry(not_null=['id']))
            self.assertFalse(missing['table_exists']);self.assertIsNone(missing['row_count'])
            self.assertIsNone(missing['categories']['not_null']['violated'])
            conn.execute('CREATE TABLE staging.fixture(id INTEGER)')
            empty=inspect_table(conn,entry(not_null=['id']))
            self.assertTrue(empty['table_exists']);self.assertEqual(empty['row_count'],0)
            self.assertFalse(empty['categories']['not_null']['violated'])

    def test_missing_column_and_partial_known_violation(self):
        with duckdb.connect(':memory:') as conn:
            conn.execute('CREATE SCHEMA staging; CREATE TABLE staging.fixture(id INTEGER); INSERT INTO staging.fixture VALUES(NULL)')
            result=inspect_table(conn,entry(not_null=['id','other']))
            summary=result['categories']['not_null']
            self.assertTrue(summary['violated']);self.assertEqual(summary['unknown_checks'],1)
            self.assertEqual(result['checks']['not_null'][1]['status'],'columns_missing')

    def test_unparsed_grain_has_no_fallback_key(self):
        with duckdb.connect(':memory:') as conn:
            conn.execute('CREATE SCHEMA staging; CREATE TABLE staging.fixture(id INTEGER); INSERT INTO staging.fixture VALUES(1),(1)')
            result=inspect_table(conn,entry(grain='One row per source record'))
            self.assertEqual(result['checks']['grain'][0]['status'],'grain_unparsed')
            self.assertIsNone(result['categories']['grain']['violated'])
            self.assertIsNone(result['any_constraint_violated'])

    def test_case_insensitive_identifiers_and_count_alias(self):
        with duckdb.connect(':memory:') as conn:
            conn.execute('CREATE SCHEMA staging; CREATE TABLE staging.FIXTURE("__ledger_group_count" INTEGER); INSERT INTO staging.FIXTURE VALUES(1),(1)')
            result=inspect_table(conn,entry(unique=['__ledger_group_count'],columns=['__ledger_group_count']))
            self.assertEqual(result['checks']['unique'][0]['duplicate_key_groups'],1)

    def test_readonly_file_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'fixture.duckdb'
            with duckdb.connect(str(path)) as conn:
                conn.execute('CREATE SCHEMA staging; CREATE TABLE staging.fixture(id INTEGER); INSERT INTO staging.fixture VALUES(1),(1)')
            before=fingerprint(path)
            with duckdb.connect(str(path),read_only=True) as conn:
                self.assertTrue(inspect_table(conn,entry(unique=['id']))['categories']['unique']['violated'])
                with self.assertRaises(duckdb.Error):conn.execute('CREATE TABLE forbidden(id INTEGER)')
            self.assertEqual(before,fingerprint(path))

    def test_summary_counts_tables_and_tasks_separately(self):
        def side(bad):
            return {'any_constraint_violated':bad,'table_exists':True,'categories':{k:{'violated':bad} for k in KINDS}}
        records=[{'task':'impl-001','declarations':{k:[{}] for k in KINDS},'agent':side(True),'gold':side(True)},
                 {'task':'impl-001','declarations':{k:[{}] for k in KINDS},'agent':side(True),'gold':side(False)}]
        report=summarize(records)['grain']
        self.assertEqual(report['agent']['violating_tables'],2);self.assertEqual(report['agent']['violating_tasks'],1)
        self.assertEqual(report['both_violating_tables'],1)


if __name__=='__main__':unittest.main()
