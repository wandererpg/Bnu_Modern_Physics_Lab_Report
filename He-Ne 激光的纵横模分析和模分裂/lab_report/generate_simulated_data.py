from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
FIGURE_DIR = ROOT / "figures"
DATA_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

FSR_MHZ = 1810.0
C = 299_792_458.0
LASER_WAVELENGTH_M = 632.8e-9
LASER_FREQUENCY_HZ = C / LASER_WAVELENGTH_M
RNG = np.random.default_rng(20260908)

CHINESE_FONT_PATH = Path(r"C:\Windows\Fonts\msyh.ttc")
if CHINESE_FONT_PATH.exists():
    font_manager.fontManager.addfont(CHINESE_FONT_PATH)
    CHINESE_FONT_FAMILY = font_manager.FontProperties(
        fname=CHINESE_FONT_PATH
    ).get_name()
else:
    CHINESE_FONT_FAMILY = "sans-serif"

plt.rcParams.update(
    {
        "font.family": CHINESE_FONT_FAMILY,
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "legend.fontsize": 9,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.unicode_minus": False,
    }
)


def r_squared(observed: np.ndarray, predicted: np.ndarray) -> float:
    residual = np.sum((observed - predicted) ** 2)
    total = np.sum((observed - np.mean(observed)) ** 2)
    return float(1.0 - residual / total)


def standard_uncertainty(values: np.ndarray, resolution: float) -> float:
    type_a = np.std(values, ddof=1) / np.sqrt(values.size)
    type_b = resolution / np.sqrt(3.0)
    return float(np.sqrt(type_a**2 + type_b**2))


# 1. Free-spectral-range calibration and resolution-limit measurements.
calibration_period_ms = np.array([9.98, 10.03, 10.01, 9.97, 10.02])
calibration = pd.DataFrame(
    {
        "trial": np.arange(1, calibration_period_ms.size + 1),
        "fsr_period_ms": calibration_period_ms,
    }
)
calibration.to_csv(DATA_DIR / "fsr_calibration.csv", index=False)

period_mean_ms = float(np.mean(calibration_period_ms))
period_u_ms = standard_uncertainty(calibration_period_ms, resolution=0.01)
frequency_scale_mhz_per_ms = FSR_MHZ / period_mean_ms
frequency_scale_u = frequency_scale_mhz_per_ms * period_u_ms / period_mean_ms

fwhm_ms = np.array([0.084, 0.087, 0.083, 0.086, 0.085])
resolution = pd.DataFrame(
    {"trial": np.arange(1, fwhm_ms.size + 1), "peak_fwhm_ms": fwhm_ms}
)
resolution.to_csv(DATA_DIR / "interferometer_resolution.csv", index=False)

fwhm_mean_ms = float(np.mean(fwhm_ms))
fwhm_u_ms = standard_uncertainty(fwhm_ms, resolution=0.002)
resolution_limit_mhz = frequency_scale_mhz_per_ms * fwhm_mean_ms
resolution_limit_u = resolution_limit_mhz * np.sqrt(
    (frequency_scale_u / frequency_scale_mhz_per_ms) ** 2
    + (fwhm_u_ms / fwhm_mean_ms) ** 2
)
finesse = FSR_MHZ / resolution_limit_mhz
resolving_power = LASER_FREQUENCY_HZ / (resolution_limit_mhz * 1e6)


# 2. Modal spectra of two He-Ne tubes within one interferometer FSR.
tube_specs = {
    "A": {
        "tem00_time_ms": np.array([0.62, 3.05, 5.46, 7.89]),
        "higher_time_ms": np.array([0.98, 3.42, 5.82, 8.26]),
        "tem00_amplitude": np.array([0.55, 0.90, 1.00, 0.65]),
        "higher_amplitude": np.array([0.20, 0.31, 0.28, 0.16]),
        "higher_mode": "TEM10",
        "ruler_length_m": 0.343,
    },
    "B": {
        "tem00_time_ms": np.array([0.45, 2.12, 3.78, 5.46, 7.13, 8.79]),
        "higher_time_ms": np.array([0.92, 2.60, 4.25, 5.93, 7.61, 9.26]),
        "tem00_amplitude": np.array([0.35, 0.61, 0.88, 1.00, 0.82, 0.48]),
        "higher_amplitude": np.array([0.11, 0.19, 0.29, 0.34, 0.25, 0.14]),
        "higher_mode": "TEM01",
        "ruler_length_m": 0.500,
    },
}

tube_results: dict[str, dict[str, float | str]] = {}
modal_frames: dict[str, pd.DataFrame] = {}
for tube_name, spec in tube_specs.items():
    fundamental = spec["tem00_time_ms"]
    higher = spec["higher_time_ms"]
    longitudinal_dt = np.diff(fundamental)
    transverse_dt = higher - fundamental
    longitudinal_mean = float(np.mean(longitudinal_dt))
    transverse_mean = float(np.mean(transverse_dt))
    longitudinal_u = standard_uncertainty(longitudinal_dt, resolution=0.01)
    transverse_u = standard_uncertainty(transverse_dt, resolution=0.01)
    longitudinal_mhz = frequency_scale_mhz_per_ms * longitudinal_mean
    transverse_mhz = frequency_scale_mhz_per_ms * transverse_mean
    longitudinal_mhz_u = longitudinal_mhz * np.sqrt(
        (frequency_scale_u / frequency_scale_mhz_per_ms) ** 2
        + (longitudinal_u / longitudinal_mean) ** 2
    )
    transverse_mhz_u = transverse_mhz * np.sqrt(
        (frequency_scale_u / frequency_scale_mhz_per_ms) ** 2
        + (transverse_u / transverse_mean) ** 2
    )
    effective_length_m = C / (2.0 * longitudinal_mhz * 1e6)
    theoretical_spacing_mhz = C / (2.0 * float(spec["ruler_length_m"])) / 1e6
    relative_deviation_pct = (
        abs(longitudinal_mhz - theoretical_spacing_mhz)
        / theoretical_spacing_mhz
        * 100.0
    )

    tem00_frame = pd.DataFrame(
        {
            "peak_index": np.arange(1, fundamental.size + 1),
            "mode": "TEM00",
            "time_ms": fundamental,
            "frequency_offset_mhz": fundamental * frequency_scale_mhz_per_ms,
            "relative_amplitude": spec["tem00_amplitude"],
        }
    )
    higher_frame = pd.DataFrame(
        {
            "peak_index": np.arange(1, higher.size + 1),
            "mode": str(spec["higher_mode"]),
            "time_ms": higher,
            "frequency_offset_mhz": higher * frequency_scale_mhz_per_ms,
            "relative_amplitude": spec["higher_amplitude"],
        }
    )
    combined = pd.concat([tem00_frame, higher_frame], ignore_index=True).sort_values(
        "time_ms"
    )
    combined.to_csv(DATA_DIR / f"tube_{tube_name.lower()}_modal_peaks.csv", index=False)
    modal_frames[tube_name] = combined
    tube_results[tube_name] = {
        "higher_mode": str(spec["higher_mode"]),
        "longitudinal_time_ms": longitudinal_mean,
        "longitudinal_time_u_ms": longitudinal_u,
        "longitudinal_spacing_mhz": longitudinal_mhz,
        "longitudinal_spacing_u_mhz": longitudinal_mhz_u,
        "transverse_time_ms": transverse_mean,
        "transverse_time_u_ms": transverse_u,
        "transverse_spacing_mhz": transverse_mhz,
        "transverse_spacing_u_mhz": transverse_mhz_u,
        "effective_length_m": effective_length_m,
        "ruler_length_m": float(spec["ruler_length_m"]),
        "theoretical_spacing_mhz": theoretical_spacing_mhz,
        "relative_deviation_pct": relative_deviation_pct,
    }


def lorentzian(x: np.ndarray, center: float, fwhm: float, amplitude: float) -> np.ndarray:
    return amplitude / (1.0 + 4.0 * ((x - center) / fwhm) ** 2)


frequency_axis = np.linspace(0.0, FSR_MHZ, 6000)
for tube_name in ["A", "B"]:
    fig, axis = plt.subplots(figsize=(6.8, 3.6))
    frame = modal_frames[tube_name]
    spectrum = np.full_like(frequency_axis, 0.015)
    for row in frame.itertuples(index=False):
        spectrum += lorentzian(
            frequency_axis,
            float(row.frequency_offset_mhz),
            resolution_limit_mhz,
            float(row.relative_amplitude),
        )
    axis.plot(frequency_axis, spectrum, color="#1f5a99", linewidth=1.25)
    higher_mode = str(tube_specs[tube_name]["higher_mode"])
    for mode_name, color in [("TEM00", "#b42318"), (higher_mode, "#297a3a")]:
        subset = frame.loc[frame["mode"].eq(mode_name)]
        axis.scatter(
            subset["frequency_offset_mhz"],
            subset["relative_amplitude"] + 0.015,
            color=color,
            s=22,
            label=mode_name,
            zorder=3,
        )
    axis.set_xlabel("一个自由光谱区内的频率偏移 / MHz")
    axis.set_ylabel("相对光强")
    axis.set_title(f"He-Ne 激光管 {tube_name} 的模拟模谱")
    axis.grid(alpha=0.2)
    axis.legend(frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(
        FIGURE_DIR / f"modal_spectrum_tube_{tube_name.lower()}.png",
        bbox_inches="tight",
    )
    plt.close(fig)


# 3. Output bandwidth and gain-envelope estimate.
gain_detuning_mhz = np.array([-735, -600, -450, -300, -150, 0, 150, 300, 450, 600, 720])
gain_relative_intensity = np.array([0.01, 0.32, 0.61, 0.82, 0.95, 1.00, 0.96, 0.83, 0.60, 0.31, 0.02])
gain = pd.DataFrame(
    {
        "frequency_detuning_mhz": gain_detuning_mhz,
        "relative_intensity": gain_relative_intensity,
    }
)
gain.to_csv(DATA_DIR / "gain_curve.csv", index=False)

gain_coefficients = np.polyfit(gain_detuning_mhz, gain_relative_intensity, 2)
gain_prediction = np.polyval(gain_coefficients, gain_detuning_mhz)
gain_r2 = r_squared(gain_relative_intensity, gain_prediction)
gain_roots = np.sort(np.roots(gain_coefficients))
output_bandwidth_mhz = float(gain_roots[1] - gain_roots[0])
output_bandwidth_u_mhz = 30.0
fluorescence_width_mhz = 1500.0
bandwidth_deviation_pct = (
    abs(output_bandwidth_mhz - fluorescence_width_mhz)
    / fluorescence_width_mhz
    * 100.0
)

gain_dense = np.linspace(gain_roots[0] - 50, gain_roots[1] + 50, 800)
fig, ax = plt.subplots(figsize=(7.0, 4.2))
ax.scatter(gain_detuning_mhz, gain_relative_intensity, color="#b42318", label="模拟数据")
ax.plot(gain_dense, np.polyval(gain_coefficients, gain_dense), color="#1f5a99", label="二次拟合")
ax.axvline(gain_roots[0], color="#666666", linestyle="--", linewidth=0.9)
ax.axvline(gain_roots[1], color="#666666", linestyle="--", linewidth=0.9)
ax.set_xlabel("频率失谐 / MHz")
ax.set_ylabel("相对输出强度")
ax.set_title("He-Ne 激光器出光带宽拟合")
ax.set_ylim(-0.05, 1.08)
ax.grid(alpha=0.2)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIGURE_DIR / "gain_curve.png", bbox_inches="tight")
plt.close(fig)


# 4. Birefringent mode splitting and polarization relationship.
crystal_angle_deg = np.array([0, 5, 10, 15, 20, 25, 30], dtype=float)
splitting_mhz = np.array([3, 13, 28, 72, 115, 190, 249], dtype=float)
sin2_angle = np.sin(np.deg2rad(crystal_angle_deg)) ** 2
split_coefficients = np.polyfit(sin2_angle, splitting_mhz, 1)
split_prediction = np.polyval(split_coefficients, sin2_angle)
split_r2 = r_squared(splitting_mhz, split_prediction)
splitting = pd.DataFrame(
    {
        "crystal_angle_deg": crystal_angle_deg,
        "sin_squared_angle": sin2_angle,
        "splitting_mhz": splitting_mhz,
    }
)
splitting.to_csv(DATA_DIR / "mode_splitting.csv", index=False)

polarizer_angle_deg = np.arange(0.0, 181.0, 15.0)
phase_deg = 4.0
o_intensity = 0.035 + 0.96 * np.cos(np.deg2rad(polarizer_angle_deg - phase_deg)) ** 2
e_intensity = 0.040 + 0.91 * np.sin(np.deg2rad(polarizer_angle_deg - phase_deg)) ** 2
o_intensity += RNG.normal(0.0, 0.014, polarizer_angle_deg.size)
e_intensity += RNG.normal(0.0, 0.014, polarizer_angle_deg.size)
o_intensity = np.clip(o_intensity, 0.0, None)
e_intensity = np.clip(e_intensity, 0.0, None)

theta_rad = np.deg2rad(polarizer_angle_deg)
design = np.column_stack(
    [np.ones_like(theta_rad), np.cos(2.0 * theta_rad), np.sin(2.0 * theta_rad)]
)
o_coefficients, *_ = np.linalg.lstsq(design, o_intensity, rcond=None)
e_coefficients, *_ = np.linalg.lstsq(design, e_intensity, rcond=None)
o_prediction = design @ o_coefficients
e_prediction = design @ e_coefficients
o_r2 = r_squared(o_intensity, o_prediction)
e_r2 = r_squared(e_intensity, e_prediction)

dense_angle = np.linspace(0.0, 180.0, 1801)
dense_rad = np.deg2rad(dense_angle)
dense_design = np.column_stack(
    [np.ones_like(dense_rad), np.cos(2.0 * dense_rad), np.sin(2.0 * dense_rad)]
)
o_dense = dense_design @ o_coefficients
e_dense = dense_design @ e_coefficients
o_max_angle = float(dense_angle[np.argmax(o_dense)])
e_max_angle = float(dense_angle[np.argmax(e_dense)])
polarization_separation_deg = abs(e_max_angle - o_max_angle)
if polarization_separation_deg > 90.0:
    polarization_separation_deg = 180.0 - polarization_separation_deg

polarization = pd.DataFrame(
    {
        "polarizer_angle_deg": polarizer_angle_deg,
        "o_mode_relative_intensity": o_intensity,
        "e_mode_relative_intensity": e_intensity,
    }
)
polarization.to_csv(DATA_DIR / "polarization_scan.csv", index=False)

fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.scatter(sin2_angle, splitting_mhz, color="#b42318", label="模拟数据")
split_dense_x = np.linspace(0.0, float(np.max(sin2_angle)), 300)
ax.plot(
    split_dense_x,
    np.polyval(split_coefficients, split_dense_x),
    color="#1f5a99",
    label="线性拟合",
)
ax.set_xlabel(r"$\sin^2\theta$")
ax.set_ylabel("模分裂频差 / MHz")
ax.set_title("模分裂随石英晶片角度的变化")
ax.grid(alpha=0.2)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIGURE_DIR / "mode_splitting_fit.png", bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.scatter(polarizer_angle_deg, o_intensity, color="#1f5a99", s=22, label="高频分裂峰")
ax.scatter(polarizer_angle_deg, e_intensity, color="#b42318", s=22, label="低频分裂峰")
ax.plot(dense_angle, o_dense, color="#1f5a99")
ax.plot(dense_angle, e_dense, color="#b42318")
ax.set_xlabel("偏振片角度 / (°)")
ax.set_ylabel("相对光强")
ax.set_title("两分裂峰的偏振响应")
ax.set_xlim(0, 180)
ax.grid(alpha=0.2)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIGURE_DIR / "polarization_scan.png", bbox_inches="tight")
plt.close(fig)


# 5. Mode competition while changing the PZT control voltage.
pzt_voltage_v = np.array([-12, -8, -4, 0, 4, 8, 12], dtype=float)
mode_1_intensity = 0.05 + 0.92 / (1.0 + np.exp(-pzt_voltage_v / 3.5))
mode_2_intensity = 0.05 + 0.90 / (1.0 + np.exp(pzt_voltage_v / 3.5))
mode_1_intensity += RNG.normal(0.0, 0.025, pzt_voltage_v.size)
mode_2_intensity += RNG.normal(0.0, 0.025, pzt_voltage_v.size)
mode_1_intensity = np.clip(mode_1_intensity, 0.0, 1.0)
mode_2_intensity = np.clip(mode_2_intensity, 0.0, 1.0)
competition_correlation = float(np.corrcoef(mode_1_intensity, mode_2_intensity)[0, 1])
competition = pd.DataFrame(
    {
        "relative_pzt_voltage_v": pzt_voltage_v,
        "mode_1_relative_intensity": mode_1_intensity,
        "mode_2_relative_intensity": mode_2_intensity,
    }
)
competition.to_csv(DATA_DIR / "mode_competition.csv", index=False)

fig, ax = plt.subplots(figsize=(7.0, 4.0))
ax.plot(pzt_voltage_v, mode_1_intensity, "o-", color="#1f5a99", label="模式 1")
ax.plot(pzt_voltage_v, mode_2_intensity, "s-", color="#b42318", label="模式 2")
ax.set_xlabel("相对 PZT 控制电压 / V")
ax.set_ylabel("相对光强")
ax.set_title("PZT 调谐过程中的模式竞争")
ax.grid(alpha=0.2)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(FIGURE_DIR / "mode_competition.png", bbox_inches="tight")
plt.close(fig)


results = {
    "data_notice": "All numerical records are simulated and must not be represented as actual measurements.",
    "fsr_mhz": FSR_MHZ,
    "period_mean_ms": period_mean_ms,
    "period_u_ms": period_u_ms,
    "frequency_scale_mhz_per_ms": frequency_scale_mhz_per_ms,
    "frequency_scale_u_mhz_per_ms": frequency_scale_u,
    "resolution_limit_mhz": resolution_limit_mhz,
    "resolution_limit_u_mhz": resolution_limit_u,
    "finesse": finesse,
    "resolving_power": resolving_power,
    "tube_results": tube_results,
    "gain_fit_coefficients": gain_coefficients.tolist(),
    "gain_fit_r2": gain_r2,
    "gain_roots_mhz": gain_roots.tolist(),
    "output_bandwidth_mhz": output_bandwidth_mhz,
    "output_bandwidth_u_mhz": output_bandwidth_u_mhz,
    "fluorescence_width_mhz": fluorescence_width_mhz,
    "bandwidth_deviation_pct": bandwidth_deviation_pct,
    "splitting_fit_slope_mhz": float(split_coefficients[0]),
    "splitting_fit_intercept_mhz": float(split_coefficients[1]),
    "splitting_fit_r2": split_r2,
    "o_polarization_r2": o_r2,
    "e_polarization_r2": e_r2,
    "o_max_angle_deg": o_max_angle,
    "e_max_angle_deg": e_max_angle,
    "polarization_separation_deg": polarization_separation_deg,
    "competition_correlation": competition_correlation,
}

with (DATA_DIR / "analysis_results.json").open("w", encoding="utf-8") as stream:
    json.dump(results, stream, ensure_ascii=False, indent=2)

print(json.dumps(results, ensure_ascii=False, indent=2))
