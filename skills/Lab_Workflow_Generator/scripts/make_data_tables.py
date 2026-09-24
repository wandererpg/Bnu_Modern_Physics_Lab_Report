# -*- coding: utf-8 -*-
"""Generate LaTeX (booktabs) table fragments from an experiment's data/*.csv.

Why: the upstream course workspace hand-copies appendix tables out of its CSVs,
so editing data never updates the report. This script keeps the appendix
reproducible: rerun it and the tables follow the data.

Usage (from the experiment's lab_report/ directory):
    python make_data_tables.py                 # data/*.csv -> tables/*.tex
    python make_data_tables.py --data-dir data --out-dir tables
    python make_data_tables.py --max-rows 40   # truncate long tables
    python make_data_tables.py --combined      # also write tables/all_tables.tex

The report then includes a table with e.g.:
    \\input{tables/fsr_calibration}

Standard library only.
"""
import argparse
import csv
import glob
import io
import json
import os
import re
import sys
import unicodedata


# GBK consoles cannot encode some glyphs; never crash on print.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(errors="replace")
    except Exception:
        pass

_ESC = [
    ("\\", r"\textbackslash{}"),
    ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
    ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
    ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
]


def tex_escape(s):
    """转义 LaTeX 特殊字符，但**保留 `$...$` 数学片段**。

    表头/单元格里常写 `$B_{res}$/G`、`$g_F$` 这类公式；若一并转义，PDF 里会显示成
    字面的 `$B_{res}$/G`（实测 10 行如此）。因此先按 `$...$` 切分，只转义非数学部分。
    """
    s = s if s is not None else ""
    if "$" in s:
        out = []
        for i, seg in enumerate(re.split(r"(\$[^$]*\$)", s)):
            if i % 2 == 1:                      # 数学片段，原样保留
                out.append(seg)
            else:
                for a, b in _ESC:
                    seg = seg.replace(a, b)
                out.append(seg)
        s = "".join(out)
        return s.replace("--", "-{-}")
    for a, b in _ESC:
        s = s.replace(a, b)
    # TeX 会把 ASCII 的 "--" 连字成 en-dash "–"，使数据里的 "--"（如方向组合 −−）
    # 显示成单个短横线而与 "-" 无法区分；这里插入空组阻断连字（放在最后，避免插入的
    # 花括号又被上面的转义规则处理）。
    return s.replace("--", "-{-}")


def slug(name):
    s = re.sub(r"[^0-9A-Za-z]+", "-", os.path.splitext(name)[0]).strip("-").lower()
    return s or "table"


def assign_slugs(files):
    """Unique, stable file slugs.

    Chinese-only names would all collapse to the same ASCII slug (and silently
    overwrite each other), so fall back to tNN and de-duplicate with a counter.
    Existing ASCII slugs are preserved, keeping older reports' \\input paths valid.
    """
    used, out = set(), {}
    for i, fn in enumerate(files, 1):
        base = slug(fn)
        if base == "table":                      # nothing ASCII left to use
            base = "t%02d" % i
        cand, k = base, 2
        while cand in used:
            print("[tables] note: slug collision resolved -> %s (from %s)" % (cand, fn))
            cand = "%s-%d" % (base, k)
            k += 1
        used.add(cand)
        out[fn] = cand
    return out


def read_csv(path, max_rows):
    with io.open(path, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except Exception:
            dialect = csv.excel
        rows = [r for r in csv.reader(f, dialect) if any((c or "").strip() for c in r)]
    if not rows:
        return None, None, 0
    header, body = rows[0], rows[1:]
    truncated = len(body) > max_rows
    if truncated:
        body = body[:max_rows]
    return header, body, (len(rows) - 1 if truncated else 0)


def is_numeric(col):
    for v in col:
        v = (v or "").strip().replace("\u00a0", "")
        if v == "" or v == "-":
            continue
        try:
            float(v)
        except ValueError:
            return False
    return True


# ---------------------------------------------------------------------------
# 列宽自适应
#
# 为什么需要：真实运行中一张 10 列表格的横线量到 x1=1025.6pt，而 A4 纸宽只有
# 595.3pt —— 约 430pt（15cm）的内容被排到纸外、读者完全看不到，但 LaTeX 只报
# 一条埋在日志里的 Overfull hbox，不报错。tabular 的 l/r 列永不换行，宽度只由
# 内容决定，所以必须由这里主动规划列宽。
#
# 做法：当自然宽度超过版心时改用 p 列，宽度写成
#     p{\dimexpr <f>\textwidth-8pt\relax}
# 每列减去的 2\tabcolsep 恰好与列间距相消，于是表格总宽 = (Σf)·\textwidth，
# 与具体模板的 \textwidth 数值无关，任何模板下都恰好落在版心内。
# ---------------------------------------------------------------------------

FIT_EM_STAR = 45.0    # 通栏（table*）版心宽度，em；thuemp 双栏 A4 + 五号(10.5pt)
FIT_EM_PLAIN = 21.0   # 单栏（table）版心宽度，em
TABCOLSEP_PT = 4.0    # 自适应列宽时收紧的列间距
FONT_PT = 10.5        # 表格字号（\wuhao 五号）
MIN_COL_EM = 3.0      # 每列宽度下限（em）：宁可略微超出，也不能把「分析项目」压成竖排单字
DIGIT_WARN = 7        # 小数位数超过此值即提示四舍五入


def _cjk(ch):
    return unicodedata.east_asian_width(ch) in ("W", "F")


def em_width(s):
    """粗略宽度（em）：CJK/全角 1.0，其余 0.5。"""
    return sum(1.0 if _cjk(c) else 0.5 for c in (s or ""))


def min_em(s):
    """不可断行的最小宽度（em）：CJK 可逐字断行，ASCII 串（数字）不可断。"""
    best = cur = 0.0
    for c in (s or ""):
        if c.isspace():
            cur = 0.0
        elif _cjk(c):
            best = max(best, cur, 1.0)
            cur = 0.0
        else:
            cur += 0.5
            best = max(best, cur)
    return max(best, cur)


def plan_columns(header, body, ncol, star, use_array=False,
                 fit_em=None, tsep=TABCOLSEP_PT, font_pt=FONT_PT, width_macro="\\textwidth"):
    """规划列规格。

    返回 (spec, kind, notes)：
      kind = "natural"  —— 自然宽度放得下，沿用 l/r（排版最好看）
      kind = "fit"      —— 改用 p 列并压缩到版心内
      kind = "overflow" —— 即使压到最小也放不下，已尽力而为并给出警告
    """
    isnum = [is_numeric([(r[i] if i < len(r) else "") for r in body]) for i in range(ncol)]
    full, mini, longnum = [], [], []
    for i in range(ncol):
        cells = [header[i] if i < len(header) else ""] + \
                [(r[i] if i < len(r) else "") for r in body]
        full.append(max(em_width(c) for c in cells) + 1.2)
        mini.append(max(min_em(c) for c in cells) + 0.35)
        for c in cells:
            m = re.match(r"^-?\d+\.(\d+)$", (c or "").strip())
            if m and len(m.group(1)) > DIGIT_WARN:
                longnum.append(len(m.group(1)))
    notes = []
    if longnum:
        notes.append("WARN  存在未四舍五入的数值（最多 %d 位小数）：建议在数据准备脚本里取 3–5 位有效数字，"
                     "否则列宽会被长数字占满、表头被挤成竖排" % max(longnum))

    natural = "".join("r" if n else "l" for n in isnum)
    e = float(fit_em) if fit_em else (FIT_EM_STAR if star else FIT_EM_PLAIN)
    budget = 0.97 * e                       # 表格总宽上限（\textwidth 的倍数，em 计）
    avail = budget - 2.0 * tsep * ncol / font_pt   # 分给各 p 列正文的 em 总数
    if sum(full) <= budget:
        return natural, "natural", notes

    # 下限：CJK 虽可逐字断行，但压到 1 个字宽会变成竖排（实测「分析项目」被压成
    # 13pt 宽、一字一行，表高 2362pt 直接被顶出纸面）。数值列另有不可断行下限。
    floor = [max(m, MIN_COL_EM) for m in mini]
    base = sum(floor)
    if base >= avail:
        alloc = floor
        kind = "overflow"
        bleed = (base + 2.0 * tsep * ncol / font_pt) / budget - 1.0
        notes.append("FAIL  表宽不足：%d 列的最小宽度合计 %.0f em > 可用 %.0f em——"
                     "本表在%s下会超出版心约 %.0f%%（约 %.0fpt），必须拆表 / 减列 / 精简文字"
                     % (ncol, base, avail, "通栏" if star else "单栏",
                        bleed * 100, bleed * budget * font_pt))
    else:
        extra = [max(f - fl, 0.0) for f, fl in zip(full, floor)]
        tot = sum(extra) or 1.0
        alloc = [fl + (avail - base) * x / tot for fl, x in zip(floor, extra)]
        kind = "fit"
        notes.append("note  自然宽度 %.0f em 超过版心 %.0f em，已改用 p 列压缩到版心内"
                     "（p 列会自动换行，字号不变）" % (sum(full), budget))
        if ncol > 7:
            notes.append("WARN  共 %d 列（>7）：即使压到版心内，通栏表格也会非常拥挤，建议拆成 2–3 张表" % ncol)

    tsep_em = tsep / font_pt                     # 单侧列间距（em）
    spec = []
    if kind == "overflow":
        # 放不下时按「实际需要」出宽度（允许超出 \textwidth）：宁可略微出血，也不能
        # 归一化回版心把每列压成 20pt、「分析项目」一字一行（实测表高 2246pt 被顶出纸面）。
        fr = [(a + 2.0 * tsep_em) / e for a in alloc]
    else:
        s = sum(alloc) or 1.0
        fr = [0.97 * a / s for a in alloc]
    for i, f in enumerate(fr):
        if use_array:
            align = "\\centering" if isnum[i] else "\\raggedright"
            spec.append(">{%s\\arraybackslash}p{\\dimexpr%.5f%s-%.1fpt\\relax}"
                        % (align, f, width_macro, 2 * tsep))
        else:
            spec.append("p{\\dimexpr%.5f%s-%.1fpt\\relax}" % (f, width_macro, 2 * tsep))
    return "".join(spec), kind, notes


def build_table(path, header, body, truncated, slug_name=None, caption=None, hmap=None,
                star=False, fit=True, use_array=False, fit_em=None, place="!t", strip=False,
                single=False, column=False):
    ncol = max([len(header)] + [len(r) for r in body]) if body else len(header)
    name = os.path.splitext(os.path.basename(path))[0]
    if fit:
        if column:
            # 半栏表用 \scriptsize（约 7.5pt）：可用宽度按 10.5/7.5 折算，
            # 否则会把本来放得下的表判成放不下
            if fit_em is None:
                fit_em = FIT_EM_PLAIN * FONT_PT / 7.5
            spec, kind, notes = plan_columns(header, body, ncol, star, use_array, fit_em,
                                              width_macro="\\columnwidth")
        else:
            spec, kind, notes = plan_columns(header, body, ncol, star, use_array, fit_em)
    else:
        spec = "".join(
            "r" if is_numeric([(r[i] if i < len(r) else "") for r in body]) else "l"
            for i in range(ncol)
        )
        kind, notes = "natural", []
    if not spec:
        spec = "l"
    if column and "p{" not in spec:
        spec = "@{\\extracolsep{\\fill}}" + spec
    if single and "p{" not in spec:
        spec = "@{\\extracolsep{\\fill}}" + spec
    out = []
    out.append("% 自动生成（make_data_tables.py），请勿手工编辑；改数据后重新运行脚本。")
    if kind != "natural":
        out.append("% 列宽已自适应到版心（p 列 + \\dimexpr），避免内容被排到纸外。")
        if use_array:
            out.append("% 数值列居中、文本列左对齐依赖 array 宏包（\\usepackage{array}）。")
    if column:
        # 双栏半栏图：就地 [H] + \\columnwidth，只影响所在栏的文字流，不会整页留洞
        out.append("\\begin{table}[H]")
    elif single:
        out.append("\\begin{table}[htbp]")
    elif strip:
        out.append("\\begin{strip}")
        out.append("\\begin{table}[H]")
    else:
        out.append("\\begin{%s}[%s]" % ("table*" if star else "table", place))
    if column:
        out.append("  \\centering")
        out.append("  \\scriptsize")
    else:
        out.append("  \\centering")
    out.append("  \\caption{%s}" % tex_escape(caption or name))
    out.append("  \\label{tab:%s}" % (slug_name or slug(name)))
    if kind != "natural":
        out.append("  \\setlength{\\tabcolsep}{%.0fpt}" % (3 if column else TABCOLSEP_PT))
    if column:
        out.append("  \\begin{tabular*}{\\columnwidth}{%s}" % spec)
    elif single:
        out.append("  \\begin{tabular*}{\\textwidth}{%s}" % spec)
    else:
        out.append("  \\begin{tabular}{%s}" % spec)
    out.append("    \\toprule")
    heads = [(hmap or {}).get(h, h) for h in header[:ncol]]
    out.append("    " + " & ".join(tex_escape(h) for h in heads) + " \\\\")
    out.append("    \\midrule")
    for r in body:
        cells = [(r[i] if i < len(r) else "") for i in range(ncol)]
        out.append("    " + " & ".join(tex_escape(c) for c in cells) + " \\\\")
    out.append("    \\bottomrule")
    out.append("  \\end{tabular*}" if (single or column) else "  \\end{tabular}")
    if truncated:
        out.append("  \\par\\smallskip\\footnotesize 表注：仅列出前 %d 行，其余见 \\texttt{data/%s}。"
                   % (len(body), os.path.basename(path)))
    if strip and not (single or column):
        out.append("\\end{table}")
        out.append("\\end{strip}")
    else:
        out.append("\\end{table*}" if (star and not (single or column)) else "\\end{table}")
    return "\n".join(out) + "\n", kind, notes


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out-dir", default="tables")
    ap.add_argument("--max-rows", type=int, default=30)
    ap.add_argument("--caption-map", help="JSON {\"<csv 文件名>\": \"<表题>\"}；缺省用文件名作表题")
    ap.add_argument("--header-map", help="JSON {\"<csv 文件名>\": {\"<原表头>\": \"<新表头（建议“物理量 / 单位”）>\"}}")
    ap.add_argument("--star", action="store_true", help="输出 table*（双栏通栏），不缩放；适合列数 ≤7 的表")
    ap.add_argument("--fit", dest="fit", action="store_true", default=True,
                    help="（默认）列宽自适应到版心：自然宽度超版心时改用 p 列 + \\dimexpr")
    ap.add_argument("--no-fit", dest="fit", action="store_false",
                    help="沿用旧的 l/r 自然宽度列（会溢出纸面，仅供对照）")
    ap.add_argument("--column", action="store_true",
                    help="双栏半栏表：table[H] + tabular*{\\columnwidth} + \\scriptsize（就地紧贴引用）")
    ap.add_argument("--single", action="store_true",
                    help="单栏就地表格：table[H] + tabular*{\\textwidth}，所有表统一撑满版心")
    ap.add_argument("--strip-csv", default="",
                    help="仅对这些 CSV 用 strip 就地表（逗号分隔文件名或 slug）；缺省空表示按 --strip 全用")
    ap.add_argument("--strip", action="store_true",
                    help="输出 cuted 的 strip + table[H]：全宽但不浮动，表格就地出现在"
                         "正文提及它的地方（需 \\usepackage{cuted}）")
    ap.add_argument("--place", default="!t",
                    help="浮动体位置参数（默认 !t＝页顶且尽量靠前，避免表格与引用它的正文相隔数页；\n"
                         "配合 \\usepackage{flafter} 可保证表格不出现在引用之前）")
    ap.add_argument("--array", action="store_true",
                    help="数值列居中 / 文本列左对齐（需 \\usepackage{array}）；缺省用普通 p 列")
    ap.add_argument("--fit-em", type=float, default=None,
                    help="版心宽度估计（em）：缺省通栏 45、单栏 21；用于判断是否放得下")
    ap.add_argument("--combined", action="store_true",
                    help="also write <out-dir>/all_tables.tex including every table")
    ap.add_argument("--no-prune", dest="prune", action="store_false", default=True,
                    help="保留陈旧生成物（默认会删除 CSV 已不存在的自动生成表，避免报告继续 \\input 到与数据脱节的旧表）")
    a = ap.parse_args()
    a.strip_csv = set(x.strip() for x in a.strip_csv.split(",") if x.strip())

    if not os.path.isdir(a.data_dir):
        print("[tables] no data dir: %s (skip)" % a.data_dir)
        return 0

    os.makedirs(a.out_dir, exist_ok=True)
    made, skipped = [], []
    csv_files = [fn for fn in sorted(os.listdir(a.data_dir)) if fn.lower().endswith(".csv")]
    cmap, hmap = {}, {}
    if a.caption_map and os.path.isfile(a.caption_map):
        with io.open(a.caption_map, "r", encoding="utf-8") as f:
            cmap = json.load(f)
        print("[tables] caption map: %s (%d entries)" % (os.path.basename(a.caption_map), len(cmap)))
    if a.header_map and os.path.isfile(a.header_map):
        with io.open(a.header_map, "r", encoding="utf-8") as f:
            hmap = json.load(f)
        print("[tables] header map: %s (%d csv)" % (os.path.basename(a.header_map), len(hmap)))
    slugs = assign_slugs(csv_files)
    problems = []
    for fn in csv_files:
        p = os.path.join(a.data_dir, fn)
        header, body, dropped = read_csv(p, a.max_rows)
        if not header:
            skipped.append(fn)
            continue
        use_strip = a.strip if not a.strip_csv else (fn in a.strip_csv)
        tex, kind, notes = build_table(p, header, body, dropped > 0, slugs[fn], cmap.get(fn),
                                       hmap.get(fn), a.star, a.fit, a.array, a.fit_em, a.place,
                                       use_strip, a.single, a.column)
        if len(header) > 7:
            print("[tables] WARN  %s 有 %d 列，双栏下会偏挤：建议拆表或减少列数" % (fn, len(header)))
        for n in notes:
            tag, _, rest = n.partition("  ")
            print("[tables] %-5s %s：%s" % (tag, fn, rest or tag))
            if tag in ("WARN", "FAIL"):
                problems.append("%s：%s" % (fn, rest or tag))
        if kind == "overflow":
            print("[tables] FAIL  %s 即使压缩到版心也放不下，编译后必被切到纸外：请拆表" % fn)
        outp = os.path.join(a.out_dir, slugs[fn] + ".tex")
        with io.open(outp, "w", encoding="utf-8", newline="\n") as f:
            f.write(tex)
        made.append((fn, slugs[fn], len(body), dropped))

    for fn, sn, n, dropped in made:
        extra = ("（截断 %d 行）" % dropped) if dropped else ""
        print("[tables] %-34s -> %s  (%d 行%s)" % (fn, sn + ".tex", n, extra))
        if n > 20:
            print("[tables] WARN  %s 有 %d 行（>20）：建议拆分或移入附录" % (fn, n))
    for fn in skipped:
        print("[tables] skip empty: %s" % fn)

    # 清理"陈旧生成物"：CSV 改名/删除后，旧的 tables/*.tex 会留在原地并被报告继续
    # \input（内容与数据脱节）。只删除带自动生成标记的文件，手写表一律不动。
    if a.prune:
        keep = {sn + ".tex" for _fn, sn, _n, _d in made}
        keep.add("all_tables.tex")
        for tf in sorted(glob.glob(os.path.join(a.out_dir, "*.tex"))):
            base = os.path.basename(tf)
            if base in keep:
                continue
            try:
                head = io.open(tf, "r", encoding="utf-8", errors="replace").read(200)
            except OSError:
                continue
            if "自动生成（make_data_tables.py）" in head:
                os.remove(tf)
                print("[tables] prune  陈旧生成物已删除：%s（对应 CSV 已不存在）" % base)

    if a.combined and made:
        comb = os.path.join(a.out_dir, "all_tables.tex")
        with io.open(comb, "w", encoding="utf-8", newline="\n") as f:
            f.write("% 自动生成：包含全部数据表\n")
            for fn, sn, _n, _d in made:
                f.write("\\input{tables/%s}\n" % sn)
        print("[tables] combined -> %s" % comb)

    print("[tables] done: %d table(s) from %d csv(s)" % (len(made), len(csv_files)))
    if problems:
        print("[tables] ===== 表宽/可读性问题 %d 条（编译不会报错，但读者会看不到内容）=====" % len(problems))
        for p in problems:
            print("[tables]   - %s" % p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
