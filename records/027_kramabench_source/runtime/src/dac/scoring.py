"""Apply official deterministic metrics without importing or calling models."""

import ast
from collections import Counter
import json
import logging
import re
from types import SimpleNamespace
from typing import List


class JudgeRequired(BaseException):
    """Escape the official metric's broad exception handler without a model."""


class NoModelJudge:
    def __init__(self, **kwargs):
        pass

    def evaluate_paraphrase(self, *args, **kwargs):
        raise JudgeRequired("String approximation requires a model judge.")


class UnigramScorer:
    """Match default ROUGE-1 tokenization for the official string-list branch."""

    def __init__(self, metrics):
        if metrics != ["rouge1"]:
            raise ValueError("Only deterministic ROUGE-1 is supported.")

    def score(self, target, prediction):
        reference = Counter(re.findall(r"[a-z0-9]+", target.lower()))
        candidate = Counter(re.findall(r"[a-z0-9]+", prediction.lower()))
        matches = sum((reference & candidate).values())
        precision = matches / sum(candidate.values()) if candidate else 0.0
        recall = matches / sum(reference.values()) if reference else 0.0
        return {"rouge1": SimpleNamespace(precision=precision, recall=recall)}


def metric_definitions(benchmark):
    """Load allowlisted definitions, replacing answer eval with literal_eval."""
    path = benchmark / "benchmark" / "metrics.py"
    keep = {"str_to_float", "try_convert_to_number", "Success", "MeanAbsoluteError", "MeanSquaredError", "RAEScore",
            "F1", "Precision", "Recall", "F1Approximate"}
    definitions = [node for node in ast.parse(path.read_text(encoding="utf-8")).body
                   if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in keep]
    namespace = {"Metric": type("Metric", (), {}), "logging": logging, "List": List, "json": json,
                 "eval": ast.literal_eval, "GPTInterface": NoModelJudge,
                 "rouge_scorer": SimpleNamespace(RougeScorer=UnigramScorer)}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def official_score(task, answer, benchmark):
    kind = task["answer_type"]
    source = "official_deterministic_definitions"
    if kind == "string_approximate":
        return {"status": "needs_judge", "success": None, "source": source}
    if answer is None:
        return {"status": "unanswered", "success": 0, "source": source}
    namespace = metric_definitions(benchmark)
    result = {"status": "scored", "source": source}
    if kind in {"numeric_exact", "numeric_approximate", "string_exact"}:
        result["success"] = namespace["Success"]()(answer, task["answer"])[0]
        if kind == "numeric_approximate":
            for name, label in (("MeanAbsoluteError", "mean_absolute_error"), ("MeanSquaredError", "mean_squared_error"), ("RAEScore", "rae_score")):
                result[label] = namespace[name]()(answer, task["answer"])[0]
    elif kind in {"list_exact", "list_approximate"}:
        metrics = (("F1", "f1"), ("Precision", "precision"), ("Recall", "recall")) if kind == "list_exact" else (("F1Approximate", "f1_approximate"),)
        for name, label in metrics:
            try:
                result[label] = namespace[name]()(answer, task["answer"])[0]
            except JudgeRequired:
                return {"status": "needs_judge", "success": None, "source": source}
            except Exception as error:
                result[label] = 0.0
                result.setdefault("metric_errors", {})[label] = type(error).__name__
        result["success"] = int(result["f1" if kind == "list_exact" else "f1_approximate"] == 1.0)
    else:
        return {"status": "unsupported", "success": None, "source": source}
    return result


def official_numeric_score(task, answer, benchmark):
    """Keep compatibility with callers of the original numeric entry point."""
    return official_score(task, answer, benchmark)
