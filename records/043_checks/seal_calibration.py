"""043 第一阶段：把独立判断和精确引句封存；绝不读取 034/036 标注内容。"""
from pathlib import Path
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / 'records'
SEALED = REC / '043_calibration_blind_sealed.json'
assert not SEALED.exists(), '封存件不得重写'

def read(p):
    return json.loads((ROOT / p).read_text())

def dump(p, x):
    (ROOT / p).write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')

def trace(task):
    path = f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent/output.jsonl'
    d = read(path)
    return path, {e['id']: e for pair in d['history'] for e in pair if 'id' in e}

def cite(task, event, field, quote):
    path, es = trace(task)
    val = es[event]
    for k in field.split('.'):
        val = val[k]
    assert quote in val, (task, event, quote)
    return dict(source=path, event=event, field=field, quote=quote)

def run(file, label):
    d = read('records/' + file)
    r = next(r for r in d['runs'] if r['label'] == label)
    b = next(r for r in d['runs'] if r['label'] == 'baseline')
    return dict(source='records/' + file, label=label,
                baseline=[{k: c[k] for k in ['level', 'row_scale', 'cell_scale']} for c in b['comparison']['levels']],
                after=[{k: c[k] for k in ['level', 'row_scale', 'cell_scale']} for c in r['comparison']['levels']],
                edits=r['edits'])

objects = []
points = []
q_null = cite('impl-006', 97, 'args.final_thought', '对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。')
q_cast = cite('impl-006', 97, 'args.final_thought', '脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。')
q_spend1 = cite('impl-006', 19, 'args.command', "'spend':['spend','local_spend_amount']")
q_spend2 = cite('impl-006', 19, 'args.command', "'spend':['local_spend_amount']")
q_cols = cite('impl-006', 18, 'content', "'priority', 'region', 'spend', 'video_fully_viewable_impressions'")
obj = 'impl-006_stg_reddit_ads__campaign_report'
specs = {
    'spend': ('代码写错', '同一个 event 19 字典先将 spend 映射到原始 spend，后一个同名键仅留下 local_spend_amount；正确映射被覆盖。按第6节代码自身明确证据排除前提类。', '高'),
    'video_views': ('Quiet Downgrade', '原始 video_started 非空1200行，是可判断的视频观看候选列；直接整列 NULL，没有作映射判断。', '高'),
    'video_view_rate': ('Unstated Choice', '没有对应的 video_view_rate 源列，契约没有规定由哪种观看量、哪个分母计算；gold 取常量0，agent 留 NULL。材料没定的选择。', '中'),
    'upvotes': ('Quiet Downgrade', '原始 comment_upvotes 非空1200行，存在明确候选，直接整列 NULL。', '高'),
    'downvotes': ('Quiet Downgrade', '原始 comment_downvotes 非空1200行，存在明确候选，直接整列 NULL。', '高'),
    'comments': ('Quiet Downgrade', '原始 viewer_comments 非空1200行，存在明确候选，直接整列 NULL。', '高'),
    'shares': ('Unstated Choice', '原始列清单无 shares 对应列；契约未规定缺失填0或NULL。', '高'),
    'saves': ('Unstated Choice', '原始列清单无 saves 对应列；契约未规定缺失填0或NULL。', '高'),
    'post_visits': ('Quiet Downgrade', '原始 comments_page_views 是帖子访问的可见候选列；agent 不判断而整列NULL。gold 的0仅用作单改诊断，不能证明正确源列。此候选的业务覆盖含义仍不充分，把握中。', '中'),
    'profile_visits': ('Unstated Choice', '原始列清单无 profile_visits 对应列；契约未规定缺失默认值。', '高'),
    'community_joins': ('Unstated Choice', '原始列清单无 community_joins 对应列；契约未规定缺失默认值。', '高'),
    'conversions': ('Unstated Choice', '有若干 app_install 事件列，但契约没有规定总转化范围或聚合方式，不能从 gold 的常量0确定定义。', '中'),
    'conversion_value': ('Unstated Choice', '契约没有确定哪些事件或支出代表转化价值；不能把 spend 直接当转化价值。NULL与gold的0属于材料没定的缺失处理。', '中'),
    'click_through_rate': ('Unstated Choice', '从原始ctr转换还是从clicks/impressions重算，契约只给类型，没有规定算法。原始是mock_ctr文本而非可确定的数字；TRY_CAST全失败不能单独证明本应有哪个数值，不将gold重算选择作为数据事实。', '中'),
    'cost_per_click': ('Unstated Choice', '原始cpc为mock_cpc文本，转换留NULL与用spend/clicks重算的差异取决于未规定的取数/重算选择；没有把mock编号解释成金额。', '中'),
    'cost_per_thousand_impressions': ('Unstated Choice', '原始ecpm为mock_ecpm文本；契约没有规定使用原始指标还是重算。不能从全部TRY_CAST失败直接推出可确定的原始金额。', '中'),
    'cost_per_video_view': ('Quiet Downgrade', '可用spend与video_started构成要求的单位观看成本，agent直接整列NULL，未判断这些候选。', '中'),
    'cost_per_conversion': ('Unstated Choice', '转化量定义及缺失时的默认值未规定，不能用gold常量0证明agent的NULL不合理。', '中'),
    'total_engagements': ('Quiet Downgrade', 'comment_upvotes/comment_downvotes/viewer_comments是可见互动候选，agent不作判断而整列NULL；确切聚合口径未规定不改变完全省略指标这一事实。', '中'),
    'engagement_rate': ('Quiet Downgrade', '有互动候选及impressions，agent不作任何判断而整列NULL；gold公式仅用于差异定位。', '中'),
}
for name, (category, reason, confidence) in specs.items():
    rr = run('024_reruns_' + obj + '.json', name)
    points.append(dict(object_id=obj, point=name, category=category, confidence=confidence,
                       role='并列主要原因', disclosure=2,
                       disclosure_reason='event 97 通用说明覆盖本类处理，但没有点名本表或一一对应的功能名称；最终SQL无注释。第2档不改类别。',
                       disclosure_citations=[q_cast if name in ['click_through_rate','cost_per_click','cost_per_thousand_impressions'] else q_null],
                       evidence_present='不适用', previously_correct='不适用', system_prompt='不适用',
                       reason=reason, decision_citations=[q_spend1,q_spend2] if name=='spend' else [q_cols],
                       premise_P=None, evidence=rr,
                       evidence_reuse=['records/024_calibration_queries.json'],
                       new_evidence=['records/043_checks/calibration_queries.json'] if name in ['click_through_rate','cost_per_click','cost_per_thousand_impressions'] else []))
objects.append(dict(object_id=obj, layer='staging', main='多因并列', tied_categories=['代码写错','Quiet Downgrade','Unstated Choice'], combination_only=False,
                    confidence='中', rationale='20处单改均为(1200行,24000格)→(1200行,22800格)，全部并列；不把多个独立可改单列合并成一个点。'))

obj = 'impl-016_workday__organization_overview'
q_contract = cite('impl-016', 1, 'args.content', 'Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id.')
q_zero = cite('impl-016', 1, 'args.content', 'annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0.')
q_mgmt = cite('impl-016', 1, 'args.content', 'management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0.')
q_risk = cite('impl-016', 1, 'args.content', 'high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0.')
q_fill = cite('impl-016', 1, 'args.content', 'position_fill_rate (%) = current_active_employees ÷ total_positions × 100 when total_positions > 0, else 0.')
q_report = cite('impl-016', 83, 'args.final_thought', 'Source data contains no worker-position-organization records with a null end date. Therefore current-assignment headcount is zero and the contract-filtered `workday__organization_performance` mart contains zero rows.')
q_labels = cite('impl-016', 1, 'args.content', 'organization_size_category by current_active_employees: 0 Empty; ≤5 Micro; ≤15 Small; ≤50 Medium; ≤200 Large; else Enterprise.')
q_maturity = cite('impl-016', 1, 'args.content', 'organization_maturity_level by age_days: <1 year New; 1–3 years Young; 3–10 years Mature; 10+ years Legacy.')
q_score = cite('impl-016', 1, 'args.content', 'organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), and risk (10/7/4/2 by high_risk_employee_percentage thresholds); final score rounded to 2 decimals.')
specs16 = [
    ('annual_turnover_rate','Intent Misreading','主要原因',q_zero,'分母0时返回0是明确业务规则；agent用NULLIF后未补0。','高'),
    ('management_ratio','Intent Misreading','主要原因',q_mgmt,'分母0时返回0是明确业务规则；agent用NULLIF后未补0。','高'),
    ('organization_maturity_level','其他','并列主要原因',q_maturity,'分桶相同，agent输出New/Young/Mature/Legacy与契约一致；gold使用扩展文案。只改变文字且无要求gold的具体字符串。','高'),
    ('organization_size_category','其他','并列主要原因',q_labels,'分桶相同，agent输出Empty/Micro等契约给出的词，gold使用扩展文案。第5/6节其他。','高'),
    ('assignment_join','Intent Misreading','参与因素',q_contract,'契约要求先按worker/role/source/organization联接再统计；agent直接按位置关系算平均任期，漏掉联接后的赋值权重。','高'),
    ('position_fill_rate','Intent Misreading','存在未确立的前提，但不是判错原因',q_fill,'缺分母0时的默认0；本批CS输出单改不减少规模。','高'),
    ('high_risk_employee_percentage','Intent Misreading','存在未确立的前提，但不是判错原因',q_risk,'缺分母0时的默认0；沿最终健康分计算后单改仍不减少规模。','高'),
    ('score_turnover','Unstated Choice','存在未确立的前提，但不是判错原因',q_score,'契约列出得分档位但没有列出对应阈值及零离职时是否同时要求正人数；具体分段是材料没定的选择。','中'),
    ('score_efficiency','Unstated Choice','存在未确立的前提，但不是判错原因',q_score,'契约列出效率得分档位但没有阈值数字；75/60与gold的80/70属未定选择。','高'),
    ('score_risk','Unstated Choice','存在未确立的前提，但不是判错原因',q_score,'契约列出风险得分档位但没有阈值数字；10/20/30与gold的5/15/25属未定选择。','高'),
]
for name, category, role, quote, reason, confidence in specs16:
    rr=run('024_reruns_'+obj+'.json',name)
    points.append(dict(object_id=obj,point=name,category=category,confidence=confidence,role=role,
                       disclosure=4,disclosure_reason='event 1 相关契约完整进入初始用户消息；event 37写下做法并非意识到替代或冲突。event 83没有针对本处说明；本SQL无注释。当前在职人数为零的说明不等于说明除零留NULL。',
                       disclosure_citations=[quote],excluded_delivery_citations=[q_report],
                       evidence_present='是' if category=='Intent Misreading' else '不适用',
                       previously_correct='否' if category=='Intent Misreading' else '不适用',system_prompt='不适用',
                       reason=reason,decision_citations=[quote],premise_P=None,evidence=rr,
                       evidence_reuse=['records/024_calibration_queries.json'],new_evidence=[]))
for name, reason in [
    ('role_count_expression','契约要求worker-position为关系入口并按关系中的role计数；agent在独立role-worker分支只计匹配到role master的id。单改目标计数表达式减少71格。'),
    ('role_input_relation','契约明确先用worker-position联接role-worker；agent直接以role-worker作入口。单改入口使差异格子增加7，不作为参与因素；完整roles_join减少106是组合诊断，不重复记一个错误点。'),
    ('role_management_role_employees','契约要求以worker-position关系中的工人按角色计数；agent从role-worker分支计数。当前数据下单改不改变规模。'),
    ('role_director_role_employees','同上，Director角色的worker-position关系缺失；单改不改变规模。'),
    ('role_lead_role_employees','同上，Lead角色的worker-position关系缺失；单改不改变规模。'),
]:
    points.append(dict(object_id=obj,point=name,category='Intent Misreading',confidence='中',
                       role='参与因素' if name=='role_count_expression' else '存在未确立的前提，但不是判错原因',
                       disclosure=4,disclosure_reason='event 1完整给出联接规则；event 37只是写实现，没有指出冲突或替代；event 83完成报告未说明本处。SQL无注释。',
                       disclosure_citations=[q_contract],evidence_present='是',previously_correct='否',system_prompt='不适用',
                       reason=reason,decision_citations=[q_contract],premise_P=None,
                       evidence=run('024_supplement_reruns_'+obj+'.json',name),evidence_reuse=[],new_evidence=[]))
objects.append(dict(object_id=obj,layer='marts',main='多因并列',tied_categories=['Intent Misreading','其他'],combination_only=False,
                    confidence='中',rationale='固定同一时钟基线(117行,696格)。annual_turnover_rate、management_ratio、两种label各减117格并列；assignment_join减5格，role_count_expression减71格。roles_join整块减少106格作为组合诊断，不覆盖逐点排序。',
                    diagnostic_combination=run('024_reruns_'+obj+'.json','roles_join'),
                    clock_note='analysis_timestamp运行时差异先用同一固定时钟2025-10-13 13:18:28.226000+08:00控制；保留值696+117=813格，统一时钟后696格。不是新增错误前提。'))

# 回查已选择引句；不读取任何盲标禁读件的标注内容。
def citations(x):
    if isinstance(x,dict):
        if {'source','event','field','quote'} <= x.keys(): yield x
        else:
            for v in x.values(): yield from citations(v)
    elif isinstance(x,list):
        for v in x: yield from citations(v)

audit=[]
for c in citations(points):
    task=c['source'].split('/')[4]
    # 路径中的 task 用完整目录名取出，避免子串匹配。
    task=next(part for part in Path(c['source']).parts if part.startswith('impl-'))
    check=cite(task,c['event'],c['field'],c['quote'])
    audit.append(dict(**check,matched=True))

sealed=dict(stage='第一阶段盲标，尚未打开036逐表判断',manual='docs/标注手册_v3.2.md',
            sealed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            guard={'034_036_annotation_content_opened':False,'018_calibration_annotation_opened':False,
                   '037_042_reports_opened':False,'036_objects_ids_only_for_scope':True,'041_content_opened':False},
            objects=objects,points=points,
            query_budget={'impl-006':{'reused':2,'new':1,'total':3},'impl-016':{'reused':1,'new':0,'total':1}},
            rule_questions=[
                {'object_id':'impl-006_stg_reddit_ads__campaign_report','point':'post_visits','alternatives':['Quiet Downgrade','Unstated Choice'],'chosen':'Quiet Downgrade','reason':'comments_page_views可以构成可见候选，但是否等同所有post visits不充分；按有候选而不判断的规则，中把握，保留边界供复核。'},
                {'object_id':'impl-006_stg_reddit_ads__campaign_report','point':'click_through_rate / cost_per_click / cost_per_thousand_impressions','alternatives':['Data Misconception','Unstated Choice'],'chosen':'Unstated Choice','reason':'mock_*原始字段本身无法确定数值；不同于可解析时间因错误解析器变NULL。契约没有要求丢弃来源指标并重算，gold计算方式不是数据事实。'},
            ],
            scope_note='只完成2张校准，不表示50张正式表已完成；不从024旧标签推导类别。')
dump('records/043_calibration_blind_sealed.json',sealed)
sha=hashlib.sha256(SEALED.read_bytes()).hexdigest()
dump('records/043_checks/calibration_seal_hash.json',{'file':str(SEALED.relative_to(ROOT)),'sha256':sha,'sealed_at':sealed['sealed_at'],'point_count':len(points)})
dump('records/043_checks/calibration_blind_quote_audit.json',audit)
print('SEALED',sha,'objects',len(objects),'points',len(points),'quote checks',len(audit))
