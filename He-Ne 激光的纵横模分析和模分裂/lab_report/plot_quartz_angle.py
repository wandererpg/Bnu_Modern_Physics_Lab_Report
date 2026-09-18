"""Read Sheet1!A23:D43 without modifying the workbook; export sorted data and scatter plots.

Run from any directory: python plot_quartz_angle.py
Dependencies: openpyxl, matplotlib. No fitting or interpolation is performed.
"""
from pathlib import Path
import csv
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import openpyxl

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "实验数据第二次.xlsx"
T_MS = 6.3
FSR_MHZ = 2667.0
workbook = openpyxl.load_workbook(SOURCE, data_only=False, read_only=True)
sheet = workbook["Sheet1"]
rows = []
for row_number in range(24, 44):
    angle, left, right, formula = [sheet.cell(row_number, c).value for c in range(1, 5)]
    if not all(isinstance(v, (int, float)) for v in (angle, left, right)):
        raise ValueError(f"Incomplete measurement in row {row_number}")
    if right < left:
        raise ValueError(f"Unexpected peak ordering in row {row_number}")
    dt = right - left
    rows.append((row_number, angle, left, right, dt, FSR_MHZ * dt / T_MS))
rows.sort(key=lambda row: row[1])
workbook.close()

(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "figures").mkdir(exist_ok=True)
with (ROOT / "data/quartz_angle_sorted.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["工作簿行号", "晶片转角示数_deg", "左峰_ms", "右峰_ms", "峰间距_ms", "频差_MHz"])
    for n, angle, left, right, dt, frequency in rows:
        writer.writerow([n, f"{angle:.1f}", f"{left:.2f}", f"{right:.2f}", f"{dt:.2f}", f"{frequency:.2f}"])

font = font_manager.FontProperties(fname="C:/Windows/Fonts/simsun.ttc")
plt.rcParams.update({"font.family": font.get_name(), "font.size": 11, "axes.unicode_minus": False,
                     "pdf.fonttype": 42, "ps.fonttype": 42})
fig, ax = plt.subplots(figsize=(8.0, 4.3), layout="constrained")
ax.scatter([r[1] for r in rows], [r[5] for r in rows], s=40, color="#245B85",
           edgecolors="white", linewidths=0.6, zorder=3, label="实测峰间距换算值")
ax.set(xlim=(1.9, 12.5), ylim=(0, 740), xlabel="石英晶片转角示数 α / (°)",
       ylabel="两峰频差 Δν / MHz", xticks=[2.2, 3.2, 4.2, 5.2, 6.2, 7.2, 8.2, 9.2, 10.2, 11.2, 12.2])
ax.grid(True, color="#dce2e7", linewidth=0.6, zorder=0)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="lower right", frameon=False)
ax.set_title("T = 6.3 ms；νFSR = 2667 MHz；2.2° 为晶片垂直时示数", fontsize=10, pad=12)
fig.savefig(ROOT / "figures/quartz_angle_scatter.pdf")
fig.savefig(ROOT / "figures/quartz_angle_scatter.png", dpi=240)
plt.close(fig)

print(json.dumps({"source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  "T_ms": T_MS, "FSR_MHz": FSR_MHZ, "rows_sorted": rows}, ensure_ascii=False, indent=2))
