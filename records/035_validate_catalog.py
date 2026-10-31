"""Task 035 delivery checks. No network or third-party code execution."""
import collections
import csv
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
path = ROOT / "records/035_related_work.csv"
with path.open(encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
assert len(rows) == 56
assert [r["编号"] for r in rows] == [f"035-{i:03d}" for i in range(1, 57)]
assert len({r["链接"] for r in rows}) == len(rows)
required = ["标题", "作者", "所属部分与组件", "类型", "发表处与日期", "链接",
            "摘要原文", "系统形态", "任务类型", "是否用了训练", "代码核实状态",
            "许可证", "主要语言", "最近提交日期", "星数", "证据来源", "核实日期"]
for row in rows:
    assert all(row[k] for k in required), row["编号"]
    assert row["链接"].startswith("https://"), row["编号"]
    if "第三部分" in row["所属部分与组件"]:
        assert "“" in row["涉及组件及其原句"] and "https://" in row["涉及组件及其原句"], row["编号"]
    if row["类型"] == "工程":
        assert row["接入方式"] and row["接入方式README原句"] and row["支持哪些工具类型"]
    if row["类型"].startswith("论文") and re.fullmatch(r"\d{4}\.\d{4,5}", row["arXiv编号"]):
        assert row["链接"].endswith(row["arXiv编号"])

parts = {p: sum(p in r["所属部分与组件"] for r in rows)
         for p in ["第一部分", "第二部分", "第三部分", "第四部分"]}
components = {f"C{i}": sum(f"第三部分-C{i}" in r["所属部分与组件"] for r in rows)
              for i in range(1, 10)}
assert parts["第一部分"] <= 15 and parts["第二部分"] <= 15
assert all(n <= 10 for n in components.values())

queries = json.loads((ROOT / "records/035_search_log.json").read_text())
assert len({q["query_id"] for q in queries}) == len(queries) == 77
assert all(q["query"] and isinstance(q["returned_count"], int) for q in queries)
manifest = json.loads((ROOT / "records/035_source_manifest.json").read_text())
verified_urls = {d["url"] for d in manifest["arxiv_pages"]}
verified_urls |= {d["url"] for d in manifest["github_pages"] if d.get("status") == 200}
verified_urls |= {d["url"] for d in manifest["web_open_attempts"] if d["status"] == "已打开"}
assert all(r["链接"] in verified_urls for r in rows)
assert not any("MORPH-DA" in r["标题"] for r in rows)
print(json.dumps({"status": "PASS", "rows": len(rows), "parts": parts,
                  "components": components, "queries": len(queries)}, ensure_ascii=False))
