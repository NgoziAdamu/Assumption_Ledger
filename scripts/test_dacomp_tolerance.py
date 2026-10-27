"""Known-answer tolerance tests, including SQL/Python parity and row correlation."""

from pathlib import Path
import tempfile
import unittest
import duckdb

from dacomp_tolerance import normal_forms,compare_python,compare_sql
from compare_dacomp_staging import fingerprint
from compare_dacomp_tolerance import anchor_l0


class ToleranceTests(unittest.TestCase):
    def test_official_l0_is_preserved_when_tuple_comparison_differs(self):
        record={'levels':[{'level':f'L{i}','whole_match':True,'keyed_match':True} for i in range(4)],'baseline_l0_whole_match':False}
        anchor_l0(record,rechecked_official=False)
        self.assertTrue(record['l0_exact_row_tuple_match'])
        self.assertFalse(record['levels'][0]['whole_match'])
        self.assertTrue(record['l0_whole_reproduced'])
        self.assertEqual(record['whole_match_level'],'L1')
    def compare(self,pred_rows,gold_rows,columns=None):
        columns=columns or ['value','other']
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);paths=[]
            for side,rows in [('p',pred_rows),('g',gold_rows)]:
                path=root/(side+'.duckdb');paths.append(path)
                with duckdb.connect(str(path)) as conn:
                    conn.execute('CREATE SCHEMA staging; CREATE TABLE staging.fixture(id VARCHAR,value VARCHAR,other VARCHAR)')
                    if rows:conn.executemany('INSERT INTO staging.fixture VALUES (?,?,?)',rows)
            before=[fingerprint(p) for p in paths]
            with duckdb.connect(str(paths[0]),read_only=True) as p,duckdb.connect(str(paths[1]),read_only=True) as g:
                expected=compare_python(p,g,'fixture','staging',columns,['id'])
                actual=compare_sql(paths[0],paths[1],'fixture','staging',columns,['id'],len(pred_rows),len(gold_rows),root/'scratch',expected['current_key_statistics'])
            for key in ['levels','current_key_statistics','l3_column_differences']:self.assertEqual(actual[key],expected[key],key)
            self.assertEqual(before,[fingerprint(p) for p in paths])
            return expected

    def test_numeric_and_boolean_transitivity(self):
        forms=[normal_forms(x)[0] for x in ['true','t','1','1.0','01.000','1e0']]
        self.assertEqual(len(set(forms)),1)
        self.assertEqual(normal_forms('0.0')[0],normal_forms('false')[0])
        r=self.compare([('a','1573',' TRUE ')],[('a','1573.0','1.0')])
        self.assertFalse(r['levels'][0]['whole_match']);self.assertTrue(r['levels'][1]['whole_match'])

    def test_decimal_precision_and_rounding(self):
        self.assertNotEqual(normal_forms('9007199254740993')[0],normal_forms('9007199254740992')[0])
        self.assertNotEqual(normal_forms('2.0000000000000000000000000001')[0],normal_forms('2')[0])
        for a,b in [('2.675','2.68'),('1.005','1.01'),('-1.005','-1.01'),('9.999','10'),('0.005','.01'),('-0.004','0')]:
            self.assertEqual(normal_forms(a)[1],normal_forms(b)[1],(a,b))
        self.assertNotEqual(normal_forms('1e5000')[0],normal_forms('1e4999')[0])
        r=self.compare([('a','2.675','x')],[('a','2.68','x')])
        self.assertFalse(r['levels'][1]['whole_match']);self.assertTrue(r['levels'][2]['whole_match'])

    def test_date_truncation_is_a_loss_of_time(self):
        r=self.compare([('a','2020-01-01 01:00:00','x')],[('a','2020-01-01 23:00:00','x')])
        self.assertFalse(r['levels'][2]['whole_match']);self.assertTrue(r['levels'][3]['whole_match'])
        self.assertEqual(normal_forms('2020-01-01')[2],normal_forms('2020-01-01t03:04:05z')[2])
        self.assertNotEqual(normal_forms('2020-01-01 23:00:00-05:00')[2],normal_forms('2020-01-02 04:00:00+00:00')[2])
        self.assertEqual(normal_forms('01/02/2020')[2],'S01/02/2020')
        self.assertEqual(normal_forms('2020-02-30')[2],'S2020-02-30')

    def test_joint_rows_must_match_not_only_column_marginals(self):
        r=self.compare([('a','1','x'),('a','2','y')],[('a','1','y'),('a','2','x')])
        self.assertTrue(all(c['marginal_multisets_equal'] for c in r['l3_column_differences']))
        self.assertTrue(all(not x['keyed_match'] and not x['whole_match'] for x in r['levels']))

    def test_duplicate_group_values_relax_but_multiplicity_remains(self):
        r=self.compare([('a','1.0','x'),('a','2.0','y')],[('a','1','x'),('a','2','y')])
        self.assertTrue(r['levels'][1]['keyed_match'])
        r=self.compare([('a','1','x'),('a','1','x')],[('a','1','x')])
        self.assertFalse(r['levels'][3]['keyed_match'])
        c=r['l3_column_differences'][0]
        self.assertEqual(c['mismatch_rows_or_minimum_pairs'],0)
        self.assertEqual(c['pred_unmatched_value_occurrences'],1)

    def test_unique_common_keys_with_different_total_rows(self):
        r=self.compare([('a','2020-01-01 12:00:00','1.000'),('p','extra','x')],[('a','2020-01-01','1')])
        self.assertTrue(r['levels'][3]['keyed_match'])
        self.assertTrue(all(not x['whole_match'] for x in r['levels']))
        self.assertEqual(r['current_key_statistics']['pred_only_keys'],1)

    def test_no_shared_keys_and_numeric_key_values(self):
        r=self.compare([('01','same','x')],[('1','same','x')],['id','value'])
        self.assertTrue(all(x['keyed_match'] is None for x in r['levels']))
        self.assertTrue(r['levels'][1]['whole_match'])
        self.assertIsNone(r['l3_column_differences'])

    def test_empty_tables_and_l0_literals(self):
        r=self.compare([],[])
        self.assertTrue(r['levels'][0]['whole_match'])
        self.assertIsNone(r['levels'][0]['keyed_match'])
        r=self.compare([('a',None,' null ')],[('a','NULL',None)])
        self.assertTrue(r['levels'][0]['whole_match'])
        self.assertNotEqual(normal_forms('null')[0],normal_forms('0')[0])


if __name__=='__main__':unittest.main()
