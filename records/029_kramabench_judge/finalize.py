"""Validate captured replies offline, then produce new CSVs and a Chinese report."""
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo
from types import SimpleNamespace
import collections
import csv
import hashlib
import json
import logging
import sys

sys.dont_write_bytecode=True
from openai.types.chat import ChatCompletion
from official_wrapper import ROOT, official_metric, MODEL

OUT=Path(__file__).resolve().parent

def save(path,obj):
    with path.open('x',encoding='utf-8') as f:
        json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')

def write_csv(path,rows):
    with path.open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def answer_text(value):
    return value if isinstance(value,str) else json.dumps(value,ensure_ascii=False)

def main():
    manifest=json.loads((OUT/'run_manifest.json').read_bytes())
    completed=json.loads((OUT/'run_completed.json').read_bytes())
    assert completed['metric_calls']==30 and completed['all_sources_unchanged']
    assert manifest['source_sha256_before']==completed['source_sha256_after']
    for name,h in manifest['source_sha256_before'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
    metas={}
    for p in (ROOT/'records/027_kramabench_source/runs').glob('*/*/meta.json'):
        m=json.loads(p.read_bytes());metas[m['task_id']]=(p,m)
    tasks={t['id']:t for p in (ROOT/'data/kramabench/workload').glob('*.json') for t in json.loads(p.read_bytes())}
    records=sorted(OUT.glob('*_call[123].json'))
    assert len(records)==30
    by_task=collections.defaultdict(dict)
    # Only replay response parsing; this mock cannot issue a network request.
    logging.disable(logging.CRITICAL)
    state={}
    def create(**kwargs):
        state['replay_request']=kwargs
        if state['raw'] is None:
            raise RuntimeError('offline replay of failed API call')
        return ChatCompletion.model_validate(state['raw'])
    metric=official_metric(lambda **kwargs:SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))))
    from benchmark.llm_tools.prompts import PARAPHRASE_INSTRUCTION_PROMPT
    costs={1:Decimal('0'),2:Decimal('0'),3:Decimal('0')}
    unknown_cost=[];http_attempts=0;raw_reply_checks=0;prompt_checks=0
    total_usage=collections.Counter();models=collections.Counter();providers=collections.Counter()
    parse_errors=[]
    for p in records:
        r=json.loads(p.read_bytes());tid=r['task_id'];rep=r['repetition'];m=metas[tid][1];task=tasks[tid]
        assert rep in [1,2,3] and rep not in by_task[tid]
        assert m['score']['status']=='needs_judge' and task['answer_type']=='string_approximate'
        assert r['predicted_original']==m['final_answer'] and type(r['predicted_original']) is type(m['final_answer'])
        assert r['target_original']==task['answer'] and type(r['target_original']) is type(task['answer'])
        assert r['purpose']==('official_score' if rep==1 else 'stability_only')
        expected_messages=[{'role':x['role'],'content':[{'type':'text','text':x['content']}]} for x in PARAPHRASE_INSTRUCTION_PROMPT]
        expected_messages.append({'role':'user','content':[{'type':'text','text':f'A:"{str(m["final_answer"])}"; B:"{str(task["answer"])}"'}]})
        assert r['http_attempts']
        http_attempts+=len(r['http_attempts'])
        raws=[]
        for attempt in r['http_attempts']:
            assert set(attempt['request_body'])=={'model','messages'}
            assert attempt['request_body']=={'model':MODEL,'messages':expected_messages}
            prompt_checks+=1
            assert not attempt.get('credential_redaction_applied',False)
            if attempt.get('raw_response_json') is not None:
                assert json.loads(attempt['raw_response_text'])==attempt['raw_response_json'];raw_reply_checks+=1
            if attempt.get('http_status')==200 and isinstance(attempt.get('raw_response_json'),dict):
                raws.append(attempt['raw_response_json'])
        raw=raws[-1] if raws else None
        state['raw']=raw
        try:
            replay=list(metric(m['final_answer'],task['answer']))
        except Exception as e:
            replay=None
            parse_errors.append({'file':p.name,'error_type':type(e).__name__})
        assert replay==r['official_metric_return'],p.name
        assert r['score']==(replay[0] if replay is not None else None)
        if raw:
            assert r['returned_model']==raw.get('model') and r['returned_provider']==raw.get('provider')
            assert r['usage']==raw.get('usage',{})
            for key in ['prompt_tokens','completion_tokens','total_tokens']:
                total_usage[key]+=r['usage'].get(key,0)
            if r['cost_source']=='response.usage.cost':assert r['cost_usd']==raw['usage']['cost']
        models[str(r['returned_model'])]+=1;providers[str(r['returned_provider'])]+=1
        if r['cost_usd'] is None:unknown_cost.append(p.name)
        else:costs[rep]+=Decimal(str(r['cost_usd']))
        by_task[tid][rep]=r
    assert set(by_task)==set(manifest['tasks']) and all(set(x)=={1,2,3} for x in by_task.values())
    rows=[];same=0;complete_same=0;formal_failures=[];diagnostic_failures=[]
    for tid,rs in sorted(by_task.items()):
        scores=[rs[i]['score'] for i in [1,2,3]]
        consistent=len(set(scores))==1
        same+=consistent;complete_same+=consistent and None not in scores
        if scores[0] is None:formal_failures.append(tid)
        diagnostic_failures.extend(f'{tid}_call{i}' for i in [2,3] if rs[i]['score'] is None)
        def label(v):return '裁判失败' if v is None else ('通过' if v==1 else '未通过')
        rows.append({'题号':tid,'最终答案原文':answer_text(rs[1]['predicted_original']),
                     '最终答案类型':rs[1]['predicted_type'],'标准答案原文':answer_text(rs[1]['target_original']),
                     '标准答案类型':rs[1]['target_type'],'正式裁判结果':label(scores[0]),'正式分数':scores[0],
                     '第2次结果':label(scores[1]),'第2次分数':scores[1],'第3次结果':label(scores[2]),'第3次分数':scores[2],
                     '是否一致':'是' if consistent else '否',
                     '三次均有有效分数':'是' if None not in scores else '否',
                     '正式记录':f'records/029_kramabench_judge/{tid}_call1.json'})
    write_csv(OUT/'summary.csv',rows)
    final=[];unchanged=0
    for tid,(p,m) in sorted(metas.items()):
        old=m['score'];source=str(p.relative_to(ROOT))+'#/score'
        if old['status']=='needs_judge':
            r=by_task[tid][1];score=r['score'];status=r['judge_status'];source=f'records/029_kramabench_judge/{tid}_call1.json#/score'
            method='official_llm_paraphrase_via_openrouter_first_call'
        else:
            unchanged+=1;score=old['success'];method='original_baseline_score_unchanged'
            status='未交卷' if old['status']=='unanswered' else ('通过' if score==1 else '未通过')
        final.append({'题号':tid,'领域':tid.split('-')[0],'难度':tid.split('-')[1],
                      '原评分状态':old['status'],'原分数':old.get('success'),'最终状态':status,'最终分数':score,
                      '分数来源':method,'来源文件字段':source})
    assert unchanged==94 and len(final)==104
    write_csv(ROOT/'records/029_kramabench_final_scores.csv',final)
    counts=dict(collections.Counter(r['最终状态'] for r in final))
    formal_counts=dict(collections.Counter(r['正式裁判结果'] for r in rows))
    summary={'tasks':10,'model_metric_calls':30,'http_completion_attempts':http_attempts,
             'formal_results':formal_counts,'all_104_final_status_counts':counts,'unchanged_original_scores':unchanged,
             'three_results_equal_tasks':same,'three_valid_results_equal_tasks':complete_same,
             'formal_judge_failures':formal_failures,'diagnostic_judge_failures':diagnostic_failures,
             'cost_usd_total':str(sum(costs.values(),Decimal('0'))),'cost_usd_formal':str(costs[1]),
             'cost_usd_stability':str(costs[2]+costs[3]),'cost_usd_by_repetition':{str(k):str(v) for k,v in costs.items()},
             'unknown_cost_records':unknown_cost,'returned_models':dict(models),'returned_providers':dict(providers),
             'token_usage_totals':dict(total_usage),'raw_response_json_checks':raw_reply_checks,
             'prompt_and_request_checks':prompt_checks,'offline_official_parser_replay_checks':30,
             'all_sources_unchanged':True,'unexpected_parser_exceptions':parse_errors,
             'started_at_utc':manifest['started_at_utc'],'finished_at_utc':completed['finished_at_utc']}
    save(OUT/'validation_and_totals.json',summary)
    localdate=datetime.fromisoformat(manifest['started_at_utc']).astimezone(ZoneInfo('Asia/Singapore')).date().isoformat()
    report=f'''# KramaBench 待裁判补评

日期：{localdate}（Asia/Singapore）。

## 任务

按已保存的 KramaBench 官方 `llm_paraphrase` 方法，补评 10 道 `string_approximate` 待裁判题。每题第 1 次结果是正式分数，第 2、3 次仅检查稳定性。不分析错因，不重跑 agent，不改变已有 meta、summary、轨迹、材料包或标准答案。

## 结论

**已核实**：完成 10 题各 3 次，共 **30 次裁判调用**。正式结果为 **{formal_counts.get('通过',0)} 题通过、{formal_counts.get('未通过',0)} 题未通过、{len(formal_failures)} 题裁判失败**。三次结果完全一致的题有 **{same}/10**；正式分数全部固定取第一次，没有使用多数票或选择更有利结果。

合并原有 94 题后，104 题最终为 **{counts.get('通过',0)} 题通过、{counts.get('未通过',0)} 题未通过、{counts.get('未交卷',0)} 题未交卷**；另有 **{counts.get('裁判失败',0)} 题裁判失败**。原 40 道“未通过”中的 `astronomy-hard-11` 原 `status=unanswered, success=0`，本表依用户要求单列“未交卷”，分数仍照搬原值 0。

30 次已记录费用合计 **US${summary['cost_usd_total']}**，其中正式 10 次 **US${summary['cost_usd_formal']}**，稳定性 20 次 **US${summary['cost_usd_stability']}**；费用缺失记录 **{len(unknown_cost)}** 条。返回的 model / provider 实测分布为 `{json.dumps(dict(models),ensure_ascii=False)}` / `{json.dumps(dict(providers),ensure_ascii=False)}`。

## 详细发现

### 方法与官方差别

评分语义与官方一致；唯一的接入差别是改走 **OpenRouter**：客户端 `base_url=https://openrouter.ai/api/v1`，key 从 `~/.openrouter_key` 仅在内存读取，模型标识从官方 `gpt-5-mini` 映射为 OpenRouter 的 `openai/gpt-5-mini`。后两项是该接入替换所需的凭据来源和名称映射，不是更换裁判方法。

薄包装 [official_wrapper.py](../records/029_kramabench_judge/official_wrapper.py) 直接从 `records/027_kramabench_source/official/` 导入原 `metrics.py` 的 `LLMParaphrase`、原 `gpt_interface.py` 与 `prompts.py`。包装没有复制重写裁判提示语、字符串转换或解析逻辑，也没有编辑官方文件。只在内存替换客户端构造器和模型名；跳过 benchmark 根包的无关 agent/workflow 初始化，没有运行 agent。

实际运行保留官方顺序：原值传给 `LLMParaphrase.__call__` → 对 predicted 与 target 分别 `str()` → 原 few-shot prompt 与 `A:"..."; B:"..."` → 原 `evaluate_paraphrase()` 从回复抽取 yes/no。官方先检查 `yes/Yes/YES`，然后检查 `no/No/NO`；返回 None 的分支不变。非字符串最终答案仍按原值类型传入，不提前转成 JSON 文本。

实际发出的请求体只有 `model` 与 `messages`，没有追加 temperature、seed、reasoning、max_tokens、provider 路由偏好或其他采样参数。使用官方 pyproject 指定的 `openai==1.72.0`，保留 SDK 默认重试和超时设置；本次观测到 **{http_attempts} 次 completion HTTP 请求**，对应 30 次裁判调用。原 prompt 中的 few-shot 内容保持原样；本任务没有根据答案或回复修改 prompt。

执行环境在 `/tmp/assumption-ledger-029-venv`；设置 `PYTHONDONTWRITEBYTECODE=1`，没有在官方目录写缓存。安装版本、输入哈希和执行起止时间见 [run_manifest.json](../records/029_kramabench_judge/run_manifest.json) 与 [run_completed.json](../records/029_kramabench_judge/run_completed.json)。官方源码、104 份 meta、两份 summary 和六份 workload 的前后 SHA-256 全部一致。

### 逐题结果

1 表示通过，0 表示未通过，None 表示裁判失败。第 2、3 次只检查稳定性。

| 题号 | 正式第 1 次 | 第 2 次 | 第 3 次 | 三次一致 |
| --- | ---: | ---: | ---: | --- |
'''
    for row in rows:
        tid=row['题号'];values=[by_task[tid][i]['score'] for i in [1,2,3]]
        report+=f'| [{tid}](../records/029_kramabench_judge/{tid}_call1.json) | {values[0]} | {values[1]} | {values[2]} | {row["是否一致"]} |\n'
    unstable=[r['题号'] for r in rows if r['是否一致']=='否']
    report+=f'''
不一致题号：{('、'.join(unstable)) if unstable else '无'}。这里只报告三次返回结果，不解释不一致原因。正式结果不受后两次结果影响。

### 裁判失败单列

正式调用裁判失败：{('、'.join(formal_failures)) if formal_failures else '无（0 题）'}。

稳定性调用裁判失败：{('、'.join(diagnostic_failures)) if diagnostic_failures else '无（0 次）'}。

裁判失败的分数保留为空/None，绝不改记为 0；如果出现正式裁判失败，最终 CSV 会以“裁判失败”单列，不能强行归入通过、未通过或未交卷。

### 104 题最终状态与费用

最终表：[029_kramabench_final_scores.csv](../records/029_kramabench_final_scores.csv)。已有 94 题的 success 数值照搬原 meta；10 题只取本次 call1 的官方返回分数。每行注明分数来源和文件字段，不覆盖任何原评分文件。

| 状态 | 题数 |
| --- | ---: |
| 通过 | {counts.get('通过',0)} |
| 未通过 | {counts.get('未通过',0)} |
| 未交卷 | {counts.get('未交卷',0)} |
| 裁判失败 | {counts.get('裁判失败',0)} |
| 合计 | 104 |

| 用途 | 调用数 | 已记录费用（USD） |
| --- | ---: | ---: |
| 正式第一次 | 10 | {summary['cost_usd_formal']} |
| 稳定性第二、三次 | 20 | {summary['cost_usd_stability']} |
| 总计 | 30 | {summary['cost_usd_total']} |

token 用量按原响应 usage 求和：prompt **{total_usage['prompt_tokens']:,}**、completion **{total_usage['completion_tokens']:,}**、total **{total_usage['total_tokens']:,}**。各条原 usage（含 reasoning/cached token 子字段）、原 cost 及 cost_details 均保存在 JSON；不使用价格表反推费用。汇总用 Decimal 加和，避免浮点累计误差。

### 原始记录与检查

- 每次调用的 `<题号>_call1/2/3.json`：用途、输入原值及类型、UTC 起止时间、耗时、请求体、HTTP 原始响应文本和解析 JSON、返回 model/provider、usage/cost、官方 metric 返回值及官方日志。只记录请求体，不保存认证请求头或客户端对象。
- `<题号>_call1/2/3_intent.json` 在调用前写入；既有 run_manifest 会阻止运行脚本再次发起整批调用，避免中断后误把第二次当第一次。没有重新发起已完成的裁判调用。
- [summary.csv](../records/029_kramabench_judge/summary.csv)：逐题最终答案和标准答案原文、原值类型、三次结果、是否一致及正式记录路径。字符串原文原样写入 CSV，其他类型使用 JSON 文本展示；实际 API 输入仍由原值经官方 str() 转换。
- [offline_validation.json](../records/029_kramabench_judge/offline_validation.json)：调用前的 8 项离线检查，验证原函数身份、原 prompt、字符串转换、yes/no 优先级和 None 分支，无网络调用。
- [validation_and_totals.json](../records/029_kramabench_judge/validation_and_totals.json)：30 条记录的请求和原响应核对；使用保存的响应对象离线重放官方解析，结果逐次一致。离线重放不请求模型，不计作稳定性调用。
- 提交前使用 [check_delivery.py](../records/029_kramabench_judge/check_delivery.py) 对新文件及 Git 暂存内容检查实际 key 字节串和凭据模式：均为 0 命中。结果见 [delivery_check.json](../records/029_kramabench_judge/delivery_check.json) 与 [delivery_check_staged.json](../records/029_kramabench_judge/delivery_check_staged.json)。key 文件未复制，认证请求头未保存，已有文件未改动。

## 证据来源

- 官方复制件：`records/027_kramabench_source/official/benchmark/metrics.py` 第 331–344 行；`benchmark/llm_tools/gpt_interface.py` 第 22–32、35–53、139–168 行；`benchmark/llm_tools/prompts.py` 的 `PARAPHRASE_INSTRUCTION_PROMPT`。均已打开并运行相应原函数，文件未改。
- 任务输入：`records/027_kramabench_source/runs/` 的 10 份 needs_judge meta.final_answer；`data/kramabench/workload/` 中对应题号的 answer。完整路径与 SHA-256 在 run_manifest；标准答案未写回原文件。
- API 实测证据：`records/029_kramabench_judge/*_call[123].json` 的 raw_response_text、raw_response_json、returned_model、returned_provider、usage 与 cost_usd；以实际返回为准。
- [OpenAI Python SDK 官方说明](https://developers.openai.com/api/reference/python)：核对 SDK 响应及默认客户端行为；本地实际安装的 SDK 版本另存 manifest。
- [OpenRouter API Reference](https://openrouter.ai/docs/api_reference/overview)：核对兼容 Chat Completions 的请求/响应结构。[OpenRouter generation metadata](https://openrouter.ai/docs/api/api-reference/generations/get-request-&-usage-metadata-for-a-generation) 说明按 generation ID 获取费用元数据；脚本仅在 response.usage.cost 缺失时使用该 GET，不另调用模型。
- 主要命令：`uv venv --python 3.12 /tmp/assumption-ledger-029-venv`；`uv pip install --python /tmp/assumption-ledger-029-venv/bin/python 'openai==1.72.0' typeguard untruncate-json nltk rouge-score ollama`；`PYTHONDONTWRITEBYTECODE=1 /tmp/assumption-ledger-029-venv/bin/python records/029_kramabench_judge/check_official_wrapper.py`；同环境运行 `run_judge.py` 与 `finalize.py`。执行日志在本次 records 目录。

## 不确定或没查到的

- 仅以 OpenRouter 返回的 model/provider 字段确认本次记录；没有直连 OpenAI 做对照，不能据此证明两个接入点的所有服务端默认行为完全一致。
- 三次调用只描述本次重复结果，不估计更大范围的稳定性或推断不一致原因。没有为稳定性设置随机种子或改变官方参数。
- 费用缺失记录：{('、'.join(unknown_cost)) if unknown_cost else '无'}。总费用采用响应/元数据返回的 USD 成本，不把 token 数乘以网页价格作为账单。
- 不重判已有 94 题，不分析答案错因，不重跑 agent；原基线中的其他评分方法和局限仍以 027 报告为准。

## 建议的下一步

使用新的 104 题 final_scores CSV 作为本次合并结果，并保留原评分和三次裁判记录以供追溯；稳定性重复结果单独阅读，不替换正式第一次分数。本任务不继续补调用或分析错因。
'''
    path=ROOT/f'notes/029_{localdate}_KramaBench待裁判补评.md'
    with path.open('x',encoding='utf-8') as f:f.write(report)
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
