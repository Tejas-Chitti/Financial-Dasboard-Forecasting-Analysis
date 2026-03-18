"""
Phase 3 – Dashboard Visualizations
Generates all charts for the 3 Power BI dashboard pages.
Outputs: dashboard/charts/*.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

BASE   = Path(__file__).resolve().parent.parent
DATA   = BASE / "data" / "sql_results"
OUT    = BASE / "dashboard" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

# ── Global style ─────────────────────────────────────────────
PALETTE   = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
BG        = "#F8F9FA"
ACCENT    = "#1f77b4"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor":   BG,
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "font.family":      "sans-serif",
    "axes.titlesize":   13,
    "axes.titleweight": "bold",
})

def save(name):
    path = OUT / name
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"  Saved: {name}")

# ════════════════════════════════════════════════════════════
# PAGE 1 – Executive Summary
# ════════════════════════════════════════════════════════════

monthly = pd.read_csv(DATA / "01_revenue_by_month.csv")
monthly["Order_Date"] = pd.to_datetime(
    monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str).str.zfill(2)
)
monthly = monthly.sort_values("Order_Date")

category = pd.read_csv(DATA / "02_revenue_by_category.csv")
region   = pd.read_csv(DATA / "04_revenue_by_region.csv")

# --- 1a. KPI Summary Card ----------------------------------------
fig, axes = plt.subplots(1, 4, figsize=(14, 3))
fig.suptitle("Executive KPI Summary", fontsize=15, fontweight="bold", y=1.02)

kpis = [
    ("Total Revenue",  f"${monthly['Total_Revenue'].sum():,.0f}",   "#1f77b4"),
    ("Total Profit",   f"${monthly['Total_Profit'].sum():,.0f}",    "#2ca02c"),
    ("Profit Margin",  f"{monthly['Total_Profit'].sum()/monthly['Total_Revenue'].sum()*100:.1f}%", "#ff7f0e"),
    ("Months of Data", f"{len(monthly)}",                           "#9467bd"),
]
for ax, (label, value, color) in zip(axes, kpis):
    ax.set_facecolor(color)
    ax.text(0.5, 0.6,  value, ha="center", va="center", fontsize=22,
            fontweight="bold", color="white", transform=ax.transAxes)
    ax.text(0.5, 0.25, label, ha="center", va="center", fontsize=10,
            color="white", transform=ax.transAxes)
    ax.axis("off")
plt.tight_layout()
save("p1_kpi_cards.png")

# --- 1b. Revenue over Time (line chart) --------------------------
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(monthly["Order_Date"], monthly["Total_Revenue"],
        color=ACCENT, linewidth=2.2, marker="o", markersize=4)
ax.fill_between(monthly["Order_Date"], monthly["Total_Revenue"],
                alpha=0.12, color=ACCENT)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.set_title("Monthly Revenue Trend")
ax.set_xlabel("")
ax.set_ylabel("Revenue")
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.tight_layout()
save("p1_revenue_trend.png")

# --- 1c. Revenue by Category (bar) --------------------------------
fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.barh(category["Category"], category["Total_Revenue"],
               color=PALETTE[:3])
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e3:.0f}K"))
for bar, val in zip(bars, category["Total_Revenue"]):
    ax.text(bar.get_width() + 5000, bar.get_y() + bar.get_height()/2,
            f"${val/1e3:.0f}K", va="center", fontsize=9)
ax.set_title("Revenue by Category")
ax.set_xlabel("Revenue")
plt.tight_layout()
save("p1_revenue_by_category.png")

# --- 1d. Revenue by Region (bar) ----------------------------------
fig, ax = plt.subplots(figsize=(7, 4))
colors = [PALETTE[i % len(PALETTE)] for i in range(len(region))]
bars = ax.bar(region["Region"], region["Total_Revenue"], color=colors)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e3:.0f}K"))
for bar, val in zip(bars, region["Total_Revenue"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5000,
            f"${val/1e3:.0f}K", ha="center", fontsize=9)
ax.set_title("Revenue by Region")
ax.set_ylabel("Revenue")
plt.tight_layout()
save("p1_revenue_by_region.png")

print("\nPage 1 charts done.")

# ════════════════════════════════════════════════════════════
# PAGE 2 – Profit & Cost Analysis
# ════════════════════════════════════════════════════════════

subcat  = pd.read_csv(DATA / "03_revenue_by_subcategory.csv")
segment = pd.read_csv(DATA / "07_revenue_by_segment.csv")
flag    = pd.read_csv(DATA / "09_profit_flag_summary.csv")

# --- 2a. Profit by Sub-Category (sorted bar) ----------------------
subcat_sorted = subcat.sort_values("Total_Profit")
colors = ["#d62728" if v < 0 else "#2ca02c" for v in subcat_sorted["Total_Profit"]]

fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(subcat_sorted["Sub_Category"], subcat_sorted["Total_Profit"], color=colors)
ax.axvline(0, color="black", linewidth=0.8)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e3:.0f}K"))
ax.set_title("Profit by Sub-Category  (red = loss-making)")
ax.set_xlabel("Total Profit")
plt.tight_layout()
save("p2_profit_by_subcategory.png")

# --- 2b. Profit Margin Comparison by Category ---------------------
fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.bar(category["Category"], category["Profit_Margin_Pct"],
              color=PALETTE[:3])
for bar, val in zip(bars, category["Profit_Margin_Pct"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"{val:.1f}%", ha="center", fontsize=10, fontweight="bold")
ax.set_title("Profit Margin % by Category")
ax.set_ylabel("Profit Margin (%)")
ax.set_ylim(0, category["Profit_Margin_Pct"].max() * 1.25)
plt.tight_layout()
save("p2_profit_margin_by_category.png")

# --- 2c. Revenue vs Profit Scatter by Sub-Category ---------------
fig, ax = plt.subplots(figsize=(10, 6))
cat_colors = {"Technology": "#1f77b4", "Furniture": "#ff7f0e",
              "Office Supplies": "#2ca02c"}
for _, row in subcat.iterrows():
    color = cat_colors.get(row["Category"], "gray")
    ax.scatter(row["Total_Revenue"], row["Total_Profit"],
               color=color, s=80, zorder=3)
    ax.annotate(row["Sub_Category"], (row["Total_Revenue"], row["Total_Profit"]),
                fontsize=7, xytext=(4, 4), textcoords="offset points")
ax.axhline(0, color="red", linewidth=0.8, linestyle="--")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e3:.0f}K"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e3:.0f}K"))
ax.set_title("Revenue vs Profit by Sub-Category")
ax.set_xlabel("Total Revenue")
ax.set_ylabel("Total Profit")
from matplotlib.patches import Patch
legend = [Patch(color=c, label=l) for l, c in cat_colors.items()]
ax.legend(handles=legend, fontsize=8)
plt.tight_layout()
save("p2_revenue_vs_profit_scatter.png")

# --- 2d. Profit Flag Donut ----------------------------------------
fig, ax = plt.subplots(figsize=(5, 5))
colors_flag = ["#2ca02c", "#d62728"]
wedges, texts, autotexts = ax.pie(
    flag["Order_Count"],
    labels=flag["Profit_Flag"],
    autopct="%1.1f%%",
    colors=colors_flag,
    startangle=90,
    wedgeprops={"width": 0.5},
)
for at in autotexts:
    at.set_fontsize(11)
    at.set_fontweight("bold")
ax.set_title("Orders: Profitable vs Loss-Making")
plt.tight_layout()
save("p2_profit_flag_donut.png")

print("Page 2 charts done.")

# ════════════════════════════════════════════════════════════
# PAGE 3 – Forecasting (placeholder — full forecast in 05_forecasting.py)
# ════════════════════════════════════════════════════════════

quarterly = pd.read_csv(DATA / "08_quarterly_growth.csv")
quarterly["Period"] = quarterly["Year"].astype(str) + " Q" + quarterly["Quarter"].astype(str)

fig, ax = plt.subplots(figsize=(12, 4))
ax.bar(quarterly["Period"], quarterly["Total_Revenue"],
       color=ACCENT, alpha=0.8, label="Actual Revenue")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e3:.0f}K"))
ax.set_title("Quarterly Revenue  (Actual)")
ax.set_ylabel("Revenue")
plt.xticks(rotation=45, ha="right", fontsize=8)
ax.legend()
plt.tight_layout()
save("p3_quarterly_revenue.png")

print("Page 3 placeholder chart done.")
print(f"\nAll charts saved to: {OUT}")
