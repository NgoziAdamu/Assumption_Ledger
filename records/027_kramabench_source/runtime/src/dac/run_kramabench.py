"""Run recorded KramaBench tasks with a fake model unless explicitly enabled."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import shlex
import subprocess
import sys
import sysconfig
from datetime import datetime, timezone
from pathlib import Path

from safe_env import scrubbed_env
from dac.capabilities import discover_capabilities, supported_parameters
from dac.tool_loop import ToolCallingLoop
from dac.executor import CPythonExecutor, StepTimeout, WorkerFailure
from dac.models import Budget, CostLimit, FakeModel, OpenRouterModel, ProviderTransientError, reference_chunks
from dac.prompting import LIBRARIES, prepare_prompts
from dac.recorder import graph_stats, json_value, write_json
from dac.scoring import official_score

ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = ROOT / "benchmarks" / "KramaBench"
DEFAULT_TASKS = ["legal-easy-3", "archeology-easy-3", "legal-hard-1", "environment-easy-1"]


def now():
    return datetime.now(timezone.utc).isoformat()


def git_commit():
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, env=scrubbed_env(), text=True).strip()


def load_task(task_id, benchmark=BENCHMARK):
    domain = task_id.split("-")[0]
    for task in json.loads((benchmark / "workload" / f"{domain}.json").read_text(encoding="utf-8")):
        if task["id"] == task_id:
            return task
    raise ValueError(f"Unknown benchmark task: {task_id}")


def hard_task_ids(benchmark=BENCHMARK):
    """Read every hard task from the benchmark workload, preserving file order."""
    return [task["id"] for path in sorted((benchmark / "workload").glob("*.json"))
            for task in json.loads(path.read_text(encoding="utf-8")) if "-hard-" in task["id"] and path.stem == task["id"].split("-")[0]]


def prepare_workspace(workspace, task_id, data_dir):
    workspace.mkdir(parents=True, exist_ok=False)
    link = workspace / "data" / task_id.split("-")[0] / "input"
    link.parent.mkdir(parents=True)
    link.symlink_to(data_dir, target_is_directory=True)


def new_run_directory(output, create=True):
    path = Path(output).expanduser().resolve()
    runs = (ROOT / "runs").resolve()
    if not path.is_relative_to(runs) or path == runs:
        raise ValueError("The output must be a new directory inside runs/.")
    if path.exists():
        raise FileExistsError("The output directory already exists.")
    if create:
        path.mkdir(parents=True, exist_ok=False)
    return path


def run_task(task_id, output, *, fake_model=True, max_steps=30, allow_real_model=False,
             budget=None, codes=None, replies=None, timeout=300, benchmark=BENCHMARK, parameters=None,
             capabilities=None, model_factory=None):
    if max_steps < 1:
        raise ValueError("max_steps must be positive.")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    task = load_task(task_id, benchmark)
    data_dir = (benchmark / "data" / task_id.split("-")[0] / "input").resolve()
    # Approval is checked before constructing either model or worker.
    prompts = prepare_prompts(data_dir, task["query"])
    workspace = output / "workspace"
    prepare_workspace(workspace, task_id, data_dir)
    for filename in ("messages.jsonl", "steps.jsonl"):
        (output / filename).touch()
    write_json(output / "graph.json", {"nodes": [], "edges": []})
    meta = {"run_id": output.name, "task_id": task_id, "model": "fake-reference" if fake_model else "openai/gpt-6-luna",
            "parameters": {"max_steps": max_steps, "step_timeout_seconds": timeout, "max_output_chars": 4000,
                           "fake_model": fake_model, "allow_real_model": allow_real_model,
                           "max_cost_usd": budget.limit if budget else None, "reasoning_effort": "medium",
                           "tool_choice": "auto", "reference_statements_per_step": 3,
                           "parallel_tool_calls": "omitted_unsupported", "retry_delays_seconds": [5, 20],
                           "libraries": LIBRARIES, "output": str(output),
                           "max_snapshot_bytes": 50 * 1024 * 1024, "max_file_hash_bytes": 100 * 1024 * 1024,
                           **(parameters or {})},
            "prompt_values": prompts["values"],
            "prompt_sha256": prompts["hashes"], "git_commit": git_commit(), "started_at": now(),
            "ended_at": None, "status": "running", "final_answer": None, "score": None,
            "data_dir": str(data_dir), "workspace": str(workspace), "replay": False,
            "versions": {name: importlib.metadata.version(name) for name in ("smolagents", "pandas", "numpy", "pyarrow")},
            "python_standard_library": sysconfig.get_path("stdlib"),
            "python": sys.version.split()[0], "cost_usd": 0.0}
    sources = [*Path(__file__).parent.glob("*.py"), ROOT / "src" / "prompt_loader.py", ROOT / "src" / "safe_env.py"]
    meta["source_sha256"] = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(sources)}
    meta["git_dirty"] = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, env=scrubbed_env()))
    write_json(output / "meta.json", meta)
    executor = None
    model = None
    agent = None
    start_cost = budget.spent if budget else 0.0
    try:
        if fake_model:
            reference = benchmark / "solutions" / task_id.split("-")[0] / f"{task_id}.py"
            model = FakeModel(codes if codes is not None else ([] if replies is not None else reference_chunks(reference)),
                              output / "messages.jsonl", replies=replies)
        else:
            model = OpenRouterModel(allow_real_model=allow_real_model, prompts_approved=True, budget=budget,
                                    messages_path=output / "messages.jsonl",
                                    supported=supported_parameters(capabilities or discover_capabilities()))
        if model_factory is not None:
            model = model_factory(output / "messages.jsonl")
        executor = CPythonExecutor(output, workspace, data_dir, timeout=timeout)
        agent = ToolCallingLoop(model, executor, prompts, max_steps=max_steps)
        answer = agent.run()
        meta.update(status=agent.run_status, final_answer=json_value(answer))
    except StepTimeout:
        meta["status"] = "step_timeout"
    except CostLimit as error:
        meta.update(status="cost_limit", stop_reason=str(error))
    except ProviderTransientError as error:
        meta.update(status="provider_transient_error", error=str(error))
    except WorkerFailure as error:
        meta.update(status="failed", error=str(error))
    except Exception as error:
        meta.update(status="failed", error=f"{type(error).__name__}: {error}")
    finally:
        if executor:
            executor.cleanup()
        meta["ended_at"] = now()
        meta["model_calls"] = len(model.calls) if model else 0
        if model and getattr(model, "last_error", None):
            meta["provider_error"] = model.last_error
        meta["step_count"] = agent.rounds if agent else 0
        for counter in ("no_tool_call_count", "extra_tool_call_count", "tool_argument_errors"):
            meta[counter] = getattr(agent, counter, 0)
        meta["retry_count"] = getattr(model, "retry_count", 0)
        meta["cost_usd"] = (budget.spent - start_cost) if budget else 0.0
        responses = [json.loads(line) for line in (output / "messages.jsonl").read_text().splitlines()]
        meta["unknown_cost_attempts"] = sum(record.get("cost_usd") is None for record in responses
                                          if record["direction"] == "response")
        records = [json.loads(line) for line in (output / "steps.jsonl").read_text().splitlines()]
        meta["executed_steps"] = sum(record.get("kind") == "execution" for record in records)
        meta["completed_execution_steps"] = sum(record.get("kind") == "execution" and not record.get("worker_failed")
                                                and not record.get("timed_out") for record in records)
        meta["final_answer_restored_count"] = sum(record.get("event") == "final_answer_restored" for record in records)
        meta["interrupted_execution_count"] = sum(record.get("event") == "execution_interrupted" for record in records)
        usage = [record.get("usage", {}) for record in responses if record["direction"] == "response"]
        meta["token_usage"] = {"input_tokens": sum(item.get("prompt_tokens", item.get("input_tokens", 0)) for item in usage),
                               "output_tokens": sum(item.get("completion_tokens", item.get("output_tokens", 0)) for item in usage)}
        meta["score"] = official_score(task, meta["final_answer"], benchmark)
        graph = json.loads((output / "graph.json").read_text())
        meta["graph"] = graph_stats(graph)
        write_json(output / "meta.json", meta)
    return meta


COUNTERS = ("model_calls", "executed_steps", "no_tool_call_count", "extra_tool_call_count", "retry_count")


def print_progress(meta, cumulative):
    score = meta["score"]
    correct = score.get("success") if score.get("success") is not None else score.get("status", "unknown")
    counts = " ".join(f"{key}={meta.get(key, 0)}" for key in COUNTERS)
    print(f"Task {meta['task_id']} status={meta['status']} correct={correct} {counts} "
          f"cost_usd={meta['cost_usd']:.6f} cumulative_usd={cumulative:.6f}", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-ids", nargs="+", required=True)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--max-steps", type=int, default=30)
    parser.add_argument("--output", required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fake-model", action="store_true")
    mode.add_argument("--allow-real-model", action="store_true")
    parser.add_argument("--max-cost-usd", type=float)
    parser.add_argument("--progress", action="store_true")
    args = parser.parse_args(argv)
    if args.repeats < 1 or args.max_steps < 1:
        parser.error("repeats and max-steps must be positive")
    budget = None
    if args.allow_real_model:
        if args.max_cost_usd is None:
            parser.error("--max-cost-usd is required for real models")
        budget = Budget(args.max_cost_usd)
        budget.check()
    # Validate all tasks and approvals before creating the output directory.
    task_ids = [item for group in args.task_ids for item in group.split(",")]
    for task_id in task_ids:
        task = load_task(task_id)
        prepare_prompts(BENCHMARK / "data" / task_id.split("-")[0] / "input", task["query"])
    capabilities = discover_capabilities() if args.allow_real_model else None
    output = new_run_directory(args.output)
    if capabilities is not None:
        write_json(output / "provider_capabilities.json", capabilities)
    results = []
    skipped = []
    batch_error = None
    for task_id in task_ids:
        for repeat in range(1, args.repeats + 1):
            if batch_error is not None:
                skipped.append({"task_id": task_id, "repeat": repeat, "status": "provider_error_not_started"})
                if args.progress:
                    print_progress({"task_id": task_id, "status": "provider_error_not_started", "score": {}, "cost_usd": 0}, budget.spent if budget else 0.0)
                continue
            if budget and (budget.blocked or budget.spent >= budget.limit):
                skipped.append({"task_id": task_id, "repeat": repeat, "status": "budget_not_started"})
                if args.progress:
                    print_progress({"task_id": task_id, "status": "budget_not_started", "score": {}, "cost_usd": 0}, budget.spent)
                break
            meta = run_task(task_id, output / f"{task_id}_{repeat:02d}", fake_model=args.fake_model,
                            allow_real_model=args.allow_real_model, budget=budget, max_steps=args.max_steps,
                            capabilities=capabilities, parameters={"repeat": repeat, "repeats": args.repeats, "task_ids": task_ids, "cli": vars(args)})
            results.append(meta)
            if args.progress:
                print_progress(meta, budget.spent if budget else 0.0)
            else:
                print(json.dumps({key: meta[key] for key in ("run_id", "status", "final_answer", "score", "graph")}, ensure_ascii=False))
            write_json(output / "summary.json", results)
            if meta.get("provider_error", {}).get("stop_batch"):
                batch_error = meta["provider_error"]
                print(f"Stopping batch: OpenRouter HTTP {batch_error['http_status']}: {batch_error['message']}", flush=True)
            if meta["status"] == "cost_limit":
                break
    write_json(output / "summary.json", results)
    write_json(output / "batch_meta.json", {"parameters": vars(args), "skipped": skipped,
                                            **{key: sum(item.get(key, 0) for item in results) for key in COUNTERS},
                                            "unknown_cost_attempts": sum(item.get("unknown_cost_attempts", 0) for item in results),
                                            "cost_usd": budget.spent if budget else 0.0, "provider_error": batch_error})
    if args.progress:
        correct = sum(item["score"].get("success") == 1 for item in results)
        print(f"Summary: completed={len(results)} skipped={len(skipped)} correct={correct} "
              + " ".join(f"{key}={sum(item.get(key, 0) for item in results)}" for key in COUNTERS)
              + f" cost_usd={budget.spent if budget else 0.0:.6f} output={output}", flush=True)
    command = shlex.join([sys.executable, "-m", "dac.run_kramabench", *(sys.argv[1:] if argv is None else argv)])
    report = os.path.relpath(ROOT / "notes" / "12_交卷保护与防护文字.md", output)
    model_name = "FakeModel" if args.fake_model else "openai/gpt-6-luna"
    readme = (f"# KramaBench 批量运行\n\n日期：{now()}。模型：{model_name}。\n\n"
              f"命令：`PYTHONPATH=src {command}`。\n\n"
              f"尝试 {len(results)} 次任务，因预算或接口错误未启动 {len(skipped)} 次。具体结果见 summary.json。\n\n"
              f"工具说明与验证见 [12 号报告]({report})。\n")
    (output / "README.md").write_text(readme, encoding="utf-8")
    return 0 if results and not skipped and all(item["status"] == "success" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
