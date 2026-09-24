#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PDF 版式守卫（编译后）：LaTeX 不会因为内容排到纸外而报错。

实测教训
--------
一次真实运行里，一张 10 列表格的横线右端量到 x1=1025.6pt，而 A4 纸宽只有
595.3pt —— 约 430pt（15cm）的内容被排到纸外、读者完全看不到；同一份 PDF 里
矢量图被缩小到 0.62 倍后，图内文字只剩 6.0–7.9pt（正文 10.5pt）；首页"数据说明"
灰框的下边框还从摘要第一行文字中穿过。三种毛病编译全部 exit=0，日志里只有埋在
深处的 Overfull hbox。所以版式必须直接量成品 PDF，而不是相信编译返回码。

检查项
------
  FATAL  元素越出纸面（一定会被切掉）
  WARN   元素越出正文版心（出血到页边距）
  WARN   通栏长行相互重叠（例如首页"数据说明"框与摘要压在一起）
  WARN   框线/表格线从文字中穿过
  WARN   图内文字过小（<8pt 的小字行成簇且带图形笔画）——矢量图缩小后字号一起缩
  WARN   位图有效分辨率 <150dpi（打印发虚）

用法
----
    python check_pdf_geometry.py lab_report.pdf
    python check_pdf_geometry.py lab_report.pdf --strict   # 警告也算失败
    python check_pdf_geometry.py lab_report.pdf --json out.json

依赖 PyMuPDF（fitz）；缺失时打印提示并以 0 退出，绝不阻断流程。
"""
import argparse
import json
import os
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(errors="replace")
    except Exception:
        pass

SMALL_PT = 8.0          # 小于此字号的文本行视为"小字"
MIN_DPI = 150.0         # 位图有效分辨率下限
BLEED_PT = 10.0         # 越过版心的报告阈值（pt）；更小的出血多为 Overfull hbox（约 2–3mm），
                        # 由 runner 的 log_summary 统一汇总，这里只在超过阈值时报
PAGE_TOL_PT = 0.5       # 越出纸面的判定容差（pt）
OVERLAP_AREA = 60.0     # 两行相撞的面积阈值（pt^2）
OVERLAP_DY = 5.5        # 纵向重叠下限（pt）：小于此值多为公式分数碎片（分子/分母）
# 横向重叠下限（pt）：分式的分子/分母会被 fitz 拆成两个"行"，它们纵向叠得很深
# （\frac 的分隔线上下各占半行）却只在中间一小段横向相交（实测 9.8–16.8pt）。
# 真实相撞（如数据说明框压住摘要首行）横向重叠都在几十 pt 以上。取 20pt 作下限，
# 可滤掉分式碎片，又不放过真正的版面碰撞。
OVERLAP_DX = 20.0
OVERLAP_WIDE = 0.80     # 判定"通栏长行"：行宽 ≥ 此比例 × 版心宽
RULE_INSIDE_PT = 1.5    # 横线须位于字形框内部这么深才算"穿透"（否则只是行距紧）
RULE_MIN_GLYPHS = 3     # 一条线至少穿透这么多字形才报
CLUSTER_MIN_LINES = 5   # 小字成簇的最少行数
CLUSTER_MIN_DRAW = 5    # 簇内"图形笔画"最少条数（用来区分图与代码清单）


def _mode(vals):
    """取众数（四舍五入到整 pt）：稳健估计版心边界。"""
    from collections import Counter
    if not vals:
        return None
    return Counter(round(v) for v in vals).most_common(1)[0][0]


def _lines(page):
    """返回 [(bbox, text, max_size)]，逐行（bbox 紧贴字形）。"""
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b.get("lines", []):
            txt = "".join(s["text"] for s in ln["spans"]).strip()
            sz = max([s["size"] for s in ln["spans"]] or [0.0])
            if txt:
                out.append((tuple(ln["bbox"]), txt, sz))
    return out


def _glyphs(page):
    """返回字形级 (bbox, char)：字形框紧贴字墨，用来判断横线是否真的穿透文字。"""
    out = []
    for b in page.get_text("rawdict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b.get("lines", []):
            for sp in ln["spans"]:
                for ch in sp["chars"]:
                    if ch["c"].strip():
                        out.append((tuple(ch["bbox"]), ch["c"]))
    return out


def _ov(a, b):
    """返回 (横向重叠, 纵向重叠)，无重叠则为 0。"""
    dx = min(a[2], b[2]) - max(a[0], b[0])
    dy = min(a[3], b[3]) - max(a[1], b[1])
    return (dx, dy) if (dx > 0 and dy > 0) else (0.0, 0.0)


def _cluster(boxes, gap=36.0):
    """单链聚类：把彼此靠近的 bbox 合成区域。boxes = [(bbox, payload)]。"""
    clusters = []
    for bbox, payload in boxes:
        for c in clusters:
            cb = c["bbox"]
            if not (bbox[2] + gap < cb[0] or bbox[0] > cb[2] + gap
                    or bbox[3] + gap < cb[1] or bbox[1] > cb[3] + gap):
                c["bbox"] = (min(cb[0], bbox[0]), min(cb[1], bbox[1]),
                             max(cb[2], bbox[2]), max(cb[3], bbox[3]))
                c["items"].append((bbox, payload))
                break
        else:
            clusters.append({"bbox": bbox, "items": [(bbox, payload)]})
    return clusters


def analyse(pdf):
    try:
        import fitz
    except ImportError:
        print("[pdf-geo] 未安装 PyMuPDF（pip install pymupdf），跳过版式检查")
        return None
    doc = fitz.open(pdf)

    # ---- 第一遍：估计正文版心（文字行的众数边界）----
    # 逐页先取该页的众数边界，再跨页汇总：若整页都是通栏浮动体（图/表），直接对所有行
    # 取众数会被浮动体带偏（实测把左界估成 312pt）。左界取各页众数的**最小值**、右界取
    # **最大值**——双栏排版下左栏起始与右栏结束才是真正的版心边界。
    def _page_mode(page):
        xs0, xs1 = [], []
        for bb, _t, _s in _lines(page):
            if bb[2] - bb[0] > 30:
                xs0.append(bb[0])
                xs1.append(bb[2])
        if len(xs0) < 5:
            return None, None
        return _mode(xs0), _mode(xs1)

    pages = []
    lefts, rights = [], []
    for page in doc:
        l0, r0 = _page_mode(page)
        if l0 is not None and r0 is not None:
            lefts.append(l0)
            rights.append(r0)
        pages.append((page, _lines(page)))
    left = min(lefts) if lefts else 0.0
    right = max(rights) if rights else 0.0
    text_w = right - left
    # 双栏版心：左栏右边界（取"起于左半页的行"的右界众数）与右栏左边界
    lc = [_mode([bb[2] for bb, _t, _s in ln if bb[0] < 0.45 * right])
          for _pg, ln in pages]
    lc = [v for v in lc if v]
    col_right = _mode([float(v) for v in lc]) or 0.0
    rc = [_mode([bb[0] for bb, _t, _s in ln if bb[0] > 0.45 * right]) for _pg, ln in pages]
    rc = [v for v in rc if v]
    col_left = _mode([float(v) for v in rc]) or 0.0
    twocol = bool(col_left and col_right and (col_left - col_right) > 8)
    if text_w <= 0:
        print("[pdf-geo] 无法估计版心（空文档？），跳过")
        return []

    findings = []          # (level, page, message)
    for pno, (page, lines) in enumerate(pages, 1):
        pw, ph = page.rect.width, page.rect.height
        draws = [tuple(d["rect"]) for d in page.get_drawings() if d["rect"].width > 20]
        # 深色线（供"穿字"判定）：浅灰网格线不计
        dark_rules = []
        for d in page.get_drawings():
            col = d.get("color")
            if col is None:
                continue
            try:
                mean = sum(float(c) for c in col) / max(len(col), 1)
            except TypeError:
                continue
            if mean <= 0.55:
                dark_rules.append((d, tuple(d["rect"])))
        images = []
        for img in page.get_images(full=True):
            for r in page.get_image_rects(img[0]):
                images.append((tuple(r), img))

        # 1) 越出纸面（聚合：每页只报最严重的一条 + 计数）
        elems = [(bb, "文本行「%s」" % t[:22]) for bb, t, _s in lines]
        elems += [(r, "表格/框线") for r in draws]
        elems += [(r, "插图") for r, _i in images]
        bad = []
        for bb, label in elems:
            over_r = bb[2] - (pw - PAGE_TOL_PT)
            over_b = bb[3] - (ph - PAGE_TOL_PT)
            under_l = PAGE_TOL_PT - bb[0]
            under_t = PAGE_TOL_PT - bb[1]
            edge, amount = max(
                [("右", over_r), ("下", over_b), ("左", under_l), ("上", under_t)],
                key=lambda e: e[1])
            if amount > 0:
                bad.append((amount, bb, label, edge))
        if bad:
            bad.sort(key=lambda x: -x[0])
            amount, bb, label, edge = bad[0]
            extra = "，另有 %d 处" % (len(bad) - 1) if len(bad) > 1 else ""
            findings.append(("FATAL", pno,
                             "内容被排到纸外：%s x=[%.0f,%.0f] y=[%.0f,%.0f]，"
                             "纸面 %.0f×%.0fpt（%s边超出 %.0fpt ≈ %.1fcm，读者看不到）%s"
                             % (label, bb[0], bb[2], bb[1], bb[3], pw, ph,
                                edge, amount, amount / 28.35, extra)))
            continue          # 已越出纸面，不再报出血

        # 2) 越出版心（出血到页边距）
        bleed = []
        for bb, label in elems:
            if bb[2] > right + BLEED_PT:
                bleed.append((bb[2] - right, label))
        if bleed:
            bleed.sort(reverse=True)
            excess, label = bleed[0]
            extra = "，另有 %d 处" % (len(bleed) - 1) if len(bleed) > 1 else ""
            findings.append(("WARN", pno,
                             "越出版心右边界：%s 达到 x1=%.1fpt，版心右界 %.1fpt"
                             "（超出 %.1fpt）%s——请检查该表/图/公式是否过宽"
                             % (label, right + excess, right, excess, extra)))

        # 2b) 栏溢出：左栏内容捅进右栏（实测缺陷：一条显示公式宽 327pt 而栏宽仅 227pt，
        #     公式右端伸进右栏 88pt 压住正文文字）
        if twocol:
            right_lines = [(bb, t) for bb, t, _s in lines if bb[0] >= col_left - 5]
            cross = []
            for bb, t, _s in lines:
                # 起于左栏、越过栏界、未延伸到版心右界，**且真的压到右栏文字上**
                # （通栏图表题注/页眉也会越过栏界，但它们不与右栏文字重叠，故不算）
                if not (bb[0] < col_right - 20 and col_right + 4 < bb[2] < right - 6):
                    continue
                for rb, rt in right_lines:
                    dx, dy = _ov(bb, rb)
                    if dx > 8 and dy > 1.5:
                        cross.append((dx, dy, t, rt))
                        break
            if cross:
                cross.sort(reverse=True)
                dx, dy, t, rt = cross[0]
                extra = "，另有 %d 处" % (len(cross) - 1) if len(cross) > 1 else ""
                findings.append(("WARN", pno,
                                 "左栏内容压到右栏文字上：「%s…」与右栏「%s…」重叠 %.0f×%.1fpt%s"
                                 "——多为过宽的显示公式（栏宽仅 %.0fpt）；请拆行"
                                 "（\\begin{split}）或改写得更紧凑"
                                 % (t[:24], rt[:22], dx, dy, extra, col_right - left)))

        # 3) 两行文字真实相撞
        #    判据来自实测：真正相撞的两行"部分纵向重叠"（dy 占行高 40%–85%），
        #    而 fitz 把同一视觉行按字体拆成的碎片会"纵向几乎完全重合"（dy/h > 0.85），
        #    公式的分子/分母碎片则 dy 很小（约 3pt）。据此区分，避免误报。
        ols = []
        for i in range(len(lines)):
            bb1, t1, _s1 = lines[i]
            h1, w1 = bb1[3] - bb1[1], bb1[2] - bb1[0]
            for j in range(i + 1, len(lines)):
                bb2, t2, _s2 = lines[j]
                h2, w2 = bb2[3] - bb2[1], bb2[2] - bb2[0]
                dx, dy = _ov(bb1, bb2)
                if dx * dy < OVERLAP_AREA or dy < OVERLAP_DY:
                    continue
                if dy > 0.85 * min(h1, h2):
                    continue          # 同一视觉行被拆成的碎片
                if dx < max(OVERLAP_DX, 0.5 * min(w1, w2)):
                    continue          # 分式分子/分母碎片（横向只交很窄一段）
                ols.append((dx * dy, dy, t1, t2))
        ols.sort(reverse=True)
        if ols:
            area, dy, t1, t2 = ols[0]
            extra = "，另有 %d 处重叠" % (len(ols) - 1) if len(ols) > 1 else ""
            findings.append(("WARN", pno,
                             "两行文字重叠 %.0fpt²（纵向 %.1fpt）：「%s…」与「%s…」%s"
                             % (area, dy, t1[:22], t2[:22], extra)))

        # 4) 框线/图形线真的从文字中穿过（线落在字形框内部）
        #    区分两种根因：图内元素互相遮挡（图例压线条） vs 版面浮动框与正文间距不足。
        #    浅色细线（如 matplotlib 的网格线，RGB≈0.69）绘制在文字下方，不构成遮挡，
        #    因此只对深色线条判定。
        glyphs = _glyphs(page)
        struck = []
        for rd, rect in dark_rules:
            r = rect
            if r[3] - r[1] > 3 or r[2] - r[0] < 60:
                continue
            y = (r[1] + r[3]) / 2.0
            n, sample = 0, ""
            for bb, ch in glyphs:
                if (bb[3] - bb[1]) < 4:          # 太扁的字形（如横杠）跳过
                    continue
                if bb[1] + RULE_INSIDE_PT < y < bb[3] - RULE_INSIDE_PT \
                        and bb[2] > r[0] and bb[0] < r[2]:
                    n += 1
                    sample = sample or ch
            if n >= RULE_MIN_GLYPHS:
                near = 0
                for _rd2, r2 in dark_rules:
                    if r2 == r:
                        continue
                    if _ov(r2, (r[0] - 40, r[1] - 40, r[2] + 40, r[3] + 40))[0] > 0:
                        near += 1
                struck.append((n, y, sample, near >= 5))
        if struck:
            struck.sort(reverse=True)
            n, y, sample, in_fig = struck[0]
            more = "，本页共 %d 处" % len(struck) if len(struck) > 1 else ""
            if in_fig:
                findings.append(("WARN", pno,
                                 "图内元素互相遮挡：y=%.1f 的图形线穿过 %d 个字符（如「%s」）%s"
                                 "——图例/标注压在数据线或坐标区上；请在绘图脚本里调整 legend 位置、"
                                 "加边距（tight_layout/bbox_inches）后重新出图"
                                 % (y, n, sample, more)))
            else:
                findings.append(("WARN", pno,
                                 "横线从文字中穿过：y=%.1f 处穿透 %d 个字形（如「%s」）%s"
                                 "——若在正文/浮动框内，加 \\vspace 或 \\enlargethispage 拉开间距；"
                                 "若在图内，请在绘图脚本里调整 legend 位置与边距后重新出图"
                                 % (y, n, sample, more)))

        # 5) 图内小字成簇（矢量图被缩小后字号一起缩）
        small = [(bb, t) for bb, t, s in lines if s < SMALL_PT and len(t) >= 2]
        if small:
            for c in _cluster(small):
                strokes = sum(1 for r in draws
                              if _ov(r, c["bbox"])[0] > 0 and _ov(r, c["bbox"])[1] > 0
                              and not (r[3] - r[1] > 3 and r[2] - r[0] > 0.8 * text_w))
                if len(c["items"]) >= CLUSTER_MIN_LINES and strokes >= CLUSTER_MIN_DRAW:
                    sizes = sorted(s for bb, _t, s in lines
                                   if s < SMALL_PT and _ov(bb, c["bbox"])[0] > 0)
                    med = sizes[len(sizes) // 2] if sizes else 0.0
                    findings.append(("WARN", pno,
                                     "图内文字过小：约 %d 行文字只有 %.1fpt（正文 10.5pt）——"
                                     "矢量图被缩小后字号跟着缩；请按最终尺寸出图，"
                                     "或用 figure* + 宽度≥0.85\\textwidth"
                                     % (len(c["items"]), med)))
                    break

        # 6) 位图有效分辨率
        for r, img in images:
            if r[2] - r[0] < 18 or r[3] - r[1] < 18:
                continue
            dpi = min(img[2] / ((r[2] - r[0]) / 72.0), img[3] / ((r[3] - r[1]) / 72.0))
            if dpi < MIN_DPI:
                findings.append(("WARN", pno, "插图有效分辨率仅 %.0f dpi（<%.0f）：打印会发虚"
                                 % (dpi, MIN_DPI)))

    summary = {}
    for lv, _p, _m in findings:
        summary[lv] = summary.get(lv, 0) + 1
    print("[pdf-geo] %s：%d 页，版心 x∈[%.1f, %.1f]（宽 %.1fpt）"
          % (os.path.basename(pdf), doc.page_count, left, right, text_w))
    for lv, pno, msg in findings:
        print("[pdf-geo] %-5s p%-3d %s" % (lv, pno, msg))
    if not findings:
        print("[pdf-geo] OK  未发现越纸/出血/重叠/穿字/小字/低分辨率问题")
    print("[pdf-geo] 汇总：FATAL %d，WARN %d" % (summary.get("FATAL", 0), summary.get("WARN", 0)))
    return findings


def main():
    ap = argparse.ArgumentParser(description="编译后 PDF 版式守卫")
    ap.add_argument("pdf", help="编译产物 PDF")
    ap.add_argument("--strict", action="store_true", help="把 WARN 也当作失败")
    ap.add_argument("--json", help="把结果写入 JSON")
    a = ap.parse_args()
    if not os.path.isfile(a.pdf):
        print("[pdf-geo] 找不到 PDF：%s（跳过）" % a.pdf)
        return 0
    findings = analyse(a.pdf)
    if findings is None:
        return 0
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump([{"level": lv, "page": p, "message": m} for lv, p, m in findings],
                      f, ensure_ascii=False, indent=2)
    if any(lv == "FATAL" for lv, _p, _m in findings) or (a.strict and findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
