#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""安装自检：解释器 / Python 库 / XeLaTeX / 中文字体 / 技能文件齐全性。

用法
----
    python verify_install.py                 # 只做环境与文件自检
    python verify_install.py --demo          # 额外把示例工程跑一遍（端到端冒烟测试）
    python verify_install.py --skills-dir D:\\my\\skills
    python verify_install.py --demo --keep-demo    # 保留临时 demo 工程

退出码：0 = 全部 PASS（可有 WARN）；1 = 存在 FAIL。
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

PKG_ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS = []          # (status, title, detail)
# 只在真终端上色：输出被重定向/被别的程序捕获时不要带 ANSI 转义码
USE_COLOR = sys.stdout.isatty()


def add(status, title, detail=""):
    RESULTS.append((status, title, detail))
    color = ""
    if USE_COLOR:
        color = {"PASS": "\033[32m", "WARN": "\033[33m", "FAIL": "\033[31m",
                 "INFO": "\033[36m"}.get(status, "")
    reset = "\033[0m" if color else ""
    line = "  %s[%s]%s %s" % (color, status, reset, title)
    if detail:
        line += "  —— %s" % detail
    print(line)


def section(title):
    print("\n== %s ==" % title)


# ---------------------------------------------------------------- 环境检查
def check_python():
    v = sys.version_info
    detail = "运行中的解释器：%s" % sys.executable
    if v >= (3, 11):
        add("PASS", "Python %d.%d.%d" % (v[0], v[1], v[2]), detail)
    else:
        add("FAIL", "Python 版本过低：%d.%d.%d（需 ≥3.11）" % (v[0], v[1], v[2]), detail)


def check_libs():
    need = [("numpy", True), ("scipy", False), ("matplotlib", True),
            ("pandas", False), ("fitz", True)]
    names = {"fitz": "PyMuPDF"}
    for mod, required in need:
        label = names.get(mod, mod)
        try:
            m = __import__(mod)
            ver = getattr(m, "__version__", "?")
            if mod == "fitz":
                ver = getattr(m, "VersionBind", None) or getattr(m, "__doc__", "?")
                ver = str(ver).strip().splitlines()[0] if ver else "?"
            add("PASS", "%s %s" % (label, ver))
        except Exception as exc:                       # noqa: BLE001
            add("FAIL" if required else "WARN",
                "%s 未安装" % label,
                "python -m pip install %s（%s）" % (label if mod != "fitz" else "PyMuPDF", exc))


def check_xelatex():
    exe = shutil.which("xelatex")
    if not exe:
        add("FAIL", "xelatex 不在 PATH 中",
            "装 TeX Live 或 MiKTeX（详见 INSTALL.md）")
        return
    try:
        p = subprocess.run([exe, "--version"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
        first = (p.stdout or p.stderr or "").strip().splitlines()
        add("PASS", "xelatex 可用", first[0] if first else exe)
    except Exception as exc:                           # noqa: BLE001
        add("FAIL", "xelatex 无法执行", str(exc))


def check_bibtex_style():
    kpse = shutil.which("kpsewhich")
    if not kpse:
        add("WARN", "找不到 kpsewhich，跳过 gbt7714 检查")
        return
    try:
        p = subprocess.run([kpse, "gbt7714-numerical.bst"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=60)
        out = (p.stdout or "").strip()
        if out:
            add("PASS", "国标参考文献样式 gbt7714-numerical.bst", out)
        else:
            add("WARN", "未找到 gbt7714-numerical.bst",
                "装 texlive-lang-chinese（否则参考文献无法编译）")
    except Exception as exc:                           # noqa: BLE001
        add("WARN", "gbt7714 检查失败", str(exc))


def check_cjk_font():
    try:
        from matplotlib import font_manager
    except Exception:                                  # noqa: BLE001
        add("WARN", "无法检查中文字体（matplotlib 未装）")
        return
    want = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Source Han Sans SC",
            "WenQuanYi Zen Hei", "PingFang SC", "Heiti SC"]
    have = {f.name for f in font_manager.fontManager.ttflist}
    hit = [w for w in want if w in have]
    if hit:
        add("PASS", "中文字体可用（matplotlib 出图）", "、".join(hit[:3]))
    else:
        add("WARN", "未找到常见中文字体",
            "图内中文会显示成方框：装 fonts-noto-cjk（Linux）或在 generate_plots.py 里指定字体")


# ---------------------------------------------------------------- 文件检查
def skill_candidates(name, skills_dir):
    return [os.path.join(skills_dir, name), os.path.join(PKG_ROOT, name)]


def find_skill(name, skills_dir):
    for c in skill_candidates(name, skills_dir):
        if os.path.isfile(os.path.join(c, "SKILL.md")):
            return c
    return None


def check_skills(skills_dir):
    wf = find_skill("Lab_Workflow_Generator", skills_dir)
    if not wf:
        add("FAIL", "未找到 Lab_Workflow_Generator",
            "先运行 install.ps1 / install.sh，或用 --skills-dir 指定目录")
    else:
        where = "已安装" if wf.startswith(os.path.abspath(skills_dir)) else "使用包内副本（未安装）"
        scripts = ["run_lab_workflow.py", "make_data_tables.py", "check_report_tex.py",
                   "check_pdf_geometry.py", "check_float_distance.py",
                   "check_inline_distance.py", "init_workspace.py", "ocr_lecture.py"]
        miss = [s for s in scripts if not os.path.isfile(os.path.join(wf, "scripts", s))]
        assets = ["assets/thu_template/thuemp.cls",
                  "assets/scaffold_template/report_frontmatter_thu.tex",
                  "references/report.md"]
        miss += [a for a in assets if not os.path.isfile(os.path.join(wf, *a.split("/")))]
        ver = "?"
        try:
            with open(os.path.join(wf, "SKILL.md"), encoding="utf-8") as fh:
                m = re.search(r"^version:\s*(\S+)", fh.read(), re.M)
                ver = m.group(1) if m else "?"
        except OSError:
            pass
        if miss:
            add("FAIL", "Lab_Workflow_Generator v%s 文件不齐" % ver, "缺：" + "、".join(miss))
        else:
            add("PASS", "Lab_Workflow_Generator v%s（8 脚本 + 模板资产齐全）" % ver, where)

    core = find_skill("advanced_lab_report_gen", skills_dir)
    if not core:
        add("FAIL", "未找到 advanced_lab_report_gen", "文本核心缺失，正文规则无法加载")
    else:
        where = "已安装" if core.startswith(os.path.abspath(skills_dir)) else "使用包内副本（未安装）"
        size = os.path.getsize(os.path.join(core, "SKILL.md"))
        add("PASS", "advanced_lab_report_gen（SKILL.md %.0f KB）" % (size / 1024.0), where)
    return wf


# ---------------------------------------------------------------- demo 冒烟
def run_demo(wf_skill, keep=False):
    demo_src = os.path.join(PKG_ROOT, "examples", "demo-单摆法测重力加速度")
    if not os.path.isdir(demo_src):
        add("WARN", "包内没有 examples/demo-单摆法测重力加速度，跳过 --demo")
        return
    runner = os.path.join(wf_skill, "scripts", "run_lab_workflow.py")
    tmp = tempfile.mkdtemp(prefix="labdemo-")
    dst = os.path.join(tmp, "demo")
    try:
        shutil.copytree(demo_src, dst)
        # 清掉随包带的编译中间产物，确保是"从源码重建"
        shutil.rmtree(os.path.join(dst, "lab_report", "build"), ignore_errors=True)
        t0 = time.time()
        proc = subprocess.run(
            [sys.executable, runner, "--workspace", dst, "--stage", "all", "--force"],
            cwd=dst, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=1800)
        dt = time.time() - t0
        if proc.returncode != 0:
            add("FAIL", "demo 流水线非零退出（%.0fs）" % dt,
                (proc.stdout or proc.stderr or "")[-400:].replace("\n", " "))
            return
        pdf = os.path.join(dst, "lab_report", "lab_report.pdf")
        if not os.path.isfile(pdf):
            add("FAIL", "demo 未产出 lab_report.pdf", (proc.stdout or "")[-300:])
            return
        pages = "?"
        try:
            import fitz
            with fitz.open(pdf) as doc:
                pages = doc.page_count
        except Exception:                              # noqa: BLE001
            pass
        add("PASS", "demo 端到端跑通：产出 %s 页 PDF（%.0fs）" % (pages, dt), pdf)

        scripts = os.path.join(wf_skill, "scripts")
        tex = os.path.join(dst, "lab_report", "lab_report.tex")
        checks = [("源码检查 0 error", [sys.executable, os.path.join(scripts, "check_report_tex.py"), tex],
                   lambda s: "0 error(s), 0 warning(s)" in s),
                  ("成品版式 FATAL 0 / WARN 0", [sys.executable, os.path.join(scripts, "check_pdf_geometry.py"), pdf],
                   lambda s: "FATAL 0" in s and "WARN 0" in s),
                  ("浮动体 ≤1 页", [sys.executable, os.path.join(scripts, "check_float_distance.py"), pdf],
                   lambda s: "[float-dist] OK" in s),
                  ("图/表紧贴引用", [sys.executable, os.path.join(scripts, "check_inline_distance.py"), pdf],
                   lambda s: "[inline] OK" in s)]
        for title, cmd, ok in checks:
            p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=300)
            out = (p.stdout or "") + (p.stderr or "")
            if ok(out):
                add("PASS", "demo " + title)
            else:
                add("FAIL", "demo " + title, out.strip().splitlines()[-1][:200] if out.strip() else "无输出")
    except subprocess.TimeoutExpired:
        add("FAIL", "demo 执行超时（>30 分钟）")
    except Exception as exc:                           # noqa: BLE001
        add("FAIL", "demo 执行异常", str(exc))
    finally:
        if keep:
            add("INFO", "demo 工程已保留", dst)
        else:
            shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="近物实验报告自动化工作流 —— 安装自检")
    ap.add_argument("--skills-dir", default=os.path.join(os.path.expanduser("~"), ".codex", "skills"),
                    help="Skill 安装目录（默认 ~/.codex/skills）")
    ap.add_argument("--demo", action="store_true", help="额外把示例工程端到端跑一遍")
    ap.add_argument("--keep-demo", action="store_true", help="保留 --demo 的临时工程")
    a = ap.parse_args()

    print("=" * 72)
    print("近物实验报告自动化工作流 —— 安装自检")
    print("  包根目录  : %s" % PKG_ROOT)
    print("  skills 目录: %s" % os.path.abspath(a.skills_dir))
    print("=" * 72)

    section("环境")
    check_python()
    check_libs()
    check_xelatex()
    check_bibtex_style()
    check_cjk_font()

    section("技能文件")
    wf = check_skills(a.skills_dir)

    if a.demo:
        section("端到端冒烟测试（示例工程）")
        if wf:
            run_demo(wf, keep=a.keep_demo)
        else:
            add("FAIL", "缺少 Lab_Workflow_Generator，无法运行 --demo")

    fails = [r for r in RESULTS if r[0] == "FAIL"]
    warns = [r for r in RESULTS if r[0] == "WARN"]
    print("\n" + "=" * 72)
    print("汇总：PASS %d，WARN %d，FAIL %d"
          % (len([r for r in RESULTS if r[0] == "PASS"]), len(warns), len(fails)))
    if fails:
        print("存在 FAIL —— 按上面的提示处理后重跑本脚本。")
    elif warns:
        print("环境可用（WARN 项按需处理）。建议再跑一次 --demo 验证端到端。")
    else:
        print("ALL PASS —— 可以开始用了：把讲义放进实验目录，在会话里 /build_lab。")
    print("=" * 72)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
