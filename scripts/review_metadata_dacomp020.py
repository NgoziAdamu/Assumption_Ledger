"""Final manual review decisions; separate from immutable blind calibration evidence."""
OVERWRITE_INDICES = {20, 22, 25, 27, 29, 30}
OVERWRITE_QUOTE = "event19 的 special 字典先有 `'campaign_id':['campaign_id','id']` 和 `'spend':['spend','local_spend_amount']`，后被同名键 `'campaign_id':['campaign_id','CAMPAIGN_ID']`、`'spend':['local_spend_amount']` 覆盖。代码自身给出正确映射意图，符合手册I的明确例子。"
TIER_OVERRIDES = {18: {'avg_cpa_currency': 3, 'avg_cpt_currency': 3}}

def apply_review(M, CAT, RULES):
    for i in OVERWRITE_INDICES:
        col = 'campaign_id' if i in {20, 25} else 'spend'
        CAT.setdefault(i, {})[col + '_restore_overwritten_mapping'] = 'I'
        CAT[i][col] = 'I'
        TIER_OVERRIDES.setdefault(i, {})[col + '_restore_overwritten_mapping'] = 3
    CAT[25]['spend_masked_diagnostic'] = 'D'
    for i in [20, 25]:
        old = M[i]
        M[i] = ('I', 'campaign_id 的正确 id 映射被后写的字典条目覆盖，最终生成 NULL。', OVERWRITE_QUOTE + ' 恢复生成器原先的id映射，只改campaign_id投影，行数规模减半；其他遗漏仍被键差异遮蔽。', 3,
                'event18输出原始id列清单；event19先写正确映射又覆盖。event97只披露缺失源字段填NULL，未说明本表已有id却因覆盖失效，不能把该缺省策略当作对此处代码错误的说明。')
    replacements = {
      22: ('多因并列', 'spend映射被覆盖（I），与CTR/CPC/CPM的NULL占位（D）并列。', OVERWRITE_QUOTE + ' spend恢复原映射与三个指标单修均减少1000格。'),
      27: ('多因并列', 'spend映射覆盖（I）、指标占位（D）与无源字段默认值（A）并列。', OVERWRITE_QUOTE + ' assists/bounce_rate/average_position无源列，默认0或NULL未规定，A；其余率指标有输入却占位，D。每项单修减少1500格。'),
      29: ('多因并列', 'spend映射覆盖（I）、率指标占位（D）及无源/异常字段默认值（A）并列。', OVERWRITE_QUOTE + ' ad_account_id缺失，异常文本清理为0或NULL未规定，A；可计算的率指标直接NULL为D。最大单项改善均900格。'),
    }
    for i, front in replacements.items():
        M[i] = (*front, *M[i][3:])
    M[30] = (*M[30][:2], M[30][2] + ' spend另有event19同名映射覆盖的I证据；独立恢复仍为1800行/48600格，不列参与因素。', *M[30][3:])
    seen = {
      0: 'event48显示campaign与account均为12,990行，event26已出现account聚合字段total_impressions缺失报错，event27生成投影；未说明省略聚合的选择。event97关于脏值TRY_CAST的通用策略不涉及本处聚合。',
      13: 'event18输出ad_group_id列，event19写转换，event86核对列类型。未找到对本表非法ID应删除还是保留的说明；event97的TRY_CAST/NULL泛述不能代替本处delete_row政策。',
      14: 'event18输出campaign_bidding_strategy列，event40有相关类型修复输出；未说明策略字符串是否采用白名单/大小写清洗。event97通用数值TRY_CAST/缺列NULL不涉及这项选择。',
      24: 'event18输出base_ad_group和id列，event29生成Google staging映射；未解释为何选base_ad_group。event97的缺列NULL策略不涉及两个已有源列之间的选择。',
    }
    for i, evidence in seen.items():
        M[i] = (*M[i][:3], 3, evidence)
    M[35] = (*M[35][:2], M[35][2].replace('单改gold类型', '诊断性地把agent的revenue表达式改为gold的小数表达式'), *M[35][3:])
    for i in [18, 22, 27, 29]:
        specific = '货币枚举校验遗漏只见event18相关列及实现，没有白名单处理说明，不能由数值TRY_CAST泛述推定已披露。' if i == 18 else 'I覆盖错误只见event18列清单与event19代码，没有说明。'
        M[i] = (*M[i][:4], M[i][4] + ' 各并列项单独分档：占位/缺省选择沿用适用的NULL通用披露；' + specific)
    for i in OVERWRITE_INDICES:
        RULES[i] = RULES.get(i, '') + ' 映射覆盖有代码自身的明确意图证据，直接适用v2的I定义，不修改规则；复核重跑恢复原先候选列，未套用gold额外清洗。旧gold表达式试验仅作诊断，避免重复计为两个错误点。'

def item_tier(i, label, default):
    return TIER_OVERRIDES.get(i, {}).get(label, default)
