049 小实验输入：按本轮定稿规则和五份原样提示词重建；不调用模型。

普通叫起（含 f_tail）：
  python3 records/049_small_exp_assemble.py impl-001 1
  python3 records/049_small_exp_assemble.py impl-001 1 --ledger-json /tmp/ledger.json
交卷重排（题面 + 全部已记录假设）：
  python3 records/049_small_exp_assemble.py impl-001 --final-rank --ledger-json /tmp/ledger.json
做法二（完整轨迹 + 相关材料去重）：
  python3 records/049_small_exp_assemble.py impl-001 --method2

第几次叫起采用各题 calls.jsonl 的 call 字段；普通/f_tail 连续编号，最后一条 f 为交卷位置。
若编号指向 f，请改用 --final-rank。缺省账本或空数组 [] 均填 (none)。
--ledger-json 与 --ledger-file 是同一参数的两个名字；文件必须是 JSON 数组。
每项保留 id、call（也接受“第几次叫起”）及 method1_review 的全部八个输出字段：
statement、about、target、evidence_of_dependence、alternative、importance、reason、updates。
拼装会原样保留所有字段和值，用 ensure_ascii=False / indent=2 序列化，不过滤、合并或排序。
拼装只替换模板中的占位符一次；轨迹或账本里的大括号保持原文。

五份模板在 records/049_prompts/；均与用户消息中的分隔标记之间的文本逐字节一致。
judge_match、judge_stated 本次只存档，不提供拼装入口、不数裁判调用 token。

每题目录：prompt.txt、material_index.txt/json、manifest.json、calls.jsonl、method2_components.json。
DAComp 另有 prompt_removal.json，定位原题面中的774个表节、删除区间和唯一插入标记。
固定部分每题只保存一份。原始动作、代码、可见反馈、reasoning及材料节均通过引用/哈希读取。
无执行回复按 response_line 顺序并入下一执行段，或交卷前 f_tail；不制造执行结果。
做法二 action_ids 恰好等于全部动作/步骤/无执行回复，section_ids 恰好为全部普通段（含尾段）用过的节去重。

material_index.json 复用048已核验的只读结构/首行/工作表元数据；没有重新打开数据库。
CSV 的首个物理行在文本索引里标为 first line of file (may not be a header):，
正文采用与048一致的JSON转义保存换行，不寻找真实表头，不读取下一物理行。

统计：../049_small_exp_token_counts.csv 是实际完整提示的 o200k_base token 和 SHA-256；
普通调用的 ledger=(none)，final 行 token 留空；prompt_before_after.csv 是题面去表节前后字符/token。
统计含模板文字，未计 API 封装、非空运行时账本、最终重排、模型输出/推理、裁判输入输出。
summary.json 含逐题统计和相对048的调用次数变化；decisions_for_claude.json 为新规则缺口清单。
验证：validation.json、ledger_cli_checks.json；提示词原文核对：prompt_source_check.json。

原始来源依赖：048的固定原件和引用，两份轨迹归档、原契约绝对路径、031说明文档。
运行时拼装不打开数据库或CSV/Excel数据文件，不执行轨迹，不联网调用模型。
提示词和来源文本由SHA-256校验，匹配失败则退出。生成脚本拒绝覆盖已有输出。
