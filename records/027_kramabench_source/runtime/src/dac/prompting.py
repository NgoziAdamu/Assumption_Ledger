"""Load only approved prompt files and prepare runtime substitutions."""

import hashlib
import json
import re
from pathlib import Path

from prompt_loader import load_prompt

LIBRARIES = "pandas, numpy, scipy, scikit-learn, statsmodels, matplotlib, beautifulsoup4, lxml, openpyxl, geopandas"
PROMPT_PATHS = ("prompts/kramabench_system_v2.md", "prompts/kramabench_task.md",
                "prompts/kramabench_tool_run_python.json", "prompts/kramabench_fixed_messages_v2.json")


def load_fixed_messages():
    """Load approved feedback before starting the untrusted execution session."""
    return json.loads(load_prompt(PROMPT_PATHS[3]))


def file_listing(data_dir, limit=200):
    root = Path(data_dir)
    files = sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.relative_to(root).as_posix())
    lines = [f"{p.relative_to(root).as_posix()} ({p.stat().st_size} bytes)" for p in files[:limit]]
    groups = {}
    for path in files[limit:]:
        folder = path.relative_to(root).parent.as_posix()
        count, size = groups.get(folder, (0, 0))
        groups[folder] = (count + 1, size + path.stat().st_size)
    for folder, (count, size) in sorted(groups.items()):
        lines.append(f"{folder}/: {count} additional files, {size} bytes")
    return "\n".join(lines)


def prepare_prompts(data_dir, query):
    source = {path: load_prompt(path) for path in PROMPT_PATHS}
    values = {"max_output_chars": "4000", "data_dir": str(Path(data_dir).resolve()), "libraries": LIBRARIES,
              "query": query, "file_listing": file_listing(data_dir)}
    rendered = []
    for path in PROMPT_PATHS[:2]:
        text = source[path]
        # Replace in one pass so braces inside task data are never interpreted.
        text = re.sub(r"{{(max_output_chars|data_dir|libraries|query|file_listing)}}", lambda m: values[m.group(1)], text)
        rendered.append(text)
    return {"system": rendered[0], "task": rendered[1], "tool": json.loads(source[PROMPT_PATHS[2]]),
            "fixed": json.loads(source[PROMPT_PATHS[3]]), "values": values,
            "hashes": {path: hashlib.sha256(text.encode()).hexdigest() for path, text in source.items()}}
