#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Install or select a report layout without generating experimental content.

Examples:
  python select_report_template.py --list-templates
  python select_report_template.py --workspace . --experiment "实验标题" --template 03
  python select_report_template.py --workspace "实验标题" --template nature

The generated lab_report.tex is managed by a recorded SHA-256. User-edited or
legacy master files require an explicit AI migration; this script never replaces
them. Body, metadata, bibliography and common layout files are copied only once.
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
COMMON_FILES = ("common.tex", "layout_v2.tex", "layout_06_he_ne.tex", "metadata.tex", "body.tex", "references.bib")


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
    """Deploy a selected master while preserving all user content.

    Explicit selection wins over template_selection.json, then registry default.
    With allow_legacy and no explicit selection, existing untracked or edited
    masters remain untouched so older runner invocations can still compile them.
    """
    lab = Path(lab_dir).resolve()
    master = lab / "lab_report.tex"
    selection = read_selection(lab)
    tracked_hash = selection.get("installed_master_sha256") if selection else None
    existing_hash = sha256(master) if master.exists() else None
    untracked = existing_hash is not None and not tracked_hash
    edited = existing_hash is not None and tracked_hash and existing_hash != tracked_hash
    if untracked or edited:
        reason = "既存的非托管 LaTeX 主文件" if untracked else "用户已修改的 LaTeX 主文件"
        if allow_legacy and template is None:
            print(f"[template] 保留{reason}：{master}；如需换版式，请先由 AI 迁移正文。")
            return selection
        raise TemplateSelectionError(
            f"拒绝覆盖{reason}：{master}。请让 AI 先审查并迁移该报告，"
            "保留现有正文、数据和元信息后再选择模板。"
        )

    root = Path(asset_root) if asset_root is not None else TEMPLATE_ASSETS
    registry = load_registry(root)
    entry = resolve_template(registry, template if template is not None else
                             (selection["id"] if selection else None))
    source = root / entry["source"]
    required = [source, *(root / name for name in COMMON_FILES),
                ASSETS / "branding" / "bnu_logo.png"]
    if entry["id"] == "01":
        required.append(ASSETS / "thu_template" / "thuemp.cls")
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise TemplateSelectionError("模板资产缺失：" + "；".join(missing))
    master_text = source.read_text(encoding="utf-8-sig")
    metadata_text = (root / "metadata.tex").read_text(encoding="utf-8-sig")
    if experiment_title:
        metadata_text = re.sub(
            r"\\newcommand\{\\ReportTitle\}\{实验题目\}",
            lambda _: r"\newcommand{\ReportTitle}{" + _tex_escape(experiment_title) + "}",
            metadata_text, count=1,
        )

    # All asset and overwrite checks precede filesystem changes.
    lab.mkdir(parents=True, exist_ok=True)
    for directory in ("data", "figures", "scripts", "tables", "build"):
        (lab / directory).mkdir(parents=True, exist_ok=True)
    content = lab / "report_template"
    content.mkdir(parents=True, exist_ok=True)
    for name in COMMON_FILES:
        target = content / name
        if not target.exists():
            if name == "metadata.tex":
                _atomic_write(target, metadata_text)
            else:
                shutil.copyfile(root / name, target)
    branding = lab / "assets"
    branding.mkdir(parents=True, exist_ok=True)
    logo = branding / "bnu_logo.png"
    if not logo.exists():
        shutil.copyfile(ASSETS / "branding" / "bnu_logo.png", logo)
    if entry["id"] == "01" and not (lab / "thuemp.cls").exists():
        shutil.copyfile(ASSETS / "thu_template" / "thuemp.cls", lab / "thuemp.cls")
    # Check again immediately before replacing the managed master.
    if master.exists() and sha256(master) != existing_hash:
        raise TemplateSelectionError(f"报告在安装期间发生修改，已停止主文件替换：{master}")
    _atomic_write(master, master_text)
    record = {
        "schema_version": 1,
        "id": entry["id"], "name": entry["name"], "source": entry["source"],
        "installed_master_sha256": sha256(master),
    }
    if "columns" in entry:
        record["columns"] = entry["columns"]
    record["layout"] = entry.get("layout", "two-column")
    record["layout_version"] = entry.get("layout_version", registry.get("version", 1))
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
    parser.add_argument("--template", help="模板编号 01–06 或注册别名；省略时沿用记录，否则使用默认 01")
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
