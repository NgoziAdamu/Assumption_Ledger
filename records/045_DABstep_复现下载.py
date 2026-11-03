"""按本报告的固定版本、大小与 SHA-256 复现下载；不调用 agent。"""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(__file__).with_name(Path(__file__).name.replace("复现下载.py", "文件清单.json"))
LIMIT = 2_000_000_000
for entry in json.loads(MANIFEST.read_text())["files"]:
    if entry["bytes"] > LIMIT:
        raise SystemExit(f"STOP: 超过 2 GB，须获得确认：{entry['url']}")
    target = ROOT / entry["path"]
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == entry["sha256"]:
        print(f"verified existing: {entry['path']}")
        continue
    with urllib.request.urlopen(entry["url"], timeout=60) as response:
        if int(response.headers.get("Content-Length", 0)) > LIMIT:
            raise SystemExit(f"STOP: 超过 2 GB，须获得确认：{entry['url']}")
        body = response.read(entry["bytes"] + 1)
    if len(body) != entry["bytes"] or hashlib.sha256(body).hexdigest() != entry["sha256"]:
        raise SystemExit(f"文件大小或 SHA-256 不一致：{entry['path']}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(body)
    print(f"downloaded: {entry['path']} ({len(body)} bytes)")
