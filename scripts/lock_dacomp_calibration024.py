import json,hashlib,datetime
from pathlib import Path
r=Path('records')
d=[dict(task='impl-006',table='stg_reddit_ads__campaign_report',primary='多因并列',categories=['I','D','A','U'],confidence='中',uncertainty='只有通用策略说明',reason='20 个独立输出表达式单改均使行规模保持1200、格子规模24000→22800。spend 的生成字典先正确配置再被覆盖，I；video_views/upvotes/downvotes/comments 及有可用组成指标的派生占位为D；原始列不存在且契约未给公式的零/NULL选择为A；ctr/cpc/ecpm均为不可解析字符串，继续直接TRY_CAST依赖其可作为有效指标的假设为U，证据曾出现但被忽略。',events=[18,19,30,95]),dict(task='impl-016',table='workday__organization_overview',primary='多因并列',categories=['C','A'],confidence='中',uncertainty='看到了但没提',reason='annual_turnover_rate与management_ratio的NULLIF零分母未按契约置0，各C；maturity和size标签契约只用短标签而gold用全标签，各A。四处单改均行117不变、格子696→579。assignment_join减少5格、roles_join减少106格为参与因素C。score的三处CASE与风险分母各自单改不减少规模，不列参与因素。',events=[30,56,72,81])]
(r/'024_calibration_blind_decisions.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
paths=[r/'024_calibration_blind_decisions.json',r/'024_calibration_queries.json',*r.glob('024_reruns_impl-006_*.json'),*r.glob('024_reruns_impl-016_*.json')]
(r/'024_blind_lock.json').write_text(json.dumps({'locked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'policy':'盲标仅使用012/013包和原始数据/轨迹；未读取records/014～023标注结果。既有脚本仅复用基础设施。','files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}},ensure_ascii=False,indent=2)+'\n')
