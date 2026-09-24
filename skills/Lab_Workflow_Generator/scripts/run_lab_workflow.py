#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lab Workflow Generator - deterministic runner.

Roles:
  - scaffold : create the per-experiment directory skeleton
  - status   : print a data/script/tex inventory
  - plots    : run lab_report/scripts/generate_plots.py
  - tables   : render lab_report/data/*.csv into tables/*.tex (width-fitted)
  - check    : static .tex checks (captions, refs, sections, table geometry)
  - compile  : compile preview.tex and lab_report.tex (xelatex x2) and copy PDFs,
               then measure the built PDF for clipping/bleeding/overlaps
  - all      : scaffold -> status -> plots (if script) -> tables -> check -> compile

Text generation (.tex prose) is performed by the Lab_Workflow_Generator Skill
(which delegates writing rules to advanced_lab_report_gen). This script only
handles deterministic steps.

Usage examples:
  python run_lab_workflow.py --experiment 塞曼效应
  python run_lab_workflow.py --experiment 塞曼效应 --stage plots
  python run_lab_workflow.py --experiment 塞曼效应 --stage tables
  python run_lab_workflow.py --experiment 塞曼效应 --stage check
"""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# Console robustness: several messages carry non-GBK glyphs (emoji like the
# guards' ❌/✅), which would crash print() on cp936/GBK Windows consoles.
# Reconfigure stdio so output can never raise UnicodeEncodeError.
def _force_utf8_stdio():
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(errors="replace")
        except Exception:
            pass


_force_utf8_stdio()




def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def experiment_dir(ws: Path, name: str) -> Path:
    """Resolve the experiment directory.

    Three accepted layouts, in order:
      1. in-place : `--workspace` IS the experiment folder (folder name == experiment)
      2. root-level: <ws>/<实验标题>/                      (current convention)
      3. legacy    : <ws>/experiments/<实验标题>/           (still supported)
    """
    if ws.name == name and (ws / "lab_report").is_dir():
        return ws
    root_level = ws / name
    legacy = ws / "experiments" / name
    if root_level.is_dir():
        return root_level
    if legacy.is_dir():
        return legacy
    return root_level


def preview_tex(exp: Path) -> Path | None:
    """Preview report source: upstream name preview_report.tex, legacy preview.tex."""
    for rel in ("preview_report/preview_report.tex", "preview_report/preview.tex"):
        p = exp / rel
        if p.exists():
            return p
    return None


def lab_tex(exp: Path) -> Path | None:
    p = exp / "lab_report" / "lab_report.tex"
    return p if p.exists() else None


def scaffold(ws: Path, name: str) -> Path:
    exp = experiment_dir(ws, name)
    ensure_dir(exp / "preview_report")
    ensure_dir(exp / "lab_report" / "data")
    ensure_dir(exp / "lab_report" / "figures")
    ensure_dir(exp / "lab_report" / "scripts")
    ensure_dir(exp / "lab_report" / "tables")
    ensure_dir(exp / "lab_report" / "build")
    ensure_dir(exp / "lab_report" / "assets")
    for sub in ("preview_report", "lab_report"):
        keep = exp / sub / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")
    # ship the branding logo and the report preamble with every experiment
    ship = Path(__file__).resolve().parent.parent / "assets"
    for src, dst in (
        (ship / "branding" / "bnu_logo.png", exp / "lab_report" / "assets" / "bnu_logo.png"),
        (ship / "scaffold_template" / "report_preamble.tex", exp / "lab_report" / "report_preamble.tex"),
        (ship / "scaffold_template" / "data_README.md", exp / "lab_report" / "data" / "README.md"),
        # default template: THU (thuemp) — the class must sit next to the .tex
        (ship / "thu_template" / "thuemp.cls", exp / "lab_report" / "thuemp.cls"),
        (ship / "scaffold_template" / "report_frontmatter_thu.tex", exp / "lab_report" / "report_frontmatter_thu.tex"),
    ):
        try:
            if src.exists() and not dst.exists():
                shutil.copyfile(src, dst)
        except OSError as exc:
            print(f"[scaffold] warn: cannot copy {src.name}: {exc}")
    stage_data(exp)
    print(f"[scaffold] ensured: {exp}")
    return exp


def stage_data(exp: Path) -> None:
    """Mirror <exp>/data/* into <exp>/lab_report/data/* (the pipeline's input).

    Users drop raw data at the experiment level (<实验>/data/); the plotting
    script and table generator keep reading lab_report/data as before.
    """
    src = exp / "data"
    if not src.is_dir():
        return
    dst = exp / "lab_report" / "data"
    ensure_dir(dst)
    staged = 0
    for p in sorted(src.rglob("*")):
        if not p.is_file() or p.name.startswith("~$"):
            continue
        target = dst / p.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        if (not target.exists()) or target.stat().st_size != p.stat().st_size:
            shutil.copyfile(p, target)
            staged += 1
    if staged:
        print(f"[data ] staged {staged} file(s): {src} -> {dst}")


def run(cmd, cwd: Path, env=None) -> int:
    print(f"[run ] {cmd}  (cwd={cwd})")
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), env=env)
        return proc.returncode
    except FileNotFoundError as exc:
        print(f"[error] command not found: {cmd} ({exc})")
        return 127


def status(exp: Path) -> None:
    print(f"[status] experiment dir: {exp}")
    lecture = list(exp.glob("*.pdf"))
    print("  lecture pdf :", [p.name for p in lecture] or ["MISSING"])
    data = list((exp / "lab_report" / "data").glob("*"))
    data = [p for p in data if p.is_file() and not p.name.startswith("~$")]
    print("  data files  :", [p.name for p in data] or ["(empty)"])
    up = list((exp / "data").glob("*")) if (exp / "data").is_dir() else []
    up = [p.name for p in up if p.is_file() and not p.name.startswith("~$")]
    if up:
        print("  <实验>/data :", up, "(运行时会自动镜像到 lab_report/data)")
    figs = list((exp / "lab_report" / "figures").glob("*"))
    print("  figures     :", len([p for p in figs if p.is_file()]))
    script = exp / "lab_report" / "scripts" / "generate_plots.py"
    print("  plots script:", "present" if script.exists() else "MISSING")
    pt, lt = preview_tex(exp), lab_tex(exp)
    print("  preview report:", pt.relative_to(exp).as_posix() if pt else "MISSING (需先由 Skill 生成正文)")
    print("  lab report    :", lt.relative_to(exp).as_posix() if lt else "MISSING (需先由 Skill 生成正文)")


def plots(exp: Path) -> int:
    stage_data(exp)
    script = exp / "lab_report" / "scripts" / "generate_plots.py"
    if not script.exists():
        print("[plots] no generate_plots.py; skip (先由 Skill 生成数据处理脚本)")
        return 0
    return run([sys.executable, str(script)], exp / "lab_report")


def ensure_lecture_text(exp: Path) -> int:
    """OCR the lecture when it is a scan and no lecture_ocr.txt exists yet."""
    out = exp / "lab_report" / "lecture_ocr.txt"
    if out.exists():
        print("[ocr ] lecture_ocr.txt already present; skip")
        return 0
    pdfs = [p for p in exp.glob("*.pdf") if p.is_file()]
    gen = Path(__file__).resolve().parent / "ocr_lecture.py"
    if not pdfs or not gen.exists():
        return 0
    chars = 0
    try:
        r = subprocess.run(["pdftotext", str(pdfs[0]), "-"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=60)
        chars = len((r.stdout or "").strip())
    except Exception:
        pass
    if chars >= 50:
        print(f"[ocr ] lecture has a text layer ({chars} chars); OCR not needed")
        return 0
    print(f"[ocr ] lecture is a scan ({chars} chars of text) -> running OCR")
    return run([sys.executable, str(gen), "--experiment", str(exp)], exp)


def skill_version():
    """Version declared by this Skill's own SKILL.md (for log cross-checks)."""
    try:
        m = re.search(r"version:\s*([0-9][0-9.]*)",
                      (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8"))
        return m.group(1) if m else None
    except OSError:
        return None


def warn_log_version(exp: Path) -> None:
    """Non-fatal: the generated generation_log should name the current Skill version."""
    log = exp / "lab_report" / "generation_log.md"
    if not log.exists():
        return
    try:
        txt = log.read_text(encoding="utf-8")
    except OSError:
        return
    m = re.search(r"Skill版本：[^\r\n]*?v([0-9][0-9.]*)", txt)
    sv = skill_version()
    if m and sv and m.group(1) != sv:
        print(f"[warn] generation_log 记为 v{m.group(1)}，本 Skill 为 v{sv}；请更新日志中的版本行")


def data_tables(exp: Path) -> int:
    """Render lab_report/data/*.csv into lab_report/tables/*.tex (booktabs).

    Keeps appendix tables reproducible: edit the CSV, rerun, and the LaTeX
    tables follow the data (the upstream workspace hand-copies them instead).
    Column widths are fitted to the text block (see make_data_tables.plan_columns):
    a natural-width tabular never breaks, it just runs off the paper, and LaTeX
    reports only an Overfull hbox for it.
    """
    stage_data(exp)
    gen = Path(__file__).resolve().parent / "make_data_tables.py"
    lab = exp / "lab_report"
    if not gen.exists():
        print("[tables] make_data_tables.py not found next to runner; skip")
        return 0
    if not (lab / "data").is_dir():
        print("[tables] no lab_report/data; skip")
        return 0
    single = has_onecolumn(exp)
    cmd = [sys.executable, str(gen), "--combined"]
    if single:
        cmd.append("--single")
    else:
        # 双栏：半栏紧凑表 + [H] 就地（紧贴正文引用）
        cmd.append("--column")
    if has_array(exp):
        cmd.append("--array")
    cap = lab / "table_captions.json"
    if cap.exists():
        cmd += ["--caption-map", str(cap)]
    hdr = lab / "table_headers.json"
    if hdr.exists():
        cmd += ["--header-map", str(hdr)]
    return run(cmd, lab)


def has_onecolumn(exp: Path) -> bool:
    """True when the report body is single-column (\onecolumn).

    Single column lets tables sit exactly where the text mentions them
    (table[H] + tabular*{\textwidth}), which a twocolumn layout cannot do
    for wide tables: table* can only go to the top of a page.
    """
    for p in (lab_tex(exp), preview_tex(exp)):
        if p is not None and Path(p).exists():
            try:
                if "\\onecolumn" in Path(p).read_text(encoding="utf-8", errors="ignore"):
                    return True
            except OSError:
                pass
    return False


def has_strip(exp: Path) -> bool:
    """True when the document loads the cuted package (strip environment).

    With cuted we emit full-width NON-floating tables (strip + table[H]): the
    table then appears exactly where the text mentions it, instead of drifting
    2-3 pages away as table* floats do in a dense twocolumn layout.
    """
    lab = exp / "lab_report"
    pat = re.compile(r"\\usepackage(\[[^\]]*\])?\{[^}]*\bcuted\b")
    for p in (lab_tex(exp), preview_tex(exp)):
        if p is not None and Path(p).exists():
            try:
                if pat.search(Path(p).read_text(encoding="utf-8", errors="ignore")):
                    return True
            except OSError:
                pass
    return False


def has_array(exp: Path) -> bool:
    """True when the document loads the array package (needed for >{...}p{})
    so generated tables can centre numeric cells and left-align text cells."""
    lab = exp / "lab_report"
    pat = re.compile(r"\\usepackage(\[[^\]]*\])?\{[^}]*\barray\b")
    for p in (lab_tex(exp), preview_tex(exp), lab / "report_preamble.tex",
              lab / "report_frontmatter_thu.tex"):
        if p is not None and Path(p).exists():
            try:
                if pat.search(Path(p).read_text(encoding="utf-8", errors="ignore")):
                    return True
            except OSError:
                pass
    return False


def check_tex(exp: Path) -> int:
    """Static source checks: captions, dangling/orphan refs, required sections."""
    chk = Path(__file__).resolve().parent / "check_report_tex.py"
    if not chk.exists():
        print("[check] check_report_tex.py not found next to runner; skip")
        return 0
    targets = [p for p in (preview_tex(exp), lab_tex(exp)) if p is not None]
    if not targets:
        print("[check] no .tex to check; skip")
        return 0
    rc = 0
    for p in targets:
        code = run([sys.executable, str(chk), str(p)], exp)
        rc = code or rc
    return rc


def pdf_geometry(exp: Path) -> int:
    """Measure the built PDF: clipping, bleeding, overlaps, tiny figure text.

    LaTeX exits 0 while happily typesetting a table 15cm off the paper, so the
    only trustworthy source of truth for layout is the PDF itself.
    """
    chk = Path(__file__).resolve().parent / "check_pdf_geometry.py"
    dist = Path(__file__).resolve().parent / "check_float_distance.py"
    inline = Path(__file__).resolve().parent / "check_inline_distance.py"
    lab = exp / "lab_report"
    pdfs = [p for p in (lab / "lab_report.pdf", lab / "preview_report.pdf") if p.exists()]
    if not pdfs:
        print("[pdf-geo] 尚未生成 PDF；跳过版式检查")
        return 0
    rc = 0
    for p in pdfs:
        if chk.exists():
            code = run([sys.executable, str(chk), str(p)], exp)
            rc = code or rc
        # 浮动体与引用距离（用户反馈"正文与表格相距太远"）：只报告，不参与退出码
        if p.name == "lab_report.pdf":
            if dist.exists():
                run([sys.executable, str(dist), str(p)], exp)
            if inline.exists():
                run([sys.executable, str(inline), str(p)], exp)
    return rc


def needs_bibtex(tex: Path) -> bool:
    """True when the document needs a real BibTeX run.

    Triggers on \bibliography{}/\bibreference (external .bib), or on \cite when a
    .bib file sits next to the .tex. A manual thebibliography environment never
    triggers a BibTeX run.
    """
    try:
        txt = tex.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    # A manual thebibliography never needs a BibTeX run, even if stray .bib
    # files sit next to the document (e.g. a THU/ctexart variant in the same dir).
    if "\\begin{thebibliography}" in txt:
        return False
    if "\\bibliography{" in txt or "\\bibreference" in txt:
        return True
    return "\\cite" in txt and any(tex.parent.glob("*.bib"))


def bibtex_env(tex: Path) -> dict:
    """Let bibtex find the workspace's 物理学报模板* dir (.bst/.bib)."""
    env = os.environ.copy()
    roots = [tex.parent, tex.parent.parent, tex.parent.parent.parent,
             tex.parent.parent.parent.parent]
    tpls = []
    for r in roots:
        if r and r.exists():
            tpls += [p for p in r.glob("*模板*") if p.is_dir()]
    paths = [str(tex.parent)] + [str(p) for p in tpls] + [str(r) for r in roots if r]
    for var in ("BSTINPUTS", "BIBINPUTS", "TEXINPUTS"):
        env[var] = os.pathsep.join(paths) + os.pathsep
    return env


def compile_tex(tex: Path) -> int:
    build = tex.parent / "build"
    ensure_dir(build)
    base = tex.stem
    xelatex = ["xelatex", "-interaction=nonstopmode", "-halt-on-error",
               "-output-directory=build", f"{base}.tex"]
    if needs_bibtex(tex):
        print("[compile] bibliography detected -> xelatex, bibtex, xelatex, xelatex")
        steps = [
            (xelatex, tex.parent, None),
            # bibtex must run where ./refs resolves (the .tex dir); the aux lives in build/
            (["bibtex", f"build/{base}"], tex.parent, bibtex_env(tex)),
            (xelatex, tex.parent, None),
            (xelatex, tex.parent, None),
        ]
    else:
        steps = [(xelatex, tex.parent, None), (xelatex, tex.parent, None)]
    for cmd, cwd, env in steps:
        code = run(cmd, cwd, env)
        if code != 0:
            return code
    log_summary(build / f"{base}.log")
    pdf = build / f"{base}.pdf"
    if pdf.exists():
        shutil.copyfile(pdf, tex.parent / f"{base}.pdf")
        print(f"[compile] copied -> {tex.parent / (base + '.pdf')}")
    else:
        print(f"[compile] WARNING: {pdf} not produced")
        return 1
    return 0

def log_summary(log: Path) -> None:
    """Surface the two log entries that mean 'the reader sees broken layout'.

    LaTeX exits 0 for both: an Overfull hbox silently runs text into the margin,
    and 'Float too large for page' pushes a table/figure off the bottom edge.
    """
    if not log.exists():
        return
    try:
        txt = log.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    over = re.findall(r"Overfull \\hbox \(([0-9.]+)pt too wide\)", txt)
    floats = re.findall(r"Float too large for page by ([0-9.]+)pt", txt)
    if over:
        worst = max(float(x) for x in over)
        print("[compile] Overfull hbox %d 处（最宽 %.1fpt）——文字挤出版心；"
              "常见原因：不可断行的长串/公式" % (len(over), worst))
    if floats:
        worst = max(float(x) for x in floats)
        print("[compile] ❌ 有 %d 个浮动体（表/图）放不进一页：最大超出 %.0fpt ≈ %.0fcm"
              "——内容会被挤出纸外；请拆表/缩小图或改用手工分页"
              % (len(floats), worst, worst / 28.35))


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def find_source_lecture(ws: Path, name: str, exp: Path = None) -> Path | None:
    candidates = []
    if exp is not None:
        candidates.append(exp / f"{name}.pdf")
    candidates += [
        ws / "refer" / f"{name}.pdf",
        ws / "experiments" / name / f"{name}.pdf",
        Path.cwd() / "refer" / f"{name}.pdf",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def lecture_guard(ws: Path, exp: Path, name: str, force: bool) -> str | None:
    """Return an error message when recorded lecture hash differs from current source."""
    if force:
        return None
    log = exp / "lab_report" / "generation_log.md"
    if not log.exists():
        return None
    text = log.read_text(encoding="utf-8")
    # Normalize markdown decoration so `file.tex` SHA-256：`hash` / **hash** all match.
    norm = text.replace("`", "").replace("*", "")
    # Lecture check (skipped only when the source lecture cannot be located).
    src = find_source_lecture(ws, name, exp)
    if src is not None:
        m_lec = re.search(r"源讲义 SHA-256：\s*([0-9a-fA-F]{64})", norm)
        if m_lec and sha256(src) != m_lec.group(1).lower():
            return (
                "❌ 讲义已更新，但 .tex 正文仍为旧版本。\n"
                f"请先运行 /build_lab --experiment {name} 重新生成正文，再执行编译。"
            )
    # .tex staleness is ALWAYS checked (never skipped just because the lecture is missing).
    m_tex = re.search(r"lab_report\.tex SHA-256：\s*([0-9a-fA-F]{64})", norm)
    m_prev = re.search(r"preview(?:_report)?\.tex SHA-256：\s*([0-9a-fA-F]{64})", norm)
    tex = lab_tex(exp)
    prev = preview_tex(exp)
    stale = []
    if m_tex and tex and sha256(tex) != m_tex.group(1).lower():
        stale.append(tex.name)
    if m_prev and prev and sha256(prev) != m_prev.group(1).lower():
        stale.append(prev.name)
    if stale:
        return (
            "❌ 预习报告或实验报告正文已过期（" + "、".join(stale) + "）。\n"
            f"请先运行 /build_lab --experiment {name} 重新生成正文，再执行编译。"
        )
    return None


def compile_all(exp: Path, ws: Path, name: str, force: bool) -> int:
    warn_log_version(exp)
    err = lecture_guard(ws, exp, name, force)
    if err:
        print("[compile-guard] " + err)
        return 1
    ok = True
    found = False
    for tex in (preview_tex(exp), lab_tex(exp)):
        if tex is None:
            continue
        found = True
        ok = compile_tex(tex) == 0 and ok
    if not found:
        print("[compile] 报告 .tex 缺失；跳过（先由 Skill 生成 LaTeX 正文）")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Lab Workflow Generator runner")
    parser.add_argument("--workspace", default=".", help="workspace root (default: cwd)")
    parser.add_argument("--experiment", help="experiment folder name; omit when running inside the experiment folder (folder name is used)")
    parser.add_argument(
        "--stage",
        choices=["scaffold", "status", "ocr", "plots", "tables", "check", "compile", "all"],
        default="all",
        help="stage to run (default: all)",
    )
    parser.add_argument("--force", action="store_true", help="skip lecture-hash guard and force regeneration/compile")
    args = parser.parse_args()

    ws = Path(args.workspace).resolve()
    name = args.experiment or ws.name          # in-place: --workspace IS the experiment folder
    exp = scaffold(ws, name)

    if args.stage in ("scaffold", "all"):
        print("[stage] scaffold done")
    if args.stage in ("status", "all"):
        status(exp)
    rc = 0
    if args.stage in ("ocr", "all"):
        c = ensure_lecture_text(exp)
        rc = c or rc
    if args.stage in ("plots", "all"):
        c = plots(exp)
        rc = c or rc
    if args.stage in ("tables", "all"):
        c = data_tables(exp)
        rc = c or rc
    if args.stage in ("check", "all"):
        c = check_tex(exp)
        rc = c or rc
    if args.stage in ("compile", "all"):
        c = compile_all(exp, ws, name, args.force)
        rc = c or rc
    # 版式检查必须看得见成品 PDF，故排在编译之后（仅 all/compile 阶段执行）
    if args.stage in ("compile", "all"):
        c = pdf_geometry(exp)
        rc = c or rc
    print("[done] 文本正文(.tex)需由 /build_lab 的 Skill 流程生成；本脚本负责确定性步骤。")
    return rc


if __name__ == "__main__":
    sys.exit(main())
