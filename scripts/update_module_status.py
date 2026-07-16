#!/usr/bin/env python3
"""Synchronize one module README with the global module-status table."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import tempfile
from pathlib import Path


MODULES_START = "<!-- MODULES_START -->"
MODULES_END = "<!-- MODULES_END -->"
AUDITS_START = "<!-- AUDITS_START -->"
AUDITS_END = "<!-- AUDITS_END -->"
ALLOWED = {"规划中", "编写中", "待审查", "待修订", "复审中", "可学习", "学习中", "已学习", "已阻塞", "已暂停"}
AUDIT_REQUIRED = {"可学习", "学习中", "已学习"}


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>").strip()


def is_external(value: str) -> bool:
    return value.startswith(("http://", "https://"))


def ensure_path(root: Path, value: str, label: str) -> None:
    if not value or value == "-":
        raise ValueError(f"{label} is required")
    if not is_external(value) and not (root / value).exists():
        raise FileNotFoundError(f"{label} does not exist: {value}")


def link_for_root(value: str) -> str:
    if not value or value == "-":
        return "-"
    if is_external(value):
        return f"[来源]({value})"
    normalized = value.replace("\\", "/")
    target = f"<{normalized}>" if " " in normalized else normalized
    return f"[{Path(normalized).name}]({target})"


def link_for_module(root: Path, module_dir: Path, value: str) -> str:
    if not value or value == "-":
        return "-"
    if is_external(value):
        return f"[来源]({value})"
    target = (root / value).resolve()
    relative = os.path.relpath(target, module_dir).replace("\\", "/")
    wrapped = f"<{relative}>" if " " in relative else relative
    return f"[{target.name}]({wrapped})"


def replace_meta(text: str, label: str, value: str) -> str:
    pattern = rf"(?m)^- {re.escape(label)}：.*$"
    replacement = f"- {label}：{value}"
    if not re.search(pattern, text):
        raise ValueError(f"Module README is missing metadata field: {label}")
    return re.sub(pattern, replacement, text, count=1)


def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def upsert_module_row(text: str, module_id: str, row: str) -> str:
    start = text.find(MODULES_START)
    end = text.find(MODULES_END)
    if start < 0 or end < 0 or end <= start:
        raise ValueError("Progress table is missing MODULES markers")
    block = text[start:end]
    lines = block.splitlines()
    for index, line in enumerate(lines):
        cells = table_cells(line) if line.lstrip().startswith("|") else []
        if cells and cells[0] == module_id:
            lines[index] = row
            break
    else:
        lines.append(row)
    new_block = "\n".join(lines) + "\n"
    return text[:start] + new_block + text[end:]


def append_audit_row(text: str, report: str, row: str) -> str:
    if report == "-":
        return text
    start = text.find(AUDITS_START)
    end = text.find(AUDITS_END)
    if start < 0 or end < 0 or end <= start:
        raise ValueError("Module README is missing AUDITS markers")
    if Path(report).name in text[start:end]:
        return text
    prefix = text[:end]
    if not prefix.endswith("\n"):
        prefix += "\n"
    return prefix + row + "\n" + text[end:]


def atomic_write(path: Path, content: str) -> None:
    fd, name = tempfile.mkstemp(prefix="study-anything-", suffix=".md", dir=path.parent)
    os.close(fd)
    temp = Path(name)
    try:
        temp.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temp, path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--module-dir", required=True, help="Path relative to workbench root")
    parser.add_argument("--module-id", required=True)
    parser.add_argument("--module-title", required=True)
    parser.add_argument("--status", required=True, choices=sorted(ALLOWED))
    parser.add_argument("--audit-result", default="待审查")
    parser.add_argument("--audit-report", default="-")
    parser.add_argument("--audit-type", choices=("初审", "修订", "复审"))
    parser.add_argument("--learning-evidence", default="-")
    parser.add_argument("--learning-review", default="-")
    parser.add_argument("--next-step", required=True)
    parser.add_argument("--date", default=dt.date.today().isoformat())
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    module_dir = (root / args.module_dir).resolve()
    readme = module_dir / "README.md"
    progress = root / "学习进度表.md"
    if not readme.exists() or not progress.exists():
        raise FileNotFoundError("Module README or progress table is missing")

    if args.status in AUDIT_REQUIRED:
        ensure_path(root, args.audit_report, "Passing audit report")
        if args.audit_result not in {"通过", "修改后通过"}:
            raise ValueError("A learnable module requires a passing audit result")
        audit_path = (root / args.audit_report).resolve() if not is_external(args.audit_report) else None
        if audit_path is not None and (module_dir / "审查").resolve() not in audit_path.parents:
            raise ValueError("Teaching audit report must be inside the module 审查 directory")

    if args.status == "已学习":
        ensure_path(root, args.learning_evidence, "Learning evidence")
        ensure_path(root, args.learning_review, "Learning review")
        review_path = (root / args.learning_review).resolve() if not is_external(args.learning_review) else None
        if review_path is not None and (root / "reviews").resolve() not in review_path.parents:
            raise ValueError("Learning review must be inside root reviews directory")

    module_text = readme.read_text(encoding="utf-8")
    module_text = replace_meta(module_text, "当前状态", args.status)
    module_text = replace_meta(module_text, "最近更新", args.date)
    module_text = replace_meta(module_text, "最新审查结论", args.audit_result)
    module_text = replace_meta(module_text, "最新审查报告", link_for_module(root, module_dir, args.audit_report))
    module_text = replace_meta(module_text, "学习证据", link_for_module(root, module_dir, args.learning_evidence))
    module_text = replace_meta(module_text, "学习 Review", link_for_module(root, module_dir, args.learning_review))
    if args.audit_type and args.audit_report != "-":
        audit_row = "| " + " | ".join(
            escape_cell(value)
            for value in (
                args.date,
                args.audit_type,
                args.audit_result,
                link_for_module(root, module_dir, args.audit_report),
            )
        ) + " |"
        module_text = append_audit_row(module_text, args.audit_report, audit_row)

    progress_text = progress.read_text(encoding="utf-8")
    row = "| " + " | ".join(
        escape_cell(value)
        for value in (
            args.module_id,
            args.module_title,
            args.status,
            args.audit_result,
            link_for_root(args.audit_report),
            link_for_root(args.learning_evidence),
            link_for_root(args.learning_review),
            args.next_step,
        )
    ) + " |"
    progress_text = upsert_module_row(progress_text, args.module_id, row)

    original_module = readme.read_text(encoding="utf-8")
    atomic_write(readme, module_text)
    try:
        atomic_write(progress, progress_text)
    except Exception:
        atomic_write(readme, original_module)
        raise

    print(json.dumps({
        "module": args.module_id,
        "status": args.status,
        "module_readme": readme.as_posix(),
        "progress": progress.as_posix(),
        "audit_report": args.audit_report,
        "learning_review": args.learning_review,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
