#!/usr/bin/env python3
"""原样存档前提句草稿、按序号合并并机械核对。默认只读，--archive 创建新文件。"""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
NUMBER = Path(__file__).name[:3]
START_COMMIT = "146009075ebb4e63d3214134de49710a15e46873"
START_MAX_NUMBER = 46
DOWNLOADS = Path("/mnt/c/Users/jucc116/Downloads")
INPUTS = {
    "前提句_第1批_序号0-39.csv": "3c051aa61f067586a518791e9f4f16a5832e64f2b9f5c3ee42bec219d425b7e9",
    "前提句_第2批_序号40-79.csv": "de26315bb3a22a4322094ce9db2fd49c4f5e82327012cd262019f7fd25b2bc07",
    "前提句_第3批_序号80-118.csv": "5240d5b431b8178112b87ac6f05909bb3dd67cb09e60c07817cbcc6e17a68397",
}
REFERENCE = ROOT / "records/046_premise_sources.json"
REFERENCE_SHA256 = "c37cb2c4c90bbab51b73ee5773b980ae32a174ec9ecf7f60cbda35423f819be7"
FIELDS = ["benchmark", "对象编号", "错误点名称", "类别", "角色"]
KNOWN_SEQUENCES = ["90", "91", "110", "114", "115", "118"]
BOM = b"\xef\xbb\xbf"


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    if not raw.startswith(BOM):
        raise ValueError("输入缺少 UTF-8 BOM")
    table = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline="")))
    if not table:
        raise ValueError("CSV 没有表头")
    header = table[0]
    if len(set(header)) != len(header):
        raise ValueError("CSV 存在重复列名")
    for n, row in enumerate(table[1:], 2):
        if len(row) != len(header):
            raise ValueError(f"CSV 第 {n} 条记录的列数与表头不同")
    return header, table[1:]


def read_batches(folder):
    missing = [str(folder / name) for name in INPUTS if not (folder / name).is_file()]
    if missing:
        raise ValueError("指定文件不存在；不查找替代文件：" + json.dumps(missing, ensure_ascii=False))
    batches = []
    for name, expected in INPUTS.items():
        raw = (folder / name).read_bytes()
        header, rows = parse(raw)
        batches.append({"文件名": name, "raw": raw, "header": header,
                        "rows": rows, "sha256": sha256(raw), "expected": expected})
    return batches


def check_headers(batches):
    header = batches[0]["header"]
    if any(b["header"] != header for b in batches):
        raise ValueError("三个文件表头不同，停止合并：" + json.dumps(
            {b["文件名"]: b["header"] for b in batches}, ensure_ascii=False))
    required = {"序号", "point_id", "做错或漏做", "备注", "素材出处", *FIELDS}
    if not required.issubset(header):
        raise ValueError("缺少所需列：" + repr(sorted(required - set(header))))
    return header


def sorted_rows(batches, header):
    index = header.index("序号")
    rows = [r for b in batches for r in b["rows"]]
    # 非数字序号保留原文放在末尾，并在核对结果中列明，不修改单元格。
    def key(row):
        try:
            return (0, int(row[index]))
        except ValueError:
            return (1, row[index])
    return sorted(rows, key=key)


def archive(folder):
    batches = read_batches(folder)
    archive_dir = ROOT / f"records/{NUMBER}_premise_drafts"
    merged_path = ROOT / f"records/{NUMBER}_premise_sentences_draft.csv"
    if archive_dir.exists() or merged_path.exists():
        raise ValueError("存档目标已存在，拒绝覆盖")
    archive_dir.mkdir()
    for b in batches:
        with (archive_dir / b["文件名"]).open("xb") as f:
            f.write(b["raw"])
        if (archive_dir / b["文件名"]).read_bytes() != b["raw"]:
            raise ValueError("逐字节复制核对失败：" + b["文件名"])
    header = check_headers(batches)
    with merged_path.open("x", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, lineterminator="\r\n")
        writer.writerow(header)
        writer.writerows(sorted_rows(batches, header))


def check(folder):
    archive_dir = ROOT / f"records/{NUMBER}_premise_drafts"
    merged_path = ROOT / f"records/{NUMBER}_premise_sentences_draft.csv"
    batches = read_batches(archive_dir)
    header = check_headers(batches)
    merged_raw = merged_path.read_bytes()
    merged_header, merged_rows = parse(merged_raw)
    reference_raw = REFERENCE.read_bytes()
    reference = json.loads(reference_raw)["points"]
    rows = [dict(zip(merged_header, r)) for r in merged_rows]
    discrepancies = []
    file_checks = []
    for batch in batches:
        name = batch["文件名"]
        source = folder / name
        source_raw = source.read_bytes() if source.is_file() else None
        entry = {
            "文件名": name, "源路径": str(source),
            "归档路径": str((archive_dir / name).relative_to(ROOT)),
            "字节数": len(batch["raw"]), "数据行数": len(batch["rows"]),
            "开工sha256": batch["expected"], "副本sha256": batch["sha256"],
            "副本与开工sha256一致": batch["sha256"] == batch["expected"],
            "原文件当前存在": source_raw is not None,
            "原文件当前sha256": sha256(source_raw) if source_raw is not None else None,
            "复制前后逐字节一致": source_raw == batch["raw"] if source_raw is not None else None,
            "带UTF8_BOM": batch["raw"].startswith(BOM),
        }
        file_checks.append(entry)
        if not entry["副本与开工sha256一致"] or entry["复制前后逐字节一致"] is False:
            discrepancies.append({"类型": "原样复制核对不一致", "文件名": name})
    headers_equal = merged_header == header
    content_equal = headers_equal and merged_rows == sorted_rows(batches, header)
    if not headers_equal:
        discrepancies.append({"类型": "合并表头不一致", "原表头": header, "合并表头": merged_header})
    if not content_equal:
        discrepancies.append({"类型": "合并表格与按序号排序的输入逐单元格不一致"})
    sequences = [r["序号"] for r in rows]
    sequence_counts = Counter(sequences)
    expected_sequences = [str(i) for i in range(119)]
    sequence_check = {
        "行数": len(rows), "预期行数": 119,
        "缺失序号": [s for s in expected_sequences if s not in sequence_counts],
        "额外序号": [s for s in sequence_counts if s not in expected_sequences],
        "重复序号": {s: n for s, n in sequence_counts.items() if n > 1},
        "按0至118依次排列": sequences == expected_sequences,
    }
    if sequences != expected_sequences:
        discrepancies.append({"类型": "序号或行数核对失败", **sequence_check})
    reference_counts = Counter(r["point_id"] for r in reference)
    merged_counts = Counter(r["point_id"] for r in rows)
    point_check = {
        "046独立point_id数": len(reference_counts), "合并独立point_id数": len(merged_counts),
        "缺失point_id": sorted(reference_counts.keys() - merged_counts.keys()),
        "额外point_id": sorted(merged_counts.keys() - reference_counts.keys()),
        "重复point_id": {p: n for p, n in merged_counts.items() if n > 1},
        "046重复point_id": {p: n for p, n in reference_counts.items() if n > 1},
        "集合完全相同": reference_counts.keys() == merged_counts.keys(),
    }
    if not point_check["集合完全相同"] or point_check["重复point_id"] or point_check["046重复point_id"]:
        discrepancies.append({"类型": "point_id核对失败", **point_check})
    by_id = {r["point_id"]: r for r in reference}
    field_mismatches = []
    for row in rows:
        if row["point_id"] not in by_id:
            continue
        for field in FIELDS:
            expected = by_id[row["point_id"]][field]
            if row[field] != expected:
                field_mismatches.append({"序号": row["序号"], "point_id": row["point_id"],
                                         "字段": field, "合并文件值": row[field], "046值": expected})
    discrepancies.extend({"类型": "字段逐字不一致", **m} for m in field_mismatches)
    known_checks = []
    for sequence in KNOWN_SEQUENCES:
        matching = [r for r in rows if r["序号"] == sequence]
        entry = {"序号": sequence, "通过": False}
        if len(matching) != 1:
            entry["失败原因"] = "该序号未定位到唯一行"
        else:
            row = matching[0]
            entry.update({"point_id": row["point_id"], "错误点名称": row["错误点名称"],
                          "素材出处": row["素材出处"]})
            matches = re.findall(r"(records/034_annotations/[^\s：:（）]+\.md):标题行\s*(\d+)",
                                 row["素材出处"])
            if len(matches) != 1:
                entry["失败原因"] = "素材出处未包含唯一的034文件路径与标题行号"
            else:
                path, line_number = matches[0]
                number = int(line_number)
                file = ROOT / path
                exists = file.is_file()
                lines = file.read_bytes().decode("utf-8").splitlines() if exists else []
                line = lines[number - 1] if 1 <= number <= len(lines) else None
                entry.update({"034文件路径": path, "标题行号": number, "文件存在": exists,
                              "标题行原文": line, "以井号开头": line is not None and line.startswith("#"),
                              "包含错误点名称": line is not None and row["错误点名称"] in line})
                entry["通过"] = exists and entry["以井号开头"] and entry["包含错误点名称"]
        known_checks.append(entry)
        if not entry["通过"]:
            discrepancies.append({"类型": "034标题核对失败", **entry})
    reference_unchanged = sha256(reference_raw) == REFERENCE_SHA256
    if not reference_unchanged:
        discrepancies.append({"类型": "046输入sha256与开工记录不一致"})
    return {
        "编号": NUMBER, "开工时commit": START_COMMIT, "开工时最大编号": START_MAX_NUMBER,
        "状态": "前提句尚未人工复核", "输入文件核对": file_checks,
        "表头": header, "三个输入表头完全相同": True,
        "合并文件带UTF8_BOM": merged_raw.startswith(BOM),
        "合并表头与输入相同": headers_equal, "合并所有单元格原文完全一致": content_equal,
        "合并文件sha256": sha256(merged_raw),
        "046文件sha256": sha256(reference_raw), "046文件未变": reference_unchanged,
        "序号核对": sequence_check, "point_id核对": point_check,
        "逐字段核对数": len(rows) * len(FIELDS), "逐字段不一致": field_mismatches,
        "做错或漏做统计": dict(Counter(r["做错或漏做"] for r in rows)),
        "备注不为空": [{"序号": r["序号"], "备注": r["备注"]} for r in rows if r["备注"] != ""],
        "046已知六点034标题核对": known_checks,
        "不一致清单": discrepancies, "全部机械核对通过": not discrepancies,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", action="store_true", help="先逐字节复制并合并；拒绝覆盖已有文件")
    parser.add_argument("--source-dir", type=Path, default=DOWNLOADS)
    args = parser.parse_args()
    try:
        if args.archive:
            archive(args.source_dir)
        result = check(args.source_dir)
    except (ValueError, OSError, UnicodeError, csv.Error) as error:
        print(json.dumps({"停止原因": str(error)}, ensure_ascii=False, indent=2))
        raise SystemExit(2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # 数字、字段或标题不一致时，保留复制和合并结果，不进行自动修正。
    raise SystemExit(0 if result["全部机械核对通过"] else 1)


if __name__ == "__main__":
    main()
