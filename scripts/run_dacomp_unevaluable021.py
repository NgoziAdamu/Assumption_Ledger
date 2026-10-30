from annotate_dacomp_batch021 import *
from review_dacomp_batch021 import pkg
for x in json.loads((REC/'021_raw_diagnosis.json').read_text())['tables']:
 if x['unevaluable']:rerun(10,[],clock='2025-10-13 00:00:00+00',pkg=pkg(x['index']))
