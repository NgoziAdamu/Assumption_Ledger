"""用公开 dev 答案原样调用官方 scorer；不运行 agent、不输出原始答案。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCORER = ROOT / "external/dabstep_official/dabstep_benchmark/evaluation/scorer.py"
TASKS = ROOT / "data/dabstep/data/tasks/dev.jsonl"
SUBMISSION = ROOT / "data/dabstep/selfcheck/dev_gold_submission.jsonl"


def forbid_network(event, args):
    if event in {"socket.connect", "socket.connect_ex", "socket.getaddrinfo", "socket.bind"}:
        raise RuntimeError(f"Offline self-check forbids network event: {event}")


sys.addaudithook(forbid_network)
before = hashlib.sha256(SCORER.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location("official_dabstep_scorer", SCORER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
tasks = [json.loads(line) for line in TASKS.read_text().splitlines() if line.strip()]
submission = [{"task_id": str(row["task_id"]), "agent_answer": row["answer"]} for row in tasks]
SUBMISSION.parent.mkdir(parents=True, exist_ok=True)
SUBMISSION.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in submission))
submitted = {row["task_id"]: row["agent_answer"] for row in map(json.loads, SUBMISSION.read_text().splitlines())}
scores = []
for row in tasks:
    answer = submitted[str(row["task_id"])]
    assert answer == row["answer"]  # No normalization by this wrapper.
    scores.append(module.question_scorer(answer, row["answer"]))
after = hashlib.sha256(SCORER.read_bytes()).hexdigest()
assert before == after
print(json.dumps({
    "python": sys.version,
    "official_function": "question_scorer",
    "scorer_sha256_before": before,
    "scorer_sha256_after": after,
    "network_policy": "Python audit hook rejects socket connect/connect_ex/getaddrinfo/bind",
    "split": "dev",
    "submission_path": str(SUBMISSION.relative_to(ROOT)),
    "submitted_answers_identical_to_gold": True,
    "total": len(scores),
    "correct": sum(scores),
    "accuracy": sum(scores) / len(scores),
    "accuracy_percent": 100 * sum(scores) / len(scores),
    "per_row_scores_in_source_order": scores,
}, ensure_ascii=False, indent=2))
