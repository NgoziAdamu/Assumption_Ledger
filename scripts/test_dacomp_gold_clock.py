"""Known-answer tests for byte-preserving clock substitution and full row checks."""

from pathlib import Path
import tempfile
import unittest

import duckdb

from complete_dacomp_comparisons import ROOT
from dacomp_gold_clock import freeze_sql,compare_full_rows


class GoldClockTests(unittest.TestCase):
    def test_only_runtime_functions_change(self):
        text="-- CURRENT_DATE\nWITH today AS (SELECT CURRENT_DATE AS today, CURRENT_TIMESTAMP AS ts)\nSELECT today, 'CURRENT_DATE', \"CURRENT_TIMESTAMP\", now() FROM today;\n"
        frozen,changes=freeze_sql(text,'2025-10-11','test.sql')
        self.assertEqual(len(changes),3)
        self.assertIn('-- CURRENT_DATE',frozen);self.assertIn('WITH today AS',frozen)
        self.assertIn("'CURRENT_DATE'",frozen);self.assertIn('FROM today;',frozen)
        cursor=0;parts=[]
        for c in changes:
            self.assertEqual(text[c['start_offset']:c['end_offset']],c['original_text'])
            parts.extend([text[cursor:c['start_offset']],c['replacement_text']]);cursor=c['end_offset']
        parts.append(text[cursor:]);self.assertEqual(''.join(parts),frozen)

    def test_optional_parentheses_and_midnight(self):
        frozen,changes=freeze_sql('SELECT current_date(), today(), getdate(), current_timestamp;','2025-10-12')
        self.assertEqual(len(changes),4)
        self.assertEqual([c['replacement_kind'] for c in changes[:2]],['date','date'])
        self.assertIn('00:00:00+00:00',frozen)
        raw=b'SELECT CURRENT_DATE d;\r\n-- keep CRLF\r\n'
        frozen,_=freeze_sql(raw.decode(),'2025-10-12')
        self.assertEqual(frozen.encode().count(b'\r\n'),2)

    def test_create_view_statement_is_preserved(self):
        text='create schema if not exists marts;\ncreate or replace view marts.x as select CURRENT_DATE d;\n'
        frozen,_=freeze_sql(text,'2025-10-12')
        self.assertTrue(frozen.startswith('create schema if not exists marts;\ncreate or replace view marts.x'))

    def compare(self,rows,expected):
        parent=ROOT/'data/010_test_scratch';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            gold=Path(temp)/'gold.duckdb'
            with duckdb.connect(str(gold)) as connection:
                connection.execute('CREATE TABLE x AS '+expected)
            with duckdb.connect(':memory:') as connection:
                connection.execute('CREATE TABLE x AS '+rows)
                connection.execute("ATTACH '"+str(gold)+"' AS gold_clock_reference (READ_ONLY)")
                cols=[r[0] for r in connection.execute('DESCRIBE x').fetchall()]
                return compare_full_rows(connection,'main','x','main',cols,Path(temp))

    def test_full_multiset_counts(self):
        self.assertTrue(self.compare('SELECT * FROM (VALUES(1),(1),(2)) t(a)','SELECT * FROM (VALUES(2),(1),(1)) t(a)')['l0_full_match'])
        self.assertFalse(self.compare('SELECT * FROM (VALUES(1),(2),(2)) t(a)','SELECT * FROM (VALUES(2),(1),(1)) t(a)')['l0_full_match'])

    def test_date_only_does_not_round_numeric_values(self):
        result=self.compare("SELECT TIMESTAMP '2025-10-11 00:00:00' ts,1.001 n","SELECT TIMESTAMP '2025-10-11 12:00:00' ts,1.002 n")
        self.assertFalse(result['date_only_full_match'])
        result=self.compare("SELECT TIMESTAMP '2025-10-11 00:00:00' ts,1.001 n","SELECT TIMESTAMP '2025-10-11 12:00:00' ts,1.001 n")
        self.assertFalse(result['l0_full_match']);self.assertTrue(result['date_only_full_match'])

    def test_spillable_full_rows_engine(self):
        parent=ROOT/'data/010_test_scratch';parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            gold=Path(temp)/'gold.duckdb'
            select="SELECT range id,range%7 n,range%3 k,'text' s,TIMESTAMP '2025-10-12 12:00:00' ts FROM range(100001)"
            with duckdb.connect(str(gold)) as connection:connection.execute('CREATE TABLE x AS '+select)
            with duckdb.connect(':memory:') as connection:
                connection.execute('CREATE TABLE x AS '+select.replace('12:00:00','00:00:00'))
                connection.execute("ATTACH '"+str(gold)+"' AS gold_clock_reference (READ_ONLY)")
                result=compare_full_rows(connection,'main','x','main',['id','n','k','s','ts'],Path(temp))
                self.assertEqual(result['engine'],'duckdb_exact_weighted_rows')
                self.assertFalse(result['l0_full_match']);self.assertTrue(result['date_only_full_match'])


if __name__=='__main__':unittest.main()
