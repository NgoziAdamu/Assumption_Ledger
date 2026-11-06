048 小实验输入准备：机械候选版，待 Claude 处理 decisions_for_claude.json。

每题目录：
  prompt.txt：题面原文，单独保存一次。
  material_index.txt/json：固定索引及来源信息，单独保存一次。
  manifest.json：动作/材料原文的来源引用和哈希，不复制完整轨迹或原始数据。
  calls.jsonl：每次普通/交卷叫起一条；交卷只记录位置及运行时假设占位。
  method2_components.json：做法一用过的材料的去重合并组成清单。

总清单：summary.json、suspicious_actions.csv、decisions_for_claude.json。
边界来源：edge_case_sources.json；来源哈希：source_hashes.json。
核验：validation.json；原有文件哈希：start_state.json。
数 token：../048_small_exp_token_counts.csv；tokens 为拼装脚本实际输出文本的 token 数，
payload_tokens 为未加顶层1/2/3/5标题、保留段内包装的串接 token 数。分项token不可简单相加替代tokens。

在仓库根目录运行（Python3标准库即可拼装，不调用模型）：
  python3 records/048_small_exp_assemble.py impl-001 1 --allow-pending
  python3 records/048_small_exp_assemble.py impl-001 --method2 --allow-pending
  python3 records/048_small_exp_assemble.py impl-001 --method2 --method2-full-trace --allow-pending
  python3 records/048_small_exp_assemble.py impl-001 1 --assumptions-file /tmp/prior.txt --allow-pending

--allow-pending 仅用于查看候选材料，不代表解决研究规则。默认拒绝输出受待定事项影响的输入。
--method2-full-trace 只展示另一候选（加入未叫起尾段）；仍不包含DAComp finish正文、system事件或
KramaBench没有执行步骤的回复，不代表研究设定已选择该候选。
给定交卷call时必须提供 --assumptions-file（该题前面列出的全部假设），否则拒绝伪造空输入。

原始来源依赖：两份traces归档；DAComp原契约的绝对路径；031领域说明摘录。
固定索引已经保存，运行拼装脚本不打开数据库或CSV/Excel数据。
任何被引用的文本或文件发生变化时，SHA-256核对会拒绝输出。
题面包含的完整契约保持原文，相关表节照用户规则另附，不做自动去重。
