"""v2 requires a common fixed clock; supplement only the unfrozen 006 trials."""
from annotate_dacomp_batch018 import REC, rerun
import json

if __name__ == '__main__':
    old = json.loads((REC / '016_reruns_impl-006.json').read_text())
    patches = [(t['label'], [(e['old'], e['new']) for e in t['edits']]) for t in old['runs'][1:]]
    # _dbt_loaded_at is outside the official comparison; arbitrary common clock,
    # not an estimate of the original execution time.
    rerun(6, patches, clock='2025-10-25 12:00:00+08')
