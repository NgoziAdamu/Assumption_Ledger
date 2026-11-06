公开/完整版分离（用户授权方案1）：
完整未替换Twilio SID的请求、返回及配套记录位于 data/050_pilot_full/，不进Git；认证信息从未保存。
records/050_pilot/ 是公开副本；只把Twilio Account SID换成一致的 [REDACTED_TWILIO_SID_1]。
共4处，涉及两份request.json；详见redaction_manifest.json。
完整文件路径与SHA-256见full_archive_manifest.json。
所有引用核对、token、费用一律以完整版为准；公开文本不用于重新计数。
runner现以data/050_pilot_full为读写根目录；历史records路径自动映射到完整归档。
缺少完整版时退出，不会将公开脱敏输入误当原始试跑输入。
GitHub首次推送因SID检测被拒绝；按用户要求重建尚未推送的提交，不动已推送历史，不绕过保护。

050 两题全流程试跑，使用官方 openai Python SDK 3.46.0。

先读 final_status.json：32次API调用均完成且JSON可解析，但本轮4次legal-hard-18 reviewer输入
被原runner的subprocess text=True自动将CRLF转换为LF，严格049输入保真检查未通过。
真实请求/返回未覆盖，未为修复重调模型。runner现已改为捕获字节再UTF-8解码，4项离线修复测试通过。

运行入口：
  TIKTOKEN_CACHE_DIR=/tmp/assumption-ledger-048-tiktoken-cache /tmp/assumption-ledger-050-venv/bin/python records/050_pilot_run.py
  TIKTOKEN_CACHE_DIR=/tmp/assumption-ledger-048-tiktoken-cache /tmp/assumption-ledger-050-venv/bin/python records/050_pilot_run.py --analyze-only
  TIKTOKEN_CACHE_DIR=/tmp/assumption-ledger-048-tiktoken-cache /tmp/assumption-ledger-050-venv/bin/python records/050_pilot_run.py --validate-only
首次模型请求曾用 --probe 单独确认；常规流程复用其缓存，不额外付费请求。
默认入口复用同tag的已存调用；若当前拼装与历史请求不同，会打印提示并保留历史结果。
复跑修正后的试验必须另建归档；本任务没有重跑。分析/复核入口不发模型请求。validation.json保留首次核验快照，重复复核只打印当前结果，不覆盖快照。

凭据仅由进程从 ~/.openai_key 和 ~/.deepseek_key 读取，不进入请求归档或输出。
Responses：gpt-6.1-sol，medium，summary=auto，max_output_tokens=32000，无JSON模式。
DeepSeek：base_url=https://api.deepseek.com，deepseek-flash，其他生成参数省略。
SDK内置重试=0；应用层仅网络/429/5xx重试，至多3次重试（首次+3），等待2/4/8秒。
估算累计超过5USD、认证/访问失败或模型名被拒绝时停止；本次未触发。

calls/<tag>/：
  request.json：POST端点和完整显式JSON请求，认证信息不保存。
  attempt_1_response_body.txt：完整原始HTTP响应体（JSON），不是输出文字的摘要。
  attempt_1_response.json：同一原始对象；attempt_1_sdk_response.json：SDK解析对象。
  text.txt：用于json.loads的最终回复文字，不把reasoning摘要拼入答案。
  parse.json：去首尾代码围栏后的json.loads结果或失败原因。
  record.json：时间、状态、截断、完整usage、缓存、reasoning、用量比、估算费率和费用、重试记录。

每题：ledger_before_call_N.json、ledger_after_call_N.json、ledger_all.json；
每个输出条目加cN-I及call，完整保留updates和旧条目。method1/2_final_lists.json为机械排序/对照。
agent_text.json存摘录规则、来源坐标、原文及问题；agent_text.txt是judge_stated使用的全文。

汇总：call_summary.csv、summary.json、report_call_index.json。
原样裁判结果：judge_results.json；表名对照：table_mapping.json。
引用核对：quote_checks.json（整字段，精确/仅归一空白）；
quote_delimiter_checks.json（所有显式引号/反引号子串的补充口径，不选哪段才是真正引用）。
引用边界待Claude决定的问题：decisions_for_claude.json。

关键核验：validation.json（记录对账通过，但strict_049_input_fidelity_passed=false）；
input_fidelity.json（4次差异的每个CR字符位置与哈希）；newline_reader_fix_tests.json（不调用模型）。
环境和来源：environment.json、requirements.freeze.txt、documentation_sources.json、start_state.json。
费用按用户指定单价计算，以账单为准；DeepSeek按请求开始时UTC判断高峰。
本次DeepSeek在周五UTC06:00–10:00时段，按高峰价格估算；reasoning token包含在output中，不重复计费。

本脚本没有执行任何保存的agent代码，没有读数据库，没有修改049提示词或任何开工前文件。
所有模型输出仅用于机械格式、字符匹配及用户规定的表名/排序处理；不作语义复评。
