#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""浮动体距离检查：表格/图与其首次正文引用相隔多少页。

为什么需要
----------
用户反馈"正文和它提到的表格相距太远，阅读体验很差"。LaTeX 把 `table*`/`figure*`
这类通栏浮动体排在页顶，每页最多放一两个；通栏浮动体一多就排队，导致表 5、图 4
与其引用相隔 3 页。这个指标必须**量成品 PDF**才能发现（源码里看不出），所以做成脚本，
改完结构后可立即复核。

判据
----
在 PDF 文本里，行首且较长的 "表N …"/"图N …" 视为**题注**，行中的 "表N"/"图N" 视为
**正文引用**；对每个浮动体取"题注页 − 首次引用页"。|相距| > 1 页即告警（附录里的
原始数据表标注 `--appendix-ok` 可豁免，因为它们本就集中在附录）。

用法
----
    python check_float_distance.py lab_report.pdf [--max-gap 1] [--strict]
"""
import argparse
import os
import re
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(errors="replace")
    except Exception:
        pass


def analyse(pdf, max_gap=1):
    try:
        import fitz
    except ImportError:
        print("[float-dist] 未安装 PyMuPDF，跳过")
        return None
    doc = fitz.open(pdf)
    caps, refs, appendix_ref = {}, {}, set()
    for pno, page in enumerate(doc, 1):
        for b in page.get_text("dict")["blocks"]:
            if b.get("type") != 0:
                continue
            for ln in b.get("lines", []):
                t = "".join(s["text"] for s in ln["spans"]).strip()
                if not t:
                    continue
                # 陷阱：正文里的"仪表 0.1 A"断行后行首出现"表 0.1 A …"，会被当成
                # "表 0"的题注。故要求编号后不接小数点/数字，且前面不是"仪"。
                for m in re.finditer(r"(?<!仪)(表|图)\s*(\d+)(?![\d.])", t):
                    key = (m.group(1), int(m.group(2)))
                    # 行首且足够长 → 题注；否则视为正文引用
                    if m.start() == 0 and len(t) > 12:
                        caps.setdefault(key, pno)
                    else:
                        refs.setdefault(key, pno)
                        # "见附录图 X" 这类引用本就指向附录，不算漂移
                        if "附录" in t[:m.end()]:
                            appendix_ref.add(key)
    rows = []
    for kind in ("表", "图"):
        for n in sorted({k[1] for k in list(caps) + list(refs) if k[0] == kind}):
            key = (kind, n)
            if key in caps and key in refs:
                rows.append((kind, n, caps[key], refs[key], caps[key] - refs[key],
                             key in appendix_ref))
    rows = [r for r in rows if not r[5]]
    # 附录里的浮动体（原始数据表、记录照片）本就在文档末尾，其引用自然早得多，不算漂移：
    # 以附录第一页（出现“原始数据/程序与数据说明/附录”章节标题的页）为界豁免。
    app_start = None
    for pno, page in enumerate(doc, 1):
        for b in page.get_text("dict")["blocks"]:
            if b.get("type") != 0:
                continue
            for ln in b.get("lines", []):
                t = "".join(s["text"] for s in ln["spans"]).strip()
                if t.startswith(("原始数据", "程序与数据说明", "附录")):
                    app_start = pno if app_start is None else min(app_start, pno)
    if app_start:
        rows = [r for r in rows if r[2] < app_start]
    bad = [r for r in rows if abs(r[4]) > max_gap]
    print("[float-dist] %s：%d 页；检查 %d 个浮动体" % (os.path.basename(pdf), doc.page_count, len(rows)))
    for kind, n, c, r, gap, _apx in rows:
        flag = "  ⚠ 相距 %+d 页" % gap if abs(gap) > max_gap else ""
        print("  %s%-3d 题注 p%-3d 首次引用 p%-3d%s" % (kind, n, c, r, flag))
    if bad:
        print("[float-dist] WARN  有 %d 个浮动体与其引用相隔超过 %d 页——"
              "通栏浮动体过多会排队；请把原始数据表移入附录、合并同类结果表，"
              "并在每节末尾加 \\FloatBarrier" % (len(bad), max_gap))
    else:
        print("[float-dist] OK  所有浮动体都在 %d 页以内" % max_gap)
    return rows


def main():
    ap = argparse.ArgumentParser(description="浮动体与正文引用距离检查")
    ap.add_argument("pdf")
    ap.add_argument("--max-gap", type=int, default=1, help="允许的最大间隔页数（默认 1）")
    ap.add_argument("--strict", action="store_true", help="超限即返回非零")
    a = ap.parse_args()
    if not os.path.isfile(a.pdf):
        print("[float-dist] 找不到 PDF：%s（跳过）" % a.pdf)
        return 0
    rows = analyse(a.pdf, a.max_gap)
    if rows is None:
        return 0
    over = [r for r in rows if abs(r[4]) > a.max_gap]
    return 1 if (a.strict and over) else 0


if __name__ == "__main__":
    sys.exit(main())
