#!/usr/bin/env python3
"""Validate Study Anything structure, module audit gates, and learning traceability."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from validate_module_review import validate_modules


TASK_START = "<!-- TASKS_START -->"
TASK_END = "<!-- TASKS_END -->"
MODULES_START = "<!-- MODULES_START -->"
MODULES_END = "<!-- MODULES_END -->"
COMPLETED = {"已完成", "完成", "completed", "done"}
REQUIRED = (
    "README.md",
    "使用文档.md",
    "学习进度表.md",
    "调研/领域调研.md",
    "调研/资料来源.md",
    "环境/README.md",
    "环境/验证.md",
    "reviews",
    "modules",
    "capstone/README.md",
    ".gitignore",
)


def cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def links(cell: str) -> list[str]:
    return re.findall(r"\]\((?:<)?([^)>]+)(?:>)?\)", cell)


def local_target(root: Path, target: str) -> Path | None:
    if target.startswith(("http://", "https://")):
        return None
    return root / target.replace("\\", "/")


def module_table_states(text: str) -> dict[str, str]:
    start = text.find(MODULES_START)
    end = text.find(MODULES_END)
    if start < 0 or end < 0 or end <= start:
        return {}
    result: dict[str, str] = {}
    for line in text[start:end].splitlines():
        row = cells(line) if line.lstrip().startswith("|") else []
        if len(row) == 8 and row[0] not in {"模块 ID", "---"}:
            result[row[0]] = row[2]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked_tasks = 0

    for relative in REQUIRED:
        if not (root / relative).exists():
            errors.append(f"Missing required path: {relative}")

    if (root / "roadmap").exists():
        warnings.append("Legacy roadmap directory exists; Study Anything does not create or use it")

    progress_path = root / "学习进度表.md"
    progress_text = progress_path.read_text(encoding="utf-8") if progress_path.exists() else ""
    if progress_text:
        start = progress_text.find(TASK_START)
        end = progress_text.find(TASK_END)
        if start < 0 or end < 0 or end <= start:
            errors.append("Progress table is missing TASKS markers")
        else:
            for line in progress_text[start:end].splitlines():
                row = cells(line) if line.lstrip().startswith("|") else []
                if len(row) != 7 or row[0] in {"任务 ID", "---"}:
                    continue
                checked_tasks += 1
                task_id, _, _, evidence_cell, review_cell, status, _ = row
                evidence_links = links(evidence_cell)
                review_links = links(review_cell)
                if not review_links:
                    errors.append(f"{task_id}: missing learning-review link")
                for target in review_links:
                    path = local_target(root, target)
                    if path is not None:
                        if not path.exists():
                            errors.append(f"{task_id}: learning review does not exist: {target}")
                        elif (root / "reviews").resolve() not in path.resolve().parents:
                            errors.append(f"{task_id}: learning review is outside root reviews directory: {target}")
                if status.lower() in COMPLETED:
                    if not evidence_links:
                        errors.append(f"{task_id}: completed task has no evidence link")
                    for target in evidence_links:
                        path = local_target(root, target)
                        if path is not None and not path.exists():
                            errors.append(f"{task_id}: evidence does not exist: {target}")

    module_errors, module_warnings, modules = validate_modules(root)
    errors.extend(module_errors)
    warnings.extend(module_warnings)
    table_states = module_table_states(progress_text)
    for module in modules:
        module_id = module["id"]
        if module_id not in table_states:
            errors.append(f"{module_id}: missing from global module-status table")
        elif table_states[module_id] != module["status"]:
            errors.append(f"{module_id}: module README state {module['status']} disagrees with progress state {table_states[module_id]}")

    result = {
        "root": root.as_posix(),
        "valid": not errors,
        "checked_tasks": checked_tasks,
        "checked_modules": len(modules),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
