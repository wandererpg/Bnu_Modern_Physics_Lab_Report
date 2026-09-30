#!/usr/bin/env python3
"""Export a portable, allowlisted report bundle; retain edited copies on conflict."""

import hashlib
import json
import shutil
from pathlib import Path


SKILL = Path(__file__).resolve().parent.parent
WORKSPACE = SKILL.parent.parent
BUNDLE = WORKSPACE / "agent_report_bundle"
SKILL_REL = Path("skills/Lab_Workflow_Generator")
DOCS = ("agents.md", "AGENT.md", "README.md", "preview.md", "report.md")
SCRIPTS = (
    "select_report_template.py", "run_lab_workflow.py", "make_data_tables.py",
    "check_report_tex.py", "check_pdf_geometry.py",
    "check_float_distance.py", "check_inline_distance.py",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_link(path):
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def export():
    registry = json.loads((SKILL / "assets/report_templates/registry.json").read_text(
        encoding="utf-8-sig"))
    if {entry["id"] for entry in registry["templates"]} != {
            "01", "02", "03", "04", "05", "06"}:
        raise ValueError("Expected registered templates 01–06")
    files = {Path(name): WORKSPACE / name for name in DOCS}
    files[Path(".gitignore")] = WORKSPACE / ".gitignore"
    files[Path(".gitattributes")] = SKILL / "assets/agent_bundle/.gitattributes"
    files[Path("START_HERE.md")] = SKILL / "assets/agent_bundle/START_HERE.md"
    files[Path("skills/README.md")] = SKILL / "assets/agent_bundle/skills_README.md"
    for name in ("agents.md", "preview.md", "report.md"):
        files[SKILL_REL / "references" / name] = WORKSPACE / name
    for name in SCRIPTS:
        files[SKILL_REL / "scripts" / name] = SKILL / "scripts" / name
    assets = (
        "registry.json", "common.tex", "layout_v2.tex", "layout_06_he_ne.tex",
        "metadata.tex", "body.tex", "references.bib", "README.md",
        "SOURCES.md", "DESIGN_06.md",
        *(entry["source"] for entry in registry["templates"]),
    )
    for name in assets:
        relative = SKILL_REL / "assets/report_templates" / name
        files[relative] = WORKSPACE / relative
    for name in (
        "branding/bnu_logo.png", "thu_template/thuemp.cls", "thu_template/README.md",
        "scaffold_template/data_README.md", "scaffold_template/report_preamble.tex",
        "scaffold_template/report_frontmatter_thu.tex",
    ):
        relative = SKILL_REL / "assets" / name
        files[relative] = WORKSPACE / relative

    # Validate sources and destinations before making any changes.
    for relative, source in files.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        if not relative.is_relative_to(Path(".")) or ".." in relative.parts:
            raise ValueError(f"Unsafe bundle path: {relative}")
        if not source.resolve().is_relative_to(WORKSPACE):
            raise ValueError(f"Source outside workspace: {source}")
        if not (BUNDLE / relative).resolve().is_relative_to(BUNDLE):
            raise ValueError(f"Destination outside bundle: {relative}")
    previous = {}
    manifest_path = BUNDLE / "manifest.json"
    if manifest_path.exists():
        previous = {row["path"]: row["sha256"] for row in json.loads(
            manifest_path.read_text(encoding="utf-8"))["files"]}
    if BUNDLE.exists():
        if is_link(BUNDLE):
            raise ValueError("Bundle directory must not be a link")
        for target in BUNDLE.rglob("*"):
            if is_link(target):
                raise ValueError(f"Bundle contains a link: {target}")
            if not target.is_file() or target == manifest_path:
                continue
            relative = target.relative_to(BUNDLE)
            key = relative.as_posix()
            if relative not in files:
                raise ValueError(f"Unexpected file; preserve or move before export: {target}")
            actual = digest(target)
            if actual != digest(files[relative]) and actual != previous.get(key):
                raise ValueError(f"Edited bundle file; merge before export: {target}")

    records = []
    for relative, source in sorted(files.items(), key=lambda pair: pair[0].as_posix()):
        target = BUNDLE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or digest(target) != digest(source):
            shutil.copyfile(source, target)
        records.append({"path": relative.as_posix(),
                        "source": source.relative_to(WORKSPACE).as_posix(),
                        "bytes": target.stat().st_size, "sha256": digest(target)})
    manifest_path.write_text(json.dumps({
        "schema_version": 1, "templates": [entry["id"] for entry in registry["templates"]],
        "files": records,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {len(records)} files and manifest to {BUNDLE}")


if __name__ == "__main__":
    try:
        export()
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Bundle export stopped: {exc}")
