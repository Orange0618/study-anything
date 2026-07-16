#!/usr/bin/env python3
"""Create a portable Study Anything workbench without overwriting user files."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SKILL_ROOT / "assets"


def render(template_name: str, **values: str) -> str:
    text = (ASSETS / template_name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def write_if_missing(path: Path, content: str, created: list[str], skipped: list[str]) -> None:
    if path.exists():
        skipped.append(path.as_posix())
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    created.append(path.as_posix())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Workbench directory")
    parser.add_argument("--title", required=True, help="Human-readable learning topic")
    parser.add_argument(
        "--profile",
        choices=("general", "python", "cpp", "hardware", "product", "research"),
        default="general",
        help="Adds only a small ecosystem-specific starter file",
    )
    parser.add_argument("--date", default=dt.date.today().isoformat())
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    skipped: list[str] = []

    for directory in ("调研", "环境", "modules", "reviews", "capstone"):
        (root / directory).mkdir(parents=True, exist_ok=True)

    common = {"TITLE": args.title, "DATE": args.date}
    files = {
        "README.md": render("README.template.md", **common),
        "使用文档.md": render("USAGE_GUIDE.template.md", **common),
        "学习进度表.md": render("PROGRESS.template.md", **common),
        "调研/领域调研.md": render("RESEARCH.template.md", **common),
        "调研/资料来源.md": render("SOURCES.template.md", **common),
        "环境/README.md": render("ENVIRONMENT.template.md", **common),
        "环境/验证.md": render("VERIFY.template.md", **common),
        "capstone/README.md": render("CAPSTONE.template.md", **common),
        ".gitignore": (ASSETS / "GITIGNORE.template").read_text(encoding="utf-8"),
    }
    if args.profile == "python":
        files["requirements.txt"] = "# Pin direct dependencies after environment research.\n"
    elif args.profile == "cpp":
        files["环境/CMake说明.md"] = "# CMake 与编译环境\n\n记录编译器、CMake 版本、构建和验证命令。\n"
    elif args.profile == "hardware":
        files["环境/设备与材料.md"] = "# 设备与材料\n\n记录型号、版本、连接方式、仪器和安全限制。\n"
    elif args.profile == "product":
        files["环境/工具与数据.md"] = "# 工具与数据\n\n记录原型工具、研究样本、指标口径和访问限制。\n"
    elif args.profile == "research":
        files["调研/检索方法.md"] = "# 检索方法\n\n记录数据库、检索式、日期和纳入排除标准。\n"

    for relative, content in files.items():
        write_if_missing(root / relative, content, created, skipped)

    result = {
        "root": root.as_posix(),
        "profile": args.profile,
        "created": created,
        "skipped_existing": skipped,
        "roadmap_created": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
