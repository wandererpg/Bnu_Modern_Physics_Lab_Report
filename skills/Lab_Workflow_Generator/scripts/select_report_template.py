#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Install or select a report layout without generating experimental content.

Examples:
  python select_report_template.py --list-templates
  python select_report_template.py --workspace . --experiment "实验标题" --template minimal
  python select_report_template.py --workspace "实验标题" --template minimal

The generated lab_report.tex is managed by a recorded SHA-256. User-edited or
legacy master files require an explicit AI migration; this script never replaces
them. The current minimal template keeps information and body in a single source.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
TEMPLATE_ASSETS = ASSETS / "report_templates"
SELECTION_FILE = "template_selection.json"


class TemplateSelectionError(ValueError):
    """An invalid selection or an unsafe overwrite was requested."""


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise TemplateSelectionError(f"无法读取模板记录 {path}: {exc}") from exc


def load_registry(asset_root: Path | None = None) -> dict:
    root = Path(asset_root) if asset_root is not None else TEMPLATE_ASSETS
    registry = _read_json(root / "registry.json")
    if not isinstance(registry, dict) or not isinstance(registry.get("templates"), list):
        raise TemplateSelectionError("registry.json 必须包含 templates 列表和 default 编号。")
    entries = registry["templates"]
    identifiers = set()
    for entry in entries:
        if not isinstance(entry, dict) or not all(entry.get(k) for k in ("id", "name", "source")):
            raise TemplateSelectionError("模板目录中的每个条目必须有 id、name 和 source。")
        if entry["id"] in identifiers:
            raise TemplateSelectionError(f"模板编号重复：{entry['id']}")
        identifiers.add(entry["id"])
        source = (root / entry["source"]).resolve()
        if not source.is_relative_to(root.resolve()):
            raise TemplateSelectionError(f"模板源文件必须位于模板资产目录内：{entry['source']}")
    if registry.get("default") not in identifiers:
        raise TemplateSelectionError("registry.json 的 default 不是有效模板编号。")
    return registry


def resolve_template(registry: dict, requested: str | None = None) -> dict:
    key = str(requested if requested is not None else registry["default"]).strip().casefold()
    if key.isdigit():
        key = key.zfill(2)
    matches = []
    for entry in registry["templates"]:
        names = [entry["id"], entry["name"], *entry.get("aliases", [])]
        if key in {str(value).strip().casefold() for value in names}:
            matches.append(entry)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise TemplateSelectionError(f"模板名称有歧义：{requested}")
    options = "；".join(f"{entry['id']} {entry['name']}" for entry in registry["templates"])
    raise TemplateSelectionError(f"未知模板 {requested!r}。可选：{options}")


def list_templates(asset_root: Path | None = None) -> None:
    registry = load_registry(asset_root)
    for entry in registry["templates"]:
        default = "（默认）" if entry["id"] == registry["default"] else ""
        aliases = "、".join(entry.get("aliases", []))
        print(f"{entry['id']}  {entry['name']}{default}" + (f"；别名：{aliases}" if aliases else ""))
        print(f"    {entry.get('description', '')}")


def read_selection(lab_dir: Path) -> dict | None:
    path = Path(lab_dir) / SELECTION_FILE
    if not path.exists():
        return None
    selection = _read_json(path)
    if not isinstance(selection, dict) or not selection.get("id"):
        raise TemplateSelectionError(f"模板记录缺少 id：{path}")
    return selection


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def _atomic_write(path: Path, text: str) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, prefix=".report-template-",
                                         suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def install_report_template(lab_dir: Path, template: str | None = None,
                            experiment_title: str | None = None,
                            allow_legacy: bool = False,
                            asset_root: Path | None = None) -> dict | None:
    """Install the current single-source template without replacing real reports.

    Legacy records and user-edited masters are preserved by normal runner calls.
    Moving an existing report to the current template requires content migration.
    """
    lab = Path(lab_dir).resolve()
    master = lab / "lab_report.tex"
    selection = read_selection(lab)
    tracked_hash = selection.get("installed_master_sha256") if selection else None
    existing_hash = sha256(master) if master.exists() else None
    root = Path(asset_root) if asset_root is not None else TEMPLATE_ASSETS
    registry = load_registry(root)
    current_ids = {entry["id"] for entry in registry["templates"]}
    legacy = selection is not None and selection["id"] not in current_ids
    edited = existing_hash is not None and (not tracked_hash or existing_hash != tracked_hash)
    if existing_hash is not None and (legacy or edited):
        reason = "旧模板报告" if legacy else "既有或手动修改的报告"
        if allow_legacy and template is None:
            print(f"[template] 保留{reason}：{master}；迁移到最小模板须先完整保留正文与数据。")
            return selection
        raise TemplateSelectionError(
            f"拒绝以空骨架覆盖{reason}：{master}。请先由 AI 审查并迁移正文、信息、文献和数据。"
        )
    if legacy:
        raise TemplateSelectionError(
            f"旧模板记录 {selection['id']} 的主文件缺失：{master}。请先恢复报告或显式完成内容迁移。"
        )
    entry = resolve_template(registry, template if template is not None else
                             (selection["id"] if selection else None))
    source = root / entry["source"]
    if not source.is_file():
        raise TemplateSelectionError(f"模板资产缺失：{source}")
    master_text = source.read_text(encoding="utf-8-sig")
    if experiment_title:
        master_text = re.sub(
            r"\\newcommand\{\\ReportTitle\}\{实验题目\}",
            lambda _: r"\newcommand{\ReportTitle}{" + _tex_escape(experiment_title) + "}",
            master_text, count=1,
        )
    # Validate selection, assets and overwrite safety before filesystem changes.
    lab.mkdir(parents=True, exist_ok=True)
    for directory in ("data", "figures", "scripts", "tables", "build"):
        (lab / directory).mkdir(parents=True, exist_ok=True)
    logo_source = ASSETS / "branding" / "bnu_logo.png"
    logo = lab / "assets" / "bnu_logo.png"
    if logo_source.is_file() and not logo.exists():
        logo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(logo_source, logo)
    if master.exists() and sha256(master) != existing_hash:
        raise TemplateSelectionError(f"报告在安装期间发生修改，已停止主文件替换：{master}")
    _atomic_write(master, master_text)
    record = {
        "schema_version": 2, "id": entry["id"], "name": entry["name"],
        "source": entry["source"], "installed_master_sha256": sha256(master),
        "columns": entry.get("columns", 1), "layout": entry.get("layout", "single-column"),
        "layout_version": entry.get("layout_version", registry.get("version", 1)),
    }
    _atomic_write(lab / SELECTION_FILE, json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(f"[template] {entry['id']} {entry['name']} -> {master}")
    return record


def find_lab_dir(workspace: Path, experiment: str | None = None) -> Path:
    ws = Path(workspace).resolve()
    if ws.name == "lab_report" and experiment is None:
        return ws
    if experiment:
        if ws.name == experiment and (ws / "lab_report").is_dir():
            return ws / "lab_report"
        root = ws / experiment
        legacy = ws / "experiments" / experiment
        if not root.exists() and legacy.is_dir():
            root = legacy
        return root / "lab_report"
    return ws / "lab_report"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".", help="实验目录；配合 --experiment 可传工作区根目录")
    parser.add_argument("--experiment", help="工作区根目录下的实验名称")
    parser.add_argument("--template", help="minimal 或注册别名；新报告默认 minimal，既有报告须保留内容后迁移")
    parser.add_argument("--list-templates", action="store_true", help="列出模板编号、名称和别名后退出")
    args = parser.parse_args()
    try:
        if args.list_templates:
            list_templates()
            return 0
        lab = find_lab_dir(Path(args.workspace), args.experiment)
        install_report_template(lab, args.template, args.experiment or lab.parent.name)
        return 0
    except (TemplateSelectionError, OSError) as exc:
        print(f"[template] ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
