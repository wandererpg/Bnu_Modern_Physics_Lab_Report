#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单摆法测重力加速度——数据处理与绘图（demo 示例）
=================================================================
实验名称：单摆法测重力加速度
作者占位：<姓名>（demo 示例，正式使用请替换为真实信息）
数据文件：../data/单摆原始数据 pendulum-raw.csv（读取，不修改）
输出：
    ../figures/pendulum-fit.pdf      T^2–L 最小二乘拟合图（半栏宽，供双栏模板就地插入）
    ../data/单摆逐次结果 pendulum-result.csv   派生结果（供 make_data_tables.py 生成附录表）
依赖：numpy、matplotlib（固定随机种子，结果可复现）
运行：python generate_plots.py
=================================================================
"""
import csv
import os
import sys

import numpy as np

np.random.seed(42)          # 可复现（本示例不引入随机量，保留以符合工作流规范）

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 中文字体：DejaVu Sans 没有 CJK 字形，缺字会变成方框（并触发 missing-glyph 警告）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# 半栏最终尺寸出图：双栏模板 \columnwidth ≈ 3.16 in。figsize 宽度取 3.15 in，
# 插进正文时按 1:1 宽度插入，图内 8pt 文字在成品 PDF 里仍是 8pt（不被缩放）。
COL_W_IN = 3.15

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FIGS = os.path.join(HERE, "..", "figures")
RAW = os.path.join(DATA, "单摆原始数据 pendulum-raw.csv")
DERIVED = os.path.join(DATA, "单摆逐次结果 pendulum-result.csv")
N_T = 50                    # 每次计时包含的周期数


def load_data(path=RAW):
    """读原始记录：摆长 L/m、50 周期累计时间 t50/s。绝不修改原始文件。"""
    L, t50 = [], []
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            L.append(float(row["摆长 L/m"]))
            t50.append(float(row["50T 时间 t50/s"]))
    return np.array(L), np.array(t50)


def process_data(L, t50):
    """计算周期、T^2 与逐次 g，并对 T^2–L 作最小二乘直线。"""
    T = t50 / N_T
    T2 = T ** 2
    g_each = 4.0 * np.pi ** 2 * L / T2
    k, b = np.polyfit(L, T2, 1)                 # T^2 = k L + b
    g_fit = 4.0 * np.pi ** 2 / k
    resid = T2 - (k * L + b)
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((T2 - T2.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot else float("nan")
    return {"T": T, "T2": T2, "g_each": g_each, "k": k, "b": b,
            "g_fit": g_fit, "r2": r2, "max_resid": float(np.max(np.abs(resid)))}


def write_derived(L, res):
    """把派生量写成 CSV（供 make_data_tables.py 生成表格；数值取 4–5 位有效数字）。"""
    with open(DERIVED, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["摆长 L/m", "周期 T/s", "$T^2/\\mathrm{s^2}$",
                    "$g/(\\mathrm{m\\cdot s^{-2}})$"])
        for li, ti, t2i, gi in zip(L, res["T"], res["T2"], res["g_each"]):
            w.writerow(["%.3f" % li, "%.4f" % ti, "%.4f" % t2i, "%.3f" % gi])
        w.writerow(["平均", "--", "--", "%.3f" % float(np.mean(res["g_each"]))])
    return DERIVED


def make_figures(L, res):
    """半栏宽紧凑图：figsize 宽度 3.15 in、字号 8–8.5 pt，1:1 插入正文后图内文字仍 ≥8pt。"""
    os.makedirs(FIGS, exist_ok=True)
    plt.rcParams.update({"font.size": 8.5, "axes.labelsize": 8.5,
                         "axes.linewidth": 0.6, "legend.fontsize": 8,
                         "xtick.major.width": 0.6, "ytick.major.width": 0.6})
    fig, ax = plt.subplots(figsize=(COL_W_IN, 2.35))
    ax.plot(L, res["T2"], "o", ms=3.6, mfc="white", mec="#1f3b73", mew=1.0,
            label="测量点")
    xs = np.linspace(L.min() * 0.97, L.max() * 1.03, 50)
    ax.plot(xs, res["k"] * xs + res["b"], "-", lw=1.0, color="#c0392b",
            label="最小二乘拟合")
    ax.set_xlabel("摆长 $L$/m")
    ax.set_ylabel("$T^2/\\mathrm{s^2}$")
    ax.tick_params(labelsize=8, length=2.5)
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    ax.text(0.97, 0.06, "$g=%.3f\\ \\mathrm{m/s^2}$" % res["g_fit"],
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5)
    fig.tight_layout(pad=0.25)
    out = os.path.join(FIGS, "pendulum-fit.pdf")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def main():
    L, t50 = load_data()
    res = process_data(L, t50)
    csv_out = write_derived(L, res)
    fig_out = make_figures(L, res)
    print("n = %d，摆长 %.3f–%.3f m" % (len(L), L.min(), L.max()))
    print("斜率 k = %.5f s^2/m，截距 b = %.5f s^2，R^2 = %.6f" % (res["k"], res["b"], res["r2"]))
    print("逐次 g = %s m/s^2（平均 %.3f）"
          % (", ".join("%.3f" % g for g in res["g_each"]), float(np.mean(res["g_each"]))))
    print("拟合得 g = %.3f m/s^2，最大残差 %.2e s^2" % (res["g_fit"], res["max_resid"]))
    print("已写出：%s" % os.path.relpath(csv_out, HERE))
    print("已写出：%s" % os.path.relpath(fig_out, HERE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
