051 正式第一批完整存档（不进 git）

提示词冻结提交：bd97e3ef9cd40ab243480de5687b05ffa6e66c5e。
原输入：records/049_small_exp_inputs，唯一变动是 Excel 行预览紧凑化。
prepare 已在第一条 API 之前完成全部 32 块 / 10921 个格子的验证。
selection.json 保存单一 random.Random(1234) 的两次抽样及剩余 19 道。
只运行 first 中的 10 道，顺序执行每题普通叫起、交卷重排、做法二；不运行裁判。

calls/<tag>/request.json：去认证信息后的完整请求。
calls/<tag>/assembled_prompt.txt：按字节保存并重新读取的完整提示。
attempt_N_response_body.txt：完整原始 HTTP 返回体。
attempt_N_response.json：完整 HTTP JSON 返回。
attempt_N_sdk_response.json：官方 SDK 解析后的完整对象。
text.txt / parse.json / record.json：模型文字、json.loads 结果、时间/状态/用量/费用。
tasks/<题号>/ledger_before/after_call_N.json：逐次的累计账本。
fewer_call_N.json 单独保存，不写入账本；ledger_all.json 保留所有成功条目，不因 updates 删除。
complete.json 保存题用时和调用编号。

统计和引用核对均从本完整版读取，公开版仅对匹配的疑似密钥字符串做固定占位符替换。
full_archive_manifest.json 与 redaction_manifest.json 在 records/051_formal_run/。
当前已知的真正 OpenAI / DeepSeek 凭据只在进程内使用，不写入本目录或仓库。
script command: /tmp/assumption-ledger-050-venv/bin/python records/051_formal_run.py <prepare|run|analyze|publish|verify|report>
run 默认 --batch first。以后收到用户指示才运行 --batch remaining，本次不执行。
所有 token 近似采用 o200k_base；账本为空时为 (none)。
