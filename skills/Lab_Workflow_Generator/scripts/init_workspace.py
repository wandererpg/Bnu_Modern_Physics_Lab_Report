#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bootstrap a *lean* lab workspace: one folder per experiment, nothing else.

Visible layout (deliberately minimal — users only ever touch these):

    <workspace>/
      <实验标题>/                # 讲义内部标题
        <实验标题>.pdf           # 讲义
        data/                    # ← 把实验数据丢这里（CSV/Excel/图片/txt）
        preview_report/          # 预习报告（纯内容）
        lab_report/              # 实验报告（thuemp.cls 等随脚手架带入）

Working sub-directories (figures/ scripts/ tables/ build/) are created later by
`run_lab_workflow.py` when generation actually starts.

Usage:
  python init_workspace.py --workspace D:\lab_work --lectures D:\lectures
  python init_workspace.py --workspace D:\lab_work --experiments "塞曼效应,液晶物性"
  python init_workspace.py --workspace D:\lab_work --lectures . --title-map titles.json

`titles.json` maps a lecture file name to its true title, for scans that carry no
text layer (e.g. {"unpub_1234.pdf": "干涉滤光片的镀制"}).
Idempotent: existing files are kept unless --force.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHIP = HERE.parent / "assets"

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(errors="replace")
    except Exception:
        pass


def raw_first_lines(pdf: Path, pages: str) -> list:
    try:
        out = subprocess.run(
            ["pdftotext", "-f", "1", "-l", pages, "-layout", str(pdf), "-"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90,
        )
        if out.returncode == 0 and out.stdout:
            return out.stdout.splitlines()
    except Exception:
        pass
    return []


def plausible(line: str) -> bool:
    t = line.strip()
    if len(t) < 2 or len(t) > 40:
        return False
    if t.isdigit():
        return False
    if t.startswith("<<<") or t.lower().startswith("page "):
        return False
    # require at least a few CJK chars or letters
    cjk = sum(1 for c in t if "\u4e00" <= c <= "\u9fff")
    return cjk >= 2 or sum(1 for c in t if c.isalpha()) >= 4


def lecture_title(pdf: Path):
    """(title, confident). Falls back to the file stem when there is no text layer."""
    for pages in ("1", "3"):
        for line in raw_first_lines(pdf, pages):
            if plausible(line):
                return line.strip(), True
    return pdf.stem, False


def safe_title(t: str) -> str:
    bad = '<>:"/\\|?*'
    t = "".join(" " if c in bad else c for c in t).strip()
    return t or "实验"


def ship_files(exp: Path) -> None:
    lab = exp / "lab_report"
    lab.mkdir(parents=True, exist_ok=True)
    exp.joinpath("data").mkdir(parents=True, exist_ok=True)
    exp.joinpath("preview_report").mkdir(parents=True, exist_ok=True)
    pairs = [
        (SHIP / "thu_template" / "thuemp.cls", lab / "thuemp.cls"),
        (SHIP / "scaffold_template" / "report_frontmatter_thu.tex", lab / "report_frontmatter_thu.tex"),
        (SHIP / "scaffold_template" / "report_preamble.tex", lab / "report_preamble.tex"),
        (SHIP / "scaffold_template" / "data_README.md", exp / "data" / "README.md"),
    ]
    for src, dst in pairs:
        try:
            if src.exists() and not dst.exists():
                shutil.copyfile(src, dst)
        except OSError as exc:
            print("  [warn] cannot ship %s: %s" % (src.name, exc))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--lectures", help="folder of lecture PDFs (batch mode)")
    ap.add_argument("--experiments", help="comma-separated experiment folder names")
    ap.add_argument("--title-map", help="JSON {lecture_filename: title} for scanned lectures")
    ap.add_argument("--force", action="store_true", help="overwrite an existing lecture PDF")
    a = ap.parse_args()

    ws = Path(a.workspace).resolve()
    ws.mkdir(parents=True, exist_ok=True)

    tmap = {}
    if a.title_map and Path(a.title_map).exists():
        tmap = json.loads(Path(a.title_map).read_text(encoding="utf-8"))

    jobs = []          # (title, lecture pdf or None, confident)
    if a.lectures:
        for pdf in sorted(Path(a.lectures).resolve().glob("*.pdf")):
            if pdf.name in tmap:
                jobs.append((safe_title(tmap[pdf.name]), pdf, True))
            else:
                title, ok = lecture_title(pdf)
                jobs.append((safe_title(title), pdf, ok))
    if a.experiments:
        for name in [s.strip() for s in a.experiments.split(",") if s.strip()]:
            jobs.append((safe_title(name), None, True))
    if not jobs:
        print("[init] nothing to do: pass --lectures and/or --experiments")
        return 2

    scans = []
    for title, pdf, ok in jobs:
        exp = ws / title
        ship_files(exp)
        if pdf is not None:
            dst = exp / (title + ".pdf")
            if dst.exists() and not a.force:
                st = "kept"
            else:
                shutil.copyfile(pdf, dst)
                st = "copied"
            print("[init] %-30s lecture(%s) <- %s" % (title, st, pdf.name))
            if not ok:
                scans.append((title, pdf.name))
        else:
            print("[init] %-30s (lecture not supplied; 把讲义放进该文件夹)" % title)

    print("\n[init] workspace: %s" % ws)
    for d in sorted(p.name for p in ws.iterdir() if p.is_dir()):
        print("  %s/" % d)
    if scans:
        print("\n[init] ⚠ 以下讲义无文本层（扫描件），文件夹名退化为文件名，请核对/重命名：")
        for t, f in scans:
            print("  %s   <- %s" % (t, f))
        print("  可用 --title-map 指定正确标题，例如 {\"%s\": \"干涉滤光片的镀制\"}" % scans[0][1])
    print("\n[init] 下一步：把数据放进 <实验>/data/，然后在该实验文件夹下运行：")
    print("  <python> <skill>/scripts/run_lab_workflow.py --workspace . --stage all")
    return 0


if __name__ == "__main__":
    sys.exit(main())
