#!/usr/bin/env python3
"""Validate module README state, audit placement, and learning completion links."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_AUDIT = {"可学习", "学习中", "已学习"}
META_FIELDS = ("模块 ID", "关联目标", "当前状态", "最近更新", "模块目标", "前置模块", "最新审查结论", "最新审查报告", "学习证据", "学习 Review")


def meta_value(text: str, label: str) -> str | None:
    match = re.search(rf"(?m)^- {re.escape(label)}：(.+)$", text)
    return match.group(1).strip() if match else None


def link_targets(value: str) -> list[str]:
    return re.findall(r"\]\((?:<)?([^)>]+)(?:>)?\)", value)


def resolve_from(base: Path, target: str) -> Path | None:
    if target.startswith(("http://", "https://")):
        return None
    return (base / target.replace("\\", "/")).resolve()


def validate_modules(root: Path) -> tuple[list[str], list[str], list[dict[str, str]]]:
    errors: list[str] = []
    warnings: list[str] = []
    modules: list[dict[str, str]] = []
    modules_root = root / "modules"
    if not modules_root.exists():
        return ["Missing modules directory"], warnings, modules

    for module_dir in sorted(path for path in modules_root.iterdir() if path.is_dir()):
        readme = module_dir / "README.md"
        audit_dir = module_dir / "审查"
        if not readme.exists():
            errors.append(f"{module_dir.name}: missing README.md")
            continue
        if not audit_dir.exists():
            errors.append(f"{module_dir.name}: missing 审查 directory")

        text = readme.read_text(encoding="utf-8")
        meta = {field: meta_value(text, field) for field in META_FIELDS}
        for field, value in meta.items():
            if value is None:
                errors.append(f"{module_dir.name}: missing metadata field {field}")

        module_id = meta.get("模块 ID") or module_dir.name
        status = meta.get("当前状态") or "未知"
        audit_result = meta.get("最新审查结论") or "-"
        audit_value = meta.get("最新审查报告") or "-"
        evidence_value = meta.get("学习证据") or "-"
        review_value = meta.get("学习 Review") or "-"

        if status in REQUIRED_AUDIT:
            if audit_result not in {"通过", "修改后通过"}:
                errors.append(f"{module_id}: state {status} requires a passing audit conclusion")
            audit_links = link_targets(audit_value)
            if not audit_links:
                errors.append(f"{module_id}: state {status} requires an audit-report link")
            for target in audit_links:
                path = resolve_from(module_dir, target)
                if path is not None:
                    if not path.exists():
                        errors.append(f"{module_id}: audit report does not exist: {target}")
                    elif audit_dir.resolve() not in path.parents:
                        errors.append(f"{module_id}: audit report is outside module 审查 directory: {target}")

        if status == "已学习":
            evidence_links = link_targets(evidence_value)
            review_links = link_targets(review_value)
            if not evidence_links:
                errors.append(f"{module_id}: learned module has no evidence link")
            if not review_links:
                errors.append(f"{module_id}: learned module has no learning-review link")
            for target in evidence_links:
                path = resolve_from(module_dir, target)
                if path is not None and not path.exists():
                    errors.append(f"{module_id}: learning evidence does not exist: {target}")
            for target in review_links:
                path = resolve_from(module_dir, target)
                if path is not None:
                    if not path.exists():
                        errors.append(f"{module_id}: learning review does not exist: {target}")
                    elif (root / "reviews").resolve() not in path.parents:
                        errors.append(f"{module_id}: learning review is outside root reviews directory: {target}")

        modules.append({
            "id": module_id,
            "name": module_dir.name,
            "status": status,
            "audit_result": audit_result,
        })

    return errors, warnings, modules


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    errors, warnings, modules = validate_modules(root)
    result = {"root": root.as_posix(), "valid": not errors, "modules": modules, "errors": errors, "warnings": warnings}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
