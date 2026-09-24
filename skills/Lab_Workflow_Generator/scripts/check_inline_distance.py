#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查“正文提及 → 图表本体”的即时性：同栏内，引用行之后多少 pt 就是该图/表。

用户要求：文中刚出现“图1”两个字，图1 就紧接在那句话之后。因此判据不是“相隔几页”，
而是**同页同栏内、引用行到该浮动体内容上沿的垂直距离（pt）**——越小越“紧贴”。

两处度量细节（v1.25 修正）
--------------------------
1. 图（`figure[H]`）的题注在图**下方**，若量到题注，就会把图高（约 140pt）算成间距，
   把“紧贴”误报成“相距 177pt”。故以**内容上沿**为准：题注上沿与图片 bbox 上沿中取更靠上者。
2. 正文里的“仪表 $0.1\ \mathrm{A}$”断行后，行首会出现“表 0.1 A …”，会被误当成“表 0”的
   题注；故要求编号后不接小数点/数字，且前面不是“仪”。

用法：python check_inline_distance.py lab_report.pdf [--max-gap 60]
输出：每个图/表一行：引用行 y、内容 y、垂直距离（pt）、是否同栏。
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


def analyse(pdf, max_gap=60.0):
    try:
        import fitz
    except ImportError:
        print("[inline] 未安装 PyMuPDF，跳过")
        return None
    doc = fitz.open(pdf)
    rows = []
    for pno, page in enumerate(doc, 1):
        items = []
        for b in page.get_text("dict")["blocks"]:
            if b.get("type") != 0:
                continue
            for ln in b.get("lines", []):
                t = "".join(s["text"] for s in ln["spans"]).strip()
                if t:
                    items.append((tuple(ln["bbox"]), t))
        # 浮动体内容上沿：图的题注在图**下方**，只量到题注会把图高（约 140pt）算成间距。
        # 需要同时看位图 bbox 与矢量绘图 bbox——matplotlib 出的 PDF 是以 Form XObject
        # 矢量嵌入的，get_image_info() 取不到，只有 get_drawings() 能看到坐标轴框线。
        # 表格的题注在上，其框线在题注下方，会被下面的 y 区间条件排除，仍以题注为准。
        cands = []
        try:
            for info in page.get_image_info():
                cands.append(tuple(info["bbox"]))
        except Exception:
            pass
        try:
            for d in page.get_drawings():
                r = d.get("rect")
                if r is not None:
                    cands.append((r.x0, r.y0, r.x1, r.y1))
        except Exception:
            pass
        # 题注：行首且较长；引用：行中。
        # 陷阱：正文"仪表 0.1 A"断行后行首出现"表 0.1 A …"，会被误判为"表 0"；
        # 故编号后不得接小数点/数字，且前面不是"仪"。
        caps, refs = {}, {}
        for bb, t in items:
            for m in re.finditer(r"(?<!仪)(表|图)\s*(\d+)(?![\d.])", t):
                key = (m.group(1), int(m.group(2)))
                if m.start() == 0 and len(t) > 12:
                    caps.setdefault(key, bb)
                else:
                    refs.setdefault(key, bb)
        for key in sorted(set(caps) & set(refs)):
            rb, cb = refs[key], caps[key]
            same_col = (rb[0] < 300) == (cb[0] < 300)
            if not same_col:
                rows.append((key[0], key[1], pno, rb[1], cb[1], None, False))
                continue
            top = cb[1]
            for ib in cands:
                if (ib[0] < 300) == (rb[0] < 300) and rb[1] - 2 <= ib[1] <= cb[1] + 2:
                    top = min(top, ib[1])
            rows.append((key[0], key[1], pno, rb[1], top, top - rb[1], True))
    print("[inline] %s：%d 页" % (os.path.basename(pdf), doc.page_count))
    bad = 0
    for kind, n, pno, ry, cy, gap, same in rows:
        if gap is None:
            print("  %s%-3d p%-3d 引用 y=%-6.0f 题注在另一栏" % (kind, n, pno, ry))
            bad += 1
        else:
            flag = "" if abs(gap) <= max_gap else "  ⚠ 相距 %.0fpt" % gap
            print("  %s%-3d p%-3d 引用 y=%-6.0f → 内容 y=%-6.0f 间距 %6.0fpt%s"
                  % (kind, n, pno, ry, cy, gap, flag))
            if abs(gap) > max_gap:
                bad += 1
    print("[inline] %s（阈值 %.0fpt ≈ 3 行）"
          % ("OK  全部紧贴引用" if not bad else "WARN 有 %d 个图/表未紧贴引用" % bad, max_gap))
    return rows


def main():
    ap = argparse.ArgumentParser(description="正文提及与图表本体的即时性检查")
    ap.add_argument("pdf")
    ap.add_argument("--max-gap", type=float, default=60.0, help="允许的垂直间距（pt，默认 60≈3 行）")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    if not os.path.isfile(a.pdf):
        print("[inline] 找不到 %s" % a.pdf)
        return 0
    rows = analyse(a.pdf, a.max_gap)
    if rows is None:
        return 0
    over = [r for r in rows if r[5] is None or abs(r[5]) > a.max_gap]
    return 1 if (a.strict and over) else 0


if __name__ == "__main__":
    sys.exit(main())
