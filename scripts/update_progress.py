#!/usr/bin/env python3
"""Create an event review and update the Study Anything progress table together."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import tempfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REVIEW_TEMPLATE = SKILL_ROOT / "assets" / "LEARNING_REVIEW.template.md"
TASK_START = "<!-- TASKS_START -->"
TASK_END = "<!-- TASKS_END -->"
REVIEW_START = "<!-- REVIEWS_START -->"
REVIEW_END = "<!-- REVIEWS_END -->"
COMPLETED = {"已完成", "完成", "completed", "done"}


def slugify(value: str) -> str:
    value = re.sub(r"[^\w\-\u4e00-\u9fff]+", "-", value, flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-_")
    return (value or "进度更新")[:48]


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>").strip()


def split_refs(values: list[str]) -> list[str]:
    refs: list[str] = []
    for value in values:
        refs.extend(item.strip() for item in value.split(";") if item.strip())
    return refs


def is_external(value: str) -> bool:
    return value.startswith(("http://", "https://"))


def link_for(value: str) -> str:
    if re.fullmatch(r"\[[^]]+\]\([^)]+\)", value):
        return value
    if is_external(value):
        return f"[来源]({value})"
    normalized = value.replace("\\", "/")
    label = Path(normalized).name or normalized
    target = f"<{normalized}>" if " " in normalized else normalized
    return f"[{label}]({target})"


def ensure_evidence(root: Path, refs: list[str], status: str) -> None:
    if status.lower() not in COMPLETED:
        return
    if not refs:
        raise ValueError("A completed task requires at least one evidence path or URL.")
    missing = [ref for ref in refs if not is_external(ref) and not (root / ref).exists()]
    if missing:
        raise FileNotFoundError("Missing evidence: " + ", ".join(missing))


def replace_status_line(text: str, label: str, value: str | None) -> str:
    if value is None:
        return text
    pattern = rf"(?m)^- {re.escape(label)}：.*$"
    replacement = f"- {label}：{value}"
    return re.sub(pattern, replacement, text, count=1) if re.search(pattern, text) else text


def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def upsert_task(text: str, task_id: str, row: str) -> tuple[str, str]:
    start = text.find(TASK_START)
    end = text.find(TASK_END)
    if start < 0 or end < 0 or end <= start:
        raise ValueError("Progress table is missing TASKS markers.")
    block = text[start:end]
    before_status = "未记录"
    lines = block.splitlines()
    found = False
    for index, line in enumerate(lines):
        cells = table_cells(line) if line.lstrip().startswith("|") else []
        if cells and cells[0] == task_id:
            if len(cells) >= 6:
                before_status = cells[5]
            lines[index] = row
            found = True
            break
    if not found:
        lines.append(row)
    new_block = "\n".join(lines) + "\n"
    return text[:start] + new_block + text[end:], before_status


def append_review_index(text: str, row: str) -> str:
    start = text.find(REVIEW_START)
    end = text.find(REVIEW_END)
    if start < 0 or end < 0 or end <= start:
        raise ValueError("Progress table is missing REVIEWS markers.")
    insertion = end
    prefix = text[:insertion]
    if not prefix.endswith("\n"):
        prefix += "\n"
    return prefix + row + "\n" + text[insertion:]


def unique_review_path(root: Path, date: str, title: str) -> Path:
    base = root / "reviews" / f"{date}_{slugify(title)}.md"
    if not base.exists():
        return base
    counter = 2
    while True:
        candidate = base.with_name(f"{base.stem}_{counter}.md")
        if not candidate.exists():
            return candidate
        counter += 1


def render_review(args: argparse.Namespace, before_status: str, refs: list[str]) -> str:
    text = REVIEW_TEMPLATE.read_text(encoding="utf-8")
    evidence = "\n".join(f"- {link_for(ref)}" for ref in refs) if refs else "- 暂无独立证据；本次状态不能标记为完成。"
    values = {
        "REVIEW_TITLE": args.review_title,
        "DATE": args.date,
        "TRIGGER": args.trigger,
        "GOAL_ID": args.goal_id,
        "TASK_ID": args.task_id,
        "BEFORE_STATUS": before_status,
        "SUMMARY": args.summary,
        "EVIDENCE": evidence,
        "ACCEPTANCE_RESULT": args.acceptance_result,
        "PROBLEMS": args.problems,
        "INSIGHTS": args.insights,
        "ADJUSTMENTS": args.adjustments,
        "NEXT_STEP": args.next_step,
    }
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--task-title", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--acceptance", required=True)
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--review-title", required=True)
    parser.add_argument("--trigger", default="进度更新")
    parser.add_argument("--goal-id", default="-")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--acceptance-result", required=True)
    parser.add_argument("--problems", default="无")
    parser.add_argument("--insights", default="待补充")
    parser.add_argument("--adjustments", default="无")
    parser.add_argument("--next-step", required=True)
    parser.add_argument("--current-stage")
    parser.add_argument("--current-task")
    parser.add_argument("--blocker")
    parser.add_argument("--date", default=dt.date.today().isoformat())
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    progress_path = root / "学习进度表.md"
    if not progress_path.exists():
        raise FileNotFoundError(progress_path)

    refs = split_refs(args.evidence)
    ensure_evidence(root, refs, args.status)
    review_path = unique_review_path(root, args.date, args.review_title)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_rel = review_path.relative_to(root).as_posix()

    original = progress_path.read_text(encoding="utf-8")
    evidence_cell = "<br>".join(link_for(ref) for ref in refs) if refs else "-"
    review_cell = link_for(review_rel)
    task_row = "| " + " | ".join(
        escape_cell(value)
        for value in (
            args.task_id,
            args.task_title,
            args.acceptance,
            evidence_cell,
            review_cell,
            args.status,
            args.next_step,
        )
    ) + " |"
    updated, before_status = upsert_task(original, args.task_id, task_row)
    review_row = "| " + " | ".join(
        escape_cell(value)
        for value in (args.date, args.review_title, args.task_id, review_cell, args.acceptance_result)
    ) + " |"
    updated = append_review_index(updated, review_row)
    updated = replace_status_line(updated, "当前阶段", args.current_stage)
    updated = replace_status_line(updated, "当前主任务", args.current_task or args.next_step)
    updated = replace_status_line(updated, "最近进展", args.summary)
    updated = replace_status_line(updated, "当前阻塞", args.blocker)
    updated = replace_status_line(updated, "下一步", args.next_step)

    review_text = render_review(args, before_status, refs)
    fd, temp_name = tempfile.mkstemp(prefix="study-progress-", suffix=".md", dir=root)
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        temp_path.write_text(updated, encoding="utf-8", newline="\n")
        review_path.write_text(review_text, encoding="utf-8", newline="\n")
        os.replace(temp_path, progress_path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        review_path.unlink(missing_ok=True)
        raise

    print(json.dumps({
        "progress": progress_path.as_posix(),
        "review": review_path.as_posix(),
        "task_id": args.task_id,
        "old_status": before_status,
        "new_status": args.status,
        "evidence": refs,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
