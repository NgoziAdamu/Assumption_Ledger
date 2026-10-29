"""Check read COPY exclusion, literal write syntax and non-executing script recovery."""

import unittest

from audit_dacomp_raw import write_hits,historical_scripts


class RawScanTests(unittest.TestCase):
    def test_reads_and_copy_to_are_not_write_hits(self):
        text="SELECT * FROM raw.x; COPY raw.x TO '/tmp/x.csv'; COPY (SELECT * FROM raw.x) TO '/tmp/y.csv';"
        self.assertEqual(write_hits(text,'fixture'),[])

    def test_quoted_dynamic_and_catalog_targets(self):
        text='CREATE OR REPLACE VIEW "raw".{name} AS SELECT 1; INSERT INTO working.raw.x VALUES (1); ALTER TABLE raw.x RENAME TO y; COPY raw.x FROM \'x.csv\';'
        hits=write_hits(text,'fixture')
        self.assertEqual({h['operation_syntax'] for h in hits},{'CREATE TABLE/VIEW','INSERT/REPLACE INTO','ALTER/DROP/TRUNCATE TABLE','COPY FROM'})

    def test_literal_script_recovery_does_not_execute(self):
        command="cat > /tmp/fixture_raw.py <<'PY'\nprint('CREATE TABLE raw.x AS SELECT 1')\nPY\npython /tmp/fixture_raw.py"
        result=historical_scripts(command)
        self.assertEqual(result['/tmp/fixture_raw.py']['text'],"print('CREATE TABLE raw.x AS SELECT 1')\n")
        command="python - <<'PY'\nfrom pathlib import Path\np=Path('/tmp/never_written.py')\np.write_text('UPDATE raw.x SET a=1')\nPY"
        result=historical_scripts(command)
        self.assertEqual(result['/tmp/never_written.py']['text'],'UPDATE raw.x SET a=1')


if __name__=='__main__':unittest.main()
