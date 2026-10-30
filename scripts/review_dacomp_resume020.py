"""Recheck generator-overwrite errors in a separate private workspace/artifact set."""
import json
from pathlib import Path
import annotate_dacomp_batch020 as harness
from plan_dacomp_batch020 import ROOT, REC, rows, pkg, oldexpr, goldexpr

harness.WORK = ROOT / 'data/020_resume_work'
harness.WORK.mkdir(exist_ok=True)
original_save = harness.save
def save_resume(path, value):
    assert path.name.startswith('020_reruns_')
    original_save(path.with_name(path.name.replace('020_reruns_', '020_resume_reruns_', 1)), value)
harness.save = save_resume

def main():
    assert (REC / '020_resume_input_before.json').exists()
    for i in [20, 22, 25, 27, 29, 30]:
        d = pkg(i)
        col = 'campaign_id' if i in [20, 25] else 'spend'
        if col == 'campaign_id':
            dtype = 'VARCHAR(20)' if i == 25 else 'VARCHAR'
            new = f'CAST(CAST("id" AS VARCHAR) AS {dtype}) AS campaign_id'
        else:
            raw = 'SPEND' if i == 30 else 'spend'
            new = f'CAST(ROUND(TRY_CAST("{raw}" AS DOUBLE), 2) AS DECIMAL(18,2)) AS spend'
        patches = [(col + '_restore_overwritten_mapping', [(oldexpr(d, col), new)])]
        if i == 25:
            patches.append(('spend_masked_diagnostic', [(oldexpr(d, 'spend'), goldexpr(d, 'spend') + ' AS spend')]))
        harness.rerun(6, patches, pkg=d)

if __name__ == '__main__':
    main()
