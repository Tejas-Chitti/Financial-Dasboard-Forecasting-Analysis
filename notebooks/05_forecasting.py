"""
Phase 3 – Revenue Forecasting
Uses ARIMA to project next 6 months of revenue.
Outputs:
  - data/forecast_results.csv   (actual + forecast, for Power BI)
  - dashboard/charts/p3_forecast.png
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from statsmodels.tsa.arima.model import ARIMA
from pathlib import Path

BASE  = Path(__file__).resolve().parent.parent
DATA  = BASE / "data"
OUT   = BASE / "dashboard" / "charts"

BG     = "#F8F9FA"
ACCENT = "#1f77b4"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor":   BG,
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "font.family":      "sans-serif",
})

# ── Load monthly revenue ──────────────────────────────────────
monthly = pd.read_csv(DATA / "sql_results" / "01_revenue_by_month.csv")
monthly["ds"] = pd.to_datetime(
    monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str).str.zfill(2)
)
monthly = monthly.sort_values("ds").set_index("ds")
ts = monthly["Total_Revenue"].asfreq("MS")   # monthly start frequency

# ── Fit ARIMA(1,1,1) ──────────────────────────────────────────
model  = ARIMA(ts, order=(1, 1, 1))
result = model.fit()

# ── Forecast next 6 months ────────────────────────────────────
FORECAST_PERIODS = 6
forecast    = result.get_forecast(steps=FORECAST_PERIODS)
forecast_df = forecast.summary_frame(alpha=0.20)   # 80% CI

future_dates   = pd.date_range(ts.index[-1] + pd.offsets.MonthBegin(), periods=FORECAST_PERIODS, freq="MS")
forecast_df.index = future_dates

# ── Build combined output CSV ─────────────────────────────────
actual_df = pd.DataFrame({
    "Date":     ts.index,
    "Revenue":  ts.values,
    "Type":     "Actual",
    "Forecast": np.nan,
    "Lower_80": np.nan,
    "Upper_80": np.nan,
})

pred_df = pd.DataFrame({
    "Date":     future_dates,
    "Revenue":  np.nan,
    "Type":     "Forecast",
    "Forecast": forecast_df["mean"].values,
    "Lower_80": forecast_df["mean_ci_lower"].values,
    "Upper_80": forecast_df["mean_ci_upper"].values,
})

combined = pd.concat([actual_df, pred_df], ignore_index=True)
combined.to_csv(DATA / "forecast_results.csv", index=False)
print("Saved: data/forecast_results.csv")

# ── Plot ──────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 5))

# Actual line
ax.plot(ts.index, ts.values, color=ACCENT, linewidth=2.2,
        marker="o", markersize=4, label="Actual Revenue", zorder=3)

# Forecast line
ax.plot(future_dates, forecast_df["mean"], color="#ff7f0e",
        linewidth=2.2, linestyle="--", marker="s", markersize=5,
        label="Forecast (ARIMA)", zorder=3)

# Confidence interval shading
ax.fill_between(future_dates,
                forecast_df["mean_ci_lower"],
                forecast_df["mean_ci_upper"],
                color="#ff7f0e", alpha=0.18, label="80% Confidence Interval")

# Divider line
ax.axvline(ts.index[-1], color="gray", linewidth=1, linestyle=":")

# Annotation
ax.annotate("Forecast starts", xy=(future_dates[0], forecast_df["mean"].iloc[0]),
            xytext=(15, 20), textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color="gray"), fontsize=9, color="gray")

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e3:.0f}K"))
ax.set_title("Monthly Revenue – Actual vs ARIMA Forecast (Next 6 Months)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Revenue")
ax.legend(fontsize=9)
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.tight_layout()

path = OUT / "p3_forecast.png"
plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Saved: {path.name}")

# ── Print forecast summary ────────────────────────────────────
print("\n=== 6-MONTH REVENUE FORECAST ===")
summary = pd.DataFrame({
    "Month":    future_dates.strftime("%Y-%m"),
    "Forecast": forecast_df["mean"].round(2),
    "Low_80":   forecast_df["mean_ci_lower"].round(2),
    "High_80":  forecast_df["mean_ci_upper"].round(2),
})
print(summary.to_string(index=False))

total_forecast = forecast_df["mean"].sum()
last_6_actual  = ts.iloc[-6:].sum()
growth = (total_forecast - last_6_actual) / last_6_actual * 100
print(f"\nLast 6 months actual:   ${last_6_actual:,.0f}")
print(f"Next 6 months forecast: ${total_forecast:,.0f}")
print(f"Projected growth:       {growth:+.1f}%")
