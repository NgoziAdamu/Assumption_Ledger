#!/usr/bin/env python3
"""按指定字段和格式机械摘录；只读原输入及标注，不调用模型或数据库。"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import statistics


ROOT = Path(__file__).resolve().parents[1]
START_COMMIT = "fbd7d426068cc472df771badcecee89d8364bbac"
START_MAX_NUMBER = 45
START_TIME = "2026-11-05T22:11:38+08:00"
INPUT_SHA256 = {
    "records/044_stats/object_audit.json":
        "14cedecfcc1bfea3cd277645dbdb4e2fff04057e62784731df605eb0abe6d57c",
    "records/044_stats/point_audit.json":
        "abd446ae3c7f04e54e381fd62d28aed3cafc057cdad6d28ae4bc7973bbb762dc",
}
CATEGORIES = {"Data Misconception", "Intent Misreading"}
EXPECTED = {
    "对象数": 79,
    "对象benchmark": {"DAComp": 70, "KramaBench": 9},
    "点数": 119,
    "点benchmark": {"DAComp": 110, "KramaBench": 9},
    "点类别": {"Data Misconception": 27, "Intent Misreading": 92},
    "点角色": {"主要": 55, "参与": 36, "并列": 28},
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal(text, start):
    return {"文字": text, "源起始字符": start}


def join_parts(groups, newline_offset):
    result = []
    for group in groups:
        if result:
            result.append(literal("\n", newline_offset))
        result.extend(group)
    return result


def part_text(parts):
    return "".join(p["文字"] for p in parts)


def clip(parts, limit):
    length = len(part_text(parts))
    if length <= limit:
        return parts
    result = []
    remaining = limit
    for p in parts:
        if not remaining:
            break
        take = min(remaining, len(p["文字"]))
        result.append(literal(p["文字"][:take], p["源起始字符"]))
        remaining -= take
    result.append({"文字": f"[截断，原长 {length} 字符]", "源起始字符": None})
    return result


def source_lines(text):
    result = []
    offset = 0
    for line in text.splitlines(keepends=True):
        content = line.removesuffix("\n").removesuffix("\r")
        result.append({"文字": content, "源起始字符": offset})
        offset += len(line)
    return result


def title_level(text):
    match = re.match(r"^#+", text)
    return len(match[0]) if match else None


def keep_line(line):
    return bool(line["文字"].strip()) and not line["文字"].startswith("|")


def format_body(lines, source):
    """先识别原文块边界；块内去空行/表格行，再限制内容字符数。"""
    newline_offset = source.index("\n")
    before_groups, after_groups, blocks = [], [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        text = line["文字"]
        if text.startswith("```"):
            end = next((j for j in range(i + 1, len(lines))
                        if lines[j]["文字"].startswith("```")), None)
            if end is None:
                raise ValueError("所选段落存在未闭合的 ```，停止而不猜测边界")
            content = join_parts([[p] for p in lines[i + 1:end] if keep_line(p)],
                                 newline_offset)
            before = [line]
            after = [line]
            if content:
                before = join_parts([before, content], newline_offset)
                after = join_parts([after, clip(content, 400)], newline_offset)
            before = join_parts([before, [lines[end]]], newline_offset)
            after = join_parts([after, [lines[end]]], newline_offset)
            before_groups.append(before)
            after_groups.append(after)
            blocks.append({"类型": "代码块", "截断前字符数": len(part_text(content)),
                           "已截断": len(part_text(content)) > 400,
                           "源起始字符": line["源起始字符"]})
            i = end + 1
        elif text.startswith(">"):
            end = i + 1
            while end < len(lines) and lines[end]["文字"].startswith(">"):
                end += 1
            content = join_parts([[p] for p in lines[i:end] if keep_line(p)],
                                 newline_offset)
            before_groups.append(content)
            after_groups.append(clip(content, 400))
            blocks.append({"类型": "引用块", "截断前字符数": len(part_text(content)),
                           "已截断": len(part_text(content)) > 400,
                           "源起始字符": line["源起始字符"]})
            i = end
        else:
            if keep_line(line):
                before_groups.append([line])
                after_groups.append([line])
            i += 1
    before = part_text(join_parts(before_groups, newline_offset))
    after_parts = join_parts(after_groups, newline_offset)
    after = part_text(after_parts)
    return before, after, blocks, verify(after, after_parts, source)


def verify(body, parts, source):
    """逐段覆盖全部正文；只豁免本脚本实际插入的截断标记。"""
    spans, failures = [], []
    cursor = 0
    for part in parts:
        text = part["文字"]
        if not text:
            continue
        end = cursor + len(text)
        start = part["源起始字符"]
        if start is None:
            valid = bool(re.fullmatch(r"\[截断，原长 \d+ 字符\]", text))
            span = {"类型": "截断标记", "正文字符区间": [cursor, end]}
        else:
            valid = source[start:start + len(text)] == text and text in source
            span = {"类型": "原文", "正文字符区间": [cursor, end],
                    "源文件字符区间": [start, start + len(text)]}
        if body[cursor:end] != text or not valid:
            failures.append(span)
        spans.append(span)
        cursor = end
    if cursor != len(body):
        failures.append({"覆盖字符数": cursor, "正文字符数": len(body)})
    return {"通过": not failures, "原文片段数": sum(s["类型"] == "原文" for s in spans),
            "失败片段": failures, "完整覆盖正文": cursor == len(body), "片段": spans}


def locate_file(point):
    batch = re.fullmatch(r"records/(\d{3})_points\.csv", point["source"])[1]
    directories = [f"records/{batch}_annotations"]
    if batch == "036":
        directories.append("records/034_annotations")
    searches = []
    for directory in directories:
        folder = ROOT / directory
        matches = sorted(str(p.relative_to(ROOT)) for p in folder.iterdir()
                         if p.is_file() and p.name.endswith(point["对象编号"] + ".md")) \
            if folder.is_dir() else []
        searches.append({"目录": directory, "匹配文件": matches})
        if matches:
            return matches, searches
    return [], searches


def extract(point, obj):
    result = {
        "benchmark": point["benchmark"], "对象编号": point["对象编号"],
        "main_category": obj["main_category"], "错误点名称": point["错误点名称"],
        "类别": point["normalized_category"], "角色": point["角色"],
        "point_id": point["point_id"], "source": point["source"],
        "文件路径": None, "起止行号": None,
        "截断前字符数": None, "截断后字符数": None, "正文": "",
        "去重标记": None, "定位状态": None, "匹配标题行号": [],
        "逐字核对": {"通过": None, "原因": "尚未定位"}, "块记录": [],
    }
    paths, searches = locate_file(point)
    result["文件查找记录"] = searches
    if len(paths) != 1:
        result["定位状态"] = "文件未定位"
        return result
    path = ROOT / paths[0]
    source = path.read_bytes().decode("utf-8")
    lines = source_lines(source)
    result["文件路径"] = paths[0]
    result["源文件sha256"] = sha256(path)
    matches = [i for i, line in enumerate(lines)
               if line["文字"].startswith("#") and point["错误点名称"] in line["文字"]]
    result["匹配标题行号"] = [i + 1 for i in matches]
    if len(matches) != 1:
        result["定位状态"] = "段落未定位"
        return result
    start = matches[0]
    level = title_level(lines[start]["文字"])
    end = next((i for i in range(start + 1, len(lines))
                if title_level(lines[i]["文字"]) is not None
                and title_level(lines[i]["文字"]) <= level), len(lines))
    before, after, blocks, verification = format_body(lines[start + 1:end], source)
    result.update({"定位状态": "已定位", "起止行号": [start + 1, end],
                   "源标题行": lines[start]["文字"],
                   "截断前字符数": len(before), "截断后字符数": len(after),
                   "正文": after, "逐字核对": verification, "块记录": blocks})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--number", default=Path(__file__).name[:3])
    parser.add_argument("--output-dir", type=Path, default=ROOT / "records")
    args = parser.parse_args()
    if not re.fullmatch(r"\d{3}", args.number):
        parser.error("--number 必须是三位编号")
    hashes = {p: sha256(ROOT / p) for p in INPUT_SHA256}
    if hashes != INPUT_SHA256:
        raise SystemExit("输入 sha256 与开工记录不一致，停止")
    objects_all = json.loads((ROOT / "records/044_stats/object_audit.json").read_text())
    points_all = json.loads((ROOT / "records/044_stats/point_audit.json").read_text())
    objects = [o for o in objects_all if o["denominator2"] is True
               and CATEGORIES.intersection(o["incidence_categories"])]
    by_id = {o["object_id"]: o for o in objects}
    assert len(by_id) == len(objects), "对象编号重复"
    points = [p for p in points_all if p["对象编号"] in by_id
              and p["normalized_category"] in CATEGORIES and p["角色"] != "非原因"]
    observed = {
        "对象数": len(objects), "对象benchmark": dict(Counter(o["benchmark"] for o in objects)),
        "点数": len(points), "点benchmark": dict(Counter(p["benchmark"] for p in points)),
        "点类别": dict(Counter(p["normalized_category"] for p in points)),
        "点角色": dict(Counter(p["角色"] for p in points)),
    }
    if observed != EXPECTED:
        print(json.dumps({"预期": EXPECTED, "实际": observed}, ensure_ascii=False, indent=2))
        raise SystemExit("自检数字不一致，停止；不得更改筛选条件")
    assert len({p["point_id"] for p in points}) == len(points), "point_id 重复"
    points.sort(key=lambda p: (p["benchmark"], p["对象编号"], p["source"], p["source_row"]))
    rows = [extract(p, by_id[p["对象编号"]]) for p in points]
    seen = {}
    for row in rows:
        if row["定位状态"] != "已定位":
            continue
        key = (row["对象编号"], row["正文"])
        if key in seen:
            previous = seen[key]
            row["去重标记"] = f'与 {previous["错误点名称"]}（{previous["point_id"]}）点正文相同'
        else:
            seen[key] = row
    located = [r for r in rows if r["定位状态"] == "已定位"]
    lengths = [r["截断后字符数"] for r in located]
    before_lengths = [r["截断前字符数"] for r in located]
    blocks = [b for r in located for b in r["块记录"]]
    summary = {
        "定位状态": dict(Counter(r["定位状态"] for r in rows)),
        "逐字核对通过点数": sum(r["逐字核对"]["通过"] is True for r in rows),
        "逐字核对失败点数": sum(r["逐字核对"]["通过"] is False for r in rows),
        "原文片段总数": sum(r["逐字核对"]["原文片段数"] for r in located),
        "截断前总字符数": sum(before_lengths), "截断后总字符数": sum(lengths),
        "截断前每点中位数": statistics.median(before_lengths) if before_lengths else None,
        "截断前每点最大值": max(before_lengths, default=None),
        "截断后每点中位数": statistics.median(lengths) if lengths else None,
        "截断后每点最大值": max(lengths, default=None),
        "代码块总数": sum(b["类型"] == "代码块" for b in blocks),
        "引用块总数": sum(b["类型"] == "引用块" for b in blocks),
        "截断代码块数": sum(b["类型"] == "代码块" and b["已截断"] for b in blocks),
        "截断引用块数": sum(b["类型"] == "引用块" and b["已截断"] for b in blocks),
        "逐字相同正文标记点数": sum(r["去重标记"] is not None for r in rows),
        "使用034回退点数": sum(r["文件路径"] is not None and
                              r["文件路径"].startswith("records/034_annotations/") for r in rows),
    }
    for r in located:
        assert sha256(ROOT / r["文件路径"]) == r["源文件sha256"], "源文件运行中发生改变"
    assert summary["逐字核对失败点数"] == 0, "逐字核对失败，停止"
    payload = {
        "metadata": {
            "编号": args.number, "开工阶段时间记录": START_TIME,
            "开工时commit": START_COMMIT, "开工时最大编号": START_MAX_NUMBER,
            "开工时输入sha256": hashes,
            "排序": "benchmark、对象编号；对象内按 source、source_row",
            "字符计数口径": "Python len(str)，Unicode code point；正文不含匹配标题行，"
            "去空行及以 | 开头的行后、截断前后分别计数；行间计一个 LF，末尾不加 LF。",
            "块截断口径": "按原始连续行识别代码块/引用块；代码块内容去空行及表格行后计数，"
            "不含 ``` 围栏；引用块含 > 前缀及行间 LF；每块保留前400字符，紧接截断标记。",
            "行号口径": "1-based，首尾均含；包含匹配标题，段尾含下个同级或更高级标题前的空行。",
            "字符区间口径": "逐字核对片段中，正文与源文件均为0-based、左闭右开；"
            "源文件以 UTF-8 解码，原文片段含行间 LF，全部正文逐段覆盖，仅豁免生成的截断标记。",
            "去重口径": "同一对象，处理后正文逐字相同则指向排序后首个点；所有点仍全文保留。",
        },
        "self_check": {"预期": EXPECTED, "实际": observed, "通过": observed == EXPECTED},
        "summary": summary, "points": rows,
    }
    md = ["# Data Misconception 与 Intent Misreading：标注原文摘录", "",
          "仅按字段、标题和格式规则摘录。各点正文保留原文；不写前提句、不概括、不合并。", "",
          "字符计数、逐字核对和完整查找记录见同名 JSON；源段落行号包含原始标题行。", ""]
    last_object = None
    for r in rows:
        key = (r["benchmark"], r["对象编号"])
        if key != last_object:
            md.extend([f'## {r["benchmark"]} / {r["对象编号"]} | main_category：{r["main_category"]}', ""])
            last_object = key
        location = (f'{r["文件路径"]}:{r["起止行号"][0]}-{r["起止行号"][1]}'
                    if r["起止行号"] else f'{r["文件路径"] or "未定位"}（{r["定位状态"]}）')
        md.extend([f'### {r["错误点名称"]} | {r["类别"]} | {r["角色"]} | {location}', "",
                   f'point_id：`{r["point_id"]}`；定位状态：{r["定位状态"]}。', ""])
        if r["去重标记"]:
            md.extend([f'去重标记：{r["去重标记"]}。', ""])
        if r["定位状态"] == "已定位":
            md.extend([r["正文"], ""])
        else:
            md.extend(["定位记录：" + json.dumps({"文件查找记录": r["文件查找记录"],
                       "匹配标题行号": r["匹配标题行号"]}, ensure_ascii=False), ""])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / f"{args.number}_premise_sources.json"
    md_path = args.output_dir / f"{args.number}_premise_sources.md"
    if json_path.exists() or md_path.exists():
        raise SystemExit("目标文件已存在，拒绝覆盖；可用 --output-dir 在新目录重现")
    with json_path.open("x", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    with md_path.open("x", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(json.dumps({"self_check": payload["self_check"], "summary": summary},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
