#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract a lecture PDF's text, OCR-ing pages that carry no text layer.

Why: some course lectures are pure scans (a 8-page scan can yield 8 characters of
text). Generation must still be able to bind report facts to the lecture, so this
script produces a page-marked text file the Skill can read.

Usage:
  python ocr_lecture.py --experiment "<exp dir>"          # <exp>/<name>.pdf -> <exp>/lab_report/lecture_ocr.txt
  python ocr_lecture.py <lecture.pdf> [--out out.txt]
  python ocr_lecture.py <lecture.pdf> --pages 1-3 --dpi 220

Per page: embedded text is used when it looks real (>= --min-text chars),
otherwise the page is rendered and OCR-ed (rapidocr-onnxruntime).
"""
import argparse
import io
import os
import sys
import tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(errors="replace")
    except Exception:
        pass

MIN_TEXT = 50          # a page with fewer chars than this is treated as a scan


def parse_pages(spec, total):
    if not spec:
        return list(range(total))
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out += list(range(int(a) - 1, min(int(b), total)))
        elif part:
            out.append(int(part) - 1)
    return [i for i in out if 0 <= i < total]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", nargs="?", help="lecture PDF")
    ap.add_argument("--experiment", help="experiment folder (finds <name>/<name>.pdf)")
    ap.add_argument("--out", help="output .txt (default: alongside the PDF)")
    ap.add_argument("--pages", help="page range, e.g. 1-3 or 2,4,6")
    ap.add_argument("--dpi", type=int, default=200, help="render DPI for OCR (default 200)")
    ap.add_argument("--min-text", type=int, default=MIN_TEXT, help="chars above which a page's text layer is trusted")
    a = ap.parse_args()

    pdf = None
    default_out = None
    if a.experiment:
        exp = Path(a.experiment).resolve()
        cands = [p for p in exp.glob("*.pdf") if p.is_file()]
        if not cands:
            print("[ocr] no lecture PDF in", exp)
            return 2
        pdf = cands[0]
        default_out = exp / "lab_report" / "lecture_ocr.txt"
    elif a.pdf:
        pdf = Path(a.pdf).resolve()
        default_out = pdf.with_name(pdf.stem + "_ocr.txt")
    else:
        print("[ocr] give <lecture.pdf> or --experiment <dir>")
        return 2

    out = Path(a.out).resolve() if a.out else default_out
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        import fitz                       # PyMuPDF
    except ImportError:
        print("[ocr] PyMuPDF (fitz) not installed -> pip install pymupdf")
        return 3

    doc = fitz.open(str(pdf))
    pages = parse_pages(a.pages, doc.page_count)
    engine = None
    chunks, n_ocr, n_text, tmpdir = [], 0, 0, tempfile.mkdtemp(prefix="ocr_")

    for i in pages:
        page = doc.load_page(i)
        embedded = (page.get_text() or "").strip()
        if len(embedded) >= a.min_text:
            n_text += 1
            chunks.append("<<<PAGE %d>>> [text]\n%s\n" % (i + 1, embedded))
            continue
        if engine is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
            except ImportError:
                print("[ocr] rapidocr-onnxruntime not installed -> pip install rapidocr-onnxruntime")
                print("[ocr] pages without a text layer cannot be read; embedding text layer instead")
                chunks.append("<<<PAGE %d>>> [no-text-layer]\n%s\n" % (i + 1, embedded))
                continue
            engine = RapidOCR()
        pix = page.get_pixmap(dpi=a.dpi)
        tmp_png = os.path.join(tmpdir, "p%03d.png" % (i + 1))
        pix.save(tmp_png)
        res, _elapse = engine(tmp_png)
        lines = [r[1] for r in (res or [])]
        n_ocr += 1
        chunks.append("<<<PAGE %d>>> [ocr]\n%s\n" % (i + 1, "\n".join(lines)))
        print("[ocr] page %d/%d OCR -> %d line(s)" % (i + 1, doc.page_count, len(lines)))

    doc.close()
    text = "\n".join(chunks)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("\n[ocr] %s" % pdf.name)
    print("[ocr] pages: %d (text layer %d, OCR %d)" % (len(pages), n_text, n_ocr))
    print("[ocr] chars: %d" % len(text))
    print("[ocr] written -> %s" % out)
    try:
        os.rmdir(tmpdir)
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
