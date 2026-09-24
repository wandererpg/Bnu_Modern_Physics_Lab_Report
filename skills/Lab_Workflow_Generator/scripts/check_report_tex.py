# -*- coding: utf-8 -*-
"""Static checks for a generated lab-report .tex source.

Turns prose rules from report.md into machine checks:
  * every figure/table environment has a caption  (report.md: all figures/tables must have a title)
  * every \\ref/\\eqref target exists              (no dangling references)
  * labels are actually referenced                 (no orphan labels)
  * required sections are present for the document kind
  * abstract length hint (teacher format: 100-200 字)

Usage:
  python check_report_tex.py lab_report.tex
  python check_report_tex.py lab_report.tex --kind lab
  python check_report_tex.py preview_report.tex --kind preview
  python check_report_tex.py --dir .            # checks preview_report*.tex + lab_report.tex
  python check_report_tex.py lab_report.tex --strict   # warnings become errors

Exit code: 0 = no errors (warnings allowed unless --strict); 1 = errors found.
Standard library only.
"""
import argparse
import io
import os
import re
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(errors="replace")
    except Exception:
        pass

LAB_SECTIONS = ["引言", "原理", "实验", "结果与分析讨论", "结论", "参考文献"]
PREVIEW_SECTIONS = ["实验目的", "实验原理", "实验仪器", "实验方法", "实验内容"]

ENVS = {"figure": r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}",
        "table": r"\\begin\{table\*?\}(.*?)\\end\{table\*?\}"}


def read(p):
    with io.open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


# --- 表格宽度守卫 ---------------------------------------------------------
# 实测教训：LaTeX 不会因为表格比版心宽而报错，只会把内容排到纸外（一张 10 列表
# 的横线右端量到 x1=1025.6pt，而 A4 纸宽仅 595.3pt）。列宽估算与 make_data_tables.py
# 共用同一套口径，避免两处判断不一致。
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from make_data_tables import em_width, min_em, FIT_EM_STAR, FIT_EM_PLAIN
except Exception:                                     # pragma: no cover
    def em_width(s):
        return sum(1.0 if ord(c) > 0x2E7F else 0.5 for c in (s or ""))

    def min_em(s):
        return em_width(s)

    FIT_EM_STAR, FIT_EM_PLAIN = 45.0, 21.0


def _brace_arg(s, i):
    """s[i] == '{' 时返回 (内容, 结束下标)；支持嵌套与转义。"""
    if i >= len(s) or s[i] != "{":
        return None, i
    depth, j = 0, i
    while j < len(s):
        if s[j] == "\\":
            j += 2
            continue
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return None, i


def tabular_specs(txt):
    """取出每张 tabular 的列规格。"""
    out = []
    for m in re.finditer(r"\\begin\{tabular\*?\}", txt):
        k = txt.find("{", m.end())
        spec, _ = _brace_arg(txt, k)
        if spec is not None:
            out.append(spec)
    return out


def n_columns(spec):
    """列数：跳过 >{...}/<{...} 修饰与 p{...} 的宽度参数。"""
    n, i = 0, 0
    while i < len(spec):
        c = spec[i]
        if c in "><":
            _, i = _brace_arg(spec, i + 1)
            continue
        if c in "pmb":
            n += 1
            _, i = _brace_arg(spec, i + 1)
            continue
        if c in "lcrXS":
            n += 1
        i += 1
    return n


def table_width_em(block, ncol):
    """估算自然宽度（em）：各列最宽单元格 + 内边距。

    必须从 tabular 表体开始量：环境前缀（[htbp]、\centering、\caption、列规格）会被
    并入第一行第一列，虚增一倍以上（实测 49 em 被算成 99 em）。
    """
    body = block
    m = re.search(r"\\begin\{tabular\*?\}", block)
    if m:
        k = block.find("{", m.end())
        _spec, end = _brace_arg(block, k)
        if end > k:
            body = block[end:]
    body = re.sub(r"\\(?:top|mid|bottom|cmid)rule\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", body)
    rows = [[c.strip() for c in ln.split("&")]
            for ln in re.split(r"\\\\", body) if "&" in ln]
    total = 0.0
    for k in range(ncol):
        widest = 0.0
        for r in rows:
            if k < len(r):
                widest = max(widest, em_width(r[k]))
        total += widest + 1.2
    return total


def load_with_inputs(path, seen=None, depth=0):
    """Text of `path` with \\input/\\include-ed files inlined.

    Labels routinely live in included fragments (e.g. tables/*.tex produced by
    make_data_tables.py), so refs must be resolved against sources too.
    """
    if seen is None:
        seen = set()
    ap = os.path.abspath(path)
    if ap in seen or depth > 8:
        return ""
    seen.add(ap)
    try:
        txt = read(path)
    except OSError:
        return ""
    base = os.path.dirname(ap)

    def sub(m):
        target = m.group(1).strip()
        if not target:
            return ""
        cand = target if os.path.splitext(target)[1] else target + ".tex"
        full = os.path.join(base, cand.replace("/", os.sep))
        if not os.path.isfile(full):
            return ""          # let LaTeX report the missing file
        return load_with_inputs(full, seen, depth + 1)

    return re.sub(r"\\(?:input|include)\s*\{([^}]*)\}", sub, txt)


def labels(txt):
    return re.findall(r"\\label\{([^}]*)\}", txt)


def refs(txt):
    out = []
    for cmd in ("ref", "eqref", "autoref", "pageref"):
        out += re.findall(r"\\%s\{([^}]*)\}" % cmd, txt)
    return out


def sections(txt):
    return [s.strip() for s in re.findall(r"\\section\*?\{([^}]*)\}", txt)]


def _plain_text(src):
    """Strip LaTeX commands and inline math, keep readable characters."""
    s = re.sub(r"\$[^$]*\$", " ", src)                       # inline math
    s = re.sub(r"\\[A-Za-z]+\s*(\[[^\]]*\])?(\{[^{}]*\})?", " ", s)
    s = re.sub(r"[\\{}$&~^_]", " ", s)
    return s


def strip_for_paren_scan(txt):
    """为「行文不得出现括号」这条规则做掩码：只留下真正的行文文字。

    掩掉（它们不是行文）：LaTeX 注释、代码环境 lstlisting/verbatim/minted、
    数学环境与行内 $...$（公式里的分组括号如 (B_h^{+−}-B_h^{−+})/2 属数学语法）、
    \\eqref（渲染成 (10)，是编号）、\\texttt{} 与 \\verb||（文件名/标识符）。
    """
    # 掩码必须保留换行符，否则后续行号会整体前移，告警定位就错了
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))

    def blank_code(m):
        """代码环境：首行是 \\begin{lstlisting}[...,caption={题注}] —— 题注是可读文字，
        必须保留（曾因整块掩掉而漏检“（prepare_real_data.py 节选）”这类括号）；只掩代码本体。"""
        return m.group(1) + re.sub(r"[^\n]", " ", m.group(2)) + " " * len(m.group(3))

    t = txt
    for env in ("equation", "equation*", "align", "align*", "gather", "gather*",
                "eqnarray", "eqnarray*", "displaymath", "split", "cases", "array"):
        t = re.sub(r"\\begin\{%s\}(\s*\[[^\]]*\])?(.*?)\\end\{%s\}"
                   % (re.escape(env), re.escape(env)), blank, t, flags=re.S)
    for env in ("lstlisting", "verbatim", "minted"):
        t = re.sub(r"(\\begin\{%s\}[^\n]*\n)(.*?)(\\end\{%s\})" % (env, env),
                   blank_code, t, flags=re.S)
    t = re.sub(r"\\\[(.*?)\\\]", blank, t, flags=re.S)
    t = re.sub(r"\\\((.*?)\\\)", blank, t, flags=re.S)
    # 行内数学：不得跨行匹配（[^$\\] 会吞掉换行，把后面整段正文都掩掉 → 漏检）
    t = re.sub(r"\$(?:[^$\\\n]|\\.)*\$", blank, t)
    t = re.sub(r"\\eqref\{[^}]*\}", blank, t)
    t = re.sub(r"\\texttt\{[^}]*\}", blank, t)
    t = re.sub(r"\\verb\|[^|]*\|", blank, t)
    t = re.sub(r"(?m)^[ \t]*%.*$", blank, t)             # 整行注释
    t = re.sub(r"(?<!\\)%.*", blank, t)                  # 行尾注释
    return t


def prose_parens(txt):
    """返回正文行文中出现的括号 [(行号, 片段), ...]。

    用户要求：正文行文中不得出现括号——旁注、说明、枚举序号、图表引用、单位提示
    都应改写成标点或从句，例如「（表 3）」写「见表 3」、「（1）…」写「第一，…」。
    数学公式内部的分组括号、\\eqref 的编号括号、代码与文件名里的括号不算。
    """
    out = []
    for i, ln in enumerate(strip_for_paren_scan(txt).split("\n"), 1):
        for m in re.finditer(r"[（(][^（()）]{0,60}?[）)]", ln):
            out.append((i, m.group(0)))
    return out


def brace_arg(s, pos):
    """取 s[pos]（应为 '{'）起始的配对花括号内容，支持嵌套。

    题注/参数里含 $T^{2}$、\\textbf{...} 时，正则的 [^}]* 会被内层 } 截断，
    导致长度判据误报——凡是要"读完整参数"的地方都用本函数（v1.26 修正）。
    """
    if pos >= len(s) or s[pos] != "{":
        return ""
    depth, out = 0, []
    for ch in s[pos:]:
        if ch == "{":
            depth += 1
            if depth == 1:
                continue
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        if depth >= 1:
            out.append(ch)
    return "".join(out)


def abstract_chars(txt):
    """Abstract length, supporting both plain 摘要…关键词 and thuemp's empAbstract env."""
    m = re.search(r"\\begin\{empAbstract\}(.*?)\\end\{empAbstract\}", txt, re.S)
    if m:
        body = m.group(1)
    else:
        m = re.search(r"摘\s*要(.{0,1500}?)(关键词|\\noindent\s*\\textbf\{关键词)", txt, re.S)
        body = m.group(1) if m else None
    if body is None:
        return None
    plain = _plain_text(body)
    # count CJK characters plus alphanumeric tokens (numbers/units count as content)
    return len(re.findall(r"[\u4e00-\u9fff]|[0-9A-Za-z]", plain))


def check_file(path, kind, strict):
    txt = load_with_inputs(path)
    errors, warns = [], []
    name = os.path.basename(path)

    # 1) figure/table must carry a caption; label is recommended
    counts = {}
    for env, pat in ENVS.items():
        blocks = re.findall(pat, txt, re.S)
        counts[env] = len(blocks)
        for i, b in enumerate(blocks, 1):
            if ("\\caption" not in b) and ("\\bicaption" not in b):
                errors.append("%s: 第 %d 个 %s 环境没有 \\caption/\\bicaption（图表必须有题）" % (name, i, env))
            if "\\label" not in b:
                warns.append("%s: 第 %d 个 %s 环境缺少 \\label（无法在正文引用）" % (name, i, env))

    # 2) references resolve, labels are referenced
    lb, rf = labels(txt), refs(txt)
    lb_set, rf_set = set(lb), set(rf)
    for r in sorted(rf_set - lb_set):
        errors.append("%s: 引用了不存在的标签 \\ref{%s}" % (name, r))
    for l in sorted(lb_set - rf_set):
        warns.append("%s: 标签 \\label{%s} 从未被引用" % (name, l))

    # 3) required sections
    want = PREVIEW_SECTIONS if kind == "preview" else LAB_SECTIONS
    joined = " ".join(sections(txt)) + " " + txt[:4000]
    # 「参考文献」在 thuemp 模板里由 \bibliography 输出（标题走 \refname），不是 \section，
    # 且排在正文之后——只查章节标题与前 4000 字符会误报缺失（v1.26 修正）。
    if re.search(r"\\bibliography\{|\\begin\{thebibliography\}|\\refname", txt):
        joined += " 参考文献"
    missing = [s for s in want if s not in joined]
    if missing:
        errors.append("%s: 缺少必需章节 %s" % (name, "、".join(missing)))

    # 3b) lab reports must carry 摘要 / 关键词 markers
    #     thuemp 模板由 empAbstract 环境与 \Keyword 宏生成版面上的「摘 要」「关键词」，
    #     .tex 里没有这两个汉字，故按宏名一并识别（v1.26 修正）。
    if kind == "lab":
        markers = (("摘要", r"摘要|\\begin\{empAbstract\}"),
                   ("关键词", r"关键词|\\Keyword"))
        for label, pat in markers:
            if not re.search(pat, txt):
                errors.append("%s: 缺少「%s」" % (name, label))

    # 3b2) 行文不得出现括号（用户硬要求：括号旁注不符合行文逻辑）
    #      改写办法：旁注并入句子（用逗号或「即」）、表图引用写成「见表 3」、
    #      枚举序号写成「第一，…」、单位提示写成「单位为 m」、不确定度写成
    #      「标准不确定度为 …」。数学分组括号与 \eqref 编号不在判据内。
    pp = prose_parens(txt)
    if pp:
        shown = "；".join("L%d %s" % (ln, frag) for ln, frag in pp[:4])
        more = "，另有 %d 处" % (len(pp) - 4) if len(pp) > 4 else ""
        warns.append("%s: 行文出现括号 %d 处（%s%s）——请改写为逗号从句或「见表 X」"
                     "「第一，…」「单位为 …」这类写法；公式分组括号与 \\eqref 编号不计"
                     % (name, len(pp), shown, more))

    # 3c) reference order: only equations must be introduced before being cited
    #     (forward references to figures/tables — "见表 3" — are normal style)
    label_pos = {}
    for mm in re.finditer(r"\\label\{([^}]*)\}", txt):
        label_pos.setdefault(mm.group(1), mm.start())
    seen_fwd = set()
    for mm in re.finditer(r"\\eqref\{([^}]*)\}", txt):
        tgt = mm.group(1)
        lp = label_pos.get(tgt)
        if lp is not None and lp > mm.start() and tgt not in seen_fwd:
            seen_fwd.add(tgt)
            warns.append("%s: 公式引用先于定义 —— 先写“式\\eqref{%s}”，其后才排版该式；建议先给出公式再引用"
                         % (name, tgt))

    # 3d) readability guards (discovered from a real run: shrunken figures/tables)
    if re.search(r"\\resizebox|\\scalebox", txt):
        warns.append("%s: 使用了 \\resizebox/\\scalebox——会把图/表整体缩到看不清；建议改用 table*、减少列数或拆表" % name)
    for m in re.finditer(r"\\includegraphics\s*(\[[^\]]*\])?\s*\{([^}]*)\}", txt):
        opts, path = m.group(1) or "", m.group(2)
        wm = re.search(r"width\s*=\s*([0-9.]+)\s*\\(?:text|line|column)width", opts)
        if wm and float(wm.group(1)) < 0.85 and ("record" not in path.lower()):
            warns.append("%s: 插图 %s 宽度仅 %.2f 倍栏宽，可能被缩得过小（图内文字会看不清）；"
                         "建议按最终尺寸出图或用 figure* + 宽度≥0.85" % (name, path, float(wm.group(1))))
    for env, pat in ENVS.items():
        for i, b in enumerate(re.findall(pat, txt, re.S), 1):
            cap = re.search(r"\\(?:bi)?caption\s*\{", b)
            if cap:
                # 题注参数按花括号配对取，不能用 [^}]*：题注里含数学 $T^{2}$、
                # \textbf{} 时会被第一个 } 截断，长度判据随之误报（v1.26 修正）。
                cap_text = brace_arg(b, cap.end() - 1)
                if len(cap_text.strip()) < 10:
                    warns.append("%s: 第 %d 个 %s 的题注过短（<10 字），读者难以看懂"
                                 % (name, i, env))
            if env == "table":
                nrow = len(re.findall(r"\\\\", b))
                if nrow > 20:
                    warns.append("%s: 第 %d 个表格约 %d 行（>20），建议拆分或移入附录" % (name, i, nrow))

    # 3e) 表格几何守卫：列数 / 自然宽度 / 长小数
    #     ENVS 的正则只捕获环境内容，看不到 \begin{table*} 标记，故单独扫描一次。
    # strip 区间：cuted 的就地通栏表在 PDF 里是通栏宽度（环境名却是 table）
    strip_spans = [(m.start(), m.end()) for m in
                   re.finditer(r"\\begin\{strip\}.*?\\end\{strip\}", txt, re.S)]
    for i, tm in enumerate(re.finditer(r"\\begin\{(table\*?)\}(.*?)\\end\{\1\}", txt, re.S), 1):
        star = tm.group(1).endswith("*") or any(a <= tm.start() <= b for a, b in strip_spans)
        blk = tm.group(2)
        for spec in tabular_specs(blk):
            ncol = n_columns(spec)
            if ncol > 7:
                warns.append("%s: 第 %d 个表格有 %d 列（>7）——通栏也放不好，建议拆成 2–3 张表"
                             % (name, i, ncol))
            in_strip = any(a <= tm.start() <= b for a, b in strip_spans)
            # tabular*{W} 必然正好排成 W 宽（列间用 \extracolsep 均分），无需估算
            is_star_tab = bool(re.search(r"\\begin\{tabular\*\}", blk))
            if "p{" not in spec and not in_strip and not is_star_tab:
                # strip 内的就地通栏表宽度由 PDF 侧守卫实测，不做文本估算
                est = table_width_em(blk, ncol)
                budget = 0.97 * (FIT_EM_STAR if star else FIT_EM_PLAIN)
                if est > budget:
                    warns.append("%s: 第 %d 个表格（%s）自然宽度约 %.0f em，超过版心 %.0f em "
                                 "——会被排到纸外（编译不报错！）；请用 make_data_tables.py "
                                 "重新生成（已支持列宽自适应）或拆表/减列"
                                 % (name, i, "通栏" if star else "单栏", est, budget))
        if re.search(r"\d+\.\d{8,}", blk):
            warns.append("%s: 第 %d 个表格存在未四舍五入的长小数（≥8 位）——"
                         "请在数据准备脚本里取 3–5 位有效数字" % (name, i))

    # 4) abstract length hint (lab reports only)
    if kind == "lab":
        n = abstract_chars(txt)
        if n is None:
            warns.append("%s: 未识别到摘要段落" % name)
        elif not (100 <= n <= 200):
            warns.append("%s: 摘要约 %d 字，超出 100–200 字建议区间" % (name, n))

    return errors, warns, counts, len(lb_set), len(rf_set)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("tex", nargs="?", help="single .tex file")
    ap.add_argument("--dir", help="directory to scan for preview_report*.tex and lab_report.tex")
    ap.add_argument("--kind", choices=["auto", "lab", "preview"], default="auto")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    a = ap.parse_args()

    targets = []
    if a.tex:
        targets.append(a.tex)
    if a.dir:
        for fn in sorted(os.listdir(a.dir)):
            if fn.endswith(".tex") and ("lab_report" in fn or "preview" in fn):
                targets.append(os.path.join(a.dir, fn))
        sub = os.path.join(a.dir, "preview_report")
        if os.path.isdir(sub):
            for fn in sorted(os.listdir(sub)):
                if fn.endswith(".tex"):
                    targets.append(os.path.join(sub, fn))
    if not targets:
        print("[check] no .tex target given; use <file> or --dir")
        return 2

    all_err, all_warn = [], []
    for p in targets:
        if not os.path.exists(p):
            print("[check] missing:", p)
            continue
        kind = a.kind
        if kind == "auto":
            kind = "preview" if "preview" in os.path.basename(p).lower() else "lab"
        e, w, counts, nl, nr = check_file(p, kind, a.strict)
        print("[%s] %s  kind=%s  figures=%d tables=%d labels=%d refs=%d"
              % ("FAIL" if e else "OK", os.path.basename(p), kind,
                 counts.get("figure", 0), counts.get("table", 0), nl, nr))
        for x in e:
            print("   ERROR  ", x)
        for x in w:
            print("   WARN   ", x)
        all_err += e
        all_warn += w

    print("\n==> %d error(s), %d warning(s)" % (len(all_err), len(all_warn)))
    if all_err or (a.strict and all_warn):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
